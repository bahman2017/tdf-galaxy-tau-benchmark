#!/usr/bin/env python3
"""Run repository cleanup audit (Step 1) and optional safe cleanup (Step 3)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tdf_galaxy_tau.analysis.repository_cleanup import (  # noqa: E402
    apply_safe_cleanup,
    finalize_after_cleanup,
    run_audit,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Repository cleanup audit and safe hygiene.")
    parser.add_argument(
        "--apply-cleanup",
        action="store_true",
        help="After audit, remove caches, .DS_Store, and LaTeX build artifacts only.",
    )
    args = parser.parse_args()
    root = ROOT

    summary = run_audit(root)
    print(f"Audited {summary['n_files']} files.")
    for cat, n in sorted(summary["counts"].items()):
        print(f"  {cat}: {n}")

    if args.apply_cleanup:
        mtimes_before = summary["mtimes_before"]
        actions = apply_safe_cleanup(root)
        finalize_after_cleanup(actions, root, mtimes_before=mtimes_before)
        print(f"Safe cleanup: {len(actions)} actions.")
        for line in actions[:20]:
            print(f"  - {line}")
        if len(actions) > 20:
            print(f"  ... and {len(actions) - 20} more")
    else:
        print("Audit only (no deletions). Re-run with --apply-cleanup for Step 3.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
