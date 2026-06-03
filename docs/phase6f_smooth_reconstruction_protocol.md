# Phase 6F — Map-smooth τ reconstruction protocol (design)

**Status:** protocol design and pre-registration only — **no cohort run**, **no code changes**, **no map regeneration** in this phase.  
**Branch:** `feature/phase6f-preregister-smooth-reconstruction`  
**Precedes:** any future Phase 6F implementation cohort and any reconsideration of Phase 6D.

**Companion:** [`phase6f_preregistration.md`](phase6f_preregistration.md) (gates, cohorts, outputs, claim boundaries)

---

## 1. Phase 6E decision (preserved, not reopened)

Phase 6E (`8f4a83b`) closed the Phase 6C-E negative cohort as a **valid scientific result**. Phase 6F **does not** revise, weaken, or supersede that conclusion.

| Decision | Status |
| --- | --- |
| **Phase 6D** (second-channel scaffold on current maps) | **BLOCKED** — 0/5 `phase6d_candidate` after R2+R6 |
| **Lensing / deflection** (Phase 7) on `phase6c_*` / `phase6d_*` maps | **Do not proceed** |
| **Post-hoc smoothing** (R2+R6 on frozen `expansion20_tau_profiles.csv`) | **CLOSED** as a path to 6D |
| **Phase 5 expansion_20** 1D holdout (**15/20**) | **Historical benchmark** — unchanged and authoritative for Phase 5 claims |

**What remains true after 6E:**

- Frozen expansion_20 radial τ is **adequate for the 1D holdout benchmark**.
- Frozen and post-hoc-regularized dτ/dr profiles are **not map-smooth enough** for second-channel map construction under Phase 6A–6E protocols.
- Map embedding τ₂D(x,y)=τ(R) is **reproducible** when the 1D reference profile is internally consistent; the blocker is **1D dτ/dr structure**, not grid code.

Phase 6F asks a **different question**: can τ be **reconstructed** so smoothness is satisfied **before** freeze, without per-galaxy cosmetic repair?

---

## 2. Phase 6F scientific question

> **Can τ reconstruction jointly satisfy 1D rotation / holdout adequacy, radial map consistency, bounded dτ/dr variation, and map-smoothness readiness—using a single pre-registered objective and shared hyperparameters across the cohort—without arbitrary per-galaxy tuning?**

**Joint success criteria (all required for a galaxy to count toward 6D promotion):**

1. **1D adequacy** — holdout velocity / acceleration residual within pre-registered tolerance vs Phase 5 frozen baseline on the same galaxy and split policy.
2. **Radial consistency** — axisymmetric pseudo-2D map τ matches the **Phase 6F reconstructed** 1D profile at ≤ pre-registered relative error.
3. **Bounded dτ/dr** — max relative adjacent dτ/dr jump ≤ pre-registered threshold (aligned with Phase 6C: **0.25** unless amended only via new pre-registration).
4. **Map-smoothness readiness** — combined 1D + map gradient smoothness metric ≤ same threshold (Phase 6C definition).
5. **No per-galaxy tuning** — one global smoothness weight λ_s, one global curvature weight λ_c (if enabled), fixed knot topology per model class; only standard holdout splits vary by galaxy.

**Explicit non-goals for 6F:**

- Proving dark-matter absence, universal τ, lensing confirmation, or true 2D Σ_b.
- Replacing or retroactively upgrading the Phase 5 **15/20** headline without a separately pre-registered claim amendment.

---

## 3. Separation from Phase 6E and 6C-E

| Aspect | Phase 6E / 6C-E | Phase 6F |
| --- | --- | --- |
| **Input profile** | Read-only copy of `expansion20_tau_profiles.csv` | **New fit** from SPARC radial data + baryonic baseline |
| **Smoothness** | Post-hoc R2 cap + R6 trim | **Primary objective penalty** during optimization |
| **Phase 5 tables** | Must not overwrite | Must not overwrite; new `phase6f_*` artifacts only |
| **6D promotion** | Failed 0/5 | Blocked until a **future 6F cohort** passes hard gates |
| **Interpretation** | Negative result on repair | **Hypothesis test** on integrated reconstruction |

---

## 4. Candidate reconstruction objectives

All terms are **interpretable** and **pre-registered** before the first 6F cohort run. Weights are **global** (cohort-wide), not per-galaxy.

### 4.1 Data fidelity term — \(\mathcal{L}_{\mathrm{data}}\)

**Purpose:** preserve 1D rotation-curve / acceleration adequacy.

**Form (default pre-registration):** weighted sum over radial bins of squared residual in **extra acceleration** or circular velocity:

\[
\mathcal{L}_{\mathrm{data}} = \sum_i w_i \,\bigl(a_{\mathrm{obs},i} - a_{\mathrm{bar},i}\, K_g\, f(\tau_i)\bigr)^2
\]

