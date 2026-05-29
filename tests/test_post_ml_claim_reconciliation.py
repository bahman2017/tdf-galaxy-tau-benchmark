from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.post_ml_claim_reconciliation import (
    POST_ML_CLAIMS,
    PROHIBITED_PHRASES,
    build_post_ml_results_summary_table,
    build_updated_claim_matrix,
    run_post_ml_claim_reconciliation,
)
from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION


@pytest.fixture
def root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_post_ml_claims_defined() -> None:
    ids = {c["claim_id"] for c in POST_ML_CLAIMS}
    assert ids == {"I", "J", "K", "L", "M", "N"}


def test_build_tables_from_repo_outputs(root: Path) -> None:
    pub = root / "outputs/tables/sparc_publication_summary_table.csv"
    ml = root / "outputs/tables/sparc_ml_sensitivity_holdout_comparison.csv"
    scaled = root / "outputs/tables/sparc_ml_scaled_best_model_summary.csv"
    base = root / "outputs/tables/sparc_claim_traceability_matrix.csv"
    if not all(p.is_file() for p in (pub, ml, scaled, base)):
        pytest.skip("Phase 4F/4G outputs missing")

    post = build_post_ml_results_summary_table(
        pd.read_csv(pub), pd.read_csv(ml), pd.read_csv(scaled)
    )
    assert len(post) == len(MANDATED_GALAXY_CLASSIFICATION)
    assert "NGC7814" in post["galaxy_id"].values
    ngc = post[post["galaxy_id"] == "NGC7814"].iloc[0]
    assert ngc["canonical_classification"] == "tdf_failure_mode"
    assert "canonical holdout failure" in ngc["post_ml_interpretation"].lower()

    matrix = build_updated_claim_matrix(base)
    assert len(matrix) == len(pd.read_csv(base)) + len(POST_ML_CLAIMS)
    assert set(matrix["claim_id"]) >= {"I", "N"}


def test_reconciliation_script(root: Path) -> None:
    if not (root / "outputs/tables/sparc_publication_summary_table.csv").is_file():
        pytest.skip("outputs missing")
    subprocess.run(
        ["python3", "scripts/run_post_ml_claim_reconciliation.py"],
        cwd=root,
        check=True,
        timeout=60,
    )
    post = pd.read_csv(root / "outputs/tables/sparc_post_ml_results_summary_table.csv")
    matrix = pd.read_csv(root / "outputs/tables/sparc_claim_traceability_matrix_updated.csv")
    report = (root / "outputs/reports/sparc_post_ml_claim_reconciliation_report.md").read_text()
    narrative = report.split("## Prohibited language")[0]
    assert len(post) == 6
    assert "NGC7814" in post["galaxy_id"].values
    row_i = matrix[matrix["claim_id"] == "I"].iloc[0]
    assert row_i["status"] == "supported"
    for phrase in PROHIBITED_PHRASES:
        assert phrase.lower() not in narrative.lower()


def test_run_reconciliation_returns_dataframes(root: Path) -> None:
    if not (root / "outputs/tables/sparc_publication_summary_table.csv").is_file():
        pytest.skip("outputs missing")
    post, matrix = run_post_ml_claim_reconciliation(
        publication_path=root / "outputs/tables/sparc_publication_summary_table.csv",
        ml_holdout_path=root / "outputs/tables/sparc_ml_sensitivity_holdout_comparison.csv",
        scaled_best_path=root / "outputs/tables/sparc_ml_scaled_best_model_summary.csv",
        base_matrix_path=root / "outputs/tables/sparc_claim_traceability_matrix.csv",
        updated_matrix_path=root / "outputs/tables/sparc_claim_traceability_matrix_updated.csv",
        post_ml_table_path=root / "outputs/tables/sparc_post_ml_results_summary_table.csv",
        reconciliation_report_path=root / "outputs/reports/sparc_post_ml_claim_reconciliation_report.md",
        subset_summary_path=root / "outputs/reports/sparc_post_ml_controlled_subset_results_summary.md",
    )
    assert len(post) == 6
    assert len(matrix) >= 14
