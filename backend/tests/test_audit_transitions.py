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
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from backend.tests.conftest_db import grant_roles_as_owner
from backend.tests.dry_run_reports import stored_dry_run_report
from backend.tests.test_approvals import (
    AUTHOR,
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
    approved_version,
    client,
    deploy,
    seat,
)
from backend.tests.test_diagnostics import _fit
from backend.tests.test_model_jobs import _actuary, _spec
from backend.tests.test_model_lifecycle import _next_version_of, _principal_with
from backend.tests.test_peril_structure_approval import (
    _model_id,
    _reconciled,
    _set_model_status,
)
from backend.tests.test_peril_structures import _book, _burning_cost_peril
from backend.tests.test_rating_versions import _draft, _gate, _principal
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ApprovalRequestRow,
    AuditEventRow,
    CustomMetricRow,
    CustomObjectiveRow,
    DatasetVersionRow,
    DeploymentRequestRow,
    JobRow,
    MetricCertificateRow,
    ModelRow,
    ObjectiveCertificateRow,
    PerilStructureRow,
    ReferenceTableRow,
    ReferenceTableVersionRow,
    ValidationRuleRow,
)
from app.db.session import Database
from app.platform import approvals as approval_service
from app.platform import audit, datasets
from app.platform import deployments as deployment_service
from app.platform import diagnostics as diagnostics_service
from app.platform import jobs as job_service
from app.platform import metrics as metric_service
from app.platform import modelling as model_service
from app.platform import objectives as objective_service
from app.platform import perils as peril_service
from app.platform import rating_versions as rating_service
from app.platform import reference as reference_service
from app.platform import validation as validation_service
from app.platform import validation_rules as rule_service
from app.worker.data_handlers import register_data_handlers
from app.worker.model_handlers import register_model_handlers
from app.worker.rating_handlers import register_rating_handlers
from model_schema import (
    Applicability,
    ArtifactRef,
    CertificateCheck,
    CertificateOutcome,
    CertificateResult,
    CheckStatus,
    DatasetStatus,
    DecisionKind,
    DeploymentCreate,
    DeploymentRequestCreate,
    HessianStrategy,
    JobKind,
    JobSource,
    JobStatus,
    MetricDirection,
    ModelStatus,
    ObjectiveTemplate,
    Principal,
    Reconciliation,
    SamplingSpec,
    Severity,
    ValidationLayer,
    ValidationReport,
    YDomain,
    new_uuid7,
)
from model_schema.approvals import VALID_APPROVAL_TRANSITIONS
from model_schema.datasets import VALID_DATASET_TRANSITIONS
from model_schema.jobs import VALID_TRANSITIONS as VALID_JOB_TRANSITIONS
from model_schema.metrics import VALID_METRIC_TRANSITIONS
from model_schema.modelling import VALID_MODEL_TRANSITIONS
from model_schema.objectives import VALID_OBJECTIVE_TRANSITIONS
from model_schema.perils import VALID_PERIL_STRUCTURE_TRANSITIONS
from model_schema.rating import VALID_RATING_VERSION_TRANSITIONS

register_data_handlers()
register_model_handlers()
register_rating_handlers()

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


async def _new_objective(session: AsyncSession, workspace_id: UUID, actor: Principal) -> Any:
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


async def _new_metric(session: AsyncSession, workspace_id: UUID, actor: Principal) -> Any:
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


async def _create_objective(database: Database, workspace_id: UUID, actor: Principal) -> Any:
    async with database.unit_of_work() as session:
        return await _new_objective(session, workspace_id, actor)


async def _create_metric(database: Database, workspace_id: UUID, actor: Principal) -> Any:
    async with database.unit_of_work() as session:
        return await _new_metric(session, workspace_id, actor)


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


# -- the table: every declared transition, two legs (PL 8376 T3) ------------------------------


@dataclass(frozen=True)
class Env:
    """What a row's set-up and perform steps share."""

    database: Database
    workspace_id: UUID
    actor: Principal
    blob_store: Any = None


@dataclass(frozen=True)
class Ctx:
    """One fresh artifact brought to a row's `before`: its `entity_ref` and anything `perform`
    needs. `ref` is `None` for a creation row, whose reference exists only after `perform`."""

    ref: str | None
    data: dict[str, Any] = field(default_factory=dict)


Setup = Callable[[Env], Awaitable[Ctx]]
Perform = Callable[[AsyncSession, Env, Ctx], Awaitable[None]]
Status = Callable[[Env, Ctx], Awaitable[str]]


@dataclass(frozen=True)
class Row:
    """One declared edge, or one creation (`before is None`), and the event it owes."""

    lifecycle: str
    before: str | None
    after: str
    action: str
    setup: Setup
    perform: Perform
    status: Status | None = None


async def _no_setup(env: Env) -> Ctx:
    return Ctx(ref=None)


def _row_id(row: Row) -> str:
    return f"{row.lifecycle}:{row.before or 'created'}>{row.after}:{row.action}"


# Dataset Version: the nine map edges (`VALID_DATASET_TRANSITIONS`).


async def _dataset_version(env: Env, *, via: tuple[DatasetStatus, ...]) -> Ctx:
    """A fresh version walked through `via` (each step a real service call)."""
    slug = f"ds-{new_uuid7().hex[-8:]}"
    report_id = new_uuid7()
    async with env.database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session, workspace_id=env.workspace_id, actor=env.actor, slug=slug
        )
        version = await datasets.new_version(
            session, workspace_id=env.workspace_id, actor=env.actor, dataset_id=dataset.id
        )
        version_id, number = version.id, version.version
    for step in via:
        async with env.database.unit_of_work() as session:
            if step is DatasetStatus.VALIDATED:
                await datasets.promote_to_validated(
                    session,
                    workspace_id=env.workspace_id,
                    actor=env.actor,
                    version_id=version_id,
                    report_id=report_id,
                    report_passed=True,
                    unacknowledged_warnings=0,
                )
            elif step is DatasetStatus.FAILED:
                await datasets.conclude_failed_validation(
                    session, workspace_id=env.workspace_id, actor=env.actor, version_id=version_id
                )
            else:
                await datasets.transition(
                    session,
                    workspace_id=env.workspace_id,
                    actor=env.actor,
                    version_id=version_id,
                    to_status=step,
                )
    return Ctx(ref=f"dataset_version:{slug}@{number}", data={"version_id": version_id})


def _dataset_setup(*via: DatasetStatus) -> Setup:
    async def setup(env: Env) -> Ctx:
        return await _dataset_version(env, via=via)

    return setup


