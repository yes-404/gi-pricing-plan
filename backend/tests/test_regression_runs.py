"""The persisted Regression Run and its lookup (03 §4.9, FR-260, FR-261, FR-9301; PL-1205 T5).

`regression_runs` has one writer, `persist_run`; the scalar `cases_blob_sha256` the generic
blob route's deny matches is written from the same object as the JSONB, and a test holds
them equal. `latest_run` is the submit gate's lookup: the LATEST run for exactly one
(bundle, suite) pair, so an earlier pass never outlives a later failure (audit A1).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import select

from app.db.models import RatingVersionRow, RegressionRunRow
from app.db.session import Database
from app.platform import regression_runs as service
from model_schema import RegressionRun, new_uuid7

_T0 = datetime(2026, 9, 28, 9, 0, 0, tzinfo=UTC)


def _run(*, overall: str = "pass", bundle: str = "b", suite: str = "a",
         minutes: int = 0, blob: str = "c") -> RegressionRun:
    failing = overall == "fail"
    return RegressionRun.model_validate({
        "suite_ref": "regression_suite:motor-gb-core@3",
        "suite_content_hash": "sha256:" + suite * 64,
        "rating_version_ref": "rating_version:motor-gb@27",
        "bundle_hash": "sha256:" + bundle * 64,
        "started_at": (_T0 + timedelta(minutes=minutes)).isoformat(),
        "finished_at": (_T0 + timedelta(minutes=minutes, seconds=4)).isoformat(),
        "overall": overall,
        "generation": {"seed": 1, "cases": 10, "hypothesis_version": "6.165.7"},
        "cases_blob": {"sha256": blob * 64, "bytes": 10, "media_type": "application/json"},
        "golden_results": [],
        "property_results": [
            {"name": "p", "status": "fail", "cases_run": 10, "counterexample": {"x": 1},
             "counterexample_minimal": True, "shrink": "completed",
             "error_code": "PROPERTY_ASSERTION_FAILED"}
            if failing else {"name": "p", "status": "pass", "cases_run": 10}
        ],
    })


async def _rating_version(database: Database, workspace_id: UUID, slug: str = "motor-gb") -> UUID:
    async with database.unit_of_work() as session:
        row = RatingVersionRow(
            workspace_id=workspace_id, slug=slug, version=1, status="draft",
            dataset_version_id=new_uuid7(), model_ref="model:motor-ad-frequency@7",
            created_by=new_uuid7(), algorithm_ref=None,
            pins={"rate_tables": [], "models": [], "reference_tables": [],
                  "custom_objectives": []},
        )
        session.add(row)
        await session.flush()
        return row.id


async def _persist(database: Database, workspace_id: UUID, rv: UUID, run: RegressionRun) -> UUID:
    async with database.unit_of_work() as session:
        row = await service.persist_run(
            session, workspace_id=workspace_id, rating_version_id=rv, run=run,
            actor_id=new_uuid7(),
        )
        return row.id


async def _latest(database: Database, workspace_id: UUID, rv: UUID, **pair: str) -> Any:
    bundle = "sha256:" + pair.get("bundle", "b") * 64
    suite = "sha256:" + pair.get("suite", "a") * 64
    async with database.session() as session:
        row = await service.latest_run(
            session, workspace_id=workspace_id, rating_version_id=rv,
            bundle_hash=bundle, suite_content_hash=suite,
        )
        return None if row is None else (row.id, row.overall)


@pytest.mark.req("FR-261")
@pytest.mark.req("NFR-499")
async def test_the_scalar_blob_digest_equals_the_runs_cases_blob(
    database: Database, workspace_id: UUID
) -> None:
    rv = await _rating_version(database, workspace_id)
    run = _run(blob="d")
    run_id = await _persist(database, workspace_id, rv, run)
    async with database.session() as session:
        row = (await session.execute(
            select(RegressionRunRow).where(RegressionRunRow.id == run_id)
        )).scalar_one()
    assert row.cases_blob_sha256 == run.cases_blob.sha256 == row.run["cases_blob"]["sha256"]
    assert (row.bundle_hash, row.suite_content_hash, row.overall) == (
        run.bundle_hash, run.suite_content_hash, "pass",
    )
    assert RegressionRun.model_validate(row.run) == run


@pytest.mark.req("FR-257")
async def test_the_latest_run_of_a_pair_wins_and_a_later_failure_supersedes_a_pass(
    database: Database, workspace_id: UUID
) -> None:
    """Limb (1) only: a passing Regression Suite; limbs (2)-(4) are not tested here."""
    rv = await _rating_version(database, workspace_id)
    assert await _latest(database, workspace_id, rv) is None
    first = await _persist(database, workspace_id, rv, _run(overall="pass", minutes=0))
    assert await _latest(database, workspace_id, rv) == (first, "pass")
    second = await _persist(database, workspace_id, rv, _run(overall="fail", minutes=5))
    assert await _latest(database, workspace_id, rv) == (second, "fail")
    third = await _persist(database, workspace_id, rv, _run(overall="pass", minutes=10))
    assert await _latest(database, workspace_id, rv) == (third, "pass")


@pytest.mark.req("FR-257")
async def test_a_run_of_another_bundle_or_suite_or_version_is_not_this_pairs_run(
    database: Database, workspace_id: UUID
) -> None:
    rv = await _rating_version(database, workspace_id)
    other = await _rating_version(database, workspace_id, slug="home-gb")
    await _persist(database, workspace_id, rv, _run(bundle="e"))   # a stale bundle
    await _persist(database, workspace_id, rv, _run(suite="f"))    # a different suite
    await _persist(database, workspace_id, other, _run())          # another version's run
    assert await _latest(database, workspace_id, rv) is None
    assert await _latest(database, workspace_id, rv, bundle="e") is not None
    assert await _latest(database, workspace_id, other) is not None


@pytest.mark.req("FR-257")
async def test_the_lookup_is_scoped_to_the_workspace(
    database: Database, workspace_id: UUID
) -> None:
    rv = await _rating_version(database, workspace_id)
    await _persist(database, workspace_id, rv, _run())
    async with database.session() as session:
        assert await service.latest_run(
            session, workspace_id=new_uuid7(), rating_version_id=rv,
            bundle_hash="sha256:" + "b" * 64, suite_content_hash="sha256:" + "a" * 64,
        ) is None
