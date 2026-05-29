# Paper-Ready Claims (Controlled Subset)

Use this document with `outputs/tables/sparc_claim_traceability_matrix_updated.csv` (Phase 4H; includes claims I–N after M/L sensitivity). Phase 4B/4H — **language guardrail only**; no new fits after 4G.

## Headline (allowed)

> On a **controlled six-galaxy subset** of SPARC rotation curves, TDF knot models achieve **rotation-curve consistency** competitive with or better than tested NFW refit and MOND fit-a0 baselines under **even/odd holdout** in **5 of 6** cases at **fixed canonical SPARC baryons**, **conditional on fixed K_tau**, with **one explicit canonical failure mode** (NGC7814). That failure is **baryonic-decomposition-sensitive** under **diagnostic M/L scaling** (Phases 4F–4G) but is **not removed** at canonical decomposition and is **not** a final M/L calibration.

## Primary model recommendation

- **Report as primary TDF model:** `tdf_3knot` (conservative flexibility).
- **Cite with caution:** `tdf_5knot` (often best in-sample and holdout RMSE in success cases; greater overfitting risk).
- **Do not lead with:** `tdf_4knot` (negative-v² pathology on NGC7814).

## Baseline framing

- **NFW refit** is the strongest non-TDF baseline overall and **wins NGC7814 holdout**.
- **MOND fit-a0** is a serious empirical rotation-curve baseline, not a cosmological claim.

## Claims A–H (quick reference)

| ID | Claim | Status | Use in prose |
| --- | --- | --- | --- |
| A | Direct radial τ reconstruction for selected galaxies | **Supported** | Diagnostic Phase 2A only |
| B | TDF knots outperform tested baselines in-sample (6 galaxies) | **Supported with caveat** | Often tdf_5knot; subset only |
| C | TDF knots outperform NFW/MOND on holdout | **Partially supported** | **5 of 6 holdout success** |
| D | TDF works for NGC7814 | **Not supported** | State as **failure mode** |
| E | TDF validates on full SPARC | **Not supported / future work** | Never imply full catalog |
| F | TDF disproves dark matter | **Prohibited** | State DM **not** disproven |
| G | TDF replaces ΛCDM | **Prohibited** | No cosmology replacement |
| H | TDF lensing confirmed | **Not tested / future work** | Lensing **not tested** |
| I | NGC7814 canonical TDF holdout failure (fixed baryons) | **Supported** | **Canonical failure** retained |
| J | NGC7814 sensitive to bulge/disk M/L scaling | **Supported (diagnostic)** | **Diagnostic M/L scaling** only |
| K | M/L scaling definitively fixes NGC7814 | **Not supported** | Do not say “solved” |
| L | TDF uniquely benefits from M/L scaling | **Not supported** | NFW/MOND improve too (4G) |
| M | TDF stable in five success galaxies (plausible M/L) | **Supported with caveat** | Plausible band only |
| N | Photometry-calibrated M/L model exists | **Not supported / future work** | Grid is diagnostic |
| O | Photometry-informed priors required before calibrated M/L claims | **Supported** | Phase 4I scaffold; 4K diagnostic weights |
| P | SPARC photometry metadata supports treating NGC7814 as structurally distinct from five robust TDF-success galaxies | **Supported (metadata context)** | Not causal proof; Phase 4J/4K |
| Q | Photometry-informed priors constitute final calibrated M/L priors | **Not supported** | Phase 4K explicit rejection |

## Post-M/L allowed phrases (Phase 4H)

- canonical failure
- baryonic-decomposition-sensitive failure
- diagnostic M/L scaling
- fair scaled comparison
- TDF remains stable in the five success galaxies
- NGC7814 is recoverable under some plausible lower-bulge settings, but the result is not a final M/L calibration

## Post-M/L prohibited phrases (Phase 4H)

- NGC7814 is solved
- TDF is validated (on SPARC / globally)
- dark matter is disproven
- ΛCDM is replaced
- M/L calibration confirms TDF
- NFW/MOND fail after scaling
- lensing is confirmed

## Required disclaimers (every external summary)

1. **Dark matter:** This benchmark does **not** disprove dark matter.
2. **ΛCDM:** Results do **not** replace ΛCDM as a cosmological framework.
3. **Scope:** **Controlled six-galaxy subset** only — **not** full-SPARC validation.
4. **Lensing:** **Not tested** in this repository phase.
5. **τ universality:** No **universal τ-profile** was discovered.
6. **NGC7814:** Report as **one explicit canonical failure mode**; do not hide or drop. M/L sensitivity is **diagnostic** (4F/4G); fair scaled comparison shows baselines improve too.
7. **M/L:** No **final** or **photometry-calibrated** M/L model in this repository phase.

