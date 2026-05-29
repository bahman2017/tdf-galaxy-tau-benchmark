from __future__ import annotations

from pathlib import Path

import pandas as pd

AUDIT_VERSION = "phase_4m_controlled_subset_final"

FINAL_CONTROLLED_SUBSET_CLAIM = (
    "On the controlled six-galaxy SPARC subset, TDF knot models show robust rotation-curve "
    "consistency in five galaxies, while NGC7814 remains a canonical tdf_3knot failure under "
    "fixed baryons. The NGC7814 failure is strongly baryonic-decomposition-sensitive, and "
    "tdf_5knot shows diagnostic recovery under some photometry-informed prior scenarios, but "
    "this is not a final M/L calibration."
)

FINAL_CAVEATS: tuple[str, ...] = (
    "This benchmark does not disprove dark matter.",
    "Results do not replace ΛCDM as a cosmological framework.",
    "Scope is a controlled six-galaxy subset only — not full-SPARC validation.",
    "Lensing is not tested in this repository phase.",
    "No universal τ-profile was discovered.",
    "No final or photometry-calibrated M/L model is claimed.",
    "K_tau is a fixed normalization convention, not a measured physical constant.",
    "tdf_5knot is a sensitivity / higher-flexibility model; tdf_3knot is the primary conservative TDF model.",
)

