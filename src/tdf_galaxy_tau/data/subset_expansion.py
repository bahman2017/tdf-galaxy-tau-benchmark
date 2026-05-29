from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.data.sparc_metadata_join import _bulge_dominated_proxy

PROTOCOL_DISCLAIMER = (
    "This phase pre-registers expansion criteria only. It does not run new fits, "
    "does not validate TDF on full SPARC, does not disprove dark matter, "
    "and does not include lensing."
)


@dataclass(frozen=True)
class SubsetExpansionConfig:
    raw: dict[str, Any]

    @property
    def original_ids(self) -> list[str]:
        return list(self.raw.get("original_subset_galaxy_ids", []))

    @property
    def min_radial_points(self) -> int:
        return int(self.raw.get("selection_criteria", {}).get("min_radial_points", 12))

    @property
    def min_radial_coverage_kpc(self) -> float:
        return float(self.raw.get("selection_criteria", {}).get("min_radial_coverage_kpc", 5.0))

    @property
    def max_median_v_err_kms(self) -> float:
        return float(self.raw.get("selection_criteria", {}).get("max_median_v_err_kms", 20.0))


def load_subset_expansion_config(path: Path | str = "configs/subset_expansion.yaml") -> SubsetExpansionConfig:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return SubsetExpansionConfig(raw=data)


def _morphology_class(morph: float, bulge_proxy: bool, cfg: SubsetExpansionConfig) -> str:
    div = cfg.raw.get("morphology_diversity", {})
    disk_min = float(div.get("disk_dominated_type_min", 7.0))
    early_max = float(div.get("early_type_max", 2.0))
    if bulge_proxy or (np.isfinite(morph) and morph <= early_max):
        return "early_bulge"
    if np.isfinite(morph) and morph >= disk_min:
        return "disk_dominated"
    return "intermediate"


def _evaluate_galaxy_qc(
    gid: str,
    group: pd.DataFrame,
    *,
    cfg: SubsetExpansionConfig,
) -> dict[str, Any]:
    crit = cfg.raw.get("selection_criteria", {})
    finite_cols = list(crit.get("require_finite_rotmod_columns", []))
    pos_cols = list(crit.get("require_positive_columns", []))

    if finite_cols:
        finite_mask = np.isfinite(group[finite_cols]).all(axis=1)
        all_finite = bool(finite_mask.all())
    else:
        all_finite = True

    n_points = int(len(group))
    r_min = float(group["r_kpc"].min())
    r_max = float(group["r_kpc"].max())
    coverage = r_max - r_min
    v_min = float(group["v_obs_kms"].min())
    v_max = float(group["v_obs_kms"].max())
    median_v_err = float(group["v_err_kms"].median())
    has_bulge = bool((group["v_bulge_kms"].abs() > 5.0).any())

    reasons: list[str] = []
    if n_points < cfg.min_radial_points:
        reasons.append(f"n_points<{cfg.min_radial_points}")
    if coverage <= cfg.min_radial_coverage_kpc:
        reasons.append(f"radial_coverage<={cfg.min_radial_coverage_kpc}")
    if not all_finite:
        reasons.append("non_finite_required_values")
    for col in pos_cols:
        if col in group.columns and (group[col] <= 0).any():
            reasons.append(f"non_positive_{col}")
    if median_v_err > cfg.max_median_v_err_kms:
        reasons.append(f"median_v_err>{cfg.max_median_v_err_kms}")

    return {
        "galaxy_id": gid,
        "n_points": n_points,
        "radial_coverage_kpc": coverage,
        "v_obs_range": f"{v_min:.1f}-{v_max:.1f}",
        "median_v_err_kms": median_v_err,
        "bulge_proxy": has_bulge,
        "eligible": len(reasons) == 0,
        "rejection_reason": "" if not reasons else ";".join(reasons),
    }


def _photometry_ok(row: pd.Series, cfg: SubsetExpansionConfig) -> tuple[bool, float, str]:
    crit = cfg.raw.get("selection_criteria", {})
    fields = list(crit.get("require_photometry_fields", []))
    allowed_flags = set(crit.get("photometry_quality_flags_allowed", []))
    missing = [f for f in fields if f not in row.index or not np.isfinite(row.get(f, np.nan))]
    flag = str(row.get("photometry_quality_flag", ""))
    flag_ok = not allowed_flags or flag in allowed_flags
    complete = len(missing) == 0 and flag_ok
    frac = 1.0 - len(missing) / max(len(fields), 1)
    reason = ""
    if missing:
        reason = f"missing_photometry:{','.join(missing)}"
    elif not flag_ok:
        reason = f"photometry_flag_not_allowed:{flag}"
    return complete, frac, reason


