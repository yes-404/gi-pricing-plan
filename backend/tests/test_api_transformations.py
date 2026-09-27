"""The banding and grouping surface over HTTP (`02` §5.1).

`02` §5.1 declares four routes for these — two proposals and two persists — and `01`'s
history is why they get their own tests rather than only service-level ones: the reference
publish lifecycle existed in the database and the API and in no document, and the endpoint
audit reported a complete surface because it compares the spec against the *contract*.
A route the contract does not carry is invisible to that audit, so it has to be visible
here.

The round trip is the point of the first test. FR-98 says the proposal is always
editable and what is stored is what was accepted — which is only true if the shape that
comes back is the shape that can be posted.
"""

from __future__ import annotations

import asyncio

import pytest
from backend.tests.test_api_datasets import _headers
from fastapi.testclient import TestClient

from model_schema import new_uuid7


@pytest.fixture
def actuary(workspace_id, principal, grant) -> dict[str, str]:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    return _headers(principal.id, workspace_id)


def _banding_body(slug: str, dataset_id: str) -> dict[str, object]:
    return {
        "id": str(new_uuid7()),
        "slug": slug,
        "dataset_id": dataset_id,
        "version": 1,
        "column": "driver_age",
        "method": "manual",
        "boundaries": [17.0, 25.0, 40.0, 99.0],
        "labels": ["17-24", "25-39", "40+"],
        "below_range": "error",
        "above_range": "clamp_to_last",
    }


def _grouping_body(slug: str, dataset_id: str) -> dict[str, object]:
    return {
        "id": str(new_uuid7()),
        "slug": slug,
        "dataset_id": dataset_id,
        "version": 1,
        "column": "region",
        "method": "manual",
        "mapping": {"N1": "NORTH", "N2": "NORTH", "S1": "SOUTH"},
        "unseen_level_behaviour": "map_to_default",
        "default_target_level": "NORTH",
    }


