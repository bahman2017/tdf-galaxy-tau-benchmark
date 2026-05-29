# SPARC Full Model Comparison Report (Phase 3B)

The TDF knot model is a low-parameter radial reconstruction model for rotation-curve residuals. This phase does not disprove dark matter, does not replace ΛCDM, does not validate TDF on full SPARC, and does not use lensing or independent dynamical evidence.

- Selected galaxies: DDO154, NGC2403, NGC3198, NGC6503, IC2574, NGC7814
- Fixed K_tau: 1.0
- Knot amplitude bounds (example galaxy): [-163.2, 693] (×2.0 safety on Phase 2A dτ/dr range)

## Fitted models

- baryonic_only, nfw_refit, burkert_refit, mond_fixed_a0_simple, mond_fit_a0_simple, rar_fixed
- tdf_3knot (primary), tdf_4knot, tdf_5knot (sensitivity)

## Knot placement (fixed, not fitted)

- 3-knot: r_min, r_mid, r_max
- 4-knot: r_min, r_min+span/3, r_min+2span/3, r_max
- 5-knot: r_min, r_min+span/4, r_mid, r_min+3span/4, r_max

## Parameter counts

- tdf_3knot: 3; tdf_4knot: 4; tdf_5knot: 5 (K_tau and knot radii not counted)

## Caveats

- Phase 2A direct τ reconstruction is diagnostic only (not in AIC/BIC table).
- Fixed SPARC baryonic decomposition; no stellar M/L fitting.
- Halo refit reduced boundary issues; high reduced chi-square may persist.
- Fitted MOND a0 often below canonical 1.2×10⁻¹⁰ m/s² in this setup.
- tdf_4knot / tdf_5knot have higher parameter count — interpret overfitting risk cautiously.
- Negative v_tau² regions may occur; fitting applies penalties when v_model² < 0.

## Fit summary

