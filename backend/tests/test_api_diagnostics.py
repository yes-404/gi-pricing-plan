"""The split and diagnostics surface over HTTP (`01` §5.1, `02` §5.1).

Written for the reason `test_api_transformations` gives, and one more specific to these:
`record_split` had a tested service function, a database table and **no route**, since WK-660.
The endpoint audit compares the spec's §5.1 table against the published contract, so an
endpoint missing from both is invisible to it — which is exactly how this one survived a
workstream closure. A test at the HTTP layer is what makes the absence detectable.
"""

from __future__ import annotations

import asyncio

import pytest
from backend.tests.test_api_datasets import _headers
from backend.tests.test_contracts import OPENAPI, _load
from fastapi.testclient import TestClient

from model_schema import new_uuid7


@pytest.fixture
def actuary(workspace_id, principal, grant) -> dict[str, str]:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    return _headers(principal.id, workspace_id)


@pytest.mark.req("FR-76")
def test_the_split_endpoints_are_published() -> None:
    """The gap this slice closed: both routes must be in the **published contract** that
    external consumers read, not merely reachable in the running app. The endpoint audit
    reads this file, so this is the layer where the absence was invisible."""
    paths = _load(OPENAPI)["paths"]
    assert "/api/v1/dataset-versions/{version_id}/splits" in paths
    entry = paths["/api/v1/dataset-versions/{version_id}/splits"]
    assert "post" in entry
    assert "get" in entry


@pytest.mark.req("FR-170")
def test_the_diagnostics_endpoint_is_published() -> None:
    paths = _load(OPENAPI)["paths"]
    assert "/api/v1/models/{slug}/diagnostics" in paths


@pytest.mark.req("FR-76")
def test_a_one_part_split_is_refused_over_the_api(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """Negative, at the edge. A one-part split is a filter, and recorded as a split it
    would let a model claim a holdout it never had — so the refusal must reach the caller
    as a 422 rather than as a 500 from inside the service."""
    refused = api_client.post(
        f"/api/v1/dataset-versions/{new_uuid7()}/splits",
        json={
            "name": "broken",
            "method": "random",
            "seed": 1,
            "parts": {"train": str(new_uuid7())},
        },
        headers=actuary,
    )
    assert refused.status_code == 422, refused.text


@pytest.mark.req("FR-170")
def test_diagnostics_for_an_unknown_model_are_a_404(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    missing = api_client.get(
        f"/api/v1/models/no-such-family-{new_uuid7().hex[-6:]}/diagnostics", headers=actuary
    )
    assert missing.status_code == 404, missing.text
