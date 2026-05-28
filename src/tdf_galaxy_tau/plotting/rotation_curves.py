from __future__ import annotations

from pathlib import Path


def plot_rotation_curve(*args, **kwargs) -> Path | None:  # pragma: no cover
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    galaxy_id = kwargs["galaxy_id"]
    radius = kwargs["radius"]
    v_obs = kwargs["v_obs"]
    v_bar = kwargs["v_bar"]
    output_path = Path(kwargs["output_path"])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(radius, v_obs, "o", label="observed", color="C0")
    ax.plot(radius, v_bar, "--", label="baryonic", color="C1")
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel("v [km/s]")
    ax.set_title(f"{galaxy_id} rotation diagnostics")
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
