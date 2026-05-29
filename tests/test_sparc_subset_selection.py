from __future__ import annotations

from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.data.subset_selection import SubsetSelectionConfig, select_sparc_subset


def test_subset_selection_prefers_candidates(tmp_path: Path) -> None:
    df = pd.DataFrame(
        [
            {
                "galaxy_id": "CAND1",
                "source_file": "CAND1_rotmod.dat",
                "distance_mpc": 1.0,
                "r_kpc": float(i + 1),
                "v_obs_kms": 100.0 + i,
                "v_err_kms": 2.0,
                "v_gas_kms": 10.0,
                "v_disk_kms": 30.0,
                "v_bulge_kms": 5.0,
                "sb_disk_lpc2": 1.0,
                "sb_bulge_lpc2": 0.0,
                "v_bar_kms": 32.0,
                "residual_v2_kms2": 100.0,
                "quality_flag": "ok",
                "data_source": "SPARC_Lelli2016",
                "data_mode": "observational_raw_ingestion",
            }
            for i in range(12)
        ]
        + [
            {
                "galaxy_id": "OTHER1",
                "source_file": "OTHER1_rotmod.dat",
                "distance_mpc": 1.0,
                "r_kpc": float(i + 1),
                "v_obs_kms": 90.0 + i,
                "v_err_kms": 2.0,
                "v_gas_kms": 10.0,
                "v_disk_kms": 20.0,
                "v_bulge_kms": 0.0,
                "sb_disk_lpc2": 1.0,
                "sb_bulge_lpc2": 0.0,
                "v_bar_kms": 22.0,
                "residual_v2_kms2": 50.0,
                "quality_flag": "ok",
                "data_source": "SPARC_Lelli2016",
                "data_mode": "observational_raw_ingestion",
            }
            for i in range(12)
        ]
    )
    input_csv = tmp_path / "std.csv"
    df.to_csv(input_csv, index=False)

    cfg = SubsetSelectionConfig(
        input_csv=str(input_csv),
        output_subset_csv=str(tmp_path / "subset.csv"),
        output_report_md=str(tmp_path / "report.md"),
        candidate_galaxies=["CAND1"],
        min_radial_points=12,
        min_radial_coverage_kpc=5.0,
        max_selected_galaxies=1,
    )
    rows, ctx = select_sparc_subset(cfg)
    assert int(rows["selected"].sum()) == 1
    assert rows.loc[rows["selected"], "galaxy_id"].iloc[0] == "CAND1"
    assert ctx["total_selected"] == 1


def test_subset_selection_rejects_low_points(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "galaxy_id": ["BAD"] * 3,
            "source_file": ["BAD_rotmod.dat"] * 3,
            "distance_mpc": [1.0] * 3,
            "r_kpc": [1.0, 2.0, 3.0],
            "v_obs_kms": [20.0, 21.0, 22.0],
            "v_err_kms": [1.0, 1.0, 1.0],
            "v_gas_kms": [5.0, 5.0, 5.0],
            "v_disk_kms": [7.0, 7.0, 7.0],
            "v_bulge_kms": [0.0, 0.0, 0.0],
            "sb_disk_lpc2": [1.0, 1.0, 1.0],
            "sb_bulge_lpc2": [0.0, 0.0, 0.0],
            "v_bar_kms": [8.6, 8.6, 8.6],
            "residual_v2_kms2": [10.0, 12.0, 13.0],
            "quality_flag": ["ok"] * 3,
            "data_source": ["SPARC_Lelli2016"] * 3,
            "data_mode": ["observational_raw_ingestion"] * 3,
        }
    )
    input_csv = tmp_path / "std.csv"
    df.to_csv(input_csv, index=False)

    cfg = SubsetSelectionConfig(
        input_csv=str(input_csv),
        output_subset_csv=str(tmp_path / "subset.csv"),
        output_report_md=str(tmp_path / "report.md"),
        candidate_galaxies=["BAD"],
        min_radial_points=12,
        min_radial_coverage_kpc=5.0,
        max_selected_galaxies=1,
    )
    rows, ctx = select_sparc_subset(cfg)
    assert int(rows["selected"].sum()) == 0
    assert ctx["rejected_candidates"][0]["galaxy_id"] == "BAD"
    assert "n_points<12" in ctx["rejected_candidates"][0]["rejection_reason"]
