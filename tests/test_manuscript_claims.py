from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from tdf_galaxy_tau.analysis.manuscript_text import (
    CORE_STATEMENT,
    PROHIBITED_PHRASES,
    REQUIRED_CAVEAT_PHRASES,
    build_manuscript_tex,
)
from tdf_galaxy_tau.analysis.paper_tables import TABLE_FILES

FIGURE_NAMES = (
    "fig1_benchmark_workflow.png",
    "fig2_expansion12_vs_20_summary.png",
    "fig3_representative_successes.png",
    "fig4_ngc7814_failure.png",
    "fig5_sensitivity_recovery_cases.png",
    "fig6_holdout_rmse_comparison.png",
    "fig7_claim_boundary_map.png",
)

REQUIRED_SECTIONS = [
    r"\\section\{Introduction\}",
    r"\\section\{TDF reconstruction framework\}",
    r"\\section\{Controlled SPARC benchmark protocol\}",
    r"\\section\{Data and cohort selection\}",
    r"\\section\{Baseline models\}",
    r"\\section\{Holdout validation methodology\}",
    r"\\section\{Results\}",
    r"\\section\{Failure modes and sensitivity recovery\}",
    r"\\section\{Limitations\}",
    r"\\section\{Future work\}",
    r"\\section\{Conclusion\}",
    r"\\section\{Reproducibility appendix\}",
    r"\\section\{Claim-boundary appendix\}",
]


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def root() -> Path:
    return _root()


@pytest.fixture
def manuscript_text(root: Path) -> str:
    path = root / "paper" / "manuscript.tex"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return build_manuscript_tex(root=root)


def test_author_block(manuscript_text: str) -> None:
    assert "Bahman Masarrat" in manuscript_text
    assert "[Authors TBD]" not in manuscript_text


def test_core_statement_present(manuscript_text: str) -> None:
    assert "15 of 20" in manuscript_text or "15 of 20" in CORE_STATEMENT
    assert "NGC7814" in manuscript_text
    assert "UGC00128" in manuscript_text
    assert "sensitivity-recovery" in manuscript_text or r"sensitivity\_recovery" in manuscript_text


def test_prohibited_phrases_absent(manuscript_text: str) -> None:
    lower = manuscript_text.lower()
    for phrase in PROHIBITED_PHRASES:
        assert phrase.lower() not in lower, f"prohibited phrase found: {phrase}"


def test_required_caveat_phrases_present(manuscript_text: str) -> None:
    lower = manuscript_text.lower().replace(r"\_", "_")
    for phrase in REQUIRED_CAVEAT_PHRASES:
        assert phrase.lower() in lower, f"missing caveat phrase: {phrase}"
    assert "not full-sparc" in lower or "not full-sparc validation" in lower


def test_all_figures_referenced(manuscript_text: str) -> None:
    for fig in FIGURE_NAMES:
        assert fig.replace(".png", "") in manuscript_text or fig in manuscript_text


def test_all_tables_included(manuscript_text: str) -> None:
    for table in TABLE_FILES:
        assert table in manuscript_text


def test_required_sections(manuscript_text: str) -> None:
    for pattern in REQUIRED_SECTIONS:
        assert re.search(pattern, manuscript_text), f"missing section {pattern}"


def test_benchmark_csv_unchanged_on_manuscript_build(root: Path, tmp_path: Path) -> None:
    comp = root / "outputs/tables/controlled_expansion_comparison_summary.csv"
    claims = root / "outputs/tables/controlled_expansion_final_claims.csv"
    if not comp.is_file():
        pytest.skip("benchmark csv missing")
    mt_comp = os.path.getmtime(comp)
    mt_claims = os.path.getmtime(claims)
    from tdf_galaxy_tau.analysis.paper_tables import run_paper_tables_export

    run_paper_tables_export(root=root, tables_dir=tmp_path / "tables")
    (tmp_path / "manuscript.tex").write_text(build_manuscript_tex(root=root), encoding="utf-8")
    assert os.path.getmtime(comp) == mt_comp
    assert os.path.getmtime(claims) == mt_claims


def test_compile_script_does_not_fail_without_latex(root: Path) -> None:
    from tdf_galaxy_tau.analysis.paper_compile import compile_paper_pdf

    result = compile_paper_pdf(root=root)
    assert "message" in result
    if not result["latex_available"]:
        assert result["pdf_path"] is None
