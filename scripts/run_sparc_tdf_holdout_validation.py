from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from tdf_galaxy_tau.reconstruction.radial_tau import load_selected_galaxy_ids
from tdf_galaxy_tau.validation.tdf_holdout_runner import run_holdout_validation

HOLDOUT_TABLE = Path("outputs/tables/sparc_tdf_holdout_validation.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description="Radial holdout validation for TDF knot models")
    parser.add_argument("--data", required=True)
    parser.add_argument("--subset", required=True)
    parser.add_argument("--tau-profiles", default="outputs/tables/sparc_subset_tau_profiles.csv")
    parser.add_argument("--config", default="configs/reconstruction.yaml")
    parser.add_argument("--models-config", default="configs/models.yaml")
    args = parser.parse_args()

    data = pd.read_csv(args.data)
    tau_df = pd.read_csv(args.tau_profiles)
    recon_yaml = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    models_yaml = yaml.safe_load(Path(args.models_config).read_text(encoding="utf-8")) or {}
    audit_cfg = recon_yaml.get("tdf_robustness_audit", {})
    tdf_models = tuple(audit_cfg.get("holdout_tdf_models", ["tdf_3knot", "tdf_5knot"]))

    selected_ids = load_selected_galaxy_ids(args.subset)
    holdout_df = run_holdout_validation(
        data,
        tau_df,
        selected_ids,
        recon_yaml,
        models_yaml,
        tdf_models=tdf_models,
    )
    HOLDOUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    holdout_df.to_csv(HOLDOUT_TABLE, index=False)
    print(f"Wrote holdout validation: {HOLDOUT_TABLE}")
    print(f"Rows: {len(holdout_df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
