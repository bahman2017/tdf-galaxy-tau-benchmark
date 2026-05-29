from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from tdf_galaxy_tau.metrics.comparison import chi_square, rmse, safe_reduced_chi_square
from tdf_galaxy_tau.metrics.information_criteria import aic, bic, model_parameter_count
from tdf_galaxy_tau.models.fitting import (
    baryonic_only_model,
    build_legacy_vs_refit_delta,
    fit_burkert_baseline,
    fit_burkert_baseline_log,
    fit_nfw_baseline,
    fit_nfw_baseline_log,
    log10_bounds_to_physical,
)
from tdf_galaxy_tau.plotting.rotation_curves import plot_baseline_rotation_comparison
from tdf_galaxy_tau.reconstruction.radial_tau import load_selected_galaxy_ids

LEGACY_TABLE_COMPARISON = Path("outputs/tables/sparc_baseline_model_comparison.csv")
LEGACY_TABLE_PARAMS = Path("outputs/tables/sparc_baseline_fit_parameters.csv")
LEGACY_REPORT_PATH = Path("outputs/reports/sparc_baseline_model_comparison_report.md")
LEGACY_FIG_SUFFIX = "_baseline_rotation_comparison.png"

REFIT_TABLE_COMPARISON = Path("outputs/tables/sparc_baseline_model_comparison_refit.csv")
REFIT_TABLE_PARAMS = Path("outputs/tables/sparc_baseline_fit_parameters_refit.csv")
REFIT_REPORT_PATH = Path("outputs/reports/sparc_baseline_refit_report.md")
REFIT_DELTA_TABLE = Path("outputs/tables/sparc_baseline_legacy_vs_refit_delta.csv")
REFIT_FIG_SUFFIX = "_baseline_rotation_comparison_refit.png"

FIG_DIR = Path("outputs/figures/sparc_subset")


def _load_models_config(path: Path) -> dict:
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
    comparison_stage: str,
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
        "comparison_stage": comparison_stage,
    }


def _legacy_nfw_params_row(gid: str, nfw) -> dict:
    return {
        "model_name": "nfw",
        "galaxy_id": gid,
        "fit_success": nfw.fit_success,
        "fit_status": nfw.fit_status,
        "fitting_mode": nfw.fitting_mode,
        "rho_s": nfw.params.get("rho_s"),
        "r_s": nfw.params.get("r_s"),
        "rho_s_bounds": nfw.bounds.get("rho_s"),
        "r_s_bounds": nfw.bounds.get("r_s"),
    }


def _refit_nfw_params_row(gid: str, nfw) -> dict:
    robust = nfw.bounds
    log_rho_bounds = robust.get("log10_rho_s", (2.0, 11.0))
    log_rs_bounds = robust.get("log10_r_s", (-1.3, 3.0))
    return {
        "model_name": "nfw",
        "galaxy_id": gid,
        "fit_success": nfw.fit_success,
        "fit_status": nfw.fit_status,
        "fitting_mode": nfw.fitting_mode,
        "n_starts_attempted": nfw.n_starts_attempted,
        "n_starts_successful": nfw.n_starts_successful,
        "rho_s_msun_kpc3": nfw.params.get("rho_s_msun_kpc3"),
        "r_s_kpc": nfw.params.get("r_s_kpc"),
        "log10_rho_s": (nfw.log_params or {}).get("log10_rho_s"),
        "log10_r_s": (nfw.log_params or {}).get("log10_r_s"),
        "rho_s_bounds": robust.get("rho_s"),
        "r_s_bounds": robust.get("r_s"),
        "log10_rho_s_bounds": log_rho_bounds,
        "log10_r_s_bounds": log_rs_bounds,
    }


def _legacy_burkert_params_row(gid: str, burk) -> dict:
    return {
        "model_name": "burkert",
        "galaxy_id": gid,
        "fit_success": burk.fit_success,
        "fit_status": burk.fit_status,
        "fitting_mode": burk.fitting_mode,
        "rho_0": burk.params.get("rho_0"),
        "r_0": burk.params.get("r_0"),
        "rho_0_bounds": burk.bounds.get("rho_0"),
        "r_0_bounds": burk.bounds.get("r_0"),
    }


