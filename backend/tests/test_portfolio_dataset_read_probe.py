"""FD 8184 probe — a Dataset-scoped `dataset:read` grant vs the portfolio Dataset Version routes.

`03` §5.1 (the rate-table diff, the Dislocation Run routes) requires `dataset:read` on the
portfolio Dataset Version. `rate_tables.rate_table_diff` checks it with
`rbac.require_permission(...)` and NO resource, and `rbac._covers` answers False for a scoped
assignment asked about no resource (FR-345), so a principal whose `dataset:read` is scoped to the
portfolio's own Dataset is refused on its own portfolio.

Red-first: the first test FAILS (403) if the defect is real; the second is the control (a scope
on a DIFFERENT Dataset must still refuse). The rate-table diff route is driven because the
portfolio can be a real validated Dataset Version with fixtures this repo already owns
(`test_rate_table_diff_portfolio`), and the first request needs no Job run.
"""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from backend.tests.test_api_datasets import _headers
from backend.tests.test_model_jobs import _actuary, _dataset
from backend.tests.test_rate_table_diff_portfolio import (
    _diff_url,
    _identity_table,
    validated_portfolio,
)
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.models import (
    DatasetVersionRow,
    RoleAssignmentRow,
    RoleRow,
    WorkspaceMemberRow,
)
from app.db.session import Database
from app.platform.blobs import BlobStore
from model_schema import ScopeType


async def _caller(database: Database, workspace_id: UUID, dataset_scope: UUID) -> dict[str, str]:
    """`rating:read` workspace-wide (the route's own permission) and `dataset:read` scoped to
    `dataset_scope` only: the only thing under test is the dataset scope."""
    caller = uuid4()
    async with database.unit_of_work() as session:
        rating = RoleRow(
            workspace_id=workspace_id,
            slug=f"rating-{uuid4().hex[:6]}",
            description="rating:read",
            permissions=["rating:read"],
            builtin=False,
        )
        reader = RoleRow(
            workspace_id=workspace_id,
            slug=f"dsread-{uuid4().hex[:6]}",
            description="dataset:read",
            permissions=["dataset:read"],
            builtin=False,
        )
        session.add_all([rating, reader])
        await session.flush()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=caller,
                role_id=rating.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=caller,
                role_id=reader.id,
                scope_type=ScopeType.DATASET.value,
                scope_id=dataset_scope,
            )
        )
        session.add(WorkspaceMemberRow(user_id=caller, workspace_id=workspace_id))
    return _headers(caller, workspace_id)


async def _world(database, workspace_id, principal, blob_store):
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    other_dataset = await _dataset(database, blob_store, workspace_id, actor)
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    async with database.session() as session:
        portfolio_dataset = (
            await session.execute(
                select(DatasetVersionRow.dataset_id).where(DatasetVersionRow.id == portfolio)
            )
        ).scalar_one()
    assert portfolio_dataset != other_dataset
    return portfolio, portfolio_dataset, other_dataset, slug


@pytest.mark.req("FR-345")
async def test_a_dataset_read_grant_scoped_to_the_portfolios_dataset_admits_the_diff(
    database: Database,
    workspace_id,
    principal,
    blob_store: BlobStore,
    grant,
    api_client: TestClient,
) -> None:
    await grant("analyst")
    portfolio, portfolio_dataset, _other, slug = await _world(
        database, workspace_id, principal, blob_store
    )
    headers = await _caller(database, workspace_id, portfolio_dataset)
    response = api_client.get(
        _diff_url(slug),
        params={"against": "previous", "portfolio": str(portfolio)},
        headers=headers,
    )
    assert response.status_code in (200, 202), (response.status_code, response.text)


@pytest.mark.req("FR-345")
async def test_a_dataset_read_grant_scoped_to_another_dataset_is_refused(
    database: Database,
    workspace_id,
    principal,
    blob_store: BlobStore,
    grant,
    api_client: TestClient,
) -> None:
    await grant("analyst")
    portfolio, _own, other_dataset, slug = await _world(
        database, workspace_id, principal, blob_store
    )
    headers = await _caller(database, workspace_id, other_dataset)
    response = api_client.get(
        _diff_url(slug),
        params={"against": "previous", "portfolio": str(portfolio)},
        headers=headers,
    )
    assert response.status_code == 403, (response.status_code, response.text)
