"""POST /api/v1/rating-versions declares the algorithm and the pins (FD-1421, RL-1428).

Create stores the declaration and checks only its shape (422); resolvability and maturity
stay with compile (FR-240), so each refusal below is read from the compile Job.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from backend.tests.approved_rows import mark_approved
from backend.tests.test_api_reference import _table as _seed_reference_table
from backend.tests.test_model_jobs_gbm import _fitted_gbm
from backend.tests.test_rating_algorithms import valid_algorithm
from backend.tests.test_rating_version_compile import (
    _empty_pins,
    _headers,
    _minimal_algorithm,
    _run_compile_job,
)
from sqlalchemy import func, select

from app.db.models import AuditEventRow, ModelRow, RatingVersionRow
from model_schema import JobStatus

_LOOP = asyncio.get_event_loop


@pytest.fixture(autouse=True)
def _handlers() -> None:
    from app.worker.rating_handlers import register_rating_handlers

    register_rating_handlers()


def _body(slug: str = "pinned-rv", **extra: object) -> dict:
    return {
        "slug": slug,
        "dataset_version_id": str(uuid4()),
        "model_ref": "model:motor-ad-frequency@7",
        **extra,
    }


def _algorithm(api_client, headers) -> str:
    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text
    return "rating_algorithm:minimal@1"


def _rows_with_slug(database, slug: str) -> int:
    async def _count() -> int:
        async with database.session() as session:
            return (
                await session.execute(
                    select(func.count())
                    .select_from(RatingVersionRow)
                    .where(RatingVersionRow.slug == slug)
                )
            ).scalar_one()

    return _LOOP().run_until_complete(_count())


def _field_codes(response) -> dict[str, str]:
    assert response.status_code == 422, response.text
    problem = response.json()
    assert problem["code"] == "VALIDATION_FAILED", problem
    return {e["field"]: e["code"] for e in problem["errors"]}


@pytest.mark.req("FR-237")
@pytest.mark.req("FR-239")
def test_a_version_created_with_its_algorithm_and_pins_compiles_over_http(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    _LOOP().run_until_complete(grant("admin"))
    headers = _headers(principal, workspace_id)
    algorithm_ref = _algorithm(api_client, headers)
    table = f"reference_table:{_seed_reference_table(api_client, headers, publish=True)}@1"
    pins = {**_empty_pins(), "reference_tables": [table]}

    created = api_client.post(
        "/api/v1/rating-versions",
        json=_body(algorithm_ref=algorithm_ref, pins=pins),
        headers=headers,
    )
    assert created.status_code == 201, created.text
    version = api_client.get(
        f"/api/v1/rating-versions/{created.json()['id']}", headers=headers
    ).json()
    assert version["algorithm_ref"] == algorithm_ref
    assert version["pins"] == pins

    job_row = _run_compile_job(api_client, headers, database, blob_store, version["id"])
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error


@pytest.mark.req("FR-239")
def test_a_version_created_without_algorithm_or_pins_is_refused_at_compile(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    created = api_client.post("/api/v1/rating-versions", json=_body(), headers=headers)
    assert created.status_code == 201, created.text
    job_row = _run_compile_job(api_client, headers, database, blob_store, created.json()["id"])
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "RATING_VERSION_UNPINNED"


@pytest.mark.req("FR-237")
def test_an_algorithm_ref_of_another_type_is_refused(
    api_client, workspace_id, principal, grant, database
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    response = api_client.post(
        "/api/v1/rating-versions",
        json=_body("bad-algo-rv", algorithm_ref="model:motor-ad-frequency@7"),
        headers=_headers(principal, workspace_id),
    )
    assert _field_codes(response).get("algorithm_ref") == "VALUE_ERROR"
    assert _rows_with_slug(database, "bad-algo-rv") == 0


@pytest.mark.req("FR-237")
@pytest.mark.parametrize(
    ("field", "ref"),
    [
        ("rate_tables", "model:motor-ad-frequency@7"),
        ("models", "rate_table:motor-expense@3"),
        ("reference_tables", "rate_table:motor-expense@3"),
        ("custom_objectives", "model:motor-ad-frequency@7"),
    ],
)
def test_a_pin_of_another_type_is_refused(
    api_client, workspace_id, principal, grant, database, field: str, ref: str
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    slug = f"bad-pin-{field.replace('_', '-')}"
    response = api_client.post(
        "/api/v1/rating-versions",
        json=_body(slug, pins={**_empty_pins(), field: [ref]}),
        headers=_headers(principal, workspace_id),
    )
    assert _field_codes(response).get("pins") == "VALUE_ERROR"
    assert _rows_with_slug(database, slug) == 0


@pytest.mark.req("FR-240")
def test_an_unknown_algorithm_is_refused_at_compile(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    created = api_client.post(
        "/api/v1/rating-versions",
        json=_body(algorithm_ref="rating_algorithm:no-such-algorithm@1", pins=_empty_pins()),
        headers=headers,
    )
    assert created.status_code == 201, created.text
    job_row = _run_compile_job(api_client, headers, database, blob_store, created.json()["id"])
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "NOT_FOUND"


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
def test_an_unapproved_model_pin_is_refused_at_compile_and_compiles_after_approval(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    algorithm_ref = _algorithm(api_client, headers)
    model_id, fit_status = _LOOP().run_until_complete(
        _fitted_gbm(database, blob_store, workspace_id)
    )
    assert fit_status is JobStatus.SUCCEEDED

    async def _ref() -> str:
        async with database.session() as session:
            row = await session.get(ModelRow, model_id)
            assert row is not None
            assert row.status != "approved", row.status
            return f"model:{row.model_family_slug}@{row.version}"

    model_ref = _LOOP().run_until_complete(_ref())
    created = api_client.post(
        "/api/v1/rating-versions",
        json=_body(
            "c4-rv", algorithm_ref=algorithm_ref, pins={**_empty_pins(), "models": [model_ref]}
        ),
        headers=headers,
    )
    assert created.status_code == 201, created.text
    version_id = created.json()["id"]

    first = _run_compile_job(api_client, headers, database, blob_store, version_id)
    assert first.status is JobStatus.FAILED
    assert first.error["code"] == "PIN_NOT_APPROVED"

    async def _approve() -> None:
        async with database.unit_of_work() as session:
            row = await session.get(ModelRow, model_id)
            await mark_approved(session, row)

    _LOOP().run_until_complete(_approve())
    second = _run_compile_job(api_client, headers, database, blob_store, version_id)
    assert second.status is JobStatus.SUCCEEDED, second.error
    assert _rows_with_slug(database, "c4-rv") == 1


@pytest.mark.req("FR-237")
def test_a_peril_structure_pin_is_stored_and_compile_names_the_missing_structure(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """A peril structure pin is stored; compile resolves it, and a missing one is named.

    This was FD-1456's tripwire (PL-1429 DP-5 (a)): the resolver had no `peril_structure`
    branch, so compile said "has no backend table yet". PL-1461 (SL-1462) adds the branch in
    the commit that rewrote this test. The positive test FD-1456's Disposition asks for, an
    unapproved structure refused and an approved one compiled, is
    `test_peril_structure_approval.py`; this one holds the pin write and the not-found path.
    """
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    algorithm_ref = _algorithm(api_client, headers)
    created = api_client.post(
        "/api/v1/rating-versions",
        json=_body(
            "peril-rv",
            algorithm_ref=algorithm_ref,
            pins={**_empty_pins(), "models": ["peril_structure:motor-perils@1"]},
        ),
        headers=headers,
    )
    assert created.status_code == 201, created.text
    job_row = _run_compile_job(api_client, headers, database, blob_store, created.json()["id"])
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "NOT_FOUND"
    # `execute_job` carries a PlatformError's detail as JobError.message (worker/tasks.py:227).
    assert "peril_structure:motor-perils@1" in job_row.error["message"]
    assert "has no backend table yet" not in job_row.error["message"]


@pytest.mark.req("FR-223")
def test_a_mode_mismatch_is_refused_at_create(
    api_client, workspace_id, principal, grant, database
) -> None:
    """RL 9758 item 2 at the pin write (PL-1429 DP-1 (a)): only a resolving algorithm is checked."""
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    saved = api_client.post("/api/v1/rating-algorithms", json=valid_algorithm(), headers=headers)
    assert saved.status_code == 201, saved.text

    refused = api_client.post(
        "/api/v1/rating-versions",
        json=_body(
            "mode-rv",
            algorithm_ref="rating_algorithm:motor-gb@1",
            pins=_empty_pins(),
            model_reference_mode="approximation",
        ),
        headers=headers,
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "MODEL_REFERENCE_MODE_INCONSISTENT"
    assert "s_rp" in refused.json()["detail"]
    assert _rows_with_slug(database, "mode-rv") == 0

    accepted = api_client.post(
        "/api/v1/rating-versions",
        json=_body(
            "mode-rv",
            algorithm_ref="rating_algorithm:motor-gb@1",
            pins=_empty_pins(),
            model_reference_mode="exact",
        ),
        headers=headers,
    )
    assert accepted.status_code == 201, accepted.text


@pytest.mark.req("NFR-499")
def test_the_mode_refusal_detail_names_the_step_and_modes_and_nothing_from_the_pins(
    api_client, workspace_id, principal, grant, database
) -> None:
    """RL-1438 / the 2026-10-06 01:44:23 BST re-ruling (B'): the FR-223 refusal's `str(exc)` is an
    artifact-level text. It names the step and the two declared modes, and carries no other part of
    the request body: a marker planted in an unrelated pin field is absent from the detail."""
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    saved = api_client.post("/api/v1/rating-algorithms", json=valid_algorithm(), headers=headers)
    assert saved.status_code == 201, saved.text
    marker = "marker-zq9x4"
    pins = {**_empty_pins(), "rate_tables": [f"rate_table:{marker}@1"]}

    refused = api_client.post(
        "/api/v1/rating-versions",
        json=_body(
            "mode-sentinel-rv",
            algorithm_ref="rating_algorithm:motor-gb@1",
            pins=pins,
            model_reference_mode="approximation",
        ),
        headers=headers,
    )
    assert refused.status_code == 422, refused.text
    body = refused.json()
    assert body["code"] == "MODEL_REFERENCE_MODE_INCONSISTENT"
    assert "s_rp" in body["detail"]
    assert "exact" in body["detail"]
    assert "approximation" in body["detail"]
    assert marker not in refused.text
    assert _rows_with_slug(database, "mode-sentinel-rv") == 0


@pytest.mark.req("FR-223")
def test_model_reference_mode_inconsistent_is_registered_and_owned() -> None:
    """RL 9758 Acceptance 3. It holds whichever slice registered the code first."""
    from pathlib import Path

    from app.errors import RATING_ERROR_CODES

    spec = (Path(__file__).resolve().parents[2] / "docs/specs/03-rating-engine.md").read_text()
    assert "MODEL_REFERENCE_MODE_INCONSISTENT" in RATING_ERROR_CODES
    owned = spec.split("### 5.1", 1)[1].split("\n### ", 1)[0]
    assert "`MODEL_REFERENCE_MODE_INCONSISTENT`" in owned


@pytest.mark.req("FR-237")
def test_the_create_body_is_the_model_schema_type(api_client) -> None:
    import model_schema
    from app.api import models as api_models

    assert api_models.RatingVersionCreate is model_schema.RatingVersionCreate
    schema = api_client.get("/openapi.json").json()["components"]["schemas"]["RatingVersionCreate"]
    assert {"algorithm_ref", "pins", "model_reference_mode"} <= set(schema["properties"])


@pytest.mark.req("FR-237")
def test_the_creation_event_records_the_declared_pins(
    api_client, workspace_id, principal, grant, database
) -> None:
    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    algorithm_ref = _algorithm(api_client, headers)
    created = api_client.post(
        "/api/v1/rating-versions",
        json=_body("audited-rv", algorithm_ref=algorithm_ref, pins=_empty_pins()),
        headers=headers,
    )
    assert created.status_code == 201, created.text

    async def _after() -> dict:
        async with database.session() as session:
            return (
                await session.execute(
                    select(AuditEventRow.after).where(
                        AuditEventRow.action == "rating_version.created",
                        AuditEventRow.entity_ref == "rating_version:audited-rv@1",
                    )
                )
            ).scalar_one()

    after = _LOOP().run_until_complete(_after())
    assert after["algorithm_ref"] == algorithm_ref
    assert after["pins"] == _empty_pins()
    assert after["model_reference_mode"] == "exact"
