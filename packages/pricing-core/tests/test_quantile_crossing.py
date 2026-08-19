"""FR-MODEL-78's crossing detection, as arithmetic (`pricing-core`, no database).

Crossing means the pair does not describe one distribution. The requirement's word is that
it is **detected, reported, and never silently reordered** — so the thing under test here is
as much what this function refuses to do as what it computes.
"""

from __future__ import annotations

import numpy as np
import pytest

from pricing_core.modelling.predict import PredictionError, detect_quantile_crossing


@pytest.mark.req("FR-MODEL-78")
def test_an_ordered_pair_does_not_cross() -> None:
    """The ordinary case: every lower bound below its upper."""
    lower = np.array([1.0, 2.0, 3.0])
    upper = np.array([1.5, 2.5, 3.5])
    assert detect_quantile_crossing(lower, upper) == (0, 0.0)


@pytest.mark.req("FR-MODEL-78")
def test_crossing_is_counted_and_its_worst_gap_reported() -> None:
    """The count says how widespread it is; the gap says how bad the worst case is.

    Both, because either alone misleads. One crossing row in a million is a curiosity; one
    crossing row by a factor of ten is a bound nobody should quote, and a count of 1
    describes them identically.
    """
    lower = np.array([1.0, 9.0, 3.0])
    upper = np.array([1.5, 2.5, 3.5])
    rows, gap = detect_quantile_crossing(lower, upper)
    assert rows == 1
    assert gap == pytest.approx(6.5)


@pytest.mark.req("FR-MODEL-78")
def test_the_worst_gap_is_the_worst_and_not_the_last() -> None:
    """With several crossings the reported gap is the maximum over all of them.

    A running variable overwritten per row rather than maximised would pass the single
    crossing test above and report the last crossing here, which is whichever row happens
    to sort last — a number that changes when the frame is reordered.
    """
    lower = np.array([9.0, 4.0, 20.0])
    upper = np.array([1.0, 3.0, 19.0])
    rows, gap = detect_quantile_crossing(lower, upper)
    assert rows == 3
    assert gap == pytest.approx(8.0)


@pytest.mark.req("FR-MODEL-78")
def test_equal_bounds_are_not_crossing() -> None:
    """A zero-width interval is degenerate, not inverted.

    `lower == upper` says the two quantile fits agree exactly at that row, which is unusual
    and not a contradiction. Counting it would report a defect on every row where a bound is
    constant — and a constant bound is what a booster returns for a leaf with one level.
    """
    assert detect_quantile_crossing(np.array([2.0]), np.array([2.0])) == (0, 0.0)


@pytest.mark.req("FR-MODEL-78")
def test_it_never_reorders_its_inputs() -> None:
    """The requirement's own word, and the reason this returns numbers rather than a pair.

    A helper that quietly swapped the arrays would make every downstream test pass and every
    downstream interval a fiction — the exact failure OQ-MODEL-2 was decided to avoid, since
    a reordered pair still does not describe one distribution.
    """
    lower = np.array([9.0, 1.0])
    upper = np.array([2.0, 5.0])
    detect_quantile_crossing(lower, upper)
    assert lower.tolist() == [9.0, 1.0]
    assert upper.tolist() == [2.0, 5.0]


@pytest.mark.req("FR-MODEL-78")
def test_bounds_of_different_lengths_are_an_error_not_a_comparison() -> None:
    """Two arrays of different lengths were scored over different rows.

    NumPy would broadcast a length-1 array against a length-n one and return a confident
    answer about a comparison nobody made.
    """
    with pytest.raises(PredictionError) as caught:
        detect_quantile_crossing(np.array([1.0]), np.array([2.0, 3.0]))
    assert caught.value.code == "MODEL_INTERVAL_UNAVAILABLE"


@pytest.mark.req("FR-MODEL-78")
def test_an_empty_pair_reports_no_crossing_rather_than_failing() -> None:
    """Zero rows is a legitimate frame, and `max()` over an empty selection would raise."""
    assert detect_quantile_crossing(np.array([]), np.array([])) == (0, 0.0)
