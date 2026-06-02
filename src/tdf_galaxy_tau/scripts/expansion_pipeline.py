from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.metrics.comparison import build_best_model_summary, chi_square, rmse, safe_reduced_chi_square
from tdf_galaxy_tau.metrics.information_criteria import aic, bic, model_parameter_count
from tdf_galaxy_tau.models.fitting import (
    baryonic_only_model,
    fit_burkert_baseline_log,
    fit_mond_a0_simple,
    fit_mond_fixed_a0,
    fit_nfw_baseline_log,
    fit_rar_fixed,
    fit_tdf_knot_baseline,
)
from tdf_galaxy_tau.models.mond import A0_DEFAULT_MS2
from tdf_galaxy_tau.models.tdf_knot import (
    amplitude_bounds_from_reconstruction,
    fixed_knot_radii_kpc,
    galaxy_tau_reconstruction_arrays,
    initial_knot_amplitudes_from_reconstruction,
    load_tdf_knot_config,
    n_knots_for_model,
)
from tdf_galaxy_tau.reconstruction.radial_tau import (
    load_reconstruction_config,
    reconstruct_selected_subset,
)
from tdf_galaxy_tau.validation.failure_modes import (
    HOLDOUT_SPLIT_PRIMARY,
    MANDATED_GALAXY_CLASSIFICATION,
)
from tdf_galaxy_tau.validation.robustness import (
    build_robust_best_model_summary,
    knot_count_stability_table,
)
from tdf_galaxy_tau.validation.tdf_holdout_runner import run_holdout_validation

PIPELINE_STAGE = "phase_5b_expansion12_benchmark"
PIPELINE_STAGE_20 = "phase_5c_expansion20_benchmark"
_ACTIVE_PIPELINE_STAGE = PIPELINE_STAGE

EXPANSION12_COHORT = "expansion_12"
EXPANSION20_COHORT = "expansion_20"

EXPANSION12_ADDITIONS = (
    "UGC02953",
    "UGC05253",
    "NGC5055",
    "UGC00128",
    "NGC0289",
    "DDO161",
)

EXPANSION20_ADDITIONS = (
    "UGC02953",
    "UGC05253",
    "UGC09133",
    "UGC06787",
    "NGC5055",
    "UGC00128",
    "NGC0289",
    "UGC12506",
    "UGC11455",
    "NGC6015",
    "DDO161",
    "NGC7793",
    "UGC07524",
    "UGC08490",
)

FROZEN_SENSITIVITY_RECOVERY = frozenset({"NGC5055", "UGC05253"})
FROZEN_MIXED_RESULT = frozenset({"UGC00128"})
NEAR_TIE_ABS_KMS = 3.0
NEAR_TIE_REL_FRAC = 0.12

REPORT_DISCLAIMER = (
    "Results are for the controlled **expansion_12** cohort only (twelve galaxies). "
    "This is not full-SPARC validation, does not disprove dark matter, does not replace ΛCDM, "
    "and does not include lensing. **tdf_3knot** is the primary conservative TDF model; "
    "**tdf_5knot** is sensitivity/high-flexibility only."
)

REPORT_DISCLAIMER_20 = (
    "Results are for the controlled **expansion_20** cohort only (twenty galaxies). "
    "This is not full-SPARC validation, does not disprove dark matter, does not replace ΛCDM, "
    "and does not include lensing. **tdf_3knot** is the primary conservative model; "
    "**tdf_5knot** is sensitivity/high-flexibility only and must not be counted as primary success. "
    "**sensitivity_recovery** cases (tdf_3knot holdout failure with tdf_5knot recovery) are "
    "reported separately from **robust_tdf_success**."
)


def load_expansion_cohort_ids(
    plan_path: Path | str,
    cohort_name: str,
) -> list[str]:
    plan = pd.read_csv(plan_path)
    sub = plan[(plan["cohort_name"] == cohort_name) & (plan["in_cohort"].astype(bool))]
    return sub.sort_values("selection_order")["galaxy_id"].astype(str).tolist()


def load_expansion12_galaxy_ids(
    plan_path: Path | str = "outputs/tables/sparc_subset_expansion_plan.csv",
) -> list[str]:
    return load_expansion_cohort_ids(plan_path, EXPANSION12_COHORT)


def load_expansion20_galaxy_ids(
    plan_path: Path | str = "outputs/tables/sparc_subset_expansion_plan.csv",
) -> list[str]:
    return load_expansion_cohort_ids(plan_path, EXPANSION20_COHORT)


def write_expansion_subset_csv(
    galaxy_ids: list[str],
    *,
    cohort_name: str,
    rotmod_path: Path | str = "data/processed/sparc/sparc_rotmod_standardized.csv",
    out_path: Path | str,
) -> pd.DataFrame:
    rotmod = pd.read_csv(rotmod_path)
    rows: list[dict[str, Any]] = []
    for rank, gid in enumerate(galaxy_ids, start=1):
        g = rotmod[rotmod["galaxy_id"] == gid].sort_values("r_kpc")
        if g.empty:
            continue
        r_min = float(g["r_kpc"].min())
        r_max = float(g["r_kpc"].max())
        rows.append(
            {
                "galaxy_id": gid,
                "selected": True,
                "selection_rank": float(rank),
                "n_points": len(g),
                "r_min_kpc": r_min,
                "r_max_kpc": r_max,
                "radial_coverage_kpc": r_max - r_min,
                "v_obs_min_kms": float(g["v_obs_kms"].min()),
                "v_obs_max_kms": float(g["v_obs_kms"].max()),
                "median_v_err_kms": float(g["v_err_kms"].median()),
                "has_bulge": bool((g["v_bulge_kms"].abs() > 0).any()),
                "quality_flag": "selected",
                "cohort": cohort_name,
            }
        )
    df = pd.DataFrame(rows)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return df


