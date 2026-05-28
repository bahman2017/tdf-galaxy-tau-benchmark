# Project Plan

## Phase 0: repo setup
Initial scaffold, package wiring, CLI entry points, and baseline tests.

## Phase 1: SPARC schema + subset selection
Define SPARC-compatible schema, validation checks, and a reproducible subset definition.

## Phase 2: radial tau reconstruction per galaxy
Reconstruct `d_tau/dr` and `tau(r)` independently for each galaxy from rotation residuals.

## Phase 3: baryonic/NFW/Burkert/TDF comparison
Evaluate baseline and TDF pathways with shared metrics and transparent assumptions.

## Phase 4: failure-mode analysis
Audit sensitivity to noisy curves, negative residuals, low-radius behavior, and smoothing choices.

## Phase 5: full SPARC benchmark
Scale subset pipeline to the full SPARC sample under the same protocol.

## Phase 6: optional 2D tau-map reconstruction
Extend radial profiles into 2D tau maps with explicit assumptions.

## Phase 7: frozen tau-map lensing/deflection prediction
Predict lensing-like observables from frozen tau maps without adding ad hoc fit terms.
