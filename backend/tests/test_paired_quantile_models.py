"""Paired quantile models — the pairing rules and the lookup (`02` FR-MODEL-78/100).

Almost every test here is a **prohibition**, and that is the point (`CLAUDE.md` §13). A
bound that agrees with the model it bounds is a bound; a bound that disagrees is an interval
drawn around a model nobody fitted, and it fits without complaint, returns two ordered
numbers, and renders identically to a correct one. Nothing downstream can tell them apart,
so the refusal has to be here.

These tests reserve models rather than fitting them. The pairing rules are decided in
`reserve_model`, before a Job exists — the same place `02` R1 is answered, and for the same
reason: learning from a failed job twenty seconds later is a worse answer to the same
question. `test_prediction.py` owns what a *fitted* pair does.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest
from backend.tests.test_custom_objectives import _certified
from backend.tests.test_model_jobs import (
    _actuary,
    _dataset,
    _factor,
    _split,
    _validated_version,
)
from backend.tests.test_model_jobs_gbm import _gbm_spec

from app.db.models import CustomObjectiveRow, ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import modelling as model_service
from app.platform.blobs import BlobStore
from model_schema import (
    MODEL_SPEC_ADAPTER,
    GbmFunctionRef,
    GbmSpec,
    IntervalFor,
    ObjectiveStatus,
    ObjectiveTemplate,
    Principal,
    SplitRef,
)


@dataclass(frozen=True)
class _Central:
    """A central Model plus everything FR-MODEL-78 makes a bound match it on."""

    actor: Principal
    id: UUID
    slug: str
    version: int
    version_id: UUID
    factors: tuple[UUID, ...]
    split: SplitRef
    quantile_ref: str


async def _approved_quantile(
    database: Database, blob_store: BlobStore, workspace_id, actor: Principal, alpha: float
) -> str:
    """An approved `quantile` Custom Objective at `alpha`, as a spec-ready ref.

    **Certified through the real Job**, not stamped: `custom_objectives` carries a CHECK
    that an objective past `draft` has a certificate, so a status set directly is refused by
    the database. That refusal is the governance invariant working, and routing around it in
    a fixture would mean these tests exercise a state the platform cannot produce.

    The approval itself *is* stamped, once the certificate exists. Driving `06`'s
    two-person approval here would make every pairing test depend on the governance path
    staying green for reasons unrelated to what it asserts, and
    `test_custom_objectives.py` already owns that lifecycle.
    """
    row = await _certified(
        database,
        blob_store,
        workspace_id,
        actor,
        template=ObjectiveTemplate.QUANTILE,
        params={"alpha": alpha},
    )
    async with database.unit_of_work() as session:
        stored = await session.get(CustomObjectiveRow, row.id)
        assert stored is not None
        assert stored.certificate_id is not None, "the CHECK needs a real certificate"
        stored.status = ObjectiveStatus.APPROVED.value
    return f"custom_objective:{row.slug}@{row.version}"


async def _central_model(
    database: Database, blob_store: BlobStore, workspace_id
) -> _Central:
    """A reserved central GBM and the artifacts a bound has to agree with it about."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    other = await _factor(database, workspace_id, actor, dataset_id, "area", "area2")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    # Each `unit_of_work` takes its own connection, so opening a second one inside the
    # first deadlocks against the pool rather than failing — the run hangs with no output.
    # Everything that needs its own transaction is therefore sequenced, never nested.
    quantile_ref = await _approved_quantile(database, blob_store, workspace_id, actor, 0.05)

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=_gbm_spec(version_id, (area, other), split_ref=split),
        )
        identity = (row.id, row.model_family_slug, row.version)

    return _Central(
        actor=actor,
        id=identity[0],
        slug=identity[1],
        version=identity[2],
        version_id=version_id,
        factors=(area, other),
        split=split,
        quantile_ref=quantile_ref,
    )


def _bound_spec(central: _Central, *, alpha: float, ref: str | None = None, **over) -> GbmSpec:
    """A bound that matches `central` on everything FR-MODEL-78 names, before `over`."""
    matching: dict[str, object] = {
        "model_family_slug": central.slug,
        "split_ref": central.split,
        "objective": GbmFunctionRef(kind="custom", ref=ref or central.quantile_ref),
        "interval_for": IntervalFor(
            model_id=central.id, model_version=central.version, alpha=alpha
        ),
    }
    # `over` wins, so a test can break exactly one of the matching fields by naming it.
    matching.update(over)
    return _gbm_spec(central.version_id, central.factors, **matching)


async def _reserve(database: Database, workspace_id, central: _Central, spec: GbmSpec):
    async with database.unit_of_work() as session:
        return await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=central.actor, spec=spec
        )


