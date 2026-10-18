"""The two-phase deployment switch and the per-process `live` reference (FR-268, FR-269).

WK-674 Slice 5, `PL-1766` D5.6/D5.8/D5.9, under the maintainer's rulings of "2026-10-18 22:59:56
BST" (DP-3 (b), DB-first) and "2026-10-18 23:03:15 BST" ((A): a per-process `live` reference
with a startup load).

**The order, DB first.** (1) PREPARE: every subscribed process hydrates the new bundle off the
request path and acknowledges; nothing is swapped. A short round raises `SwitchIncompleteError`
naming the processes that did not acknowledge, and the deploy writes no row. (2) The deploy
transaction commits (the Deployment row, `deployment.created` whose after-state carries the
PREPARE set). (3) COMMIT: each prepared process swaps its one `live` reference and
acknowledges. (4) `deployment.switched`, in its own transaction, records who did and who did
not. There is **no revert**: the DB never rolls back after a switch, so the record is never
behind what a process serves.

**What is given up.** `/score` used to read the latest committed Deployment on every request
(`api/score.py`), so convergence was immediate. A process that is alive but missed COMMIT now
serves the previous version until it restarts (and loads the latest committed Deployment). The
event and the response name it; the remedy is FD 8129 (MEDIUM, WK-674, before the 12 Nov exit
demo), not built here.

**Who is expected to acknowledge.** The processes that received the PREPARE message
(`SwitchTransport.publish` returns the receiver count). Their names come from a roster each
process joins at subscribe and leaves at clean shutdown. A process that crashed leaves a stale
roster entry: when every receiver acknowledged, the extra roster names are pruned; when the
round is short, they are reported (a stale name may be among them) and nothing is pruned.
There is no heartbeat and no lease.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
import socket
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import asdict, dataclass
from typing import Literal, Protocol, cast
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DeploymentRow, EnvironmentRow

__all__ = [
    "COMMIT_TIMEOUT_SECONDS",
    "PREPARE_TIMEOUT_SECONDS",
    "CommitOutcome",
    "LiveEntry",
    "LiveRefs",
    "PrepareOutcome",
    "RedisSwitchTransport",
    "SwitchIncompleteError",
    "SwitchMember",
    "SwitchMessage",
    "SwitchSubscription",
    "SwitchTransport",
    "build_switch_client",
    "commit_round",
    "prepare_round",
    "process_id",
]

_log = logging.getLogger(__name__)


def _awaited[T](call: Awaitable[T] | T) -> Awaitable[T]:
    """redis-py types its set and pub/sub commands as `Awaitable[T] | T` (one stub for the sync
    and async clients); on the asyncio client every one of them is awaitable."""
    return cast("Awaitable[T]", call)


_STARTED_AT = int(time.time())


def process_id() -> str:
    """The name of this process incarnation in a switch: `<hostname>:<pid>:<start epoch>`.

    The hostname is the container (the replica). The start epoch makes a restarted process a new
    name, so it is never confused with its own ghost in the roster. No secrets, no values.
    """
    return f"{socket.gethostname()}:{os.getpid()}:{_STARTED_AT}"


@dataclass(frozen=True)
class LiveEntry:
    """What one Environment is serving in one process."""

    deployment_id: UUID
    rating_version_ref: str
    bundle_hash: str


class LiveRefs:
    """The per-process `live` reference: (workspace, environment slug) -> `LiveEntry`.

    Read once at request start; written only by a COMMIT this process acknowledged, and loaded
    once at startup from the latest committed Deployment of every Environment. Confined to one
    event loop, like `BundleSlot`: plain dict operations, no lock.
    """

    def __init__(self) -> None:
        self._live: dict[tuple[UUID, str], LiveEntry] = {}

    def get(self, workspace_id: UUID, environment: str) -> LiveEntry | None:
        return self._live.get((workspace_id, environment))

    def set(self, workspace_id: UUID, environment: str, entry: LiveEntry) -> None:
        self._live[(workspace_id, environment)] = entry

    @classmethod
    def from_latest(cls, rows: Iterable[tuple[UUID, str, UUID, str, str]]) -> LiveRefs:
        """(workspace_id, environment, deployment_id, rating_version_ref, bundle_hash) rows."""
        live = cls()
        for workspace_id, environment, deployment_id, ref, bundle_hash in rows:
            live.set(workspace_id, environment, LiveEntry(deployment_id, ref, bundle_hash))
        return live

    async def load_latest(self, session: AsyncSession) -> None:
        """The startup load: the latest committed Deployment of every Environment, into `self`.

        The DB is ahead of or equal to any COMMIT a process has acknowledged (DB first), so
        this never moves a reference backwards.
        """
        result = await session.execute(
            select(
                DeploymentRow.workspace_id,
                EnvironmentRow.slug,
                DeploymentRow.id,
                DeploymentRow.rating_version_ref,
                DeploymentRow.bundle_hash,
            )
            .join(EnvironmentRow, EnvironmentRow.id == DeploymentRow.environment_id)
            .distinct(DeploymentRow.environment_id)
            .order_by(
                DeploymentRow.environment_id,
                DeploymentRow.deployed_at.desc(),
                DeploymentRow.id.desc(),
            )
        )
        for workspace_id, environment, deployment_id, ref, bundle_hash in result.all():
            self.set(workspace_id, environment, LiveEntry(deployment_id, ref, bundle_hash))


@dataclass(frozen=True)
class SwitchMessage:
    switch_id: str
    phase: Literal["prepare", "commit"]
    workspace_id: UUID
    environment: str
    deployment_id: UUID
    rating_version_ref: str
    bundle_hash: str

    def to_json(self) -> str:
        return json.dumps(
            {
                **asdict(self),
                "workspace_id": str(self.workspace_id),
                "deployment_id": str(self.deployment_id),
            }
        )

    @classmethod
    def from_json(cls, raw: str | bytes) -> SwitchMessage:
        data = json.loads(raw)
        return cls(
            **{
                **data,
                "workspace_id": UUID(data["workspace_id"]),
                "deployment_id": UUID(data["deployment_id"]),
            }
        )

    def entry(self) -> LiveEntry:
        return LiveEntry(self.deployment_id, self.rating_version_ref, self.bundle_hash)


class SwitchTransport(Protocol):
    """How the coordinator reaches the processes. Redis in the product, a bus in the tests."""

    async def publish(self, message: SwitchMessage) -> int:
        """Send to every subscribed process; return how many received it."""
        ...

    async def acks(self, switch_id: str, phase: str, want: int, timeout: float) -> set[str]:
        """The process ids that acknowledged `phase`, waiting up to `timeout` for `want`."""
        ...

    async def roster(self) -> set[str]: ...

    async def drop_from_roster(self, ids: set[str]) -> None: ...


class SwitchIncompleteError(Exception):
    """PREPARE was short. Nothing was swapped; `unacknowledged` names who did not answer."""

    def __init__(
        self, *, acknowledged: Iterable[str], unacknowledged: Iterable[str], receivers: int
    ) -> None:
        self.acknowledged = frozenset(acknowledged)
        self.unacknowledged = frozenset(unacknowledged)
        self.receivers = receivers
        super().__init__(
            f"{len(self.acknowledged)} of {receivers} subscribed processes acknowledged PREPARE; "
            f"possibly stale (unacknowledged; a ghost of a crashed process may be among them): "
            f"{sorted(self.unacknowledged)}"
        )


@dataclass(frozen=True)
class PrepareOutcome:
    """A full PREPARE: who acknowledged, how many received it, and which roster names were
    ghosts of crashed processes and were pruned (`pruned_stale`, the maintainer's
    "2026-10-18 23:07:57 BST" ruling)."""

    prepared: frozenset[str]
    receivers: int
    pruned_stale: frozenset[str]


@dataclass(frozen=True)
class CommitOutcome:
    committed: frozenset[str]
    unacknowledged: frozenset[str]


async def prepare_round(
    transport: SwitchTransport, message: SwitchMessage, *, timeout: float
) -> PrepareOutcome:
    """PREPARE: the processes that hydrated the bundle and acknowledged.

    The expected count is `publish`'s receiver count; names come from the roster. Every
    receiver acknowledged: the other roster names are ghosts, pruned and reported
    `pruned_stale`. Short: `SwitchIncompleteError`, every unacknowledged roster name reported
    `possibly_stale` and none dropped (a ghost and a live-but-silent process cannot be told
    apart without a heartbeat).

    No receivers is an empty set, not a refusal: a process started later loads the latest
    committed Deployment itself.
    """
    receivers = await transport.publish(message)
    acked = await transport.acks(message.switch_id, "prepare", receivers, timeout)
    roster = await transport.roster()
    if len(acked) >= receivers:
        stale = frozenset(roster - acked)
        if stale:
            await transport.drop_from_roster(set(stale))
        return PrepareOutcome(frozenset(acked), receivers, stale)
    raise SwitchIncompleteError(
        acknowledged=acked, unacknowledged=roster - acked, receivers=receivers
    )


async def commit_round(
    transport: SwitchTransport,
    message: SwitchMessage,
    prepared: frozenset[str],
    *,
    timeout: float,
) -> CommitOutcome:
    """COMMIT: ask the prepared processes to swap; report who did and who did not."""
    await transport.publish(message)
    acked = await transport.acks(message.switch_id, "commit", len(prepared), timeout)
    return CommitOutcome(
        committed=frozenset(acked & prepared), unacknowledged=prepared - frozenset(acked)
    )


class SwitchMember:
    """One process's side: hydrate on PREPARE, swap on COMMIT, acknowledge only what it did."""

    _PENDING_BOUND = 8

    def __init__(
        self,
        process: str,
        live: LiveRefs,
        hydrate: Callable[[SwitchMessage], Awaitable[None]],
    ) -> None:
        self.process = process
        self.live = live
        self._hydrate = hydrate
        self._pending: OrderedDict[str, SwitchMessage] = OrderedDict()

    async def handle(self, message: SwitchMessage) -> bool:
        """True when this process should acknowledge `message`'s phase."""
        if message.phase == "prepare":
            try:
                await self._hydrate(message)
            except Exception:
                _log.exception(
                    "PREPARE %s: hydration failed in %s", message.switch_id, self.process
                )
                return False
            self._pending[message.switch_id] = message
            while len(self._pending) > self._PENDING_BOUND:
                self._pending.popitem(last=False)
            return True
        prepared = self._pending.pop(message.switch_id, None)
        if prepared is None:
            return False
        self.live.set(prepared.workspace_id, prepared.environment, prepared.entry())
        return True


