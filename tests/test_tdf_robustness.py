from __future__ import annotations

import numpy as np

from tdf_galaxy_tau.models.tdf_knot import smoothness_second_difference_metric
from tdf_galaxy_tau.validation.holdout import (
    all_holdout_splits,
    even_odd_radial_split,
    inner_middle_outer_split,
    mask_from_indices,
)
from tdf_galaxy_tau.validation.robustness import knot_count_stability_table, negative_v2_audit_table


def test_even_odd_split_covers_all_points() -> None:
    split = even_odd_radial_split(12)
    covered = np.sort(np.concatenate([split.train_indices, split.test_indices]))
    assert len(covered) == 12
    assert covered[0] == 0 and covered[-1] == 11


def test_inner_middle_outer_requires_enough_points() -> None:
    assert inner_middle_outer_split(8) is None
    split = inner_middle_outer_split(12)
    assert split is not None
    train_mask = mask_from_indices(12, split.train_indices)
    test_mask = mask_from_indices(12, split.test_indices)
    assert not np.any(train_mask & test_mask)


def test_kfold_only_when_enough_points() -> None:
    assert len(all_holdout_splits(10)) == 2
    assert len(all_holdout_splits(20)) >= 6


def test_smoothness_metric_finite() -> None:
    r = np.linspace(1.0, 10.0, 10)
    d = np.linspace(10.0, 50.0, 10)
    raw, norm = smoothness_second_difference_metric(r, d)
    assert np.isfinite(raw) and np.isfinite(norm)


def test_negative_v2_audit_detects_status_flag() -> None:
    import pandas as pd

    df = pd.DataFrame(
        [
            {"galaxy_id": "G1", "model_name": "tdf_4knot", "fit_success": True, "fit_status": "ok;negative_v2_regions"},
        ]
    )
    audit = negative_v2_audit_table(df)
    assert bool(audit.iloc[0]["negative_v2_flag"])


def test_knot_stability_delta_columns() -> None:
    import pandas as pd

    df = pd.DataFrame(
        [
            {"galaxy_id": "G1", "model_name": "tdf_3knot", "aic": 100.0, "bic": 105.0, "rmse_kms": 5.0},
            {"galaxy_id": "G1", "model_name": "tdf_4knot", "aic": 90.0, "bic": 98.0, "rmse_kms": 4.0, "fit_success": True, "fit_status": "ok", "reduced_chi_square": 1.0},
            {"galaxy_id": "G1", "model_name": "tdf_5knot", "aic": 80.0, "bic": 92.0, "rmse_kms": 3.0},
        ]
    )
    stab = knot_count_stability_table(df)
    assert stab.iloc[0]["delta_aic_5_minus_3"] == -20.0
