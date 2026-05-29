# SPARC Fair M/L-Scaled Baseline Comparison Report (Phase 4G)

> This phase is a fair M/L-scaled diagnostic comparison. It does not recalibrate SPARC baryons, does not introduce a final fitted M/L model, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Objective

Re-evaluate **TDF**, **NFW**, and **MOND** under the same diagnostic disk/bulge M/L scaling grid used in Phase 4F, with train-only even/odd holdout refits at each scale.

## Why this phase was needed after Phase 4F

Phase 4F showed strong NGC7814 TDF sensitivity to bulge scaling but compared TDF only against **canonical** (unscaled) NFW/MOND holdout RMSE. Phase 4G refits NFW and MOND on the **same scaled** baryons for a fair comparison.

## Scaling method

`v_bar² = v_gas² + s_disk·v_disk² + s_bulge·v_bulge²` (signed components; gas unscaled). τ reconstruction uses `tau(r_min)=0`.

## Fair model comparison method

- Models: ['tdf_3knot', 'tdf_5knot', 'nfw_refit_scaled', 'mond_fit_a0_scaled']
- Split: `even_odd_index`
- Comparison mode: `train_only_scaled_holdout`
- NFW: log-space multistart refit (Phase 3A-R) on train points only.
- MOND: log10(a0) refit on train only.
- TDF: same train-only knot refit as Phase 4F; K_tau fixed.

## Scale grid

- disk_scale: [0.5, 0.7, 1.0, 1.3]
- bulge_scale: [0.2, 0.5, 0.7, 1.0, 1.3]

## NGC7814 results

- Canonical scales (1,1): tdf_3knot=155.8, nfw_scaled=24.9, mond_scaled=27.8 km/s
- Best model at (1,1): **nfw_refit_scaled**

- Best plausible-band tdf_3knot: disk=0.7, bulge=0.5, RMSE=3.4 km/s (nfw=3.3, mond=3.1)
- TDF beats scaled NFW in **3/9** plausible-band cells

### Interpretation (NGC7814)

At **canonical** M/L=1, scaled NFW/MOND remain far better than TDF on holdout RMSE; the canonical failure label is unchanged. After fair scaled refit, **NFW or MOND often remain competitive or better** than TDF at many plausible-band scales. TDF beats scaled NFW in 3/9 (33%) plausible-band cells; lowering bulge_scale typically helps **all** models, not only TDF. The failure is **primarily sensitive to fixed bulge-dominated baryons** at canonical decomposition; fair comparison shows TDF improvement can be **shared** with baselines when baryons are rescaled. NFW or MOND wins at least one plausible-scale cell for NGC7814. Extreme disk_scale=0.5 is outside the plausible band; conclusions about competition should emphasize the plausible band unless noted.

## Success-galaxy stability

- Galaxies with `tdf_success_stable_under_plausible_scaling`: 5 / 6
- Galaxies where NFW/MOND wins at some plausible scale: 1 / 6

## Limitations

- Diagnostic M/L grid; not photometric calibration.
- Distance, inclination, and K_tau fixed.
- even/odd split only in aggregated tables.
- Canonical Phase 4A failure label at M/L=1 unchanged.
