# Phase 6C-D — Pre-registered frozen-gradient regularization protocol

**Status:** Pre-registration and acceptance criteria only. **No τ modification**, **no map regeneration**, **no fits**, **Phase 6D blocked.**

Machine-readable registry: `configs/phase6d_regularization_preregistration.yaml`  
Acceptance detail: [`phase6d_regularization_acceptance_criteria.md`](phase6d_regularization_acceptance_criteria.md)

---

## 1. Scope (map-construction only)

| Layer | Treatment |
| --- | --- |
| **Phase 5 expansion_20** | **Frozen** — holdout counts, `expansion20_tau_profiles.csv`, all `expansion20_*` benchmark tables |
| **Phase 6C-B maps** | **Frozen** — diagnostic baseline; not overwritten |
| **Future regularized profiles** | **New files only** under `outputs/tables/phase6d_*` |
| **Future regularized maps** | **New files only** under `outputs/maps/phase6d/` |
| **Phase 6D second-channel** | **Blocked** until implementation passes all gates below |

This is a **pre-registered repair attempt** for diagnosed map-smoothness failure (Phase 6C-C). It is **not** a successful second-channel, lensing, or true-2D result.

---

## 2. Scientific motivation (Phase 6C-C summary)

- Five Tier-1 pilots: radial consistency **5/5 PASS**; smoothness **0/5 PASS** (threshold **0.25**).
- Failures inherit from **frozen 1D dτ/dr** in `expansion20_tau_profiles.csv`, dominated by **inner-radius instability** (τ≈0 at r_min) and, for **NGC2403**, **sparse Δr**.
- **K_g** remains **1.0** (legacy CSV **K_tau**); **κ_tau** is not used as projection.

**Pre-registered intervention pair:** **R2** (global jump cap) + **R6** (boundary trim). Options R1, R3, R4, R5 remain out of scope unless a new protocol is written.

---

## 3. Option R2 — Global relative jump cap (exact rule)

| Parameter | Value |
| --- | --- |
| **Threshold** | **0.25** (relative adjacent jump on **dτ/dr**) |
| **Quantity** | `dtaudr_reconstructed` on the SPARC radial grid (sorted by `r_kpc`) |
| **Relative jump** | \(\|d\tau/dr_{i+1} - d\tau/dr_i\| / \max(\|d\tau/dr_i\|, 10^{-12})\) |
| **Application** | Single forward sweep \(i = 0 \ldots N-2\): if jump > 0.25, adjust **only** \(d\tau/dr_{i+1}\) minimally toward \(d\tau/dr_i\) so jump = 0.25 |
| **Sign** | **Preserved** — no sign flip of \(d\tau/dr\) |
| **Monotonicity** | **Not required** for τ or dτ/dr |
| **τ after cap** | **Re-integrate** τ from r_min with **τ(r_min) unchanged** (trapezoidal cumulative along r) |
| **Max segments capped** | ≤ **40%** of \(N-1\) segments |
| **Fail if** | Fraction of capped segments > **40%** |
| **Audit** | Per-segment: r, dτ/dr before/after, correction magnitude, capped flag |

**Not allowed:** per-galaxy thresholds, smoothing kernels (R1), or knot refits (R4).

---

## 4. Option R6 — Boundary trim (exact rule)

Applied **after R2** on the regularized profile.

### Inner rule

Trim up to **1** innermost point if **either**:

- `|tau_reconstructed(r_min)| < 10^{-9}`, or  
- First-segment relative dτ/dr jump (on pre-R2 frozen profile) > **0.25**

### Outer rule

Trim up to **1** outermost point if **either**:

- Last-segment relative dτ/dr jump > **0.25**, or  
- Phase 6C-C `worst_jump_region == outer_third` **and** last-segment jump > **0.25**

### Global trim limits

| Limit | Value |
| --- | --- |
| Max fraction of points trimmed | **10%** |
| Fail if trim fraction exceeds | **10%** |
| Min remaining points | **12** (Phase 6B N_min) |
| Min remaining coverage | **5.0 kpc** (Phase 6B) |

### Map embedding

- Trimmed radii **excluded** from τ₂D interpolation domain.  
- `valid_mask = false` outside retained \([r_{\min}^+, r_{\max}^-]\).  
- Outer grid extrapolation still ≤ **5%** beyond retained r_max (Phase 6B policy).

### Radial consistency (post-implementation)

Maps must match the **regularized Phase 6 profile**, not the frozen `expansion20` table, with relative error ≤ **10⁻⁶**.

---

## 5. Phase lineage

| Phase | Role |
| --- | --- |
| **6C-D** | **This document** — pre-registration only |
| **6C-E** | Implementation: R2+R6 → regularized profiles, maps, audits |
| **6D** | Second-channel scaffold — **blocked** until ≥1 pilot passes all gates |

---

## 6. Required future outputs (6C-E)

Per galaxy (`GALAXY` ∈ primary pilots):

- `outputs/tables/phase6d_{GALAXY}_regularized_profile.csv`
- `outputs/tables/phase6d_{GALAXY}_correction_audit.csv`
- `outputs/maps/phase6d/{GALAXY}_regularized_pseudo2d_tau_map.npz`

Combined:

- `outputs/tables/phase6d_regularized_map_summary.csv`
- `outputs/reports/phase6d_regularization_report.md`

---

## 7. Claim boundaries (unchanged)

- No dark-matter disproof; no full-SPARC validation; no lensing confirmation; no universal τ profile.  
- **Axisymmetric pseudo-2D regularized** — not true 2D Σ_b.  
- Failure after regularization is a **valid negative outcome**; Phase 6D stays blocked.

---

## 8. Negative outcome policy

If **zero** pilots pass all gates after R2+R6:

- Report as **negative map-smoothness repair result**.  
- Do **not** update Phase 5 **15/20**.  
- Do **not** claim second-channel or lensing success.  
- Recommend publication of 6C-B/6C-C diagnostic + this protocol as methods appendix material only.
