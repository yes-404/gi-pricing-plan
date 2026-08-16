"""Dataset versions: validation, profiling, lineage and derivation (`01` §5.1).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/dataset-versions/{id}/validate` | **202** Run validation → Job (FR-DATA-15) |
| `GET` | `/dataset-versions/{id}/validation-reports` | Report history |
| `POST` | `/dataset-versions/{id}/transition` | Enforces `01` §4.2's invariants |
| `GET` | `/dataset-versions/{id}/profile` | Profile artifact (FR-DATA-25) |
| `GET` | `/dataset-versions/{id}/one-ways` | One-way summary (FR-DATA-26) |
| `GET` | `/dataset-versions/{id}/compare` | Profile comparison / PSI (FR-DATA-28) |
| `POST` | `/dataset-versions/{id}/derive` | **202** Sample / split / filter → Job |
| `GET` | `/dataset-versions/{id}/lineage` | Lineage graph (FR-DATA-35) |
| `GET` | `/dataset-versions/{id}/rejected` | Quarantined rows, paged (FR-DATA-7) |

`POST .../transition` is the only route that can reach `validated`, and it cannot do so on
a caller's say-so: it reads the stored report and refuses unless the report passed and
every warning is acknowledged. `01` §1.3 has no override, so neither does this.
"""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authz import requires
from app.api.deps import Caller, job_identity
from app.api.responses import problems
from app.db.models import DatasetVersionRow, IngestionRunRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import profiles as profile_service
from app.platform import validation as validation_service
from model_schema import (
    DatasetSplit,
    DatasetStatus,
    DatasetVersion,
    Job,
    JobKind,
    OneWaySummary,
    OverallOutcome,
    Profile,
    ProfileComparison,
)
from model_schema import Permission as Perm

__all__ = ["router"]

router = APIRouter(prefix="/dataset-versions", tags=["dataset versions"])

ReadDatasets = Annotated[Caller, Depends(requires(Perm.DATASET_READ))]
WriteDatasets = Annotated[Caller, Depends(requires(Perm.DATASET_WRITE))]
ValidateDatasets = Annotated[Caller, Depends(requires(Perm.DATASET_VALIDATE))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


async def _scoped(session: AsyncSession, version_id: UUID, caller: Caller) -> DatasetVersionRow:
    """A version in the caller's workspace, or the same 404 as one that does not exist."""
    row = await session.get(DatasetVersionRow, version_id)
    if row is None or row.workspace_id != caller.workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Dataset version not found", 404, f"No version {version_id}."
        )
    return row


class ValidateRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_set_id: UUID | None = None
    reference_dataset_version_id: UUID | None = None


class TransitionRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    to: DatasetStatus
    report_id: UUID | None = None
    reason: str | None = None


class DeriveRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    operation: str
    params: dict[str, Any] = Field(default_factory=dict)


