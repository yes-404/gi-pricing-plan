"""The approval API (`06` §5.1).

| Method | Path |
|---|---|
| `POST` | `/api/v1/approval-requests` — submit an artifact |
| `GET` | `/api/v1/approval-requests` — list, filtered, cursor-paginated |
| `GET` | `/api/v1/approval-requests/{id}` — one request with its decisions |
| `POST` | `/api/v1/approval-requests/{id}/decide` — approve / reject / request changes |
| `POST` | `/api/v1/approval-requests/{id}/withdraw` |
| `GET`/`PUT` | `/api/v1/approval-policy` |

**FR-358's Approvals inbox is not this.** The list endpoint supports its query
(`?status=review`), but the requirement is about *evidence inline* — diffs, diagnostics,
dislocation, GIPP — and none of those artifacts exist before WK-660 and WK-661. Shipping a list and
calling it the inbox would claim the requirement while delivering the part that was easy.
"""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authz import requires
from app.api.deps import Caller, require_caller
from app.api.pagination import (
    COUNT_CAP,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    Page,
    decode_cursor,
    encode_cursor,
)
from app.api.responses import problems
from app.db.models import ApprovalDecisionRow, ApprovalRequestRow, DeploymentRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as service
from app.platform import datasets as datasets_service
from app.platform import deployments as deployments_service
from app.platform import metrics as metrics_service
from app.platform import modelling as modelling_service
from app.platform import objectives as objectives_service
from app.platform import perils as perils_service
from app.platform import rating_versions as rating_versions_service
from app.platform import validation_rules as validation_rules_service
from model_schema import (
    ApprovalPolicy,
    ApprovalRequest,
    ApprovalStatus,
    ApprovalSubmission,
    ApprovalWithdrawal,
    ArtifactRef,
    Decide,
    DecisionKind,
    Permission,
)

__all__ = ["decide_and_carry", "router"]

router = APIRouter(tags=["governance"])

AnyCaller = Annotated[Caller, Depends(require_caller)]
Decider = Annotated[Caller, Depends(requires(Permission.APPROVAL_DECIDE))]
PolicyAdmin = Annotated[Caller, Depends(requires(Permission.ADMIN_MANAGE_ROLES))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


async def _detail(database: Database, row: ApprovalRequestRow) -> ApprovalRequest:
    async with database.session() as session:
        decisions = list(
            (
                await session.execute(
                    select(ApprovalDecisionRow)
                    .where(ApprovalDecisionRow.request_id == row.id)
                    .order_by(ApprovalDecisionRow.at)
                )
            ).scalars()
        )
    return service.to_approval_request(row, decisions)


@router.post(
    "/approval-requests",
    status_code=status.HTTP_201_CREATED,
    summary="Submit an artifact for approval",
    responses=problems(401, 403, 404, 409, 422),
)
async def submit_for_approval(
    body: ApprovalSubmission, caller: AnyCaller, database: DatabaseDep
) -> ApprovalRequest:
    """Anyone authenticated may submit; the policy decides who may approve.

    Deliberately not permission-gated beyond authentication: submitting is asking, and the
    module that owns the artifact has already decided whether this principal could create
    it. Gating the ask as well would mean an analyst who built a model could not put it
    forward.

    The `404` this route now declares is FR-386's: the reference is the pin, and a
    reference to a version that was never created pins nothing. `_resolve_the_artifact` is
    what makes that refusal, and `service.submit` is what sequences it.
    """
    try:
        ref = ArtifactRef.model_validate(body.artifact_ref)
    except ValueError as exc:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Malformed artifact reference",
            422,
            f"{body.artifact_ref!r} is not a canonical {{type}}:{{slug}}@{{version}} "
            "reference (ID-3).",
        ) from exc

    async with database.unit_of_work() as session:
        row = await service.submit(
            session,
            workspace_id=caller.workspace_id,
            submitter=caller.principal,
            artifact_ref=ref,
            change_summary=body.change_summary,
            environment=body.environment,
            resolve=_resolve_the_artifact,
        )
        return service.to_approval_request(row, [])


