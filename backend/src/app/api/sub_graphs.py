"""Sub-graph routes (03 §5.1, FR-217's artifact limb; WK-1250 Slice 1).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/sub-graphs` | Create a Sub-graph (version 1); 409 on an existing slug |
| `POST` | `/api/v1/sub-graphs/{slug}/versions` | Write the next version; 404 on an unknown slug |
| `GET` | `/api/v1/sub-graphs/{slug}@{version}` | Read one version |
| `GET` | `/api/v1/sub-graphs/{slug}/versions` | List a slug's versions, cursor-paginated |

There is no update and no delete (`00` FR-4). The two creates take the raw JSON body, as
`POST /rating-algorithms` does, so that the service's one refusal mapping — not FastAPI's
request validation — chooses the code a refusal returns (`RATING_GRAPH_CYCLIC`,
`RATING_GRAPH_UNRESOLVED_REF`, `RATING_TYPE_MISMATCH`). The request shapes are published as
`sub-graph-create` and `sub-graph-body` JSON Schemas instead.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.authz import requires
from app.api.deps import Caller, DatabaseDep
from app.api.pagination import DEFAULT_LIMIT, MAX_LIMIT, Page
from app.api.responses import problems
from app.platform import sub_graphs as service
from model_schema import Permission, SubGraph

__all__ = ["router"]

router = APIRouter(prefix="/sub-graphs", tags=["rating"])

RatingWriteDep = Annotated[Caller, Depends(requires(Permission.RATING_WRITE))]
RatingReadDep = Annotated[Caller, Depends(requires(Permission.RATING_READ))]


@router.post(
    "",
    summary="Create a Sub-graph",
    status_code=status.HTTP_201_CREATED,
    response_model=SubGraph,
    responses=problems(401, 403, 409, 422),
)
async def create_sub_graph(
    body: dict[str, Any], caller: RatingWriteDep, database: DatabaseDep
) -> SubGraph:
    """**201** with version 1. The body is a `SubGraphCreate` (03 §4.11); **409** if the
    slug exists, and a refusal carries the code of the rule it broke."""
    return await service.create_sub_graph(database, caller.workspace_id, caller.principal, body)


@router.post(
    "/{slug}/versions",
    summary="Write the next version of a Sub-graph",
    status_code=status.HTTP_201_CREATED,
    response_model=SubGraph,
    responses=problems(401, 403, 404, 409, 422),
)
async def create_sub_graph_version(
    slug: str, body: dict[str, Any], caller: RatingWriteDep, database: DatabaseDep
) -> SubGraph:
    """**201** with the next version (maximum plus one). The body is a `SubGraphBody`;
    **404** on an unknown slug."""
    return await service.create_version(
        database, caller.workspace_id, caller.principal, slug, body
    )


@router.get(
    "/{slug}@{version}",
    summary="Read one Sub-graph version",
    response_model=SubGraph,
    responses=problems(401, 403, 404, 422),
)
async def get_sub_graph(
    slug: str, version: int, caller: RatingReadDep, database: DatabaseDep
) -> SubGraph:
    """**200** with the version; another workspace's is a **404**."""
    return await service.get_version(database, caller.workspace_id, slug, version)


@router.get(
    "/{slug}/versions",
    summary="List a Sub-graph's versions",
    response_model=Page[SubGraph],
    responses=problems(401, 403, 404, 422),
)
async def list_sub_graph_versions(
    slug: str,
    caller: RatingReadDep,
    database: DatabaseDep,
    cursor: str | None = None,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
) -> Page[SubGraph]:
    """**200** with a page of versions, oldest first."""
    return await service.list_versions(database, caller.workspace_id, slug, cursor, limit)
