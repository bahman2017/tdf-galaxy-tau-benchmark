from __future__ import annotations

from pathlib import Path

import numpy as np


def write_plot_warning_report(path: str | Path, message: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(message + "\n", encoding="utf-8")


def plot_rotation_baryonic_residual(
    galaxy_id: str,
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    residual_v2_kms2: np.ndarray,
    output_path: Path,
) -> Path | None:
    """Rotation + residual panel (reconstruction diagnostics, not model comparison)."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    residual_accel = residual_v2_kms2 / np.maximum(r_kpc, 1.0e-12)

    fig, (ax_v, ax_r) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    ax_v.errorbar(
        r_kpc,
        v_obs_kms,
        yerr=v_err_kms,
        fmt="o",
        capsize=2,
        label="v_obs",
        color="C0",
    )
    ax_v.plot(r_kpc, v_bar_kms, "--", label="v_bar", color="C1")
    ax_v.set_ylabel("v [km/s]")
    ax_v.set_title(f"{galaxy_id} — rotation reconstruction diagnostics")
    ax_v.grid(alpha=0.3)
    ax_v.legend(loc="best")

    ax_r.plot(r_kpc, residual_accel, "-", color="C4", label="(v_obs^2 - v_bar^2)/r")
    ax_r.axhline(0.0, color="k", linewidth=0.8, alpha=0.5)
    ax_r.set_xlabel("r [kpc]")
    ax_r.set_ylabel("(km/s)^2 / kpc")
    ax_r.set_title("Residual acceleration proxy (not NFW/Burkert/TDF comparison)")
    ax_r.grid(alpha=0.3)
    ax_r.legend(loc="best")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
