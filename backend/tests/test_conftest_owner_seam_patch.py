"""The owner-seam patch (S1a, FD-1729): under the autouse fixture in `conftest_db`, the two
production seeding functions a test calls module-qualified are the owner-routed wrappers.

DB-free by design. "Runs on the owner engine" is proved by routing, not by connecting: the
wrappers reach the database only through `conftest_db.seed_as_owner`, whose body opens an
engine on `test_owner_database_url()`. A stub of `seed_as_owner` that records the call
therefore shows the wrapper took the one owner seam, with no database to ask `current_user`.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from backend.tests import conftest_db

from app.platform import rbac, workspaces

# Captured at import, before any fixture runs: the production functions themselves.
_ORIGINAL_ENSURE_WORKSPACE = workspaces.ensure_workspace
_ORIGINAL_SEED_BUILTIN_ROLES = rbac.seed_builtin_roles


def test_ensure_workspace_is_the_owner_routed_wrapper() -> None:
    assert workspaces.ensure_workspace is not _ORIGINAL_ENSURE_WORKSPACE


def test_seed_builtin_roles_is_the_owner_routed_wrapper() -> None:
    assert rbac.seed_builtin_roles is not _ORIGINAL_SEED_BUILTIN_ROLES


async def test_the_patched_functions_run_through_seed_as_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []

    async def stub_seed_as_owner(seed: object) -> str:
        calls.append(seed)
        return "owner"

    monkeypatch.setattr(conftest_db, "seed_as_owner", stub_seed_as_owner)

    assert await workspaces.ensure_workspace(None, workspace_id=uuid4()) == "owner"  # type: ignore[arg-type]
    assert await rbac.seed_builtin_roles(None, uuid4()) == "owner"  # type: ignore[arg-type]
    assert len(calls) == 2


@pytest.mark.production_seed
def test_a_production_seed_test_gets_the_original_functions() -> None:
    assert workspaces.ensure_workspace is _ORIGINAL_ENSURE_WORKSPACE
    assert rbac.seed_builtin_roles is _ORIGINAL_SEED_BUILTIN_ROLES
