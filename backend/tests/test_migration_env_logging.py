"""Running alembic in-process must not silence the application's loggers.

`backend/migrations/env.py` applies `alembic.ini`'s logging config with `fileConfig`, whose
`disable_existing_loggers` argument defaults to true. In the CLI that is harmless: the process
does nothing else. In this test suite alembic runs in-process (`command.upgrade`), so every
logger that already exists, all the `app.*` ones included, is disabled for the rest of the
session, and a disabled logger drops its records before any handler sees them. Every later test
that asserts on log output, or on its absence, then passes vacuously; NFR-499's "quote inputs
are never logged in full" check is one of them.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from backend.tests.conftest_db import test_database_url

_REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def restore_logger_state() -> Iterator[None]:
    """Put every logger's `disabled` flag back, so a red run here cannot poison other tests."""
    before = {
        name: logger.disabled
        for name, logger in logging.root.manager.loggerDict.items()
        if isinstance(logger, logging.Logger)
    }
    yield
    for name, disabled in before.items():
        logging.getLogger(name).disabled = disabled


@pytest.mark.req("NFR-499")
async def test_an_in_process_migration_run_leaves_the_app_loggers_enabled(
    monkeypatch: pytest.MonkeyPatch, restore_logger_state: None
) -> None:
    """`alembic current` runs `env.py` end to end, so it is enough to reach `fileConfig`.

    The logger is created first, as it is in the suite: `fileConfig` only disables loggers
    that already exist.
    """
    probe = logging.getLogger("app.env_logging_probe")
    probe.disabled = False
    monkeypatch.setenv("GIP_DATABASE_URL", test_database_url())
    cfg = Config(str(_REPO_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_REPO_ROOT / "backend" / "migrations"))
    cfg.set_main_option("prepend_sys_path", str(_REPO_ROOT / "backend" / "src"))

    # `env.py` calls `asyncio.run(...)`, which raises from inside a running loop.
    await asyncio.to_thread(command.current, cfg)

    assert not probe.disabled, "the migration run disabled a pre-existing app logger"
    # And the whole class, not the one probe: no logger under `app` may have been disabled.
    disabled = sorted(
        name
        for name, logger in logging.root.manager.loggerDict.items()
        if isinstance(logger, logging.Logger) and name.startswith("app") and logger.disabled
    )
    assert not disabled, f"the migration run disabled app loggers: {disabled}"
