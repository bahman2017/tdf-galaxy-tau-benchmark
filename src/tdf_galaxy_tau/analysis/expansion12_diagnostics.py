from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tdf_galaxy_tau.analysis.ngc7814_diagnostics import (
    compute_baryonic_diagnostics,
    compute_residual_tau_diagnostics,
)

FOCUS_GALAXY_IDS = ("NGC7814", "NGC5055", "UGC00128", "UGC05253")
HOLDOUT_SPLIT = "even_odd_index"
HOLDOUT_MODELS = ("tdf_3knot", "tdf_5knot", "nfw_refit", "mond_fit_a0_simple")
ANALYSIS_STAGE = "phase_5b_audit_expansion12_failure_diagnostics"

AUDIT_DISCLAIMER = (
    "This audit diagnoses expansion_12 failure and mixed cases only. "
    "It does not add new fits, does not validate TDF on full SPARC, "
    "does not disprove dark matter, and does not include lensing."
)

NEAR_TIE_ABS_KMS = 3.0
NEAR_TIE_REL_FRAC = 0.12


@dataclass
class Expansion12DiagnosticResult:
    failure_diagnostics: pd.DataFrame
    case_review_summary: pd.DataFrame
    figure_paths: dict[str, Path | None]
    ngc5055_vs_ngc7814: dict[str, Any]


def _even_odd_holdout(holdout: pd.DataFrame) -> pd.DataFrame:
    sub = holdout[
        (holdout["split_name"] == HOLDOUT_SPLIT) & (holdout["model_name"].isin(HOLDOUT_MODELS))
    ].copy()
    return sub


def _holdout_rmse_by_model(holdout: pd.DataFrame, galaxy_id: str) -> dict[str, float]:
    sub = _even_odd_holdout(holdout)
    sub = sub[sub["galaxy_id"] == galaxy_id]
    out: dict[str, float] = {}
    for model in HOLDOUT_MODELS:
        row = sub[sub["model_name"] == model]
        out[model] = float(row["test_rmse_kms"].iloc[0]) if not row.empty else float("nan")
    return out


def _best_holdout_model(rmses: dict[str, float]) -> str:
    finite = {k: v for k, v in rmses.items() if np.isfinite(v)}
    if not finite:
        return ""
    return min(finite, key=finite.get)  # type: ignore[arg-type]


def _tdf_failure_scope(
    r3: float,
    r5: float,
    rnfw: float,
    rmond: float,
) -> str:
    """primary_model_failure | flex_recovery | all_tdf_failure | tdf_competitive."""
    if not np.isfinite(r3):
        return "unknown"
    baseline_best = min(
        x for x in (rnfw, rmond) if np.isfinite(x)
    ) if any(np.isfinite(x) for x in (rnfw, rmond)) else float("inf")
    tdf3_fails = r3 > baseline_best
    tdf5_beats_baseline = np.isfinite(r5) and r5 < baseline_best
    tdf5_beats_3 = np.isfinite(r5) and r5 < r3

    if not tdf3_fails:
        return "tdf_competitive"
    if tdf5_beats_baseline and tdf5_beats_3:
        return "flex_recovery"
    if np.isfinite(r5) and r5 > baseline_best:
        return "all_tdf_failure"
    return "primary_model_failure"


