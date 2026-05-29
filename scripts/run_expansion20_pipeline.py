from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.scripts.expansion_pipeline import (
    EXPANSION20_ADDITIONS,
    REPORT_DISCLAIMER_20,
    run_expansion20_benchmark,
)

COMPARISON_OUT = Path("outputs/tables/expansion20_model_comparison.csv")
HOLDOUT_OUT = Path("outputs/tables/expansion20_holdout_validation.csv")
FAILURE_OUT = Path("outputs/tables/expansion20_failure_mode_summary.csv")
CLAIMS_OUT = Path("outputs/tables/expansion20_claim_traceability.csv")
REPORT_OUT = Path("outputs/reports/expansion20_benchmark_report.md")


def main() -> int:
    result = run_expansion20_benchmark(
        comparison_out=COMPARISON_OUT,
        holdout_out=HOLDOUT_OUT,
        failure_out=FAILURE_OUT,
        claims_out=CLAIMS_OUT,
        report_out=REPORT_OUT,
    )
    fail = result["failure_mode_summary"]
    n_robust = int((fail["failure_mode_classification"] == "robust_tdf_success").sum())
    n_sens = int((fail["failure_mode_classification"] == "sensitivity_recovery").sum())
    n_bad = int((fail["failure_mode_classification"] == "tdf_failure_mode").sum())
    n_mixed = int((fail["failure_mode_classification"] == "mixed_result").sum())

    print(REPORT_DISCLAIMER_20)
    print(f"Processed {len(result['galaxy_ids'])} galaxies")
    print(f"Wrote {COMPARISON_OUT} ({len(result['model_comparison'])} rows)")
    print(f"Wrote {HOLDOUT_OUT}")
    print(
        f"Wrote {FAILURE_OUT} (robust={n_robust}, sensitivity_recovery={n_sens}, "
        f"failure={n_bad}, mixed={n_mixed})"
    )
    print(f"Wrote {CLAIMS_OUT}")
    print(f"Wrote {REPORT_OUT}")
    print(f"Phase 5A additions ({len(EXPANSION20_ADDITIONS)}): {', '.join(EXPANSION20_ADDITIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
