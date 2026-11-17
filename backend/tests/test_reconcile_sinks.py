"""The reconcile report's two exception sinks carry no stored text (FR-2163, NFR-499).

Database-free: the verifier and the loader are stubbed, so no session is touched.
"""

from __future__ import annotations

import dataclasses
import json
from typing import Any
from uuid import UUID, uuid4

import pytest

from app.platform import audit
from app.platform import reconcile as rc

pytestmark = pytest.mark.req("FR-2163")

SENTINEL = "SENTINEL-row-text-9f3a"


def _line(report: rc.WorkspaceReport) -> str:
    return json.dumps(dataclasses.asdict(report), default=str)


async def test_a_broken_chain_report_is_the_reason_and_the_position_never_the_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def broken(session: Any, workspace_id: UUID) -> int:
        exc = audit.ChainBrokenError(uuid4(), 7, "content does not match stored hash")
        exc.args = (SENTINEL,)  # the message is made to carry the sentinel
        raise exc

    monkeypatch.setattr(audit, "verify_chain", broken)
    report = await rc.reconcile(None, uuid4())  # type: ignore[arg-type]
    assert report.chain == "broken"
    assert (
        report.chain_detail
        == "audit chain broken at sequence 7: content does not match stored hash"
    )
    assert SENTINEL not in _line(report)


async def test_an_unreadable_workspace_report_is_the_type_name_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def intact(session: Any, workspace_id: UUID) -> int:
        return 0

    async def unreadable(session: Any, workspace_id: UUID) -> rc.WorkspaceData:
        raise ValueError(f"bad stored row: {SENTINEL}")

    monkeypatch.setattr(audit, "verify_chain", intact)
    monkeypatch.setattr(rc, "load_workspace_data", unreadable)
    report = await rc.reconcile(None, uuid4())  # type: ignore[arg-type]
    assert report.chain == "unreadable"
    assert report.chain_detail == "ValueError"
    assert SENTINEL not in _line(report)
