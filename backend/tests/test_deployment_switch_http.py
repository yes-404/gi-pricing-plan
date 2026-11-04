"""The deploy route's DB-first switch over HTTP (WK-674 Slice 5; FR-268, FR-269, FR-272).

`PL-1766` D5.6, D5.8, D5.9 and D5.10, under the maintainer's rulings of "2026-10-18 22:59:56 BST"
(DB first), "23:03:15 BST" ((A): a per-process `live` reference with a startup load) and
"23:07:57 BST" (the expected-process rule). **Written red first**: these were run on the commit
before the wiring and failed for their own reason, then run at head (`LG-1824`).

Needs the database and the Redis the lifespan subscribes to: it runs only in a window that is
granted. The app's own process is one subscriber; a `_Peer` is another, on its own event loop in
its own thread, standing in for a second replica. Bundle hydration is replaced by a no-op because
the seeded Rating Versions carry a hash and no blob (the PREPARE-hydration check itself is
`hydrate_for_switch`'s, covered where a compiled bundle exists).
"""

from __future__ import annotations

import asyncio
import contextlib
import threading
import time
from collections.abc import Awaitable, Callable, Iterator
from contextlib import contextmanager
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
    switch_stack,
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
        switch = RedisSwitch(
            self._client, switch_stack(settings.environment.value, settings.tenant_id)
        )
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


# --- the reconcile (SL-1992, FD-1823; FR-268, FR-269) ------------------------------------------
#
# Written red first. B is `Settings.deployment_reconcile_seconds`; a test sets it through
# `model_copy(update=...)`, which at the base (no such field) is silently ignored, so the base
# runs on its absence of any reconcile and not on a settings error.


@contextmanager
def _app(settings: Settings, seconds: int) -> Iterator[TestClient]:
    """The app inside its lifespan. A failing test body is reported as itself: at the base a
    dropped pub/sub connection also fails the lifespan's shutdown, which would mask it."""
    tuned = settings.model_copy(update={"deployment_reconcile_seconds": seconds})
    app_client = TestClient(create_app(tuned), raise_server_exceptions=False)
    app_client.__enter__()
    try:
        yield app_client
    except BaseException:
        with contextlib.suppress(Exception):
            app_client.__exit__(None, None, None)
        raise
    app_client.__exit__(None, None, None)


class _DeafWhenSet(SwitchMember):
    """The app's own member: `_DeafToCommit`, but deaf only while `deaf` is set."""

    deaf = False

    async def handle(self, message: SwitchMessage) -> bool:
        if self.deaf and message.phase == "commit":
            return False
        return await super().handle(message)


@pytest.fixture
def switchable_app_member(monkeypatch: pytest.MonkeyPatch) -> Iterator[type[_DeafWhenSet]]:
    from app import main as main_module

    monkeypatch.setattr(main_module, "SwitchMember", _DeafWhenSet)
    _DeafWhenSet.deaf = False
    yield _DeafWhenSet
    _DeafWhenSet.deaf = False


@pytest.fixture
def subscriptions(monkeypatch: pytest.MonkeyPatch) -> list[SwitchSubscription]:
    """The app's own `SwitchSubscription`, recorded as the lifespan builds it."""
    from app import main as main_module

    seen: list[SwitchSubscription] = []

    class _Recorded(SwitchSubscription):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            seen.append(self)

    monkeypatch.setattr(main_module, "SwitchSubscription", _Recorded)
    return seen


