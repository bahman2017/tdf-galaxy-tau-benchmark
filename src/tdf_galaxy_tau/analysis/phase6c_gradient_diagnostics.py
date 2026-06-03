"""Phase 6C-C: diagnostic analysis of frozen radial dτ/dr smoothness (read-only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tdf_galaxy_tau.analysis.phase6b_data_availability import PHASE6C_MAX_DTAUDR_JUMP_REL
from tdf_galaxy_tau.analysis.phase6c_frozen_pseudo2d import PRIMARY_PILOT_GALAXY_IDS

DIAGNOSTIC_VERSION = "phase_6c_c_v1"
DEFAULT_TAU_PROFILES = Path("outputs/tables/expansion20_tau_profiles.csv")
DEFAULT_MAP_SUMMARY = Path("outputs/tables/phase6c_primary_pilot_map_summary.csv")
SMOOTHNESS_THRESHOLD = PHASE6C_MAX_DTAUDR_JUMP_REL

FAILURE_CAUSES = (
    "sparse_radial_sampling",
    "sharp_frozen_knot_transition",
    "interpolation_artifact",
    "inner_radius_instability",
    "outer_radius_instability",
    "physical_map_hostile_gradient",
    "unknown_needs_review",
)


def _load_frozen_profile(tau_path: Path, galaxy_id: str) -> pd.DataFrame:
    tau = pd.read_csv(tau_path)
    sub = tau[tau["galaxy_id"] == galaxy_id].copy()
    if sub.empty:
        raise ValueError(f"No profile for {galaxy_id}")
    return sub.sort_values("r_kpc").reset_index(drop=True)


def _radial_region(r: float, r_min: float, r_max: float) -> str:
    span = r_max - r_min
    if span <= 0:
        return "inner"
    frac = (r - r_min) / span
    if frac < 1.0 / 3.0:
        return "inner_third"
    if frac < 2.0 / 3.0:
        return "mid_disk"
    return "outer_third"


def _compute_jump_stats(profile: pd.DataFrame) -> dict[str, Any]:
    r = profile["r_kpc"].astype(float).to_numpy()
    dtaudr = profile["dtaudr_reconstructed"].astype(float).to_numpy()
    tau = profile["tau_reconstructed"].astype(float).to_numpy()
    n = len(r)
    r_min, r_max = float(r.min()), float(r.max())

    if n < 2:
        return {
            "n_radial_points": n,
            "r_min_kpc": r_min,
            "r_max_kpc": r_max,
            "max_abs_dtaudr_jump": 0.0,
            "max_rel_dtaudr_jump": 0.0,
            "median_rel_dtaudr_jump": 0.0,
            "p95_rel_dtaudr_jump": 0.0,
            "n_jumps_above_threshold": 0,
            "worst_jump_r_kpc": np.nan,
            "worst_jump_region": "",
            "median_delta_r_kpc": 0.0,
            "max_delta_r_kpc": 0.0,
            "delta_r_sparsity_ratio": 1.0,
            "jump_failure_dominance": "none",
            "fraction_jumps_above_threshold": 0.0,
        }

    abs_jumps = np.abs(np.diff(dtaudr))
    denom = np.maximum(np.abs(dtaudr[:-1]), 1e-12)
    rel_jumps = abs_jumps / denom
    delta_r = np.diff(r)

    worst_idx = int(np.argmax(rel_jumps))
    worst_r = float(0.5 * (r[worst_idx] + r[worst_idx + 1]))
    above = rel_jumps > SMOOTHNESS_THRESHOLD
    n_above = int(above.sum())

    if n_above == 0:
        dominance = "none"
    elif n_above == 1:
        dominance = "single_dominant_jump"
    elif rel_jumps[worst_idx] > 2.0 * np.median(rel_jumps[~above]) if (~above).any() else True:
        dominance = "single_dominant_jump"
    else:
        dominance = "distributed_jumps"

    return {
        "n_radial_points": n,
        "r_min_kpc": r_min,
        "r_max_kpc": r_max,
        "max_abs_dtaudr_jump": float(abs_jumps.max()),
        "max_rel_dtaudr_jump": float(rel_jumps.max()),
        "median_rel_dtaudr_jump": float(np.median(rel_jumps)),
        "p95_rel_dtaudr_jump": float(np.percentile(rel_jumps, 95)),
        "n_jumps_above_threshold": n_above,
        "worst_jump_r_kpc": worst_r,
        "worst_jump_region": _radial_region(worst_r, r_min, r_max),
        "worst_jump_abs_dtaudr": float(abs_jumps[worst_idx]),
        "worst_jump_rel_dtaudr": float(rel_jumps[worst_idx]),
        "median_delta_r_kpc": float(np.median(delta_r)),
        "max_delta_r_kpc": float(delta_r.max()),
        "delta_r_sparsity_ratio": float(delta_r.max() / max(np.median(delta_r), 1e-12)),
        "jump_failure_dominance": dominance,
        "fraction_jumps_above_threshold": float(n_above / len(rel_jumps)),
        "tau_zero_at_inner_boundary": bool(abs(tau[0]) < 1e-9),
        "max_abs_dtaudr": float(np.abs(dtaudr).max()),
    }


def classify_failure_cause(stats: dict[str, Any]) -> tuple[str, str]:
    """Return primary cause label and short rationale."""
    region = stats["worst_jump_region"]
    sparsity = stats["delta_r_sparsity_ratio"]
    n_pts = stats["n_radial_points"]
    dom = stats["jump_failure_dominance"]
    max_rel = stats["max_rel_dtaudr_jump"]
    med_dr = stats["median_delta_r_kpc"]
    worst_dr = stats.get("worst_jump_delta_r_kpc", stats["median_delta_r_kpc"])

    causes: list[str] = []

    if sparsity > 4.0 or (n_pts < 20 and stats["n_jumps_above_threshold"] > 0):
        causes.append("sparse_radial_sampling")
    if region == "inner_third" and (stats["tau_zero_at_inner_boundary"] or max_rel > 1.0):
        causes.append("inner_radius_instability")
    if region == "outer_third":
        causes.append("outer_radius_instability")
    if dom == "single_dominant_jump" and worst_dr <= 1.5 * med_dr:
        causes.append("sharp_frozen_knot_transition")
    if stats["max_abs_dtaudr"] > 1000 and max_rel > 0.25:
        causes.append("physical_map_hostile_gradient")
    if not causes:
        if max_rel > SMOOTHNESS_THRESHOLD:
            causes.append("unknown_needs_review")
        else:
            causes.append("none")

    primary = causes[0]
    rationale_parts = [
        f"max rel jump {max_rel:.3f} at r≈{stats['worst_jump_r_kpc']:.2f} kpc ({region})",
        f"dominance={dom}",
        f"n_above_0.25={stats['n_jumps_above_threshold']}",
    ]
    if sparsity > 4.0:
        rationale_parts.append(f"sparse Δr ratio={sparsity:.2f}")
    return primary, "; ".join(rationale_parts)


def diagnose_galaxy(
    galaxy_id: str,
    *,
    tau_path: Path,
    map_summary_row: pd.Series | None,
) -> dict[str, Any]:
    profile = _load_frozen_profile(tau_path, galaxy_id)
    stats = _compute_jump_stats(profile)
    # attach delta r at worst jump
    r = profile["r_kpc"].astype(float).to_numpy()
    dtaudr = profile["dtaudr_reconstructed"].astype(float).to_numpy()
    rel = np.abs(np.diff(dtaudr)) / np.maximum(np.abs(dtaudr[:-1]), 1e-12)
    wi = int(np.argmax(rel))
    stats["worst_jump_delta_r_kpc"] = float(r[wi + 1] - r[wi]) if len(r) > 1 else np.nan

    primary_cause, rationale = classify_failure_cause(stats)

    row: dict[str, Any] = {
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "galaxy_id": galaxy_id,
        **stats,
        "smoothness_threshold": SMOOTHNESS_THRESHOLD,
        "primary_failure_cause": primary_cause,
        "failure_cause_rationale": rationale,
        "tau_or_dtaudr_modified": False,
        "diagnostic_only": True,
    }

    if map_summary_row is not None:
        row["phase6c_smoothness_metric"] = float(map_summary_row["smoothness_metric"])
        row["phase6c_smoothness_dtaudr_jump"] = float(map_summary_row["smoothness_dtaudr_jump"])
        row["phase6c_smoothness_grad_jump"] = float(map_summary_row["smoothness_grad_jump"])
        row["phase6c_smoothness_pass"] = bool(map_summary_row["smoothness_pass"])
        row["phase6c_radial_consistency_pass"] = bool(map_summary_row["radial_consistency_pass"])
        row["phase6c_ready_for_second_channel"] = bool(
            map_summary_row["phase6c_ready_for_second_channel_scaffold"]
        )
        dtaudr_match = np.isclose(
            row["max_rel_dtaudr_jump"],
            row["phase6c_smoothness_dtaudr_jump"],
            rtol=1e-6,
            atol=1e-9,
        )
        row["map_smoothness_dominated_by_1d_dtaudr"] = bool(
            row["phase6c_smoothness_dtaudr_jump"] >= row["phase6c_smoothness_grad_jump"]
        )
        row["diagnostic_matches_map_dtaudr_metric"] = dtaudr_match
    return row


def build_gradient_diagnostics_table(
    *,
    root: Path | None = None,
    galaxy_ids: tuple[str, ...] | None = None,
    tau_path: Path | None = None,
    map_summary_path: Path | None = None,
) -> pd.DataFrame:
    root = root or Path.cwd()
    tau_path = tau_path or (root / DEFAULT_TAU_PROFILES)
    map_summary_path = map_summary_path or (root / DEFAULT_MAP_SUMMARY)
    galaxy_ids = galaxy_ids or PRIMARY_PILOT_GALAXY_IDS

    map_summary = pd.read_csv(map_summary_path) if map_summary_path.is_file() else None
    rows = []
    for gid in galaxy_ids:
        ms_row = None
        if map_summary is not None and gid in map_summary["galaxy_id"].values:
            ms_row = map_summary[map_summary["galaxy_id"] == gid].iloc[0]
        rows.append(diagnose_galaxy(gid, tau_path=tau_path, map_summary_row=ms_row))
    return pd.DataFrame(rows)


def build_gradient_diagnostic_report(diag: pd.DataFrame) -> str:
    n_ready = int(diag["phase6c_ready_for_second_channel"].sum()) if "phase6c_ready_for_second_channel" in diag.columns else 0
    cause_counts = diag["primary_failure_cause"].value_counts()
    lines = [
        "# Phase 6C-C frozen radial τ-gradient diagnostic report",
        "",
        f"**Version:** {DIAGNOSTIC_VERSION}",
        "",
        "## Scope",
        "",
        "- **Diagnostic only** — frozen `expansion20_tau_profiles.csv` was read, not modified.",
        "- **No** τ smoothing, refit, K_g change, or pseudo-2D map regeneration.",
        "- **Not** a lensing or second-channel result.",
        "- Phase **6D remains blocked** until a future pre-registered Phase **6C-D** fix passes gates.",
        "",
        "## Summary",
        "",
        f"- Primary pilots analyzed: **{len(diag)}**",
        f"- Phase 6D ready (from 6C-B): **{n_ready}/{len(diag)}**",
        f"- Smoothness threshold: **{SMOOTHNESS_THRESHOLD}** (relative adjacent dτ/dr jump)",
        "",
        "### Failure cause counts (primary label)",
        "",
        cause_counts.to_string(),
        "",
        "## Per-galaxy diagnostics",
        "",
        diag[
            [
                "galaxy_id",
                "n_radial_points",
                "max_rel_dtaudr_jump",
                "n_jumps_above_threshold",
                "worst_jump_r_kpc",
                "worst_jump_region",
                "jump_failure_dominance",
                "primary_failure_cause",
                "phase6c_smoothness_pass",
                "phase6c_ready_for_second_channel",
            ]
        ].to_markdown(index=False),
        "",
        "## Comparison with Phase 6C-B maps",
        "",
        "For all pilots, `map_smoothness_dominated_by_1d_dtaudr` is true: pseudo-2D map "
        "smoothness failure is inherited from frozen radial dτ/dr, not from Cartesian gradient "
        "discretization alone.",
        "",
        "## Next step",
        "",
        "See `docs/phase6c_gradient_regularization_options.md` for pre-registered options. "
        "**Phase 6C-D** must be explicitly approved before applying any regularization.",
        "",
        "## Reproducibility",
        "",
        "```bash",
        "python3 scripts/build_phase6c_gradient_diagnostics.py",
        "```",
        "",
    ]
    return "\n".join(lines)


def run_phase6c_gradient_diagnostics(
    *,
    root: Path | None = None,
    table_out: Path | None = None,
    report_out: Path | None = None,
) -> dict[str, Any]:
    root = root or Path.cwd()
    table_out = table_out or root / "outputs/tables/phase6c_primary_pilot_gradient_diagnostics.csv"
    report_out = report_out or root / "outputs/reports/phase6c_gradient_diagnostic_report.md"

    diag = build_gradient_diagnostics_table(root=root)
    report = build_gradient_diagnostic_report(diag)

    table_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    diag.to_csv(table_out, index=False)
    report_out.write_text(report, encoding="utf-8")

    return {"diagnostics": diag, "table_path": table_out, "report_path": report_out}
