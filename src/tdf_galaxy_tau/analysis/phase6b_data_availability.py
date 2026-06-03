"""Phase 6B: expansion_20 data availability audit and pilot ranking (read-only)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

AUDIT_VERSION = "phase_6b_v1"
COHORT = "expansion_20"
N_COHORT = 20

# Pre-registered Phase 6C thresholds (fixed in 6B; not tuned on map outcomes).
PHASE6C_N_MIN = 12
PHASE6C_RADIAL_COVERAGE_MIN_KPC = 5.0
PHASE6C_INCLINATION_MIN_DEG = 30.0
PHASE6C_INCLINATION_MAX_DEG = 90.0
PHASE6C_MAX_EXTRAPOLATION_FRAC = 0.05
PHASE6C_MAX_DTAUDR_JUMP_REL = 0.25
PHASE6C_TAU_RADIAL_MATCH_EPS_REL = 1.0e-6
# Conservative primary-pilot gate: stable tdf_3knot even/odd holdout (pre-registered in 6B).
PHASE6C_MAX_PRIMARY_HOLDOUT_RMSE_KMS = 10.0

DEFAULT_PATHS = {
    "subset_selection": Path("outputs/tables/expansion20_subset_selection.csv"),
    "failure_mode": Path("outputs/tables/expansion20_failure_mode_summary.csv"),
    "failure_diagnostics": Path("outputs/tables/expansion20_failure_diagnostics.csv"),
    "tau_profiles": Path("outputs/tables/expansion20_tau_profiles.csv"),
    "model_comparison": Path("outputs/tables/expansion20_model_comparison.csv"),
    "rotmod": Path("data/processed/sparc/sparc_rotmod_standardized.csv"),
    "photometry": Path("data/processed/sparc/sparc_photometry_metadata.csv"),
    "reconstruction_config": Path("configs/reconstruction.yaml"),
}

CLAIM_BOUNDARY_FIELDS = {
    "claim_no_dm_disproof": True,
    "claim_no_full_sparc_validation": True,
    "claim_no_lensing_confirmation": True,
    "claim_no_universal_tau_profile": True,
    "claim_no_true_2d_without_2d_data": True,
    "claim_phase6_separate_from_phase5_15_of_20": True,
}


@dataclass(frozen=True)
class Phase6bPaths:
    root: Path

    def p(self, key: str) -> Path:
        return self.root / DEFAULT_PATHS[key]


def _load_yaml_k_g(root: Path) -> float:
    import yaml

    cfg_path = root / DEFAULT_PATHS["reconstruction_config"]
    with cfg_path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    for key in ("k_g", "K_g", "k_tau", "K_tau"):
        if key in cfg:
            return float(cfg[key])
    radial = cfg.get("radial_tau_reconstruction") or {}
    for key in ("K_g", "k_g", "K_tau", "k_tau"):
        if key in radial:
            return float(radial[key])
    return 1.0


def _rotmod_galaxy_stats(rotmod: pd.DataFrame, galaxy_id: str) -> dict[str, Any]:
    g = rotmod[rotmod["galaxy_id"] == galaxy_id].copy()
    if g.empty:
        return {
            "n_radial_points": 0,
            "r_min_kpc": np.nan,
            "r_max_kpc": np.nan,
            "radial_coverage_kpc": np.nan,
            "v_obs_available": False,
            "v_err_available": False,
            "v_bar_available": False,
            "v_gas_available": False,
            "v_disk_available": False,
            "v_bulge_available": False,
            "missing_baryonic_component_flag": True,
            "sb_disk_profile_points": 0,
            "sb_bulge_profile_points": 0,
            "distance_rotmod_mpc": np.nan,
        }
    r = g["r_kpc"].astype(float)
    finite = lambda col: bool(g[col].notna().all() and np.isfinite(g[col]).all())
    has_gas = bool((g["v_gas_kms"].abs() > 0).any())
    has_disk = bool((g["v_disk_kms"].abs() > 0).any())
    has_bulge = bool((g["v_bulge_kms"].abs() > 0).any())
    missing_baryon = not (finite("v_gas_kms") and finite("v_disk_kms") and finite("v_bulge_kms"))
    sb_disk_pts = int(g["sb_disk_lpc2"].notna().sum()) if "sb_disk_lpc2" in g.columns else 0
    sb_bulge_pts = int(g["sb_bulge_lpc2"].notna().sum()) if "sb_bulge_lpc2" in g.columns else 0
    dist = g["distance_mpc"].dropna()
    return {
        "n_radial_points": len(g),
        "r_min_kpc": float(r.min()),
        "r_max_kpc": float(r.max()),
        "radial_coverage_kpc": float(r.max() - r.min()),
        "v_obs_available": finite("v_obs_kms"),
        "v_err_available": finite("v_err_kms"),
        "v_bar_available": finite("v_bar_kms"),
        "v_gas_available": has_gas,
        "v_disk_available": has_disk,
        "v_bulge_available": has_bulge,
        "missing_baryonic_component_flag": missing_baryon,
        "sb_disk_profile_points": sb_disk_pts,
        "sb_bulge_profile_points": sb_bulge_pts,
        "distance_rotmod_mpc": float(dist.iloc[0]) if len(dist) else np.nan,
    }


def _tau_profile_stats(tau: pd.DataFrame, galaxy_id: str) -> dict[str, Any]:
    g = tau[tau["galaxy_id"] == galaxy_id]
    if g.empty:
        return {
            "frozen_tau_profile_available": False,
            "frozen_dtaudr_available": False,
            "frozen_K_tau_value": np.nan,
            "n_tau_profile_points": 0,
            "max_abs_dtaudr": np.nan,
            "max_dtaudr_adjacent_jump": np.nan,
            "negative_residual_fraction": np.nan,
        }
    dtaudr = g["dtaudr_reconstructed"].astype(float)
    dtaudr_vals = dtaudr.to_numpy()
    jumps = np.abs(np.diff(dtaudr_vals)) if len(dtaudr_vals) > 1 else np.array([0.0])
    denom = np.maximum(np.abs(dtaudr_vals[:-1]), 1e-12)
    rel_jumps = jumps / denom
    neg_frac = float(g["negative_residual_flag"].astype(bool).mean())
    k_vals = g["K_tau"].dropna().unique()
    return {
        "frozen_tau_profile_available": bool(g["tau_reconstructed"].notna().any()),
        "frozen_dtaudr_available": bool(g["dtaudr_reconstructed"].notna().any()),
        "frozen_K_tau_value": float(k_vals[0]) if len(k_vals) else np.nan,
        "n_tau_profile_points": len(g),
        "max_abs_dtaudr": float(np.abs(dtaudr_vals).max()),
        "max_dtaudr_adjacent_jump": float(rel_jumps.max()) if len(rel_jumps) else np.nan,
        "negative_residual_fraction": neg_frac,
    }


def _photometry_row(photo: pd.DataFrame, galaxy_id: str) -> dict[str, Any]:
    g = photo[photo["galaxy_id"] == galaxy_id]
    if g.empty:
        return {
            "distance_photometry_mpc": np.nan,
            "inclination_deg": np.nan,
            "position_angle_available": False,
            "morphological_type": np.nan,
            "disk_scale_length_kpc": np.nan,
            "luminosity_3p6_lsun": np.nan,
            "photometry_metadata_available": False,
            "photometry_quality_flag": "",
        }
    row = g.iloc[0]
    return {
        "distance_photometry_mpc": float(row["distance_mpc"]),
        "inclination_deg": float(row["inclination_deg"]),
        "position_angle_available": False,
        "morphological_type": float(row["morphological_type"]),
        "disk_scale_length_kpc": float(row["disk_scale_length_kpc"]),
        "luminosity_3p6_lsun": float(row["luminosity_3p6_lsun"]),
        "photometry_metadata_available": True,
        "photometry_quality_flag": str(row.get("photometry_quality_flag", "")),
    }


def _map_type_flags(
    *,
    l1_ok: bool,
    l2_ok: bool,
    l3_ok: bool,
    l4_ok: bool,
    sb_profile: bool,
) -> dict[str, str]:
    axisym = "attemptable" if (l1_ok and l2_ok and l3_ok) else "not_attemptable"
    sky = "attemptable" if (axisym == "attemptable" and l4_ok) else "future_only"
    true_2d = "future_only"
    lensing = "future_only"
    return {
        "map_type_axisymmetric_pseudo_2d": axisym,
        "map_type_sky_projected": sky,
        "map_type_true_2d_sigma_b": true_2d,
        "map_type_deflection_lensing_proxy": lensing,
        "surface_brightness_1d_profile": "available" if sb_profile else "partial_or_missing",
        "true_2d_status": "future_only",
        "lensing_status": "future_only_not_confirmed",
    }


def _pilot_tier(
    *,
    galaxy_id: str,
    failure_mode: str,
    counts_primary: bool,
    primary_eligible: bool,
    l1_ok: bool,
    l4_ok: bool,
) -> str:
    if galaxy_id == "NGC7814" or failure_mode == "tdf_failure_mode":
        return "tier_3_avoid_defer"
    if galaxy_id == "UGC00128" or failure_mode == "mixed_result":
        return "tier_2_diagnostic"
    if failure_mode == "sensitivity_recovery":
        return "tier_2_diagnostic"
    if primary_eligible and counts_primary and l1_ok and l4_ok:
        return "tier_1_primary_candidate"
    if failure_mode == "robust_tdf_success" and not primary_eligible:
        return "tier_2_diagnostic"
    return "tier_3_avoid_defer"


def _rank_score(row: pd.Series, cohort: pd.DataFrame) -> float:
    if row["pilot_tier"] != "tier_1_primary_candidate":
        return np.nan
    elig = cohort[cohort["pilot_tier"] == "tier_1_primary_candidate"]
    if elig.empty:
        return np.nan

    def norm(col: str, invert: bool = False) -> float:
        vals = elig[col].astype(float)
        lo, hi = vals.min(), vals.max()
        if hi <= lo:
            v = 1.0
        else:
            v = (float(row[col]) - lo) / (hi - lo)
        if invert:
            v = 1.0 - v
        return v

    return (
        0.25 * norm("n_radial_points")
        + 0.15 * norm("radial_coverage_kpc")
        + 0.35 * norm("tdf_3knot_holdout_rmse_kms", invert=True)
        + 0.15 * norm("max_abs_dtaudr", invert=True)
        + 0.10 * (1.0 if row["geometry_complete_flag"] else 0.0)
    )


def build_phase6b_audit_table(root: Path | None = None) -> pd.DataFrame:
    root = root or Path.cwd()
    paths = Phase6bPaths(root)
    k_g_config = _load_yaml_k_g(root)

    subset = pd.read_csv(paths.p("subset_selection"))
    failure = pd.read_csv(paths.p("failure_mode"))
    tau = pd.read_csv(paths.p("tau_profiles"))
    models = pd.read_csv(paths.p("model_comparison"))
    rotmod = pd.read_csv(paths.p("rotmod"))
    photo = pd.read_csv(paths.p("photometry"))

    diag_path = paths.p("failure_diagnostics")
    diag = pd.read_csv(diag_path) if diag_path.is_file() else pd.DataFrame()

    galaxies = sorted(subset["galaxy_id"].astype(str).unique())
    if len(galaxies) != N_COHORT:
        raise ValueError(f"Expected {N_COHORT} expansion_20 galaxies, got {len(galaxies)}")

    tdf3 = models[models["model_name"] == "tdf_3knot"].set_index("galaxy_id")

    rows: list[dict[str, Any]] = []
    for gid in galaxies:
        fm = failure[failure["galaxy_id"] == gid].iloc[0]
        rot = _rotmod_galaxy_stats(rotmod, gid)
        tau_s = _tau_profile_stats(tau, gid)
        phot = _photometry_row(photo, gid)
        sel = subset[subset["galaxy_id"] == gid].iloc[0]

        has_tdf3 = gid in tdf3.index
        l1_ok = (
            rot["n_radial_points"] >= PHASE6C_N_MIN
            and rot["v_obs_available"]
            and rot["v_err_available"]
            and rot["radial_coverage_kpc"] >= PHASE6C_RADIAL_COVERAGE_MIN_KPC
        )
        l2_ok = rot["v_bar_available"] and not rot["missing_baryonic_component_flag"]
        l3_ok = (
            tau_s["frozen_tau_profile_available"]
            and tau_s["frozen_dtaudr_available"]
            and has_tdf3
        )
        inc = phot["inclination_deg"]
        dist_ok = np.isfinite(phot["distance_photometry_mpc"]) or np.isfinite(
            rot["distance_rotmod_mpc"]
        )
        inc_ok = (
            np.isfinite(inc)
            and PHASE6C_INCLINATION_MIN_DEG <= inc <= PHASE6C_INCLINATION_MAX_DEG
        )
        l4_ok = dist_ok and inc_ok and phot["photometry_metadata_available"]
        geometry_complete = l4_ok

        sb_profile = rot["sb_disk_profile_points"] > 0 or rot["sb_bulge_profile_points"] > 0
        maps = _map_type_flags(l1_ok=l1_ok, l2_ok=l2_ok, l3_ok=l3_ok, l4_ok=l4_ok, sb_profile=sb_profile)

        failure_mode = str(fm["failure_mode_classification"])
        counts_primary = bool(fm["counts_as_primary_success"])
        holdout_rmse = float(fm["tdf_3knot_holdout_rmse_kms"])
        holdout_stable = holdout_rmse <= PHASE6C_MAX_PRIMARY_HOLDOUT_RMSE_KMS
        primary_eligible = (
            failure_mode == "robust_tdf_success"
            and counts_primary
            and gid not in ("NGC7814", "UGC00128")
            and holdout_stable
        )

        tier = _pilot_tier(
            galaxy_id=gid,
            failure_mode=failure_mode,
            counts_primary=counts_primary,
            primary_eligible=primary_eligible,
            l1_ok=l1_ok,
            l4_ok=l4_ok,
        )

        dtaudr_jump_ok = (
            np.isfinite(tau_s["max_dtaudr_adjacent_jump"])
            and tau_s["max_dtaudr_adjacent_jump"] <= PHASE6C_MAX_DTAUDR_JUMP_REL
        )
        if not diag.empty:
            diag_row = diag[diag["galaxy_id"] == gid]
            if not diag_row.empty:
                tau_s["max_abs_dtaudr"] = float(diag_row.iloc[0]["max_abs_dtaudr"])

        row = {
            "audit_version": AUDIT_VERSION,
            "cohort": COHORT,
            "galaxy_id": gid,
            "cohort_role": str(fm["cohort_role"]),
            # L1
            "l1_rotation_available": l1_ok,
            "n_radial_points": rot["n_radial_points"],
            "r_min_kpc": rot["r_min_kpc"],
            "r_max_kpc": rot["r_max_kpc"],
            "radial_coverage_kpc": rot["radial_coverage_kpc"],
            "v_obs_available": rot["v_obs_available"],
            "v_err_available": rot["v_err_available"],
            # L2
            "l2_baryonic_available": l2_ok,
            "v_bar_available": rot["v_bar_available"],
            "v_gas_available": rot["v_gas_available"],
            "v_disk_available": rot["v_disk_available"],
            "v_bulge_available": rot["v_bulge_available"],
            "missing_baryonic_component_flag": rot["missing_baryonic_component_flag"],
            "baryonic_sufficient_for_scaffold": l2_ok,
            # L3
            "l3_frozen_tdf_available": l3_ok,
            "frozen_tdf_3knot_profile_exists": has_tdf3,
            "frozen_tau_profile_available": tau_s["frozen_tau_profile_available"],
            "frozen_dtaudr_available": tau_s["frozen_dtaudr_available"],
            "frozen_K_tau_value": tau_s["frozen_K_tau_value"],
            "K_g_config_value": k_g_config,
            "K_g_matches_frozen_K_tau": bool(
                np.isfinite(tau_s["frozen_K_tau_value"])
                and abs(tau_s["frozen_K_tau_value"] - k_g_config) < 1e-9
            ),
            "failure_mode_classification": failure_mode,
            "counts_as_primary_success_expansion20": counts_primary,
            "tdf_3knot_holdout_rmse_kms": holdout_rmse,
            "holdout_stable_for_primary_pilot": holdout_stable,
            "holdout_status": failure_mode,
            # L4
            "l4_geometry_available": l4_ok,
            "geometry_complete_flag": geometry_complete,
            "distance_mpc": phot["distance_photometry_mpc"]
            if np.isfinite(phot["distance_photometry_mpc"])
            else rot["distance_rotmod_mpc"],
            "inclination_deg": phot["inclination_deg"],
            "position_angle_available": phot["position_angle_available"],
            "morphological_type": phot["morphological_type"],
            "disk_scale_length_kpc": phot["disk_scale_length_kpc"],
            "luminosity_3p6_lsun": phot["luminosity_3p6_lsun"],
            "photometry_metadata_available": phot["photometry_metadata_available"],
            "axisymmetric_pseudo_2d_attemptable": maps["map_type_axisymmetric_pseudo_2d"]
            == "attemptable",
            # L5
            "l5_surface_brightness_metadata": sb_profile,
            "sb_disk_profile_points": rot["sb_disk_profile_points"],
            "sb_bulge_profile_points": rot["sb_bulge_profile_points"],
            "sparc_photometry_metadata_available": phot["photometry_metadata_available"],
            "true_2d_pixel_map_available": False,
            **maps,
            # L6
            "l6_second_channel_lensing_data": False,
            # smoothness / Phase 6C gates
            "max_abs_dtaudr": tau_s["max_abs_dtaudr"],
            "max_dtaudr_adjacent_jump_rel": tau_s["max_dtaudr_adjacent_jump"],
            "dtaudr_jump_within_threshold": dtaudr_jump_ok,
            "median_v_err_kms": float(sel["median_v_err_kms"]),
            "selection_rank_expansion20": float(sel["selection_rank"]),
            # pilot
            "primary_pilot_eligible": primary_eligible,
            "pilot_tier": tier,
            "is_primary_pilot": False,
            "pilot_rank_score": np.nan,
            # claim boundaries (conservative constants)
            **CLAIM_BOUNDARY_FIELDS,
            "notes": "",
        }
        rows.append(row)

    audit = pd.DataFrame(rows)
    audit["pilot_rank_score"] = audit.apply(lambda r: _rank_score(r, audit), axis=1)

    tier1 = audit[audit["pilot_tier"] == "tier_1_primary_candidate"].copy()
    tier1 = tier1.sort_values("pilot_rank_score", ascending=False, na_position="last")
    top_n = min(5, len(tier1))
    primary_ids = set(tier1.head(top_n)["galaxy_id"].astype(str))
    audit["is_primary_pilot"] = audit["galaxy_id"].isin(primary_ids) & (
        audit["pilot_tier"] == "tier_1_primary_candidate"
    )
    audit.loc[audit["is_primary_pilot"], "notes"] = "Phase 6B ranked primary pilot (top 5 tier-1)."

    return audit


def build_phase6b_ranking_table(audit: pd.DataFrame) -> pd.DataFrame:
    rank_rows: list[dict[str, Any]] = []
    order = {
        "tier_1_primary_candidate": 0,
        "tier_2_diagnostic": 1,
        "tier_3_avoid_defer": 2,
    }
    sorted_audit = audit.copy()
    sorted_audit["_tier_ord"] = sorted_audit["pilot_tier"].map(order)
    sorted_audit = sorted_audit.sort_values(
        ["_tier_ord", "pilot_rank_score"],
        ascending=[True, False],
        na_position="last",
    )
    for i, (_, row) in enumerate(sorted_audit.iterrows(), start=1):
        rank_rows.append(
            {
                "audit_version": AUDIT_VERSION,
                "overall_rank": i,
                "galaxy_id": row["galaxy_id"],
                "pilot_tier": row["pilot_tier"],
                "is_primary_pilot": bool(row["is_primary_pilot"]),
                "pilot_rank_score": row["pilot_rank_score"],
                "failure_mode_classification": row["failure_mode_classification"],
                "holdout_stable_for_primary_pilot": row["holdout_stable_for_primary_pilot"],
                "n_radial_points": row["n_radial_points"],
                "radial_coverage_kpc": row["radial_coverage_kpc"],
                "tdf_3knot_holdout_rmse_kms": row["tdf_3knot_holdout_rmse_kms"],
                "geometry_complete_flag": row["geometry_complete_flag"],
                "map_type_axisymmetric_pseudo_2d": row["map_type_axisymmetric_pseudo_2d"],
                "selection_rationale": row["notes"] or _default_rationale(row),
            }
        )
    return pd.DataFrame(rank_rows)


def _default_rationale(row: pd.Series) -> str:
    gid = row["galaxy_id"]
    tier = row["pilot_tier"]
    fm = row.get("failure_mode_classification", "")
    if tier == "tier_3_avoid_defer" and gid == "NGC7814":
        return "Excluded from primary pilot: canonical all-TDF failure."
    if tier == "tier_2_diagnostic" and gid == "UGC00128":
        return "Diagnostic only: mixed near-tie holdout; not primary expansion_20 success."
    if tier == "tier_2_diagnostic" and fm == "sensitivity_recovery":
        return "Diagnostic: tdf_5knot sensitivity-recovery; not primary expansion_20 success."
    if tier == "tier_2_diagnostic" and fm == "robust_tdf_success":
        return (
            "Diagnostic: robust expansion_20 success but holdout RMSE above "
            f"{PHASE6C_MAX_PRIMARY_HOLDOUT_RMSE_KMS} km/s primary-pilot gate."
        )
    if tier == "tier_2_diagnostic":
        return "Diagnostic tier: non-primary holdout or cohort guardrail."
    if tier == "tier_1_primary_candidate":
        return "Conservative primary candidate: robust tdf_3knot + complete L1–L4 + stable holdout."
    return "Deferred or lower priority for Phase 6C pilot."


def build_phase6b_report_markdown(audit: pd.DataFrame, ranking: pd.DataFrame) -> str:
    primary = ranking[ranking["is_primary_pilot"]]
    tier1_n = int((audit["pilot_tier"] == "tier_1_primary_candidate").sum())
    lines = [
        "# Phase 6B pilot selection report",
        "",
        f"**Audit version:** {AUDIT_VERSION}",
        f"**Cohort:** {COHORT} ({N_COHORT} galaxies)",
        "",
        "## Summary",
        "",
        f"- Tier-1 primary candidates: **{tier1_n}** galaxies",
        f"- Selected primary pilots (top 5 by score): **{', '.join(primary['galaxy_id'].astype(str).tolist()) or 'none'}**",
        "- Phase 5 expansion_20 headline (**15/20**) unchanged; Phase 6 is a separate test layer.",
        "",
        "## Pre-registered Phase 6C thresholds",
        "",
        f"| Parameter | Value |",
        f"| --- | --- |",
        f"| N_min radial points | {PHASE6C_N_MIN} |",
        f"| Min radial coverage (kpc) | {PHASE6C_RADIAL_COVERAGE_MIN_KPC} |",
        f"| Inclination range (deg) | [{PHASE6C_INCLINATION_MIN_DEG}, {PHASE6C_INCLINATION_MAX_DEG}] |",
        f"| Max extrapolation fraction beyond r_max | {PHASE6C_MAX_EXTRAPOLATION_FRAC} |",
        f"| Max relative adjacent dτ/dr jump | {PHASE6C_MAX_DTAUDR_JUMP_REL} |",
        f"| τ radial match tolerance (relative) | {PHASE6C_TAU_RADIAL_MATCH_EPS_REL} |",
        f"| Max tdf_3knot holdout RMSE for primary pilot | {PHASE6C_MAX_PRIMARY_HOLDOUT_RMSE_KMS} km/s |",
        "",
        "## Map types (repo v0.1.6)",
        "",
        "- **Axisymmetric pseudo-2D:** attemptable when L1–L3 satisfied",
        "- **Sky-projected:** attemptable when L4 geometry complete",
        "- **True 2D Σ_b:** future-only (no pixel maps in repo)",
        "- **Lensing/deflection:** future-only; not confirmed",
        "",
        "## Claim boundaries",
        "",
        "No dark-matter disproof; no full-SPARC validation; no lensing confirmation; "
        "no universal τ profile; pseudo-2D ≠ true 2D.",
        "",
        "## Reproducibility",
        "",
        "```bash",
        "python3 scripts/build_phase6b_data_availability_audit.py",
        "```",
        "",
        "## Primary pilot table",
        "",
        primary.to_markdown(index=False) if len(primary) else "_No primary pilots selected._",
        "",
    ]
    return "\n".join(lines)


def run_phase6b_audit(
    *,
    root: Path | None = None,
    audit_out: Path | None = None,
    ranking_out: Path | None = None,
    report_out: Path | None = None,
) -> dict[str, Any]:
    root = root or Path.cwd()
    audit_out = audit_out or root / "outputs/tables/phase6b_expansion20_data_availability_audit.csv"
    ranking_out = ranking_out or root / "outputs/tables/phase6b_pilot_candidate_ranking.csv"
    report_out = report_out or root / "outputs/reports/phase6b_pilot_selection_report.md"

    audit = build_phase6b_audit_table(root)
    ranking = build_phase6b_ranking_table(audit)
    report = build_phase6b_report_markdown(audit, ranking)

    audit_out.parent.mkdir(parents=True, exist_ok=True)
    ranking_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)

    audit.to_csv(audit_out, index=False)
    ranking.to_csv(ranking_out, index=False)
    report_out.write_text(report, encoding="utf-8")

    return {"audit": audit, "ranking": ranking, "report_path": report_out}
