# M/L Prior Weighting Audit Report (Phase 4I-Audit)

> Priors are **diagnostic placeholders**. **No final M/L calibration** is claimed. **NGC7814 remains a canonical TDF holdout failure** at disk=bulge=1.

> Interpretation logic: `phase_4i_audit_v2`

## Correction applied

Phase 4I used a single `prior_supported_tdf_recovery` label driven mainly by **tdf_5knot** win fractions while **tdf_3knot** had 0% wins. Labels are now split: primary **tdf_3knot** vs sensitivity **tdf_5knot** vs either-variant. Per-model beat-NFW fractions are computed per model (not tdf_3knot only). Phase 4I tables and framework report were **regenerated**.

## 1. Prior weight verification

### uniform_plausible_band
- Normalized weights sum: **1.000000** (expect 1.0)
- Weighting: `uniform`

### conservative_bulge_downweight_test
- Normalized weights sum: **1.000000** (expect 1.0)
- Weighting: `bulge_downweight`
- Low bulge (0.5): mean norm weight **0.1449**; high bulge (1.0): **0.0725** (higher weight at **lower** bulge_scale — as intended).

### canonical_delta_prior
- Normalized weights sum: **1.000000** (expect 1.0)
- Weighting: `gaussian_delta`

## 2. Uniform vs conservative discrepancy (NGC7814)

Phase 4F/4G show better TDF performance at **lower bulge_scale**. **conservative_bulge_downweight_test** assigns **more** normalized weight to low-bulge cells than **uniform_plausible_band**, so tdf_5knot win fraction **increases** (e.g. ~67% → ~78%). Both scenarios should show **sensitivity_tdf_5knot_diagnostic_recovery**, not contradictory `canonical_failure_only` vs generic recovery.

Primary **tdf_3knot** remains at **0%** prior-weight wins in plausible band because **tdf_5knot** or **MOND/NFW** win per-cell RMSE on those cells.

## 3. NGC7814 interpretation by scenario

### uniform_plausible_band
- Category: `sensitivity_tdf_5knot_diagnostic_recovery`
- Primary tdf_3knot: `baryon_sensitive_competitive`
- Sensitivity tdf_5knot: `prior_weighted_win_fraction_elevated`
- Either variant: `either_tdf_variant_elevated_win_fraction`
- Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration.

### conservative_bulge_downweight_test
- Category: `sensitivity_tdf_5knot_diagnostic_recovery`
- Primary tdf_3knot: `baryon_sensitive_competitive`
- Sensitivity tdf_5knot: `prior_weighted_win_fraction_elevated`
- Either variant: `either_tdf_variant_elevated_win_fraction`
- Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration.

### canonical_delta_prior
- Category: `canonical_failure_primary_tdf_3knot`
- Primary tdf_3knot: `canonical_failure_persists_under_prior`
- Sensitivity tdf_5knot: `limited_prior_support`
- Either variant: `either_tdf_variant_mixed_support`
- Canonical TDF holdout failure at M/L=1; primary tdf_3knot lacks prior-weighted win support. Lower-bulge cells can still lower RMSE (baryon sensitivity).

## 4. Interpretation logic (thresholds)

- **canonical_result:** tdf_3knot RMSE > 2× NFW at M/L=1
- **primary_tdf_3knot:** uses tdf_3knot win fraction & tdf_3knot beats-NFW fraction
- **sensitivity_tdf_5knot:** uses tdf_5knot win fraction & beats-NFW
- **interpretation_category:** `sensitivity_tdf_5knot_diagnostic_recovery` if tdf_3 wins <15% and tdf_5 wins ≥45%

## Outputs

- `outputs/tables/ml_prior_weight_audit.csv`
- `outputs/tables/ngc7814_prior_scenario_breakdown.csv`