class ReportSummary(BaseModel):
    """A report's headline, without its body (NFR-DATA-7).

    The history view renders dates and verdicts. Loading fifty full reports to do that is
    the difference between a 500 ms budget met and missed, so the list returns this and
    `GET /validation-reports/{id}` returns the artifact.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    dataset_version_id: UUID
    rule_set_id: UUID
    rule_set_version: int
    job_id: UUID | None
    overall: OverallOutcome
    rule_count: int
    fail_count: int
    warn_count: int
    error_count: int
    unacknowledged_warnings: int
    started_at: Any
    finished_at: Any


@router.post(
    "/{version_id}/validate",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run validation",
    responses=problems(401, 403, 404, 422),
)
async def run_validation(
    version_id: UUID,
    body: ValidateRequest,
    caller: ValidateDatasets,
    database: DatabaseDep,
    response: Response,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> Job:
    """**202** with the Job (FR-DATA-15)."""
    async with database.unit_of_work() as session:
        version = await _scoped(session, version_id, caller)
        job = await job_service.submit(
            session,
            JobKind.DATASET_VALIDATE,
            {
                **job_identity(caller),
                "dataset_version_id": str(version.id),
                "rule_set_id": str(body.rule_set_id) if body.rule_set_id else None,
                "reference_dataset_version_id": (
                    str(body.reference_dataset_version_id)
                    if body.reference_dataset_version_id
                    else None
                ),
            },
            caller.principal,
            workspace_id=caller.workspace_id,
            idempotency_key=idempotency_key,
        )
    response.headers["Location"] = f"/api/v1/jobs/{job.id}"
    return job


@router.get(
    "/{version_id}/validation-reports",
    summary="Validation report history",
    responses=problems(401, 403, 404, 422),
)
async def list_reports(
    version_id: UUID, caller: ReadDatasets, database: DatabaseDep
) -> list[ReportSummary]:
    async with database.session() as session:
        await _scoped(session, version_id, caller)
        rows = await validation_service.reports_for_version(
            session, workspace_id=caller.workspace_id, version_id=version_id
        )
        return [
            ReportSummary(
                id=row.id,
                dataset_version_id=row.dataset_version_id,
                rule_set_id=row.rule_set_id,
                rule_set_version=row.rule_set_version,
                job_id=row.job_id,
                overall=OverallOutcome(row.overall),
                rule_count=row.rule_count,
                fail_count=row.fail_count,
                warn_count=row.warn_count,
                error_count=row.error_count,
                unacknowledged_warnings=await validation_service.unacknowledged_warnings(
                    session, workspace_id=caller.workspace_id, report_id=row.id
                ),
                started_at=row.started_at,
                finished_at=row.finished_at,
            )
            for row in rows
        ]


@router.post(
    "/{version_id}/transition",
    summary="Change a version's status",
    responses=problems(401, 403, 404, 409, 422),
)
async def transition(
    version_id: UUID,
    body: TransitionRequest,
    caller: ValidateDatasets,
    database: DatabaseDep,
) -> DatasetVersion:
    """`01` §4.2's invariants, enforced (FR-DATA-17).

    Reaching `validated` requires a `report_id`, and the report is read here rather than
    trusted: the caller says which report, never whether it passed.
    """
    async with database.unit_of_work() as session:
        await _scoped(session, version_id, caller)
        if body.to is DatasetStatus.VALIDATED:
            if body.report_id is None:
                raise PlatformError(
                    "VALIDATION_HAS_FAILURES",
                    "Validating a version requires the report that validated it",
                    422,
                    "`01` §4.2: a validated version names its validation report. Without "
                    "one there is nothing to check the promotion against.",
                )
            row = await validation_service.promote_using_report(
                session,
                workspace_id=caller.workspace_id,
                actor=caller.principal,
                version_id=version_id,
                report_id=body.report_id,
            )
        elif body.to is DatasetStatus.ARCHIVED:
            row = await dataset_service.archive_version(
                session,
                workspace_id=caller.workspace_id,
                actor=caller.principal,
                version_id=version_id,
                reason=body.reason or "",
            )
        else:
            row = await dataset_service.transition(
                session,
                workspace_id=caller.workspace_id,
                actor=caller.principal,
                version_id=version_id,
                to_status=body.to,
                justification=body.reason,
            )
        return _version_schema(row)


def _version_schema(row: DatasetVersionRow) -> DatasetVersion:
    from app.api.datasets import _version_schema as shared

    return shared(row)


@router.get(
    "/{version_id}/profile", summary="Profile artifact", responses=problems(401, 403, 404, 422)
)
async def get_profile(
    version_id: UUID, caller: ReadDatasets, database: DatabaseDep
) -> Profile:
    """FR-DATA-25. Read, never recomputed (FR-DATA-27)."""
    async with database.session() as session:
        await _scoped(session, version_id, caller)
        return await profile_service.latest_profile(
            session, workspace_id=caller.workspace_id, version_id=version_id
        )


@router.get(
    "/{version_id}/one-ways",
    summary="One-way summary for a column",
    responses=problems(401, 403, 404, 422),
)
async def get_one_way(
    version_id: UUID,
    caller: ReadDatasets,
    database: DatabaseDep,
    column: Annotated[str, Query(min_length=1)],
) -> OneWaySummary:
    """FR-DATA-26, NFR-DATA-4: read from the stored Profile in a single lookup."""
    async with database.session() as session:
        await _scoped(session, version_id, caller)
        return await profile_service.one_way_of(
            session, workspace_id=caller.workspace_id, version_id=version_id, column=column
        )


@router.get(
    "/{version_id}/compare",
    summary="Profile comparison / PSI",
    responses=problems(401, 403, 404, 422),
)
async def compare(
    version_id: UUID,
    caller: ReadDatasets,
    database: DatabaseDep,
    against: Annotated[UUID, Query()],
) -> ProfileComparison:
    """FR-DATA-28. Computed from two stored Profiles, which is why it is cheap enough to
    be a `GET` — neither dataset is read."""
    from pricing_core.data.profile import compare_profiles

    async with database.session() as session:
        current = await _scoped(session, version_id, caller)
        reference = await _scoped(session, against, caller)
        if current.dataset_id != reference.dataset_id:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Profiles can only be compared within one dataset",
                422,
                "FR-DATA-28 compares two versions *of the same Dataset*. A PSI between "
                "unrelated datasets is a number with no interpretation.",
            )
        return compare_profiles(
            await profile_service.latest_profile(
                session, workspace_id=caller.workspace_id, version_id=version_id
            ),
            await profile_service.latest_profile(
                session, workspace_id=caller.workspace_id, version_id=against
            ),
        )


@router.post(
    "/{version_id}/derive",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Derive a version",
    responses=problems(401, 403, 404, 422),
)
async def derive(
    version_id: UUID,
    body: DeriveRequest,
    caller: WriteDatasets,
    database: DatabaseDep,
    response: Response,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> Job:
    """**202**. FR-DATA-33: sample, split, filter or union."""
    async with database.unit_of_work() as session:
        version = await _scoped(session, version_id, caller)
        job = await job_service.submit(
            session,
            JobKind.DATASET_DERIVE,
            {
                **job_identity(caller),
                "parent_version_id": str(version.id),
                "operation": body.operation,
                "params": body.params,
            },
            caller.principal,
            workspace_id=caller.workspace_id,
            idempotency_key=idempotency_key,
        )
    response.headers["Location"] = f"/api/v1/jobs/{job.id}"
    return job


@router.get(
    "/{version_id}/lineage", summary="Lineage graph", responses=problems(401, 403, 404, 422)
)
async def lineage(
    version_id: UUID,
    caller: ReadDatasets,
    database: DatabaseDep,
    direction: Annotated[str, Query(pattern="^(up|down|both)$")] = "both",
) -> dict[str, Any]:
    """FR-DATA-35."""
    async with database.session() as session:
        await _scoped(session, version_id, caller)
        graph = await dataset_service.lineage_of(
            session, workspace_id=caller.workspace_id, version_id=version_id
        )
    if direction == "up":
        return {key: value for key, value in graph.items() if key != "descendants"}
    if direction == "down":
        return {key: value for key, value in graph.items() if key != "ancestors"}
    return graph


@router.get(
    "/{version_id}/rejected",
    summary="Quarantined rows",
    responses=problems(401, 403, 404, 422),
)
async def rejected_rows(
    version_id: UUID, caller: ReadDatasets, database: DatabaseDep
) -> dict[str, Any]:
    """FR-DATA-7: the rows ingestion could not accept, with the reason each was refused.

    A sample rather than the full quarantine. The reject file itself is a blob; this is the
    screen that answers "why is my row count short?", and a hundred examples answer it as
    well as a million.
    """
    async with database.session() as session:
        version = await _scoped(session, version_id, caller)
        run = (
            await session.execute(
                select(IngestionRunRow).where(
                    IngestionRunRow.id == version.ingestion_run_id
                )
            )
        ).scalar_one_or_none()
    if run is None:
        raise PlatformError(
            "NOT_FOUND",
            "This version has no ingestion run",
            404,
            "A derived version has no rejected rows of its own — look at the parent it "
            "was derived from.",
        )
    return {
        "rows_read": run.rows_read,
        "rows_written": run.rows_written,
        "rows_rejected": run.rows_rejected,
        # Computed from what was read, not stored: a rate and its numerator that can
        # disagree is a number somebody will quote in a meeting.
        "reject_rate": run.rows_rejected / run.rows_read if run.rows_read else 0.0,
        "sample": run.reject_sample,
    }


class SplitRequest(BaseModel):
    """Record a named split over parts that already exist (FR-DATA-36)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=64)
    method: str
    seed: int
    parts: dict[str, UUID] = Field(min_length=2)
    params: dict[str, Any] = Field(default_factory=dict)


