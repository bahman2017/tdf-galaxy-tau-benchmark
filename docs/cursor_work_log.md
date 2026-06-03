# Cursor Work Log

## Date/time

Wednesday, May 27, 2026 (UTC-7)

## Prompt summary

Phase 6C-A: frozen axisymmetric pseudo-2D τ-map for DDO161 (no refit).

## Files changed

- `src/tdf_galaxy_tau/analysis/phase6c_frozen_pseudo2d.py`, `scripts/build_phase6c_frozen_pseudo2d_map.py`, tests
- DDO161 map outputs under `outputs/maps/phase6c/`, tables, report, figure
- docs: `project_status.md`, `roadmap.md`, `reproducibility_commands.md`, `phase6b_pilot_selection_rationale.md`

## Tests run

- `python3 scripts/build_phase6c_frozen_pseudo2d_map.py --galaxy-id DDO161`
- `python3 -m pytest -q`

## Notes

- K_g=1.0 from frozen profile; tau_retuned=false.
- Radial consistency PASS; smoothness FAIL reflects frozen 1D dτ/dr jumps (not map retuning).

---

## Date/time

Wednesday, May 27, 2026 (UTC-7)

## Prompt summary

Phase 6B: expansion_20 data availability audit and conservative pilot selection (no fits).

## Files changed

- `src/tdf_galaxy_tau/analysis/phase6b_data_availability.py` (new)
- `scripts/build_phase6b_data_availability_audit.py`, `tests/test_phase6b_data_availability_audit.py` (new)
- `docs/phase6b_data_availability_audit.md`, `docs/phase6b_pilot_selection_rationale.md` (new)
- `outputs/tables/phase6b_*.csv`, `outputs/reports/phase6b_pilot_selection_report.md` (new)
- `docs/project_status.md`, `docs/roadmap.md`, `docs/reproducibility_commands.md`

## Tests run

- `python3 scripts/build_phase6b_data_availability_audit.py`
- `python3 -m pytest -q`

## Notes

- Primary pilots: DDO161, UGC07524, UGC08490, IC2574, NGC2403.
- No expansion_20 rerun; Phase 5 15/20 unchanged.
- Next: Phase 6C frozen pseudo-2D map construction.

---

## Date/time

Wednesday, May 27, 2026 (UTC-7)

## Prompt summary

Phase 6A: pre-registered protocol for 2D / frozen-map effective-gravity test (design only; no fits).

## Files changed

- `docs/phase6a_2d_frozen_map_protocol.md` (new)
- `docs/phase6a_data_requirements.md` (new)
- `docs/phase6a_success_failure_criteria.md` (new)
- `docs/project_status.md`, `docs/roadmap.md`, `docs/reproducibility_commands.md`, `docs/cursor_work_log.md`

## Tests run

- `python3 -m pytest -q` — 264 passed

## Notes

- Documentation-only; expansion_20 1D benchmark unchanged; Phase 6 is a new test layer.
- Next: Phase 6B (data availability audit + pilot galaxy selection).

---

## Date/time

Wednesday, May 29, 2026 (UTC-7)

## Prompt summary

Phase 5I: v0.1.6 publication-freeze release notes and Zenodo documentation update.

## Files changed

- `docs/release_notes_v0.1.6_publication_freeze.md` (new)
- `docs/zenodo_release_notes.md`, `docs/project_status.md`, `docs/roadmap.md`, `README.md`, `docs/cursor_work_log.md`

## Tests run

- `python3 -m pytest -q` — 264 passed

## Notes

- Documentation-only; no benchmark rerun or frozen output changes.
- Next scientific phase: Phase 6A (2D / frozen-map test formulation).

---

## Date/time

Wednesday, May 29, 2026 (UTC-7)

## Prompt summary

Phase 5H-B: metadata hygiene (LICENSE, CITATION.cff, pyproject.toml) before v0.1.6-publication-freeze tag.

## Files changed

- `LICENSE` (new), `CITATION.cff`, `pyproject.toml`
- `README.md`, docs: `project_status.md`, `roadmap.md`, `reproducibility_commands.md`, `phase5h_publication_readiness_freeze.md`, `pre_submission_checklist.md`, `cursor_work_log.md`

## Tests run

- `python3 -m pytest -q` — 264 passed

## Notes

