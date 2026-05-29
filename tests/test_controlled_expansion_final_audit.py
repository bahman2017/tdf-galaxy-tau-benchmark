from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.controlled_expansion_audit import (
    FINAL_EXPANSION_20_CLAIM,
    FINAL_CAVEATS,
    build_expansion_comparison_summary,
    build_final_expansion_claims_table,
    run_controlled_expansion_final_audit,
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_final_claim_text() -> None:
    assert "15 of 20" in FINAL_EXPANSION_20_CLAIM
    assert "sensitivity-recovery" in FINAL_EXPANSION_20_CLAIM
    assert "NGC7814" in FINAL_EXPANSION_20_CLAIM
    assert "UGC00128" in FINAL_EXPANSION_20_CLAIM


def test_c20_claims_table() -> None:
    claims = build_final_expansion_claims_table()
    ids = set(claims["claim_id"].astype(str))
    for cid in ("C20-A", "C20-B", "C20-C", "C20-D", "C20-E", "C20-F", "C20-G", "C20-H"):
        assert cid in ids
    prohibited = claims[claims["claim_id"] == "C20-F"].iloc[0]
    assert prohibited["status"] == "prohibited"


def test_comparison_counts(root: Path | None = None) -> None:
    root = root or _root()
    e12_path = root / "outputs/tables/expansion12_failure_mode_summary.csv"
    e20_path = root / "outputs/tables/expansion20_failure_mode_summary.csv"
    if not e12_path.is_file() or not e20_path.is_file():
        pytest.skip("expansion summaries missing")
    e12 = pd.read_csv(e12_path)
    e20 = pd.read_csv(e20_path)
    comp = build_expansion_comparison_summary(e12, e20)

    def val(metric: str) -> int:
        row = comp[comp["metric"] == metric].iloc[0]
        return int(row["expansion_20"])

    assert val("cohort_size") == 20
    assert val("robust_tdf_success") == 15
    assert val("sensitivity_recovery") == 3
    assert val("tdf_failure_mode") == 1
    assert val("mixed_result") == 1
    assert val("tdf_3knot_beats_nfw_holdout") == 15
    assert val("tdf_3knot_beats_mond_holdout") == 17  # can exceed robust (requires both NFW and MOND)


def test_run_audit(root: Path | None = None) -> None:
    root = root or _root()
    if not (root / "outputs/tables/expansion20_failure_mode_summary.csv").is_file():
        pytest.skip("expansion20 outputs missing")
    result = run_controlled_expansion_final_audit(
        comparison_out=root / "outputs/tables/controlled_expansion_comparison_summary.csv",
        claims_out=root / "outputs/tables/controlled_expansion_final_claims.csv",
        report_out=root / "outputs/reports/controlled_expansion20_final_audit_report.md",
    )
    assert len(result["comparison"]) >= 7
    assert len(result["claims"]) >= 8
    report = (root / "outputs/reports/controlled_expansion20_final_audit_report.md").read_text()
    assert FINAL_EXPANSION_20_CLAIM in report
    assert "does not disprove dark matter" in report.lower()


def test_build_script() -> None:
    root = _root()
    if not (root / "outputs/tables/expansion20_failure_mode_summary.csv").is_file():
        pytest.skip("expansion20 outputs missing")
    subprocess.run(
        ["python3", "scripts/build_controlled_expansion_final_audit.py"],
        cwd=root,
        check=True,
    )
    assert (root / "outputs/tables/controlled_expansion_comparison_summary.csv").is_file()


def test_caveats() -> None:
    text = " ".join(FINAL_CAVEATS).lower()
    assert "full-sparc" in text or "full sparc" in text
    assert "lensing" in text
    assert "tdf_5knot" in text
