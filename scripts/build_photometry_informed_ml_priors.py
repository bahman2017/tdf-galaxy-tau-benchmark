from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.analysis.ml_priors import load_ml_priors_config
from tdf_galaxy_tau.analysis.photometry_informed_priors import (
    GALAXY_ORDER,
    build_photometry_informed_prior_weights,
    parse_photometry_informed_scenarios,
)

WEIGHTS_OUT = Path("outputs/tables/sparc_photometry_informed_prior_weights.csv")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4K: build photometry-informed diagnostic M/L prior weights (no fits)"
    )
    parser.add_argument(
        "--photometry",
        default="data/processed/sparc/sparc_photometry_metadata.csv",
    )
    parser.add_argument(
        "--subset-context",
        default="outputs/tables/sparc_subset_photometry_context.csv",
    )
    parser.add_argument("--priors", default="configs/ml_priors.yaml")
    parser.add_argument("--output", default=str(WEIGHTS_OUT))
    args = parser.parse_args()

    config = load_ml_priors_config(args.priors)
    photometry = pd.read_csv(args.photometry)
    subset = pd.read_csv(args.subset_context)
    photometry = photometry[photometry["galaxy_id"].isin(GALAXY_ORDER)]

    weights = build_photometry_informed_prior_weights(photometry, subset, config)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    weights.to_csv(out, index=False)

    scenarios = parse_photometry_informed_scenarios(config)
    print(f"Wrote {out} ({len(weights)} rows, {len(scenarios)} scenarios, {len(GALAXY_ORDER)} galaxies)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
