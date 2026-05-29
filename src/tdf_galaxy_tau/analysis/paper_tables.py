from __future__ import annotations

from pathlib import Path

import pandas as pd

PHASE_DISCLAIMER = (
    "Phase 5F-C/5F-D export LaTeX tables from frozen benchmark outputs only. "
    "No model fitting and no modification of benchmark CSV files."
)

TABLE_FILES = (
    "table1_cohort_summary.tex",
    "table2_holdout_rmse.tex",
    "table3_classification_summary.tex",
    "table4_nonrobust_diagnostics.tex",
    "table5_claim_traceability.tex",
    "table6_assumptions_limitations.tex",
)

FAILURE_CLASS_LABELS = {
    "robust_tdf_success": "Robust TDF success",
    "sensitivity_recovery": "Sensitivity recovery",
    "tdf_failure_mode": "TDF failure mode",
    "mixed_result": "Mixed result",
}

CLAIM_STATUS_LABELS = {
    "supported": "Supported",
    "supported_with_caveat": "Supported (caveat)",
    "supported_sensitivity_only": "Sensitivity only",
    "supported_with_caveats": "Supported (caveats)",
    "not_supported": "Not supported",
    "not_tested": "Not tested",
    "prohibited": "Prohibited",
}

METRIC_LABELS = {
    "cohort_size": "Cohort size",
    "robust_tdf_success": "Robust TDF success (primary)",
    "sensitivity_recovery": "Sensitivity recovery",
    "tdf_failure_mode": "TDF failure mode",
    "mixed_result": "Mixed result",
    "tdf_3knot_beats_nfw_holdout": "Primary beats NFW (holdout)",
    "tdf_3knot_beats_mond_holdout": "Primary beats MOND (holdout)",
}


def latex_escape(text: object) -> str:
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    s = str(text)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s


def readable_failure_class(code: str) -> str:
    return FAILURE_CLASS_LABELS.get(str(code), str(code).replace("_", " "))


def readable_claim_status(status: str) -> str:
    return CLAIM_STATUS_LABELS.get(str(status), str(status).replace("_", " "))


def _fmt_num(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return "---"
    return f"{float(x):.{digits}f}"


def _table_wrapper(
    *,
    caption: str,
    label: str,
    tabular_body: str,
    source_note: str,
    caveat_note: str | None = None,
) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        tabular_body,
        r"\vspace{0.4em}",
        r"{\footnotesize",
        rf"\par\noindent\textbf{{Source:}} {source_note}",
    ]
    if caveat_note:
        lines.append(rf"\par\noindent\textbf{{Caveat:}} {caveat_note}")
    lines.extend([r"\par", r"}", r"\end{table}", ""])
    return "\n".join(lines)


def export_table1_cohort_summary(plan_csv: Path | str) -> str:
    plan = pd.read_csv(plan_csv)
    e12 = set(plan.loc[plan["cohort_name"] == "expansion_12", "galaxy_id"])
    e20 = plan.loc[plan["cohort_name"] == "expansion_20"].sort_values("selection_order")

    rows = []
    for _, r in e20.iterrows():
        gid = r["galaxy_id"]
        role = str(r["cohort_role"]).replace("_", " ")
        rows.append(
            " & ".join(
                [
                    latex_escape(gid),
                    latex_escape(role),
                    "Y" if gid in e12 else "---",
                    str(int(r["selection_order"])),
                ]
            )
            + r" \\"
        )

    tabular = "\n".join(
        [
            r"\footnotesize",
            r"\begin{tabular}{llcc}",
            r"\toprule",
            r"Galaxy & Role & In expansion\_12 & Order \\",
            r"\midrule",
            *rows,
            r"\bottomrule",
            r"\end{tabular}",
        ]
    )
    return _table_wrapper(
        caption="Pre-registered expansion\\_20 cohort membership (Phase 5A plan).",
        label="tab:cohort",
        tabular_body=tabular,
        source_note=r"\texttt{outputs/tables/sparc\_subset\_expansion\_plan.csv}.",
        caveat_note="Controlled subset only; not full-SPARC validation.",
    )


