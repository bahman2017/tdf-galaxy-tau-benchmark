from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.reconstruction.radial_tau import load_selected_galaxy_ids
from tdf_galaxy_tau.validation.holdout import radial_region_label_for_index
from tdf_galaxy_tau.validation.holdout_residuals import (
    COMPARISON_MODE,
    VALIDATION_STAGE,
    export_holdout_point_residuals,
    load_holdout_export_configs,
)


def test_radial_region_labels() -> None:
    assert radial_region_label_for_index(12, 0) == "inner"
    assert radial_region_label_for_index(12, 11) == "outer"


def test_export_small_galaxy() -> None:
    root = Path(__file__).resolve().parents[1]
    data_path = root / "data/processed/sparc/sparc_rotmod_standardized.csv"
    tau_path = root / "outputs/tables/sparc_subset_tau_profiles.csv"
    if not data_path.is_file() or not tau_path.is_file():
        pytest.skip("SPARC inputs missing")
    recon, models = load_holdout_export_configs(
        root / "configs/reconstruction.yaml",
        root / "configs/models.yaml",
    )
    data = pd.read_csv(data_path)
    tau = pd.read_csv(tau_path)
    points = export_holdout_point_residuals(
        data,
        tau,
        ["DDO154"],
        recon,
        models,
        tdf_models=("tdf_3knot",),
        baseline_models=("nfw_refit",),
    )
    assert (points["train_or_test"] == "test").all()
    assert (points["comparison_mode"] == COMPARISON_MODE).all()
    assert (points["validation_stage"] == VALIDATION_STAGE).all()
    assert "residual_kms" in points.columns
    assert points["galaxy_id"].nunique() == 1
    assert len(points) > 0


def test_export_script() -> None:
    root = Path(__file__).resolve().parents[1]
    if not (root / "data/processed/sparc/sparc_rotmod_standardized.csv").is_file():
        pytest.skip("data missing")
    subprocess.run(
        ["python3", "scripts/export_sparc_holdout_residuals.py"],
        cwd=root,
        check=True,
    )
    out = root / "outputs/tables/sparc_holdout_point_residuals.csv"
    assert out.is_file()
    df = pd.read_csv(out)
    assert set(df["galaxy_id"].unique()) == set(load_selected_galaxy_ids(root / "outputs/tables/sparc_subset_selection.csv"))
    assert "tdf_5knot" in df["model_name"].values
    assert "even_odd_index" in df["split_name"].values
