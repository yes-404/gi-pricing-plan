"""Submission of a Custom Objective: `OBJECTIVE_NOT_CERTIFIED` and the extra Approver
(`02` FR-152, FR-163; `RL-1362` DP-S3-3 and DP-S3-4; WK-690 S3 Task 7; FD-1510).

Two rules, both read from the objective's certificate at submission:

* a `draft` objective, of either kind, is refused 409 `OBJECTIVE_NOT_CERTIFIED`; every other
  invalid transition to `review` keeps 409 `VALIDATION_FAILED`;
* when the latest certificate's `convexity` check is `violated`, the request's
  `approvers_required` is the policy entry's count plus one, for both kinds, stored on the
  request row and in the submission's audit `after`.

Each `violated` objective is certified through the real Job: the quantile template (the live
instance FD-1510 found) and `02` §4.6's example expression (which certifies `violated` too).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_custom_objectives import COUNT_GRID, _certified, _objective
from backend.tests.test_custom_objectives_expression import _derived
from backend.tests.test_model_jobs import _actuary
from backend.tests.test_model_lifecycle import _principal_with
from sqlalchemy import select

from app.db.models import (
    ApprovalPolicyRow,
    ApprovalRequestRow,
    AuditEventRow,
    CustomObjectiveRow,
    ObjectiveCertificateRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as approval_service
from app.platform import jobs as job_service
from app.platform import objectives as service
from app.platform.objectives import default_sampling
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import (
    DEFAULT_POLICY,
    ApprovalPolicy,
    ApprovalRequest,
    ApprovalStatus,
    ArtifactRef,
    CheckStatus,
    DecisionKind,
    JobKind,
    JobStatus,
    ObjectiveStatus,
    ObjectiveTemplate,
    Principal,
    new_uuid7,
)

register_model_handlers()


@pytest.fixture
async def author(database: Database, workspace_id: Any) -> dict[str, str]:
    """`model:fit` and `custom_objective:author`: what create and derive need."""
    from backend.tests.test_custom_objectives import _principal_holding

    return await _principal_holding(
        database, workspace_id, {"custom_objective:author", "model:fit", "model:read"}
    )


async def _set_count(database: Database, workspace_id: Any, count: int) -> None:
    """`DEFAULT_POLICY` with the `custom_objective` entry's `approvers_required` set."""
    document = DEFAULT_POLICY.model_dump(mode="json")
    for entry in document["policies"]:
        if entry["artifact_type"] == "custom_objective":
            entry["approvers_required"] = count
    async with database.unit_of_work() as session:
        session.add(ApprovalPolicyRow(workspace_id=workspace_id, policy=document))


async def _violated(
    kind: str,
    database: Database,
    blob_store: Any,
    workspace_id: Any,
    api_client: Any,
    author: Any,
) -> UUID:
    """A `certified` objective of `kind` whose latest certificate's convexity is `violated`."""
    if kind == "template":
        actor = await _actuary(database, workspace_id)
        row = await _certified(
            database,
            blob_store,
            workspace_id,
            actor,
            template=ObjectiveTemplate.QUANTILE,
            params={"alpha": 0.9},
        )
        return row.id
    derived = await _derived(api_client, author, database, workspace_id)
    actor = await _actuary(database, workspace_id)
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.OBJECTIVE_CERTIFY,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "objective_id": derived["id"],
                "sampling": COUNT_GRID.model_dump(mode="json"),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    return UUID(derived["id"])


async def _submit(database: Database, workspace_id: Any, objective_id: UUID) -> tuple[UUID, int]:
    submitter = await _actuary(database, workspace_id)
    async with database.unit_of_work() as session:
        _, request = await service.submit_for_review(
            session,
            workspace_id=workspace_id,
            actor=submitter,
            objective_id=objective_id,
            change_summary="please",
        )
        return request.id, request.approvers_required


async def _approve(database: Database, workspace_id: Any, request_id: UUID, how_many: int) -> str:
    """`how_many` distinct non-author Approvers approve in turn; the objective's status."""
    for _ in range(how_many):
        approver: Principal = await _principal_with(database, workspace_id, "approver")
        async with database.unit_of_work() as session:
            decided = await approval_service.decide(
                session,
                workspace_id=workspace_id,
                approver=approver,
                request_id=request_id,
                decision=DecisionKind.APPROVE,
                comment="checked",
            )
            await service.apply_approval_decision(
                session, workspace_id=workspace_id, actor=approver, request=decided
            )
    async with database.session() as session:
        request = await session.get(ApprovalRequestRow, request_id)
        assert request is not None
        objective = (
            await session.execute(
                select(CustomObjectiveRow).where(
                    CustomObjectiveRow.workspace_id == workspace_id,
                    CustomObjectiveRow.approval_request_id == request_id,
                )
            )
        ).scalar_one()
        return objective.status