or equivalent velocity-space RMSE consistent with existing `tdf_3knot` holdout evaluation.

**Constraints:**

- \(K_g = 1.0\) fixed (no retuning in 6F unless explicitly pre-registered).
- Same baryonic \(a_{\mathrm{bar}}\) / \(v_{\mathrm{bar}}\) pipeline as expansion_20.
- No separate halo added in 6F primary model.

### 4.2 Smoothness penalty — \(\mathcal{L}_{\mathrm{smooth}}\)

**Purpose:** bound adjacent dτ/dr variation **during** fit, not after freeze.

**Form:**

\[
\mathcal{L}_{\mathrm{smooth}} = \sum_{i=0}^{N-2} \psi\!\left(
\frac{|d\tau/dr_{i+1} - d\tau/dr_i|}{\max(|d\tau/dr_i|, \epsilon)}
\right)
\]

with \(\psi\) = Huber or squared hinge above threshold \(\tau_{\mathrm{jump}} = 0.25\), and \(\epsilon = 10^{-12}\).

**Interpretation:** penalizes the same relative jump metric that failed Phase 6C-B/6C-E gates.

### 4.3 Optional curvature penalty — \(\mathcal{L}_{\mathrm{curv}}\)

**Purpose:** limit non-physical oscillations in dτ/dr.

\[
\mathcal{L}_{\mathrm{curv}} = \sum_i \left(\frac{d^2\tau}{dr^2}\Big|_i\right)^2
\]

or discrete second difference along sorted \(r_kpc\). **Optional** in v1; if disabled, \(\lambda_c = 0\) and documented as such.

### 4.4 Inner boundary constraint — \(\mathcal{L}_{\mathrm{inner}}\)

**Purpose:** address Phase 6C-C inner-radius instability (τ≈0 at \(r_{\min}\)).

**Form (one of, pre-registered before run):**

- **B1:** soft anchor \(\tau(r_{\min}) = \tau_{\mathrm{anchor}}\) with \(\tau_{\mathrm{anchor}}\) from baryonic inner slope or small positive floor; **or**
- **B2:** penalty on first-segment relative jump only when \(|\tau(r_{\min})| < \tau_{\mathrm{zero}}\) (\(\tau_{\mathrm{zero}} = 10^{-9}\)).

**Not allowed:** dropping inner points post-hoc as the primary fix (that was R6 in 6C-E).

### 4.5 Sparse Δr robustness — \(\mathcal{L}_{\mathrm{sparse}}\)

**Purpose:** reduce spike dominance when \(\Delta r_i\) is large (NGC2403 class failure).

**Form:**

\[
\mathcal{L}_{\mathrm{sparse}} = \sum_{i} \omega(\Delta r_i)\,
\frac{|d\tau/dr_{i+1} - d\tau/dr_i|^2}{\max(|d\tau/dr_i|, \epsilon)^2}
\]

with \(\omega(\Delta r) \propto \min(1, \Delta r_{\mathrm{ref}} / \Delta r_i)\) or fixed down-weight above median Δr.

**Diagnostic (not a substitute for penalty):** flag if `delta_r_sparsity_ratio` from Phase 6C-C exceeds pre-registered limit.

### 4.6 Total objective

\[
\mathcal{L} = \mathcal{L}_{\mathrm{data}}
+ \lambda_s \mathcal{L}_{\mathrm{smooth}}
+ \lambda_c \mathcal{L}_{\mathrm{curv}}
+ \lambda_{\mathrm{inner}} \mathcal{L}_{\mathrm{inner}}
+ \lambda_{\mathrm{sparse}} \mathcal{L}_{\mathrm{sparse}}
\]

**Hyperparameter selection (pre-registered):**

- \(\lambda_s, \lambda_c, \lambda_{\mathrm{inner}}, \lambda_{\mathrm{sparse}}\) chosen on a **development subset only** (e.g. 2–3 primary pilots), then **frozen** before holdout evaluation on the full 6F cohort.
- **No per-galaxy \(\lambda\)** adjustments after seeing holdout metrics.

---

## 5. Hard gates before any Phase 6D promotion

Gates apply **per galaxy** after a Phase 6F cohort freeze. Cohort promotion requires ≥1 primary pilot passing **all** gates (same policy as 6C-D/6E unless amended here).

