from __future__ import annotations

import ast
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from tdf_galaxy_tau.metrics.comparison import chi_square, poor_rmse_relative_to_median_velocity

from .burkert import BurkertParams, burkert_params_from_log10, burkert_velocity
from .nfw import NFWParams, nfw_params_from_log10, nfw_velocity


@dataclass(frozen=True)
class FitResult:
    model_name: str
    fit_success: bool
    fit_status: str
    n_parameters: int
    params: dict[str, float]
    bounds: dict[str, tuple[float, float]]
    v_model_kms: np.ndarray
    log_params: dict[str, float] | None = None
    fitting_mode: str = "legacy_linear"
    chi_square: float | None = None
    n_starts_attempted: int = 1
    n_starts_successful: int = 0


def baryonic_only_model(v_bar_kms: np.ndarray) -> FitResult:
    return FitResult(
        model_name="baryonic_only",
        fit_success=True,
        fit_status="fixed_baryonic_model",
        n_parameters=0,
        params={},
        bounds={},
        v_model_kms=np.asarray(v_bar_kms, dtype=float),
    )


def _weighted_residual(v_obs: np.ndarray, v_model: np.ndarray, v_err: np.ndarray) -> np.ndarray:
    return (v_obs - v_model) / v_err


def fit_nfw_baseline(
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    *,
    rho_s_bounds: tuple[float, float],
    r_s_bounds: tuple[float, float],
) -> FitResult:
    r = np.asarray(r_kpc, dtype=float)
    obs = np.asarray(v_obs_kms, dtype=float)
    err = np.asarray(v_err_kms, dtype=float)
    vbar = np.asarray(v_bar_kms, dtype=float)
    bounds = {"rho_s": rho_s_bounds, "r_s": r_s_bounds}

    if np.any(r <= 0) or np.any(err <= 0):
        return FitResult("nfw", False, "invalid_input", 2, {}, bounds, np.full_like(obs, np.nan))

    lo = np.array([rho_s_bounds[0], r_s_bounds[0]], dtype=float)
    hi = np.array([rho_s_bounds[1], r_s_bounds[1]], dtype=float)
    x0 = np.sqrt(lo * hi)

    def residual_fn(theta: np.ndarray) -> np.ndarray:
        params = NFWParams(rho_s=float(theta[0]), r_s=float(theta[1]))
        v_halo = nfw_velocity(r, params)
        v_model = np.sqrt(np.maximum(vbar**2 + v_halo**2, 0.0))
        return _weighted_residual(obs, v_model, err)

    try:
        res = least_squares(residual_fn, x0=x0, bounds=(lo, hi), method="trf")
        if (not res.success) or np.any(~np.isfinite(res.x)):
            return FitResult("nfw", False, f"fit_failed:{res.status}", 2, {}, bounds, np.full_like(obs, np.nan))
        p = NFWParams(rho_s=float(res.x[0]), r_s=float(res.x[1]))
        v_halo = nfw_velocity(r, p)
        v_model = np.sqrt(np.maximum(vbar**2 + v_halo**2, 0.0))
        return FitResult(
            "nfw",
            True,
            f"ok:{res.status}",
            2,
            {"rho_s": p.rho_s, "r_s": p.r_s},
            bounds,
            v_model,
        )
    except Exception as exc:  # noqa: BLE001
        return FitResult("nfw", False, f"exception:{exc}", 2, {}, bounds, np.full_like(obs, np.nan))


def fit_burkert_baseline(
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    *,
    rho0_bounds: tuple[float, float],
    r0_bounds: tuple[float, float],
) -> FitResult:
    r = np.asarray(r_kpc, dtype=float)
    obs = np.asarray(v_obs_kms, dtype=float)
    err = np.asarray(v_err_kms, dtype=float)
    vbar = np.asarray(v_bar_kms, dtype=float)
    bounds = {"rho_0": rho0_bounds, "r_0": r0_bounds}

    if np.any(r <= 0) or np.any(err <= 0):
        return FitResult("burkert", False, "invalid_input", 2, {}, bounds, np.full_like(obs, np.nan))

    lo = np.array([rho0_bounds[0], r0_bounds[0]], dtype=float)
    hi = np.array([rho0_bounds[1], r0_bounds[1]], dtype=float)
    x0 = np.sqrt(lo * hi)

    def residual_fn(theta: np.ndarray) -> np.ndarray:
        params = BurkertParams(rho0=float(theta[0]), r0=float(theta[1]))
        v_halo = burkert_velocity(r, params)
        v_model = np.sqrt(np.maximum(vbar**2 + v_halo**2, 0.0))
        return _weighted_residual(obs, v_model, err)

    try:
        res = least_squares(residual_fn, x0=x0, bounds=(lo, hi), method="trf")
        if (not res.success) or np.any(~np.isfinite(res.x)):
            return FitResult("burkert", False, f"fit_failed:{res.status}", 2, {}, bounds, np.full_like(obs, np.nan))
        p = BurkertParams(rho0=float(res.x[0]), r0=float(res.x[1]))
        v_halo = burkert_velocity(r, p)
        v_model = np.sqrt(np.maximum(vbar**2 + v_halo**2, 0.0))
        return FitResult(
            "burkert",
            True,
            f"ok:{res.status}",
            2,
            {"rho_0": p.rho0, "r_0": p.r0},
            bounds,
            v_model,
        )
    except Exception as exc:  # noqa: BLE001
        return FitResult("burkert", False, f"exception:{exc}", 2, {}, bounds, np.full_like(obs, np.nan))


