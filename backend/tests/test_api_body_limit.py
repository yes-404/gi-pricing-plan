"""FR-450: a request body past the stated limit is a 413 before the handler (FD-1802).

DB-free: a small app carries the middleware, the trace middleware outside it, the error
handlers and one `File()` route, with a sentinel that records whether the handler ran.
"""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from typing import Annotated

import httpx
import pytest
from fastapi import FastAPI, File, UploadFile

from app.api import body_limit
from app.api.body_limit import MIB, BodyLimitMiddleware
from app.config import Environment, Settings
from app.errors import install_error_handlers
from app.main import create_app
from app.observability.middleware import TraceMiddleware

LIMIT = 4096
CHUNK = 512
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
    payload, content_type = _multipart(LIMIT * 10)

    async def body() -> AsyncIterator[bytes]:
        nonlocal pulled
        for start in range(0, len(payload), CHUNK):
            pulled += 1
            yield payload[start : start + CHUNK]

    async with _client(_app(entered)) as client:
        response = await client.post(
            PATH,
            content=body(),
            headers={"content-type": content_type, "traceparent": TRACEPARENT},
        )
    assert response.status_code == 413
    problem = response.json()
    assert problem["code"] == "PAYLOAD_TOO_LARGE"
    # The ordering trap, part 1: the cap is raised from `receive` as `HTTPException` (a
    # `PlatformError` there would be rewritten as a 400 by FastAPI's body parsing), and
    # part 2: the problem still carries the trace id, because the trace middleware is outside.
    assert problem["trace_id"] == "0af7651916cd43dd8448eb211c80319c"
    # The body was not read to its end: the refusal came as the limit was passed.
    assert pulled <= LIMIT // CHUNK + 2
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


def _unpaired() -> list[str]:
    """Routes that declare 413 without a cap, and caps that match no declaring route."""
    app = create_app(Settings(environment=Environment.LOCAL, version="test"))
    paths = app.openapi()["paths"]
    declared = {p for p, ops in paths.items() if any("413" in op.get("responses", {}) for op in ops.values())}
    assert declared
    uncapped = [p for p in declared if not any(r.match(p) for r in body_limit.CAPPED_ROUTES)]
    dangling = [r.pattern for r in body_limit.CAPPED_ROUTES if not any(r.match(p) for p in declared)]
    return [*uncapped, *dangling]


@pytest.mark.req("FR-450")
def test_the_capped_routes_are_the_routes_that_declare_413() -> None:
    assert _unpaired() == []


@pytest.mark.req("FR-450")
def test_a_declaration_without_a_cap_or_a_cap_without_a_declaration_is_caught(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The proof by break: each direction of the pairing goes red when it is broken."""
    first, *_ = body_limit.CAPPED_ROUTES
    monkeypatch.setattr(body_limit, "CAPPED_ROUTES", (first,))
    assert _unpaired()  # a route declares 413 and is not capped
    monkeypatch.setattr(body_limit, "CAPPED_ROUTES", (*body_limit.CAPPED_ROUTES, re.compile("^/nowhere$")))
    assert "^/nowhere$" in _unpaired()


@pytest.mark.req("FR-450")
async def test_the_application_caps_its_real_upload_route_before_authentication() -> None:
    """The wiring: `create_app` refuses an oversized body with no credentials, with a trace id."""
    app = create_app(Settings(environment=Environment.LOCAL, version="test", max_upload_body_mib=1))
    body, content_type = _multipart(MIB + 1)
    async with _client(app) as client:
        response = await client.post(
            "/api/v1/sources/abc/preview",
            content=body,
            headers={"content-type": content_type, "traceparent": TRACEPARENT},
        )
    assert response.status_code == 413
    assert response.json()["code"] == "PAYLOAD_TOO_LARGE"
    assert response.json()["trace_id"] == "0af7651916cd43dd8448eb211c80319c"
    assert "1 MiB" in response.json()["detail"]


@pytest.mark.req("FR-450")
def test_the_limit_is_a_typed_setting_defaulting_to_64_mib() -> None:
    assert Settings(environment=Environment.LOCAL, version="test").max_upload_body_mib == 64
    with pytest.raises(ValueError, match="max_upload_body_mib"):
        Settings(environment=Environment.LOCAL, version="test", max_upload_body_mib=0)
