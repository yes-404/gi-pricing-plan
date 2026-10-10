"""RatingAlgorithmDraft is RatingAlgorithm's field set without its invariants (RL-1474 item 1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema import RatingAlgorithm, RatingAlgorithmDraft, RatingAlgorithmSaved


def _cyclic() -> dict:
    """Two expression steps that consume each other's product: a cycle, nothing else wrong."""
    return {
        "slug": "cyc",
        "version": 1,
        "input_contract": [{"name": "x", "type": "decimal"}],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor"}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "x", "input_name": "x",
             "on_missing": "error", "produces": "x"},
            {"step_id": "s_a", "type": "expression", "label": "a", "expr": "x + b",
             "result_type": "decimal", "consumes": ["x", "b"], "produces": "a"},
            {"step_id": "s_b", "type": "expression", "label": "b", "expr": "a",
             "result_type": "decimal", "consumes": ["a"], "produces": "b"},
            {"step_id": "s_out", "type": "output", "label": "out",
             "output_name": "payable_premium_minor",
             "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["a"], "produces": "payable_premium_minor"},
        ],
    }


@pytest.mark.req("FR-212")
def test_the_draft_accepts_a_graph_the_algorithm_refuses() -> None:
    RatingAlgorithmDraft.model_validate(_cyclic())
    with pytest.raises(ValidationError):
        RatingAlgorithm.model_validate(_cyclic())


@pytest.mark.req("FR-212")
def test_the_field_set_is_written_once() -> None:
    assert issubclass(RatingAlgorithm, RatingAlgorithmDraft)
    assert RatingAlgorithm.model_fields.keys() == RatingAlgorithmDraft.model_fields.keys()


@pytest.mark.req("FR-212")
def test_the_draft_still_refuses_an_unknown_field() -> None:
    with pytest.raises(ValidationError):
        RatingAlgorithmDraft.model_validate({**_cyclic(), "cycle_note": "x"})


def test_the_saved_shape_is_the_201_wire() -> None:
    saved = RatingAlgorithmSaved.model_validate(
        {"id": "01a04394-338b-7651-9e42-c73ee70396f8", "slug": "motor-gb", "version": 2}
    )
    assert saved.model_dump(mode="json") == {
        "id": "01a04394-338b-7651-9e42-c73ee70396f8", "slug": "motor-gb", "version": 2,
    }
