"""Migration `9b3e7c15d4a2`: `routing_rules`, `shadow_configs`, `shadow_results`
(`03` §4.13; WK-674 Slice 6, `RL-1834`). Each runs on a throwaway database that
`test_migration_deployments.py`'s fixture creates and drops.
"""

from __future__ import annotations

import pytest
from alembic import command
from backend.tests.test_migration_deployments import (  # noqa: F401
    _alembic,
    _alembic_config,
    _revision_of,
    _run,
    _upgrade,
    scratch_database,
)
from sqlalchemy.exc import DBAPIError

_PREVIOUS = "a4d1f08c3b97"
_THIS = "9b3e7c15d4a2"
_TABLES = ("routing_rules", "shadow_configs", "shadow_results")
_HASH = "sha256:" + "a" * 64


async def _exists(url: str, table: str) -> bool:
    rows = await _run(url, "SELECT to_regclass(:t) IS NOT NULL", {"t": table})
    return bool(rows[0][0])


async def _privilege(url: str, table: str, kind: str) -> bool:
    rows = await _run(
        url, "SELECT has_table_privilege('gip_app', :t, :k)", {"t": table, "k": kind}
    )
    return bool(rows[0][0])


@pytest.mark.req("FR-270", "FR-271", "FR-417")
async def test_the_migration_round_trips(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    cfg = _alembic_config()
    await _upgrade(cfg, _PREVIOUS)
    await _upgrade(cfg, _THIS)
    assert await _revision_of(scratch_database) == _THIS
    for table in _TABLES:
        assert await _exists(scratch_database, table), table
    await _alembic(command.downgrade, cfg, "-1")
    assert await _revision_of(scratch_database) == _PREVIOUS
    for table in _TABLES:
        assert not await _exists(scratch_database, table), table
    await _upgrade(cfg, _THIS)
    assert await _revision_of(scratch_database) == _THIS


@pytest.mark.req("FR-4", "FR-270", "FR-271")
async def test_the_application_role_may_only_select_and_insert(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    await _upgrade(_alembic_config(), "head")
    for table in _TABLES:
        assert await _privilege(scratch_database, table, "SELECT"), table
        assert await _privilege(scratch_database, table, "INSERT"), table
        assert not await _privilege(scratch_database, table, "UPDATE"), table
        assert not await _privilege(scratch_database, table, "DELETE"), table


@pytest.mark.req("FR-4", "FR-270")
async def test_even_the_owner_cannot_update_or_delete_a_row(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The `artifact_append_only()` trigger stops the role the grants cannot."""
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    await _upgrade(_alembic_config(), "head")
    await _run(
        scratch_database,
        "INSERT INTO routing_rules (id, workspace_id, environment_id, ranges, written_by) "
        "VALUES (gen_random_uuid(), gen_random_uuid(), "
        "(SELECT id FROM environments WHERE slug = 'dev'), '[]'::jsonb, gen_random_uuid())",
    )
    with pytest.raises(DBAPIError):
        await _run(scratch_database, "UPDATE routing_rules SET ranges = '[1]'::jsonb")
    with pytest.raises(DBAPIError):
        await _run(scratch_database, "DELETE FROM routing_rules")
    with pytest.raises(DBAPIError):
        await _run(scratch_database, "TRUNCATE routing_rules")


@pytest.mark.req("FR-271")
@pytest.mark.parametrize("fraction", ["0", "-0.5", "1.5"])
async def test_a_fraction_outside_the_unit_interval_is_refused_by_the_database(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch, fraction: str
) -> None:
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    await _upgrade(_alembic_config(), "head")
    with pytest.raises(DBAPIError):
        await _run(
            scratch_database,
            "INSERT INTO shadow_configs (id, workspace_id, environment_id, "
            "candidate_rating_version_ref, candidate_bundle_hash, fraction, written_by) "
            "VALUES (gen_random_uuid(), gen_random_uuid(), "
            "(SELECT id FROM environments WHERE slug = 'dev'), 'rating_version:m@1', "
            f"'{_HASH}', {fraction}, gen_random_uuid())",
        )


@pytest.mark.req("FR-271")
async def test_a_malformed_bundle_hash_is_refused_by_the_database(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GIP_DATABASE_URL", scratch_database)
    await _upgrade(_alembic_config(), "head")
    with pytest.raises(DBAPIError):
        await _run(
            scratch_database,
            "INSERT INTO shadow_configs (id, workspace_id, environment_id, "
            "candidate_rating_version_ref, candidate_bundle_hash, fraction, written_by) "
            "VALUES (gen_random_uuid(), gen_random_uuid(), "
            "(SELECT id FROM environments WHERE slug = 'dev'), 'rating_version:m@1', "
            "'md5:xyz', 0.5, gen_random_uuid())",
        )
