"""Datasets, sources and dataset versions (`01` §5.1).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/sources` | Register a Source (FR-DATA-1) |
| `GET` | `/sources` | List sources, credentials redacted |
| `POST` | `/datasets` | Create a Dataset with its Data Dictionary |
| `GET` | `/datasets` | List / filter |
| `GET` | `/datasets/{slug}` | Detail with `latest_version` |
| `PUT` | `/datasets/{slug}/dictionary` | Replace the Data Dictionary, audited |
| `POST` | `/datasets/{slug}/versions` | **202** Start an Ingestion Run → Job |
| `GET` | `/datasets/{slug}/versions/{version}` | Version detail |
| `PATCH` | `/datasets/{slug}/versions/{version}/schema` | Correct inferred schema while `draft` |

**A Source never returns its credentials** (FR-DATA-1, `07` FR-PLAT-25). The row holds a
reference to a platform secret and nothing else, so there is no redaction step that could
be forgotten — the response shape simply has nowhere to put one.
"""

from __future__ import annotations

import dataclasses
from typing import Annotated, Any
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authz import requires
from app.api.deps import Caller, job_identity
from app.api.pagination import (
    COUNT_CAP,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    Page,
    decode_cursor,
    decode_int_cursor,
    encode_cursor,
)
from app.api.responses import problems
from app.data import ingestion
from app.data.formats import read_tabular
from app.db.models import DatasetRow, DatasetVersionRow, SourceRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import datasets as service
from app.platform import jobs as job_service
from model_schema import (
    DataDictionaryEntry,
    Dataset,
    DatasetVersion,
    Job,
    JobKind,
    RecordGrain,
    SourceKind,
)
from model_schema import (
    Permission as Perm,
)
from pricing_core.data.ingest import infer_schema, normalise_columns

__all__ = ["router"]

router = APIRouter(tags=["datasets"])

ReadDatasets = Annotated[Caller, Depends(requires(Perm.DATASET_READ))]
WriteDatasets = Annotated[Caller, Depends(requires(Perm.DATASET_WRITE))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]

_SLUG = r"^[a-z0-9][a-z0-9-]{1,62}$"


class SourceCreate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Annotated[str, Field(pattern=_SLUG)]
    kind: SourceKind
    config: dict[str, Any] = Field(default_factory=dict)
    #: A *reference* to a platform secret, never the secret (FR-DATA-1, FR-PLAT-25). The
    #: field is a string key into the secret store; a caller who posts an actual password
    #: here has stored a password in a database column, which is why the name says `_ref`.
    credentials_secret_ref: str | None = None


