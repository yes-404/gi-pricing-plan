"""FR-450: a request body past the stated limit is a 413 before the handler (FD-1802).

DB-free: a small app carries the middleware, the trace middleware outside it, the error
handlers and one `File()` route, with a sentinel that records whether the handler ran.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

import httpx
import pytest
from fastapi import FastAPI, File, UploadFile

from app.api.body_limit import BodyLimitMiddleware
from app.errors import install_error_handlers
from app.observability.middleware import TraceMiddleware

LIMIT = 4096
PATH = "/api/v1/sources/abc/preview"
TRACEPARENT = "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"


def _app(entered: list[int]) -> FastAPI:
    app = FastAPI()

    @app.post(PATH)
    async def preview(file: Annotated[UploadFile, File()]) -> dict[str, int]:
        entered.append(1)
        return {"size": len(await file.read())}

    # The order the application uses: the trace middleware is the outermost.
    app.add_middleware(BodyLimitMiddleware, max_bytes=LIMIT)
    app.add_middleware(TraceMiddleware)
    install_error_handlers(app)
    return app


def _client(app: FastAPI) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t")


def _multipart(total: int) -> tuple[bytes, str]:
    """A valid multipart body of exactly `total` bytes."""

    def build(n: int) -> tuple[bytes, str]:
        request = httpx.Request("POST", "http://t/", files={"file": ("f.csv", b"x" * n)})
        return request.read(), request.headers["content-type"]

    overhead = len(build(0)[0])
    body, content_type = build(total - overhead)
    assert len(body) == total
    return body, content_type


@pytest.mark.req("FR-450")
async def test_a_declared_length_over_the_limit_is_refused_before_the_handler() -> None:
    entered: list[int] = []
    body, content_type = _multipart(LIMIT + 1)
    async with _client(_app(entered)) as client:
        response = await client.post(
            PATH, content=body, headers={"content-type": content_type, "traceparent": TRACEPARENT}
        )
    assert response.status_code == 413
    problem = response.json()
    assert problem["code"] == "PAYLOAD_TOO_LARGE"
    assert problem["trace_id"] == "0af7651916cd43dd8448eb211c80319c"
    assert response.headers["content-type"].startswith("application/problem+json")
    assert entered == []


@pytest.mark.req("FR-450")
async def test_a_chunked_body_over_the_limit_is_refused() -> None:
    entered: list[int] = []
    pulled = 0
    chunk = b"y" * 1000

    async def body() -> AsyncIterator[bytes]:
        nonlocal pulled
        for _ in range(100):
            pulled += 1
            yield chunk

    async with _client(_app(entered)) as client:
        response = await client.post(
            PATH,
            content=body(),
            headers={"content-type": "multipart/form-data; boundary=b", "traceparent": TRACEPARENT},
        )
    assert response.status_code == 413
    problem = response.json()
    assert problem["code"] == "PAYLOAD_TOO_LARGE"
    # The ordering trap, part 1: the cap is raised from `receive` as `HTTPException` (a
    # `PlatformError` there would be rewritten as a 400 by FastAPI's body parsing), and
    # part 2: the problem still carries the trace id, because the trace middleware is outside.
    assert problem["trace_id"] == "0af7651916cd43dd8448eb211c80319c"
    # The body was not read to its end: the refusal came as the limit was passed.
    assert pulled <= LIMIT // len(chunk) + 2
    assert entered == []


@pytest.mark.req("FR-450")
@pytest.mark.parametrize(("size", "status"), [(LIMIT - 1, 200), (LIMIT, 200), (LIMIT + 1, 413)])
async def test_a_body_at_the_limit_passes(size: int, status: int) -> None:
    entered: list[int] = []
    body, content_type = _multipart(size)
    async with _client(_app(entered)) as client:
        response = await client.post(PATH, content=body, headers={"content-type": content_type})
    assert response.status_code == status
    assert bool(entered) == (status == 200)
