from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.analysis.phase6c_gradient_diagnostics import (
    DIAGNOSTIC_VERSION,
    run_phase6c_gradient_diagnostics,
)

TABLE_OUT = Path("outputs/tables/phase6c_primary_pilot_gradient_diagnostics.csv")
REPORT_OUT = Path("outputs/reports/phase6c_gradient_diagnostic_report.md")


def main() -> int:
    result = run_phase6c_gradient_diagnostics(
        table_out=TABLE_OUT,
        report_out=REPORT_OUT,
    )
    diag = result["diagnostics"]
    print(f"Diagnostic version: {DIAGNOSTIC_VERSION}")
    print(f"Wrote {TABLE_OUT}")
    print(f"Wrote {REPORT_OUT}")
    for _, row in diag.iterrows():
        print(
            f"  {row['galaxy_id']}: max_rel_jump={row['max_rel_dtaudr_jump']:.3f} "
            f"cause={row['primary_failure_cause']} "
            f"6D_ready={row.get('phase6c_ready_for_second_channel', False)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
