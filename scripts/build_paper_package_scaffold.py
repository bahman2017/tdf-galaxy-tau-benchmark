from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.analysis.paper_package import (
    PACKAGE_DISCLAIMER,
    run_paper_package_scaffold,
)

FIGURE_INV = Path("outputs/tables/paper_figure_inventory.csv")
TABLE_INV = Path("outputs/tables/paper_table_inventory.csv")
REPORT = Path("outputs/reports/paper_package_scaffold_report.md")


def main() -> int:
    result = run_paper_package_scaffold(
        figure_inventory_out=FIGURE_INV,
        table_inventory_out=TABLE_INV,
        report_out=REPORT,
    )
    print(PACKAGE_DISCLAIMER)
    print(f"Wrote {FIGURE_INV} ({len(result['figures'])} figures)")
    print(f"Wrote {TABLE_INV} ({len(result['tables'])} tables)")
    print(f"Wrote {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
