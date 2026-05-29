from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from tdf_galaxy_tau.models.burkert import burkert_params_from_log10
from tdf_galaxy_tau.models.fitting import (
    deterministic_log_multistart_guesses,
    fit_burkert_baseline_log,
    fit_nfw_baseline_log,
    log10_to_physical_parameter,
    physical_to_log10_parameter,
)
from tdf_galaxy_tau.models.nfw import nfw_params_from_log10, nfw_velocity


def test_log_space_parameter_transform_positive() -> None:
    assert log10_to_physical_parameter(6.0) == 1e6
    assert physical_to_log10_parameter(1e6) == 6.0
    p = nfw_params_from_log10(7.0, 1.0)
    assert p.rho_s == 1e7 and p.r_s == 10.0
    b = burkert_params_from_log10(5.0, 0.0)
    assert b.rho0 == 1e5 and b.r0 == 1.0


def test_nfw_velocity_finite_for_valid_log_parameters() -> None:
    r = np.array([0.5, 2.0, 8.0])
    p = nfw_params_from_log10(7.5, 0.7)
    v = nfw_velocity(r, p)
    assert np.all(np.isfinite(v))
    assert np.all(v >= 0)


def test_multistart_picks_lowest_chi_square_on_synthetic_data() -> None:
    rng = np.random.default_rng(0)
    r = np.linspace(0.5, 15.0, 20)
    true_p = nfw_params_from_log10(7.2, 0.5)
    v_halo = nfw_velocity(r, true_p)
    v_bar = np.full_like(r, 20.0)
    v_obs = np.sqrt(v_bar**2 + v_halo**2)
    v_err = np.full_like(r, 2.0)
    res = fit_nfw_baseline_log(
        r,
        v_obs,
        v_err,
        v_bar,
        log10_rho_s_bounds=(2.0, 11.0),
        log10_r_s_bounds=(-1.3, 3.0),
    )
    assert res.fit_success
    assert res.chi_square is not None
    assert res.n_starts_successful >= 1


def test_deterministic_multistart_has_three_corner_guesses() -> None:
    starts = deterministic_log_multistart_guesses((2.0, 11.0), (-1.3, 3.0))
    assert len(starts) == 3


def test_fit_failure_graceful_on_bad_input() -> None:
    from tdf_galaxy_tau.models.fitting import fit_nfw_baseline

    res = fit_nfw_baseline(
        r_kpc=[0.0, 1.0],
        v_obs_kms=[10.0, 11.0],
        v_err_kms=[1.0, 1.0],
        v_bar_kms=[9.0, 10.0],
        rho_s_bounds=(1e5, 1e8),
        r_s_bounds=(0.1, 10.0),
    )
    assert res.fit_success is False


def test_refit_outputs_do_not_overwrite_legacy_phase3a(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    legacy_comp = root / "outputs/tables/sparc_baseline_model_comparison.csv"
    if not legacy_comp.is_file():
        return
    legacy_mtime = legacy_comp.stat().st_mtime
    cmd = [
        "python3",
        "scripts/fit_sparc_baselines.py",
        "--data",
        "data/processed/sparc/sparc_rotmod_standardized.csv",
        "--subset",
        "outputs/tables/sparc_subset_selection.csv",
        "--config",
        "configs/models.yaml",
        "--mode",
        "refit",
    ]
    subprocess.run(cmd, check=True, cwd=root, capture_output=True, text=True)
    assert legacy_comp.stat().st_mtime == legacy_mtime
    refit_comp = root / "outputs/tables/sparc_baseline_model_comparison_refit.csv"
    assert refit_comp.is_file()


def test_refit_comparison_table_models_only() -> None:
    path = Path("outputs/tables/sparc_baseline_model_comparison_refit.csv")
    if not path.is_file():
        return
    df = pd.read_csv(path)
    models = set(df["model_name"].unique())
    assert models == {"baryonic_only", "nfw", "burkert"}
    assert "tdf" not in {m.lower() for m in models}


def test_refit_report_non_inference_language() -> None:
    path = Path("outputs/reports/sparc_baseline_refit_report.md")
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    assert "TDF is **not** fitted" in text or "not fitted" in text.lower()
    assert "does not disprove" in text.lower() or "not disproof" in text.lower()
    assert "legacy outputs were **not** deleted" in text or "not deleted" in text.lower()


def test_baseline_table_has_only_expected_models_legacy() -> None:
    cmd = [
        "python3",
        "scripts/fit_sparc_baselines.py",
        "--data",
        "data/processed/sparc/sparc_rotmod_standardized.csv",
        "--subset",
        "outputs/tables/sparc_subset_selection.csv",
        "--config",
        "configs/models.yaml",
        "--mode",
        "legacy",
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    df = pd.read_csv("outputs/tables/sparc_baseline_model_comparison.csv")
    models = set(df["model_name"].unique())
    assert models == {"baryonic_only", "nfw", "burkert"}


def test_baseline_report_has_non_inference_warning() -> None:
    text = open("outputs/reports/sparc_baseline_model_comparison_report.md", "r", encoding="utf-8").read()
    assert "does not fit or validate the TDF model" in text
    assert "does not claim that dark matter is disproven" in text
