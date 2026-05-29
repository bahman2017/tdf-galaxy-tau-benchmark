from __future__ import annotations

import argparse
from pathlib import Path

from tdf_galaxy_tau.analysis.ml_priors import TARGET_GALAXY, run_ml_prior_weighting_audit

WEIGHT_AUDIT = Path("outputs/tables/ml_prior_weight_audit.csv")
BREAKDOWN = Path("outputs/tables/ngc7814_prior_scenario_breakdown.csv")
AUDIT_REPORT = Path("outputs/reports/ml_prior_weighting_audit_report.md")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4I-Audit: M/L prior weighting verification")
    parser.add_argument(
        "--comparison",
        default="outputs/tables/sparc_ml_scaled_model_comparison.csv",
    )
    parser.add_argument(
        "--post-ml",
        default="outputs/tables/sparc_post_ml_results_summary_table.csv",
    )
    parser.add_argument("--priors", default="configs/ml_priors.yaml")
    parser.add_argument(
        "--no-regenerate",
        action="store_true",
        help="Skip regenerating Phase 4I summary tables",
    )
    args = parser.parse_args()

    result = run_ml_prior_weighting_audit(
        comparison_path=args.comparison,
        post_ml_path=args.post_ml,
        priors_config_path=args.priors,
        weight_audit_out=WEIGHT_AUDIT,
        breakdown_out=BREAKDOWN,
        audit_report_out=AUDIT_REPORT,
        regenerate_phase4i=not args.no_regenerate,
    )

    print(f"Wrote {WEIGHT_AUDIT} ({len(result['weight_audit'])} rows)")
    print(f"Wrote {BREAKDOWN} ({len(result['breakdown'])} rows)")
    print(f"Wrote {AUDIT_REPORT}")
    print(f"Weight sums per scenario: {result['weight_sums']}")
    print(f"Correction applied (Phase 4I regen): {result['correction_applied']}")
    uni = result["ngc_interp"][result["ngc_interp"]["prior_scenario"] == "uniform_plausible_band"].iloc[0]
    con = result["ngc_interp"][
        result["ngc_interp"]["prior_scenario"] == "conservative_bulge_downweight_test"
    ].iloc[0]
    print(
        f"{TARGET_GALAXY} uniform: {uni['interpretation_category']} "
        f"(tdf3_win={uni['tdf_3knot_fraction_prior_weight_wins']:.2f}, "
        f"tdf5_win={uni['tdf_5knot_fraction_prior_weight_wins']:.2f})"
    )
    print(
        f"{TARGET_GALAXY} conservative: {con['interpretation_category']} "
        f"(tdf3_win={con['tdf_3knot_fraction_prior_weight_wins']:.2f}, "
        f"tdf5_win={con['tdf_5knot_fraction_prior_weight_wins']:.2f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
