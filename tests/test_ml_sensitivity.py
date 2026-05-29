from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.ml_sensitivity import (
    MlSensitivityConfig,
    TARGET_GALAXY,
    compute_v_bar_scaled_kms,
    is_plausible_scale,
    run_ml_sensitivity_audit,
    scaled_galaxy_frame,
)


def test_v_bar_scaling_matches_canonical_at_unity() -> None:
    v_gas = np.array([1.0, 2.0])
    v_disk = np.array([3.0, 4.0])
    v_bulge = np.array([0.0, 5.0])
    v_can = np.sqrt(v_gas**2 + v_disk**2 + v_bulge**2)
    v_scaled = compute_v_bar_scaled_kms(v_gas, v_disk, v_bulge, disk_scale=1.0, bulge_scale=1.0)
    np.testing.assert_allclose(v_scaled, v_can)


def test_bulge_scale_reduces_v_bar_when_bulge_dominated() -> None:
    v_bar_full = compute_v_bar_scaled_kms(
        np.array([0.0]), np.array([10.0]), np.array([300.0]), disk_scale=1.0, bulge_scale=1.0
    )[0]
    v_bar_low = compute_v_bar_scaled_kms(
        np.array([0.0]), np.array([10.0]), np.array([300.0]), disk_scale=1.0, bulge_scale=0.5
    )[0]
    assert v_bar_low < v_bar_full


def test_small_grid_audit() -> None:
    root = Path(__file__).resolve().parents[1]
    rotmod_path = root / "data/processed/sparc/sparc_rotmod_standardized.csv"
    if not rotmod_path.is_file():
        pytest.skip("rotmod missing")
    rotmod = pd.read_csv(rotmod_path)
    cfg = MlSensitivityConfig(
        disk_scales=(1.0, 0.7),
        bulge_scales=(1.0, 0.5),
        tdf_models=("tdf_3knot",),
    )
    summary, detail, comp = run_ml_sensitivity_audit(
        rotmod,
        ["DDO154"],
        recon_path=root / "configs/reconstruction.yaml",
        models_path=root / "configs/models.yaml",
        holdout_validation_path=root / "outputs/tables/sparc_tdf_holdout_validation.csv",
        ml_config=cfg,
    )
    assert len(summary) == 4
    assert "classification_under_scale" in summary.columns


def test_full_audit_script() -> None:
    root = Path(__file__).resolve().parents[1]
    if not (root / "data/processed/sparc/sparc_rotmod_standardized.csv").is_file():
        pytest.skip("data missing")
    subprocess.run(
        ["python3", "scripts/run_sparc_ml_sensitivity_audit.py"],
        cwd=root,
        check=True,
        timeout=300,
    )
    assert (root / "outputs/tables/sparc_ml_sensitivity_summary.csv").is_file()
    comp = pd.read_csv(root / "outputs/tables/sparc_ml_sensitivity_holdout_comparison.csv")
    ngc = comp[comp["galaxy_id"] == TARGET_GALAXY].iloc[0]
    assert np.isfinite(ngc["canonical_tdf_3knot_rmse"])


def test_plausible_scale_band() -> None:
    assert is_plausible_scale(1.0, 0.7)
    assert not is_plausible_scale(0.2, 1.3)
