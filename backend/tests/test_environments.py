"""The Environment record's routes (`07` FR-428, `03` §5.1; WK-674 Slice 2, PL-1392 Task 4).

Every test starts from a **fresh** Environment slug rather than from a seed. `environments` is
deployment-wide and the suite empties the database only at session end (`conftest_db.py`
re-seeds `dev`, `uat` and `prod` then), so a test that renamed or retired a seed would leave
that change for every later test in the session.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment as RuntimeEnvironment
from app.config import Settings
from app.db.models import AuditEventRow, DeploymentRow, EnvironmentRow
from app.db.session import Database


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_blob_bucket, test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=RuntimeEnvironment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        blob_bucket=test_blob_bucket(),
    )


@pytest.fixture
def client(api_settings: Settings):
    from app.main import create_app

    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


def _identity(workspace_id, principal) -> dict[str, str]:
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


@pytest_asyncio.fixture
async def headers(workspace_id, principal, grant) -> dict[str, str]:
    await grant("admin")
    return _identity(workspace_id, principal)


@pytest_asyncio.fixture
async def deployer_headers(workspace_id, grant) -> dict[str, str]:
    """A member holding the read set and `deployment:promote`, not `admin:manage_environments`.

    A **second principal**: the `headers` fixture grants `admin` to the test principal, and a
    caller holding both roles would hold the write permission.
    """
    from model_schema import new_uuid7

    other = new_uuid7()
    await grant("deployer", principal_id=other)
    return {DEV_PRINCIPAL_HEADER: str(other), "Workspace-Id": str(workspace_id)}


@pytest_asyncio.fixture
async def unprivileged_headers(workspace_id, principal, membership) -> dict[str, str]:
    await membership()
    return _identity(workspace_id, principal)


def _slug() -> str:
    return f"env-{uuid4().hex[:8]}"


def _body(slug: str, **overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "slug": slug,
        "name": f"Name of {slug}",
        "description": "a test environment",
        "promotion_order": 4,
        "requires_prior_environment": "prod",
    }
    body.update(overrides)
    return body


def _create(client: TestClient, headers: dict[str, str], slug: str | None = None, **overrides):
    return client.post(
        "/api/v1/environments", json=_body(slug or _slug(), **overrides), headers=headers
    )


def _policy_naming(client: TestClient, headers: dict[str, str], environment: str | None) -> dict:
    """The workspace policy with `prod`'s `deployment` entry copied to `environment`.

    `None` returns the policy without any entry naming a test environment.
    """
    policy = client.get("/api/v1/approval-policy", headers=headers).json()
    entry = next(
        p for p in policy["policies"] if p["artifact_type"] == "deployment"
    )
    policy["policies"] = [p for p in policy["policies"] if p["artifact_type"] != "deployment"]
    policy["policies"].append(entry)
    if environment is not None:
        policy["policies"].append(
            {**entry, "environment": environment, "skippable_predecessors": []}
        )
    return policy


def _service_account(client: TestClient, headers: dict[str, str], environments: list[str]):
    return client.post(
        "/api/v1/service-accounts",
        json={
            "slug": f"sa-{uuid4().hex[:8]}",
            "environments": environments,
            "permissions": ["score:execute"],
        },
        headers=headers,
    )


# --- the permission (Acceptance 4, FR-428, RL-1236 DP-B) -----------------------------------


@pytest.mark.req("FR-428")
def test_a_caller_without_the_environments_permission_cannot_create_rename_or_retire(
    client: TestClient, deployer_headers, headers
) -> None:
    """Predicted red before the router: 404. After the router without the check: the
    non-Admin call succeeds (201/200). The deployer holds the read set, so the refusal is the
    write permission's and not the read's."""
    slug = _slug()
    assert _create(client, deployer_headers, slug).status_code == 403
    assert _create(client, deployer_headers, slug).json()["code"] == "PERMISSION_DENIED"

    # An Admin makes one, so the rename and retire refusals are not 404s.
    assert _create(client, headers, slug).status_code == 201
    renamed = client.patch(
        f"/api/v1/environments/{slug}", json={"name": "New"}, headers=deployer_headers
    )
    assert renamed.status_code == 403
    assert renamed.json()["code"] == "PERMISSION_DENIED"
    retired = client.post(f"/api/v1/environments/{slug}/retire", headers=deployer_headers)
    assert retired.status_code == 403
    assert retired.json()["code"] == "PERMISSION_DENIED"

    # Nothing changed.
    row = next(
        e
        for e in client.get("/api/v1/environments", headers=headers).json()["items"]
        if e["slug"] == slug
    )
    assert row["name"] == f"Name of {slug}"
    assert row["retired_at"] is None


@pytest.mark.req("FR-428")
def test_an_unprivileged_member_cannot_even_list_environments(
    client: TestClient, unprivileged_headers
) -> None:
    response = client.get("/api/v1/environments", headers=unprivileged_headers)
    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-428")
def test_an_admin_creates_lists_renames_and_retires(client: TestClient, headers) -> None:
    slug = _slug()
    created = _create(client, headers, slug)
    assert created.status_code == 201
    body = created.json()
    assert body["slug"] == slug
    assert body["promotion_order"] == 4
    assert body["requires_prior_environment"] == "prod"
    assert body["retired_at"] is None
    assert body["live_deployments"] == []

    listing = client.get("/api/v1/environments", headers=headers).json()
    slugs = [e["slug"] for e in listing["items"]]
    assert {"dev", "uat", "prod", slug} <= set(slugs)
    assert listing["total_estimate"] >= 4

    renamed = client.patch(
        f"/api/v1/environments/{slug}",
        json={"name": "Renamed", "description": "new words"},
        headers=headers,
    )
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Renamed"
    assert renamed.json()["description"] == "new words"
    assert renamed.json()["slug"] == slug

    retired = client.post(f"/api/v1/environments/{slug}/retire", headers=headers)
    assert retired.status_code == 200
    assert retired.json()["retired_at"] is not None
    assert retired.json()["slug"] == slug


@pytest.mark.req("FR-428")
def test_the_list_is_cursor_paginated_in_promotion_order(client: TestClient, headers) -> None:
    first = client.get("/api/v1/environments?limit=1", headers=headers).json()
    assert len(first["items"]) == 1
    assert first["next_cursor"] is not None
    seen = [first["items"][0]]
    cursor = first["next_cursor"]
    while cursor:
        page = client.get(f"/api/v1/environments?limit=1&cursor={cursor}", headers=headers).json()
        seen.extend(page["items"])
        cursor = page["next_cursor"]
    orders = [e["promotion_order"] for e in seen]
    assert orders == sorted(orders)
    assert len({e["slug"] for e in seen}) == len(seen)


# --- the slug and the rename (RL-1301 A.6; auditor-plans N1, N2) -----------------------------


@pytest.mark.req("FR-428")
def test_a_body_naming_a_different_slug_is_refused(client: TestClient, headers) -> None:
    """`EnvironmentUpdate` is `extra="forbid"`: a changed slug is refused, naming the field."""
    slug = _slug()
    _create(client, headers, slug)
    response = client.patch(
        f"/api/v1/environments/{slug}", json={"slug": "somewhere-else"}, headers=headers
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"
    assert "slug" in response.text
    listing = client.get("/api/v1/environments", headers=headers).json()["items"]
    assert "somewhere-else" not in {e["slug"] for e in listing}


@pytest.mark.req("FR-428")
@pytest.mark.parametrize("bad", ["a", "UPPER-case", "has space", "-leading"])
def test_a_slug_outside_the_reference_grammar_is_refused(
    client: TestClient, headers, bad: str
) -> None:
    """N2: one `Slug` type, not a second copy of the pattern."""
    response = _create(client, headers, bad)
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-428")
def test_a_slug_is_never_reissued_after_retirement(client: TestClient, headers) -> None:
    """N1: otherwise an old `deployment:<slug>@n` reference would name another Environment."""
    slug = _slug()
    assert _create(client, headers, slug).status_code == 201
    assert client.post(f"/api/v1/environments/{slug}/retire", headers=headers).status_code == 200
    again = _create(client, headers, slug)
    assert again.status_code == 409
    assert slug in again.json()["detail"]
    assert "retired" in again.json()["detail"]


@pytest.mark.req("FR-428")
def test_a_live_slug_cannot_be_created_twice(client: TestClient, headers) -> None:
    slug = _slug()
    assert _create(client, headers, slug).status_code == 201
    assert _create(client, headers, slug).status_code == 409


@pytest.mark.req("FR-428")
def test_a_predecessor_must_be_an_existing_environment(client: TestClient, headers) -> None:
    response = _create(client, headers, requires_prior_environment="no-such-env")
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"
    assert "no-such-env" in response.json()["detail"]


@pytest.mark.req("FR-428")
def test_an_unknown_slug_is_a_404_on_rename_and_retire(client: TestClient, headers) -> None:
    assert (
        client.patch("/api/v1/environments/no-such-env", json={"name": "x"}, headers=headers)
    ).status_code == 404
    assert (
        client.post("/api/v1/environments/no-such-env/retire", headers=headers)
    ).status_code == 404


@pytest.mark.req("FR-428")
def test_a_retired_environment_cannot_be_retired_or_renamed(client: TestClient, headers) -> None:
    slug = _slug()
    _create(client, headers, slug)
    client.post(f"/api/v1/environments/{slug}/retire", headers=headers)
    assert client.post(f"/api/v1/environments/{slug}/retire", headers=headers).status_code == 409
    assert (
        client.patch(f"/api/v1/environments/{slug}", json={"name": "x"}, headers=headers)
    ).status_code == 409


# --- retirement is refused while something names the Environment ---------------------------


@pytest.mark.req("FR-428")
def test_retirement_is_refused_while_a_policy_entry_names_it(client: TestClient, headers) -> None:
    slug = _slug()
    _create(client, headers, slug)
    put = client.put(
        "/api/v1/approval-policy", json=_policy_naming(client, headers, slug), headers=headers
    )
    assert put.status_code == 200, put.text

    refused = client.post(f"/api/v1/environments/{slug}/retire", headers=headers)
    assert refused.status_code == 409
    assert "deployment" in refused.json()["detail"]
    assert slug in refused.json()["detail"]
    live = [e for e in client.get("/api/v1/environments", headers=headers).json()["items"]]
    assert next(e for e in live if e["slug"] == slug)["retired_at"] is None

    # Removing the entry lifts the refusal.
    client.put(
        "/api/v1/approval-policy", json=_policy_naming(client, headers, None), headers=headers
    )
    assert client.post(f"/api/v1/environments/{slug}/retire", headers=headers).status_code == 200


@pytest.mark.req("FR-428")
def test_retirement_is_refused_while_an_unrevoked_key_names_it(
    client: TestClient, headers
) -> None:
    slug = _slug()
    _create(client, headers, slug)
    account = _service_account(client, headers, [slug]).json()["account"]

    refused = client.post(f"/api/v1/environments/{slug}/retire", headers=headers)
    assert refused.status_code == 409
    assert account["keys"][0]["prefix"] in refused.json()["detail"]

    revoked = client.delete(
        f"/api/v1/service-accounts/{account['id']}/keys/{account['keys'][0]['prefix']}",
        headers=headers,
    )
    assert revoked.status_code == 200
    assert client.post(f"/api/v1/environments/{slug}/retire", headers=headers).status_code == 200


@pytest.mark.req("FR-428")
async def test_retirement_is_refused_while_a_deployment_is_live(
    client: TestClient, headers, database: Database, workspace_id, principal
) -> None:
    slug = _slug()
    _create(client, headers, slug)
    async with database.unit_of_work() as session:
        environment = (
            await session.execute(select(EnvironmentRow).where(EnvironmentRow.slug == slug))
        ).scalar_one()
        session.add(
            DeploymentRow(
                workspace_id=workspace_id,
                environment_id=environment.id,
                rating_version_ref="rating_version:motor@1",
                bundle_hash="sha256:" + "0" * 64,
                deployed_by=principal.id,
                reason="a test deployment",
            )
        )
    refused = client.post(f"/api/v1/environments/{slug}/retire", headers=headers)
    assert refused.status_code == 409
    assert "rating_version:motor@1" in refused.json()["detail"]

    listed = next(
        e
        for e in client.get("/api/v1/environments", headers=headers).json()["items"]
        if e["slug"] == slug
    )
    assert [d["rating_version_ref"] for d in listed["live_deployments"]] == [
        "rating_version:motor@1"
    ]
    assert listed["live_deployments"][0]["bundle_hash"] == "sha256:" + "0" * 64


# --- "existing" means non-retired (RL-1301 A.6, N3) ------------------------------------------


@pytest.mark.req("FR-428")
def test_the_policy_refuses_a_deployment_entry_naming_an_unknown_environment(
    client: TestClient, headers
) -> None:
    """A policy naming `prd` would ungate the real target as silently as a rename."""
    response = client.put(
        "/api/v1/approval-policy", json=_policy_naming(client, headers, "prd"), headers=headers
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"
    assert "prd" in response.json()["detail"]


@pytest.mark.req("FR-428")
def test_the_policy_refuses_a_deployment_entry_naming_a_retired_environment(
    client: TestClient, headers
) -> None:
    slug = _slug()
    _create(client, headers, slug)
    client.post(f"/api/v1/environments/{slug}/retire", headers=headers)
    response = client.put(
        "/api/v1/approval-policy", json=_policy_naming(client, headers, slug), headers=headers
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"
    assert slug in response.json()["detail"]


@pytest.mark.req("FR-428")
def test_a_policy_with_no_named_environment_is_still_accepted(client: TestClient, headers) -> None:
    """The control: the check reads only environment-qualified `deployment` entries."""
    put = client.put(
        "/api/v1/approval-policy", json=_policy_naming(client, headers, None), headers=headers
    )
    assert put.status_code == 200, put.text


# --- credentials name only existing Environments (RL-1301 A.6 at 80afeb40) -------------------


@pytest.mark.req("FR-428")
def test_a_key_for_an_unknown_environment_is_refused_at_creation(
    client: TestClient, headers
) -> None:
    response = _service_account(client, headers, ["prd"])
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"
    assert "prd" in response.json()["detail"]


@pytest.mark.req("FR-428")
def test_a_key_for_a_retired_environment_is_refused_at_creation(
    client: TestClient, headers
) -> None:
    slug = _slug()
    _create(client, headers, slug)
    client.post(f"/api/v1/environments/{slug}/retire", headers=headers)
    response = _service_account(client, headers, [slug])
    assert response.status_code == 422
    assert slug in response.json()["detail"]


@pytest.mark.req("FR-428")
def test_a_key_for_a_seeded_environment_is_still_minted(client: TestClient, headers) -> None:
    """The control: `dev`, `uat` and `prod` exist, so the check does not over-refuse."""
    response = _service_account(client, headers, ["uat", "prod"])
    assert response.status_code == 201, response.text


@pytest.mark.req("FR-428")
def test_rotation_is_refused_for_an_account_naming_a_retired_environment(
    client: TestClient, headers
) -> None:
    slug = _slug()
    _create(client, headers, slug)
    account = _service_account(client, headers, [slug]).json()["account"]
    client.delete(
        f"/api/v1/service-accounts/{account['id']}/keys/{account['keys'][0]['prefix']}",
        headers=headers,
    )
    assert client.post(f"/api/v1/environments/{slug}/retire", headers=headers).status_code == 200

    rotated = client.post(f"/api/v1/service-accounts/{account['id']}/rotate", headers=headers)
    assert rotated.status_code == 422
    assert rotated.json()["code"] == "VALIDATION_FAILED"
    assert slug in rotated.json()["detail"]


# --- audit (FR-272, NFR-498) -------------------------------------------------------------


@pytest.mark.req("FR-428")
async def test_each_write_has_exactly_one_audit_event(
    client: TestClient, headers, database: Database, workspace_id
) -> None:
    slug = _slug()
    _create(client, headers, slug)
    client.patch(f"/api/v1/environments/{slug}", json={"name": "Renamed"}, headers=headers)
    client.post(f"/api/v1/environments/{slug}/retire", headers=headers)
    # A refused write adds none.
    client.patch(f"/api/v1/environments/{slug}", json={"slug": "x-y"}, headers=headers)

    async with database.session() as session:
        events = (
            (
                await session.execute(
                    select(AuditEventRow)
                    .where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.entity_ref == f"environment:{slug}",
                    )
                    .order_by(AuditEventRow.sequence)
                )
            )
            .scalars()
            .all()
        )
    assert [e.action for e in events] == [
        "environment.created",
        "environment.updated",
        "environment.retired",
    ]
    assert events[0].before is None
    assert events[0].after["slug"] == slug
    assert events[1].before["name"] == f"Name of {slug}"
    assert events[1].after["name"] == "Renamed"
    assert events[2].before["retired_at"] is None
    assert events[2].after["retired_at"] is not None
