import numpy as np
import pytest

from tdf_galaxy_tau.models.burkert import BurkertParams, burkert_params_from_log10, burkert_velocity
from tdf_galaxy_tau.models.nfw import NFWParams, nfw_params_from_log10, nfw_velocity


def test_halo_velocities_non_negative() -> None:
    r = np.array([0.1, 1.0, 5.0])
    v_nfw = nfw_velocity(r, NFWParams(rho_s=1e7, r_s=5.0))
    v_burkert = burkert_velocity(r, BurkertParams(rho0=1e7, r0=3.0))
    assert (v_nfw >= 0).all()
    assert (v_burkert >= 0).all()


def test_log_parameter_helpers_match_physical() -> None:
    p = nfw_params_from_log10(6.0, 1.0)
    assert p.rho_s == 1e6 and p.r_s == 10.0
    b = burkert_params_from_log10(4.0, 0.5)
    assert b.rho0 == 1e4 and b.r0 == 10 ** 0.5


def test_halo_velocity_rejects_non_positive_radius() -> None:
    with pytest.raises(ValueError, match="radius must be strictly positive"):
        _ = nfw_velocity(np.array([0.0, 1.0]), NFWParams(rho_s=1e7, r_s=5.0))
    with pytest.raises(ValueError, match="radius must be strictly positive"):
        _ = burkert_velocity(np.array([-1.0, 1.0]), BurkertParams(rho0=1e7, r0=3.0))
