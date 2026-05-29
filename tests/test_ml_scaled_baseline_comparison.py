from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.ml_scaled_baseline_comparison import (
    MlScaledBaselineConfig,
    TARGET_GALAXY,
    build_ngc7814_fair_comparison,
    run_ml_scaled_baseline_comparison,
    run_scaled_nfw_holdout,
)
from tdf_galaxy_tau.analysis.ml_sensitivity import scaled_galaxy_frame


def test_scaled_nfw_holdout_finite() -> None:
    root = Path(__file__).resolve().parents[1]
    rotmod_path = root / "data/processed/sparc/sparc_rotmod_standardized.csv"
    if not rotmod_path.is_file():
        pytest.skip("rotmod missing")
    rotmod = pd.read_csv(rotmod_path)
    g = rotmod[rotmod["galaxy_id"] == "DDO154"].sort_values("r_kpc")
    g_scaled = scaled_galaxy_frame(g, disk_scale=1.0, bulge_scale=1.0)
    from tdf_galaxy_tau.validation.holdout_residuals import load_holdout_export_configs

    _, models_yaml = load_holdout_export_configs(
        root / "configs/reconstruction.yaml", root / "configs/models.yaml"
    )
    m = run_scaled_nfw_holdout(g_scaled, models_yaml=models_yaml, n_points=len(g_scaled))
    assert np.isfinite(m["total_holdout_rmse_kms"])
    assert m["fit_success"]


def test_small_grid_fair_comparison() -> None:
    root = Path(__file__).resolve().parents[1]
    rotmod_path = root / "data/processed/sparc/sparc_rotmod_standardized.csv"
    if not rotmod_path.is_file():
        pytest.skip("rotmod missing")
    rotmod = pd.read_csv(rotmod_path)
    cfg = MlScaledBaselineConfig(
        disk_scales=(1.0,),
        bulge_scales=(1.0, 0.5),
        models=("tdf_3knot", "nfw_refit_scaled"),
    )
    comparison, ngc_fair, best = run_ml_scaled_baseline_comparison(
        rotmod,
        ["DDO154"],
        recon_path=root / "configs/reconstruction.yaml",
        models_path=root / "configs/models.yaml",
        holdout_validation_path=root / "outputs/tables/sparc_tdf_holdout_validation.csv",
        ml_config=cfg,
    )
    assert len(comparison) == 4
    assert "comparison_mode" in comparison.columns
    assert comparison["comparison_mode"].iloc[0] == "train_only_scaled_holdout"
    assert len(best) == 1


def test_ngc7814_fair_table_columns() -> None:
    df = pd.DataFrame(
        [
            {
                "galaxy_id": TARGET_GALAXY,
                "disk_scale": 1.0,
                "bulge_scale": 0.5,
                "model_name": "tdf_3knot",
                "total_holdout_rmse_kms": 5.0,
            },
            {
                "galaxy_id": TARGET_GALAXY,
                "disk_scale": 1.0,
                "bulge_scale": 0.5,
                "model_name": "nfw_refit_scaled",
                "total_holdout_rmse_kms": 10.0,
            },
            {
                "galaxy_id": TARGET_GALAXY,
                "disk_scale": 1.0,
                "bulge_scale": 0.5,
                "model_name": "mond_fit_a0_scaled",
                "total_holdout_rmse_kms": 12.0,
            },
            {
                "galaxy_id": TARGET_GALAXY,
                "disk_scale": 1.0,
                "bulge_scale": 0.5,
                "model_name": "tdf_5knot",
                "total_holdout_rmse_kms": 6.0,
            },
        ]
    )
    fair = build_ngc7814_fair_comparison(df)
    row = fair.iloc[0]
    assert row["tdf_beats_nfw"]
    assert row["best_model"] == "tdf_3knot"


def test_full_comparison_script() -> None:
    root = Path(__file__).resolve().parents[1]
    if not (root / "data/processed/sparc/sparc_rotmod_standardized.csv").is_file():
        pytest.skip("data missing")
    subprocess.run(
        ["python3", "scripts/run_sparc_ml_scaled_baseline_comparison.py"],
        cwd=root,
        check=True,
        timeout=600,
    )
    assert (root / "outputs/tables/sparc_ml_scaled_model_comparison.csv").is_file()
    fair = pd.read_csv(root / "outputs/tables/ngc7814_ml_scaled_fair_comparison.csv")
    assert len(fair) == 20
