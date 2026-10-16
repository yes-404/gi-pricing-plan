"""`diff_traces` — the Quote Sandbox step diff (FR-262, `03` §4.10; PL-1213 Task 3).

`own_change` comes from step-definition equality (`RL-1261`; SL-1549), so every call passes both
compiled algorithms alongside both traces.
"""

from __future__ import annotations

from typing import Any

import pytest

from model_schema.rating import RatingAlgorithm, diff_algorithms
from model_schema.refs import ArtifactRef
from model_schema.scoring import Trace, TraceDiff, TraceStep
from model_schema.sub_graphs import SubGraph
from pricing_core.rating.inline import inline_mounts
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


def _expr(step_id: str, expr: str = "k + 1", **overrides: Any) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "type": "expression",
        "label": step_id,
        "expr": expr,
        "result_type": "decimal",
        "consumes": ["k"],
        "produces": f"v_{step_id}",
        **overrides,
    }


def _alg(*steps: dict[str, Any]) -> RatingAlgorithm:
    """A valid algorithm of the given steps (plus an output step) over one input, `k`."""
    return RatingAlgorithm.model_validate({
        "slug": "motor-gb",
        "version": 1,
        "input_contract": [{"name": "k", "type": "int", "nullable": False}],
        "outputs": [{"name": "out", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_in_k", "type": "input", "label": "k", "input_name": "k",
             "on_missing": "error", "produces": "k"},
            *steps,
            {"step_id": "s_out", "type": "output", "label": "out", "output_name": "out",
             "rounding": {"mode": "half_even", "dp": 0},
             "consumes": [s["produces"] for s in steps]},
        ],
    })


def _table(step_id: str, ref: str) -> dict[str, Any]:
    return {"step_id": step_id, "type": "table", "label": step_id, "rate_table_ref": ref,
            "key_expr": ["k"], "on_miss": "default", "consumes": ["k"], "produces": f"v_{step_id}"}


SAME = _alg(_expr("s_area"), _expr("s_rate"), _expr("s_total"))


def _own(base: Trace, other: Trace, base_alg: RatingAlgorithm, other_alg: RatingAlgorithm):
    return {c.step_id: c.own_change for c in diff_traces(base, other, base_alg, other_alg).steps}



def test_a_change_to_one_steps_own_definition_is_the_one_own_change() -> None:
    # s_area is unchanged; s_rate's definition changed and it produced a different value;
    # s_total's definition is unchanged and it differs only because its input moved.
    base = _trace(
        _step("s_area"), _step("s_rate", produced={"r": 1}), _step("s_total", consumed={"r": 1})
    )
    other = _trace(
        _step("s_area"), _step("s_rate", produced={"r": 2}), _step("s_total", consumed={"r": 2})
    )
    edited = _alg(_expr("s_area"), _expr("s_rate", "k + 2"), _expr("s_total"))
    diff = diff_traces(base, other, SAME, edited)
    own = [c.step_id for c in diff.steps if c.own_change]
    assert own == ["s_rate"]  # exactly one own change, the edited step
    assert [c.step_id for c in diff.steps] == ["s_rate", "s_total"]
    for change in diff.steps:  # every other entry is explained by a moved input
        if not change.own_change:
            assert "consumed" in change.changed_fields
            assert change.base is not None
            assert change.comparison is not None
            assert change.base.consumed != change.comparison.consumed
    assert diff.unchanged == 1


def test_a_downstream_steps_own_edit_is_not_masked_by_its_moved_input() -> None:
    # RL-1261 / auditor-b F5: s_total is itself edited AND its consumed input moved. The old
    # trace-derived rule read False here; the step definition differs, so it reads True.
    base = _trace(
        _step("s_rate", produced={"r": 1}), _step("s_total", consumed={"r": 1}, produced={"t": 10})
    )
    other = _trace(
        _step("s_rate", produced={"r": 2}), _step("s_total", consumed={"r": 2}, produced={"t": 99})
    )
    edited = _alg(_expr("s_rate", "k + 2"), _expr("s_total", "k + 99"))
    assert _own(base, other, _alg(_expr("s_rate"), _expr("s_total")), edited) == {
        "s_rate": True,
        "s_total": True,
    }


def test_a_downstream_step_with_an_unchanged_definition_and_a_moved_input_is_not_own() -> None:
    base = _trace(_step("s_rate", produced={"r": 1}), _step("s_total", consumed={"r": 1}))
    other = _trace(_step("s_rate", produced={"r": 2}), _step("s_total", consumed={"r": 2}))
    edited = _alg(_expr("s_rate", "k + 2"), _expr("s_total"))
    assert _own(base, other, _alg(_expr("s_rate"), _expr("s_total")), edited) == {
        "s_rate": True,
        "s_total": False,
    }