#: How long a round waits for its acknowledgements. Fixed, not configuration: a PREPARE that
#: needs longer than this is a process that cannot hydrate in the time NFR-494 allows.
PREPARE_TIMEOUT_SECONDS = 10.0
COMMIT_TIMEOUT_SECONDS = 10.0
_ACK_POLL_SECONDS = 0.02
_ACK_TTL_SECONDS = 120


def build_switch_client(url: str) -> Redis:
    """The switch's own Redis client: not the rate limiter's.

    `rate_limit.build_redis_client` sets a 50 ms socket timeout so a hung Redis costs a request
    little (RL-1347 rule 5). A subscription blocks reading its channel for as long as nothing is
    published, so on that client it would raise a timeout every 50 ms and stop listening; found
    the first time it ran against Redis. This one connects within 5 s and reads without a limit,
    and pings an idle connection every 30 s.
    """
    client: Redis = Redis.from_url(url, socket_connect_timeout=5, health_check_interval=30)
    return client


class RedisSwitchTransport:
    """The switch channel on Redis: a pub/sub channel, a roster set, one ack set per round.

    Namespaced per platform environment and tenant (`<environment>:<tenant>`), so two stacks on
    one Redis never hear each other. Acks
    are polled while a round waits; that is the coordinator's own wait, not a process
    heartbeat.
    """

    def __init__(self, client: Redis, namespace: str) -> None:
        self._client = client
        self.channel = f"gip:switch:{namespace}"
        self._roster_key = f"gip:switch:{namespace}:roster"
        self._namespace = namespace

    def _ack_key(self, switch_id: str, phase: str) -> str:
        return f"gip:switch:{self._namespace}:acks:{switch_id}:{phase}"

    async def publish(self, message: SwitchMessage) -> int:
        return int(await _awaited(self._client.publish(self.channel, message.to_json())))

    async def acks(self, switch_id: str, phase: str, want: int, timeout: float) -> set[str]:
        key = self._ack_key(switch_id, phase)
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while True:
            got = {
                m.decode() if isinstance(m, bytes) else str(m)
                for m in await _awaited(self._client.smembers(key))
            }
            if len(got) >= want or loop.time() >= deadline:
                return got
            await asyncio.sleep(_ACK_POLL_SECONDS)

    async def roster(self) -> set[str]:
        return {
            m.decode() if isinstance(m, bytes) else str(m)
            for m in await _awaited(self._client.smembers(self._roster_key))
        }

    async def drop_from_roster(self, ids: set[str]) -> None:
        if ids:
            await _awaited(self._client.srem(self._roster_key, *ids))

    async def acknowledge(self, switch_id: str, phase: str, process: str) -> None:
        key = self._ack_key(switch_id, phase)
        await _awaited(self._client.sadd(key, process))
        await _awaited(self._client.expire(key, _ACK_TTL_SECONDS))

    async def join(self, process: str) -> None:
        await _awaited(self._client.sadd(self._roster_key, process))

    async def leave(self, process: str) -> None:
        await _awaited(self._client.srem(self._roster_key, process))


