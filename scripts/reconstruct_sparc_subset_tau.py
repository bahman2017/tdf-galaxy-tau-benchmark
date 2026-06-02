from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from tdf_galaxy_tau.plotting.diagnostics import plot_rotation_baryonic_residual
from tdf_galaxy_tau.plotting.tau_profiles import (
    plot_tau_gradient_diagnostic,
    plot_tau_profile_diagnostic,
)
from tdf_galaxy_tau.reconstruction.radial_tau import (
    PHASE_2A_OUTPUT_COLUMNS,
    load_reconstruction_config,
    load_selected_galaxy_ids,
    reconstruct_radial_tau_profile,
)


COMBINED_OUT = Path("outputs/tables/sparc_subset_tau_profiles.csv")
PER_GALAXY_DIR = Path("outputs/tables/tau_profiles")
FIGURE_DIR = Path("outputs/figures/sparc_subset")
REPORT_PATH = Path("outputs/reports/sparc_radial_tau_reconstruction_report.md")


def _galaxy_summary(recon: pd.DataFrame) -> dict[str, object]:
    n = len(recon)
    n_neg = int(recon["negative_residual_flag"].sum())
    return {
        "n_points": n,
        "n_negative_residual": n_neg,
        "negative_residual_fraction": float(n_neg / n) if n else 0.0,
        "dtaudr_min": float(recon["dtaudr_reconstructed"].min()),
        "dtaudr_max": float(recon["dtaudr_reconstructed"].max()),
        "tau_min": float(recon["tau_reconstructed"].min()),
        "tau_max": float(recon["tau_reconstructed"].max()),
    }


def _write_report(
    path: Path,
    *,
    galaxy_ids: list[str],
    summaries: dict[str, dict[str, object]],
    config_block: object,
    figure_paths: list[str],
    table_paths: list[str],
) -> None:
    cfg = config_block
    lines = [
        "# SPARC Radial Tau Reconstruction Report (Phase 2A)",
        "",
        "## Scope",
        "",
        "This phase reconstructs radial τ-profiles from rotation residuals only. "
        "It does not compare TDF against NFW or Burkert, does not validate TDF on SPARC, "
        "and does not disprove dark matter.",
        "",
        "## Run settings",
        "",
        f"- Selected galaxies processed: {', '.join(galaxy_ids)}",
        f"- K_g (legacy K_tau label): {cfg.k_g}",
        f"- Negative residual policy: {cfg.negative_residual_policy}",
        f"- Integration boundary: {cfg.integration_boundary}",
        f"- Smoothing enabled: {cfg.smoothing.enabled}",
        f"- Smoothing method: {cfg.smoothing.method}",
        f"- Smoothing sigma_points: {cfg.smoothing.sigma_points}",
        f"- Smoothing diagnostic_only: {cfg.smoothing.diagnostic_only}",
        "",
        "## Per-galaxy summary",
        "",
        "| Galaxy | n_points | n_neg_residual | neg_fraction | dτ/dr min | dτ/dr max | τ min | τ max |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for gid in galaxy_ids:
        s = summaries[gid]
        lines.append(
            f"| {gid} | {s['n_points']} | {s['n_negative_residual']} | "
            f"{s['negative_residual_fraction']:.3f} | {s['dtaudr_min']:.4g} | {s['dtaudr_max']:.4g} | "
            f"{s['tau_min']:.4g} | {s['tau_max']:.4g} |"
        )

    lines.extend(["", "## Generated tables", ""])
    for p in table_paths:
        lines.append(f"- `{p}`")

    lines.extend(["", "## Generated figures", ""])
    for p in figure_paths:
        lines.append(f"- `{p}`")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 2A radial tau reconstruction for selected SPARC subset")
    parser.add_argument("--data", required=True, help="Standardized SPARC CSV")
    parser.add_argument("--subset", required=True, help="Subset selection CSV")
    parser.add_argument("--config", required=True, help="Reconstruction YAML config")
    args = parser.parse_args()

    cfg = load_reconstruction_config(args.config)
    data = pd.read_csv(args.data)
    galaxy_ids = load_selected_galaxy_ids(args.subset)

    frames: list[pd.DataFrame] = []
    summaries: dict[str, dict[str, object]] = {}
    figure_paths: list[str] = []
    table_paths: list[str] = []

    PER_GALAXY_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    for gid in galaxy_ids:
        group = data[data["galaxy_id"] == gid]
        if group.empty:
            raise ValueError(f"selected galaxy {gid!r} not found in {args.data}")

        recon = reconstruct_radial_tau_profile(group, gid, cfg)
        frames.append(recon)
        summaries[gid] = _galaxy_summary(recon)

        per_galaxy_csv = PER_GALAXY_DIR / f"{gid}_tau_profile.csv"
        recon.to_csv(per_galaxy_csv, index=False)
        table_paths.append(str(per_galaxy_csv))

        d_smooth = recon["dtaudr_smoothed_diagnostic"].to_numpy()
        tau_smooth = recon["tau_smoothed_diagnostic"].to_numpy()
        has_smooth = cfg.smoothing.enabled and pd.notna(d_smooth).any()

        rot_path = FIGURE_DIR / f"{gid}_rotation_baryonic_residual.png"
        grad_path = FIGURE_DIR / f"{gid}_tau_gradient.png"
        tau_path = FIGURE_DIR / f"{gid}_tau_profile.png"

        plot_rotation_baryonic_residual(
            gid,
            recon["r_kpc"].to_numpy(),
            recon["v_obs_kms"].to_numpy(),
            recon["v_err_kms"].to_numpy(),
            recon["v_bar_kms"].to_numpy(),
            recon["residual_v2_kms2"].to_numpy(),
            rot_path,
        )
        plot_tau_gradient_diagnostic(
            gid,
            recon["r_kpc"].to_numpy(),
            recon["dtaudr_reconstructed"].to_numpy(),
            grad_path,
            dtaudr_smoothed=d_smooth if has_smooth else None,
        )
        plot_tau_profile_diagnostic(
            gid,
            recon["r_kpc"].to_numpy(),
            recon["tau_reconstructed"].to_numpy(),
            tau_path,
            tau_smoothed=tau_smooth if has_smooth else None,
        )
        for p in (rot_path, grad_path, tau_path):
            figure_paths.append(str(p))

    combined = pd.concat(frames, ignore_index=True)
    assert list(combined.columns) == PHASE_2A_OUTPUT_COLUMNS
    COMBINED_OUT.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(COMBINED_OUT, index=False)
    table_paths.insert(0, str(COMBINED_OUT))

    _write_report(
        REPORT_PATH,
        galaxy_ids=galaxy_ids,
        summaries=summaries,
        config_block=cfg,
        figure_paths=figure_paths,
        table_paths=table_paths,
    )

    print(f"Processed galaxies: {', '.join(galaxy_ids)}")
    print(f"Total reconstructed rows: {len(combined)}")
    print(f"Wrote combined table: {COMBINED_OUT}")
    print(f"Wrote report: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
