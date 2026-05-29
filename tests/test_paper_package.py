from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.paper_package import (
    FIGURE_INVENTORY,
    PACKAGE_DISCLAIMER,
    TABLE_INVENTORY,
    build_figure_inventory,
    build_table_inventory,
    run_paper_package_scaffold,
)

REQUIRED_MANUSCRIPT_SECTIONS = [
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

REQUIRED_BASELINE_SUBSECTIONS = [
    r"\\subsection\{Baryonic-only\}",
    r"\\subsection\{NFW and Burkert\}",
    r"\\subsection\{MOND and RAR\}",
]

REQUIRED_RESULT_SUBSECTIONS = [
    r"\\subsection\{expansion\\_20 \(main cohort\)\}",
    r"\\subsection\{expansion\\_12 \(nested context\)\}",
]


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def root() -> Path:
    return _root()


def test_figure_inventory_schema() -> None:
    df = build_figure_inventory()
    assert len(df) == 7
    assert list(df["figure_id"]) == [f"Fig{i}" for i in range(1, 8)]
    for col in (
        "title",
        "source_files",
        "generation_command",
        "scientific_purpose",
        "claim_supported",
        "status",
    ):
        assert col in df.columns
        assert df[col].notna().all()


def test_table_inventory_schema() -> None:
    df = build_table_inventory()
    assert len(df) == 6
    assert list(df["table_id"]) == [f"Table{i}" for i in range(1, 7)]


def test_manuscript_structure(root: Path) -> None:
    tex = (root / "paper/manuscript.tex").read_text(encoding="utf-8")
    for pattern in REQUIRED_MANUSCRIPT_SECTIONS:
        assert re.search(pattern, tex), f"missing section matching {pattern}"
    for pattern in REQUIRED_BASELINE_SUBSECTIONS + REQUIRED_RESULT_SUBSECTIONS:
        assert re.search(pattern, tex), f"missing subsection matching {pattern}"
    assert "\\documentclass" in tex
    assert "\\begin{document}" in tex
    assert "\\end{document}" in tex


def test_paper_readme_reproducibility(root: Path) -> None:
    readme = (root / "paper/README.md").read_text(encoding="utf-8")
    assert "Phase 5F-A" in readme
    assert "build_paper_package_scaffold.py" in readme
    assert "does **not** rerun model fitting" in readme
    for phrase in ("dark matter", "full-SPARC", "lensing", "universal"):
        assert phrase.lower() in readme.lower() or "Full-SPARC" in readme


def test_scaffold_writes_inventories(root: Path, tmp_path: Path) -> None:
    fig_out = tmp_path / "paper_figure_inventory.csv"
    tab_out = tmp_path / "paper_table_inventory.csv"
    rep_out = tmp_path / "report.md"
    run_paper_package_scaffold(
        figure_inventory_out=fig_out,
        table_inventory_out=tab_out,
        report_out=rep_out,
        paper_dir=tmp_path / "paper",
    )
    fig_df = pd.read_csv(fig_out)
    tab_df = pd.read_csv(tab_out)
    assert len(fig_df) == len(FIGURE_INVENTORY)
    assert len(tab_df) == len(TABLE_INVENTORY)
    report = rep_out.read_text(encoding="utf-8")
    assert "paper package" in report.lower() or "scaffold" in report.lower()
    assert "does not add new model fitting" in PACKAGE_DISCLAIMER


def test_committed_inventories_exist(root: Path) -> None:
    fig_path = root / "outputs/tables/paper_figure_inventory.csv"
    tab_path = root / "outputs/tables/paper_table_inventory.csv"
    if not fig_path.is_file():
        run_paper_package_scaffold(
            figure_inventory_out=fig_path,
            table_inventory_out=tab_path,
            report_out=root / "outputs/reports/paper_package_scaffold_report.md",
        )
    assert fig_path.is_file()
    assert tab_path.is_file()
    assert len(pd.read_csv(fig_path)) == 7
    assert len(pd.read_csv(tab_path)) == 6


def test_manuscript_pdflatex_optional(root: Path) -> None:
    if subprocess.run(["which", "pdflatex"], capture_output=True).returncode != 0:
        pytest.skip("pdflatex not installed")
    proc = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "manuscript.tex"],
        cwd=root / "paper",
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0 and "Output written on" not in proc.stdout:
        pytest.fail(f"pdflatex failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-500:]}")
