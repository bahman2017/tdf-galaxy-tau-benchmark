from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.validation.failure_modes import (
    build_failure_mode_summary,
    write_failure_mode_report,
)

SUMMARY_TABLE = Path("outputs/tables/sparc_failure_mode_summary.csv")
REPORT_PATH = Path("outputs/reports/sparc_failure_mode_analysis_report.md")


def _load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4A SPARC failure-mode analysis")
    parser.add_argument(
        "--tables-dir",
        default="outputs/tables",
        help="Directory containing Phase 3 output tables",
    )
    parser.add_argument(
        "--subset",
        default="outputs/tables/sparc_subset_selection.csv",
    )
    args = parser.parse_args()

    tdir = Path(args.tables_dir)
    summary = build_failure_mode_summary(
        full_comparison=_load(tdir / "sparc_full_model_comparison.csv"),
        best_model=_load(tdir / "sparc_best_model_summary.csv"),
        robust_best=_load(tdir / "sparc_tdf_robust_best_model_summary.csv"),
        holdout=_load(tdir / "sparc_tdf_holdout_validation.csv"),
        ktau=_load(tdir / "sparc_tdf_ktau_sensitivity.csv"),
        bounds=_load(tdir / "sparc_tdf_bounds_sensitivity.csv"),
        smooth=_load(tdir / "sparc_tdf_smoothness_diagnostics.csv"),
        tdf_comparison=_load(tdir / "sparc_tdf_knot_model_comparison.csv"),
        subset_selection=_load(args.subset),
    )

    SUMMARY_TABLE.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_TABLE, index=False)
    write_failure_mode_report(REPORT_PATH, summary)

    n_robust = int((summary["failure_mode_classification"] == "robust_tdf_success").sum())
    n_fail = int((summary["failure_mode_classification"] == "tdf_failure_mode").sum())
    print(f"Wrote failure-mode summary: {SUMMARY_TABLE}")
    print(f"Wrote report: {REPORT_PATH}")
    print(f"robust_tdf_success: {n_robust}; tdf_failure_mode: {n_fail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
