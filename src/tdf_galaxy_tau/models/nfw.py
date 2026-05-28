from __future__ import annotations

from dataclasses import dataclass

import numpy as np

G_KPC = 4.30091e-6
_R_EPS = 1.0e-8


@dataclass(frozen=True)
class NFWParams:
    rho_s: float
    r_s: float


def nfw_mass_enclosed(radius: np.ndarray, params: NFWParams) -> np.ndarray:
    r = np.asarray(radius, dtype=float)
    x = np.maximum(r / params.r_s, 0.0)
    return 4.0 * np.pi * params.rho_s * params.r_s**3 * (np.log1p(x) - x / (1.0 + x))


def nfw_velocity(radius: np.ndarray, params: NFWParams) -> np.ndarray:
    r = np.maximum(np.asarray(radius, dtype=float), _R_EPS)
    mass = nfw_mass_enclosed(r, params)
    return np.sqrt(np.maximum(G_KPC * mass / r, 0.0))
