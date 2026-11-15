"""The audit hash chain's bytes are pinned (FR-372, FR-370, #1497 slice 5).

A changed chain hash is data loss: every stored audit log would stop verifying. These tests fail
if anything that feeds the hash changes, and none of them recomputes its expectation with the
code under test.

1. `test_a_fixed_events_hash_is_a_literal_digest`: one fixed event, its digest written here.
2. The field set. The canonical form sorts keys, so order does not move the bytes, and
   `test_field_order_does_not_move_the_digest` pins that property against the literal digest.
   `test_the_hashed_fields_and_their_order_are_pinned` pins the field set (and, harmlessly, the
   declaration order); a renamed, dropped or added field also turns the digest test red.
3. `test_a_chain_written_before_slice_5_verifies_now`: `fixtures/audit-chain-base.jsonl` was
   written by the code at base `5ba4f404` and is verified here by the current verifier.
"""

from __future__ import annotations

import pathlib
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import pytest

from model_schema import (
    ActorKind,
    AuditEvent,
    AuditEventCore,
    JobSource,
    Principal,
    compute_event_hash,
)

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "audit-chain-base.jsonl"

#: The digest of `_fixed_core()` with `_PREV`, computed by the code at base `5ba4f404` and
#: quoted here (run log: scratch run4-base-fixture.log).
BASE_DIGEST = "sha256:33f771dffeeac293ece9789c6199f6f3512a72ba63cd4deddeac40bc4855b896"
_PREV = "sha256:" + "3b8e" * 16


def _fixed_core() -> AuditEventCore:
    return AuditEventCore(
        id=UUID("0190b5a2-7c3e-7a10-9d21-4f6b8c2e1a02"),
        workspace_id=UUID("0190b5a2-7c3e-7a10-9d21-4f6b8c2e1a01"),
        at=datetime(2026, 9, 13, 10, 11, 0, 482000, tzinfo=UTC),
        actor=Principal(
            kind=ActorKind.USER,
            id=UUID("0190b5a2-7c3e-7a10-9d21-4f6b8c2e1a03"),
            display="a.actuary@insurer.example",
        ),
        source=JobSource.UI,
        action="rating_version.approved",
        entity_ref="rating_version:motor-gb@27",
        before={"status": "review", "approvers_recorded": 1},
        after={"status": "approved", "approvers_recorded": 2, "note": "café £"},
        justification="Dislocation within the agreed envelope; GIPP clean.",
        trace_id="4bf92f3577b34da6a3ce929d0e0e4736",
        job_id=UUID("0190b5a2-7c3e-7a10-9d21-4f6b8c2e1a04"),
    )


@pytest.mark.req("FR-372")
def test_a_fixed_events_hash_is_a_literal_digest() -> None:
    assert compute_event_hash(_fixed_core(), prev_event_hash=_PREV) == BASE_DIGEST


class _Reordered:
    """A core whose `model_dump` yields the same fields in reverse order."""

    def __init__(self, core: AuditEventCore) -> None:
        self._core = core

    def model_dump(self, *, mode: str) -> dict[str, Any]:
        dumped = self._core.model_dump(mode=mode)
        return dict(reversed(list(dumped.items())))


@pytest.mark.req("FR-372")
def test_field_order_does_not_move_the_digest() -> None:
    """Order-independence is a pinned property: the canonical form sorts keys, so the same
    fields in any order give the literal digest above. (The fields themselves are what the
    digest depends on; the next test pins them.)"""
    reordered = _Reordered(_fixed_core())
    digest = compute_event_hash(reordered, prev_event_hash=_PREV)  # type: ignore[arg-type]
    assert digest == BASE_DIGEST


@pytest.mark.req("FR-372")
def test_the_hashed_fields_and_their_order_are_pinned() -> None:
    assert list(AuditEventCore.model_fields) == [
        "id",
        "workspace_id",
        "at",
        "actor",
        "source",
        "action",
        "entity_ref",
        "before",
        "after",
        "justification",
        "trace_id",
        "job_id",
    ]
    assert list(AuditEvent.model_fields)[-2:] == ["prev_event_hash", "event_hash"]


@pytest.mark.req("FR-372")
def test_a_chain_written_before_slice_5_verifies_now() -> None:
    assert FIXTURE.exists(), f"{FIXTURE.name} is produced by the base code (see the slice runs)"
    events = [AuditEvent.model_validate_json(line) for line in FIXTURE.read_text().splitlines()]
    assert len(events) >= 3
    assert events[0].prev_event_hash is None
    assert all(event.verify() for event in events)
    assert [e.prev_event_hash for e in events[1:]] == [e.event_hash for e in events[:-1]]
