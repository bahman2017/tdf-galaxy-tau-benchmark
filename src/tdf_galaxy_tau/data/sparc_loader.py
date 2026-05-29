from __future__ import annotations

from pathlib import Path

import pandas as pd

from .sparc_rotmod_parser import ingest_rotmod_directory
from .validation import validate_sparc_like_dataframe, validate_standardized_sparc_dataframe


def load_sparc_like_csv(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    validate_sparc_like_dataframe(frame)
    return frame.sort_values(["galaxy_id", "r_kpc"]).reset_index(drop=True)


def load_standardized_sparc_csv(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    validate_standardized_sparc_dataframe(frame)
    return frame.sort_values(["galaxy_id", "r_kpc"]).reset_index(drop=True)


def ingest_sparc_rotmod_to_csv(input_dir: str | Path, out_csv: str | Path) -> tuple[pd.DataFrame, list[dict[str, str]], object]:
    standardized, failures, summary = ingest_rotmod_directory(input_dir)
    validate_standardized_sparc_dataframe(standardized)
    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    standardized.to_csv(out_path, index=False)
    return standardized, failures, summary


def build_mock_sparc_subset(galaxy_ids: list[str]) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for i, gid in enumerate(galaxy_ids):
        for radius in [0.5, 1.0, 2.0, 4.0, 8.0]:
            v_gas = 10.0 + 0.4 * radius
            v_disk = 30.0 + 0.9 * radius
            v_bulge = 5.0 if i % 2 == 0 else 2.0
            v_bar = (v_gas**2 + v_disk**2 + v_bulge**2) ** 0.5
            v_obs = v_bar + 8.0 + 0.3 * radius
            rows.append(
                {
                    "galaxy_id": gid,
                    "r_kpc": radius,
                    "v_obs_kms": v_obs,
                    "v_err_kms": 3.0,
                    "v_gas_kms": v_gas,
                    "v_disk_kms": v_disk,
                    "v_bulge_kms": v_bulge,
                    "data_mode": "mock",
                }
            )
    return pd.DataFrame(rows)
