"""Environment routes (`07` §5.1, FR-428; WK-674 Slice 2, `PL-1392` Task 4).

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/environments` | List, retired ones included, in promotion order |
| `POST` | `/api/v1/environments` | Create one; a slug is never reissued |
| `PATCH` | `/api/v1/environments/{slug}` | Change `name` and `description` only |
| `POST` | `/api/v1/environments/{slug}/retire` | Retire one nothing still names |

Every body is a `model-schema` type and every 2xx a `model-schema` shape (the Route table of
`PL-1392`, rows 1 to 4; `tests/test_deployment_route_types.py`). The three writes need
`admin:manage_environments`; the list needs `settings:read` (the plan names no read
permission for the list; the choice is recorded in `LG-9737` for the lead).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.authz import requires
from app.api.deps import Caller, DatabaseDep
from app.api.pagination import DEFAULT_LIMIT, MAX_LIMIT, Page
from app.api.responses import problems
from app.platform import environments as service
from model_schema import Environment, EnvironmentCreate, EnvironmentUpdate, Permission

__all__ = ["router"]

router = APIRouter(prefix="/environments", tags=["platform"])

ManageEnvironmentsDep = Annotated[
    Caller, Depends(requires(Permission.ADMIN_MANAGE_ENVIRONMENTS))
]
ReadEnvironmentsDep = Annotated[Caller, Depends(requires(Permission.SETTINGS_READ))]


@router.get(
    "",
    summary="List environments",
    response_model=Page[Environment],
    responses=problems(401, 403, 422),
)
async def list_environments(
    caller: ReadEnvironmentsDep,
    database: DatabaseDep,
    cursor: str | None = None,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
) -> Page[Environment]:
    """**200** with a page of Environments, retired ones included, in promotion order."""
    return await service.list_environments(database, caller.workspace_id, cursor, limit)


@router.post(
    "",
    summary="Create an environment",
    status_code=status.HTTP_201_CREATED,
    response_model=Environment,
    responses=problems(401, 403, 409, 422),
)
async def create_environment(
    body: EnvironmentCreate, caller: ManageEnvironmentsDep, database: DatabaseDep
) -> Environment:
    """**201**. **409** if the slug exists, retired or not; **422** if the slug is outside
    the reference grammar or the predecessor is not an existing Environment."""
    return await service.create_environment(
        database, caller.workspace_id, caller.principal, body
    )


@router.patch(
    "/{slug}",
    summary="Rename an environment",
    response_model=Environment,
    responses=problems(401, 403, 404, 409, 422),
)
async def update_environment(
    slug: str, body: EnvironmentUpdate, caller: ManageEnvironmentsDep, database: DatabaseDep
) -> Environment:
    """**200**. The body has `name` and `description` only: one naming `slug` is a **422**
    (`RL-1301` A.6)."""
    return await service.update_environment(
        database, caller.workspace_id, caller.principal, slug, body
    )


@router.post(
    "/{slug}/retire",
    summary="Retire an environment",
    response_model=Environment,
    responses=problems(401, 403, 404, 409, 422),
)
async def retire_environment(
    slug: str, caller: ManageEnvironmentsDep, database: DatabaseDep
) -> Environment:
    """**200** with `retired_at` set. **409** while a Deployment is live in it, a policy
    entry names it, or an unrevoked Service Account key names it."""
    return await service.retire_environment(
        database, caller.workspace_id, caller.principal, slug
    )
