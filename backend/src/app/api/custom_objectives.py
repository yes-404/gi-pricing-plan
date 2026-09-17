"""Custom Objectives over HTTP (`02` §5.1, FR-MODEL-38..47, 75, 127).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/custom-objectives` | **201** Create or version an objective → `draft` (FR-142) |
| `GET` | `/custom-objectives` | The library: paginated, filtered, counted (FR-167) |
| `GET` | `/custom-objectives/{id}` | The objective and its lifecycle (FR-166) |
| `POST` | `/custom-objectives/{id}/derive` | Refused: `expression` is Phase 2 (FR-MODEL-40, 75) |
| `POST` | `/custom-objectives/{id}/certify` | **202** Run §4.7's checks → Job (FR-146) |
| `GET` | `/custom-objectives/{id}/certificate` | The latest certificate (FR-166) |
| `POST` | `/custom-objectives/{id}/submit` | Submit for approval (FR-163) |
| `GET` | `/custom-objectives/{id}/usage` | Blast radius (FR-164) |

**The `GET`s are additions to §5.1's table**, which declared five writes and no read — a
create whose artifact nothing can fetch, and a certificate produced by a Job that no
endpoint returns. The same omission FR-192 repaired for the Peril Structure, and
invisible to the endpoint audit for the same reason: it compares the spec against the
contract, and an endpoint missing from both is in neither. FR-166 declares them.

**The collection `GET` is the eighth route and the latest of those additions**
(FR-167, 2026-08-23). For five days this module was seven routes none of which
listed, which FR-166's amendment recorded as an observation and cured nothing: `02`
§5.3 asked for a library screen no endpoint could supply, and a `slug@version` address had
nothing to resolve against a UUID-only detail route.

`/derive` **is** built, as a refusal. FR-150 names it explicitly as one of the two
paths that answer `OBJECTIVE_KIND_NOT_ENABLED`, and a declared endpoint that 404s says
"this platform has no such concept" where the truth is "not until Phase 2".
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.authz import requires
from app.api.deps import Caller, SettingsDep, job_identity
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
from app.errors import PlatformError
from app.platform import jobs as job_service
from app.platform import objectives as service
from model_schema import (
    Applicability,
    CustomObjective,
    HessianStrategy,
    Job,
    JobKind,
    JobQueue,
    ObjectiveCertificate,
    ObjectiveKind,
    ObjectiveStatus,
    ObjectiveTemplate,
    ObjectiveUsage,
    SamplingSpec,
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


class CreateCustomObjective(BaseModel):
    """FR-142's artifact. Every range and rule is `CustomObjective`'s, not this one's.

    `kind` is here rather than assumed so that a caller asking for an `expression`
    objective is *answered* — FR-150 makes that a named refusal, and a body that
    silently forbade the field would leave them reading a 422 about an unexpected key.
    """

    model_config = ConfigDict(extra="forbid")

    slug: Slug
    kind: ObjectiveKind = ObjectiveKind.TEMPLATE
    template: ObjectiveTemplate | None = None
    #: `int | float`, `CustomObjective.params`'s own type — a money-kind template parameter
    #: (`capped_gamma.cap`, `spliced_severity`'s threshold) must arrive as an integer
    #: minor-unit amount (`CLAUDE.md` §7), and a narrower `dict[str, float]` here would
    #: coerce it to a float before the contract's own `TemplateParameter.check` ever saw
    #: it, turning a valid request into a 422 the caller cannot fix by re-reading §4.5.
    params: dict[str, int | float] = Field(default_factory=dict)
    #: Omitted means the template's own (§4.5). An author may narrow it and never widen it.
    applicability: Applicability | None = None
    hessian_strategy: HessianStrategy = HessianStrategy.CLIP_TO_MIN
    hessian_min: float = Field(default=1e-6, gt=0.0)
    description: str | None = None


class CertifyRequest(BaseModel):
    """§4.7's sampling grid, or nothing.

    Omitted means `default_sampling` derives it from the objective's applicability — a
    probability response, a count and money in minor units need spans of 1, 20 and 10⁶, and
    one default for all three would certify most of the catalogue on a domain it never sees.
    A caller who names a grid gets exactly it, and the certificate records which was used.
    """

    model_config = ConfigDict(extra="forbid")

    sampling: SamplingSpec | None = None


class SubmitCustomObjective(BaseModel):
    model_config = ConfigDict(extra="forbid")

    change_summary: str = Field(min_length=1)


class ObjectiveFilter(BaseModel):
    """`GET /custom-objectives`' filters and cursor page (`00` §5.2, FR-167).

    `extra="forbid"` for `ModelFilter`'s reason: a misspelled query parameter that is
    silently ignored returns a full library where the caller asked for one artifact.

    `slug` is an **exact** match. FR-167 makes this filter what resolves §5.3's
    `slug@version` addresses against UUID-only detail routes, so a prefix or substring
    match would answer `motor-ad` with `motor-ad-severity` too — a wrong artifact rather
    than a wide result.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: ObjectiveStatus | None = Field(
        default=None, description="Restrict to objectives in this lifecycle state."
    )
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description="Objective slug, matched exactly.",
    )
    cursor: str | None = Field(
        default=None, description="Opaque; pass back the previous page's `next_cursor`."
    )
    limit: int = Field(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)


