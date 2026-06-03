# Phase 5G-D — Final notation QA (read-only)

**Date:** 2026-05-29  
**Tagged baseline:** `v0.1.4-internal-kg-rename` → `08cfc5dad898ab7ca34621936434703661aff392`  
**Verdict:** **PASS** — Phase **5G notation migration is complete** for the current benchmark scope.

This pass is **QA/audit only**. No code behavior changes, no benchmark rerun, no frozen output rewrites.

---

## 1. Current release stack

| Tag | Commit | Role |
| --- | --- | --- |
| `v0.1.0-expansion20-paper` | `0da4190` | Expansion-20 paper release |
| `v0.1.1-notation-alignment` | `144c77d` | Documentation / manuscript K_g alignment |
| `v0.1.2-notation-aliases` | `533ae11` | Phase 5G-A config alias layer |
| `v0.1.3-notation-compatibility` | `e80eae1` | Phase 5G-B loader regression lock |
| `v0.1.4-internal-kg-rename` | `08cfc5d` | Phase 5G-C-B internal `k_g` rename + legacy aliases |

---

## 2. Final notation policy

| Symbol | Role | Where used |
| --- | --- | --- |
| **k_g / K_g** | Preferred **gravitational projection coefficient** | Internal dataclasses, function parameters, loaders, manuscript, new report-generator prose |
| **k_tau / K_tau** | **Legacy only** — backward-compatible YAML keys, deprecated `.k_tau` property / `k_tau=` kwargs, **frozen CSV column headers**, sensitivity sweep axis labels, historical docs/reports | Must not be introduced as a new primary internal field |
| **kappa_tau / κ_tau** | **Mother-field stiffness only** | `notation.py` rejects as projection; never mapped to K_g |

Radial closure (unchanged numerically):

- \(v_\tau^2(r) = r\, K_g\, d\tau/dr\)
- Frozen tables label the coefficient column **`K_tau`** for byte-stable benchmark artifacts.

---

## 3. Grep audit summary

Command (repository root):

```bash
grep -R "K_tau\|k_tau\|K_g\|k_g\|kappa_tau\|κ_tau" configs src scripts tests docs paper | head -1000
```

**Scope scanned:** `configs/`, `src/`, `scripts/`, `tests/`, `docs/`, `paper/`  
**Classification pass:** automated + manual review on `08cfc5d`  
**Excluded false positives:** `rank_g`, `mock_galaxies`, `egg-info/PKG-INFO`

### Match volume (line hits, approximate)

| Pattern family | Lines (configs–paper) | Notes |
| --- | ---: | --- |
| `k_tau` / `K_tau` (legacy) | ~430 | Includes tests, ktau module, frozen-output writers |
| `k_g` / `K_g` (preferred) | ~320 | Dominant in dataclasses, notation, manuscript |
| `kappa_tau` / `κ_tau` | ~45 | Almost entirely guardrails + explanatory docs |

**Frozen artifacts (classification only, not edited):**

| Location | Approx. legacy-line hits |
| --- | ---: |
| `outputs/tables/` | ~189 |
| `outputs/reports/` | ~47 |

---

## 4. Classification of remaining legacy K_tau / k_tau references

| Classification | Approx. count | Representative locations |
| --- | ---: | --- |
| **backward-compatible config** | 8 | `configs/reconstruction.yaml` (`k_tau`, `K_tau`, `k_tau_values`, `reference_k_tau`) |
| **deprecated alias / property** | 35 | `TauReconstructionConfig.k_tau` property; `resolve_projection_coefficient_kwarg`; deprecated `k_tau=` kwargs |
| **frozen CSV / report label** | ~241 | `PHASE_2A_OUTPUT_COLUMNS` `"K_tau"`; holdout row dicts; committed `outputs/tables/*.csv`, `outputs/reports/*.md` |
| **sensitivity sweep legacy axis** | 79 | `ktau_sensitivity.py`; config `k_tau_values`; `sparc_ktau_sensitivity_summary.csv` axis |
| **historical documentation** | 169 | `docs/theory_summary.md`, `paper_ready_claims.md`, report-source f-strings with legacy label |
| **test compatibility** | 154 | `test_notation_*.py`, `test_phase5g_internal_kg_rename.py`, legacy YAML fixtures |
| **forbidden guardrail (κ_tau)** | 4 | `notation.py` `FORBIDDEN_PROJECTION_KEYS` + error messages |
| **confusing / needs-fix** | **0** | — |

