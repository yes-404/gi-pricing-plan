"""`ScoringResult.outputs` admits no non-integer number at any depth (`RL-1343` rule 4, SL-1569)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from model_schema.scoring import ScoringResult

_REF = {"type": "rating_version", "slug": "motor", "version": 1}


def _result(outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "outcome": "quoted", "rating_version_ref": _REF, "bundle_hash": "sha256:" + "0" * 64,
        "premium_ladder": [], "outputs": outputs,
    }


@pytest.mark.req("FR-273")
@pytest.mark.parametrize(
    "outputs",
    [{"r": 1.5}, {"w": 3.0}, {"m": {"a": 1.5}}, {"l": [1, 1.5]}],
    ids=["float", "whole-float", "in-map", "in-list"],
)
def test_a_float_anywhere_in_outputs_is_refused(outputs: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        ScoringResult.model_validate(_result(outputs))


@pytest.mark.req("FR-273")
def test_the_json_forms_of_an_output_are_accepted() -> None:
    """Control: an integer, a decimal string, a bool, null, and maps and lists of them."""
    outputs = {"i": 27, "s": "27.00", "b": True, "n": None, "m": {"a": 1}, "l": [1, "2.00"]}
    result = ScoringResult.model_validate(_result(outputs))
    assert json.loads(result.model_dump_json())["outputs"] == outputs
    assert result.outputs["b"] is True


@pytest.mark.req("FR-273")
def test_a_whole_integer_is_accepted_because_the_model_does_not_know_declared_types() -> None:
    """The documented blind spot (PL-1568 item 10): `27` under a declared `decimal` is valid
    here; `_build_outputs` (item 1) and batch's check (item 11) close it."""
    assert ScoringResult.model_validate(_result({"r": 27})).outputs == {"r": 27}
