# SPARC TDF Robustness Audit Report (Phase 3C)

This audit evaluates robustness of the six-galaxy rotation-curve TDF knot fits only. It does not validate TDF on full SPARC, does not disprove dark matter, does not replace ΛCDM, and does not include lensing or independent dynamical evidence.

## Knot-count stability (3 vs 5)

- Galaxies with ΔAIC(5−3) < −10.0 (large 5-knot gain): **6** / 6

| Galaxy | ΔAIC(5−3) | ΔRMSE(5−3) | 4-knot status |
| --- | ---: | ---: | --- |
| DDO154 | -27.8 | -1.18 | ok:2 |
| IC2574 | -63.0 | -0.77 | ok:2 |
| NGC2403 | -2256.2 | -5.43 | ok:2 |
| NGC3198 | -250.8 | -1.72 | ok:2 |
| NGC6503 | -351.0 | -3.02 | ok:2 |
| NGC7814 | -61.0 | -7.83 | ok:2;negative_v2_regions |

## Holdout validation (even/odd split summary)

- tdf_3knot beats nfw_refit on holdout test RMSE: **5** / 6 galaxies
- five_knot overfit risk flags: **0** / 6

| Galaxy | tdf_3knot test RMSE | tdf_5knot test RMSE | nfw test RMSE | mond fit test RMSE |
| --- | ---: | ---: | ---: | ---: |
| DDO154 | 2.03 | 1.44 | 3.56 | 3.98 |
| IC2574 | 2.98 | 1.73 | 6.39 | 6.29 |
| NGC2403 | 8.66 | 3.44 | 9.76 | 14.24 |
| NGC3198 | 10.45 | 8.24 | 12.00 | 14.34 |
| NGC6503 | 9.33 | 4.90 | 10.14 | 12.39 |
| NGC7814 | 155.80 | 113.25 | 24.89 | 27.85 |

## K_tau sensitivity (tdf_3knot, refitted)

K_tau is partially degenerate with dτ/dr amplitude; metrics should be compared cautiously.

| Galaxy | K_tau=0.5 RMSE | K_tau=1.0 RMSE | K_tau=2.0 RMSE |
| --- | ---: | ---: | ---: |
| DDO154 | 3.58 | 1.59 | 1.59 |
| IC2574 | 3.24 | 2.62 | 2.62 |
| NGC2403 | 8.77 | 8.77 | 8.77 |
| NGC3198 | 11.58 | 11.58 | 11.58 |
| NGC6503 | 9.51 | 9.51 | 9.51 |
| NGC7814 | 25.27 | 25.27 | 25.27 |

## Bounds safety-factor sensitivity (tdf_3knot)

| Galaxy | sf=1.0 | sf=1.5 | sf=2.0 | sf=3.0 |
| --- | ---: | ---: | ---: | ---: |
| DDO154 | 1.82 | 1.59 | 1.59 | 1.59 |
| IC2574 | 2.40 | 2.62 | 2.62 | 2.62 |
| NGC2403 | 8.77 | 8.77 | 8.77 | 8.77 |
| NGC3198 | 11.58 | 11.58 | 11.58 | 11.58 |
| NGC6503 | 9.51 | 9.51 | 9.51 | 9.51 |
| NGC7814 | 25.44 | 25.27 | 25.27 | 25.27 |

## Negative v² audit

- **NGC7814** / tdf_4knot: ok:2;negative_v2_regions

### NGC7814 tdf_4knot (explicit check)

- fit_status: `ok:2;negative_v2_regions`
- 4-knot fit can explore pathological amplitudes; prefer tdf_3knot for reporting unless holdout supports 4-knot.

## Smoothness diagnostics (diagnostic only, not fitted)

| Galaxy | model | smoothness (norm) | negative_v2 flag |
| --- | --- | ---: | --- |
| DDO154 | tdf_3knot | 65.3 | False |
| DDO154 | tdf_4knot | 223.1 | False |
| DDO154 | tdf_5knot | 353.1 | False |
| IC2574 | tdf_3knot | 0.08196 | False |
| IC2574 | tdf_4knot | 0.5336 | False |
| IC2574 | tdf_5knot | 8.068 | False |
| NGC2403 | tdf_3knot | 0.6085 | False |
| NGC2403 | tdf_4knot | 36.65 | False |
| NGC2403 | tdf_5knot | 144 | False |
| NGC3198 | tdf_3knot | 2.974 | False |
| NGC3198 | tdf_4knot | 14.26 | False |
| NGC3198 | tdf_5knot | 9.941 | False |
| NGC6503 | tdf_3knot | 2.831 | False |
| NGC6503 | tdf_4knot | 59.24 | False |
| NGC6503 | tdf_5knot | 154.7 | False |
| NGC7814 | tdf_3knot | 319.2 | False |
| NGC7814 | tdf_4knot | 3.423e+05 | True |
| NGC7814 | tdf_5knot | 2.277e+04 | False |

## Recommended reporting model (robust summary)

| Galaxy | recommended |
| --- | --- |
| DDO154 | tdf_5knot |
| IC2574 | tdf_5knot |
| NGC2403 | tdf_5knot |
| NGC3198 | tdf_5knot |
| NGC6503 | tdf_5knot |
| NGC7814 | tdf_5knot |

## Outputs
- `outputs/tables/sparc_tdf_robustness_summary.csv`
- `outputs/tables/sparc_tdf_holdout_validation.csv`
- `outputs/tables/sparc_tdf_ktau_sensitivity.csv`
- `outputs/tables/sparc_tdf_bounds_sensitivity.csv`
- `outputs/tables/sparc_tdf_smoothness_diagnostics.csv`
- `outputs/tables/sparc_tdf_robust_best_model_summary.csv`
