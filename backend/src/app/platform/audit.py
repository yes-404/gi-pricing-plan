"""The audit sink — cross-cutting, and it lands before the governance module (DEP-537).

> **`06` R2** — Every governed transition writes its event in the same database
> transaction as the change. If the audit write fails, the change fails.

The whole design follows from taking that literally. `record()` takes the caller's
`AsyncSession` rather than opening its own; there is no `commit()` here, and no
`try/except` around the insert. A swallowed audit failure would leave a change with no
record, which is the one outcome the requirement forbids.

Chain integrity (FR-372) needs the previous event's hash, so appends are serialised per
workspace by a transaction-scoped advisory lock. Per *workspace*, not globally: two
workspaces have independent chains and must not queue behind each other.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEventRow
from app.observability.trace import current_trace_id
from model_schema import (
    AuditEvent,
    AuditEventCore,
    JobSource,
    Principal,
    compute_event_hash,
    new_uuid7,
)

__all__ = ["ChainBrokenError", "record", "verify_chain"]

# Namespace for pg_advisory_xact_lock, so the audit chain lock cannot collide with any
# other advisory lock the platform takes later.
_LOCK_NAMESPACE = 0x4749_5041  # "GIPA"


class ChainBrokenError(Exception):
    """The stored chain does not verify. Carries the first event that failed."""

    def __init__(self, event_id: UUID, sequence: int, reason: str) -> None:
        super().__init__(f"audit chain broken at sequence {sequence} ({event_id}): {reason}")
        self.event_id = event_id
        self.sequence = sequence
        self.reason = reason


async def record(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    source: JobSource,
    action: str,
    entity_ref: str,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    justification: str | None = None,
    job_id: UUID | None = None,
) -> AuditEvent:
    """Append one event to the workspace's chain, inside the caller's transaction.

    Deliberately not `async with session.begin()`: this must join the transaction that is
    already open, not start a nested one. If the caller has no transaction, that is a bug
    in the caller — the event would commit independently of the change it describes.
    """
    if not session.in_transaction():
        raise RuntimeError(
            "audit.record() requires an open transaction. `06` R2 makes the audit write "
            "share the caller's transaction — writing it in its own would leave the "
            "record and the change able to disagree. Use Database.unit_of_work()."
        )

    # Serialise appends for this workspace only. Transaction-scoped, so it releases on
    # commit or rollback without an explicit unlock — an unlock that a failure path could
    # skip would deadlock every later write to the workspace.
    await session.execute(
        text("SELECT pg_advisory_xact_lock(:ns, :key)").bindparams(
            ns=_LOCK_NAMESPACE, key=_workspace_lock_key(workspace_id)
        )
    )

    head = (
        await session.execute(
            select(AuditEventRow.event_hash, AuditEventRow.sequence)
            .where(AuditEventRow.workspace_id == workspace_id)
            .order_by(AuditEventRow.sequence.desc())
            .limit(1)
        )
    ).first()
    prev_hash = head[0] if head else None
    sequence = (head[1] + 1) if head else 1

    event_id = new_uuid7()
    at = (await session.execute(select(func.now()))).scalar_one()

    # Hash the model, never a hand-built dict of "the same" fields. Two serialisations
    # drift — they differed on datetime format the first time this was written, producing
    # a chain that verified against itself and failed against the exported record.
    core = AuditEventCore(
        id=event_id,
        workspace_id=workspace_id,
        at=at,
        actor=actor,
        source=source,
        action=action,
        entity_ref=entity_ref,
        before=before,
        after=after,
        justification=justification,
        trace_id=current_trace_id(),
        job_id=job_id,
    )
    event_hash = compute_event_hash(core, prev_event_hash=prev_hash)

    session.add(
        AuditEventRow(
            id=event_id,
            workspace_id=workspace_id,
            at=at,
            actor=actor.model_dump(mode="json"),
            source=source,
            action=action,
            entity_ref=entity_ref,
            before=before,
            after=after,
            justification=justification,
            trace_id=current_trace_id(),
            job_id=job_id,
            prev_event_hash=prev_hash,
            event_hash=event_hash,
            sequence=sequence,
        )
    )
    # Flush, not commit: a constraint violation must surface here — inside the caller's
    # transaction, where it still fails the change — rather than at commit time where the
    # caller has already returned success.
    await session.flush()

    return AuditEvent(
        **core.model_dump(), prev_event_hash=prev_hash, event_hash=event_hash
    )


def _workspace_lock_key(workspace_id: UUID) -> int:
    """Map a workspace to a signed 32-bit advisory-lock key.

    A collision costs contention between two workspaces, never correctness — the lock only
    serialises appends, and the sequence uniqueness constraint is the real guard.
    """
    return (workspace_id.int & 0x7FFF_FFFF) - 0x4000_0000


async def verify_chain(session: AsyncSession, workspace_id: UUID) -> int:
    """Recompute every hash in a workspace's chain (FR-372). Returns the count checked.

    Raises `ChainBrokenError` at the first event whose stored hash disagrees with its content,
    or whose `prev_event_hash` does not match its predecessor. Both matter: the first
    detects an edited row, the second a removed one.
    """
    rows = (
        await session.execute(
            select(AuditEventRow)
            .where(AuditEventRow.workspace_id == workspace_id)
            .order_by(AuditEventRow.sequence)
        )
    ).scalars()

    expected_prev: str | None = None
    expected_sequence = 1
    checked = 0
    for row in rows:
        if row.sequence != expected_sequence:
            raise ChainBrokenError(row.id, row.sequence, f"expected sequence {expected_sequence}")
        if row.prev_event_hash != expected_prev:
            raise ChainBrokenError(
                row.id, row.sequence, "prev_event_hash does not match predecessor"
            )

        core = AuditEventCore(
            id=row.id,
            workspace_id=row.workspace_id,
            at=row.at,
            actor=Principal.model_validate(row.actor),
            source=row.source,
            action=row.action,
            entity_ref=row.entity_ref,
            before=row.before,
            after=row.after,
            justification=row.justification,
            trace_id=row.trace_id,
            job_id=row.job_id,
        )
        if compute_event_hash(core, prev_event_hash=row.prev_event_hash) != row.event_hash:
            raise ChainBrokenError(row.id, row.sequence, "content does not match stored hash")

        expected_prev = row.event_hash
        expected_sequence += 1
        checked += 1
    return checked
