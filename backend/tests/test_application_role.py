"""S1b (FD-1729 part 2, PL 8227 row 4, LG-1947): the start-up refusal, the trigger-tamper proof
and the exact grant map. Requirement: `01` FR-44.

**DB-backed, in a throwaway Postgres only** (never the shared cluster, never `gipricing`), except
the two DB-free structural tests. **DRAFT: written DB-free on S1a's seam head; no test here has
been run.** The reds are measured at S1b's base after S1a's squash (LG-1947, O4).

**The three cause-reds (R-b1 = T6, R-b5 = T4, R-b6 = T5) and O1 (a).** After S1a's flip the
`database` fixture connects as the login role, so the cause these tests were written against
("the application connects as the owner") is gone. Their *red* form is the same test run with
`GIP_TEST_APP_DATABASE_URL` set to the **owner's DSN** (S1a's own override,
`conftest_db.test_database_url`); their *green* form is the default (the login role):

    GIP_TEST_APP_DATABASE_URL=<owner DSN> pytest backend/tests/test_application_role.py \\
        -k "r_b1 or r_b5 or r_b6"          # RED: the connection is the owner
    pytest backend/tests/test_application_role.py -k "r_b1 or r_b5 or r_b6"      # GREEN

**O2 (c), T7.** Red at `down_revision` `9b3e7c15d4a2` (`alembic downgrade -1` on the throwaway,
then the test), green at head; plus the planted-drift tests, which prove both directions of the
comparison inside a rolled-back transaction.

**O5, T1.** The refusal comes BEFORE `require_tenant_binding` (`backend/src/app/main.py`). The
test makes the order observable: the blob and Redis endpoints are unreachable, so a lifespan that
reached `require_tenant_binding` first would fail with a connection error, not with
`LeastPrivilegeError`. T1 therefore needs no MinIO.

Every test taking `owner_database` is listed in `conftest_db.OWNER_FIXTURE_USERS`
(`owner-subject`). The grant map in T7 is written here, never imported from the migration's
`_TARGET`: a map read from the migration would be the source checking itself.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from backend.tests.conftest_db import owner_subject_settings
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection

from app.config import Settings
from app.db.immutability import (
    P_OWN,
    PINNED_GUARD_FUNCTION_MD5,
    LeastPrivilegeError,
    _declared,
    assert_least_privilege,
)
from app.db.session import Database
from app.main import create_app

_REPO_ROOT = Path(__file__).resolve().parents[2]
_APP_ROLE = "gip_app"
_LOGIN_ROLE = "gip_app_login"
_UNREACHABLE = "http://127.0.0.1:1"
_DEFINITION = "def " + "_declared("  # not a literal: this file would otherwise match itself


def _owner_settings() -> Settings:
    """Settings whose database is the OWNER's and whose other stores are unreachable."""
    return owner_subject_settings(
        version="test",
        dev_auth_enabled=True,
        blob_endpoint_url=_UNREACHABLE,
        redis_url=SecretStr("redis://127.0.0.1:1/0"),
    )


# --------------------------------------------------------------------------- T1 (R-b2)


@pytest.mark.req("FR-44")
def test_the_api_refuses_to_start_as_the_owner() -> None:
    """T1 / R-b2, API. The lifespan raises `LeastPrivilegeError` naming the provisioning script.

    Ordering invariant under test (O5): the refusal precedes `require_tenant_binding`; the blob
    and Redis endpoints are unreachable, so reaching the tenant binding first would raise a
    connection error instead.
    """
    with (
        pytest.raises(LeastPrivilegeError, match=r"provision-app-role\.py"),
        TestClient(create_app(_owner_settings())),
    ):
        pass


