"""Exception text that is safe to persist and log (NFR-499, RL-917, R3): an ALLOW-list.

A quote input is persisted only in the named, access-controlled stores. An exception's own text
is not one of them, and it often carries the value that caused it: a Pydantic `ValidationError`
prints every failing `input_value`, its `msg` can echo the value for some error types, and its
`loc` carries the offending KEY of a dict-typed field; a library error (a database driver, a
dataframe engine) repeats the rejected value. A deny-list of the exception types known to do this
misses the next library, so this module inverts it: **an exception's text is kept only where it is
ours and known to be input-free; everything else is its type name and nothing more.**

What is kept, and why each is input-free:

* **Our coded errors**: an instance of `CodedError`, the class `_raise_named` (and the model-call
  sentinel) raise, whose text is `CODE: message`. It is recognised by class, not by the shape of
  its text, so a library's `ValueError("FOO: secret")` is not one. Every raise site that can
  concern a quote input names the field, the constraint and the bounds, never the value; a test
  enumerates those sites by AST and fails when one is added without a case.
* **A `ValidationError`**, rebuilt from its parts and never from its text: each failing location
  kept only for the parts that are field names a model declares (a dict key or an extra key
  becomes `<key>`; a list index is kept), the error `type`, the declared constraint bounds in its
  `ctx` (`ge`, `gt`, `le`, `lt`, `min_length`, `max_length`, `pattern`), and the `msg` only for an
  error type in `_FIXED_TEXT_TYPES`, each verified to carry no input, or for a `value_error`
  raised as `model_schema`'s `InputFreeError`, whose raise sites are literals. A type in
  `_AUTHORED_TEXT` (the request-common types whose own `msg` can echo input) renders a fixed
  text of ours instead. `assertion_error`, a plain `value_error` and any type not listed keep
  the type only. `safe_validation_message` is the one function that decides this, read by the
  request-validation 422 as well (FD-1589 row 8, DP-5 (b)).

Everything else is `Type` alone: an operator still has the type, the Job id, the trace id and the
frames of the logged traceback. A layer that knows more input-free types adds them on top of this
(the backend's `app.platform.safe_exception` adds `PlatformError` and the database errors).

Standalone by design (ADR-703): this package imports no database or web library.
"""

from __future__ import annotations

import types
from collections.abc import Callable, Mapping
from typing import Any

from pydantic import BaseModel, ValidationError

from model_schema.input_free import InputFreeError

__all__ = [
    "CodedError",
    "SanitisedError",
    "safe_error_detail",
    "safe_error_text",
    "safe_exc_info",
    "safe_validation_message",
]

#: Pydantic error types whose `msg` is fixed text or names only the declared constraint. Each has
#: a sentinel test in `packages/pricing-core/tests/test_safe_error.py`; a type not listed here is
#: reported by its `type` alone.
_FIXED_TEXT_TYPES = frozenset({
    "missing", "extra_forbidden", "int_type", "int_parsing", "float_type", "float_parsing",
    "string_type", "bool_type", "bool_parsing", "decimal_type", "decimal_parsing",
    "decimal_max_digits", "date_type", "date_from_datetime_parsing", "datetime_type",
    "datetime_from_date_parsing",
    "literal_error", "enum", "string_pattern_mismatch", "string_too_long", "string_too_short",
    "greater_than", "greater_than_equal", "less_than", "less_than_equal", "too_short",
    "too_long", "list_type", "dict_type", "model_type",
})

#: Pydantic error types whose own `msg` can carry input (`union_tag_invalid` echoes the submitted
#: tag, `uuid_parsing` input characters, `json_invalid` the parser's detail), each given a FIXED
#: text of ours that keeps the guidance. Request-common types only (PL-1599 DP-5's extension);
#: each has a sentinel case in `packages/pricing-core/tests/test_safe_error.py`, and a set test
#: fails when a type here has no case.
_AUTHORED_TEXT: Mapping[str, str] = {
    "json_invalid": "The request body is not valid JSON.",
    "date_parsing": "The value should be a valid date in the format YYYY-MM-DD.",
    "date_from_datetime_inexact": (
        "The value should be a date with no time part, in the format YYYY-MM-DD."
    ),
    "datetime_parsing": (
        "The value should be a valid date-time in ISO 8601 format, for example "
        "2026-01-31T09:30:00Z."
    ),
    "uuid_parsing": (
        "The value should be a valid UUID: 32 hexadecimal digits in the form 8-4-4-4-12."
    ),
    "uuid_type": "The value should be a UUID given as a string.",
    "union_tag_invalid": "The discriminator field's value is not one of the expected tags.",
    "union_tag_not_found": (
        "The discriminator field is missing; it selects which kind of object this is."
    ),
    "int_from_float": "The value should be a whole number, with no fractional part.",
    "decimal_max_places": "The value has more decimal places than this field allows.",
}