def log10_to_physical_parameter(log10_value: float) -> float:
    """Transform a log10 halo parameter to its positive physical value."""
    return float(10.0 ** float(log10_value))


def physical_to_log10_parameter(value: float) -> float:
    if value <= 0:
        raise ValueError("physical parameter must be positive for log10 transform")
    return float(np.log10(value))


def log10_bounds_to_physical(bounds_log10: tuple[float, float]) -> tuple[float, float]:
    lo, hi = bounds_log10
    return (log10_to_physical_parameter(lo), log10_to_physical_parameter(hi))


def deterministic_log_multistart_guesses(
    log_rho_bounds: tuple[float, float],
    log_r_bounds: tuple[float, float],
) -> list[np.ndarray]:
    """Deterministic log-space initial guesses: low-ρ/large-r, medium, high-ρ/small-r."""
    lo_rho, hi_rho = log_rho_bounds
    lo_r, hi_r = log_r_bounds
    span_rho = hi_rho - lo_rho
    span_r = hi_r - lo_r
    inset = 0.05
    return [
        np.array([lo_rho + inset * span_rho, hi_r - inset * span_r], dtype=float),
        np.array([lo_rho + 0.5 * span_rho, lo_r + 0.5 * span_r], dtype=float),
        np.array([hi_rho - inset * span_rho, lo_r + inset * span_r], dtype=float),
    ]


def data_informed_log_guess(
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    log_rho_bounds: tuple[float, float],
    log_r_bounds: tuple[float, float],
) -> np.ndarray:
    """One data-informed log-space start from outer excess over baryons."""
    r = np.asarray(r_kpc, dtype=float)
    excess_sq = np.maximum(np.asarray(v_obs_kms, dtype=float) ** 2 - np.asarray(v_bar_kms, dtype=float) ** 2, 0.0)
    if np.any(excess_sq > 0):
        idx = int(np.argmax(excess_sq))
        r_eff = float(r[idx])
        log_r = float(np.clip(np.log10(max(r_eff, 0.05)), log_r_bounds[0], log_r_bounds[1]))
        frac = float(np.clip(excess_sq[idx] / max(np.max(excess_sq), 1.0), 0.05, 1.0))
        log_rho = float(log_rho_bounds[0] + frac * (log_rho_bounds[1] - log_rho_bounds[0]))
        return np.array([log_rho, log_r], dtype=float)
    return np.array(
        [
            0.5 * (log_rho_bounds[0] + log_rho_bounds[1]),
            0.5 * (log_r_bounds[0] + log_r_bounds[1]),
        ],
        dtype=float,
    )