def _refit_burkert_params_row(gid: str, burk) -> dict:
    robust = burk.bounds
    log_rho_bounds = robust.get("log10_rho_0", (2.0, 11.0))
    log_r0_bounds = robust.get("log10_r_0", (-1.3, 3.0))
    return {
        "model_name": "burkert",
        "galaxy_id": gid,
        "fit_success": burk.fit_success,
        "fit_status": burk.fit_status,
        "fitting_mode": burk.fitting_mode,
        "n_starts_attempted": burk.n_starts_attempted,
        "n_starts_successful": burk.n_starts_successful,
        "rho_0_msun_kpc3": burk.params.get("rho_0_msun_kpc3"),
        "r_0_kpc": burk.params.get("r_0_kpc"),
        "log10_rho_0": (burk.log_params or {}).get("log10_rho_0"),
        "log10_r_0": (burk.log_params or {}).get("log10_r_0"),
        "rho_0_bounds": robust.get("rho_0"),
        "r_0_bounds": robust.get("r_0"),
        "log10_rho_0_bounds": log_rho_bounds,
        "log10_r_0_bounds": log_r0_bounds,
    }


def _run_legacy(selected_ids, data, cfg) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    legacy = cfg.get("legacy_bounds_phase3a", {})
    nfw_bounds = legacy.get("nfw", cfg["models"]["nfw"])
    burk_bounds = legacy.get("burkert", cfg["models"]["burkert"])
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

        bary = baryonic_only_model(v_bar)
        rows_metrics.append(
            _metrics_row(
                gid,
                "baryonic_only",
                len(g),
                v_obs,
                bary.v_model_kms,
                v_err,
                fit_success=True,
                fit_status=bary.fit_status,
                data_source=data_source,
                data_mode=data_mode,
                comparison_stage="phase_3a_baseline_only",
            )
        )

        nfw = fit_nfw_baseline(
            r,
            v_obs,
            v_err,
            v_bar,
            rho_s_bounds=tuple(nfw_bounds["rho_s_bounds_msun_kpc3"]),
            r_s_bounds=tuple(nfw_bounds["r_s_bounds_kpc"]),
        )
        nfw_model = nfw.v_model_kms if nfw.fit_success else v_bar
        rows_metrics.append(
            _metrics_row(
                gid,
                "nfw",
                len(g),
                v_obs,
                nfw_model,
                v_err,
                fit_success=nfw.fit_success,
                fit_status=nfw.fit_status,
                data_source=data_source,
                data_mode=data_mode,
                comparison_stage="phase_3a_baseline_only",
            )
        )
        rows_params.append(_legacy_nfw_params_row(gid, nfw))
        if not nfw.fit_success:
            fit_notes.append(f"{gid} NFW failed: {nfw.fit_status}")

        burk = fit_burkert_baseline(
            r,
            v_obs,
            v_err,
            v_bar,
            rho0_bounds=tuple(burk_bounds["rho_0_bounds_msun_kpc3"]),
            r0_bounds=tuple(burk_bounds["r_0_bounds_kpc"]),
        )
        burk_model = burk.v_model_kms if burk.fit_success else v_bar
        rows_metrics.append(
            _metrics_row(
                gid,
                "burkert",
                len(g),
                v_obs,
                burk_model,
                v_err,
                fit_success=burk.fit_success,
                fit_status=burk.fit_status,
                data_source=data_source,
                data_mode=data_mode,
                comparison_stage="phase_3a_baseline_only",
            )
        )
        rows_params.append(_legacy_burkert_params_row(gid, burk))
        if not burk.fit_success:
            fit_notes.append(f"{gid} Burkert failed: {burk.fit_status}")

        plot_baseline_rotation_comparison(
            gid,
            r,
            v_obs,
            v_err,
            bary.v_model_kms,
            FIG_DIR / f"{gid}{LEGACY_FIG_SUFFIX}",
            v_nfw_kms=nfw.v_model_kms if nfw.fit_success else None,
            v_burkert_kms=burk.v_model_kms if burk.fit_success else None,
        )

    return pd.DataFrame(rows_metrics), pd.DataFrame(rows_params), fit_notes


