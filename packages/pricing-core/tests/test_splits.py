"""Deterministic partitioning (`01` FR-DATA-33, FR-DATA-36).

The property under test is not "a split runs". It is that **two independent calls agree** —
the `train` Job and the `test` Job never meet, and a holdout that overlaps its training set
reports the model's memory as its performance.
"""

from __future__ import annotations

import polars as pl
import pytest

from pricing_core.data.splits import SplitError, assign_folds, assign_parts, partition


def _book(n: int = 1000) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "row": list(range(n)),
            "policy": [f"P{i // 5}" for i in range(n)],
            "inception": ["2025-01-15"] * (n // 2) + ["2025-11-15"] * (n - n // 2),
        }
    )


@pytest.mark.req("FR-DATA-33")
def test_two_independent_calls_produce_the_same_partition() -> None:
    """The whole point. The parts are derived by separate Jobs, in separate processes,
    sharing only the seed — so the assignment must be a function of the seed and nothing
    else, including anything stored between the calls."""
    frame = _book()
    first = assign_parts(frame, method="random", seed=99, fractions={"train": 0.8, "test": 0.2})
    second = assign_parts(frame, method="random", seed=99, fractions={"train": 0.8, "test": 0.2})
    assert first.to_list() == second.to_list()


@pytest.mark.req("FR-DATA-33")
def test_a_different_seed_produces_a_different_partition() -> None:
    """Negative of the above: if the seed did not matter, determinism would be trivially
    satisfied by ignoring it, and every split would be the same split."""
    frame = _book()
    a = assign_parts(frame, method="random", seed=1, fractions={"train": 0.8, "test": 0.2})
    b = assign_parts(frame, method="random", seed=2, fractions={"train": 0.8, "test": 0.2})
    assert a.to_list() != b.to_list()


@pytest.mark.req("FR-DATA-36")
def test_the_parts_are_disjoint_and_cover_every_row() -> None:
    """A row in both parts inflates the holdout; a row in neither is silently discarded.
    Both are failures a row count alone would not reveal, so the identity is checked."""
    frame = _book()
    parts = partition(frame, method="random", seed=7, fractions={"train": 0.75, "test": 0.25})
    train = set(parts["train"]["row"].to_list())
    test = set(parts["test"]["row"].to_list())
    assert train.isdisjoint(test)
    assert train | test == set(range(frame.height))


@pytest.mark.req("FR-DATA-36")
def test_a_grouped_split_keeps_a_policy_whole() -> None:
    """The leakage bug this method exists to prevent: a policy with twelve monthly rows
    split across train and holdout lets the model see the very risk it is scored on."""
    frame = _book()
    parts = partition(
        frame,
        method="grouped_by_key",
        seed=3,
        key_column="policy",
        fractions={"train": 0.7, "test": 0.3},
    )
    train = set(parts["train"]["policy"].to_list())
    test = set(parts["test"]["policy"].to_list())
    assert train.isdisjoint(test)


@pytest.mark.req("FR-DATA-33")
def test_a_temporal_split_puts_the_later_rows_in_the_holdout() -> None:
    frame = _book()
    parts = partition(
        frame, method="temporal", seed=0, time_column="inception", cutoff="2025-07-01"
    )
    assert set(parts["train"]["inception"].to_list()) == {"2025-01-15"}
    assert set(parts["test"]["inception"].to_list()) == {"2025-11-15"}


@pytest.mark.req("FR-DATA-33")
def test_fractions_that_do_not_cover_the_data_are_refused() -> None:
    """Negative: 0.5/0.2 leaves 30 % of the book in no part at all — rows dropped with no
    error, which is the one thing a holdout cannot survive."""
    with pytest.raises(SplitError, match="do not cover"):
        partition(_book(), method="random", seed=1, fractions={"train": 0.5, "test": 0.2})


@pytest.mark.req("FR-DATA-33")
def test_a_temporal_split_without_a_cutoff_is_refused() -> None:
    """Negative: falling back to a random partition would record `method: temporal` on a
    split that is not temporal — a method recorded as one it is not."""
    with pytest.raises(SplitError, match="time_column"):
        partition(_book(), method="temporal", seed=1)


@pytest.mark.req("FR-DATA-33")
def test_an_unknown_method_is_refused() -> None:
    with pytest.raises(SplitError, match="unknown split method"):
        partition(_book(), method="stratified_by_vibes", seed=1)


@pytest.mark.req("FR-MODEL-53")
def test_two_independent_calls_produce_the_same_fold_assignment() -> None:
    """The property `assign_parts` exists for, carried to folds: two Jobs computing CV for
    the same spec must agree on which rows are held out for fold `i`, and the only thing
    they share is `method`, `seed` and `folds`."""
    frame = _book()
    first = assign_folds(frame, method="random", seed=11, folds=4)
    second = assign_folds(frame, method="random", seed=11, folds=4)
    assert first.tolist() == second.tolist()