PHASE_STATUS_ROWS: list[dict[str, str]] = [
    {
        "phase": "1A",
        "main_output": "data/processed/sparc/sparc_rotmod_standardized.csv",
        "status": "complete",
        "supported_claim": "Standardized SPARC rotmod ingestion for downstream analysis",
        "caveat": "Raw rotmod not modified in later phases",
        "next_action": "None for controlled subset; full catalog deferred",
    },
    {
        "phase": "1B",
        "main_output": "outputs/tables/sparc_subset_selection.csv",
        "status": "complete",
        "supported_claim": "Deterministic six-galaxy controlled subset (DDO154, IC2574, NGC2403, NGC3198, NGC6503, NGC7814)",
        "caveat": "Subset selection is not a random SPARC sample",
        "next_action": "Document any future expansion criteria before adding galaxies",
    },
    {
        "phase": "2A",
        "main_output": "outputs/tables/sparc_subset_tau_profiles.csv",
        "status": "complete",
        "supported_claim": "Direct radial τ reconstruction (claim A; diagnostic only)",
        "caveat": "Diagnostic reconstruction, not fitted knot model",
        "next_action": "Optional 2D τ-map deferred",
    },
    {
        "phase": "3A",
        "main_output": "outputs/tables/sparc_baseline_comparison.csv",
        "status": "complete",
        "supported_claim": "Baryonic-only, NFW, Burkert baseline fits on subset",
        "caveat": "Legacy linear bounds superseded by 3A-R for halos",
        "next_action": "Use refit tables for publication numbers",
    },
    {
        "phase": "3A-R",
        "main_output": "outputs/tables/sparc_baseline_comparison_refit.csv",
        "status": "complete",
        "supported_claim": "Log-space multistart NFW/Burkert refit",
        "caveat": "Halo degeneracy may persist",
        "next_action": "Monitor boundary-limited fits in audits",
    },
    {
        "phase": "3M",
        "main_output": "outputs/tables/sparc_mond_comparison.csv",
        "status": "complete",
        "supported_claim": "MOND/RAR empirical rotation-curve baselines",
        "caveat": "MOND is empirical baseline, not cosmology claim",
        "next_action": "None within subset",
    },
    {
        "phase": "3B",
        "main_output": "outputs/tables/sparc_full_model_comparison.csv",
        "status": "complete",
        "supported_claim": "TDF 3/4/5-knot in-sample comparison (claim B with caveat)",
        "caveat": "Often tdf_5knot wins in-sample; tdf_4knot pathological on NGC7814",
        "next_action": "Lead with tdf_3knot for conservative claims",
    },
    {
        "phase": "3C",
        "main_output": "outputs/tables/sparc_tdf_holdout_validation.csv",
        "status": "complete",
        "supported_claim": "5 of 6 holdout success; even/odd split (claim C partial)",
        "caveat": "NGC7814 canonical failure; fixed K_tau",
        "next_action": "Phase 4L K_tau audit documents normalization sensitivity",
    },
    {
        "phase": "4A",
        "main_output": "outputs/tables/sparc_failure_mode_summary.csv",
        "status": "complete",
        "supported_claim": "Per-galaxy failure-mode classification; claim traceability A–H",
        "caveat": "NGC7814 retained as tdf_failure_mode",
        "next_action": "Use updated matrix through claim Q",
    },
    {
        "phase": "4B",
        "main_output": "docs/results_summary.md; sparc_publication_summary_table.csv",
        "status": "complete",
        "supported_claim": "Paper-ready controlled-subset summary and publication table",
        "caveat": "Documentation layer; numbers from 3B/3C",
        "next_action": "Superseded by 4M final audit for external handoff",
    },
    {
        "phase": "4C",
        "main_output": "outputs/tables/sparc_normalized_tau_pattern_summary.csv",
        "status": "complete",
        "supported_claim": "Normalized τ-pattern similarity and outlier scores",
        "caveat": "NGC7814 outlier in pattern space; not universal τ law",
        "next_action": "No universal τ-profile claim",
    },
    {
        "phase": "4D",
        "main_output": "docs/ngc7814_failure_mode.md",
        "status": "complete",
        "supported_claim": "NGC7814 structural/holdout/pattern diagnostics (claim D not supported)",
        "caveat": "Canonical tdf_3knot failure at M/L=1",
        "next_action": "Cross-reference photometry context (4J–4K)",
    },
    {
        "phase": "4E",
        "main_output": "outputs/tables/sparc_holdout_residuals.csv",
        "status": "complete",
        "supported_claim": "Per-point holdout residual localization",
        "caveat": "Inner-region failure on NGC7814 for tdf_3knot",
        "next_action": "Use for failure-map figures only",
    },
    {
        "phase": "4F",
        "main_output": "outputs/tables/sparc_ml_sensitivity_summary.csv",
        "status": "complete",
        "supported_claim": "Diagnostic M/L grid; NGC7814 baryonic sensitivity (claim J)",
        "caveat": "TDF-only scaling in 4F; NFW/MOND not re-scaled",
        "next_action": "Superseded by 4G fair comparison for baselines",
    },
    {
        "phase": "4G",
        "main_output": "outputs/tables/sparc_ml_scaled_model_comparison.csv",
        "status": "complete",
        "supported_claim": "Fair scaled TDF/NFW/MOND holdout on same M/L grid",
        "caveat": "Diagnostic grid; claim L not supported (baselines improve too)",
        "next_action": "Input to prior-weighting phases",
    },
    {
        "phase": "4H",
        "main_output": "outputs/tables/sparc_claim_traceability_matrix_updated.csv",
        "status": "complete",
        "supported_claim": "Post-M/L claim reconciliation (claims I–N)",
        "caveat": "No new fits",
        "next_action": "Extend with O–Q in final claims table",
    },
    {
        "phase": "4I",
        "main_output": "outputs/tables/sparc_ml_prior_weighted_summary.csv",
        "status": "complete",
        "supported_claim": "Diagnostic placeholder prior scaffold (claim O)",
        "caveat": "Not photometry-calibrated",
        "next_action": "Superseded by 4K photometry-informed weights",
    },
    {
        "phase": "4I-Audit",
        "main_output": "outputs/reports/ml_prior_weighting_audit_report.md",
        "status": "complete",
        "supported_claim": "Layered NGC7814 interpretation (tdf_3knot vs tdf_5knot)",
        "caveat": "tdf_5knot can win weighted cells without primary recovery",
        "next_action": "Cite audit when using prior language",
    },
    {
        "phase": "4J",
        "main_output": "data/processed/sparc/sparc_photometry_metadata.csv",
        "status": "complete",
        "supported_claim": "SPARC Table-1 metadata for prior scaffolding (claim P context)",
        "caveat": "No final M/L calibration",
        "next_action": "Ingest explicit bulge L_3.6 when available",
    },
    {
        "phase": "4K",
        "main_output": "outputs/tables/sparc_photometry_informed_prior_weights.csv",
        "status": "complete",
        "supported_claim": "Photometry-informed diagnostic prior weights (claim Q not supported)",
        "caveat": "tdf_5knot diagnostic recovery on NGC7814 under some scenarios",
        "next_action": "Do not claim calibrated M/L",
    },
    {
        "phase": "4L",
        "main_output": "outputs/tables/sparc_ktau_sensitivity_summary.csv",
        "status": "complete",
        "supported_claim": "K_tau sensitivity on 4K harness; qualitative claims stable over {0.5,1,2}",
        "caveat": "K_tau not measured or fitted; partial degeneracy with amplitudes",
        "next_action": "Optional extreme K_tau via --include-optional-ktau",
    },
    {
        "phase": "4M",
        "main_output": "outputs/reports/sparc_controlled_subset_final_audit_report.md",
        "status": "complete",
        "supported_claim": FINAL_CONTROLLED_SUBSET_CLAIM,
        "caveat": "; ".join(FINAL_CAVEATS[:3]) + "; see full caveat list",
        "next_action": "Controlled subset expansion or full SPARC only after frozen claim review",
    },
]


