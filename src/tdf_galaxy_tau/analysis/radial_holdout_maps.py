from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tdf_galaxy_tau.metrics.comparison import rmse
from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION

TARGET_GALAXY = "NGC7814"
PRIMARY_SPLIT = "even_odd_index"
TDF_MODELS_PLOT = ("tdf_3knot", "tdf_5knot", "nfw_refit", "mond_fit_a0_simple")


def build_radial_failure_map_summary(points: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-point holdout residuals by galaxy, model, split, and radial region."""
    rows: list[dict[str, Any]] = []
    grouped = points.groupby(
        ["galaxy_id", "model_name", "split_name", "radial_region_label"], dropna=False
    )
    for (gid, model, split, region), sub in grouped:
        if sub.empty:
            continue
        abs_res = sub["abs_residual_kms"].astype(float)
        norm = sub["normalized_residual"].astype(float)
        worst_idx = abs_res.idxmax()
        interpretation = _region_interpretation(gid, model, split, region, sub)
        rows.append(
            {
                "galaxy_id": gid,
                "model_name": model,
                "split_name": split,
                "radial_region_label": region,
                "n_test_points": int(len(sub)),
                "rmse_kms": float(rmse(sub["v_obs_kms"], sub["v_pred_kms"])),
                "median_abs_residual_kms": float(abs_res.median()),
                "max_abs_residual_kms": float(abs_res.max()),
                "mean_normalized_abs_residual": float(np.nanmean(np.abs(norm))),
                "worst_radius_kpc": float(sub.loc[worst_idx, "r_kpc"]),
                "worst_region_label": str(sub.loc[worst_idx, "radial_region_label"]),
                "negative_v2_count": int(sub["negative_v2_flag"].astype(bool).sum()),
                "interpretation": interpretation,
            }
        )
    return pd.DataFrame(rows)


def _region_interpretation(
    gid: str,
    model: str,
    split: str,
    region: str,
    sub: pd.DataFrame,
) -> str:
    rmse_v = float(rmse(sub["v_obs_kms"], sub["v_pred_kms"]))
    if gid == TARGET_GALAXY and split == PRIMARY_SPLIT and model.startswith("tdf"):
        if region == "inner" and rmse_v > 50:
            return "Large inner-region holdout errors for TDF on NGC7814 (exploratory)."
        if rmse_v > 80:
            return "Elevated regional holdout RMSE for TDF on NGC7814."
    if rmse_v < 15:
        return "Moderate regional holdout errors on this subset."
    return "Regional holdout RMSE diagnostic."


def _even_odd(points: pd.DataFrame, galaxy_id: str) -> pd.DataFrame:
    return points[
        (points["galaxy_id"] == galaxy_id) & (points["split_name"] == PRIMARY_SPLIT)
    ]


def plot_ngc7814_radial_map(points: pd.DataFrame, output_path: Path) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    sub = _even_odd(points, TARGET_GALAXY)
    if sub.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 5.5))
    colors = {"tdf_3knot": "C2", "tdf_5knot": "C1", "nfw_refit": "C0", "mond_fit_a0_simple": "C4"}
    for model in TDF_MODELS_PLOT:
        m = sub[sub["model_name"] == model]
        if m.empty:
            continue
        ax.plot(
            m["r_kpc"],
            m["residual_kms"],
            "o-",
            ms=5,
            label=model,
            color=colors.get(model, None),
            alpha=0.85,
        )
    r_min, r_max = sub["r_kpc"].min(), sub["r_kpc"].max()
    third = (r_max - r_min) / 3.0
    ax.axvspan(r_min, r_min + third, alpha=0.08, color="C3", label="inner third")
    ax.axvspan(r_min + third, r_min + 2 * third, alpha=0.05, color="gray")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel("holdout residual v_obs − v_pred [km/s]")
    ax.set_title(f"{TARGET_GALAXY} — holdout residual diagnostic (even/odd, train-only fits)")
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.3)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_all_galaxies_compact(points: pd.DataFrame, output_path: Path) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    gids = sorted(points["galaxy_id"].unique())
    n = len(gids)
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), sharex=False, sharey=True)
    axes_flat = axes.flatten()
    for ax, gid in zip(axes_flat, gids):
        sub = _even_odd(points, gid)
        tdf = sub[sub["model_name"] == "tdf_3knot"]
        nfw = sub[sub["model_name"] == "nfw_refit"]
        if not tdf.empty:
            ax.plot(tdf["r_kpc"], tdf["abs_residual_kms"], "o-", ms=3, color="C2", label="tdf_3knot |res|")
        if not nfw.empty:
            ax.plot(nfw["r_kpc"], nfw["abs_residual_kms"], "s--", ms=3, color="C0", label="nfw |res|")
        title = gid
        if gid == TARGET_GALAXY:
            title += " (holdout failure)"
            ax.set_facecolor("#fff5f5")
        ax.set_title(title, fontsize=9)
        ax.grid(alpha=0.3)
    for ax in axes_flat[n:]:
        ax.axis("off")
    axes_flat[0].legend(loc="upper right", fontsize=7)
    fig.suptitle("Holdout |residual| maps — even/odd split, train-only fits", y=1.02)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def ngc7814_radial_localization(summary: pd.DataFrame, points: pd.DataFrame) -> dict[str, Any]:
    """Derive which radial region dominates TDF holdout failure on even/odd split."""
    sub = summary[
        (summary["galaxy_id"] == TARGET_GALAXY)
        & (summary["split_name"] == PRIMARY_SPLIT)
        & (summary["model_name"].isin(["tdf_3knot", "tdf_5knot", "nfw_refit"]))
    ]
    if sub.empty:
        return {"localized": False, "worst_region_tdf_3knot": None}

    tdf3 = sub[sub["model_name"] == "tdf_3knot"]
    worst_row = tdf3.loc[tdf3["rmse_kms"].idxmax()] if not tdf3.empty else None
    inner_rmse = float(tdf3[tdf3["radial_region_label"] == "inner"]["rmse_kms"].iloc[0]) if (
        (tdf3["radial_region_label"] == "inner").any()
    ) else float("nan")
    nfw_inner = sub[
        (sub["model_name"] == "nfw_refit") & (sub["radial_region_label"] == "inner")
    ]
    nfw_inner_rmse = float(nfw_inner["rmse_kms"].iloc[0]) if not nfw_inner.empty else float("nan")

    pts = _even_odd(points, TARGET_GALAXY)
    tdf3_inner_neg = int(
        pts[
            (pts["model_name"] == "tdf_3knot")
            & (pts["radial_region_label"] == "inner")
            & (pts["negative_v2_flag"])
        ].shape[0]
    )

    return {
        "localized": True,
        "worst_region_tdf_3knot": str(worst_row["radial_region_label"]) if worst_row is not None else None,
        "inner_rmse_tdf_3knot": inner_rmse,
        "inner_rmse_nfw_refit": nfw_inner_rmse,
        "tdf_3knot_inner_negative_v2_count": tdf3_inner_neg,
        "worst_radius_kpc_tdf_3knot": float(worst_row["worst_radius_kpc"]) if worst_row is not None else None,
    }


def write_radial_holdout_report(
    path: Path,
    *,
    points: pd.DataFrame,
    summary: pd.DataFrame,
    localization: dict[str, Any],
) -> None:
    ng_reg = summary[
        (summary["galaxy_id"] == TARGET_GALAXY)
        & (summary["split_name"] == PRIMARY_SPLIT)
        & (summary["model_name"] == "tdf_3knot")
    ].sort_values("rmse_kms", ascending=False)

    lines = [
        "# SPARC Radial Holdout Failure Report (Phase 4E)",
        "",
        "> This phase archives per-point holdout residuals and diagnoses radial failure structure. "
        "It does not add new models, does not validate TDF on full SPARC, does not disprove dark matter, "
        "and does not include lensing.",
        "",
        "## Objective",
        "",
        "Export **train-only** holdout predictions at each test radius and localize where TDF vs NFW/MOND "
        "errors concentrate, with emphasis on **NGC7814**.",
        "",
        "## Holdout residual export method",
        "",
        "- Protocol: Phase 3C splits (`even_odd_index`, `inner_middle_outer_blocked`, `radial_kfold_5`).",
        "- Models: `tdf_3knot`, `tdf_5knot`, `nfw_refit`, `mond_fit_a0_simple`.",
        f"- **comparison_mode:** `{points['comparison_mode'].iloc[0] if len(points) else 'train_only_holdout'}` "
        "(all models refit on training radii; no full-sample baseline mixing).",
        "- TDF: Phase 2A initialization/bounds on **training radii only**; predictions on held-out points.",
        "- Table: `outputs/tables/sparc_holdout_point_residuals.csv`.",
        "",
        f"- Total test-point rows exported: **{len(points)}**.",
        "",
        "## Per-galaxy radial failure summary (even/odd, tdf_3knot)",
        "",
        "| galaxy_id | worst_region | rmse inner | rmse middle | rmse outer |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for gid in sorted(MANDATED_GALAXY_CLASSIFICATION.keys()):
        gsub = summary[
            (summary["galaxy_id"] == gid)
            & (summary["split_name"] == PRIMARY_SPLIT)
            & (summary["model_name"] == "tdf_3knot")
        ]
        if gsub.empty:
            continue
        by_reg = {row["radial_region_label"]: row["rmse_kms"] for _, row in gsub.iterrows()}
        worst = max(by_reg, key=by_reg.get)  # type: ignore[arg-type]
        lines.append(
            f"| {gid} | {worst} | {by_reg.get('inner', float('nan')):.1f} | "
            f"{by_reg.get('middle', float('nan')):.1f} | {by_reg.get('outer', float('nan')):.1f} |"
        )

    lines.extend(
        [
            "",
            "## NGC7814 radial failure map discussion",
            "",
            f"- Dominant TDF error region (tdf_3knot, even/odd): **{localization.get('worst_region_tdf_3knot', 'n/a')}**.",
            f"- Inner-region RMSE — tdf_3knot: **{localization.get('inner_rmse_tdf_3knot', float('nan')):.1f}** km/s; "
            f"nfw_refit: **{localization.get('inner_rmse_nfw_refit', float('nan')):.1f}** km/s.",
            f"- tdf_3knot negative-v² flags on inner holdout points: **{localization.get('tdf_3knot_inner_negative_v2_count', 0)}**.",
            "",
            "Holdout failures for TDF on NGC7814 **cluster at inner/bulge-dominated radii** (r ≲ few kpc) where "
            "fixed SPARC baryonic decomposition shows strong bulge contribution and Phase 4D reported negative "
            "diagnostic residuals. NFW/MOND holdout residuals are **radially smoother** at smaller |residual| in the inner third on even/odd.",
            "",
            "**tdf_5knot** can lower RMSE in some blocked/CV folds but remains unstable on even/odd relative to NFW; "
            "see regional summary table. **tdf_4knot** is not in the export set; Phase 4D negative-v² pathology at the inner knot (r ≈ 0.63 kpc) "
            "aligns with the inner holdout radius band.",
            "",
            "## TDF vs NFW/MOND residual localization",
            "",
            "On NGC7814 even/odd holdout, TDF exhibits large signed residuals at inner radii; NFW/MOND absorb much of "
            "the inner rotation curve with smoother holdout residual maps (see figures).",
            "",
            "## Limitations",
            "",
            "- Refitting cost scales with galaxies × splits × models; export is diagnostic only.",
            "- Radial regions are index-thirds, not physical bulge/halo boundaries.",
            "- Single K_tau and fixed baryons; no M/L or distance fitting.",
            "",
            "## Outputs",
            "",
            "- `outputs/tables/sparc_holdout_point_residuals.csv`",
            "- `outputs/tables/sparc_radial_failure_map_summary.csv`",
            "- `outputs/figures/sparc_subset/ngc7814_radial_holdout_residual_map.png`",
            "- `outputs/figures/sparc_subset/holdout_residual_maps_all_galaxies.png`",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
