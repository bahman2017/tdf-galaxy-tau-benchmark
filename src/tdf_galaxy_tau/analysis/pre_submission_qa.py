from __future__ import annotations

import re
from pathlib import Path

from tdf_galaxy_tau.analysis.manuscript_text import (
    PROHIBITED_PHRASES,
    REQUIRED_CAVEAT_PHRASES,
    build_manuscript_tex,
)
from tdf_galaxy_tau.analysis.paper_tables import TABLE_FILES

PHASE_DISCLAIMER = (
    "Phase 5F-F performs final manuscript polish and pre-submission QA only. "
    "No model fitting and no modification of benchmark CSV files."
)

FIGURE_FILES = (
    "fig1_benchmark_workflow.png",
    "fig2_expansion12_vs_20_summary.png",
    "fig3_representative_successes.png",
    "fig4_ngc7814_failure.png",
    "fig5_sensitivity_recovery_cases.png",
    "fig6_holdout_rmse_comparison.png",
    "fig7_claim_boundary_map.png",
)

STALE_MANUSCRIPT_PHRASES = (
    "selected six-galaxy subset",
    "selected six-galaxy",
    "Phase 1B",
    "Phase 3A does not",
    "Phase 3B TDF",
    "Carry both legacy",
)

STALE_TABLE6_PHRASES = (
    "Phase 1B",
    "Phase 3A",
    "Phase 3B",
    "selected six-galaxy",
)

ABSTRACT_GRAMMAR_BUGS = (
    ", In the pre-registered",
    "$K_\\tau$, In the",
    "$K_\\tau$, In ",
)


def run_pre_submission_qa(
    *,
    root: Path | str = ".",
    checklist_out: Path | str = "docs/pre_submission_checklist.md",
    report_out: Path | str = "outputs/reports/paper_pre_submission_qa_report.md",
    compile_pdf: bool = True,
) -> dict[str, object]:
    root = Path(root).resolve()
    tex = build_manuscript_tex(root=root)
    manuscript_path = root / "paper" / "manuscript.tex"
    manuscript_path.write_text(tex, encoding="utf-8")

    pdf_path = root / "paper" / "manuscript.pdf"
    compile_result: dict[str, object] = {"latex_available": False, "pdf_path": None}
    if compile_pdf:
        from tdf_galaxy_tau.analysis.paper_compile import compile_paper_pdf

        from tdf_galaxy_tau.analysis.paper_tables import run_paper_tables_export

        run_paper_tables_export(root=root)
        compile_result = compile_paper_pdf(root=root)
        if compile_result.get("pdf_path"):
            pdf_path = Path(compile_result["pdf_path"])

    checks = perform_qa_checks(root=root, tex=tex, pdf_path=pdf_path)
    write_checklist(root / checklist_out, checks=checks, pdf_path=pdf_path)
    write_qa_report(root / report_out, checks=checks, pdf_path=pdf_path)
    return {"checks": checks, "pdf_path": pdf_path if pdf_path.is_file() else None}


def perform_qa_checks(
    *,
    root: Path,
    tex: str,
    pdf_path: Path,
) -> dict[str, object]:
    lower = tex.lower().replace(r"\_", "_")
    fig_refs = re.findall(r"figures/(fig\d+_[^}]+\.png)", tex)
    table_inputs = [t for t in TABLE_FILES if t in tex]

    stale_ms = [p for p in STALE_MANUSCRIPT_PHRASES if p.lower() in lower]
    table6_path = root / "paper/tables/table6_assumptions_limitations.tex"
    table6_text = table6_path.read_text(encoding="utf-8") if table6_path.is_file() else ""
    stale_t6 = [p for p in STALE_TABLE6_PHRASES if p in table6_text]

    abstract_bugs = [b for b in ABSTRACT_GRAMMAR_BUGS if b.replace("\\", "") in tex or b in tex]
    prohibited = [p for p in PROHIBITED_PHRASES if p.lower() in lower]
    missing_caveats = [
        p for p in REQUIRED_CAVEAT_PHRASES if p.lower() not in lower.replace("$", "")
    ]

    bib_path = root / "paper/references.bib"
    bib_keys = []
    if bib_path.is_file():
        bib_keys = re.findall(r"@\w+\{([^,]+),", bib_path.read_text(encoding="utf-8"))

    return {
        "pdf_exists": pdf_path.is_file(),
        "figure_count_files": sum(
            1 for f in FIGURE_FILES if (root / "paper/figures" / f).is_file()
        ),
        "figure_refs_order": fig_refs,
        "table_count_included": len(table_inputs),
        "stale_manuscript": stale_ms,
        "stale_table6": stale_t6,
        "abstract_bugs": abstract_bugs,
        "prohibited_hits": prohibited,
        "missing_caveats": missing_caveats,
        "bib_entry_count": len(bib_keys),
        "equations_present": all(
            lbl in tex for lbl in ("eq:vobs", "eq:vtau", "eq:dtaudr")
        ),
        "author_present": "Bahman Masarrat" in tex,
    }


