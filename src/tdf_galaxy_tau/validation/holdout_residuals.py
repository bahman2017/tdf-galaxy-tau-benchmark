from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.models.fitting import fit_mond_a0_simple, fit_nfw_baseline_log, fit_tdf_knot_baseline
from tdf_galaxy_tau.models.tdf_knot import (
    amplitude_bounds_from_reconstruction,
    fitted_knot_amplitudes_from_params,
    fixed_knot_radii_kpc,
    galaxy_tau_reconstruction_train_only,
    initial_knot_amplitudes_from_reconstruction,
    interpolate_dtaudr_at_radii,
    load_tdf_knot_config,
    n_knots_for_model,
    tdf_velocity_kms,
)
from tdf_galaxy_tau.validation.holdout import (
    all_holdout_splits,
    fold_id_from_split_name,
    mask_from_indices,
    radial_region_label_for_index,
)
from tdf_galaxy_tau.validation.tdf_holdout_runner import load_yaml

VALIDATION_STAGE = "phase_4e_holdout_point_residuals"
COMPARISON_MODE = "train_only_holdout"
DEFAULT_TDF_MODELS = ("tdf_3knot", "tdf_5knot")
DEFAULT_BASELINE_MODELS = ("nfw_refit", "mond_fit_a0_simple")

HOLDOUT_POINT_COLUMNS = [
    "galaxy_id",
    "split_name",
    "fold_id",
    "model_name",
    "r_kpc",
    "radial_region_label",
    "v_obs_kms",
    "v_err_kms",
    "v_bar_kms",
    "v_pred_kms",
    "residual_kms",
    "abs_residual_kms",
    "normalized_residual",
    "residual_v2_kms2",
    "dtaudr_reconstructed",
    "negative_v2_flag",
    "train_or_test",
    "comparison_mode",
    "fit_status",
    "fit_success",
    "data_mode",
    "validation_stage",
]


def _point_row(
    *,
    galaxy_id: str,
    split_name: str,
    model_name: str,
    n_points: int,
    idx: int,
    r_kpc: float,
    v_obs: float,
    v_err: float,
    v_bar: float,
    v_pred: float,
    residual_v2: float,
    dtaudr: float,
    negative_v2: bool,
    fit_status: str,
    fit_success: bool,
    data_mode: str,
) -> dict[str, Any]:
    residual = float(v_obs - v_pred)
    err = float(v_err) if v_err > 0 else float("nan")
    return {
        "galaxy_id": galaxy_id,
        "split_name": split_name,
        "fold_id": fold_id_from_split_name(split_name),
        "model_name": model_name,
        "r_kpc": float(r_kpc),
        "radial_region_label": radial_region_label_for_index(n_points, idx),
        "v_obs_kms": float(v_obs),
        "v_err_kms": float(v_err),
        "v_bar_kms": float(v_bar),
        "v_pred_kms": float(v_pred),
        "residual_kms": residual,
        "abs_residual_kms": abs(residual),
        "normalized_residual": residual / err if err > 0 else float("nan"),
        "residual_v2_kms2": float(residual_v2),
        "dtaudr_reconstructed": float(dtaudr) if np.isfinite(dtaudr) else float("nan"),
        "negative_v2_flag": bool(negative_v2),
        "train_or_test": "test",
        "comparison_mode": COMPARISON_MODE,
        "fit_status": fit_status,
        "fit_success": bool(fit_success),
        "data_mode": data_mode,
        "validation_stage": VALIDATION_STAGE,
    }


