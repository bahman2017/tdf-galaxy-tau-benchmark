from __future__ import annotations

import subprocess

import pandas as pd
import pytest

from tdf_galaxy_tau.reconstruction.radial_tau import TauReconstructionConfig, reconstruct_radial_tau_profile


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "r_kpc": [0.0, 1.0, 2.0],
            "v_obs_kms": [80.0, 85.0, 90.0],
            "v_bar_kms": [70.0, 90.0, 80.0],
        }
    )


def test_k_tau_must_be_positive() -> None:
    with pytest.raises(ValueError, match="k_tau must be positive"):
        reconstruct_radial_tau_profile(_frame(), "G1", TauReconstructionConfig(k_tau=0.0))


def test_negative_radius_rejected() -> None:
    frame = _frame()
    frame.loc[0, "r_kpc"] = -0.1
    with pytest.raises(ValueError, match="r_kpc must be non-negative"):
        reconstruct_radial_tau_profile(frame, "G1", TauReconstructionConfig(k_tau=1.0))


def test_negative_residual_policies() -> None:
    frame = _frame()

    allow = reconstruct_radial_tau_profile(
        frame,
        "G1",
        TauReconstructionConfig(k_tau=1.0, negative_residual_policy="allow_signed"),
    )
    assert (allow["residual_v2_kms2"] < 0).any()
    assert (allow["v_tau2_kms2"] < 0).any()

    clipped = reconstruct_radial_tau_profile(
        frame,
        "G1",
        TauReconstructionConfig(k_tau=1.0, negative_residual_policy="clip_to_zero"),
    )
    assert (clipped["v_tau2_kms2"] >= 0).all()

    masked = reconstruct_radial_tau_profile(
        frame,
        "G1",
        TauReconstructionConfig(k_tau=1.0, negative_residual_policy="mask_negative"),
    )
    assert masked.loc[masked["residual_v2_kms2"] < 0, "v_tau2_kms2"].isna().all()


def test_cli_prints_mock_warning_when_input_missing() -> None:
    cmd = ["python3", "scripts/run_sparc_subset.py", "--config", "configs/sparc_subset.yaml"]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert "No observational claim can be made from mock data." in result.stdout