- Metadata-only; no benchmark rerun or frozen output changes.
- Ready to tag `v0.1.6-publication-freeze`.

---

## Date/time

Wednesday, May 29, 2026 (UTC-7)

## Prompt summary

Phase 5H-A: publication readiness freeze audit after Phase 5G (release stack, claims, artifacts, blockers).

## Files changed

- `docs/phase5h_publication_readiness_freeze.md` (new)
- `README.md`, `docs/project_status.md`, `docs/roadmap.md`, `docs/reproducibility_commands.md`, `docs/pre_submission_checklist.md`, `docs/cursor_work_log.md`

## Tests run

- `python3 -m pytest -q` — 264 passed

## Notes

- Verdict: **ready with minor metadata blockers** (LICENSE, CITATION.cff version).
- No benchmark rerun; no frozen outputs modified.

---

## Date/time

Wednesday, May 29, 2026 (UTC-7)

## Prompt summary

Phase 5G-D: final notation QA after v0.1.4-internal-kg-rename (grep audit, claim boundaries, tests).

## Files changed

- `docs/phase5g_final_notation_qa.md` (new)
- `docs/project_status.md`, `docs/roadmap.md`, `docs/reproducibility_commands.md`, `docs/cursor_work_log.md`

## Tests run

- `python3 -m pytest -q` — 264 passed

## Notes

- QA verdict: **PASS**; zero confusing/needs-fix legacy references.
- Phase 5G notation migration marked **complete**.
- No code, frozen outputs, or figures modified.

---

## Date/time

Wednesday, May 29, 2026 (UTC-7)

## Prompt summary

Phase 5G-C-B: internal k_g rename with legacy k_tau property and keyword aliases.

## Files changed

- `src/tdf_galaxy_tau/reconstruction/radial_tau.py`, `models/tdf_knot.py`, `models/fitting.py`
- `validation/tdf_holdout_runner.py`, `validation/holdout_residuals.py`
- `config/notation.py` — `resolve_projection_coefficient_kwarg`
- `analysis/ktau_sensitivity.py`, `analysis/ml_sensitivity.py` — holdout export call sites
- `scripts/expansion_pipeline.py`, `compare_sparc_models.py`, `fit_sparc_tdf_knot_model.py`, etc.
- `tests/test_phase5g_internal_kg_rename.py` + updated notation/radial tests
- docs: `project_status.md`, `roadmap.md`, `reproducibility_commands.md`, `ktau_sensitivity.md`

## Tests run

- `python3 -m pytest -q` — 264 passed

## Notes

- Frozen CSV column `K_tau` unchanged; no benchmark rerun; no outputs/tables rewrite.
- Deprecated `k_tau=` kwarg on velocity/fit functions emits DeprecationWarning.

---

## Date/time

Wednesday, May 29, 2026 (UTC-7)

## Prompt summary

Phase 5G-C-A: internal K_g rename audit (read-only); classify remaining k_tau / K_tau references for 5G-C-B.

## Files changed

- `docs/phase5g_internal_rename_audit.md` (new)
- `docs/project_status.md`, `docs/roadmap.md`, `docs/cursor_work_log.md`

## Tests run

- `python3 -m pytest -q`

## Notes

- No code, dataclass, benchmark, or frozen output changes.
- Audit: ~52 internal_projection_candidate, ~350+ sensitivity_sweep_legacy_axis, frozen CSV columns must stay `K_tau`.
- Next: Phase 5G-C-B dataclass rename + `.k_tau` property alias per audit.

---

## Date/time

Wednesday, May 29, 2026 (UTC-7)

## Prompt summary

Phase 5G-B status synchronization: align `project_status.md` with completed regression lock.

## Files changed

- `docs/project_status.md`, `docs/roadmap.md`, `docs/cursor_work_log.md`
- `docs/reproducibility_commands.md`, `docs/ktau_sensitivity.md`, `README.md`

## Notes

- Documentation-only; no code, tests, or frozen outputs modified.
- Recommended next tag: `v0.1.3-notation-compatibility`.

---

## Date/time

Wednesday, May 29, 2026 (UTC-7)

## Prompt summary

Phase 5G-B: compatibility regression tests locking k_g ≡ legacy k_tau loader equivalence.

## Files changed (Phase 5G-B)

