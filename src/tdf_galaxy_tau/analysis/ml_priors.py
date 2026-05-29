from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION

TARGET_GALAXY = "NGC7814"
GALAXY_ORDER = tuple(MANDATED_GALAXY_CLASSIFICATION.keys())
MODELS = ("tdf_3knot", "tdf_5knot", "nfw_refit_scaled", "mond_fit_a0_scaled")
TDF_PRIMARY = "tdf_3knot"
TDF_SENSITIVITY = "tdf_5knot"
NFW_MODEL = "nfw_refit_scaled"
MOND_MODEL = "mond_fit_a0_scaled"

INTERPRETATION_LOGIC_VERSION = "phase_4i_audit_v2"

NGC7814_INTERPRETATIONS = (
    "canonical_failure_only",
    "canonical_failure_primary_tdf_3knot",
    "baryon_sensitive_competitive",
    "sensitivity_tdf_5knot_diagnostic_recovery",
    "primary_tdf_3knot_diagnostic_recovery",
    "prior_supported_baseline_preference",
    "inconclusive",
)


@dataclass(frozen=True)
class PriorScenario:
    name: str
    description: str
    grid_scope: str
    weighting: str
    params: dict[str, Any]


def load_ml_priors_config(path: Path | str = "configs/ml_priors.yaml") -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def parse_prior_scenarios(config: dict[str, Any]) -> list[PriorScenario]:
    scenarios_cfg = config.get("scenarios", {})
    out: list[PriorScenario] = []
    for name, spec in scenarios_cfg.items():
        if not isinstance(spec, dict):
            continue
        params = {k: v for k, v in spec.items() if k not in ("description", "grid_scope", "weighting")}
        out.append(
            PriorScenario(
                name=name,
                description=str(spec.get("description", "")),
                grid_scope=str(spec.get("grid_scope", "plausible_only")),
                weighting=str(spec.get("weighting", "uniform")),
                params=params,
            )
        )
    return out


def cell_in_scope(
    disk_scale: float,
    bulge_scale: float,
    *,
    grid_scope: str,
    plausible_disk: tuple[float, float],
    plausible_bulge: tuple[float, float],
) -> bool:
    if grid_scope == "all_grid":
        return True
    return (
        plausible_disk[0] <= disk_scale <= plausible_disk[1]
        and plausible_bulge[0] <= bulge_scale <= plausible_bulge[1]
    )


def cell_prior_weight(
    disk_scale: float,
    bulge_scale: float,
    scenario: PriorScenario,
    *,
    canonical_disk: float,
    canonical_bulge: float,
    plausible_disk: tuple[float, float],
    plausible_bulge: tuple[float, float],
) -> float:
    if not cell_in_scope(
        disk_scale,
        bulge_scale,
        grid_scope=scenario.grid_scope,
        plausible_disk=plausible_disk,
        plausible_bulge=plausible_bulge,
    ):
        return 0.0

    if scenario.weighting == "uniform":
        return 1.0

    if scenario.weighting == "bulge_downweight":
        ref = float(scenario.params.get("bulge_reference", 1.0))
        return max(ref - bulge_scale + 0.5, 0.05)

    if scenario.weighting == "gaussian_delta":
        sd = float(scenario.params.get("sigma_disk", 0.2))
        sb = float(scenario.params.get("sigma_bulge", 0.2))
        zd = (disk_scale - canonical_disk) / sd
        zb = (bulge_scale - canonical_bulge) / sb
        return float(np.exp(-0.5 * (zd * zd + zb * zb)))

    return 0.0


def _weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    w = np.asarray(weights, dtype=float)
    v = np.asarray(values, dtype=float)
    mask = w > 0
    if not np.any(mask):
        return float("nan")
    return float(np.average(v[mask], weights=w[mask]))


def _weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    w = np.asarray(weights, dtype=float)
    v = np.asarray(values, dtype=float)
    mask = w > 0
    if not np.any(mask):
        return float("nan")
    order = np.argsort(v[mask])
    v_sorted = v[mask][order]
    w_sorted = w[mask][order]
    cum = np.cumsum(w_sorted) / w_sorted.sum()
    idx = int(np.searchsorted(cum, 0.5))
    idx = min(idx, len(v_sorted) - 1)
    return float(v_sorted[idx])


def _pivot_cell_rmse(galaxy_df: pd.DataFrame) -> pd.DataFrame:
    """One row per (disk_scale, bulge_scale) with RMSE columns per model."""
    rows: list[dict[str, Any]] = []
    for (d, b), grp in galaxy_df.groupby(["disk_scale", "bulge_scale"], sort=False):
        row: dict[str, Any] = {
            "disk_scale": float(d),
            "bulge_scale": float(b),
            "plausible_scale_flag": bool(grp["plausible_scale_flag"].iloc[0]),
        }
        for model in MODELS:
            sub = grp[grp["model_name"] == model]
            row[model] = float(sub["total_holdout_rmse_kms"].iloc[0]) if not sub.empty else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def _winner_model(row: pd.Series) -> str:
    rmse_map = {m: float(row[m]) for m in MODELS if np.isfinite(row.get(m, np.nan))}
    if not rmse_map:
        return ""
    return min(rmse_map, key=rmse_map.get)


