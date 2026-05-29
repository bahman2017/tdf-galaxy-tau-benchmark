# SPARC Normalized τ-Pattern Report (Phase 4C)

**Exploratory normalized pattern analysis** on the controlled six-galaxy subset. No new fits were run. Phase 2A diagnostic τ profiles only.

> This analysis searches for normalized τ-pattern similarities. It does not assume or discover a universal τ-profile, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Objective

Test whether galaxy-specific reconstructed profiles show **normalized pattern similarity** across the five **robust_tdf_success** galaxies. **NGC7814** is the known **holdout failure mode** (Phase 4A); normalized-profile metrics are computed **without forcing** it to be an outlier in every quantity.

## Holdout failure vs normalized-profile outlier

| Concept | Definition |
| --- | --- |
| **Holdout failure mode** | Phase 4A `tdf_failure_mode`: poor even/odd test RMSE vs NFW/MOND (predictive). |
| **Normalized-profile outlier** | Largest RMSE vs success-group mean and/or elevated shape score in Phase 4C metrics only. |

These are **not equivalent**. A galaxy can fail holdout while ranking mid-pack in normalized shape metrics.

## Normalization choices

- Radial coordinate: **x_span** = (r − r_min) / (r_max − r_min) mapped to a common grid x_grid ∈ [0, 1] with 100 points (linear interpolation, no extrapolation).
- **dtaudr_norm** = dτ/dr / max|dτ/dr|; **gtau** = residual_v²/r; **gtau_norm** = gτ / max|gτ|.
- **residual_v2_norm**, **tau_norm**: same max-abs scaling.
- Source: `sparc_subset_tau_profiles.csv` (Phase 2A, `phase_2a_radial_reconstruction`).

## Success-group profile behavior

- Success-group galaxies: DDO154, IC2574, NGC2403, NGC3198, NGC6503.
- Median pairwise **dtaudr_corr** (success only): **0.619**.
- Median pairwise **gtau_corr** (success only): **0.619**.
- Overlay figures show a **success-group mean profile** with ±1σ envelope.
- Language: **candidate τ-gradient family** and **exploratory evidence for repeatable structure** where correlations are high; not proof of a universal law.

## Per-metric largest outlier (honest ranks)

- **dtaudr_norm (shape)**: largest outlier = **NGC7814** (RMSE rank 1). NGC7814 **is** the largest outlier for this metric.
- **gtau_norm (shape)**: largest outlier = **NGC7814** (RMSE rank 1). NGC7814 **is** the largest outlier for this metric.
- **tau_norm (integrated τ)**: largest outlier = **NGC7814** (RMSE rank 1). NGC7814 **is** the largest outlier for this metric.
- **residual_v2_norm (amplitude)**: largest outlier = **NGC7814** (RMSE rank 1). NGC7814 **is** the largest outlier for this metric.

## NGC7814 discussion

- **Holdout failure mode:** True (Phase 4A; NFW/MOND beat TDF on test RMSE).
- **Normalized-profile outlier (metric-driven flag):** True.
- Shape score (dτ/dr + gτ only): 0.734 — rank **2/6** (1 = highest; **NGC3198** is higher at 0.815).
- RMSE ranks vs success-group mean — dτ/dr: 1; gτ: 1; τ: 1; residual_v²: 1.
- τ_corr to success mean: 0.129 (much lower than success galaxies ≳ 0.97 — integrated-τ **shape** differs strongly).

**NGC7814 is rank 1 by RMSE vs success-group mean in all four normalized metrics on this run.** That supports strong **normalized-profile outlier behavior**, separate from the holdout label.
 However, the combined **shape score** ranks NGC7814 **2**/6 — so holdout failure is **not** the same as the highest shape-score deviation among the six galaxies.

Holdout failure is **not** claimed to be *caused* by normalized-profile distance; metrics are exploratory.

## Similarity matrix summary

Full pairwise table: `outputs/tables/sparc_tau_pattern_similarity_matrix.csv`.
Heatmap: `outputs/figures/sparc_subset/tau_pattern_similarity_heatmap.png`.

## Outlier-score summary

| galaxy_id | holdout_failure | norm_profile_outlier | shape_score | dτ/dr rank | τ rank | res_v² rank |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| NGC3198 | False | False | 0.815 | 2 | 6 | 4 |
| NGC7814 | True | True | 0.734 | 1 | 1 | 1 |
| NGC6503 | False | False | 0.590 | 3 | 2 | 3 |
| DDO154 | False | False | 0.537 | 4 | 3 | 5 |
| NGC2403 | False | False | 0.427 | 5 | 5 | 6 |
| IC2574 | False | False | 0.402 | 6 | 4 | 2 |

## Candidate shared normalized pattern?

**Moderate exploratory similarity** among success-group galaxies is visible in normalized dτ/dr and gτ overlays; treat as a **candidate τ-gradient family**, not a universal profile.

## Limitations

- Phase 2A diagnostic reconstruction only (not Phase 3B knot fits).
- Six galaxies; morphology and baryonic decomposition differ.
- Max-abs normalization removes amplitude scale; shape-only comparison.
- No M/L, K_tau, distance, or inclination sensitivity in this phase.

## Outputs

- `outputs/tables/sparc_normalized_tau_patterns.csv`
- `outputs/tables/sparc_tau_pattern_similarity_matrix.csv`
- `outputs/tables/sparc_tau_pattern_outlier_scores.csv`
- Figures under `outputs/figures/sparc_subset/`
