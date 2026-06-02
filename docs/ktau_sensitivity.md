# Legacy K_tau (K_g projection) sensitivity on photometry-informed M/L harness (Phase 4L)

> **Notation:** Phase 4L and frozen CSVs use **K_tau** as the historical benchmark label for the fixed **gravitational projection coefficient** (\(K_g\) in updated TDF prose). **κ_tau** denotes mother-field stiffness and is **not** varied in this phase. See `docs/theory_summary.md`.

Phase 4L tests whether six-galaxy TDF conclusions under **Phase 4K photometry-informed prior weighting** are stable when legacy **K_tau** is varied as a **fixed normalization convention**. Knot amplitudes are refit at each K_tau; K_tau is **not** fitted.

## Scope

- Six-galaxy controlled subset only
- Photometry-informed prior scenarios from Phase 4K
- TDF knot amplitude refit only; NFW/MOND holdout RMSE from Phase 4G grid

## K_tau values (legacy label; K_g-like role)

`{0.5, 1.0, 2.0}` — config key `K_tau` unchanged in frozen outputs

## Key outputs

- `outputs/tables/sparc_ktau_sensitivity_summary.csv`
- `outputs/tables/sparc_tdf_ktau_sensitivity.csv`
- `outputs/tables/ngc7814_ktau_sensitivity.csv`
- `outputs/reports/sparc_ktau_sensitivity_report.md`

## Command

```bash
python3 scripts/run_photometry_prior_ktau_sensitivity.py
```

## Interpretation

- Legacy **K_tau** is partially degenerate with dτ/dr amplitude.
- NGC7814 remains a **canonical tdf_3knot failure** at M/L=1 regardless of K_tau audit.
- Qualitative six-galaxy claims stable over tested values; not a measurement of \(K_g\) or κ_tau.

## Claim boundaries

- Not full-SPARC validation
- No dark-matter disproof; no ΛCDM replacement
- Lensing not tested
- No final M/L calibration
