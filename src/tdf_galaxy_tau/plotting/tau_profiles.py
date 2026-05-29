from __future__ import annotations

from pathlib import Path

import numpy as np


def plot_tau_gradient_diagnostic(
    galaxy_id: str,
    r_kpc: np.ndarray,
    dtaudr_raw: np.ndarray,
    output_path: Path,
    *,
    dtaudr_smoothed: np.ndarray | None = None,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(r_kpc, dtaudr_raw, "-", color="C2", label="dτ/dr reconstructed (raw)")
    if dtaudr_smoothed is not None and np.isfinite(dtaudr_smoothed).any():
        ax.plot(
            r_kpc,
            dtaudr_smoothed,
            "--",
            color="C3",
            label="dτ/dr smoothed (diagnostic)",
        )
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel("dτ/dr [reconstruction units]")
    ax.set_title(f"{galaxy_id} — radial τ-gradient reconstruction (not model comparison)")
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_tau_profile_diagnostic(
    galaxy_id: str,
    r_kpc: np.ndarray,
    tau_raw: np.ndarray,
    output_path: Path,
    *,
    tau_smoothed: np.ndarray | None = None,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(r_kpc, tau_raw, "-", color="C2", label="τ reconstructed (raw)")
    if tau_smoothed is not None and np.isfinite(tau_smoothed).any():
        ax.plot(
            r_kpc,
            tau_smoothed,
            "--",
            color="C3",
            label="τ smoothed (diagnostic)",
        )
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel("τ [reconstruction units]")
    ax.set_title(f"{galaxy_id} — radial τ-profile reconstruction (not model comparison)")
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_tdf_knot_tau_gradient(
    galaxy_id: str,
    r_kpc: np.ndarray,
    dtaudr_model: np.ndarray,
    knot_r_kpc: np.ndarray,
    knot_dtaudr: np.ndarray,
    output_path: Path,
    *,
    dtaudr_diagnostic: np.ndarray | None = None,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    if dtaudr_diagnostic is not None:
        ax.plot(
            r_kpc,
            dtaudr_diagnostic,
            ":",
            color="C0",
            alpha=0.6,
            label="Phase 2A dτ/dr (diagnostic only)",
        )
    ax.plot(r_kpc, dtaudr_model, "-", color="C2", label="TDF knot dτ/dr model")
    ax.scatter(knot_r_kpc, knot_dtaudr, color="C3", zorder=5, label="knot amplitudes")
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel("dτ/dr")
    ax.set_title(f"{galaxy_id} — TDF knot τ-gradient (fitted model)")
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_tdf_knot_tau_profile(
    galaxy_id: str,
    r_kpc: np.ndarray,
    tau_model: np.ndarray,
    output_path: Path,
    *,
    tau_diagnostic: np.ndarray | None = None,
) -> Path | None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    if tau_diagnostic is not None:
        ax.plot(
            r_kpc,
            tau_diagnostic,
            ":",
            color="C0",
            alpha=0.6,
            label="Phase 2A τ (diagnostic only)",
        )
    ax.plot(r_kpc, tau_model, "-", color="C2", label="TDF knot τ (integrated)")
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel("τ")
    ax.set_title(f"{galaxy_id} — TDF knot τ-profile (fitted model)")
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