def _mixed_case_subtype(
    galaxy_id: str,
    rmses: dict[str, float],
    failure_mode: str,
    tdf_scope: str,
) -> str:
    if failure_mode == "tdf_failure_mode":
        return "canonical_failure"
    if failure_mode != "mixed_result":
        return ""

    r3 = rmses.get("tdf_3knot", float("nan"))
    r5 = rmses.get("tdf_5knot", float("nan"))
    rnfw = rmses.get("nfw_refit", float("nan"))
    rmond = rmses.get("mond_fit_a0_simple", float("nan"))
    ranked = sorted(
        [(m, v) for m, v in rmses.items() if np.isfinite(v)],
        key=lambda x: x[1],
    )
    if len(ranked) < 2:
        return "unstable_classification"

    best_m, best_v = ranked[0]
    second_m, second_v = ranked[1]
    gap = second_v - best_v
    rel = gap / best_v if best_v > 0 else float("inf")

    if tdf_scope == "flex_recovery":
        return "tdf_3knot_failure_tdf_5knot_recovery"
    if best_m in ("nfw_refit", "mond_fit_a0_simple") and gap <= NEAR_TIE_ABS_KMS:
        return "near_tie_mixed_case"
    if best_m in ("nfw_refit", "mond_fit_a0_simple") and rel <= NEAR_TIE_REL_FRAC:
        return "near_tie_mixed_case"
    if best_m in ("nfw_refit", "mond_fit_a0_simple"):
        return "baseline_dominated_mixed_case"
    if np.isfinite(r3) and np.isfinite(r5) and r5 < r3 and r3 > rnfw:
        return "tdf_3knot_failure_tdf_5knot_recovery"
    if galaxy_id == "UGC05253":
        return "unstable_classification_needs_more_diagnostics"
    return "unstable_classification"


