# Project Status

## Current phase

**Phase 0B — scaffold hardening and unit-policy stabilization**

## Completed tasks

- Added unit-explicit schema conventions (`r_kpc`, `v_*_kms`, `*_kms2`).
- Implemented configurable negative residual policy in reconstruction.
- Hardened radial reconstruction safeguards (`K_tau > 0`, radius non-negative guard).
- Updated docs for conservative interpretation and mock-data boundaries.
- Added tests for policy behavior and mock-data warning emission.

## Current blockers

- Real SPARC ingestion and provenance audit not yet implemented in this repo.
- Model fitting beyond baryonic-only baseline remains scaffold stage.

## Next recommended tasks

1. Implement reproducible SPARC subset ingestion with explicit provenance logs.
2. Add NFW/Burkert fit routines and parameter constraints.
3. Add failure-mode diagnostics across residual policies and smoothing options.

## Latest validation/test results

- `python3 -m pytest -q`: `8 passed in 2.11s`
- `python3 scripts/run_sparc_subset.py --config configs/sparc_subset.yaml`: completed successfully and printed mock-data warning

## Latest generated outputs

- `outputs/tables/sparc_subset_tau_profiles.csv`
- `outputs/tables/model_comparison.csv`
- `outputs/reports/mock_data_warning.txt`
- `outputs/figures/*_rotation.png`, `outputs/figures/*_tau.png`

## Mock-data claim boundary

**No observational claim can be made from mock data.**
