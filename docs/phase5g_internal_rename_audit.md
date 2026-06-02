# Phase 5G-C-A — Internal K_g rename audit (read-only)

**Date:** 2026-05-29  
**Status:** Audit complete; **no code, outputs, or benchmark reruns in this phase.**  
**Prerequisite tags:** `v0.1.2-notation-aliases` (5G-A), `v0.1.3-notation-compatibility` (5G-B)

## Scope statement

This audit inventories remaining **K_tau / k_tau** references (including Unicode **Kτ / kτ** if present — none found) and classifies what may migrate to **K_g / k_g** in **Phase 5G-C-B**. It does **not**:

- modify benchmark numbers, frozen CSV schemas, figures, or `paper/manuscript.pdf`;
- rename frozen CSV column headers in place;
- map **κ_tau / kappa_tau** (field stiffness) to projection;
- imply full-SPARC validation, dark-matter disproof, lensing confirmation, or a universal τ profile.

**Symbol roles (unchanged):**

| Symbol | Role |
| --- | --- |
| **K_g / k_g** | Preferred gravitational **projection coefficient** |
| **K_tau / k_tau** | Legacy benchmark/config/output label for the same projection role |
| **κ_tau / kappa_tau** | Mother-field **stiffness** only — never a projection alias |

---

## 1. Reference inventory and classification

Occurrences below are grouped by **artifact** (not every CSV cell). Scan method: `grep -R 'K_tau\|k_tau\|Kτ\|kτ'` over `configs/`, `src/`, `scripts/`, `tests/`, `docs/`, `paper/`, `outputs/tables/`, `outputs/reports/` on commit `e80eae1`. False positives excluded (`rank_g`, `mock_galaxies`).

### A. Source code — dataclasses and loaders

| Location | Symbol(s) | Classification | Recommendation | Risk |
| --- | --- | --- | --- | --- |
| `src/tdf_galaxy_tau/reconstruction/radial_tau.py` — `TauReconstructionConfig.k_tau` | `k_tau` field | internal_projection_candidate | rename_now_in_5G-C-B → `k_g`; add read-only `.k_tau` property alias | medium |
| `src/tdf_galaxy_tau/models/tdf_knot.py` — `TdfKnotConfig.k_tau` | `k_tau` field | internal_projection_candidate | rename_now_in_5G-C-B → `k_g`; add `.k_tau` property alias | medium |
| `load_reconstruction_config` / `load_tdf_knot_config` — assign `k_tau=float(projection["k_g"])` | `k_tau` | internal_projection_candidate | rename_now_in_5G-C-B → assign `k_g=` after field rename | low |
| `radial_tau.py` — `config.k_tau` in math / validation | `k_tau` | internal_projection_candidate | rename_now_in_5G-C-B → use `config.k_g` (`.k_tau` via property during transition) | low |
| `radial_tau.py` — `PHASE_2A_OUTPUT_COLUMNS` includes `"K_tau"` | `K_tau` | frozen_csv_column | keep_frozen_output_unchanged — writer must still emit column name `K_tau` | high |
| `radial_tau.py` — DataFrame `"K_tau": [config.k_tau]` | `K_tau` | frozen_csv_column | keep_frozen_output_unchanged — values from internal `k_g`, label unchanged | high |
| `tdf_knot.py` — `tdf_velocity_squared_kms2` / `tdf_velocity_kms` param `k_tau` | `k_tau` | internal_projection_candidate | rename_now_in_5G-C-B → param `k_g`; optional deprecated `k_tau=` kw-only alias | medium |
| `models/fitting.py` — `fit_tdf_knot_model(..., k_tau: float)` | `k_tau` | internal_projection_candidate | rename_now_in_5G-C-B → `k_g` param + legacy alias | medium |
| `validation/tdf_holdout_runner.py` — `k_tau` arg; row dict `"K_tau"` | both | internal_projection_candidate + frozen_csv_column | rename param to `k_g`; **keep** CSV key `"K_tau"` | medium |
| `validation/holdout_residuals.py` — `k_tau` arg; `tdf_cfg.k_tau` | `k_tau` | internal_projection_candidate | rename_now_in_5G-C-B | medium |
| `scripts/expansion_pipeline.py` — `tdf_cfg.k_tau`; report strings `fixed K_tau` | both | internal_projection_candidate + update_new_report_label_only | field access → `.k_g`; new report text → `K_g (legacy K_tau)` | low |
| `scripts/compare_sparc_models.py`, `fit_sparc_tdf_knot_model.py`, `reconstruct_sparc_subset_tau.py`, `audit_sparc_tdf_robustness.py` | `k_tau`, `K_tau` | internal_projection_candidate + update_new_report_label_only | rename internal access; label-only in newly generated report headers | low |
| `src/tdf_galaxy_tau/config/notation.py` — legacy keys, `K_tau` in normalized dict | `k_tau`, `K_tau` | config_backward_compatibility | keep_legacy_with_alias — loader must accept legacy YAML keys indefinitely | low |
| `src/tdf_galaxy_tau/config/notation.py` — `kappa_tau` rejection | `kappa_tau` | forbidden_or_confusing | do_not_touch — correct guardrail | high |
| `analysis/ktau_sensitivity.py` — sweep loop `k_tau`, DataFrame `K_tau` column | both | sensitivity_sweep_legacy_axis + frozen_csv_column | keep legacy axis labels in **output** CSVs; internal loop var may rename to `k_g` in 5G-C-B | medium |
| `analysis/*` report builders (`controlled_subset_audit.py`, `failure_modes.py`, `ml_sensitivity.py`, etc.) — prose `K_tau` | `K_tau` | update_new_report_label_only | update_new_report_label_only when reports regenerated; do not rewrite frozen `outputs/reports/` | low |
| `metrics/comparison.py` — caution token `fixed_K_tau` | `K_tau` | frozen_csv_column | keep_frozen_output_unchanged — matches existing CSV caution strings | medium |
| `analysis/pre_submission_qa.py` — checklist string `K_tau fixed` | `K_tau` | update_new_report_label_only | update to `K_g fixed (legacy K_tau)` in 5G-C-B | low |
| `analysis/manuscript_text.py`, `paper_tables.py` | `K_g`, legacy `K_τ` | (already migrated) | do_not_touch — manuscript source already uses K_g | low |
| `tdf_galaxy_tau_benchmark.egg-info/PKG-INFO` | `K_tau` in equations | historical_documentation | update on next package build / regenerate from README | low |

