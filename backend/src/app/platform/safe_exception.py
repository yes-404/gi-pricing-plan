"""Exception text that is safe to persist and log (NFR-499, RL-917, R3).

A quote input is persisted only in the named, access-controlled stores. An exception's own text
is not one of them, and it often carries the value that caused it:

* a Pydantic `ValidationError`'s `str()` prints every failing `input_value`;
* a SQLAlchemy `DBAPIError` prints `[parameters: ...]`, and the database's own message can echo
  the failing row (`Failing row contains (...)`) or the rejected value.

The worker stores an unexpected exception's text in `JobError.message` and logs its traceback,
so both must go through this one module: `safe_message` for text, `safe_exc_info` for a
`logging` call. What it keeps is what an operator needs to act on: the type, and for a
validation error each failing field's path, message and error type; for a database error the
driver's exception type, its SQLSTATE and the constraint name. It never keeps a value.

Any other exception is kept as `Type: message`. A handler that puts a value in its own
exception text is a bug in that handler, and this module cannot know which words are values.
"""

from __future__ import annotations

import types
from typing import Any

from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError

__all__ = ["safe_exc_info", "safe_message"]


class SanitisedError(Exception):
    """Stands in for an exception whose own text is not safe to log or persist."""


def safe_message(exc: BaseException) -> str:
    """`Type: text` for `exc`, with no input value in it."""
    if isinstance(exc, ValidationError):
        problems = "; ".join(
            f"{'.'.join(str(part) for part in error['loc']) or '<root>'}: "
            f"{error['msg']} [{error['type']}]"
            for error in exc.errors(include_url=False, include_context=False, include_input=False)
        )
        return (
            f"{type(exc).__name__}: {exc.error_count()} validation error(s) for {exc.title}: "
            f"{problems}"
        )
    if isinstance(exc, DBAPIError):
        orig: Any = exc.orig
        # SQLAlchemy's asyncpg adapter wraps the driver's exception and keeps it as `__cause__`.
        holders = (orig, getattr(orig, "__cause__", None))
        parts = [type(orig).__name__]
        sqlstate = next((v for h in holders if (v := getattr(h, "sqlstate", None))), None)
        if sqlstate:
            parts.append(f"sqlstate {sqlstate}")
        constraint = next((v for h in holders if (v := getattr(h, "constraint_name", None))), None)
        if constraint:
            parts.append(f"constraint {constraint}")
        return f"{type(exc).__name__}: {', '.join(parts)}"
    return f"{type(exc).__name__}: {exc}"


def safe_exc_info(
    exc: BaseException,
) -> tuple[type[BaseException], BaseException, types.TracebackType | None]:
    """An `exc_info` for a `logging` call whose formatted traceback ends in `safe_message`.

    The frames are the original's, so an operator still sees where it failed; the final line,
    and any chained `__cause__` or `__context__`, are not, because the stand-in has none.
    """
    return SanitisedError, SanitisedError(safe_message(exc)), exc.__traceback__
