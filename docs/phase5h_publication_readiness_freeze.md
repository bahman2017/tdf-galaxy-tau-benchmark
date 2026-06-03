# Phase 5H-A — Publication readiness freeze audit

**Date:** 2026-05-29  
**Baseline tag:** `v0.1.5-notation-qa` → `91eea5cfb9a8b60767e8d908dc3500418b5e3358`  
**Verdict:** **Ready with minor metadata blockers** — scientifically frozen for paper / Zenodo snapshot; see §8.

This pass is **documentation and package QA only**. No benchmark rerun, no frozen CSV rewrites, no code behavior changes.

---

## 1. Release stack

| Tag | Commit | Milestone |
| --- | --- | --- |
| `v0.1.0-expansion20-paper` | `0da4190` | Expansion-20 paper package |
| `v0.1.1-notation-alignment` | `144c77d` | Doc/manuscript K_g alignment |
| `v0.1.2-notation-aliases` | `533ae11` | Phase 5G-A config alias layer |
| `v0.1.3-notation-compatibility` | `e80eae1` | Phase 5G-B loader regression lock |
| `v0.1.4-internal-kg-rename` | `08cfc5d` | Phase 5G-C-B internal `k_g` rename |
| `v0.1.5-notation-qa` | `91eea5c` | Phase 5G-D final notation QA |

