# Expansion-20 Failure-Mode Analysis (Phase 5D)

> This audit diagnoses expansion_20 failure, mixed, and sensitivity-recovery cases only. It does not add new fits, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Scope

Audit of five **non-robust** expansion_20 galaxies (15/20 are robust_tdf_success): **NGC7814**, **NGC5055**, **UGC05253**, **UGC12506**, **UGC00128**. Uses Phase 5C tables only — no new model fitting.

## Non-robust classification summary

- **all_tdf_failure:** 1
- **sensitivity_recovery:** 3
- **mixed_result:** 1

Primary success count remains **tdf_3knot only** (robust_tdf_success = 15). sensitivity_recovery cases must **not** increment primary success.

## UGC12506 archetype (new in expansion_20)

- **Assigned archetype:** `NGC5055_style_knot_flexibility`
- **Rationale:** Milder sensitivity-recovery (Δholdout≈6.2 km/s) vs NGC5055's ~123 km/s gap; same knot-flexibility class but lower severity.

- tdf_3knot holdout: **11.92** km/s
- tdf_5knot holdout: **5.76** km/s
- Improvement (3k−5k): **6.16** km/s
- Best holdout model: **tdf_5knot**

**Conclusion:** UGC12506 is **not** NGC7814-style (tdf_5knot beats baselines). It is **not** UGC00128 near-tie (tdf_5knot is clearly best). It is closest to **NGC5055-style knot-flexibility** with a **milder** holdout gap (~6 km/s vs ~123 km/s for NGC5055), not the bulge-heavy UGC05253 mixed pattern.

## Reference comparisons

| Galaxy | failure_scope | tdf_3knot | tdf_5knot | NFW | MOND |
| --- | --- | ---: | ---: | ---: | ---: |
| NGC7814 | all_tdf_failure | 155.8 | 113.3 | 24.9 | 27.8 |
| NGC5055 | sensitivity_recovery | 142.9 | 19.6 | 56.9 | 55.4 |
| UGC05253 | sensitivity_recovery | 48.5 | 16.5 | 36.1 | 37.4 |
| UGC12506 | sensitivity_recovery | 11.9 | 5.8 | 8.0 | 20.1 |
| UGC00128 | mixed_result | 3.0 | 5.1 | 2.7 | 6.2 |

## Per-case detail

### NGC7814 (tdf_failure_mode)

- **failure_scope:** all_tdf_failure
- **Best holdout:** nfw_refit
- **tdf_5knot − tdf_3knot:** 42.55 km/s
- **Archetype:** —
- **Radial suspicion:** inner_radius_residual_or_baryonic_tension
- **Baryonic:** median v_bulge/v_bar=0.803
- **Interpretation:** Canonical all-TDF holdout failure on expansion_20; mandated label preserved. Inner baryonic/residual tension; not recoverable by tdf_5knot alone.

### NGC5055 (sensitivity_recovery)

- **failure_scope:** sensitivity_recovery
- **Best holdout:** tdf_5knot
- **tdf_5knot − tdf_3knot:** 123.31 km/s
- **Archetype:** —
- **Radial suspicion:** inner_radius_residual_or_baryonic_tension
- **Baryonic:** median v_bulge/v_bar=0.000
- **Interpretation:** Frozen sensitivity-recovery: tdf_3knot catastrophic on holdout; tdf_5knot competitive. NGC5055-style knot-flexibility (Phase 5B-R). Not primary success.

### UGC05253 (sensitivity_recovery)

- **failure_scope:** sensitivity_recovery
- **Best holdout:** tdf_5knot
- **tdf_5knot − tdf_3knot:** 32.05 km/s
- **Archetype:** —
- **Radial suspicion:** inner_radius_residual_or_baryonic_tension
- **Baryonic:** median v_bulge/v_bar=0.844
- **Interpretation:** Frozen sensitivity-recovery with bulge-influenced baryons and outer radial tension (Phase 5B-R). UGC05253-style mixed baryonic+knot; unstable without blocked holdout.

### UGC12506 (sensitivity_recovery)

- **failure_scope:** sensitivity_recovery
- **Best holdout:** tdf_5knot
- **tdf_5knot − tdf_3knot:** 6.16 km/s
- **Archetype:** NGC5055_style_knot_flexibility
- **Radial suspicion:** mid_disk_mixed
- **Baryonic:** median v_bulge/v_bar=0.000
- **Interpretation:** New expansion_20 sensitivity-recovery; archetype=NGC5055_style_knot_flexibility. NGC5055 style knot flexibility — report tdf_5knot as sensitivity only, not robust success.

### UGC00128 (mixed_result)

- **failure_scope:** mixed_result
- **Best holdout:** nfw_refit
- **tdf_5knot − tdf_3knot:** -2.06 km/s
- **Archetype:** —
- **Radial suspicion:** outer_radius_tension
- **Baryonic:** median v_bulge/v_bar=0.000
- **Interpretation:** Frozen mixed/near-tie: NFW marginally best; tdf_5knot worse than tdf_3knot. Not sensitivity-recovery; exclude from primary success counts.

## Figures

- `outputs/figures/sparc_subset/expansion20_failure_case_residuals.png`
- `outputs/figures/sparc_subset/expansion20_tdf3_vs_tdf5_gap.png`

## Claim boundaries

- expansion_20 controlled cohort only
- No new fits; no full SPARC
- No dark-matter disproof; no lensing

## Outputs

- `outputs/tables/expansion20_failure_diagnostics.csv`
- `outputs/tables/expansion20_case_review_summary.csv`
