"""Phase 5G-C-B: internal k_g rename with legacy k_tau property and keyword aliases."""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from tdf_galaxy_tau.config.notation import resolve_projection_coefficient_kwarg
from tdf_galaxy_tau.models.tdf_knot import (
    TdfKnotConfig,
    load_tdf_knot_config,
    tdf_velocity_kms,
    tdf_velocity_squared_kms2,
)
from tdf_galaxy_tau.reconstruction.radial_tau import (
    TauReconstructionConfig,
    load_reconstruction_config,
    reconstruct_radial_tau_profile,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "notation"


def test_tau_reconstruction_config_k_g_primary_and_k_tau_alias() -> None:
    cfg = TauReconstructionConfig(k_g=1.25)
    assert cfg.k_g == pytest.approx(1.25)
    assert cfg.k_tau == pytest.approx(1.25)


def test_tdf_knot_config_k_g_primary_and_k_tau_alias() -> None:
    cfg = TdfKnotConfig(k_g=0.75)
    assert cfg.k_g == pytest.approx(0.75)
    assert cfg.k_tau == pytest.approx(0.75)


def test_legacy_fixture_loaders_set_k_g_and_k_tau_alias() -> None:
    kg_path = FIXTURES / "reconstruction_k_g.yaml"
    kt_path = FIXTURES / "reconstruction_k_tau_legacy.yaml"
    kg_tau = load_reconstruction_config(kg_path)
    kt_tau = load_reconstruction_config(kt_path)
    assert kg_tau.k_g == pytest.approx(1.25)
    assert kt_tau.k_g == pytest.approx(1.25)
    assert kg_tau.k_tau == kg_tau.k_g
    assert kt_tau.k_tau == kt_tau.k_g


def test_knot_config_loaders_set_k_g_from_fixtures() -> None:
    kg_raw = yaml.safe_load((FIXTURES / "reconstruction_k_g.yaml").read_text(encoding="utf-8"))
    kt_raw = yaml.safe_load((FIXTURES / "reconstruction_k_tau_legacy.yaml").read_text(encoding="utf-8"))
    kg_cfg = load_tdf_knot_config(kg_raw)
    kt_cfg = load_tdf_knot_config(kt_raw)
    assert kg_cfg.k_g == pytest.approx(1.25)
    assert kt_cfg.k_g == pytest.approx(1.25)
    assert kg_cfg.k_tau == kg_cfg.k_g


def test_tdf_velocity_accepts_k_g() -> None:
    r = np.array([1.0, 2.0, 3.0])
    v_bar = np.array([10.0, 20.0, 30.0])
    knot_r = np.array([1.0, 3.0])
    knot_a = np.array([1.0, 2.0])
    v2_kg = tdf_velocity_squared_kms2(r, v_bar, knot_r, knot_a, k_g=1.0)
    v_kg, _ = tdf_velocity_kms(r, v_bar, knot_r, knot_a, k_g=1.0)
    assert np.all(np.isfinite(v2_kg))
    assert np.all(np.isfinite(v_kg))


def test_tdf_velocity_deprecated_k_tau_kwarg() -> None:
    r = np.array([1.0, 2.0, 3.0])
    v_bar = np.array([10.0, 20.0, 30.0])
    knot_r = np.array([1.0, 3.0])
    knot_a = np.array([1.0, 2.0])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        v2_kt = tdf_velocity_squared_kms2(r, v_bar, knot_r, knot_a, k_tau=1.0)
        v2_kg = tdf_velocity_squared_kms2(r, v_bar, knot_r, knot_a, k_g=1.0)
    assert any(isinstance(w.message, DeprecationWarning) for w in caught)
    assert v2_kt == pytest.approx(v2_kg)


def test_conflicting_k_g_and_k_tau_raises() -> None:
    with pytest.raises(ValueError, match="Conflicting projection coefficients"):
        resolve_projection_coefficient_kwarg(k_g=1.0, k_tau=2.0)
    with pytest.raises(ValueError, match="Conflicting projection coefficients"):
        tdf_velocity_squared_kms2(
            np.array([1.0]),
            np.array([10.0]),
            np.array([1.0]),
            np.array([1.0]),
            k_g=1.0,
            k_tau=2.0,
        )


def test_equal_k_g_and_k_tau_accepts_k_g() -> None:
    assert resolve_projection_coefficient_kwarg(k_g=1.5, k_tau=1.5) == pytest.approx(1.5)


def test_csv_writer_emits_k_tau_column_from_k_g() -> None:
    frame = pd.DataFrame(
        {
            "r_kpc": [0.5, 1.0, 2.0],
            "v_obs_kms": [80.0, 85.0, 90.0],
            "v_bar_kms": [70.0, 90.0, 80.0],
            "v_err_kms": [2.0, 2.0, 2.0],
        }
    )
    out = reconstruct_radial_tau_profile(frame, "G1", TauReconstructionConfig(k_g=1.75))
    assert "K_tau" in out.columns
    assert np.allclose(out["K_tau"].to_numpy(), 1.75)
