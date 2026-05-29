from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

AUDIT_VERSION = "phase_5e_controlled_expansion_final"

FINAL_EXPANSION_20_CLAIM = (
    "In the pre-registered controlled expansion_20 cohort, the primary conservative tdf_3knot "
    "model achieves robust holdout success in 15 of 20 galaxies. Three additional galaxies show "
    "sensitivity-recovery where tdf_5knot improves substantially but is not counted as primary "
    "success. NGC7814 remains the only all-TDF holdout failure, and UGC00128 remains a mixed "
    "near-tie case."
)

FINAL_CAVEATS: tuple[str, ...] = (
    "Results apply to the pre-registered expansion_20 controlled cohort only — not full-SPARC validation.",
    "Lensing is not tested in this repository phase.",
    "This benchmark does not disprove dark matter.",
    "Results do not replace ΛCDM as a cosmological framework.",
    "No universal τ-profile was discovered.",
    "tdf_5knot is sensitivity/high-flexibility only; tdf_3knot is the primary conservative TDF model.",
    "sensitivity_recovery cases must not be counted as primary robust success.",
    "No final or photometry-calibrated M/L model is claimed.",
    "Expansion_12 (12 galaxies) is a nested subset of expansion_20; cohort comparisons are descriptive.",
)

PHASE_STATUS_ROWS: list[dict[str, str]] = [
    {
        "phase": "5B",
        "main_output": "outputs/reports/expansion12_benchmark_report.md",
        "status": "complete",
        "supported_claim": "expansion_12 reproducible benchmark (12 galaxies)",
        "caveat": "Not full SPARC; tdf_3knot primary",
        "next_action": "Superseded by 5C/5E for expansion_20 headline",
    },
    {
        "phase": "5B-Audit",
        "main_output": "outputs/reports/expansion12_failure_mode_analysis_report.md",
        "status": "complete",
        "supported_claim": "NGC5055 ≠ NGC7814; UGC00128/UGC05253 mixed/flex diagnostics",
        "caveat": "No new fits",
        "next_action": "Guardrails carried into 5C",
    },
    {
        "phase": "5B-R",
        "main_output": "outputs/reports/expansion12_radial_residual_map_report.md",
        "status": "complete",
        "supported_claim": "Radial holdout maps for NGC5055, UGC05253 flex-recovery",
        "caveat": "Diagnostic refit of per-point holdout only",
        "next_action": "Optional UGC12506 radial maps deferred",
    },
    {
        "phase": "5C",
        "main_output": "outputs/reports/expansion20_benchmark_report.md",
        "status": "complete",
        "supported_claim": "expansion_20 benchmark; sensitivity_recovery class; 15/20 robust",
        "caveat": "Primary success = tdf_3knot only",
        "next_action": "5D audit of non-robust cases",
    },
    {
        "phase": "5D",
        "main_output": "outputs/reports/expansion20_failure_mode_analysis_report.md",
        "status": "complete",
        "supported_claim": "UGC12506 NGC5055-style knot-flexibility; five non-robust audited",
        "caveat": "Documentation only",
        "next_action": "5E final package",
    },
    {
        "phase": "5E",
        "main_output": "outputs/reports/controlled_expansion20_final_audit_report.md",
        "status": "complete",
        "supported_claim": FINAL_EXPANSION_20_CLAIM,
        "caveat": "; ".join(FINAL_CAVEATS[:4]),
        "next_action": "Publication handoff; full SPARC only after explicit scope change",
    },
]