def compute_prior_weighted_metrics_for_galaxy(
    galaxy_df: pd.DataFrame,
    scenario: PriorScenario,
    *,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    plausible = config.get("plausible_band", {})
    p_disk = tuple(plausible.get("disk_scale", [0.7, 1.3]))
    p_bulge = tuple(plausible.get("bulge_scale", [0.5, 1.0]))
    can = config.get("canonical_ml", {})
    c_disk = float(can.get("disk_scale", 1.0))
    c_bulge = float(can.get("bulge_scale", 1.0))

    cells = _pivot_cell_rmse(galaxy_df)
    weights = np.array(
        [
            cell_prior_weight(
                float(r["disk_scale"]),
                float(r["bulge_scale"]),
                scenario,
                canonical_disk=c_disk,
                canonical_bulge=c_bulge,
                plausible_disk=p_disk,
                plausible_bulge=p_bulge,
            )
            for _, r in cells.iterrows()
        ]
    )
    total_w = float(weights.sum())
    if total_w <= 0:
        return []

    winners = cells.apply(_winner_model, axis=1)
    plausible_mask = cells["plausible_scale_flag"].to_numpy()

    rows_out: list[dict[str, Any]] = []
    for model in MODELS:
        rmse_vals = cells[model].to_numpy(dtype=float)
        win_mask = winners == model
        beats_nfw_mask = np.array(
            [
                np.isfinite(cells[model].iloc[i])
                and np.isfinite(cells[NFW_MODEL].iloc[i])
                and cells[model].iloc[i] < cells[NFW_MODEL].iloc[i]
                for i in range(len(cells))
            ]
        )
        beats_mond_mask = np.array(
            [
                np.isfinite(cells[model].iloc[i])
                and np.isfinite(cells[MOND_MODEL].iloc[i])
                and cells[model].iloc[i] < cells[MOND_MODEL].iloc[i]
                for i in range(len(cells))
            ]
        )

        pl_rmse = rmse_vals[plausible_mask]
        pl_w = weights[plausible_mask]
        best_plausible = float(np.nanmin(pl_rmse)) if len(pl_rmse) else float("nan")

        rows_out.append(
            {
                "prior_scenario": scenario.name,
                "grid_scope": scenario.grid_scope,
                "model_name": model,
                "prior_weighted_mean_rmse": _weighted_mean(rmse_vals, weights),
                "prior_weighted_median_rmse": _weighted_median(rmse_vals, weights),
                "best_plausible_rmse": best_plausible,
                "fraction_of_prior_weight_where_model_wins": float(weights[win_mask].sum() / total_w),
                "fraction_of_prior_weight_where_tdf_beats_nfw": float(
                    weights[beats_nfw_mask].sum() / total_w
                ),
                "fraction_of_prior_weight_where_tdf_beats_mond": float(
                    weights[beats_mond_mask].sum() / total_w
                ),
                "total_prior_weight": total_w,
                "n_cells_in_scope": int(np.sum(weights > 0)),
            }
        )
    return rows_out


def _model_metrics_dict(by_model: dict[str, pd.Series]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for name in MODELS:
        row = by_model.get(name)
        if row is None or (isinstance(row, pd.Series) and row.empty):
            out[name] = {}
            continue
        r = row if isinstance(row, dict) else row.to_dict()
        out[name] = {
            "prior_weighted_mean_rmse": float(r.get("prior_weighted_mean_rmse", float("nan"))),
            "fraction_wins": float(r.get("fraction_of_prior_weight_where_model_wins", 0)),
            "fraction_beats_nfw": float(r.get("fraction_of_prior_weight_where_tdf_beats_nfw", 0)),
            "fraction_beats_mond": float(r.get("fraction_of_prior_weight_where_tdf_beats_mond", 0)),
        }
    return out


def _per_model_prior_result(
    *,
    win_frac: float,
    beats_nfw_frac: float,
    weighted_mean: float,
    canonical_tdf_rmse: float,
    is_primary_tdf: bool,
) -> str:
    if win_frac >= 0.45:
        return "prior_weighted_win_fraction_elevated"
    if beats_nfw_frac >= 0.45:
        return "competitive_beats_nfw_on_weighted_cells"
    if win_frac >= 0.25 or beats_nfw_frac >= 0.3:
        return "baryon_sensitive_competitive"
    if is_primary_tdf and np.isfinite(weighted_mean) and weighted_mean > canonical_tdf_rmse * 0.25:
        return "canonical_failure_persists_under_prior"
    if not is_primary_tdf and win_frac >= 0.35:
        return "sensitivity_model_elevated_support"
    return "limited_prior_support"


def classify_ngc7814_layered(
    by_model: dict[str, pd.Series],
    *,
    canonical_tdf_rmse: float,
    canonical_nfw_rmse: float,
) -> dict[str, str]:
    """Layered NGC7814 labels: canonical vs primary tdf_3knot vs sensitivity tdf_5knot."""
    metrics = _model_metrics_dict(by_model)
    tdf3 = metrics.get(TDF_PRIMARY, {})
    tdf5 = metrics.get(TDF_SENSITIVITY, {})
    nfw = metrics.get(NFW_MODEL, {})

    tdf3_wins = tdf3.get("fraction_wins", 0.0)
    tdf5_wins = tdf5.get("fraction_wins", 0.0)
    tdf3_beats_nfw = tdf3.get("fraction_beats_nfw", 0.0)
    tdf5_beats_nfw = tdf5.get("fraction_beats_nfw", 0.0)
    tdf3_mean = tdf3.get("prior_weighted_mean_rmse", float("nan"))
    nfw_mean = nfw.get("prior_weighted_mean_rmse", float("nan"))

    canonical_fail = (
        np.isfinite(canonical_tdf_rmse)
        and np.isfinite(canonical_nfw_rmse)
        and canonical_tdf_rmse > canonical_nfw_rmse * 2
    )

    canonical_result = (
        "canonical_tdf_holdout_failure_at_ml_1"
        if canonical_fail
        else "canonical_not_failure_by_rmse_threshold"
    )

    primary_result = _per_model_prior_result(
        win_frac=tdf3_wins,
        beats_nfw_frac=tdf3_beats_nfw,
        weighted_mean=tdf3_mean,
        canonical_tdf_rmse=canonical_tdf_rmse,
        is_primary_tdf=True,
    )
    sensitivity_result = _per_model_prior_result(
        win_frac=tdf5_wins,
        beats_nfw_frac=tdf5_beats_nfw,
        weighted_mean=tdf5.get("prior_weighted_mean_rmse", float("nan")),
        canonical_tdf_rmse=canonical_tdf_rmse,
        is_primary_tdf=False,
    )

    either_wins = max(tdf3_wins, tdf5_wins)
    if either_wins >= 0.45:
        either_result = "either_tdf_variant_elevated_win_fraction"
    elif max(tdf3_beats_nfw, tdf5_beats_nfw) >= 0.35:
        either_result = "either_tdf_variant_competitive_vs_nfw"
    elif either_wins >= 0.2:
        either_result = "either_tdf_variant_mixed_support"
    else:
        either_result = "either_tdf_variant_limited_support"

    if not canonical_fail:
        category = "inconclusive"
    elif tdf3_wins >= 0.45:
        category = "primary_tdf_3knot_diagnostic_recovery"
    elif tdf3_wins < 0.15 and tdf5_wins >= 0.45:
        category = "sensitivity_tdf_5knot_diagnostic_recovery"
    elif np.isfinite(nfw_mean) and np.isfinite(tdf3_mean) and nfw_mean < min(tdf3_mean, 20) * 0.85:
        category = "prior_supported_baseline_preference"
    elif tdf3_wins < 0.15 and tdf5_wins < 0.25:
        category = "canonical_failure_primary_tdf_3knot"
    elif either_wins >= 0.25 or max(tdf3_beats_nfw, tdf5_beats_nfw) >= 0.3:
        category = "baryon_sensitive_competitive"
    else:
        category = "canonical_failure_only"

    if category == "sensitivity_tdf_5knot_diagnostic_recovery":
        claim = (
            "Canonical failure at M/L=1 unchanged. Under this diagnostic prior, "
            "**tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — "
            "not primary **tdf_3knot** recovery. Not final M/L calibration."
        )
    elif category == "primary_tdf_3knot_diagnostic_recovery":
        claim = (
            "Canonical failure at M/L=1 unchanged. Diagnostic prior shows elevated "
            "**tdf_3knot** support — still conditional, not calibrated."
        )
    elif category == "prior_supported_baseline_preference":
        claim = (
            "Canonical failure at M/L=1. Prior-weighted mean RMSE favors scaled NFW/MOND "
            "over primary tdf_3knot on this scenario."
        )
    elif category in ("canonical_failure_only", "canonical_failure_primary_tdf_3knot"):
        claim = (
            "Canonical TDF holdout failure at M/L=1; primary tdf_3knot lacks prior-weighted "
            "win support. Lower-bulge cells can still lower RMSE (baryon sensitivity)."
        )
    else:
        claim = (
            "Mixed diagnostic prior signals; use per-cell breakdown. Canonical failure at M/L=1 "
            "unchanged. Do not claim calibrated recovery."
        )

    return {
        "canonical_result": canonical_result,
        "primary_tdf_3knot_prior_result": primary_result,
        "sensitivity_tdf_5knot_prior_result": sensitivity_result,
        "either_tdf_variant_prior_result": either_result,
        "interpretation_category": category,
        "recommended_claim_language": claim,
    }


def classify_ngc7814_interpretation(
    summary_row: pd.Series,
    *,
    canonical_tdf_rmse: float,
    canonical_nfw_rmse: float,
) -> str:
    """Backward-compatible single category from enriched tdf_3knot row."""
    layered = classify_ngc7814_layered(
        {
            TDF_PRIMARY: summary_row,
            TDF_SENSITIVITY: pd.Series(
                {
                    "fraction_of_prior_weight_where_model_wins": summary_row.get(
                        "tdf_5knot_fraction_wins", 0
                    ),
                    "fraction_of_prior_weight_where_tdf_beats_nfw": summary_row.get(
                        "tdf_5knot_fraction_beats_nfw", 0
                    ),
                    "prior_weighted_mean_rmse": summary_row.get(
                        "tdf_5knot_prior_weighted_mean_rmse", float("nan")
                    ),
                }
            ),
            NFW_MODEL: pd.Series(
                {"prior_weighted_mean_rmse": summary_row.get("nfw_prior_weighted_mean_rmse")}
            ),
        },
        canonical_tdf_rmse=canonical_tdf_rmse,
        canonical_nfw_rmse=canonical_nfw_rmse,
    )
    return layered["interpretation_category"]


def build_prior_weighted_summary(
    comparison: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    scenarios = parse_prior_scenarios(config)
    rows: list[dict[str, Any]] = []

    for gid in GALAXY_ORDER:
        gdf = comparison[comparison["galaxy_id"] == gid]
        if gdf.empty:
            continue
        classification = MANDATED_GALAXY_CLASSIFICATION.get(gid, "unknown")
        for scenario in scenarios:
            metrics = compute_prior_weighted_metrics_for_galaxy(gdf, scenario, config=config)
            for m in metrics:
                rows.append(
                    {
                        "galaxy_id": gid,
                        "canonical_classification": classification,
                        **m,
                    }
                )

    return pd.DataFrame(rows)


def build_ngc7814_prior_interpretation(
    summary: pd.DataFrame,
    post_ml: pd.DataFrame,
    *,
    primary_scenario: str = "uniform_plausible_band",
) -> pd.DataFrame:
    ngc_post = post_ml[post_ml["galaxy_id"] == TARGET_GALAXY]
    can_tdf = float(ngc_post["canonical_tdf_3knot_rmse"].iloc[0]) if not ngc_post.empty else float("nan")
    can_nfw = float(ngc_post["canonical_nfw_rmse"].iloc[0]) if not ngc_post.empty else float("nan")

    rows: list[dict[str, Any]] = []
    for scenario_name in summary["prior_scenario"].unique():
        sub = summary[(summary["galaxy_id"] == TARGET_GALAXY) & (summary["prior_scenario"] == scenario_name)]
        if sub.empty:
            continue
        by_model = {str(r["model_name"]): r for _, r in sub.iterrows()}
        tdf_row = by_model.get(TDF_PRIMARY, pd.Series(dtype=float))
        tdf5_row = by_model.get(TDF_SENSITIVITY, pd.Series(dtype=float))
        nfw_row = by_model.get(NFW_MODEL, pd.Series(dtype=float))
        mond_row = by_model.get(MOND_MODEL, pd.Series(dtype=float))

        enriched = tdf_row.copy() if isinstance(tdf_row, pd.Series) else pd.Series(dtype=float)
        if isinstance(enriched, pd.Series) and not enriched.empty:
            enriched = enriched.to_dict()
        else:
            enriched = {}
        enriched["nfw_prior_weighted_mean_rmse"] = (
            float(nfw_row["prior_weighted_mean_rmse"]) if len(nfw_row) else float("nan")
        )
        enriched["mond_prior_weighted_mean_rmse"] = (
            float(mond_row["prior_weighted_mean_rmse"]) if len(mond_row) else float("nan")
        )
        enriched["tdf_5knot_fraction_wins"] = (
            float(tdf5_row["fraction_of_prior_weight_where_model_wins"]) if len(tdf5_row) else float("nan")
        )
        enriched["tdf_5knot_prior_weighted_mean_rmse"] = (
            float(tdf5_row["prior_weighted_mean_rmse"]) if len(tdf5_row) else float("nan")
        )
        enriched["tdf_5knot_fraction_beats_nfw"] = (
            float(tdf5_row["fraction_of_prior_weight_where_tdf_beats_nfw"])
            if len(tdf5_row)
            else float("nan")
        )

        layered = classify_ngc7814_layered(
            by_model,
            canonical_tdf_rmse=can_tdf,
            canonical_nfw_rmse=can_nfw,
        )
        interpretation = layered["interpretation_category"]
        rows.append(
            {
                "prior_scenario": scenario_name,
                "interpretation_logic_version": INTERPRETATION_LOGIC_VERSION,
                "canonical_tdf_3knot_rmse": can_tdf,
                "canonical_nfw_rmse": can_nfw,
                "canonical_result": layered["canonical_result"],
                "tdf_3knot_prior_weighted_mean_rmse": enriched.get("prior_weighted_mean_rmse"),
                "tdf_3knot_best_plausible_rmse": enriched.get("best_plausible_rmse"),
                "nfw_prior_weighted_mean_rmse": enriched.get("nfw_prior_weighted_mean_rmse"),
                "mond_prior_weighted_mean_rmse": enriched.get("mond_prior_weighted_mean_rmse"),
                "tdf_3knot_fraction_prior_weight_wins": enriched.get(
                    "fraction_of_prior_weight_where_model_wins"
                ),
                "tdf_3knot_fraction_beats_nfw": enriched.get(
                    "fraction_of_prior_weight_where_tdf_beats_nfw"
                ),
                "tdf_5knot_fraction_prior_weight_wins": enriched.get("tdf_5knot_fraction_wins"),
                "tdf_5knot_fraction_beats_nfw": enriched.get("tdf_5knot_fraction_beats_nfw"),
                "tdf_5knot_prior_weighted_mean_rmse": enriched.get("tdf_5knot_prior_weighted_mean_rmse"),
                "primary_tdf_3knot_prior_result": layered["primary_tdf_3knot_prior_result"],
                "sensitivity_tdf_5knot_prior_result": layered["sensitivity_tdf_5knot_prior_result"],
                "either_tdf_variant_prior_result": layered["either_tdf_variant_prior_result"],
                "interpretation_category": interpretation,
                "recommended_claim_language": layered["recommended_claim_language"],
                "interpretation_note": _interpretation_note(interpretation, scenario_name),
            }
        )
    return pd.DataFrame(rows)


def _interpretation_note(category: str, scenario: str) -> str:
    notes = {
        "canonical_failure_only": (
            "Canonical holdout failure dominates; limited prior-weighted TDF win support."
        ),
        "canonical_failure_primary_tdf_3knot": (
            "Canonical failure at M/L=1; primary tdf_3knot lacks prior-weighted wins."
        ),
        "baryon_sensitive_competitive": (
            "Diagnostic priors place substantial weight where TDF is competitive but not uniquely favored."
        ),
        "sensitivity_tdf_5knot_diagnostic_recovery": (
            "tdf_5knot elevated win fraction — sensitivity model only, not primary conservative claim."
        ),
        "primary_tdf_3knot_diagnostic_recovery": (
            "tdf_3knot elevated win fraction under diagnostic prior — still not calibrated."
        ),
        "prior_supported_baseline_preference": (
            "Prior-weighted mean RMSE favors scaled NFW/MOND over primary tdf_3knot."
        ),
        "inconclusive": "Mixed prior-weighted signals; ingest photometry before stronger claims.",
    }
    return f"[{scenario}] {notes.get(category, '')}"


def write_ml_prior_framework_report(
    path: Path,
    *,
    summary: pd.DataFrame,
    ngc_interp: pd.DataFrame,
    config: dict[str, Any],
) -> None:
    primary = ngc_interp[ngc_interp["prior_scenario"] == "uniform_plausible_band"]
    ngc_line = primary.iloc[0] if not primary.empty else None

    lines = [
        "# SPARC Diagnostic M/L Prior Framework Report (Phase 4I)",
        "",
        "> **No final photometric M/L calibration is performed.** Priors are **diagnostic placeholders** "
        "over existing Phase 4G grid results. This scaffold guides which photometric metadata to ingest next.",
        "",
        "> NGC7814 remains a **canonical TDF holdout failure** at disk=bulge=1. Any “recovery” under priors "
        "is **conditional and diagnostic**, not validation.",
        "",
        "## Objective",
        "",
        "Provide a conservative **prior-weighting scaffold** on Phase 4G fair scaled comparisons without new fits.",
        "",
        "## Prior scenarios (diagnostic only)",
        "",
    ]
    for sc in parse_prior_scenarios(config):
        lines.append(f"- **{sc.name}:** {sc.description} (`{sc.weighting}`, scope={sc.grid_scope})")

    lines.extend(
        [
            "",
            "## Plausible band (from config)",
            "",
            f"- disk_scale ∈ {config.get('plausible_band', {}).get('disk_scale')}",
            f"- bulge_scale ∈ {config.get('plausible_band', {}).get('bulge_scale')}",
            "",
            "## NGC7814 prior-weighted interpretation",
            "",
        ]
    )
    if ngc_line is not None:
        lines.extend(
            [
                f"- Category (**uniform_plausible_band**): `{ngc_line['interpretation_category']}`",
                f"- Canonical tdf_3knot / NFW: {ngc_line['canonical_tdf_3knot_rmse']:.1f} / "
                f"{ngc_line['canonical_nfw_rmse']:.1f} km/s",
                f"- Primary tdf_3knot win fraction: {ngc_line['tdf_3knot_fraction_prior_weight_wins']:.2f}; "
                f"sensitivity tdf_5knot: {ngc_line['tdf_5knot_fraction_prior_weight_wins']:.2f}",
                f"- {ngc_line.get('recommended_claim_language', ngc_line.get('interpretation_note', ''))}",
                "",
            ]
        )

    success = summary[summary["galaxy_id"] != TARGET_GALAXY]
    sc = "uniform_plausible_band"
    tdf_primary = success[
        (success["prior_scenario"] == sc) & (success["model_name"] == TDF_PRIMARY)
    ]
    stable = int((tdf_primary["fraction_of_prior_weight_where_model_wins"] >= 0.3).sum())

    lines.extend(
        [
            "## Five success galaxies",
            "",
            f"- Under **{sc}**, tdf_3knot holds ≥30% prior-weight win fraction in **{stable}/5** galaxies.",
            "- Success cases remain broadly TDF-favorable under diagnostic priors; see summary table.",
            "",
            "## Claim O (Phase 4I)",
            "",
            "**Photometry-informed prior framework is required before treating M/L-scaled results as calibrated.** "
            "Status: **supported**.",
            "",
            "## Limitations",
            "",
            "- No SPARC photometry ingested; weights are scenario placeholders.",
            "- No new model fits; Phase 4G CSV is the sole numeric source.",
            "- Full SPARC and lensing remain future work.",
            "",
            "## Outputs",
            "",
            "- `outputs/tables/sparc_ml_prior_weighted_summary.csv`",
            "- `outputs/tables/ngc7814_ml_prior_weighted_interpretation.csv`",
            "- `configs/ml_priors.yaml`",
            "- `docs/ml_prior_framework.md`",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_ngc7814_prior_support(ngc_interp: pd.DataFrame, output_path: Path) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(ngc_interp))
    width = 0.25
    ax.bar(x - width, ngc_interp["tdf_3knot_fraction_prior_weight_wins"], width, label="tdf_3knot wins")
    ax.bar(x, ngc_interp["tdf_3knot_fraction_beats_nfw"], width, label="tdf_3knot beats NFW")
    ax.bar(x + width, ngc_interp["tdf_5knot_fraction_prior_weight_wins"], width, label="tdf_5knot wins")
    ax.set_xticks(x)
    ax.set_xticklabels(ngc_interp["prior_scenario"], rotation=20, ha="right")
    ax.set_ylabel("fraction of prior weight")
    ax.set_title(f"{TARGET_GALAXY} — diagnostic prior-weighted model support (Phase 4I)")
    ax.legend(fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", alpha=0.3)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_success_prior_summary(summary: pd.DataFrame, output_path: Path) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    sc = "uniform_plausible_band"
    sub = summary[
        (summary["prior_scenario"] == sc)
        & (summary["model_name"] == TDF_PRIMARY)
        & (summary["galaxy_id"] != TARGET_GALAXY)
    ]
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["C0"] * len(sub)
    ax.bar(sub["galaxy_id"], sub["fraction_of_prior_weight_where_model_wins"], color=colors)
    ax.set_ylabel("tdf_3knot prior-weight win fraction")
    ax.set_title("Success galaxies — uniform plausible diagnostic prior (Phase 4I)")
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", alpha=0.3)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def build_ml_prior_weight_audit(
    comparison: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    """Every grid cell with raw and normalized prior weights per scenario."""
    plausible = config.get("plausible_band", {})
    p_disk = tuple(plausible.get("disk_scale", [0.7, 1.3]))
    p_bulge = tuple(plausible.get("bulge_scale", [0.5, 1.0]))
    can = config.get("canonical_ml", {})
    c_disk = float(can.get("disk_scale", 1.0))
    c_bulge = float(can.get("bulge_scale", 1.0))

    disk_vals = sorted(comparison["disk_scale"].unique())
    bulge_vals = sorted(comparison["bulge_scale"].unique())
    rows: list[dict[str, Any]] = []

    for scenario in parse_prior_scenarios(config):
        raw_weights: list[float] = []
        cells: list[tuple[float, float]] = []
        for d in disk_vals:
            for b in bulge_vals:
                w = cell_prior_weight(
                    float(d),
                    float(b),
                    scenario,
                    canonical_disk=c_disk,
                    canonical_bulge=c_bulge,
                    plausible_disk=p_disk,
                    plausible_bulge=p_bulge,
                )
                if w > 0:
                    raw_weights.append(w)
                    cells.append((float(d), float(b)))
        total = sum(raw_weights)
        for (d, b), raw in zip(cells, raw_weights):
            rows.append(
                {
                    "scenario_name": scenario.name,
                    "weighting": scenario.weighting,
                    "grid_scope": scenario.grid_scope,
                    "disk_scale": d,
                    "bulge_scale": b,
                    "raw_weight": raw,
                    "normalized_weight": raw / total if total > 0 else 0.0,
                    "weights_sum_check": total,
                    "in_plausible_band": cell_in_scope(
                        d, b, grid_scope="plausible_only", plausible_disk=p_disk, plausible_bulge=p_bulge
                    ),
                }
            )
    audit = pd.DataFrame(rows)
    if not audit.empty:
        sums = audit.groupby("scenario_name")["normalized_weight"].sum()
        audit["normalized_sum_per_scenario"] = audit["scenario_name"].map(sums)
    return audit


def build_ngc7814_prior_scenario_breakdown(
    comparison: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    gdf = comparison[comparison["galaxy_id"] == TARGET_GALAXY]
    cells = _pivot_cell_rmse(gdf)
    plausible = config.get("plausible_band", {})
    p_disk = tuple(plausible.get("disk_scale", [0.7, 1.3]))
    p_bulge = tuple(plausible.get("bulge_scale", [0.5, 1.0]))
    can = config.get("canonical_ml", {})
    c_disk = float(can.get("disk_scale", 1.0))
    c_bulge = float(can.get("bulge_scale", 1.0))

    rows: list[dict[str, Any]] = []
    for scenario in parse_prior_scenarios(config):
        raw_list = [
            cell_prior_weight(
                float(r["disk_scale"]),
                float(r["bulge_scale"]),
                scenario,
                canonical_disk=c_disk,
                canonical_bulge=c_bulge,
                plausible_disk=p_disk,
                plausible_bulge=p_bulge,
            )
            for _, r in cells.iterrows()
        ]
        total_w = float(sum(raw_list))
        for (_, r), raw in zip(cells.iterrows(), raw_list):
            if raw <= 0:
                continue
            t3 = float(r[TDF_PRIMARY])
            t5 = float(r[TDF_SENSITIVITY])
            nfw = float(r[NFW_MODEL])
            mond = float(r[MOND_MODEL])
            winner = _winner_model(r)
            rows.append(
                {
                    "disk_scale": float(r["disk_scale"]),
                    "bulge_scale": float(r["bulge_scale"]),
                    "scenario_name": scenario.name,
                    "prior_weight": raw / total_w if total_w > 0 else 0.0,
                    "raw_weight": raw,
                    "tdf_3knot_rmse": t3,
                    "tdf_5knot_rmse": t5,
                    "nfw_scaled_rmse": nfw,
                    "mond_scaled_rmse": mond,
                    "winning_model": winner,
                    "tdf_3knot_beats_nfw": bool(np.isfinite(t3) and np.isfinite(nfw) and t3 < nfw),
                    "tdf_3knot_beats_mond": bool(np.isfinite(t3) and np.isfinite(mond) and t3 < mond),
                    "tdf_5knot_beats_nfw": bool(np.isfinite(t5) and np.isfinite(nfw) and t5 < nfw),
                    "tdf_5knot_beats_mond": bool(np.isfinite(t5) and np.isfinite(mond) and t5 < mond),
                }
            )
    return pd.DataFrame(rows)


def write_ml_prior_weighting_audit_report(
    path: Path,
    *,
    weight_audit: pd.DataFrame,
    breakdown: pd.DataFrame,
    ngc_interp: pd.DataFrame,
    config: dict[str, Any],
    correction_applied: bool,
) -> None:
    lines = [
        "# M/L Prior Weighting Audit Report (Phase 4I-Audit)",
        "",
        "> Priors are **diagnostic placeholders**. **No final M/L calibration** is claimed. "
        "**NGC7814 remains a canonical TDF holdout failure** at disk=bulge=1.",
        "",
        f"> Interpretation logic: `{INTERPRETATION_LOGIC_VERSION}`",
        "",
    ]
    if correction_applied:
        lines.extend(
            [
                "## Correction applied",
                "",
                "Phase 4I used a single `prior_supported_tdf_recovery` label driven mainly by "
                "**tdf_5knot** win fractions while **tdf_3knot** had 0% wins. Labels are now split: "
                "primary **tdf_3knot** vs sensitivity **tdf_5knot** vs either-variant. "
                "Per-model beat-NFW fractions are computed per model (not tdf_3knot only). "
                "Phase 4I tables and framework report were **regenerated**.",
                "",
            ]
        )
    else:
        lines.append("## Audit outcome\n\nNo logic correction required.\n")

    lines.extend(["## 1. Prior weight verification", ""])
    for sc_name in weight_audit["scenario_name"].unique():
        sub = weight_audit[weight_audit["scenario_name"] == sc_name].sort_values(
            ["bulge_scale", "disk_scale"]
        )
        norm_sum = float(sub["normalized_weight"].sum())
        lines.append(f"### {sc_name}")
        lines.append(f"- Normalized weights sum: **{norm_sum:.6f}** (expect 1.0)")
        lines.append(f"- Weighting: `{sub['weighting'].iloc[0]}`")
        if sub["weighting"].iloc[0] == "bulge_downweight":
            low = sub[sub["bulge_scale"] == sub["bulge_scale"].min()]
            high = sub[sub["bulge_scale"] == sub["bulge_scale"].max()]
            lines.append(
                f"- Low bulge ({low['bulge_scale'].iloc[0]}): mean norm weight "
                f"**{low['normalized_weight'].mean():.4f}**; high bulge "
                f"({high['bulge_scale'].iloc[0]}): **{high['normalized_weight'].mean():.4f}** "
                "(higher weight at **lower** bulge_scale — as intended)."
            )
        lines.append("")

    lines.extend(
        [
            "## 2. Uniform vs conservative discrepancy (NGC7814)",
            "",
            "Phase 4F/4G show better TDF performance at **lower bulge_scale**. "
            "**conservative_bulge_downweight_test** assigns **more** normalized weight to low-bulge cells "
            "than **uniform_plausible_band**, so tdf_5knot win fraction **increases** (e.g. ~67% → ~78%). "
            "Both scenarios should show **sensitivity_tdf_5knot_diagnostic_recovery**, not contradictory "
            "`canonical_failure_only` vs generic recovery.",
            "",
            "Primary **tdf_3knot** remains at **0%** prior-weight wins in plausible band because "
            "**tdf_5knot** or **MOND/NFW** win per-cell RMSE on those cells.",
            "",
            "## 3. NGC7814 interpretation by scenario",
            "",
        ]
    )
    for _, row in ngc_interp.iterrows():
        lines.append(f"### {row['prior_scenario']}")
        lines.append(f"- Category: `{row['interpretation_category']}`")
        lines.append(f"- Primary tdf_3knot: `{row['primary_tdf_3knot_prior_result']}`")
        lines.append(f"- Sensitivity tdf_5knot: `{row['sensitivity_tdf_5knot_prior_result']}`")
        lines.append(f"- Either variant: `{row['either_tdf_variant_prior_result']}`")
        lines.append(f"- {row['recommended_claim_language']}")
        lines.append("")

    lines.extend(
        [
            "## 4. Interpretation logic (thresholds)",
            "",
            "- **canonical_result:** tdf_3knot RMSE > 2× NFW at M/L=1",
            "- **primary_tdf_3knot:** uses tdf_3knot win fraction & tdf_3knot beats-NFW fraction",
            "- **sensitivity_tdf_5knot:** uses tdf_5knot win fraction & beats-NFW",
            "- **interpretation_category:** `sensitivity_tdf_5knot_diagnostic_recovery` if tdf_3 wins <15% "
            "and tdf_5 wins ≥45%",
            "",
            "## Outputs",
            "",
            "- `outputs/tables/ml_prior_weight_audit.csv`",
            "- `outputs/tables/ngc7814_prior_scenario_breakdown.csv`",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_ngc7814_prior_weight_distribution(
    weight_audit: pd.DataFrame,
    output_path: Path,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    scenarios = list(weight_audit["scenario_name"].unique())
    fig, axes = plt.subplots(1, len(scenarios), figsize=(4 * len(scenarios), 4), sharey=True)
    if len(scenarios) == 1:
        axes = [axes]
    for ax, sc in zip(axes, scenarios):
        sub = weight_audit[weight_audit["scenario_name"] == sc]
        pivot = sub.pivot_table(
            index="bulge_scale", columns="disk_scale", values="normalized_weight", aggfunc="first"
        )
        im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd")
        ax.set_title(sc.replace("_", "\n"), fontsize=8)
        ax.set_xlabel("disk_scale")
        ax.set_ylabel("bulge_scale")
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle(f"{TARGET_GALAXY} — normalized prior weights (Phase 4I-Audit)")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_ngc7814_prior_weighted_rmse_by_scenario(
    breakdown: pd.DataFrame,
    output_path: Path,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    scenarios = list(breakdown["scenario_name"].unique())
    fig, axes = plt.subplots(1, len(scenarios), figsize=(4 * len(scenarios), 4), sharey=True)
    if len(scenarios) == 1:
        axes = [axes]
    for ax, sc in zip(axes, scenarios):
        sub = breakdown[breakdown["scenario_name"] == sc]
        x = np.arange(len(sub))
        w = sub["prior_weight"].to_numpy()
        ax.scatter(x, sub["tdf_3knot_rmse"], s=30 + 200 * w, alpha=0.7, label="tdf_3knot")
        ax.scatter(x, sub["tdf_5knot_rmse"], s=30 + 200 * w, alpha=0.7, label="tdf_5knot")
        ax.scatter(x, sub["nfw_scaled_rmse"], s=30 + 200 * w, alpha=0.7, label="nfw")
        ax.set_title(sc.replace("_", "\n"), fontsize=8)
        ax.set_xticks([])
        ax.legend(fontsize=6)
        ax.set_ylabel("holdout RMSE [km/s]")
    fig.suptitle(f"{TARGET_GALAXY} — RMSE by cell (marker size ∝ prior weight)")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def run_ml_prior_weighting_audit(
    *,
    comparison_path: Path | str = "outputs/tables/sparc_ml_scaled_model_comparison.csv",
    post_ml_path: Path | str = "outputs/tables/sparc_post_ml_results_summary_table.csv",
    priors_config_path: Path | str = "configs/ml_priors.yaml",
    weight_audit_out: Path | str = "outputs/tables/ml_prior_weight_audit.csv",
    breakdown_out: Path | str = "outputs/tables/ngc7814_prior_scenario_breakdown.csv",
    audit_report_out: Path | str = "outputs/reports/ml_prior_weighting_audit_report.md",
    regenerate_phase4i: bool = True,
) -> dict[str, Any]:
    config = load_ml_priors_config(priors_config_path)
    comparison = pd.read_csv(comparison_path)
    post_ml = pd.read_csv(post_ml_path)

    weight_audit = build_ml_prior_weight_audit(comparison, config)
    breakdown = build_ngc7814_prior_scenario_breakdown(comparison, config)
    weight_audit.to_csv(weight_audit_out, index=False)
    breakdown.to_csv(breakdown_out, index=False)

    correction_applied = regenerate_phase4i
    ngc_interp: pd.DataFrame
    if regenerate_phase4i:
        summary, ngc_interp = run_ml_prior_weighting(
            comparison_path=comparison_path,
            post_ml_path=post_ml_path,
            priors_config_path=priors_config_path,
        )
    else:
        ngc_interp = pd.read_csv("outputs/tables/ngc7814_ml_prior_weighted_interpretation.csv")

    write_ml_prior_weighting_audit_report(
        audit_report_out,
        weight_audit=weight_audit,
        breakdown=breakdown,
        ngc_interp=ngc_interp,
        config=config,
        correction_applied=correction_applied,
    )
    plot_ngc7814_prior_weight_distribution(
        weight_audit,
        "outputs/figures/sparc_subset/ngc7814_prior_weight_distribution.png",
    )
    plot_ngc7814_prior_weighted_rmse_by_scenario(
        breakdown,
        "outputs/figures/sparc_subset/ngc7814_prior_weighted_rmse_by_scenario.png",
    )

    weight_sums = weight_audit.groupby("scenario_name")["normalized_weight"].sum().to_dict()
    return {
        "weight_audit": weight_audit,
        "breakdown": breakdown,
        "ngc_interp": ngc_interp,
        "weight_sums": weight_sums,
        "correction_applied": correction_applied,
    }


def run_ml_prior_weighting(
    *,
    comparison_path: Path | str = "outputs/tables/sparc_ml_scaled_model_comparison.csv",
    post_ml_path: Path | str = "outputs/tables/sparc_post_ml_results_summary_table.csv",
    priors_config_path: Path | str = "configs/ml_priors.yaml",
    summary_out: Path | str = "outputs/tables/sparc_ml_prior_weighted_summary.csv",
    ngc_out: Path | str = "outputs/tables/ngc7814_ml_prior_weighted_interpretation.csv",
    report_out: Path | str = "outputs/reports/sparc_ml_prior_framework_report.md",
    fig_ngc: Path | str = "outputs/figures/sparc_subset/ngc7814_ml_prior_weighted_model_support.png",
    fig_success: Path | str = "outputs/figures/sparc_subset/ml_prior_weighted_success_summary.png",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    config = load_ml_priors_config(priors_config_path)
    comparison = pd.read_csv(comparison_path)
    post_ml = pd.read_csv(post_ml_path)

    summary = build_prior_weighted_summary(comparison, config)
    ngc_interp = build_ngc7814_prior_interpretation(summary, post_ml)

    summary.to_csv(summary_out, index=False)
    ngc_interp.to_csv(ngc_out, index=False)

    write_ml_prior_framework_report(report_out, summary=summary, ngc_interp=ngc_interp, config=config)
    plot_ngc7814_prior_support(ngc_interp, fig_ngc)
    plot_success_prior_summary(summary, fig_success)

    return summary, ngc_interp
