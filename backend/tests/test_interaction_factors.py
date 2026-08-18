"""An interaction Factor through the platform (`02` FR-MODEL-91, FR-MODEL-5).

`packages/pricing-core/tests/test_interactions.py` owns the crossing itself. This owns the
one thing only the platform can be wrong about: **a Model Spec pins an interaction by id
and says nothing about what it crosses.** Without transitive loading every such fit failed
inside `pricing-core` with "crosses factor …, which was not supplied" — a correct refusal,
arriving from the wrong layer, about something the caller had no way to provide.

`ModelSpec.factors` stays flat, which is what makes a spec readable; the platform resolves
the tree. And because it does, the refusals already written against the pinned factors —
prohibited (FR-MODEL-5) and foreign-dataset (FR-MODEL-2) — reach the operands for free,
which is the second thing tested here.
"""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from backend.tests.test_data_jobs import _ingest, _validate
from backend.tests.test_model_jobs import _actuary, _dataset, _spec, _split

from app.db.session import Database
from app.errors import PlatformError
from app.platform import jobs as job_service
from app.platform import modelling as service
from app.platform import validation as validation_service
from app.worker.tasks import execute_job
from model_schema import Factor, FactorType, JobKind, JobStatus, ModelStatus

#: Two categorical columns, because a cross needs two. `test_model_jobs`' own book carries
#: only `area`, and crossing a factor with itself is what the contract refuses. Urban/G2
#: runs hot beyond what either main effect predicts, so the cross has something to find
#: that two separate factors cannot represent.
BOOK = (
    b"policy_id,exposure_years,area,vehicle_group,claim_count,claim_amount_minor\n"
    + b"".join(
        f"P{i},1.0,{'urban' if i % 2 == 0 else 'rural'},G{i % 3},"
        f"{(4 if i % 3 == 2 else 2) if i % 2 == 0 else 1},100000\n".encode()
        for i in range(1, 601)
    )
)


async def _validated(database, blob_store, workspace_id, actor, dataset_id) -> UUID:
    """Ingest **this** book and promote it, by the path `_validated_version` uses."""
    version_id = await _ingest(database, blob_store, workspace_id, actor, dataset_id, BOOK)
    report_id = await _validate(database, blob_store, workspace_id, actor, version_id)
    async with database.unit_of_work() as session:
        await validation_service.promote_using_report(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, report_id=report_id,
        )
    return version_id


async def _factor(
    database: Database, workspace_id, actor, dataset_id: UUID, slug: str, column: str,
    **over: object,
) -> UUID:
    """`test_model_jobs`' helper, widened to carry the prohibition fields this file needs."""
    fields: dict[str, object] = {
        "id": uuid4(), "slug": slug, "dataset_id": dataset_id, "version": 1,
        "type": FactorType.IDENTITY, "source_columns": (column,),
    }
    fields.update(over)
    async with database.unit_of_work() as session:
        row = await service.create_factor(
            session, workspace_id=workspace_id, actor=actor,
            factor=Factor(**fields),  # type: ignore[arg-type]
        )
        return row.id


async def _interaction_factor(
    database: Database, workspace_id, actor, dataset_id: UUID, operands: list[UUID]
) -> UUID:
    async with database.unit_of_work() as session:
        row = await service.create_factor(
            session,
            workspace_id=workspace_id,
            actor=actor,
            factor=Factor(
                id=uuid4(),
                slug=f"crossed_{uuid4().hex[-6:]}",
                dataset_id=dataset_id,
                version=1,
                type=FactorType.INTERACTION,
                source_columns=(),
                operand_factor_ids=tuple(operands),
            ),
        )
        return row.id