| ID | Gate | Pre-registered criterion |
| --- | --- | --- |
| **G1** | Radial consistency | max relative error map τ vs **6F reconstructed** profile ≤ **10⁻⁶** |
| **G2** | Smoothness (1D) | max relative adjacent dτ/dr jump ≤ **0.25** |
| **G3** | Smoothness (map) | max adjacent \|∇τ\| jump on valid mask ≤ **0.25** (Phase 6C combined metric) |
| **G4** | Inner boundary | \(|\tau(r_{\min})| \geq \tau_{\mathrm{zero}}\) **or** first-segment relative jump ≤ **0.25** |
| **G5** | Sparse-Δr spike | worst jump not solely attributable to single largest-Δr segment: `jump_failure_dominance` ≠ `sparse_delta_r_only` per 6C-C logic |
| **G6** | Holdout non-degradation | per-galaxy holdout metric within **+15%** RMSE (or equivalent) vs frozen expansion_20 row for same galaxy/model class |
| **G7** | Cohort holdout floor | 6F cohort primary success count ≥ **14/20** on pre-registered registry **or** non-inferiority test pre-registered in `phase6f_preregistration.md` |
| **G8** | Parameter control | same knot count / topology as `tdf_3knot`; no extra halo DOF; `kg_retuned=false`, `tau_refit` only within 6F protocol |
| **G9** | Audit | full smoothness + holdout + boundary diagnostics in `phase6f_*` tables |

**Phase 6D remains blocked** until a future implementation commit documents ≥1 pilot with all G1–G9 pass and cohort gate G7 satisfied.

---

## 6. Cohort design

### 6.1 Fresh cohort, not repaired expansion_20

- **Primary artifact:** `outputs/tables/phase6f_reconstructed_tau_profiles.csv` (new fits).
- **Forbidden:** overwriting `expansion20_tau_profiles.csv`, `expansion20_holdout_validation.csv`, or Phase 5 claim tables.

### 6.2 Comparison to expansion_20

| Role | expansion_20 | Phase 6F cohort |
| --- | --- | --- |
| **Purpose** | Historical Phase 5 benchmark | New smoothness-integrated reconstruction |
| **Holdout headline** | **15/20** frozen | Reported separately; not auto-merged into Phase 5 claims |
| **Profiles** | `expansion20_tau_profiles.csv` | `phase6f_reconstructed_tau_profiles.csv` |
| **Use in 6F** | Read-only baseline for G6 comparison | Primary source for new maps |

### 6.3 Galaxy registry

- **Default:** same 20-galaxy expansion_20 registry and holdout splits (pre-registered list in implementation YAML).
- **Primary pilots (map gate):** DDO161, UGC07524, UGC08490, IC2574, NGC2403 — same Tier-1 set as Phase 6B.
- **Development subset for λ tuning:** subset of primary pilots only; documented before holdout lock.

### 6.4 Freeze policy

After cohort run, commit a **Phase 6F freeze tag** with checksums for `phase6f_*` tables; subsequent map builds read only frozen 6F profiles, analogous to Phase 6C reading expansion_20.

---

## 7. Future implementation outputs (not yet created)

| Artifact | Path |
| --- | --- |
| Reconstructed profiles | `outputs/tables/phase6f_reconstructed_tau_profiles.csv` |
| Smoothness metrics | `outputs/tables/phase6f_smoothness_metrics.csv` |
| Holdout metrics | `outputs/tables/phase6f_holdout_metrics.csv` |
| Candidate ranking | `outputs/tables/phase6f_candidate_ranking.csv` |
| Decision gate report | `outputs/reports/phase6f_decision_gate_report.md` |
| Figures (per galaxy) | `outputs/figures/phase6f_{GALAXY}_tau_profile.png`, `_dtaudr_profile.png`, `_smoothness_diagnostic.png` |
| Accepted/rejected overlay | `outputs/figures/phase6f_cohort_gate_summary.png` |

**Placeholder only** — these files do not exist until an explicit implementation phase is approved.

---

## 8. Claim boundaries

Every Phase 6F report must assert:

- [ ] **No dark-matter disproof**
- [ ] **No full-SPARC validation**
- [ ] **No lensing confirmation**
- [ ] **No second-channel success yet** (6D still blocked at pre-registration time)
- [ ] **No universal τ profile claim**
- [ ] **No deflection prediction** from current `phase6c_*` / `phase6d_*` maps
- [ ] **Phase 5 15/20** remains historical unless a separate claim amendment is pre-registered

---

## 9. Implementation phases (after this document)

| Step | Label | Action |
| --- | --- | --- |
| 1 | **6F-A** | Machine-readable YAML + config loader (mirror 6C-D pattern) |
| 2 | **6F-B** | Cohort fit script + tables above |
| 3 | **6F-C** | Pseudo-2D maps from **frozen 6F** profiles only; re-run G1–G3 |
| 4 | **6F-D** | Decision gate report; update 6D block only if gates pass |

**This commit (6F pre-registration):** steps 0 — design docs only.

---

## References

- `docs/phase6e_negative_result_decision_gate.md`
- `docs/phase6d_regularized_map_results.md`
- `docs/phase6c_gradient_regularization_options.md`
- `configs/phase6d_regularization_preregistration.yaml` (closed post-hoc path)
- `docs/phase6a_2d_frozen_map_protocol.md`
