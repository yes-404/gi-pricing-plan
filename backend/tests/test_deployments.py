"""The Deployment and the Deployment Request (`03` §4.12, FR-267; WK-674 Slice 2, PL-1392 Task 5).

`RL-1401` item 1's five cases come first: the positive control (a), the submitter (b), the
fail-closed half (c), the parity test (d) and limb (ii) as ruled (e). Each is red first, with
the red quoted in `LG-1405`.

Every test starts from a fresh workspace and a fresh Rating Version slug. The Environments are
deployment-wide (`dev`, `uat`, `prod` are seeded by the migration), so a test that changed one
would change it for every later test; none does.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from backend.tests.approved_rows import add_approved
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment as RuntimeEnvironment
from app.config import Settings
from app.db.models import (
    ApprovalRequestRow,
    AuditEventRow,
    DeploymentRequestRow,
    EnvironmentRow,
    RatingVersionRow,
)
from app.db.session import Database
from model_schema import DEFAULT_POLICY, EVIDENCE_FLOOR, new_uuid7

_HASH = "sha256:" + "a" * 64


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_blob_bucket, test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=RuntimeEnvironment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        blob_bucket=test_blob_bucket(),
    )


@pytest.fixture
def client(api_settings: Settings):
    from app.main import create_app

    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


class Seat:
    """One principal and the headers that act as it."""

    def __init__(self, workspace_id: UUID) -> None:
        self.id = new_uuid7()
        self.headers = {DEV_PRINCIPAL_HEADER: str(self.id), "Workspace-Id": str(workspace_id)}


@pytest_asyncio.fixture
async def seat(workspace_id, grant):
    """`seat("deployer", "approver")` is a new principal holding those roles."""

    async def make(*roles: str) -> Seat:
        made = Seat(workspace_id)
        for role in roles:
            await grant(role, principal_id=made.id)
        return made

    return make


async def approved_version(
    database: Database, workspace_id: UUID, author: UUID, *, compiled: bool = True
) -> str:
    """An `approved` Rating Version, compiled or not, and its reference string."""
    slug = f"rv-{uuid4().hex[:8]}"
    async with database.unit_of_work() as session:
        await add_approved(
            session,
            RatingVersionRow(
                workspace_id=workspace_id,
                slug=slug,
                version=1,
                status="approved",
                dataset_version_id=uuid4(),
                model_ref="model:motor-ad-frequency@7",
                created_by=author,
                bundle={"content_hash": _HASH} if compiled else None,
            ),
        )
    return f"rating_version:{slug}@1"


def deploy(client: TestClient, seat: Seat, env: str, ref: str, **extra: Any):
    return client.post(
        f"/api/v1/environments/{env}/deployments",
        json={"rating_version_ref": ref, "reason": "release", **extra},
        headers=seat.headers,
    )


def request_into(client: TestClient, seat: Seat, env: str, ref: str, **extra: Any):
    return client.post(
        f"/api/v1/environments/{env}/deployment-requests",
        json={"rating_version_ref": ref, "change_summary": "annual review", **extra},
        headers=seat.headers,
    )


def decide(client: TestClient, seat: Seat, approval_request_id: str, decision: str = "approve"):
    return client.post(
        f"/api/v1/approval-requests/{approval_request_id}/decide",
        json={"decision": decision, "comment": "ok"},
        headers=seat.headers,
    )


def promoted_to_uat(client: TestClient, seat: Seat, ref: str) -> None:
    """The predecessor item: a successful Deployment of `ref` in `dev`, then in `uat`."""
    assert deploy(client, seat, "dev", ref).status_code == 201
    assert deploy(client, seat, "uat", ref).status_code == 201


async def _request_for_prod(
    client: TestClient, database: Database, workspace_id: UUID, seat, *, author: UUID | None = None
):
    """A Deployment Request into `prod` for a fresh version, submitted by a new Deployer.

    Returns `(submitter, ref, request_body)`; the request is in `review`.
    """
    submitter = await seat("deployer")
    ref = await approved_version(database, workspace_id, author or new_uuid7())
    promoted_to_uat(client, submitter, ref)
    created = request_into(client, submitter, "prod", ref)
    assert created.status_code == 201, created.text
    return submitter, ref, created.json()


def _approval_id(client: TestClient, submitter: Seat, request_ref: str) -> str:
    listed = client.get(
        "/api/v1/approval-requests?artifact_type=deployment", headers=submitter.headers
    )
    return next(r["id"] for r in listed.json()["items"] if r["artifact_ref"] == request_ref)


# --- RL-1401 item 1: the Author of a Deployment Request ----------------------------------


@pytest.mark.req("FR-353", "FR-267")
@pytest.mark.asyncio
async def test_a_deployer_who_is_neither_submitter_nor_author_approves_a_deployment_request(
    client: TestClient, database, workspace_id, seat
) -> None:
    """(a) The positive control. Predicted red with `"deployment"` absent from
    `CREATION_ACTIONS`: `_author_of` finds no creation event and `decide` refuses 403
    `APPROVAL_AUTHOR_UNRESOLVED`. Green once the key is present and the route records
    `deployment_request.created`."""
    submitter, _, request = await _request_for_prod(client, database, workspace_id, seat)
    decider = await seat("approver", "deployer")
    decided = decide(client, decider, _approval_id(client, submitter, request["ref"]))
    assert decided.status_code == 200, decided.text
    assert decided.json()["status"] == "approved"
    async with database.session() as session:
        status = (
            await session.execute(
                select(DeploymentRequestRow.status).where(
                    DeploymentRequestRow.workspace_id == workspace_id
                )
            )
        ).scalar_one()
    assert status == "approved"


@pytest.mark.req("FR-353")
@pytest.mark.asyncio
async def test_the_submitter_cannot_decide_their_own_deployment_request(
    client: TestClient, database, workspace_id, seat, grant
) -> None:
    """(b) R1 comes first: a Deployer who also holds the approver role and submitted the request
    is refused 403 `SUBMITTER_CANNOT_APPROVE`, not the author refusal."""
    submitter = await seat("deployer", "approver")
    ref = await approved_version(database, workspace_id, new_uuid7())
    promoted_to_uat(client, submitter, ref)
    request = request_into(client, submitter, "prod", ref).json()
    refused = decide(client, submitter, _approval_id(client, submitter, request["ref"]))
    assert refused.status_code == 403
    assert refused.json()["code"] == "SUBMITTER_CANNOT_APPROVE"


@pytest.mark.req("FR-353")
@pytest.mark.asyncio
async def test_a_deployment_request_with_no_creation_event_is_refused_fail_closed(
    client: TestClient, database, workspace_id, seat
) -> None:
    """(c) With the key present but the `deployment_request.created` event deleted by a fixture,
    the decision is refused 403 `APPROVAL_AUTHOR_UNRESOLVED`: an author that cannot be
    established is never allowed (`06` FR-353). `audit_events` refuses `DELETE`, so the fixture
    lifts the guard for its own transaction only."""
    submitter, _, request = await _request_for_prod(client, database, workspace_id, seat)
    async with database.unit_of_work() as session:
        from sqlalchemy import text

        await session.execute(text("ALTER TABLE audit_events DISABLE TRIGGER USER"))
        await session.execute(
            delete(AuditEventRow).where(
                AuditEventRow.workspace_id == workspace_id,
                AuditEventRow.entity_ref == request["ref"],
                AuditEventRow.action == "deployment_request.created",
            )
        )
        await session.execute(text("ALTER TABLE audit_events ENABLE TRIGGER USER"))
    decider = await seat("approver", "deployer")
    refused = decide(client, decider, _approval_id(client, submitter, request["ref"]))
    assert refused.status_code == 403
    assert refused.json()["code"] == "APPROVAL_AUTHOR_UNRESOLVED"


def test_every_approvable_type_has_an_author_resolution() -> None:
    """(d) The parity test: every `artifact_type` of `DEFAULT_POLICY` and every key of
    `EVIDENCE_FLOOR` is a key of `CREATION_ACTIONS`. Predicted red naming `deployment` until
    the entry is added; red again on any future type added without one (`RL-1401`
    Acceptance 2)."""
    from app.platform.approvals import CREATION_ACTIONS

    types = {p.artifact_type for p in DEFAULT_POLICY.policies} | set(EVIDENCE_FLOOR)
    assert sorted(types - set(CREATION_ACTIONS)) == []


@pytest.mark.req("FR-353")
@pytest.mark.asyncio
async def test_the_author_of_the_deployed_rating_version_is_not_barred_by_the_author_check(
    client: TestClient, database, workspace_id, seat
) -> None:
    """(e) Limb (ii), pinned as ruled by `RL-1401` item 1 and its mint-pass note (A1, A2): the
    Author of the Rating Version, holding the Deployer role, may decide the deployment request.
    The Author of a Deployment Request is its submitter; the Rating Version's own Author is a
    component author, carried to WK-677 beside the rate-table and model-version Authors.
    A later change that bars them must amend FR-353 and that carry, and so changes this test
    deliberately."""
    decider = await seat("approver", "deployer")
    submitter = await seat("deployer")
    ref = await approved_version(database, workspace_id, decider.id)
    promoted_to_uat(client, submitter, ref)
    request = request_into(client, submitter, "prod", ref).json()
    decided = decide(client, decider, _approval_id(client, submitter, request["ref"]))
    assert decided.status_code == 200, decided.text


@pytest.mark.asyncio
async def test_the_creation_event_is_recorded_with_the_request_reference_and_the_submitter(
    client: TestClient, database, workspace_id, seat
) -> None:
    """`RL-1401` T1/T2: `entity_ref` is exactly `deployment:<env>@<n>`, the actor the submitter,
    `before` null, `after` the request with its pins and its pinned evidence."""
    submitter, ref, request = await _request_for_prod(client, database, workspace_id, seat)
    assert request["ref"] == "deployment:prod@1"
    async with database.session() as session:
        event = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "deployment_request.created",
                )
            )
        ).scalar_one()
        approval = (
            await session.execute(
                select(ApprovalRequestRow.artifact_ref).where(
                    ApprovalRequestRow.workspace_id == workspace_id,
                    ApprovalRequestRow.artifact_type == "deployment",
                )
            )
        ).scalar_one()
    assert event.entity_ref == approval == "deployment:prod@1"
    assert event.actor["id"] == str(submitter.id)
    assert not event.before
    assert event.after["rating_version_ref"] == ref
    assert set(event.after["evidence"]) == {"rating_version_approval", "uat_deployment"}


# --- Acceptance 4: the refusals, each by its cause -----------------------------------------


async def _version(database: Database, workspace_id: UUID, status: str) -> str:
    slug = f"rv-{uuid4().hex[:8]}"
    async with database.unit_of_work() as session:
        session.add(
            RatingVersionRow(
                workspace_id=workspace_id,
                slug=slug,
                version=1,
                status=status,
                dataset_version_id=uuid4(),
                model_ref="model:motor-ad-frequency@7",
                created_by=new_uuid7(),
                bundle={"content_hash": _HASH},
            )
        )
    return f"rating_version:{slug}@1"


@pytest.mark.req("FR-267", "FR-238")
@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["draft", "review"])
async def test_only_an_approved_rating_version_deploys(
    client: TestClient, database, workspace_id, seat, status: str
) -> None:
    deployer = await seat("deployer")
    ref = await _version(database, workspace_id, status)
    refused = deploy(client, deployer, "dev", ref)
    assert refused.status_code == 409
    assert refused.json()["code"] == "VALIDATION_FAILED"
    assert status in refused.json()["detail"]
    requested = request_into(client, deployer, "prod", ref)
    assert requested.status_code == 409
    assert status in requested.json()["detail"]


@pytest.mark.req("FR-267")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "artifact_type",
    sorted(__import__("model_schema").ARTIFACT_TYPES - {"rating_version"}),
)
async def test_g3_a_reference_that_is_not_a_rating_version_is_refused_before_any_row_is_read(
    client: TestClient, workspace_id, seat, monkeypatch, artifact_type: str
) -> None:
    """G3. The Rating Version loader is replaced with one that fails the test if it is reached,
    so a 422 proves the type check ran **before** any row was read; with the check deleted the
    `sub_graph` case reaches the loader and answers 500."""
    from app.platform import deployments

    async def _must_not_be_reached(*_a: Any, **_k: Any) -> None:
        raise AssertionError("a row was read before the type check")

    monkeypatch.setattr(deployments, "_approved_compiled_version", _must_not_be_reached)
    deployer = await seat("deployer")
    ref = f"{artifact_type}:some-thing@1"
    for refused in (
        deploy(client, deployer, "dev", ref),
        request_into(client, deployer, "prod", ref),
    ):
        assert refused.status_code == 422, refused.text
        assert refused.json()["code"] == "VALIDATION_FAILED"
        assert artifact_type in refused.json()["detail"]


@pytest.mark.req("FR-267", "FR-347")
@pytest.mark.asyncio
async def test_a_caller_without_deployment_promote_is_refused(
    client: TestClient, database, workspace_id, seat
) -> None:
    ref = await approved_version(database, workspace_id, new_uuid7())
    analyst = await seat("analyst")
    refused = deploy(client, analyst, "dev", ref)
    assert refused.status_code == 403
    assert refused.json()["code"] == "PERMISSION_DENIED"
    assert request_into(client, analyst, "prod", ref).status_code == 403


@pytest.mark.req("FR-347")
@pytest.mark.asyncio
async def test_a_service_account_is_refused_on_the_deploy_routes(
    client: TestClient, database, workspace_id, seat
) -> None:
    admin = await seat("admin")
    created = client.post(
        "/api/v1/service-accounts",
        json={
            "slug": f"sa-{uuid4().hex[:8]}",
            "environments": ["dev"],
            "permissions": ["score:execute"],
        },
        headers=admin.headers,
    )
    assert created.status_code == 201, created.text
    key = {"X-API-Key": created.json()["key"], "Workspace-Id": str(workspace_id)}
    ref = await approved_version(database, workspace_id, new_uuid7())
    body = {"rating_version_ref": ref, "reason": "x"}
    refused = client.post("/api/v1/environments/dev/deployments", json=body, headers=key)
    assert refused.status_code == 403
    assert refused.json()["code"] == "PERMISSION_DENIED"


async def _scoped_deployer(database: Database, workspace_id: UUID, env_slug: str, seat) -> Seat:
    """A member whose `deployer` assignment is scoped to one Environment (`RL-1301` B.5)."""
    from app.db.models import EnvironmentRow, RoleAssignmentRow, RoleRow, WorkspaceMemberRow
    from model_schema import ScopeType

    made = await seat("analyst")  # a member with the roles table seeded
    async with database.unit_of_work() as session:
        env = (
            await session.execute(select(EnvironmentRow).where(EnvironmentRow.slug == env_slug))
        ).scalar_one()
        role = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == "deployer"
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=made.id,
                role_id=role.id,
                scope_type=ScopeType.ENVIRONMENT.value,
                scope_id=env.id,
            )
        )
        assert (
            await session.execute(
                select(WorkspaceMemberRow).where(WorkspaceMemberRow.user_id == made.id)
            )
        ).scalar_one_or_none()
    return made


@pytest.mark.req("FR-267", "FR-345")
@pytest.mark.asyncio
async def test_a_deployer_scoped_to_uat_deploys_in_uat_and_is_refused_on_prod(
    client: TestClient, database, workspace_id, seat, monkeypatch
) -> None:
    """`RL-1301` B.5: the Environment is the permission's resource. With the handler's
    `resource=` argument removed the scoped Deployer is refused **in `uat` as well**, which is
    what the second half of this test shows by wrapping `require_permission` to drop it."""
    workspace = await seat("deployer")
    scoped = await _scoped_deployer(database, workspace_id, "uat", seat)
    ref = await approved_version(database, workspace_id, new_uuid7())
    assert deploy(client, workspace, "dev", ref).status_code == 201

    assert deploy(client, scoped, "uat", ref).status_code == 201
    refused = request_into(client, scoped, "prod", ref)
    assert refused.status_code == 403
    assert refused.json()["code"] == "SCOPE_DENIED"  # held, but not here (FR-345)
    assert deploy(client, workspace, "uat", ref).status_code == 201  # workspace-wide: both
    assert request_into(client, workspace, "prod", ref).status_code == 201

    from app.platform import deployments, rbac

    real = rbac.require_permission

    async def _without_the_resource(session: Any, **kwargs: Any) -> None:
        kwargs.pop("resource", None)
        await real(session, **kwargs)

    monkeypatch.setattr(deployments.rbac, "require_permission", _without_the_resource)
    ref2 = await approved_version(database, workspace_id, new_uuid7())
    assert deploy(client, workspace, "dev", ref2).status_code == 201
    assert deploy(client, scoped, "uat", ref2).status_code == 403


@pytest.mark.req("FR-267")
@pytest.mark.asyncio
async def test_a_prod_deploy_with_no_approved_request_is_409_deploy_requires_approval(
    client: TestClient, database, workspace_id, seat
) -> None:
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, new_uuid7())
    promoted_to_uat(client, deployer, ref)
    refused = deploy(client, deployer, "prod", ref)
    assert refused.status_code == 409
    assert refused.json()["code"] == "DEPLOY_REQUIRES_APPROVAL"
    # A request still in review is not approved either.
    created = request_into(client, deployer, "prod", ref).json()
    still = deploy(client, deployer, "prod", ref, deployment_request_ref=created["ref"])
    assert still.status_code == 409
    assert still.json()["code"] == "DEPLOY_REQUIRES_APPROVAL"


async def _approve(client, seat, submitter: Seat, request_ref: str) -> None:
    decider = await seat("approver", "deployer")
    assert decide(client, decider, _approval_id(client, submitter, request_ref)).status_code == 200


@pytest.mark.req("FR-267", "FR-272", "NFR-498")
@pytest.mark.asyncio
async def test_a_deployer_deploys_dev_then_uat_then_prod_with_its_approval(
    client: TestClient, database, workspace_id, seat
) -> None:
    """The positive control, and FR-272: each Deployment has exactly one `deployment.created`
    event, whose `before` is the previous live Deployment of the Environment or null and whose
    `after` is the Deployment, written in the same transaction as the row."""
    submitter, ref, request = await _request_for_prod(client, database, workspace_id, seat)
    await _approve(client, seat, submitter, request["ref"])
    done = deploy(client, submitter, "prod", ref, deployment_request_ref=request["ref"])
    assert done.status_code == 201, done.text
    body = done.json()
    assert body["environment"] == "prod"
    assert body["bundle_hash"] == _HASH
    assert body["deployment_request_ref"] == request["ref"]
    assert body["deployed_by"] == str(submitter.id)

    async with database.session() as session:
        events = (
            (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == "deployment.created",
                    )
                )
            )
            .scalars()
            .all()
        )
        request_status = (
            await session.execute(
                select(DeploymentRequestRow.status).where(
                    DeploymentRequestRow.workspace_id == workspace_id
                )
            )
        ).scalar_one()
    assert len(events) == 3  # dev, uat, prod: one each
    prod = next(e for e in events if e.entity_ref == "environment:prod")
    assert not prod.before
    assert prod.after["id"] == body["id"]
    uat = next(e for e in events if e.entity_ref == "environment:uat")
    assert uat.after["environment"] == "uat"
    assert request_status == "executed"

    history = client.get("/api/v1/environments/prod/deployments", headers=submitter.headers)
    assert history.status_code == 200
    assert [d["id"] for d in history.json()["items"]] == [body["id"]]


@pytest.mark.req("FR-272", "NFR-498")
@pytest.mark.asyncio
async def test_a_deployment_commits_with_its_audit_event_or_not_at_all(
    client: TestClient, database, workspace_id, seat, monkeypatch
) -> None:
    """Red on broken input: with `audit.record` a no-op the Deployment would commit with no
    event. Here `audit.record` raises for `deployment.created`, and **no Deployment row** is
    left behind: the row and its event share one transaction."""
    from app.db.models import DeploymentRow
    from app.platform import audit, deployments

    real = audit.record

    async def _failing(session: Any, **kwargs: Any) -> Any:
        if kwargs["action"] == "deployment.created":
            raise RuntimeError("audit is down")
        return await real(session, **kwargs)

    monkeypatch.setattr(deployments.audit, "record", _failing)
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, new_uuid7())
    assert deploy(client, deployer, "dev", ref).status_code == 500
    async with database.session() as session:
        rows = (
            (
                await session.execute(
                    select(DeploymentRow).where(DeploymentRow.workspace_id == workspace_id)
                )
            )
            .scalars()
            .all()
        )
    assert rows == []


@pytest.mark.req("FR-429")
@pytest.mark.asyncio
async def test_an_ungated_target_enforces_the_promotion_order_at_the_route(
    client: TestClient, database, workspace_id, seat
) -> None:
    """`uat` has no `deployment` entry, so no request and no skip: a version never deployed to
    `dev` is refused 409 `PROMOTION_ORDER_VIOLATION`."""
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, new_uuid7())
    refused = deploy(client, deployer, "uat", ref)
    assert refused.status_code == 409
    assert refused.json()["code"] == "PROMOTION_ORDER_VIOLATION"
    assert "'dev'" in refused.json()["detail"]


def _set_prod_skippable(client: TestClient, admin: Seat, skippable: list[str]) -> None:
    policy = client.get("/api/v1/approval-policy", headers=admin.headers).json()
    for entry in policy["policies"]:
        if entry["artifact_type"] == "deployment" and entry["environment"] == "prod":
            entry["skippable_predecessors"] = skippable
    assert (
        client.put("/api/v1/approval-policy", json=policy, headers=admin.headers).status_code == 200
    )


@pytest.mark.req("FR-429")
@pytest.mark.asyncio
async def test_the_skip_flips_the_request_and_the_deploy_refusals_together(
    client: TestClient, database, workspace_id, seat
) -> None:
    """One predicate, two call sites. `prod` with no `uat` deployment and no permitted skip is
    refused at the request with 422 `EVIDENCE_INCOMPLETE`; permit the skip and the request is
    accepted, approved, and deployed (the positive control for a reasoned skip). Withdraw the
    permission after approval and the **route** refuses with 409 `PROMOTION_ORDER_VIOLATION`
    from the request's **pinned** skip."""
    admin = await seat("admin")
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, new_uuid7())
    skip = {"skipped_environment": "uat", "reason": "hotfix, uat environment is down"}

    refused = request_into(client, deployer, "prod", ref, skip=skip)
    assert refused.status_code == 422
    assert refused.json()["code"] == "EVIDENCE_INCOMPLETE"
    assert request_into(client, deployer, "prod", ref).json()["code"] == "EVIDENCE_INCOMPLETE"

    _set_prod_skippable(client, admin, ["uat"])
    blank = request_into(client, deployer, "prod", ref, skip={**skip, "reason": "   "})
    assert blank.status_code == 422  # a blank reason is refused by the shape
    created = request_into(client, deployer, "prod", ref, skip=skip)
    assert created.status_code == 201, created.text
    assert created.json()["evidence"]["uat_deployment"] == skip
    await _approve(client, seat, deployer, created.json()["ref"])

    _set_prod_skippable(client, admin, [])
    refused_again = deploy(
        client, deployer, "prod", ref, deployment_request_ref=created.json()["ref"]
    )
    assert refused_again.status_code == 409
    assert refused_again.json()["code"] == "PROMOTION_ORDER_VIOLATION"

    _set_prod_skippable(client, admin, ["uat"])
    done = deploy(client, deployer, "prod", ref, deployment_request_ref=created.json()["ref"])
    assert done.status_code == 201, done.text


