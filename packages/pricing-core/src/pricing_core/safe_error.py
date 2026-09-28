"""Exception text that is safe to persist and log (NFR-499, RL-917, R3).

A quote input is persisted only in the named, access-controlled stores. An exception's own text
is not one of them, and it often carries the value that caused it:

* a Pydantic `ValidationError`'s `str()` prints every failing `input_value`;
* a SQLAlchemy `DBAPIError` prints `[parameters: ...]`, and the database's own message can echo
  the failing row (`Failing row contains (...)`) or the rejected value.

Every place that stores or logs an unexpected exception's text goes through this one module:
the worker's failed-Job path and `score_batch`'s per-row error rows. What it keeps is what an
operator needs to act on: the type, and for a validation error each failing field's path,
message and error type; for a database error the driver's exception type, its SQLSTATE and the
constraint name. It never keeps a value.

Any other exception is kept as its own text. A handler that puts a value in its own exception
message is a bug in that handler, and this module cannot know which words are values.

Standalone by design (ADR-703): this package imports no database or web library. A database
error is recognised by shape (an `orig` driver exception beside a `statement`), which is what
SQLAlchemy's `StatementError` family carries.
"""

from __future__ import annotations

import types
from typing import Any

from pydantic import ValidationError

__all__ = ["SanitisedError", "safe_error_detail", "safe_error_text", "safe_exc_info"]


class SanitisedError(Exception):
    """Stands in for an exception whose own text is not safe to log or persist."""


def safe_error_detail(exc: BaseException) -> str:
    """The text of `exc` with no input value in it, and without the type name."""
    if isinstance(exc, ValidationError):
        problems = "; ".join(
            f"{'.'.join(str(part) for part in error['loc']) or '<root>'}: "
            f"{error['msg']} [{error['type']}]"
            for error in exc.errors(include_url=False, include_context=False, include_input=False)
        )
        return f"{exc.error_count()} validation error(s) for {exc.title}: {problems}"
    orig: Any = getattr(exc, "orig", None)
    if orig is not None and hasattr(exc, "statement"):
        # The driver's own text is not kept: it can echo the rejected value or the failing
        # row. SQLAlchemy's asyncpg adapter wraps the driver's exception as `__cause__`.
        holders = (orig, getattr(orig, "__cause__", None))
        parts = [type(orig).__name__]
        sqlstate = next((v for h in holders if (v := getattr(h, "sqlstate", None))), None)
        if sqlstate:
            parts.append(f"sqlstate {sqlstate}")
        constraint = next((v for h in holders if (v := getattr(h, "constraint_name", None))), None)
        if constraint:
            parts.append(f"constraint {constraint}")
        return ", ".join(parts)
    return str(exc)


def safe_error_text(exc: BaseException) -> str:
    """`Type: detail` for `exc`, with no input value in it."""
    return f"{type(exc).__name__}: {safe_error_detail(exc)}"


def safe_exc_info(
    exc: BaseException,
) -> tuple[type[BaseException], BaseException, types.TracebackType | None]:
    """An `exc_info` for a `logging` call whose formatted traceback ends in `safe_error_text`.

    The frames are the original's, so an operator still sees where it failed; the final line,
    and any chained `__cause__` or `__context__`, are not, because the stand-in has none.
    """
    return SanitisedError, SanitisedError(safe_error_text(exc)), exc.__traceback__
