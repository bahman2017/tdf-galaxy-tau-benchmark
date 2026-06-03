# Phase 6C-C — Gradient regularization options (pre-registration draft)

**Status:** Protocol and options only. **No option is applied in Phase 6C-C.**

Companion diagnostics: `outputs/tables/phase6c_primary_pilot_gradient_diagnostics.csv`,  
`outputs/reports/phase6c_gradient_diagnostic_report.md`

---

## Why this document exists

All five Tier-1 primary pilots pass **radial consistency** on pseudo-2D maps but fail the pre-registered **smoothness** gate (relative adjacent dτ/dr jump ≤ **0.25**). Failures trace to **frozen** `expansion20_tau_profiles.csv`, not to 6C map retuning. Phase **6D** (second-channel scaffold) remains **blocked** until a future **Phase 6C-D** implementation passes both gates under explicit pre-registration.

---

## Options (not implemented)

### Option R1 — Pre-smooth dτ/dr before map embedding

| Aspect | Detail |
| --- | --- |
| **What it would change** | Apply a fixed-kernel or Savitzky–Golay smooth to **dτ/dr** (or τ) on the radial grid before τ₂D(R) interpolation. |
| **What it must not change** | Phase 5 expansion_20 holdout metrics, frozen benchmark CSVs, or **K_g**; no per-galaxy tuning of kernel width from lensing/second-channel data. |
| **Overfitting risk** | Medium — kernel width could be tuned to pass smoothness while degrading rotation-curve fidelity. |
| **Required validation** | Even/odd holdout RMSE vs frozen baseline; radial consistency τ₂D = τ_radial; document max Δ(dτ/dr) change. |
| **Phase 6C-D pre-registration** | **Required** — kernel family, width bounds, and pass/fail gates fixed before any apply. |

### Option R2 — Bounded relative jump constraint (clip / cap)

| Aspect | Detail |
| --- | --- |
| **What it would change** | Enforce \|Δ(dτ/dr)\| / \|dτ/dr\| ≤ 0.25 between adjacent radial points (or cap absolute Δ). |
| **What it must not change** | Unconstrained refit of knot amplitudes for second-channel targets; Phase 5 primary success counts. |
| **Overfitting risk** | Low–medium if cap is global; high if cap is per-galaxy. |
| **Required validation** | Report number of capped segments; rotation-curve residual impact at capped radii. |
| **Phase 6C-D pre-registration** | **Required** — global cap only; per-galaxy caps prohibited without new cohort protocol. |

### Option R3 — Spline τ(r) with roughness penalty

| Aspect | Detail |
| --- | --- |
| **What it would change** | Re-represent τ(r) as a penalized spline on the SPARC radial grid; derive dτ/dr analytically from spline. |
| **What it must not change** | Phase 2A / expansion_20 **frozen** τ table (unless full rerun explicitly approved); **K_g**. |
| **Overfitting risk** | High — penalty λ is a free hyperparameter. |
| **Required validation** | Holdout RMSE non-inferiority vs tdf_3knot; AIC/BIC comparison; smoothness pass on derived dτ/dr. |
| **Phase 6C-D pre-registration** | **Required** — λ grid pre-registered; no lensing-driven λ selection. |

### Option R4 — Knot-count selection with map-smoothness penalty

| Aspect | Detail |
| --- | --- |
| **What it would change** | Select knot count using holdout + λ_smooth · max_rel_jump(dτ/dr) in objective. |
| **What it must not change** | Phase 5 **15/20** primary headline without a new expansion cohort; retroactive relabeling of sensitivity cases. |
| **Overfitting risk** | High — extra penalty term tuned on N=5 pilots. |
| **Required validation** | Full expansion_20 re-benchmark or a new pre-registered pilot-only rerun policy. |
| **Phase 6C-D pre-registration** | **Required** — likely needs **new fits** → new scientific phase, not silent 6C patch. |

### Option R5 — Holdout-aware regularization only

| Aspect | Detail |
| --- | --- |
| **What it would change** | Regularize dτ/dr only where holdout errors are insensitive (e.g. outer disk). |
| **What it must not change** | Inner-radius structure that drives holdout success on DDO161-like systems. |
| **Overfitting risk** | Medium — region mask could chase holdout noise. |
| **Required validation** | Per-region holdout tables; show inner-region jumps preserved or documented. |
| **Phase 6C-D pre-registration** | **Required** — mask rules fixed from rotmod geometry, not from map outcomes. |

### Option R6 — Exclude unstable boundary radii

| Aspect | Detail |
| --- | --- |
| **What it would change** | Truncate map domain to [r_min + δ, r_max − δ] where jumps exceed threshold. |
| **What it must not change** | Claim of full radial coverage from SPARC; must report excluded fraction (<5% extrapolation rule). |
| **Overfitting risk** | Low if δ is fixed globally (e.g. inner 1 point + outer 1 point). |
| **Required validation** | Map valid_mask metadata; second-channel scaffold only on retained domain. |
| **Phase 6C-D pre-registration** | **Required** — δ rule global; document NGC2403 / inner-τ=0 cases. |

### Option R7 — Report failure (no regularization)

| Aspect | Detail |
| --- | --- |
| **What it would change** | Nothing — Phase 6D blocked; publish pseudo-2D maps as **negative** map-smoothness result. |
| **What it must not change** | Frozen Phase 5 benchmark; conservative claim boundaries. |
| **Overfitting risk** | None |
| **Required validation** | N/A |
| **Phase 6C-D pre-registration** | **Not required** — default if no option passes validation. |

---

## Recommended default for Phase 6C-D (if approved)

1. Pre-register **R2 + R6** (global jump cap + documented boundary trim) as the **minimal** intervention.  
2. Treat **R1** as sensitivity only.  
3. Treat **R3/R4** as **new-fit phases**, not 6C-D hotfixes.  
4. Any applied regularization must re-run **radial consistency** and **smoothness** gates before Phase 6D.

---

## Claim boundaries (unchanged)

- No dark-matter disproof; no full-SPARC validation; no lensing confirmation; no true 2D Σ_b map.  
- Regularization options are **not** results — they are a future protocol menu only.
