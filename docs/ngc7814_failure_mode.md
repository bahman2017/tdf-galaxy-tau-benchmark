# NGC7814 Failure Mode (Phase 4D)

## Role in the benchmark

NGC7814 is the **only canonical holdout failure mode** among the six-galaxy controlled SPARC subset. It is **retained** in all summaries and reports (Phase 4H). Diagnostic M/L tests (4F–4G) **do not remove** this label at fixed canonical SPARC baryons.

## Reconciled interpretation (Phase 4H)

| Layer | Statement |
| --- | --- |
| **Canonical** | Under fixed SPARC baryons (M/L=1), NGC7814 remains a **TDF holdout failure** (tdf_3knot ≈ 156 km/s vs NFW ≈ 25 km/s). |
| **Sensitivity** | Failure is **baryonic-decomposition-sensitive**: lowering `bulge_scale` reduces inner TDF error and holdout RMSE dramatically. |
| **Fair comparison** | When NFW/MOND are refit on the **same** scaled baryons, they **also** improve; TDF improvement is **not unique**. |
| **Plausible band** | At some lower-bulge plausible settings, TDF (often **tdf_5knot**) can be competitive or best — **diagnostic only**, not final M/L calibration. |
| **Primary model** | Report **tdf_3knot** as conservative; **tdf_5knot** as high-flexibility sensitivity. |

**Do not say:** NGC7814 is solved; M/L calibration confirms TDF; NFW/MOND fail after scaling.

## Two distinct labels

| Label | Meaning |
| --- | --- |
| **Holdout failure mode** | Phase 4A/3C: poor even/odd **predictive** test RMSE vs NFW/MOND. |
| **Normalized-profile outlier** | Phase 4C: large RMSE vs success-group mean in normalized profiles (metric-driven). |

These are **not the same**. **NGC3198** has the **highest combined shape score** but **passes holdout**.

## Key structural findings (this repository pass)

- **Bulge-dominated** fixed SPARC decomposition (high v_bulge/v_bar at inner radii).
- **Inner negative residual_v²** in Phase 2A diagnostic reconstruction (v_obs < v_bar).
- Max |residual_v²| and extreme |dτ/dr| at **inner radii** (r ≲ 2 kpc).
- **tdf_4knot** negative-v² pathology with catastrophic inner knot amplitude.
- Normalized **τ** profile poorly correlated with success-group mean (τ_corr ≈ 0.13).

## What we do not claim

- Definitive proof that bulge dominance causes holdout failure.
- General invalidation of TDF.
- Dark-matter proof or disproof.
- Full-SPARC or lensing conclusions.

## M/L sensitivity (Phase 4F)

At **canonical** SPARC decomposition (disk_scale=bulge_scale=1.0), holdout failure persists (~156 km/s tdf_3knot).

Diagnostic scaling shows **strong sensitivity**: lowering bulge_scale (and moderately disk_scale) reduces inner negative residuals and can bring TDF holdout RMSE to **~3–7 km/s** (e.g. disk=0.7, bulge=0.5), competitive with canonical NFW (~25 km/s) on the same scaled baryons — but NFW/MOND were **not** re-scaled in Phase 4F.

**Conclusion:** The failure is **partially explained** by fixed bulge-dominated baryons at M/L=1; it is **not** removed at canonical scaling. This is diagnostic only, not a final M/L calibration.

## Diagnostic prior weighting (Phase 4I)

Placeholder priors over Phase 4G cells (`configs/ml_priors.yaml`) — **not** photometric calibration. **Canonical failure at M/L=1 unchanged.** Phase **4I-Audit** clarified labels: **`sensitivity_tdf_5knot_diagnostic_recovery`** when tdf_5knot carries prior-weight wins but **tdf_3knot** does not (0% in plausible band). **conservative_bulge_downweight_test** increases weight on low-bulge cells (as intended) and is **consistent** with uniform, not opposite. See `outputs/reports/ml_prior_weighting_audit_report.md`.


## Photometry context (Phase 4J)

SPARC Table-1 metadata ingestion adds context for future priors:

- NGC7814: Type~2 (early-type disk), high 3.6um luminosity, high central disk SB, bulge proxy true.
- Five robust-success galaxies are mostly later-type and less centrally concentrated in this metadata view.

This supports treating NGC7814 as structurally distinct for **future prior construction**, but does **not** change the canonical `tdf_3knot` holdout failure label at M/L=1.

## Photometry-informed priors (Phase 4K)

Diagnostic photometry-informed scenarios (`outputs/tables/ngc7814_photometry_prior_interpretation.csv`, `outputs/reports/sparc_photometry_informed_prior_report.md`):

- **canonical_anchor_prior:** canonical `tdf_3knot` failure at M/L=1 **unchanged**.
- **morphology_aware_conservative:** does not auto-favor extreme low `bulge_scale` for early-type/bulge-proxy systems; may still show **tdf_5knot** weighted support under diagnostic priors.
- **ngc7814_bulge_sensitivity_diagnostic:** NGC7814-only test of lower-bulge cells — **not** calibrated bulge M/L; any improved weighted RMSE for **tdf_5knot** is sensitivity-only, not primary conservative recovery.

Do **not** use Phase 4K outputs to claim final M/L calibration (claim Q: not supported).

## Fair scaled baseline comparison (Phase 4G)

When **NFW** and **MOND** are refit on the **same** scaled baryons as TDF:

- At **canonical** (1,1): scaled NFW/MOND remain far better than TDF on holdout RMSE (~25–28 vs ~156 km/s).
- Lowering `bulge_scale` improves **all** models, not only TDF.
- In the **plausible** M/L band, TDF can beat scaled NFW at some cells but NFW/MOND often remain competitive or win.
- See `outputs/reports/sparc_ml_scaled_baseline_comparison_report.md` and `docs/ml_scaled_baseline_comparison.md`.

## Radial holdout localization (Phase 4E)

On **even/odd** holdout with train-only refits:

- **tdf_3knot** inner-region RMSE ≈ **236 km/s** (worst region); max |residual| at r ≈ **1.7 kpc**.
- **nfw_refit** inner-region RMSE ≈ **43 km/s** — substantially smoother.
- **3** inner holdout points with TDF negative-v² flags.
- See `outputs/figures/sparc_subset/ngc7814_radial_holdout_residual_map.png` and `sparc_holdout_point_residuals.csv`.

## How to run diagnostics

```bash
python3 scripts/analyze_ngc7814_failure_mode.py
python3 scripts/export_sparc_holdout_residuals.py
python3 scripts/analyze_radial_holdout_failure_maps.py
```

## Outputs

- `outputs/tables/ngc7814_failure_diagnostics.csv`
- `outputs/tables/ngc7814_vs_success_group_diagnostics.csv`
- `outputs/reports/ngc7814_failure_mode_report.md`
- `outputs/figures/sparc_subset/ngc7814_*.png`
