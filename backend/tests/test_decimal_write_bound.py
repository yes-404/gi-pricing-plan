"""FR-21's bound on writing, through a real request model (N1, to-lead 2026-11-05 20:46:28).

Validation takes any exponent (G3), so `1E+999999999` is accepted; writing it positionally is
refused, and the refusal reaches the caller as a 422 with a named code, never a 500.
The echo routes below return the real `ReconcileRequest` (`api/peril_structures.py`), whose
`tolerance` is a `DecimalStr`. Only exponents of 400 are echoed, so no test writes a gigabyte.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.api.peril_structures import ReconcileRequest
from app.config import Environment, Settings
from app.main import create_app
from app.platform.perils import reconcile_payload


@pytest.fixture
def client() -> TestClient:
    app = create_app(Settings(environment=Environment.LOCAL, version="test"))

    @app.post("/_test/accept")
    async def _accept(body: ReconcileRequest) -> dict[str, bool]:
        return {"ok": True}

    @app.post("/_test/echo")
    async def _echo(body: ReconcileRequest) -> ReconcileRequest:
        return body

    return TestClient(app, raise_server_exceptions=False)


def _body(tolerance: str) -> dict[str, str]:
    return {"observed_column": "o", "exposure_column": "e", "tolerance": tolerance}


@pytest.mark.req("FR-21")
def test_validation_accepts_an_exponent_past_the_bound(client: TestClient) -> None:
    assert client.post("/_test/accept", json=_body("1E+999999999")).status_code == 200


@pytest.mark.req("FR-21")
@pytest.mark.parametrize("tolerance", ["1E+400", "1E-400"])
def test_echoing_a_value_past_the_bound_is_a_422_with_a_named_code(
    client: TestClient, tolerance: str
) -> None:
    response = client.post("/_test/echo", json=_body(tolerance))
    assert response.status_code == 422, response.text
    assert response.headers["content-type"].startswith("application/problem+json")
    problem = response.json()
    assert problem["code"] == "DECIMAL_OUT_OF_RANGE"
    assert tolerance not in response.text  # NFR-499: the value is not echoed back


@pytest.mark.req("FR-21")
def test_echoing_a_value_inside_the_bound_is_written_positionally(client: TestClient) -> None:
    response = client.post("/_test/echo", json=_body("1E-7"))
    assert response.status_code == 200
    assert response.json()["tolerance"] == "0.0000001"


@pytest.mark.req("FR-21")
def test_the_reconcile_job_payload_does_not_write_the_tolerance_positionally() -> None:
    """The one real route that takes the field (`POST /peril-structures/{id}/reconcile`) puts
    `str(tolerance)` in the Job's parameters (`platform/perils.py:reconcile_payload`) and
    answers with a Job, so `1E+999999999` crosses it as 12 characters, not a gigabyte."""
    payload = reconcile_payload(
        row=type("Row", (), {"id": "x"})(),  # type: ignore[arg-type]
        tolerance=Decimal("1E+999999999"),
        observed_column="o",
        exposure_column="e",
    )
    assert payload["tolerance"] == "1E+999999999"
