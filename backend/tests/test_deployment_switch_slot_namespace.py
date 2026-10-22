"""The switch's channels are per gate slot (FD-1838; WK-1178).

PUBLISH's receiver count is the PREPARE quorum and it counts subscribers server-wide, in every
Redis db. A second process on the same channel is a receiver that never acknowledges, so a
deploy beside it ends `DEPLOY_SWITCH_INCOMPLETE`. Under a gate slot (`GIP_GATE_SLOT`) the stack
prefix therefore carries the slot's name, so two slots, and a slot and a plain process, do not
share a channel. **Written red first.**

The Redis tests exercise the deployment switch: they run only with no gate or other switch test
running and `PUBSUB NUMSUB gip:switch:*` at 0 (the rule of 2026-10-21 21:13:34 BST, FD-1838).
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.config import Settings
from app.platform.deployment_switch import (
    LiveRefs,
    RedisSwitch,
    SwitchMember,
    SwitchMessage,
    SwitchSubscription,
    build_switch_client,
    prepare_round,
    switch_stack,
)

_PLAIN = "local:local"


def _synthetic_slot() -> str:
    """A slot name no real gate holds (FD-8199).

    Redis channels are server-wide, so a test that names a REAL slot (`/tmp/slots/gate-1`)
    shares its channel with whichever paired gate holds that slot, and that gate's subscriber
    is counted in the PREPARE quorum. A per-run name cannot collide with one.
    """
    return f"/tmp/slots/test-{uuid4().hex[:8]}"


def test_without_a_gate_slot_the_stack_is_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GIP_GATE_SLOT", raising=False)
    assert switch_stack("local", "local") == _PLAIN


def test_two_gate_slots_get_two_stacks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIP_GATE_SLOT", _synthetic_slot())
    first = switch_stack("local", "local")
    monkeypatch.setenv("GIP_GATE_SLOT", _synthetic_slot())
    second = switch_stack("local", "local")
    assert first != second
    assert _PLAIN not in {first, second}


@pytest.mark.parametrize("foreign_is_another_slot", [False, True], ids=["plain", "other-slot"])
async def test_a_subscriber_on_the_unsuffixed_channel_is_not_counted_in_the_quorum(
    monkeypatch: pytest.MonkeyPatch, foreign_is_another_slot: bool
) -> None:
    """A foreign subscriber (another slot's, or a plain process's) never acknowledges here.

    `other-slot` stands in for a paired gate holding a real slot (FD-8199): its subscriber is
    on a channel server-wide visible to this run, and the run must still count only its own.
    """
    monkeypatch.setenv("GIP_GATE_SLOT", _synthetic_slot())
    client = build_switch_client(Settings().redis_url.get_secret_value())
    foreign = client.pubsub()
    if foreign_is_another_slot:
        with monkeypatch.context() as other:
            other.setenv("GIP_GATE_SLOT", _synthetic_slot())
            channel = f"gip:switch:{switch_stack('local', 'local')}:dev"
    else:
        channel = f"gip:switch:{_PLAIN}:dev"
    await foreign.subscribe(channel)
    switch = RedisSwitch(client, switch_stack("local", "local"))

    async def hydrated(_: SwitchMessage) -> None:
        return None

    subscription = SwitchSubscription(
        switch, client, SwitchMember("slot-process", LiveRefs(), hydrated), ("dev",)
    )
    await subscription.start()
    try:
        message = SwitchMessage(
            switch_id=str(uuid4()),
            phase="prepare",
            workspace_id=uuid4(),
            environment="dev",
            deployment_id=uuid4(),
            rating_version_ref="rating_version:motor@1",
            bundle_hash="a" * 64,
        )
        outcome = await prepare_round(switch.for_environment("dev"), message, timeout=3.0)
        assert outcome.receivers == 1
        assert outcome.prepared == frozenset({"slot-process"})
    finally:
        await subscription.stop()
        await foreign.aclose()  # type: ignore[no-untyped-call]
        await client.aclose()
