# Phase 6E — Negative result summary

**Date:** 2026-05-27  
**Type:** decision-gate report (documentation only; no code or map regeneration)

## Headline

Radial τ reconstruction for the frozen **expansion_20** benchmark remains valid. **Frozen and pre-registered-regularized τ-gradient profiles are not map-smooth enough** for a Phase 6D second-channel scaffold. **0/5** primary pilots pass all hard gates after R2+R6.

## Cohort metrics

| Stage | Radial consistency | Smoothness ≤ 0.25 | Ready for 6D |
| --- | --- | --- | --- |
| 6C-B (frozen τ maps) | 5/5 PASS | 0/5 PASS | 0/5 |
| 6C-E (R2+R6 regularized) | 5/5 PASS | 0/5 PASS | 0/5 (`phase6d_candidate`) |

**Phase 6D: BLOCKED**

## Per-galaxy (6C-E)

| Galaxy | Capped | Trimmed | Mean dτ/dr drift | Smoothness | Candidate |
| --- | ---: | ---: | ---: | --- | --- |
| DDO161 | 14 | 1 | 1.32 | FAIL | no |
| UGC07524 | 11 | 1 | 0.20 | FAIL | no |
| UGC08490 | 1 | 1 | 0.007 | FAIL | no |
| IC2574 | 12 | 1 | 0.14 | FAIL | no |
| NGC2403 | 35 | 1 | 0.74 | FAIL | no |

## Interpretation (one paragraph)

Map embedding is reproducible; the blocker is **1D dτ/dr jump structure** in frozen expansion_20 profiles. Post-hoc R2+R6 cannot repair this within pre-registered limits without over-capping or breaking fidelity. Smoothness must be enforced **inside** a future reconstruction protocol (Phase **6F**), not after freezing Phase 5 outputs.

## Claim boundaries

No DM disproof · no full-SPARC validation · no lensing confirmation · no true 2D Σ_b · no universal τ · no second-channel success · Phase 5 **15/20** unchanged.

## Decision

- Do **not** open Phase 6D.
- Do **not** proceed to lensing/deflection on current maps.
- Next: **Phase 6F** — pre-register reconstruction with map-smoothness in the primary objective and holdout.

## Artifacts

- Decision gate: `docs/phase6e_negative_result_decision_gate.md`
- 6C-E detail: `docs/phase6d_regularized_map_results.md`
- Tables: `outputs/tables/phase6c_primary_pilot_map_summary.csv`, `outputs/tables/phase6d_regularized_map_summary.csv`