class SwitchSubscription:
    """A process's subscription: listens on the channel and answers for its `SwitchMember`.

    `start` returns only once the channel's SUBSCRIBE is confirmed and the process is on the
    roster, so a PREPARE published after `start` returns is received (and counted) here.
    """

    def __init__(
        self, transport: RedisSwitchTransport, client: Redis, member: SwitchMember
    ) -> None:
        self._transport = transport
        self._client = client
        self._member = member
        self._pubsub = client.pubsub()
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        await self._pubsub.subscribe(self._transport.channel)
        confirmed = await self._pubsub.get_message(ignore_subscribe_messages=False, timeout=5.0)
        if confirmed is None or confirmed.get("type") != "subscribe":
            raise RuntimeError(f"the switch channel {self._transport.channel} was not confirmed")
        await self._transport.join(self._member.process)
        self._task = asyncio.create_task(self._listen(), name="deployment-switch-subscriber")

    async def _listen(self) -> None:
        async for raw in self._pubsub.listen():
            if raw.get("type") != "message":
                continue
            try:
                message = SwitchMessage.from_json(raw["data"])
                if await self._member.handle(message):
                    await self._transport.acknowledge(
                        message.switch_id, message.phase, self._member.process
                    )
            except Exception:
                _log.exception("deployment switch message not handled")

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        with contextlib.suppress(Exception):
            await self._transport.leave(self._member.process)
        await self._pubsub.aclose()  # type: ignore[no-untyped-call]
