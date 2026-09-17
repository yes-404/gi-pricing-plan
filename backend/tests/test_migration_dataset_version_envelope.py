"""OQ-568 (c): the envelope backfill resolves every field, and refuses when it cannot.

`2057e7372a9a` gives a `dataset_versions` row the envelope's nine flat fields. For rows
that already exist the migration answers five questions no other table can: the slug is
the dataset's own; the creator is read back out of the audit chain's
`dataset_version.created` event; `parent_id` is the previous version id in the same
dataset; `updated_at` is the creation moment (OQ-553, resolved (a)); the currency is
the dataset's. It falls back to the workspace's earliest member when no creation event
survived, and stops — `alter_column(nullable=False)` raises — when a row still has no
slug or no creator: inventing a creator for a governed field is worse than a migration
that refuses and says so, the decision `82edffbe1dce` records for `datasets.owner_id`.

Two shapes are used, deliberately, exactly as `test_migration_dataset_owner.py`:

* A **shadow table** — `CREATE TEMP TABLE dataset_versions (LIKE public.dataset_versions
  INCLUDING ALL)` with the backfilled `NOT NULL`s dropped — carries the resolution cases
  and the mutation proofs. `pg_temp` precedes `public` on the search path, so the
  backfills' unqualified `dataset_versions` and `datasets` resolve to the shadows while
  `audit_events` and `workspace_members` still resolve to the real tables. That is what
  lets the migration's own SQL run **verbatim**, which is the point: a test that pastes
  the query proves the paste.
* **Alembic against a scratch database** for the round-trip and the refusal, because
  `alter_column(nullable=False)` is not part of the backfills and is unreachable from the
  shadows.

Everything the shadow tests write lives inside one transaction that is never committed,
including the `audit_events` rows: FR-370 forbids deleting them, and a rollback is not
a delete.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import pathlib
import secrets
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config

# Aliased: pytest collects any module-level name beginning `test_` as a test, and this
# is a helper, not one.
from backend.tests.conftest_db import test_database_url as _test_database_url
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.db.session import Database
from model_schema import ActorKind, JobSource, Principal, new_uuid7

#: Resolved from `__file__`, never from the working directory: pytest may be invoked from
#: anywhere and this test is worthless if it silently reads no migration.
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_MIGRATION = (
    _REPO_ROOT / "backend" / "migrations" / "versions" / "2057e7372a9a_dataset_version_envelope.py"
)

#: The revision under test and the one immediately before it (its `down_revision`).
_REVISION = "2057e7372a9a"
_PREVIOUS_REVISION = "57547846f0a3"


def _backfill_statements() -> tuple[str, ...]:
    """Load `_BACKFILLS` from the migration itself.

    `versions/` has no `__init__.py` and the module name starts with a digit, so it is not
    importable by name. Pasting the SQL into the test instead would test the paste.
    """
    spec = importlib.util.spec_from_file_location("_dataset_version_envelope_migration", _MIGRATION)
    assert spec is not None, f"no import spec for {_MIGRATION}"
    assert spec.loader is not None, f"no loader for {_MIGRATION}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return tuple(module._BACKFILLS)


# --------------------------------------------------------------------------------------
# Shadow table
# --------------------------------------------------------------------------------------


@pytest_asyncio.fixture
async def shadow_versions(database: Database) -> AsyncIterator[AsyncSession]:
    """Writable copies of `dataset_versions` and `datasets`, pre-envelope shape.

    The backfilled columns exist on `public.dataset_versions` (the suite's database is
    migrated to head), so the shadow copies them and drops their `NOT NULL` — the migration
    finds a pre-envelope row as one without them. The datasets shadow drops `currency`'s
    `NOT NULL` so the `COALESCE(d.currency, 'GBP')` fallback is reachable at all.
    """
    async with database.unit_of_work() as session:
        await session.execute(
            text(
                "CREATE TEMP TABLE dataset_versions "
                "(LIKE public.dataset_versions INCLUDING ALL) ON COMMIT DROP"
            )
        )
        await session.execute(
            text(
                "ALTER TABLE pg_temp.dataset_versions ALTER COLUMN slug DROP NOT NULL, "
                "ALTER COLUMN created_by DROP NOT NULL, "
                "ALTER COLUMN updated_at DROP NOT NULL, "
                "ALTER COLUMN labels DROP NOT NULL, "
                "ALTER COLUMN schema_version DROP NOT NULL, "
                "ALTER COLUMN currency DROP NOT NULL"
            )
        )
        await session.execute(
            text("CREATE TEMP TABLE datasets (LIKE public.datasets INCLUDING ALL) ON COMMIT DROP")
        )
        await session.execute(
            text("ALTER TABLE pg_temp.datasets ALTER COLUMN currency DROP NOT NULL")
        )
        yield session
        await session.rollback()


_INSERT_DATASET = """
INSERT INTO datasets (id, workspace_id, slug, name, currency, data_dictionary, owner_id)
VALUES (:id, :workspace_id, :slug, :slug, :currency, '{}'::jsonb, :owner_id)
"""

#: Every `nullable=False` column of `DatasetVersionRow` that has no default. `created_at`
#: is supplied anyway because the `updated_at = created_at` backfill is only provable
#: when the creation moment is known.
_INSERT_VERSION = """
INSERT INTO dataset_versions
    (id, workspace_id, dataset_id, version, status, kind, tables, library_versions, created_at)