def _run_refit(selected_ids, data, cfg) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    robust = cfg["robust_fit"]
    nfw_bounds = robust["nfw"]
    burk_bounds = robust["burkert"]
    log_rho_nfw = tuple(nfw_bounds["log10_rho_s_bounds_msun_kpc3"])
    log_rs_nfw = tuple(nfw_bounds["log10_r_s_bounds_kpc"])
    log_rho_burk = tuple(burk_bounds["log10_rho_0_bounds_msun_kpc3"])
    log_r0_burk = tuple(burk_bounds["log10_r_0_bounds_kpc"])

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

        bary = baryonic_only_model(v_bar)
        rows_metrics.append(
            _metrics_row(
                gid,
                "baryonic_only",
                len(g),
                v_obs,
                bary.v_model_kms,
                v_err,
                fit_success=True,
                fit_status=bary.fit_status,
                data_source=data_source,
                data_mode=data_mode,
                comparison_stage="phase_3a_r_robust_refit",
            )
        )

        nfw = fit_nfw_baseline_log(
            r,
            v_obs,
            v_err,
            v_bar,
            log10_rho_s_bounds=log_rho_nfw,
            log10_r_s_bounds=log_rs_nfw,
        )
        nfw_model = nfw.v_model_kms if nfw.fit_success else v_bar
        rows_metrics.append(
            _metrics_row(
                gid,
                "nfw",
                len(g),
                v_obs,
                nfw_model,
                v_err,
                fit_success=nfw.fit_success,
                fit_status=nfw.fit_status,
                data_source=data_source,
                data_mode=data_mode,
                comparison_stage="phase_3a_r_robust_refit",
            )
        )
        rows_params.append(_refit_nfw_params_row(gid, nfw))
        if not nfw.fit_success:
            fit_notes.append(f"{gid} NFW refit failed: {nfw.fit_status}")

        burk = fit_burkert_baseline_log(
            r,
            v_obs,
            v_err,
            v_bar,
            log10_rho_0_bounds=log_rho_burk,
            log10_r_0_bounds=log_r0_burk,
        )
        burk_model = burk.v_model_kms if burk.fit_success else v_bar
        rows_metrics.append(
            _metrics_row(
                gid,
                "burkert",
                len(g),
                v_obs,
                burk_model,
                v_err,
                fit_success=burk.fit_success,
                fit_status=burk.fit_status,
                data_source=data_source,
                data_mode=data_mode,
                comparison_stage="phase_3a_r_robust_refit",
            )
        )
        rows_params.append(_refit_burkert_params_row(gid, burk))
        if not burk.fit_success:
            fit_notes.append(f"{gid} Burkert refit failed: {burk.fit_status}")

        plot_baseline_rotation_comparison(
            gid,
            r,
            v_obs,
            v_err,
            bary.v_model_kms,
            FIG_DIR / f"{gid}{REFIT_FIG_SUFFIX}",
            v_nfw_kms=nfw.v_model_kms if nfw.fit_success else None,
            v_burkert_kms=burk.v_model_kms if burk.fit_success else None,
            title_suffix="robust refit (log-space multistart)",
        )

    return pd.DataFrame(rows_metrics), pd.DataFrame(rows_params), fit_notes


def _write_legacy_report(selected_ids, cfg, fit_notes: list[str]) -> None:
    legacy = cfg.get("legacy_bounds_phase3a", {})
    nfw_bounds = legacy.get("nfw", cfg["models"]["nfw"])
    burk_bounds = legacy.get("burkert", cfg["models"]["burkert"])
    summary = [
        "# SPARC Baseline Model Comparison Report (Phase 3A)",
        "",
        "This phase fits baryonic-only, NFW, and Burkert baselines only. It does not fit or validate the TDF model. It does not claim that dark matter is disproven.",
        "",
        f"- Selected galaxies processed: {', '.join(selected_ids)}",
        f"- Fitting method: {cfg.get('fitting', {}).get('method', 'least_squares')}",
        f"- NFW bounds: rho_s={nfw_bounds['rho_s_bounds_msun_kpc3']}, r_s={nfw_bounds['r_s_bounds_kpc']}",
        f"- Burkert bounds: rho_0={burk_bounds['rho_0_bounds_msun_kpc3']}, r_0={burk_bounds['r_0_bounds_kpc']}",
        "",
        "## Fit notes",
    ]
    if fit_notes:
        summary.extend([f"- {x}" for x in fit_notes])
    else:
        summary.append("- No fit failures")
    summary.extend(
        [
            "",
            "## Outputs",
            f"- `{LEGACY_TABLE_COMPARISON}`",
            f"- `{LEGACY_TABLE_PARAMS}`",
            f"- `outputs/figures/sparc_subset/*{LEGACY_FIG_SUFFIX}`",
        ]
    )
    LEGACY_REPORT_PATH.write_text("\n".join(summary) + "\n", encoding="utf-8")


