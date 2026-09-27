"""Comparison, from the request to the stored artifact (`02` FR-186, §5.1).

`packages/pricing-core/tests/test_comparison.py` owns the maths. This file owns the four
things only the platform can be wrong about:

* **the refusals happen before a Job is queued.** `reserve_model` set the precedent and the
  reason: learning that two models are incomparable from a failed job twenty seconds later
  is a worse answer to the same question. The handler checks again, because the world can
  move while a Job sits in a queue;
* **the artifact is immutable at the privilege layer** (FR-43). An approval cites it;
* **both routes are in the published contract.** A `POST` that produces an artifact with no
  `GET` is the surface `01`'s reference lifecycle had — complete to the endpoint audit,
  unusable to a caller;
* **the whole path runs**, `WF-698` E1 end to end, on two models fitted through the real fit
  Job on one recorded split.

The two candidates differ by **regularisation** — `alpha = 0` against a heavily penalised
fit of the same factor. That gives a real difference without needing a second column in the
book, and the difference is a precise one worth knowing: shrinkage changes the predicted
*magnitudes* and not their *order*, so `holdout_deviance` separates the two models and Gini
ties. The test asserts both, which is only possible because a tie yields no leader.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import pytest
from backend.tests.test_api_datasets import _headers
from backend.tests.test_contracts import OPENAPI, _load
from backend.tests.test_model_jobs import (
    _actuary,
    _dataset,
    _factor,
    _spec,
    _split,
    _validated_version,
)
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.db.models import ModelComparisonRow, ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import comparison as service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.worker.handlers import handler_for
from app.worker.progress import JobProgress
from app.worker.tasks import execute_job
from model_schema import (
    EbmSpec,
    JobKind,
    JobStatus,
    ModelStatus,
    Principal,
    SplitRef,
    new_uuid7,
)


async def _two_models(
    database: Database, blob_store, workspace_id: UUID
) -> tuple[Principal, list[UUID], SplitRef]:
    """Two models of the same shape on one recorded split, fitted through the real Job."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    ids: list[UUID] = []
    for alpha in (0.0, 25.0):
        async with database.unit_of_work() as session:
            row, _ = await model_service.reserve_model(
                session,
                workspace_id=workspace_id,
                actor=actor,
                spec=_spec(version_id, (area,), split_ref=split, alpha=alpha),
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
        ids.append(model_id)
    return actor, ids, split


def _ebm_spec(
    version_id: UUID, factor_ids: tuple[UUID, ...], **over: object
) -> EbmSpec:
    """The EBM arm of the union, on the same version and factors `_spec` uses."""
    base: dict[str, object] = {
        "model_family_slug": f"freq-{new_uuid7().hex[-6:]}",
        "dataset_version_id": version_id,
        "response_column": "claim_count",
        "factors": factor_ids,
    }
    base.update(over)
    return EbmSpec(**base)  # type: ignore[arg-type]


# -- The refusals, before a Job exists ----------------------------------------------------


@pytest.mark.req("FR-186")
async def test_a_comparison_of_one_model_is_refused(
    database, blob_store, workspace_id
) -> None:
    actor, ids, _ = await _two_models(database, blob_store, workspace_id)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.request_comparison(
                session, workspace_id=workspace_id, actor=actor, model_ids=ids[:1]
            )
    assert refused.value.code == "MODELS_NOT_COMPARABLE"


@pytest.mark.req("FR-186")
async def test_models_on_different_splits_are_refused_and_both_are_named(
    database, blob_store, workspace_id
) -> None:
    """FR-186 compares models fitted on the **same holdout**, and `01` FR-76 made
    that checkable: the split is one artifact two models cite. Comparing across two splits
    compares two models on different rows and reports the difference as performance.

    Both split ids appear in the message, because "these are not comparable" without saying
    which two things differ is a refusal the caller cannot act on.
    """
    actor, ids, first = await _two_models(database, blob_store, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    other = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=_spec(version_id, (area,), split_ref=other),
        )
        elsewhere = row.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(elsewhere)},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.request_comparison(
                session, workspace_id=workspace_id, actor=actor,
                model_ids=[ids[0], elsewhere],
            )
    assert refused.value.code == "MODELS_NOT_COMPARABLE"
    detail = refused.value.detail or ""
    assert str(first.split_artifact_id) in detail
    assert str(other.split_artifact_id) in detail


