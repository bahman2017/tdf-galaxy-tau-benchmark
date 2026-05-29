from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.expansion12_radial_maps import (
    AUDIT_DISCLAIMER,
    FOCUS_GALAXY_IDS,
    PRIMARY_SPLIT,
    VALIDATION_STAGE,
    classify_tension_type,
    export_expansion12_holdout_points,
    localize_flex_recovery_failure,
    run_expansion12_radial_maps,
)
from tdf_galaxy_tau.analysis.radial_holdout_maps import build_radial_failure_map_summary


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _inputs_exist(root: Path) -> bool:
    return (
        root / "data/processed/sparc/sparc_rotmod_standardized.csv"
    ).is_file() and (root / "outputs/tables/expansion12_tau_profiles.csv").is_file()


def test_disclaimer() -> None:
    assert "does not run expansion_20" in AUDIT_DISCLAIMER.lower()
    assert "does not disprove dark matter" in AUDIT_DISCLAIMER.lower()


def test_export_two_galaxies_even_odd() -> None:
    root = _root()
    if not _inputs_exist(root):
        pytest.skip("expansion12 inputs missing")
    data = pd.read_csv(root / "data/processed/sparc/sparc_rotmod_standardized.csv")
    data = data[data["galaxy_id"].isin(FOCUS_GALAXY_IDS)]
    tau = pd.read_csv(root / "outputs/tables/expansion12_tau_profiles.csv")
    points = export_expansion12_holdout_points(
        data,
        tau,
        list(FOCUS_GALAXY_IDS),
        recon_path=root / "configs/reconstruction.yaml",
        models_path=root / "configs/models.yaml",
    )
    assert (points["validation_stage"] == VALIDATION_STAGE).all()
    assert set(points["galaxy_id"].unique()) == set(FOCUS_GALAXY_IDS)
    models = set(points["model_name"].unique())
    assert "tdf_3knot" in models
    assert "tdf_5knot" in models
    assert "nfw_refit" in models
    assert "mond_fit_a0_simple" in models
    even = points[points["split_name"] == PRIMARY_SPLIT]
    assert len(even) > 0
    assert (even["train_or_test"] == "test").all()


def test_ngc5055_knot_flexibility_not_baryonic_like_7814() -> None:
    root = _root()
    if not _inputs_exist(root):
        pytest.skip("expansion12 inputs missing")
    result = run_expansion12_radial_maps(
        rotmod_path=root / "data/processed/sparc/sparc_rotmod_standardized.csv",
        tau_path=root / "outputs/tables/expansion12_tau_profiles.csv",
        failure_diag_path=root / "outputs/tables/expansion12_failure_diagnostics.csv",
        figures_dir=root / "outputs/figures/sparc_subset",
    )
    loc5055 = result.localization["NGC5055"]
    assert loc5055["tension_type"] == "knot_flexibility_tension"
    assert loc5055["tdf_5knot_recovers_regions"] != ""
    assert classify_tension_type("NGC5055", loc5055) == "knot_flexibility_tension"


def test_localization_has_worst_region() -> None:
    root = _root()
    if not _inputs_exist(root):
        pytest.skip("expansion12 inputs missing")
    result = run_expansion12_radial_maps(
        rotmod_path=root / "data/processed/sparc/sparc_rotmod_standardized.csv",
        tau_path=root / "outputs/tables/expansion12_tau_profiles.csv",
        figures_dir=root / "outputs/figures/sparc_subset",
    )
    for gid in FOCUS_GALAXY_IDS:
        loc = result.localization[gid]
        assert loc["tdf_3knot_worst_region"] in ("inner", "middle", "outer")


def test_analyze_script() -> None:
    root = _root()
    if not _inputs_exist(root):
        pytest.skip("expansion12 inputs missing")
    subprocess.run(
        ["python3", "scripts/analyze_expansion12_radial_residual_maps.py"],
        cwd=root,
        check=True,
        timeout=600,
    )
    points = pd.read_csv(root / "outputs/tables/expansion12_holdout_point_residuals.csv")
    assert len(points) > 100
    summary = pd.read_csv(root / "outputs/tables/expansion12_radial_failure_map_summary.csv")
    assert len(summary) > 0
    report = (root / "outputs/reports/expansion12_radial_residual_map_report.md").read_text()
    assert "NGC5055" in report
    assert "UGC05253" in report
    assert "does not disprove dark matter" in report.lower()
    assert (root / "outputs/figures/sparc_subset/ngc5055_radial_holdout_residuals.png").is_file()
    assert (root / "outputs/figures/sparc_subset/ugc05253_radial_holdout_residuals.png").is_file()
    assert (
        root / "outputs/figures/sparc_subset/expansion12_flex_recovery_radial_comparison.png"
    ).is_file()

    # Phase 5B summary tables unchanged in row count (spot-check)
    comp = pd.read_csv(root / "outputs/tables/expansion12_model_comparison.csv")
    assert comp["galaxy_id"].nunique() == 12
