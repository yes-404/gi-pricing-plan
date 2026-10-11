"""A validation rule is approved only through the approval workflow (FD-1356, PL-1408).

Before the fix `POST /validation-rules/{id}/approve` wrote `approved` itself: no approval
request, no decision row, no quorum, no policy role, and a rule whose dry run **errored**
was approvable (`01` §4.5 step 2 says the rule "must execute successfully"). These tests
drive the real surface: rules authored over HTTP, a real ingested Dataset Version, the real
`dataset.validate` dry-run job, and the real decide route.

Where an `error` dry run is needed past the submit refusal, the rule is moved to `review`
and its request filed by a test-only write, because the refusal under test is exactly what
stops the public path from getting there.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from backend.tests.approved_rows import add_approved, mark_approved
from backend.tests.test_api_approvals import _headers, _require_two_approvals
from backend.tests.test_data_jobs import CLEAN, DIRTY, _ingest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.config import Environment, Settings
from app.db.models import (
    ApprovalDecisionRow,
    ApprovalRequestRow,
    AuditEventRow,
    JobRow,
    RoleAssignmentRow,
    RoleRow,
    ValidationReportRow,
    ValidationRuleRow,
    ValidationRuleSetRow,
)
from app.db.session import Database
from app.main import create_app
from app.platform import approvals as approvals_service
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.tasks import execute_job
from model_schema import ArtifactRef, JobKind, JobStatus, Principal, ScopeType, new_uuid7

ERROR_RULES = {
    "missing_column": {
        "check": "range",
        "target": {"table": "policy_exposure", "column": "no_such_column"},
        "params": {"min_inclusive": 0, "key_columns": ["policy_id"]},
    },
    "unknown_check": {
        "check": "no_such_check",
        "target": {"table": "policy_exposure", "column": "exposure_years"},
        "params": {},
    },
    "missing_table": {
        "check": "range",
        "target": {"table": "no_such_table", "column": "exposure_years"},
        "params": {"min_inclusive": 0, "key_columns": ["policy_id"]},
    },
}


@pytest.fixture(autouse=True)
def _handlers() -> None:
    register_data_handlers()


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_blob_bucket, test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        blob_bucket=test_blob_bucket(),
    )


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest_asyncio.fixture
async def author(workspace_id, principal, grant) -> dict[str, str]:
    """The rule's author: an analyst, who also submits and ingests."""
    await grant("analyst")
    return _headers(principal.id, workspace_id)


async def _approver(grant, workspace_id) -> tuple[UUID, dict[str, str]]:
    who = new_uuid7()
    await grant("approver", principal_id=who)
    return who, _headers(who, workspace_id)


def _new_rule(
    client: TestClient, headers, *, severity: str = "warn", **over: Any
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "slug": f"rng-{new_uuid7().hex[-8:]}",
        "layer": "actuarial_sanity",
        "check": "range",
        "severity": severity,
        "target": {"table": "policy_exposure", "column": "exposure_years"},
        "params": {"min_inclusive": 0, "key_columns": ["policy_id"]},
    }
    body.update(over)
    created = client.post("/api/v1/validation-rules", json=body, headers=headers)
    assert created.status_code == 201, created.text
    return created.json()


async def _a_version(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
    payload: bytes = CLEAN,
) -> UUID:
    async with database.unit_of_work() as session:
        dataset = await dataset_service.create_dataset(
            session, workspace_id=workspace_id, actor=principal, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        dataset_id = dataset.id
    return await _ingest(database, blob_store, workspace_id, principal, dataset_id, payload)


async def _dry_run_job(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    headers,
    rule_id: str,
    version_id: UUID,
) -> tuple[UUID, JobStatus]:
    response = client.post(
        f"/api/v1/validation-rules/{rule_id}/dry-run",
        json={"dataset_version_id": str(version_id)},
        headers=headers,
    )
    assert response.status_code == 202, response.text
    job_id = UUID(response.json()["id"])
    return job_id, await execute_job(database, job_id, blob_store)


async def _dry_run(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    headers,
    rule_id: str,
    version_id: UUID,
) -> JobStatus:
    return (await _dry_run_job(client, database, blob_store, headers, rule_id, version_id))[1]


async def _row(database: Database, rule_id: str) -> ValidationRuleRow:
    async with database.session() as session:
        row = await session.get(ValidationRuleRow, UUID(rule_id))
        assert row is not None
        return row


async def _report(database: Database, row: ValidationRuleRow) -> ValidationReportRow:
    async with database.session() as session:
        report = await session.get(ValidationReportRow, row.dry_run_report_id)
        assert report is not None
        return report


async def _requests(database: Database, workspace_id, row: ValidationRuleRow) -> list[Any]:
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(ApprovalRequestRow).where(
                        ApprovalRequestRow.workspace_id == workspace_id,
                        ApprovalRequestRow.artifact_ref
                        == f"validation_rule:{row.slug}@{row.version}",
                    )
                )
            ).scalars()
        )


