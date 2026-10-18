"""FR-213 (`RL-1613`, WK-675 S5): an `enum` Rating Input may declare its level order.

`ordered` is opt-in, valid only on an `enum` with a non-empty `domain`, and absent from the
stored form while `false` — so an input that never declares it leaves every bundle hash alone.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from model_schema.input_free import InputFreeError
from model_schema.rating import InputContractField


def _field(**kw: Any) -> InputContractField:
    return InputContractField.model_validate({"name": "band", **kw})


@pytest.mark.req("FR-213")
def test_ordered_defaults_to_false_and_is_left_out_of_the_dump() -> None:
    field = _field(type="enum", domain=["a", "b"])
    assert field.ordered is False
    assert "ordered" not in field.model_dump()
    assert "ordered" not in field.model_dump(mode="json")
    assert "ordered" not in field.model_dump_json()


@pytest.mark.req("FR-213")
def test_ordered_true_is_kept_in_the_dump() -> None:
    field = _field(type="enum", domain=["a", "b"], ordered=True)
    assert field.model_dump()["ordered"] is True
    assert field.model_dump(mode="json")["ordered"] is True
    assert InputContractField.model_validate(field.model_dump()) == field


@pytest.mark.req("FR-213")
def test_an_explicit_false_is_also_left_out() -> None:
    assert "ordered" not in _field(type="enum", domain=["a"], ordered=False).model_dump()


@pytest.mark.req("FR-213")
@pytest.mark.parametrize("kw", [
    {"type": "int"},
    {"type": "string"},
    {"type": "enum"},                  # no domain
    {"type": "enum", "domain": []},    # an empty domain
], ids=["int", "string", "enum-no-domain", "enum-empty-domain"])
def test_ordered_is_refused_where_it_is_invalid(kw: dict[str, Any]) -> None:
    with pytest.raises(ValidationError) as caught:
        _field(ordered=True, **kw)
    assert isinstance(caught.value.errors()[0]["ctx"]["error"], InputFreeError)


@pytest.mark.req("FR-213")
def test_an_unordered_field_of_any_type_still_validates() -> None:
    _field(type="int", min=0, max=9)
    _field(type="enum")
