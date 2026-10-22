"""Deployment routes (`03` §5.1, FR-267; WK-674 Slice 2, `PL-1392` Task 5).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/environments/{env}/deployment-requests` | Submit a Deployment Request |
| `POST` | `/api/v1/environments/{env}/deployments` | Deploy an approved version |
| `POST` | `/api/v1/environments/{env}/deployments/rollback` | Roll back (`deployment:promote`) |
| `GET` | `/api/v1/environments/{env}/deployments` | History, newest first (`rating:read`) |
| `PUT` | `/api/v1/environments/{env}/routing` | Write the date-routing rule |
| `PUT` | `/api/v1/environments/{env}/shadow` | Write the shadow configuration |

The two writes are **handler-guarded**, not `requires(...)`: `deployment:promote` is checked with
the target Environment as the resource, which needs the Environment row the handler loads
(`RL-1301` B.2; the authorisation sweep's `HANDLER_GUARDED` names each site). The bodies and
2xx are `model-schema` types (`tests/test_deployment_route_types.py`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.authz import CallerDep, CountAfterCheck, management_counter, requires
from app.api.deps import Caller, DatabaseDep
from app.api.pagination import DEFAULT_LIMIT, MAX_LIMIT, Page
from app.api.responses import problems
from app.platform import deployments as service
from app.platform import routing, shadow
from model_schema import (
    Deployment,
    DeploymentCreate,
    DeploymentCreated,
    DeploymentRequest,
    DeploymentRequestCreate,
    Permission,
    RollbackCreate,
    RoutingRule,
    RoutingRuleUpdate,
    ShadowConfig,
    ShadowConfigUpdate,
)

__all__ = ["router"]

router = APIRouter(prefix="/environments", tags=["platform"])

CountDep = Annotated[CountAfterCheck, Depends(management_counter)]
ReadHistoryDep = Annotated[Caller, Depends(requires(Permission.RATING_READ))]


@router.post(
    "/{env}/deployment-requests",
    summary="Submit a deployment request",
    status_code=status.HTTP_201_CREATED,
    response_model=DeploymentRequest,
    responses=problems(401, 403, 404, 409, 422),
)
async def submit_deployment_request(
    env: str,
    body: DeploymentRequestCreate,
    caller: CallerDep,
    count: CountDep,
    database: DatabaseDep,
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
            count_management=count,
        )


@router.post(
    "/{env}/deployments",
    summary="Deploy an approved version",
    status_code=status.HTTP_201_CREATED,
    response_model=DeploymentCreated,
    responses=problems(401, 403, 404, 409, 422, 503),
)
async def create_deployment(
    env: str,
    body: DeploymentCreate,
    request: Request,
    caller: CallerDep,
    count: CountDep,
    database: DatabaseDep,
) -> DeploymentCreated:
    """**201** with the Deployment and `switch`: the processes that swapped to it and the ones
    that did not (`03` FR-268). **409** `DEPLOY_REQUIRES_APPROVAL` for a gated target without an
    approved, unexecuted request; **409** `PROMOTION_ORDER_VIOLATION`; the Rating Version and
    Environment refusals of the request route; **422** for a non-Rating-Version reference;
    **503** `DEPLOY_SWITCH_INCOMPLETE` when a subscribed process did not acknowledge PREPARE (no
    Deployment is written)."""
    return await service.deploy_and_switch(
        database,
        workspace_id=caller.workspace_id,
        actor=caller.principal,
        environment=env,
        body=body,
        count_management=count,
        switch=getattr(request.app.state, "switch", None),
    )


@router.post(
    "/{env}/deployments/rollback",
    summary="Roll an environment back to an earlier Rating Version",
    status_code=status.HTTP_201_CREATED,
    response_model=DeploymentCreated,
    responses=problems(401, 403, 404, 409, 422, 503),
)
async def rollback_deployment(
    env: str,
    body: RollbackCreate,
    request: Request,
    caller: CallerDep,
    count: CountDep,
    database: DatabaseDep,
) -> DeploymentCreated:
    """**201** with the new Deployment and `switch` (`03` FR-269). Needs `deployment:promote` on
    the Environment and no new approval. **409** `VALIDATION_FAILED` when the Rating Version was
    never deployed to this Environment; **422** for a non-Rating-Version reference; **503**
    `DEPLOY_SWITCH_INCOMPLETE` when a subscribed process did not acknowledge PREPARE."""
    return await service.rollback_and_switch(
        database,
        workspace_id=caller.workspace_id,
        actor=caller.principal,
        environment=env,
        body=body,
        count_management=count,
        switch=getattr(request.app.state, "switch", None),
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
    plan names no permission for it, and the choice is recorded in `LG-1405`)."""
    return await service.list_deployments(
        database,
        workspace_id=caller.workspace_id,
        environment=env,
        cursor=cursor,
        limit=limit,
    )


@router.put(
    "/{env}/routing",
    summary="Write an environment's date-routing rule",
    response_model=RoutingRule,
    responses=problems(401, 403, 404, 409, 422),
)
async def write_routing_rule(
    env: str,
    body: RoutingRuleUpdate,
    caller: CallerDep,
    count: CountDep,
    database: DatabaseDep,
) -> RoutingRule:
    """**200** with the rule as written (`03` FR-270; `RL-1834` D1). Needs `deployment:promote`
    on the Environment; handler-guarded like the other writes. **404** for an unknown
    Environment; **409** `VALIDATION_FAILED` for a retired Environment or a Rating Version never
    deployed there, **409** `DEPLOY_DATE_RANGE_OVERLAP`; **422** for a non-Rating-Version
    reference or a range that does not end after it starts. An empty list clears the rule."""
    async with database.unit_of_work() as session:
        return await routing.write_rule(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            environment=env,
            body=body,
            count_management=count,
        )


@router.put(
    "/{env}/shadow",
    summary="Write an environment's shadow-scoring configuration",
    response_model=ShadowConfig,
    responses=problems(401, 403, 404, 409, 422),
)
async def write_shadow_config(
    env: str,
    body: ShadowConfigUpdate,
    caller: CallerDep,
    count: CountDep,
    database: DatabaseDep,
) -> ShadowConfig:
    """**200** with the configuration as written (`03` FR-271; `RL-1834` D2). Needs
    `admin:manage_settings` on the Environment; handler-guarded. **404** for an unknown
    Environment; **409** `VALIDATION_FAILED` for a retired one, **409** `BUNDLE_COMPILE_FAILED`
    for a candidate with no compiled bundle; **422** for a candidate that is not a Rating Version
    of this workspace, or is a `draft`, or a fraction outside `(0, 1]`."""
    async with database.unit_of_work() as session:
        return await shadow.write_config(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            environment=env,
            body=body,
            count_management=count,
        )