ObjectiveFilterDep = Annotated[ObjectiveFilter, Query()]


@router.get(
    "/custom-objectives",
    summary="List the workspace's Custom Objectives",
    responses=problems(400, 401, 403, 422),
)
async def list_custom_objectives(
    caller: ReadModels,
    database: DatabaseDep,
    filters: ObjectiveFilterDep,
) -> Page[CustomObjective]:
    """The library `02` §5.3 renders (FR-167), cursor-paginated, newest first.

    Until this route the module had create, detail, certify, submit and usage and nothing
    that lists, so §5.3 asked for a screen no endpoint could supply and a `slug@version`
    address had no way to reach a UUID-only detail route.

    **400 in, 404 out.** A filter matching nothing is an empty 200 — the artifact the
    caller named may simply not exist yet, which is a result, not an error. Only a cursor
    this API did not issue is a 400.

    `usage_count` is **one grouped aggregate over the page's refs**, never one query per
    row: FR-167 makes that budget part of the requirement rather than an
    optimisation, because the query reads an unindexed JSONB column and an N+1 here would
    be indistinguishable from this until a workspace held a few hundred artifacts. It
    counts exactly what `GET /{id}/usage` counts, so a row and the page opened from it
    cannot disagree.
    """
    after = decode_cursor(filters.cursor)

    async with database.session() as session:
        rows, total = await service.list_objectives(
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

        counts = await service.usage_counts(
            session,
            workspace_id=caller.workspace_id,
            refs=[f"custom_objective:{row.slug}@{row.version}" for row in page_rows],
        )

    return Page[CustomObjective](
        items=[
            service.to_objective(
                row,
                usage_count=counts.get(f"custom_objective:{row.slug}@{row.version}", 0),
            )
            for row in page_rows
        ],
        next_cursor=encode_cursor(page_rows[-1].id) if has_more and page_rows else None,
        total_estimate=total,
    )


@router.post(
    "/custom-objectives",
    summary="Create or version a Custom Objective",
    status_code=status.HTTP_201_CREATED,
    responses=problems(401, 403, 404, 409, 422),
)
async def create_custom_objective(
    body: CreateCustomObjective,
    caller: FitModels,
    database: DatabaseDep,
    settings: SettingsDep,
) -> CustomObjective:
    """**201** with the objective, as a `draft` (`WF-702` A1, FR-142).

    201 rather than 202: authoring is not work. The parameters are checked against §4.5's
    ranges and the applicability against the template's, both by the contract, and what is
    written is a declaration. The *certification* is the work, and it is a separate call for
    exactly that reason — FR-146 makes it the evidence, not a side effect of authoring.
    """
    async with database.unit_of_work() as session:
        if body.kind is not ObjectiveKind.TEMPLATE:
            await service.refuse_expression_kind(
                session, settings=settings, workspace_id=caller.workspace_id
            )
        if body.template is None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "A template objective names a template",
                422,
                "Phase 1 ships template objectives only (FR-150), so `template` is "
                "required. §4.5 lists the twelve.",
            )
        row = await service.create_objective(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=body.slug,
            template=body.template,
            params=dict(body.params),
            applicability=body.applicability,
            hessian_strategy=body.hessian_strategy,
            hessian_min=body.hessian_min,
            description=body.description,
        )
        return service.to_objective(row)


@router.get(
    "/custom-objectives/{objective_id}",
    summary="A Custom Objective",
    responses=problems(401, 403, 404, 422),
)
async def get_custom_objective(
    objective_id: UUID, caller: ReadModels, database: DatabaseDep
) -> CustomObjective:
    """**Added to `02` §5.1 with this slice** (FR-166) — see the module docstring."""
    async with database.session() as session:
        return await service.load_objective(
            session, workspace_id=caller.workspace_id, objective_id=objective_id
        )


