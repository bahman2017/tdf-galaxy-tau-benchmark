# Expansion-12 Radial Holdout Residual Map Report (Phase 5B-R)

> This diagnostic phase analyzes radial residual structure for expansion_12 flex-recovery cases only. It does not add new fits for scientific claims, does not run expansion_20, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Objective

Localize **where** primary **tdf_3knot** holdout errors occur for flex-recovery galaxies **NGC5055** and **UGC05253**, and whether **tdf_5knot** recovers the same radial bands. Per-point predictions are regenerated with the same train-only protocol as Phases 3C/4E/5B (no alteration of Phase 5B aggregate tables).

## Export method

- **comparison_mode:** `train_only_holdout`
- **validation_stage:** `phase_5b_r_expansion12_holdout_point_residuals`
- **Primary split:** `even_odd_index`
- **Models:** tdf_3knot, tdf_5knot, nfw_refit, mond_fit_a0_simple
- **Test-point rows (all splits):** 736
- **Galaxies:** NGC5055, UGC05253

## Regional RMSE (even/odd)

| galaxy | model | inner | middle | outer | 3k worst region | 5k recovers |
| --- | --- | ---: | ---: | ---: | --- | --- |
| NGC5055 | tdf_3knot | 171.7 | 183.2 | 3.9 | middle | inner;middle;outer |
| NGC5055 | tdf_5knot | 31.7 | 16.3 | 1.7 |  |  |
| NGC5055 | nfw_refit | 81.3 | 45.2 | 41.5 |  |  |
| UGC05253 | tdf_3knot | 33.1 | 21.1 | 74.3 | outer | inner;middle;outer |
| UGC05253 | tdf_5knot | 24.6 | 9.2 | 11.0 |  |  |
| UGC05253 | nfw_refit | 42.3 | 41.1 | 21.0 |  |  |

## NGC5055

- **tdf_3knot fails mainly in:** middle region (even/odd regional RMSE: inner=171.7, middle=183.2, outer=3.9 km/s).
- **tdf_5knot recovery:** regions=inner;middle;outer; same worst band as 3knot=True.
- **Tension type:** knot_flexibility_tension (cf. NGC7814 baryonic inner failure).
- **Before expansion_20:** sensitivity_recovery_case.

## UGC05253

- **tdf_3knot fails mainly in:** outer region (even/odd regional RMSE: inner=33.1, middle=21.1, outer=74.3 km/s).
- **tdf_5knot recovery:** regions=inner;middle;outer; same worst band as 3knot=True.
- **Tension type:** mixed_baryonic_and_knot_flexibility (cf. NGC7814 baryonic inner failure).
- **Before expansion_20:** mixed_sensitivity_recovery_case.

## NGC5055 vs UGC05253

Both show primary tdf_3knot holdout failure with tdf_5knot regional recovery, but NGC5055 is disk-dominated (no bulge in fixed baryons) with inner diagnostic negative residual_v²; UGC05253 is bulge-influenced (high v_bulge/v_bar) closer to NGC7814 baryonic structure yet still flex-recovers on holdout — knot-flexibility dominates for NGC5055, mixed baryonic+knot for UGC05253.

Neither is NGC7814-style all-TDF failure: tdf_5knot improves holdout substantially. NGC7814 inner baryonic tension persists for both knot counts; these flex cases are primarily knot-placement / flexibility tension.

- Similar worst region (tdf_3knot): **False**

## Expansion_20 guidance

- Treat both as **sensitivity-recovery** cases for reporting (tdf_3knot primary fails; tdf_5knot holdout competitive).
- Do **not** promote to robust success without blocked-split stability.
- NGC5055: knot-flexibility tension (disk-dominated baryons).
- UGC05253: mixed baryonic structure + knot-flexibility; higher point count → unstable labels.

## Figures

- `outputs/figures/sparc_subset/ngc5055_radial_holdout_residuals.png`
- `outputs/figures/sparc_subset/ugc05253_radial_holdout_residuals.png`
- `outputs/figures/sparc_subset/expansion12_flex_recovery_radial_comparison.png`

## Outputs

- `outputs/tables/expansion12_holdout_point_residuals.csv`
- `outputs/tables/expansion12_radial_failure_map_summary.csv`
