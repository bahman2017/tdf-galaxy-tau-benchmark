from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from tdf_galaxy_tau.metrics.comparison import build_best_model_summary
from tdf_galaxy_tau.models.fitting import (
    fit_burkert_baseline_log,
    fit_mond_a0_simple,
    fit_nfw_baseline_log,
    fit_tdf_knot_baseline,
)
from tdf_galaxy_tau.models.tdf_knot import (
    amplitude_bounds_from_reconstruction,
    fixed_knot_radii_kpc,
    galaxy_tau_reconstruction_arrays,
    initial_knot_amplitudes_from_reconstruction,
    load_tdf_knot_config,
    n_knots_for_model,
)
from tdf_galaxy_tau.plotting.rotation_curves import plot_full_model_rotation_comparison
from tdf_galaxy_tau.reconstruction.radial_tau import load_selected_galaxy_ids

FULL_TABLE = Path("outputs/tables/sparc_full_model_comparison.csv")
SUMMARY_TABLE = Path("outputs/tables/sparc_best_model_summary.csv")
REPORT_PATH = Path("outputs/reports/sparc_full_model_comparison_report.md")
FIG_DIR = Path("outputs/figures/sparc_subset")

_EXCLUDED_MODELS = {"direct_tau_reconstruction", "tdf"}


def _filter_models(df: pd.DataFrame) -> pd.DataFrame:
    out = df[~df["model_name"].isin(_EXCLUDED_MODELS)].copy()
    return out


