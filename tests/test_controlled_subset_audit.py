from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.controlled_subset_audit import (
    FINAL_CONTROLLED_SUBSET_CLAIM,
    FINAL_CAVEATS,
    build_final_claims_table,
    build_final_status_table,
    run_controlled_subset_final_audit,
)


def test_final_claim_text() -> None:
    assert "NGC7814" in FINAL_CONTROLLED_SUBSET_CLAIM
    assert "tdf_3knot" in FINAL_CONTROLLED_SUBSET_CLAIM
    assert "not a final M/L calibration" in FINAL_CONTROLLED_SUBSET_CLAIM


def test_caveats_include_dm_and_lensing() -> None:
    text = " ".join(FINAL_CAVEATS).lower()
    assert "dark matter" in text
    assert "lensing" in text
    assert "full-sparc" in text or "full sparc" in text


def test_status_table_columns() -> None:
    df = build_final_status_table()
    assert {"phase", "main_output", "status", "supported_claim", "caveat", "next_action"}.issubset(
        df.columns
    )
    assert len(df) >= 20
    assert "4M" in df["phase"].values


def test_claims_table(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    claims = build_final_claims_table(root / "outputs/tables/sparc_claim_traceability_matrix_updated.csv")
    ids = set(claims["claim_id"].astype(str))
    assert "FINAL" in ids
    assert "I" in ids or "claim_id" in claims.columns


def test_build_audit_outputs(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    status, claims = run_controlled_subset_final_audit(
        status_out=root / "outputs/tables/sparc_controlled_subset_final_status.csv",
        claims_out=root / "outputs/tables/sparc_controlled_subset_final_claims.csv",
        report_out=root / "outputs/reports/sparc_controlled_subset_final_audit_report.md",
    )
    assert len(status) >= 20
    assert len(claims) >= 10
    report = (root / "outputs/reports/sparc_controlled_subset_final_audit_report.md").read_text()
    assert "does not disprove dark matter" in report.lower()
    assert FINAL_CONTROLLED_SUBSET_CLAIM in report


def test_build_script(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python3", "scripts/build_controlled_subset_final_audit.py"],
        cwd=root,
        check=True,
        timeout=30,
    )
    assert (root / "outputs/tables/sparc_controlled_subset_final_status.csv").is_file()
