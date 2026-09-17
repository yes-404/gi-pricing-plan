"""Rating Algorithm routes (03 §5.1, slice W9-2).

`POST /rating-algorithms` validates the submitted algorithm at save time and refuses an
invalid one with the named error; `GET /rating-algorithms/{slug}@{version}/diff` returns
the structural diff between two versions (FR-219).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.authz import requires
from app.api.deps import Caller, DatabaseDep
from app.api.responses import problems
from app.platform import rating_algorithms as service
from model_schema import Permission

__all__ = ["router"]

router = APIRouter(tags=["rating"])

RatingWriteDep = Annotated[Caller, Depends(requires(Permission.RATING_WRITE))]
RatingReadDep = Annotated[Caller, Depends(requires(Permission.RATING_READ))]


@router.post(
    "/rating-algorithms",
    summary="Create or version a Rating Algorithm",
    status_code=status.HTTP_201_CREATED,
    responses=problems(401, 403, 422, 409),
)
async def create_rating_algorithm(
    body: dict[str, Any],
    caller: RatingWriteDep,
    database: DatabaseDep,
) -> dict[str, Any]:
    """**201** with the saved slug and version, once save-time validation passes.

    The body is the raw `RatingAlgorithm` JSON (03 §4.1). Save-time validation runs
    before the row is written: the shape's graph invariants (FR-212) and the deeper
    checks in `pricing-core` (FR-216/227/273/274/275/276) — an invalid graph or a broken
    boundary guard is refused with its named code.
    """
    assert caller.principal.id is not None
    row = await service.create_algorithm(
        database, caller.workspace_id, caller.principal.id, body
    )
    return {"id": str(row.id), "slug": row.slug, "version": row.version}


@router.get(
    "/rating-algorithms/{slug}@{version}/diff",
    summary="Structural diff between two algorithm versions",
    responses=problems(401, 403, 404, 422),
)
async def algorithm_diff(
    slug: str,
    version: int,
    caller: RatingReadDep,
    database: DatabaseDep,
    against: int = Query(..., description="The version to diff against"),
) -> dict[str, Any]:
    """**200** with the structural diff (FR-219): steps added, removed, or changed,
    and tables re-pointed."""
    return await service.diff_between(
        database, caller.workspace_id, slug, version, against
    )
