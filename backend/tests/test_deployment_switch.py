"""The two-phase deployment switch (WK-674 Slice 5; FR-268, FR-269; PL-1766 D5.6, D5.9).

Proved here with an in-memory transport and no database or Redis: the coordinator's rounds, a
process's `live` reference, and what each failure leaves behind. The DB-first ordering of the
deploy transaction and the Redis transport are proved where they run.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from uuid import UUID, uuid4

import pytest

from app.platform.deployment_switch import (
    LiveEntry,
    LiveRefs,
    SwitchIncompleteError,
    SwitchMember,
    SwitchMessage,
    commit_round,
    prepare_round,
)

WS = uuid4()
OLD = LiveEntry(uuid4(), "rating_version:motor@1", "a" * 64)
NEW = LiveEntry(uuid4(), "rating_version:motor@2", "b" * 64)


def _message(phase: str = "prepare", switch_id: str = "s1") -> SwitchMessage:
    return SwitchMessage(
        switch_id=switch_id,
        phase=phase,  # type: ignore[arg-type]
        workspace_id=WS,
        environment="uat",
        deployment_id=NEW.deployment_id,
        rating_version_ref=NEW.rating_version_ref,
        bundle_hash=NEW.bundle_hash,
    )


class _Bus:
    """An in-memory transport: each member sees every published message; acks are collected."""

    def __init__(self) -> None:
        self.members: dict[str, SwitchMember] = {}
        #: process ids that receive a phase but never ack it (a hung or partitioned process).
        self.mute: set[tuple[str, str]] = set()
        self._roster: set[str] = set()
        self._acks: dict[tuple[str, str], set[str]] = {}

    def join(
        self, process_id: str, hydrate: Callable[[SwitchMessage], Awaitable[None]] | None = None
    ) -> SwitchMember:
        async def _noop(_: SwitchMessage) -> None:
            return None

        live = LiveRefs()
        live.set(WS, "uat", OLD)
        member = SwitchMember(process_id, live, hydrate or _noop)
        self.members[process_id] = member
        self._roster.add(process_id)
        return member

    async def publish(self, message: SwitchMessage) -> int:
        for pid, member in self.members.items():
            if (pid, message.phase) in self.mute:
                continue
            if await member.handle(message):
                self._acks.setdefault((message.switch_id, message.phase), set()).add(pid)
        return len(self.members)

    async def acks(self, switch_id: str, phase: str, want: int, timeout: float) -> set[str]:
        return set(self._acks.get((switch_id, phase), set()))

    async def roster(self) -> set[str]:
        return set(self._roster)

    async def drop_from_roster(self, ids: set[str]) -> None:
        self._roster -= ids


async def test_a_switch_swaps_every_process_and_names_the_committed_set() -> None:
    bus = _Bus()
    for pid in ("api-1:1", "api-1:2", "api-2:1"):
        bus.join(pid)
    prepared = await prepare_round(bus, _message("prepare"), timeout=0.1)
    assert prepared == {"api-1:1", "api-1:2", "api-2:1"}
    assert all(m.live.get(WS, "uat") == OLD for m in bus.members.values()), "PREPARE swaps nothing"
    outcome = await commit_round(bus, _message("commit"), prepared, timeout=0.1)
    assert outcome.committed == prepared
    assert outcome.unacknowledged == frozenset()
    assert all(m.live.get(WS, "uat") == NEW for m in bus.members.values())


async def test_a_short_prepare_names_the_missing_process_and_swaps_nothing() -> None:
    bus = _Bus()
    for pid in ("api-1:1", "api-1:2"):
        bus.join(pid)
    bus.mute.add(("api-1:2", "prepare"))
    with pytest.raises(SwitchIncompleteError) as short:
        await prepare_round(bus, _message("prepare"), timeout=0.1)
    assert short.value.unacknowledged == {"api-1:2"}
    assert short.value.acknowledged == {"api-1:1"}
    assert all(m.live.get(WS, "uat") == OLD for m in bus.members.values())


async def test_a_partial_commit_names_the_unacknowledged_process_and_leaves_it_on_the_old_ref() -> (
    None
):
    bus = _Bus()
    for pid in ("api-1:1", "api-1:2"):
        bus.join(pid)
    prepared = await prepare_round(bus, _message("prepare"), timeout=0.1)
    bus.mute.add(("api-1:2", "commit"))
    outcome = await commit_round(bus, _message("commit"), prepared, timeout=0.1)
    assert outcome.committed == {"api-1:1"}
    assert outcome.unacknowledged == {"api-1:2"}
    assert bus.members["api-1:1"].live.get(WS, "uat") == NEW
    assert bus.members["api-1:2"].live.get(WS, "uat") == OLD


async def test_a_process_that_did_not_prepare_never_commits() -> None:
    bus = _Bus()
    member = bus.join("api-1:1")
    assert await member.handle(_message("commit")) is False
    assert member.live.get(WS, "uat") == OLD


async def test_a_failed_hydration_is_not_an_acknowledgement() -> None:
    async def broken(_: SwitchMessage) -> None:
        raise RuntimeError("bundle blob unreadable")

    bus = _Bus()
    bus.join("api-1:1")
    bus.join("api-1:2", hydrate=broken)
    with pytest.raises(SwitchIncompleteError) as short:
        await prepare_round(bus, _message("prepare"), timeout=0.1)
    assert short.value.unacknowledged == {"api-1:2"}


async def test_a_stale_roster_entry_is_pruned_when_every_receiver_acknowledged() -> None:
    bus = _Bus()
    bus.join("api-1:1")
    bus._roster.add("api-9:7")  # a crashed process that never left the roster
    prepared = await prepare_round(bus, _message("prepare"), timeout=0.1)
    assert prepared == {"api-1:1"}
    assert await bus.roster() == {"api-1:1"}


async def test_a_short_prepare_reports_a_roster_name_that_may_be_stale() -> None:
    bus = _Bus()
    bus.join("api-1:1")
    bus.join("api-1:2")
    bus.mute.add(("api-1:2", "prepare"))
    bus._roster.add("api-9:7")
    with pytest.raises(SwitchIncompleteError) as short:
        await prepare_round(bus, _message("prepare"), timeout=0.1)
    assert short.value.unacknowledged == {"api-1:2", "api-9:7"}
    assert await bus.roster() >= {"api-9:7"}, "a short round prunes nothing"


def test_a_fresh_process_serves_the_latest_committed_deployment() -> None:
    rows = [
        (WS, "uat", OLD.deployment_id, OLD.rating_version_ref, OLD.bundle_hash),
        (WS, "prod", NEW.deployment_id, NEW.rating_version_ref, NEW.bundle_hash),
    ]
    live = LiveRefs.from_latest(rows)
    assert live.get(WS, "uat") == OLD
    assert live.get(WS, "prod") == NEW
    assert live.get(WS, "dev") is None
    assert live.get(UUID(int=1), "uat") is None


def test_the_per_process_reference_is_read_once_per_call_not_shared_between_processes() -> None:
    a, b = LiveRefs(), LiveRefs()
    a.set(WS, "uat", NEW)
    assert b.get(WS, "uat") is None


async def test_concurrent_switches_for_different_environments_do_not_interfere() -> None:
    bus = _Bus()
    bus.join("api-1:1")
    msg_uat = _message("prepare", "s-uat")
    msg_prod = SwitchMessage(**{**msg_uat.__dict__, "switch_id": "s-prod", "environment": "prod"})
    a, b = await asyncio.gather(
        prepare_round(bus, msg_uat, timeout=0.1), prepare_round(bus, msg_prod, timeout=0.1)
    )
    assert a == b == {"api-1:1"}
