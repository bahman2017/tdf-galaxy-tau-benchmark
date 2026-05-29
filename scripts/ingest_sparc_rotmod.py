from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.data.sparc_loader import ingest_sparc_rotmod_to_csv


REPORT_PATH = Path("outputs/reports/sparc_ingestion_report.md")
SUMMARY_PATH = Path("outputs/tables/sparc_ingestion_summary.csv")


def _write_report(summary: object, failures: list[dict[str, str]], out_csv: Path) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# SPARC Ingestion Report (Phase 1A)",
        "",
        "## Scope",
        "",
        "Data ingestion and standardization only. This is **not** model validation.",
        "",
        "## Metrics",
        "",
        f"- Raw files found: {summary.raw_files_found}",
        f"- Galaxies parsed successfully: {summary.galaxies_parsed_successfully}",
        f"- Galaxies failed: {summary.galaxies_failed}",
        f"- Total radial data points: {summary.total_radial_points}",
        f"- Radius range [kpc]: {summary.min_r_kpc} to {summary.max_r_kpc}",
        f"- Observed velocity range [km/s]: {summary.min_v_obs_kms} to {summary.max_v_obs_kms}",
        f"- Galaxies with bulge contribution: {summary.galaxies_with_bulge}",
        f"- Rows with negative residual_v2_kms2: {summary.rows_negative_residual_v2}",
        "",
        "## Output",
        "",
        f"- Standardized CSV: `{out_csv}`",
        f"- Summary CSV: `{SUMMARY_PATH}`",
        "",
        "## Failed files",
        "",
    ]
    if failures:
        lines.extend([f"- `{item['source_file']}`: {item['error']}" for item in failures])
    else:
        lines.append("- None")

    lines.extend([
        "",
        "## Claim boundary",
        "",
        "This report documents ingestion quality only; it does not validate TDF, NFW, or Burkert fits and does not make any dark-matter-disproof claim.",
    ])

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary(summary: object) -> None:
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "raw_files_found": summary.raw_files_found,
                "galaxies_parsed_successfully": summary.galaxies_parsed_successfully,
                "galaxies_failed": summary.galaxies_failed,
                "total_radial_points": summary.total_radial_points,
                "min_r_kpc": summary.min_r_kpc,
                "max_r_kpc": summary.max_r_kpc,
                "min_v_obs_kms": summary.min_v_obs_kms,
                "max_v_obs_kms": summary.max_v_obs_kms,
                "galaxies_with_bulge": summary.galaxies_with_bulge,
                "rows_negative_residual_v2": summary.rows_negative_residual_v2,
            }
        ]
    ).to_csv(SUMMARY_PATH, index=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest SPARC Rotmod_LTG files into standardized CSV")
    parser.add_argument("--input", required=True, help="Input directory containing *_rotmod.dat files")
    parser.add_argument("--out", required=True, help="Output standardized CSV path")
    args = parser.parse_args()

    out_csv = Path(args.out)
    df, failures, summary = ingest_sparc_rotmod_to_csv(args.input, out_csv)

    _write_report(summary, failures, out_csv)
    _write_summary(summary)

    print(f"Ingested rows: {len(df)}")
    print(f"Galaxies parsed successfully: {summary.galaxies_parsed_successfully}")
    print(f"Galaxies failed: {summary.galaxies_failed}")
    print(f"Wrote standardized CSV: {out_csv}")
    print(f"Wrote report: {REPORT_PATH}")
    print(f"Wrote summary: {SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
