"""A data-frozen Dataset Version is never re-profiled (`01` FR-60; PL-1769 Step 2.10).

The maintainer (by delegation), `to-lead.md` "2026-10-14 15:14:52 BST" (4) and "15:32:52 BST":
no requirement allows re-profiling a validated version, so `dataset_versions_snapshot_guard()`
refuses a re-point of `profile_id` after the data freezes, and `store_profile` refuses it first
with the named, existing `DATASET_VERSION_IMMUTABLE` (`409`) -- never a raw trigger exception,
which the API would turn into a `500`.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from backend.tests.conftest_db import grant_roles_as_owner
from sqlalchemy import func, select, text

from app.db.models import DatasetVersionRow, ProfileRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import datasets, profiles
from model_schema import ActorKind, Principal, Profile, new_uuid7

ACTOR = Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@insurer.example")


async def _grant(database: Database, workspace_id: UUID) -> None:
    await grant_roles_as_owner(workspace_id, ACTOR.id, "analyst")


async def _version(database: Database, workspace_id: UUID) -> UUID:
    await _grant(database, workspace_id)
    async with database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=ACTOR, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        version = await datasets.new_version(
            session, workspace_id=workspace_id, actor=ACTOR, dataset_id=dataset.id
        )
        return version.id


def _profile(version_id: UUID) -> Profile:
    return Profile(
        id=uuid4(),
        dataset_version_id=version_id,
        computed_at=datetime.now(UTC),
        row_count=10,
        columns=(),
        one_ways=(),
    )


async def _store(database: Database, workspace_id: UUID, version_id: UUID) -> UUID:
    profile = _profile(version_id)
    async with database.unit_of_work() as session:
        await profiles.store_profile(
            session, workspace_id=workspace_id, actor=ACTOR, profile=profile
        )
    return profile.id


async def _begin_validation(database: Database, workspace_id: UUID, version_id: UUID) -> None:
    async with database.unit_of_work() as session:
        await datasets.begin_validation(
            session, workspace_id=workspace_id, actor=ACTOR, version_id=version_id
        )


async def _profile_count(database: Database, version_id: UUID) -> int:
    async with database.session() as session:
        return (
            await session.execute(
                select(func.count())
                .select_from(ProfileRow)
                .where(ProfileRow.dataset_version_id == version_id)
            )
        ).scalar_one()


@pytest.mark.req("FR-60")
async def test_a_data_frozen_version_with_a_profile_refuses_a_second_one_by_name(
    database: Database, workspace_id: UUID
) -> None:
    """The red: without the application check the trigger's raw refusal escapes instead."""
    version_id = await _version(database, workspace_id)
    first = await _store(database, workspace_id, version_id)
    await _begin_validation(database, workspace_id, version_id)  # the data freezes here

    with pytest.raises(PlatformError) as refused:
        await _store(database, workspace_id, version_id)

    assert refused.value.code == "DATASET_VERSION_IMMUTABLE"
    assert refused.value.status_code == 409
    assert "FR-60" in (refused.value.detail or "")
    assert await _profile_count(database, version_id) == 1  # no profiles row was added
    async with database.session() as session:
        pinned = await session.scalar(
            select(DatasetVersionRow.profile_id).where(DatasetVersionRow.id == version_id)
        )
    assert pinned == first


@pytest.mark.req("FR-60")
async def test_a_data_frozen_version_without_a_profile_takes_its_first(
    database: Database, workspace_id: UUID
) -> None:
    """A profiling Job that finishes after validation began records the profile of the data."""
    version_id = await _version(database, workspace_id)
    await _begin_validation(database, workspace_id, version_id)

    profile_id = await _store(database, workspace_id, version_id)

    async with database.session() as session:
        pinned = await session.scalar(
            select(DatasetVersionRow.profile_id).where(DatasetVersionRow.id == version_id)
        )
        frozen = await session.scalar(
            text("SELECT data_frozen_at FROM dataset_versions WHERE id = :id"),
            {"id": version_id},
        )
    assert pinned == profile_id
    assert frozen is not None


@pytest.mark.req("FR-60")
async def test_a_never_validated_draft_may_still_be_re_profiled(
    database: Database, workspace_id: UUID
) -> None:
    """Before the data freezes, a profile adds a row and re-points (the unchanged rule 6)."""
    version_id = await _version(database, workspace_id)
    await _store(database, workspace_id, version_id)
    second = await _store(database, workspace_id, version_id)

    assert await _profile_count(database, version_id) == 2
    async with database.session() as session:
        pinned = await session.scalar(
            select(DatasetVersionRow.profile_id).where(DatasetVersionRow.id == version_id)
        )
    assert pinned == second