def _selection_score(row: pd.Series, cfg: SubsetExpansionConfig) -> float:
    w = cfg.raw.get("scoring", {}).get("weights", {})
    w_n = float(w.get("n_points", 0.3))
    w_cov = float(w.get("radial_coverage_kpc", 0.25))
    w_photo = float(w.get("photometry_completeness", 0.2))
    w_err = float(w.get("inverse_median_v_err", 0.15))
    w_npc = float(w.get("n_points_per_coverage", 0.1))

    n_norm = min(float(row["n_points"]) / 80.0, 1.0)
    cov_norm = min(float(row["radial_coverage_kpc"]) / 50.0, 1.0)
    photo = float(row.get("photometry_completeness", 0.0))
    err = float(row["median_v_err_kms"])
    err_norm = 1.0 / (1.0 + err / 5.0) if err > 0 else 0.0
    npc = n_norm * cov_norm if cov_norm > 0 else 0.0

    return w_n * n_norm + w_cov * cov_norm + w_photo * photo + w_err * err_norm + w_npc * npc


def build_expansion_candidates(
    rotmod: pd.DataFrame,
    photometry: pd.DataFrame,
    *,
    cfg: SubsetExpansionConfig,
    original_ids: list[str] | None = None,
) -> pd.DataFrame:
    original = set(original_ids or cfg.original_ids)
    photo_by = photometry.set_index("galaxy_id")

    rows: list[dict[str, Any]] = []
    for gid, group in rotmod.groupby("galaxy_id", sort=True):
        if gid in original:
            continue
        qc = _evaluate_galaxy_qc(gid, group, cfg=cfg)
        photo_row = photo_by.loc[gid] if gid in photo_by.index else pd.Series(dtype=float)
        photo_ok, photo_frac, photo_reason = _photometry_ok(photo_row, cfg)

        eligible = qc["eligible"] and photo_ok
        morph = float(photo_row.get("morphological_type", np.nan)) if len(photo_row) else float("nan")
        bulge_proxy = bool(qc["bulge_proxy"])
        if len(photo_row):
            proxy_row = pd.Series(
                {
                    "morphological_type": morph,
                    "rotmod_has_bulge_proxy": bulge_proxy,
                }
            )
            bulge_proxy = bulge_proxy or bool(_bulge_dominated_proxy(proxy_row))

        morph_class = _morphology_class(morph, bulge_proxy, cfg)
        rejection = qc["rejection_reason"]
        if not photo_ok and photo_reason:
            rejection = f"{rejection};{photo_reason}" if rejection else photo_reason

        row = {
            **qc,
            "morphology_type": morph,
            "inclination_deg": photo_row.get("inclination_deg", np.nan) if len(photo_row) else np.nan,
            "luminosity_3p6_lsun": photo_row.get("luminosity_3p6_lsun", np.nan) if len(photo_row) else np.nan,
            "disk_scale_length_kpc": photo_row.get("disk_scale_length_kpc", np.nan) if len(photo_row) else np.nan,
            "bulge_proxy": bulge_proxy,
            "morphology_class": morph_class,
            "photometry_completeness": photo_frac if photo_ok else 0.0,
            "eligible_for_expansion": eligible,
        }
        row["selection_score"] = _selection_score(pd.Series(row), cfg) if eligible else 0.0
        row["selected_for_expansion_12"] = False
        row["selected_for_expansion_20"] = False
        row["selection_reason"] = ""
        row["caveat"] = (
            "QC/photometry-based score only; not selected using TDF holdout outcomes."
            if eligible
            else f"Not eligible: {rejection}"
        )
        rows.append(row)

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["selection_score", "galaxy_id"], ascending=[False, True]).reset_index(drop=True)
    return out


def _pick_stratified(
    pool: pd.DataFrame,
    n: int,
    quotas: dict[str, int],
) -> list[str]:
    picked: list[str] = []
    for morph_class, quota in quotas.items():
        sub = pool[
            (pool["morphology_class"] == morph_class) & (~pool["galaxy_id"].isin(picked))
        ].sort_values(["selection_score", "galaxy_id"], ascending=[False, True])
        take = sub.head(int(quota))
        picked.extend(take["galaxy_id"].tolist())

    if len(picked) < n:
        rest = pool[~pool["galaxy_id"].isin(picked)].sort_values(
            ["selection_score", "galaxy_id"], ascending=[False, True]
        )
        need = n - len(picked)
        picked.extend(rest.head(need)["galaxy_id"].tolist())
    return picked[:n]


