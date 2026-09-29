"""Regression Suite routes (03 §5.1, FR-260; PL-1189 Task 4).

`POST /regression-suites/{slug}/versions` creates the next version (`rating:write`, 201);
`GET /regression-suites/{slug}@{version}` reads one (`rating:read`). Both bodies are
`model-schema`'s shapes. A suite version carries full quote inputs, so the read is
permission-checked like any other rating artifact (NFR-499).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.authz import requires
from app.api.deps import Caller, DatabaseDep
from app.api.responses import problems
from app.platform import regression_suites as service
from model_schema import (
    Permission,
    RegressionSuite,
    RegressionSuiteContent,
    RegressionSuiteVersionCreate,
)

__all__ = ["router"]

router = APIRouter(tags=["rating"])

RatingWriteDep = Annotated[Caller, Depends(requires(Permission.RATING_WRITE))]
RatingReadDep = Annotated[Caller, Depends(requires(Permission.RATING_READ))]


@router.post(
    "/regression-suites/{slug}/versions",
    summary="Create a new Regression Suite version",
    status_code=status.HTTP_201_CREATED,
    responses=problems(401, 403, 409, 422),
)
async def create_regression_suite_version(
    slug: str,
    body: RegressionSuiteVersionCreate,
    caller: RatingWriteDep,
    database: DatabaseDep,
) -> RegressionSuite:
    """**201** with the new version. One suite per Rating Algorithm (409 otherwise), and a
    suite never changes algorithm across versions (409)."""
    content = RegressionSuiteContent.model_validate(
        body.model_dump(include=set(RegressionSuiteContent.model_fields))
    )
    async with database.unit_of_work() as session:
        suite, row = await service.create_suite_version(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=slug,
            content=content,
            change_note=body.change_note,
        )
        return service.to_schema(suite, row)


@router.get(
    "/regression-suites/{slug}@{version}",
    summary="Read a Regression Suite version",
    responses=problems(401, 403, 404, 422),
)
async def get_regression_suite_version(
    slug: str,
    version: int,
    caller: RatingReadDep,
    database: DatabaseDep,
) -> RegressionSuite:
    """**200** with the version, golden-quote contexts included (access-controlled)."""
    async with database.session() as session:
        suite, row = await service.load_suite_version(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=slug,
            version=version,
        )
        return service.to_schema(suite, row)
