from __future__ import annotations

from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION

GALAXY_ORDER = tuple(MANDATED_GALAXY_CLASSIFICATION.keys())
TARGET_GALAXY = "NGC7814"

POST_ML_CLAIMS: list[dict[str, str]] = [
    {
        "claim_id": "I",
        "claim_text": "NGC7814 is a canonical TDF holdout failure under fixed SPARC baryons.",
        "status": "supported",
        "supporting_tables": "sparc_publication_summary_table.csv; sparc_ml_sensitivity_holdout_comparison.csv",
        "supporting_figures": "outputs/figures/sparc_subset/NGC7814_full_model_rotation_comparison.png",
        "caveats": "Even/odd holdout at M/L=1; tdf_3knot RMSE ~156 km/s vs NFW ~25 km/s.",
        "allowed_language": "canonical failure; explicit holdout failure mode under fixed baryons",
        "prohibited_language": "NGC7814 is solved; failure removed",
    },
    {
        "claim_id": "J",
        "claim_text": "NGC7814 failure is sensitive to bulge/disk M/L scaling.",
        "status": "supported_diagnostic_sensitivity",
        "supporting_tables": "sparc_ml_sensitivity_summary.csv; ngc7814_ml_sensitivity_detail.csv",
        "supporting_figures": "outputs/figures/sparc_subset/ngc7814_ml_sensitivity_inner_residuals.png",
        "caveats": "Diagnostic grid only; not photometric M/L calibration.",
        "allowed_language": "baryonic-decomposition-sensitive failure; diagnostic M/L scaling",
        "prohibited_language": "M/L calibration confirms TDF; definitively fixes NGC7814",
    },
    {
        "claim_id": "K",
        "claim_text": "M/L scaling definitively fixes NGC7814.",
        "status": "not_supported",
        "supporting_tables": "ngc7814_ml_scaled_fair_comparison.csv",
        "supporting_figures": "none",
        "caveats": "Fair scaled NFW/MOND also improve; canonical label unchanged at M/L=1.",
        "allowed_language": "recoverable under some plausible lower-bulge settings (diagnostic)",
        "prohibited_language": "NGC7814 is solved; M/L scaling fixes the failure",
    },
    {
        "claim_id": "L",
        "claim_text": "TDF uniquely benefits from M/L scaling.",
        "status": "not_supported",
        "supporting_tables": "sparc_ml_scaled_model_comparison.csv; ngc7814_ml_scaled_fair_comparison.csv",
        "supporting_figures": "outputs/figures/sparc_subset/ngc7814_ml_scaled_fair_comparison.png",
        "caveats": "Phase 4G fair comparison: NFW and MOND refit on same scaled baryons.",
        "allowed_language": "TDF improvement is not unique; baselines improve too",
        "prohibited_language": "TDF uniquely benefits; NFW/MOND fail after scaling",
    },
    {
        "claim_id": "M",
        "claim_text": "TDF remains stable across the five original success galaxies under plausible M/L scaling.",
        "status": "supported_with_caveat",
        "supporting_tables": "sparc_ml_scaled_best_model_summary.csv; sparc_post_ml_results_summary_table.csv",
        "supporting_figures": "outputs/figures/sparc_subset/ml_scaled_success_stability.png",
        "caveats": "Plausible band disk [0.7,1.3], bulge [0.5,1.0]; tdf_5knot often best at scaled scales.",
        "allowed_language": "TDF remains stable in the five success galaxies (plausible diagnostic scaling)",
        "prohibited_language": "universal stability; photometry-calibrated M/L",
    },
    {
        "claim_id": "N",
        "claim_text": "The current benchmark has a photometry-calibrated M/L model.",
        "status": "not_supported_future_work",
        "supporting_tables": "none",
        "supporting_figures": "none",
        "caveats": "Phase 4F/4G use a diagnostic Cartesian M/L grid only.",
        "allowed_language": "future work: photometry-informed M/L priors",
        "prohibited_language": "M/L calibration confirms TDF; final M/L model",
    },
]

