# Phase 6C primary-pilot frozen pseudo-2D map results

**Phase 6C-B** — axisymmetric pseudo-2D embedding only; **no new fits**, **no τ smoothing**, **no K_g retuning**.

Reproduce:

```bash
python3 scripts/build_phase6c_frozen_pseudo2d_map.py --all-primary-pilots
# or per galaxy:
python3 scripts/build_phase6c_frozen_pseudo2d_map.py --galaxy-id UGC07524
```

Combined audit: `outputs/reports/phase6c_primary_pilot_smoothness_audit.md`  
Summary table: `outputs/tables/phase6c_primary_pilot_map_summary.csv`

---

## Primary pilots (Tier-1)

| Galaxy | Radial consistency | Smoothness (≤0.25) | Phase 6D ready |
| --- | --- | --- | --- |
| DDO161 | PASS (0.0) | FAIL (10.85; frozen dτ/dr) | **No** |
| UGC07524 | PASS (0.0) | FAIL (5.35; frozen dτ/dr) | **No** |
| UGC08490 | PASS (0.0) | FAIL (0.38; frozen dτ/dr) | **No** |
| IC2574 | PASS (0.0) | FAIL (2.42; frozen dτ/dr) | **No** |
| NGC2403 | PASS (0.0) | FAIL (116.12; frozen dτ/dr) | **No** |

All five maps pass **radial consistency** (machine precision vs frozen `expansion20_tau_profiles.csv`).  
**None** pass the pre-registered **smoothness** gate (threshold **0.25**). Failures are inherited from **frozen 1D dτ/dr** jumps, not from 6C map retuning.

---

## Phase 6D gate

**Phase 6D is blocked** until at least one pilot passes both radial consistency and smoothness.

**Phase 6C-C complete:** see `outputs/reports/phase6c_gradient_diagnostic_report.md` and `docs/phase6c_gradient_regularization_options.md`.

**Recommended next step:** Phase **6C-D** — pre-registered regularization (if approved) before Phase 6D.

---

## Claim boundaries

- Axisymmetric pseudo-2D only; **not** true 2D Σ_b(x,y).
- **No** lensing confirmation; **no** dark-matter disproof; **no** full-SPARC validation.
- Does **not** update Phase 5 expansion_20 (**15/20** primary `tdf_3knot` success).

---

## Artifacts per galaxy

| Galaxy | NPZ | Metadata |
| --- | --- | --- |
| DDO161 | `outputs/maps/phase6c/DDO161_frozen_pseudo2d_tau_map.npz` | `phase6c_DDO161_frozen_pseudo2d_map_metadata.csv` |
| UGC07524 | `outputs/maps/phase6c/UGC07524_frozen_pseudo2d_tau_map.npz` | `phase6c_UGC07524_frozen_pseudo2d_map_metadata.csv` |
| UGC08490 | `outputs/maps/phase6c/UGC08490_frozen_pseudo2d_tau_map.npz` | `phase6c_UGC08490_frozen_pseudo2d_map_metadata.csv` |
| IC2574 | `outputs/maps/phase6c/IC2574_frozen_pseudo2d_tau_map.npz` | `phase6c_IC2574_frozen_pseudo2d_map_metadata.csv` |
| NGC2403 | `outputs/maps/phase6c/NGC2403_frozen_pseudo2d_tau_map.npz` | `phase6c_NGC2403_frozen_pseudo2d_map_metadata.csv` |

Figures (optional): `outputs/figures/phase6c_<GALAXY>_frozen_pseudo2d_tau_map.png`
