"""The demo rating version's regression evidence is EXECUTED, never inserted (DP-S3-8, T6b).

`examples/fremtpl2/model.py`'s `author_demo_rating_evidence` saves a labelled demo-fixture
algorithm, compiles it through the `rating.compile` Job, computes the golden quote's expected
premium with `score_one` at seed time and runs the regression through the `rating.regression`
Job. These tests drive that function and the shared submit/approve step, and assert the
seeded run's hashes are exactly what the submit gate pins (DP-S3-2).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from uuid import UUID

import pytest
from backend.tests.test_rating_versions import _principal
from sqlalchemy import select

from app.db.models import JobRow, RegressionRunRow
from app.db.session import Database
from app.platform import rating_versions as rating_service
from model_schema import ArtifactRef, JobKind, JobStatus, Pins, RegressionRun, new_uuid7

_SPEC = importlib.util.spec_from_file_location(
    "demo_model", Path(__file__).resolve().parents[2] / "examples" / "fremtpl2" / "model.py"
)
assert _SPEC is not None
assert _SPEC.loader is not None
demo_model = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(demo_model)


async def _draft(database: Database, workspace_id: UUID, analyst) -> UUID:
    algorithm_ref = await demo_model.save_demo_algorithm(database, workspace_id, analyst)
    async with database.unit_of_work() as session:
        row = await rating_service.create_rating_version(
            session, workspace_id=workspace_id, actor=analyst, slug="fremtpl2-demo",
            dataset_version_id=new_uuid7(),
            model_ref=ArtifactRef(type="model", slug="fremtpl2-glm", version=1),
            algorithm_ref=algorithm_ref, pins=Pins(),
        )
        return row.id


@pytest.mark.req("FR-257")
async def test_the_demo_evidence_is_produced_by_the_jobs_and_labelled_a_demo_fixture(
    database: Database, workspace_id, blob_store
) -> None:
    """Limb (1) only: a passing Regression Suite; limbs (2)-(4) are not tested here."""
    analyst = await _principal(database, workspace_id, "analyst")
    rating_id = await _draft(database, workspace_id, analyst)
    run_id = await demo_model.author_demo_rating_evidence(
        database, blob_store, workspace_id, analyst, rating_id
    )
    async with database.session() as session:
        run_row = (await session.execute(
            select(RegressionRunRow).where(RegressionRunRow.id == run_id)
        )).scalar_one()
        jobs = (await session.execute(
            select(JobRow).where(JobRow.kind == JobKind.RATING_REGRESSION)
        )).scalars().all()
    run = RegressionRun.model_validate(run_row.run)
    # executed: the run carries the Job that produced it, and that Job succeeded
    assert run.job_id is not None
    (job,) = [j for j in jobs if j.id == run.job_id]
    assert job.status is JobStatus.SUCCEEDED
    assert run.overall == "pass"
    # the label
    assert demo_model.DEMO_FIXTURE in run.suite_ref.slug
    assert demo_model.DEMO_QUOTE_NAME.startswith(demo_model.DEMO_FIXTURE)
    assert demo_model.DEMO_ALGORITHM_SLUG.startswith(demo_model.DEMO_FIXTURE)
    # the golden quote's expected premium was computed, not typed: doubling the input
    assert [g.status for g in run.golden_results] == ["pass"]
    assert run.golden_results[0].expected_minor == demo_model.DEMO_PREMIUM_IN * 2


@pytest.mark.req("FR-257")
async def test_the_seeded_runs_hashes_are_what_the_gate_pins_and_the_version_reaches_approved(
    database: Database, workspace_id, blob_store
) -> None:
    """Limb (1) only: a passing Regression Suite; limbs (2)-(4) are not tested here. DP-S3-2:
    the run's `bundle_hash` and `suite_content_hash` equal what the submit gate pins."""
    analyst = await _principal(database, workspace_id, "analyst")
    actuary = await _principal(database, workspace_id, "pricing_actuary")
    approver = await _principal(database, workspace_id, "approver")
    second = await _principal(database, workspace_id, "approver")
    rating_id = await _draft(database, workspace_id, analyst)
    run_id = await demo_model.author_demo_rating_evidence(
        database, blob_store, workspace_id, analyst, rating_id
    )
    await demo_model.submit_and_approve_demo(
        database, blob_store, workspace_id, actuary, approver, second, rating_id
    )
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        run_row = await session.get(RegressionRunRow, run_id)
    assert run_row is not None
    assert row.status == "approved"
    evidence = row.evidence or {}
    pinned = evidence["golden_quotes"]
    assert evidence["regression_suite_run_id"] == str(run_id)
    assert pinned["bundle_hash"] == run_row.bundle_hash == (row.bundle or {})["content_hash"]
    assert pinned["suite_content_hash"] == run_row.suite_content_hash
