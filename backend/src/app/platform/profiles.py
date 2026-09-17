"""Stored profiles and the one-ways read from them (`01` §3.4, §4.7, FR-60, FR-61, FR-62, FR-63).

FR-62 forbids the UI recomputing a one-way and NFR-468 gives it 300 ms. Both are
statements about *reading*, and they are only true if a profile is computed once and
stored whole. This module is the storage; `pricing_core.data.profile` is the computation,
and it does not know this module exists (ADR-703).
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DatasetVersionRow, ProfileRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit
from model_schema import JobSource, OneWaySummary, Principal, Profile

__all__ = ["latest_profile", "load_profile", "one_way_of", "store_profile"]

_log = get_logger("app.profiles")


async def store_profile(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    profile: Profile,
    job_id: UUID | None = None,
) -> ProfileRow:
    """Persist a profile against its version and point the version at it (FR-60)."""
    version = await session.get(DatasetVersionRow, profile.dataset_version_id)
    if version is None or version.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND",
            "Dataset version not found",
            404,
            f"No version {profile.dataset_version_id} in this workspace.",
        )

    row = ProfileRow(
        id=profile.id,
        workspace_id=workspace_id,
        dataset_version_id=profile.dataset_version_id,
        job_id=job_id,
        row_count=profile.row_count,
        body=profile.model_dump(mode="json"),
        computed_at=profile.computed_at,
    )
    session.add(row)
    # The version names its current profile so that "the profile of @12" is a lookup
    # rather than a search with a tie-break. Re-profiling adds a row and re-points; the
    # superseded profile stays, because a comparison may cite it.
    version.profile_id = profile.id
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="profile.created",
        entity_ref=f"profile:{profile.id}",
        after={
            "dataset_version_id": str(profile.dataset_version_id),
            "row_count": profile.row_count,
            "columns": len(profile.columns),
            "one_ways": [summary.column for summary in profile.one_ways],
        },
        job_id=job_id,
    )
    _log.info("profile stored", extra={"profile_id": str(profile.id)})
    return row


async def load_profile(
    session: AsyncSession, *, workspace_id: UUID, profile_id: UUID
) -> Profile:
    row = await session.get(ProfileRow, profile_id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError("NOT_FOUND", "Profile not found", 404, f"No profile {profile_id}.")
    return Profile.model_validate(row.body)


async def latest_profile(
    session: AsyncSession, *, workspace_id: UUID, version_id: UUID
) -> Profile:
    """The current profile of a version (FR-60)."""
    result = await session.execute(
        select(ProfileRow)
        .where(
            ProfileRow.workspace_id == workspace_id,
            ProfileRow.dataset_version_id == version_id,
        )
        .order_by(ProfileRow.created_at.desc(), ProfileRow.id.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "This dataset version has no profile",
            404,
            "Profiling runs after a successful ingestion (FR-60); a version without "
            "one has not completed ingestion or predates profiling.",
        )
    return Profile.model_validate(row.body)


async def one_way_of(
    session: AsyncSession, *, workspace_id: UUID, version_id: UUID, column: str
) -> OneWaySummary:
    """One column's one-way, **read** from the stored profile (FR-62, NFR-468).

    Never computed here. A function that fell back to computing when the column was not in
    the stored profile would meet the latency budget in testing and miss it in production,
    which is the failure mode NFR-468 exists to prevent — so a missing column is a 404
    naming the ones that are present.
    """
    profile = await latest_profile(session, workspace_id=workspace_id, version_id=version_id)
    for summary in profile.one_ways:
        if summary.column == column:
            return summary
    available = ", ".join(sorted(s.column for s in profile.one_ways)) or "none"
    raise PlatformError(
        "NOT_FOUND",
        f"No stored one-way for column {column!r}",
        404,
        f"FR-62: one-ways are read from the stored Profile, never computed on "
        f"request. Columns with a stored one-way: {available}.",
    )