### Manual review notes (not classified as needs-fix)

- `metrics/comparison.py` token `fixed_K_tau` — matches frozen CSV caution strings; **keep**.
- `failure_modes.py` / `expansion_pipeline.py` strings mentioning `K_tau` — legacy label in claim language or frozen-table cross-reference; **keep**.
- `ktau_sensitivity.py` parameter names `reference_k_tau`, loop `k_tau` — sensitivity-axis legacy naming; values flow through internal `k_g` at holdout export boundary; **keep**.
- No `TauReconstructionConfig(k_tau=…)` or `TdfKnotConfig(k_tau=…)` dataclass **fields** remain in `src/` (only `k_g` field + `.k_tau` property).

---

## 5. Confusing / needs-fix references

**Count: 0**

All legacy `K_tau` / `k_tau` occurrences are accounted for under the classifications above. None map `kappa_tau` to projection. None reintroduce `k_tau` as a primary dataclass field.

---

## 6. Claim-boundary check (documentation)

Searched `docs/` for prohibited implication language. **PASS.**

| Prohibited claim | Finding |
| --- | --- |
| Dark matter disproven | Docs state **not** disproven / **prohibited** (`paper_ready_claims.md`, `results_summary.md`, `zenodo_release_notes.md`, etc.) |
| Full-SPARC validation complete | Docs state **controlled subset / expansion_20 only** — not full SPARC |
| Lensing confirmed | Docs state **lensing not tested** / future work |
| Universal τ profile | Docs state **no universal τ-profile** / not supported |

Manuscript (`paper/manuscript.tex`) uses **K_g** with explicit legacy **K_τ** note; claim boundaries unchanged.

---

## 7. Tests

```bash
python3 -m pytest -q
```

**Result:** **264 passed** (2 expected `DeprecationWarning` from intentional legacy `k_tau=` in `test_tdf_knot_model.py`).

Phase 5G regression suites:

- `tests/test_notation_aliases.py`
- `tests/test_notation_compatibility_regression.py`
- `tests/test_phase5g_internal_kg_rename.py`

---

## 8. Frozen outputs and figures

- **No** `outputs/tables/*.csv` modified in this QA pass.
- **No** `outputs/figures/` modified.
- **No** `paper/manuscript.pdf` regeneration committed.
- **No** expansion-20 or long benchmark pipeline rerun.

---

## 9. Phase 5G completion statement

| Sub-phase | Status |
| --- | --- |
| 5G-A alias layer | **Complete** (`v0.1.2-notation-aliases`) |
| 5G-B compatibility regression lock | **Complete** (`v0.1.3-notation-compatibility`) |
| 5G-C-A internal rename audit | **Complete** |
| 5G-C-B internal `k_g` rename | **Complete** (`v0.1.4-internal-kg-rename`) |
| 5G-D final notation QA | **Complete** (this document) |

**Phase 5G notation migration is complete** for the frozen expansion-20 benchmark package.

**Optional follow-up (not required for 5G closure):** Phase **5G-C-C** — migrate production `configs/reconstruction.yaml` to `k_g` keys and regenerate reports only under an explicit rerun policy.

---

## 10. Tag recommendation

**`v0.1.5-notation-qa` is not required.** `v0.1.4-internal-kg-rename` already pins the code state; this QA commit is documentation-only. Tag `v0.1.5-notation-qa` only if you want a release marker for the audit artifact itself.