def apply_expansion_selections(
    candidates: pd.DataFrame,
    cfg: SubsetExpansionConfig,
) -> pd.DataFrame:
    div = cfg.raw.get("morphology_diversity", {})
    q20 = div.get("quotas_expansion_20", {"disk_dominated": 5, "intermediate": 5, "early_bulge": 4})
    q12 = div.get("quotas_expansion_12", {"disk_dominated": 2, "intermediate": 2, "early_bulge": 2})
    n20 = int(cfg.raw.get("cohorts", {}).get("expansion_20", {}).get("additional_count", 14))
    n12 = int(cfg.raw.get("cohorts", {}).get("expansion_12", {}).get("additional_count", 6))

    pool = candidates[candidates["eligible_for_expansion"]].copy()
    out = candidates.copy()

    pick20 = _pick_stratified(pool, n20, q20)
    pick12 = _pick_stratified(pool[pool["galaxy_id"].isin(pick20)], n12, q12)
    if not set(pick12).issubset(set(pick20)):
        pick12 = pick20[:n12]

    for gid in pick20:
        mask = out["galaxy_id"] == gid
        out.loc[mask, "selected_for_expansion_20"] = True
        out.loc[mask, "selection_reason"] = (
            out.loc[mask, "selection_reason"].astype(str)
            + f"expansion_20:{out.loc[mask, 'morphology_class'].iloc[0]}_quota;"
        )

    for gid in pick12:
        mask = out["galaxy_id"] == gid
        out.loc[mask, "selected_for_expansion_12"] = True
        out.loc[mask, "selection_reason"] = (
            out.loc[mask, "selection_reason"].astype(str) + "expansion_12:stratified_subcohort;"
        )

    return out


def build_expansion_plan(
    cfg: SubsetExpansionConfig,
    candidates: pd.DataFrame,
) -> pd.DataFrame:
    original = cfg.original_ids
    rows: list[dict[str, Any]] = []
    order = 0
    for gid in original:
        order += 1
        rows.append(
            {
                "cohort_name": "expansion_12",
                "galaxy_id": gid,
                "cohort_role": "original_controlled_six",
                "in_cohort": True,
                "selection_order": order,
                "cumulative_galaxy_count": order,
            }
        )
    for gid in candidates.loc[candidates["selected_for_expansion_12"], "galaxy_id"]:
        order += 1
        rows.append(
            {
                "cohort_name": "expansion_12",
                "galaxy_id": gid,
                "cohort_role": "expansion_addition",
                "in_cohort": True,
                "selection_order": order,
                "cumulative_galaxy_count": order,
            }
        )

    order20 = 0
    for gid in original:
        order20 += 1
        rows.append(
            {
                "cohort_name": "expansion_20",
                "galaxy_id": gid,
                "cohort_role": "original_controlled_six",
                "in_cohort": True,
                "selection_order": order20,
                "cumulative_galaxy_count": order20,
            }
        )
    for gid in candidates.loc[candidates["selected_for_expansion_20"], "galaxy_id"]:
        order20 += 1
        rows.append(
            {
                "cohort_name": "expansion_20",
                "galaxy_id": gid,
                "cohort_role": "expansion_addition",
                "in_cohort": True,
                "selection_order": order20,
                "cumulative_galaxy_count": order20,
            }
        )
    return pd.DataFrame(rows)