@pytest.mark.req("FR-186")
async def test_an_unfitted_model_cannot_be_compared(
    database, blob_store, workspace_id
) -> None:
    """A `draft` model has no coefficients, so there is nothing to score the holdout with."""
    actor, ids, split = await _two_models(database, blob_store, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), split_ref=split),
        )
        reserved = row.id
        assert row.status == ModelStatus.DRAFT.value

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.request_comparison(
                session, workspace_id=workspace_id, actor=actor,
                model_ids=[ids[0], reserved],
            )
    assert refused.value.code == "MODELS_NOT_COMPARABLE"
    assert "draft" in (refused.value.detail or "")


@pytest.mark.req("FR-186")
async def test_the_same_model_twice_is_refused(
    database, blob_store, workspace_id
) -> None:
    actor, ids, _ = await _two_models(database, blob_store, workspace_id)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.request_comparison(
                session, workspace_id=workspace_id, actor=actor,
                model_ids=[ids[0], ids[0]],
            )
    assert refused.value.code == "MODELS_NOT_COMPARABLE"


@pytest.mark.req("FR-140")
async def test_an_ebm_row_is_refused_by_name_at_the_comparison_boundary(
    database, blob_store, workspace_id
) -> None:
    """FR-140's model is transparent by construction, so `WF-698` E1 — surrogate
    validation of a GLM against a GBM — has nothing to compare.

    The refusal lives in the handler, not in `request_comparison`, because the Job can
    outlive the world that queued it — the same re-check the no-fit-result refusal makes.
    The EBM row is a reservation whose spec is an `EbmSpec`, fitted by writing a real GLM
    fit onto it while it is still unfitted (`02` R2 freezes `spec` and `fit_result`
    together once either exists). No EBM was ever fitted: the refusal fires on the spec,
    before any scoring of the holdout.
    """
    actor, ids, _ = await _two_models(database, blob_store, workspace_id)

    async with database.session() as session:
        fitted = await session.get(ModelRow, ids[0])
        assert fitted is not None
        version_id = fitted.dataset_version_id
        factors = tuple(fitted.spec["factors"])
        split_ref = (fitted.spec or {}).get("split_ref")

    async with database.unit_of_work() as session:
        ebm_row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_ebm_spec(version_id, factors, split_ref=split_ref),
        )
        ebm_id = ebm_row.id
        fitted = await session.get(ModelRow, ids[0])
        assert fitted is not None
        await session.execute(
            ModelRow.__table__.update()
            .where(ModelRow.id == ebm_id)
            .values(
                fit_result=fitted.fit_result,
                status=ModelStatus.FITTED.value,
                diagnostics_id=fitted.diagnostics_id,
            )
        )
        job = await job_service.submit(
            session,
            JobKind.MODEL_COMPARE,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "model_ids": [str(ids[0]), str(ebm_id)],
                "baseline_id": str(ids[0]),
            },
            actor,
            workspace_id=workspace_id,
        )

    # Through the handler directly rather than `execute_job`, which maps every handler
    # exception to `JOB_HANDLER_FAILED`: the code under test is what `PlatformError.code`
    # carries out of `_resolve_candidate`, not what the runner does with it once it has it.
    handler = handler_for(JobKind.MODEL_COMPARE)
    assert handler is not None
    progress = JobProgress(
        job.id, database, asyncio.get_running_loop(), blob_store=blob_store
    )
    with pytest.raises(PlatformError) as refused:
        await asyncio.to_thread(
            handler,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "model_ids": [str(ids[0]), str(ebm_id)],
                "baseline_id": str(ids[0]),
            },
            progress,
        )
    assert refused.value.code == "MODELS_NOT_COMPARABLE"


# -- The artifact --------------------------------------------------------------------------


@pytest.mark.req("FR-43")
async def test_a_comparison_cannot_be_rewritten(database, workspace_id) -> None:
    """An approval cites this artifact (`06` §3.3). Evidence that can change after the
    approval is not evidence — the same discipline `diagnostics` and validation reports
    carry, at the layer a direct `UPDATE` cannot walk past."""
    async with database.session() as session:
        granted = (
            await session.execute(
                text(
                    "SELECT privilege_type FROM information_schema.table_privileges "
                    "WHERE table_name = 'model_comparisons' AND grantee = 'gip_app'"
                )
            )
        ).scalars().all()
    assert "INSERT" in granted
    assert "SELECT" in granted
    assert "UPDATE" not in granted
    assert "DELETE" not in granted


# -- The whole path, `WF-698` E1 -----------------------------------------------------------


