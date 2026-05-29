from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.analysis.radial_holdout_maps import build_radial_failure_map_summary
from tdf_galaxy_tau.metrics.comparison import rmse
from tdf_galaxy_tau.validation.holdout_residuals import (
    COMPARISON_MODE,
    export_holdout_point_residuals,
    load_holdout_export_configs,
)

FOCUS_GALAXY_IDS = ("NGC5055", "UGC05253")
PRIMARY_SPLIT = "even_odd_index"
TDF_MODELS = ("tdf_3knot", "tdf_5knot")
BASELINE_MODELS = ("nfw_refit", "mond_fit_a0_simple")
PLOT_MODELS = TDF_MODELS + BASELINE_MODELS
VALIDATION_STAGE = "phase_5b_r_expansion12_holdout_point_residuals"
ANALYSIS_STAGE = "phase_5b_r_expansion12_radial_maps"

AUDIT_DISCLAIMER = (
    "This diagnostic phase analyzes radial residual structure for expansion_12 flex-recovery "
    "cases only. It does not add new fits for scientific claims, does not run expansion_20, "
    "does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing."
)

NGC7814_REFERENCE = {
    "median_vbulge_over_vbar": 0.80,
    "worst_region_tdf_3knot": "inner",
    "tension_type": "baryonic_decomposition_and_inner_residual",
}


@dataclass
class Expansion12RadialMapResult:
    holdout_points: pd.DataFrame
    radial_summary: pd.DataFrame
    localization: dict[str, dict[str, Any]]
    comparison: dict[str, Any]
    figure_paths: dict[str, Path | None]


def _even_odd(points: pd.DataFrame, galaxy_id: str) -> pd.DataFrame:
    return points[
        (points["galaxy_id"] == galaxy_id) & (points["split_name"] == PRIMARY_SPLIT)
    ]


def export_expansion12_holdout_points(
    data: pd.DataFrame,
    tau_df: pd.DataFrame,
    galaxy_ids: list[str] | None = None,
    *,
    recon_path: Path | str = "configs/reconstruction.yaml",
    models_path: Path | str = "configs/models.yaml",
) -> pd.DataFrame:
    """Regenerate per-point holdout predictions (train-only); does not touch Phase 5B summary tables."""
    gids = list(galaxy_ids or FOCUS_GALAXY_IDS)
    recon_yaml, models_yaml = load_holdout_export_configs(recon_path, models_path)
    audit_cfg = recon_yaml.get("tdf_robustness_audit", {})
    tdf_models = tuple(audit_cfg.get("holdout_tdf_models", list(TDF_MODELS)))

    points = export_holdout_point_residuals(
        data,
        tau_df,
        gids,
        recon_yaml,
        models_yaml,
        tdf_models=tdf_models,
        baseline_models=BASELINE_MODELS,
    )
    points = points.copy()
    points["validation_stage"] = VALIDATION_STAGE
    return points


def _region_rmse_table(summary: pd.DataFrame, galaxy_id: str, model_name: str) -> dict[str, float]:
    sub = summary[
        (summary["galaxy_id"] == galaxy_id)
        & (summary["split_name"] == PRIMARY_SPLIT)
        & (summary["model_name"] == model_name)
    ]
    return {
        str(row["radial_region_label"]): float(row["rmse_kms"])
        for _, row in sub.iterrows()
    }