async def _until(check: Callable[[], Awaitable[bool]], seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if await check():
            return True
        await asyncio.sleep(0.1)
    return await check()


def _live_id(client: TestClient, workspace_id: UUID, env: str) -> str | None:
    entry = client.app.state.live_refs.get(workspace_id, env)  # type: ignore[attr-defined]
    return None if entry is None else str(entry.deployment_id)


async def _two_deploys_the_second_missed(
    client: TestClient,
    switchable: type[_DeafWhenSet],
    api_settings: Settings,
    database: Any,
    workspace_id: UUID,
    seat: Any,
) -> tuple[str, str]:
    """Deploy 1 is acknowledged by the app; deploy 2 commits in the DB and the app misses it."""
    deployer = await seat("deployer")
    first = await approved_version(database, workspace_id, deployer.id)
    second = await approved_version(database, workspace_id, deployer.id)
    one = deploy(client, deployer, "dev", first)
    assert one.status_code == 201, one.text
    assert _live_id(client, workspace_id, "dev") == one.json()["id"]
    switchable.deaf = True
    peer = _Peer(api_settings, "acking-peer:6:1", _hydrates)
    try:
        two = deploy(client, deployer, "dev", second)
    finally:
        peer.stop()
    assert two.status_code == 201, two.text
    stale = [p for p, s in two.json()["switch"]["processes"].items() if s == "possibly_stale"]
    assert len(stale) == 1, two.json()["switch"]
    assert stale[0] != "acking-peer:6:1", two.json()["switch"]
    return one.json()["id"], two.json()["id"]


@pytest.mark.req("FR-268")
@pytest.mark.asyncio
async def test_r1b_a_process_that_missed_a_commit_converges_without_a_restart(
    api_settings: Settings,
    database: Any,
    workspace_id: UUID,
    seat: Any,
    switchable_app_member: type[_DeafWhenSet],
) -> None:
    with _app(api_settings, 1) as client:
        _, newest = await _two_deploys_the_second_missed(
            client, switchable_app_member, api_settings, database, workspace_id, seat
        )

        async def converged() -> bool:
            return _live_id(client, workspace_id, "dev") == newest

        assert await _until(converged, 1 + 5), (
            f"live still names {_live_id(client, workspace_id, 'dev')}, not {newest}"
        )


@pytest.mark.req("FR-268")
@pytest.mark.asyncio
async def test_r1c_a_resubscribe_runs_a_pass_at_once_not_at_the_next_tick(
    api_settings: Settings,
    database: Any,
    workspace_id: UUID,
    seat: Any,
    switchable_app_member: type[_DeafWhenSet],
    subscriptions: list[SwitchSubscription],
) -> None:
    """B is 30 s (the ceiling), so only the reconnect can converge inside the margin. The
    connection is dropped in-process: `CLIENT KILL` acts on the whole Redis server and would drop
    every other slot's subscribers."""
    with _app(api_settings, 30) as client:
        previous, newest = await _two_deploys_the_second_missed(
            client, switchable_app_member, api_settings, database, workspace_id, seat
        )
        assert _live_id(client, workspace_id, "dev") == previous, "B is 30 s: no tick has run"
        (subscription,) = subscriptions
        pubsub = subscription._pubsub
        assert pubsub.connection is not None
        client.portal.call(pubsub.connection.disconnect)  # type: ignore[union-attr]

        async def converged() -> bool:
            return _live_id(client, workspace_id, "dev") == newest

        assert await _until(converged, 5), (
            f"live still names {_live_id(client, workspace_id, 'dev')} after the reconnect"
        )


@pytest.mark.req("FR-268")
@pytest.mark.asyncio
async def test_r2_an_environment_created_after_start_is_discovered(
    api_settings: Settings, database: Any, workspace_id: UUID, seat: Any
) -> None:
    from uuid import uuid4

    from app.platform.deployment_switch import process_id

    admin = await seat("admin")
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, deployer.id)
    slug = f"late-{uuid4().hex[:8]}"
    redis_client = build_switch_client(api_settings.redis_url.get_secret_value())
    roster_of = RedisSwitch(
        redis_client, switch_stack(api_settings.environment.value, api_settings.tenant_id)
    ).for_environment(slug)
    try:
        with _app(api_settings, 1) as client:
            made = client.post(
                "/api/v1/environments",
                json={"slug": slug, "name": slug, "promotion_order": 4},
                headers=admin.headers,
            )
            assert made.status_code == 201, made.text

            async def joined() -> bool:
                return process_id() in await roster_of.roster()

            assert await _until(joined, 1 + 5), "the app's process never joined the new roster"
            done = deploy(client, deployer, slug, ref)
            assert done.status_code == 201, done.text
            assert done.json()["switch"]["processes"][process_id()] == "committed"
            assert _live_id(client, workspace_id, slug) == done.json()["id"]
    finally:
        await roster_of.leave(process_id())
        await redis_client.aclose()


@pytest.mark.req("FR-268")
@pytest.mark.asyncio
async def test_r3c_a_dead_listener_is_restarted_by_the_next_pass(
    api_settings: Settings,
    database: Any,
    workspace_id: UUID,
    seat: Any,
    subscriptions: list[SwitchSubscription],
) -> None:
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, deployer.id)
    with _app(api_settings, 1) as client:
        (subscription,) = subscriptions
        task = subscription._task
        assert task is not None
        assert not task.done()
        client.portal.call(task.cancel)  # type: ignore[union-attr]

        async def listening() -> bool:
            current = subscription._task
            return current is not None and not current.done()

        assert await _until(listening, 1 + 5), "the listener task is still dead"
        done = deploy(client, deployer, "dev", ref)
        assert done.status_code == 201, done.text
        from app.platform.deployment_switch import process_id

        assert done.json()["switch"]["processes"][process_id()] == "committed"
