# Controlled SPARC Subset Expansion Protocol (Phase 5A)

Phase 5A **pre-registers** selection criteria for expanding the six-galaxy controlled subset. It does **not** run TDF/NFW/MOND fits, does **not** validate TDF on full SPARC, and does **not** add lensing.

## Cohorts

| Cohort | Total galaxies | New galaxies beyond original six |
| --- | --- | --- |
| **expansion_12** | 12 | 6 |
| **expansion_20** | 20 | 14 |

The six original galaxies (DDO154, IC2574, NGC2403, NGC3198, NGC6503, NGC7814) are always retained. **expansion_12** additions are a subset of **expansion_20** additions.

## Pre-registered criteria

Defined in `configs/subset_expansion.yaml`:

- Minimum radial points and coverage (same spirit as Phase 1B)
- Finite baryonic and velocity columns; positive r, v_obs, v_err
- SPARC photometry metadata required (Type, inclination, L3.6, Rdisk)
- Morphology diversity quotas (disk-dominated, intermediate, early/bulge)
- Selection score uses **QC + photometry only** — no TDF holdout outcomes

## Build protocol tables

```bash
python3 scripts/plan_sparc_subset_expansion.py
```

## Outputs

- `outputs/tables/sparc_subset_expansion_candidates.csv`
- `outputs/tables/sparc_subset_expansion_plan.csv`
- `outputs/reports/sparc_subset_expansion_protocol_report.md`

## Before fitting (Phase 5B+)

1. Freeze `configs/subset_expansion.yaml`.
2. Confirm expansion list with collaborators.
3. Re-run claim traceability; do not imply full-catalog validation.
