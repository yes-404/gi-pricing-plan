"""FD 8177 probe — a Dataset-scoped `dataset:write` grant against `PUT /datasets/{slug}/dictionary`.

FR-345: an assignment may be limited to named Datasets. The route's `WriteDatasets`
dependency calls `requires(Perm.DATASET_WRITE)` with no resource, and `rbac._covers` answers
False for a scoped assignment asked about no resource, so the route may refuse a principal the
handler's own scoped check (`platform/datasets.update_dictionary`) would admit.

Red-first: the first test FAILS (403) if the defect is real; the second is the control (a scope
that does not cover Y must still refuse).
"""

from __future__ import annotations

from uuid import UUID

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.db.models import RoleAssignmentRow, RoleRow
from model_schema import ScopeType, new_uuid7


@pytest.fixture
def client(api_client: TestClient) -> TestClient:
    return api_client


def _headers(principal_id, workspace_id) -> dict[str, str]:
    return {DEV_PRINCIPAL_HEADER: str(principal_id), "Workspace-Id": str(workspace_id)}


@pytest_asyncio.fixture
async def world(client, grant, membership, database, workspace_id, principal):
    """Datasets X and Y, and a principal whose only `analyst` grant is scoped to X."""
    await grant("analyst")
    creator = _headers(principal.id, workspace_id)
    ids = {}
    for name in ("x", "y"):
        slug = f"ds-{name}-{new_uuid7().hex[-8:]}"
        created = client.post("/api/v1/datasets", json={"slug": slug}, headers=creator)
        assert created.status_code in (200, 201), created.text
        ids[name] = (slug, created.json()["id"])

    scoped = new_uuid7()
    await membership(principal_id=scoped)
    async with database.unit_of_work() as session:
        role = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == "analyst"
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=scoped,
                role_id=role.id,
                scope_type=ScopeType.DATASET.value,
                scope_id=UUID(ids["x"][1]),
            )
        )
    return ids, _headers(scoped, workspace_id)


_BODY = {"data_dictionary": {"policy_id": {"pii_class": "pseudonymous_key"}}}


@pytest.mark.req("FR-345")
def test_a_grant_scoped_to_one_dataset_may_replace_that_datasets_dictionary(
    client: TestClient, world
) -> None:
    ids, headers = world
    response = client.put(f"/api/v1/datasets/{ids['x'][0]}/dictionary", json=_BODY, headers=headers)
    assert response.status_code == 200, response.text


@pytest.mark.req("FR-345")
def test_the_same_grant_is_refused_on_another_dataset(client: TestClient, world) -> None:
    ids, headers = world
    response = client.put(f"/api/v1/datasets/{ids['y'][0]}/dictionary", json=_BODY, headers=headers)
    assert response.status_code == 403, response.text
