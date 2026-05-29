from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.reconstruction.radial_tau import (
    PHASE_2A_OUTPUT_COLUMNS,
    load_reconstruction_config,
    load_selected_galaxy_ids,
    reconstruct_selected_subset,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "data/processed/sparc/sparc_rotmod_standardized.csv"
SUBSET_CSV = ROOT / "outputs/tables/sparc_subset_selection.csv"
CONFIG = ROOT / "configs/reconstruction.yaml"
REPORT = ROOT / "outputs/reports/sparc_radial_tau_reconstruction_report.md"


@pytest.mark.skipif(not DATA_CSV.is_file(), reason="standardized SPARC CSV not present")
def test_reconstruct_selected_subset_preserves_ids_only() -> None:
    cfg = load_reconstruction_config(CONFIG)
    selected = load_selected_galaxy_ids(SUBSET_CSV)
    combined = reconstruct_selected_subset(DATA_CSV, SUBSET_CSV, cfg)
    assert set(combined["galaxy_id"].unique()) == set(selected)
    assert list(combined.columns) == PHASE_2A_OUTPUT_COLUMNS


@pytest.mark.skipif(not REPORT.is_file(), reason="run reconstruct_sparc_subset_tau.py first")
def test_reconstruction_report_has_non_inference_language() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert "does not compare TDF against NFW or Burkert" in text
    assert "does not disprove dark matter" in text


def test_reconstruction_script_outputs(tmp_path: Path) -> None:
    data = pd.DataFrame(
        {
            "galaxy_id": ["G1"] * 3 + ["G2"] * 3,
            "source_file": ["G1_rotmod.dat"] * 3 + ["G2_rotmod.dat"] * 3,
            "distance_mpc": [1.0] * 6,
            "r_kpc": [1.0, 2.0, 3.0, 1.0, 2.0, 3.0],
            "v_obs_kms": [50.0, 55.0, 60.0, 40.0, 45.0, 50.0],
            "v_err_kms": [2.0] * 6,
            "v_gas_kms": [10.0] * 6,
            "v_disk_kms": [20.0] * 6,
            "v_bulge_kms": [0.0] * 6,
            "sb_disk_lpc2": [1.0] * 6,
            "sb_bulge_lpc2": [0.0] * 6,
            "v_bar_kms": [22.36] * 6,
            "residual_v2_kms2": [100.0] * 6,
            "quality_flag": ["ok"] * 6,
            "data_source": ["SPARC_Lelli2016"] * 6,
            "data_mode": ["observational_raw_ingestion"] * 6,
        }
    )
    subset = pd.DataFrame({"galaxy_id": ["G1", "G2"], "selected": [True, False]})
    data_csv = tmp_path / "data.csv"
    subset_csv = tmp_path / "subset.csv"
    data.to_csv(data_csv, index=False)
    subset.to_csv(subset_csv, index=False)

    cfg = load_reconstruction_config(CONFIG)
    out = reconstruct_selected_subset(data_csv, subset_csv, cfg)
    assert set(out["galaxy_id"].unique()) == {"G1"}
