# SPARC Baseline Model Comparison Report (Phase 3A)

This phase fits baryonic-only, NFW, and Burkert baselines only. It does not fit or validate the TDF model. It does not claim that dark matter is disproven.

- Selected galaxies processed: DDO154, NGC2403, NGC3198, NGC6503, IC2574, NGC7814
- Fitting method: least_squares
- NFW bounds: rho_s=[100000.0, 1000000000.0], r_s=[0.1, 100.0]
- Burkert bounds: rho_0=[100000.0, 1000000000.0], r_0=[0.1, 100.0]

## Fit notes
- No fit failures

## Outputs
- `outputs/tables/sparc_baseline_model_comparison.csv`
- `outputs/tables/sparc_baseline_fit_parameters.csv`
- `outputs/figures/sparc_subset/*_baseline_rotation_comparison.png`
