"""FD-8256: the `database` and `blob_store` fixtures must not skip when the service they
are configured for is unreachable.

A skip on connect failure lets a gate read green with every DB test skipped when the
configured DSN is unreachable or mis-provisioned. The rule under test: when
`GIP_TEST_DATABASE_URL` or `GIP_TEST_APP_DATABASE_URL` is set, a connect failure FAILS the
test naming host, port, user and database -- never the password; only when nothing is
configured does the fixture skip.

The REAL `database` fixture is driven in a child pytest run on a one-test module, against
port 1 on loopback (nothing listens there), so no database is needed. The third case of the
rule -- configured and reachable but no migrations applied -- needs a live database and is
left to the gate. `blob_store` follows the same rule: `GIP_TEST_BUCKET` or
`GIP_BLOB_ENDPOINT_URL` set and unreachable fails naming endpoint and bucket, never a key.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SECRET = "s3cr3t-pw-do-not-print"
_DSN = f"postgresql+asyncpg://fd8256user:{_SECRET}@127.0.0.1:1/fd8256db"

_MODULE = """
from backend.tests import conftest_db
from backend.tests.conftest_db import blob_store, database  # noqa: F401

{patch}

async def test_uses_the_database(database):
    raise AssertionError("the fixture yielded")

async def test_uses_the_blob_store(blob_store):
    raise AssertionError("the fixture yielded")
"""
_BLOB_SECRET = "blob-secret-do-not-print"
_ENDPOINT = "http://127.0.0.1:1"
_BUCKET = "fd8256bucket"

# Nothing configured: pin the fallbacks to something unreachable so the child run stays
# database-free (the per-worktree lookup would otherwise try the shared cluster, and the
# default MinIO endpoint may be up).
_UNCONFIGURED_PATCH = f"""
conftest_db._per_worktree_test_database_url = lambda: {_DSN!r}

class _Down:
    def __init__(self, *a, **k): pass
    async def ensure_bucket(self): raise ConnectionError("down")

conftest_db.BlobStore = _Down
"""

_CONFIGURED = {
    "GIP_TEST_DATABASE_URL": {"GIP_TEST_DATABASE_URL": _DSN},
    "GIP_TEST_APP_DATABASE_URL": {"GIP_TEST_APP_DATABASE_URL": _DSN},
    "GIP_BLOB_ENDPOINT_URL": {
        "GIP_BLOB_ENDPOINT_URL": _ENDPOINT,
        "GIP_BLOB_SECRET_KEY": _BLOB_SECRET,
        "GIP_TEST_DATABASE_URL": _DSN,
    },
    "GIP_TEST_BUCKET": {
        "GIP_TEST_BUCKET": _BUCKET,
        "GIP_BLOB_ENDPOINT_URL": _ENDPOINT,
        "GIP_BLOB_SECRET_KEY": _BLOB_SECRET,
        "GIP_TEST_DATABASE_URL": _DSN,
    },
}
_SCRUBBED = (
    "GIP_TEST_DATABASE_URL",
    "GIP_TEST_APP_DATABASE_URL",
    "GIP_TEST_BUCKET",
    "GIP_BLOB_ENDPOINT_URL",
    "GIP_BLOB_SECRET_KEY",
    "GIP_BLOB_ACCESS_KEY",
)


def _run(tmp_path: Path, test: str, env_extra: dict[str, str], patch: str = "") -> tuple[int, str]:
    (tmp_path / "test_child.py").write_text(_MODULE.format(patch=patch))
    env = {k: v for k, v in os.environ.items() if k not in _SCRUBBED}
    env.update(env_extra)
    env["PYTHONPATH"] = str(_ROOT)
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            "-o",
            "asyncio_mode=auto",
            "--rootdir",
            str(tmp_path),
            "-rA",
            "-k",
            test,
            "test_child.py",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


def _summary(out: str) -> str:
    return out.strip().splitlines()[-1]


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("env_name", ["GIP_TEST_DATABASE_URL", "GIP_TEST_APP_DATABASE_URL"])
def test_configured_but_unreachable_database_fails_naming_the_target(
    tmp_path: Path, env_name: str
) -> None:
    rc, out = _run(tmp_path, "uses_the_database", _CONFIGURED[env_name])
    assert "skipped" not in _summary(out), _summary(out)
    assert rc != 0, _summary(out)
    for part in ("127.0.0.1", "fd8256user", "fd8256db", ":1"):
        assert part in out, part
    assert _SECRET not in out


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("env_name", ["GIP_BLOB_ENDPOINT_URL", "GIP_TEST_BUCKET"])
def test_configured_but_unreachable_blob_store_fails_naming_endpoint_and_bucket(
    tmp_path: Path, env_name: str
) -> None:
    rc, out = _run(tmp_path, "uses_the_blob_store", _CONFIGURED[env_name])
    assert "skipped" not in _summary(out), _summary(out)
    assert rc != 0, _summary(out)
    assert _ENDPOINT in out
    assert (_BUCKET if env_name == "GIP_TEST_BUCKET" else "gip-test-blobs") in out
    assert _BLOB_SECRET not in out


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("test", ["uses_the_database", "uses_the_blob_store"])
def test_nothing_configured_still_skips_without_a_password(tmp_path: Path, test: str) -> None:
    rc, out = _run(tmp_path, test, {}, _UNCONFIGURED_PATCH)
    assert rc == 0, _summary(out)
    assert "1 skipped" in _summary(out), _summary(out)
    assert _SECRET not in out
    assert "gip_app_login" not in out
