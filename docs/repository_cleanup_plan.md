# Repository cleanup plan (Zenodo / paper release)

**Purpose:** Make `tdf-galaxy-tau-benchmark` readable and reproducible for the controlled
expansion-20 manuscript **without changing scientific results**, benchmark metrics, or claim
boundaries.

## Principles

1. **Audit before deletion** — inventory and reference scan first (`scripts/build_repository_cleanup_audit.py`).
2. **Frozen science** — do not modify `outputs/tables/expansion*`, `controlled_expansion_*`, or claim CSVs.
3. **Keep provenance** — retain `data/raw/sparc/` and `data/processed/` SPARC inputs.
4. **Keep publication chain** — `paper/manuscript.{tex,pdf}`, `paper/figures/`, `paper/tables/`, `references.bib`.
5. **Reference-gated moves** — no file is deleted or archived if referenced in README, docs, paper, scripts, tests, or configs.

## Classification (7 buckets)

| Category | Scope | Action |
| --- | --- | --- |
| `keep_core` | `src/`, `scripts/`, `configs/`, `tests/`, `README.md`, `pyproject.toml`, `requirements.txt`, `.gitignore` | Keep |
| `keep_data` | `data/raw/sparc/`, `data/processed/` | Keep |
| `keep_outputs_frozen` | Benchmark tables/reports/figures, paper statistical summaries | Keep |
| `keep_paper` | `paper/` manuscript, figures, tables, bibliography | Keep |
| `keep_docs` | `docs/` methodology, status, claims, reviewer matrix, checklists | Keep |
| `cleanup_candidate` | `__pycache__/`, `.pytest_cache/`, `.DS_Store`, LaTeX aux | **Delete** (safe) |
| `archive_candidate` | Unreferenced superseded intermediates | **Move** to `archive/` only if unreferenced |

## Step workflow

### Step 1 — Audit (required first)

```bash
python3 scripts/build_repository_cleanup_audit.py
```

Writes:

- `outputs/tables/repository_file_inventory.csv`
- `outputs/tables/repository_cleanup_candidates.csv`
- `outputs/reports/repository_cleanup_audit_report.md`

### Step 2 — Reference check (automated)

The audit scans path strings in README, all `docs/*.md`, `paper/*`, `scripts/*.py`,
`tests/*.py`, `configs/*.yaml`, and `src/**/*.py`. Referenced archive candidates are
downgraded to `keep_outputs_frozen`.

### Step 3 — Safe cleanup

```bash
python3 scripts/build_repository_cleanup_audit.py --apply-cleanup
```

Allowed removals only:

- Python/pytest caches
- `.DS_Store`
- `paper/manuscript.{aux,log,out,bbl,blg,fls,fdb_latexmk}` (rebuilt by compile script)
- Local `.vscode/` if present

### Step 4 — Release docs

Update `README.md`, `docs/repository_map.md`, `docs/reproducibility_commands.md`,
`docs/zenodo_release_notes.md`.

### Step 5 — Validation

```bash
python3 -m pytest -q
python3 scripts/compile_paper_pdf.py
```

Optional (regenerates from frozen tables; does not refit):

```bash
python3 scripts/export_paper_tables.py
python3 scripts/build_paper_figures.py
```

## Explicit do-not-delete list

- Raw/processed SPARC data
- `expansion12_*` / `expansion20_*` / `controlled_expansion_*` outputs
- Claim traceability tables and failure-mode reports
- `docs/reviewer_objection_matrix.md`, `docs/pre_submission_checklist.md`
- `docs/project_status.md`, `docs/cursor_work_log.md`, `docs/data_sources.md`
- `docs/assumptions.md`, `docs/limitations.md`, `docs/controlled_expansion_results.md`
- `docs/paper_ready_claims.md`

## .gitignore hygiene

After cleanup, ensure caches and LaTeX debris stay untracked (see root `.gitignore`).
