"""Rating Version compile endpoint (slice W9-3, FR-RATE-24/25).

A pinned version compiles to a self-contained Bundle with a reproducible hash; an
unpinned version and a broken guard are refused with named errors.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.db.models import RatingVersionRow


def _minimal_algorithm() -> dict:
    """A minimal graph with no external artifact refs — input, expression, output."""
    return {
        "slug": "minimal",
        "version": 1,
        "input_contract": [
            {"name": "premium_in", "type": "int", "nullable": False},
        ],
        "outputs": [
            {"name": "payable_premium_minor", "type": "money_minor", "required": True},
        ],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In",
             "input_name": "premium_in", "on_missing": "error", "produces": "premium_in"},
            {"step_id": "s_expr", "type": "expression", "label": "Apply",
             "expr": "premium_in * 2", "result_type": "money_minor",
             "consumes": ["premium_in"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }


def _headers(principal, workspace_id) -> dict[str, str]:
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }


async def _insert_version(
    database, workspace_id, created_by, algorithm_ref: str | None, pins: dict
) -> RatingVersionRow:
    row = RatingVersionRow(
        workspace_id=workspace_id,
        slug="minimal-rv",
        version=1,
        status="draft",
        dataset_version_id=uuid4(),
        model_ref="model:motor-ad-frequency@7",
        created_by=created_by,
        algorithm_ref=algorithm_ref,
        pins=pins,
    )
    async with database.unit_of_work() as session:
        session.add(row)
        await session.flush()
        return row


@pytest.mark.req("FR-RATE-24")
def test_a_pinned_version_compiles_over_http(
    api_client, workspace_id, principal, grant, database
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms",
        json=_minimal_algorithm(),
        headers=headers,
    )
    assert created.status_code == 201, created.text

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={"rate_tables": [], "models": [], "reference_tables": [], "custom_objectives": []},
        )
    )

    response = api_client.post(
        f"/api/v1/rating-versions/{row.id}/compile", headers=headers
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["content_hash"].startswith("sha256:")
    assert body["bytes"] > 0
    assert body["compiled_at"]


@pytest.mark.req("FR-RATE-22")
def test_an_unpinned_version_is_refused_over_http(
    api_client, workspace_id, principal, grant, database
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref=None,
            pins={"rate_tables": [], "models": [], "reference_tables": [], "custom_objectives": []},
        )
    )

    response = api_client.post(
        f"/api/v1/rating-versions/{row.id}/compile", headers=headers
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "RATING_VERSION_UNPINNED"
