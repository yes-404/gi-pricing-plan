"""The Environment and Deployment migration (WK-674 Slice 2, PL-1392 Task 3, Acceptance 3, 13).

One Alembic revision adds `environments` (seeded `dev`, `uat`, `prod`), `deployment_requests`,
`deployments` and the nullable `scoring_traces.deployment_id`, and puts Slice 2a's
`approval_guard()` trigger on `deployment_requests` (evidence-only, no `'flag'` argument).

Everything here runs **Alembic against a scratch database**, the shape of
`test_migration_dataset_owner.py` (its `scratch_database` and `_upgrade` are mirrored, not
invented). The scratch database is upgraded to `2f598e89d12c`, the head before this revision,
rows are inserted at that revision, and then `upgrade head` runs over them: the only way to
test "pre-existing rows keep their value" and the credential pre-check, which a shadow table
cannot reach.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import pathlib
import secrets
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config

# Aliased: pytest collects any module-level name beginning `test_` as a test.
from backend.tests.conftest_db import ENVIRONMENT_SEEDS, empty_the_database
from backend.tests.conftest_db import test_database_url as _test_database_url
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from model_schema import new_uuid7

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

#: The head before this revision (PL-1392, C5), and the SQLSTATE `approval_guard()` raises.
_PREVIOUS_REVISION = "2f598e89d12c"
_THIS_REVISION = "c4a81f6d2e95"  # this migration; head moves on as later slices append
_MIGRATION_FILE = "c4a81f6d2e95_environments_and_deployments.py"
_GUARD_SQLSTATE = "GP001"

_BUNDLE_HASH = "sha256:" + "a" * 64
_SECRET_HASH = "sha256:" + "b" * 64


@pytest_asyncio.fixture
async def scratch_database() -> AsyncIterator[str]:
    """A throwaway database with no migrations applied, dropped on the way out.

    Mirrors `test_migration_dataset_owner.py`'s fixture, except that it **fails** rather
    than skips when PostgreSQL is unreachable: a migration test that skips proves nothing.
    """
    admin_url = make_url(_test_database_url())
    name = f"gip_scratch_{secrets.token_hex(6)}"
    engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            await conn.execute(text(f'CREATE DATABASE "{name}"'))
    except Exception as exc:
        await engine.dispose()
        pytest.fail(f"the migration tests need PostgreSQL at {admin_url.database}: {exc!r}")
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
    cfg = Config(str(_REPO_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_REPO_ROOT / "backend" / "migrations"))
    cfg.set_main_option("prepend_sys_path", str(_REPO_ROOT / "backend" / "src"))
    return cfg


async def _alembic(fn: Callable[..., None], cfg: Config, revision: str) -> None:
    """Off the test's loop: `backend/migrations/env.py` calls `asyncio.run` at import."""
    await asyncio.to_thread(fn, cfg, revision)


async def _upgrade(cfg: Config, revision: str) -> None:
    await _alembic(command.upgrade, cfg, revision)


async def _revision_of(url: str) -> str:
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            return str(
                (await conn.execute(text("SELECT version_num FROM alembic_version"))).scalar_one()
            )
    finally:
        await engine.dispose()


async def _run(url: str, sql: str, params: dict[str, Any] | None = None) -> list[Any]:
    """One statement in its own committed transaction; the rows it returns, if any."""
    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text(sql), params or {})
            return list(result.all()) if result.returns_rows else []
    finally:
        await engine.dispose()


_INSERT_TRACE = """
INSERT INTO scoring_traces (id, workspace_id, rating_version_ref, bundle_hash, sample_reason,
                            environment, blob_sha256, status)
VALUES (:id, :ws, 'rating_version:motor@1', :bundle_hash, 'rate', :environment, :blob, 'complete')
"""


async def _insert_trace(url: str, environment: str | None) -> UUID:
    trace_id = new_uuid7()
    await _run(
        url,
        _INSERT_TRACE,
        {
            "id": trace_id,
            "ws": new_uuid7(),
            "bundle_hash": _BUNDLE_HASH,
            "environment": environment,
            "blob": "c" * 64,
        },
    )
    return trace_id


async def _insert_account(url: str, slug: str, environments: list[str]) -> UUID:
    account_id = new_uuid7()
    await _run(
        url,
        "INSERT INTO service_accounts (id, workspace_id, slug, environments, permissions) "
        "VALUES (:id, :ws, :slug, CAST(:envs AS jsonb), CAST('[]' AS jsonb))",
        {
            "id": account_id,
            "ws": new_uuid7(),
            "slug": slug,
            "envs": "[" + ",".join(f'"{e}"' for e in environments) + "]",
        },
    )
    return account_id


