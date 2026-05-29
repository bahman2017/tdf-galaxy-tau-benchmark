# SPARC Baseline Fit Audit Report (Phase 3A-R refit audit)

This audit reviews Phase 3A baseline fits only. It does not fit or validate TDF and does not disprove dark matter.

## Executive summary

- **NFW has the lowest RMSE among baseline models for all six selected galaxies.**
- **NFW also has the best AIC and BIC among baseline models for all six galaxies.**
- Burkert fits flagged as boundary-limited: **6 / 6** rows.
- NFW fits flagged as boundary-limited: **2** rows.
- Rows with reduced chi-square > 5.0: **18**.
- Rows with reduced chi-square > 20.0: **15**.

## Caveats before TDF comparison

- Burkert is numerically fit-successful in Phase 3A but often boundary-limited (especially `rho_0` at the lower bound).
- Several NFW solutions are near or at parameter bounds (`r_s` upper bound and/or `rho_s` lower bound).
- Baryonic-only and some halo baselines show very high reduced chi-square; interpret metrics with caution.
- These baseline caveats must be carried forward before any Phase 3B TDF knot comparison.

## Audit configuration

- Boundary tolerance: 1.0% of allowed parameter range
- High reduced chi-square threshold: 5.0
- Very high reduced chi-square threshold: 20.0
- Poor RMSE threshold: 20% of median v_obs

## Model status counts

- `boundary_limited_and_high_chi_square`: 8
- `high_chi_square`: 10

## Per-galaxy audit table

| Galaxy | Model | RMSE | red. chi2 | model_status | boundary flags |
| --- | --- | ---: | ---: | --- | --- |
| DDO154 | baryonic_only | 22.68 | 5924.84 | high_chi_square | none |
| DDO154 | burkert | 11.32 | 258.88 | boundary_limited_and_high_chi_square | rho_0_lower_bound |
| DDO154 | nfw | 3.46 | 18.52 | high_chi_square | none |
| IC2574 | baryonic_only | 18.90 | 224.46 | high_chi_square | none |
| IC2574 | burkert | 16.42 | 198.67 | boundary_limited_and_high_chi_square | rho_0_lower_bound |
| IC2574 | nfw | 5.89 | 36.31 | boundary_limited_and_high_chi_square | r_s_upper_bound |
| NGC2403 | baryonic_only | 37.90 | 2076.46 | high_chi_square | none |
| NGC2403 | burkert | 30.05 | 454.50 | boundary_limited_and_high_chi_square | rho_0_lower_bound |
| NGC2403 | nfw | 9.75 | 41.23 | high_chi_square | none |
| NGC3198 | baryonic_only | 37.61 | 301.08 | high_chi_square | none |
| NGC3198 | burkert | 33.06 | 119.53 | boundary_limited_and_high_chi_square | rho_0_lower_bound |
| NGC3198 | nfw | 13.02 | 15.78 | high_chi_square | none |
| NGC6503 | baryonic_only | 41.67 | 854.84 | high_chi_square | none |
| NGC6503 | burkert | 19.97 | 83.95 | boundary_limited_and_high_chi_square | rho_0_lower_bound |
| NGC6503 | nfw | 10.49 | 25.05 | high_chi_square | none |
| NGC7814 | baryonic_only | 53.46 | 165.38 | high_chi_square | none |
| NGC7814 | burkert | 43.01 | 33.67 | boundary_limited_and_high_chi_square | r_0_upper_bound |
| NGC7814 | nfw | 29.62 | 10.56 | boundary_limited_and_high_chi_square | r_s_upper_bound |

## Outputs

- `outputs/tables/sparc_baseline_fit_audit_refit.csv`
- `outputs/reports/sparc_baseline_fit_audit_refit_report.md`
