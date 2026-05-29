# SPARC Radial Tau Reconstruction Report (Phase 2A)

## Scope

This phase reconstructs radial τ-profiles from rotation residuals only. It does not compare TDF against NFW or Burkert, does not validate TDF on SPARC, and does not disprove dark matter.

## Run settings

- Selected galaxies processed: DDO154, NGC2403, NGC3198, NGC6503, IC2574, NGC7814
- K_tau: 1.0
- Negative residual policy: allow_signed
- Integration boundary: tau_at_r_min_zero
- Smoothing enabled: True
- Smoothing method: gaussian
- Smoothing sigma_points: 1.0
- Smoothing diagnostic_only: True

## Per-galaxy summary

| Galaxy | n_points | n_neg_residual | neg_fraction | dτ/dr min | dτ/dr max | τ min | τ max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DDO154 | 12 | 0 | 0.000 | 50.85 | 478.9 | 0 | 2084 |
| NGC2403 | 73 | 28 | 0.384 | -1117 | 1106 | -1007 | 1.433e+04 |
| NGC3198 | 43 | 10 | 0.233 | -1.065e+04 | 676.7 | -6521 | 1.304e+04 |
| NGC6503 | 31 | 4 | 0.129 | -3658 | 1199 | -6048 | 5122 |
| IC2574 | 34 | 0 | 0.000 | 16.61 | 342.8 | 0 | 1963 |
| NGC7814 | 18 | 5 | 0.278 | -8.02e+04 | 1544 | -7.756e+04 | 0 |

## Generated tables

- `outputs/tables/sparc_subset_tau_profiles.csv`
- `outputs/tables/tau_profiles/DDO154_tau_profile.csv`
- `outputs/tables/tau_profiles/NGC2403_tau_profile.csv`
- `outputs/tables/tau_profiles/NGC3198_tau_profile.csv`
- `outputs/tables/tau_profiles/NGC6503_tau_profile.csv`
- `outputs/tables/tau_profiles/IC2574_tau_profile.csv`
- `outputs/tables/tau_profiles/NGC7814_tau_profile.csv`

## Generated figures

- `outputs/figures/sparc_subset/DDO154_rotation_baryonic_residual.png`
- `outputs/figures/sparc_subset/DDO154_tau_gradient.png`
- `outputs/figures/sparc_subset/DDO154_tau_profile.png`
- `outputs/figures/sparc_subset/NGC2403_rotation_baryonic_residual.png`
- `outputs/figures/sparc_subset/NGC2403_tau_gradient.png`
- `outputs/figures/sparc_subset/NGC2403_tau_profile.png`
- `outputs/figures/sparc_subset/NGC3198_rotation_baryonic_residual.png`
- `outputs/figures/sparc_subset/NGC3198_tau_gradient.png`
- `outputs/figures/sparc_subset/NGC3198_tau_profile.png`
- `outputs/figures/sparc_subset/NGC6503_rotation_baryonic_residual.png`
- `outputs/figures/sparc_subset/NGC6503_tau_gradient.png`
- `outputs/figures/sparc_subset/NGC6503_tau_profile.png`
- `outputs/figures/sparc_subset/IC2574_rotation_baryonic_residual.png`
- `outputs/figures/sparc_subset/IC2574_tau_gradient.png`
- `outputs/figures/sparc_subset/IC2574_tau_profile.png`
- `outputs/figures/sparc_subset/NGC7814_rotation_baryonic_residual.png`
- `outputs/figures/sparc_subset/NGC7814_tau_gradient.png`
- `outputs/figures/sparc_subset/NGC7814_tau_profile.png`
