from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PHASE_DISCLAIMER = (
    "Phase 5F-E performs descriptive statistical summaries and referee-readiness "
    "documentation only. No model fitting and no modification of benchmark CSV files."
)

CLASSIFICATION_COL = "failure_mode_classification"
HOLDOUT_SPLIT = "even_odd_index"


def _bootstrap_proportion_ci(
    indicators: np.ndarray,
    *,
    n_resamples: int = 5000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Descriptive percentile CI for a binary proportion; not a hypothesis test."""
    indicators = np.asarray(indicators, dtype=float)
    n = len(indicators)
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = float(indicators.mean())
    rng = np.random.default_rng(seed)
    boots = np.empty(n_resamples)
    for i in range(n_resamples):
        sample = rng.choice(indicators, size=n, replace=True)
        boots[i] = sample.mean()
    return p, float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def build_statistical_summary(
    failure_summary: pd.DataFrame,
    *,
    cohort_label: str = "expansion_20",
) -> pd.DataFrame:
    """Descriptive cohort statistics from frozen failure-mode summary (no new fits)."""
    df = failure_summary.copy()
    n = len(df)
    if n == 0:
        raise ValueError("empty failure summary")

    class_counts = df[CLASSIFICATION_COL].value_counts()
    robust = (df[CLASSIFICATION_COL] == "robust_tdf_success").to_numpy()
    sens = (df[CLASSIFICATION_COL] == "sensitivity_recovery").to_numpy()
    fail = (df[CLASSIFICATION_COL] == "tdf_failure_mode").to_numpy()
    mixed = (df[CLASSIFICATION_COL] == "mixed_result").to_numpy()
    beats_nfw = df["tdf_3knot_beats_nfw_holdout"].astype(bool).to_numpy()
    beats_mond = df["tdf_3knot_beats_mond_holdout"].astype(bool).to_numpy()

    delta_nfw = df["tdf_3knot_holdout_rmse_kms"] - df["nfw_refit_holdout_rmse_kms"]
    delta_mond = df["tdf_3knot_holdout_rmse_kms"] - df["mond_fit_a0_holdout_rmse_kms"]

    rows: list[dict[str, object]] = []

    def add_fraction_metric(
        metric_id: str,
        description: str,
        indicator: np.ndarray,
    ) -> None:
        p, lo, hi = _bootstrap_proportion_ci(indicator)
        rows.append(
            {
                "cohort": cohort_label,
                "metric_id": metric_id,
                "description": description,
                "value": p,
                "n_galaxies": n,
                "count": int(indicator.sum()),
                "ci_lower_95_descriptive": lo,
                "ci_upper_95_descriptive": hi,
                "units": "fraction",
                "notes": "Bootstrap percentile interval (descriptive; not a significance test)",
            }
        )

    add_fraction_metric("robust_success_fraction", "robust_tdf_success fraction", robust)
    add_fraction_metric("sensitivity_recovery_fraction", "sensitivity_recovery fraction", sens)
    add_fraction_metric("failure_fraction", "tdf_failure_mode fraction", fail)
    add_fraction_metric("mixed_fraction", "mixed_result fraction", mixed)
    add_fraction_metric("tdf_3knot_beats_nfw_fraction", "tdf_3knot beats NFW (holdout)", beats_nfw)
    add_fraction_metric("tdf_3knot_beats_mond_fraction", "tdf_3knot beats MOND (holdout)", beats_mond)

    for metric_id, desc, series in (
        ("median_delta_rmse_tdf3_minus_nfw", "Median RMSE(tdf_3knot) - RMSE(NFW)", delta_nfw),
        ("median_delta_rmse_tdf3_minus_mond", "Median RMSE(tdf_3knot) - RMSE(MOND)", delta_mond),
    ):
        rows.append(
            {
                "cohort": cohort_label,
                "metric_id": metric_id,
                "description": desc,
                "value": float(series.median()),
                "n_galaxies": n,
                "count": np.nan,
                "ci_lower_95_descriptive": float(series.quantile(0.025)),
                "ci_upper_95_descriptive": float(series.quantile(0.975)),
                "units": "km/s",
                "notes": "Negative values favor tdf_3knot (lower holdout RMSE)",
            }
        )

    rows.append(
        {
            "cohort": cohort_label,
            "metric_id": "classification_counts",
            "description": "Per-class counts",
            "value": np.nan,
            "n_galaxies": n,
            "count": np.nan,
            "ci_lower_95_descriptive": np.nan,
            "ci_upper_95_descriptive": np.nan,
            "units": "count",
            "notes": str(class_counts.to_dict()),
        }
    )
    return pd.DataFrame(rows)


def format_statistical_prose(summary: pd.DataFrame) -> str:
    """LaTeX-ready descriptive summary for Results section."""

    def row(metric_id: str) -> pd.Series:
        r = summary[summary["metric_id"] == metric_id].iloc[0]
        return r

    def frac_line(metric_id: str, label: str) -> str:
        r = row(metric_id)
        p = 100 * float(r["value"])
        lo = 100 * float(r["ci_lower_95_descriptive"])
        hi = 100 * float(r["ci_upper_95_descriptive"])
        return (
            f"{label}: {int(r['count'])}/{int(r['n_galaxies'])} "
            f"({p:.0f}\\%; descriptive 95\\% bootstrap interval "
            f"$[{lo:.0f}\\%,\\,{hi:.0f}\\%]$)"
        )

    r_nfw = row("median_delta_rmse_tdf3_minus_nfw")
    r_mond = row("median_delta_rmse_tdf3_minus_mond")
    return (
        r"Descriptive summary (expansion\_20, even/odd holdout; not hypothesis testing): "
        + frac_line("robust_success_fraction", "robust primary success")
        + "; "
        + frac_line("sensitivity_recovery_fraction", "sensitivity-recovery")
        + "; "
        + frac_line("failure_fraction", "TDF failure")
        + "; "
        + frac_line("mixed_fraction", "mixed")
        + ". "
        + frac_line("tdf_3knot_beats_nfw_fraction", "Primary beats NFW")
        + "; "
        + frac_line("tdf_3knot_beats_mond_fraction", "primary beats MOND")
        + ". "
        + f"Median $\\Delta$RMSE $\\equiv$ RMSE$_{{\\mathrm{{3k}}}}$ $-$ RMSE$_{{\\mathrm{{baseline}}}}$: "
        + f"${float(r_nfw['value']):.2f}$\\,km/s vs NFW "
        + f"(galaxy-level 2.5--97.5\\% range "
        + f"$[{float(r_nfw['ci_lower_95_descriptive']):.2f},\\,"
        + f"{float(r_nfw['ci_upper_95_descriptive']):.2f}]$\\,km/s) and "
        + f"${float(r_mond['value']):.2f}$\\,km/s vs MOND "
        + f"($[{float(r_mond['ci_lower_95_descriptive']):.2f},\\,"
        + f"{float(r_mond['ci_upper_95_descriptive']):.2f}]$\\,km/s). "
        + r"Negative $\Delta$RMSE indicates lower primary TDF holdout error."
    )


def write_referee_readiness_report(
    path: Path | str,
    *,
    summary: pd.DataFrame,
    objection_matrix_path: Path | str,
    manuscript_path: Path | str,
    pdf_path: Path | str | None,
) -> None:
    path = Path(path)
    objections = Path(objection_matrix_path)
    n_obj = 0
    if objections.is_file():
        import re

        n_obj = sum(
            1
            for line in objections.read_text(encoding="utf-8").splitlines()
            if re.match(r"^\| R\d+", line)
        )

    lines = [
        "# Paper Referee Readiness Report (Phase 5F-E)",
        "",
        f"> {PHASE_DISCLAIMER}",
        "",
        "## Statistical summary",
        "",
        f"- Output: `outputs/tables/paper_statistical_summary.csv` ({len(summary)} metrics)",
        "",
        "## Reviewer objection matrix",
        "",
        f"- Document: `{objection_matrix_path}`",
        f"- Objections catalogued: **{n_obj}** (target $\\geq 20$)",
        "",
        "## Manuscript updates",
        "",
        "- Benchmark equations formalized in TDF framework section",
        "- Introduction: predictive holdout vs in-sample emphasis",
        "- Results: descriptive statistics (no significance claims)",
        "- Burkert baseline scope paragraph",
        "- Expanded bibliography",
        "",
        "## PDF",
        "",
    ]
    if pdf_path and Path(pdf_path).is_file():
        lines.append(f"- Compiled: `{pdf_path}`")
    else:
        lines.append("- PDF not rebuilt or LaTeX unavailable")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_referee_readiness_build(
    *,
    root: Path | str = ".",
    failure_summary_csv: Path | str = "outputs/tables/expansion20_failure_mode_summary.csv",
    stats_out: Path | str = "outputs/tables/paper_statistical_summary.csv",
    report_out: Path | str = "outputs/reports/paper_referee_readiness_report.md",
    objection_matrix: Path | str = "docs/reviewer_objection_matrix.md",
) -> dict[str, object]:
    root = Path(root).resolve()
    failure_path = root / failure_summary_csv
    summary = build_statistical_summary(pd.read_csv(failure_path))
    stats_path = root / stats_out
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(stats_path, index=False)

    from tdf_galaxy_tau.analysis.manuscript_text import build_manuscript_tex

    manuscript_path = root / "paper" / "manuscript.tex"
    manuscript_path.write_text(build_manuscript_tex(root=root), encoding="utf-8")

    from tdf_galaxy_tau.analysis.paper_compile import compile_paper_pdf

    compile_result = compile_paper_pdf(root=root)
    pdf_path = compile_result.get("pdf_path")

    write_referee_readiness_report(
        root / report_out,
        summary=summary,
        objection_matrix_path=root / objection_matrix,
        manuscript_path=manuscript_path,
        pdf_path=pdf_path,
    )
    return {
        "summary": summary,
        "stats_path": stats_path,
        "stat_prose": format_statistical_prose(summary),
        "pdf_path": pdf_path,
    }