@router.get(
    "/approval-requests",
    summary="List approval requests",
    responses=problems(400, 401, 403, 422),
)
async def list_requests(
    caller: AnyCaller,
    database: DatabaseDep,
    status_filter: Annotated[ApprovalStatus | None, Query(alias="status")] = None,
    artifact_type: str | None = None,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
) -> Page[ApprovalRequest]:
    conditions: list[Any] = [ApprovalRequestRow.workspace_id == caller.workspace_id]
    if status_filter is not None:
        conditions.append(ApprovalRequestRow.status == status_filter.value)
    if artifact_type is not None:
        conditions.append(ApprovalRequestRow.artifact_type == artifact_type)

    after = decode_cursor(cursor)
    query = (
        select(ApprovalRequestRow)
        .where(*conditions)
        .order_by(ApprovalRequestRow.id.desc())
        .limit(limit + 1)
    )
    if after is not None:
        query = query.where(ApprovalRequestRow.id < after)

    async with database.session() as session:
        rows = list((await session.execute(query)).scalars())
        total = (
            await session.execute(
                select(func.count()).select_from(
                    select(ApprovalRequestRow.id)
                    .where(*conditions)
                    .limit(COUNT_CAP)
                    .subquery()
                )
            )
        ).scalar_one()

    has_more = len(rows) > limit
    page_rows = rows[:limit]
    return Page[ApprovalRequest](
        items=[await _detail(database, row) for row in page_rows],
        next_cursor=encode_cursor(page_rows[-1].id) if has_more and page_rows else None,
        total_estimate=total,
    )


@router.get(
    "/approval-requests/{request_id}",
    summary="One request with its decisions",
    responses=problems(401, 403, 404, 422),
)
async def get_request(
    request_id: UUID, caller: AnyCaller, database: DatabaseDep
) -> ApprovalRequest:
    async with database.session() as session:
        row = await session.get(ApprovalRequestRow, request_id)
    if row is None or row.workspace_id != caller.workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Approval request not found", 404, f"No request {request_id}."
        )
    return await _detail(database, row)


@router.post(
    "/approval-requests/{request_id}/decide",
    summary="Approve, reject or request changes",
    responses=problems(401, 403, 404, 409, 422),
)
async def decide_request(
    request_id: UUID, body: Decide, caller: Decider, database: DatabaseDep
) -> ApprovalRequest:
    """The decision, and the artifact transition it implies, in **one** transaction.

    `06` FR-351 stops the approval machine at `approved` — "post-approval states belong to
    the owning module" — so something has to carry the decision across, and the direction
    settles where. `MODEL` depends on `GOV` and never the reverse (DEP-1), so a hook inside
    `approvals.decide` calling back into modelling is the one design that is not available.
    This route holds both and is above both, which is the same seam `withdraw` uses for
    `artifact_is_live`.

    One transaction is not a tidiness preference: a model left in `review` after its request
    reached `approved` is a model no Rating Version may reference and no screen can explain,
    and two transactions is all it takes to produce one. It also makes FR-205's block
    work — the flag refusal rolls the decision back with it, so an approver is told the
    model is flagged rather than finding their approval recorded against nothing.
    """
    async with database.unit_of_work() as session:
        row = await decide_and_carry(
            session,
            caller=caller,
            request_id=request_id,
            decision=body.decision,
            comment=body.comment,
        )
        decisions = list(
            (
                await session.execute(
                    select(ApprovalDecisionRow)
                    .where(ApprovalDecisionRow.request_id == row.id)
                    .order_by(ApprovalDecisionRow.at)
                )
            ).scalars()
        )
        return service.to_approval_request(row, decisions)


