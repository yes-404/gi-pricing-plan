"""The `environment_settings` migration leaves `api_keys` alone (FD-1650, PL-1666 D4.4).

WK-674 Slice 4.

`c5a91e7d3b26` creates `environment_settings` and, by its own docstring, touches no existing
table: a credential's secret is shown once (FR-389), so a migration that rewrote an `api_keys`
row could not be put right afterwards. SL-1257 shipped it with no committed round trip over a
database that holds keys. This is that test, mirroring `test_the_migration_round_trips` in
`test_migration_deployments.py` (its helpers and scratch database are imported, not rebuilt).

The revision is **not** the head (`d4e81b7a2c95` follows it), so each step pins a revision id
and `downgrade -1` is never taken from head.
"""

from __future__ import annotations

from typing import Any

import pytest
from alembic import command
from backend.tests.test_migration_deployments import (
    _alembic,
    _alembic_config,
    _insert_account,
    _insert_key,
    _revision_of,
    _run,
    _table_exists,
    _upgrade,
    scratch_database,  # noqa: F401 - a fixture, used by name
)

_BEFORE = "b8d2f4a6c0e1"  # the revision before `environment_settings`
_THIS_REVISION = "c5a91e7d3b26"


async def _api_key_rows(url: str) -> list[tuple[Any, ...]]:
    """Every `api_keys` row, every column, in primary-key order."""
    rows = await _run(url, "SELECT * FROM api_keys ORDER BY id")
    return [tuple(row) for row in rows]


@pytest.mark.req("FR-417", "FR-431", "FR-446")
async def test_environment_settings_round_trip_leaves_api_keys_unchanged(
    scratch_database: str,  # noqa: F811 - the imported fixture
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`upgrade`, `downgrade`, `upgrade` over a database holding `api_keys` rows (FD-1650)."""
    monkeypatch.setenv("GIP_MIGRATION_DATABASE_URL", scratch_database)
    cfg = _alembic_config()
    await _upgrade(cfg, _BEFORE)
    account = await _insert_account(scratch_database, "round-trip", ["dev", "uat"])
    await _insert_key(scratch_database, account, "dev")
    await _insert_key(scratch_database, account, "uat", revoked=True)
    await _insert_key(scratch_database, account, "dev", expired=True)
    before = await _api_key_rows(scratch_database)
    assert len(before) == 3

    steps = (
        ("upgrade", _upgrade, _THIS_REVISION),
        ("downgrade", lambda c, r: _alembic(command.downgrade, c, r), _BEFORE),
        ("upgrade again", _upgrade, _THIS_REVISION),
    )
    for name, step, revision in steps:
        await step(cfg, revision)
        assert await _revision_of(scratch_database) == revision, name
        assert await _table_exists(scratch_database, "environment_settings") == (
            revision == _THIS_REVISION
        ), name
        after = await _api_key_rows(scratch_database)
        assert after == before, f"api_keys rows differ after {name}: {before!r} != {after!r}"
