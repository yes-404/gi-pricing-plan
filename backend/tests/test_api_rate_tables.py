"""Rate table routes (03 §5.1, slice W10-2): seeding and cell diffs.

`POST /rate-tables/{slug}/seed-from-model` (FR-RATE-16) and
`GET /rate-tables/{slug}@{version}/diff?against=` (FR-RATE-17). Models are inserted
rather than fitted — these routes care that the model row carries an approved status and
a fit result with relativities, not how the fit happened, and a real GLM fit per test
would buy nothing this file asserts.
"""

from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

import pytest
from backend.tests.test_api_datasets import _headers
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.config import Settings
from app.db.models import (
    ModelRow,
    RateTableRow,
    RateTableVersionRow,
)
from app.db.session import Database
from model_schema import GlmSpec, ModelStatus, OffsetSpec, new_uuid7


@pytest.fixture
def actuary(workspace_id, principal, grant) -> dict[str, str]:
    """A caller with `RATING_WRITE` and `RATING_READ` (the `analyst` role)."""
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    return _headers(principal.id, workspace_id)


@pytest.fixture
def auditor_headers(workspace_id, grant) -> dict[str, str]:
    """A caller with `RATING_READ` but not `RATING_WRITE` (the `auditor` role)."""
    other = uuid4()
    asyncio.get_event_loop().run_until_complete(grant("auditor", principal_id=other))
    return _headers(other, workspace_id)


def _glm_spec(family: str, dataset_version_id: UUID) -> dict[str, object]:
    """A valid `GlmSpec` as JSON — `to_model` re-validates it, so `{}` will not do."""
    spec = GlmSpec(
        model_family_slug=family,
        dataset_version_id=dataset_version_id,
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
    )
    return spec.model_dump(mode="json")


def _fit_result(relativities: dict[str, list[float]]) -> dict[str, object]:
    """A `GlmFitResult` as JSON: one entry per factor, one per level."""
    return {
        "model_type": "glm",
        "converged": True,
        "iterations": 8,
        "fit_seconds": 1.0,
        "relativities": {
            factor: [
                {"level": level, "relativity": relativity, "estimate": 0.5}
                for level, relativity in levels
            ]
            for factor, levels in relativities.items()
        },
    }


def _insert_rows(rows: list[object]) -> None:
    """Insert rows on a loop of our own (`TestClient` is blocking, so an async fixture
    cannot be requested from the synchronous tests below)."""
    from backend.tests.conftest_db import test_database_url

    async def _insert(database: Database) -> None:
        async with database.unit_of_work() as session:
            session.add_all(rows)
            await session.flush()

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        try:
            loop.run_until_complete(_insert(database))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()


def _seed_approved_model(
    workspace_id: UUID, family: str, relativities: dict[str, list[tuple[str, float]]]
) -> None:
    """An approved ModelRow whose fit carries the given relativities."""
    _insert_rows(
        [
            ModelRow(
                workspace_id=workspace_id,
                model_family_slug=family,
                version=1,
                status=ModelStatus.APPROVED.value,
                dataset_version_id=new_uuid7(),
                spec=_glm_spec(family, new_uuid7()),
                spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}",
                fit_result=_fit_result(relativities),
                diagnostics_id=uuid4(),
            )
        ]
    )


_LEVELS: dict[str, list[tuple[str, float]]] = {
    "driver_age_band": [
        ("17-20", 1.92),
        ("21-24", 1.41),
        ("25-29", 1.12),
    ]
}


def _seed_body(family: str, change_note: str = "Seeded for the W10-2 tests") -> dict[str, object]:
    return {"model_ref": f"model:{family}@1", "change_note": change_note}


def _table_slug() -> str:
    return f"motor-driver-age-{uuid4().hex[:8]}"


@pytest.mark.req("FR-RATE-16")
def test_seed_creates_version_one_with_cells(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["slug"] == slug
    assert body["version"] == 1
    assert body["rateable"] is True
    assert body["storage"] == "rows"
    assert [key["name"] for key in body["keys"]] == ["driver_age_band"]
    assert body["value"]["name"] == "relativity"
    assert body["change_note"] == "Seeded for the W10-2 tests"
    assert body["seeded_from"]["model_ref"] == f"model:{family}@1"
    assert [row["driver_age_band"] for row in body["rows"]] == [
        "17-20",
        "21-24",
        "25-29",
    ]
    assert [row["relativity"] for row in body["rows"]] == ["1.92", "1.41", "1.12"]


@pytest.mark.req("FR-RATE-16")
@pytest.mark.req("FR-RATE-17")
def test_seed_appends_the_next_version_and_diff_vs_previous(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()

    first = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert first.status_code == 201, first.text
    assert first.json()["version"] == 1

    softened = {"driver_age_band": [("17-20", 1.84), ("21-24", 1.41), ("25-29", 1.12)]}
    family_v2 = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family_v2, softened)
    second = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family_v2, change_note="Softened 17-20"),
        headers=actuary,
    )
    assert second.status_code == 201, second.text
    assert second.json()["version"] == 2

    diff = api_client.get(
        f"/api/v1/rate-tables/{slug}@2/diff",
        params={"against": "previous"},
        headers=actuary,
    )
    assert diff.status_code == 200, diff.text
    body = diff.json()
    assert body["changed_cells"] == 1
    assert body["max_abs_change_pct"].startswith("4.166")
    assert body["exposure_weighted_mean_change_pct"] is None


