# Roadmap

## Completed (high level)

- **Phase 0–1:** repo setup, SPARC schema, subset selection
- **Phase 2:** radial τ reconstruction
- **Phase 3:** baryonic / NFW / Burkert / MOND / TDF comparison and holdout
- **Phase 4:** failure modes, M/L diagnostics, photometry-informed priors, controlled six-galaxy audit
- **Phase 5A–5E:** pre-registered expansion_12 / expansion_20 cohorts and final audit (C20 claims)
- **Phase 5F:** publication package (manuscript, figures, tables, QA) and Zenodo preprint

## Current

- **Phase 5E/5F (maintenance):** controlled expansion-20 publication package; documentation consistency with updated TDF effective-gravity notation (**K_g**, **κ_tau** vs legacy **K_tau** in frozen outputs).

## Planned

### Phase 5G — notation migration (K_tau → K_g)

**Goal:** Align code, configs, and report generators with updated notation without changing frozen benchmark numbers.

**Scope:**

1. Introduce **K_g** as the primary symbol in documentation strings and user-facing prose generators.
2. Retain **K_tau** as a **backward-compatible alias** in configs and CSV readers (map `K_tau` → `K_g` internally).
3. Add tests that alias paths reproduce identical holdout metrics on frozen expansion_20 tables.
4. Explicitly document that **κ_tau** is reserved for mother-field stiffness and is **not** renamed from legacy **K_tau**.
5. Do **not** rewrite historical `outputs/tables/*.csv` column headers without a versioned migration pass.

**Out of scope for 5G:** new fits, cohort expansion, or claim-boundary changes.

### Phase 6 — optional 2D τ-map reconstruction

Requires frozen 1D benchmark and explicit scope change.

### Phase 7 — frozen τ-map lensing / deflection prediction

Only after Phase 6 and independent validation protocol; **not** part of current expansion_20 claims.

## Explicit non-goals (unless scope changes)

- Full-SPARC validation in the current claim set
- Dark-matter disproof or ΛCDM replacement language
- Universal closed-form τ profile across galaxies