### B. Configuration

| Location | Symbol(s) | Classification | Recommendation | Risk |
| --- | --- | --- | --- | --- |
| `configs/reconstruction.yaml` — top-level `k_tau`, `k_tau_note` | `k_tau` | config_backward_compatibility | keep_legacy_with_alias — production config stays legacy until optional 5G-C-C | low |
| `configs/reconstruction.yaml` — `radial_tau_reconstruction.K_tau`, `tdf_knot.K_tau` | `K_tau` | config_backward_compatibility | keep_legacy_with_alias | low |
| `configs/reconstruction.yaml` — `k_tau_values`, `optional_k_tau_values`, `reference_k_tau` | `k_tau_*` | sensitivity_sweep_legacy_axis | keep_legacy_with_alias; optional alias `k_g_values` in 5G-C-B loader only | medium |
| `tests/fixtures/notation/reconstruction_k_tau_legacy.yaml` | `k_tau`, `K_tau` | test_backward_compatibility | do_not_touch — regression fixture for legacy path | low |
| `tests/fixtures/notation/reconstruction_k_g.yaml` | `k_g` | test_backward_compatibility | do_not_touch | low |

### C. Tests

| Location | Symbol(s) | Classification | Recommendation | Risk |
| --- | --- | --- | --- | --- |
| `tests/test_notation_aliases.py` | `k_tau`, `K_tau`, `k_g` | test_backward_compatibility | keep_legacy_with_alias — extend in 5G-C-B for `.k_tau` property | low |
| `tests/test_notation_compatibility_regression.py` | `k_tau`, `K_tau`, `cfg.k_tau` | test_backward_compatibility | keep and extend — assert `.k_tau == .k_g` after rename | low |
| `tests/test_radial_tau.py`, `test_tdf_knot_model.py`, `test_ktau_sensitivity.py` | `k_tau`, `K_tau` | test_backward_compatibility | update constructors to `k_g=`; keep legacy alias tests | medium |
| `tests/test_pre_submission_qa.py`, `test_referee_readiness.py` | `K_g`, legacy `K_τ` | test_backward_compatibility | do_not_touch unless manuscript strings change | low |

### D. Documentation (historical / explanatory)

| Location | Symbol(s) | Classification | Recommendation | Risk |
| --- | --- | --- | --- | --- |
| `docs/theory_summary.md`, `docs/assumptions.md`, `docs/limitations.md`, `docs/paper_ready_claims.md`, `docs/results_summary.md`, `docs/ktau_sensitivity.md`, `docs/reproducibility_commands.md`, `docs/project_status.md`, `docs/roadmap.md`, README | mixed `K_g` + legacy `K_tau` | historical_documentation | keep_legacy_with_alias in prose explaining frozen outputs; no bulk rewrite required in 5G-C-B | low |
| `docs/cursor_work_log.md` — Phase 4L entries | `K_tau` | historical_documentation | do_not_touch | low |
| `paper/manuscript.tex`, `paper/tables/table6_assumptions_limitations.tex` | `K_g`, legacy `K_τ` | (already migrated) | do_not_touch — no PDF regeneration in 5G-C-B | low |

