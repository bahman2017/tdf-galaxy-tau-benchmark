from __future__ import annotations

import pandas as pd

from .smoothing import moving_average


def regularize_gradient(df: pd.DataFrame, column: str = "d_tau_dr", window: int = 3) -> pd.DataFrame:
    out = df.copy()
    out[f"{column}_regularized"] = moving_average(out[column], window=window)
    return out
