# Expansion-12 Benchmark Results (Phase 5B)

Phase 5B runs the same reproducible rotation-curve pipeline as the original six-galaxy benchmark on the **pre-registered expansion_12** cohort from Phase 5A.

## Cohort (12 galaxies)

**Original six:** DDO154, IC2574, NGC2403, NGC3198, NGC6503, NGC7814

**Phase 5A additions:** UGC02953, UGC05253, NGC5055, UGC00128, NGC0289, DDO161

## Command

```bash
python3 scripts/run_expansion12_pipeline.py
```

## Pipeline steps

1. Radial τ reconstruction (Phase 2A logic)
2. NFW/Burkert log refit + baryonic-only
3. MOND/RAR baselines
4. TDF 3/4/5-knot in-sample fits
5. Even/odd train-only holdout validation
6. Failure-mode classification and claim traceability

## Model hierarchy

- **Primary:** `tdf_3knot`
- **Sensitivity:** `tdf_5knot` (and `tdf_4knot` in tables for diagnostics)
- Report holdout wins using **tdf_3knot** unless explicitly discussing sensitivity.

## Outputs

| File | Description |
| --- | --- |
| `outputs/tables/expansion12_model_comparison.csv` | In-sample metrics all models |
| `outputs/tables/expansion12_holdout_validation.csv` | Holdout test RMSE |
| `outputs/tables/expansion12_failure_mode_summary.csv` | Per-galaxy classification |
| `outputs/tables/expansion12_claim_traceability.csv` | Allowed/prohibited claims |
| `outputs/reports/expansion12_benchmark_report.md` | Summary report |

## Claim boundaries

- Controlled **expansion_12** only — not full SPARC
- Does not disprove dark matter
- Does not replace ΛCDM
- Lensing not tested
- No final M/L calibration in this phase
