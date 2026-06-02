"""Configuration helpers (notation aliases, etc.)."""

from tdf_galaxy_tau.config.notation import (
    ALIAS_STATUS_BOTH_EQUAL,
    ALIAS_STATUS_LEGACY_K_TAU,
    ALIAS_STATUS_PREFERRED_K_G,
    merge_projection_from_yaml_blocks,
    normalize_projection_coefficient,
)

__all__ = [
    "ALIAS_STATUS_BOTH_EQUAL",
    "ALIAS_STATUS_LEGACY_K_TAU",
    "ALIAS_STATUS_PREFERRED_K_G",
    "merge_projection_from_yaml_blocks",
    "normalize_projection_coefficient",
]