def _write_report(
    selected_ids: list[str],
    full_df: pd.DataFrame,
    summary: pd.DataFrame,
    tdf_cfg,
    amp_bounds_example: tuple[float, float],
) -> None:
    lines = [
        "# SPARC Full Model Comparison Report (Phase 3B)",
        "",
        "The TDF knot model is a low-parameter radial reconstruction model for rotation-curve residuals. "
        "This phase does not disprove dark matter, does not replace ΛCDM, does not validate TDF on full SPARC, "
        "and does not use lensing or independent dynamical evidence.",
        "",
        f"- Selected galaxies: {', '.join(selected_ids)}",
        f"- Fixed K_g (legacy K_tau label): {tdf_cfg.k_g}",
        f"- Knot amplitude bounds (example galaxy): [{amp_bounds_example[0]:.4g}, {amp_bounds_example[1]:.4g}] "
        f"(×{tdf_cfg.amplitude_bound_safety_factor} safety on Phase 2A dτ/dr range)",
        "",
        "## Fitted models",
        "",
        "- baryonic_only, nfw_refit, burkert_refit, mond_fixed_a0_simple, mond_fit_a0_simple, rar_fixed",
        "- tdf_3knot (primary), tdf_4knot, tdf_5knot (sensitivity)",
        "",
        "## Knot placement (fixed, not fitted)",
        "",
        "- 3-knot: r_min, r_mid, r_max",
        "- 4-knot: r_min, r_min+span/3, r_min+2span/3, r_max",
        "- 5-knot: r_min, r_min+span/4, r_mid, r_min+3span/4, r_max",
        "",
        "## Parameter counts",
        "",
        "- tdf_3knot: 3; tdf_4knot: 4; tdf_5knot: 5 (K_g / legacy K_tau and knot radii not counted)",
        "",
        "## Caveats",
        "",
        "- Phase 2A direct τ reconstruction is diagnostic only (not in AIC/BIC table).",
        "- Fixed SPARC baryonic decomposition; no stellar M/L fitting.",
        "- Halo refit reduced boundary issues; high reduced chi-square may persist.",
        "- Fitted MOND a0 often below canonical 1.2×10⁻¹⁰ m/s² in this setup.",
        "- tdf_4knot / tdf_5knot have higher parameter count — interpret overfitting risk cautiously.",
        "- Negative v_tau² regions may occur; fitting applies penalties when v_model² < 0.",
        "",
        "## Fit summary",
        "",
        "| Galaxy | Model | success | RMSE | AIC | red. χ² |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for _, row in full_df.sort_values(["galaxy_id", "aic"]).iterrows():
        lines.append(
            f"| {row['galaxy_id']} | {row['model_name']} | {row['fit_success']} | "
            f"{row['rmse_kms']:.2f} | {row['aic']:.1f} | {row['reduced_chi_square']:.2f} |"
        )

    lines.extend(["", "## Best model per galaxy", ""])
    for _, row in summary.iterrows():
        lines.append(
            f"- **{row['galaxy_id']}**: RMSE={row['best_by_rmse']}, AIC={row['best_by_aic']}, "
            f"BIC={row['best_by_bic']}; tdf_3knot beats NFW (AIC)={row['tdf_3knot_beats_nfw_refit_by_aic']}, "
            f"beats MOND fit-a0 (AIC)={row['tdf_3knot_beats_mond_fit_a0_by_aic']}"
        )

    lines.extend(
        [
            "",
            "## Outputs",
            f"- `{FULL_TABLE}`",
            f"- `{SUMMARY_TABLE}`",
            f"- `outputs/figures/sparc_subset/*_full_model_rotation_comparison.png`",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Combine halo/MOND and TDF knot comparisons")
    parser.add_argument("--halo-mond", required=True)
    parser.add_argument("--tdf", required=True)
    parser.add_argument(
        "--data",
        default="data/processed/sparc/sparc_rotmod_standardized.csv",
    )
    parser.add_argument(
        "--subset",
        default="outputs/tables/sparc_subset_selection.csv",
    )
    parser.add_argument(
        "--tau-profiles",
        default="outputs/tables/sparc_subset_tau_profiles.csv",
    )
    parser.add_argument("--config", default="configs/reconstruction.yaml")
    parser.add_argument("--models-config", default="configs/models.yaml")
    args = parser.parse_args()

    halo_mond = _filter_models(pd.read_csv(args.halo_mond))
    tdf = _filter_models(pd.read_csv(args.tdf))
    full = pd.concat([halo_mond, tdf], ignore_index=True)
    FULL_TABLE.parent.mkdir(parents=True, exist_ok=True)
    full.to_csv(FULL_TABLE, index=False)

    summary = build_best_model_summary(full)
    summary.to_csv(SUMMARY_TABLE, index=False)

    recon_yaml = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    tdf_cfg = load_tdf_knot_config(recon_yaml)
    data = pd.read_csv(args.data)
    tau_profiles = pd.read_csv(args.tau_profiles)
    selected_ids = load_selected_galaxy_ids(args.subset)
    models_yaml = yaml.safe_load(Path(args.models_config).read_text(encoding="utf-8")) or {}

    amp_example = (-1.0, 1.0)
    try:
        gid0 = selected_ids[0]
        _, drec = galaxy_tau_reconstruction_arrays(tau_profiles, gid0)
        amp_example = amplitude_bounds_from_reconstruction(
            drec,
            safety_factor=tdf_cfg.amplitude_bound_safety_factor,
        )
    except Exception:
        pass

    _write_report(selected_ids, full, summary, tdf_cfg, amp_example)

    mond_cfg = models_yaml.get("mond", {})
    log_bounds = tuple(mond_cfg.get("log10_a0_bounds_m_s2", [-11.5, -9.5]))
    log_init = float(mond_cfg.get("log10_a0_initial", -10.0))
    robust = models_yaml.get("robust_fit", {})

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc")
        if g.empty:
            continue
        r = g["r_kpc"].to_numpy()
        v_obs = g["v_obs_kms"].to_numpy()
        v_err = g["v_err_kms"].to_numpy()
        v_bar = g["v_bar_kms"].to_numpy()

        nfw = fit_nfw_baseline_log(
            r,
            v_obs,
            v_err,
            v_bar,
            log10_rho_s_bounds=tuple(robust["nfw"]["log10_rho_s_bounds_msun_kpc3"]),
            log10_r_s_bounds=tuple(robust["nfw"]["log10_r_s_bounds_kpc"]),
        )
        burk = fit_burkert_baseline_log(
            r,
            v_obs,
            v_err,
            v_bar,
            log10_rho_0_bounds=tuple(robust["burkert"]["log10_rho_0_bounds_msun_kpc3"]),
            log10_r_0_bounds=tuple(robust["burkert"]["log10_r_0_bounds_kpc"]),
        )
        mond = fit_mond_a0_simple(
            r,
            v_obs,
            v_err,
            v_bar,
            log10_a0_bounds=log_bounds,
            log10_a0_initial=log_init,
        )

        r_recon, dtaudr_recon = galaxy_tau_reconstruction_arrays(tau_profiles, gid)
        amp_bounds = amplitude_bounds_from_reconstruction(
            dtaudr_recon,
            safety_factor=tdf_cfg.amplitude_bound_safety_factor,
        )

        def _fit_tdf(name: str):
            nk = n_knots_for_model(name)
            kr = fixed_knot_radii_kpc(r, nk)
            x0 = initial_knot_amplitudes_from_reconstruction(kr, r_recon, dtaudr_recon)
            return fit_tdf_knot_baseline(
                r,
                v_obs,
                v_err,
                v_bar,
                model_name=name,
                knot_r_kpc=kr,
                initial_knot_dtaudr=x0,
                dtaudr_bounds=amp_bounds,
                k_g=tdf_cfg.k_g,
                negative_v2_penalty=tdf_cfg.negative_v2_penalty,
            )

        tdf3 = _fit_tdf("tdf_3knot")
        tdf5 = _fit_tdf("tdf_5knot")

        plot_full_model_rotation_comparison(
            gid,
            r,
            v_obs,
            v_err,
            v_bar,
            FIG_DIR / f"{gid}_full_model_rotation_comparison.png",
            v_nfw_kms=nfw.v_model_kms if nfw.fit_success else None,
            v_burkert_kms=burk.v_model_kms if burk.fit_success else None,
            v_mond_fit_kms=mond.v_model_kms if mond.fit_success else None,
            v_tdf_3knot_kms=tdf3.v_model_kms if tdf3.fit_success else None,
            v_tdf_5knot_kms=tdf5.v_model_kms if tdf5.fit_success else None,
        )

    print(f"Wrote full comparison: {FULL_TABLE}")
    print(f"Wrote best-model summary: {SUMMARY_TABLE}")
    print(f"Wrote report: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
