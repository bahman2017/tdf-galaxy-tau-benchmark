from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.analysis.manuscript_text import build_manuscript_tex
from tdf_galaxy_tau.analysis.paper_tables import PHASE_DISCLAIMER, run_paper_tables_export


def write_manuscript_draft_report(
    path: Path,
    *,
    tables: dict[str, Path],
    manuscript_path: Path,
    pdf_path: Path | None,
    latex_available: bool,
) -> None:
    lines = [
        "# Paper Manuscript Draft Report (Phase 5F-C)",
        "",
        f"> {PHASE_DISCLAIMER}",
        "",
        "## Tables exported",
        "",
    ]
    for name, p in sorted(tables.items()):
        lines.append(f"- `{p}`")
    lines.extend(
        [
            "",
            "## Manuscript",
            "",
            f"- Draft: `{manuscript_path}`",
            "",
            "## PDF compile",
            "",
        ]
    )
    if pdf_path and pdf_path.is_file():
        lines.append(f"- **Success:** `{pdf_path}`")
    elif latex_available:
        lines.append("- LaTeX was available but PDF was not produced; see compile log.")
    else:
        lines.append("- **LaTeX not installed** on this system; PDF skipped (tests do not fail).")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tables = run_paper_tables_export(root=root)
    manuscript_path = root / "paper" / "manuscript.tex"
    manuscript_path.write_text(build_manuscript_tex(root=root), encoding="utf-8")

    from tdf_galaxy_tau.analysis.paper_compile import compile_paper_pdf

    result = compile_paper_pdf(root=root)
    write_manuscript_draft_report(
        root / "outputs/reports/paper_manuscript_draft_report.md",
        tables=tables,
        manuscript_path=manuscript_path,
        pdf_path=result.get("pdf_path"),
        latex_available=result.get("latex_available", False),
    )
    edit_report = root / "outputs/reports/paper_scientific_edit_report.md"
    if edit_report.is_file():
        print(f"See also {edit_report}")
    print(PHASE_DISCLAIMER)
    print(f"Wrote {len(tables)} tables to paper/tables/")
    print(f"Wrote {manuscript_path}")
    if result.get("pdf_path"):
        print(f"Wrote {result['pdf_path']}")
    else:
        print(result.get("message", "PDF not built"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
