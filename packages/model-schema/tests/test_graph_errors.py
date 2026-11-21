"""The typed signal of a graph refusal on `RatingAlgorithm` (FD working id 9948, FR-212).

A caller maps a refusal to its code by the class pydantic carries in `errors()`, never by
matching the message, whose echoed input can contain any word.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema.graph_errors import GraphCycleError, GraphUnresolvedRefError
from model_schema.input_free import InputFreeError
from model_schema.rating import RatingAlgorithm

pytestmark = pytest.mark.req("FR-212")


def algorithm() -> dict:
    return {
        "slug": "motor-gb",
        "version": 1,
        "input_contract": [{"name": "age", "type": "int", "nullable": False}],
        "outputs": [{"name": "out", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "age", "input_name": "age",
             "on_missing": "error", "produces": "age"},
            {"step_id": "s_out", "type": "output", "label": "out", "output_name": "out",
             "rounding": {"mode": "half_even", "dp": 0}, "consumes": "age"},
        ],
    }


def raised(data: dict) -> BaseException:
    with pytest.raises(ValidationError) as caught:
        RatingAlgorithm.model_validate(data)
    (error,) = caught.value.errors()
    assert error["type"] == "value_error"
    return error["ctx"]["error"]  # type: ignore[no-any-return]


def test_an_undefined_value_raises_the_unresolved_ref_class() -> None:
    data = algorithm()
    data["steps"][1]["consumes"] = "ghost"
    assert isinstance(raised(data), GraphUnresolvedRefError)


def test_a_cycle_raises_the_cycle_class() -> None:
    data = algorithm()
    data["steps"] = [
        {"step_id": "a", "type": "expression", "label": "a", "expr": "b", "result_type": "int",
         "consumes": "b", "produces": "a"},
        {"step_id": "b", "type": "expression", "label": "b", "expr": "a", "result_type": "int",
         "consumes": "a", "produces": "b"},
        {"step_id": "s_out", "type": "output", "label": "out", "output_name": "out",
         "rounding": {"mode": "half_even", "dp": 0}, "consumes": "a"},
    ]
    assert isinstance(raised(data), GraphCycleError)


def test_an_input_free_error_is_a_value_error() -> None:
    """Pydantic wraps a `ValueError` in a validator, and callers catching `ValueError` still
    catch an `InputFreeError`: the tests below rely on it."""
    assert issubclass(InputFreeError, ValueError)


def test_a_declared_output_without_an_output_step_is_an_input_free_error() -> None:
    data = algorithm()
    data["outputs"].append({"name": "extra", "type": "int", "required": False})
    error = raised(data)
    assert type(error) is InputFreeError
    assert "FR-214" in str(error)


# --- #1712 S7c: a typed signal's text carries no caller-controlled string --------------------
# Every string the request controls carries the sentinel, so a text that echoes any of them
# (a step id, a value name, an output name, a mount point, a port name) is caught whichever
# rule fires first.

SENT = "sentinels7c91"


def _planted() -> dict:
    return {
        "slug": f"slug-{SENT}",
        "version": 1,
        "input_contract": [{"name": f"age_{SENT}", "type": "int", "nullable": False}],
        "outputs": [{"name": f"out_{SENT}", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": f"s_in_{SENT}", "type": "input", "label": f"label {SENT}",
             "input_name": f"age_{SENT}", "on_missing": "error", "produces": f"age_{SENT}"},
            {"step_id": f"s_out_{SENT}", "type": "output", "label": f"label {SENT}",
             "output_name": f"out_{SENT}", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": f"age_{SENT}"},
        ],
    }


def test_an_undefined_value_signal_names_neither_the_step_nor_the_value() -> None:
    data = _planted()
    data["steps"][1]["consumes"] = f"ghost_{SENT}"
    error = raised(data)
    assert isinstance(error, GraphUnresolvedRefError)
    assert SENT not in str(error)


def test_a_blank_mount_input_signal_names_neither_the_mount_nor_the_port() -> None:
    data = _planted()
    data["sub_graphs"] = [
        {"ref": "sub_graph:ncd@1", "mount_point": f"m_{SENT}", "inputs": {f"p_{SENT}": " "}}
    ]
    error = raised(data)
    assert isinstance(error, GraphUnresolvedRefError)
    assert SENT not in str(error)


def test_a_missing_output_step_names_the_output_in_located_and_not_in_the_message() -> None:
    data = _planted()
    data["outputs"].append({"name": f"extra_{SENT}", "type": "money_minor", "required": False})
    error = raised(data)
    assert isinstance(error, InputFreeError)
    assert SENT not in str(error)
    assert error.located == {"output": f"extra_{SENT}"}