async def _submitted_audit_after(
    database: Database, workspace_id: Any, request_id: UUID
) -> dict[str, Any]:
    async with database.session() as session:
        request = await session.get(ApprovalRequestRow, request_id)
        assert request is not None
        event = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "approval_request.submitted",
                    AuditEventRow.entity_ref == request.artifact_ref,
                )
            )
        ).scalar_one()
        assert event.after is not None
        return event.after


# -- OBJECTIVE_NOT_CERTIFIED --------------------------------------------------------------


@pytest.mark.req("FR-163")
@pytest.mark.parametrize("kind", ["template", "expression"])
async def test_submitting_a_draft_is_objective_not_certified_for_both_kinds(
    kind: str, database: Database, workspace_id, api_client, author
) -> None:
    actor = await _actuary(database, workspace_id)
    if kind == "template":
        draft = await _objective(database, workspace_id, actor)
        objective_id = draft.id
    else:
        objective_id = UUID((await _derived(api_client, author, database, workspace_id))["id"])
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.submit_for_review(
                session,
                workspace_id=workspace_id,
                actor=actor,
                objective_id=objective_id,
                change_summary="please",
            )
    assert refused.value.status_code == 409
    assert refused.value.code == "OBJECTIVE_NOT_CERTIFIED"


@pytest.mark.req("FR-163")
async def test_submitting_an_approved_objective_is_still_validation_failed(
    database: Database, blob_store, workspace_id
) -> None:
    """The control: the new code is raised for `draft` only, not for every invalid transition."""
    actor = await _actuary(database, workspace_id)
    row = await _certified(database, blob_store, workspace_id, actor)
    request_id, _ = await _submit(database, workspace_id, row.id)
    assert await _approve(database, workspace_id, request_id, 1) == "approved"
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.submit_for_review(
                session,
                workspace_id=workspace_id,
                actor=actor,
                objective_id=row.id,
                change_summary="again",
            )
    assert refused.value.status_code == 409
    assert refused.value.code == "VALIDATION_FAILED"


@pytest.mark.req("FR-146")
@pytest.mark.req("FR-163")
async def test_submitting_with_a_certificate_id_that_names_no_row_is_validation_failed(
    database: Database, blob_store, workspace_id
) -> None:
    """Delta 7 (g): the pointer is the evidence, so a pointer to nothing is no evidence.

    There is no foreign key, so a `certified` row can carry a `certificate_id` with no
    certificate behind it. Before the guard that read as "no `violated` finding" and the
    objective went to `review` with the policy's plain count.
    """
    from uuid import uuid4

    from sqlalchemy import update

    actor = await _actuary(database, workspace_id)
    row = await _certified(database, blob_store, workspace_id, actor)
    dangling = uuid4()
    async with database.unit_of_work() as session:
        await session.execute(
            update(CustomObjectiveRow)
            .where(CustomObjectiveRow.id == row.id)
            .values(certificate_id=dangling)
        )
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.submit_for_review(
                session,
                workspace_id=workspace_id,
                actor=actor,
                objective_id=row.id,
                change_summary="please",
            )
    assert refused.value.status_code == 409
    assert refused.value.code == "VALIDATION_FAILED"
    assert str(dangling) in (refused.value.detail or "")


async def _latest_certificate_id(database: Database, objective_id: UUID) -> UUID:
    async with database.session() as session:
        return (await session.get(CustomObjectiveRow, objective_id)).certificate_id  # type: ignore[union-attr,return-value]


async def _submit_pointing_at(
    database: Database, workspace_id, actor: Principal, row: CustomObjectiveRow, pointer: UUID
) -> PlatformError:
    from sqlalchemy import update

    async with database.unit_of_work() as session:
        await session.execute(
            update(CustomObjectiveRow)
            .where(CustomObjectiveRow.id == row.id)
            .values(certificate_id=pointer)
        )
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.submit_for_review(
                session,
                workspace_id=workspace_id,
                actor=actor,
                objective_id=row.id,
                change_summary="please",
            )
    return refused.value


@pytest.mark.req("FR-146")
@pytest.mark.req("FR-163")
async def test_submitting_with_another_objectives_certificate_is_validation_failed(
    database: Database, blob_store, workspace_id
) -> None:
    """A certificate that exists in this workspace but certifies a different objective is no
    evidence for this one (`RL-1362` S5's fail-open class, audit A7)."""
    actor = await _actuary(database, workspace_id)
    row = await _certified(database, blob_store, workspace_id, actor)
    other = await _certified(database, blob_store, workspace_id, actor)
    foreign = await _latest_certificate_id(database, other.id)
    refused = await _submit_pointing_at(database, workspace_id, actor, row, foreign)
    assert refused.status_code == 409
    assert refused.code == "VALIDATION_FAILED"
    assert str(foreign) in (refused.detail or "")


