"""S1a (FD-1729, PL 8227 S1a; PL-1769 Task 1, Steps 1.1 and 1.2): the application's login
role is provisioned by `deploy/postgres/app-login-role.sql` and `scripts/provision-app-role.py`.

DB-free by design: the SQL file is read as text, the verifier is checked against the
RFC 7677 vector, and the script's refusals fire before it connects. The convergence proof
(applied twice, attributes reset) is a DB-window act in S1a's `LG-`, not a test here.
*(Amended 2026-10-26, SL-1962, FD-1951: the module is DB-backed from S1c, for the last test
only, which plants a state as the owner in a rolled-back transaction and applies the SQL file
over it.)*

**Interface drafted here, to be ratified at the GO** (the plan fixes behaviour, not names):
`scripts/provision-app-role.py` exposes `scram_sha256_verifier(password, *, salt,
iterations=4096) -> str`; its CLI reads `GIP_MIGRATION_DATABASE_URL` and
`GIP_APP_DB_PASSWORD` and takes `--allow-default-password`.

Every test is RED at `origin/main` (3cd5fcf7): neither the script nor the SQL file exists.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
from sqlalchemy import text

from app.db.session import Database

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "scripts" / "provision-app-role.py"
_SQL = _ROOT / "deploy" / "postgres" / "app-login-role.sql"

# RFC 7677 §3 example exchange (user "user", password "pencil").
_SALT = base64.b64decode("W22ZaJ0SNY7soEsUEjb6gQ==")
_AUTH_MESSAGE = (
    b"n=user,r=rOprNGfwEbeRWgbNEkqO,"
    b"r=rOprNGfwEbeRWgbNEkqO%hvYDpWUa2RaTCAfuxFIlj)hNlF$k0,s=W22ZaJ0SNY7soEsUEjb6gQ==,i=4096,"
    b"c=biws,r=rOprNGfwEbeRWgbNEkqO%hvYDpWUa2RaTCAfuxFIlj)hNlF$k0"
)
_SERVER_SIGNATURE = "6rriTRBi23WpRR/wtup+mMhUZUn/dB5nLTJRsjl95G4="


def _load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("_provision_app_role", _SCRIPT)
    assert _SCRIPT.is_file(), f"{_SCRIPT} does not exist"
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_script(*args: str, **env: str) -> subprocess.CompletedProcess[str]:
    base = {k: v for k, v in os.environ.items() if not k.startswith("GIP_")}
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *args],
        capture_output=True,
        text=True,
        env={**base, **env},
        timeout=60,
        check=False,
    )


@pytest.mark.req("FR-44")
def test_the_scram_verifier_matches_the_rfc_7677_vector() -> None:
    """Plan step 1.2 (R8). Red at main: `scripts/provision-app-role.py` is absent, so the
    load fails. Proves the verifier's keys: its ServerKey must reproduce the RFC's
    ServerSignature, and its StoredKey must be the SHA-256 of a ClientKey derived the same way.
    """
    verifier = _load_script().scram_sha256_verifier("pencil", salt=_SALT, iterations=4096)
    head, keys = verifier.split("$", 2)[0], verifier.split("$", 2)[2]
    iterations_salt = verifier.split("$", 2)[1]
    assert head == "SCRAM-SHA-256"
    assert iterations_salt == f"4096:{base64.b64encode(_SALT).decode()}"
    stored_b64, server_b64 = keys.split(":")
    signature = hmac.new(base64.b64decode(server_b64), _AUTH_MESSAGE, hashlib.sha256).digest()
    assert base64.b64encode(signature).decode() == _SERVER_SIGNATURE
    salted = hashlib.pbkdf2_hmac("sha256", b"pencil", _SALT, 4096)
    client_key = hmac.new(salted, b"Client Key", hashlib.sha256).digest()
    assert base64.b64decode(stored_b64) == hashlib.sha256(client_key).digest()


@pytest.mark.req("FR-44")
def test_the_verifier_salt_is_random_per_call() -> None:
    """Plan step 1.2 ("a random 16-byte salt"). Red at main: script absent."""
    script = _load_script()
    first = script.scram_sha256_verifier("pencil")
    second = script.scram_sha256_verifier("pencil")
    assert first != second
    assert len(base64.b64decode(first.split("$")[1].split(":")[1])) == 16


@pytest.mark.req("FR-44")
def test_the_script_refuses_the_default_password_without_the_flag() -> None:
    """Plan step 1.2 (R8: "refuses the default unless --allow-default-password").
    Red at main: script absent, so the interpreter exits 2 with "can't open file" and the
    asserted refusal message is not on stderr. The refusal must fire before any connection
    (the DSN here points at a closed port), and name the flag.
    """
    done = _run_script(
        GIP_MIGRATION_DATABASE_URL="postgresql+asyncpg://owner:owner@127.0.0.1:1/none",
        GIP_APP_DB_PASSWORD="gip_app_login",
    )
    assert done.returncode != 0
    assert "--allow-default-password" in done.stderr
    assert "gip_app_login" not in done.stdout.replace("--allow-default-password", "")


@pytest.mark.req("FR-44")
def test_the_script_refuses_when_the_migration_dsn_is_unset_and_leaks_no_secret() -> None:
    """Plan step 1.2 and Task 2 (the owner DSN is the only one it connects with, and the
    password never appears in output). Red at main: script absent.
    """
    secret = "s3cret-not-a-default-9f2c"
    done = _run_script("--allow-default-password", GIP_APP_DB_PASSWORD=secret)
    assert done.returncode != 0
    assert "GIP_MIGRATION_DATABASE_URL" in done.stderr
    assert secret not in done.stdout + done.stderr


@pytest.mark.req("FR-44")
def test_the_login_role_sql_converges_and_carries_no_password() -> None:
    """Plan step 1.1 (R7: "Converge, not only create"). Red at main: the file is absent."""
    sql = _SQL.read_text(encoding="utf-8")
    flat = " ".join(sql.split()).upper()
    assert "CREATE ROLE GIP_APP NOLOGIN" in flat
    assert "CREATE ROLE GIP_APP_LOGIN LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE" in flat
    assert (
        "ALTER ROLE GIP_APP_LOGIN LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION"
        " NOBYPASSRLS INHERIT" in flat
    )
    assert "GRANT GIP_APP TO GIP_APP_LOGIN" in flat
    assert "PASSWORD" not in flat
    assert "SUPERUSER;" not in flat.replace("NOSUPERUSER", "")


@pytest.mark.req("FR-44")
def test_compose_mounts_the_login_role_sql_for_fresh_volumes() -> None:
    """Plan step 1.2 (initdb mount). Red at main: `docker-compose.yml` has no such mount."""
    compose = (_ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8")
    assert (
        "./postgres/app-login-role.sql:/docker-entrypoint-initdb.d/10-app-login-role.sql:ro"
        in compose
    )


#: `{case id: (state the owner plants, a probe over the state after the SQL file, the value the
#: probe must return)}`. The SQL file is applied over the planted state, in one rolled-back
#: transaction, exactly as `provision-app-role.py` applies it.
_CONVERGENCE: dict[str, tuple[str, str, object]] = {
    "b1_gip_app_attributes": (
        "ALTER ROLE gip_app CREATEROLE CREATEDB REPLICATION",
        "SELECT rolcreaterole OR rolcreatedb OR rolreplication FROM pg_roles "
        "WHERE rolname = 'gip_app'",
        False,
    ),
    "b2_membership_options": (
        "REVOKE gip_app FROM gip_app_login; "
        "GRANT gip_app TO gip_app_login WITH INHERIT FALSE, SET TRUE",
        "SELECT inherit_option AND NOT set_option AND NOT admin_option FROM pg_auth_members "
        "WHERE roleid = 'gip_app'::regrole AND member = 'gip_app_login'::regrole",
        True,
    ),
    "m4_role_settings": (
        "ALTER ROLE gip_app_login SET search_path = shadow, public",
        "SELECT count(*) FROM pg_db_role_setting s JOIN pg_roles r ON r.oid = s.setrole "
        "WHERE r.rolname IN ('gip_app', 'gip_app_login') AND s.setdatabase = 0",
        0,
    ),
    "m4b_database_role_settings": (
        "DO $p$ BEGIN EXECUTE format("
        "'ALTER ROLE gip_app_login IN DATABASE %I SET search_path = shadow, public', "
        "current_database()); END $p$",
        "SELECT count(*) FROM pg_db_role_setting s JOIN pg_roles r ON r.oid = s.setrole "
        "WHERE r.rolname IN ('gip_app', 'gip_app_login') AND s.setdatabase <> 0",
        0,
    ),
}


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("case", list(_CONVERGENCE))
async def test_the_login_role_sql_converges_a_planted_state(
    owner_database: Database, case: str
) -> None:
    """S1c (FD-1951): a pre-existing `gip_app` with CREATEROLE, CREATEDB or REPLICATION, a
    membership with other options, and role settings (role-wide or per-database) are all
    reset by the SQL file. The file is applied with the raw driver connection's `execute()`
    (simple protocol, as `provision-app-role.py` does): a `text()` cannot carry a `DO` block
    and several statements."""
    plant, probe, expected = _CONVERGENCE[case]
    async with owner_database.engine.connect() as connection:
        transaction = await connection.begin()
        try:
            await connection.execute(text("SELECT 1"))  # opens the transaction on the driver
            raw = await connection.get_raw_connection()
            driver = raw.driver_connection
            assert driver is not None
            await driver.execute(plant)
            await driver.execute(_SQL.read_text(encoding="utf-8"))
            assert (await connection.execute(text(probe))).scalar_one() == expected
        finally:
            await transaction.rollback()