PROHIBITED_PHRASES = (
    "NGC7814 is solved",
    "TDF is validated",
    "dark matter is disproven",
    "ΛCDM is replaced",
    "M/L calibration confirms TDF",
    "NFW/MOND fail after scaling",
    "lensing is confirmed",
)


def _interpret_galaxy_row(
    gid: str,
    classification: str,
    *,
    canonical_best: str,
    scaled_best: str,
    nfw_wins_plausible: bool,
    tdf_stable: bool,
) -> tuple[str, str]:
    if classification == "robust_tdf_success":
        interp = (
            "Canonical holdout success retained. TDF remains competitive under plausible "
            "diagnostic M/L scaling (fair scaled comparison)."
        )
        status = "canonical_success_retained"
        if not tdf_stable:
            status = "supported_with_caveat"
            interp += " Some grid cells show elevated RMSE; see scaled comparison tables."
        return interp, status

    if gid == TARGET_GALAXY:
        interp = (
            "Canonical holdout failure retained under fixed SPARC baryons. "
            "Baryonic-decomposition-sensitive failure: lowering bulge_scale reduces inner TDF error. "
            "Under fair scaled comparison, NFW and MOND also improve; TDF can be competitive at "
            "some plausible lower-bulge settings (especially tdf_5knot), but this is not a final M/L calibration."
        )
        status = "canonical_failure_retained; ml_sensitivity_diagnostic"
        if nfw_wins_plausible:
            interp += " NFW or MOND wins at some plausible-scale cells."
        return interp, status

    return "See scaled comparison tables.", "unknown"


