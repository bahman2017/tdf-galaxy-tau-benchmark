from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tdf_galaxy_tau.analysis.expansion12_diagnostics import (
    NEAR_TIE_ABS_KMS,
    NEAR_TIE_REL_FRAC,
    _best_holdout_model,
    _holdout_rmse_by_model,
    _mixed_case_subtype,
    _photometry_context,
    _radial_region_assessment,
    _tdf_failure_scope,
)
from tdf_galaxy_tau.analysis.ngc7814_diagnostics import (
    compute_baryonic_diagnostics,
    compute_residual_tau_diagnostics,
)

FOCUS_GALAXY_IDS = (
    "NGC7814",
    "NGC5055",
    "UGC05253",
    "UGC12506",
    "UGC00128",
)
HOLDOUT_SPLIT = "even_odd_index"
ANALYSIS_STAGE = "phase_5d_audit_expansion20_failure_diagnostics"

AUDIT_DISCLAIMER = (
    "This audit diagnoses expansion_20 failure, mixed, and sensitivity-recovery cases only. "
    "It does not add new fits, does not validate TDF on full SPARC, "
    "does not disprove dark matter, and does not include lensing."
)

BULGE_LOW_THRESHOLD = 0.15
BULGE_HIGH_THRESHOLD = 0.50
LARGE_IMPROVEMENT_KMS = 50.0


@dataclass
class Expansion20DiagnosticResult:
    failure_diagnostics: pd.DataFrame
    case_review_summary: pd.DataFrame
    figure_paths: dict[str, Path | None]
    ugc12506_archetype: dict[str, Any]
    nonrobust_summary: dict[str, int]


def _failure_scope_label(failure_mode: str, tdf_scope: str) -> str:
    """Map Phase 5C classification + holdout scope to audit failure_scope."""
    if failure_mode == "tdf_failure_mode":
        return "all_tdf_failure"
    if failure_mode == "sensitivity_recovery" or tdf_scope == "flex_recovery":
        return "sensitivity_recovery"
    if failure_mode == "mixed_result":
        return "mixed_result"
    if tdf_scope == "all_tdf_failure":
        return "all_tdf_failure"
    return tdf_scope


def classify_ugc12506_archetype(row: pd.Series) -> dict[str, Any]:
    """Compare UGC12506 to reference archetypes from Phase 5B-Audit / 5B-R."""
    r3 = float(row["tdf_3knot_holdout_rmse_kms"])
    r5 = float(row["tdf_5knot_holdout_rmse_kms"])
    nfw = float(row["nfw_refit_holdout_rmse_kms"])
    mond = float(row["mond_fit_a0_holdout_rmse_kms"])
    improvement = float(row["tdf_5knot_minus_tdf_3knot_holdout_improvement_kms"])
    bulge = float(row.get("median_vbulge_over_vbar", np.nan))
    failure_mode = str(row["failure_mode_classification"])

    baseline_best = min(x for x in (nfw, mond) if np.isfinite(x))
    tdf5_beats_both = np.isfinite(r5) and r5 < nfw and r5 < mond
    tdf5_fails_both = not tdf5_beats_both

    ranked = sorted(
        [
            ("tdf_3knot", r3),
            ("tdf_5knot", r5),
            ("nfw_refit", nfw),
            ("mond_fit_a0_simple", mond),
        ],
        key=lambda x: x[1],
    )
    best_m, best_v = ranked[0]
    second_v = ranked[1][1] if len(ranked) > 1 else float("nan")
    gap = second_v - best_v if np.isfinite(second_v) else float("nan")
    near_tie = bool(
        best_m in ("nfw_refit", "mond_fit_a0_simple")
        and np.isfinite(gap)
        and (gap <= NEAR_TIE_ABS_KMS or (best_v > 0 and gap / best_v <= NEAR_TIE_REL_FRAC))
    )

    archetype = "unclassified"
    rationale = ""

    if failure_mode == "tdf_failure_mode" or tdf5_fails_both:
        archetype = "NGC7814_style_all_tdf_failure"
        rationale = "Both TDF knot counts fail vs NFW/MOND on holdout (canonical all-TDF pattern)."
    elif near_tie or failure_mode == "mixed_result":
        archetype = "UGC00128_style_near_tie"
        rationale = (
            f"Holdout models within near-tie band (best={best_m}, gap≈{gap:.2f} km/s); "
            "not a clean sensitivity-recovery case."
        )
    elif tdf5_beats_both and improvement >= LARGE_IMPROVEMENT_KMS:
        if bulge < BULGE_LOW_THRESHOLD:
            archetype = "NGC5055_style_knot_flexibility"
            rationale = (
                "Large tdf_3knot failure with strong tdf_5knot recovery; disk-dominated baryons "
                f"(v_bulge/v_bar≈{bulge:.2f}) — matches NGC5055 knot-flexibility tension."
            )
        elif bulge >= BULGE_HIGH_THRESHOLD:
            archetype = "UGC05253_style_mixed_baryonic_knot"
            rationale = (
                "Large recovery with bulge-influenced baryons — closer to UGC05253 mixed "
                "baryonic+knot-flexibility pattern."
            )
        else:
            archetype = "NGC5055_style_knot_flexibility"
            rationale = (
                "Strong tdf_5knot recovery vs tdf_3knot with moderate bulge; dominant signal is "
                "knot-flexibility (NGC5055-like), not all-TDF failure."
            )
    elif tdf5_beats_both:
        if bulge >= BULGE_HIGH_THRESHOLD:
            archetype = "UGC05253_style_mixed_baryonic_knot"
            rationale = (
                "Moderate tdf_5knot recovery with high bulge fraction — mixed baryonic structure "
                "and knot sensitivity (UGC05253-like)."
            )
        else:
            archetype = "NGC5055_style_knot_flexibility"
            rationale = (
                f"Milder sensitivity-recovery (Δholdout≈{improvement:.1f} km/s) vs NGC5055's "
                "~123 km/s gap; same knot-flexibility class but lower severity."
            )
    else:
        archetype = "UGC00128_style_near_tie"
        rationale = "Ambiguous holdout ordering; treat cautiously."

    return {
        "galaxy_id": "UGC12506",
        "archetype": archetype,
        "rationale": rationale,
        "tdf_3knot_holdout_rmse_kms": r3,
        "tdf_5knot_holdout_rmse_kms": r5,
        "holdout_improvement_kms": improvement,
        "median_vbulge_over_vbar": bulge,
        "best_holdout_model": str(row.get("best_holdout_model", "")),
    }


