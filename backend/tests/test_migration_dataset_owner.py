"""The FR-82 owner backfill resolves an owner, and refuses when it cannot.

`82edffbe1dce` gives a Dataset a non-null `owner_id`. For a Dataset that already existed
the only record of who created it is the audit chain, so the migration reads it back out
with a `LIKE` over `entity_ref` and an `ORDER BY sequence`. Four things in that query can
be wrong in ways nothing else in this repository would notice, and **no other test here
exercises a migration at all**.

Two shapes are used, deliberately:

* A **shadow table** — `CREATE TEMP TABLE datasets (LIKE public.datasets INCLUDING ALL)`
  with the `NOT NULL` dropped — carries the resolution cases and the two mutation proofs.
  `pg_temp` precedes `public` on the search path, so `_BACKFILL`'s unqualified `datasets`
  resolves to the shadow while its `audit_events` still resolves to the real table. That
  is what lets the migration's own SQL run **verbatim**, which is the point: a test that
  pastes the query proves the paste.
* **Alembic against a scratch database** for the refusal, because
  `alter_column(nullable=False)` is not part of `_BACKFILL` and is unreachable from the
  shadow table. It is also the migration's most consequential line — inventing an owner
  for a governed field is worse than a migration that stops.

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
_MIGRATION = _REPO_ROOT / "backend" / "migrations" / "versions" / "82edffbe1dce_dataset_owner.py"

#: The revision under test and the one immediately before it (its `down_revision`).
_REVISION = "82edffbe1dce"
_PREVIOUS_REVISION = "7c1a9e40b3d2"


def _backfill_sql() -> str:
    """Load `_BACKFILL` from the migration itself.

    `versions/` has no `__init__.py` and the module name starts with a digit, so it is not
    importable by name. Pasting the SQL into the test instead would test the paste.
    """
    spec = importlib.util.spec_from_file_location("_dataset_owner_migration", _MIGRATION)
    assert spec is not None, f"no import spec for {_MIGRATION}"
    assert spec.loader is not None, f"no loader for {_MIGRATION}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return str(module._BACKFILL)


# --------------------------------------------------------------------------------------
# Shadow table
# --------------------------------------------------------------------------------------


@pytest_asyncio.fixture
async def shadow_datasets(database: Database) -> AsyncIterator[AsyncSession]:
    """A writable copy of `datasets` with `owner_id` nullable, in this transaction only.

    `INCLUDING ALL` copies defaults, constraints and indexes but never foreign keys, which
    is what is wanted here — the shadow rows reference nothing. `ON COMMIT DROP` plus the
    rollback below means nothing outlives the test either way.
    """
    async with database.unit_of_work() as session:
        await session.execute(
            text("CREATE TEMP TABLE datasets (LIKE public.datasets INCLUDING ALL) ON COMMIT DROP")
        )
        await session.execute(
            text("ALTER TABLE pg_temp.datasets ALTER COLUMN owner_id DROP NOT NULL")
        )
        yield session
        await session.rollback()


_INSERT_DATASET = """
INSERT INTO datasets (id, workspace_id, slug, name, currency, data_dictionary)
VALUES (:id, :workspace_id, :slug, :slug, 'GBP', '{}'::jsonb)
"""

#: Every `nullable=False` column of `AuditEventRow` that has no default. `id` has a Python
#: default and `at` a server default, so neither is required — `at` is supplied anyway
#: because one test needs the `at` order to disagree with the `sequence` order.
_INSERT_EVENT = """
INSERT INTO audit_events
    (id, workspace_id, actor, source, action, entity_ref, event_hash, sequence, at)
VALUES
    (:id, :workspace_id, CAST(:actor AS jsonb), CAST(:source AS job_source),
     :action, :entity_ref, :event_hash, :sequence, :at)
