from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.ml_priors import (
    INTERPRETATION_LOGIC_VERSION,
    TARGET_GALAXY,
    build_ml_prior_weight_audit,
    build_ngc7814_prior_scenario_breakdown,
    cell_prior_weight,
    classify_ngc7814_layered,
    load_ml_priors_config,
    parse_prior_scenarios,
    run_ml_prior_weighting_audit,
)


@pytest.fixture
def root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_normalized_weights_sum_to_one(root: Path) -> None:
    comp = root / "outputs/tables/sparc_ml_scaled_model_comparison.csv"
    if not comp.is_file():
        pytest.skip("4G missing")
    cfg = load_ml_priors_config(root / "configs/ml_priors.yaml")
    audit = build_ml_prior_weight_audit(pd.read_csv(comp), cfg)
    for sc, grp in audit.groupby("scenario_name"):
        assert np.isclose(grp["normalized_weight"].sum(), 1.0, atol=1e-9), sc


def test_bulge_downweight_favors_low_bulge(root: Path) -> None:
    cfg = load_ml_priors_config(root / "configs/ml_priors.yaml")
    scenarios = {s.name: s for s in parse_prior_scenarios(cfg)}
    sc = scenarios["conservative_bulge_downweight_test"]
    p_disk = tuple(cfg["plausible_band"]["disk_scale"])
    p_bulge = tuple(cfg["plausible_band"]["bulge_scale"])
    w_low = cell_prior_weight(1.0, 0.5, sc, canonical_disk=1.0, canonical_bulge=1.0, plausible_disk=p_disk, plausible_bulge=p_bulge)
    w_high = cell_prior_weight(1.0, 1.0, sc, canonical_disk=1.0, canonical_bulge=1.0, plausible_disk=p_disk, plausible_bulge=p_bulge)
    assert w_low > w_high


def test_layered_interpretation_tdf5_not_primary_recovery() -> None:
    layered = classify_ngc7814_layered(
        {
            "tdf_3knot": pd.Series({"fraction_of_prior_weight_where_model_wins": 0.0, "fraction_of_prior_weight_where_tdf_beats_nfw": 0.33, "prior_weighted_mean_rmse": 55.0}),
            "tdf_5knot": pd.Series({"fraction_of_prior_weight_where_model_wins": 0.67, "fraction_of_prior_weight_where_tdf_beats_nfw": 0.33, "prior_weighted_mean_rmse": 40.0}),
            "nfw_refit_scaled": pd.Series({"prior_weighted_mean_rmse": 12.0}),
            "mond_fit_a0_scaled": pd.Series({"prior_weighted_mean_rmse": 14.0}),
        },
        canonical_tdf_rmse=155.8,
        canonical_nfw_rmse=24.89,
    )
    assert layered["interpretation_category"] == "sensitivity_tdf_5knot_diagnostic_recovery"
    assert "tdf_5knot" in layered["recommended_claim_language"]


def test_audit_script(root: Path) -> None:
    if not (root / "outputs/tables/sparc_ml_scaled_model_comparison.csv").is_file():
        pytest.skip("4G missing")
    subprocess.run(
        ["python3", "scripts/audit_ml_prior_weighting.py"],
        cwd=root,
        check=True,
        timeout=120,
    )
    audit = pd.read_csv(root / "outputs/tables/ml_prior_weight_audit.csv")
    ngc = pd.read_csv(root / "outputs/tables/ngc7814_ml_prior_weighted_interpretation.csv")
    assert len(audit) > 0
    assert INTERPRETATION_LOGIC_VERSION in ngc["interpretation_logic_version"].iloc[0]
    uni = ngc[ngc["prior_scenario"] == "uniform_plausible_band"].iloc[0]
    con = ngc[ngc["prior_scenario"] == "conservative_bulge_downweight_test"].iloc[0]
    assert uni["interpretation_category"] == con["interpretation_category"] == "sensitivity_tdf_5knot_diagnostic_recovery"


def test_breakdown_columns(root: Path) -> None:
    comp = root / "outputs/tables/sparc_ml_scaled_model_comparison.csv"
    if not comp.is_file():
        pytest.skip("4G missing")
    cfg = load_ml_priors_config(root / "configs/ml_priors.yaml")
    bd = build_ngc7814_prior_scenario_breakdown(pd.read_csv(comp), cfg)
    assert "tdf_5knot_beats_nfw" in bd.columns
    assert not bd.empty
