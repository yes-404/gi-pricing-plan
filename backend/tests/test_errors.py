"""Every non-2xx response is one shape, with a code and a trace id (`00` §5.3)."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.errors import PLATFORM_ERROR_CODES, PlatformError, install_error_handlers
from app.main import create_app
from app.observability.middleware import TraceMiddleware
from app.observability.trace import TRACE_ID_PATTERN

PROBLEM = "application/problem+json"


class _Body(BaseModel):
    count: int


@pytest.fixture
def failing_client(settings) -> TestClient:
    """An app with routes that fail in each of the four ways the handlers cover."""
    app = create_app(settings)

    @app.post("/_test/validate")
    async def _validate(body: _Body) -> dict[str, int]:
        return {"count": body.count}

    @app.get("/_test/platform-error")
    async def _platform_error() -> None:
        raise PlatformError(
            "JOB_NOT_CANCELLABLE",
            "Job is not cancellable",
            409,
            "Job has already finished.",
        )

    @app.get("/_test/boom")
    async def _boom() -> None:
        raise RuntimeError("password=hunter2 leaked into the exception message")

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.req("FR-PLAT-47")
def test_platform_error_renders_as_problem_json(failing_client: TestClient) -> None:
    response = failing_client.get("/_test/platform-error")
    assert response.status_code == 409
    assert response.headers["content-type"].startswith(PROBLEM)
    body = response.json()
    assert body["code"] == "JOB_NOT_CANCELLABLE"
    assert body["status"] == 409
    assert body["instance"] == "/_test/platform-error"
    assert body["type"].endswith("/job-not-cancellable")


@pytest.mark.req("FR-PLAT-42")
def test_every_problem_carries_a_trace_id(failing_client: TestClient) -> None:
    """R4: a support conversation starts with an identifier, not a screenshot."""
    for path in ("/_test/platform-error", "/_test/boom", "/no-such-route"):
        body = failing_client.get(path).json()
        assert TRACE_ID_PATTERN.match(body["trace_id"]), path


@pytest.mark.req("FR-PLAT-47")
def test_framework_404_is_a_problem_not_a_bare_detail(failing_client: TestClient) -> None:
    """Negative: Starlette's default `{"detail": ...}` would be a second error shape."""
    response = failing_client.get("/no-such-route")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith(PROBLEM)
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-PLAT-11")
def test_validation_failure_names_the_field(failing_client: TestClient) -> None:
    """A deterministic rejection must be renderable against the form that caused it."""
    response = failing_client.post("/_test/validate", json={"count": "not-an-int"})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_FAILED"
    assert body["errors"][0]["field"] == "count"
    assert body["errors"][0]["code"]


@pytest.mark.req("NFR-PLAT-7")
def test_unexpected_error_does_not_leak_the_exception_message(
    failing_client: TestClient,
) -> None:
    """R3: an exception string can carry a credential. The trace id is the way in."""
    response = failing_client.get("/_test/boom")
    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "INTERNAL_ERROR"
    assert "hunter2" not in response.text
    assert "password" not in response.text
    assert body["trace_id"]


@pytest.mark.req("FR-PLAT-47")
def test_unknown_error_code_is_refused_at_construction() -> None:
    """Negative: an unenumerated code reaches a client as something it cannot branch on."""
    with pytest.raises(ValueError, match="unknown error code"):
        PlatformError("NOT_A_REAL_CODE", "Nope", 400)


@pytest.mark.req("FR-PLAT-47")
def test_spec_error_codes_are_all_constructible() -> None:
    """The registry must match 07 §5.1 — a code in the spec but not here cannot be raised."""
    for code in PLATFORM_ERROR_CODES:
        assert PlatformError(code, "title", 400).code == code


@pytest.mark.req("FR-PLAT-42")
def test_problem_response_survives_middleware_ordering() -> None:
    """Trace binding is outermost, so even a handler-less app problem carries the id."""
    app = FastAPI()
    app.add_middleware(TraceMiddleware)
    install_error_handlers(app)
    body = TestClient(app, raise_server_exceptions=False).get("/nope").json()
    assert TRACE_ID_PATTERN.match(body["trace_id"])


@pytest.mark.req("FR-PLAT-47")
def test_no_live_rating_version_is_registered_at_409() -> None:
    """Ruling 14's refusal code, registered before the branch that raises it.

    `POST /api/v1/score` with no `options.rating_version_ref` answers *"this platform
    has no live Rating Version to score you against"* rather than guessing one, and
    `live` is a property of a Deployment (FR-RATE-23), which is W14's. 409 because this
    backend already answers "the artifact is not in a state that permits this" at 409
    (`platform/datasets.py`, `jobs.py`, `rating_versions.py`, `approvals.py`), and the
    caller's operator resolves it by deploying a version and retrying.

    `PlatformError.__init__` refuses an unenumerated code, so the route's branch cannot
    be written before this registration exists — the mechanism that stops Ruling 14
    being half-applied.
    """
    error = PlatformError(
        "NO_LIVE_RATING_VERSION",
        "No live Rating Version",
        409,
        "Supply options.rating_version_ref.",
    )
    assert error.code == "NO_LIVE_RATING_VERSION"
    assert error.status_code == 409
