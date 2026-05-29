from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tdf_galaxy_tau.analysis.ml_sensitivity import (
    DEFAULT_BULGE_SCALES,
    DEFAULT_DISK_SCALES,
    TARGET_GALAXY,
    is_plausible_scale,
    load_canonical_holdout_rmse,
    reconstruct_scaled_tau_table,
    run_scaled_tdf_holdout,
    scaled_galaxy_frame,
)
from tdf_galaxy_tau.metrics.comparison import rmse
from tdf_galaxy_tau.models.fitting import (
    BaselineAuditConfig,
    _at_lower_bound,
    _at_upper_bound,
    fit_mond_a0_simple,
    fit_nfw_baseline_log,
)
from tdf_galaxy_tau.reconstruction.radial_tau import load_reconstruction_config
from tdf_galaxy_tau.validation.failure_modes import HOLDOUT_SPLIT_PRIMARY, MANDATED_GALAXY_CLASSIFICATION
from tdf_galaxy_tau.validation.holdout import even_odd_radial_split, mask_from_indices, radial_region_label_for_index
from tdf_galaxy_tau.validation.holdout_residuals import load_holdout_export_configs

ANALYSIS_STAGE = "phase_4g_ml_scaled_fair_baseline_comparison"
COMPARISON_MODE = "train_only_scaled_holdout"
MODELS = ("tdf_3knot", "tdf_5knot", "nfw_refit_scaled", "mond_fit_a0_scaled")
CANONICAL_MODEL_MAP = {
    "tdf_3knot": "tdf_3knot",
    "tdf_5knot": "tdf_5knot",
    "nfw_refit_scaled": "nfw_refit",
    "mond_fit_a0_scaled": "mond_fit_a0_simple",
}


@dataclass(frozen=True)
class MlScaledBaselineConfig:
    disk_scales: tuple[float, ...] = DEFAULT_DISK_SCALES
    bulge_scales: tuple[float, ...] = DEFAULT_BULGE_SCALES
    holdout_split: str = HOLDOUT_SPLIT_PRIMARY
    models: tuple[str, ...] = MODELS


