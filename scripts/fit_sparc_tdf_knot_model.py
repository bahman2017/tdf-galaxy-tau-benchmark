from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.metrics.comparison import chi_square, rmse, safe_reduced_chi_square
from tdf_galaxy_tau.metrics.information_criteria import aic, bic, model_parameter_count
from tdf_galaxy_tau.models.fitting import fit_tdf_knot_baseline
from tdf_galaxy_tau.models.tdf_knot import (
    amplitude_bounds_from_reconstruction,
    fixed_knot_radii_kpc,
    galaxy_tau_reconstruction_arrays,
    initial_knot_amplitudes_from_reconstruction,
    integrate_tau_profile,
    interpolate_dtaudr_at_radii,
    knot_position_rule_label,
    load_tdf_knot_config,
    n_knots_for_model,
)
from tdf_galaxy_tau.plotting.tau_profiles import plot_tdf_knot_tau_gradient, plot_tdf_knot_tau_profile
from tdf_galaxy_tau.reconstruction.radial_tau import load_selected_galaxy_ids

TABLE_COMPARISON = Path("outputs/tables/sparc_tdf_knot_model_comparison.csv")
TABLE_PARAMS = Path("outputs/tables/sparc_tdf_knot_fit_parameters.csv")
FIG_DIR = Path("outputs/figures/sparc_subset")


def _metrics_row(
    galaxy_id: str,
    model_name: str,
    n_points: int,
    v_obs,
    v_model,
    v_err,
    *,
    fit_success: bool,
    fit_status: str,
    data_source: str,
    data_mode: str,
) -> dict:
    n_params = model_parameter_count(model_name)
    chi2 = chi_square(v_obs, v_model, v_err)
    return {
        "model_name": model_name,
        "galaxy_id": galaxy_id,
        "n_points": n_points,
        "n_parameters": n_params,
        "rmse_kms": rmse(v_obs, v_model),
        "chi_square": chi2,
        "reduced_chi_square": safe_reduced_chi_square(chi2, n_points, n_params),
        "aic": aic(chi2, n_params),
        "bic": bic(chi2, n_points, n_params),
        "fit_success": bool(fit_success),
        "fit_status": fit_status,
        "data_source": data_source,
        "data_mode": data_mode,
        "comparison_stage": "phase_3b_tdf_knot_fit",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fit TDF piecewise-linear knot model on SPARC subset")
    parser.add_argument("--data", required=True)
    parser.add_argument("--subset", required=True)
    parser.add_argument("--tau-profiles", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    data = pd.read_csv(args.data)
    tau_profiles = pd.read_csv(args.tau_profiles)
    recon_yaml = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    tdf_cfg = load_tdf_knot_config(recon_yaml)
    selected_ids = load_selected_galaxy_ids(args.subset)

    rows_metrics: list[dict] = []
    rows_params: list[dict] = []
    fit_notes: list[str] = []

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_COMPARISON.parent.mkdir(parents=True, exist_ok=True)

    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc").reset_index(drop=True)
        if g.empty:
            fit_notes.append(f"{gid}: missing from data")
            continue

        r = g["r_kpc"].to_numpy()
        v_obs = g["v_obs_kms"].to_numpy()
        v_err = g["v_err_kms"].to_numpy()
        v_bar = g["v_bar_kms"].to_numpy()
        data_source = str(g["data_source"].iloc[0])
        data_mode = str(g["data_mode"].iloc[0])

        r_recon, dtaudr_recon = galaxy_tau_reconstruction_arrays(tau_profiles, gid)
        amp_bounds = amplitude_bounds_from_reconstruction(
            dtaudr_recon,
            safety_factor=tdf_cfg.amplitude_bound_safety_factor,
        )
        tau_diag = None
        tg = tau_profiles[tau_profiles["galaxy_id"] == gid].sort_values("r_kpc")
        if not tg.empty and "tau_reconstructed" in tg.columns:
            tau_diag = tg["tau_reconstructed"].to_numpy(dtype=float)

        v_tdf_3 = None
        for model_name in tdf_cfg.variants:
            n_knots = n_knots_for_model(model_name)
            knot_r = fixed_knot_radii_kpc(r, n_knots)
            x0 = initial_knot_amplitudes_from_reconstruction(knot_r, r_recon, dtaudr_recon)
            fit = fit_tdf_knot_baseline(
                r,
                v_obs,
                v_err,
                v_bar,
                model_name=model_name,
                knot_r_kpc=knot_r,
                initial_knot_dtaudr=x0,
                dtaudr_bounds=amp_bounds,
                k_tau=tdf_cfg.k_tau,
                negative_v2_penalty=tdf_cfg.negative_v2_penalty,
            )
            v_model = fit.v_model_kms if fit.fit_success else v_bar
            rows_metrics.append(
                _metrics_row(
                    gid,
                    model_name,
                    len(g),
                    v_obs,
                    v_model,
                    v_err,
                    fit_success=fit.fit_success,
                    fit_status=fit.fit_status,
                    data_source=data_source,
                    data_mode=data_mode,
                )
            )
            if not fit.fit_success:
                fit_notes.append(f"{gid} {model_name}: {fit.fit_status}")
                continue

            theta = np.array([fit.params[f"knot_{i}_dtaudr"] for i in range(n_knots)])
            for i in range(n_knots):
                rows_params.append(
                    {
                        "galaxy_id": gid,
                        "model_name": model_name,
                        "K_tau": tdf_cfg.k_tau,
                        "knot_index": i,
                        "knot_r_kpc": float(knot_r[i]),
                        "knot_position_rule": knot_position_rule_label(n_knots),
                        "fitted_dtaudr": float(theta[i]),
                        "lower_bound": amp_bounds[0],
                        "upper_bound": amp_bounds[1],
                        "n_parameters": fit.n_parameters,
                        "fit_success": fit.fit_success,
                        "fit_status": fit.fit_status,
                    }
                )

            if model_name == "tdf_3knot":
                v_tdf_3 = v_model
                dtaudr_model = interpolate_dtaudr_at_radii(r, knot_r, theta)
                tau_model = integrate_tau_profile(r, dtaudr_model)
                plot_tdf_knot_tau_gradient(
                    gid,
                    r,
                    dtaudr_model,
                    knot_r,
                    theta,
                    FIG_DIR / f"{gid}_tdf_knot_tau_gradient.png",
                    dtaudr_diagnostic=dtaudr_recon,
                )
                plot_tdf_knot_tau_profile(
                    gid,
                    r,
                    tau_model,
                    FIG_DIR / f"{gid}_tdf_knot_tau_profile.png",
                    tau_diagnostic=tau_diag,
                )

    df_metrics = pd.DataFrame(rows_metrics)
    df_params = pd.DataFrame(rows_params)
    df_metrics.to_csv(TABLE_COMPARISON, index=False)
    df_params.to_csv(TABLE_PARAMS, index=False)

    print(f"Processed galaxies: {', '.join(selected_ids)}")
    print(f"K_tau (fixed): {tdf_cfg.k_tau}")
    print(f"Amplitude bounds safety factor: {tdf_cfg.amplitude_bound_safety_factor}")
    print(f"Wrote TDF comparison: {TABLE_COMPARISON}")
    print(f"Wrote TDF parameters: {TABLE_PARAMS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