- `tests/test_notation_compatibility_regression.py`
- `tests/fixtures/notation/reconstruction_k_g.yaml`, `reconstruction_k_tau_legacy.yaml`
- `docs/project_status.md`, `docs/roadmap.md`, `docs/ktau_sensitivity.md`, `docs/reproducibility_commands.md`

## Tests run (Phase 5G-B)

- `python3 -m pytest -q`

## Notes

- No frozen outputs modified; no expansion20 rerun.
- Internal dataclass fields still named `k_tau`.

---

## Date/time

Wednesday, May 29, 2026 (UTC-7)

## Prompt summary

Phase 5G-A: backward-compatible K_g / legacy K_tau projection coefficient alias layer (no benchmark rerun).

## Files changed (Phase 5G-A)

- `src/tdf_galaxy_tau/config/notation.py`, `src/tdf_galaxy_tau/config/__init__.py`
- `src/tdf_galaxy_tau/reconstruction/radial_tau.py` — `load_reconstruction_config`
- `src/tdf_galaxy_tau/models/tdf_knot.py` — `load_tdf_knot_config`
- `tests/test_notation_aliases.py`
- `docs/project_status.md`, `docs/roadmap.md`, `docs/ktau_sensitivity.md`, `docs/reproducibility_commands.md`

## Tests run (Phase 5G-A)

- `python3 -m pytest -q`

## Notes

- Frozen CSV columns and `outputs/tables/*` not modified.
- `kappa_tau` rejected if used alone as projection key.

---

## Date/time

Wednesday, May 27, 2026 (UTC-7)

## Prompt summary

Phase 5F-F: final polish, stale-reference cleanup, pre-submission QA (no new fits).

## Files changed (Phase 5F-F)

- `src/tdf_galaxy_tau/analysis/manuscript_text.py`
- `src/tdf_galaxy_tau/analysis/paper_tables.py`
- `src/tdf_galaxy_tau/analysis/pre_submission_qa.py`
- `paper/manuscript.tex`, `paper/tables/table6_assumptions_limitations.tex`, `paper/manuscript.pdf`
- `docs/pre_submission_checklist.md`
- `outputs/reports/paper_pre_submission_qa_report.md`
- `tests/test_pre_submission_qa.py`

## Tests run (Phase 5F-F)

- `python3 scripts/compile_paper_pdf.py` (via QA module)
- `python3 -m pytest -q` → **220 passed**

---

## Prompt summary

Phase 5F-E: referee critique, equation formalization, descriptive statistics (no new fits).

## Files changed (Phase 5F-E)

- `src/tdf_galaxy_tau/analysis/reviewer_analysis.py`
- `src/tdf_galaxy_tau/analysis/manuscript_text.py`
- `scripts/build_referee_readiness_report.py`
- `docs/reviewer_objection_matrix.md`
- `outputs/tables/paper_statistical_summary.csv`
- `outputs/reports/paper_referee_readiness_report.md`
- `paper/manuscript.tex`, `paper/references.bib`, `paper/manuscript.pdf`
- `tests/test_referee_readiness.py`

## Tests run (Phase 5F-E)

- `python3 scripts/build_referee_readiness_report.py`
- `python3 -m pytest -q` → **212 passed**

---

## Prompt summary

Phase 5F-D: scientific editing, LaTeX cleanup, figure order, bibliography (no new fits).

## Files changed (Phase 5F-D)

- `src/tdf_galaxy_tau/analysis/manuscript_text.py`
- `src/tdf_galaxy_tau/analysis/paper_tables.py`
- `paper/manuscript.tex`, `paper/references.bib`, `paper/tables/*.tex`
- `outputs/reports/paper_scientific_edit_report.md`
- `tests/test_paper_layout.py`, `tests/test_manuscript_claims.py`
- `paper/README.md`, `docs/project_status.md`

## Tests run (Phase 5F-D)

- `python3 scripts/export_paper_tables.py` → `paper/manuscript.pdf`
- `python3 -m pytest -q` → **206 passed**

---

## Prompt summary

Phase 5F-C: export LaTeX tables, draft manuscript prose, compile-check PDF (no new fits).

## Files changed (Phase 5F-C)

