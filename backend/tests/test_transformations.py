"""Bandings and Groupings through the platform (`02` §3.2, §3.3, §5.1).

What the maths does is `packages/pricing-core/tests`' subject. What this covers is the
governance around it, which is where a transformation stops being a statistic and becomes
an artifact a model can pin:

* **R1** — a proposal is derived against a `validated` version, or refused. Evidence
  (FR-MODEL-10) for a fit that cannot happen is worse than no evidence.
* **FR-MODEL-12 / FR-MODEL-16** — versioned, never edited, and audited on creation.
* **The fit that pins one** — a `banding` factor reaching `model.fit` must resolve through
  its stored Banding, which is only true if the handler loaded it.
"""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from backend.tests.test_model_jobs import (
    BOOK,
    _actuary,
    _dataset,
    _spec,
    _validated_version,
)
from sqlalchemy import select

from app.db.models import AuditEventRow, BandingRow, GroupingRow, ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import transformations as transform_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import (
    Banding,
    BandingMethod,
    BandingProposal,
    Factor,
    FactorType,
    GroupingMethod,
    GroupingProposal,
    JobKind,
    JobStatus,
    Principal,
    UnseenLevelBehaviour,
)

register_data_handlers()
register_model_handlers()

#: `BOOK` is 400 rows of `area` ∈ {urban, rural} with `exposure_years` 1.0 and claim counts
#: of 1 or 2. It carries no continuous column worth banding, so the banding tests band
#: `claim_amount_minor`, which takes exactly two values — enough for a two-band cut and
#: nothing more, which is why the boundaries below are manual.


async def _banding(
    database: Database, workspace_id: UUID, actor: Principal, dataset_id: UUID, **over: object
) -> Banding:
    base: dict[str, object] = {
        "id": uuid4(), "slug": f"amt-{uuid4().hex[-6:]}", "dataset_id": dataset_id,
        "version": 1, "column": "claim_amount_minor", "method": BandingMethod.MANUAL,
        "boundaries": (0.0, 150_000.0, 300_000.0), "labels": ("low", "high"),
    }
    base.update(over)
    banding = Banding(**base)  # type: ignore[arg-type]
    async with database.unit_of_work() as session:
        row = await transform_service.create_banding(
            session, workspace_id=workspace_id, actor=actor, banding=banding
        )
        return transform_service.to_banding(row)


@pytest.mark.req("FR-MODEL-12")
async def test_a_second_banding_of_one_slug_allocates_the_next_version(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-12: editing a banding creates a new version and alters no fitted model."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    slug = f"amt-{uuid4().hex[-6:]}"

    first = await _banding(database, workspace_id, actor, dataset_id, slug=slug)
    second = await _banding(
        database, workspace_id, actor, dataset_id, slug=slug,
        boundaries=(0.0, 120_000.0, 300_000.0), labels=("low", "high"),
    )

    assert (first.version, second.version) == (1, 2)
    assert first.id != second.id
    # The first is untouched: a model that pinned it still describes what it did.
    async with database.session() as session:
        stored = await session.get(BandingRow, first.id)
        assert stored is not None
        assert tuple(stored.body["boundaries"]) == (0.0, 150_000.0, 300_000.0)


@pytest.mark.req("FR-MODEL-16")
async def test_creating_a_grouping_emits_an_audit_event(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-16 makes it auditable because grouping is a modelling decision.

    The event carries the method and the level counts, so the model document can list the
    grouping with its method without re-reading the artifact.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    slug = f"area-{uuid4().hex[-6:]}"

    from model_schema import Grouping

    async with database.unit_of_work() as session:
        await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=Grouping(
                id=uuid4(), slug=slug, dataset_id=dataset_id, version=1, column="area",
                method=GroupingMethod.MANUAL,
                mapping={"urban": "ALL", "rural": "ALL"},
                unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
            ),
        )

    async with database.session() as session:
        event = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.entity_ref == f"grouping:{slug}@1",
                )
            )
        ).scalar_one()
    assert event.action == "grouping.created"
    assert event.after["method"] == "manual"
    assert event.after["source_levels"] == 2
    assert event.after["target_levels"] == 1
    assert event.after["unseen_level_behaviour"] == "error"


