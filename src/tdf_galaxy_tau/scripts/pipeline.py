from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from tdf_galaxy_tau.data.sparc_loader import build_mock_sparc_subset, load_sparc_like_csv
from tdf_galaxy_tau.metrics.comparison import chi_square, reduced_chi_square, rmse
from tdf_galaxy_tau.metrics.information_criteria import aic, bic, model_parameter_count
from tdf_galaxy_tau.models.baryonic import add_baryonic_column
from tdf_galaxy_tau.plotting.diagnostics import write_plot_warning_report
from tdf_galaxy_tau.plotting.rotation_curves import plot_rotation_curve
from tdf_galaxy_tau.plotting.tau_profiles import plot_tau_profile
from tdf_galaxy_tau.reconstruction.radial_tau import TauReconstructionConfig, reconstruct_radial_tau_profile


MOCK_WARNING = "No observational claim can be made from mock data."


def _load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def run_pipeline(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/sparc_subset.yaml")
    args = parser.parse_args(argv)

    run_config = _load_config(Path(args.config))
    recon_config = _load_config(Path("configs/reconstruction.yaml"))

    input_csv = Path(run_config.get("input_csv", "data/processed/sparc_subset_processed.csv"))

    using_mock = False
    if input_csv.exists():
        data = load_sparc_like_csv(input_csv)
        if "data_mode" not in data.columns:
            data["data_mode"] = "observational"
    else:
        if not bool(run_config.get("allow_mock_data", True)):
            raise FileNotFoundError(f"Input CSV not found: {input_csv}")
        using_mock = True
        mock_galaxies = list(run_config.get("mock_galaxies", ["MockGalaxy"]))
        data = build_mock_sparc_subset(mock_galaxies)
        print(f"WARNING: {MOCK_WARNING}")

    data = add_baryonic_column(data)

    tau_rows = []
    metric_rows = []
    figure_dir = Path(run_config.get("output_figure_dir", "outputs/figures"))
    k_tau = float(recon_config.get("k_tau", 1.0))
    negative_policy = str(recon_config.get("negative_residual_policy", "allow_signed"))

    for galaxy_id, group in data.groupby("galaxy_id", sort=False):
        recon = reconstruct_radial_tau_profile(
            group,
            galaxy_id,
            TauReconstructionConfig(k_tau=k_tau, negative_residual_policy=negative_policy),
        )
        tau_rows.append(recon)

        model_v = group["v_bar_kms"].to_numpy()
        obs_v = group["v_obs_kms"].to_numpy()
        err_v = group["v_err_kms"].to_numpy()
        chi2 = chi_square(obs_v, model_v, err_v)
        n_points = len(group)
        n_params = model_parameter_count("baryonic")

        metric_rows.append(
            {
                "galaxy_id": galaxy_id,
                "model_name": "baryonic",
                "n_points": n_points,
                "number_of_parameters": n_params,
                "rmse_kms": rmse(obs_v, model_v),
                "chi_square": chi2,
                "reduced_chi_square": reduced_chi_square(chi2, n_points, n_params),
                "aic": aic(chi2, n_params),
                "bic": bic(chi2, n_points, n_params),
                "smoothness_penalty": 0.0,
                "data_mode": "mock" if using_mock else "observational",
                "negative_residual_policy": negative_policy,
            }
        )

        _ = plot_rotation_curve(
            galaxy_id=galaxy_id,
            radius=group["r_kpc"].to_numpy(),
            v_obs=obs_v,
            v_bar=model_v,
            output_path=figure_dir / f"{galaxy_id}_rotation.png",
        )
        _ = plot_tau_profile(
            galaxy_id=galaxy_id,
            radius=recon["r_kpc"].to_numpy(),
            tau=recon["tau_reconstructed"].to_numpy(),
            output_path=figure_dir / f"{galaxy_id}_tau.png",
        )

    tau_df = pd.concat(tau_rows, ignore_index=True)
    metrics_df = pd.DataFrame(metric_rows)

    tau_out = Path(run_config.get("output_tau_profiles", "outputs/tables/sparc_subset_tau_profiles.csv"))
    metrics_out = Path(run_config.get("output_model_comparison", "outputs/tables/model_comparison.csv"))
    tau_out.parent.mkdir(parents=True, exist_ok=True)
    metrics_out.parent.mkdir(parents=True, exist_ok=True)
    tau_df.to_csv(tau_out, index=False)
    metrics_df.to_csv(metrics_out, index=False)

    if using_mock:
        write_plot_warning_report("outputs/reports/mock_data_warning.txt", MOCK_WARNING)

    print(f"Wrote tau profiles: {tau_out}")
    print(f"Wrote model comparison: {metrics_out}")
    return 0
