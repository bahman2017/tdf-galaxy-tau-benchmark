# Reproducibility commands

Run all commands from the repository root with the virtual environment activated and
`pip install -e ".[plots,dev]"` (or `requirements.txt`) completed.

## Validation (no refitting)

```bash
python3 -m pytest -q
```

## Controlled expansion-20 benchmark

Full pipeline (ingestion steps may be skipped if processed CSVs already exist):

```bash
python3 scripts/run_expansion20_pipeline.py
python3 scripts/build_controlled_expansion_final_audit.py
```

Nested expansion-12 only:

```bash
python3 scripts/run_expansion12_pipeline.py
```

## Paper package (reads frozen benchmark tables; export scripts do not refit)

```bash
python3 scripts/export_paper_tables.py
python3 scripts/build_paper_figures.py
python3 scripts/compile_paper_pdf.py
```

## Optional QA reports (documentation only)

```bash
python3 scripts/build_referee_readiness_report.py
python3 scripts/build_paper_package_scaffold.py
python3 scripts/build_repository_cleanup_audit.py
```

## Repository cleanup (release hygiene only)

Audit only:

```bash
python3 scripts/build_repository_cleanup_audit.py
```

Safe cache/LaTeX debris removal:

```bash
python3 scripts/build_repository_cleanup_audit.py --apply-cleanup
```

## Notation

Frozen benchmark tables use legacy **K_tau** column names. Config loaders accept **both**:

- Preferred: `k_g` / `K_g` (gravitational projection coefficient)
- Legacy: `k_tau` / `K_tau` (same role; backward compatible)

`kappa_tau` is field stiffness and is **not** accepted as a projection alias. See
[`theory_summary.md`](theory_summary.md) and `src/tdf_galaxy_tau/config/notation.py`.

Loader equivalence (`k_g` ≡ legacy `k_tau`) is regression-locked in Phase **5G-B** (**complete**):
`tests/test_notation_compatibility_regression.py`.

Release tags: `v0.1.0-expansion20-paper` → … → **`v0.1.5-notation-qa`** (`91eea5c`).

Phase **5H-A** (**complete**): publication readiness freeze — [`phase5h_publication_readiness_freeze.md`](phase5h_publication_readiness_freeze.md). Suggested tag after audit: **`v0.1.6-publication-freeze`**.

**Safe commands (no refit):** `pytest`, `build_controlled_expansion_final_audit.py`, `export_paper_tables.py`, `build_paper_figures.py`, `compile_paper_pdf.py`.

**Long commands (benchmark refit):** `run_expansion20_pipeline.py`, `run_expansion12_pipeline.py` — not required for snapshot validation.

## Expected headline artifacts

| Artifact | Path |
| --- | --- |
| Final claims | `outputs/tables/controlled_expansion_final_claims.csv` |
| Cohort comparison | `outputs/tables/controlled_expansion_comparison_summary.csv` |
| expansion-20 holdout | `outputs/tables/expansion20_holdout_validation.csv` |
| Final audit report | `outputs/reports/controlled_expansion20_final_audit_report.md` |
| Manuscript PDF | `paper/manuscript.pdf` |
