# Project Status

## Current phase

**Phase 5F-F — pre-submission polish and QA**

## Completed tasks

- Phase 1A: SPARC raw rotmod ingestion and standardization.
- Phase 1B: deterministic subset selection and QC reporting.
- Phase 2A: per-galaxy radial τ reconstruction from rotation residuals for selected galaxies.
- Phase 3A: fitted baryonic-only, NFW, and Burkert baselines (legacy linear bounds).
- Phase 3A-Audit: boundary and high-chi-square flags on legacy baselines.
- Phase 3A-R: log-space multistart NFW/Burkert refit with wider documented bounds; legacy outputs preserved.
- Phase 3M: MOND/RAR baselines (fixed and fitted a0, optional RAR) on six-galaxy subset; combined comparison with halo refit.
- Phase 3B: TDF 3/4/5-knot fitted models with AIC/BIC comparison vs halo refit and MOND.
- Phase 3C: holdout validation, K_tau/bounds sensitivity, knot-count stability, smoothness diagnostics.
- Phase 4A: per-galaxy failure-mode classification and claim traceability matrix (A–H).
- Phase 4B: paper-ready results summary, publication table, and conservative claim language (`docs/results_summary.md`, `docs/paper_ready_claims.md`).
- Phase 4C: normalized τ-pattern similarity, outlier scores, overlays (`docs/normalized_tau_patterns.md`, `scripts/analyze_normalized_tau_patterns.py`).
- Phase 4D: NGC7814 structural/holdout/pattern diagnostics (`docs/ngc7814_failure_mode.md`, `scripts/analyze_ngc7814_failure_mode.py`).
- Phase 4E: per-point holdout residual CSV and radial failure-map figures/reports (`scripts/export_sparc_holdout_residuals.py`).
- Phase 4F: diagnostic disk/bulge M/L scaling grid and holdout sensitivity (`docs/ml_sensitivity_audit.md`).
- Phase 4G: fair scaled-baseline refit (TDF + NFW + MOND) on same M/L grid (`docs/ml_scaled_baseline_comparison.md`).
- Phase 4H: claim matrix I–N, post-M/L summary tables/reports, updated `docs/paper_ready_claims.md` (no new fits).
- Phase 4I: diagnostic prior scaffold on Phase 4G outputs (`configs/ml_priors.yaml`, `docs/ml_prior_framework.md`).
- Phase 4I-Audit: prior weight verification, NGC7814 layered interpretation, Phase 4I table regen (`scripts/audit_ml_prior_weighting.py`).
- Phase 4J: SPARC photometry metadata ingestion (175 galaxies; subset context for six galaxies).
- Phase 4K: photometry-informed diagnostic prior weights and re-weighted interpretation (`docs/photometry_informed_ml_priors.md`).
- Phase 4L: K_tau sensitivity audit on Phase 4K harness (`docs/ktau_sensitivity.md`).
- Phase 4M: final controlled-subset audit package (`docs/controlled_subset_audit.md`; no new fits).
- Phase 5A: pre-registered expansion protocol for cohorts of 12 and 20 galaxies (`docs/subset_expansion_protocol.md`; no fits).
- Phase 5B: expansion_12 full benchmark pipeline (`docs/expansion12_results.md`; 12 galaxies).
- Phase 5B-Audit: failure/mixed diagnostics for NGC7814, NGC5055, UGC00128, UGC05253 (`docs/expansion12_failure_mode_analysis.md`; no new fits).
- Phase 5B-R: radial holdout residual maps for NGC5055, UGC05253 flex-recovery (`docs/expansion12_radial_residual_maps.md`; diagnostic refit only).
- Phase 5C: expansion_20 controlled benchmark (`docs/expansion20_results.md`; 20 galaxies; sensitivity_recovery class).
- Phase 5D: expansion_20 failure/mixed/sensitivity audit (`docs/expansion20_failure_mode_analysis.md`; 5 non-robust galaxies).
- Phase 5E: expansion_12 vs expansion_20 final audit package (`docs/controlled_expansion_results.md`; claims C20-A–H).
- Phase 5F-A: paper package scaffold (`paper/manuscript.tex`, figure/table inventories; no new fits).
- Phase 5F-B: composed paper figures in `paper/figures/` (`scripts/build_paper_figures.py`; no new fits).
- Phase 5F-C: LaTeX tables, first-draft manuscript prose, PDF compile (`scripts/export_paper_tables.py`; no new fits).
- Phase 5F-D: scientific edit, figure/table layout, bibliography (`scripts/export_paper_tables.py`; no new fits).
- Phase 5F-E: equations, descriptive stats, reviewer matrix (`scripts/build_referee_readiness_report.py`; no new fits).
- Phase 5F-F: final polish, Table 6 assumptions, pre-submission QA (`docs/pre_submission_checklist.md`; no new fits).

## Current blockers
- Halo degeneracy and high reduced chi-square may persist after refit.

## Next recommended tasks

1. Author review of `paper/manuscript.pdf`; optional prose polish and journal formatting.
2. Optional blocked-holdout for UGC12506.
2. Explicit bulge L_3.6 or stellar-population priors before calibrated M/L language.
3. Full SPARC and lensing deferred per claim boundaries.

## Latest validation/test results

- `python3 -m pytest -q`
- `python3 scripts/fit_sparc_baselines.py ... --mode refit`
- `python3 scripts/audit_sparc_baseline_fits.py ... --out outputs/tables/sparc_baseline_fit_audit_refit.csv`

## Claim boundary

Phases 4A–4M: use `docs/controlled_subset_audit.md`, `docs/paper_ready_claims.md`, and `outputs/reports/sparc_controlled_subset_final_audit_report.md`. Subset-only; 5/6 holdout success; NGC7814 canonical tdf_3knot failure; tdf_5knot sensitivity-only; no lensing; no final M/L calibration.