def _dataset_to(target: DatasetStatus) -> Perform:
    async def perform(session: AsyncSession, env: Env, ctx: Ctx) -> None:
        kwargs = {
            "workspace_id": env.workspace_id,
            "actor": env.actor,
            "version_id": ctx.data["version_id"],
        }
        if target is DatasetStatus.ARCHIVED:
            await datasets.archive_version(session, reason="FR-7 table", **kwargs)
        elif target is DatasetStatus.VALIDATED:
            await datasets.promote_to_validated(
                session,
                report_id=new_uuid7(),
                report_passed=True,
                unacknowledged_warnings=0,
                **kwargs,
            )
        elif target in {DatasetStatus.FAILED, DatasetStatus.DRAFT}:
            await datasets.conclude_failed_validation(session, **kwargs)
        else:
            await datasets.transition(session, to_status=target, **kwargs)

    return perform


async def _dataset_status(env: Env, ctx: Ctx) -> str:
    async with env.database.session() as session:
        row = await session.get(DatasetVersionRow, ctx.data["version_id"])
        assert row is not None
        return str(row.status)


def _dataset_row(before: DatasetStatus, after: DatasetStatus, *via: DatasetStatus) -> Row:
    return Row(
        "dataset_version",
        before.value,
        after.value,
        f"dataset_version.{after.value}",
        _dataset_setup(*via),
        _dataset_to(after),
        _dataset_status,
    )


_D = DatasetStatus
DATASET_ROWS = [
    _dataset_row(_D.DRAFT, _D.VALIDATING),
    _dataset_row(_D.DRAFT, _D.ARCHIVED),
    _dataset_row(_D.VALIDATING, _D.VALIDATED, _D.VALIDATING),
    _dataset_row(_D.VALIDATING, _D.FAILED, _D.VALIDATING),
    # FR-53: a validated version re-validated and failing goes back to `draft`, its report
    # reference still set when it is `validating` again.
    _dataset_row(_D.VALIDATING, _D.DRAFT, _D.VALIDATING, _D.VALIDATED, _D.VALIDATING),
    _dataset_row(_D.VALIDATED, _D.VALIDATING, _D.VALIDATING, _D.VALIDATED),
    _dataset_row(_D.VALIDATED, _D.ARCHIVED, _D.VALIDATING, _D.VALIDATED),
    _dataset_row(_D.FAILED, _D.VALIDATING, _D.VALIDATING, _D.FAILED),
    _dataset_row(_D.FAILED, _D.ARCHIVED, _D.VALIDATING, _D.FAILED),
]


# Job: the six map edges (`VALID_TRANSITIONS` of `model_schema.jobs`).


async def _job(env: Env, *, running: bool) -> Ctx:
    async with env.database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.OBJECTIVE_CERTIFY,
            {"table": "FR-7"},
            env.actor,
            workspace_id=env.workspace_id,
        )
        if running:
            await job_service.transition(session, job.id, JobStatus.RUNNING, actor=env.actor)
    return Ctx(ref=f"job:{job.id}@1", data={"job_id": job.id})


def _job_setup(running: bool) -> Setup:
    async def setup(env: Env) -> Ctx:
        return await _job(env, running=running)

    return setup


def _job_to(target: JobStatus) -> Perform:
    async def perform(session: AsyncSession, env: Env, ctx: Ctx) -> None:
        await job_service.transition(session, ctx.data["job_id"], target, actor=env.actor)

    return perform


async def _job_status(env: Env, ctx: Ctx) -> str:
    async with env.database.session() as session:
        row = await session.get(JobRow, ctx.data["job_id"])
        assert row is not None
        return row.status.value


def _job_row(before: JobStatus, after: JobStatus) -> Row:
    return Row(
        "job",
        before.value,
        after.value,
        f"job.{after.value}",
        _job_setup(before is JobStatus.RUNNING),
        _job_to(after),
        _job_status,
    )


_J = JobStatus
JOB_ROWS = [
    _job_row(_J.QUEUED, _J.RUNNING),
    _job_row(_J.QUEUED, _J.CANCELLED),
    _job_row(_J.QUEUED, _J.FAILED),
    _job_row(_J.RUNNING, _J.SUCCEEDED),
    _job_row(_J.RUNNING, _J.FAILED),
    _job_row(_J.RUNNING, _J.CANCELLED),
]


# Approval Request: the map edges that have a writer, and the first of two approvals.

_MODEL_REF = "model:motor-ad-frequency@7"
_RATING_REF = str(RATING)


async def _approval(env: Env, *, ref: ArtifactRef, approved: bool) -> Ctx:
    submitter, approver = _user("s"), _user("a")
    await _with_role(env.database, env.workspace_id, approver, "approver")
    request_id = await _submit(env.database, env.workspace_id, submitter, ref=ref)
    if approved:
        async with env.database.unit_of_work() as session:
            await approval_service.decide(
                session,
                evidence_authors=_no_evidence_authors,
                workspace_id=env.workspace_id,
                request_id=request_id,
                approver=approver,
                decision=DecisionKind.APPROVE,
                comment="FR-7 table",
            )
    return Ctx(ref=str(ref), data={"request_id": request_id, "approver": approver})


def _approval_setup(ref: ArtifactRef, *, approved: bool = False) -> Setup:
    async def setup(env: Env) -> Ctx:
        return await _approval(env, ref=ref, approved=approved)

    return setup


def _approval_decides(decision: DecisionKind) -> Perform:
    async def perform(session: AsyncSession, env: Env, ctx: Ctx) -> None:
        await approval_service.decide(
            session,
            evidence_authors=_no_evidence_authors,
            workspace_id=env.workspace_id,
            request_id=ctx.data["request_id"],
            approver=ctx.data["approver"],
            decision=decision,
            comment="FR-7 table",
        )

    return perform


