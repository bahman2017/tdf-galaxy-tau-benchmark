from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.analysis.radial_holdout_maps import (
    TARGET_GALAXY,
    build_radial_failure_map_summary,
    ngc7814_radial_localization,
    plot_all_galaxies_compact,
    plot_ngc7814_radial_map,
    write_radial_holdout_report,
)

POINTS_CSV = Path("outputs/tables/sparc_holdout_point_residuals.csv")
SUMMARY_CSV = Path("outputs/tables/sparc_radial_failure_map_summary.csv")
REPORT_PATH = Path("outputs/reports/sparc_radial_holdout_failure_report.md")
FIGURES_DIR = Path("outputs/figures/sparc_subset")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4E radial holdout failure-map analysis")
    parser.add_argument("--points", default=str(POINTS_CSV))
    parser.add_argument("--figures-dir", default=str(FIGURES_DIR))
    args = parser.parse_args()

    points = pd.read_csv(args.points)
    summary = build_radial_failure_map_summary(points)
    localization = ngc7814_radial_localization(summary, points)

    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_CSV, index=False)

    fig_dir = Path(args.figures_dir)
    p1 = plot_ngc7814_radial_map(points, fig_dir / "ngc7814_radial_holdout_residual_map.png")
    p2 = plot_all_galaxies_compact(points, fig_dir / "holdout_residual_maps_all_galaxies.png")

    write_radial_holdout_report(
        REPORT_PATH,
        points=points,
        summary=summary,
        localization=localization,
    )

    print(f"Wrote {SUMMARY_CSV} ({len(summary)} summary rows)")
    print(f"Wrote {REPORT_PATH}")
    print(f"Figure ngc7814: {p1}")
    print(f"Figure all galaxies: {p2}")
    print(f"{TARGET_GALAXY} localization: {localization}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