@pytest.mark.req("FR-101")
def test_a_banding_round_trips_through_the_api(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """Posted, listed, and re-posted as the next version — the shape survives each hop."""
    dataset_id = str(new_uuid7())
    slug = f"age-{new_uuid7().hex[-6:]}"

    created = api_client.post(
        "/api/v1/bandings", json=_banding_body(slug, dataset_id), headers=actuary
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["version"] == 1
    assert body["labels"] == ["17-24", "25-39", "40+"]
    assert body["above_range"] == "clamp_to_last"

    # FR-101: the same slug again is a **new version**, not an edit.
    edited = _banding_body(slug, dataset_id)
    edited["boundaries"] = [17.0, 22.0, 40.0, 99.0]
    again = api_client.post("/api/v1/bandings", json=edited, headers=actuary)
    assert again.status_code == 201
    assert again.json()["version"] == 2

    listed = api_client.get(
        "/api/v1/bandings", params={"dataset_id": dataset_id}, headers=actuary
    )
    assert listed.status_code == 200
    versions = sorted(row["version"] for row in listed.json() if row["slug"] == slug)
    assert versions == [1, 2]


@pytest.mark.req("FR-104")
def test_a_grouping_round_trips_and_keeps_its_unseen_level_behaviour(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    dataset_id = str(new_uuid7())
    slug = f"region-{new_uuid7().hex[-6:]}"

    created = api_client.post(
        "/api/v1/groupings", json=_grouping_body(slug, dataset_id), headers=actuary
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["unseen_level_behaviour"] == "map_to_default"
    assert body["default_target_level"] == "NORTH"
    assert body["mapping"]["N2"] == "NORTH"


@pytest.mark.req("FR-104")
def test_a_grouping_without_an_unseen_level_behaviour_is_refused_at_the_edge(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """A `422` naming the field, not a default chosen for the caller.

    The three answers price an unknown level very differently and none of them is obviously
    right, so there is nothing for the platform to fall back to.
    """
    body = _grouping_body(f"r-{new_uuid7().hex[-6:]}", str(new_uuid7()))
    del body["unseen_level_behaviour"]
    del body["default_target_level"]

    refused = api_client.post("/api/v1/groupings", json=body, headers=actuary)
    assert refused.status_code == 422
    problem = refused.json()
    assert problem["code"] == "VALIDATION_FAILED"
    assert any(
        "unseen_level_behaviour" in error["field"] for error in problem.get("errors", [])
    ), problem


@pytest.mark.req("FR-97")
def test_an_invalid_banding_is_refused_at_the_edge(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """The type's invariants reach the caller as a `422`, not a `500` from a validator."""
    body = _banding_body(f"bad-{new_uuid7().hex[-6:]}", str(new_uuid7()))
    body["labels"] = ["17-24", "25+"]  # one short for three bands

    refused = api_client.post("/api/v1/bandings", json=body, headers=actuary)
    assert refused.status_code == 422
    assert refused.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-83")
def test_a_banding_factor_declares_its_banding_over_the_api(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """`02` §4.1's `banding_id` reaches the Factor endpoint, and a mismatch is a `422`.

    The alternative is discovering it as a resolution failure inside a job, twenty seconds
    and one queue hop after the caller could have been told.
    """
    dataset_id = str(new_uuid7())
    banding = api_client.post(
        "/api/v1/bandings",
        json=_banding_body(f"age-{new_uuid7().hex[-6:]}", dataset_id),
        headers=actuary,
    ).json()

    created = api_client.post(
        "/api/v1/factors",
        json={
            "slug": f"age-banded-{new_uuid7().hex[-6:]}",
            "dataset_id": dataset_id,
            "type": "banding",
            "source_columns": ["driver_age"],
            "banding_id": banding["id"],
        },
        headers=actuary,
    )
    assert created.status_code == 201, created.text
    assert created.json()["banding_id"] == banding["id"]

    without = api_client.post(
        "/api/v1/factors",
        json={
            "slug": f"age-naked-{new_uuid7().hex[-6:]}",
            "dataset_id": dataset_id,
            "type": "banding",
            "source_columns": ["driver_age"],
        },
        headers=actuary,
    )
    assert without.status_code == 422, without.text


@pytest.mark.req("FR-96")
def test_a_factor_of_an_existing_slug_becomes_the_next_version(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """FR-96: factors are versioned independently and a Model Spec pins the version.

    Untested until now, which the scope audit reported and this closes: `create_factor`
    has always allocated the next version, but nothing asserted that editing a factor
    cannot change what a model fitted on it was fitted on.
    """
    dataset_id = str(new_uuid7())
    slug = f"driver-age-{new_uuid7().hex[-6:]}"

    def _post(intent: str) -> dict[str, object]:
        response = api_client.post(
            "/api/v1/factors",
            json={
                "slug": slug,
                "dataset_id": dataset_id,
                "source_columns": ["driver_age"],
                "intent": intent,
            },
            headers=actuary,
        )
        assert response.status_code == 201, response.text
        return response.json()

    first, second = _post("risk"), _post("control")
    assert (first["version"], second["version"]) == (1, 2)
    assert first["id"] != second["id"]

    listed = api_client.get(
        "/api/v1/factors", params={"dataset_id": dataset_id}, headers=actuary
    ).json()
    by_version = {row["version"]: row for row in listed if row["slug"] == slug}
    assert by_version[1]["intent"] == "risk", "version 1 still says what it said"
    assert by_version[2]["intent"] == "control"


@pytest.mark.req("FR-98")
def test_the_published_contract_carries_all_four_declared_routes() -> None:
    """`02` §5.1's table, against the artifact external consumers read (FR-451).

    Asserted against the committed contract rather than the running app: a route the
    contract does not carry is invisible to the endpoint audit, which is how `01`'s
    reference lifecycle stayed unspecified while every test passed.
    """
    import json
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2]
    document = json.loads(
        (root / "docs" / "contracts" / "openapi" / "generated.json").read_text()
    )
    for path in (
        "/api/v1/bandings/propose",
        "/api/v1/bandings",
        "/api/v1/groupings/propose",
        "/api/v1/groupings",
    ):
        assert path in document["paths"], path
        assert "post" in document["paths"][path], path
