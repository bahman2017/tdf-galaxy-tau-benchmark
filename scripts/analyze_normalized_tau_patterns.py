from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.analysis.normalized_patterns import (
    run_normalized_pattern_analysis,
    write_normalized_pattern_report,
)

PATTERNS_CSV = Path("outputs/tables/sparc_normalized_tau_patterns.csv")
SIMILARITY_CSV = Path("outputs/tables/sparc_tau_pattern_similarity_matrix.csv")
OUTLIERS_CSV = Path("outputs/tables/sparc_tau_pattern_outlier_scores.csv")
REPORT_PATH = Path("outputs/reports/sparc_normalized_tau_pattern_report.md")
FIGURES_DIR = Path("outputs/figures/sparc_subset")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4C exploratory normalized τ-pattern discovery (six-galaxy subset)"
    )
    parser.add_argument(
        "--tau-profiles",
        default="outputs/tables/sparc_subset_tau_profiles.csv",
        help="Phase 2A per-galaxy τ profile table",
    )
    parser.add_argument(
        "--figures-dir",
        default=str(FIGURES_DIR),
    )
    args = parser.parse_args()

    tau_profiles = pd.read_csv(args.tau_profiles)
    result = run_normalized_pattern_analysis(tau_profiles, figures_dir=Path(args.figures_dir))

    PATTERNS_CSV.parent.mkdir(parents=True, exist_ok=True)
    result.patterns_table.to_csv(PATTERNS_CSV, index=False)
    result.similarity.to_csv(SIMILARITY_CSV, index=False)
    result.outliers.to_csv(OUTLIERS_CSV, index=False)
    write_normalized_pattern_report(
        REPORT_PATH,
        patterns_table=result.patterns_table,
        similarity=result.similarity,
        outliers=result.outliers,
        profiles=result.profiles,
    )

    ng = result.outliers[result.outliers["galaxy_id"] == "NGC7814"].iloc[0]
    success = result.similarity[
        (result.similarity["galaxy_id_a"].isin({"DDO154", "IC2574", "NGC2403", "NGC3198", "NGC6503"}))
        & (result.similarity["galaxy_id_b"].isin({"DDO154", "IC2574", "NGC2403", "NGC3198", "NGC6503"}))
        & (result.similarity["galaxy_id_a"] != result.similarity["galaxy_id_b"])
    ]
    print(f"Wrote {PATTERNS_CSV} ({len(result.patterns_table)} rows)")
    print(f"Wrote {SIMILARITY_CSV} ({len(result.similarity)} pairs)")
    print(f"Wrote {OUTLIERS_CSV}")
    print(f"Wrote {REPORT_PATH}")
    for name, p in result.figure_paths.items():
        print(f"Figure {name}: {p}")
    print(f"Success-group median dtaudr_corr: {success['dtaudr_corr'].median():.3f}")
    print(
        f"NGC7814: holdout_failure_mode={ng['holdout_failure_mode']}; "
        f"normalized_profile_outlier={ng['normalized_profile_outlier']}; "
        f"dtaudr_rmse_rank={int(ng['dtaudr_rmse_rank'])}; tau_rmse_rank={int(ng['tau_rmse_rank'])}; "
        f"residual_v2_rmse_rank={int(ng['residual_v2_rmse_rank'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
