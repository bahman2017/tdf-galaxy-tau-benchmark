# Controlled Subset Final Audit (Phase 4M)

Phase 4M consolidates Phases **1A–4L** into a reproducible audit package for the **six-galaxy SPARC** benchmark. **No new fits**, models, full-SPARC extension, or lensing.

## Final claim

On the controlled six-galaxy SPARC subset, TDF knot models show robust rotation-curve consistency in five galaxies, while NGC7814 remains a canonical tdf_3knot failure under fixed baryons. The NGC7814 failure is strongly baryonic-decomposition-sensitive, and tdf_5knot shows diagnostic recovery under some photometry-informed prior scenarios, but this is not a final M/L calibration.

## Build audit outputs

```bash
python3 scripts/build_controlled_subset_final_audit.py
```

## Deliverables

| Artifact | Role |
| --- | --- |
| `outputs/reports/sparc_controlled_subset_final_audit_report.md` | Consolidated narrative |
| `outputs/tables/sparc_controlled_subset_final_status.csv` | Per-phase status |
| `outputs/tables/sparc_controlled_subset_final_claims.csv` | Claims A–Q + FINAL |
| `docs/paper_ready_claims.md` | Language guardrails |
| `docs/results_summary.md` | Phase 4B summary (updated through 4H) |

## Phase map (1A–4L)

| Topic | Phases | Doc / output |
| --- | --- | --- |
| Data ingestion | 1A | `sparc_rotmod_standardized.csv` |
| Subset selection | 1B | `sparc_subset_selection.csv` |
| Radial τ reconstruction | 2A | `sparc_subset_tau_profiles.csv` |
| Baselines | 3A, 3A-R | baseline comparison tables |
| MOND/RAR | 3M | `sparc_mond_comparison.csv` |
| TDF knots | 3B | `sparc_full_model_comparison.csv` |
| Holdout | 3C | `sparc_tdf_holdout_validation.csv` |
| Failure modes | 4A | `sparc_failure_mode_summary.csv` |
| Results summary | 4B | `docs/results_summary.md` |
| τ patterns | 4C | normalized pattern tables |
| NGC7814 | 4D, 4E | `docs/ngc7814_failure_mode.md` |
| M/L sensitivity | 4F, 4G | scaled comparison CSV |
| Claim reconciliation | 4H | traceability matrix |
| Prior scaffold | 4I, 4I-Audit | `docs/ml_prior_framework.md` |
| Photometry metadata | 4J | `sparc_photometry_metadata.csv` |
| Photometry priors | 4K | `docs/photometry_informed_ml_priors.md` |
| K_tau sensitivity | 4L | `docs/ktau_sensitivity.md` |

## Caveats (mandatory)

- No dark-matter disproof
- No ΛCDM replacement
- No full-SPARC validation
- No lensing confirmation
- No universal τ-profile claim
- No final M/L calibration
- K_tau not measured
- **tdf_3knot** primary; **tdf_5knot** sensitivity only

## Before expanding the subset

1. Review `sparc_controlled_subset_final_audit_report.md` and final claims CSV.
2. Pre-register selection criteria for additional galaxies.
3. Do not use tdf_5knot-only prior recovery as primary NGC7814 narrative.