def test_an_own_change_with_identical_consumed_reads_false_when_the_definition_is_unchanged() -> (
    None
):
    # The mirror of the old rule: `consumed` identical used to mean own_change True. With the
    # definitions equal (the trace differs for another reason) it reads False.
    base = _trace(_step("s_rate", produced={"r": 1}))
    other = _trace(_step("s_rate", produced={"r": 2}))
    assert _own(base, other, SAME, SAME) == {"s_rate": False}


def test_a_note_only_edit_on_a_step_listed_through_consumed_reads_false() -> None:
    # RL-1261 negative 3: `note` is excluded at this call site, though diff_algorithms counts it.
    base = _trace(_step("s_rate", consumed={"r": 1}))
    other = _trace(_step("s_rate", consumed={"r": 2}))
    noted = _alg(_expr("s_area"), _expr("s_rate", note="documented"), _expr("s_total"))
    assert any(c.field == "note" for c in diff_algorithms(SAME, noted).changed_steps)
    assert _own(base, other, SAME, noted) == {"s_rate": False}


def test_a_label_edit_reads_true() -> None:
    # RL-1261: `label` stays compared.
    base = _trace(_step("s_rate", label="Rate"))
    other = _trace(_step("s_rate", label="Rate v2"))
    relabelled = _alg(_expr("s_area"), _expr("s_rate", label="Rate v2"), _expr("s_total"))
    assert _own(base, other, SAME, relabelled) == {"s_rate": True}


def test_a_changed_rate_table_ref_gives_exactly_one_own_change() -> None:
    # RL-1261 negative 5 / RL-1172 section 5: the table step is the one own change, the step
    # that consumes its output differs only through its input.
    use = _expr("s_use", "v_s_tab + 1", consumes=["v_s_tab"])
    old = _alg(_table("s_tab", "rate_table:motor-expense@3"), use)
    new = _alg(_table("s_tab", "rate_table:motor-expense@4"), use)
    base = _trace(_step("s_tab", produced={"f": 1}), _step("s_use", consumed={"f": 1}))
    other = _trace(_step("s_tab", produced={"f": 2}), _step("s_use", consumed={"f": 2}))
    diff = diff_traces(base, other, old, new)
    assert [c.step_id for c in diff.steps if c.own_change] == ["s_tab"]
    assert [c.step_id for c in diff.steps] == ["s_tab", "s_use"]


@pytest.mark.parametrize("edit", ["expr", "label", "note"])
def test_own_change_agrees_with_diff_algorithms_except_for_note(edit: str) -> None:
    # RL-1261 negative 4: for a step listed by the traces, own_change is "diff_algorithms
    # reports a non-note field for it".
    overrides = {"expr": {"expr": "k + 7"}, "label": {"label": "New"}, "note": {"note": "n"}}[edit]
    edited = _alg(_expr("s_area"), _expr("s_rate", **overrides), _expr("s_total"))
    reported = {
        c.step_id for c in diff_algorithms(SAME, edited).changed_steps if c.field != "note"
    }
    base = _trace(_step("s_rate", consumed={"r": 1}))
    other = _trace(_step("s_rate", consumed={"r": 2}))
    assert _own(base, other, SAME, edited)["s_rate"] == ("s_rate" in reported)


def test_an_edit_that_feeds_nothing_that_changes_is_the_only_entry() -> None:
    # s_rate's produced value changes but s_total's consumed dict does not carry it, so nothing
    # downstream differs.
    base = _trace(
        _step("s_area"), _step("s_rate", produced={"r": 1}), _step("s_total", consumed={"q": 5})
    )
    other = _trace(
        _step("s_area"), _step("s_rate", produced={"r": 2}), _step("s_total", consumed={"q": 5})
    )
    edited = _alg(_expr("s_area"), _expr("s_rate", "k + 2"), _expr("s_total"))
    diff = diff_traces(base, other, SAME, edited)
    assert [c.step_id for c in diff.steps] == ["s_rate"]


def _fragment(expr: str, cap: int = 50) -> SubGraph:
    return SubGraph.model_validate({
        "slug": "ncd-ladder", "version": 4,
        "inputs": [{"name": "ncd_years", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_ladder", "type": "expression", "label": "Ladder", "expr": expr,
             "result_type": "decimal", "consumes": ["ncd_years"], "produces": "ncd_raw"},
            {"step_id": "s_cap", "type": "expression", "label": "Cap",
             "expr": f"min([ncd_raw, {cap}])", "result_type": "decimal",
             "consumes": ["ncd_raw"], "produces": "ncd_factor"},
        ],
        "change_note": "cut",
    })


