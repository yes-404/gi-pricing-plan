"""Shared fixtures for the backend suite.

Database fixtures live in `conftest_db.py` and are re-exported here so pytest collects
them for every test module without each one importing them.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.health import clear_probes
from app.config import Environment, Settings
from app.main import create_app


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


@pytest.fixture(autouse=True)
def _isolate_probes() -> None:
    """Readiness probes are process-global; a leak between tests is a flaky suite."""
    clear_probes()


# Re-exported so pytest registers them as fixtures for the whole package.
from backend.tests.conftest_db import (  # noqa: E402,F401
    blob_store,
    database,
    principal,
    workspace_id,
)
