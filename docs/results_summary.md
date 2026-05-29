# Results Summary — Controlled Six-Galaxy SPARC Benchmark

Phase 4B publication-style summary, updated through **Phase 4H** (post-M/L claim reconciliation). **Documentation only** — no new fits after Phase 4G. Canonical numbers trace to Phase 3B/3C and Phase 4A; M/L interpretation from Phases 4F–4G.

## Executive summary

On a **controlled six-galaxy subset** of SPARC rotation curves, TDF piecewise-linear knot models provide **rotation-curve consistency** with tested halo and MOND baselines under **fixed canonical SPARC baryonic inputs** and fixed **K_tau**. Under **even/odd holdout** test RMSE at M/L=1, TDF achieves **5 of 6 holdout success**; **NGC7814** is **one explicit canonical failure mode** where NFW refit outperforms TDF despite strong in-sample TDF metrics.

**Post-M/L (Phases 4F–4G, reconciled in 4H):** NGC7814 is a **baryonic-decomposition-sensitive failure** under **diagnostic M/L scaling**. Lowering bulge_scale reduces inner TDF holdout error sharply. Under **fair scaled comparison**, NFW and MOND improve on the same scaled baryons, so improvement is **not uniquely a TDF effect**. At some **plausible lower-bulge** settings, TDF (often **tdf_5knot**) is competitive or best — **not** a final M/L calibration. The five success galaxies remain **stable** under plausible diagnostic scaling.

**Primary conservative TDF model:** `tdf_3knot`. **Higher-flexibility reference:** `tdf_5knot` (often best in-sample and holdout RMSE in success cases, with greater overfitting risk).

This work does **not** disprove dark matter, does **not** replace ΛCDM, does **not** validate TDF on full SPARC, and does **not** test lensing.

## Scientific objective

Test whether a fixed TDF radial reconstruction law, implemented as fitted piecewise-linear **dτ/dr** knot models, can reproduce SPARC rotation curves competitively with standard empirical baselines (NFW/Burkert halos, MOND fit-a0) on a small, QC-selected subset — with honest holdout validation and explicit failure-mode reporting.

## Dataset and controlled subset

Six galaxies from Phase 1B subset selection: **DDO154, IC2574, NGC2403, NGC3198, NGC6503, NGC7814**. Data: standardized SPARC rotmod (`data/processed/sparc/sparc_rotmod_standardized.csv`). Selection rationale documented in `docs/sparc_subset_selection.md` and `outputs/tables/sparc_subset_selection.csv`.

## Models compared

| Category | Models |
| --- | --- |
| Baryonic | `baryonic_only` (fixed decomposition) |
| Halos | `nfw_refit`, `burkert_refit` (log-space multistart, Phase 3A-R) |
| MOND / RAR | `mond_fixed_a0_simple`, `mond_fit_a0_simple`, `rar_fixed` (Phase 3M) |
| TDF knots | `tdf_3knot`, `tdf_4knot`, `tdf_5knot` (Phase 3B; fixed knot radii, fixed K_tau) |

## TDF reconstruction law

Pointwise diagnostic (Phase 2A) and fitted knot form (Phase 3B):

- `v_obs²(r) = v_bar²(r) + v_τ²(r)`
- `v_τ²(r) = r · K_tau · dτ/dr`
- `dτ/dr` piecewise-linear between fixed knot radii; amplitudes fitted with bounds from diagnostic τ range.

**K_tau** is fixed (not fitted). **M/L, distance, and inclination** are not fitted.

## In-sample comparison

On all six galaxies, TDF knot models (most often **tdf_5knot**) achieve the best or among the best **AIC/BIC** versus tested baselines (`outputs/tables/sparc_full_model_comparison.csv`, `sparc_best_model_summary.csv`). This is **in-sample** only; higher knot count increases flexibility and overfitting risk relative to **tdf_3knot**.

## Holdout validation

Even/odd index holdout (Phase 3C; `sparc_tdf_holdout_validation.csv`):

- **5 of 6:** TDF knot variant (typically **tdf_5knot**) has lowest holdout test RMSE among compared models; **tdf_3knot** also beats NFW and MOND fit-a0 on holdout in these five cases.
- **1 of 6 (NGC7814):** **nfw_refit** wins holdout; TDF holdout RMSE is an order of magnitude worse than NFW/MOND.

See `outputs/tables/sparc_publication_summary_table.csv` for per-galaxy holdout RMSE.

## Failure-mode analysis

Phase 4A classification (`sparc_failure_mode_summary.csv`, `docs/failure_mode_analysis.md`):

| Classification | Galaxies |
| --- | --- |
| `robust_tdf_success` | DDO154, IC2574, NGC2403, NGC3198, NGC6503 |
| `tdf_failure_mode` | NGC7814 |

NGC7814 is retained and reported openly: strong in-sample TDF, **canonical** failed holdout at M/L=1, **tdf_4knot** negative-v² pathology, **diagnostic M/L sensitivity** (4F), **fair scaled baseline comparison** (4G).

## Post-M/L sensitivity (Phases 4F–4G)

| Topic | Finding |
| --- | --- |
| Canonical (M/L=1) | NGC7814 holdout failure **unchanged** (~156 km/s tdf_3knot vs ~25 km/s NFW) |
| Diagnostic scaling | Strong sensitivity to bulge/disk M/L; inner errors drop when bulge_scale lowered |
| Fair comparison (4G) | NFW/MOND refit on same scaled baryons; baselines improve too |
| Success galaxies | TDF holdout success **stable** under plausible diagnostic band |
| Calibration | **No** final photometry-calibrated M/L model |

See `outputs/reports/sparc_post_ml_claim_reconciliation_report.md` and `sparc_post_ml_results_summary_table.csv`.

## Claim boundaries

Authoritative matrix: `outputs/tables/sparc_claim_traceability_matrix_updated.csv` (claims A–N). Short form in `docs/paper_ready_claims.md`.

**Allowed (canonical):** rotation-curve consistency; 5 of 6 holdout success; one explicit **canonical failure** mode; fixed baryonic inputs.

**Allowed (post-M/L):** baryonic-decomposition-sensitive failure; diagnostic M/L scaling; fair scaled comparison; TDF stable in five success galaxies; recoverable under some plausible lower-bulge settings (not final calibration).

**Prohibited:** NGC7814 is solved; M/L calibration confirms TDF; TDF uniquely benefits from M/L; NFW/MOND fail after scaling; dark matter disproof; ΛCDM replacement; full-SPARC validation; lensing confirmation.

## Next required work

**Future work:** full SPARC, **photometry-informed M/L**, K_tau calibration, 2D τ-map, and lensing **only after** frozen τ-map validation.

Immediate follow-ups: prefer **tdf_3knot** in external wording; cite **tdf_5knot** only as sensitivity; expand subset only with updated claim matrix.

## Key output artifacts

| Artifact | Path |
| --- | --- |
| Publication table | `outputs/tables/sparc_publication_summary_table.csv` |
| Controlled-subset report | `outputs/reports/sparc_controlled_subset_results_summary.md` |
| Failure modes | `outputs/tables/sparc_failure_mode_summary.csv` |
| Claim guardrail | `outputs/tables/sparc_claim_traceability_matrix_updated.csv` |
| Post-M/L summary | `outputs/tables/sparc_post_ml_results_summary_table.csv` |
| Post-M/L reconciliation | `outputs/reports/sparc_post_ml_claim_reconciliation_report.md` |
