# Expansion-12 Failure-Mode Analysis (Phase 5B-Audit)

Phase 5B-Audit diagnoses the four expansion_12 **failure** and **mixed** cases before any expansion_20 run. It uses existing Phase 5B tables only — **no new model fitting**.

## Focus galaxies

| Galaxy | Phase 5B class | TDF failure scope (holdout) |
| --- | --- | --- |
| NGC7814 | `tdf_failure_mode` | all-TDF failure |
| NGC5055 | `tdf_failure_mode` | primary failure; tdf_5knot flex-recovery |
| UGC00128 | `mixed_result` | near-tie / baseline-dominated |
| UGC05253 | `mixed_result` | flex-recovery; unstable |

## Command

```bash
python3 scripts/analyze_expansion12_failure_modes.py
```

## Key distinction: NGC5055 ≠ NGC7814

- **NGC7814:** tdf_3knot and tdf_5knot both fail vs NFW/MOND on even/odd holdout.
- **NGC5055:** tdf_3knot fails badly; tdf_5knot holdout is competitive and beats NFW/MOND — knot-count / flexibility sensitivity, not canonical all-TDF failure.

## Outputs

| File | Role |
| --- | --- |
| `outputs/tables/expansion12_failure_diagnostics.csv` | Full per-galaxy diagnostic fields |
| `outputs/tables/expansion12_case_review_summary.csv` | Compact review table |
| `outputs/reports/expansion12_failure_mode_analysis_report.md` | Narrative report |
| `outputs/figures/sparc_subset/expansion12_failure_case_residuals.png` | residual_v² panels |
| `outputs/figures/sparc_subset/expansion12_tdf3_vs_tdf5_gap.png` | Holdout RMSE comparison |

## Claim boundaries

This audit diagnoses expansion_12 failure and mixed cases only. It does not add new fits, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.
