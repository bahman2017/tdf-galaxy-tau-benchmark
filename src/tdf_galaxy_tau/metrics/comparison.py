from __future__ import annotations

import numpy as np


def rmse(v_obs: np.ndarray, v_model: np.ndarray) -> float:
    obs = np.asarray(v_obs, dtype=float)
    model = np.asarray(v_model, dtype=float)
    return float(np.sqrt(np.mean((obs - model) ** 2)))


def chi_square(v_obs: np.ndarray, v_model: np.ndarray, v_err: np.ndarray) -> float:
    obs = np.asarray(v_obs, dtype=float)
    model = np.asarray(v_model, dtype=float)
    err = np.asarray(v_err, dtype=float)
    if np.any(err <= 0):
        raise ValueError("v_err must be positive")
    return float(np.sum(((obs - model) / err) ** 2))


def reduced_chi_square(chi2: float, n_points: int, n_parameters: int) -> float:
    dof = n_points - n_parameters - 1
    if dof <= 0:
        raise ValueError("non-positive degrees of freedom")
    return float(chi2 / dof)
