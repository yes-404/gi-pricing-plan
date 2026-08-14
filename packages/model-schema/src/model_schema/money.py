"""Monetary and decimal primitives.

FR-OVR-7: money is integer minor units (pence/cents) or `Decimal` throughout the rating
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
   violating FR-OVR-7. Constraining it here closes that gap at the source.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any

from pydantic import Field, GetJsonSchemaHandler, PlainSerializer, Strict
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
            "description": "Exact decimal as a string; never a binary float (FR-OVR-7).",
        }


#: An amount in minor units (pence/cents). Strict: a float is a validation error.
MoneyMinor = Annotated[
    int,
    Strict(),
    Field(description="Amount in minor units (pence/cents) of the workspace currency."),
]

#: An exact decimal that crosses every boundary as a string.
DecimalStr = Annotated[
    Decimal,
    PlainSerializer(str, return_type=str, when_used="always"),
    _DecimalStrSchema(),
]

#: A multiplicative rating factor. Same exactness rules as any other decimal.
Relativity = Annotated[Decimal, PlainSerializer(str, return_type=str), _DecimalStrSchema()]

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
            "converting to minor units (FR-RATE-12: rounding is never implicit)"
        )
    return int(scaled)


def apply_factor(amount_minor: int, factor: Decimal, *, rounding: str) -> int:
    """Apply a multiplicative factor to a minor-unit amount, rounding explicitly.

    `rounding` is required and has no default. FR-RATE-12 says rounding mode is declared
    per step and never implicit, so a default here would quietly undo that requirement.
    """
    if not isinstance(factor, Decimal):  # pragma: no cover - defensive
        raise TypeError(f"factor must be Decimal, got {type(factor).__name__} (FR-OVR-7)")
    product = Decimal(amount_minor) * factor
    return int(product.quantize(Decimal(1), rounding=rounding))


def __getattr__(name: str) -> Any:  # pragma: no cover - import guard
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