async def _decisions(database: Database, request_id: UUID) -> int:
    async with database.session() as session:
        return (
            await session.execute(
                select(func.count())
                .select_from(ApprovalDecisionRow)
                .where(ApprovalDecisionRow.request_id == request_id)
            )
        ).scalar_one()


async def _events(
    database: Database, workspace_id, row: ValidationRuleRow, action: str
) -> list[Any]:
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.entity_ref == f"validation_rule:{row.slug}@{row.version}",
                        AuditEventRow.action == action,
                    )
                )
            ).scalars()
        )


async def _file_in_review(
    database: Database, workspace_id, row: ValidationRuleRow, submitter: Principal
) -> ApprovalRequestRow:
    """Test-only: the state the refusal under test normally keeps a rule out of."""
    async with database.unit_of_work() as session:
        stored = await session.get(ValidationRuleRow, row.id)
        assert stored is not None
        stored.status = "review"
        await session.flush()
        return await approvals_service.submit(
            session,
            workspace_id=workspace_id,
            submitter=submitter,
            artifact_ref=ArtifactRef(type="validation_rule", slug=row.slug, version=row.version),
            change_summary="filed by the test",
        )


async def _submitted_rule(
    client, database, blob_store, workspace_id, principal, author, **rule: Any
) -> dict[str, Any]:
    """Author, dry-run on a clean version, submit through the module route."""
    created = _new_rule(client, author, **rule)
    version = await _a_version(database, blob_store, workspace_id, principal)
    assert await _dry_run(client, database, blob_store, author, created["id"], version) is (
        JobStatus.SUCCEEDED
    )
    submitted = client.post(
        f"/api/v1/validation-rules/{created['id']}/submit",
        json={"change_summary": "first cut"},
        headers=author,
    )
    assert submitted.status_code == 200, submitted.text
    return created


def _decide(client, headers, request_id: UUID, decision: str = "approve"):
    return client.post(
        f"/api/v1/approval-requests/{request_id}/decide",
        json={"decision": decision, "comment": "reviewed"},
        headers=headers,
    )


@pytest.mark.req("FR-50")
@pytest.mark.req("FR-363")
@pytest.mark.parametrize("cause", list(ERROR_RULES))
async def test_an_error_dry_run_is_refused_at_submit(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
    cause: str,
) -> None:
    created = _new_rule(client, author, **ERROR_RULES[cause])
    version = await _a_version(database, blob_store, workspace_id, principal)
    await _dry_run(client, database, blob_store, author, created["id"], version)
    row = await _row(database, created["id"])
    assert (await _report(database, row)).error_count >= 1

    submitted = client.post(
        f"/api/v1/validation-rules/{created['id']}/submit",
        json={"change_summary": "first cut"},
        headers=author,
    )
    assert submitted.status_code == 422, submitted.text
    assert submitted.json()["code"] == "EVIDENCE_INCOMPLETE"
    assert (await _row(database, created["id"])).status == "draft"


