from __future__ import annotations

from pathlib import Path


def write_plot_warning_report(path: str | Path, message: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(message + "\n", encoding="utf-8")