def export_table2_holdout_rmse(failure_summary_csv: Path | str) -> str:
    df = pd.read_csv(failure_summary_csv).sort_values("galaxy_id")
    rows = []
    for _, r in df.iterrows():
        rows.append(
            " & ".join(
                [
                    latex_escape(r["galaxy_id"]),
                    latex_escape(readable_failure_class(r["failure_mode_classification"])),
                    _fmt_num(r["tdf_3knot_holdout_rmse_kms"]),
                    _fmt_num(r["nfw_refit_holdout_rmse_kms"]),
                    _fmt_num(r["mond_fit_a0_holdout_rmse_kms"]),
                    _fmt_num(r["tdf_5knot_holdout_rmse_kms"]),
                ]
            )
            + r" \\"
        )

    tabular = "\n".join(
        [
            r"\scriptsize",
            r"\begin{tabular}{@{}l l r r r r@{}}",
            r"\toprule",
            r"Galaxy & Classification & \texttt{tdf\_3knot} & NFW & MOND & \texttt{tdf\_5knot} \\",
            r"\midrule",
            *rows,
            r"\bottomrule",
            r"\end{tabular}",
        ]
    )
    return _table_wrapper(
        caption="Even/odd holdout test RMSE [km/s] for expansion\\_20 (train-only refit).",
        label="tab:holdout-rmse",
        tabular_body=tabular,
        source_note=r"\texttt{expansion20\_failure\_mode\_summary.csv}.",
        caveat_note=r"Primary gate uses \texttt{tdf\_3knot}; \texttt{tdf\_5knot} is sensitivity only.",
    )


def export_table3_classification(comparison_csv: Path | str) -> str:
    comp = pd.read_csv(comparison_csv)
    rows = []
    for metric, label in METRIC_LABELS.items():
        row = comp[comp["metric"] == metric]
        if row.empty:
            continue
        r = row.iloc[0]
        note = r.get("notes", "")
        note = "" if pd.isna(note) else str(note)
        rows.append(
            f"{latex_escape(label)} & {int(r['expansion_12'])} & {int(r['expansion_20'])} & "
            f"{latex_escape(note[:100])} \\\\"
        )

    tabular = "\n".join(
        [
            r"\footnotesize",
            r"\begin{tabular}{@{}l r r p{4.5cm}@{}}",
            r"\toprule",
            r"Metric & expansion\_12 & expansion\_20 & Notes \\",
            r"\midrule",
            *rows,
            r"\bottomrule",
            r"\end{tabular}",
        ]
    )
    return _table_wrapper(
        caption="Classification and holdout comparison: expansion\\_12 vs expansion\\_20.",
        label="tab:classification",
        tabular_body=tabular,
        source_note=r"\texttt{controlled\_expansion\_comparison\_summary.csv}.",
        caveat_note=(
            r"Robust TDF success requires primary \texttt{tdf\_3knot} to beat both NFW and MOND on holdout."
        ),
    )


def export_table4_nonrobust(
    diagnostics_csv: Path | str,
    case_review_csv: Path | str,
) -> str:
    _ = case_review_csv
    df = pd.read_csv(diagnostics_csv)

    rows = []
    for _, r in df.iterrows():
        rows.append(
            " & ".join(
                [
                    latex_escape(r["galaxy_id"]),
                    latex_escape(readable_failure_class(r["failure_mode_classification"])),
                    _fmt_num(r["tdf_3knot_holdout_rmse_kms"]),
                    _fmt_num(r["tdf_5knot_holdout_rmse_kms"]),
                    _fmt_num(r["tdf_5knot_minus_tdf_3knot_holdout_improvement_kms"]),
                ]
            )
            + r" \\"
        )

    tabular = "\n".join(
        [
            r"\footnotesize",
            r"\begin{tabular}{@{}l l r r r@{}}",
            r"\toprule",
            r"Galaxy & Classification & RMSE$_{\mathrm{3k}}$ & RMSE$_{\mathrm{5k}}$ & "
            r"$\Delta$RMSE [km/s] \\",
            r"\midrule",
            *rows,
            r"\bottomrule",
            r"\end{tabular}",
        ]
    )
    return _table_wrapper(
        caption="Non-robust expansion\\_20 cases: holdout diagnostics (five galaxies).",
        label="tab:nonrobust",
        tabular_body=tabular,
        source_note=r"\texttt{expansion20\_failure\_diagnostics.csv}.",
        caveat_note="Descriptive labels only; not causal claims about baryons or dark matter.",
    )


def export_table5_claim_traceability(claims_csv: Path | str) -> str:
    claims = pd.read_csv(claims_csv)
    c20 = claims[claims["claim_id"].astype(str).str.match(r"^C20-[A-H]$")].sort_values("claim_id")
    rows = []
    for _, r in c20.iterrows():
        rows.append(
            " & ".join(
                [
                    latex_escape(r["claim_id"]),
                    latex_escape(str(r["claim_text"])),
                    latex_escape(readable_claim_status(r["status"])),
                ]
            )
            + r" \\"
        )

    tabular = "\n".join(
        [
            r"\scriptsize",
            r"\begin{tabular}{@{}p{1.1cm} p{10.2cm} p{2.8cm}@{}}",
            r"\toprule",
            r"ID & Claim & Status \\",
            r"\midrule",
            *rows,
            r"\bottomrule",
            r"\end{tabular}",
        ]
    )
    return _table_wrapper(
        caption="Claim traceability matrix for controlled expansion\\_20 (C20-A--C20-H).",
        label="tab:claims-matrix",
        tabular_body=tabular,
        source_note=r"\texttt{controlled\_expansion\_final\_claims.csv}.",
        caveat_note="Authoritative language boundary for external reporting.",
    )