### E. Frozen outputs — tables (`outputs/tables/`)

| Location | Symbol(s) | Classification | Recommendation | Risk |
| --- | --- | --- | --- | --- |
| Column header `K_tau` in ~20 benchmark CSVs (`expansion20_holdout_validation.csv`, `expansion20_tau_profiles.csv`, `expansion12_*`, `sparc_tdf_holdout_validation.csv`, `sparc_tdf_knot_fit_parameters.csv`, `sparc_subset_tau_profiles.csv`, `tau_profiles/*.csv`, etc.) | `K_tau` | frozen_csv_column | keep_frozen_output_unchanged | high |
| `sparc_ktau_sensitivity_summary.csv` (~298 data rows + header) | `K_tau` | sensitivity_sweep_legacy_axis + frozen_csv_column | keep_frozen_output_unchanged | high |
| `ngc7814_ktau_sensitivity.csv` (~37 rows) | `K_tau` | sensitivity_sweep_legacy_axis + frozen_csv_column | keep_frozen_output_unchanged | high |
| `sparc_best_model_summary.csv` — caution `fixed_K_tau` | `K_tau` | frozen_csv_column | keep_frozen_output_unchanged | high |
| `controlled_expansion_final_claims.csv` — claim text `fixed baryons and K_tau` | `K_tau` | frozen_csv_column | keep_frozen_output_unchanged | high |
| `expansion20_failure_mode_summary.csv` — narrative cells `fixed K_tau` | `K_tau` | frozen_generated_report | keep_frozen_output_unchanged | high |

### F. Frozen outputs — reports (`outputs/reports/`)

| Location | Symbol(s) | Classification | Recommendation | Risk |
| --- | --- | --- | --- | --- |
| `sparc_ktau_sensitivity_report.md` and 12 other `sparc_*_report.md` files | `K_tau` | frozen_generated_report | keep_frozen_output_unchanged — regenerate only under explicit rerun policy | high |
| Report generator source in `src/tdf_galaxy_tau/analysis/*.py` | `K_tau` in f-strings | update_new_report_label_only | prefer `K_g` in **new** generated text; note legacy label for frozen tables | low |

---

## 2. Summary counts by classification

| Classification | Approx. occurrences | Primary locations |
| --- | ---: | --- |
| **internal_projection_candidate** | **~52** | `radial_tau.py`, `tdf_knot.py`, `fitting.py`, holdout runners, scripts calling `tdf_cfg.k_tau` |
| **config_backward_compatibility** | **~25** | `configs/reconstruction.yaml`, `notation.py` legacy keys |
| **sensitivity_sweep_legacy_axis** | **~350+** | `ktau_sensitivity.py`, `sparc_ktau_sensitivity_summary.csv`, `ngc7814_ktau_sensitivity.csv`, config `k_tau_values` |
| **frozen_csv_column** | **~30 headers + column cells** | All expansion20/expansion12/SPARC benchmark CSVs |
| **frozen_generated_report** | **~55** | `outputs/reports/sparc_*.md` |
| **historical_documentation** | **~45** | `docs/*.md`, README (dual notation explanations) |
| **test_backward_compatibility** | **~68** | `tests/test_notation_*.py`, `test_radial_tau.py`, `test_ktau_sensitivity.py` |
| **forbidden_or_confusing** | **~8** | `notation.py` `kappa_tau` guards (must remain) |

**Total distinct files with matches:** ~85 (excluding egg-info).  
**Unicode Kτ / kτ:** 0 matches.

---

## 3. Recommended safe Phase 5G-C-B rename scope

### In scope (low–medium risk, behavior-preserving)

1. **Dataclass primary fields**
   - `TauReconstructionConfig.k_tau` → `k_g`
   - `TdfKnotConfig.k_tau` → `k_g`

2. **Property alias plan**
   ```python
   @property
   def k_tau(self) -> float:
       """Deprecated alias for gravitational projection coefficient (K_g)."""
       return self.k_g
   ```
   - Read-only; no setter in 5G-C-B.
   - `@dataclass` frozen configs: implement via `__init__` wrapper or small mixin; avoid breaking pickle/hash if used.

