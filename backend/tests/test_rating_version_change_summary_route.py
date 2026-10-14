"""`GET /api/v1/rating-versions/{id}/change-summary-draft` (03 FR-242; WF-699 E1; PL-1502
Acceptance 10-15).

The draft is built from the structural diff and each re-pinned rate table's diff against the
most recently approved other version of the same algorithm. It is read-only. Versions are
seeded through the service, as `test_rating_version_compile.py` does: no HTTP route sets a
version's algorithm and pins yet (PL-1502 P7).
"""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import uuid4

import pytest
from backend.tests.approved_rows import add_approved, mark_approved
from backend.tests.test_api_rate_tables import _LEVELS, _diff_ready
from backend.tests.test_rate_tables_service import _seed_approved_model, _table_slug
from backend.tests.test_rating_version_compile import _headers, _minimal_algorithm
from sqlalchemy import func, select

from app.config import Settings
from app.db.models import (
    AuditEventRow,
    JobRow,
    RateTableRow,
    RateTableVersionRow,
    RatingVersionRow,
)
from app.db.session import Database
from app.platform import audit
from app.platform import rate_tables as rate_tables_service
from model_schema import ActorKind, ArtifactRef, JobSource, Principal
from model_schema.rating import AlgorithmDiff, RatingAlgorithm, diff_algorithms

pytestmark = pytest.mark.req("FR-242")

_SOFTENED = {"driver_age_band": [("17-20", 1.84), ("21-24", 1.41), ("25-29", 1.12)]}


def _run(coro: Any) -> Any:
    return asyncio.get_event_loop().run_until_complete(coro)


def _algorithm(version: int, *, extra_step: bool = False) -> dict[str, Any]:
    body = _minimal_algorithm()
    body["version"] = version
    if extra_step:
        body["steps"].insert(
            2,
            {
                "step_id": "s_extra",
                "type": "expression",
                "label": "Extra",
                "expr": "payable + 1",
                "result_type": "money_minor",
                "consumes": ["payable"],
                "produces": "payable2",
            },
        )
        body["steps"][-1]["consumes"] = ["payable2"]
    return body


async def _seed_table_version(
    database: Database, workspace_id, principal, slug: str, blob_store, relativities
) -> int:
    family = f"mf-{uuid4().hex[:8]}"
    await _seed_approved_model(database, workspace_id, family, relativities)
    seeded = await rate_tables_service.seed_from_model(
        database,
        workspace_id,
        principal,
        Settings(),
        blob_store,
        slug=slug,
        model_ref=ArtifactRef(type="model", slug=family, version=1),
        factor="driver_age_band",
        change_note="Seeded for the change-summary draft tests",
    )
    return seeded.version


def _pins(*tables: ArtifactRef) -> dict[str, list[str]]:
    return {
        "rate_tables": [str(ref) for ref in tables],
        "models": [],
        "reference_tables": [],
        "custom_objectives": [],
    }


async def _insert(
    database: Database,
    workspace_id,
    principal,
    *,
    version: int,
    algorithm_version: int | None,
    pins: dict | None,
    approved: bool = False,
    slug: str = "motor-rv",
    algorithm_slug: str = "minimal",
) -> RatingVersionRow:
    row = RatingVersionRow(
        workspace_id=workspace_id,
        slug=slug,
        version=version,
        status="approved" if approved else "draft",
        dataset_version_id=uuid4(),
        model_ref="model:motor-ad-frequency@7",
        created_by=principal.id,
        algorithm_ref=(
            None
            if algorithm_version is None
            else f"rating_algorithm:{algorithm_slug}@{algorithm_version}"
        ),
        pins=pins,
    )
    async with database.unit_of_work() as session:
        if approved:
            await add_approved(session, row)
            await audit.record(
                session,
                workspace_id=workspace_id,
                actor=Principal(kind=ActorKind.USER, id=principal.id, display="a@b.example"),
                source=JobSource.API,
                action="rating_version.approved",
                entity_ref=f"rating_version:{slug}@{version}",
                before={"status": "review"},
                after={"status": "approved"},
            )
        else:
            session.add(row)
            await session.flush()
        return row


def _url(row: RatingVersionRow) -> str:
    return f"/api/v1/rating-versions/{row.id}/change-summary-draft"


