# SPARC Radial Holdout Failure Report (Phase 4E)

> This phase archives per-point holdout residuals and diagnoses radial failure structure. It does not add new models, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Objective

Export **train-only** holdout predictions at each test radius and localize where TDF vs NFW/MOND errors concentrate, with emphasis on **NGC7814**.

## Holdout residual export method

- Protocol: Phase 3C splits (`even_odd_index`, `inner_middle_outer_blocked`, `radial_kfold_5`).
- Models: `tdf_3knot`, `tdf_5knot`, `nfw_refit`, `mond_fit_a0_simple`.
- **comparison_mode:** `train_only_holdout` (all models refit on training radii; no full-sample baseline mixing).
- TDF: Phase 2A initialization/bounds on **training radii only**; predictions on held-out points.
- Table: `outputs/tables/sparc_holdout_point_residuals.csv`.

- Total test-point rows exported: **1488**.

## Per-galaxy radial failure summary (even/odd, tdf_3knot)

| galaxy_id | worst_region | rmse inner | rmse middle | rmse outer |
| --- | --- | ---: | ---: | ---: |
| DDO154 | outer | 1.9 | 0.4 | 2.9 |
| IC2574 | middle | 3.0 | 3.1 | 2.8 |
| NGC2403 | inner | 10.6 | 10.5 | 1.3 |
| NGC3198 | inner | 16.4 | 6.7 | 3.9 |
| NGC6503 | inner | 15.4 | 2.0 | 4.6 |
| NGC7814 | inner | 236.2 | 130.5 | 0.7 |

## NGC7814 radial failure map discussion

- Dominant TDF error region (tdf_3knot, even/odd): **inner**.
- Inner-region RMSE — tdf_3knot: **236.2** km/s; nfw_refit: **43.1** km/s.
- tdf_3knot negative-v² flags on inner holdout points: **3**.

Holdout failures for TDF on NGC7814 **cluster at inner/bulge-dominated radii** (r ≲ few kpc) where fixed SPARC baryonic decomposition shows strong bulge contribution and Phase 4D reported negative diagnostic residuals. NFW/MOND holdout residuals are **radially smoother** at smaller |residual| in the inner third on even/odd.

**tdf_5knot** can lower RMSE in some blocked/CV folds but remains unstable on even/odd relative to NFW; see regional summary table. **tdf_4knot** is not in the export set; Phase 4D negative-v² pathology at the inner knot (r ≈ 0.63 kpc) aligns with the inner holdout radius band.

## TDF vs NFW/MOND residual localization

On NGC7814 even/odd holdout, TDF exhibits large signed residuals at inner radii; NFW/MOND absorb much of the inner rotation curve with smoother holdout residual maps (see figures).

## Limitations

- Refitting cost scales with galaxies × splits × models; export is diagnostic only.
- Radial regions are index-thirds, not physical bulge/halo boundaries.
- Single K_tau and fixed baryons; no M/L or distance fitting.

## Outputs

- `outputs/tables/sparc_holdout_point_residuals.csv`
- `outputs/tables/sparc_radial_failure_map_summary.csv`
- `outputs/figures/sparc_subset/ngc7814_radial_holdout_residual_map.png`
- `outputs/figures/sparc_subset/holdout_residual_maps_all_galaxies.png`