@pytest.mark.req("FR-50")
@pytest.mark.req("FR-363")
@pytest.mark.parametrize("cause", list(ERROR_RULES))
async def test_an_error_dry_run_is_refused_at_approve(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
    grant,
    cause: str,
) -> None:
    created = _new_rule(client, author, **ERROR_RULES[cause])
    version = await _a_version(database, blob_store, workspace_id, principal)
    await _dry_run(client, database, blob_store, author, created["id"], version)
    row = await _row(database, created["id"])
    request = await _file_in_review(database, workspace_id, row, principal)
    _, approver = await _approver(grant, workspace_id)

    decided = _decide(client, approver, request.id)
    assert decided.status_code == 422, decided.text
    assert decided.json()["code"] == "EVIDENCE_INCOMPLETE"
    assert (await _row(database, created["id"])).status == "review"
    (stored,) = await _requests(database, workspace_id, row)
    assert stored.status == "review"
    assert await _decisions(database, request.id) == 0


@pytest.mark.req("FR-50")
async def test_a_fail_dry_run_is_still_approvable(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
    grant,
) -> None:
    """Control: a `fail` is a rule that ran and caught rows. Only `error` is refused."""
    created = _new_rule(client, author, severity="fail")
    version = await _a_version(database, blob_store, workspace_id, principal, DIRTY)
    assert await _dry_run(client, database, blob_store, author, created["id"], version) is (
        JobStatus.SUCCEEDED
    )
    report = await _report(database, await _row(database, created["id"]))
    assert report.overall == "fail"
    assert report.error_count == 0

    submitted = client.post(
        f"/api/v1/validation-rules/{created['id']}/submit",
        json={"change_summary": "first cut"},
        headers=author,
    )
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["status"] == "review"
    row = await _row(database, created["id"])
    (request,) = await _requests(database, workspace_id, row)
    _, approver = await _approver(grant, workspace_id)
    assert _decide(client, approver, request.id).status_code == 200
    assert (await _row(database, created["id"])).status == "approved"