@pytest.mark.req("FR-RATE-17")
def test_diff_vs_seed_compares_against_the_origin_not_the_previous_version(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """With three versions, `against=seed` answers v3-vs-v1 where
    `against=previous` answers v3-vs-v2."""
    slug = _table_slug()
    softened = {"driver_age_band": [("17-20", 1.84), ("21-24", 1.41), ("25-29", 1.12)]}
    softened_again = {
        "driver_age_band": [("17-20", 1.84), ("21-24", 1.50), ("25-29", 1.12)]
    }
    for family, relativities in (
        (f"mf-{uuid4().hex[:8]}", _LEVELS),
        (f"mf-{uuid4().hex[:8]}", softened),
        (f"mf-{uuid4().hex[:8]}", softened_again),
    ):
        _seed_approved_model(workspace_id, family, relativities)
        created = api_client.post(
            f"/api/v1/rate-tables/{slug}/seed-from-model",
            json=_seed_body(family),
            headers=actuary,
        )
        assert created.status_code == 201, created.text

    vs_previous = api_client.get(
        f"/api/v1/rate-tables/{slug}@3/diff",
        params={"against": "previous"},
        headers=actuary,
    )
    assert vs_previous.status_code == 200, vs_previous.text
    assert vs_previous.json()["changed_cells"] == 1  # 21-24 only

    vs_seed = api_client.get(
        f"/api/v1/rate-tables/{slug}@3/diff",
        params={"against": "seed"},
        headers=actuary,
    )
    assert vs_seed.status_code == 200, vs_seed.text
    assert vs_seed.json()["changed_cells"] == 2  # 17-20 and 21-24, from the origin


@pytest.mark.req("FR-RATE-17")
def test_diff_against_an_explicit_version(
    api_client: TestClient, workspace_id, actuary
) -> None:
    slug = _table_slug()
    softened = {"driver_age_band": [("17-20", 1.84), ("21-24", 1.41), ("25-29", 1.12)]}
    for family, relativities in (
        (f"mf-{uuid4().hex[:8]}", _LEVELS),
        (f"mf-{uuid4().hex[:8]}", softened),
    ):
        _seed_approved_model(workspace_id, family, relativities)
        created = api_client.post(
            f"/api/v1/rate-tables/{slug}/seed-from-model",
            json=_seed_body(family),
            headers=actuary,
        )
        assert created.status_code == 201, created.text

    diff = api_client.get(
        f"/api/v1/rate-tables/{slug}@2/diff",
        params={"against": "1"},
        headers=actuary,
    )
    assert diff.status_code == 200, diff.text
    assert diff.json()["changed_cells"] == 1


@pytest.mark.req("FR-RATE-16")
def test_seed_refuses_a_non_approved_model(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _insert_rows(
        [
            ModelRow(
                workspace_id=workspace_id,
                model_family_slug=family,
                version=1,
                status=ModelStatus.FITTED.value,
                dataset_version_id=new_uuid7(),
                spec=_glm_spec(family, new_uuid7()),
                spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}",
                fit_result=_fit_result(_LEVELS),
                diagnostics_id=uuid4(),
            )
        ]
    )

    response = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "PIN_NOT_APPROVED"


@pytest.mark.req("FR-RATE-16")
def test_seed_refuses_a_missing_model(
    api_client: TestClient, workspace_id, actuary
) -> None:
    response = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json=_seed_body(f"missing-{uuid4().hex[:8]}"),
        headers=actuary,
    )
    assert response.status_code == 404, response.text


@pytest.mark.req("FR-RATE-15")
@pytest.mark.req("FR-RATE-16")
def test_seed_refuses_a_bad_body(api_client: TestClient, workspace_id, actuary) -> None:
    response = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json={"model_ref": "not-a-ref", "change_note": "x"},
        headers=actuary,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"

    missing_note = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json={"model_ref": "model:whatever@1"},
        headers=actuary,
    )
    assert missing_note.status_code == 422, missing_note.text

    wrong_type = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json={"model_ref": "rating_algorithm:whatever@1", "change_note": "x"},
        headers=actuary,
    )
    assert wrong_type.status_code == 422, wrong_type.text


