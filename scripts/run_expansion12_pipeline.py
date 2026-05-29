from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.scripts.expansion_pipeline import (
    EXPANSION12_ADDITIONS,
    REPORT_DISCLAIMER,
    run_expansion12_benchmark,
)

COMPARISON_OUT = Path("outputs/tables/expansion12_model_comparison.csv")
HOLDOUT_OUT = Path("outputs/tables/expansion12_holdout_validation.csv")
FAILURE_OUT = Path("outputs/tables/expansion12_failure_mode_summary.csv")
CLAIMS_OUT = Path("outputs/tables/expansion12_claim_traceability.csv")
REPORT_OUT = Path("outputs/reports/expansion12_benchmark_report.md")


def main() -> int:
    result = run_expansion12_benchmark(
        comparison_out=COMPARISON_OUT,
        holdout_out=HOLDOUT_OUT,
        failure_out=FAILURE_OUT,
        claims_out=CLAIMS_OUT,
        report_out=REPORT_OUT,
    )
    gids = result["galaxy_ids"]
    fail = result["failure_mode_summary"]
    n_ok = int((fail["failure_mode_classification"] == "robust_tdf_success").sum())
    n_bad = int((fail["failure_mode_classification"] == "tdf_failure_mode").sum())

    print(REPORT_DISCLAIMER)
    print(f"Processed {len(gids)} galaxies")
    print(f"Wrote {COMPARISON_OUT} ({len(result['model_comparison'])} rows)")
    print(f"Wrote {HOLDOUT_OUT}")
    print(f"Wrote {FAILURE_OUT} (robust={n_ok}, failure={n_bad})")
    print(f"Wrote {CLAIMS_OUT}")
    print(f"Wrote {REPORT_OUT}")
    print(f"Phase 5A additions: {', '.join(EXPANSION12_ADDITIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
