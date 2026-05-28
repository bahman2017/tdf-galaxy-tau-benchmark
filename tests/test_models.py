import numpy as np

from tdf_galaxy_tau.models.burkert import BurkertParams, burkert_velocity
from tdf_galaxy_tau.models.nfw import NFWParams, nfw_velocity


def test_halo_velocities_non_negative() -> None:
    r = np.array([0.1, 1.0, 5.0])
    v_nfw = nfw_velocity(r, NFWParams(rho_s=1e7, r_s=5.0))
    v_burkert = burkert_velocity(r, BurkertParams(rho0=1e7, r0=3.0))
    assert (v_nfw >= 0).all()
    assert (v_burkert >= 0).all()
