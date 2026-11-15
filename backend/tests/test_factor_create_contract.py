"""`FactorCreate.unseen_level_behaviour`: the contract offers what the API accepts (FR-2143).

A Factor may declare `error` or `map_to_base`. `map_to_default` is a Grouping behaviour; a Factor
refuses it, so the create contract must not offer it. DB-free: the shape and its validation only.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.api.models import FactorCreate
from model_schema import UnseenLevelBehaviour


def _body(**over: Any) -> dict[str, Any]:
    return {"slug": "area", "dataset_id": str(uuid4()), "source_columns": ["area"], **over}


def _offered() -> set[str]:
    schema = FactorCreate.model_json_schema()
    field = schema["properties"]["unseen_level_behaviour"]
    offered: set[str] = set()
    for branch in field.get("anyOf", [field]):
        if "$ref" in branch:  # a shared definition: follow it
            branch = schema["$defs"][branch["$ref"].rsplit("/", 1)[-1]]
        offered |= set(branch.get("enum", ()))
    return offered


@pytest.mark.req("FR-2143")
def test_the_create_contract_offers_exactly_error_and_map_to_base() -> None:
    assert _offered() == {"error", "map_to_base"}


@pytest.mark.req("FR-2143")
def test_map_to_default_is_refused_at_validation_with_the_same_contract() -> None:
    with pytest.raises(ValidationError) as refused:
        FactorCreate.model_validate(_body(unseen_level_behaviour="map_to_default"))
    assert "unseen_level_behaviour" in str(refused.value)


@pytest.mark.req("FR-2143")
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("error", UnseenLevelBehaviour.ERROR),
        ("map_to_base", UnseenLevelBehaviour.MAP_TO_BASE),
        (None, None),
    ],
)
def test_a_declared_value_reaches_the_factor_as_model_schemas_own_enum(
    value: str | None, expected: UnseenLevelBehaviour | None
) -> None:
    factor = FactorCreate.model_validate(_body(unseen_level_behaviour=value)).as_factor()
    assert factor.unseen_level_behaviour is expected