def _fit_halo_log_multistart(
    model_name: str,
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    *,
    log_rho_bounds: tuple[float, float],
    log_r_bounds: tuple[float, float],
    build_params,
    halo_velocity,
    rho_key: str,
    r_key: str,
) -> FitResult:
    r = np.asarray(r_kpc, dtype=float)
    obs = np.asarray(v_obs_kms, dtype=float)
    err = np.asarray(v_err_kms, dtype=float)
    vbar = np.asarray(v_bar_kms, dtype=float)
    phys_rho_bounds = log10_bounds_to_physical(log_rho_bounds)
    phys_r_bounds = log10_bounds_to_physical(log_r_bounds)
    log_rho_name = "log10_rho_s" if model_name == "nfw" else "log10_rho_0"
    log_r_name = "log10_r_s" if model_name == "nfw" else "log10_r_0"
    bounds = {
        rho_key: phys_rho_bounds,
        r_key: phys_r_bounds,
        log_rho_name: log_rho_bounds,
        log_r_name: log_r_bounds,
    }

    if np.any(r <= 0) or np.any(err <= 0):
        return FitResult(
            model_name,
            False,
            "invalid_input",
            2,
            {},
            bounds,
            np.full_like(obs, np.nan),
            log_params={},
            fitting_mode="log_multistart",
        )

    lo = np.array([log_rho_bounds[0], log_r_bounds[0]], dtype=float)
    hi = np.array([log_rho_bounds[1], log_r_bounds[1]], dtype=float)
    starts = deterministic_log_multistart_guesses(log_rho_bounds, log_r_bounds)
    starts.append(data_informed_log_guess(r, obs, vbar, log_rho_bounds, log_r_bounds))

    def residual_fn(theta: np.ndarray) -> np.ndarray:
        params = build_params(float(theta[0]), float(theta[1]))
        v_halo = halo_velocity(r, params)
        v_model = np.sqrt(np.maximum(vbar**2 + v_halo**2, 0.0))
        return _weighted_residual(obs, v_model, err)

    best_x: np.ndarray | None = None
    best_chi2 = np.inf
    best_status = ""
    n_success = 0
    for x0 in starts:
        x0 = np.clip(x0, lo, hi)
        try:
            res = least_squares(residual_fn, x0=x0, bounds=(lo, hi), method="trf")
        except Exception:
            continue
        if not res.success or np.any(~np.isfinite(res.x)):
            continue
        params = build_params(float(res.x[0]), float(res.x[1]))
        v_halo = halo_velocity(r, params)
        v_model = np.sqrt(np.maximum(vbar**2 + v_halo**2, 0.0))
        if np.any(~np.isfinite(v_model)):
            continue
        chi2 = chi_square(obs, v_model, err)
        n_success += 1
        if chi2 < best_chi2:
            best_chi2 = chi2
            best_x = res.x
            best_status = f"ok:{res.status}"

    if best_x is None:
        return FitResult(
            model_name,
            False,
            "multistart_fit_failed",
            2,
            {},
            bounds,
            np.full_like(obs, np.nan),
            log_params={},
            fitting_mode="log_multistart",
            n_starts_attempted=len(starts),
            n_starts_successful=0,
        )

    p = build_params(float(best_x[0]), float(best_x[1]))
    v_halo = halo_velocity(r, p)
    v_model = np.sqrt(np.maximum(vbar**2 + v_halo**2, 0.0))
    if model_name == "nfw":
        phys = {"rho_s_msun_kpc3": p.rho_s, "r_s_kpc": p.r_s}
        logp = {"log10_rho_s": float(best_x[0]), "log10_r_s": float(best_x[1])}
    else:
        phys = {"rho_0_msun_kpc3": p.rho0, "r_0_kpc": p.r0}
        logp = {"log10_rho_0": float(best_x[0]), "log10_r_0": float(best_x[1])}

    return FitResult(
        model_name,
        True,
        best_status,
        2,
        phys,
        bounds,
        v_model,
        log_params=logp,
        fitting_mode="log_multistart",
        chi_square=float(best_chi2),
        n_starts_attempted=len(starts),
        n_starts_successful=n_success,
    )


def fit_nfw_baseline_log(
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    *,
    log10_rho_s_bounds: tuple[float, float],
    log10_r_s_bounds: tuple[float, float],
) -> FitResult:
    return _fit_halo_log_multistart(
        "nfw",
        r_kpc,
        v_obs_kms,
        v_err_kms,
        v_bar_kms,
        log_rho_bounds=log10_rho_s_bounds,
        log_r_bounds=log10_r_s_bounds,
        build_params=nfw_params_from_log10,
        halo_velocity=nfw_velocity,
        rho_key="rho_s",
        r_key="r_s",
    )


def fit_burkert_baseline_log(
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    *,
    log10_rho_0_bounds: tuple[float, float],
    log10_r_0_bounds: tuple[float, float],
) -> FitResult:
    return _fit_halo_log_multistart(
        "burkert",
        r_kpc,
        v_obs_kms,
        v_err_kms,
        v_bar_kms,
        log_rho_bounds=log10_rho_0_bounds,
        log_r_bounds=log10_r_0_bounds,
        build_params=burkert_params_from_log10,
        halo_velocity=burkert_velocity,
        rho_key="rho_0",
        r_key="r_0",
    )


def _audit_density_value(row: pd.Series, model: str) -> float:
    if model == "nfw":
        for key in ("rho_s_msun_kpc3", "rho_s"):
            if key in row and np.isfinite(row.get(key, np.nan)):
                return float(row[key])
    else:
        for key in ("rho_0_msun_kpc3", "rho_0"):
            if key in row and np.isfinite(row.get(key, np.nan)):
                return float(row[key])
    return float("nan")


def _audit_scale_value(row: pd.Series, model: str) -> float:
    if model == "nfw":
        for key in ("r_s_kpc", "r_s"):
            if key in row and np.isfinite(row.get(key, np.nan)):
                return float(row[key])
    else:
        for key in ("r_0_kpc", "r_0"):
            if key in row and np.isfinite(row.get(key, np.nan)):
                return float(row[key])
    return float("nan")


def _audit_log_density(row: pd.Series, model: str) -> float:
    key = "log10_rho_s" if model == "nfw" else "log10_rho_0"
    if key in row and np.isfinite(row.get(key, np.nan)):
        return float(row[key])
    val = _audit_density_value(row, model)
    return float(np.log10(val)) if np.isfinite(val) and val > 0 else float("nan")


