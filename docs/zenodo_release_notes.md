# Zenodo release notes (draft)

## Release title

**tdf-galaxy-tau-benchmark: Controlled SPARC expansion-20 TDF radial holdout benchmark and publication package**

## Description

This deposit contains code, frozen benchmark outputs, and a manuscript package for a
controlled rotation-curve study of Time-Delay Field (TDF) radial τ reconstruction on a
pre-registered 20-galaxy SPARC subset (expansion-20), with a nested 12-galaxy cohort
(expansion-12). The primary model is **tdf_3knot** (conservative knot count); **tdf_5knot**
is documented as sensitivity-only. Train-only even/odd holdout comparisons use fixed
canonical baryons and fixed \(K_\tau\) against NFW and MOND baselines.

## Keywords

rotation curves; SPARC; galaxy dynamics; holdout validation; model comparison; MOND; NFW;
benchmark; reproducibility

## Included artifacts

- Source: `src/tdf_galaxy_tau/`, `scripts/`, `configs/`, `tests/`
- Data: `data/raw/sparc/`, `data/processed/sparc/`
- Frozen outputs: `outputs/tables/`, `outputs/reports/`, `outputs/figures/sparc_subset/`
- Paper: `paper/manuscript.pdf`, `paper/manuscript.tex`, `paper/figures/`, `paper/tables/`, `paper/references.bib`
- Documentation: `docs/` (assumptions, limitations, claims, reviewer matrix)

## Known limitations

- **Subset-only:** not full-SPARC validation.
- **Radial holdout only:** no lensing data or tests.
- **Fixed baryons / fixed \(K_\tau\):** no final photometry-calibrated \(M/L\) claim.
- **Primary metric:** tdf_3knot holdout success; tdf_5knot is not primary success.
- **Canonical failure:** NGC7814 remains an all-TDF holdout failure in this cohort.

## Claim boundaries (do not over-interpret)

- Does **not** disprove dark matter.
- Does **not** replace ΛCDM.
- Does **not** establish a universal τ-profile.
- Does **not** confirm lensing predictions.

## Reproducibility

See [`reproducibility_commands.md`](reproducibility_commands.md). Minimum check:

```bash
python3 -m pytest -q
python3 scripts/compile_paper_pdf.py
```

## Citation

**Published Zenodo preprint (manuscript PDF):**

- **DOI:** [10.5281/zenodo.20437254](https://doi.org/10.5281/zenodo.20437254)
- **Record:** https://zenodo.org/records/20437254

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

**Software repository** (separate from the preprint deposit):

```bibtex
@software{tdf_galaxy_tau_benchmark2026,
  title  = {tdf-galaxy-tau-benchmark: Controlled SPARC expansion-20 TDF holdout benchmark},
  author = {Masarrat, Bahman},
  year   = {2026},
  url    = {https://github.com/bahman2017/tdf-galaxy-tau-benchmark},
  version = {v0.1.0-expansion20-paper}
}
```

## Version

Repository commit at release time should be tagged (e.g. `v0.1.0-expansion20-paper`).
