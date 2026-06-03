# Phase 6A — Success and failure criteria (frozen-map test)

Companion to [`phase6a_2d_frozen_map_protocol.md`](phase6a_2d_frozen_map_protocol.md).

Criteria are **pre-registered** — evaluation happens in Phase **6C/6D**, not in 6A.

---

## 1. Primary success criteria (map construction — type A/B)

A pilot galaxy **passes map construction** if all of the following hold:

| ID | Criterion | Metric / check |
| --- | --- | --- |
| **S1** | Radial consistency | max \|τ_2D(R,0) − τ_radial(R)\| / max(\|τ_radial\|) < ε_τ (e.g. ε_τ = 10⁻⁶ or machine epsilon at grid) |
| **S2** | Frozen 1D preservation | τ_radial(R) equals `expansion20_tau_profiles` (or recomputed dτ/dr with identical policy) at shared radii |
| **S3** | Map smoothness | max \|∇τ_2D\| below threshold OR bounded total variation TV(τ_2D) < TV_max |
| **S4** | No unphysical discontinuities | No jumps Δτ > Δτ_max between adjacent cells (Δτ_max set in 6B) |
| **S5** | Regularization documented | Single smoothing scale recorded; not tuned per observable |
| **S6** | No τ retuning | K_g, knot amplitudes, dτ/dr refit unchanged from freeze step |

**Optional S7 (geometry):** inclination in [i_min, i_max] (e.g. 30°–90°) for sky projection quality.

---

## 2. Primary success criteria (second-channel scaffold — Phase 6D)

| ID | Criterion | Description |
| --- | --- | --- |
| **C1** | Scaffold generated | At least one pre-registered scaffold (S1/S2/S3) computed from **frozen** map only |
| **C2** | No observable-specific τ retuning | Same τ_2D used; no halo fit added |
| **C3** | Comparison baseline stated | e.g. baryonic-only g_bar or NFW holdout RMSE from **frozen** Phase 5 tables |
| **C4** | Quantitative metric reported | e.g. RMS extra-acceleration residual, correlation coefficient, or holdout velocity RMSE |
| **C5** | Failure allowed | Negative or null result is a valid Phase 6 outcome |

**Not required for success:** beating NFW on a new metric unless pre-registered in 6B as a **secondary** exploratory comparison (not a Phase 5 holdout contest).

---

## 3. Failure criteria (mandatory reporting)

Phase 6 **fails** or **stops** for a galaxy/attempt if any trigger applies:

| ID | Failure mode | Action |
| --- | --- | --- |
| **F1** | Per-observable τ retuning required | **Stop** — violates frozen-map rule |
| **F2** | Map unstable / non-smooth | Report failure; do not claim map validity |
| **F3** | Morphology assumption dominates | e.g. arbitrary ellipticity added without data — report |
| **F4** | Missing true 2D data but true-2D claimed | **Protocol violation** — reject claim |
| **F5** | Lensing proxy mislabeled as lensing confirmation | **Protocol violation** |
| **F6** | Radial τ incompatible with 1D freeze | \|S1\| or \|S2\| failed |
| **F7** | Second channel undefined | No pre-registered scaffold in 6B |
| **F8** | NGC7814-style 1D failure galaxy used as primary pilot | Exclude by selection criteria |

---

## 4. Diagnostic tiers (non-primary)

| Tier | Galaxies | Use |
| --- | --- | --- |
| **Primary pilot** | robust_tdf_success + data complete | Main Phase 6 report |
| **Diagnostic** | mixed_result (UGC00128), sensitivity_recovery | Sensitivity only; separate subsection |
| **Excluded** | tdf_failure_mode (NGC7814) | Case study only with failure label |

---

## 5. Comparison baselines (allowed, not halos in τ)

| Baseline | Role in Phase 6 |
| --- | --- |
| Baryonic-only g_bar | Reference acceleration field |
| Frozen NFW/MOND holdout RMSE | From `expansion20_holdout_validation.csv` — **read-only** |
| NFW/Burkert halo | **Comparison proxy only** — must not be added to τ freeze |

---

## 6. Metrics registry (to fix numeric thresholds in 6B)

| Parameter | Proposed default | Set in |
| --- | --- | --- |
| N_min radial points | 12 | 6B audit |
| ε_τ radial match | 10⁻⁶ relative | 6B |
| TV_max | TBD from pilot null | 6B |
| Δτ_max | TBD from grid spacing | 6B |
| Smoothing kernel width | 0.5 × median Δr | 6B |

---

## 7. Claim boundary checklist (evaluation reporting)

Every Phase 6 report must include explicit **NO** statements:

- [ ] No dark-matter disproof
- [ ] No full-SPARC validation
- [ ] No lensing confirmation
- [ ] No universal τ-profile
- [ ] No true 2D validation without 2D Σ_b data
- [ ] Axisymmetric pseudo-map ≠ true baryonic 2D map
- [ ] Phase 6 results do not update expansion_20 15/20 count

---

## 8. Outcome classes (for Phase 6D summary table)

| Class | Meaning |
| --- | --- |
| `map_success_scaffold_success` | S1–S6 and C1–C4 passed |
| `map_success_scaffold_inconclusive` | Map OK; second channel weak or null |
| `map_failure` | F2, F6 |
| `protocol_violation` | F4, F5, F7 |
| `deferred_true_2d` | F4 anticipated — type C not attempted |

---

## 9. Relation to Phase 5 metrics

| Phase 5 metric | Phase 6 use |
| --- | --- |
| robust_tdf_success | Pilot **selection** only |
| holdout RMSE | **Baseline reference** only — not a Phase 6 primary metric unless pre-registered |
| sensitivity_recovery | Not primary success in Phase 6 |

Phase 6 success is **not** defined as “another holdout win vs NFW/MOND” unless explicitly pre-registered as a **secondary** exploratory endpoint in 6B.
