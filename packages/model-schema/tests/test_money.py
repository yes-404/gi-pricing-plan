"""FR-OVR-7: money is integer minor units or Decimal, never float.

These are mostly *negative* tests. skills-map §9.1 makes the point that for a governed
system the suite must prove the wrong thing cannot happen, not merely that the right thing
can — so the tests that earn their keep here are the ones asserting a float is refused.
"""

from decimal import ROUND_HALF_EVEN, Decimal

import pytest
from pydantic import BaseModel, ValidationError

from model_schema.money import DecimalStr, MoneyMinor, Relativity, apply_factor, to_minor


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


class Exact(BaseModel):
    """A model over the two exact-decimal types, including a container of one."""

    amount: DecimalStr
    weights: tuple[DecimalStr, ...] = ()


@pytest.mark.req("FR-OVR-7")
@pytest.mark.parametrize("bad", [0.1 + 0.2, 12.5, 12.0, float("1e-7")])
def test_decimal_str_refuses_a_float(bad):
    """`OQ-OVR-8`, decided 2026-08-19: the input shape is policed, not only the wire shape.

    `12.0` is refused as firmly as `0.1 + 0.2`, for `MoneyMinor`'s reason above: a whole-
    valued float coerces cleanly, and accepting it is what teaches the next caller that a
    float is fine here. The one that motivated the decision is the first — it used to yield
    `Decimal('0.30000000000000004')` inside a field FR-OVR-7 calls exact.
    """
    with pytest.raises(ValidationError, match="float"):
        Exact(amount=bad)


@pytest.mark.req("FR-OVR-7")
def test_decimal_str_refuses_a_float_inside_a_container():
    """The rule is the type's, so it holds wherever the type appears.

    `Histogram.exposure` and `Profile`'s level weights are tuples of `DecimalStr`; a check
    written per-field would have left every one of them open.
    """
    with pytest.raises(ValidationError, match="float"):
        Exact(amount=Decimal("1"), weights=(Decimal("1.5"), 2.5))


@pytest.mark.req("FR-OVR-7")
def test_decimal_str_refuses_a_json_number():
    """A hand-written client posting `1.5` rather than `"1.5"` is the other half of the
    exposure `OQ-OVR-8` names. The contract has always declared this field a string."""
    with pytest.raises(ValidationError, match="float"):
        Exact.model_validate_json('{"amount": 1.5}')


@pytest.mark.req("FR-OVR-7")
@pytest.mark.parametrize("good", ["1.5", 2, Decimal("1.500")])
def test_decimal_str_still_accepts_every_exact_form(good):
    """Refusing floats must not narrow the type to `Decimal` alone: `str` is what the wire
    carries and `int` is exact, so both stay valid."""
    assert Exact(amount=good).amount == Decimal(str(good))


@pytest.mark.req("FR-OVR-7")
def test_relativity_refuses_a_float_too():
    """A rating factor is the exact-decimal field with the most leverage over a premium.

    Leaving it lax while `DecimalStr` was strict would rebuild the inconsistency
    `OQ-OVR-8` was decided to remove.
    """
    with pytest.raises(ValidationError, match="float"):
        Premium(payable_minor=1, factor=1.04)
