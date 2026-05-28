from __future__ import annotations

from dataclasses import dataclass

import numpy as np

G_KPC = 4.30091e-6
_R_EPS = 1.0e-8


@dataclass(frozen=True)
class BurkertParams:
    rho0: float
    r0: float


def burkert_mass_enclosed(radius: np.ndarray, params: BurkertParams) -> np.ndarray:
    r = np.asarray(radius, dtype=float)
    x = np.maximum(r / params.r0, 0.0)
    inner = np.log1p(x) + np.arctan(x) - 0.5 * np.log1p(x**2)
    return 4.0 * np.pi * params.rho0 * params.r0**3 * inner


def burkert_velocity(radius: np.ndarray, params: BurkertParams) -> np.ndarray:
    r = np.maximum(np.asarray(radius, dtype=float), _R_EPS)
    mass = burkert_mass_enclosed(r, params)
    return np.sqrt(np.maximum(G_KPC * mass / r, 0.0))
