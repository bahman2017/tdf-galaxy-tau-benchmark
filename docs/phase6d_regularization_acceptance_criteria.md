# Phase 6C-D — Regularization acceptance and failure criteria

Companion: [`phase6d_frozen_gradient_regularization_preregistration.md`](phase6d_frozen_gradient_regularization_preregistration.md)  
Config: `configs/phase6d_regularization_preregistration.yaml`

**Implementation phase label:** **6C-E** (not executed in 6C-D).

---

## 1. Hard acceptance gates (all required per pilot)

| ID | Gate | Criterion |
| --- | --- | --- |
| **A1** | Radial consistency | max relative error map τ vs **regularized** profile ≤ **10⁻⁶** |
| **A2** | Smoothness | max relative adjacent dτ/dr jump ≤ **0.25** after R2 (+ R6 profile) |
| **A3** | K_g fixed | **K_g = 1.0**; `kg_retuned = false` |
| **A4** | No τ refit | `tau_retuned = false`; no knot optimization |
| **A5** | No halo | `separate_halo_added = false` |
| **A6** | No lensing τ | `lensing_only_tau_fit = false` |
| **A7** | Map type | `true_2d_sigma_b = false`; axisymmetric pseudo-2D only |
| **A8** | Phase 5 frozen | `expansion20_tau_profiles.csv` **unchanged**; headline **15/20** unchanged |
| **A9** | Correction audit | Every R2/R6 change row in `phase6d_{GALAXY}_correction_audit.csv` |
| **A10** | Coverage | ≥ **12** points and ≥ **5.0 kpc** after trim |
| **A11** | Fidelity guard | Mean \|Δdτ/dr\| / \|dτ/dr\| vs frozen expansion20 ≤ **15%** (diagnostic; holdout not rerun) |

**Phase 6D readiness (per pilot):** A1–A11 pass → `phase6d_ready_for_second_channel_scaffold = true`.

**Phase 6D cohort gate:** ≥ **1** pilot ready; else **6D blocked**.

---

## 2. Failure gates (mandatory stop/report)

| ID | Failure | Action |
| --- | --- | --- |
| **F1** | R2 capped segments > **40%** | Fail pilot; report over-correction |
| **F2** | R6 trimmed points > **10%** | Fail pilot |
| **F3** | Remaining points < **12** or coverage < **5 kpc** | Fail pilot |
| **F4** | Smoothness still > **0.25** after R2+R6 | Fail pilot; 6D blocked for that galaxy |
| **F5** | Radial consistency fail vs regularized profile | Fail pilot |
| **F6** | Mean dτ/dr change vs frozen > **15%** | Fail pilot — arbitrary wholesale replacement |
| **F7** | Correction driven by per-galaxy tuning | **Protocol violation** |
| **F8** | Overwrite of `expansion20_*` | **Protocol violation** |
| **F9** | Lensing / second-channel claimed | **Protocol violation** |
| **F10** | Zero pilots pass all gates | Cohort **negative result**; 6D blocked |

---

## 3. Comparison to Phase 6C-B baseline

| Metric | 6C-B (frozen τ) | 6C-E (regularized τ) |
| --- | --- | --- |
| Profile source | `expansion20_tau_profiles.csv` | `phase6d_{GALAXY}_regularized_profile.csv` |
| Radial consistency reference | Frozen expansion20 | Regularized profile |
| Smoothness | Failed 5/5 | Must pass per A2 |
| Phase 5 benchmark | Authoritative | **Read-only** |

---

## 4. Correction audit schema (required columns)

`phase6d_{GALAXY}_correction_audit.csv` must include:

- `galaxy_id`, `r_kpc`, `step` (`r2_cap` \| `r6_inner_trim` \| `r6_outer_trim` \| `none`)
- `dtaudr_before`, `dtaudr_after`, `tau_before`, `tau_after`
- `relative_jump_before`, `relative_jump_after`
- `correction_applied`, `abs_correction_dtaudr`
- `cumulative_fraction_segments_capped`

---

## 5. Claim-boundary checklist (reporting)

Every 6C-E summary row must assert:

- [ ] No dark-matter disproof  
- [ ] No full-SPARC validation  
- [ ] No lensing confirmation  
- [ ] No universal τ profile  
- [ ] No true 2D without 2D data  
- [ ] Not a successful second-channel result (unless 6D scaffold passes **separate** 6D protocol)  
- [ ] Phase 5 expansion_20 headline unchanged  

---

## 6. What success does and does not mean

**Success (gates pass):** Permits **consideration** of Phase **6D** second-channel scaffold tests under a **separate** 6D pre-registration. It does **not** validate lensing, DM alternatives, or cosmology.

**Failure:** Scientifically valid. Report inherited frozen-gradient structure as a **map-hostile** feature of the committed radial reconstruction at fixed **K_g**.
