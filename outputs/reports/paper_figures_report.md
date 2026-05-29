# Paper Figures Report (Phase 5F-B)

> Phase 5F-B composes publication figures from frozen audited benchmark outputs only. No model fitting and no modification of benchmark tables under outputs/tables/expansion20_*.

## Figures built

| File | Path |
| --- | --- |
| fig1_benchmark_workflow.png | `paper/figures/fig1_benchmark_workflow.png` |
| fig2_expansion12_vs_20_summary.png | `paper/figures/fig2_expansion12_vs_20_summary.png` |
| fig3_representative_successes.png | `paper/figures/fig3_representative_successes.png` |
| fig4_ngc7814_failure.png | `paper/figures/fig4_ngc7814_failure.png` |
| fig5_sensitivity_recovery_cases.png | `paper/figures/fig5_sensitivity_recovery_cases.png` |
| fig6_holdout_rmse_comparison.png | `paper/figures/fig6_holdout_rmse_comparison.png` |
| fig7_claim_boundary_map.png | `paper/figures/fig7_claim_boundary_map.png` |

## Composition notes

- **Fig1:** matplotlib workflow schematic; dashed branch = tdf_5knot sensitivity.
- **Fig2:** bar chart from `controlled_expansion_comparison_summary.csv`.
- **Fig3:** 1×3 mosaic of existing `*_full_model_rotation_comparison.png` panels.
- **Fig4:** NGC7814 rotation + radial holdout map; descriptive failure label only.
- **Fig5:** radial maps (NGC5055, UGC05253) + UGC12506 holdout bars from diagnostics CSV.
- **Fig6:** expansion_20 per-galaxy holdout RMSE; hatched tdf_5knot = sensitivity only.
- **Fig7:** C20-A–H claim status map from `controlled_expansion_final_claims.csv`.

## Benchmark outputs

No files under `outputs/tables/expansion20_*` or other benchmark tables were modified.

## Regenerate

```bash
python3 scripts/build_paper_figures.py
```
