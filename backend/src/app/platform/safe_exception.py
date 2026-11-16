"""Exception text with no input value in it, for a failed Job, a request and a log (NFR-499).

An ALLOW-list, built on `pricing_core.safe_error` (read its docstring first): an exception's
text is kept only where it is ours and known to be input-free, and everything else is its type
name. This adds the two backend types the pricing-core rule cannot know:

* **`PlatformError`**: our coded error. Its `code` is kept in a log line; its message is the
  handler's own, persisted by the handler in `JobError` and in the problem response.
* **`DBAPIError`**: the driver exception's type, its SQLSTATE and the constraint name, never the
  driver's text, which echoes the failing row (`Failing row contains (...)`) or the value
  (`Key (col)=(value) already exists`). `hide_parameters=True` on the engine
  (`app/db/session.py`) removes the bound parameters from the text at the source.

Every unexpected exception keeps its type, and the caller keeps the Job id, the trace id and the
frames of the logged traceback.
"""

from __future__ import annotations

import re
import types
from typing import Any

from sqlalchemy.exc import DBAPIError

from app.errors import DEADLOCK_SQLSTATE, PlatformError, is_registered_code
from pricing_core.safe_error import (
    CodedError,
    safe_error_detail,
    safe_error_text,
    safe_exc_info,
)

__all__ = [
    "coded_job_error",
    "is_retryable_job_code",
    "safe_job_error_text",
    "safe_job_exc_info",
]

_CODE_RE = re.compile(r"[A-Z][A-Z0-9_]*")

#: The Job error codes that tell the caller to submit the Job again (#1888 option (d)). Nothing
#: re-submits automatically: the flag is information on `JobError`, not a retry.
_RETRYABLE_JOB_CODES = frozenset({"CONCURRENT_WRITE_RETRY"})


def is_retryable_job_code(code: str) -> bool:
    """Whether a failed Job's `code` is one the caller may answer by submitting the Job again."""
    return code in _RETRYABLE_JOB_CODES


def safe_job_error_text(exc: BaseException) -> str:
    """`Type` or `Type: detail` for `exc`, with no input value in it."""
    if isinstance(exc, PlatformError):
        return f"{type(exc).__name__}: {exc.code}"
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
    return safe_error_text(exc)


def coded_job_error(exc: BaseException) -> tuple[str, str] | None:
    """`(code, message)` for a pricing-core `CodedError` whose code a catalogue registers.

    Recognition is by class, never by the shape of the text: a library's
    `ValueError("FOO_BAR: secret")` is not one. The text is `safe_error_detail`'s, which
    keeps a `CodedError`'s own input-free message, so no new sink is added (NFR-499). An
    unregistered code returns `None`, as does anything that is not a `CodedError`; the caller
    then stores `JOB_HANDLER_FAILED` as before.
    """
    if isinstance(exc, DBAPIError):
        # A deadlock victim (SQLSTATE 40P01, #1888 option (d)): a named, retryable refusal. The
        # text is ours and carries no driver text.
        orig: Any = exc.orig
        holders = (orig, getattr(orig, "__cause__", None))
        if any(getattr(h, "sqlstate", None) == DEADLOCK_SQLSTATE for h in holders):
            return (
                "CONCURRENT_WRITE_RETRY",
                "Another write to the same data won; nothing was written. Submit the Job again.",
            )
        return None
    if not isinstance(exc, CodedError):
        return None
    code, sep, message = safe_error_detail(exc).partition(": ")
    if not sep or not _CODE_RE.fullmatch(code) or not is_registered_code(code):
        return None
    return code, message


def safe_job_exc_info(
    exc: BaseException,
) -> tuple[type[BaseException], BaseException, types.TracebackType | None]:
    """`safe_exc_info` with the backend's types, for a `logging` call."""
    return safe_exc_info(exc, safe_job_error_text)
