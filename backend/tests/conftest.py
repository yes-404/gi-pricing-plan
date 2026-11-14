"""Shared fixtures for the backend suite.

Database fixtures live in `conftest_db.py` and are re-exported here so pytest collects
them for every test module without each one importing them.
"""

from __future__ import annotations

import gc
import os
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.health import clear_probes
from app.config import Environment, Settings
from app.main import create_app

_REDIS_URL_EXAMPLE = "export GIP_REDIS_URL=redis://localhost:6379/12"


def refuse_live_redis(url: str | None) -> str | None:
    """The refusal message for a test run whose Redis URL could reach database 0, else None.

    `Settings.redis_url` defaults to database 0, the live one on a shared box, and a test run
    once deleted a Celery list from it that way (#1806). So the run must NAME a scratch
    database (index 1 or higher) in `GIP_REDIS_URL`: an unset or empty value, an index of 0,
    and a URL with no index (redis-py reads that as 0) are all refused. An unreadable index is
    refused too, since it cannot be shown to be safe. The message never repeats the URL:
    it can carry a password.
    """
    if not url or not url.strip():
        return (
            "GIP_REDIS_URL is unset or empty, and the app's default is Redis database 0, the "
            f"live one. Name a scratch database (1 or higher) first, e.g. `{_REDIS_URL_EXAMPLE}`."
        )
    try:
        parts = urlsplit(url.strip())
        path = parts.path.strip("/")
        raw = path if path else (parse_qs(parts.query).get("db") or [""])[0]
        db = int(raw) if raw else 0
        where = f"host {parts.hostname or '?'!r}"
    except ValueError:
        return (
            "GIP_REDIS_URL does not name a readable database index, so it cannot be shown "
            "not to be database 0. Set it to a scratch database (1 or higher), "
            f"e.g. `{_REDIS_URL_EXAMPLE}`."
        )
    if db < 1:
        return (
            f"GIP_REDIS_URL names database {db} on {where}; database 0 is the live one. "
            f"Set a scratch database (1 or higher), e.g. `{_REDIS_URL_EXAMPLE}`."
        )
    return None


def pytest_configure(config: pytest.Config) -> None:
    """End the run, before any test or app starts, if its Redis URL could reach database 0."""
    message = refuse_live_redis(os.environ.get("GIP_REDIS_URL"))
    if message is not None:
        pytest.exit(message, returncode=4)


@pytest.fixture
def settings() -> Settings:
    """Settings for a local test run, built explicitly rather than read from the process."""
    return Settings(environment=Environment.LOCAL, version="test")


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings)


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    # raise_server_exceptions=False so the 500 handler is exercised rather than the
    # exception being re-raised into the test — otherwise the last-resort handler, which
    # exists precisely for the unexpected, is never covered.
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def api_settings() -> Settings:
    """Settings for a test that talks to the real database through the API.

    Distinct from `settings` above, which builds an app with no database at all — the
    health and error tests want that, and making every client DB-backed would make them
    slower for nothing.
    """
    from backend.tests.conftest_db import test_blob_bucket, test_database_url

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        # The same bucket every fixture store uses. Without this the app reads and writes
        # the default `gip-blobs` while the fixtures use the test bucket, so an object
        # written by a fixture is invisible to a route and vice versa — which is what
        # `POST /api/v1/score` hit as the first route to *read* a blob a fixture had
        # *written*. Everything before it stayed on one side of that boundary.
        blob_bucket=test_blob_bucket(),
    )


@pytest.fixture
def api_client(api_settings: Settings) -> TestClient:
    """A client over the full app, inside its lifespan so startup actually runs."""
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as client:
        yield client


@pytest.fixture(autouse=True)
def _isolate_probes():
    """Readiness probes are process-global; a leak between tests is a flaky suite.

    Cleared on the way out as well as the way in. Clearing only on entry is not enough:
    a test whose fixture starts an app (`with TestClient(...)`) registers probes during
    setup, and whether that happens before or after this fixture runs depends on fixture
    ordering pytest does not promise. Clearing both ends makes the outcome independent of
    that ordering.
    """
    clear_probes()
    yield
    clear_probes()


@pytest.fixture(autouse=True)
def _leave_no_frozen_objects():
    """An app lifespan calls `gc.freeze()` (PL-1454 DP-4); the permanent generation is
    process-wide, so hand it back as found after every test rather than let it leak."""
    yield
    gc.unfreeze()


# Re-exported so pytest registers them as fixtures for the whole package.
from backend.tests.conftest_db import (  # noqa: E402,F401
    _empty_the_database_after_the_session,
    _seed_through_the_owner_seam,
    blob_store,
    database,
    grant,
    membership,
    owner_database,
    principal,
    workspace_id,
)
