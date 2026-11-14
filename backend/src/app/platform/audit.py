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

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Final
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEventRow
from app.observability.trace import current_trace_id
from model_schema import (
    ArtifactHistory,
    ArtifactHistoryEntry,
    ArtifactRef,
    AuditEvent,
    AuditEventCore,
    FieldChange,
    JobSource,
    Principal,
    StatusTransition,
    compute_event_hash,
    new_uuid7,
)

__all__ = [
    "RETURNED_LEGACY_ACTIONS",
    "ChainBrokenError",
    "VerifiedSpan",
    "artifact_history",
    "field_diff",
    "record",
    "verify_chain",
    "verify_range",
]

#: C1 (#1783): a return from review is `<type>.returned`. Before it, these four types wrote
#: the forward state's name for the return too, so one name meant two transitions. Stored
#: rows keep that spelling (FR-370); this maps each new name to the legacy one, which a
#: query tells apart by `before.status == "review"`.
RETURNED_LEGACY_ACTIONS: Final = {
    "model.returned": "model.fitted",
    "custom_objective.returned": "custom_objective.certified",
    "custom_metric.returned": "custom_metric.certified",
    "peril_structure.returned": "peril_structure.reconciled",
}

# Namespace for pg_advisory_xact_lock, so the audit chain lock cannot collide with any
# other advisory lock the platform takes later.
_LOCK_NAMESPACE = 0x4749_5041  # "GIPA"


class ChainBrokenError(Exception):
    """The stored chain does not verify. Carries the first event that failed."""

    def __init__(
        self,
        event_id: UUID,
        sequence: int,
        reason: str,
        *,
        first_sequence: int = 1,
        checked: int = 0,
    ) -> None:
        super().__init__(f"audit chain broken at sequence {sequence} ({event_id}): {reason}")
        self.event_id = event_id
        self.sequence = sequence
        self.reason = reason
        #: Where the failed check began, and how many events it verified before the break.
        self.first_sequence = first_sequence
        self.checked = checked


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


@dataclass(frozen=True)
class VerifiedSpan:
    """What `verify_range` checked: the contiguous sequence span, and how many events.

    `first_sequence` and `last_sequence` are `None` when the span holds no event.
    """

    first_sequence: int | None
    last_sequence: int | None
    events_checked: int
    whole_chain: bool


async def verify_chain(session: AsyncSession, workspace_id: UUID) -> int:
    """Recompute every hash in a workspace's whole chain (FR-372). Returns the count checked.

    Raises `ChainBrokenError` at the first event whose stored hash disagrees with its content,
    or whose `prev_event_hash` does not match its predecessor. Both matter: the first
    detects an edited row, the second a removed one.
    """
    return (await verify_range(session, workspace_id)).events_checked


async def _resolve_span(
    session: AsyncSession, workspace_id: UUID, from_: datetime | None, to: datetime | None
) -> tuple[int, int] | None:
    """The contiguous sequence span a time range selects (#1497 Q6 (a)), or `None` if empty.

    From the first sequence with `at >= from_` to the last with `at <= to`. `at` is the
    transaction's start time while `sequence` is assigned under the lock, so `at` is not
    monotonic in `sequence`: the span is closed over sequence, not over the events whose `at`
    happens to fall in range, because a chain can only be checked over contiguous links.
    """
    first_where = [AuditEventRow.workspace_id == workspace_id]
    last_where = [AuditEventRow.workspace_id == workspace_id]
    if from_ is not None:
        first_where.append(AuditEventRow.at >= from_)
    if to is not None:
        last_where.append(AuditEventRow.at <= to)
    first = (
        await session.execute(select(func.min(AuditEventRow.sequence)).where(*first_where))
    ).scalar()
    last = (
        await session.execute(select(func.max(AuditEventRow.sequence)).where(*last_where))
    ).scalar()
    if first is None or last is None or first > last:
        return None
    return first, last


