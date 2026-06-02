"""Tests for K_g / legacy K_tau projection coefficient aliases (Phase 5G-A)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tdf_galaxy_tau.config.notation import (
    ALIAS_STATUS_BOTH_EQUAL,
    ALIAS_STATUS_LEGACY_K_TAU,
    ALIAS_STATUS_PREFERRED_K_G,
    merge_projection_from_yaml_blocks,
    normalize_projection_coefficient,
)
from tdf_galaxy_tau.models.tdf_knot import load_tdf_knot_config
from tdf_galaxy_tau.reconstruction.radial_tau import load_reconstruction_config


def test_accepts_new_k_g() -> None:
    out = normalize_projection_coefficient({"k_g": 1.25})
    assert out["k_g"] == pytest.approx(1.25)
    assert out["k_tau"] == pytest.approx(1.25)
    assert out["legacy_projection_alias"] is False
    assert out["alias_status"] == ALIAS_STATUS_PREFERRED_K_G
    assert out["projection_coefficient_source"] == "k_g"


def test_accepts_legacy_k_tau_maps_to_k_g() -> None:
    out = normalize_projection_coefficient({"k_tau": 0.5})
    assert out["k_g"] == pytest.approx(0.5)
    assert out["legacy_projection_alias"] is True
    assert out["alias_status"] == ALIAS_STATUS_LEGACY_K_TAU


def test_accepts_K_tau_capitalization() -> None:
    out = normalize_projection_coefficient({"K_tau": 2.0})
    assert out["k_g"] == pytest.approx(2.0)
    assert out["alias_status"] == ALIAS_STATUS_LEGACY_K_TAU
    assert out["projection_coefficient_source"] == "K_tau"


def test_accepts_K_g_capitalization() -> None:
    out = normalize_projection_coefficient({"K_g": 1.0})
    assert out["k_g"] == pytest.approx(1.0)
    assert out["alias_status"] == ALIAS_STATUS_PREFERRED_K_G


def test_rejects_conflicting_k_g_and_k_tau() -> None:
    with pytest.raises(ValueError, match="Conflicting projection coefficients"):
        normalize_projection_coefficient({"k_g": 1.0, "k_tau": 2.0})


def test_accepts_equal_k_g_and_k_tau() -> None:
    out = normalize_projection_coefficient({"k_g": 1.0, "K_tau": 1.0})
    assert out["k_g"] == pytest.approx(1.0)
    assert out["legacy_projection_alias"] is True
    assert out["alias_status"] == ALIAS_STATUS_BOTH_EQUAL


def test_rejects_kappa_tau_as_projection_coefficient() -> None:
    with pytest.raises(ValueError, match="kappa_tau is dynamical field stiffness"):
        normalize_projection_coefficient({"kappa_tau": 1.0})


def test_kappa_tau_ignored_when_legacy_k_tau_present() -> None:
    out = normalize_projection_coefficient({"kappa_tau": 99.0, "k_tau": 1.0})
    assert out["k_g"] == pytest.approx(1.0)
    assert out["alias_status"] == ALIAS_STATUS_LEGACY_K_TAU


def test_normalized_config_contains_alias_metadata() -> None:
    out = normalize_projection_coefficient({"k_tau": 1.0})
    for key in (
        "k_g",
        "k_tau",
        "K_g",
        "K_tau",
        "projection_coefficient_source",
        "legacy_projection_alias",
        "alias_status",
    ):
        assert key in out


def test_legacy_reconstruction_yaml_still_loads(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    path = root / "configs/reconstruction.yaml"
    cfg = load_reconstruction_config(path)
    assert cfg.k_tau == pytest.approx(1.0)


def test_legacy_tdf_knot_yaml_still_loads(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    raw = yaml.safe_load((root / "configs/reconstruction.yaml").read_text(encoding="utf-8"))
    cfg = load_tdf_knot_config(raw)
    assert cfg.k_tau == pytest.approx(1.0)


def test_new_k_g_yaml_block(tmp_path: Path) -> None:
    cfg_path = tmp_path / "recon.yaml"
    cfg_path.write_text(
        yaml.dump(
            {
                "radial_tau_reconstruction": {"k_g": 1.5, "negative_residual_policy": "allow_signed"},
                "tdf_knot": {"k_g": 1.5},
            }
        ),
        encoding="utf-8",
    )
    tau_cfg = load_reconstruction_config(cfg_path)
    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    knot_cfg = load_tdf_knot_config(raw)
    assert tau_cfg.k_tau == pytest.approx(1.5)
    assert knot_cfg.k_tau == pytest.approx(1.5)


def test_merge_projection_from_yaml_blocks_order() -> None:
    out = merge_projection_from_yaml_blocks({"k_g": 1.0}, {"k_g": 2.0})
    assert out["k_g"] == pytest.approx(2.0)
    assert out["alias_status"] == ALIAS_STATUS_PREFERRED_K_G