def _export_tdf_test_points(
    gid: str,
    r: np.ndarray,
    v_obs: np.ndarray,
    v_err: np.ndarray,
    v_bar: np.ndarray,
    tau_df: pd.DataFrame,
    model_name: str,
    split_name: str,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    *,
    k_g: float,
    safety_factor: float,
    negative_v2_penalty: float,
    data_mode: str,
    n_points: int,
) -> list[dict[str, Any]]:
    train_mask = mask_from_indices(n_points, train_idx)
    r_train = r[train_mask]
    r_recon, d_recon = galaxy_tau_reconstruction_train_only(tau_df, gid, train_mask)
    n_knots = n_knots_for_model(model_name)
    knot_r = fixed_knot_radii_kpc(r_train, n_knots)
    bounds = amplitude_bounds_from_reconstruction(d_recon, safety_factor=safety_factor)
    x0 = initial_knot_amplitudes_from_reconstruction(knot_r, r_recon, d_recon)

    fit = fit_tdf_knot_baseline(
        r,
        v_obs,
        v_err,
        v_bar,
        model_name=model_name,
        knot_r_kpc=knot_r,
        initial_knot_dtaudr=x0,
        dtaudr_bounds=bounds,
        k_g=k_g,
        negative_v2_penalty=negative_v2_penalty,
        train_mask=train_mask,
    )
    rows: list[dict[str, Any]] = []
    if fit.fit_success and fit.params:
        theta = fitted_knot_amplitudes_from_params(fit.params, n_knots)
        v_model, v2 = tdf_velocity_kms(r, v_bar, knot_r, theta, k_g=k_g)
        dtaudr_all = interpolate_dtaudr_at_radii(r, knot_r, theta)
    else:
        v_model = v_bar.copy()
        v2 = v_bar**2
        dtaudr_all = np.full_like(r, np.nan)

    for i in np.asarray(test_idx, dtype=int):
        rows.append(
            _point_row(
                galaxy_id=gid,
                split_name=split_name,
                model_name=model_name,
                n_points=n_points,
                idx=int(i),
                r_kpc=float(r[i]),
                v_obs=float(v_obs[i]),
                v_err=float(v_err[i]),
                v_bar=float(v_bar[i]),
                v_pred=float(v_model[i]),
                residual_v2=float(v2[i]),
                dtaudr=float(dtaudr_all[i]),
                negative_v2=bool(v2[i] < 0),
                fit_status=fit.fit_status,
                fit_success=fit.fit_success,
                data_mode=data_mode,
            )
        )
    return rows


def _export_nfw_test_points(
    gid: str,
    r: np.ndarray,
    v_obs: np.ndarray,
    v_err: np.ndarray,
    v_bar: np.ndarray,
    split_name: str,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    models_yaml: dict,
    data_mode: str,
    n_points: int,
) -> list[dict[str, Any]]:
    from tdf_galaxy_tau.models.nfw import nfw_params_from_log10, nfw_velocity

    train_mask = mask_from_indices(n_points, train_idx)
    test_mask = mask_from_indices(n_points, test_idx)
    robust = models_yaml.get("robust_fit", {})
    nfw_b = robust.get("nfw", {})
    fit = fit_nfw_baseline_log(
        r[train_mask],
        v_obs[train_mask],
        v_err[train_mask],
        v_bar[train_mask],
        log10_rho_s_bounds=tuple(nfw_b["log10_rho_s_bounds_msun_kpc3"]),
        log10_r_s_bounds=tuple(nfw_b["log10_r_s_bounds_kpc"]),
    )
    rows: list[dict[str, Any]] = []
    if fit.fit_success and fit.log_params:
        log_rho = fit.log_params["log10_rho_s"]
        log_rs = fit.log_params["log10_r_s"]
        p = nfw_params_from_log10(log_rho, log_rs)
        v_halo = nfw_velocity(r[test_mask], p)
        v_pred = np.sqrt(np.maximum(v_bar[test_mask] ** 2 + v_halo**2, 0.0))
        v2 = v_pred**2
    else:
        v_pred = v_bar[test_mask]
        v2 = v_pred**2

    for j, i in enumerate(np.asarray(test_idx, dtype=int)):
        rows.append(
            _point_row(
                galaxy_id=gid,
                split_name=split_name,
                model_name="nfw_refit",
                n_points=n_points,
                idx=int(i),
                r_kpc=float(r[i]),
                v_obs=float(v_obs[i]),
                v_err=float(v_err[i]),
                v_bar=float(v_bar[i]),
                v_pred=float(v_pred[j]),
                residual_v2=float(v2[j]),
                dtaudr=float("nan"),
                negative_v2=False,
                fit_status=fit.fit_status,
                fit_success=fit.fit_success,
                data_mode=data_mode,
            )
        )
    return rows


