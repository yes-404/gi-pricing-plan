"""Request middleware: bind a trace, log the outcome, return the id to the caller."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.errors import problem_response, unexpected_problem
from app.observability.logging import get_logger
from app.observability.trace import (
    bind_trace_id,
    new_trace_id,
    parse_traceparent,
    reset_trace_id,
)

__all__ = ["TraceMiddleware"]

_log = get_logger("app.request")

TRACE_HEADER = "traceparent"
RESPONSE_HEADER = "x-trace-id"


class TraceMiddleware(BaseHTTPMiddleware):
    """Give every request a trace id, and give it back to the caller (R4, FR-PLAT-42).

    The id is echoed in a response header on success as well as failure. A user reporting
    "the page was slow" has no error body to quote, and the alternative — asking them to
    reproduce it — is how a five-minute investigation becomes a day.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        trace_id = parse_traceparent(request.headers.get(TRACE_HEADER)) or new_trace_id()
        token = bind_trace_id(trace_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # Rendered here rather than re-raised. Starlette installs an app-level
            # `Exception` handler on ServerErrorMiddleware, which is *outside* every user
            # middleware — so it runs after the `finally` below has cleared the context,
            # and returns a problem with no `trace_id`. R4 makes that the one field the
            # response must carry, so the problem is built while the context is still live.
            _log.exception(
                "request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            response = problem_response(unexpected_problem(request.url.path))
            response.headers[RESPONSE_HEADER] = trace_id
            return response
        else:
            response.headers[RESPONSE_HEADER] = trace_id
            _log.info(
                "request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            return response
        finally:
            reset_trace_id(token)
