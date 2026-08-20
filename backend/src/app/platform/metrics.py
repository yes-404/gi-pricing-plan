"""Custom Metrics — authoring, certification, submission and blast radius.

`02` §4.13 (FR-MODEL-45, 103, 104, 105, 108). Parallel to `platform.objectives` on
purpose — FR-MODEL-45 makes a Custom Metric follow "the same lifecycle and grammar as
objectives" — and deliberately not a thin wrapper over it: a metric carries no
`hessian_strategy`/`hessian_min`, its certificate has no derivative or convexity checks
(§4.13's four are finiteness, direction_holds, scale_behaviour, smoke_evaluation), and its
certification samples a fixed internal grid rather than one a caller supplies
(`certify_metric(metric, *, seed)` — no `SamplingSpec`).

Two things worth reading before using it, matching `objectives.py`'s own two:

* **The artifact is validated by its contract before the row exists.** `create` builds a
  `CustomMetric` and lets its validators refuse — the template's own parameter ranges, an
  applicability wider than the template's, a direction an early-stopping loop cannot use.

* **Certification is a Job**, for the same reason an objective's is: §4.13's checks end in
  a smoke evaluation, and a synchronous endpoint would hold a request open across it.

**`resolve_ref` raises `METRIC_REF_UNRESOLVED`, not `NOT_FOUND`** — a deliberate departure
from `objectives.resolve_ref`. A caller resolving a reference embedded in a
`GbmSpec.eval_metrics` entry needs to tell "this reference is malformed or stale" from
"this id does not exist" at the fit path, and the two `resolve_ref`s are reached by
different callers making different decisions with the answer.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import cast, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ApprovalRequestRow,
    CustomMetricRow,
    MetricCertificateRow,
    ModelRow,
)
from app.errors import PlatformError
from app.platform import approvals, audit, rbac
from model_schema import (
    TEMPLATE_APPLICABILITY,
    VALID_METRIC_TRANSITIONS,
    Applicability,
    ApprovalStatus,
    ArtifactRef,
    CertificateOutcome,
    CertificateResult,
    CustomMetric,
    JobSource,
    MetricCertificate,
    MetricDirection,
    MetricStatus,
    ObjectiveTemplate,
    Permission,
    Principal,
    Slug,
    new_uuid7,
)

__all__ = [
    "DEFAULT_SEED",
    "apply_approval_decision",
    "certifiable_or_refuse",
    "create",
    "load_certificate",
    "load_metric",
    "record_certificate",
    "resolve_ref",
    "submit",
    "to_certificate",
    "to_metric",
    "usage",
]

#: The seed every certification uses unless a future revision names another — matching
#: `objectives.DEFAULT_SEED`'s reasoning: `certify_metric` samples a fixed internal grid
#: (`pricing_core.modelling.metrics._grid`), and two certifications of the same metric are
#: only comparable if they sampled it with the same seed.
DEFAULT_SEED = 20260818


class MetricUsageModel(BaseModel):
    """One model fitted (or early-stopped) under a Custom Metric — `usage`'s row shape.

    `model_schema` has `ObjectiveUsage`/`ObjectiveUsageModel` for the objective's blast
    radius but no metric equivalent (a metric's usage is a Task 5 addition, arriving after
    the objectives' shape was set) — defined here rather than in `model_schema`, since it
    is not a shape any other module or the frontend contract needs yet, only this service's
    `usage()` and its router.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: UUID
    model_family_slug: Slug
    version: int
    status: str
    dataset_version_id: UUID


class MetricUsage(BaseModel):
    """FR-MODEL-108's blast radius: everything fitted under this metric version."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    custom_metric_id: UUID
    slug: Slug
    version: int
    status: MetricStatus
    models: tuple[MetricUsageModel, ...] = ()


def to_metric(row: CustomMetricRow) -> CustomMetric:
    """The stored artifact, re-validated on the way out — `objectives.to_objective`'s
    reason: the definition columns are JSONB behind a trigger, not behind the contract."""
    return CustomMetric.model_validate(
        {
            "id": str(row.id),
            "slug": row.slug,
            "version": row.version,
            "kind": row.kind,
            "template": row.template,
            "params": row.params,
            "applicability": row.applicability,
            "direction": row.direction,
            "status": row.status,
            "description": row.description,
            "certificate_id": str(row.certificate_id) if row.certificate_id else None,
            "approval_request_id": (
                str(row.approval_request_id) if row.approval_request_id else None
            ),
        }
    )


def to_certificate(row: MetricCertificateRow) -> MetricCertificate:
    """The stored certificate, re-validated — including `overall` against its own checks."""
    return MetricCertificate.model_validate(
        {
            "id": str(row.id),
            "custom_metric_id": str(row.custom_metric_id),
            "metric_version": row.metric_version,
            "certified_at": row.certified_at.isoformat(),
            "job_id": str(row.job_id) if row.job_id else None,
            "result": row.payload,
        }
    )


async def create(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    template: ObjectiveTemplate,
    params: dict[str, int | float],
    applicability: Applicability | None,
    direction: MetricDirection,
    description: str | None,
) -> CustomMetricRow:
    """Create the next version of a Custom Metric, as a `draft` (FR-MODEL-45, 103).

    Versioning is by slug, exactly as an objective's is: FR-MODEL-103 makes editing a
    metric a new version requiring fresh certification, and a `GbmSpec.eval_metrics` entry
    fitted last month must still resolve `custom_metric:<slug>@<version>` to the loss it
    early-stopped under.

    `applicability` defaults to the **template's own** rather than to something
    permissive, for `objectives.create_objective`'s reason: an author may narrow it and
    may not widen it, and a default of "everything" would invert the direction the
    contract allows movement in.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_FIT,
    )
    latest = await session.scalar(
        select(CustomMetricRow.version)
        .where(
            CustomMetricRow.workspace_id == workspace_id,
            CustomMetricRow.slug == slug,
        )
        .order_by(CustomMetricRow.version.desc())
        .limit(1)
    )
    version = (latest or 0) + 1

    # The contract refuses first, so a rejected metric never reaches the table and the
    # message names the parameter rather than a constraint.
    metric = _validated(
        {
            "id": str(new_uuid7()),
            "slug": slug,
            "version": version,
            "template": template.value,
            "params": params,
            "applicability": (
                applicability.model_dump(mode="json") if applicability is not None else None
            ),
            "direction": direction.value,
            "description": description,
        },
        template=template,
    )
    row = CustomMetricRow(
        id=metric.id,
        workspace_id=workspace_id,
        slug=metric.slug,
        version=metric.version,
        status=MetricStatus.DRAFT.value,
        kind=metric.kind.value,
        template=metric.template.value if metric.template else None,
        params=dict(metric.params),
        applicability=metric.applicability.model_dump(mode="json"),
        direction=metric.direction.value,
        description=metric.description,
    )
    session.add(row)
    try:
        await session.flush()
    except IntegrityError:  # pragma: no cover — a concurrent create of the same slug
        raise PlatformError(
            "VALIDATION_FAILED",
            "That metric version already exists",
            409,
            f"{slug}@{version} was created by another request. Retry to take the next "
            "version.",
        ) from None

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="custom_metric.created",
        entity_ref=f"custom_metric:{row.slug}@{row.version}",
        after={
            "status": row.status,
            "template": row.template,
            "params": row.params,
            "direction": row.direction,
        },
    )
    return row