def export_table6_assumptions_limitations(
    assumptions_md: Path | str,
    limitations_md: Path | str,
) -> str:
    _ = (assumptions_md, limitations_md)  # inventory traceability; content frozen for expansion-20
    pairs = [
        (
            "Benchmark scope is the pre-registered controlled expansion-20 cohort ($n{=}20$) only.",
            "Not full-SPARC validation; cohort fractions must not be extrapolated.",
        ),
        (
            "Fixed canonical SPARC baryonic decomposition; no final $M/L$ calibration in this manuscript.",
            "Halo and MOND baselines remain degenerate with baryonic assumptions.",
        ),
        (
            "$K_\\tau$ is fixed across the cohort and is not measured or inferred here.",
            "Higher knot count (\\texttt{tdf\\_5knot}) increases flexibility and overfitting risk.",
        ),
        (
            "NFW and MOND are rotation-curve empirical baselines, not cosmology or lensing tests.",
            "Does not disprove dark matter and does not replace $\\Lambda$CDM.",
        ),
        (
            "Burkert halos are fitted for completeness but are not part of the primary holdout gate.",
            "Lensing is not tested in this benchmark phase.",
        ),
        (
            "Primary model: \\texttt{tdf\\_3knot}; sensitivity model: \\texttt{tdf\\_5knot} (not primary success).",
            "No universal $\\tau$-profile claim; per-galaxy $\\tau$ diagnostics only.",
        ),
        (
            "Even/odd train-only holdout is the primary predictive gate.",
            "Bootstrap intervals in the manuscript are descriptive, not significance tests.",
        ),
    ]
    body = [
        r"\footnotesize",
        r"\begin{tabular}{@{}p{0.48\linewidth}p{0.48\linewidth}@{}}",
        r"\toprule",
        r"\textbf{Assumptions (expansion-20)} & \textbf{Limitations (expansion-20)} \\",
        r"\midrule",
    ]
    for a, ell in pairs:
        body.append(f"$\\bullet$ {a} & $\\bullet$ {ell} \\\\")
    body.extend([r"\bottomrule", r"\end{tabular}"])

    return _table_wrapper(
        caption="Assumptions and limitations for the controlled expansion-20 manuscript.",
        label="tab:assumptions",
        tabular_body="\n".join(body),
        source_note=r"Phase~5F-F expansion-20 checklist (replaces legacy six-galaxy assumption bullets).",
        caveat_note=(
            "Aligned with claims C20-A--C20-H; no change to frozen benchmark metrics."
        ),
    )


def run_paper_tables_export(
    *,
    root: Path | str = ".",
    tables_dir: Path | str = "paper/tables",
    plan_csv: Path | str = "outputs/tables/sparc_subset_expansion_plan.csv",
    comparison_csv: Path | str = "outputs/tables/controlled_expansion_comparison_summary.csv",
    failure_summary_csv: Path | str = "outputs/tables/expansion20_failure_mode_summary.csv",
    diagnostics_csv: Path | str = "outputs/tables/expansion20_failure_diagnostics.csv",
    case_review_csv: Path | str = "outputs/tables/expansion20_case_review_summary.csv",
    claims_csv: Path | str = "outputs/tables/controlled_expansion_final_claims.csv",
    assumptions_md: Path | str = "docs/assumptions.md",
    limitations_md: Path | str = "docs/limitations.md",
) -> dict[str, Path]:
    root = Path(root).resolve()
    out_dir = Path(tables_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    exporters = {
        "table1_cohort_summary.tex": lambda: export_table1_cohort_summary(root / plan_csv),
        "table2_holdout_rmse.tex": lambda: export_table2_holdout_rmse(root / failure_summary_csv),
        "table3_classification_summary.tex": lambda: export_table3_classification(root / comparison_csv),
        "table4_nonrobust_diagnostics.tex": lambda: export_table4_nonrobust(
            root / diagnostics_csv, root / case_review_csv
        ),
        "table5_claim_traceability.tex": lambda: export_table5_claim_traceability(root / claims_csv),
        "table6_assumptions_limitations.tex": lambda: export_table6_assumptions_limitations(
            root / assumptions_md, root / limitations_md
        ),
    }
    written: dict[str, Path] = {}
    for name, fn in exporters.items():
        path = out_dir / name
        path.write_text(fn(), encoding="utf-8")
        written[name] = path
    return written