def build_final_status_table() -> pd.DataFrame:
    return pd.DataFrame(PHASE_STATUS_ROWS)


def build_final_claims_table(
    traceability_path: Path | str = "outputs/tables/sparc_claim_traceability_matrix_updated.csv",
) -> pd.DataFrame:
    path = Path(traceability_path)
    if path.is_file():
        base = pd.read_csv(path)
    else:
        base = pd.DataFrame(columns=["claim_id", "claim_text", "status"])

    extra = pd.DataFrame(
        [
            {
                "claim_id": "O",
                "claim_text": "Photometry-informed priors required before calibrated M/L claims.",
                "status": "supported",
                "caveat": "Phase 4I–4K diagnostic scaffold only",
            },
            {
                "claim_id": "P",
                "claim_text": "SPARC photometry metadata supports treating NGC7814 as structurally distinct from five success galaxies.",
                "status": "supported_metadata_context",
                "caveat": "Not causal proof; Phase 4J/4K",
            },
            {
                "claim_id": "Q",
                "claim_text": "Photometry-informed priors constitute final calibrated M/L priors.",
                "status": "not_supported",
                "caveat": "Explicitly rejected in Phase 4K",
            },
            {
                "claim_id": "FINAL",
                "claim_text": FINAL_CONTROLLED_SUBSET_CLAIM,
                "status": "supported_with_caveats",
                "caveat": "Primary model tdf_3knot; NGC7814 canonical failure; no final M/L calibration",
            },
        ]
    )
    if "claim_id" in base.columns:
        existing = set(base["claim_id"].astype(str))
        add = extra[~extra["claim_id"].isin(existing)]
        out = pd.concat([base, add], ignore_index=True)
    else:
        out = extra
    return out


