from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.scripts.expansion_pipeline import (
    EXPANSION12_ADDITIONS,
    classify_expansion12_failure_mode,
    load_expansion12_galaxy_ids,
    run_expansion12_benchmark,
)
from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION

EXPECTED_12 = list(MANDATED_GALAXY_CLASSIFICATION.keys()) + list(EXPANSION12_ADDITIONS)


def test_load_expansion12_ids() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = root / "outputs/tables/sparc_subset_expansion_plan.csv"
    if not plan.is_file():
        pytest.skip("Phase 5A plan missing")
    gids = load_expansion12_galaxy_ids(plan)
    assert len(gids) == 12
    assert set(gids) == set(EXPECTED_12)


def test_mandated_classification_preserved() -> None:
    ho = pd.DataFrame(
        [
            {
                "galaxy_id": "NGC7814",
                "split_name": "even_odd_index",
                "model_name": "tdf_3knot",
                "test_rmse_kms": 200.0,
            },
            {
                "galaxy_id": "NGC7814",
                "split_name": "even_odd_index",
                "model_name": "nfw_refit",
                "test_rmse_kms": 25.0,
            },
        ]
    )
    assert classify_expansion12_failure_mode("NGC7814", ho) == "tdf_failure_mode"


def test_run_expansion12_benchmark_outputs(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    rotmod = root / "data/processed/sparc/sparc_rotmod_standardized.csv"
    plan = root / "outputs/tables/sparc_subset_expansion_plan.csv"
    if not rotmod.is_file() or not plan.is_file():
        pytest.skip("inputs missing")

    result = run_expansion12_benchmark(
        rotmod_path=rotmod,
        plan_path=plan,
        comparison_out=root / "outputs/tables/expansion12_model_comparison.csv",
        holdout_out=root / "outputs/tables/expansion12_holdout_validation.csv",
        failure_out=root / "outputs/tables/expansion12_failure_mode_summary.csv",
        claims_out=root / "outputs/tables/expansion12_claim_traceability.csv",
        report_out=root / "outputs/reports/expansion12_benchmark_report.md",
    )
    assert len(result["galaxy_ids"]) == 12
    comp = result["model_comparison"]
    assert comp["galaxy_id"].nunique() == 12
    assert "tdf_3knot" in comp["model_name"].values
    assert "nfw_refit" in comp["model_name"].values
    fail = result["failure_mode_summary"]
    assert len(fail) == 12
    assert "failure_mode_classification" in fail.columns


def test_run_script(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    if not (root / "data/processed/sparc/sparc_rotmod_standardized.csv").is_file():
        pytest.skip("data missing")
    subprocess.run(
        ["python3", "scripts/run_expansion12_pipeline.py"],
        cwd=root,
        check=True,
        timeout=600,
    )
    report = (root / "outputs/reports/expansion12_benchmark_report.md").read_text()
    assert "expansion_12" in report.lower()
    assert "does not disprove dark matter" in report.lower()
