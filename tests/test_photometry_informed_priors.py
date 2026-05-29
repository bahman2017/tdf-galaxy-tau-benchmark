from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.ml_priors import TARGET_GALAXY, load_ml_priors_config
from tdf_galaxy_tau.analysis.photometry_informed_priors import (
    GALAXY_ORDER,
    PhotometryInformedScenario,
    build_photometry_informed_prior_weights,
    cell_in_photometry_scope,
    compute_photometry_prior_weighted_summary,
    parse_photometry_informed_scenarios,
    photometry_cell_weight,
    run_photometry_informed_prior_pipeline,
)
from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION


def test_parse_photometry_scenarios() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_ml_priors_config(root / "configs/ml_priors.yaml")
    names = {s.name for s in parse_photometry_informed_scenarios(cfg)}
    assert "photometry_uniform_plausible" in names
    assert "morphology_aware_conservative" in names
    assert "ngc7814_bulge_sensitivity_diagnostic" in names
    assert "canonical_anchor_prior" in names


def test_ngc7814_diagnostic_zero_on_other_galaxies() -> None:
    sc = PhotometryInformedScenario(
        name="ngc7814_bulge_sensitivity_diagnostic",
        description="",
        grid_scope="plausible_only",
        weighting="ngc7814_bulge_diagnostic",
        metadata_basis="test",
        galaxy_filter="NGC7814",
        params={},
    )
    w_other = photometry_cell_weight(
        "NGC2403",
        0.7,
        0.5,
        sc,
        photo_row=pd.Series(dtype=float),
        subset_row=None,
        plausible_disk=(0.7, 1.3),
        plausible_bulge=(0.5, 1.0),
        canonical_disk=1.0,
        canonical_bulge=1.0,
    )
    assert w_other == 0.0


def test_morphology_aware_downweights_low_bulge_for_early_type() -> None:
    sc = PhotometryInformedScenario(
        name="morphology_aware_conservative",
        description="",
        grid_scope="plausible_only",
        weighting="morphology_aware",
        metadata_basis="test",
        galaxy_filter=None,
        params={},
    )
    photo = pd.Series({"morphological_type": 2.0})
    subset = pd.Series({"bulge_dominated_proxy": True, "has_bulge_proxy": True})
    w_low = photometry_cell_weight(
        TARGET_GALAXY,
        1.0,
        0.5,
        sc,
        photo_row=photo,
        subset_row=subset,
        plausible_disk=(0.7, 1.3),
        plausible_bulge=(0.5, 1.0),
        canonical_disk=1.0,
        canonical_bulge=1.0,
    )
    w_high = photometry_cell_weight(
        TARGET_GALAXY,
        1.0,
        1.0,
        sc,
        photo_row=photo,
        subset_row=subset,
        plausible_disk=(0.7, 1.3),
        plausible_bulge=(0.5, 1.0),
        canonical_disk=1.0,
        canonical_bulge=1.0,
    )
    assert w_high >= w_low


def test_build_weights_normalized_per_galaxy_scenario(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    photo = root / "data/processed/sparc/sparc_photometry_metadata.csv"
    subset = root / "outputs/tables/sparc_subset_photometry_context.csv"
    if not photo.is_file() or not subset.is_file():
        pytest.skip("Phase 4J outputs missing")
    cfg = load_ml_priors_config(root / "configs/ml_priors.yaml")
    weights = build_photometry_informed_prior_weights(
        pd.read_csv(photo),
        pd.read_csv(subset),
        cfg,
    )
    assert {"galaxy_id", "scenario_name", "normalized_weight", "diagnostic_only"}.issubset(weights.columns)
    for (gid, sc), grp in weights.groupby(["galaxy_id", "scenario_name"]):
        if grp["raw_weight"].sum() <= 0:
            continue
        assert np.isclose(grp["normalized_weight"].sum(), 1.0, rtol=1e-5, atol=1e-5), (gid, sc)


def test_summary_from_phase4g(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    comp = root / "outputs/tables/sparc_ml_scaled_model_comparison.csv"
    if not comp.is_file():
        pytest.skip("Phase 4G missing")
    cfg = load_ml_priors_config(root / "configs/ml_priors.yaml")
    photo = pd.read_csv(root / "data/processed/sparc/sparc_photometry_metadata.csv")
    subset = pd.read_csv(root / "outputs/tables/sparc_subset_photometry_context.csv")
    weights = build_photometry_informed_prior_weights(photo, subset, cfg)
    summary = compute_photometry_prior_weighted_summary(pd.read_csv(comp), weights)
    n_sc = len(parse_photometry_informed_scenarios(cfg))
    # NGC7814-only scenario yields rows for one galaxy only (76 = 6*3*4 + 4)
    assert len(summary) == (len(MANDATED_GALAXY_CLASSIFICATION) * (n_sc - 1) + 1) * 4


def test_pipeline_scripts(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    if not (root / "outputs/tables/sparc_ml_scaled_model_comparison.csv").is_file():
        pytest.skip("Phase 4G missing")
    subprocess.run(
        ["python3", "scripts/build_photometry_informed_ml_priors.py"],
        cwd=root,
        check=True,
        timeout=60,
    )
    subprocess.run(
        ["python3", "scripts/apply_photometry_informed_prior_weighting.py"],
        cwd=root,
        check=True,
        timeout=60,
    )
    report = (root / "outputs/reports/sparc_photometry_informed_prior_report.md").read_text()
    assert "does not perform final M/L calibration" in report
    assert "tdf_3knot" in report


def test_cell_in_scope() -> None:
    sc = PhotometryInformedScenario(
        name="x",
        description="",
        grid_scope="plausible_only",
        weighting="uniform",
        metadata_basis="",
        galaxy_filter=None,
        params={},
    )
    assert cell_in_photometry_scope(0.7, 0.5, sc, plausible_disk=(0.7, 1.3), plausible_bulge=(0.5, 1.0))
    assert not cell_in_photometry_scope(0.5, 0.5, sc, plausible_disk=(0.7, 1.3), plausible_bulge=(0.5, 1.0))
