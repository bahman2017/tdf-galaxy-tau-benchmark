# Controlled Expansion Cohort — Final Audit Report (Phase 5E)

> Audit version: `phase_5e_controlled_expansion_final`. **Documentation and consolidation only** — no new fits, no new models, no full SPARC, no lensing.

## Final expansion_20 statement

> In the pre-registered controlled expansion_20 cohort, the primary conservative tdf_3knot model achieves robust holdout success in 15 of 20 galaxies. Three additional galaxies show sensitivity-recovery where tdf_5knot improves substantially but is not counted as primary success. NGC7814 remains the only all-TDF holdout failure, and UGC00128 remains a mixed near-tie case.

## Required caveats

- Results apply to the pre-registered expansion_20 controlled cohort only — not full-SPARC validation.
- Lensing is not tested in this repository phase.
- This benchmark does not disprove dark matter.
- Results do not replace ΛCDM as a cosmological framework.
- No universal τ-profile was discovered.
- tdf_5knot is sensitivity/high-flexibility only; tdf_3knot is the primary conservative TDF model.
- sensitivity_recovery cases must not be counted as primary robust success.
- No final or photometry-calibrated M/L model is claimed.
- Expansion_12 (12 galaxies) is a nested subset of expansion_20; cohort comparisons are descriptive.

## expansion_12 vs expansion_20 comparison

| Metric | expansion_12 | expansion_20 |
| --- | ---: | ---: |
| cohort_size | 12.0 | 20.0 |
| robust_tdf_success | 8.0 | 15.0 |
| sensitivity_recovery | 0.0 | 3.0 |
| tdf_failure_mode | 2.0 | 1.0 |
| mixed_result | 2.0 | 1.0 |
| tdf_3knot_beats_nfw_holdout | 8.0 | 15.0 |
| tdf_3knot_beats_mond_holdout | 9.0 | 17.0 |
| primary_success_fraction | 0.667 | 0.75 |

### Interpretation

- **Robust primary success:** 8.0/12 → **15.0/20** (tdf_3knot holdout gate).
- **Sensitivity-recovery:** 0.0/12 → **3.0/20** (NGC5055, UGC05253, UGC12506 in e20; e12 used legacy labels — NGC5055 was `tdf_failure_mode` in 5B, reclassified in 5C).
- **All-TDF failure:** 2.0 (NGC7814) in both cohorts.
- **Mixed near-tie:** 2.0 (UGC00128) in both cohorts.
- **tdf_3knot vs NFW holdout:** 8.0/12 → 15.0/20.
- **tdf_3knot vs MOND holdout:** 9.0/12 → 17.0/20.

## Phase 5B–5D consolidation

| Phase | Focus |
| --- | --- |
| 5B | expansion_12 benchmark (12 galaxies) |
| 5B-Audit | NGC7814, NGC5055, UGC00128, UGC05253 failure/mixed diagnostics |
| 5B-R | Radial holdout maps for NGC5055, UGC05253 |
| 5C | expansion_20 benchmark with sensitivity_recovery class |
| 5D | Five non-robust e20 cases; UGC12506 archetype |

## Per-galaxy expansion_20 classification

| Galaxy | Class | tdf_3knot | tdf_5knot | NFW | MOND | Primary? |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| DDO154 | robust_tdf_success | 2.0 | 1.4 | 3.6 | 4.0 | yes |
| DDO161 | robust_tdf_success | 0.7 | 0.8 | 3.9 | 6.6 | yes |
| IC2574 | robust_tdf_success | 3.0 | 1.7 | 6.4 | 6.3 | yes |
| NGC0289 | robust_tdf_success | 19.8 | 19.5 | 21.9 | 22.9 | yes |
| NGC2403 | robust_tdf_success | 8.7 | 3.4 | 9.8 | 14.2 | yes |
| NGC3198 | robust_tdf_success | 10.4 | 8.2 | 12.0 | 14.3 | yes |
| NGC5055 | sensitivity_recovery | 142.9 | 19.6 | 56.9 | 55.4 | no |
| NGC6015 | robust_tdf_success | 7.1 | 4.9 | 8.3 | 13.4 | yes |
| NGC6503 | robust_tdf_success | 9.3 | 4.9 | 10.1 | 12.4 | yes |
| NGC7793 | robust_tdf_success | 4.6 | 3.8 | 8.2 | 8.5 | yes |
| NGC7814 | tdf_failure_mode | 155.8 | 113.3 | 24.9 | 27.8 | no |
| UGC00128 | mixed_result | 3.0 | 5.1 | 2.7 | 6.2 | no |
| UGC02953 | robust_tdf_success | 37.8 | 26.3 | 41.4 | 44.2 | yes |
| UGC05253 | sensitivity_recovery | 48.5 | 16.5 | 36.1 | 37.4 | no |
| UGC06787 | robust_tdf_success | 38.3 | 30.8 | 38.6 | 43.1 | yes |
| UGC07524 | robust_tdf_success | 1.6 | 1.5 | 2.8 | 3.6 | yes |
| UGC08490 | robust_tdf_success | 1.1 | 1.1 | 1.6 | 1.8 | yes |
| UGC09133 | robust_tdf_success | 33.2 | 25.7 | 36.3 | 38.0 | yes |
| UGC11455 | robust_tdf_success | 15.8 | 16.0 | 39.4 | 39.4 | yes |
| UGC12506 | sensitivity_recovery | 11.9 | 5.8 | 8.0 | 20.1 | no |

## Non-robust cases (expansion_20)

- **NGC7814:** all-TDF failure (tdf_3knot and tdf_5knot fail vs baselines).
- **NGC5055, UGC05253, UGC12506:** sensitivity_recovery — tdf_5knot recovers; not primary.
- **UGC00128:** mixed near-tie; NFW marginally best.

## Claims C20-A – C20-H

| ID | Status | Claim |
| --- | --- | --- |
| C20-A | supported | expansion_20 cohort processed reproducibly through frozen pipeline.... |
| C20-B | supported_with_caveat | Primary tdf_3knot robust holdout success in 15 of 20 galaxies.... |
| C20-C | supported_sensitivity_only | tdf_5knot improves sensitivity-recovery cases.... |
| C20-D | supported | NGC7814 remains all-TDF holdout failure.... |
| C20-E | not_supported | TDF validated on full SPARC.... |
| C20-F | prohibited | Dark matter is disproven.... |
| C20-G | not_tested | Lensing confirms TDF.... |
| C20-H | not_supported | Universal τ-profile discovered.... |

## Phase status (5B–5E)

| Phase | Output | Status |
| --- | --- | --- |
| 5B | `outputs/reports/expansion12_benchmark_report.md` | complete |
| 5B-Audit | `outputs/reports/expansion12_failure_mode_analysis_report.md` | complete |
| 5B-R | `outputs/reports/expansion12_radial_residual_map_report.md` | complete |
| 5C | `outputs/reports/expansion20_benchmark_report.md` | complete |
| 5D | `outputs/reports/expansion20_failure_mode_analysis_report.md` | complete |
| 5E | `outputs/reports/controlled_expansion20_final_audit_report.md` | complete |

## Key artifacts

- `outputs/tables/controlled_expansion_comparison_summary.csv`
- `outputs/tables/controlled_expansion_final_claims.csv`
- `docs/controlled_expansion_results.md`
- `docs/paper_ready_claims.md` (expansion section)

## Recommended next steps

1. Publication tables from expansion_20 failure summary and comparison CSV.
2. Optional blocked-holdout stability for UGC12506.
3. Full SPARC or lensing only after explicit protocol amendment and claim review.
