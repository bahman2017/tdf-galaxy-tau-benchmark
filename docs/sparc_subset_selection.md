# SPARC Subset Selection

## Phase 1B objective

Create a deterministic, controlled subset from `data/processed/sparc/sparc_rotmod_standardized.csv` for first real radial tau reconstruction tests.

This phase performs **selection and quality control only**.

## Deterministic criteria

- Minimum radial points per galaxy: 12
- Minimum radial coverage: > 5 kpc
- Require finite values for:
  - `r_kpc`, `v_obs_kms`, `v_err_kms`, `v_gas_kms`, `v_disk_kms`, `v_bulge_kms`, `v_bar_kms`, `residual_v2_kms2`
- Require positive values for:
  - `r_kpc`, `v_obs_kms`, `v_err_kms`
- Allow negative `residual_v2_kms2` and report counts/fractions

## Candidate-priority policy

Preferred candidates are attempted first (if they pass criteria):

- DDO154
- NGC2403
- NGC3198
- NGC6503
- IC2574
- NGC7814

If fewer than `max_selected_galaxies` pass from candidates, remaining slots are filled deterministically by quality-passing galaxies sorted by:
1. higher `n_points`
2. higher `radial_coverage_kpc`
3. alphabetical `galaxy_id`

## Why these galaxies

These candidates provide a practical starting mix of commonly used SPARC systems with differing rotation-curve structures and bulge/no-bulge characteristics, while keeping first-pass run scope small and reproducible.

## Output artifacts

- `outputs/tables/sparc_subset_selection.csv`
- `outputs/reports/sparc_subset_selection_report.md`

## Phase 2A usage

The six selected galaxies above are used for Phase 2A radial τ reconstruction (rotation-residual inference only):

- Outputs: `outputs/tables/sparc_subset_tau_profiles.csv`
- Per-galaxy tables: `outputs/tables/tau_profiles/`
- Diagnostics: `outputs/figures/sparc_subset/`

## Claim boundary

This is subset selection only. No TDF, NFW, Burkert, or dark-matter inference is made in this phase.