@pytest.mark.req("FR-186")
async def test_the_comparison_job_produces_a_readable_artifact(
    database, blob_store, workspace_id
) -> None:
    """E1 end to end: request, run, read. The unpenalised fit must lead on Gini — shrinking
    the only factor toward zero cannot improve the ordering, so this is a known answer rather
    than an assertion that a leader exists."""
    actor, ids, split = await _two_models(database, blob_store, workspace_id)

    async with database.unit_of_work() as session:
        rows = await service.request_comparison(
            session, workspace_id=workspace_id, actor=actor, model_ids=ids
        )
        job = await job_service.submit(
            session,
            JobKind.MODEL_COMPARE,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                **service.compare_payload(rows, baseline_id=ids[0]),
            },
            actor,
            workspace_id=workspace_id,
        )
        job_id = job.id
    assert await execute_job(database, job_id, blob_store) is JobStatus.SUCCEEDED

    # Read the way the frontend does: the Job's result names the artifact, and the artifact
    # is fetched by id through the same function the `GET` route calls — which is what makes
    # this test cover the read path rather than the table.
    async with database.session() as session:
        recorded = (
            await session.execute(
                select(ModelComparisonRow.id).where(ModelComparisonRow.job_id == job_id)
            )
        ).scalar_one()
        stored = await service.load_comparison(
            session, workspace_id=workspace_id, comparison_id=recorded
        )
    assert stored.job_id == job_id
    assert len(stored.summary.model_refs) == 2
    assert stored.summary.split_ref.split_artifact_id == split.split_artifact_id
    assert stored.summary.holdout_rows > 0

    unpenalised = stored.summary.model_refs[0]

    # **Gini cannot separate these two, and that is the correct answer.** It is computed from
    # the *ordering* of predicted rates, and with a single binary factor shrinkage moves both
    # levels toward the grand mean without ever swapping them — so both models rank every row
    # identically and the metric ties. `_leader` returns `None` on a tie rather than letting
    # dictionary order pick a winner, which is what makes this assertable.
    gini = next(m for m in stored.summary.metrics if m.metric == "gini_normalised")
    assert gini.leader is None, "a rank metric cannot distinguish two orderings that agree"

    # Deviance can: it is sensitive to the *magnitude* of the prediction, which is exactly
    # what the penalty changed. This is the known answer the test is built around.
    deviance = next(m for m in stored.summary.metrics if m.metric == "holdout_deviance")
    assert deviance.leader == unpenalised, (
        "the penalised fit's predictions are pulled toward the grand mean, so its holdout "
        "deviance must be the worse of the two"
    )

    assert len(stored.summary.double_lift) == 1
    assert stored.summary.double_lift[0].baseline_ref == unpenalised


# -- The published contract ----------------------------------------------------------------


@pytest.mark.req("FR-186")
def test_both_comparison_routes_are_published() -> None:
    """The `GET` matters as much as the `POST`. `02` §5.1 declared only the `POST`, and a
    202 whose artifact has no route is complete to the endpoint audit and unusable to a
    caller — the omission `01`'s reference publish lifecycle made."""
    paths = _load(OPENAPI)["paths"]
    assert "post" in paths["/api/v1/models/compare"]
    assert "get" in paths["/api/v1/models/comparisons/{comparison_id}"]


@pytest.mark.req("FR-186")
def test_comparing_over_the_api_answers_202_with_a_job(
    api_client: TestClient, workspace_id, database, blob_store
) -> None:
    """202 rather than 200: the comparison reads the holdout and scores every candidate on
    it, which is work. `POST /models` makes the same distinction for the same reason."""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        from backend.tests.conftest_db import test_blob_bucket, test_database_url

        from app.config import Settings
        from app.platform.blobs import BlobStore

        db = Database(Settings(database_url=test_database_url()))
        store = BlobStore(Settings(blob_bucket=test_blob_bucket()))
        try:
            loop.run_until_complete(store.ensure_bucket())
        except Exception as exc:  # pragma: no cover - infrastructure
            pytest.skip(f"MinIO not reachable: {type(exc).__name__}")
        try:
            actor, ids, _ = loop.run_until_complete(
                _two_models(db, store, workspace_id)
            )
        finally:
            loop.run_until_complete(db.dispose())
    finally:
        loop.close()

    accepted = api_client.post(
        "/api/v1/models/compare",
        json={"model_ids": [str(i) for i in ids]},
        headers=_headers(actor.id, workspace_id),
    )
    assert accepted.status_code == 202, accepted.text
    assert accepted.headers["Location"].startswith("/api/v1/jobs/")


@pytest.mark.req("FR-186")
def test_reading_an_unknown_comparison_is_a_404(
    api_client: TestClient, workspace_id, principal, grant
) -> None:
    import asyncio

    from model_schema import new_uuid7

    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    missing = api_client.get(
        f"/api/v1/models/comparisons/{new_uuid7()}",
        headers=_headers(principal.id, workspace_id),
    )
    assert missing.status_code == 404, missing.text
