"""`06` R2 and FR-GOV-20..24 — the invariants that cannot be retrofitted.

Against a real PostgreSQL. Every claim here is about what the *database* refuses, so a
mock would test the wrong thing.
"""

from __future__ import annotations

import json

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, InternalError, ProgrammingError

from app.db.models import AuditEventRow, JobRow
from app.db.session import Database
from app.platform import audit
from app.platform.audit import ChainBrokenError
from model_schema import (
    ActorKind,
    AuditEventCore,
    JobSource,
    Principal,
    compute_event_hash,
    new_uuid7,
)


async def _record(session, workspace_id, principal, action="job.submitted", **kw):
    return await audit.record(
        session,
        workspace_id=workspace_id,
        actor=principal,
        source=JobSource.API,
        action=action,
        entity_ref=kw.pop("entity_ref", "job:test@1"),
        **kw,
    )


@pytest.mark.req("FR-GOV-20")
async def test_event_is_written_in_the_callers_transaction(
    database: Database, workspace_id, principal
) -> None:
    async with database.unit_of_work() as session:
        event = await _record(session, workspace_id, principal)

    async with database.session() as session:
        stored = (
            await session.execute(
                select(AuditEventRow).where(AuditEventRow.workspace_id == workspace_id)
            )
        ).scalars().all()
    assert len(stored) == 1
    assert stored[0].event_hash == event.event_hash


@pytest.mark.req("FR-GOV-20")
@pytest.mark.req("NFR-GOV-2")
async def test_rollback_discards_the_change_and_its_audit_event_together(
    database: Database, workspace_id, principal
) -> None:
    """R2's real content: the record and the change cannot disagree."""
    from model_schema import JobKind, JobQueue, JobStatus

    # PT012: the block is the test — the failure must happen *after* both writes,
    # inside the transaction, which cannot be expressed as a single statement.
    with pytest.raises(RuntimeError, match="deliberate"):  # noqa: PT012
        async with database.unit_of_work() as session:
            session.add(
                JobRow(
                    workspace_id=workspace_id,
                    kind=JobKind.MODEL_FIT,
                    status=JobStatus.QUEUED,
                    queue=JobQueue.COMPUTE,
                    source=JobSource.API,
                    submitted_by=principal.model_dump(mode="json"),
                    parameters={},
                    retries={},
                )
            )
            await session.flush()
            await _record(session, workspace_id, principal)
            raise RuntimeError("deliberate failure after both writes")

    async with database.session() as session:
        jobs = (
            await session.execute(select(JobRow).where(JobRow.workspace_id == workspace_id))
        ).scalars().all()
        events = (
            await session.execute(
                select(AuditEventRow).where(AuditEventRow.workspace_id == workspace_id)
            )
        ).scalars().all()
    assert jobs == []
    assert events == []


@pytest.mark.req("FR-GOV-20")
async def test_recording_without_a_transaction_is_refused(
    database: Database, workspace_id, principal
) -> None:
    """Negative: an audit write in its own transaction could outlive a rolled-back change."""
    async with database.session() as session:
        with pytest.raises(RuntimeError, match="requires an open transaction"):
            await _record(session, workspace_id, principal)


@pytest.mark.req("FR-GOV-24")
async def test_chain_links_each_event_to_its_predecessor(
    database: Database, workspace_id, principal
) -> None:
    async with database.unit_of_work() as session:
        first = await _record(session, workspace_id, principal, action="job.submitted")
        second = await _record(session, workspace_id, principal, action="job.running")
        third = await _record(session, workspace_id, principal, action="job.succeeded")

    assert first.prev_event_hash is None
    assert second.prev_event_hash == first.event_hash
    assert third.prev_event_hash == second.event_hash

    async with database.session() as session:
        assert await audit.verify_chain(session, workspace_id) == 3


@pytest.mark.req("FR-GOV-24")
async def test_chains_are_independent_per_workspace(
    database: Database, principal
) -> None:
    """Two workspaces must not interleave, or one tenant's writes reorder another's chain."""
    a, b = new_uuid7(), new_uuid7()
    async with database.unit_of_work() as session:
        first_a = await _record(session, a, principal)
        first_b = await _record(session, b, principal)
    assert first_a.prev_event_hash is None
    assert first_b.prev_event_hash is None

    async with database.session() as session:
        assert await audit.verify_chain(session, a) == 1
        assert await audit.verify_chain(session, b) == 1


@pytest.mark.req("FR-GOV-24")
async def test_an_event_verifies_against_its_own_content(
    database: Database, workspace_id, principal
) -> None:
    async with database.unit_of_work() as session:
        event = await _record(session, workspace_id, principal, justification="because")
    assert event.verify()
    assert event.recompute_hash() == event.event_hash


@pytest.mark.req("FR-GOV-24")
async def test_tampering_below_the_application_is_detected(
    database: Database, workspace_id, principal
) -> None:
    """The chain's purpose (FR-GOV-24): detect what privileges and triggers cannot prevent.

    `session_replication_role = replica` disables triggers, which is exactly how a
    privileged operator would edit the log. The hash chain is the layer that survives it.
    """
    async with database.unit_of_work() as session:
        await _record(session, workspace_id, principal, action="job.submitted")
        await _record(session, workspace_id, principal, action="job.succeeded")

    async with database.unit_of_work() as session:
        await session.execute(text("SET LOCAL session_replication_role = replica"))
        await session.execute(
            text(
                "UPDATE audit_events SET action = 'job.failed' "
                "WHERE workspace_id = :ws AND sequence = 2"
            ).bindparams(ws=workspace_id)
        )

    async with database.session() as session:
        with pytest.raises(ChainBrokenError) as exc:
            await audit.verify_chain(session, workspace_id)
    assert exc.value.sequence == 2
    assert "content does not match stored hash" in exc.value.reason