#: Constraint bounds a validation error's `ctx` may carry: what the model declares, not the input.
_CONSTRAINT_KEYS = ("ge", "gt", "le", "lt", "min_length", "max_length", "pattern")


class CodedError(ValueError):
    """A code-named error of ours: its text is `CODE: message`, and the message is input-free.

    Raised by `pricing_core.rating`'s `_raise_named` and by the model-call sentinel. A
    `ValueError` subclass so existing `except ValueError` handling and the `f"{code}: {message}"`
    text the API parses are unchanged; the allow-list keeps its text by `isinstance`.
    """


class SanitisedError(Exception):
    """Stands in for an exception whose own text is not safe to log or persist."""


def _declared_field_names() -> frozenset[str]:
    """Every field name (and alias) any loaded Pydantic model declares."""
    names: set[str] = set()
    stack: list[type[BaseModel]] = [BaseModel]
    seen: set[type[BaseModel]] = set()
    while stack:
        model = stack.pop()
        for subclass in model.__subclasses__():
            if subclass in seen:
                continue
            seen.add(subclass)
            stack.append(subclass)
            for name, field in subclass.model_fields.items():
                names.add(name)
                if field.alias:
                    names.add(field.alias)
    return frozenset(names)


def _safe_location(loc: tuple[int | str, ...], declared: frozenset[str]) -> str:
    parts = [
        f"[{part}]" if isinstance(part, int) else (part if part in declared else "<key>")
        for part in loc
    ]
    return ".".join(parts).replace(".[", "[") or "<root>"


def safe_validation_message(error: Mapping[str, Any]) -> str | None:
    """The `msg` of one pydantic error when it carries no input, else `None`.

    Kept for an error type in `_FIXED_TEXT_TYPES`, and for a `value_error` raised as an
    `InputFreeError` (whose every raise site is a literal). A type in `_AUTHORED_TEXT` gets its
    fixed authored text in place of pydantic's `msg`. One rule for every sink: the
    request-validation 422 and `_validation_detail` both read it.
    """
    error_type = error["type"]
    if error_type in _FIXED_TEXT_TYPES:
        return str(error["msg"])
    if error_type in _AUTHORED_TEXT:
        return _AUTHORED_TEXT[error_type]
    underlying = (error.get("ctx") or {}).get("error")
    if error_type == "value_error" and isinstance(underlying, InputFreeError):
        return str(error["msg"])
    return None


def _validation_detail(exc: ValidationError) -> str:
    declared = _declared_field_names()
    problems: list[str] = []
    for error in exc.errors(include_url=False, include_context=True, include_input=False):
        error_type = error["type"]
        text = f"{_safe_location(error['loc'], declared)}: [{error_type}]"
        bounds = {k: v for k, v in (error.get("ctx") or {}).items() if k in _CONSTRAINT_KEYS}
        if bounds:
            text += " " + ", ".join(f"{k}={v!r}" for k, v in sorted(bounds.items()))
        message = safe_validation_message(error)
        if message is not None:
            text += f" {message}"
        problems.append(text)
    return f"{exc.error_count()} validation error(s) for {exc.title}: " + "; ".join(problems)


def safe_error_detail(exc: BaseException) -> str:
    """The text of `exc` that is safe to keep, without the type name; `""` when none is."""
    if isinstance(exc, ValidationError):
        return _validation_detail(exc)
    if isinstance(exc, CodedError):
        return str(exc)
    return ""


def safe_error_text(exc: BaseException) -> str:
    """`Type` or `Type: detail` for `exc`, with no input value in it."""
    detail = safe_error_detail(exc)
    # A `CodedError` is rendered as the `ValueError` it always was: the class is the allow-list's
    # marker, not something a reader or a stored message should see.
    name = "ValueError" if isinstance(exc, CodedError) else type(exc).__name__
    return f"{name}: {detail}" if detail else name


def safe_exc_info(
    exc: BaseException, describe: Callable[[BaseException], str] = safe_error_text
) -> tuple[type[BaseException], BaseException, types.TracebackType | None]:
    """An `exc_info` for a `logging` call whose formatted traceback ends in `describe(exc)`.

    The frames are the original's, so an operator still sees where it failed; the final line,
    and any chained `__cause__` or `__context__`, are not, because the stand-in has none.
    `describe` lets a layer that knows more input-free exception types (the backend's) supply
    its own text.
    """
    return SanitisedError, SanitisedError(describe(exc)), exc.__traceback__
