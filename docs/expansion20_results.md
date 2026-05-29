# Expansion-20 Benchmark Results (Phase 5C)

Phase 5C runs the controlled benchmark on the pre-registered **expansion_20** cohort from Phase 5A, with classification guardrails from Phase 5B-Audit and Phase 5B-R.

## Cohort (20 galaxies)

**Original six:** DDO154, IC2574, NGC2403, NGC3198, NGC6503, NGC7814

**Phase 5A additions:** UGC02953, UGC05253, UGC09133, UGC06787, NGC5055, UGC00128, NGC0289, UGC12506, UGC11455, NGC6015, DDO161, NGC7793, UGC07524, UGC08490

## Command

```bash
python3 scripts/run_expansion20_pipeline.py
```

## Classification (Phase 5C)

| Label | Definition |
| --- | --- |
| `robust_tdf_success` | Primary **tdf_3knot** beats NFW **and** MOND on even/odd holdout |
| `sensitivity_recovery` | **tdf_3knot** fails; **tdf_5knot** recovers vs baselines — not primary success |
| `tdf_failure_mode` | Both TDF variants fail vs baselines |
| `mixed_result` | Near-tie or unstable |

### Frozen guardrails

- **NGC7814:** canonical all-TDF failure
- **NGC5055, UGC05253:** sensitivity_recovery (Phase 5B-R)
- **UGC00128:** mixed unless tdf_3knot beats both baselines

## Reporting

- Primary success count uses **tdf_3knot** only (`robust_tdf_success`)
- **tdf_5knot** is sensitivity/high-flexibility only
- Do not count sensitivity_recovery as primary success

## Claim boundaries

- Controlled expansion_20 only — not full SPARC
- Does not disprove dark matter or replace ΛCDM
- Lensing not tested
- No universal τ-profile claim

## Outputs

| File | Description |
| --- | --- |
| `outputs/tables/expansion20_model_comparison.csv` | In-sample metrics |
| `outputs/tables/expansion20_holdout_validation.csv` | Holdout validation |
| `outputs/tables/expansion20_failure_mode_summary.csv` | Per-galaxy classification |
| `outputs/tables/expansion20_claim_traceability.csv` | Allowed/prohibited claims |
| `outputs/reports/expansion20_benchmark_report.md` | Summary report |
