# SPARC Claim Traceability Report (Phase 4A)

This matrix maps scientific claims to evidence tables and conservative language boundaries. Dark matter is **not** disproven. Full-SPARC validation and lensing are **future work**.

| ID | Status | Claim |
| --- | --- | --- |
| A | supported | TDF direct radial reconstruction can be generated for selected SPARC galaxies. |
| B | supported_with_caveat | TDF knot models outperform tested baselines in-sample on six selected galaxies. |
| C | partially_supported | TDF knot models outperform NFW/MOND under holdout validation. |
| D | not_supported | TDF works for NGC7814. |
| E | not_supported_future_work | TDF validates on full SPARC. |
| F | prohibited | TDF disproves dark matter. |
| G | prohibited | TDF replaces ΛCDM. |
| H | not_tested_future_work | TDF lensing predictions are confirmed. |

## Claim details

### Claim A

**Claim:** TDF direct radial reconstruction can be generated for selected SPARC galaxies.

- **Status:** `supported`
- **Supporting tables:** sparc_subset_tau_profiles.csv; outputs/tables/sparc_subset_tau_profiles.csv
- **Supporting figures:** outputs/figures/sparc_subset/*_tau_*.png
- **Caveats:** Phase 2A diagnostic reconstruction only; not an AIC/BIC fitted model.
- **Allowed language:** direct radial τ reconstruction generated for selected galaxies
- **Prohibited language:** universal τ-profile discovered; full-SPARC validation

### Claim B

**Claim:** TDF knot models outperform tested baselines in-sample on six selected galaxies.

- **Status:** `supported_with_caveat`
- **Supporting tables:** sparc_full_model_comparison.csv; sparc_best_model_summary.csv
- **Supporting figures:** outputs/figures/sparc_subset/*_full_model_rotation_comparison.png
- **Caveats:** Often tdf_5knot wins in-sample; higher knot count may overfit. Fixed baryons, fixed K_tau, six-galaxy subset.
- **Allowed language:** competitive; outperforms tested baselines in this controlled subset (in-sample)
- **Prohibited language:** validated on SPARC; universal discovery

### Claim C

**Claim:** TDF knot models outperform NFW/MOND under holdout validation.

- **Status:** `partially_supported`
- **Supporting tables:** sparc_tdf_holdout_validation.csv; sparc_tdf_robust_best_model_summary.csv
- **Supporting figures:** outputs/reports/sparc_tdf_robustness_audit_report.md
- **Caveats:** 5 of 6 galaxies on even/odd holdout test RMSE; NGC7814 is a clear failure mode.
- **Allowed language:** 5 of 6 holdout success; partially supported on this subset
- **Prohibited language:** always outperforms; validated on SPARC

### Claim D

**Claim:** TDF works for NGC7814.

- **Status:** `not_supported`
- **Supporting tables:** sparc_failure_mode_summary.csv; sparc_tdf_holdout_validation.csv
- **Supporting figures:** outputs/figures/sparc_subset/NGC7814_full_model_rotation_comparison.png
- **Caveats:** In-sample TDF metrics are strong; holdout fails. NFW/MOND better on test RMSE.
- **Allowed language:** NGC7814 is an honest failure mode under holdout
- **Prohibited language:** TDF works for NGC7814; TDF validates this galaxy

### Claim E

**Claim:** TDF validates on full SPARC.

- **Status:** `not_supported_future_work`
- **Supporting tables:** sparc_subset_selection.csv
- **Supporting figures:** none
- **Caveats:** Only six galaxies in controlled subset.
- **Allowed language:** future work; subset-only benchmark
- **Prohibited language:** TDF is validated on SPARC; SPARC validates TDF

### Claim F

**Claim:** TDF disproves dark matter.

- **Status:** `prohibited`
- **Supporting tables:** none
- **Supporting figures:** none
- **Caveats:** Rotation-curve consistency test only; no cosmological claim.
- **Allowed language:** does not disprove dark matter
- **Prohibited language:** dark matter is disproven; DM is wrong

### Claim G

**Claim:** TDF replaces ΛCDM.

- **Status:** `prohibited`
- **Supporting tables:** none
- **Supporting figures:** none
- **Caveats:** Empirical rotation-curve baselines only.
- **Allowed language:** does not replace ΛCDM
- **Prohibited language:** ΛCDM is replaced; replaces standard cosmology

### Claim H

**Claim:** TDF lensing predictions are confirmed.

- **Status:** `not_tested_future_work`
- **Supporting tables:** none
- **Supporting figures:** none
- **Caveats:** No lensing module in this repository phase.
- **Allowed language:** lensing not tested; future work
- **Prohibited language:** lensing confirmed; lensing validates TDF

