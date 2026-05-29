from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.ktau_sensitivity import (
    ktau_stability_flag,
    load_ktau_sensitivity_config,
    merge_ktau_tdf_with_phase4g_baselines,
    run_ktau_tdf_grid,
)
from tdf_galaxy_tau.analysis.ml_priors import NFW_MODEL
from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION


def test_load_ktau_config() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_ktau_sensitivity_config(root / "configs/reconstruction.yaml")
    assert 0.5 in cfg["k_tau_values"]
    assert 1.0 in cfg["k_tau_values"]
    assert cfg["reference_k_tau"] == 1.0


def test_ktau_stability_flag() -> None:
    ref = {"prior_weighted_mean_rmse": 10.0, "fraction_prior_weight_model_wins": 0.2}
    cur = {"prior_weighted_mean_rmse": 10.5, "fraction_prior_weight_model_wins": 0.22}
    assert ktau_stability_flag(cur, ref) == "stable_vs_reference_ktau"
    cur2 = {"prior_weighted_mean_rmse": 20.0, "fraction_prior_weight_model_wins": 0.5}
    assert ktau_stability_flag(cur2, ref) == "sensitive_to_ktau"


def test_merge_baselines() -> None:
    root = Path(__file__).resolve().parents[1]
    p4g = root / "outputs/tables/sparc_ml_scaled_model_comparison.csv"
    if not p4g.is_file():
        pytest.skip("Phase 4G missing")
    phase4g = pd.read_csv(p4g)
    tdf = phase4g[phase4g["model_name"].str.startswith("tdf")].head(4).copy()
    tdf["K_tau"] = 0.5
    merged = merge_ktau_tdf_with_phase4g_baselines(tdf, phase4g)
    assert NFW_MODEL in merged["model_name"].values
    assert "tdf_3knot" in merged["model_name"].values


def test_ktau_grid_one_galaxy(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    rotmod = root / "data/processed/sparc/sparc_rotmod_standardized.csv"
    subset = root / "outputs/tables/sparc_subset_selection.csv"
    if not rotmod.is_file() or not subset.is_file():
        pytest.skip("data missing")
    ids = pd.read_csv(subset)["galaxy_id"].tolist()[:1]
    data = pd.read_csv(rotmod)
    grid = run_ktau_tdf_grid(data, ids, [1.0, 2.0], recon_path=root / "configs/reconstruction.yaml")
    assert len(grid) == 2 * 20 * 2  # 2 k_tau * 20 cells * 2 models
    assert np.isfinite(grid["total_holdout_rmse_kms"].iloc[0])


def test_run_pipeline_smoke(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    needed = [
        root / "outputs/tables/sparc_ml_scaled_model_comparison.csv",
        root / "outputs/tables/sparc_photometry_informed_prior_weights.csv",
    ]
    if not all(p.is_file() for p in needed):
        pytest.skip("Phase 4G/4K outputs missing")
    subprocess.run(
        ["python3", "scripts/run_photometry_prior_ktau_sensitivity.py"],
        cwd=root,
        check=True,
        timeout=300,
    )
    report = (root / "outputs/reports/sparc_ktau_sensitivity_report.md").read_text()
    assert "does not measure K_tau" in report
    summary = pd.read_csv(root / "outputs/tables/sparc_ktau_sensitivity_summary.csv")
    n_sc = len(summary["scenario_name"].unique())
    assert len(summary) >= len(MANDATED_GALAXY_CLASSIFICATION) * 3 * 2 * (n_sc - 1) + 4

