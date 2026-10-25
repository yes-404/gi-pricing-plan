#!/usr/bin/env python3
"""Provision the application's login role and set its password (FD-1729, PL-1769 Task 1).

Connects as the owner (`GIP_MIGRATION_DATABASE_URL`), applies
`deploy/postgres/app-login-role.sql`, then sets `gip_app_login`'s password from
`GIP_APP_DB_PASSWORD` as a **pre-hashed SCRAM-SHA-256 verifier** (RFC 5802 / RFC 7677):
PostgreSQL stores a verifier as given, so the plain password never reaches the server, its
log under `log_statement`, or an error message. The script never prints the password or the
verifier.

The default password (`gip_app_login`) is for a fresh local volume only; the script refuses
it unless `--allow-default-password` is passed.

Run: `GIP_MIGRATION_DATABASE_URL=… GIP_APP_DB_PASSWORD=… uv run python scripts/provision-app-role.py`
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import hmac
import os
import pathlib
import secrets
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SQL_FILE = ROOT / "deploy" / "postgres" / "app-login-role.sql"
DEFAULT_PASSWORD = "gip_app_login"
ITERATIONS = 4096


def scram_sha256_verifier(
    password: str, *, salt: bytes | None = None, iterations: int = ITERATIONS
) -> str:
    """`SCRAM-SHA-256$<iterations>:<salt>$<StoredKey>:<ServerKey>` as PostgreSQL stores it."""
    salt = secrets.token_bytes(16) if salt is None else salt
    salted = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    client_key = hmac.new(salted, b"Client Key", hashlib.sha256).digest()
    stored_key = hashlib.sha256(client_key).digest()
    server_key = hmac.new(salted, b"Server Key", hashlib.sha256).digest()
    salt_b64, stored_b64, server_b64 = (
        base64.b64encode(raw).decode() for raw in (salt, stored_key, server_key)
    )
    return f"SCRAM-SHA-256${iterations}:{salt_b64}${stored_b64}:{server_b64}"


async def provision(owner_dsn: str, password: str) -> None:
    import asyncpg

    verifier = scram_sha256_verifier(password)
    # base64, digits, `$`, `:` and `=` only: nothing to quote or escape in the literal.
    assert "'" not in verifier
    conn = await asyncpg.connect(owner_dsn.replace("postgresql+asyncpg://", "postgresql://", 1))
    try:
        async with conn.transaction():
            await conn.execute(SQL_FILE.read_text(encoding="utf-8"))
            await conn.execute(f"ALTER ROLE gip_app_login PASSWORD '{verifier}'")
    finally:
        await conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--allow-default-password",
        action="store_true",
        help="permit the default password (fresh local volumes and CI only)",
    )
    args = parser.parse_args(argv)

    password = os.environ.get("GIP_APP_DB_PASSWORD", DEFAULT_PASSWORD)
    if password == DEFAULT_PASSWORD and not args.allow_default_password:
        print(
            "refusing the default application password: set a non-default "
            "GIP_APP_DB_PASSWORD, or pass --allow-default-password on a fresh local volume",
            file=sys.stderr,
        )
        return 2
    owner_dsn = os.environ.get("GIP_MIGRATION_DATABASE_URL")
    if not owner_dsn:
        print(
            "GIP_MIGRATION_DATABASE_URL is not set: provisioning connects as the owner and "
            "never falls back to the application DSN",
            file=sys.stderr,
        )
        return 2
    asyncio.run(provision(owner_dsn, password))
    print("gip_app_login provisioned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