VALUES
    (:id, :workspace_id, :dataset_id, :version, 'draft', 'ingested',
     '[]'::jsonb, '{}'::jsonb, :created_at)
"""

#: Every `nullable=False` column of `AuditEventRow` that has no default — the same shape
#: `test_migration_dataset_owner.py` seeds with.
_INSERT_EVENT = """
INSERT INTO audit_events
    (id, workspace_id, actor, source, action, entity_ref, event_hash, sequence, at)
VALUES
    (:id, :workspace_id, CAST(:actor AS jsonb), CAST(:source AS job_source),
     :action, :entity_ref, :event_hash, :sequence, :at)
"""

_INSERT_MEMBER = """
INSERT INTO workspace_members (id, user_id, workspace_id, created_at)
VALUES (:id, :user_id, :workspace_id, :created_at)
"""

#: `workspace_members` carries a foreign key to the **real** `workspaces` (only
#: `dataset_versions` and `datasets` are shadowed), so the fallback test must create the
#: workspace the members belong to.
_INSERT_WORKSPACE = """
INSERT INTO workspaces (id, slug, name)
VALUES (:id, :slug, :slug)
"""


async def _seed_dataset(
    session: AsyncSession, workspace_id: UUID, *, slug: str, currency: str | None = "GBP"
) -> UUID:
    """A Dataset as the migration finds it: an envelope-less version under it."""
    dataset_id = new_uuid7()
    await session.execute(
        text(_INSERT_DATASET),
        {
            "id": dataset_id,
            "workspace_id": workspace_id,
            "slug": slug,
            "currency": currency,
            "owner_id": new_uuid7(),
        },
    )
    return dataset_id


async def _seed_version(
    session: AsyncSession,
    workspace_id: UUID,
    dataset_id: UUID,
    *,
    version: int,
    created_at: datetime | None = None,
) -> UUID:
    version_id = new_uuid7()
    await session.execute(
        text(_INSERT_VERSION),
        {
            "id": version_id,
            "workspace_id": workspace_id,
            "dataset_id": dataset_id,
            "version": version,
            "created_at": created_at or datetime(2026, 8, 14, 9, 0, 0, tzinfo=UTC),
        },
    )
    return version_id


async def _seed_event(
    session: AsyncSession,
    workspace_id: UUID,
    action: str,
    entity_ref: str,
    actor_id: UUID,
    *,
    sequence: int = 1,
    at: datetime | None = None,
) -> None:
    """One row on the real audit chain.

    The actor is built from `model_schema.Principal` and dumped, rather than hand-written
    JSON: `CLAUDE.md` §2 — nobody hand-writes a shape that already exists in the schema,
    and the migration's `->> 'id'` depends on the field name that model chooses.
    """
    actor = Principal(kind=ActorKind.USER, id=actor_id, display="a.actuary@insurer.example")
    await session.execute(
        text(_INSERT_EVENT),
        {
            "id": new_uuid7(),
            "workspace_id": workspace_id,
            "actor": json.dumps(actor.model_dump(mode="json")),
            "source": JobSource.API.value,
            "action": action,
            "entity_ref": entity_ref,
            # Unique and `^sha256:[a-f0-9]{64}$`; the chain itself is not under test here.
            "event_hash": f"sha256:{secrets.token_hex(32)}",
            "sequence": sequence,
            "at": at or datetime.now(UTC),
        },
    )


async def _seed_member(
    session: AsyncSession,
    workspace_id: UUID,
    user_id: UUID,
    *,
    created_at: datetime,
) -> None:
    await session.execute(
        text(_INSERT_MEMBER),
        {
            "id": new_uuid7(),
            "user_id": user_id,
            "workspace_id": workspace_id,
            "created_at": created_at,
        },
    )


async def _envelope_of(session: AsyncSession, version_id: UUID) -> dict[str, object]:
    row = await session.execute(
        text(
            "SELECT slug, created_by, updated_at, parent_id, labels, schema_version, currency "
            "FROM dataset_versions WHERE id = :version_id"
        ),
        {"version_id": version_id},
    )
    return dict(row.mappings().one())


@pytest.mark.req("FR-34")
async def test_the_backfill_resolves_every_field(shadow_versions: AsyncSession) -> None:
    """The happy path: one dataset, two versions, one creation event."""
    workspace, actor = new_uuid7(), new_uuid7()
    created_at = datetime(2026, 8, 14, 9, 0, 0, tzinfo=UTC)
    dataset_id = await _seed_dataset(shadow_versions, workspace, slug="motor-ad", currency="EUR")
    v1 = await _seed_version(
        shadow_versions, workspace, dataset_id, version=1, created_at=created_at
    )
    v2 = await _seed_version(
        shadow_versions, workspace, dataset_id, version=2, created_at=created_at
    )
    await _seed_event(
        shadow_versions, workspace, "dataset_version.created", "dataset_version:motor-ad@1", actor
    )

    for statement in _backfill_statements():
        await shadow_versions.execute(text(statement))

    assert await _envelope_of(shadow_versions, v1) == {
        "slug": "motor-ad",
        "created_by": actor,
        "updated_at": created_at,
        "parent_id": None,
        "labels": {},
        "schema_version": 1,
        "currency": "EUR",
    }
    # v2's parent is v1 — the previous version id in the same dataset.
    assert (await _envelope_of(shadow_versions, v2))["parent_id"] == v1


@pytest.mark.req("FR-34")
async def test_the_currency_falls_back_to_gbp(shadow_versions: AsyncSession) -> None:
    """`COALESCE(d.currency, 'GBP')`, reachable only with the datasets shadow's dropped
    `NOT NULL` — a real dataset always carries a currency, but the statement must not
    depend on that being true of every database it is run against."""
    workspace = new_uuid7()
    dataset_id = await _seed_dataset(shadow_versions, workspace, slug="motor-ad", currency=None)
    v1 = await _seed_version(shadow_versions, workspace, dataset_id, version=1)

    for statement in _backfill_statements():
        await shadow_versions.execute(text(statement))

    assert (await _envelope_of(shadow_versions, v1))["currency"] == "GBP"


@pytest.mark.req("FR-34")
async def test_the_earliest_creation_event_wins_by_sequence(
    shadow_versions: AsyncSession,
) -> None:
    """`ORDER BY sequence`, not `at` — `AuditEventRow` records that `at` has no defined
    order within a millisecond, so the later `sequence` deliberately carries the *earlier*
    `at`, and an `at` ordering picks the wrong actor every time rather than sometimes."""
    workspace = new_uuid7()
    first_by_sequence, second_by_sequence = new_uuid7(), new_uuid7()
    dataset_id = await _seed_dataset(shadow_versions, workspace, slug="motor-ad")
    v1 = await _seed_version(shadow_versions, workspace, dataset_id, version=1)
    later = datetime(2026, 8, 23, 12, 0, 0, tzinfo=UTC)
    earlier = datetime(2026, 8, 23, 11, 0, 0, tzinfo=UTC)
    await _seed_event(
        shadow_versions,
        workspace,
        "dataset_version.created",
        "dataset_version:motor-ad@1",
        first_by_sequence,
        sequence=1,
        at=later,
    )
    await _seed_event(
        shadow_versions,
        workspace,
        "dataset_version.created",
        "dataset_version:motor-ad@1",
        second_by_sequence,
        sequence=2,
        at=earlier,
    )

    for statement in _backfill_statements():
        await shadow_versions.execute(text(statement))

    assert (await _envelope_of(shadow_versions, v1))["created_by"] == first_by_sequence


@pytest.mark.req("FR-34")
async def test_the_backfill_falls_back_to_the_earliest_member(
    shadow_versions: AsyncSession,
) -> None:
    """A version whose creation event did not survive still gets a creator — the
    workspace's earliest member — so the migration cannot stall on old rows."""
    workspace = new_uuid7()
    earlier_member, later_member = new_uuid7(), new_uuid7()
    await shadow_versions.execute(
        text(_INSERT_WORKSPACE), {"id": workspace, "slug": "member-fallback"}
    )
    dataset_id = await _seed_dataset(shadow_versions, workspace, slug="motor-ad")
    v1 = await _seed_version(shadow_versions, workspace, dataset_id, version=1)
    await _seed_member(
        shadow_versions, workspace, later_member, created_at=datetime(2026, 8, 2, tzinfo=UTC)
    )
    await _seed_member(
        shadow_versions, workspace, earlier_member, created_at=datetime(2026, 8, 1, tzinfo=UTC)
    )

    for statement in _backfill_statements():
        await shadow_versions.execute(text(statement))

    assert (await _envelope_of(shadow_versions, v1))["created_by"] == earlier_member


