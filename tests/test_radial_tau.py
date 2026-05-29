from __future__ import annotations

import subprocess

import numpy as np
import pandas as pd
import pytest
import yaml

from tdf_galaxy_tau.reconstruction.radial_tau import (
    PHASE_2A_OUTPUT_COLUMNS,
    TauReconstructionConfig,
    reconstruct_radial_tau_profile,
)
from tdf_galaxy_tau.reconstruction.regularization import SmoothingConfig


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "r_kpc": [0.5, 1.0, 2.0],
            "v_obs_kms": [80.0, 85.0, 90.0],
            "v_bar_kms": [70.0, 90.0, 80.0],
            "v_err_kms": [2.0, 2.0, 2.0],
            "data_source": ["test"] * 3,
            "data_mode": ["test"] * 3,
        }
    )


def test_k_tau_must_be_positive() -> None:
    with pytest.raises(ValueError, match="k_tau must be positive"):
        reconstruct_radial_tau_profile(_frame(), "G1", TauReconstructionConfig(k_tau=0.0))


def test_non_positive_radius_rejected() -> None:
    frame = _frame()
    frame.loc[0, "r_kpc"] = 0.0
    with pytest.raises(ValueError, match="r_kpc must be strictly positive"):
        reconstruct_radial_tau_profile(frame, "G1", TauReconstructionConfig(k_tau=1.0))


def test_rows_sorted_before_integration() -> None:
    frame = _frame().iloc[::-1].reset_index(drop=True)
    out = reconstruct_radial_tau_profile(frame, "G1", TauReconstructionConfig(k_tau=1.0))
    assert out["r_kpc"].is_monotonic_increasing


def test_tau_starts_at_zero() -> None:
    out = reconstruct_radial_tau_profile(_frame(), "G1", TauReconstructionConfig(k_tau=1.0))
    assert out["tau_reconstructed"].iloc[0] == pytest.approx(0.0)


def test_allow_signed_preserves_negative_residuals() -> None:
    out = reconstruct_radial_tau_profile(
        _frame(),
        "G1",
        TauReconstructionConfig(k_tau=1.0, negative_residual_policy="allow_signed"),
    )
    assert (out["residual_v2_kms2"] < 0).any()
    assert (out["dtaudr_reconstructed"] < 0).any()


def test_clip_to_zero_clips_negative_residual() -> None:
    out = reconstruct_radial_tau_profile(
        _frame(),
        "G1",
        TauReconstructionConfig(k_tau=1.0, negative_residual_policy="clip_to_zero"),
    )
    assert (out["residual_v2_kms2"] < 0).any()
    neg_mask = out["negative_residual_flag"]
    assert (out.loc[neg_mask, "dtaudr_reconstructed"] >= 0).all()


def test_mask_negative_removes_negative_rows() -> None:
    frame = _frame()
    out = reconstruct_radial_tau_profile(
        frame,
        "G1",
        TauReconstructionConfig(k_tau=1.0, negative_residual_policy="mask_negative"),
    )
    assert len(out) < len(frame)
    assert (out["residual_v2_kms2"] >= 0).all()


def test_phase_2a_output_columns() -> None:
    out = reconstruct_radial_tau_profile(
        _frame(),
        "G1",
        TauReconstructionConfig(k_tau=1.0, smoothing=SmoothingConfig(enabled=True)),
    )
    assert list(out.columns) == PHASE_2A_OUTPUT_COLUMNS


def test_cli_prints_mock_warning_when_input_missing(tmp_path) -> None:
    cfg = {
        "input_csv": str(tmp_path / "missing.csv"),
        "output_tau_profiles": str(tmp_path / "tau.csv"),
        "output_model_comparison": str(tmp_path / "model.csv"),
        "output_figure_dir": str(tmp_path / "figures"),
        "allow_mock_data": True,
        "mock_galaxies": ["MockA"],
    }
    cfg_path = tmp_path / "mock_cfg.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    cmd = ["python3", "scripts/run_sparc_subset.py", "--config", str(cfg_path)]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert "No observational claim can be made from mock data." in result.stdout
