# SPARC Photometry Metadata Ingestion Report (Phase 4J)

> This phase ingests photometry metadata for future M/L prior construction. It does not perform final M/L calibration, does not rerun model fits, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Data source and provenance

- **Scientific citation:** Lelli, McGaugh & Schombert (2016), AJ 152, 157; SPARC http://astroweb.case.edu/SPARC/
- **Working copy used:** `SPARC_Table1_vizier_working_copy.tsv` under `data/raw/sparc/photometry/` (CDS/VizieR transport)
- **Rotmod cross-check:** distance from `sparc_rotmod_standardized.csv` when needed

## Schema and units

- `distance_mpc` — Mpc
- `inclination_deg` — degrees
- `luminosity_3p6_lsun` — L_sun at 3.6 µm (Table 1)
- `disk_scale_length_kpc` — exponential disk scale length R_d (kpc)
- `central_surface_brightness` — 3.6 µm central disk SB (L_sun/pc²) from Table 1
- `morphological_type` — numerical Hubble type (0–11) from Table 1

## Missing-field summary

- `distance_mpc`: 175/175 finite (0.0% missing)
- `inclination_deg`: 175/175 finite (0.0% missing)
- `luminosity_3p6_lsun`: 175/175 finite (0.0% missing)
- `disk_scale_length_kpc`: 175/175 finite (0.0% missing)
- `central_surface_brightness`: 175/175 finite (0.0% missing)
- `morphological_type`: 175/175 finite (0.0% missing)
- Galaxies in metadata table: **175**

## Six-galaxy subset

| Galaxy | Class | D [Mpc] | i [deg] | L3.6 | Rd [kpc] | Type | Bulge proxy |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| DDO154 | robust_tdf_success | 4.04 | 64.0 | 0.053 | 0.37 | 10.0 | False |
| NGC2403 | robust_tdf_success | 3.16 | 63.0 | 10.041 | 1.39 | 6.0 | False |
| NGC3198 | robust_tdf_success | 13.8 | 73.0 | 38.279 | 3.14 | 5.0 | False |
| NGC6503 | robust_tdf_success | 6.26 | 74.0 | 12.845 | 2.16 | 6.0 | False |
| IC2574 | robust_tdf_success | 3.91 | 75.0 | 1.016 | 2.78 | 9.0 | False |
| NGC7814 | tdf_failure_mode | 14.4 | 90.0 | 74.529 | 2.54 | 2.0 | True |

## NGC7814 photometry and structural context

- Sa-type (Type~2), high L3.6 and SBdisk; bulge-dominated proxy True. Supports photometry-informed downweight of bulge M/L in future priors; does not change canonical tdf_3knot failure.
- Distance **14.4** Mpc, inclination **90.0**°, L3.6 **74.529** L_sun, R_disk **2.54** kpc.
- Compared to success galaxies: **higher luminosity**, **earlier type (bulge/spheroid component)**, **much higher central disk SB** — structurally distinct for future bulge-aware M/L priors.
- **Canonical tdf_3knot holdout failure unchanged** at fixed rotmod baryons.

## Five success galaxies

- Typically later types / lower central SB / no strong bulge in rotmod (see subset table).
- Bulge-dominated proxy True count: **0 / 5**

## Future M/L priors (not implemented here)

- Map L3.6 and type to disk/bulge M/L bands with uncertainties
- Replace Cartesian diagnostic weights in `configs/ml_priors.yaml`
- Re-run prior audit (4I-Audit) before external recovery language
