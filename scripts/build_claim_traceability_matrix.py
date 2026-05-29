from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.validation.failure_modes import (
    build_claim_traceability_matrix,
    write_claim_traceability_report,
)

MATRIX_TABLE = Path("outputs/tables/sparc_claim_traceability_matrix.csv")
REPORT_PATH = Path("outputs/reports/sparc_claim_traceability_report.md")


def main() -> int:
    matrix = build_claim_traceability_matrix()
    MATRIX_TABLE.parent.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(MATRIX_TABLE, index=False)
    write_claim_traceability_report(REPORT_PATH, matrix)
    print(f"Wrote claim traceability matrix: {MATRIX_TABLE}")
    print(f"Wrote report: {REPORT_PATH}")
    print(f"Claims: {len(matrix)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