## Allowed phrases (copy-safe)

- rotation-curve consistency
- controlled six-galaxy subset
- 5 of 6 holdout success
- one explicit failure mode
- conditional on fixed baryonic inputs and fixed K_tau
- promising / competitive on this controlled subset
- outperforms tested baselines in this controlled subset (where tables support it)
- future work: full SPARC, **photometry ingestion into M/L priors** (beyond Phase 4I placeholders), K_tau calibration, 2D τ-map, and lensing only after frozen τ-map validation
- diagnostic prior-weighted summary (Phase 4I; not calibration)
- baryonic-decomposition-sensitive failure (NGC7814; diagnostic only)
- fair scaled comparison (Phase 4G)

## Prohibited phrases (never use)

- dark matter is disproven / DM is wrong
- ΛCDM is replaced / replaces standard cosmology
- TDF is validated on SPARC / SPARC validates TDF
- lensing confirmed / lensing validates TDF
- universal τ-profile discovered
- TDF works for NGC7814 (under holdout)
- NGC7814 is solved / M/L scaling fixes NGC7814
- M/L calibration confirms TDF
- NFW/MOND fail after scaling
- TDF uniquely benefits from M/L scaling

## Conditions (methods boilerplate)

Results are **conditional on**:

- fixed SPARC baryonic decomposition (`v_bar` from gas+disk+bulge as provided)
- fixed **K_tau** (not fitted)
- no M/L, distance, or inclination fitting
- six-galaxy subset selection (Phase 1B)
- 1D rotation curves only (no 2D τ-map, no lensing)

## Controlled expansion cohort (Phases 5B–5E) — claims C20-A – C20-H

### Headline (expansion_20, allowed)

> In the pre-registered controlled **expansion_20** cohort, the primary conservative **tdf_3knot** model achieves **robust holdout success in 15 of 20** galaxies. **Three** additional galaxies show **sensitivity-recovery** where **tdf_5knot** improves substantially but is **not** counted as primary success. **NGC7814** remains the only **all-TDF** holdout failure, and **UGC00128** remains a **mixed near-tie** case.

### Claims C20 quick reference

| ID | Claim | Status |
| --- | --- | --- |
| C20-A | expansion_20 processed reproducibly | **Supported** |
| C20-B | tdf_3knot robust success 15/20 | **Supported with caveat** |
| C20-C | tdf_5knot sensitivity-recovery | **Supported (sensitivity only)** |
| C20-D | NGC7814 all-TDF failure | **Supported** |
| C20-E | Full SPARC validation | **Not supported** |
| C20-F | Dark matter disproven | **Prohibited** |
| C20-G | Lensing confirmed | **Not tested** |
| C20-H | Universal τ-profile | **Not supported** |

### Expansion disclaimers (required)

1. **Scope:** **expansion_20** controlled cohort only — **not** full-SPARC validation.
2. **Primary model:** **tdf_3knot** only for robust success counts; **tdf_5knot** is sensitivity/high-flexibility.
3. **Sensitivity-recovery:** NGC5055, UGC05253, UGC12506 — **do not** count as primary wins.
4. **NGC7814:** Canonical all-TDF failure; **UGC00128:** mixed near-tie.
5. **Dark matter / ΛCDM / lensing / τ universality:** Same prohibitions as six-galaxy subset (claims F, G, H analogues).
6. **M/L:** No final or photometry-calibrated M/L calibration.

See `docs/controlled_expansion_results.md` and `outputs/reports/controlled_expansion20_final_audit_report.md`.

## Supporting tables and reports

- `outputs/tables/controlled_expansion_comparison_summary.csv`
- `outputs/tables/controlled_expansion_final_claims.csv`
- `outputs/reports/controlled_expansion20_final_audit_report.md`
- `outputs/tables/sparc_publication_summary_table.csv`
- `outputs/tables/sparc_failure_mode_summary.csv`
- `outputs/tables/sparc_claim_traceability_matrix_updated.csv`
- `outputs/tables/sparc_post_ml_results_summary_table.csv`
- `outputs/reports/sparc_post_ml_claim_reconciliation_report.md`
- `outputs/reports/sparc_post_ml_controlled_subset_results_summary.md`
- `outputs/reports/sparc_controlled_subset_results_summary.md`
- `docs/results_summary.md`
