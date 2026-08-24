"""Peril structures over HTTP (`02` §5.1, FR-MODEL-58..61).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/peril-structures` | **201** Create or version a Peril Structure (FR-MODEL-58) |
| `GET` | `/peril-structures` | One page of the workspace's structures (FR-MODEL-127) |
| `GET` | `/peril-structures/{id}` | The structure and its reconciliation (FR-MODEL-90) |
| `POST` | `/peril-structures/{id}/reconcile` | **202** Reconcile → Job (FR-MODEL-60) |
| `POST` | `/peril-structures/{id}/submit` | Submit for approval (FR-MODEL-61) |

**The `GET` and the submit are additions to §5.1's table**, which declared the create and
the reconcile and nothing else. That is a create whose artifact nothing can fetch and an
approvable artifact with no way to submit it — the same omission FR-MODEL-84 repaired for
the transparency artifact and FR-MODEL-56 for the comparison, and invisible to the endpoint
audit for the same reason: it compares the spec against the contract, and an endpoint
missing from both is in neither. FR-MODEL-90 declares them.

A separate module rather than more of `models.py`: a Peril Structure is a different artifact
with its own lifecycle, and `models.py` is already the longest router in the service.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.authz import requires
from app.api.deps import Caller, job_identity
from app.api.pagination import (
    COUNT_CAP,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    Page,
    decode_cursor,
    encode_cursor,
)
from app.api.responses import problems
from app.db.session import Database
from app.platform import jobs as job_service
from app.platform import perils as service
from model_schema import (
    DecimalStr,
    ExcludedPeril,
    Job,
    JobKind,
    JobQueue,
    PerilComponent,
    PerilStructure,
    PerilStructureStatus,
    Slug,
)
from model_schema import Permission as Perm

__all__ = ["router"]

router = APIRouter(tags=["modelling"])

ReadModels = Annotated[Caller, Depends(requires(Perm.MODEL_READ))]
FitModels = Annotated[Caller, Depends(requires(Perm.MODEL_FIT))]
SubmitModels = Annotated[Caller, Depends(requires(Perm.MODEL_SUBMIT))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


class CreatePerilStructure(BaseModel):
    """FR-MODEL-58's composition. Every invariant is the contract type's, not this one's."""

    model_config = ConfigDict(extra="forbid")

    slug: Slug
    perils: list[PerilComponent] = Field(min_length=1)
    excluded_perils: list[ExcludedPeril] = []


class ReconcileRequest(BaseModel):
    """FR-MODEL-60's inputs.

    **The two column names have no defaults, deliberately.** FR-MODEL-60 says the modelled
    burning cost reconciles to the *observed* burning cost and does not say where the
    observed figure comes from — and it cannot be derived: a peril's severity model responds
    to its own peril's cost, not to the total, and the exposure a frequency model offsets by
    is not necessarily the exposure the burning cost is expressed per. A default here would
    reconcile against whichever column happened to match, and report a ratio for it.
    Recorded in `02` §4.10 with this slice.
    """

    model_config = ConfigDict(extra="forbid")

    observed_column: str = Field(
        min_length=1,
        description="Holdout column holding observed incurred cost, in minor units.",
    )
    exposure_column: str = Field(
        min_length=1, description="Holdout column holding exposure, in the same unit the "
        "models were fitted against.",
    )
    #: `DecimalStr`, not a bare `Decimal` — **corrected 2026-08-22 (W5, the
    #: audit-remediation slice).** A bare `Decimal` is the hole FR-OVR-18 closed one layer
    #: up and this field reopened at the wire: Pydantic renders it as
    #: `anyOf: [{"type": "number"}, {"type": "string"}]`, so the *published contract*
    #: admitted a binary float, and `{"tolerance": 0.1 + 0.2}` validated to
    #: `Decimal('0.30000000000000004')` — the float's error preserved verbatim inside the
    #: value that decides whether a reconciliation passes (FR-MODEL-60's `|ratio - 1| <=
    #: tolerance`). Measured, not assumed: research finding F7 is what `money.py` records,
    #: and the behaviour was re-checked against this exact model before the change.
    #:
    #: This is a **breaking wire change**: a caller sending a JSON number now gets a 422
    #: naming the reason. That is the same trade FR-OVR-7 has already been paid everywhere
    #: else in the exact-decimal path, and a tolerance is squarely in it.
    tolerance: DecimalStr = Field(
        default=Decimal("0.02"),
        description="Fractional tolerance on |modelled/observed - 1| (FR-MODEL-60).",
    )


class SubmitPerilStructure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    change_summary: str = Field(min_length=1)