def _audit_log_scale(row: pd.Series, model: str) -> float:
    key = "log10_r_s" if model == "nfw" else "log10_r_0"
    if key in row and np.isfinite(row.get(key, np.nan)):
        return float(row[key])
    val = _audit_scale_value(row, model)
    return float(np.log10(val)) if np.isfinite(val) and val > 0 else float("nan")


@dataclass(frozen=True)
class BaselineAuditConfig:
    boundary_tolerance_fraction: float = 0.01
    high_reduced_chi_square_threshold: float = 5.0
    very_high_reduced_chi_square_threshold: float = 20.0
    poor_rmse_fraction_of_median_v_obs: float = 0.20


def parse_bounds_tuple(value: object) -> tuple[float, float] | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, tuple):
        return (float(value[0]), float(value[1]))
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    parsed = ast.literal_eval(text)
    if not isinstance(parsed, (tuple, list)) or len(parsed) != 2:
        raise ValueError(f"cannot parse bounds tuple from {value!r}")
    return (float(parsed[0]), float(parsed[1]))


def _at_lower_bound(value: float, bounds: tuple[float, float], tol_fraction: float) -> bool:
    lo, hi = bounds
    span = hi - lo
    if span <= 0:
        return False
    return value <= lo + tol_fraction * span


def _at_upper_bound(value: float, bounds: tuple[float, float], tol_fraction: float) -> bool:
    lo, hi = bounds
    span = hi - lo
    if span <= 0:
        return False
    return value >= hi - tol_fraction * span


def _model_status(
    *,
    boundary_limited: bool,
    high_chi: bool,
) -> str:
    if boundary_limited and high_chi:
        return "boundary_limited_and_high_chi_square"
    if boundary_limited:
        return "boundary_limited"
    if high_chi:
        return "high_chi_square"
    return "ok"


