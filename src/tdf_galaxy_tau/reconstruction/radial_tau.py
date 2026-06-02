from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from scipy.integrate import cumulative_trapezoid

from tdf_galaxy_tau.config.notation import merge_projection_from_yaml_blocks

from .regularization import SmoothingConfig, apply_diagnostic_smoothing


_NEGATIVE_EPS = 1.0e-12
_VALID_POLICIES = {"allow_signed", "clip_to_zero", "mask_negative"}

PHASE_2A_OUTPUT_COLUMNS = [
    "galaxy_id",
    "r_kpc",
    "v_obs_kms",
    "v_err_kms",
    "v_bar_kms",
    "residual_v2_kms2",
    "residual_policy_applied",
    "K_tau",
    "dtaudr_reconstructed",
    "tau_reconstructed",
    "dtaudr_smoothed_diagnostic",
    "tau_smoothed_diagnostic",
    "negative_residual_flag",
    "data_source",
    "data_mode",
    "reconstruction_stage",
]


@dataclass(frozen=True)
class TauReconstructionConfig:
    """Radial τ reconstruction settings (Phase 2A).

    ``k_tau`` stores the gravitational projection coefficient (K_g); legacy config key name.
    dtaudr_reconstructed is inferred from rotation residuals, not a directly measured field.
    """

    k_tau: float = 1.0
    negative_residual_policy: str = "allow_signed"
    integration_boundary: str = "tau_at_r_min_zero"
    smoothing: SmoothingConfig = SmoothingConfig()


def _validate_policy(policy: str) -> str:
    if policy not in _VALID_POLICIES:
        raise ValueError(f"negative_residual_policy must be one of {_VALID_POLICIES}; got {policy}")
    return policy


def load_reconstruction_config(path: str | Path) -> TauReconstructionConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    block = raw.get("radial_tau_reconstruction", raw)
    smooth_raw = block.get("smoothing", {})
    smoothing = SmoothingConfig(
        enabled=bool(smooth_raw.get("enabled", False)),
        method=str(smooth_raw.get("method", "gaussian")),
        sigma_points=float(smooth_raw.get("sigma_points", 1.0)),
        window=int(smooth_raw.get("window", 3)),
        diagnostic_only=bool(smooth_raw.get("diagnostic_only", True)),
    )
    projection = merge_projection_from_yaml_blocks(raw, block)
    return TauReconstructionConfig(
        k_tau=float(projection["k_g"]),
        negative_residual_policy=str(
            block.get("negative_residual_policy", raw.get("negative_residual_policy", "allow_signed"))
        ),
        integration_boundary=str(block.get("integration_boundary", "tau_at_r_min_zero")),
        smoothing=smoothing,
    )


