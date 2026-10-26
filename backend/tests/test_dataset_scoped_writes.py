"""FD-1852 — a Dataset-scoped grant reaches the three writes whose handler checks the Dataset.

`PL-1877` Task 2. `06` FR-345 (dated clause, SL-1878): a permission that can be held on a named
Dataset is checked held-anywhere first (403 `PERMISSION_DENIED`), then on the resource by the
handler (404, then 403 `SCOPE_DENIED`). The three routes were refused at the first step for a
scoped holder, because `requires()` names no resource and `rbac._covers` answers False for a
scoped assignment asked about no resource.

Per route R in {dictionary, rule-set, acknowledge}: in-scope → 2xx, out-of-scope → `SCOPE_DENIED`
(the handler's refusal, not the route's `PERMISSION_DENIED`), workspace-wide holder → 2xx, no
grant and an unknown id → `PERMISSION_DENIED`. `07` FR-452: no 403 is counted, either kind.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from backend.tests.conftest_db import seed_as_owner
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Settings
from app.db.models import RoleAssignmentRow, RoleRow, WorkspaceSettingRow
from app.errors import PlatformError
from app.main import create_app
from app.platform import datasets as dataset_service
from app.platform import rate_limit, validation, workspaces
from app.platform import settings as settings_service
from model_schema import (
    ActorKind,
    Principal,
    RuleOutcome,
    RuleResult,
    ScopeType,
    Severity,
    ValidationLayer,
    ValidationReport,
    new_uuid7,
)

LIMIT_KEY = "platform.default_management_rate_limit_rps"
FIXED_SECOND = 1_800_000_000.0
_DICTIONARY = {"data_dictionary": {"policy_id": {"pii_class": "pseudonymous_key"}}}
_RULE_SET: dict[str, Any] = {"rules": []}
_ACK = {"justification": "Large losses reviewed with the reserving team."}


def _headers(principal_id: UUID, workspace_id: UUID) -> dict[str, str]:
    return {DEV_PRINCIPAL_HEADER: str(principal_id), "Workspace-Id": str(workspace_id)}


def _warn() -> RuleResult:
    return RuleResult(
        rule_id=uuid4(),
        rule_slug="severity-outlier",
        rule_version=1,
        layer=ValidationLayer.ACTUARIAL_SANITY,
        severity=Severity.WARN,
        outcome=RuleOutcome.WARN,
        detail="12 claims above the outlier threshold",
    )


class World:
    """Datasets X and Y, one report each (a `warn` result), and the principals that use them."""

    def __init__(self) -> None:
        self.slug: dict[str, str] = {}
        self.dataset_id: dict[str, UUID] = {}
        self.report: dict[str, tuple[UUID, UUID]] = {}  # name -> (report_id, rule_id)
        self.headers: dict[str, dict[str, str]] = {}
        self.principals: dict[str, Principal] = {}


@pytest_asyncio.fixture
async def world(database, grant, membership, workspace_id, principal) -> World:
    w = World()
    # The workspace-wide holder: both roles, so one principal exercises all three routes.
    await grant("pricing_actuary")
    w.headers["workspace"] = _headers(principal.id, workspace_id)
    for name in ("x", "y"):
        warn = _warn()
        async with database.unit_of_work() as session:
            dataset = await dataset_service.create_dataset(
                session,
                workspace_id=workspace_id,
                actor=principal,
                slug=f"ds-{name}-{new_uuid7().hex[-8:]}",
            )
            version = await dataset_service.new_version(
                session, workspace_id=workspace_id, actor=principal, dataset_id=dataset.id
            )
        started = datetime.now(UTC)
        report = ValidationReport(
            id=uuid4(),
            dataset_version_id=version.id,
            rule_set_id=uuid4(),
            rule_set_version=1,
            started_at=started,
            finished_at=started + timedelta(seconds=1),
            results=(warn,),
        )
        async with database.unit_of_work() as session:
            await validation.store_report(
                session, workspace_id=workspace_id, actor=principal, report=report
            )
        w.slug[name] = dataset.slug
        w.dataset_id[name] = dataset.id
        w.report[name] = (report.id, warn.rule_id)

    async def scoped(key: str, role_slug: str, dataset_id: UUID) -> dict[str, str]:
        member = new_uuid7()
        w.principals[key] = Principal(kind=ActorKind.USER, id=member, display=key)
        await membership(principal_id=member)

        async def seed(session: AsyncSession) -> None:
            role = (
                await session.execute(
                    select(RoleRow).where(
                        RoleRow.workspace_id == workspace_id, RoleRow.slug == role_slug
                    )
                )
            ).scalar_one()
            session.add(
                RoleAssignmentRow(
                    workspace_id=workspace_id,
                    principal_kind="user",
                    principal_id=member,
                    role_id=role.id,
                    scope_type=ScopeType.DATASET.value,
                    scope_id=dataset_id,
                )
            )

        await seed_as_owner(seed)
        return _headers(member, workspace_id)

    w.headers["analyst_x"] = await scoped("analyst_x", "analyst", w.dataset_id["x"])
    w.headers["actuary_x"] = await scoped("actuary_x", "pricing_actuary", w.dataset_id["x"])
    nobody = new_uuid7()
    await membership(principal_id=nobody)
    w.headers["nobody"] = _headers(nobody, workspace_id)
    return w


@pytest.fixture
def client(api_client: TestClient) -> TestClient:
    return api_client


# One row per route: how to call it on a named Dataset, as which scoped principal, and the
# unknown-id form of the same call.
def _dictionary(client: TestClient, w: World, name: str, headers: dict[str, str]):
    return client.put(
        f"/api/v1/datasets/{w.slug[name]}/dictionary", json=_DICTIONARY, headers=headers
    )


def _rule_set(client: TestClient, w: World, name: str, headers: dict[str, str]):
    return client.put(f"/api/v1/datasets/{w.slug[name]}/rule-set", json=_RULE_SET, headers=headers)


def _acknowledge(client: TestClient, w: World, name: str, headers: dict[str, str]):
    report_id, rule_id = w.report[name]
    return client.post(
        f"/api/v1/validation-reports/{report_id}/results/{rule_id}/acknowledge",
        json=_ACK,
        headers=headers,
    )


def _unknown(route: str, client: TestClient, headers: dict[str, str]):
    if route == "dictionary":
        return client.put(
            f"/api/v1/datasets/no-such-{new_uuid7().hex[-8:]}/dictionary",
            json=_DICTIONARY,
            headers=headers,
        )
    if route == "rule-set":
        return client.put(
            f"/api/v1/datasets/no-such-{new_uuid7().hex[-8:]}/rule-set",
            json=_RULE_SET,
            headers=headers,
        )
    return client.post(
        f"/api/v1/validation-reports/{uuid4()}/results/{uuid4()}/acknowledge",
        json=_ACK,
        headers=headers,
    )


_RULE_SET_OWED = pytest.mark.xfail(
    strict=True,
    reason=(
        "FD 8177 rule-set limb: owned by SL 8192 (SL-1878 Task 4 follow-on), "
        "activates when SL-1736 merges"
    ),
)


# route -> (call, the scoped-to-X principal's key in `world.headers`, the success status)
ROUTES: dict[str, tuple[Callable[..., Any], str, int]] = {
    "dictionary": (_dictionary, "analyst_x", 200),
    "rule-set": (_rule_set, "analyst_x", 200),
    "acknowledge": (_acknowledge, "actuary_x", 201),
}

#: The routes for the tests that are red at base. The rule-set limb is carried to SL 8192: its four
#: tests are STRICT xfails, so the day the fix lands they XPASS and fail the run, forcing this mark
#: and the rule-set row of `test_route_scope_guard.KNOWN_SCOPE_GAPS` out together.
RED_ROUTES = [
    "dictionary",
    pytest.param("rule-set", marks=_RULE_SET_OWED),
    "acknowledge",
]


@pytest.mark.req("FR-345")
@pytest.mark.parametrize("route", RED_ROUTES)
def test_a_grant_scoped_to_one_dataset_reaches_that_datasets_write(
    client: TestClient, world: World, route: str
) -> None:
    """Red at base: 403 `PERMISSION_DENIED` from the route's scope-less `requires()`."""
    call, who, ok = ROUTES[route]
    response = call(client, world, "x", world.headers[who])
    assert response.status_code == ok, response.text


