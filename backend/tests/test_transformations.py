"""Bandings and Groupings through the platform (`02` §3.2, §3.3, §5.1).

What the maths does is `packages/pricing-core/tests`' subject. What this covers is the
governance around it, which is where a transformation stops being a statistic and becomes
an artifact a model can pin:

* **R1** — a proposal is derived against a `validated` version, or refused. Evidence
  (FR-99) for a fit that cannot happen is worse than no evidence.
* **FR-101 / FR-108** — versioned, never edited, and audited on creation.
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
    _split,
    _validated_version,
)
from sqlalchemy import select

from app.db.models import AuditEventRow, BandingRow, GroupingRow, JobRow, ModelRow
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
    Grouping,
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
        "id": uuid4(),
        "slug": f"amt-{uuid4().hex[-6:]}",
        "dataset_id": dataset_id,
        "version": 1,
        "column": "claim_amount_minor",
        "method": BandingMethod.MANUAL,
        "boundaries": (0.0, 150_000.0, 300_000.0),
        "labels": ("low", "high"),
    }
    base.update(over)
    banding = Banding(**base)  # type: ignore[arg-type]
    async with database.unit_of_work() as session:
        row = await transform_service.create_banding(
            session, workspace_id=workspace_id, actor=actor, banding=banding
        )
        return transform_service.to_banding(row)


@pytest.mark.req("FR-101")
async def test_a_second_banding_of_one_slug_allocates_the_next_version(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-101: editing a banding creates a new version and alters no fitted model."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    slug = f"amt-{uuid4().hex[-6:]}"

    first = await _banding(database, workspace_id, actor, dataset_id, slug=slug)
    second = await _banding(
        database,
        workspace_id,
        actor,
        dataset_id,
        slug=slug,
        boundaries=(0.0, 120_000.0, 300_000.0),
        labels=("low", "high"),
    )

    assert (first.version, second.version) == (1, 2)
    assert first.id != second.id
    # The first is untouched: a model that pinned it still describes what it did.
    async with database.session() as session:
        stored = await session.get(BandingRow, first.id)
        assert stored is not None
        assert tuple(stored.body["boundaries"]) == (0.0, 150_000.0, 300_000.0)


@pytest.mark.req("FR-108")
async def test_creating_a_grouping_emits_an_audit_event(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-108 makes it auditable because grouping is a modelling decision.

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
                id=uuid4(),
                slug=slug,
                dataset_id=dataset_id,
                version=1,
                column="area",
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


@pytest.mark.req("FR-98")
async def test_a_proposal_needs_a_validated_version(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """`02` R1 again, one layer out.

    Bands proposed from a draft version carry FR-99 evidence for a fit the platform
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


