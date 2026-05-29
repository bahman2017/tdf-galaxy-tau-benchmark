# Expansion-12 Failure-Mode Analysis (Phase 5B-Audit)

> This audit diagnoses expansion_12 failure and mixed cases only. It does not add new fits, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Scope

Diagnostic review of four expansion_12 galaxies before any expansion_20 run: **NGC7814**, **NGC5055**, **UGC00128**, **UGC05253**. Uses Phase 5B tables only (no new model fitting).

## NGC5055 vs NGC7814 (not equivalent)

NGC7814: all-TDF holdout failure (tdf_3knot and tdf_5knot both >> NFW/MOND). NGC5055: primary tdf_3knot failure only; tdf_5knot holdout ~20 km/s beats NFW/MOND ~56 km/s — flexibility/knot-count sensitivity, not canonical all-TDF failure.

| Quantity | NGC7814 | NGC5055 |
| --- | ---: | ---: |
| tdf_3knot holdout RMSE [km/s] | 155.8 | 142.9 |
| tdf_5knot holdout RMSE [km/s] | 113.3 | 19.6 |
| nfw_refit holdout RMSE [km/s] | 24.9 | 56.9 |
| TDF failure scope | all_tdf_failure | flex_recovery |

- **NGC7814:** both tdf_3knot and tdf_5knot fail vs NFW/MOND on even/odd holdout (all-TDF failure).
- **NGC5055:** tdf_3knot fails; tdf_5knot is much better (~123 km/s improvement), beating NFW/MOND on holdout — knot-placement / flexibility sensitivity, not canonical all-TDF failure.

## Per-case summary

### NGC7814 (tdf_failure_mode)

- **Holdout RMSE (km/s):** tdf_3knot=155.80, tdf_5knot=113.25, NFW=24.89, MOND=27.85
- **Best holdout model:** nfw_refit
- **tdf_5knot − tdf_3knot improvement (positive = 5 better):** 42.55 km/s
- **TDF failure scope:** all_tdf_failure
- **Mixed subtype:** canonical_failure
- **Radial region:** inner_radius_residual_or_baryonic_tension
- **Baryonic context:** median v_bulge/v_bar=0.803, frac negative residual_v²=0.28
- **Interpretation:** Canonical expansion_12 holdout failure: primary tdf_3knot and sensitivity tdf_5knot both fail vs NFW/MOND on even/odd holdout; not recoverable by knot count alone. Retain mandated failure language; bulge/inner-residual context applies.

### NGC5055 (tdf_failure_mode)

- **Holdout RMSE (km/s):** tdf_3knot=142.86, tdf_5knot=19.56, NFW=56.87, MOND=55.37
- **Best holdout model:** tdf_5knot
- **tdf_5knot − tdf_3knot improvement (positive = 5 better):** 123.31 km/s
- **TDF failure scope:** flex_recovery
- **Mixed subtype:** canonical_failure
- **Radial region:** inner_radius_residual_or_baryonic_tension
- **Baryonic context:** median v_bulge/v_bar=0.000, frac negative residual_v²=0.54
- **Interpretation:** Primary-model (tdf_3knot) holdout failure with large RMSE, but tdf_5knot holdout is competitive (~20 km/s vs NFW/MOND ~56 km/s). Interpret as knot-placement / flexibility sensitivity, not an NGC7814-style all-TDF failure. Do not use tdf_5knot as primary success without explicit sensitivity labeling.

### UGC00128 (mixed_result)

- **Holdout RMSE (km/s):** tdf_3knot=3.00, tdf_5knot=5.06, NFW=2.72, MOND=6.24
- **Best holdout model:** nfw_refit
- **tdf_5knot − tdf_3knot improvement (positive = 5 better):** -2.06 km/s
- **TDF failure scope:** all_tdf_failure
- **Mixed subtype:** near_tie_mixed_case
- **Radial region:** outer_radius_tension
- **Baryonic context:** median v_bulge/v_bar=0.000, frac negative residual_v²=0.00
- **Interpretation:** Near-tie mixed case: NFW marginally best on holdout (~2.7 vs tdf_3knot ~3.0 km/s); tdf_5knot worse than tdf_3knot on holdout. Not a flex-recovery case; exclude from expansion_20 success claims until holdout stabilizes.

### UGC05253 (mixed_result)

- **Holdout RMSE (km/s):** tdf_3knot=48.52, tdf_5knot=16.46, NFW=36.15, MOND=37.38
- **Best holdout model:** tdf_5knot
- **tdf_5knot − tdf_3knot improvement (positive = 5 better):** 32.05 km/s
- **TDF failure scope:** flex_recovery
- **Mixed subtype:** tdf_3knot_failure_tdf_5knot_recovery
- **Radial region:** inner_radius_residual_or_baryonic_tension
- **Baryonic context:** median v_bulge/v_bar=0.844, frac negative residual_v²=0.74
- **Interpretation:** Mixed case with tdf_3knot holdout failure vs NFW but tdf_5knot recovery on holdout; many radial points and split instability suggest caution. Classify as flex-recovery / unstable — needs blocked-split or residual-map review before expansion_20.

## UGC00128 and UGC05253 classification

- **UGC00128:** near-tie mixed case; NFW marginally best on holdout; tdf_5knot does not recover. Baseline-dominated / near-tie — not flex-recovery.
- **UGC05253:** tdf_3knot fails vs NFW on holdout; tdf_5knot recovers (flex-recovery). High point count and split sensitivity → unstable classification needing more diagnostics before expansion_20.

## Figures

- `outputs/figures/sparc_subset/expansion12_failure_case_residuals.png`
- `outputs/figures/sparc_subset/expansion12_tdf3_vs_tdf5_gap.png`

## Claim boundaries

- Controlled expansion_12 audit only
- No new fits in this phase
- No full-SPARC validation
- No dark-matter disproof
- No lensing
- **tdf_3knot** remains primary; **tdf_5knot** sensitivity only

## Outputs

- `outputs/tables/expansion12_failure_diagnostics.csv`
- `outputs/tables/expansion12_case_review_summary.csv`