async def load_metric(
    session: AsyncSession, *, workspace_id: UUID, metric_id: UUID
) -> CustomMetric:
    """One metric by id."""
    return to_metric(
        await _get_or_404(session, workspace_id=workspace_id, metric_id=metric_id)
    )


async def load_certificate(
    session: AsyncSession, *, workspace_id: UUID, metric_id: UUID
) -> MetricCertificate:
    """The metric's latest certificate (§4.13), or a 404 if it has never been certified.

    The latest rather than the one `certificate_id` names, for `objectives.load_certificate`'s
    reason: a re-certification that came back `failed` clears the pointer.
    """
    await _get_or_404(session, workspace_id=workspace_id, metric_id=metric_id)
    row = (
        await session.execute(
            select(MetricCertificateRow)
            .where(
                MetricCertificateRow.workspace_id == workspace_id,
                MetricCertificateRow.custom_metric_id == metric_id,
            )
            .order_by(MetricCertificateRow.certified_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "This metric has not been certified",
            404,
            f"No certificate for metric {metric_id}. POST "
            "/api/v1/custom-metrics/{id}/certify produces one (FR-MODEL-105).",
        )
    return to_certificate(row)


async def resolve_ref(session: AsyncSession, *, workspace_id: UUID, ref: str) -> CustomMetric:
    """`custom_metric:<slug>@<version>` → the artifact, for `GbmSpec.eval_metrics` (Task 6).

    Raises **`METRIC_REF_UNRESOLVED`**, not the generic `NOT_FOUND`
    `objectives.resolve_ref` still raises — see the module docstring for why the two
    diverge.
    """
    parsed = ArtifactRef.model_validate(ref)
    row = (
        await session.execute(
            select(CustomMetricRow).where(
                CustomMetricRow.workspace_id == workspace_id,
                CustomMetricRow.slug == parsed.slug,
                CustomMetricRow.version == parsed.version,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "METRIC_REF_UNRESOLVED",
            "Custom metric not found",
            404,
            f"{ref} resolves to no custom metric in this workspace.",
        )
    return to_metric(row)


async def certifiable_or_refuse(
    session: AsyncSession, *, workspace_id: UUID, actor: Principal, metric_id: UUID
) -> CustomMetricRow:
    """Answer "may this be certified?" before a Job exists (FR-MODEL-105).

    Gated on `model:fit` rather than `model:read`, for `objectives.certifiable_or_refuse`'s
    reason: this queues a compute Job. Refused past `certified` for the same reason too —
    an objective in `review` or `approved` is one whose certificate an approver is reading
    or has already argued from.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_FIT,
    )
    row = await _get_or_404(session, workspace_id=workspace_id, metric_id=metric_id)
    status = MetricStatus(row.status)
    if status not in {MetricStatus.DRAFT, MetricStatus.CERTIFIED}:
        raise PlatformError(
            "VALIDATION_FAILED",
            "This metric cannot be certified in its current status",
            409,
            f"{row.slug}@{row.version} is {row.status}. Certification is what `certified` "
            "rests on (FR-MODEL-105), and re-running it under review or after approval "
            "would change the evidence a decision was made against. Withdraw the "
            "submission, or create the next version.",
        )
    return row


async def record_certificate(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    metric_id: UUID,
    result: CertificateResult,
    job_id: UUID | None = None,
) -> tuple[CustomMetricRow, MetricCertificateRow]:
    """Persist a certificate and move the metric's status (FR-MODEL-105).

    A `failed` certificate is **recorded and leaves the metric in `draft`**, and a
    re-certification that fails also **clears `certificate_id`** —
    `objectives.record_certificate`'s reasoning applies unchanged.
    """
    row = await _get_or_404(session, workspace_id=workspace_id, metric_id=metric_id)
    before = row.status

    certificate = MetricCertificateRow(
        id=new_uuid7(),
        workspace_id=workspace_id,
        custom_metric_id=row.id,
        metric_version=row.version,
        job_id=job_id,
        payload=result.model_dump(mode="json"),
    )
    session.add(certificate)

    failed = result.overall is CertificateOutcome.FAILED
    row.status = (MetricStatus.DRAFT if failed else MetricStatus.CERTIFIED).value
    row.certificate_id = None if failed else certificate.id
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.SYSTEM if job_id else JobSource.API,
        action="custom_metric.certified",
        entity_ref=f"custom_metric:{row.slug}@{row.version}",
        before={"status": before},
        after={
            "status": row.status,
            "certificate_id": str(certificate.id),
            "overall": result.overall.value,
            "findings": [
                f"{check.name}={check.status.value}"
                for check in result.checks
                if check.status.value != "pass"
            ],
        },
    )
    return row, certificate


async def submit(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    metric_id: UUID,
    change_summary: str,
) -> tuple[CustomMetricRow, ApprovalRequestRow]:
    """`certified → review` and the approval request it exists to create (FR-MODEL-105).

    The lifecycle-transition check runs **before** the evidence check, exactly as
    `objectives.submit_for_review`'s does: a `draft` metric is refused here with
    `VALIDATION_FAILED` at 409 without ever reaching `_require_evidence` or
    `approvals.submit` — the request is well formed and the metric is real, and what fails
    is the state it is in.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_SUBMIT,
    )
    row = await _get_or_404(session, workspace_id=workspace_id, metric_id=metric_id)
    current = MetricStatus(row.status)
    if MetricStatus.REVIEW not in VALID_METRIC_TRANSITIONS[current]:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Invalid custom metric lifecycle transition",
            409,
            f"{row.slug}@{row.version} is {row.status}; FR-MODEL-105 reaches `review` "
            "from `certified` only. Certification is the evidence the approval reads.",
        )
    await _require_evidence(session, workspace_id=workspace_id, row=row)

    request = await approvals.submit(
        session,
        workspace_id=workspace_id,
        submitter=actor,
        artifact_ref=ArtifactRef(type="custom_metric", slug=row.slug, version=row.version),
        change_summary=change_summary,
    )
    row.status = MetricStatus.REVIEW.value
    row.approval_request_id = request.id
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="custom_metric.submitted",
        entity_ref=f"custom_metric:{row.slug}@{row.version}",
        before={"status": MetricStatus.CERTIFIED.value},
        after={
            "status": MetricStatus.REVIEW.value,
            "approval_request_id": str(request.id),
        },
        justification=change_summary,
    )
    return row, request



async def apply_approval_decision(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    request: ApprovalRequestRow,
) -> CustomMetricRow | None:
    """Carry a governance decision into the metric (FR-MODEL-45, `06` FR-GOV-13).

    Mirrors `objectives.apply_approval_decision` exactly, including its reason: returns
    `None` for a request about anything else, so `_carry_to_the_artifact` drives every
    artifact type through one call; same transaction as the decision, since a metric left
    in `review` after its request reached `approved` is one no model evaluated on it may be
    approved under and no screen can explain.

    `changes_requested` returns the metric to **`certified`**, not to `draft` — `06`
    FR-GOV-13's pre-submission state for a certified artifact is `certified`, and a review
    decision does not withdraw a certificate.
    """
    if request.artifact_type != "custom_metric":
        return None

    ref = ArtifactRef.model_validate(request.artifact_ref)
    row = (
        await session.execute(
            select(CustomMetricRow)
            .where(
                CustomMetricRow.workspace_id == workspace_id,
                CustomMetricRow.slug == ref.slug,
                CustomMetricRow.version == ref.version,
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if row is None:
        # Tolerated for the reason a Model's and an objective's are: `POST
        # /approval-requests` accepts any well-formed ref, and a request naming a metric
        # that was never created must still be decidable rather than sitting open forever
        # (`06` FR-GOV-36).
        return None

    target = _target_status(ApprovalStatus(request.status))
    if target is None or MetricStatus(row.status) is target:
        # A partial approval: the policy wants another approver and nothing has moved.
        return row

    before = MetricStatus(row.status)
    if target not in VALID_METRIC_TRANSITIONS[before]:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Invalid custom metric lifecycle transition",
            409,
            f"{ref} is {before.value} and the decision would move it to {target.value}, "
            "which FR-MODEL-45 does not allow.",
        )
    row.status = target.value
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action=f"custom_metric.{target.value}",
        entity_ref=str(ref),
        before={"status": before.value},
        after={"status": target.value, "approval_request_id": str(request.id)},
    )
    return row


async def usage(
    session: AsyncSession, *, workspace_id: UUID, actor: Principal, metric_id: UUID
) -> MetricUsage:
    """FR-MODEL-108's blast radius: everything fitted (or early-stopped) under this metric.

    Asked model→metric, `objectives.usage`'s direction and reason: a Model Spec carries the
    reference, not the other way round.

    A `GbmSpec.eval_metrics` entry is a JSONB **array** of `GbmFunctionRef` objects
    (`objective` is a single top-level field; `eval_metrics` is not), so the match is `@>`
    containment against an array holding one object with this ref — unlike the objective's
    `.astext ==` on a single nested field.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_READ,
    )
    row = await _get_or_404(session, workspace_id=workspace_id, metric_id=metric_id)
    ref = f"custom_metric:{row.slug}@{row.version}"

    models = (
        (
            await session.execute(
                select(ModelRow)
                .where(
                    ModelRow.workspace_id == workspace_id,
                    ModelRow.spec["eval_metrics"].op("@>")(
                        cast([{"ref": ref}], JSONB)
                    ),
                )
                .order_by(ModelRow.model_family_slug, ModelRow.version)
            )
        )
        .scalars()
        .all()
    )
    return MetricUsage(
        custom_metric_id=row.id,
        slug=row.slug,
        version=row.version,
        status=MetricStatus(row.status),
        models=tuple(
            MetricUsageModel(
                model_id=model.id,
                model_family_slug=model.model_family_slug,
                version=model.version,
                status=model.status,
                dataset_version_id=UUID(str(model.spec["dataset_version_id"])),
            )
            for model in models
        ),
    )


# -- internals -----------------------------------------------------------------------------


def _validated(payload: dict[str, Any], *, template: ObjectiveTemplate) -> CustomMetric:
    """`CustomMetric` or a 422 that names what the template actually allows.

    The contract's validators carry the explanation — the template's parameter ranges, the
    applicability rule, FR-MODEL-104's direction — so the refusal quotes them rather than
    restating them differently.
    """
    if payload.get("applicability") is None:
        payload["applicability"] = TEMPLATE_APPLICABILITY[template].model_dump(mode="json")
    try:
        return CustomMetric.model_validate(payload)
    except ValueError as exc:
        raise PlatformError(
            "VALIDATION_FAILED",
            "This custom metric is not valid",
            422,
            f"{exc}",
        ) from exc


async def _get_or_404(
    session: AsyncSession, *, workspace_id: UUID, metric_id: UUID
) -> CustomMetricRow:
    row = await session.get(CustomMetricRow, metric_id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND",
            "Custom metric not found",
            404,
            f"No custom metric {metric_id} in this workspace.",
        )
    return row


async def _require_evidence(
    session: AsyncSession, *, workspace_id: UUID, row: CustomMetricRow
) -> None:
    """`06` R4 and FR-GOV-10 for this artifact type, failing closed on what it cannot check.

    `objectives._require_evidence` carries the reasoning; the shape is the same and the
    difference is only which kinds are verifiable here. The workspace policy names
    `metric_certificate` for `custom_metric`, the way it names `objective_certificate` for
    `custom_objective` (`model_schema.approvals.DEFAULT_POLICY`).

    **A known gap, stated rather than asserted away.** `custom_metric` has no
    `EVIDENCE_FLOOR` entry, because `06` §3.3 has no row for it — so `below_floor()`
    returns nothing for this artifact type and a workspace that edits `metric_certificate`
    out of its policy is *accepted*, leaving this function with nothing to require.
    `custom_objective` is in the floor and is protected; this is not. Until 2026-08-20 this
    docstring claimed the opposite — that such an edit "will 422 here with
    `EVIDENCE_INCOMPLETE`" — which was never true of any build.

    What actually protects a metric today is the **lifecycle**, not the policy: submission
    requires status `certified`, only `record_certificate` sets that status, it sets it
    alongside a `certificate_id`, and the `certified_metric_has_a_certificate` CHECK
    refuses the pair coming apart at a layer a direct `UPDATE` cannot walk past. So an
    uncertified metric cannot be
    submitted even under an emptied policy — but the policy reader is being told a floor
    exists where none does, which is the failure mode `POLICY_BELOW_EVIDENCE_FLOOR` was
    added to prevent.

    Owed: a `06` §3.3 evidence row for `custom_metric` and the matching `EVIDENCE_FLOOR`
    entry. Adding the entry alone would put the code above its own specification, so it is
    a governance change rather than part of this fix wave. Recorded in `docs/roadmap.md`'s
    custom-metrics slice record under "Not delivered", with an owner.
    """
    policy = await approvals.policy_for(session, workspace_id)

    verifiable = {"metric_certificate": row.certificate_id is not None}
    missing = [
        kind
        for kind in policy.effective_evidence("custom_metric")
        if not verifiable.get(kind, False)
    ]
    if missing:
        unknown = [kind for kind in missing if kind not in verifiable]
        detail = (
            f"{row.slug}@{row.version} is missing required evidence: {', '.join(missing)}. "
            "`06` FR-GOV-19 defines it per artifact type and R4 makes it a condition of "
            "submission. FR-MODEL-105: certification is what an approver reads."
        )
        if unknown:
            detail += (
                f" This build cannot verify {', '.join(unknown)} — treating an uncheckable "
                "requirement as met would make a policy tightening do nothing."
            )
        raise PlatformError("EVIDENCE_INCOMPLETE", "Required evidence is missing", 422, detail)


def _target_status(request_status: ApprovalStatus) -> MetricStatus | None:
    """What a request's status means for the metric behind it.

    Mirrors `objectives._target_status` exactly, including its reason: the three
    non-approvals return the metric to **`certified`** rather than to `draft`, the same
    amendment `06` FR-GOV-13 carries for a Model and for an objective — `draft` is the
    pre-submission state, and for a certified metric that is `certified`. Sending it to
    `draft` would say the certificate had been withdrawn, which no review decision does.
    """
    return {
        ApprovalStatus.APPROVED: MetricStatus.APPROVED,
        ApprovalStatus.CHANGES_REQUESTED: MetricStatus.CERTIFIED,
        ApprovalStatus.REJECTED: MetricStatus.CERTIFIED,
        ApprovalStatus.WITHDRAWN: MetricStatus.CERTIFIED,
    }.get(request_status)
