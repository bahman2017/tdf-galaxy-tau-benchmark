from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.phase6b_data_availability import PHASE6C_MAX_DTAUDR_JUMP_REL
from tdf_galaxy_tau.analysis.phase6c_frozen_pseudo2d import PRIMARY_PILOT_GALAXY_IDS
from tdf_galaxy_tau.analysis.phase6c_gradient_diagnostics import (
    DIAGNOSTIC_VERSION,
    build_gradient_diagnostics_table,
    run_phase6c_gradient_diagnostics,
)

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "outputs/tables/phase6c_primary_pilot_gradient_diagnostics.csv"
REPORT = ROOT / "outputs/reports/phase6c_gradient_diagnostic_report.md"
TAU = ROOT / "outputs/tables/expansion20_tau_profiles.csv"
MAP_SUMMARY = ROOT / "outputs/tables/phase6c_primary_pilot_map_summary.csv"


@pytest.fixture(scope="module")
def diagnostics_table() -> pd.DataFrame:
    if not TAU.is_file():
        pytest.skip("tau profiles missing")
    return build_gradient_diagnostics_table(root=ROOT)


def test_five_primary_pilots(diagnostics_table: pd.DataFrame) -> None:
    assert len(diagnostics_table) == 5
    assert set(diagnostics_table["galaxy_id"]) == set(PRIMARY_PILOT_GALAXY_IDS)


def test_no_tau_modification_flag(diagnostics_table: pd.DataFrame) -> None:
    assert (diagnostics_table["tau_or_dtaudr_modified"] == False).all()  # noqa: E712
    assert (diagnostics_table["diagnostic_only"] == True).all()  # noqa: E712


def test_diagnostics_match_map_dtaudr_metric(diagnostics_table: pd.DataFrame) -> None:
    for _, row in diagnostics_table.iterrows():
        assert row["diagnostic_matches_map_dtaudr_metric"] in (True, "True", 1)
        assert np.isclose(
            row["max_rel_dtaudr_jump"],
            row["phase6c_smoothness_dtaudr_jump"],
            rtol=1e-5,
        )


def test_all_fail_smoothness_none_6d_ready(diagnostics_table: pd.DataFrame) -> None:
    assert not diagnostics_table["phase6c_smoothness_pass"].any()
    assert not diagnostics_table["phase6c_ready_for_second_channel"].any()


def test_required_columns(diagnostics_table: pd.DataFrame) -> None:
    for col in (
        "max_rel_dtaudr_jump",
        "n_jumps_above_threshold",
        "worst_jump_r_kpc",
        "primary_failure_cause",
        "jump_failure_dominance",
    ):
        assert col in diagnostics_table.columns


def test_script_outputs_exist() -> None:
    if TABLE.is_file():
        return
    run_phase6c_gradient_diagnostics(root=ROOT)
    assert TABLE.is_file()
    assert REPORT.is_file()


def test_report_claims_not_lensing() -> None:
    if not REPORT.is_file():
        run_phase6c_gradient_diagnostics(root=ROOT)
    text = REPORT.read_text(encoding="utf-8").lower()
    assert "diagnostic only" in text
    assert "6d remains blocked" in text or "6d remain blocked" in text
    assert "not" in text and "lensing" in text


def test_threshold_matches_phase6b(diagnostics_table: pd.DataFrame) -> None:
    assert (diagnostics_table["smoothness_threshold"] == PHASE6C_MAX_DTAUDR_JUMP_REL).all()
