# Theory Summary

The τ field is treated as a reconstructed geometric field inferred from observed rotation data.

- Each galaxy has its own reconstructed τ profile.
- The universal part is the reconstruction law and protocol, not one final τ map for all galaxies.
- TDF should be compared against baryonic-only, NFW, and Burkert baselines.

## Notation: effective-gravity vs legacy benchmark labels

This repository separates three symbols:

| Symbol | Meaning |
| --- | --- |
| **K_g** | Gravitational **projection coefficient** in the updated conservative TDF effective-gravity formulation. Enters the radial velocity closure below. |
| **κ_tau** | **Dynamical stiffness** in the mother field equation of the full TDF framework. Governs field dynamics; **must not** be confused with \(K_g\). |
| **K_tau** (legacy) | Historical label in **frozen benchmark outputs**, configs (`K_tau`), CSV column names, and phase reports for the fixed projection-normalization factor used in radial reconstruction. In prose, treat legacy **K_tau** as the benchmark name for the **K_g-like** projection role; numerical results are unchanged until Phase 5G code migration. |

## Core radial equations (benchmark closure)

Updated notation (conceptual):

- `v_obs^2(r) = v_bar^2(r) + v_tau^2(r)`
- `v_tau^2(r) = r K_g d_tau/dr`
- `d_tau/dr = [v_obs^2(r) - v_bar^2(r)] / [r K_g]`

Legacy benchmark/config form (same numbers, historical symbol):

- `v_tau^2(r) = r K_tau d_tau/dr`
- `d_tau/dr = [v_obs^2(r) - v_bar^2(r)] / [r K_tau]`

**κ_tau** does not appear in the rotation-curve benchmark closure above; it belongs to the broader field-equation layer and is out of scope for the frozen holdout tables in this repository.

This benchmark is designed as model comparison and reconstruction quality analysis, not as a standalone proof against dark matter.
