"""SL-2118 (FD-1671, condition (c), FR-239 same hash, same price): parsing a decimal Rating Input
as `Decimal` (the score routes' JSON parse, FR-273) changes no price that parsing it as a `float`
priced, for any text of at most 15 significant digits.

Two claims, over 2000 seeded texts of 1 to 15 significant digits (leading and trailing zeros,
positions of the decimal point, integers and fractions):

1. `float(Decimal(text)) == float(text)`, the float the route used to hand over and the float
   FR-273's guard hands the engine are the same float (a `Decimal` that round-trips as a float is
   accepted, never rounded);
2. `score_one` over the `Decimal` parse and over the `float` parse give an equal result, the
   wall-clock `timing_ms` aside.

Pure: no database. The generator is seeded so a failure names a text that reproduces."""

from __future__ import annotations

import random
from decimal import Decimal

import pytest
from test_rating_score import _ctx
from test_rating_score_decimal_input import _INPUTS, _compiled_with_a_decimal_input

from pricing_core.rating.score import score_one

_SEED = 8432
_TEXTS = 2000


def _texts() -> list[str]:
    rng = random.Random(_SEED)
    texts: list[str] = []
    while len(texts) < _TEXTS:
        digits = rng.randint(1, 15)
        mantissa = rng.randint(10 ** (digits - 1), 10**digits - 1)
        scale = rng.randint(0, digits + 3)
        text = format(Decimal(mantissa).scaleb(-scale), "f")
        if rng.random() < 0.2 and "." in text:
            text += "0" * rng.randint(1, 3)  # trailing zeros do not add significant digits
        texts.append(text)
    return texts


@pytest.mark.req("FR-239")
def test_the_generator_covers_the_range_and_is_deterministic() -> None:
    texts = _texts()
    assert texts == _texts()
    sig = {
        len(Decimal(t).as_tuple().digits) - (len(t) - len(t.rstrip("0")) if "." in t else 0)
        for t in texts
    }
    assert min(sig) <= 2
    assert max(sig) >= 15
    assert len(set(texts)) > 1900


@pytest.mark.req("FR-239")
@pytest.mark.req("FR-273")
def test_a_decimal_parse_of_at_most_15_digits_is_the_float_parse() -> None:
    for text in _texts():
        assert float(Decimal(text)) == float(text), text
        assert Decimal(repr(float(Decimal(text)))) == Decimal(text), text


@pytest.mark.req("FR-239")
@pytest.mark.req("FR-273")
async def test_the_priced_result_is_equal_on_both_parses() -> None:
    bundle = await _compiled_with_a_decimal_input()
    for text in _texts():
        as_float = await score_one(bundle, _ctx(inputs={**_INPUTS, "exposure_years": float(text)}))
        as_decimal = await score_one(
            bundle, _ctx(inputs={**_INPUTS, "exposure_years": Decimal(text)})
        )
        # `timing_ms` is wall-clock; everything priced (ladder, outputs, outcome, hash) is compared.
        assert as_decimal.model_dump(exclude={"timing_ms"}) == as_float.model_dump(
            exclude={"timing_ms"}
        ), text
