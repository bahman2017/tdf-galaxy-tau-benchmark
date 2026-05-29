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


def plot_baseline_rotation_comparison(
    galaxy_id: str,
    r_kpc,
    v_obs_kms,
    v_err_kms,
    v_baryonic_kms,
    output_path: Path,
    *,
    v_nfw_kms=None,
    v_burkert_kms=None,
    title_suffix: str | None = None,
) -> Path | None:  # pragma: no cover
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(r_kpc, v_obs_kms, yerr=v_err_kms, fmt="o", capsize=2, label="observed", color="C0")
    ax.plot(r_kpc, v_baryonic_kms, "--", label="baryonic-only", color="C1")
    if v_nfw_kms is not None:
        ax.plot(r_kpc, v_nfw_kms, "-", label="NFW fit", color="C2")
    if v_burkert_kms is not None:
        ax.plot(r_kpc, v_burkert_kms, "-.", label="Burkert fit", color="C3")
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel("v [km/s]")
    title = f"{galaxy_id} baseline rotation comparison (no TDF fit in this phase)"
    if title_suffix:
        title = f"{galaxy_id} baseline rotation comparison — {title_suffix}"
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_baseline_with_mond_rotation_comparison(
    galaxy_id: str,
    r_kpc,
    v_obs_kms,
    v_err_kms,
    v_baryonic_kms,
    output_path: Path,
    *,
    v_nfw_kms=None,
    v_burkert_kms=None,
    v_mond_fixed_kms=None,
    v_mond_fit_kms=None,
) -> Path | None:  # pragma: no cover
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.errorbar(r_kpc, v_obs_kms, yerr=v_err_kms, fmt="o", capsize=2, label="observed", color="C0")
    ax.plot(r_kpc, v_baryonic_kms, "--", label="baryonic-only", color="C1")
    if v_nfw_kms is not None:
        ax.plot(r_kpc, v_nfw_kms, "-", label="NFW refit", color="C2")
    if v_burkert_kms is not None:
        ax.plot(r_kpc, v_burkert_kms, "-.", label="Burkert refit", color="C3")
    if v_mond_fixed_kms is not None:
        ax.plot(r_kpc, v_mond_fixed_kms, ":", label="MOND fixed a0", color="C4")
    if v_mond_fit_kms is not None:
        ax.plot(r_kpc, v_mond_fit_kms, "-", label="MOND fit a0", color="C5", linewidth=1.2)
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel("v [km/s]")
    ax.set_title(f"{galaxy_id} baselines with MOND (no TDF fit)")
    ax.grid(alpha=0.3)
    ax.legend(loc="best", fontsize=8)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_full_model_rotation_comparison(
    galaxy_id: str,
    r_kpc,
    v_obs_kms,
    v_err_kms,
    v_baryonic_kms,
    output_path: Path,
    *,
    v_nfw_kms=None,
    v_burkert_kms=None,
    v_mond_fit_kms=None,
    v_tdf_3knot_kms=None,
    v_tdf_5knot_kms=None,
) -> Path | None:  # pragma: no cover
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.errorbar(r_kpc, v_obs_kms, yerr=v_err_kms, fmt="o", capsize=2, label="observed", color="C0")
    ax.plot(r_kpc, v_baryonic_kms, "--", label="baryonic-only", color="C1")
    if v_nfw_kms is not None:
        ax.plot(r_kpc, v_nfw_kms, "-", label="NFW refit", color="C2", alpha=0.85)
    if v_burkert_kms is not None:
        ax.plot(r_kpc, v_burkert_kms, "-.", label="Burkert refit", color="C3", alpha=0.85)
    if v_mond_fit_kms is not None:
        ax.plot(r_kpc, v_mond_fit_kms, ":", label="MOND fit a0", color="C4")
    if v_tdf_3knot_kms is not None:
        ax.plot(r_kpc, v_tdf_3knot_kms, "-", label="TDF 3-knot", color="C5", linewidth=1.5)
    if v_tdf_5knot_kms is not None:
        ax.plot(r_kpc, v_tdf_5knot_kms, "--", label="TDF 5-knot (sensitivity)", color="C6", linewidth=1.0)
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel("v [km/s]")
    ax.set_title(f"{galaxy_id} — full model rotation comparison (subset)")
    ax.grid(alpha=0.3)
    ax.legend(loc="best", fontsize=7)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