@router.post(
    "/custom-objectives/{objective_id}/derive",
    summary="Derive gradient and hessian from a loss expression",
    responses=problems(401, 403, 404, 409, 422),
)
async def derive_custom_objective(
    objective_id: UUID,
    caller: FitModels,
    database: DatabaseDep,
    settings: SettingsDep,
) -> CustomObjective:
    """Always refused in Phase 1 with `OBJECTIVE_KIND_NOT_ENABLED` (FR-MODEL-40, 75).

    Built as a refusal rather than left out: FR-150 names this endpoint as one of the
    two that answer that code, and the distinction between "no such concept" and "not until
    Phase 2" is exactly what a 404 would destroy. The return type is the one Phase 2 will
    answer with; nothing reaches it yet.
    """
    async with database.session() as session:
        await service.refuse_expression_kind(
            session, settings=settings, workspace_id=caller.workspace_id
        )


@router.post(
    "/custom-objectives/{objective_id}/certify",
    summary="Run the certificate checks over a Custom Objective",
    responses=problems(401, 403, 404, 409, 422),
)
async def certify_custom_objective(
    objective_id: UUID,
    body: CertifyRequest,
    caller: FitModels,
    database: DatabaseDep,
    response: Response,
) -> Job:
    """**202** with a Job (`WF-702` A2, FR-146).

    202 because §4.7's checks end in a smoke fit: a booster is trained, over a sampled grid,
    and a synchronous endpoint would hold the request open across it. What is answered
    before the Job exists is what can be — the permission, and whether re-certifying would
    move evidence a live decision already rests on.
    """
    async with database.unit_of_work() as session:
        row = await service.certifiable_or_refuse(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            objective_id=objective_id,
        )
        sampling = body.sampling or service.default_sampling(service.to_objective(row))
        job = await job_service.submit(
            session,
            JobKind.OBJECTIVE_CERTIFY,
            {
                **job_identity(caller),
                "objective_id": str(row.id),
                # The resolved grid, not the request's — the worker must certify over the
                # grid this response implies, and re-deriving it there would let a change
                # to the default rule silently change what a queued Job measures.
                "sampling": sampling.model_dump(mode="json"),
            },
            caller.principal,
            workspace_id=caller.workspace_id,
            queue=JobQueue.COMPUTE,
        )
        response.status_code = status.HTTP_202_ACCEPTED
        response.headers["Location"] = f"/api/v1/jobs/{job.id}"
        return job


@router.get(
    "/custom-objectives/{objective_id}/certificate",
    summary="The latest certificate for a Custom Objective",
    responses=problems(401, 403, 404, 422),
)
async def get_certificate(
    objective_id: UUID, caller: ReadModels, database: DatabaseDep
) -> ObjectiveCertificate:
    """**Added to `02` §5.1 with this slice** (FR-166).

    Without it the certificate is produced by a Job and readable nowhere — and it is what
    an approver is asked to read (`06` §4.2 names `objective_certificate` as the evidence).
    """
    async with database.session() as session:
        return await service.load_certificate(
            session, workspace_id=caller.workspace_id, objective_id=objective_id
        )


@router.post(
    "/custom-objectives/{objective_id}/submit",
    summary="Submit a Custom Objective for approval",
    responses=problems(401, 403, 404, 409, 422),
)
async def submit_custom_objective(
    objective_id: UUID,
    body: SubmitCustomObjective,
    caller: SubmitModels,
    database: DatabaseDep,
) -> CustomObjective:
    """`certified → review` (`WF-702` A3, FR-163).

    Gated on `model:submit` for the reason a Model's submission is: putting an artifact in
    front of an approver starts a governed process, and the role that may author is not
    automatically the role that may do that.
    """
    async with database.unit_of_work() as session:
        row, _request = await service.submit_for_review(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            objective_id=objective_id,
            change_summary=body.change_summary,
        )
        return service.to_objective(row)


@router.get(
    "/custom-objectives/{objective_id}/usage",
    summary="What was fitted under this Custom Objective",
    responses=problems(401, 403, 404, 422),
)
async def get_usage(
    objective_id: UUID, caller: ReadModels, database: DatabaseDep
) -> ObjectiveUsage:
    """FR-164's blast radius.

    `rating_versions` and `deployments` are named and always empty in Phase 1 — `03` is not
    built — which is FR-207's staging rule rather than an oversight. The models are
    real, and they are the half that exists to be found.
    """
    async with database.session() as session:
        return await service.usage(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            objective_id=objective_id,
        )
