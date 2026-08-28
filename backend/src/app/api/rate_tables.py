"""Rate table routes (03 §5.1, slice W10-2).

`POST /rate-tables/{slug}/seed-from-model` seeds a new rate table version from an
approved model's relativities (FR-RATE-15, FR-RATE-16); `GET
/rate-tables/{slug}@{version}/diff?against=` computes the cell diff against the
previous version or the seed version (FR-RATE-17). Cell diffs are computed on read:
the portfolio weights live in the platform, not in pricing-core (DP1, DP3).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.authz import requires
from app.api.deps import Caller, DatabaseDep
from app.api.responses import problems
from app.errors import PlatformError
from app.platform import rate_tables as service
from model_schema import Permission
from model_schema.refs import ArtifactRef

__all__ = ["router"]

router = APIRouter(tags=["rating"])

RatingWriteDep = Annotated[Caller, Depends(requires(Permission.RATING_WRITE))]
RatingReadDep = Annotated[Caller, Depends(requires(Permission.RATING_READ))]


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
) -> dict[str, Any]:
    """**201** with the seeded version: its definition, rows, and `seeded_from` (FR-RATE-15).

    The source model must be approved (PIN_NOT_APPROVED otherwise), and its relativities
    must validate as a rate table (named `RATE_TABLE_*` codes, 03 §5.2). Seeding always
    writes a `rows` version; parquet storage arrives with W10-3.
    """
    assert caller.principal.id is not None
    model_ref, change_note = _seed_body(body)
    return await service.seed_from_model(
        database,
        caller.workspace_id,
        caller.principal.id,
        slug=slug,
        model_ref=model_ref,
        change_note=change_note,
    )


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
