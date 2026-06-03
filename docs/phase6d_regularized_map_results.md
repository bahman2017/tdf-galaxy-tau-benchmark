# Phase 6C-E — Regularized pseudo-2D map results

**Implementation:** `phase_6c_e_v1`  
**Protocol:** `phase_6c_d_preregistration_v1` (commit `b4d1f34`)  
**Builder:** `python3 scripts/build_phase6d_regularized_maps.py --all-primary-pilots`

## Cohort outcome

**Phase 6D remains blocked** — **0/5** Tier-1 primary pilots pass all hard gates after pre-registered R2+R6 repair.

This is a **negative cohort result** for map-smoothness via frozen-gradient regularization. It does **not** refute Phase 5 holdout success; it does **not** confirm lensing; it is **not** true 2D Σ_b.

## Per-pilot summary

| Galaxy | Segments capped | Points trimmed | Remaining pts | Coverage (kpc) | Mean dτ/dr drift | Smoothness | Radial consist. | phase6d_candidate |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| DDO161 | 14 (46.7%) | 1 | 30 | 12.64 | 1.32 | FAIL (0.396) | PASS | false |
| UGC07524 | 11 (36.7%) | 1 | 30 | 10.00 | 0.20 | FAIL (0.304) | PASS | false |
| UGC08490 | 1 (3.4%) | 1 | 29 | 9.47 | 0.007 | FAIL (0.822) | PASS | false |
| IC2574 | 12 (36.4%) | 1 | 33 | 9.09 | 0.14 | FAIL (0.250†) | PASS | false |
| NGC2403 | 35 (48.6%) | 1 | 72 | 20.61 | 0.74 | FAIL (9.33) | PASS | false |

† IC2574: radial dτ/dr jump at cap (≈0.25); map |∇τ| metric still fails threshold.

### Gate failures (hard)

| Galaxy | Failures |
| --- | --- |
| DDO161 | R2 >40% capped; smoothness; fidelity >15% |
| UGC07524 | smoothness; fidelity >15% |
| UGC08490 | smoothness (map |∇τ| dominates) |
| IC2574 | smoothness |
| NGC2403 | R2 >40% capped; smoothness; fidelity >15% |

## R2 / R6 confirmation

- **R2:** single forward sweep on `dtaudr_reconstructed`; relative jump cap **0.25**; minimal adjustment of `dτ/dr[i+1]`; sign preserved; τ re-integrated from `r_min` with τ(r_min) unchanged; fail if **>40%** segments capped.
- **R6:** after R2; ≤1 inner trim (τ≈0 or first frozen jump >0.25); ≤1 outer trim (last jump >0.25 or `worst_jump_region=outer_third`); fail if **>10%** trimmed or coverage/point minima violated; trimmed radii masked in maps.

## Claim boundary checklist

| Check | Result |
| --- | --- |
| Phase 5 `expansion20_*` unchanged | yes |
| No τ refit | yes |
| K_g = 1.0, no retuning | yes |
| No halo | yes |
| No lensing-only τ fit / confirmation | yes |
| No true 2D Σ_b | yes |
| Full correction audits | yes (all five pilots) |

## Artifacts

- Summary: `outputs/tables/phase6d_regularized_map_summary.csv`
- Cohort report: `outputs/reports/phase6d_regularization_cohort_report.md`
- Per galaxy: `outputs/tables/phase6d_{GALAXY}_*`, `outputs/maps/phase6d/{GALAXY}_regularized_pseudo2d_tau_map.npz`

## Recommended next step

Do **not** open Phase 6D on this repair path. Options: document negative result in manuscript supplement; revisit **non-pre-registered** regularization only via new pre-registration; or pursue Phase 6D only under a **different** pre-registered protocol (not R2+R6 as implemented here).
