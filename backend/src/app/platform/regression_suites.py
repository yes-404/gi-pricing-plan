"""Regression Suites: the versioned, access-controlled golden-quote store (03 §4.7, FR-260).

A suite is its own versioned artifact, bound to one Rating Algorithm by `algorithm_slug`
and never approvable (the deputy's DP-S2-1 (A), `PL-1189` Task 4). Every read is
permission-checked, because a golden quote's `context` is a full quote input (NFR-499 as
clarified by RL-917); no audit payload and no log line carries one.

**One suite per algorithm is the database's rule, not this module's.** The registry is
unique on `(workspace_id, slug)` and on `(workspace_id, algorithm_slug)`, and versions on
`(suite_id, version)`. This module never checks first and inserts second — two writers
racing past a check would both succeed (audit finding F6) — it inserts, and maps the
`IntegrityError` a constraint raises to 409.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RegressionSuiteRow, RegressionSuiteVersionRow
from app.errors import PlatformError
from app.platform import audit, rbac
from model_schema import (
    JobSource,
    Permission,
    Principal,
    RegressionSuite,
    RegressionSuiteContent,
    suite_content_hash,
)

__all__ = [
    "create_suite_version",
    "current_suite_for_algorithm",
    "load_suite_version",
    "suite_versions",
    "to_schema",
]

#: The Audit Event every created suite version carries exactly one of. Its actor is the
#: version's Author (`06` FR-368), which the approval delta reads.
CREATED_ACTION = "regression_suite.created"


def entity_ref(slug: str, version: int) -> str:
    return f"regression_suite:{slug}@{version}"


def to_schema(suite: RegressionSuiteRow, row: RegressionSuiteVersionRow) -> RegressionSuite:
    return RegressionSuite.model_validate(
        {
            **row.content,
            "slug": suite.slug,
            "version": row.version,
            "change_note": row.change_note,
            "content_hash": row.content_hash,
            "created_at": row.created_at,
            "created_by": row.created_by,
        }
    )


def _conflict(title: str, detail: str) -> PlatformError:
    return PlatformError("VALIDATION_FAILED", title, 409, detail)


async def _registry(
    session: AsyncSession, *, workspace_id: UUID, slug: str
) -> RegressionSuiteRow | None:
    return (
        await session.execute(
            select(RegressionSuiteRow).where(
                RegressionSuiteRow.workspace_id == workspace_id,
                RegressionSuiteRow.slug == slug,
            )
        )
    ).scalar_one_or_none()


async def _next_version(session: AsyncSession, *, suite: RegressionSuiteRow) -> int:
    """`1 + max(version)`. Two writers may compute the same number; the
    `(suite_id, version)` constraint then refuses the second (re-audit N3)."""
    current = (
        await session.execute(
            select(func.coalesce(func.max(RegressionSuiteVersionRow.version), 0)).where(
                RegressionSuiteVersionRow.suite_id == suite.id
            )
        )
    ).scalar_one()
    return int(current) + 1


async def create_suite_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    content: RegressionSuiteContent,
    change_note: str,
) -> tuple[RegressionSuiteRow, RegressionSuiteVersionRow]:
    """Create the next version of suite `slug` (`rating:write`), audited in the same
    transaction. The first version of a slug creates its registry row too."""
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor,
        permission=Permission.RATING_WRITE,
    )
    suite = await _registry(session, workspace_id=workspace_id, slug=slug)
    if suite is None:
        suite = RegressionSuiteRow(
            workspace_id=workspace_id, slug=slug,
            algorithm_slug=content.algorithm_slug, created_by=actor.id,
        )
        session.add(suite)
        try:
            await session.flush()
        except IntegrityError as exc:
            raise _conflict(
                "This algorithm already has a Regression Suite",
                f"Algorithm {content.algorithm_slug!r} already has a Regression Suite in "
                f"this workspace, or suite {slug!r} was created concurrently; one suite "
                "per algorithm (03 §4.7).",
            ) from exc
    elif suite.algorithm_slug != content.algorithm_slug:
        raise _conflict(
            "A Regression Suite cannot change algorithm",
            f"Suite {slug!r} is bound to algorithm {suite.algorithm_slug!r}, not "
            f"{content.algorithm_slug!r}.",
        )

    version = await _next_version(session, suite=suite)
    content_hash = suite_content_hash(content)
    row = RegressionSuiteVersionRow(
        suite_id=suite.id,
        version=version,
        content=content.model_dump(mode="json", include=set(RegressionSuiteContent.model_fields)),
        content_hash=content_hash,
        change_note=change_note,
        created_by=actor.id,
    )
    session.add(row)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise _conflict(
            "A newer version of this suite was created concurrently",
            f"{slug}@{version} was created concurrently; retry.",
        ) from exc
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action=CREATED_ACTION,
        entity_ref=entity_ref(slug, version),
        before={},
        # Never the golden quotes' contexts (NFR-499): names and the hash only.
        after={
            "content_hash": content_hash,
            "change_note": change_note,
            "algorithm_slug": content.algorithm_slug,
            "golden_quote_names": [quote.name for quote in content.golden_quotes],
        },
    )
    return suite, row


async def load_suite_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    version: int,
) -> tuple[RegressionSuiteRow, RegressionSuiteVersionRow]:
    """One suite version (`rating:read`). A cross-workspace or missing one reads as 404."""
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor,
        permission=Permission.RATING_READ,
    )
    suite = await _registry(session, workspace_id=workspace_id, slug=slug)
    row = None
    if suite is not None:
        row = (
            await session.execute(
                select(RegressionSuiteVersionRow).where(
                    RegressionSuiteVersionRow.suite_id == suite.id,
                    RegressionSuiteVersionRow.version == version,
                )
            )
        ).scalar_one_or_none()
    if suite is None or row is None:
        raise PlatformError(
            "NOT_FOUND", "Regression Suite version not found", 404,
            f"No Regression Suite version {entity_ref(slug, version)}.",
        )
    return suite, row


async def suite_versions(
    session: AsyncSession, *, suite: RegressionSuiteRow
) -> list[RegressionSuiteVersionRow]:
    """Every version of `suite`, ascending. For the server's own gate, not a route."""
    return list(
        (
            await session.execute(
                select(RegressionSuiteVersionRow)
                .where(RegressionSuiteVersionRow.suite_id == suite.id)
                .order_by(RegressionSuiteVersionRow.version)
            )
        ).scalars()
    )


async def current_suite_for_algorithm(
    session: AsyncSession, *, workspace_id: UUID, algorithm_slug: str
) -> tuple[RegressionSuiteRow, RegressionSuiteVersionRow] | None:
    """The highest version of the one suite bound to `algorithm_slug`, or `None`.

    Unambiguous by `uq_regression_suites_algorithm`. For the server's own submit gate,
    which checks the submitter's permission itself; not a route.
    """
    suite = (
        await session.execute(
            select(RegressionSuiteRow).where(
                RegressionSuiteRow.workspace_id == workspace_id,
                RegressionSuiteRow.algorithm_slug == algorithm_slug,
            )
        )
    ).scalar_one_or_none()
    if suite is None:
        return None
    versions = await suite_versions(session, suite=suite)
    return (suite, versions[-1]) if versions else None
