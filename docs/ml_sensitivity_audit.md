# M/L Sensitivity Audit (Phase 4F)

## Purpose

Diagnostic test of whether TDF holdout results — especially **NGC7814** inner failure — change when disk and bulge stellar mass-to-light contributions are scaled in the fixed SPARC baryonic decomposition.

**Not** a final M/L calibration or photometric fit.

## Scaling law

\[
v_{\mathrm{bar,scaled}}^2 = v_{\mathrm{gas}}^2 + s_{\mathrm{disk}}\, v_{\mathrm{disk}}^2 + s_{\mathrm{bulge}}\, v_{\mathrm{bulge}}^2
\]

Same signed-square convention as Phase 1A (`sparc_rotmod_parser`). Gas is not scaled.

## Grid

- disk_scale: 0.5, 0.7, 1.0, 1.3  
- bulge_scale: 0.2, 0.5, 0.7, 1.0, 1.3  

Plausible diagnostic band: disk ∈ [0.7, 1.3], bulge ∈ [0.5, 1.0].

## Protocol

Per (galaxy, scale, model): reconstruct τ with τ(r_min)=0; even/odd train-only TDF holdout; regional RMSE.

NFW/MOND comparisons use **canonical** Phase 3C holdout at default baryons (not re-scaled in this phase).

## Run

```bash
python3 scripts/run_sparc_ml_sensitivity_audit.py
```

## Outputs

- `outputs/tables/sparc_ml_sensitivity_summary.csv`
- `outputs/tables/ngc7814_ml_sensitivity_detail.csv`
- `outputs/tables/sparc_ml_sensitivity_holdout_comparison.csv`
- `outputs/reports/sparc_ml_sensitivity_audit_report.md`

## Phase 4H reconciliation

Claims **I** (canonical failure) and **J** (diagnostic M/L sensitivity) are recorded in `outputs/tables/sparc_claim_traceability_matrix_updated.csv`. Fair NFW/MOND comparison is Phase 4G (`docs/ml_scaled_baseline_comparison.md`). No new fits in 4H.
