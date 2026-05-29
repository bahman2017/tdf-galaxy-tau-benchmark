# SPARC Photometry-Informed M/L Prior Report (Phase 4K)

> This phase constructs diagnostic photometry-informed M/L prior weights. It does not perform final M/L calibration, does not rerun model fits, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Objective

Replace purely placeholder Phase 4I prior scenarios with **metadata-informed diagnostic** weights over the existing Phase 4G scaled-holdout grid, using Phase 4J photometry context.

## Metadata source and limitations

- Metadata ingested for prior scaffolding only; no final M/L calibration is performed.
- No explicit bulge luminosity; morphology and central-concentration proxies only.
- This is a **photometry-informed scaffold**, not a stellar-population-calibrated prior.

## Prior scenarios

- **photometry_uniform_plausible:** Uniform diagnostic weight over plausible-band Phase 4G grid cells (photometry-informed scaffold). (`uniform plausible band [disk 0.7-1.3, bulge 0.5-1.0]; no morphology tilt`)
- **morphology_aware_conservative:** Morphology-aware diagnostic prior using morphological_type and bulge_dominated_proxy; early-type systems do not auto-favor extreme low bulge_scale. (`morphological_type, bulge_dominated_proxy, central-concentration context`)
- **ngc7814_bulge_sensitivity_diagnostic:** NGC7814-only diagnostic — tests lower-bulge_scale cell support; not calibrated bulge M/L. (`NGC7814 Sa-type bulge-proxy; diagnostic lower-bulge emphasis only`)
- **canonical_anchor_prior:** Gaussian anchor at canonical disk=bulge=1.0 to preserve reference interpretation at fixed SPARC decomposition. (`canonical M/L=1 anchor; not photometry-calibrated`)

## How metadata influences weights

- **morphological_type** and **bulge_dominated_proxy** gate bulge_scale emphasis.
- Early-type / bulge-proxy systems avoid automatically favoring extreme low bulge_scale.
- Disk-dominated success galaxies emphasize disk_scale near unity.
- NGC7814 has a dedicated diagnostic scenario testing lower-bulge support.

## Six-galaxy summary

| Galaxy | Class | Bulge-dom proxy | Notes |
| --- | --- | --- | --- |
| DDO154 | robust_tdf_success | False | Disk-dominated dwarf/spiral; future priors may favor near-un... |
| NGC2403 | robust_tdf_success | False | Disk-dominated dwarf/spiral; future priors may favor near-un... |
| NGC3198 | robust_tdf_success | False | Disk-dominated dwarf/spiral; future priors may favor near-un... |
| NGC6503 | robust_tdf_success | False | Disk-dominated dwarf/spiral; future priors may favor near-un... |
| IC2574 | robust_tdf_success | False | Disk-dominated dwarf/spiral; future priors may favor near-un... |
| NGC7814 | tdf_failure_mode | True | Sa-type (Type~2), high L3.6 and SBdisk; bulge-dominated prox... |

## NGC7814 interpretation

- Sa-type (Type~2), high L3.6 and SBdisk; bulge-dominated proxy True. Supports photometry-informed downweight of bulge M/L in future priors; does not change canonical tdf_3knot failure.

### Scenario: photometry_uniform_plausible
- Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration.
- Primary tdf_3knot: `baryon_sensitive_competitive`
- Sensitivity tdf_5knot: `prior_weighted_win_fraction_elevated`
- Photometry-informed diagnostic prior only; no bulge L_3.6; not final M/L calibration. Primary conservative model is tdf_3knot.

### Scenario: morphology_aware_conservative
- Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration.
- Primary tdf_3knot: `baryon_sensitive_competitive`
- Sensitivity tdf_5knot: `prior_weighted_win_fraction_elevated`
- Photometry-informed diagnostic prior only; no bulge L_3.6; not final M/L calibration. Primary conservative model is tdf_3knot.

### Scenario: canonical_anchor_prior
- Canonical TDF holdout failure at M/L=1; primary tdf_3knot lacks prior-weighted win support. Lower-bulge cells can still lower RMSE (baryon sensitivity).
- Primary tdf_3knot: `canonical_failure_persists_under_prior`
- Sensitivity tdf_5knot: `limited_prior_support`
- Photometry-informed diagnostic prior only; no bulge L_3.6; not final M/L calibration. Primary conservative model is tdf_3knot.

### Scenario: ngc7814_bulge_sensitivity_diagnostic
- Canonical failure at M/L=1 unchanged. Under this diagnostic prior, **tdf_5knot** (higher-flexibility sensitivity) carries elevated win fraction — not primary **tdf_3knot** recovery. Not final M/L calibration.
- Primary tdf_3knot: `baryon_sensitive_competitive`
- Sensitivity tdf_5knot: `prior_weighted_win_fraction_elevated`
- Photometry-informed diagnostic prior only; no bulge L_3.6; not final M/L calibration. Primary conservative model is tdf_3knot.

## Difference: tdf_3knot vs tdf_5knot

Photometry-informed priors can increase **tdf_5knot** weighted win fraction without improving **tdf_3knot** (primary conservative model). Any recovery language must specify which TDF variant and must not imply final calibration.

## Why this is not final M/L calibration

Missing bulge L_3.6, no fitted M/L parameters, and weights are diagnostic scaffolds over a fixed Cartesian grid.

## Next required data

- Explicit bulge luminosity or stellar-population priors
- Photometry quality flags per galaxy
- Independent validation before external claims
