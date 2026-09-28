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

import types
from typing import Any

from sqlalchemy.exc import DBAPIError

from app.errors import PlatformError
from pricing_core.safe_error import safe_error_text, safe_exc_info

__all__ = ["safe_job_error_text", "safe_job_exc_info"]


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


def safe_job_exc_info(
    exc: BaseException,
) -> tuple[type[BaseException], BaseException, types.TracebackType | None]:
    """`safe_exc_info` with the backend's types, for a `logging` call."""
    return safe_exc_info(exc, safe_job_error_text)