class SourceView(BaseModel):
    """What a Source looks like from outside. Note what is absent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: str
    kind: SourceKind
    config: dict[str, Any]
    has_credentials: bool


class DatasetCreate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Annotated[str, Field(pattern=_SLUG)]
    name: str = ""
    description: str | None = None
    line_of_business: str | None = None
    territory: str | None = None
    currency: Annotated[str | None, Field(pattern=r"^[A-Z]{3}$")] = None
    default_record_grain: RecordGrain | None = None
    data_dictionary: dict[str, DataDictionaryEntry] = Field(default_factory=dict)


class DictionaryUpdate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    data_dictionary: dict[str, DataDictionaryEntry]


class VersionCreate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    #: The SHA-256 of an already-uploaded blob. The file does not travel through this
    #: endpoint: a ten-gigabyte parquet through the API process ties up a worker for the
    #: length of the upload. `POST /blobs/upload-url` first, then this.
    blob: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    filename: str = "upload.csv"
    source_id: UUID | None = None
    recipe: list[dict[str, Any]] = Field(default_factory=list)


class SchemaCorrection(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    table: str
    #: Column name to target dtype, e.g. `{"policy_id": "string"}`. A recast, never a
    #: rename: every name must already exist in the table.
    columns: dict[str, str]


@router.post(
    "/sources",
    status_code=status.HTTP_201_CREATED,
    summary="Register a source",
    responses=problems(401, 403, 409, 422),
)
async def create_source(
    body: SourceCreate, caller: WriteDatasets, database: DatabaseDep
) -> SourceView:
    """FR-DATA-1."""
    async with database.unit_of_work() as session:
        row = await service.create_source(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=body.slug,
            kind=body.kind,
            config=body.config,
            credentials_secret_ref=body.credentials_secret_ref,
        )
        return _source_view(row)


def _source_view(row: SourceRow) -> SourceView:
    return SourceView(
        id=row.id,
        slug=row.slug,
        kind=SourceKind(row.kind),
        config=row.config,
        # A boolean, not the reference. Whether a secret is configured is operationally
        # useful; which secret it is, is not the caller's business.
        has_credentials=row.credentials_secret_ref is not None,
    )


@router.post(
    "/sources/{source_id}/preview",
    summary="Preview a source without creating a version",
    responses=problems(401, 403, 404, 413, 422),
)
async def preview_source(
    source_id: UUID,
    caller: WriteDatasets,
    database: DatabaseDep,
    file: Annotated[UploadFile, File()],
    rows: Annotated[int, Query(ge=1, le=200)] = 20,
) -> dict[str, Any]:
    """First N rows and the inferred schema, **without creating a Dataset Version**.

    The point is that it is free to be wrong. Inference guesses — a zero-padded policy id
    reads as an integer, a European date reads as American — and an analyst needs to see
    that before a version exists, because a version is immutable and the only remedy after
    the fact is another one.

    Nothing is stored: no blob, no version, no ingestion run. A preview that left a trace
    would make "just have a look at this file" an audited act, and people would stop
    looking.
    """
    async with database.session() as session:
        source = (
            await session.execute(
                select(SourceRow).where(
                    SourceRow.workspace_id == caller.workspace_id,
                    SourceRow.id == source_id,
                )
            )
        ).scalar_one_or_none()
    if source is None:
        raise PlatformError("NOT_FOUND", "Source not found", 404, f"No source {source_id}.")

    frame = read_tabular(await file.read(), file.filename or "upload.csv")
    mapping = normalise_columns(frame.columns)
    frame = frame.rename(mapping.rename_map)
    inferred = infer_schema(frame)

    return {
        "source_id": str(source_id),
        "row_count_in_sample": frame.height,
        "columns": [dataclasses.asdict(column) for column in inferred.columns],
        "candidate_keys": list(inferred.candidate_keys),
        # The original headers, so an analyst can see what `Policy ID` became. A silent
        # rename is the one thing more confusing than a rejected file.
        "source_names": mapping.source_names,
        "rows": frame.head(rows).to_dicts(),
    }


@router.get("/sources", summary="List sources", responses=problems(401, 403))
async def list_sources(caller: ReadDatasets, database: DatabaseDep) -> list[SourceView]:
    async with database.session() as session:
        rows = (
            await session.execute(
                select(SourceRow)
                .where(
                    SourceRow.workspace_id == caller.workspace_id,
                    SourceRow.archived_at.is_(None),
                )
                .order_by(SourceRow.slug)
            )
        ).scalars()
        return [_source_view(row) for row in rows]


@router.post(
    "/datasets",
    status_code=status.HTTP_201_CREATED,
    summary="Create a dataset",
    responses=problems(401, 403, 409, 422),
)
async def create_dataset(
    body: DatasetCreate, caller: WriteDatasets, database: DatabaseDep
) -> Dataset:
    async with database.unit_of_work() as session:
        row = await service.create_dataset(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=body.slug,
            name=body.name,
            description=body.description,
            line_of_business=body.line_of_business,
            territory=body.territory,
            currency=body.currency,
            default_record_grain=body.default_record_grain,
            data_dictionary=body.data_dictionary,
        )
        return service.to_schema(row)


@router.get("/datasets", summary="List datasets", responses=problems(400, 401, 403, 422))
async def list_datasets(
    caller: ReadDatasets,
    database: DatabaseDep,
    line_of_business: str | None = None,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
) -> Page[Dataset]:
    after = decode_cursor(cursor)
    conditions = [DatasetRow.workspace_id == caller.workspace_id]
    if line_of_business is not None:
        conditions.append(DatasetRow.line_of_business == line_of_business)

    query = select(DatasetRow).where(*conditions).order_by(DatasetRow.id.desc()).limit(limit + 1)
    if after is not None:
        query = query.where(DatasetRow.id < after)

    async with database.session() as session:
        rows = list((await session.execute(query)).scalars())
        total = (
            await session.execute(
                select(func.count()).select_from(
                    select(DatasetRow.id).where(*conditions).limit(COUNT_CAP).subquery()
                )
            )
        ).scalar_one()

    has_more = len(rows) > limit
    page_rows = rows[:limit]
    return Page[Dataset](
        items=[service.to_schema(row) for row in page_rows],
        next_cursor=encode_cursor(page_rows[-1].id) if has_more and page_rows else None,
        total_estimate=int(total),
    )


async def _latest_version(session: AsyncSession, dataset_id: UUID) -> int | None:
    latest: int | None = (
        await session.execute(
            select(func.max(DatasetVersionRow.version)).where(
                DatasetVersionRow.dataset_id == dataset_id
            )
        )
    ).scalar_one_or_none()
    return latest


@router.get(
    "/datasets/{slug}", summary="Dataset detail", responses=problems(401, 403, 404, 422)
)
async def get_dataset(slug: str, caller: ReadDatasets, database: DatabaseDep) -> Dataset:
    async with database.session() as session:
        row = await service.load_dataset(
            session, workspace_id=caller.workspace_id, slug=slug
        )
        return service.to_schema(row, latest_version=await _latest_version(session, row.id))


@router.put(
    "/datasets/{slug}/dictionary",
    summary="Replace the data dictionary",
    responses=problems(401, 403, 404, 422),
)
async def put_dictionary(
    slug: str, body: DictionaryUpdate, caller: WriteDatasets, database: DatabaseDep
) -> Dataset:
    """A replace, audited with before and after (NFR-DATA-8)."""
    async with database.unit_of_work() as session:
        row = await service.update_dictionary(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=slug,
            entries=body.data_dictionary,
        )
        return service.to_schema(row)


@router.post(
    "/datasets/{slug}/versions",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start an ingestion run",
    responses=problems(401, 403, 404, 422),
)
async def start_ingestion(
    slug: str,
    body: VersionCreate,
    caller: WriteDatasets,
    database: DatabaseDep,
    response: Response,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> Job:
    """**202** with the Job (`00` §5.1 R1, FR-DATA-2).

    The version row is created by the worker, not here: a version that exists before its
    data does is a version something can be fitted on. What this returns is the Job, and
    `Location` points at it.
    """
    async with database.unit_of_work() as session:
        dataset = await service.load_dataset(
            session, workspace_id=caller.workspace_id, slug=slug
        )
        job = await job_service.submit(
            session,
            JobKind.DATASET_INGEST,
            {
                **job_identity(caller),
                "dataset_id": str(dataset.id),
                "blob": body.blob,
                "filename": body.filename,
                "source_id": str(body.source_id) if body.source_id else None,
                "recipe": body.recipe,
            },
            caller.principal,
            workspace_id=caller.workspace_id,
            idempotency_key=idempotency_key,
        )
    response.headers["Location"] = f"/api/v1/jobs/{job.id}"
    return job


async def _load_version(
    session: AsyncSession, *, workspace_id: UUID, slug: str, version: int
) -> DatasetVersionRow:
    dataset = await service.load_dataset(session, workspace_id=workspace_id, slug=slug)
    row: DatasetVersionRow | None = (
        await session.execute(
            select(DatasetVersionRow).where(
                DatasetVersionRow.dataset_id == dataset.id,
                DatasetVersionRow.version == version,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "Dataset version not found",
            404,
            f"Dataset {slug!r} has no version {version}.",
        )
    return row


@router.get(
    "/datasets/{slug}/versions",
    summary="Version timeline",
    responses=problems(400, 401, 403, 404, 422),
)
async def list_versions(
    slug: str,
    caller: ReadDatasets,
    database: DatabaseDep,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
) -> Page[DatasetVersion]:
    """The timeline `01` §5.3's dataset view renders.

    Newest first, because a timeline is read from the top and a dataset refreshed monthly
    for ten years has a hundred and twenty versions. Cursor-paginated on the version number
    rather than the id: version is unique per dataset, monotonic, and the thing a reader is
    actually ordering by.
    """
    async with database.session() as session:
        dataset = await service.load_dataset(
            session, workspace_id=caller.workspace_id, slug=slug
        )
        conditions = [DatasetVersionRow.dataset_id == dataset.id]
        if cursor is not None:
            after = decode_int_cursor(cursor)
            if after is not None:
                conditions.append(DatasetVersionRow.version < after)

        rows = list(
            (
                await session.execute(
                    select(DatasetVersionRow)
                    .where(*conditions)
                    .order_by(DatasetVersionRow.version.desc())
                    .limit(limit + 1)
                )
            ).scalars()
        )
        total = (
            await session.execute(
                select(func.count()).select_from(
                    select(DatasetVersionRow.id)
                    .where(DatasetVersionRow.dataset_id == dataset.id)
                    .limit(COUNT_CAP)
                    .subquery()
                )
            )
        ).scalar_one()

    has_more = len(rows) > limit
    page = rows[:limit]
    return Page[DatasetVersion](
        items=[_version_schema(row) for row in page],
        next_cursor=encode_cursor(page[-1].version) if has_more and page else None,
        total_estimate=int(total),
    )


@router.get(
    "/datasets/{slug}/versions/{version}",
    summary="Dataset version detail",
    responses=problems(401, 403, 404, 422),
)
async def get_version(
    slug: str, version: int, caller: ReadDatasets, database: DatabaseDep
) -> DatasetVersion:
    async with database.session() as session:
        row = await _load_version(
            session, workspace_id=caller.workspace_id, slug=slug, version=version
        )
        return _version_schema(row)


def _version_schema(row: DatasetVersionRow) -> DatasetVersion:
    return DatasetVersion.model_validate(
        {
            "id": row.id,
            "dataset_id": row.dataset_id,
            "workspace_id": row.workspace_id,
            "version": row.version,
            "status": row.status,
            "kind": row.kind,
            "tables": row.tables,
            "source_id": row.source_id,
            "source_fingerprint": row.source_fingerprint,
            "ingestion_run_id": row.ingestion_run_id,
            "preparation_recipe_id": row.preparation_recipe_id,
            "period_from": row.period_from,
            "period_to": row.period_to,
            "totals": row.totals,
            "validation_report_id": row.validation_report_id,
            "profile_id": row.profile_id,
            "derived_from": row.derived_from,
            "library_versions": row.library_versions,
            "created_at": row.created_at,
        }
    )


@router.patch(
    "/datasets/{slug}/versions/{version}/schema",
    summary="Correct the inferred schema",
    responses=problems(401, 403, 404, 409, 422),
)
async def patch_schema(
    slug: str,
    version: int,
    body: SchemaCorrection,
    caller: WriteDatasets,
    database: DatabaseDep,
    request: Request,
) -> DatasetVersion:
    """FR-DATA-4: correctable **while `draft` only**.

    Once a version leaves `draft` its schema is part of what was validated and what a model
    may be fitted on. Editing it afterwards would silently change the meaning of a report
    that has already been signed off, which is the immutability ID-1 exists to prevent.
    """
    async with database.unit_of_work() as session:
        row = await _load_version(
            session, workspace_id=caller.workspace_id, slug=slug, version=version
        )
        if row.status != "draft":
            raise PlatformError(
                "DATASET_VERSION_IMMUTABLE",
                "The schema can only be corrected while the version is draft",
                409,
                f"This version is {row.status!r}. FR-DATA-4 allows schema correction in "
                "`draft` only — a later edit would change what an existing validation "
                "report was about.",
            )
        corrected = await ingestion.correct_schema(
            session,
            request.app.state.blob_store,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            version_id=row.id,
            table=body.table,
            columns=body.columns,
        )
        return _version_schema(corrected)