@pytest.mark.req("FR-44")
def test_the_worker_refuses_to_start_as_the_owner() -> None:
    """T1 / R-b2, worker. Importing the entrypoint with the owner DSN fails (a subprocess: the
    module runs `load_settings()` and `asyncio.run(...)` at import). Same ordering invariant."""
    env = {
        **os.environ,
        "GIP_DATABASE_URL": _owner_settings().database_url.get_secret_value(),
        "GIP_BLOB_ENDPOINT_URL": _UNREACHABLE,
        "GIP_REDIS_URL": "redis://127.0.0.1:1/0",
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
    assert "LeastPrivilegeError" in done.stderr
    assert "provision-app-role.py" in done.stderr


# --------------------------------------------------------------------------- T2 (R-b1b)


async def _become(connection: AsyncConnection, statements: list[str], role: str) -> None:
    for statement in statements:
        await connection.execute(text(statement))
    await connection.execute(text(f"SET LOCAL ROLE {role}"))


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("case", ["inherit_false_member_of_the_owner", "bypassrls_role"])
async def test_an_inherit_false_membership_of_the_owner_is_refused(
    owner_database: Database, case: str
) -> None:
    """T2 / R-b1b. In a rolled-back transaction a scratch role is made a member of the owner with
    `INHERIT FALSE` (case 1) or given `BYPASSRLS` (case 2); acting as it, P-own returns a row and
    `assert_least_privilege` raises. Case 1 is the by-cause red of a `'USAGE'` predicate."""
    async with owner_database.engine.connect() as connection:
        transaction = await connection.begin()
        try:
            owner = (await connection.execute(text("SELECT current_user"))).scalar_one()
            if case == "inherit_false_member_of_the_owner":
                setup = [
                    "CREATE ROLE gip_scratch_r4 NOLOGIN",
                    f'GRANT "{owner}" TO gip_scratch_r4 WITH INHERIT FALSE',
                ]
            else:
                setup = ["CREATE ROLE gip_scratch_r4 NOLOGIN BYPASSRLS"]
            await _become(connection, setup, "gip_scratch_r4")
            rows = (await connection.execute(P_OWN)).all()
            assert rows, "P-own must flag the scratch role"
            with pytest.raises(LeastPrivilegeError):
                await assert_least_privilege(connection)
        finally:
            await transaction.rollback()


# --------------------------------------------------------------------------- S1c (FD-1951)
# Every route to the owner is refused at startup. Each case plants ONE route as the owner, in a
# rolled-back transaction, and acts as the login role: `assert_least_privilege` must raise,
# naming the route. A control before the plant proves the same call passes on the provisioned
# state, so the raise is the plant's (SL 8266).

_PREDEFINED_ROLES = (
    "pg_write_all_data",
    "pg_execute_server_program",
    "pg_write_server_files",
    "pg_read_server_files",
)

#: `{case id: ([statements the owner plants], the route the refusal names)}`.
_ROUTES: dict[str, tuple[list[str], str]] = {
    "a1_gip_app_createrole": (["ALTER ROLE gip_app CREATEROLE"], r"gip_app \(createrole\)"),
    "a2_login_createrole": (
        ["ALTER ROLE gip_app_login CREATEROLE"],
        r"gip_app_login \(createrole\)",
    ),
    **{
        f"m1_{role}": ([f"GRANT {role} TO gip_app_login"], rf"{role} \(predefined role\)")
        for role in _PREDEFINED_ROLES
    },
    "m2_session_replication_role": (
        ["GRANT SET ON PARAMETER session_replication_role TO gip_app_login"],
        "session_replication_role",
    ),
    "m3a_guard_function_owner": (
        ["ALTER FUNCTION artifact_append_only() OWNER TO gip_app"],
        r"owns artifact_append_only\(\)",
    ),
    "m3b_schema_owner": (["ALTER SCHEMA public OWNER TO gip_app"], r"owns schema public"),
}


async def _as_login_role(connection: AsyncConnection) -> None:
    await connection.execute(text(f"SET LOCAL ROLE {_LOGIN_ROLE}"))


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("case", list(_ROUTES))
async def test_a_route_to_the_owner_is_refused_at_startup(
    owner_database: Database, case: str
) -> None:
    """S1c (FD-1951): CREATEROLE on a reachable role, a predefined role, the SET privilege on
    `session_replication_role`, ownership of a pinned guard function or of schema `public`."""
    statements, route = _ROUTES[case]
    async with owner_database.engine.connect() as connection:
        transaction = await connection.begin()
        try:
            await _as_login_role(connection)
            await assert_least_privilege(connection)  # control: the provisioned state passes
            await connection.execute(text("RESET ROLE"))
            for statement in statements:
                await connection.execute(text(statement))
            await _as_login_role(connection)
            with pytest.raises(LeastPrivilegeError, match=route) as refused:
                await assert_least_privilege(connection)
            assert "provision-app-role.py" in str(refused.value)
        finally:
            await transaction.rollback()


@pytest.mark.req("FR-44")
@pytest.mark.parametrize(
    "grant",
    [
        'GRANT "{owner}" TO gip_app_login WITH ADMIN OPTION',
        'GRANT "{owner}" TO gip_app_login WITH ADMIN TRUE, INHERIT FALSE, SET FALSE',
    ],
    ids=["plain_admin_option", "admin_only"],
)
async def test_an_admin_option_on_the_owner_is_refused(
    owner_database: Database, grant: str
) -> None:
    """S1c control (acceptance 21, not a red): on PostgreSQL 16 any `pg_auth_members` row counts
    as `'MEMBER'`, the admin-only form included, so `P_OWN` refuses both at the base and at the
    head. Present so that a change to `P_OWN` cannot lose it unseen."""
    async with owner_database.engine.connect() as connection:
        transaction = await connection.begin()
        try:
            owner = (await connection.execute(text("SELECT current_user"))).scalar_one()
            await connection.execute(text(grant.format(owner=owner)))
            await _as_login_role(connection)
            with pytest.raises(LeastPrivilegeError, match=r"provision-app-role\.py"):
                await assert_least_privilege(connection)
        finally:
            await transaction.rollback()


# --------------------------------------------------------------------------- T3 (DP-14 (b))

_TAMPER = {
    "disable": (
        "ALTER TABLE factors DISABLE TRIGGER factors_no_modify",
        "factors_no_modify on factors",
    ),
    "replica": (
        "ALTER TABLE factors ENABLE REPLICA TRIGGER factors_no_modify",
        "factors_no_modify on factors",
    ),
    "drop": ("DROP TRIGGER factors_no_modify ON factors", "factors_no_modify on factors"),
    "replace_body": (
        "CREATE OR REPLACE FUNCTION artifact_append_only() RETURNS trigger "
        "LANGUAGE plpgsql AS $$ BEGIN RETURN NEW; END $$",
        "artifact_append_only",
    ),
}


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("route", list(_TAMPER))
async def test_a_tampered_artifact_trigger_refuses_startup(
    owner_database: Database, route: str
) -> None:
    """T3 / DP-14 (b). The owner tampers with one declared table's trigger in a rolled-back
    transaction; acting as the application role afterwards, `assert_least_privilege` raises and
    names the table and trigger (or, for the body, the function). A control before the tamper
    proves the same call passes on the untouched head, so the raise is the tamper's."""
    statement, expected = _TAMPER[route]
    async with owner_database.engine.connect() as connection:
        transaction = await connection.begin()
        try:
            await connection.execute(text(f"SET LOCAL ROLE {_APP_ROLE}"))
            await assert_least_privilege(connection)  # control: untouched head passes
            await connection.execute(text("RESET ROLE"))
            await connection.execute(text(statement))
            await connection.execute(text(f"SET LOCAL ROLE {_APP_ROLE}"))
            with pytest.raises(LeastPrivilegeError, match=expected):
                await assert_least_privilege(connection)
        finally:
            await transaction.rollback()


@pytest.mark.req("FR-44")
async def test_an_enable_always_trigger_is_accepted(owner_database: Database) -> None:
    """T3 / PL-1769 Step 4.2: the trigger check accepts `tgenabled IN ('O','A')`. `ENABLE ALWAYS`
    (`'A'`) fires under `session_replication_role = replica` too, so it is no weaker than `'O'`;
    the `'D'` and `'R'` routes above stay refused."""
    async with owner_database.engine.connect() as connection:
        transaction = await connection.begin()
        try:
            await connection.execute(
                text("ALTER TABLE factors ENABLE ALWAYS TRIGGER factors_no_modify")
            )
            await connection.execute(text(f"SET LOCAL ROLE {_APP_ROLE}"))
            await assert_least_privilege(connection)
        finally:
            await transaction.rollback()


# --- T4-T6 (R-b5, R-b6, R-b1) ---


@pytest.mark.req("FR-44")
async def test_r_b5_the_application_role_cannot_disable_a_trigger(database: Database) -> None:
    """T4 / R-b5. As the application connection, `DISABLE TRIGGER` and `SET
    session_replication_role` are refused. RED with `GIP_TEST_APP_DATABASE_URL` = the owner DSN
    (O1 (a)); GREEN on the default login role."""
    async with database.session() as session:
        with pytest.raises(DBAPIError) as disable:
            await session.execute(text("ALTER TABLE factors DISABLE TRIGGER factors_no_modify"))
        assert "must be owner of table factors" in str(disable.value)
        await session.rollback()
        with pytest.raises(DBAPIError) as replica:
            await session.execute(text("SET session_replication_role = replica"))
        assert "permission denied" in str(replica.value)


@pytest.mark.req("FR-44")
async def test_r_b6_the_application_role_is_not_superuser_not_owner_and_cannot_bypass(
    database: Database,
) -> None:
    """T5 / R-b6. Neither superuser nor bypassing, owns nothing (P-own empty), and cannot set
    `session_replication_role`. RED with the owner DSN override (O1 (a)); GREEN by default."""
    async with database.session() as session:
        flags = (
            await session.execute(
                text("SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user")
            )
        ).one()
        assert tuple(flags) == (False, False)
        assert (await session.execute(P_OWN)).all() == []
        with pytest.raises(DBAPIError) as refused:
            await session.execute(text("SET session_replication_role = replica"))
        assert "permission denied to set parameter" in str(refused.value)


@pytest.mark.req("FR-44")
async def test_r_b1_the_application_does_not_connect_as_an_owner_or_a_superuser(
    database: Database,
) -> None:
    """T6 / R-b1. P-own returns no row for the application connection. RED with the owner DSN
    override (O1 (a)); GREEN by default."""
    async with database.session() as session:
        assert (await session.execute(P_OWN)).all() == []
        await database.assert_least_privilege()  # the whole start-up check, as the app role


# --------------------------------------------------------------------------- T7 (Step 5.2)

#: `{table: (table-level privileges, {column: column-level privileges beyond those})}` for
#: `gip_app`, over EVERY public table. Written here from the census, not read from the migration.
_R = ({"SELECT"}, {})
_A = ({"SELECT", "INSERT"}, {})
_L = ({"SELECT", "INSERT", "UPDATE"}, {})


def _c(*columns: str) -> tuple[set[str], dict[str, set[str]]]:
    return ({"SELECT", "INSERT"}, {column: {"UPDATE"} for column in columns})


EXPECTED_GRANTS: dict[str, tuple[set[str], dict[str, set[str]]]] = {
    "alembic_version": _R,
    "api_keys": _c("expires_at", "revoked_at", "last_used_at"),
    "approval_decisions": _A,
    "approval_policies": _c("policy", "updated_at"),
    "approval_requests": _c("status", "decided_at", "withdrawn_reason"),
    "audit_events": _A,
    "backtests": _A,
    "bandings": _A,
    "blob_uploads": _c("job_id", "sha256"),
    "blobs": _c("ref_count"),
    "custom_metrics": _L,
    "custom_objectives": _L,
    "dataset_splits": _A,
    "dataset_versions": _L,
    "datasets": _c("data_dictionary", "owner_id", "validation_rule_set_id"),
    "deployment_requests": _c("approval_request_id", "status"),
    "deployments": _A,
    "diagnostics": _A,
    "dislocation_runs": _A,
    "environment_settings": _c("value", "updated_by", "updated_at"),
    "environments": _c("name", "description", "retired_at"),
    "factors": _A,
    "groupings": _A,
    "ingestion_runs": _A,
    "job_logs": _A,
    "jobs": _L,
    "metric_certificates": _A,
    "model_comparisons": _A,
    "models": _L,
    "objective_certificates": _A,
    "outbox": _c("attempts", "last_error", "status", "published_at"),
    "peril_structures": _L,
    "profiles": _A,
    "rate_table_cells": _A,
    "rate_table_versions": _A,
    "rate_tables": _c("current_version", "updated_at"),
    "rating_algorithms": _A,
    "rating_versions": _L,
    "reference_rows": _A,
    "reference_table_versions": _c("status"),
    "reference_tables": _A,
    "regression_runs": _A,
    "regression_suite_versions": _A,
    "regression_suites": _A,
    "role_assignments": _R,
    "roles": _R,
    "routing_rules": _A,
    "scoring_traces": ({"SELECT", "INSERT", "DELETE"}, {}),
    "service_accounts": _A,
    "shadow_configs": _A,
    "shadow_results": _A,
    "sources": _A,
    "sub_graph_versions": _A,
    "subject_purges": _R,
    "tenant_marker": _R,
    "transparency_artifacts": _A,
    "users": _c("email", "display_name", "last_login_at"),
    "validation_acknowledgements": _A,
    "validation_reports": _A,
    "validation_rule_sets": _A,
    "validation_rules": _c("dry_run_report_id", "status", "approved_by"),
    "workspace_members": _R,
    "workspace_settings": _c("value"),
    "workspaces": _R,
}


async def _grant_differences(connection: AsyncConnection) -> list[str]:
    """Every difference, both ways, between `EXPECTED_GRANTS` and what `gip_app` holds."""
    tables = {
        row[0]
        for row in await connection.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        )
    }
    table_level: dict[str, set[str]] = {t: set() for t in tables}
    for table, privilege in await connection.execute(
        text(
            "SELECT table_name, privilege_type FROM information_schema.role_table_grants "
            "WHERE grantee = :role AND table_schema = 'public'"
        ),
        {"role": _APP_ROLE},
    ):
        table_level[table].add(privilege)
    column_level: dict[str, dict[str, set[str]]] = {t: {} for t in tables}
    for table, column, privilege in await connection.execute(
        text(
            "SELECT table_name, column_name, privilege_type "
            "FROM information_schema.column_privileges "
            "WHERE grantee = :role AND table_schema = 'public'"
        ),
        {"role": _APP_ROLE},
    ):
        if privilege not in table_level[table]:  # a table-level grant is expanded to its columns
            column_level[table].setdefault(column, set()).add(privilege)

    differences = [f"{t}: no expected row" for t in sorted(tables - EXPECTED_GRANTS.keys())]
    differences += [f"{t}: expected table absent" for t in sorted(EXPECTED_GRANTS.keys() - tables)]
    for table in sorted(tables & EXPECTED_GRANTS.keys()):
        want_table, want_columns = EXPECTED_GRANTS[table]
        if table_level[table] != want_table:
            got = sorted(table_level[table])
            differences.append(f"{table}: table privileges {got} != {sorted(want_table)}")
        if column_level[table] != want_columns:
            got_columns = column_level[table]
            differences.append(f"{table}: column privileges {got_columns} != {want_columns}")
    return differences


