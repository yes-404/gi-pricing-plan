"""S1a (FD-1729, PL 8227 S1a; PL-1769 Task 3, Step 3.1): the fixtures' default flips.

`conftest_db.test_database_url()` returns the application (login-role) DSN;
`test_owner_database_url()` returns the owner's and is called only inside `conftest_db.py`;
`OWNER_FIXTURE_USERS` is a closed, labelled tuple. No `req` marker rule exception: these are
S1a evidence for FR-44, so each carries it.

NOTE for the GO: `test_conftest_db.py` (existing) asserts `test_database_url()` returns the
`GIP_TEST_DATABASE_URL` override and derives the owner URL. After the flip those cases
describe `test_owner_database_url()`; renaming their target is part of S1a-3 and is a lead
disposition (never a silent weakening). They are not edited here.

Every test is RED at `origin/main` (3cd5fcf7): `conftest_db` has no
`test_owner_database_url`, `OWNER_FIXTURE_USERS` or `owner_database`.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from backend.tests import conftest_db

_ROOT = Path(__file__).resolve().parents[2]
_LABELS = {"migration", "provisioning", "DP-22", "owner-subject", "bootstrap"}


@pytest.fixture(autouse=True)
def _clean_slate(monkeypatch: pytest.MonkeyPatch) -> None:
    conftest_db._per_worktree_test_database_url.cache_clear()
    for name in ("GIP_TEST_DATABASE_URL", "GIP_TEST_APP_DATABASE_URL", "GIP_APP_DB_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    yield
    conftest_db._per_worktree_test_database_url.cache_clear()


@pytest.mark.req("FR-44")
def test_database_url_is_the_login_role_on_the_owner_databases_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Step 3.1 bullet 1: the same database, the login role's credentials, password from
    `GIP_APP_DB_PASSWORD` (default `gip_app_login`). Red at main: it returns the owner DSN.
    """
    monkeypatch.setenv(
        "GIP_TEST_DATABASE_URL", "postgresql+asyncpg://gipricing:gipricing@h:5432/wt_db"
    )
    assert (
        conftest_db.test_database_url()
        == "postgresql+asyncpg://gip_app_login:gip_app_login@h:5432/wt_db"
    )
    monkeypatch.setenv("GIP_APP_DB_PASSWORD", "non-default-pw")
    assert (
        conftest_db.test_database_url()
        == "postgresql+asyncpg://gip_app_login:non-default-pw@h:5432/wt_db"
    )


@pytest.mark.req("FR-44")
def test_app_database_url_override_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 3.1 ("`GIP_TEST_APP_DATABASE_URL` overrides it"). Red at main: the variable is
    not read.
    """
    monkeypatch.setenv(
        "GIP_TEST_DATABASE_URL", "postgresql+asyncpg://gipricing:gipricing@h:5432/wt_db"
    )
    monkeypatch.setenv("GIP_TEST_APP_DATABASE_URL", "postgresql+asyncpg://x:y@z/explicit")
    assert conftest_db.test_database_url() == "postgresql+asyncpg://x:y@z/explicit"


@pytest.mark.req("FR-44")
def test_owner_database_url_keeps_the_meaning_of_gip_test_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Step 3.1 bullet 2 (CI sets the owner there, unchanged). Red at main: the function
    does not exist (AttributeError).
    """
    monkeypatch.setenv(
        "GIP_TEST_DATABASE_URL", "postgresql+asyncpg://gipricing:gipricing@h:5432/wt_db"
    )
    assert (
        conftest_db.test_owner_database_url()
        == "postgresql+asyncpg://gipricing:gipricing@h:5432/wt_db"
    )


@pytest.mark.req("FR-44")
def test_owner_database_url_is_called_only_inside_conftest_db() -> None:
    """Step 3.1 ("a test asserts that `git grep -n 'test_owner_database_url(' -- backend/tests`
    hits only that file"). Red at main: zero hits, so the set of hit files is not exactly
    {conftest_db.py}.
    """
    out = subprocess.run(
        ["git", "-C", str(_ROOT), "grep", "-l", "test_owner_database_url(", "--", "backend/tests"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.split()
    own = {"backend/tests/conftest_db.py", "backend/tests/test_conftest_db_login_role.py"}
    assert set(out) - own == set()
    assert "backend/tests/conftest_db.py" in out


@pytest.mark.req("FR-44")
def test_owner_fixture_users_is_a_closed_labelled_tuple() -> None:
    """Step 3.1 (`OWNER_FIXTURE_USERS`, a closed tuple of `(node id, label, reason)`; labels
    `migration`, `provisioning`, `DP-22`, `owner-subject`, `bootstrap`; `api_settings` not
    among them). Red at main: the name is absent.
    """
    users = conftest_db.OWNER_FIXTURE_USERS
    assert isinstance(users, tuple)
    assert users
    for entry in users:
        node_id, label, reason = entry
        assert label in _LABELS, entry
        assert reason.strip(), entry
        assert (_ROOT / node_id.split("::", 1)[0]).is_file(), node_id
        assert "api_settings" not in node_id
        assert "api_client" not in node_id
    assert len({u[0] for u in users}) == len(users)


@pytest.mark.req("FR-44")
def test_the_owner_database_fixture_exists() -> None:
    """Step 3.1 ("a new `owner_database` fixture uses the owner's"). Red at main: absent."""
    assert hasattr(conftest_db, "owner_database")


def _src_files_naming(root: Path, *names: str) -> list[str]:
    """Every `.py` under `root` whose text contains any of `names`."""
    return sorted(
        str(p.relative_to(root))
        for p in root.rglob("*.py")
        if any(n in p.read_text(encoding="utf-8") for n in names)
    )


_SEAM_NAMES = ("conftest_db", "seed_as_owner")


@pytest.mark.req("FR-44")
def test_the_owner_seam_exists_and_is_not_named_anywhere_in_backend_src() -> None:
    """Condition (i) of the S1a seeding-seam ruling (to-lead 2026-10-25 22:24:25 GMT): the
    owner-engine seam `conftest_db.seed_as_owner` is test-only -- nothing under
    `backend/src` names it or its module. Import-linter cannot say this: `backend` is a
    namespace package, not one of the contract's root packages.

    RED means the seam is absent (`seed_as_owner` missing from `conftest_db`); the zero-hit
    half is green by construction until a source file names the seam, which the negative
    case below proves it would notice.
    """
    assert callable(getattr(conftest_db, "seed_as_owner", None))
    assert _src_files_naming(_ROOT / "backend" / "src", *_SEAM_NAMES) == []


@pytest.mark.req("FR-44")
def test_the_seam_guard_notices_a_source_file_that_imports_the_seam(tmp_path: Path) -> None:
    """Negative case: the same scan, on a copy of `backend/src` with one injected file."""
    import shutil

    copy = tmp_path / "src"
    shutil.copytree(_ROOT / "backend" / "src", copy)
    assert _src_files_naming(copy, *_SEAM_NAMES) == []
    (copy / "app" / "injected.py").write_text(
        "from backend.tests.conftest_db import seed_as_owner\n", encoding="utf-8"
    )
    assert _src_files_naming(copy, *_SEAM_NAMES) == ["app/injected.py"]
