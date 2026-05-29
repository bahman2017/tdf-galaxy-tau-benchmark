# Controlled Six-Galaxy Results Summary (Post-M/L, Phase 4H)

> Diagnostic M/L sensitivity (4F/4G) updates interpretation only. Canonical holdout results at fixed SPARC baryons are unchanged.

## Headline

On a **controlled six-galaxy subset**, TDF achieves **5 of 6 holdout success** under **fixed canonical SPARC baryons** and even/odd holdout. **NGC7814** remains an explicit **canonical failure** that is **baryonic-decomposition-sensitive** under diagnostic M/L scaling.

## Canonical holdout (M/L = 1)

| Galaxy | Classification | Best holdout | tdf_3knot | NFW |
| --- | --- | --- | ---: | ---: |
| DDO154 | robust_tdf_success | tdf_5knot | 2.03 | 3.56 |
| IC2574 | robust_tdf_success | tdf_5knot | 2.98 | 6.39 |
| NGC2403 | robust_tdf_success | tdf_5knot | 8.66 | 9.76 |
| NGC3198 | robust_tdf_success | tdf_5knot | 10.45 | 12.0 |
| NGC6503 | robust_tdf_success | tdf_5knot | 9.33 | 10.14 |
| NGC7814 | tdf_failure_mode | nfw_refit | 155.8 | 24.89 |

## Post-M/L diagnostic interpretation

**NGC7814:** Canonical holdout failure retained under fixed SPARC baryons. Baryonic-decomposition-sensitive failure: lowering bulge_scale reduces inner TDF error. Under fair scaled comparison, NFW and MOND also improve; TDF can be competitive at some plausible lower-bulge settings (especially tdf_5knot), but this is not a final M/L calibration. NFW or MOND wins at some plausible-scale cells.

**Five success galaxies:** TDF holdout success is **stable** under plausible diagnostic M/L scaling (Phase 4G); no galaxy flips to NFW/MOND as best model across all plausible cells.

## Model recommendation

- **Primary:** `tdf_3knot` (conservative).
- **Sensitivity:** `tdf_5knot` (higher flexibility; often best scaled RMSE).

## Claim boundary

See `outputs/tables/sparc_claim_traceability_matrix_updated.csv` and `docs/paper_ready_claims.md`.