@pytest.mark.req("FR-267")
@pytest.mark.asyncio
async def test_a_request_is_executed_exactly_once(
    client: TestClient, database, workspace_id, seat
) -> None:
    """auditor-plans F5: a second deploy naming an executed request is 409
    `DEPLOY_REQUIRES_APPROVAL` and writes no second Deployment."""
    submitter, ref, request = await _request_for_prod(client, database, workspace_id, seat)
    await _approve(client, seat, submitter, request["ref"])
    assert (
        deploy(client, submitter, "prod", ref, deployment_request_ref=request["ref"]).status_code
        == 201
    )
    again = deploy(client, submitter, "prod", ref, deployment_request_ref=request["ref"])
    assert again.status_code == 409
    assert again.json()["code"] == "DEPLOY_REQUIRES_APPROVAL"
    history = client.get("/api/v1/environments/prod/deployments", headers=submitter.headers).json()
    assert len(history["items"]) == 1


@pytest.mark.req("FR-267")
@pytest.mark.asyncio
async def test_two_concurrent_deploys_of_one_request_write_exactly_one_deployment(
    client: TestClient, database, workspace_id, seat
) -> None:
    """auditor-plans F5, concurrently. Both deploys pass the `approved` check on their own
    snapshot; the conditional `UPDATE ... WHERE status = 'approved'` lets one win. Red on broken
    input: with that `WHERE` removed both would write a Deployment."""
    from concurrent.futures import ThreadPoolExecutor

    submitter, ref, request = await _request_for_prod(client, database, workspace_id, seat)
    await _approve(client, seat, submitter, request["ref"])

    def go() -> Any:
        return deploy(client, submitter, "prod", ref, deployment_request_ref=request["ref"])

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: go(), range(2)))
    assert sorted(r.status_code for r in results) == [201, 409]
    assert (
        next(r for r in results if r.status_code == 409).json()["code"]
        == "DEPLOY_REQUIRES_APPROVAL"
    )
    history = client.get("/api/v1/environments/prod/deployments", headers=submitter.headers).json()
    assert len(history["items"]) == 1


