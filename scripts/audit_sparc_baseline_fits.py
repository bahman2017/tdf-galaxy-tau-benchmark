from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from tdf_galaxy_tau.models.fitting import (
    BaselineAuditConfig,
    audit_baseline_fits,
    summarize_baseline_audit,
)


AUDIT_CSV = Path("outputs/tables/sparc_baseline_fit_audit.csv")
REPORT_PATH = Path("outputs/reports/sparc_baseline_fit_audit_report.md")


def _load_audit_config(path: Path) -> BaselineAuditConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    audit = raw.get("audit", {})
    return BaselineAuditConfig(
        boundary_tolerance_fraction=float(audit.get("boundary_tolerance_fraction", 0.01)),
        high_reduced_chi_square_threshold=float(audit.get("high_reduced_chi_square_threshold", 5.0)),
        very_high_reduced_chi_square_threshold=float(audit.get("very_high_reduced_chi_square_threshold", 20.0)),
        poor_rmse_fraction_of_median_v_obs=float(audit.get("poor_rmse_fraction_of_median_v_obs", 0.20)),
    )


def _median_v_obs_by_galaxy(data_csv: Path | None, galaxy_ids: list[str]) -> dict[str, float]:
    if data_csv is None or not data_csv.is_file():
        return {}
    data = pd.read_csv(data_csv)
    data = data[data["galaxy_id"].isin(galaxy_ids)]
    return data.groupby("galaxy_id")["v_obs_kms"].median().astype(float).to_dict()


def _write_report(
    path: Path,
    audit_df: pd.DataFrame,
    summary: dict[str, object],
    cfg: BaselineAuditConfig,
    *,
    report_title: str,
    audit_csv_path: Path,
) -> None:
    lines = [
        f"# SPARC Baseline Fit Audit Report ({report_title})",
        "",
        "This audit reviews Phase 3A baseline fits only. It does not fit or validate TDF and does not disprove dark matter.",
        "",
        "## Executive summary",
        "",
    ]

    if summary["nfw_best_rmse_all_galaxies"]:
        lines.append("- **NFW has the lowest RMSE among baseline models for all six selected galaxies.**")
    else:
        lines.append("- NFW is **not** the lowest-RMSE baseline for every galaxy in this audit.")

    if summary["nfw_best_aic_all_galaxies"] and summary["nfw_best_bic_all_galaxies"]:
        lines.append("- **NFW also has the best AIC and BIC among baseline models for all six galaxies.**")
    else:
        lines.append("- NFW is not uniformly best by AIC/BIC across galaxies.")

    lines.extend(
        [
            f"- Burkert fits flagged as boundary-limited: **{summary['burkert_boundary_limited_rows']} / {summary['burkert_total_rows']}** rows.",
            f"- NFW fits flagged as boundary-limited: **{summary['nfw_boundary_limited_rows']}** rows.",
            f"- Rows with reduced chi-square > {cfg.high_reduced_chi_square_threshold}: **{summary['high_chi_rows']}**.",
            f"- Rows with reduced chi-square > {cfg.very_high_reduced_chi_square_threshold}: **{summary['very_high_chi_rows']}**.",
            "",
            "## Caveats before TDF comparison",
            "",
            "- Burkert is numerically fit-successful in Phase 3A but often boundary-limited (especially `rho_0` at the lower bound).",
            "- Several NFW solutions are near or at parameter bounds (`r_s` upper bound and/or `rho_s` lower bound).",
            "- Baryonic-only and some halo baselines show very high reduced chi-square; interpret metrics with caution.",
            "- These baseline caveats must be carried forward before any Phase 3B TDF knot comparison.",
            "",
            "## Audit configuration",
            "",
            f"- Boundary tolerance: {cfg.boundary_tolerance_fraction * 100:.1f}% of allowed parameter range",
            f"- High reduced chi-square threshold: {cfg.high_reduced_chi_square_threshold}",
            f"- Very high reduced chi-square threshold: {cfg.very_high_reduced_chi_square_threshold}",
            f"- Poor RMSE threshold: {cfg.poor_rmse_fraction_of_median_v_obs * 100:.0f}% of median v_obs",
            "",
            "## Model status counts",
            "",
        ]
    )
    for status, count in sorted(summary["status_counts"].items()):
        lines.append(f"- `{status}`: {count}")

    lines.extend(["", "## Per-galaxy audit table", ""])
    lines.append("| Galaxy | Model | RMSE | red. chi2 | model_status | boundary flags |")
    lines.append("| --- | --- | ---: | ---: | --- | --- |")
    for _, row in audit_df.sort_values(["galaxy_id", "model_name"]).iterrows():
        flags = []
        for col in [
            "rho_s_lower_bound",
            "rho_s_upper_bound",
            "r_s_lower_bound",
            "r_s_upper_bound",
            "rho_0_lower_bound",
            "rho_0_upper_bound",
            "r_0_lower_bound",
            "r_0_upper_bound",
        ]:
            if bool(row.get(col, False)):
                flags.append(col)
        flag_text = ", ".join(flags) if flags else "none"
        lines.append(
            f"| {row['galaxy_id']} | {row['model_name']} | {row['rmse_kms']:.2f} | "
            f"{row['reduced_chi_square']:.2f} | {row['model_status']} | {flag_text} |"
        )

    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{audit_csv_path}`",
            f"- `{path}`",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Phase 3A SPARC baseline fits")
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--parameters", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument(
        "--data",
        default="data/processed/sparc/sparc_rotmod_standardized.csv",
        help="Optional standardized data CSV for median v_obs per galaxy",
    )
    parser.add_argument(
        "--out",
        default=str(AUDIT_CSV),
        help="Output audit CSV path",
    )
    parser.add_argument(
        "--report",
        default=str(REPORT_PATH),
        help="Output audit markdown report path",
    )
    parser.add_argument(
        "--report-title",
        default="Phase 3A-Audit",
        help="Short phase label for report heading",
    )
    args = parser.parse_args()

    comparison = pd.read_csv(args.comparison)
    parameters = pd.read_csv(args.parameters)
    cfg = _load_audit_config(Path(args.config))

    galaxy_ids = comparison["galaxy_id"].astype(str).unique().tolist()
    medians = _median_v_obs_by_galaxy(Path(args.data), galaxy_ids)

    audit_df = audit_baseline_fits(
        comparison,
        parameters,
        median_v_obs_by_galaxy=medians,
        config=cfg,
    )
    summary = summarize_baseline_audit(audit_df)

    out_csv = Path(args.out)
    out_report = Path(args.report)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    audit_df.to_csv(out_csv, index=False)
    _write_report(
        out_report,
        audit_df,
        summary,
        cfg,
        report_title=args.report_title,
        audit_csv_path=out_csv,
    )

    print(f"Wrote audit table: {out_csv}")
    print(f"Wrote audit report: {out_report}")
    print(f"Boundary-limited rows: {summary['boundary_limited_rows']}")
    print(f"High reduced-chi-square rows: {summary['high_chi_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
