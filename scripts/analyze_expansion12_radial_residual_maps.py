from __future__ import annotations

import argparse
from pathlib import Path

from tdf_galaxy_tau.analysis.expansion12_radial_maps import (
    AUDIT_DISCLAIMER,
    FOCUS_GALAXY_IDS,
    run_expansion12_radial_maps,
    write_expansion12_radial_report,
)

POINTS_CSV = Path("outputs/tables/expansion12_holdout_point_residuals.csv")
SUMMARY_CSV = Path("outputs/tables/expansion12_radial_failure_map_summary.csv")
REPORT_PATH = Path("outputs/reports/expansion12_radial_residual_map_report.md")
FIGURES_DIR = Path("outputs/figures/sparc_subset")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 5B-R: radial holdout residual maps for expansion_12 flex-recovery cases"
    )
    parser.add_argument("--rotmod", default="data/processed/sparc/sparc_rotmod_standardized.csv")
    parser.add_argument("--tau-profiles", default="outputs/tables/expansion12_tau_profiles.csv")
    parser.add_argument(
        "--failure-diagnostics",
        default="outputs/tables/expansion12_failure_diagnostics.csv",
    )
    parser.add_argument("--recon", default="configs/reconstruction.yaml")
    parser.add_argument("--models", default="configs/models.yaml")
    parser.add_argument("--figures-dir", default=str(FIGURES_DIR))
    args = parser.parse_args()

    result = run_expansion12_radial_maps(
        rotmod_path=args.rotmod,
        tau_path=args.tau_profiles,
        failure_diag_path=args.failure_diagnostics,
        recon_path=args.recon,
        models_path=args.models,
        figures_dir=args.figures_dir,
    )

    POINTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    result.holdout_points.to_csv(POINTS_CSV, index=False)
    result.radial_summary.to_csv(SUMMARY_CSV, index=False)

    failure_diag = None
    fpath = Path(args.failure_diagnostics)
    if fpath.is_file():
        import pandas as pd

        failure_diag = pd.read_csv(fpath)

    write_expansion12_radial_report(
        REPORT_PATH,
        points=result.holdout_points,
        summary=result.radial_summary,
        localization=result.localization,
        comparison=result.comparison,
        failure_diag=failure_diag,
        figure_paths=result.figure_paths,
    )

    print(AUDIT_DISCLAIMER)
    print(f"Wrote {POINTS_CSV} ({len(result.holdout_points)} test-point rows)")
    print(f"Wrote {SUMMARY_CSV} ({len(result.radial_summary)} summary rows)")
    print(f"Wrote {REPORT_PATH}")
    for name, p in result.figure_paths.items():
        print(f"Figure {name}: {p}")
    for gid in FOCUS_GALAXY_IDS:
        loc = result.localization[gid]
        print(
            f"{gid}: 3k worst={loc.get('tdf_3knot_worst_region')}; "
            f"5k recovers={loc.get('tdf_5knot_recovers_regions')}; "
            f"tension={loc.get('tension_type')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
