"""FR-7: every declared transition emits its Audit Event (`00` FR-7; `06` FR-368).

SL 8377 / PL 8376, FD-1723's FR-7 limb. T1 first: the two events whose name says a state that
did not happen, and the certificate that lands under a review (PL 8376 DP-1, DP-3).

A failed certification run is `<type>.certification_failed`, never `<type>.certified`, from
`draft` or from `certified`. A run that ends after submission (any status outside `draft` and
`certified`) keeps its certificate row, moves nothing, does not repoint `certificate_id`, and is
recorded as `<type>.certificate_recorded` with the result, passed or failed, in `after`.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_approvals import (
    RATING,
    _no_evidence_authors,
    _submit,
    _user,
    _with_role,
)
from backend.tests.test_deployments import (  # noqa: F401  (fixtures, by import)
    _approve,
    _request_for_prod,
    api_settings,
    client,
    deploy,
    seat,
)
from backend.tests.test_model_jobs import _actuary
from backend.tests.test_model_lifecycle import _principal_with
from backend.tests.test_rating_versions import _draft, _gate, _principal
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.models import (
    AuditEventRow,
    CustomMetricRow,
    CustomObjectiveRow,
    MetricCertificateRow,
    ObjectiveCertificateRow,
)
from app.db.session import Database
from app.platform import approvals as approval_service
from app.platform import metrics as metric_service
from app.platform import objectives as objective_service
from app.platform import rating_versions as rating_service
from model_schema import (
    Applicability,
    ArtifactRef,
    CertificateCheck,
    CertificateOutcome,
    CertificateResult,
    CheckStatus,
    DecisionKind,
    HessianStrategy,
    MetricDirection,
    ObjectiveTemplate,
    Principal,
    SamplingSpec,
    YDomain,
    new_uuid7,
)

_GRID = SamplingSpec(
    n_points=1_000, y_range=(0.0, 20.0), f_range=(-5.0, 4.0), w_range=(0.01, 10.0), seed=7
)
_APPLICABILITY = Applicability(
    responses=frozenset({"claim_severity"}),
    backends=frozenset({"xgboost"}),
    offset_required=False,
    y_domain=YDomain(min_exclusive=0.0),
)


def _result(outcome: CertificateOutcome) -> CertificateResult:
    failed = outcome is CertificateOutcome.FAILED
    check = CertificateCheck(
        name="hessian_matches_numeric",
        status=CheckStatus.FAILED if failed else CheckStatus.PASS,
        detail="max relative error 4.1e-01" if failed else "matches",
    )
    return CertificateResult(
        overall=outcome, sampling=_GRID, checks=(check,), library_versions={"numpy": "2.0.0"}
    )


PASSED = _result(CertificateOutcome.CERTIFIED)
FAILED = _result(CertificateOutcome.FAILED)


@dataclass(frozen=True)
class Kind:
    """What differs between the two certified artifact types; everything asserted is shared."""

    prefix: str
    row: type
    certificate_row: type
    create: Callable[..., Awaitable[Any]]
    record: Callable[..., Awaitable[Any]]
    submit: Callable[..., Awaitable[Any]]
    apply: Callable[..., Awaitable[Any]]
    key: str  # keyword naming the artifact's id in `record` and `submit`

    def ref(self, row: Any) -> str:
        return f"{self.prefix}:{row.slug}@{row.version}"


async def _create_objective(database: Database, workspace_id: UUID, actor: Principal) -> Any:
    async with database.unit_of_work() as session:
        return await objective_service.create_objective(
            session,
            workspace_id=workspace_id,
            actor=actor,
            slug=f"obj-{new_uuid7().hex[-6:]}",
            template=ObjectiveTemplate.POISSON,
            params={},
            applicability=None,
            hessian_strategy=HessianStrategy.CLIP_TO_MIN,
            hessian_min=1e-6,
            description=None,
        )


async def _create_metric(database: Database, workspace_id: UUID, actor: Principal) -> Any:
    async with database.unit_of_work() as session:
        return await metric_service.create(
            session,
            workspace_id=workspace_id,
            actor=actor,
            slug=f"metric-{new_uuid7().hex[-6:]}",
            template=ObjectiveTemplate.CAPPED_GAMMA,
            params={"cap": 250000},
            applicability=_APPLICABILITY,
            direction=MetricDirection.LOWER_IS_BETTER,
            description=None,
        )


KINDS = {
    "custom_objective": Kind(
        "custom_objective",
        CustomObjectiveRow,
        ObjectiveCertificateRow,
        _create_objective,
        objective_service.record_certificate,
        objective_service.submit_for_review,
        objective_service.apply_approval_decision,
        "objective_id",
    ),
    "custom_metric": Kind(
        "custom_metric",
        CustomMetricRow,
        MetricCertificateRow,
        _create_metric,
        metric_service.record_certificate,
        metric_service.submit,
        metric_service.apply_approval_decision,
        "metric_id",
    ),
}


async def _record(
    kind: Kind,
    database: Database,
    workspace_id: UUID,
    actor: Principal,
    row: Any,
    result: CertificateResult,
) -> Any:
    async with database.unit_of_work() as session:
        moved, _certificate = await kind.record(
            session,
            workspace_id=workspace_id,
            actor=actor,
            result=result,
            **{kind.key: row.id},
        )
    return moved


async def _stored(database: Database, kind: Kind, row_id: UUID) -> Any:
    async with database.session() as session:
        return await session.get(kind.row, row_id)


async def _events(database: Database, workspace_id: UUID, entity_ref: str) -> list[AuditEventRow]:
    async with database.session() as session:
        return list(
            (
                await session.scalars(
                    select(AuditEventRow)
                    .where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.entity_ref == entity_ref,
                    )
                    .order_by(AuditEventRow.sequence)
                )
            ).all()
        )


async def _certificates(database: Database, kind: Kind, row_id: UUID) -> int:
    column = {
        "custom_objective": ObjectiveCertificateRow.custom_objective_id,
        "custom_metric": MetricCertificateRow.custom_metric_id,
    }[kind.prefix]
    async with database.session() as session:
        return len(
            (await session.scalars(select(kind.certificate_row).where(column == row_id))).all()
        )


@pytest.mark.req("FR-7")
@pytest.mark.req("FR-146")
@pytest.mark.req("FR-157")
@pytest.mark.parametrize("before", ["draft", "certified"])
@pytest.mark.parametrize("kind_name", sorted(KINDS))
async def test_a_failed_certificate_says_so(
    database: Database, workspace_id: UUID, kind_name: str, before: str
) -> None:
    """A failed run is `<type>.certification_failed` with the true `before` and `after`
    (PL 8376 DP-1): the audit trail never tells a reader a failed run "certified" it."""
    kind = KINDS[kind_name]
    actor = await _actuary(database, workspace_id)
    row = await kind.create(database, workspace_id, actor)
    if before == "certified":
        row = await _record(kind, database, workspace_id, actor, row, PASSED)
        assert row.status == "certified"

    row = await _record(kind, database, workspace_id, actor, row, FAILED)

    events = [e for e in await _events(database, workspace_id, kind.ref(row)) if e.after]
    last = events[-1]
    assert last.action == f"{kind.prefix}.certification_failed"
    assert last.before == {"status": before}
    assert last.after is not None
    assert last.after["status"] == "draft"
    assert last.after["overall"] == "failed"


@pytest.mark.req("FR-7")
@pytest.mark.req("FR-146")
@pytest.mark.req("FR-157")
@pytest.mark.parametrize("result_name", ["passed", "failed"])
@pytest.mark.parametrize("status", ["review", "approved"])
@pytest.mark.parametrize("kind_name", sorted(KINDS))
async def test_a_late_certificate_moves_nothing(
    database: Database,
    workspace_id: UUID,
    kind_name: str,
    status: str,
    result_name: str,
) -> None:
    """A run that ends after submission keeps its certificate row, moves nothing, does not
    repoint `certificate_id`, and is recorded as `<type>.certificate_recorded` (PL 8376 DP-3):
    an approver reviews what was submitted, and a failed run landing under a review is readable."""
    kind = KINDS[kind_name]
    result = PASSED if result_name == "passed" else FAILED
    actor = await _actuary(database, workspace_id)
    row = await kind.create(database, workspace_id, actor)
    row = await _record(kind, database, workspace_id, actor, row, PASSED)
    submitted_certificate = row.certificate_id

    async with database.unit_of_work() as session:
        moved, request = await kind.submit(
            session,
            workspace_id=workspace_id,
            actor=actor,
            change_summary="certified, ready for review",
            **{kind.key: row.id},
        )
        assert moved.status == "review"
        request_id = request.id
    if status == "approved":
        approver = await _principal_with(database, workspace_id, "approver")
        async with database.unit_of_work() as session:
            decided = await approval_service.decide(
                session,
                workspace_id=workspace_id,
                approver=approver,
                request_id=request_id,
                decision=DecisionKind.APPROVE,
                comment="checks out",
            )
            await kind.apply(session, workspace_id=workspace_id, actor=approver, request=decided)
    assert (await _stored(database, kind, row.id)).status == status
    certificates_before = await _certificates(database, kind, row.id)

    late = await _record(kind, database, workspace_id, actor, row, result)

    stored = await _stored(database, kind, row.id)
    assert late.status == stored.status == status
    assert stored.certificate_id == submitted_certificate
    assert await _certificates(database, kind, row.id) == certificates_before + 1
    recorded = [
        e
        for e in await _events(database, workspace_id, kind.ref(row))
        if e.action == f"{kind.prefix}.certificate_recorded"
    ]
    (event,) = recorded
    assert event.before is not None
    assert event.after is not None
    assert event.before["status"] == event.after["status"] == status
    assert event.after["overall"] == result.overall.value


@pytest.mark.req("FR-7")
@pytest.mark.req("FR-368")
async def test_the_first_of_two_approvals_is_a_decision_not_a_state(
    database: Database, workspace_id: UUID
) -> None:
    """`approval_request.approve` names a decision (PL 8376 DP-2): on the first of two the
    request stays in `review`, and the row says how many approvers are recorded."""
    first = _user("a1")
    await _with_role(database, workspace_id, first, "approver")
    request_id = await _submit(database, workspace_id, _user("s"), ref=RATING)
    async with database.unit_of_work() as session:
        await approval_service.decide(
            session,
            evidence_authors=_no_evidence_authors,
            workspace_id=workspace_id,
            request_id=request_id,
            approver=first,
            decision=DecisionKind.APPROVE,
            comment="first",
        )
    async with database.session() as session:
        events = list(
            (
                await session.scalars(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == "approval_request.approve",
                    )
                )
            ).all()
        )
    (event,) = events
    assert event.before == {"status": "review", "approvers_recorded": 0}
    assert event.after == {"status": "review", "approvers_recorded": 1}


async def _events_named(database: Database, workspace_id: UUID, action: str) -> list[AuditEventRow]:
    async with database.session() as session:
        return list(
            (
                await session.scalars(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == action,
                    )
                )
            ).all()
        )


@pytest.mark.req("FR-7")
@pytest.mark.req("FR-238")
async def test_submitting_a_rating_version_emits_its_event(
    database: Database, workspace_id: UUID
) -> None:
    """`draft → review` is built (PL 8376 DP-6) and owes `rating_version.submitted`, on the
    version's own ArtifactRef, found by a query on that `entity_ref`."""
    analyst = await _principal(database, workspace_id, "analyst")
    actuary = await _principal(database, workspace_id, "pricing_actuary")
    rating_id = await _draft(
        database, workspace_id, analyst, ArtifactRef(type="model", slug="fremtpl2-glm", version=1)
    )
    gate = await _gate(database, workspace_id)
    await gate.adopt(rating_id)
    async with database.unit_of_work() as session:
        row, request = await rating_service.submit_for_review(
            session,
            workspace_id=workspace_id,
            actor=actuary,
            rating_version_id=rating_id,
            change_summary="submitted",
            blob_store=gate.blob_store,
            load_compiled=gate.load,
        )
        ref = f"rating_version:{row.slug}@{row.version}"
        request_id = request.id

    submitted = [
        e
        for e in await _events(database, workspace_id, ref)
        if e.action == "rating_version.submitted"
    ]
    (event,) = submitted
    assert event.before == {"status": "draft"}
    assert event.after == {"status": "review", "approval_request_id": str(request_id)}


@pytest.mark.req("FR-7")
@pytest.mark.req("FR-267")
async def test_executing_a_deployment_request_emits_its_event(
    client: TestClient,  # noqa: F811
    database: Database,
    workspace_id: UUID,
    seat: Any,  # noqa: F811
) -> None:
    """`approved → executed` is built (PL 8376 DP-6) and owes `deployment_request.executed`,
    on the request's own reference."""
    submitter, ref, request = await _request_for_prod(client, database, workspace_id, seat)
    await _approve(client, seat, submitter, request["ref"])
    done = deploy(client, submitter, "prod", ref, deployment_request_ref=request["ref"])
    assert done.status_code == 201, done.text

    (event,) = [
        e
        for e in await _events_named(database, workspace_id, "deployment_request.executed")
        if e.entity_ref == request["ref"]
    ]
    assert event.before == {"status": "approved"}
    assert event.after == {"status": "executed"}
