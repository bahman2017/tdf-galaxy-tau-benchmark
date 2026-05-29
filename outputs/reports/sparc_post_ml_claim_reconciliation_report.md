# SPARC Post-M/L Claim Reconciliation Report (Phase 4H)

> This reconciliation updates claim language after diagnostic M/L sensitivity tests. It does not introduce a final M/L calibration, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Objective

Reconcile publication-ready claims and controlled-subset narrative after Phase 4F (TDF M/L sensitivity) and Phase 4G (fair scaled TDF/NFW/MOND comparison) **without new fits**.

## What Phase 4F showed

- NGC7814 canonical TDF holdout failure (~156 km/s tdf_3knot at M/L=1) is **strongly sensitive** to diagnostic disk/bulge scaling.
- Lowering `bulge_scale` reduces inner negative residuals and TDF holdout RMSE dramatically.
- Phase 4F compared TDF at scaled baryons to **canonical** (unscaled) NFW/MOND only.

## What Phase 4G changed

- NFW and MOND were refit on the **same** scaled baryons as TDF at each grid point.
- At canonical (1,1), scaled NFW/MOND still dominate NGC7814 (~25–28 vs ~156 km/s).
- At plausible lower-bulge settings, **all** models improve; MOND/NFW often remain competitive with TDF.
- Five success galaxies remain stable under plausible diagnostic scaling.

## Updated interpretation of NGC7814

- **Canonical:** Canonical holdout failure retained under fixed SPARC baryons. Baryonic-decomposition-sensitive failure: lowering bulge_scale reduces inner TDF error. Under fair scaled comparison, NFW and MOND also improve; TDF can be competitive at some plausible lower-bulge settings (especially tdf_5knot), but this is not a final M/L calibration. NFW or MOND wins at some plausible-scale cells.
- Holdout RMSE at M/L=1: tdf_3knot=155.8, nfw=24.89, mond=27.85 km/s.
- Best plausible scaled model (Phase 4G): tdf_5knot (disk=1.3, bulge=0.7).
- NGC7814 is **not removed** from the benchmark.

## Updated interpretation of the five success galaxies

- **5 of 5** retain canonical holdout-success interpretation with `tdf_success_stable_under_plausible_scaling=True` in Phase 4G.
- Primary conservative model remains **tdf_3knot**; **tdf_5knot** often best at scaled scales.

## Updated supported claims (I–N)

- **I:** NGC7814 is a canonical TDF holdout failure under fixed SPARC baryons. — `supported`
- **J:** NGC7814 failure is sensitive to bulge/disk M/L scaling. — `supported_diagnostic_sensitivity`
- **K:** M/L scaling definitively fixes NGC7814. — `not_supported`
- **L:** TDF uniquely benefits from M/L scaling. — `not_supported`
- **M:** TDF remains stable across the five original success galaxies under plausible M/L scaling. — `supported_with_caveat`
- **N:** The current benchmark has a photometry-calibrated M/L model. — `not_supported_future_work`

## Allowed language (post-M/L)

- canonical failure
- baryonic-decomposition-sensitive failure
- diagnostic M/L scaling
- fair scaled comparison
- TDF remains stable in the five success galaxies
- NGC7814 is recoverable under some plausible lower-bulge settings, but the result is not a final M/L calibration

## Prohibited language (post-M/L)

- "NGC7814 is solved"
- "TDF is validated"
- "dark matter is disproven"
- "ΛCDM is replaced"
- "M/L calibration confirms TDF"
- "NFW/MOND fail after scaling"
- "lensing is confirmed"

## Next recommended work

1. Photometry-informed M/L priors (not Cartesian grid).
2. K_tau sensitivity with fair scaled baselines.
3. Full SPARC and lensing only after frozen τ-map validation and updated claim matrix.

## Outputs

- `outputs/tables/sparc_claim_traceability_matrix_updated.csv`
- `outputs/tables/sparc_post_ml_results_summary_table.csv`
- `docs/paper_ready_claims.md`, `docs/results_summary.md`
