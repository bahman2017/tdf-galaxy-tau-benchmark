# Phase 6A — Pre-registered protocol: 2D / frozen-map effective-gravity test

**Status:** Design and pre-registration only — **no new fits**, **no benchmark reruns**, **no output changes**.  
**Prior validated result (unchanged):** controlled **expansion_20** radial 1D benchmark (`v0.1.6-publication-freeze`).  
**Phase 6** is a **new scientific test layer**, not an extension of the Phase 5 paper claims.

---

## 1. Scope

| Rule | Statement |
| --- | --- |
| Phase 6A role | Protocol design and pre-registration only |
| Fits | **None** in 6A |
| Frozen 1D benchmark | `outputs/tables/expansion20_*`, `controlled_expansion_final_claims.csv` — **read-only** |
| Phase 5 closure | Tags through `v0.1.6-publication-freeze`; notation: **K_g** preferred, legacy **K_tau** in frozen CSVs, **κ_tau** = field stiffness only |
| Phase 6 identity | Separate pre-registered test; results must not be merged into expansion_20 headline counts |

Supporting documents:

- [`phase6a_data_requirements.md`](phase6a_data_requirements.md)
- [`phase6a_success_failure_criteria.md`](phase6a_success_failure_criteria.md)

---

## 2. Core scientific question

> Can a galaxy-specific τ-field reconstructed from **rotation dynamics** be **frozen**, extended into a controlled **2D or axisymmetric effective-gravity map**, and then used to generate a **second-channel prediction scaffold** without fitting a separate halo model or a separate lensing-only τ-field?

**Second channel** means an independent observable class (e.g. sky-projected effective-acceleration proxy, curvature/deflection scaffold, or holdout radial prediction from the frozen map) that was **not** used to tune τ during map construction.

---

## 3. Relationship to Phase 5 (expansion_20)

| Layer | What it validates |
| --- | --- |
| **Phase 5 (closed)** | Radial 1D: even/odd holdout, **tdf_3knot** primary success **15/20**, **tdf_5knot** sensitivity-recovery **3**, NGC7814 failure, UGC00128 mixed |
| **Phase 6 (new)** | Whether a **frozen** τ-field from that radial reconstruction supports a **controlled 2D map** and a **second-channel scaffold** under explicit assumptions |

Phase 6 **does not** re-open expansion_20 success/failure counts. A Phase 6 pilot may use galaxies from the expansion_20 cohort but reports under **Phase 6 claim IDs** (to be assigned in 6B).

---

## 4. Map types (definitions and repo feasibility)

| Map type | Definition | Current repo (`v0.1.6`) | Future data needed |
| --- | --- | --- | --- |
| **A. Axisymmetric pseudo-2D τ-map** | τ₂D(x,y) = τ_radial(R), R = cylindrical radius in disk plane; derived from frozen 1D τ(r) only | **Attemptable** — `expansion20_tau_profiles.csv`, `sparc_rotmod_standardized.csv`, photometry `inclination_deg` | None for axisymmetric scaffold |
| **B. Sky-projected τ-map** | τ_sky(α,δ) or projected plane coordinates via inclination + systemic geometry; still τ(R) underneath | **Attemptable** with metadata — inclination/distance in `sparc_photometry_metadata.csv`; no full WCS image pipeline yet | Optional: verified astrometry / image headers |
| **C. True 2D τ-map (baryonic source)** | Solve or constrain τ(x,y) from 2D Poisson-like mother-field equation with source J_τ(x,y) ∝ Σ_b(x,y) | **Not attemptable as validated true-2D** — repo has **scalar** disk/bulge surface brightness per radius (`sb_disk_lpc2`, `sb_bulge_lpc2`), not pixel Σ_b(x,y) maps | 2D photometry / mass maps (e.g. Spitzer 3.6 μm images, HI moment maps) |
| **D. Deflection / lensing proxy map** | κ_proxy or deflection-angle scaffold from ∇τ (not full GR lensing pipeline) | **Future-only (Phase 7)** — no lensing observations or forward model in repo | External lensing catalogs, mass-sheet priors, ray-tracing protocol |

**Critical distinction:** Map type **A** is **not** the same as map type **C**. Claiming “2D validation” requires type **C** data and success criteria; type **A** may only be labeled **axisymmetric pseudo-2D extension**.

---

## 5. Frozen-map rule (non-negotiable)

1. **τ is fixed from rotation dynamics first** using the Phase 2A / expansion_20 radial closure at fixed **K_g** (legacy CSV label **K_tau**).
2. The **same frozen τ-map** (or its axisymmetric embedding) is used for any second-channel prediction.
3. **No separate lensing-only τ-field** fitted only to lensing data.
4. **No NFW/Burkert halo** added in the TDF second-channel stage (halo baselines may appear only as **comparison proxies**, not as part of the frozen τ construction).
5. **No retuning** of τ amplitudes, knot counts, or **K_g** when evaluating the second channel.

Optional: document a **single** global smoothing parameter applied to the map for numerical stability, fixed **before** second-channel evaluation and recorded in the protocol registry.

---

## 6. Mathematical protocol (documentation only)

### 6.1 Radial dynamics (frozen 1D — already validated in Phase 5)

\[
v_{\mathrm{obs}}^2(r) = v_{\mathrm{bar}}^2(r) + v_\tau^2(r)
\]

\[
v_\tau^2(r) = r\, K_g\, \frac{d\tau}{dr}
\]

\[
\frac{d\tau}{dr} = \frac{v_{\mathrm{obs}}^2(r) - v_{\mathrm{bar}}^2(r)}{r\, K_g}
\]

- **K_g**: fixed gravitational projection coefficient (internal code; frozen outputs may label **K_tau**).
- **κ_tau**: mother-field **stiffness** in the full TDF framework — **not** used as K_g in this benchmark closure.

