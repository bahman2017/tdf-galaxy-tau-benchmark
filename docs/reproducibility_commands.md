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

## Expected headline artifacts

| Artifact | Path |
| --- | --- |
| Final claims | `outputs/tables/controlled_expansion_final_claims.csv` |
| Cohort comparison | `outputs/tables/controlled_expansion_comparison_summary.csv` |
| expansion-20 holdout | `outputs/tables/expansion20_holdout_validation.csv` |
| Final audit report | `outputs/reports/controlled_expansion20_final_audit_report.md` |
| Manuscript PDF | `paper/manuscript.pdf` |