"""


async def _seed_dataset(session: AsyncSession, workspace_id: UUID, *, slug: str) -> None:
    """A pre-existing Dataset, as the migration finds it: `owner_id` still NULL."""
    await session.execute(
        text(_INSERT_DATASET),
        {"id": new_uuid7(), "workspace_id": workspace_id, "slug": slug},
    )


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


async def _owner_of(session: AsyncSession, slug: str) -> UUID | None:
    row = await session.execute(
        text("SELECT owner_id FROM datasets WHERE slug = :slug"), {"slug": slug}
    )
    owner: UUID | None = row.scalar_one()
    return owner


@pytest.mark.req("FR-82")
async def test_the_backfill_resolves_an_owner_from_the_creation_event(
    shadow_datasets: AsyncSession,
) -> None:
    """The happy path, and the only one the migration was shipped with any confidence in."""
    workspace, actor = new_uuid7(), new_uuid7()
    await _seed_dataset(shadow_datasets, workspace, slug="motor-ad")
    await _seed_event(shadow_datasets, workspace, "dataset.created", "dataset:motor-ad@1", actor)

    await shadow_datasets.execute(text(_backfill_sql()))

    assert await _owner_of(shadow_datasets, "motor-ad") == actor


@pytest.mark.req("FR-82")
async def test_the_earliest_creation_event_wins_by_sequence(
    shadow_datasets: AsyncSession,
) -> None:
    """`ORDER BY sequence`, not `at`.

    `AuditEventRow:198-201` records that `at` has no defined order within a millisecond, so
    two events written in the same millisecond would resolve arbitrarily under an `at`
    ordering — and such a test would pass most of the time, which is worse than failing.
    Here the later `sequence` deliberately carries the *earlier* `at`, so an `at` ordering
    picks the wrong actor every time rather than sometimes.
    """
    workspace = new_uuid7()
    first_by_sequence, second_by_sequence = new_uuid7(), new_uuid7()
    later = datetime(2026, 8, 23, 12, 0, 0, tzinfo=UTC)
    earlier = datetime(2026, 8, 23, 11, 0, 0, tzinfo=UTC)
    await _seed_dataset(shadow_datasets, workspace, slug="motor-ad")
    await _seed_event(
        shadow_datasets,
        workspace,
        "dataset.created",
        "dataset:motor-ad@1",
        first_by_sequence,
        sequence=1,
        at=later,
    )
    await _seed_event(
        shadow_datasets,
        workspace,
        "dataset.created",
        "dataset:motor-ad@1",
        second_by_sequence,
        sequence=2,
        at=earlier,
    )

    await shadow_datasets.execute(text(_backfill_sql()))

    assert await _owner_of(shadow_datasets, "motor-ad") == first_by_sequence


@pytest.mark.req("FR-82")
async def test_a_slug_that_prefixes_another_does_not_borrow_its_owner(
    shadow_datasets: AsyncSession,
) -> None:
    """**Negative.** `LIKE 'dataset:' || slug || '@%'` and not `... || '%'`.

    `motor` and `motor-ad` are ordinary neighbouring slugs. Without the `@` the first would
    resolve to the second's creator, silently and only for datasets whose names happen to
    nest — the kind of defect that survives review and appears as a governance question a
    year later.
    """
    workspace, actor = new_uuid7(), new_uuid7()
    await _seed_dataset(shadow_datasets, workspace, slug="motor")
    await _seed_dataset(shadow_datasets, workspace, slug="motor-ad")
    await _seed_event(shadow_datasets, workspace, "dataset.created", "dataset:motor-ad@1", actor)

    await shadow_datasets.execute(text(_backfill_sql()))

    assert await _owner_of(shadow_datasets, "motor") is None
    assert await _owner_of(shadow_datasets, "motor-ad") == actor


@pytest.mark.req("FR-82")
async def test_any_version_in_the_ref_resolves(shadow_datasets: AsyncSession) -> None:
    """`@%`, deliberately, and the migration's comment at :31-36 says why.

    `dataset.created` writes `@1` today, but `platform/datasets.py:951` writes a UUID where
    the rest write the slug and `:293` omits `@version` altogether. Those inconsistencies
    are what the migration must survive; narrowing to `@1` would stop resolving rows the
    day one of them is fixed. Asserting `@7` resolves is what stops a later tidy-up from
    narrowing it.
    """
    workspace, actor = new_uuid7(), new_uuid7()
    await _seed_dataset(shadow_datasets, workspace, slug="motor-ad")
    await _seed_event(shadow_datasets, workspace, "dataset.created", "dataset:motor-ad@7", actor)

    await shadow_datasets.execute(text(_backfill_sql()))

    assert await _owner_of(shadow_datasets, "motor-ad") == actor


@pytest.mark.req("FR-82")
async def test_the_inconsistent_refs_are_not_picked_up(shadow_datasets: AsyncSession) -> None:
    """**Negative**, and the only way those two inconsistencies are reachable at all.

    `dataset.subject_purged` writes `dataset:<uuid>@1` (`datasets.py:951`) and
    `dataset.dictionary_updated` writes `dataset:<slug>` with no `@` (`:293`). Neither is a
    `dataset.created`, and neither matches `dataset:<slug>@%` either — the first because
    the ref carries an id where the slug belongs, the second because there is no `@`.
    Planting both and proving the Dataset stays unowned pins both facts at once.
    """
    workspace = new_uuid7()
    dataset_id = new_uuid7()
    await _seed_dataset(shadow_datasets, workspace, slug="motor-ad")
    await _seed_event(
        shadow_datasets,
        workspace,
        "dataset.subject_purged",
        f"dataset:{dataset_id}@1",
        new_uuid7(),
        sequence=1,
    )
    await _seed_event(
        shadow_datasets,
        workspace,
        "dataset.dictionary_updated",
        "dataset:motor-ad",
        new_uuid7(),
        sequence=2,
    )

    await shadow_datasets.execute(text(_backfill_sql()))

    assert await _owner_of(shadow_datasets, "motor-ad") is None


# --------------------------------------------------------------------------------------
# Mutation proofs: the two guards are load-bearing, not incidental
# --------------------------------------------------------------------------------------
#
# Both mutate the *loaded copy* of the SQL, so nothing on disk changes and the merged
# migration is never edited. `CLAUDE.md` §13: a check that has never printed a failure has
# not been tested.


@pytest.mark.req("FR-82")
async def test_a_prefix_matching_backfill_would_be_caught(shadow_datasets: AsyncSession) -> None:
    """The `@` guard, proven to bite: widen the `LIKE` and `motor` borrows `motor-ad`'s owner."""
    widened = _backfill_sql().replace("|| '@%'", "|| '%'")
    assert widened != _backfill_sql(), "the LIKE pattern moved; this proof no longer mutates it"

    workspace, actor = new_uuid7(), new_uuid7()
    await _seed_dataset(shadow_datasets, workspace, slug="motor")
    await _seed_dataset(shadow_datasets, workspace, slug="motor-ad")
    await _seed_event(shadow_datasets, workspace, "dataset.created", "dataset:motor-ad@1", actor)

    await shadow_datasets.execute(text(widened))

    # Exactly what the real query must not do, and what the negative above asserts it does not.
    assert await _owner_of(shadow_datasets, "motor") == actor


