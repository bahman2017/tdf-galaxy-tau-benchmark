# Phase 6B pilot selection report

**Audit version:** phase_6b_v1
**Cohort:** expansion_20 (20 galaxies)

## Summary

- Tier-1 primary candidates: **9** galaxies
- Selected primary pilots (top 5 by score): **DDO161, UGC07524, UGC08490, IC2574, NGC2403**
- Phase 5 expansion_20 headline (**15/20**) unchanged; Phase 6 is a separate test layer.

## Pre-registered Phase 6C thresholds

| Parameter | Value |
| --- | --- |
| N_min radial points | 12 |
| Min radial coverage (kpc) | 5.0 |
| Inclination range (deg) | [30.0, 90.0] |
| Max extrapolation fraction beyond r_max | 0.05 |
| Max relative adjacent dτ/dr jump | 0.25 |
| τ radial match tolerance (relative) | 1e-06 |
| Max tdf_3knot holdout RMSE for primary pilot | 10.0 km/s |

## Map types (repo v0.1.6)

- **Axisymmetric pseudo-2D:** attemptable when L1–L3 satisfied
- **Sky-projected:** attemptable when L4 geometry complete
- **True 2D Σ_b:** future-only (no pixel maps in repo)
- **Lensing/deflection:** future-only; not confirmed

## Claim boundaries

No dark-matter disproof; no full-SPARC validation; no lensing confirmation; no universal τ profile; pseudo-2D ≠ true 2D.

## Reproducibility

```bash
python3 scripts/build_phase6b_data_availability_audit.py
```

## Primary pilot table

| audit_version   |   overall_rank | galaxy_id   | pilot_tier               | is_primary_pilot   |   pilot_rank_score | failure_mode_classification   | holdout_stable_for_primary_pilot   |   n_radial_points |   radial_coverage_kpc |   tdf_3knot_holdout_rmse_kms | geometry_complete_flag   | map_type_axisymmetric_pseudo_2d   | selection_rationale                           |
|:----------------|---------------:|:------------|:-------------------------|:-------------------|-------------------:|:------------------------------|:-----------------------------------|------------------:|----------------------:|-----------------------------:|:-------------------------|:----------------------------------|:----------------------------------------------|
| phase_6b_v1     |              1 | DDO161      | tier_1_primary_candidate | True               |           0.7248   | robust_tdf_success            | True                               |                31 |                 12.77 |                     0.715129 | True                     | attemptable                       | Phase 6B ranked primary pilot (top 5 tier-1). |
| phase_6b_v1     |              2 | UGC07524    | tier_1_primary_candidate | True               |           0.662195 | robust_tdf_success            | True                               |                31 |                 10.34 |                     1.63088  | True                     | attemptable                       | Phase 6B ranked primary pilot (top 5 tier-1). |
| phase_6b_v1     |              3 | UGC08490    | tier_1_primary_candidate | True               |           0.636519 | robust_tdf_success            | True                               |                30 |                  9.81 |                     1.13356  | True                     | attemptable                       | Phase 6B ranked primary pilot (top 5 tier-1). |
| phase_6b_v1     |              4 | IC2574      | tier_1_primary_candidate | True               |           0.622668 | robust_tdf_success            | True                               |                34 |                  9.38 |                     2.97936  | True                     | attemptable                       | Phase 6B ranked primary pilot (top 5 tier-1). |
| phase_6b_v1     |              5 | NGC2403     | tier_1_primary_candidate | True               |           0.603714 | robust_tdf_success            | True                               |                73 |                 20.71 |                     8.65888  | True                     | attemptable                       | Phase 6B ranked primary pilot (top 5 tier-1). |
