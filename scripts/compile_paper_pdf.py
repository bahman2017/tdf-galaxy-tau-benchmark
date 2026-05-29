from __future__ import annotations

from pathlib import Path

from tdf_galaxy_tau.analysis.paper_compile import compile_paper_pdf


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = compile_paper_pdf(root=root)
    print(result["message"])
    if result.get("pdf_path"):
        print(result["pdf_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
