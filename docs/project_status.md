# Project Status

## Current phase

**Phase 5G-B — K_g / legacy K_tau compatibility regression lock** — **complete**

Supporting notation steps (also complete):

- **Phase 5G-A — notation alias layer (K_g / legacy K_tau)**
- **Phase 5E/5F — controlled expansion-20 publication package and scientific consistency audit**

Publication package (manuscript PDF, paper figures/tables, reviewer matrix, pre-submission QA) is complete. Phase **5G-A** added a backward-compatible config alias layer: **`k_g` / `K_g`** (preferred projection coefficient) and legacy **`k_tau` / `K_tau`** (same role). Phase **5G-B** regression-locks loader-level equivalence before any internal rename. **`kappa_tau` / κ_tau** is field stiffness only and is never mapped to projection. Frozen benchmark outputs and CSV column names unchanged.

### Phase 5G-B deliverables

- `tests/test_notation_compatibility_regression.py` — loader-level equivalence lock (255 tests total in suite)
- `tests/fixtures/notation/reconstruction_k_g.yaml` and `reconstruction_k_tau_legacy.yaml`
- Loader-level equivalence proven for **`k_g` / `K_g`** and legacy **`k_tau` / `K_tau`**
- No benchmark rerun; no frozen output changes; no internal dataclass field rename yet

### Phase 5G-A deliverables

- `src/tdf_galaxy_tau/config/notation.py` — `normalize_projection_coefficient`, `merge_projection_from_yaml_blocks`
- `load_reconstruction_config` and `load_tdf_knot_config` use the alias layer
- `tests/test_notation_aliases.py`

### expansion_20 headline (frozen)

In the pre-registered controlled **expansion_20** cohort:

- **Primary `tdf_3knot` robust holdout success:** 15 of 20 galaxies  
- **`tdf_5knot` sensitivity-recovery:** 3 galaxies (not primary success)  
- **All-TDF holdout failure:** NGC7814 (canonical)  
- **Mixed near-tie:** UGC00128  

Authoritative claims: `docs/paper_ready_claims.md` (C20-A–C20-H), `docs/controlled_expansion_results.md`, `outputs/tables/controlled_expansion_final_claims.csv`.

### Notation (Phase 5G-A / 5G-B complete; 5G-C planned)

| Symbol | Role |
| --- | --- |
| **K_g** | Gravitational **projection coefficient** (preferred notation; radial closure \(v_\tau^2 = r K_g \, d\tau/dr\)). |
| **κ_tau** | **Dynamical stiffness** in the mother field equation; **not** interchangeable with \(K_g\). |
| **K_tau** (legacy) | Historical benchmark/config label and frozen CSV column name for the projection coefficient. |

See `docs/theory_summary.md` and `docs/roadmap.md` (Phase **5G-C** internal rename planned).

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
- Phase 5G-B: compatibility regression lock (`tests/test_notation_compatibility_regression.py`; commits `863e153`, `74f92b6`).
- Release prep: repository cleanup audit, Git tag `v0.1.0-expansion20-paper`, Zenodo preprint DOI [10.5281/zenodo.20437254](https://doi.org/10.5281/zenodo.20437254).

## Current blockers

- Halo degeneracy and high reduced chi-square may persist after refit.
- Root `LICENSE` file not yet added (MIT declared in `pyproject.toml` / `CITATION.cff`).

## Next recommended tasks

1. **Phase 5G-C:** optional internal rename from `k_tau` dataclass fields to `k_g` with backward-compatible `.k_tau` property alias; report-string updates.
2. **Tag `v0.1.3-notation-compatibility`** on `main` after this status sync (points at 5G-B regression lock).
3. Author/journal formatting review of `paper/manuscript.pdf`.
4. Optional blocked-holdout for UGC12506.
5. Explicit bulge L_3.6 or stellar-population priors before calibrated M/L language.
6. Full SPARC and lensing deferred per claim boundaries.

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