@pytest.mark.req("FR-146")
@pytest.mark.req("FR-163")
async def test_submitting_with_a_certificate_stored_in_another_workspace_is_validation_failed(
    database: Database, blob_store, workspace_id
) -> None:
    """A certificate stored in another workspace is refused as if absent (tenancy)."""
    actor = await _actuary(database, workspace_id)
    row = await _certified(database, blob_store, workspace_id, actor)
    # Same objective id and version, so only the workspace clause can refuse it.
    async with database.unit_of_work() as session:
        genuine = await session.get(ObjectiveCertificateRow, row.certificate_id)
        assert genuine is not None
        foreign_row = ObjectiveCertificateRow(
            workspace_id=new_uuid7(),
            custom_objective_id=row.id,
            objective_version=genuine.objective_version,
            payload=genuine.payload,
        )
        session.add(foreign_row)
        await session.flush()
        foreign = foreign_row.id
    refused = await _submit_pointing_at(database, workspace_id, actor, row, foreign)
    assert refused.status_code == 409
    assert refused.code == "VALIDATION_FAILED"
    assert str(foreign) in (refused.detail or "")


# -- the extra Approver -------------------------------------------------------------------


@pytest.mark.req("FR-152")
@pytest.mark.req("FR-163")
@pytest.mark.parametrize("kind", ["template", "expression"])
async def test_a_violated_objective_needs_two_approvers_at_policy_one(
    kind: str, database: Database, blob_store, workspace_id, api_client, author
) -> None:
    objective_id = await _violated(kind, database, blob_store, workspace_id, api_client, author)
    request_id, required = await _submit(database, workspace_id, objective_id)
    assert required == 2
    assert (await _submitted_audit_after(database, workspace_id, request_id))[
        "approvers_required"
    ] == 2
    assert await _approve(database, workspace_id, request_id, 1) == ObjectiveStatus.REVIEW.value
    assert await _approve(database, workspace_id, request_id, 1) == ObjectiveStatus.APPROVED.value


@pytest.mark.req("FR-152")
@pytest.mark.parametrize("kind", ["template", "expression"])
async def test_a_violated_objective_needs_three_approvers_at_policy_two(
    kind: str, database: Database, blob_store, workspace_id, api_client, author
) -> None:
    await _set_count(database, workspace_id, 2)
    objective_id = await _violated(kind, database, blob_store, workspace_id, api_client, author)
    request_id, required = await _submit(database, workspace_id, objective_id)
    assert required == 3
    assert await _approve(database, workspace_id, request_id, 2) == ObjectiveStatus.REVIEW.value
    assert await _approve(database, workspace_id, request_id, 1) == ObjectiveStatus.APPROVED.value


# FD-1510: six of the twelve templates certify `convexity: violated`.
_VIOLATED_TEMPLATES: dict[ObjectiveTemplate, dict[str, float]] = {
    ObjectiveTemplate.ASYMMETRIC_SQUARED: {},
    ObjectiveTemplate.HUBER: {"delta": 1000},
    ObjectiveTemplate.PSEUDO_HUBER: {"delta": 1},
    ObjectiveTemplate.QUANTILE: {"alpha": 0.9},
    ObjectiveTemplate.ZERO_INFLATED_POISSON: {"pi": 0.3},
    ObjectiveTemplate.FOCAL_BINOMIAL: {},
}


@pytest.mark.req("FR-152")
@pytest.mark.parametrize("template", list(_VIOLATED_TEMPLATES), ids=lambda t: t.value)
async def test_each_template_certified_violated_needs_the_extra_approver(
    template: ObjectiveTemplate, database: Database, blob_store, workspace_id
) -> None:
    """FD-1510: each of the six, certified through the real Job on its own
    `default_sampling` grid, reaches `convexity: violated`, and one approval leaves it in
    `review` (two Approvers under the default policy)."""
    actor = await _actuary(database, workspace_id)
    draft = await _objective(
        database, workspace_id, actor, template=template, params=_VIOLATED_TEMPLATES[template]
    )
    grid = default_sampling(service.to_objective(draft))
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.OBJECTIVE_CERTIFY,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "objective_id": str(draft.id),
                "sampling": grid.model_dump(mode="json"),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        certificate = (
            await session.execute(
                select(ObjectiveCertificateRow).where(
                    ObjectiveCertificateRow.custom_objective_id == draft.id
                )
            )
        ).scalar_one()
    convexity = next(
        check
        for check in service.to_certificate(certificate).result.checks
        if check.name == "convexity"
    )
    assert convexity.status is CheckStatus.VIOLATED
    request_id, required = await _submit(database, workspace_id, draft.id)
    assert required == 2
    assert await _approve(database, workspace_id, request_id, 1) == ObjectiveStatus.REVIEW.value


