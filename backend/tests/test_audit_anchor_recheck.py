"""FR-373 (4): under the lock the signer re-reads that row N is the one it verified.

The chain is verified without the workspace lock, so a storage-layer edit to row N can land
between that verify and the lock. The anchor must then refuse rather than sign a head it did
not verify. No database: a scripted session answers each statement by what it asks for, so
the window between the verify and the lock is deterministic, and `anchor()` runs to
completion if the re-read is gone. The test then fails on its own assertion (a signed head),
never on the script running dry.
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
    key (none) and the database clock.
    """

    def __init__(self, head: tuple[int, UUID, str], current_hash: str | None) -> None:
        self._head = head
        self._current_hash = current_hash

    async def execute(self, statement: Any) -> _Result:
        sql = str(statement)
        if "now()" in sql:
            return _Result(_NOW)
        if "audit_events.id" in sql:
            return _Result(self._head)
        if "audit_events.action" in sql:
            return _Result(None)
        return _Result(self._current_hash)


async def _refused(session: _Session, appended: list[str]) -> audit.ChainBrokenError:
    """Run `anchor()`; return the refusal, or fail the test if it signed instead."""
    try:
        anchored = await audit.anchor(
            session,  # type: ignore[arg-type]
            workspace_id=new_uuid7(),
            key=Ed25519PrivateKey.generate(),
            actor=Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@b.example"),
            source=JobSource.API,
        )
    except audit.ChainBrokenError as exc:
        assert appended == [], "an anchor was appended after a head that changed"
        return exc
    pytest.fail(
        f"signed sequence {anchored.statement.head_sequence} although its hash "
        "changed after it was verified"
    )


@pytest.fixture
def appended(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """The actions `anchor()` appended, with the verify, the lock and the append stubbed."""
    calls: list[str] = []

    async def _verified(*_args: Any, **_kwargs: Any) -> None:
        return None

    async def _locked(*_args: Any, **_kwargs: Any) -> None:
        return None

    async def _record(*_args: Any, action: str, **_kwargs: Any) -> None:
        calls.append(action)

    monkeypatch.setattr(audit, "verify_range", _verified)
    monkeypatch.setattr(audit, "_lock_workspace", _locked)
    monkeypatch.setattr(audit, "record", _record)
    return calls


@pytest.mark.req("FR-373")
async def test_a_head_edited_between_the_verify_and_the_lock_is_refused(
    appended: list[str],
) -> None:
    event_id = new_uuid7()
    session = _Session((5, event_id, _VERIFIED), current_hash=_EDITED)
    refused = await _refused(session, appended)
    assert (refused.sequence, refused.event_id) == (5, event_id)
    assert "changed after it was verified" in refused.reason


@pytest.mark.req("FR-373")
async def test_a_head_removed_between_the_verify_and_the_lock_is_refused(
    appended: list[str],
) -> None:
    session = _Session((5, new_uuid7(), _VERIFIED), current_hash=None)
    await _refused(session, appended)


@pytest.mark.req("FR-373")
async def test_an_unchanged_head_is_signed_and_appended_once(appended: list[str]) -> None:
    """The control: the same script with the re-read agreeing signs N and appends the event."""
    session = _Session((5, new_uuid7(), _VERIFIED), current_hash=_VERIFIED)
    anchored = await audit.anchor(
        session,  # type: ignore[arg-type]
        workspace_id=new_uuid7(),
        key=Ed25519PrivateKey.generate(),
        actor=Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@b.example"),
        source=JobSource.API,
    )
    assert anchored.statement.head_sequence == 5
    assert anchored.statement.head_event_hash == _VERIFIED
    assert appended == [audit.ANCHORED_ACTION]
