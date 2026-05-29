# Pre-Submission Checklist (Phase 5F-F)

> Phase 5F-F performs final manuscript polish and pre-submission QA only. No model fitting and no modification of benchmark CSV files.

## Build

- [ ] PDF compiled: **PASS** (`/Users/bahmanmasarratbakhsh/TDF_projects/tdf-galaxy-tau-benchmark/paper/manuscript.pdf`)
- [ ] Figures on disk: **7/7**
- [ ] Tables referenced in manuscript: **6/6**
- [ ] Equations present: **PASS**
- [ ] Author block: **PASS**

## Claim boundaries

- [ ] Prohibited phrases absent: **PASS**
- [ ] Required caveats present: **PASS**

## Stale content

- [ ] Manuscript stale phrases: **PASS**
- [ ] Table 6 (assumptions) updated: **PASS**
- [ ] Abstract grammar: **PASS**

## Bibliography

- [ ] Bib entries: **12** (expect $\geq 10$)

## Reproducibility commands

```bash
python3 scripts/run_expansion20_pipeline.py
python3 scripts/build_controlled_expansion_final_audit.py
python3 scripts/build_paper_figures.py
python3 scripts/export_paper_tables.py
python3 scripts/build_referee_readiness_report.py
python3 scripts/compile_paper_pdf.py
```

## Known remaining limitations

- Controlled expansion-20 cohort only (not full SPARC)
- Fixed baryons; no final M/L calibration
- K_tau fixed, not measured
- Lensing not tested
- NGC7814 canonical failure retained
- tdf_5knot sensitivity-only
