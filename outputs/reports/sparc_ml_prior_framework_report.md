# SPARC Diagnostic M/L Prior Framework Report (Phase 4I)

> **No final photometric M/L calibration is performed.** Priors are **diagnostic placeholders** over existing Phase 4G grid results. This scaffold guides which photometric metadata to ingest next.

> NGC7814 remains a **canonical TDF holdout failure** at disk=bulge=1. Any “recovery” under priors is **conditional and diagnostic**, not validation.

## Objective

Provide a conservative **prior-weighting scaffold** on Phase 4G fair scaled comparisons without new fits.

## Prior scenarios (diagnostic only)

- **uniform_plausible_band:** Uniform diagnostic weight over plausible-band Phase 4G grid cells only. (`uniform`, scope=plausible_only)
- **conservative_bulge_downweight_test:** Diagnostic test — higher prior weight at lower bulge_scale within plausible band. (`bulge_downweight`, scope=plausible_only)
- **canonical_delta_prior:** Diagnostic delta-like weight centered at disk=1, bulge=1 on full Phase 4G grid. (`gaussian_delta`, scope=all_grid)

## Plausible band (from config)

- disk_scale ∈ [0.7, 1.3]
- bulge_scale ∈ [0.5, 1.0]

## NGC7814 prior-weighted interpretation

- Category (**uniform_plausible_band**): `sensitivity_tdf_5knot_diagnostic_recovery`
- Canonical tdf_3knot / NFW: 155.8 / 24.9 km/s
- Primary tdf_3knot win fraction: 0.00; sensitivity tdf_5knot: 0.67
- Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration.

## Five success galaxies

- Under **uniform_plausible_band**, tdf_3knot holds ≥30% prior-weight win fraction in **0/5** galaxies.
- Success cases remain broadly TDF-favorable under diagnostic priors; see summary table.

## Claim O (Phase 4I)

**Photometry-informed prior framework is required before treating M/L-scaled results as calibrated.** Status: **supported**.

## Limitations

- No SPARC photometry ingested; weights are scenario placeholders.
- No new model fits; Phase 4G CSV is the sole numeric source.
- Full SPARC and lensing remain future work.

## Outputs

- `outputs/tables/sparc_ml_prior_weighted_summary.csv`
- `outputs/tables/ngc7814_ml_prior_weighted_interpretation.csv`
- `configs/ml_priors.yaml`
- `docs/ml_prior_framework.md`
