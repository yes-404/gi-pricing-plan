"""Backtests, from the request to the stored artifact (`02` FR-MODEL-57, §4.12, §5.1).

`packages/pricing-core/tests/test_backtests.py` owns the maths. This file owns the four
things only the platform can be wrong about:

* **the refusals happen before a Job is queued**, `request_comparison`'s precedent and its
  reason — learning that a version cannot be backtested from a failed job twenty seconds
  later is a worse answer to the same question;
* **"a version other than the one it was fitted on" reaches the split parts.** The parent
  case is enforced by `BacktestSummary` itself; the parts are ids the contract has never
  seen, so this is the only layer that can refuse them, and refusing them is the whole
  difference between a backtest and the fit-time holdout figure under a later-period
  heading;
* **the artifact is immutable in the database**, at both layers — the first test here to
  exercise the trigger rather than only the grants, and the one that found FR-DATA-47;
* **both routes are in the published contract**, the omission FR-MODEL-84, FR-MODEL-56 and
  FR-MODEL-90 each had to repair.

The later period is the same book with **every rural row's claim count doubled**, which is a
known answer: the model was fitted where rural carries half of urban, so a book where the
gap has closed must read as an A/E above one, and the deterioration must be visible in the
rural cell of `ae_by_factor` specifically.
"""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from backend.tests.test_contracts import OPENAPI, _load
from backend.tests.test_data_jobs import _ingest, _validate
from backend.tests.test_model_jobs import (
    _actuary,
    _dataset,
    _factor,
    _spec,
    _split,
    _validated_version,
)
from backend.tests.test_model_offset_jobs import (
    _RESIDUAL_CAST_RECIPE,
    _residual_book,
)
from backend.tests.test_prediction import _fitted_residual_pair
from sqlalchemy import select, text

from app.db.models import BacktestRow, DatasetVersionRow, ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import backtests as service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.worker.tasks import execute_job
from model_schema import (
    MODEL_SPEC_ADAPTER,
    JobKind,
    JobStatus,
    Principal,
    SplitRef,
)

#: The same shape as `test_model_jobs.BOOK`, with the **rural** rows' claim counts doubled.
#: A model fitted on the original prices rural at half of urban; on this book the two are
#: level, so the model under-predicts and A/E must rise — and rise in the rural cell.
DETERIORATED = b"policy_id,exposure_years,area,claim_count,claim_amount_minor\n" + b"".join(
    f"P{i},1.0,{'urban' if i % 4 == 0 else 'rural'},2,"
    f"{200000 if i % 4 == 0 else 100000}\n".encode()
    for i in range(1, 401)
)


