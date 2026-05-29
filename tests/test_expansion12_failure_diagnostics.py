from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.expansion12_diagnostics import (
    AUDIT_DISCLAIMER,
    FOCUS_GALAXY_IDS,
    build_expansion12_failure_diagnostics,
    compare_ngc5055_vs_ngc7814,
    run_expansion12_diagnostics,
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _inputs_exist(root: Path) -> bool:
    required = [
        root / "outputs/tables/expansion12_failure_mode_summary.csv",
        root / "outputs/tables/expansion12_holdout_validation.csv",
        root / "data/processed/sparc/sparc_rotmod_standardized.csv",
        root / "outputs/tables/expansion12_tau_profiles.csv",
    ]
    return all(p.is_file() for p in required)


def test_audit_disclaimer_text() -> None:
    assert "does not add new fits" in AUDIT_DISCLAIMER.lower()
    assert "does not disprove dark matter" in AUDIT_DISCLAIMER.lower()
    assert "does not include lensing" in AUDIT_DISCLAIMER.lower()


def test_focus_galaxy_count() -> None:
    assert len(FOCUS_GALAXY_IDS) == 4


def test_ngc5055_not_equivalent_to_ngc7814() -> None:
    root = _root()
    if not _inputs_exist(root):
        pytest.skip("Phase 5B outputs missing")
    result = run_expansion12_diagnostics(
        failure_summary_path=root / "outputs/tables/expansion12_failure_mode_summary.csv",
        holdout_path=root / "outputs/tables/expansion12_holdout_validation.csv",
        rotmod_path=root / "data/processed/sparc/sparc_rotmod_standardized.csv",
        tau_path=root / "outputs/tables/expansion12_tau_profiles.csv",
        photometry_path=root / "data/processed/sparc/sparc_photometry_metadata.csv",
        model_comparison_path=root / "outputs/tables/expansion12_model_comparison.csv",
        figures_dir=root / "outputs/figures/sparc_subset",
    )
    cmp = compare_ngc5055_vs_ngc7814(result.failure_diagnostics)
    assert cmp["equivalent_failure"] is False
    assert cmp["ngc7814_tdf_failure_scope"] == "all_tdf_failure"
    assert cmp["ngc5055_tdf_failure_scope"] == "flex_recovery"

    ng5055 = result.failure_diagnostics[
        result.failure_diagnostics["galaxy_id"] == "NGC5055"
    ].iloc[0]
    assert float(ng5055["tdf_5knot_minus_tdf_3knot_holdout_improvement_kms"]) > 100.0
    assert bool(ng5055["tdf_5knot_beats_nfw_holdout"])


def test_mixed_case_subtypes() -> None:
    root = _root()
    if not _inputs_exist(root):
        pytest.skip("Phase 5B outputs missing")
    result = run_expansion12_diagnostics(
        failure_summary_path=root / "outputs/tables/expansion12_failure_mode_summary.csv",
        holdout_path=root / "outputs/tables/expansion12_holdout_validation.csv",
        rotmod_path=root / "data/processed/sparc/sparc_rotmod_standardized.csv",
        tau_path=root / "outputs/tables/expansion12_tau_profiles.csv",
        photometry_path=root / "data/processed/sparc/sparc_photometry_metadata.csv",
        model_comparison_path=root / "outputs/tables/expansion12_model_comparison.csv",
        figures_dir=root / "outputs/figures/sparc_subset",
    )
    diag = result.failure_diagnostics.set_index("galaxy_id")
    assert diag.loc["UGC00128", "mixed_case_subtype"] in (
        "near_tie_mixed_case",
        "baseline_dominated_mixed_case",
    )
    assert diag.loc["UGC05253", "tdf_failure_scope"] == "flex_recovery"


def test_build_diagnostics_four_rows() -> None:
    root = _root()
    if not _inputs_exist(root):
        pytest.skip("Phase 5B outputs missing")
    diag = build_expansion12_failure_diagnostics(
        failure_summary=pd.read_csv(root / "outputs/tables/expansion12_failure_mode_summary.csv"),
        holdout=pd.read_csv(root / "outputs/tables/expansion12_holdout_validation.csv"),
        rotmod=pd.read_csv(root / "data/processed/sparc/sparc_rotmod_standardized.csv"),
        tau_profiles=pd.read_csv(root / "outputs/tables/expansion12_tau_profiles.csv"),
        photometry=pd.read_csv(root / "data/processed/sparc/sparc_photometry_metadata.csv"),
    )
    assert len(diag) == 4
    assert "recommended_interpretation" in diag.columns


def test_analyze_script() -> None:
    root = _root()
    if not _inputs_exist(root):
        pytest.skip("Phase 5B outputs missing")
    subprocess.run(
        ["python3", "scripts/analyze_expansion12_failure_modes.py"],
        cwd=root,
        check=True,
    )
    assert (root / "outputs/tables/expansion12_failure_diagnostics.csv").is_file()
    assert (root / "outputs/tables/expansion12_case_review_summary.csv").is_file()
    report = (root / "outputs/reports/expansion12_failure_mode_analysis_report.md").read_text()
    assert "expansion_12" in report.lower()
    assert "does not disprove dark matter" in report.lower()
    assert (root / "outputs/figures/sparc_subset/expansion12_failure_case_residuals.png").is_file()
    assert (root / "outputs/figures/sparc_subset/expansion12_tdf3_vs_tdf5_gap.png").is_file()
