"""Repository cleanup audit artifacts (no science changes)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tdf_galaxy_tau.analysis.repository_cleanup import (
    CATEGORIES,
    build_file_inventory,
    run_audit,
)


@pytest.fixture
def root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_cleanup_audit_artifacts_exist(root: Path) -> None:
    run_audit(root)
    inv = root / "outputs/tables/repository_file_inventory.csv"
    cand = root / "outputs/tables/repository_cleanup_candidates.csv"
    report = root / "outputs/reports/repository_cleanup_audit_report.md"
    plan = root / "docs/repository_cleanup_plan.md"
    assert inv.is_file() and inv.stat().st_size > 0
    assert cand.is_file()
    assert report.is_file()
    assert plan.is_file()


def test_inventory_categories_valid(root: Path) -> None:
    records = build_file_inventory(root)
    cats = {r.category for r in records}
    assert cats <= set(CATEGORIES)
    assert any(r.rel_path.startswith("src/") and r.category == "keep_core" for r in records)
    assert any("controlled_expansion_final_claims.csv" in r.rel_path for r in records)


def test_readme_release_sections(root: Path) -> None:
    text = (root / "README.md").read_text(encoding="utf-8")
    assert "expansion-20" in text
    assert "15 of 20" in text
    assert "tdf_5knot" in text
    assert "docs/repository_map.md" in text
    assert "docs/reproducibility_commands.md" in text
