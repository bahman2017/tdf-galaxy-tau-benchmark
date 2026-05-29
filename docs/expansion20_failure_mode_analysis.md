# Expansion-20 Failure-Mode Analysis (Phase 5D)

Phase 5D audits the five **non-robust** galaxies from the expansion_20 benchmark (Phase 5C): one all-TDF failure, three sensitivity-recovery cases, and one mixed near-tie.

## Non-robust cases

| Galaxy | Phase 5C class | failure_scope |
| --- | --- | --- |
| NGC7814 | tdf_failure_mode | all_tdf_failure |
| NGC5055 | sensitivity_recovery | sensitivity_recovery |
| UGC05253 | sensitivity_recovery | sensitivity_recovery |
| UGC12506 | sensitivity_recovery | sensitivity_recovery |
| UGC00128 | mixed_result | mixed_result |

## Command

```bash
python3 scripts/analyze_expansion20_failure_modes.py
```

## UGC12506 (new)

Phase 5D assigns an **archetype** by comparing holdout metrics and baryonic context to NGC7814, NGC5055, UGC05253, and UGC00128. See the report for the full rationale.

## Disclaimer

This audit diagnoses expansion_20 failure, mixed, and sensitivity-recovery cases only. It does not add new fits, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Outputs

- `outputs/tables/expansion20_failure_diagnostics.csv`
- `outputs/tables/expansion20_case_review_summary.csv`
- `outputs/reports/expansion20_failure_mode_analysis_report.md`
- `outputs/figures/sparc_subset/expansion20_failure_case_residuals.png`
- `outputs/figures/sparc_subset/expansion20_tdf3_vs_tdf5_gap.png`
