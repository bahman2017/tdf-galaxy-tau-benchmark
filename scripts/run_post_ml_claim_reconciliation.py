from __future__ import annotations

import argparse
from pathlib import Path

from tdf_galaxy_tau.analysis.post_ml_claim_reconciliation import run_post_ml_claim_reconciliation

UPDATED_MATRIX = Path("outputs/tables/sparc_claim_traceability_matrix_updated.csv")
POST_ML_TABLE = Path("outputs/tables/sparc_post_ml_results_summary_table.csv")
RECON_REPORT = Path("outputs/reports/sparc_post_ml_claim_reconciliation_report.md")
SUBSET_SUMMARY = Path("outputs/reports/sparc_post_ml_controlled_subset_results_summary.md")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4H post-M/L claim reconciliation (no new fits)")
    parser.add_argument(
        "--publication",
        default="outputs/tables/sparc_publication_summary_table.csv",
    )
    parser.add_argument(
        "--ml-holdout",
        default="outputs/tables/sparc_ml_sensitivity_holdout_comparison.csv",
    )
    parser.add_argument(
        "--scaled-best",
        default="outputs/tables/sparc_ml_scaled_best_model_summary.csv",
    )
    parser.add_argument(
        "--base-matrix",
        default="outputs/tables/sparc_claim_traceability_matrix.csv",
    )
    args = parser.parse_args()

    post_ml, matrix = run_post_ml_claim_reconciliation(
        publication_path=args.publication,
        ml_holdout_path=args.ml_holdout,
        scaled_best_path=args.scaled_best,
        base_matrix_path=args.base_matrix,
        updated_matrix_path=UPDATED_MATRIX,
        post_ml_table_path=POST_ML_TABLE,
        reconciliation_report_path=RECON_REPORT,
        subset_summary_path=SUBSET_SUMMARY,
    )

    ngc = post_ml[post_ml["galaxy_id"] == "NGC7814"].iloc[0]
    print(f"Wrote {POST_ML_TABLE} ({len(post_ml)} rows)")
    print(f"Wrote {UPDATED_MATRIX} ({len(matrix)} claims)")
    print(f"Wrote {RECON_REPORT}")
    print(f"Wrote {SUBSET_SUMMARY}")
    print(
        f"NGC7814: canonical tdf_3knot={ngc['canonical_tdf_3knot_rmse']} "
        f"status={ngc['claim_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