- `src/tdf_galaxy_tau/analysis/paper_tables.py`
- `src/tdf_galaxy_tau/analysis/manuscript_text.py`
- `src/tdf_galaxy_tau/analysis/paper_compile.py`
- `scripts/export_paper_tables.py`
- `scripts/compile_paper_pdf.py`
- `paper/manuscript.tex`, `paper/tables/table1_cohort_summary.tex` … `table6_assumptions_limitations.tex`
- `outputs/reports/paper_manuscript_draft_report.md`
- `tests/test_paper_tables.py`, `tests/test_manuscript_claims.py`
- `docs/project_status.md`

## Tests run (Phase 5F-C)

- `python3 scripts/export_paper_tables.py` → `paper/manuscript.pdf` built (latexmk/pdflatex)
- `python3 -m pytest -q` → **200 passed**

---

## Prompt summary

Phase 5F-B: compose publication figures and freeze paper assets (no new fits).

## Files changed (Phase 5F-B)

- `src/tdf_galaxy_tau/analysis/paper_figures.py`
- `scripts/build_paper_figures.py`
- `paper/figures/fig1_benchmark_workflow.png` … `fig7_claim_boundary_map.png`
- `paper/manuscript.tex` (includegraphics references)
- `paper/README.md`
- `outputs/reports/paper_figures_report.md`
- `docs/project_status.md`
- `tests/test_paper_figures.py`

## Tests run (Phase 5F-B)

- `python3 scripts/build_paper_figures.py`
- `python3 -m pytest -q` → **190 passed** in ~109s

---

## Prompt summary

Phase 5F-A: publication manuscript scaffold and frozen figure/table inventory (no new fits).

## Files changed (Phase 5F-A)

- `src/tdf_galaxy_tau/analysis/paper_package.py`
- `scripts/build_paper_package_scaffold.py`
- `paper/manuscript.tex`, `paper/references.bib`, `paper/README.md`, `paper/figures/`, `paper/tables/`
- `docs/paper_outline.md`
- `docs/project_status.md`
- `outputs/tables/paper_figure_inventory.csv`
- `outputs/tables/paper_table_inventory.csv`
- `outputs/reports/paper_package_scaffold_report.md`
- `tests/test_paper_package.py`

## Tests run (Phase 5F-A)

- `python3 scripts/build_paper_package_scaffold.py`
- `python3 -m pytest -q` → **186 passed** in ~107s

---

## Prompt summary

Phase 5E: controlled expansion final audit (5B–5D consolidation).

## Files changed (Phase 5E)

- `src/tdf_galaxy_tau/analysis/controlled_expansion_audit.py`
- `scripts/build_controlled_expansion_final_audit.py`
- `docs/controlled_expansion_results.md`
- `docs/paper_ready_claims.md`
- `outputs/tables/controlled_expansion_comparison_summary.csv`
- `outputs/tables/controlled_expansion_final_claims.csv`
- `outputs/reports/controlled_expansion20_final_audit_report.md`
- `tests/test_controlled_expansion_final_audit.py`

## Tests run (Phase 5E)

- `python3 scripts/build_controlled_expansion_final_audit.py`
- `python3 -m pytest -q` → **179 passed** in ~111s

---

## Prompt summary

Phase 5D: expansion_20 non-robust case audit (5 galaxies).

## Files changed (Phase 5D)

- `src/tdf_galaxy_tau/analysis/expansion20_diagnostics.py`
- `scripts/analyze_expansion20_failure_modes.py`
- `docs/expansion20_failure_mode_analysis.md`
- `outputs/tables/expansion20_failure_diagnostics.csv`
- `outputs/tables/expansion20_case_review_summary.csv`
- `outputs/reports/expansion20_failure_mode_analysis_report.md`
- `outputs/figures/sparc_subset/expansion20_*.png`
- `tests/test_expansion20_failure_diagnostics.py`

## Tests run (Phase 5D)

- `python3 scripts/analyze_expansion20_failure_modes.py` → UGC12506=NGC5055_style_knot_flexibility
- `python3 -m pytest -q` → **173 passed** in ~108s

---

## Prompt summary

Phase 5C: expansion_20 controlled benchmark (20 galaxies).

## Files changed (Phase 5C)

- `src/tdf_galaxy_tau/scripts/expansion_pipeline.py` (expansion_20 + classification)
- `scripts/run_expansion20_pipeline.py`
- `docs/expansion20_results.md`
- `outputs/tables/expansion20_*.csv`
- `outputs/reports/expansion20_benchmark_report.md`
- `tests/test_expansion20_pipeline.py`

