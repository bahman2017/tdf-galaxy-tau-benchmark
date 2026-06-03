"""Phase 6C-E: pre-registered R2+R6 regularized profiles and pseudo-2D maps."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.analysis.phase6c_frozen_pseudo2d import (
    DEFAULT_GRID_N,
    PRIMARY_PILOT_GALAXY_IDS,
    REQUIRED_NPZ_KEYS,
    _build_cartesian_grid,
    _gradient_fields,
    _grad_tau_max_adjacent_jump,
    _interpolate_tau_on_grid,
    _radial_dtaudr_jump,
    plot_pseudo2d_tau_map,
    radial_consistency_check,
)

IMPLEMENTATION_VERSION = "phase_6c_e_v1"
DEFAULT_CONFIG = Path("configs/phase6d_regularization_preregistration.yaml")
DEFAULT_TAU_PROFILES = Path("outputs/tables/expansion20_tau_profiles.csv")
DEFAULT_GRADIENT_DIAG = Path("outputs/tables/phase6c_primary_pilot_gradient_diagnostics.csv")
EPS_DENOM = 1e-12


@dataclass
class RegularizedMapResult:
    galaxy_id: str
    regularized_profile: pd.DataFrame
    correction_audit: pd.DataFrame
    arrays: dict[str, np.ndarray]
    metadata: dict[str, Any]
    consistency: pd.DataFrame
    report_md: str
    gates_pass: bool
    gate_failures: list[str]


def load_preregistration_config(path: Path | None = None) -> dict[str, Any]:
    path = path or DEFAULT_CONFIG
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _relative_jumps(dtaudr: np.ndarray) -> np.ndarray:
    if len(dtaudr) < 2:
        return np.array([])
    return np.abs(np.diff(dtaudr)) / np.maximum(np.abs(dtaudr[:-1]), EPS_DENOM)


def _cap_dtaudr_forward(
    dtaudr: np.ndarray,
    threshold: float,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Single forward sweep R2 cap; returns adjusted dtaudr and per-segment audit rows."""
    out = dtaudr.astype(float).copy()
    audits: list[dict[str, Any]] = []
    for i in range(len(out) - 1):
        d0, d1_before = out[i], out[i + 1]
        rel = abs(d1_before - d0) / max(abs(d0), EPS_DENOM)
        rel_after = rel
        corrected = False
        if rel > threshold:
            delta = np.sign(d1_before - d0) * threshold * max(abs(d0), EPS_DENOM)
            new_d1 = d0 + delta
            if d1_before != 0.0 and np.sign(new_d1) != np.sign(d1_before):
                new_d1 = np.sign(d1_before) * abs(new_d1)
            out[i + 1] = new_d1
            corrected = True
            rel_after = abs(out[i + 1] - d0) / max(abs(d0), EPS_DENOM)
        audits.append(
            {
                "segment_index": i,
                "step": "r2_cap" if corrected else "none",
                "dtaudr_before": float(d1_before),
                "dtaudr_after": float(out[i + 1]),
                "relative_jump_before": float(rel),
                "relative_jump_after": float(rel_after),
                "correction_applied": corrected,
                "abs_correction_dtaudr": float(abs(out[i + 1] - d1_before)) if corrected else 0.0,
            }
        )
    return out, audits


def _reintegrate_tau(r: np.ndarray, dtaudr: np.ndarray, tau0: float) -> np.ndarray:
    tau = np.zeros(len(r), dtype=float)
    tau[0] = tau0
    for i in range(1, len(r)):
        dr = r[i] - r[i - 1]
        tau[i] = tau[i - 1] + 0.5 * (dtaudr[i - 1] + dtaudr[i]) * dr
    return tau


