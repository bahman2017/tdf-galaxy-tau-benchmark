from __future__ import annotations

import re
from pathlib import Path

import pytest

from tdf_galaxy_tau.analysis.manuscript_text import build_manuscript_tex


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def root() -> Path:
    return _root()


@pytest.fixture
def tex(root: Path) -> str:
    return build_manuscript_tex(root=root)


def test_no_double_escaped_tdf_models(tex: str) -> None:
    assert "tdf\\\\_3knot" not in tex
    assert "tdf\\\\_5knot" not in tex
    assert r"\texttt{tdf\_3knot}" in tex


def test_no_glued_model_prose(tex: str) -> None:
    compact = re.sub(r"\\[a-zA-Z]+\{?", "", tex)
    compact = compact.replace(" ", "").replace("\n", "")
    assert "tdf3knotmodel" not in compact.lower()
    assert "tdf5knotimproves" not in compact.lower()


def test_captions_without_fig_prefix(tex: str) -> None:
    captions = re.findall(r"\\caption\{([^}]+)", tex, flags=re.DOTALL)
    assert captions, "expected captions"
    for cap in captions:
        assert not re.match(r"\s*Fig\.?\s*~?\s*\d+", cap, re.IGNORECASE), f"caption starts with Fig.: {cap[:60]}"


def test_table_source_below_tabular(root: Path) -> None:
    for path in (root / "paper/tables").glob("*.tex"):
        text = path.read_text(encoding="utf-8")
        if "Source:" not in text:
            continue
        tabular_end = text.find(r"\end{tabular}")
        source_pos = text.find("Source:")
        assert tabular_end >= 0 and source_pos > tabular_end, path.name
        assert "\\\\ \\textbf{Caveat" not in text, path.name
