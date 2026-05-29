from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.analysis.controlled_expansion_audit import (
    AUDIT_VERSION,
    FINAL_EXPANSION_20_CLAIM,
    run_controlled_expansion_final_audit,
)

COMPARISON_OUT = Path("outputs/tables/controlled_expansion_comparison_summary.csv")
CLAIMS_OUT = Path("outputs/tables/controlled_expansion_final_claims.csv")
REPORT_OUT = Path("outputs/reports/controlled_expansion20_final_audit_report.md")


def main() -> int:
    result = run_controlled_expansion_final_audit(
        comparison_out=COMPARISON_OUT,
        claims_out=CLAIMS_OUT,
        report_out=REPORT_OUT,
    )
    comp = result["comparison"]
    print(f"Audit version: {AUDIT_VERSION}")
    print(FINAL_EXPANSION_20_CLAIM)
    print(f"Wrote {COMPARISON_OUT}")
    print(f"Wrote {CLAIMS_OUT} ({len(result['claims'])} claims)")
    print(f"Wrote {REPORT_OUT}")
    for _, row in comp.iterrows():
        print(f"  {row['metric']}: e12={row['expansion_12']}, e20={row['expansion_20']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
