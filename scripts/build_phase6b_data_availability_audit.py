from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.analysis.phase6b_data_availability import (
    AUDIT_VERSION,
    N_COHORT,
    run_phase6b_audit,
)

AUDIT_OUT = Path("outputs/tables/phase6b_expansion20_data_availability_audit.csv")
RANKING_OUT = Path("outputs/tables/phase6b_pilot_candidate_ranking.csv")
REPORT_OUT = Path("outputs/reports/phase6b_pilot_selection_report.md")


def main() -> int:
    result = run_phase6b_audit(
        audit_out=AUDIT_OUT,
        ranking_out=RANKING_OUT,
        report_out=REPORT_OUT,
    )
    audit = result["audit"]
    primary = audit[audit["is_primary_pilot"]]["galaxy_id"].tolist()
    print(f"Audit version: {AUDIT_VERSION}")
    print(f"Galaxies audited: {len(audit)} (expected {N_COHORT})")
    print(f"Wrote {AUDIT_OUT}")
    print(f"Wrote {RANKING_OUT}")
    print(f"Wrote {REPORT_OUT}")
    print(f"Primary pilots (top 5 tier-1): {', '.join(primary) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