@pytest.mark.req("FR-267")
@pytest.mark.asyncio
async def test_a_stale_approved_snapshot_cannot_execute_a_request_twice(
    client: TestClient, database, workspace_id, seat, monkeypatch
) -> None:
    """auditor-plans F5, deterministically: the second deploy is handed the request row as it
    was **before** the first executed it (a stale `approved` snapshot, as a racing transaction
    would hold). The conditional `UPDATE ... WHERE status = 'approved'` returns no row, so it
    is refused 409 and writes nothing. Red on broken input: with that `WHERE` removed the
    stale deploy writes a second Deployment (the concurrent test above cannot show this: the
    row lock serialises the two, so the second reads `executed` and is refused earlier)."""
    from app.platform import deployments

    submitter, ref, request = await _request_for_prod(client, database, workspace_id, seat)
    await _approve(client, seat, submitter, request["ref"])
    real = deployments._executable_request
    snapshots: list[Any] = []

    async def _remembering(*args: Any, **kwargs: Any) -> Any:
        row = await real(*args, **kwargs)
        snapshots.append(row)
        return row

    monkeypatch.setattr(deployments, "_executable_request", _remembering)
    assert (
        deploy(client, submitter, "prod", ref, deployment_request_ref=request["ref"]).status_code
        == 201
    )

    async def _stale(*_a: Any, **_k: Any) -> Any:
        return snapshots[0]

    monkeypatch.setattr(deployments, "_executable_request", _stale)
    again = deploy(client, submitter, "prod", ref, deployment_request_ref=request["ref"])
    assert again.status_code == 409
    assert again.json()["code"] == "DEPLOY_REQUIRES_APPROVAL"
    history = client.get("/api/v1/environments/prod/deployments", headers=submitter.headers).json()
    assert len(history["items"]) == 1


