"""FR-OVR-7: money is integer minor units or Decimal, never float.

These are mostly *negative* tests. skills-map §9.1 makes the point that for a governed
system the suite must prove the wrong thing cannot happen, not merely that the right thing
can — so the tests that earn their keep here are the ones asserting a float is refused.
"""

from decimal import ROUND_HALF_EVEN, Decimal

import pytest
from pydantic import BaseModel, ValidationError

from model_schema.money import MoneyMinor, Relativity, apply_factor, to_minor


class Premium(BaseModel):
    payable_minor: MoneyMinor
    factor: Relativity


@pytest.mark.req("FR-OVR-7")
def test_money_minor_accepts_an_integer():
    assert Premium(payable_minor=36120, factor=Decimal("1.04")).payable_minor == 36120


@pytest.mark.req("FR-OVR-7")
@pytest.mark.parametrize("bad", [361.20, 250.0, "36120"])
def test_money_minor_refuses_floats_and_strings(bad):
    """250.0 is refused as firmly as 361.20.

    It is a whole number of pence, so coercing it would "work" — and that is exactly why
    it must not. Accepting it teaches every caller that floats are fine in the money path.
    """
    with pytest.raises(ValidationError):
        Premium(payable_minor=bad, factor=Decimal("1.0"))


@pytest.mark.req("FR-OVR-7")
def test_decimal_serialises_as_a_json_string_not_a_number():
    """Research F7: a bare Decimal generates `anyOf: [number, string]`, and the number
    branch is the lossy form the spec forbids. Serialising as a string closes it."""
    dumped = Premium(payable_minor=1, factor=Decimal("1.0400")).model_dump_json()
    assert '"factor":"1.0400"' in dumped, dumped


@pytest.mark.req("FR-OVR-7")
def test_json_schema_declares_decimal_as_string_only():
    """The generated contract must not admit a payload the specification forbids."""
    schema = Premium.model_json_schema()["properties"]["factor"]
    assert schema.get("type") == "string", schema
    assert "anyOf" not in schema, "Decimal must not generate the permissive number|string union"


@pytest.mark.req("FR-RATE-12")
def test_to_minor_refuses_to_round_silently():
    assert to_minor(Decimal("361.20")) == 36120
    with pytest.raises(ValueError, match="not exact"):
        to_minor(Decimal("361.205"))


@pytest.mark.req("FR-RATE-12")
def test_apply_factor_requires_an_explicit_rounding_mode():
    # 24150 * 1.15 == 27772.5 exactly, so the mode — not the arithmetic — decides the
    # answer. half-even resolves the tie to the even neighbour, 27772.
    assert apply_factor(24150, Decimal("1.15"), rounding=ROUND_HALF_EVEN) == 27772
    with pytest.raises(TypeError):
        apply_factor(24150, Decimal("1.15"))  # type: ignore[call-arg]