def audit_baseline_fits(
    comparison_df: pd.DataFrame,
    parameters_df: pd.DataFrame,
    *,
    median_v_obs_by_galaxy: dict[str, float] | None = None,
    config: BaselineAuditConfig | None = None,
) -> pd.DataFrame:
    """Audit Phase 3A baseline fits for boundary hits and poor goodness-of-fit flags."""
    cfg = config or BaselineAuditConfig()
    param_cols = [
        c
        for c in (
            "rho_s",
            "r_s",
            "rho_s_msun_kpc3",
            "r_s_kpc",
            "log10_rho_s",
            "log10_r_s",
            "rho_s_bounds",
            "r_s_bounds",
            "log10_rho_s_bounds",
            "log10_r_s_bounds",
            "rho_0",
            "r_0",
            "rho_0_msun_kpc3",
            "r_0_kpc",
            "log10_rho_0",
            "log10_r_0",
            "rho_0_bounds",
            "r_0_bounds",
            "log10_rho_0_bounds",
            "log10_r_0_bounds",
        )
        if c in parameters_df.columns
    ]
    if parameters_df.empty or not {"galaxy_id", "model_name"}.issubset(parameters_df.columns):
        merged = comparison_df.copy()
        for col in param_cols:
            merged[col] = np.nan
    else:
        merged = comparison_df.merge(
            parameters_df[["galaxy_id", "model_name", *param_cols]],
            on=["galaxy_id", "model_name"],
            how="left",
        )
    rows: list[dict[str, object]] = []

    for _, comp in merged.iterrows():
        gid = str(comp["galaxy_id"])
        model = str(comp["model_name"])
        med_v = None if median_v_obs_by_galaxy is None else median_v_obs_by_galaxy.get(gid)

        row: dict[str, object] = {
            "galaxy_id": gid,
            "model_name": model,
            "fit_success": bool(comp.get("fit_success", False)),
            "fit_status": comp.get("fit_status", ""),
            "rmse_kms": float(comp["rmse_kms"]),
            "reduced_chi_square": float(comp["reduced_chi_square"]),
            "aic": float(comp["aic"]),
            "bic": float(comp["bic"]),
            "rho_s": _audit_density_value(comp, "nfw") if model == "nfw" else np.nan,
            "r_s": _audit_scale_value(comp, "nfw") if model == "nfw" else np.nan,
            "rho_0": _audit_density_value(comp, "burkert") if model == "burkert" else np.nan,
            "r_0": _audit_scale_value(comp, "burkert") if model == "burkert" else np.nan,
            "log10_rho_s": comp.get("log10_rho_s", np.nan),
            "log10_r_s": comp.get("log10_r_s", np.nan),
            "log10_rho_0": comp.get("log10_rho_0", np.nan),
            "log10_r_0": comp.get("log10_r_0", np.nan),
            "rho_s_lower_bound": False,
            "rho_s_upper_bound": False,
            "r_s_lower_bound": False,
            "r_s_upper_bound": False,
            "rho_0_lower_bound": False,
            "rho_0_upper_bound": False,
            "r_0_lower_bound": False,
            "r_0_upper_bound": False,
        }

        if model == "nfw":
            log_rho_bounds = parse_bounds_tuple(comp.get("log10_rho_s_bounds"))
            log_rs_bounds = parse_bounds_tuple(comp.get("log10_r_s_bounds"))
            rho_bounds = parse_bounds_tuple(comp.get("rho_s_bounds"))
            rs_bounds = parse_bounds_tuple(comp.get("r_s_bounds"))
            log_rho = _audit_log_density(comp, "nfw")
            log_rs = _audit_log_scale(comp, "nfw")
            if log_rho_bounds and np.isfinite(log_rho):
                row["rho_s_lower_bound"] = _at_lower_bound(log_rho, log_rho_bounds, cfg.boundary_tolerance_fraction)
                row["rho_s_upper_bound"] = _at_upper_bound(log_rho, log_rho_bounds, cfg.boundary_tolerance_fraction)
            elif rho_bounds and np.isfinite(row["rho_s"]):
                row["rho_s_lower_bound"] = _at_lower_bound(float(row["rho_s"]), rho_bounds, cfg.boundary_tolerance_fraction)
                row["rho_s_upper_bound"] = _at_upper_bound(float(row["rho_s"]), rho_bounds, cfg.boundary_tolerance_fraction)
            if log_rs_bounds and np.isfinite(log_rs):
                row["r_s_lower_bound"] = _at_lower_bound(log_rs, log_rs_bounds, cfg.boundary_tolerance_fraction)
                row["r_s_upper_bound"] = _at_upper_bound(log_rs, log_rs_bounds, cfg.boundary_tolerance_fraction)
            elif rs_bounds and np.isfinite(row["r_s"]):
                row["r_s_lower_bound"] = _at_lower_bound(float(row["r_s"]), rs_bounds, cfg.boundary_tolerance_fraction)
                row["r_s_upper_bound"] = _at_upper_bound(float(row["r_s"]), rs_bounds, cfg.boundary_tolerance_fraction)
        elif model == "burkert":
            log_rho0_bounds = parse_bounds_tuple(comp.get("log10_rho_0_bounds"))
            log_r0_bounds = parse_bounds_tuple(comp.get("log10_r_0_bounds"))
            rho0_bounds = parse_bounds_tuple(comp.get("rho_0_bounds"))
            r0_bounds = parse_bounds_tuple(comp.get("r_0_bounds"))
            log_rho0 = _audit_log_density(comp, "burkert")
            log_r0 = _audit_log_scale(comp, "burkert")
            if log_rho0_bounds and np.isfinite(log_rho0):
                row["rho_0_lower_bound"] = _at_lower_bound(log_rho0, log_rho0_bounds, cfg.boundary_tolerance_fraction)
                row["rho_0_upper_bound"] = _at_upper_bound(log_rho0, log_rho0_bounds, cfg.boundary_tolerance_fraction)
            elif rho0_bounds and np.isfinite(row["rho_0"]):
                row["rho_0_lower_bound"] = _at_lower_bound(float(row["rho_0"]), rho0_bounds, cfg.boundary_tolerance_fraction)
                row["rho_0_upper_bound"] = _at_upper_bound(float(row["rho_0"]), rho0_bounds, cfg.boundary_tolerance_fraction)
            if log_r0_bounds and np.isfinite(log_r0):
                row["r_0_lower_bound"] = _at_lower_bound(log_r0, log_r0_bounds, cfg.boundary_tolerance_fraction)
                row["r_0_upper_bound"] = _at_upper_bound(log_r0, log_r0_bounds, cfg.boundary_tolerance_fraction)
            elif r0_bounds and np.isfinite(row["r_0"]):
                row["r_0_lower_bound"] = _at_lower_bound(float(row["r_0"]), r0_bounds, cfg.boundary_tolerance_fraction)
                row["r_0_upper_bound"] = _at_upper_bound(float(row["r_0"]), r0_bounds, cfg.boundary_tolerance_fraction)

        reduced_chi2 = float(row["reduced_chi_square"])
        row["high_reduced_chi_square"] = reduced_chi2 > cfg.high_reduced_chi_square_threshold
        row["very_high_reduced_chi_square"] = reduced_chi2 > cfg.very_high_reduced_chi_square_threshold
        row["poor_rmse_relative_to_velocity"] = (
            poor_rmse_relative_to_median_velocity(
                float(row["rmse_kms"]),
                float(med_v),
                fraction_threshold=cfg.poor_rmse_fraction_of_median_v_obs,
            )
            if med_v is not None
            else False
        )

        boundary_flags = [
            row["rho_s_lower_bound"],
            row["rho_s_upper_bound"],
            row["r_s_lower_bound"],
            row["r_s_upper_bound"],
            row["rho_0_lower_bound"],
            row["rho_0_upper_bound"],
            row["r_0_lower_bound"],
            row["r_0_upper_bound"],
        ]
        boundary_limited = any(bool(x) for x in boundary_flags)
        high_chi = bool(row["high_reduced_chi_square"] or row["very_high_reduced_chi_square"])
        row["model_status"] = _model_status(boundary_limited=boundary_limited, high_chi=high_chi)
        rows.append(row)

    audit_df = pd.DataFrame(rows)

    best_rmse = audit_df.groupby("galaxy_id")["rmse_kms"].transform("min")
    best_aic = audit_df.groupby("galaxy_id")["aic"].transform("min")
    best_bic = audit_df.groupby("galaxy_id")["bic"].transform("min")
    audit_df["best_rmse_in_galaxy"] = audit_df["rmse_kms"] <= best_rmse + 1.0e-12
    audit_df["best_aic_in_galaxy"] = audit_df["aic"] <= best_aic + 1.0e-12
    audit_df["best_bic_in_galaxy"] = audit_df["bic"] <= best_bic + 1.0e-12

    return audit_df


