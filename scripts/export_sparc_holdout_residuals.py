from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from tdf_galaxy_tau.reconstruction.radial_tau import load_selected_galaxy_ids
from tdf_galaxy_tau.validation.holdout_residuals import export_holdout_point_residuals

OUTPUT_CSV = Path("outputs/tables/sparc_holdout_point_residuals.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4E export per-point holdout residuals")
    parser.add_argument("--data", default="data/processed/sparc/sparc_rotmod_standardized.csv")
    parser.add_argument("--subset", default="outputs/tables/sparc_subset_selection.csv")
    parser.add_argument("--tau-profiles", default="outputs/tables/sparc_subset_tau_profiles.csv")
    parser.add_argument("--config", default="configs/reconstruction.yaml")
    parser.add_argument("--models-config", default="configs/models.yaml")
    args = parser.parse_args()

    recon_yaml = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    models_yaml = yaml.safe_load(Path(args.models_config).read_text(encoding="utf-8")) or {}
    audit_cfg = recon_yaml.get("tdf_robustness_audit", {})
    tdf_models = tuple(audit_cfg.get("holdout_tdf_models", ["tdf_3knot", "tdf_5knot"]))

    data = pd.read_csv(args.data)
    tau_df = pd.read_csv(args.tau_profiles)
    selected_ids = load_selected_galaxy_ids(args.subset)

    points = export_holdout_point_residuals(
        data,
        tau_df,
        selected_ids,
        recon_yaml,
        models_yaml,
        tdf_models=tdf_models,
    )
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    points.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {OUTPUT_CSV} ({len(points)} test-point rows)")
    print(f"comparison_mode: {points['comparison_mode'].iloc[0] if len(points) else 'n/a'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
