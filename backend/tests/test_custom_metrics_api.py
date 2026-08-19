"""Custom Metrics over HTTP (`02` FR-MODEL-108).

Parallel to `test_custom_objectives.py`'s one HTTP test, but this is the file that owns the
Custom Metric endpoints — the service and the database-layer invariants
(`test_custom_metrics_table.py`) are proved elsewhere. This proves the surface a caller
actually reaches: create answers 201 with a draft, the artifact is readable back, the
certificate 404s by name before certification, an uncertified metric cannot be submitted,
a metric with no declared direction is refused at creation, and re-creating a slug takes
the next version.

Follows `test_api_datasets.py`'s client fixture and auth headers exactly: plain sync tests
over the DB-backed `api_client`, dev-auth headers from a granted role, not the async
`client`/`pytest.mark.anyio` pattern a from-scratch draft of this file might reach for —
`asyncio_mode = "auto"` (root `pyproject.toml`) is what lets `pytest_asyncio.fixture` async
fixtures resolve transparently inside these sync tests.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from backend.tests.test_api_datasets import _headers
from fastapi.testclient import TestClient

_BODY = {
    "slug": "capped-gamma-nll",
    "template": "capped_gamma",
    "params": {"cap": 250000},
    "applicability": {
        "responses": ["claim_severity"],
        "backends": ["xgboost"],
        "offset_required": False,
        "y_domain": {"min_exclusive": 0.0},
    },
    "direction": "lower_is_better",
}


@pytest.fixture
def client(api_client: TestClient) -> TestClient:
    """The shared DB-backed client, under the name this module's tests already use."""
    return api_client


@pytest_asyncio.fixture
async def actuary(workspace_id, principal, grant) -> dict[str, str]:
    await grant("pricing_actuary")
    return _headers(principal.id, workspace_id)


@pytest.mark.req("FR-MODEL-45")
def test_create_returns_201_and_a_draft(
    client: TestClient, actuary: dict[str, str]
) -> None:
    response = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["version"] == 1
    assert body["certificate_id"] is None


@pytest.mark.req("FR-MODEL-108")
def test_the_created_metric_is_readable(
    client: TestClient, actuary: dict[str, str]
) -> None:
    created = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary).json()
    response = client.get(f"/api/v1/custom-metrics/{created['id']}", headers=actuary)
    assert response.status_code == 200
    assert response.json()["slug"] == "capped-gamma-nll"


@pytest.mark.req("FR-MODEL-108")
def test_the_certificate_404s_before_certification_and_names_the_metric(
    client: TestClient, actuary: dict[str, str]
) -> None:
    created = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary).json()
    response = client.get(
        f"/api/v1/custom-metrics/{created['id']}/certificate", headers=actuary
    )
    assert response.status_code == 404
    assert created["id"] in response.text


@pytest.mark.req("FR-MODEL-105")
def test_an_uncertified_metric_cannot_be_submitted(
    client: TestClient, actuary: dict[str, str]
) -> None:
    """The negative half of the lifecycle: `draft -> review` is not an edge.

    The 409's `code` is `VALIDATION_FAILED` — the same code
    `submit_custom_objective` raises for a bad transition (`objectives.submit_for_review`),
    asserted here rather than left implicit so a second code meaning the same thing is
    never introduced by mistake.
    """
    created = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary).json()
    response = client.post(
        f"/api/v1/custom-metrics/{created['id']}/submit", headers=actuary
    )
    assert response.status_code == 409
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-MODEL-104")
def test_a_metric_without_a_direction_is_refused(
    client: TestClient, actuary: dict[str, str]
) -> None:
    body = {k: v for k, v in _BODY.items() if k != "direction"}
    response = client.post("/api/v1/custom-metrics", json=body, headers=actuary)
    assert response.status_code == 422


@pytest.mark.req("FR-MODEL-103")
def test_creating_the_same_slug_twice_makes_a_second_version(
    client: TestClient, actuary: dict[str, str]
) -> None:
    first = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary).json()
    second = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary).json()
    assert (first["version"], second["version"]) == (1, 2)
