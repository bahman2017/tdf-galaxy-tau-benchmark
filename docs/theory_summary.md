# Theory Summary

The tau field is treated as a reconstructed geometric field inferred from observed rotation data.

- Each galaxy has its own reconstructed tau profile.
- The universal part is the reconstruction law and protocol, not one final tau map for all galaxies.
- TDF should be compared against baryonic-only, NFW, and Burkert baselines.

Core radial equations used in this benchmark:

- `v_obs^2(r) = v_bar^2(r) + v_tau^2(r)`
- `v_tau^2(r) = r K_tau d_tau/dr`
- `d_tau/dr = [v_obs^2(r) - v_bar^2(r)] / [r K_tau]`

This benchmark is designed as model comparison and reconstruction quality analysis, not as a standalone proof against dark matter.
