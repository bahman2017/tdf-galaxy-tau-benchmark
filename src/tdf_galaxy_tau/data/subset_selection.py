from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REQUIRED_FINITE_COLUMNS = [
    "r_kpc",
    "v_obs_kms",
    "v_err_kms",
    "v_gas_kms",
    "v_disk_kms",
    "v_bulge_kms",
    "v_bar_kms",
    "residual_v2_kms2",
]


@dataclass(frozen=True)
class SubsetSelectionConfig:
    input_csv: str
    output_subset_csv: str
    output_report_md: str
    candidate_galaxies: list[str]
    min_radial_points: int = 12
    min_radial_coverage_kpc: float = 5.0
    max_selected_galaxies: int = 6
    allow_mock_data: bool = False


def _load_table(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("standardized SPARC table is empty")
    missing = [c for c in ["galaxy_id", "data_source", "data_mode", *REQUIRED_FINITE_COLUMNS] if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns for subset selection: {missing}")
    return df


def _evaluate_one_galaxy(galaxy_id: str, group: pd.DataFrame, cfg: SubsetSelectionConfig) -> dict[str, Any]:
    finite_mask = np.isfinite(group[REQUIRED_FINITE_COLUMNS]).all(axis=1)
    all_finite = bool(finite_mask.all())

    n_points = int(len(group))
    r_min = float(group["r_kpc"].min())
    r_max = float(group["r_kpc"].max())
    coverage = r_max - r_min
    v_min = float(group["v_obs_kms"].min())
    v_max = float(group["v_obs_kms"].max())
    median_v_err = float(group["v_err_kms"].median())
    has_bulge = bool((group["v_bulge_kms"].abs() > 0).any())
    n_negative = int((group["residual_v2_kms2"] < 0).sum())
    neg_frac = float(n_negative / n_points) if n_points > 0 else 0.0

    reasons: list[str] = []
    if n_points < cfg.min_radial_points:
        reasons.append(f"n_points<{cfg.min_radial_points}")
    if coverage <= cfg.min_radial_coverage_kpc:
        reasons.append(f"radial_coverage<={cfg.min_radial_coverage_kpc}")
    if not all_finite:
        reasons.append("non_finite_required_values")
    if (group["r_kpc"] <= 0).any():
        reasons.append("non_positive_r_kpc")
    if (group["v_obs_kms"] <= 0).any():
        reasons.append("non_positive_v_obs_kms")
    if (group["v_err_kms"] <= 0).any():
        reasons.append("non_positive_v_err_kms")

    selected = False
    return {
        "galaxy_id": galaxy_id,
        "selected": selected,
        "selection_rank": np.nan,
        "n_points": n_points,
        "r_min_kpc": r_min,
        "r_max_kpc": r_max,
        "radial_coverage_kpc": coverage,
        "v_obs_min_kms": v_min,
        "v_obs_max_kms": v_max,
        "median_v_err_kms": median_v_err,
        "has_bulge": has_bulge,
        "n_negative_residual_points": n_negative,
        "negative_residual_fraction": neg_frac,
        "quality_flag": "eligible" if not reasons else "rejected_quality",
        "rejection_reason": "" if not reasons else ";".join(reasons),
        "data_source": str(group["data_source"].mode().iloc[0]),
        "data_mode": str(group["data_mode"].mode().iloc[0]),
    }


def _deterministic_select(rows: pd.DataFrame, cfg: SubsetSelectionConfig) -> pd.DataFrame:
    eligible = rows[rows["quality_flag"] == "eligible"].copy()
    selected_ids: list[str] = []

    eligible_ids = set(eligible["galaxy_id"].tolist())
    for gid in cfg.candidate_galaxies:
        if gid in eligible_ids and gid not in selected_ids:
            selected_ids.append(gid)
        if len(selected_ids) >= cfg.max_selected_galaxies:
            break

    if len(selected_ids) < cfg.max_selected_galaxies:
        remainder = eligible[~eligible["galaxy_id"].isin(selected_ids)].copy()
        remainder = remainder.sort_values(
            by=["n_points", "radial_coverage_kpc", "galaxy_id"],
            ascending=[False, False, True],
        )
        need = cfg.max_selected_galaxies - len(selected_ids)
        selected_ids.extend(remainder["galaxy_id"].head(need).tolist())

    rows = rows.copy()
    rows["selected"] = rows["galaxy_id"].isin(selected_ids)
    rows.loc[rows["selected"], "quality_flag"] = "selected"
    rows.loc[(~rows["selected"]) & (rows["quality_flag"] == "eligible"), "quality_flag"] = "eligible_not_selected"

    rank_map = {gid: i + 1 for i, gid in enumerate(selected_ids)}
    rows["selection_rank"] = rows["galaxy_id"].map(rank_map)
    return rows.sort_values(["selected", "selection_rank", "galaxy_id"], ascending=[False, True, True]).reset_index(drop=True)


def select_sparc_subset(cfg: SubsetSelectionConfig) -> tuple[pd.DataFrame, dict[str, Any]]:
    df = _load_table(cfg.input_csv)
    rows = pd.DataFrame([_evaluate_one_galaxy(gid, grp, cfg) for gid, grp in df.groupby("galaxy_id", sort=True)])
    rows = _deterministic_select(rows, cfg)

    selected = rows[rows["selected"]]["galaxy_id"].tolist()

    missing_candidates = [gid for gid in cfg.candidate_galaxies if gid not in set(rows["galaxy_id"].tolist())]
    rejected_candidates = rows[(rows["galaxy_id"].isin(cfg.candidate_galaxies)) & (~rows["selected"])].copy()

    context = {
        "total_evaluated": int(len(rows)),
        "total_selected": int(rows["selected"].sum()),
        "selected_galaxies": selected,
        "missing_candidates": missing_candidates,
        "rejected_candidates": rejected_candidates[["galaxy_id", "rejection_reason", "quality_flag"]].to_dict("records"),
        "criteria": {
            "min_radial_points": cfg.min_radial_points,
            "min_radial_coverage_kpc": cfg.min_radial_coverage_kpc,
            "required_finite_columns": REQUIRED_FINITE_COLUMNS,
            "require_positive": ["r_kpc", "v_obs_kms", "v_err_kms"],
            "allow_negative_residual_v2": True,
            "max_selected_galaxies": cfg.max_selected_galaxies,
        },
        "negative_residual_note": (
            "Negative residual_v2_kms2 values are allowed and reported; they are not a rejection criterion in Phase 1B."
        ),
        "bulge_diversity_note": (
            f"Selected galaxies with bulge contribution: {int(rows[rows['selected']]['has_bulge'].sum())} of {int(rows['selected'].sum())}."
            if int(rows['selected'].sum()) > 0
            else "No galaxies selected."
        ),
    }
    return rows, context
