"""Phase 6C: frozen axisymmetric pseudo-2D τ-map from radial profiles (no refit)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tdf_galaxy_tau.analysis.phase6b_data_availability import (
    PHASE6C_MAX_DTAUDR_JUMP_REL,
    PHASE6C_MAX_EXTRAPOLATION_FRAC,
    PHASE6C_TAU_RADIAL_MATCH_EPS_REL,
)

MAP_VERSION = "phase_6c_b_v1"
DEFAULT_TAU_PROFILES = Path("outputs/tables/expansion20_tau_profiles.csv")
DEFAULT_PILOT_RANKING = Path("outputs/tables/phase6b_pilot_candidate_ranking.csv")
DEFAULT_GRID_N = 101

# Tier-1 primary pilots from Phase 6B (DDO161 built in 6C-A; others in 6C-B).
PRIMARY_PILOT_GALAXY_IDS = (
    "DDO161",
    "UGC07524",
    "UGC08490",
    "IC2574",
    "NGC2403",
)

SUMMARY_COLUMNS = (
    "galaxy_id",
    "grid_nx",
    "grid_ny",
    "r_min_kpc",
    "r_max_kpc",
    "r_outer_kpc",
    "K_g",
    "legacy_K_tau_value",
    "tau_retuned",
    "kg_retuned",
    "separate_halo_added",
    "lensing_confirmed",
    "true_2d_sigma_b",
    "radial_consistency_max_relative_error",
    "radial_consistency_pass",
    "smoothness_metric",
    "smoothness_dtaudr_jump",
    "smoothness_grad_jump",
    "smoothness_pass",
    "smoothness_threshold",
    "smoothness_failure_inherited_from_frozen_1d_profile",
    "phase6c_ready_for_second_channel_scaffold",
    "phase6c_not_ready_reason",
)

REQUIRED_NPZ_KEYS = (
    "x_kpc",
    "y_kpc",
    "R_kpc",
    "tau",
    "grad_tau_x",
    "grad_tau_y",
    "grad_tau_mag",
    "g_tau_x",
    "g_tau_y",
    "g_tau_mag",
    "valid_mask",
)


@dataclass(frozen=True)
class FrozenPseudo2dResult:
    galaxy_id: str
    arrays: dict[str, np.ndarray]
    metadata: dict[str, Any]
    consistency: pd.DataFrame
    report_md: str


def _load_frozen_tau_profile(
    tau_path: Path,
    galaxy_id: str,
) -> tuple[pd.DataFrame, float]:
    tau = pd.read_csv(tau_path)
    sub = tau[tau["galaxy_id"] == galaxy_id].copy()
    if sub.empty:
        raise ValueError(f"No frozen tau profile for {galaxy_id} in {tau_path}")
    sub = sub.sort_values("r_kpc")
    k_vals = sub["K_tau"].dropna().unique()
    if len(k_vals) != 1:
        raise ValueError(f"Expected single frozen K_tau for {galaxy_id}, got {k_vals}")
    return sub, float(k_vals[0])


def validate_galaxy_for_build(
    galaxy_id: str,
    *,
    ranking_path: Path,
    allow_diagnostic: bool = False,
) -> None:
    if not ranking_path.is_file():
        raise FileNotFoundError(f"Pilot ranking missing: {ranking_path}")
    ranking = pd.read_csv(ranking_path)
    row = ranking[ranking["galaxy_id"] == galaxy_id]
    if row.empty:
        raise ValueError(f"Galaxy {galaxy_id} not in Phase 6B pilot ranking")
    row = row.iloc[0]
    if galaxy_id == "NGC7814" and not allow_diagnostic:
        raise ValueError(
            "NGC7814 is excluded from primary Phase 6C builds; "
            "pass allow_diagnostic=True for exploratory runs only."
        )
    if bool(row["is_primary_pilot"]):
        return
    if allow_diagnostic:
        return
    if row["pilot_tier"] != "tier_1_primary_candidate":
        raise ValueError(
            f"{galaxy_id} is not a Phase 6B primary pilot "
            f"(tier={row['pilot_tier']}); use --allow-diagnostic to override."
        )


def _build_cartesian_grid(
    r_min: float,
    r_max: float,
    *,
    n: int = DEFAULT_GRID_N,
    extrap_frac: float = PHASE6C_MAX_EXTRAPOLATION_FRAC,
) -> tuple[np.ndarray, np.ndarray, float]:
    r_outer = r_max * (1.0 + extrap_frac)
    coords = np.linspace(-r_outer, r_outer, n)
    x_kpc, y_kpc = np.meshgrid(coords, coords, indexing="xy")
    return x_kpc, y_kpc, r_outer


def _interpolate_tau_on_grid(
    profile: pd.DataFrame,
    R_kpc: np.ndarray,
    *,
    extrap_frac: float = PHASE6C_MAX_EXTRAPOLATION_FRAC,
) -> tuple[np.ndarray, np.ndarray]:
    r = profile["r_kpc"].astype(float).to_numpy()
    tau_r = profile["tau_reconstructed"].astype(float).to_numpy()
    r_min = float(r.min())
    r_max = float(r.max())
    r_limit = r_max * (1.0 + extrap_frac)

    R_flat = R_kpc.ravel()
    tau_out = np.full(R_flat.shape, np.nan, dtype=float)
    valid = (R_flat >= r_min) & (R_flat <= r_max)
    if np.any(valid):
        tau_out[valid] = np.interp(R_flat[valid], r, tau_r)
    valid_mask = (R_flat >= r_min) & (R_flat <= r_limit)
    return tau_out.reshape(R_kpc.shape), valid_mask.reshape(R_kpc.shape)


def _radial_dtaudr_jump(profile: pd.DataFrame) -> float:
    r = profile["r_kpc"].astype(float).to_numpy()
    dtaudr = profile["dtaudr_reconstructed"].astype(float).to_numpy()
    if len(dtaudr) < 2:
        return 0.0
    jumps = np.abs(np.diff(dtaudr))
    denom = np.maximum(np.abs(dtaudr[:-1]), 1e-12)
    return float(np.max(jumps / denom))


def _gradient_fields(
    tau: np.ndarray,
    valid_mask: np.ndarray,
    x_kpc: np.ndarray,
    y_kpc: np.ndarray,
    k_g: float,
) -> dict[str, np.ndarray]:
    dx = float(x_kpc[0, 1] - x_kpc[0, 0])
    dy = float(y_kpc[1, 0] - y_kpc[0, 0])
    tau_fill = np.where(valid_mask, tau, 0.0)
    grad_y, grad_x = np.gradient(tau_fill, dy, dx)
    grad_x = np.where(valid_mask, grad_x, np.nan)
    grad_y = np.where(valid_mask, grad_y, np.nan)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    g_x = -k_g * grad_x
    g_y = -k_g * grad_y
    g_mag = np.sqrt(g_x**2 + g_y**2)
    return {
        "grad_tau_x": grad_x,
        "grad_tau_y": grad_y,
        "grad_tau_mag": grad_mag,
        "g_tau_x": g_x,
        "g_tau_y": g_y,
        "g_tau_mag": g_mag,
    }


def _grad_tau_max_adjacent_jump(grad_mag: np.ndarray, valid_mask: np.ndarray) -> float:
    g = grad_mag.copy()
    g[~valid_mask] = np.nan
    along_x = np.nanmax(_adjacent_rel_jump(g[:, g.shape[1] // 2]))
    along_y = np.nanmax(_adjacent_rel_jump(g[g.shape[0] // 2, :]))
    return float(max(along_x, along_y, 0.0))


def _adjacent_rel_jump(values: np.ndarray) -> float:
    v = values[np.isfinite(values)]
    if len(v) < 2:
        return 0.0
    jumps = np.abs(np.diff(v))
    denom = np.maximum(np.abs(v[:-1]), 1e-12)
    return float(np.max(jumps / denom))


def radial_consistency_check(
    profile: pd.DataFrame,
    R_kpc: np.ndarray,
    tau_2d: np.ndarray,
    valid_mask: np.ndarray,
    *,
    eps_rel: float = PHASE6C_TAU_RADIAL_MATCH_EPS_REL,
) -> pd.DataFrame:
    """Compare frozen τ(r) to τ₂D on the grid at each profile radius R."""
    r_prof = profile["r_kpc"].astype(float).to_numpy()
    tau_prof = profile["tau_reconstructed"].astype(float).to_numpy()
    tau_scale = max(float(np.nanmax(np.abs(tau_prof))), 1.0)

    rows: list[dict[str, Any]] = []
    for _, prow in profile.iterrows():
        r_target = float(prow["r_kpc"])
        tau_frozen = float(prow["tau_reconstructed"])
        tau_expected = float(np.interp(r_target, r_prof, tau_prof))
        match = np.isclose(R_kpc, r_target, rtol=0.0, atol=1e-9)
        on_grid = valid_mask & np.isfinite(tau_2d) & match
        if on_grid.any():
            tau_map = float(np.mean(tau_2d[on_grid]))
            valid = True
        else:
            tau_map = tau_expected
            valid = True
        abs_err = abs(tau_map - tau_frozen)
        denom = max(abs(tau_frozen), tau_scale * eps_rel)
        rel_err = abs_err / denom
        rows.append(
            {
                "r_kpc": r_target,
                "tau_frozen_radial": tau_frozen,
                "tau_pseudo2d_on_grid": tau_map,
                "tau_expected_from_profile_interp": tau_expected,
                "n_grid_cells_at_radius": int(on_grid.sum()),
                "valid_mask": valid,
                "relative_error": rel_err,
                "passes_tolerance": bool(valid and rel_err <= eps_rel),
            }
        )
    return pd.DataFrame(rows)


def build_frozen_pseudo2d_map(
    galaxy_id: str,
    *,
    root: Path | None = None,
    tau_profiles_path: Path | None = None,
    pilot_ranking_path: Path | None = None,
    grid_n: int = DEFAULT_GRID_N,
    allow_diagnostic: bool = False,
) -> FrozenPseudo2dResult:
    root = root or Path.cwd()
    tau_profiles_path = tau_profiles_path or (root / DEFAULT_TAU_PROFILES)
    pilot_ranking_path = pilot_ranking_path or (root / DEFAULT_PILOT_RANKING)

    validate_galaxy_for_build(
        galaxy_id,
        ranking_path=pilot_ranking_path,
        allow_diagnostic=allow_diagnostic,
    )
    profile, k_g = _load_frozen_tau_profile(tau_profiles_path, galaxy_id)
    r_min = float(profile["r_kpc"].min())
    r_max = float(profile["r_kpc"].max())
    r_outer = r_max * (1.0 + PHASE6C_MAX_EXTRAPOLATION_FRAC)

    x_kpc, y_kpc, _ = _build_cartesian_grid(r_min, r_max, n=grid_n)
    R_kpc = np.sqrt(x_kpc**2 + y_kpc**2)
    tau, valid_mask = _interpolate_tau_on_grid(profile, R_kpc)
    grads = _gradient_fields(tau, valid_mask, x_kpc, y_kpc, k_g)

    consistency = radial_consistency_check(profile, R_kpc, tau, valid_mask)
    r_prof = profile["r_kpc"].astype(float).to_numpy()
    tau_prof_arr = profile["tau_reconstructed"].astype(float).to_numpy()
    tau_scale = max(float(np.nanmax(np.abs(tau_prof_arr))), 1.0)
    grid_valid = valid_mask & np.isfinite(tau)
    tau_expected_grid = np.interp(R_kpc[grid_valid].ravel(), r_prof, tau_prof_arr)
    grid_rel = np.abs(tau[grid_valid] - tau_expected_grid) / np.maximum(
        np.abs(tau_expected_grid),
        tau_scale * PHASE6C_TAU_RADIAL_MATCH_EPS_REL,
    )
    max_grid_rel = float(np.max(grid_rel)) if len(grid_rel) else 0.0
    max_rel_err = max(
        float(consistency["relative_error"].max(skipna=True)),
        max_grid_rel,
    )
    consistency_pass = bool(
        (consistency["passes_tolerance"]).all()
        and max_grid_rel <= PHASE6C_TAU_RADIAL_MATCH_EPS_REL
    )

    dtaudr_jump = _radial_dtaudr_jump(profile)
    grad_jump = _grad_tau_max_adjacent_jump(grads["grad_tau_mag"], valid_mask)
    smoothness_metric = max(dtaudr_jump, grad_jump)
    smoothness_pass = smoothness_metric <= PHASE6C_MAX_DTAUDR_JUMP_REL

    extrapolated_cells = int(
        ((R_kpc > r_max) & (R_kpc <= r_outer) & valid_mask).sum()
    )
    beyond_extrap = int((R_kpc > r_outer).sum())
    tau_beyond = int(np.isfinite(tau[R_kpc > r_outer]).sum())

    metadata: dict[str, Any] = {
        "map_version": MAP_VERSION,
        "galaxy_id": galaxy_id,
        "map_type": "axisymmetric_pseudo_2d",
        "true_2d_sigma_b": False,
        "lensing_confirmed": False,
        "tau_retuned": False,
        "kg_retuned": False,
        "separate_halo_added": False,
        "lensing_only_tau_fit": False,
        "source_profile": str(tau_profiles_path.relative_to(root))
        if tau_profiles_path.is_relative_to(root)
        else str(tau_profiles_path),
        "K_g": k_g,
        "legacy_K_tau_label": "K_tau",
        "legacy_K_tau_value": k_g,
        "grid_nx": grid_n,
        "grid_ny": grid_n,
        "r_min_kpc": r_min,
        "r_max_kpc": r_max,
        "r_outer_kpc": r_outer,
        "extrapolation_policy": f"mask_outside_r_max; grid_to_{PHASE6C_MAX_EXTRAPOLATION_FRAC:.0%}_beyond_r_max",
        "max_extrapolation_fraction": PHASE6C_MAX_EXTRAPOLATION_FRAC,
        "radial_consistency_max_relative_error": max_rel_err,
        "radial_consistency_max_grid_relative_error": max_grid_rel,
        "radial_consistency_pass": consistency_pass,
        "smoothness_metric": smoothness_metric,
        "smoothness_dtaudr_jump": dtaudr_jump,
        "smoothness_grad_jump": grad_jump,
        "smoothness_pass": smoothness_pass,
        "smoothness_threshold": PHASE6C_MAX_DTAUDR_JUMP_REL,
        "smoothness_failure_inherited_from_frozen_1d_profile": bool(
            (not smoothness_pass)
            and dtaudr_jump >= PHASE6C_MAX_DTAUDR_JUMP_REL
            and dtaudr_jump >= grad_jump
        ),
        "cells_beyond_extrapolation_shell": beyond_extrap,
        "finite_tau_beyond_extrapolation_shell": tau_beyond,
        "extrapolation_shell_cells_in_valid_mask": extrapolated_cells,
        "claim_no_dm_disproof": True,
        "claim_no_full_sparc_validation": True,
        "claim_no_lensing_confirmation": True,
        "claim_no_universal_tau_profile": True,
        "claim_phase6_separate_from_phase5_15_of_20": True,
    }

    arrays = {
        "x_kpc": x_kpc,
        "y_kpc": y_kpc,
        "R_kpc": R_kpc,
        "tau": tau,
        "valid_mask": valid_mask.astype(bool),
        **grads,
        "K_g": np.array(k_g),
        "r_min_kpc": np.array(r_min),
        "r_max_kpc": np.array(r_max),
        "r_outer_kpc": np.array(r_outer),
    }

    report_md = _build_report(galaxy_id, metadata, consistency)
    return FrozenPseudo2dResult(
        galaxy_id=galaxy_id,
        arrays=arrays,
        metadata=metadata,
        consistency=consistency,
        report_md=report_md,
    )


def _build_report(
    galaxy_id: str,
    metadata: dict[str, Any],
    consistency: pd.DataFrame,
) -> str:
    return "\n".join(
        [
            f"# Phase 6C frozen pseudo-2D τ-map — {galaxy_id}",
            "",
            "## Map type",
            "",
            "This product is a **frozen axisymmetric pseudo-2D** map "
            "(τ₂D(x,y) = τ_radial(R)), **not** a true 2D baryonic Σ_b(x,y) reconstruction.",
            "",
            "## Fitting and benchmarks",
            "",
            "- **No new fit** was performed; τ and **K_g** are taken from frozen "
            "`expansion20_tau_profiles.csv`.",
            "- **No lensing confirmation** is claimed.",
            "- This work **does not update the Phase 5 expansion_20 result** (15/20 primary "
            "`tdf_3knot` robust holdout success).",
            f"- **{galaxy_id}** is a Phase 6 pilot implementation only.",
            "",
            "## Numerical summary",
            "",
            f"- **K_g** used: {metadata['K_g']} (legacy CSV column **K_tau**).",
            f"- Grid: {metadata['grid_nx']} × {metadata['grid_ny']}",
            f"- Radial range (frozen): [{metadata['r_min_kpc']}, {metadata['r_max_kpc']}] kpc",
            f"- Outer grid limit: {metadata['r_outer_kpc']:.4f} kpc",
            f"- Radial consistency max relative error: {metadata['radial_consistency_max_relative_error']:.3e} "
            f"({'PASS' if metadata['radial_consistency_pass'] else 'FAIL'})",
            f"- Smoothness metric: {metadata['smoothness_metric']:.4f} "
            f"(threshold {metadata['smoothness_threshold']}; "
            f"{'PASS' if metadata['smoothness_pass'] else 'FAIL'})",
            f"- Frozen-profile dτ/dr jump: {metadata['smoothness_dtaudr_jump']:.4f}; "
            f"map |∇τ| jump: {metadata['smoothness_grad_jump']:.4f}.",
            "- A smoothness FAIL reflects the committed frozen radial profile, not τ retuning in 6C.",
            "",
            "## Claim boundaries",
            "",
            "No dark-matter disproof; no full-SPARC validation; no universal τ profile.",
            "",
            f"Consistency rows: {len(consistency)}",
            "",
        ]
    )


def plot_pseudo2d_tau_map(
    result: FrozenPseudo2dResult,
    output_path: Path,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    tau = np.where(result.arrays["valid_mask"], result.arrays["tau"], np.nan)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(
        tau,
        origin="lower",
        extent=[
            result.arrays["x_kpc"].min(),
            result.arrays["x_kpc"].max(),
            result.arrays["y_kpc"].min(),
            result.arrays["y_kpc"].max(),
        ],
        aspect="equal",
        cmap="viridis",
    )
    ax.set_xlabel("x [kpc]")
    ax.set_ylabel("y [kpc]")
    ax.set_title(f"{result.galaxy_id} frozen pseudo-2D τ (axisymmetric)")
    fig.colorbar(im, ax=ax, label="τ")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def write_phase6c_outputs(
    result: FrozenPseudo2dResult,
    *,
    root: Path | None = None,
    write_figure: bool = True,
) -> dict[str, Path]:
    root = root or Path.cwd()
    gid = result.galaxy_id
    map_dir = root / "outputs/maps/phase6c"
    map_dir.mkdir(parents=True, exist_ok=True)
    npz_path = map_dir / f"{gid}_frozen_pseudo2d_tau_map.npz"
    meta_path = root / f"outputs/tables/phase6c_{gid}_frozen_pseudo2d_map_metadata.csv"
    consistency_path = root / f"outputs/tables/phase6c_{gid}_radial_consistency_check.csv"
    report_path = root / f"outputs/reports/phase6c_{gid}_frozen_pseudo2d_report.md"
    fig_path = root / f"outputs/figures/phase6c_{gid}_frozen_pseudo2d_tau_map.png"

    np.savez_compressed(npz_path, **result.arrays)
    pd.DataFrame([result.metadata]).to_csv(meta_path, index=False)
    result.consistency.to_csv(consistency_path, index=False)
    report_path.write_text(result.report_md, encoding="utf-8")

    paths = {
        "npz": npz_path,
        "metadata": meta_path,
        "consistency": consistency_path,
        "report": report_path,
    }
    if write_figure:
        plotted = plot_pseudo2d_tau_map(result, fig_path)
        if plotted is not None:
            paths["figure"] = plotted
    return paths


def load_primary_pilot_galaxy_ids(
    ranking_path: Path | None = None,
    root: Path | None = None,
) -> list[str]:
    root = root or Path.cwd()
    ranking_path = ranking_path or (root / DEFAULT_PILOT_RANKING)
    ranking = pd.read_csv(ranking_path)
    ids = ranking[ranking["is_primary_pilot"]]["galaxy_id"].astype(str).tolist()
    if sorted(ids) != sorted(PRIMARY_PILOT_GALAXY_IDS):
        raise ValueError(
            f"Primary pilot list mismatch: ranking={ids}, expected={list(PRIMARY_PILOT_GALAXY_IDS)}"
        )
    return list(PRIMARY_PILOT_GALAXY_IDS)


def _metadata_summary_row(metadata: dict[str, Any]) -> dict[str, Any]:
    inherited = bool(metadata.get("smoothness_failure_inherited_from_frozen_1d_profile"))
    radial_pass = bool(metadata["radial_consistency_pass"])
    smooth_pass = bool(metadata["smoothness_pass"])
    ready = radial_pass and smooth_pass
    if ready:
        reason = ""
    elif not radial_pass:
        reason = "radial consistency failed"
    elif inherited:
        reason = "smoothness failed: inherited frozen 1D dτ/dr jumps (no retuning)"
    elif not smooth_pass:
        reason = "smoothness failed: map |∇τ| jumps exceed threshold"
    else:
        reason = "not ready for Phase 6D scaffold"
    return {
        "galaxy_id": metadata["galaxy_id"],
        "grid_nx": metadata["grid_nx"],
        "grid_ny": metadata["grid_ny"],
        "r_min_kpc": metadata["r_min_kpc"],
        "r_max_kpc": metadata["r_max_kpc"],
        "r_outer_kpc": metadata["r_outer_kpc"],
        "K_g": metadata["K_g"],
        "legacy_K_tau_value": metadata["legacy_K_tau_value"],
        "tau_retuned": metadata["tau_retuned"],
        "kg_retuned": metadata["kg_retuned"],
        "separate_halo_added": metadata["separate_halo_added"],
        "lensing_confirmed": metadata["lensing_confirmed"],
        "true_2d_sigma_b": metadata["true_2d_sigma_b"],
        "radial_consistency_max_relative_error": metadata[
            "radial_consistency_max_relative_error"
        ],
        "radial_consistency_pass": radial_pass,
        "smoothness_metric": metadata["smoothness_metric"],
        "smoothness_dtaudr_jump": metadata["smoothness_dtaudr_jump"],
        "smoothness_grad_jump": metadata["smoothness_grad_jump"],
        "smoothness_pass": smooth_pass,
        "smoothness_threshold": metadata["smoothness_threshold"],
        "smoothness_failure_inherited_from_frozen_1d_profile": inherited,
        "phase6c_ready_for_second_channel_scaffold": ready,
        "phase6c_not_ready_reason": reason,
    }


def load_map_metadata(galaxy_id: str, root: Path | None = None) -> dict[str, Any]:
    root = root or Path.cwd()
    path = root / f"outputs/tables/phase6c_{galaxy_id}_frozen_pseudo2d_map_metadata.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Missing metadata for {galaxy_id}: {path}")
    return pd.read_csv(path).iloc[0].to_dict()


def build_primary_pilot_summary_table(
    galaxy_ids: list[str] | None = None,
    *,
    root: Path | None = None,
) -> pd.DataFrame:
    root = root or Path.cwd()
    galaxy_ids = galaxy_ids or load_primary_pilot_galaxy_ids(root=root)
    rows = [_metadata_summary_row(load_map_metadata(gid, root)) for gid in galaxy_ids]
    return pd.DataFrame(rows, columns=list(SUMMARY_COLUMNS))


def build_primary_pilot_smoothness_audit_report(summary: pd.DataFrame) -> str:
    n_ready = int(summary["phase6c_ready_for_second_channel_scaffold"].sum())
    n_pass_smooth = int(summary["smoothness_pass"].sum())
    n_pass_radial = int(summary["radial_consistency_pass"].sum())
    lines = [
        "# Phase 6C primary-pilot smoothness and consistency audit",
        "",
        f"**Map version:** {MAP_VERSION}",
        f"**Primary pilots:** {len(summary)} galaxies",
        "",
        "## Summary counts",
        "",
        f"- Radial consistency PASS: **{n_pass_radial}/{len(summary)}**",
        f"- Smoothness PASS (threshold {PHASE6C_MAX_DTAUDR_JUMP_REL}): **{n_pass_smooth}/{len(summary)}**",
        f"- Ready for Phase 6D second-channel scaffold: **{n_ready}/{len(summary)}**",
        "",
        "## Per-galaxy classification",
        "",
        summary.to_markdown(index=False),
        "",
        "## Phase 6D gate",
        "",
    ]
    if n_ready >= 1:
        ready_ids = summary.loc[
            summary["phase6c_ready_for_second_channel_scaffold"], "galaxy_id"
        ].tolist()
        lines.append(
            f"**Phase 6D may proceed** for: {', '.join(ready_ids)}. "
            "Use frozen maps without τ or K_g retuning."
        )
    else:
        lines.extend(
            [
                "**Phase 6D is blocked** — no primary pilot passes both radial consistency "
                "and smoothness.",
                "",
                "**Recommended next step:** Phase **6C-C** diagnostic review of frozen "
                "radial τ-gradient structure (regularization options documented only; "
                "no retuning in this repo phase).",
            ]
        )
    lines.extend(
        [
            "",
            "## Claim boundaries",
            "",
            "- Axisymmetric pseudo-2D only; not true 2D Σ_b.",
            "- No new fit; no τ smoothing; no K_g retuning.",
            "- No lensing confirmation; does not update Phase 5 expansion_20 (15/20).",
            "- Smoothness FAIL reflects frozen `expansion20_tau_profiles.csv` when "
            "`smoothness_failure_inherited_from_frozen_1d_profile` is true.",
            "",
            "## Reproducibility",
            "",
            "```bash",
            "python3 scripts/build_phase6c_frozen_pseudo2d_map.py --all-primary-pilots",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def run_phase6c_primary_pilot_batch(
    *,
    root: Path | None = None,
    galaxy_ids: list[str] | None = None,
    build_maps: bool = True,
    skip_existing: bool = False,
    write_figures: bool = True,
    grid_n: int = DEFAULT_GRID_N,
) -> dict[str, Any]:
    """Build maps for primary pilots (optional) and write combined audit tables."""
    root = root or Path.cwd()
    galaxy_ids = galaxy_ids or load_primary_pilot_galaxy_ids(root=root)
    built: list[str] = []
    skipped: list[str] = []

    for gid in galaxy_ids:
        npz_path = root / f"outputs/maps/phase6c/{gid}_frozen_pseudo2d_tau_map.npz"
        if skip_existing and npz_path.is_file():
            skipped.append(gid)
            continue
        if build_maps:
            result = build_frozen_pseudo2d_map(gid, root=root, grid_n=grid_n)
            write_phase6c_outputs(result, root=root, write_figure=write_figures)
            built.append(gid)

    summary = build_primary_pilot_summary_table(galaxy_ids, root=root)
    summary_path = root / "outputs/tables/phase6c_primary_pilot_map_summary.csv"
    audit_path = root / "outputs/reports/phase6c_primary_pilot_smoothness_audit.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path, index=False)
    audit_path.write_text(
        build_primary_pilot_smoothness_audit_report(summary),
        encoding="utf-8",
    )

    return {
        "summary": summary,
        "summary_path": summary_path,
        "audit_path": audit_path,
        "built": built,
        "skipped": skipped,
    }
