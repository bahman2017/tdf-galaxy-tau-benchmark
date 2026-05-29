from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Phase 4A mandated classifications from Phase 3C audit
MANDATED_GALAXY_CLASSIFICATION: dict[str, str] = {
    "DDO154": "robust_tdf_success",
    "IC2574": "robust_tdf_success",
    "NGC2403": "robust_tdf_success",
    "NGC3198": "robust_tdf_success",
    "NGC6503": "robust_tdf_success",
    "NGC7814": "tdf_failure_mode",
}

HOLDOUT_SPLIT_PRIMARY = "even_odd_index"


def _ktau_sensitivity_status(ktau_df: pd.DataFrame, galaxy_id: str, *, rtol: float = 0.15) -> str:
    sub = ktau_df[ktau_df["galaxy_id"] == galaxy_id]
    if sub.empty:
        return "not_available"
    rmse = sub["rmse_kms"].astype(float).to_numpy()
    if len(rmse) < 2:
        return "insufficient_data"
    span = float(np.max(rmse) - np.min(rmse))
    med = float(np.median(rmse))
    if med <= 0:
        return "unstable"
    if span / med <= rtol:
        return "stable"
    return "moderate_variation"


def _bounds_sensitivity_status(bounds_df: pd.DataFrame, galaxy_id: str, *, rtol: float = 0.15) -> str:
    sub = bounds_df[bounds_df["galaxy_id"] == galaxy_id]
    if sub.empty:
        return "not_available"
    rmse = sub["rmse_kms"].astype(float).to_numpy()
    if len(rmse) < 2:
        return "insufficient_data"
    span = float(np.max(rmse) - np.min(rmse))
    med = float(np.median(rmse))
    if med <= 0:
        return "unstable"
    if span / med <= rtol:
        return "stable"
    return "moderate_variation"


def _negative_v2_summary(tdf_comparison: pd.DataFrame, galaxy_id: str) -> str:
    sub = tdf_comparison[tdf_comparison["galaxy_id"] == galaxy_id]
    flags = [
        f"{row['model_name']}"
        for _, row in sub.iterrows()
        if "negative_v2" in str(row.get("fit_status", ""))
    ]
    return ";".join(flags) if flags else "none"


def _smoothness_summary(smooth_df: pd.DataFrame, galaxy_id: str) -> str:
    sub = smooth_df[smooth_df["galaxy_id"] == galaxy_id]
    if sub.empty:
        return "not_available"
    parts = [
        f"{row['model_name']}:norm={float(row['smoothness_normalized']):.4g}"
        for _, row in sub.sort_values("model_name").iterrows()
    ]
    return "; ".join(parts)


def _holdout_even_odd(holdout_df: pd.DataFrame) -> pd.DataFrame:
    return holdout_df[holdout_df["split_name"] == HOLDOUT_SPLIT_PRIMARY].copy()


def _best_holdout_model(ho: pd.DataFrame, galaxy_id: str) -> str:
    sub = ho[ho["galaxy_id"] == galaxy_id]
    if sub.empty:
        return "unknown"
    return str(sub.loc[sub["test_rmse_kms"].idxmin(), "model_name"])


def _holdout_rmse(ho: pd.DataFrame, galaxy_id: str, model_name: str) -> float:
    sub = ho[(ho["galaxy_id"] == galaxy_id) & (ho["model_name"] == model_name)]
    if sub.empty:
        return float("nan")
    return float(sub.iloc[0]["test_rmse_kms"])


def _recommended_interpretation(classification: str, galaxy_id: str) -> str:
    if classification == "robust_tdf_success":
        return (
            "TDF knot models are competitive with or better than tested baselines on this galaxy "
            "under both in-sample metrics and even/odd holdout test RMSE (conditional on fixed baryons and K_tau)."
        )
    if classification == "tdf_failure_mode":
        return (
            f"{galaxy_id}: in-sample TDF fits are strong but holdout validation fails; "
            "NFW/MOND outperform TDF on test RMSE. Treat as an honest failure mode, not a success case."
        )
    if classification == "tdf_in_sample_success_only":
        return "In-sample TDF metrics favor TDF, but holdout performance does not support predictive claims."
    return "Mixed or inconclusive; report with explicit caveats and avoid strong generalizations."


