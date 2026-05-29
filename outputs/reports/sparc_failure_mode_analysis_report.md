# SPARC Failure-Mode Analysis Report (Phase 4A)

This audit evaluates success cases and failure modes for the six-galaxy controlled SPARC TDF benchmark. It does not validate TDF on full SPARC, does not disprove dark matter, does not replace ΛCDM, and does not include lensing or independent dynamical evidence.

- Galaxies classified as **robust_tdf_success**: **5**
- Galaxies classified as **tdf_failure_mode**: **1**
- Primary holdout reference split: `even_odd_index`

## Per-galaxy summary

| Galaxy | classification | in-sample AIC best | holdout RMSE best | tdf_3knot HO | NFW HO | MOND HO |
| --- | --- | --- | --- | ---: | ---: | ---: |
| DDO154 | robust_tdf_success | tdf_5knot | tdf_5knot | 2.03 | 3.56 | 3.98 |
| IC2574 | robust_tdf_success | tdf_5knot | tdf_5knot | 2.98 | 6.39 | 6.29 |
| NGC2403 | robust_tdf_success | tdf_5knot | tdf_5knot | 8.66 | 9.76 | 14.24 |
| NGC3198 | robust_tdf_success | tdf_5knot | tdf_5knot | 10.45 | 12.00 | 14.34 |
| NGC6503 | robust_tdf_success | tdf_5knot | tdf_5knot | 9.33 | 10.14 | 12.39 |
| NGC7814 | tdf_failure_mode | tdf_5knot | nfw_refit | 155.80 | 24.89 | 27.85 |

## NGC7814 — dedicated failure-mode investigation

NGC7814 remains in the benchmark as an **honest failure mode**. It is not removed or hidden.

### Observations

- **In-sample:** best by AIC/BIC is `tdf_5knot` (TDF knot variant).
- **Holdout (even_odd_index):** best test RMSE is `nfw_refit` (not TDF).
- tdf_3knot holdout RMSE ≈ **155.8 km/s** vs NFW ≈ **24.9** and MOND fit-a0 ≈ **27.8 km/s**.
- **Negative v² flags:** `tdf_4knot` (tdf_4knot pathological).
- **Smoothness (diagnostic):** tdf_3knot:norm=319.2; tdf_4knot:norm=3.423e+05; tdf_5knot:norm=2.277e+04

### Interpretation

TDF performs well **in-sample** but **fails holdout** on this galaxy. The tdf_4knot variant shows negative-v² pathology and very poor RMSE in-sample. NFW and MOND outperform TDF on holdout test RMSE.

### Possible causes to investigate later (not resolved in Phase 4A)

- Bulge dominance and fixed SPARC baryonic decomposition (no M/L fitting)
- Radial structure / limited azimuthal information in 1D curves
- Fixed knot placement rules vs galaxy morphology
- Fixed K_tau convention (partial degeneracy with dτ/dr amplitude)
- Geometry / inclination not fitted
- Insufficient regularization for higher knot counts

### Reporting guidance

Do **not** claim that TDF works for NGC7814 under holdout validation. Report it as **one clear failure mode** among six subset galaxies.

## Success cases (robust_tdf_success)

- **DDO154**: TDF knot models are competitive with or better than tested baselines on this galaxy under both in-sample metrics and even/odd holdout test RMSE (conditional on fixed baryons and K_tau).
- **NGC2403**: TDF knot models are competitive with or better than tested baselines on this galaxy under both in-sample metrics and even/odd holdout test RMSE (conditional on fixed baryons and K_tau).
- **NGC3198**: TDF knot models are competitive with or better than tested baselines on this galaxy under both in-sample metrics and even/odd holdout test RMSE (conditional on fixed baryons and K_tau).
- **NGC6503**: TDF knot models are competitive with or better than tested baselines on this galaxy under both in-sample metrics and even/odd holdout test RMSE (conditional on fixed baryons and K_tau).
- **IC2574**: TDF knot models are competitive with or better than tested baselines on this galaxy under both in-sample metrics and even/odd holdout test RMSE (conditional on fixed baryons and K_tau).

## Outputs
- `outputs/tables/sparc_failure_mode_summary.csv`
- `outputs/reports/sparc_failure_mode_analysis_report.md`
