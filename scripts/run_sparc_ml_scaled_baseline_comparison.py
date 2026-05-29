from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.analysis.ml_scaled_baseline_comparison import (
    MlScaledBaselineConfig,
    TARGET_GALAXY,
    plot_model_winners_heatmap,
    plot_ngc7814_fair_comparison,
    plot_success_stability,
    run_ml_scaled_baseline_comparison,
    write_ml_scaled_baseline_report,
)
from tdf_galaxy_tau.reconstruction.radial_tau import load_selected_galaxy_ids

COMPARISON_CSV = Path("outputs/tables/sparc_ml_scaled_model_comparison.csv")
NGC_FAIR_CSV = Path("outputs/tables/ngc7814_ml_scaled_fair_comparison.csv")
BEST_SUMMARY_CSV = Path("outputs/tables/sparc_ml_scaled_best_model_summary.csv")
REPORT_PATH = Path("outputs/reports/sparc_ml_scaled_baseline_comparison_report.md")
FIGURES_DIR = Path("outputs/figures/sparc_subset")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4G fair M/L-scaled TDF/NFW/MOND comparison")
    parser.add_argument("--data", default="data/processed/sparc/sparc_rotmod_standardized.csv")
    parser.add_argument("--subset", default="outputs/tables/sparc_subset_selection.csv")
    parser.add_argument("--holdout", default="outputs/tables/sparc_tdf_holdout_validation.csv")
    parser.add_argument("--config", default="configs/reconstruction.yaml")
    parser.add_argument("--models-config", default="configs/models.yaml")
    args = parser.parse_args()

    rotmod = pd.read_csv(args.data)
    selected = load_selected_galaxy_ids(args.subset)
    cfg = MlScaledBaselineConfig()

    comparison, ngc_fair, best_summary = run_ml_scaled_baseline_comparison(
        rotmod,
        selected,
        recon_path=args.config,
        models_path=args.models_config,
        holdout_validation_path=args.holdout,
        ml_config=cfg,
    )

    COMPARISON_CSV.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(COMPARISON_CSV, index=False)
    ngc_fair.to_csv(NGC_FAIR_CSV, index=False)
    best_summary.to_csv(BEST_SUMMARY_CSV, index=False)

    p1 = plot_ngc7814_fair_comparison(ngc_fair, FIGURES_DIR / "ngc7814_ml_scaled_fair_comparison.png")
    p2 = plot_model_winners_heatmap(comparison, FIGURES_DIR / "ml_scaled_model_winners_heatmap.png")
    p3 = plot_success_stability(best_summary, FIGURES_DIR / "ml_scaled_success_stability.png")

    write_ml_scaled_baseline_report(
        REPORT_PATH,
        comparison=comparison,
        ngc_fair=ngc_fair,
        best_summary=best_summary,
        ml_config=cfg,
    )

    ngc_can = ngc_fair[(ngc_fair["disk_scale"] == 1.0) & (ngc_fair["bulge_scale"] == 1.0)].iloc[0]
    ngc_row = best_summary[best_summary["galaxy_id"] == TARGET_GALAXY].iloc[0]
    print(f"Wrote {COMPARISON_CSV} ({len(comparison)} rows)")
    print(f"Wrote {NGC_FAIR_CSV}")
    print(f"Wrote {BEST_SUMMARY_CSV}")
    print(f"Wrote {REPORT_PATH}")
    print(f"Figures: {p1}, {p2}, {p3}")
    print(
        f"NGC7814 canonical (1,1): tdf_3knot={ngc_can['tdf_3knot_rmse']:.1f} "
        f"nfw={ngc_can['nfw_scaled_rmse']:.1f} mond={ngc_can['mond_scaled_rmse']:.1f} "
        f"best={ngc_can['best_model']}"
    )
    print(f"Best plausible model for NGC7814: {ngc_row['best_model_best_plausible_scale']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
