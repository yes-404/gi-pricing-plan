"""Failed-Job exception text with no input value in it: the database layer (NFR-499, RL-917).

`pricing_core.safe_error` holds the rule for a Pydantic `ValidationError` and cannot know a
database error, because that package imports no database library. This adds the one it cannot:
a SQLAlchemy `DBAPIError` prints `[parameters: ...]`, and the driver's own message can echo the
failing row (`Failing row contains (...)`) or the rejected value (`Key (col)=(value) already
exists`). It keeps the driver exception's type, its SQLSTATE and the constraint name, which is
what an operator acts on, and nothing else. `hide_parameters=True` on the engine
(`app/db/session.py`) removes the parameters from the text at the source; this covers the rest.
"""

from __future__ import annotations

import types
from typing import Any

from sqlalchemy.exc import DBAPIError

from pricing_core.safe_error import safe_error_text, safe_exc_info

__all__ = ["safe_job_error_text", "safe_job_exc_info"]


def safe_job_error_text(exc: BaseException) -> str:
    """`Type: detail` for `exc`, with no input value in it."""
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
    """`safe_exc_info` with the database layer, for a `logging` call."""
    return safe_exc_info(exc, safe_job_error_text)
