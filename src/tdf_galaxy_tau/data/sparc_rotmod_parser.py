from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import numpy as np
import pandas as pd


EXPECTED_STANDARDIZED_COLUMNS = [
    "galaxy_id",
    "source_file",
    "distance_mpc",
    "r_kpc",
    "v_obs_kms",
    "v_err_kms",
    "v_gas_kms",
    "v_disk_kms",
    "v_bulge_kms",
    "sb_disk_lpc2",
    "sb_bulge_lpc2",
    "v_bar_kms",
    "residual_v2_kms2",
    "quality_flag",
    "data_source",
    "data_mode",
]


@dataclass(frozen=True)
class IngestionSummary:
    raw_files_found: int
    galaxies_parsed_successfully: int
    galaxies_failed: int
    total_radial_points: int
    min_r_kpc: float | None
    max_r_kpc: float | None
    min_v_obs_kms: float | None
    max_v_obs_kms: float | None
    galaxies_with_bulge: int
    rows_negative_residual_v2: int


def _extract_distance_mpc(lines: list[str]) -> float | None:
    for line in lines[:20]:
        if not line.strip().startswith("#"):
            continue
        m = re.search(r"distance\s*=\s*([-+]?\d*\.?\d+)\s*mpc", line, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None
    return None


def parse_rotmod_file(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.name.endswith("_rotmod.dat"):
        raise ValueError(f"unexpected rotmod filename: {path.name}")

    text_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    distance_mpc = _extract_distance_mpc(text_lines)

    raw = pd.read_csv(path, sep=r"\s+", comment="#", header=None, engine="python")
    if raw.shape[1] < 6:
        raise ValueError(f"insufficient columns ({raw.shape[1]}) in {path.name}")

    col_names = [
        "r_kpc",
        "v_obs_kms",
        "v_err_kms",
        "v_gas_kms",
        "v_disk_kms",
        "v_bulge_kms",
        "sb_disk_lpc2",
        "sb_bulge_lpc2",
    ]
    raw = raw.iloc[:, : min(len(col_names), raw.shape[1])].copy()
    raw.columns = col_names[: raw.shape[1]]

    if "sb_disk_lpc2" not in raw.columns:
        raw["sb_disk_lpc2"] = np.nan
    if "sb_bulge_lpc2" not in raw.columns:
        raw["sb_bulge_lpc2"] = np.nan

    for c in [
        "r_kpc",
        "v_obs_kms",
        "v_err_kms",
        "v_gas_kms",
        "v_disk_kms",
        "v_bulge_kms",
        "sb_disk_lpc2",
        "sb_bulge_lpc2",
    ]:
        raw[c] = pd.to_numeric(raw[c], errors="coerce")

    raw = raw.dropna(subset=["r_kpc", "v_obs_kms", "v_err_kms", "v_gas_kms", "v_disk_kms", "v_bulge_kms"])
    raw = raw[(raw["r_kpc"] > 0) & (raw["v_obs_kms"] > 0) & (raw["v_err_kms"] > 0)].copy()
    if raw.empty:
        raise ValueError(f"no valid rows after filtering for {path.name}")

    v_bar2 = raw["v_gas_kms"] ** 2 + raw["v_disk_kms"] ** 2 + raw["v_bulge_kms"] ** 2
    raw["v_bar_kms"] = np.sqrt(np.maximum(v_bar2.to_numpy(dtype=float), 0.0))
    raw["residual_v2_kms2"] = raw["v_obs_kms"] ** 2 - raw["v_bar_kms"] ** 2

    has_negative_component = (
        (raw["v_gas_kms"] < 0) | (raw["v_disk_kms"] < 0) | (raw["v_bulge_kms"] < 0)
    )
    raw["quality_flag"] = np.where(has_negative_component, "negative_component_present", "ok")

    galaxy_id = path.name.replace("_rotmod.dat", "")
    raw.insert(0, "galaxy_id", galaxy_id)
    raw.insert(1, "source_file", path.name)
    raw.insert(2, "distance_mpc", distance_mpc)
    raw["data_source"] = "SPARC_Lelli2016"
    raw["data_mode"] = "observational_raw_ingestion"

    out = raw[EXPECTED_STANDARDIZED_COLUMNS].copy()
    return out.reset_index(drop=True)


def ingest_rotmod_directory(input_dir: str | Path) -> tuple[pd.DataFrame, list[dict[str, str]], IngestionSummary]:
    input_dir = Path(input_dir)
    files = sorted(input_dir.glob("*_rotmod.dat"))
    failures: list[dict[str, str]] = []
    frames: list[pd.DataFrame] = []

    for file_path in files:
        try:
            frames.append(parse_rotmod_file(file_path))
        except Exception as exc:  # noqa: BLE001
            failures.append({"source_file": file_path.name, "error": str(exc)})

    if frames:
        df = pd.concat(frames, ignore_index=True)
        min_r = float(df["r_kpc"].min())
        max_r = float(df["r_kpc"].max())
        min_v = float(df["v_obs_kms"].min())
        max_v = float(df["v_obs_kms"].max())
        bulge_count = int(df.groupby("galaxy_id")["v_bulge_kms"].apply(lambda s: (s.abs() > 0).any()).sum())
        neg_resid_rows = int((df["residual_v2_kms2"] < 0).sum())
    else:
        df = pd.DataFrame(columns=EXPECTED_STANDARDIZED_COLUMNS)
        min_r = max_r = min_v = max_v = None
        bulge_count = 0
        neg_resid_rows = 0

    summary = IngestionSummary(
        raw_files_found=len(files),
        galaxies_parsed_successfully=int(df["galaxy_id"].nunique()) if not df.empty else 0,
        galaxies_failed=len(failures),
        total_radial_points=int(len(df)),
        min_r_kpc=min_r,
        max_r_kpc=max_r,
        min_v_obs_kms=min_v,
        max_v_obs_kms=max_v,
        galaxies_with_bulge=bulge_count,
        rows_negative_residual_v2=neg_resid_rows,
    )
    return df, failures, summary