## Tests run (Phase 5C)

- `python3 scripts/run_expansion20_pipeline.py` → robust=15, sensitivity_recovery=3, failure=1, mixed=1
- `python3 -m pytest -q` → **168 passed** in ~107s

---

## Prompt summary

Phase 5B-R: radial holdout residual maps for NGC5055 and UGC05253 (flex-recovery).

## Files changed (Phase 5B-R)

- `src/tdf_galaxy_tau/analysis/expansion12_radial_maps.py`
- `scripts/analyze_expansion12_radial_residual_maps.py`
- `docs/expansion12_radial_residual_maps.md`
- `outputs/tables/expansion12_holdout_point_residuals.csv`
- `outputs/tables/expansion12_radial_failure_map_summary.csv`
- `outputs/reports/expansion12_radial_residual_map_report.md`
- `outputs/figures/sparc_subset/ngc5055_radial_holdout_residuals.png`
- `outputs/figures/sparc_subset/ugc05253_radial_holdout_residuals.png`
- `outputs/figures/sparc_subset/expansion12_flex_recovery_radial_comparison.png`
- `tests/test_expansion12_radial_maps.py`

## Tests run (Phase 5B-R)

- `python3 scripts/analyze_expansion12_radial_residual_maps.py` → 736 point rows, 84 summary rows
- `python3 -m pytest -q` → **162 passed** in ~100s

---

## Prompt summary

Phase 5B-Audit: expansion_12 failure/mixed-case diagnostics (4 galaxies; no new fits).

## Files changed (Phase 5B-Audit)

- `src/tdf_galaxy_tau/analysis/expansion12_diagnostics.py`
- `scripts/analyze_expansion12_failure_modes.py`
- `docs/expansion12_failure_mode_analysis.md`
- `outputs/tables/expansion12_failure_diagnostics.csv`
- `outputs/tables/expansion12_case_review_summary.csv`
- `outputs/reports/expansion12_failure_mode_analysis_report.md`
- `outputs/figures/sparc_subset/expansion12_*.png`
- `tests/test_expansion12_failure_diagnostics.py`

## Tests run (Phase 5B-Audit)

- `python3 -m pytest -q`
- `python3 scripts/analyze_expansion12_failure_modes.py`

---

## Prompt summary

Phase 5B: run expansion_12 controlled benchmark (12 galaxies).

## Files changed (Phase 5B)

- `src/tdf_galaxy_tau/scripts/expansion_pipeline.py`
- `scripts/run_expansion12_pipeline.py`
- `docs/expansion12_results.md`
- `outputs/tables/expansion12_*.csv`
- `outputs/reports/expansion12_benchmark_report.md`
- `tests/test_expansion12_pipeline.py`

## Tests run (Phase 5B)

- `python3 -m pytest -q` → **151 passed** in ~96s
- `python3 scripts/run_expansion12_pipeline.py` → success (12 galaxies; robust=8, failure=2, mixed=2)

## Fixes during 5B

- `fit_rar_fixed`: use `g_dagger_ms2` (not `g_dagger_m_s2`)
- `knot_count_stability_table` before `build_robust_best_model_summary` (empty DataFrame broke on `galaxy_id`)

---

## Prompt summary

Phase 5A: pre-register controlled SPARC subset expansion criteria (no fits).

## Files changed (Phase 5A)

- `configs/subset_expansion.yaml`
- `src/tdf_galaxy_tau/data/subset_expansion.py`
- `scripts/plan_sparc_subset_expansion.py`
- `docs/subset_expansion_protocol.md`
- `outputs/tables/sparc_subset_expansion_candidates.csv`
- `outputs/tables/sparc_subset_expansion_plan.csv`
- `outputs/reports/sparc_subset_expansion_protocol_report.md`
- `tests/test_subset_expansion.py`

## Tests run (Phase 5A)

- `python3 -m pytest -q`
- `python3 scripts/plan_sparc_subset_expansion.py`

---

## Prompt summary

Phase 4M: final controlled-subset audit package (documentation only; no new fits).

## Files changed (Phase 4M)

- `src/tdf_galaxy_tau/analysis/controlled_subset_audit.py`
- `scripts/build_controlled_subset_final_audit.py`
- `docs/controlled_subset_audit.md`
- `outputs/reports/sparc_controlled_subset_final_audit_report.md`
- `outputs/tables/sparc_controlled_subset_final_claims.csv`
- `outputs/tables/sparc_controlled_subset_final_status.csv`
- `tests/test_controlled_subset_audit.py`

