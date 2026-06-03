# Project Status

## Current phase

**Phase 6C-B — primary-pilot maps + smoothness audit** — **complete** (5 maps; no fits)

**Publication-freeze tag:** **`v0.1.6-publication-freeze`** → `0e4b202` (Phase 5 closed).

**Next scientific phase:** **Phase 6C-C** — frozen radial τ-gradient diagnostic (Phase 6D **blocked**: 0/5 pilots pass smoothness).

**Phase 6C-A — frozen pseudo-2D map (DDO161 pilot)** — **complete**

**Phase 6B — data availability audit & pilot selection** — **complete**

**Phase 6A — 2D / frozen-map test protocol** — **complete** (design only; no fits)

**Phase 5I — v0.1.6 publication-freeze release notes** — **complete**

**Phase 5G notation migration — complete** (tags `v0.1.2`–`v0.1.5`; QA in `docs/phase5g_final_notation_qa.md`).

Supporting steps (all complete):

- **Phase 5G-C-B** — internal `k_g` rename — tag `v0.1.4-internal-kg-rename`
- **Phase 5G-C-A** — internal rename audit — `docs/phase5g_internal_rename_audit.md`
- **Phase 5G-B** — loader compatibility regression lock — tag `v0.1.3-notation-compatibility`
- **Phase 5G-A** — config alias layer — tag `v0.1.2-notation-aliases`
- **Phase 5E/5F** — controlled expansion-20 publication package

Internal code uses **`k_g`** as the primary projection field; read-only **`.k_tau`** property and legacy YAML/CSV labels remain for backward compatibility. **`kappa_tau` / κ_tau** is field stiffness only. Frozen benchmark CSV column **`K_tau`** unchanged.

### Phase 6C-B deliverables

- Maps for all five Tier-1 pilots: DDO161, UGC07524, UGC08490, IC2574, NGC2403
- `outputs/tables/phase6c_primary_pilot_map_summary.csv`, `outputs/reports/phase6c_primary_pilot_smoothness_audit.md`
- `docs/phase6c_primary_pilot_map_results.md` — **5/5 radial PASS**, **0/5 smoothness PASS** (frozen 1D dτ/dr); Phase 6D blocked

### Phase 6C-A deliverables

- `src/tdf_galaxy_tau/analysis/phase6c_frozen_pseudo2d.py`, `scripts/build_phase6c_frozen_pseudo2d_map.py`
- DDO161 pilot map and diagnostics (first implementation)

### Phase 6B deliverables

- `docs/phase6b_data_availability_audit.md`, `docs/phase6b_pilot_selection_rationale.md`
- `scripts/build_phase6b_data_availability_audit.py` — read-only L1–L6 audit
- `outputs/tables/phase6b_expansion20_data_availability_audit.csv`, `phase6b_pilot_candidate_ranking.csv`
- `outputs/reports/phase6b_pilot_selection_report.md`
- Primary pilots (top 5): **DDO161**, **UGC07524**, **UGC08490**, **IC2574**, **NGC2403**

### Phase 6A deliverables

- `docs/phase6a_2d_frozen_map_protocol.md` — pre-registered frozen-map test protocol
- `docs/phase6a_data_requirements.md` — L1–L6 data layers and repo feasibility
- `docs/phase6a_success_failure_criteria.md` — success/failure metrics and claim checklist
- **No new fits**; expansion_20 1D benchmark unchanged; Phase 6 is a **new test layer**

### Phase 5I deliverables

- `docs/release_notes_v0.1.6_publication_freeze.md` — publication-freeze release notes
- Updated `docs/zenodo_release_notes.md` for Zenodo software deposit

### Phase 5H-B deliverables

- Root `LICENSE` (MIT, Copyright 2026 Bahman Masarrat)
- `CITATION.cff` → `v0.1.6-publication-freeze`; K_g abstract; Zenodo DOI relation preserved
- `pyproject.toml` version `0.1.6`

### Phase 5H-A deliverables

