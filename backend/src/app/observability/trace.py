"""Trace identity, propagated from the edge inward (R4, FR-PLAT-38/39/42).

> **R4** — Every request carries a `trace_id` from edge to worker to `pricing-core`, and
> that id appears in every log line, error response, and audit event.

The id is the **W3C / OpenTelemetry trace id**: 32 lowercase hex characters (`00` §5.3).
That format is not cosmetic — it is what makes the id in a problem response join to the
span in a trace backend. A ULID would read as an identifier and correlate with nothing.

A context variable carries it rather than a parameter on every call: the audit writer, the
logger and the error renderer all need it, and threading it through each signature would
put the one thing that must never be forgotten in the place easiest to forget.
"""

from __future__ import annotations

import re
import secrets
from contextvars import ContextVar, Token
from typing import Final

__all__ = [
    "TRACE_ID_PATTERN",
    "bind_trace_id",
    "current_trace_id",
    "new_trace_id",
    "parse_traceparent",
    "reset_trace_id",
]

TRACE_ID_PATTERN: Final = re.compile(r"^[0-9a-f]{32}$")

# All-zero is explicitly invalid in the W3C spec — it is the "no trace" sentinel, and
# accepting it would produce log lines that all correlate with each other.
_INVALID_TRACE_ID: Final = "0" * 32

# W3C traceparent: version "-" trace-id "-" parent-id "-" trace-flags
_TRACEPARENT: Final = re.compile(r"^[0-9a-f]{2}-([0-9a-f]{32})-[0-9a-f]{16}-[0-9a-f]{2}$")

_trace_id: ContextVar[str | None] = ContextVar("trace_id", default=None)


def new_trace_id() -> str:
    """Generate a fresh 128-bit trace id in W3C hex form."""
    while (candidate := secrets.token_hex(16)) == _INVALID_TRACE_ID:  # pragma: no cover
        pass
    return candidate


def parse_traceparent(header: str | None) -> str | None:
    """Extract the trace id from a W3C `traceparent` header, if it is valid.

    An inbound trace is joined rather than replaced, so a request arriving from another
    service keeps one trace across the hop. A malformed header yields `None` and the caller
    starts a new trace — a bad header should not fail the request, only fail to correlate.
    """
    if not header:
        return None
    match = _TRACEPARENT.match(header.strip())
    if match is None:
        return None
    trace_id = match.group(1)
    return None if trace_id == _INVALID_TRACE_ID else trace_id


def bind_trace_id(trace_id: str) -> Token[str | None]:
    """Bind a trace id to the current context, returning a token for `reset_trace_id`."""
    if not TRACE_ID_PATTERN.match(trace_id):
        raise ValueError(
            f"trace_id must be 32 lowercase hex characters (W3C/OpenTelemetry), got "
            f"{trace_id!r}"
        )
    return _trace_id.set(trace_id)


def reset_trace_id(token: Token[str | None]) -> None:
    """Restore the previous trace id. Always paired with `bind_trace_id`."""
    _trace_id.reset(token)


def current_trace_id() -> str | None:
    """The trace id for the current context, or `None` outside a traced operation.

    Returns `None` rather than inventing one: a fabricated id in an audit event would
    assert a correlation that does not exist.
    """
    return _trace_id.get()
