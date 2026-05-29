# Photometry-Informed M/L Diagnostic Priors (Phase 4K)

Phase 4K replaces **placeholder-only** Phase 4I weighting with **metadata-informed diagnostic** scenarios over the existing Phase 4G scaled-holdout grid. No new TDF/NFW/MOND fits are run.

## Scientific framing

- **Photometry-informed scaffold** — weights use SPARC Table-1 metadata and subset context, not fitted M/L.
- **Morphology-aware diagnostic prior** — early-type / bulge-proxy galaxies are not pushed toward extreme low `bulge_scale` without justification.
- **Central-concentration proxy** — `morphological_type`, `bulge_dominated_proxy`, and related fields guide conservative tilts.
- This is **not a final stellar-population prior** and **not bulge M/L calibration** (no explicit bulge L₃.₆).

## Scenarios (`configs/ml_priors.yaml`)

| Scenario | Role |
| --- | --- |
| `photometry_uniform_plausible` | Uniform over plausible band (baseline photometry scaffold) |
| `morphology_aware_conservative` | Morphology / bulge-proxy aware weights |
| `ngc7814_bulge_sensitivity_diagnostic` | NGC7814-only lower-bulge diagnostic |
| `canonical_anchor_prior` | Gaussian anchor at disk=bulge=1.0 |

## Commands

```bash
python3 scripts/build_photometry_informed_ml_priors.py
python3 scripts/apply_photometry_informed_prior_weighting.py
```

## Outputs

- `outputs/tables/sparc_photometry_informed_prior_weights.csv`
- `outputs/tables/sparc_photometry_prior_weighted_summary.csv`
- `outputs/tables/ngc7814_photometry_prior_interpretation.csv`
- `outputs/reports/sparc_photometry_informed_prior_report.md`
- Figures under `outputs/figures/sparc_subset/`

Phase 4G/4H/4I/4J outputs are **not** overwritten.
