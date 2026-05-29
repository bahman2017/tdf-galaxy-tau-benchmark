from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd


def test_tdf_pipeline_and_combined_table() -> None:
    root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [
            "python3",
            "scripts/fit_sparc_tdf_knot_model.py",
            "--data",
            "data/processed/sparc/sparc_rotmod_standardized.csv",
            "--subset",
            "outputs/tables/sparc_subset_selection.csv",
            "--tau-profiles",
            "outputs/tables/sparc_subset_tau_profiles.csv",
            "--config",
            "configs/reconstruction.yaml",
        ],
        check=True,
        cwd=root,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            "python3",
            "scripts/compare_sparc_models.py",
            "--halo-mond",
            "outputs/tables/sparc_baseline_with_mond_comparison.csv",
            "--tdf",
            "outputs/tables/sparc_tdf_knot_model_comparison.csv",
        ],
        check=True,
        cwd=root,
        capture_output=True,
        text=True,
    )

    full = pd.read_csv(root / "outputs/tables/sparc_full_model_comparison.csv")
    models = set(full["model_name"].unique())
    assert "tdf_3knot" in models
    assert "nfw_refit" in models
    assert "mond_fit_a0_simple" in models
    assert "direct_tau_reconstruction" not in models
    assert "tdf" not in {m.lower() for m in models if m == "tdf"}

    summary = pd.read_csv(root / "outputs/tables/sparc_best_model_summary.csv")
    assert "tdf_3knot_beats_nfw_refit_by_aic" in summary.columns

    report = (root / "outputs/reports/sparc_full_model_comparison_report.md").read_text(encoding="utf-8")
    assert "does not disprove dark matter" in report
    assert "does not validate TDF on full SPARC" in report
    assert "diagnostic only" in report.lower()


def test_direct_reconstruction_not_in_tdf_metrics_table() -> None:
    path = Path("outputs/tables/sparc_tdf_knot_model_comparison.csv")
    if not path.is_file():
        return
    df = pd.read_csv(path)
    assert "direct_tau_reconstruction" not in df["model_name"].values