def _radial_region_assessment(
    rotmod: pd.DataFrame,
    tau_profiles: pd.DataFrame,
    galaxy_id: str,
) -> dict[str, Any]:
    g = rotmod[rotmod["galaxy_id"] == galaxy_id].sort_values("r_kpc")
    t = tau_profiles[tau_profiles["galaxy_id"] == galaxy_id].sort_values("r_kpc")
    merged = g[["r_kpc"]].merge(
        t[["r_kpc", "residual_v2_kms2", "negative_residual_flag"]],
        on="r_kpc",
        how="inner",
    )
    if merged.empty:
        return {
            "radial_region_issue": "unknown",
            "r_at_max_abs_residual_v2_kpc": float("nan"),
            "inner_third_fraction_negative_residual": float("nan"),
            "outer_third_mean_abs_residual_v2": float("nan"),
        }

    r = merged["r_kpc"].to_numpy(dtype=float)
    rv2 = merged["residual_v2_kms2"].to_numpy(dtype=float)
    r_max = float(r[np.nanargmax(np.abs(rv2))])
    r_span = float(np.nanmax(r) - np.nanmin(r)) if r.size else 1.0
    tert = max(1, len(r) // 3)
    order = np.argsort(r)
    inner = order[:tert]
    outer = order[-tert:]
    inner_neg_frac = float(np.mean(rv2[inner] < 0)) if inner.size else float("nan")
    outer_mean = float(np.nanmean(np.abs(rv2[outer]))) if outer.size else float("nan")

    if r_max < 0.15 * (np.nanmax(r) + 1e-6) or inner_neg_frac > 0.5:
        issue = "inner_radius_residual_or_baryonic_tension"
    elif r_max > 0.7 * np.nanmax(r):
        issue = "outer_radius_tension"
    else:
        issue = "mid_disk_mixed"

    return {
        "radial_region_issue": issue,
        "r_at_max_abs_residual_v2_kpc": r_max,
        "inner_third_fraction_negative_residual": inner_neg_frac,
        "outer_third_mean_abs_residual_v2": outer_mean,
    }


def _photometry_context(photometry: pd.DataFrame, galaxy_id: str) -> dict[str, Any]:
    row = photometry[photometry["galaxy_id"] == galaxy_id]
    if row.empty:
        return {
            "distance_mpc": float("nan"),
            "inclination_deg": float("nan"),
            "morphological_type": float("nan"),
            "disk_scale_length_kpc": float("nan"),
            "luminosity_3p6_lsun": float("nan"),
            "photometry_quality_flag": "",
        }
    r = row.iloc[0]
    return {
        "distance_mpc": float(r.get("distance_mpc", np.nan)),
        "inclination_deg": float(r.get("inclination_deg", np.nan)),
        "morphological_type": float(r.get("morphological_type", np.nan)),
        "disk_scale_length_kpc": float(r.get("disk_scale_length_kpc", np.nan)),
        "luminosity_3p6_lsun": float(r.get("luminosity_3p6_lsun", np.nan)),
        "photometry_quality_flag": str(r.get("photometry_quality_flag", "")),
    }


def _recommended_interpretation(
    galaxy_id: str,
    failure_mode: str,
    tdf_scope: str,
    mixed_subtype: str,
    rmses: dict[str, float],
) -> str:
    r3 = rmses.get("tdf_3knot", float("nan"))
    r5 = rmses.get("tdf_5knot", float("nan"))
    rnfw = rmses.get("nfw_refit", float("nan"))

    if galaxy_id == "NGC7814":
        return (
            "Canonical expansion_12 holdout failure: primary tdf_3knot and sensitivity tdf_5knot "
            "both fail vs NFW/MOND on even/odd holdout; not recoverable by knot count alone. "
            "Retain mandated failure language; bulge/inner-residual context applies."
        )
    if galaxy_id == "NGC5055":
        return (
            "Primary-model (tdf_3knot) holdout failure with large RMSE, but tdf_5knot holdout "
            "is competitive (~20 km/s vs NFW/MOND ~56 km/s). Interpret as knot-placement / "
            "flexibility sensitivity, not an NGC7814-style all-TDF failure. Do not use tdf_5knot "
            "as primary success without explicit sensitivity labeling."
        )
    if galaxy_id == "UGC00128":
        return (
            "Near-tie mixed case: NFW marginally best on holdout (~2.7 vs tdf_3knot ~3.0 km/s); "
            "tdf_5knot worse than tdf_3knot on holdout. Not a flex-recovery case; exclude from "
            "expansion_20 success claims until holdout stabilizes."
        )
    if galaxy_id == "UGC05253":
        return (
            "Mixed case with tdf_3knot holdout failure vs NFW but tdf_5knot recovery on holdout; "
            "many radial points and split instability suggest caution. Classify as "
            "flex-recovery / unstable — needs blocked-split or residual-map review before expansion_20."
        )
    if tdf_scope == "all_tdf_failure":
        return f"{galaxy_id}: all TDF variants fail vs baselines on holdout."
    if tdf_scope == "flex_recovery":
        return f"{galaxy_id}: primary tdf_3knot fails; higher knot count recovers on holdout (sensitivity only)."
    return f"{galaxy_id}: {failure_mode}; {mixed_subtype}."


def build_expansion12_failure_diagnostics(
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

        ho_row = _even_odd_holdout(holdout)
        ho_row = ho_row[ho_row["galaxy_id"] == gid]
        tdf3_status = ""
        tdf5_status = ""
        if not ho_row.empty:
            s3 = ho_row[ho_row["model_name"] == "tdf_3knot"]
            s5 = ho_row[ho_row["model_name"] == "tdf_5knot"]
            if not s3.empty:
                tdf3_status = str(s3["fit_status"].iloc[0])
            if not s5.empty:
                tdf5_status = str(s5["fit_status"].iloc[0])

        rows.append(
            {
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
                "tdf_failure_scope": tdf_scope,
                "mixed_case_subtype": mixed_subtype,
                "tdf_3knot_holdout_fit_status": tdf3_status,
                "tdf_5knot_holdout_fit_status": tdf5_status,
                "in_sample_tdf_3knot_rmse_kms": in_sample_3,
                "in_sample_tdf_5knot_rmse_kms": in_sample_5,
                **compute_baryonic_diagnostics(rotmod, gid),
                **compute_residual_tau_diagnostics(rotmod, tau_profiles, gid),
                **_radial_region_assessment(rotmod, tau_profiles, gid),
                **_photometry_context(photometry, gid),
                "recommended_interpretation": _recommended_interpretation(
                    gid, failure_mode, tdf_scope, mixed_subtype, rmses
                ),
            }
        )
    return pd.DataFrame(rows)


def build_expansion12_case_review_summary(diagnostics: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "galaxy_id",
        "failure_mode_classification",
        "tdf_3knot_holdout_rmse_kms",
        "tdf_5knot_holdout_rmse_kms",
        "nfw_refit_holdout_rmse_kms",
        "mond_fit_a0_holdout_rmse_kms",
        "best_holdout_model",
        "tdf_5knot_minus_tdf_3knot_holdout_improvement_kms",
        "tdf_failure_scope",
        "mixed_case_subtype",
        "radial_region_issue",
        "median_vbulge_over_vbar",
        "fraction_negative_residual_v2",
        "recommended_interpretation",
    ]
    return diagnostics[cols].copy()


def compare_ngc5055_vs_ngc7814(diagnostics: pd.DataFrame) -> dict[str, Any]:
    ng = diagnostics[diagnostics["galaxy_id"] == "NGC7814"].iloc[0]
    n5 = diagnostics[diagnostics["galaxy_id"] == "NGC5055"].iloc[0]
    return {
        "ngc7814_tdf_3knot_holdout_rmse": float(ng["tdf_3knot_holdout_rmse_kms"]),
        "ngc7814_tdf_5knot_holdout_rmse": float(ng["tdf_5knot_holdout_rmse_kms"]),
        "ngc7814_nfw_holdout_rmse": float(ng["nfw_refit_holdout_rmse_kms"]),
        "ngc5055_tdf_3knot_holdout_rmse": float(n5["tdf_3knot_holdout_rmse_kms"]),
        "ngc5055_tdf_5knot_holdout_rmse": float(n5["tdf_5knot_holdout_rmse_kms"]),
        "ngc5055_nfw_holdout_rmse": float(n5["nfw_refit_holdout_rmse_kms"]),
        "ngc7814_tdf_failure_scope": str(ng["tdf_failure_scope"]),
        "ngc5055_tdf_failure_scope": str(n5["tdf_failure_scope"]),
        "equivalent_failure": False,
        "distinction": (
            "NGC7814: all-TDF holdout failure (tdf_3knot and tdf_5knot both >> NFW/MOND). "
            "NGC5055: primary tdf_3knot failure only; tdf_5knot holdout ~20 km/s beats "
            "NFW/MOND ~56 km/s — flexibility/knot-count sensitivity, not canonical all-TDF failure."
        ),
    }


def plot_expansion12_figures(
    diagnostics: pd.DataFrame,
    rotmod: pd.DataFrame,
    tau_profiles: pd.DataFrame,
    *,
    figures_dir: Path,
) -> dict[str, Path | None]:
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path | None] = {
        "expansion12_failure_case_residuals.png": None,
        "expansion12_tdf3_vs_tdf5_gap.png": None,
    }
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return paths

    # Residual structure panel (2x2)
    fig, axes = plt.subplots(2, 2, figsize=(11, 9), sharex=False)
    for ax, gid in zip(axes.flat, FOCUS_GALAXY_IDS):
        t = tau_profiles[tau_profiles["galaxy_id"] == gid].sort_values("r_kpc")
        r = t["r_kpc"].to_numpy()
        rv2 = t["residual_v2_kms2"].to_numpy()
        ax.plot(r, rv2, "b.-", ms=4)
        ax.axhline(0, color="k", lw=0.6)
        neg = rv2 < 0
        if neg.any():
            ax.scatter(r[neg], rv2[neg], c="C3", s=25, zorder=5)
        row = diagnostics[diagnostics["galaxy_id"] == gid].iloc[0]
        ax.set_title(
            f"{gid} ({row['failure_mode_classification']})\n"
            f"holdout 3k/5k/NFW: {row['tdf_3knot_holdout_rmse_kms']:.1f}/"
            f"{row['tdf_5knot_holdout_rmse_kms']:.1f}/"
            f"{row['nfw_refit_holdout_rmse_kms']:.1f} km/s"
        )
        ax.set_xlabel("r [kpc]")
        ax.set_ylabel("residual_v² [km²/s²]")
        ax.grid(alpha=0.3)
    fig.suptitle("Expansion-12 failure/mixed cases — Phase 2A residual_v² (no new fits)", y=1.02)
    fig.tight_layout()
    p_res = figures_dir / "expansion12_failure_case_residuals.png"
    fig.savefig(p_res, dpi=150, bbox_inches="tight")
    plt.close(fig)
    paths["expansion12_failure_case_residuals.png"] = p_res

    # tdf3 vs tdf5 holdout gap
    fig, ax = plt.subplots(figsize=(8, 5))
    gids = list(FOCUS_GALAXY_IDS)
    r3 = diagnostics["tdf_3knot_holdout_rmse_kms"].to_numpy()
    r5 = diagnostics["tdf_5knot_holdout_rmse_kms"].to_numpy()
    x = np.arange(len(gids))
    w = 0.35
    ax.bar(x - w / 2, r3, width=w, label="tdf_3knot holdout RMSE")
    ax.bar(x + w / 2, r5, width=w, label="tdf_5knot holdout RMSE")
    rnfw = diagnostics["nfw_refit_holdout_rmse_kms"].to_numpy()
    ax.plot(x, rnfw, "k^--", label="nfw_refit holdout RMSE", ms=8)
    ax.set_xticks(x)
    ax.set_xticklabels(gids, rotation=15, ha="right")
    ax.set_ylabel("holdout test RMSE [km/s]")
    ax.set_title("Primary vs sensitivity TDF holdout gap (expansion_12 audit)")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    p_gap = figures_dir / "expansion12_tdf3_vs_tdf5_gap.png"
    fig.savefig(p_gap, dpi=150)
    plt.close(fig)
    paths["expansion12_tdf3_vs_tdf5_gap.png"] = p_gap

    return paths


def write_expansion12_failure_report(
    path: Path | str,
    *,
    diagnostics: pd.DataFrame,
    case_review: pd.DataFrame,
    comparison: dict[str, Any],
    figure_paths: dict[str, Path | None],
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Expansion-12 Failure-Mode Analysis (Phase 5B-Audit)",
        "",
        f"> {AUDIT_DISCLAIMER}",
        "",
        "## Scope",
        "",
        "Diagnostic review of four expansion_12 galaxies before any expansion_20 run: "
        "**NGC7814**, **NGC5055**, **UGC00128**, **UGC05253**. "
        "Uses Phase 5B tables only (no new model fitting).",
        "",
        "## NGC5055 vs NGC7814 (not equivalent)",
        "",
        comparison["distinction"],
        "",
        "| Quantity | NGC7814 | NGC5055 |",
        "| --- | ---: | ---: |",
        f"| tdf_3knot holdout RMSE [km/s] | {comparison['ngc7814_tdf_3knot_holdout_rmse']:.1f} | "
        f"{comparison['ngc5055_tdf_3knot_holdout_rmse']:.1f} |",
        f"| tdf_5knot holdout RMSE [km/s] | {comparison['ngc7814_tdf_5knot_holdout_rmse']:.1f} | "
        f"{comparison['ngc5055_tdf_5knot_holdout_rmse']:.1f} |",
        f"| nfw_refit holdout RMSE [km/s] | {comparison['ngc7814_nfw_holdout_rmse']:.1f} | "
        f"{comparison['ngc5055_nfw_holdout_rmse']:.1f} |",
        f"| TDF failure scope | {comparison['ngc7814_tdf_failure_scope']} | "
        f"{comparison['ngc5055_tdf_failure_scope']} |",
        "",
        "- **NGC7814:** both tdf_3knot and tdf_5knot fail vs NFW/MOND on even/odd holdout (all-TDF failure).",
        "- **NGC5055:** tdf_3knot fails; tdf_5knot is much better (~123 km/s improvement), beating NFW/MOND "
        "on holdout — knot-placement / flexibility sensitivity, not canonical all-TDF failure.",
        "",
        "## Per-case summary",
        "",
    ]

    for _, row in case_review.iterrows():
        lines.extend(
            [
                f"### {row['galaxy_id']} ({row['failure_mode_classification']})",
                "",
                f"- **Holdout RMSE (km/s):** tdf_3knot={row['tdf_3knot_holdout_rmse_kms']:.2f}, "
                f"tdf_5knot={row['tdf_5knot_holdout_rmse_kms']:.2f}, "
                f"NFW={row['nfw_refit_holdout_rmse_kms']:.2f}, "
                f"MOND={row['mond_fit_a0_holdout_rmse_kms']:.2f}",
                f"- **Best holdout model:** {row['best_holdout_model']}",
                f"- **tdf_5knot − tdf_3knot improvement (positive = 5 better):** "
                f"{row['tdf_5knot_minus_tdf_3knot_holdout_improvement_kms']:.2f} km/s",
                f"- **TDF failure scope:** {row['tdf_failure_scope']}",
                f"- **Mixed subtype:** {row['mixed_case_subtype'] or '—'}",
                f"- **Radial region:** {row['radial_region_issue']}",
                f"- **Baryonic context:** median v_bulge/v_bar={row['median_vbulge_over_vbar']:.3f}, "
                f"frac negative residual_v²={row['fraction_negative_residual_v2']:.2f}",
                f"- **Interpretation:** {row['recommended_interpretation']}",
                "",
            ]
        )

    lines.extend(
        [
            "## UGC00128 and UGC05253 classification",
            "",
            "- **UGC00128:** near-tie mixed case; NFW marginally best on holdout; tdf_5knot does not recover. "
            "Baseline-dominated / near-tie — not flex-recovery.",
            "- **UGC05253:** tdf_3knot fails vs NFW on holdout; tdf_5knot recovers (flex-recovery). "
            "High point count and split sensitivity → unstable classification needing more diagnostics "
            "before expansion_20.",
            "",
            "## Figures",
            "",
        ]
    )
    for name, p in figure_paths.items():
        lines.append(f"- `{p}`" if p else f"- {name}: (not generated)")

    lines.extend(
        [
            "",
            "## Claim boundaries",
            "",
            "- Controlled expansion_12 audit only",
            "- No new fits in this phase",
            "- No full-SPARC validation",
            "- No dark-matter disproof",
            "- No lensing",
            "- **tdf_3knot** remains primary; **tdf_5knot** sensitivity only",
            "",
            "## Outputs",
            "",
            "- `outputs/tables/expansion12_failure_diagnostics.csv`",
            "- `outputs/tables/expansion12_case_review_summary.csv`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_expansion12_diagnostics(
    *,
    failure_summary_path: Path | str = "outputs/tables/expansion12_failure_mode_summary.csv",
    holdout_path: Path | str = "outputs/tables/expansion12_holdout_validation.csv",
    rotmod_path: Path | str = "data/processed/sparc/sparc_rotmod_standardized.csv",
    tau_path: Path | str = "outputs/tables/expansion12_tau_profiles.csv",
    photometry_path: Path | str = "data/processed/sparc/sparc_photometry_metadata.csv",
    model_comparison_path: Path | str = "outputs/tables/expansion12_model_comparison.csv",
    figures_dir: Path | str = "outputs/figures/sparc_subset",
) -> Expansion12DiagnosticResult:
    failure_summary = pd.read_csv(failure_summary_path)
    holdout = pd.read_csv(holdout_path)
    rotmod = pd.read_csv(rotmod_path)
    tau_profiles = pd.read_csv(tau_path)
    photometry = pd.read_csv(photometry_path)
    model_comparison = pd.read_csv(model_comparison_path)

    diagnostics = build_expansion12_failure_diagnostics(
        failure_summary=failure_summary,
        holdout=holdout,
        rotmod=rotmod,
        tau_profiles=tau_profiles,
        photometry=photometry,
        model_comparison=model_comparison,
    )
    case_review = build_expansion12_case_review_summary(diagnostics)
    comparison = compare_ngc5055_vs_ngc7814(diagnostics)
    figure_paths = plot_expansion12_figures(
        diagnostics, rotmod, tau_profiles, figures_dir=Path(figures_dir)
    )
    return Expansion12DiagnosticResult(
        failure_diagnostics=diagnostics,
        case_review_summary=case_review,
        figure_paths=figure_paths,
        ngc5055_vs_ngc7814=comparison,
    )
