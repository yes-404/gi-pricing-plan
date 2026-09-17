"""Custom Metrics — the platform lifecycle only (`02` §4.13, FR-MODEL-45, 105).

Parallel to `test_custom_objectives.py`'s approval-decision coverage, and narrow on
purpose: `test_custom_metrics_api.py` owns the HTTP surface and
`test_custom_metrics_table.py` owns the row-level invariants. This owns the one thing
neither reaches — `metrics.apply_approval_decision`, added alongside
`modelling.apply_approval_decision` and `objectives.apply_approval_decision` at
`approvals.py`'s `_carry_to_the_artifact` so `review -> approved` is actually reachable
and not just a declared edge in `VALID_METRIC_TRANSITIONS`.

Certification here goes straight through `service.record_certificate` with a
hand-built `CertificateResult`, not the real `METRIC_CERTIFY` Job — `test_custom_objectives
.test_a_failed_certificate_is_recorded_and_clears_the_passing_one` uses the same shortcut
for the same reason: proving the lifecycle transition does not need the Job machinery or
`certify_metric`'s actual sampling, only a certificate row that says `passed`.
"""

from __future__ import annotations

import pytest
from backend.tests.test_model_jobs import _actuary
from backend.tests.test_model_lifecycle import _principal_with

from app.db.models import ApprovalRequestRow, CustomMetricRow
from app.db.session import Database
from app.platform import approvals as approval_service
from app.platform import metrics as service
from model_schema import (
    Applicability,
    ArtifactRef,
    CertificateCheck,
    CertificateOutcome,
    CertificateResult,
    CheckStatus,
    DecisionKind,
    MetricDirection,
    MetricStatus,
    ObjectiveTemplate,
    Principal,
    SamplingSpec,
    YDomain,
    new_uuid7,
)

#: A minimal grid — `CertificateResult.sampling` is required by the shared shape, but this
#: file bypasses `certify_metric` entirely, so nothing here reads it back.
_GRID = SamplingSpec(
    n_points=1_000, y_range=(0.0, 20.0), f_range=(-5.0, 4.0), w_range=(0.01, 10.0), seed=7
)

_APPLICABILITY = Applicability(
    responses=frozenset({"claim_severity"}),
    backends=frozenset({"xgboost"}),
    offset_required=False,
    y_domain=YDomain(min_exclusive=0.0),
)


async def _metric(
    database: Database, workspace_id, actor: Principal, **over: object
) -> CustomMetricRow:
    async with database.unit_of_work() as session:
        return await service.create(
            session,
            workspace_id=workspace_id,
            actor=actor,
            slug=over.get("slug") or f"metric-{new_uuid7().hex[-6:]}",  # type: ignore[arg-type]
            template=ObjectiveTemplate.CAPPED_GAMMA,
            params={"cap": 250000},
            applicability=_APPLICABILITY,
            direction=MetricDirection.LOWER_IS_BETTER,
            description=None,
        )


async def _certified(
    database: Database, workspace_id, actor: Principal, **over: object
) -> CustomMetricRow:
    """One metric, `certified` by recording a passing certificate directly."""
    row = await _metric(database, workspace_id, actor, **over)
    passed = CertificateResult(
        overall=CertificateOutcome.CERTIFIED,
        sampling=_GRID,
        checks=(
            CertificateCheck(name="finiteness", status=CheckStatus.PASS, detail="finite"),
        ),
        library_versions={"numpy": "2.0.0"},
    )
    async with database.unit_of_work() as session:
        certified, _certificate = await service.record_certificate(
            session,
            workspace_id=workspace_id,
            actor=actor,
            metric_id=row.id,
            result=passed,
        )
    return certified


@pytest.mark.req("FR-154")
async def test_the_approval_decision_reaches_the_metric(
    database: Database, workspace_id
) -> None:
    """`certified -> review -> approved`, driven by the same decision the API takes."""
    actor = await _actuary(database, workspace_id)
    row = await _certified(database, workspace_id, actor)

    async with database.unit_of_work() as session:
        moved, request = await service.submit(
            session,
            workspace_id=workspace_id,
            actor=actor,
            metric_id=row.id,
            change_summary="certified, ready for review",
        )
        assert moved.status == MetricStatus.REVIEW.value
        request_id = request.id

    approver = await _principal_with(database, workspace_id, "approver")
    async with database.unit_of_work() as session:
        decided = await approval_service.decide(
            session,
            workspace_id=workspace_id,
            approver=approver,
            request_id=request_id,
            decision=DecisionKind.APPROVE,
            comment="direction and bounds check out",
        )
        applied = await service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=decided
        )
    assert applied is not None
    assert applied.status == MetricStatus.APPROVED.value


@pytest.mark.req("FR-154")
async def test_a_decision_about_another_artifact_type_leaves_the_metric_alone(
    database: Database, workspace_id
) -> None:
    """Mirrors `test_custom_objectives`'s sibling test — the negative half of the same
    dispatch: a request naming a different artifact type is not this function's to act on,
    and it must say so by returning `None` rather than raising or moving anything."""
    actor = await _actuary(database, workspace_id)
    request = ApprovalRequestRow(
        id=new_uuid7(),
        workspace_id=workspace_id,
        artifact_type="model",
        artifact_ref=str(ArtifactRef(type="model", slug="anything", version=1)),
        status="approved",
        submitted_by=actor.id,
        change_summary="not a metric",
        approvers_required=1,
    )
    async with database.session() as session:
        assert (
            await service.apply_approval_decision(
                session, workspace_id=workspace_id, actor=actor, request=request
            )
            is None
        )