## Tests run (Phase 4M)

- `python3 -m pytest -q`
- `python3 scripts/build_controlled_subset_final_audit.py`

---

## Prompt summary

Phase 4L: K_tau sensitivity on photometry-informed fair-scaled M/L harness (TDF amplitude refit only).

## Files changed (Phase 4L)

- `src/tdf_galaxy_tau/analysis/ktau_sensitivity.py`
- `scripts/run_photometry_prior_ktau_sensitivity.py`
- `configs/reconstruction.yaml` (`photometry_prior_ktau_sensitivity`)
- `docs/ktau_sensitivity.md`
- `tests/test_ktau_sensitivity.py`
- `outputs/tables/sparc_ktau_sensitivity_summary.csv`
- `outputs/tables/ngc7814_ktau_sensitivity.csv`
- `outputs/reports/sparc_ktau_sensitivity_report.md`

## Tests run (Phase 4L)

- `python3 -m pytest -q`
- `python3 scripts/run_photometry_prior_ktau_sensitivity.py`

---

## Prompt summary

Phase 4K: photometry-informed M/L prior construction and re-weighted diagnostic interpretation (no new fits).

## Files changed (Phase 4K)

- `src/tdf_galaxy_tau/analysis/photometry_informed_priors.py`
- `scripts/build_photometry_informed_ml_priors.py`
- `scripts/apply_photometry_informed_prior_weighting.py`
- `configs/ml_priors.yaml` (photometry_informed_scenarios)
- `docs/photometry_informed_ml_priors.md`, `docs/ml_prior_framework.md`, `docs/ngc7814_failure_mode.md`, `docs/paper_ready_claims.md`
- `outputs/tables/sparc_photometry_informed_prior_weights.csv`
- `outputs/tables/sparc_photometry_prior_weighted_summary.csv`
- `outputs/tables/ngc7814_photometry_prior_interpretation.csv`
- `outputs/reports/sparc_photometry_informed_prior_report.md`
- `tests/test_photometry_informed_priors.py`

## Tests run (Phase 4K)

- `python3 -m pytest -q`
- `python3 scripts/build_photometry_informed_ml_priors.py`
- `python3 scripts/apply_photometry_informed_prior_weighting.py`

---

## Prompt summary

Phase 4J: ingest SPARC photometry metadata for future M/L priors (no new fits).

## Files changed (Phase 4J)

- `src/tdf_galaxy_tau/data/sparc_photometry_parser.py`
- `src/tdf_galaxy_tau/data/sparc_metadata_join.py`
- `scripts/ingest_sparc_photometry_metadata.py`
- `tests/test_sparc_photometry_parser.py`, `tests/test_sparc_metadata_join.py`
- `data/processed/sparc/sparc_photometry_metadata.csv`
- `outputs/tables/sparc_photometry_metadata_summary.csv`
- `outputs/tables/sparc_subset_photometry_context.csv`
- `outputs/reports/sparc_photometry_metadata_ingestion_report.md`

## Tests run (Phase 4J)

- `python3 -m pytest -q`
- `python3 scripts/ingest_sparc_photometry_metadata.py`

---

## Prompt summary

Phase 4I-Audit: verify prior weights; fix NGC7814 layered interpretation; regen 4I outputs.

## Files changed (Phase 4I-Audit)

- `src/tdf_galaxy_tau/analysis/ml_priors.py` (layered interpretation, audit builders)
- `scripts/audit_ml_prior_weighting.py`, `tests/test_ml_prior_weighting_audit.py`
- Regenerated `sparc_ml_prior_weighted_summary.csv`, `ngc7814_ml_prior_weighted_interpretation.csv`

## Tests run (Phase 4I-Audit)

- `python3 -m pytest -q`
- `python3 scripts/audit_ml_prior_weighting.py`

---

## Prompt summary (prior)

Phase 4I: diagnostic M/L prior scaffold and prior-weighted summary (no new fits).

## Files changed (Phase 4I)

- `configs/ml_priors.yaml`, `src/tdf_galaxy_tau/analysis/ml_priors.py`
- `scripts/apply_ml_prior_weighting.py`, `tests/test_ml_priors.py`
- `docs/ml_prior_framework.md`, claim O in `docs/paper_ready_claims.md`