- `docs/phase5h_publication_readiness_freeze.md` — release stack, claim boundaries, artifact inventory, **ready with minor metadata blockers**
- **264 tests passed**; no benchmark rerun; no frozen output changes

### Phase 5G-D deliverables

- `docs/phase5g_final_notation_qa.md` — grep audit, claim-boundary check, **PASS**
- **264 tests passed**; no benchmark rerun; no frozen output changes

### expansion_20 headline (frozen)

In the pre-registered controlled **expansion_20** cohort:

- **Primary `tdf_3knot` robust holdout success:** 15 of 20 galaxies  
- **`tdf_5knot` sensitivity-recovery:** 3 galaxies (not primary success)  
- **All-TDF holdout failure:** NGC7814 (canonical)  
- **Mixed near-tie:** UGC00128  

Authoritative claims: `docs/paper_ready_claims.md` (C20-A–C20-H), `docs/controlled_expansion_results.md`, `outputs/tables/controlled_expansion_final_claims.csv`.

### Notation (Phase 5G complete; 5G-C-C optional)

| Symbol | Role |
| --- | --- |
| **K_g** | Gravitational **projection coefficient** (preferred notation; radial closure \(v_\tau^2 = r K_g \, d\tau/dr\)). |
| **κ_tau** | **Dynamical stiffness** in the mother field equation; **not** interchangeable with \(K_g\). |
| **K_tau** (legacy) | Historical benchmark/config label and frozen CSV column name for the projection coefficient. |

See `docs/theory_summary.md`, `docs/phase5g_final_notation_qa.md`, and `docs/roadmap.md`.

## Completed tasks

