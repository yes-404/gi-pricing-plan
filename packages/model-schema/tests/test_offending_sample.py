"""The Offending Sample item is a keyed object, its shape written out (OQ-DATA-12, (b)).

FR-DATA-20 persists an Offending Sample of up to 100 primary keys so an actuary can trace
a non-pass outcome back to rows. The item is one object per offending row — property keys
are column names, values are the cell value as a string or null — so a composite key is
one item with several properties, and `None` is distinct from `""`. An item with no
properties names no row and is refused at the type.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from model_schema import RuleResult


def _result(**over: object) -> RuleResult:
    base: dict[str, object] = {
        "rule_id": uuid4(),
        "rule_slug": "psi-driver-age",
        "rule_version": 2,
        "layer": "distributional",
        "severity": "warn",
        "outcome": "warn",
    }
    base.update(over)
    return RuleResult(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-DATA-20")
def test_an_item_with_no_properties_names_no_row_and_is_refused() -> None:
    """A sample exists to be traced back to rows, and an empty object names none.

    `minProperties: 1` is the refusal: the shape is written out, so an object that cannot
    name a row is not merely unhelpful, it is invalid.
    """
    with pytest.raises(ValidationError) as error:
        _result(offending_sample=({},))
    assert "at least 1 item" in str(error.value) or "minProperties" in str(error.value)


@pytest.mark.req("FR-DATA-20")
def test_values_are_strings_or_null() -> None:
    """The cell value reaches the report as a string or `null` — never a number.

    `None` is distinct from `""`: an empty cell and a cell containing the empty string are
    different rows, and the item keeps them different.
    """
    sample = _result(
        offending_sample=({"claim_ref": "C-9", "excess_waived": None, "amount": ""},)
    )
    assert sample.offending_sample == ({"claim_ref": "C-9", "excess_waived": None, "amount": ""},)

    with pytest.raises(ValidationError):
        _result(offending_sample=({"claim_amount_minor": 12_500},))


@pytest.mark.req("FR-DATA-20")
def test_a_composite_key_is_one_item_with_several_properties() -> None:
    """FR-DATA-20's cap counts items; a composite key is one item, not several.

    The cap counts primary keys, and a composite key is one primary key — the shape makes
    that count read directly off the array length.
    """
    sample = _result(offending_sample=({"policy_ref": "P-123", "claim_ref": "C-9"},))
    assert len(sample.offending_sample) == 1
    assert sample.offending_sample[0]["policy_ref"] == "P-123"
