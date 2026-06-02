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
- **Phase 5G-C-A:** internal rename audit (**complete**; `docs/phase5g_internal_rename_audit.md`)

## Current

- **Phase 5G-C-A complete; Phase 5G-C-B planned:** audit maps ~52 internal projection candidates; frozen CSV columns and sensitivity tables remain legacy **K_tau**.

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

#### Phase 5G-C-B — internal rename (planned)

**Goal:** Rename internal `k_tau` dataclass fields and function parameters to `k_g` with read-only `.k_tau` property aliases — per audit; only after 5G-B lock.

**Scope (from audit):**

1. `TauReconstructionConfig.k_tau` → `k_g`; `TdfKnotConfig.k_tau` → `k_g`; deprecated `.k_tau` property.
2. Internal API params (`tdf_velocity_*`, `fit_tdf_knot_model`, holdout runners) primary `k_g`; optional deprecated `k_tau=` kwarg.
3. Docstrings and report-generator source prefer **K_g**; frozen CSV writers keep column name **`K_tau`**.
4. Tests: extend 5G-B regression; property alias test; CSV column name unchanged.
5. **κ_tau** guards unchanged; **no** in-place frozen CSV header renames.

#### Phase 5G-C-C — optional production config migration (future)

- Migrate `configs/reconstruction.yaml` to `k_g` keys; regenerate reports under explicit rerun policy only.

**Out of scope for 5G:** new fits, cohort expansion, or claim-boundary changes.

### Phase 6 — optional 2D τ-map reconstruction

Requires frozen 1D benchmark and explicit scope change.

### Phase 7 — frozen τ-map lensing / deflection prediction

Only after Phase 6 and independent validation protocol; **not** part of current expansion_20 claims.

## Explicit non-goals (unless scope changes)

- Full-SPARC validation in the current claim set
- Dark-matter disproof or ΛCDM replacement language
- Universal closed-form τ profile across galaxies
