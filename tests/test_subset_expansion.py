from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.data.subset_expansion import (
    PROTOCOL_DISCLAIMER,
    apply_expansion_selections,
    build_expansion_candidates,
    load_subset_expansion_config,
    run_subset_expansion_planning,
)

ORIGINAL_SIX = {"DDO154", "IC2574", "NGC2403", "NGC3198", "NGC6503", "NGC7814"}


def test_config_loads() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_subset_expansion_config(root / "configs/subset_expansion.yaml")
    assert set(cfg.original_ids) == ORIGINAL_SIX
    assert cfg.min_radial_points >= 12


def test_excludes_original_six() -> None:
    root = Path(__file__).resolve().parents[1]
    rotmod = root / "data/processed/sparc/sparc_rotmod_standardized.csv"
    photo = root / "data/processed/sparc/sparc_photometry_metadata.csv"
    if not rotmod.is_file() or not photo.is_file():
        pytest.skip("data missing")
    cfg = load_subset_expansion_config(root / "configs/subset_expansion.yaml")
    cand = build_expansion_candidates(pd.read_csv(rotmod), pd.read_csv(photo), cfg=cfg)
    assert not set(cand["galaxy_id"]).intersection(ORIGINAL_SIX)


def test_expansion_counts() -> None:
    root = Path(__file__).resolve().parents[1]
    rotmod = root / "data/processed/sparc/sparc_rotmod_standardized.csv"
    photo = root / "data/processed/sparc/sparc_photometry_metadata.csv"
    if not rotmod.is_file() or not photo.is_file():
        pytest.skip("data missing")
    cfg = load_subset_expansion_config(root / "configs/subset_expansion.yaml")
    cand = build_expansion_candidates(pd.read_csv(rotmod), pd.read_csv(photo), cfg=cfg)
    cand = apply_expansion_selections(cand, cfg)
    n12 = int(cand["selected_for_expansion_12"].sum())
    n20 = int(cand["selected_for_expansion_20"].sum())
    assert n12 == 6
    assert n20 == 14
    pick12 = set(cand.loc[cand["selected_for_expansion_12"], "galaxy_id"])
    pick20 = set(cand.loc[cand["selected_for_expansion_20"], "galaxy_id"])
    assert pick12.issubset(pick20)


def test_candidate_columns() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "outputs/tables/sparc_subset_expansion_candidates.csv"
    if not path.is_file():
        pytest.skip("run plan script first")
    df = pd.read_csv(path)
    required = {
        "galaxy_id",
        "n_points",
        "radial_coverage_kpc",
        "v_obs_range",
        "median_v_err_kms",
        "morphology_type",
        "bulge_proxy",
        "selection_score",
        "selected_for_expansion_12",
        "selected_for_expansion_20",
        "selection_reason",
        "caveat",
    }
    assert required.issubset(df.columns)


def test_plan_script_and_report(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    if not (root / "data/processed/sparc/sparc_rotmod_standardized.csv").is_file():
        pytest.skip("data missing")
    subprocess.run(
        ["python3", "scripts/plan_sparc_subset_expansion.py"],
        cwd=root,
        check=True,
        timeout=60,
    )
    report = (root / "outputs/reports/sparc_subset_expansion_protocol_report.md").read_text()
    assert PROTOCOL_DISCLAIMER.split(".")[0] in report
    assert "expansion_12" in report
    plan = pd.read_csv(root / "outputs/tables/sparc_subset_expansion_plan.csv")
    assert len(plan[plan["cohort_name"] == "expansion_12"]) == 12
    assert len(plan[plan["cohort_name"] == "expansion_20"]) == 20


def test_run_pipeline(root: Path | None = None) -> None:
    root = root or Path(__file__).resolve().parents[1]
    if not (root / "data/processed/sparc/sparc_rotmod_standardized.csv").is_file():
        pytest.skip("data missing")
    candidates, plan = run_subset_expansion_planning(
        rotmod_path=root / "data/processed/sparc/sparc_rotmod_standardized.csv",
        photometry_path=root / "data/processed/sparc/sparc_photometry_metadata.csv",
        config_path=root / "configs/subset_expansion.yaml",
    )
    assert len(candidates) > 50
    assert len(plan) == 32
