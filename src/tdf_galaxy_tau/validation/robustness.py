from __future__ import annotations

import numpy as np
import pandas as pd

from tdf_galaxy_tau.metrics.comparison import rmse
from tdf_galaxy_tau.metrics.information_criteria import model_parameter_count
from tdf_galaxy_tau.models.tdf_knot import n_knots_for_model


def knot_count_stability_table(tdf_comparison: pd.DataFrame) -> pd.DataFrame:
    """Per-galaxy delta AIC/BIC between 3-knot and 5-knot models."""
    rows: list[dict[str, object]] = []
    for gid, g in tdf_comparison.groupby("galaxy_id"):
        m3 = g[g["model_name"] == "tdf_3knot"]
        m4 = g[g["model_name"] == "tdf_4knot"]
        m5 = g[g["model_name"] == "tdf_5knot"]
        if m3.empty or m5.empty:
            continue
        r3 = m3.iloc[0]
        r5 = m5.iloc[0]
        delta_aic = float(r5["aic"]) - float(r3["aic"])
        delta_bic = float(r5["bic"]) - float(r3["bic"])
        delta_rmse = float(r5["rmse_kms"]) - float(r3["rmse_kms"])
        large_aic_gain = delta_aic < -10.0
        rows.append(
            {
                "galaxy_id": gid,
                "aic_tdf_3knot": float(r3["aic"]),
                "aic_tdf_5knot": float(r5["aic"]),
                "delta_aic_5_minus_3": delta_aic,
                "bic_tdf_3knot": float(r3["bic"]),
                "bic_tdf_5knot": float(r5["bic"]),
                "delta_bic_5_minus_3": delta_bic,
                "rmse_tdf_3knot": float(r3["rmse_kms"]),
                "rmse_tdf_5knot": float(r5["rmse_kms"]),
                "delta_rmse_5_minus_3": delta_rmse,
                "five_knot_large_aic_improvement": large_aic_gain,
                "tdf_4knot_fit_success": bool(m4.iloc[0]["fit_success"]) if not m4.empty else False,
                "tdf_4knot_rmse": float(m4.iloc[0]["rmse_kms"]) if not m4.empty else np.nan,
                "tdf_4knot_fit_status": str(m4.iloc[0]["fit_status"]) if not m4.empty else "",
                "tdf_4knot_reduced_chi_square": float(m4.iloc[0]["reduced_chi_square"]) if not m4.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def negative_v2_audit_table(
    tdf_comparison: pd.DataFrame,
    tdf_params: pd.DataFrame | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in tdf_comparison.iterrows():
        status = str(row.get("fit_status", ""))
        has_neg = "negative_v2" in status
        rows.append(
            {
                "galaxy_id": row["galaxy_id"],
                "model_name": row["model_name"],
                "fit_success": bool(row["fit_success"]),
                "fit_status": status,
                "negative_v2_flag": has_neg,
            }
        )
    return pd.DataFrame(rows)


def build_robust_best_model_summary(
    holdout_df: pd.DataFrame,
    full_best: pd.DataFrame,
    knot_stability: pd.DataFrame,
) -> pd.DataFrame:
    """Combine full-sample and holdout evidence for cautious best-model labels."""
    rows: list[dict[str, object]] = []
    for gid in full_best["galaxy_id"].unique():
        fb = full_best[full_best["galaxy_id"] == gid].iloc[0]
        ks = knot_stability[knot_stability["galaxy_id"] == gid]
        ho = holdout_df[
            (holdout_df["galaxy_id"] == gid)
            & (holdout_df["split_name"] == "even_odd_index")
        ]
        ho3 = ho[ho["model_name"] == "tdf_3knot"]
        ho5 = ho[ho["model_name"] == "tdf_5knot"]
        honfw = ho[ho["model_name"] == "nfw_refit"]
        homond = ho[ho["model_name"] == "mond_fit_a0_simple"]

        tdf3_beats_nfw_ho = False
        if not ho3.empty and not honfw.empty:
            tdf3_beats_nfw_ho = float(ho3.iloc[0]["test_rmse_kms"]) < float(honfw.iloc[0]["test_rmse_kms"])

        five_knot_overfit_risk = False
        if not ks.empty:
            five_knot_overfit_risk = bool(ks.iloc[0]["five_knot_large_aic_improvement"]) and (
                not ho5.empty
                and not ho3.empty
                and float(ho5.iloc[0]["test_rmse_kms"]) >= float(ho3.iloc[0]["test_rmse_kms"])
            )

        rows.append(
            {
                "galaxy_id": gid,
                "full_sample_best_by_aic": fb["best_by_aic"],
                "full_sample_best_tdf_variant": fb.get("best_tdf_variant", ""),
                "tdf_3knot_holdout_test_rmse": float(ho3.iloc[0]["test_rmse_kms"]) if not ho3.empty else np.nan,
                "tdf_5knot_holdout_test_rmse": float(ho5.iloc[0]["test_rmse_kms"]) if not ho5.empty else np.nan,
                "nfw_refit_holdout_test_rmse": float(honfw.iloc[0]["test_rmse_kms"]) if not honfw.empty else np.nan,
                "mond_fit_holdout_test_rmse": float(homond.iloc[0]["test_rmse_kms"]) if not homond.empty else np.nan,
                "tdf_3knot_beats_nfw_holdout_rmse": tdf3_beats_nfw_ho,
                "five_knot_overfit_risk_flag": five_knot_overfit_risk,
                "recommended_reporting_model": "tdf_3knot"
                if five_knot_overfit_risk
                else str(fb.get("best_tdf_variant", "tdf_3knot")),
                "caution_flag": str(fb.get("caution_flag", "")) + ";phase_3c_holdout_audit",
            }
        )
    return pd.DataFrame(rows)
