# Phase 6C primary-pilot smoothness and consistency audit

**Map version:** phase_6c_b_v1
**Primary pilots:** 5 galaxies

## Summary counts

- Radial consistency PASS: **5/5**
- Smoothness PASS (threshold 0.25): **0/5**
- Ready for Phase 6D second-channel scaffold: **0/5**

## Per-galaxy classification

| galaxy_id   |   grid_nx |   grid_ny |   r_min_kpc |   r_max_kpc |   r_outer_kpc |   K_g |   legacy_K_tau_value | tau_retuned   | kg_retuned   | separate_halo_added   | lensing_confirmed   | true_2d_sigma_b   |   radial_consistency_max_relative_error | radial_consistency_pass   |   smoothness_metric |   smoothness_dtaudr_jump |   smoothness_grad_jump | smoothness_pass   |   smoothness_threshold | smoothness_failure_inherited_from_frozen_1d_profile   | phase6c_ready_for_second_channel_scaffold   | phase6c_not_ready_reason                                         |
|:------------|----------:|----------:|------------:|------------:|--------------:|------:|---------------------:|:--------------|:-------------|:----------------------|:--------------------|:------------------|----------------------------------------:|:--------------------------|--------------------:|-------------------------:|-----------------------:|:------------------|-----------------------:|:------------------------------------------------------|:--------------------------------------------|:-----------------------------------------------------------------|
| DDO161      |       101 |       101 |        0.6  |       13.37 |       14.0385 |     1 |                    1 | False         | False        | False                 | False               | False             |                                       0 | True                      |           10.8452   |                10.8452   |               0.62933  | False             |                   0.25 | True                                                  | False                                       | smoothness failed: inherited frozen 1D dτ/dr jumps (no retuning) |
| UGC07524    |       101 |       101 |        0.35 |       10.69 |       11.2245 |     1 |                    1 | False         | False        | False                 | False               | False             |                                       0 | True                      |            5.3451   |                 5.3451   |               1.48801  | False             |                   0.25 | True                                                  | False                                       | smoothness failed: inherited frozen 1D dτ/dr jumps (no retuning) |
| UGC08490    |       101 |       101 |        0.34 |       10.15 |       10.6575 |     1 |                    1 | False         | False        | False                 | False               | False             |                                       0 | True                      |            0.383294 |                 0.383294 |               0.318093 | False             |                   0.25 | True                                                  | False                                       | smoothness failed: inherited frozen 1D dτ/dr jumps (no retuning) |
| IC2574      |       101 |       101 |        0.85 |       10.23 |       10.7415 |     1 |                    1 | False         | False        | False                 | False               | False             |                                       0 | True                      |            2.41575  |                 2.41575  |               1.59958  | False             |                   0.25 | True                                                  | False                                       | smoothness failed: inherited frozen 1D dτ/dr jumps (no retuning) |
| NGC2403     |       101 |       101 |        0.16 |       20.87 |       21.9135 |     1 |                    1 | False         | False        | False                 | False               | False             |                                       0 | True                      |          116.125    |               116.125    |               6.06175  | False             |                   0.25 | True                                                  | False                                       | smoothness failed: inherited frozen 1D dτ/dr jumps (no retuning) |

## Phase 6D gate

**Phase 6D is blocked** — no primary pilot passes both radial consistency and smoothness.

**Recommended next step:** Phase **6C-C** diagnostic review of frozen radial τ-gradient structure (regularization options documented only; no retuning in this repo phase).

## Claim boundaries

- Axisymmetric pseudo-2D only; not true 2D Σ_b.
- No new fit; no τ smoothing; no K_g retuning.
- No lensing confirmation; does not update Phase 5 expansion_20 (15/20).
- Smoothness FAIL reflects frozen `expansion20_tau_profiles.csv` when `smoothness_failure_inherited_from_frozen_1d_profile` is true.

## Reproducibility

```bash
python3 scripts/build_phase6c_frozen_pseudo2d_map.py --all-primary-pilots
```
