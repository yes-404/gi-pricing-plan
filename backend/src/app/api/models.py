"""Factors and Models over HTTP (`02` §5.1).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/factors` | Create or version a Factor (FR-MODEL-1, FR-MODEL-7) |
| `GET` | `/factors` | List factors, with intent and prohibition visible |
| `POST` | `/bandings/propose` | Propose boundaries by method (FR-MODEL-9) — persists nothing |
| `POST` | `/bandings/evaluate` | Recompute band stats for **edited** boundaries (FR-MODEL-83) |
| `POST` | `/bandings` | Persist a Banding, editable boundaries and all (FR-MODEL-12) |
| `GET` | `/bandings` | List bandings |
| `POST` | `/groupings/propose` | Propose a mapping by method (FR-MODEL-14) |
| `POST` | `/groupings/evaluate` | Change in fit for an **edited** mapping (FR-MODEL-83) |
| `POST` | `/groupings` | Persist a Grouping (FR-MODEL-16) |
| `GET` | `/groupings` | List groupings |
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
from pydantic import BaseModel, ConfigDict, model_validator

from app.api.authz import requires
from app.api.deps import Caller, job_identity
from app.api.responses import problems
from app.db.session import Database
from app.platform import diagnostics as diagnostics_service
from app.platform import jobs as job_service
from app.platform import modelling as service
from app.platform import transformations as transform_service
from app.platform.blobs import BlobStore
from model_schema import (
    Banding,
    BandingEvaluation,
    BandingProposal,
    Diagnostics,
    Factor,
    FactorIntent,
    FactorType,
    GlmSpec,
    Grouping,
    GroupingEvaluation,
    GroupingProposal,
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


def _blob_store(request: Request) -> BlobStore:
    store: BlobStore = request.app.state.blob_store
    return store


BlobStoreDep = Annotated[BlobStore, Depends(_blob_store)]


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
    #: `02` §4.1. The `Factor` type refuses a `banding` with no `banding_id`, so the
    #: mismatch is a `422` with the field named rather than a resolution failure at fit
    #: time, twenty seconds and one Job later.
    banding_id: UUID | None = None
    grouping_id: UUID | None = None

    def as_factor(self) -> Factor:
        return Factor(id=uuid4(), version=1, **self.model_dump())

    @model_validator(mode="after")
    def _it_describes_a_factor_that_can_exist(self) -> FactorCreate:
        """Build the artifact here so its own invariants answer **422**, not 500.

        The handler used to construct the `Factor` itself, and every rule the type enforces
        — a prohibition with no reason, a monotonic direction with no rationale, and now a
        `banding` with no `banding_id` — reached the caller as an internal error with a
        pydantic traceback in the log. Restating the rules on this shape instead would be
        the same shape defined twice, which `CLAUDE.md` §2 forbids for exactly the reason
        that matters here: the two would diverge.
        """
        self.as_factor()
        return self


class BandingProposalRequest(BandingProposal):
    """A `BandingProposal` plus the slug the resulting artifact would carry.

    Separate from the core shape because a proposal is not yet an artifact: `pricing-core`
    is handed the statistical question, and the name belongs to the platform that will one
    day store it.
    """

    slug: str


class GroupingProposalRequest(GroupingProposal):
    slug: str


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
            factor=body.as_factor(),
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
    "/bandings/propose",
    summary="Propose banding boundaries",
    responses=problems(401, 403, 404, 409, 422),
)
async def propose_banding(
    body: BandingProposalRequest,
    caller: FitModels,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
) -> Banding:
    """FR-MODEL-9: the platform proposes, the actuary edits, and **nothing is stored**.

    The returned `Banding` carries a fresh id it does not own yet — `POST /bandings` is
    what allocates a version. Returning the whole artifact rather than a list of numbers is
    what makes "always editable" true: the caller can change a boundary and post back the
    same shape.
    """
    async with database.session() as session:
        return await transform_service.propose_banding_for_version(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            blob_store=blob_store,
            proposal=BandingProposal.model_validate(
                body.model_dump(exclude={"slug"})
            ),
            slug=body.slug,
        )


@router.post(
    "/bandings/evaluate",
    summary="Recompute band statistics for edited boundaries",
    responses=problems(401, 403, 404, 409, 422),
)
async def evaluate_banding(
    body: BandingEvaluation,
    caller: FitModels,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
) -> Banding:
    """FR-MODEL-83: what an edited boundary *did*, before the banding is saved.

    `/propose` derives boundaries from a method and cannot accept one, so this is the only
    route by which §5.3's interaction requirement can hold — band stats and CI widths that
    update as the actuary drags a cut point rather than after they commit to it.
    """
    async with database.session() as session:
        return await transform_service.evaluate_banding_for_version(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            blob_store=blob_store,
            evaluation=body,
        )


@router.post(
    "/bandings",
    status_code=status.HTTP_201_CREATED,
    summary="Persist a Banding",
    responses=problems(401, 403, 409, 422),
)
async def create_banding(
    body: Banding, caller: FitModels, database: DatabaseDep
) -> Banding:
    """FR-MODEL-12: an existing slug allocates the next version rather than editing.

    The whole artifact is the request body — boundaries the caller may have moved, labels
    they may have renamed, and the evidence the proposal came back with. `id` and `version`
    in the body are ignored; the platform allocates both.
    """
    async with database.unit_of_work() as session:
        row = await transform_service.create_banding(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            banding=body,
        )
        return transform_service.to_banding(row)


@router.get("/bandings", summary="List bandings", responses=problems(401, 403, 422))
async def list_bandings(
    caller: ReadModels,
    database: DatabaseDep,
    dataset_id: Annotated[UUID | None, Query()] = None,
) -> list[Banding]:
    async with database.session() as session:
        rows = await transform_service.list_bandings(
            session, workspace_id=caller.workspace_id, dataset_id=dataset_id
        )
        return [transform_service.to_banding(row) for row in rows]


@router.post(
    "/groupings/propose",
    summary="Propose a grouping",
    responses=problems(401, 403, 404, 409, 422),
)
async def propose_grouping(
    body: GroupingProposalRequest,
    caller: FitModels,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
) -> Grouping:
    """FR-MODEL-14, with FR-MODEL-15's evidence attached and nothing persisted."""
    async with database.session() as session:
        return await transform_service.propose_grouping_for_version(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            blob_store=blob_store,
            proposal=GroupingProposal.model_validate(
                body.model_dump(exclude={"slug"})
            ),
            slug=body.slug,
        )


