"""FR-223 through the platform (WK-675 S3, FD-1437 limb 2; RL-1438 acceptance 1 and 4).

A version whose declared `model_reference_mode` disagrees with a `model_call` step fails its
compile Job with `MODEL_REFERENCE_MODE_INCONSISTENT`, not `BUNDLE_COMPILE_FAILED`; saving the
same algorithm on its own is unaffected. Helpers are imported by name from
`test_rating_version_compile`, as `test_rating_pin_membership_api` does.
"""

from __future__ import annotations

import asyncio

import pytest
from backend.tests.test_rating_version_compile import (
    _empty_pins,
    _handlers,  # noqa: F401  # the module's autouse fixture; imported by name so it applies
    _headers,
    _insert_version,
    _minimal_algorithm,
    _run_compile_job,
)

from app.db.models import RatingVersionRow
from model_schema import JobStatus


def _algorithm_with_an_exact_model_call() -> dict:
    algorithm = _minimal_algorithm()
    algorithm["steps"].insert(1, {
        "step_id": "s_model", "type": "model_call", "label": "Risk premium",
        "model_ref": "model:motor-ad-frequency@7", "mode": "exact",
        "feature_map": {"premium_in": "premium_in"},
        "consumes": ["premium_in"], "produces": "risk_premium_minor",
    })
    return algorithm


@pytest.mark.req("FR-223")
def test_the_autouse_handler_registration_fixture_applies_to_this_module(request) -> None:
    """See `test_rating_pin_membership_api`: importing `_handlers` is what makes it apply."""
    assert "_handlers" in request.fixturenames


@pytest.mark.req("FR-223")
def test_a_mode_mismatch_fails_the_compile_job_with_its_named_code(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_algorithm_with_an_exact_model_call(), headers=headers
    )
    assert created.status_code == 201, created.text  # save does not check FR-223 (RL-1438 item 3)

    async def _make_version():
        row = await _insert_version(
            database, workspace_id, principal.id,
            algorithm_ref="rating_algorithm:minimal@1", pins=_empty_pins(),
        )
        async with database.unit_of_work() as session:
            stored = await session.get(RatingVersionRow, row.id)
            stored.model_reference_mode = "approximation"
        return row

    row = asyncio.get_event_loop().run_until_complete(_make_version())

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "MODEL_REFERENCE_MODE_INCONSISTENT"
    assert "s_model" in job_row.error["message"]