### 6.2 Axisymmetric pseudo-2D embedding (Phase 6 primary near-term)

Let plane coordinates (x, y) be in the disk plane, R = √(x² + y²):

\[
\tau_{2\mathrm{D}}(x,y) = \tau_{\mathrm{radial}}(R)
\]

where τ_radial is interpolated from the **frozen** radial profile (no refit).

Effective-gravity scaffold from the projection closure:

\[
\mathbf{g}_\tau(x,y) = -K_g\, \nabla \tau_{2\mathrm{D}}(x,y)
\]

In axisymmetry, only the radial component of ∇τ is nonzero by construction; azimuthal structure is **assumed absent**, not measured.

### 6.3 True 2D mother-field model (future — not implemented in 6A/6B)

For reference only (full TDF field layer):

\[
\kappa_\tau\, \nabla^2 \tau(x,y) - V'(\tau) = J_\tau(x,y)
\]

with J_τ(x,y) tied to baryonic surface density Σ_b(x,y). **Phase 6A does not implement** this PDE solve. It is listed so Phase 6B/6C do not confuse pseudo-2D embedding with true 2D source reconstruction.

### 6.4 Second-channel scaffold (to be operationalized in 6C)

Examples (one primary per pilot study; pre-register in 6B):

- **S1:** Predict holdout radial velocities from g_τ(R) vs observed (consistency check, not a new holdout contest).
- **S2:** Predict a proxy “extra acceleration” field magnitude map vs baryonic-only ∇Φ_bar.
- **S3:** Deflection-angle proxy α_proxy ∝ |∇τ| (Phase 7 precursor; **not** lensing confirmation).

---

## 7. Candidate pilot galaxies (selection criteria only)

**Do not finalize the pilot list in 6A** — Phase **6B** audits data coverage per galaxy.

### Inclusion criteria (proposed)

| Criterion | Rationale |
| --- | --- |
| `counts_as_primary_success == True` in `expansion20_failure_mode_summary.csv` | Prefer galaxies with validated **tdf_3knot** robust holdout in expansion_20 |
| `failure_mode_classification == robust_tdf_success` | Exclude canonical failure and sensitivity-only primary labels |
| ≥ N_min radial points (e.g. N_min ≥ 12) in `sparc_rotmod_standardized.csv` | Stable τ(r) interpolation |
| Monotonic or mild negative-residual policy documented | Reconstruction quality |
| `inclination_deg` present in `sparc_photometry_metadata.csv` | Sky projection / plane geometry |
| `distance_mpc` present | Scale conversion |
| Holdout test RMSE ratio tdf_3knot / best baseline not extreme outlier | Stability |

### Exclusion criteria (proposed)

| Criterion | Rationale |
| --- | --- |
| **NGC7814** | Canonical all-TDF failure — **exclude from primary pilot** |
| `sensitivity_recovery` or `mixed_result` | Not primary 1D success — optional diagnostic tier only |
| **UGC00128** | Mixed near-tie — **diagnostic only**, not primary pilot |
| Missing photometry metadata | Cannot define plane geometry |
| Very high holdout RMSE or irregular τ(r) | Map instability risk |

### Illustrative tier (not final selection)

From frozen `expansion20_failure_mode_summary.csv`, galaxies satisfying **robust_tdf_success** include (alphabetical): DDO154, DDO161, IC2574, NGC0289, NGC2403, NGC3198, NGC6015, NGC6503, NGC7793, UGC02953, UGC06787, UGC07524, UGC08490, UGC09133, UGC11455. **Phase 6B** ranks by radial point count, τ smoothness, and metadata completeness.

---

## 8. Success / failure criteria

Detailed metrics: [`phase6a_success_failure_criteria.md`](phase6a_success_failure_criteria.md).

Summary:

- **Success:** frozen map reproduces radial τ(r); smooth pseudo-2D map; second-channel scaffold generated without τ retuning; failures reported honestly.
- **Failure:** allowed and documented (instability, tuning dependence, missing 2D data, mislabeled lensing).

---

## 9. Claim boundaries (Phase 6)

Phase 6 must **never** claim:

- dark matter is disproven;
- full-SPARC validation;
- lensing confirmation;
- a universal τ-profile across galaxies;
- true 2D τ reconstruction **without** 2D baryonic data;
- axisymmetric pseudo-2D map **equals** a true baryonic 2D map;
- ΛCDM replacement.

Allowed language:

- “controlled pilot under pre-registered Phase 6 protocol”;
- “axisymmetric pseudo-2D extension of frozen radial τ”;
- “second-channel **scaffold**” (not confirmation);
- “deflection **proxy**” (not lensing test).

---

## 10. Phase 6B recommendation

**Phase 6B — data availability audit and pilot galaxy selection**

Deliverables:

1. Per-galaxy checklist against [`phase6a_data_requirements.md`](phase6a_data_requirements.md) for all expansion_20 IDs.
2. Ranked shortlist (e.g. 3–5 galaxies) for axisymmetric pseudo-2D pilot.
3. Explicit statement which map types (A/B/C/D) are **in scope** for 6C implementation.
4. Draft Phase 6C implementation plan (frozen-map construction script spec only).

**No fits in 6B** unless explicitly approved after audit sign-off.

---

## 11. Phase lineage

| Phase | Role |
| --- | --- |
| 5G | Notation migration (closed) |
| 5H | Publication freeze (closed) |
| 5I | Release notes (closed) |
| **6A** | **This protocol** |
| 6B | Data audit + pilot selection |
| 6C | Implement frozen-map construction (pilot) |
| 6D | Second-channel scaffold evaluation |
| 7 | Lensing/deflection with external data (future) |
