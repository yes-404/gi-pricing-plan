"""Rate table routes (03 §5.1, slices W10-2/W10-3C).

`POST /rate-tables/{slug}/seed-from-model` seeds a new rate table version from an
approved model's relativities (FR-229, FR-230); `GET
/rate-tables/{slug}@{version}/diff?against=` computes the cell diff against the
previous version or the seed version (FR-231); `POST
/rate-tables/{slug}@{version}/bulk-operation` applies a bulk operation to a version
(FR-233). Cell diffs are computed on read: the portfolio weights live in the
platform, not in pricing-core (DP1, DP3).
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Annotated, Any
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)

from app.api.authz import requires
from app.api.deps import Caller, DatabaseDep, SettingsDep, job_identity
from app.api.pagination import DEFAULT_LIMIT, MAX_LIMIT, Page
from app.api.responses import problems
from app.errors import PlatformError
from app.platform import jobs as job_service
from app.platform import rate_tables as service
from app.platform import rbac
from app.platform.blobs import BlobStore
from model_schema import JobKind, Permission
from model_schema.jobs import Job
from model_schema.rating import (
    RateTable,
    RateTableCell,
    RateTableDiff,
    RateTableDiffCell,
    RateTableManualEdit,
    RateTableVersion,
    SeedFromModelRequest,
)

__all__ = ["router"]

router = APIRouter(tags=["rating"])

RatingWriteDep = Annotated[Caller, Depends(requires(Permission.RATING_WRITE))]
RatingReadDep = Annotated[Caller, Depends(requires(Permission.RATING_READ))]


def _blob_store(request: Request) -> BlobStore:
    store: BlobStore = request.app.state.blob_store
    return store


BlobStoreDep = Annotated[BlobStore, Depends(_blob_store)]


@contextmanager
def spec_not_found() -> Iterator[None]:
    """`03` §5.1 types the S4 routes' unknown table, version or `base_version` as 404
    `NOT_FOUND` (RL-1555 T1; the maintainer's rulings of 2026-10-10 04:19:42 and 04:23:36: the
    spec governs, and the reads follow the edit route).
    The shared loaders keep `RATE_TABLE_MISS`, which the scoring path relies on, so the route
    maps it here and nothing below it changes."""
    try:
        yield
    except PlatformError as exc:
        if exc.code != "RATE_TABLE_MISS":
            raise
        raise PlatformError("NOT_FOUND", "Not Found", 404, exc.detail) from exc


def _parse_against(raw: str) -> str | int:
    """Parse the `against` query parameter: `previous`, `seed`, or an explicit version."""
    if raw in ("previous", "seed"):
        return raw
    if raw.isdigit() and int(raw) >= 1:
        return int(raw)
    raise PlatformError(
        "VALIDATION_FAILED",
        "Request validation failed",
        422,
        detail="against must be `previous`, `seed`, or a version number",
    )


@router.post(
    "/rate-tables/{slug}/seed-from-model",
    summary="Seed a rate table version from an approved model",
    status_code=status.HTTP_201_CREATED,
    response_model=RateTableVersion,
    responses=problems(401, 403, 404, 409, 422),
)
async def seed_rate_table_from_model(
    slug: str,
    body: SeedFromModelRequest,
    caller: RatingWriteDep,
    database: DatabaseDep,
    settings: SettingsDep,
    blob_store: BlobStoreDep,
) -> RateTableVersion:
    """**201** with the seeded version: its definition, rows, and `seeded_from` (FR-229).

    The body is a `SeedFromModelRequest`: `model_ref`, `factor` (the Factor's slug, a key of
    the model's relativities) and `change_note`; an unknown field is refused. One seed
    holds one Factor, bound by `factor_ref` to the Factor version the model pins (FR-230,
    `RL-1361`). The source model must be approved (PIN_NOT_APPROVED otherwise); a Factor id
    of the model that does not resolve is 404. A `factor` that names no relativity entry, a
    Factor outside the factor slug grammar, and a re-seed of a lineage bound to another
    Factor are 422 `VALIDATION_FAILED`; the relativities must validate as a rate table
    (named `RATE_TABLE_*` codes, 03 §5.2). Storage is decided against the workspace's
    cell-count threshold at creation and immutable with the version (FR-232, DP2).
    """
    assert caller.principal.id is not None
    version = await service.seed_from_model(
        database,
        caller.workspace_id,
        caller.principal.id,
        settings,
        blob_store,
        slug=slug,
        model_ref=body.model_ref,
        factor=body.factor,
        change_note=body.change_note,
    )
    return version


@router.post(
    "/rate-tables/{slug}/versions",
    summary="Preview or create a Rate Table Version from manual cell edits",
    response_model=None,
    responses={
        **problems(401, 403, 404, 409, 422),
        200: {"model": RateTableDiff},
        201: {"model": RateTableVersion},
    },
)
async def edit_rate_table(
    slug: str,
    body: RateTableManualEdit,
    caller: RatingWriteDep,
    database: DatabaseDep,
    settings: SettingsDep,
    blob_store: BlobStoreDep,
    response: Response,
) -> RateTableDiff | RateTableVersion:
    """**200** with a bare `RateTableDiff` of the would-be version against `base_version`;
    nothing is created (FR-229, FR-231). **201** with `confirm: true`: the `RateTableVersion`
    at `base_version + 1`, carrying `created_by_edit` (`RL-1555`). **404** `NOT_FOUND` for an
    unknown table or `base_version`. **409** where
    `base_version + 1` already exists (the base is not the latest). **422** with every
    failure as a field error in `errors` (FR-234).
    """
    if not body.confirm:
        with spec_not_found():
            return await service.manual_edit_preview(
                database, caller.workspace_id, slug, body, blob_store
            )
    assert caller.principal.id is not None
    with spec_not_found():
        created = await service.manual_edit_confirmed(
            database, caller.workspace_id, caller.principal.id, settings, blob_store,
            slug=slug, body=body,
        )
    response.status_code = status.HTTP_201_CREATED
    return created


@router.post(
    "/rate-tables/{slug}@{version}/bulk-operation",
    summary="Apply a bulk operation to a rate table version",
    status_code=status.HTTP_201_CREATED,
    responses=problems(401, 403, 404, 409, 422),
)
async def bulk_operate_rate_table(
    slug: str,
    version: int,
    body: dict[str, Any],
    caller: RatingWriteDep,
    database: DatabaseDep,
    settings: SettingsDep,
    blob_store: BlobStoreDep,
) -> dict[str, Any]:
    """**201** with the new version (FR-233): the operation and its parameters
    recorded as `created_by_operation` (04 §4.4), the seed anchor inherited and
    proven equal to the baseline's at save time (03 §4.2, FR-234).

    The body is `{"kind", "parameters"}` — `applied_to` and `result` are server-side:
    `applied_to` names the addressed version, and `result` is computed by the
    operation. Parameters are decimal strings, never floats (R2).
    """
    assert caller.principal.id is not None
    kind = body.get("kind")
    parameters = body.get("parameters")
    if not isinstance(kind, str) or not isinstance(parameters, dict):
        raise PlatformError(
            "VALIDATION_FAILED",
            "Request validation failed",
            422,
            detail="body must carry `kind` and `parameters` (04 §4.4)",
        )
    created = await service.bulk_operation(
        database,
        caller.workspace_id,
        caller.principal.id,
        settings,
        blob_store,
        slug=slug,
        version=version,
        kind=kind,
        parameters=parameters,
    )
    return created.model_dump(mode="json")


@router.get(
    "/rate-tables/{slug}@{version}/export/csv",
    summary="Export the version's cells as CSV",
    responses=problems(401, 403, 404),
)
async def export_rate_table_csv(
    slug: str,
    version: int,
    caller: RatingReadDep,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
) -> Response:
    """**200** with the CSV (FR-235): header, then one row per cell — decimal
    strings, never floats (R2). Parquet-stored versions are read inline from their
    blob; the Job-worthy read is the diff (W10-3D), not a bounded export."""
    content = await service.export_csv(
        database, caller.workspace_id, slug, version, blob_store
    )
    return Response(content=content, media_type="text/csv")


@router.get(
    "/rate-tables/{slug}@{version}/export/xlsx",
    summary="Export the version's cells as XLSX",
    responses=problems(401, 403, 404),
)
async def export_rate_table_xlsx(
    slug: str,
    version: int,
    caller: RatingReadDep,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
) -> Response:
    """**200** with the XLSX (FR-235): every cell written as text, so the strict
    round-trip an import's verdict asserts survives a spreadsheet's number handling."""
    content = await service.export_xlsx(
        database, caller.workspace_id, slug, version, blob_store
    )
    return Response(
        content=content,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )


@router.post(
    "/rate-tables/{slug}@{version}/import",
    summary="Preview an import as a diff against the addressed version",
    responses=problems(401, 403, 404, 413, 422),
)
async def import_rate_table(
    slug: str,
    version: int,
    caller: RatingWriteDep,
    database: DatabaseDep,
    settings: SettingsDep,
    blob_store: BlobStoreDep,
    response: Response,
    file: Annotated[UploadFile, File()],
    confirm: Annotated[bool, Form()] = False,
) -> dict[str, Any]:
    """**200** with the would-be version's diff and its strict verdict (FR-235,
    03 §5.1): the file is checked against the addressed version's own domain — same
    keys, same key types, same coverage — and nothing is created.

    **201** with `confirm: true` (DP6): the same upload is parsed again through the
    same strict pipeline and the version is created — confirmation cannot override
    the round-trip verdict, so the created version cannot diverge from the preview.
    The permission is `RATING_WRITE` by the platform convention that file-upload
    endpoints take the write dep (the datasets preview does).
    """
    filename = file.filename or "import.csv"
    if len(filename) > 255:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Import filename too long",
            422,
            f"the upload's filename is {len(filename)} characters; the verdict "
            "records it bounded to 255 (DP5) — it is a record, never a path.",
        )
    content = await file.read()
    if not confirm:
        preview = await service.import_preview(
            database,
            caller.workspace_id,
            slug,
            version,
            blob_store,
            filename=filename,
            content=content,
        )
        return preview.model_dump(mode="json")
    assert caller.principal.id is not None
    created = await service.import_confirmed(
        database,
        caller.workspace_id,
        caller.principal.id,
        settings,
        blob_store,
        slug=slug,
        version=version,
        filename=filename,
        content=content,
    )
    response.status_code = status.HTTP_201_CREATED
    return created.model_dump(mode="json")


async def _cells_job_response(
    needed: service.DiffCellsJobNeeded,
    caller: Caller,
    database: Any,
    response: Response,
    *,
    slug: str,
    version: int,
    against: str,
    portfolio: UUID | None,
) -> Job:
    """202 with the `rate_table.diff_cells` Job that builds this query's artifact: the one in
    flight if there is one, else a new one carrying the artifact's `key`."""
    job = needed.in_flight
    if job is None:
        async with database.unit_of_work() as session:
            job = await job_service.submit(
                session,
                JobKind.RATE_TABLE_DIFF_CELLS,
                {
                    **job_identity(caller),
                    "slug": slug,
                    "version": version,
                    "against": against,
                    "key": needed.key,
                    **({"portfolio": str(portfolio)} if portfolio is not None else {}),
                },
                caller.principal,
                workspace_id=caller.workspace_id,
            )
    response.status_code = status.HTTP_202_ACCEPTED
    response.headers["Location"] = f"/api/v1/jobs/{job.id}"
    return job


