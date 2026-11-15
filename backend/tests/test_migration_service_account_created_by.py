"""The `service_accounts.created_by` migration (#1843, FR-348).

Alembic against a scratch database, the shape of `test_migration_deployments.py` (its
fixture and helpers are imported, not re-written). The scratch database is upgraded to the
head before this revision, accounts and a creation audit event are inserted there, then
`upgrade head` runs over them: the only way to test the backfill.
"""

from __future__ import annotations

import pytest
from backend.tests.test_migration_deployments import (
    _alembic_config,
    _insert_account,
    _run,
    _upgrade,
    scratch_database,  # noqa: F401  (fixture)
)

from model_schema import new_uuid7

_PREVIOUS_REVISION = "c3a8e51f7d20"


async def _insert_creation_event(url: str, workspace_id, slug: str, actor_id, seq: int) -> None:
    await _run(
        url,
        "INSERT INTO audit_events (id, workspace_id, actor, source, action, entity_ref, "
        "event_hash, sequence) VALUES (:id, :ws, CAST(:actor AS jsonb), 'api', "
        "'service_account.created', :ref, :hash, :seq)",
        {
            "id": new_uuid7(),
            "ws": workspace_id,
            "actor": f'{{"kind": "user", "id": "{actor_id}", "display": "a"}}',
            "ref": f"service_account:{slug}@1",
            "hash": "sha256:" + f"{seq:064x}",
            "seq": seq,
        },
    )


@pytest.mark.req("FR-348")
async def test_the_backfill_sets_the_owner_from_the_creation_event_and_leaves_the_rest_null(
    scratch_database: str, monkeypatch: pytest.MonkeyPatch  # noqa: F811
) -> None:
    monkeypatch.setenv("GIP_MIGRATION_DATABASE_URL", scratch_database)
    cfg = _alembic_config()
    await _upgrade(cfg, _PREVIOUS_REVISION)

    owner = new_uuid7()
    with_event = await _insert_account(scratch_database, "with-event", ["dev"])
    without_event = await _insert_account(scratch_database, "no-event", ["dev"])
    workspace = (
        await _run(
            scratch_database, "SELECT workspace_id FROM service_accounts WHERE id = :id",
            {"id": with_event},
        )
    )[0][0]
    await _insert_creation_event(scratch_database, workspace, "with-event", owner, 1)

    await _upgrade(cfg, "head")

    rows = await _run(
        scratch_database,
        "SELECT id, created_by FROM service_accounts WHERE id = ANY(:ids)",
        {"ids": [with_event, without_event]},
    )
    assert {r[0]: r[1] for r in rows} == {with_event: owner, without_event: None}
