"""FR-373 (4): under the lock the signer re-reads that row N is the one it verified.

The chain is verified without the workspace lock, so a storage-layer edit to row N can land
between that verify and the lock. The anchor must then refuse rather than sign a head it did
not verify. No database: a scripted session returns the rows, so the window between the
verify and the lock is made deterministic.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.platform import audit
from model_schema import ActorKind, JobSource, Principal, new_uuid7

_VERIFIED = "sha256:" + "11" * 32
_EDITED = "sha256:" + "22" * 32


class _Result:
    def __init__(self, row: Any) -> None:
        self._row = row

    def first(self) -> Any:
        return self._row

    def scalar(self) -> Any:
        return self._row


class _ScriptedSession:
    """Answers `execute` from a fixed script, in order, and records nothing else."""

    def __init__(self, *rows: Any) -> None:
        self._rows = list(rows)

    async def execute(self, _statement: Any) -> _Result:
        return _Result(self._rows.pop(0))


async def _anchor(session: _ScriptedSession, workspace_id: UUID) -> Any:
    return await audit.anchor(
        session,  # type: ignore[arg-type]
        workspace_id=workspace_id,
        key=Ed25519PrivateKey.generate(),
        actor=Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@b.example"),
        source=JobSource.API,
    )


@pytest.fixture(autouse=True)
def _no_database(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _verified(*_args: Any, **_kwargs: Any) -> None:
        return None

    async def _locked(*_args: Any, **_kwargs: Any) -> None:
        return None

    async def _never_appended(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("an anchor was appended after a head that changed")

    monkeypatch.setattr(audit, "verify_range", _verified)
    monkeypatch.setattr(audit, "_lock_workspace", _locked)
    monkeypatch.setattr(audit, "record", _never_appended)


@pytest.mark.req("FR-373")
async def test_a_head_edited_between_the_verify_and_the_lock_is_refused() -> None:
    workspace_id, event_id = new_uuid7(), new_uuid7()
    # The head read sees (sequence 5, its id, the hash that was verified); the re-read under
    # the lock finds a different hash at sequence 5.
    session = _ScriptedSession((5, event_id, _VERIFIED), _EDITED)
    with pytest.raises(audit.ChainBrokenError) as refused:
        await _anchor(session, workspace_id)
    assert (refused.value.sequence, refused.value.event_id) == (5, event_id)
    assert "changed after it was verified" in refused.value.reason


@pytest.mark.req("FR-373")
async def test_a_head_removed_between_the_verify_and_the_lock_is_refused() -> None:
    event_id = new_uuid7()
    session = _ScriptedSession((5, event_id, _VERIFIED), None)
    with pytest.raises(audit.ChainBrokenError):
        await _anchor(session, new_uuid7())