- Phase 1A: SPARC raw rotmod ingestion and standardization.
- Phase 1B: deterministic subset selection and QC reporting.
- Phase 2A: per-galaxy radial τ reconstruction from rotation residuals for selected galaxies.
- Phase 3A: fitted baryonic-only, NFW, and Burkert baselines (legacy linear bounds).
- Phase 3A-Audit: boundary and high-chi-square flags on legacy baselines.
- Phase 3A-R: log-space multistart NFW/Burkert refit with wider documented bounds; legacy outputs preserved.
- Phase 3M: MOND/RAR baselines (fixed and fitted a0, optional RAR) on six-galaxy subset; combined comparison with halo refit.
- Phase 3B: TDF 3/4/5-knot fitted models with AIC/BIC comparison vs halo refit and MOND.
- Phase 3C: holdout validation, legacy **K_tau** (\(K_g\)-like) / bounds sensitivity, knot-count stability, smoothness diagnostics.
- Phase 4A: per-galaxy failure-mode classification and claim traceability matrix (A–H).
- Phase 4B: paper-ready results summary, publication table, and conservative claim language (`docs/results_summary.md`, `docs/paper_ready_claims.md`).
- Phase 4C: normalized τ-pattern similarity, outlier scores, overlays (`docs/normalized_tau_patterns.md`).
- Phase 4D: NGC7814 structural/holdout/pattern diagnostics (`docs/ngc7814_failure_mode.md`).
- Phase 4E: per-point holdout residual CSV and radial failure-map figures/reports.
- Phase 4F: diagnostic disk/bulge M/L scaling grid and holdout sensitivity (`docs/ml_sensitivity_audit.md`).
- Phase 4G: fair scaled-baseline refit (TDF + NFW + MOND) on same M/L grid (`docs/ml_scaled_baseline_comparison.md`).
- Phase 4H: claim matrix I–N, post-M/L summary tables/reports, updated `docs/paper_ready_claims.md` (no new fits).
- Phase 4I: diagnostic prior scaffold on Phase 4G outputs (`configs/ml_priors.yaml`, `docs/ml_prior_framework.md`).
- Phase 4I-Audit: prior weight verification, NGC7814 layered interpretation.
- Phase 4J: SPARC photometry metadata ingestion (175 galaxies; subset context for six galaxies).
- Phase 4K: photometry-informed diagnostic prior weights (`docs/photometry_informed_ml_priors.md`).
- Phase 4L: legacy **K_tau** sensitivity audit on Phase 4K harness (`docs/ktau_sensitivity.md`).
- Phase 4M: final controlled-subset audit package (`docs/controlled_subset_audit.md`; no new fits).
- Phase 5A: pre-registered expansion protocol for cohorts of 12 and 20 galaxies (`docs/subset_expansion_protocol.md`; no fits).
- Phase 5B: expansion_12 full benchmark pipeline (`docs/expansion12_results.md`; 12 galaxies).
- Phase 5B-Audit / 5B-R: failure/mixed diagnostics and radial holdout maps (expansion_12).
- Phase 5C: expansion_20 controlled benchmark (`docs/expansion20_results.md`; sensitivity_recovery class).
- Phase 5D: expansion_20 failure/mixed/sensitivity audit (5 non-robust galaxies).
- Phase 5E: expansion_12 vs expansion_20 final audit package (`docs/controlled_expansion_results.md`; claims C20-A–H).
- Phase 5F-A–F: paper scaffold, figures, LaTeX tables, manuscript PDF, scientific edit, referee readiness, pre-submission QA (`docs/pre_submission_checklist.md`).
- Phase 5G-A: `normalize_projection_coefficient` alias layer (`src/tdf_galaxy_tau/config/notation.py`; tag `v0.1.2-notation-aliases`).
- Phase 5G-B: compatibility regression lock (`tests/test_notation_compatibility_regression.py`; tag `v0.1.3-notation-compatibility`).
- Phase 6B: expansion_20 data audit and pilot selection (`docs/phase6b_*.md`; audit only).
- Phase 6A: 2D / frozen-map test protocol (`docs/phase6a_*.md`; design only).
- Phase 5I: v0.1.6 publication-freeze release notes (`docs/release_notes_v0.1.6_publication_freeze.md`).
- Phase 5H-B: metadata hygiene (LICENSE, CITATION.cff, pyproject.toml `0.1.6`; tag `v0.1.6-publication-freeze`).
- Phase 5H-A: publication readiness freeze audit (`docs/phase5h_publication_readiness_freeze.md`).
- Phase 5G-D: final notation QA (`docs/phase5g_final_notation_qa.md`; tag `v0.1.5-notation-qa`).
- Phase 5G-C-B: internal `k_g` field rename with `.k_tau` property aliases (tag `v0.1.4-internal-kg-rename`).
- Phase 5G-C-A: internal rename audit (`docs/phase5g_internal_rename_audit.md`).
- Release prep: repository cleanup audit, Git tag `v0.1.0-expansion20-paper`, Zenodo preprint DOI [10.5281/zenodo.20437254](https://doi.org/10.5281/zenodo.20437254).

## Current blockers

- Halo degeneracy and high reduced chi-square may persist after refit.

## Next recommended tasks

1. **Phase 6C-C:** frozen radial τ-gradient diagnostic before Phase 6D (smoothness gate unmet on all primary pilots).
2. Author/journal formatting review of `paper/manuscript.pdf`.
3. Optional blocked-holdout for UGC12506.
4. Explicit bulge L_3.6 or stellar-population priors before calibrated M/L language.
5. Full SPARC and lensing deferred per claim boundaries.

## Latest validation/test results

- `python3 -m pytest -q`
- `python3 scripts/compile_paper_pdf.py`
- `python3 scripts/build_controlled_expansion_final_audit.py` (regenerates audit reports from frozen tables only)

## Claim boundary (expansion_20)

- **Controlled expansion_20 cohort only** — not full-SPARC validation.
- **15/20** primary **`tdf_3knot`** robust holdout success; **3** sensitivity-recovery; **NGC7814** all-TDF failure; **UGC00128** mixed near-tie.
- **`tdf_5knot`** sensitivity-only; not primary success metric.
- No dark-matter disproof; no ΛCDM replacement; **lensing not tested**; no universal τ-profile; no final M/L calibration.
- Legacy six-galaxy subset claims (5/6) remain documented under Phases 4A–4M in `docs/controlled_subset_audit.md`.
