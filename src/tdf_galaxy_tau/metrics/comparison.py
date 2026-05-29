from __future__ import annotations

import numpy as np
import pandas as pd


def rmse(v_obs: np.ndarray, v_model: np.ndarray) -> float:
    obs = np.asarray(v_obs, dtype=float)
    model = np.asarray(v_model, dtype=float)
    return float(np.sqrt(np.mean((obs - model) ** 2)))


def chi_square(v_obs: np.ndarray, v_model: np.ndarray, v_err: np.ndarray) -> float:
    obs = np.asarray(v_obs, dtype=float)
    model = np.asarray(v_model, dtype=float)
    err = np.asarray(v_err, dtype=float)
    if np.any(err <= 0):
        raise ValueError("v_err must be positive")
    return float(np.sum(((obs - model) / err) ** 2))


def reduced_chi_square(chi2: float, n_points: int, n_parameters: int) -> float:
    dof = n_points - n_parameters - 1
    if dof <= 0:
        raise ValueError("non-positive degrees of freedom")
    return float(chi2 / dof)


def safe_reduced_chi_square(chi2: float, n_points: int, n_parameters: int) -> float:
    """Reduced chi-square with guarded dof floor for reporting."""
    dof = max(n_points - n_parameters - 1, 1)
    return float(chi2 / dof)


def poor_rmse_relative_to_median_velocity(
    rmse_kms: float,
    median_v_obs_kms: float,
    *,
    fraction_threshold: float = 0.20,
) -> bool:
    """True when RMSE exceeds a fraction of the galaxy median observed speed."""
    if median_v_obs_kms <= 0:
        return False
    return float(rmse_kms) > fraction_threshold * float(median_v_obs_kms)


def rank_models_within_galaxy(comparison_df: pd.DataFrame, metric: str = "aic") -> pd.DataFrame:
    """Add rank column (1 = best) for each galaxy_id by ascending metric."""
    df = comparison_df.copy()
    df[f"{metric}_rank"] = df.groupby("galaxy_id")[metric].rank(method="min", ascending=True)
    return df


def build_best_baseline_with_mond_summary(comparison_df: pd.DataFrame) -> pd.DataFrame:
    """Per-galaxy best baseline by RMSE/AIC/BIC and MOND/NFW ranks."""
    df = comparison_df.copy()
    rows: list[dict[str, object]] = []
    for gid, g in df.groupby("galaxy_id"):
        g = g.sort_values("aic")
        best_rmse = g.loc[g["rmse_kms"].idxmin(), "model_name"]
        best_aic = g.loc[g["aic"].idxmin(), "model_name"]
        best_bic = g.loc[g["bic"].idxmin(), "model_name"]

        aic_ranks = g["aic"].rank(method="min", ascending=True)

        def _rank(model: str) -> int | None:
            sub = g[g["model_name"] == model]
            if sub.empty:
                return None
            return int(aic_ranks.loc[sub.index[0]])

        high_chi = bool((g["reduced_chi_square"] > 5.0).all())
        caution_parts = ["fixed_baryonic_decomposition_no_ML"]
        if high_chi:
            caution_parts.append("all_models_high_reduced_chi_square")

        rows.append(
            {
                "galaxy_id": gid,
                "best_baseline_by_rmse": best_rmse,
                "best_baseline_by_aic": best_aic,
                "best_baseline_by_bic": best_bic,
                "mond_fixed_rank_by_aic": _rank("mond_fixed_a0_simple"),
                "mond_fit_a0_rank_by_aic": _rank("mond_fit_a0_simple"),
                "nfw_refit_rank_by_aic": _rank("nfw_refit"),
                "caution_flag": ";".join(caution_parts),
            }
        )
    return pd.DataFrame(rows)


_BASELINE_MODELS = {
    "baryonic_only",
    "nfw_refit",
    "burkert_refit",
    "mond_fixed_a0_simple",
    "mond_fit_a0_simple",
    "rar_fixed",
}


def build_best_model_summary(comparison_df: pd.DataFrame) -> pd.DataFrame:
    """Per-galaxy best overall and TDF vs baseline flags for Phase 3B."""
    rows: list[dict[str, object]] = []
    for gid, g in comparison_df.groupby("galaxy_id"):
        g = g.copy()
        aic_ranks = g["aic"].rank(method="min", ascending=True)
        bic_ranks = g["bic"].rank(method="min", ascending=True)

        def _rank(model: str, ranks: pd.Series) -> int | None:
            sub = g[g["model_name"] == model]
            if sub.empty:
                return None
            return int(ranks.loc[sub.index[0]])

        best_rmse = g.loc[g["rmse_kms"].idxmin(), "model_name"]
        best_aic = g.loc[g["aic"].idxmin(), "model_name"]
        best_bic = g.loc[g["bic"].idxmin(), "model_name"]

        baselines = g[g["model_name"].isin(_BASELINE_MODELS)]
        best_baseline_aic = (
            baselines.loc[baselines["aic"].idxmin(), "model_name"] if not baselines.empty else None
        )

        tdf = g[g["model_name"].str.startswith("tdf_")]
        best_tdf = tdf.loc[tdf["aic"].idxmin(), "model_name"] if not tdf.empty else None

        tdf3_aic_rank = _rank("tdf_3knot", aic_ranks)
        nfw_aic_rank = _rank("nfw_refit", aic_ranks)
        mond_aic_rank = _rank("mond_fit_a0_simple", aic_ranks)

        def _beats(model_a: str, model_b: str, ranks: pd.Series) -> bool:
            ra, rb = _rank(model_a, ranks), _rank(model_b, ranks)
            if ra is None or rb is None:
                return False
            return ra < rb

        caution = ["fixed_baryonic_decomposition_no_ML", "fixed_K_tau", "six_galaxy_subset_only"]
        if bool((g["reduced_chi_square"] > 5.0).all()):
            caution.append("all_models_high_reduced_chi_square")

        rows.append(
            {
                "galaxy_id": gid,
                "best_by_rmse": best_rmse,
                "best_by_aic": best_aic,
                "best_by_bic": best_bic,
                "best_baseline_by_aic": best_baseline_aic,
                "best_tdf_variant": best_tdf,
                "tdf_3knot_rank_by_aic": tdf3_aic_rank,
                "tdf_3knot_rank_by_bic": _rank("tdf_3knot", bic_ranks),
                "tdf_3knot_beats_nfw_refit_by_aic": _beats("tdf_3knot", "nfw_refit", aic_ranks),
                "tdf_3knot_beats_nfw_refit_by_bic": _beats("tdf_3knot", "nfw_refit", bic_ranks),
                "tdf_3knot_beats_mond_fit_a0_by_aic": _beats("tdf_3knot", "mond_fit_a0_simple", aic_ranks),
                "tdf_3knot_beats_mond_fit_a0_by_bic": _beats("tdf_3knot", "mond_fit_a0_simple", bic_ranks),
                "caution_flag": ";".join(caution),
            }
        )
    return pd.DataFrame(rows)
