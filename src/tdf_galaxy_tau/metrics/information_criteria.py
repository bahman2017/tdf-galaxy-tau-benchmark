from __future__ import annotations

import numpy as np


def aic(chi2: float, n_parameters: int, smoothness_penalty: float = 0.0) -> float:
    return float(chi2 + 2.0 * n_parameters + smoothness_penalty)


def bic(chi2: float, n_points: int, n_parameters: int, smoothness_penalty: float = 0.0) -> float:
    n = max(int(n_points), 1)
    return float(chi2 + n_parameters * np.log(n) + smoothness_penalty)


def model_parameter_count(model_name: str) -> int:
    lookup = {"baryonic": 0, "nfw": 2, "burkert": 2, "tdf": 1}
    return lookup.get(model_name.lower(), 0)
