from __future__ import annotations

import re
from pathlib import Path

import pytest

from tdf_galaxy_tau.analysis.manuscript_text import build_manuscript_tex

EXPECTED_FIGURE_ORDER = (
    "fig1_benchmark_workflow.png",
    "fig2_expansion12_vs_20_summary.png",
    "fig3_representative_successes.png",
    "fig4_ngc7814_failure.png",
    "fig5_sensitivity_recovery_cases.png",
    "fig6_holdout_rmse_comparison.png",
    "fig7_claim_boundary_map.png",
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def manuscript_text(root: Path) -> str:
    path = root / "paper" / "manuscript.tex"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return build_manuscript_tex()


@pytest.fixture
def root() -> Path:
    return _root()


def test_author_present(manuscript_text: str) -> None:
    assert "Bahman Masarrat" in manuscript_text
    assert "Independent Researcher" in manuscript_text
    assert "bmasarrat@gmail.com" in manuscript_text
    assert "[Authors TBD]" not in manuscript_text


def test_figure_include_order(manuscript_text: str) -> None:
    paths = re.findall(r"figures/(fig\d+_[^}]+\.png)", manuscript_text)
    assert paths == list(EXPECTED_FIGURE_ORDER), f"figure order mismatch: {paths}"


def test_workflow_figure_before_conclusion(manuscript_text: str) -> None:
    w = manuscript_text.find("fig1_benchmark_workflow.png")
    c = manuscript_text.find(r"\section{Conclusion}")
    assert w >= 0 and c >= 0 and w < c


def test_tables_no_malformed_escaped_labels(root: Path) -> None:
    tables_dir = root / "paper" / "tables"
    if not tables_dir.is_dir():
        pytest.skip("tables not exported")
    bad_patterns = [
        r"robust\{\}",
        r"tdf\{\}",
        r"supported\{\}",
        r"with\{\}",
        r"caveat\{\}",
    ]
    for tex in tables_dir.glob("*.tex"):
        text = tex.read_text(encoding="utf-8")
        for pat in bad_patterns:
            assert not re.search(pat, text), f"{tex.name} contains malformed pattern {pat}"


def test_bibliography_entries(root: Path) -> None:
    bib = root / "paper" / "references.bib"
    assert bib.is_file()
    text = bib.read_text(encoding="utf-8")
    for key in ("lelli2016sparc", "navarro1997", "burkert1995", "milgrom1983", "tdf_benchmark2026"):
        assert key in text