async def _insert_key(
    url: str,
    account_id: UUID,
    environment: str,
    *,
    revoked: bool = False,
    expired: bool = False,
) -> UUID:
    key_id = new_uuid7()
    now = datetime.now(UTC)
    await _run(
        url,
        "INSERT INTO api_keys (id, service_account_id, prefix, secret_hash, environment, "
        "expires_at, revoked_at) VALUES (:id, :sa, :prefix, :secret, :env, :exp, :rev)",
        {
            "id": key_id,
            "sa": account_id,
            "prefix": f"gp_{secrets.token_hex(6)}",
            "secret": _SECRET_HASH,
            "env": environment,
            "exp": now - timedelta(days=1) if expired else now + timedelta(days=30),
            "rev": now if revoked else None,
        },
    )
    return key_id


async def _table_exists(url: str, table: str) -> bool:
    rows = await _run(url, "SELECT to_regclass(:t) IS NOT NULL", {"t": f"public.{table}"})
    return bool(rows[0][0])


async def _environments(url: str) -> list[tuple[str, int, str | None, str | None]]:
    rows = await _run(
        url,
        "SELECT slug, promotion_order, requires_prior_environment, retired_at::text "
        "FROM environments ORDER BY promotion_order",
    )
    return [(r[0], r[1], r[2], r[3]) for r in rows]


