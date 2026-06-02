from __future__ import annotations

import os
import re
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.manuscript_text import PROHIBITED_PHRASES, build_manuscript_tex
from tdf_galaxy_tau.analysis.reviewer_analysis import (
    build_statistical_summary,
    run_referee_readiness_build,
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def root() -> Path:
    return _root()


def test_statistical_summary_values(root: Path, tmp_path: Path) -> None:
    fail = root / "outputs/tables/expansion20_failure_mode_summary.csv"
    if not fail.is_file():
        pytest.skip("failure summary missing")
    mtime = os.path.getmtime(fail)
    summary = build_statistical_summary(pd.read_csv(fail))
    out = tmp_path / "paper_statistical_summary.csv"
    summary.to_csv(out, index=False)
    assert os.path.getmtime(fail) == mtime

    robust = summary[summary["metric_id"] == "robust_success_fraction"].iloc[0]
    assert int(robust["count"]) == 15
    assert int(robust["n_galaxies"]) == 20
    assert float(robust["value"]) == pytest.approx(0.75, abs=0.01)


def test_manuscript_contains_equations(root: Path) -> None:
    tex = build_manuscript_tex(root=root)
    for label in ("eq:vobs", "eq:vtau", "eq:dtaudr"):
        assert f"\\label{{{label}}}" in tex
    assert "v_{\\mathrm{obs}}^2" in tex or "v_\\mathrm{obs}" in tex
    assert "K_g" in tex
    assert "K_{\\tau}" in tex or "K_\\tau" in tex  # legacy benchmark label in prose
    assert "kappa" in tex or "\\kappa" in tex


def test_holdout_priority_paragraph(root: Path) -> None:
    tex = build_manuscript_tex(root=root).replace("\n", " ")
    assert "Many rotation-curve studies optimize in-sample fit quality" in tex
    assert "predictive holdout consistency" in tex


def test_prohibited_phrases_after_referee_edit(root: Path) -> None:
    lower = build_manuscript_tex(root=root).lower()
    for phrase in PROHIBITED_PHRASES:
        assert phrase.lower() not in lower


def test_objection_matrix_count(root: Path) -> None:
    path = root / "docs/reviewer_objection_matrix.md"
    assert path.is_file()
    n = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if re.match(r"^\| R\d+", line))
    assert n >= 20


def test_referee_build_pipeline(root: Path, tmp_path: Path) -> None:
    fail = root / "outputs/tables/expansion20_failure_mode_summary.csv"
    if not fail.is_file():
        pytest.skip("failure summary missing")
    mtime = os.path.getmtime(fail)
    stats_out = tmp_path / "paper_statistical_summary.csv"
    report_out = tmp_path / "report.md"
    run_referee_readiness_build(
        root=root,
        stats_out=stats_out,
        report_out=report_out,
    )
    assert os.path.getmtime(fail) == mtime
    assert stats_out.is_file()
    assert report_out.is_file()
    assert len(pd.read_csv(stats_out)) >= 7