@pytest.mark.req("FR-267")
@pytest.mark.asyncio
async def test_a_request_for_another_version_or_environment_does_not_authorise_a_deploy(
    client: TestClient, database, workspace_id, seat
) -> None:
    submitter, ref, request = await _request_for_prod(client, database, workspace_id, seat)
    await _approve(client, seat, submitter, request["ref"])
    other = await approved_version(database, workspace_id, new_uuid7())
    promoted_to_uat(client, submitter, other)
    refused = deploy(client, submitter, "prod", other, deployment_request_ref=request["ref"])
    assert refused.status_code == 409
    assert refused.json()["code"] == "DEPLOY_REQUIRES_APPROVAL"
    uat_history = "/api/v1/environments/uat/deployments"
    before = client.get(uat_history, headers=submitter.headers).json()["items"]
    ungated = deploy(client, submitter, "uat", ref, deployment_request_ref=request["ref"])
    # `uat` takes no request at all: RL-1404 D3 refuses the reference rather than ignoring it.
    assert ungated.status_code == 422
    assert ungated.json()["code"] == "VALIDATION_FAILED"
    assert client.get(uat_history, headers=submitter.headers).json()["items"] == before
    async with database.session() as session:
        assert (
            await session.execute(
                select(DeploymentRequestRow.status).where(
                    DeploymentRequestRow.workspace_id == workspace_id,
                    DeploymentRequestRow.slug == "prod",
                    DeploymentRequestRow.version == 1,
                )
            )
        ).scalar_one() == "approved"


