from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

from .smoothing import gaussian_smooth_1d, moving_average


@dataclass(frozen=True)
class SmoothingConfig:
    enabled: bool = False
    method: str = "gaussian"
    sigma_points: float = 1.0
    window: int = 3
    diagnostic_only: bool = True


def apply_diagnostic_smoothing(
    r_kpc: np.ndarray,
    dtaudr_reconstructed: np.ndarray,
    smoothing: SmoothingConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Return diagnostic smoothed dτ/dr and integrated τ (not a replacement fit)."""
    if not smoothing.enabled:
        nan = np.full_like(dtaudr_reconstructed, np.nan, dtype=float)
        return nan, nan

    if smoothing.method == "gaussian":
        d_smooth = gaussian_smooth_1d(dtaudr_reconstructed, smoothing.sigma_points)
    elif smoothing.method == "moving_average":
        d_smooth = moving_average(pd.Series(dtaudr_reconstructed), window=smoothing.window).to_numpy()
    else:
        raise ValueError(f"unsupported smoothing method: {smoothing.method}")

    d_for_int = np.where(np.isfinite(d_smooth), d_smooth, 0.0)
    tau_smooth = cumulative_trapezoid(d_for_int, r_kpc, initial=0.0)
    return d_smooth, tau_smooth
