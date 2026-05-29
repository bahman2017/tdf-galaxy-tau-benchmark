from __future__ import annotations

import pandas as pd

from .schema import REQUIRED_COLUMNS
from .sparc_rotmod_parser import EXPECTED_STANDARDIZED_COLUMNS


def validate_sparc_like_dataframe(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if (df["r_kpc"] < 0).any():
        raise ValueError("r_kpc must be non-negative")
    if (df["v_err_kms"] <= 0).any():
        raise ValueError("v_err_kms must be positive")


def validate_standardized_sparc_dataframe(df: pd.DataFrame) -> None:
    missing = [c for c in EXPECTED_STANDARDIZED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing standardized columns: {missing}")
    if df.empty:
        raise ValueError("standardized SPARC dataframe is empty")
    if (df["r_kpc"] <= 0).any():
        raise ValueError("r_kpc must be positive after ingestion filtering")
    if (df["v_obs_kms"] <= 0).any():
        raise ValueError("v_obs_kms must be positive after ingestion filtering")
    if (df["v_err_kms"] <= 0).any():
        raise ValueError("v_err_kms must be positive after ingestion filtering")