class PerilStructureFilter(BaseModel):
    """`GET /peril-structures`'s query string — `02` §5.1:1712's two filters, and no more.

    `extra="forbid"` for `ObjectiveFilter`'s reason: a mistyped `?stauts=archived` that is
    silently ignored returns the unfiltered library, and the caller reads it as the answer
    to the question they meant to ask.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: PerilStructureStatus | None = Field(
        default=None, description="Restrict to structures in this lifecycle state."
    )
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description="Structure slug, matched exactly.",
    )
    cursor: str | None = Field(
        default=None, description="Opaque; pass back the previous page's `next_cursor`."
    )
    limit: int = Field(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)


PerilStructureFilterDep = Annotated[PerilStructureFilter, Query()]


@router.post(
    "/peril-structures",
    summary="Create or version a Peril Structure",
    status_code=status.HTTP_201_CREATED,
    responses=problems(401, 403, 404, 409, 422),
)
async def create_peril_structure(
    body: CreatePerilStructure, caller: FitModels, database: DatabaseDep
) -> PerilStructure:
    """**201** with the structure (`wf-01` E4, FR-MODEL-58).

    201 rather than 202: composing is not work. The models are already fitted, and what this
    writes is the declaration of how they combine. The *reconciliation* is the work, and it
    is a separate call for exactly that reason.

    Every referenced model is resolved here, before the row exists — a structure citing a
    model that does not resolve, or one that was never fitted, is a composition that cannot
    be priced, and it is cheaper to say so now than at reconcile time.
    """
    async with database.unit_of_work() as session:
        row = await service.create_structure(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=body.slug,
            perils=list(body.perils),
            excluded_perils=[e.model_dump(mode="json") for e in body.excluded_perils],
        )
        return service.to_structure(row)


@router.get(
    "/peril-structures",
    summary="List the workspace's Peril Structures",
    responses=problems(400, 401, 403, 422),
)
async def list_peril_structures_route(
    caller: ReadModels,
    database: DatabaseDep,
    filters: PerilStructureFilterDep,
) -> Page[PerilStructure]:
    """One page of the library (FR-MODEL-127), newest first.

    **No `usage_count`, deliberately.** `02` §5.1:1712 asks this row for pagination and the
    two filters and stops, where :1697 and :1705 name the count for objectives and metrics —
    and FR-MODEL-127's prose says "`usage_count` is on the row" without saying which rows.
    This route builds the endpoint table's reading and `test_the_row_carries_no_usage_count`
    asserts the absence, so the field cannot appear here by accident. The disagreement
    between the table and the prose is raised as an open question in `open-questions.md` and
    mirrored in `02` §10 rather than settled here: whether a Peril Structure has a blast
    radius worth counting depends on how a Model Spec names one, which is a question about
    the reference direction and not about this route.

    Named `list_peril_structures_route` because `service.list_peril_structures` is the query
    behind it; two different things sharing one name in one module is an import the reader
    has to disambiguate.
    """
    after = decode_cursor(filters.cursor)

    async with database.session() as session:
        rows, total = await service.list_peril_structures(
            session,
            workspace_id=caller.workspace_id,
            limit=filters.limit,
            count_cap=COUNT_CAP,
            status=filters.status,
            slug=filters.slug,
            after=after,
        )

    # The extra row exists only to answer "is there another page?" and is not returned.
    has_more = len(rows) > filters.limit
    page_rows = list(rows[: filters.limit])

    return Page[PerilStructure](
        items=[service.to_structure(row) for row in page_rows],
        next_cursor=encode_cursor(page_rows[-1].id) if has_more and page_rows else None,
        total_estimate=total,
    )


@router.get(
    "/peril-structures/{structure_id}",
    summary="A Peril Structure and its reconciliation",
    responses=problems(401, 403, 404, 422),
)
async def get_peril_structure(
    structure_id: UUID, caller: ReadModels, database: DatabaseDep
) -> PerilStructure:
    """**Added to `02` §5.1 with this slice** (FR-MODEL-90) — see the module docstring."""
    async with database.unit_of_work() as session:
        return await service.load_structure(
            session, workspace_id=caller.workspace_id, structure_id=structure_id
        )


@router.post(
    "/peril-structures/{structure_id}/reconcile",
    summary="Reconcile modelled risk premium against observed burning cost",
    responses=problems(401, 403, 404, 409, 422),
)
async def reconcile_peril_structure(
    structure_id: UUID,
    body: ReconcileRequest,
    caller: FitModels,
    database: DatabaseDep,
    response: Response,
) -> Job:
    """**202** with a Job (`wf-01` E5, FR-MODEL-60).

    202 because it is work: every peril's models are scored over the holdout before anything
    can be compared. The refusals a caller can be told about now — a tolerance of zero, a
    model that is not fitted, a `separate_model` treatment nothing computes yet — are
    answered before the Job exists, so the answer is a 409 naming the peril rather than a
    failed job twenty seconds later.
    """
    async with database.unit_of_work() as session:
        row = await service.request_reconciliation(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            structure_id=structure_id,
            tolerance=body.tolerance,
        )
        job = await job_service.submit(
            session,
            JobKind.PERIL_STRUCTURE_RECONCILE,
            {
                **job_identity(caller),
                **service.reconcile_payload(
                    row,
                    tolerance=body.tolerance,
                    observed_column=body.observed_column,
                    exposure_column=body.exposure_column,
                ),
            },
            caller.principal,
            workspace_id=caller.workspace_id,
            queue=JobQueue.COMPUTE,
        )
        response.status_code = status.HTTP_202_ACCEPTED
        response.headers["Location"] = f"/api/v1/jobs/{job.id}"
        return job


@router.post(
    "/peril-structures/{structure_id}/submit",
    summary="Submit a Peril Structure for approval",
    responses=problems(401, 403, 404, 409, 422),
)
async def submit_peril_structure(
    structure_id: UUID,
    body: SubmitPerilStructure,
    caller: SubmitModels,
    database: DatabaseDep,
) -> PerilStructure:
    """`reconciled → review` (FR-MODEL-61, FR-MODEL-90).

    Gated on `model:submit` for the reason a Model's submission is: putting an artifact in
    front of an approver starts a governed process, and the role that may compose is not
    automatically the role that may do that.
    """
    async with database.unit_of_work() as session:
        row, _request = await service.submit_for_review(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            structure_id=structure_id,
            change_summary=body.change_summary,
        )
        return service.to_structure(row)
