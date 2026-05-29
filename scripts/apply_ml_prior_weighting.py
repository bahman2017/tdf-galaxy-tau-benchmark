from __future__ import annotations

import argparse
from pathlib import Path

from tdf_galaxy_tau.analysis.ml_priors import TARGET_GALAXY, run_ml_prior_weighting

SUMMARY_CSV = Path("outputs/tables/sparc_ml_prior_weighted_summary.csv")
NGC_CSV = Path("outputs/tables/ngc7814_ml_prior_weighted_interpretation.csv")
REPORT = Path("outputs/reports/sparc_ml_prior_framework_report.md")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4I diagnostic M/L prior weighting (no new fits)")
    parser.add_argument(
        "--comparison",
        default="outputs/tables/sparc_ml_scaled_model_comparison.csv",
    )
    parser.add_argument(
        "--post-ml",
        default="outputs/tables/sparc_post_ml_results_summary_table.csv",
    )
    parser.add_argument("--priors", default="configs/ml_priors.yaml")
    args = parser.parse_args()

    summary, ngc = run_ml_prior_weighting(
        comparison_path=args.comparison,
        post_ml_path=args.post_ml,
        priors_config_path=args.priors,
        summary_out=SUMMARY_CSV,
        ngc_out=NGC_CSV,
        report_out=REPORT,
    )

    row = ngc[ngc["prior_scenario"] == "uniform_plausible_band"].iloc[0]
    print(f"Wrote {SUMMARY_CSV} ({len(summary)} rows)")
    print(f"Wrote {NGC_CSV}")
    print(f"Wrote {REPORT}")
    print(
        f"{TARGET_GALAXY} uniform_plausible_band: {row['interpretation_category']} "
        f"(tdf_3knot_win={row['tdf_3knot_fraction_prior_weight_wins']:.2f}, "
        f"tdf_5knot_win={row['tdf_5knot_fraction_prior_weight_wins']:.2f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