@pytest.mark.req("FR-GOV-24")
async def test_removing_a_middle_event_is_detected(
    database: Database, workspace_id, principal
) -> None:
    """A deletion breaks the sequence *and* the prev-hash link. Either alone is enough."""
    async with database.unit_of_work() as session:
        await _record(session, workspace_id, principal, action="job.submitted")
        await _record(session, workspace_id, principal, action="job.running")
        await _record(session, workspace_id, principal, action="job.succeeded")

    async with database.unit_of_work() as session:
        await session.execute(text("SET LOCAL session_replication_role = replica"))
        await session.execute(
            text("DELETE FROM audit_events WHERE workspace_id = :ws AND sequence = 2")
            .bindparams(ws=workspace_id)
        )

    async with database.session() as session:
        with pytest.raises(ChainBrokenError) as exc:
            await audit.verify_chain(session, workspace_id)
    assert exc.value.sequence == 3


@pytest.mark.req("FR-GOV-22")
@pytest.mark.parametrize(
    "statement", ["UPDATE audit_events SET action = 'x'", "DELETE FROM audit_events"]
)
async def test_update_and_delete_are_rejected_by_the_database(
    database: Database, workspace_id, principal, statement: str
) -> None:
    """Negative: the trigger blocks even the table owner, which privileges cannot."""
    async with database.unit_of_work() as session:
        await _record(session, workspace_id, principal)

    with pytest.raises((DBAPIError, InternalError, ProgrammingError)) as exc:
        async with database.unit_of_work() as session:
            await session.execute(
                text(f"{statement} WHERE workspace_id = :ws").bindparams(ws=workspace_id)
            )
    assert "append-only" in str(exc.value)


@pytest.mark.req("FR-GOV-22")
async def test_truncate_is_rejected(database: Database, workspace_id, principal) -> None:
    """Row triggers do not fire on TRUNCATE — without a statement trigger this wipes the log."""
    async with database.unit_of_work() as session:
        await _record(session, workspace_id, principal)

    with pytest.raises((DBAPIError, InternalError, ProgrammingError)) as exc:
        async with database.unit_of_work() as session:
            await session.execute(text("TRUNCATE audit_events"))
    assert "append-only" in str(exc.value)

    async with database.session() as session:
        surviving = (
            await session.execute(
                select(AuditEventRow).where(AuditEventRow.workspace_id == workspace_id)
            )
        ).scalars().all()
    assert len(surviving) == 1


@pytest.mark.req("FR-GOV-22")
async def test_application_role_holds_insert_and_select_only(database: Database) -> None:
    """FR-GOV-22 literally: the role the application connects as cannot UPDATE or DELETE.

    Checked as granted privilege rather than by connecting as `gip_app` — the role is
    NOLOGIN by design, because provisioning a credential in a migration is what R3 forbids.
    """
    async with database.session() as session:
        granted = set(
            (
                await session.execute(
                    text(
                        "SELECT privilege_type FROM information_schema.table_privileges "
                        "WHERE grantee = 'gip_app' AND table_name = 'audit_events'"
                    )
                )
            ).scalars()
        )
    assert granted == {"SELECT", "INSERT"}


@pytest.mark.req("FR-GOV-21")
async def test_event_records_actor_action_entity_and_trace(
    database: Database, workspace_id, principal
) -> None:
    from app.observability.trace import bind_trace_id, reset_trace_id

    token = bind_trace_id("4bf92f3577b34da6a3ce929d0e0e4736")
    try:
        async with database.unit_of_work() as session:
            event = await _record(
                session,
                workspace_id,
                principal,
                action="rating_version.approved",
                entity_ref="rating_version:motor-gb@27",
                before={"status": "review"},
                after={"status": "approved"},
                justification="Dislocation within the agreed envelope.",
            )
    finally:
        reset_trace_id(token)

    assert event.actor == principal
    assert event.action == "rating_version.approved"
    assert event.entity_ref == "rating_version:motor-gb@27"
    assert event.trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert event.at.tzinfo is not None


@pytest.mark.req("FR-GOV-24")
async def test_hash_is_reproducible_from_an_export(
    database: Database, workspace_id, principal
) -> None:
    """An auditor with an exported record and model-schema must reach the same digest.

    The route taken here is the auditor's: serialise the event to JSON, parse it back with
    no access to the writing code, and recompute. If the platform were the only thing that
    could verify its own chain, the chain would prove nothing.
    """
    async with database.unit_of_work() as session:
        event = await _record(session, workspace_id, principal, justification="exported")

    exported = json.loads(event.model_dump_json())
    prev = exported.pop("prev_event_hash")
    stored_hash = exported.pop("event_hash")

    reparsed = AuditEventCore.model_validate(exported)
    assert compute_event_hash(reparsed, prev_event_hash=prev) == stored_hash == event.event_hash


@pytest.mark.req("FR-GOV-21")
async def test_system_principal_needs_no_id_but_a_user_does() -> None:
    Principal(kind=ActorKind.SYSTEM)
    with pytest.raises(ValueError, match="must carry an id"):
        Principal(kind=ActorKind.USER)
