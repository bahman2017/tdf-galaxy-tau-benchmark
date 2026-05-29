from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from tdf_galaxy_tau.data.subset_selection import SubsetSelectionConfig, select_sparc_subset


def _load_config(path: Path) -> SubsetSelectionConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    criteria = raw.get("selection_criteria", {})
    return SubsetSelectionConfig(
        input_csv=raw["input_standardized_csv"],
        output_subset_csv=raw["output_subset_selection_csv"],
        output_report_md=raw["output_subset_selection_report"],
        candidate_galaxies=list(raw.get("candidate_galaxies", [])),
        min_radial_points=int(criteria.get("min_radial_points", 12)),
        min_radial_coverage_kpc=float(criteria.get("min_radial_coverage_kpc", 5.0)),
        max_selected_galaxies=int(raw.get("max_selected_galaxies", 6)),
        allow_mock_data=bool(raw.get("allow_mock_data", False)),
    )


def _write_report(path: Path, ctx: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SPARC Subset Selection Report (Phase 1B)",
        "",
        "## Summary",
        "",
        f"- Total galaxies evaluated: {ctx['total_evaluated']}",
        f"- Total selected: {ctx['total_selected']}",
        f"- Selected galaxies: {', '.join(ctx['selected_galaxies']) if ctx['selected_galaxies'] else 'None'}",
        "",
        "## Criteria used",
        "",
        f"- Minimum radial points: {ctx['criteria']['min_radial_points']}",
        f"- Minimum radial coverage [kpc]: {ctx['criteria']['min_radial_coverage_kpc']}",
        f"- Finite required columns: {', '.join(ctx['criteria']['required_finite_columns'])}",
        f"- Positive required columns: {', '.join(ctx['criteria']['require_positive'])}",
        f"- Negative residual handling: allow and report",
        f"- Maximum selected galaxies: {ctx['criteria']['max_selected_galaxies']}",
        "",
        "## Candidate outcomes",
        "",
    ]

    if ctx["rejected_candidates"]:
        lines.append("### Rejected candidate galaxies")
        lines.append("")
        for row in ctx["rejected_candidates"]:
            reason = row["rejection_reason"] or row["quality_flag"]
            lines.append(f"- {row['galaxy_id']}: {reason}")
        lines.append("")
    else:
        lines.append("### Rejected candidate galaxies")
        lines.append("")
        lines.append("- None")
        lines.append("")

    if ctx["missing_candidates"]:
        lines.append("### Missing candidate galaxies")
        lines.append("")
        for gid in ctx["missing_candidates"]:
            lines.append(f"- {gid}: not present in standardized CSV")
        lines.append("")
    else:
        lines.append("### Missing candidate galaxies")
        lines.append("")
        lines.append("- None")
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            f"- {ctx['negative_residual_note']}",
            f"- {ctx['bulge_diversity_note']}",
            "",
            "## Claim boundary",
            "",
            "This is subset selection only. No TDF, NFW, Burkert, or dark-matter inference is made in this phase.",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Select deterministic controlled SPARC subset")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = _load_config(Path(args.config))
    rows, ctx = select_sparc_subset(cfg)

    out_csv = Path(cfg.output_subset_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    rows.to_csv(out_csv, index=False)

    _write_report(Path(cfg.output_report_md), ctx)

    print(f"Total galaxies evaluated: {ctx['total_evaluated']}")
    print(f"Total selected: {ctx['total_selected']}")
    print(f"Selected galaxies: {', '.join(ctx['selected_galaxies']) if ctx['selected_galaxies'] else 'None'}")
    print(f"Wrote subset-selection CSV: {out_csv}")
    print(f"Wrote subset-selection report: {cfg.output_report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
