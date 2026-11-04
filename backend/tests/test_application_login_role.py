"""S1a (FD-1729, PL 8227 S1a; PL-1769 Task 3 outcome and Task 5, Steps 5.1/5.3): the
application connection IS the login role, and the one grants migration is shaped as planned.

(`test_application_role.py` is S1b's file: the startup refusal and the exact grant map.
Nothing here is S1b's.)

DB-backed tests use the `database` fixture, which skips when PostgreSQL is unreachable and
needs the login role provisioned (Step 1.3): they are RED at `origin/main` (3cd5fcf7) by
ASSERTION, because the fixture connects as the owner there. The migration-file tests are
DB-free and RED because no `*_application_role_grants.py` exists.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from sqlalchemy import text

_VERSIONS = Path(__file__).resolve().parents[1] / "migrations" / "versions"


def _grants_migration() -> Path:
    found = sorted(_VERSIONS.glob("*_application_role_grants.py"))
    assert len(found) == 1, f"expected exactly one grants migration, found {found}"
    return found[0]


@pytest.mark.req("FR-44")
async def test_the_application_connection_is_the_login_role(database) -> None:  # type: ignore[no-untyped-def]
    """Task 3 outcome. Red at main: `current_user` is `gipricing`, the owner."""
    async with database.session() as session:
        who = (await session.execute(text("SELECT current_user"))).scalar_one()
    assert who == "gip_app_login"


@pytest.mark.req("FR-44")
async def test_the_login_role_owns_nothing_and_holds_no_direct_table_privilege(database) -> None:  # type: ignore[no-untyped-def]
    """Step 1.4 premise ("every table grant goes to `gip_app`, so the login role owns nothing
    and holds no direct privilege"). Red at main: the connection is the owner, which owns
    every table.
    """
    async with database.session() as session:
        owned = (
            await session.execute(
                text(
                    "SELECT count(*) FROM pg_tables "
                    "WHERE schemaname='public' AND tableowner=current_user"
                )
            )
        ).scalar_one()
        direct = (
            await session.execute(
                text(
                    "SELECT count(*) FROM information_schema.role_table_grants "
                    "WHERE grantee = 'gip_app_login'"
                )
            )
        ).scalar_one()
    assert (owned, direct) == (0, 0)


@pytest.mark.req("FR-44")
async def test_the_application_can_read_the_tenant_marker_but_not_write_it(database) -> None:  # type: ignore[no-untyped-def]
    """Step 3.2 / 5.1: `tenant_marker` is the first refused path (the lifespan's
    `require_tenant_binding`), granted `SELECT` only. Red at main: the owner can also write.
    """
    async with database.session() as session:
        await session.execute(text("SELECT 1 FROM tenant_marker LIMIT 1"))
    async with database.session() as session:
        with pytest.raises(Exception, match="permission denied"):
            await session.execute(text("DELETE FROM tenant_marker"))


@pytest.mark.req("FR-44")
async def test_the_excess_delete_on_jobs_and_outbox_is_revoked(database) -> None:  # type: ignore[no-untyped-def]
    """Step 5.1 "Revoke the excess" (R9): `jobs` and `outbox` hold `DELETE` at the base
    unless the census diff records a caller (then this test moves with the `LG-`). Red at
    main: `gip_app` still has it.
    """
    async with database.session() as session:
        rows = (
            await session.execute(
                text(
                    "SELECT table_name FROM information_schema.role_table_grants "
                    "WHERE grantee='gip_app' AND privilege_type='DELETE' "
                    "AND table_name IN ('jobs','outbox')"
                )
            )
        ).all()
    assert rows == []


@pytest.mark.req("FR-44")
def test_exactly_one_grants_migration_and_every_grant_line_is_commented() -> None:
    """Acceptance 5 / Step 5.1. Red at main: no `*_application_role_grants.py`."""
    lines = _grants_migration().read_text(encoding="utf-8").splitlines()
    grant_idx = [
        i for i, ln in enumerate(lines) if re.search(r"\bGRANT\b", ln) and "REVOKE" not in ln
    ]
    assert grant_idx, "the migration grants nothing"
    for i in grant_idx:
        around = lines[i] + (lines[i - 1] if i else "")
        assert "#" in around or "--" in around, f"uncommented GRANT at line {i + 1}"


@pytest.mark.req("FR-44")
def test_the_grants_migration_grants_only_to_gip_app_and_downgrades() -> None:
    """Step 1.4 / DP-17 (all grants to `gip_app`, none to the login role), Step 5.1
    (downgrade revokes exactly what it granted). Red at main: file absent.
    """
    src = _grants_migration().read_text(encoding="utf-8")
    assert "gip_app_login" not in src
    assert "def downgrade(" in src
    assert "REVOKE" in src.split("def downgrade(", 1)[1]
    assert not re.search(r"GRANT[^\n]*\bDELETE\b[^\n]*\b(jobs|outbox)\b", src)
