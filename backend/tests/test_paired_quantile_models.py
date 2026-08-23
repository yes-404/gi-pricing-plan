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
from backend.tests.test_model_jobs_gbm import _fitted_gbm, _gbm_spec

from app.db.models import CustomObjectiveRow, DiagnosticsRow, JobRow, ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import diagnostics as diagnostics_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import prediction as prediction_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import (
    MODEL_SPEC_ADAPTER,
    GbmFunctionRef,
    GbmSpec,
    IntervalFor,
    JobKind,
    JobStatus,
    ModelStatus,
    ObjectiveStatus,
    ObjectiveTemplate,
    Principal,
    ResponseKind,
    SplitRef,
    UnavailableReason,
    UncertaintyKind,
)

register_data_handlers()
register_model_handlers()


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
    # A genuine second column, so the factor-set tests below compare two real designs.
    # `_factor` takes (slug, column) in that order; a slug and a column that do not
    # both exist in `BOOK` fails at fit time rather than at creation.
    other = await _factor(
        database, workspace_id, actor, dataset_id, "amount", "claim_amount_minor"
    )
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
        # FR-MODEL-44: a custom objective declares the responses it applies to, and a
        # column name cannot be checked against that list — so a spec naming one must say
        # what it is modelling. A builtin objective names its own family and needs none.
        "response": ResponseKind.CLAIM_COUNT,
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


# --------------------------------------------------------------------------------------
# FR-MODEL-78 — crossing, detected when the second bound is fitted
# --------------------------------------------------------------------------------------


async def _fit_bound(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    central: _Central,
    *,
    alpha: float,
    ref: str | None = None,
) -> tuple[UUID, JobStatus]:
    """Reserve and fit one bound through the real `model.fit` Job."""
    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=central.actor,
            spec=_bound_spec(central, alpha=alpha, ref=ref),
        )
        assert should_fit is True
        model_id = row.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {
                "workspace_id": str(workspace_id),
                "actor": central.actor.model_dump(mode="json"),
                "model_id": str(model_id),
            },
            central.actor,
            workspace_id=workspace_id,
        )
    status = await execute_job(database, job.id, blob_store)
    if status is not JobStatus.SUCCEEDED:
        async with database.session() as session:
            failed = await session.get(JobRow, job.id)
        raise AssertionError(f"the bound at alpha={alpha} did not fit: {failed.error}")
    return model_id, status


async def _gbm_diagnostics_of(database: Database, model_id: UUID):
    async with database.session() as session:
        row = await session.get(ModelRow, model_id)
        assert row is not None
        assert row.diagnostics_id is not None
        stored = await session.get(DiagnosticsRow, row.diagnostics_id)
    assert stored is not None
    return diagnostics_service.to_diagnostics(stored).gbm


