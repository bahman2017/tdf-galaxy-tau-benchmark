# Phase 6B — Data availability audit (expansion_20)

**Status:** Audit and pilot selection complete — **no new fits**, **no expansion_20 rerun**, **no τ-map construction**.

Companion: [`phase6b_pilot_selection_rationale.md`](phase6b_pilot_selection_rationale.md)

**Reproduce:**

```bash
python3 scripts/build_phase6b_data_availability_audit.py
```

**Outputs:**

| Artifact | Path |
| --- | --- |
| Per-galaxy audit | `outputs/tables/phase6b_expansion20_data_availability_audit.csv` |
| Ranking | `outputs/tables/phase6b_pilot_candidate_ranking.csv` |
| Report | `outputs/reports/phase6b_pilot_selection_report.md` |

---

## Scope

- Cohort: frozen **expansion_20** (20 galaxies).
- Sources: committed rotmod, photometry metadata, expansion_20 frozen tables only.
- Phase 5 headline (**15/20** primary `tdf_3knot` success) is **unchanged**.

---

## L1 — Rotation-curve availability

| Field | Meaning |
| --- | --- |
| `n_radial_points` | Count of rotmod rows |
| `r_min_kpc`, `r_max_kpc`, `radial_coverage_kpc` | Radial span |
| `v_obs_available`, `v_err_available` | Finite observed velocities and errors |
| `l1_rotation_available` | Passes N_min and coverage gates |

**Missing-data:** no rotmod rows → L1 fail; galaxy ineligible for map construction.

---

## L2 — Baryonic model availability

| Field | Meaning |
| --- | --- |
| `v_bar_available` | Finite `v_bar_kms` |
| `v_gas/disk/bulge_available` | Component flags |
| `missing_baryonic_component_flag` | Any component non-finite |
| `baryonic_sufficient_for_scaffold` | L2 pass for frozen-map scaffold |

Uses **fixed canonical** SPARC baryons (same as expansion_20).

---

## L3 — Frozen TDF profile availability

| Field | Meaning |
| --- | --- |
| `frozen_tau_profile_available` | `tau_reconstructed` in `expansion20_tau_profiles.csv` |
| `frozen_dtaudr_available` | `dtaudr_reconstructed` present |
| `frozen_K_tau_value` | Legacy CSV label (= **K_g** projection) |
| `K_g_config_value` | From `configs/reconstruction.yaml` |
| `frozen_tdf_3knot_profile_exists` | Row in `expansion20_model_comparison.csv` |
| `failure_mode_classification` | Phase 5 frozen label |
| `holdout_stable_for_primary_pilot` | `tdf_3knot` even/odd RMSE ≤ 10 km/s gate |

**Notation:** **K_g** preferred; **κ_tau** is stiffness only (not in this audit).

---

## L4 — Geometry / projection metadata

| Field | Meaning |
| --- | --- |
| `distance_mpc` | Photometry (preferred) or rotmod |
| `inclination_deg` | SPARC Table-1 via Phase 4J |
| `position_angle_available` | **False** for all cohort (not in ingested Table-1 columns) |
| `geometry_complete_flag` | Distance + inclination in [30°, 90°] |
| `axisymmetric_pseudo_2d_attemptable` | L1–L3 pass |
| `map_type_sky_projected` | `attemptable` if L4 pass, else `future_only` |

**Missing-data:** missing inclination → axisymmetric in-plane map may still be defined; sky projection deferred.

---

## L5 — Photometry / surface-density metadata

| Field | Meaning |
| --- | --- |
| `sb_disk_profile_points`, `sb_bulge_profile_points` | Per-radius 1D SB in rotmod |
| `surface_brightness_1d_profile` | `available` if any SB points |
| `true_2d_pixel_map_available` | Always **False** in repo |
| `true_2d_status` | Always **`future_only`** |
| `map_type_true_2d_sigma_b` | **`future_only`** |

No pixel-level Σ_b(x,y) maps are committed.

---

## L6 — Second-channel / lensing data

| Field | Meaning |
| --- | --- |
| `l6_second_channel_lensing_data` | Always **False** |
| `lensing_status` | **`future_only_not_confirmed`** |
| `map_type_deflection_lensing_proxy` | **`future_only`** |

---

## Map types attemptable now (v0.1.6)

| Type | Status |
| --- | --- |
| Axisymmetric pseudo-2D τ(R) | **Attemptable** for all 20 galaxies (L1–L3 pass) |
| Sky-projected embedding | **Attemptable** when L4 passes (all 20 in cohort) |
| True 2D Σ_b source map | **Future-only** |
| Lensing / deflection confirmation | **Future-only** |

---

## Pre-registered Phase 6C numeric thresholds

Defined in `src/tdf_galaxy_tau/analysis/phase6b_data_availability.py`:

| Parameter | Value |
| --- | --- |
| `N_min` radial points | 12 |
| Min radial coverage | 5.0 kpc |
| Inclination range | 30°–90° |
| Max extrapolation beyond r_max | 5% (Phase 6C implementation) |
| Max relative adjacent dτ/dr jump | 0.25 |
| τ radial match tolerance (relative) | 10⁻⁶ |
| Max `tdf_3knot` holdout RMSE for **primary pilot** | **10.0 km/s** |

---

## Missing-data handling summary

| Situation | Action |
| --- | --- |
| Missing L1 | Ineligible for Phase 6C |
| Missing L2 | Ineligible |
| Missing L3 frozen τ | Ineligible |
| Missing L4 | Tier-2/diagnostic; in-plane axisymmetric only |
| Missing true 2D | Do not claim true 2D |
| Missing lensing | Proxy only in Phase 7+; never “confirmed” |
