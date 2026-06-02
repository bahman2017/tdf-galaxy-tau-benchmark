"""Phase 5G-B: compatibility regression lock for K_g vs legacy K_tau loaders."""

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
from tdf_galaxy_tau.models.tdf_knot import TdfKnotConfig, load_tdf_knot_config
from tdf_galaxy_tau.reconstruction.radial_tau import TauReconstructionConfig, load_reconstruction_config

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "notation"

EQUIVALENT_DICT_PAIRS: list[tuple[dict, dict, float]] = [
    ({"k_g": 1.0}, {"k_tau": 1.0}, 1.0),
    ({"K_g": 0.75}, {"K_tau": 0.75}, 0.75),
    ({"k_g": 2.0}, {"k_tau": 2.0}, 2.0),
]


@pytest.fixture
def root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("preferred,legacy,expected", EQUIVALENT_DICT_PAIRS)
def test_normalize_equivalent_dict_pairs(preferred: dict, legacy: dict, expected: float) -> None:
    out_kg = normalize_projection_coefficient(preferred)
    out_kt = normalize_projection_coefficient(legacy)
    assert out_kg["k_g"] == pytest.approx(expected)
    assert out_kt["k_g"] == pytest.approx(expected)
    assert out_kg["k_g"] == pytest.approx(out_kt["k_g"])
    assert out_kg["k_tau"] == pytest.approx(out_kt["k_tau"])


@pytest.mark.parametrize("preferred,legacy,expected", EQUIVALENT_DICT_PAIRS)
def test_merge_yaml_blocks_split_notation(preferred: dict, legacy: dict, expected: float) -> None:
    """One block uses k_g; a later block may repeat legacy k_tau at the same value."""
    merged = merge_projection_from_yaml_blocks(legacy, preferred)
    assert merged["k_g"] == pytest.approx(expected)
    assert merged["alias_status"] in {
        ALIAS_STATUS_PREFERRED_K_G,
        ALIAS_STATUS_LEGACY_K_TAU,
        ALIAS_STATUS_BOTH_EQUAL,
    }


def test_merge_k_g_from_later_block_without_prior_projection_key() -> None:
    out = merge_projection_from_yaml_blocks(
        {"negative_residual_policy": "allow_signed"},
        {"k_g": 1.75},
    )
    assert out["k_g"] == pytest.approx(1.75)
    assert out["alias_status"] == ALIAS_STATUS_PREFERRED_K_G


def test_merge_legacy_k_tau_maps_to_k_g() -> None:
    out = merge_projection_from_yaml_blocks({"other_key": "x"}, {"K_tau": 0.5})
    assert out["k_g"] == pytest.approx(0.5)
    assert out["legacy_projection_alias"] is True


def test_merge_conflicting_blocks_raise() -> None:
    with pytest.raises(ValueError, match="Conflicting projection coefficients"):
        merge_projection_from_yaml_blocks({"k_tau": 1.0}, {"k_g": 2.0})


def test_merge_kappa_tau_never_maps_to_projection() -> None:
    with pytest.raises(ValueError, match="kappa_tau is dynamical field stiffness"):
        merge_projection_from_yaml_blocks({"kappa_tau": 1.0})


def test_merge_kappa_tau_ignored_with_valid_legacy_key() -> None:
    out = merge_projection_from_yaml_blocks({"kappa_tau": 99.0, "k_tau": 1.0})
    assert out["k_g"] == pytest.approx(1.0)


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def test_fixture_loaders_equivalent_k_g_and_legacy_k_tau() -> None:
    kg_path = FIXTURES / "reconstruction_k_g.yaml"
    kt_path = FIXTURES / "reconstruction_k_tau_legacy.yaml"
    kg_tau = load_reconstruction_config(kg_path)
    kt_tau = load_reconstruction_config(kt_path)
    kg_raw = _load_yaml(kg_path)
    kt_raw = _load_yaml(kt_path)
    kg_knot = load_tdf_knot_config(kg_raw)
    kt_knot = load_tdf_knot_config(kt_raw)
    assert kg_tau.k_g == pytest.approx(kt_tau.k_g)
    assert kg_tau.k_tau == pytest.approx(kt_tau.k_tau)
    assert kg_knot.k_g == pytest.approx(kt_knot.k_g)
    assert kg_knot.k_tau == pytest.approx(kt_knot.k_tau)
    assert kg_tau.k_g == pytest.approx(1.25)


def test_reconstruction_config_fields_match_except_alias_metadata(
    tmp_path: Path,
) -> None:
    """Equivalent notation yields identical effective loader numeric coefficient."""
    kg_file = tmp_path / "kg.yaml"
    kt_file = tmp_path / "kt.yaml"
    kg_file.write_text(
        yaml.dump({"radial_tau_reconstruction": {"k_g": 1.1, "negative_residual_policy": "allow_signed"}}),
        encoding="utf-8",
    )
    kt_file.write_text(
        yaml.dump({"radial_tau_reconstruction": {"k_tau": 1.1, "negative_residual_policy": "allow_signed"}}),
        encoding="utf-8",
    )
    kg_cfg: TauReconstructionConfig = load_reconstruction_config(kg_file)
    kt_cfg: TauReconstructionConfig = load_reconstruction_config(kt_file)
    assert kg_cfg.k_g == pytest.approx(kt_cfg.k_g)
    assert kg_cfg.k_tau == pytest.approx(kt_cfg.k_tau)
    assert kg_cfg.negative_residual_policy == kt_cfg.negative_residual_policy


def test_tdf_knot_config_equivalent_notation(tmp_path: Path) -> None:
    kg_raw = {"tdf_knot": {"k_g": 1.3}, "radial_tau_reconstruction": {"k_g": 1.3}}
    kt_raw = {"tdf_knot": {"K_tau": 1.3}, "k_tau": 1.3}
    kg_cfg: TdfKnotConfig = load_tdf_knot_config(kg_raw)
    kt_cfg: TdfKnotConfig = load_tdf_knot_config(kt_raw)
    assert kg_cfg.k_g == pytest.approx(kt_cfg.k_g)
    assert kg_cfg.k_tau == pytest.approx(kt_cfg.k_tau)
    assert kg_cfg.amplitude_bound_safety_factor == pytest.approx(kt_cfg.amplitude_bound_safety_factor)


def test_production_legacy_config_matches_k_g_fixture_coefficient(root: Path) -> None:
    prod = load_reconstruction_config(root / "configs/reconstruction.yaml")
    legacy_fixture = load_reconstruction_config(FIXTURES / "reconstruction_k_tau_legacy.yaml")
    assert prod.k_g == pytest.approx(1.0)
    assert legacy_fixture.k_g == pytest.approx(1.25)
    assert prod.k_tau == prod.k_g
    prod_raw = _load_yaml(root / "configs/reconstruction.yaml")
    prod_knot = load_tdf_knot_config(prod_raw)
    assert prod_knot.k_g == pytest.approx(1.0)
    assert prod_knot.k_tau == prod_knot.k_g