@pytest.mark.req("FR-44")
async def test_every_table_grants_the_application_exactly_its_declared_privileges(
    owner_database: Database,
) -> None:
    """T7 / Step 5.2. The written map equals what `gip_app` holds on every public table, both
    ways; and no `DELETE` on `jobs` or `outbox`. RED (O2 (c)) at `down_revision`
    `9b3e7c15d4a2`: `alembic downgrade -1` on the throwaway, then this test, expecting a
    difference on every table the grants revision changed, `jobs` and `outbox` included."""
    async with owner_database.engine.connect() as connection:
        assert await _grant_differences(connection) == []
    assert "DELETE" not in EXPECTED_GRANTS["jobs"][0] | EXPECTED_GRANTS["outbox"][0]


@pytest.mark.req("FR-44")
@pytest.mark.parametrize(
    ("drift", "table"),
    [
        (f"GRANT DELETE ON jobs TO {_APP_ROLE}", "jobs"),
        (f"REVOKE UPDATE (status) ON outbox FROM {_APP_ROLE}", "outbox"),
        (f"GRANT UPDATE (kind) ON sources TO {_APP_ROLE}", "sources"),
        ("GRANT UPDATE ON jobs TO PUBLIC", "jobs"),
    ],
    ids=["extra_table_grant", "missing_column_grant", "extra_column_grant", "public_table_grant"],
)
async def test_the_grant_comparison_sees_a_drift_in_both_directions(
    owner_database: Database, drift: str, table: str
) -> None:
    """O2 (c): a grant planted (or removed) inside a rolled-back transaction is reported, so the
    comparison is shown to fail in both directions rather than assumed to."""
    async with owner_database.engine.connect() as connection:
        transaction = await connection.begin()
        try:
            await connection.execute(text(drift))
            differences = await _grant_differences(connection)
            assert any(d.startswith(f"{table}:") for d in differences), differences
        finally:
            await transaction.rollback()


