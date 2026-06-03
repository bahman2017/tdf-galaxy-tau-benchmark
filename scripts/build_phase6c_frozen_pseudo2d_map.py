from __future__ import annotations

import argparse
from pathlib import Path

from tdf_galaxy_tau.analysis.phase6c_frozen_pseudo2d import (
    MAP_VERSION,
    build_frozen_pseudo2d_map,
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
    args = parser.parse_args()

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
