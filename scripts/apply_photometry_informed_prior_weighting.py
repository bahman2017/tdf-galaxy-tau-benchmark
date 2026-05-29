from __future__ import annotations

import argparse
from pathlib import Path

from tdf_galaxy_tau.analysis.ml_priors import TARGET_GALAXY
from tdf_galaxy_tau.analysis.photometry_informed_priors import (
    PHOTOMETRY_PRIOR_LOGIC_VERSION,
    build_ngc7814_photometry_prior_interpretation,
    compute_photometry_prior_weighted_summary,
    plot_ngc7814_photometry_prior_distribution,
    plot_photometry_prior_model_support,
    write_photometry_informed_prior_report,
)
import pandas as pd

from tdf_galaxy_tau.analysis.ml_priors import load_ml_priors_config

SUMMARY_OUT = Path("outputs/tables/sparc_photometry_prior_weighted_summary.csv")
NGC_OUT = Path("outputs/tables/ngc7814_photometry_prior_interpretation.csv")
REPORT_OUT = Path("outputs/reports/sparc_photometry_informed_prior_report.md")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4K: apply photometry-informed priors to Phase 4G grid (no fits)"
    )
    parser.add_argument(
        "--comparison",
        default="outputs/tables/sparc_ml_scaled_model_comparison.csv",
    )
    parser.add_argument(
        "--weights",
        default="outputs/tables/sparc_photometry_informed_prior_weights.csv",
    )
    parser.add_argument(
        "--post-ml",
        default="outputs/tables/sparc_post_ml_results_summary_table.csv",
    )
    parser.add_argument("--priors", default="configs/ml_priors.yaml")
    args = parser.parse_args()

    comparison = pd.read_csv(args.comparison)
    weights = pd.read_csv(args.weights)
    config = load_ml_priors_config(args.priors)
    subset_ctx = pd.read_csv("outputs/tables/sparc_subset_photometry_context.csv")

    summary = compute_photometry_prior_weighted_summary(comparison, weights)
    ngc = build_ngc7814_photometry_prior_interpretation(summary, post_ml_path=args.post_ml)

    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_OUT, index=False)
    ngc.to_csv(NGC_OUT, index=False)
    write_photometry_informed_prior_report(
        REPORT_OUT,
        weights=weights,
        summary=summary,
        ngc_interp=ngc,
        subset_ctx=subset_ctx,
        config=config,
    )
    plot_ngc7814_photometry_prior_distribution(
        weights, Path("outputs/figures/sparc_subset/ngc7814_photometry_prior_weight_distribution.png")
    )
    plot_photometry_prior_model_support(
        summary, Path("outputs/figures/sparc_subset/photometry_prior_model_support_summary.png")
    )

    anchor = ngc[ngc["scenario_name"] == "canonical_anchor_prior"]
    if not anchor.empty:
        row = anchor.iloc[0]
        print(f"Wrote {SUMMARY_OUT} ({len(summary)} rows)")
        print(f"Wrote {NGC_OUT}")
        print(f"Wrote {REPORT_OUT}")
        print(
            f"{TARGET_GALAXY} canonical_anchor: {row['canonical_result']}; "
            f"primary={row['primary_tdf_3knot_prior_result']}; "
            f"sensitivity={row['sensitivity_tdf_5knot_prior_result']}"
        )
    print(f"Logic version: {PHOTOMETRY_PRIOR_LOGIC_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
