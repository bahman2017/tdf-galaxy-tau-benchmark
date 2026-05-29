# Expansion-12 Radial Holdout Residual Maps (Phase 5B-R)

Phase 5B-R exports per-point train-only holdout residuals for flex-recovery galaxies **NGC5055** and **UGC05253** and summarizes failure localization by radial region (inner / middle / outer).

## Command

```bash
python3 scripts/analyze_expansion12_radial_residual_maps.py
```

## Scope

- Galaxies: NGC5055, UGC05253 only
- Models: `tdf_3knot`, `tdf_5knot`, `nfw_refit`, `mond_fit_a0_simple`
- Primary split for interpretation: `even_odd_index`
- Regenerates per-point predictions using Phase 5B configs; **does not modify** Phase 5B summary CSVs

## Disclaimer

This diagnostic phase analyzes radial residual structure for expansion_12 flex-recovery cases only. It does not add new fits for scientific claims, does not run expansion_20, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Outputs

| File | Description |
| --- | --- |
| `outputs/tables/expansion12_holdout_point_residuals.csv` | Per held-out point residuals |
| `outputs/tables/expansion12_radial_failure_map_summary.csv` | Regional RMSE aggregates |
| `outputs/reports/expansion12_radial_residual_map_report.md` | Narrative report |
| `outputs/figures/sparc_subset/ngc5055_radial_holdout_residuals.png` | NGC5055 residual map |
| `outputs/figures/sparc_subset/ugc05253_radial_holdout_residuals.png` | UGC05253 residual map |
| `outputs/figures/sparc_subset/expansion12_flex_recovery_radial_comparison.png` | Side-by-side comparison |