def summarize_baseline_audit(audit_df: pd.DataFrame) -> dict[str, object]:
    """Build summary dict for markdown report generation."""
    halo = audit_df[audit_df["model_name"].isin(["nfw", "burkert"])]
    nfw_only = audit_df[audit_df["model_name"] == "nfw"]
    burkert_only = audit_df[audit_df["model_name"] == "burkert"]

    nfw_best_rmse = bool((nfw_only.groupby("galaxy_id")["best_rmse_in_galaxy"].max() == 1).all())
    nfw_best_aic = bool((nfw_only.groupby("galaxy_id")["best_aic_in_galaxy"].max() == 1).all())
    nfw_best_bic = bool((nfw_only.groupby("galaxy_id")["best_bic_in_galaxy"].max() == 1).all())

    return {
        "nfw_best_rmse_all_galaxies": nfw_best_rmse,
        "nfw_best_aic_all_galaxies": nfw_best_aic,
        "nfw_best_bic_all_galaxies": nfw_best_bic,
        "burkert_boundary_limited_rows": int((burkert_only["model_status"].str.contains("boundary")).sum()),
        "burkert_total_rows": len(burkert_only),
        "nfw_boundary_limited_rows": int((nfw_only["model_status"].str.contains("boundary")).sum()),
        "high_chi_rows": int(audit_df["high_reduced_chi_square"].sum()),
        "very_high_chi_rows": int(audit_df["very_high_reduced_chi_square"].sum()),
        "boundary_limited_rows": int(audit_df["model_status"].str.contains("boundary").sum()),
        "status_counts": audit_df["model_status"].value_counts().to_dict(),
    }


def _status_has_boundary(status: str) -> bool:
    return "boundary" in str(status)


def _status_has_high_chi(status: str) -> bool:
    return "high_chi" in str(status)


def build_legacy_vs_refit_delta(
    legacy_comparison: pd.DataFrame,
    refit_comparison: pd.DataFrame,
    legacy_audit: pd.DataFrame,
    refit_audit: pd.DataFrame,
) -> pd.DataFrame:
    """Side-by-side legacy Phase 3A vs robust refit metrics and audit status."""
    keys = ["galaxy_id", "model_name"]
    leg = legacy_comparison.merge(
        legacy_audit[keys + ["model_status", "high_reduced_chi_square"]],
        on=keys,
        how="inner",
        suffixes=("", "_audit"),
    )
    ref = refit_comparison.merge(
        refit_audit[keys + ["model_status", "high_reduced_chi_square"]],
        on=keys,
        how="inner",
        suffixes=("", "_audit"),
    )
    merged = leg.merge(
        ref,
        on=keys,
        suffixes=("_legacy", "_refit"),
    )
    rows: list[dict[str, object]] = []
    for _, row in merged.iterrows():
        legacy_status = str(row["model_status_legacy"])
        refit_status = str(row["model_status_refit"])
        legacy_high = bool(row.get("high_reduced_chi_square_legacy", False))
        refit_high = bool(row.get("high_reduced_chi_square_refit", False))
        rmse_leg = float(row["rmse_kms_legacy"])
        rmse_ref = float(row["rmse_kms_refit"])
        aic_leg = float(row["aic_legacy"])
        aic_ref = float(row["aic_refit"])
        bic_leg = float(row["bic_legacy"])
        bic_ref = float(row["bic_refit"])
        rows.append(
            {
                "galaxy_id": row["galaxy_id"],
                "model_name": row["model_name"],
                "rmse_legacy": rmse_leg,
                "rmse_refit": rmse_ref,
                "delta_rmse": rmse_ref - rmse_leg,
                "aic_legacy": aic_leg,
                "aic_refit": aic_ref,
                "delta_aic": aic_ref - aic_leg,
                "bic_legacy": bic_leg,
                "bic_refit": bic_ref,
                "delta_bic": bic_ref - bic_leg,
                "legacy_model_status": legacy_status,
                "refit_model_status": refit_status,
                "boundary_status_improved": _status_has_boundary(legacy_status)
                and not _status_has_boundary(refit_status),
                "chi_square_status_improved": (legacy_high and not refit_high)
                or (
                    float(row["reduced_chi_square_refit"]) < float(row["reduced_chi_square_legacy"])
                    and not refit_high
                ),
            }
        )
    return pd.DataFrame(rows)


