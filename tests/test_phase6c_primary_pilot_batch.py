from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.phase6c_frozen_pseudo2d import (
    PRIMARY_PILOT_GALAXY_IDS,
    REQUIRED_NPZ_KEYS,
    build_primary_pilot_summary_table,
    load_primary_pilot_galaxy_ids,
    run_phase6c_primary_pilot_batch,
)

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "outputs/tables/phase6c_primary_pilot_map_summary.csv"
AUDIT = ROOT / "outputs/reports/phase6c_primary_pilot_smoothness_audit.md"
RANKING = ROOT / "outputs/tables/phase6b_pilot_candidate_ranking.csv"


@pytest.fixture(scope="module")
def primary_summary() -> pd.DataFrame:
    if not SUMMARY.is_file():
        if not (ROOT / "outputs/maps/phase6c/DDO161_frozen_pseudo2d_tau_map.npz").is_file():
            pytest.skip("Phase 6C maps not built")
        run_phase6c_primary_pilot_batch(root=ROOT, build_maps=False)
    return pd.read_csv(SUMMARY)


def test_primary_pilot_list_matches_ranking() -> None:
    if not RANKING.is_file():
        pytest.skip("ranking missing")
    assert load_primary_pilot_galaxy_ids(root=ROOT) == list(PRIMARY_PILOT_GALAXY_IDS)


def test_all_five_maps_exist(primary_summary: pd.DataFrame) -> None:
    assert len(primary_summary) == 5
    for gid in PRIMARY_PILOT_GALAXY_IDS:
        npz = ROOT / f"outputs/maps/phase6c/{gid}_frozen_pseudo2d_tau_map.npz"
        assert npz.is_file(), f"missing map {gid}"
        meta = ROOT / f"outputs/tables/phase6c_{gid}_frozen_pseudo2d_map_metadata.csv"
        assert meta.is_file(), f"missing metadata {gid}"


def test_excluded_galaxies_not_in_summary(primary_summary: pd.DataFrame) -> None:
    ids = set(primary_summary["galaxy_id"].astype(str))
    assert "NGC7814" not in ids
    assert "UGC00128" not in ids


def test_claim_boundary_flags_all_maps(primary_summary: pd.DataFrame) -> None:
    for gid in PRIMARY_PILOT_GALAXY_IDS:
        meta = pd.read_csv(
            ROOT / f"outputs/tables/phase6c_{gid}_frozen_pseudo2d_map_metadata.csv"
        ).iloc[0]
        assert meta["tau_retuned"] in (False, "False")
        assert meta["kg_retuned"] in (False, "False")
        assert meta["lensing_confirmed"] in (False, "False")
        assert meta["true_2d_sigma_b"] in (False, "False")


def test_npz_keys_all_primary_pilots() -> None:
    import numpy as np

    for gid in PRIMARY_PILOT_GALAXY_IDS:
        data = np.load(ROOT / f"outputs/maps/phase6c/{gid}_frozen_pseudo2d_tau_map.npz")
        for key in REQUIRED_NPZ_KEYS:
            assert key in data.files


def test_radial_consistency_computed(primary_summary: pd.DataFrame) -> None:
    assert primary_summary["radial_consistency_max_relative_error"].notna().all()
    for gid in PRIMARY_PILOT_GALAXY_IDS:
        path = ROOT / f"outputs/tables/phase6c_{gid}_radial_consistency_check.csv"
        assert path.is_file()
        assert len(pd.read_csv(path)) >= 1


def test_phase6d_readiness_false_when_smoothness_fails(primary_summary: pd.DataFrame) -> None:
    for _, row in primary_summary.iterrows():
        if not bool(row["smoothness_pass"]):
            assert not bool(row["phase6c_ready_for_second_channel_scaffold"])
            assert str(row["phase6c_not_ready_reason"]).strip() != ""


def test_summary_has_required_columns(primary_summary: pd.DataFrame) -> None:
    for col in (
        "smoothness_failure_inherited_from_frozen_1d_profile",
        "phase6c_ready_for_second_channel_scaffold",
        "smoothness_threshold",
    ):
        assert col in primary_summary.columns


def test_combined_audit_report_exists() -> None:
    assert AUDIT.is_file()
    text = AUDIT.read_text(encoding="utf-8").lower()
    assert "phase 6d" in text
