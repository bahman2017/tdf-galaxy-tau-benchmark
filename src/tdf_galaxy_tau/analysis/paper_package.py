from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

PACKAGE_VERSION = "phase_5f_a_paper_package_scaffold"

PACKAGE_DISCLAIMER = (
    "This phase prepares a publication manuscript scaffold and frozen figure/table "
    "inventory only. It does not add new model fitting, does not change benchmark "
    "outputs, and does not extend claims beyond Phases 5B–5E audited results."
)

FIGURE_INVENTORY: list[dict[str, str]] = [
    {
        "figure_id": "Fig1",
        "title": "Controlled benchmark workflow and analysis phases",
        "source_files": "docs/project_status.md; configs/subset_expansion.yaml; scripts/run_expansion20_pipeline.py",
        "generation_command": "python3 scripts/build_paper_figures.py",
        "scientific_purpose": "Orient reader to preregistered cohort, pipeline, and audit phases",
        "claim_supported": "C20-A (reproducible protocol)",
        "status": "existing",
    },
    {
        "figure_id": "Fig2",
        "title": "expansion_12 vs expansion_20 classification summary",
        "source_files": "outputs/tables/controlled_expansion_comparison_summary.csv; outputs/figures/sparc_subset/expansion20_tdf3_vs_tdf5_gap.png",
        "generation_command": "python3 scripts/build_paper_figures.py",
        "scientific_purpose": "Show cohort growth and primary vs sensitivity classification counts",
        "claim_supported": "C20-B; C20-C (sensitivity separate)",
        "status": "existing",
    },
    {
        "figure_id": "Fig3",
        "title": "Representative robust successes — rotation curves",
        "source_files": "outputs/figures/sparc_subset/DDO154_full_model_rotation_comparison.png; outputs/figures/sparc_subset/NGC2403_full_model_rotation_comparison.png; outputs/tables/expansion20_model_comparison.csv",
        "generation_command": "python3 scripts/build_paper_figures.py",
        "scientific_purpose": "Illustrate competitive TDF vs baselines on holdout-success galaxies",
        "claim_supported": "C20-B (subset examples only)",
        "status": "existing",
    },
    {
        "figure_id": "Fig4",
        "title": "NGC7814 canonical all-TDF holdout failure",
        "source_files": "outputs/figures/sparc_subset/ngc7814_baryonic_components.png; outputs/figures/sparc_subset/ngc7814_radial_holdout_residual_map.png; outputs/tables/expansion20_failure_diagnostics.csv",
        "generation_command": "python3 scripts/build_paper_figures.py",
        "scientific_purpose": "Document mandated failure; inner baryonic tension",
        "claim_supported": "C20-D",
        "status": "existing",
    },
    {
        "figure_id": "Fig5",
        "title": "Sensitivity-recovery cases (NGC5055, UGC05253, UGC12506)",
        "source_files": "outputs/figures/sparc_subset/ngc5055_radial_holdout_residuals.png; outputs/figures/sparc_subset/ugc05253_radial_holdout_residuals.png; outputs/figures/sparc_subset/expansion20_failure_case_residuals.png; outputs/tables/expansion20_case_review_summary.csv",
        "generation_command": "python3 scripts/build_paper_figures.py",
        "scientific_purpose": "Show tdf_3knot failure vs tdf_5knot recovery; not primary success",
        "claim_supported": "C20-C (sensitivity only)",
        "status": "existing",
    },
    {
        "figure_id": "Fig6",
        "title": "Holdout RMSE comparison (even/odd, primary models)",
        "source_files": "outputs/tables/expansion20_holdout_validation.csv; outputs/tables/expansion20_failure_mode_summary.csv",
        "generation_command": "python3 scripts/build_paper_figures.py",
        "scientific_purpose": "Summarize predictive performance gate for claims",
        "claim_supported": "C20-B; C20-D",
        "status": "existing",
    },
    {
        "figure_id": "Fig7",
        "title": "Claim-boundary and evidence map",
        "source_files": "outputs/tables/controlled_expansion_final_claims.csv; docs/paper_ready_claims.md",
        "generation_command": "python3 scripts/build_paper_figures.py",
        "scientific_purpose": "Make supported vs prohibited claims explicit for readers",
        "claim_supported": "C20-A through C20-H",
        "status": "existing",
    },
]

