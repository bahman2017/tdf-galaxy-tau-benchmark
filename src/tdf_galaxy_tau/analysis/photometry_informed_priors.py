from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.analysis.ml_priors import (
    GALAXY_ORDER,
    MODELS,
    MOND_MODEL,
    NFW_MODEL,
    TARGET_GALAXY,
    TDF_PRIMARY,
    TDF_SENSITIVITY,
    _pivot_cell_rmse,
    _weighted_mean,
    _weighted_median,
    _winner_model,
    classify_ngc7814_layered,
    load_ml_priors_config,
)
from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION

PHOTOMETRY_PRIOR_LOGIC_VERSION = "phase_4k_photometry_informed"
DISK_SCALES = (0.5, 0.7, 1.0, 1.3)
BULGE_SCALES = (0.2, 0.5, 0.7, 1.0, 1.3)


@dataclass(frozen=True)
class PhotometryInformedScenario:
    name: str
    description: str
    grid_scope: str
    weighting: str
    metadata_basis: str
    galaxy_filter: str | None
    params: dict[str, Any]


def parse_photometry_informed_scenarios(config: dict[str, Any]) -> list[PhotometryInformedScenario]:
    block = config.get("photometry_informed_scenarios", {})
    out: list[PhotometryInformedScenario] = []
    for name, spec in block.items():
        if not isinstance(spec, dict):
            continue
        skip = {"description", "grid_scope", "weighting", "metadata_basis", "galaxy_filter"}
        params = {k: v for k, v in spec.items() if k not in skip}
        out.append(
            PhotometryInformedScenario(
                name=name,
                description=str(spec.get("description", "")),
                grid_scope=str(spec.get("grid_scope", "plausible_only")),
                weighting=str(spec.get("weighting", "uniform")),
                metadata_basis=str(spec.get("metadata_basis", name)),
                galaxy_filter=spec.get("galaxy_filter"),
                params=params,
            )
        )
    return out


def _plausible_band(config: dict[str, Any]) -> tuple[tuple[float, float], tuple[float, float]]:
    pl = config.get("plausible_band", {})
    return (
        tuple(pl.get("disk_scale", [0.7, 1.3])),
        tuple(pl.get("bulge_scale", [0.5, 1.0])),
    )


def _canonical_ml(config: dict[str, Any]) -> tuple[float, float]:
    can = config.get("canonical_ml", {})
    return float(can.get("disk_scale", 1.0)), float(can.get("bulge_scale", 1.0))


def cell_in_photometry_scope(
    disk_scale: float,
    bulge_scale: float,
    scenario: PhotometryInformedScenario,
    *,
    plausible_disk: tuple[float, float],
    plausible_bulge: tuple[float, float],
) -> bool:
    if scenario.grid_scope == "all_grid":
        return True
    return (
        plausible_disk[0] <= disk_scale <= plausible_disk[1]
        and plausible_bulge[0] <= bulge_scale <= plausible_bulge[1]
    )


def photometry_cell_weight(
    galaxy_id: str,
    disk_scale: float,
    bulge_scale: float,
    scenario: PhotometryInformedScenario,
    *,
    photo_row: pd.Series,
    subset_row: pd.Series | None,
    plausible_disk: tuple[float, float],
    plausible_bulge: tuple[float, float],
    canonical_disk: float,
    canonical_bulge: float,
) -> float:
    if scenario.galaxy_filter and galaxy_id != scenario.galaxy_filter:
        return 0.0
    if not cell_in_photometry_scope(
        disk_scale, bulge_scale, scenario, plausible_disk=plausible_disk, plausible_bulge=plausible_bulge
    ):
        return 0.0

    w = scenario.weighting

    if w == "uniform":
        return 1.0

    if w == "morphology_aware":
        morph = float(photo_row.get("morphological_type", np.nan))
        bulge_dom = bool(subset_row.get("bulge_dominated_proxy", False)) if subset_row is not None else False
        has_bulge = bool(subset_row.get("has_bulge_proxy", False)) if subset_row is not None else False
        early_type = bool(np.isfinite(morph) and morph <= 2.0) or bulge_dom or has_bulge

        disk_kernel = float(np.exp(-0.5 * ((disk_scale - 1.0) / 0.28) ** 2))
        if early_type:
            if bulge_scale < plausible_bulge[0]:
                bulge_kernel = 0.15 + 0.85 * (bulge_scale / plausible_bulge[0])
            else:
                bulge_kernel = float(np.exp(-0.5 * ((bulge_scale - 0.85) / 0.2) ** 2))
            return max(disk_kernel * bulge_kernel, 0.01)

        bulge_kernel = float(np.exp(-0.5 * ((bulge_scale - 0.75) / 0.22) ** 2))
        return max(disk_kernel * (0.25 + 0.75 * bulge_kernel), 0.01)

    if w == "ngc7814_bulge_diagnostic":
        bulge_kernel = max(1.3 - bulge_scale, 0.05)
        disk_kernel = max(1.0 - 0.35 * abs(disk_scale - 0.7), 0.15)
        return bulge_kernel * disk_kernel

    if w == "gaussian_anchor":
        sd = float(scenario.params.get("sigma_disk", 0.15))
        sb = float(scenario.params.get("sigma_bulge", 0.15))
        zd = (disk_scale - canonical_disk) / sd
        zb = (bulge_scale - canonical_bulge) / sb
        return float(np.exp(-0.5 * (zd * zd + zb * zb)))

    return 0.0


