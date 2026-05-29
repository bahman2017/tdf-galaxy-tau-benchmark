from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PHASE_DISCLAIMER = (
    "Phase 5F-B composes publication figures from frozen audited benchmark outputs only. "
    "No model fitting and no modification of benchmark tables under outputs/tables/expansion20_*."
)

PAPER_FIGURE_NAMES = (
    "fig1_benchmark_workflow.png",
    "fig2_expansion12_vs_20_summary.png",
    "fig3_representative_successes.png",
    "fig4_ngc7814_failure.png",
    "fig5_sensitivity_recovery_cases.png",
    "fig6_holdout_rmse_comparison.png",
    "fig7_claim_boundary_map.png",
)

SUCCESS_GALAXY_IDS = ("DDO154", "NGC2403", "NGC3198")
SENSITIVITY_GALAXY_IDS = ("NGC5055", "UGC05253", "UGC12506")

CLAIM_STATUS_COLORS = {
    "supported": "#2ca02c",
    "supported_with_caveat": "#98df8a",
    "supported_sensitivity_only": "#ff7f0e",
    "supported_with_caveats": "#98df8a",
    "not_supported": "#bdbdbd",
    "not_tested": "#c7c7c7",
    "prohibited": "#d62728",
}

CLAIM_STATUS_LABELS = {
    "supported": "supported",
    "supported_with_caveat": "supported (caveat)",
    "supported_sensitivity_only": "sensitivity only",
    "supported_with_caveats": "supported (caveats)",
    "not_supported": "not supported",
    "not_tested": "not tested",
    "prohibited": "prohibited",
}


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _figures_subset_dir(root: Path) -> Path:
    return root / "outputs/figures/sparc_subset"


def _load_image(path: Path):
    from matplotlib import image as mpimg

    if not path.is_file():
        raise FileNotFoundError(path)
    return mpimg.imread(path)


