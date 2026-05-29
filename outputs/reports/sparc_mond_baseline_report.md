# SPARC MOND/RAR Baseline Report (Phase 3M)

This phase adds MOND/RAR as an empirical rotation-curve baseline only. It does not fit or validate TDF, does not disprove dark matter, and does not establish MOND as a complete replacement for ΛCDM.

- Selected galaxies: DDO154, NGC2403, NGC3198, NGC6503, IC2574, NGC7814

## Formulas

- Simple MOND: `nu(y) = 0.5 + sqrt(0.25 + 1/y)` with `y = g_bar / a0`, `g_obs = nu(y) * g_bar`
- RAR (optional): `g_obs = g_bar / (1 - exp(-sqrt(g_bar / g_dagger)))`

## Unit conversions

- `r_m = r_kpc * 3.085677581e19`
- `v_ms = v_kms * 1000`
- `g_bar = v_bar^2 / r` (m/s²)
- `v_model_kms = sqrt(g_obs * r_m) / 1000`

## Parameters

- Fixed a0: `1.2e-10` m/s²
- Fitted log10(a0) bounds: `[-11.5, -9.5]`
- `mond_fixed_a0_simple`: n_parameters = 0
- `mond_fit_a0_simple`: n_parameters = 1
- `rar_fixed`: n_parameters = 0 (if enabled)

## Cautions

- No stellar M/L fitting in this phase.
- Baryonic decomposition is fixed from SPARC rotmod columns.
- Distance and inclination are not fitted.

## Fit success

| Galaxy | Model | fit_success | fit_status | RMSE | AIC |
| --- | --- | --- | --- | ---: | ---: |
| DDO154 | mond_fit_a0_simple | True | ok:4 | 4.20 | 289.4 |
| DDO154 | mond_fixed_a0_simple | True | fixed_a0 | 6.77 | 2385.7 |
| DDO154 | rar_fixed | True | fixed_g_dagger | 6.74 | 2359.1 |
| IC2574 | mond_fit_a0_simple | True | ok:2 | 5.93 | 973.8 |
| IC2574 | mond_fixed_a0_simple | True | fixed_a0 | 20.71 | 18740.2 |
| IC2574 | rar_fixed | True | fixed_g_dagger | 20.67 | 18667.4 |
| NGC2403 | mond_fit_a0_simple | True | ok:2 | 13.97 | 5976.0 |
| NGC2403 | mond_fixed_a0_simple | True | fixed_a0 | 19.40 | 23692.1 |
| NGC2403 | rar_fixed | True | fixed_g_dagger | 18.34 | 21323.6 |
| NGC3198 | mond_fit_a0_simple | True | ok:2 | 15.21 | 1307.9 |
| NGC3198 | mond_fixed_a0_simple | True | fixed_a0 | 36.04 | 12971.9 |
| NGC3198 | rar_fixed | True | fixed_g_dagger | 35.00 | 12186.8 |
| NGC6503 | mond_fit_a0_simple | True | ok:2 | 12.44 | 1024.9 |
| NGC6503 | mond_fixed_a0_simple | True | fixed_a0 | 25.20 | 8005.8 |
| NGC6503 | rar_fixed | True | fixed_g_dagger | 24.36 | 7621.1 |
| NGC7814 | mond_fit_a0_simple | True | ok:2 | 32.07 | 241.3 |
| NGC7814 | mond_fixed_a0_simple | True | fixed_a0 | 35.05 | 422.0 |
| NGC7814 | rar_fixed | True | fixed_g_dagger | 31.90 | 320.2 |

## Best by galaxy (AIC)

- DDO154: mond_fit_a0_simple (AIC=289.4, RMSE=4.20)
- IC2574: mond_fit_a0_simple (AIC=973.8, RMSE=5.93)
- NGC2403: mond_fit_a0_simple (AIC=5976.0, RMSE=13.97)
- NGC3198: mond_fit_a0_simple (AIC=1307.9, RMSE=15.21)
- NGC6503: mond_fit_a0_simple (AIC=1024.9, RMSE=12.44)
- NGC7814: mond_fit_a0_simple (AIC=241.3, RMSE=32.07)

## Fitted a0 values

| Galaxy | log10_a0 | a0 [m/s²] |
| --- | ---: | ---: |
| DDO154 | -10.1072 | 7.812e-11 |
| NGC2403 | -10.1731 | 6.712e-11 |
| NGC3198 | -10.5170 | 3.041e-11 |
| NGC6503 | -10.3084 | 4.916e-11 |
| IC2574 | -10.8569 | 1.390e-11 |
| NGC7814 | -10.0923 | 8.086e-11 |

## Outputs
- `outputs/tables/sparc_mond_model_comparison.csv`
- `outputs/tables/sparc_mond_fit_parameters.csv`