async def _approval_withdraws(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await approval_service.withdraw(
        session,
        workspace_id=env.workspace_id,
        request_id=ctx.data["request_id"],
        actor=ctx.data["approver"],
        reason="FR-7 table",
    )


async def _approval_status(env: Env, ctx: Ctx) -> str:
    async with env.database.session() as session:
        row = await session.get(ApprovalRequestRow, ctx.data["request_id"])
        assert row is not None
        return str(row.status)


_MODEL = ArtifactRef.parse(_MODEL_REF)
APPROVAL_ROWS = [
    Row(
        "approval_request",
        "review",
        "approved",
        "approval_request.approve",
        _approval_setup(_MODEL),
        _approval_decides(DecisionKind.APPROVE),
        _approval_status,
    ),
    Row(
        "approval_request",
        "review",
        "rejected",
        "approval_request.reject",
        _approval_setup(_MODEL),
        _approval_decides(DecisionKind.REJECT),
        _approval_status,
    ),
    Row(
        "approval_request",
        "review",
        "changes_requested",
        "approval_request.request_changes",
        _approval_setup(_MODEL),
        _approval_decides(DecisionKind.REQUEST_CHANGES),
        _approval_status,
    ),
    # Not a map edge: the first of two required approvals, the status stays `review` (DP-2).
    Row(
        "approval_request",
        "review",
        "review",
        "approval_request.approve",
        _approval_setup(RATING),
        _approval_decides(DecisionKind.APPROVE),
        _approval_status,
    ),
    Row(
        "approval_request",
        "review",
        "withdrawn",
        "approval_request.withdrawn",
        _approval_setup(_MODEL),
        _approval_withdraws,
        _approval_status,
    ),
    Row(
        "approval_request",
        "approved",
        "withdrawn",
        "approval_request.withdrawn",
        _approval_setup(_MODEL, approved=True),
        _approval_withdraws,
        _approval_status,
    ),
]


# Custom Objective and Custom Metric: six rows each, through T1's `Kind` adapters.


async def _certified_kind(env: Env, kind: Kind, *, upto: str) -> Ctx:
    """A fresh artifact brought to `draft`, `certified` or `review`."""
    row = await kind.create(env.database, env.workspace_id, env.actor)
    data: dict[str, Any] = {"id": row.id, "kind": kind}
    if upto in {"certified", "review"}:
        row = await _record(kind, env.database, env.workspace_id, env.actor, row, PASSED)
    if upto == "review":
        async with env.database.unit_of_work() as session:
            _moved, request = await kind.submit(
                session,
                workspace_id=env.workspace_id,
                actor=env.actor,
                change_summary="FR-7 table",
                **{kind.key: row.id},
            )
            data["request_id"] = request.id
        data["approver"] = await _principal_with(env.database, env.workspace_id, "approver")
    return Ctx(ref=kind.ref(row), data=data)


def _kind_setup(kind: Kind, upto: str) -> Setup:
    async def setup(env: Env) -> Ctx:
        return await _certified_kind(env, kind, upto=upto)

    return setup


def _kind_records(result: CertificateResult) -> Perform:
    async def perform(session: AsyncSession, env: Env, ctx: Ctx) -> None:
        kind: Kind = ctx.data["kind"]
        await kind.record(
            session,
            workspace_id=env.workspace_id,
            actor=env.actor,
            result=result,
            **{kind.key: ctx.data["id"]},
        )

    return perform


async def _kind_submits(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    kind: Kind = ctx.data["kind"]
    await kind.submit(
        session,
        workspace_id=env.workspace_id,
        actor=env.actor,
        change_summary="FR-7 table",
        **{kind.key: ctx.data["id"]},
    )


def _kind_decides(decision: DecisionKind) -> Perform:
    async def perform(session: AsyncSession, env: Env, ctx: Ctx) -> None:
        kind: Kind = ctx.data["kind"]
        approver = ctx.data["approver"]
        decided = await approval_service.decide(
            session,
            workspace_id=env.workspace_id,
            approver=approver,
            request_id=ctx.data["request_id"],
            decision=decision,
            comment="FR-7 table",
        )
        await kind.apply(session, workspace_id=env.workspace_id, actor=approver, request=decided)

    return perform


async def _kind_status(env: Env, ctx: Ctx) -> str:
    kind: Kind = ctx.data["kind"]
    async with env.database.session() as session:
        row = await session.get(kind.row, ctx.data["id"])
        assert row is not None
        return str(row.status)


def _kind_rows(kind: Kind) -> list[Row]:
    p = kind.prefix

    def row(before: str, after: str, action: str, upto: str, perform: Perform) -> Row:
        setup = _kind_setup(kind, upto)
        return Row(p, before, after, f"{p}.{action}", setup, perform, _kind_status)

    return [
        row("draft", "certified", "certified", "draft", _kind_records(PASSED)),
        row("draft", "draft", "certification_failed", "draft", _kind_records(FAILED)),
        row("certified", "draft", "certification_failed", "certified", _kind_records(FAILED)),
        row("certified", "review", "submitted", "certified", _kind_submits),
        row("review", "approved", "approved", "review", _kind_decides(DecisionKind.APPROVE)),
        row(
            "review",
            "certified",
            "certified",
            "review",
            _kind_decides(DecisionKind.REQUEST_CHANGES),
        ),
    ]


KIND_ROWS = [r for name in sorted(KINDS) for r in _kind_rows(KINDS[name])]


# Rating Version: three rows.


async def _rating(env: Env, *, submitted: bool) -> Ctx:
    analyst = await _principal(env.database, env.workspace_id, "analyst")
    actuary = await _principal(env.database, env.workspace_id, "pricing_actuary")
    rating_id = await _draft(
        env.database,
        env.workspace_id,
        analyst,
        ArtifactRef(type="model", slug="fremtpl2-glm", version=1),
    )
    gate = await _gate(env.database, env.workspace_id)
    await gate.adopt(rating_id)
    data: dict[str, Any] = {"id": rating_id, "gate": gate, "actuary": actuary}
    async with env.database.unit_of_work() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=env.workspace_id, rating_version_id=rating_id
        )
        ref = f"rating_version:{row.slug}@{row.version}"
    if submitted:
        async with env.database.unit_of_work() as session:
            _row, request = await rating_service.submit_for_review(
                session,
                workspace_id=env.workspace_id,
                actor=actuary,
                rating_version_id=rating_id,
                change_summary="FR-7 table",
                blob_store=gate.blob_store,
                load_compiled=gate.load,
            )
            data["request_id"] = request.id
        data["approvers"] = [
            await _principal(env.database, env.workspace_id, "approver"),
            await _principal(env.database, env.workspace_id, "approver"),
        ]
    return Ctx(ref=ref, data=data)


def _rating_setup(*, submitted: bool) -> Setup:
    async def setup(env: Env) -> Ctx:
        return await _rating(env, submitted=submitted)

    return setup


async def _rating_submits(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    gate = ctx.data["gate"]
    await rating_service.submit_for_review(
        session,
        workspace_id=env.workspace_id,
        actor=ctx.data["actuary"],
        rating_version_id=ctx.data["id"],
        change_summary="FR-7 table",
        blob_store=gate.blob_store,
        load_compiled=gate.load,
    )


def _rating_decides(decision: DecisionKind, *, approvers: int) -> Perform:
    async def perform(session: AsyncSession, env: Env, ctx: Ctx) -> None:
        for who in ctx.data["approvers"][:approvers]:
            request = await approval_service.decide(
                session,
                evidence_authors=rating_service.golden_quote_delta_authors,
                workspace_id=env.workspace_id,
                request_id=ctx.data["request_id"],
                approver=who,
                decision=decision,
                comment="FR-7 table",
            )
            await rating_service.apply_approval_decision(
                session, workspace_id=env.workspace_id, actor=who, request=request
            )

    return perform


async def _rating_status(env: Env, ctx: Ctx) -> str:
    async with env.database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=env.workspace_id, rating_version_id=ctx.data["id"]
        )
        return str(row.status)


RATING_ROWS = [
    Row(
        "rating_version",
        "draft",
        "review",
        "rating_version.submitted",
        _rating_setup(submitted=False),
        _rating_submits,
        _rating_status,
    ),
    Row(
        "rating_version",
        "review",
        "approved",
        "rating_version.approved",
        _rating_setup(submitted=True),
        _rating_decides(DecisionKind.APPROVE, approvers=2),
        _rating_status,
    ),
    Row(
        "rating_version",
        "review",
        "draft",
        "rating_version.returned_to_draft",
        _rating_setup(submitted=True),
        _rating_decides(DecisionKind.REJECT, approvers=1),
        _rating_status,
    ),
]


# Model: the eight map edges. Setup fits one real model per row (the slow part); the later
# versions are inserted as `test_model_lifecycle` inserts them.


async def _fitted_model(env: Env) -> Ctx:
    actor, model_id = await _fit(env.database, env.blob_store, env.workspace_id)
    async with env.database.session() as session:
        row = await session.get(ModelRow, model_id)
        assert row is not None
        ref = f"model:{row.model_family_slug}@{row.version}"
    return Ctx(ref=ref, data={"id": model_id, "actor": actor})


async def _draft_copy(env: Env, fitted: Ctx) -> Ctx:
    """A draft sibling of `fitted`'s model, as `modelling.reserve_model` leaves one."""
    async with env.database.unit_of_work() as session:
        first = await session.get(ModelRow, fitted.data["id"])
        assert first is not None
        row = ModelRow(
            workspace_id=env.workspace_id,
            model_family_slug=first.model_family_slug,
            version=first.version + 1,
            status=ModelStatus.DRAFT.value,
            dataset_version_id=first.dataset_version_id,
            spec=first.spec,
            spec_hash=f"v2:sha256:{new_uuid7().hex}",
            parent_model_id=first.id,
            change_reason="refit_new_data",
        )
        session.add(row)
        await session.flush()
        data = {**fitted.data, "id": row.id, "first_id": first.id}
        return Ctx(ref=f"model:{row.model_family_slug}@{row.version}", data=data)


async def _submit_model(env: Env, ctx: Ctx) -> Ctx:
    async with env.database.unit_of_work() as session:
        _row, request = await model_service.submit_for_review(
            session,
            workspace_id=env.workspace_id,
            actor=ctx.data["actor"],
            model_id=ctx.data["id"],
            change_summary="FR-7 table",
        )
        request_id = request.id
    approver = await _principal_with(env.database, env.workspace_id, "approver")
    return Ctx(ref=ctx.ref, data={**ctx.data, "request_id": request_id, "approver": approver})


async def _decide_model(
    env: Env, ctx: Ctx, decision: DecisionKind, session: AsyncSession | None = None
) -> None:
    async def run(session: AsyncSession) -> None:
        decided = await approval_service.decide(
            session,
            workspace_id=env.workspace_id,
            request_id=ctx.data["request_id"],
            approver=ctx.data["approver"],
            decision=decision,
            comment="FR-7 table",
        )
        await model_service.apply_approval_decision(
            session, workspace_id=env.workspace_id, actor=ctx.data["approver"], request=decided
        )

    if session is not None:
        await run(session)
        return
    async with env.database.unit_of_work() as own:
        await run(own)


def _model_setup(upto: str) -> Setup:
    """`draft`, `fitted`, `review`, `approved`, `superseding` (approved, with a later version
    in review) or `superseded`: the model to act on."""

    async def setup(env: Env) -> Ctx:
        fitted = await _fitted_model(env)
        if upto == "fitted":
            return fitted
        if upto == "draft":
            return await _draft_copy(env, fitted)
        ctx = await _submit_model(env, fitted)
        if upto == "review":
            return ctx
        await _decide_model(env, ctx, DecisionKind.APPROVE)
        if upto == "approved":
            return ctx
        # A later version of the family, in review: approving it supersedes this one.
        later_id = await _next_version_of(env.database, env.workspace_id, ctx.data["id"])
        later = await _submit_model(env, Ctx(ref="", data={**ctx.data, "id": later_id}))
        if upto == "superseding":
            return Ctx(ref=ctx.ref, data={**ctx.data, "later": later})
        await _decide_model(env, later, DecisionKind.APPROVE)
        return ctx

    return setup


def _model_performs(step: str) -> Perform:
    async def perform(session: AsyncSession, env: Env, ctx: Ctx) -> None:
        if step == "fit":
            fitted_id = ctx.data["first_id"]
            async with env.database.session() as read:
                first = await read.get(ModelRow, fitted_id)
                assert first is not None
                result = model_service.to_model(first).fit_result
                evidence = await diagnostics_service.load_diagnostics(
                    read, workspace_id=env.workspace_id, model_id=fitted_id
                )
            assert result is not None
            await model_service.record_fit(
                session,
                workspace_id=env.workspace_id,
                actor=ctx.data["actor"],
                model_id=ctx.data["id"],
                fit_result=result,
                diagnostics=evidence,
            )
        elif step == "submit":
            await model_service.submit_for_review(
                session,
                workspace_id=env.workspace_id,
                actor=ctx.data["actor"],
                model_id=ctx.data["id"],
                change_summary="FR-7 table",
            )
        elif step == "archive":
            await model_service.archive(
                session,
                workspace_id=env.workspace_id,
                actor=ctx.data["actor"],
                model_id=ctx.data["id"],
            )
        elif step == "approve":
            await _decide_model(env, ctx, DecisionKind.APPROVE, session)
        elif step == "changes":
            await _decide_model(env, ctx, DecisionKind.REQUEST_CHANGES, session)
        else:  # supersede: approve the later version, whose hook supersedes this one
            await _decide_model(env, ctx.data["later"], DecisionKind.APPROVE, session)

    return perform


async def _model_status(env: Env, ctx: Ctx) -> str:
    async with env.database.session() as session:
        row = await session.get(ModelRow, ctx.data["id"])
        assert row is not None
        return str(row.status)


def _model_row(before: str, after: str, action: str, upto: str, step: str) -> Row:
    return Row(
        "model",
        before,
        after,
        f"model.{action}",
        _model_setup(upto),
        _model_performs(step),
        _model_status,
    )


MODEL_ROWS = [
    _model_row("draft", "fitted", "fitted", "draft", "fit"),
    _model_row("fitted", "review", "submitted", "fitted", "submit"),
    _model_row("review", "approved", "approved", "review", "approve"),
    _model_row("review", "fitted", "fitted", "review", "changes"),
    _model_row("approved", "superseded", "superseded", "superseding", "supersede"),
    _model_row("fitted", "archived", "archived", "fitted", "archive"),
    _model_row("draft", "archived", "archived", "draft", "archive"),
    _model_row("superseded", "archived", "archived", "superseded", "archive"),
]


# Peril Structure: five rows. Setup books a dataset and fits the component models once per
# row; the reconciliation is replayed from a first, really reconciled structure.


async def _peril_book(env: Env) -> dict[str, Any]:
    actor, version_id, area, split = await _book(env.database, env.blob_store, env.workspace_id)
    peril = await _burning_cost_peril(
        env.database, env.blob_store, env.workspace_id, actor, version_id, area, split
    )
    await _set_model_status(
        env.database,
        await _model_id(env.database, str(peril.burning_cost_model)),
        ModelStatus.APPROVED,
    )
    return {"actor": actor, "peril": peril, "slug": f"ps-{uuid4().hex[-6:]}"}


async def _peril_draft(env: Env, book: dict[str, Any]) -> UUID:
    async with env.database.unit_of_work() as session:
        row = await peril_service.create_structure(
            session,
            workspace_id=env.workspace_id,
            actor=book["actor"],
            slug=book["slug"],
            perils=[book["peril"]],
            excluded_perils=[],
        )
        return row.id


async def _peril_reconciled(env: Env, book: dict[str, Any]) -> PerilStructureRow:
    return await _reconciled(
        env.database, env.blob_store, env.workspace_id, book["actor"], [book["peril"]], book["slug"]
    )


async def _peril_submit(env: Env, book: dict[str, Any], structure_id: UUID) -> UUID:
    async with env.database.unit_of_work() as session:
        _row, request = await peril_service.submit_for_review(
            session,
            workspace_id=env.workspace_id,
            actor=book["actor"],
            structure_id=structure_id,
            change_summary="FR-7 table",
        )
        return request.id


def _peril_setup(upto: str) -> Setup:
    """`draft` (a draft beside a reconciled first version), `reconciled`, `review`, or
    `superseding` (approved, with a later version in review)."""

    async def setup(env: Env) -> Ctx:
        book = await _peril_book(env)
        approver = await _principal_with(env.database, env.workspace_id, "approver")
        first = await _peril_reconciled(env, book)
        data: dict[str, Any] = {"book": book, "approver": approver, "id": first.id}
        ref = f"peril_structure:{first.slug}@{first.version}"
        if upto == "draft":
            data["reconciliation"] = first.reconciliation
            data["id"] = await _peril_draft(env, book)
            ref = f"peril_structure:{first.slug}@{first.version + 1}"
        elif upto in {"review", "superseding"}:
            data["request_id"] = await _peril_submit(env, book, first.id)
            if upto == "superseding":
                async with env.database.unit_of_work() as session:
                    decided = await approval_service.decide(
                        session,
                        workspace_id=env.workspace_id,
                        request_id=data["request_id"],
                        approver=approver,
                        decision=DecisionKind.APPROVE,
                        comment="FR-7 table",
                    )
                    await peril_service.apply_approval_decision(
                        session, workspace_id=env.workspace_id, actor=approver, request=decided
                    )
                later = await _peril_reconciled(env, book)
                data["later_request_id"] = await _peril_submit(env, book, later.id)
        return Ctx(ref=ref, data=data)

    return setup


def _peril_performs(step: str) -> Perform:
    async def perform(session: AsyncSession, env: Env, ctx: Ctx) -> None:
        book, approver = ctx.data["book"], ctx.data["approver"]
        if step == "reconcile":
            await peril_service.record_reconciliation(
                session,
                workspace_id=env.workspace_id,
                actor=book["actor"],
                structure_id=ctx.data["id"],
                reconciliation=Reconciliation.model_validate(ctx.data["reconciliation"]),
            )
        elif step == "submit":
            await peril_service.submit_for_review(
                session,
                workspace_id=env.workspace_id,
                actor=book["actor"],
                structure_id=ctx.data["id"],
                change_summary="FR-7 table",
            )
        else:
            decision = DecisionKind.REQUEST_CHANGES if step == "changes" else DecisionKind.APPROVE
            request_id = ctx.data.get("later_request_id", ctx.data.get("request_id"))
            decided = await approval_service.decide(
                session,
                workspace_id=env.workspace_id,
                request_id=request_id,
                approver=approver,
                decision=decision,
                comment="FR-7 table",
            )
            await peril_service.apply_approval_decision(
                session, workspace_id=env.workspace_id, actor=approver, request=decided
            )

    return perform


async def _peril_status(env: Env, ctx: Ctx) -> str:
    async with env.database.session() as session:
        row = await session.get(PerilStructureRow, ctx.data["id"])
        assert row is not None
        return str(row.status)


def _peril_row(before: str, after: str, action: str, upto: str, step: str) -> Row:
    return Row(
        "peril_structure",
        before,
        after,
        f"peril_structure.{action}",
        _peril_setup(upto),
        _peril_performs(step),
        _peril_status,
    )


PERIL_ROWS = [
    _peril_row("draft", "reconciled", "reconciled", "draft", "reconcile"),
    _peril_row("reconciled", "review", "submitted", "reconciled", "submit"),
    _peril_row("review", "approved", "approved", "review", "approve"),
    _peril_row("review", "reconciled", "reconciled", "review", "changes"),
    _peril_row("approved", "superseded", "superseded", "superseding", "approve"),
]


# Validation Rule: three rows. Reference Table Version: one.


async def _rule(env: Env, *, upto: str) -> Ctx:
    actor = await _actuary(env.database, env.workspace_id)
    async with env.database.unit_of_work() as session:
        row = await rule_service.create_rule(
            session,
            workspace_id=env.workspace_id,
            actor=actor,
            slug=f"rng-{new_uuid7().hex[-8:]}",
            layer=ValidationLayer.ACTUARIAL_SANITY,
            check="range",
            severity=Severity.WARN,
            target={"table": "policy_exposure", "column": "exposure_years"},
            params={"min_inclusive": 0, "key_columns": ["policy_id"]},
        )
        await stored_dry_run_report(session, workspace_id=env.workspace_id, rule=row)
        rule_id, slug, version = row.id, row.slug, row.version
    data: dict[str, Any] = {"id": rule_id, "actor": actor}
    if upto == "review":
        async with env.database.unit_of_work() as session:
            await rule_service.submit_for_review(
                session,
                workspace_id=env.workspace_id,
                actor=actor,
                rule_id=rule_id,
                change_summary="FR-7 table",
            )
        data["approver"] = await _principal_with(env.database, env.workspace_id, "approver")
    return Ctx(ref=f"validation_rule:{slug}@{version}", data=data)


def _rule_setup(upto: str) -> Setup:
    async def setup(env: Env) -> Ctx:
        return await _rule(env, upto=upto)

    return setup


async def _rule_submits(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await rule_service.submit_for_review(
        session,
        workspace_id=env.workspace_id,
        actor=ctx.data["actor"],
        rule_id=ctx.data["id"],
        change_summary="FR-7 table",
    )


def _rule_decides(decision: DecisionKind) -> Perform:
    async def perform(session: AsyncSession, env: Env, ctx: Ctx) -> None:
        rule = await session.get(ValidationRuleRow, ctx.data["id"])
        assert rule is not None
        request_id = await rule_service.open_request_for(
            session, workspace_id=env.workspace_id, row=rule
        )
        decided = await approval_service.decide(
            session,
            workspace_id=env.workspace_id,
            request_id=request_id,
            approver=ctx.data["approver"],
            decision=decision,
            comment="FR-7 table",
        )
        await rule_service.apply_approval_decision(
            session, workspace_id=env.workspace_id, actor=ctx.data["approver"], request=decided
        )

    return perform


async def _rule_status(env: Env, ctx: Ctx) -> str:
    async with env.database.session() as session:
        row = await session.get(ValidationRuleRow, ctx.data["id"])
        assert row is not None
        return str(row.status)


RULE_ROWS = [
    Row(
        "validation_rule",
        "draft",
        "review",
        "validation_rule.submitted",
        _rule_setup("draft"),
        _rule_submits,
        _rule_status,
    ),
    Row(
        "validation_rule",
        "review",
        "approved",
        "validation_rule.approved",
        _rule_setup("review"),
        _rule_decides(DecisionKind.APPROVE),
        _rule_status,
    ),
    Row(
        "validation_rule",
        "review",
        "draft",
        "validation_rule.draft",
        _rule_setup("review"),
        _rule_decides(DecisionKind.REQUEST_CHANGES),
        _rule_status,
    ),
]


async def _reference_version(env: Env) -> Ctx:
    admin = await _principal(env.database, env.workspace_id, "admin")
    slug = f"ref-{new_uuid7().hex[-8:]}"
    async with env.database.unit_of_work() as session:
        await reference_service.create_table(
            session,
            workspace_id=env.workspace_id,
            actor=admin,
            slug=slug,
            key_columns=["code"],
            payload_columns=["relativity"],
        )
        version = await reference_service.load_version(
            session,
            workspace_id=env.workspace_id,
            actor=admin,
            slug=slug,
            rows=[{"key": "A", "payload": {"relativity": 1}, "effective_from": "2026-01-01"}],
        )
        number = version.version
    return Ctx(ref=f"reference_table:{slug}@{number}", data={"slug": slug, "admin": admin})


async def _reference_publishes(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await reference_service.publish_version(
        session,
        workspace_id=env.workspace_id,
        actor=ctx.data["admin"],
        slug=ctx.data["slug"],
        version=1,
    )


async def _reference_status(env: Env, ctx: Ctx) -> str:
    async with env.database.session() as session:
        row = (
            await session.execute(
                select(ReferenceTableVersionRow)
                .join(
                    ReferenceTableRow,
                    ReferenceTableRow.id == ReferenceTableVersionRow.reference_table_id,
                )
                .where(
                    ReferenceTableRow.workspace_id == env.workspace_id,
                    ReferenceTableRow.slug == ctx.data["slug"],
                )
            )
        ).scalar_one()
        return str(row.status)


REFERENCE_ROWS = [
    Row(
        "reference_table_version",
        "draft",
        "published",
        "reference_table_version.published",
        _reference_version,
        _reference_publishes,
        _reference_status,
    ),
]


# Deployment Request: four rows. Setup walks the real path with `switch=None`, as
# `test_deployments.py` does (no PUBLISH, so no `test_deployment_switch*` coupling).


async def _deployment_request(env: Env, *, upto: str) -> Ctx:
    deployer = await _principal(env.database, env.workspace_id, "deployer")
    version_ref = await approved_version(env.database, env.workspace_id, new_uuid7())
    rating_ref = ArtifactRef.parse(version_ref)
    for target in ("dev", "uat"):
        async with env.database.unit_of_work() as session:
            await deployment_service.deploy(
                session,
                workspace_id=env.workspace_id,
                actor=deployer,
                environment=target,
                body=DeploymentCreate(rating_version_ref=rating_ref, reason="release"),
                switch=None,
            )
    if upto == "deployed":
        return Ctx(ref=None, data={"deployer": deployer, "rating_ref": rating_ref})
    async with env.database.unit_of_work() as session:
        request = await deployment_service.submit_request(
            session,
            workspace_id=env.workspace_id,
            actor=deployer,
            environment="prod",
            body=DeploymentRequestCreate(rating_version_ref=rating_ref, change_summary="FR-7"),
        )
    async with env.database.session() as session:
        approval = (
            await session.execute(
                select(ApprovalRequestRow).where(
                    ApprovalRequestRow.workspace_id == env.workspace_id,
                    ApprovalRequestRow.artifact_ref == str(request.ref),
                )
            )
        ).scalar_one()
    decider = await _principal(env.database, env.workspace_id, "approver")
    await grant_roles_as_owner(env.workspace_id, decider.id, "deployer")
    data: dict[str, Any] = {
        "deployer": deployer,
        "decider": decider,
        "approval_id": approval.id,
        "rating_ref": rating_ref,
        "request_ref": request.ref,
    }
    if upto == "approved":
        async with env.database.unit_of_work() as session:
            decided = await approval_service.decide(
                session,
                workspace_id=env.workspace_id,
                request_id=approval.id,
                approver=decider,
                decision=DecisionKind.APPROVE,
                comment="FR-7 table",
            )
            await deployment_service.apply_approval_decision(
                session, workspace_id=env.workspace_id, actor=decider, request=decided
            )
    return Ctx(ref=str(request.ref), data=data)


def _deployment_setup(upto: str) -> Setup:
    async def setup(env: Env) -> Ctx:
        return await _deployment_request(env, upto=upto)

    return setup


def _deployment_decides(decision: DecisionKind | None) -> Perform:
    """A decision, or (`None`) the approver's withdrawal, carried into the request."""

    async def perform(session: AsyncSession, env: Env, ctx: Ctx) -> None:
        decider = ctx.data["decider"]
        if decision is None:
            decided = await approval_service.withdraw(
                session,
                workspace_id=env.workspace_id,
                request_id=ctx.data["approval_id"],
                actor=decider,
                reason="FR-7 table",
            )
        else:
            decided = await approval_service.decide(
                session,
                workspace_id=env.workspace_id,
                request_id=ctx.data["approval_id"],
                approver=decider,
                decision=decision,
                comment="FR-7 table",
            )
        await deployment_service.apply_approval_decision(
            session, workspace_id=env.workspace_id, actor=decider, request=decided
        )

    return perform


async def _deployment_executes(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await deployment_service.deploy(
        session,
        workspace_id=env.workspace_id,
        actor=ctx.data["deployer"],
        environment="prod",
        body=DeploymentCreate(
            rating_version_ref=ctx.data["rating_ref"],
            reason="release",
            deployment_request_ref=ctx.data["request_ref"],
        ),
        switch=None,
    )


async def _deployment_status(env: Env, ctx: Ctx) -> str:
    async with env.database.session() as session:
        row = (
            await session.execute(
                select(DeploymentRequestRow.status).where(
                    DeploymentRequestRow.workspace_id == env.workspace_id
                )
            )
        ).scalar_one()
        return str(row)


def _deployment_row(before: str, after: str, upto: str, perform: Perform) -> Row:
    return Row(
        "deployment_request",
        before,
        after,
        f"deployment_request.{after}",
        _deployment_setup(upto),
        perform,
        _deployment_status,
    )


DEPLOYMENT_ROWS = [
    _deployment_row("review", "approved", "review", _deployment_decides(DecisionKind.APPROVE)),
    _deployment_row("review", "rejected", "review", _deployment_decides(DecisionKind.REJECT)),
    _deployment_row("review", "withdrawn", "review", _deployment_decides(None)),
    _deployment_row("approved", "executed", "approved", _deployment_executes),
]


# Creation rows (PL 8376 DP-4 (a)): the event that brings a governed Artifact into existence.
# `before is None`; the entity reference exists only after `perform`, so the commit leg finds
# the event by its action alone.


async def _book_setup(env: Env) -> Ctx:
    actor, version_id, area, split = await _book(env.database, env.blob_store, env.workspace_id)
    return Ctx(
        ref=None, data={"actor": actor, "version_id": version_id, "area": area, "split": split}
    )


async def _dataset_only(env: Env) -> Ctx:
    async with env.database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session,
            workspace_id=env.workspace_id,
            actor=env.actor,
            slug=f"ds-{new_uuid7().hex[-8:]}",
        )
    return Ctx(ref=None, data={"dataset_id": dataset.id})


async def _version_only(env: Env) -> Ctx:
    ctx = await _dataset_only(env)
    async with env.database.unit_of_work() as session:
        version = await datasets.new_version(
            session,
            workspace_id=env.workspace_id,
            actor=env.actor,
            dataset_id=ctx.data["dataset_id"],
        )
    return Ctx(ref=None, data={"version_id": version.id})


async def _creates_version(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await datasets.new_version(
        session, workspace_id=env.workspace_id, actor=env.actor, dataset_id=ctx.data["dataset_id"]
    )


async def _stores_report(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    started = datetime.now(UTC)
    report = ValidationReport(
        id=uuid4(),
        dataset_version_id=ctx.data["version_id"],
        rule_set_id=uuid4(),
        rule_set_version=1,
        started_at=started,
        finished_at=started + timedelta(seconds=1),
        results=(),
    )
    await validation_service.store_report(
        session, workspace_id=env.workspace_id, actor=env.actor, report=report
    )


async def _reserves_model(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await model_service.reserve_model(
        session,
        workspace_id=env.workspace_id,
        actor=ctx.data["actor"],
        spec=_spec(ctx.data["version_id"], (ctx.data["area"],), split_ref=ctx.data["split"]),
    )


async def _creates_objective(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await _new_objective(session, env.workspace_id, env.actor)


async def _creates_metric(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await _new_metric(session, env.workspace_id, env.actor)


async def _peril_book_setup(env: Env) -> Ctx:
    return Ctx(ref=None, data={"book": await _peril_book(env)})


async def _creates_peril(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    book = ctx.data["book"]
    await peril_service.create_structure(
        session,
        workspace_id=env.workspace_id,
        actor=book["actor"],
        slug=book["slug"],
        perils=[book["peril"]],
        excluded_perils=[],
    )


async def _actuary_setup(env: Env) -> Ctx:
    return Ctx(ref=None, data={"actor": await _actuary(env.database, env.workspace_id)})


async def _creates_rule(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await rule_service.create_rule(
        session,
        workspace_id=env.workspace_id,
        actor=ctx.data["actor"],
        slug=f"rng-{new_uuid7().hex[-8:]}",
        layer=ValidationLayer.ACTUARIAL_SANITY,
        check="range",
        severity=Severity.WARN,
        target={"table": "policy_exposure", "column": "exposure_years"},
        params={"min_inclusive": 0, "key_columns": ["policy_id"]},
    )


async def _analyst_setup(env: Env) -> Ctx:
    return Ctx(
        ref=None, data={"actor": await _principal(env.database, env.workspace_id, "analyst")}
    )


async def _creates_rating_version(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await rating_service.create_rating_version(
        session,
        workspace_id=env.workspace_id,
        actor=ctx.data["actor"],
        slug="fremtpl2-demo",
        dataset_version_id=new_uuid7(),
        model_ref=ArtifactRef(type="model", slug="fremtpl2-glm", version=1),
    )


async def _submits_approval(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    # The version's creation event, as its owning module records it (`test_approvals._submit`).
    await audit.record(
        session,
        workspace_id=env.workspace_id,
        actor=AUTHOR,
        source=JobSource.API,
        action=approval_service.CREATION_ACTIONS[_MODEL.type],
        entity_ref=str(_MODEL),
    )
    await approval_service.submit(
        session,
        workspace_id=env.workspace_id,
        submitter=_user("s"),
        artifact_ref=_MODEL,
        change_summary="FR-7 table",
    )


async def _deployed_setup(env: Env) -> Ctx:
    return await _deployment_request(env, upto="deployed")


async def _creates_deployment_request(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await deployment_service.submit_request(
        session,
        workspace_id=env.workspace_id,
        actor=ctx.data["deployer"],
        environment="prod",
        body=DeploymentRequestCreate(
            rating_version_ref=ctx.data["rating_ref"], change_summary="FR-7"
        ),
    )


async def _submits_job(session: AsyncSession, env: Env, ctx: Ctx) -> None:
    await job_service.submit(
        session,
        JobKind.OBJECTIVE_CERTIFY,
        {"table": "FR-7"},
        env.actor,
        workspace_id=env.workspace_id,
    )


def _created(lifecycle: str, action: str, setup: Setup, perform: Perform) -> Row:
    return Row(lifecycle, None, "created", action, setup, perform)


CREATION_ROWS = [
    _created("dataset_version", "dataset_version.created", _dataset_only, _creates_version),
    _created("validation_report", "validation_report.created", _version_only, _stores_report),
    _created("model", "model.reserved", _book_setup, _reserves_model),
    _created("custom_objective", "custom_objective.created", _no_setup, _creates_objective),
    _created("custom_metric", "custom_metric.created", _no_setup, _creates_metric),
    _created("peril_structure", "peril_structure.created", _peril_book_setup, _creates_peril),
    _created("validation_rule", "validation_rule.created", _actuary_setup, _creates_rule),
    _created("rating_version", "rating_version.created", _analyst_setup, _creates_rating_version),
    _created("approval_request", "approval_request.submitted", _no_setup, _submits_approval),
    _created(
        "deployment_request",
        "deployment_request.created",
        _deployed_setup,
        _creates_deployment_request,
    ),
    _created("job", "job.submitted", _no_setup, _submits_job),
]

ROWS: list[Row] = [
    *DATASET_ROWS,
    *JOB_ROWS,
    *APPROVAL_ROWS,
    *KIND_ROWS,
    *RATING_ROWS,
    *MODEL_ROWS,
    *PERIL_ROWS,
    *RULE_ROWS,
    *REFERENCE_ROWS,
    *DEPLOYMENT_ROWS,
    *CREATION_ROWS,
]


# The two guards and the table's test (PL 8376 T3).

MAPS: dict[str, dict[Any, frozenset[Any]]] = {
    "approval_request": VALID_APPROVAL_TRANSITIONS,
    "dataset_version": VALID_DATASET_TRANSITIONS,
    "job": VALID_JOB_TRANSITIONS,
    "custom_metric": VALID_METRIC_TRANSITIONS,
    "model": VALID_MODEL_TRANSITIONS,
    "custom_objective": VALID_OBJECTIVE_TRANSITIONS,
    "peril_structure": VALID_PERIL_STRUCTURE_TRANSITIONS,
    "rating_version": VALID_RATING_VERSION_TRANSITIONS,
}

#: Declared, with no writer in P2: the reason is the ruling that carried the edge. Never empty.
NOT_BUILT: dict[tuple[str, str, str], str] = {
    ("custom_objective", "draft", "deprecated"): "PL 8376 DP-9, carry C2 (FD-2007)",
    ("custom_objective", "certified", "deprecated"): "PL 8376 DP-9, carry C2 (FD-2007)",
    ("custom_objective", "approved", "deprecated"): "PL 8376 DP-9, carry C2 (FD-2007)",
    ("custom_metric", "draft", "deprecated"): "PL 8376 DP-9, carry C2 (FD-2007)",
    ("custom_metric", "certified", "deprecated"): "PL 8376 DP-9, carry C2 (FD-2007)",
    ("custom_metric", "approved", "deprecated"): "PL 8376 DP-9, carry C2 (FD-2007)",
    ("peril_structure", "draft", "archived"): "PL 8376 DP-10, carry C3 (FD-2007)",
    ("peril_structure", "reconciled", "archived"): "PL 8376 DP-10, carry C3 (FD-2007)",
    ("peril_structure", "superseded", "archived"): "PL 8376 DP-10, carry C3 (FD-2007)",
}

#: Statuses no P2 path may write: a writer built later owes its Audit Event and a row.
_UNBUILT_WRITES = (
    "ObjectiveStatus.DEPRECATED",
    "MetricStatus.DEPRECATED",
    "PerilStructureStatus.ARCHIVED",
)
_SRC = Path(__file__).resolve().parents[1] / "src"


def _declared() -> set[tuple[str, str, str]]:
    return {(n, a.value, b.value) for n, m in MAPS.items() for a, to in m.items() for b in to}


def _rowed() -> set[tuple[str, str, str]]:
    return {(r.lifecycle, r.before, r.after) for r in ROWS if r.lifecycle in MAPS and r.before}


@pytest.mark.req("FR-7")
def test_every_declared_edge_has_a_row_or_a_reason() -> None:
    """The list comes from the maps, never from the call sites (FD-1723): an edge is either
    asserted by a row or named here with the ruling that left it unbuilt."""
    declared, rowed = _declared(), _rowed()
    assert declared - rowed == set(NOT_BUILT)
    assert not set(NOT_BUILT) & rowed
    assert all(reason.strip() for reason in NOT_BUILT.values())


@pytest.mark.req("FR-7")
def test_a_not_built_edge_has_no_writer() -> None:
    """A write of an unbuilt status fails this test, naming the file: whoever builds it owes
    the event and a row."""
    hits = [
        f"{path.relative_to(_SRC)}: {name}"
        for path in sorted(_SRC.rglob("*.py"))
        for name in _UNBUILT_WRITES
        if name in path.read_text(encoding="utf-8")
    ]
    assert hits == []


class _RollbackError(Exception):
    """Raised inside a unit of work to prove the event leaves with the change."""


async def _sequence(database: Database, workspace_id: UUID) -> int:
    async with database.session() as session:
        return int(
            await session.scalar(
                select(func.coalesce(func.max(AuditEventRow.sequence), 0)).where(
                    AuditEventRow.workspace_id == workspace_id
                )
            )
            or 0
        )


async def _owed(
    database: Database, workspace_id: UUID, row: Row, ref: str | None, since: int
) -> list[AuditEventRow]:
    async with database.session() as session:
        query = select(AuditEventRow).where(
            AuditEventRow.workspace_id == workspace_id,
            AuditEventRow.action == row.action,
            AuditEventRow.sequence > since,
        )
        if ref is not None:
            query = query.where(AuditEventRow.entity_ref == ref)
        return list((await session.scalars(query.order_by(AuditEventRow.sequence))).all())


@pytest.mark.req("FR-7")
@pytest.mark.req("FR-368")
@pytest.mark.parametrize("leg", ["commit", "rollback"])
@pytest.mark.parametrize("row", ROWS, ids=_row_id)
async def test_a_declared_transition_writes_its_event_in_its_transaction(
    database: Database, workspace_id: UUID, blob_store: Any, row: Row, leg: str
) -> None:
    """One event with the row's `action`, `before` and `after` on commit; none, and the status
    unmoved, when the unit of work raises after the call."""
    env = Env(database, workspace_id, await _actuary(database, workspace_id), blob_store)
    ctx = await row.setup(env)
    since = await _sequence(database, workspace_id)

    if leg == "rollback":
        with pytest.raises(_RollbackError):  # noqa: PT012
            async with database.unit_of_work() as session:
                await row.perform(session, env, ctx)
                raise _RollbackError
        assert await _owed(database, workspace_id, row, ctx.ref, since) == []
        if row.status is not None:
            assert await row.status(env, ctx) == row.before
        return

    async with database.unit_of_work() as session:
        await row.perform(session, env, ctx)
    (event,) = await _owed(database, workspace_id, row, ctx.ref, since)
    if row.before is None:
        assert not event.before
        return
    assert (event.before or {}).get("status") == row.before
    assert (event.after or {}).get("status") == row.after
    if row.status is not None:
        assert await row.status(env, ctx) == row.after