@pytest.mark.req("FR-152")
async def test_the_default_policy_instance_stores_two(
    database: Database, blob_store, workspace_id, api_client, author
) -> None:
    """`06` §4.2's default `custom_objective` entry is one Approver; `1 + 1 = 2`, the outcome
    the struck `escalation` key printed. No policy row is written: this is `DEFAULT_POLICY`."""
    objective_id = await _violated(
        "template", database, blob_store, workspace_id, api_client, author
    )
    _, required = await _submit(database, workspace_id, objective_id)
    assert required == 2


@pytest.mark.req("FR-152")
async def test_policy_five_stores_six_and_the_request_validates(
    database: Database, blob_store, workspace_id, api_client, author
) -> None:
    """The policy's `le=5` does not clip the request: `ApprovalRequest.approvers_required` is
    `ge=1` with no upper bound."""
    await _set_count(database, workspace_id, 5)
    objective_id = await _violated(
        "template", database, blob_store, workspace_id, api_client, author
    )
    request_id, required = await _submit(database, workspace_id, objective_id)
    assert required == 6
    async with database.session() as session:
        row = await session.get(ApprovalRequestRow, request_id)
        assert row is not None
        assert (
            ApprovalRequest(
                id=row.id,
                workspace_id=workspace_id,
                artifact_ref=ArtifactRef.parse(row.artifact_ref),
                artifact_type=row.artifact_type,
                submitted_by=row.submitted_by,
                submitted_at=row.submitted_at,
                change_summary=row.change_summary,
                status=ApprovalStatus(row.status),
                approvers_required=row.approvers_required,
                approvers_recorded=0,
            ).approvers_required
            == 6
        )


@pytest.mark.req("FR-152")
async def test_a_passing_certificate_needs_one_approver_at_policy_one(
    database: Database, blob_store, workspace_id
) -> None:
    """The control: a `pass` convexity adds nobody."""
    actor = await _actuary(database, workspace_id)
    row = await _certified(database, blob_store, workspace_id, actor)  # poisson: convex
    request_id, required = await _submit(database, workspace_id, row.id)
    assert required == 1
    assert (await _submitted_audit_after(database, workspace_id, request_id))[
        "approvers_required"
    ] == 1
    assert await _approve(database, workspace_id, request_id, 1) == ObjectiveStatus.APPROVED.value


@pytest.mark.req("FR-152")
async def test_another_artifact_type_is_unchanged_by_the_new_keyword(
    database: Database, workspace_id
) -> None:
    """`approvals.submit`'s increment defaults to 0: a `validation_rule` stores the entry count."""
    submitter = await _actuary(database, workspace_id)
    async with database.unit_of_work() as session:
        request = await approval_service.submit(
            session,
            workspace_id=workspace_id,
            submitter=submitter,
            artifact_ref=ArtifactRef(type="validation_rule", slug="rule-a", version=1),
            change_summary="x",
        )
        assert request.approvers_required == 1


@pytest.mark.req("FR-152")
def test_a_policy_entry_with_an_escalation_key_is_refused() -> None:
    """No workspace can configure the rule: the entry is `extra="forbid"`."""
    document = DEFAULT_POLICY.model_dump(mode="json")
    for entry in document["policies"]:
        if entry["artifact_type"] == "custom_objective":
            entry["escalation"] = {"when": "x", "approvers_required": 2}
    with pytest.raises(ValueError, match="escalation"):
        ApprovalPolicy.model_validate(document)


@pytest.mark.req("FR-152")
def test_the_section_4_2_policies_array_validates_as_policy_entries() -> None:
    """`FD-1281`'s method on `06` §4.2: the `policies` array parsed out of the spec's JSON
    block and validated as `ApprovalPolicyEntry` values. The struck `escalation` key made it
    refuse on `policies.1.escalation`; the whole document still refuses on `expedited` and
    `separation_of_duties` (`FD-1281`'s other limbs), which this test does not assert."""
    import json
    import re
    from pathlib import Path

    from model_schema import ApprovalPolicyEntry

    text = (Path(__file__).parents[2] / "docs/specs/06-governance.md").read_text()
    section = text[text.index("### 4.2 `ApprovalPolicy`") :]
    block = re.search(r"```json\n(.*?)\n```", section, re.DOTALL)
    assert block is not None
    for entry in json.loads(block.group(1))["policies"]:
        ApprovalPolicyEntry.model_validate(entry)
