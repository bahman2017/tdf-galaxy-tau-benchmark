from __future__ import annotations

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.metrics.comparison import chi_square, rmse, safe_reduced_chi_square
from tdf_galaxy_tau.metrics.information_criteria import aic, bic, model_parameter_count
from tdf_galaxy_tau.models.fitting import (
    fit_burkert_baseline_log,
    fit_mond_a0_simple,
    fit_nfw_baseline_log,
    fit_tdf_knot_baseline,
)
from tdf_galaxy_tau.models.tdf_knot import (
    amplitude_bounds_from_reconstruction,
    fixed_knot_radii_kpc,
    galaxy_tau_reconstruction_train_only,
    initial_knot_amplitudes_from_reconstruction,
    load_tdf_knot_config,
    n_knots_for_model,
    tdf_velocity_kms,
)
from tdf_galaxy_tau.validation.holdout import all_holdout_splits, mask_from_indices


def _test_metrics(
    v_obs: np.ndarray,
    v_model: np.ndarray,
    v_err: np.ndarray,
    model_name: str,
) -> dict[str, float]:
    n_params = model_parameter_count(model_name)
    n_pts = len(v_obs)
    chi2 = chi_square(v_obs, v_model, v_err)
    return {
        "test_rmse_kms": rmse(v_obs, v_model),
        "test_chi_square": chi2,
        "test_reduced_chi_square": safe_reduced_chi_square(chi2, n_pts, n_params),
        "test_aic": aic(chi2, n_params),
        "test_bic": bic(chi2, n_pts, n_params),
    }


def _fit_tdf_holdout_row(
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
) -> dict[str, object]:
    train_mask = mask_from_indices(len(r), train_idx)
    test_mask = mask_from_indices(len(r), test_idx)
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
    v_test = fit.v_model_kms[test_mask] if fit.fit_success else v_bar[test_mask]
    tm = _test_metrics(v_obs[test_mask], v_test, v_err[test_mask], model_name)
    return {
        "galaxy_id": gid,
        "split_name": split_name,
        "model_name": model_name,
        "train_n": int(train_mask.sum()),
        "test_n": int(test_mask.sum()),
        "fit_success": fit.fit_success,
        "fit_status": fit.fit_status,
        "K_tau": k_g,
        "bounds_safety_factor": safety_factor,
        **tm,
    }


def _fit_nfw_holdout_row(
    gid: str,
    r: np.ndarray,
    v_obs: np.ndarray,
    v_err: np.ndarray,
    v_bar: np.ndarray,
    split_name: str,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    models_yaml: dict,
) -> dict[str, object]:
    train_mask = mask_from_indices(len(r), train_idx)
    test_mask = mask_from_indices(len(r), test_idx)
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
    if fit.fit_success:
        from tdf_galaxy_tau.models.nfw import nfw_params_from_log10, nfw_velocity

        log_rho = fit.log_params["log10_rho_s"] if fit.log_params else 0.0
        log_rs = fit.log_params["log10_r_s"] if fit.log_params else 0.0
        p = nfw_params_from_log10(log_rho, log_rs)
        v_halo = nfw_velocity(r[test_mask], p)
        v_test = np.sqrt(np.maximum(v_bar[test_mask] ** 2 + v_halo**2, 0.0))
    else:
        v_test = v_bar[test_mask]
    tm = _test_metrics(v_obs[test_mask], v_test, v_err[test_mask], "nfw_refit")
    return {
        "galaxy_id": gid,
        "split_name": split_name,
        "model_name": "nfw_refit",
        "train_n": int(train_mask.sum()),
        "test_n": int(test_mask.sum()),
        "fit_success": fit.fit_success,
        "fit_status": fit.fit_status,
        "K_tau": np.nan,
        "bounds_safety_factor": np.nan,
        **tm,
    }


def _fit_mond_holdout_row(
    gid: str,
    r: np.ndarray,
    v_obs: np.ndarray,
    v_err: np.ndarray,
    v_bar: np.ndarray,
    split_name: str,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    models_yaml: dict,
) -> dict[str, object]:
    train_mask = mask_from_indices(len(r), train_idx)
    test_mask = mask_from_indices(len(r), test_idx)
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
    if fit.fit_success:
        from tdf_galaxy_tau.models.mond import mond_fit_a0_velocity_kms

        log_a0 = fit.log_params["log10_a0_m_s2"] if fit.log_params else log_init
        v_test = mond_fit_a0_velocity_kms(r[test_mask], v_bar[test_mask], log_a0)
    else:
        v_test = v_bar[test_mask]
    tm = _test_metrics(v_obs[test_mask], v_test, v_err[test_mask], "mond_fit_a0_simple")
    return {
        "galaxy_id": gid,
        "split_name": split_name,
        "model_name": "mond_fit_a0_simple",
        "train_n": int(train_mask.sum()),
        "test_n": int(test_mask.sum()),
        "fit_success": fit.fit_success,
        "fit_status": fit.fit_status,
        "K_tau": np.nan,
        "bounds_safety_factor": np.nan,
        **tm,
    }


def run_holdout_validation(
    data: pd.DataFrame,
    tau_df: pd.DataFrame,
    selected_ids: list[str],
    recon_yaml: dict,
    models_yaml: dict,
    *,
    tdf_models: tuple[str, ...] = ("tdf_3knot", "tdf_5knot"),
    include_baselines: bool = True,
) -> pd.DataFrame:
    """Aggregated holdout test RMSE. Per-point export: holdout_residuals.export_holdout_point_residuals."""
    tdf_cfg = load_tdf_knot_config(recon_yaml)
    rows: list[dict[str, object]] = []

    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc").reset_index(drop=True)
        if g.empty:
            continue
        r = g["r_kpc"].to_numpy()
        v_obs = g["v_obs_kms"].to_numpy()
        v_err = g["v_err_kms"].to_numpy()
        v_bar = g["v_bar_kms"].to_numpy()

        for split in all_holdout_splits(len(g)):
            for model_name in tdf_models:
                rows.append(
                    _fit_tdf_holdout_row(
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
                    )
                )
            if include_baselines:
                rows.append(
                    _fit_nfw_holdout_row(
                        gid, r, v_obs, v_err, v_bar, split.name,
                        split.train_indices, split.test_indices, models_yaml,
                    )
                )
                rows.append(
                    _fit_mond_holdout_row(
                        gid, r, v_obs, v_err, v_bar, split.name,
                        split.train_indices, split.test_indices, models_yaml,
                    )
                )

    return pd.DataFrame(rows)


def load_yaml(path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