def _write_refit_report(
    selected_ids,
    cfg,
    fit_notes: list[str],
    delta_df: pd.DataFrame,
    refit_audit_summary: dict[str, object] | None,
) -> None:
    robust = cfg["robust_fit"]
    nfw_bounds = robust["nfw"]
    burk_bounds = robust["burkert"]
    phys_rho_nfw = log10_bounds_to_physical(tuple(nfw_bounds["log10_rho_s_bounds_msun_kpc3"]))
    phys_rs_nfw = log10_bounds_to_physical(tuple(nfw_bounds["log10_r_s_bounds_kpc"]))

    halo_delta = delta_df[delta_df["model_name"].isin(["nfw", "burkert"])]
    nfw_delta = halo_delta[halo_delta["model_name"] == "nfw"]
    burk_delta = halo_delta[halo_delta["model_name"] == "burkert"]

    boundary_improved = int(halo_delta["boundary_status_improved"].sum())
    chi_improved = int(halo_delta["chi_square_status_improved"].sum())
    rmse_improved_nfw = int((nfw_delta["delta_rmse"] < 0).sum()) if len(nfw_delta) else 0
    rmse_improved_burk = int((burk_delta["delta_rmse"] < 0).sum()) if len(burk_delta) else 0

    lines = [
        "# SPARC Baseline Robust Refit Report (Phase 3A-R)",
        "",
        "This is a **baseline-only** robustness improvement. TDF is **not** fitted in this phase.",
        "Phase 3A legacy outputs were **not** deleted or overwritten.",
        "",
        "## Method",
        "",
        "- Log-space halo parameters (`log10_rho`, `log10_r`) with physical-unit outputs.",
        "- Wider documented bounds in `configs/models.yaml` under `robust_fit`.",
        "- Deterministic multistart (3 corner guesses + 1 data-informed guess); lowest chi-square kept.",
        "- Baryonic-only model unchanged from Phase 3A.",
        "",
        f"- Selected galaxies: {', '.join(selected_ids)}",
        f"- NFW log bounds: log10_rho_s={nfw_bounds['log10_rho_s_bounds_msun_kpc3']}, log10_r_s={nfw_bounds['log10_r_s_bounds_kpc']}",
        f"- NFW physical bounds (derived): rho_s={list(phys_rho_nfw)}, r_s={list(phys_rs_nfw)}",
        f"- Burkert log bounds: log10_rho_0={burk_bounds['log10_rho_0_bounds_msun_kpc3']}, log10_r_0={burk_bounds['log10_r_0_bounds_kpc']}",
        "",
        "## Legacy vs refit summary",
        "",
        f"- Halo fits with improved boundary status: **{boundary_improved}** / {len(halo_delta)}",
        f"- Halo fits with improved chi-square status: **{chi_improved}** / {len(halo_delta)}",
        f"- NFW galaxies with lower RMSE after refit: **{rmse_improved_nfw}** / {len(nfw_delta)}",
        f"- Burkert galaxies with lower RMSE after refit: **{rmse_improved_burk}** / {len(burk_delta)}",
        "",
    ]

    if refit_audit_summary:
        lines.extend(
            [
                "## Refit audit (post-fit)",
                "",
                f"- Boundary-limited rows (refit): **{refit_audit_summary.get('boundary_limited_rows', 'n/a')}**",
                f"- High reduced chi-square rows (refit): **{refit_audit_summary.get('high_chi_rows', 'n/a')}**",
                "",
            ]
        )

    if fit_notes:
        lines.extend(["## Fit notes", ""])
        lines.extend([f"- {x}" for x in fit_notes])
        lines.append("")

    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "- NFW and Burkert remain **comparison baselines**, not proof of dark matter and not disproof of TDF.",
            "- Worse or unstable refit results are reported explicitly; the goal is fairness and traceability.",
            "",
            "## Outputs",
            f"- `{REFIT_TABLE_COMPARISON}`",
            f"- `{REFIT_TABLE_PARAMS}`",
            f"- `{REFIT_DELTA_TABLE}`",
            f"- `outputs/figures/sparc_subset/*{REFIT_FIG_SUFFIX}`",
        ]
    )
    REFIT_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fit baryonic-only, NFW, Burkert baselines on selected SPARC subset")
    parser.add_argument("--data", required=True)
    parser.add_argument("--subset", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument(
        "--mode",
        choices=("legacy", "refit"),
        default="legacy",
        help="legacy=Phase 3A linear bounds; refit=Phase 3A-R log-space multistart",
    )
    args = parser.parse_args()

    data = pd.read_csv(args.data)
    selected_ids = load_selected_galaxy_ids(args.subset)
    cfg = _load_models_config(Path(args.config))

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    if args.mode == "legacy":
        df_metrics, df_params, fit_notes = _run_legacy(selected_ids, data, cfg)
        LEGACY_TABLE_COMPARISON.parent.mkdir(parents=True, exist_ok=True)
        df_metrics.to_csv(LEGACY_TABLE_COMPARISON, index=False)
        df_params.to_csv(LEGACY_TABLE_PARAMS, index=False)
        _write_legacy_report(selected_ids, cfg, fit_notes)
        print(f"Processed galaxies: {', '.join(selected_ids)}")
        print(f"Wrote baseline comparison table: {LEGACY_TABLE_COMPARISON}")
        print(f"Wrote baseline parameter table: {LEGACY_TABLE_PARAMS}")
        print(f"Wrote report: {LEGACY_REPORT_PATH}")
        return 0

    df_metrics, df_params, fit_notes = _run_refit(selected_ids, data, cfg)
    REFIT_TABLE_COMPARISON.parent.mkdir(parents=True, exist_ok=True)
    df_metrics.to_csv(REFIT_TABLE_COMPARISON, index=False)
    df_params.to_csv(REFIT_TABLE_PARAMS, index=False)

    legacy_comparison = pd.read_csv(LEGACY_TABLE_COMPARISON) if LEGACY_TABLE_COMPARISON.is_file() else pd.DataFrame()
    legacy_audit = (
        pd.read_csv(Path("outputs/tables/sparc_baseline_fit_audit.csv"))
        if Path("outputs/tables/sparc_baseline_fit_audit.csv").is_file()
        else pd.DataFrame()
    )

    refit_audit_summary: dict[str, object] | None = None
    delta_df = pd.DataFrame()
    if legacy_comparison.empty:
        fit_notes.append("legacy comparison table missing; skipped legacy-vs-refit delta")
    else:
        from tdf_galaxy_tau.models.fitting import BaselineAuditConfig, audit_baseline_fits, summarize_baseline_audit

        audit_cfg = BaselineAuditConfig(
            boundary_tolerance_fraction=float(cfg.get("audit", {}).get("boundary_tolerance_fraction", 0.01)),
            high_reduced_chi_square_threshold=float(cfg.get("audit", {}).get("high_reduced_chi_square_threshold", 5.0)),
            very_high_reduced_chi_square_threshold=float(
                cfg.get("audit", {}).get("very_high_reduced_chi_square_threshold", 20.0)
            ),
            poor_rmse_fraction_of_median_v_obs=float(
                cfg.get("audit", {}).get("poor_rmse_fraction_of_median_v_obs", 0.20)
            ),
        )
        medians = data.groupby("galaxy_id")["v_obs_kms"].median().astype(float).to_dict()
        refit_audit = audit_baseline_fits(
            df_metrics,
            df_params,
            median_v_obs_by_galaxy=medians,
            config=audit_cfg,
        )
        refit_audit_summary = summarize_baseline_audit(refit_audit)
        if legacy_audit.empty:
            legacy_audit = audit_baseline_fits(
                legacy_comparison,
                pd.read_csv(LEGACY_TABLE_PARAMS) if LEGACY_TABLE_PARAMS.is_file() else pd.DataFrame(),
                median_v_obs_by_galaxy=medians,
                config=audit_cfg,
            )
        delta_df = build_legacy_vs_refit_delta(legacy_comparison, df_metrics, legacy_audit, refit_audit)
        delta_df.to_csv(REFIT_DELTA_TABLE, index=False)

    _write_refit_report(selected_ids, cfg, fit_notes, delta_df, refit_audit_summary)

    print(f"Processed galaxies: {', '.join(selected_ids)}")
    print(f"Wrote refit comparison table: {REFIT_TABLE_COMPARISON}")
    print(f"Wrote refit parameter table: {REFIT_TABLE_PARAMS}")
    print(f"Wrote refit report: {REFIT_REPORT_PATH}")
    if not delta_df.empty:
        print(f"Wrote legacy-vs-refit delta: {REFIT_DELTA_TABLE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
