"""The backfill migration `c3a8e51f7d20`, run rather than trusted (#1504 N3).

The migration freezes a copy of the owner SQL (a migration describes the schema as it was), and
the registry tests exercise `blobs.backfill_ref_counts`, not that copy. These run the revision's
own `upgrade()` against the test database through Alembic's operations, on planted blobs: a
two-owner blob at 0, an ownerless blob at 0 (the pin), and a blob held above its owner count.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from backend.tests.blob_fixtures import job_result_owner
from sqlalchemy.engine import Connection

from app.db.models import BlobRow
from app.db.session import Database
from app.platform import blobs
from app.platform.blobs import BLOB_OWNERS, BlobStore
from model_schema import new_uuid7

REVISION = (
    Path(__file__).resolve().parents[1]
    / "migrations"
    / "versions"
    / "c3a8e51f7d20_backfill_blob_reference_counts.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("c3a8e51f7d20", REVISION)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _upgrade(connection: Connection) -> None:
    with Operations.context(MigrationContext.configure(connection)):
        _load().upgrade()


async def _run_upgrade(database: Database) -> None:
    async with database.engine.begin() as connection:
        await connection.run_sync(_upgrade)


async def _unowned(database: Database, blob_store: BlobStore, label: bytes) -> str:
    """A blob at ref_count 0, as before slice 1 (put, then its reference released)."""
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, label + b" " + str(new_uuid7()).encode(), "text/plain")
        await blobs.release(session, ref.sha256)
    return ref.sha256


async def _count(database: Database, sha256: str) -> int:
    async with database.session() as session:
        row = await session.get(BlobRow, sha256)
        assert row is not None
        await session.refresh(row)
        return row.ref_count


@pytest.mark.req("FR-416")
@pytest.mark.req("FR-420")
async def test_the_revision_counts_owners_pins_the_ownerless_and_never_lowers(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Breakers: edit an owner line in `_OWNERS` -> `two` stays 0; drop the pin UPDATE -> `orphan`
    stays 0 and is collectable; make the first UPDATE unconditional -> `held` falls to 1."""
    two = await _unowned(database, blob_store, b"two owners")
    for _ in range(2):
        await job_result_owner(database, workspace_id, two)

    orphan = await _unowned(database, blob_store, b"no visible owner")

    held = await _unowned(database, blob_store, b"held above its owners")
    async with database.unit_of_work() as session:
        for _ in range(5):
            await blobs.retain(session, held)
    await job_result_owner(database, workspace_id, held)

    await _run_upgrade(database)
    assert await _count(database, two) == 2
    assert await _count(database, orphan) == 1  # the pin
    assert await _count(database, held) == 5  # never lowered

    await _run_upgrade(database)  # idempotent
    assert await _count(database, two) == 2
    assert await _count(database, orphan) == 1
    assert await _count(database, held) == 5


@pytest.mark.req("FR-416")
def test_the_revisions_frozen_owner_sql_is_a_subset_of_the_registry() -> None:
    """The revision's copy is frozen, the registry grows: every frozen line must still be a
    registered owner, so an edit to one side that breaks the other shows here. Positive control
    on a planted drift below."""
    registry = {owner.digests for owner in BLOB_OWNERS}
    assert set(_load()._OWNERS) <= registry


@pytest.mark.req("FR-416")
def test_a_drifted_frozen_line_would_be_found() -> None:
    registry = {owner.digests for owner in BLOB_OWNERS}
    drifted = {*_load()._OWNERS[:-1], "SELECT sha256 FROM scoring_traces"}
    assert not drifted <= registry


@pytest.mark.req("FR-416")
def test_the_downgrade_says_it_is_irreversible() -> None:
    module = _load()
    assert "Irreversible: a no-op" in (module.downgrade.__doc__ or "")
    assert "irreversible: a no-op" in (module.__doc__ or "").lower()