TABLE_INVENTORY: list[dict[str, str]] = [
    {
        "table_id": "Table1",
        "title": "Preregistered cohort summary (expansion_12 and expansion_20)",
        "source_files": "outputs/tables/sparc_subset_expansion_plan.csv; outputs/tables/expansion20_subset_selection.csv; outputs/tables/expansion12_subset_selection.csv",
        "generation_command": "Phase 5A plan_sparc_subset_expansion.py; frozen plan CSV",
        "scientific_purpose": "Document galaxy membership and selection order",
        "claim_supported": "C20-A",
        "status": "existing",
    },
    {
        "table_id": "Table2",
        "title": "Holdout RMSE comparison (even/odd index)",
        "source_files": "outputs/tables/expansion20_failure_mode_summary.csv; outputs/tables/expansion20_holdout_validation.csv",
        "generation_command": "python3 scripts/run_expansion20_pipeline.py (already run); export subset of holdout table",
        "scientific_purpose": "Primary predictive metric for all models",
        "claim_supported": "C20-B",
        "status": "existing",
    },
    {
        "table_id": "Table3",
        "title": "Failure-mode classification summary",
        "source_files": "outputs/tables/controlled_expansion_comparison_summary.csv; outputs/tables/expansion20_failure_mode_summary.csv",
        "generation_command": "python3 scripts/build_controlled_expansion_final_audit.py",
        "scientific_purpose": "Report robust vs sensitivity vs failure vs mixed counts",
        "claim_supported": "C20-B; C20-C; C20-D",
        "status": "existing",
    },
    {
        "table_id": "Table4",
        "title": "Non-robust case diagnostics",
        "source_files": "outputs/tables/expansion20_failure_diagnostics.csv; outputs/tables/expansion20_case_review_summary.csv",
        "generation_command": "python3 scripts/analyze_expansion20_failure_modes.py",
        "scientific_purpose": "Detail five non-robust galaxies including UGC12506 archetype",
        "claim_supported": "C20-C; C20-D",
        "status": "existing",
    },
    {
        "table_id": "Table5",
        "title": "Claim traceability matrix (expansion cohort)",
        "source_files": "outputs/tables/controlled_expansion_final_claims.csv; outputs/tables/expansion20_claim_traceability.csv",
        "generation_command": "python3 scripts/build_controlled_expansion_final_audit.py",
        "scientific_purpose": "Authoritative allowed/prohibited language",
        "claim_supported": "C20-A through C20-H",
        "status": "existing",
    },
    {
        "table_id": "Table6",
        "title": "Assumptions and limitations",
        "source_files": "docs/assumptions.md; docs/limitations.md",
        "generation_command": "Manual curation from repository docs (no new fits)",
        "scientific_purpose": "Methods transparency and scope boundaries",
        "claim_supported": "Scope caveats (not C20-E/F/G/H)",
        "status": "existing",
    },
]


def build_figure_inventory() -> pd.DataFrame:
    return pd.DataFrame(FIGURE_INVENTORY)


def build_table_inventory() -> pd.DataFrame:
    return pd.DataFrame(TABLE_INVENTORY)


def write_paper_package_report(path: Path | str, *, figures: pd.DataFrame, tables: pd.DataFrame) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n_exist_f = int((figures["status"] == "existing").sum())
    n_comp_f = int((figures["status"] == "needs_composition").sum())
    n_exist_t = int((tables["status"] == "existing").sum())

    lines = [
        "# Paper Package Scaffold Report (Phase 5F-A)",
        "",
        f"> {PACKAGE_DISCLAIMER}",
        "",
        "## Package version",
        "",
        f"`{PACKAGE_VERSION}`",
        "",
        "## Manuscript",
        "",
        "- LaTeX skeleton: `paper/manuscript.tex`",
        "- Bibliography stub: `paper/references.bib`",
        "- Reproducibility: `paper/README.md`",
        "- Outline: `docs/paper_outline.md`",
        "",
        "## Figure inventory",
        "",
        f"- Total figures registered: **{len(figures)}**",
        f"- Status existing (source artifacts in repo): **{n_exist_f}**",
        f"- Status needs_composition: **{n_comp_f}**",
        "",
        "| ID | Title | Status | Claim |",
        "| --- | --- | --- | --- |",
    ]
    for _, r in figures.iterrows():
        lines.append(
            f"| {r['figure_id']} | {r['title'][:50]}... | {r['status']} | {r['claim_supported'][:30]}... |"
        )

    lines.extend(
        [
            "",
            "## Table inventory",
            "",
            f"- Total tables registered: **{len(tables)}**",
            f"- Status existing: **{n_exist_t}**",
            "",
            "| ID | Title | Status |",
            "| --- | --- | --- |",
        ]
    )
    for _, r in tables.iterrows():
        lines.append(f"| {r['table_id']} | {r['title'][:55]}... | {r['status']} |")

    lines.extend(
        [
            "",
            "## Claim boundaries (manuscript)",
            "",
            "The manuscript must **not** claim: dark matter disproven; ΛCDM replaced; "
            "full-SPARC validation; lensing confirmation; universal τ-profile.",
            "",
            "## Outputs",
            "",
            "- `outputs/tables/paper_figure_inventory.csv`",
            "- `outputs/tables/paper_table_inventory.csv`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_paper_package_scaffold(
    *,
    figure_inventory_out: Path | str = "outputs/tables/paper_figure_inventory.csv",
    table_inventory_out: Path | str = "outputs/tables/paper_table_inventory.csv",
    report_out: Path | str = "outputs/reports/paper_package_scaffold_report.md",
    paper_dir: Path | str = "paper",
) -> dict[str, pd.DataFrame]:
    figures = build_figure_inventory()
    tables = build_table_inventory()
    figures.to_csv(figure_inventory_out, index=False)
    tables.to_csv(table_inventory_out, index=False)
    write_paper_package_report(report_out, figures=figures, tables=tables)

    paper = Path(paper_dir)
    (paper / "figures").mkdir(parents=True, exist_ok=True)
    (paper / "tables").mkdir(parents=True, exist_ok=True)

    return {"figures": figures, "tables": tables}
