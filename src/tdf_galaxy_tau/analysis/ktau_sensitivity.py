from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.analysis.ml_priors import (
    GALAXY_ORDER,
    MOND_MODEL,
    NFW_MODEL,
    TARGET_GALAXY,
    TDF_PRIMARY,
    TDF_SENSITIVITY,
    _pivot_cell_rmse,
    _weighted_mean,
    _winner_model,
    classify_ngc7814_layered,
)
from tdf_galaxy_tau.analysis.ml_sensitivity import (
    DEFAULT_BULGE_SCALES,
    DEFAULT_DISK_SCALES,
    is_plausible_scale,
    reconstruct_scaled_tau_table,
    scaled_galaxy_frame,
)
from tdf_galaxy_tau.metrics.comparison import rmse
from tdf_galaxy_tau.reconstruction.radial_tau import load_reconstruction_config
from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION
from tdf_galaxy_tau.validation.holdout import even_odd_radial_split, mask_from_indices, radial_region_label_for_index
from tdf_galaxy_tau.validation.holdout_residuals import (
    _export_tdf_test_points,
    load_holdout_export_configs,
)

ANALYSIS_STAGE = "phase_4l_photometry_prior_ktau_sensitivity"
DEFAULT_KTAU_VALUES = (0.5, 1.0, 2.0)
OPTIONAL_KTAU_VALUES = (0.25, 4.0)
TDF_MODELS = (TDF_PRIMARY, TDF_SENSITIVITY)


def load_ktau_sensitivity_config(recon_path: Path | str = "configs/reconstruction.yaml") -> dict[str, Any]:
    cfg = yaml.safe_load(Path(recon_path).read_text(encoding="utf-8")) or {}
    block = cfg.get("photometry_prior_ktau_sensitivity", {})
    audit = cfg.get("tdf_robustness_audit", {})
    k_vals = [float(x) for x in block.get("k_tau_values", audit.get("k_tau_values", list(DEFAULT_KTAU_VALUES)))]
    optional = [float(x) for x in block.get("optional_k_tau_values", list(OPTIONAL_KTAU_VALUES))]
    include_opt = bool(block.get("include_optional", False))
    if include_opt:
        k_vals = sorted(set(k_vals + optional))
    return {
        "k_tau_values": k_vals,
        "stability_rtol": float(block.get("stability_rtol", 0.15)),
        "win_fraction_tol": float(block.get("win_fraction_tol", 0.12)),
        "reference_k_tau": float(block.get("reference_k_tau", 1.0)),
    }


def run_scaled_tdf_holdout_at_ktau(
    g_scaled: pd.DataFrame,
    tau_df: pd.DataFrame,
    galaxy_id: str,
    model_name: str,
    *,
    k_tau: float,
    recon_yaml: dict,
    models_yaml: dict,
    n_points: int,
) -> dict[str, Any]:
    from tdf_galaxy_tau.models.tdf_knot import load_tdf_knot_config

    tdf_cfg = load_tdf_knot_config(recon_yaml)
    r = g_scaled["r_kpc"].to_numpy(dtype=float)
    v_obs = g_scaled["v_obs_kms"].to_numpy(dtype=float)
    v_err = g_scaled["v_err_kms"].to_numpy(dtype=float)
    v_bar = g_scaled["v_bar_kms"].to_numpy(dtype=float)
    split = even_odd_radial_split(n_points)
    data_mode = str(g_scaled["data_mode"].iloc[0]) if "data_mode" in g_scaled.columns else "unknown"

    rows = _export_tdf_test_points(
        galaxy_id,
        r,
        v_obs,
        v_err,
        v_bar,
        tau_df,
        model_name,
        split.name,
        split.train_indices,
        split.test_indices,
        k_g=float(k_tau),
        safety_factor=tdf_cfg.amplitude_bound_safety_factor,
        negative_v2_penalty=tdf_cfg.negative_v2_penalty,
        data_mode=data_mode,
        n_points=n_points,
    )
    if not rows:
        return {
            "total_holdout_rmse_kms": float("nan"),
            "fit_success": False,
            "fit_status": "no_points",
            "negative_v2_count": 0,
        }
    df = pd.DataFrame(rows)
    return {
        "total_holdout_rmse_kms": float(rmse(df["v_obs_kms"], df["v_pred_kms"])),
        "fit_success": bool(rows[0]["fit_success"]),
        "fit_status": str(rows[0]["fit_status"]),
        "negative_v2_count": int(sum(1 for row in rows if row.get("negative_v2_flag"))),
    }


