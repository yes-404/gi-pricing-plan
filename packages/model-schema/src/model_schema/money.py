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

from decimal import Context, Decimal, Inexact, InvalidOperation
from typing import Annotated, Any

from pydantic import BeforeValidator, Field, GetJsonSchemaHandler, PlainSerializer, Strict
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from model_schema.input_free import InputFreeError

__all__ = [
    "CanonicalDecimalStr",
    "Currency",
    "DecimalMagnitudeError",
    "DecimalStr",
    "MoneyMinor",
    "PositionalDecimalStr",
    "Relativity",
    "SchemaDecimal",
    "apply_factor",
    "to_minor",
]


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


#: The string pattern Pydantic <= 2.13 put on a bare `Decimal`'s JSON Schema string branch and
#: 2.14 stopped emitting: it refuses `"abc"`, `"1.2.3"` and a lone sign or point.
_DECIMAL_STRING_PATTERN = r"^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$"


class _DecimalStringPattern:
    """Restore `_DECIMAL_STRING_PATTERN` on every string branch of a bare `Decimal`'s schema.

    Pydantic 2.14 renders a `Decimal` as `{"type": "string"}` with no pattern, which loosens
    a published money-semantic contract (the contract is byte-identical to the one 2.13
    generated; `test_decimal_contract_pattern.py` holds it there). Applies in validation
    mode (`anyOf` number/string) and serialization mode (string) alike.
    """

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        js = handler(schema)
        for branch in (*js.get("anyOf", ()), js):
            if branch.get("type") == "string":
                branch.setdefault("pattern", _DECIMAL_STRING_PATTERN)
        return js


#: A `Decimal` that keeps Pydantic's own wire shape (number-or-string on input, string on
#: output) with the string pattern pinned explicitly, so a Pydantic upgrade cannot drop it.
#: Use `DecimalStr` for a new field; this type exists for contract fields published as the
#: bare-`Decimal` shape.
SchemaDecimal = Annotated[Decimal, _DecimalStringPattern()]

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
        raise InputFreeError(
            "a float has already lost the precision an exact decimal is for (FR-10). Pass a "
            "string, an int or a Decimal — quantising explicitly first if the value was computed "
            "in float."
        )
    return value


#: The largest adjusted exponent, either sign, an exact decimal may have when it is *written*
#: (FR-21). Positional text grows with the exponent (`1E+999999999` is a gigabyte, `1E-400` is
#: 402 characters), and the engine carries float64 (FR-273), whose magnitude ends near
#: `1E+308`: a value past it is no value the engine can use. Writing only: validation takes
#: any exponent, and a value past the bound fails loudly when it is serialised.
MAX_POSITIONAL_EXPONENT = 308


class DecimalMagnitudeError(InputFreeError):
    """An exact decimal past `MAX_POSITIONAL_EXPONENT`, refused when written (FR-21).

    A type of its own so the API can answer it as a coded 422 (`DECIMAL_OUT_OF_RANGE`) rather
    than the 500 an unnamed serialisation error becomes.
    """


def _positional(value: Decimal) -> str:
    """`format(value, "f")` behind the FR-21 bound on the adjusted exponent.

    The one writer for `DecimalStr`, `Relativity` and `CanonicalDecimalStr`.
    """
    if not -MAX_POSITIONAL_EXPONENT <= value.adjusted() <= MAX_POSITIONAL_EXPONENT:
        raise DecimalMagnitudeError(
            "an exact decimal whose adjusted exponent is beyond 308 either way is not written "
            "in positional notation (FR-21; the engine carries float64, FR-273)"
        )
    return format(value, "f")


#: An exact decimal that crosses every boundary as a string, always positional, so every value
#: matches the published pattern (FR-21, FD-1337). Spelling is kept: `66000.440` stays. A float
#: is a validation error, not a silent coercion (`OQ-547`).
DecimalStr = Annotated[
    Decimal,
    BeforeValidator(_reject_float),
    PlainSerializer(_positional, return_type=str, when_used="always"),
    _DecimalStrSchema(),
]

#: Kept for the ladder's imports (`RL-1329`): the same type since FD-1337.
PositionalDecimalStr = DecimalStr


def _canonical_decimal(value: Decimal) -> str:
    """One spelling per value: positional, trailing zeros dropped, every zero `0` (FD-1337).

    `normalize` rounds to the *ambient* context's precision (28 digits by default), which would
    make a governed hash depend on a thread-local setting and merge two long values. The
    context here is sized to the value's own digits and traps `Inexact` and `InvalidOperation`,
    so a rounding, or a signalling NaN that skipped validation, raises instead of silently
    changing the value. `normalize` also keeps a zero's sign, hence the zero branch.
    """
    if not value:
        return "0"
    exact = Context(prec=max(len(value.as_tuple().digits), 1), traps=[Inexact, InvalidOperation])
    return _positional(value.normalize(exact))


#: `DecimalStr` with one spelling per value, for a field a governed hash reads (FD-1337).
#: `normalize` alone would give `1E+2`; `format` keeps it positional. Every zero (`-0`, `0.00`,
#: `0E+3`) is written `0`: `normalize` keeps a zero's sign, which is no part of the value.
CanonicalDecimalStr = Annotated[
    Decimal,
    BeforeValidator(_reject_float),
    PlainSerializer(_canonical_decimal, return_type=str, when_used="always"),
    _DecimalStrSchema(),
]

#: A multiplicative rating factor. Same exactness rules as any other decimal — including
#: choice 3: a factor computed in float is quantised by its caller, not by this type.
Relativity = Annotated[
    Decimal,
    BeforeValidator(_reject_float),
    PlainSerializer(_positional, return_type=str),
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
        raise InputFreeError(
            "the value is not exact to the requested decimal places; round explicitly before "
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
