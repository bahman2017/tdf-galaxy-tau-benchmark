from __future__ import annotations

import os
from pathlib import Path

import pytest

from tdf_galaxy_tau.analysis.paper_tables import TABLE_FILES, run_paper_tables_export


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def root() -> Path:
    return _root()


def test_table_files_exist_after_export(root: Path, tmp_path: Path) -> None:
    plan = root / "outputs/tables/sparc_subset_expansion_plan.csv"
    if not plan.is_file():
        pytest.skip("expansion plan missing")
    mtime = os.path.getmtime(plan)
    out = tmp_path / "tables"
    written = run_paper_tables_export(root=root, tables_dir=out)
    assert os.path.getmtime(plan) == mtime
    assert set(written.keys()) == set(TABLE_FILES)
    for name in TABLE_FILES:
        text = (out / name).read_text(encoding="utf-8")
        assert r"\begin{table}" in text
        assert r"\caption{" in text
        assert r"\label{" in text
        assert "Source:" in text


def test_committed_table_tex_files(root: Path) -> None:
    tables_dir = root / "paper" / "tables"
    missing = [n for n in TABLE_FILES if not (tables_dir / n).is_file()]
    if missing:
        run_paper_tables_export(root=root)
    for name in TABLE_FILES:
        assert (tables_dir / name).is_file(), name
