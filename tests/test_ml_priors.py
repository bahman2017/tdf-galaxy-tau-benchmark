from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.ml_priors import (
    TARGET_GALAXY,
    build_prior_weighted_summary,
    cell_prior_weight,
    load_ml_priors_config,
    parse_prior_scenarios,
    run_ml_prior_weighting,
)
from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION


def test_load_priors_config() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_ml_priors_config(root / "configs/ml_priors.yaml")
    scenarios = parse_prior_scenarios(cfg)
    names = {s.name for s in scenarios}
    assert "uniform_plausible_band" in names
    assert "canonical_delta_prior" in names


def test_uniform_weights_sum_positive() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_ml_priors_config(root / "configs/ml_priors.yaml")
    sc = parse_prior_scenarios(cfg)[0]
    p_disk = tuple(cfg["plausible_band"]["disk_scale"])
    p_bulge = tuple(cfg["plausible_band"]["bulge_scale"])
    w = cell_prior_weight(
        0.7,
        0.5,
        sc,
        canonical_disk=1.0,
        canonical_bulge=1.0,
        plausible_disk=p_disk,
        plausible_bulge=p_bulge,
    )
    assert w > 0


def test_prior_summary_from_phase4g(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    comp = root / "outputs/tables/sparc_ml_scaled_model_comparison.csv"
    if not comp.is_file():
        pytest.skip("Phase 4G output missing")
    cfg = load_ml_priors_config(root / "configs/ml_priors.yaml")
    comparison = pd.read_csv(comp)
    summary = build_prior_weighted_summary(comparison, cfg)
    assert len(summary) == len(MANDATED_GALAXY_CLASSIFICATION) * len(parse_prior_scenarios(cfg)) * 4
    ngc = summary[summary["galaxy_id"] == TARGET_GALAXY]
    assert not ngc.empty
    assert np.isfinite(ngc["prior_weighted_mean_rmse"].iloc[0])


def test_apply_script(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    if not (root / "outputs/tables/sparc_ml_scaled_model_comparison.csv").is_file():
        pytest.skip("Phase 4G missing")
    subprocess.run(
        ["python3", "scripts/apply_ml_prior_weighting.py"],
        cwd=root,
        check=True,
        timeout=60,
    )
    assert (root / "outputs/tables/sparc_ml_prior_weighted_summary.csv").is_file()
    report = (root / "outputs/reports/sparc_ml_prior_framework_report.md").read_text()
    assert "diagnostic placeholder" in report.lower() or "diagnostic placeholders" in report.lower()
    assert "canonical" in report.lower()


def test_run_ml_prior_weighting_returns(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    if not (root / "outputs/tables/sparc_post_ml_results_summary_table.csv").is_file():
        pytest.skip("post-ml table missing")
    summary, ngc = run_ml_prior_weighting(
        comparison_path=root / "outputs/tables/sparc_ml_scaled_model_comparison.csv",
        post_ml_path=root / "outputs/tables/sparc_post_ml_results_summary_table.csv",
    )
    assert len(ngc) >= 3
    assert "interpretation_category" in ngc.columns
    assert "recommended_claim_language" in ngc.columns
