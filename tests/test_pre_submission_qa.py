from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from tdf_galaxy_tau.analysis.manuscript_text import (
    PROHIBITED_PHRASES,
    REQUIRED_CAVEAT_PHRASES,
    build_manuscript_tex,
)
from tdf_galaxy_tau.analysis.paper_tables import TABLE_FILES
from tdf_galaxy_tau.analysis.pre_submission_qa import (
    ABSTRACT_GRAMMAR_BUGS,
    FIGURE_FILES,
    STALE_MANUSCRIPT_PHRASES,
    STALE_TABLE6_PHRASES,
    perform_qa_checks,
    run_pre_submission_qa,
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def root() -> Path:
    return _root()


def test_pdf_exists(root: Path) -> None:
    pdf = root / "paper/manuscript.pdf"
    if not pdf.is_file():
        from tdf_galaxy_tau.analysis.pre_submission_qa import run_pre_submission_qa

        run_pre_submission_qa(root=root, compile_pdf=True)
    assert pdf.is_file()


def test_figures_and_tables_referenced(root: Path) -> None:
    tex = build_manuscript_tex(root=root)
    for fig in FIGURE_FILES:
        assert fig.replace(".png", "") in tex or fig in tex
    for table in TABLE_FILES:
        assert table in tex


def test_prohibited_and_caveats(root: Path) -> None:
    tex = build_manuscript_tex(root=root).lower().replace(r"\_", "_")
    for phrase in PROHIBITED_PHRASES:
        assert phrase.lower() not in tex
    for phrase in REQUIRED_CAVEAT_PHRASES:
        assert phrase.lower() in tex.replace("$", "")


def test_stale_wording_absent_manuscript(root: Path) -> None:
    tex = build_manuscript_tex(root=root).lower()
    for phrase in STALE_MANUSCRIPT_PHRASES:
        assert phrase.lower() not in tex


def test_table6_expansion20_assumptions(root: Path) -> None:
    path = root / "paper/tables/table6_assumptions_limitations.tex"
    if not path.is_file():
        from tdf_galaxy_tau.analysis.paper_tables import run_paper_tables_export

        run_paper_tables_export(root=root)
    text = path.read_text(encoding="utf-8")
    assert "expansion-20" in text or "expansion\_20" in text
    assert r"\texttt{tdf\_3knot}" in text
    assert "tdf\\\\_3knot" not in text
    for stale in STALE_TABLE6_PHRASES:
        assert stale not in text


def test_abstract_grammar(root: Path) -> None:
    tex = build_manuscript_tex(root=root)
    for bug in ABSTRACT_GRAMMAR_BUGS:
        assert bug not in tex
    assert "We use train-only" in tex and "even/odd holdout" in tex
    assert "expansion-20 cohort" in tex
    assert "$K_\\tau$. In the pre-registered" in tex
    assert ", In the pre-registered" not in tex
    assert "Using train-only" not in tex


def test_benchmark_csv_unchanged(root: Path) -> None:
    comp = root / "outputs/tables/controlled_expansion_comparison_summary.csv"
    if not comp.is_file():
        pytest.skip("benchmark csv missing")
    mtime = os.path.getmtime(comp)
    run_pre_submission_qa(root=root, compile_pdf=False)
    assert os.path.getmtime(comp) == mtime


def test_perform_qa_checks_pass(root: Path) -> None:
    tex = build_manuscript_tex(root=root)
    checks = perform_qa_checks(
        root=root,
        tex=tex,
        pdf_path=root / "paper/manuscript.pdf",
    )
    assert not checks["stale_manuscript"]
    assert not checks["stale_table6"]
    assert not checks["abstract_bugs"]
    assert not checks["prohibited_hits"]