def fit_mond_fixed_a0(
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    *,
    a0_ms2: float,
) -> FitResult:
    from .mond import A0_DEFAULT_MS2, mond_fixed_a0_velocity_kms

    r = np.asarray(r_kpc, dtype=float)
    obs = np.asarray(v_obs_kms, dtype=float)
    err = np.asarray(v_err_kms, dtype=float)
    vbar = np.asarray(v_bar_kms, dtype=float)
    a0 = float(a0_ms2)

    if np.any(r <= 0) or np.any(err <= 0):
        return FitResult(
            "mond_fixed_a0_simple",
            False,
            "invalid_input",
            0,
            {},
            {},
            np.full_like(obs, np.nan),
            fitting_mode="mond_fixed_a0",
        )

    try:
        v_model = mond_fixed_a0_velocity_kms(r, vbar, a0_ms2=a0)
        if np.any(~np.isfinite(v_model)):
            raise ValueError("non-finite MOND velocities")
        chi2 = chi_square(obs, v_model, err)
        return FitResult(
            "mond_fixed_a0_simple",
            True,
            "fixed_a0",
            0,
            {"a0_m_s2": a0},
            {"a0_m_s2": (a0, a0)},
            v_model,
            log_params={"log10_a0_m_s2": float(np.log10(a0))},
            fitting_mode="mond_fixed_a0",
            chi_square=float(chi2),
        )
    except Exception as exc:  # noqa: BLE001
        return FitResult(
            "mond_fixed_a0_simple",
            False,
            f"exception:{exc}",
            0,
            {},
            {},
            np.full_like(obs, np.nan),
            fitting_mode="mond_fixed_a0",
        )


def fit_mond_a0_simple(
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    *,
    log10_a0_bounds: tuple[float, float],
    log10_a0_initial: float | None = None,
) -> FitResult:
    from .mond import A0_DEFAULT_MS2, log10_a0_to_a0, mond_fit_a0_velocity_kms

    r = np.asarray(r_kpc, dtype=float)
    obs = np.asarray(v_obs_kms, dtype=float)
    err = np.asarray(v_err_kms, dtype=float)
    vbar = np.asarray(v_bar_kms, dtype=float)
    lo, hi = log10_a0_bounds
    bounds = {"log10_a0_m_s2": (lo, hi), "a0_m_s2": log10_bounds_to_physical((lo, hi))}

    if np.any(r <= 0) or np.any(err <= 0):
        return FitResult(
            "mond_fit_a0_simple",
            False,
            "invalid_input",
            1,
            {},
            bounds,
            np.full_like(obs, np.nan),
            fitting_mode="mond_fit_log10_a0",
        )

    x0 = np.array([log10_a0_initial if log10_a0_initial is not None else np.log10(A0_DEFAULT_MS2)])
    x0 = np.clip(x0, lo, hi)

    def residual_fn(theta: np.ndarray) -> np.ndarray:
        v_model = mond_fit_a0_velocity_kms(r, vbar, float(theta[0]))
        return _weighted_residual(obs, v_model, err)

    try:
        res = least_squares(
            residual_fn,
            x0=x0,
            bounds=([lo], [hi]),
            method="trf",
        )
        if not res.success or np.any(~np.isfinite(res.x)):
            return FitResult(
                "mond_fit_a0_simple",
                False,
                f"fit_failed:{res.status}",
                1,
                {},
                bounds,
                np.full_like(obs, np.nan),
                fitting_mode="mond_fit_log10_a0",
            )
        log10_a0 = float(res.x[0])
        a0 = log10_a0_to_a0(log10_a0)
        v_model = mond_fit_a0_velocity_kms(r, vbar, log10_a0)
        chi2 = chi_square(obs, v_model, err)
        return FitResult(
            "mond_fit_a0_simple",
            True,
            f"ok:{res.status}",
            1,
            {"a0_m_s2": a0},
            bounds,
            v_model,
            log_params={"log10_a0_m_s2": log10_a0},
            fitting_mode="mond_fit_log10_a0",
            chi_square=float(chi2),
        )
    except Exception as exc:  # noqa: BLE001
        return FitResult(
            "mond_fit_a0_simple",
            False,
            f"exception:{exc}",
            1,
            {},
            bounds,
            np.full_like(obs, np.nan),
            fitting_mode="mond_fit_log10_a0",
        )


