"""`graph_invariant_issues` — every graph breach, located (RL-1474 items 2 and 4; FR-212/214/215).

The save path raises on the first breach; the validate route reports all of them. One
function holds the rules, so these tests pin its order, its skips and its locations.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from model_schema import RatingAlgorithm, RatingAlgorithmDraft, graph_invariant_issues


def _input(step_id: str, name: str) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "type": "input",
        "label": step_id,
        "input_name": name,
        "on_missing": "error",
        "produces": name,
    }


def _expr(step_id: str, consumes: list[str], produces: str) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "type": "expression",
        "label": step_id,
        "expr": "x",
        "result_type": "int",
        "consumes": consumes,
        "produces": produces,
    }


def _output(step_id: str, name: str, consumes: str) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "type": "output",
        "label": step_id,
        "output_name": name,
        "rounding": {"mode": "half_even", "dp": 0},
        "consumes": [consumes],
    }


def _draft(steps: list[dict[str, Any]], outputs: list[str] | None = None) -> RatingAlgorithmDraft:
    names = {s["input_name"] for s in steps if s["type"] == "input"}
    return RatingAlgorithmDraft.model_validate(
        {
            "slug": "motor-gb",
            "version": 1,
            "input_contract": [
                {"name": n, "type": "int", "nullable": False} for n in sorted(names)
            ],
            "outputs": [{"name": n, "type": "int", "required": True} for n in (outputs or ["out"])],
            "steps": steps,
        }
    )


def _cycle(prefix: str = "s") -> list[dict[str, Any]]:
    return [_expr(f"{prefix}_a", ["b"], "a"), _expr(f"{prefix}_b", ["a"], "b")]


def _valid_steps() -> list[dict[str, Any]]:
    return [_input("s_in", "x"), _output("s_out", "out", "x")]


@pytest.mark.req("FR-212")
def test_a_valid_graph_has_no_issue() -> None:
    assert graph_invariant_issues(_draft(_valid_steps())) == []


@pytest.mark.req("FR-215")
def test_a_duplicate_step_id_is_the_only_issue_even_with_a_cycle() -> None:
    steps = [*_valid_steps(), _input("s_dup", "y"), _input("s_dup", "z"), *_cycle()]
    issues = graph_invariant_issues(_draft(steps))
    assert [(i.code, i.step_id) for i in issues] == [("VALIDATION_FAILED", "s_dup")]


@pytest.mark.req("FR-212")
def test_a_cycle_names_only_the_steps_on_it() -> None:
    steps = [
        *_cycle(),
        _expr("s_c", ["a"], "c"),  # downstream of the cycle, not on it
        _output("s_out", "out", "c"),
    ]
    issues = graph_invariant_issues(_draft(steps))
    cyclic = {i.step_id for i in issues if i.code == "RATING_GRAPH_CYCLIC"}
    assert cyclic == {"s_a", "s_b"}


@pytest.mark.req("FR-212")
def test_no_ambiguous_producer_issue_after_a_cycle() -> None:
    steps = [*_valid_steps(), _input("s_in2", "x"), *_cycle()]  # two unchained producers of x
    issues = graph_invariant_issues(_draft(steps))
    assert any(i.code == "RATING_GRAPH_CYCLIC" for i in issues)
    assert all("re-production chain" not in i.message for i in issues)


@pytest.mark.req("FR-212")
def test_two_unchained_producers_are_ambiguous_when_there_is_no_cycle() -> None:
    steps = [*_valid_steps(), _input("s_in2", "x")]
    issues = graph_invariant_issues(_draft(steps))
    ambiguous = [i.step_id for i in issues if "re-production chain" in i.message]
    assert len(ambiguous) == 1
    assert ambiguous[0] in {"s_in", "s_in2"}


@pytest.mark.req("FR-212")
def test_every_breach_is_reported_not_the_first() -> None:
    steps = [*_valid_steps(), _expr("s_consumer", ["ghost"], "g"), _expr("s_orphan", [], "z")]
    found = [(i.code, i.step_id) for i in graph_invariant_issues(_draft(steps))]
    assert ("RATING_GRAPH_UNRESOLVED_REF", "s_consumer") in found
    assert ("VALIDATION_FAILED", "s_orphan") in found


@pytest.mark.req("FR-214")
def test_a_declared_output_without_an_output_step_has_no_step_id() -> None:
    issues = graph_invariant_issues(_draft(_valid_steps(), outputs=["out", "missing"]))
    assert [(i.code, i.step_id) for i in issues] == [("VALIDATION_FAILED", None)]
    assert "FR-214" in issues[0].message


def _mount_draft(
    steps: list[dict[str, Any]], mounts: list[dict[str, Any]], outputs: list[str] | None = None
) -> RatingAlgorithmDraft:
    base = _draft(steps, outputs)
    data = base.model_dump(mode="json")
    data["sub_graphs"] = mounts
    return RatingAlgorithmDraft.model_validate(data)


def _mount(point: str, inputs: dict[str, str], outputs: dict[str, str]) -> dict[str, Any]:
    return {
        "ref": "sub_graph:ncd-ladder@4",
        "mount_point": point,
        "inputs": inputs,
        "outputs": outputs,
    }


@pytest.mark.req("FR-215")
def test_a_pinned_mount_is_a_node_its_outputs_resolve() -> None:
    # `s_out` consumes `ncd`, which only the mount produces: without the mount as a node it
    # reads as an undefined value (RL-1309 DP-3 item 4).
    steps = [_input("s_in", "x"), _output("s_out", "out", "ncd")]
    draft = _mount_draft(steps, [_mount("s_ncd", {"claims": "x"}, {"factor": "ncd"})])
    assert graph_invariant_issues(draft) == []


@pytest.mark.req("FR-212")
def test_a_broken_mount_is_refused_by_the_invariants() -> None:
    steps = [_input("s_in", "x"), _output("s_out", "out", "ncd")]
    draft = _mount_draft(steps, [_mount("s_ncd", {"claims": "ghost"}, {"factor": "ncd"})])
    issues = graph_invariant_issues(draft)
    assert [(i.code, i.step_id) for i in issues] == [("RATING_GRAPH_UNRESOLVED_REF", "s_ncd")]


@pytest.mark.req("FR-215")
def test_a_mount_point_equal_to_a_step_id_is_an_issue() -> None:
    steps = [_input("s_in", "x"), _output("s_out", "out", "ncd")]
    draft = _mount_draft(steps, [_mount("s_in", {"claims": "x"}, {"factor": "ncd"})])
    issues = graph_invariant_issues(draft)
    assert len(issues) == 1
    assert "mount_point is unique" in issues[0].message


@pytest.mark.req("FR-217")
@pytest.mark.parametrize("blank", ["", "  "])
def test_an_input_port_mapped_to_a_blank_name_is_refused_naming_the_port(blank: str) -> None:
    # RL-1876 item 2: one issue on the mount, naming the port, not "consumes undefined value ''".
    steps = [_input("s_in", "x"), _output("s_out", "out", "ncd")]
    draft = _mount_draft(steps, [_mount("s_ncd", {"claims": blank}, {"factor": "ncd"})])
    issues = graph_invariant_issues(draft)
    assert [(i.code, i.step_id) for i in issues] == [("RATING_GRAPH_UNRESOLVED_REF", "s_ncd")]
    assert "'claims'" in issues[0].message
    assert "unmapped" in issues[0].message
    assert not any("consumes undefined value" in i.message for i in issues)


@pytest.mark.req("FR-217")
def test_an_output_port_mapped_to_a_blank_name_is_refused_naming_the_port() -> None:
    # The output hole: "" used to count as produced, so a step consuming "" resolved and saved.
    steps = [_input("s_in", "x"), _output("s_out", "out", "")]
    draft = _mount_draft(steps, [_mount("s_ncd", {"claims": "x"}, {"factor": ""})])
    issues = graph_invariant_issues(draft)
    blank = [i for i in issues if i.code == "VALIDATION_FAILED" and i.step_id == "s_ncd"]
    assert len(blank) == 1
    assert "'factor'" in blank[0].message
    with pytest.raises(ValidationError):
        RatingAlgorithm.model_validate(draft.model_dump(mode="json"))
