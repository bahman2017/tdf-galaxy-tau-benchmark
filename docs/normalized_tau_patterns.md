# Normalized τ-Pattern Discovery (Phase 4C)

## Purpose

Exploratory **normalized pattern similarity** analysis across the controlled six-galaxy SPARC subset. Phase 4C asks whether Phase 2A reconstructed **dτ/dr** and missing-acceleration proxies share a **candidate τ-gradient family** among the five **robust_tdf_success** galaxies, while keeping **NGC7814** as an explicit **outlier / failure-mode** case.

This phase does **not** discover a universal τ-profile, does **not** rerun fits, and does **not** extend to full SPARC or lensing.

## Data source

- `outputs/tables/sparc_subset_tau_profiles.csv` — Phase 2A diagnostic radial reconstruction (`dtaudr_reconstructed`, `tau_reconstructed`, `residual_v2_kms2`).
- Galaxy classifications from Phase 4A (`MANDATED_GALAXY_CLASSIFICATION` in `failure_modes.py`).

## Normalization

| Quantity | Definition |
| --- | --- |
| x_span | (r − r_min) / (r_max − r_min) |
| x_grid | 100 points from 0 to 1 |
| dtaudr_norm | dτ/dr / max\|dτ/dr\| |
| gtau | residual_v² / r (km²/s² per kpc) |
| gtau_norm | gτ / max\|gτ\| |
| residual_v2_norm | residual_v² / max\|residual_v²\| |
| tau_norm | τ / max\|τ\| (if denominator > 0) |

Profiles are linearly interpolated onto x_grid without extrapolation beyond each galaxy’s radial coverage.

## Metrics

- Pairwise Pearson correlation and RMSE of **dtaudr_norm** and **gtau_norm** (`sparc_tau_pattern_similarity_matrix.csv`).
- **Success-group mean** profile ±1σ over five robust successes.
- **Outlier score** vs success-group mean: combines normalized RMSE and (1 − correlation) for dτ/dr and gτ (`pattern_outlier_score`).

## NGC7814

Always included. **Holdout failure mode** (Phase 4A) is separate from **normalized-profile outlier** status (Phase 4C metrics).

Per-metric RMSE ranks vs the success-group mean are reported honestly. NGC7814 may rank highest in `tau_norm` or `residual_v2_norm` but **not** be the largest outlier in `dtaudr_norm` / `gtau_norm` shape. The report states clearly when NGC7814 is **not** rank 1 for a metric.

Pattern metrics do **not** establish causation for holdout failure.

## How to run

```bash
python3 scripts/analyze_normalized_tau_patterns.py
```

## Outputs

| File | Role |
| --- | --- |
| `outputs/tables/sparc_normalized_tau_patterns.csv` | Long-form grid profiles |
| `outputs/tables/sparc_tau_pattern_similarity_matrix.csv` | Pairwise similarity |
| `outputs/tables/sparc_tau_pattern_outlier_scores.csv` | Outlier scores |
| `outputs/reports/sparc_normalized_tau_pattern_report.md` | Technical report |
| `outputs/figures/sparc_subset/normalized_tau_gradient_overlay.png` | dτ/dr_norm overlay |
| `outputs/figures/sparc_subset/normalized_missing_acceleration_overlay.png` | gτ_norm overlay |
| `outputs/figures/sparc_subset/tau_pattern_similarity_heatmap.png` | Correlation heatmap |

## Allowed language

- normalized pattern similarity
- candidate τ-gradient family
- success-group mean profile
- outlier behavior
- exploratory evidence for repeatable structure

## Prohibited language

- universal τ-profile
- proof of TDF
- dark matter disproven
- ΛCDM replaced
- lensing confirmed
