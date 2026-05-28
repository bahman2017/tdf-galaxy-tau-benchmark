from dataclasses import dataclass


REQUIRED_COLUMNS = [
    "galaxy_id",
    "r_kpc",
    "v_obs_kms",
    "v_err_kms",
    "v_gas_kms",
    "v_disk_kms",
    "v_bulge_kms",
]


@dataclass(frozen=True)
class SparcSchema:
    """Unit-explicit SPARC-like row schema used by the scaffold pipeline."""

    galaxy_id: str
    r_kpc: float
    v_obs_kms: float
    v_err_kms: float
    v_gas_kms: float
    v_disk_kms: float
    v_bulge_kms: float
