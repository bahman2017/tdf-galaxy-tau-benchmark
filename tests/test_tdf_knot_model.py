from __future__ import annotations

import numpy as np
import pytest

from tdf_galaxy_tau.metrics.information_criteria import model_parameter_count
from tdf_galaxy_tau.models.fitting import fit_tdf_knot_baseline
from tdf_galaxy_tau.models.tdf_knot import (
    fixed_knot_radii_kpc,
    interpolate_dtaudr_at_radii,
    n_knots_for_model,
    tdf_velocity_kms,
)


def test_knot_radii_sorted_and_fixed_count() -> None:
    r = np.array([0.5, 1.0, 2.0, 5.0, 8.0])
    k3 = fixed_knot_radii_kpc(r, 3)
    assert len(k3) == 3
    assert np.all(np.diff(k3) >= 0)
    assert k3[0] == pytest.approx(0.5)
    assert k3[-1] == pytest.approx(8.0)


def test_n_parameters_equals_knot_count() -> None:
    assert model_parameter_count("tdf_3knot") == 3
    assert model_parameter_count("tdf_4knot") == 4
    assert model_parameter_count("tdf_5knot") == 5
    assert n_knots_for_model("tdf_3knot") == 3


def test_tdf_velocity_finite_for_valid_parameters() -> None:
    r = np.linspace(0.5, 10.0, 20)
    v_bar = np.linspace(15.0, 90.0, 20)
    knot_r = fixed_knot_radii_kpc(r, 3)
    knot_a = np.array([100.0, 200.0, 150.0])
    v, v2 = tdf_velocity_kms(r, v_bar, knot_r, knot_a, k_tau=1.0)
    assert np.all(np.isfinite(v))
    assert np.all(v >= 0)


def test_non_positive_v2_penalty_does_not_crash() -> None:
    r = np.array([1.0, 2.0, 3.0])
    v_obs = np.array([50.0, 55.0, 60.0])
    v_err = np.array([2.0, 2.0, 2.0])
    v_bar = np.array([40.0, 45.0, 50.0])
    knot_r = fixed_knot_radii_kpc(r, 3)
    # Large negative knot amplitudes can drive v^2 negative
    fit = fit_tdf_knot_baseline(
        r,
        v_obs,
        v_err,
        v_bar,
        model_name="tdf_3knot",
        knot_r_kpc=knot_r,
        initial_knot_dtaudr=np.array([-1e6, -1e6, -1e6]),
        dtaudr_bounds=(-1e7, 1e7),
        k_tau=1.0,
        negative_v2_penalty=500.0,
    )
    assert isinstance(fit.fit_success, bool)


def test_interpolate_dtaudr_linear() -> None:
    knot_r = np.array([1.0, 5.0])
    knot_a = np.array([10.0, 30.0])
    mid = interpolate_dtaudr_at_radii(np.array([3.0]), knot_r, knot_a)
    assert mid[0] == pytest.approx(20.0)


def test_k_tau_not_counted_as_fitted_parameter() -> None:
    assert model_parameter_count("tdf_3knot") == 3