@router.get(
    "/rate-tables/{slug}@{version}/diff",
    summary="Cell diff of a rate table version against a baseline",
    response_model=None,
    responses={
        **problems(401, 403, 404, 409, 422),
        200: {"model": RateTableDiff},
        202: {"model": Job},
    },
)
async def rate_table_diff(
    slug: str,
    version: int,
    caller: RatingReadDep,
    database: DatabaseDep,
    response: Response,
    blob_store: BlobStoreDep,
    against: str = Query(..., description="`previous`, `seed`, or a version number"),
    portfolio: Annotated[
        UUID | None,
        Query(
            description=(
                "A `validated` portfolio Dataset Version whose exposure weights the diff "
                "(FR-231). Needs `dataset:read`; there is no default."
            )
        ),
    ] = None,
) -> RateTableDiff | Job:
    """**200** with the diff summary (FR-231) read from the stored artifact; **202** with a
    `rate_table.diff_cells` Job where this query's artifact is not yet stored, for either
    storage (FR-232, R1: an operation that can exceed 2 s returns 202). The Job is the one the
    cells route uses: one artifact serves both, found by the identity of the two versions and
    of the portfolio, so a later request loads no cell.

    The baseline resolves to the previous version, the seed version, or an explicit version
    number. With `portfolio` the cells are weighted by its exposure (`RL-1361`): the caller needs
    `dataset:read` for that, checked here and not route-wide, so a rating-only caller still gets
    an unweighted diff; the refusal is the same **403** for any id, so it never says whether the
    portfolio exists. Its scope and status are then checked before any Job is created. A refusal
    that depends on the portfolio's content is the Job's failure, with the same code.
    """
    baseline = _parse_against(against)
    if portfolio is not None:
        async with database.session() as session:
            await rbac.require_permission(
                session,
                workspace_id=caller.workspace_id,
                principal=caller.principal,
                permission=Permission.DATASET_READ,
                credential_permissions=caller.permissions,
            )
    answer = await service.diff_from_artifact(
        database, caller.workspace_id, slug, version, baseline,
        blob_store=blob_store, portfolio_dataset_version_id=portfolio,
    )
    if isinstance(answer, service.DiffCellsJobNeeded):
        return await _cells_job_response(
            answer, caller, database, response,
            slug=slug, version=version, against=against, portfolio=portfolio,
        )
    return answer