async def decide_and_carry(
    session: Any,
    *,
    caller: Caller,
    request_id: UUID,
    decision: DecisionKind,
    comment: str | None,
) -> ApprovalRequestRow:
    """Record the decision and carry it into the artifact, in the caller's transaction.

    The one place a decision becomes an artifact transition: the decide route and the
    validation-rule approve route (a client of this path, FD-1356, DP-1 (b)) both call it,
    so a rule is approved by exactly the checks a model is, and by nothing else.
    """
    row = await service.decide(
        session,
        workspace_id=caller.workspace_id,
        request_id=request_id,
        approver=caller.principal,
        decision=decision,
        comment=comment,
        evidence_authors=rating_versions_service.golden_quote_delta_authors,
    )
    await _carry_to_the_artifact(session, caller=caller, request=row)
    return row


async def _is_deployed(session: AsyncSession, workspace_id: UUID, request_id: UUID) -> bool:
    """Whether the request's artifact is a Rating Version with at least one Deployment.

    An unknown request is not live: `service.withdraw` answers it 404 itself.
    """
    row = (
        await session.execute(
            select(ApprovalRequestRow.artifact_type, ApprovalRequestRow.artifact_ref).where(
                ApprovalRequestRow.id == request_id,
                ApprovalRequestRow.workspace_id == workspace_id,
            )
        )
    ).one_or_none()
    if row is None or row.artifact_type != "rating_version":
        return False
    deployment = await session.scalar(
        select(DeploymentRow.id)
        .where(
            DeploymentRow.workspace_id == workspace_id,
            DeploymentRow.rating_version_ref == row.artifact_ref,
        )
        .limit(1)
    )
    return deployment is not None


@router.post(
    "/approval-requests/{request_id}/withdraw",
    summary="Withdraw before deployment (FR-357)",
    responses=problems(401, 403, 404, 409, 422),
)
async def withdraw_request(
    request_id: UUID, body: ApprovalWithdrawal, caller: Decider, database: DatabaseDep
) -> ApprovalRequest:
    """Withdraw a request before its artifact is deployed (FR-357).

    Liveness is the server's to derive, never the client's to assert (`PL-1392` Task 6): a
    Rating Version with a Deployment row is live, and the request is refused 409
    `WITHDRAW_AFTER_DEPLOY_FORBIDDEN`. Governance owns the rule (`service.withdraw`); the
    deployment state is `03`'s fact, read here from its rows.
    """
    async with database.unit_of_work() as session:
        artifact_is_live = await _is_deployed(session, caller.workspace_id, request_id)
        row = await service.withdraw(
            session,
            workspace_id=caller.workspace_id,
            request_id=request_id,
            actor=caller.principal,
            reason=body.reason,
            artifact_is_live=artifact_is_live,
        )
        # A withdrawn request leaves the artifact where a rejected one does: back in its
        # pre-submission state. Without this the model would sit in `review` for ever with
        # no open request behind it — reviewable by nobody and resubmittable by nobody.
        await _carry_to_the_artifact(session, caller=caller, request=row)
        return service.to_approval_request(row, [])


@router.get(
    "/approval-policy",
    summary="The workspace approval policy",
    responses=problems(401, 403),
)
async def get_policy(caller: AnyCaller, database: DatabaseDep) -> ApprovalPolicy:
    async with database.session() as session:
        return await service.policy_for(session, caller.workspace_id)


@router.put(
    "/approval-policy",
    summary="Replace the workspace approval policy",
    responses=problems(401, 403, 422),
)
async def put_policy(
    body: ApprovalPolicy, caller: PolicyAdmin, database: DatabaseDep
) -> ApprovalPolicy:
    async with database.unit_of_work() as session:
        return await service.set_policy(
            session, workspace_id=caller.workspace_id, actor=caller.principal, policy=body
        )


