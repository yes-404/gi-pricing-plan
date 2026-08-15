"""The reference-table read surface over HTTP (`01` §5.1, §5.3).

`01` §5.3 asks the `/reference` view for a table list, a version timeline and an
effective-date viewer, and §5.1 declared none of the three. The endpoint audit compares
the spec's table against the published contract, so an endpoint missing from **both** was
invisible to it — these tests exist so the routes cannot go missing again quietly.
"""

from __future__ import annotations

import asyncio

import pytest
from backend.tests.test_api_datasets import _headers
from fastapi.testclient import TestClient

from model_schema import new_uuid7

ROWS = [
    {"key": "SW1A", "payload": {"area": 12}, "effective_from": "2026-01-01",
     "effective_to": "2026-07-01"},
    {"key": "SW1A", "payload": {"area": 13}, "effective_from": "2026-07-01"},
    {"key": "EC1", "payload": {"area": 20}, "effective_from": "2026-01-01",
     "effective_to": "2026-04-01"},
]


@pytest.fixture
def admin(workspace_id, principal, grant) -> dict[str, str]:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("admin"))
    return _headers(principal.id, workspace_id)


def _table(api_client: TestClient, admin: dict[str, str], *, publish: bool = True) -> str:
    slug = f"area-{new_uuid7().hex[-6:]}"
    assert api_client.post(
        "/api/v1/reference-tables",
        json={"slug": slug, "key_columns": ["postcode"], "payload_columns": ["area"]},
        headers=admin,
    ).status_code == 201
    assert api_client.post(
        f"/api/v1/reference-tables/{slug}/versions",
        json={"source_note": "2026 refresh", "rows": ROWS},
        headers=admin,
    ).status_code == 201
    if publish:
        assert api_client.post(
            f"/api/v1/reference-tables/{slug}/versions/1/publish", headers=admin
        ).status_code == 200
    return slug


@pytest.mark.req("FR-DATA-30")
def test_a_table_with_only_drafts_reports_no_published_version(
    api_client: TestClient, admin: dict[str, str]
) -> None:
    """The state that decides whether the table can be pinned at all.

    A list that showed a version number regardless would say a table is usable when
    nothing in it has been published, and rating pins a published version (FR-DATA-32).
    """
    slug = _table(api_client, admin, publish=False)
    listed = api_client.get("/api/v1/reference-tables", headers=admin).json()
    table = next(t for t in listed if t["slug"] == slug)
    assert table["latest_published_version"] is None
    assert table["version_count"] == 1

    api_client.post(f"/api/v1/reference-tables/{slug}/versions/1/publish", headers=admin)
    listed = api_client.get("/api/v1/reference-tables", headers=admin).json()
    assert next(t for t in listed if t["slug"] == slug)["latest_published_version"] == 1


@pytest.mark.req("FR-DATA-30")
def test_a_version_reports_the_period_its_rows_actually_cover(
    api_client: TestClient, admin: dict[str, str]
) -> None:
    """`VR-REF-3` fails a dataset whose as-at date falls outside this period.

    `covers_to` is null because one row is open-ended — computed as `max(effective_to)`
    it would be 2026-07-01, which would say a table that never expires expires in July.
    """
    slug = _table(api_client, admin)
    timeline = api_client.get(f"/api/v1/reference-tables/{slug}/versions", headers=admin).json()
    assert len(timeline) == 1
    assert timeline[0]["row_count"] == 3
    assert timeline[0]["covers_from"] == "2026-01-01"
    assert timeline[0]["covers_to"] is None


@pytest.mark.req("FR-DATA-30")
def test_the_write_routes_report_what_was_stored_not_what_was_asked_for(
    api_client: TestClient, admin: dict[str, str]
) -> None:
    """Publish used to answer `row_count: 0` for a version with rows.

    A response that reports the request rather than the state will eventually report
    something that did not happen, and a client has no way to tell the two apart.
    """
    slug = f"area-{new_uuid7().hex[-6:]}"
    api_client.post(
        "/api/v1/reference-tables",
        json={"slug": slug, "key_columns": ["postcode"]},
        headers=admin,
    )
    loaded = api_client.post(
        f"/api/v1/reference-tables/{slug}/versions",
        json={"source_note": "load", "rows": ROWS},
        headers=admin,
    ).json()
    assert (loaded["row_count"], loaded["covers_from"]) == (3, "2026-01-01")

    published = api_client.post(
        f"/api/v1/reference-tables/{slug}/versions/1/publish", headers=admin
    ).json()
    assert published["row_count"] == 3
    assert published["status"] == "published"


@pytest.mark.req("FR-DATA-31")
def test_the_effective_date_viewer_reads_the_interval_as_half_open(
    api_client: TestClient, admin: dict[str, str]
) -> None:
    """A row ending on a date does not cover that date.

    This is the property that lets consecutive versions abut without overlapping, and the
    viewer must show it rather than round it away — a reader checking why a quote used
    area 13 on 1 July is checking exactly this boundary.
    """
    slug = _table(api_client, admin)
    url = f"/api/v1/reference-tables/{slug}/versions/1/rows"

    whole = api_client.get(url, headers=admin).json()
    assert len(whole) == 3, "no date means the version whole — what changed, not what applied"

    before = api_client.get(url, params={"as_at": "2026-06-30"}, headers=admin).json()
    assert [(r["key"], r["payload"]["area"]) for r in before] == [("SW1A", 12)]

    on_the_boundary = api_client.get(url, params={"as_at": "2026-07-01"}, headers=admin).json()
    assert [(r["key"], r["payload"]["area"]) for r in on_the_boundary] == [("SW1A", 13)]


@pytest.mark.req("FR-DATA-32")
def test_the_viewer_reads_the_pinned_version_and_never_falls_back(
    api_client: TestClient, admin: dict[str, str]
) -> None:
    """A version that does not exist is a 404, not the latest one.

    Falling back would be the mistake FR-DATA-32 exists to prevent, taught by the one
    screen an actuary uses to understand reference data.
    """
    slug = _table(api_client, admin)
    missing = api_client.get(
        f"/api/v1/reference-tables/{slug}/versions/7/rows", headers=admin
    )
    assert missing.status_code == 404
    assert missing.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-DATA-31")
def test_the_lookup_debugger_explains_a_miss_in_terms_of_the_interval(
    api_client: TestClient, admin: dict[str, str]
) -> None:
    """"No row" is the answer most likely to look like a bug, so it says why."""
    slug = _table(api_client, admin)
    hit = api_client.get(
        f"/api/v1/reference-tables/{slug}/lookup",
        params={"key": "SW1A", "as_at": "2026-07-01"},
        headers=admin,
    )
    assert hit.status_code == 200
    assert hit.json()["payload"] == {"area": 13}
    assert hit.json()["version"] == 1

    miss = api_client.get(
        f"/api/v1/reference-tables/{slug}/lookup",
        params={"key": "EC1", "as_at": "2026-09-01"},
        headers=admin,
    )
    assert miss.status_code == 404
    assert "half-open" in miss.json()["detail"]
