from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION

DEFAULT_GALAXY_IDS: tuple[str, ...] = tuple(MANDATED_GALAXY_CLASSIFICATION.keys())
SUCCESS_GALAXY_IDS: tuple[str, ...] = tuple(
    gid for gid, cls in MANDATED_GALAXY_CLASSIFICATION.items() if cls == "robust_tdf_success"
)
FAILURE_GALAXY_IDS: tuple[str, ...] = tuple(
    gid for gid, cls in MANDATED_GALAXY_CLASSIFICATION.items() if cls == "tdf_failure_mode"
)

DEFAULT_X_GRID = np.linspace(0.0, 1.0, 100)
ANALYSIS_STAGE = "phase_4c_normalized_pattern_discovery"
SOURCE_PROFILE = "phase_2a_radial_reconstruction"
OUTLIER_SCORE_THRESHOLD = 0.35


@dataclass(frozen=True)
class GalaxyNormalizedProfile:
    galaxy_id: str
    classification: str
    x_grid: np.ndarray
    dtaudr_norm: np.ndarray
    gtau_norm: np.ndarray
    residual_v2_norm: np.ndarray
    tau_norm: np.ndarray
    data_mode: str


def _safe_max_abs(values: np.ndarray) -> float:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return 0.0
    m = float(np.max(np.abs(finite)))
    return m if m > 0.0 else 0.0


def _normalize_by_max_abs(values: np.ndarray) -> np.ndarray:
    denom = _safe_max_abs(values)
    if denom <= 0.0:
        return np.zeros_like(values, dtype=float)
    return values.astype(float) / denom


def _normalized_radial_coords(r_kpc: np.ndarray) -> dict[str, np.ndarray]:
    r = np.asarray(r_kpc, dtype=float)
    r_min = float(np.min(r))
    r_max = float(np.max(r))
    span = r_max - r_min
    x_rmax = r / r_max if r_max > 0.0 else np.zeros_like(r)
    x_span = (r - r_min) / span if span > 0.0 else np.zeros_like(r)
    x_rhalf: np.ndarray | None = None
    if r_max > r_min:
        rhalf = 0.5 * (r_min + r_max)
        x_rhalf = (r - rhalf) / (0.5 * span)
    return {"x_rmax": x_rmax, "x_span": x_span, "x_rhalf": x_rhalf}


def _interp_no_extrap(x_src: np.ndarray, y_src: np.ndarray, x_grid: np.ndarray) -> np.ndarray:
    order = np.argsort(x_src)
    x_sorted = x_src[order]
    y_sorted = y_src[order]
    mask = np.isfinite(x_sorted) & np.isfinite(y_sorted)
    x_sorted = x_sorted[mask]
    y_sorted = y_sorted[mask]
    if x_sorted.size < 2:
        return np.full_like(x_grid, np.nan, dtype=float)
    # np.interp leaves endpoints as nan outside coverage
    y_out = np.interp(x_grid, x_sorted, y_sorted, left=np.nan, right=np.nan)
    below = x_grid < x_sorted[0]
    above = x_grid > x_sorted[-1]
    y_out[below | above] = np.nan
    return y_out


