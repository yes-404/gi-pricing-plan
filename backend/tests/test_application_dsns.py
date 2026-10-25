"""S1a (FD-1729, PL 8227 S1a; PL-1769 Task 2, Steps 2.1 and 2.2): two DSNs.

`GIP_DATABASE_URL` is the application's (the login role); `GIP_MIGRATION_DATABASE_URL` is
the owner's and only migrations use it. DB-free: settings objects, a subprocess alembic run in
offline (`--sql`) mode, and source text.

Every test is RED at `origin/main` (3cd5fcf7) for the cause named in its docstring.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.config import Settings

_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.req("FR-44")
def test_the_application_dsn_defaults_to_the_login_role() -> None:
    """Step 2.1. Red at main: `config.py`'s default DSN is `gip:gip@…/gip`, not the login role."""
    url = Settings().database_url.get_secret_value()
    assert url.startswith("postgresql+asyncpg://gip_app_login:")
    assert "@localhost:5432/" in url


@pytest.mark.req("FR-44")
def test_the_migration_dsn_is_a_separate_optional_secret() -> None:
    """Step 2.1. Red at main: `Settings` has no `migration_database_url`, and `extra="forbid"`
    makes the keyword a ValidationError.
    """
    assert Settings().migration_database_url is None
    owner = "postgresql+asyncpg://owner:pw@localhost:5432/gipricing"
    settings = Settings(migration_database_url=owner)
    assert settings.migration_database_url is not None
    assert settings.migration_database_url.get_secret_value() == owner
    assert "pw" not in repr(settings)


@pytest.mark.req("FR-44")
def test_the_migration_dsn_gets_the_same_scheme_validator() -> None:
    """Step 2.1 ("the same scheme validator"). Red at main: the field is absent, so the
    ValidationError raised is for the unknown keyword, not the scheme; the match on the
    scheme message fails.
    """
    with pytest.raises(ValidationError, match="postgresql\\+asyncpg"):
        Settings(migration_database_url="postgresql://owner:pw@localhost/gipricing")


@pytest.mark.req("FR-44")
def test_alembic_refuses_without_the_migration_dsn_and_never_falls_back() -> None:
    """Step 2.1 (`migrations/env.py` "raises a RuntimeError naming GIP_MIGRATION_DATABASE_URL …
    never falls back to the application DSN"). Red at main: env.py reads `database_url`, so the
    offline run does not refuse for the missing migration DSN — it proceeds off the application
    DSN and exits non-zero for another reason (observed at d1d96465: rc != 0, stderr ending
    "...No literal value renderer is available..."), so the assert on a `RuntimeError` naming
    `GIP_MIGRATION_DATABASE_URL` fails.
    """
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIP_")}
    env["GIP_DATABASE_URL"] = "postgresql+asyncpg://gip_app_login:x@localhost:5432/none"
    done = subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            str(_ROOT / "alembic.ini"),
            "upgrade",
            "head",
            "--sql",
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=_ROOT,
        timeout=120,
        check=False,
    )
    assert done.returncode != 0
    assert "RuntimeError" in done.stderr
    assert "GIP_MIGRATION_DATABASE_URL" in done.stderr


@pytest.mark.req("FR-44")
def test_no_backend_source_names_the_owner_credentials() -> None:
    """PL-1769 Acceptance 10: `git grep -nE "gipricing:gipricing" -- backend/src` prints
    nothing. A control, green at main as well (the default DSN names no owner credential);
    it guards S1a against reintroducing one.
    """
    hits = [
        str(p.relative_to(_ROOT))
        for p in (_ROOT / "backend" / "src").rglob("*.py")
        if "gipricing:gipricing" in p.read_text(encoding="utf-8")
    ]
    assert hits == []


@pytest.mark.req("FR-44")
def test_migrations_env_reads_the_migration_dsn() -> None:
    """PL-1769 Acceptance 10: `git grep -n "migration_database_url" -- backend/migrations/env.py`
    prints a hit. Red at main: env.py has no such text.
    """
    text = (_ROOT / "backend" / "migrations" / "env.py").read_text(encoding="utf-8")
    assert "migration_database_url" in text
    assert re.search(r"database_url\.get_secret_value\(\)", text) is None


@pytest.mark.req("FR-44")
def test_ci_migrates_as_the_owner_and_runs_the_suite_as_the_login_role() -> None:
    """Step 2.2 (`python.yml` `:296`, `:304-305`). Red at main: the Migrate step sets
    `GIP_DATABASE_URL` to the owner, and no step provisions the role.
    """
    text = (_ROOT / ".github" / "workflows" / "python.yml").read_text(encoding="utf-8")
    assert "GIP_MIGRATION_DATABASE_URL: postgresql+asyncpg://gipricing:gipricing@" in text
    assert "scripts/provision-app-role.py" in text
    assert "--allow-default-password" in text
