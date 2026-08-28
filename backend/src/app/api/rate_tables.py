"""Rate table routes (03 §5.1, slices W10-2/W10-3C).

`POST /rate-tables/{slug}/seed-from-model` seeds a new rate table version from an
approved model's relativities (FR-RATE-15, FR-RATE-16); `GET
/rate-tables/{slug}@{version}/diff?against=` computes the cell diff against the
previous version or the seed version (FR-RATE-17); `POST
/rate-tables/{slug}@{version}/bulk-operation` applies a bulk operation to a version
(FR-RATE-18). Cell diffs are computed on read: the portfolio weights live in the
platform, not in pricing-core (DP1, DP3).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Query, Request, Response, UploadFile, status

from app.api.authz import requires
from app.api.deps import Caller, DatabaseDep, SettingsDep
from app.api.responses import problems
from app.errors import PlatformError
from app.platform import rate_tables as service
from app.platform.blobs import BlobStore
from model_schema import Permission
from model_schema.refs import ArtifactRef

__all__ = ["router"]

router = APIRouter(tags=["rating"])

RatingWriteDep = Annotated[Caller, Depends(requires(Permission.RATING_WRITE))]
RatingReadDep = Annotated[Caller, Depends(requires(Permission.RATING_READ))]


def _blob_store(request: Request) -> BlobStore:
    store: BlobStore = request.app.state.blob_store
    return store


BlobStoreDep = Annotated[BlobStore, Depends(_blob_store)]


def _seed_body(body: dict[str, Any]) -> tuple[ArtifactRef, str]:
    """Validate the seed request body, returning the canonical model ref and change note.

    The body is the raw JSON from 03 §4.2: `model_ref` is the canonical wire form
    `model:slug@version` (ID-3), and `change_note` is required (FR-RATE-15).
    """
    raw_ref = body.get("model_ref")
    if not isinstance(raw_ref, str):
        raise PlatformError(
            "VALIDATION_FAILED",
            "Request validation failed",
            422,
            detail="model_ref must be the canonical artifact reference `model:slug@version`",
        )
    try:
        ref = ArtifactRef.parse(raw_ref)
    except ValueError as exc:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Request validation failed",
            422,
            detail=str(exc),
        ) from exc
    if ref.type != "model":
        raise PlatformError(
            "VALIDATION_FAILED",
            "Request validation failed",
            422,
            detail="model_ref must reference a model artifact",
        )
    change_note = body.get("change_note")
    if not isinstance(change_note, str) or not change_note.strip():
        raise PlatformError(
            "VALIDATION_FAILED",
            "Request validation failed",
            422,
            detail="change_note is required and must be non-empty (FR-RATE-15)",
        )
    return ref, change_note.strip()


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
    responses=problems(401, 403, 404, 409, 422),
)
async def seed_rate_table_from_model(
    slug: str,
    body: dict[str, Any],
    caller: RatingWriteDep,
    database: DatabaseDep,
    settings: SettingsDep,
    blob_store: BlobStoreDep,
) -> dict[str, Any]:
    """**201** with the seeded version: its definition, rows, and `seeded_from` (FR-RATE-15).

    The source model must be approved (PIN_NOT_APPROVED otherwise), and its relativities
    must validate as a rate table (named `RATE_TABLE_*` codes, 03 §5.2). Storage is
    decided against the workspace's cell-count threshold at creation and immutable with
    the version (FR-RATE-62, DP2).
    """
    assert caller.principal.id is not None
    model_ref, change_note = _seed_body(body)
    version = await service.seed_from_model(
        database,
        caller.workspace_id,
        caller.principal.id,
        settings,
        blob_store,
        slug=slug,
        model_ref=model_ref,
        change_note=change_note,
    )
    return version.model_dump(mode="json")


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
    """**201** with the new version (FR-RATE-18): the operation and its parameters
    recorded as `created_by_operation` (04 §4.4), the seed anchor inherited and
    proven equal to the baseline's at save time (03 §4.2, FR-RATE-19).

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
    version = await service.bulk_operation(
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
    return version.model_dump(mode="json")


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
    """**200** with the CSV (FR-RATE-20): header, then one row per cell — decimal
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
    """**200** with the XLSX (FR-RATE-20): every cell written as text, so the strict
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
    blob_store: BlobStoreDep,
    file: Annotated[UploadFile, File()],
) -> dict[str, Any]:
    """**200** with the would-be version's diff and its strict verdict (FR-RATE-20,
    03 §5.1): the file is checked against the addressed version's own domain — same
    keys, same key types, same coverage — and nothing is created.

    The permission is `RATING_WRITE` by the platform convention that file-upload
    preview endpoints take the write dep (the datasets preview does), even though
    this call only previews; the confirmed-clean creation half is ruling-gated.
    """
    preview = await service.import_preview(
        database,
        caller.workspace_id,
        slug,
        version,
        blob_store,
        filename=file.filename or "import.csv",
        content=await file.read(),
    )
    return preview.model_dump(mode="json")


@router.get(
    "/rate-tables/{slug}@{version}/diff",
    summary="Cell diff of a rate table version against a baseline",
    responses=problems(401, 403, 404, 422, 501),
)
async def rate_table_diff(
    slug: str,
    version: int,
    caller: RatingReadDep,
    database: DatabaseDep,
    against: str = Query(..., description="`previous`, `seed`, or a version number"),
) -> dict[str, Any]:
    """**200** with the diff (FR-RATE-17): changed cells and exposure-weighted change.

    The baseline resolves to the previous version, the seed version, or an explicit
    version number. A diff touching a `parquet` version is refused with **501**
    `RATE_TABLE_PARQUET_UNBUILT` until W10-3 delivers parquet storage.
    """
    baseline = _parse_against(against)
    diff = await service.diff(
        database, caller.workspace_id, slug, version, baseline
    )
    return diff.model_dump()
