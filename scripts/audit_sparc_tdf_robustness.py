from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.metrics.comparison import chi_square, rmse, safe_reduced_chi_square
from tdf_galaxy_tau.metrics.information_criteria import aic, bic, model_parameter_count
from tdf_galaxy_tau.models.fitting import fit_tdf_knot_baseline
from tdf_galaxy_tau.models.tdf_knot import (
    amplitude_bounds_from_reconstruction,
    fixed_knot_radii_kpc,
    galaxy_tau_reconstruction_arrays,
    initial_knot_amplitudes_from_reconstruction,
    interpolate_dtaudr_at_radii,
    load_tdf_knot_config,
    n_knots_for_model,
    smoothness_second_difference_metric,
    tdf_velocity_squared_kms2,
)
from tdf_galaxy_tau.reconstruction.radial_tau import load_selected_galaxy_ids
from tdf_galaxy_tau.validation.robustness import (
    build_robust_best_model_summary,
    knot_count_stability_table,
    negative_v2_audit_table,
)
from tdf_galaxy_tau.validation.tdf_holdout_runner import run_holdout_validation

ROBUST_SUMMARY = Path("outputs/tables/sparc_tdf_robustness_summary.csv")
HOLDOUT_TABLE = Path("outputs/tables/sparc_tdf_holdout_validation.csv")
KTAU_TABLE = Path("outputs/tables/sparc_tdf_ktau_sensitivity.csv")
BOUNDS_TABLE = Path("outputs/tables/sparc_tdf_bounds_sensitivity.csv")
SMOOTH_TABLE = Path("outputs/tables/sparc_tdf_smoothness_diagnostics.csv")
ROBUST_BEST = Path("outputs/tables/sparc_tdf_robust_best_model_summary.csv")
REPORT_PATH = Path("outputs/reports/sparc_tdf_robustness_audit_report.md")


def _fit_tdf3_galaxy(
    gid: str,
    g: pd.DataFrame,
    tau_df: pd.DataFrame,
    *,
    k_g: float,
    safety_factor: float,
    negative_v2_penalty: float,
) -> dict[str, object]:
    r = g["r_kpc"].to_numpy()
    v_obs = g["v_obs_kms"].to_numpy()
    v_err = g["v_err_kms"].to_numpy()
    v_bar = g["v_bar_kms"].to_numpy()
    r_recon, d_recon = galaxy_tau_reconstruction_arrays(tau_df, gid)
    knot_r = fixed_knot_radii_kpc(r, 3)
    bounds = amplitude_bounds_from_reconstruction(d_recon, safety_factor=safety_factor)
    x0 = initial_knot_amplitudes_from_reconstruction(knot_r, r_recon, d_recon)
    fit = fit_tdf_knot_baseline(
        r,
        v_obs,
        v_err,
        v_bar,
        model_name="tdf_3knot",
        knot_r_kpc=knot_r,
        initial_knot_dtaudr=x0,
        dtaudr_bounds=bounds,
        k_g=k_g,
        negative_v2_penalty=negative_v2_penalty,
    )
    n_params = model_parameter_count("tdf_3knot")
    v_model = fit.v_model_kms if fit.fit_success else v_bar
    chi2 = chi_square(v_obs, v_model, v_err)
    theta = np.array([fit.params.get(f"knot_{i}_dtaudr", np.nan) for i in range(3)])
    v2 = tdf_velocity_squared_kms2(r, v_bar, knot_r, theta, k_g=k_g) if fit.fit_success else v_bar**2
    return {
        "galaxy_id": gid,
        "fit_success": fit.fit_success,
        "fit_status": fit.fit_status,
        "rmse_kms": rmse(v_obs, v_model),
        "chi_square": chi2,
        "reduced_chi_square": safe_reduced_chi_square(chi2, len(g), n_params),
        "aic": aic(chi2, n_params),
        "bic": bic(chi2, len(g), n_params),
        "n_negative_v2": int(np.sum(v2 < 0)),
        "knot_amplitudes": theta,
        "knot_r_kpc": knot_r,
    }


