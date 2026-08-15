"""Reference tables (`01` §5.1, FR-DATA-29..32).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/reference-tables` | Declare a table |
| `POST` | `/reference-tables/{slug}/versions` | Load a new version (FR-DATA-29) |
| `POST` | `/reference-tables/{slug}/versions/{version}/publish` | Make it pinnable |
| `GET` | `/reference-tables/{slug}/lookup` | Point lookup for debugging (FR-DATA-31) |

The lookup endpoint is **for debugging**, and its docstring says so where a reader will
see it. Rating resolves a reference through a pinned version id (FR-DATA-32); an endpoint
that answers "what does the latest table say?" is the wrong thing to build a rating on,
because "latest" is a different answer each month.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.authz import requires
from app.api.deps import Caller
from app.api.responses import problems
from app.db.session import Database
from app.platform import reference as service
from model_schema import Permission as Perm

__all__ = ["router"]

router = APIRouter(prefix="/reference-tables", tags=["reference data"])

ReadDatasets = Annotated[Caller, Depends(requires(Perm.DATASET_READ))]
ManageReference = Annotated[Caller, Depends(requires(Perm.ADMIN_MANAGE_SETTINGS))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


class TableCreate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")]
    key_columns: Annotated[list[str], Field(min_length=1)]
    payload_columns: list[str] = Field(default_factory=list)
    description: str | None = None


class ReferenceRowIn(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str
    payload: dict[str, Any] = Field(default_factory=dict)
    effective_from: date
    #: `None` means "still in force". The interval is half-open, so a row ending on a date
    #: does not cover that date — which is what makes consecutive versions abut cleanly.
    effective_to: date | None = None


class VersionLoad(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rows: Annotated[list[ReferenceRowIn], Field(min_length=1)]
    source_note: str | None = None


class VersionView(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: str
    version: int
    status: str
    row_count: int


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Declare a reference table",
    responses=problems(401, 403, 409, 422),
)
async def create_table(
    body: TableCreate, caller: ManageReference, database: DatabaseDep
) -> dict[str, Any]:
    async with database.unit_of_work() as session:
        row = await service.create_table(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=body.slug,
            key_columns=body.key_columns,
            payload_columns=body.payload_columns,
            description=body.description,
        )
        return {
            "id": str(row.id),
            "slug": row.slug,
            "key_columns": row.key_columns,
            "payload_columns": row.payload_columns,
        }


@router.post(
    "/{slug}/versions",
    status_code=status.HTTP_201_CREATED,
    summary="Load a reference table version",
    responses=problems(401, 403, 404, 409, 422),
)
async def load_version(
    slug: str, body: VersionLoad, caller: ManageReference, database: DatabaseDep
) -> VersionView:
    """FR-DATA-29. Loaded whole, into `draft`; publish it to make it pinnable."""
    async with database.unit_of_work() as session:
        row = await service.load_version(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=slug,
            rows=[entry.model_dump() for entry in body.rows],
            source_note=body.source_note,
        )
        return VersionView(
            id=row.id, slug=slug, version=row.version, status=row.status,
            row_count=len(body.rows),
        )


@router.post(
    "/{slug}/versions/{version}/publish",
    summary="Publish a reference table version",
    responses=problems(401, 403, 404, 422),
)
async def publish_version(
    slug: str, version: int, caller: ManageReference, database: DatabaseDep
) -> VersionView:
    async with database.unit_of_work() as session:
        row = await service.publish_version(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=slug,
            version=version,
        )
        return VersionView(
            id=row.id, slug=slug, version=row.version, status=row.status, row_count=0
        )


@router.get(
    "/{slug}/lookup",
    summary="Point lookup, as at a date",
    responses=problems(401, 403, 404, 422),
)
async def lookup(
    slug: str,
    caller: ReadDatasets,
    database: DatabaseDep,
    key: Annotated[str, Query(min_length=1)],
    as_at: Annotated[date, Query()],
    version: Annotated[int | None, Query(ge=1)] = None,
) -> dict[str, Any]:
    """**For debugging** (FR-DATA-31).

    Rating pins a reference version id (FR-DATA-32) and never resolves "the latest" at
    scoring time. This endpoint exists to answer "what does this table say about this key
    on this date?" when a quote looks wrong.
    """
    async with database.session() as session:
        return await service.lookup(
            session,
            workspace_id=caller.workspace_id,
            slug=slug,
            key=key,
            as_at=as_at,
            version=version,
        )