def _export_mond_test_points(
    gid: str,
    r: np.ndarray,
    v_obs: np.ndarray,
    v_err: np.ndarray,
    v_bar: np.ndarray,
    split_name: str,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    models_yaml: dict,
    data_mode: str,
    n_points: int,
) -> list[dict[str, Any]]:
    from tdf_galaxy_tau.models.mond import mond_fit_a0_velocity_kms

    train_mask = mask_from_indices(n_points, train_idx)
    test_mask = mask_from_indices(n_points, test_idx)
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
    v2 = v_pred**2

    for j, i in enumerate(np.asarray(test_idx, dtype=int)):
        rows.append(
            _point_row(
                galaxy_id=gid,
                split_name=split_name,
                model_name="mond_fit_a0_simple",
                n_points=n_points,
                idx=int(i),
                r_kpc=float(r[i]),
                v_obs=float(v_obs[i]),
                v_err=float(v_err[i]),
                v_bar=float(v_bar[i]),
                v_pred=float(v_pred[j]),
                residual_v2=float(v2[j]),
                dtaudr=float("nan"),
                negative_v2=False,
                fit_status=fit.fit_status,
                fit_success=fit.fit_success,
                data_mode=data_mode,
            )
        )
    return rows


def export_holdout_point_residuals(
    data: pd.DataFrame,
    tau_df: pd.DataFrame,
    selected_ids: list[str],
    recon_yaml: dict,
    models_yaml: dict,
    *,
    tdf_models: tuple[str, ...] = DEFAULT_TDF_MODELS,
    baseline_models: tuple[str, ...] = DEFAULT_BASELINE_MODELS,
) -> pd.DataFrame:
    """Per-point holdout test predictions; all models refit on training radii only."""
    tdf_cfg = load_tdf_knot_config(recon_yaml)
    rows: list[dict[str, Any]] = []

    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc").reset_index(drop=True)
        if g.empty:
            continue
        n_points = len(g)
        r = g["r_kpc"].to_numpy(dtype=float)
        v_obs = g["v_obs_kms"].to_numpy(dtype=float)
        v_err = g["v_err_kms"].to_numpy(dtype=float)
        v_bar = g["v_bar_kms"].to_numpy(dtype=float)
        data_mode = str(g["data_mode"].iloc[0]) if "data_mode" in g.columns else "unknown"

        for split in all_holdout_splits(n_points):
            for model_name in tdf_models:
                rows.extend(
                    _export_tdf_test_points(
                        gid,
                        r,
                        v_obs,
                        v_err,
                        v_bar,
                        tau_df,
                        model_name,
                        split.name,
                        split.train_indices,
                        split.test_indices,
                        k_g=tdf_cfg.k_g,
                        safety_factor=tdf_cfg.amplitude_bound_safety_factor,
                        negative_v2_penalty=tdf_cfg.negative_v2_penalty,
                        data_mode=data_mode,
                        n_points=n_points,
                    )
                )
            if "nfw_refit" in baseline_models:
                rows.extend(
                    _export_nfw_test_points(
                        gid,
                        r,
                        v_obs,
                        v_err,
                        v_bar,
                        split.name,
                        split.train_indices,
                        split.test_indices,
                        models_yaml,
                        data_mode,
                        n_points,
                    )
                )
            if "mond_fit_a0_simple" in baseline_models:
                rows.extend(
                    _export_mond_test_points(
                        gid,
                        r,
                        v_obs,
                        v_err,
                        v_bar,
                        split.name,
                        split.train_indices,
                        split.test_indices,
                        models_yaml,
                        data_mode,
                        n_points,
                    )
                )

    df = pd.DataFrame(rows)
    for col in HOLDOUT_POINT_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan
    return df[HOLDOUT_POINT_COLUMNS]


def load_holdout_export_configs(
    recon_path: Path | str,
    models_path: Path | str,
) -> tuple[dict, dict]:
    return load_yaml(Path(recon_path)), load_yaml(Path(models_path))