| Galaxy | Model | success | RMSE | AIC | red. χ² |
| --- | --- | --- | ---: | ---: | ---: |
| DDO154 | tdf_5knot | True | 0.41 | 14.2 | 0.69 |
| DDO154 | tdf_4knot | True | 0.78 | 20.9 | 1.85 |
| DDO154 | tdf_3knot | True | 1.59 | 42.0 | 4.50 |
| DDO154 | nfw_refit | True | 3.46 | 170.7 | 18.52 |
| DDO154 | mond_fit_a0_simple | True | 4.20 | 289.4 | 28.74 |
| DDO154 | burkert_refit | True | 11.32 | 2333.9 | 258.88 |
| DDO154 | rar_fixed | True | 6.74 | 2359.1 | 214.47 |
| DDO154 | mond_fixed_a0_simple | True | 6.77 | 2385.7 | 216.88 |
| DDO154 | baryonic_only | True | 22.68 | 65173.2 | 5924.84 |
| IC2574 | tdf_5knot | True | 1.85 | 21.5 | 0.41 |
| IC2574 | tdf_4knot | True | 2.22 | 73.6 | 2.26 |
| IC2574 | tdf_3knot | True | 2.62 | 84.5 | 2.62 |
| IC2574 | mond_fit_a0_simple | True | 5.93 | 973.8 | 30.37 |
| IC2574 | nfw_refit | True | 5.89 | 1129.5 | 36.31 |
| IC2574 | burkert_refit | True | 16.42 | 6162.7 | 198.67 |
| IC2574 | baryonic_only | True | 18.90 | 7407.3 | 224.46 |
| IC2574 | rar_fixed | True | 20.67 | 18667.4 | 565.68 |
| IC2574 | mond_fixed_a0_simple | True | 20.71 | 18740.2 | 567.88 |
| NGC2403 | tdf_5knot | True | 3.34 | 422.1 | 6.15 |
| NGC2403 | tdf_4knot | True | 5.24 | 1221.3 | 17.84 |
| NGC2403 | tdf_3knot | True | 8.77 | 2678.2 | 38.73 |
| NGC2403 | nfw_refit | True | 9.75 | 2890.3 | 41.23 |
| NGC2403 | mond_fit_a0_simple | True | 13.97 | 5976.0 | 84.14 |
| NGC2403 | rar_fixed | True | 18.34 | 21323.6 | 296.16 |
| NGC2403 | mond_fixed_a0_simple | True | 19.40 | 23692.1 | 329.06 |
| NGC2403 | burkert_refit | True | 30.05 | 31819.1 | 454.50 |
| NGC2403 | baryonic_only | True | 37.90 | 149504.9 | 2076.46 |
| NGC3198 | tdf_5knot | True | 9.87 | 72.5 | 1.69 |
| NGC3198 | tdf_4knot | True | 10.20 | 98.0 | 2.37 |
| NGC3198 | tdf_3knot | True | 11.58 | 323.3 | 8.14 |
| NGC3198 | nfw_refit | True | 13.02 | 635.1 | 15.78 |
| NGC3198 | mond_fit_a0_simple | True | 15.21 | 1307.9 | 31.85 |
| NGC3198 | burkert_refit | True | 33.06 | 4785.3 | 119.53 |
| NGC3198 | rar_fixed | True | 35.00 | 12186.8 | 290.16 |
| NGC3198 | baryonic_only | True | 37.61 | 12645.3 | 301.08 |
| NGC3198 | mond_fixed_a0_simple | True | 36.04 | 12971.9 | 308.85 |
| NGC6503 | tdf_5knot | True | 6.49 | 226.9 | 8.67 |
| NGC6503 | tdf_4knot | True | 7.69 | 369.9 | 13.92 |
| NGC6503 | tdf_3knot | True | 9.51 | 577.9 | 21.18 |
| NGC6503 | nfw_refit | True | 10.49 | 705.4 | 25.05 |
| NGC6503 | mond_fit_a0_simple | True | 12.44 | 1024.9 | 35.27 |
| NGC6503 | burkert_refit | True | 19.97 | 2354.5 | 83.95 |
| NGC6503 | rar_fixed | True | 24.36 | 7621.1 | 254.04 |
| NGC6503 | mond_fixed_a0_simple | True | 25.20 | 8005.8 | 266.86 |
| NGC6503 | baryonic_only | True | 41.67 | 25645.1 | 854.84 |
| NGC7814 | tdf_5knot | True | 17.44 | 41.0 | 2.58 |
| NGC7814 | tdf_3knot | True | 25.27 | 102.0 | 6.86 |
| NGC7814 | nfw_refit | True | 29.62 | 162.3 | 10.56 |
| NGC7814 | mond_fit_a0_simple | True | 32.07 | 241.3 | 14.95 |
| NGC7814 | rar_fixed | True | 31.90 | 320.2 | 18.84 |
| NGC7814 | mond_fixed_a0_simple | True | 35.05 | 422.0 | 24.82 |
| NGC7814 | burkert_refit | True | 43.01 | 509.0 | 33.67 |
| NGC7814 | baryonic_only | True | 53.46 | 2811.5 | 165.38 |
| NGC7814 | tdf_4knot | True | 123.31 | 6335.1 | 486.70 |

## Best model per galaxy

- **DDO154**: RMSE=tdf_5knot, AIC=tdf_5knot, BIC=tdf_5knot; tdf_3knot beats NFW (AIC)=True, beats MOND fit-a0 (AIC)=True
- **IC2574**: RMSE=tdf_5knot, AIC=tdf_5knot, BIC=tdf_5knot; tdf_3knot beats NFW (AIC)=True, beats MOND fit-a0 (AIC)=True
- **NGC2403**: RMSE=tdf_5knot, AIC=tdf_5knot, BIC=tdf_5knot; tdf_3knot beats NFW (AIC)=True, beats MOND fit-a0 (AIC)=True
- **NGC3198**: RMSE=tdf_5knot, AIC=tdf_5knot, BIC=tdf_5knot; tdf_3knot beats NFW (AIC)=True, beats MOND fit-a0 (AIC)=True
- **NGC6503**: RMSE=tdf_5knot, AIC=tdf_5knot, BIC=tdf_5knot; tdf_3knot beats NFW (AIC)=True, beats MOND fit-a0 (AIC)=True
- **NGC7814**: RMSE=tdf_5knot, AIC=tdf_5knot, BIC=tdf_5knot; tdf_3knot beats NFW (AIC)=True, beats MOND fit-a0 (AIC)=True

## Outputs
- `outputs/tables/sparc_full_model_comparison.csv`
- `outputs/tables/sparc_best_model_summary.csv`
- `outputs/figures/sparc_subset/*_full_model_rotation_comparison.png`