def write_checklist(path: Path, *, checks: dict[str, object], pdf_path: Path) -> None:
    ok = lambda cond: "PASS" if cond else "FAIL"
    lines = [
        "# Pre-Submission Checklist (Phase 5F-F)",
        "",
        f"> {PHASE_DISCLAIMER}",
        "",
        "## Build",
        "",
        f"- [ ] PDF compiled: **{ok(checks['pdf_exists'])}** (`{pdf_path}`)",
        f"- [ ] Figures on disk: **{checks['figure_count_files']}/7**",
        f"- [ ] Tables referenced in manuscript: **{checks['table_count_included']}/6**",
        f"- [ ] Equations present: **{ok(checks['equations_present'])}**",
        f"- [ ] Author block: **{ok(checks['author_present'])}**",
        "",
        "## Claim boundaries",
        "",
        f"- [ ] Prohibited phrases absent: **{ok(not checks['prohibited_hits'])}**",
        f"- [ ] Required caveats present: **{ok(not checks['missing_caveats'])}**",
        "",
        "## Stale content",
        "",
        f"- [ ] Manuscript stale phrases: **{ok(not checks['stale_manuscript'])}**",
        f"- [ ] Table 6 (assumptions) updated: **{ok(not checks['stale_table6'])}**",
        f"- [ ] Abstract grammar: **{ok(not checks['abstract_bugs'])}**",
        "",
        "## Bibliography",
        "",
        f"- [ ] Bib entries: **{checks['bib_entry_count']}** (expect $\\geq 10$)",
        "",
        "## Reproducibility commands",
        "",
        "```bash",
        "python3 scripts/run_expansion20_pipeline.py",
        "python3 scripts/build_controlled_expansion_final_audit.py",
        "python3 scripts/build_paper_figures.py",
        "python3 scripts/export_paper_tables.py",
        "python3 scripts/build_referee_readiness_report.py",
        "python3 scripts/compile_paper_pdf.py",
        "```",
        "",
        "## Known remaining limitations",
        "",
        "- Controlled expansion-20 cohort only (not full SPARC)",
        "- Fixed baryons; no final M/L calibration",
        "- K_tau fixed, not measured",
        "- Lensing not tested",
        "- NGC7814 canonical failure retained",
        "- tdf_5knot sensitivity-only",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_qa_report(path: Path, *, checks: dict[str, object], pdf_path: Path) -> None:
    lines = [
        "# Paper Pre-Submission QA Report (Phase 5F-F)",
        "",
        f"> {PHASE_DISCLAIMER}",
        "",
        "## Summary",
        "",
        f"- PDF: `{pdf_path}` ({'exists' if checks['pdf_exists'] else 'missing'})",
        f"- Figures: {checks['figure_count_files']}/7 files; document order: {checks['figure_refs_order']}",
        f"- Tables in manuscript: {checks['table_count_included']}/6",
        "",
        "## Checks",
        "",
    ]
    for key, val in checks.items():
        lines.append(f"- **{key}:** {val}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
