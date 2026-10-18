"""The deploy route's DB-first switch over HTTP (WK-674 Slice 5; FR-268, FR-269, FR-272).

`PL-1766` D5.6, D5.8, D5.9 and D5.10, under the maintainer's rulings of "2026-10-18 22:59:56 BST"
(DB first), "23:03:15 BST" ((A): a per-process `live` reference with a startup load) and
"23:07:57 BST" (the expected-process rule). **Written red first**: these were run on the commit
before the wiring and failed for their own reason, then run at head (`LG-8127`).

Needs the database and the Redis the lifespan subscribes to: it runs only in a window that is
granted. The app's own process is one subscriber; a `_Peer` is another, on its own event loop in
its own thread, standing in for a second replica. Bundle hydration is replaced by a no-op because
the seeded Rating Versions carry a hash and no blob (the PREPARE-hydration check itself is
`hydrate_for_switch`'s, covered where a compiled bundle exists).
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Awaitable, Callable, Iterator
from typing import Any
from uuid import UUID

import pytest
from backend.tests import test_deployments as _deployments
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api import score as score_module
from app.config import Settings
from app.db.models import AuditEventRow, DeploymentRow
from app.main import create_app
from app.platform.deployment_switch import (
    LiveRefs,
    RedisSwitch,
    SwitchMember,
    SwitchMessage,
    SwitchSubscription,
    build_switch_client,
)

# The Slice 2 deployment tests' fixtures and helpers, shared rather than copied.
api_settings = _deployments.api_settings
seat = _deployments.seat
approved_version = _deployments.approved_version
deploy = _deployments.deploy


@pytest.fixture(autouse=True)
def _no_bundle_blob(monkeypatch: pytest.MonkeyPatch) -> None:
    async def hydrated(*_: Any, **__: Any) -> None:
        return None

    monkeypatch.setattr(score_module, "hydrate_for_switch", hydrated, raising=False)


@pytest.fixture
def client(api_settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


class _DeafToCommit(SwitchMember):
    """Acknowledges PREPARE and never COMMIT: alive, subscribed, and still on the old version."""

    async def handle(self, message: SwitchMessage) -> bool:
        return False if message.phase == "commit" else await super().handle(message)


class _Peer:
    """A second subscribed process, on its own event loop in its own thread."""

    def __init__(
        self,
        settings: Settings,
        process: str,
        hydrate: Callable[[SwitchMessage], Awaitable[None]],
        *,
        deaf_to_commit: bool = False,
        environments: tuple[str, ...] = ("dev", "uat", "prod"),
    ) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()
        self._client = build_switch_client(settings.redis_url.get_secret_value())
        switch = RedisSwitch(self._client, f"{settings.environment.value}:{settings.tenant_id}")
        kind = _DeafToCommit if deaf_to_commit else SwitchMember
        self.process = process
        self._subscription = SwitchSubscription(
            switch, self._client, kind(process, LiveRefs(), hydrate), environments
        )
        asyncio.run_coroutine_threadsafe(self._subscription.start(), self._loop).result(10)

    def stop(self) -> None:
        asyncio.run_coroutine_threadsafe(self._subscription.stop(), self._loop).result(10)
        asyncio.run_coroutine_threadsafe(self._client.aclose(), self._loop).result(10)
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(5)


async def _hydrates(_: SwitchMessage) -> None:
    return None


async def _cannot_hydrate(_: SwitchMessage) -> None:
    raise RuntimeError("bundle blob unreadable")


async def _events(database: Any, workspace_id: UUID, action: str) -> list[AuditEventRow]:
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(AuditEventRow)
                    .where(
                        AuditEventRow.workspace_id == workspace_id, AuditEventRow.action == action
                    )
                    .order_by(AuditEventRow.at)
                )
            )
            .scalars()
            .all()
        )


@pytest.mark.req("FR-268")
@pytest.mark.asyncio
async def test_a_short_prepare_writes_no_row_no_event_and_names_the_process(
    client: TestClient, api_settings: Settings, database: Any, workspace_id: UUID, seat: Any
) -> None:
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, deployer.id)
    peer = _Peer(api_settings, "ghost-host:9:1", _cannot_hydrate)
    try:
        refused = deploy(client, deployer, "dev", ref)
    finally:
        peer.stop()
    assert refused.status_code == 503, refused.text
    assert refused.json()["code"] == "DEPLOY_SWITCH_INCOMPLETE"
    assert "ghost-host:9:1" in refused.json()["detail"]
    async with database.session() as session:
        rows = (
            await session.execute(
                select(DeploymentRow.id).where(DeploymentRow.workspace_id == workspace_id)
            )
        ).all()
    assert rows == []
    assert await _events(database, workspace_id, "deployment.created") == []
    assert await _events(database, workspace_id, "deployment.switched") == []


@pytest.mark.req("FR-268")
@pytest.mark.asyncio
async def test_a_partial_commit_names_the_unacknowledged_process_possibly_stale(
    client: TestClient, api_settings: Settings, database: Any, workspace_id: UUID, seat: Any
) -> None:
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, deployer.id)
    peer = _Peer(api_settings, "deaf-host:8:1", _hydrates, deaf_to_commit=True)
    try:
        done = deploy(client, deployer, "dev", ref)
    finally:
        peer.stop()
    assert done.status_code == 201, done.text
    switch = done.json()["switch"]
    assert switch["receivers"] == 2
    assert switch["processes"]["deaf-host:8:1"] == "possibly_stale"
    committed = [p for p, s in switch["processes"].items() if s == "committed"]
    assert len(committed) == 1
    created = await _events(database, workspace_id, "deployment.created")
    assert sorted(created[0].after["prepared"]) == sorted(switch["processes"])
    switched = await _events(database, workspace_id, "deployment.switched")
    assert [e.after["processes"] for e in switched] == [switch["processes"]]
    assert switched[0].after["deployment_ref"] == done.json()["id"]
    assert switched[0].entity_ref == "environment:dev"
    assert not switched[0].before


@pytest.mark.req("FR-268")
@pytest.mark.asyncio
async def test_a_fresh_app_serves_the_latest_committed_deployment(
    client: TestClient, api_settings: Settings, database: Any, workspace_id: UUID, seat: Any
) -> None:
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, deployer.id)
    done = deploy(client, deployer, "dev", ref)
    assert done.status_code == 201, done.text
    with TestClient(create_app(api_settings)) as fresh:
        entry = fresh.app.state.live_refs.get(workspace_id, "dev")  # type: ignore[attr-defined]
    assert entry is not None
    assert str(entry.deployment_id) == done.json()["id"]
    assert entry.rating_version_ref == ref


@pytest.mark.req("FR-269")
@pytest.mark.req("FR-272", "NFR-498")
@pytest.mark.asyncio
async def test_a_rollback_emits_rolled_back_then_switched_and_swaps_live(
    client: TestClient, database: Any, workspace_id: UUID, seat: Any
) -> None:
    deployer = await seat("deployer")
    first = await approved_version(database, workspace_id, deployer.id)
    second = await approved_version(database, workspace_id, deployer.id)
    assert deploy(client, deployer, "dev", first).status_code == 201
    assert deploy(client, deployer, "dev", second).status_code == 201
    back = client.post(
        "/api/v1/environments/dev/deployments/rollback",
        json={"rating_version_ref": first, "reason": "regression"},
        headers=deployer.headers,
    )
    assert back.status_code == 201, back.text
    rolled = await _events(database, workspace_id, "deployment.rolled_back")
    assert len(rolled) == 1
    assert rolled[0].after["id"] == back.json()["id"]
    assert rolled[0].before["rating_version_ref"] == second
    switched = await _events(database, workspace_id, "deployment.switched")
    assert [e.after["deployment_ref"] for e in switched][-1] == back.json()["id"]
    live = client.app.state.live_refs.get(workspace_id, "dev")  # type: ignore[attr-defined]
    assert live.rating_version_ref == first
    never = client.post(
        "/api/v1/environments/uat/deployments/rollback",
        json={"rating_version_ref": first, "reason": "never went there"},
        headers=deployer.headers,
    )
    assert never.status_code == 409, never.text


@pytest.mark.req("FR-268")
@pytest.mark.asyncio
async def test_a_deploy_is_not_acknowledged_by_a_process_serving_only_another_environment(
    client: TestClient, api_settings: Settings, database: Any, workspace_id: UUID, seat: Any
) -> None:
    """The maintainer's scope answer: one channel and roster per platform Environment. A
    `prod`-only subscriber that could not hydrate neither receives a `dev` PREPARE nor blocks it."""
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, deployer.id)
    peer = _Peer(api_settings, "prod-only:7:1", _cannot_hydrate, environments=("prod",))
    try:
        done = deploy(client, deployer, "dev", ref)
    finally:
        peer.stop()
    assert done.status_code == 201, done.text
    switch = done.json()["switch"]
    assert "prod-only:7:1" not in switch["processes"]
    assert switch["receivers"] == 1