@pytest.mark.req("FR-34")
async def test_a_fingerprint_without_an_extraction_moment_gets_the_creation_moment(
    shadow_versions: AsyncSession,
) -> None:
    """A stored fingerprint with no `extracted_at` cannot be serialised — the model
    requires the field (OQ-568 (c)) — so the backfill answers with the only honest
    moment it has, the version's creation moment, and leaves complete fingerprints alone."""
    workspace = new_uuid7()
    created_at = datetime(2026, 8, 14, 9, 0, 0, tzinfo=UTC)
    dataset_id = await _seed_dataset(shadow_versions, workspace, slug="motor-ad")
    v1 = await _seed_version(
        shadow_versions, workspace, dataset_id, version=1, created_at=created_at
    )
    await shadow_versions.execute(
        text(
            "UPDATE dataset_versions SET source_fingerprint = "
            '\'{"kind": "file_sha256", "value": "a"}\'::jsonb WHERE id = :id'
        ),
        {"id": v1},
    )

    for statement in _backfill_statements():
        await shadow_versions.execute(text(statement))

    row = (
        await shadow_versions.execute(
            text(
                "SELECT source_fingerprint ->> 'extracted_at' AS extracted_at "
                "FROM dataset_versions WHERE id = :id"
            ),
            {"id": v1},
        )
    ).scalar_one()
    assert row == "2026-08-14T09:00:00+00:00"


