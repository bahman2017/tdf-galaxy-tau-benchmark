from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_galaxy_tau.analysis.phase6b_data_availability import (
    PHASE6C_MAX_EXTRAPOLATION_FRAC,
    PHASE6C_TAU_RADIAL_MATCH_EPS_REL,
)
from tdf_galaxy_tau.analysis.phase6c_frozen_pseudo2d import (
    REQUIRED_NPZ_KEYS,
    build_frozen_pseudo2d_map,
    validate_galaxy_for_build,
    write_phase6c_outputs,
)

ROOT = Path(__file__).resolve().parents[1]
RANKING = ROOT / "outputs/tables/phase6b_pilot_candidate_ranking.csv"
NPZ = ROOT / "outputs/maps/phase6c/DDO161_frozen_pseudo2d_tau_map.npz"
META = ROOT / "outputs/tables/phase6c_DDO161_frozen_pseudo2d_map_metadata.csv"
REPORT = ROOT / "outputs/reports/phase6c_DDO161_frozen_pseudo2d_report.md"


@pytest.fixture(scope="module")
def ddo161_result():
    if not RANKING.is_file():
        pytest.skip("Phase 6B ranking missing")
    return build_frozen_pseudo2d_map("DDO161", root=ROOT)


def test_ddo161_is_primary_pilot() -> None:
    ranking = pd.read_csv(RANKING)
    row = ranking[ranking["galaxy_id"] == "DDO161"].iloc[0]
    assert bool(row["is_primary_pilot"])


def test_ngc7814_refused_without_diagnostic() -> None:
    with pytest.raises(ValueError, match="NGC7814"):
        validate_galaxy_for_build("NGC7814", ranking_path=RANKING, allow_diagnostic=False)


def test_metadata_claim_flags(ddo161_result) -> None:
    m = ddo161_result.metadata
    assert m["tau_retuned"] is False
    assert m["kg_retuned"] is False
    assert m["separate_halo_added"] is False
    assert m["lensing_confirmed"] is False
    assert m["true_2d_sigma_b"] is False


def test_npz_required_arrays(ddo161_result) -> None:
    if not NPZ.is_file():
        write_phase6c_outputs(ddo161_result, root=ROOT)
    data = np.load(NPZ)
    for key in REQUIRED_NPZ_KEYS:
        assert key in data.files, f"missing {key}"
    assert data["x_kpc"].shape == data["tau"].shape


def test_radial_consistency(ddo161_result) -> None:
    assert ddo161_result.metadata["radial_consistency_pass"] is True
    assert (
        ddo161_result.metadata["radial_consistency_max_relative_error"]
        <= PHASE6C_TAU_RADIAL_MATCH_EPS_REL
    )


def test_no_tau_beyond_extrapolation_shell(ddo161_result) -> None:
    R = ddo161_result.arrays["R_kpc"]
    tau = ddo161_result.arrays["tau"]
    r_outer = float(ddo161_result.metadata["r_outer_kpc"])
    beyond = R > r_outer + 1e-9
    assert int(np.isfinite(tau[beyond]).sum()) == 0


def test_extrapolation_shell_masked_tau(ddo161_result) -> None:
    R = ddo161_result.arrays["R_kpc"]
    tau = ddo161_result.arrays["tau"]
    valid = ddo161_result.arrays["valid_mask"]
    r_max = float(ddo161_result.metadata["r_max_kpc"])
    shell = (R > r_max) & (R <= r_max * (1 + PHASE6C_MAX_EXTRAPOLATION_FRAC))
    assert not np.any(np.isfinite(tau[shell & valid]))
    assert ddo161_result.metadata["finite_tau_beyond_extrapolation_shell"] == 0


def test_metadata_csv_fields(ddo161_result) -> None:
    write_phase6c_outputs(ddo161_result, root=ROOT, write_figure=False)
    meta = pd.read_csv(META).iloc[0]
    for col in (
        "tau_retuned",
        "kg_retuned",
        "lensing_confirmed",
        "true_2d_sigma_b",
        "claim_no_lensing_confirmation",
    ):
        assert col in meta.index
    assert meta["tau_retuned"] in (False, "False")
    assert meta["lensing_confirmed"] in (False, "False")


def test_report_phrases(ddo161_result) -> None:
    write_phase6c_outputs(ddo161_result, root=ROOT, write_figure=False)
    text = REPORT.read_text(encoding="utf-8").lower()
    assert "axisymmetric pseudo-2d" in text
    assert "no new fit" in text
    assert "no lensing confirmation" in text
    assert "does not update the phase 5 expansion_20 result" in text


def test_build_script_smoke() -> None:
    import subprocess

    proc = subprocess.run(
        [
            "python3",
            "scripts/build_phase6c_frozen_pseudo2d_map.py",
            "--galaxy-id",
            "DDO161",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
