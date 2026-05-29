from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.validation.failure_modes import (
    MANDATED_GALAXY_CLASSIFICATION,
    build_failure_mode_summary,
    build_claim_traceability_matrix,
)


def _minimal_inputs(root: Path) -> dict:
    tdir = root / "outputs/tables"
    return {
        "full_comparison": pd.read_csv(tdir / "sparc_full_model_comparison.csv"),
        "best_model": pd.read_csv(tdir / "sparc_best_model_summary.csv"),
        "robust_best": pd.read_csv(tdir / "sparc_tdf_robust_best_model_summary.csv"),
        "holdout": pd.read_csv(tdir / "sparc_tdf_holdout_validation.csv"),
        "ktau": pd.read_csv(tdir / "sparc_tdf_ktau_sensitivity.csv"),
        "bounds": pd.read_csv(tdir / "sparc_tdf_bounds_sensitivity.csv"),
        "smooth": pd.read_csv(tdir / "sparc_tdf_smoothness_diagnostics.csv"),
        "tdf_comparison": pd.read_csv(tdir / "sparc_tdf_knot_model_comparison.csv"),
        "subset_selection": pd.read_csv(tdir / "sparc_subset_selection.csv"),
    }


def test_mandated_classifications() -> None:
    assert MANDATED_GALAXY_CLASSIFICATION["NGC7814"] == "tdf_failure_mode"
    assert sum(v == "robust_tdf_success" for v in MANDATED_GALAXY_CLASSIFICATION.values()) == 5


def test_failure_mode_summary_ngc7814() -> None:
    root = Path(__file__).resolve().parents[1]
    if not (root / "outputs/tables/sparc_tdf_holdout_validation.csv").is_file():
        return
    summary = build_failure_mode_summary(**_minimal_inputs(root))
    ng = summary[summary["galaxy_id"] == "NGC7814"].iloc[0]
    assert ng["failure_mode_classification"] == "tdf_failure_mode"
    assert not bool(ng["tdf_3knot_beats_nfw_holdout"])
    assert "tdf_4knot" in str(ng["negative_v2_flags"])


def test_analyze_script() -> None:
    root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python3", "scripts/analyze_sparc_failure_modes.py"],
        check=True,
        cwd=root,
        capture_output=True,
        text=True,
    )
    report = (root / "outputs/reports/sparc_failure_mode_analysis_report.md").read_text(encoding="utf-8")
    assert "does not disprove dark matter" in report
    assert "NGC7814" in report
    assert "failure mode" in report.lower()


def test_claim_matrix_has_prohibited_claims() -> None:
    matrix = build_claim_traceability_matrix()
    f_row = matrix[matrix["claim_id"] == "F"].iloc[0]
    assert f_row["status"] == "prohibited"
    assert "disproves dark matter" in str(f_row["claim_text"])


def test_claim_script() -> None:
    root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["python3", "scripts/build_claim_traceability_matrix.py"],
        check=True,
        cwd=root,
        capture_output=True,
        text=True,
    )
    matrix = pd.read_csv(root / "outputs/tables/sparc_claim_traceability_matrix.csv")
    assert len(matrix) == 8
    c = matrix[matrix["claim_id"] == "C"].iloc[0]
    assert c["status"] == "partially_supported"