def _save_algorithms(api_client, headers, *bodies: dict[str, Any]) -> None:
    for body in bodies:
        created = api_client.post("/api/v1/rating-algorithms", json=body, headers=headers)
        assert created.status_code == 201, created.text


def test_wf699_e1_the_draft_is_built_from_the_approved_baseline(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    _run(grant("analyst"))
    headers = _headers(principal, workspace_id)
    slug = _table_slug()
    one = _run(_seed_table_version(database, workspace_id, principal, slug, blob_store, _LEVELS))
    two = _run(
        _seed_table_version(database, workspace_id, principal, slug, blob_store, _SOFTENED)
    )
    _save_algorithms(api_client, headers, _algorithm(1), _algorithm(2, extra_step=True))
    v1 = _run(
        _insert(
            database,
            workspace_id,
            principal,
            version=1,
            algorithm_version=1,
            pins=_pins(ArtifactRef(type="rate_table", slug=slug, version=one)),
            approved=True,
        )
    )
    v2 = _run(
        _insert(
            database,
            workspace_id,
            principal,
            version=2,
            algorithm_version=2,
            pins=_pins(ArtifactRef(type="rate_table", slug=slug, version=two)),
        )
    )

    response = api_client.get(_url(v2), headers=headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["baseline"] == f"rating_version:{v1.slug}@1"
    expected = diff_algorithms(
        RatingAlgorithm.model_validate(_algorithm(1)),
        RatingAlgorithm.model_validate(_algorithm(2, extra_step=True)),
    )
    assert AlgorithmDiff.model_validate(body["structural_diff"]) == expected
    assert "s_extra" in body["text"]
    (entry,) = body["rate_tables"]
    assert entry["slug"] == slug
    assert entry["pending"] is False
    # The diff route is a Job the first time (FR-232, R1), rows pairs too: run it to its end,
    # then read the stored artifact's summary, which is what the route serves.
    table_diff = _diff_ready(
        api_client, f"/api/v1/rate-tables/{slug}@{two}/diff", {"against": str(one)}, headers
    )
    assert table_diff.status_code == 200, table_diff.text
    assert entry["diff"] == table_diff.json()
    assert entry["diff"]["changed_cells"] == 1


def test_the_baseline_is_the_most_recently_approved_not_the_highest_number(
    api_client, workspace_id, principal, grant, database
) -> None:
    _run(grant("analyst"))
    headers = _headers(principal, workspace_id)
    _save_algorithms(api_client, headers, _algorithm(1))
    # v2 is approved first and v1 later: v1 is the later-approved, v3 the highest number.
    _run(
        _insert(
            database, workspace_id, principal, version=2, algorithm_version=1,
            pins=_pins(), approved=True,
        )
    )
    _run(
        _insert(
            database, workspace_id, principal, version=1, algorithm_version=1,
            pins=_pins(), approved=True,
        )
    )
    v3 = _run(
        _insert(
            database, workspace_id, principal, version=3, algorithm_version=1, pins=_pins()
        )
    )

    body = api_client.get(_url(v3), headers=headers).json()

    assert body["baseline"] == "rating_version:motor-rv@1"


@pytest.mark.parametrize(
    ("algorithm_version", "pins", "missing"),
    [(None, {"rate_tables": []}, "algorithm_ref"), (1, None, "pins")],
)
def test_a_version_without_an_algorithm_or_pins_is_refused(
    api_client, workspace_id, principal, grant, database, algorithm_version, pins, missing
) -> None:
    _run(grant("analyst"))
    headers = _headers(principal, workspace_id)
    row = _run(
        _insert(
            database, workspace_id, principal, version=1,
            algorithm_version=algorithm_version, pins=pins,
        )
    )

    response = api_client.get(_url(row), headers=headers)

    assert response.status_code == 409, response.text
    assert response.json()["code"] == "RATING_VERSION_UNPINNED"
    assert missing in response.json()["detail"]


def test_another_workspaces_version_is_404(
    api_client, workspace_id, principal, grant, database
) -> None:
    _run(grant("analyst"))
    headers = _headers(principal, workspace_id)
    # The algorithm exists for the caller, so with workspace scoping removed the draft would be
    # built and answer 200; the 404 below can only be the version's own scoped miss.
    _save_algorithms(api_client, headers, _algorithm(1))
    other = uuid4()
    row = _run(_insert(database, other, principal, version=1, algorithm_version=1, pins=_pins()))

    response = api_client.get(_url(row), headers=headers)

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "NOT_FOUND"
    assert body["title"] == "Rating version not found"


def test_rating_read_is_required(api_client, workspace_id, principal, grant, database) -> None:
    _run(grant("analyst"))
    row = _run(
        _insert(database, workspace_id, principal, version=1, algorithm_version=1, pins=_pins())
    )
    nobody = uuid4()

    stranger = Principal(kind=ActorKind.USER, id=nobody)

    response = api_client.get(_url(row), headers=_headers(stranger, workspace_id))

    assert response.status_code == 403


def _snapshot(database: Database, workspace_id, rating_version_id) -> tuple[Any, ...]:
    async def read() -> tuple[Any, ...]:
        async with database.session() as session:
            row = await session.get(RatingVersionRow, rating_version_id, populate_existing=True)
            assert row is not None
            events = await session.scalar(
                select(func.count())
                .select_from(AuditEventRow)
                .where(AuditEventRow.workspace_id == workspace_id)
            )
            jobs = await session.scalar(
                select(func.count()).select_from(JobRow).where(JobRow.workspace_id == workspace_id)
            )
            return (row.status, row.change_summary, row.evidence, row.updated_at, events, jobs)

    return _run(read())


def test_the_route_writes_nothing(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    _run(grant("analyst"))
    headers = _headers(principal, workspace_id)
    _save_algorithms(api_client, headers, _algorithm(1), _algorithm(2, extra_step=True))
    _run(
        _insert(
            database, workspace_id, principal, version=1, algorithm_version=1,
            pins=_pins(), approved=True,
        )
    )
    v2 = _run(
        _insert(database, workspace_id, principal, version=2, algorithm_version=2, pins=_pins())
    )
    before = _snapshot(database, workspace_id, v2.id)

    response = api_client.get(_url(v2), headers=headers)

    assert response.status_code == 200, response.text
    assert _snapshot(database, workspace_id, v2.id) == before


def test_a_parquet_table_answers_200_with_the_entry_pending(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    _run(grant("analyst"))
    headers = _headers(principal, workspace_id)
    slug = _table_slug()
    one = _run(_seed_table_version(database, workspace_id, principal, slug, blob_store, _LEVELS))
    two = _run(
        _seed_table_version(database, workspace_id, principal, slug, blob_store, _SOFTENED)
    )

    async def make_parquet() -> None:
        async with database.unit_of_work() as session:
            table = await session.scalar(
                select(RateTableRow).where(
                    RateTableRow.workspace_id == workspace_id, RateTableRow.slug == slug
                )
            )
            assert table is not None
            version = await session.scalar(
                select(RateTableVersionRow).where(
                    RateTableVersionRow.rate_table_id == table.id,
                    RateTableVersionRow.version_number == two,
                )
            )
            assert version is not None
            version.storage = "parquet"

    _run(make_parquet())
    _save_algorithms(api_client, headers, _algorithm(1), _algorithm(2))
    _run(
        _insert(
            database, workspace_id, principal, version=1, algorithm_version=1,
            pins=_pins(ArtifactRef(type="rate_table", slug=slug, version=one)), approved=True,
        )
    )
    v2 = _run(
        _insert(
            database, workspace_id, principal, version=2, algorithm_version=2,
            pins=_pins(ArtifactRef(type="rate_table", slug=slug, version=two)),
        )
    )
    jobs_before = _snapshot(database, workspace_id, v2.id)[-1]

    response = api_client.get(_url(v2), headers=headers)

    assert response.status_code == 200, response.text
    (entry,) = response.json()["rate_tables"]
    assert entry["pending"] is True
    assert entry["diff"] is None
    assert _snapshot(database, workspace_id, v2.id)[-1] == jobs_before


# --- FD-1679 / SL-1678: a version pinning two versions of one rate-table slug ---------------
# `RL-1538` makes such pins valid input, so create accepts them (each test asserts the 201);
# the drafted summary pairs rate tables by slug and refuses (409) rather than drop or mis-pair.


def _create_over_http(
    api_client, headers, *, algorithm_version: int, pins: dict[str, Any]
) -> str:
    created = api_client.post(
        "/api/v1/rating-versions",
        json={
            "slug": "motor-rv",
            "dataset_version_id": str(uuid4()),
            "model_ref": "model:motor-ad-frequency@7",
            "algorithm_ref": f"rating_algorithm:minimal@{algorithm_version}",
            "pins": pins,
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    return created.json()["id"]


async def _approve(database: Database, principal, workspace_id, rating_version_id: str) -> None:
    # Approval over HTTP needs the full FR-257 evidence, which is not this slice's subject:
    # mark the row approved the way `_insert(approved=True)` does.
    async with database.unit_of_work() as session:
        row = await session.get(RatingVersionRow, rating_version_id)
        assert row is not None
        await mark_approved(session, row)
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=Principal(kind=ActorKind.USER, id=principal.id, display="a@b.example"),
            source=JobSource.API,
            action="rating_version.approved",
            entity_ref=f"rating_version:{row.slug}@{row.version}",
            before={"status": "review"},
            after={"status": "approved"},
        )


def _two_versions_of_one_table(
    api_client, workspace_id, principal, grant, database, blob_store
) -> tuple[dict[str, str], ArtifactRef, ArtifactRef]:
    _run(grant("analyst"))
    headers = _headers(principal, workspace_id)
    slug = _table_slug()
    one = _run(_seed_table_version(database, workspace_id, principal, slug, blob_store, _LEVELS))
    two = _run(
        _seed_table_version(database, workspace_id, principal, slug, blob_store, _SOFTENED)
    )
    _save_algorithms(api_client, headers, _algorithm(1), _algorithm(2, extra_step=True))
    return (
        headers,
        ArtifactRef(type="rate_table", slug=slug, version=one),
        ArtifactRef(type="rate_table", slug=slug, version=two),
    )


def _assert_refused(response, slug: str) -> None:
    assert response.status_code == 409, response.text
    problem = response.json()
    assert problem["code"] == "VALIDATION_FAILED", problem
    assert slug in problem["detail"], problem
    assert "FD-1679" in problem["detail"], problem


@pytest.mark.parametrize("candidate_order", ["two_then_one", "one_then_two"])
def test_a_candidate_pinning_two_versions_of_one_table_is_refused(
    api_client, workspace_id, principal, grant, database, blob_store, candidate_order
) -> None:
    """Red 1 (X@two, X@one: today the entry is dropped) and Red 2 (X@one, X@two: today a
    false `X one -> two`)."""
    headers, one, two = _two_versions_of_one_table(
        api_client, workspace_id, principal, grant, database, blob_store
    )
    baseline = _create_over_http(api_client, headers, algorithm_version=1, pins=_pins(one))
    _run(_approve(database, principal, workspace_id, baseline))
    pair = (two, one) if candidate_order == "two_then_one" else (one, two)
    candidate = _create_over_http(api_client, headers, algorithm_version=2, pins=_pins(*pair))

    response = api_client.get(
        f"/api/v1/rating-versions/{candidate}/change-summary-draft", headers=headers
    )

    _assert_refused(response, one.slug)


def test_a_baseline_pinning_two_versions_of_one_table_is_refused(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """Red 3: the duplicate is on the baseline side; today `rate_tables == []`."""
    headers, one, two = _two_versions_of_one_table(
        api_client, workspace_id, principal, grant, database, blob_store
    )
    _run(
        _insert(
            database, workspace_id, principal, version=1, algorithm_version=1,
            pins=_pins(one, two), approved=True,
        )
    )
    candidate = _run(
        _insert(
            database, workspace_id, principal, version=2, algorithm_version=2, pins=_pins(two)
        )
    )

    _assert_refused(api_client.get(_url(candidate), headers=headers), one.slug)


def test_a_first_version_pinning_two_versions_of_one_table_is_still_answered(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """Red 4, a guard that passes on main: with no baseline nothing is paired, so the
    summary is not wrong and is not refused (PL-1677 DP-G2 (a))."""
    headers, one, two = _two_versions_of_one_table(
        api_client, workspace_id, principal, grant, database, blob_store
    )
    first = _create_over_http(api_client, headers, algorithm_version=1, pins=_pins(one, two))

    response = api_client.get(
        f"/api/v1/rating-versions/{first}/change-summary-draft", headers=headers
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["baseline"] is None
    assert body["rate_tables"] == []
