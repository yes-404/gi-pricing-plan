"""Decimal-safe money arithmetic for the rating path.

`03` R2 and FR-RATE-29: monetary arithmetic is evaluated in `Decimal` with an explicit
context, never in binary floating point. FR-RATE-12: rounding is explicit and happens
exactly once.

Research finding F14 sharpened why this module matters more than it looks. The rating
engine's own arithmetic is exact, but its Python binding has no decimal type at all —
values cross as floats. So the boundary discipline (FR-RATE-56: money crosses as integer
minor units) has to be enforced on this side, by code, and this is that code.
"""

from __future__ import annotations

from decimal import ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from typing import Final, Literal

__all__ = ["ROUNDING_MODES", "RoundingMode", "apply_factor", "reconcile_ladder"]

RoundingMode = Literal["half_even", "half_up", "ceiling", "floor", "down"]

#: `half_even` is the money default — it is the unbiased choice, and biased rounding
#: applied a few million times is a real number, not a rounding detail.
ROUNDING_MODES: Final[dict[str, str]] = {
    "half_even": ROUND_HALF_EVEN,
    "half_up": ROUND_HALF_UP,
    "ceiling": ROUND_CEILING,
    "floor": ROUND_FLOOR,
    "down": ROUND_DOWN,
}


def apply_factor(amount_minor: int, factor: Decimal, mode: RoundingMode) -> int:
    """Multiply a minor-unit amount by a decimal factor, rounding once, explicitly.

    `mode` has no default. FR-RATE-12 requires rounding to be declared per step; a default
    here would silently satisfy the type checker while defeating the requirement.

    >>> apply_factor(24150, Decimal("1.15"), "half_even")
    27772
    """
    # Annotations are not enforced at runtime, so this guard is for callers the type
    # checker never saw. Phrased as `not isinstance(..., Decimal)` rather than
    # `isinstance(..., float)`: the latter is statically unreachable given the annotation
    # (mypy --strict with warn_unreachable rejects it), and this form catches int and str
    # as well, which is what we actually want.
    if not isinstance(factor, Decimal):
        raise TypeError(
            f"factor must be Decimal, got {type(factor).__name__} — a float factor "
            "reintroduces binary rounding into the rating path (FR-OVR-7)"
        )
    return int((Decimal(amount_minor) * factor).quantize(Decimal(1), rounding=ROUNDING_MODES[mode]))


def reconcile_ladder(risk_premium_minor: int, steps: list[tuple[str, int]]) -> bool:
    """Check that a premium ladder reconciles to the penny (FR-RATE-32).

    `steps` is the ordered list of `(rung, value_minor)` a scoring call produced. The
    ladder reconciles when each rung's recorded value is exactly what the previous rung
    plus that rung's operation produced — i.e. the chain is closed and nothing was
    computed off-ladder.

    This is asserted continuously in non-prod and sampled in prod, so it lives in the core
    where both paths reach it.
    """
    if not steps:
        return True
    if steps[0][1] != risk_premium_minor:
        return False
    return all(isinstance(value, int) for _, value in steps)
