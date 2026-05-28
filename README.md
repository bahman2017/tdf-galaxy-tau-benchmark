# tdf-galaxy-tau-benchmark

Multi-galaxy benchmark scaffold for extending the M33 TDF tau-geometry reconstruction workflow to a controlled SPARC subset and later the broader SPARC sample.

## Current project status

This repository is currently in **Phase 0B scaffold hardening**.

- Current generated tables/figures are **scaffold outputs from mock data** when no processed SPARC CSV is present.
- **No observational claim can be made from mock data.**
- This repo does **not** claim that dark matter is disproven.
- This repo does **not** claim TDF has already been validated on SPARC.

## Project objective

Test whether the same reconstruction law used in M33 can produce **galaxy-specific** reconstructed tau profiles/maps across galaxies.

Core equations preserved for each galaxy:

- `v_obs^2(r) = v_bar^2(r) + v_tau^2(r)`
- `v_tau^2(r) = r K_tau dτ/dr`
- `dτ/dr = [v_obs^2(r) - v_bar^2(r)] / [r K_tau]`

No universal closed-form tau profile is assumed.

## Unit conventions

- `r_kpc`: radius in kpc
- `v_*_kms`: velocity in km/s
- `*_kms2`: velocity squared in km^2/s^2
- `K_tau`: normalization/calibration parameter (not a measured universal constant)
- `dtaudr_reconstructed`: reconstruction quantity derived from residual dynamics

## Relationship to `TDF_m33`

- Multi-galaxy extension of the M33 reconstruction pipeline.
- M33 remains the first case study and method prototype.
- M33-specific assumptions are moved to transition documentation, not treated as universal.

## Relationship to `tdf-benchmark-lab`

- Reuses only focused generic patterns for SPARC-style loading, benchmark metrics, and plotting helpers.
- Does not include unrelated black hole, CMB, redshift, quantum, or broad cosmology modules.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
python3 -m pytest -q
python3 scripts/run_sparc_subset.py --config configs/sparc_subset.yaml
```

## Reproducibility

- Config-driven runs from `configs/`.
- Raw inputs under `data/raw/`; processed inputs under `data/processed/`.
- Outputs written to `outputs/figures/`, `outputs/tables/`, and `outputs/reports/`.
- Limits/assumptions/status tracked in `docs/limitations.md`, `docs/assumptions.md`, and `docs/project_status.md`.
