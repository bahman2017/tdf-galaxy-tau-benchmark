from __future__ import annotations

import pandas as pd


def moving_average(series: pd.Series, window: int = 3) -> pd.Series:
    return series.rolling(window=window, min_periods=1, center=True).mean()
