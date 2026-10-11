"""Sub-graph contract (WK-1250 Slice 1, 03 §4.11) — typed ports and fragment invariants.

Covers FR-217 (a stored, versioned fragment with declared ports) and FR-212 (the DAG
rules, restated for ports). The result-type check (FR-227) lives in `pricing-core`.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest
from pydantic import ValidationError

from model_schema.graph_errors import GraphCycleError, GraphUnresolvedRefError
from model_schema.input_free import InputFreeError
from model_schema.sub_graphs import SubGraph, SubGraphBody, SubGraphCreate, SubGraphInputPort

pytestmark = pytest.mark.req("FR-217")


def body() -> dict[str, Any]:
    """The 03 §4.11 example, without its slug and version."""
    return {
        "inputs": [{"name": "ncd_years", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": "relativity", "required": True}],
        "steps": [
            {
                "step_id": "s_ncd", "type": "table", "label": "NCD ladder",
                "rate_table_ref": "rate_table:ncd@2", "key_expr": ["ncd_years"],
                "consumes": "ncd_years", "produces": "ncd_factor",
            }
        ],
        "change_note": "Step-back after one claim is two years, not three.",
    }


def refusal(payload: dict[str, Any]) -> dict[str, Any]:
    with pytest.raises(ValidationError) as caught:
        SubGraphBody.model_validate(payload)
    return caught.value.errors()[0]  # type: ignore[return-value]


def test_the_spec_example_parses_as_stored_shape() -> None:
    sub_graph = SubGraph.model_validate({"slug": "ncd-ladder", "version": 4, **body()})
    assert sub_graph.inputs == [SubGraphInputPort(name="ncd_years", type="int")]
    assert sub_graph.outputs[0].name == "ncd_factor"
    assert SubGraphCreate.model_validate({"slug": "ncd-ladder", **body()}).slug == "ncd-ladder"


def test_an_input_port_is_a_producer_and_a_clamp_chain_is_accepted() -> None:
    payload = body()
    payload["steps"].append(
        {
            "step_id": "s_clamp", "type": "constraint", "label": "Cap",
            "condition": "ncd_factor <= 1", "on_violation": "clamp",
            "clamp_bounds": {"max": "1"}, "reason_code": "NCD_CAP",
            "consumes": "ncd_factor", "produces": "ncd_factor",
        }
    )
    assert SubGraphBody.model_validate(payload).steps[1].step_id == "s_clamp"


def test_a_step_consuming_an_unproduced_name_is_unresolved() -> None:
    payload = body()
    payload["steps"][0]["consumes"] = ["ncd_years", "nothing_makes_this"]
    err = refusal(payload)
    assert isinstance(err["ctx"]["error"], GraphUnresolvedRefError)
    assert "consumes undefined value" in str(err["ctx"]["error"])


def test_an_output_port_no_step_produces_is_unresolved() -> None:
    payload = body()
    payload["outputs"].append({"name": "ghost", "type": "int", "required": False})
    err = refusal(payload)
    assert isinstance(err["ctx"]["error"], GraphUnresolvedRefError)
    assert "undefined value" in str(err["ctx"]["error"])


def test_a_cycle_is_refused_with_the_cycle_class() -> None:
    payload = body()
    payload["steps"] = [
        {"step_id": "a", "type": "expression", "label": "a", "expr": "b + 1",
         "result_type": "int", "consumes": "b", "produces": "ncd_factor"},
        {"step_id": "b", "type": "expression", "label": "b", "expr": "ncd_factor + 1",
         "result_type": "int", "consumes": "ncd_factor", "produces": "b"},
    ]
    err = refusal(payload)
    assert isinstance(err["ctx"]["error"], GraphCycleError)
    assert "cycle" in str(err["ctx"]["error"])


def test_producing_an_input_port_without_consuming_it_is_refused() -> None:
    payload = body()
    payload["steps"].append(
        {"step_id": "s_redo", "type": "expression", "label": "redo", "expr": "1",
         "result_type": "int", "produces": "ncd_years"}
    )
    err = refusal(payload)
    assert type(err["ctx"]["error"]) is ValueError
    assert "re-production chain" in str(err["ctx"]["error"])


def test_an_orphan_step_is_refused() -> None:
    payload = body()
    payload["steps"].append(
        {"step_id": "s_orphan", "type": "expression", "label": "orphan", "expr": "1",
         "result_type": "int", "produces": "unused"}
    )
    err = refusal(payload)
    assert type(err["ctx"]["error"]) is ValueError
    assert "unreachable" in str(err["ctx"]["error"])


def test_a_duplicate_step_id_is_refused() -> None:
    payload = body()
    payload["steps"].append(copy.deepcopy(payload["steps"][0]))
    err = refusal(payload)
    assert type(err["ctx"]["error"]) is InputFreeError
    assert "unique" in str(err["ctx"]["error"])


def test_sub_graphs_is_an_unknown_field() -> None:
    payload = body()
    payload["sub_graphs"] = []
    err = refusal(payload)
    assert err["type"] == "extra_forbidden"
    assert err["loc"] == ("sub_graphs",)


@pytest.mark.parametrize("step_type", ["input", "output"])
def test_ports_replace_input_and_output_steps(step_type: str) -> None:
    payload = body()
    extra: dict[str, Any] = (
        {"step_id": "s_in", "type": "input", "label": "in", "input_name": "x",
         "on_missing": "error", "produces": "x"}
        if step_type == "input"
        else {"step_id": "s_out", "type": "output", "label": "out", "output_name": "ncd_factor",
              "rounding": {"mode": "half_even", "dp": 0}, "consumes": "ncd_factor"}
    )
    payload["steps"].append(extra)
    err = refusal(payload)
    assert type(err["ctx"]["error"]) is InputFreeError
    assert "ports replace" in str(err["ctx"]["error"])


@pytest.mark.parametrize("note", ["", "   "])
def test_an_empty_change_note_is_refused(note: str) -> None:
    payload = body()
    payload["change_note"] = note
    with pytest.raises(ValidationError):
        SubGraphBody.model_validate(payload)


def test_a_float_port_type_is_refused() -> None:
    payload = body()
    payload["inputs"][0]["type"] = "float"
    with pytest.raises(ValidationError):
        SubGraphBody.model_validate(payload)


def test_port_names_are_unique() -> None:
    payload = body()
    payload["inputs"].append({"name": "ncd_years", "type": "int"})
    err = refusal(payload)
    assert type(err["ctx"]["error"]) is InputFreeError