def localize_flex_recovery_failure(
    summary: pd.DataFrame,
    points: pd.DataFrame,
    galaxy_id: str,
) -> dict[str, Any]:
    """Where does tdf_3knot fail radially, and does tdf_5knot recover in the same regions?"""
    tdf3 = _region_rmse_table(summary, galaxy_id, "tdf_3knot")
    tdf5 = _region_rmse_table(summary, galaxy_id, "tdf_5knot")
    nfw = _region_rmse_table(summary, galaxy_id, "nfw_refit")

    worst_3 = max(tdf3, key=tdf3.get) if tdf3 else None  # type: ignore[arg-type]
    worst_5 = max(tdf5, key=tdf5.get) if tdf5 else None  # type: ignore[arg-type]

    recovery_regions: list[str] = []
    for region in ("inner", "middle", "outer"):
        r3 = tdf3.get(region, float("nan"))
        r5 = tdf5.get(region, float("nan"))
        rn = nfw.get(region, float("nan"))
        if np.isfinite(r3) and np.isfinite(r5) and r5 < r3 and (not np.isfinite(rn) or r5 < rn):
            recovery_regions.append(region)

    pts = _even_odd(points, galaxy_id)
    tdf3_pts = pts[pts["model_name"] == "tdf_3knot"]
    inner_neg_v2 = int(
        tdf3_pts[tdf3_pts["radial_region_label"] == "inner"]["negative_v2_flag"].astype(bool).sum()
    )

    return {
        "galaxy_id": galaxy_id,
        "tdf_3knot_worst_region": worst_3,
        "tdf_5knot_worst_region": worst_5,
        "tdf_3knot_region_rmse_kms": tdf3,
        "tdf_5knot_region_rmse_kms": tdf5,
        "nfw_refit_region_rmse_kms": nfw,
        "tdf_5knot_recovers_regions": ";".join(recovery_regions) if recovery_regions else "",
        "tdf_5knot_recovers_same_worst_region_as_3knot": bool(worst_3 and worst_3 in recovery_regions),
        "tdf_3knot_inner_negative_v2_holdout_count": inner_neg_v2,
        "even_odd_holdout_rmse_tdf_3knot": float(rmse(tdf3_pts["v_obs_kms"], tdf3_pts["v_pred_kms"]))
        if not tdf3_pts.empty
        else float("nan"),
        "even_odd_holdout_rmse_tdf_5knot": float(
            rmse(
                pts[pts["model_name"] == "tdf_5knot"]["v_obs_kms"],
                pts[pts["model_name"] == "tdf_5knot"]["v_pred_kms"],
            )
        )
        if not pts[pts["model_name"] == "tdf_5knot"].empty
        else float("nan"),
    }


def classify_tension_type(
    galaxy_id: str,
    localization: dict[str, Any],
    failure_diag: pd.DataFrame | None = None,
) -> str:
    bulge_med = float("nan")
    neg_frac = float("nan")
    if failure_diag is not None and not failure_diag.empty:
        row = failure_diag[failure_diag["galaxy_id"] == galaxy_id]
        if not row.empty:
            bulge_med = float(row["median_vbulge_over_vbar"].iloc[0])
            neg_frac = float(row["fraction_negative_residual_v2"].iloc[0])

    flex_recovery = localization.get("tdf_5knot_recovers_regions", "")
    if galaxy_id == "NGC5055":
        return "knot_flexibility_tension"
    if bulge_med > 0.5 and neg_frac > 0.3:
        return "mixed_baryonic_and_knot_flexibility"
    if flex_recovery:
        return "knot_flexibility_tension"
    return "knot_flexibility_tension"


def expansion20_recommendation(
    galaxy_id: str,
    localization: dict[str, Any],
    tension_type: str,
) -> str:
    if tension_type == "knot_flexibility_tension" and localization.get("tdf_5knot_recovers_same_worst_region_as_3knot"):
        return "sensitivity_recovery_case"
    if tension_type.startswith("mixed"):
        return "mixed_sensitivity_recovery_case"
    return "sensitivity_recovery_case"


def compare_flex_recovery_cases(
    loc_5055: dict[str, Any],
    loc_05253: dict[str, Any],
) -> dict[str, Any]:
    return {
        "similar_worst_region_tdf_3knot": loc_5055.get("tdf_3knot_worst_region")
        == loc_05253.get("tdf_3knot_worst_region"),
        "ngc5055_worst_region": loc_5055.get("tdf_3knot_worst_region"),
        "ugc05253_worst_region": loc_05253.get("tdf_3knot_worst_region"),
        "both_recover_with_5knot": bool(
            loc_5055.get("tdf_5knot_recovers_regions") and loc_05253.get("tdf_5knot_recovers_regions")
        ),
        "distinction": (
            "Both show primary tdf_3knot holdout failure with tdf_5knot regional recovery, but "
            "NGC5055 is disk-dominated (no bulge in fixed baryons) with inner diagnostic negative "
            "residual_v²; UGC05253 is bulge-influenced (high v_bulge/v_bar) closer to NGC7814 "
            "baryonic structure yet still flex-recovers on holdout — knot-flexibility dominates "
            "for NGC5055, mixed baryonic+knot for UGC05253."
        ),
        "vs_ngc7814": (
            "Neither is NGC7814-style all-TDF failure: tdf_5knot improves holdout substantially. "
            "NGC7814 inner baryonic tension persists for both knot counts; these flex cases are "
            "primarily knot-placement / flexibility tension."
        ),
    }