async def _resolve_model(
    session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
) -> bool:
    """`02`'s own by-slug-and-version read, adapted to the fan-out's contract.

    TODO(main-thread): this belongs in `platform.modelling` as `resolve_artifact_ref`,
    beside `perils`', `validation_rules`' and `datasets`'. It sits here only because this
    slice was not given that file to edit; moving it changes no behaviour and deletes this
    adapter.
    """
    if artifact_ref.type != "model":
        return False
    row = await modelling_service.load_model(
        session,
        workspace_id=workspace_id,
        slug=artifact_ref.slug,
        version=artifact_ref.version,
    )
    service.require_in_review(artifact_ref, row.status)
    return True


async def _resolve_custom_objective(
    session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
) -> bool:
    """`objectives.resolve_ref`, adapted to the fan-out's contract.

    TODO(main-thread): as `_resolve_model` — `platform.objectives` should carry a
    `resolve_artifact_ref` that returns `False` for a reference that is not its own, and
    this adapter should go.
    """
    if artifact_ref.type != "custom_objective":
        return False
    objective = await objectives_service.resolve_ref(
        session, workspace_id=workspace_id, ref=str(artifact_ref)
    )
    service.require_in_review(artifact_ref, objective.status.value)
    return True


async def _resolve_custom_metric(
    session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
) -> bool:
    """`metrics.resolve_ref`, adapted — and its error code translated.

    `metrics.resolve_ref` raises **`METRIC_REF_UNRESOLVED`** where its sibling
    `objectives.resolve_ref` raises `NOT_FOUND`, deliberately: `02` §4.13's caller resolves
    a reference embedded in a `GbmSpec.eval_metrics` entry and needs to tell a stale
    reference from a missing artifact at the fit path. FR-386 names `NOT_FOUND` for
    *this* path, and one of the six types answering a submission differently from the other
    five is a difference a client would have to branch on for no reason it could see.

    TODO(main-thread): the fix is a sibling `metrics.resolve_artifact_ref` raising
    `NOT_FOUND` — which is metrics.py's own stated reason for diverging in the first place,
    "the two `resolve_ref`s are reached by different callers making different decisions with
    the answer", applied once more. That file was not this slice's to edit; until it is,
    the translation is here rather than the divergence being left in the API.
    """
    if artifact_ref.type != "custom_metric":
        return False
    try:
        metric = await metrics_service.resolve_ref(
            session, workspace_id=workspace_id, ref=str(artifact_ref)
        )
    except PlatformError as exc:
        if exc.code != "METRIC_REF_UNRESOLVED":
            raise
        raise PlatformError(
            "NOT_FOUND",
            "Custom metric not found",
            404,
            f"{artifact_ref} resolves to no custom metric in this workspace.",
        ) from exc
    service.require_in_review(artifact_ref, metric.status.value)
    return True