def run_ktau_tdf_grid(
    rotmod: pd.DataFrame,
    selected_ids: list[str],
    k_tau_values: list[float],
    *,
    recon_path: Path | str = "configs/reconstruction.yaml",
    models_path: Path | str = "configs/models.yaml",
    disk_scales: tuple[float, ...] = DEFAULT_DISK_SCALES,
    bulge_scales: tuple[float, ...] = DEFAULT_BULGE_SCALES,
) -> pd.DataFrame:
    recon_yaml, models_yaml = load_holdout_export_configs(recon_path, models_path)
    tau_config = load_reconstruction_config(recon_path)
    rows: list[dict[str, Any]] = []

    for gid in selected_ids:
        g = rotmod[rotmod["galaxy_id"] == gid].copy()
        if g.empty:
            continue
        n_points = len(g)
        for disk_scale in disk_scales:
            for bulge_scale in bulge_scales:
                g_scaled = scaled_galaxy_frame(g, disk_scale=disk_scale, bulge_scale=bulge_scale)
                tau_df = reconstruct_scaled_tau_table(g_scaled, gid, tau_config)
                plausible = is_plausible_scale(disk_scale, bulge_scale)
                for k_tau in k_tau_values:
                    for model_name in TDF_MODELS:
                        metrics = run_scaled_tdf_holdout_at_ktau(
                            g_scaled,
                            tau_df,
                            gid,
                            model_name,
                            k_tau=k_tau,
                            recon_yaml=recon_yaml,
                            models_yaml=models_yaml,
                            n_points=n_points,
                        )
                        rows.append(
                            {
                                "galaxy_id": gid,
                                "disk_scale": disk_scale,
                                "bulge_scale": bulge_scale,
                                "plausible_scale_flag": plausible,
                                "model_name": model_name,
                                "K_tau": float(k_tau),
                                "total_holdout_rmse_kms": metrics["total_holdout_rmse_kms"],
                                "fit_success": metrics["fit_success"],
                                "fit_status": metrics["fit_status"],
                                "negative_v2_count": metrics["negative_v2_count"],
                                "analysis_stage": ANALYSIS_STAGE,
                            }
                        )
    return pd.DataFrame(rows)


def merge_ktau_tdf_with_phase4g_baselines(
    tdf_grid: pd.DataFrame,
    phase4g: pd.DataFrame,
) -> pd.DataFrame:
    """Per K_tau: long-form comparison with TDF@K_tau and fixed Phase 4G NFW/MOND."""
    baselines = phase4g[
        phase4g["model_name"].isin([NFW_MODEL, MOND_MODEL])
    ][
        [
            "galaxy_id",
            "disk_scale",
            "bulge_scale",
            "plausible_scale_flag",
            "model_name",
            "total_holdout_rmse_kms",
        ]
    ].copy()
    baselines["K_tau"] = np.nan

    tdf_part = tdf_grid[
        [
            "galaxy_id",
            "disk_scale",
            "bulge_scale",
            "plausible_scale_flag",
            "model_name",
            "K_tau",
            "total_holdout_rmse_kms",
        ]
    ].copy()
    return pd.concat([tdf_part, baselines], ignore_index=True)