def _mounted_parent() -> RatingAlgorithm:
    return RatingAlgorithm.model_validate({
        "slug": "motor-gb", "version": 1,
        "input_contract": [{"name": "years", "type": "int", "nullable": False}],
        "outputs": [{"name": "premium", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_in_years", "type": "input", "label": "years", "input_name": "years",
             "on_missing": "error", "produces": "years"},
            {"step_id": "s_out", "type": "output", "label": "Premium", "output_name": "premium",
             "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["ncd_factor"]},
        ],
        "sub_graphs": [{"ref": "sub_graph:ncd-ladder@4", "mount_point": "m_ncd",
                        "inputs": {"ncd_years": "years"}, "outputs": {"ncd_factor": "ncd_factor"}}],
    })


def test_a_namespaced_step_inside_a_mounted_sub_graph_is_compared_by_its_namespaced_id() -> None:
    # R7b.1 (SL-1340 merged): the compiled algorithm is the inlined one, so the fragment's edited
    # step reads own_change by `m_ncd__s_ladder`, and the unedited `m_ncd__s_cap`, whose input
    # moved, does not.
    parent = _mounted_parent()
    old = inline_mounts(parent, {"sub_graph:ncd-ladder@4": _fragment("ncd_years * 10")})
    new = inline_mounts(parent, {"sub_graph:ncd-ladder@4": _fragment("ncd_years * 12")})
    base = _trace(
        _step("m_ncd__s_ladder", produced={"ncd_raw": 10}),
        _step("m_ncd__s_cap", consumed={"ncd_raw": 10}, produced={"ncd_factor": 10}),
    )
    other = _trace(
        _step("m_ncd__s_ladder", produced={"ncd_raw": 12}),
        _step("m_ncd__s_cap", consumed={"ncd_raw": 12}, produced={"ncd_factor": 12}),
    )
    assert _own(base, other, old, new) == {"m_ncd__s_ladder": True, "m_ncd__s_cap": False}


def test_an_edited_namespaced_step_whose_input_also_moved_reads_true() -> None:
    # LOW 2 (SL-1549 audit): the old `consumed` rule and definition equality DISAGREE here.
    # `m_ncd__s_cap`'s cap is edited AND its input moved (the ladder was edited too), so the old
    # rule read False; its definition differs, so it reads True.
    parent = _mounted_parent()
    old = inline_mounts(parent, {"sub_graph:ncd-ladder@4": _fragment("ncd_years * 10", 50)})
    new = inline_mounts(parent, {"sub_graph:ncd-ladder@4": _fragment("ncd_years * 12", 40)})
    base = _trace(
        _step("m_ncd__s_ladder", produced={"ncd_raw": 10}),
        _step("m_ncd__s_cap", consumed={"ncd_raw": 10}, produced={"ncd_factor": 10}),
    )
    other = _trace(
        _step("m_ncd__s_ladder", produced={"ncd_raw": 12}),
        _step("m_ncd__s_cap", consumed={"ncd_raw": 12}, produced={"ncd_factor": 12}),
    )
    assert _own(base, other, old, new) == {"m_ncd__s_ladder": True, "m_ncd__s_cap": True}


def test_elapsed_time_never_makes_a_step_differ() -> None:
    assert (
        diff_traces(
            _trace(_step("a", elapsed_us=1)), _trace(_step("a", elapsed_us=900)), SAME, SAME
        ).steps
        == []
    )


@pytest.mark.parametrize(("left", "right"), [(1, 1.0), (True, 1), (0, False)])
def test_one_and_one_point_zero_and_true_are_different_values(left: object, right: object) -> None:
    diff = diff_traces(
        _trace(_step("a", produced={"v": left})),
        _trace(_step("a", produced={"v": right})),
        SAME,
        SAME,
    )
    assert [(c.change, c.changed_fields) for c in diff.steps] == [("changed", ["produced"])]


def test_an_added_and_a_removed_step_are_reported_with_their_kind() -> None:
    old = _alg(_expr("gone"), _expr("kept"))
    new = _alg(_expr("kept"), _expr("new"))
    diff = diff_traces(
        _trace(_step("gone"), _step("kept")), _trace(_step("kept"), _step("new")), old, new
    )
    assert [(c.step_id, c.change, c.own_change) for c in diff.steps] == [
        ("gone", "removed", True),
        ("new", "added", True),
    ]
    assert diff.unchanged == 1


def test_identical_traces_have_an_empty_diff() -> None:
    trace = _trace(_step("a"), _step("b"))
    assert diff_traces(trace, trace, SAME, SAME) == TraceDiff(steps=[], unchanged=2)


def test_a_duplicate_step_id_in_one_trace_is_refused() -> None:
    with pytest.raises(ValueError, match="duplicate step_id"):
        diff_traces(_trace(_step("a"), _step("a")), _trace(_step("a")), SAME, SAME)
