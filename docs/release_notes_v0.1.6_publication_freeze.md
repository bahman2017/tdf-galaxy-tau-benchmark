# Release notes — v0.1.6-publication-freeze

## Release title

**tdf-galaxy-tau-benchmark: Controlled SPARC expansion-20 publication-freeze snapshot**

## Tag and commit

| Field | Value |
| --- | --- |
| **Git tag** | `v0.1.6-publication-freeze` |
| **Commit** | `0e4b202b01dee2ae67177993ada05453cb9d47bf` |
| **Package version** | `0.1.6` (`pyproject.toml`, `CITATION.cff`) |
| **Date** | 2026-05-29 |

Prior release tags: `v0.1.0-expansion20-paper` through `v0.1.5-notation-qa`.

---

## Scientific scope

This snapshot freezes a **controlled expansion_20** rotation-curve benchmark on a pre-registered 20-galaxy SPARC subset (nested expansion_12 cohort). Train-only even/odd radial holdout compares the primary conservative **`tdf_3knot`** model against NFW and MOND at **fixed canonical baryons** and fixed gravitational projection coefficient.

**This is not full-SPARC validation.** Claims are limited to the pre-registered controlled cohort.

---

## Key benchmark results (frozen)

| Result | Value |
| --- | --- |
| Primary **`tdf_3knot` robust holdout success** | **15 / 20** galaxies |
| **`tdf_5knot` sensitivity-recovery** | **3** galaxies (not primary success) |
| **NGC7814** | All-TDF holdout failure (canonical) |
| **UGC00128** | Mixed near-tie |

Authoritative claim table: `outputs/tables/controlled_expansion_final_claims.csv` (C20-A–H, FINAL-E20).

---

## Notation status (Phase 5G complete)

| Symbol | Role in this release |
| --- | --- |
| **K_g / k_g** | Preferred gravitational **projection coefficient** (code, manuscript, `CITATION.cff`) |
| **K_tau / k_tau** | **Legacy only** — YAML config keys, deprecated `.k_tau` property, **frozen CSV column headers**, sensitivity-axis labels |
| **κ_tau / kappa_tau** | **Field stiffness** in the mother field equation — **not** interchangeable with K_g |

Frozen benchmark CSVs retain legacy **`K_tau`** column names for byte-stable artifacts.

---

## Reproducibility commands

**Safe (no benchmark refit):**

```bash
python3 -m pytest -q
python3 scripts/build_controlled_expansion_final_audit.py
python3 scripts/export_paper_tables.py
python3 scripts/build_paper_figures.py
python3 scripts/compile_paper_pdf.py
```

**Long / benchmark-generating (not required to validate this snapshot):**

```bash
python3 scripts/run_expansion20_pipeline.py
python3 scripts/run_expansion12_pipeline.py
```

Full list: [`reproducibility_commands.md`](reproducibility_commands.md).

---

## Included artifacts

- **Source:** `src/tdf_galaxy_tau/`, `scripts/`, `configs/`, `tests/` (264 tests)
- **Data:** `data/raw/sparc/`, `data/processed/sparc/`
- **Frozen benchmark outputs:** `outputs/tables/expansion20_*`, `outputs/tables/controlled_expansion_*`, related reports and diagnostic figures under `outputs/figures/sparc_subset/`
- **Paper package:** `paper/manuscript.tex`, `paper/manuscript.pdf`, `paper/tables/`, `paper/references.bib`
- **Documentation:** `docs/` including claims matrix, limitations, Phase 5G/5H audits
- **License:** root `LICENSE` (MIT)

---

## Known limitations

- Controlled **expansion_20** cohort only — not the full SPARC catalog.
- Radial 1D holdout only — no 2D τ-map or lensing tests in this release.
- Fixed baryonic decomposition — no final photometry-calibrated M/L claim.
- Fixed projection coefficient — not measured or fitted.
- **`tdf_5knot`** is sensitivity-only; not the primary success metric.
- NGC7814 remains a documented canonical TDF holdout failure.

---

## Claim boundaries (do not over-interpret)

This release **does not**:

- disprove dark matter;
- replace ΛCDM;
- validate TDF on full SPARC;
- confirm lensing predictions;
- establish a universal τ-profile across galaxies.

---

## Recommended citation

**Manuscript (Zenodo preprint):**

- DOI: [10.5281/zenodo.20437254](https://doi.org/10.5281/zenodo.20437254)

**Software (this snapshot):**

```bibtex
@software{tdf_galaxy_tau_benchmark2026,
  title   = {tdf-galaxy-tau-benchmark: Controlled SPARC expansion-20 TDF holdout benchmark},
  author  = {Masarrat, Bahman},
  year    = {2026},
  url     = {https://github.com/bahman2017/tdf-galaxy-tau-benchmark},
  version = {v0.1.6-publication-freeze}
}
```

See also [`CITATION.cff`](../CITATION.cff) at repository root.

---

## Next planned phase

**Phase 6A** — formulation of a new **2D / frozen-map** test protocol (scientific scope change; requires explicit pre-registration before any new fits). Phase 5 publication package and notation migration are **closed** at this tag.
