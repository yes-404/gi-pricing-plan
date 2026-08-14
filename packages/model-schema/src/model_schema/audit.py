"""The Audit Event and its hash chain (`06` §4.5, FR-GOV-20..26).

> **R2** — The audit log is append-only and complete. Every governed transition writes its
> event in the same database transaction as the change — if the audit write fails, the
> change fails.

Two things live here rather than in the backend.

The **shape**, because every module emits one and the frontend renders it (ADR-0002).

The **hash computation**, because FR-GOV-24 makes the chain a tamper-detection mechanism,
and a mechanism that can only be checked by the software under suspicion is not one. An
auditor with an exported CSV and this package must be able to recompute every hash and find
the break. That requires the serialisation to be canonical and stable — so it is pinned
here, with its own tests, and changing it is a breaking change to the audit record.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from model_schema.jobs import JobSource, Principal

__all__ = ["AuditEvent", "canonical_payload", "compute_event_hash"]

HASH_PREFIX = "sha256:"
_HASH_PATTERN = r"^sha256:[a-f0-9]{64}$"

#: `{noun}.{verb_past}` — matches audit-event.schema.json. A closed enum was rejected:
#: every module adds actions, and a registry in this package would make `model-schema`
#: depend on knowing every module's vocabulary.
ACTION_PATTERN = r"^[a-z_]+\.[a-z_]+$"


class AuditEventCore(BaseModel):
    """Exactly the fields the hash covers (FR-GOV-24).

    Split out so there is **one** serialisation of the hashed content. The writer computes
    the hash from this model and the verifier recomputes it from this model; a second,
    hand-built dict of "the same" fields is how a chain ends up self-consistent in one code
    path and broken in another — which is worse than no chain, because it verifies.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    workspace_id: UUID
    at: datetime
    actor: Principal
    source: JobSource
    action: str = Field(pattern=ACTION_PATTERN)
    entity_ref: str = Field(description="Canonical `{type}:{slug}@{version}` form (ID-3).")
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    justification: str | None = None
    trace_id: str | None = Field(default=None, pattern="^[0-9a-f]{32}$")
    job_id: UUID | None = Field(
        default=None, description="The Job that caused this change, where one did (FR-GOV-25)."
    )

    @field_validator("at")
    @classmethod
    def _timestamp_is_utc(cls, v: datetime) -> datetime:
        """FR-GOV-21 says UTC. A naive datetime is ambiguous the moment it is exported."""
        if v.tzinfo is None:
            raise ValueError("audit timestamps must be timezone-aware and UTC")
        return v


class AuditEvent(AuditEventCore):
    """One immutable record of a governed change (FR-GOV-21).

    `before`/`after` hold the changed state, not the whole entity: an audit log that
    duplicates every row is unreadable at the moment it is needed, and FR-GOV-26 forbids
    verbatim secrets and full quote inputs regardless.
    """

    prev_event_hash: str | None = Field(
        default=None,
        pattern=_HASH_PATTERN,
        description="Hash of the previous event in this workspace. Null for the first "
        "event — deliberately null rather than a sentinel, because a sentinel is "
        "indistinguishable from a real predecessor and would let a truncated chain verify.",
    )
    event_hash: str = Field(pattern=_HASH_PATTERN)

    @property
    def core(self) -> AuditEventCore:
        """The hashed subset of this event."""
        return AuditEventCore.model_validate(
            self.model_dump(exclude={"prev_event_hash", "event_hash"})
        )

    def recompute_hash(self) -> str:
        """Recompute this event's hash from its own fields."""
        return compute_event_hash(self.core, prev_event_hash=self.prev_event_hash)

    def verify(self) -> bool:
        """True when the stored hash matches the content. See `verify_chain` in the backend."""
        return self.recompute_hash() == self.event_hash


def canonical_payload(core: AuditEventCore, prev_event_hash: str | None) -> bytes:
    """Serialise the hashed fields deterministically.

    Every field of `AuditEventCore` is covered, plus `prev_event_hash` — which is what
    chains the events rather than merely timestamping them. Removing a middle event breaks
    every hash after it.

    Canonical means: JSON, keys sorted, no insignificant whitespace, UTF-8, non-ASCII kept
    as characters rather than escaped. Values come from Pydantic's JSON mode, so a
    round-trip through the API produces the same bytes as a round-trip through the
    database — including the datetime format, which is the detail that silently splits two
    hand-written serialisers.
    """
    data: dict[str, Any] = core.model_dump(mode="json")
    data["prev_event_hash"] = prev_event_hash
    return json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def compute_event_hash(core: AuditEventCore, *, prev_event_hash: str | None) -> str:
    """`sha256:<hex>` over the canonical payload (FR-GOV-24)."""
    digest = hashlib.sha256(canonical_payload(core, prev_event_hash)).hexdigest()
    return f"{HASH_PREFIX}{digest}"