@pytest.mark.req("FR-267")
@pytest.mark.asyncio
async def test_an_environment_with_no_deployment_policy_entry_takes_no_request(
    client: TestClient, database, workspace_id, seat
) -> None:
    """RL-886: with the policy's `deployment` entries removed, `prod` is ungated and the request
    is refused 422 "No approval policy for this artifact type", **before** any evidence is read
    (a version with no predecessor deployment would otherwise be `EVIDENCE_INCOMPLETE`)."""
    admin = await seat("admin")
    deployer = await seat("deployer")
    policy = client.get("/api/v1/approval-policy", headers=admin.headers).json()
    policy["policies"] = [p for p in policy["policies"] if p["artifact_type"] != "deployment"]
    assert (
        client.put("/api/v1/approval-policy", json=policy, headers=admin.headers).status_code == 200
    )
    ref = await approved_version(database, workspace_id, new_uuid7())
    refused = request_into(client, deployer, "uat", ref)
    assert refused.status_code == 422
    assert refused.json()["code"] == "VALIDATION_FAILED"
    assert "No approval policy for this artifact type" in refused.json()["title"]


# --- RL-1404 D2, D4, D5: the Task 5 flags, decided ------------------------------------------


async def _gated_environment(client: TestClient, seat, *, requires_prior: str | None) -> str:
    """A fresh Environment (the seeded ones are deployment-wide and stay untouched) and a
    `deployment` entry for it in the workspace policy, copied from `prod`'s."""
    admin = await seat("admin")
    slug = f"env-{uuid4().hex[:8]}"
    created = client.post(
        "/api/v1/environments",
        json={
            "slug": slug,
            "name": slug,
            "description": "gated for a test",
            "promotion_order": 5,
            "requires_prior_environment": requires_prior,
        },
        headers=admin.headers,
    )
    assert created.status_code == 201, created.text
    _set_policy_entry(client, admin, slug, present=True)
    return slug


