"""`graph_invariant_issues` — every graph breach, located (RL-1474 items 2 and 4; FR-212/214/215).

The save path raises on the first breach; the validate route reports all of them. One
function holds the rules, so these tests pin its order, its skips and its locations.
"""

from __future__ import annotations

from typing import Any

import pytest

from model_schema import RatingAlgorithmDraft, graph_invariant_issues


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