def write_expansion_protocol_report(
    path: Path,
    *,
    cfg: SubsetExpansionConfig,
    candidates: pd.DataFrame,
    plan: pd.DataFrame,
    final_status_path: Path | str | None = None,
) -> None:
    crit = cfg.raw.get("selection_criteria", {})
    pick12 = candidates[candidates["selected_for_expansion_12"]]["galaxy_id"].tolist()
    pick20 = candidates[candidates["selected_for_expansion_20"]]["galaxy_id"].tolist()
    n_eval = len(candidates)
    n_elig = int(candidates["eligible_for_expansion"].sum())

    lines = [
        "# SPARC Controlled Subset Expansion Protocol Report (Phase 5A)",
        "",
        f"> {PROTOCOL_DISCLAIMER}",
        "",
        "## Objective",
        "",
        "Pre-register deterministic criteria for expanding the six-galaxy controlled subset "
        "to **12** and **20** galaxies before any new TDF/NFW/MOND fitting campaign.",
        "",
        "## Cohorts",
        "",
    ]
    for name, spec in cfg.raw.get("cohorts", {}).items():
        lines.append(f"- **{name}:** {spec.get('description', '')} ({spec.get('total_galaxies', '?')} total)")

    lines.extend(
        [
            "",
            "## Selection criteria (pre-registered)",
            "",
            f"- Minimum radial points: **{crit.get('min_radial_points')}**",
            f"- Minimum radial coverage (kpc): **{crit.get('min_radial_coverage_kpc')}**",
            f"- Maximum median velocity uncertainty (km/s): **{crit.get('max_median_v_err_kms')}**",
            f"- Finite rotmod columns: {crit.get('require_finite_rotmod_columns')}",
            f"- Required photometry fields: {crit.get('require_photometry_fields')}",
            "- Morphology diversity quotas (disk-dominated, intermediate, early/bulge)",
            "- **Anti-cherry-picking:** no TDF/NFW/MOND holdout metrics in selection score",
            "",
            "## Candidate pool",
            "",
            f"- Galaxies evaluated (excluding original six): **{n_eval}**",
            f"- Eligible after QC + photometry: **{n_elig}**",
            "",
            "## Proposed expansion_12 additions (6 galaxies)",
            "",
            ", ".join(pick12) if pick12 else "_None_",
            "",
            "## Proposed expansion_20 additions (14 galaxies)",
            "",
            ", ".join(pick20) if pick20 else "_None_",
            "",
            "## Morphology mix (expansion_20 additions)",
            "",
        ]
    )
    if pick20:
        sub = candidates[candidates["galaxy_id"].isin(pick20)]
        for cls, cnt in sub["morphology_class"].value_counts().items():
            lines.append(f"- {cls}: {int(cnt)}")

    lines.extend(
        [
            "",
            "## Relationship to Phase 4M audit",
            "",
        ]
    )
    if final_status_path and Path(final_status_path).is_file():
        lines.append(f"Final six-galaxy audit: `{final_status_path}` (Phase 4M complete).")
    lines.extend(
        [
            "",
            "## Next steps (not part of Phase 5A)",
            "",
            "1. Review and freeze `configs/subset_expansion.yaml`.",
            "2. Run expansion fitting pipeline only after protocol sign-off.",
            "3. Update claim traceability; do not imply full-SPARC validation.",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_subset_expansion_planning(
    *,
    rotmod_path: Path | str = "data/processed/sparc/sparc_rotmod_standardized.csv",
    photometry_path: Path | str = "data/processed/sparc/sparc_photometry_metadata.csv",
    config_path: Path | str = "configs/subset_expansion.yaml",
    subset_path: Path | str = "outputs/tables/sparc_subset_selection.csv",
    final_status_path: Path | str = "outputs/tables/sparc_controlled_subset_final_status.csv",
    candidates_out: Path | str = "outputs/tables/sparc_subset_expansion_candidates.csv",
    plan_out: Path | str = "outputs/tables/sparc_subset_expansion_plan.csv",
    report_out: Path | str = "outputs/reports/sparc_subset_expansion_protocol_report.md",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    cfg = load_subset_expansion_config(config_path)
    rotmod = pd.read_csv(rotmod_path)
    photometry = pd.read_csv(photometry_path)

    subset = pd.read_csv(subset_path)
    original_from_subset = subset.loc[subset["selected"] == True, "galaxy_id"].astype(str).tolist()  # noqa: E712
    if original_from_subset:
        cfg_ids = set(cfg.original_ids)
        if set(original_from_subset) != cfg_ids:
            pass  # config is authoritative; subset used for validation only

    candidates = build_expansion_candidates(rotmod, photometry, cfg=cfg)
    candidates = apply_expansion_selections(candidates, cfg)
    plan = build_expansion_plan(cfg, candidates)

    write_expansion_protocol_report(
        report_out,
        cfg=cfg,
        candidates=candidates,
        plan=plan,
        final_status_path=final_status_path,
    )
    col_order = [
        "galaxy_id",
        "n_points",
        "radial_coverage_kpc",
        "v_obs_range",
        "median_v_err_kms",
        "morphology_type",
        "inclination_deg",
        "luminosity_3p6_lsun",
        "disk_scale_length_kpc",
        "bulge_proxy",
        "selection_score",
        "selected_for_expansion_12",
        "selected_for_expansion_20",
        "selection_reason",
        "caveat",
    ]
    candidates_out_df = candidates[[c for c in col_order if c in candidates.columns]]
    candidates_out_df.to_csv(candidates_out, index=False)
    plan.to_csv(plan_out, index=False)
    return candidates, plan
