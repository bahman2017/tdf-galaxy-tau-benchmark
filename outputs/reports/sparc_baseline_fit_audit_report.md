# SPARC Baseline Fit Audit Report (Phase 3A-Audit)

This audit reviews Phase 3A baseline fits only. It does not fit or validate TDF and does not disprove dark matter.

## Executive summary

- **NFW has the lowest RMSE among baseline models for all six selected galaxies.**
- **NFW also has the best AIC and BIC among baseline models for all six galaxies.**
- Burkert fits flagged as boundary-limited: **6 / 6** rows.
- NFW fits flagged as boundary-limited: **6** rows.
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

- `boundary_limited_and_high_chi_square`: 12
- `high_chi_square`: 6

## Per-galaxy audit table

| Galaxy | Model | RMSE | red. chi2 | model_status | boundary flags |
| --- | --- | ---: | ---: | --- | --- |
| DDO154 | baryonic_only | 22.68 | 5924.84 | high_chi_square | none |
| DDO154 | burkert | 12.50 | 328.80 | boundary_limited_and_high_chi_square | rho_0_lower_bound |
| DDO154 | nfw | 3.46 | 18.52 | boundary_limited_and_high_chi_square | rho_s_lower_bound |
| IC2574 | baryonic_only | 18.90 | 224.46 | high_chi_square | none |
| IC2574 | burkert | 18.09 | 227.34 | boundary_limited_and_high_chi_square | rho_0_lower_bound |
| IC2574 | nfw | 6.36 | 41.40 | boundary_limited_and_high_chi_square | rho_s_lower_bound |
| NGC2403 | baryonic_only | 37.90 | 2076.46 | high_chi_square | none |
| NGC2403 | burkert | 33.59 | 570.07 | boundary_limited_and_high_chi_square | rho_0_lower_bound |
| NGC2403 | nfw | 9.75 | 41.23 | boundary_limited_and_high_chi_square | rho_s_lower_bound |
| NGC3198 | baryonic_only | 37.61 | 301.08 | high_chi_square | none |
| NGC3198 | burkert | 38.88 | 182.08 | boundary_limited_and_high_chi_square | rho_0_lower_bound |
| NGC3198 | nfw | 13.27 | 17.77 | boundary_limited_and_high_chi_square | rho_s_lower_bound, r_s_upper_bound |
| NGC6503 | baryonic_only | 41.67 | 854.84 | high_chi_square | none |
| NGC6503 | burkert | 23.32 | 114.61 | boundary_limited_and_high_chi_square | rho_0_lower_bound |
| NGC6503 | nfw | 10.49 | 25.05 | boundary_limited_and_high_chi_square | rho_s_lower_bound |
| NGC7814 | baryonic_only | 53.46 | 165.38 | high_chi_square | none |
| NGC7814 | burkert | 45.20 | 39.16 | boundary_limited_and_high_chi_square | rho_0_lower_bound |
| NGC7814 | nfw | 30.07 | 11.33 | boundary_limited_and_high_chi_square | rho_s_lower_bound, r_s_upper_bound |

## Outputs

- `outputs/tables/sparc_baseline_fit_audit.csv`
- `outputs/reports/sparc_baseline_fit_audit_report.md`
