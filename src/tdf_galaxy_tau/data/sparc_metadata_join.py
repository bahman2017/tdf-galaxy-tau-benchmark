from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tdf_galaxy_tau.data.sparc_photometry_parser import STANDARD_PHOTOMETRY_COLUMNS, load_table1_photometry
from tdf_galaxy_tau.reconstruction.radial_tau import load_selected_galaxy_ids
from tdf_galaxy_tau.validation.failure_modes import MANDATED_GALAXY_CLASSIFICATION

TARGET_GALAXY = "NGC7814"
INGESTION_STAGE = "phase_4j_photometry_metadata"


def _rotmod_derived_features(rotmod: pd.DataFrame) -> pd.DataFrame:
    """Supplement Table 1 with rotmod-only proxies (distance cross-check, bulge flags)."""
    rows: list[dict[str, Any]] = []
    for gid, g in rotmod.groupby("galaxy_id"):
        g = g.sort_values("r_kpc")
        dist = float(g["distance_mpc"].iloc[0]) if "distance_mpc" in g.columns else float("nan")
        v_bulge = g["v_bulge_kms"].to_numpy(dtype=float)
        sb_bulge = g["sb_bulge_lpc2"].to_numpy(dtype=float) if "sb_bulge_lpc2" in g.columns else np.zeros(len(g))
        sb_disk = g["sb_disk_lpc2"].to_numpy(dtype=float) if "sb_disk_lpc2" in g.columns else np.full(len(g), np.nan)
        r = g["r_kpc"].to_numpy(dtype=float)

        has_bulge = bool(np.any(np.abs(v_bulge) > 5.0))
        inner_sb_bulge = float(np.nanmax(sb_bulge[: max(1, len(sb_bulge) // 5)])) if has_bulge else float("nan")
        inner_sb_disk = float(sb_disk[0]) if len(sb_disk) and np.isfinite(sb_disk[0]) else float("nan")

        rd_est = float("nan")
        if np.any(np.isfinite(sb_disk)) and np.any(r > 0):
            valid = np.isfinite(sb_disk) & (sb_disk > 0) & (r > 0)
            if valid.sum() >= 3:
                s0 = float(sb_disk[valid][0])
                target = s0 / np.e
                idx = np.where((sb_disk[valid] <= target) & (r[valid] > r[valid][0]))[0]
                if len(idx):
                    rd_est = float(r[valid][idx[0]])

        rows.append(
            {
                "galaxy_id": gid,
                "rotmod_distance_mpc": dist,
                "rotmod_has_bulge_proxy": has_bulge,
                "rotmod_inner_sb_bulge_lpc2": inner_sb_bulge,
                "rotmod_inner_sb_disk_lpc2": inner_sb_disk,
                "rotmod_disk_scale_length_est_kpc": rd_est,
            }
        )
    return pd.DataFrame(rows)


def build_photometry_metadata_table(
    rotmod: pd.DataFrame,
    table1: pd.DataFrame,
) -> pd.DataFrame:
    galaxy_ids = sorted(rotmod["galaxy_id"].unique())
    rot = _rotmod_derived_features(rotmod)
    t1 = table1.drop_duplicates(subset=["galaxy_id"], keep="first")
    merged = pd.DataFrame({"galaxy_id": galaxy_ids})
    merged = merged.merge(t1, on="galaxy_id", how="left")
    merged = merged.merge(rot, on="galaxy_id", how="left")

    if "distance_mpc" in merged.columns:
        miss = merged["distance_mpc"].isna()
        merged.loc[miss, "distance_mpc"] = merged.loc[miss, "rotmod_distance_mpc"]
        merged.loc[miss, "metadata_source"] = merged.loc[miss, "metadata_source"].fillna("rotmod_header_fallback")

    for col in STANDARD_PHOTOMETRY_COLUMNS:
        if col not in merged.columns:
            merged[col] = np.nan if col != "galaxy_id" else ""

    merged["data_mode"] = INGESTION_STAGE
    merged["photometry_quality_flag"] = merged["photometry_quality_flag"].fillna("missing_table1")
    merged["metadata_source"] = merged["metadata_source"].fillna("unmatched")
    merged["source_table"] = merged["source_table"].fillna("")
    merged["source_notes"] = merged["source_notes"].fillna("")

    return merged[STANDARD_PHOTOMETRY_COLUMNS + ["rotmod_has_bulge_proxy", "rotmod_disk_scale_length_est_kpc"]]


def build_photometry_summary(metadata: pd.DataFrame) -> pd.DataFrame:
    fields = [
        "distance_mpc",
        "inclination_deg",
        "luminosity_3p6_lsun",
        "disk_scale_length_kpc",
        "central_surface_brightness",
        "morphological_type",
    ]
    rows: list[dict[str, Any]] = []
    for f in fields:
        if f not in metadata.columns:
            continue
        s = metadata[f]
        rows.append(
            {
                "field": f,
                "n_total": int(len(s)),
                "n_finite": int(s.notna().sum()),
                "n_missing": int(s.isna().sum()),
                "fraction_missing": float(s.isna().mean()),
            }
        )
    rows.append(
        {
            "field": "n_galaxies",
            "n_total": len(metadata),
            "n_finite": len(metadata),
            "n_missing": 0,
            "fraction_missing": 0.0,
        }
    )
    return pd.DataFrame(rows)


def _bulge_dominated_proxy(row: pd.Series) -> bool:
    if bool(row.get("rotmod_has_bulge_proxy", False)):
        return True
    t = row.get("morphological_type", np.nan)
    try:
        if np.isfinite(float(t)) and float(t) <= 2:
            return True
    except (TypeError, ValueError):
        pass
    return False


def build_subset_photometry_context(
    metadata: pd.DataFrame,
    subset_path: Path | str,
) -> pd.DataFrame:
    selected = load_selected_galaxy_ids(subset_path)
    sub = metadata[metadata["galaxy_id"].isin(selected)].copy()
    rows: list[dict[str, Any]] = []
    for gid in selected:
        if gid not in sub["galaxy_id"].values:
            rows.append({"galaxy_id": gid, "notes_for_ml_prior": "missing from metadata join"})
            continue
        row = sub[sub["galaxy_id"] == gid].iloc[0]
        classification = MANDATED_GALAXY_CLASSIFICATION.get(gid, "unknown")
        has_bulge = bool(row.get("rotmod_has_bulge_proxy", False))
        bulge_dom = _bulge_dominated_proxy(row)
        note = _ml_prior_note(gid, classification, row, has_bulge, bulge_dom)
        rows.append(
            {
                "galaxy_id": gid,
                "canonical_classification": classification,
                "distance_mpc": row.get("distance_mpc"),
                "inclination_deg": row.get("inclination_deg"),
                "luminosity_3p6_lsun": row.get("luminosity_3p6_lsun"),
                "disk_scale_length_kpc": row.get("disk_scale_length_kpc"),
                "morphological_type": row.get("morphological_type"),
                "has_bulge_proxy": has_bulge,
                "bulge_dominated_proxy": bulge_dom,
                "notes_for_ml_prior": note,
            }
        )
    return pd.DataFrame(rows)


def _ml_prior_note(
    gid: str,
    classification: str,
    row: pd.Series,
    has_bulge: bool,
    bulge_dom: bool,
) -> str:
    if gid == TARGET_GALAXY:
        return (
            "Sa-type (Type~2), high L3.6 and SBdisk; bulge-dominated proxy True. "
            "Supports photometry-informed downweight of bulge M/L in future priors; "
            "does not change canonical tdf_3knot failure."
        )
    if classification == "robust_tdf_success":
        if has_bulge:
            return "Success case with disk-dominated rotmod; moderate Table-1 type."
        return "Disk-dominated dwarf/spiral; future priors may favor near-unity disk M/L."
    return "See Table 1 + rotmod proxies."


def write_photometry_ingestion_report(
    path: Path,
    *,
    metadata: pd.DataFrame,
    summary: pd.DataFrame,
    subset_ctx: pd.DataFrame,
    source_file: str,
) -> None:
    ngc = subset_ctx[subset_ctx["galaxy_id"] == TARGET_GALAXY].iloc[0]
    success = subset_ctx[subset_ctx["galaxy_id"] != TARGET_GALAXY]

    lines = [
        "# SPARC Photometry Metadata Ingestion Report (Phase 4J)",
        "",
        "> This phase ingests photometry metadata for future M/L prior construction. "
        "It does not perform final M/L calibration, does not rerun model fits, "
        "does not validate TDF on full SPARC, does not disprove dark matter, "
        "and does not include lensing.",
        "",
        "## Data source and provenance",
        "",
        "- **Scientific citation:** Lelli, McGaugh & Schombert (2016), AJ 152, 157; SPARC http://astroweb.case.edu/SPARC/",
        f"- **Working copy used:** `{source_file}` under `data/raw/sparc/photometry/` (CDS/VizieR transport)",
        "- **Rotmod cross-check:** distance from `sparc_rotmod_standardized.csv` when needed",
        "",
        "## Schema and units",
        "",
        "- `distance_mpc` — Mpc",
        "- `inclination_deg` — degrees",
        "- `luminosity_3p6_lsun` — L_sun at 3.6 µm (Table 1)",
        "- `disk_scale_length_kpc` — exponential disk scale length R_d (kpc)",
        "- `central_surface_brightness` — 3.6 µm central disk SB (L_sun/pc²) from Table 1",
        "- `morphological_type` — numerical Hubble type (0–11) from Table 1",
        "",
        "## Missing-field summary",
        "",
    ]
    for _, r in summary.iterrows():
        if r["field"] == "n_galaxies":
            lines.append(f"- Galaxies in metadata table: **{int(r['n_finite'])}**")
        else:
            lines.append(
                f"- `{r['field']}`: {int(r['n_finite'])}/{int(r['n_total'])} finite "
                f"({100 * r['fraction_missing']:.1f}% missing)"
            )

    lines.extend(
        [
            "",
            "## Six-galaxy subset",
            "",
            "| Galaxy | Class | D [Mpc] | i [deg] | L3.6 | Rd [kpc] | Type | Bulge proxy |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for _, r in subset_ctx.iterrows():
        lines.append(
            f"| {r['galaxy_id']} | {r['canonical_classification']} | {r['distance_mpc']} | "
            f"{r['inclination_deg']} | {r['luminosity_3p6_lsun']} | {r['disk_scale_length_kpc']} | "
            f"{r['morphological_type']} | {r['bulge_dominated_proxy']} |"
        )

    lines.extend(
        [
            "",
            "## NGC7814 photometry and structural context",
            "",
            f"- {ngc['notes_for_ml_prior']}",
            f"- Distance **{ngc['distance_mpc']}** Mpc, inclination **{ngc['inclination_deg']}**°, "
            f"L3.6 **{ngc['luminosity_3p6_lsun']}** L_sun, R_disk **{ngc['disk_scale_length_kpc']}** kpc.",
            "- Compared to success galaxies: **higher luminosity**, **earlier type (bulge/spheroid component)**, "
            "**much higher central disk SB** — structurally distinct for future bulge-aware M/L priors.",
            "- **Canonical tdf_3knot holdout failure unchanged** at fixed rotmod baryons.",
            "",
            "## Five success galaxies",
            "",
            "- Typically later types / lower central SB / no strong bulge in rotmod (see subset table).",
            f"- Bulge-dominated proxy True count: **{int(success['bulge_dominated_proxy'].sum())} / 5**",
            "",
            "## Future M/L priors (not implemented here)",
            "",
            "- Map L3.6 and type to disk/bulge M/L bands with uncertainties",
            "- Replace Cartesian diagnostic weights in `configs/ml_priors.yaml`",
            "- Re-run prior audit (4I-Audit) before external recovery language",
            "",
        ]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_photometry_metadata_ingestion(
    *,
    rotmod_path: Path | str = "data/processed/sparc/sparc_rotmod_standardized.csv",
    photometry_dir: Path | str = "data/raw/sparc/photometry",
    subset_path: Path | str = "outputs/tables/sparc_subset_selection.csv",
    metadata_out: Path | str = "data/processed/sparc/sparc_photometry_metadata.csv",
    summary_out: Path | str = "outputs/tables/sparc_photometry_metadata_summary.csv",
    subset_ctx_out: Path | str = "outputs/tables/sparc_subset_photometry_context.csv",
    report_out: Path | str = "outputs/reports/sparc_photometry_metadata_ingestion_report.md",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rotmod = pd.read_csv(rotmod_path)
    table1, source_name = load_table1_photometry(photometry_dir)
    metadata = build_photometry_metadata_table(rotmod, table1)
    summary = build_photometry_summary(metadata)
    subset_ctx = build_subset_photometry_context(metadata, subset_path)

    out_cols = [c for c in STANDARD_PHOTOMETRY_COLUMNS if c in metadata.columns]
    metadata[out_cols].to_csv(metadata_out, index=False)
    summary.to_csv(summary_out, index=False)
    subset_ctx.to_csv(subset_ctx_out, index=False)
    write_photometry_ingestion_report(
        report_out,
        metadata=metadata,
        summary=summary,
        subset_ctx=subset_ctx,
        source_file=source_name,
    )
    return metadata, summary, subset_ctx
