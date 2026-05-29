# SPARC Controlled-Subset Results Summary (Phase 4B)

**Paper-ready technical summary** for the six-galaxy TDF rotation-curve benchmark. Compiled from Phase 1–4A outputs only. **No new fits were run for this report.**

---

## Scientific objective

Evaluate **rotation-curve consistency** of the TDF radial law — implemented as fitted piecewise-linear **dτ/dr** knot models — against standard empirical baselines on a **controlled six-galaxy subset** of SPARC, with in-sample information criteria, even/odd holdout test RMSE, and explicit failure-mode reporting before any full-catalog or pattern-discovery work.

---

## Dataset and controlled subset

| Galaxy | Role in benchmark |
| --- | --- |
| DDO154 | Dwarf / low-mass disk |
| IC2574 | Dwarf irregular |
| NGC2403 | Nearby spiral |
| NGC3198 | Well-studied spiral |
| NGC6503 | Spiral |
| NGC7814 | Bulge-dominated spiral (**holdout failure mode**) |

Data pipeline: SPARC rotmod → standardized table → Phase 1B QC subset (`sparc_subset_selection.csv`). Six galaxies only; **not** representative of full SPARC.

---

## Models compared

- **Baryonic-only** (fixed `v_bar` from SPARC components)
- **NFW refit**, **Burkert refit** (Phase 3A-R; log-space multistart)
- **MOND** fixed-a0 and **MOND fit-a0**; optional RAR (Phase 3M)
- **TDF knots:** `tdf_3knot`, `tdf_4knot`, `tdf_5knot` (Phase 3B)

No new models were added in Phase 4B.

---

## TDF reconstruction law

\[
v_{\mathrm{obs}}^2(r) = v_{\mathrm{bar}}^2(r) + r\, K_\tau \,\frac{d\tau}{dr}
\]

Fitted quantities: knot amplitudes of **dτ/dr** (piecewise-linear between fixed knot radii). **K_tau** fixed from configuration. Phase 2A provides diagnostic initialization bounds only.

---

## In-sample comparison

Across all six galaxies, TDF knot models — most often **tdf_5knot** — rank best by **AIC/BIC** among models in `sparc_full_model_comparison.csv`.

**Interpretation (conservative):** Strong in-sample performance is **promising** on this subset but **conditional on fixed baryonic inputs and fixed K_tau**. Higher knot count increases flexibility; **tdf_3knot** should be treated as the **primary conservative TDF model** for reporting; **tdf_5knot** may reflect extra degrees of freedom with **overfitting risk** despite low holdout RMSE in five success cases.

---

## Holdout validation

Protocol: **even/odd index** train/test split (Phase 3C). Metric: holdout **test RMSE** (km/s).

### Aggregate result

- **TDF succeeds under holdout in 5 of 6 selected galaxies** (holdout-best model is a TDF knot variant, typically `tdf_5knot`).
- **NGC7814 is a clear TDF holdout failure mode** — holdout-best is **`nfw_refit`**, not TDF.

### Per-galaxy holdout RMSE (km/s)

| Galaxy | Classification | Holdout best | tdf_3knot | tdf_5knot | NFW refit | MOND fit-a0 | TDF holdout success |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| DDO154 | robust_tdf_success | tdf_5knot | 2.03 | 1.44 | 3.56 | 3.98 | Yes |
| IC2574 | robust_tdf_success | tdf_5knot | 2.98 | 1.73 | 6.39 | 6.29 | Yes |
| NGC2403 | robust_tdf_success | tdf_5knot | 8.66 | 3.44 | 9.76 | 14.24 | Yes |
| NGC3198 | robust_tdf_success | tdf_5knot | 10.45 | 8.24 | 12.00 | 14.34 | Yes |
| NGC6503 | robust_tdf_success | tdf_5knot | 9.33 | 4.90 | 10.14 | 12.39 | Yes |
| NGC7814 | tdf_failure_mode | nfw_refit | 155.80 | 113.25 | 24.89 | 27.85 | **No** |

Machine-readable: `outputs/tables/sparc_publication_summary_table.csv`.

In all five success cases, **tdf_3knot** also beats NFW and MOND fit-a0 on holdout RMSE (conservative TDF still competitive).

---

## Failure-mode analysis

**NGC7814** (not removed from the benchmark):

1. **In-sample:** TDF (`tdf_5knot`) best AIC/BIC — misleading if holdout is ignored.
2. **Holdout:** NFW refit ≈ 25 km/s vs tdf_3knot ≈ 156 km/s — **one explicit failure mode**.
3. **Pathology:** `tdf_4knot` negative-v² flags; catastrophic smoothness/RMSE for 4knot.
4. **Likely contributors (future work):** bulge dominance, fixed baryonic decomposition, radial/knot placement, fixed K_tau, geometry/inclination not fitted.

**NFW** remains the **strongest non-TDF baseline** and wins this galaxy on holdout. **MOND fit-a0** is competitive with NFW on NGC7814 holdout (~28 km/s).

Full narrative: `docs/failure_mode_analysis.md`, `outputs/reports/sparc_failure_mode_analysis_report.md`.

---

## Claim boundaries

| Statement | Verdict |
| --- | --- |
| TDF disproves dark matter | **Prohibited** — not supported |
| TDF replaces ΛCDM | **Prohibited** — not supported |
| TDF validated on full SPARC | **Prohibited** — subset only; **future work** |
| Lensing confirms TDF | **Prohibited** — **lensing not tested** |
| Universal τ-profile discovered | **Prohibited** — not claimed |
| TDF works for NGC7814 (holdout) | **Not supported** — report failure openly |
| 5/6 holdout success on subset | **Supported** with caveats above |

Traceability: `outputs/tables/sparc_claim_traceability_matrix.csv`, `docs/paper_ready_claims.md`.

---

## Next required work

**Future work:** full SPARC, M/L sensitivity, K_tau calibration, normalized τ-pattern discovery, 2D τ-map, and lensing **only after** frozen τ-map validation.

Near-term: NGC7814 diagnostic deep-dive; standardize external text on **tdf_3knot**; expand galaxy count only with updated holdout audit and claim matrix.

---

## Phase 4B outputs

| File | Description |
| --- | --- |
| `outputs/tables/sparc_publication_summary_table.csv` | One row per galaxy for publication tables |
| `docs/results_summary.md` | Short project results summary |
| `docs/paper_ready_claims.md` | Allowed / prohibited language |
| This report | Controlled-subset technical summary |

**Generated:** Phase 4B documentation pass (no refit).
