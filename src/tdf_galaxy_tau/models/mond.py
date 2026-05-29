from __future__ import annotations

import numpy as np

# Unit conversions (SI)
KPC_TO_M = 3.085677581e19
KMS_TO_MS = 1000.0
A0_DEFAULT_MS2 = 1.2e-10

# Avoid division by zero in acceleration ratios
_G_BAR_FLOOR_MS2 = 1.0e-30


def kpc_to_meters(r_kpc: np.ndarray) -> np.ndarray:
    return np.asarray(r_kpc, dtype=float) * KPC_TO_M


def kms_to_ms(v_kms: np.ndarray) -> np.ndarray:
    return np.asarray(v_kms, dtype=float) * KMS_TO_MS


def ms_to_kms(v_ms: np.ndarray) -> np.ndarray:
    return np.asarray(v_ms, dtype=float) / KMS_TO_MS


def baryonic_acceleration_ms2(r_kpc: np.ndarray, v_bar_kms: np.ndarray) -> np.ndarray:
    """g_bar = v_bar^2 / r with r in meters and v_bar in m/s."""
    r_m = kpc_to_meters(r_kpc)
    v_ms = kms_to_ms(v_bar_kms)
    r_safe = np.maximum(r_m, 1.0e-6)
    return np.maximum(v_ms**2 / r_safe, 0.0)


def simple_mond_nu(y: np.ndarray) -> np.ndarray:
    """Simple MOND interpolation: nu(y) = 0.5 + sqrt(0.25 + 1/y)."""
    y_arr = np.asarray(y, dtype=float)
    y_safe = np.maximum(y_arr, _G_BAR_FLOOR_MS2 / A0_DEFAULT_MS2)
    return 0.5 + np.sqrt(0.25 + 1.0 / y_safe)


def mond_observed_acceleration_simple(g_bar_ms2: np.ndarray, a0_ms2: float) -> np.ndarray:
    """g_obs = nu(g_bar/a0) * g_bar for the simple interpolation function."""
    g_bar = np.asarray(g_bar_ms2, dtype=float)
    a0 = float(a0_ms2)
    if a0 <= 0:
        raise ValueError("a0 must be positive")
    y = np.maximum(g_bar / a0, 0.0)
    # Deep-MOND limit: when g_bar is tiny, use g_obs = sqrt(g_bar * a0)
    tiny = g_bar <= _G_BAR_FLOOR_MS2
    g_obs = np.empty_like(g_bar)
    if np.any(tiny):
        g_obs[tiny] = np.sqrt(np.maximum(g_bar[tiny], 0.0) * a0)
    if np.any(~tiny):
        g_nt = g_bar[~tiny]
        g_obs[~tiny] = simple_mond_nu(g_nt / a0) * g_nt
    return np.maximum(g_obs, 0.0)


def rar_observed_acceleration(g_bar_ms2: np.ndarray, g_dagger_ms2: float) -> np.ndarray:
    """Empirical RAR-style: g_obs = g_bar / (1 - exp(-sqrt(g_bar / g_dagger)))."""
    g_bar = np.asarray(g_bar_ms2, dtype=float)
    g_d = float(g_dagger_ms2)
    if g_d <= 0:
        raise ValueError("g_dagger must be positive")
    ratio = np.sqrt(np.maximum(g_bar / g_d, 0.0))
    denom = 1.0 - np.exp(-ratio)
    with np.errstate(invalid="ignore", divide="ignore"):
        g_rar = np.where(denom > 0, g_bar / denom, 0.0)
    return np.where(g_bar <= _G_BAR_FLOOR_MS2, 0.0, g_rar)


def acceleration_to_velocity_kms(g_obs_ms2: np.ndarray, r_kpc: np.ndarray) -> np.ndarray:
    """v = sqrt(g * r) with consistent SI units, returned in km/s."""
    r_m = kpc_to_meters(r_kpc)
    g = np.maximum(np.asarray(g_obs_ms2, dtype=float), 0.0)
    v_ms = np.sqrt(g * np.maximum(r_m, 1.0e-6))
    return ms_to_kms(v_ms)


def mond_fixed_a0_velocity_kms(
    r_kpc: np.ndarray,
    v_bar_kms: np.ndarray,
    *,
    a0_ms2: float = A0_DEFAULT_MS2,
) -> np.ndarray:
    g_bar = baryonic_acceleration_ms2(r_kpc, v_bar_kms)
    g_obs = mond_observed_acceleration_simple(g_bar, a0_ms2)
    return acceleration_to_velocity_kms(g_obs, r_kpc)


def mond_fit_a0_velocity_kms(
    r_kpc: np.ndarray,
    v_bar_kms: np.ndarray,
    log10_a0_ms2: float,
) -> np.ndarray:
    a0 = float(10.0 ** log10_a0_ms2)
    return mond_fixed_a0_velocity_kms(r_kpc, v_bar_kms, a0_ms2=a0)


def rar_fixed_velocity_kms(
    r_kpc: np.ndarray,
    v_bar_kms: np.ndarray,
    *,
    g_dagger_ms2: float = A0_DEFAULT_MS2,
) -> np.ndarray:
    g_bar = baryonic_acceleration_ms2(r_kpc, v_bar_kms)
    g_obs = rar_observed_acceleration(g_bar, g_dagger_ms2)
    return acceleration_to_velocity_kms(g_obs, r_kpc)


def log10_a0_to_a0(log10_a0: float) -> float:
    return float(10.0 ** float(log10_a0))
