from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.scripts.expansion_pipeline import (
    EXPANSION20_ADDITIONS,
    FROZEN_SENSITIVITY_RECOVERY,
    classify_expansion20_failure_mode,
    classify_expansion20_failure_mode_from_holdout,
    load_expansion20_galaxy_ids,
    run_expansion20_benchmark,
)
from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION

EXPECTED_20 = list(MANDATED_GALAXY_CLASSIFICATION.keys()) + list(EXPANSION20_ADDITIONS)


def test_load_expansion20_ids() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = root / "outputs/tables/sparc_subset_expansion_plan.csv"
    if not plan.is_file():
        pytest.skip("Phase 5A plan missing")
    gids = load_expansion20_galaxy_ids(plan)
    assert len(gids) == 20
    assert set(gids) == set(EXPECTED_20)


def test_frozen_guardrails() -> None:
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
    assert classify_expansion20_failure_mode("NGC7814", ho) == "tdf_failure_mode"
    assert classify_expansion20_failure_mode("NGC5055", ho) == "sensitivity_recovery"
    assert classify_expansion20_failure_mode("UGC05253", ho) == "sensitivity_recovery"
    assert classify_expansion20_failure_mode("UGC00128", ho) == "mixed_result"


def test_sensitivity_recovery_from_holdout() -> None:
    ho = pd.DataFrame(
        [
            {
                "galaxy_id": "TESTGAL",
                "split_name": "even_odd_index",
                "model_name": "tdf_3knot",
                "test_rmse_kms": 100.0,
            },
            {
                "galaxy_id": "TESTGAL",
                "split_name": "even_odd_index",
                "model_name": "tdf_5knot",
                "test_rmse_kms": 10.0,
            },
            {
                "galaxy_id": "TESTGAL",
                "split_name": "even_odd_index",
                "model_name": "nfw_refit",
                "test_rmse_kms": 50.0,
            },
            {
                "galaxy_id": "TESTGAL",
                "split_name": "even_odd_index",
                "model_name": "mond_fit_a0_simple",
                "test_rmse_kms": 55.0,
            },
        ]
    )
    assert (
        classify_expansion20_failure_mode_from_holdout("TESTGAL", ho) == "sensitivity_recovery"
    )


def test_robust_requires_both_baselines() -> None:
    ho = pd.DataFrame(
        [
            {
                "galaxy_id": "G",
                "split_name": "even_odd_index",
                "model_name": "tdf_3knot",
                "test_rmse_kms": 5.0,
            },
            {
                "galaxy_id": "G",
                "split_name": "even_odd_index",
                "model_name": "tdf_5knot",
                "test_rmse_kms": 4.0,
            },
            {
                "galaxy_id": "G",
                "split_name": "even_odd_index",
                "model_name": "nfw_refit",
                "test_rmse_kms": 10.0,
            },
            {
                "galaxy_id": "G",
                "split_name": "even_odd_index",
                "model_name": "mond_fit_a0_simple",
                "test_rmse_kms": 8.0,
            },
        ]
    )
    assert classify_expansion20_failure_mode_from_holdout("G", ho) == "robust_tdf_success"


def test_run_expansion20_benchmark_outputs() -> None:
    root = Path(__file__).resolve().parents[1]
    rotmod = root / "data/processed/sparc/sparc_rotmod_standardized.csv"
    plan = root / "outputs/tables/sparc_subset_expansion_plan.csv"
    if not rotmod.is_file() or not plan.is_file():
        pytest.skip("inputs missing")

    result = run_expansion20_benchmark(
        rotmod_path=rotmod,
        plan_path=plan,
        comparison_out=root / "outputs/tables/expansion20_model_comparison.csv",
        holdout_out=root / "outputs/tables/expansion20_holdout_validation.csv",
        failure_out=root / "outputs/tables/expansion20_failure_mode_summary.csv",
        claims_out=root / "outputs/tables/expansion20_claim_traceability.csv",
        report_out=root / "outputs/reports/expansion20_benchmark_report.md",
    )
    assert len(result["galaxy_ids"]) == 20
    fail = result["failure_mode_summary"]
    assert len(fail) == 20
    assert fail[fail["galaxy_id"] == "NGC7814"]["failure_mode_classification"].iloc[0] == "tdf_failure_mode"
    for gid in FROZEN_SENSITIVITY_RECOVERY:
        assert (
            fail[fail["galaxy_id"] == gid]["failure_mode_classification"].iloc[0]
            == "sensitivity_recovery"
        )
    assert "counts_as_primary_success" in fail.columns
    assert fail["counts_as_primary_success"].sum() == (
        fail["failure_mode_classification"] == "robust_tdf_success"
    ).sum()


def test_run_script() -> None:
    root = Path(__file__).resolve().parents[1]
    if not (root / "data/processed/sparc/sparc_rotmod_standardized.csv").is_file():
        pytest.skip("data missing")
    subprocess.run(
        ["python3", "scripts/run_expansion20_pipeline.py"],
        cwd=root,
        check=True,
        timeout=900,
    )
    report = (root / "outputs/reports/expansion20_benchmark_report.md").read_text()
    assert "expansion_20" in report.lower()
    assert "sensitivity_recovery" in report.lower()
    assert "does not disprove dark matter" in report.lower()
    claims = pd.read_csv(root / "outputs/tables/expansion20_claim_traceability.csv")
    assert (claims["status"] == "prohibited").any()
