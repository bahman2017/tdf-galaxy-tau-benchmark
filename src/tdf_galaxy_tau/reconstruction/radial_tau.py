from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid


_R_EPS = 1.0e-12
_NEGATIVE_EPS = 1.0e-12
_VALID_POLICIES = {"allow_signed", "clip_to_zero", "mask_negative"}


@dataclass(frozen=True)
class TauReconstructionConfig:
    """Configuration for radial tau reconstruction.

    Notes:
    - K_tau is a normalization/calibration parameter, not a measured universal constant.
    - dtaudr_reconstructed is a reconstruction quantity inferred from residual dynamics.
    """

    k_tau: float = 1.0
    negative_residual_policy: str = "allow_signed"


def _validate_policy(policy: str) -> str:
    if policy not in _VALID_POLICIES:
        raise ValueError(f"negative_residual_policy must be one of {_VALID_POLICIES}; got {policy}")
    return policy


def _flags_for_row(r_kpc: float, residual_v2_kms2: float, policy_applied: str) -> str:
    flags = []
    if r_kpc <= _R_EPS:
        flags.append("radius_zero_guard")
    if residual_v2_kms2 < -_NEGATIVE_EPS:
        flags.append("negative_residual")
        if policy_applied == "clip_to_zero":
            flags.append("residual_clipped")
        if policy_applied == "mask_negative":
            flags.append("residual_masked")
    return "|".join(flags) if flags else "ok"


def reconstruct_radial_tau_profile(
    galaxy_df: pd.DataFrame,
    galaxy_id: str,
    config: TauReconstructionConfig,
) -> pd.DataFrame:
    """Reconstruct radial tau profile from rotation residuals.

    Core equations (preserved):
    - v_obs^2(r) = v_bar^2(r) + v_tau^2(r)
    - v_tau^2(r) = r K_tau dτ/dr
    - dτ/dr = [v_obs^2(r) - v_bar^2(r)] / [r K_tau]

    Required input columns:
    - r_kpc
    - v_obs_kms
    - v_bar_kms
    """

    required = ["r_kpc", "v_obs_kms", "v_bar_kms"]
    missing = [c for c in required if c not in galaxy_df.columns]
    if missing:
        raise ValueError(f"Missing required columns for reconstruction: {missing}")
    if config.k_tau <= 0:
        raise ValueError("k_tau must be positive")

    policy = _validate_policy(config.negative_residual_policy)

    work = galaxy_df.sort_values("r_kpc").reset_index(drop=True).copy()
    r_kpc = work["r_kpc"].to_numpy(dtype=float)
    if np.any(r_kpc < 0):
        raise ValueError("r_kpc must be non-negative")

    v_obs_kms = work["v_obs_kms"].to_numpy(dtype=float)
    v_bar_kms = work["v_bar_kms"].to_numpy(dtype=float)

    residual_v2_kms2 = v_obs_kms**2 - v_bar_kms**2

    if policy == "allow_signed":
        residual_for_calc = residual_v2_kms2
    elif policy == "clip_to_zero":
        residual_for_calc = np.maximum(residual_v2_kms2, 0.0)
    else:
        residual_for_calc = residual_v2_kms2.copy()
        residual_for_calc[residual_v2_kms2 < 0.0] = np.nan

    safe_r_kpc = np.maximum(r_kpc, _R_EPS)
    residual_accel_proxy_kms2_per_kpc = residual_for_calc / safe_r_kpc
    dtaudr_reconstructed = residual_for_calc / (safe_r_kpc * config.k_tau)

    dtaudr_for_integration = np.where(np.isfinite(dtaudr_reconstructed), dtaudr_reconstructed, 0.0)
    tau_reconstructed = cumulative_trapezoid(dtaudr_for_integration, r_kpc, initial=0.0)

    flags = [_flags_for_row(r, rv2, policy) for r, rv2 in zip(r_kpc, residual_v2_kms2)]

    return pd.DataFrame(
        {
            "galaxy_id": [galaxy_id] * len(work),
            "r_kpc": r_kpc,
            "v_obs_kms": v_obs_kms,
            "v_bar_kms": v_bar_kms,
            "v_tau2_kms2": residual_for_calc,
            "residual_v2_kms2": residual_v2_kms2,
            "residual_accel_proxy_kms2_per_kpc": residual_accel_proxy_kms2_per_kpc,
            "dtaudr_reconstructed": dtaudr_reconstructed,
            "tau_reconstructed": tau_reconstructed,
            "negative_residual_policy": [policy] * len(work),
            "flags": flags,
        }
    )