def write_expansion12_subset_csv(
    galaxy_ids: list[str],
    *,
    rotmod_path: Path | str = "data/processed/sparc/sparc_rotmod_standardized.csv",
    out_path: Path | str = "outputs/tables/expansion12_subset_selection.csv",
) -> pd.DataFrame:
    """Build subset-selection-compatible CSV for expansion_12."""
    return write_expansion_subset_csv(
        galaxy_ids,
        cohort_name=EXPANSION12_COHORT,
        rotmod_path=rotmod_path,
        out_path=out_path,
    )


def write_expansion20_subset_csv(
    galaxy_ids: list[str],
    *,
    rotmod_path: Path | str = "data/processed/sparc/sparc_rotmod_standardized.csv",
    out_path: Path | str = "outputs/tables/expansion20_subset_selection.csv",
) -> pd.DataFrame:
    return write_expansion_subset_csv(
        galaxy_ids,
        cohort_name=EXPANSION20_COHORT,
        rotmod_path=rotmod_path,
        out_path=out_path,
    )


def _metrics_row(
    galaxy_id: str,
    model_name: str,
    n_points: int,
    v_obs: np.ndarray,
    v_model: np.ndarray,
    v_err: np.ndarray,
    *,
    fit_success: bool,
    fit_status: str,
    data_source: str,
    data_mode: str,
) -> dict[str, Any]:
    n_params = model_parameter_count(model_name)
    chi2 = chi_square(v_obs, v_model, v_err)
    return {
        "galaxy_id": galaxy_id,
        "model_name": model_name,
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
        "comparison_stage": _ACTIVE_PIPELINE_STAGE,
    }


def fit_halo_and_baryon_models(
    selected_ids: list[str],
    data: pd.DataFrame,
    models_yaml: dict[str, Any],
) -> pd.DataFrame:
    robust = models_yaml.get("robust_fit", {})
    nfw_b = robust.get("nfw", {})
    burk_b = robust.get("burkert", {})
    rows: list[dict[str, Any]] = []

    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc").reset_index(drop=True)
        if g.empty:
            continue
        r = g["r_kpc"].to_numpy(dtype=float)
        v_obs = g["v_obs_kms"].to_numpy(dtype=float)
        v_err = g["v_err_kms"].to_numpy(dtype=float)
        v_bar = g["v_bar_kms"].to_numpy(dtype=float)
        ds = str(g["data_source"].iloc[0])
        dm = str(g["data_mode"].iloc[0])

        bary = baryonic_only_model(v_bar)
        rows.append(
            _metrics_row(
                gid,
                "baryonic_only",
                len(g),
                v_obs,
                bary.v_model_kms,
                v_err,
                fit_success=True,
                fit_status=bary.fit_status,
                data_source=ds,
                data_mode=dm,
            )
        )

        nfw = fit_nfw_baseline_log(
            r,
            v_obs,
            v_err,
            v_bar,
            log10_rho_s_bounds=tuple(nfw_b["log10_rho_s_bounds_msun_kpc3"]),
            log10_r_s_bounds=tuple(nfw_b["log10_r_s_bounds_kpc"]),
        )
        rows.append(
            _metrics_row(
                gid,
                "nfw_refit",
                len(g),
                v_obs,
                nfw.v_model_kms if nfw.fit_success else v_bar,
                v_err,
                fit_success=nfw.fit_success,
                fit_status=nfw.fit_status,
                data_source=ds,
                data_mode=dm,
            )
        )

        burk = fit_burkert_baseline_log(
            r,
            v_obs,
            v_err,
            v_bar,
            log10_rho_0_bounds=tuple(burk_b["log10_rho_0_bounds_msun_kpc3"]),
            log10_r_0_bounds=tuple(burk_b["log10_r_0_bounds_kpc"]),
        )
        rows.append(
            _metrics_row(
                gid,
                "burkert_refit",
                len(g),
                v_obs,
                burk.v_model_kms if burk.fit_success else v_bar,
                v_err,
                fit_success=burk.fit_success,
                fit_status=burk.fit_status,
                data_source=ds,
                data_mode=dm,
            )
        )
    return pd.DataFrame(rows)