@pytest.mark.req("FR-MODEL-91")
async def test_load_factors_brings_the_operands_a_spec_never_names(
    database, blob_store, workspace_id
) -> None:
    """The spec pins one id and the fit needs three factors. That gap is the platform's."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    vehicle = await _factor(
        database, workspace_id, actor, dataset_id, "vehicle", "vehicle_group"
    )
    crossed = await _interaction_factor(
        database, workspace_id, actor, dataset_id, [area, vehicle]
    )

    async with database.unit_of_work() as session:
        loaded = await service.load_factors(
            session, workspace_id=workspace_id, factor_ids=[crossed]
        )
    assert [f.id for f in loaded] == [crossed, area, vehicle]
    # The pinned factor comes first: the design's column order follows the spec's, and the
    # operands contribute no column at all.
    assert loaded[0].type is FactorType.INTERACTION


@pytest.mark.req("FR-MODEL-91")
async def test_an_operand_is_loaded_once_even_when_two_interactions_share_it(
    database, blob_store, workspace_id
) -> None:
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    vehicle = await _factor(
        database, workspace_id, actor, dataset_id, "vehicle", "vehicle_group"
    )
    first = await _interaction_factor(
        database, workspace_id, actor, dataset_id, [area, vehicle]
    )
    second = await _interaction_factor(
        database, workspace_id, actor, dataset_id, [vehicle, area]
    )

    async with database.unit_of_work() as session:
        loaded = await service.load_factors(
            session, workspace_id=workspace_id, factor_ids=[first, second]
        )
    ids = [f.id for f in loaded]
    assert ids[:2] == [first, second]
    assert sorted(ids[2:]) == sorted([area, vehicle]), "an operand loaded twice is a bug"


@pytest.mark.req("FR-MODEL-91")
async def test_an_operand_that_does_not_exist_is_a_404_naming_it(
    database, blob_store, workspace_id
) -> None:
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    ghost = uuid4()
    crossed = await _interaction_factor(
        database, workspace_id, actor, dataset_id, [area, ghost]
    )

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.load_factors(
                session, workspace_id=workspace_id, factor_ids=[crossed]
            )
    assert refused.value.code == "NOT_FOUND"
    assert str(ghost) in (refused.value.detail or "")
    assert "operand" in (refused.value.title or "").lower()


@pytest.mark.req("FR-MODEL-5")
async def test_a_prohibited_operand_is_refused_before_a_job_exists(
    database, blob_store, workspace_id
) -> None:
    """FR-MODEL-5 reaching through the cross, at the layer that can refuse the *attempt*.

    A prohibited factor that cannot enter a spec directly, but can enter one crossed with
    something else, is not prohibited. The check was already written against the spec's own
    factors; transitive loading is what makes it reach an operand.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated(database, blob_store, workspace_id, actor, dataset_id)
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    banned = await _factor(
        database, workspace_id, actor, dataset_id, "banned", "vehicle_group",
        prohibited=True, prohibited_reason="Proxy for a protected characteristic.",
    )
    crossed = await _interaction_factor(
        database, workspace_id, actor, dataset_id, [area, banned]
    )
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.reserve_model(
                session,
                workspace_id=workspace_id,
                actor=actor,
                spec=_spec(version_id, (crossed,), split_ref=split),
            )
    assert refused.value.code == "FACTOR_PROHIBITED"
    assert "banned" in (refused.value.detail or "")


@pytest.mark.req("FR-MODEL-91")
async def test_a_fit_on_an_interaction_runs_end_to_end(
    database, blob_store, workspace_id
) -> None:
    """`wf-01` D7's shape: a spec naming only the cross, fitted through the real Job.

    The seeded book's `area` and `vehicle_group` are both categorical, so the cross is a
    genuine table of cells — which is what makes the fitted model rateable and the whole
    reason operands are Factors rather than columns.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated(database, blob_store, workspace_id, actor, dataset_id)
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    vehicle = await _factor(
        database, workspace_id, actor, dataset_id, "vehicle", "vehicle_group"
    )
    crossed = await _interaction_factor(
        database, workspace_id, actor, dataset_id, [area, vehicle]
    )
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        spec = _spec(version_id, (crossed,), split_ref=split)
        # The spec pins one factor and the fit needs three. Asserted here as well as in
        # `test_load_factors_…` because this is the exact call the handler makes, and a
        # regression in the expansion shows up as a *job* failure otherwise — one layer
        # away from the cause.
        assert len(
            await service.load_factors(
                session, workspace_id=workspace_id, factor_ids=list(spec.factors)
            )
        ) == 3
        row, should_fit = await service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec
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
        model = service.to_model(
            await service.load_model_by_id(
                session, workspace_id=workspace_id, model_id=model_id
            )
        )
    assert model.status is ModelStatus.FITTED
    assert model.fit_result is not None
    # The relativity table is keyed by the *crossed* factor's slug, and its levels carry the
    # separator — a table keyed by either operand alone would mean the cross never ran.
    crossed_slug = next(
        slug for slug in model.fit_result.relativities if slug.startswith("crossed_")
    )
    levels = [row.level for row in model.fit_result.relativities[crossed_slug]]
    assert levels, "the cross produced no levels"
    assert all(" | " in level for level in levels), levels
