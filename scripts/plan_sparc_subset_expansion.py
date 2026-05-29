from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.data.subset_expansion import (
    PROTOCOL_DISCLAIMER,
    load_subset_expansion_config,
    run_subset_expansion_planning,
)

CANDIDATES_OUT = Path("outputs/tables/sparc_subset_expansion_candidates.csv")
PLAN_OUT = Path("outputs/tables/sparc_subset_expansion_plan.csv")
REPORT_OUT = Path("outputs/reports/sparc_subset_expansion_protocol_report.md")


def main() -> int:
    cfg = load_subset_expansion_config()
    candidates, plan = run_subset_expansion_planning()

    pick12 = candidates[candidates["selected_for_expansion_12"]]["galaxy_id"].tolist()
    pick20 = candidates[candidates["selected_for_expansion_20"]]["galaxy_id"].tolist()
    n_eval = len(candidates)
    n_elig = int(candidates["eligible_for_expansion"].sum()) if "eligible_for_expansion" in candidates.columns else 0

    print(PROTOCOL_DISCLAIMER)
    print(f"Wrote {CANDIDATES_OUT} ({n_eval} candidates, {n_elig} eligible)")
    print(f"Wrote {PLAN_OUT} ({len(plan)} plan rows)")
    print(f"Wrote {REPORT_OUT}")
    print(f"expansion_12 additions ({len(pick12)}): {', '.join(pick12)}")
    print(f"expansion_20 additions ({len(pick20)}): {', '.join(pick20)}")
    print(f"Original six: {', '.join(cfg.original_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
