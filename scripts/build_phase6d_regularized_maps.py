from __future__ import annotations

import argparse

from tdf_galaxy_tau.analysis.phase6d_regularized_maps import (
    IMPLEMENTATION_VERSION,
    run_phase6d_regularized_maps,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 6C-E regularized pseudo-2D maps (R2+R6).")
    parser.add_argument(
        "--all-primary-pilots",
        action="store_true",
        help="Build all five Tier-1 primary pilots.",
    )
    parser.add_argument("--galaxy-id", default=None, help="Single galaxy ID.")
    parser.add_argument("--no-figure", action="store_true", help="Skip PNG figures.")
    args = parser.parse_args()

    if args.all_primary_pilots:
        batch = run_phase6d_regularized_maps(write_figures=not args.no_figure)
    elif args.galaxy_id:
        from tdf_galaxy_tau.analysis.phase6d_regularized_maps import (
            build_regularized_pseudo2d_map,
            write_regularized_outputs,
        )

        res = build_regularized_pseudo2d_map(args.galaxy_id)
        write_regularized_outputs(res, write_figure=not args.no_figure)
        batch = {"results": [res], "summary": None}
    else:
        batch = run_phase6d_regularized_maps(write_figures=not args.no_figure)

    print(f"Implementation version: {IMPLEMENTATION_VERSION}")
    for res in batch["results"]:
        print(
            f"  {res.galaxy_id}: candidate={res.metadata['phase6d_candidate']} "
            f"smooth={res.metadata['smoothness_pass']} "
            f"radial={res.metadata['radial_consistency_pass']} "
            f"capped={res.metadata['fraction_segments_capped']:.1%}"
        )
    if batch.get("summary") is not None:
        n = int(batch["summary"]["phase6d_candidate"].sum())
        print(f"Phase 6D candidates: {n}/5")
        print(f"Wrote {batch['summary_path']}")
        print(f"Wrote {batch['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
