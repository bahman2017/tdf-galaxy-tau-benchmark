from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.metrics.comparison import chi_square, rmse, safe_reduced_chi_square
from tdf_galaxy_tau.metrics.information_criteria import aic, bic, model_parameter_count
from tdf_galaxy_tau.models.fitting import fit_mond_a0_simple, fit_mond_fixed_a0, fit_rar_fixed
from tdf_galaxy_tau.models.mond import A0_DEFAULT_MS2
from tdf_galaxy_tau.reconstruction.radial_tau import load_selected_galaxy_ids

TABLE_COMPARISON = Path("outputs/tables/sparc_mond_model_comparison.csv")
TABLE_PARAMS = Path("outputs/tables/sparc_mond_fit_parameters.csv")
REPORT_PATH = Path("outputs/reports/sparc_mond_baseline_report.md")


def _load_config(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _metrics_row(
    galaxy_id: str,
    model_name: str,
    n_points: int,
    v_obs,
    v_model,
    v_err,
    *,
    fit_success: bool,
    fit_status: str,
    data_source: str,
    data_mode: str,
) -> dict:
    n_params = model_parameter_count(model_name)
    chi2 = chi_square(v_obs, v_model, v_err)
    return {
        "model_name": model_name,
        "galaxy_id": galaxy_id,
        "n_points": n_points,
        "n_parameters": n_params,
        "rmse_kms": rmse(v_obs, v_model),
        "chi_square": chi2,
        "reduced_chi_square": safe_reduced_chi_square(chi2, n_points, n_params),
        "aic": aic(chi2, n_params),
        "bic": bic(chi2, n_points, n_params),
        "fit_success": bool(fit_success),
        "fit_status": fit_status,
        "data_source": data_source,
        "data_mode": data_mode,
        "comparison_stage": "phase_3m_mond_rar_baseline",
    }


def _param_row(
    galaxy_id: str,
    model_name: str,
    fit: object,
    *,
    a0_fixed_or_fitted: str,
    lower_bound: float | None,
    upper_bound: float | None,
) -> dict:
    a0 = fit.params.get("a0_m_s2") or fit.params.get("g_dagger_m_s2")
    log10_a0 = None
    if fit.log_params:
        log10_a0 = fit.log_params.get("log10_a0_m_s2")
    elif a0 is not None and a0 > 0:
        log10_a0 = float(np.log10(a0))
    return {
        "galaxy_id": galaxy_id,
        "model_name": model_name,
        "a0_m_s2": a0,
        "log10_a0_m_s2": log10_a0,
        "a0_fixed_or_fitted": a0_fixed_or_fitted,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "n_parameters": fit.n_parameters,
        "fit_success": fit.fit_success,
        "fit_status": fit.fit_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fit MOND/RAR baselines on selected SPARC subset")
    parser.add_argument("--data", required=True)
    parser.add_argument("--subset", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    data = pd.read_csv(args.data)
    selected_ids = load_selected_galaxy_ids(args.subset)
    cfg = _load_config(Path(args.config))
    mond_cfg = cfg.get("mond", {})
    a0_fixed = float(mond_cfg.get("a0_fixed_m_s2", A0_DEFAULT_MS2))
    g_dagger = float(mond_cfg.get("g_dagger_fixed_m_s2", A0_DEFAULT_MS2))
    log_bounds = tuple(mond_cfg.get("log10_a0_bounds_m_s2", [-11.5, -9.5]))
    log_init = float(mond_cfg.get("log10_a0_initial", -10.0))
    enable_rar = bool(mond_cfg.get("enable_rar_fixed", True))

    rows_metrics: list[dict] = []
    rows_params: list[dict] = []
    fit_notes: list[str] = []

    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc").reset_index(drop=True)
        if g.empty:
            fit_notes.append(f"{gid}: missing from data")
            continue

        r = g["r_kpc"].to_numpy()
        v_obs = g["v_obs_kms"].to_numpy()
        v_err = g["v_err_kms"].to_numpy()
        v_bar = g["v_bar_kms"].to_numpy()
        data_source = str(g["data_source"].iloc[0])
        data_mode = str(g["data_mode"].iloc[0])

        fixed = fit_mond_fixed_a0(r, v_obs, v_err, v_bar, a0_ms2=a0_fixed)
        v_fixed = fixed.v_model_kms if fixed.fit_success else v_bar
        rows_metrics.append(
            _metrics_row(
                gid,
                "mond_fixed_a0_simple",
                len(g),
                v_obs,
                v_fixed,
                v_err,
                fit_success=fixed.fit_success,
                fit_status=fixed.fit_status,
                data_source=data_source,
                data_mode=data_mode,
            )
        )
        rows_params.append(
            _param_row(
                gid,
                "mond_fixed_a0_simple",
                fixed,
                a0_fixed_or_fitted="fixed",
                lower_bound=a0_fixed,
                upper_bound=a0_fixed,
            )
        )

        fitted = fit_mond_a0_simple(
            r,
            v_obs,
            v_err,
            v_bar,
            log10_a0_bounds=log_bounds,
            log10_a0_initial=log_init,
        )
        v_fit = fitted.v_model_kms if fitted.fit_success else v_bar
        rows_metrics.append(
            _metrics_row(
                gid,
                "mond_fit_a0_simple",
                len(g),
                v_obs,
                v_fit,
                v_err,
                fit_success=fitted.fit_success,
                fit_status=fitted.fit_status,
                data_source=data_source,
                data_mode=data_mode,
            )
        )
        phys_bounds = (10.0 ** log_bounds[0], 10.0 ** log_bounds[1])
        rows_params.append(
            _param_row(
                gid,
                "mond_fit_a0_simple",
                fitted,
                a0_fixed_or_fitted="fitted",
                lower_bound=phys_bounds[0],
                upper_bound=phys_bounds[1],
            )
        )
        if not fitted.fit_success:
            fit_notes.append(f"{gid} mond_fit_a0_simple: {fitted.fit_status}")

        if enable_rar:
            rar = fit_rar_fixed(r, v_obs, v_err, v_bar, g_dagger_ms2=g_dagger)
            v_rar = rar.v_model_kms if rar.fit_success else v_bar
            rows_metrics.append(
                _metrics_row(
                    gid,
                    "rar_fixed",
                    len(g),
                    v_obs,
                    v_rar,
                    v_err,
                    fit_success=rar.fit_success,
                    fit_status=rar.fit_status,
                    data_source=data_source,
                    data_mode=data_mode,
                )
            )
            rows_params.append(
                _param_row(
                    gid,
                    "rar_fixed",
                    rar,
                    a0_fixed_or_fitted="fixed_g_dagger",
                    lower_bound=g_dagger,
                    upper_bound=g_dagger,
                )
            )

    df_metrics = pd.DataFrame(rows_metrics)
    df_params = pd.DataFrame(rows_params)
    TABLE_COMPARISON.parent.mkdir(parents=True, exist_ok=True)
    df_metrics.to_csv(TABLE_COMPARISON, index=False)
    df_params.to_csv(TABLE_PARAMS, index=False)

    _write_report(selected_ids, mond_cfg, df_metrics, df_params, fit_notes, a0_fixed, log_bounds)
    print(f"Processed galaxies: {', '.join(selected_ids)}")
    print(f"Wrote MOND comparison: {TABLE_COMPARISON}")
    print(f"Wrote MOND parameters: {TABLE_PARAMS}")
    print(f"Wrote report: {REPORT_PATH}")
    return 0


def _write_report(
    selected_ids: list[str],
    mond_cfg: dict,
    metrics: pd.DataFrame,
    params: pd.DataFrame,
    fit_notes: list[str],
    a0_fixed: float,
    log_bounds: tuple[float, float],
) -> None:
    lines = [
        "# SPARC MOND/RAR Baseline Report (Phase 3M)",
        "",
        "This phase adds MOND/RAR as an empirical rotation-curve baseline only. "
        "It does not fit or validate TDF, does not disprove dark matter, "
        "and does not establish MOND as a complete replacement for ΛCDM.",
        "",
        f"- Selected galaxies: {', '.join(selected_ids)}",
        "",
        "## Formulas",
        "",
        "- Simple MOND: `nu(y) = 0.5 + sqrt(0.25 + 1/y)` with `y = g_bar / a0`, `g_obs = nu(y) * g_bar`",
        "- RAR (optional): `g_obs = g_bar / (1 - exp(-sqrt(g_bar / g_dagger)))`",
        "",
        "## Unit conversions",
        "",
        "- `r_m = r_kpc * 3.085677581e19`",
        "- `v_ms = v_kms * 1000`",
        "- `g_bar = v_bar^2 / r` (m/s²)",
        "- `v_model_kms = sqrt(g_obs * r_m) / 1000`",
        "",
        "## Parameters",
        "",
        f"- Fixed a0: `{a0_fixed}` m/s²",
        f"- Fitted log10(a0) bounds: `{list(log_bounds)}`",
        "- `mond_fixed_a0_simple`: n_parameters = 0",
        "- `mond_fit_a0_simple`: n_parameters = 1",
        "- `rar_fixed`: n_parameters = 0 (if enabled)",
        "",
        "## Cautions",
        "",
        "- No stellar M/L fitting in this phase.",
        "- Baryonic decomposition is fixed from SPARC rotmod columns.",
        "- Distance and inclination are not fitted.",
        "",
        "## Fit success",
        "",
        "| Galaxy | Model | fit_success | fit_status | RMSE | AIC |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for _, row in metrics.sort_values(["galaxy_id", "model_name"]).iterrows():
        lines.append(
            f"| {row['galaxy_id']} | {row['model_name']} | {row['fit_success']} | "
            f"{row['fit_status']} | {row['rmse_kms']:.2f} | {row['aic']:.1f} |"
        )

    if fit_notes:
        lines.extend(["", "## Fit notes", ""])
        lines.extend([f"- {n}" for n in fit_notes])

    lines.extend(
        [
            "",
            "## Best by galaxy (AIC)",
            "",
        ]
    )
    for gid, g in metrics.groupby("galaxy_id"):
        best = g.loc[g["aic"].idxmin()]
        lines.append(f"- {gid}: {best['model_name']} (AIC={best['aic']:.1f}, RMSE={best['rmse_kms']:.2f})")

    lines.extend(
        [
            "",
            "## Fitted a0 values",
            "",
            "| Galaxy | log10_a0 | a0 [m/s²] |",
            "| --- | ---: | ---: |",
        ]
    )
    fit_params = params[params["model_name"] == "mond_fit_a0_simple"]
    for _, row in fit_params.iterrows():
        lines.append(
            f"| {row['galaxy_id']} | {row['log10_a0_m_s2']:.4f} | {row['a0_m_s2']:.3e} |"
        )

    lines.extend(
        [
            "",
            "## Outputs",
            f"- `{TABLE_COMPARISON}`",
            f"- `{TABLE_PARAMS}`",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
