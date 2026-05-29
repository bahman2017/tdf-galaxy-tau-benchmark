from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.normalized_patterns import (
    DEFAULT_GALAXY_IDS,
    ANALYSIS_STAGE,
    build_normalized_tau_patterns,
    build_outlier_scores,
    build_similarity_matrix,
    extract_galaxy_profile,
)
from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION


def _synthetic_tau_profiles() -> pd.DataFrame:
    rows = []
    for i, gid in enumerate(["G1", "G2", "G3"]):
        for j, r in enumerate([1.0, 2.0, 3.0, 4.0]):
            rows.append(
                {
                    "galaxy_id": gid,
                    "r_kpc": r,
                    "residual_v2_kms2": (j + 1) * 10.0 * (1 + 0.1 * i),
                    "dtaudr_reconstructed": (j + 1) * 2.0 * (1 + 0.05 * i),
                    "tau_reconstructed": float(j),
                    "data_mode": "test",
                    "reconstruction_stage": "phase_2a_radial_reconstruction",
                }
            )
    return pd.DataFrame(rows)


def test_normalize_and_grid_shape() -> None:
    prof = extract_galaxy_profile(_synthetic_tau_profiles(), "G1")
    assert len(prof.x_grid) == 100
    assert prof.dtaudr_norm.shape == (100,)
    finite = prof.dtaudr_norm[np.isfinite(prof.dtaudr_norm)]
    assert finite.size > 0
    assert np.nanmax(np.abs(finite)) <= 1.0 + 0.05


def test_similarity_self_correlation() -> None:
    _, profiles = build_normalized_tau_patterns(_synthetic_tau_profiles(), galaxy_ids=["G1", "G2"])
    sim = build_similarity_matrix(profiles)
    self_row = sim[(sim["galaxy_id_a"] == "G1") & (sim["galaxy_id_b"] == "G1")].iloc[0]
    assert self_row["dtaudr_corr"] == pytest.approx(1.0, abs=0.05)


def test_mandated_six_galaxy_analysis() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "outputs/tables/sparc_subset_tau_profiles.csv"
    if not path.is_file():
        pytest.skip("sparc_subset_tau_profiles.csv not present")
    tau = pd.read_csv(path)
    table, profiles = build_normalized_tau_patterns(tau)
    assert set(table["galaxy_id"].unique()) == set(DEFAULT_GALAXY_IDS)
    assert len(table) == 100 * len(DEFAULT_GALAXY_IDS)
    assert (table["analysis_stage"] == ANALYSIS_STAGE).all()
    outliers = build_outlier_scores(profiles)
    ng = outliers[outliers["galaxy_id"] == "NGC7814"].iloc[0]
    assert ng["classification"] == "tdf_failure_mode"
    assert bool(ng["holdout_failure_mode"])
    assert "dtaudr_rmse_rank" in outliers.columns
    assert "tau_rmse_rank" in outliers.columns
    assert "normalized_profile_outlier" in outliers.columns
    # Holdout failure must not auto-set normalized outlier; metrics decide.
    if not bool(ng["normalized_profile_outlier"]):
        assert not bool(ng["is_largest_outlier_dtaudr_norm"]) or not bool(
            ng["is_largest_outlier_gtau_norm"]
        )


def test_analyze_script() -> None:
    root = Path(__file__).resolve().parents[1]
    if not (root / "outputs/tables/sparc_subset_tau_profiles.csv").is_file():
        pytest.skip("tau profiles missing")
    subprocess.run(
        ["python3", "scripts/analyze_normalized_tau_patterns.py"],
        cwd=root,
        check=True,
    )
    assert (root / "outputs/tables/sparc_normalized_tau_patterns.csv").is_file()
    assert (root / "outputs/reports/sparc_normalized_tau_pattern_report.md").is_file()


def test_classifications_match_phase_4a() -> None:
    for gid, cls in MANDATED_GALAXY_CLASSIFICATION.items():
        assert cls in ("robust_tdf_success", "tdf_failure_mode")
