from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.analysis.controlled_subset_audit import (
    AUDIT_VERSION,
    FINAL_CONTROLLED_SUBSET_CLAIM,
    run_controlled_subset_final_audit,
)

STATUS_OUT = Path("outputs/tables/sparc_controlled_subset_final_status.csv")
CLAIMS_OUT = Path("outputs/tables/sparc_controlled_subset_final_claims.csv")
REPORT_OUT = Path("outputs/reports/sparc_controlled_subset_final_audit_report.md")


def main() -> int:
    status, claims = run_controlled_subset_final_audit(
        status_out=STATUS_OUT,
        claims_out=CLAIMS_OUT,
        report_out=REPORT_OUT,
    )
    print(f"Audit version: {AUDIT_VERSION}")
    print(f"Wrote {STATUS_OUT} ({len(status)} phases)")
    print(f"Wrote {CLAIMS_OUT} ({len(claims)} claims)")
    print(f"Wrote {REPORT_OUT}")
    print(f"Final claim: {FINAL_CONTROLLED_SUBSET_CLAIM[:80]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
