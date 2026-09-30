"""FR-237 through the platform (WK-1178 fix slice, PL-1299 acceptance 6).

A version whose algorithm names a rate table its pins do not carry fails its compile Job with
`RATING_VERSION_UNPINNED`. This mirrors `test_an_unpinned_version_is_refused_over_http` and
imports its helpers by name rather than copying them (the dispatch record's condition 1b: a
new file, so this slice and WK-674 Slice 2 do not both edit `test_rating_version_compile.py`).
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

from model_schema import JobStatus


@pytest.mark.req("FR-237")
def test_a_step_ref_the_pins_do_not_carry_is_refused_over_http(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    algorithm = _minimal_algorithm()
    algorithm["steps"].insert(1, {
        "step_id": "s_tbl", "type": "table", "label": "Factor",
        "rate_table_ref": "rate_table:unpinned-tbl@1", "key_expr": ["premium_in"],
        "on_miss": "error", "consumes": ["premium_in"], "produces": "factor",
    })
    created = api_client.post("/api/v1/rating-algorithms", json=algorithm, headers=headers)
    assert created.status_code == 201, created.text

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database, workspace_id, principal.id,
            algorithm_ref="rating_algorithm:minimal@1", pins=_empty_pins(),
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "RATING_VERSION_UNPINNED"
    assert "rate_table:unpinned-tbl@1" in job_row.error["message"]