# --------------------------------------------------------------------------------------
# Acceptance 3: the seeds, and the rows that existed before
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-428", "FR-417")
async def test_the_upgrade_seeds_the_three_environments_and_leaves_existing_traces_alone(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**Red first.** Predicted failure: the `environments` table does not exist.

    Two `scoring_traces` rows are inserted *before* the upgrade, one in `prod` and one in
    `staging` (a value outside the seeds). Neither had a Deployment to serve it, so both keep
    their `environment` string and get a null `deployment_id`; the column stays a string and
    is never a foreign key, so `staging` cannot dangle.
    """
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    cfg = _alembic_config()
    await _upgrade(cfg, _PREVIOUS_REVISION)
    prod_trace = await _insert_trace(scratch_database, "prod")
    staging_trace = await _insert_trace(scratch_database, "staging")
    assert not await _table_exists(scratch_database, "environments")

    await _upgrade(cfg, "head")

    assert await _environments(scratch_database) == [
        ("dev", 1, None, None),
        ("uat", 2, "dev", None),
        ("prod", 3, "uat", None),
    ]
    rows = await _run(
        scratch_database,
        "SELECT id, environment, deployment_id FROM scoring_traces WHERE id = ANY(:ids)",
        {"ids": [prod_trace, staging_trace]},
    )
    assert {r[0]: (r[1], r[2]) for r in rows} == {
        prod_trace: ("prod", None),
        staging_trace: ("staging", None),
    }


@pytest.mark.req("FR-428")
async def test_an_environment_slug_is_unique_across_every_row(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A slug is never reissued, retired included (RL-1301 A.6, N1)."""
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    await _upgrade(_alembic_config(), "head")
    await _run(scratch_database, "UPDATE environments SET retired_at = now() WHERE slug = 'uat'")
    with pytest.raises(DBAPIError, match="uq_environments_slug"):
        await _run(
            scratch_database,
            "INSERT INTO environments (id, slug, name, promotion_order) "
            "VALUES (:id, 'uat', 'Again', 9)",
            {"id": new_uuid7()},
        )


# --------------------------------------------------------------------------------------
# Acceptance 3: the credential pre-check (auditor-plans V2)
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-428", "FR-389")
async def test_a_key_naming_an_unknown_environment_stops_the_upgrade_before_any_change(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**Deliberately broken input.** An unrevoked `staging` key makes `upgrade head` fail.

    The error names the key id and the name it carries, the database stays at the previous
    revision with no new table, a revoked key and a `uat` key do not block it, and an expired
    but unrevoked key does not either (it is refused at authentication and nothing revives
    it). The account's own list is checked on its own.
    """
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    cfg = _alembic_config()
    await _upgrade(cfg, _PREVIOUS_REVISION)
    account = await _insert_account(scratch_database, "batch", ["uat", "prod"])
    await _insert_key(scratch_database, account, "uat")
    stale = await _insert_key(scratch_database, account, "staging", expired=True)
    bad = await _insert_key(scratch_database, account, "staging")

    with pytest.raises(Exception, match="staging") as caught:
        await _upgrade(cfg, "head")
    assert str(bad) in str(caught.value)
    assert str(stale) not in str(caught.value), "an expired key must not block the upgrade"
    assert await _revision_of(scratch_database) == _PREVIOUS_REVISION
    assert not await _table_exists(scratch_database, "environments")

    await _run(
        scratch_database, "UPDATE api_keys SET revoked_at = now() WHERE id = :id", {"id": bad}
    )
    await _upgrade(cfg, "head")
    assert await _table_exists(scratch_database, "environments")


@pytest.mark.req("FR-428", "FR-389")
async def test_a_service_account_listing_an_unknown_environment_stops_the_upgrade(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    cfg = _alembic_config()
    await _upgrade(cfg, _PREVIOUS_REVISION)
    account = await _insert_account(scratch_database, "legacy", ["dev", "staging"])

    with pytest.raises(Exception, match="staging") as caught:
        await _upgrade(cfg, "head")
    assert str(account) in str(caught.value)
    assert await _revision_of(scratch_database) == _PREVIOUS_REVISION

    # Archived, the account no longer blocks.
    await _run(
        scratch_database,
        "UPDATE service_accounts SET archived_at = now() WHERE id = :id",
        {"id": account},
    )
    await _upgrade(cfg, "head")
    assert await _table_exists(scratch_database, "deployments")


# --------------------------------------------------------------------------------------
# Round trip, privileges
# --------------------------------------------------------------------------------------


async def _trigger_tables(url: str) -> set[str]:
    rows = await _run(
        url,
        "SELECT c.relname FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid "
        "WHERE t.tgname = 'approval_guard' AND NOT t.tgisinternal "
        "AND c.relnamespace = 'public'::regnamespace",
    )
    return {r[0] for r in rows}


async def _has_column(url: str, table: str, column: str) -> bool:
    rows = await _run(
        url,
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = :t AND column_name = :c",
        {"t": table, "c": column},
    )
    return bool(rows)


@pytest.mark.req("FR-417", "FR-428")
async def test_the_migration_round_trips(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """FR-417: `upgrade`, `downgrade -1`, `upgrade`; each step names the revision it reached."""
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    cfg = _alembic_config()
    await _upgrade(cfg, _PREVIOUS_REVISION)
    await _upgrade(cfg, _THIS_REVISION)
    head = await _revision_of(scratch_database)
    assert head == _THIS_REVISION
    tables = ("environments", "deployment_requests", "deployments")
    for table in tables:
        assert await _table_exists(scratch_database, table), table
    assert await _has_column(scratch_database, "scoring_traces", "deployment_id")
    assert "deployment_requests" in await _trigger_tables(scratch_database)

    await _alembic(command.downgrade, cfg, "-1")
    assert await _revision_of(scratch_database) == _PREVIOUS_REVISION
    for table in tables:
        assert not await _table_exists(scratch_database, table), table
    assert not await _has_column(scratch_database, "scoring_traces", "deployment_id")
    assert "deployment_requests" not in await _trigger_tables(scratch_database)
    assert await _trigger_tables(scratch_database), "the downgrade must keep Slice 2a's triggers"

    await _upgrade(cfg, _THIS_REVISION)
    assert await _revision_of(scratch_database) == _THIS_REVISION
    assert "deployment_requests" in await _trigger_tables(scratch_database)


@pytest.mark.req("FR-4", "FR-267")
async def test_the_application_role_cannot_update_or_delete_a_deployment(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A Deployment is a record: no update path in the application (`00` FR-4)."""
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    await _upgrade(_alembic_config(), "head")

    async def privilege(table: str, kind: str) -> bool:
        rows = await _run(
            scratch_database,
            "SELECT has_table_privilege('gip_app', :t, :k)",
            {"t": table, "k": kind},
        )
        return bool(rows[0][0])

    assert await privilege("deployments", "INSERT")
    assert not await privilege("deployments", "UPDATE")
    assert not await privilege("deployments", "DELETE")
    assert not await privilege("environments", "DELETE")
    assert not await privilege("deployment_requests", "DELETE")
    assert await privilege("environments", "UPDATE")
    assert await privilege("deployment_requests", "UPDATE")


# --------------------------------------------------------------------------------------
# Acceptance 13: `deployment_requests` joins the guarded set, evidence-only
# --------------------------------------------------------------------------------------


async def _flag(conn: AsyncConnection, value: str) -> None:
    await conn.execute(text("SELECT set_config('app.approval_decision', :v, true)"), {"v": value})


async def _dev_environment_id(url: str) -> UUID:
    return (await _run(url, "SELECT id FROM environments WHERE slug = 'dev'"))[0][0]


_INSERT_REQUEST = """
INSERT INTO deployment_requests (id, workspace_id, slug, version, environment_id,
    rating_version_ref, status, evidence, change_summary, submitted_by)
VALUES (:id, :ws, 'dev', :version, :env, 'rating_version:motor@1', 'approved',
    CAST(:evidence AS jsonb), 's', :by)
"""


def _request_params(ws: UUID, env: UUID, version: int = 1) -> dict[str, Any]:
    evidence = json.dumps(
        {"rating_version_approval": str(new_uuid7()), "uat_deployment": {"reason": "no uat yet"}}
    )
    return {
        "id": new_uuid7(),
        "ws": ws,
        "version": version,
        "env": env,
        "evidence": evidence,
        "by": new_uuid7(),
    }


async def _approved_request(conn: AsyncConnection, ws: UUID, ref: str, status: str) -> None:
    """An `approval_requests` row as `decide` writes it: under the flag, then reset."""
    await _flag(conn, "on")
    await conn.execute(
        text(
            "INSERT INTO approval_requests (id, workspace_id, artifact_ref, artifact_type, "
            "submitted_by, change_summary, status, approvers_required) "
            "VALUES (:id, :ws, :ref, 'deployment', :by, 's', :status, 1)"
        ),
        {"id": new_uuid7(), "ws": ws, "ref": ref, "by": new_uuid7(), "status": status},
    )
    await _flag(conn, "off")


async def _sqlstate(conn: AsyncConnection, sql: str, params: dict[str, Any]) -> str | None:
    """The SQLSTATE the statement raised (in a savepoint), or `None` when it succeeded."""
    try:
        async with conn.begin_nested():
            await conn.execute(text(sql), params)
    except DBAPIError as exc:
        return str(getattr(exc.orig, "sqlstate", None))
    return None


@pytest.mark.req("FR-351", "FR-356")
async def test_an_approved_deployment_request_needs_a_decided_approval_and_the_flag_is_no_evidence(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The plant, in raw SQL: the guard's refusals and its positive control, at the table.

    The Core and ORM write forms and the full table (other versions, other workspaces) are
    Task 5's; what this proves is that the migration put the evidence-only trigger on the
    table, so the flag **forged** with `set_config` does not satisfy it.
    """
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    await _upgrade(_alembic_config(), "head")
    env = await _dev_environment_id(scratch_database)
    ws = new_uuid7()
    engine = create_async_engine(scratch_database)
    try:
        async with engine.connect() as conn:
            trans = await conn.begin()
            # No approval request at all.
            assert (
                await _sqlstate(conn, _INSERT_REQUEST, _request_params(ws, env)) == _GUARD_SQLSTATE
            )
            # The forgery: the decision flag set by hand does not satisfy an evidence-only table.
            await _flag(conn, "on")
            assert (
                await _sqlstate(conn, _INSERT_REQUEST, _request_params(ws, env)) == _GUARD_SQLSTATE
            )
            await _flag(conn, "off")
            # A request still in `review`, and another version's approval, are not evidence.
            await _approved_request(conn, ws, "deployment:dev@1", "review")
            await _approved_request(conn, ws, "deployment:dev@2", "approved")
            assert (
                await _sqlstate(conn, _INSERT_REQUEST, _request_params(ws, env, 1))
                == _GUARD_SQLSTATE
            )
            # Positive control: a decided request for this exact ref.
            await _approved_request(conn, ws, "deployment:dev@1", "approved")
            assert await _sqlstate(conn, _INSERT_REQUEST, _request_params(ws, env, 1)) is None
            await trans.rollback()
    finally:
        await engine.dispose()


# --------------------------------------------------------------------------------------
# The suite's teardown puts the seeds back
# --------------------------------------------------------------------------------------


def _migration_seeds() -> tuple[tuple[str, str, int, str | None], ...]:
    path = _REPO_ROOT / "backend" / "migrations" / "versions" / _MIGRATION_FILE
    spec = importlib.util.spec_from_file_location("_environments_migration", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return tuple(module.SEEDS)


@pytest.mark.req("FR-428")
async def test_the_teardown_restores_the_three_seeds_the_migration_wrote() -> None:
    """`empty_the_database()` truncates every table, `environments` included, and re-seeds it.

    Without that, the first session to finish leaves a database whose `dev`, `uat` and `prod`
    are gone and every Deployment test after it fails on a missing Environment. The seed
    tuple the teardown uses is pinned equal to the migration's own.
    """
    assert _migration_seeds() == ENVIRONMENT_SEEDS
    await empty_the_database()
    url = _test_database_url()
    assert await _environments(url) == [
        ("dev", 1, None, None),
        ("uat", 2, "dev", None),
        ("prod", 3, "uat", None),
    ]
