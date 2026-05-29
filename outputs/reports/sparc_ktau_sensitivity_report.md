# SPARC K_tau Sensitivity Report (Phase 4L)

> K_tau is treated as a fixed normalization convention in this audit. This phase does not measure K_tau, does not perform final M/L calibration, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Objective

Test whether six-galaxy TDF conclusions under **photometry-informed prior weighting** (Phase 4K) are stable when **K_tau** is varied while knot amplitudes are refit. NFW/MOND holdout RMSE values are taken from Phase 4G (fair scaled baselines).

## K_tau values tested

0.5, 1.0, 2.0

## Method

- Same M/L grid and Phase 4K photometry-informed prior weights.
- Train-only even/odd holdout; refit **tdf_3knot** and **tdf_5knot** amplitudes only.
- K_tau is **not** fitted.

## Five success-galaxy stability

- **DDO154** (tdf_3knot): {'sensitive_to_ktau': 3, 'reference_ktau': 3, 'stable_vs_reference_ktau': 3}
- **IC2574** (tdf_3knot): {'moderate_ktau_variation': 3, 'reference_ktau': 3, 'stable_vs_reference_ktau': 3}
- **NGC2403** (tdf_3knot): {'stable_vs_reference_ktau': 6, 'reference_ktau': 3}
- **NGC3198** (tdf_3knot): {'sensitive_to_ktau': 6, 'reference_ktau': 3}
- **NGC6503** (tdf_3knot): {'stable_vs_reference_ktau': 6, 'reference_ktau': 3}

## NGC7814

Canonical **tdf_3knot** failure at M/L=1 is unchanged by definition (canonical holdout at fixed baryons).
Prior-weighted diagnostic **tdf_5knot** support may vary with K_tau; see `ngc7814_ktau_sensitivity.csv`.

### photometry_uniform_plausible
- K_tau=0.5: Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration. (5knot recovery survives: True)
- K_tau=1.0: Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration. (5knot recovery survives: True)
- K_tau=2.0: Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration. (5knot recovery survives: True)

### morphology_aware_conservative
- K_tau=0.5: Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration. (5knot recovery survives: True)
- K_tau=1.0: Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration. (5knot recovery survives: True)
- K_tau=2.0: Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration. (5knot recovery survives: True)

### canonical_anchor_prior
- K_tau=0.5: Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration. (5knot recovery survives: False)
- K_tau=1.0: Canonical TDF holdout failure at M/L=1; primary tdf_3knot lacks prior-weighted win support. Lower-bulge cells can still lower RMSE (baryon sensitivity). (5knot recovery survives: False)
- K_tau=2.0: Canonical TDF holdout failure at M/L=1; primary tdf_3knot lacks prior-weighted win support. Lower-bulge cells can still lower RMSE (baryon sensitivity). (5knot recovery survives: False)

### ngc7814_bulge_sensitivity_diagnostic
- K_tau=0.5: Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration. (5knot recovery survives: True)
- K_tau=1.0: Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration. (5knot recovery survives: True)
- K_tau=2.0: Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration. (5knot recovery survives: True)

Reference Phase 4K summary: `outputs/tables/sparc_photometry_prior_weighted_summary.csv`

## Conclusion on K_tau dependence

K_tau is partially degenerate with dτ/dr amplitude; interpret metric shifts as normalization-sensitivity, not as a measured physical constant.
