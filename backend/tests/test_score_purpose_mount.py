"""FR-218's real check over HTTP: `POST /api/v1/score` and `POST /api/v1/score/compare`.

WK-1250 Slice 3 (`SL-1341`; `PL-1629` acceptance 4 and 5). A Rating Version whose only purpose
mount selects `cancellation` re-produces the annual premium halved for a cancellation, prices a
`new_business` quote exactly as it would without the mount, and refuses a
`mid_term_adjustment` quote with `INPUT_CONTRACT_VIOLATION` (a 422): no mount for that purpose
is inlined in the bundle. `packages/pricing-core/tests/test_rating_purpose_mount.py` is the
`pricing-core` half; the fixtures here are written out, as `test_score_as_at.py` does.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_rating_version_compile import _headers, _insert_version
from fastapi.testclient import TestClient

from app.db.session import Database
from app.platform.blobs import BlobStore
from app.worker.rating_handlers import register_rating_handlers
from app.worker.tasks import execute_job
from model_schema import JobStatus, Principal

SCORE_URL = "/api/v1/score"
COMPARE_URL = "/api/v1/score/compare"
SCORED_REF = "rating_version:minimal-rv@1"
CANCEL_REF = "sub_graph:cancel-refund@1"


def _cancel_sub_graph() -> dict[str, Any]:
    return {
        "slug": "cancel-refund",
        "inputs": [{"name": "annual", "type": "decimal"}],
        "outputs": [{"name": "refund", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_prorata", "type": "expression", "label": "Pro-rata",
             "expr": "annual * 0.5", "result_type": "decimal",
             "consumes": ["annual"], "produces": "refund"},
        ],
        "change_note": "first cut",
    }


def _algorithm() -> dict[str, Any]:
    """The payable is the annual premium; the cancellation mount re-produces it halved."""
    return {
        "slug": "minimal",
        "version": 1,
        "input_contract": [{"name": "premium_in", "type": "int", "nullable": False}],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In", "input_name": "premium_in",
             "on_missing": "error", "produces": "premium_in"},
            {"step_id": "s_annual", "type": "expression", "label": "Annual premium",
             "expr": "premium_in * 1", "result_type": "decimal",
             "consumes": ["premium_in"], "produces": "annual_premium"},
            {"step_id": "s_payable", "type": "expression", "label": "Payable",
             "expr": "annual_premium", "result_type": "money_minor",
             "consumes": ["annual_premium"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor",
             "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["payable"]},
        ],
        "sub_graphs": [
            {"ref": CANCEL_REF, "mount_point": "m_cancel", "purposes": ["cancellation"],
             "inputs": {"annual": "annual_premium"}, "outputs": {"refund": "annual_premium"}},
        ],
    }


def _context(purpose: str) -> dict[str, Any]:
    return {
        "purpose": purpose,
        "quoted_at": "2026-08-30T09:00:00Z",
        "effective_date": "2026-09-01",
        "inputs": {"premium_in": 1000},
    }


def _scored(purpose: str) -> dict[str, Any]:
    return {**_context(purpose), "options": {"rating_version_ref": SCORED_REF}}


@pytest.fixture
async def headers(principal: Principal, workspace_id: UUID, grant: Any) -> dict[str, str]:
    await grant("admin")
    await grant("analyst")
    return _headers(principal, workspace_id)


@pytest.fixture
def scoring_headers(
    api_client: TestClient, headers: dict[str, str], workspace_id: UUID
) -> dict[str, str]:
    created = api_client.post(
        "/api/v1/service-accounts",
        json={"slug": "purpose-mount", "environments": ["uat"], "permissions": ["score:execute"]},
        headers=headers,
    )
    assert created.status_code == 201, created.text
    return {"X-API-Key": created.json()["key"], "Workspace-Id": str(workspace_id)}


@pytest.fixture
async def compiled_version(
    api_client: TestClient,
    headers: dict[str, str],
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    principal: Principal,
) -> None:
    """A genuinely compiled Rating Version at `SCORED_REF` whose one mount is for `cancellation`."""
    register_rating_handlers()
    made = api_client.post("/api/v1/sub-graphs", json=_cancel_sub_graph(), headers=headers)
    assert made.status_code == 201, made.text
    created = api_client.post("/api/v1/rating-algorithms", json=_algorithm(), headers=headers)
    assert created.status_code in (200, 201), created.text
    row = await _insert_version(
        database, workspace_id, principal.id,
        algorithm_ref="rating_algorithm:minimal@1",
        pins={
            "rate_tables": [], "models": [], "reference_tables": [],
            "custom_objectives": [], "sub_graphs": [CANCEL_REF],
        },
    )
    response = api_client.post(f"/api/v1/rating-versions/{row.id}/compile", headers=headers)
    assert response.status_code == 202, response.text
    status = await execute_job(database, UUID(response.json()["id"]), blob_store)
    assert status is JobStatus.SUCCEEDED, status


@pytest.mark.req("FR-218")
def test_score_prices_a_cancellation_with_the_purpose_mount(
    api_client: TestClient, scoring_headers: dict[str, str], compiled_version: None
) -> None:
    response = api_client.post(SCORE_URL, json=_scored("cancellation"), headers=scoring_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["outputs"]["payable_premium_minor"] == 500
    assert body["premium_ladder"][-1]["value_minor"] == 500


@pytest.mark.req("FR-218")
def test_score_prices_new_business_as_if_the_cancellation_mount_were_absent(
    api_client: TestClient, scoring_headers: dict[str, str], compiled_version: None
) -> None:
    response = api_client.post(SCORE_URL, json=_scored("new_business"), headers=scoring_headers)

    assert response.status_code == 200, response.text
    assert response.json()["outputs"]["payable_premium_minor"] == 1000


@pytest.mark.req("FR-218")
def test_score_refuses_a_mid_term_adjustment_the_cancellation_mount_does_not_serve(
    api_client: TestClient, scoring_headers: dict[str, str], compiled_version: None
) -> None:
    response = api_client.post(
        SCORE_URL, json=_scored("mid_term_adjustment"), headers=scoring_headers
    )

    assert response.status_code == 422, response.text
    problem = response.json()
    assert problem["code"] == "INPUT_CONTRACT_VIOLATION"
    assert "interim" not in response.text


@pytest.mark.req("FR-218")
def test_score_compare_prices_each_side_by_its_purposes_graph(
    api_client: TestClient, headers: dict[str, str], compiled_version: None
) -> None:
    body = {"context": _context("cancellation"), "base": SCORED_REF, "comparison": SCORED_REF}
    response = api_client.post(COMPARE_URL, json=body, headers=headers)

    assert response.status_code == 200, response.text
    served = response.json()
    assert served["base"]["outputs"]["payable_premium_minor"] == 500
    assert served["comparison"]["outputs"]["payable_premium_minor"] == 500


@pytest.mark.req("FR-218")
def test_score_compare_refuses_a_mid_term_adjustment_naming_the_failing_side(
    api_client: TestClient, headers: dict[str, str], compiled_version: None
) -> None:
    body = {
        "context": _context("mid_term_adjustment"), "base": SCORED_REF, "comparison": SCORED_REF,
    }
    response = api_client.post(COMPARE_URL, json=body, headers=headers)

    assert response.status_code == 422, response.text
    assert response.json()["code"] == "INPUT_CONTRACT_VIOLATION"
