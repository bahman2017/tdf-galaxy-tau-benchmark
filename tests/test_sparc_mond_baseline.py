from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from tdf_galaxy_tau.metrics.information_criteria import model_parameter_count
from tdf_galaxy_tau.models.fitting import fit_mond_a0_simple, fit_mond_fixed_a0


def test_fixed_a0_n_parameters_zero() -> None:
    assert model_parameter_count("mond_fixed_a0_simple") == 0


def test_fitted_a0_n_parameters_one() -> None:
    assert model_parameter_count("mond_fit_a0_simple") == 1


def test_mond_fit_on_synthetic_curve() -> None:
    r = np.linspace(0.5, 12.0, 15)
    v_bar = np.linspace(20.0, 80.0, 15)
    fixed = fit_mond_fixed_a0(r, v_bar * 1.05, np.full(15, 3.0), v_bar, a0_ms2=1.2e-10)
    assert fixed.fit_success
    fitted = fit_mond_a0_simple(
        r,
        fixed.v_model_kms,
        np.full(15, 2.0),
        v_bar,
        log10_a0_bounds=(-11.5, -9.5),
    )
    assert fitted.fit_success
    assert fitted.n_parameters == 1


def test_mond_pipeline_outputs() -> None:
    root = Path(__file__).resolve().parents[1]
    cmd_fit = [
        "python3",
        "scripts/fit_sparc_mond_baseline.py",
        "--data",
        "data/processed/sparc/sparc_rotmod_standardized.csv",
        "--subset",
        "outputs/tables/sparc_subset_selection.csv",
        "--config",
        "configs/models.yaml",
    ]
    subprocess.run(cmd_fit, check=True, cwd=root, capture_output=True, text=True)

    cmd_cmp = [
        "python3",
        "scripts/compare_sparc_baselines_with_mond.py",
        "--halo",
        "outputs/tables/sparc_baseline_model_comparison_refit.csv",
        "--mond",
        "outputs/tables/sparc_mond_model_comparison.csv",
    ]
    subprocess.run(cmd_cmp, check=True, cwd=root, capture_output=True, text=True)

    combined = pd.read_csv(root / "outputs/tables/sparc_baseline_with_mond_comparison.csv")
    models = set(combined["model_name"].unique())
    assert "mond_fixed_a0_simple" in models
    assert "mond_fit_a0_simple" in models
    assert "nfw_refit" in models
    assert "tdf" not in {m.lower() for m in models}

    report = (root / "outputs/reports/sparc_mond_baseline_report.md").read_text(encoding="utf-8")
    assert "does not fit or validate TDF" in report
    assert "does not disprove dark matter" in report
    assert "does not establish MOND" in report or "ΛCDM" in report
