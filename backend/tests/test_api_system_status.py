"""`GET /api/v1/admin/status`, the System status route (`07` §4.6, §5.1; FR-443, FR-444).

The permission is `settings:read` (the maintainer's decision of 2026-11-21 on #1505,
answer 1): every built-in role may read it, so the refusal pinned here is a caller who
holds a membership and no role.
"""

from __future__ import annotations

import logging

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.api.health import register_probe
from app.config import Environment, Settings
from app.main import create_app
from model_schema import SystemStatus
from model_schema.system_status import BlobStoreUsage, ComponentHealth, ComponentStatus

STATUS = "/api/v1/admin/status"


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_blob_bucket, test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        blob_bucket=test_blob_bucket(),
    )


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest_asyncio.fixture
async def headers(workspace_id, principal, grant) -> dict[str, str]:
    await grant("admin")
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


@pytest_asyncio.fixture
async def unprivileged_headers(workspace_id, principal, membership) -> dict[str, str]:
    """Authenticated, a member, and holding no role: the refusal must come from the role
    check, not from the membership check."""
    await membership()
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


@pytest.mark.req("FR-443", "FR-444")
def test_a_caller_with_no_role_is_refused(client: TestClient, unprivileged_headers) -> None:
    """**Negative.** Answer 1: the route is behind `settings:read`, and a caller holding no
    role does not hold it."""
    response = client.get(STATUS, headers=unprivileged_headers)
    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


#: The one literal: the field names `07` §4.6 states. It pins the spec against the model; the
#: other assertions read the models' `model_fields`, so no field name is written a second time
#: (CLAUDE.md §4).
_SPEC_STATUS_FIELDS = {"status", "components", "schema_version", "queues", "blob_store", "caches"}


@pytest.mark.req("FR-443", "FR-444")
def test_the_model_declares_the_fields_the_spec_names() -> None:
    assert set(SystemStatus.model_fields) == _SPEC_STATUS_FIELDS


