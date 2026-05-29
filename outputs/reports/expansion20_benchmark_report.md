# Expansion-20 Controlled Benchmark Report (Phase 5C)

> Results are for the controlled **expansion_20** cohort only (twenty galaxies). This is not full-SPARC validation, does not disprove dark matter, does not replace ΛCDM, and does not include lensing. **tdf_3knot** is the primary conservative model; **tdf_5knot** is sensitivity/high-flexibility only and must not be counted as primary success. **sensitivity_recovery** cases (tdf_3knot holdout failure with tdf_5knot recovery) are reported separately from **robust_tdf_success**.

## Cohort

Galaxies (20): DDO154, IC2574, NGC2403, NGC3198, NGC6503, NGC7814, UGC02953, UGC05253, UGC09133, UGC06787, NGC5055, UGC00128, NGC0289, UGC12506, UGC11455, NGC6015, DDO161, NGC7793, UGC07524, UGC08490

- Original six: DDO154, IC2574, NGC2403, NGC3198, NGC6503, NGC7814
- Phase 5A additions (14): UGC02953, UGC05253, UGC09133, UGC06787, NGC5055, UGC00128, NGC0289, UGC12506, UGC11455, NGC6015, DDO161, NGC7793, UGC07524, UGC08490

## Classification summary (primary = tdf_3knot only)

- **robust_tdf_success:** 15 (counts toward primary success: **15**)
- **sensitivity_recovery:** 3 (tdf_5knot recovery — **not** primary success)
- **tdf_failure_mode:** 1
- **mixed_result:** 1

- Primary **tdf_3knot** beats **nfw_refit** on holdout: **15** / 20
- Primary **tdf_3knot** beats **mond_fit** on holdout: **17** / 20

### Frozen guardrails (Phase 5B-Audit / 5B-R)

- **NGC7814:** canonical all-TDF failure (mandated).
- **NGC5055, UGC05253:** sensitivity_recovery (not robust success).
- **UGC00128:** mixed/near-tie unless tdf_3knot beats both baselines.

## Per-galaxy holdout (even/odd, km/s)

| Galaxy | Class | Primary? | tdf_3knot | tdf_5knot | nfw | mond | Best |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| DDO154 | robust_tdf_success | yes | 2.0 | 1.4 | 3.6 | 4.0 | tdf_5knot |
| DDO161 | robust_tdf_success | yes | 0.7 | 0.8 | 3.9 | 6.6 | tdf_3knot |
| IC2574 | robust_tdf_success | yes | 3.0 | 1.7 | 6.4 | 6.3 | tdf_5knot |
| NGC0289 | robust_tdf_success | yes | 19.8 | 19.5 | 21.9 | 22.9 | tdf_5knot |
| NGC2403 | robust_tdf_success | yes | 8.7 | 3.4 | 9.8 | 14.2 | tdf_5knot |
| NGC3198 | robust_tdf_success | yes | 10.4 | 8.2 | 12.0 | 14.3 | tdf_5knot |
| NGC5055 | sensitivity_recovery | no | 142.9 | 19.6 | 56.9 | 55.4 | tdf_5knot |
| NGC6015 | robust_tdf_success | yes | 7.1 | 4.9 | 8.3 | 13.4 | tdf_5knot |
| NGC6503 | robust_tdf_success | yes | 9.3 | 4.9 | 10.1 | 12.4 | tdf_5knot |
| NGC7793 | robust_tdf_success | yes | 4.6 | 3.8 | 8.2 | 8.5 | tdf_5knot |
| NGC7814 | tdf_failure_mode | no | 155.8 | 113.3 | 24.9 | 27.8 | nfw_refit |
| UGC00128 | mixed_result | no | 3.0 | 5.1 | 2.7 | 6.2 | nfw_refit |
| UGC02953 | robust_tdf_success | yes | 37.8 | 26.3 | 41.4 | 44.2 | tdf_5knot |
| UGC05253 | sensitivity_recovery | no | 48.5 | 16.5 | 36.1 | 37.4 | tdf_5knot |
| UGC06787 | robust_tdf_success | yes | 38.3 | 30.8 | 38.6 | 43.1 | tdf_5knot |
| UGC07524 | robust_tdf_success | yes | 1.6 | 1.5 | 2.8 | 3.6 | tdf_5knot |
| UGC08490 | robust_tdf_success | yes | 1.1 | 1.1 | 1.6 | 1.8 | tdf_3knot |
| UGC09133 | robust_tdf_success | yes | 33.2 | 25.7 | 36.3 | 38.0 | tdf_5knot |
| UGC11455 | robust_tdf_success | yes | 15.8 | 16.0 | 39.4 | 39.4 | tdf_3knot |
| UGC12506 | sensitivity_recovery | no | 11.9 | 5.8 | 8.0 | 20.1 | tdf_5knot |

## TDF vs NFW/MOND

Holdout gates predictive claims. **tdf_5knot** may beat baselines where **tdf_3knot** fails; such cases are **sensitivity_recovery**, not robust primary success.

## Claim boundaries

See `outputs/tables/expansion20_claim_traceability.csv`. No full-SPARC validation, no dark-matter disproof, no lensing.

## Outputs

- `outputs/tables/expansion20_model_comparison.csv`
- `outputs/tables/expansion20_holdout_validation.csv`
- `outputs/tables/expansion20_failure_mode_summary.csv`
