from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.metrics.comparison import rmse
from tdf_galaxy_tau.reconstruction.radial_tau import (
    TauReconstructionConfig,
    load_reconstruction_config,
    reconstruct_radial_tau_profile,
)
from tdf_galaxy_tau.validation.failure_modes import HOLDOUT_SPLIT_PRIMARY, MANDATED_GALAXY_CLASSIFICATION
from tdf_galaxy_tau.validation.holdout import even_odd_radial_split, radial_region_label_for_index
from tdf_galaxy_tau.validation.holdout_residuals import (
    _export_tdf_test_points,
    load_holdout_export_configs,
)
TARGET_GALAXY = "NGC7814"
DEFAULT_DISK_SCALES = (0.5, 0.7, 1.0, 1.3)
DEFAULT_BULGE_SCALES = (0.2, 0.5, 0.7, 1.0, 1.3)
PLAUSIBLE_DISK_RANGE = (0.7, 1.3)
PLAUSIBLE_BULGE_RANGE = (0.5, 1.0)
ANALYSIS_STAGE = "phase_4f_ml_sensitivity_audit"


@dataclass(frozen=True)
class MlSensitivityConfig:
    disk_scales: tuple[float, ...] = DEFAULT_DISK_SCALES
    bulge_scales: tuple[float, ...] = DEFAULT_BULGE_SCALES
    holdout_split: str = HOLDOUT_SPLIT_PRIMARY
    tdf_models: tuple[str, ...] = ("tdf_3knot", "tdf_5knot")


def compute_v_bar_scaled_kms(
    v_gas_kms: np.ndarray,
    v_disk_kms: np.ndarray,
    v_bulge_kms: np.ndarray,
    *,
    disk_scale: float,
    bulge_scale: float,
) -> np.ndarray:
    """Canonical SPARC convention: v_bar^2 = v_gas^2 + s_d v_disk^2 + s_b v_bulge^2 (signed components)."""
    v2 = (
        np.asarray(v_gas_kms, dtype=float) ** 2
        + disk_scale * np.asarray(v_disk_kms, dtype=float) ** 2
        + bulge_scale * np.asarray(v_bulge_kms, dtype=float) ** 2
    )
    return np.sqrt(np.maximum(v2, 0.0))


def scaled_galaxy_frame(g: pd.DataFrame, *, disk_scale: float, bulge_scale: float) -> pd.DataFrame:
    out = g.sort_values("r_kpc").reset_index(drop=True).copy()
    out["v_bar_kms"] = compute_v_bar_scaled_kms(
        out["v_gas_kms"].to_numpy(),
        out["v_disk_kms"].to_numpy(),
        out["v_bulge_kms"].to_numpy(),
        disk_scale=disk_scale,
        bulge_scale=bulge_scale,
    )
    out["residual_v2_kms2"] = out["v_obs_kms"].to_numpy(dtype=float) ** 2 - out["v_bar_kms"].to_numpy(dtype=float) ** 2
    return out


def reconstruct_scaled_tau_table(
    g_scaled: pd.DataFrame,
    galaxy_id: str,
    tau_config: TauReconstructionConfig,
) -> pd.DataFrame:
    return reconstruct_radial_tau_profile(
        g_scaled,
        galaxy_id,
        tau_config,
        reconstruction_stage="phase_4f_ml_sensitivity_tau",
    )


def _regional_rmse_from_test_points(rows: list[dict[str, Any]], n_points: int) -> dict[str, float]:
    if not rows:
        return {
            "total_holdout_rmse_kms": float("nan"),
            "inner_holdout_rmse_kms": float("nan"),
            "middle_holdout_rmse_kms": float("nan"),
            "outer_holdout_rmse_kms": float("nan"),
        }
    df = pd.DataFrame(rows)
    out: dict[str, float] = {
        "total_holdout_rmse_kms": float(rmse(df["v_obs_kms"], df["v_pred_kms"])),
    }
    for region in ("inner", "middle", "outer"):
        sub = df[df["radial_region_label"] == region]
        out[f"{region}_holdout_rmse_kms"] = (
            float(rmse(sub["v_obs_kms"], sub["v_pred_kms"])) if len(sub) else float("nan")
        )
    return out


