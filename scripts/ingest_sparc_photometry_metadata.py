from __future__ import annotations

import argparse
from pathlib import Path

from tdf_galaxy_tau.data.sparc_metadata_join import run_photometry_metadata_ingestion

METADATA_OUT = Path("data/processed/sparc/sparc_photometry_metadata.csv")
SUMMARY_OUT = Path("outputs/tables/sparc_photometry_metadata_summary.csv")
SUBSET_OUT = Path("outputs/tables/sparc_subset_photometry_context.csv")
REPORT_OUT = Path("outputs/reports/sparc_photometry_metadata_ingestion_report.md")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4J: ingest SPARC photometry metadata")
    parser.add_argument("--rotmod", default="data/processed/sparc/sparc_rotmod_standardized.csv")
    parser.add_argument("--photometry-dir", default="data/raw/sparc/photometry")
    parser.add_argument("--subset", default="outputs/tables/sparc_subset_selection.csv")
    args = parser.parse_args()

    metadata, summary, subset_ctx = run_photometry_metadata_ingestion(
        rotmod_path=args.rotmod,
        photometry_dir=args.photometry_dir,
        subset_path=args.subset,
        metadata_out=METADATA_OUT,
        summary_out=SUMMARY_OUT,
        subset_ctx_out=SUBSET_OUT,
        report_out=REPORT_OUT,
    )

    print(f"Wrote {METADATA_OUT} ({len(metadata)} rows)")
    print(f"Wrote {SUMMARY_OUT} ({len(summary)} rows)")
    print(f"Wrote {SUBSET_OUT} ({len(subset_ctx)} rows)")
    print(f"Wrote {REPORT_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
