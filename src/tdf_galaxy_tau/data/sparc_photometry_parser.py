from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

STANDARD_PHOTOMETRY_COLUMNS = [
    "galaxy_id",
    "distance_mpc",
    "inclination_deg",
    "luminosity_3p6_lsun",
    "disk_scale_length_kpc",
    "central_surface_brightness",
    "morphological_type",
    "photometry_quality_flag",
    "metadata_source",
    "data_mode",
    "source_table",
    "source_notes",
]

VIZIER_COLUMN_MAP = {
    "Name": "galaxy_id",
    "Dist": "distance_mpc",
    "i": "inclination_deg",
    "L3.6": "luminosity_3p6_lsun",
    "Rdisk": "disk_scale_length_kpc",
    "SBdisk": "central_surface_brightness",
    "Type": "morphological_type",
}


def normalize_galaxy_id(name: str) -> str:
    return re.sub(r"\s+", "", str(name).strip())


def parse_vizier_table1_tsv(path: Path | str) -> pd.DataFrame:
    """Parse VizieR ASU-TSV export of J/AJ/152/157 table1."""
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    data_lines = [ln for ln in lines if ln.strip() and not ln.startswith("#")]
    if len(data_lines) < 2:
        raise ValueError(f"no data rows in {path}")

    header = data_lines[0].split("\t")
    header = [h.strip() for h in header]
    rows: list[dict[str, Any]] = []
    for ln in data_lines[1:]:
        if ln.strip().startswith("---") or ln.strip().startswith("deg"):
            continue
        parts = ln.split("\t")
        if len(parts) < len(header):
            parts.extend([""] * (len(header) - len(parts)))
        row = dict(zip(header, parts))
        rows.append(row)

    raw = pd.DataFrame(rows)
    out = pd.DataFrame()
    for src, dst in VIZIER_COLUMN_MAP.items():
        if src in raw.columns:
            out[dst] = pd.to_numeric(raw[src], errors="coerce") if dst != "galaxy_id" else raw[src]
        else:
            out[dst] = np.nan if dst != "galaxy_id" else ""

    if "galaxy_id" in out.columns:
        out["galaxy_id"] = out["galaxy_id"].astype(str).map(normalize_galaxy_id)
    out["metadata_source"] = "VizieR_J_AJ_152_157_table1_working_copy"
    out["source_table"] = "J/AJ/152/157/table1"
    out["source_notes"] = (
        "CDS/VizieR transport of Lelli+2016 Table 1; cite AJ paper and SPARC site for science."
    )
    out["data_mode"] = "sparc_table1_ingestion"
    out["photometry_quality_flag"] = "vizier_table1"
    return out


def parse_mrt_table1_simple(path: Path | str) -> pd.DataFrame:
    """Best-effort parser for fixed-width SPARC Table1.mrt-style files."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    data_start = 0
    for i, ln in enumerate(lines):
        if re.match(r"^[A-Za-z]", ln.strip()) and "Galaxy" not in ln and "----" not in ln:
            data_start = i
            break
    rows: list[dict[str, Any]] = []
    for ln in lines[data_start:]:
        if ln.strip().startswith("----") or len(ln) < 12:
            continue
        name = ln[:11].strip()
        if not name or name.lower() == "galaxy":
            continue
        try:
            t = int(ln[11:13].strip())
        except ValueError:
            t = np.nan
        try:
            d = float(ln[13:19].strip())
        except ValueError:
            d = np.nan
        try:
            i_deg = float(ln[24:28].strip())
        except ValueError:
            i_deg = np.nan
        try:
            l36 = float(ln[28:35].strip())
        except ValueError:
            l36 = np.nan
        try:
            rd = float(ln[35:41].strip())
        except ValueError:
            rd = np.nan
        try:
            sb = float(ln[41:50].strip())
        except ValueError:
            sb = np.nan
        rows.append(
            {
                "galaxy_id": normalize_galaxy_id(name),
                "morphological_type": t,
                "distance_mpc": d,
                "inclination_deg": i_deg,
                "luminosity_3p6_lsun": l36,
                "disk_scale_length_kpc": rd,
                "central_surface_brightness": sb,
            }
        )
    df = pd.DataFrame(rows)
    df["metadata_source"] = "local_MasterSheet_SPARC_mrt"
    df["source_table"] = "Table1.mrt"
    df["source_notes"] = "Local working copy of official SPARC Table 1."
    df["data_mode"] = "sparc_table1_ingestion"
    df["photometry_quality_flag"] = "official_mrt"
    return df


def load_table1_photometry(photometry_dir: Path | str) -> tuple[pd.DataFrame, str]:
    """Prefer official .mrt if present; else VizieR working copy."""
    root = Path(photometry_dir)
    mrt_candidates = list(root.glob("MasterSheet*.mrt")) + list(root.glob("Table1.mrt"))
    for p in mrt_candidates:
        if p.is_file():
            return parse_mrt_table1_simple(p), str(p.name)

    vizier = root / "SPARC_Table1_vizier_working_copy.tsv"
    if vizier.is_file():
        return parse_vizier_table1_tsv(vizier), vizier.name

    raise FileNotFoundError(
        f"No SPARC Table 1 working copy in {root}. "
        "Add SPARC_Table1_vizier_working_copy.tsv or MasterSheet_SPARC.mrt."
    )
