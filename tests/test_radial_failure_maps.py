from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.radial_holdout_maps import (
    TARGET_GALAXY,
    build_radial_failure_map_summary,
    ngc7814_radial_localization,
)


def test_summary_columns() -> None:
    root = Path(__file__).resolve().parents[1]
    points_path = root / "outputs/tables/sparc_holdout_point_residuals.csv"
    if not points_path.is_file():
        pytest.skip("holdout points not exported")
    points = pd.read_csv(points_path)
    summary = build_radial_failure_map_summary(points)
    required = {
        "galaxy_id",
        "model_name",
        "split_name",
        "radial_region_label",
        "rmse_kms",
        "worst_radius_kpc",
        "negative_v2_count",
        "interpretation",
    }
    assert required.issubset(summary.columns)
    loc = ngc7814_radial_localization(summary, points)
    assert loc.get("localized") is True
    assert loc.get("worst_region_tdf_3knot") is not None


def test_analyze_script() -> None:
    root = Path(__file__).resolve().parents[1]
    if not (root / "outputs/tables/sparc_holdout_point_residuals.csv").is_file():
        pytest.skip("points csv missing")
    subprocess.run(
        ["python3", "scripts/analyze_radial_holdout_failure_maps.py"],
        cwd=root,
        check=True,
    )
    report = (root / "outputs/reports/sparc_radial_holdout_failure_report.md").read_text(encoding="utf-8")
    assert TARGET_GALAXY in report
    assert "does not disprove dark matter" in report
    assert (root / "outputs/figures/sparc_subset/ngc7814_radial_holdout_residual_map.png").is_file()