C20_CLAIMS: list[dict[str, str]] = [
    {
        "claim_id": "C20-A",
        "claim_text": "expansion_20 cohort processed reproducibly through frozen pipeline.",
        "status": "supported",
        "allowed_language": "reproducible expansion_20 controlled benchmark",
        "prohibited_language": "full-SPARC validation; universal processing of all SPARC",
    },
    {
        "claim_id": "C20-B",
        "claim_text": "Primary tdf_3knot robust holdout success in 15 of 20 galaxies.",
        "status": "supported_with_caveat",
        "allowed_language": "15/20 robust_tdf_success at fixed baryons and K_tau",
        "prohibited_language": "all galaxies pass; TDF validated on SPARC",
    },
    {
        "claim_id": "C20-C",
        "claim_text": "tdf_5knot improves sensitivity-recovery cases.",
        "status": "supported_sensitivity_only",
        "allowed_language": "three sensitivity_recovery cases; tdf_5knot diagnostic improvement",
        "prohibited_language": "tdf_5knot primary success; count flex recovery as robust win",
    },
    {
        "claim_id": "C20-D",
        "claim_text": "NGC7814 remains all-TDF holdout failure.",
        "status": "supported",
        "allowed_language": "canonical all-TDF failure; mandated label",
        "prohibited_language": "NGC7814 solved; TDF works for NGC7814",
    },
    {
        "claim_id": "C20-E",
        "claim_text": "TDF validated on full SPARC.",
        "status": "not_supported",
        "allowed_language": "expansion_20 controlled cohort only",
        "prohibited_language": "validated on SPARC; SPARC validates TDF",
    },
    {
        "claim_id": "C20-F",
        "claim_text": "Dark matter is disproven.",
        "status": "prohibited",
        "allowed_language": "does not disprove dark matter",
        "prohibited_language": "dark matter disproven; DM is wrong",
    },
    {
        "claim_id": "C20-G",
        "claim_text": "Lensing confirms TDF.",
        "status": "not_tested",
        "allowed_language": "lensing not tested",
        "prohibited_language": "lensing confirmed; lensing validates TDF",
    },
    {
        "claim_id": "C20-H",
        "claim_text": "Universal τ-profile discovered.",
        "status": "not_supported",
        "allowed_language": "per-galaxy τ diagnostics on controlled cohort",
        "prohibited_language": "universal τ-profile; τ law for all galaxies",
    },
]


def _count_class(df: pd.DataFrame, label: str) -> int:
    col = "failure_mode_classification"
    return int((df[col] == label).sum())


def _tdf3_beats_mond(df: pd.DataFrame) -> int:
    if "tdf_3knot_beats_mond_holdout" in df.columns:
        return int(df["tdf_3knot_beats_mond_holdout"].astype(bool).sum())
    if "tdf_3knot_holdout_rmse_kms" not in df.columns:
        return 0
    return int(
        (
            df["tdf_3knot_holdout_rmse_kms"].astype(float)
            < df["mond_fit_a0_holdout_rmse_kms"].astype(float)
        ).sum()
    )