def _recommended_interpretation_20(
    galaxy_id: str,
    failure_mode: str,
    failure_scope: str,
    mixed_subtype: str,
    archetype: str,
) -> str:
    if galaxy_id == "NGC7814":
        return (
            "Canonical all-TDF holdout failure on expansion_20; mandated label preserved. "
            "Inner baryonic/residual tension; not recoverable by tdf_5knot alone."
        )
    if galaxy_id == "NGC5055":
        return (
            "Frozen sensitivity-recovery: tdf_3knot catastrophic on holdout; tdf_5knot competitive. "
            "NGC5055-style knot-flexibility (Phase 5B-R). Not primary success."
        )
    if galaxy_id == "UGC05253":
        return (
            "Frozen sensitivity-recovery with bulge-influenced baryons and outer radial tension "
            "(Phase 5B-R). UGC05253-style mixed baryonic+knot; unstable without blocked holdout."
        )
    if galaxy_id == "UGC12506":
        return (
            f"New expansion_20 sensitivity-recovery; archetype={archetype}. "
            f"{archetype.replace('_', ' ')} — report tdf_5knot as sensitivity only, not robust success."
        )
    if galaxy_id == "UGC00128":
        return (
            "Frozen mixed/near-tie: NFW marginally best; tdf_5knot worse than tdf_3knot. "
            "Not sensitivity-recovery; exclude from primary success counts."
        )
    return f"{galaxy_id}: {failure_mode} ({failure_scope}); {mixed_subtype or archetype}."


