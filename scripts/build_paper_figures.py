from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.analysis.paper_figures import PHASE_DISCLAIMER, run_paper_figures_build


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    built = run_paper_figures_build(root=root)
    print(PHASE_DISCLAIMER)
    for name, path in built.items():
        print(f"  {name} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
