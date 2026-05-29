# Failure-Mode Analysis (Phase 4A)

## Scope

Six-galaxy controlled SPARC subset only. This document summarizes honest success and failure modes after Phase 3B (TDF knot fitting) and Phase 3C (robustness / holdout audit).

## Summary

| Classification | Count | Galaxies |
| --- | ---: | --- |
| robust_tdf_success | 5 | DDO154, IC2574, NGC2403, NGC3198, NGC6503 |
| tdf_failure_mode | 1 | NGC7814 |

## Robust success cases

For five galaxies, TDF knot models (often tdf_5knot in-sample) outperform or match tested baselines on **even/odd holdout test RMSE**, in addition to strong in-sample AIC/BIC. Language should remain conditional:

- fixed SPARC baryonic decomposition (no M/L fitting)
- fixed K_tau convention
- six-galaxy subset only
- rotation-curve consistency test, not lensing or cosmology

Prefer **tdf_3knot** for primary reporting when higher knot counts show in-sample gains but holdout sensitivity suggests flexibility risk.

## NGC7814 failure mode

NGC7814 is retained in the benchmark as an explicit failure mode.

- **In-sample:** TDF knot models (especially tdf_5knot) achieve the best AIC/BIC among compared models.
- **Holdout:** NFW refit and MOND fit-a0 achieve much lower test RMSE than TDF (tdf_3knot holdout RMSE ~156 km/s vs NFW ~25 km/s on even/odd split).
- **Pathology:** tdf_4knot shows negative-v² regions and catastrophic in-sample RMSE (~123 km/s).

Do not claim that TDF works for NGC7814 under holdout validation.

## Claim boundaries

See `outputs/tables/sparc_claim_traceability_matrix.csv` and `outputs/reports/sparc_claim_traceability_report.md`.

**Supported with caveats:** direct τ reconstruction (diagnostic); in-sample TDF vs baselines on subset; holdout advantage in 5/6 galaxies.

**Not supported:** full SPARC validation; NGC7814 holdout success; lensing confirmation.

**Prohibited:** dark matter disproof; ΛCDM replacement.