@pytest.mark.req("FR-98")
async def test_a_proposal_reads_the_version_and_persists_nothing(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-98: the platform proposes, the actuary edits, and nothing is stored yet."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(database, blob_store, workspace_id, actor, dataset_id)

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
    assert proposed.band_stats, "FR-99: a proposal carries its evidence"

    async with database.session() as session:
        stored = (
            (
                await session.execute(
                    select(BandingRow).where(BandingRow.workspace_id == workspace_id)
                )
            )
            .scalars()
            .all()
        )
    assert stored == [], "proposing is not persisting"


@pytest.mark.req("FR-105")
async def test_a_grouping_proposal_carries_its_change_in_fit(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-107's evidence, from the real read path rather than a fixture frame."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(database, blob_store, workspace_id, actor, dataset_id)

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


@pytest.mark.req("FR-102")
async def test_evaluating_edited_boundaries_moves_the_band_statistics(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-102: what an edited boundary *did*, before the banding is saved.

    The assertion that matters is that the numbers **change with the cut**. A stub that
    echoed the request, or one that recomputed against the wrong column, would return
    plausible statistics for both bandings — so the test compares two cuts of the same
    column and requires them to disagree, and requires each to reconcile with its own rows.
    """
    from model_schema import BandingEvaluation

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(database, blob_store, workspace_id, actor, dataset_id)

    async def _stats(cut: float) -> dict[str, tuple[float, int]]:
        banding = Banding(
            id=uuid4(),
            slug="amt",
            dataset_id=dataset_id,
            version=1,
            column="claim_amount_minor",
            method=BandingMethod.MANUAL,
            boundaries=(0.0, cut, 300_000.0),
            labels=("low", "high"),
        )
        async with database.session() as session:
            evaluated = await transform_service.evaluate_banding_for_version(
                session,
                workspace_id=workspace_id,
                actor=actor,
                blob_store=blob_store,
                evaluation=BandingEvaluation(dataset_version_id=version_id, banding=banding),
            )
        assert evaluated.derived_on_dataset_version_id == version_id
        return {
            row.level: (float(row.exposure_years), row.claim_count) for row in evaluated.band_stats
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


@pytest.mark.req("FR-102")
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
    version_id = await _validated_version(database, blob_store, workspace_id, actor, dataset_id)

    async def _evidence(mapping: dict[str, str]):
        grouping = Grouping(
            id=uuid4(),
            slug="area",
            dataset_id=dataset_id,
            version=1,
            column="area",
            method=GroupingMethod.MANUAL,
            mapping=mapping,
            unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
        )
        async with database.session() as session:
            evaluated = await transform_service.evaluate_grouping_for_version(
                session,
                workspace_id=workspace_id,
                actor=actor,
                blob_store=blob_store,
                evaluation=GroupingEvaluation(dataset_version_id=version_id, grouping=grouping),
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


@pytest.mark.req("FR-102")
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
                        id=uuid4(),
                        slug="amt",
                        dataset_id=dataset_id,
                        version=1,
                        column="claim_amount_minor",
                        method=BandingMethod.MANUAL,
                        boundaries=(0.0, 150_000.0, 300_000.0),
                        labels=("low", "high"),
                    ),
                ),
            )
    assert refused.value.code == "DATASET_NOT_VALIDATED"


@pytest.mark.req("FR-102")
async def test_evaluating_persists_nothing(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """A preview that quietly saved would make every dragged boundary a stored version."""
    from model_schema import BandingEvaluation

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(database, blob_store, workspace_id, actor, dataset_id)

    async with database.session() as session:
        await transform_service.evaluate_banding_for_version(
            session,
            workspace_id=workspace_id,
            actor=actor,
            blob_store=blob_store,
            evaluation=BandingEvaluation(
                dataset_version_id=version_id,
                banding=Banding(
                    id=uuid4(),
                    slug="amt",
                    dataset_id=dataset_id,
                    version=1,
                    column="claim_amount_minor",
                    method=BandingMethod.MANUAL,
                    boundaries=(0.0, 150_000.0, 300_000.0),
                    labels=("low", "high"),
                ),
            ),
        )

    async with database.session() as session:
        stored = (
            (
                await session.execute(
                    select(BandingRow).where(BandingRow.workspace_id == workspace_id)
                )
            )
            .scalars()
            .all()
        )
    assert stored == []


@pytest.mark.req("FR-97")
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
    version_id = await _validated_version(database, blob_store, workspace_id, actor, dataset_id)
    banding = await _banding(database, workspace_id, actor, dataset_id)

    async with database.unit_of_work() as session:
        factor_row = await model_service.create_factor(
            session,
            workspace_id=workspace_id,
            actor=actor,
            factor=Factor(
                id=uuid4(),
                slug=f"amt-banded-{uuid4().hex[-6:]}",
                dataset_id=dataset_id,
                version=1,
                type=FactorType.BANDING,
                source_columns=("claim_amount_minor",),
                banding_id=banding.id,
            ),
        )
        factor_id = factor_row.id

    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=_spec(version_id, (factor_id,), split_ref=split),
        )
        assert should_fit is True
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

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, model_id))

    assert model.fit_result is not None
    table = next(iter(model.fit_result.relativities.values()))
    assert {level.level for level in table} == {"low", "high"}, (
        "the fit saw the bands, not the raw amounts"
    )


@pytest.mark.req("FR-87")
async def test_a_fit_naming_a_banding_that_does_not_exist_fails_the_job(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """A dangling reference is a `404` naming the id, not a fit on the raw column."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(database, blob_store, workspace_id, actor, dataset_id)

    async with database.unit_of_work() as session:
        factor_row = await model_service.create_factor(
            session,
            workspace_id=workspace_id,
            actor=actor,
            factor=Factor(
                id=uuid4(),
                slug=f"ghost-{uuid4().hex[-6:]}",
                dataset_id=dataset_id,
                version=1,
                type=FactorType.BANDING,
                source_columns=("claim_amount_minor",),
                banding_id=uuid4(),
            ),
        )
        factor_id = factor_row.id

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=_spec(version_id, (factor_id,)),
        )
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "model_id": str(row.id),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.FAILED


@pytest.mark.req("FR-101")
async def test_a_stored_banding_cannot_be_updated_or_deleted(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The privilege layer, not the service layer.

    FR-101 holds for callers who remember it; this is what holds for a psql session. The
    `database` fixture is the login role, which inherits exactly `gip_app`'s grants and holds no
    `SET ROLE` option on it (FD-1951, SL-1962), so the refusal is read as itself.
    """
    from sqlalchemy import text

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    banding = await _banding(database, workspace_id, actor, dataset_id)

    async with database.session() as session:
        with pytest.raises(Exception, match=r"permission denied|InsufficientPrivilege"):
            await session.execute(
                text("UPDATE bandings SET slug = 'rewritten' WHERE id = :i"),
                {"i": banding.id},
            )

    async with database.session() as session:
        with pytest.raises(Exception, match=r"permission denied|InsufficientPrivilege"):
            await session.execute(text("DELETE FROM bandings WHERE id = :i"), {"i": banding.id})


@pytest.mark.req("FR-104")
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


@pytest.mark.req("FR-87")
async def test_loading_a_banding_that_does_not_exist_names_the_id(
    database: Database, workspace_id
) -> None:
    missing = uuid4()
    with pytest.raises(PlatformError) as refused:
        async with database.session() as session:
            await transform_service.load_bandings(session, workspace_id=workspace_id, ids=[missing])
    assert refused.value.code == "NOT_FOUND"
    assert str(missing) in (refused.value.detail or "")


def _chain_link(
    dataset_id: UUID,
    slug: str,
    mapping: dict[str, str],
    *,
    parent_id: UUID | None = None,
) -> Grouping:
    return Grouping(
        id=uuid4(),
        slug=f"{slug}-{uuid4().hex[-6:]}",
        dataset_id=dataset_id,
        version=1,
        column=slug,
        method=GroupingMethod.MANUAL,
        mapping=mapping,
        unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
        parent_grouping_id=parent_id,
    )


@pytest.mark.req("FR-105")
async def test_a_grouping_row_records_its_parent_for_a_hierarchy(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-109's chain, stored as a column so it is queryable rather than only in JSON."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)

    async with database.unit_of_work() as session:
        parent = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=_chain_link(dataset_id, "fine", {"u1": "urban", "r1": "rural"}),
        )
        parent_id = parent.id
        row = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=_chain_link(
                dataset_id, "area", {"urban": "ALL", "rural": "ALL"}, parent_id=parent_id
            ),
        )
        stored_id = row.id

    async with database.session() as session:
        stored = await session.get(GroupingRow, stored_id)
        assert stored is not None
        assert stored.parent_grouping_id == parent_id
        assert transform_service.to_grouping(stored).parent_grouping_id == parent_id


@pytest.mark.req("FR-109")
async def test_a_grouping_whose_parent_does_not_exist_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await transform_service.create_grouping(
                session,
                workspace_id=workspace_id,
                actor=actor,
                grouping=_chain_link(dataset_id, "area", {"a": "A"}, parent_id=uuid4()),
            )
    assert refused.value.code == "GROUPING_PARENT_NOT_FOUND"
    assert refused.value.status_code == 422


@pytest.mark.req("FR-109")
async def test_a_parent_in_another_workspace_reads_as_not_found(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The same code and the same text, so the answer does not say the id exists elsewhere."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    async with database.unit_of_work() as session:
        parent = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=_chain_link(dataset_id, "fine", {"a1": "A"}),
        )
        parent_id = parent.id
    child = _chain_link(dataset_id, "area", {"A": "X"}, parent_id=parent_id)
    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await transform_service._require_chain(session, workspace_id=uuid4(), grouping=child)
    assert refused.value.code == "GROUPING_PARENT_NOT_FOUND"


@pytest.mark.req("FR-109")
async def test_a_child_level_the_parent_does_not_produce_is_refused_without_the_level(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    async with database.unit_of_work() as session:
        parent = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=_chain_link(dataset_id, "fine", {"a1": "A"}),
        )
        parent_id = parent.id
    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await transform_service.create_grouping(
                session,
                workspace_id=workspace_id,
                actor=actor,
                grouping=_chain_link(
                    dataset_id, "area", {"A": "X", "ZZ-SENTINEL-9": "Y"}, parent_id=parent_id
                ),
            )
    assert refused.value.code == "GROUPING_CHAIN_LEVELS_MISMATCH"
    assert refused.value.status_code == 422
    assert "ZZ-SENTINEL-9" not in (refused.value.detail or "")


@pytest.mark.req("FR-109")
async def test_a_three_link_chain_whose_levels_chain_is_created_and_audited(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    async with database.unit_of_work() as session:
        fine_link = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=_chain_link(dataset_id, "fine", {"ab1": "AB", "cd1": "CD"}),
        )
        area = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=_chain_link(
                dataset_id, "area", {"AB": "N", "CD": "S"}, parent_id=fine_link.id
            ),
        )
        region = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=_chain_link(dataset_id, "region", {"N": "ALL", "S": "ALL"}, parent_id=area.id),
        )
        assert region.parent_grouping_id == area.id
        # The event of the region link, read by its entity ref and not by time: the three links
        # are created in one transaction, so their events share its `at` (audit.py: "`at` is the
        # transaction's start time"), and ordering by it picks any of them.
        region_ref = f"grouping:{region.slug}@{region.version}"
    async with database.session() as session:
        event = (
            (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.action == "grouping.created",
                        AuditEventRow.entity_ref == region_ref,
                    )
                )
            )
            .scalars()
            .first()
        )
        assert event is not None
        assert event.after["parent_grouping_ref"].startswith("grouping:area-")


@pytest.mark.req("FR-109")
async def test_a_fit_whose_grouping_factor_maps_none_of_the_column_fails_the_job_with_its_code(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The book's `area` holds `urban` and `rural`; the grouping maps neither."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(database, blob_store, workspace_id, actor, dataset_id)
    async with database.unit_of_work() as session:
        grouping_row = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=Grouping(
                id=uuid4(),
                slug=f"region-{uuid4().hex[-6:]}",
                dataset_id=dataset_id,
                version=1,
                column="area",
                method=GroupingMethod.MANUAL,
                mapping={"AB": "R1", "CD": "R2"},
                unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT,
                default_target_level="R1",
            ),
        )
        factor_row = await model_service.create_factor(
            session,
            workspace_id=workspace_id,
            actor=actor,
            factor=Factor(
                id=uuid4(),
                slug=f"region-f-{uuid4().hex[-6:]}",
                dataset_id=dataset_id,
                version=1,
                type=FactorType.GROUPING,
                source_columns=("area",),
                grouping_id=grouping_row.id,
            ),
        )
        factor_id = factor_row.id

    # A fit with no split is refused first, `MODEL_SPLIT_REQUIRED` (02-modelling.md: "before
    # any compute is spent"), so this fit carries one and reaches the refusal the test is about.
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=_spec(version_id, (factor_id,), split_ref=split),
        )
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "model_id": str(row.id),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.FAILED
    async with database.session() as session:
        job_row = await session.get(JobRow, job.id)
    assert job_row is not None
    assert job_row.error is not None
    assert job_row.error["code"] == "GROUPING_MAPS_NO_VALUE"
    assert "urban" not in job_row.error["message"]
    assert "rural" not in job_row.error["message"]
    assert "region-f-" in job_row.error["message"]  # the Factor is named; the 409 is the handler's


@pytest.mark.req("FR-109")
async def test_a_grouping_cannot_name_its_own_request_id_as_its_parent(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The row's id is the application's `new_uuid7` default, never the request's, so a body id
    that equals its own `parent_grouping_id` names no stored row and reads as not found.

    A later change that took the id from the request would let a Grouping be its own parent;
    this test turns red then.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    own = uuid4()
    child = _chain_link(dataset_id, "area", {"a": "A"}, parent_id=own).model_copy(
        update={"id": own}
    )
    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await transform_service.create_grouping(
                session, workspace_id=workspace_id, actor=actor, grouping=child
            )
    assert refused.value.code == "GROUPING_PARENT_NOT_FOUND"


@pytest.mark.req("FR-109")
async def test_loading_a_grouping_brings_its_whole_chain(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    async with database.unit_of_work() as session:
        fine = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=_chain_link(dataset_id, "fine", {"ab1": "AB", "cd1": "CD"}),
        )
        area = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=_chain_link(dataset_id, "area", {"AB": "N", "CD": "S"}, parent_id=fine.id),
        )
        region = await transform_service.create_grouping(
            session,
            workspace_id=workspace_id,
            actor=actor,
            grouping=_chain_link(dataset_id, "region", {"N": "ALL", "S": "ALL"}, parent_id=area.id),
        )
        ids = (fine.id, area.id, region.id)
    async with database.session() as session:
        loaded = await transform_service.load_groupings(
            session, workspace_id=workspace_id, ids=[ids[2]]
        )
    assert set(loaded) == set(ids)
