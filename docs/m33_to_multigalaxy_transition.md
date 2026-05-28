# M33 to Multi-Galaxy Transition

M33 is the first case study and method prototype. This repository extends that workflow into a controlled multi-galaxy benchmark.

## What is adapted

- Radial reconstruction equations:
  - `v_obs^2(r) = v_bar^2(r) + v_tau^2(r)`
  - `v_tau^2(r) = r K_tau dτ/dr`
  - `dτ/dr = [v_obs^2(r) - v_bar^2(r)] / [r K_tau]`
- Baryonic residual handling and baseline model interfaces (baryonic/NFW/Burkert).
- Shared metrics and comparison protocol design patterns.

## What is not universalized

- M33-specific boundary/selection assumptions.
- Any single fixed closed-form tau profile across all galaxies.

## Conservative interpretation

This transition is methodology scaling, not a claim of SPARC validation or dark-matter falsification.