@pytest.mark.req("FR-443", "FR-444")
def test_the_keys_are_those_of_the_shape(client: TestClient, headers) -> None:
    """`07` §4.6: the response carries the fields of `SystemStatus` and of the shapes inside
    it, read from the models rather than listed again here."""
    response = client.get(STATUS, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == set(SystemStatus.model_fields)
    assert set(body["blob_store"]) == set(BlobStoreUsage.model_fields)
    assert all(set(c) <= set(ComponentHealth.model_fields) for c in body["components"])
    assert body["status"] == ComponentStatus.UP
    assert [c["name"] for c in body["components"]] == ["blobs", "database", "redis"]
    assert all(c["status"] in set(ComponentStatus) for c in body["components"])
    assert isinstance(body["queues"], list)
    assert isinstance(body["blob_store"]["objects"], int)
    assert isinstance(body["blob_store"]["bytes"], int)


@pytest.mark.req("FR-443", "FR-444")
def test_a_failing_probe_is_a_down_component(client: TestClient, headers) -> None:
    async def down() -> str:
        return "unreachable: ConnectionError"

    register_probe("blobs", down)
    body = client.get(STATUS, headers=headers).json()
    components = {c["name"]: c for c in body["components"]}
    assert components["blobs"] == {
        "name": "blobs",
        "status": "down",
        "detail": "unreachable: ConnectionError",
    }
    assert components["database"]["status"] == "up"
    # `blobs` gates readiness, so the whole is down, as `/readyz` says (`07` §4.6).
    assert body["status"] == "down"


@pytest.mark.req("FR-443", "FR-444")
def test_a_redis_outage_is_down_beside_an_up_whole(client: TestClient, headers) -> None:
    """Answer 4 (i): Redis is reported, and does not decide the verdict. The same function
    decides it for `/readyz` and for this route."""

    async def down() -> str:
        return "unreachable: ConnectionError"

    register_probe("redis", down)
    body = client.get(STATUS, headers=headers).json()
    assert {c["name"]: c["status"] for c in body["components"]}["redis"] == "down"
    assert body["status"] == "up"
    assert client.get("/readyz").status_code == 200


@pytest.mark.req("FR-443", "FR-444")
async def test_the_schema_version_is_the_migration_revision(
    client: TestClient, headers, api_settings: Settings
) -> None:
    """Answer 4 (ii), option b: read from the database's `alembic_version` table, not from
    a constant that could drift from it."""
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(api_settings.database_url.get_secret_value())
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT version_num FROM alembic_version"))
            revision = result.scalar_one()
    finally:
        await engine.dispose()
    assert client.get(STATUS, headers=headers).json()["schema_version"] == revision


@pytest.mark.req("FR-443", "FR-444")
def test_caches_report_the_bundle_slot_and_not_the_diff_cache(client: TestClient, headers) -> None:
    """`07` §4.6: a slot with no reads shows 0/0; `diff_cache` reports nothing until a
    caller is given one, so it has no entry."""
    slot = client.app.state.bundle_slot
    assert slot.get("a" * 64) is None
    assert slot.get("b" * 64) is None
    caches = client.get(STATUS, headers=headers).json()["caches"]
    assert caches == [{"name": "bundle_slot", "hits": 0, "misses": 2}]


# --- the database cannot be read (decision of 2026-11-21 on #1505, comment 7070124577) ------
#
# Authentication succeeds first (the caller's role is read from the database by
# `resolve_caller`, `app/api/deps.py`), then the status queries fail. A database that is down
# for the whole request fails at authentication, before this route, and is not this case:
# the cases here are a database that answered for the caller and then failed the status reads.
#
# SystemStatus has six fields. Their sources, and the rule "`null` only when its own source
# cannot be read", applied per field (`07` §4.6, decision #1505 comment 7070124577):
#   status, components : the readiness probes (`/readyz`'s functions); never null. A failed
#                        read of the database makes the `database` component `down`, and so
#                        `status` `down`.
#   schema_version     : the `alembic_version` query -> null when that query fails.
#   queues, blob_store : the platform-figures read (`jobs`, `blobs`) -> null when it fails.
#   caches             : this process's memory (BundleSlot counters); cannot fail, so never null.
# A field whose own read succeeded keeps its value, whatever the other read did.

_DATABASE_FIELDS = ("schema_version", "queues", "blob_store")
_FIGURES_FIELDS = ("queues", "blob_store")
_ALEMBIC_FIELDS = ("schema_version",)


async def _boom_sqlalchemy(*_args: object, **_kwargs: object) -> None:
    raise SQLAlchemyError("the figures could not be read")


async def _boom_os(*_args: object, **_kwargs: object) -> None:
    raise OSError("the connection was reset")


#: Each way a status read can fail after authentication: the failing reads, and the fields
#: that read alone supplies (those are the ones that must be `null`).
_FAILURES = {
    "figures-sqlalchemy": (("read_platform_figures",), _boom_sqlalchemy, _FIGURES_FIELDS),
    "figures-oserror": (("read_platform_figures",), _boom_os, _FIGURES_FIELDS),
    "alembic-sqlalchemy": (("_schema_version",), _boom_sqlalchemy, _ALEMBIC_FIELDS),
    "alembic-oserror": (("_schema_version",), _boom_os, _ALEMBIC_FIELDS),
    "both-sqlalchemy": (
        ("read_platform_figures", "_schema_version"),
        _boom_sqlalchemy,
        _DATABASE_FIELDS,
    ),
    "both-oserror": (("read_platform_figures", "_schema_version"), _boom_os, _DATABASE_FIELDS),
}


@pytest.fixture(params=sorted(_FAILURES))
def unreadable(request, client: TestClient, headers, monkeypatch: pytest.MonkeyPatch):
    """The response, and the fields that must be `null` under this failure."""
    from app.api import system_status

    targets, boom, nulled = _FAILURES[request.param]
    for target in targets:
        monkeypatch.setattr(system_status, target, boom)
    return client.get(STATUS, headers=headers), nulled


@pytest.mark.req("FR-443", "FR-444")
def test_unreadable_database_still_answers_200(unreadable) -> None:
    response, _ = unreadable
    assert response.status_code == 200


@pytest.mark.req("FR-443", "FR-444")
@pytest.mark.parametrize("field", _DATABASE_FIELDS)
def test_a_failed_read_nulls_its_own_fields_and_only_those(unreadable, field: str) -> None:
    """`null`, in the body: not omitted, not an empty list, not zeros. A field whose own read
    succeeded keeps its value: it is filled, not null (a partial failure, `07` §4.6)."""
    response, nulled = unreadable
    body = response.json()
    assert field in body
    if field in nulled:
        assert body[field] is None
    else:
        assert body[field] is not None


@pytest.mark.req("FR-443", "FR-444")
def test_a_partial_failure_leaves_the_other_read_filled(unreadable) -> None:
    """The reverse cases, by value: figures failing leaves the revision; the revision failing
    leaves the queues list and the blob usage object."""
    response, nulled = unreadable
    body = response.json()
    if "schema_version" not in nulled:
        assert isinstance(body["schema_version"], str)
        assert body["schema_version"]
    if "queues" not in nulled:
        assert isinstance(body["queues"], list)
    if "blob_store" not in nulled:
        assert set(body["blob_store"]) == set(BlobStoreUsage.model_fields)


@pytest.mark.req("FR-443", "FR-444")
def test_unreadable_database_is_a_down_database_component(unreadable) -> None:
    """Either read failing marks the component `down`: the decision's "with the database read
    failing, the field is `null` and the component is `down`"."""
    response, _ = unreadable
    components = {c["name"]: c for c in response.json()["components"]}
    assert components["database"]["status"] == "down"
    assert components["database"]["detail"]
    # The other components are untouched: each is `null` or `down` only for its own source.
    assert components["blobs"]["status"] == "up"
    assert [c["name"] for c in response.json()["components"]] == ["blobs", "database", "redis"]


@pytest.mark.req("FR-443", "FR-444")
def test_unreadable_database_makes_the_whole_down(unreadable) -> None:
    """`status` follows the readiness verdict over the components as this route reports them,
    and the database gates readiness."""
    response, _ = unreadable
    assert response.json()["status"] == "down"


@pytest.mark.req("FR-443", "FR-444")
def test_unreadable_database_does_not_null_the_process_fields(unreadable) -> None:
    """`caches` is read from this process, not the database: its own source is readable."""
    response, _ = unreadable
    assert response.json()["caches"] == [{"name": "bundle_slot", "hits": 0, "misses": 0}]


@pytest.mark.req("FR-443", "FR-444")
def test_a_failed_read_detail_names_the_type_and_does_not_say_unreachable(
    client: TestClient, headers, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The database may have answered, so the detail must not say it was unreachable, and it
    carries the exception's type only, never its message (`00` R3, NFR-499)."""
    from app.api import system_status

    monkeypatch.setattr(system_status, "_schema_version", _boom_sqlalchemy)
    detail = {c["name"]: c for c in client.get(STATUS, headers=headers).json()["components"]}[
        "database"
    ]["detail"]
    assert detail == "could not be read: SQLAlchemyError"
    assert "unreachable" not in detail
    assert "the figures" not in detail  # the message text is never carried


@pytest.mark.req("FR-443", "FR-444")
def test_an_empty_alembic_table_is_a_failed_read_not_an_unreachable_database(
    client: TestClient, headers, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A real `NoResultFound` (the table answers with no row), not a raised stand-in: the
    database answered, so the detail says the revision could not be read, not that the
    database was unreachable. `queues` and `blob_store` keep their values."""
    from app.api import system_status

    real_text = system_status.text
    monkeypatch.setattr(
        system_status,
        "text",
        lambda _sql: real_text("SELECT version_num FROM alembic_version WHERE false"),
    )
    body = client.get(STATUS, headers=headers).json()
    database = {c["name"]: c for c in body["components"]}["database"]
    assert database["status"] == "down"
    assert database["detail"] == "could not be read: NoResultFound"
    assert body["schema_version"] is None
    assert isinstance(body["queues"], list)
    assert body["blob_store"] is not None
    assert body["status"] == "down"


@pytest.mark.req("FR-443", "FR-444")
@pytest.mark.parametrize("case", sorted(_FAILURES))
def test_a_failed_read_is_logged_once_with_the_error_type_only(
    case: str,
    client: TestClient,
    headers,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Each failed read leaves one WARNING with `error_type` and nothing of the exception's
    message or traceback: the message can carry a DSN and so a password (`00` R3, NFR-499),
    as the Redis probe's log line does. The app is built by the `client` fixture, before
    `caplog` attaches (#1894)."""
    from app.api import system_status

    targets, boom, _ = _FAILURES[case]
    for target in targets:
        monkeypatch.setattr(system_status, target, boom)
    expected_type = "SQLAlchemyError" if boom is _boom_sqlalchemy else "OSError"
    secret = "the figures could not be read" if boom is _boom_sqlalchemy else "the connection"
    with caplog.at_level(logging.DEBUG, logger="app.system_status"):
        assert client.get(STATUS, headers=headers).status_code == 200
    records = [r for r in caplog.records if r.name == "app.system_status"]
    assert len(records) == len(targets)
    for record in records:
        assert record.levelno == logging.WARNING
        assert record.__dict__["error_type"] == expected_type
        assert record.exc_info is None
        assert secret not in record.getMessage() + str(record.__dict__)


@pytest.mark.req("FR-443", "FR-444")
def test_a_down_database_probe_with_both_reads_succeeding(client: TestClient, headers) -> None:
    """The probe says `database` is `down` but the route's own reads both succeed: the fields
    are filled, the component is `down` (from the probe), and `status` is `down`, because it
    is the verdict over the components as this route reports them (`07` §4.6)."""

    async def down() -> str:
        return "unreachable: TimeoutError"

    register_probe("database", down)
    body = client.get(STATUS, headers=headers).json()
    components = {c["name"]: c for c in body["components"]}
    assert components["database"] == {
        "name": "database",
        "status": "down",
        "detail": "unreachable: TimeoutError",
    }
    assert isinstance(body["schema_version"], str)
    assert body["schema_version"]
    assert isinstance(body["queues"], list)
    assert set(body["blob_store"]) == set(BlobStoreUsage.model_fields)
    assert body["status"] == "down"


@pytest.mark.req("FR-443", "FR-444")
def test_the_model_makes_the_three_fields_nullable() -> None:
    """The published contract says so, and a null is a valid body (not a 500)."""
    status = SystemStatus(
        status=ComponentStatus.DOWN,
        components=(),
        schema_version=None,
        queues=None,
        blob_store=None,
        caches=(),
    )
    assert (status.schema_version, status.queues, status.blob_store) == (None, None, None)
    # An empty list and zeros are different, valid answers: the read succeeded.
    readable = status.model_copy(
        update={"queues": (), "blob_store": BlobStoreUsage(objects=0, bytes=0)}
    )
    assert readable.queues == ()
    assert readable.blob_store == BlobStoreUsage(objects=0, bytes=0)
