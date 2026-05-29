from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _which(cmd: str) -> str | None:
    return shutil.which(cmd)


def compile_paper_pdf(
    *,
    root: Path | str = ".",
    paper_dir: Path | str = "paper",
    manuscript_name: str = "manuscript",
) -> dict[str, object]:
    root = Path(root).resolve()
    paper = root / paper_dir
    tex = paper / f"{manuscript_name}.tex"
    pdf = paper / f"{manuscript_name}.pdf"
    log_lines: list[str] = []

    if not tex.is_file():
        return {
            "latex_available": False,
            "pdf_path": None,
            "message": f"Missing {tex}",
            "log": "",
        }

    latexmk = _which("latexmk")
    pdflatex = _which("pdflatex")
    bibtex = _which("bibtex")

    if latexmk:
        cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", f"{manuscript_name}.tex"]
        proc = subprocess.run(cmd, cwd=paper, capture_output=True, text=True, timeout=180)
        log_lines.extend([proc.stdout, proc.stderr])
        if proc.returncode == 0 and pdf.is_file():
            return {
                "latex_available": True,
                "pdf_path": pdf,
                "message": "PDF built with latexmk",
                "log": "\n".join(log_lines)[-8000:],
            }

    if not pdflatex:
        return {
            "latex_available": False,
            "pdf_path": None,
            "message": "LaTeX unavailable (pdflatex not found); skipping PDF build",
            "log": "\n".join(log_lines),
        }

    for _ in range(2):
        proc = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", f"{manuscript_name}.tex"],
            cwd=paper,
            capture_output=True,
            text=True,
            timeout=120,
        )
        log_lines.extend([proc.stdout[-4000:], proc.stderr[-1000:]])

    if bibtex and (paper / f"{manuscript_name}.aux").is_file():
        subprocess.run(
            [bibtex, manuscript_name],
            cwd=paper,
            capture_output=True,
            text=True,
            timeout=60,
        )
        for _ in range(2):
            subprocess.run(
                [pdflatex, "-interaction=nonstopmode", f"{manuscript_name}.tex"],
                cwd=paper,
                capture_output=True,
                text=True,
                timeout=120,
            )

    if pdf.is_file():
        return {
            "latex_available": True,
            "pdf_path": pdf,
            "message": "PDF built with pdflatex",
            "log": "\n".join(log_lines)[-8000:],
        }

    return {
        "latex_available": True,
        "pdf_path": None,
        "message": "pdflatex ran but manuscript.pdf was not produced",
        "log": "\n".join(log_lines)[-8000:],
    }