def build_failure_mode_summary(
    *,
    full_comparison: pd.DataFrame,
    best_model: pd.DataFrame,
    robust_best: pd.DataFrame,
    holdout: pd.DataFrame,
    ktau: pd.DataFrame,
    bounds: pd.DataFrame,
    smooth: pd.DataFrame,
    tdf_comparison: pd.DataFrame,
    subset_selection: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build per-galaxy failure-mode summary table for Phase 4A."""
    if subset_selection is not None and "galaxy_id" in subset_selection.columns:
        if "selected" in subset_selection.columns:
            galaxy_ids = (
                subset_selection[subset_selection["selected"].astype(bool)]["galaxy_id"].astype(str).tolist()
            )
        else:
            galaxy_ids = sorted(MANDATED_GALAXY_CLASSIFICATION.keys())
    else:
        galaxy_ids = sorted(MANDATED_GALAXY_CLASSIFICATION.keys())
    # Phase 4A analysis is restricted to the six-galaxy benchmark subset
    mandated = set(MANDATED_GALAXY_CLASSIFICATION.keys())
    galaxy_ids = [gid for gid in galaxy_ids if gid in mandated]

    ho = _holdout_even_odd(holdout)
    rows: list[dict[str, object]] = []

    for gid in galaxy_ids:
        classification = MANDATED_GALAXY_CLASSIFICATION.get(gid, "mixed_result")
        bm = best_model[best_model["galaxy_id"] == gid]
        rb = robust_best[robust_best["galaxy_id"] == gid]

        in_aic = str(bm.iloc[0]["best_by_aic"]) if not bm.empty else "unknown"
        in_bic = str(bm.iloc[0]["best_by_bic"]) if not bm.empty else "unknown"
        holdout_best = _best_holdout_model(ho, gid)

        tdf3_ho = _holdout_rmse(ho, gid, "tdf_3knot")
        tdf5_ho = _holdout_rmse(ho, gid, "tdf_5knot")
        nfw_ho = _holdout_rmse(ho, gid, "nfw_refit")
        mond_ho = _holdout_rmse(ho, gid, "mond_fit_a0_simple")

        beats_nfw = bool(rb.iloc[0]["tdf_3knot_beats_nfw_holdout_rmse"]) if not rb.empty else False

        rows.append(
            {
                "galaxy_id": gid,
                "failure_mode_classification": classification,
                "in_sample_best_by_aic": in_aic,
                "in_sample_best_by_bic": in_bic,
                "holdout_best_by_test_rmse": holdout_best,
                "tdf_3knot_holdout_rmse_kms": tdf3_ho,
                "tdf_5knot_holdout_rmse_kms": tdf5_ho,
                "nfw_refit_holdout_rmse_kms": nfw_ho,
                "mond_fit_a0_holdout_rmse_kms": mond_ho,
                "tdf_3knot_beats_nfw_holdout": beats_nfw,
                "tdf_3knot_beats_mond_holdout": tdf3_ho < mond_ho if np.isfinite(tdf3_ho) and np.isfinite(mond_ho) else False,
                "negative_v2_flags": _negative_v2_summary(tdf_comparison, gid),
                "smoothness_diagnostic": _smoothness_summary(smooth, gid),
                "ktau_sensitivity_status": _ktau_sensitivity_status(ktau, gid),
                "bounds_sensitivity_status": _bounds_sensitivity_status(bounds, gid),
                "five_knot_overfit_risk": bool(rb.iloc[0]["five_knot_overfit_risk_flag"]) if not rb.empty else False,
                "recommended_interpretation": _recommended_interpretation(classification, gid),
            }
        )

    return pd.DataFrame(rows)


def build_claim_traceability_matrix() -> pd.DataFrame:
    """Static claim traceability matrix for Phase 4A (claims A–H)."""
    rows = [
        {
            "claim_id": "A",
            "claim_text": "TDF direct radial reconstruction can be generated for selected SPARC galaxies.",
            "status": "supported",
            "supporting_tables": "sparc_subset_tau_profiles.csv; outputs/tables/sparc_subset_tau_profiles.csv",
            "supporting_figures": "outputs/figures/sparc_subset/*_tau_*.png",
            "caveats": "Phase 2A diagnostic reconstruction only; not an AIC/BIC fitted model.",
            "allowed_language": "direct radial τ reconstruction generated for selected galaxies",
            "prohibited_language": "universal τ-profile discovered; full-SPARC validation",
        },
        {
            "claim_id": "B",
            "claim_text": "TDF knot models outperform tested baselines in-sample on six selected galaxies.",
            "status": "supported_with_caveat",
            "supporting_tables": "sparc_full_model_comparison.csv; sparc_best_model_summary.csv",
            "supporting_figures": "outputs/figures/sparc_subset/*_full_model_rotation_comparison.png",
            "caveats": "Often tdf_5knot wins in-sample; higher knot count may overfit. Fixed baryons, fixed K_tau, six-galaxy subset.",
            "allowed_language": "competitive; outperforms tested baselines in this controlled subset (in-sample)",
            "prohibited_language": "validated on SPARC; universal discovery",
        },
        {
            "claim_id": "C",
            "claim_text": "TDF knot models outperform NFW/MOND under holdout validation.",
            "status": "partially_supported",
            "supporting_tables": "sparc_tdf_holdout_validation.csv; sparc_tdf_robust_best_model_summary.csv",
            "supporting_figures": "outputs/reports/sparc_tdf_robustness_audit_report.md",
            "caveats": "5 of 6 galaxies on even/odd holdout test RMSE; NGC7814 is a clear failure mode.",
            "allowed_language": "5 of 6 holdout success; partially supported on this subset",
            "prohibited_language": "always outperforms; validated on SPARC",
        },
        {
            "claim_id": "D",
            "claim_text": "TDF works for NGC7814.",
            "status": "not_supported",
            "supporting_tables": "sparc_failure_mode_summary.csv; sparc_tdf_holdout_validation.csv",
            "supporting_figures": "outputs/figures/sparc_subset/NGC7814_full_model_rotation_comparison.png",
            "caveats": "In-sample TDF metrics are strong; holdout fails. NFW/MOND better on test RMSE.",
            "allowed_language": "NGC7814 is an honest failure mode under holdout",
            "prohibited_language": "TDF works for NGC7814; TDF validates this galaxy",
        },
        {
            "claim_id": "E",
            "claim_text": "TDF validates on full SPARC.",
            "status": "not_supported_future_work",
            "supporting_tables": "sparc_subset_selection.csv",
            "supporting_figures": "none",
            "caveats": "Only six galaxies in controlled subset.",
            "allowed_language": "future work; subset-only benchmark",
            "prohibited_language": "TDF is validated on SPARC; SPARC validates TDF",
        },
        {
            "claim_id": "F",
            "claim_text": "TDF disproves dark matter.",
            "status": "prohibited",
            "supporting_tables": "none",
            "supporting_figures": "none",
            "caveats": "Rotation-curve consistency test only; no cosmological claim.",
            "allowed_language": "does not disprove dark matter",
            "prohibited_language": "dark matter is disproven; DM is wrong",
        },
        {
            "claim_id": "G",
            "claim_text": "TDF replaces ΛCDM.",
            "status": "prohibited",
            "supporting_tables": "none",
            "supporting_figures": "none",
            "caveats": "Empirical rotation-curve baselines only.",
            "allowed_language": "does not replace ΛCDM",
            "prohibited_language": "ΛCDM is replaced; replaces standard cosmology",
        },
        {
            "claim_id": "H",
            "claim_text": "TDF lensing predictions are confirmed.",
            "status": "not_tested_future_work",
            "supporting_tables": "none",
            "supporting_figures": "none",
            "caveats": "No lensing module in this repository phase.",
            "allowed_language": "lensing not tested; future work",
            "prohibited_language": "lensing confirmed; lensing validates TDF",
        },
    ]
    return pd.DataFrame(rows)


def write_failure_mode_report(
    path: Path,
    summary: pd.DataFrame,
    *,
    holdout_primary: str = HOLDOUT_SPLIT_PRIMARY,
) -> None:
    """Write markdown failure-mode analysis report."""
    n_success = int((summary["failure_mode_classification"] == "robust_tdf_success").sum())
    n_fail = int((summary["failure_mode_classification"] == "tdf_failure_mode").sum())

    lines = [
        "# SPARC Failure-Mode Analysis Report (Phase 4A)",
        "",
        "This audit evaluates success cases and failure modes for the six-galaxy controlled SPARC TDF benchmark. "
        "It does not validate TDF on full SPARC, does not disprove dark matter, does not replace ΛCDM, "
        "and does not include lensing or independent dynamical evidence.",
        "",
        f"- Galaxies classified as **robust_tdf_success**: **{n_success}**",
        f"- Galaxies classified as **tdf_failure_mode**: **{n_fail}**",
        f"- Primary holdout reference split: `{holdout_primary}`",
        "",
        "## Per-galaxy summary",
        "",
        "| Galaxy | classification | in-sample AIC best | holdout RMSE best | tdf_3knot HO | NFW HO | MOND HO |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for _, row in summary.sort_values("galaxy_id").iterrows():
        lines.append(
            f"| {row['galaxy_id']} | {row['failure_mode_classification']} | "
            f"{row['in_sample_best_by_aic']} | {row['holdout_best_by_test_rmse']} | "
            f"{row['tdf_3knot_holdout_rmse_kms']:.2f} | {row['nfw_refit_holdout_rmse_kms']:.2f} | "
            f"{row['mond_fit_a0_holdout_rmse_kms']:.2f} |"
        )

    ng = summary[summary["galaxy_id"] == "NGC7814"]
    if not ng.empty:
        r = ng.iloc[0]
        lines.extend(
            [
                "",
                "## NGC7814 — dedicated failure-mode investigation",
                "",
                "NGC7814 remains in the benchmark as an **honest failure mode**. It is not removed or hidden.",
                "",
                "### Observations",
                "",
                f"- **In-sample:** best by AIC/BIC is `{r['in_sample_best_by_aic']}` (TDF knot variant).",
                f"- **Holdout ({holdout_primary}):** best test RMSE is `{r['holdout_best_by_test_rmse']}` (not TDF).",
                f"- tdf_3knot holdout RMSE ≈ **{r['tdf_3knot_holdout_rmse_kms']:.1f} km/s** vs NFW ≈ **{r['nfw_refit_holdout_rmse_kms']:.1f}** "
                f"and MOND fit-a0 ≈ **{r['mond_fit_a0_holdout_rmse_kms']:.1f} km/s**.",
                f"- **Negative v² flags:** `{r['negative_v2_flags']}` (tdf_4knot pathological).",
                f"- **Smoothness (diagnostic):** {r['smoothness_diagnostic']}",
                "",
                "### Interpretation",
                "",
                "TDF performs well **in-sample** but **fails holdout** on this galaxy. The tdf_4knot variant shows "
                "negative-v² pathology and very poor RMSE in-sample. NFW and MOND outperform TDF on holdout test RMSE.",
                "",
                "### Possible causes to investigate later (not resolved in Phase 4A)",
                "",
                "- Bulge dominance and fixed SPARC baryonic decomposition (no M/L fitting)",
                "- Radial structure / limited azimuthal information in 1D curves",
                "- Fixed knot placement rules vs galaxy morphology",
                "- Fixed K_tau convention (partial degeneracy with dτ/dr amplitude)",
                "- Geometry / inclination not fitted",
                "- Insufficient regularization for higher knot counts",
                "",
                "### Reporting guidance",
                "",
                "Do **not** claim that TDF works for NGC7814 under holdout validation. "
                "Report it as **one clear failure mode** among six subset galaxies.",
            ]
        )

    lines.extend(
        [
            "",
            "## Success cases (robust_tdf_success)",
            "",
        ]
    )
    for _, row in summary[summary["failure_mode_classification"] == "robust_tdf_success"].iterrows():
        lines.append(f"- **{row['galaxy_id']}**: {row['recommended_interpretation']}")

    lines.extend(
        [
            "",
            "## Outputs",
            "- `outputs/tables/sparc_failure_mode_summary.csv`",
            "- `outputs/reports/sparc_failure_mode_analysis_report.md`",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_claim_traceability_report(path: Path, matrix: pd.DataFrame) -> None:
    lines = [
        "# SPARC Claim Traceability Report (Phase 4A)",
        "",
        "This matrix maps scientific claims to evidence tables and conservative language boundaries. "
        "Dark matter is **not** disproven. Full-SPARC validation and lensing are **future work**.",
        "",
        "| ID | Status | Claim |",
        "| --- | --- | --- |",
    ]
    for _, row in matrix.iterrows():
        text = str(row["claim_text"])[:80] + ("…" if len(str(row["claim_text"])) > 80 else "")
        lines.append(f"| {row['claim_id']} | {row['status']} | {text} |")

    lines.extend(["", "## Claim details", ""])
    for _, row in matrix.iterrows():
        lines.extend(
            [
                f"### Claim {row['claim_id']}",
                "",
                f"**Claim:** {row['claim_text']}",
                "",
                f"- **Status:** `{row['status']}`",
                f"- **Supporting tables:** {row['supporting_tables']}",
                f"- **Supporting figures:** {row['supporting_figures']}",
                f"- **Caveats:** {row['caveats']}",
                f"- **Allowed language:** {row['allowed_language']}",
                f"- **Prohibited language:** {row['prohibited_language']}",
                "",
            ]
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