# --------------------------------------------------------------------------------------
# FR-MODEL-78 — a bound must match the model it bounds
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-78")
async def test_a_matching_bound_is_accepted(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The positive case, so the rules below cannot be satisfied by refusing everything.

    A suite of nothing but prohibitions passes just as well against a check that raises
    unconditionally, and that check would make the feature unbuildable rather than safe.
    """
    central = await _central_model(database, blob_store, workspace_id)
    _, should_fit = await _reserve(
        database, workspace_id, central, _bound_spec(central, alpha=0.05)
    )
    assert should_fit is True


@pytest.mark.req("FR-MODEL-78")
async def test_a_bound_on_a_different_dataset_version_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """An interval around a model fitted on other data is not this model's interval.

    It fits, it produces two ordered numbers, and it describes a different population.
    """
    central = await _central_model(database, blob_store, workspace_id)
    other_dataset = await _dataset(database, blob_store, workspace_id, central.actor)
    other_version = await _validated_version(
        database, blob_store, workspace_id, central.actor, other_dataset
    )
    with pytest.raises(PlatformError) as caught:
        await _reserve(
            database,
            workspace_id,
            central,
            _bound_spec(central, alpha=0.05, dataset_version_id=other_version),
        )
    assert caught.value.code == "MODEL_INTERVAL_PAIR_INVALID"
    assert "dataset_version_id" in str(caught.value.detail)


@pytest.mark.req("FR-MODEL-78")
async def test_a_bound_with_a_different_factor_set_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """A bound fitted on fewer factors is an interval around a different design."""
    central = await _central_model(database, blob_store, workspace_id)
    with pytest.raises(PlatformError) as caught:
        await _reserve(
            database,
            workspace_id,
            central,
            _bound_spec(central, alpha=0.05, factors=central.factors[:1]),
        )
    assert caught.value.code == "MODEL_INTERVAL_PAIR_INVALID"
    assert "factors" in str(caught.value.detail)


@pytest.mark.req("FR-MODEL-78")
async def test_a_bound_whose_factors_are_only_reordered_is_accepted(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The comparison is on the set, and this is what stops it being tightened by accident.

    Two specs listing the same factors in a different order describe the same design
    matrix. Comparing the tuples would refuse a legitimate bound for a difference the fit
    cannot see — and the refusal would arrive with a message about factors that look
    identical when read.
    """
    central = await _central_model(database, blob_store, workspace_id)
    _, should_fit = await _reserve(
        database,
        workspace_id,
        central,
        _bound_spec(central, alpha=0.05, factors=tuple(reversed(central.factors))),
    )
    assert should_fit is True


@pytest.mark.req("FR-MODEL-78")
async def test_a_bound_in_a_different_model_family_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-78 names the family first, and a family is how a reader finds the pair."""
    central = await _central_model(database, blob_store, workspace_id)
    with pytest.raises(PlatformError) as caught:
        await _reserve(
            database,
            workspace_id,
            central,
            _bound_spec(central, alpha=0.05, model_family_slug="somewhere-else"),
        )
    assert "model_family_slug" in str(caught.value.detail)


@pytest.mark.req("FR-MODEL-78")
async def test_a_bound_fitted_with_a_poisson_objective_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-78: a bound is fitted **with the `quantile` template**, and this is that.

    The sharpest of these rules and the one most easily left out: a bound whose objective is
    `count:poisson` estimates the *mean*, not a quantile. Every other rule would pass — same
    family, dataset, split, factor set — and the pair would be two mean estimates reported
    as an interval, which is not merely wrong but wrong in the direction of looking right.
    """
    central = await _central_model(database, blob_store, workspace_id)
    with pytest.raises(PlatformError) as caught:
        await _reserve(
            database,
            workspace_id,
            central,
            _bound_spec(central, alpha=0.05).model_copy(
                update={"objective": GbmFunctionRef(kind="builtin", name="count:poisson")}
            ),
        )
    assert caught.value.code == "MODEL_INTERVAL_PAIR_INVALID"
    assert "quantile" in str(caught.value.detail)


@pytest.mark.req("FR-MODEL-78")
async def test_a_bound_whose_objective_alpha_disagrees_with_its_own_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Two alphas, one bound: the objective's and `interval_for`'s must be the same number.

    They are declared in two places because they mean two things — the loss the booster
    minimises, and the quantile the pair claims to estimate — and a bound whose loss seeks
    the 5th percentile while its artifact says 25th is mislabelled at exactly the point a
    reader would check.
    """
    central = await _central_model(database, blob_store, workspace_id)
    with pytest.raises(PlatformError) as caught:
        await _reserve(
            database, workspace_id, central, _bound_spec(central, alpha=0.25)
        )
    assert caught.value.code == "MODEL_INTERVAL_PAIR_INVALID"
    assert "0.25" in str(caught.value.detail)


@pytest.mark.req("FR-MODEL-100")
async def test_a_second_bound_on_the_same_side_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-100(iv). One lower and one upper, so the response's `level` is unambiguous.

    Two lower bounds at 0.05 and 0.10 satisfy every other rule, and the prediction path
    would have to choose between them with nothing in either artifact saying which the
    actuary meant.
    """
    central = await _central_model(database, blob_store, workspace_id)
    await _reserve(database, workspace_id, central, _bound_spec(central, alpha=0.05))
    ref = await _approved_quantile(database, blob_store, workspace_id, central.actor, 0.10)
    with pytest.raises(PlatformError) as caught:
        await _reserve(
            database, workspace_id, central, _bound_spec(central, alpha=0.10, ref=ref)
        )
    assert caught.value.code == "MODEL_INTERVAL_PAIR_INVALID"
    assert "lower bound" in str(caught.value.detail)


@pytest.mark.req("FR-MODEL-100")
async def test_the_opposite_side_is_still_allowed_after_one_is_taken(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """One per side, not one in total — the pair needs both halves to exist."""
    central = await _central_model(database, blob_store, workspace_id)
    await _reserve(database, workspace_id, central, _bound_spec(central, alpha=0.05))
    ref = await _approved_quantile(database, blob_store, workspace_id, central.actor, 0.95)
    _, should_fit = await _reserve(
        database, workspace_id, central, _bound_spec(central, alpha=0.95, ref=ref)
    )
    assert should_fit is True


@pytest.mark.req("FR-MODEL-100")
async def test_a_bound_naming_a_model_that_does_not_exist_is_a_404(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """404, not 409: the caller named something that is not there.

    Kept here rather than with the generic not-found tests because the id arrives inside a
    spec rather than in the path, which is the mistake a copied-and-edited request makes.
    """
    central = await _central_model(database, blob_store, workspace_id)
    spec = _bound_spec(central, alpha=0.05).model_copy(
        update={
            "interval_for": IntervalFor(model_id=uuid4(), model_version=1, alpha=0.05)
        }
    )
    with pytest.raises(PlatformError) as caught:
        await _reserve(database, workspace_id, central, spec)
    assert caught.value.status_code == 404


# --------------------------------------------------------------------------------------
# FR-MODEL-78 — finding the pair
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-78")
async def test_the_bounds_come_back_lower_first(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Ordered by alpha, so a caller reads `[lower, upper]` rather than sorting again.

    Reserved upper-first deliberately: insertion order must not be what makes this pass.
    Two callers sorting the same list two ways is how a lower bound reaches the upper side
    of a response, and `PredictedRow`'s ordering validator would then raise three layers
    away from the cause.
    """
    central = await _central_model(database, blob_store, workspace_id)
    upper_ref = await _approved_quantile(database, blob_store, workspace_id, central.actor, 0.95)
    await _reserve(
        database, workspace_id, central, _bound_spec(central, alpha=0.95, ref=upper_ref)
    )
    await _reserve(database, workspace_id, central, _bound_spec(central, alpha=0.05))

    async with database.unit_of_work() as session:
        found = await model_service.load_interval_models(
            session, workspace_id=workspace_id, central_model_id=central.id
        )
    alphas = [_alpha_of(row) for row in found]
    assert alphas == [0.05, 0.95]


@pytest.mark.req("FR-MODEL-78")
async def test_a_model_with_no_bounds_finds_none(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The common case, and the one that must not be an error.

    Almost no model is bounded, so `[]` is the normal answer and the prediction path reads
    it as FR-MODEL-77's `no_interval_models_fitted` rather than as a failure.
    """
    central = await _central_model(database, blob_store, workspace_id)
    async with database.unit_of_work() as session:
        assert (
            await model_service.load_interval_models(
                session, workspace_id=workspace_id, central_model_id=central.id
            )
            == []
        )


@pytest.mark.req("FR-MODEL-78")
async def test_the_lookup_does_not_reach_another_models_bounds(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Two central models in one workspace, and each finds only its own.

    The predicate reads a field inside a JSON document. Unlike a foreign key it carries no
    relationship of its own, so "which model is this a bound for" is only as good as the
    `->>` path — and a path typo would return every bound in the workspace to every model.
    """
    first = await _central_model(database, blob_store, workspace_id)
    second = await _central_model(database, blob_store, workspace_id)
    await _reserve(database, workspace_id, first, _bound_spec(first, alpha=0.05))

    async with database.unit_of_work() as session:
        assert (
            len(
                await model_service.load_interval_models(
                    session, workspace_id=workspace_id, central_model_id=first.id
                )
            )
            == 1
        )
        assert (
            await model_service.load_interval_models(
                session, workspace_id=workspace_id, central_model_id=second.id
            )
            == []
        )


def _alpha_of(row: ModelRow) -> float:
    spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
    assert isinstance(spec, GbmSpec)
    assert spec.interval_for is not None
    return spec.interval_for.alpha
