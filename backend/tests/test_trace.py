"""R4 — a trace id from the edge inward, in the one format that correlates."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.observability.trace import (
    TRACE_ID_PATTERN,
    bind_trace_id,
    current_trace_id,
    new_trace_id,
    parse_traceparent,
    reset_trace_id,
)

VALID = "4bf92f3577b34da6a3ce929d0e0e4736"
ZERO = "0" * 32


@pytest.mark.req("FR-PLAT-38")
def test_generated_id_is_w3c_hex() -> None:
    """32 lowercase hex, not a ULID — this is what joins a log line to a span."""
    assert TRACE_ID_PATTERN.match(new_trace_id())


@pytest.mark.req("FR-PLAT-38")
def test_generated_ids_are_distinct() -> None:
    assert len({new_trace_id() for _ in range(200)}) == 200


@pytest.mark.req("FR-PLAT-39")
def test_traceparent_is_joined_not_replaced() -> None:
    """An inbound trace continues across the hop, or it is not one trace."""
    assert parse_traceparent(f"00-{VALID}-00f067aa0ba902b7-01") == VALID


@pytest.mark.req("FR-PLAT-39")
@pytest.mark.parametrize(
    "header",
    [
        None,
        "",
        "not-a-traceparent",
        f"00-{VALID}-00f067aa0ba902b7",          # missing flags
        f"00-{VALID[:31]}-00f067aa0ba902b7-01",  # trace id too short
        f"00-{VALID.upper()}-00f067aa0ba902b7-01",  # uppercase is not W3C
        f"00-{ZERO}-00f067aa0ba902b7-01",        # all-zero is the "no trace" sentinel
    ],
)
def test_unusable_traceparent_yields_none(header: str | None) -> None:
    """A bad header must not fail the request — it must only fail to correlate."""
    assert parse_traceparent(header) is None


@pytest.mark.req("FR-PLAT-38")
def test_binding_rejects_a_non_w3c_id() -> None:
    """Negative: a ULID must not be bindable, or the format promise means nothing."""
    with pytest.raises(ValueError, match="32 lowercase hex"):
        bind_trace_id("01JABCDEFGHJKMNPQRSTVWXYZ0")


@pytest.mark.req("FR-PLAT-38")
def test_context_is_restored_after_reset() -> None:
    assert current_trace_id() is None
    token = bind_trace_id(VALID)
    assert current_trace_id() == VALID
    reset_trace_id(token)
    assert current_trace_id() is None


@pytest.mark.req("FR-PLAT-42")
def test_response_carries_the_trace_id(client: TestClient) -> None:
    """A slow page has no error body to quote; the header is the only identifier."""
    response = client.get("/healthz")
    assert TRACE_ID_PATTERN.match(response.headers["x-trace-id"])


@pytest.mark.req("FR-PLAT-39")
def test_inbound_trace_appears_in_the_response(client: TestClient) -> None:
    response = client.get(
        "/healthz", headers={"traceparent": f"00-{VALID}-00f067aa0ba902b7-01"}
    )
    assert response.headers["x-trace-id"] == VALID


@pytest.mark.req("FR-PLAT-38")
def test_each_request_gets_its_own_trace(client: TestClient) -> None:
    """Negative: a leaked context variable would correlate unrelated requests."""
    first = client.get("/healthz").headers["x-trace-id"]
    second = client.get("/healthz").headers["x-trace-id"]
    assert first != second