def reconstruct_radial_tau_profile(
    galaxy_df: pd.DataFrame,
    galaxy_id: str,
    config: TauReconstructionConfig,
    *,
    reconstruction_stage: str = "phase_2a_radial_reconstruction",
) -> pd.DataFrame:
    """Reconstruct galaxy-specific radial τ from rotation residuals.

    Core equations (preserved):
    - v_obs^2(r) = v_bar^2(r) + v_tau^2(r)
    - v_tau^2(r) = r K_tau dτ/dr
    - dτ/dr = [v_obs^2(r) - v_bar^2(r)] / [r K_tau]
    """
    required = ["r_kpc", "v_obs_kms", "v_bar_kms"]
    missing = [c for c in required if c not in galaxy_df.columns]
    if missing:
        raise ValueError(f"Missing required columns for reconstruction: {missing}")
    if config.k_tau <= 0:
        raise ValueError("k_tau must be positive")
    if config.integration_boundary != "tau_at_r_min_zero":
        raise ValueError("only integration_boundary=tau_at_r_min_zero is implemented")

    policy = _validate_policy(config.negative_residual_policy)

    work = galaxy_df.sort_values("r_kpc").reset_index(drop=True).copy()
    if (work["r_kpc"] <= 0).any():
        raise ValueError("r_kpc must be strictly positive")

    v_obs_kms = work["v_obs_kms"].to_numpy(dtype=float)
    v_bar_kms = work["v_bar_kms"].to_numpy(dtype=float)
    r_kpc = work["r_kpc"].to_numpy(dtype=float)
    v_err_kms = (
        work["v_err_kms"].to_numpy(dtype=float)
        if "v_err_kms" in work.columns
        else np.full(len(work), np.nan)
    )

    residual_v2_kms2 = v_obs_kms**2 - v_bar_kms**2

    if policy == "mask_negative":
        keep = residual_v2_kms2 >= 0.0
        work = work.loc[keep].reset_index(drop=True)
        v_obs_kms = work["v_obs_kms"].to_numpy(dtype=float)
        v_bar_kms = work["v_bar_kms"].to_numpy(dtype=float)
        r_kpc = work["r_kpc"].to_numpy(dtype=float)
        v_err_kms = (
            work["v_err_kms"].to_numpy(dtype=float)
            if "v_err_kms" in work.columns
            else np.full(len(work), np.nan)
        )
        residual_v2_kms2 = v_obs_kms**2 - v_bar_kms**2

    if policy == "allow_signed":
        residual_for_calc = residual_v2_kms2
    elif policy == "clip_to_zero":
        residual_for_calc = np.maximum(residual_v2_kms2, 0.0)
    else:
        residual_for_calc = residual_v2_kms2

    dtaudr_reconstructed = residual_for_calc / (r_kpc * config.k_tau)
    d_for_int = np.where(np.isfinite(dtaudr_reconstructed), dtaudr_reconstructed, 0.0)
    tau_reconstructed = cumulative_trapezoid(d_for_int, r_kpc, initial=0.0)

    d_smooth, tau_smooth = apply_diagnostic_smoothing(
        r_kpc,
        dtaudr_reconstructed,
        config.smoothing,
    )

    neg_flag = residual_v2_kms2 < -_NEGATIVE_EPS
    data_source = str(work["data_source"].iloc[0]) if "data_source" in work.columns else "unknown"
    data_mode = str(work["data_mode"].iloc[0]) if "data_mode" in work.columns else "unknown"

    out = pd.DataFrame(
        {
            "galaxy_id": [galaxy_id] * len(work),
            "r_kpc": r_kpc,
            "v_obs_kms": v_obs_kms,
            "v_err_kms": v_err_kms,
            "v_bar_kms": v_bar_kms,
            "residual_v2_kms2": residual_v2_kms2,
            "residual_policy_applied": [policy] * len(work),
            "K_tau": [config.k_tau] * len(work),
            "dtaudr_reconstructed": dtaudr_reconstructed,
            "tau_reconstructed": tau_reconstructed,
            "dtaudr_smoothed_diagnostic": d_smooth,
            "tau_smoothed_diagnostic": tau_smooth,
            "negative_residual_flag": neg_flag,
            "data_source": [data_source] * len(work),
            "data_mode": [data_mode] * len(work),
            "reconstruction_stage": [reconstruction_stage] * len(work),
        }
    )
    return out[PHASE_2A_OUTPUT_COLUMNS]


def load_selected_galaxy_ids(subset_csv: str | Path) -> list[str]:
    subset = pd.read_csv(subset_csv)
    if "selected" not in subset.columns:
        raise ValueError("subset selection table must include 'selected' column")
    selected = subset[subset["selected"].astype(bool)]
    return selected["galaxy_id"].astype(str).tolist()


def reconstruct_selected_subset(
    data_csv: str | Path,
    subset_csv: str | Path,
    config: TauReconstructionConfig,
) -> pd.DataFrame:
    data = pd.read_csv(data_csv)
    galaxy_ids = load_selected_galaxy_ids(subset_csv)
    frames: list[pd.DataFrame] = []
    for gid in galaxy_ids:
        group = data[data["galaxy_id"] == gid]
        if group.empty:
            raise ValueError(f"selected galaxy {gid!r} not found in data table")
        frames.append(reconstruct_radial_tau_profile(group, gid, config))
    return pd.concat(frames, ignore_index=True)
