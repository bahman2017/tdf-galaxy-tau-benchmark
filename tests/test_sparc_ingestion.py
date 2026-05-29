from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.data.sparc_loader import ingest_sparc_rotmod_to_csv


def test_ingest_directory_with_failure_and_success(tmp_path: Path) -> None:
    input_dir = tmp_path / "Rotmod_LTG"
    input_dir.mkdir(parents=True)

    good = input_dir / "GOOD_rotmod.dat"
    good.write_text(
        "# Distance = 5 Mpc\n"
        "1.0 30 1 8 12 0 1 0\n"
        "2.0 35 1 9 13 0 1 0\n",
        encoding="utf-8",
    )

    bad = input_dir / "BAD_rotmod.dat"
    bad.write_text("# header\n1.0 20\n", encoding="utf-8")

    out_csv = tmp_path / "processed.csv"
    df, failures, summary = ingest_sparc_rotmod_to_csv(input_dir, out_csv)

    assert out_csv.exists()
    assert len(df) == 2
    assert summary.raw_files_found == 2
    assert summary.galaxies_parsed_successfully == 1
    assert summary.galaxies_failed == 1
    assert len(failures) == 1