@pytest.mark.req("FR-34")
async def test_another_versions_event_does_not_resolve(
    shadow_versions: AsyncSession,
) -> None:
    """**Negative.** The `entity_ref` is matched exactly, `dataset_version:{slug}@{version}`.

    A neighbouring slug (`motor` and `motor-ad`) or another version's event (`@2`) must
    not lend its actor: without the exact match, the first would borrow the second's
    creator silently, and only for datasets whose names happen to nest.
    """
    workspace, actor = new_uuid7(), new_uuid7()
    dataset_id = await _seed_dataset(shadow_versions, workspace, slug="motor-ad")
    v1 = await _seed_version(shadow_versions, workspace, dataset_id, version=1)
    await _seed_event(
        shadow_versions,
        workspace,
        "dataset_version.created",
        "dataset_version:motor@1",
        actor,
        sequence=1,
    )
    await _seed_event(
        shadow_versions,
        workspace,
        "dataset_version.created",
        "dataset_version:motor-ad@2",
        actor,
        sequence=2,
    )

    for statement in _backfill_statements():
        await shadow_versions.execute(text(statement))

    assert (await _envelope_of(shadow_versions, v1))["created_by"] is None


# --------------------------------------------------------------------------------------
# Mutation proofs: the guards are load-bearing, not incidental
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-34")
async def test_a_prefix_matching_backfill_would_be_caught(
    shadow_versions: AsyncSession,
) -> None:
    """The exact-match guard, proven to bite: weaken it to a slug prefix and `motor`
    borrows `motor-ad`'s creator.

    The pattern drops the version and matches `LIKE 'dataset_version:{slug}%'` — the
    wildcard-pathspec shape, where `dataset_version:motor%` resolves
    `dataset_version:motor-ad@1`. The real query's equality must not, and the negative
    above asserts exactly that.
    """
    statements = _backfill_statements()
    creator = statements[2]
    widened = creator.replace(
        "a.entity_ref = 'dataset_version:' || d.slug || '@' || v.version",
        "a.entity_ref LIKE 'dataset_version:' || d.slug || '%'",
    )
    assert widened != creator, "the equality moved; this proof no longer mutates it"
    narrowed = tuple(widened if s == creator else s for s in statements)

    workspace, actor = new_uuid7(), new_uuid7()
    dataset_id = await _seed_dataset(shadow_versions, workspace, slug="motor")
    v1 = await _seed_version(shadow_versions, workspace, dataset_id, version=1)
    await _seed_event(
        shadow_versions, workspace, "dataset_version.created", "dataset_version:motor-ad@1", actor
    )

    for statement in narrowed:
        await shadow_versions.execute(text(statement))

    # Exactly what the real query must not do, and what the negative above asserts it does not.
    assert (await _envelope_of(shadow_versions, v1))["created_by"] == actor