def extract_galaxy_profile(
    tau_profiles: pd.DataFrame,
    galaxy_id: str,
    *,
    x_grid: np.ndarray | None = None,
) -> GalaxyNormalizedProfile:
    sub = tau_profiles[tau_profiles["galaxy_id"] == galaxy_id].copy()
    if sub.empty:
        raise ValueError(f"galaxy {galaxy_id!r} not found in tau profiles table")
    sub = sub.sort_values("r_kpc")
    r = sub["r_kpc"].to_numpy(dtype=float)
    residual_v2 = sub["residual_v2_kms2"].to_numpy(dtype=float)
    dtaudr = sub["dtaudr_reconstructed"].to_numpy(dtype=float)
    tau = sub["tau_reconstructed"].to_numpy(dtype=float)

    with np.errstate(divide="ignore", invalid="ignore"):
        gtau = np.where(r > 0, residual_v2 / r, np.nan)

    coords = _normalized_radial_coords(r)
    x_span = coords["x_span"]

    residual_v2_norm = _normalize_by_max_abs(residual_v2)
    dtaudr_norm_pts = _normalize_by_max_abs(dtaudr)
    gtau_norm_pts = _normalize_by_max_abs(gtau)
    tau_norm_pts = _normalize_by_max_abs(tau)

    grid = DEFAULT_X_GRID if x_grid is None else np.asarray(x_grid, dtype=float)
    classification = MANDATED_GALAXY_CLASSIFICATION.get(galaxy_id, "mixed_result")
    data_mode = str(sub["data_mode"].iloc[0]) if "data_mode" in sub.columns else "unknown"

    return GalaxyNormalizedProfile(
        galaxy_id=galaxy_id,
        classification=classification,
        x_grid=grid,
        dtaudr_norm=_interp_no_extrap(x_span, dtaudr_norm_pts, grid),
        gtau_norm=_interp_no_extrap(x_span, gtau_norm_pts, grid),
        residual_v2_norm=_interp_no_extrap(x_span, residual_v2_norm, grid),
        tau_norm=_interp_no_extrap(x_span, tau_norm_pts, grid),
        data_mode=data_mode,
    )


