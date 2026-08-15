"""Reference tables (`01` §5.1, FR-DATA-29..32).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/reference-tables` | Declare a table |
| `POST` | `/reference-tables/{slug}/versions` | Load a new version (FR-DATA-29) |
| `POST` | `/reference-tables/{slug}/versions/{version}/publish` | Make it pinnable |
| `GET` | `/reference-tables` | List declared tables |
| `GET` | `/reference-tables/{slug}/versions` | The version timeline |
| `GET` | `/reference-tables/{slug}/versions/{version}/rows` | Rows, optionally as at a date |
| `GET` | `/reference-tables/{slug}/lookup` | Point lookup for debugging (FR-DATA-31) |

The three read routes were added in W6a. `01` §5.3 asks the `/reference` view for a table
list, a version timeline and an effective-date viewer, and §5.1 declared none of them —
so the endpoint audit, which compares the spec's table against the published contract,
saw a complete surface. An endpoint missing from **both** is invisible to it.

The lookup endpoint is **for debugging**, and its docstring says so where a reader will
see it. Rating resolves a reference through a pinned version id (FR-DATA-30); an endpoint
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
from model_schema import (
    ReferenceLookup,
    ReferenceRow,
    ReferenceTable,
    ReferenceTableVersion,
)

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
) -> ReferenceTable:
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
        # The schema type, not a hand-built dict: `CLAUDE.md` §2's rule is that a shape
        # crossing the boundary is defined once. The dict published `additionalProperties`
        # to the contract, which generates a TypeScript type a client cannot read a field
        # from — the frontend would have had to declare the shape a second time.
        return service.to_table_schema(row)


@router.post(
    "/{slug}/versions",
    status_code=status.HTTP_201_CREATED,
    summary="Load a reference table version",
    responses=problems(401, 403, 404, 409, 422),
)
async def load_version(
    slug: str, body: VersionLoad, caller: ManageReference, database: DatabaseDep
) -> ReferenceTableVersion:
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
        # The real covered period, not `(len(rows), None, None)`: a load response that
        # said `covers_from: null` for a version that covers 2026 is the same lie the
        # publish response used to tell about its row count, and a client cannot tell a
        # fabricated null from a genuine one.
        return await service.version_view(
            session, workspace_id=caller.workspace_id, slug=slug, version=row.version
        )


@router.post(
    "/{slug}/versions/{version}/publish",
    summary="Publish a reference table version",
    responses=problems(401, 403, 404, 422),
)
async def publish_version(
    slug: str, version: int, caller: ManageReference, database: DatabaseDep
) -> ReferenceTableVersion:
    async with database.unit_of_work() as session:
        row = await service.publish_version(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            slug=slug,
            version=version,
        )
        # Was `row_count=0` regardless — a published version's own response said it had
        # no rows, and a client rendering it would have shown exactly that.
        return await service.version_view(
            session, workspace_id=caller.workspace_id, slug=slug, version=row.version
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
) -> ReferenceLookup:
    """**For debugging** (FR-DATA-31).

    Rating pins a reference version id (FR-DATA-30) and never resolves "the latest" at
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


@router.get(
    "",
    summary="List declared reference tables",
    responses=problems(401, 403, 422),
)
async def list_tables(caller: ReadDatasets, database: DatabaseDep) -> list[ReferenceTable]:
    """`01` §5.3's table list.

    Not paginated: a workspace has tens of reference tables, not thousands, and a cursor
    on a list this size is machinery with nothing to do. Each row carries
    `latest_published_version`, which is null while every version is a draft — the state
    that decides whether the table can be pinned at all.
    """
    async with database.session() as session:
        return await service.list_tables(session, workspace_id=caller.workspace_id)


@router.get(
    "/{slug}/versions",
    summary="The version timeline",
    responses=problems(401, 403, 404, 422),
)
async def list_versions(
    slug: str, caller: ReadDatasets, database: DatabaseDep
) -> list[ReferenceTableVersion]:
    """Newest first, each with the period its rows cover.

    `covers_from`/`covers_to` are what `VR-REF-3` checks a dataset's as-at date against, so
    a reader deciding which version to pin can see the answer rather than infer it.
    """
    async with database.session() as session:
        return await service.list_versions(
            session, workspace_id=caller.workspace_id, slug=slug
        )


@router.get(
    "/{slug}/versions/{version}/rows",
    summary="Rows of a pinned version, optionally as at a date",
    responses=problems(401, 403, 404, 422),
)
async def list_rows(
    slug: str,
    version: int,
    caller: ReadDatasets,
    database: DatabaseDep,
    as_at: Annotated[date | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 200,
) -> list[ReferenceRow]:
    """`01` §5.3's effective-date viewer.

    Always reads the **pinned** version named in the path. Omitting `as_at` returns the
    version whole, which answers "what changed?"; supplying one answers "what applied
    then?". Neither ever falls back to the latest version — that is the mistake
    FR-DATA-30 exists to prevent, and a viewer that made it would teach it.
    """
    async with database.session() as session:
        return await service.rows_as_at(
            session,
            workspace_id=caller.workspace_id,
            slug=slug,
            version=version,
            as_at=as_at,
            limit=limit,
        )