# --------------------------------------------------------------------------------------
# The round-trip and the refusal, through alembic
# --------------------------------------------------------------------------------------


@pytest_asyncio.fixture
async def scratch_database() -> AsyncIterator[str]:
    """A throwaway database with no migrations applied, dropped on the way out."""
    admin_url = make_url(_test_database_url())
    name = f"gip_scratch_{secrets.token_hex(6)}"
    engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            await conn.execute(text(f'CREATE DATABASE "{name}"'))
    except Exception as exc:
        await engine.dispose()
        pytest.skip(f"PostgreSQL not reachable at {admin_url.database}: {type(exc).__name__}")

    try:
        yield admin_url.set(database=name).render_as_string(hide_password=False)
    finally:
        async with engine.connect() as conn:
            await conn.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :name AND pid <> pg_backend_pid()"
                ),
                {"name": name},
            )
            await conn.execute(text(f'DROP DATABASE IF EXISTS "{name}"'))
        await engine.dispose()


def _alembic_config() -> Config:
    """The repository's alembic config, with both relative paths made absolute."""
    cfg = Config(str(_REPO_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_REPO_ROOT / "backend" / "migrations"))
    cfg.set_main_option("prepend_sys_path", str(_REPO_ROOT / "backend" / "src"))
    return cfg


async def _upgrade(cfg: Config, revision: str) -> None:
    """Run `alembic upgrade` off the test's event loop.

    `backend/migrations/env.py` calls `asyncio.run(...)` at import, which raises from
    inside a running loop. `to_thread` gives it a thread with no loop of its own.
    """
    await asyncio.to_thread(command.upgrade, cfg, revision)


