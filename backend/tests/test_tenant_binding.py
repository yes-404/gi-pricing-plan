"""FR-436: a deployment is bound to one tenant, and refuses to start when any store disagrees.

Every startup test enters `TestClient(create_app(...))`, whose context manager runs the
lifespan's startup and re-raises what it raises. The stores are real: PostgreSQL, MinIO and
Redis. Each test gets its own bucket and its own Redis database index, so a mismatch marker
one test plants cannot be seen by another, or by a concurrent run.
"""

from __future__ import annotations

import asyncio
import os
import secrets
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
import pytest_asyncio
import redis.asyncio
from backend.tests.conftest_db import test_blob_bucket, test_database_url
from backend.tests.test_migration_dataset_owner import (  # noqa: F401  (fixture + helpers)
    _alembic_config,
    _upgrade,
    scratch_database,
)
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import Settings
from app.main import create_app
from app.platform.blobs import BlobStore
from app.platform.tenancy import TENANT_BLOB_KEY, TENANT_REDIS_KEY, TenantMismatchError

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MARKER_MIGRATION_DOWN_REVISION = "c4d1e8a7b302"


@pytest.fixture
def redis_url() -> str:
    """A Redis database index of its own, so a planted marker stays in this test."""
    return f"redis://localhost:6379/{1 + secrets.randbelow(15)}"


@pytest.fixture
def stores(redis_url: str) -> Iterator[Settings]:
    """Settings for the shared test database, a bucket that does not exist yet, and a
    Redis database with no marker. Bucket and key are removed afterwards."""
    settings = Settings(
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        blob_bucket=f"gip-tenant-{secrets.token_hex(6)}",
        redis_url=SecretStr(redis_url),
    )
    yield settings
    asyncio.run(_teardown(settings))


async def _teardown(settings: Settings) -> None:
    client = BlobStore(settings)._client
    try:
        for obj in client.list_objects_v2(Bucket=settings.blob_bucket).get("Contents", []):
            client.delete_object(Bucket=settings.blob_bucket, Key=obj["Key"])
        client.delete_bucket(Bucket=settings.blob_bucket)
    except Exception:  # the bucket was never created
        pass
    r = redis.asyncio.from_url(settings.redis_url.get_secret_value())  # type: ignore[no-untyped-call]
    await r.delete(TENANT_REDIS_KEY)
    await r.aclose()


def _blob_marker(settings: Settings) -> str | None:
    client = BlobStore(settings)._client
    try:
        return client.get_object(Bucket=settings.blob_bucket, Key=TENANT_BLOB_KEY)[
            "Body"
        ].read().decode()
    except (client.exceptions.NoSuchKey, client.exceptions.NoSuchBucket):
        return None


def _plant_blob_marker(settings: Settings, tenant: str) -> None:
    async def _go() -> None:
        store = BlobStore(settings)
        await store.ensure_bucket()
        store._client.put_object(
            Bucket=settings.blob_bucket, Key=TENANT_BLOB_KEY, Body=tenant.encode()
        )

    asyncio.run(_go())


async def _redis_marker(settings: Settings) -> str | None:
    r = redis.asyncio.from_url(settings.redis_url.get_secret_value())  # type: ignore[no-untyped-call]
    try:
        raw = await r.get(TENANT_REDIS_KEY)
    finally:
        await r.aclose()
    return raw.decode() if raw is not None else None


def _startup(settings: Settings) -> None:
    with TestClient(create_app(settings)):
        pass


# -- the database ---------------------------------------------------------------------


@pytest.mark.req("FR-436")
def test_matching_markers_start_the_app(stores: Settings) -> None:
    """Positive control: the shared test database is migrated with the `local` tenant."""
    _startup(stores)


