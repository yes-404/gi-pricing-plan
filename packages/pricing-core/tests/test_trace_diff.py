"""`diff_traces` — the Quote Sandbox step diff (FR-262, `03` §4.10; PL-1213 Task 3)."""

from __future__ import annotations

from typing import Any

import pytest

from model_schema.refs import ArtifactRef
from model_schema.scoring import Trace, TraceDiff, TraceStep
from pricing_core.rating.trace_diff import diff_traces


def _step(step_id: str, **overrides: Any) -> TraceStep:
    fields: dict[str, Any] = {"step_id": step_id, "type": "expression", **overrides}
    return TraceStep(**fields)


def _trace(*steps: TraceStep) -> Trace:
    return Trace(
        rating_version_ref=ArtifactRef.parse("rating_version:motor-gb@1"),
        bundle_hash="sha256:" + "a" * 64,
        steps=list(steps),
        ladder_reconciled=True,
    )


def test_a_change_to_one_steps_own_definition_is_the_one_own_change() -> None:
    # s_area is unchanged; s_rate consumed the same input and produced a different value;
    # s_total consumed the moved value and so differs only by propagation.
    base = _trace(
        _step("s_area"), _step("s_rate", produced={"r": 1}), _step("s_total", consumed={"r": 1})
    )
    other = _trace(
        _step("s_area"), _step("s_rate", produced={"r": 2}), _step("s_total", consumed={"r": 2})
    )
    diff = diff_traces(base, other)
    own = [c.step_id for c in diff.steps if c.own_change]
    assert own == ["s_rate"]  # assertion 1: exactly one own change, the edited step
    assert [c.step_id for c in diff.steps] == ["s_rate", "s_total"]
    for change in diff.steps:  # assertion 2: every other entry is explained by a moved input
        if not change.own_change:
            assert "consumed" in change.changed_fields
            assert change.base is not None
            assert change.comparison is not None
            assert change.base.consumed != change.comparison.consumed
    assert diff.unchanged == 1


def test_a_downstream_steps_own_edit_is_masked_by_its_moved_input_a_known_limit() -> None:
    # KNOWN LIMITATION (auditor-b F5, 03 §4.10): s_total is itself edited (its produced value
    # differs for a reason beyond its input) AND its consumed input moved. `own_change` is
    # derived from `consumed` alone, so it reads False. This test pins the behaviour so a
    # change to it is deliberate.
    base = _trace(
        _step("s_rate", produced={"r": 1}), _step("s_total", consumed={"r": 1}, produced={"t": 10})
    )
    other = _trace(
        _step("s_rate", produced={"r": 2}), _step("s_total", consumed={"r": 2}, produced={"t": 99})
    )
    own = {c.step_id: c.own_change for c in diff_traces(base, other).steps}
    assert own == {"s_rate": True, "s_total": False}


def test_an_edit_that_feeds_nothing_that_changes_is_the_only_entry() -> None:
    # assertion 3: s_rate's produced value changes but s_total's consumed dict does not
    # carry it, so nothing downstream differs.
    base = _trace(
        _step("s_area"), _step("s_rate", produced={"r": 1}), _step("s_total", consumed={"q": 5})
    )
    other = _trace(
        _step("s_area"), _step("s_rate", produced={"r": 2}), _step("s_total", consumed={"q": 5})
    )
    diff = diff_traces(base, other)
    assert [c.step_id for c in diff.steps] == ["s_rate"]


def test_elapsed_time_never_makes_a_step_differ() -> None:
    assert (
        diff_traces(_trace(_step("a", elapsed_us=1)), _trace(_step("a", elapsed_us=900))).steps
        == []
    )


@pytest.mark.parametrize(("left", "right"), [(1, 1.0), (True, 1), (0, False)])
def test_one_and_one_point_zero_and_true_are_different_values(left: object, right: object) -> None:
    diff = diff_traces(
        _trace(_step("a", produced={"v": left})), _trace(_step("a", produced={"v": right}))
    )
    assert [(c.change, c.changed_fields) for c in diff.steps] == [("changed", ["produced"])]


def test_an_added_and_a_removed_step_are_reported_with_their_kind() -> None:
    diff = diff_traces(_trace(_step("gone"), _step("kept")), _trace(_step("kept"), _step("new")))
    assert [(c.step_id, c.change, c.own_change) for c in diff.steps] == [
        ("gone", "removed", True),
        ("new", "added", True),
    ]
    assert diff.unchanged == 1


def test_identical_traces_have_an_empty_diff() -> None:
    trace = _trace(_step("a"), _step("b"))
    assert diff_traces(trace, trace) == TraceDiff(steps=[], unchanged=2)


def test_a_duplicate_step_id_in_one_trace_is_refused() -> None:
    with pytest.raises(ValueError, match="duplicate step_id"):
        diff_traces(_trace(_step("a"), _step("a")), _trace(_step("a")))
