# Zenodo release notes — v0.1.6-publication-freeze

## Release title

**tdf-galaxy-tau-benchmark: Controlled SPARC expansion-20 TDF radial holdout benchmark — publication-freeze snapshot**

## Software version

**`v0.1.6-publication-freeze`** (commit `0e4b202`)

## Related DOI (manuscript preprint)

- **DOI:** [10.5281/zenodo.20437254](https://doi.org/10.5281/zenodo.20437254)
- **Relation:** This software deposit supplements the Zenodo preprint (manuscript PDF).

## Description (Zenodo-ready)

This deposit is a **publication-freeze software snapshot** for a controlled rotation-curve benchmark of Time-Delay Field (TDF) radial τ reconstruction on a **pre-registered 20-galaxy SPARC subset (expansion-20)**, with a nested 12-galaxy cohort (expansion-12). Train-only even/odd holdout validation compares the primary conservative **tdf_3knot** model against NFW and MOND at fixed canonical baryons and fixed **K_g** (gravitational projection coefficient; legacy benchmark label **K_tau** in frozen outputs and configs).

**Headline results (controlled cohort only):** primary **tdf_3knot** robust holdout success in **15 of 20** galaxies; **three** **tdf_5knot** sensitivity-recovery cases (not primary success); **NGC7814** all-TDF holdout failure; **UGC00128** mixed near-tie.

**Explicit scope statement:** This is a **controlled expansion_20 benchmark snapshot**, **not** full-SPARC validation. The deposit includes frozen benchmark tables, audit reports, tests (264), manuscript sources, and documentation through Phase 5G notation migration and Phase 5H publication readiness.

## Keywords

rotation curves; SPARC; galaxy dynamics; holdout validation; model comparison; MOND; NFW; benchmark; reproducibility; Time-Delay Field; TDF

## Included artifacts

- Source: `src/tdf_galaxy_tau/`, `scripts/`, `configs/`, `tests/`
- Data: `data/raw/sparc/`, `data/processed/sparc/`
- Frozen outputs: `outputs/tables/`, `outputs/reports/`, `outputs/figures/sparc_subset/`
- Paper: `paper/manuscript.pdf`, `paper/manuscript.tex`, `paper/tables/`, `paper/references.bib`
- Documentation: `docs/` (assumptions, limitations, claims, release notes)
- License: `LICENSE` (MIT)

## Known limitations

- **Subset-only:** not full-SPARC validation.
- **Radial holdout only:** no lensing data or tests.
- **Fixed baryons / fixed K_g:** no final photometry-calibrated M/L claim.
- **Primary metric:** tdf_3knot holdout success; tdf_5knot is sensitivity-only.
- **Canonical failure:** NGC7814 remains an all-TDF holdout failure.

## Claim boundaries (do not over-interpret)

- Does **not** disprove dark matter.
- Does **not** replace ΛCDM.
- Does **not** establish a universal τ-profile.
- Does **not** confirm lensing predictions.

## Reproducibility

See [`reproducibility_commands.md`](reproducibility_commands.md). Minimum validation:

```bash
python3 -m pytest -q
python3 scripts/build_controlled_expansion_final_audit.py
```

## Citation

**Published Zenodo preprint (manuscript PDF):**

```bibtex
@misc{masarrat2026tdf_preprint,
  author       = {Masarrat, Bahman},
  title        = {TDF Galaxy Tau Benchmark: Controlled SPARC Expansion-20 Rotation-Curve Benchmark with Holdout Validation, Failure Modes, and Sensitivity-Recovery Analysis},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.20437254},
  url          = {https://doi.org/10.5281/zenodo.20437254}
}
```

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

Full release notes: [`release_notes_v0.1.6_publication_freeze.md`](release_notes_v0.1.6_publication_freeze.md).