@router.post(
    "/{version_id}/splits",
    status_code=status.HTTP_201_CREATED,
    summary="Record a named split",
    responses=problems(401, 403, 404, 409, 422),
)
async def record_split(
    version_id: UUID,
    body: SplitRequest,
    caller: WriteDatasets,
    database: DatabaseDep,
) -> DatasetSplit:
    """FR-DATA-36: the split is recorded on the **parent**, over parts already derived.

    Synchronous, unlike `/derive`: this writes one row referencing versions that exist. The
    expensive half — partitioning the rows — happened in the `dataset.derive` Jobs that
    produced the parts.

    The service function has existed since W4 and had no route, so a split could be created
    only from inside the platform. `02`'s `split_ref` needs one that a caller can name,
    which is what made the gap visible.
    """
    async with database.unit_of_work() as session:
        version = await _scoped(session, version_id, caller)
        row = await dataset_service.record_split(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            parent_version_id=version.id,
            name=body.name,
            method=body.method,
            seed=body.seed,
            parts=body.parts,
            params=body.params,
        )
        return dataset_service.to_split(row)


@router.get(
    "/{version_id}/splits",
    summary="Splits recorded on this version",
    responses=problems(401, 403, 404, 422),
)
async def list_splits(
    version_id: UUID,
    caller: ReadDatasets,
    database: DatabaseDep,
) -> list[DatasetSplit]:
    """Every split on this version, so a Model Spec can cite one by id (FR-DATA-36)."""
    async with database.session() as session:
        version = await _scoped(session, version_id, caller)
        rows = await dataset_service.list_splits(
            session, workspace_id=caller.workspace_id, parent_version_id=version.id
        )
        return [dataset_service.to_split(row) for row in rows]
