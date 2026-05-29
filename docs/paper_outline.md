# Paper Outline — TDF Controlled SPARC Benchmark

**Phase 5F-A scaffold.** Full prose deferred to later drafting phases.

## Title (working)

TDF Radial Reconstruction on a Preregistered Controlled SPARC Subset: Holdout Validation, Failure Modes, and Sensitivity-Recovery Cases

## Abstract (placeholder)

- Empirical benchmark of TDF reconstruction on preregistered subsets (12 and 20 galaxies).
- Primary model: `tdf_3knot`; sensitivity: `tdf_5knot`.
- Holdout: train-only even/odd; baselines NFW, Burkert, MOND/RAR.
- Key numbers: 15/20 robust; 3 sensitivity-recovery; NGC7814 failure; UGC00128 mixed.

## 1. Introduction

- Rotation-curve modeling context; need for explicit holdout and failure reporting.
- TDF as reconstruction framework, not cosmology replacement.
- Contributions: protocol, cohort expansion, classification taxonomy.

## 2. TDF reconstruction framework

- Residual-based τ; knot velocity model; K_τ convention.
- Primary vs sensitivity knot counts.

## 3. Controlled benchmark protocol

- Phase 5A preregistration; `sparc_subset_expansion_plan.csv`.
- Pipeline stages; no post-hoc galaxy cherry-picking.

## 4. Baselines

- Baryonic-only, NFW, Burkert, MOND/RAR (fixed/fitted a₀).

## 5. Holdout validation methodology

- Train-only refit; even/odd primary gate; optional blocked/CV splits documented.

## 6. Results

### 6.1 expansion_12

- 8 robust; 2 failure; 2 mixed (pre-5C taxonomy).

### 6.2 expansion_20

- 15 robust; 3 sensitivity-recovery; 1 failure; 1 mixed.

## 7. Failure modes and sensitivity-recovery

- NGC7814 canonical failure.
- NGC5055, UGC05253, UGC12506: knot-flexibility recovery (not primary success).

## 8. Limitations

- Subset only; fixed baryons; no lensing; no universal τ claim.

## 9. Future work

- Full SPARC, lensing, 2D maps—after protocol amendment.

## 10. Conclusion

- Bounded summary aligned with C20 claims.

## Appendices

- **A. Reproducibility** — commands, configs, data paths (`paper/README.md`).
- **B. Claim boundaries** — C20-A–H; prohibited language.

## Figure map (inventory)

| ID | Section | Status |
| --- | --- | --- |
| Fig1 | §3 | needs_composition |
| Fig2 | §6 | needs_composition |
| Fig3 | §6 | existing |
| Fig4 | §7 | existing |
| Fig5 | §7 | existing |
| Fig6 | §5–6 | needs_composition |
| Fig7 | App. B | needs_composition |

## Table map (inventory)

| ID | Section | Source |
| --- | --- | --- |
| Table1 | §3 | expansion plan CSV |
| Table2 | §5–6 | holdout validation |
| Table3 | §6–7 | failure mode summary |
| Table4 | §7 | failure diagnostics |
| Table5 | App. B | controlled_expansion_final_claims |
| Table6 | §8 | assumptions + limitations docs |

## Prohibited claims

See `docs/paper_ready_claims.md` (C20-F, C20-G, C20-H).
