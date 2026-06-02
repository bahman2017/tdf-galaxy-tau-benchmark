"""TDF notation aliases: K_g (projection) vs legacy K_tau vs kappa_tau (field stiffness)."""

from __future__ import annotations

import math
import warnings
from collections.abc import Mapping
from typing import Any

# Gravitational projection coefficient (radial closure).
PROJECTION_KEYS_PREFERRED: tuple[str, ...] = ("k_g", "K_g")
PROJECTION_KEYS_LEGACY: tuple[str, ...] = ("k_tau", "K_tau")

# Mother-field dynamical stiffness — must never substitute for K_g.
FORBIDDEN_PROJECTION_KEYS: tuple[str, ...] = ("kappa_tau", "Kappa_tau", "κ_tau")

ALIAS_STATUS_PREFERRED_K_G = "preferred_k_g"
ALIAS_STATUS_LEGACY_K_TAU = "legacy_k_tau"
ALIAS_STATUS_BOTH_EQUAL = "both_equal"


def _first_present(mapping: Mapping[str, Any], keys: tuple[str, ...]) -> tuple[str | None, Any]:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return key, mapping[key]
    return None, None


def _coerce_positive(value: Any, key: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be a positive number; got {value!r}") from exc
    if out <= 0.0 or not math.isfinite(out):
        raise ValueError(f"{key} must be positive and finite; got {out}")
    return out


def normalize_projection_coefficient(
    config_or_mapping: Mapping[str, Any],
    *,
    context: str = "",
) -> dict[str, Any]:
    """Resolve gravitational projection coefficient from config keys.

    Preferred: ``k_g`` / ``K_g``. Legacy: ``k_tau`` / ``K_tau`` (maps to ``k_g``).
    ``kappa_tau`` / ``κ_tau`` is field stiffness and is never used as projection.
    """
    if not isinstance(config_or_mapping, Mapping):
        raise TypeError("config_or_mapping must be a mapping")

    mapping = dict(config_or_mapping)
    prefix = f"{context}: " if context else ""

    has_projection = any(k in mapping for k in (*PROJECTION_KEYS_PREFERRED, *PROJECTION_KEYS_LEGACY))
    has_forbidden = any(k in mapping for k in FORBIDDEN_PROJECTION_KEYS)
    if has_forbidden and not has_projection:
        raise ValueError(
            f"{prefix}kappa_tau is dynamical field stiffness in the mother field equation, "
            "not the gravitational projection coefficient K_g. "
            "Provide k_g/K_g or legacy k_tau/K_tau for radial reconstruction."
        )

    kg_key, kg_val = _first_present(mapping, PROJECTION_KEYS_PREFERRED)
    kt_key, kt_val = _first_present(mapping, PROJECTION_KEYS_LEGACY)

    if kg_val is not None and kt_val is not None:
        k_g = _coerce_positive(kg_val, kg_key or "k_g")
        k_tau_legacy = _coerce_positive(kt_val, kt_key or "k_tau")
        if not math.isclose(k_g, k_tau_legacy, rel_tol=0.0, abs_tol=0.0):
            raise ValueError(
                f"{prefix}Conflicting projection coefficients: "
                f"{kg_key}={k_g} vs {kt_key}={k_tau_legacy}. "
                "Use one notation or ensure both values are equal."
            )
        alias_status = ALIAS_STATUS_BOTH_EQUAL
        legacy_projection_alias = True
        source = f"{kg_key}+{kt_key}"
    elif kg_val is not None:
        k_g = _coerce_positive(kg_val, kg_key or "k_g")
        alias_status = ALIAS_STATUS_PREFERRED_K_G
        legacy_projection_alias = False
        source = str(kg_key)
    elif kt_val is not None:
        k_g = _coerce_positive(kt_val, kt_key or "k_tau")
        alias_status = ALIAS_STATUS_LEGACY_K_TAU
        legacy_projection_alias = True
        source = str(kt_key)
    else:
        raise ValueError(
            f"{prefix}Missing projection coefficient. "
            "Provide k_g/K_g (preferred) or legacy k_tau/K_tau."
        )

    return {
        "k_g": k_g,
        "k_tau": k_g,
        "K_g": k_g,
        "K_tau": k_g,
        "projection_coefficient_source": source,
        "legacy_projection_alias": legacy_projection_alias,
        "alias_status": alias_status,
    }


def merge_projection_from_yaml_blocks(*blocks: Mapping[str, Any] | None) -> dict[str, Any]:
    """Merge YAML block dicts (later overrides earlier) and normalize projection."""
    merged: dict[str, Any] = {}
    for block in blocks:
        if not block:
            continue
        for key, value in block.items():
            if isinstance(value, dict):
                continue
            merged[key] = value
    return normalize_projection_coefficient(merged)


def resolve_projection_coefficient_kwarg(
    *,
    k_g: float | None = None,
    k_tau: float | None = None,
    context: str = "",
) -> float:
    """Resolve ``k_g`` from primary and/or deprecated ``k_tau`` keyword arguments."""
    prefix = f"{context}: " if context else ""
    if k_g is not None and k_tau is not None:
        kg = float(k_g)
        kt = float(k_tau)
        if not math.isclose(kg, kt, rel_tol=0.0, abs_tol=0.0):
            raise ValueError(
                f"{prefix}Conflicting projection coefficients: k_g={kg} vs k_tau={kt}"
            )
        return kg
    if k_g is not None:
        return float(k_g)
    if k_tau is not None:
        warnings.warn(
            "k_tau is deprecated; use k_g for the gravitational projection coefficient K_g",
            DeprecationWarning,
            stacklevel=3,
        )
        return float(k_tau)
    raise TypeError(f"{prefix}missing required projection coefficient keyword: k_g")
