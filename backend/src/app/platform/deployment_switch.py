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

import json
import logging
import os
import socket
from collections import OrderedDict
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import asdict, dataclass
from typing import Literal, Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DeploymentRow, EnvironmentRow

__all__ = [
    "CommitOutcome",
    "LiveEntry",
    "LiveRefs",
    "SwitchIncompleteError",
    "SwitchMember",
    "SwitchMessage",
    "SwitchTransport",
    "commit_round",
    "prepare_round",
    "process_id",
]

_log = logging.getLogger(__name__)


def process_id() -> str:
    """The name of this process in a switch: its container (the replica) and its pid."""
    return f"{socket.gethostname()}:{os.getpid()}"


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

    @classmethod
    async def load_latest(cls, session: AsyncSession) -> LiveRefs:
        """The startup load: the latest committed Deployment of every Environment."""
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
        return cls.from_latest((r[0], r[1], r[2], r[3], r[4]) for r in result.all())


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
            f"unacknowledged (a stale roster name may be among them): "
            f"{sorted(self.unacknowledged)}"
        )


@dataclass(frozen=True)
class CommitOutcome:
    committed: frozenset[str]
    unacknowledged: frozenset[str]


async def prepare_round(
    transport: SwitchTransport, message: SwitchMessage, *, timeout: float
) -> frozenset[str]:
    """PREPARE: the set of processes that hydrated the bundle and acknowledged.

    No receivers is an empty set, not a refusal: a process started later loads the latest
    committed Deployment itself.
    """
    receivers = await transport.publish(message)
    acked = await transport.acks(message.switch_id, "prepare", receivers, timeout)
    roster = await transport.roster()
    if len(acked) >= receivers:
        if stale := roster - acked:
            await transport.drop_from_roster(stale)
        return frozenset(acked)
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
