# Phase 6A — Data requirements for frozen-map test

Companion to [`phase6a_2d_frozen_map_protocol.md`](phase6a_2d_frozen_map_protocol.md).

**Phase 6A:** requirements specification only — **no ingestion, no new fits**.

---

## 1. Data layers

| Layer | Purpose in Phase 6 |
| --- | --- |
| **L1 — Rotation dynamics (required)** | Freeze τ(r) from residuals |
| **L2 — Baryonic decomposition (required)** | v_bar(r), component velocities |
| **L3 — Geometry (required for map embedding)** | Inclination, distance, optional PA |
| **L4 — Surface photometry (optional / future true-2D)** | Σ_b(x,y) maps |
| **L5 — Second-channel observations (optional)** | Lensing, kinematics cross-checks |
| **L6 — Uncertainty (required)** | Propagate v_err, map regularization |

---

## 2. Required data (minimum viable — map type A)

| Field | Source in repo (v0.1.6) | Notes |
| --- | --- | --- |
| `galaxy_id` | All tables | Join key |
| `r_kpc` | `sparc_rotmod_standardized.csv` | Strictly positive radii |
| `v_obs_kms`, `v_err_kms` | Same | Rotation curve |
| `v_bar_kms` | Same | Fixed canonical baryons (expansion_20 policy) |
| `v_gas_kms`, `v_disk_kms`, `v_bulge_kms` | Same | Audit decomposition |
| Frozen `tau_reconstructed`, `dtaudr_reconstructed` | `expansion20_tau_profiles.csv` (or recompute from frozen policy) | Must match Phase 5 frozen **K_tau** column values |
| Fixed `K_g` | `configs/reconstruction.yaml` (legacy keys) / internal `k_g` | No refit in Phase 6 |
| `distance_mpc` | `sparc_rotmod_standardized.csv`, `sparc_photometry_metadata.csv` | Scale |
| `inclination_deg` | `sparc_photometry_metadata.csv` | Disk plane → sky |
| Negative-residual policy | `configs/reconstruction.yaml` | Document per galaxy |

**Repo status:** **Available** for all expansion_20 galaxies with rotmod rows.

---

## 3. Optional but recommended (map type B)

| Field | Source in repo | Gap |
| --- | --- | --- |
| Position angle (PA) | Not in standardized rotmod; may be in VizieR working copy only | **6B:** check Table 1 / literature |
| `disk_scale_length_kpc`, `luminosity_3p6_lsun` | `sparc_photometry_metadata.csv` | Morphology context |
| `sb_disk_lpc2`, `sb_bulge_lpc2` | Per-radius in rotmod | **1D SB profile**, not 2D image |
| `morphological_type` | Photometry metadata | Selection stratification |
| Quality flags | `quality_flag`, `photometry_quality_flag` | Exclude poor metadata |

---

## 4. Required for true 2D map (map type C) — **not in repo**

| Field | Needed | Repo status |
| --- | --- | --- |
| 2D stellar surface density Σ_★(x,y) | Spitzer/IRAC or equivalent | **Missing** (scalar SB per r only) |
| 2D gas surface density Σ_gas(x,y) | HI 2D or stacked | **Missing** |
| PSF / mask / inclination-corrected disk model | True 2D source J_τ | **Missing** |
| κ_tau field equation boundary conditions | Full PDE domain | **Not specified** in benchmark repo |

**Conclusion:** True 2D τ-map claims are **future-only** until external 2D maps are ingested under a new data phase.

---

## 5. Second-channel / lensing (map type D) — **future-only**

| Field | Purpose | Repo status |
| --- | --- | --- |
| Einstein radius / shear catalog | Compare to proxy | **Missing** |
| Lensing images or ray-tracing inputs | Confirmation test | **Missing** |
| Independent kinematics (e.g. gas at large R) | Cross-check | Partial (same rotmod only) |

Deflection proxies may be computed from ∇τ in Phase 6C/7 but must be labeled **proxy**, not lensing confirmation.

---

## 6. Uncertainty model (required specification in 6B)

| Element | Requirement |
| --- | --- |
| Radial velocity errors | Use `v_err_kms`; document if inflated for map regularization |
| τ reconstruction uncertainty | Optional: bootstrap on holdout splits — **not** in frozen Phase 5 tables |
| Map smoothing | Fixed kernel width ΔR or Δx; record in registry |
| Interpolation | Linear τ(R) between radial grid; document edge extrapolation |

---

## 7. Missing-data handling (protocol rules)

| Situation | Rule |
| --- | --- |
| Missing inclination | Galaxy **ineligible** for sky-projected map (type B); may still allow type A in plane |
| Missing distance | Use rotmod distance if present; else **exclude** |
| Sparse radial points | Require N ≥ N_min; else exclude or flag “low resolution” |
| Negative residuals policy `mask_negative` | Document reduced radial extent |
| No photometry row | Eligible for type A only; flag “no morphology metadata” |

---

## 8. Data explicitly out of scope for Phase 6A/B

- Refitting expansion_20 holdout contests
- Changing frozen `expansion20_holdout_validation.csv`
- Ingesting full SPARC (175 galaxies) as Phase 6 validation
- Adding halo parameters to τ freeze step

---

## 9. Phase 6B audit outputs (expected)

| Output | Description |
| --- | --- |
| `docs/phase6b_data_availability_audit.md` (planned) | Per-galaxy matrix: L1–L6 satisfied? |
| `outputs/tables/phase6b_pilot_candidate_ranking.csv` (planned) | Ranked pilots — **new file in 6B only** |
| Map-type scope statement | A+B in 6C; C+D deferred |

---

## 10. Notation on data labels

- Frozen CSV column **`K_tau`** in `expansion20_tau_profiles.csv` is the legacy label for the fixed projection coefficient (**K_g**).
- Config keys `k_tau` / `K_tau` remain valid via Phase 5G alias layer.
- **κ_tau** must not appear as a column substitute for **K_tau** / **K_g** in Phase 6 data joins.