**Zenodo preprint (manuscript PDF):** [10.5281/zenodo.20437254](https://doi.org/10.5281/zenodo.20437254)

---

## 2. Current scientific claim summary (frozen expansion_20)

Authoritative sources: `outputs/tables/controlled_expansion_final_claims.csv`, `docs/paper_ready_claims.md`, `docs/controlled_expansion_results.md`.

| Headline | Status |
| --- | --- |
| Primary **`tdf_3knot` robust holdout success** | **15 / 20** galaxies |
| **`tdf_5knot` sensitivity-recovery** | **3** galaxies (not primary success) |
| **NGC7814** | All-TDF holdout failure (canonical) |
| **UGC00128** | Mixed near-tie |
| **Scope** | Pre-registered **expansion_20** controlled cohort only (nested expansion_12) |

**FINAL-E20 language** (from frozen claims CSV): primary conservative `tdf_3knot` success in 15/20; three sensitivity-recovery cases; NGC7814 sole all-TDF failure; UGC00128 mixed near-tie.

All public claims remain **controlled-subset / expansion_20** — not full SPARC.

---

## 3. Claim boundary checklist

| Boundary | Result | Evidence |
| --- | --- | --- |
| No dark-matter disproof | **PASS** | C20-F `prohibited`; README, `paper_ready_claims.md`, manuscript caveats |
| No full-SPARC validation | **PASS** | C20-E `not_supported`; docs state expansion_20 only |
| No lensing confirmation | **PASS** | C20-G `not_tested`; limitations docs |
| No universal τ profile | **PASS** | C20-H `not_supported`; README + theory docs |
| No new τ formula introduced | **PASS** | Phase 5G/5H changed notation only; radial closure unchanged |

---

## 4. Reproducibility checklist

| Command | Safe / long | Role |
| --- | --- | --- |
| `python3 -m pytest -q` | **Safe** (~2 min) | Validation; 264 tests; no benchmark refit |
| `python3 scripts/build_controlled_expansion_final_audit.py` | **Safe** | Regenerates audit **reports from frozen tables** only |
| `python3 scripts/export_paper_tables.py` | **Safe** | Exports LaTeX tables + manuscript source from frozen CSVs |
| `python3 scripts/build_paper_figures.py` | **Safe** | Copies/composes paper figures from existing PNGs |
| `python3 scripts/compile_paper_pdf.py` | **Safe** | PDF build from `paper/manuscript.tex` |
| `python3 scripts/build_referee_readiness_report.py` | **Safe** | QA report only |
| `python3 scripts/build_repository_cleanup_audit.py` | **Safe** | Inventory audit only |
| `python3 scripts/run_expansion20_pipeline.py` | **Long / benchmark** | Full expansion_20 refit pipeline — **not required** for snapshot |
| `python3 scripts/run_expansion12_pipeline.py` | **Long / benchmark** | expansion_12 refit — **not required** for snapshot |
| `python3 scripts/run_photometry_prior_ktau_sensitivity.py` | **Long** | Phase 4L sensitivity — frozen outputs already committed |

**Minimum snapshot check:**

```bash
python3 -m pytest -q
python3 scripts/build_controlled_expansion_final_audit.py
python3 scripts/compile_paper_pdf.py   # optional if PDF already committed
```

Full command reference: [`reproducibility_commands.md`](reproducibility_commands.md).

---

## 5. Artifact inventory

### Key CSVs (frozen benchmark)

| Artifact | Path | Notes |
| --- | --- | --- |
| Final claims | `outputs/tables/controlled_expansion_final_claims.csv` | C20-A–H + FINAL-E20 |
| Cohort comparison | `outputs/tables/controlled_expansion_comparison_summary.csv` | expansion_12 vs expansion_20 |
| expansion_20 holdout | `outputs/tables/expansion20_holdout_validation.csv` | Primary metric source |
| expansion_20 failure summary | `outputs/tables/expansion20_failure_mode_summary.csv` | Per-galaxy classification |
| expansion_20 claims traceability | `outputs/tables/expansion20_claim_traceability.csv` | |
| expansion_20 model comparison | `outputs/tables/expansion20_model_comparison.csv` | |
| expansion_20 tau profiles | `outputs/tables/expansion20_tau_profiles.csv` | Legacy **`K_tau`** column |
| Six-galaxy legacy | `outputs/tables/sparc_*` | Phases 3–4 subset artifacts |

**Note:** `outputs/tables/controlled_expansion_final_metrics.csv` is **not present** in the repository; use `controlled_expansion_comparison_summary.csv` and `expansion20_holdout_validation.csv` for headline metrics.

### Key reports

| Report | Path |
| --- | --- |
| Final expansion_20 audit | `outputs/reports/controlled_expansion20_final_audit_report.md` |
| expansion_20 benchmark | `outputs/reports/expansion20_benchmark_report.md` |
| expansion_20 failure analysis | `outputs/reports/expansion20_failure_mode_analysis_report.md` |
| Pre-submission QA | `docs/pre_submission_checklist.md` |
| Notation QA | `docs/phase5g_final_notation_qa.md` |

### Key figures

| Location | Count | Notes |
| --- | ---: | --- |
| `outputs/figures/sparc_subset/` | 66 PNG | Diagnostic + expansion cohort figures |
| `paper/figures/` | (via build script) | Seven publication figures when `build_paper_figures.py` run |
| Inventory | `outputs/tables/paper_figure_inventory.csv` | If generated |

### Manuscript files

| File | Role |
| --- | --- |
| `paper/manuscript.tex` | Source (K_g notation; legacy K_τ note) |
| `paper/manuscript.pdf` | Committed PDF |
| `paper/tables/table1–6_*.tex` | LaTeX tables |
| `paper/references.bib` | Bibliography |

### Release / citation metadata

| File | Role | QA note |
| --- | --- | --- |
| `CITATION.cff` | Software citation | Version `v0.1.0-expansion20-paper` — **stale vs tag stack** |
| `docs/zenodo_release_notes.md` | Zenodo deposit template | Claim boundaries current |
| `README.md` | Landing page | Status section updated in 5H-A |
| `pyproject.toml` | Package version `0.1.0` | **stale vs v0.1.5** |

---

## 6. Notation freeze (post Phase 5G)

| Symbol | Policy |
| --- | --- |
| **k_g / K_g** | Preferred internal projection coefficient (code, manuscript) |
| **k_tau / K_tau** | Legacy only: YAML keys, `.k_tau` property, **frozen CSV/report column labels**, sensitivity axis |
| **kappa_tau / κ_tau** | Field stiffness only — never projection |

Frozen benchmark CSV headers remain **`K_tau`**. No in-place column renames without a versioned migration.

Reference: [`phase5g_final_notation_qa.md`](phase5g_final_notation_qa.md).

---

## 7. Test validation

```bash
python3 -m pytest -q
```

**Result (Phase 5H-A):** **264 passed** (2 expected DeprecationWarnings from legacy `k_tau=` in tests).

---

## 8. Publication readiness conclusion

### Overall: **Ready with minor metadata blockers**

The **scientific benchmark package** (frozen expansion_20 tables, conservative claims, manuscript, tests, notation migration) is **ready for a publication / Zenodo readiness snapshot** at `v0.1.5-notation-qa`.

### Blockers (non-scientific; recommended before new Zenodo software deposit)

| Blocker | Severity | Recommendation |
| --- | --- | --- |
| No root `LICENSE` file | Low | Add MIT `LICENSE` matching `pyproject.toml` / `CITATION.cff` |
| `CITATION.cff` version `v0.1.0-expansion20-paper` | Low | Bump to `v0.1.5-notation-qa` or new `v0.1.6-publication-freeze` on tag |
| `pyproject.toml` version `0.1.0` | Low | Align with release tag if publishing new software version |
| `controlled_expansion_final_metrics.csv` absent | Informational | Documented; use comparison + holdout CSVs |

### Recommended final pre-submission steps

1. Author/journal formatting pass on `paper/manuscript.pdf` (Phase 5F follow-up).
2. Sync `CITATION.cff` + README software citation version with chosen release tag.
3. Add root `LICENSE` file (MIT).
4. Optional: tag **`v0.1.6-publication-freeze`** on this audit commit for snapshot reproducibility.
5. Optional Phase **5G-C-C**: production YAML `k_g` keys — **not required** for publication freeze.

### Zenodo / paper snapshot statement

**Yes** — the repository is ready for a **paper-readiness / Zenodo software snapshot**. Existing Zenodo preprint DOI covers the manuscript.

---

## 9. Phase 5H-B addendum — metadata hygiene (2026-05-29)

Phase **5H-B** cleared the metadata blockers identified in §8:

| Item (was blocker) | Status after 5H-B |
| --- | --- |
| No root `LICENSE` file | **Cleared** — MIT `LICENSE` at repo root (Copyright 2026 Bahman Masarrat) |
| `CITATION.cff` version stale | **Cleared** — `v0.1.6-publication-freeze`; K_g abstract; DOI `10.5281/zenodo.20437254` preserved |
| `pyproject.toml` version `0.1.0` | **Cleared** — version `0.1.6` |

**Updated verdict:** **Ready** for tag **`v0.1.6-publication-freeze`**.

| Item | Status |
| --- | --- |
| `controlled_expansion_final_metrics.csv` absent | Informational only — unchanged |
