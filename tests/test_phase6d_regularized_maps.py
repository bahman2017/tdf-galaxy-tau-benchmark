from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from tdf_galaxy_tau.analysis.phase6c_frozen_pseudo2d import PRIMARY_PILOT_GALAXY_IDS
from tdf_galaxy_tau.analysis.phase6d_regularized_maps import (
    DEFAULT_CONFIG,
    apply_r2_r6_regularization,
    build_regularized_pseudo2d_map,
    load_preregistration_config,
    run_phase6d_regularized_maps,
)

ROOT = Path(__file__).resolve().parents[1]
EXPANSION20 = ROOT / "outputs/tables/expansion20_tau_profiles.csv"
SUMMARY = ROOT / "outputs/tables/phase6d_regularized_map_summary.csv"
COHORT_REPORT = ROOT / "outputs/reports/phase6d_regularization_cohort_report.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _minimal_cfg(threshold: float = 0.25) -> dict:
    with (ROOT / DEFAULT_CONFIG).open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["option_r2_global_jump_cap"]["threshold_relative_jump"] = threshold
    return cfg


def test_r2_threshold_from_yaml() -> None:
    cfg = load_preregistration_config(ROOT / DEFAULT_CONFIG)
    assert cfg["option_r2_global_jump_cap"]["threshold_relative_jump"] == 0.25


def test_r2_fails_when_more_than_40_percent_capped() -> None:
    cfg = _minimal_cfg()
    n = 10
    r = np.linspace(1.0, 10.0, n)
    dtaudr = np.ones(n) * 1.0
    dtaudr[1:] = 100.0
    frozen = pd.DataFrame(
        {
            "galaxy_id": ["SYN"] * n,
            "r_kpc": r,
            "tau_reconstructed": np.linspace(0.0, 1.0, n),
            "dtaudr_reconstructed": dtaudr,
        }
    )
    _, _, status = apply_r2_r6_regularization(frozen, cfg, galaxy_id="SYN")
    assert status["fraction_segments_capped"] > 0.40
    assert status["r2_fail"] is True


def test_r6_fails_when_trim_fraction_exceeds_10_percent() -> None:
    cfg = _minimal_cfg()
    cfg["option_r6_boundary_trim"]["global_limits"]["fail_if_fraction_points_trimmed_exceeds"] = 0.10
    cfg["option_r6_boundary_trim"]["global_limits"]["min_remaining_radial_points"] = 2
    cfg["option_r6_boundary_trim"]["global_limits"]["min_remaining_radial_coverage_kpc"] = 0.1
    n = 5
    r = np.linspace(1.0, 5.0, n)
    frozen = pd.DataFrame(
        {
            "galaxy_id": ["SYN"] * n,
            "r_kpc": r,
            "tau_reconstructed": np.zeros(n),
            "dtaudr_reconstructed": np.array([1.0, 100.0, 1.0, 100.0, 1.0]),
        }
    )
    _, _, status = apply_r2_r6_regularization(
        frozen, cfg, galaxy_id="SYN", worst_jump_region="outer_third"
    )
    assert status["n_points_trimmed"] >= 1
    if status["fraction_points_trimmed"] > 0.10:
        assert status["r6_fail"] is True


def test_expansion20_not_modified_by_regularization_run() -> None:
    if not EXPANSION20.is_file():
        pytest.skip("expansion20_tau_profiles.csv missing")
    before = _sha256(EXPANSION20)
    mtime_before = EXPANSION20.stat().st_mtime
    run_phase6d_regularized_maps(root=ROOT, write_figures=False)
    assert _sha256(EXPANSION20) == before
    assert EXPANSION20.stat().st_mtime == mtime_before


def test_outputs_only_under_phase6d_paths() -> None:
    if not SUMMARY.is_file():
        pytest.skip("phase6d summary not built")
    for gid in PRIMARY_PILOT_GALAXY_IDS:
        assert (ROOT / f"outputs/tables/phase6d_{gid}_regularized_profile.csv").is_file()
        assert (ROOT / f"outputs/tables/phase6d_{gid}_correction_audit.csv").is_file()
        assert (ROOT / f"outputs/tables/phase6d_{gid}_regularized_map_metadata.csv").is_file()
        assert (ROOT / f"outputs/maps/phase6d/{gid}_regularized_pseudo2d_tau_map.npz").is_file()
        prof = ROOT / f"outputs/tables/phase6d_{gid}_regularized_profile.csv"
        assert "expansion20" not in prof.name


@pytest.mark.parametrize("galaxy_id", PRIMARY_PILOT_GALAXY_IDS)
def test_metadata_claim_flags(galaxy_id: str) -> None:
    meta_path = ROOT / f"outputs/tables/phase6d_{galaxy_id}_regularized_map_metadata.csv"
    if not meta_path.is_file():
        pytest.skip("phase6d outputs not built")
    meta = pd.read_csv(meta_path).iloc[0]
    assert not bool(meta["tau_retuned"])
    assert not bool(meta["kg_retuned"])
    assert not bool(meta["lensing_confirmed"])
    assert not bool(meta["true_2d_sigma_b"])
    assert float(meta["K_g"]) == 1.0


def test_summary_has_five_rows() -> None:
    if not SUMMARY.is_file():
        pytest.skip("phase6d summary missing")
    summary = pd.read_csv(SUMMARY)
    assert len(summary) == 5
    assert set(summary["galaxy_id"]) == set(PRIMARY_PILOT_GALAXY_IDS)


def test_phase6d_candidate_only_when_all_hard_gates_pass() -> None:
    if not SUMMARY.is_file():
        pytest.skip("phase6d summary missing")
    summary = pd.read_csv(SUMMARY)
    for _, row in summary.iterrows():
        hard = (
            row["radial_consistency_pass"]
            and row["smoothness_pass"]
            and row["r2_gate_pass"]
            and row["r6_gate_pass"]
            and row["fidelity_pass"]
        )
        assert bool(row["phase6d_candidate"]) == bool(hard)


def test_cohort_report_blocked_when_zero_pass() -> None:
    if not COHORT_REPORT.is_file() or not SUMMARY.is_file():
        pytest.skip("cohort outputs missing")
    summary = pd.read_csv(SUMMARY)
    text = COHORT_REPORT.read_text(encoding="utf-8")
    if int(summary["phase6d_candidate"].sum()) == 0:
        assert "Phase 6D remains blocked" in text
        assert "0/5" in text


def test_build_single_galaxy_ddo161() -> None:
    if not EXPANSION20.is_file():
        pytest.skip("expansion20 missing")
    res = build_regularized_pseudo2d_map("DDO161", root=ROOT)
    assert res.galaxy_id == "DDO161"
    assert "tau_frozen" in res.regularized_profile.columns
    assert len(res.correction_audit) >= 1
