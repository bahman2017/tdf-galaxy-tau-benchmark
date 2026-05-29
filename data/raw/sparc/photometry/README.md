# SPARC Photometry Metadata (Phase 4J)

## Scientific provenance (citation target)

- SPARC: http://astroweb.case.edu/SPARC/
- Lelli, McGaugh & Schombert (2016), *AJ* 152, 157 — *SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves*
- VizieR catalog `J/AJ/152/157` (CDS): https://cdsarc.cds.unistra.fr/viz-bin/cat/J/AJ/152/157

## Working copies in this folder

| File | Role |
|------|------|
| `SPARC_Table1_vizier_working_copy.tsv` | **Transport/cache** of Table 1 galaxy parameters from VizieR/CDS (not a substitute for citing the paper) |
| `MasterSheet_SPARC.mrt` | Optional local copy of official `Table1.mrt` from the SPARC site (if placed manually) |

Do **not** modify official SPARC raw `Rotmod_LTG` files. Phase 4J only reads metadata tables and existing processed rotmod.

## Ingestion

```bash
python3 scripts/ingest_sparc_photometry_metadata.py
```

Produces `data/processed/sparc/sparc_photometry_metadata.csv`.
