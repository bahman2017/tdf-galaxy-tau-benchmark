# Phase 6F design summary

**Type:** pre-registration / protocol design (no computation)  
**Branch:** `feature/phase6f-preregister-smooth-reconstruction`  
**Date:** 2026-05-27

## One-line summary

Phase 6F pre-registers **map-smoothness inside τ reconstruction** as a primary objective, on a **fresh cohort**, while preserving the Phase 6E negative result and keeping **Phase 6D blocked**.

## Why Phase 6F exists

| Finding (6E) | Implication |
| --- | --- |
| 1D holdout OK on expansion_20 | Do not discard Phase 5 benchmark |
| 0/5 map-smooth on frozen + R2+R6 | Post-hoc repair is insufficient |
| Map build reproducible | Fix the **profile**, not the embedder |

## Scientific question

Can τ be fit so **holdout adequacy**, **bounded dτ/dr**, and **map-smoothness readiness** hold together with **global** hyperparameters?

## Objective (pre-registered terms)

1. Data fidelity (v / a residuals)
2. Smoothness penalty on relative dτ/dr jumps
3. Optional d²τ/dr² curvature penalty (disabled v1)
4. Inner boundary constraint
5. Sparse Δr robustness weighting

## Hard gates before 6D

- Radial consistency ≤ 1e-6 vs **6F** profile
- Smoothness ≤ 0.25 (1D + map)
- Inner boundary + sparse-Δr checks
- Holdout ≤ 1.15× expansion_20 per galaxy; cohort ≥ 14/20 or non-inferiority test
- Fixed knot topology; no halo; K_g = 1

## Cohort policy

- **New:** `phase6f_reconstructed_tau_profiles.csv`
- **Read-only:** `expansion20_*` for comparison
- **Historical:** Phase 5 **15/20** unchanged

## What is not happening in this phase

- No cohort run
- No new maps
- No code changes
- No benchmark rerun
- No 6D unblock

## Documents

| Doc | Path |
| --- | --- |
| Full protocol | `docs/phase6f_smooth_reconstruction_protocol.md` |
| Pre-registration | `docs/phase6f_preregistration.md` |
| 6E decision (preserved) | `docs/phase6e_negative_result_decision_gate.md` |

## Next step (after merge)

Phase **6F-A:** add `configs/phase6f_smooth_reconstruction_preregistration.yaml` + implementation approval, then cohort script (explicit request required).
