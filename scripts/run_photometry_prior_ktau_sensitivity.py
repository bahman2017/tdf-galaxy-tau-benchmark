from __future__ import annotations

import argparse
from pathlib import Path

from tdf_galaxy_tau.analysis.ktau_sensitivity import (
    TARGET_GALAXY,
    load_ktau_sensitivity_config,
    run_photometry_prior_ktau_sensitivity,
)

SUMMARY_OUT = Path("outputs/tables/sparc_ktau_sensitivity_summary.csv")
NGC_OUT = Path("outputs/tables/ngc7814_ktau_sensitivity.csv")
REPORT_OUT = Path("outputs/reports/sparc_ktau_sensitivity_report.md")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4L: K_tau sensitivity on photometry-informed M/L harness (TDF refit only)"
    )
    parser.add_argument("--rotmod", default="data/processed/sparc/sparc_rotmod_standardized.csv")
    parser.add_argument("--subset", default="outputs/tables/sparc_subset_selection.csv")
    parser.add_argument(
        "--phase4g",
        default="outputs/tables/sparc_ml_scaled_model_comparison.csv",
    )
    parser.add_argument(
        "--weights",
        default="outputs/tables/sparc_photometry_informed_prior_weights.csv",
    )
    parser.add_argument("--recon", default="configs/reconstruction.yaml")
    parser.add_argument(
        "--include-optional-ktau",
        action="store_true",
        help="Also test K_tau in {0.25, 4.0}",
    )
    args = parser.parse_args()

    kt_cfg = load_ktau_sensitivity_config(args.recon)
    summary, ngc = run_photometry_prior_ktau_sensitivity(
        rotmod_path=args.rotmod,
        subset_path=args.subset,
        phase4g_path=args.phase4g,
        weights_path=args.weights,
        recon_path=args.recon,
        summary_out=SUMMARY_OUT,
        ngc_out=NGC_OUT,
        report_out=REPORT_OUT,
        include_optional_ktau=args.include_optional_ktau,
    )

    k_vals = kt_cfg["k_tau_values"]
    if args.include_optional_ktau:
        from tdf_galaxy_tau.analysis.ktau_sensitivity import OPTIONAL_KTAU_VALUES

        k_vals = sorted(set(k_vals) | set(OPTIONAL_KTAU_VALUES))

    anchor = ngc[
        (ngc["scenario_name"] == "canonical_anchor_prior")
        & (ngc["K_tau"] == kt_cfg["reference_k_tau"])
    ]
    print(f"K_tau values: {k_vals}")
    print(f"Wrote {SUMMARY_OUT} ({len(summary)} rows)")
    print(f"Wrote {NGC_OUT}")
    print(f"Wrote {REPORT_OUT}")
    if not anchor.empty:
        row = anchor.iloc[0]
        print(
            f"{TARGET_GALAXY} @ K_tau={row['K_tau']}: {row['canonical_result']}; "
            f"5knot recovery survives: {row['tdf_5knot_diagnostic_recovery_survives_ktau']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
