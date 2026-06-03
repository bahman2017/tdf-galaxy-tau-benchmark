# Phase 6E — Negative result decision gate

**Status:** documentation / report QA only (no new fits, maps, or regularization)  
**Implementation commit (6C-E):** `7286168`  
**Pre-registration commit (6C-D):** `b4d1f34`

This document consolidates Phase 6A–6C-E and records the **scientific decision** to keep Phase 6D blocked. The negative cohort result is a **valid scientific outcome**, not a repository execution failure.

---

## 1. Phase 6A–6C-E summary

| Phase | Label | What was done | Key artifact |
| --- | --- | --- | --- |
| **6A** | Protocol | Defined frozen-map test scope, axisymmetric pseudo-2D τ(x,y)=τ(R), success/failure gates, claim boundaries; **no fits** | `docs/phase6a_2d_frozen_map_protocol.md` |
| **6B** | Pilot selection | Data-availability audit; Tier-1 primary pilots: DDO161, UGC07524, UGC08490, IC2574, NGC2403 | `docs/phase6b_pilot_selection_rationale.md` |
| **6C-A** | First map | DDO161 frozen pseudo-2D map from `expansion20_tau_profiles.csv` | `outputs/maps/phase6c/DDO161_frozen_pseudo2d_tau_map.npz` |
| **6C-B** | Cohort maps | All five primary pilots; radial vs smoothness audit | `outputs/tables/phase6c_primary_pilot_map_summary.csv` |
| **6C-C** | Gradient diagnostic | Read-only dτ/dr jump analysis; inner-radius instability (4/5) | `outputs/tables/phase6c_primary_pilot_gradient_diagnostics.csv` |
| **6C-D** | Pre-registration | R2 (global jump cap 0.25) + R6 (boundary trim); acceptance gates frozen | `configs/phase6d_regularization_preregistration.yaml` |
| **6C-E** | R2+R6 implementation | Regularized profiles/maps under `phase6d_*` only; Phase 5 unchanged | `docs/phase6d_regularized_map_results.md` |

Phase 5 **expansion_20** radial τ holdout (**15/20** primary `tdf_3knot` success) remains the authoritative 1D benchmark. Phase 6 tests whether **frozen** radial τ supports a **map-smooth** axisymmetric pseudo-2D scaffold for a future second channel—not whether Phase 5 failed.

---

## 2. Scientific result

### Before regularization (6C-B frozen maps)

| Metric | Cohort result |
| --- | --- |
| Radial consistency (map τ vs frozen expansion20 profile) | **5/5 PASS** |
| Smoothness (max relative adjacent dτ/dr jump ≤ 0.25) | **0/5 PASS** |
| `phase6c_ready_for_second_channel_scaffold` | **0/5** |

All five pilots inherit smoothness failure from **frozen 1D dτ/dr structure** (`smoothness_failure_inherited_from_frozen_1d_profile=true` in `phase6c_primary_pilot_map_summary.csv`).

### After pre-registered R2+R6 (6C-E)

| Metric | Cohort result |
| --- | --- |
| Radial consistency (map τ vs **regularized** profile) | **5/5 PASS** |
| All hard gates (smoothness, R2/R6 limits, fidelity ≤15% mean dτ/dr drift) | **0/5 PASS** |
| `phase6d_candidate` | **0/5** |

### Phase 6D gate

**Phase 6D remains blocked.** Do not proceed to lensing/deflection scaffold evaluation on the current frozen or post-hoc-regularized τ maps.

---

## 3. Per-galaxy table (6C-E)

Source: `outputs/tables/phase6d_regularized_map_summary.csv` (commit `7286168`).

| Galaxy | Segments capped | Points trimmed | Mean dτ/dr drift vs frozen | Smoothness | phase6d_candidate |
| --- | ---: | ---: | ---: | --- | --- |
| DDO161 | 14 (46.7%) | 1 | 1.32 | FAIL (0.396) | false |
| UGC07524 | 11 (36.7%) | 1 | 0.20 | FAIL (0.304) | false |
| UGC08490 | 1 (3.4%) | 1 | 0.007 | FAIL (0.822) | false |
| IC2574 | 12 (36.4%) | 1 | 0.14 | FAIL (0.250) | false |
| NGC2403 | 35 (48.6%) | 1 | 0.74 | FAIL (9.33) | false |

Correction audits: `outputs/tables/phase6d_{GALAXY}_correction_audit.csv` (all five present).

---

## 4. Interpretation

1. **Map construction is reproducible.** Axisymmetric pseudo-2D embedding τ₂D(x,y)=τ(R) achieves radial consistency when the reference profile is internally consistent (frozen or regularized).

2. **The limiting factor is frozen radial dτ/dr structure**, not grid code or K_g projection. Large relative adjacent jumps in `dtaudr_reconstructed` from `expansion20_tau_profiles.csv` dominate the smoothness metric; Phase 6C-C tied this to inner-radius τ₀≈0 boundaries and sparse Δr (NGC2403).

3. **Post-hoc smoothing (R2+R6) is not scientifically acceptable** for opening Phase 6D on this protocol: either too many segments must be capped (>40% on 2/5 pilots), fidelity to the frozen profile is violated (>15% mean drift on 3/5), or smoothness still fails (including map |∇τ| on UGC08490 and NGC2403).

4. **A future method must embed map-smoothness in the reconstruction/validation protocol**—as part of the primary objective and holdout design—not as an after-the-fact repair on frozen Phase 5 outputs.

---

## 5. Claim boundaries (unchanged)

| Boundary | Asserted |
| --- | --- |
| No dark-matter disproof | yes |
| No full-SPARC validation | yes |
| No lensing confirmation | yes |
| No true 2D Σ_b map | yes |
| No universal τ profile | yes |
| No second-channel success | yes |
| Phase 5 expansion_20 headline unchanged | yes |

---

## 6. Decision

| Decision | Verdict |
| --- | --- |
| Phase 6D (second-channel scaffold) | **BLOCKED** |
| Lensing / deflection (Phase 7) | **Do not proceed** from current maps |
| Post-hoc R2+R6 on frozen profiles | **Closed** as negative cohort (6C-E) |
| Recommended next phase | **Phase 6F** — design a **new reconstruction protocol** where map-smoothness (e.g. bounded dτ/dr variation) is part of **primary fitting and holdout validation**, with fresh pre-registration before any new cohort run |

---

## References

- `docs/phase6d_regularized_map_results.md`
- `outputs/reports/phase6d_regularization_cohort_report.md`
- `outputs/reports/phase6e_negative_result_summary.md`
- `docs/phase6c_gradient_regularization_options.md` (R1–R7 menu; only R2+R6 were pre-registered)
- `docs/phase6d_frozen_gradient_regularization_preregistration.md`
