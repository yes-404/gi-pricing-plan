"""Monetary and decimal primitives.

FR-10: money is integer minor units (pence/cents) or `Decimal` throughout the rating
path. Floats are permitted only inside model fitting and diagnostics, never in a quoted
premium.

This module makes that a *type* rather than a convention, because a rule stated only in
prose is one nobody notices breaking. Two design choices carry the weight:

1. `MoneyMinor` is **strict** — a `float` is rejected at validation, not silently coerced.
   `1.5` and `250.0` are both errors: the first because it is not a whole number of pence,
   the second because accepting it teaches callers that floats are fine here.

2. `DecimalStr` **serialises as a JSON string and declares itself as one in JSON Schema.**
   Research finding F7 measured that Pydantic renders a bare `Decimal` as
   `anyOf: [{"type": "number"}, {"type": "string"}]` — which permits the lossy binary-float
   form the specification forbids, so a payload could satisfy the generated contract while
   violating FR-10. Constraining it here closes that gap at the source.

3. `DecimalStr` **refuses a `float` on the way in** (`OQ-547`, decided 2026-08-19).
   Choice 2 fixed the *wire* shape; it left the *input* shape open, and
   `OneWayRow(exposure_years=0.1 + 0.2)` returned `Decimal('0.30000000000000004')` — the
   float's binary error preserved verbatim inside a field FR-10 defines as exact. By the
   time Pydantic sees a float the precision the source amount carried is already gone, so
   there is nothing a validator downstream can recover. A caller that legitimately computes
   in float quantises explicitly first (`pricing_core.data.profile._stored_exposure` is the
   precedent) — which puts the choice of decimal places in the caller's code, where a
   reviewer can see it, instead of in whatever binary expansion the hardware produced.

   `int`, `str` and `Decimal` are all still accepted: they are exact, and the string form is
   what every contract round-trip actually carries.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any

from pydantic import BeforeValidator, Field, GetJsonSchemaHandler, PlainSerializer, Strict
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

__all__ = ["Currency", "DecimalStr", "MoneyMinor", "Relativity", "apply_factor", "to_minor"]


class _DecimalStrSchema:
    """Force `Decimal` to render as a JSON *string* in the generated schema (F7)."""

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {
            "type": "string",
            "pattern": r"^-?[0-9]+(\.[0-9]+)?$",
            "description": "Exact decimal as a string; never a binary float (FR-10).",
        }


#: An amount in minor units (pence/cents). Strict: a float is a validation error.
MoneyMinor = Annotated[
    int,
    Strict(),
    Field(description="Amount in minor units (pence/cents) of the workspace currency."),
]


def _reject_float(value: Any) -> Any:
    """Refuse a `float` before it is coerced to `Decimal` (FR-10, `OQ-547`).

    `bool` is not caught here and does not need to be: `isinstance(True, float)` is false,
    and Pydantic rejects a bool for a `Decimal` field on its own.
    """
    if isinstance(value, float):
        raise ValueError(
            f"{value!r} is a float, and a float has already lost the precision an exact "
            "decimal is for (FR-10). Pass a string, an int or a Decimal — quantising "
            "explicitly first if the value was computed in float."
        )
    return value


#: An exact decimal that crosses every boundary as a string. Strict on the way in: a float
#: is a validation error, not a silent coercion (`OQ-547`).
DecimalStr = Annotated[
    Decimal,
    BeforeValidator(_reject_float),
    PlainSerializer(str, return_type=str, when_used="always"),
    _DecimalStrSchema(),
]

#: A multiplicative rating factor. Same exactness rules as any other decimal — including
#: choice 3: a factor computed in float is quantised by its caller, not by this type.
Relativity = Annotated[
    Decimal,
    BeforeValidator(_reject_float),
    PlainSerializer(str, return_type=str),
    _DecimalStrSchema(),
]

#: ISO-4217 alphabetic currency code.
Currency = Annotated[str, Field(pattern=r"^[A-Z]{3}$")]


def to_minor(value: Decimal, *, places: int = 2) -> int:
    """Convert a major-unit decimal to integer minor units.

    Refuses rather than rounds. A value that is not already exact at `places` is a caller
    error — silently rounding here is how a penny goes missing and nobody can say where.

    >>> to_minor(Decimal("361.20"))
    36120
    """
    scaled = value.scaleb(places)
    if scaled != scaled.to_integral_value():
        raise ValueError(
            f"{value} is not exact to {places} decimal places; round explicitly before "
            "converting to minor units (FR-226: rounding is never implicit)"
        )
    return int(scaled)


def apply_factor(amount_minor: int, factor: Decimal, *, rounding: str) -> int:
    """Apply a multiplicative factor to a minor-unit amount, rounding explicitly.

    `rounding` is required and has no default. FR-226 says rounding mode is declared
    per step and never implicit, so a default here would quietly undo that requirement.
    """
    if not isinstance(factor, Decimal):  # pragma: no cover - defensive
        raise TypeError(f"factor must be Decimal, got {type(factor).__name__} (FR-10)")
    product = Decimal(amount_minor) * factor
    return int(product.quantize(Decimal(1), rounding=rounding))


def __getattr__(name: str) -> Any:  # pragma: no cover - import guard
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