@pytest.mark.req("FR-RATE-19")
def test_seed_validation_failure_is_named(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """A model whose relativities repeat a level is refused with the named code —
    the plan's DUPLICATE_KEY maps onto 03 §5.2's RATE_TABLE_KEY_DUPLICATE."""
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(
        workspace_id, family, {"driver_age_band": [("17-20", 1.92), ("17-20", 1.50)]}
    )

    response = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "RATE_TABLE_KEY_DUPLICATE"


@pytest.mark.req("FR-RATE-17")
def test_diff_404s_for_unknown_table_and_version(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()
    created = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert created.status_code == 201, created.text

    missing_table = api_client.get(
        f"/api/v1/rate-tables/{_table_slug()}@1/diff",
        params={"against": "previous"},
        headers=actuary,
    )
    assert missing_table.status_code == 404, missing_table.text
    assert missing_table.json()["code"] == "RATE_TABLE_MISS"

    missing_version = api_client.get(
        f"/api/v1/rate-tables/{slug}@9/diff",
        params={"against": "previous"},
        headers=actuary,
    )
    assert missing_version.status_code == 404, missing_version.text

    no_previous = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/diff",
        params={"against": "previous"},
        headers=actuary,
    )
    assert no_previous.status_code == 404, no_previous.text


@pytest.mark.req("FR-RATE-17")
def test_diff_rejects_an_unknown_baseline(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()
    created = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert created.status_code == 201, created.text

    response = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/diff",
        params={"against": "banana"},
        headers=actuary,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-RATE-17")
def test_diff_seed_without_a_seed_origin_404s(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """`against=seed` resolves the baseline from the `seeded_from` trail; a version
    carrying no trail (direct inserts — the only creation path in this slice always
    pins a seed origin) answers 404 RATE_TABLE_MISS."""
    slug = _table_slug()
    table_row = RateTableRow(
        workspace_id=workspace_id,
        slug=slug,
        current_version=1,
        created_by=uuid4(),
    )
    _insert_rows([table_row])
    _insert_rows(
        [
            RateTableVersionRow(
                workspace_id=workspace_id,
                rate_table_id=table_row.id,
                version_number=1,
                storage="rows",
                definition={
                    "slug": slug,
                    "version": 1,
                    "rateable": True,
                    "storage": "rows",
                    "keys": [
                        {
                            "name": "driver_age_band",
                            "type": "string",
                            "banding_ref": None,
                        }
                    ],
                    "value": {
                        "name": "relativity",
                        "type": "relativity",
                        "unit": "factor",
                        "min": None,
                        "max": None,
                    },
                    "default_row": None,
                },
                change_note="unseeded probe",
                created_by=uuid4(),
            ),
        ]
    )

    response = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/diff",
        params={"against": "seed"},
        headers=actuary,
    )
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "RATE_TABLE_MISS"


@pytest.mark.req("FR-RATE-62")
def test_a_parquet_version_is_refused_until_w10_3(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """FR-RATE-62's parquet form answers 202 with a Job in W10-3; nothing can yet write
    parquet storage, so a diff touching one is refused with the named code rather than
    fabricating a diff."""
    slug = _table_slug()
    _insert_rows(
        [
            RateTableRow(
                workspace_id=workspace_id,
                slug=slug,
                current_version=1,
                created_by=uuid4(),
            )
        ]
    )

    async def _add_parquet_version(database: Database) -> None:
        async with database.unit_of_work() as session:
            table_row = (
                await session.execute(
                    select(RateTableRow).where(
                        RateTableRow.workspace_id == workspace_id,
                        RateTableRow.slug == slug,
                    )
                )
            ).scalar_one()
            session.add(
                RateTableVersionRow(
                    workspace_id=workspace_id,
                    rate_table_id=table_row.id,
                    version_number=1,
                    storage="parquet",
                    definition={
                        "slug": slug,
                        "version": 1,
                        "rateable": True,
                        "storage": "parquet",
                        "keys": [
                            {
                                "name": "driver_age_band",
                                "type": "string",
                                "banding_ref": None,
                            }
                        ],
                        "value": {
                            "name": "relativity",
                            "type": "relativity",
                            "unit": "factor",
                            "min": None,
                            "max": None,
                        },
                        "default_row": None,
                    },
                    change_note="parquet probe",
                    created_by=uuid4(),
                )
            )
            await session.flush()

    from backend.tests.conftest_db import test_database_url

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        try:
            loop.run_until_complete(_add_parquet_version(database))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()

    response = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/diff",
        params={"against": "previous"},
        headers=actuary,
    )
    assert response.status_code == 501, response.text
    assert response.json()["code"] == "RATE_TABLE_PARQUET_UNBUILT"


@pytest.mark.req("FR-PLAT-47")
def test_routes_are_permission_gated(
    api_client: TestClient, workspace_id, principal, auditor_headers, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()

    anon_seed = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
    )
    assert anon_seed.status_code == 401, anon_seed.text

    read_only_seed = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=auditor_headers,
    )
    assert read_only_seed.status_code == 403, read_only_seed.text

    created = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert created.status_code == 201, created.text

    anon_diff = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/diff",
        params={"against": "previous"},
    )
    assert anon_diff.status_code == 401, anon_diff.text

    read_only_diff = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/diff",
        # Version 1 has no `previous` (that diff is a 404, asserted in the 404s test);
        # the seed origin is version 1 itself, so this answers 200 with zero changes.
        params={"against": "seed"},
        headers=auditor_headers,
    )
    assert read_only_diff.status_code == 200, read_only_diff.text
