# Data Sources

## Phase 1B status

This phase uses the standardized SPARC table to perform deterministic subset selection and QC reporting only.
No model fitting is performed in this phase.

## Primary scientific provenance

Use these as citation sources:

- SPARC official site: http://astroweb.case.edu/SPARC/
- Lelli, McGaugh, Schombert (2016): *SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves*.

## Mirror/cache note

A local mirror such as `bahman2017/sparc` can be used for transport/cache of raw `Rotmod_LTG` files.
The mirror is **not** the scientific citation source.

## Standardized source table used by Phase 1B

- `data/processed/sparc/sparc_rotmod_standardized.csv`

Subset selection reads this table and produces selection metadata only. It does not modify raw files.

## Subset-selection outputs

- `outputs/tables/sparc_subset_selection.csv`
- `outputs/reports/sparc_subset_selection_report.md`

## Schema and units (standardized table)

- `galaxy_id`
- `source_file`
- `distance_mpc`
- `r_kpc`
- `v_obs_kms`
- `v_err_kms`
- `v_gas_kms`
- `v_disk_kms`
- `v_bulge_kms`
- `sb_disk_lpc2`
- `sb_bulge_lpc2`
- `v_bar_kms`
- `residual_v2_kms2`
- `quality_flag`
- `data_source`
- `data_mode`

## Claim boundary

Subset selection quality does not validate TDF, NFW, Burkert, or dark-matter alternatives.
No claim is made that TDF fits SPARC in this phase.


## Phase 4J photometry metadata provenance

- Scientific citation source remains **SPARC official site** and **Lelli et al. (2016)**.
- Working-copy transport used in this repo: `data/raw/sparc/photometry/SPARC_Table1_vizier_working_copy.tsv` from CDS/VizieR `J/AJ/152/157/table1`.
- The VizieR TSV is a **working copy cache** for ingestion only; do not cite mirrors/caches as the scientific source.
- Metadata ingestion output: `data/processed/sparc/sparc_photometry_metadata.csv`.
- Phase 4J ingests metadata only; no new model fitting and no raw rotmod modification.
