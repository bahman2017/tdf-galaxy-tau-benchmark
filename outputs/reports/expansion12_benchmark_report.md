# Expansion-12 Controlled Benchmark Report (Phase 5B)

> Results are for the controlled **expansion_12** cohort only (twelve galaxies). This is not full-SPARC validation, does not disprove dark matter, does not replace ΛCDM, and does not include lensing. **tdf_3knot** is the primary conservative TDF model; **tdf_5knot** is sensitivity/high-flexibility only.

## Cohort

Galaxies (12): DDO154, IC2574, NGC2403, NGC3198, NGC6503, NGC7814, UGC02953, UGC05253, NGC5055, UGC00128, NGC0289, DDO161

- Original six: DDO154, IC2574, NGC2403, NGC3198, NGC6503, NGC7814
- Phase 5A additions: UGC02953, UGC05253, NGC5055, UGC00128, NGC0289, DDO161

## Failure-mode summary

- **robust_tdf_success:** 8
- **tdf_failure_mode:** 2
- **mixed_result / other:** 2
- Primary **tdf_3knot** beats **nfw_refit** on holdout: **8** / 12 galaxies

## Per-galaxy holdout (even/odd, km/s)

| Galaxy | Class | tdf_3knot | tdf_5knot | nfw_refit | mond_fit | Best |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| DDO154 | robust_tdf_success | 2.0 | 1.4 | 3.6 | 4.0 | tdf_5knot |
| DDO161 | robust_tdf_success | 0.7 | 0.8 | 3.9 | 6.6 | tdf_3knot |
| IC2574 | robust_tdf_success | 3.0 | 1.7 | 6.4 | 6.3 | tdf_5knot |
| NGC0289 | robust_tdf_success | 19.8 | 19.5 | 21.9 | 22.9 | tdf_5knot |
| NGC2403 | robust_tdf_success | 8.7 | 3.4 | 9.8 | 14.2 | tdf_5knot |
| NGC3198 | robust_tdf_success | 10.4 | 8.2 | 12.0 | 14.3 | tdf_5knot |
| NGC5055 | tdf_failure_mode | 142.9 | 19.6 | 56.9 | 55.4 | tdf_5knot |
| NGC6503 | robust_tdf_success | 9.3 | 4.9 | 10.1 | 12.4 | tdf_5knot |
| NGC7814 | tdf_failure_mode | 155.8 | 113.3 | 24.9 | 27.8 | nfw_refit |
| UGC00128 | mixed_result | 3.0 | 5.1 | 2.7 | 6.2 | nfw_refit |
| UGC02953 | robust_tdf_success | 37.8 | 26.3 | 41.4 | 44.2 | tdf_5knot |
| UGC05253 | mixed_result | 48.5 | 16.5 | 36.1 | 37.4 | tdf_5knot |

## TDF vs NFW/MOND (holdout)

Primary reporting uses **tdf_3knot**. **tdf_5knot** is documented as sensitivity only. In-sample metrics often favor higher knot counts; holdout is the gate for predictive claims.

## Claim boundaries

See `outputs/tables/expansion12_claim_traceability.csv`. Do not claim full-SPARC validation, final M/L calibration, or dark-matter disproof.

## Outputs

- `outputs/tables/expansion12_model_comparison.csv`
- `outputs/tables/expansion12_holdout_validation.csv`
- `outputs/tables/expansion12_failure_mode_summary.csv`
