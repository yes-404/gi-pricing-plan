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

**What is given up, and how it converges.** `/score` used to read the latest committed
Deployment on every request (`api/score.py`), so convergence was immediate. A process that is
alive but missed COMMIT serves the previous version until the next **reconcile pass** (SL-1992,
FD-1823): `SwitchReconciler` reloads the latest committed Deployment of every Environment each
`Settings.deployment_reconcile_seconds` (B, at most NFR-494's 30 s) and at once when the
subscription reconnects, subscribes to an Environment created after start, and restarts a dead
listener. The event and the response still name such a process `possibly_stale`: a ghost and a
process that missed COMMIT cannot be told apart without a heartbeat.

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
from typing import Any, Literal, Protocol, cast
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DeploymentRow, EnvironmentRow

__all__ = [
    "COMMIT_TIMEOUT_SECONDS",
    "PREPARE_TIMEOUT_SECONDS",
    "CommitOutcome",
    "LatestState",
    "LiveEntry",
    "LiveRefs",
    "PrepareOutcome",
    "RedisSwitch",
    "RedisSwitchTransport",
    "SwitchIncompleteError",
    "SwitchMember",
    "SwitchMessage",
    "SwitchReconciler",
    "SwitchRegistry",
    "SwitchSubscription",
    "SwitchTransport",
    "build_switch_client",
    "commit_round",
    "prepare_round",
    "process_id",
    "read_latest",
    "switch_stack",
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


#: (workspace_id, environment, deployment_id, rating_version_ref, bundle_hash)
type DeploymentRowTuple = tuple[UUID, str, UUID, str, str]


@dataclass(frozen=True)
class LatestState:
    """What one DB read says: the unretired Environment slugs and each one's latest Deployment."""

    environments: tuple[str, ...]
    deployments: tuple[DeploymentRowTuple, ...]


type LatestReader = Callable[[], Awaitable[LatestState]]


async def _latest_deployments(session: AsyncSession) -> tuple[DeploymentRowTuple, ...]:
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
    return tuple((w, e, d, r, h) for w, e, d, r, h in result.all())


async def read_latest(session: AsyncSession) -> LatestState:
    """The unretired Environments and the latest committed Deployment of every Environment."""
    slugs = (
        await session.execute(
            select(EnvironmentRow.slug).where(EnvironmentRow.retired_at.is_(None))
        )
    ).scalars()
    return LatestState(tuple(slugs), await _latest_deployments(session))


class LiveRefs:
    """The per-process `live` reference: (workspace, environment slug) -> `LiveEntry`.

    Read once at request start. Written by a COMMIT this process acknowledged, and by a reconcile
    pass from the latest committed Deployment of every Environment (the startup load is the first
    such pass). Confined to one event loop, like `BundleSlot`: plain dict operations, no lock.
    """

    def __init__(self) -> None:
        self._live: dict[tuple[UUID, str], LiveEntry] = {}
        self._writes: dict[tuple[UUID, str], int] = {}

    def get(self, workspace_id: UUID, environment: str) -> LiveEntry | None:
        return self._live.get((workspace_id, environment))

    def set(self, workspace_id: UUID, environment: str, entry: LiveEntry) -> None:
        key = (workspace_id, environment)
        self._live[key] = entry
        self._writes[key] = self._writes.get(key, 0) + 1

    @classmethod
    def from_latest(cls, rows: Iterable[DeploymentRowTuple]) -> LiveRefs:
        """(workspace_id, environment, deployment_id, rating_version_ref, bundle_hash) rows."""
        live = cls()
        for workspace_id, environment, deployment_id, ref, bundle_hash in rows:
            live.set(workspace_id, environment, LiveEntry(deployment_id, ref, bundle_hash))
        return live

    async def reconcile(self, read: LatestReader) -> LatestState:
        """One pass: set every Environment's entry to its latest committed Deployment.

        **Never backwards.** The DB is ahead of or equal to any COMMIT this process acknowledged
        (DB first), but a read that began before a COMMIT can return the Deployment that COMMIT
        replaced. An entry written (by a COMMIT) while the read was in flight is therefore left
        alone: it is at least as new as anything the read can hold. That is the order
        `(deployed_at, id)` gives, decided by what was written rather than by comparing stamps
        the COMMIT message does not carry.
        """
        since = dict(self._writes)
        state = await read()
        for workspace_id, environment, deployment_id, ref, bundle_hash in state.deployments:
            key = (workspace_id, environment)
            if self._writes.get(key, 0) == since.get(key, 0):
                self.set(workspace_id, environment, LiveEntry(deployment_id, ref, bundle_hash))
        return state

    async def load_latest(self, session: AsyncSession) -> None:
        """The startup load, the first reconcile pass: the latest committed Deployment of every
        Environment, into `self`. Never moves a reference backwards (`reconcile`)."""

        async def read() -> LatestState:
            return LatestState((), await _latest_deployments(session))

        await self.reconcile(read)


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

    One transport is one platform Environment's (`dev`, `uat`, `prod`, ...) switch, namespaced
    `<GIP_ENVIRONMENT>:<tenant>:<environment slug>` (the maintainer's "2026-10-18" answer on
    scope, relayed by the lead): the stack prefix keeps two stacks on one Redis apart, and the
    slug keeps a `uat` deploy from reaching a process that serves only `prod`. Acks are polled
    while a round waits; that is the coordinator's own wait, not a process heartbeat.
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


class SwitchRegistry(Protocol):
    """The switch for every Environment: what the deploy service is given."""

    def for_environment(self, environment: str) -> SwitchTransport: ...


def switch_stack(environment: str, tenant_id: str) -> str:
    """The stack prefix of this process's switch channels: `<GIP_ENVIRONMENT>:<tenant>`.

    Under a gate slot (`GIP_GATE_SLOT`, the slot's flock path) the slot's name is appended
    (FD-1838): PUBLISH's receiver count is the PREPARE quorum and counts subscribers on the
    whole Redis server whatever the db, so two slots sharing a channel would each count the
    other as a receiver that never acknowledges. Production sets no slot and is unchanged.
    """
    stack = f"{environment}:{tenant_id}"
    slot = os.environ.get("GIP_GATE_SLOT")
    return f"{stack}:{os.path.basename(slot)}" if slot else stack


class RedisSwitch:
    """The Redis switch of one stack: a `RedisSwitchTransport` per Environment slug."""

    def __init__(self, client: Redis, stack: str) -> None:
        self._client = client
        self._stack = stack

    def for_environment(self, environment: str) -> RedisSwitchTransport:
        return RedisSwitchTransport(self._client, f"{self._stack}:{environment}")


class SwitchSubscription:
    """A process's subscriptions, one channel per Environment it serves, answering for its
    `SwitchMember`.

    `start` returns only once every channel's SUBSCRIBE is confirmed and the process is on every
    roster, so a PREPARE published after `start` returns is received (and counted) here. A
    process serving several Environments appears in each roster.

    `ensure` is what a reconcile pass asks of it (SL-1992, FD-1823): subscribe and join an
    Environment created since the last pass, and, if the listener task has ended (its connection
    retries ran out), start it again and re-subscribe and re-join every channel. A Redis
    reconnect re-subscribes by itself and tells nobody (redis-py's `PubSub.on_connect`); this
    class sets `reconnected` then, so a reconcile pass runs at once rather than at the next tick.
    """

    _CONFIRM_SECONDS = 5.0

    def __init__(
        self,
        switch: RedisSwitch,
        client: Redis,
        member: SwitchMember,
        environments: Iterable[str],
        *,
        reconnected: asyncio.Event | None = None,
    ) -> None:
        self._switch = switch
        self._member = member
        self._environments = tuple(environments)
        self._transports: dict[str, RedisSwitchTransport] = {}
        self._pubsub = client.pubsub()
        self._task: asyncio.Task[None] | None = None
        self._confirmed: dict[str, asyncio.Event] = {}
        self._reconnected = reconnected

    async def start(self) -> None:
        await self.ensure(self._environments)

    async def ensure(self, environments: Iterable[str]) -> None:
        """Be subscribed and on the roster for every Environment named, with a live listener."""
        listener = self._task
        dead = listener is not None and listener.done()
        if listener is not None and dead:
            ended = None if listener.cancelled() else listener.exception()
            _log.error("the deployment switch listener ended; subscribing again", exc_info=ended)
        added = {
            env: self._switch.for_environment(env)
            for env in environments
            if env not in self._transports
        }
        wanted = {**self._transports, **added} if dead else added
        if not wanted:
            return
        self._transports.update(added)
        self._confirmed = {t.channel: asyncio.Event() for t in wanted.values()}
        await self._pubsub.subscribe(*self._confirmed)
        if self._reconnected is not None:
            # redis-py annotates `PubSub.connection` as `None`; it is the live connection once
            # subscribed. The callback is held weakly, so it must be this bound method.
            connection = cast("Any", self._pubsub).connection
            connection.register_connect_callback(self._on_connect)
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._listen(), name="deployment-switch-subscriber")
        channels = list(self._confirmed)
        try:
            async with asyncio.timeout(self._CONFIRM_SECONDS):
                for event in self._confirmed.values():
                    await event.wait()
        except TimeoutError:
            raise RuntimeError(f"the switch channels {channels} were not confirmed") from None
        for transport in wanted.values():
            await transport.join(self._member.process)

    def _on_connect(self, _: object) -> None:
        if self._reconnected is not None:
            self._reconnected.set()

    async def _listen(self) -> None:
        async for raw in self._pubsub.listen():
            kind = raw.get("type")
            if kind == "subscribe":
                channel = raw["channel"]
                event = self._confirmed.get(
                    channel.decode() if isinstance(channel, bytes) else str(channel)
                )
                if event is not None:
                    event.set()
                continue
            if kind != "message":
                continue
            try:
                message = SwitchMessage.from_json(raw["data"])
                transport = self._transports.get(message.environment)
                if transport is not None and await self._member.handle(message):
                    await transport.acknowledge(
                        message.switch_id, message.phase, self._member.process
                    )
            except Exception:
                _log.exception("deployment switch message not handled")

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        for transport in self._transports.values():
            with contextlib.suppress(Exception):
                await transport.leave(self._member.process)
        await self._pubsub.aclose()  # type: ignore[no-untyped-call]


class SwitchReconciler:
    """The periodic reconcile (SL-1992, FD-1823): the DB is the truth a missed message is
    repaired from.

    Each pass reads the latest committed Deployment of every Environment and the unretired
    Environments' slugs, asks `ensure` to subscribe to any it is not yet on, and then lets
    `LiveRefs.reconcile` fix `live`. A pass runs every `interval` seconds and whenever `wake`
    is set (a Redis reconnect). A pass that raises is logged and the loop goes on. Worst case a
    missed COMMIT converges in `interval`; an Environment created between a pass's read and its
    `ensure` is picked up by the next pass, so discovery takes at most twice that.
    """

    def __init__(
        self,
        live: LiveRefs,
        read: LatestReader,
        ensure: Callable[[Iterable[str]], Awaitable[None]],
        *,
        interval: float,
        wake: asyncio.Event | None = None,
    ) -> None:
        self._live = live
        self._read = read
        self._ensure = ensure
        self._interval = interval
        self._wake = wake if wake is not None else asyncio.Event()
        self.task: asyncio.Task[None] | None = None

    async def run_once(self) -> None:
        async def read_then_ensure() -> LatestState:
            state = await self._read()
            await self._ensure(state.environments)
            return state

        await self._live.reconcile(read_then_ensure)

    def start(self) -> None:
        self.task = asyncio.create_task(self._run(), name="deployment-switch-reconciler")

    async def _run(self) -> None:
        while True:
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(self._wake.wait(), self._interval)
            self._wake.clear()
            try:
                await self.run_once()
            except Exception:
                _log.exception("deployment switch reconcile pass failed")

    async def stop(self) -> None:
        if self.task is not None:
            self.task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.task