@pytest.mark.req("FR-34")
async def test_the_migration_round_trips_on_seeded_data(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Upgrade and downgrade both round-trip, on a database with real rows.

    The shadow tables prove the backfill statements; this proves the whole revision —
    DDL included — leaves the schema exactly as it found it, and that the backfills run
    against a real, populated database rather than only a shadow.
    """
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    cfg = _alembic_config()

    await _upgrade(cfg, _PREVIOUS_REVISION)

    engine = create_async_engine(scratch_database)
    try:
        async with engine.begin() as conn:
            workspace, actor = new_uuid7(), new_uuid7()
            dataset_id = new_uuid7()
            await conn.execute(
                text(_INSERT_DATASET),
                {
                    "id": dataset_id,
                    "workspace_id": workspace,
                    "slug": "motor",
                    "currency": "EUR",
                    "owner_id": new_uuid7(),
                },
            )
            await conn.execute(
                text(_INSERT_VERSION),
                {
                    "id": new_uuid7(),
                    "workspace_id": workspace,
                    "dataset_id": dataset_id,
                    "version": 1,
                    "created_at": datetime(2026, 8, 14, 9, 0, 0, tzinfo=UTC),
                },
            )
            await conn.execute(
                text(_INSERT_EVENT),
                {
                    "id": new_uuid7(),
                    "workspace_id": workspace,
                    "actor": json.dumps(
                        Principal(
                            kind=ActorKind.USER, id=actor, display="a.actuary@example"
                        ).model_dump(mode="json")
                    ),
                    "source": JobSource.API.value,
                    "action": "dataset_version.created",
                    "entity_ref": "dataset_version:motor@1",
                    "event_hash": f"sha256:{secrets.token_hex(32)}",
                    "sequence": 1,
                    "at": datetime.now(UTC),
                },
            )
    finally:
        await engine.dispose()

    await _upgrade(cfg, _REVISION)

    engine = create_async_engine(scratch_database)
    try:
        async with engine.connect() as conn:
            row = (
                (
                    await conn.execute(
                        text(
                            "SELECT slug, created_by, updated_at, labels, schema_version, currency "
                            "FROM dataset_versions"
                        )
                    )
                )
                .mappings()
                .one()
            )
            assert row["slug"] == "motor"
            assert row["created_by"] == actor
            assert row["updated_at"] == datetime(2026, 8, 14, 9, 0, 0, tzinfo=UTC)
            assert row["labels"] == {}
            assert row["schema_version"] == 1
            # The version copies its dataset's currency; the `COALESCE(..., 'GBP')`
            # fallback is proven in the shadow tests.
            assert row["currency"] == "EUR"
    finally:
        await engine.dispose()

    await asyncio.to_thread(command.downgrade, cfg, _PREVIOUS_REVISION)

    engine = create_async_engine(scratch_database)
    try:
        async with engine.connect() as conn:
            # The nine columns are gone: selecting one fails on the missing column.
            with pytest.raises(DBAPIError, match="slug"):
                await conn.execute(text("SELECT slug FROM dataset_versions"))
    finally:
        await engine.dispose()


@pytest.mark.req("FR-34")
async def test_a_version_with_no_creator_stops_the_migration(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**Deliberately broken input.** A version whose creation event did not survive and
    whose workspace has no members has no creator to resolve.

    The migration must refuse and name the column, not invent one — the branch the
    governed-field argument rests on, and the shadow tables cannot reach it:
    `alter_column(nullable=False)` is not part of `_BACKFILLS`.
    """
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    cfg = _alembic_config()

    await _upgrade(cfg, _PREVIOUS_REVISION)

    engine = create_async_engine(scratch_database)
    try:
        async with engine.begin() as conn:
            workspace = new_uuid7()
            dataset_id = new_uuid7()
            await conn.execute(
                text(_INSERT_DATASET),
                {
                    "id": dataset_id,
                    "workspace_id": workspace,
                    "slug": "orphaned",
                    "currency": "GBP",
                    "owner_id": new_uuid7(),
                },
            )
            await conn.execute(
                text(_INSERT_VERSION),
                {
                    "id": new_uuid7(),
                    "workspace_id": workspace,
                    "dataset_id": dataset_id,
                    "version": 1,
                    "created_at": datetime(2026, 8, 14, 9, 0, 0, tzinfo=UTC),
                },
            )
    finally:
        await engine.dispose()

    # The column, by name, is what the operator has to act on.
    with pytest.raises(DBAPIError, match="created_by") as caught:
        await _upgrade(cfg, _REVISION)

    assert "contains null values" in str(caught.value), str(caught.value)
