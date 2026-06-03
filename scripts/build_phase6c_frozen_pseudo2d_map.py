from __future__ import annotations

import argparse
from pathlib import Path

from tdf_galaxy_tau.analysis.phase6c_frozen_pseudo2d import (
    MAP_VERSION,
    PRIMARY_PILOT_GALAXY_IDS,
    build_frozen_pseudo2d_map,
    run_phase6c_primary_pilot_batch,
    write_phase6c_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build frozen axisymmetric pseudo-2D tau map (Phase 6C; no refit)."
    )
    parser.add_argument(
        "--galaxy-id",
        default="DDO161",
        help="Galaxy ID (default: DDO161 primary pilot).",
    )
    parser.add_argument(
        "--allow-diagnostic",
        action="store_true",
        help="Allow non-primary galaxies (e.g. NGC7814 exploratory).",
    )
    parser.add_argument(
        "--grid-n",
        type=int,
        default=101,
        help="Cartesian grid points per axis.",
    )
    parser.add_argument(
        "--no-figure",
        action="store_true",
        help="Skip optional PNG figure.",
    )
    parser.add_argument(
        "--all-primary-pilots",
        action="store_true",
        help="Build all five Tier-1 primary pilots and write combined audit.",
    )
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="With --all-primary-pilots: skip map build, summary/audit from existing outputs.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="With --all-primary-pilots: skip galaxies that already have NPZ maps.",
    )
    args = parser.parse_args()

    if args.all_primary_pilots:
        batch = run_phase6c_primary_pilot_batch(
            build_maps=not args.audit_only,
            skip_existing=args.skip_existing,
            write_figures=not args.no_figure,
            grid_n=args.grid_n,
        )
        summary = batch["summary"]
        print(f"Map version: {MAP_VERSION}")
        print(f"Primary pilots: {', '.join(PRIMARY_PILOT_GALAXY_IDS)}")
        print(f"Built: {', '.join(batch['built']) or 'none'}")
        print(f"Skipped existing: {', '.join(batch['skipped']) or 'none'}")
        print(f"Wrote {batch['summary_path']}")
        print(f"Wrote {batch['audit_path']}")
        ready = summary[summary["phase6c_ready_for_second_channel_scaffold"]]
        print(f"Phase 6D ready: {', '.join(ready['galaxy_id'].astype(str).tolist()) or 'NONE'}")
        return 0

    result = build_frozen_pseudo2d_map(
        args.galaxy_id,
        grid_n=args.grid_n,
        allow_diagnostic=args.allow_diagnostic,
    )
    paths = write_phase6c_outputs(
        result,
        write_figure=not args.no_figure,
    )

    print(f"Map version: {MAP_VERSION}")
    print(f"Galaxy: {result.galaxy_id}")
    print(f"K_g: {result.metadata['K_g']} (tau_retuned={result.metadata['tau_retuned']})")
    print(
        f"Radial consistency max rel err: "
        f"{result.metadata['radial_consistency_max_relative_error']:.3e} "
        f"({'PASS' if result.metadata['radial_consistency_pass'] else 'FAIL'})"
    )
    print(
        f"Smoothness: {result.metadata['smoothness_metric']:.4f} "
        f"({'PASS' if result.metadata['smoothness_pass'] else 'FAIL'})"
    )
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