@pytest.mark.req("FR-MODEL-53")
def test_a_different_seed_produces_a_different_fold_assignment() -> None:
    frame = _book()
    a = assign_folds(frame, method="random", seed=1, folds=4)
    b = assign_folds(frame, method="random", seed=2, folds=4)
    assert a.tolist() != b.tolist()


@pytest.mark.req("FR-MODEL-53")
def test_every_row_gets_one_of_the_declared_folds() -> None:
    """Coverage, the fold equivalent of `test_the_parts_are_disjoint_and_cover_every_row`:
    a row with no fold is a row `_fit_cv_path` would silently never score or never train
    on, in whichever fold it should have belonged to."""
    frame = _book()
    folds = assign_folds(frame, method="random", seed=5, folds=4)
    assert folds.shape == (frame.height,)
    assert set(folds.tolist()) == {0, 1, 2, 3}
    assert folds.min() >= 0
    assert folds.max() < 4


@pytest.mark.req("FR-MODEL-53")
def test_a_grouped_fold_assignment_keeps_a_policy_whole() -> None:
    """The same leakage bug `assign_parts`'s grouped method exists to prevent, at K folds:
    a policy's twelve monthly rows split across two folds lets a model trained on fold A
    see rows from the very policy fold B holds out."""
    frame = _book()
    folds = assign_folds(frame, method="grouped_by_key", seed=3, folds=4, key_column="policy")
    tagged = frame.with_columns(pl.Series("fold", folds.tolist()))
    per_policy_fold_count = (
        tagged.group_by("policy").agg(pl.col("fold").n_unique().alias("n")).select("n")
    )
    assert per_policy_fold_count["n"].max() == 1


@pytest.mark.req("FR-MODEL-53")
def test_a_grouped_fold_assignment_without_a_key_column_is_refused() -> None:
    """Negative: `grouped_by_key` with no key to group by would hash row indices — a
    random fold by another name, recorded as a method the data was not folded by."""
    with pytest.raises(SplitError, match="key_column"):
        assign_folds(_book(), method="grouped_by_key", seed=1, folds=4)


@pytest.mark.req("FR-MODEL-53")
def test_a_grouped_fold_assignment_naming_a_missing_column_is_refused() -> None:
    """Negative: a key column the frame does not carry is a typo, not a grouping — every
    row would hash to its own singleton key, again a random fold in disguise."""
    with pytest.raises(SplitError, match="which is not a column"):
        assign_folds(_book(), method="grouped_by_key", seed=1, folds=4, key_column="policy_no")


@pytest.mark.req("FR-MODEL-53")
def test_a_temporal_fold_assignment_orders_folds_by_time() -> None:
    """The gap this plan documents and resolves: FR-DATA-33/FR-MODEL-53 define no K-fold
    temporal semantics, so this fixes it as contiguous time-ordered blocks — the earliest
    rows land in fold 0, the latest in the last fold, and a block never straddles a fold
    boundary out of time order."""
    n = 400
    frame = pl.DataFrame({"row": list(range(n)), "day": list(range(n))})
    folds = assign_folds(frame, method="temporal", seed=0, folds=4, time_column="day")
    tagged = frame.with_columns(pl.Series("fold", folds.tolist())).sort("day")
    # Each fold's rows are a contiguous run once sorted by time: 3 boundaries between the
    # 4 folds. The leading "no previous" row compares against null, which is null in Polars
    # and so does not add to the count.
    changes = (tagged["fold"] != tagged["fold"].shift(1)).sum()
    assert changes == 3
    assert tagged["fold"][0] == 0
    assert tagged["fold"][-1] == 3


@pytest.mark.req("FR-MODEL-53")
def test_a_temporal_fold_assignment_without_a_time_column_is_refused() -> None:
    with pytest.raises(SplitError, match="time_column"):
        assign_folds(_book(), method="temporal", seed=1, folds=4)


@pytest.mark.req("FR-MODEL-53")
def test_a_temporal_fold_assignment_naming_a_missing_column_is_refused() -> None:
    """Negative: a time column the frame does not carry is a typo, not a fold order."""
    with pytest.raises(SplitError, match="which is not a column"):
        assign_folds(_book(), method="temporal", seed=1, folds=4, time_column="inception_date")


@pytest.mark.req("FR-MODEL-53")
def test_fewer_than_two_folds_is_refused() -> None:
    """Negative: one fold has no held-out rows for itself to be scored against, and
    `_fit_cv_path` would divide the book into a training set with nothing to validate on."""
    with pytest.raises(SplitError, match="at least 2"):
        assign_folds(_book(), method="random", seed=1, folds=1)


@pytest.mark.req("FR-MODEL-53")
def test_an_unknown_fold_method_is_refused() -> None:
    with pytest.raises(SplitError, match="unknown split method"):
        assign_folds(_book(), method="stratified_by_vibes", seed=1, folds=3)
