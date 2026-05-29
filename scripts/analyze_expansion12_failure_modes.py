from __future__ import annotations

import argparse
from pathlib import Path

from tdf_galaxy_tau.analysis.expansion12_diagnostics import (
    AUDIT_DISCLAIMER,
    run_expansion12_diagnostics,
    write_expansion12_failure_report,
)

DIAGNOSTICS_CSV = Path("outputs/tables/expansion12_failure_diagnostics.csv")
CASE_REVIEW_CSV = Path("outputs/tables/expansion12_case_review_summary.csv")
REPORT_PATH = Path("outputs/reports/expansion12_failure_mode_analysis_report.md")
FIGURES_DIR = Path("outputs/figures/sparc_subset")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 5B-Audit: expansion_12 failure/mixed-case diagnostics (no new fits)"
    )
    parser.add_argument(
        "--failure-summary",
        default="outputs/tables/expansion12_failure_mode_summary.csv",
    )
    parser.add_argument("--holdout", default="outputs/tables/expansion12_holdout_validation.csv")
    parser.add_argument("--rotmod", default="data/processed/sparc/sparc_rotmod_standardized.csv")
    parser.add_argument("--tau-profiles", default="outputs/tables/expansion12_tau_profiles.csv")
    parser.add_argument("--photometry", default="data/processed/sparc/sparc_photometry_metadata.csv")
    parser.add_argument(
        "--model-comparison",
        default="outputs/tables/expansion12_model_comparison.csv",
    )
    parser.add_argument("--figures-dir", default=str(FIGURES_DIR))
    args = parser.parse_args()

    result = run_expansion12_diagnostics(
        failure_summary_path=args.failure_summary,
        holdout_path=args.holdout,
        rotmod_path=args.rotmod,
        tau_path=args.tau_profiles,
        photometry_path=args.photometry,
        model_comparison_path=args.model_comparison,
        figures_dir=args.figures_dir,
    )

    DIAGNOSTICS_CSV.parent.mkdir(parents=True, exist_ok=True)
    result.failure_diagnostics.to_csv(DIAGNOSTICS_CSV, index=False)
    result.case_review_summary.to_csv(CASE_REVIEW_CSV, index=False)
    write_expansion12_failure_report(
        REPORT_PATH,
        diagnostics=result.failure_diagnostics,
        case_review=result.case_review_summary,
        comparison=result.ngc5055_vs_ngc7814,
        figure_paths=result.figure_paths,
    )

    print(AUDIT_DISCLAIMER)
    print(f"Wrote {DIAGNOSTICS_CSV} ({len(result.failure_diagnostics)} rows)")
    print(f"Wrote {CASE_REVIEW_CSV}")
    print(f"Wrote {REPORT_PATH}")
    for name, p in result.figure_paths.items():
        print(f"Figure {name}: {p}")
    cmp = result.ngc5055_vs_ngc7814
    print(f"NGC5055 vs NGC7814 equivalent_failure={cmp['equivalent_failure']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