def apply_r2_r6_regularization(
    frozen: pd.DataFrame,
    cfg: dict[str, Any],
    *,
    galaxy_id: str,
    worst_jump_region: str = "",
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Return regularized profile, correction audit, and R2/R6 status dict."""
    r2 = cfg["option_r2_global_jump_cap"]
    r6 = cfg["option_r6_boundary_trim"]
    thresh = float(r2["threshold_relative_jump"])
    max_cap_frac = float(r2["fail_if_fraction_segments_capped_exceeds"])
    tau_zero_tol = float(r6["inner_rule"]["tau_zero_tolerance"])

    frozen = frozen.sort_values("r_kpc").reset_index(drop=True)
    r = frozen["r_kpc"].astype(float).to_numpy()
    dtaudr_frozen = frozen["dtaudr_reconstructed"].astype(float).to_numpy()
    tau_frozen = frozen["tau_reconstructed"].astype(float).to_numpy()
    tau0 = float(tau_frozen[0])

    frozen_jumps = _relative_jumps(dtaudr_frozen)
    dtaudr_reg, seg_audits = _cap_dtaudr_forward(dtaudr_frozen, thresh)
    n_capped = sum(1 for a in seg_audits if a["correction_applied"])
    n_seg = max(len(dtaudr_reg) - 1, 1)
    frac_capped = n_capped / n_seg

    tau_reg = _reintegrate_tau(r, dtaudr_reg, tau0)

    reg = frozen.copy()
    reg["tau_frozen"] = tau_frozen
    reg["dtaudr_frozen"] = dtaudr_frozen
    reg["tau_reconstructed"] = tau_reg
    reg["dtaudr_reconstructed"] = dtaudr_reg
    reg["tau_regularized"] = tau_reg
    reg["dtaudr_regularized"] = dtaudr_reg

    audit_rows: list[dict[str, Any]] = []
    for i, row in enumerate(seg_audits):
        audit_rows.append(
            {
                "galaxy_id": galaxy_id,
                "r_kpc": float(0.5 * (r[i] + r[i + 1])),
                **row,
            }
        )

    r2_fail = frac_capped > max_cap_frac
    jumps_after_r2 = _relative_jumps(dtaudr_reg)

    trim_inner = False
    trim_outer = False
    if r6["enabled"]:
        if abs(tau_reg[0]) < tau_zero_tol or (
            r6["inner_rule"]["trigger_if_first_segment_jump_above_threshold"]
            and len(frozen_jumps) > 0
            and frozen_jumps[0] > thresh
        ):
            trim_inner = True
        last_jump = float(jumps_after_r2[-1]) if len(jumps_after_r2) else 0.0
        if last_jump > thresh or (
            worst_jump_region == "outer_third"
            and r6["outer_rule"]["trigger_if_last_segment_jump_above_threshold"]
            and last_jump > thresh
        ):
            trim_outer = True
        if not trim_outer and r6["outer_rule"]["trigger_if_last_segment_jump_above_threshold"]:
            if len(jumps_after_r2) > 0 and jumps_after_r2[-1] > thresh:
                trim_outer = True

    keep = np.ones(len(reg), dtype=bool)
    n_trim = 0
    if trim_inner and len(keep) > 0:
        audit_rows.append(
            {
                "galaxy_id": galaxy_id,
                "r_kpc": float(r[0]),
                "segment_index": -1,
                "step": "r6_inner_trim",
                "dtaudr_before": float(dtaudr_reg[0]),
                "dtaudr_after": np.nan,
                "relative_jump_before": float(frozen_jumps[0]) if len(frozen_jumps) else np.nan,
                "relative_jump_after": np.nan,
                "correction_applied": True,
                "abs_correction_dtaudr": np.nan,
            }
        )
        keep[0] = False
        n_trim += 1
    if trim_outer and keep.sum() > 0:
        last_i = len(keep) - 1
        audit_rows.append(
            {
                "galaxy_id": galaxy_id,
                "r_kpc": float(r[last_i]),
                "segment_index": last_i,
                "step": "r6_outer_trim",
                "dtaudr_before": float(dtaudr_reg[last_i]),
                "dtaudr_after": np.nan,
                "relative_jump_before": float(jumps_after_r2[-1]) if len(jumps_after_r2) else np.nan,
                "relative_jump_after": np.nan,
                "correction_applied": True,
                "abs_correction_dtaudr": np.nan,
            }
        )
        keep[last_i] = False
        n_trim += 1

    reg = reg.loc[keep].reset_index(drop=True)
    frac_trimmed = n_trim / len(frozen)
    n_remain = len(reg)
    r_cov = float(reg["r_kpc"].max() - reg["r_kpc"].min()) if n_remain >= 2 else 0.0

    r6_limits = r6["global_limits"]
    r6_fail = (
        frac_trimmed > float(r6_limits["fail_if_fraction_points_trimmed_exceeds"])
        or n_remain < int(r6_limits["min_remaining_radial_points"])
        or r_cov < float(r6_limits["min_remaining_radial_coverage_kpc"])
    )

    mean_dtaudr_drift = float(
        np.mean(
            np.abs(reg["dtaudr_regularized"] - reg["dtaudr_frozen"])
            / np.maximum(np.abs(reg["dtaudr_frozen"]), EPS_DENOM)
        )
    )

    status = {
        "n_segments_capped": n_capped,
        "fraction_segments_capped": frac_capped,
        "n_points_trimmed": n_trim,
        "fraction_points_trimmed": frac_trimmed,
        "n_remaining_points": n_remain,
        "remaining_radial_coverage_kpc": r_cov,
        "r2_fail": r2_fail,
        "r6_fail": r6_fail,
        "mean_fractional_dtaudr_drift_vs_frozen": mean_dtaudr_drift,
        "max_rel_jump_after_r2_r6": float(_relative_jumps(reg["dtaudr_reconstructed"].to_numpy()).max())
        if len(reg) > 1
        else 0.0,
        "trim_inner": trim_inner,
        "trim_outer": trim_outer,
    }

    audit = pd.DataFrame(audit_rows)
    return reg, audit, status


def _load_frozen_copy(tau_path: Path, galaxy_id: str) -> pd.DataFrame:
    tau = pd.read_csv(tau_path)
    sub = tau[tau["galaxy_id"] == galaxy_id].copy()
    if sub.empty:
        raise ValueError(f"No frozen profile for {galaxy_id}")
    return sub.sort_values("r_kpc").reset_index(drop=True)


def build_regularized_pseudo2d_map(
    galaxy_id: str,
    *,
    root: Path | None = None,
    config: dict[str, Any] | None = None,
    grid_n: int = DEFAULT_GRID_N,
) -> RegularizedMapResult:
    root = root or Path.cwd()
    cfg = config or load_preregistration_config(root / DEFAULT_CONFIG)
    tau_path = root / DEFAULT_TAU_PROFILES
    diag_path = root / DEFAULT_GRADIENT_DIAG

    frozen = _load_frozen_copy(tau_path, galaxy_id)
    worst_region = ""
    if diag_path.is_file():
        dg = pd.read_csv(diag_path)
        row = dg[dg["galaxy_id"] == galaxy_id]
        if not row.empty:
            worst_region = str(row.iloc[0]["worst_jump_region"])

    reg, audit, rstatus = apply_r2_r6_regularization(
        frozen, cfg, galaxy_id=galaxy_id, worst_jump_region=worst_region
    )

    k_g = float(cfg["scope"]["k_g_fixed"])
    profile = reg.rename(columns={"tau_reconstructed": "tau_reconstructed"})
    r_min = float(profile["r_kpc"].min())
    r_max = float(profile["r_kpc"].max())
    extrap_frac = float(
        cfg["option_r6_boundary_trim"]["map_embedding"]["extrapolation_beyond_r_max_fraction"]
    )
    r_outer = r_max * (1.0 + extrap_frac)

    x_kpc, y_kpc, _ = _build_cartesian_grid(r_min, r_max, n=grid_n, extrap_frac=extrap_frac)
    R_kpc = np.sqrt(x_kpc**2 + y_kpc**2)
    tau, valid_mask = _interpolate_tau_on_grid(profile, R_kpc, extrap_frac=extrap_frac)
    grads = _gradient_fields(tau, valid_mask, x_kpc, y_kpc, k_g)

    eps = float(cfg["radial_consistency_gate"]["max_relative_error"])
    consistency = radial_consistency_check(profile, R_kpc, tau, valid_mask, eps_rel=eps)

    r_prof = profile["r_kpc"].astype(float).to_numpy()
    tau_prof = profile["tau_reconstructed"].astype(float).to_numpy()
    tau_scale = max(float(np.nanmax(np.abs(tau_prof))), 1.0)
    grid_valid = valid_mask & np.isfinite(tau)
    tau_expected = np.interp(R_kpc[grid_valid].ravel(), r_prof, tau_prof)
    grid_rel = np.abs(tau[grid_valid] - tau_expected) / np.maximum(
        np.abs(tau_expected), tau_scale * eps
    )
    max_grid_rel = float(np.max(grid_rel)) if len(grid_rel) else 0.0
    max_rel_err = max(float(consistency["relative_error"].max(skipna=True)), max_grid_rel)
    radial_pass = bool(
        (consistency["passes_tolerance"]).all() and max_grid_rel <= eps
    )

    dtaudr_jump = _radial_dtaudr_jump(profile)
    grad_jump = _grad_tau_max_adjacent_jump(grads["grad_tau_mag"], valid_mask)
    smooth_thresh = float(cfg["smoothness_gate"]["threshold"])
    smoothness_metric = max(dtaudr_jump, grad_jump)
    smooth_pass = smoothness_metric <= smooth_thresh

    fid_max = float(cfg["fidelity_to_frozen_phase5"]["fail_if_mean_change_exceeds"])
    fid_pass = rstatus["mean_fractional_dtaudr_drift_vs_frozen"] <= fid_max

    gate_failures: list[str] = []
    if rstatus["r2_fail"]:
        gate_failures.append("r2_fraction_capped_exceeds_limit")
    if rstatus["r6_fail"]:
        gate_failures.append("r6_trim_or_coverage_fail")
    if not radial_pass:
        gate_failures.append("radial_consistency_fail")
    if not smooth_pass:
        gate_failures.append("smoothness_fail")
    if not fid_pass:
        gate_failures.append("fidelity_drift_fail")

    gates_pass = len(gate_failures) == 0
    phase6d_candidate = gates_pass

    metadata: dict[str, Any] = {
        "implementation_version": IMPLEMENTATION_VERSION,
        "protocol_version": cfg["protocol_version"],
        "galaxy_id": galaxy_id,
        "map_type": cfg["claim_boundaries"]["map_type_label"],
        "source_profile_frozen": str(DEFAULT_TAU_PROFILES),
        "source_profile_regularized": f"outputs/tables/phase6d_{galaxy_id}_regularized_profile.csv",
        "K_g": k_g,
        "tau_retuned": False,
        "kg_retuned": False,
        "separate_halo_added": False,
        "lensing_only_tau_fit": False,
        "lensing_confirmed": False,
        "true_2d_sigma_b": False,
        "grid_nx": grid_n,
        "grid_ny": grid_n,
        "r_min_kpc": r_min,
        "r_max_kpc": r_max,
        "r_outer_kpc": r_outer,
        "n_segments_capped": rstatus["n_segments_capped"],
        "fraction_segments_capped": rstatus["fraction_segments_capped"],
        "n_points_trimmed": rstatus["n_points_trimmed"],
        "fraction_points_trimmed": rstatus["fraction_points_trimmed"],
        "n_remaining_radial_points": rstatus["n_remaining_points"],
        "remaining_radial_coverage_kpc": rstatus["remaining_radial_coverage_kpc"],
        "mean_fractional_dtaudr_drift_vs_frozen": rstatus["mean_fractional_dtaudr_drift_vs_frozen"],
        "radial_consistency_max_relative_error": max_rel_err,
        "radial_consistency_pass": radial_pass,
        "smoothness_metric": smoothness_metric,
        "smoothness_dtaudr_jump": dtaudr_jump,
        "smoothness_grad_jump": grad_jump,
        "smoothness_pass": smooth_pass,
        "smoothness_threshold": smooth_thresh,
        "fidelity_pass": fid_pass,
        "r2_gate_pass": not rstatus["r2_fail"],
        "r6_gate_pass": not rstatus["r6_fail"],
        "phase6d_candidate": phase6d_candidate,
        "phase6d_gate_failures": ";".join(gate_failures) if gate_failures else "",
        "claim_phase5_unchanged": True,
        **{k: v for k, v in cfg["claim_boundaries"].items() if k.startswith("claim_")},
    }

    arrays = {
        "x_kpc": x_kpc,
        "y_kpc": y_kpc,
        "R_kpc": R_kpc,
        "tau": tau,
        "valid_mask": valid_mask.astype(bool),
        **grads,
        "K_g": np.array(k_g),
    }

    report_md = _build_galaxy_report(galaxy_id, metadata, gate_failures, cfg)
    return RegularizedMapResult(
        galaxy_id=galaxy_id,
        regularized_profile=reg,
        correction_audit=audit,
        arrays=arrays,
        metadata=metadata,
        consistency=consistency,
        report_md=report_md,
        gates_pass=gates_pass,
        gate_failures=gate_failures,
    )


def _build_galaxy_report(
    galaxy_id: str,
    meta: dict[str, Any],
    failures: list[str],
    cfg: dict[str, Any],
) -> str:
    return "\n".join(
        [
            f"# Phase 6C-E regularized pseudo-2D map — {galaxy_id}",
            "",
            "Axisymmetric pseudo-2D from **regularized** radial profile (R2+R6). "
            "**Not** lensing; **not** true 2D; **not** a second-channel success.",
            "",
            f"- phase6d_candidate: **{meta['phase6d_candidate']}**",
            f"- Gates failed: {', '.join(failures) if failures else 'none'}",
            f"- Segments capped: {meta['n_segments_capped']} ({meta['fraction_segments_capped']:.1%})",
            f"- Points trimmed: {meta['n_points_trimmed']}",
            f"- Smoothness: {meta['smoothness_metric']:.4f} (pass={meta['smoothness_pass']})",
            f"- Radial consistency max rel err: {meta['radial_consistency_max_relative_error']:.3e}",
            f"- Mean dτ/dr drift vs frozen: {meta['mean_fractional_dtaudr_drift_vs_frozen']:.3f}",
            "",
            "Phase 5 expansion_20 benchmark unchanged.",
            "",
        ]
    )


def write_regularized_outputs(
    result: RegularizedMapResult,
    *,
    root: Path | None = None,
    write_figure: bool = True,
) -> dict[str, Path]:
    root = root or Path.cwd()
    gid = result.galaxy_id
    paths = {
        "profile": root / f"outputs/tables/phase6d_{gid}_regularized_profile.csv",
        "audit": root / f"outputs/tables/phase6d_{gid}_correction_audit.csv",
        "metadata": root / f"outputs/tables/phase6d_{gid}_regularized_map_metadata.csv",
        "consistency": root / f"outputs/tables/phase6d_{gid}_regularized_radial_consistency_check.csv",
        "report": root / f"outputs/reports/phase6d_{gid}_regularized_map_report.md",
        "npz": root / f"outputs/maps/phase6d/{gid}_regularized_pseudo2d_tau_map.npz",
    }
    for p in paths.values():
        p.parent.mkdir(parents=True, exist_ok=True)

    result.regularized_profile.to_csv(paths["profile"], index=False)
    result.correction_audit.to_csv(paths["audit"], index=False)
    pd.DataFrame([result.metadata]).to_csv(paths["metadata"], index=False)
    result.consistency.to_csv(paths["consistency"], index=False)
    paths["report"].write_text(result.report_md, encoding="utf-8")
    np.savez_compressed(paths["npz"], **result.arrays)

    if write_figure:
        fig_path = root / f"outputs/figures/phase6d_{gid}_regularized_pseudo2d_tau_map.png"
        from tdf_galaxy_tau.analysis.phase6c_frozen_pseudo2d import FrozenPseudo2dResult

        pseudo = FrozenPseudo2dResult(
            galaxy_id=gid,
            arrays=result.arrays,
            metadata=result.metadata,
            consistency=result.consistency,
            report_md=result.report_md,
        )
        if plot_pseudo2d_tau_map(pseudo, fig_path):
            paths["figure"] = fig_path
    return paths


def build_cohort_summary(results: list[RegularizedMapResult]) -> pd.DataFrame:
    rows = [r.metadata for r in results]
    return pd.DataFrame(rows)


def build_cohort_report(summary: pd.DataFrame, cfg: dict[str, Any]) -> str:
    n_cand = int(summary["phase6d_candidate"].sum()) if "phase6d_candidate" in summary.columns else 0
    lines = [
        "# Phase 6C-E regularization cohort report",
        "",
        f"**Implementation:** {IMPLEMENTATION_VERSION}",
        "",
        "## Phase 6D gate",
        "",
    ]
    if n_cand >= 1:
        ids = summary.loc[summary["phase6d_candidate"], "galaxy_id"].astype(str).tolist()
        lines.append(f"**Phase 6D may proceed for:** {', '.join(ids)} ({n_cand}/5).")
    else:
        lines.append(
            "**Phase 6D remains blocked** — 0/5 pilots pass all hard gates. "
            "Negative cohort result for map-smoothness repair."
        )
    lines.extend(
        [
            "",
            "## Summary table",
            "",
            summary.to_markdown(index=False),
            "",
            "Not lensing; not true 2D; Phase 5 unchanged.",
            "",
        ]
    )
    return "\n".join(lines)


def run_phase6d_regularized_maps(
    *,
    root: Path | None = None,
    galaxy_ids: tuple[str, ...] | None = None,
    write_figures: bool = True,
) -> dict[str, Any]:
    root = root or Path.cwd()
    cfg = load_preregistration_config(root / DEFAULT_CONFIG)
    galaxy_ids = galaxy_ids or tuple(cfg["primary_pilot_galaxy_ids"])

    results: list[RegularizedMapResult] = []
    for gid in galaxy_ids:
        res = build_regularized_pseudo2d_map(gid, root=root, config=cfg)
        write_regularized_outputs(res, root=root, write_figure=write_figures)
        results.append(res)

    summary = build_cohort_summary(results)
    summary_path = root / "outputs/tables/phase6d_regularized_map_summary.csv"
    report_path = root / "outputs/reports/phase6d_regularization_cohort_report.md"
    summary.to_csv(summary_path, index=False)
    report_path.write_text(build_cohort_report(summary, cfg), encoding="utf-8")

    return {
        "results": results,
        "summary": summary,
        "summary_path": summary_path,
        "report_path": report_path,
    }
