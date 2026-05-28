from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BaryonicInputs:
    v_gas_kms: np.ndarray
    v_disk_kms: np.ndarray
    v_bulge_kms: np.ndarray


def baryonic_velocity(v_gas_kms: np.ndarray, v_disk_kms: np.ndarray, v_bulge_kms: np.ndarray) -> np.ndarray:
    v2 = (
        np.asarray(v_gas_kms, dtype=float) ** 2
        + np.asarray(v_disk_kms, dtype=float) ** 2
        + np.asarray(v_bulge_kms, dtype=float) ** 2
    )
    return np.sqrt(np.maximum(v2, 0.0))


def add_baryonic_column(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["v_bar_kms"] = baryonic_velocity(
        out["v_gas_kms"].to_numpy(),
        out["v_disk_kms"].to_numpy(),
        out["v_bulge_kms"].to_numpy(),
    )
    return out
