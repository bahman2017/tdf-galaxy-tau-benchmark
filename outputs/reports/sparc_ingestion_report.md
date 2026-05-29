# SPARC Ingestion Report (Phase 1A)

## Scope

Data ingestion and standardization only. This is **not** model validation.

## Metrics

- Raw files found: 175
- Galaxies parsed successfully: 175
- Galaxies failed: 0
- Total radial data points: 3391
- Radius range [kpc]: 0.08 to 108.31
- Observed velocity range [km/s]: 1.41 to 383.0
- Galaxies with bulge contribution: 32
- Rows with negative residual_v2_kms2: 1053

## Output

- Standardized CSV: `data/processed/sparc/sparc_rotmod_standardized.csv`
- Summary CSV: `outputs/tables/sparc_ingestion_summary.csv`

## Failed files

- None

## Claim boundary

This report documents ingestion quality only; it does not validate TDF, NFW, or Burkert fits and does not make any dark-matter-disproof claim.