def _set_policy_entry(client: TestClient, admin: Seat, slug: str, *, present: bool) -> None:
    policy = client.get("/api/v1/approval-policy", headers=admin.headers).json()
    policy["policies"] = [
        p
        for p in policy["policies"]
        if not (p["artifact_type"] == "deployment" and p["environment"] == slug)
    ]
    if present:
        prod = next(
            p
            for p in policy["policies"]
            if p["artifact_type"] == "deployment" and p["environment"] == "prod"
        )
        policy["policies"].append({**prod, "environment": slug, "skippable_predecessors": []})
    assert (
        client.put("/api/v1/approval-policy", json=policy, headers=admin.headers).status_code == 200
    )


@pytest.mark.req("FR-429", "FR-364")
@pytest.mark.asyncio
async def test_a_gated_environment_with_no_predecessor_refuses_every_request_naming_the_remedy(
    client: TestClient, database, workspace_id, seat
) -> None:
    """RL-1404 D2: a gated Environment with `requires_prior_environment` `null` has no
    predecessor item to pin, so every request into it is 422 `EVIDENCE_INCOMPLETE`, and the
    detail names the Environment and the remedy (removing its `deployment` policy entry), since
    `requires_prior_environment` cannot be changed after creation. No row is written."""
    slug = await _gated_environment(client, seat, requires_prior=None)
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, new_uuid7())
    refused = request_into(client, deployer, slug, ref)
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "EVIDENCE_INCOMPLETE"
    detail = refused.json()["detail"]
    assert slug in detail
    assert f"Remove the `deployment` policy entry for {slug!r}" in detail
    assert "requires_prior_environment" in detail
    async with database.session() as session:
        assert (
            await session.execute(
                select(DeploymentRequestRow).where(
                    DeploymentRequestRow.workspace_id == workspace_id
                )
            )
        ).first() is None


@pytest.mark.req("FR-355", "FR-267")
@pytest.mark.asyncio
async def test_a_request_for_changes_ends_a_deployment_request_rejected(
    client: TestClient, database, workspace_id, seat
) -> None:
    """RL-1404 D4: a request for changes has no pre-submission state to return a Deployment
    Request to, so it ends `rejected` (read from its row, not from an approval response), with
    a `deployment_request.rejected` Audit Event. A deploy naming it is 409
    `DEPLOY_REQUIRES_APPROVAL`; a new request for the same version into the same Environment is
    accepted as the next `@n`."""
    submitter, ref, request = await _request_for_prod(client, database, workspace_id, seat)
    decider = await seat("approver", "deployer")
    decided = client.post(
        f"/api/v1/approval-requests/{_approval_id(client, submitter, request['ref'])}/decide",
        json={"decision": "request_changes", "comment": "pin a newer uat deployment"},
        headers=decider.headers,
    )
    assert decided.status_code == 200, decided.text
    async with database.session() as session:
        status = (
            await session.execute(
                select(DeploymentRequestRow.status).where(
                    DeploymentRequestRow.workspace_id == workspace_id,
                    DeploymentRequestRow.slug == "prod",
                    DeploymentRequestRow.version == 1,
                )
            )
        ).scalar_one()
        event = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "deployment_request.rejected",
                )
            )
        ).scalar_one_or_none()
    assert status == "rejected"
    assert event is not None
    refused = deploy(client, submitter, "prod", ref, deployment_request_ref=request["ref"])
    assert refused.status_code == 409
    assert refused.json()["code"] == "DEPLOY_REQUIRES_APPROVAL"
    again = request_into(client, submitter, "prod", ref)
    assert again.status_code == 201, again.text
    assert again.json()["ref"].endswith("@2")


