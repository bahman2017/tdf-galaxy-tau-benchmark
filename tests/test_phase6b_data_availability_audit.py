from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.phase6b_data_availability import (
    CLAIM_BOUNDARY_FIELDS,
    N_COHORT,
    build_phase6b_audit_table,
    build_phase6b_ranking_table,
    run_phase6b_audit,
)

AUDIT_CSV = Path("outputs/tables/phase6b_expansion20_data_availability_audit.csv")
RANKING_CSV = Path("outputs/tables/phase6b_pilot_candidate_ranking.csv")
REPORT_MD = Path("outputs/reports/phase6b_pilot_selection_report.md")

REQUIRED_AUDIT_COLUMNS = [
    "galaxy_id",
    "l1_rotation_available",
    "l2_baryonic_available",
    "l3_frozen_tdf_available",
    "l4_geometry_available",
    "true_2d_status",
    "lensing_status",
    "failure_mode_classification",
    "primary_pilot_eligible",
    "pilot_tier",
    "is_primary_pilot",
    "claim_no_dm_disproof",
    "claim_no_lensing_confirmation",
]


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def audit_table() -> pd.DataFrame:
    root = _root()
    if not (root / "outputs/tables/expansion20_subset_selection.csv").is_file():
        pytest.skip("expansion_20 tables missing")
    return build_phase6b_audit_table(root)


def test_audit_csv_exists_and_row_count() -> None:
    root = _root()
    if not AUDIT_CSV.is_file():
        run_phase6b_audit(root=root)
    audit = pd.read_csv(root / AUDIT_CSV)
    assert len(audit) == N_COHORT
    assert set(audit["galaxy_id"].astype(str)) == set(
        pd.read_csv(root / "outputs/tables/expansion20_subset_selection.csv")[
            "galaxy_id"
        ].astype(str)
    )


def test_required_columns(audit_table: pd.DataFrame) -> None:
    for col in REQUIRED_AUDIT_COLUMNS:
        assert col in audit_table.columns, f"missing column {col}"


def test_ngc7814_not_primary_pilot(audit_table: pd.DataFrame) -> None:
    row = audit_table[audit_table["galaxy_id"] == "NGC7814"].iloc[0]
    assert not bool(row["is_primary_pilot"])
    assert row["pilot_tier"] == "tier_3_avoid_defer"
    assert not bool(row["primary_pilot_eligible"])


def test_ugc00128_not_primary_pilot(audit_table: pd.DataFrame) -> None:
    row = audit_table[audit_table["galaxy_id"] == "UGC00128"].iloc[0]
    assert not bool(row["is_primary_pilot"])
    assert row["pilot_tier"] == "tier_2_diagnostic"
    assert not bool(row["primary_pilot_eligible"])


def test_primary_pilots_are_robust_tdf_3knot(audit_table: pd.DataFrame) -> None:
    prim = audit_table[audit_table["is_primary_pilot"]]
    assert len(prim) >= 1
    for _, row in prim.iterrows():
        assert row["failure_mode_classification"] == "robust_tdf_success"
        assert bool(row["counts_as_primary_success_expansion20"])
        assert bool(row["holdout_stable_for_primary_pilot"])


def test_primary_pilots_have_geometry(audit_table: pd.DataFrame) -> None:
    prim = audit_table[audit_table["is_primary_pilot"]]
    for _, row in prim.iterrows():
        assert bool(row["geometry_complete_flag"])
        assert bool(row["l4_geometry_available"])


def test_true_2d_not_available(audit_table: pd.DataFrame) -> None:
    assert (audit_table["true_2d_pixel_map_available"] == False).all()  # noqa: E712
    assert (audit_table["true_2d_status"] == "future_only").all()
    assert (audit_table["map_type_true_2d_sigma_b"] == "future_only").all()


def test_lensing_not_confirmed(audit_table: pd.DataFrame) -> None:
    assert (audit_table["lensing_status"] == "future_only_not_confirmed").all()
    assert (audit_table["l6_second_channel_lensing_data"] == False).all()  # noqa: E712
    assert bool(audit_table["claim_no_lensing_confirmation"].all())


def test_claim_boundary_fields(audit_table: pd.DataFrame) -> None:
    for field, expected in CLAIM_BOUNDARY_FIELDS.items():
        assert field in audit_table.columns
        assert (audit_table[field] == expected).all()


def test_ranking_table() -> None:
    root = _root()
    audit = build_phase6b_audit_table(root)
    ranking = build_phase6b_ranking_table(audit)
    assert len(ranking) == N_COHORT
    assert ranking["overall_rank"].is_unique
    primary = ranking[ranking["is_primary_pilot"]]
    assert "NGC7814" not in set(primary["galaxy_id"].astype(str))
    assert "UGC00128" not in set(primary["galaxy_id"].astype(str))


def test_build_script_idempotent() -> None:
    root = _root()
    result = run_phase6b_audit(root=root)
    assert (root / REPORT_MD).is_file()
    assert len(result["audit"]) == N_COHORT
