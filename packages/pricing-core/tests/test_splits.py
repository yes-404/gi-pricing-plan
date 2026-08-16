"""Deterministic partitioning (`01` FR-DATA-33, FR-DATA-36).

The property under test is not "a split runs". It is that **two independent calls agree** —
the `train` Job and the `test` Job never meet, and a holdout that overlaps its training set
reports the model's memory as its performance.
"""

from __future__ import annotations

import polars as pl
import pytest

from pricing_core.data.splits import SplitError, assign_parts, partition


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
