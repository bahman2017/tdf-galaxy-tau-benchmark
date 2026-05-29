from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.expansion20_diagnostics import (
    AUDIT_DISCLAIMER,
    FOCUS_GALAXY_IDS,
    build_expansion20_failure_diagnostics,
    classify_ugc12506_archetype,
    run_expansion20_diagnostics,
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _inputs_exist(root: Path) -> bool:
    required = [
        root / "outputs/tables/expansion20_failure_mode_summary.csv",
        root / "outputs/tables/expansion20_holdout_validation.csv",
        root / "data/processed/sparc/sparc_rotmod_standardized.csv",
        root / "outputs/tables/expansion20_tau_profiles.csv",
    ]
    return all(p.is_file() for p in required)


def test_disclaimer() -> None:
    assert "expansion_20" in AUDIT_DISCLAIMER.lower()
    assert "does not disprove dark matter" in AUDIT_DISCLAIMER.lower()


def test_five_focus_galaxies() -> None:
    assert len(FOCUS_GALAXY_IDS) == 5
    assert "UGC12506" in FOCUS_GALAXY_IDS


def test_ugc12506_archetype_knot_flex() -> None:
    root = _root()
    if not _inputs_exist(root):
        pytest.skip("expansion20 outputs missing")
    result = run_expansion20_diagnostics(
        failure_summary_path=root / "outputs/tables/expansion20_failure_mode_summary.csv",
        holdout_path=root / "outputs/tables/expansion20_holdout_validation.csv",
        rotmod_path=root / "data/processed/sparc/sparc_rotmod_standardized.csv",
        tau_path=root / "outputs/tables/expansion20_tau_profiles.csv",
        photometry_path=root / "data/processed/sparc/sparc_photometry_metadata.csv",
        model_comparison_path=root / "outputs/tables/expansion20_model_comparison.csv",
        figures_dir=root / "outputs/figures/sparc_subset",
    )
    arch = result.ugc12506_archetype
    assert arch["archetype"] == "NGC5055_style_knot_flexibility"
    assert arch["archetype"] != "NGC7814_style_all_tdf_failure"
    assert arch["archetype"] != "UGC00128_style_near_tie"

    u = result.failure_diagnostics[
        result.failure_diagnostics["galaxy_id"] == "UGC12506"
    ].iloc[0]
    assert u["failure_scope"] == "sensitivity_recovery"
    assert bool(u["tdf_5knot_beats_nfw_holdout"])


def test_failure_scopes() -> None:
    root = _root()
    if not _inputs_exist(root):
        pytest.skip("expansion20 outputs missing")
    diag = build_expansion20_failure_diagnostics(
        failure_summary=pd.read_csv(root / "outputs/tables/expansion20_failure_mode_summary.csv"),
        holdout=pd.read_csv(root / "outputs/tables/expansion20_holdout_validation.csv"),
        rotmod=pd.read_csv(root / "data/processed/sparc/sparc_rotmod_standardized.csv"),
        tau_profiles=pd.read_csv(root / "outputs/tables/expansion20_tau_profiles.csv"),
        photometry=pd.read_csv(root / "data/processed/sparc/sparc_photometry_metadata.csv"),
    )
    by_id = diag.set_index("galaxy_id")
    assert by_id.loc["NGC7814", "failure_scope"] == "all_tdf_failure"
    assert by_id.loc["NGC5055", "failure_scope"] == "sensitivity_recovery"
    assert by_id.loc["UGC00128", "failure_scope"] == "mixed_result"
    assert len(diag) == 5


def test_analyze_script() -> None:
    root = _root()
    if not _inputs_exist(root):
        pytest.skip("expansion20 outputs missing")
    subprocess.run(
        ["python3", "scripts/analyze_expansion20_failure_modes.py"],
        cwd=root,
        check=True,
    )
    report = (root / "outputs/reports/expansion20_failure_mode_analysis_report.md").read_text()
    assert "UGC12506" in report
    assert "NGC5055_style_knot_flexibility" in report
    assert (root / "outputs/figures/sparc_subset/expansion20_failure_case_residuals.png").is_file()
    assert (root / "outputs/figures/sparc_subset/expansion20_tdf3_vs_tdf5_gap.png").is_file()
