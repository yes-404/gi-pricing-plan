"""The approval request's one shape (FD-1416; PL-1528).

Task 1 characterises what the routes emit at the base tree and pins the decision values; the
later tasks add the typed-2xx and contract tests to this module.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import select

from app.config import Environment, Settings
from app.db.models import ApprovalRequestRow, RatingVersionRow
from app.db.session import Database
from app.main import create_app
from app.platform import approvals, audit
from backend.tests.test_api_approvals import _headers
from backend.tests.test_deployment_route_types import APPROVAL_REQUEST_KEYS
from model_schema import ActorKind, JobSource, Principal, new_uuid7

#: Who created the versions these tests submit: nobody who submits or decides here (`06`
#: FR-353 keeps an author out of the approval, and a version without a creation event fails
#: closed).
AUTHOR = Principal(kind=ActorKind.USER, id=new_uuid7(), display="author@insurer.example")


@pytest.fixture
def client() -> TestClient:
    from backend.tests.conftest_db import test_blob_bucket, test_database_url

    settings = Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        blob_bucket=test_blob_bucket(),
    )
    with TestClient(create_app(settings), raise_server_exceptions=False) as c:
        yield c


async def _seat(grant: Any, workspace_id: UUID, role: str) -> dict[str, str]:
    who = new_uuid7()
    await grant(role, principal_id=who)
    return _headers(who, workspace_id)


@pytest_asyncio.fixture
async def analyst(grant: Any, workspace_id: UUID) -> dict[str, str]:
    return await _seat(grant, workspace_id, "analyst")


@pytest_asyncio.fixture
async def approver(grant: Any, workspace_id: UUID) -> dict[str, str]:
    return await _seat(grant, workspace_id, "approver")


async def _rating_version_in_review(database: Database, workspace_id: UUID) -> str:
    """A Rating Version in `review`, with the creation event the approval path requires."""
    slug = f"rv-{uuid4().hex[:8]}"
    ref = f"rating_version:{slug}@1"
    async with database.unit_of_work() as session:
        session.add(
            RatingVersionRow(
                workspace_id=workspace_id,
                slug=slug,
                version=1,
                status="review",
                dataset_version_id=uuid4(),
                model_ref="model:motor-ad-frequency@7",
                created_by=AUTHOR.id,
            )
        )
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=AUTHOR,
            source=JobSource.API,
            action=approvals.CREATION_ACTIONS["rating_version"],
            entity_ref=ref,
        )
    return ref


async def _submitted(
    client: TestClient, database: Database, workspace_id: UUID, analyst: dict[str, str]
) -> tuple[str, dict[str, Any]]:
    ref = await _rating_version_in_review(database, workspace_id)
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": ref, "change_summary": "go"},
        headers=analyst,
    )
    assert created.status_code == 201, created.text
    return ref, created.json()


def _decide(client: TestClient, headers: dict[str, str], request_id: str, decision: str):
    return client.post(
        f"/api/v1/approval-requests/{request_id}/decide",
        json={"decision": decision, "comment": "reviewed"},
        headers=headers,
    )


# -- Acceptance 1: what the routes emit at the base tree ------------------------------------


@pytest.mark.req("FR-9")
async def test_the_get_and_list_routes_emit_the_declared_keys(
    client: TestClient, database: Database, workspace_id: UUID, analyst: dict[str, str]
) -> None:
    """Characterisation (PL-1528 Acceptance 1): the two routes no test pinned. Green at the
    base tree; Task 3 edits `APPROVAL_REQUEST_KEYS` deliberately."""
    _, created = await _submitted(client, database, workspace_id, analyst)

    one = client.get(f"/api/v1/approval-requests/{created['id']}", headers=analyst)
    assert one.status_code == 200, one.text
    assert set(one.json()) == APPROVAL_REQUEST_KEYS

    listed = client.get("/api/v1/approval-requests", headers=analyst)
    assert listed.status_code == 200, listed.text
    items = listed.json()["items"]
    assert items, "the list route returned no request to characterise"
    for item in items:
        assert set(item) == APPROVAL_REQUEST_KEYS


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("decision", ["approve", "reject", "request_changes"])
async def test_a_decision_reads_back_as_the_ruled_value(
    decision: str,
    client: TestClient,
    database: Database,
    workspace_id: UUID,
    analyst: dict[str, str],
    approver: dict[str, str],
) -> None:
    """DP-1 (a), `RL-1522`: the code's verbs. Green at the base tree; pins them against a
    later rename (PL-1528 Acceptance 5)."""
    _, created = await _submitted(client, database, workspace_id, analyst)
    decided = _decide(client, approver, created["id"], decision)
    assert decided.status_code == 200, decided.text
    assert [d["decision"] for d in decided.json()["decisions"]] == [decision]
    read_back = client.get(f"/api/v1/approval-requests/{created['id']}", headers=analyst)
    assert [d["decision"] for d in read_back.json()["decisions"]] == [decision]


# -- Acceptance 12 and 13: behaviour a Rating Version already has, pinned (owed by RL-1522) ---


@pytest.mark.req("FR-351")
async def test_a_rating_version_in_review_refuses_a_second_request(
    client: TestClient, database: Database, workspace_id: UUID, analyst: dict[str, str]
) -> None:
    """The partial unique index `uq_approval_requests_open_artifact`, whose `IntegrityError`
    `service.submit` turns into a 409 (PL-1528 Acceptance 12)."""
    ref, _ = await _submitted(client, database, workspace_id, analyst)
    again = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": ref, "change_summary": "again"},
        headers=analyst,
    )
    assert again.status_code == 409, again.text
    assert again.json()["title"] == "This artifact version is already under review"


@pytest.mark.req("FR-355")
async def test_changes_requested_returns_a_rating_version_to_draft(
    client: TestClient,
    database: Database,
    workspace_id: UUID,
    analyst: dict[str, str],
    approver: dict[str, str],
) -> None:
    """`_target_status` maps `CHANGES_REQUESTED` to `DRAFT`; `_carry_to_the_artifact` applies
    it (PL-1528 Acceptance 13)."""
    ref, created = await _submitted(client, database, workspace_id, analyst)
    decided = _decide(client, approver, created["id"], "request_changes")
    assert decided.status_code == 200, decided.text
    assert decided.json()["status"] == "changes_requested"

    slug, version = ref.split(":", 1)[1].rsplit("@", 1)
    async with database.session() as session:
        rating_version = (
            await session.execute(
                select(RatingVersionRow).where(
                    RatingVersionRow.workspace_id == workspace_id,
                    RatingVersionRow.slug == slug,
                    RatingVersionRow.version == int(version),
                )
            )
        ).scalar_one()
        request = await session.get(ApprovalRequestRow, UUID(created["id"]))
    assert request is not None and request.status == "changes_requested"
    assert rating_version.status == "draft"


# -- Acceptance 2: every route's 2xx is an ApprovalRequest (FD-1416) -------------------------


@pytest.mark.req("FR-9")
async def test_every_approval_route_returns_an_approval_request(
    client: TestClient,
    database: Database,
    workspace_id: UUID,
    analyst: dict[str, str],
    approver: dict[str, str],
) -> None:
    """The five routes `to_dict` served (DP-7 (a) puts the list in scope), each body through
    `ApprovalRequest.model_validate`. Red at the base tree: `workspace_id` is missing and
    `environment` is refused by `extra="forbid"`."""
    from model_schema import ApprovalRequest

    _, submitted = await _submitted(client, database, workspace_id, analyst)
    ApprovalRequest.model_validate(submitted)

    one = client.get(f"/api/v1/approval-requests/{submitted['id']}", headers=analyst)
    assert one.status_code == 200, one.text
    ApprovalRequest.model_validate(one.json())

    listed = client.get("/api/v1/approval-requests", headers=analyst)
    assert listed.status_code == 200, listed.text
    assert listed.json()["items"]
    for item in listed.json()["items"]:
        ApprovalRequest.model_validate(item)

    decided = _decide(client, approver, submitted["id"], "approve")
    assert decided.status_code == 200, decided.text
    ApprovalRequest.model_validate(decided.json())

    _, second = await _submitted(client, database, workspace_id, analyst)
    withdrawn = client.post(
        f"/api/v1/approval-requests/{second['id']}/withdraw",
        json={"reason": "not ready"},
        headers=approver,
    )
    assert withdrawn.status_code == 200, withdrawn.text
    ApprovalRequest.model_validate(withdrawn.json())


# -- Acceptance 3: the OpenAPI 2xx is a $ref --------------------------------------------------

_REF = {"$ref": "#/components/schemas/ApprovalRequest"}


@pytest.mark.req("FR-451")
def test_the_approval_routes_publish_the_approval_request_ref() -> None:
    """The committed `generated.json`: red at the base tree, where `ApprovalRequest` is not a
    component and the four 2xx are open objects."""
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[2] / "docs" / "contracts" / "openapi" / "generated.json"
    paths = json.loads(path.read_text())["paths"]
    base = "/api/v1/approval-requests"
    found: dict[str, Any] = {}
    for route, method in (
        (base, "post"),
        (f"{base}/{{request_id}}", "get"),
        (f"{base}/{{request_id}}/decide", "post"),
        (f"{base}/{{request_id}}/withdraw", "post"),
    ):
        responses = paths[route][method]["responses"]
        (code,) = (c for c in responses if c.startswith("2"))
        found[f"{method.upper()} {route}"] = responses[code]["content"]["application/json"]["schema"]
    wrong = {k: v for k, v in found.items() if v != _REF}
    assert not wrong, f"2xx that is not {_REF}: {wrong}"

    listed = paths[base]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    page = json.loads(path.read_text())["components"]["schemas"][listed["$ref"].rsplit("/", 1)[-1]]
    assert page["properties"]["items"]["items"] == _REF, page["properties"]["items"]
