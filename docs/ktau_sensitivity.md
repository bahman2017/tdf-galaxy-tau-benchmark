# K_tau Sensitivity on Photometry-Informed M/L Harness (Phase 4L)

Phase 4L tests whether six-galaxy TDF conclusions under **Phase 4K photometry-informed prior weighting** are stable when **K_tau** is varied as a **fixed normalization convention**. Knot amplitudes are refit at each K_tau; K_tau is **not** fitted.

## Inputs

- Phase 4G scaled holdout grid (`sparc_ml_scaled_model_comparison.csv`) for **NFW/MOND reference** RMSE
- Phase 4K photometry-informed prior weights
- Standardized rotmod + six-galaxy subset

## K_tau values

Default: `0.5`, `1.0`, `2.0` (`configs/reconstruction.yaml` → `photometry_prior_ktau_sensitivity`).

Optional extended values `0.25`, `4.0` via `--include-optional-ktau`.

## Command

```bash
python3 scripts/run_photometry_prior_ktau_sensitivity.py
```

## Outputs

- `outputs/tables/sparc_ktau_sensitivity_summary.csv`
- `outputs/tables/ngc7814_ktau_sensitivity.csv`
- `outputs/reports/sparc_ktau_sensitivity_report.md`
- Figures under `outputs/figures/sparc_subset/`

## Interpretation guardrails

- K_tau is partially degenerate with dτ/dr amplitude.
- NGC7814 remains a **canonical tdf_3knot failure** at M/L=1 regardless of K_tau audit.
- **tdf_5knot** diagnostic recovery language must be distinguished from primary **tdf_3knot** claims.
