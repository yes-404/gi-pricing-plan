"""Sub-graph persistence and create-time validation (03 §4.11, FR-217's artifact limb).

A Sub-graph Version is written once and never changed (`00` FR-4): this module has a
create, a revise, a read, a list and a resolver, and no update. Create-time validation is
the shape's graph invariants (FR-212, through the one shared refusal mapping) and FR-227's
result-type check of the output ports. Every write records an Audit Event in the same
transaction (`06` FR-368). Pinning, inlining and compiling a Sub-graph are Slice 2's.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.pagination import COUNT_CAP, Page, decode_int_cursor, encode_cursor
from app.db.models import SubGraphVersionRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import audit
from app.platform.rating_algorithms import (
    check_model_call_feature_maps,
    graph_validation_error,
    raise_first_issue,
)
from model_schema import ArtifactRef, JobSource, Principal, SubGraph, SubGraphBody, SubGraphCreate
from pricing_core.rating.compile import fragment_output_type_issues

__all__ = [
    "create_sub_graph",
    "create_version",
    "get_version",
    "list_versions",
    "resolve_ref",
]

_ARTIFACT = "sub-graph"


def _check(body: SubGraphBody) -> None:
    """FR-227 at create: an output port's type against its producing step's."""
    raise_first_issue(fragment_output_type_issues(body.steps, body.inputs, body.outputs))


def _to_model(row: SubGraphVersionRow) -> SubGraph:
    return SubGraph.model_validate({"slug": row.slug, "version": row.version, **row.content})


async def _latest_version(session: AsyncSession, workspace_id: UUID, slug: str) -> int | None:
    latest: int | None = await session.scalar(
        select(func.max(SubGraphVersionRow.version)).where(
            SubGraphVersionRow.workspace_id == workspace_id,
            SubGraphVersionRow.slug == slug,
        )
    )
    return latest


async def _write(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    version: int,
    body: SubGraphBody,
) -> SubGraph:
    """Insert one version and its Audit Event; a number already taken is a 409."""
    assert actor.id is not None
    row = SubGraphVersionRow(
        workspace_id=workspace_id,
        slug=slug,
        version=version,
        content=body.model_dump(mode="json"),
        change_note=body.change_note,
        created_by=actor.id,
    )
    session.add(row)
    try:
        await session.flush()
    except IntegrityError:
        raise PlatformError(
            "VALIDATION_FAILED",
            "That sub-graph version already exists",
            409,
            f"{slug}@{version} was created by another request. Retry to take the next version.",
        ) from None
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="sub_graph.created",
        entity_ref=f"sub_graph:{slug}@{version}",
        after={
            "change_note": body.change_note,
            "inputs": [p.model_dump(mode="json") for p in body.inputs],
            "outputs": [o.model_dump(mode="json") for o in body.outputs],
        },
    )
    return _to_model(row)


async def create_sub_graph(
    database: Database, workspace_id: UUID, actor: Principal, content: dict[str, Any]
) -> SubGraph:
    """Validate and write version 1 of a new slug; an existing slug is a 409."""
    try:
        body = SubGraphCreate.model_validate(content)
    except ValidationError as exc:
        raise graph_validation_error(exc, artifact=_ARTIFACT) from exc
    _check(body)
    async with database.unit_of_work() as session:
        await check_model_call_feature_maps(session, workspace_id, body.steps)
        if await _latest_version(session, workspace_id, body.slug) is not None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Sub-graph already exists",
                409,
                f"{body.slug} already exists in this workspace. "
                f"POST /api/v1/sub-graphs/{body.slug}/versions writes its next version.",
            )
        return await _write(
            session, workspace_id=workspace_id, actor=actor, slug=body.slug, version=1, body=body
        )


async def create_version(
    database: Database, workspace_id: UUID, actor: Principal, slug: str, content: dict[str, Any]
) -> SubGraph:
    """Validate and write the next version of an existing slug (maximum plus one)."""
    try:
        body = SubGraphBody.model_validate(content)
    except ValidationError as exc:
        raise graph_validation_error(exc, artifact=_ARTIFACT) from exc
    _check(body)
    async with database.unit_of_work() as session:
        latest = await _latest_version(session, workspace_id, slug)
        if latest is None:
            raise _not_found(f"No sub-graph {slug} exists in this workspace.")
        await check_model_call_feature_maps(session, workspace_id, body.steps)
        return await _write(
            session, workspace_id=workspace_id, actor=actor, slug=slug, version=latest + 1,
            body=body,
        )


def _not_found(detail: str) -> PlatformError:
    return PlatformError("NOT_FOUND", "Sub-graph not found", 404, detail)


async def _row(
    session: AsyncSession, workspace_id: UUID, slug: str, version: int
) -> SubGraphVersionRow:
    row = await session.scalar(
        select(SubGraphVersionRow).where(
            SubGraphVersionRow.workspace_id == workspace_id,
            SubGraphVersionRow.slug == slug,
            SubGraphVersionRow.version == version,
        )
    )
    if row is None:
        raise _not_found(f"no sub-graph {slug}@{version} in this workspace.")
    return row


async def get_version(
    database: Database, workspace_id: UUID, slug: str, version: int
) -> SubGraph:
    """Load one version by its address; another workspace's is a 404."""
    async with database.session() as session:
        return _to_model(await _row(session, workspace_id, slug, version))


async def list_versions(
    database: Database, workspace_id: UUID, slug: str, cursor: str | None, limit: int
) -> Page[SubGraph]:
    """A slug's versions in ascending order, cursor-paginated on the version number."""
    after = decode_int_cursor(cursor)
    where = (SubGraphVersionRow.workspace_id == workspace_id, SubGraphVersionRow.slug == slug)
    async with database.session() as session:
        total = int(
            await session.scalar(
                select(func.count()).select_from(
                    select(SubGraphVersionRow.id).where(*where).limit(COUNT_CAP).subquery()
                )
            )
            or 0
        )
        if total == 0:
            raise _not_found(f"No sub-graph {slug} exists in this workspace.")
        query = select(SubGraphVersionRow).where(*where).order_by(SubGraphVersionRow.version)
        if after is not None:
            query = query.where(SubGraphVersionRow.version > after)
        rows = list((await session.scalars(query.limit(limit + 1))).all())
    page = rows[:limit]
    return Page[SubGraph](
        items=[_to_model(r) for r in page],
        next_cursor=encode_cursor(page[-1].version) if len(rows) > limit else None,
        total_estimate=total,
    )


async def resolve_ref(
    session: AsyncSession, *, workspace_id: UUID, ref: ArtifactRef
) -> SubGraph:
    """`sub_graph:<slug>@<version>` → exactly that version. Not wired into compile (Slice 2)."""
    if ref.type != "sub_graph":
        raise PlatformError(
            "VALIDATION_FAILED",
            "Not a sub-graph reference",
            422,
            f"{ref.type}:{ref.slug}@{ref.version} is not a sub_graph reference.",
        )
    return _to_model(await _row(session, workspace_id, ref.slug, ref.version))