def build_expansion20_failure_diagnostics(
    *,
    failure_summary: pd.DataFrame,
    holdout: pd.DataFrame,
    rotmod: pd.DataFrame,
    tau_profiles: pd.DataFrame,
    photometry: pd.DataFrame,
    model_comparison: pd.DataFrame | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for gid in FOCUS_GALAXY_IDS:
        fail_row = failure_summary[failure_summary["galaxy_id"] == gid]
        failure_mode = (
            str(fail_row["failure_mode_classification"].iloc[0]) if not fail_row.empty else "unknown"
        )
        cohort_role = str(fail_row["cohort_role"].iloc[0]) if not fail_row.empty else ""

        rmses = _holdout_rmse_by_model(holdout, gid)
        r3 = rmses["tdf_3knot"]
        r5 = rmses["tdf_5knot"]
        rnfw = rmses["nfw_refit"]
        rmond = rmses["mond_fit_a0_simple"]
        tdf_scope = _tdf_failure_scope(r3, r5, rnfw, rmond)
        failure_scope = _failure_scope_label(failure_mode, tdf_scope)
        mixed_subtype = _mixed_case_subtype(gid, rmses, failure_mode, tdf_scope)
        improvement = r3 - r5 if np.isfinite(r3) and np.isfinite(r5) else float("nan")

        in_sample_3 = float("nan")
        in_sample_5 = float("nan")
        if model_comparison is not None:
            mc = model_comparison[
                (model_comparison["galaxy_id"] == gid)
                & (model_comparison["model_name"].isin(["tdf_3knot", "tdf_5knot"]))
            ]
            m3 = mc[mc["model_name"] == "tdf_3knot"]
            m5 = mc[mc["model_name"] == "tdf_5knot"]
            if not m3.empty:
                in_sample_3 = float(m3["rmse_kms"].iloc[0])
            if not m5.empty:
                in_sample_5 = float(m5["rmse_kms"].iloc[0])

        row_data: dict[str, Any] = {
            "analysis_stage": ANALYSIS_STAGE,
            "galaxy_id": gid,
            "cohort_role": cohort_role,
            "failure_mode_classification": failure_mode,
            "holdout_split": HOLDOUT_SPLIT,
            "tdf_3knot_holdout_rmse_kms": r3,
            "tdf_5knot_holdout_rmse_kms": r5,
            "nfw_refit_holdout_rmse_kms": rnfw,
            "mond_fit_a0_holdout_rmse_kms": rmond,
            "best_holdout_model": _best_holdout_model(rmses),
            "tdf_5knot_minus_tdf_3knot_holdout_improvement_kms": improvement,
            "tdf_3knot_beats_nfw_holdout": bool(np.isfinite(r3) and np.isfinite(rnfw) and r3 < rnfw),
            "tdf_5knot_beats_nfw_holdout": bool(np.isfinite(r5) and np.isfinite(rnfw) and r5 < rnfw),
            "failure_scope": failure_scope,
            "tdf_failure_scope_diagnostic": tdf_scope,
            "mixed_case_subtype": mixed_subtype,
            "in_sample_tdf_3knot_rmse_kms": in_sample_3,
            "in_sample_tdf_5knot_rmse_kms": in_sample_5,
            **compute_baryonic_diagnostics(rotmod, gid),
            **compute_residual_tau_diagnostics(rotmod, tau_profiles, gid),
            **_radial_region_assessment(rotmod, tau_profiles, gid),
            **_photometry_context(photometry, gid),
            "archetype_reference": "",
        }
        rows.append(row_data)

    diagnostics = pd.DataFrame(rows)
    u125 = classify_ugc12506_archetype(
        diagnostics[diagnostics["galaxy_id"] == "UGC12506"].iloc[0]
    )
    diagnostics.loc[diagnostics["galaxy_id"] == "UGC12506", "archetype_reference"] = u125["archetype"]

    interpretations: list[str] = []
    for _, drow in diagnostics.iterrows():
        arch = (
            str(drow["archetype_reference"])
            if drow["galaxy_id"] == "UGC12506"
            else ""
        )
        interpretations.append(
            _recommended_interpretation_20(
                str(drow["galaxy_id"]),
                str(drow["failure_mode_classification"]),
                str(drow["failure_scope"]),
                str(drow["mixed_case_subtype"]),
                arch,
            )
        )
    diagnostics["recommended_interpretation"] = interpretations
    return diagnostics


def build_expansion20_case_review_summary(diagnostics: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "galaxy_id",
        "failure_mode_classification",
        "failure_scope",
        "tdf_3knot_holdout_rmse_kms",
        "tdf_5knot_holdout_rmse_kms",
        "nfw_refit_holdout_rmse_kms",
        "mond_fit_a0_holdout_rmse_kms",
        "best_holdout_model",
        "tdf_5knot_minus_tdf_3knot_holdout_improvement_kms",
        "archetype_reference",
        "radial_region_issue",
        "median_vbulge_over_vbar",
        "fraction_negative_residual_v2",
        "recommended_interpretation",
    ]
    return diagnostics[cols].copy()


def nonrobust_classification_summary(diagnostics: pd.DataFrame) -> dict[str, int]:
    counts: dict[str, int] = {}
    for label in ("all_tdf_failure", "sensitivity_recovery", "mixed_result"):
        counts[label] = int((diagnostics["failure_scope"] == label).sum())
    counts["total_nonrobust"] = len(diagnostics)
    return counts


def plot_expansion20_figures(
    diagnostics: pd.DataFrame,
    tau_profiles: pd.DataFrame,
    *,
    figures_dir: Path,
) -> dict[str, Path | None]:
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path | None] = {
        "expansion20_failure_case_residuals.png": None,
        "expansion20_tdf3_vs_tdf5_gap.png": None,
    }
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return paths

    fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=False)
    for ax, gid in zip(axes.flat, FOCUS_GALAXY_IDS):
        t = tau_profiles[tau_profiles["galaxy_id"] == gid].sort_values("r_kpc")
        r = t["r_kpc"].to_numpy()
        rv2 = t["residual_v2_kms2"].to_numpy()
        ax.plot(r, rv2, "b.-", ms=3)
        ax.axhline(0, color="k", lw=0.6)
        neg = rv2 < 0
        if neg.any():
            ax.scatter(r[neg], rv2[neg], c="C3", s=20, zorder=5)
        row = diagnostics[diagnostics["galaxy_id"] == gid].iloc[0]
        ax.set_title(
            f"{gid}\n{row['failure_mode_classification']}\n"
            f"3k/5k/NFW: {row['tdf_3knot_holdout_rmse_kms']:.1f}/"
            f"{row['tdf_5knot_holdout_rmse_kms']:.1f}/"
            f"{row['nfw_refit_holdout_rmse_kms']:.1f}",
            fontsize=8,
        )
        ax.set_xlabel("r [kpc]")
        ax.set_ylabel("residual_v²")
        ax.grid(alpha=0.3)
    axes.flat[-1].axis("off")
    fig.suptitle("Expansion-20 non-robust cases — τ residual structure (no new fits)", y=1.02)
    fig.tight_layout()
    p_res = figures_dir / "expansion20_failure_case_residuals.png"
    fig.savefig(p_res, dpi=150, bbox_inches="tight")
    plt.close(fig)
    paths["expansion20_failure_case_residuals.png"] = p_res

    fig, ax = plt.subplots(figsize=(10, 5.5))
    gids = list(FOCUS_GALAXY_IDS)
    r3 = diagnostics["tdf_3knot_holdout_rmse_kms"].to_numpy()
    r5 = diagnostics["tdf_5knot_holdout_rmse_kms"].to_numpy()
    rnfw = diagnostics["nfw_refit_holdout_rmse_kms"].to_numpy()
    x = np.arange(len(gids))
    w = 0.28
    ax.bar(x - w, r3, width=w, label="tdf_3knot", color="C2")
    ax.bar(x, r5, width=w, label="tdf_5knot", color="C1")
    ax.bar(x + w, rnfw, width=w, label="nfw_refit", color="C0", alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(gids, rotation=20, ha="right")
    ax.set_ylabel("even/odd holdout RMSE [km/s]")
    ax.set_title("Expansion-20 non-robust holdout comparison (primary vs sensitivity)")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    p_gap = figures_dir / "expansion20_tdf3_vs_tdf5_gap.png"
    fig.savefig(p_gap, dpi=150)
    plt.close(fig)
    paths["expansion20_tdf3_vs_tdf5_gap.png"] = p_gap
    return paths


def write_expansion20_failure_report(
    path: Path | str,
    *,
    diagnostics: pd.DataFrame,
    case_review: pd.DataFrame,
    ugc12506: dict[str, Any],
    summary_counts: dict[str, int],
    figure_paths: dict[str, Path | None],
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Expansion-20 Failure-Mode Analysis (Phase 5D)",
        "",
        f"> {AUDIT_DISCLAIMER}",
        "",
        "## Scope",
        "",
        "Audit of five **non-robust** expansion_20 galaxies (15/20 are robust_tdf_success): "
        "**NGC7814**, **NGC5055**, **UGC05253**, **UGC12506**, **UGC00128**. "
        "Uses Phase 5C tables only — no new model fitting.",
        "",
        "## Non-robust classification summary",
        "",
        f"- **all_tdf_failure:** {summary_counts.get('all_tdf_failure', 0)}",
        f"- **sensitivity_recovery:** {summary_counts.get('sensitivity_recovery', 0)}",
        f"- **mixed_result:** {summary_counts.get('mixed_result', 0)}",
        "",
        "Primary success count remains **tdf_3knot only** (robust_tdf_success = 15). "
        "sensitivity_recovery cases must **not** increment primary success.",
        "",
        "## UGC12506 archetype (new in expansion_20)",
        "",
        f"- **Assigned archetype:** `{ugc12506['archetype']}`",
        f"- **Rationale:** {ugc12506['rationale']}",
        "",
        f"- tdf_3knot holdout: **{ugc12506['tdf_3knot_holdout_rmse_kms']:.2f}** km/s",
        f"- tdf_5knot holdout: **{ugc12506['tdf_5knot_holdout_rmse_kms']:.2f}** km/s",
        f"- Improvement (3k−5k): **{ugc12506['holdout_improvement_kms']:.2f}** km/s",
        f"- Best holdout model: **{ugc12506['best_holdout_model']}**",
        "",
        "**Conclusion:** UGC12506 is **not** NGC7814-style (tdf_5knot beats baselines). "
        "It is **not** UGC00128 near-tie (tdf_5knot is clearly best). "
        "It is closest to **NGC5055-style knot-flexibility** with a **milder** holdout gap "
        "(~6 km/s vs ~123 km/s for NGC5055), not the bulge-heavy UGC05253 mixed pattern.",
        "",
        "## Reference comparisons",
        "",
        "| Galaxy | failure_scope | tdf_3knot | tdf_5knot | NFW | MOND |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]

    for _, row in case_review.iterrows():
        lines.append(
            f"| {row['galaxy_id']} | {row['failure_scope']} | "
            f"{row['tdf_3knot_holdout_rmse_kms']:.1f} | {row['tdf_5knot_holdout_rmse_kms']:.1f} | "
            f"{row['nfw_refit_holdout_rmse_kms']:.1f} | {row['mond_fit_a0_holdout_rmse_kms']:.1f} |"
        )

    lines.extend(["", "## Per-case detail", ""])
    for _, row in case_review.iterrows():
        lines.extend(
            [
                f"### {row['galaxy_id']} ({row['failure_mode_classification']})",
                "",
                f"- **failure_scope:** {row['failure_scope']}",
                f"- **Best holdout:** {row['best_holdout_model']}",
                f"- **tdf_5knot − tdf_3knot:** {row['tdf_5knot_minus_tdf_3knot_holdout_improvement_kms']:.2f} km/s",
                f"- **Archetype:** {row['archetype_reference'] or '—'}",
                f"- **Radial suspicion:** {row['radial_region_issue']}",
                f"- **Baryonic:** median v_bulge/v_bar={row['median_vbulge_over_vbar']:.3f}",
                f"- **Interpretation:** {row['recommended_interpretation']}",
                "",
            ]
        )

    lines.extend(["## Figures", ""])
    for name, p in figure_paths.items():
        lines.append(f"- `{p}`" if p else f"- {name}: (not generated)")

    lines.extend(
        [
            "",
            "## Claim boundaries",
            "",
            "- expansion_20 controlled cohort only",
            "- No new fits; no full SPARC",
            "- No dark-matter disproof; no lensing",
            "",
            "## Outputs",
            "",
            "- `outputs/tables/expansion20_failure_diagnostics.csv`",
            "- `outputs/tables/expansion20_case_review_summary.csv`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_expansion20_diagnostics(
    *,
    failure_summary_path: Path | str = "outputs/tables/expansion20_failure_mode_summary.csv",
    holdout_path: Path | str = "outputs/tables/expansion20_holdout_validation.csv",
    rotmod_path: Path | str = "data/processed/sparc/sparc_rotmod_standardized.csv",
    tau_path: Path | str = "outputs/tables/expansion20_tau_profiles.csv",
    photometry_path: Path | str = "data/processed/sparc/sparc_photometry_metadata.csv",
    model_comparison_path: Path | str = "outputs/tables/expansion20_model_comparison.csv",
    figures_dir: Path | str = "outputs/figures/sparc_subset",
) -> Expansion20DiagnosticResult:
    failure_summary = pd.read_csv(failure_summary_path)
    holdout = pd.read_csv(holdout_path)
    rotmod = pd.read_csv(rotmod_path)
    tau_profiles = pd.read_csv(tau_path)
    photometry = pd.read_csv(photometry_path)
    model_comparison = pd.read_csv(model_comparison_path)

    diagnostics = build_expansion20_failure_diagnostics(
        failure_summary=failure_summary,
        holdout=holdout,
        rotmod=rotmod,
        tau_profiles=tau_profiles,
        photometry=photometry,
        model_comparison=model_comparison,
    )
    case_review = build_expansion20_case_review_summary(diagnostics)
    ugc12506 = classify_ugc12506_archetype(
        diagnostics[diagnostics["galaxy_id"] == "UGC12506"].iloc[0]
    )
    summary_counts = nonrobust_classification_summary(diagnostics)
    figure_paths = plot_expansion20_figures(
        diagnostics, tau_profiles, figures_dir=Path(figures_dir)
    )
    return Expansion20DiagnosticResult(
        failure_diagnostics=diagnostics,
        case_review_summary=case_review,
        figure_paths=figure_paths,
        ugc12506_archetype=ugc12506,
        nonrobust_summary=summary_counts,
    )
