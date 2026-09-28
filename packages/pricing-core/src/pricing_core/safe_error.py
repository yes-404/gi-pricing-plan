"""Exception text that is safe to persist and log (NFR-499, RL-917, R3).

A quote input is persisted only in the named, access-controlled stores. An exception's own text
is not one of them, and a Pydantic `ValidationError`'s `str()` prints every failing
`input_value`, which for a quote is a quote input.

Every place that stores or logs an unexpected exception's text goes through this rule: the
worker's failed-Job path and `score_batch`'s per-row error rows. For a validation error it keeps
what an operator needs to act on, each failing field's path, message and error type, and never
a value. Any other exception is kept as its own text: a handler that puts a value in its own
exception message is a bug in that handler, and this module cannot know which words are values.

Standalone by design (ADR-703): this package imports no database or web library. The database
layer, which needs one, is the backend's `app.platform.safe_exception`, and it builds on this.
"""

from __future__ import annotations

import types
from collections.abc import Callable

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
    return str(exc)


def safe_error_text(exc: BaseException) -> str:
    """`Type: detail` for `exc`, with no input value in it."""
    return f"{type(exc).__name__}: {safe_error_detail(exc)}"


def safe_exc_info(
    exc: BaseException, describe: Callable[[BaseException], str] = safe_error_text
) -> tuple[type[BaseException], BaseException, types.TracebackType | None]:
    """An `exc_info` for a `logging` call whose formatted traceback ends in `describe(exc)`.

    The frames are the original's, so an operator still sees where it failed; the final line,
    and any chained `__cause__` or `__context__`, are not, because the stand-in has none.
    `describe` lets a layer that knows more exception types (the backend's database errors)
    supply its own text.
    """
    return SanitisedError, SanitisedError(describe(exc)), exc.__traceback__
