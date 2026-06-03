# Phase 6B — Pilot galaxy selection rationale

**Phase 6B does not update the Phase 5 expansion_20 result (15/20 primary `tdf_3knot` robust holdout success).**

Reproduce ranking: `python3 scripts/build_phase6b_data_availability_audit.py`

---

## Selection criteria (pre-registered)

1. **Cohort membership:** frozen expansion_20 (`expansion20_subset_selection.csv`).
2. **Primary expansion_20 success:** `failure_mode_classification == robust_tdf_success` and `counts_as_primary_success_expansion20 == True`.
3. **Stable holdout:** `tdf_3knot` even/odd holdout RMSE ≤ **10.0 km/s** (conservative gate).
4. **Radial coverage:** ≥ 12 points and ≥ 5 kpc span (matches expansion selection protocol).
5. **Geometry:** distance and inclination in SPARC photometry metadata; inclination 30°–90°.
6. **Frozen τ:** `expansion20_tau_profiles.csv` with traceable **K_tau** (= **K_g**).
7. **Exclusions:** **NGC7814** (all-TDF failure); **UGC00128** (mixed near-tie); **tdf_5knot sensitivity-recovery** cases as non-primary.

**Ranking score** (tier-1 only): 35% holdout stability + 25% n_points + 15% coverage + 15% τ-gradient scale + 10% geometry completeness.

---

## Tiered candidates

### Tier 1 — Primary pilots (top 5 by score)

| Rank | Galaxy | Holdout RMSE (km/s) | n_points | Coverage (kpc) |
| --- | --- | --- | --- | --- |
| 1 | **DDO161** | 0.72 | 31 | 12.8 |
| 2 | **UGC07524** | 1.63 | 31 | 10.3 |
| 3 | **UGC08490** | 1.13 | 30 | 9.8 |
| 4 | **IC2574** | 2.98 | 34 | 9.4 |
| 5 | **NGC2403** | 8.66 | 73 | 20.7 |

These five are flagged `is_primary_pilot == True` in the audit CSV.

### Tier 1 — Alternate primary candidates (same tier, not top-5)

- **NGC6015**, **DDO154**, **NGC7793**, **NGC6503** — robust success, stable holdout, full L1–L4; suitable backups if a pilot is deferred in 6C.

### Tier 2 — Diagnostic

- **UGC00128** — mixed near-tie; **not** primary expansion_20 success.
- **NGC5055**, **UGC05253**, **UGC12506** — `tdf_5knot` sensitivity-recovery only.
- **NGC0289**, **NGC3198**, **UGC02953**, **UGC06787**, **UGC09133**, **UGC11455** — robust in Phase 5 but holdout RMSE **> 10 km/s** or borderline instability; useful for stress tests, not first frozen-map pilots.

### Tier 3 — Avoid / defer as primary

- **NGC7814** — canonical all-TDF holdout failure; case-study only.

---

## Why NGC7814 is excluded

Canonical **all-TDF failure** on expansion_20 holdout; NFW refit wins. Using it as a Phase 6 primary pilot would conflate map-construction tests with known 1D reconstruction failure.

---

## Why UGC00128 is diagnostic-only

**Mixed near-tie:** NFW marginally best on holdout; not counted in **15/20** primary successes. Useful to test frozen-map behavior near baseline degeneracy, not for headline Phase 6 claims.

---

## Claim boundaries

- No dark-matter disproof.
- No full-SPARC validation (20-galaxy audit only).
- No lensing confirmation.
- No universal τ profile.
- Axisymmetric pseudo-2D ≠ true 2D Σ_b map.

---

## Recommended Phase 6C step

Implement **frozen axisymmetric pseudo-2D** τ-map construction for **DDO161** first (best holdout stability + coverage), then replicate script on the other four primary pilots without τ retuning.

## Phase 6C status (all Tier-1 pilots)

See [`phase6c_primary_pilot_map_results.md`](phase6c_primary_pilot_map_results.md).

```bash
python3 scripts/build_phase6c_frozen_pseudo2d_map.py --all-primary-pilots
```

- Five maps under `outputs/maps/phase6c/`
- Combined audit: `outputs/reports/phase6c_primary_pilot_smoothness_audit.md`
