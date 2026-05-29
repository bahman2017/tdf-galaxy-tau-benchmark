# Diagnostic M/L Prior Framework (Phase 4I)

## Purpose

Phase 4F/4G used a **Cartesian diagnostic M/L grid**, not photometric calibration. Phase 4I adds a **prior-weighting scaffold** on existing Phase 4G holdout RMSE tables to explore how **placeholder priors** would summarize model support — without new fits.

## What this is not

- Not a final astrophysical or photometric M/L model
- Not TDF validation on full SPARC
- Not a change to canonical NGC7814 failure at M/L=1

## Prior scenarios (`configs/ml_priors.yaml`)

| Scenario | Scope | Weighting |
| --- | --- | --- |
| `uniform_plausible_band` | Plausible band only | Uniform |
| `conservative_bulge_downweight_test` | Plausible band | Higher weight at lower `bulge_scale` |
| `canonical_delta_prior` | Full 4G grid | Gaussian centered at disk=bulge=1 |

## Metrics (per galaxy, model, scenario)

- `prior_weighted_mean_rmse`, `prior_weighted_median_rmse`
- `best_plausible_rmse`
- `fraction_of_prior_weight_where_model_wins`
- `fraction_of_prior_weight_where_tdf_beats_nfw` / `_mond` (tdf_3knot)

## NGC7814 interpretation categories (Phase 4I-Audit v2)

- `canonical_failure_primary_tdf_3knot` / `canonical_failure_only`
- `sensitivity_tdf_5knot_diagnostic_recovery` — **tdf_5knot** win fraction elevated; not primary conservative claim
- `primary_tdf_3knot_diagnostic_recovery`
- `baryon_sensitive_competitive`
- `prior_supported_baseline_preference`
- `inconclusive`

Explicit fields: `canonical_result`, `primary_tdf_3knot_prior_result`, `sensitivity_tdf_5knot_prior_result`, `either_tdf_variant_prior_result`, `recommended_claim_language`.

**Uniform vs conservative:** both up-weight low-bulge plausible cells; conservative increases tdf_5knot win fraction further. Neither implies calibrated recovery for **tdf_3knot** (0% wins in plausible band).

See `outputs/reports/ml_prior_weighting_audit_report.md`.

## Run

```bash
python3 scripts/apply_ml_prior_weighting.py
```

## Claim O

**Photometry-informed prior framework is required before treating M/L-scaled results as calibrated.** Status: **supported**.

## Outputs

- `outputs/tables/sparc_ml_prior_weighted_summary.csv`
- `outputs/tables/ngc7814_ml_prior_weighted_interpretation.csv`
- `outputs/reports/sparc_ml_prior_framework_report.md`


## Phase 4J next-step prior construction

Phase 4J ingests SPARC Table-1 photometry metadata (`distance`, `inclination`, `L3.6`, `Rdisk`, `SBdisk`, `Type`) into `data/processed/sparc/sparc_photometry_metadata.csv`. This enables future photometry-informed priors but **does not** calibrate final M/L priors yet.

Use `outputs/tables/sparc_subset_photometry_context.csv` and `outputs/reports/sparc_photometry_metadata_ingestion_report.md` before modifying scenario weights.

## Phase 4K photometry-informed scenarios

Implemented in `photometry_informed_scenarios` (`configs/ml_priors.yaml`):

| Name | Weighting | Scope |
| --- | --- | --- |
| `photometry_uniform_plausible` | uniform | plausible band |
| `morphology_aware_conservative` | morphology_aware | plausible band |
| `ngc7814_bulge_sensitivity_diagnostic` | ngc7814_bulge_diagnostic | NGC7814 only |
| `canonical_anchor_prior` | gaussian_anchor | full grid |

Scripts: `build_photometry_informed_ml_priors.py`, `apply_photometry_informed_prior_weighting.py`. See `docs/photometry_informed_ml_priors.md`. Phase 4I placeholder scenarios remain in `scenarios:` for backward comparison.
