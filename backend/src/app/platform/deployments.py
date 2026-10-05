"""The Deployment and the Deployment Request (`03` §4.12, FR-267; WK-674 Slice 2, `PL-1392` Task 5).

A **Deployment** binds one `approved`, compiled Rating Version to one Environment. A target
with a `deployment` entry in the Approval Policy (`prod` by default) is **gated**: it is
deployed only by naming an **approved Deployment Request**, the artifact this module owns
(`RL-1301` A.1). Submission writes the request, its pinned evidence and its approval request
in one transaction; `apply_approval_decision` is the only writer of `approved` (`RL-1301` A.4;
the database's approval guard refuses any other).

`platform/approvals.py` imports nothing from here (DEP-1, Acceptance 5): `06` receives the
facts it needs through arguments and through `app.api.approvals`' fan-out.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.pagination import COUNT_CAP, Page, decode_cursor, encode_cursor
from app.db.models import (
    ApprovalRequestRow,
    DeploymentRequestRow,
    DeploymentRow,
    EnvironmentRow,
    RatingVersionRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals, audit, environments, rbac
from model_schema import (
    ApprovalStatus,
    ArtifactRef,
    Deployment,
    DeploymentCreate,
    DeploymentRequest,
    DeploymentRequestCreate,
    DeploymentRequestEvidence,
    DeploymentRequestStatus,
    JobSource,
    Permission,
    Principal,
    PromotionSkip,
    ScopeType,
    promotion_order_refusal,
)

__all__ = [
    "apply_approval_decision",
    "deploy",
    "list_deployments",
    "resolve_artifact_ref",
    "submit_request",
]

_CREATED = "deployment_request.created"


# -- shared checks ------------------------------------------------------------------------


def _require_rating_version(ref: ArtifactRef, *, what: str) -> None:
    """G3: a Rating Version is the only deployable subject, refused before any row is read."""
    if ref.type != "rating_version":
        raise PlatformError(
            "VALIDATION_FAILED",
            "Only a Rating Version can be deployed",
            422,
            f"{what} names a {ref.type!r} ({ref}). A Rating Version is the only deployable "
            "subject (`03` §4.12); a Sub-graph reaches a deployment only inside the Rating "
            "Version that pins it.",
        )


async def _authorised_environment(
    session: AsyncSession, *, workspace_id: UUID, actor: Principal, slug: str, lock: bool = False
) -> EnvironmentRow:
    """The target Environment, after `deployment:promote` with it as the resource and after
    the retired check (`RL-1301` B.2; `RL-1401` item 3: after the permission, before the
    Rating Version is read). An unknown slug is 404 (`RL-1401` T3)."""
    env = await environments._load(session, slug, lock=lock)
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.DEPLOYMENT_PROMOTE,
        resource=rbac.ResourceRef(scope_type=ScopeType.ENVIRONMENT, scope_id=env.id),
    )
    environments._require_not_retired(env, "deployed to")
    return env


async def _approved_compiled_version(
    session: AsyncSession, *, workspace_id: UUID, ref: ArtifactRef
) -> tuple[RatingVersionRow, str]:
    """The `approved` Rating Version `ref` names and its Bundle hash (FR-238, FR-239).

    **Compiled only** (`RL-1401` item 2): a version whose `bundle` metadata is absent or has no
    `content_hash` has no hash to record. It is refused after the `approved` check, so a draft
    reports its status first.
    """
    row = (
        await session.execute(
            select(RatingVersionRow).where(
                RatingVersionRow.workspace_id == workspace_id,
                RatingVersionRow.slug == ref.slug,
                RatingVersionRow.version == ref.version,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND", "Rating version not found", 404, f"No rating version {ref}."
        )
    if row.status != "approved":
        raise PlatformError(
            "VALIDATION_FAILED",
            "Only an approved Rating Version can be deployed",
            409,
            f"{ref} is {row.status}; only an `approved` version deploys (FR-238, FR-267).",
        )
    content_hash = (row.bundle or {}).get("content_hash")
    if not content_hash:
        raise PlatformError(
            "BUNDLE_COMPILE_FAILED",
            "The Rating Version has no compiled Bundle",
            409,
            f"{ref} has no `content_hash`, so there is no Bundle hash to record (FR-239; "
            "`RL-1401`). It cannot be compiled once it has left `draft` (`RL-1379`): the way "
            "forward is a new draft version.",
        )
    return row, str(content_hash)


async def _predecessor_deployment(
    session: AsyncSession, *, workspace_id: UUID, env: EnvironmentRow, ref: ArtifactRef
) -> tuple[str | None, DeploymentRow | None]:
    """The predecessor's slug and the latest Deployment of `ref` in it, if any (FR-429)."""
    predecessor = env.requires_prior_environment
    if predecessor is None:
        return None, None
    found = (
        await session.execute(
            select(DeploymentRow)
            .join(EnvironmentRow, EnvironmentRow.id == DeploymentRow.environment_id)
            .where(
                DeploymentRow.workspace_id == workspace_id,
                EnvironmentRow.slug == predecessor,
                DeploymentRow.rating_version_ref == str(ref),
            )
            .order_by(DeploymentRow.deployed_at.desc(), DeploymentRow.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    return predecessor, found


def _to_request(row: DeploymentRequestRow) -> DeploymentRequest:
    return DeploymentRequest(
        id=row.id,
        workspace_id=row.workspace_id,
        ref=_request_ref(row),
        environment=row.slug,
        rating_version_ref=ArtifactRef.parse(row.rating_version_ref),
        change_summary=row.change_summary,
        status=DeploymentRequestStatus(row.status),
        approval_request_id=row.approval_request_id,
        evidence=DeploymentRequestEvidence.model_validate(row.evidence),
        submitted_by=row.submitted_by,
        created_at=row.created_at,
    )


def _request_ref(row: DeploymentRequestRow) -> ArtifactRef:
    return ArtifactRef(type="deployment", slug=row.slug, version=row.version)


def _to_deployment(
    row: DeploymentRow, env_slug: str, request_ref: ArtifactRef | None
) -> Deployment:
    return Deployment(
        id=row.id,
        workspace_id=row.workspace_id,
        environment=env_slug,
        rating_version_ref=ArtifactRef.parse(row.rating_version_ref),
        bundle_hash=row.bundle_hash,
        deployed_by=row.deployed_by,
        deployed_at=row.deployed_at,
        reason=row.reason,
        deployment_request_ref=request_ref,
    )


def _missing_floor(evidence: dict[str, Any]) -> list[str]:
    """The `deployment` evidence-floor items a row's `evidence` does not hold (FR-364)."""
    from model_schema import EVIDENCE_FLOOR

    return [item for item in EVIDENCE_FLOOR["deployment"] if not evidence.get(item)]


# -- the Deployment Request ---------------------------------------------------------------


async def submit_request(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    environment: str,
    body: DeploymentRequestCreate,
) -> DeploymentRequest:
    """Write a Deployment Request with its evidence **once**, and submit it (`RL-1301` A).

    Order: G3, the Environment and `deployment:promote`, the retired check, the Rating Version
    (`approved`, then compiled), the policy entry, then the two evidence items. The row, its
    approval request and the `deployment_request.created` Audit Event share one transaction;
    that event's actor is the request's Author for `06` FR-353 (`RL-1401` item 1).
    """
    _require_rating_version(body.rating_version_ref, what="A deployment request")
    # Locked: the version is numbered per Environment, so two submissions into one
    # Environment serialise rather than racing for the same `@n`.
    env = await _authorised_environment(
        session, workspace_id=workspace_id, actor=actor, slug=environment, lock=True
    )
    ref = body.rating_version_ref
    await _approved_compiled_version(session, workspace_id=workspace_id, ref=ref)

    policy = await approvals.policy_for(session, workspace_id)
    entry = policy.entry_for("deployment", env.slug)
    if entry is None:
        raise PlatformError(
            "VALIDATION_FAILED",
            "No approval policy for this artifact type",
            422,
            f"The workspace policy has no `deployment` entry for {env.slug!r}, so it is not a "
            "gated target and takes no Deployment Request (`RL-1301` A.5). Deploy to it "
            "directly.",
        )

    approval = (
        await session.execute(
            select(ApprovalRequestRow)
            .where(
                ApprovalRequestRow.workspace_id == workspace_id,
                ApprovalRequestRow.artifact_ref == str(ref),
                ApprovalRequestRow.status == ApprovalStatus.APPROVED.value,
            )
            .order_by(ApprovalRequestRow.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    predecessor, deployed = await _predecessor_deployment(
        session, workspace_id=workspace_id, env=env, ref=ref
    )
    reason = promotion_order_refusal(
        entry,
        target=env.slug,
        predecessor=predecessor,
        predecessor_deployed=deployed is not None,
        skip=body.skip,
    )
    pinned: UUID | PromotionSkip | None = (
        deployed.id if deployed is not None else body.skip if predecessor is not None else None
    )
    if reason is not None or approval is None or pinned is None:
        raise PlatformError(
            "EVIDENCE_INCOMPLETE",
            "The deployment request's evidence is incomplete",
            422,
            reason
            or (
                f"{ref} has no decided approval request."
                if approval is None
                else f"{env.slug!r} has no predecessor Environment to pin a deployment or a "
                "skip of, so every request into it is refused. Remove the `deployment` policy "
                f"entry for {env.slug!r} to make it an ungated target "
                "(`requires_prior_environment` cannot be changed after creation)."
            ),
        )
    evidence = DeploymentRequestEvidence(rating_version_approval=approval.id, uat_deployment=pinned)

    number = (
        await session.execute(
            select(func.coalesce(func.max(DeploymentRequestRow.version), 0)).where(
                DeploymentRequestRow.workspace_id == workspace_id,
                DeploymentRequestRow.slug == env.slug,
            )
        )
    ).scalar_one() + 1
    request_ref = ArtifactRef(type="deployment", slug=env.slug, version=number)
    row = DeploymentRequestRow(
        workspace_id=workspace_id,
        slug=env.slug,
        version=number,
        environment_id=env.id,
        rating_version_ref=str(ref),
        status=DeploymentRequestStatus.REVIEW.value,
        evidence=evidence.model_dump(mode="json"),
        change_summary=body.change_summary,
        submitted_by=actor.id,
    )
    session.add(row)
    await session.flush()
    submitted = await approvals.submit(
        session,
        workspace_id=workspace_id,
        submitter=actor,
        artifact_ref=request_ref,
        change_summary=body.change_summary,
        environment=env.slug,
    )
    row.approval_request_id = submitted.id
    await session.flush()
    await session.refresh(row)
    model = _to_request(row)
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action=_CREATED,
        entity_ref=str(request_ref),
        before=None,
        after=model.model_dump(mode="json"),
    )
    return model


async def resolve_artifact_ref(
    session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
) -> bool:
    """The generic `POST /approval-requests`' resolver for a `deployment` reference.

    `False` for another type, as its siblings do. For a `deployment` reference it accepts
    **only** a Deployment Request row in `review` whose evidence holds both floor items, and
    refuses every other (`PL-1392` Task 5 step 6; `RL-1301` audit advisory A2): the generic
    route cannot become a way around this module's submission.
    """
    if artifact_ref.type != "deployment":
        return False
    row = (
        await session.execute(
            select(DeploymentRequestRow).where(
                DeploymentRequestRow.workspace_id == workspace_id,
                DeploymentRequestRow.slug == artifact_ref.slug,
                DeploymentRequestRow.version == artifact_ref.version,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "Deployment request not found",
            404,
            f"No Deployment Request {artifact_ref}. One is created only by "
            "`POST /api/v1/environments/{env}/deployment-requests`.",
        )
    approvals.require_in_review(artifact_ref, row.status)
    _require_floor(row)
    return True


def _require_floor(row: DeploymentRequestRow) -> None:
    missing = _missing_floor(row.evidence)
    if missing:
        raise PlatformError(
            "EVIDENCE_INCOMPLETE",
            "The deployment request's evidence is incomplete",
            422,
            f"{_request_ref(row)} lacks {', '.join(missing)}: no deployment request is "
            "approvable without its pinned evidence (`RL-1301` A.4).",
        )


async def apply_approval_decision(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    request: ApprovalRequestRow,
) -> DeploymentRequestRow | None:
    """Carry a governance decision into the Deployment Request; `None` for any other type.

    The **only** writer of `approved` on `deployment_requests` (Acceptance 13). The row is
    loaded locked and must be in `review` (`06` FR-351; auditor-plans F4), and an `approved`
    outcome is refused for a row whose evidence lacks a floor item.
    """
    if request.artifact_type != "deployment":
        return None
    ref = ArtifactRef.parse(request.artifact_ref)
    row = (
        await session.execute(
            select(DeploymentRequestRow)
            .where(
                DeploymentRequestRow.workspace_id == workspace_id,
                DeploymentRequestRow.slug == ref.slug,
                DeploymentRequestRow.version == ref.version,
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if row is None:
        return None
    target = {
        ApprovalStatus.APPROVED: DeploymentRequestStatus.APPROVED,
        # A request has no draft to return to and no resubmission route: a request for
        # changes ends it as `rejected`, and a new request is submitted.
        ApprovalStatus.CHANGES_REQUESTED: DeploymentRequestStatus.REJECTED,
        ApprovalStatus.REJECTED: DeploymentRequestStatus.REJECTED,
        ApprovalStatus.WITHDRAWN: DeploymentRequestStatus.WITHDRAWN,
    }.get(ApprovalStatus(request.status))
    if target is None:
        return row
    approvals.require_in_review(ref, row.status)
    if target is DeploymentRequestStatus.APPROVED:
        _require_floor(row)
    before = row.status
    row.status = target.value
    await session.flush()
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action=f"deployment_request.{target.value}",
        entity_ref=str(ref),
        before={"status": before},
        after={"status": target.value},
    )
    return row


# -- the Deployment -----------------------------------------------------------------------


async def deploy(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    environment: str,
    body: DeploymentCreate,
) -> Deployment:
    """Bind an `approved`, compiled Rating Version to an Environment (FR-267, FR-272).

    A gated target needs an **approved** Deployment Request, executed exactly once by a
    conditional `UPDATE`; FR-429's predicate is re-evaluated from the request's **pinned**
    evidence. An ungated target has no request and the predicate reads the predecessor's
    Deployment directly, with no skip possible (`RL-1301` A.5).
    """
    ref = body.rating_version_ref
    _require_rating_version(ref, what="A deploy")
    env = await _authorised_environment(
        session, workspace_id=workspace_id, actor=actor, slug=environment
    )
    _, bundle_hash = await _approved_compiled_version(session, workspace_id=workspace_id, ref=ref)

    entry = (await approvals.policy_for(session, workspace_id)).entry_for("deployment", env.slug)
    predecessor, deployed = await _predecessor_deployment(
        session, workspace_id=workspace_id, env=env, ref=ref
    )
    request_row: DeploymentRequestRow | None = None
    if entry is None:
        if body.deployment_request_ref is not None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "No deployment request applies to this Environment",
                422,
                f"{env.slug!r} has no `deployment` policy entry, so it takes no Deployment "
                f"Request and {body.deployment_request_ref} was named for nothing.",
            )
        reason = promotion_order_refusal(
            None,
            target=env.slug,
            predecessor=predecessor,
            predecessor_deployed=deployed is not None,
            skip=None,
        )
    else:
        request_row = await _executable_request(
            session, workspace_id=workspace_id, env=env, ref=ref, named=body.deployment_request_ref
        )
        pinned = DeploymentRequestEvidence.model_validate(request_row.evidence).uat_deployment
        reason = promotion_order_refusal(
            entry,
            target=env.slug,
            predecessor=predecessor,
            predecessor_deployed=isinstance(pinned, UUID),
            skip=pinned if isinstance(pinned, PromotionSkip) else None,
        )
    if reason is not None:
        raise PlatformError(
            "PROMOTION_ORDER_VIOLATION", "The promotion order is not satisfied", 409, reason
        )
    if request_row is not None:
        executed = (
            await session.execute(
                update(DeploymentRequestRow)
                .where(
                    DeploymentRequestRow.id == request_row.id,
                    DeploymentRequestRow.status == DeploymentRequestStatus.APPROVED.value,
                )
                .values(status=DeploymentRequestStatus.EXECUTED.value)
                .returning(DeploymentRequestRow.id)
            )
        ).scalar_one_or_none()
        if executed is None:
            raise _not_approved(body.deployment_request_ref, "has been executed")

    previous = (
        await session.execute(
            select(DeploymentRow)
            .where(
                DeploymentRow.workspace_id == workspace_id,
                DeploymentRow.environment_id == env.id,
            )
            .order_by(DeploymentRow.deployed_at.desc(), DeploymentRow.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    request_ref = None if request_row is None else _request_ref(request_row)
    row = DeploymentRow(
        workspace_id=workspace_id,
        environment_id=env.id,
        rating_version_ref=str(ref),
        bundle_hash=bundle_hash,
        deployed_by=actor.id,
        reason=body.reason,
        deployment_request_id=None if request_row is None else request_row.id,
    )
    session.add(row)
    await session.flush()
    await session.refresh(row)
    model = _to_deployment(row, env.slug, request_ref)
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="deployment.created",
        entity_ref=f"environment:{env.slug}",
        before=None
        if previous is None
        else _to_deployment(
            previous,
            env.slug,
            await _request_ref_of(session, previous.deployment_request_id),
        ).model_dump(mode="json"),
        after=model.model_dump(mode="json"),
        justification=body.reason,
    )
    return model


def _not_approved(named: ArtifactRef | None, why: str) -> PlatformError:
    return PlatformError(
        "DEPLOY_REQUIRES_APPROVAL",
        "This deploy needs an approved Deployment Request",
        409,
        f"The target is gated by an approval policy entry, and the request {named} is not "
        f"approved, or {why} (FR-267, `RL-1301` A.5).",
    )


async def _request_ref_of(session: AsyncSession, request_id: UUID | None) -> ArtifactRef | None:
    if request_id is None:
        return None
    row = await session.get(DeploymentRequestRow, request_id)
    return None if row is None else _request_ref(row)


async def _executable_request(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    env: EnvironmentRow,
    ref: ArtifactRef,
    named: ArtifactRef | None,
) -> DeploymentRequestRow:
    """The `approved` Deployment Request for this version and this Environment (A.5)."""
    if named is None:
        raise _not_approved(None, "none was named")
    if named.type != "deployment":
        raise PlatformError(
            "VALIDATION_FAILED",
            "Not a Deployment Request reference",
            422,
            f"`deployment_request_ref` names a {named.type!r} ({named}).",
        )
    row = (
        await session.execute(
            select(DeploymentRequestRow).where(
                DeploymentRequestRow.workspace_id == workspace_id,
                DeploymentRequestRow.slug == named.slug,
                DeploymentRequestRow.version == named.version,
            )
        )
    ).scalar_one_or_none()
    if (
        row is None
        or row.environment_id != env.id
        or row.rating_version_ref != str(ref)
        or row.status != DeploymentRequestStatus.APPROVED.value
    ):
        raise _not_approved(named, "names another Environment or Rating Version")
    return row


async def list_deployments(
    database: Database,
    *,
    workspace_id: UUID,
    environment: str,
    cursor: str | None,
    limit: int,
) -> Page[Deployment]:
    """The Environment's Deployment history, newest first (FR-267; `06` FR-382)."""
    after = decode_cursor(cursor)
    async with database.session() as session:
        env = await environments._load(session, environment)
        conditions = [
            DeploymentRow.workspace_id == workspace_id,
            DeploymentRow.environment_id == env.id,
        ]
        total = len(
            (
                await session.scalars(select(DeploymentRow.id).where(*conditions).limit(COUNT_CAP))
            ).all()
        )
        query = select(DeploymentRow).where(*conditions).order_by(DeploymentRow.id.desc())
        if after is not None:
            query = query.where(DeploymentRow.id < after)
        rows = list((await session.scalars(query.limit(limit + 1))).all())
        page = rows[:limit]
        refs = {r.id: await _request_ref_of(session, r.deployment_request_id) for r in page}
    return Page[Deployment](
        items=[_to_deployment(r, env.slug, refs[r.id]) for r in page],
        next_cursor=encode_cursor(page[-1].id) if len(rows) > limit else None,
        total_estimate=total,
    )
