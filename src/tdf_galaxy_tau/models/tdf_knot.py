from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

from tdf_galaxy_tau.config.notation import merge_projection_from_yaml_blocks, resolve_projection_coefficient_kwarg

# Large penalty scale when v_model^2 < 0 during optimization
DEFAULT_NEGATIVE_V2_PENALTY = 1000.0

_MODEL_TO_N_KNOTS = {
    "tdf_3knot": 3,
    "tdf_4knot": 4,
    "tdf_5knot": 5,
}

_KNOT_RULE_LABEL = {
    3: "r_min,r_mid,r_max",
    4: "r_min,r_min+span/3,r_min+2span/3,r_max",
    5: "r_min,r_min+span/4,r_mid,r_min+3span/4,r_max",
}


@dataclass(frozen=True)
class TdfKnotConfig:
    k_g: float = 1.0
    amplitude_bound_safety_factor: float = 2.0
    negative_v2_penalty: float = DEFAULT_NEGATIVE_V2_PENALTY
    variants: tuple[str, ...] = ("tdf_3knot", "tdf_4knot", "tdf_5knot")

    @property
    def k_tau(self) -> float:
        """Deprecated alias for gravitational projection coefficient K_g."""
        return self.k_g


def n_knots_for_model(model_name: str) -> int:
    if model_name not in _MODEL_TO_N_KNOTS:
        raise ValueError(f"unknown TDF knot model: {model_name}")
    return _MODEL_TO_N_KNOTS[model_name]


def knot_position_rule_label(n_knots: int) -> str:
    return _KNOT_RULE_LABEL[n_knots]


def fixed_knot_radii_kpc(r_kpc: np.ndarray, n_knots: int) -> np.ndarray:
    """Fixed knot radii per galaxy from normalized placement rules."""
    r = np.asarray(r_kpc, dtype=float)
    if np.any(r <= 0):
        raise ValueError("r_kpc must be strictly positive for knot placement")
    r_min = float(np.min(r))
    r_max = float(np.max(r))
    span = r_max - r_min
    r_mid = r_min + 0.5 * span
    if n_knots == 3:
        knots = np.array([r_min, r_mid, r_max], dtype=float)
    elif n_knots == 4:
        knots = np.array([r_min, r_min + span / 3.0, r_min + 2.0 * span / 3.0, r_max], dtype=float)
    elif n_knots == 5:
        knots = np.array(
            [r_min, r_min + span / 4.0, r_mid, r_min + 3.0 * span / 4.0, r_max],
            dtype=float,
        )
    else:
        raise ValueError(f"unsupported knot count: {n_knots}")
    return np.sort(knots)


def interpolate_dtaudr_at_radii(
    r_eval_kpc: np.ndarray,
    knot_r_kpc: np.ndarray,
    knot_dtaudr: np.ndarray,
) -> np.ndarray:
    """Piecewise-linear dτ/dr between fixed knot radii."""
    return np.interp(
        np.asarray(r_eval_kpc, dtype=float),
        np.asarray(knot_r_kpc, dtype=float),
        np.asarray(knot_dtaudr, dtype=float),
    )


def tdf_velocity_squared_kms2(
    r_kpc: np.ndarray,
    v_bar_kms: np.ndarray,
    knot_r_kpc: np.ndarray,
    knot_dtaudr: np.ndarray,
    *,
    k_g: float | None = None,
    k_tau: float | None = None,
) -> np.ndarray:
    """v_tdf^2 = v_bar^2 + r * K_g * dτ/dr_model."""
    kg = resolve_projection_coefficient_kwarg(k_g=k_g, k_tau=k_tau, context="tdf_velocity_squared_kms2")
    r = np.asarray(r_kpc, dtype=float)
    vbar = np.asarray(v_bar_kms, dtype=float)
    dtaudr = interpolate_dtaudr_at_radii(r, knot_r_kpc, knot_dtaudr)
    return vbar**2 + r * kg * dtaudr


