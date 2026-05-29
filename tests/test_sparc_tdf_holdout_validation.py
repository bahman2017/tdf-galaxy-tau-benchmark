from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd


def test_holdout_script_produces_table() -> None:
    root = Path(__file__).resolve().parents[1]
    cmd = [
        "python3",
        "scripts/run_sparc_tdf_holdout_validation.py",
        "--data",
        "data/processed/sparc/sparc_rotmod_standardized.csv",
        "--subset",
        "outputs/tables/sparc_subset_selection.csv",
        "--config",
        "configs/reconstruction.yaml",
    ]
    subprocess.run(cmd, check=True, cwd=root, capture_output=True, text=True)
    out = root / "outputs/tables/sparc_tdf_holdout_validation.csv"
    assert out.is_file()
    df = pd.read_csv(out)
    assert "tdf_3knot" in df["model_name"].values
    assert "test_rmse_kms" in df.columns
    assert "even_odd_index" in df["split_name"].values


def test_robustness_audit_script() -> None:
    root = Path(__file__).resolve().parents[1]
    cmd = [
        "python3",
        "scripts/audit_sparc_tdf_robustness.py",
        "--data",
        "data/processed/sparc/sparc_rotmod_standardized.csv",
        "--subset",
        "outputs/tables/sparc_subset_selection.csv",
        "--tau-profiles",
        "outputs/tables/sparc_subset_tau_profiles.csv",
        "--config",
        "configs/reconstruction.yaml",
    ]
    subprocess.run(cmd, check=True, cwd=root, capture_output=True, text=True)
    for name in (
        "sparc_tdf_robustness_summary.csv",
        "sparc_tdf_holdout_validation.csv",
        "sparc_tdf_ktau_sensitivity.csv",
        "sparc_tdf_bounds_sensitivity.csv",
        "sparc_tdf_smoothness_diagnostics.csv",
        "sparc_tdf_robust_best_model_summary.csv",
    ):
        assert (root / "outputs/tables" / name).is_file()
    report = (root / "outputs/reports/sparc_tdf_robustness_audit_report.md").read_text(encoding="utf-8")
    assert "does not validate TDF on full SPARC" in report
    assert "does not disprove dark matter" in report
