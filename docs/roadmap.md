# Roadmap

## Completed (high level)

- **Phase 0–1:** repo setup, SPARC schema, subset selection
- **Phase 2:** radial τ reconstruction
- **Phase 3:** baryonic / NFW / Burkert / MOND / TDF comparison and holdout
- **Phase 4:** failure modes, M/L diagnostics, photometry-informed priors, controlled six-galaxy audit
- **Phase 5A–5E:** pre-registered expansion_12 / expansion_20 cohorts and final audit (C20 claims)
- **Phase 5F:** publication package (manuscript, figures, tables, QA) and Zenodo preprint
- **Phase 5G-A:** K_g / legacy K_tau config alias layer (**complete**; tag `v0.1.2-notation-aliases`)
- **Phase 5G-B:** loader compatibility regression lock (**complete**; tag `v0.1.3-notation-compatibility`)
- **Phase 5G-C-B:** internal k_g rename with legacy aliases (**complete**; tag `v0.1.4-internal-kg-rename`)
- **Phase 5G-C-A:** internal rename audit (**complete**; `docs/phase5g_internal_rename_audit.md`)
- **Phase 5G-D:** final notation QA (**complete**; tag `v0.1.5-notation-qa`)
- **Phase 5I:** v0.1.6 publication-freeze release notes (**complete**)
- **Phase 5H-B:** metadata hygiene (**complete**; tag `v0.1.6-publication-freeze`)

## Current

- **Phase 5 publication package closed** at `v0.1.6-publication-freeze`. **Next:** Phase **6A** (2D / frozen-map test formulation).

## Planned

### Phase 5G — notation migration (K_tau → K_g)

#### Phase 5G-A — alias layer (**complete**)

- `normalize_projection_coefficient()` accepts `k_g`/`K_g` and legacy `k_tau`/`K_tau`
- Rejects `kappa_tau` as projection; rejects conflicting dual keys
- Frozen CSV column names and outputs **not** renamed

#### Phase 5G-B — compatibility regression lock (**complete**)

- Proves `k_g`/`K_g` and legacy `k_tau`/`K_tau` load to identical effective projection at config-loader level
- `tests/test_notation_compatibility_regression.py` + fixtures under `tests/fixtures/notation/`
- **Not** a full internal rename; dataclass fields and CSV columns unchanged

#### Phase 5G-C-A — internal rename audit (**complete**)

- Read-only reference map: `docs/phase5g_internal_rename_audit.md`
- Classifies ~85 files; no code or frozen output changes

#### Phase 5G-C-B — internal rename (**complete**)

- `TauReconstructionConfig.k_g` / `TdfKnotConfig.k_g` primary fields; read-only `.k_tau` property aliases
- `tdf_velocity_*`, `fit_tdf_knot_baseline`, holdout helpers: primary `k_g`; deprecated `k_tau=` kwarg
- CSV writers still emit column **`K_tau`**; frozen tables not rewritten
- `tests/test_phase5g_internal_kg_rename.py` + extended 5G-A/5G-B tests (264 tests)

#### Phase 5G-D — final notation QA (**complete**)

- Grep audit, claim-boundary check, 264 tests — **PASS**
- `docs/phase5g_final_notation_qa.md`
- **Phase 5G closed** for frozen expansion-20 benchmark scope

#### Phase 5G-C-C — optional production config migration (future)

- Migrate `configs/reconstruction.yaml` to `k_g` keys; regenerate reports under explicit rerun policy only.

**Out of scope for 5G:** new fits, cohort expansion, or claim-boundary changes.

### Phase 5H — publication readiness freeze

#### Phase 5H-A — publication readiness audit (**complete**)

- `docs/phase5h_publication_readiness_freeze.md`
- Verdict: **ready with minor metadata blockers** (LICENSE, version metadata sync)
- No benchmark rerun; frozen expansion_20 claims unchanged

#### Phase 5H-B — metadata hygiene (**complete**)

- Root MIT `LICENSE`; `CITATION.cff` `v0.1.6-publication-freeze`; `pyproject.toml` `0.1.6`
- Metadata blockers from 5H-A cleared; ready for publication-freeze tag

### Phase 5I — release notes / Zenodo documentation (**complete**)

- `docs/release_notes_v0.1.6_publication_freeze.md`
- Updated `docs/zenodo_release_notes.md` for software deposit at `v0.1.6-publication-freeze`

### Phase 6 — optional 2D τ-map reconstruction

#### Phase 6A — test protocol formulation (planned)

- Pre-register 2D / frozen-map validation scope before any new fits
- Requires explicit scope change from frozen expansion_20 1D benchmark

Requires frozen 1D benchmark and explicit scope change.

### Phase 7 — frozen τ-map lensing / deflection prediction

Only after Phase 6 and independent validation protocol; **not** part of current expansion_20 claims.

## Explicit non-goals (unless scope changes)

- Full-SPARC validation in the current claim set
- Dark-matter disproof or ΛCDM replacement language
- Universal closed-form τ profile across galaxies
