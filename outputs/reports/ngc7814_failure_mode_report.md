# NGC7814 Failure-Mode Diagnostic Report (Phase 4D)

> This diagnostic deep-dive investigates why NGC7814 is a TDF holdout failure mode in the six-galaxy controlled subset. It does not remove the failure case, does not refit the physical models, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Executive summary

- **NGC7814** is the only **holdout failure mode** in the six-galaxy subset (even/odd test RMSE: TDF ≫ NFW/MOND).
- **Normalized-profile metrics (Phase 4C):** rank-1 RMSE vs success-group mean in dτ/dr, gτ, τ, and residual_v²; combined **shape score rank 2/6** (below **NGC3198**).
- **Baryonic structure:** bulge-dominated inner regions (median v_bulge/v_bar ≈ 0.80 vs success medians ≪ 1).
- **Residual structure:** 5/18 negative residual_v² points; max |residual_v²| at r ≈ 0.63 kpc (inner).
- **tdf_4knot** shows negative-v² pathology with extreme inner knot amplitude; per-point holdout curves are **not** archived.

## Why NGC7814 matters

It is the single predictive failure in an otherwise promising six-galaxy benchmark. Removing it would overstate subset performance; retaining it enforces honest reporting.

## Holdout failure vs normalized-profile outlier

| Concept | NGC7814 | NGC3198 (counterexample) |
| --- | --- | --- |
| Holdout failure mode | True | False |
| Normalized-profile outlier | True | False |
| Shape score (dτ/dr+gτ) | 0.734 (rank 2/6) | 0.815 (rank 1/6) |
| dτ/dr RMSE rank vs success mean | 1 | 2 |
| τ_corr to success mean | 0.129 | 0.995 |

**NGC3198** has the highest shape-score deviation but **passes holdout** — holdout failure cannot be reduced to “largest shape outlier.”

## Baryonic-structure diagnostics

| Galaxy | median v_bulge/v_bar | max v_bulge/v_bar | central conc. proxy |
| --- | ---: | ---: | ---: |
| NGC7814 | 0.803 | 0.993 | 0.895 |
| DDO154 | 0.000 | 0.000 | 0.788 |
| IC2574 | 0.000 | 0.000 | 0.326 |
| NGC2403 | 0.000 | 0.000 | 0.329 |
| NGC3198 | 0.000 | 0.000 | 0.504 |
| NGC6503 | 0.000 | 0.000 | 0.786 |

NGC7814 exceeds success-group median bulge fraction: **True**. Stronger central concentration than all success cases: **True**.

## Residual and τ-gradient diagnostics

- Negative residual_v² fraction: **0.28** (success max **0.38**).
- Sign changes in residual_v²: **1** (success max **6**).
- Max |residual_v²| at r = **0.63** kpc; max |dτ/dr| at r = **0.63** kpc.
- Largest features at inner radii (r < 2 kpc): **True**.

## Holdout failure diagnostics

Per-point holdout velocity residuals are **not stored** in Phase 3C outputs. Table-level even/odd test RMSE for NGC7814: tdf_3knot ≈ 155.8 km/s; nfw_refit ≈ 24.9 km/s; mond ≈ 27.8 km/s.

See `ngc7814_holdout_residuals.png` (bar chart). Split-dependent RMSE varies strongly — holdout failure is not uniform across all split schemes.

## Normalized-pattern diagnostics (Phase 4C)

- NGC7814 is rank **1** by RMSE vs success-group mean for dτ/dr, gτ, τ, and residual_v² on this run.
- Integrated τ shape (τ_corr ≈ 0.13) diverges strongly from the success family (≳ 0.97).
- Combined shape score is **not** rank 1; **NGC3198** is higher.

## Candidate explanations (hypotheses only)

- *Bulge-dominated fixed decomposition* — may be associated with this factor (supported by subset metrics).
- *Inner negative residual_v² and sign structure* — is consistent with this factor (weak / mixed support in this pass).
- *Fixed knot placement missing bulge-to-disk transition* — suggests a possible role for this factor (supported by subset metrics).
- *Holdout driven by predictive error rather than normalized shape alone* — cannot yet distinguish between this factor (supported by subset metrics).

## What is supported vs not supported

**Supported:** NGC7814 is a holdout failure; bulge-heavy; inner residual pathology; rank-1 normalized RMSE outlier vs success mean; tdf_4knot negative-v² flag.

**Not supported:** Bulge dominance as the sole definitive cause; general TDF failure; dark-matter proof/disproof; full-SPARC validation; lensing tests.

## Outputs

- `outputs/tables/ngc7814_failure_diagnostics.csv`
- `outputs/tables/ngc7814_vs_success_group_diagnostics.csv`
- Figures under `outputs/figures/sparc_subset/ngc7814_*.png`
