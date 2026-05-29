from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.models.fitting import (
    BaselineAuditConfig,
    audit_baseline_fits,
    parse_bounds_tuple,
    summarize_baseline_audit,
)


def test_parse_bounds_tuple_from_string() -> None:
    assert parse_bounds_tuple("(100000.0, 1000000000.0)") == (100000.0, 1000000000.0)


def test_audit_detects_burkert_lower_rho_bound() -> None:
    comparison = pd.DataFrame(
        [
            {
                "model_name": "burkert",
                "galaxy_id": "G1",
                "fit_success": True,
                "fit_status": "ok:4",
                "rmse_kms": 30.0,
                "reduced_chi_square": 100.0,
                "aic": 110.0,
                "bic": 115.0,
            }
        ]
    )
    parameters = pd.DataFrame(
        [
            {
                "model_name": "burkert",
                "galaxy_id": "G1",
                "rho_0": 100000.0,
                "r_0": 5.0,
                "rho_0_bounds": "(100000.0, 1000000000.0)",
                "r_0_bounds": "(0.1, 100.0)",
            }
        ]
    )
    audit = audit_baseline_fits(
        comparison,
        parameters,
        median_v_obs_by_galaxy={"G1": 100.0},
        config=BaselineAuditConfig(boundary_tolerance_fraction=0.01),
    )
    assert bool(audit.loc[0, "rho_0_lower_bound"])
    assert audit.loc[0, "model_status"] in {"boundary_limited", "boundary_limited_and_high_chi_square"}


def test_audit_flags_high_reduced_chi_square() -> None:
    comparison = pd.DataFrame(
        [
            {
                "model_name": "baryonic_only",
                "galaxy_id": "G1",
                "fit_success": True,
                "fit_status": "fixed",
                "rmse_kms": 50.0,
                "reduced_chi_square": 25.0,
                "aic": 30.0,
                "bic": 35.0,
            }
        ]
    )
    audit = audit_baseline_fits(comparison, pd.DataFrame(), median_v_obs_by_galaxy={"G1": 100.0})
    assert bool(audit.loc[0, "very_high_reduced_chi_square"])
    assert audit.loc[0, "model_status"] == "high_chi_square"


def test_summarize_nfw_best_rmse() -> None:
    comparison = pd.DataFrame(
        [
            {"model_name": "baryonic_only", "galaxy_id": "G1", "fit_success": True, "fit_status": "x", "rmse_kms": 40.0, "reduced_chi_square": 50.0, "aic": 50.0, "bic": 50.0},
            {"model_name": "nfw", "galaxy_id": "G1", "fit_success": True, "fit_status": "x", "rmse_kms": 5.0, "reduced_chi_square": 10.0, "aic": 12.0, "bic": 13.0},
            {"model_name": "burkert", "galaxy_id": "G1", "fit_success": True, "fit_status": "x", "rmse_kms": 20.0, "reduced_chi_square": 30.0, "aic": 32.0, "bic": 33.0},
        ]
    )
    audit = audit_baseline_fits(comparison, pd.DataFrame())
    summary = summarize_baseline_audit(audit)
    assert summary["nfw_best_rmse_all_galaxies"] is True


def test_audit_refit_output_has_model_status() -> None:
    root = Path(__file__).resolve().parents[1]
    audit_path = root / "outputs/tables/sparc_baseline_fit_audit_refit.csv"
    if not audit_path.is_file():
        return
    audit = pd.read_csv(audit_path)
    assert "model_status" in audit.columns


def test_legacy_vs_refit_delta_table_exists() -> None:
    root = Path(__file__).resolve().parents[1]
    delta = root / "outputs/tables/sparc_baseline_legacy_vs_refit_delta.csv"
    if not delta.is_file():
        return
    df = pd.read_csv(delta)
    for col in (
        "galaxy_id",
        "model_name",
        "rmse_legacy",
        "rmse_refit",
        "delta_rmse",
        "legacy_model_status",
        "refit_model_status",
        "boundary_status_improved",
        "chi_square_status_improved",
    ):
        assert col in df.columns
    assert set(df["model_name"].unique()).issubset({"baryonic_only", "nfw", "burkert"})


def test_audit_script_runs_on_existing_outputs() -> None:
    root = Path(__file__).resolve().parents[1]
    comp = root / "outputs/tables/sparc_baseline_model_comparison.csv"
    params = root / "outputs/tables/sparc_baseline_fit_parameters.csv"
    if not comp.is_file():
        return
    cmd = [
        "python3",
        "scripts/audit_sparc_baseline_fits.py",
        "--comparison",
        str(comp),
        "--parameters",
        str(params),
        "--config",
        "configs/models.yaml",
    ]
    subprocess.run(cmd, check=True, cwd=root, capture_output=True, text=True)
    report = (root / "outputs/reports/sparc_baseline_fit_audit_report.md").read_text(encoding="utf-8")
    assert "does not disprove dark matter" in report
    assert "boundary-limited" in report.lower()
