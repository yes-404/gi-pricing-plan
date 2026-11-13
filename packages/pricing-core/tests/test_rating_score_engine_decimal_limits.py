"""SL 8432 round 3: the guard and the engine's decimal limits are pinned together (the
maintainer's ruling, to-lead 2026-11-13 21:00:31 GMT, condition (2)).

`decimals_as_floats` refuses a `Decimal` whose float the engine's decimal cannot hold (scale
above 28, magnitude from 2**96). This test measures the engine itself, with the guard bypassed
(a float input is not touched by the guard), and asserts both directions over generated floats:
the guard accepts exactly what the engine evaluates, and refuses exactly what the engine fails
on. A dependency upgrade that moves the engine's limits turns it red, rather than silently
widening or narrowing the refusal."""

from __future__ import annotations

import math
import random
import struct
from decimal import Decimal
from typing import Any

import pytest
from test_rating_score_undeclared_input_precision import _INPUTS, _bundle, _ctx

from pricing_core.rating.score import decimals_as_floats, score_one

_EDGES = [
    0.0, -0.0, 1e-28, 1.5e-28, 9.9e-29, 1e-29, 1.23456789012345e-14, 1.234567890123456e-14,
    5e-324, 1e-321, -5e-324, 2.2250738585072014e-308, 1e-300, 0.5, -1.5, 1e22, 1e28, 7.9e28,
    math.nextafter(2.0**96, 0.0), 2.0**96, math.nextafter(2.0**96, math.inf), 1e29, 1e30, 1e300,
    1.7976931348623157e308, -2.0**96, -math.nextafter(2.0**96, 0.0),
]  # fmt: skip


def _generated() -> list[float]:
    """Floats across the whole range: random bit patterns (every exponent), short decimal
    mantissas at every power of ten from 1e-35 to 1e32, and the neighbours of each edge."""
    rng = random.Random(8432)
    out = list(_EDGES)
    for e in _EDGES:
        if math.isfinite(e):
            out += [math.nextafter(e, math.inf), math.nextafter(e, -math.inf)]
    for _ in range(150):
        bits = rng.getrandbits(64)
        value = struct.unpack("<d", struct.pack("<Q", bits))[0]
        if math.isfinite(value):
            out.append(value)
    for _ in range(250):
        digits = rng.randint(1, 17)
        mantissa = rng.randint(10 ** (digits - 1), 10**digits - 1)
        out.append(float(f"{rng.choice(['', '-'])}{mantissa}e{rng.randint(-45, 15)}"))
    return [x for x in out if math.isfinite(x)]  # a Decimal is never non-finite here


async def _engine_evaluates(bundle: Any, x: float) -> bool:
    """Whether the engine evaluates a float, the guard bypassed: any failure is `False`."""
    ctx = _ctx(inputs={**_INPUTS, "ghost": 0.5, "unread": x})
    try:
        await score_one(bundle, ctx)
    except Exception:  # the engine raises a bare Exception on the large side
        return False
    return True


def _guard_accepts(x: float) -> bool:
    try:
        decimals_as_floats(Decimal(repr(x)), "k")
    except ValueError:
        return False
    return True


@pytest.mark.req("FR-273")
async def test_the_guard_accepts_exactly_what_the_engine_evaluates() -> None:
    bundle = await _bundle(declared=False)
    disagreements: list[str] = []
    seen = {True: 0, False: 0}
    for x in _generated():
        accepts = _guard_accepts(x)
        evaluates = await _engine_evaluates(bundle, x)
        seen[evaluates] += 1
        if accepts != evaluates:
            disagreements.append(f"{x!r}: guard accepts={accepts}, engine evaluates={evaluates}")
    assert not disagreements, "\n".join(disagreements)
    assert seen[True] > 50, seen  # both sides were exercised
    assert seen[False] > 50, seen


@pytest.mark.req("FR-273")
@pytest.mark.parametrize("text", ["5e-324", "1e-321", "-5e-324", "2.2250738585072014e-308"])
def test_a_subnormal_or_the_smallest_normal_is_refused_naming_the_path_not_the_value(
    text: str,
) -> None:
    with pytest.raises(ValueError, match=r"INPUT_CONTRACT_VIOLATION.*'k'") as info:
        decimals_as_floats(Decimal(text), "k")
    assert text not in str(info.value)  # NFR-499


@pytest.mark.req("FR-273")
def test_zero_and_negative_zero_are_accepted_and_equal() -> None:
    assert (
        decimals_as_floats(Decimal("0.0"), "k") == decimals_as_floats(Decimal("-0.0"), "k") == 0.0
    )
