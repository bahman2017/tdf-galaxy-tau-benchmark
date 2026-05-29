from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.analysis.ngc7814_diagnostics import (
    TARGET_GALAXY,
    _ngc7814_checks,
    run_ngc7814_diagnostics,
    write_ngc7814_failure_report,
)

FAILURE_CSV = Path("outputs/tables/ngc7814_failure_diagnostics.csv")
VS_SUCCESS_CSV = Path("outputs/tables/ngc7814_vs_success_group_diagnostics.csv")
REPORT_PATH = Path("outputs/reports/ngc7814_failure_mode_report.md")
FIGURES_DIR = Path("outputs/figures/sparc_subset")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4D NGC7814 failure-mode diagnostic deep-dive")
    parser.add_argument("--rotmod", default="data/processed/sparc/sparc_rotmod_standardized.csv")
    parser.add_argument("--tau-profiles", default="outputs/tables/sparc_subset_tau_profiles.csv")
    parser.add_argument("--knot-params", default="outputs/tables/sparc_tdf_knot_fit_parameters.csv")
    parser.add_argument("--outliers", default="outputs/tables/sparc_tau_pattern_outlier_scores.csv")
    parser.add_argument("--holdout", default="outputs/tables/sparc_tdf_holdout_validation.csv")
    parser.add_argument("--smoothness", default="outputs/tables/sparc_tdf_smoothness_diagnostics.csv")
    parser.add_argument("--figures-dir", default=str(FIGURES_DIR))
    args = parser.parse_args()

    rotmod = pd.read_csv(args.rotmod)
    tau_profiles = pd.read_csv(args.tau_profiles)
    knot_params = pd.read_csv(args.knot_params)
    outlier_scores = pd.read_csv(args.outliers)
    holdout = pd.read_csv(args.holdout)
    smoothness = pd.read_csv(args.smoothness)

    result = run_ngc7814_diagnostics(
        rotmod,
        tau_profiles,
        knot_params,
        outlier_scores,
        holdout,
        smoothness,
        figures_dir=Path(args.figures_dir),
    )
    checks = _ngc7814_checks(result.failure_diagnostics, result.vs_success)

    FAILURE_CSV.parent.mkdir(parents=True, exist_ok=True)
    result.failure_diagnostics.to_csv(FAILURE_CSV, index=False)
    result.vs_success.to_csv(VS_SUCCESS_CSV, index=False)
    write_ngc7814_failure_report(
        REPORT_PATH,
        failure_diag=result.failure_diagnostics,
        vs_success=result.vs_success,
        outlier_scores=outlier_scores,
        checks=checks,
    )

    print(f"Wrote {FAILURE_CSV}")
    print(f"Wrote {VS_SUCCESS_CSV}")
    print(f"Wrote {REPORT_PATH}")
    for name, p in result.figure_paths.items():
        print(f"Figure {name}: {p}")
    ng = result.failure_diagnostics[result.failure_diagnostics["galaxy_id"] == TARGET_GALAXY].iloc[0]
    print(
        f"{TARGET_GALAXY}: median v_bulge/v_bar={ng['median_vbulge_over_vbar']:.3f}; "
        f"neg residual frac={ng['fraction_negative_residual_v2']:.2f}; "
        f"holdout_failure checks={checks}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