@pytest.mark.req("FR-345")
@pytest.mark.parametrize("route", RED_ROUTES)
def test_the_same_grant_on_another_dataset_is_refused_by_the_handler_as_scope_denied(
    client: TestClient, world: World, route: str
) -> None:
    """The control: the refusal must come from the handler's scoped check, so its code is
    `SCOPE_DENIED`, not the route's `PERMISSION_DENIED`. Red at base: `PERMISSION_DENIED`."""
    call, who, _ = ROUTES[route]
    response = call(client, world, "y", world.headers[who])
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "SCOPE_DENIED", response.text


@pytest.mark.req("FR-345")
@pytest.mark.parametrize("route", list(ROUTES))
def test_a_workspace_wide_holder_still_reaches_the_write(
    client: TestClient, world: World, route: str
) -> None:
    """Green at base and must stay so: the held-anywhere gate admits a workspace-wide grant."""
    call, _, ok = ROUTES[route]
    assert call(client, world, "x", world.headers["workspace"]).status_code == ok


@pytest.mark.req("FR-343")
@pytest.mark.parametrize("route", list(ROUTES))
def test_a_member_with_no_grant_is_refused_by_the_route_before_any_lookup(
    client: TestClient, world: World, route: str
) -> None:
    """FR-343's order: held nowhere → 403 `PERMISSION_DENIED`, an unknown id included (no 404).
    Green at base and must stay so."""
    response = _unknown(route, client, world.headers["nobody"])
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED", response.text
    call, _, _ = ROUTES[route]
    known = call(client, world, "x", world.headers["nobody"])
    assert known.status_code == 403
    assert known.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-345")
