from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/phase6d_regularization_preregistration.yaml"


def _load_config() -> dict:
    assert CONFIG.is_file(), "phase6d preregistration config missing"
    with CONFIG.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_jump_threshold_is_0_25() -> None:
    cfg = _load_config()
    assert cfg["option_r2_global_jump_cap"]["threshold_relative_jump"] == 0.25
    assert cfg["smoothness_gate"]["threshold"] == 0.25


def test_max_trim_fraction_exists() -> None:
    cfg = _load_config()
    lim = cfg["option_r6_boundary_trim"]["global_limits"]
    assert lim["max_fraction_points_trimmed"] == 0.10
    assert lim["min_remaining_radial_points"] == 12


def test_no_overwrite_expansion20_paths() -> None:
    cfg = _load_config()
    forbidden = cfg["scope"]["overwrite_forbidden"]
    assert "outputs/tables/expansion20_tau_profiles.csv" in forbidden
    assert "expansion20_tau_profiles.csv" in cfg["scope"]["source_profile_readonly"]


def test_output_paths_are_phase6d_only() -> None:
    cfg = _load_config()
    paths = cfg["future_output_paths"]
    for key in ("profile_template", "audit_template", "map_template", "summary", "report"):
        assert "phase6d" in paths[key]
    assert "expansion20" not in paths["profile_template"]


def test_claim_boundary_flags() -> None:
    cfg = _load_config()
    cb = cfg["claim_boundaries"]
    assert cb["claim_no_lensing_confirmation"] is True
    assert cb["claim_no_true_2d_sigma_b"] is True
    assert cb["claim_not_successful_second_channel"] is True
    assert cb["claim_phase5_headline_unchanged"] is True


def test_phase6d_blocked_until_gates() -> None:
    cfg = _load_config()
    assert cfg["phase6d_readiness"]["blocked_until_all_gates_pass"] is True