async def verify_range(
    session: AsyncSession,
    workspace_id: UUID,
    *,
    from_: datetime | None = None,
    to: datetime | None = None,
) -> VerifiedSpan:
    """`verify_chain` over the whole chain, or over the span `from_`/`to` select (FR-372).

    With neither bound this is the whole chain, and that is NFR-521's proof. With a range it
    checks every hash and link inside the span, and the first event's `prev_event_hash`
    against its predecessor's stored hash. **The predecessor itself is not verified**: the
    result's `first_sequence` says where the check began.

    Rows are streamed (`yield_per`), so a chain of seven years is never held in memory.
    """
    whole = from_ is None and to is None
    first_sequence = 1
    last_sequence: int | None = None
    expected_prev: str | None = None
    if not whole:
        span = await _resolve_span(session, workspace_id, from_, to)
        if span is None:
            return VerifiedSpan(None, None, 0, whole_chain=False)
        first_sequence, last_sequence = span
        if first_sequence > 1:
            expected_prev = (
                await session.execute(
                    select(AuditEventRow.event_hash).where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.sequence == first_sequence - 1,
                    )
                )
            ).scalar()

    query = select(AuditEventRow).where(
        AuditEventRow.workspace_id == workspace_id,
        AuditEventRow.sequence >= first_sequence,
    )
    if last_sequence is not None:
        query = query.where(AuditEventRow.sequence <= last_sequence)
    rows = await session.stream_scalars(
        query.order_by(AuditEventRow.sequence), execution_options={"yield_per": 1000}
    )

    expected_sequence = first_sequence
    checked = 0
    last_checked: int | None = None
    async for row in rows:
        if row.sequence != expected_sequence:
            raise ChainBrokenError(
                row.id,
                row.sequence,
                f"expected sequence {expected_sequence}",
                first_sequence=first_sequence,
                checked=checked,
            )
        if row.prev_event_hash != expected_prev:
            raise ChainBrokenError(
                row.id,
                row.sequence,
                "prev_event_hash does not match predecessor",
                first_sequence=first_sequence,
                checked=checked,
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
            raise ChainBrokenError(
                row.id,
                row.sequence,
                "content does not match stored hash",
                first_sequence=first_sequence,
                checked=checked,
            )

        expected_prev = row.event_hash
        last_checked = row.sequence
        expected_sequence += 1
        checked += 1
    return VerifiedSpan(
        first_sequence=first_sequence if checked else None,
        last_sequence=last_checked,
        events_checked=checked,
        whole_chain=whole,
    )


def _flatten(value: dict[str, Any] | None, prefix: str = "") -> dict[str, Any]:
    """`{"a": {"b": 1}}` as `{"a.b": 1}`. A list or a scalar is one value."""
    flat: dict[str, Any] = {}
    for key, item in (value or {}).items():
        path = f"{prefix}{key}"
        if isinstance(item, dict) and item:
            flat.update(_flatten(item, f"{path}."))
        else:
            flat[path] = item
    return flat


def field_diff(
    before: dict[str, Any] | None, after: dict[str, Any] | None
) -> list[FieldChange]:
    """The fields an event changed, from its `before` and `after` (#1497 Q2 (a)).

    A field present on one side only reads as `None` on the other. Governance sees only what
    the event carries; an artifact's own content diff is its owning module's (`06` §7.1).
    """
    old, new = _flatten(before), _flatten(after)
    return [
        FieldChange(path=path, before=old.get(path), after=new.get(path))
        for path in sorted(old.keys() | new.keys())
        if old.get(path) != new.get(path)
    ]


_LEGACY_RETURN_NAMES: Final = {legacy: new for new, legacy in RETURNED_LEGACY_ACTIONS.items()}


def _history_entry(row: AuditEventRow) -> ArtifactHistoryEntry:
    before_status = (row.before or {}).get("status")
    after_status = (row.after or {}).get("status")
    action = row.action
    if action in _LEGACY_RETURN_NAMES and before_status == "review":
        action = _LEGACY_RETURN_NAMES[action]  # C1: a pre-rename return reads as `returned`
    both = isinstance(before_status, str) and isinstance(after_status, str)
    return ArtifactHistoryEntry(
        sequence=row.sequence,
        at=row.at,
        actor=Principal.model_validate(row.actor),
        source=row.source,
        action=action,
        transition=(
            StatusTransition.model_validate({"from": before_status, "to": after_status})
            if both and before_status != after_status
            else None
        ),
        justification=row.justification,
        diff=field_diff(row.before, row.after),
        job_id=row.job_id,
        trace_id=row.trace_id,
    )


async def artifact_history(
    session: AsyncSession, workspace_id: UUID, ref: ArtifactRef
) -> ArtifactHistory:
    """Every event written under exactly `ref`, oldest first (FR-383).

    By exact `entity_ref`, on `ix_audit_events_entity_ref`: no prefix match, so the history
    of `model:motor@2` never includes `model:motor@20`. It is the audit log's own reading, so
    it needs nothing from the modules that own the artifact types (`06` §7.1, DEP-1).
    """
    rows = (
        await session.execute(
            select(AuditEventRow)
            .where(
                AuditEventRow.workspace_id == workspace_id,
                AuditEventRow.entity_ref == str(ref),
            )
            .order_by(AuditEventRow.sequence)
        )
    ).scalars()
    return ArtifactHistory(ref=ref, events=[_history_entry(row) for row in rows])