## Tests run (Phase 4I)

- `python3 -m pytest -q`
- `python3 scripts/apply_ml_prior_weighting.py`

---

## Prompt summary (prior)

Phase 4H: post-M/L claim reconciliation (documentation only; claims I–N).

## Files changed (Phase 4H)

- `src/tdf_galaxy_tau/analysis/post_ml_claim_reconciliation.py`
- `scripts/run_post_ml_claim_reconciliation.py`
- `tests/test_post_ml_claim_reconciliation.py`
- `docs/paper_ready_claims.md`, `docs/results_summary.md`, `docs/ngc7814_failure_mode.md`
- `outputs/tables/sparc_claim_traceability_matrix_updated.csv`
- `outputs/tables/sparc_post_ml_results_summary_table.csv`
- `outputs/reports/sparc_post_ml_claim_reconciliation_report.md`
- `outputs/reports/sparc_post_ml_controlled_subset_results_summary.md`

## Tests run (Phase 4H)

- `python3 -m pytest -q`

---

## Prompt summary (prior)

Phase 4G: fair M/L-scaled TDF/NFW/MOND holdout comparison on six-galaxy subset.

## Files changed (Phase 4G)

- `src/tdf_galaxy_tau/analysis/ml_scaled_baseline_comparison.py`
- `scripts/run_sparc_ml_scaled_baseline_comparison.py`
- `tests/test_ml_scaled_baseline_comparison.py`, `docs/ml_scaled_baseline_comparison.md`

## Tests run (Phase 4G)

- `python3 -m pytest -q`
- `python3 scripts/run_sparc_ml_scaled_baseline_comparison.py`

---

## Prompt summary (prior)

Phase 4F: diagnostic M/L sensitivity audit (disk/bulge scaling grid).

## Files changed (Phase 4F)

- `src/tdf_galaxy_tau/analysis/ml_sensitivity.py`
- `src/tdf_galaxy_tau/validation/holdout.py` (radial region helpers)
- `scripts/run_sparc_ml_sensitivity_audit.py`
- `tests/test_ml_sensitivity.py`, `docs/ml_sensitivity_audit.md`

## Tests run (Phase 4F)

- `python3 -m pytest -q` — 100 passed
- `python3 scripts/run_sparc_ml_sensitivity_audit.py` — 240 summary rows

---

## Prompt summary (prior)

Phase 4E: per-point holdout residual archive and radial failure-map diagnostics.

## Files changed (Phase 4E)

- `src/tdf_galaxy_tau/validation/holdout.py`, `holdout_residuals.py`, `tdf_holdout_runner.py`
- `src/tdf_galaxy_tau/analysis/radial_holdout_maps.py`
- `scripts/export_sparc_holdout_residuals.py`, `scripts/analyze_radial_holdout_failure_maps.py`
- `tests/test_holdout_point_residuals.py`, `tests/test_radial_failure_maps.py`
- docs updates

## Tests run (Phase 4E)

- `python3 -m pytest -q` — 95 passed
- `python3 scripts/export_sparc_holdout_residuals.py` — 1488 rows
- `python3 scripts/analyze_radial_holdout_failure_maps.py`

---

## Prompt summary (prior)

Phase 4D: NGC7814 failure-mode diagnostic deep-dive (baryonic/residual/holdout/pattern; no new fits).

## Files changed (Phase 4D)

- `src/tdf_galaxy_tau/analysis/ngc7814_diagnostics.py` (new)
- `scripts/analyze_ngc7814_failure_mode.py` (new)
- `tests/test_ngc7814_failure_diagnostics.py` (new)
- `docs/ngc7814_failure_mode.md` (new)
- `docs/project_status.md`, `docs/cursor_work_log.md`, `docs/limitations.md`, `docs/assumptions.md`

## Tests run (Phase 4D)

- `python3 -m pytest -q`
- `python3 scripts/analyze_ngc7814_failure_mode.py`

## Outputs generated (Phase 4D)

- `outputs/tables/ngc7814_failure_diagnostics.csv`
- `outputs/tables/ngc7814_vs_success_group_diagnostics.csv`
- `outputs/reports/ngc7814_failure_mode_report.md`
- `outputs/figures/sparc_subset/ngc7814_*.png` (4 figures)

