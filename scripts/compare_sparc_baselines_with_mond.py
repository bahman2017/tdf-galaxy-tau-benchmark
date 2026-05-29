from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from tdf_galaxy_tau.metrics.comparison import build_best_baseline_with_mond_summary
from tdf_galaxy_tau.models.fitting import (
    fit_burkert_baseline_log,
    fit_mond_a0_simple,
    fit_mond_fixed_a0,
    fit_nfw_baseline_log,
)
from tdf_galaxy_tau.plotting.rotation_curves import plot_baseline_with_mond_rotation_comparison
from tdf_galaxy_tau.reconstruction.radial_tau import load_selected_galaxy_ids

COMBINED_TABLE = Path("outputs/tables/sparc_baseline_with_mond_comparison.csv")
SUMMARY_TABLE = Path("outputs/tables/sparc_best_baseline_with_mond_summary.csv")
FIG_DIR = Path("outputs/figures/sparc_subset")
FIG_SUFFIX = "_baseline_with_mond_rotation_comparison.png"


def _rename_halo_models(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    rename = {"nfw": "nfw_refit", "burkert": "burkert_refit"}
    out["model_name"] = out["model_name"].replace(rename)
    return out


def _load_halo_refit_velocities(
    data: pd.DataFrame,
    gid: str,
    cfg: dict,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Recompute NFW/Burkert refit curves for plotting if halo table lacks velocities."""
    g = data[data["galaxy_id"] == gid].sort_values("r_kpc")
    if g.empty:
        return None, None
    r = g["r_kpc"].to_numpy()
    v_obs = g["v_obs_kms"].to_numpy()
    v_err = g["v_err_kms"].to_numpy()
    v_bar = g["v_bar_kms"].to_numpy()
    robust = cfg.get("robust_fit", {})
    nfw_b = robust.get("nfw", {})
    burk_b = robust.get("burkert", {})
    nfw = fit_nfw_baseline_log(
        r,
        v_obs,
        v_err,
        v_bar,
        log10_rho_s_bounds=tuple(nfw_b["log10_rho_s_bounds_msun_kpc3"]),
        log10_r_s_bounds=tuple(nfw_b["log10_r_s_bounds_kpc"]),
    )
    burk = fit_burkert_baseline_log(
        r,
        v_obs,
        v_err,
        v_bar,
        log10_rho_0_bounds=tuple(burk_b["log10_rho_0_bounds_msun_kpc3"]),
        log10_r_0_bounds=tuple(burk_b["log10_r_0_bounds_kpc"]),
    )
    v_nfw = nfw.v_model_kms if nfw.fit_success else None
    v_burk = burk.v_model_kms if burk.fit_success else None
    return v_nfw, v_burk


def main() -> int:
    parser = argparse.ArgumentParser(description="Combine halo refit and MOND baselines")
    parser.add_argument("--halo", required=True, help="Halo refit comparison CSV")
    parser.add_argument("--mond", required=True, help="MOND comparison CSV")
    parser.add_argument(
        "--data",
        default="data/processed/sparc/sparc_rotmod_standardized.csv",
        help="Standardized SPARC data for figure recomputation",
    )
    parser.add_argument(
        "--subset",
        default="outputs/tables/sparc_subset_selection.csv",
        help="Subset selection table",
    )
    parser.add_argument("--config", default="configs/models.yaml")
    args = parser.parse_args()

    halo = _rename_halo_models(pd.read_csv(args.halo))
    mond = pd.read_csv(args.mond)
    combined = pd.concat([halo, mond], ignore_index=True)
    combined = combined[combined["model_name"] != "tdf"]
    COMBINED_TABLE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(COMBINED_TABLE, index=False)

    summary = build_best_baseline_with_mond_summary(combined)
    summary.to_csv(SUMMARY_TABLE, index=False)

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    data = pd.read_csv(args.data)
    selected_ids = load_selected_galaxy_ids(args.subset)
    mond_cfg = cfg.get("mond", {})
    a0_fixed = float(mond_cfg.get("a0_fixed_m_s2", 1.2e-10))
    log_bounds = tuple(mond_cfg.get("log10_a0_bounds_m_s2", [-11.5, -9.5]))
    log_init = float(mond_cfg.get("log10_a0_initial", -10.0))

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for gid in selected_ids:
        g = data[data["galaxy_id"] == gid].sort_values("r_kpc")
        if g.empty:
            continue
        r = g["r_kpc"].to_numpy()
        v_obs = g["v_obs_kms"].to_numpy()
        v_err = g["v_err_kms"].to_numpy()
        v_bar = g["v_bar_kms"].to_numpy()

        v_nfw, v_burk = _load_halo_refit_velocities(data, gid, cfg)
        fixed = fit_mond_fixed_a0(r, v_obs, v_err, v_bar, a0_ms2=a0_fixed)
        fitted = fit_mond_a0_simple(
            r,
            v_obs,
            v_err,
            v_bar,
            log10_a0_bounds=log_bounds,
            log10_a0_initial=log_init,
        )
        plot_baseline_with_mond_rotation_comparison(
            gid,
            r,
            v_obs,
            v_err,
            v_bar,
            FIG_DIR / f"{gid}{FIG_SUFFIX}",
            v_nfw_kms=v_nfw,
            v_burkert_kms=v_burk,
            v_mond_fixed_kms=fixed.v_model_kms if fixed.fit_success else None,
            v_mond_fit_kms=fitted.v_model_kms if fitted.fit_success else None,
        )

    print(f"Wrote combined comparison: {COMBINED_TABLE}")
    print(f"Wrote best-baseline summary: {SUMMARY_TABLE}")
    print(f"Wrote figures: outputs/figures/sparc_subset/*{FIG_SUFFIX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