3. **Function parameters** (internal API)
   - `tdf_velocity_squared_kms2`, `tdf_velocity_kms`, `fit_tdf_knot_model`, holdout helpers: primary arg `k_g`; accept deprecated `k_tau=` keyword with `DeprecationWarning` for one release cycle.

4. **Docstrings and inline comments** in `radial_tau.py`, `tdf_knot.py`: use **K_g** in equations; note legacy **K_tau** CSV label.

5. **Report generator source** (not frozen files): prefer **K_g** in newly emitted prose; parenthetical “legacy benchmark label K_tau in frozen tables”.

6. **Tests**
   - Before rename: full `pytest` green (255 tests).
   - After rename: existing 5G-A/5G-B tests unchanged in intent; add `test_dataclass_k_tau_property_alias`.
   - Assert CSV writers still produce column name exactly `K_tau` and identical numeric cells when inputs unchanged.
   - Optional byte-identity check: hash `expansion20_holdout_validation.csv` at HEAD vs post-rename **without** rerunning pipeline (static writer unit test only).

### Out of scope for 5G-C-B

- Renaming frozen CSV column headers (`K_tau` → `K_g`).
- Rewriting committed `outputs/tables/*.csv` or `outputs/reports/*.md`.
- Changing `configs/reconstruction.yaml` production keys (legacy remains valid).
- Renaming sensitivity config keys `k_tau_values` / `reference_k_tau` in YAML (loader alias only).
- Touching **kappa_tau** handling or implying it maps to projection.
- Rerunning expansion20, Phase 4L sensitivity, or regenerating `paper/manuscript.pdf`.

---

## 4. References that must not be touched

| Category | Examples | Reason |
| --- | --- | --- |
| Frozen benchmark CSV schemas | `K_tau` column in `expansion20_holdout_validation.csv`, `expansion20_tau_profiles.csv`, `controlled_expansion_final_claims.csv` | Byte-identical release artifacts |
| Frozen sensitivity tables | `sparc_ktau_sensitivity_summary.csv`, `ngc7814_ktau_sensitivity.csv` | Phase 4L audit record |
| Committed reports | `outputs/reports/sparc_ktau_sensitivity_report.md`, etc. | Historical audit trail |
| Legacy config file keys | `configs/reconstruction.yaml` `k_tau`, `K_tau`, `k_tau_values` | Backward compatibility |
| `notation.py` legacy key map + `kappa_tau` rejection | `PROJECTION_KEYS_LEGACY`, `FORBIDDEN_PROJECTION_KEYS` | 5G-A/5G-B contract |
| 5G-B regression fixtures | `tests/fixtures/notation/reconstruction_k_tau_legacy.yaml` | Proves loader equivalence |
| Manuscript / paper PDF | `paper/manuscript.tex` (already K_g), `paper/manuscript.pdf` | Publication package frozen |
| Caution tokens in frozen CSVs | `fixed_K_tau` in `sparc_best_model_summary.csv` | Matches published tables |

---

## 5. Outputs that must remain byte-identical (5G-C-B acceptance)

If any code path re-emits these without an explicit rerun request, output must match `v0.1.3-notation-compatibility` bytes:

- `outputs/tables/expansion20_holdout_validation.csv`
- `outputs/tables/expansion20_tau_profiles.csv`
- `outputs/tables/expansion20_failure_mode_summary.csv`
- `outputs/tables/controlled_expansion_final_claims.csv`
- `outputs/tables/expansion12_holdout_validation.csv`
- `outputs/tables/expansion12_tau_profiles.csv`
- `outputs/tables/expansion12_failure_mode_summary.csv`
- `outputs/tables/sparc_*` benchmark summaries (six-galaxy subset)
- `outputs/tables/tau_profiles/*.csv`
- `outputs/figures/**` (no figure regeneration)

---

## 6. Explicit audit disclaimer

**This audit does not modify benchmark numbers, outputs, figures, or frozen CSV schemas.** It is a read-only map for Phase 5G-C-B implementation planning. **κ_tau** remains field stiffness only; **K_g** is the preferred projection coefficient; legacy **K_tau** remains the frozen-output label until a versioned migration pass (not planned in 5G-C-B).

---

## 7. Suggested 5G-C sub-phases

| Sub-phase | Status | Deliverable |
| --- | --- | --- |
| **5G-C-A** | **complete** (this document) | Reference map + classification |
| **5G-C-B** | planned | Dataclass/param rename + property alias + tests; no frozen output rewrite |
| **5G-C-C** (optional) | future | Production YAML migration to `k_g`; report regeneration policy |
