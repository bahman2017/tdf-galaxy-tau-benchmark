# SPARC Controlled Subset — Final Audit Report (Phase 4M)

> Audit version: `phase_4m_controlled_subset_final`. **Documentation and consolidation only** — no new fits, no new models, no full SPARC, no lensing.

## Final controlled-subset claim

> On the controlled six-galaxy SPARC subset, TDF knot models show robust rotation-curve consistency in five galaxies, while NGC7814 remains a canonical tdf_3knot failure under fixed baryons. The NGC7814 failure is strongly baryonic-decomposition-sensitive, and tdf_5knot shows diagnostic recovery under some photometry-informed prior scenarios, but this is not a final M/L calibration.

## Required caveats

- This benchmark does not disprove dark matter.
- Results do not replace ΛCDM as a cosmological framework.
- Scope is a controlled six-galaxy subset only — not full-SPARC validation.
- Lensing is not tested in this repository phase.
- No universal τ-profile was discovered.
- No final or photometry-calibrated M/L model is claimed.
- K_tau is a fixed normalization convention, not a measured physical constant.
- tdf_5knot is a sensitivity / higher-flexibility model; tdf_3knot is the primary conservative TDF model.

## Executive summary

Phases **1A–4L** establish a reproducible six-galaxy benchmark: standardized ingestion, deterministic subset, radial τ diagnostics, halo/MOND/TDF comparisons, even/odd holdout, failure-mode taxonomy, normalized τ patterns, diagnostic M/L and fair scaled baselines, photometry-informed prior scaffolds, and K_tau sensitivity. **Five galaxies** show robust TDF holdout consistency at canonical baryons; **NGC7814** is an explicit **tdf_3knot** canonical failure with **baryonic-decomposition-sensitive** diagnostic behavior.

## Phase summary

| Phase | Main output | Status | Supported claim (short) |
| --- | --- | --- | --- |
| 1A | `data/processed/sparc/sparc_rotmod_standardized.csv` | complete | Standardized SPARC rotmod ingestion for downstream analysis... |
| 1B | `outputs/tables/sparc_subset_selection.csv` | complete | Deterministic six-galaxy controlled subset (DDO154, IC2574, NGC2403, NGC3198, NG... |
| 2A | `outputs/tables/sparc_subset_tau_profiles.csv` | complete | Direct radial τ reconstruction (claim A; diagnostic only)... |
| 3A | `outputs/tables/sparc_baseline_comparison.csv` | complete | Baryonic-only, NFW, Burkert baseline fits on subset... |
| 3A-R | `outputs/tables/sparc_baseline_comparison_refit.csv` | complete | Log-space multistart NFW/Burkert refit... |
| 3M | `outputs/tables/sparc_mond_comparison.csv` | complete | MOND/RAR empirical rotation-curve baselines... |
| 3B | `outputs/tables/sparc_full_model_comparison.csv` | complete | TDF 3/4/5-knot in-sample comparison (claim B with caveat)... |
| 3C | `outputs/tables/sparc_tdf_holdout_validation.csv` | complete | 5 of 6 holdout success; even/odd split (claim C partial)... |
| 4A | `outputs/tables/sparc_failure_mode_summary.csv` | complete | Per-galaxy failure-mode classification; claim traceability A–H... |
| 4B | `docs/results_summary.md; sparc_publication_summary_table.csv` | complete | Paper-ready controlled-subset summary and publication table... |
| 4C | `outputs/tables/sparc_normalized_tau_pattern_summary.csv` | complete | Normalized τ-pattern similarity and outlier scores... |
| 4D | `docs/ngc7814_failure_mode.md` | complete | NGC7814 structural/holdout/pattern diagnostics (claim D not supported)... |
| 4E | `outputs/tables/sparc_holdout_residuals.csv` | complete | Per-point holdout residual localization... |
| 4F | `outputs/tables/sparc_ml_sensitivity_summary.csv` | complete | Diagnostic M/L grid; NGC7814 baryonic sensitivity (claim J)... |
| 4G | `outputs/tables/sparc_ml_scaled_model_comparison.csv` | complete | Fair scaled TDF/NFW/MOND holdout on same M/L grid... |
| 4H | `outputs/tables/sparc_claim_traceability_matrix_updated.csv` | complete | Post-M/L claim reconciliation (claims I–N)... |
| 4I | `outputs/tables/sparc_ml_prior_weighted_summary.csv` | complete | Diagnostic placeholder prior scaffold (claim O)... |
| 4I-Audit | `outputs/reports/ml_prior_weighting_audit_report.md` | complete | Layered NGC7814 interpretation (tdf_3knot vs tdf_5knot)... |
| 4J | `data/processed/sparc/sparc_photometry_metadata.csv` | complete | SPARC Table-1 metadata for prior scaffolding (claim P context)... |
| 4K | `outputs/tables/sparc_photometry_informed_prior_weights.csv` | complete | Photometry-informed diagnostic prior weights (claim Q not supported)... |
| 4L | `outputs/tables/sparc_ktau_sensitivity_summary.csv` | complete | K_tau sensitivity on 4K harness; qualitative claims stable over {0.5,1,2}... |
| 4M | `outputs/reports/sparc_controlled_subset_final_audit_report.md` | complete | On the controlled six-galaxy SPARC subset, TDF knot models show robust rotation-... |

## Per-galaxy post-M/L status

| Galaxy | Class | Canonical tdf_3knot RMSE | Canonical NFW RMSE | Post-M/L note |
| --- | --- | --- | --- | --- |
| DDO154 | robust_tdf_success | 2.0 | 3.6 | Canonical holdout success retained. TDF remains competitive ... |
| IC2574 | robust_tdf_success | 3.0 | 6.4 | Canonical holdout success retained. TDF remains competitive ... |
| NGC2403 | robust_tdf_success | 8.7 | 9.8 | Canonical holdout success retained. TDF remains competitive ... |
| NGC3198 | robust_tdf_success | 10.4 | 12.0 | Canonical holdout success retained. TDF remains competitive ... |
| NGC6503 | robust_tdf_success | 9.3 | 10.1 | Canonical holdout success retained. TDF remains competitive ... |
| NGC7814 | tdf_failure_mode | 155.8 | 24.9 | Canonical holdout failure retained under fixed SPARC baryons... |

## NGC7814 (consolidated)

- **Canonical:** `tdf_3knot` holdout failure at fixed SPARC baryons (claim I).
- **M/L:** Strong diagnostic sensitivity; fair scaled NFW/MOND also improve (claims J, L).
- **Photometry:** Structurally distinct from five success galaxies (claim P).
- **Priors:** `tdf_5knot` may show diagnostic weighted support; not primary recovery (4K/4I-Audit).
- **K_tau:** Canonical failure label unchanged across tested K_tau values (4L).

## Claim inventory

See `outputs/tables/sparc_controlled_subset_final_claims.csv` and `docs/paper_ready_claims.md` (claims A–Q).

## Key supporting artifacts

- `outputs/tables/sparc_publication_summary_table.csv`
- `outputs/tables/sparc_post_ml_results_summary_table.csv`
- `outputs/tables/sparc_photometry_prior_weighted_summary.csv`
- `outputs/tables/sparc_ktau_sensitivity_summary.csv`
- `outputs/reports/sparc_photometry_informed_prior_report.md`
- `outputs/reports/sparc_ktau_sensitivity_report.md`

## Recommended next steps (outside this audit)

1. Controlled subset expansion with pre-registered selection criteria.
2. Explicit bulge L_3.6 or stellar-population priors before calibrated M/L language.
3. Full SPARC and lensing only after frozen τ-map validation and claim review.
