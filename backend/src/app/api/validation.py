"""Validation reports, acknowledgements, rules and rule sets (`01` §5.1).

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/validation-reports/{id}` | Full report |
| `POST` | `/validation-reports/{id}/results/{rule_id}/acknowledge` | Acknowledge a warn |
| `POST` | `/validation-rules` | Create a custom rule → `draft` (FR-DATA-21) |
| `POST` | `/validation-rules/{id}/dry-run` | **202** Execute against a chosen version |
| `POST` | `/validation-rules/{id}/submit` | Submit for approval |
| `GET`/`PUT` | `/datasets/{slug}/rule-set` | Read / replace the Rule Set |

The acknowledgement route carries the module's sharpest rule: a `warn` may be accepted by
an actuary with a justification, and a `fail` may not be accepted by anyone (`01` §1.3).
"""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.authz import requires
from app.api.deps import Caller, require_caller
from app.api.responses import problems
from app.db.session import Database
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import validation as service
from app.platform import validation_rules as rule_service
from model_schema import (
    Job,
    JobKind,
    Severity,
    ValidationLayer,
    ValidationReport,
    ValidationRule,
    ValidationRuleSet,
)
from model_schema import Permission as Perm

__all__ = ["router"]

router = APIRouter(tags=["validation"])

ReadDatasets = Annotated[Caller, Depends(requires(Perm.DATASET_READ))]
WriteDatasets = Annotated[Caller, Depends(requires(Perm.DATASET_WRITE))]
AcknowledgeWarnings = Annotated[
    Caller, Depends(requires(Perm.DATASET_ACKNOWLEDGE_WARNING))
]
#: The one route whose permission is check-dependent; see `create_rule`.
AuthenticatedCaller = Annotated[Caller, Depends(require_caller)]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


class AcknowledgeRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    justification: Annotated[str, Field(min_length=1)]


class RuleCreate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")]
    layer: ValidationLayer
    check: str
    severity: Severity
    target: dict[str, Any] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    rationale: str = ""


class DryRunRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_version_id: UUID


class RuleSetReplace(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_ids: list[UUID]
    reference_dataset_version_id: UUID | None = None


@router.get(
    "/validation-reports/{report_id}",
    summary="Full validation report",
    responses=problems(401, 403, 404, 422),
)
async def get_report(
    report_id: UUID, caller: ReadDatasets, database: DatabaseDep
) -> ValidationReport:
    async with database.session() as session:
        return await service.load_report(
            session, workspace_id=caller.workspace_id, report_id=report_id
        )


@router.post(
    "/validation-reports/{report_id}/results/{rule_id}/acknowledge",
    status_code=status.HTTP_201_CREATED,
    summary="Acknowledge a validation warning",
    responses=problems(401, 403, 404, 409, 422),
)
async def acknowledge(
    report_id: UUID,
    rule_id: UUID,
    body: AcknowledgeRequest,
    caller: AcknowledgeWarnings,
    database: DatabaseDep,
) -> dict[str, Any]:
    """FR-DATA-17. Actuary only, justified, audited, once per `(report, rule)`."""
    async with database.unit_of_work() as session:
        row = await service.acknowledge(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            report_id=report_id,
            rule_id=rule_id,
            justification=body.justification,
        )
        return {
            "id": str(row.id),
            "report_id": str(row.report_id),
            "rule_id": str(row.rule_id),
            "user_id": str(row.user_id),
            "justification": row.justification,
            "acknowledged_at": row.acknowledged_at.isoformat(),
        }


@router.post(
    "/validation-rules",
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom validation rule",
    responses=problems(401, 403, 409, 422),
)
async def create_rule(
    body: RuleCreate, caller: AuthenticatedCaller, database: DatabaseDep, request: Request
) -> ValidationRule:
    """FR-DATA-21 step 1: authored → `draft`.

    The permission depends on the *check*, which is why it is not on the route: a
    declarative rule needs `dataset:write`, and a `sql` rule needs `admin:manage_settings`
    **instead** (`01` §4.5 step 5). Requiring both would leave no built-in role able to
    author one. The service makes the choice, and it fails closed either way.
    """
    async with database.unit_of_work() as session:
        row = await rule_service.create_rule(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=body.slug,
            layer=body.layer,
            check=body.check,
            severity=body.severity,
            target=body.target,
            params=body.params,
            message=body.message,
            rationale=body.rationale,
            settings=request.app.state.settings,
        )
        return rule_service.to_schema(row)


@router.post(
    "/validation-rules/{rule_id}/dry-run",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Dry-run a rule against a version",
    responses=problems(401, 403, 404, 409, 422),
)
async def dry_run(
    rule_id: UUID,
    body: DryRunRequest,
    caller: WriteDatasets,
    database: DatabaseDep,
    response: Response,
) -> Job:
    """**202**. FR-DATA-21 step 2: a rule cannot be approved until it has run somewhere.

    The dry run is what makes the approval a decision rather than a signature — an approver
    reading a rule's JSON cannot tell whether it selects three rows or three million.
    """
    async with database.unit_of_work() as session:
        rule = await rule_service.load_rule(
            session, workspace_id=caller.workspace_id, rule_id=rule_id
        )
        job = await job_service.submit(
            session,
            JobKind.DATASET_VALIDATE,
            {
                "dataset_version_id": str(body.dataset_version_id),
                "dry_run_rule_id": str(rule.id),
            },
            caller.principal,
            workspace_id=caller.workspace_id,
        )
    response.headers["Location"] = f"/api/v1/jobs/{job.id}"
    return job


@router.post(
    "/validation-rules/{rule_id}/submit",
    summary="Submit a rule for approval",
    responses=problems(401, 403, 404, 409, 422),
)
async def submit_rule(
    rule_id: UUID, caller: WriteDatasets, database: DatabaseDep
) -> ValidationRule:
    """FR-DATA-21 step 3: `draft` → `review`, and only with a dry run attached."""
    async with database.unit_of_work() as session:
        row = await rule_service.submit_for_review(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            rule_id=rule_id,
        )
        return rule_service.to_schema(row)


@router.get(
    "/datasets/{slug}/rule-set",
    summary="Read a dataset's rule set",
    responses=problems(401, 403, 404, 422),
)
async def get_rule_set(
    slug: str, caller: ReadDatasets, database: DatabaseDep
) -> ValidationRuleSet:
    async with database.session() as session:
        dataset = await dataset_service.load_dataset(
            session, workspace_id=caller.workspace_id, slug=slug
        )
        return await rule_service.rule_set_for(
            session, workspace_id=caller.workspace_id, dataset_id=dataset.id, slug=slug
        )


@router.put(
    "/datasets/{slug}/rule-set",
    summary="Replace a dataset's rule set",
    responses=problems(401, 403, 404, 409, 422),
)
async def put_rule_set(
    slug: str, body: RuleSetReplace, caller: WriteDatasets, database: DatabaseDep
) -> ValidationRuleSet:
    """FR-DATA-22: a replace creates a **new rule-set version**.

    Never an edit in place. A Validation Report records the exact `rule_set_version` it
    ran, so mutating a rule set would change what every past report was a report *of*.
    """
    async with database.unit_of_work() as session:
        dataset = await dataset_service.load_dataset(
            session, workspace_id=caller.workspace_id, slug=slug
        )
        return await rule_service.replace_rule_set(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            dataset_id=dataset.id,
            slug=slug,
            rule_ids=body.rule_ids,
            reference_dataset_version_id=body.reference_dataset_version_id,
        )