def tdf_velocity_kms(
    r_kpc: np.ndarray,
    v_bar_kms: np.ndarray,
    knot_r_kpc: np.ndarray,
    knot_dtaudr: np.ndarray,
    *,
    k_g: float | None = None,
    k_tau: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (v_model_kms, v_squared_kms2); sqrt only where v^2 > 0."""
    v2 = tdf_velocity_squared_kms2(
        r_kpc, v_bar_kms, knot_r_kpc, knot_dtaudr, k_g=k_g, k_tau=k_tau
    )
    v_model = np.sqrt(np.maximum(v2, 0.0))
    return v_model, v2


def initial_knot_amplitudes_from_reconstruction(
    knot_r_kpc: np.ndarray,
    r_recon_kpc: np.ndarray,
    dtaudr_reconstructed: np.ndarray,
) -> np.ndarray:
    """Sample Phase 2A dτ/dr at knot radii via linear interpolation."""
    return np.interp(
        knot_r_kpc,
        np.asarray(r_recon_kpc, dtype=float),
        np.asarray(dtaudr_reconstructed, dtype=float),
    )


def amplitude_bounds_from_reconstruction(
    dtaudr_reconstructed: np.ndarray,
    *,
    safety_factor: float,
) -> tuple[float, float]:
    """Symmetric bounds from reconstruction range × safety factor."""
    d = np.asarray(dtaudr_reconstructed, dtype=float)
    finite = d[np.isfinite(d)]
    if finite.size == 0:
        return (-1.0e6, 1.0e6)
    d_min = float(np.min(finite))
    d_max = float(np.max(finite))
    if d_min == d_max:
        margin = max(abs(d_min), 1.0) * safety_factor
        return (d_min - margin, d_max + margin)
    span = d_max - d_min
    pad = 0.5 * span * (safety_factor - 1.0) + 1.0e-9
    return (d_min - pad, d_max + pad)


def integrate_tau_profile(
    r_kpc: np.ndarray,
    dtaudr: np.ndarray,
    *,
    tau_at_r_min: float = 0.0,
) -> np.ndarray:
    """Integrate dτ/dr with τ(r_min)=0."""
    r = np.asarray(r_kpc, dtype=float)
    d = np.asarray(dtaudr, dtype=float)
    tau_inc = cumulative_trapezoid(d, r, initial=0.0)
    return tau_inc + float(tau_at_r_min)


def load_tdf_knot_config(reconstruction_yaml: dict) -> TdfKnotConfig:
    block = reconstruction_yaml.get("tdf_knot", {})
    radial = reconstruction_yaml.get("radial_tau_reconstruction", {})
    projection = merge_projection_from_yaml_blocks(reconstruction_yaml, radial, block)
    variants = tuple(block.get("variants", ["tdf_3knot", "tdf_4knot", "tdf_5knot"]))
    return TdfKnotConfig(
        k_g=float(projection["k_g"]),
        amplitude_bound_safety_factor=float(block.get("amplitude_bound_safety_factor", 2.0)),
        negative_v2_penalty=float(block.get("negative_v2_penalty", DEFAULT_NEGATIVE_V2_PENALTY)),
        variants=variants,
    )


def galaxy_tau_reconstruction_arrays(tau_df: pd.DataFrame, galaxy_id: str) -> tuple[np.ndarray, np.ndarray]:
    g = tau_df[tau_df["galaxy_id"] == galaxy_id].sort_values("r_kpc")
    if g.empty:
        raise ValueError(f"no tau reconstruction for galaxy {galaxy_id}")
    return g["r_kpc"].to_numpy(dtype=float), g["dtaudr_reconstructed"].to_numpy(dtype=float)


def galaxy_tau_reconstruction_train_only(
    tau_df: pd.DataFrame,
    galaxy_id: str,
    train_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Phase 2A dτ/dr on training radii only (for holdout fitting)."""
    r_all, d_all = galaxy_tau_reconstruction_arrays(tau_df, galaxy_id)
    mask = np.asarray(train_mask, dtype=bool)
    if mask.shape[0] != r_all.shape[0]:
        raise ValueError("train_mask length must match galaxy radial points")
    return r_all[mask], d_all[mask]


def fitted_knot_amplitudes_from_params(params: dict[str, float], n_knots: int) -> np.ndarray:
    return np.array([float(params[f"knot_{i}_dtaudr"]) for i in range(n_knots)], dtype=float)


def smoothness_second_difference_metric(
    r_kpc: np.ndarray,
    dtaudr: np.ndarray,
) -> tuple[float, float]:
    """Sum of squared second differences of dτ/dr; normalized by radial span."""
    r = np.asarray(r_kpc, dtype=float)
    d = np.asarray(dtaudr, dtype=float)
    if len(d) < 3:
        return float("nan"), float("nan")
    d2 = np.diff(d, n=2)
    raw = float(np.sum(d2**2))
    span = float(np.max(r) - np.min(r)) if len(r) > 1 else 1.0
    norm = raw / max(span**2, 1.0e-12)
    return raw, norm


def count_negative_velocity_squared(
    v_squared_kms2: np.ndarray,
) -> int:
    v2 = np.asarray(v_squared_kms2, dtype=float)
    return int(np.sum(v2 < 0))
