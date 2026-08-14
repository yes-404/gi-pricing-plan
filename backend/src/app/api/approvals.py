"""The approval API (`06` §5.1).

| Method | Path |
|---|---|
| `POST` | `/api/v1/approval-requests` — submit an artifact |
| `GET` | `/api/v1/approval-requests` — list, filtered, cursor-paginated |
| `GET` | `/api/v1/approval-requests/{id}` — one request with its decisions |
| `POST` | `/api/v1/approval-requests/{id}/decide` — approve / reject / request changes |
| `POST` | `/api/v1/approval-requests/{id}/withdraw` |
| `GET`/`PUT` | `/api/v1/approval-policy` |

**FR-GOV-16's Approvals inbox is not this.** The list endpoint supports its query
(`?status=review`), but the requirement is about *evidence inline* — diffs, diagnostics,
dislocation, GIPP — and none of those artifacts exist before W4 and W5. Shipping a list and
calling it the inbox would claim the requirement while delivering the part that was easy.
"""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select

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
from app.db.models import ApprovalDecisionRow, ApprovalRequestRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as service
from model_schema import (
    ApprovalPolicy,
    ApprovalStatus,
    ArtifactRef,
    DecisionKind,
    Permission,
)

__all__ = ["router"]

router = APIRouter(tags=["governance"])

AnyCaller = Annotated[Caller, Depends(require_caller)]
Decider = Annotated[Caller, Depends(requires(Permission.APPROVAL_DECIDE))]
PolicyAdmin = Annotated[Caller, Depends(requires(Permission.ADMIN_MANAGE_ROLES))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


class SubmitApproval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_ref: str = Field(description="Canonical `{type}:{slug}@{version}` (ID-3).")
    change_summary: str = Field(min_length=1)
    environment: str | None = None


class Decide(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: DecisionKind
    comment: str | None = None


class Withdraw(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(min_length=1)
    artifact_is_live: bool = Field(
        default=False,
        description="Supplied by the caller: liveness belongs to the owning module (`03` "
        "for a Rating Version), not to governance. Governance owns the rule.",
    )


async def _detail(database: Database, row: ApprovalRequestRow) -> dict[str, Any]:
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
    return service.to_dict(row, decisions)


@router.post(
    "/approval-requests",
    status_code=status.HTTP_201_CREATED,
    summary="Submit an artifact for approval",
    responses=problems(401, 403, 409, 422),
)
async def submit_for_approval(
    body: SubmitApproval, caller: AnyCaller, database: DatabaseDep
) -> dict[str, Any]:
    """Anyone authenticated may submit; the policy decides who may approve.

    Deliberately not permission-gated beyond authentication: submitting is asking, and the
    module that owns the artifact has already decided whether this principal could create
    it. Gating the ask as well would mean an analyst who built a model could not put it
    forward.
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
        )
        return service.to_dict(row, [])


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
) -> Page[dict[str, Any]]:
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
    return Page[dict[str, Any]](
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
) -> dict[str, Any]:
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
) -> dict[str, Any]:
    async with database.unit_of_work() as session:
        row = await service.decide(
            session,
            workspace_id=caller.workspace_id,
            request_id=request_id,
            approver=caller.principal,
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
        return service.to_dict(row, decisions)


@router.post(
    "/approval-requests/{request_id}/withdraw",
    summary="Withdraw before deployment (FR-GOV-15)",
    responses=problems(401, 403, 404, 409, 422),
)
async def withdraw_request(
    request_id: UUID, body: Withdraw, caller: Decider, database: DatabaseDep
) -> dict[str, Any]:
    async with database.unit_of_work() as session:
        row = await service.withdraw(
            session,
            workspace_id=caller.workspace_id,
            request_id=request_id,
            actor=caller.principal,
            reason=body.reason,
            artifact_is_live=body.artifact_is_live,
        )
        return service.to_dict(row, [])


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
