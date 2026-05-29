# tdf-galaxy-tau-benchmark

Controlled multi-galaxy benchmark for Time-Delay Field (TDF) radial τ reconstruction on a
**pre-registered SPARC subset** (expansion-12 nested in expansion-20). This repository supports
the manuscript *TDF Radial Reconstruction on a Preregistered Controlled SPARC Subset*.

## Project objective

Test whether the M33-style reconstruction law produces **galaxy-specific** reconstructed τ
profiles on a controlled cohort using fixed canonical baryons and fixed \(K_\tau\), with
train-only even/odd radial holdout validation against NFW and MOND baselines.

Core relations (per galaxy):

- \(v_{\mathrm{obs}}^2(r) = v_{\mathrm{bar}}^2(r) + v_\tau^2(r)\)
- \(v_\tau^2(r) = r K_\tau \, d\tau/dr\)

No universal closed-form τ profile is assumed.

## Main result (controlled expansion-20)

In the preregistered controlled expansion-20 cohort, the primary conservative **tdf_3knot**
model achieves robust holdout success in **15 of 20** galaxies; **tdf_5knot** is
**sensitivity-only** (not primary success). NGC7814 remains the canonical all-TDF holdout
failure; UGC00128 is a documented mixed near-tie case.

Authoritative claim language: [`docs/paper_ready_claims.md`](docs/paper_ready_claims.md),
[`outputs/tables/controlled_expansion_final_claims.csv`](outputs/tables/controlled_expansion_final_claims.csv).

## What this does **not** claim

- No dark-matter disproof
- No ΛCDM replacement
- No full-SPARC validation (subset-only)
- No lensing confirmation
- No universal τ-profile across galaxies
- No final \(M/L\) calibration claim

## Quickstart

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python3 -m pip install -e ".[plots,dev]"
# or: python3 -m pip install -r requirements.txt
```

### Run tests

```bash
python3 -m pytest -q
```

### Reproduce expansion-20 benchmark (frozen pipeline)

```bash
python3 scripts/run_expansion20_pipeline.py
python3 scripts/build_controlled_expansion_final_audit.py
```

### Rebuild paper package (no refitting in figure/table export)

```bash
python3 scripts/export_paper_tables.py
python3 scripts/build_paper_figures.py
python3 scripts/compile_paper_pdf.py
```

PDF output: [`paper/manuscript.pdf`](paper/manuscript.pdf).

## Repository map

| Path | Role |
| --- | --- |
| [`configs/`](configs/) | YAML configs for subset, models, reconstruction, expansion |
| [`data/raw/sparc/`](data/raw/sparc/) | SPARC Rotmod_LTG inputs (provenance in `data/raw/sparc/README.md`) |
| [`data/processed/sparc/`](data/processed/sparc/) | Standardized rotmod + photometry CSVs |
| [`src/tdf_galaxy_tau/`](src/tdf_galaxy_tau/) | Library: data, models, validation, analysis |
| [`scripts/`](scripts/) | CLI entry points for ingestion, pipelines, paper build |
| [`outputs/tables/`](outputs/tables/) | Frozen benchmark CSVs |
| [`outputs/reports/`](outputs/reports/) | Phase audit and diagnostic reports |
| [`outputs/figures/sparc_subset/`](outputs/figures/sparc_subset/) | Diagnostic rotation-curve figures |
| [`paper/`](paper/) | Manuscript TeX/PDF, figures, LaTeX tables |
| [`docs/`](docs/) | Assumptions, limitations, claims, reviewer matrix |
| [`tests/`](tests/) | Pytest suite (224+ tests) |
| [`archive/`](archive/) | Optional home for superseded unreferenced artifacts |

Details: [`docs/repository_map.md`](docs/repository_map.md).

## Data provenance

- SPARC rotation-curve files: `data/raw/sparc/Rotmod_LTG/` (see [`docs/data_sources.md`](docs/data_sources.md)).
- Processed tables: `data/processed/sparc/sparc_rotmod_standardized.csv`, `sparc_photometry_metadata.csv`.
- Cohort selection: `outputs/tables/sparc_subset_expansion_plan.csv` (Phase 5A protocol).

## Reproducibility

Exact command list: [`docs/reproducibility_commands.md`](docs/reproducibility_commands.md).

Release notes template: [`docs/zenodo_release_notes.md`](docs/zenodo_release_notes.md).

## Citation / Zenodo

If you use this benchmark, cite the repository and the manuscript when available:

```bibtex
@software{tdf_galaxy_tau_benchmark2026,
  title  = {tdf-galaxy-tau-benchmark: Controlled SPARC expansion-20 TDF holdout benchmark},
  author = {Masarrat, Bahman},
  year   = {2026},
  url    = {https://github.com/bahman2017/tdf-galaxy-tau-benchmark}
}
```

Zenodo DOI: *to be assigned on release* (see `docs/zenodo_release_notes.md`).

## Related work

- **TDF_m33** — M33 prototype reconstruction.
- **tdf-benchmark-lab** — shared SPARC-style loading/metrics patterns only (no cosmology modules).

## Status

Phase **5E/5F** complete for controlled expansion-20 publication package. See
[`docs/project_status.md`](docs/project_status.md) and [`docs/controlled_expansion_results.md`](docs/controlled_expansion_results.md).