@pytest.mark.req("FR-436")
def test_a_database_marker_for_another_tenant_stops_startup(stores: Settings) -> None:
    other = stores.model_copy(update={"tenant_id": "another-insurer"})
    with pytest.raises(TenantMismatchError) as exc:
        _startup(other)
    message = str(exc.value)
    assert "database" in message
    assert "another-insurer" in message
    assert "'local'" in message


@pytest.mark.req("FR-436")
def test_the_database_is_checked_before_any_other_store_is_written(stores: Settings) -> None:
    """A configuration pointing at another tenant's database stops before it touches
    object storage or the broker."""
    other = stores.model_copy(update={"tenant_id": "another-insurer"})
    with pytest.raises(TenantMismatchError):
        _startup(other)
    assert _blob_marker(stores) is None  # the bucket was never even created
    assert asyncio.run(_redis_marker(stores)) is None


@pytest_asyncio.fixture
async def migrated_scratch(
    scratch_database: str,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> str:
    """A scratch database migrated to head, so it carries this revision's marker table."""
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    await _upgrade(_alembic_config(), "head")
    return scratch_database


def _scratch_settings(base: Settings, url: str) -> Settings:
    return base.model_copy(update={"database_url": SecretStr(url)})


@pytest.mark.req("FR-436")
async def test_an_empty_marker_table_stops_startup(
    stores: Settings, migrated_scratch: str
) -> None:
    engine = create_async_engine(migrated_scratch, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        await conn.execute(text("DELETE FROM tenant_marker"))
    await engine.dispose()

    with pytest.raises(TenantMismatchError) as exc:
        await asyncio.to_thread(_startup, _scratch_settings(stores, migrated_scratch))
    message = str(exc.value)
    assert "database" in message
    assert "missing" in message
    # The application never writes an absent database marker; only the migration does.
    engine = create_async_engine(migrated_scratch)
    async with engine.connect() as conn:
        count = (await conn.execute(text("SELECT count(*) FROM tenant_marker"))).scalar_one()
    await engine.dispose()
    assert count == 0


@pytest.mark.req("FR-436")
async def test_a_database_not_migrated_to_this_revision_stops_startup(
    stores: Settings,
    scratch_database: str,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    await _upgrade(_alembic_config(), _MARKER_MIGRATION_DOWN_REVISION)

    with pytest.raises(TenantMismatchError) as exc:
        await asyncio.to_thread(_startup, _scratch_settings(stores, scratch_database))
    message = str(exc.value)
    assert "database" in message
    assert "missing" in message
    assert "alembic upgrade head" in message


# -- the migration -----------------------------------------------------------------------


@pytest.mark.req("FR-436")
async def test_the_migration_writes_the_configured_tenant_and_refuses_a_second_row(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch  # noqa: F811
) -> None:
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    monkeypatch.setenv("GIP_TENANT_ID", "acme-motor")
    await _upgrade(_alembic_config(), "head")

    engine = create_async_engine(scratch_database, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        rows = (await conn.execute(text("SELECT id, tenant_id FROM tenant_marker"))).all()
        assert [tuple(r) for r in rows] == [(1, "acme-motor")]
        # Refused by the database, not by application code: a second id violates the
        # primary key, and any id other than 1 violates the CHECK.
        with pytest.raises(Exception, match="tenant_marker"):
            await conn.execute(text("INSERT INTO tenant_marker VALUES (1, 'x')"))
        with pytest.raises(Exception, match="tenant_marker"):
            await conn.execute(text("INSERT INTO tenant_marker VALUES (2, 'x')"))
    await engine.dispose()


# -- object storage and the broker ------------------------------------------------------


@pytest.mark.req("FR-436")
def test_a_blob_marker_for_another_tenant_stops_startup(stores: Settings) -> None:
    _plant_blob_marker(stores, "another-insurer")
    with pytest.raises(TenantMismatchError) as exc:
        _startup(stores)
    message = str(exc.value)
    assert "blob" in message
    assert "another-insurer" in message
    assert "'local'" in message


@pytest.mark.req("FR-436")
async def test_a_broker_marker_for_another_tenant_stops_startup(stores: Settings) -> None:
    r = redis.asyncio.from_url(stores.redis_url.get_secret_value())  # type: ignore[no-untyped-call]
    await r.set(TENANT_REDIS_KEY, "another-insurer")
    await r.aclose()
    with pytest.raises(TenantMismatchError) as exc:
        await asyncio.to_thread(_startup, stores)
    message = str(exc.value)
    assert "broker" in message
    assert "another-insurer" in message
    assert "'local'" in message


@pytest.mark.req("FR-436")
async def test_a_fresh_deployment_starts_and_arms_both_markers(stores: Settings) -> None:
    """No bucket, no blob marker, no broker marker, database migrated: it starts, creates
    the bucket, and writes both markers. The order is what makes this work: the bucket must
    exist before its marker can be written."""
    await asyncio.to_thread(_startup, stores)
    assert _blob_marker(stores) == "local"
    assert await _redis_marker(stores) == "local"

    # Restarting on the same stores starts too.
    await asyncio.to_thread(_startup, stores)

    # A different configured tenant on the same stores refuses, naming the database.
    other = stores.model_copy(update={"tenant_id": "another-insurer"})
    with pytest.raises(TenantMismatchError) as exc:
        await asyncio.to_thread(_startup, other)
    assert "database" in str(exc.value)


# -- the worker -------------------------------------------------------------------------


@pytest.mark.req("FR-436")
def test_a_celery_signal_handler_cannot_stop_a_worker() -> None:
    """Why the worker's check is not a signal handler. Celery's `Signal.send` catches
    what a receiver raises and returns it, so a handler that raised would log nothing and
    the worker would go on to consume. Proved here, not assumed (PL-1239 Task 4)."""
    from celery.signals import worker_init

    def _refuse(**_: object) -> None:
        raise TenantMismatchError("database", "a", "b")

    worker_init.connect(_refuse, weak=False)
    try:
        results = worker_init.send(sender=None)  # does not raise
    finally:
        worker_init.disconnect(_refuse)
    assert any(isinstance(err, TenantMismatchError) for _, err in results)


@pytest.mark.req("FR-436")
def test_the_worker_entrypoint_refuses_to_import_on_a_database_mismatch(
    stores: Settings,
) -> None:
    """`celery -A app.worker.entrypoint worker` imports this module before it consumes
    anything, so an exception at import is a worker that never starts."""
    env = {
        **os.environ,
        "GIP_DATABASE_URL": test_database_url(),
        "GIP_TENANT_ID": "another-insurer",
        "GIP_BLOB_BUCKET": stores.blob_bucket,
        "GIP_REDIS_URL": stores.redis_url.get_secret_value(),
        "PYTHONPATH": os.pathsep.join(
            [str(_REPO_ROOT / "backend" / "src"), os.environ.get("PYTHONPATH", "")]
        ),
    }
    done = subprocess.run(
        [sys.executable, "-c", "import app.worker.entrypoint"],
        cwd=_REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert done.returncode != 0
    assert "TenantMismatchError" in done.stderr
    assert "database" in done.stderr
    assert "another-insurer" in done.stderr


@pytest.mark.req("FR-436")
def test_the_worker_entrypoint_imports_when_the_markers_match(stores: Settings) -> None:
    env = {
        **os.environ,
        "GIP_DATABASE_URL": test_database_url(),
        "GIP_BLOB_BUCKET": test_blob_bucket(),
        "GIP_REDIS_URL": stores.redis_url.get_secret_value(),
        "PYTHONPATH": os.pathsep.join(
            [str(_REPO_ROOT / "backend" / "src"), os.environ.get("PYTHONPATH", "")]
        ),
    }
    done = subprocess.run(
        [sys.executable, "-c", "import app.worker.entrypoint"],
        cwd=_REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert done.returncode == 0, done.stderr