@router.post(
    "/groupings/evaluate",
    summary="Recompute the change in fit for an edited mapping",
    responses=problems(401, 403, 404, 409, 422),
)
async def evaluate_grouping(
    body: GroupingEvaluation,
    caller: FitModels,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
) -> Grouping:
    """FR-MODEL-83, and the half `02` §5.3 names outright.

    Merging two levels shows the deviance/df trade-off *before* the grouping is saved. An
    actuary should never have to fit a model to find out whether a grouping was sensible,
    and computing the p-value only on save is computing it after the decision.
    """
    async with database.session() as session:
        return await transform_service.evaluate_grouping_for_version(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            blob_store=blob_store,
            evaluation=body,
        )


@router.post(
    "/groupings",
    status_code=status.HTTP_201_CREATED,
    summary="Persist a Grouping",
    responses=problems(401, 403, 409, 422),
)
async def create_grouping(
    body: Grouping, caller: FitModels, database: DatabaseDep
) -> Grouping:
    """FR-MODEL-16: creation is an audited event, because grouping is a modelling decision."""
    async with database.unit_of_work() as session:
        row = await transform_service.create_grouping(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            grouping=body,
        )
        return transform_service.to_grouping(row)


@router.get("/groupings", summary="List groupings", responses=problems(401, 403, 422))
async def list_groupings(
    caller: ReadModels,
    database: DatabaseDep,
    dataset_id: Annotated[UUID | None, Query()] = None,
) -> list[Grouping]:
    async with database.session() as session:
        rows = await transform_service.list_groupings(
            session, workspace_id=caller.workspace_id, dataset_id=dataset_id
        )
        return [transform_service.to_grouping(row) for row in rows]


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
        row, should_fit = await service.reserve_model(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            spec=body.spec,
            change_reason=body.change_reason,
        )
        if not should_fit:
            # FR-MODEL-66. The caller asked for a model with this specification and it is
            # fitted; fitting it again would produce the same numbers under a new id.
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


@router.get(
    "/models/{slug}/diagnostics",
    summary="Model diagnostics",
    responses=problems(401, 403, 404, 422),
)
async def get_model_diagnostics(
    slug: str,
    caller: ReadModels,
    database: DatabaseDep,
    version: Annotated[int | None, Query(ge=1)] = None,
) -> Diagnostics:
    """The evidence behind a fitted model (FR-MODEL-49, `02` §5.1).

    Read, never recomputed. FR-MODEL-49 makes diagnostics a product of the fit, so this
    endpoint returns what that fit recorded — a screen that recalculated them would be
    showing numbers no approval could cite.

    `?version=` selects a model version, like `GET /models/{slug}`; the latest without it.
    """
    async with database.session() as session:
        model = await service.load_model(
            session, workspace_id=caller.workspace_id, slug=slug, version=version
        )
        return await diagnostics_service.load_diagnostics(
            session, workspace_id=caller.workspace_id, model_id=model.id
        )