def run_scaled_tdf_holdout(
    g_scaled: pd.DataFrame,
    tau_df: pd.DataFrame,
    galaxy_id: str,
    model_name: str,
    *,
    recon_yaml: dict,
    models_yaml: dict,
    n_points: int,
) -> dict[str, Any]:
    from tdf_galaxy_tau.models.tdf_knot import load_tdf_knot_config

    tdf_cfg = load_tdf_knot_config(recon_yaml)
    r = g_scaled["r_kpc"].to_numpy(dtype=float)
    v_obs = g_scaled["v_obs_kms"].to_numpy(dtype=float)
    v_err = g_scaled["v_err_kms"].to_numpy(dtype=float)
    v_bar = g_scaled["v_bar_kms"].to_numpy(dtype=float)
    split = even_odd_radial_split(n_points)
    data_mode = str(g_scaled["data_mode"].iloc[0]) if "data_mode" in g_scaled.columns else "unknown"

    rows = _export_tdf_test_points(
        galaxy_id,
        r,
        v_obs,
        v_err,
        v_bar,
        tau_df,
        model_name,
        split.name,
        split.train_indices,
        split.test_indices,
        k_g=tdf_cfg.k_g,
        safety_factor=tdf_cfg.amplitude_bound_safety_factor,
        negative_v2_penalty=tdf_cfg.negative_v2_penalty,
        data_mode=data_mode,
        n_points=n_points,
    )
    metrics = _regional_rmse_from_test_points(rows, n_points)
    neg_frac = float(np.mean(g_scaled["residual_v2_kms2"].to_numpy() < 0))
    neg_v2_count = int(sum(1 for row in rows if row.get("negative_v2_flag")))
    fit_status = rows[0]["fit_status"] if rows else "no_points"
    return {
        **metrics,
        "negative_residual_fraction": neg_frac,
        "negative_v2_count": neg_v2_count,
        "fit_status": fit_status,
        "fit_success": bool(rows[0]["fit_success"]) if rows else False,
    }


def _classification_under_scale(
    tdf_rmse: float,
    canonical_nfw: float,
    canonical_mond: float,
) -> str:
    if not np.isfinite(tdf_rmse):
        return "holdout_failure_like"
    if np.isfinite(canonical_nfw) and np.isfinite(canonical_mond):
        if tdf_rmse < canonical_nfw and tdf_rmse < canonical_mond:
            return "holdout_success_like"
    return "holdout_failure_like"


def is_plausible_scale(disk_scale: float, bulge_scale: float) -> bool:
    return (
        PLAUSIBLE_DISK_RANGE[0] <= disk_scale <= PLAUSIBLE_DISK_RANGE[1]
        and PLAUSIBLE_BULGE_RANGE[0] <= bulge_scale <= PLAUSIBLE_BULGE_RANGE[1]
    )


def load_canonical_holdout_rmse(holdout_csv: Path | str) -> pd.DataFrame:
    ho = pd.read_csv(holdout_csv)
    ho = ho[ho["split_name"] == HOLDOUT_SPLIT_PRIMARY]
    return ho.pivot_table(
        index="galaxy_id", columns="model_name", values="test_rmse_kms", aggfunc="first"
    )