# --------------------------------------------------------------------------- T8 (Step 4.2)


@pytest.mark.req("FR-44")
async def test_the_pinned_guard_function_hashes_match_the_head(database: Database) -> None:
    """T8 / DP-14 (b). For every trigger on an append-only or guarded table, `md5(prosrc)` of its
    function equals the pin. The pins are measured from the migrated head, never typed. Its
    broken-input proof (owed, LG-1947): one pin altered in a scratch edit, red."""
    tables = list(_declared("append_only") + _declared("guarded"))
    assert len(tables) >= 35, tables  # the derivation going quiet would pass vacuously
    async with database.session() as session:
        rows = (
            await session.execute(
                text(
                    "SELECT DISTINCT p.proname, md5(p.prosrc) FROM pg_trigger t "
                    "JOIN pg_class c ON c.oid = t.tgrelid JOIN pg_proc p ON p.oid = t.tgfoid "
                    "WHERE NOT t.tgisinternal AND c.relname = ANY(:tables)"
                ),
                {"tables": tables},
            )
        ).all()
    assert rows
    mismatched = [name for name, digest in rows if PINNED_GUARD_FUNCTION_MD5.get(name) != digest]
    assert mismatched == []


# --------------------------------------------------------------------------- S1, S2 (DB-free)


@pytest.mark.req("FR-44")
def test_p_own_is_defined_once() -> None:
    """S1. `pg_has_role` appears once in `backend/src`, in `app/db/immutability.py`, with
    `'MEMBER'`."""
    hits = [
        (path, line)
        for path in (_REPO_ROOT / "backend" / "src").rglob("*.py")
        for line in path.read_text().splitlines()
        if "pg_has_role" in line
    ]
    assert len(hits) == 1, hits
    path, line = hits[0]
    assert path.name == "immutability.py"
    assert "'MEMBER'" in line


@pytest.mark.req("FR-44")
def test_declared_lives_in_the_application() -> None:
    """S2. the `_declared` function is defined only in `app/db/immutability.py` under `backend/`."""
    defining = [
        path.relative_to(_REPO_ROOT).as_posix()
        for path in (_REPO_ROOT / "backend").rglob("*.py")
        if _DEFINITION in path.read_text()
    ]
    assert defining == ["backend/src/app/db/immutability.py"]