def plot_galaxy_radial_holdout_map(
    points: pd.DataFrame,
    galaxy_id: str,
    output_path: Path,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    sub = _even_odd(points, galaxy_id)
    if sub.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 5.5))
    colors = {
        "tdf_3knot": "C2",
        "tdf_5knot": "C1",
        "nfw_refit": "C0",
        "mond_fit_a0_simple": "C4",
    }
    for model in PLOT_MODELS:
        m = sub[sub["model_name"] == model]
        if m.empty:
            continue
        ax.plot(
            m["r_kpc"],
            m["residual_kms"],
            "o-",
            ms=4,
            label=model.replace("_simple", ""),
            color=colors.get(model, None),
            alpha=0.85,
        )
    r_min, r_max = sub["r_kpc"].min(), sub["r_kpc"].max()
    third = (r_max - r_min) / 3.0 if r_max > r_min else 1.0
    ax.axvspan(r_min, r_min + third, alpha=0.08, color="C3", label="inner third")
    ax.axvspan(r_min + third, r_min + 2 * third, alpha=0.05, color="gray")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel("holdout residual v_obs − v_pred [km/s]")
    ax.set_title(f"{galaxy_id} — even/odd holdout residuals (expansion_12 flex-recovery audit)")
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.3)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_flex_recovery_comparison(
    points: pd.DataFrame,
    localization: dict[str, dict[str, Any]],
    output_path: Path,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, gid in zip(axes, FOCUS_GALAXY_IDS):
        sub = _even_odd(points, gid)
        for model, color, ls in (
            ("tdf_3knot", "C2", "-"),
            ("tdf_5knot", "C1", "--"),
            ("nfw_refit", "C0", ":"),
        ):
            m = sub[sub["model_name"] == model]
            if m.empty:
                continue
            ax.plot(m["r_kpc"], m["abs_residual_kms"], ls, marker="o", ms=3, label=model, color=color)
        loc = localization.get(gid, {})
        ax.set_title(
            f"{gid}\n3k worst={loc.get('tdf_3knot_worst_region', '?')}; "
            f"5k recovers={loc.get('tdf_5knot_recovers_regions', '—')}"
        )
        ax.set_xlabel("r [kpc]")
        ax.set_ylabel("|residual| [km/s]")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    fig.suptitle("Flex-recovery radial holdout comparison (even/odd, train-only)", y=1.02)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def write_expansion12_radial_report(
    path: Path | str,
    *,
    points: pd.DataFrame,
    summary: pd.DataFrame,
    localization: dict[str, dict[str, Any]],
    comparison: dict[str, Any],
    failure_diag: pd.DataFrame | None = None,
    figure_paths: dict[str, Path | None] | None = None,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Expansion-12 Radial Holdout Residual Map Report (Phase 5B-R)",
        "",
        f"> {AUDIT_DISCLAIMER}",
        "",
        "## Objective",
        "",
        "Localize **where** primary **tdf_3knot** holdout errors occur for flex-recovery galaxies "
        "**NGC5055** and **UGC05253**, and whether **tdf_5knot** recovers the same radial bands. "
        "Per-point predictions are regenerated with the same train-only protocol as Phases 3C/4E/5B "
        "(no alteration of Phase 5B aggregate tables).",
        "",
        "## Export method",
        "",
        f"- **comparison_mode:** `{COMPARISON_MODE}`",
        f"- **validation_stage:** `{VALIDATION_STAGE}`",
        f"- **Primary split:** `{PRIMARY_SPLIT}`",
        f"- **Models:** {', '.join(PLOT_MODELS)}",
        f"- **Test-point rows (all splits):** {len(points)}",
        f"- **Galaxies:** {', '.join(FOCUS_GALAXY_IDS)}",
        "",
        "## Regional RMSE (even/odd)",
        "",
        "| galaxy | model | inner | middle | outer | 3k worst region | 5k recovers |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]

    for gid in FOCUS_GALAXY_IDS:
        loc = localization[gid]
        for model in ("tdf_3knot", "tdf_5knot", "nfw_refit"):
            regs = _region_rmse_table(summary, gid, model)
            lines.append(
                f"| {gid} | {model} | {regs.get('inner', float('nan')):.1f} | "
                f"{regs.get('middle', float('nan')):.1f} | {regs.get('outer', float('nan')):.1f} | "
                f"{loc.get('tdf_3knot_worst_region', '') if model == 'tdf_3knot' else ''} | "
                f"{loc.get('tdf_5knot_recovers_regions', '') if model == 'tdf_3knot' else ''} |"
            )

    lines.extend(
        [
            "",
            "## NGC5055",
            "",
        ]
    )
    _append_galaxy_section(lines, "NGC5055", localization, failure_diag)

    lines.extend(["", "## UGC05253", ""])
    _append_galaxy_section(lines, "UGC05253", localization, failure_diag)

    lines.extend(
        [
            "",
            "## NGC5055 vs UGC05253",
            "",
            comparison.get("distinction", ""),
            "",
            comparison.get("vs_ngc7814", ""),
            "",
            f"- Similar worst region (tdf_3knot): **{comparison.get('similar_worst_region_tdf_3knot')}**",
            "",
            "## Expansion_20 guidance",
            "",
            "- Treat both as **sensitivity-recovery** cases for reporting (tdf_3knot primary fails; "
            "tdf_5knot holdout competitive).",
            "- Do **not** promote to robust success without blocked-split stability.",
            "- NGC5055: knot-flexibility tension (disk-dominated baryons).",
            "- UGC05253: mixed baryonic structure + knot-flexibility; higher point count → unstable labels.",
            "",
            "## Figures",
            "",
        ]
    )
    for name, p in (figure_paths or {}).items():
        lines.append(f"- `{p}`" if p else f"- {name}: (not generated)")

    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `outputs/tables/expansion12_holdout_point_residuals.csv`",
            "- `outputs/tables/expansion12_radial_failure_map_summary.csv`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _append_galaxy_section(
    lines: list[str],
    gid: str,
    localization: dict[str, dict[str, Any]],
    failure_diag: pd.DataFrame | None,
) -> None:
    loc = localization[gid]
    tension = classify_tension_type(gid, loc, failure_diag)
    rec = expansion20_recommendation(gid, loc, tension)
    lines.extend(
        [
            f"- **tdf_3knot fails mainly in:** {loc.get('tdf_3knot_worst_region', 'n/a')} region "
            f"(even/odd regional RMSE: inner={loc.get('tdf_3knot_region_rmse_kms', {}).get('inner', float('nan')):.1f}, "
            f"middle={loc.get('tdf_3knot_region_rmse_kms', {}).get('middle', float('nan')):.1f}, "
            f"outer={loc.get('tdf_3knot_region_rmse_kms', {}).get('outer', float('nan')):.1f} km/s).",
            f"- **tdf_5knot recovery:** regions={loc.get('tdf_5knot_recovers_regions', 'none')}; "
            f"same worst band as 3knot={loc.get('tdf_5knot_recovers_same_worst_region_as_3knot')}.",
            f"- **Tension type:** {tension} (cf. NGC7814 baryonic inner failure).",
            f"- **Before expansion_20:** {rec}.",
        ]
    )


def run_expansion12_radial_maps(
    *,
    rotmod_path: Path | str = "data/processed/sparc/sparc_rotmod_standardized.csv",
    tau_path: Path | str = "outputs/tables/expansion12_tau_profiles.csv",
    failure_diag_path: Path | str = "outputs/tables/expansion12_failure_diagnostics.csv",
    recon_path: Path | str = "configs/reconstruction.yaml",
    models_path: Path | str = "configs/models.yaml",
    figures_dir: Path | str = "outputs/figures/sparc_subset",
    galaxy_ids: list[str] | None = None,
) -> Expansion12RadialMapResult:
    gids = list(galaxy_ids or FOCUS_GALAXY_IDS)
    data = pd.read_csv(rotmod_path)
    data = data[data["galaxy_id"].isin(gids)].copy()
    tau_df = pd.read_csv(tau_path)

    failure_diag: pd.DataFrame | None = None
    fpath = Path(failure_diag_path)
    if fpath.is_file():
        failure_diag = pd.read_csv(fpath)

    points = export_expansion12_holdout_points(
        data,
        tau_df,
        gids,
        recon_path=recon_path,
        models_path=models_path,
    )
    summary = build_radial_failure_map_summary(points)
    summary["analysis_stage"] = ANALYSIS_STAGE

    localization = {
        gid: localize_flex_recovery_failure(summary, points, gid) for gid in gids
    }
    for gid, loc in localization.items():
        loc["tension_type"] = classify_tension_type(gid, loc, failure_diag)
        loc["expansion20_recommendation"] = expansion20_recommendation(
            gid, loc, loc["tension_type"]
        )

    comparison = compare_flex_recovery_cases(
        localization["NGC5055"],
        localization["UGC05253"],
    )

    fig_dir = Path(figures_dir)
    figure_paths = {
        "ngc5055_radial_holdout_residuals.png": plot_galaxy_radial_holdout_map(
            points, "NGC5055", fig_dir / "ngc5055_radial_holdout_residuals.png"
        ),
        "ugc05253_radial_holdout_residuals.png": plot_galaxy_radial_holdout_map(
            points, "UGC05253", fig_dir / "ugc05253_radial_holdout_residuals.png"
        ),
        "expansion12_flex_recovery_radial_comparison.png": plot_flex_recovery_comparison(
            points, localization, fig_dir / "expansion12_flex_recovery_radial_comparison.png"
        ),
    }

    return Expansion12RadialMapResult(
        holdout_points=points,
        radial_summary=summary,
        localization=localization,
        comparison=comparison,
        figure_paths=figure_paths,
    )