@router.get(
    "/rate-tables/{slug}@{version}",
    summary="Read one Rate Table Version's definition, without its cells",
    responses=problems(401, 403, 404),
)
async def read_rate_table(
    slug: str, version: int, caller: RatingReadDep, database: DatabaseDep
) -> RateTable:
    """FR 9940: the version's keys, value, storage, flag and default row; never its cells."""
    with spec_not_found():
        return await service.read_definition(database, caller.workspace_id, slug, version)


@router.get(
    "/rate-tables/{slug}@{version}/cells",
    summary="Page through one Rate Table Version's cells, either storage, no Job",
    responses=problems(400, 401, 403, 404, 422),
)
async def read_rate_table_cells(
    slug: str,
    version: int,
    caller: RatingReadDep,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    cursor: str | None = None,
) -> Page[RateTableCell]:
    """FR 9940, FR-232: one cursor page of `RateTableCell` rows in key order, for `rows` and
    `parquet` storage alike, answered **200** and never as a Job. A cursor this API did not
    issue is a **400**, a `limit` out of range a **422**."""
    with spec_not_found():
        return await service.cells_page(
            database, caller.workspace_id, slug, version, blob_store, cursor=cursor, limit=limit
        )


@router.get(
    "/rate-tables/{slug}@{version}/diff/cells",
    summary="The changed cells of a rate table diff, one cursor page at a time",
    response_model=None,
    responses={
        **problems(400, 401, 403, 404, 409, 422),
        200: {"model": Page[RateTableDiffCell]},
        202: {"model": Job},
    },
)
async def rate_table_diff_cells(
    slug: str,
    version: int,
    caller: RatingReadDep,
    database: DatabaseDep,
    response: Response,
    blob_store: BlobStoreDep,
    against: str = Query(..., description="`previous`, `seed`, or a version number"),
    portfolio: Annotated[
        UUID | None,
        Query(
            description=(
                "A `validated` portfolio Dataset Version whose exposure gives each cell its "
                "weight (FR-231). Needs `dataset:read`; there is no default."
            )
        ),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    cursor: str | None = None,
) -> Page[RateTableDiffCell] | Job:
    """Every cell the diff counts as changed, in `03` §4.2's key order (FR-231, `RL-1418`).

    **200** with one cursor page: a page bounds one response, not the cells. **202** with a
    `rate_table.diff_cells` Job, for either storage, where this query's cell artifact is not yet
    stored (R1: an operation that can exceed 2 s returns 202); the Job writes every changed cell
    as one blob, and the same request then answers 200 from it, reading only its slice. The
    artifact is found by the identity of the two versions and of the portfolio, without loading
    a cell. `against` and `portfolio` are checked as on the diff route, before any Job. A cursor
    this API did not issue is a **400**, a `limit` out of range a **422**.
    """
    baseline = _parse_against(against)
    if portfolio is not None:
        async with database.session() as session:
            await rbac.require_permission(
                session,
                workspace_id=caller.workspace_id,
                principal=caller.principal,
                permission=Permission.DATASET_READ,
                credential_permissions=caller.permissions,
            )
    answer = await service.diff_cells_page(
        database, caller.workspace_id, slug, version, baseline,
        blob_store=blob_store, portfolio_dataset_version_id=portfolio,
        limit=limit, cursor=cursor,
    )
    if isinstance(answer, service.DiffCellsJobNeeded):
        return await _cells_job_response(
            answer, caller, database, response,
            slug=slug, version=version, against=against, portfolio=portfolio,
        )
    return Page[RateTableDiffCell](
        items=answer.items, next_cursor=answer.next_cursor, total_estimate=answer.total_estimate
    )