async def _fitted_model(
    database: Database, blob_store, workspace_id: UUID
) -> tuple[Principal, UUID, UUID, UUID, SplitRef]:
    """One model fitted through the real Job, and the dataset it was fitted on."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=_spec(version_id, (area,), split_ref=split),
        )
        model_id = row.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "model_id": str(model_id),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    return actor, model_id, dataset_id, version_id, split


async def _later_period(
    database: Database, blob_store, workspace_id: UUID, actor: Principal, dataset_id: UUID
) -> UUID:
    """A second validated version of the same dataset, carrying the deteriorated book."""
    version_id = await _ingest(
        database, blob_store, workspace_id, actor, dataset_id, DETERIORATED
    )
    report_id = await _validate(database, blob_store, workspace_id, actor, version_id)
    from app.platform import validation as validation_service

    async with database.unit_of_work() as session:
        await validation_service.promote_using_report(
            session,
            workspace_id=workspace_id,
            actor=actor,
            version_id=version_id,
            report_id=report_id,
        )
    return version_id


# -- The refusals, before a Job exists ----------------------------------------------------


@pytest.mark.req("FR-MODEL-57")
async def test_a_backtest_on_the_version_it_was_fitted_on_is_refused(
    database, blob_store, workspace_id
) -> None:
    """`02` §2's definition. A model measured on its own training data reports how well it
    memorised, and that number renders identically to out-of-time performance."""
    actor, model_id, _, version_id, _ = await _fitted_model(
        database, blob_store, workspace_id
    )
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.request_backtest(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                dataset_version_id=version_id,
            )
    assert refused.value.status_code == 409
    assert "fitted on" in (refused.value.detail or "")


@pytest.mark.req("FR-MODEL-57")
async def test_a_backtest_on_a_split_part_is_refused_and_the_part_is_named(
    database, blob_store, workspace_id
) -> None:
    """**The refusal the parent-only check would miss**, and the reason it exists.

    The frames a model is fitted and judged on are *derived versions* with ids of their own
    (`01` FR-DATA-36), so a request naming the holdout walks straight past a check that only
    compares against `spec.dataset_version_id` — and produces the fit-time holdout figure
    under a heading that says later period.
    """
    actor, model_id, _, _, split = await _fitted_model(database, blob_store, workspace_id)

    async with database.session() as session:
        from app.db.models import DatasetSplitRow

        parts = (await session.get(DatasetSplitRow, split.split_artifact_id)).parts
    holdout_version_id = UUID(str(parts["test"]))

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.request_backtest(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                dataset_version_id=holdout_version_id,
            )
    assert refused.value.status_code == 409
    assert "'test'" in (refused.value.detail or "")


@pytest.mark.req("FR-MODEL-57")
async def test_an_unfitted_model_cannot_be_backtested(
    database, blob_store, workspace_id
) -> None:
    """A `draft` has no coefficients, so there is nothing to score the later period with."""
    actor, _, dataset_id, version_id, split = await _fitted_model(
        database, blob_store, workspace_id
    )
    later = await _later_period(database, blob_store, workspace_id, actor, dataset_id)
    area = await _factor(database, workspace_id, actor, dataset_id, "area2", "area")

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=_spec(version_id, (area,), split_ref=split),
        )
        reserved = row.id

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.request_backtest(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=reserved,
                dataset_version_id=later,
            )
    assert refused.value.code == "MODEL_NOT_FITTED"
    assert "draft" in (refused.value.detail or "")


@pytest.mark.req("FR-MODEL-57")
async def test_a_version_that_is_not_validated_is_refused(
    database, blob_store, workspace_id
) -> None:
    """`01` §1.3's gate, reached through the one function that answers it. A number measured
    on data that never passed validation is not evidence anything may be approved against."""
    actor, model_id, dataset_id, _, _ = await _fitted_model(
        database, blob_store, workspace_id
    )
    draft_version = await _ingest(
        database, blob_store, workspace_id, actor, dataset_id, DETERIORATED
    )

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.request_backtest(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                dataset_version_id=draft_version,
            )
    assert refused.value.code == "DATASET_NOT_VALIDATED"


@pytest.mark.req("FR-MODEL-57")
async def test_a_version_missing_a_scored_column_is_refused_before_the_queue(
    database, blob_store, workspace_id
) -> None:
    """A later period that renamed a column is the ordinary way a backtest fails.

    Checked against the version's declared `arrow_schema` rather than by reading the
    parquet: the schema is what the version records about itself, and opening the file to
    answer a request is the cost this check exists to avoid.
    """
    _, model_id, _, _, _ = await _fitted_model(database, blob_store, workspace_id)

    async with database.session() as session:
        model = await session.get(ModelRow, model_id)
        spec = MODEL_SPEC_ADAPTER.validate_python(model.spec)
        factors = await model_service.load_factors(
            session, workspace_id=workspace_id, factor_ids=list(spec.factors)
        )
        version = await session.get(DatasetVersionRow, spec.dataset_version_id)

    # A version whose schema knows every column but `area` — the shape of a feed that
    # renamed a field between periods.
    without_area = DatasetVersionRow(
        id=uuid4(),
        workspace_id=workspace_id,
        dataset_id=version.dataset_id,
        version=99,
        status=version.status,
        tables=[
            {
                **version.tables[0],
                "arrow_schema": {
                    k: v
                    for k, v in (version.tables[0].get("arrow_schema") or {}).items()
                    if k != "area"
                },
            }
        ],
    )

    with pytest.raises(PlatformError) as refused:
        service.refuse_missing_columns(
            model=model, spec=spec, version=without_area, factors=factors
        )
    assert refused.value.status_code == 409
    assert "area" in (refused.value.detail or "")


# -- The artifact --------------------------------------------------------------------------


@pytest.mark.req("FR-DATA-42")
async def test_a_backtest_cannot_be_rewritten_at_either_layer(
    database, blob_store, workspace_id
) -> None:
    """**Both layers, and the trigger is the one that matters.**

    `a1b2c3d4e5f6` installed the trigger pattern and stated why privileges alone are not
    enough: revoking `UPDATE` from the *owner* does nothing, because ownership carries
    implicit privileges. The grants below are what stops the application; the `UPDATE` that
    follows is run as the owner and must still be refused.

    This was the first test in the repository to exercise an artifact table's trigger rather
    than only its grants, and writing it is what found FR-DATA-47: three tables with the
    grants and no trigger at all. `e1f2a3b4c5d6` closed that, and six tables rather than
    three — `backend/tests/test_artifact_immutability.py` now derives the list from the
    grants, so this test is no longer the only one of its kind.
    """
    async with database.session() as session:
        granted = (
            (
                await session.execute(
                    text(
                        "SELECT privilege_type FROM information_schema.table_privileges "
                        "WHERE table_name = 'backtests' AND grantee = 'gip_app'"
                    )
                )
            )
            .scalars()
            .all()
        )
    assert "INSERT" in granted
    assert "SELECT" in granted
    assert "UPDATE" not in granted
    assert "DELETE" not in granted

    backtest_id = await _run_backtest(database, blob_store, workspace_id)

    async with database.session() as session:
        with pytest.raises(Exception, match="append-only"):
            await session.execute(
                text("UPDATE backtests SET payload = '{}'::jsonb WHERE id = :i"),
                {"i": str(backtest_id)},
            )


async def _run_backtest(database: Database, blob_store, workspace_id: UUID) -> UUID:
    """Fit, ingest a later period, backtest — through the real Jobs, returning the id."""
    actor, model_id, dataset_id, _, _ = await _fitted_model(
        database, blob_store, workspace_id
    )
    later = await _later_period(database, blob_store, workspace_id, actor, dataset_id)

    async with database.unit_of_work() as session:
        model, version = await service.request_backtest(
            session,
            workspace_id=workspace_id,
            actor=actor,
            model_id=model_id,
            dataset_version_id=later,
        )
        job = await job_service.submit(
            session,
            JobKind.MODEL_BACKTEST,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                **service.backtest_payload(model, version),
            },
            actor,
            workspace_id=workspace_id,
        )
        job_id = job.id
    assert await execute_job(database, job_id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        return (
            await session.execute(select(BacktestRow.id).where(BacktestRow.job_id == job_id))
        ).scalar_one()


async def _later_residual_period(
    database: Database, blob_store, workspace_id: UUID, actor: Principal, dataset_id: UUID
) -> UUID:
    """A second validated version of the residual book — fresh draws under the same truth.

    `_later_period`'s convention, with the residual cast recipe: without the casts
    `resid_flag` arrives as a String column and the frame the backtest scores is not the
    one the fit's factors expect (`_RESIDUAL_CAST_RECIPE`, Task 5).
    """
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, _residual_book(seed=20260822), "text/csv")
        job = await job_service.submit(
            session,
            JobKind.DATASET_INGEST,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "dataset_id": str(dataset_id),
                "blob": ref.sha256,
                "filename": "exposure.csv",
                "recipe": _RESIDUAL_CAST_RECIPE,
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        version_id = (
            await session.execute(
                select(DatasetVersionRow.id)
                .where(DatasetVersionRow.dataset_id == dataset_id)
                .order_by(DatasetVersionRow.version.desc())
                .limit(1)
            )
        ).scalar_one()
    report_id = await _validate(database, blob_store, workspace_id, actor, version_id)
    from app.platform import validation as validation_service

    async with database.unit_of_work() as session:
        await validation_service.promote_using_report(
            session,
            workspace_id=workspace_id,
            actor=actor,
            version_id=version_id,
            report_id=report_id,
        )
    return version_id


async def _run_residual_backtest(
    database: Database, blob_store, workspace_id: UUID
) -> UUID:
    """Fit the base+residual pair, ingest a later residual period, backtest the residual
    model against it — through the real Jobs, returning the backtest id."""
    pair = await _fitted_residual_pair(database, blob_store, workspace_id)

    async with database.session() as session:
        v2 = await session.get(DatasetVersionRow, pair.v2_id)
    assert v2 is not None
    later = await _later_residual_period(
        database, blob_store, workspace_id, pair.actor, v2.dataset_id
    )

    async with database.unit_of_work() as session:
        model, version = await service.request_backtest(
            session,
            workspace_id=workspace_id,
            actor=pair.actor,
            model_id=pair.residual_id,
            dataset_version_id=later,
        )
        job = await job_service.submit(
            session,
            JobKind.MODEL_BACKTEST,
            {
                "workspace_id": str(workspace_id),
                "actor": pair.actor.model_dump(mode="json"),
                **service.backtest_payload(model, version),
            },
            pair.actor,
            workspace_id=workspace_id,
        )
        job_id = job.id
    assert await execute_job(database, job_id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        return (
            await session.execute(
                select(BacktestRow.id).where(BacktestRow.job_id == job_id)
            )
        ).scalar_one()


# -- The whole path -------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-57")
async def test_the_backtest_job_produces_a_readable_artifact(
    database, blob_store, workspace_id
) -> None:
    """Request, run, read — with a known answer rather than a non-null assertion.

    The model was fitted where rural carries half of urban's claims; the later period levels
    them up. So the overall A/E must exceed one, the *rural* cell must be the one carrying
    it, and the artifact must name both versions — which is what makes it evidence rather
    than a number.
    """
    backtest_id = await _run_backtest(database, blob_store, workspace_id)

    async with database.session() as session:
        stored = await service.load_backtest(
            session, workspace_id=workspace_id, backtest_id=backtest_id
        )

    assert stored.summary.model_ref.startswith("model:")
    assert stored.summary.dataset_version_ref != stored.summary.fitted_on_ref
    assert stored.summary.partition.rows == 400

    assert stored.summary.partition.ae_overall > 1.0, (
        "the later period doubled rural claims against a model that prices rural at half "
        "of urban; a backtest that did not move is one that scored the wrong frame"
    )
    rural = next(
        c for c in stored.summary.partition.ae_by_factor if c.level == "rural"
    )
    urban = next(
        c for c in stored.summary.partition.ae_by_factor if c.level == "urban"
    )
    assert rural.ae > urban.ae, (
        "the deterioration is entirely in the rural cell, and an A/E by level that could "
        "not localise it would be a table nobody could act on"
    )


@pytest.mark.req("FR-MODEL-24")
async def test_a_model_offset_backtest_honours_the_offset(
    database, blob_store, workspace_id
) -> None:
    """Request, run, read — the residual model's offset honoured on a period it never saw.

    The residual model's prediction is `exp(η_base + β̂·resid_flag)`: the referenced
    base model's linear predictor plus the residual fit's own terms (FR-MODEL-24). A
    backtest that drops the offset scores `exp(β̂·resid_flag)` alone, and a book whose
    claims sit at `exp(η_base + …)` then reads at A/E ≈ e² — which is what makes the
    ≈1.0 assertion discriminate the offset actually being honoured, not merely the job
    running. And without the wiring the job does not even run: `backtest_model` refuses
    a `kind="model"` spec that arrives without its array (`MODEL_OFFSET_MISSING`).
    """
    backtest_id = await _run_residual_backtest(database, blob_store, workspace_id)

    async with database.session() as session:
        stored = await service.load_backtest(
            session, workspace_id=workspace_id, backtest_id=backtest_id
        )

    assert stored.summary.model_ref.startswith("model:")
    assert stored.summary.dataset_version_ref != stored.summary.fitted_on_ref
    assert stored.summary.partition.rows == 4000
    assert stored.summary.partition.ae_overall == pytest.approx(1.0, abs=0.15)


@pytest.mark.req("FR-MODEL-57")
async def test_a_second_backtest_of_the_same_pair_is_refused_by_the_database(
    database, blob_store, workspace_id
) -> None:
    """One answer per (model, version). A second row would be a second answer to one
    question, with nothing to say which of the two a monitoring review cited."""
    backtest_id = await _run_backtest(database, blob_store, workspace_id)

    async with database.session() as session:
        row = await session.get(BacktestRow, backtest_id)
        model_id, version_id, payload = row.model_id, row.dataset_version_id, row.payload

    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        async with database.unit_of_work() as session:
            session.add(
                BacktestRow(
                    id=uuid4(),
                    workspace_id=workspace_id,
                    model_id=model_id,
                    dataset_version_id=version_id,
                    payload=payload,
                )
            )


# -- The published contract ----------------------------------------------------------------


@pytest.mark.req("FR-MODEL-92")
def test_both_backtest_routes_are_published() -> None:
    """The `GET` matters as much as the `POST`. §5.1 declared only the `POST`, and a 202
    whose artifact has no route is complete to the endpoint audit and unusable to a caller —
    the fourth artifact in `02` to need this repair."""
    paths = _load(OPENAPI)["paths"]
    assert "post" in paths["/api/v1/models/{model_id}/backtest"]
    assert "get" in paths["/api/v1/models/backtests/{backtest_id}"]