def _compose_row(
    image_paths: list[Path],
    out_path: Path,
    *,
    titles: list[str] | None = None,
    suptitle: str | None = None,
    figsize: tuple[float, float] = (14, 4.5),
    dpi: int = 150,
) -> Path:
    plt = _plt()
    n = len(image_paths)
    fig, axes = plt.subplots(1, n, figsize=figsize)
    if n == 1:
        axes = [axes]
    for ax, img_path, title in zip(axes, image_paths, titles or [""] * n):
        ax.imshow(_load_image(img_path))
        ax.axis("off")
        if title:
            ax.set_title(title, fontsize=10)
    if suptitle:
        fig.suptitle(suptitle, fontsize=11, y=1.02)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_fig1_workflow(out_path: Path) -> Path:
    """Benchmark pipeline schematic; tdf_5knot as dashed sensitivity branch."""
    plt = _plt()
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    def box(xy, text, *, primary=True, width=1.8, height=0.55):
        x, y = xy
        fc = "#e8f4fc" if primary else "#fff3e0"
        ec = "#1f77b4" if primary else "#ff7f0e"
        p = FancyBboxPatch(
            (x - width / 2, y - height / 2),
            width,
            height,
            boxstyle="round,pad=0.03",
            linewidth=1.5 if primary else 1.2,
            edgecolor=ec,
            facecolor=fc,
            linestyle="-" if primary else "--",
        )
        ax.add_patch(p)
        ax.text(x, y, text, ha="center", va="center", fontsize=8, wrap=True)

    def arrow(p0, p1, *, style="-"):
        ax.add_patch(
            FancyArrowPatch(
                p0,
                p1,
                arrowstyle="->",
                mutation_scale=12,
                linewidth=1.2,
                linestyle=style,
                color="#333333",
            )
        )

    y_main = 8.5
    steps = [
        (1.0, "SPARC\ningestion"),
        (2.6, "Subset\nprotocol"),
        (4.2, "τ\nreconstruction"),
        (5.8, "Baselines\nNFW / Burkert / MOND"),
        (7.4, "tdf_3knot\n(primary)"),
        (9.0, "Holdout\nvalidation"),
    ]
    for i, (x, t) in enumerate(steps):
        box((x, y_main), t, primary=True)
        if i > 0:
            arrow((steps[i - 1][0] + 0.95, y_main), (x - 0.95, y_main))

    y_audit = 5.8
    box((7.4, y_audit), "Failure-mode\naudit", primary=True)
    box((9.0, y_audit), "Claim\ntraceability", primary=True)
    arrow((9.0, y_main - 0.35), (9.0, y_audit + 0.35))
    arrow((7.4, y_main - 0.35), (7.4, y_audit + 0.35))
    arrow((7.4 + 0.95, y_audit), (9.0 - 0.95, y_audit))

    box((7.4, 3.2), "tdf_5knot\n(sensitivity only)", primary=False)
    arrow((7.4, y_main - 0.35), (7.4, 3.55), style="--")
    ax.text(
        8.35,
        5.9,
        "higher flexibility;\nnot primary success",
        fontsize=7,
        color="#cc6600",
        style="italic",
    )

    ax.text(
        5.0,
        1.2,
        "Controlled expansion benchmark (Phases 5B–5E) — composition only; no new fits",
        ha="center",
        fontsize=9,
        color="#444444",
    )
    fig.suptitle("Fig. 1 — Controlled benchmark workflow", fontsize=12, y=0.98)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_fig2_expansion_summary(
    comparison: pd.DataFrame,
    out_path: Path,
) -> Path:
    """expansion_12 vs expansion_20 classification counts."""
    plt = _plt()
    metrics = [
        ("robust_tdf_success", "robust (primary)", "#2ca02c"),
        ("sensitivity_recovery", "sensitivity recovery", "#ff7f0e"),
        ("tdf_failure_mode", "TDF failure", "#d62728"),
        ("mixed_result", "mixed", "#9467bd"),
    ]
    x = np.arange(len(metrics))
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for i, (metric, label, color) in enumerate(metrics):
        row = comparison[comparison["metric"] == metric]
        if row.empty:
            continue
        e12 = float(row.iloc[0]["expansion_12"])
        e20 = float(row.iloc[0]["expansion_20"])
        ax.bar(x[i] - w / 2, e12, width=w, label="expansion_12" if i == 0 else "", color=color, alpha=0.55)
        ax.bar(x[i] + w / 2, e20, width=w, label="expansion_20" if i == 0 else "", color=color, alpha=1.0)
        ax.text(x[i] - w / 2, e12 + 0.15, f"{int(e12)}", ha="center", fontsize=8)
        ax.text(x[i] + w / 2, e20 + 0.15, f"{int(e20)}", ha="center", fontsize=8)

    cohort = comparison[comparison["metric"] == "cohort_size"].iloc[0]
    ax.set_title(
        f"Fig. 2 — Cohort classification (n₁₂={int(cohort['expansion_12'])}, "
        f"n₂₀={int(cohort['expansion_20'])})"
    )
    ax.set_xticks(x)
    ax.set_xticklabels([m[1] for m in metrics], rotation=15, ha="right")
    ax.set_ylabel("galaxy count")
    ax.legend(loc="upper left")
    ax.axhline(0, color="k", lw=0.5)
    ax.text(
        0.02,
        0.98,
        "Primary success (robust) ≠ sensitivity recovery (tdf_5knot only)",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
        style="italic",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.4),
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_fig3_representative_successes(root: Path, out_path: Path) -> Path:
    fig_dir = _figures_subset_dir(root)
    paths = [
        fig_dir / f"{gid}_full_model_rotation_comparison.png" for gid in SUCCESS_GALAXY_IDS
    ]
    return _compose_row(
        paths,
        out_path,
        titles=list(SUCCESS_GALAXY_IDS),
        suptitle="Fig. 3 — Representative robust successes (existing rotation-curve panels)",
        figsize=(15, 4.8),
    )


