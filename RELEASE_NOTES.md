# Release notes — v0.1.0-expansion20-paper

**Tag:** `v0.1.0-expansion20-paper`  
**Repository:** https://github.com/bahman2017/tdf-galaxy-tau-benchmark

## Summary

This release packages the **controlled expansion-20** SPARC subset benchmark for Time-Delay
Field (TDF) radial τ reconstruction, with frozen benchmark tables, phase audit reports, and
the manuscript PDF (`paper/manuscript.pdf`).

## Main result

In the preregistered controlled **expansion-20** cohort, the primary conservative
**tdf_3knot** model achieves **robust holdout success in 15 of 20 galaxies**. **tdf_5knot**
is **sensitivity-only** (not primary success).

## Cohort diagnostics (frozen)

| Case | Status |
| --- | --- |
| Primary robust success | 15 / 20 galaxies (`tdf_3knot`) |
| Sensitivity-recovery | 3 galaxies (`tdf_5knot` improves; not primary success) |
| All-TDF holdout failure | NGC7814 (canonical failure) |
| Mixed near-tie | UGC00128 |

Nested **expansion-12** results are included for protocol context; headline claims are
expansion-20 only.

## Claim boundaries (what this release does **not** claim)

- No dark-matter disproof
- No ΛCDM replacement
- No full-SPARC validation (subset-only)
- No lensing confirmation
- No universal τ-profile across galaxies
- No final \(M/L\) calibration claim

Authoritative claim IDs: `outputs/tables/controlled_expansion_final_claims.csv` (C20-A–C20-H);
see `docs/paper_ready_claims.md`.

## Included artifacts

- Source: `src/`, `scripts/`, `configs/`, `tests/`
- Data: `data/raw/sparc/`, `data/processed/sparc/`
- Frozen outputs: `outputs/tables/`, `outputs/reports/`, `outputs/figures/sparc_subset/`
- Paper: `paper/manuscript.pdf`, `paper/manuscript.tex`, `paper/figures/`, `paper/tables/`
- Documentation: `docs/` (assumptions, limitations, reviewer matrix, reproducibility)

## Reproducibility

```bash
python3 -m pip install -e ".[plots,dev]"
python3 -m pytest -q
python3 scripts/run_expansion20_pipeline.py
python3 scripts/build_controlled_expansion_final_audit.py
python3 scripts/export_paper_tables.py
python3 scripts/build_paper_figures.py
python3 scripts/compile_paper_pdf.py
```

Full command reference: `docs/reproducibility_commands.md`.  
Zenodo deposit draft: `docs/zenodo_release_notes.md`.

## Repository hygiene (this release)

- LaTeX build artifacts under `paper/` are gitignored; only `paper/manuscript.pdf` is tracked.
- Phase 0 mock figures and a duplicate manuscript PDF were moved to `archive/` (see `archive/README.md`).

## Citation

See `CITATION.cff`. Zenodo DOI to be assigned on upload.
