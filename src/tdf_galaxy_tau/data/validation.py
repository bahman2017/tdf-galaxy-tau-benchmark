from __future__ import annotations

import pandas as pd

from .schema import REQUIRED_COLUMNS


def validate_sparc_like_dataframe(df: pd.DataFrame) -> None:
    """Validate unit-explicit scaffold input table.

    Required units:
    - r_kpc in kpc
    - v_*_kms in km/s
    """

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if (df["r_kpc"] < 0).any():
        raise ValueError("r_kpc must be non-negative")
    if (df["v_err_kms"] <= 0).any():
        raise ValueError("v_err_kms must be positive")
