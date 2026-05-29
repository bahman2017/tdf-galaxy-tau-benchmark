from __future__ import annotations

import numpy as np


def aic(chi2: float, n_parameters: int, smoothness_penalty: float = 0.0) -> float:
    return float(chi2 + 2.0 * n_parameters + smoothness_penalty)


def bic(chi2: float, n_points: int, n_parameters: int, smoothness_penalty: float = 0.0) -> float:
    n = max(int(n_points), 1)
    return float(chi2 + n_parameters * np.log(n) + smoothness_penalty)


def model_parameter_count(model_name: str) -> int:
    lookup = {
        "baryonic_only": 0,
        "baryonic": 0,
        "nfw": 2,
        "nfw_refit": 2,
        "burkert": 2,
        "burkert_refit": 2,
        "mond_fixed_a0_simple": 0,
        "mond_fit_a0_simple": 1,
        "rar_fixed": 0,
        "tdf": 1,
        "tdf_3knot": 3,
        "tdf_4knot": 4,
        "tdf_5knot": 5,
        "direct_tau_reconstruction": 0,
    }
    return lookup.get(model_name.lower(), 0)