def build_post_ml_results_summary_table(
    publication: pd.DataFrame,
    ml_holdout: pd.DataFrame,
    scaled_best: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for gid in GALAXY_ORDER:
        pub = publication[publication["galaxy_id"] == gid]
        if pub.empty:
            continue
        pub_row = pub.iloc[0]
        scaled_row = scaled_best[scaled_best["galaxy_id"] == gid].iloc[0]
        classification = str(pub_row.get("classification", MANDATED_GALAXY_CLASSIFICATION.get(gid, "")))
        interp, claim_status = _interpret_galaxy_row(
            gid,
            classification,
            canonical_best=str(pub_row.get("holdout_best_model", "")),
            scaled_best=str(scaled_row.get("best_model_best_plausible_scale", "")),
            nfw_wins_plausible=bool(scaled_row.get("nfw_or_mond_wins_any_plausible_scale", False)),
            tdf_stable=bool(scaled_row.get("tdf_success_stable_under_plausible_scaling", False)),
        )
        caveat = (
            "Canonical metrics at M/L=1. Scaled metrics from Phase 4G fair comparison (diagnostic grid). "
            "Primary conservative TDF model: tdf_3knot."
        )
        rows.append(
            {
                "galaxy_id": gid,
                "canonical_classification": classification,
                "canonical_holdout_best_model": pub_row.get("holdout_best_model"),
                "canonical_tdf_3knot_rmse": round(float(pub_row["tdf_3knot_holdout_rmse_kms"]), 2),
                "canonical_tdf_5knot_rmse": round(float(pub_row["tdf_5knot_holdout_rmse_kms"]), 2),
                "canonical_nfw_rmse": round(float(pub_row["nfw_refit_holdout_rmse_kms"]), 2),
                "canonical_mond_rmse": round(float(pub_row["mond_fit_a0_holdout_rmse_kms"]), 2),
                "best_plausible_scaled_model": scaled_row.get("best_model_best_plausible_scale"),
                "best_plausible_disk_scale": scaled_row.get("best_plausible_disk_scale"),
                "best_plausible_bulge_scale": scaled_row.get("best_plausible_bulge_scale"),
                "post_ml_interpretation": interp,
                "claim_status": claim_status,
                "caveat": caveat,
            }
        )
    return pd.DataFrame(rows)


def build_updated_claim_matrix(base_matrix_path: Path | str) -> pd.DataFrame:
    base = pd.read_csv(base_matrix_path)
    post = pd.DataFrame(POST_ML_CLAIMS)
    for col in base.columns:
        if col not in post.columns:
            post[col] = ""
    combined = pd.concat([base, post[base.columns]], ignore_index=True)
    return combined


def write_claim_reconciliation_report(
    path: Path,
    *,
    post_ml_table: pd.DataFrame,
    updated_matrix: pd.DataFrame,
) -> None:
    ngc = post_ml_table[post_ml_table["galaxy_id"] == TARGET_GALAXY].iloc[0]
    success = post_ml_table[post_ml_table["galaxy_id"] != TARGET_GALAXY]
    stable_count = int(
        success["claim_status"].str.contains("canonical_success_retained", na=False).sum()
    )

    lines = [
        "# SPARC Post-M/L Claim Reconciliation Report (Phase 4H)",
        "",
        "> This reconciliation updates claim language after diagnostic M/L sensitivity tests. "
        "It does not introduce a final M/L calibration, does not validate TDF on full SPARC, "
        "does not disprove dark matter, and does not include lensing.",
        "",
        "## Objective",
        "",
        "Reconcile publication-ready claims and controlled-subset narrative after Phase 4F (TDF M/L sensitivity) "
        "and Phase 4G (fair scaled TDF/NFW/MOND comparison) **without new fits**.",
        "",
        "## What Phase 4F showed",
        "",
        "- NGC7814 canonical TDF holdout failure (~156 km/s tdf_3knot at M/L=1) is **strongly sensitive** "
        "to diagnostic disk/bulge scaling.",
        "- Lowering `bulge_scale` reduces inner negative residuals and TDF holdout RMSE dramatically.",
        "- Phase 4F compared TDF at scaled baryons to **canonical** (unscaled) NFW/MOND only.",
        "",
        "## What Phase 4G changed",
        "",
        "- NFW and MOND were refit on the **same** scaled baryons as TDF at each grid point.",
        "- At canonical (1,1), scaled NFW/MOND still dominate NGC7814 (~25–28 vs ~156 km/s).",
        "- At plausible lower-bulge settings, **all** models improve; MOND/NFW often remain competitive with TDF.",
        "- Five success galaxies remain stable under plausible diagnostic scaling.",
        "",
        "## Updated interpretation of NGC7814",
        "",
        f"- **Canonical:** {ngc['post_ml_interpretation']}",
        f"- Holdout RMSE at M/L=1: tdf_3knot={ngc['canonical_tdf_3knot_rmse']}, "
        f"nfw={ngc['canonical_nfw_rmse']}, mond={ngc['canonical_mond_rmse']} km/s.",
        f"- Best plausible scaled model (Phase 4G): {ngc['best_plausible_scaled_model']} "
        f"(disk={ngc['best_plausible_disk_scale']}, bulge={ngc['best_plausible_bulge_scale']}).",
        "- NGC7814 is **not removed** from the benchmark.",
        "",
        "## Updated interpretation of the five success galaxies",
        "",
        f"- **{stable_count} of 5** retain canonical holdout-success interpretation with "
        "`tdf_success_stable_under_plausible_scaling=True` in Phase 4G.",
        "- Primary conservative model remains **tdf_3knot**; **tdf_5knot** often best at scaled scales.",
        "",
        "## Updated supported claims (I–N)",
        "",
    ]
    for _, row in updated_matrix[updated_matrix["claim_id"].isin(["I", "J", "K", "L", "M", "N"])].iterrows():
        lines.append(f"- **{row['claim_id']}:** {row['claim_text']} — `{row['status']}`")

    lines.extend(
        [
            "",
            "## Allowed language (post-M/L)",
            "",
            "- canonical failure",
            "- baryonic-decomposition-sensitive failure",
            "- diagnostic M/L scaling",
            "- fair scaled comparison",
            "- TDF remains stable in the five success galaxies",
            "- NGC7814 is recoverable under some plausible lower-bulge settings, but the result is not a final M/L calibration",
            "",
            "## Prohibited language (post-M/L)",
            "",
        ]
    )
    for phrase in PROHIBITED_PHRASES:
        lines.append(f"- \"{phrase}\"")

    lines.extend(
        [
            "",
            "## Next recommended work",
            "",
            "1. Photometry-informed M/L priors (not Cartesian grid).",
            "2. K_tau sensitivity with fair scaled baselines.",
            "3. Full SPARC and lensing only after frozen τ-map validation and updated claim matrix.",
            "",
            "## Outputs",
            "",
            "- `outputs/tables/sparc_claim_traceability_matrix_updated.csv`",
            "- `outputs/tables/sparc_post_ml_results_summary_table.csv`",
            "- `docs/paper_ready_claims.md`, `docs/results_summary.md`",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_controlled_subset_results_summary(
    path: Path,
    *,
    post_ml_table: pd.DataFrame,
) -> None:
    ngc = post_ml_table[post_ml_table["galaxy_id"] == TARGET_GALAXY].iloc[0]
    lines = [
        "# Controlled Six-Galaxy Results Summary (Post-M/L, Phase 4H)",
        "",
        "> Diagnostic M/L sensitivity (4F/4G) updates interpretation only. Canonical holdout results at fixed "
        "SPARC baryons are unchanged.",
        "",
        "## Headline",
        "",
        "On a **controlled six-galaxy subset**, TDF achieves **5 of 6 holdout success** under **fixed canonical "
        "SPARC baryons** and even/odd holdout. **NGC7814** remains an explicit **canonical failure** that is "
        "**baryonic-decomposition-sensitive** under diagnostic M/L scaling.",
        "",
        "## Canonical holdout (M/L = 1)",
        "",
        "| Galaxy | Classification | Best holdout | tdf_3knot | NFW |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for _, row in post_ml_table.iterrows():
        lines.append(
            f"| {row['galaxy_id']} | {row['canonical_classification']} | "
            f"{row['canonical_holdout_best_model']} | {row['canonical_tdf_3knot_rmse']} | "
            f"{row['canonical_nfw_rmse']} |"
        )

    lines.extend(
        [
            "",
            "## Post-M/L diagnostic interpretation",
            "",
            f"**NGC7814:** {ngc['post_ml_interpretation']}",
            "",
            "**Five success galaxies:** TDF holdout success is **stable** under plausible diagnostic M/L scaling "
            "(Phase 4G); no galaxy flips to NFW/MOND as best model across all plausible cells.",
            "",
            "## Model recommendation",
            "",
            "- **Primary:** `tdf_3knot` (conservative).",
            "- **Sensitivity:** `tdf_5knot` (higher flexibility; often best scaled RMSE).",
            "",
            "## Claim boundary",
            "",
            "See `outputs/tables/sparc_claim_traceability_matrix_updated.csv` and `docs/paper_ready_claims.md`.",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_post_ml_claim_reconciliation(
    *,
    publication_path: Path | str = "outputs/tables/sparc_publication_summary_table.csv",
    ml_holdout_path: Path | str = "outputs/tables/sparc_ml_sensitivity_holdout_comparison.csv",
    scaled_best_path: Path | str = "outputs/tables/sparc_ml_scaled_best_model_summary.csv",
    base_matrix_path: Path | str = "outputs/tables/sparc_claim_traceability_matrix.csv",
    updated_matrix_path: Path | str = "outputs/tables/sparc_claim_traceability_matrix_updated.csv",
    post_ml_table_path: Path | str = "outputs/tables/sparc_post_ml_results_summary_table.csv",
    reconciliation_report_path: Path | str = "outputs/reports/sparc_post_ml_claim_reconciliation_report.md",
    subset_summary_path: Path | str = "outputs/reports/sparc_post_ml_controlled_subset_results_summary.md",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    publication = pd.read_csv(publication_path)
    ml_holdout = pd.read_csv(ml_holdout_path)
    scaled_best = pd.read_csv(scaled_best_path)

    post_ml_table = build_post_ml_results_summary_table(publication, ml_holdout, scaled_best)
    updated_matrix = build_updated_claim_matrix(base_matrix_path)

    post_ml_table.to_csv(post_ml_table_path, index=False)
    updated_matrix.to_csv(updated_matrix_path, index=False)

    write_claim_reconciliation_report(
        reconciliation_report_path,
        post_ml_table=post_ml_table,
        updated_matrix=updated_matrix,
    )
    write_controlled_subset_results_summary(
        subset_summary_path,
        post_ml_table=post_ml_table,
    )

    return post_ml_table, updated_matrix
