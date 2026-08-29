"""FR-RATE-56's startup self-check, wired into the app lifespan (W11 Task 1.4, F-W11-1-3).

The requirement's own words: "A startup self-check asserts the round-trip; failing it
prevents the service starting." `assert_integer_minor_round_trip` (`pricing_core.rating.
compile`) has existed since W9-2 with exactly one caller, a test that calls it directly
(`packages/pricing-core/tests/test_rating_compile.py`) — the W9-2 audit booked FR-RATE-56
"delivered" on the strength of the function and that test alone, and nothing in the
service's own startup path called it (F-W11-1-3). This is the first production caller,
and the first test proving a *failing* check actually stops the service rather than the
function merely existing to be imported.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.config import Settings
from app.main import create_app


@pytest.mark.req("FR-RATE-56")
def test_the_app_starts_when_the_round_trip_holds(api_settings: Settings) -> None:
    """Positive control: on a real machine the check passes and startup proceeds — the
    same lifespan entry every other `api_client`-based backend test already relies on."""
    with TestClient(create_app(api_settings)):
        pass  # entering the lifespan without raising is the assertion.


@pytest.mark.req("FR-RATE-56")
def test_a_failing_round_trip_check_prevents_the_service_starting(
    monkeypatch: pytest.MonkeyPatch, api_settings: Settings
) -> None:
    """The negative half, stated as the violation FR-RATE-56 forbids: a broken check must
    stop startup, not merely exist and be ignored. `TestClient`'s context manager runs the
    ASGI lifespan's startup phase on `__enter__`; Starlette re-raises a startup exception
    there rather than swallowing it, so the app never becomes ready to serve a request.
    """

    def _broken() -> None:
        raise AssertionError("simulated FR-RATE-56 round-trip failure")

    monkeypatch.setattr(main_module, "assert_integer_minor_round_trip", _broken)

    with (
        pytest.raises(AssertionError, match="simulated FR-RATE-56"),
        TestClient(create_app(api_settings)),
    ):
        pytest.fail("the app must not finish starting when the self-check fails")
