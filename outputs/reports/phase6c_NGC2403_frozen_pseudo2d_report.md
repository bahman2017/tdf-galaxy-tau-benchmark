# Phase 6C frozen pseudo-2D τ-map — NGC2403

## Map type

This product is a **frozen axisymmetric pseudo-2D** map (τ₂D(x,y) = τ_radial(R)), **not** a true 2D baryonic Σ_b(x,y) reconstruction.

## Fitting and benchmarks

- **No new fit** was performed; τ and **K_g** are taken from frozen `expansion20_tau_profiles.csv`.
- **No lensing confirmation** is claimed.
- This work **does not update the Phase 5 expansion_20 result** (15/20 primary `tdf_3knot` robust holdout success).
- **NGC2403** is a Phase 6 pilot implementation only.

## Numerical summary

- **K_g** used: 1.0 (legacy CSV column **K_tau**).
- Grid: 101 × 101
- Radial range (frozen): [0.16, 20.87] kpc
- Outer grid limit: 21.9135 kpc
- Radial consistency max relative error: 0.000e+00 (PASS)
- Smoothness metric: 116.1246 (threshold 0.25; FAIL)
- Frozen-profile dτ/dr jump: 116.1246; map |∇τ| jump: 6.0617.
- A smoothness FAIL reflects the committed frozen radial profile, not τ retuning in 6C.

## Claim boundaries

No dark-matter disproof; no full-SPARC validation; no universal τ profile.

Consistency rows: 73
