# SPARC Controlled Subset Expansion Protocol Report (Phase 5A)

> This phase pre-registers expansion criteria only. It does not run new fits, does not validate TDF on full SPARC, does not disprove dark matter, and does not include lensing.

## Objective

Pre-register deterministic criteria for expanding the six-galaxy controlled subset to **12** and **20** galaxies before any new TDF/NFW/MOND fitting campaign.

## Cohorts

- **expansion_12:** Original six galaxies plus six additional (twelve total). (12 total)
- **expansion_20:** Original six galaxies plus fourteen additional (twenty total). (20 total)

## Selection criteria (pre-registered)

- Minimum radial points: **12**
- Minimum radial coverage (kpc): **5.0**
- Maximum median velocity uncertainty (km/s): **20.0**
- Finite rotmod columns: ['r_kpc', 'v_obs_kms', 'v_err_kms', 'v_gas_kms', 'v_disk_kms', 'v_bulge_kms', 'v_bar_kms', 'residual_v2_kms2']
- Required photometry fields: ['morphological_type', 'inclination_deg', 'luminosity_3p6_lsun', 'disk_scale_length_kpc']
- Morphology diversity quotas (disk-dominated, intermediate, early/bulge)
- **Anti-cherry-picking:** no TDF/NFW/MOND holdout metrics in selection score

## Candidate pool

- Galaxies evaluated (excluding original six): **169**
- Eligible after QC + photometry: **94**

## Proposed expansion_12 additions (6 galaxies)

UGC02953, UGC05253, NGC5055, UGC00128, NGC0289, DDO161

## Proposed expansion_20 additions (14 galaxies)

UGC02953, UGC05253, UGC09133, UGC06787, NGC5055, UGC00128, NGC0289, UGC12506, UGC11455, NGC6015, DDO161, NGC7793, UGC07524, UGC08490

## Morphology mix (expansion_20 additions)

- intermediate: 5
- disk_dominated: 5
- early_bulge: 4

## Relationship to Phase 4M audit

Final six-galaxy audit: `outputs/tables/sparc_controlled_subset_final_status.csv` (Phase 4M complete).

## Next steps (not part of Phase 5A)

1. Review and freeze `configs/subset_expansion.yaml`.
2. Run expansion fitting pipeline only after protocol sign-off.
3. Update claim traceability; do not imply full-SPARC validation.
