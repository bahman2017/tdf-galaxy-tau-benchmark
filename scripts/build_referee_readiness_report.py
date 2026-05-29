from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.analysis.reviewer_analysis import PHASE_DISCLAIMER, run_referee_readiness_build


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = run_referee_readiness_build(root=root)
    print(PHASE_DISCLAIMER)
    print(f"Wrote {result['stats_path']}")
    if result.get("pdf_path"):
        print(f"Wrote {result['pdf_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