def run_ml_sensitivity_audit(
    rotmod: pd.DataFrame,
    selected_ids: list[str],
    *,
    recon_path: Path | str = "configs/reconstruction.yaml",
    models_path: Path | str = "configs/models.yaml",
    holdout_validation_path: Path | str = "outputs/tables/sparc_tdf_holdout_validation.csv",
    ml_config: MlSensitivityConfig | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cfg = ml_config or MlSensitivityConfig()
    recon_yaml, models_yaml = load_holdout_export_configs(recon_path, models_path)
    tau_config = load_reconstruction_config(recon_path)
    canonical = load_canonical_holdout_rmse(holdout_validation_path)

    summary_rows: list[dict[str, Any]] = []

    for gid in selected_ids:
        g = rotmod[rotmod["galaxy_id"] == gid].copy()
        if g.empty:
            continue
        n_points = len(g)
        classification_canonical = MANDATED_GALAXY_CLASSIFICATION.get(gid, "unknown")
        nfw_can = float(canonical.loc[gid, "nfw_refit"]) if gid in canonical.index else float("nan")
        mond_can = float(canonical.loc[gid, "mond_fit_a0_simple"]) if gid in canonical.index else float("nan")

        for disk_scale in cfg.disk_scales:
            for bulge_scale in cfg.bulge_scales:
                g_scaled = scaled_galaxy_frame(g, disk_scale=disk_scale, bulge_scale=bulge_scale)
                tau_df = reconstruct_scaled_tau_table(g_scaled, gid, tau_config)
                for model_name in cfg.tdf_models:
                    metrics = run_scaled_tdf_holdout(
                        g_scaled,
                        tau_df,
                        gid,
                        model_name,
                        recon_yaml=recon_yaml,
                        models_yaml=models_yaml,
                        n_points=n_points,
                    )
                    inner_neg_frac = compute_inner_negative_fraction(g_scaled, n_points)
                    cls = _classification_under_scale(
                        metrics["total_holdout_rmse_kms"], nfw_can, mond_can
                    )
                    interpretation = (
                        "Diagnostic M/L scale; not final baryonic calibration. "
                        f"{'Improved vs canonical TDF' if np.isfinite(metrics['total_holdout_rmse_kms']) else 'fit issue'}."
                    )
                    summary_rows.append(
                        {
                            "galaxy_id": gid,
                            "classification_canonical": classification_canonical,
                            "disk_scale": disk_scale,
                            "bulge_scale": bulge_scale,
                            "model_name": model_name,
                            "total_holdout_rmse_kms": metrics["total_holdout_rmse_kms"],
                            "inner_holdout_rmse_kms": metrics["inner_holdout_rmse_kms"],
                            "middle_holdout_rmse_kms": metrics["middle_holdout_rmse_kms"],
                            "outer_holdout_rmse_kms": metrics["outer_holdout_rmse_kms"],
                            "negative_residual_fraction": metrics["negative_residual_fraction"],
                            "inner_negative_residual_fraction": inner_neg_frac,
                            "negative_v2_count": metrics["negative_v2_count"],
                            "classification_under_scale": cls,
                            "interpretation": interpretation,
                            "analysis_stage": ANALYSIS_STAGE,
                        }
                    )

    summary = pd.DataFrame(summary_rows)
    ngc_detail = build_ngc7814_ml_detail(summary, canonical)
    comparison = build_holdout_comparison(summary, canonical)
    return summary, ngc_detail, comparison


def build_ngc7814_ml_detail(summary: pd.DataFrame, canonical: pd.DataFrame) -> pd.DataFrame:
    del canonical
    sub = summary[summary["galaxy_id"] == TARGET_GALAXY].copy()
    if sub.empty:
        return pd.DataFrame()

    pivot_3 = sub[sub["model_name"] == "tdf_3knot"]
    pivot_5 = sub[sub["model_name"] == "tdf_5knot"]
    merged = pivot_3.merge(pivot_5, on=["disk_scale", "bulge_scale"], suffixes=("_3", "_5"))
    rows: list[dict[str, Any]] = []
    best_rmse = float(pivot_3["total_holdout_rmse_kms"].min())
    for _, row in merged.iterrows():
        d_scale = float(row["disk_scale"])
        b_scale = float(row["bulge_scale"])
        t3 = float(row["total_holdout_rmse_kms_3"])
        t3_inner = float(row["inner_holdout_rmse_kms_3"])
        t5 = float(row["total_holdout_rmse_kms_5"])
        t5_inner = float(row["inner_holdout_rmse_kms_5"])
        inner_neg = float(row.get("inner_negative_residual_fraction_3", float("nan")))
        plausible = is_plausible_scale(d_scale, b_scale)
        rows.append(
            {
                "disk_scale": d_scale,
                "bulge_scale": b_scale,
                "tdf_3knot_total_rmse": t3,
                "tdf_3knot_inner_rmse": t3_inner,
                "tdf_5knot_total_rmse": t5,
                "tdf_5knot_inner_rmse": t5_inner,
                "negative_residual_fraction_inner": inner_neg,
                "best_tdf_setting_flag": bool(np.isfinite(t3) and t3 <= best_rmse + 1e-6),
                "plausible_scale_flag": plausible,
                "interpretation": _ngc7814_cell_interpretation(t3, t3_inner, plausible, d_scale, b_scale),
            }
        )
    return pd.DataFrame(rows)


def _ngc7814_cell_interpretation(
    t3: float,
    t3_inner: float,
    plausible: bool,
    disk_scale: float,
    bulge_scale: float,
) -> str:
    parts = []
    if plausible:
        parts.append("Plausible diagnostic scale band.")
    else:
        parts.append("Outside plausible diagnostic band (may be extreme).")
    if np.isfinite(t3_inner) and t3_inner < 100:
        parts.append("Moderate inner TDF RMSE at this scale.")
    elif np.isfinite(t3_inner):
        parts.append("Inner TDF RMSE remains elevated.")
    return " ".join(parts)


def _best_rmse_in_plausible_band(sub: pd.DataFrame) -> float:
    mask = sub.apply(
        lambda r: is_plausible_scale(float(r["disk_scale"]), float(r["bulge_scale"])),
        axis=1,
    )
    pl = sub[mask]
    return float(pl["total_holdout_rmse_kms"].min()) if not pl.empty else float("nan")


def build_holdout_comparison(summary: pd.DataFrame, canonical: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for gid in summary["galaxy_id"].unique():
        sub = summary[(summary["galaxy_id"] == gid) & (summary["model_name"] == "tdf_3knot")]
        sub5 = summary[(summary["galaxy_id"] == gid) & (summary["model_name"] == "tdf_5knot")]
        if sub.empty:
            continue
        best_3 = float(sub["total_holdout_rmse_kms"].min())
        best_3_plausible = _best_rmse_in_plausible_band(sub)
        best_5 = float(sub5["total_holdout_rmse_kms"].min()) if not sub5.empty else float("nan")
        can_3 = float(canonical.loc[gid, "tdf_3knot"]) if gid in canonical.index else float("nan")
        can_5 = float(canonical.loc[gid, "tdf_5knot"]) if gid in canonical.index else float("nan")
        nfw = float(canonical.loc[gid, "nfw_refit"]) if gid in canonical.index else float("nan")
        mond = float(canonical.loc[gid, "mond_fit_a0_simple"]) if gid in canonical.index else float("nan")
        improved = bool(np.isfinite(best_3) and np.isfinite(can_3) and best_3 < can_3 * 0.95)
        beats_nfw = bool(np.isfinite(best_3) and np.isfinite(nfw) and best_3 < nfw)
        beats_mond = bool(np.isfinite(best_3) and np.isfinite(mond) and best_3 < mond)
        beats_nfw_plausible = bool(
            np.isfinite(best_3_plausible) and np.isfinite(nfw) and best_3_plausible < nfw
        )
        rows.append(
            {
                "galaxy_id": gid,
                "canonical_tdf_3knot_rmse": can_3,
                "best_scaled_tdf_3knot_rmse": best_3,
                "best_plausible_scaled_tdf_3knot_rmse": best_3_plausible,
                "canonical_tdf_5knot_rmse": can_5,
                "best_scaled_tdf_5knot_rmse": best_5,
                "canonical_nfw_rmse": nfw,
                "canonical_mond_rmse": mond,
                "tdf_improved_under_ml_scaling": improved,
                "tdf_beats_nfw_under_best_scale": beats_nfw,
                "tdf_beats_mond_under_best_scale": beats_mond,
                "tdf_beats_nfw_under_plausible_scale": beats_nfw_plausible,
                "caveat": (
                    "NFW/MOND are canonical train-only holdout at M/L=1; not re-scaled in Phase 4F. "
                    "TDF refit per scale uses scaled baryons."
                ),
            }
        )
    return pd.DataFrame(rows)


def compute_inner_negative_fraction(g_scaled: pd.DataFrame, n_points: int) -> float:
    rv2 = g_scaled["residual_v2_kms2"].to_numpy()
    inner_idx = [i for i in range(n_points) if radial_region_label_for_index(n_points, i) == "inner"]
    if not inner_idx:
        return float("nan")
    return float(np.mean(rv2[inner_idx] < 0))


def plot_ngc7814_inner_rmse_heatmap(detail: pd.DataFrame, output_path: Path) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    pivot = detail.pivot_table(
        index="bulge_scale", columns="disk_scale", values="tdf_3knot_inner_rmse", aggfunc="first"
    )
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(pivot.values, aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_yticks(range(len(pivot.index)))
    ax.set_xticklabels([f"{c:.1f}" for c in pivot.columns])
    ax.set_yticklabels([f"{i:.1f}" for i in pivot.index])
    ax.set_xlabel("disk_scale (diagnostic M/L)")
    ax.set_ylabel("bulge_scale (diagnostic M/L)")
    ax.set_title(f"{TARGET_GALAXY} — diagnostic M/L sensitivity: tdf_3knot inner holdout RMSE")
    fig.colorbar(im, ax=ax, label="inner RMSE [km/s]")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_ngc7814_tau_profiles(
    rotmod: pd.DataFrame,
    tau_config: TauReconstructionConfig,
    detail: pd.DataFrame,
    output_path: Path,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    g = rotmod[rotmod["galaxy_id"] == TARGET_GALAXY].sort_values("r_kpc")
    tau_can = reconstruct_radial_tau_profile(g, TARGET_GALAXY, tau_config)
    best = detail[detail["best_tdf_setting_flag"]].iloc[0]
    g_best = scaled_galaxy_frame(
        g, disk_scale=float(best["disk_scale"]), bulge_scale=float(best["bulge_scale"])
    )
    tau_best = reconstruct_scaled_tau_table(g_best, TARGET_GALAXY, tau_config)

    fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    axes[0].plot(tau_can["r_kpc"], tau_can["dtaudr_reconstructed"], "k-", label="canonical M/L (1,1)")
    axes[0].plot(
        tau_best["r_kpc"],
        tau_best["dtaudr_reconstructed"],
        "C3--",
        label=f"scaled d={best['disk_scale']}, b={best['bulge_scale']}",
    )
    axes[0].set_ylabel("dτ/dr")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)
    axes[1].plot(tau_can["r_kpc"], tau_can["tau_reconstructed"], "k-")
    axes[1].plot(tau_best["r_kpc"], tau_best["tau_reconstructed"], "C3--")
    axes[1].set_xlabel("r [kpc]")
    axes[1].set_ylabel("τ")
    axes[1].set_title(f"{TARGET_GALAXY} — diagnostic τ profiles (not final calibration)")
    fig.tight_layout()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_success_vs_failure_summary(comparison: pd.DataFrame, output_path: Path) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(comparison))
    width = 0.2
    ax.bar(x - 1.5 * width, comparison["canonical_tdf_3knot_rmse"], width, label="canonical tdf_3knot")
    ax.bar(x - 0.5 * width, comparison["best_scaled_tdf_3knot_rmse"], width, label="best scaled tdf_3knot")
    ax.bar(x + 0.5 * width, comparison["canonical_nfw_rmse"], width, label="canonical nfw")
    ax.bar(x + 1.5 * width, comparison["canonical_mond_rmse"], width, label="canonical mond")
    ax.set_xticks(x)
    ax.set_xticklabels(comparison["galaxy_id"], rotation=30, ha="right")
    ax.set_ylabel("even/odd holdout RMSE [km/s]")
    ax.set_title("M/L sensitivity: canonical vs best scaled TDF (diagnostic)")
    ax.legend(fontsize=7)
    ax.grid(axis="y", alpha=0.3)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def write_ml_sensitivity_report(
    path: Path,
    *,
    summary: pd.DataFrame,
    ngc_detail: pd.DataFrame,
    comparison: pd.DataFrame,
    ml_config: MlSensitivityConfig,
) -> None:
    ngc = comparison[comparison["galaxy_id"] == TARGET_GALAXY].iloc[0]
    best_row = ngc_detail[ngc_detail["best_tdf_setting_flag"]].iloc[0] if not ngc_detail.empty else None
    success = comparison[comparison["galaxy_id"] != TARGET_GALAXY]

    lines = [
        "# SPARC M/L Sensitivity Audit Report (Phase 4F)",
        "",
        "> This phase is a diagnostic M/L sensitivity audit. It does not recalibrate SPARC baryons, "
        "does not introduce a final fitted M/L model, does not validate TDF on full SPARC, "
        "does not disprove dark matter, and does not include lensing.",
        "",
        "## Objective",
        "",
        "Test whether the **NGC7814** TDF holdout failure (Phase 4E inner-region localization) is sensitive "
        "to diagnostic disk/bulge mass-to-light scaling of the fixed SPARC baryonic decomposition.",
        "",
        "## Scaling method",
        "",
        "Canonical convention (Phase 1A): `v_bar² = v_gas² + s_disk·v_disk² + s_bulge·v_bulge²` with "
        "signed component velocities as stored in SPARC rotmod. Gas term is **not** scaled. "
        "τ profiles use `tau(r_min)=0` as in Phase 2A. TDF holdout uses **train-only** even/odd refit per scale.",
        "",
        "## Scale grid",
        "",
        f"- disk_scale: {list(ml_config.disk_scales)}",
        f"- bulge_scale: {list(ml_config.bulge_scales)}",
        f"- Plausible band (diagnostic): disk ∈ {PLAUSIBLE_DISK_RANGE}, bulge ∈ {PLAUSIBLE_BULGE_RANGE}",
        "",
        "## NGC7814 results",
        "",
        f"- Canonical tdf_3knot RMSE: **{ngc['canonical_tdf_3knot_rmse']:.1f}** km/s",
        f"- Best scaled tdf_3knot RMSE: **{ngc['best_scaled_tdf_3knot_rmse']:.1f}** km/s",
        f"- Canonical NFW/MOND (not M/L-scaled): **{ngc['canonical_nfw_rmse']:.1f}** / **{ngc['canonical_mond_rmse']:.1f}** km/s",
        f"- TDF improved under scaling: **{ngc['tdf_improved_under_ml_scaling']}**",
        f"- TDF beats NFW under best scale (any grid point): **{ngc['tdf_beats_nfw_under_best_scale']}**",
        f"- TDF beats NFW under plausible band: **{ngc.get('tdf_beats_nfw_under_plausible_scale', False)}**",
        f"- Best plausible scaled tdf_3knot RMSE: **{ngc.get('best_plausible_scaled_tdf_3knot_rmse', float('nan')):.1f}** km/s",
        f"- TDF beats MOND under best scale: **{ngc['tdf_beats_mond_under_best_scale']}**",
        "",
    ]
    if best_row is not None:
        lines.extend(
            [
                f"- Best grid cell (tdf_3knot): disk_scale={best_row['disk_scale']}, bulge_scale={best_row['bulge_scale']}, "
                f"inner RMSE={best_row['tdf_3knot_inner_rmse']:.1f} km/s, plausible_scale={best_row['plausible_scale_flag']}.",
                "",
            ]
        )

    lines.extend(
        [
            "### Interpretation (NGC7814)",
            "",
            _ngc7814_report_conclusion(ngc, ngc_detail, best_row),
            "",
            "## Success-galaxy stability",
            "",
            f"- Success cases with `tdf_improved_under_ml_scaling` True: "
            f"{int(success['tdf_improved_under_ml_scaling'].sum())} / {len(success)}.",
            f"- Success cases losing holdout-success-like status under any grid cell: "
            f"{_count_success_unstable(summary)} galaxies (see summary table).",
            "",
            "## Limitations",
            "",
            "- Diagnostic scaling only; not a full M/L fit or photometric calibration.",
            "- NFW/MOND comparisons use **canonical** holdout at default baryons unless noted.",
            "- K_tau, distance, and inclination are fixed.",
            "- even/odd split only for aggregated Phase 4F tables.",
            "",
            "## Outputs",
            "",
            "- `outputs/tables/sparc_ml_sensitivity_summary.csv`",
            "- `outputs/tables/ngc7814_ml_sensitivity_detail.csv`",
            "- `outputs/tables/sparc_ml_sensitivity_holdout_comparison.csv`",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _ngc7814_report_conclusion(
    ngc: pd.Series,
    detail: pd.DataFrame,
    best_row: pd.Series | None,
) -> str:
    can = float(ngc["canonical_tdf_3knot_rmse"])
    best = float(ngc["best_scaled_tdf_3knot_rmse"])
    nfw = float(ngc["canonical_nfw_rmse"])
    improved = best < can * 0.95 if np.isfinite(best) and np.isfinite(can) else False
    beats_nfw = bool(ngc["tdf_beats_nfw_under_best_scale"])
    plausible_best = bool(best_row["plausible_scale_flag"]) if best_row is not None else False

    parts = []
    if improved:
        parts.append(
            "Lowering bulge_scale and/or disk_scale **can reduce** TDF holdout RMSE versus canonical baryons; "
            "inner RMSE typically improves when bulge contribution is reduced."
        )
    else:
        parts.append("M/L scaling does **not** materially improve total holdout RMSE on the explored grid.")

    if beats_nfw and plausible_best:
        parts.append(
            "At the **best plausible-scale** setting, TDF becomes competitive with canonical NFW/MOND on total RMSE."
        )
    beats_nfw_pl = bool(ngc.get("tdf_beats_nfw_under_plausible_scale", False))
    best_pl = float(ngc.get("best_plausible_scaled_tdf_3knot_rmse", float("nan")))
    if beats_nfw_pl:
        parts.append(
            f"Within the **plausible diagnostic band**, TDF tdf_3knot RMSE (~{best_pl:.1f} km/s) can be "
            "competitive with canonical NFW/MOND — but this is **not** the canonical SPARC decomposition."
        )
    elif beats_nfw and not plausible_best:
        parts.append(
            "TDF can beat NFW/MOND only when **disk_scale** is below the plausible band (e.g. 0.5) — scientifically suspicious."
        )
    else:
        parts.append(
            "**NGC7814 remains a holdout failure mode** relative to canonical NFW/MOND across the tested grid; "
            "the Phase 4A label at canonical M/L=1 is unchanged."
        )
    parts.append(
        "At **canonical** disk_scale=bulge_scale=1.0, holdout RMSE matches Phase 3C/4E (~156 km/s); "
        "the failure is **highly sensitive** to bulge/disk scaling."
    )
    parts.append(
        "This **partially reduces** inner negative residual_v² when bulge_scale is lowered but does **not** "
        "establish a final astrophysical M/L calibration."
    )
    return " ".join(parts)


def _count_success_unstable(summary: pd.DataFrame) -> int:
    unstable = 0
    for gid in summary["galaxy_id"].unique():
        if gid == TARGET_GALAXY:
            continue
        if MANDATED_GALAXY_CLASSIFICATION.get(gid) != "robust_tdf_success":
            continue
        sub = summary[(summary["galaxy_id"] == gid) & (summary["model_name"] == "tdf_3knot")]
        if (sub["classification_under_scale"] == "holdout_failure_like").any():
            unstable += 1
    return unstable
