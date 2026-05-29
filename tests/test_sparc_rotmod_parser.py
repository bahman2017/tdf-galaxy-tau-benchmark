from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.data.sparc_rotmod_parser import parse_rotmod_file


def test_parse_rotmod_file_basic(tmp_path: Path) -> None:
    sample = tmp_path / "TEST_rotmod.dat"
    sample.write_text(
        "# Distance = 10.0 Mpc\n"
        "# Rad Vobs errV Vgas Vdisk Vbul SBdisk SBbul\n"
        "1.0 50 2 10 20 5 1 0\n"
        "2.0 60 2 12 22 5 1 0\n",
        encoding="utf-8",
    )
    out = parse_rotmod_file(sample)
    assert len(out) == 2
    assert out.loc[0, "galaxy_id"] == "TEST"
    assert out.loc[0, "distance_mpc"] == 10.0
    assert "v_bar_kms" in out.columns


def test_parse_rotmod_filters_invalid_rows(tmp_path: Path) -> None:
    sample = tmp_path / "BAD_rotmod.dat"
    sample.write_text(
        "# Distance = 8 Mpc\n"
        "1.0 50 2 10 20 5 1 0\n"
        "0.0 40 2 10 20 5 1 0\n"
        "2.0 -1 2 10 20 5 1 0\n",
        encoding="utf-8",
    )
    out = parse_rotmod_file(sample)
    assert len(out) == 1