def write_final_audit_report(
    path: Path,
    *,
    status: pd.DataFrame,
    claims: pd.DataFrame,
    post_ml_path: Path | str = "outputs/tables/sparc_post_ml_results_summary_table.csv",
) -> None:
    lines = [
        "# SPARC Controlled Subset — Final Audit Report (Phase 4M)",
        "",
        f"> Audit version: `{AUDIT_VERSION}`. **Documentation and consolidation only** — no new fits, "
        "no new models, no full SPARC, no lensing.",
        "",
        "## Final controlled-subset claim",
        "",
        f"> {FINAL_CONTROLLED_SUBSET_CLAIM}",
        "",
        "## Required caveats",
        "",
    ]
    for c in FINAL_CAVEATS:
        lines.append(f"- {c}")

    lines.extend(
        [
            "",
            "## Executive summary",
            "",
            "Phases **1A–4L** establish a reproducible six-galaxy benchmark: standardized ingestion, "
            "deterministic subset, radial τ diagnostics, halo/MOND/TDF comparisons, even/odd holdout, "
            "failure-mode taxonomy, normalized τ patterns, diagnostic M/L and fair scaled baselines, "
            "photometry-informed prior scaffolds, and K_tau sensitivity. **Five galaxies** show robust "
            "TDF holdout consistency at canonical baryons; **NGC7814** is an explicit **tdf_3knot** "
            "canonical failure with **baryonic-decomposition-sensitive** diagnostic behavior.",
            "",
            "## Phase summary",
            "",
            "| Phase | Main output | Status | Supported claim (short) |",
            "| --- | --- | --- | --- |",
        ]
    )
    for _, r in status.iterrows():
        lines.append(
            f"| {r['phase']} | `{r['main_output']}` | {r['status']} | {r['supported_claim'][:80]}... |"
        )

    lines.extend(["", "## Per-galaxy post-M/L status", ""])
    p = Path(post_ml_path)
    if p.is_file():
        post = pd.read_csv(p)
        lines.append("| Galaxy | Class | Canonical tdf_3knot RMSE | Canonical NFW RMSE | Post-M/L note |")
        lines.append("| --- | --- | --- | --- | --- |")
        for _, r in post.iterrows():
            lines.append(
                f"| {r['galaxy_id']} | {r['canonical_classification']} | "
                f"{r['canonical_tdf_3knot_rmse']:.1f} | {r['canonical_nfw_rmse']:.1f} | "
                f"{str(r['post_ml_interpretation'])[:60]}... |"
            )
    else:
        lines.append("_Post-M/L table not found._")

    lines.extend(
        [
            "",
            "## NGC7814 (consolidated)",
            "",
            "- **Canonical:** `tdf_3knot` holdout failure at fixed SPARC baryons (claim I).",
            "- **M/L:** Strong diagnostic sensitivity; fair scaled NFW/MOND also improve (claims J, L).",
            "- **Photometry:** Structurally distinct from five success galaxies (claim P).",
            "- **Priors:** `tdf_5knot` may show diagnostic weighted support; not primary recovery (4K/4I-Audit).",
            "- **K_tau:** Canonical failure label unchanged across tested K_tau values (4L).",
            "",
            "## Claim inventory",
            "",
            "See `outputs/tables/sparc_controlled_subset_final_claims.csv` and "
            "`docs/paper_ready_claims.md` (claims A–Q).",
            "",
            "## Key supporting artifacts",
            "",
            "- `outputs/tables/sparc_publication_summary_table.csv`",
            "- `outputs/tables/sparc_post_ml_results_summary_table.csv`",
            "- `outputs/tables/sparc_photometry_prior_weighted_summary.csv`",
            "- `outputs/tables/sparc_ktau_sensitivity_summary.csv`",
            "- `outputs/reports/sparc_photometry_informed_prior_report.md`",
            "- `outputs/reports/sparc_ktau_sensitivity_report.md`",
            "",
            "## Recommended next steps (outside this audit)",
            "",
            "1. Controlled subset expansion with pre-registered selection criteria.",
            "2. Explicit bulge L_3.6 or stellar-population priors before calibrated M/L language.",
            "3. Full SPARC and lensing only after frozen τ-map validation and claim review.",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_controlled_subset_final_audit(
    *,
    status_out: Path | str = "outputs/tables/sparc_controlled_subset_final_status.csv",
    claims_out: Path | str = "outputs/tables/sparc_controlled_subset_final_claims.csv",
    report_out: Path | str = "outputs/reports/sparc_controlled_subset_final_audit_report.md",
    traceability_path: Path | str = "outputs/tables/sparc_claim_traceability_matrix_updated.csv",
    post_ml_path: Path | str = "outputs/tables/sparc_post_ml_results_summary_table.csv",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    status = build_final_status_table()
    claims = build_final_claims_table(traceability_path)
    status.to_csv(status_out, index=False)
    claims.to_csv(claims_out, index=False)
    write_final_audit_report(
        report_out,
        status=status,
        claims=claims,
        post_ml_path=post_ml_path,
    )
    return status, claims