def fit_rar_fixed(
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    *,
    g_dagger_ms2: float,
) -> FitResult:
    from .mond import rar_fixed_velocity_kms

    r = np.asarray(r_kpc, dtype=float)
    obs = np.asarray(v_obs_kms, dtype=float)
    err = np.asarray(v_err_kms, dtype=float)
    vbar = np.asarray(v_bar_kms, dtype=float)
    g_d = float(g_dagger_ms2)

    if np.any(r <= 0) or np.any(err <= 0):
        return FitResult(
            "rar_fixed",
            False,
            "invalid_input",
            0,
            {},
            {},
            np.full_like(obs, np.nan),
            fitting_mode="rar_fixed",
        )

    try:
        v_model = rar_fixed_velocity_kms(r, vbar, g_dagger_ms2=g_d)
        if np.any(~np.isfinite(v_model)):
            raise ValueError("non-finite RAR velocities")
        chi2 = chi_square(obs, v_model, err)
        return FitResult(
            "rar_fixed",
            True,
            "fixed_g_dagger",
            0,
            {"g_dagger_m_s2": g_d},
            {"g_dagger_m_s2": (g_d, g_d)},
            v_model,
            fitting_mode="rar_fixed",
            chi_square=float(chi2),
        )
    except Exception as exc:  # noqa: BLE001
        return FitResult(
            "rar_fixed",
            False,
            f"exception:{exc}",
            1,
            {},
            {},
            np.full_like(obs, np.nan),
            fitting_mode="rar_fixed",
        )


def fit_tdf_knot_baseline(
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    *,
    model_name: str,
    knot_r_kpc: np.ndarray,
    initial_knot_dtaudr: np.ndarray,
    dtaudr_bounds: tuple[float, float],
    k_tau: float,
    negative_v2_penalty: float = 1000.0,
    train_mask: np.ndarray | None = None,
) -> FitResult:
    from .tdf_knot import n_knots_for_model, tdf_velocity_kms, tdf_velocity_squared_kms2

    r = np.asarray(r_kpc, dtype=float)
    obs = np.asarray(v_obs_kms, dtype=float)
    err = np.asarray(v_err_kms, dtype=float)
    vbar = np.asarray(v_bar_kms, dtype=float)
    n_params = n_knots_for_model(model_name)
    lo_b, hi_b = dtaudr_bounds
    lo = np.full(n_params, lo_b, dtype=float)
    hi = np.full(n_params, hi_b, dtype=float)
    bounds = {"dtaudr_knot": (lo_b, hi_b)}

    if np.any(r <= 0) or np.any(err <= 0):
        return FitResult(
            model_name,
            False,
            "invalid_input",
            n_params,
            {},
            bounds,
            np.full_like(obs, np.nan),
            fitting_mode="tdf_knot",
        )

    x0 = np.clip(np.asarray(initial_knot_dtaudr, dtype=float), lo, hi)
    if train_mask is None:
        fit_mask = np.ones(len(r), dtype=bool)
    else:
        fit_mask = np.asarray(train_mask, dtype=bool)
        if fit_mask.shape[0] != r.shape[0]:
            raise ValueError("train_mask length must match r_kpc")

    def residual_fn(theta: np.ndarray) -> np.ndarray:
        v2 = tdf_velocity_squared_kms2(r, vbar, knot_r_kpc, theta, k_tau=k_tau)
        v_model, _ = tdf_velocity_kms(r, vbar, knot_r_kpc, theta, k_tau=k_tau)
        base = _weighted_residual(obs[fit_mask], v_model[fit_mask], err[fit_mask])
        penalty = np.where(v2[fit_mask] < 0.0, np.sqrt(negative_v2_penalty), 0.0)
        return base + penalty

    try:
        res = least_squares(residual_fn, x0=x0, bounds=(lo, hi), method="trf")
        if not res.success or np.any(~np.isfinite(res.x)):
            return FitResult(
                model_name,
                False,
                f"fit_failed:{res.status}",
                n_params,
                {},
                bounds,
                np.full_like(obs, np.nan),
                fitting_mode="tdf_knot",
            )
        theta = res.x
        v_model, v2 = tdf_velocity_kms(r, vbar, knot_r_kpc, theta, k_tau=k_tau)
        status = f"ok:{res.status}"
        if np.any(v2 < 0):
            status = f"{status};negative_v2_regions"
        chi2 = chi_square(obs, v_model, err)
        if np.any(v2 < 0):
            chi2 += float(np.sum(v2 < 0)) * negative_v2_penalty
        param_dict = {f"knot_{i}_dtaudr": float(theta[i]) for i in range(n_params)}
        return FitResult(
            model_name,
            True,
            status,
            n_params,
            param_dict,
            bounds,
            v_model,
            fitting_mode="tdf_knot",
            chi_square=float(chi2),
        )
    except Exception as exc:  # noqa: BLE001
        return FitResult(
            model_name,
            False,
            f"exception:{exc}",
            n_params,
            {},
            bounds,
            np.full_like(obs, np.nan),
            fitting_mode="tdf_knot",
        )