@pytest.mark.req("FR-363")
async def test_the_generic_submit_refuses_an_error_dry_run(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
) -> None:
    created = _new_rule(client, author, **ERROR_RULES["missing_column"])
    version = await _a_version(database, blob_store, workspace_id, principal)
    await _dry_run(client, database, blob_store, author, created["id"], version)
    async with database.unit_of_work() as session:
        stored = await session.get(ValidationRuleRow, UUID(created["id"]))
        assert stored is not None
        stored.status = "review"

    response = client.post(
        "/api/v1/approval-requests",
        json={
            "artifact_ref": f"validation_rule:{created['slug']}@{created['version']}",
            "change_summary": "straight to the generic route",
        },
        headers=author,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "EVIDENCE_INCOMPLETE"


@pytest.mark.req("FR-363")
async def test_a_dry_run_report_that_cannot_be_read_is_refused(
    client: TestClient,
    database: Database,
    workspace_id,
    author,
) -> None:
    created = _new_rule(client, author)
    async with database.unit_of_work() as session:
        stored = await session.get(ValidationRuleRow, UUID(created["id"]))
        assert stored is not None
        stored.dry_run_report_id = new_uuid7()  # no such report row

    submitted = client.post(
        f"/api/v1/validation-rules/{created['id']}/submit",
        json={"change_summary": "first cut"},
        headers=author,
    )
    assert submitted.status_code == 422, submitted.text
    assert submitted.json()["code"] == "EVIDENCE_INCOMPLETE"


@pytest.mark.req("FR-355")
async def test_one_approval_under_a_quorum_of_two_leaves_the_rule_in_review(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
    grant,
) -> None:
    await _require_two_approvals(client, workspace_id, grant, database, "validation_rule")
    created = await _submitted_rule(client, database, blob_store, workspace_id, principal, author)
    _, first_headers = await _approver(grant, workspace_id)
    second, second_headers = await _approver(grant, workspace_id)

    one = client.post(f"/api/v1/validation-rules/{created['id']}/approve", headers=first_headers)
    assert one.status_code == 200, one.text
    row = await _row(database, created["id"])
    assert row.status == "review"
    (request,) = await _requests(database, workspace_id, row)
    assert request.status == "review"
    assert await _decisions(database, request.id) == 1

    two = client.post(f"/api/v1/validation-rules/{created['id']}/approve", headers=second_headers)
    assert two.status_code == 200, two.text
    row = await _row(database, created["id"])
    assert row.status == "approved"
    assert row.approved_by == second


@pytest.mark.req("FR-50")
async def test_the_approve_route_decides_through_the_workflow(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
    grant,
) -> None:
    created = await _submitted_rule(client, database, blob_store, workspace_id, principal, author)
    approver, approver_headers = await _approver(grant, workspace_id)
    approved = client.post(
        f"/api/v1/validation-rules/{created['id']}/approve", headers=approver_headers
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "approved"
    row = await _row(database, created["id"])
    (request,) = await _requests(database, workspace_id, row)
    assert request.status == "approved"
    assert await _decisions(database, request.id) == 1
    (event,) = await _events(database, workspace_id, row, "validation_rule.approved")
    assert event.after["approval_request_id"] == str(request.id)
    assert row.approved_by == approver

    # A rule not in `review` is refused before any request is looked for (Acceptance 4).
    draft = _new_rule(client, author)
    for rule_id, status in ((draft["id"], "draft"), (created["id"], "approved")):
        refused = client.post(
            f"/api/v1/validation-rules/{rule_id}/approve", headers=approver_headers
        )
        assert refused.status_code == 409, refused.text
        assert refused.json()["code"] == "RULE_NOT_APPROVED"
        assert (
            refused.json()["title"]
            == f"Only a rule in review can be approved; this one is {status!r}"
        )
        assert (await _row(database, rule_id)).status == status

    # A rule in `review` that has no open request has no path through this route.
    orphan = _new_rule(client, author)
    async with database.unit_of_work() as session:
        stored = await session.get(ValidationRuleRow, UUID(orphan["id"]))
        assert stored is not None
        stored.status = "review"
    refused = client.post(
        f"/api/v1/validation-rules/{orphan['id']}/approve", headers=approver_headers
    )
    assert refused.status_code == 409, refused.text
    assert refused.json()["code"] == "RULE_NOT_APPROVED"
    assert "/api/v1/approval-requests" in refused.json()["detail"]
    assert (await _row(database, orphan["id"])).status == "review"


@pytest.mark.req("FR-353")
async def test_an_approver_without_a_policy_role_is_refused(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
    grant,
) -> None:
    """Holds `approval:decide`, but is neither `approver` nor `admin` (the policy's roles)."""
    created = await _submitted_rule(client, database, blob_store, workspace_id, principal, author)
    custom = new_uuid7()
    await grant("analyst", principal_id=custom)  # seeds the workspace and the membership
    async with database.unit_of_work() as session:
        role = RoleRow(workspace_id=workspace_id, slug="decider", permissions=["approval:decide"])
        session.add(role)
        await session.flush()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=custom,
                role_id=role.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )

    refused = client.post(
        f"/api/v1/validation-rules/{created['id']}/approve",
        headers=_headers(custom, workspace_id),
    )
    assert refused.status_code == 403, refused.text
    assert refused.json()["code"] == "PERMISSION_DENIED"
    assert (await _row(database, created["id"])).status == "review"


@pytest.mark.req("FR-352")
async def test_the_module_submit_creates_the_request(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
) -> None:
    created = _new_rule(client, author)
    version = await _a_version(database, blob_store, workspace_id, principal)
    await _dry_run(client, database, blob_store, author, created["id"], version)
    url = f"/api/v1/validation-rules/{created['id']}/submit"

    for bad in ({"change_summary": ""}, None):
        refused = (
            client.post(url, headers=author)
            if bad is None
            else client.post(url, json=bad, headers=author)
        )
        assert refused.status_code == 422, refused.text
        assert (await _row(database, created["id"])).status == "draft"

    submitted = client.post(url, json={"change_summary": "first cut"}, headers=author)
    assert submitted.status_code == 200, submitted.text
    row = await _row(database, created["id"])
    (request,) = await _requests(database, workspace_id, row)
    assert request.status == "review"
    assert request.change_summary == "first cut"
    assert request.approvers_required == 1
    (event,) = await _events(database, workspace_id, row, "validation_rule.submitted")
    assert event.after["approval_request_id"] == str(request.id)


@pytest.mark.req("FR-355")
async def test_the_carry_records_the_request_it_carried(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
    grant,
) -> None:
    created = await _submitted_rule(client, database, blob_store, workspace_id, principal, author)
    row = await _row(database, created["id"])
    (request,) = await _requests(database, workspace_id, row)
    _, approver = await _approver(grant, workspace_id)
    assert _decide(client, approver, request.id).status_code == 200
    (event,) = await _events(database, workspace_id, row, "validation_rule.approved")
    assert event.after["approval_request_id"] == str(request.id)


@pytest.mark.req("FR-50")
async def test_an_approved_rules_dry_run_cannot_be_replaced(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
    grant,
) -> None:
    """FD-1415: a dry run re-run on an `approved` rule would rewrite the evidence it was
    approved on. The refusal rolls the stored report back with the job."""
    version = await _a_version(database, blob_store, workspace_id, principal)
    created = _new_rule(client, author)
    assert await _dry_run(client, database, blob_store, author, created["id"], version) is (
        JobStatus.SUCCEEDED
    )
    # Test-only write: the workflow's end state, without the workflow (the plan's
    # `mark_approved` route), so this test does not depend on the code under repair.
    async with database.unit_of_work() as session:
        stored = await session.get(ValidationRuleRow, UUID(created["id"]))
        assert stored is not None
        stored.approved_by = new_uuid7()
        await mark_approved(session, stored)
    first_report = (await _row(database, created["id"])).dry_run_report_id

    version = await _a_version(database, blob_store, workspace_id, principal)
    async with database.session() as session:
        before = (
            await session.execute(select(func.count()).select_from(ValidationReportRow))
        ).scalar_one()
    job_id, status = await _dry_run_job(
        client, database, blob_store, author, created["id"], version
    )
    assert status is not JobStatus.SUCCEEDED
    async with database.session() as session:
        failed = await session.get(JobRow, job_id)
    assert failed is not None
    assert failed.error is not None
    assert failed.error["code"] == "RULE_VERSION_IMMUTABLE"
    assert (await _row(database, created["id"])).dry_run_report_id == first_report
    async with database.session() as session:
        after = (
            await session.execute(select(func.count()).select_from(ValidationReportRow))
        ).scalar_one()
    assert after == before

    # Control: a rule still in `review` takes the new report.
    other = await _submitted_rule(client, database, blob_store, workspace_id, principal, author)
    old = (await _row(database, other["id"])).dry_run_report_id
    assert (await _row(database, other["id"])).status == "review"
    assert await _dry_run(client, database, blob_store, author, other["id"], version) is (
        JobStatus.SUCCEEDED
    )
    assert (await _row(database, other["id"])).dry_run_report_id != old


async def _dataset_with_set(
    database: Database, workspace_id, principal: Principal, rule_ids: list[UUID]
) -> tuple[str, UUID]:
    slug = f"ds-{new_uuid7().hex[-8:]}"
    async with database.unit_of_work() as session:
        dataset = await dataset_service.create_dataset(
            session, workspace_id=workspace_id, actor=principal, slug=slug
        )
        dataset_id = dataset.id
        await add_approved(
            session,
            ValidationRuleSetRow(
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                slug=str(dataset_id),
                version=1,
                body={"rules": [{"rule_id": str(r), "enabled": True} for r in rule_ids]},
                status="approved",
            ),
        )
    return slug, dataset_id


@pytest.mark.req("FR-51")
async def test_a_rule_set_run_refuses_a_member_with_no_rule(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
) -> None:
    ghost = new_uuid7()
    slug, dataset_id = await _dataset_with_set(database, workspace_id, principal, [ghost])
    version = await _ingest(database, blob_store, workspace_id, principal, dataset_id, CLEAN)

    read = client.get(f"/api/v1/datasets/{slug}/rule-set", headers=author)
    assert read.status_code == 404, read.text
    assert str(ghost) in read.json()["detail"]

    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.DATASET_VALIDATE,
            {
                "workspace_id": str(workspace_id),
                "actor": principal.model_dump(mode="json"),
                "dataset_version_id": str(version),
            },
            principal,
            workspace_id=workspace_id,
        )
    status = await execute_job(database, job.id, blob_store)
    assert status is not JobStatus.SUCCEEDED
    async with database.session() as session:
        stored_job = await session.get(JobRow, job.id)
        assert stored_job is not None
    assert stored_job.error is not None
    assert stored_job.error["code"] == "NOT_FOUND"
    # RL-1407 (#1070 @24ea2130), the maintainer's condition 1: this exact text, which
    # names the way back.
    assert stored_job.error["message"] == (
        f"Unknown rule id(s): {ghost}. A rule set runs only rules that exist (`01` FR-50). "
        f"The way back: replace the rule set without them (PUT /api/v1/datasets/{slug}/rule-set)."
    )
    async with database.session() as session:
        reports = (
            await session.execute(
                select(func.count())
                .select_from(ValidationReportRow)
                .where(ValidationReportRow.dataset_version_id == version)
            )
        ).scalar_one()
    assert reports == 0