def _metrics_for_galaxy_scenario_ktau(
    galaxy_df: pd.DataFrame,
    weight_map: dict[tuple[float, float], float],
    *,
    gid: str,
    scenario_name: str,
    k_tau: float,
    model_name: str,
) -> dict[str, Any] | None:
    cells = _pivot_cell_rmse(galaxy_df)
    w_arr = np.array(
        [weight_map.get((float(r.disk_scale), float(r.bulge_scale)), 0.0) for _, r in cells.iterrows()]
    )
    total_w = float(w_arr.sum())
    if total_w <= 0:
        return None

    winners = cells.apply(_winner_model, axis=1)
    plausible_mask = cells["plausible_scale_flag"].to_numpy()

    def _beats(tdf_model: str, baseline: str) -> np.ndarray:
        return np.array(
            [
                np.isfinite(cells[tdf_model].iloc[i])
                and np.isfinite(cells[baseline].iloc[i])
                and cells[tdf_model].iloc[i] < cells[baseline].iloc[i]
                for i in range(len(cells))
            ]
        )

    beats_3_nfw = _beats(TDF_PRIMARY, NFW_MODEL)
    beats_3_mond = _beats(TDF_PRIMARY, MOND_MODEL)
    beats_5_nfw = _beats(TDF_SENSITIVITY, NFW_MODEL)
    beats_5_mond = _beats(TDF_SENSITIVITY, MOND_MODEL)

    rmse_vals = cells[model_name].to_numpy(dtype=float)
    pl_rmse = rmse_vals[plausible_mask]

    if model_name == TDF_PRIMARY:
        frac_beats_nfw = float(w_arr[beats_3_nfw].sum() / total_w)
        frac_beats_mond = float(w_arr[beats_3_mond].sum() / total_w)
    else:
        frac_beats_nfw = float(w_arr[beats_5_nfw].sum() / total_w)
        frac_beats_mond = float(w_arr[beats_5_mond].sum() / total_w)

    return {
        "galaxy_id": gid,
        "K_tau": k_tau,
        "scenario_name": scenario_name,
        "model_name": model_name,
        "prior_weighted_mean_rmse": _weighted_mean(rmse_vals, w_arr),
        "best_plausible_rmse": float(np.nanmin(pl_rmse)) if len(pl_rmse) else float("nan"),
        "fraction_prior_weight_model_wins": float(w_arr[winners == model_name].sum() / total_w),
        "fraction_prior_weight_tdf_beats_nfw": frac_beats_nfw,
        "fraction_prior_weight_tdf_beats_mond": frac_beats_mond,
    }


def ktau_stability_flag(
    current: dict[str, float],
    reference: dict[str, float],
    *,
    rtol: float = 0.15,
    win_tol: float = 0.12,
) -> str:
    ref_rmse = reference.get("prior_weighted_mean_rmse", float("nan"))
    cur_rmse = current.get("prior_weighted_mean_rmse", float("nan"))
    ref_win = reference.get("fraction_prior_weight_model_wins", 0.0)
    cur_win = current.get("fraction_prior_weight_model_wins", 0.0)

    if not np.isfinite(ref_rmse) or not np.isfinite(cur_rmse):
        return "insufficient_data"
    if ref_rmse <= 0:
        return "unstable"
    rel = abs(cur_rmse - ref_rmse) / ref_rmse
    win_delta = abs(cur_win - ref_win)
    if rel <= rtol and win_delta <= win_tol:
        return "stable_vs_reference_ktau"
    if rel <= rtol * 2 and win_delta <= win_tol * 2:
        return "moderate_ktau_variation"
    return "sensitive_to_ktau"


def _default_caveat() -> str:
    return (
        "K_tau is a fixed normalization convention; amplitudes refit per K_tau. "
        "Not measured, not fitted. NFW/MOND from Phase 4G at K_tau=1 reference grid."
    )


