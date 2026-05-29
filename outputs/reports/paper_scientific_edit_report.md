# Paper Scientific Edit Report (Phase 5F-D)

> Editing and layout polish only. No model fitting; benchmark CSV files unchanged.

## Author block

- Bahman Masarrat, Independent Researcher, bmasarrat@gmail.com

## Figure numbering (document order)

1. `fig1_benchmark_workflow.png` — after Controlled SPARC benchmark protocol
2. `fig2_expansion12_vs_20_summary.png` — Results (expansion_20)
3. `fig3_representative_successes.png` — Results
4. `fig4_ngc7814_failure.png` — Failure modes
5. `fig5_sensitivity_recovery_cases.png` — Failure modes
6. `fig6_holdout_rmse_comparison.png` — Failure modes (end of section)
7. `fig7_claim_boundary_map.png` — Claim-boundary appendix

Removed workflow figure placement after Conclusion.

## Table formatting

- Classification and status columns use readable English labels (no malformed `robust{} tdf{}` escapes).
- Claim traceability table uses full claim text (wide column).
- Metric names in Table 3 use readable labels.

## Prose edits

- Abstract: concise journal-style with all caveats and core 15/20 statement.
- Introduction: controlled benchmark framing; holdout motivation.
- Methods: explicit definitions of primary/sensitivity models and four failure classes.
- Results: expansion_20 main; expansion_12 nested context.
- Limitations: fixed baryons, no final M/L, no lensing, not full SPARC, fixed $K_\tau$, flexibility risk.

## Bibliography

- SPARC (Lelli et al. 2016), NFW, Burkert, MOND, repository misc entry.

## Regenerate

```bash
python3 scripts/export_paper_tables.py
python3 scripts/compile_paper_pdf.py
```
