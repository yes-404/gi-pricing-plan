"""Custom Metrics over HTTP (`02` §5.1, FR-MODEL-45, 103, 104, 105, 108).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/custom-metrics` | **201** Create or version a metric → `draft` (FR-MODEL-45, 103) |
| `GET` | `/custom-metrics/{id}` | The metric and its lifecycle (FR-MODEL-108) |
| `POST` | `/custom-metrics/{id}/certify` | **202** Run §4.13's checks → Job (FR-MODEL-105) |
| `GET` | `/custom-metrics/{id}/certificate` | The latest certificate (FR-MODEL-108) |
| `POST` | `/custom-metrics/{id}/submit` | Submit for approval (FR-MODEL-45's lifecycle) |
| `GET` | `/custom-metrics/{id}/usage` | Blast radius (FR-MODEL-108) |

Six routes, not `custom_objectives.py`'s seven: a metric has no `expression` path to refuse
— FR-MODEL-103 admits `kind: template` only, the same as an objective in Phase 1, but
`/derive` is `custom-objectives`' own declared refusal (FR-MODEL-75) and §5.1's table
carries no `/custom-metrics/{id}/derive` row to parallel it.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.authz import requires
from app.api.deps import Caller, job_identity
from app.api.responses import problems
from app.db.session import Database
from app.errors import PlatformError
from app.platform import jobs as job_service
from app.platform import metrics as service
from app.platform.metrics import MetricUsage
from model_schema import (
    Applicability,
    CustomMetric,
    Job,
    JobKind,
    JobQueue,
    MetricCertificate,
    MetricDirection,
    ObjectiveKind,
    ObjectiveTemplate,
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


class CreateCustomMetric(BaseModel):
    """FR-MODEL-45's artifact. Every range and rule is `CustomMetric`'s, not this one's.

    `kind` is here for `CreateCustomObjective`'s reason: a caller asking for an
    `expression` metric is *answered* — refused by the contract's own
    `_only_templates_are_built` validator with a 422 that names FR-MODEL-103, rather than
    silently forbidding the field and leaving them reading a 422 about an unexpected key.
    """

    model_config = ConfigDict(extra="forbid")

    slug: Slug
    kind: ObjectiveKind = ObjectiveKind.TEMPLATE
    template: ObjectiveTemplate | None = None
    #: `int | float`, `CustomMetric.params`'s own type — a money-kind template parameter
    #: (`capped_gamma.cap`) must arrive as an integer minor-unit amount (`CLAUDE.md` §7), and
    #: a narrower `dict[str, float]` here would coerce it to a float before the contract's own
    #: `TemplateParameter.check` ever saw it, turning a valid request into a 422 the caller
    #: cannot fix by re-reading §4.5.
    params: dict[str, int | float] = Field(default_factory=dict)
    #: Omitted means the template's own (§4.5). An author may narrow it and never widen it.
    applicability: Applicability | None = None
    #: FR-MODEL-104: no default. A metric with no declared direction is not a metric an
    #: early-stopping loop or a comparison screen can use, and a silent default would pick
    #: one on the author's behalf for every template, most of which are not `lower_is_better`.
    direction: MetricDirection
    description: str | None = None


class SubmitCustomMetric(BaseModel):
    """A change summary, or nothing.

    Unlike `custom_objectives.SubmitCustomObjective`, `change_summary` is **not**
    `min_length=1`-required here, and the parameter default is an empty instance: a `draft`
    metric's submit is refused by the lifecycle-transition check (FR-MODEL-105) before
    `approvals.submit`'s own non-empty check is ever reached, so requiring a body at the
    FastAPI layer would turn that 409 into a 422 about a field the caller never gets to
    matter for. A `certified` metric's submit still needs a real summary — `approvals.submit`
    enforces that once the transition passes.
    """

    model_config = ConfigDict(extra="forbid")

    change_summary: str = ""


#: A shared default instance rather than a call in the route's own default (B008): the
#: model has no mutable state, so one instance answers every bodyless submit the same way.
_EMPTY_SUBMIT = SubmitCustomMetric()


@router.post(
    "/custom-metrics",
    summary="Create or version a Custom Metric",
    status_code=status.HTTP_201_CREATED,
    responses=problems(401, 403, 404, 409, 422),
)
async def create_custom_metric(
    body: CreateCustomMetric,
    caller: FitModels,
    database: DatabaseDep,
) -> CustomMetric:
    """**201** with the metric, as a `draft` (FR-MODEL-45, 103).

    201 rather than 202, `custom_objectives.create_custom_objective`'s reason: authoring is
    not work, and the parameters are checked against §4.5's ranges by the contract at write
    time. The *certification* — §4.13's checks — is the work, and it is a separate call.
    """
    async with database.unit_of_work() as session:
        if body.template is None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "A template metric names a template",
                422,
                "Phase 1 ships template metrics only (FR-MODEL-103), so `template` is "
                "required. §4.5 lists the twelve.",
            )
        row = await service.create(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=body.slug,
            template=body.template,
            params=dict(body.params),
            applicability=body.applicability,
            direction=body.direction,
            description=body.description,
        )
        return service.to_metric(row)


@router.get(
    "/custom-metrics/{metric_id}",
    summary="A Custom Metric",
    responses=problems(401, 403, 404, 422),
)
async def get_custom_metric(
    metric_id: UUID, caller: ReadModels, database: DatabaseDep
) -> CustomMetric:
    async with database.session() as session:
        return await service.load_metric(
            session, workspace_id=caller.workspace_id, metric_id=metric_id
        )


@router.post(
    "/custom-metrics/{metric_id}/certify",
    summary="Run the certificate checks over a Custom Metric",
    responses=problems(401, 403, 404, 409, 422),
)
async def certify_custom_metric(
    metric_id: UUID,
    caller: FitModels,
    database: DatabaseDep,
    response: Response,
) -> Job:
    """**202** with a Job (FR-MODEL-105).

    202 because §4.13's checks end in a smoke evaluation over a sampled grid —
    `certify_custom_objective`'s reason, unchanged. Unlike the objective's route, there is
    no request body: `certify_metric` samples a fixed internal grid rather than one a
    caller supplies, so there is nothing a body could name.
    """
    async with database.unit_of_work() as session:
        row = await service.certifiable_or_refuse(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            metric_id=metric_id,
        )
        job = await job_service.submit(
            session,
            JobKind.METRIC_CERTIFY,
            {**job_identity(caller), "metric_id": str(row.id)},
            caller.principal,
            workspace_id=caller.workspace_id,
            queue=JobQueue.COMPUTE,
        )
        response.status_code = status.HTTP_202_ACCEPTED
        response.headers["Location"] = f"/api/v1/jobs/{job.id}"
        return job


@router.get(
    "/custom-metrics/{metric_id}/certificate",
    summary="The latest certificate for a Custom Metric",
    responses=problems(401, 403, 404, 422),
)
async def get_metric_certificate(
    metric_id: UUID, caller: ReadModels, database: DatabaseDep
) -> MetricCertificate:
    async with database.session() as session:
        return await service.load_certificate(
            session, workspace_id=caller.workspace_id, metric_id=metric_id
        )


@router.post(
    "/custom-metrics/{metric_id}/submit",
    summary="Submit a Custom Metric for approval",
    responses=problems(401, 403, 404, 409, 422),
)
async def submit_custom_metric(
    metric_id: UUID,
    caller: SubmitModels,
    database: DatabaseDep,
    # Defaulted, not a bare `SubmitCustomMetric`: every field of the model is itself
    # optional, but FastAPI still treats an un-defaulted Pydantic body parameter as a
    # required part of the request — a bodyless POST would 422 on "Field required"
    # before the service ever got to answer the real question, which is FR-MODEL-105's
    # 409 for a `draft` metric.
    body: SubmitCustomMetric = _EMPTY_SUBMIT,
) -> CustomMetric:
    """`certified → review` (FR-MODEL-45's lifecycle).

    Gated on `model:submit`, `submit_custom_objective`'s reason: putting an artifact in
    front of an approver starts a governed process, and the role that may author is not
    automatically the role that may do that.
    """
    async with database.unit_of_work() as session:
        row, _request = await service.submit(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            metric_id=metric_id,
            change_summary=body.change_summary,
        )
        return service.to_metric(row)


@router.get(
    "/custom-metrics/{metric_id}/usage",
    summary="What was fitted under this Custom Metric",
    responses=problems(401, 403, 404, 422),
)
async def get_metric_usage(
    metric_id: UUID, caller: ReadModels, database: DatabaseDep
) -> MetricUsage:
    """FR-MODEL-108's blast radius."""
    async with database.session() as session:
        return await service.usage(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            metric_id=metric_id,
        )