def build_ktau_sensitivity_summary(
    merged_by_ktau: dict[float, pd.DataFrame],
    weights: pd.DataFrame,
    *,
    reference_k_tau: float = 1.0,
    stability_rtol: float = 0.15,
    win_fraction_tol: float = 0.12,
) -> pd.DataFrame:
    ref_df = merged_by_ktau.get(reference_k_tau)
    if ref_df is None:
        ref_df = merged_by_ktau[sorted(merged_by_ktau.keys())[len(merged_by_ktau) // 2]]

    ref_metrics_cache: dict[tuple[str, str, str, float], dict[str, float]] = {}
    if ref_df is not None:
        for gid in GALAXY_ORDER:
            for scenario_name in weights["scenario_name"].unique():
                w_sub = weights[(weights["galaxy_id"] == gid) & (weights["scenario_name"] == scenario_name)]
                if w_sub.empty or w_sub["raw_weight"].sum() <= 0:
                    continue
                weight_map = {
                    (float(r.disk_scale), float(r.bulge_scale)): float(r.normalized_weight)
                    for r in w_sub.itertuples(index=False)
                }
                g_ref = ref_df[ref_df["galaxy_id"] == gid]
                for model in TDF_MODELS:
                    m = _metrics_for_galaxy_scenario_ktau(
                        g_ref,
                        weight_map,
                        gid=gid,
                        scenario_name=scenario_name,
                        k_tau=reference_k_tau,
                        model_name=model,
                    )
                    if m:
                        ref_metrics_cache[(gid, scenario_name, model)] = m

    rows: list[dict[str, Any]] = []
    for k_tau, comp in sorted(merged_by_ktau.items()):
        for gid in GALAXY_ORDER:
            g_comp = comp[comp["galaxy_id"] == gid]
            if g_comp.empty:
                continue
            for scenario_name in weights["scenario_name"].unique():
                w_sub = weights[(weights["galaxy_id"] == gid) & (weights["scenario_name"] == scenario_name)]
                if w_sub.empty or w_sub["raw_weight"].sum() <= 0:
                    continue
                weight_map = {
                    (float(r.disk_scale), float(r.bulge_scale)): float(r.normalized_weight)
                    for r in w_sub.itertuples(index=False)
                }
                for model in TDF_MODELS:
                    m = _metrics_for_galaxy_scenario_ktau(
                        g_comp,
                        weight_map,
                        gid=gid,
                        scenario_name=scenario_name,
                        k_tau=k_tau,
                        model_name=model,
                    )
                    if not m:
                        continue
                    ref = ref_metrics_cache.get((gid, scenario_name, model), {})
                    flag = (
                        "reference_ktau"
                        if abs(k_tau - reference_k_tau) < 1e-9
                        else ktau_stability_flag(
                            m,
                            ref,
                            rtol=stability_rtol,
                            win_tol=win_fraction_tol,
                        )
                    )
                    rows.append(
                        {
                            **m,
                            "ktau_stability_flag": flag,
                            "caveat": _default_caveat(),
                        }
                    )
    return pd.DataFrame(rows)


def _ktau_summary_to_prior_by_model(sub: pd.DataFrame) -> dict[str, pd.Series]:
    out: dict[str, pd.Series] = {}
    for _, r in sub.iterrows():
        model = str(r["model_name"])
        out[model] = pd.Series(
            {
                "prior_weighted_mean_rmse": r["prior_weighted_mean_rmse"],
                "fraction_of_prior_weight_where_model_wins": r["fraction_prior_weight_model_wins"],
                "fraction_of_prior_weight_where_tdf_beats_nfw": r["fraction_prior_weight_tdf_beats_nfw"],
                "fraction_of_prior_weight_where_tdf_beats_mond": r["fraction_prior_weight_tdf_beats_mond"],
            }
        )
    return out


def build_ngc7814_ktau_sensitivity(
    summary: pd.DataFrame,
    *,
    post_ml_path: Path | str = "outputs/tables/sparc_post_ml_results_summary_table.csv",
    reference_k_tau: float = 1.0,
    extreme_ktau: tuple[float, ...] = (0.25, 4.0),
) -> pd.DataFrame:
    post = pd.read_csv(post_ml_path)
    ngc_post = post[post["galaxy_id"] == TARGET_GALAXY]
    can_tdf = float(ngc_post["canonical_tdf_3knot_rmse"].iloc[0]) if not ngc_post.empty else float("nan")
    can_nfw = float(ngc_post["canonical_nfw_rmse"].iloc[0]) if not ngc_post.empty else float("nan")
    canonical_fail = (
        np.isfinite(can_tdf) and np.isfinite(can_nfw) and can_tdf > can_nfw * 2
    )

    rows: list[dict[str, Any]] = []
    for scenario_name in summary["scenario_name"].unique():
        for k_tau in sorted(summary["K_tau"].unique()):
            sub = summary[
                (summary["galaxy_id"] == TARGET_GALAXY)
                & (summary["scenario_name"] == scenario_name)
                & (summary["K_tau"] == k_tau)
            ]
            if sub.empty:
                continue
            by_model = _ktau_summary_to_prior_by_model(sub)
            layered = classify_ngc7814_layered(by_model, canonical_tdf_rmse=can_tdf, canonical_nfw_rmse=can_nfw)

            ref_sub = summary[
                (summary["galaxy_id"] == TARGET_GALAXY)
                & (summary["scenario_name"] == scenario_name)
                & (np.isclose(summary["K_tau"], reference_k_tau))
            ]
            ref_by = _ktau_summary_to_prior_by_model(ref_sub) if not ref_sub.empty else {}
            t5 = by_model.get(TDF_SENSITIVITY, pd.Series(dtype=float))
            t5_ref = ref_by.get(TDF_SENSITIVITY, pd.Series(dtype=float))
            t5_wins = float(t5.get("fraction_of_prior_weight_where_model_wins", 0)) if len(t5) else 0.0
            t5_ref_wins = float(t5_ref.get("fraction_of_prior_weight_where_model_wins", 0)) if len(t5_ref) else 0.0
            recovery = layered["interpretation_category"] == "sensitivity_tdf_5knot_diagnostic_recovery"
            ref_recovery = False
            if ref_by:
                ref_layered = classify_ngc7814_layered(
                    ref_by, canonical_tdf_rmse=can_tdf, canonical_nfw_rmse=can_nfw
                )
                ref_recovery = ref_layered["interpretation_category"] == "sensitivity_tdf_5knot_diagnostic_recovery"

            survives = recovery and (abs(k_tau - reference_k_tau) < 1e-9 or (recovery == ref_recovery and t5_wins >= t5_ref_wins * 0.85))
            is_extreme = float(k_tau) in extreme_ktau
            ref_flags = set(ref_sub["ktau_stability_flag"].unique()) if not ref_sub.empty else set()
            cur_flags = set(sub["ktau_stability_flag"].unique())
            only_extreme_change = is_extreme and (
                cur_flags != ref_flags
                or layered["interpretation_category"]
                != (
                    classify_ngc7814_layered(
                        ref_by, canonical_tdf_rmse=can_tdf, canonical_nfw_rmse=can_nfw
                    )["interpretation_category"]
                    if ref_by
                    else ""
                )
            )

            rows.append(
                {
                    "scenario_name": scenario_name,
                    "K_tau": float(k_tau),
                    "canonical_tdf_failure_at_ml_1": canonical_fail,
                    "canonical_result": layered["canonical_result"],
                    "primary_tdf_3knot_prior_result": layered["primary_tdf_3knot_prior_result"],
                    "sensitivity_tdf_5knot_prior_result": layered["sensitivity_tdf_5knot_prior_result"],
                    "tdf_5knot_diagnostic_recovery_survives_ktau": bool(survives and recovery),
                    "conclusion_changes_only_at_extreme_ktau": bool(only_extreme_change),
                    "ktau_stability_flag": ",".join(sorted(cur_flags)),
                    "recommended_claim_language": layered["recommended_claim_language"],
                    "caveat": _default_caveat(),
                }
            )
    return pd.DataFrame(rows)


def write_ktau_sensitivity_report(
    path: Path,
    *,
    summary: pd.DataFrame,
    ngc: pd.DataFrame,
    k_tau_values: list[float],
    photometry_prior_summary_path: Path | str | None = None,
) -> None:
    lines = [
        "# SPARC K_tau Sensitivity Report (Phase 4L)",
        "",
        "> K_tau is treated as a fixed normalization convention in this audit. "
        "This phase does not measure K_tau, does not perform final M/L calibration, "
        "does not validate TDF on full SPARC, does not disprove dark matter, "
        "and does not include lensing.",
        "",
        "## Objective",
        "",
        "Test whether six-galaxy TDF conclusions under **photometry-informed prior weighting** "
        "(Phase 4K) are stable when **K_tau** is varied while knot amplitudes are refit. "
        "NFW/MOND holdout RMSE values are taken from Phase 4G (fair scaled baselines).",
        "",
        "## K_tau values tested",
        "",
        ", ".join(str(k) for k in k_tau_values),
        "",
        "## Method",
        "",
        "- Same M/L grid and Phase 4K photometry-informed prior weights.",
        "- Train-only even/odd holdout; refit **tdf_3knot** and **tdf_5knot** amplitudes only.",
        "- K_tau is **not** fitted.",
        "",
        "## Five success-galaxy stability",
        "",
    ]
    success = [g for g in GALAXY_ORDER if MANDATED_GALAXY_CLASSIFICATION.get(g) == "robust_tdf_success"]
    for gid in success:
        sub = summary[(summary["galaxy_id"] == gid) & (summary["model_name"] == TDF_PRIMARY)]
        flags = sub["ktau_stability_flag"].value_counts().to_dict()
        lines.append(f"- **{gid}** (tdf_3knot): {flags}")

    lines.extend(
        [
            "",
            "## NGC7814",
            "",
            "Canonical **tdf_3knot** failure at M/L=1 is unchanged by definition (canonical holdout at fixed baryons).",
            "Prior-weighted diagnostic **tdf_5knot** support may vary with K_tau; see `ngc7814_ktau_sensitivity.csv`.",
            "",
        ]
    )
    for scenario in ngc["scenario_name"].unique():
        s = ngc[ngc["scenario_name"] == scenario]
        lines.append(f"### {scenario}")
        for _, r in s.iterrows():
            lines.append(
                f"- K_tau={r['K_tau']}: {r['recommended_claim_language']} "
                f"(5knot recovery survives: {r['tdf_5knot_diagnostic_recovery_survives_ktau']})"
            )
        lines.append("")

    if photometry_prior_summary_path:
        lines.append(f"Reference Phase 4K summary: `{photometry_prior_summary_path}`")

    lines.extend(
        [
            "",
            "## Conclusion on K_tau dependence",
            "",
            "K_tau is partially degenerate with dτ/dr amplitude; interpret metric shifts as "
            "normalization-sensitivity, not as a measured physical constant.",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_ktau_sensitivity_summary(
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
        (summary["scenario_name"] == sc) & (summary["model_name"] == TDF_PRIMARY)
    ]
    gids = [g for g in GALAXY_ORDER if g in sub["galaxy_id"].values]
    k_vals = sorted(sub["K_tau"].unique())
    fig, ax = plt.subplots(figsize=(10, 5))
    for gid in gids:
        ys = [
            float(sub[(sub["galaxy_id"] == gid) & (sub["K_tau"] == k)]["prior_weighted_mean_rmse"].iloc[0])
            for k in k_vals
        ]
        ax.plot(k_vals, ys, marker="o", label=gid)
    ax.set_xlabel("K_tau (fixed)")
    ax.set_ylabel("prior-weighted mean holdout RMSE (tdf_3knot)")
    ax.set_title(f"K_tau sensitivity — {sc}")
    ax.legend(fontsize=7, ncol=2)
    ax.set_xscale("log")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_ngc7814_ktau_from_summary(
    summary: pd.DataFrame,
    output_path: Path,
    *,
    scenario: str = "morphology_aware_conservative",
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    sub = summary[
        (summary["galaxy_id"] == TARGET_GALAXY)
        & (summary["scenario_name"] == scenario)
        & (summary["model_name"] == TDF_SENSITIVITY)
    ].sort_values("K_tau")
    if sub.empty:
        return None
    t3 = summary[
        (summary["galaxy_id"] == TARGET_GALAXY)
        & (summary["scenario_name"] == scenario)
        & (summary["model_name"] == TDF_PRIMARY)
    ].sort_values("K_tau")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(sub["K_tau"], sub["fraction_prior_weight_model_wins"], "o-", label="tdf_5knot win frac")
    ax.plot(t3["K_tau"], t3["fraction_prior_weight_model_wins"], "s--", label="tdf_3knot win frac")
    ax.set_xlabel("K_tau")
    ax.set_ylabel("prior-weight win fraction")
    ax.set_title(f"{TARGET_GALAXY} — K_tau sensitivity ({scenario})")
    ax.legend(fontsize=8)
    ax.set_xscale("log")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def run_photometry_prior_ktau_sensitivity(
    *,
    rotmod_path: Path | str = "data/processed/sparc/sparc_rotmod_standardized.csv",
    subset_path: Path | str = "outputs/tables/sparc_subset_selection.csv",
    phase4g_path: Path | str = "outputs/tables/sparc_ml_scaled_model_comparison.csv",
    weights_path: Path | str = "outputs/tables/sparc_photometry_informed_prior_weights.csv",
    recon_path: Path | str = "configs/reconstruction.yaml",
    models_path: Path | str = "configs/models.yaml",
    summary_out: Path | str = "outputs/tables/sparc_ktau_sensitivity_summary.csv",
    ngc_out: Path | str = "outputs/tables/ngc7814_ktau_sensitivity.csv",
    report_out: Path | str = "outputs/reports/sparc_ktau_sensitivity_report.md",
    include_optional_ktau: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    kt_cfg = load_ktau_sensitivity_config(recon_path)
    if include_optional_ktau:
        k_vals = sorted(
            set(kt_cfg["k_tau_values"]) | set(float(x) for x in OPTIONAL_KTAU_VALUES)
        )
    else:
        k_vals = kt_cfg["k_tau_values"]

    rotmod = pd.read_csv(rotmod_path)
    subset = pd.read_csv(subset_path)
    selected = [str(x) for x in subset["galaxy_id"].tolist()]
    phase4g = pd.read_csv(phase4g_path)
    weights = pd.read_csv(weights_path)

    tdf_grid = run_ktau_tdf_grid(
        rotmod,
        selected,
        k_vals,
        recon_path=recon_path,
        models_path=models_path,
    )

    merged_by_ktau: dict[float, pd.DataFrame] = {}
    for k in k_vals:
        tdf_k = tdf_grid[tdf_grid["K_tau"] == k]
        merged_by_ktau[k] = merge_ktau_tdf_with_phase4g_baselines(tdf_k, phase4g)

    summary = build_ktau_sensitivity_summary(
        merged_by_ktau,
        weights,
        reference_k_tau=kt_cfg["reference_k_tau"],
        stability_rtol=kt_cfg["stability_rtol"],
        win_fraction_tol=kt_cfg["win_fraction_tol"],
    )
    ngc = build_ngc7814_ktau_sensitivity(summary, reference_k_tau=kt_cfg["reference_k_tau"])

    summary.to_csv(summary_out, index=False)
    ngc.to_csv(ngc_out, index=False)
    write_ktau_sensitivity_report(
        report_out,
        summary=summary,
        ngc=ngc,
        k_tau_values=k_vals,
        photometry_prior_summary_path="outputs/tables/sparc_photometry_prior_weighted_summary.csv",
    )
    plot_ktau_sensitivity_summary(
        summary, Path("outputs/figures/sparc_subset/ktau_sensitivity_summary.png")
    )
    plot_ngc7814_ktau_from_summary(
        summary, Path("outputs/figures/sparc_subset/ngc7814_ktau_sensitivity.png")
    )
    return summary, ngc
