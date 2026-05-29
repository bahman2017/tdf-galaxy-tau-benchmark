from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.analysis.ml_sensitivity import (
    MlSensitivityConfig,
    plot_ngc7814_inner_rmse_heatmap,
    plot_ngc7814_tau_profiles,
    plot_success_vs_failure_summary,
    run_ml_sensitivity_audit,
    write_ml_sensitivity_report,
)
from tdf_galaxy_tau.reconstruction.radial_tau import load_reconstruction_config, load_selected_galaxy_ids

SUMMARY_CSV = Path("outputs/tables/sparc_ml_sensitivity_summary.csv")
NGC_DETAIL_CSV = Path("outputs/tables/ngc7814_ml_sensitivity_detail.csv")
COMPARISON_CSV = Path("outputs/tables/sparc_ml_sensitivity_holdout_comparison.csv")
REPORT_PATH = Path("outputs/reports/sparc_ml_sensitivity_audit_report.md")
FIGURES_DIR = Path("outputs/figures/sparc_subset")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4F diagnostic M/L sensitivity audit")
    parser.add_argument("--data", default="data/processed/sparc/sparc_rotmod_standardized.csv")
    parser.add_argument("--subset", default="outputs/tables/sparc_subset_selection.csv")
    parser.add_argument("--holdout", default="outputs/tables/sparc_tdf_holdout_validation.csv")
    parser.add_argument("--config", default="configs/reconstruction.yaml")
    parser.add_argument("--models-config", default="configs/models.yaml")
    args = parser.parse_args()

    rotmod = pd.read_csv(args.data)
    selected = load_selected_galaxy_ids(args.subset)
    ml_config = MlSensitivityConfig()

    summary, ngc_detail, comparison = run_ml_sensitivity_audit(
        rotmod,
        selected,
        recon_path=args.config,
        models_path=args.models_config,
        holdout_validation_path=args.holdout,
        ml_config=ml_config,
    )

    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_CSV, index=False)
    ngc_detail.to_csv(NGC_DETAIL_CSV, index=False)
    comparison.to_csv(COMPARISON_CSV, index=False)

    tau_config = load_reconstruction_config(args.config)
    p1 = plot_ngc7814_inner_rmse_heatmap(ngc_detail, FIGURES_DIR / "ngc7814_ml_sensitivity_inner_residuals.png")
    p2 = plot_ngc7814_tau_profiles(
        rotmod, tau_config, ngc_detail, FIGURES_DIR / "ngc7814_ml_sensitivity_tau_profiles.png"
    )
    p3 = plot_success_vs_failure_summary(
        comparison, FIGURES_DIR / "ml_sensitivity_success_vs_failure_summary.png"
    )

    write_ml_sensitivity_report(
        REPORT_PATH,
        summary=summary,
        ngc_detail=ngc_detail,
        comparison=comparison,
        ml_config=ml_config,
    )

    ngc = comparison[comparison["galaxy_id"] == "NGC7814"].iloc[0]
    print(f"Wrote {SUMMARY_CSV} ({len(summary)} rows)")
    print(f"Wrote {NGC_DETAIL_CSV}")
    print(f"Wrote {COMPARISON_CSV}")
    print(f"Wrote {REPORT_PATH}")
    print(f"Figures: {p1}, {p2}, {p3}")
    print(
        f"NGC7814 canonical tdf_3knot={ngc['canonical_tdf_3knot_rmse']:.1f} "
        f"best_scaled={ngc['best_scaled_tdf_3knot_rmse']:.1f} "
        f"beats_nfw={ngc['tdf_beats_nfw_under_best_scale']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
