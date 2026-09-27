"""Rating Algorithm persistence and save-time validation (03 §4.1, slice W9-2).

A saved algorithm is stored as its validated JSON content. Save-time validation runs
before a row is written: the shape's own invariants (FR-212) and the deeper checks
in `pricing_core.rating.compile.validate_algorithm` (FR-216/227/273/274/275/276).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import select

from app.db.models import RatingAlgorithmRow
from app.db.session import Database
from app.errors import PlatformError
from model_schema.rating import RatingAlgorithm, diff_algorithms
from pricing_core.rating.compile import validate_algorithm

__all__ = ["create_algorithm", "diff_between", "get_algorithm"]


def _parse_algorithm(content: dict[str, Any]) -> RatingAlgorithm:
    """Parse the submitted JSON, mapping a shape-invariant refusal to its named code.

    The `RatingAlgorithm` shape enforces the graph invariants (FR-212) in its own
    validator; a cyclic graph or an unresolved reference is refused here with the code
    the spec's §5.1 names, rather than leaking Pydantic's generic 422.
    """
    try:
        return RatingAlgorithm.model_validate(content)
    except ValidationError as exc:
        text = str(exc).lower()
        if "cycle" in text:
            raise PlatformError(
                "RATING_GRAPH_CYCLIC",
                "Rating graph is cyclic",
                422,
                "A rating algorithm is a directed acyclic graph (FR-212).",
            ) from exc
        if "undefined value" in text:
            raise PlatformError(
                "RATING_GRAPH_UNRESOLVED_REF",
                "Rating graph references an undefined value",
                422,
                "Every consumed value is produced by a step (FR-212).",
            ) from exc
        raise PlatformError(
            "VALIDATION_FAILED",
            "Rating algorithm is invalid",
            422,
            str(exc),
        ) from exc


def _issues_to_error(algorithm: RatingAlgorithm) -> None:
    """Refuse an algorithm whose deeper checks fail, naming the first issue."""
    issues = validate_algorithm(algorithm)
    if not issues:
        return
    issue = issues[0]
    raise PlatformError(
        issue.code,
        issue.code.replace("_", " ").title(),
        422,
        issue.message,
    )


async def create_algorithm(
    database: Database,
    workspace_id: UUID,
    created_by: UUID,
    content: dict[str, Any],
) -> RatingAlgorithmRow:
    """Parse, validate, and persist a rating algorithm (03 §5.1).

    A conflicting (slug, version) is refused as a conflict; save-time validation runs
    before the row is written.
    """
    algorithm = _parse_algorithm(content)
    _issues_to_error(algorithm)

    async with database.unit_of_work() as session:
        existing = await session.scalar(
            select(RatingAlgorithmRow).where(
                RatingAlgorithmRow.workspace_id == workspace_id,
                RatingAlgorithmRow.slug == algorithm.slug,
                RatingAlgorithmRow.version == algorithm.version,
            )
        )
        if existing is not None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Rating algorithm version already exists",
                409,
                f"{algorithm.slug}@{algorithm.version} already exists in this workspace.",
            )
        row = RatingAlgorithmRow(
            workspace_id=workspace_id,
            slug=algorithm.slug,
            version=algorithm.version,
            content=content,
            created_by=created_by,
        )
        session.add(row)
        await session.flush()
        return row


async def get_algorithm(
    database: Database, workspace_id: UUID, slug: str, version: int
) -> RatingAlgorithm:
    """Load one algorithm version by its canonical `slug@version`."""
    async with database.session() as session:
        row = await session.scalar(
            select(RatingAlgorithmRow).where(
                RatingAlgorithmRow.workspace_id == workspace_id,
                RatingAlgorithmRow.slug == slug,
                RatingAlgorithmRow.version == version,
            )
        )
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "Rating algorithm not found",
            404,
            f"No rating algorithm {slug}@{version} in this workspace.",
        )
    return RatingAlgorithm.model_validate(row.content)


async def diff_between(
    database: Database, workspace_id: UUID, slug: str, version: int, against: int
) -> dict[str, Any]:
    """The structural diff between two versions of one algorithm (FR-219)."""
    current = await get_algorithm(database, workspace_id, slug, version)
    base = await get_algorithm(database, workspace_id, slug, against)
    return diff_algorithms(base, current).model_dump()
