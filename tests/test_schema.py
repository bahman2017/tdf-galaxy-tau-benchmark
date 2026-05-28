import pandas as pd
import pytest

from tdf_galaxy_tau.data.validation import validate_sparc_like_dataframe


def test_schema_validation_accepts_unit_explicit_frame() -> None:
    frame = pd.DataFrame(
        {
            "galaxy_id": ["G1"],
            "r_kpc": [1.0],
            "v_obs_kms": [100.0],
            "v_err_kms": [5.0],
            "v_gas_kms": [20.0],
            "v_disk_kms": [50.0],
            "v_bulge_kms": [10.0],
        }
    )
    validate_sparc_like_dataframe(frame)


def test_schema_validation_requires_unit_columns() -> None:
    frame = pd.DataFrame({"galaxy_id": ["G1"], "radius": [1.0]})
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_sparc_like_dataframe(frame)
