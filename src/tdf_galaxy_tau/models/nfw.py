from __future__ import annotations

from dataclasses import dataclass

import numpy as np

G_KPC = 4.30091e-6
_R_EPS = 1.0e-8


@dataclass(frozen=True)
class NFWParams:
    """NFW parameters.

    rho_s units: Msun / kpc^3
    r_s units: kpc
    """

    rho_s: float
    r_s: float


def nfw_params_from_log10(log10_rho_s: float, log10_r_s: float) -> NFWParams:
    """Build physical NFW parameters from log10 density and scale radius."""
    return NFWParams(rho_s=float(10.0 ** log10_rho_s), r_s=float(10.0 ** log10_r_s))


def nfw_log10_from_params(params: NFWParams) -> tuple[float, float]:
    return float(np.log10(params.rho_s)), float(np.log10(params.r_s))


def nfw_mass_enclosed(radius: np.ndarray, params: NFWParams) -> np.ndarray:
    if params.rho_s <= 0 or params.r_s <= 0:
        raise ValueError("NFW parameters must be positive")
    r = np.asarray(radius, dtype=float)
    if np.any(r <= 0):
        raise ValueError("radius must be strictly positive")
    x = np.maximum(r / params.r_s, 0.0)
    return 4.0 * np.pi * params.rho_s * params.r_s**3 * (np.log1p(x) - x / (1.0 + x))


def nfw_velocity(radius: np.ndarray, params: NFWParams) -> np.ndarray:
    r = np.asarray(radius, dtype=float)
    if np.any(r <= 0):
        raise ValueError("radius must be strictly positive")
    r = np.maximum(r, _R_EPS)
    mass = nfw_mass_enclosed(r, params)
    return np.sqrt(np.maximum(G_KPC * mass / r, 0.0))
