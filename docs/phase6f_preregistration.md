# Phase 6F — Pre-registration (smooth τ reconstruction)

**Version:** `phase_6f_preregistration_v1`  
**Status:** PRE-REGISTERED DESIGN ONLY — no cohort execution  
**Branch:** `feature/phase6f-preregister-smooth-reconstruction`

Machine-readable companion (future): `configs/phase6f_smooth_reconstruction_preregistration.yaml` — **not created in this phase**.

---

## 1. Inherited decisions (immutable)

From Phase 6E (`8f4a83b`):

1. Phase **6D blocked** (0/5 `phase6d_candidate` after 6C-E).
2. **No** lensing/deflection using `phase6c_*` or `phase6d_*` maps.
3. Post-hoc R2+R6 on `expansion20_tau_profiles.csv` is **closed**.
4. Phase 5 expansion_20 **15/20** holdout is **historical** and **not** overwritten by 6F outputs.

---

## 2. Primary hypothesis

Integrated τ reconstruction with explicit smoothness penalties can produce profiles that pass Phase 6 map-smoothness gates **without** exceeding pre-registered holdout degradation limits, using **cohort-global** hyperparameters only.

**Null expectation (from 6E):** if smoothness conflicts with holdout fidelity under shared λ, 6F will reproduce a **negative cohort** and 6D stays blocked.

---

## 3. Pre-registered objective weights

| Symbol | Term | Initial registry value | Tuning allowed |
| --- | --- | --- | --- |
| — | \(\mathcal{L}_{\mathrm{data}}\) | expansion_20-equivalent fidelity | fixed functional form |
| \(\lambda_s\) | \(\mathcal{L}_{\mathrm{smooth}}\) | grid search on dev subset | dev subset only, then frozen |
| \(\lambda_c\) | \(\mathcal{L}_{\mathrm{curv}}\) | 0 (disabled v1) | optional enable before freeze |
| \(\lambda_{\mathrm{inner}}\) | \(\mathcal{L}_{\mathrm{inner}}\) | grid search on dev subset | dev subset only, then frozen |
| \(\lambda_{\mathrm{sparse}}\) | \(\mathcal{L}_{\mathrm{sparse}}\) | grid search on dev subset | dev subset only, then frozen |

**Dev subset (frozen list):** DDO161, UGC08490, NGC2403 (inner-boundary + sparse-Δr coverage).

**Tuning grid (pre-registered):** \(\lambda_s \in \{10^{-4}, 10^{-3}, 10^{-2}, 10^{-1}\}\); others \(\in \{0, 10^{-3}, 10^{-2}\}\) when enabled.

**Selection rule:** minimize dev-subset **G2 violations** subject to dev-subset G6 pass; tie-break by lower \(\mathcal{L}_{\mathrm{data}}\).

---

## 4. Hard gates (G1–G9)

### G1 — Radial consistency

- **Metric:** max relative \|τ_map − τ_profile\| / max(\|τ_profile\|, τ_scale_floor)
- **Threshold:** ≤ **1.0e-6**
- **Reference profile:** `phase6f_reconstructed_tau_profiles.csv` (not expansion_20)

### G2 — 1D smoothness

- **Metric:** max relative adjacent dτ/dr jump (Phase 6C definition)
- **Threshold:** ≤ **0.25**

### G3 — Map smoothness

- **Metric:** max of G2 and map \|∇τ\| adjacent jump on valid mask
- **Threshold:** ≤ **0.25**

### G4 — Inner boundary

- **Pass if:** \(|\tau(r_{\min})| \geq 10^{-9}\) **OR** first-segment relative jump ≤ **0.25**

### G5 — Sparse-Δr spike dominance

- **Fail if:** `jump_failure_dominance == sparse_delta_r_only` (same classification as Phase 6C-C)
- **Pass otherwise**

### G6 — Per-galaxy holdout non-degradation

