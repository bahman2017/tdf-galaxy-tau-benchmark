from __future__ import annotations

import numpy as np
import pandas as pd


def moving_average(series: pd.Series, window: int = 3) -> pd.Series:
    return series.rolling(window=window, min_periods=1, center=True).mean()


def gaussian_smooth_1d(values: np.ndarray, sigma_points: float) -> np.ndarray:
    """Gaussian smooth a 1D series along radial index (diagnostic only)."""
    from scipy.ndimage import gaussian_filter1d

    arr = np.asarray(values, dtype=float)
    if len(arr) == 0:
        return arr
    if sigma_points <= 0:
        return arr.copy()
    # Preserve NaNs at masked locations while smoothing finite values.
    finite = np.isfinite(arr)
    if not finite.any():
        return arr.copy()
    filled = arr.copy()
    filled[~finite] = np.interp(
        np.flatnonzero(~finite),
        np.flatnonzero(finite),
        filled[finite],
    )
    smoothed = gaussian_filter1d(filled, sigma=sigma_points, mode="nearest")
    smoothed[~finite] = np.nan
    return smoothed
