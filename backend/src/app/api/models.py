"""Factors and Models over HTTP (`02` §5.1).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/factors` | Create or version a Factor (FR-MODEL-1, FR-MODEL-7) |
| `GET` | `/factors` | List factors, with intent and prohibition visible |
| `POST` | `/models` | **202** Fit → Job; returns the existing model on `spec_hash` match |
| `GET` | `/models/{slug}` | The model artifact, latest or a named version |

`POST /models` answers **202 with a Job** for a new fit and **200 with the model** when the
specification has already been fitted (FR-MODEL-66). Two status codes for one route because
they are two different facts: work has started, or the answer already exists.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Query, Request, Response, status
from pydantic import BaseModel, ConfigDict

from app.api.authz import requires
from app.api.deps import Caller, job_identity
from app.api.responses import problems
from app.db.session import Database
from app.platform import jobs as job_service
from app.platform import modelling as service
from model_schema import (
    Factor,
    FactorIntent,
    FactorType,
    GlmSpec,
    Job,
    JobKind,
    JobQueue,
    Model,
    MonotonicDirection,
)
from model_schema import Permission as Perm

__all__ = ["router"]

router = APIRouter(tags=["modelling"])

ReadModels = Annotated[Caller, Depends(requires(Perm.MODEL_READ))]
FitModels = Annotated[Caller, Depends(requires(Perm.MODEL_FIT))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


class FactorCreate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: str
    dataset_id: UUID
    type: FactorType = FactorType.IDENTITY
    source_columns: tuple[str, ...]
    intent: FactorIntent = FactorIntent.RISK
    monotonic_direction: MonotonicDirection = MonotonicDirection.NONE
    monotonic_rationale: str | None = None
    prohibited: bool = False
    prohibited_reason: str | None = None


class ModelCreate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    spec: GlmSpec
    change_reason: str | None = None


@router.post(
    "/factors",
    status_code=status.HTTP_201_CREATED,
    summary="Create or version a Factor",
    responses=problems(401, 403, 422),
)
async def create_factor(
    body: FactorCreate, caller: FitModels, database: DatabaseDep
) -> Factor:
    """FR-MODEL-7: an existing slug allocates the next version rather than editing.

    A Model Spec pins a factor *version*, so editing one in place would silently change
    what every model fitted on it was fitted on.
    """
    async with database.unit_of_work() as session:
        row = await service.create_factor(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            factor=Factor(id=uuid4(), version=1, **body.model_dump()),
        )
        return service.to_factor(row)


@router.get(
    "/factors",
    summary="List factors",
    responses=problems(401, 403, 422),
)
async def list_factors(
    caller: ReadModels,
    database: DatabaseDep,
    dataset_id: Annotated[UUID | None, Query()] = None,
) -> list[Factor]:
    async with database.session() as session:
        rows = await service.list_factors(
            session, workspace_id=caller.workspace_id, dataset_id=dataset_id
        )
        return [service.to_factor(row) for row in rows]


@router.post(
    "/models",
    summary="Fit a model",
    responses=problems(401, 403, 404, 409, 422),
)
async def fit_model(
    body: ModelCreate,
    caller: FitModels,
    database: DatabaseDep,
    response: Response,
) -> Job | Model:
    """**202** with a Job for a new fit; **200** with the model when it already exists.

    `02` R1 is answered here rather than in the worker: a dataset version that is not
    `validated` is refused with a `409` before any Job exists, because learning it from a
    failed job twenty seconds later is a worse answer to the same question.
    """
    async with database.unit_of_work() as session:
        row, created = await service.reserve_model(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            spec=body.spec,
            change_reason=body.change_reason,
        )
        if not created:
            # FR-MODEL-66. The caller asked for a model with this specification and it
            # exists; fitting it again would produce the same numbers under a new id.
            response.status_code = status.HTTP_200_OK
            return service.to_model(row)

        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {**job_identity(caller), **service.fit_payload(row)},
            caller.principal,
            workspace_id=caller.workspace_id,
            queue=JobQueue.COMPUTE,
        )
        response.status_code = status.HTTP_202_ACCEPTED
        response.headers["Location"] = f"/api/v1/jobs/{job.id}"
        return job


@router.get(
    "/models/{slug}",
    summary="Model artifact",
    responses=problems(401, 403, 404, 422),
)
async def get_model(
    slug: str,
    caller: ReadModels,
    database: DatabaseDep,
    version: Annotated[int | None, Query(ge=1)] = None,
) -> Model:
    async with database.session() as session:
        row = await service.load_model(
            session, workspace_id=caller.workspace_id, slug=slug, version=version
        )
        return service.to_model(row)
