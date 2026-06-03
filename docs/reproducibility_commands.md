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

Release tags: `v0.1.0-expansion20-paper` → … → **`v0.1.5-notation-qa`** → target **`v0.1.6-publication-freeze`** (after Phase 5H-B metadata hygiene).

Phase **5H-B** (**complete**): LICENSE, `CITATION.cff`, `pyproject.toml` version sync — [`phase5h_publication_readiness_freeze.md`](phase5h_publication_readiness_freeze.md) §9.

**Safe commands (no refit):** `pytest`, `build_controlled_expansion_final_audit.py`, `export_paper_tables.py`, `build_paper_figures.py`, `compile_paper_pdf.py`.

**Long commands (benchmark refit):** `run_expansion20_pipeline.py`, `run_expansion12_pipeline.py` — not required for snapshot validation.

## Phase 6A protocol (documentation only — no pipeline yet)

Read-only protocol docs (no scripts in 6A):

- [`phase6a_2d_frozen_map_protocol.md`](phase6a_2d_frozen_map_protocol.md)
- [`phase6a_data_requirements.md`](phase6a_data_requirements.md)
- [`phase6a_success_failure_criteria.md`](phase6a_success_failure_criteria.md)

**Do not run** expansion_20 refit or modify `outputs/tables/expansion20_*` when validating Phase 6A docs.

## Phase 6B audit (read-only; no refit)

```bash
python3 scripts/build_phase6b_data_availability_audit.py
```

Produces `outputs/tables/phase6b_expansion20_data_availability_audit.csv`,
`outputs/tables/phase6b_pilot_candidate_ranking.csv`, and
`outputs/reports/phase6b_pilot_selection_report.md`.

## Phase 6C frozen pseudo-2D maps (no refit)

All five Tier-1 primary pilots:

```bash
python3 scripts/build_phase6c_frozen_pseudo2d_map.py --all-primary-pilots
```

Single galaxy:

```bash
python3 scripts/build_phase6c_frozen_pseudo2d_map.py --galaxy-id DDO161
```

Combined audit only (maps already built):

```bash
python3 scripts/build_phase6c_frozen_pseudo2d_map.py --all-primary-pilots --audit-only
```

Outputs: `outputs/tables/phase6c_primary_pilot_map_summary.csv`,  
`outputs/reports/phase6c_primary_pilot_smoothness_audit.md`

## Phase 6C-C gradient diagnostics (read-only; no τ change)

```bash
python3 scripts/build_phase6c_gradient_diagnostics.py
```

Outputs: `outputs/tables/phase6c_primary_pilot_gradient_diagnostics.csv`,  
`outputs/reports/phase6c_gradient_diagnostic_report.md`  
Options menu: `docs/phase6c_gradient_regularization_options.md`

## Phase 6C-D regularization pre-registration (protocol only)

Config: `configs/phase6d_regularization_preregistration.yaml`  
Docs: `docs/phase6d_frozen_gradient_regularization_preregistration.md`,  
`docs/phase6d_regularization_acceptance_criteria.md`

**No builder script in 6C-D** — implementation is Phase **6C-E**.

## Phase 6C-E regularized pseudo-2D maps (R2+R6)

```bash
python3 scripts/build_phase6d_regularized_maps.py --all-primary-pilots
python3 -m pytest -q tests/test_phase6d_regularized_maps.py
```

Outputs: `outputs/tables/phase6d_*`, `outputs/maps/phase6d/`,  
`outputs/reports/phase6d_regularization_cohort_report.md`  
Results: `docs/phase6d_regularized_map_results.md`

**Phase 6D remains blocked** — 0/5 pilots pass all hard gates after R2+R6 (negative cohort).

## Phase 6E negative-result decision gate (documentation only)

No builder script. Read:

- `docs/phase6e_negative_result_decision_gate.md`
- `outputs/reports/phase6e_negative_result_summary.md`

Phase 6D and lensing/deflection remain **blocked**. Next planned phase: **6F** (map-smooth reconstruction protocol design).

## Expected headline artifacts

| Artifact | Path |
| --- | --- |
| Final claims | `outputs/tables/controlled_expansion_final_claims.csv` |
| Cohort comparison | `outputs/tables/controlled_expansion_comparison_summary.csv` |
| expansion-20 holdout | `outputs/tables/expansion20_holdout_validation.csv` |
| Final audit report | `outputs/reports/controlled_expansion20_final_audit_report.md` |
| Manuscript PDF | `paper/manuscript.pdf` |