def build_photometry_informed_prior_weights(
    photometry: pd.DataFrame,
    subset_context: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    plausible_disk, plausible_bulge = _plausible_band(config)
    c_disk, c_bulge = _canonical_ml(config)
    subset_by_gid = subset_context.set_index("galaxy_id") if not subset_context.empty else pd.DataFrame()
    photo_by_gid = photometry.set_index("galaxy_id")

    rows: list[dict[str, Any]] = []
    for scenario in parse_photometry_informed_scenarios(config):
        for gid in GALAXY_ORDER:
            if gid not in photo_by_gid.index:
                continue
            photo_row = photo_by_gid.loc[gid] if gid in photo_by_gid.index else pd.Series(dtype=float)
            subset_row = subset_by_gid.loc[gid] if gid in subset_by_gid.index else None
            cell_weights: list[float] = []
            for d in DISK_SCALES:
                for b in BULGE_SCALES:
                    w = photometry_cell_weight(
                        gid,
                        d,
                        b,
                        scenario,
                        photo_row=photo_row,
                        subset_row=subset_row,
                        plausible_disk=plausible_disk,
                        plausible_bulge=plausible_bulge,
                        canonical_disk=c_disk,
                        canonical_bulge=c_bulge,
                    )
                    cell_weights.append(w)
            total = float(sum(cell_weights))
            for (d, b), raw in zip(
                [(dd, bb) for dd in DISK_SCALES for bb in BULGE_SCALES],
                cell_weights,
            ):
                norm = raw / total if total > 0 else 0.0
                rows.append(
                    {
                        "galaxy_id": gid,
                        "scenario_name": scenario.name,
                        "disk_scale": d,
                        "bulge_scale": b,
                        "raw_weight": raw,
                        "normalized_weight": norm,
                        "metadata_basis": scenario.metadata_basis,
                        "diagnostic_only": True,
                        "interpretation_note": _weight_interpretation_note(
                            gid, scenario, d, b, photo_row, subset_row
                        ),
                    }
                )
    return pd.DataFrame(rows)


def _weight_interpretation_note(
    gid: str,
    scenario: PhotometryInformedScenario,
    disk_scale: float,
    bulge_scale: float,
    photo_row: pd.Series,
    subset_row: pd.Series | None,
) -> str:
    if scenario.weighting == "ngc7814_bulge_diagnostic":
        return "NGC7814-only diagnostic: favors lower bulge_scale cells; not calibrated bulge M/L."
    if scenario.weighting == "morphology_aware":
        t = photo_row.get("morphological_type", np.nan)
        bd = subset_row.get("bulge_dominated_proxy", False) if subset_row is not None else False
        return (
            f"Morphology-aware scaffold (Type={t}, bulge_dom={bd}); "
            "early-type/bulge-proxy galaxies do not auto-favor extreme low bulge_scale."
        )
    if scenario.weighting == "gaussian_anchor":
        return "Canonical M/L=1 anchor; preserves reference to fixed SPARC decomposition."
    return "Uniform diagnostic weight over plausible M/L band."


def _photometry_metrics_for_galaxy(
    galaxy_df: pd.DataFrame,
    weight_map: dict[tuple[float, float], float],
    *,
    gid: str,
    scenario_name: str,
) -> list[dict[str, Any]]:
    cells = _pivot_cell_rmse(galaxy_df)
    w_arr = np.array(
        [weight_map.get((float(r.disk_scale), float(r.bulge_scale)), 0.0) for _, r in cells.iterrows()]
    )
    total_w = float(w_arr.sum())
    if total_w <= 0:
        return []

    winners = cells.apply(_winner_model, axis=1)
    plausible_mask = cells["plausible_scale_flag"].to_numpy()

    def _beats(model: str, baseline: str) -> np.ndarray:
        return np.array(
            [
                np.isfinite(cells[model].iloc[i])
                and np.isfinite(cells[baseline].iloc[i])
                and cells[model].iloc[i] < cells[baseline].iloc[i]
                for i in range(len(cells))
            ]
        )

    beats_3_nfw = _beats(TDF_PRIMARY, NFW_MODEL)
    beats_3_mond = _beats(TDF_PRIMARY, MOND_MODEL)
    beats_5_nfw = _beats(TDF_SENSITIVITY, NFW_MODEL)
    beats_5_mond = _beats(TDF_SENSITIVITY, MOND_MODEL)

    frac_3_nfw = float(w_arr[beats_3_nfw].sum() / total_w)
    frac_3_mond = float(w_arr[beats_3_mond].sum() / total_w)
    frac_5_nfw = float(w_arr[beats_5_nfw].sum() / total_w)
    frac_5_mond = float(w_arr[beats_5_mond].sum() / total_w)

    scenario_metrics = {
        "tdf3_wins": float(w_arr[winners == TDF_PRIMARY].sum() / total_w),
        "tdf5_wins": float(w_arr[winners == TDF_SENSITIVITY].sum() / total_w),
    }

    rows_out: list[dict[str, Any]] = []
    for model in MODELS:
        rmse_vals = cells[model].to_numpy(dtype=float)
        pl_rmse = rmse_vals[plausible_mask]
        rows_out.append(
            {
                "galaxy_id": gid,
                "scenario_name": scenario_name,
                "model_name": model,
                "prior_weighted_mean_rmse": _weighted_mean(rmse_vals, w_arr),
                "prior_weighted_median_rmse": _weighted_median(rmse_vals, w_arr),
                "best_plausible_rmse": float(np.nanmin(pl_rmse)) if len(pl_rmse) else float("nan"),
                "fraction_prior_weight_model_wins": float(w_arr[winners == model].sum() / total_w),
                "fraction_prior_weight_tdf_3knot_beats_nfw": frac_3_nfw,
                "fraction_prior_weight_tdf_3knot_beats_mond": frac_3_mond,
                "fraction_prior_weight_tdf_5knot_beats_nfw": frac_5_nfw,
                "fraction_prior_weight_tdf_5knot_beats_mond": frac_5_mond,
                "recommended_interpretation": _galaxy_scenario_interpretation(
                    gid, scenario_name, model, scenario_metrics
                ),
            }
        )
    return rows_out


def compute_photometry_prior_weighted_summary(
    comparison: pd.DataFrame,
    weights: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for gid in GALAXY_ORDER:
        g_comp = comparison[comparison["galaxy_id"] == gid]
        if g_comp.empty:
            continue
        for scenario_name in weights["scenario_name"].unique():
            w_sub = weights[(weights["galaxy_id"] == gid) & (weights["scenario_name"] == scenario_name)]
            if w_sub.empty:
                continue
            weight_map = {
                (float(r.disk_scale), float(r.bulge_scale)): float(r.normalized_weight)
                for r in w_sub.itertuples(index=False)
            }
            rows.extend(_photometry_metrics_for_galaxy(g_comp, weight_map, gid=gid, scenario_name=scenario_name))
    return pd.DataFrame(rows)


def _galaxy_scenario_interpretation(
    gid: str,
    scenario_name: str,
    model: str,
    scenario_metrics: dict[str, float],
) -> str:
    tdf3_wins = scenario_metrics.get("tdf3_wins", 0.0)
    tdf5_wins = scenario_metrics.get("tdf5_wins", 0.0)
    if gid == TARGET_GALAXY and scenario_name == "canonical_anchor_prior":
        return "Canonical-anchor prior: NGC7814 canonical tdf_3knot failure at M/L=1 unchanged."
    if gid == TARGET_GALAXY and scenario_name == "ngc7814_bulge_sensitivity_diagnostic":
        if model == TDF_SENSITIVITY and tdf5_wins > tdf3_wins:
            return "Diagnostic lower-bulge weights favor tdf_5knot (sensitivity), not primary tdf_3knot."
        return "NGC7814 bulge-sensitivity diagnostic; not calibrated bulge M/L."
    if MANDATED_GALAXY_CLASSIFICATION.get(gid) == "robust_tdf_success":
        if model == TDF_PRIMARY and tdf3_wins >= 0.25:
            return "Photometry-informed prior: stable primary tdf_3knot support on success galaxy."
        if model in (NFW_MODEL, MOND_MODEL) and tdf3_wins < 0.2:
            return "Baseline competitive under morphology-aware photometry prior."
        return "Moderate photometry-informed prior support."
    return "See photometry prior report."


def _summary_to_prior_by_model(sub: pd.DataFrame) -> dict[str, pd.Series]:
    out: dict[str, pd.Series] = {}
    for _, r in sub.iterrows():
        model = str(r["model_name"])
        out[model] = pd.Series(
            {
                "prior_weighted_mean_rmse": r["prior_weighted_mean_rmse"],
                "fraction_of_prior_weight_where_model_wins": r["fraction_prior_weight_model_wins"],
                "fraction_of_prior_weight_where_tdf_beats_nfw": (
                    r["fraction_prior_weight_tdf_3knot_beats_nfw"]
                    if model == TDF_PRIMARY
                    else r["fraction_prior_weight_tdf_5knot_beats_nfw"]
                ),
                "fraction_of_prior_weight_where_tdf_beats_mond": (
                    r["fraction_prior_weight_tdf_3knot_beats_mond"]
                    if model == TDF_PRIMARY
                    else r["fraction_prior_weight_tdf_5knot_beats_mond"]
                ),
            }
        )
    return out


def build_ngc7814_photometry_prior_interpretation(
    summary: pd.DataFrame,
    *,
    post_ml_path: Path | str = "outputs/tables/sparc_post_ml_results_summary_table.csv",
) -> pd.DataFrame:
    can_tdf, can_nfw = _canonical_rmse_from_post_ml(post_ml_path)
    rows: list[dict[str, Any]] = []
    for scenario_name in summary["scenario_name"].unique():
        sub = summary[(summary["galaxy_id"] == TARGET_GALAXY) & (summary["scenario_name"] == scenario_name)]
        by_model = _summary_to_prior_by_model(sub)
        layered = classify_ngc7814_layered(by_model, canonical_tdf_rmse=can_tdf, canonical_nfw_rmse=can_nfw)
        nfw_row = by_model.get(NFW_MODEL, pd.Series(dtype=float))
        mond_row = by_model.get(MOND_MODEL, pd.Series(dtype=float))
        nfw_wins = float(nfw_row.get("fraction_prior_weight_model_wins", 0))
        mond_wins = float(mond_row.get("fraction_prior_weight_model_wins", 0))
        if nfw_wins > mond_wins:
            nfw_mond = "prior_weighted_nfw_preferred"
        elif mond_wins > nfw_wins:
            nfw_mond = "prior_weighted_mond_preferred"
        else:
            nfw_mond = "prior_weighted_nfw_mond_mixed"

        rows.append(
            {
                "scenario_name": scenario_name,
                "canonical_result": layered["canonical_result"],
                "primary_tdf_3knot_prior_result": layered["primary_tdf_3knot_prior_result"],
                "sensitivity_tdf_5knot_prior_result": layered["sensitivity_tdf_5knot_prior_result"],
                "either_tdf_variant_prior_result": layered["either_tdf_variant_prior_result"],
                "nfw_mond_prior_result": nfw_mond,
                "recommended_claim_language": layered["recommended_claim_language"],
                "caveat": (
                    "Photometry-informed diagnostic prior only; no bulge L_3.6; not final M/L calibration. "
                    "Primary conservative model is tdf_3knot."
                ),
            }
        )
    return pd.DataFrame(rows)


def _canonical_rmse_from_post_ml(path: Path | str) -> tuple[float, float]:
    p = Path(path)
    if not p.is_file():
        return float("nan"), float("nan")
    post = pd.read_csv(p)
    ngc = post[post["galaxy_id"] == TARGET_GALAXY]
    if ngc.empty:
        return float("nan"), float("nan")
    row = ngc.iloc[0]
    return float(row["canonical_tdf_3knot_rmse"]), float(row["canonical_nfw_rmse"])


def write_photometry_informed_prior_report(
    path: Path,
    *,
    weights: pd.DataFrame,
    summary: pd.DataFrame,
    ngc_interp: pd.DataFrame,
    subset_ctx: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    ngc = subset_ctx[subset_ctx["galaxy_id"] == TARGET_GALAXY].iloc[0]
    success = subset_ctx[subset_ctx["galaxy_id"] != TARGET_GALAXY]
    lines = [
        "# SPARC Photometry-Informed M/L Prior Report (Phase 4K)",
        "",
        "> This phase constructs diagnostic photometry-informed M/L prior weights. "
        "It does not perform final M/L calibration, does not rerun model fits, "
        "does not validate TDF on full SPARC, does not disprove dark matter, "
        "and does not include lensing.",
        "",
        "## Objective",
        "",
        "Replace purely placeholder Phase 4I prior scenarios with **metadata-informed diagnostic** "
        "weights over the existing Phase 4G scaled-holdout grid, using Phase 4J photometry context.",
        "",
        "## Metadata source and limitations",
        "",
        f"- {config.get('photometry_metadata_status', {}).get('note', '')}",
        "- No explicit bulge luminosity; morphology and central-concentration proxies only.",
        "- This is a **photometry-informed scaffold**, not a stellar-population-calibrated prior.",
        "",
        "## Prior scenarios",
        "",
    ]
    for sc in parse_photometry_informed_scenarios(config):
        lines.append(f"- **{sc.name}:** {sc.description} (`{sc.metadata_basis}`)")

    lines.extend(
        [
            "",
            "## How metadata influences weights",
            "",
            "- **morphological_type** and **bulge_dominated_proxy** gate bulge_scale emphasis.",
            "- Early-type / bulge-proxy systems avoid automatically favoring extreme low bulge_scale.",
            "- Disk-dominated success galaxies emphasize disk_scale near unity.",
            "- NGC7814 has a dedicated diagnostic scenario testing lower-bulge support.",
            "",
            "## Six-galaxy summary",
            "",
            "| Galaxy | Class | Bulge-dom proxy | Notes |",
            "| --- | --- | --- | --- |",
        ]
    )
    for _, r in subset_ctx.iterrows():
        lines.append(
            f"| {r['galaxy_id']} | {r['canonical_classification']} | {r['bulge_dominated_proxy']} | "
            f"{r['notes_for_ml_prior'][:60]}... |"
        )

    lines.extend(
        [
            "",
            "## NGC7814 interpretation",
            "",
            f"- {ngc['notes_for_ml_prior']}",
            "",
        ]
    )
    for _, r in ngc_interp.iterrows():
        lines.extend(
            [
                f"### Scenario: {r['scenario_name']}",
                f"- {r['recommended_claim_language']}",
                f"- Primary tdf_3knot: `{r['primary_tdf_3knot_prior_result']}`",
                f"- Sensitivity tdf_5knot: `{r['sensitivity_tdf_5knot_prior_result']}`",
                f"- {r['caveat']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Difference: tdf_3knot vs tdf_5knot",
            "",
            "Photometry-informed priors can increase **tdf_5knot** weighted win fraction "
            "without improving **tdf_3knot** (primary conservative model). "
            "Any recovery language must specify which TDF variant and must not imply final calibration.",
            "",
            "## Why this is not final M/L calibration",
            "",
            "Missing bulge L_3.6, no fitted M/L parameters, and weights are diagnostic scaffolds over a fixed Cartesian grid.",
            "",
            "## Next required data",
            "",
            "- Explicit bulge luminosity or stellar-population priors",
            "- Photometry quality flags per galaxy",
            "- Independent validation before external claims",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_ngc7814_photometry_prior_distribution(
    weights: pd.DataFrame,
    output_path: Path,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    sub = weights[(weights["galaxy_id"] == TARGET_GALAXY)]
    scenarios = list(sub["scenario_name"].unique())
    fig, axes = plt.subplots(1, len(scenarios), figsize=(4 * len(scenarios), 4), sharey=True)
    if len(scenarios) == 1:
        axes = [axes]
    for ax, sc in zip(axes, scenarios):
        s = sub[sub["scenario_name"] == sc]
        pivot = s.pivot_table(
            index="bulge_scale", columns="disk_scale", values="normalized_weight", aggfunc="first"
        )
        im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd")
        ax.set_title(sc.replace("_", "\n"), fontsize=8)
        ax.set_xlabel("disk_scale")
        ax.set_ylabel("bulge_scale")
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle(f"{TARGET_GALAXY} — photometry-informed prior weights (Phase 4K)")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_photometry_prior_model_support(
    summary: pd.DataFrame,
    output_path: Path,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    sc = "morphology_aware_conservative"
    sub = summary[
        (summary["scenario_name"] == sc)
        & (summary["model_name"].isin([TDF_PRIMARY, TDF_SENSITIVITY, NFW_MODEL]))
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(sub["galaxy_id"].unique()))
    gids = sorted(sub["galaxy_id"].unique())
    width = 0.25
    for i, model in enumerate([TDF_PRIMARY, TDF_SENSITIVITY, NFW_MODEL]):
        vals = [
            float(
                sub[(sub["galaxy_id"] == g) & (sub["model_name"] == model)][
                    "fraction_prior_weight_model_wins"
                ].iloc[0]
            )
            for g in gids
        ]
        ax.bar(np.arange(len(gids)) + (i - 1) * width, vals, width, label=model)
    ax.set_xticks(np.arange(len(gids)))
    ax.set_xticklabels(gids, rotation=30, ha="right")
    ax.set_ylabel("prior-weight win fraction")
    ax.set_title(f"Photometry-informed prior: {sc}")
    ax.legend(fontsize=8)
    ax.set_ylim(0, 1.05)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def run_photometry_informed_prior_pipeline(
    *,
    photometry_path: Path | str = "data/processed/sparc/sparc_photometry_metadata.csv",
    subset_context_path: Path | str = "outputs/tables/sparc_subset_photometry_context.csv",
    comparison_path: Path | str = "outputs/tables/sparc_ml_scaled_model_comparison.csv",
    config_path: Path | str = "configs/ml_priors.yaml",
    weights_out: Path | str = "outputs/tables/sparc_photometry_informed_prior_weights.csv",
    summary_out: Path | str = "outputs/tables/sparc_photometry_prior_weighted_summary.csv",
    ngc_out: Path | str = "outputs/tables/ngc7814_photometry_prior_interpretation.csv",
    report_out: Path | str = "outputs/reports/sparc_photometry_informed_prior_report.md",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    config = load_ml_priors_config(config_path)
    photometry = pd.read_csv(photometry_path)
    subset_ctx = pd.read_csv(subset_context_path)
    comparison = pd.read_csv(comparison_path)

    weights = build_photometry_informed_prior_weights(photometry, subset_ctx, config)
    summary = compute_photometry_prior_weighted_summary(comparison, weights)
    ngc_interp = build_ngc7814_photometry_prior_interpretation(
        summary, post_ml_path="outputs/tables/sparc_post_ml_results_summary_table.csv"
    )

    weights.to_csv(weights_out, index=False)
    summary.to_csv(summary_out, index=False)
    ngc_interp.to_csv(ngc_out, index=False)
    write_photometry_informed_prior_report(
        report_out,
        weights=weights,
        summary=summary,
        ngc_interp=ngc_interp,
        subset_ctx=subset_ctx,
        config=config,
    )
    plot_ngc7814_photometry_prior_distribution(
        weights, "outputs/figures/sparc_subset/ngc7814_photometry_prior_weight_distribution.png"
    )
    plot_photometry_prior_model_support(
        summary, "outputs/figures/sparc_subset/photometry_prior_model_support_summary.png"
    )
    return weights, summary, ngc_interp
