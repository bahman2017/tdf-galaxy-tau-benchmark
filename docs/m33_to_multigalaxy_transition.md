# M33 to Multi-Galaxy Transition

M33 is the first case study and method prototype. This repository extends that workflow into a controlled multi-galaxy benchmark.

## What is adapted

- Radial reconstruction equations (updated **K_g** notation; legacy benchmark label **K_tau**):
  - `v_obs^2(r) = v_bar^2(r) + v_tau^2(r)`
  - `v_tau^2(r) = r K_g dτ/dr`  *(frozen outputs/config: legacy **K_tau**)*
  - `dτ/dr = [v_obs^2(r) - v_bar^2(r)] / [r K_g]`
- **κ_tau** (mother-field stiffness) is part of the broader TDF field framework and is **not** the same symbol as **K_g** or legacy **K_tau** in the radial benchmark closure.
- Baryonic residual handling and baseline model interfaces (baryonic/NFW/Burkert).
- Shared metrics and comparison protocol design patterns.

## What is not universalized

- M33-specific boundary/selection assumptions.
- Any single fixed closed-form tau profile across all galaxies.

## Conservative interpretation

This transition is methodology scaling, not a claim of SPARC validation or dark-matter falsification.

See `docs/theory_summary.md` and `docs/roadmap.md` (Phase 5G) for notation migration plans.