## Next action recommended by Cursor (Phase 4D)

K_tau or M/L sensitivity with claim-matrix update; optional holdout residual archival for radial maps.

---

## Prompt summary (prior)

Phase 4C: normalized τ-pattern discovery across six-galaxy subset (exploratory analysis; Phase 2A profiles; no new fits).

## Files changed (Phase 4C)

- `src/tdf_galaxy_tau/analysis/normalized_patterns.py` (new)
- `src/tdf_galaxy_tau/analysis/__init__.py` (new)
- `scripts/analyze_normalized_tau_patterns.py` (new)
- `tests/test_normalized_tau_patterns.py` (new)
- `docs/normalized_tau_patterns.md` (new)
- `docs/project_status.md`, `docs/cursor_work_log.md`, `docs/limitations.md`, `docs/assumptions.md`

## Tests run (Phase 4C)

- `python3 -m pytest -q`
- `python3 scripts/analyze_normalized_tau_patterns.py`

## Outputs generated (Phase 4C)

- `outputs/tables/sparc_normalized_tau_patterns.csv`
- `outputs/tables/sparc_tau_pattern_similarity_matrix.csv`
- `outputs/tables/sparc_tau_pattern_outlier_scores.csv`
- `outputs/reports/sparc_normalized_tau_pattern_report.md`
- `outputs/figures/sparc_subset/normalized_tau_gradient_overlay.png`
- `outputs/figures/sparc_subset/normalized_missing_acceleration_overlay.png`
- `outputs/figures/sparc_subset/tau_pattern_similarity_heatmap.png`

## Next action recommended by Cursor (Phase 4C)

NGC7814 structural diagnostic or K_tau/M/L sensitivity with updated claim matrix before subset expansion.

---

## Prompt summary (prior)

Phase 4B: publication-style controlled-subset results summary, publication table, and paper-ready claim guardrail (documentation only; no new fits).

## Files changed (Phase 4B)

- `docs/results_summary.md` (new)
- `docs/paper_ready_claims.md` (new)
- `outputs/reports/sparc_controlled_subset_results_summary.md` (new)
- `outputs/tables/sparc_publication_summary_table.csv` (new)
- `docs/project_status.md`
- `docs/cursor_work_log.md`
- `docs/limitations.md`

## Tests run (Phase 4B)

- `python3 -m pytest -q` — all passed

## Outputs generated (Phase 4B)

- `outputs/tables/sparc_publication_summary_table.csv`
- `outputs/reports/sparc_controlled_subset_results_summary.md`

## Issues encountered (Phase 4B)

- None (read-only aggregation from Phase 4A tables).

## Next action recommended by Cursor (Phase 4B)

NGC7814 diagnostic work or controlled subset expansion only with updated holdout audit and claim matrix.

---

## Date/time (prior)

Wednesday, May 27, 2026 (UTC-7)

## Prompt summary (prior)

Phase 4A: failure-mode classification and claim traceability matrix (NGC7814 holdout failure documented).

## Files changed

- `src/tdf_galaxy_tau/models/fitting.py`
- `src/tdf_galaxy_tau/metrics/comparison.py`
- `scripts/audit_sparc_baseline_fits.py`
- `configs/models.yaml`
- `docs/project_status.md`
- `docs/cursor_work_log.md`
- `docs/assumptions.md`
- `docs/limitations.md`
- `tests/test_sparc_baseline_fit_audit.py`

## Tests run

- `python3 -m pytest -q`
- `python3 scripts/audit_sparc_baseline_fits.py --comparison outputs/tables/sparc_baseline_model_comparison.csv --parameters outputs/tables/sparc_baseline_fit_parameters.csv --config configs/models.yaml`

## Outputs generated

- `outputs/tables/sparc_baseline_fit_audit.csv`
- `outputs/reports/sparc_baseline_fit_audit_report.md`

## Issues encountered

- No formula/unit bugs identified in NFW/Burkert implementations during audit.
- Burkert `rho_0` consistently at lower search bound; NFW sometimes at `r_s` upper or `rho_s` lower bound.

## Next action recommended by Cursor

Proceed to Phase 3B TDF knot model only after documenting baseline caveats in comparison reports; consider wider `rho_0` bounds in a future refit phase if scientifically justified.
