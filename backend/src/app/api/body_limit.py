"""A request-body limit on the two upload routes (FR-450, FD-1802).

Pure ASGI, not `BaseHTTPMiddleware` and not a dependency. FastAPI parses a `File()` body
(`await request.form()`) in `get_request_handler`, **before** the dependencies and the
handler run, so a per-route cap cannot see the request until the whole multipart body has
been read. The cap therefore sits below routing, and the order rules in the
`fastapi-service` skill apply:

* it is added to the application **before** `TraceMiddleware`, which stays outermost, so a
  413 carries `trace_id` (FR-445);
* a limit passed while the body streams is raised from the wrapped `receive` as
  `fastapi.HTTPException`: FastAPI's body parsing turns any other exception into a 400,
  and `HTTPException` it re-raises to the handler `errors.py` installs.
"""

from __future__ import annotations

import re
from typing import Final

from fastapi import HTTPException, status
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.errors import PlatformError, problem_response

__all__ = ["CAPPED_ROUTES", "MIB", "BodyLimitMiddleware"]

MIB: Final = 1024 * 1024

#: The routes that declare `413` (FR-450). An operation declares it iff it is capped; a test
#: holds the OpenAPI document and this tuple to each other in both directions.
CAPPED_ROUTES: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"^/api/v1/rate-tables/[^/]+/import$"),
    re.compile(r"^/api/v1/sources/[^/]+/preview$"),
)

_CODE: Final = "PAYLOAD_TOO_LARGE"
_TITLE: Final = "Request body too large"


def too_large_detail(max_bytes: int) -> str:
    """The refusal's text: the limit and the blob path, never the filename (NFR-499)."""
    return (
        f"The request body is larger than the {max_bytes // MIB} MiB limit. Upload a "
        "larger file to the blob store and ingest it from there (07 FR-1776)."
    )


class BodyLimitMiddleware:
    """Refuse a body past `max_bytes` on the capped routes, before any of it is held."""

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not any(r.match(scope["path"]) for r in CAPPED_ROUTES):
            await self.app(scope, receive, send)
            return
        declared = Headers(scope=scope).get("content-length")
        if declared is not None and declared.isdigit() and int(declared) > self.max_bytes:
            problem = PlatformError(
                _CODE, _TITLE, status.HTTP_413_CONTENT_TOO_LARGE, too_large_detail(self.max_bytes)
            ).to_problem(scope["path"])
            response = problem_response(problem)
            await response(scope, receive, send)
            return
        seen = 0

        async def counted() -> Message:
            nonlocal seen
            message = await receive()
            seen += len(message.get("body", b""))
            if seen > self.max_bytes:
                raise HTTPException(
                    status.HTTP_413_CONTENT_TOO_LARGE, too_large_detail(self.max_bytes)
                )
            return message

        await self.app(scope, counted, send)
