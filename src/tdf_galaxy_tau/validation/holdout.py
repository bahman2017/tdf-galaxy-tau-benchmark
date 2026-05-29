from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class HoldoutSplit:
    name: str
    train_indices: np.ndarray
    test_indices: np.ndarray


def even_odd_radial_split(n_points: int) -> HoldoutSplit:
    """Deterministic even-index train, odd-index test after sorting by radius."""
    train = np.arange(0, n_points, 2, dtype=int)
    test = np.arange(1, n_points, 2, dtype=int)
    return HoldoutSplit("even_odd_index", train, test)


def inner_middle_outer_split(n_points: int, *, min_points: int = 9) -> HoldoutSplit | None:
    """Blocked split: middle third test, inner+outer train. Requires enough points."""
    if n_points < min_points:
        return None
    third = n_points // 3
    if third < 2:
        return None
    test = np.arange(third, 2 * third, dtype=int)
    train = np.concatenate([np.arange(0, third), np.arange(2 * third, n_points)])
    return HoldoutSplit("inner_middle_outer_blocked", train.astype(int), test.astype(int))


def radial_kfold_splits(n_points: int, k: int = 5, *, min_points: int = 15) -> list[HoldoutSplit]:
    """Deterministic contiguous radial blocks as CV folds."""
    if n_points < min_points or k < 2:
        return []
    fold_sizes = [n_points // k] * k
    for i in range(n_points % k):
        fold_sizes[i] += 1
    splits: list[HoldoutSplit] = []
    start = 0
    for fold_id, size in enumerate(fold_sizes):
        test = np.arange(start, start + size, dtype=int)
        train = np.concatenate([np.arange(0, start), np.arange(start + size, n_points)])
        splits.append(HoldoutSplit(f"radial_kfold_{k}_fold{fold_id + 1}", train.astype(int), test.astype(int)))
        start += size
    return splits


def all_holdout_splits(n_points: int) -> list[HoldoutSplit]:
    """Collect applicable deterministic splits for a galaxy."""
    splits: list[HoldoutSplit] = [even_odd_radial_split(n_points)]
    blocked = inner_middle_outer_split(n_points)
    if blocked is not None:
        splits.append(blocked)
    splits.extend(radial_kfold_splits(n_points, k=5))
    return splits


def mask_from_indices(n_points: int, indices: np.ndarray) -> np.ndarray:
    m = np.zeros(n_points, dtype=bool)
    m[np.asarray(indices, dtype=int)] = True
    return m


def radial_region_label_for_index(n_points: int, index: int) -> str:
    """Inner/middle/outer third by sorted radial index (0 = innermost)."""
    if n_points < 3:
        return "inner"
    third = n_points // 3
    idx = int(index)
    if idx < third:
        return "inner"
    if idx < 2 * third:
        return "middle"
    return "outer"


def fold_id_from_split_name(split_name: str) -> str:
    """Stable fold identifier for exported holdout rows."""
    if split_name == "even_odd_index":
        return "even_odd"
    if split_name == "inner_middle_outer_blocked":
        return "blocked"
    if split_name.startswith("radial_kfold_"):
        return split_name.split("_fold")[-1] if "_fold" in split_name else split_name
    return split_name