- **Metric:** holdout velocity RMSE (or pre-registered acceleration metric)
- **Threshold:** ≤ **1.15 ×** expansion_20 frozen value for same `galaxy_id` and model class

### G7 — Cohort holdout floor

- **Threshold:** 6F primary `tdf_3knot` holdout success ≥ **14/20** on frozen registry  
  **OR** Wilcoxon signed-rank non-inferiority vs expansion_20 per-galaxy RMSE at α=0.05 (pre-registered alternative if count < 14)

### G8 — Parameter control

- Model class: **`tdf_3knot`** only for primary gate
- Knot count: **unchanged** from expansion_20 per galaxy
- `K_g = 1.0`, `kg_retuned = false`, `separate_halo_added = false`
- `lensing_only_tau_fit = false`

### G9 — Audit completeness

- Row present in `phase6f_smoothness_metrics.csv`, `phase6f_holdout_metrics.csv`, and correction log if any constraint active-set hit

### Phase 6D promotion rule

- `phase6d_candidate = true` only if G1–G9 pass for that galaxy **and** cohort has ≥1 primary pilot with `phase6d_candidate=true`.
- Until then: **6D blocked**.

---

## 5. Cohort and freeze policy

| Item | Policy |
| --- | --- |
| **Cohort ID** | `phase6f_expansion20_registry_v1` |
| **Galaxy list** | Same 20 galaxies as controlled expansion_20 (read list from frozen config at implementation time) |
| **Profiles output** | `outputs/tables/phase6f_reconstructed_tau_profiles.csv` |
| **expansion_20** | Read-only comparison for G6/G7 |
| **Overwrite forbidden** | All `expansion20_*` benchmark tables, `controlled_expansion_final_claims.csv` |
| **Freeze tag (future)** | `v0.1.7-phase6f-cohort-freeze` (proposed name; assign at implementation) |

---

## 6. Expected outputs (future implementation)

```
outputs/tables/phase6f_reconstructed_tau_profiles.csv
outputs/tables/phase6f_smoothness_metrics.csv
outputs/tables/phase6f_holdout_metrics.csv
outputs/tables/phase6f_candidate_ranking.csv
outputs/reports/phase6f_decision_gate_report.md
outputs/figures/phase6f_{GALAXY}_tau_profile.png
outputs/figures/phase6f_{GALAXY}_dtaudr_profile.png
outputs/figures/phase6f_{GALAXY}_smoothness_diagnostic.png
outputs/figures/phase6f_cohort_gate_summary.png
```

**None of the above exist at pre-registration time.**

---

## 7. Claim boundaries (checklist)

| Claim | Allowed in 6F? |
| --- | --- |
| Dark matter disproved | **No** |
| Full SPARC validated | **No** |
| Lensing confirmed | **No** |
| Second-channel success | **No** (until 6D gates pass on 6F maps) |
| Universal τ profile | **No** |
| Deflection from phase6c/phase6d maps | **No** |
| Phase 5 headline auto-upgraded | **No** |

---

## 8. Protocol violations (automatic fail)

- Per-galaxy λ tuning after holdout exposure
- Overwriting `expansion20_tau_profiles.csv`
- Using post-hoc R2/R6 as primary smoothness mechanism
- Promoting 6D without G1–G9 documentation
- Claiming lensing/2D success from axisymmetric τ(R) maps

---

## 9. Relation to Phase 6C-D/E

| Path | Status |
| --- | --- |
| 6C-D/E R2+R6 post-hoc repair | **Closed** (negative cohort) |
| 6F integrated reconstruction | **Pre-registered** (this document) |
| 6D second-channel | **Blocked** until 6F cohort + map gate pass |

---

## Sign-off fields (implementation phase)

| Field | Value at pre-registration |
| --- | --- |
| `protocol_version` | `phase_6f_preregistration_v1` |
| `cohort_executed` | false |
| `phase6d_unblocked` | false |
| `phase5_headline_changed` | false |
