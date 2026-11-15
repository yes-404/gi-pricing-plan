"""FR-373 (4): the order of the anchor, and the re-read of row N under the lock.

The chain is verified without the workspace lock, so a storage-layer edit to row N can land
between that verify and the lock. The anchor must then refuse rather than sign a head it did
not verify, and the order verify, lock, re-read, sign, append is what makes that so: a lock
taken after the re-read, or not at all, leaves the same window open.

No database: a scripted session answers each statement by what it asks for, so the window
between the verify and the lock is deterministic, and `anchor()` runs to completion if the
re-read is gone. The tests then fail on their own assertion (a signed head, or the wrong
order), never on the script running dry.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.platform import audit
from model_schema import ActorKind, JobSource, Principal, new_uuid7

_VERIFIED = "sha256:" + "11" * 32
_EDITED = "sha256:" + "22" * 32
_NOW = datetime(2026, 11, 15, 10, 0, tzinfo=UTC)
_SLUG = "motor-gb"
_ORDER = ["verify", "lock", "re-read", "sign", "append"]


class _Result:
    def __init__(self, row: Any) -> None:
        self._row = row

    def first(self) -> Any:
        return self._row

    def scalar(self) -> Any:
        return self._row

    def scalar_one(self) -> Any:
        return self._row


class _Session:
    """Answers each `execute` by the statement's text, so the number of calls is free.

    The head read returns `(sequence, id, hash)` as verified; the read of row N's hash under
    the lock returns `current_hash` (`None` when the row is gone); the rest are the previous
    key (none), the workspace slug and the database clock. The read of row N's hash is logged
    as `re-read` in `calls`.
    """

    def __init__(
        self, head: tuple[int, UUID, str], current_hash: str | None, calls: list[str]
    ) -> None:
        self._head = head
        self._current_hash = current_hash
        self._calls = calls

    async def execute(self, statement: Any) -> _Result:
        sql = str(statement)
        if "now()" in sql:
            return _Result(_NOW)
        if "audit_events.id" in sql:
            return _Result(self._head)
        if "audit_events.action" in sql:
            return _Result(None)
        if "slug" in sql:
            return _Result(_SLUG)
        self._calls.append("re-read")
        return _Result(self._current_hash)


class _RecordingKey:
    """An Ed25519 key that logs the moment it signs."""

    def __init__(self, calls: list[str]) -> None:
        self._key = Ed25519PrivateKey.generate()
        self._calls = calls

    def public_key(self) -> Any:
        return self._key.public_key()

    def sign(self, data: bytes) -> bytes:
        self._calls.append("sign")
        return self._key.sign(data)


async def _anchor(session: _Session, key: Any) -> audit.AuditAnchor:
    return await audit.anchor(
        session,  # type: ignore[arg-type]
        workspace_id=new_uuid7(),
        key=key,
        actor=Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@b.example"),
        source=JobSource.API,
    )


async def _refused(session: _Session, appended: list[str]) -> audit.ChainBrokenError:
    """Run `anchor()`; return the refusal, or fail the test if it signed instead."""
    try:
        anchored = await _anchor(session, _RecordingKey([]))
    except audit.ChainBrokenError as exc:
        assert appended == [], "an anchor was appended after a head that changed"
        return exc
    pytest.fail(
        f"signed sequence {anchored.statement.head_sequence} although its hash "
        "changed after it was verified"
    )


@pytest.fixture
def calls() -> list[str]:
    """The order in which `anchor()` verified, locked, re-read, signed and appended."""
    return []


@pytest.fixture
def appended(monkeypatch: pytest.MonkeyPatch, calls: list[str]) -> list[str]:
    """The `entity_ref` of each event `anchor()` appended, with verify, lock and append stubbed."""
    refs: list[str] = []

    async def _verified(*_args: Any, **_kwargs: Any) -> None:
        calls.append("verify")

    async def _locked(*_args: Any, **_kwargs: Any) -> None:
        calls.append("lock")

    async def _record(*_args: Any, action: str, entity_ref: str, **_kwargs: Any) -> None:
        assert action == audit.ANCHORED_ACTION
        calls.append("append")
        refs.append(entity_ref)

    monkeypatch.setattr(audit, "verify_range", _verified)
    monkeypatch.setattr(audit, "_lock_workspace", _locked)
    monkeypatch.setattr(audit, "record", _record)
    return refs


@pytest.mark.req("FR-373")
async def test_a_head_edited_between_the_verify_and_the_lock_is_refused(
    appended: list[str], calls: list[str]
) -> None:
    event_id = new_uuid7()
    session = _Session((5, event_id, _VERIFIED), current_hash=_EDITED, calls=calls)
    refused = await _refused(session, appended)
    assert (refused.sequence, refused.event_id) == (5, event_id)
    assert "changed after it was verified" in refused.reason


@pytest.mark.req("FR-373")
async def test_a_head_removed_between_the_verify_and_the_lock_is_refused(
    appended: list[str], calls: list[str]
) -> None:
    session = _Session((5, new_uuid7(), _VERIFIED), current_hash=None, calls=calls)
    await _refused(session, appended)


@pytest.mark.req("FR-373")
async def test_an_unchanged_head_is_signed_and_appended_once_under_the_workspace_ref(
    appended: list[str], calls: list[str]
) -> None:
    """The control: the same script with the re-read agreeing signs N and appends the event,
    and the event is about the workspace in FR-369's `{type}:{slug}@{version}` form, the one
    the workspace switch writes (`workspace:<slug>@1`), not a second spelling."""
    session = _Session((5, new_uuid7(), _VERIFIED), current_hash=_VERIFIED, calls=calls)
    anchored = await _anchor(session, _RecordingKey(calls))
    assert anchored.statement.head_sequence == 5
    assert anchored.statement.head_event_hash == _VERIFIED
    assert appended == [f"workspace:{_SLUG}@1"]



@pytest.mark.req("FR-373")
async def test_the_anchor_verifies_then_locks_then_rereads_then_signs_then_appends(
    appended: list[str], calls: list[str]
) -> None:
    """The lock is what makes the re-read mean something: taken after it, or not taken, the
    same window is open. Plant (a): remove the `_lock_workspace` call, and `lock` is absent.
    Plant (b): move it after the re-read, and `lock` follows `re-read`. Each reddens this."""
    session = _Session((5, new_uuid7(), _VERIFIED), current_hash=_VERIFIED, calls=calls)
    await _anchor(session, _RecordingKey(calls))
    assert calls == _ORDER
