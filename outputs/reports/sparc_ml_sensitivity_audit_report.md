# SPARC M/L Sensitivity Audit Report (Phase 4F)

> This phase is a diagnostic M/L sensitivity audit. It does not recalibrate SPARC baryons, does not introduce a final fitted M/L model, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Objective

Test whether the **NGC7814** TDF holdout failure (Phase 4E inner-region localization) is sensitive to diagnostic disk/bulge mass-to-light scaling of the fixed SPARC baryonic decomposition.

## Scaling method

Canonical convention (Phase 1A): `v_bar² = v_gas² + s_disk·v_disk² + s_bulge·v_bulge²` with signed component velocities as stored in SPARC rotmod. Gas term is **not** scaled. τ profiles use `tau(r_min)=0` as in Phase 2A. TDF holdout uses **train-only** even/odd refit per scale.

## Scale grid

- disk_scale: [0.5, 0.7, 1.0, 1.3]
- bulge_scale: [0.2, 0.5, 0.7, 1.0, 1.3]
- Plausible band (diagnostic): disk ∈ (0.7, 1.3), bulge ∈ (0.5, 1.0)

## NGC7814 results

- Canonical tdf_3knot RMSE: **155.8** km/s
- Best scaled tdf_3knot RMSE: **3.4** km/s
- Canonical NFW/MOND (not M/L-scaled): **24.9** / **27.8** km/s
- TDF improved under scaling: **True**
- TDF beats NFW under best scale (any grid point): **True**
- TDF beats NFW under plausible band: **True**
- Best plausible scaled tdf_3knot RMSE: **3.4** km/s
- TDF beats MOND under best scale: **True**

- Best grid cell (tdf_3knot): disk_scale=0.5, bulge_scale=0.5, inner RMSE=4.4 km/s, plausible_scale=False.

### Interpretation (NGC7814)

Lowering bulge_scale and/or disk_scale **can reduce** TDF holdout RMSE versus canonical baryons; inner RMSE typically improves when bulge contribution is reduced. Within the **plausible diagnostic band**, TDF tdf_3knot RMSE (~3.4 km/s) can be competitive with canonical NFW/MOND — but this is **not** the canonical SPARC decomposition. At **canonical** disk_scale=bulge_scale=1.0, holdout RMSE matches Phase 3C/4E (~156 km/s); the failure is **highly sensitive** to bulge/disk scaling. This **partially reduces** inner negative residual_v² when bulge_scale is lowered but does **not** establish a final astrophysical M/L calibration.

## Success-galaxy stability

- Success cases with `tdf_improved_under_ml_scaling` True: 4 / 5.
- Success cases losing holdout-success-like status under any grid cell: 3 galaxies (see summary table).

## Limitations

- Diagnostic scaling only; not a full M/L fit or photometric calibration.
- NFW/MOND comparisons use **canonical** holdout at default baryons unless noted.
- K_tau, distance, and inclination are fixed.
- even/odd split only for aggregated Phase 4F tables.

## Outputs

- `outputs/tables/sparc_ml_sensitivity_summary.csv`
- `outputs/tables/ngc7814_ml_sensitivity_detail.csv`
- `outputs/tables/sparc_ml_sensitivity_holdout_comparison.csv`
