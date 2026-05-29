from __future__ import annotations

import numpy as np

from tdf_galaxy_tau.models.mond import (
    A0_DEFAULT_MS2,
    KPC_TO_M,
    KMS_TO_MS,
    acceleration_to_velocity_kms,
    baryonic_acceleration_ms2,
    kpc_to_meters,
    kms_to_ms,
    log10_a0_to_a0,
    mond_fixed_a0_velocity_kms,
    mond_observed_acceleration_simple,
    ms_to_kms,
    rar_observed_acceleration,
    simple_mond_nu,
)


def test_unit_conversion_kpc_kms_roundtrip() -> None:
    r_kpc = np.array([1.0, 5.0])
    v_kms = np.array([50.0, 100.0])
    r_m = kpc_to_meters(r_kpc)
    v_ms = kms_to_ms(v_kms)
    assert np.allclose(r_m / KPC_TO_M, r_kpc)
    assert np.allclose(ms_to_kms(v_ms), v_kms)


def test_mond_acceleration_non_negative_finite() -> None:
    g_bar = np.array([1e-12, 1e-10, 1e-8, 1e-6])
    g_obs = mond_observed_acceleration_simple(g_bar, A0_DEFAULT_MS2)
    assert np.all(np.isfinite(g_obs))
    assert np.all(g_obs >= 0)


def test_simple_nu_finite_for_small_y() -> None:
    y = np.array([1e-6, 0.1, 1.0, 10.0])
    nu = simple_mond_nu(y)
    assert np.all(np.isfinite(nu))
    assert np.all(nu > 0)


def test_velocity_from_acceleration_si() -> None:
    r_kpc = np.array([1.0, 3.0])
    v_bar = np.array([30.0, 60.0])
    v_model = mond_fixed_a0_velocity_kms(r_kpc, v_bar, a0_ms2=A0_DEFAULT_MS2)
    assert np.all(np.isfinite(v_model))
    assert np.all(v_model >= 0)


def test_log10_a0_positive() -> None:
    assert log10_a0_to_a0(-10.0) == 1e-10


def test_rar_acceleration_non_negative() -> None:
    g_bar = np.array([0.0, 1e-11, 1e-9])
    g_obs = rar_observed_acceleration(g_bar, A0_DEFAULT_MS2)
    assert np.all(np.isfinite(g_obs))
    assert np.all(g_obs >= 0)


def test_baryonic_acceleration_formula() -> None:
    r_kpc = np.array([2.0])
    v_kms = np.array([100.0])
    g = baryonic_acceleration_ms2(r_kpc, v_kms)
    expected = (kms_to_ms(v_kms)[0] ** 2) / kpc_to_meters(r_kpc)[0]
    assert np.isclose(g[0], expected)
