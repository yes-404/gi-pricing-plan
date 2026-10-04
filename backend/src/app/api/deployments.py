"""Deployment routes (`03` §5.1, FR-267; WK-674 Slice 2, `PL-1392` Task 5).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/environments/{env}/deployment-requests` | Submit a Deployment Request |
| `POST` | `/api/v1/environments/{env}/deployments` | Deploy an approved version |
| `GET` | `/api/v1/environments/{env}/deployments` | History, newest first (`rating:read`) |

The two writes are **handler-guarded**, not `requires(...)`: `deployment:promote` is checked with
the target Environment as the resource, which needs the Environment row the handler loads
(`RL-1301` B.2; the authorisation sweep's `HANDLER_GUARDED` names each site). The bodies and
2xx are `model-schema` types (`tests/test_deployment_route_types.py`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.authz import requires
from app.api.deps import Caller, DatabaseDep, require_caller
from app.api.pagination import DEFAULT_LIMIT, MAX_LIMIT, Page
from app.api.responses import problems
from app.platform import deployments as service
from model_schema import (
    Deployment,
    DeploymentCreate,
    DeploymentRequest,
    DeploymentRequestCreate,
    Permission,
)

__all__ = ["router"]

router = APIRouter(prefix="/environments", tags=["platform"])

AnyCaller = Annotated[Caller, Depends(require_caller)]
ReadHistoryDep = Annotated[Caller, Depends(requires(Permission.RATING_READ))]


@router.post(
    "/{env}/deployment-requests",
    summary="Submit a deployment request",
    status_code=status.HTTP_201_CREATED,
    response_model=DeploymentRequest,
    responses=problems(401, 403, 404, 409, 422),
)
async def submit_deployment_request(
    env: str, body: DeploymentRequestCreate, caller: AnyCaller, database: DatabaseDep
) -> DeploymentRequest:
    """**201**. **403** without `deployment:promote` on this Environment; **404** for an unknown
    Environment or Rating Version; **409** `VALIDATION_FAILED` for a retired Environment or a
    version that is not `approved`, **409** `BUNDLE_COMPILE_FAILED` for one never compiled;
    **422** for a non-Rating-Version reference, an Environment with no `deployment` policy
    entry, or incomplete evidence (`EVIDENCE_INCOMPLETE`)."""
    async with database.unit_of_work() as session:
        return await service.submit_request(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            environment=env,
            body=body,
        )


@router.post(
    "/{env}/deployments",
    summary="Deploy an approved version",
    status_code=status.HTTP_201_CREATED,
    response_model=Deployment,
    responses=problems(401, 403, 404, 409, 422),
)
async def create_deployment(
    env: str, body: DeploymentCreate, caller: AnyCaller, database: DatabaseDep
) -> Deployment:
    """**201**. **409** `DEPLOY_REQUIRES_APPROVAL` for a gated target without an approved,
    unexecuted request; **409** `PROMOTION_ORDER_VIOLATION`; the Rating Version and Environment
    refusals of the request route; **422** for a non-Rating-Version reference."""
    async with database.unit_of_work() as session:
        return await service.deploy(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            environment=env,
            body=body,
        )


@router.get(
    "/{env}/deployments",
    summary="Deployment history for an environment",
    response_model=Page[Deployment],
    responses=problems(401, 403, 404, 422),
)
async def list_deployments(
    env: str,
    caller: ReadHistoryDep,
    database: DatabaseDep,
    cursor: str | None = None,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
) -> Page[Deployment]:
    """**200**, newest first; needs `rating:read` (the history is `06` FR-382's evidence; the
    plan names no permission for it, and the choice is recorded in `LG-9737`)."""
    return await service.list_deployments(
        database,
        workspace_id=caller.workspace_id,
        environment=env,
        cursor=cursor,
        limit=limit,
    )
