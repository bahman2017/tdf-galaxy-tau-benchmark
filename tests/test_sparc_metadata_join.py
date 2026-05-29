from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.data.sparc_metadata_join import (
    TARGET_GALAXY,
    build_subset_photometry_context,
    run_photometry_metadata_ingestion,
)


def test_run_ingestion_outputs() -> None:
    root = Path(__file__).resolve().parents[1]
    rot = root / "data/processed/sparc/sparc_rotmod_standardized.csv"
    if not rot.is_file():
        pytest.skip("rotmod missing")
    metadata, summary, subset = run_photometry_metadata_ingestion(
        rotmod_path=rot,
        photometry_dir=root / "data/raw/sparc/photometry",
        subset_path=root / "outputs/tables/sparc_subset_selection.csv",
    )
    assert len(metadata) == 175
    assert len(subset) == 6
    assert TARGET_GALAXY in subset["galaxy_id"].values
    ngc = subset[subset["galaxy_id"] == TARGET_GALAXY].iloc[0]
    assert bool(ngc["bulge_dominated_proxy"])


def test_subset_context_columns() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "outputs/tables/sparc_subset_photometry_context.csv"
    if not p.is_file():
        pytest.skip("subset context not generated yet")
    df = pd.read_csv(p)
    needed = {
        "galaxy_id",
        "canonical_classification",
        "distance_mpc",
        "inclination_deg",
        "luminosity_3p6_lsun",
        "disk_scale_length_kpc",
        "morphological_type",
        "has_bulge_proxy",
        "bulge_dominated_proxy",
        "notes_for_ml_prior",
    }
    assert needed.issubset(df.columns)