async def _resolve_rating_version(
    session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
) -> bool:
    """W7-3's own by-slug-and-version read, adapted to the fan-out's contract.

    A `rating_version` reference must resolve so a submission naming a rating version is
    refused if it does not exist (FR-386) — and accepted once `W7-3` builds the version.
    """
    if artifact_ref.type != "rating_version":
        return False
    from app.db.models import RatingVersionRow

    row = (
        await session.execute(
            select(RatingVersionRow).where(
                RatingVersionRow.workspace_id == workspace_id,
                RatingVersionRow.slug == artifact_ref.slug,
                RatingVersionRow.version == artifact_ref.version,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        return False
    service.require_in_review(artifact_ref, row.status)
    return True


async def _resolve_the_artifact(
    session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
) -> None:
    """Refuse a submission whose reference names a version that does not exist (FR-386).

    `_carry_to_the_artifact`'s shape for the other direction, and for its reason: one call
    per artifact type rather than a branch here, each returning `False` for a reference that
    is not its own, so adding a type is a change in that module and not in this route. The
    fan-out lives in the route because resolution needs a lookup per type and DEP-1 forbids
    `GOV` importing `DATA` through `MON`; this sits above both, which satisfies DEP-1 with no
    resolver registry — a second mechanism for a seam that already has one.

    **A type no module owns fails closed.** `rating_version` has a policy entry (`06` §4.2)
    and no module, because `03` is unbuilt, and thirteen more of `ARTIFACT_TYPES`' twenty
    have neither. `07`'s `JOB_HANDLER_NOT_REGISTERED` settles what a platform deployable
    before every kind has an implementation owes the caller: say the capability is absent.
    Letting the submission through instead recreates FR-386's own defect one level up —
    a request that decides without effect, and nothing to explain why.
    """
    if await _resolve_model(session, workspace_id=workspace_id, artifact_ref=artifact_ref):
        return
    if await _resolve_custom_objective(
        session, workspace_id=workspace_id, artifact_ref=artifact_ref
    ):
        return
    if await _resolve_custom_metric(
        session, workspace_id=workspace_id, artifact_ref=artifact_ref
    ):
        return
    if await perils_service.resolve_artifact_ref(
        session, workspace_id=workspace_id, artifact_ref=artifact_ref
    ):
        return
    if await validation_rules_service.resolve_artifact_ref(
        session, workspace_id=workspace_id, artifact_ref=artifact_ref
    ):
        return
    if await datasets_service.resolve_artifact_ref(
        session, workspace_id=workspace_id, artifact_ref=artifact_ref
    ):
        return
    if await _resolve_rating_version(
        session, workspace_id=workspace_id, artifact_ref=artifact_ref
    ):
        return
    # A Deployment Request: only one the deployment module wrote, in `review`, holding both
    # floor items (`PL-1392` Task 5 step 6; `RL-1301` audit advisory A2).
    if await deployments_service.resolve_artifact_ref(
        session, workspace_id=workspace_id, artifact_ref=artifact_ref
    ):
        return
    raise PlatformError(
        # Registered in GOVERNANCE_ERROR_CODES and declared in `06` §5.1 on 2026-08-22.
        # Deliberately **not** `VALIDATION_FAILED`, which the malformed-reference branch
        # above still uses correctly: there the caller's input is bad. Here it is not — the
        # reference is well formed, its type is in `ARTIFACT_TYPES`, and the workspace
        # policy admits it. What is absent is a module in this build, which is a fact about
        # the deployment. The same distinction `07` drew when it refused to fail a
        # handler-less Job as a bad request.
        "ARTIFACT_TYPE_NOT_RESOLVABLE",
        "No module in this deployment can resolve this artifact type",
        422,
        f"{artifact_ref.type!r} has an approval policy but no owning module here, so a "
        f"request pinning {artifact_ref} could be decided and would move nothing "
        "(`06` FR-386). Refused rather than accepted, for the reason `07` refuses a Job "
        "whose kind has no handler.",
    )


async def _carry_to_the_artifact(
    session: Any, *, caller: Caller, request: ApprovalRequestRow
) -> None:
    """Drive the owning module's transition for whatever type this request is about.

    One call per artifact type rather than a branch here: each module's function returns
    `None` for a request that is not its own, so adding a type is a change in that module
    and not in this route. `model`, `custom_objective`, `custom_metric`, `validation_rule`,
    `peril_structure`, `rating_version` and `deployment` have lifecycles in code; a type
    without one decides without an artifact to move.
    """
    async with service.approval_decision(session):
        await modelling_service.apply_approval_decision(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            request=request,
        )
        await objectives_service.apply_approval_decision(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            request=request,
        )
        await metrics_service.apply_approval_decision(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            request=request,
        )
        await validation_rules_service.apply_approval_decision(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            request=request,
        )
        await perils_service.apply_approval_decision(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            request=request,
        )
        await rating_versions_service.apply_approval_decision(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            request=request,
        )
        await deployments_service.apply_approval_decision(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            request=request,
        )