@pytest.mark.req("FR-82")
async def test_an_unfiltered_backfill_would_be_caught(shadow_datasets: AsyncSession) -> None:
    """The action filter, proven to bite.

    A Dataset with no `dataset.created` on the chain — its creation predates auditing, or
    the event was written under a different action — has no owner to resolve. Drop
    `AND a.action = 'dataset.created'` and any later event on the same ref answers instead,
    which is how a migration invents an owner without anyone noticing. Both queries run
    against one seeding, so the difference is the filter and nothing else.
    """
    workspace, actor = new_uuid7(), new_uuid7()
    await _seed_dataset(shadow_datasets, workspace, slug="motor-ad")
    await _seed_event(shadow_datasets, workspace, "dataset.archived", "dataset:motor-ad@2", actor)

    # The behavioural assertion comes first, deliberately: it is the one that must fail if
    # the filter is ever dropped from the migration, and a structural guard placed above it
    # would fire first and hide it.
    await shadow_datasets.execute(text(_backfill_sql()))
    assert await _owner_of(shadow_datasets, "motor-ad") is None

    unfiltered = _backfill_sql().replace("       AND a.action = 'dataset.created'\n", "")
    assert unfiltered != _backfill_sql(), "the action filter moved; this proof no longer mutates it"

    await shadow_datasets.execute(text(unfiltered))
    assert await _owner_of(shadow_datasets, "motor-ad") == actor


# --------------------------------------------------------------------------------------
# The refusal, through alembic
# --------------------------------------------------------------------------------------


@pytest_asyncio.fixture
async def scratch_database() -> AsyncIterator[str]:
    """A throwaway database with no migrations applied, dropped on the way out.

    Skips rather than fails when nothing is listening, matching `conftest_db.py`'s idiom:
    a developer without the compose stack up should still be able to run the unit tests,
    and CI provides the service so the skip never hides a regression there.
    """
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
    """The repository's alembic config, with both relative paths made absolute.

    `alembic.ini` resolves `script_location` and `prepend_sys_path` against the working
    directory, and a test must not depend on where pytest was invoked from.
    """
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


@pytest.mark.req("FR-82")
async def test_an_unresolvable_dataset_stops_the_migration(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**Deliberately broken input.** A Dataset with no creation event has no owner.

    The migration must refuse and name the column, not invent one. This is the branch the
    requirement's governance argument rests on, and the shadow-table tests cannot reach it:
    `alter_column(nullable=False)` is not part of `_BACKFILL`.

    `env.py` reads the DSN from `Settings`, never from `alembic.ini`, so the scratch
    database is selected through the environment variable the application itself uses.
    """
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    cfg = _alembic_config()

    await _upgrade(cfg, _PREVIOUS_REVISION)

    engine = create_async_engine(scratch_database)
    try:
        async with engine.begin() as conn:
            # `owner_id` does not exist yet at this revision, which is the whole point.
            await conn.execute(
                text(_INSERT_DATASET),
                {"id": new_uuid7(), "workspace_id": new_uuid7(), "slug": "orphaned"},
            )
    finally:
        await engine.dispose()

    # The column, by name, is what the operator has to act on — "some row somewhere is
    # null" would not be a usable refusal.
    with pytest.raises(DBAPIError, match="owner_id") as caught:
        await _upgrade(cfg, _REVISION)

    assert "contains null values" in str(caught.value), str(caught.value)