@pytest.mark.req("FR-51")
async def test_the_read_shows_a_member_in_review(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
) -> None:
    """Control: the read reports a member's status; only the run refuses it."""
    created = await _submitted_rule(client, database, blob_store, workspace_id, principal, author)
    slug, _ = await _dataset_with_set(database, workspace_id, principal, [UUID(created["id"])])
    read = client.get(f"/api/v1/datasets/{slug}/rule-set", headers=author)
    assert read.status_code == 200, read.text
    (entry,) = read.json()["entries"]
    assert entry["rule"]["id"] == created["id"]
    assert entry["rule"]["status"] == "review"


@pytest.mark.req("FR-353")
async def test_the_submitter_and_the_author_cannot_decide(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
    grant,
) -> None:
    await grant("approver")  # the author also holds the approver role
    created = await _submitted_rule(client, database, blob_store, workspace_id, principal, author)
    own = client.post(f"/api/v1/validation-rules/{created['id']}/approve", headers=author)
    assert own.status_code == 403, own.text
    assert own.json()["code"] == "SUBMITTER_CANNOT_APPROVE"

    # Someone else submits the author's rule; the author may still not decide it.
    second = _new_rule(client, author)
    version = await _a_version(database, blob_store, workspace_id, principal)
    await _dry_run(client, database, blob_store, author, second["id"], version)
    row = await _row(database, second["id"])
    other = Principal(kind=principal.kind, id=new_uuid7(), display="b@insurer.example")
    await _file_in_review(database, workspace_id, row, other)
    refused = client.post(f"/api/v1/validation-rules/{second['id']}/approve", headers=author)
    assert refused.status_code == 403, refused.text
    assert refused.json()["code"] == "AUTHOR_CANNOT_APPROVE"