def _ktau_sensitivity(
    data: pd.DataFrame,
    tau_df: pd.DataFrame,
    selected_ids: list[str],
    k_values: list[float],
    tdf_cfg,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc")
        for k in k_values:
            res = _fit_tdf3_galaxy(
                gid,
                g,
                tau_df,
                k_g=float(k),
                safety_factor=tdf_cfg.amplitude_bound_safety_factor,
                negative_v2_penalty=tdf_cfg.negative_v2_penalty,
            )
            rows.append(
                {
                    "galaxy_id": gid,
                    "K_tau": float(k),
                    "model_name": "tdf_3knot",
                    **{k2: res[k2] for k2 in ("fit_success", "fit_status", "rmse_kms", "aic", "bic", "n_negative_v2")},
                }
            )
    return pd.DataFrame(rows)


def _bounds_sensitivity(
    data: pd.DataFrame,
    tau_df: pd.DataFrame,
    selected_ids: list[str],
    factors: list[float],
    tdf_cfg,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc")
        for sf in factors:
            res = _fit_tdf3_galaxy(
                gid,
                g,
                tau_df,
                k_g=tdf_cfg.k_g,
                safety_factor=float(sf),
                negative_v2_penalty=tdf_cfg.negative_v2_penalty,
            )
            rows.append(
                {
                    "galaxy_id": gid,
                    "bounds_safety_factor": float(sf),
                    "model_name": "tdf_3knot",
                    **{k2: res[k2] for k2 in ("fit_success", "fit_status", "rmse_kms", "aic", "bic", "n_negative_v2")},
                }
            )
    return pd.DataFrame(rows)


def _smoothness_diagnostics(
    data: pd.DataFrame,
    tdf_comparison: pd.DataFrame,
    tdf_params: pd.DataFrame,
    selected_ids: list[str],
    tdf_cfg,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc")
        r = g["r_kpc"].to_numpy()
        for model_name in tdf_cfg.variants:
            sub = tdf_params[(tdf_params["galaxy_id"] == gid) & (tdf_params["model_name"] == model_name)]
            if sub.empty:
                continue
            nk = n_knots_for_model(model_name)
            knot_r = sub.sort_values("knot_index")["knot_r_kpc"].to_numpy()
            theta = sub.sort_values("knot_index")["fitted_dtaudr"].to_numpy()
            d_on_r = interpolate_dtaudr_at_radii(r, knot_r, theta)
            raw, norm = smoothness_second_difference_metric(r, d_on_r)
            comp = tdf_comparison[
                (tdf_comparison["galaxy_id"] == gid) & (tdf_comparison["model_name"] == model_name)
            ]
            status = str(comp.iloc[0]["fit_status"]) if not comp.empty else ""
            rows.append(
                {
                    "galaxy_id": gid,
                    "model_name": model_name,
                    "smoothness_sum_sq_second_diff": raw,
                    "smoothness_normalized": norm,
                    "fit_status": status,
                    "negative_v2_in_status": "negative_v2" in status,
                }
            )
    return pd.DataFrame(rows)


def _write_report(
    knot_stab: pd.DataFrame,
    holdout: pd.DataFrame,
    ktau: pd.DataFrame,
    bounds: pd.DataFrame,
    smooth: pd.DataFrame,
    neg_audit: pd.DataFrame,
    robust_best: pd.DataFrame,
    audit_cfg: dict,
) -> None:
    ho_even = holdout[holdout["split_name"] == "even_odd_index"]
    n_gal = len(robust_best)

    tdf3_beats_nfw = int(robust_best["tdf_3knot_beats_nfw_holdout_rmse"].sum())
    overfit_flags = int(robust_best["five_knot_overfit_risk_flag"].sum())

    ng7814_4 = neg_audit[
        (neg_audit["galaxy_id"] == "NGC7814") & (neg_audit["model_name"] == "tdf_4knot")
    ]

    lines = [
        "# SPARC TDF Robustness Audit Report (Phase 3C)",
        "",
        "This audit evaluates robustness of the six-galaxy rotation-curve TDF knot fits only. "
        "It does not validate TDF on full SPARC, does not disprove dark matter, "
        "does not replace ΛCDM, and does not include lensing or independent dynamical evidence.",
        "",
        "## Knot-count stability (3 vs 5)",
        "",
        f"- Galaxies with ΔAIC(5−3) < −{audit_cfg.get('delta_aic_large_improvement_threshold', 10)} "
        f"(large 5-knot gain): **{int(knot_stab['five_knot_large_aic_improvement'].sum())}** / {len(knot_stab)}",
        "",
        "| Galaxy | ΔAIC(5−3) | ΔRMSE(5−3) | 4-knot status |",
        "| --- | ---: | ---: | --- |",
    ]
    for _, row in knot_stab.sort_values("galaxy_id").iterrows():
        lines.append(
            f"| {row['galaxy_id']} | {row['delta_aic_5_minus_3']:.1f} | "
            f"{row['delta_rmse_5_minus_3']:.2f} | {row['tdf_4knot_fit_status']} |"
        )

    lines.extend(
        [
            "",
            "## Holdout validation (even/odd split summary)",
            "",
            f"- tdf_3knot beats nfw_refit on holdout test RMSE: **{tdf3_beats_nfw}** / {n_gal} galaxies",
            f"- five_knot overfit risk flags: **{overfit_flags}** / {n_gal}",
            "",
            "| Galaxy | tdf_3knot test RMSE | tdf_5knot test RMSE | nfw test RMSE | mond fit test RMSE |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for gid in sorted(robust_best["galaxy_id"].unique()):
        rb = robust_best[robust_best["galaxy_id"] == gid].iloc[0]
        lines.append(
            f"| {gid} | {rb['tdf_3knot_holdout_test_rmse']:.2f} | {rb['tdf_5knot_holdout_test_rmse']:.2f} | "
            f"{rb['nfw_refit_holdout_test_rmse']:.2f} | {rb['mond_fit_holdout_test_rmse']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## K_tau sensitivity (tdf_3knot, refitted)",
            "",
            "K_tau is partially degenerate with dτ/dr amplitude; metrics should be compared cautiously.",
            "",
            "| Galaxy | K_tau=0.5 RMSE | K_tau=1.0 RMSE | K_tau=2.0 RMSE |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for gid in sorted(ktau["galaxy_id"].unique()):
        kg = ktau[ktau["galaxy_id"] == gid]
        vals = {float(r["K_tau"]): float(r["rmse_kms"]) for _, r in kg.iterrows()}
        lines.append(
            f"| {gid} | {vals.get(0.5, float('nan')):.2f} | {vals.get(1.0, float('nan')):.2f} | {vals.get(2.0, float('nan')):.2f} |"
        )

    lines.extend(
        [
            "",
            "## Bounds safety-factor sensitivity (tdf_3knot)",
            "",
            "| Galaxy | sf=1.0 | sf=1.5 | sf=2.0 | sf=3.0 |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for gid in sorted(bounds["galaxy_id"].unique()):
        bg = bounds[bounds["galaxy_id"] == gid]
        vals = {float(r["bounds_safety_factor"]): float(r["rmse_kms"]) for _, r in bg.iterrows()}
        lines.append(
            f"| {gid} | {vals.get(1.0, float('nan')):.2f} | {vals.get(1.5, float('nan')):.2f} | "
            f"{vals.get(2.0, float('nan')):.2f} | {vals.get(3.0, float('nan')):.2f} |"
        )

    lines.extend(
        [
            "",
            "## Negative v² audit",
            "",
        ]
    )
    neg_rows = neg_audit[neg_audit["negative_v2_flag"]]
    if neg_rows.empty:
        lines.append("- No fits with `negative_v2` in fit_status.")
    else:
        for _, row in neg_rows.iterrows():
            lines.append(f"- **{row['galaxy_id']}** / {row['model_name']}: {row['fit_status']}")

    if not ng7814_4.empty:
        lines.extend(
            [
                "",
                "### NGC7814 tdf_4knot (explicit check)",
                "",
                f"- fit_status: `{ng7814_4.iloc[0]['fit_status']}`",
                "- 4-knot fit can explore pathological amplitudes; prefer tdf_3knot for reporting unless holdout supports 4-knot.",
            ]
        )

    lines.extend(
        [
            "",
            "## Smoothness diagnostics (diagnostic only, not fitted)",
            "",
            "| Galaxy | model | smoothness (norm) | negative_v2 flag |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for _, row in smooth.sort_values(["galaxy_id", "model_name"]).iterrows():
        lines.append(
            f"| {row['galaxy_id']} | {row['model_name']} | {row['smoothness_normalized']:.4g} | "
            f"{row['negative_v2_in_status']} |"
        )

    lines.extend(
        [
            "",
            "## Recommended reporting model (robust summary)",
            "",
            "| Galaxy | recommended |",
            "| --- | --- |",
        ]
    )
    for _, row in robust_best.iterrows():
        lines.append(f"| {row['galaxy_id']} | {row['recommended_reporting_model']} |")

    lines.extend(
        [
            "",
            "## Outputs",
            f"- `{ROBUST_SUMMARY}`",
            f"- `{HOLDOUT_TABLE}`",
            f"- `{KTAU_TABLE}`",
            f"- `{BOUNDS_TABLE}`",
            f"- `{SMOOTH_TABLE}`",
            f"- `{ROBUST_BEST}`",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 3C TDF robustness audit")
    parser.add_argument("--data", required=True)
    parser.add_argument("--subset", required=True)
    parser.add_argument("--tau-profiles", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--models-config", default="configs/models.yaml")
    args = parser.parse_args()

    data = pd.read_csv(args.data)
    tau_df = pd.read_csv(args.tau_profiles)
    recon_yaml = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    models_yaml = yaml.safe_load(Path(args.models_config).read_text(encoding="utf-8")) or {}
    audit_cfg = recon_yaml.get("tdf_robustness_audit", {})
    tdf_cfg = load_tdf_knot_config(recon_yaml)

    selected_ids = load_selected_galaxy_ids(args.subset)

    tdf_comparison = pd.read_csv("outputs/tables/sparc_tdf_knot_model_comparison.csv")
    tdf_params = pd.read_csv("outputs/tables/sparc_tdf_knot_fit_parameters.csv")
    full_best = pd.read_csv("outputs/tables/sparc_best_model_summary.csv")

    knot_stab = knot_count_stability_table(tdf_comparison)
    knot_stab.to_csv(ROBUST_SUMMARY, index=False)

    neg_audit = negative_v2_audit_table(tdf_comparison, tdf_params)
    neg_audit.to_csv(ROBUST_SUMMARY.parent / "sparc_tdf_negative_v2_audit.csv", index=False)

    k_values = [float(x) for x in audit_cfg.get("k_tau_values", [0.5, 1.0, 2.0])]
    sf_values = [float(x) for x in audit_cfg.get("bounds_safety_factors", [1.0, 1.5, 2.0, 3.0])]

    ktau_df = _ktau_sensitivity(data, tau_df, selected_ids, k_values, tdf_cfg)
    ktau_df.to_csv(KTAU_TABLE, index=False)

    bounds_df = _bounds_sensitivity(data, tau_df, selected_ids, sf_values, tdf_cfg)
    bounds_df.to_csv(BOUNDS_TABLE, index=False)

    smooth_df = _smoothness_diagnostics(data, tdf_comparison, tdf_params, selected_ids, tdf_cfg)
    smooth_df.to_csv(SMOOTH_TABLE, index=False)

    tdf_models = tuple(audit_cfg.get("holdout_tdf_models", ["tdf_3knot", "tdf_5knot"]))
    holdout_df = run_holdout_validation(
        data,
        tau_df,
        selected_ids,
        recon_yaml,
        models_yaml,
        tdf_models=tdf_models,
    )
    holdout_df.to_csv(HOLDOUT_TABLE, index=False)

    robust_best = build_robust_best_model_summary(holdout_df, full_best, knot_stab)
    robust_best.to_csv(ROBUST_BEST, index=False)

    _write_report(knot_stab, holdout_df, ktau_df, bounds_df, smooth_df, neg_audit, robust_best, audit_cfg)

    print(f"Wrote robustness summary: {ROBUST_SUMMARY}")
    print(f"Wrote holdout validation: {HOLDOUT_TABLE}")
    print(f"Wrote K_tau sensitivity: {KTAU_TABLE}")
    print(f"Wrote bounds sensitivity: {BOUNDS_TABLE}")
    print(f"Wrote smoothness diagnostics: {SMOOTH_TABLE}")
    print(f"Wrote robust best-model summary: {ROBUST_BEST}")
    print(f"Wrote report: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