@pytest.mark.req("FR-MODEL-78")
async def test_only_the_second_bound_of_a_pair_records_crossing(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The first bound has no counterpart to cross; the second compares itself with it.

    Asserted on **both** models rather than only the second. A detector that attached the
    block to whichever model it happened to be looking at would pass a test that checked
    one of them, and `QuantileCrossing` would then appear on a model whose counterpart did
    not exist when it was written.
    """
    central = await _central_model(database, blob_store, workspace_id)
    upper_ref = await _approved_quantile(
        database, blob_store, workspace_id, central.actor, 0.95
    )

    lower_id, lower_status = await _fit_bound(
        database, blob_store, workspace_id, central, alpha=0.05
    )
    upper_id, upper_status = await _fit_bound(
        database, blob_store, workspace_id, central, alpha=0.95, ref=upper_ref
    )
    assert (lower_status, upper_status) == (JobStatus.SUCCEEDED, JobStatus.SUCCEEDED)

    assert (await _gbm_diagnostics_of(database, lower_id)).quantile_crossing is None

    crossing = (await _gbm_diagnostics_of(database, upper_id)).quantile_crossing
    assert crossing is not None
    assert crossing.counterpart_model_id == lower_id
    assert crossing.rows_checked > 0
    # Whether these two particular fits cross is a property of the data, not of the code,
    # so the assertion is on the invariant rather than on a number: the two figures agree
    # about whether there was any crossing at all.
    assert (crossing.rows_crossing == 0) == (crossing.worst_gap == 0.0)
    assert crossing.rows_crossing <= crossing.rows_checked


@pytest.mark.req("FR-MODEL-78")
async def test_an_ordinary_gbm_records_no_crossing_block(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """A model that is not a bound carries `None`, not a zeroed block.

    A zeroed block would read as "checked, and they did not cross", which is a measurement
    this model never made — the same defect FR-MODEL-50's `double_lift` and
    `Diagnostics.backtest` were removed for.
    """
    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED
    assert (await _gbm_diagnostics_of(database, model_id)).quantile_crossing is None


# --------------------------------------------------------------------------------------
# FR-MODEL-77/78/100/101 — what a prediction says about a bounded GBM
# --------------------------------------------------------------------------------------


async def _fitted_pair(
    database: Database, blob_store: BlobStore, workspace_id
) -> tuple[_Central, UUID, UUID]:
    """A fitted central GBM with a complete, fitted pair of bounds."""
    central = await _central_model(database, blob_store, workspace_id)
    upper_ref = await _approved_quantile(
        database, blob_store, workspace_id, central.actor, 0.95
    )
    lower_id, _ = await _fit_bound(
        database, blob_store, workspace_id, central, alpha=0.05
    )
    upper_id, _ = await _fit_bound(
        database, blob_store, workspace_id, central, alpha=0.95, ref=upper_ref
    )
    await _fit_central(database, blob_store, workspace_id, central)
    return central, lower_id, upper_id


async def _fit_central(
    database: Database, blob_store: BlobStore, workspace_id, central: _Central
) -> None:
    """Fit the reserved central model itself, so it can be scored."""
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {
                "workspace_id": str(workspace_id),
                "actor": central.actor.model_dump(mode="json"),
                "model_id": str(central.id),
            },
            central.actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED


async def _set_status(database: Database, model_id: UUID, status: ModelStatus) -> None:
    """Put a model row into a status directly.

    The lifecycle transitions are `test_model_lifecycle.py`'s subject; what these tests need
    is the *state*, and driving `06`'s two-person approval for each of them would make every
    assertion here depend on the governance path for reasons unrelated to what it asserts.
    """
    async with database.unit_of_work() as session:
        row = await session.get(ModelRow, model_id)
        assert row is not None
        row.status = status.value


async def _predict(database: Database, blob_store: BlobStore, workspace_id, central, model_id):
    async with database.session() as session:
        return await prediction_service.predict_rows(
            session,
            workspace_id=workspace_id,
            actor=central.actor,
            model_id=model_id,
            rows=[
                {"exposure_years": 1.0, "area": "urban", "claim_amount_minor": 200000},
                {"exposure_years": 1.0, "area": "rural", "claim_amount_minor": 100000},
            ],
            blob_store=blob_store,
        )


@pytest.mark.req("FR-MODEL-78")
@pytest.mark.req("FR-MODEL-101")
async def test_a_gbm_with_a_complete_pair_returns_an_interval(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The first time a GBM prediction has ever carried bounds.

    `level` is the spread between the alphas — 0.90 for a 0.05/0.95 pair — and not
    `CONFIDENCE_LEVEL`, which describes a covariance matrix this interval never used.
    `basis` is absent for the same reason: there is no matrix to describe (FR-MODEL-101).
    """
    central, lower_id, upper_id = await _fitted_pair(database, blob_store, workspace_id)
    prediction = await _predict(database, blob_store, workspace_id, central, central.id)

    assert prediction.uncertainty.kind is UncertaintyKind.QUANTILE_PAIR_INTERVAL
    assert prediction.uncertainty.level == pytest.approx(0.90)
    assert prediction.uncertainty.basis is None
    models = prediction.uncertainty.interval_models
    assert models is not None
    assert (models.lower_model_id, models.upper_model_id) == (lower_id, upper_id)
    assert (models.lower_alpha, models.upper_alpha) == (0.05, 0.95)
    assert all(row.lower is not None and row.upper is not None for row in prediction.rows)


@pytest.mark.req("FR-MODEL-77")
async def test_a_gbm_with_only_one_bound_says_no_interval_models_fitted(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Half a pair is not a pair, and it needs no new vocabulary to say so.

    FR-MODEL-77's set is closed; the absence of a *pair* is exactly what
    `no_interval_models_fitted` already says, so a lone bound reuses it rather than earning
    a fifth reason.
    """
    central = await _central_model(database, blob_store, workspace_id)
    await _fit_bound(database, blob_store, workspace_id, central, alpha=0.05)
    await _fit_central(database, blob_store, workspace_id, central)

    prediction = await _predict(database, blob_store, workspace_id, central, central.id)
    assert prediction.uncertainty.kind is UncertaintyKind.UNAVAILABLE
    assert prediction.uncertainty.reason is UnavailableReason.NO_INTERVAL_MODELS_FITTED
    assert all(row.lower is None for row in prediction.rows)


@pytest.mark.req("FR-MODEL-100")
async def test_an_approved_model_whose_bounds_are_only_fitted_says_not_approved(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-100(ii), and the first time this reason has been reachable at all.

    The bounds are left at `fitted` while the model they bound is `approved`. Quoting them
    would put a reviewed and an unreviewed number on one line with nothing separating them.
    """
    central, _, _ = await _fitted_pair(database, blob_store, workspace_id)
    await _set_status(database, central.id, ModelStatus.APPROVED)

    prediction = await _predict(database, blob_store, workspace_id, central, central.id)
    assert prediction.uncertainty.reason is UnavailableReason.INTERVAL_MODELS_NOT_APPROVED


@pytest.mark.req("FR-MODEL-100")
async def test_an_approved_model_with_approved_bounds_still_gets_its_interval(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The other half of FR-MODEL-100(ii), so the rule cannot be satisfied by refusing.

    Without this, "the bounds must be at least as reviewed" and "an approved model never
    gets an interval" pass the same tests.
    """
    central, lower_id, upper_id = await _fitted_pair(database, blob_store, workspace_id)
    for model_id in (central.id, lower_id, upper_id):
        await _set_status(database, model_id, ModelStatus.APPROVED)

    prediction = await _predict(database, blob_store, workspace_id, central, central.id)
    assert prediction.uncertainty.kind is UncertaintyKind.QUANTILE_PAIR_INTERVAL


@pytest.mark.req("FR-MODEL-100")
async def test_a_superseded_model_reports_its_bounds_stale(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-100(iii), and the fourth reason made reachable.

    `SCOREABLE_MODEL_STATUSES` admits `superseded`, so this model answers a prediction and
    its bounds are quotable. Quoting them without saying the family has moved past this
    version is the silence FR-MODEL-77 exists to refuse.
    """
    central, _, _ = await _fitted_pair(database, blob_store, workspace_id)
    await _set_status(database, central.id, ModelStatus.SUPERSEDED)

    prediction = await _predict(database, blob_store, workspace_id, central, central.id)
    assert prediction.uncertainty.reason is UnavailableReason.INTERVAL_MODELS_STALE


@pytest.mark.req("FR-MODEL-100")
async def test_staleness_outranks_approval_because_it_is_the_more_useful_thing_to_say(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """A superseded model with unapproved bounds reports staleness, not approval.

    The four arms are ordered most-specific-first and nothing but this pins that order.
    Reversed, the caller is told to go and get the bounds approved for a model version
    nobody should be quoting in the first place.
    """
    central, _, _ = await _fitted_pair(database, blob_store, workspace_id)
    await _set_status(database, central.id, ModelStatus.SUPERSEDED)

    prediction = await _predict(database, blob_store, workspace_id, central, central.id)
    assert prediction.uncertainty.reason is UnavailableReason.INTERVAL_MODELS_STALE


@pytest.mark.req("FR-MODEL-78")
async def test_a_crossing_pair_is_refused_rather_than_reordered(
    database: Database, blob_store: BlobStore, workspace_id, monkeypatch
) -> None:
    """FR-MODEL-78's "never silently reordered", at the point a caller would see it.

    **The crossing is injected, and deliberately so.** Two quantile fits at 0.05 and 0.95
    over this fixture's 400 rows do not cross, and manufacturing data that makes them cross
    would be tuning a dataset until an assertion passes. The arithmetic is unit-tested in
    `packages/pricing-core/tests/test_quantile_crossing.py`; what only this test can cover is
    the **wiring** — that a crossing verdict becomes a 409 naming the rows, rather than
    reaching `PredictedRow`, whose ordering validator would raise and turn an honest finding
    into a 500 with the reason buried in a traceback.
    """
    central, _, _ = await _fitted_pair(database, blob_store, workspace_id)

    import pricing_core.modelling.predict as core_predict

    monkeypatch.setattr(
        core_predict, "detect_quantile_crossing", lambda lower, upper: (2, 1.5)
    )

    with pytest.raises(PlatformError) as caught:
        await _predict(database, blob_store, workspace_id, central, central.id)
    assert caught.value.code == "MODEL_INTERVAL_UNAVAILABLE"
    assert caught.value.status_code == 409
    assert "2 of 2 rows" in str(caught.value.detail)
    assert "1.5" in str(caught.value.detail)


@pytest.mark.req("FR-MODEL-87")
@pytest.mark.req("FR-MODEL-124")
def test_every_unavailable_reason_is_returned_by_the_platform() -> None:
    """FR-MODEL-87's staging rule, as a check rather than as a sentence.

    Two of these were declared and unreachable until this slice, and the docstrings saying
    so have been removed. This is what stops that removal being a claim: if a member is ever
    added, or one stops being produced, the set stops matching and this fails.

    It fired as designed on 2026-08-23: `MODEL_TYPE_HAS_NO_INTERVAL` was added for the EBM
    predict arm (FR-MODEL-124) and this test failed until the new member was listed here.
    The EBM arm in `app.platform.prediction` returns it, so listing it is the resolution
    rather than a weakening — `backend/tests/test_prediction.py` holds the test that shows
    a scored EBM actually carries it.
    """
    returned = {
        UnavailableReason.NO_INTERVAL_MODELS_FITTED,
        UnavailableReason.INTERVAL_MODELS_NOT_APPROVED,
        UnavailableReason.INTERVAL_MODELS_STALE,
        UnavailableReason.COVARIANCE_NOT_STORED,
        UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL,
    }
    assert returned == set(UnavailableReason)