def fit_mond_rar_models(
    selected_ids: list[str],
    data: pd.DataFrame,
    models_yaml: dict[str, Any],
) -> pd.DataFrame:
    mond_cfg = models_yaml.get("mond", {})
    a0_fixed = float(mond_cfg.get("a0_fixed_m_s2", A0_DEFAULT_MS2))
    g_dagger = float(mond_cfg.get("g_dagger_fixed_m_s2", A0_DEFAULT_MS2))
    log_bounds = tuple(mond_cfg.get("log10_a0_bounds_m_s2", [-11.5, -9.5]))
    log_init = float(mond_cfg.get("log10_a0_initial", -10.0))
    enable_rar = bool(mond_cfg.get("enable_rar_fixed", True))
    rows: list[dict[str, Any]] = []

    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc").reset_index(drop=True)
        if g.empty:
            continue
        r = g["r_kpc"].to_numpy(dtype=float)
        v_obs = g["v_obs_kms"].to_numpy(dtype=float)
        v_err = g["v_err_kms"].to_numpy(dtype=float)
        v_bar = g["v_bar_kms"].to_numpy(dtype=float)
        ds = str(g["data_source"].iloc[0])
        dm = str(g["data_mode"].iloc[0])

        fixed = fit_mond_fixed_a0(r, v_obs, v_err, v_bar, a0_ms2=a0_fixed)
        rows.append(
            _metrics_row(
                gid,
                "mond_fixed_a0_simple",
                len(g),
                v_obs,
                fixed.v_model_kms if fixed.fit_success else v_bar,
                v_err,
                fit_success=fixed.fit_success,
                fit_status=fixed.fit_status,
                data_source=ds,
                data_mode=dm,
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
        rows.append(
            _metrics_row(
                gid,
                "mond_fit_a0_simple",
                len(g),
                v_obs,
                fitted.v_model_kms if fitted.fit_success else v_bar,
                v_err,
                fit_success=fitted.fit_success,
                fit_status=fitted.fit_status,
                data_source=ds,
                data_mode=dm,
            )
        )

        if enable_rar:
            rar = fit_rar_fixed(r, v_obs, v_err, v_bar, g_dagger_ms2=g_dagger)
            rows.append(
                _metrics_row(
                    gid,
                    "rar_fixed",
                    len(g),
                    v_obs,
                    rar.v_model_kms if rar.fit_success else v_bar,
                    v_err,
                    fit_success=rar.fit_success,
                    fit_status=rar.fit_status,
                    data_source=ds,
                    data_mode=dm,
                )
            )
    return pd.DataFrame(rows)


def fit_tdf_knot_models(
    selected_ids: list[str],
    data: pd.DataFrame,
    tau_profiles: pd.DataFrame,
    recon_yaml: dict[str, Any],
) -> pd.DataFrame:
    tdf_cfg = load_tdf_knot_config(recon_yaml)
    rows: list[dict[str, Any]] = []

    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc").reset_index(drop=True)
        if g.empty:
            continue
        r = g["r_kpc"].to_numpy(dtype=float)
        v_obs = g["v_obs_kms"].to_numpy(dtype=float)
        v_err = g["v_err_kms"].to_numpy(dtype=float)
        v_bar = g["v_bar_kms"].to_numpy(dtype=float)
        ds = str(g["data_source"].iloc[0])
        dm = str(g["data_mode"].iloc[0])

        r_recon, dtaudr_recon = galaxy_tau_reconstruction_arrays(tau_profiles, gid)
        amp_bounds = amplitude_bounds_from_reconstruction(
            dtaudr_recon,
            safety_factor=tdf_cfg.amplitude_bound_safety_factor,
        )

        for model_name in tdf_cfg.variants:
            n_knots = n_knots_for_model(model_name)
            knot_r = fixed_knot_radii_kpc(r, n_knots)
            x0 = initial_knot_amplitudes_from_reconstruction(knot_r, r_recon, dtaudr_recon)
            fit = fit_tdf_knot_baseline(
                r,
                v_obs,
                v_err,
                v_bar,
                model_name=model_name,
                knot_r_kpc=knot_r,
                initial_knot_dtaudr=x0,
                dtaudr_bounds=amp_bounds,
                k_g=tdf_cfg.k_g,
                negative_v2_penalty=tdf_cfg.negative_v2_penalty,
            )
            rows.append(
                _metrics_row(
                    gid,
                    model_name,
                    len(g),
                    v_obs,
                    fit.v_model_kms if fit.fit_success else v_bar,
                    v_err,
                    fit_success=fit.fit_success,
                    fit_status=fit.fit_status,
                    data_source=ds,
                    data_mode=dm,
                )
            )
    return pd.DataFrame(rows)


def classify_expansion12_failure_mode(
    galaxy_id: str,
    holdout: pd.DataFrame,
    *,
    original_classifications: dict[str, str] | None = None,
) -> str:
    """Assign failure-mode label; preserve mandated labels for original six."""
    orig = original_classifications or MANDATED_GALAXY_CLASSIFICATION
    if galaxy_id in orig:
        return orig[galaxy_id]

    ho = holdout[
        (holdout["galaxy_id"] == galaxy_id) & (holdout["split_name"] == HOLDOUT_SPLIT_PRIMARY)
    ]
    if ho.empty:
        return "mixed_result"

    def _rmse(model: str) -> float:
        sub = ho[ho["model_name"] == model]
        return float(sub.iloc[0]["test_rmse_kms"]) if not sub.empty else float("nan")

    tdf3 = _rmse("tdf_3knot")
    nfw = _rmse("nfw_refit")
    mond = _rmse("mond_fit_a0_simple")

    if not np.isfinite(tdf3) or not np.isfinite(nfw):
        return "mixed_result"

    if tdf3 > nfw * 2.0 and (not np.isfinite(mond) or tdf3 > mond * 2.0):
        return "tdf_failure_mode"

    if np.isfinite(mond) and tdf3 < nfw and tdf3 < mond:
        return "robust_tdf_success"

    if tdf3 < nfw:
        return "robust_tdf_success"

    return "mixed_result"


def _holdout_rmse_map(galaxy_id: str, holdout: pd.DataFrame) -> dict[str, float]:
    ho = holdout[
        (holdout["galaxy_id"] == galaxy_id) & (holdout["split_name"] == HOLDOUT_SPLIT_PRIMARY)
    ]

    def _rmse(model: str) -> float:
        sub = ho[ho["model_name"] == model]
        return float(sub.iloc[0]["test_rmse_kms"]) if not sub.empty else float("nan")

    return {
        "tdf_3knot": _rmse("tdf_3knot"),
        "tdf_5knot": _rmse("tdf_5knot"),
        "nfw_refit": _rmse("nfw_refit"),
        "mond_fit_a0_simple": _rmse("mond_fit_a0_simple"),
    }


def _is_near_tie(rmses: dict[str, float]) -> bool:
    ranked = sorted(
        [(m, v) for m, v in rmses.items() if np.isfinite(v)],
        key=lambda x: x[1],
    )
    if len(ranked) < 2:
        return False
    best_v = ranked[0][1]
    second_v = ranked[1][1]
    gap = second_v - best_v
    if gap <= NEAR_TIE_ABS_KMS:
        return True
    return bool(best_v > 0 and gap / best_v <= NEAR_TIE_REL_FRAC)


def classify_expansion20_failure_mode_from_holdout(
    galaxy_id: str,
    holdout: pd.DataFrame,
) -> str:
    """Phase 5C rules: robust / all-TDF failure / sensitivity_recovery / mixed."""
    rmses = _holdout_rmse_map(galaxy_id, holdout)
    t3 = rmses["tdf_3knot"]
    t5 = rmses["tdf_5knot"]
    nfw = rmses["nfw_refit"]
    mond = rmses["mond_fit_a0_simple"]

    if not np.isfinite(t3) or not np.isfinite(nfw):
        return "mixed_result"

    t3_beats_both = np.isfinite(mond) and t3 < nfw and t3 < mond
    if t3_beats_both:
        return "robust_tdf_success"

    t5_beats_both = (
        np.isfinite(t5) and np.isfinite(mond) and t5 < nfw and t5 < mond
    )
    if t5_beats_both and not t3_beats_both:
        return "sensitivity_recovery"

    t5_fails_baselines = not t5_beats_both
    if t5_fails_baselines and (
        t3 > nfw * 2.0 or (np.isfinite(mond) and t3 > mond * 2.0)
    ):
        return "tdf_failure_mode"
    if t5_fails_baselines:
        return "tdf_failure_mode"

    if _is_near_tie(rmses):
        return "mixed_result"

    return "mixed_result"


def classify_expansion20_failure_mode(galaxy_id: str, holdout: pd.DataFrame) -> str:
    """Apply Phase 5B-Audit / 5B-R frozen guardrails then holdout rules."""
    if galaxy_id == "NGC7814":
        return "tdf_failure_mode"
    if galaxy_id in MANDATED_GALAXY_CLASSIFICATION and galaxy_id != "NGC7814":
        return MANDATED_GALAXY_CLASSIFICATION[galaxy_id]
    if galaxy_id in FROZEN_SENSITIVITY_RECOVERY:
        return "sensitivity_recovery"
    if galaxy_id in FROZEN_MIXED_RESULT:
        computed = classify_expansion20_failure_mode_from_holdout(galaxy_id, holdout)
        if computed == "robust_tdf_success":
            return computed
        return "mixed_result"
    return classify_expansion20_failure_mode_from_holdout(galaxy_id, holdout)


def build_expansion12_failure_summary(
    full_comparison: pd.DataFrame,
    best_summary: pd.DataFrame,
    holdout: pd.DataFrame,
    robust_best: pd.DataFrame,
) -> pd.DataFrame:
    ho = holdout[holdout["split_name"] == HOLDOUT_SPLIT_PRIMARY]
    rows: list[dict[str, Any]] = []

    for gid in sorted(full_comparison["galaxy_id"].unique()):
        classification = classify_expansion12_failure_mode(gid, holdout)
        bm = best_summary[best_summary["galaxy_id"] == gid]
        rb = robust_best[robust_best["galaxy_id"] == gid]
        sub_ho = ho[ho["galaxy_id"] == gid]

        def _ho_rmse(model: str) -> float:
            s = sub_ho[sub_ho["model_name"] == model]
            return float(s.iloc[0]["test_rmse_kms"]) if not s.empty else float("nan")

        best_ho = (
            str(sub_ho.loc[sub_ho["test_rmse_kms"].idxmin(), "model_name"])
            if not sub_ho.empty
            else "unknown"
        )

        cohort_role = (
            "original_controlled_six"
            if gid in MANDATED_GALAXY_CLASSIFICATION
            else "expansion_addition"
        )

        rows.append(
            {
                "galaxy_id": gid,
                "cohort_role": cohort_role,
                "failure_mode_classification": classification,
                "in_sample_best_by_aic": str(bm.iloc[0]["best_by_aic"]) if not bm.empty else "",
                "in_sample_best_by_rmse": str(bm.iloc[0]["best_by_rmse"]) if not bm.empty else "",
                "holdout_best_by_test_rmse": best_ho,
                "tdf_3knot_holdout_rmse_kms": _ho_rmse("tdf_3knot"),
                "tdf_5knot_holdout_rmse_kms": _ho_rmse("tdf_5knot"),
                "nfw_refit_holdout_rmse_kms": _ho_rmse("nfw_refit"),
                "mond_fit_a0_holdout_rmse_kms": _ho_rmse("mond_fit_a0_simple"),
                "tdf_3knot_beats_nfw_holdout": bool(rb.iloc[0]["tdf_3knot_beats_nfw_holdout_rmse"])
                if not rb.empty
                else False,
                "primary_tdf_model": "tdf_3knot",
                "sensitivity_tdf_model": "tdf_5knot",
                "recommended_interpretation": _interpretation(classification, gid),
            }
        )
    return pd.DataFrame(rows)


def build_expansion20_failure_summary(
    full_comparison: pd.DataFrame,
    best_summary: pd.DataFrame,
    holdout: pd.DataFrame,
    robust_best: pd.DataFrame,
) -> pd.DataFrame:
    ho = holdout[holdout["split_name"] == HOLDOUT_SPLIT_PRIMARY]
    rows: list[dict[str, Any]] = []

    for gid in sorted(full_comparison["galaxy_id"].unique()):
        classification = classify_expansion20_failure_mode(gid, holdout)
        bm = best_summary[best_summary["galaxy_id"] == gid]
        rb = robust_best[robust_best["galaxy_id"] == gid]
        sub_ho = ho[ho["galaxy_id"] == gid]

        def _ho_rmse(model: str) -> float:
            s = sub_ho[sub_ho["model_name"] == model]
            return float(s.iloc[0]["test_rmse_kms"]) if not s.empty else float("nan")

        best_ho = (
            str(sub_ho.loc[sub_ho["test_rmse_kms"].idxmin(), "model_name"])
            if not sub_ho.empty
            else "unknown"
        )

        cohort_role = (
            "original_controlled_six"
            if gid in MANDATED_GALAXY_CLASSIFICATION
            else "expansion_addition"
        )

        rows.append(
            {
                "galaxy_id": gid,
                "cohort_role": cohort_role,
                "failure_mode_classification": classification,
                "in_sample_best_by_aic": str(bm.iloc[0]["best_by_aic"]) if not bm.empty else "",
                "in_sample_best_by_rmse": str(bm.iloc[0]["best_by_rmse"]) if not bm.empty else "",
                "holdout_best_by_test_rmse": best_ho,
                "tdf_3knot_holdout_rmse_kms": _ho_rmse("tdf_3knot"),
                "tdf_5knot_holdout_rmse_kms": _ho_rmse("tdf_5knot"),
                "nfw_refit_holdout_rmse_kms": _ho_rmse("nfw_refit"),
                "mond_fit_a0_holdout_rmse_kms": _ho_rmse("mond_fit_a0_simple"),
                "tdf_3knot_beats_nfw_holdout": bool(rb.iloc[0]["tdf_3knot_beats_nfw_holdout_rmse"])
                if not rb.empty
                else False,
                "tdf_3knot_beats_mond_holdout": bool(
                    np.isfinite(_ho_rmse("tdf_3knot"))
                    and np.isfinite(_ho_rmse("mond_fit_a0_simple"))
                    and _ho_rmse("tdf_3knot") < _ho_rmse("mond_fit_a0_simple")
                ),
                "primary_tdf_model": "tdf_3knot",
                "sensitivity_tdf_model": "tdf_5knot",
                "counts_as_primary_success": classification == "robust_tdf_success",
                "recommended_interpretation": _interpretation_20(classification, gid),
            }
        )
    return pd.DataFrame(rows)


def _interpretation(classification: str, galaxy_id: str) -> str:
    if classification == "robust_tdf_success":
        return (
            f"{galaxy_id}: primary tdf_3knot competitive on even/odd holdout "
            "(expansion_12; fixed baryons, fixed K_g; legacy K_tau label in frozen tables)."
        )
    if classification == "tdf_failure_mode":
        return (
            f"{galaxy_id}: canonical-style TDF holdout failure; report honestly "
            "(expansion_12 diagnostic)."
        )
    return f"{galaxy_id}: mixed or inconclusive under expansion_12 criteria."


def _interpretation_20(classification: str, galaxy_id: str) -> str:
    if classification == "robust_tdf_success":
        return (
            f"{galaxy_id}: primary tdf_3knot beats NFW and MOND on even/odd holdout "
            "(expansion_20; fixed baryons, fixed K_g; legacy K_tau label in frozen tables)."
        )
    if classification == "sensitivity_recovery":
        return (
            f"{galaxy_id}: tdf_3knot holdout failure with tdf_5knot recovery — "
            "sensitivity/high-flexibility only; not primary success (Phase 5B-R guardrail)."
        )
    if classification == "tdf_failure_mode":
        if galaxy_id == "NGC7814":
            return (
                f"{galaxy_id}: canonical all-TDF holdout failure; mandated label preserved."
            )
        return (
            f"{galaxy_id}: tdf_3knot and tdf_5knot fail vs baselines on holdout; report honestly."
        )
    if galaxy_id == "UGC00128":
        return (
            f"{galaxy_id}: near-tie/mixed holdout; not counted as primary success "
            "(Phase 5B-Audit guardrail)."
        )
    return f"{galaxy_id}: mixed or unstable under expansion_20 criteria."


def build_expansion12_claim_traceability() -> pd.DataFrame:
    rows = [
        {
            "claim_id": "E12-A",
            "claim_text": "Radial τ reconstruction can be generated for all expansion_12 galaxies.",
            "status": "supported",
            "allowed_language": "direct radial τ reconstruction for expansion_12 cohort",
            "prohibited_language": "full-SPARC validation; universal τ-profile",
        },
        {
            "claim_id": "E12-B",
            "claim_text": "TDF knot models are competitive in-sample on expansion_12.",
            "status": "supported_with_caveat",
            "allowed_language": "competitive on controlled expansion_12 subset (in-sample)",
            "prohibited_language": "validated on SPARC; TDF disproves dark matter",
        },
        {
            "claim_id": "E12-C",
            "claim_text": "Primary tdf_3knot holdout performance on expansion_12.",
            "status": "partially_supported",
            "allowed_language": "holdout success/failure per galaxy; count primary tdf_3knot wins",
            "prohibited_language": "TDF validated on SPARC; all galaxies success",
        },
        {
            "claim_id": "E12-D",
            "claim_text": "TDF validates on full SPARC.",
            "status": "not_supported",
            "allowed_language": "expansion_12 controlled cohort only",
            "prohibited_language": "validated on SPARC; SPARC validates TDF",
        },
        {
            "claim_id": "E12-E",
            "claim_text": "Dark matter is disproven.",
            "status": "prohibited",
            "allowed_language": "does not disprove dark matter",
            "prohibited_language": "dark matter disproven; DM is wrong",
        },
        {
            "claim_id": "E12-F",
            "claim_text": "Lensing confirms TDF.",
            "status": "not_tested",
            "allowed_language": "lensing not tested",
            "prohibited_language": "lensing confirmed",
        },
    ]
    return pd.DataFrame(rows)


def build_expansion20_claim_traceability() -> pd.DataFrame:
    rows = [
        {
            "claim_id": "E20-A",
            "claim_text": "Radial τ reconstruction for all expansion_20 galaxies.",
            "status": "supported",
            "allowed_language": "τ reconstruction on controlled expansion_20 cohort",
            "prohibited_language": "full-SPARC validation; universal τ-profile",
        },
        {
            "claim_id": "E20-B",
            "claim_text": "Primary tdf_3knot holdout success on expansion_20.",
            "status": "partially_supported",
            "allowed_language": "count robust_tdf_success only (tdf_3knot beats NFW and MOND)",
            "prohibited_language": "count tdf_5knot as primary success; all galaxies pass",
        },
        {
            "claim_id": "E20-C",
            "claim_text": "sensitivity_recovery equals scientific validation.",
            "status": "not_supported",
            "allowed_language": "report sensitivity_recovery separately from robust success",
            "prohibited_language": "tdf_5knot validates TDF; flex recovery is primary win",
        },
        {
            "claim_id": "E20-D",
            "claim_text": "TDF validated on full SPARC.",
            "status": "not_supported",
            "allowed_language": "expansion_20 controlled cohort only",
            "prohibited_language": "validated on SPARC; SPARC validates TDF",
        },
        {
            "claim_id": "E20-E",
            "claim_text": "Dark matter is disproven.",
            "status": "prohibited",
            "allowed_language": "does not disprove dark matter",
            "prohibited_language": "dark matter disproven; DM is wrong; ΛCDM replaced",
        },
        {
            "claim_id": "E20-F",
            "claim_text": "Lensing confirms TDF.",
            "status": "not_tested",
            "allowed_language": "lensing not tested",
            "prohibited_language": "lensing confirmed",
        },
    ]
    return pd.DataFrame(rows)


def write_expansion12_benchmark_report(
    path: Path,
    *,
    galaxy_ids: list[str],
    failure_summary: pd.DataFrame,
    holdout: pd.DataFrame,
    full_comparison: pd.DataFrame,
) -> None:
    ho = holdout[holdout["split_name"] == HOLDOUT_SPLIT_PRIMARY]
    n_robust = int((failure_summary["failure_mode_classification"] == "robust_tdf_success").sum())
    n_fail = int((failure_summary["failure_mode_classification"] == "tdf_failure_mode").sum())
    n_mixed = len(failure_summary) - n_robust - n_fail

    tdf3_beats_nfw = int(failure_summary["tdf_3knot_beats_nfw_holdout"].sum())

    lines = [
        "# Expansion-12 Controlled Benchmark Report (Phase 5B)",
        "",
        f"> {REPORT_DISCLAIMER}",
        "",
        "## Cohort",
        "",
        f"Galaxies ({len(galaxy_ids)}): {', '.join(galaxy_ids)}",
        "",
        f"- Original six: {', '.join(MANDATED_GALAXY_CLASSIFICATION.keys())}",
        f"- Phase 5A additions: {', '.join(EXPANSION12_ADDITIONS)}",
        "",
        "## Failure-mode summary",
        "",
        f"- **robust_tdf_success:** {n_robust}",
        f"- **tdf_failure_mode:** {n_fail}",
        f"- **mixed_result / other:** {n_mixed}",
        f"- Primary **tdf_3knot** beats **nfw_refit** on holdout: **{tdf3_beats_nfw}** / {len(failure_summary)} galaxies",
        "",
        "## Per-galaxy holdout (even/odd, km/s)",
        "",
        "| Galaxy | Class | tdf_3knot | tdf_5knot | nfw_refit | mond_fit | Best |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]

    for _, row in failure_summary.sort_values("galaxy_id").iterrows():
        gid = row["galaxy_id"]
        sub = ho[ho["galaxy_id"] == gid]
        best = row["holdout_best_by_test_rmse"]
        lines.append(
            f"| {gid} | {row['failure_mode_classification']} | "
            f"{row['tdf_3knot_holdout_rmse_kms']:.1f} | {row['tdf_5knot_holdout_rmse_kms']:.1f} | "
            f"{row['nfw_refit_holdout_rmse_kms']:.1f} | {row['mond_fit_a0_holdout_rmse_kms']:.1f} | {best} |"
        )

    lines.extend(
        [
            "",
            "## TDF vs NFW/MOND (holdout)",
            "",
            "Primary reporting uses **tdf_3knot**. **tdf_5knot** is documented as sensitivity only. "
            "In-sample metrics often favor higher knot counts; holdout is the gate for predictive claims.",
            "",
            "## Claim boundaries",
            "",
            "See `outputs/tables/expansion12_claim_traceability.csv`. "
            "Do not claim full-SPARC validation, final M/L calibration, or dark-matter disproof.",
            "",
            "## Outputs",
            "",
            "- `outputs/tables/expansion12_model_comparison.csv`",
            "- `outputs/tables/expansion12_holdout_validation.csv`",
            "- `outputs/tables/expansion12_failure_mode_summary.csv`",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_expansion20_benchmark_report(
    path: Path,
    *,
    galaxy_ids: list[str],
    failure_summary: pd.DataFrame,
    holdout: pd.DataFrame,
) -> None:
    ho = holdout[holdout["split_name"] == HOLDOUT_SPLIT_PRIMARY]
    n_robust = int((failure_summary["failure_mode_classification"] == "robust_tdf_success").sum())
    n_sens = int((failure_summary["failure_mode_classification"] == "sensitivity_recovery").sum())
    n_fail = int((failure_summary["failure_mode_classification"] == "tdf_failure_mode").sum())
    n_mixed = int((failure_summary["failure_mode_classification"] == "mixed_result").sum())
    primary_success = int(failure_summary["counts_as_primary_success"].sum())
    tdf3_beats_nfw = int(failure_summary["tdf_3knot_beats_nfw_holdout"].sum())
    tdf3_beats_mond = int(failure_summary["tdf_3knot_beats_mond_holdout"].sum())

    lines = [
        "# Expansion-20 Controlled Benchmark Report (Phase 5C)",
        "",
        f"> {REPORT_DISCLAIMER_20}",
        "",
        "## Cohort",
        "",
        f"Galaxies ({len(galaxy_ids)}): {', '.join(galaxy_ids)}",
        "",
        f"- Original six: {', '.join(MANDATED_GALAXY_CLASSIFICATION.keys())}",
        f"- Phase 5A additions ({len(EXPANSION20_ADDITIONS)}): {', '.join(EXPANSION20_ADDITIONS)}",
        "",
        "## Classification summary (primary = tdf_3knot only)",
        "",
        f"- **robust_tdf_success:** {n_robust} (counts toward primary success: **{primary_success}**)",
        f"- **sensitivity_recovery:** {n_sens} (tdf_5knot recovery — **not** primary success)",
        f"- **tdf_failure_mode:** {n_fail}",
        f"- **mixed_result:** {n_mixed}",
        "",
        f"- Primary **tdf_3knot** beats **nfw_refit** on holdout: **{tdf3_beats_nfw}** / {len(failure_summary)}",
        f"- Primary **tdf_3knot** beats **mond_fit** on holdout: **{tdf3_beats_mond}** / {len(failure_summary)}",
        "",
        "### Frozen guardrails (Phase 5B-Audit / 5B-R)",
        "",
        "- **NGC7814:** canonical all-TDF failure (mandated).",
        "- **NGC5055, UGC05253:** sensitivity_recovery (not robust success).",
        "- **UGC00128:** mixed/near-tie unless tdf_3knot beats both baselines.",
        "",
        "## Per-galaxy holdout (even/odd, km/s)",
        "",
        "| Galaxy | Class | Primary? | tdf_3knot | tdf_5knot | nfw | mond | Best |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]

    for _, row in failure_summary.sort_values("galaxy_id").iterrows():
        primary = "yes" if row["counts_as_primary_success"] else "no"
        lines.append(
            f"| {row['galaxy_id']} | {row['failure_mode_classification']} | {primary} | "
            f"{row['tdf_3knot_holdout_rmse_kms']:.1f} | {row['tdf_5knot_holdout_rmse_kms']:.1f} | "
            f"{row['nfw_refit_holdout_rmse_kms']:.1f} | {row['mond_fit_a0_holdout_rmse_kms']:.1f} | "
            f"{row['holdout_best_by_test_rmse']} |"
        )

    lines.extend(
        [
            "",
            "## TDF vs NFW/MOND",
            "",
            "Holdout gates predictive claims. **tdf_5knot** may beat baselines where **tdf_3knot** fails; "
            "such cases are **sensitivity_recovery**, not robust primary success.",
            "",
            "## Claim boundaries",
            "",
            "See `outputs/tables/expansion20_claim_traceability.csv`. "
            "No full-SPARC validation, no dark-matter disproof, no lensing.",
            "",
            "## Outputs",
            "",
            "- `outputs/tables/expansion20_model_comparison.csv`",
            "- `outputs/tables/expansion20_holdout_validation.csv`",
            "- `outputs/tables/expansion20_failure_mode_summary.csv`",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_expansion12_benchmark(
    *,
    rotmod_path: Path | str = "data/processed/sparc/sparc_rotmod_standardized.csv",
    plan_path: Path | str = "outputs/tables/sparc_subset_expansion_plan.csv",
    recon_path: Path | str = "configs/reconstruction.yaml",
    models_path: Path | str = "configs/models.yaml",
    subset_out: Path | str = "outputs/tables/expansion12_subset_selection.csv",
    tau_out: Path | str = "outputs/tables/expansion12_tau_profiles.csv",
    comparison_out: Path | str = "outputs/tables/expansion12_model_comparison.csv",
    holdout_out: Path | str = "outputs/tables/expansion12_holdout_validation.csv",
    failure_out: Path | str = "outputs/tables/expansion12_failure_mode_summary.csv",
    claims_out: Path | str = "outputs/tables/expansion12_claim_traceability.csv",
    report_out: Path | str = "outputs/reports/expansion12_benchmark_report.md",
) -> dict[str, pd.DataFrame]:
    global _ACTIVE_PIPELINE_STAGE
    _ACTIVE_PIPELINE_STAGE = PIPELINE_STAGE

    galaxy_ids = load_expansion12_galaxy_ids(plan_path)
    if len(galaxy_ids) != 12:
        raise ValueError(f"expected 12 expansion_12 galaxies, got {len(galaxy_ids)}")

    write_expansion12_subset_csv(galaxy_ids, rotmod_path=rotmod_path, out_path=subset_out)

    recon_cfg = load_reconstruction_config(recon_path)
    recon_yaml = yaml.safe_load(Path(recon_path).read_text(encoding="utf-8")) or {}
    models_yaml = yaml.safe_load(Path(models_path).read_text(encoding="utf-8")) or {}

    data = pd.read_csv(rotmod_path)
    data = data[data["galaxy_id"].isin(galaxy_ids)].copy()

    tau_df = reconstruct_selected_subset(rotmod_path, subset_out, recon_cfg)
    tau_df.to_csv(tau_out, index=False)

    halo = fit_halo_and_baryon_models(galaxy_ids, data, models_yaml)
    mond = fit_mond_rar_models(galaxy_ids, data, models_yaml)
    tdf = fit_tdf_knot_models(galaxy_ids, data, tau_df, recon_yaml)
    full = pd.concat([halo, mond, tdf], ignore_index=True)
    full.to_csv(comparison_out, index=False)

    audit_cfg = recon_yaml.get("tdf_robustness_audit", {})
    tdf_models = tuple(audit_cfg.get("holdout_tdf_models", ["tdf_3knot", "tdf_5knot"]))
    holdout = run_holdout_validation(
        data,
        tau_df,
        galaxy_ids,
        recon_yaml,
        models_yaml,
        tdf_models=tdf_models,
    )
    holdout.to_csv(holdout_out, index=False)

    best_summary = build_best_model_summary(full)
    tdf_only = full[full["model_name"].str.startswith("tdf_")]
    knot_stab = knot_count_stability_table(tdf_only)
    robust_best = build_robust_best_model_summary(holdout, best_summary, knot_stab)
    failure_summary = build_expansion12_failure_summary(full, best_summary, holdout, robust_best)
    failure_summary.to_csv(failure_out, index=False)

    claims = build_expansion12_claim_traceability()
    claims.to_csv(claims_out, index=False)

    write_expansion12_benchmark_report(
        report_out,
        galaxy_ids=galaxy_ids,
        failure_summary=failure_summary,
        holdout=holdout,
        full_comparison=full,
    )

    return {
        "galaxy_ids": galaxy_ids,
        "tau_profiles": tau_df,
        "model_comparison": full,
        "holdout_validation": holdout,
        "failure_mode_summary": failure_summary,
        "claim_traceability": claims,
    }


def run_expansion20_benchmark(
    *,
    rotmod_path: Path | str = "data/processed/sparc/sparc_rotmod_standardized.csv",
    plan_path: Path | str = "outputs/tables/sparc_subset_expansion_plan.csv",
    recon_path: Path | str = "configs/reconstruction.yaml",
    models_path: Path | str = "configs/models.yaml",
    subset_out: Path | str = "outputs/tables/expansion20_subset_selection.csv",
    tau_out: Path | str = "outputs/tables/expansion20_tau_profiles.csv",
    comparison_out: Path | str = "outputs/tables/expansion20_model_comparison.csv",
    holdout_out: Path | str = "outputs/tables/expansion20_holdout_validation.csv",
    failure_out: Path | str = "outputs/tables/expansion20_failure_mode_summary.csv",
    claims_out: Path | str = "outputs/tables/expansion20_claim_traceability.csv",
    report_out: Path | str = "outputs/reports/expansion20_benchmark_report.md",
) -> dict[str, pd.DataFrame]:
    global _ACTIVE_PIPELINE_STAGE
    _ACTIVE_PIPELINE_STAGE = PIPELINE_STAGE_20

    galaxy_ids = load_expansion20_galaxy_ids(plan_path)
    if len(galaxy_ids) != 20:
        raise ValueError(f"expected 20 expansion_20 galaxies, got {len(galaxy_ids)}")

    write_expansion20_subset_csv(galaxy_ids, rotmod_path=rotmod_path, out_path=subset_out)

    recon_cfg = load_reconstruction_config(recon_path)
    recon_yaml = yaml.safe_load(Path(recon_path).read_text(encoding="utf-8")) or {}
    models_yaml = yaml.safe_load(Path(models_path).read_text(encoding="utf-8")) or {}

    data = pd.read_csv(rotmod_path)
    data = data[data["galaxy_id"].isin(galaxy_ids)].copy()

    tau_df = reconstruct_selected_subset(rotmod_path, subset_out, recon_cfg)
    tau_df.to_csv(tau_out, index=False)

    halo = fit_halo_and_baryon_models(galaxy_ids, data, models_yaml)
    mond = fit_mond_rar_models(galaxy_ids, data, models_yaml)
    tdf = fit_tdf_knot_models(galaxy_ids, data, tau_df, recon_yaml)
    full = pd.concat([halo, mond, tdf], ignore_index=True)
    full.to_csv(comparison_out, index=False)

    audit_cfg = recon_yaml.get("tdf_robustness_audit", {})
    tdf_models = tuple(audit_cfg.get("holdout_tdf_models", ["tdf_3knot", "tdf_5knot"]))
    holdout = run_holdout_validation(
        data,
        tau_df,
        galaxy_ids,
        recon_yaml,
        models_yaml,
        tdf_models=tdf_models,
    )
    holdout.to_csv(holdout_out, index=False)

    best_summary = build_best_model_summary(full)
    tdf_only = full[full["model_name"].str.startswith("tdf_")]
    knot_stab = knot_count_stability_table(tdf_only)
    robust_best = build_robust_best_model_summary(holdout, best_summary, knot_stab)
    failure_summary = build_expansion20_failure_summary(full, best_summary, holdout, robust_best)
    failure_summary.to_csv(failure_out, index=False)

    claims = build_expansion20_claim_traceability()
    claims.to_csv(claims_out, index=False)

    write_expansion20_benchmark_report(
        report_out,
        galaxy_ids=galaxy_ids,
        failure_summary=failure_summary,
        holdout=holdout,
    )

    return {
        "galaxy_ids": galaxy_ids,
        "tau_profiles": tau_df,
        "model_comparison": full,
        "holdout_validation": holdout,
        "failure_mode_summary": failure_summary,
        "claim_traceability": claims,
    }
