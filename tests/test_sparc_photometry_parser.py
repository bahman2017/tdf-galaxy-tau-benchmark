from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.data.sparc_photometry_parser import (
    load_table1_photometry,
    normalize_galaxy_id,
    parse_vizier_table1_tsv,
)


def test_normalize_galaxy_id() -> None:
    assert normalize_galaxy_id("NGC 7814 ") == "NGC7814"


def test_parse_vizier_working_copy() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "data/raw/sparc/photometry/SPARC_Table1_vizier_working_copy.tsv"
    if not p.is_file():
        pytest.skip("table1 working copy missing")
    df = parse_vizier_table1_tsv(p)
    assert len(df) >= 175
    req = {
        "galaxy_id",
        "distance_mpc",
        "inclination_deg",
        "luminosity_3p6_lsun",
        "disk_scale_length_kpc",
        "central_surface_brightness",
        "morphological_type",
    }
    assert req.issubset(df.columns)
    ngc = df[df["galaxy_id"] == "NGC7814"].iloc[0]
    assert float(ngc["distance_mpc"]) > 10


def test_load_table1_prefers_available_source() -> None:
    root = Path(__file__).resolve().parents[1]
    df, source = load_table1_photometry(root / "data/raw/sparc/photometry")
    assert len(df) >= 175
    assert source