@pytest.mark.parametrize("route", RED_ROUTES)
def test_a_scoped_holder_asking_for_an_unknown_id_gets_not_found(
    client: TestClient, world: World, route: str
) -> None:
    """R-scoped-unknown-id: the order is held-anywhere, load (404), scoped. A holder on X passes
    the first step, so an unknown id is `NOT_FOUND`: the accepted residual's other half.
    Red at base: 403 `PERMISSION_DENIED` from the route."""
    _, who, _ = ROUTES[route]
    response = _unknown(route, client, world.headers[who])
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "NOT_FOUND", response.text


# ---- FR-452: a 403 is never counted ------------------------------------------------------


@pytest.fixture
def limited_client(api_settings: Settings, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(rate_limit, "_KEY_TTL_SECONDS", 3600)
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as test_client:
        test_client.app.state.rate_limiter.clock = lambda: FIXED_SECOND  # type: ignore[attr-defined]
        yield test_client


@pytest_asyncio.fixture
async def limit_two(database, workspace_id):
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        await settings_service.set_workspace_setting(session, workspace_id, LIMIT_KEY, 2)
    yield

    async def remove(session: AsyncSession) -> None:
        await session.execute(
            delete(WorkspaceSettingRow).where(WorkspaceSettingRow.workspace_id == workspace_id)
        )

    await seed_as_owner(remove)


@pytest.mark.req("FR-452")
@pytest.mark.parametrize("route", list(ROUTES))
def test_the_route_gates_refusal_is_not_counted(
    limited_client: TestClient, world: World, limit_two: None, route: str
) -> None:
    """R-count-gate. A member holding the permission nowhere is refused by the route (403) and
    that refusal leaves the budget whole: two management reads after two refusals are admitted
    and the third is `429`, which also proves the counter is live. Green at base."""
    call, _, _ = ROUTES[route]
    headers = world.headers["nobody"]
    for _ in range(2):
        assert call(limited_client, world, "x", headers).status_code == 403
    assert limited_client.get("/api/v1/me", headers=headers).status_code == 200
    assert limited_client.get("/api/v1/me", headers=headers).status_code == 200
    assert limited_client.get("/api/v1/me", headers=headers).status_code == 429


@pytest.mark.req("FR-452")
@pytest.mark.parametrize("route", RED_ROUTES)
def test_the_scoped_refusal_is_a_scope_denied_and_is_not_counted(
    limited_client: TestClient, world: World, limit_two: None, route: str
) -> None:
    """R-count-scoped. The X-scoped principal's 403 on Y is the handler's `SCOPE_DENIED` and is
    not counted either. Red at base on the code (`PERMISSION_DENIED`); after the fix it fails if
    the route gate or the service counts before the scoped check."""
    call, who, _ = ROUTES[route]
    headers = world.headers[who]
    for _ in range(2):
        refused = call(limited_client, world, "y", headers)
        assert refused.status_code == 403, refused.text
        assert refused.json()["code"] == "SCOPE_DENIED", refused.text
    assert limited_client.get("/api/v1/me", headers=headers).status_code == 200
    assert limited_client.get("/api/v1/me", headers=headers).status_code == 200
    assert limited_client.get("/api/v1/me", headers=headers).status_code == 429


# ---- DP-3: the acknowledge refusal names the cause ---------------------------------------


@pytest.mark.req("FR-46")
async def test_acknowledge_by_a_role_without_the_permission_is_acknowledge_forbidden_role(
    database, workspace_id, world: World, grant
) -> None:
    """DP-3, the role refusal: an analyst holds the permission nowhere, so the service keeps
    `ACKNOWLEDGE_FORBIDDEN_ROLE`. Green at base; must stay so."""
    report_id, rule_id = world.report["x"]
    with pytest.raises(PlatformError) as excinfo:
        async with database.unit_of_work() as session:
            await validation.acknowledge(
                session,
                workspace_id=workspace_id,
                actor=world.principals["analyst_x"],
                report_id=report_id,
                rule_id=rule_id,
                justification="reviewed",
            )
    assert excinfo.value.code == "ACKNOWLEDGE_FORBIDDEN_ROLE"


@pytest.mark.req("FR-345")
async def test_acknowledge_by_an_actuary_scoped_to_another_dataset_is_scope_denied(
    database, workspace_id, world: World
) -> None:
    """DP-3, the scope refusal: the actuary holds the permission, on X only, so the report of Y
    is refused as `SCOPE_DENIED`, not as a role refusal. Red at base:
    `ACKNOWLEDGE_FORBIDDEN_ROLE`."""
    report_id, rule_id = world.report["y"]
    with pytest.raises(PlatformError) as excinfo:
        async with database.unit_of_work() as session:
            await validation.acknowledge(
                session,
                workspace_id=workspace_id,
                actor=world.principals["actuary_x"],
                report_id=report_id,
                rule_id=rule_id,
                justification="reviewed",
            )
    assert excinfo.value.code == "SCOPE_DENIED"


@pytest.mark.req("FR-452")
@pytest.mark.parametrize("route", RED_ROUTES)
def test_a_not_found_after_the_route_gate_is_counted(
    limited_client: TestClient, world: World, limit_two: None, route: str
) -> None:
    """DP-3 (b), the maintainer's "2026-10-22 18:21:15 BST": FR-452 exempts only 401 and 403, so
    the load `404` a held-anywhere holder gets for an unknown id counts. Limit 2: the `404`
    spends one, the first `/me` the second, the next `/me` is `429`. Red at base: the `404` is not
    counted, so the second `/me` is admitted."""
    _, who, _ = ROUTES[route]
    headers = world.headers[who]
    assert _unknown(route, limited_client, headers).status_code == 404
    assert limited_client.get("/api/v1/me", headers=headers).status_code == 200
    assert limited_client.get("/api/v1/me", headers=headers).status_code == 429