# The key set of `ApprovalRequest` (`model_schema/approvals.py`), which decide's `200` returns
# since FD-1416 (PL-1528); `workspace_id` joined the 12 keys `to_dict` emitted (DP-2 (a)).
DECIDE_RESPONSE_KEYS = {
    "id",
    "workspace_id",
    "artifact_ref",
    "artifact_type",
    "environment",
    "submitted_by",
    "submitted_at",
    "change_summary",
    "status",
    "approvers_required",
    "approvers_recorded",
    "decisions",
    "withdrawn_reason",
}


@pytest.mark.req("FR-351")
@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/approval-requests/{request_id}/decide",
        "/api/v1/validation-rules/{rule_id}/submit",
    ],
)
def test_every_body_this_slice_edits_is_a_model_schema_type(path: str) -> None:
    import model_schema

    document = create_app(
        Settings(environment=Environment.LOCAL, version="0.1.0", log_level="ERROR")
    ).openapi()
    schema = document["paths"][path]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]
    name = schema["$ref"].rsplit("/", 1)[-1]
    assert hasattr(model_schema, name), f"{name} is a route-local body, not a model_schema type"


@pytest.mark.req("FR-351")
async def test_the_decide_response_keeps_its_key_set(
    client: TestClient,
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal,
    author,
    grant,
) -> None:
    created = await _submitted_rule(client, database, blob_store, workspace_id, principal, author)
    _approver_id, approver_headers = await _approver(grant, workspace_id)
    row = await _row(database, created["id"])
    (request,) = await _requests(database, workspace_id, row)
    decided = _decide(client, approver_headers, request.id)
    assert decided.status_code == 200, decided.text
    assert set(decided.json()) == DECIDE_RESPONSE_KEYS