def build_expansion_comparison_summary(
    e12_summary: pd.DataFrame,
    e20_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Side-by-side cohort metrics for expansion_12 vs expansion_20."""
    n12 = len(e12_summary)
    n20 = len(e20_summary)

    rows: list[dict[str, Any]] = [
        {
            "metric": "cohort_size",
            "expansion_12": n12,
            "expansion_20": n20,
            "notes": "expansion_12 ⊂ expansion_20 (same original six + overlapping additions)",
        },
        {
            "metric": "robust_tdf_success",
            "expansion_12": _count_class(e12_summary, "robust_tdf_success"),
            "expansion_20": _count_class(e20_summary, "robust_tdf_success"),
            "notes": "Primary conservative success (tdf_3knot beats NFW and MOND on holdout for e20)",
        },
        {
            "metric": "sensitivity_recovery",
            "expansion_12": _count_class(e12_summary, "sensitivity_recovery"),
            "expansion_20": _count_class(e20_summary, "sensitivity_recovery"),
            "notes": "Phase 5C class; not counted as primary success in e20",
        },
        {
            "metric": "tdf_failure_mode",
            "expansion_12": _count_class(e12_summary, "tdf_failure_mode"),
            "expansion_20": _count_class(e20_summary, "tdf_failure_mode"),
            "notes": "NGC7814 all-TDF failure in both cohorts",
        },
        {
            "metric": "mixed_result",
            "expansion_12": _count_class(e12_summary, "mixed_result"),
            "expansion_20": _count_class(e20_summary, "mixed_result"),
            "notes": "UGC00128 near-tie in both",
        },
        {
            "metric": "tdf_3knot_beats_nfw_holdout",
            "expansion_12": int(e12_summary["tdf_3knot_beats_nfw_holdout"].astype(bool).sum()),
            "expansion_20": int(e20_summary["tdf_3knot_beats_nfw_holdout"].astype(bool).sum()),
            "notes": "even/odd holdout; train-only refit",
        },
        {
            "metric": "tdf_3knot_beats_mond_holdout",
            "expansion_12": _tdf3_beats_mond(e12_summary),
            "expansion_20": _tdf3_beats_mond(e20_summary),
            "notes": "Required for robust_tdf_success in expansion_20",
        },
        {
            "metric": "primary_success_fraction",
            "expansion_12": round(_count_class(e12_summary, "robust_tdf_success") / n12, 3)
            if n12
            else float("nan"),
            "expansion_20": round(_count_class(e20_summary, "robust_tdf_success") / n20, 3)
            if n20
            else float("nan"),
            "notes": "robust_tdf_success / cohort_size",
        },
    ]
    return pd.DataFrame(rows)


def build_final_expansion_claims_table(
    e20_claims_path: Path | str = "outputs/tables/expansion20_claim_traceability.csv",
) -> pd.DataFrame:
    rows = list(C20_CLAIMS)
    path = Path(e20_claims_path)
    if path.is_file():
        prior = pd.read_csv(path)
        existing = {str(x) for x in prior.get("claim_id", [])}
        for r in rows:
            if r["claim_id"] in existing:
                continue
    rows.append(
        {
            "claim_id": "FINAL-E20",
            "claim_text": FINAL_EXPANSION_20_CLAIM,
            "status": "supported_with_caveats",
            "allowed_language": "15/20 robust; 3 sensitivity_recovery; NGC7814 failure; UGC00128 mixed",
            "prohibited_language": "full SPARC; DM disproof; tdf_5knot as primary",
        }
    )
    return pd.DataFrame(rows)


def build_phase_status_table() -> pd.DataFrame:
    return pd.DataFrame(PHASE_STATUS_ROWS)


def write_controlled_expansion_final_report(
    path: Path | str,
    *,
    comparison: pd.DataFrame,
    claims: pd.DataFrame,
    e12_summary: pd.DataFrame,
    e20_summary: pd.DataFrame,
    status: pd.DataFrame,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    def _metric(name: str) -> tuple[Any, Any]:
        row = comparison[comparison["metric"] == name]
        if row.empty:
            return "—", "—"
        r = row.iloc[0]
        return r["expansion_12"], r["expansion_20"]

    lines = [
        "# Controlled Expansion Cohort — Final Audit Report (Phase 5E)",
        "",
        f"> Audit version: `{AUDIT_VERSION}`. **Documentation and consolidation only** — "
        "no new fits, no new models, no full SPARC, no lensing.",
        "",
        "## Final expansion_20 statement",
        "",
        f"> {FINAL_EXPANSION_20_CLAIM}",
        "",
        "## Required caveats",
        "",
    ]
    for c in FINAL_CAVEATS:
        lines.append(f"- {c}")

    lines.extend(
        [
            "",
            "## expansion_12 vs expansion_20 comparison",
            "",
            "| Metric | expansion_12 | expansion_20 |",
            "| --- | ---: | ---: |",
        ]
    )
    for _, r in comparison.iterrows():
        lines.append(f"| {r['metric']} | {r['expansion_12']} | {r['expansion_20']} |")

    r12, r20 = _metric("robust_tdf_success")
    s12, s20 = _metric("sensitivity_recovery")
    f12, f20 = _metric("tdf_failure_mode")
    m12, m20 = _metric("mixed_result")
    n12, n20 = _metric("tdf_3knot_beats_nfw_holdout")
    mond12, mond20 = _metric("tdf_3knot_beats_mond_holdout")

    lines.extend(
        [
            "",
            "### Interpretation",
            "",
            f"- **Robust primary success:** {r12}/12 → **{r20}/20** (tdf_3knot holdout gate).",
            f"- **Sensitivity-recovery:** {s12}/12 → **{s20}/20** "
            f"(NGC5055, UGC05253, UGC12506 in e20; e12 used legacy labels — "
            "NGC5055 was `tdf_failure_mode` in 5B, reclassified in 5C).",
            f"- **All-TDF failure:** {f12} (NGC7814) in both cohorts.",
            f"- **Mixed near-tie:** {m12} (UGC00128) in both cohorts.",
            f"- **tdf_3knot vs NFW holdout:** {n12}/12 → {n20}/20.",
            f"- **tdf_3knot vs MOND holdout:** {mond12}/12 → {mond20}/20.",
            "",
            "## Phase 5B–5D consolidation",
            "",
            "| Phase | Focus |",
            "| --- | --- |",
            "| 5B | expansion_12 benchmark (12 galaxies) |",
            "| 5B-Audit | NGC7814, NGC5055, UGC00128, UGC05253 failure/mixed diagnostics |",
            "| 5B-R | Radial holdout maps for NGC5055, UGC05253 |",
            "| 5C | expansion_20 benchmark with sensitivity_recovery class |",
            "| 5D | Five non-robust e20 cases; UGC12506 archetype |",
            "",
            "## Per-galaxy expansion_20 classification",
            "",
            "| Galaxy | Class | tdf_3knot | tdf_5knot | NFW | MOND | Primary? |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for _, row in e20_summary.sort_values("galaxy_id").iterrows():
        primary = "yes" if row.get("counts_as_primary_success", row["failure_mode_classification"] == "robust_tdf_success") else "no"
        if "counts_as_primary_success" not in e20_summary.columns:
            primary = "yes" if row["failure_mode_classification"] == "robust_tdf_success" else "no"
        lines.append(
            f"| {row['galaxy_id']} | {row['failure_mode_classification']} | "
            f"{row['tdf_3knot_holdout_rmse_kms']:.1f} | {row['tdf_5knot_holdout_rmse_kms']:.1f} | "
            f"{row['nfw_refit_holdout_rmse_kms']:.1f} | {row['mond_fit_a0_holdout_rmse_kms']:.1f} | {primary} |"
        )

    lines.extend(
        [
            "",
            "## Non-robust cases (expansion_20)",
            "",
            "- **NGC7814:** all-TDF failure (tdf_3knot and tdf_5knot fail vs baselines).",
            "- **NGC5055, UGC05253, UGC12506:** sensitivity_recovery — tdf_5knot recovers; not primary.",
            "- **UGC00128:** mixed near-tie; NFW marginally best.",
            "",
            "## Claims C20-A – C20-H",
            "",
            "| ID | Status | Claim |",
            "| --- | --- | --- |",
        ]
    )
    c20 = claims[claims["claim_id"].astype(str).str.startswith("C20")]
    for _, r in c20.iterrows():
        lines.append(f"| {r['claim_id']} | {r['status']} | {str(r['claim_text'])[:70]}... |")

    lines.extend(
        [
            "",
            "## Phase status (5B–5E)",
            "",
            "| Phase | Output | Status |",
            "| --- | --- | --- |",
        ]
    )
    for _, r in status.iterrows():
        lines.append(f"| {r['phase']} | `{r['main_output']}` | {r['status']} |")

    lines.extend(
        [
            "",
            "## Key artifacts",
            "",
            "- `outputs/tables/controlled_expansion_comparison_summary.csv`",
            "- `outputs/tables/controlled_expansion_final_claims.csv`",
            "- `docs/controlled_expansion_results.md`",
            "- `docs/paper_ready_claims.md` (expansion section)",
            "",
            "## Recommended next steps",
            "",
            "1. Publication tables from expansion_20 failure summary and comparison CSV.",
            "2. Optional blocked-holdout stability for UGC12506.",
            "3. Full SPARC or lensing only after explicit protocol amendment and claim review.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_controlled_expansion_final_audit(
    *,
    e12_summary_path: Path | str = "outputs/tables/expansion12_failure_mode_summary.csv",
    e20_summary_path: Path | str = "outputs/tables/expansion20_failure_mode_summary.csv",
    comparison_out: Path | str = "outputs/tables/controlled_expansion_comparison_summary.csv",
    claims_out: Path | str = "outputs/tables/controlled_expansion_final_claims.csv",
    report_out: Path | str = "outputs/reports/controlled_expansion20_final_audit_report.md",
) -> dict[str, pd.DataFrame]:
    e12 = pd.read_csv(e12_summary_path)
    e20 = pd.read_csv(e20_summary_path)

    comparison = build_expansion_comparison_summary(e12, e20)
    claims = build_final_expansion_claims_table()
    status = build_phase_status_table()

    comparison.to_csv(comparison_out, index=False)
    claims.to_csv(claims_out, index=False)
    write_controlled_expansion_final_report(
        report_out,
        comparison=comparison,
        claims=claims,
        e12_summary=e12,
        e20_summary=e20,
        status=status,
    )

    return {
        "comparison": comparison,
        "claims": claims,
        "status": status,
        "expansion12_summary": e12,
        "expansion20_summary": e20,
    }