@pytest.mark.req("FR-MODEL-9")
async def test_a_proposal_needs_a_validated_version(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """`02` R1 again, one layer out.

    Bands proposed from a draft version carry FR-MODEL-10 evidence for a fit the platform
    has already refused — and the numbers would look exactly as authoritative.
    """
    from backend.tests.test_data_jobs import _ingest

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    draft = await _ingest(database, blob_store, workspace_id, actor, dataset_id, BOOK)

    with pytest.raises(PlatformError) as refused:
        async with database.session() as session:
            await transform_service.propose_banding_for_version(
                session,
                workspace_id=workspace_id,
                actor=actor,
                blob_store=blob_store,
                proposal=BandingProposal(
                    dataset_version_id=draft,
                    column="claim_amount_minor",
                    method=BandingMethod.QUANTILE,
                    n_bands=2,
                ),
                slug="amt",
            )
    assert refused.value.code == "DATASET_NOT_VALIDATED"


@pytest.mark.req("FR-MODEL-9")
async def test_a_proposal_reads_the_version_and_persists_nothing(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-9: the platform proposes, the actuary edits, and nothing is stored yet."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )

    async with database.session() as session:
        proposed = await transform_service.propose_banding_for_version(
            session,
            workspace_id=workspace_id,
            actor=actor,
            blob_store=blob_store,
            proposal=BandingProposal(
                dataset_version_id=version_id,
                column="claim_amount_minor",
                method=BandingMethod.QUANTILE,
                n_bands=2,
            ),
            slug="amt-proposed",
        )

    assert proposed.derived_on_dataset_version_id == version_id
    assert proposed.band_stats, "FR-MODEL-10: a proposal carries its evidence"

    async with database.session() as session:
        stored = (
            await session.execute(
                select(BandingRow).where(BandingRow.workspace_id == workspace_id)
            )
        ).scalars().all()
    assert stored == [], "proposing is not persisting"


@pytest.mark.req("FR-MODEL-14")
async def test_a_grouping_proposal_carries_its_change_in_fit(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-15's evidence, from the real read path rather than a fixture frame."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )

    async with database.session() as session:
        proposed = await transform_service.propose_grouping_for_version(
            session,
            workspace_id=workspace_id,
            actor=actor,
            blob_store=blob_store,
            proposal=GroupingProposal(
                dataset_version_id=version_id,
                column="area",
                method=GroupingMethod.HIERARCHICAL_CLUSTERING,
                n_groups=1,
                unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
            ),
            slug="area-1",
        )

    assert proposed.evidence is not None
    assert proposed.evidence.source_level_count == 2
    assert proposed.evidence.target_level_count == 1
    assert proposed.evidence.df_saved == 1
    # Urban carries twice the frequency of rural, so collapsing them costs real deviance
    # and the p-value must say so.
    assert proposed.evidence.chi2_p_value is not None
    assert proposed.evidence.chi2_p_value < 0.01


@pytest.mark.req("FR-MODEL-83")
async def test_evaluating_edited_boundaries_moves_the_band_statistics(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-83: what an edited boundary *did*, before the banding is saved.

    The assertion that matters is that the numbers **change with the cut**. A stub that
    echoed the request, or one that recomputed against the wrong column, would return
    plausible statistics for both bandings — so the test compares two cuts of the same
    column and requires them to disagree, and requires each to reconcile with its own rows.
    """
    from model_schema import BandingEvaluation

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )

    async def _stats(cut: float) -> dict[str, tuple[float, int]]:
        banding = Banding(
            id=uuid4(), slug="amt", dataset_id=dataset_id, version=1,
            column="claim_amount_minor", method=BandingMethod.MANUAL,
            boundaries=(0.0, cut, 300_000.0), labels=("low", "high"),
        )
        async with database.session() as session:
            evaluated = await transform_service.evaluate_banding_for_version(
                session,
                workspace_id=workspace_id,
                actor=actor,
                blob_store=blob_store,
                evaluation=BandingEvaluation(
                    dataset_version_id=version_id, banding=banding
                ),
            )
        assert evaluated.derived_on_dataset_version_id == version_id
        return {
            row.level: (float(row.exposure_years), row.claim_count)
            for row in evaluated.band_stats
        }

    # `BOOK` puts 100 000 minor units on three quarters of the rows and 200 000 on the rest.
    # A cut at 150 000 splits them; a cut at 250 000 puts everything in `low`.
    split = await _stats(150_000.0)
    lumped = await _stats(250_000.0)

    assert set(split) == {"low", "high"}
    assert split["low"][1] > 0
    assert split["high"][1] > 0
    assert set(lumped) == {"low"}, "moving the cut past every value empties the top band"
    assert split != lumped, "the statistics must follow the boundary, not the request"


@pytest.mark.req("FR-MODEL-83")
async def test_evaluating_an_edited_mapping_moves_the_evidence(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """`02` §5.3: merging levels shows the deviance/df trade-off before it is saved.

    Urban carries twice the frequency of rural in `BOOK`, so collapsing them costs real
    deviance and the p-value has to say so — while mapping each to its own target costs
    nothing and must not.
    """
    from model_schema import Grouping, GroupingEvaluation

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )

    async def _evidence(mapping: dict[str, str]):
        grouping = Grouping(
            id=uuid4(), slug="area", dataset_id=dataset_id, version=1, column="area",
            method=GroupingMethod.MANUAL, mapping=mapping,
            unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
        )
        async with database.session() as session:
            evaluated = await transform_service.evaluate_grouping_for_version(
                session,
                workspace_id=workspace_id,
                actor=actor,
                blob_store=blob_store,
                evaluation=GroupingEvaluation(
                    dataset_version_id=version_id, grouping=grouping
                ),
            )
        assert evaluated.evidence is not None
        return evaluated.evidence

    collapsed = await _evidence({"urban": "ALL", "rural": "ALL"})
    kept = await _evidence({"urban": "U", "rural": "R"})

    assert collapsed.target_level_count == 1
    assert collapsed.df_saved == 1
    assert collapsed.chi2_p_value is not None
    assert collapsed.chi2_p_value < 0.01, "merging two genuinely different rates is not free"

    assert kept.target_level_count == 2
    assert kept.df_saved == 0
    assert kept.chi2_p_value is None, "no degrees of freedom saved, so no test to report"


@pytest.mark.req("FR-MODEL-83")
async def test_evaluating_needs_a_validated_version_too(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """R1 does not stop applying because the caller is only previewing."""
    from backend.tests.test_data_jobs import _ingest

    from model_schema import BandingEvaluation

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    draft = await _ingest(database, blob_store, workspace_id, actor, dataset_id, BOOK)

    with pytest.raises(PlatformError) as refused:
        async with database.session() as session:
            await transform_service.evaluate_banding_for_version(
                session,
                workspace_id=workspace_id,
                actor=actor,
                blob_store=blob_store,
                evaluation=BandingEvaluation(
                    dataset_version_id=draft,
                    banding=Banding(
                        id=uuid4(), slug="amt", dataset_id=dataset_id, version=1,
                        column="claim_amount_minor", method=BandingMethod.MANUAL,
                        boundaries=(0.0, 150_000.0, 300_000.0), labels=("low", "high"),
                    ),
                ),
            )
    assert refused.value.code == "DATASET_NOT_VALIDATED"


@pytest.mark.req("FR-MODEL-83")
async def test_evaluating_persists_nothing(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """A preview that quietly saved would make every dragged boundary a stored version."""
    from model_schema import BandingEvaluation

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )

    async with database.session() as session:
        await transform_service.evaluate_banding_for_version(
            session,
            workspace_id=workspace_id,
            actor=actor,
            blob_store=blob_store,
            evaluation=BandingEvaluation(
                dataset_version_id=version_id,
                banding=Banding(
                    id=uuid4(), slug="amt", dataset_id=dataset_id, version=1,
                    column="claim_amount_minor", method=BandingMethod.MANUAL,
                    boundaries=(0.0, 150_000.0, 300_000.0), labels=("low", "high"),
                ),
            ),
        )

    async with database.session() as session:
        stored = (
            await session.execute(
                select(BandingRow).where(BandingRow.workspace_id == workspace_id)
            )
        ).scalars().all()
    assert stored == []


@pytest.mark.req("FR-MODEL-8")
async def test_a_model_fits_through_a_stored_banding(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The whole seam, end to end: a `banding` factor resolves through its stored artifact.

    The handler has to load the Banding the factor pins — `pricing-core` cannot, and it
    refuses rather than falling back to the raw column, so a handler that forgot would fail
    the job rather than fit the wrong model.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    banding = await _banding(database, workspace_id, actor, dataset_id)

    async with database.unit_of_work() as session:
        factor_row = await model_service.create_factor(
            session,
            workspace_id=workspace_id,
            actor=actor,
            factor=Factor(
                id=uuid4(), slug=f"amt-banded-{uuid4().hex[-6:]}", dataset_id=dataset_id,
                version=1, type=FactorType.BANDING,
                source_columns=("claim_amount_minor",), banding_id=banding.id,
            ),
        )
        factor_id = factor_row.id

    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (factor_id,)),
        )
        assert should_fit is True
        model_id = row.id
        job = await job_service.submit(
            session, JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor, workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, model_id))

    assert model.fit_result is not None
    table = next(iter(model.fit_result.relativities.values()))
    assert {level.level for level in table} == {"low", "high"}, (
        "the fit saw the bands, not the raw amounts"
    )


@pytest.mark.req("FR-MODEL-2")
async def test_a_fit_naming_a_banding_that_does_not_exist_fails_the_job(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """A dangling reference is a `404` naming the id, not a fit on the raw column."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )

    async with database.unit_of_work() as session:
        factor_row = await model_service.create_factor(
            session,
            workspace_id=workspace_id,
            actor=actor,
            factor=Factor(
                id=uuid4(), slug=f"ghost-{uuid4().hex[-6:]}", dataset_id=dataset_id,
                version=1, type=FactorType.BANDING,
                source_columns=("claim_amount_minor",), banding_id=uuid4(),
            ),
        )
        factor_id = factor_row.id

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (factor_id,)),
        )
        job = await job_service.submit(
            session, JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(row.id)},
            actor, workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.FAILED


@pytest.mark.req("FR-MODEL-12")
async def test_a_stored_banding_cannot_be_updated_or_deleted(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The privilege layer, not the service layer.

    FR-MODEL-12 holds for callers who remember it; this is what holds for a psql session.
    """
    from sqlalchemy import text

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    banding = await _banding(database, workspace_id, actor, dataset_id)

    async with database.session() as session:
        await session.execute(text("SET LOCAL ROLE gip_app"))
        with pytest.raises(Exception, match=r"permission denied|InsufficientPrivilege"):
            await session.execute(
                text("UPDATE bandings SET slug = 'rewritten' WHERE id = :i"),
                {"i": banding.id},
            )

    async with database.session() as session:
        await session.execute(text("SET LOCAL ROLE gip_app"))
        with pytest.raises(Exception, match=r"permission denied|InsufficientPrivilege"):
            await session.execute(
                text("DELETE FROM bandings WHERE id = :i"), {"i": banding.id}
            )


@pytest.mark.req("FR-MODEL-13")
async def test_groupings_and_bandings_list_by_dataset(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    other = await _dataset(database, blob_store, workspace_id, actor)
    mine = await _banding(database, workspace_id, actor, dataset_id)
    await _banding(database, workspace_id, actor, other)

    async with database.session() as session:
        rows = await transform_service.list_bandings(
            session, workspace_id=workspace_id, dataset_id=dataset_id
        )
    assert [row.id for row in rows] == [mine.id]


@pytest.mark.req("FR-MODEL-2")
async def test_loading_a_banding_that_does_not_exist_names_the_id(
    database: Database, workspace_id
) -> None:
    missing = uuid4()
    with pytest.raises(PlatformError) as refused:
        async with database.session() as session:
            await transform_service.load_bandings(
                session, workspace_id=workspace_id, ids=[missing]
            )
    assert refused.value.code == "NOT_FOUND"
    assert str(missing) in (refused.value.detail or "")


@pytest.mark.req("FR-MODEL-14")
async def test_a_grouping_row_records_its_parent_for_a_hierarchy(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-17's chain, stored as a column so it is queryable rather than only in JSON."""
    from model_schema import Grouping

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    parent_id = uuid4()

    async with database.unit_of_work() as session:
        row = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=Grouping(
                id=uuid4(), slug=f"area-{uuid4().hex[-6:]}", dataset_id=dataset_id,
                version=1, column="area", method=GroupingMethod.MANUAL,
                mapping={"urban": "ALL", "rural": "ALL"},
                unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
                parent_grouping_id=parent_id,
            ),
        )
        stored_id = row.id

    async with database.session() as session:
        stored = await session.get(GroupingRow, stored_id)
        assert stored is not None
        assert stored.parent_grouping_id == parent_id
        assert transform_service.to_grouping(stored).parent_grouping_id == parent_id
