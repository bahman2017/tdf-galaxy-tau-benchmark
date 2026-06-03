# Phase 6C-C frozen radial τ-gradient diagnostic report

**Version:** phase_6c_c_v1

## Scope

- **Diagnostic only** — frozen `expansion20_tau_profiles.csv` was read, not modified.
- **No** τ smoothing, refit, K_g change, or pseudo-2D map regeneration.
- **Not** a lensing or second-channel result.
- Phase **6D remains blocked** until a future pre-registered Phase **6C-D** fix passes gates.

## Summary

- Primary pilots analyzed: **5**
- Phase 6D ready (from 6C-B): **0/5**
- Smoothness threshold: **0.25** (relative adjacent dτ/dr jump)

### Failure cause counts (primary label)

primary_failure_cause
inner_radius_instability    4
sparse_radial_sampling      1

## Per-galaxy diagnostics

| galaxy_id   |   n_radial_points |   max_rel_dtaudr_jump |   n_jumps_above_threshold |   worst_jump_r_kpc | worst_jump_region   | jump_failure_dominance   | primary_failure_cause    | phase6c_smoothness_pass   | phase6c_ready_for_second_channel   |
|:------------|------------------:|----------------------:|--------------------------:|-------------------:|:--------------------|:-------------------------|:-------------------------|:--------------------------|:-----------------------------------|
| DDO161      |                31 |             10.8452   |                         9 |              1.305 | inner_third         | single_dominant_jump     | inner_radius_instability | False                     | False                              |
| UGC07524    |                31 |              5.3451   |                         1 |              0.52  | inner_third         | single_dominant_jump     | inner_radius_instability | False                     | False                              |
| UGC08490    |                30 |              0.383294 |                         1 |              0.51  | inner_third         | single_dominant_jump     | inner_radius_instability | False                     | False                              |
| IC2574      |                34 |              2.41575  |                         8 |              2.135 | inner_third         | single_dominant_jump     | inner_radius_instability | False                     | False                              |
| NGC2403     |                73 |            116.125    |                        24 |              0.31  | inner_third         | single_dominant_jump     | sparse_radial_sampling   | False                     | False                              |

## Comparison with Phase 6C-B maps

For all pilots, `map_smoothness_dominated_by_1d_dtaudr` is true: pseudo-2D map smoothness failure is inherited from frozen radial dτ/dr, not from Cartesian gradient discretization alone.

## Next step

See `docs/phase6c_gradient_regularization_options.md` for pre-registered options. **Phase 6C-D** must be explicitly approved before applying any regularization.

## Reproducibility

```bash
python3 scripts/build_phase6c_gradient_diagnostics.py
```
