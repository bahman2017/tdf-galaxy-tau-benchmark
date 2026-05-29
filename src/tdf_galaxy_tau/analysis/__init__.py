"""Exploratory analysis utilities (normalized τ-pattern discovery, etc.)."""

from tdf_galaxy_tau.analysis.ngc7814_diagnostics import run_ngc7814_diagnostics
from tdf_galaxy_tau.analysis.normalized_patterns import (
    DEFAULT_X_GRID,
    build_normalized_tau_patterns,
    build_outlier_scores,
    build_similarity_matrix,
    run_normalized_pattern_analysis,
    write_normalized_pattern_report,
)

__all__ = [
    "run_ngc7814_diagnostics",
    "DEFAULT_X_GRID",
    "build_normalized_tau_patterns",
    "build_similarity_matrix",
    "build_outlier_scores",
    "run_normalized_pattern_analysis",
    "write_normalized_pattern_report",
]