def _regional_rmse_from_test_rows(rows: list[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        return {
            "total_holdout_rmse_kms": float("nan"),
            "inner_holdout_rmse_kms": float("nan"),
            "middle_holdout_rmse_kms": float("nan"),
            "outer_holdout_rmse_kms": float("nan"),
        }
    df = pd.DataFrame(rows)
    out: dict[str, float] = {
        "total_holdout_rmse_kms": float(rmse(df["v_obs_kms"], df["v_pred_kms"])),
    }
    for region in ("inner", "middle", "outer"):
        sub = df[df["radial_region_label"] == region]
        out[f"{region}_holdout_rmse_kms"] = (
            float(rmse(sub["v_obs_kms"], sub["v_pred_kms"])) if len(sub) else float("nan")
        )
    return out


def _nfw_boundary_limited(fit, log_rho_bounds: tuple[float, float], log_rs_bounds: tuple[float, float]) -> bool:
    if not fit.fit_success or not fit.log_params:
        return False
    tol = BaselineAuditConfig().boundary_tolerance_fraction
    log_rho = float(fit.log_params["log10_rho_s"])
    log_rs = float(fit.log_params["log10_r_s"])
    flags = [
        _at_lower_bound(log_rho, log_rho_bounds, tol),
        _at_upper_bound(log_rho, log_rho_bounds, tol),
        _at_lower_bound(log_rs, log_rs_bounds, tol),
        _at_upper_bound(log_rs, log_rs_bounds, tol),
    ]
    return any(flags)


def _mond_boundary_limited(fit, log_bounds: tuple[float, float]) -> bool:
    if not fit.fit_success or not fit.log_params:
        return False
    tol = BaselineAuditConfig().boundary_tolerance_fraction
    log_a0 = float(fit.log_params["log10_a0_m_s2"])
    return _at_lower_bound(log_a0, log_bounds, tol) or _at_upper_bound(log_a0, log_bounds, tol)


def run_scaled_nfw_holdout(
    g_scaled: pd.DataFrame,
    *,
    models_yaml: dict,
    n_points: int,
) -> dict[str, Any]:
    from tdf_galaxy_tau.models.nfw import nfw_params_from_log10, nfw_velocity

    r = g_scaled["r_kpc"].to_numpy(dtype=float)
    v_obs = g_scaled["v_obs_kms"].to_numpy(dtype=float)
    v_err = g_scaled["v_err_kms"].to_numpy(dtype=float)
    v_bar = g_scaled["v_bar_kms"].to_numpy(dtype=float)
    split = even_odd_radial_split(n_points)
    train_mask = mask_from_indices(n_points, split.train_indices)
    test_mask = mask_from_indices(n_points, split.test_indices)
    robust = models_yaml.get("robust_fit", {})
    nfw_b = robust.get("nfw", {})
    log_rho_bounds = tuple(nfw_b["log10_rho_s_bounds_msun_kpc3"])
    log_rs_bounds = tuple(nfw_b["log10_r_s_bounds_kpc"])

    fit = fit_nfw_baseline_log(
        r[train_mask],
        v_obs[train_mask],
        v_err[train_mask],
        v_bar[train_mask],
        log10_rho_s_bounds=log_rho_bounds,
        log10_r_s_bounds=log_rs_bounds,
    )
    rows: list[dict[str, Any]] = []
    if fit.fit_success and fit.log_params:
        p = nfw_params_from_log10(fit.log_params["log10_rho_s"], fit.log_params["log10_r_s"])
        v_halo = nfw_velocity(r[test_mask], p)
        v_pred = np.sqrt(np.maximum(v_bar[test_mask] ** 2 + v_halo**2, 0.0))
    else:
        v_pred = v_bar[test_mask]

    for j, i in enumerate(np.asarray(split.test_indices, dtype=int)):
        rows.append(
            {
                "v_obs_kms": float(v_obs[i]),
                "v_pred_kms": float(v_pred[j]),
                "radial_region_label": radial_region_label_for_index(n_points, int(i)),
            }
        )

    metrics = _regional_rmse_from_test_rows(rows)
    return {
        **metrics,
        "n_test_points": int(test_mask.sum()),
        "fit_success": bool(fit.fit_success),
        "fit_status": str(fit.fit_status),
        "negative_v2_count": 0,
        "boundary_limited_flag": _nfw_boundary_limited(fit, log_rho_bounds, log_rs_bounds),
    }


def run_scaled_mond_holdout(
    g_scaled: pd.DataFrame,
    *,
    models_yaml: dict,
    n_points: int,
) -> dict[str, Any]:
    from tdf_galaxy_tau.models.mond import mond_fit_a0_velocity_kms

    r = g_scaled["r_kpc"].to_numpy(dtype=float)
    v_obs = g_scaled["v_obs_kms"].to_numpy(dtype=float)
    v_err = g_scaled["v_err_kms"].to_numpy(dtype=float)
    v_bar = g_scaled["v_bar_kms"].to_numpy(dtype=float)
    split = even_odd_radial_split(n_points)
    train_mask = mask_from_indices(n_points, split.train_indices)
    test_mask = mask_from_indices(n_points, split.test_indices)
    mond_cfg = models_yaml.get("mond", {})
    log_bounds = tuple(mond_cfg.get("log10_a0_bounds_m_s2", [-11.5, -9.5]))
    log_init = float(mond_cfg.get("log10_a0_initial", -10.0))

    fit = fit_mond_a0_simple(
        r[train_mask],
        v_obs[train_mask],
        v_err[train_mask],
        v_bar[train_mask],
        log10_a0_bounds=log_bounds,
        log10_a0_initial=log_init,
    )
    rows: list[dict[str, Any]] = []
    if fit.fit_success and fit.log_params:
        log_a0 = fit.log_params["log10_a0_m_s2"]
        v_pred = mond_fit_a0_velocity_kms(r[test_mask], v_bar[test_mask], log_a0)
    else:
        v_pred = v_bar[test_mask]

    for j, i in enumerate(np.asarray(split.test_indices, dtype=int)):
        rows.append(
            {
                "v_obs_kms": float(v_obs[i]),
                "v_pred_kms": float(v_pred[j]),
                "radial_region_label": radial_region_label_for_index(n_points, int(i)),
            }
        )

    metrics = _regional_rmse_from_test_rows(rows)
    return {
        **metrics,
        "n_test_points": int(test_mask.sum()),
        "fit_success": bool(fit.fit_success),
        "fit_status": str(fit.fit_status),
        "negative_v2_count": 0,
        "boundary_limited_flag": _mond_boundary_limited(fit, log_bounds),
    }


def _run_model_holdout(
    model_name: str,
    g_scaled: pd.DataFrame,
    tau_df: pd.DataFrame,
    galaxy_id: str,
    *,
    recon_yaml: dict,
    models_yaml: dict,
    n_points: int,
) -> dict[str, Any]:
    if model_name == "tdf_3knot" or model_name == "tdf_5knot":
        return run_scaled_tdf_holdout(
            g_scaled,
            tau_df,
            galaxy_id,
            model_name,
            recon_yaml=recon_yaml,
            models_yaml=models_yaml,
            n_points=n_points,
        )
    if model_name == "nfw_refit_scaled":
        return run_scaled_nfw_holdout(g_scaled, models_yaml=models_yaml, n_points=n_points)
    if model_name == "mond_fit_a0_scaled":
        return run_scaled_mond_holdout(g_scaled, models_yaml=models_yaml, n_points=n_points)
    raise ValueError(f"unknown model: {model_name}")


def run_ml_scaled_baseline_comparison(
    rotmod: pd.DataFrame,
    selected_ids: list[str],
    *,
    recon_path: Path | str = "configs/reconstruction.yaml",
    models_path: Path | str = "configs/models.yaml",
    holdout_validation_path: Path | str = "outputs/tables/sparc_tdf_holdout_validation.csv",
    ml_config: MlScaledBaselineConfig | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cfg = ml_config or MlScaledBaselineConfig()
    recon_yaml, models_yaml = load_holdout_export_configs(recon_path, models_path)
    tau_config = load_reconstruction_config(recon_path)
    canonical = load_canonical_holdout_rmse(holdout_validation_path)

    rows: list[dict[str, Any]] = []
    for gid in selected_ids:
        g = rotmod[rotmod["galaxy_id"] == gid].copy()
        if g.empty:
            continue
        n_points = len(g)
        for disk_scale in cfg.disk_scales:
            for bulge_scale in cfg.bulge_scales:
                g_scaled = scaled_galaxy_frame(g, disk_scale=disk_scale, bulge_scale=bulge_scale)
                tau_df = reconstruct_scaled_tau_table(g_scaled, gid, tau_config)
                plausible = is_plausible_scale(disk_scale, bulge_scale)
                for model_name in cfg.models:
                    metrics = _run_model_holdout(
                        model_name,
                        g_scaled,
                        tau_df,
                        gid,
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
                            "split_name": cfg.holdout_split,
                            "total_holdout_rmse_kms": metrics["total_holdout_rmse_kms"],
                            "inner_holdout_rmse_kms": metrics["inner_holdout_rmse_kms"],
                            "middle_holdout_rmse_kms": metrics["middle_holdout_rmse_kms"],
                            "outer_holdout_rmse_kms": metrics["outer_holdout_rmse_kms"],
                            "n_test_points": metrics.get("n_test_points", int(n_points // 2)),
                            "fit_success": metrics["fit_success"],
                            "fit_status": metrics["fit_status"],
                            "negative_v2_count": metrics.get("negative_v2_count", 0),
                            "boundary_limited_flag": metrics.get("boundary_limited_flag", False),
                            "comparison_mode": COMPARISON_MODE,
                            "analysis_stage": ANALYSIS_STAGE,
                        }
                    )

    comparison = pd.DataFrame(rows)
    ngc_fair = build_ngc7814_fair_comparison(comparison)
    best_summary = build_best_model_summary(comparison, canonical)
    return comparison, ngc_fair, best_summary


def build_ngc7814_fair_comparison(comparison: pd.DataFrame) -> pd.DataFrame:
    sub = comparison[comparison["galaxy_id"] == TARGET_GALAXY].copy()
    if sub.empty:
        return pd.DataFrame()

    out_rows: list[dict[str, Any]] = []
    for (d_scale, b_scale), grp in sub.groupby(["disk_scale", "bulge_scale"], sort=False):
        rmse_by_model = {
            str(m): float(grp.loc[grp["model_name"] == m, "total_holdout_rmse_kms"].iloc[0])
            for m in MODELS
            if (grp["model_name"] == m).any()
        }
        t3 = rmse_by_model.get("tdf_3knot", float("nan"))
        t5 = rmse_by_model.get("tdf_5knot", float("nan"))
        nfw = rmse_by_model.get("nfw_refit_scaled", float("nan"))
        mond = rmse_by_model.get("mond_fit_a0_scaled", float("nan"))
        best_model = min(rmse_by_model, key=lambda k: rmse_by_model[k]) if rmse_by_model else ""
        plausible = is_plausible_scale(float(d_scale), float(b_scale))
        out_rows.append(
            {
                "disk_scale": float(d_scale),
                "bulge_scale": float(b_scale),
                "plausible_scale_flag": plausible,
                "tdf_3knot_rmse": t3,
                "tdf_5knot_rmse": t5,
                "nfw_scaled_rmse": nfw,
                "mond_scaled_rmse": mond,
                "best_model": best_model,
                "tdf_beats_nfw": bool(np.isfinite(t3) and np.isfinite(nfw) and t3 < nfw),
                "tdf_beats_mond": bool(np.isfinite(t3) and np.isfinite(mond) and t3 < mond),
                "interpretation": _ngc7814_fair_cell_interpretation(t3, nfw, mond, plausible, best_model),
            }
        )
    return pd.DataFrame(out_rows)


def _ngc7814_fair_cell_interpretation(
    t3: float,
    nfw: float,
    mond: float,
    plausible: bool,
    best_model: str,
) -> str:
    parts = []
    if plausible:
        parts.append("Plausible diagnostic M/L band.")
    else:
        parts.append("Outside plausible diagnostic band.")
    if best_model == "tdf_3knot":
        parts.append("TDF 3-knot wins at this scale (fair scaled comparison).")
    elif best_model in ("nfw_refit_scaled", "mond_fit_a0_scaled"):
        parts.append(f"{best_model} wins at this scale.")
    if np.isfinite(t3) and np.isfinite(nfw) and t3 < nfw:
        parts.append("TDF beats scaled NFW.")
    elif np.isfinite(nfw) and np.isfinite(t3):
        parts.append("Scaled NFW competitive or better than TDF.")
    return " ".join(parts)


def _canonical_best_model(canonical: pd.DataFrame, gid: str) -> str:
    candidates = {
        "tdf_3knot": float(canonical.loc[gid, "tdf_3knot"]) if "tdf_3knot" in canonical.columns else float("nan"),
        "tdf_5knot": float(canonical.loc[gid, "tdf_5knot"]) if "tdf_5knot" in canonical.columns else float("nan"),
        "nfw_refit": float(canonical.loc[gid, "nfw_refit"]) if "nfw_refit" in canonical.columns else float("nan"),
        "mond_fit_a0_simple": float(canonical.loc[gid, "mond_fit_a0_simple"])
        if "mond_fit_a0_simple" in canonical.columns
        else float("nan"),
    }
    finite = {k: v for k, v in candidates.items() if np.isfinite(v)}
    return min(finite, key=finite.get) if finite else "unknown"


def _best_in_plausible_band(sub: pd.DataFrame) -> tuple[str, float, float, float]:
    pl = sub[sub["plausible_scale_flag"] == True]  # noqa: E712
    if pl.empty:
        return "unknown", float("nan"), float("nan"), float("nan")
    idx = pl["total_holdout_rmse_kms"].idxmin()
    row = pl.loc[idx]
    return (
        str(row["model_name"]),
        float(row["total_holdout_rmse_kms"]),
        float(row["disk_scale"]),
        float(row["bulge_scale"]),
    )


def build_best_model_summary(comparison: pd.DataFrame, canonical: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for gid in comparison["galaxy_id"].unique():
        sub = comparison[comparison["galaxy_id"] == gid]
        classification = MANDATED_GALAXY_CLASSIFICATION.get(gid, "unknown")
        can_best = _canonical_best_model(canonical, gid) if gid in canonical.index else "unknown"
        pl_model, pl_rmse, pl_disk, pl_bulge = _best_in_plausible_band(sub)

        tdf_pl = sub[
            (sub["model_name"] == "tdf_3knot")
            & (sub["plausible_scale_flag"] == True)  # noqa: E712
        ]
        tdf_stable = False
        if classification == "robust_tdf_success" and not tdf_pl.empty:
            can_tdf = float(canonical.loc[gid, "tdf_3knot"]) if gid in canonical.index else float("nan")
            best_tdf_pl = float(tdf_pl["total_holdout_rmse_kms"].min())
            nfw_can = float(canonical.loc[gid, "nfw_refit"]) if gid in canonical.index else float("nan")
            mond_can = float(canonical.loc[gid, "mond_fit_a0_simple"]) if gid in canonical.index else float("nan")
            tdf_stable = bool(
                np.isfinite(best_tdf_pl)
                and np.isfinite(can_tdf)
                and best_tdf_pl <= can_tdf * 1.15
                and (not np.isfinite(nfw_can) or best_tdf_pl < nfw_can * 1.1)
            )

        baseline_wins = False
        for (_, _), grp in sub[sub["plausible_scale_flag"] == True].groupby(  # noqa: E712
            ["disk_scale", "bulge_scale"]
        ):
            rmse_map = {
                m: float(grp.loc[grp["model_name"] == m, "total_holdout_rmse_kms"].iloc[0])
                for m in MODELS
                if (grp["model_name"] == m).any()
            }
            if not rmse_map:
                continue
            winner = min(rmse_map, key=rmse_map.get)
            if winner in ("nfw_refit_scaled", "mond_fit_a0_scaled"):
                baseline_wins = True
                break

        rows.append(
            {
                "galaxy_id": gid,
                "canonical_classification": classification,
                "best_model_canonical": can_best,
                "best_model_best_plausible_scale": pl_model,
                "best_plausible_disk_scale": pl_disk,
                "best_plausible_bulge_scale": pl_bulge,
                "best_plausible_rmse_kms": pl_rmse,
                "tdf_success_stable_under_plausible_scaling": tdf_stable,
                "nfw_or_mond_wins_any_plausible_scale": baseline_wins,
                "caveat": (
                    "Fair comparison: all models use same scaled baryons and even/odd holdout. "
                    "Diagnostic M/L grid only; not final calibration."
                ),
            }
        )
    return pd.DataFrame(rows)


def plot_ngc7814_fair_comparison(ngc_fair: pd.DataFrame, output_path: Path) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
    metrics = [
        ("tdf_3knot_rmse", "TDF 3-knot"),
        ("nfw_scaled_rmse", "NFW (scaled)"),
        ("mond_scaled_rmse", "MOND (scaled)"),
    ]
    for ax, (col, title) in zip(axes, metrics):
        pivot = ngc_fair.pivot_table(index="bulge_scale", columns="disk_scale", values=col, aggfunc="first")
        im = ax.imshow(pivot.values, aspect="auto", cmap="viridis_r")
        ax.set_title(title)
        ax.set_xlabel("disk_scale")
        ax.set_ylabel("bulge_scale")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_yticks(range(len(pivot.index)))
        ax.set_xticklabels([f"{c:.1f}" for c in pivot.columns], fontsize=7)
        ax.set_yticklabels([f"{i:.1f}" for i in pivot.index], fontsize=7)
        fig.colorbar(im, ax=ax, label="RMSE [km/s]")
    fig.suptitle(f"{TARGET_GALAXY} — fair M/L-scaled holdout RMSE (diagnostic)")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_model_winners_heatmap(comparison: pd.DataFrame, output_path: Path) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    sub = comparison[comparison["galaxy_id"] == TARGET_GALAXY]
    winners: list[list[str]] = []
    disk_scales = sorted(sub["disk_scale"].unique())
    bulge_scales = sorted(sub["bulge_scale"].unique())
    for b in bulge_scales:
        row: list[str] = []
        for d in disk_scales:
            grp = sub[(sub["disk_scale"] == d) & (sub["bulge_scale"] == b)]
            rmse_map = {
                str(m): float(grp.loc[grp["model_name"] == m, "total_holdout_rmse_kms"].iloc[0])
                for m in MODELS
                if (grp["model_name"] == m).any()
            }
            row.append(min(rmse_map, key=rmse_map.get) if rmse_map else "")
        winners.append(row)

    label_map = {
        "tdf_3knot": 0,
        "tdf_5knot": 1,
        "nfw_refit_scaled": 2,
        "mond_fit_a0_scaled": 3,
    }
    z = np.array([[label_map.get(w, -1) for w in row] for row in winners])
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(z, aspect="auto", cmap="tab10", vmin=0, vmax=3)
    ax.set_xticks(range(len(disk_scales)))
    ax.set_yticks(range(len(bulge_scales)))
    ax.set_xticklabels([f"{d:.1f}" for d in disk_scales])
    ax.set_yticklabels([f"{b:.1f}" for b in bulge_scales])
    ax.set_xlabel("disk_scale")
    ax.set_ylabel("bulge_scale")
    ax.set_title(f"{TARGET_GALAXY} — best model per M/L cell (fair scaled)")
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2, 3])
    cbar.ax.set_yticklabels(["tdf_3knot", "tdf_5knot", "nfw_scaled", "mond_scaled"])
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_success_stability(best_summary: pd.DataFrame, output_path: Path) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(best_summary))
    colors = ["C3" if g == TARGET_GALAXY else "C0" for g in best_summary["galaxy_id"]]
    stable = best_summary["tdf_success_stable_under_plausible_scaling"].astype(int)
    baseline_wins = best_summary["nfw_or_mond_wins_any_plausible_scale"].astype(int)
    ax.bar(x - 0.2, stable, 0.4, label="TDF stable (plausible band)", color=colors, alpha=0.7)
    ax.bar(x + 0.2, baseline_wins, 0.4, label="NFW/MOND wins any plausible cell", color="gray", alpha=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(best_summary["galaxy_id"], rotation=30, ha="right")
    ax.set_ylabel("flag (0/1)")
    ax.set_title("M/L-scaled fair comparison: success stability vs NGC7814")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def write_ml_scaled_baseline_report(
    path: Path,
    *,
    comparison: pd.DataFrame,
    ngc_fair: pd.DataFrame,
    best_summary: pd.DataFrame,
    ml_config: MlScaledBaselineConfig,
) -> None:
    ngc_sum = best_summary[best_summary["galaxy_id"] == TARGET_GALAXY].iloc[0]
    pl_ngc = ngc_fair[ngc_fair["plausible_scale_flag"] == True]  # noqa: E712
    tdf_wins_pl = int(pl_ngc["tdf_beats_nfw"].sum()) if not pl_ngc.empty else 0
    n_cells_pl = len(pl_ngc)

    can_row = ngc_fair[
        (ngc_fair["disk_scale"] == 1.0) & (ngc_fair["bulge_scale"] == 1.0)
    ]
    can = can_row.iloc[0] if not can_row.empty else None

    best_pl_tdf = pl_ngc.loc[pl_ngc["tdf_3knot_rmse"].idxmin()] if not pl_ngc.empty else None

    lines = [
        "# SPARC Fair M/L-Scaled Baseline Comparison Report (Phase 4G)",
        "",
        "> This phase is a fair M/L-scaled diagnostic comparison. It does not recalibrate SPARC baryons, "
        "does not introduce a final fitted M/L model, does not validate TDF on full SPARC, "
        "does not disprove dark matter, and does not include lensing.",
        "",
        "## Objective",
        "",
        "Re-evaluate **TDF**, **NFW**, and **MOND** under the same diagnostic disk/bulge M/L scaling grid "
        "used in Phase 4F, with train-only even/odd holdout refits at each scale.",
        "",
        "## Why this phase was needed after Phase 4F",
        "",
        "Phase 4F showed strong NGC7814 TDF sensitivity to bulge scaling but compared TDF only against "
        "**canonical** (unscaled) NFW/MOND holdout RMSE. Phase 4G refits NFW and MOND on the **same scaled** "
        "baryons for a fair comparison.",
        "",
        "## Scaling method",
        "",
        "`v_bar² = v_gas² + s_disk·v_disk² + s_bulge·v_bulge²` (signed components; gas unscaled). "
        "τ reconstruction uses `tau(r_min)=0`.",
        "",
        "## Fair model comparison method",
        "",
        f"- Models: {list(ml_config.models)}",
        f"- Split: `{ml_config.holdout_split}`",
        f"- Comparison mode: `{COMPARISON_MODE}`",
        "- NFW: log-space multistart refit (Phase 3A-R) on train points only.",
        "- MOND: log10(a0) refit on train only.",
        "- TDF: same train-only knot refit as Phase 4F; K_tau fixed.",
        "",
        "## Scale grid",
        "",
        f"- disk_scale: {list(ml_config.disk_scales)}",
        f"- bulge_scale: {list(ml_config.bulge_scales)}",
        "",
        "## NGC7814 results",
        "",
    ]
    if can is not None:
        lines.extend(
            [
                f"- Canonical scales (1,1): tdf_3knot={can['tdf_3knot_rmse']:.1f}, "
                f"nfw_scaled={can['nfw_scaled_rmse']:.1f}, mond_scaled={can['mond_scaled_rmse']:.1f} km/s",
                f"- Best model at (1,1): **{can['best_model']}**",
                "",
            ]
        )
    if best_pl_tdf is not None:
        lines.extend(
            [
                f"- Best plausible-band tdf_3knot: disk={best_pl_tdf['disk_scale']}, bulge={best_pl_tdf['bulge_scale']}, "
                f"RMSE={best_pl_tdf['tdf_3knot_rmse']:.1f} km/s (nfw={best_pl_tdf['nfw_scaled_rmse']:.1f}, "
                f"mond={best_pl_tdf['mond_scaled_rmse']:.1f})",
                f"- TDF beats scaled NFW in **{tdf_wins_pl}/{n_cells_pl}** plausible-band cells",
                "",
            ]
        )

    lines.extend(
        [
            "### Interpretation (NGC7814)",
            "",
            _ngc7814_fair_report_conclusion(ngc_fair, ngc_sum, can, best_pl_tdf, tdf_wins_pl, n_cells_pl),
            "",
            "## Success-galaxy stability",
            "",
            f"- Galaxies with `tdf_success_stable_under_plausible_scaling`: "
            f"{int(best_summary['tdf_success_stable_under_plausible_scaling'].sum())} / {len(best_summary)}",
            f"- Galaxies where NFW/MOND wins at some plausible scale: "
            f"{int(best_summary['nfw_or_mond_wins_any_plausible_scale'].sum())} / {len(best_summary)}",
            "",
            "## Limitations",
            "",
            "- Diagnostic M/L grid; not photometric calibration.",
            "- Distance, inclination, and K_tau fixed.",
            "- even/odd split only in aggregated tables.",
            "- Canonical Phase 4A failure label at M/L=1 unchanged.",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _ngc7814_fair_report_conclusion(
    ngc_fair: pd.DataFrame,
    ngc_sum: pd.Series,
    can: pd.Series | None,
    best_pl_tdf: pd.Series | None,
    tdf_wins_pl: int,
    n_cells_pl: int,
) -> str:
    parts: list[str] = []
    if can is not None:
        if can["best_model"] != "tdf_3knot" and float(can["tdf_3knot_rmse"]) > float(can["nfw_scaled_rmse"]):
            parts.append(
                "At **canonical** M/L=1, scaled NFW/MOND remain far better than TDF on holdout RMSE; "
                "the canonical failure label is unchanged."
            )
        else:
            parts.append("At canonical scales, model ranking should be checked against Phase 3C.")

    if best_pl_tdf is not None:
        t3 = float(best_pl_tdf["tdf_3knot_rmse"])
        nfw = float(best_pl_tdf["nfw_scaled_rmse"])
        mond = float(best_pl_tdf["mond_scaled_rmse"])
        if t3 < nfw and t3 < mond:
            parts.append(
                "Under the **best plausible-scale** cell for TDF, TDF can beat **both** scaled NFW and MOND "
                "when all models use the same scaled baryons."
            )
        elif t3 < nfw:
            parts.append("TDF can beat scaled NFW but not scaled MOND at its best plausible cell.")
        else:
            parts.append(
                "After fair scaled refit, **NFW or MOND often remain competitive or better** than TDF "
                "at many plausible-band scales."
            )

    if n_cells_pl > 0:
        frac = tdf_wins_pl / n_cells_pl
        parts.append(
            f"TDF beats scaled NFW in {tdf_wins_pl}/{n_cells_pl} ({frac:.0%}) plausible-band cells; "
            "lowering bulge_scale typically helps **all** models, not only TDF."
        )

    parts.append(
        "The failure is **primarily sensitive to fixed bulge-dominated baryons** at canonical decomposition; "
        "fair comparison shows TDF improvement can be **shared** with baselines when baryons are rescaled."
    )
    if bool(ngc_sum.get("nfw_or_mond_wins_any_plausible_scale", False)):
        parts.append("NFW or MOND wins at least one plausible-scale cell for NGC7814.")

    parts.append(
        "Extreme disk_scale=0.5 is outside the plausible band; conclusions about competition should emphasize "
        "the plausible band unless noted."
    )
    return " ".join(parts)