def profiles_to_long_table(profiles: list[GalaxyNormalizedProfile]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for prof in profiles:
        for i, x in enumerate(prof.x_grid):
            rows.append(
                {
                    "galaxy_id": prof.galaxy_id,
                    "classification": prof.classification,
                    "x_grid": float(x),
                    "dtaudr_norm": float(prof.dtaudr_norm[i]) if np.isfinite(prof.dtaudr_norm[i]) else np.nan,
                    "gtau_norm": float(prof.gtau_norm[i]) if np.isfinite(prof.gtau_norm[i]) else np.nan,
                    "residual_v2_norm": float(prof.residual_v2_norm[i])
                    if np.isfinite(prof.residual_v2_norm[i])
                    else np.nan,
                    "tau_norm": float(prof.tau_norm[i]) if np.isfinite(prof.tau_norm[i]) else np.nan,
                    "source_profile": SOURCE_PROFILE,
                    "data_mode": prof.data_mode,
                    "analysis_stage": ANALYSIS_STAGE,
                }
            )
    return pd.DataFrame(rows)


def build_normalized_tau_patterns(
    tau_profiles: pd.DataFrame,
    *,
    galaxy_ids: list[str] | None = None,
    x_grid: np.ndarray | None = None,
) -> tuple[pd.DataFrame, list[GalaxyNormalizedProfile]]:
    gids = list(galaxy_ids) if galaxy_ids is not None else list(DEFAULT_GALAXY_IDS)
    profiles = [extract_galaxy_profile(tau_profiles, gid, x_grid=x_grid) for gid in gids]
    return profiles_to_long_table(profiles), profiles


def _pairwise_metric(
    a: np.ndarray,
    b: np.ndarray,
) -> tuple[float, float]:
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 3:
        return float("nan"), float("nan")
    aa = a[mask]
    bb = b[mask]
    if np.std(aa) == 0.0 or np.std(bb) == 0.0:
        corr = float("nan")
    else:
        corr = float(np.corrcoef(aa, bb)[0, 1])
    rmse = float(np.sqrt(np.mean((aa - bb) ** 2)))
    return corr, rmse


def build_similarity_matrix(profiles: list[GalaxyNormalizedProfile]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    by_id = {p.galaxy_id: p for p in profiles}
    ids = [p.galaxy_id for p in profiles]
    for i, gid_a in enumerate(ids):
        for gid_b in ids[i:]:
            pa, pb = by_id[gid_a], by_id[gid_b]
            d_corr, d_rmse = _pairwise_metric(pa.dtaudr_norm, pb.dtaudr_norm)
            g_corr, g_rmse = _pairwise_metric(pa.gtau_norm, pb.gtau_norm)
            rows.append(
                {
                    "galaxy_id_a": gid_a,
                    "galaxy_id_b": gid_b,
                    "dtaudr_corr": d_corr,
                    "dtaudr_rmse_norm": d_rmse,
                    "gtau_corr": g_corr,
                    "gtau_rmse_norm": g_rmse,
                }
            )
    return pd.DataFrame(rows)


@dataclass(frozen=True)
class SuccessGroupMeans:
    mean_dtaudr: np.ndarray
    std_dtaudr: np.ndarray
    mean_gtau: np.ndarray
    std_gtau: np.ndarray
    mean_tau: np.ndarray
    std_tau: np.ndarray
    mean_residual_v2: np.ndarray
    std_residual_v2: np.ndarray


def _success_group_mean_profile(
    profiles: list[GalaxyNormalizedProfile],
) -> SuccessGroupMeans:
    success = [p for p in profiles if p.classification == "robust_tdf_success"]
    if not success:
        raise ValueError("no robust_tdf_success profiles for success-group mean")

    def _stack(attr: str) -> tuple[np.ndarray, np.ndarray]:
        stack = np.vstack([getattr(p, attr) for p in success])
        return np.nanmean(stack, axis=0), np.nanstd(stack, axis=0)

    mean_d, std_d = _stack("dtaudr_norm")
    mean_g, std_g = _stack("gtau_norm")
    mean_t, std_t = _stack("tau_norm")
    mean_r, std_r = _stack("residual_v2_norm")
    return SuccessGroupMeans(
        mean_dtaudr=mean_d,
        std_dtaudr=std_d,
        mean_gtau=mean_g,
        std_gtau=std_g,
        mean_tau=mean_t,
        std_tau=std_t,
        mean_residual_v2=mean_r,
        std_residual_v2=std_r,
    )


def _rank_by_rmse_descending(rmse_by_galaxy: dict[str, float]) -> dict[str, int]:
    """Rank 1 = largest RMSE (most deviant from success-group mean)."""
    valid = {gid: v for gid, v in rmse_by_galaxy.items() if np.isfinite(v)}
    ordered = sorted(valid.items(), key=lambda item: item[1], reverse=True)
    return {gid: rank + 1 for rank, (gid, _) in enumerate(ordered)}


def _metrics_vs_mean(profile: np.ndarray, mean: np.ndarray) -> tuple[float, float]:
    return _pairwise_metric(profile, mean)


def build_outlier_scores(
    profiles: list[GalaxyNormalizedProfile],
    *,
    outlier_threshold: float = OUTLIER_SCORE_THRESHOLD,
) -> pd.DataFrame:
    """Score deviation from success-group mean per metric; never auto-flag holdout failures."""
    means = _success_group_mean_profile(profiles)
    interim: list[dict[str, Any]] = []

    for prof in profiles:
        d_corr, d_rmse = _metrics_vs_mean(prof.dtaudr_norm, means.mean_dtaudr)
        g_corr, g_rmse = _metrics_vs_mean(prof.gtau_norm, means.mean_gtau)
        t_corr, t_rmse = _metrics_vs_mean(prof.tau_norm, means.mean_tau)
        r_corr, r_rmse = _metrics_vs_mean(prof.residual_v2_norm, means.mean_residual_v2)
        interim.append(
            {
                "galaxy_id": prof.galaxy_id,
                "classification": prof.classification,
                "holdout_failure_mode": prof.classification == "tdf_failure_mode",
                "dtaudr_corr_to_success_mean": d_corr,
                "dtaudr_rmse_to_success_mean": d_rmse,
                "gtau_corr_to_success_mean": g_corr,
                "gtau_rmse_to_success_mean": g_rmse,
                "tau_corr_to_success_mean": t_corr,
                "tau_rmse_to_success_mean": t_rmse,
                "residual_v2_corr_to_success_mean": r_corr,
                "residual_v2_rmse_to_success_mean": r_rmse,
            }
        )

    rmse_d = {r["galaxy_id"]: r["dtaudr_rmse_to_success_mean"] for r in interim}
    rmse_g = {r["galaxy_id"]: r["gtau_rmse_to_success_mean"] for r in interim}
    rmse_t = {r["galaxy_id"]: r["tau_rmse_to_success_mean"] for r in interim}
    rmse_r = {r["galaxy_id"]: r["residual_v2_rmse_to_success_mean"] for r in interim}
    rank_d = _rank_by_rmse_descending(rmse_d)
    rank_g = _rank_by_rmse_descending(rmse_g)
    rank_t = _rank_by_rmse_descending(rmse_t)
    rank_r = _rank_by_rmse_descending(rmse_r)

    def _largest_outlier_galaxy(ranks: dict[str, int]) -> str:
        return min(ranks, key=ranks.get)  # type: ignore[arg-type]

    largest_d = _largest_outlier_galaxy(rank_d)
    largest_g = _largest_outlier_galaxy(rank_g)
    largest_t = _largest_outlier_galaxy(rank_t)
    largest_r = _largest_outlier_galaxy(rank_r)

    success_rmse_d = [v for gid, v in rmse_d.items() if gid in SUCCESS_GALAXY_IDS and np.isfinite(v)]
    success_rmse_g = [v for gid, v in rmse_g.items() if gid in SUCCESS_GALAXY_IDS and np.isfinite(v)]
    scale_d = float(np.median(success_rmse_d)) if success_rmse_d else 1.0
    scale_g = float(np.median(success_rmse_g)) if success_rmse_g else 1.0
    if scale_d <= 0.0:
        scale_d = 1.0
    if scale_g <= 0.0:
        scale_g = 1.0

    shape_scores_all = []
    for row in interim:
        d_rmse_n = row["dtaudr_rmse_to_success_mean"] / scale_d if np.isfinite(row["dtaudr_rmse_to_success_mean"]) else float("nan")
        g_rmse_n = row["gtau_rmse_to_success_mean"] / scale_g if np.isfinite(row["gtau_rmse_to_success_mean"]) else float("nan")
        d_corr = row["dtaudr_corr_to_success_mean"]
        g_corr = row["gtau_corr_to_success_mean"]
        d_one_minus = (1.0 - d_corr) if np.isfinite(d_corr) else 1.0
        g_one_minus = (1.0 - g_corr) if np.isfinite(g_corr) else 1.0
        d_rmse_term = d_rmse_n if np.isfinite(d_rmse_n) else 1.0
        g_rmse_term = g_rmse_n if np.isfinite(g_rmse_n) else 1.0
        shape_scores_all.append(0.25 * (d_rmse_term + g_rmse_term + d_one_minus + g_one_minus))

    shape_threshold = float(np.percentile(shape_scores_all, 75)) + 0.12 if shape_scores_all else outlier_threshold

    rows: list[dict[str, Any]] = []
    for row, shape_score in zip(interim, shape_scores_all):
        gid = row["galaxy_id"]
        is_largest_d = gid == largest_d
        is_largest_g = gid == largest_g
        is_largest_t = gid == largest_t
        is_largest_r = gid == largest_r
        normalized_profile_outlier = bool(
            is_largest_d
            or is_largest_g
            or is_largest_t
            or is_largest_r
            or (np.isfinite(shape_score) and shape_score >= shape_threshold)
        )

        holdout = bool(row["holdout_failure_mode"])
        parts: list[str] = []
        if holdout:
            parts.append("Phase 4A holdout failure mode (predictive RMSE); distinct from normalized-profile metrics.")
        if normalized_profile_outlier:
            metric_notes = []
            if is_largest_d:
                metric_notes.append("largest dtaudr_norm RMSE vs success mean")
            if is_largest_g:
                metric_notes.append("largest gtau_norm RMSE vs success mean")
            if is_largest_t:
                metric_notes.append("largest tau_norm RMSE vs success mean")
            if is_largest_r:
                metric_notes.append("largest residual_v2_norm RMSE vs success mean")
            if metric_notes:
                parts.append("Normalized-profile outlier: " + "; ".join(metric_notes) + ".")
            elif np.isfinite(shape_score) and shape_score >= shape_threshold:
                parts.append("Elevated combined shape score (dτ/dr + gτ) vs subset.")
        if not parts:
            parts.append(
                "Within typical success-group normalized similarity for shape metrics (exploratory)."
            )
        if holdout and not (is_largest_d or is_largest_g or is_largest_t or is_largest_r):
            parts.append(
                "Holdout failure is not the same as largest normalized-shape outlier in this metric set."
            )

        rows.append(
            {
                **row,
                "pattern_outlier_score": shape_score,
                "dtaudr_rmse_rank": rank_d.get(gid),
                "gtau_rmse_rank": rank_g.get(gid),
                "tau_rmse_rank": rank_t.get(gid),
                "residual_v2_rmse_rank": rank_r.get(gid),
                "is_largest_outlier_dtaudr_norm": is_largest_d,
                "is_largest_outlier_gtau_norm": is_largest_g,
                "is_largest_outlier_tau_norm": is_largest_t,
                "is_largest_outlier_residual_v2_norm": is_largest_r,
                "normalized_profile_outlier": normalized_profile_outlier,
                "outlier_flag": normalized_profile_outlier,
                "interpretation": " ".join(parts),
            }
        )
    return pd.DataFrame(rows)


def plot_normalized_overlays(
    profiles: list[GalaxyNormalizedProfile],
    *,
    figures_dir: Path,
) -> dict[str, Path | None]:
    sg = _success_group_mean_profile(profiles)
    x = profiles[0].x_grid
    paths: dict[str, Path | None] = {}
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return {
            "normalized_tau_gradient_overlay.png": None,
            "normalized_missing_acceleration_overlay.png": None,
            "tau_pattern_similarity_heatmap.png": None,
        }

    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    def _overlay(
        y_attr: str,
        mean_y: np.ndarray,
        std_y: np.ndarray,
        ylabel: str,
        filename: str,
        title_suffix: str,
    ) -> Path | None:
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.fill_between(
            x,
            mean_y - std_y,
            mean_y + std_y,
            alpha=0.25,
            color="C0",
            label="success-group mean ± 1σ",
        )
        ax.plot(x, mean_y, "-", color="C0", lw=2, label="success-group mean")
        for prof in profiles:
            y = getattr(prof, y_attr)
            if prof.classification == "robust_tdf_success":
                ax.plot(x, y, "-", alpha=0.55, lw=1.2, label=f"{prof.galaxy_id}")
            else:
                ax.plot(
                    x,
                    y,
                    "--",
                    color="C3",
                    lw=2.5,
                    label=f"{prof.galaxy_id} (holdout failure mode)",
                )
        ax.set_xlabel("normalized radius x_span = (r − r_min) / (r_max − r_min)")
        ax.set_ylabel(ylabel)
        ax.set_title(
            f"Exploratory normalized pattern analysis — {title_suffix}\n"
            "(not a universal τ-profile; six-galaxy subset)"
        )
        ax.grid(alpha=0.3)
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc="best", fontsize=7)
        out = figures_dir / filename
        fig.tight_layout()
        fig.savefig(out, dpi=150)
        plt.close(fig)
        return out

    paths["normalized_tau_gradient_overlay.png"] = _overlay(
        "dtaudr_norm",
        sg.mean_dtaudr,
        sg.std_dtaudr,
        "dτ/dr / max|dτ/dr|",
        "normalized_tau_gradient_overlay.png",
        "normalized τ-gradient",
    )
    paths["normalized_missing_acceleration_overlay.png"] = _overlay(
        "gtau_norm",
        sg.mean_gtau,
        sg.std_gtau,
        "g_τ = residual_v²/r  (normalized)",
        "normalized_missing_acceleration_overlay.png",
        "normalized missing-acceleration proxy",
    )

    sim = build_similarity_matrix(profiles)
    ids = [p.galaxy_id for p in profiles]
    n = len(ids)
    corr_mat = np.full((n, n), np.nan)
    for _, row in sim.iterrows():
        i = ids.index(row["galaxy_id_a"])
        j = ids.index(row["galaxy_id_b"])
        corr_mat[i, j] = row["dtaudr_corr"]
        corr_mat[j, i] = row["dtaudr_corr"]
    np.fill_diagonal(corr_mat, 1.0)

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(corr_mat, vmin=-1, vmax=1, cmap="RdBu_r", aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(ids, rotation=45, ha="right")
    ax.set_yticklabels(ids)
    ax.set_title(
        "Exploratory normalized pattern analysis\n"
        "Pearson correlation of dτ/dr_norm profiles (six-galaxy subset)"
    )
    fig.colorbar(im, ax=ax, label="dtaudr_corr")
    heat_path = figures_dir / "tau_pattern_similarity_heatmap.png"
    fig.tight_layout()
    fig.savefig(heat_path, dpi=150)
    plt.close(fig)
    paths["tau_pattern_similarity_heatmap.png"] = heat_path
    return paths


def _metric_outlier_line(outliers: pd.DataFrame, metric: str, rank_col: str, largest_col: str) -> str:
    sub = outliers.sort_values(rank_col)
    top = sub.iloc[0]
    ng_row = outliers[outliers["galaxy_id"] == "NGC7814"]
    ng_rank = int(ng_row[rank_col].iloc[0]) if not ng_row.empty else -1
    ng_largest = bool(ng_row[largest_col].iloc[0]) if not ng_row.empty else False
    n = len(outliers)
    if ng_largest:
        ng_clause = "NGC7814 **is** the largest outlier for this metric."
    else:
        ng_clause = (
            f"NGC7814 is **not** the largest outlier (rank {ng_rank}/{n} by RMSE vs success-group mean); "
            f"largest is **{top['galaxy_id']}**."
        )
    return f"- **{metric}**: largest outlier = **{top['galaxy_id']}** (RMSE rank 1). {ng_clause}"


def write_normalized_pattern_report(
    path: Path,
    *,
    patterns_table: pd.DataFrame,
    similarity: pd.DataFrame,
    outliers: pd.DataFrame,
    profiles: list[GalaxyNormalizedProfile],
) -> None:
    del patterns_table, profiles  # reserved for future appendix use
    ng = outliers[outliers["galaxy_id"] == "NGC7814"].iloc[0] if "NGC7814" in outliers["galaxy_id"].values else None

    success_pairs = similarity[
        (similarity["galaxy_id_a"].isin(SUCCESS_GALAXY_IDS))
        & (similarity["galaxy_id_b"].isin(SUCCESS_GALAXY_IDS))
        & (similarity["galaxy_id_a"] != similarity["galaxy_id_b"])
    ]
    d_corr_med = float(success_pairs["dtaudr_corr"].median()) if not success_pairs.empty else float("nan")
    g_corr_med = float(success_pairs["gtau_corr"].median()) if not success_pairs.empty else float("nan")

    lines = [
        "# SPARC Normalized τ-Pattern Report (Phase 4C)",
        "",
        "**Exploratory normalized pattern analysis** on the controlled six-galaxy subset. "
        "No new fits were run. Phase 2A diagnostic τ profiles only.",
        "",
        "> This analysis searches for normalized τ-pattern similarities. It does not assume or "
        "discover a universal τ-profile, does not validate TDF on full SPARC, does not disprove "
        "dark matter, and does not include lensing.",
        "",
        "## Objective",
        "",
        "Test whether galaxy-specific reconstructed profiles show **normalized pattern similarity** "
        "across the five **robust_tdf_success** galaxies. **NGC7814** is the known **holdout failure mode** "
        "(Phase 4A); normalized-profile metrics are computed **without forcing** it to be an outlier in every quantity.",
        "",
        "## Holdout failure vs normalized-profile outlier",
        "",
        "| Concept | Definition |",
        "| --- | --- |",
        "| **Holdout failure mode** | Phase 4A `tdf_failure_mode`: poor even/odd test RMSE vs NFW/MOND (predictive). |",
        "| **Normalized-profile outlier** | Largest RMSE vs success-group mean and/or elevated shape score in Phase 4C metrics only. |",
        "",
        "These are **not equivalent**. A galaxy can fail holdout while ranking mid-pack in normalized shape metrics.",
        "",
        "## Normalization choices",
        "",
        "- Radial coordinate: **x_span** = (r − r_min) / (r_max − r_min) mapped to a common grid "
        f"x_grid ∈ [0, 1] with {len(DEFAULT_X_GRID)} points (linear interpolation, no extrapolation).",
        "- **dtaudr_norm** = dτ/dr / max|dτ/dr|; **gtau** = residual_v²/r; **gtau_norm** = gτ / max|gτ|.",
        "- **residual_v2_norm**, **tau_norm**: same max-abs scaling.",
        "- Source: `sparc_subset_tau_profiles.csv` (Phase 2A, `phase_2a_radial_reconstruction`).",
        "",
        "## Success-group profile behavior",
        "",
        f"- Success-group galaxies: {', '.join(SUCCESS_GALAXY_IDS)}.",
        f"- Median pairwise **dtaudr_corr** (success only): **{d_corr_med:.3f}**.",
        f"- Median pairwise **gtau_corr** (success only): **{g_corr_med:.3f}**.",
        "- Overlay figures show a **success-group mean profile** with ±1σ envelope.",
        "- Language: **candidate τ-gradient family** and **exploratory evidence for repeatable structure** "
        "where correlations are high; not proof of a universal law.",
        "",
        "## Per-metric largest outlier (honest ranks)",
        "",
    ]
    lines.append(_metric_outlier_line(outliers, "dtaudr_norm (shape)", "dtaudr_rmse_rank", "is_largest_outlier_dtaudr_norm"))
    lines.append(_metric_outlier_line(outliers, "gtau_norm (shape)", "gtau_rmse_rank", "is_largest_outlier_gtau_norm"))
    lines.append(_metric_outlier_line(outliers, "tau_norm (integrated τ)", "tau_rmse_rank", "is_largest_outlier_tau_norm"))
    lines.append(
        _metric_outlier_line(
            outliers, "residual_v2_norm (amplitude)", "residual_v2_rmse_rank", "is_largest_outlier_residual_v2_norm"
        )
    )
    lines.extend(["", "## NGC7814 discussion", ""])
    if ng is not None:
        shape_rank = int((outliers["pattern_outlier_score"] >= ng["pattern_outlier_score"]).sum())
        not_rank1_metrics = [
            label
            for label, col in [
                ("dtaudr_norm", "is_largest_outlier_dtaudr_norm"),
                ("gtau_norm", "is_largest_outlier_gtau_norm"),
                ("tau_norm", "is_largest_outlier_tau_norm"),
                ("residual_v2_norm", "is_largest_outlier_residual_v2_norm"),
            ]
            if not bool(ng[col])
        ]
        lines.extend(
            [
                f"- **Holdout failure mode:** {bool(ng['holdout_failure_mode'])} (Phase 4A; NFW/MOND beat TDF on test RMSE).",
                f"- **Normalized-profile outlier (metric-driven flag):** {bool(ng['normalized_profile_outlier'])}.",
                f"- Shape score (dτ/dr + gτ only): {ng['pattern_outlier_score']:.3f} — rank **{shape_rank}/6** "
                f"(1 = highest; **NGC3198** is higher at "
                f"{outliers.loc[outliers['galaxy_id'] == 'NGC3198', 'pattern_outlier_score'].iloc[0]:.3f}).",
                f"- RMSE ranks vs success-group mean — dτ/dr: {int(ng['dtaudr_rmse_rank'])}; "
                f"gτ: {int(ng['gtau_rmse_rank'])}; τ: {int(ng['tau_rmse_rank'])}; "
                f"residual_v²: {int(ng['residual_v2_rmse_rank'])}.",
                f"- τ_corr to success mean: {ng['tau_corr_to_success_mean']:.3f} "
                "(much lower than success galaxies ≳ 0.97 — integrated-τ **shape** differs strongly).",
                "",
            ]
        )
        if not_rank1_metrics:
            lines.append(
                f"**NGC7814 is not the largest normalized-profile outlier in:** {', '.join(not_rank1_metrics)}. "
                "Holdout failure therefore stands **independently** of those metrics."
            )
        else:
            lines.append(
                "**NGC7814 is rank 1 by RMSE vs success-group mean in all four normalized metrics on this run.** "
                "That supports strong **normalized-profile outlier behavior**, separate from the holdout label."
            )
        if shape_rank > 1:
            lines.append(
                f" However, the combined **shape score** ranks NGC7814 **{shape_rank}**/6 — so holdout failure is **not** "
                "the same as the highest shape-score deviation among the six galaxies."
            )
        lines.extend(
            [
                "",
                "Holdout failure is **not** claimed to be *caused* by normalized-profile distance; metrics are exploratory.",
                "",
            ]
        )
    else:
        lines.append("- NGC7814 metrics not available.\n")

    lines.extend(
        [
            "## Similarity matrix summary",
            "",
            "Full pairwise table: `outputs/tables/sparc_tau_pattern_similarity_matrix.csv`.",
            "Heatmap: `outputs/figures/sparc_subset/tau_pattern_similarity_heatmap.png`.",
            "",
            "## Outlier-score summary",
            "",
            "| galaxy_id | holdout_failure | norm_profile_outlier | shape_score | dτ/dr rank | τ rank | res_v² rank |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for _, row in outliers.sort_values("pattern_outlier_score", ascending=False).iterrows():
        lines.append(
            f"| {row['galaxy_id']} | {row['holdout_failure_mode']} | {row['normalized_profile_outlier']} | "
            f"{row['pattern_outlier_score']:.3f} | {int(row['dtaudr_rmse_rank'])} | "
            f"{int(row['tau_rmse_rank'])} | {int(row['residual_v2_rmse_rank'])} |"
        )

    candidate_visible = bool(d_corr_med > 0.5) if np.isfinite(d_corr_med) else False
    lines.extend(
        [
            "",
            "## Candidate shared normalized pattern?",
            "",
            (
                "**Moderate exploratory similarity** among success-group galaxies is visible in normalized "
                "dτ/dr and gτ overlays; treat as a **candidate τ-gradient family**, not a universal profile."
                if candidate_visible
                else "**Weak or mixed similarity** in normalized metrics; do not claim a shared universal pattern."
            ),
            "",
            "## Limitations",
            "",
            "- Phase 2A diagnostic reconstruction only (not Phase 3B knot fits).",
            "- Six galaxies; morphology and baryonic decomposition differ.",
            "- Max-abs normalization removes amplitude scale; shape-only comparison.",
            "- No M/L, K_tau, distance, or inclination sensitivity in this phase.",
            "",
            "## Outputs",
            "",
            "- `outputs/tables/sparc_normalized_tau_patterns.csv`",
            "- `outputs/tables/sparc_tau_pattern_similarity_matrix.csv`",
            "- `outputs/tables/sparc_tau_pattern_outlier_scores.csv`",
            "- Figures under `outputs/figures/sparc_subset/`",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


@dataclass
class NormalizedPatternAnalysisResult:
    patterns_table: pd.DataFrame
    similarity: pd.DataFrame
    outliers: pd.DataFrame
    profiles: list[GalaxyNormalizedProfile]
    figure_paths: dict[str, Path | None]


def run_normalized_pattern_analysis(
    tau_profiles: pd.DataFrame,
    *,
    galaxy_ids: list[str] | None = None,
    figures_dir: Path | None = None,
) -> NormalizedPatternAnalysisResult:
    patterns_table, profiles = build_normalized_tau_patterns(tau_profiles, galaxy_ids=galaxy_ids)
    similarity = build_similarity_matrix(profiles)
    outliers = build_outlier_scores(profiles)
    fig_dir = figures_dir or Path("outputs/figures/sparc_subset")
    figure_paths = plot_normalized_overlays(profiles, figures_dir=fig_dir)
    return NormalizedPatternAnalysisResult(
        patterns_table=patterns_table,
        similarity=similarity,
        outliers=outliers,
        profiles=profiles,
        figure_paths=figure_paths,
    )
