# SPARC Baseline Robust Refit Report (Phase 3A-R)

This is a **baseline-only** robustness improvement. TDF is **not** fitted in this phase.
Phase 3A legacy outputs were **not** deleted or overwritten.

## Method

- Log-space halo parameters (`log10_rho`, `log10_r`) with physical-unit outputs.
- Wider documented bounds in `configs/models.yaml` under `robust_fit`.
- Deterministic multistart (3 corner guesses + 1 data-informed guess); lowest chi-square kept.
- Baryonic-only model unchanged from Phase 3A.

- Selected galaxies: DDO154, NGC2403, NGC3198, NGC6503, IC2574, NGC7814
- NFW log bounds: log10_rho_s=[2.0, 11.0], log10_r_s=[-1.3, 3.0]
- NFW physical bounds (derived): rho_s=[100.0, 100000000000.0], r_s=[0.05011872336272722, 1000.0]
- Burkert log bounds: log10_rho_0=[2.0, 11.0], log10_r_0=[-1.3, 3.0]

## Legacy vs refit summary

- Halo fits with improved boundary status: **4** / 12
- Halo fits with improved chi-square status: **0** / 12
- NFW galaxies with lower RMSE after refit: **6** / 6
- Burkert galaxies with lower RMSE after refit: **6** / 6

## Refit audit (post-fit)

- Boundary-limited rows (refit): **8**
- High reduced chi-square rows (refit): **18**

## Interpretation boundary

- NFW and Burkert remain **comparison baselines**, not proof of dark matter and not disproof of TDF.
- Worse or unstable refit results are reported explicitly; the goal is fairness and traceability.

## Outputs
- `outputs/tables/sparc_baseline_model_comparison_refit.csv`
- `outputs/tables/sparc_baseline_fit_parameters_refit.csv`
- `outputs/tables/sparc_baseline_legacy_vs_refit_delta.csv`
- `outputs/figures/sparc_subset/*_baseline_rotation_comparison_refit.png`
