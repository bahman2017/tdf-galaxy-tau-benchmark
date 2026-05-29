from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.ngc7814_diagnostics import (
    TARGET_GALAXY,
    build_failure_diagnostics_table,
    run_ngc7814_diagnostics,
)


def _paths(root: Path) -> dict[str, Path]:
    return {
        "rotmod": root / "data/processed/sparc/sparc_rotmod_standardized.csv",
        "tau": root / "outputs/tables/sparc_subset_tau_profiles.csv",
        "knot": root / "outputs/tables/sparc_tdf_knot_fit_parameters.csv",
        "outliers": root / "outputs/tables/sparc_tau_pattern_outlier_scores.csv",
        "holdout": root / "outputs/tables/sparc_tdf_holdout_validation.csv",
        "smoothness": root / "outputs/tables/sparc_tdf_smoothness_diagnostics.csv",
    }


@pytest.mark.parametrize("key", ["rotmod", "tau", "knot", "outliers", "holdout", "smoothness"])
def test_inputs_exist(key: str) -> None:
    root = Path(__file__).resolve().parents[1]
    p = _paths(root)[key]
    if not p.is_file():
        pytest.skip(f"{p} missing")


def test_failure_diagnostics_has_six_galaxies() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = _paths(root)
    if not paths["rotmod"].is_file():
        pytest.skip("data missing")
    rotmod = pd.read_csv(paths["rotmod"])
    tau = pd.read_csv(paths["tau"])
    knot = pd.read_csv(paths["knot"])
    table = build_failure_diagnostics_table(rotmod, tau, knot)
    assert len(table) == 6
    ng = table[table["galaxy_id"] == TARGET_GALAXY].iloc[0]
    assert ng["median_vbulge_over_vbar"] > 0.5
    assert ng["fraction_negative_residual_v2"] > 0


def test_ngc7814_holdout_not_forced_as_shape_rank1() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = _paths(root)
    if not paths["outliers"].is_file():
        pytest.skip("outlier table missing")
    outliers = pd.read_csv(paths["outliers"])
    ng = outliers[outliers["galaxy_id"] == TARGET_GALAXY].iloc[0]
    assert bool(ng["holdout_failure_mode"])
    # Phase 4C: NGC3198 has higher shape score than NGC7814
    n31 = outliers[outliers["galaxy_id"] == "NGC3198"].iloc[0]
    assert float(n31["pattern_outlier_score"]) > float(ng["pattern_outlier_score"])


def test_analyze_script() -> None:
    root = Path(__file__).resolve().parents[1]
    if not (root / "outputs/tables/sparc_subset_tau_profiles.csv").is_file():
        pytest.skip("tau profiles missing")
    subprocess.run(
        ["python3", "scripts/analyze_ngc7814_failure_mode.py"],
        cwd=root,
        check=True,
    )
    assert (root / "outputs/reports/ngc7814_failure_mode_report.md").is_file()
    assert (root / "outputs/tables/ngc7814_failure_diagnostics.csv").is_file()
