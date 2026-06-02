# Fair M/L-Scaled Baseline Comparison (Phase 4G)

## Purpose

Phase 4F showed that NGC7814 TDF holdout failure is highly sensitive to diagnostic disk/bulge M/L scaling, but NFW and MOND were compared only at **canonical** (unscaled) baryons. Phase 4G refits **TDF**, **NFW**, and **MOND** on the **same** scaled `v_bar` at each grid point.

This remains a **diagnostic sensitivity audit**, not a final baryonic calibration.

## Scaling

Same as Phase 4F:

`v_bar² = v_gas² + s_disk·v_disk² + s_bulge·v_bulge²`

Gas is not scaled. Component velocities keep SPARC sign convention.

## Grid

- `disk_scale`: 0.5, 0.7, 1.0, 1.3
- `bulge_scale`: 0.2, 0.5, 0.7, 1.0, 1.3
- Plausible band: disk ∈ [0.7, 1.3], bulge ∈ [0.5, 1.0]

## Protocol

- Six subset galaxies (including NGC7814)
- `even_odd_index` train-only holdout
- Models: `tdf_3knot`, `tdf_5knot`, `nfw_refit_scaled`, `mond_fit_a0_scaled`
- NFW: Phase 3A-R log multistart on train points
- MOND: log10(a0) refit on train points
- TDF: Phase 4F train-only knot refit; legacy **K_tau** (\(K_g\)) fixed

## Run

```bash
python3 scripts/run_sparc_ml_scaled_baseline_comparison.py
```

## Outputs

| File | Description |
|------|-------------|
| `outputs/tables/sparc_ml_scaled_model_comparison.csv` | Per galaxy × scale × model metrics |
| `outputs/tables/ngc7814_ml_scaled_fair_comparison.csv` | NGC7814 side-by-side RMSE |
| `outputs/tables/sparc_ml_scaled_best_model_summary.csv` | Best plausible-scale winner per galaxy |
| `outputs/reports/sparc_ml_scaled_baseline_comparison_report.md` | Narrative report |
| `outputs/figures/sparc_subset/ngc7814_ml_scaled_fair_comparison.png` | RMSE heatmaps |
| `outputs/figures/sparc_subset/ml_scaled_model_winners_heatmap.png` | Best model per cell |
| `outputs/figures/sparc_subset/ml_scaled_success_stability.png` | Success vs failure flags |

## Claim boundary

Does **not** recalibrate SPARC, validate full SPARC, disprove dark matter, or include lensing. Canonical Phase 4A labels at M/L=1 are unchanged.

**Phase 4H:** Post-M/L claim language and `sparc_post_ml_results_summary_table.csv` integrate 4F+4G without new fits. Claim L (TDF uniquely benefits) is **not supported**; claim M (five success galaxies stable) is **supported with caveat**.
