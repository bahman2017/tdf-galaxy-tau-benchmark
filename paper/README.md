# TDF Controlled Expansion Benchmark — Paper Package

**Phase 5F-A:** manuscript scaffold and frozen figure/table inventory only.

This directory does **not** rerun model fitting or modify benchmark outputs under `outputs/tables/expansion20_*` or related Phase 5B–5E artifacts.

## Contents

| Path | Purpose |
| --- | --- |
| `manuscript.tex` | LaTeX skeleton (placeholder prose) |
| `references.bib` | Bibliography stub |
| `figures/` | Copy or symlink finalized figures here before submission |
| `tables/` | LaTeX/CSV exports for manuscript tables |

## Build publication figures (Phase 5F-B)

From repository root:

```bash
python3 scripts/build_paper_figures.py
```

Writes seven PNG files to `paper/figures/` and `outputs/reports/paper_figures_report.md`. No model fitting.

## Regenerate inventories

From repository root:

```bash
python3 scripts/build_paper_package_scaffold.py
```

Writes:

- `outputs/tables/paper_figure_inventory.csv`
- `outputs/tables/paper_table_inventory.csv`
- `outputs/reports/paper_package_scaffold_report.md`

## Scientific edit (Phase 5F-D)

Phase 5F-D polishes prose, table labels, figure order, and bibliography. Regenerate via the export script below; see `outputs/reports/paper_scientific_edit_report.md`.

## Export tables and manuscript draft (Phase 5F-C)

```bash
python3 scripts/export_paper_tables.py
```

Writes six `paper/tables/*.tex` files, regenerates `paper/manuscript.tex` (first-draft prose), and attempts PDF compile.

## Compile manuscript only

```bash
python3 scripts/compile_paper_pdf.py
```

Uses `latexmk` or `pdflatex`/`bibtex` when available; otherwise reports LaTeX unavailable without failing tests.

## Reproducibility chain (benchmark results)

1. **Cohort plan:** `outputs/tables/sparc_subset_expansion_plan.csv` (Phase 5A)
2. **expansion_12:** `python3 scripts/run_expansion12_pipeline.py`
3. **expansion_20:** `python3 scripts/run_expansion20_pipeline.py`
4. **Failure audits:** `python3 scripts/analyze_expansion20_failure_modes.py`
5. **Final audit:** `python3 scripts/build_controlled_expansion_final_audit.py`

Authoritative claim language: `docs/paper_ready_claims.md`, `outputs/tables/controlled_expansion_final_claims.csv`.

## Claim boundaries

Do **not** state in the manuscript:

- Dark matter is disproven
- ΛCDM is replaced
- Full-SPARC validation
- Lensing confirmation
- A universal τ-profile across galaxies

Primary success metric: `tdf_3knot` beats NFW **and** MOND on even/odd holdout RMSE (`robust_tdf_success`). `tdf_5knot` is sensitivity-only.

## Figure sources

See `outputs/tables/paper_figure_inventory.csv` for `figure_id`, source paths, and `status` (`existing` vs `needs_composition`).