def build_fig4_ngc7814_failure(root: Path, out_path: Path) -> Path:
    fig_dir = _figures_subset_dir(root)
    paths = [
        fig_dir / "NGC7814_full_model_rotation_comparison.png",
        fig_dir / "ngc7814_radial_holdout_residual_map.png",
    ]
    plt = _plt()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    titles = ["Rotation comparison", "Radial holdout residual map"]
    for ax, p, title in zip(axes, paths, titles):
        ax.imshow(_load_image(p))
        ax.axis("off")
        ax.set_title(title, fontsize=10)
    fig.suptitle(
        "Fig. 4 — NGC7814: canonical all-TDF holdout failure\n"
        "(descriptive benchmark label; not a causal claim)",
        fontsize=11,
        y=1.05,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_fig5_sensitivity_recovery(
    root: Path,
    diagnostics: pd.DataFrame,
    out_path: Path,
) -> Path:
    fig_dir = _figures_subset_dir(root)
    plt = _plt()
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))

    radial_paths = {
        "NGC5055": fig_dir / "ngc5055_radial_holdout_residuals.png",
        "UGC05253": fig_dir / "ugc05253_radial_holdout_residuals.png",
    }
    for ax, gid in zip(axes[:2], SENSITIVITY_GALAXY_IDS[:2]):
        ax.imshow(_load_image(radial_paths[gid]))
        ax.axis("off")
        ax.set_title(gid, fontsize=10)

    ax = axes[2]
    row = diagnostics[diagnostics["galaxy_id"] == "UGC12506"].iloc[0]
    models = ["tdf_3knot", "tdf_5knot", "nfw_refit", "mond"]
    vals = [
        row["tdf_3knot_holdout_rmse_kms"],
        row["tdf_5knot_holdout_rmse_kms"],
        row["nfw_refit_holdout_rmse_kms"],
        row["mond_fit_a0_holdout_rmse_kms"],
    ]
    colors = ["#2ca02c", "#ff7f0e", "#1f77b4", "#9467bd"]
    x = np.arange(len(models))
    ax.bar(x, vals, color=colors)
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("holdout RMSE [km/s]")
    ax.set_title("UGC12506")
    ax.grid(axis="y", alpha=0.3)

    fig.suptitle(
        "Fig. 5 — Sensitivity-recovery (tdf_5knot only; not primary success)",
        fontsize=11,
        y=1.02,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_fig6_holdout_rmse_comparison(
    failure_summary: pd.DataFrame,
    out_path: Path,
) -> Path:
    """Per-galaxy even/odd holdout RMSE; primary vs sensitivity models."""
    plt = _plt()
    df = failure_summary.sort_values("galaxy_id").reset_index(drop=True)
    gids = df["galaxy_id"].tolist()
    x = np.arange(len(gids))

    r3 = df["tdf_3knot_holdout_rmse_kms"].to_numpy()
    r5 = df["tdf_5knot_holdout_rmse_kms"].to_numpy()
    rnfw = df["nfw_refit_holdout_rmse_kms"].to_numpy()
    rmond = df["mond_fit_a0_holdout_rmse_kms"].to_numpy()

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={"height_ratios": [2, 1]})
    w = 0.2
    ax_top.bar(x - 1.5 * w, r3, width=w, label="tdf_3knot (primary)", color="#2ca02c")
    ax_top.bar(x - 0.5 * w, rnfw, width=w, label="NFW refit", color="#1f77b4", alpha=0.85)
    ax_top.bar(x + 0.5 * w, rmond, width=w, label="MOND fit a₀", color="#9467bd", alpha=0.85)
    ax_top.bar(
        x + 1.5 * w,
        r5,
        width=w,
        label="tdf_5knot (sensitivity)",
        color="#ff7f0e",
        hatch="//",
        edgecolor="#cc6600",
    )
    for i, cls in enumerate(df["failure_mode_classification"]):
        if cls == "tdf_failure_mode":
            ax_top.axvspan(i - 0.5, i + 0.5, color="#d62728", alpha=0.08)
        elif cls == "sensitivity_recovery":
            ax_top.axvspan(i - 0.5, i + 0.5, color="#ff7f0e", alpha=0.06)

    ax_top.set_ylabel("even/odd holdout RMSE [km/s]")
    ax_top.set_title("Fig. 6 — Holdout RMSE by galaxy (expansion_20)")
    ax_top.legend(loc="upper right", fontsize=8, ncol=2)
    ax_top.set_xticks(x)
    ax_top.set_xticklabels([])
    ax_top.grid(axis="y", alpha=0.3)

    wins3 = df["tdf_3knot_beats_nfw_holdout"].astype(int) + df["tdf_3knot_beats_mond_holdout"].astype(int)
    ax_bot.bar(x, wins3, color="#2ca02c", alpha=0.7)
    ax_bot.set_ylabel("beats (NFW+MOND)")
    ax_bot.set_ylim(0, 2.2)
    ax_bot.set_xticks(x)
    ax_bot.set_xticklabels(gids, rotation=60, ha="right", fontsize=7)
    ax_bot.axhline(2, color="k", ls="--", lw=0.6, alpha=0.5)
    ax_bot.text(
        0.01,
        0.95,
        "Shaded: failure (red) / sensitivity-recovery (orange). Hatched bars = not primary claim.",
        transform=ax_bot.transAxes,
        fontsize=7,
        va="top",
    )

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_fig7_claim_boundary_map(claims: pd.DataFrame, out_path: Path) -> Path:
    plt = _plt()
    from matplotlib.patches import Rectangle

    c20 = claims[claims["claim_id"].str.match(r"^C20-[A-H]$")].copy()
    c20 = c20.sort_values("claim_id")

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(c20) + 1)
    ax.axis("off")

    legend_handles = []
    for status, color in CLAIM_STATUS_COLORS.items():
        if status == "supported_with_caveats":
            continue
        legend_handles.append(
            Rectangle((0, 0), 1, 1, fc=color, ec="k", lw=0.5, label=CLAIM_STATUS_LABELS.get(status, status))
        )
    ax.legend(handles=legend_handles, loc="lower center", ncol=4, fontsize=8, bbox_to_anchor=(0.5, -0.02))

    for i, (_, row) in enumerate(c20.iterrows()):
        y = len(c20) - i
        status = str(row["status"])
        color = CLAIM_STATUS_COLORS.get(status, "#eeeeee")
        ax.add_patch(Rectangle((0.3, y - 0.35), 9.4, 0.7, fc=color, ec="#333333", lw=0.8, alpha=0.85))
        ax.text(0.5, y, row["claim_id"], fontsize=10, fontweight="bold", va="center")
        ax.text(1.4, y, str(row["claim_text"])[:72] + ("…" if len(str(row["claim_text"])) > 72 else ""), fontsize=8, va="center")
        ax.text(9.2, y, CLAIM_STATUS_LABELS.get(status, status), fontsize=7, ha="right", va="center")

    ax.set_title("Fig. 7 — Claim-boundary evidence map (expansion_20)", fontsize=12, pad=12)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def write_paper_figures_report(
    path: Path | str,
    *,
    built: dict[str, Path],
    root: Path,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Paper Figures Report (Phase 5F-B)",
        "",
        f"> {PHASE_DISCLAIMER}",
        "",
        "## Figures built",
        "",
        "| File | Path |",
        "| --- | --- |",
    ]
    for name in PAPER_FIGURE_NAMES:
        p = built.get(name)
        if p and p.is_file():
            try:
                rel = p.relative_to(root)
            except ValueError:
                rel = p
        else:
            rel = "—"
        lines.append(f"| {name} | `{rel}` |")

    lines.extend(
        [
            "",
            "## Composition notes",
            "",
            "- **Fig1:** matplotlib workflow schematic; dashed branch = tdf_5knot sensitivity.",
            "- **Fig2:** bar chart from `controlled_expansion_comparison_summary.csv`.",
            "- **Fig3:** 1×3 mosaic of existing `*_full_model_rotation_comparison.png` panels.",
            "- **Fig4:** NGC7814 rotation + radial holdout map; descriptive failure label only.",
            "- **Fig5:** radial maps (NGC5055, UGC05253) + UGC12506 holdout bars from diagnostics CSV.",
            "- **Fig6:** expansion_20 per-galaxy holdout RMSE; hatched tdf_5knot = sensitivity only.",
            "- **Fig7:** C20-A–H claim status map from `controlled_expansion_final_claims.csv`.",
            "",
            "## Benchmark outputs",
            "",
            "No files under `outputs/tables/expansion20_*` or other benchmark tables were modified.",
            "",
            "## Regenerate",
            "",
            "```bash",
            "python3 scripts/build_paper_figures.py",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_paper_figures_build(
    *,
    root: Path | str = ".",
    paper_figures_dir: Path | str = "paper/figures",
    comparison_csv: Path | str = "outputs/tables/controlled_expansion_comparison_summary.csv",
    claims_csv: Path | str = "outputs/tables/controlled_expansion_final_claims.csv",
    failure_summary_csv: Path | str = "outputs/tables/expansion20_failure_mode_summary.csv",
    failure_diagnostics_csv: Path | str = "outputs/tables/expansion20_failure_diagnostics.csv",
    report_out: Path | str = "outputs/reports/paper_figures_report.md",
) -> dict[str, Path]:
    root = Path(root).resolve()
    out_dir = Path(paper_figures_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir

    comparison = pd.read_csv(root / comparison_csv)
    claims = pd.read_csv(root / claims_csv)
    failure_summary = pd.read_csv(root / failure_summary_csv)
    diagnostics = pd.read_csv(root / failure_diagnostics_csv)

    built: dict[str, Path] = {}
    built["fig1_benchmark_workflow.png"] = build_fig1_workflow(out_dir / "fig1_benchmark_workflow.png")
    built["fig2_expansion12_vs_20_summary.png"] = build_fig2_expansion_summary(
        comparison, out_dir / "fig2_expansion12_vs_20_summary.png"
    )
    built["fig3_representative_successes.png"] = build_fig3_representative_successes(
        root, out_dir / "fig3_representative_successes.png"
    )
    built["fig4_ngc7814_failure.png"] = build_fig4_ngc7814_failure(root, out_dir / "fig4_ngc7814_failure.png")
    built["fig5_sensitivity_recovery_cases.png"] = build_fig5_sensitivity_recovery(
        root, diagnostics, out_dir / "fig5_sensitivity_recovery_cases.png"
    )
    built["fig6_holdout_rmse_comparison.png"] = build_fig6_holdout_rmse_comparison(
        failure_summary, out_dir / "fig6_holdout_rmse_comparison.png"
    )
    built["fig7_claim_boundary_map.png"] = build_fig7_claim_boundary_map(
        claims, out_dir / "fig7_claim_boundary_map.png"
    )

    write_paper_figures_report(report_out if Path(report_out).is_absolute() else root / report_out, built=built, root=root)
    return built
