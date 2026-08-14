"""The approval API (`06` §5.1) — the state machine over HTTP."""

from __future__ import annotations

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER, DEV_WORKSPACE_HEADER
from app.config import Environment, Settings
from app.main import create_app
from model_schema import new_uuid7

MODEL = "model:motor-ad-frequency@7"


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
    )


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


def _headers(principal_id, workspace_id) -> dict[str, str]:
    return {
        DEV_PRINCIPAL_HEADER: str(principal_id),
        DEV_WORKSPACE_HEADER: str(workspace_id),
    }


@pytest_asyncio.fixture
async def submitter_headers(workspace_id, principal, grant) -> dict[str, str]:
    await grant("analyst")
    return _headers(principal.id, workspace_id)


@pytest_asyncio.fixture
async def approver_headers(workspace_id, grant) -> dict[str, str]:
    approver = new_uuid7()
    await grant("approver", principal_id=approver)
    return _headers(approver, workspace_id)


@pytest.mark.req("FR-GOV-9")
def test_submitting_returns_a_request_in_review(
    client: TestClient, submitter_headers
) -> None:
    response = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit on 2026H1."},
        headers=submitter_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "review"
    assert body["artifact_ref"] == MODEL
    assert body["approvers_required"] == 1


@pytest.mark.req("FR-GOV-11")
async def test_the_submitter_cannot_approve_even_holding_the_approver_role(
    client: TestClient, workspace_id, principal, grant, submitter_headers
) -> None:
    """R1 end to end, and the grant is what makes it a test of R1.

    Without also granting the submitter `approver`, the route's permission dependency
    refuses first and the response says PERMISSION_DENIED — which would pass while proving
    nothing about separation of duties.
    """
    await grant("approver")

    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit."},
        headers=submitter_headers,
    ).json()

    response = client.post(
        f"/api/v1/approval-requests/{created['id']}/decide",
        json={"decision": "approve"},
        headers=submitter_headers,
    )
    assert response.status_code == 403
    assert response.json()["code"] == "SUBMITTER_CANNOT_APPROVE"


@pytest.mark.req("FR-GOV-9")
def test_an_approver_approves(
    client: TestClient, submitter_headers, approver_headers
) -> None:
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit."},
        headers=submitter_headers,
    ).json()

    body = client.post(
        f"/api/v1/approval-requests/{created['id']}/decide",
        json={"decision": "approve", "comment": "Diagnostics clean."},
        headers=approver_headers,
    ).json()
    assert body["status"] == "approved"
    assert body["approvers_recorded"] == 1
    assert body["decisions"][0]["comment"] == "Diagnostics clean."


@pytest.mark.req("FR-GOV-2")
def test_deciding_requires_the_permission(
    client: TestClient, submitter_headers
) -> None:
    """Negative: an analyst may submit but not decide."""
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit."},
        headers=submitter_headers,
    ).json()
    other = new_uuid7()
    response = client.post(
        f"/api/v1/approval-requests/{created['id']}/decide",
        json={"decision": "approve"},
        headers=_headers(other, submitter_headers[DEV_WORKSPACE_HEADER]),
    )
    assert response.status_code == 403


@pytest.mark.req("FR-GOV-15")
def test_withdrawing_after_deployment_is_refused(
    client: TestClient, submitter_headers, approver_headers
) -> None:
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit."},
        headers=submitter_headers,
    ).json()
    client.post(
        f"/api/v1/approval-requests/{created['id']}/decide",
        json={"decision": "approve"},
        headers=approver_headers,
    )
    response = client.post(
        f"/api/v1/approval-requests/{created['id']}/withdraw",
        json={"reason": "changed my mind", "artifact_is_live": True},
        headers=approver_headers,
    )
    assert response.status_code == 409
    assert response.json()["code"] == "WITHDRAW_AFTER_DEPLOY_FORBIDDEN"


@pytest.mark.req("FR-GOV-9")
def test_a_malformed_artifact_reference_is_refused(
    client: TestClient, submitter_headers
) -> None:
    """ID-3: the reference is the pin. A malformed one pins nothing."""
    response = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": "model:motor-ad-frequency", "change_summary": "x"},
        headers=submitter_headers,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-GOV-16")
def test_requests_are_listable_and_filterable(
    client: TestClient, submitter_headers, approver_headers
) -> None:
    """The inbox *query* (FR-GOV-16). Evidence inline is deferred — it needs the artifacts
    W4 and W5 produce, and shipping a list under that name would claim the requirement
    while delivering the easy half."""
    for i in (7, 8, 9):
        client.post(
            "/api/v1/approval-requests",
            json={"artifact_ref": f"model:motor-ad-frequency@{i}", "change_summary": "x"},
            headers=submitter_headers,
        )
    body = client.get("/api/v1/approval-requests?status=review", headers=approver_headers).json()
    assert body["total_estimate"] == 3
    assert all(i["status"] == "review" for i in body["items"])


@pytest.mark.req("FR-GOV-12")
def test_the_default_policy_is_the_documented_one(
    client: TestClient, submitter_headers
) -> None:
    """`06` §4.2: a rating version needs two approvers, a model one."""
    body = client.get("/api/v1/approval-policy", headers=submitter_headers).json()
    required = {p["artifact_type"]: p["approvers_required"] for p in body["policies"]}
    assert required["rating_version"] == 2
    assert required["model"] == 1
    assert body["submitter_may_approve"] is False


@pytest.mark.req("FR-GOV-12")
async def test_replacing_the_policy_requires_admin(
    client: TestClient, workspace_id, grant, submitter_headers
) -> None:
    policy = client.get("/api/v1/approval-policy", headers=submitter_headers).json()
    denied = client.put("/api/v1/approval-policy", json=policy, headers=submitter_headers)
    assert denied.status_code == 403

    admin = new_uuid7()
    await grant("admin", principal_id=admin)
    allowed = client.put(
        "/api/v1/approval-policy",
        json=policy,
        headers=_headers(admin, workspace_id),
    )
    assert allowed.status_code == 200


@pytest.mark.req("FR-GOV-11")
async def test_a_policy_that_disables_separation_of_duties_is_refused(
    client: TestClient, workspace_id, grant
) -> None:
    """Negative: `06` R1 cannot be configured away, so the API must refuse to store it."""
    admin = new_uuid7()
    await grant("admin", principal_id=admin)
    response = client.put(
        "/api/v1/approval-policy",
        json={"policies": [], "submitter_may_approve": True},
        headers=_headers(admin, workspace_id),
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-OVR-13")
def test_another_workspaces_request_is_404(
    client: TestClient, submitter_headers
) -> None:
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit."},
        headers=submitter_headers,
    ).json()
    # The detail route needs only authentication, so the caller reaches the handler and
    # the 404 is about tenancy rather than about being refused a permission.
    other = _headers(submitter_headers[DEV_PRINCIPAL_HEADER], new_uuid7())
    response = client.get(f"/api/v1/approval-requests/{created['id']}", headers=other)
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
