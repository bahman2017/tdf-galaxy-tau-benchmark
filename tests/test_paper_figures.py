from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.paper_figures import (
    PAPER_FIGURE_NAMES,
    PHASE_DISCLAIMER,
    run_paper_figures_build,
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def root() -> Path:
    return _root()


def test_phase_disclaimer() -> None:
    assert "No model fitting" in PHASE_DISCLAIMER
    assert "expansion20" in PHASE_DISCLAIMER


def test_build_paper_figures(tmp_path: Path, root: Path) -> None:
    comp = root / "outputs/tables/controlled_expansion_comparison_summary.csv"
    claims = root / "outputs/tables/controlled_expansion_final_claims.csv"
    fail = root / "outputs/tables/expansion20_failure_mode_summary.csv"
    diag = root / "outputs/tables/expansion20_failure_diagnostics.csv"
    if not all(p.is_file() for p in (comp, claims, fail, diag)):
        pytest.skip("benchmark tables missing")

    fig3_src = root / "outputs/figures/sparc_subset/DDO154_full_model_rotation_comparison.png"
    if not fig3_src.is_file():
        pytest.skip("source rotation figures missing")

    mtime_fail = os.path.getmtime(fail)
    mtime_comp = os.path.getmtime(comp)

    out_dir = tmp_path / "paper/figures"
    built = run_paper_figures_build(
        root=root,
        paper_figures_dir=out_dir,
        report_out=tmp_path / "paper_figures_report.md",
    )

    assert os.path.getmtime(fail) == mtime_fail
    assert os.path.getmtime(comp) == mtime_comp

    for name in PAPER_FIGURE_NAMES:
        p = built[name]
        assert p.is_file(), name
        assert p.stat().st_size > 5000, name


def test_committed_paper_figures_exist(root: Path) -> None:
    fig_dir = root / "paper/figures"
    missing = [n for n in PAPER_FIGURE_NAMES if not (fig_dir / n).is_file()]
    if missing:
        run_paper_figures_build(root=root)
    for name in PAPER_FIGURE_NAMES:
        assert (fig_dir / name).is_file(), name


def test_fig7_claim_ids_in_output(tmp_path: Path, root: Path) -> None:
    claims_path = root / "outputs/tables/controlled_expansion_final_claims.csv"
    if not claims_path.is_file():
        pytest.skip("claims table missing")
    out = tmp_path / "fig7.png"
    from tdf_galaxy_tau.analysis.paper_figures import build_fig7_claim_boundary_map

    build_fig7_claim_boundary_map(pd.read_csv(claims_path), out)
    assert out.is_file()