@pytest.mark.req("FR-428", "FR-267")
@pytest.mark.asyncio
async def test_a_request_approved_before_its_target_was_retired_is_refused_at_execution(
    client: TestClient, database, workspace_id, seat
) -> None:
    """`RL-1401` T3's last sentence, as tested through the routes (RL-1404 D5): the request is
    approved while the policy entry exists; the entry is then removed and the Environment
    retired (nothing now names it); then a deploy naming the approved request (i) and a deploy
    naming none (ii) are each 409 `VALIDATION_FAILED` naming the retirement. No Deployment row
    is written and the request stays `approved`."""
    from app.db.models import DeploymentRow

    admin = await seat("admin")
    submitter = await seat("deployer")
    slug = await _gated_environment(client, seat, requires_prior="uat")
    ref = await approved_version(database, workspace_id, new_uuid7())
    promoted_to_uat(client, submitter, ref)
    created = request_into(client, submitter, slug, ref)
    assert created.status_code == 201, created.text
    request_ref = created.json()["ref"]
    await _approve(client, seat, submitter, request_ref)
    _set_policy_entry(client, admin, slug, present=False)
    retired = client.post(f"/api/v1/environments/{slug}/retire", headers=admin.headers)
    assert retired.status_code == 200, retired.text

    named = deploy(client, submitter, slug, ref, deployment_request_ref=request_ref)
    none = deploy(client, submitter, slug, ref)
    for refused in (named, none):
        assert refused.status_code == 409, refused.text
        assert refused.json()["code"] == "VALIDATION_FAILED"
        assert slug in refused.json()["detail"]
        assert "retired" in refused.json()["detail"]
    async with database.session() as session:
        assert (
            await session.execute(
                select(DeploymentRow).where(
                    DeploymentRow.workspace_id == workspace_id,
                    DeploymentRow.environment_id
                    == select(EnvironmentRow.id)
                    .where(EnvironmentRow.slug == slug)
                    .scalar_subquery(),
                )
            )
        ).first() is None
        assert (
            await session.execute(
                select(DeploymentRequestRow.status).where(
                    DeploymentRequestRow.workspace_id == workspace_id,
                    DeploymentRequestRow.slug == slug,
                )
            )
        ).scalar_one() == "approved"


# --- RL-1301 A.4: the evidence floor, and the generic route -----------------------------------


@pytest.mark.req("FR-267", "FR-364")
@pytest.mark.asyncio
async def test_a_decision_on_a_request_stripped_of_a_floor_item_is_refused(
    client: TestClient, database, workspace_id, seat
) -> None:
    """With the floor check removed from `apply_approval_decision` the stripped row would be
    approved. A fixture removes `uat_deployment` from the pinned evidence (the evidence is
    immutable through the module's functions, so this goes round them, as an attacker with
    SQL would); the decision is refused 422 and the request stays in review."""
    from sqlalchemy import text

    submitter, _, request = await _request_for_prod(client, database, workspace_id, seat)
    async with database.unit_of_work() as session:
        await session.execute(
            text(
                "UPDATE deployment_requests SET evidence = evidence - 'uat_deployment' "
                "WHERE workspace_id = :w"
            ),
            {"w": workspace_id},
        )
    decider = await seat("approver", "deployer")
    refused = decide(client, decider, _approval_id(client, submitter, request["ref"]))
    assert refused.status_code == 422
    assert refused.json()["code"] == "EVIDENCE_INCOMPLETE"
    async with database.session() as session:
        status = (
            await session.execute(
                select(DeploymentRequestRow.status).where(
                    DeploymentRequestRow.workspace_id == workspace_id
                )
            )
        ).scalar_one()
    assert status == "review"


@pytest.mark.req("FR-386", "FR-267")
@pytest.mark.asyncio
async def test_the_generic_route_cannot_create_an_approvable_deployment_request(
    client: TestClient, database, workspace_id, seat
) -> None:
    """RL-1301 audit advisory A2, auditor-plans F3: `POST /approval-requests` naming
    `deployment:…` is refused when no row exists, when the row is not in `review`, and when a
    fixture has stripped a floor item. A row in `review` already holds its open request, so
    naming it again is 409."""
    from sqlalchemy import text

    submitter, ref, request = await _request_for_prod(client, database, workspace_id, seat)

    def generic(artifact_ref: str):
        return client.post(
            "/api/v1/approval-requests",
            json={
                "artifact_ref": artifact_ref,
                "change_summary": "via the generic route",
                "environment": "prod",
            },
            headers=submitter.headers,
        )

    assert generic("deployment:prod@99").status_code == 404  # no such row
    assert generic(request["ref"]).status_code == 409  # already holds its open request

    # A row not in `review`: withdrawn by the module's own path.
    approval = _approval_id(client, submitter, request["ref"])
    withdrawn = client.post(
        f"/api/v1/approval-requests/{approval}/withdraw",
        json={"reason": "no longer needed"},
        headers=(await seat("approver")).headers,
    )
    assert withdrawn.status_code == 200, withdrawn.text
    refused = generic(request["ref"])
    assert refused.status_code in (409, 422)
    assert refused.json()["code"] != "ARTIFACT_TYPE_NOT_RESOLVABLE"

    # Stripped of a floor item: a second, fresh request, then a fixture removes one item.
    request2 = request_into(client, submitter, "prod", ref).json()
    async with database.unit_of_work() as session:
        await session.execute(
            text(
                "UPDATE deployment_requests SET evidence = evidence - 'rating_version_approval' "
                "WHERE workspace_id = :w AND version = 2"
            ),
            {"w": workspace_id},
        )
    stripped = generic(request2["ref"])
    assert stripped.status_code == 422
    assert stripped.json()["code"] == "EVIDENCE_INCOMPLETE"


@pytest.mark.req("FR-351")
@pytest.mark.asyncio
async def test_a_decision_on_a_request_not_in_review_is_refused_by_the_module(
    client: TestClient, database, workspace_id, seat
) -> None:
    """auditor-plans F4: `apply_approval_decision` calls `require_in_review` on the locked row,
    not only the route. Called directly with a decided approval request over a row already
    `executed`, it refuses."""
    from app.platform import deployments
    from model_schema import ActorKind, Principal

    submitter, ref, request = await _request_for_prod(client, database, workspace_id, seat)
    await _approve(client, seat, submitter, request["ref"])
    assert (
        deploy(client, submitter, "prod", ref, deployment_request_ref=request["ref"]).status_code
        == 201
    )
    async with database.unit_of_work() as session:
        approval = (
            await session.execute(
                select(ApprovalRequestRow).where(
                    ApprovalRequestRow.workspace_id == workspace_id,
                    ApprovalRequestRow.artifact_ref == request["ref"],
                )
            )
        ).scalar_one()
        from app.errors import PlatformError

        with pytest.raises(PlatformError) as refused:
            await deployments.apply_approval_decision(
                session,
                workspace_id=workspace_id,
                actor=Principal(kind=ActorKind.USER, id=new_uuid7(), display="x"),
                request=approval,
            )
        assert refused.value.status_code == 409


