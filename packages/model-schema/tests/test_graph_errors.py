"""The typed signal of a graph refusal on `RatingAlgorithm` (FD working id 9948, FR-212).

A caller maps a refusal to its code by the class pydantic carries in `errors()`, never by
matching the message, whose echoed input can contain any word.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema.graph_errors import GraphCycleError, GraphUnresolvedRefError
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


def test_a_declared_output_without_an_output_step_is_a_plain_value_error() -> None:
    data = algorithm()
    data["outputs"].append({"name": "extra", "type": "int", "required": False})
    error = raised(data)
    assert type(error) is ValueError
    assert "FR-214" in str(error)