# --- RL-1401 items 2 and 3: the uncompiled version and the retired Environment ---------------


@pytest.mark.req("FR-239", "FR-267")
@pytest.mark.asyncio
async def test_an_approved_version_that_was_never_compiled_is_refused_at_both_routes(
    client: TestClient, database, workspace_id, seat
) -> None:
    """`RL-1401` item 2. The fixture is an `approved` version with no `bundle` metadata: what a
    no-suite submission leaves, since only `compile` writes it and a version cannot compile
    once it has left `draft` (`RL-1379`). Predicted red before the check: the deploy reaches
    the `bundle_hash` column's format constraint (a 500), and the request is accepted (201).
    After it, both routes refuse 409 `BUNDLE_COMPILE_FAILED`, naming the version, and no
    Deployment row or audit event is written."""
    from app.db.models import DeploymentRow

    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, new_uuid7(), compiled=False)
    refused = deploy(client, deployer, "dev", ref)
    assert refused.status_code == 409, refused.text
    assert refused.json()["code"] == "BUNDLE_COMPILE_FAILED"
    assert ref in refused.json()["detail"]
    requested = request_into(client, deployer, "prod", ref)
    assert requested.status_code == 409, requested.text
    assert requested.json()["code"] == "BUNDLE_COMPILE_FAILED"
    async with database.session() as session:
        assert (
            await session.execute(
                select(DeploymentRow).where(DeploymentRow.workspace_id == workspace_id)
            )
        ).first() is None
        assert (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action.in_(("deployment.created", "deployment_request.created")),
                )
            )
        ).first() is None


@pytest.mark.req("FR-239")
@pytest.mark.asyncio
async def test_a_bundle_with_no_content_hash_is_refused_the_same_way(
    client: TestClient, database, workspace_id, seat
) -> None:
    """Metadata present but without `content_hash` is as uncompiled as none at all."""
    deployer = await seat("deployer")
    slug = f"rv-{uuid4().hex[:8]}"
    async with database.unit_of_work() as session:
        await add_approved(
            session,
            RatingVersionRow(
                workspace_id=workspace_id,
                slug=slug,
                version=1,
                status="approved",
                dataset_version_id=uuid4(),
                model_ref="model:motor-ad-frequency@7",
                created_by=new_uuid7(),
                bundle={"blob": "elsewhere"},
            ),
        )
    refused = deploy(client, deployer, "dev", f"rating_version:{slug}@1")
    assert refused.status_code == 409
    assert refused.json()["code"] == "BUNDLE_COMPILE_FAILED"


async def _retired_environment(client: TestClient, seat) -> str:
    """A fresh Environment, retired. `uat` itself is not retired here: the Environments are
    deployment-wide and the suite re-seeds them only at session end, so retiring a seed would
    break every later test that deploys to it (`test_environments.py` starts every test from a
    fresh slug for the same reason). `RL-1401` item 3 names `uat` for its having no live
    Deployment and no policy entry; a fresh Environment has neither."""
    admin = await seat("admin")
    slug = f"env-{uuid4().hex[:8]}"
    created = client.post(
        "/api/v1/environments",
        json={
            "slug": slug,
            "name": slug,
            "description": "retired for a test",
            "promotion_order": 4,
            "requires_prior_environment": "prod",
        },
        headers=admin.headers,
    )
    assert created.status_code == 201, created.text
    assert (
        client.post(f"/api/v1/environments/{slug}/retire", headers=admin.headers).status_code == 200
    )
    return slug


@pytest.mark.req("FR-428", "FR-267")
@pytest.mark.asyncio
async def test_a_retired_environment_is_refused_at_both_routes_and_writes_nothing(
    client: TestClient, database, workspace_id, seat
) -> None:
    """`RL-1401` item 3, after the permission check and before the Rating Version is read: the
    version here does not exist, so a refusal that names the Environment proves the order.
    Predicted red before the check: 404 (the version is read first). After it, both routes
    refuse 409 `VALIDATION_FAILED` naming the slug and the retirement, and no Deployment row,
    no Deployment Request row and no audit event is written."""
    from app.db.models import DeploymentRow

    slug = await _retired_environment(client, seat)
    deployer = await seat("deployer")
    ghost = "rating_version:no-such-version@1"
    for refused in (
        deploy(client, deployer, slug, ghost),
        request_into(client, deployer, slug, ghost),
    ):
        assert refused.status_code == 409, refused.text
        assert refused.json()["code"] == "VALIDATION_FAILED"
        assert slug in refused.json()["detail"]
        assert "retired" in refused.json()["detail"]
    async with database.session() as session:
        for table in (DeploymentRow, DeploymentRequestRow):
            assert (
                await session.execute(select(table).where(table.workspace_id == workspace_id))
            ).first() is None
        assert (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action.in_(("deployment.created", "deployment_request.created")),
                )
            )
        ).first() is None


@pytest.mark.req("FR-428")
@pytest.mark.asyncio
async def test_the_permission_check_comes_before_the_retired_refusal_and_an_unknown_slug_is_404(
    client: TestClient, database, workspace_id, seat
) -> None:
    """`RL-1401` T3: the refusal is after the permission check, so an analyst is told 403 and
    not that the Environment is retired; an unknown slug is 404 `NOT_FOUND`."""
    slug = await _retired_environment(client, seat)
    analyst = await seat("analyst")
    ghost = "rating_version:no-such-version@1"
    assert deploy(client, analyst, slug, ghost).status_code == 403
    assert request_into(client, analyst, slug, ghost).status_code == 403
    deployer = await seat("deployer")
    for missing in (
        deploy(client, deployer, "no-such-env", ghost),
        request_into(client, deployer, "no-such-env", ghost),
    ):
        assert missing.status_code == 404
        assert missing.json()["code"] == "NOT_FOUND"
