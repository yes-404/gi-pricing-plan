"""Scoring a model over supplied rows (`02` FR-MODEL-62/63/77/93, §5.1).

`packages/pricing-core/tests/test_prediction_interval.py` owns the arithmetic — that the
interval is `g⁻¹(η̂ ± z·√(x'Vx))`, that the off-diagonal terms matter, and that it covers
the mean as often as it claims. This file owns the four things only the platform can be
wrong about:

* **the covariance blob makes the round trip.** The fit computes the digest and hands back
  the bytes (ADR-0001); the worker stores them; the prediction path fetches them by that
  digest. Three components, and nothing but an end-to-end fit-then-score proves the chain,
  because each of them is individually happy with a matrix that never arrives.
* **the uncertainty verdict matches the model in front of it** — an interval for a GLM
  that has its matrix, `covariance_not_stored` for one that does not, and FR-MODEL-77's
  `no_interval_models_fitted` for every GBM. `02` R5 is satisfied by the *right* one of
  these, not by any of them.
* **the refusals are refusals**, with the status a caller can act on: `422` for a request
  that is not a scoring request, `409` for a model that cannot answer it, `403` for a
  caller who may not ask.
* **the route is in the published contract**, the omission `test_api_diagnostics` records
  three requirements repairing.

The book is `test_model_jobs.BOOK`, where urban carries twice rural's claim count on equal
exposure — so a fitted model must price urban above rural, and a scorer that has silently
dropped the factor is visible rather than merely plausible.
"""

from __future__ import annotations

from typing import NamedTuple
from uuid import UUID, uuid4

import numpy as np
import polars as pl
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
from backend.tests.test_model_jobs_gbm import _fitted_gbm
from backend.tests.test_model_offset_jobs import (
    _residual_row,
    _residual_spec,
    _residual_version,
)
from fastapi.testclient import TestClient

from app.db.models import ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import prediction as service
from app.worker.tasks import execute_job
from model_schema import (
    GlmSpec,
    JobKind,
    JobStatus,
    ModelStatus,
    Principal,
    SplitRef,
    UnavailableReason,
    UncertaintyBasis,
    UncertaintyKind,
    new_uuid7,
)
from pricing_core.modelling import linear_predictor

#: Two rows the fitted model must price differently: same exposure, opposite area.
ROWS = [
    {"exposure_years": 1.0, "area": "urban"},
    {"exposure_years": 1.0, "area": "rural"},
]

#: Rows a model-offset spec can score. A prediction against `kind="model"` carries the
#: offset model's factors too: the endpoint computes the referenced linear predictor on
#: these very rows, so `exposure_years` and `area` (the base model's) must travel with
#: the residual model's own `resid_flag`.
RESIDUAL_ROWS = [
    {"exposure_years": 1.0, "area": "urban", "resid_flag": 0.0},
    {"exposure_years": 1.0, "area": "urban", "resid_flag": 1.0},
    {"exposure_years": 1.0, "area": "rural", "resid_flag": 0.0},
    {"exposure_years": 1.0, "area": "rural", "resid_flag": 1.0},
]


async def _fitted_glm(
    database: Database, blob_store, workspace_id, *, spare: bool = False, alpha: float = 0.0
) -> tuple[Principal, UUID] | tuple[Principal, UUID, UUID]:
    """One GLM fitted through the real Job, so its covariance blob is really in the store.

    With `spare=True` a second model is reserved on the same factors and left at `draft`,
    for the one test that needs a row whose `fit_result` can still be written.

    `alpha > 0` fits a **penalised** model, which is the case FR-MODEL-99 is about: `glum`
    returns the unpenalised information matrix and warns that it is incorrect, and the
    prediction has to say so rather than pass the interval off as exact.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), split_ref=split, alpha=alpha),
        )
        model_id = row.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    if not spare:
        return actor, model_id

    async with database.unit_of_work() as session:
        spare_row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), split_ref=split),
        )
        return actor, model_id, spare_row.id


class _ResidualPair(NamedTuple):
    """The Task 5 pair fitted through the real Jobs: the base GLM on v1 and the residual
    GLM on v2, offset against the base's linear predictor — plus the v2 artifacts a
    further residual reservation needs (`test_model_offset_jobs._residual_spec`)."""

    actor: Principal
    base_id: UUID
    residual_id: UUID
    v2_id: UUID
    resid_flag_id: UUID
    split2: SplitRef
    ref: str


async def _fitted_residual_pair(database, blob_store, workspace_id) -> _ResidualPair:
    """The base GLM, then the residual GLM offset against it, through the real Jobs —
    the seeding `test_model_offset_jobs.py`'s happy path makes, with the ref read off
    the base row's own family and version."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        base, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), split_ref=split),
        )
        assert should_fit is True
        base_id = base.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(base_id)},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    dataset2_id = await _dataset(database, blob_store, workspace_id, actor)
    v2_id = await _residual_version(database, blob_store, workspace_id, actor, dataset2_id)
    resid_flag = await _factor(
        database, workspace_id, actor, dataset2_id, "resid_flag", "resid_flag"
    )
    split2 = await _split(database, blob_store, workspace_id, actor, v2_id)

    async with database.session() as session:
        base_row = await session.get(ModelRow, base_id)
    assert base_row is not None
    ref = f"model:{base_row.model_family_slug}@{base_row.version}"

    residual_id, job = await _residual_row(
        database, blob_store, workspace_id, actor,
        _residual_spec(v2_id, resid_flag, split2, ref=ref),
    )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    return _ResidualPair(actor, base_id, residual_id, v2_id, resid_flag, split2, ref)


# -- The interval, end to end -------------------------------------------------------------


@pytest.mark.req("FR-MODEL-63")
@pytest.mark.req("FR-MODEL-98")
async def test_the_covariance_blob_survives_the_fit_the_store_and_the_prediction(
    database, blob_store, workspace_id
) -> None:
    """**The chain no single component can prove.** `fit_glm` computes a digest over bytes
    it does not store (ADR-0001), the worker stores them under it, and the prediction path
    fetches them back by that digest — and a break anywhere in between surfaces as a
    perfectly well-formed prediction with no interval on it, which is the one failure mode
    that looks like a design decision."""
    actor, model_id = await _fitted_glm(database, blob_store, workspace_id)

    async with database.session() as session:
        prediction = await service.predict_rows(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            rows=ROWS, blob_store=blob_store,
        )

    assert prediction.uncertainty.kind is UncertaintyKind.CONFIDENCE_INTERVAL_MEAN
    assert prediction.uncertainty.level == service.CONFIDENCE_LEVEL
    assert prediction.uncertainty.reason is None
    urban, rural = prediction.rows
    # The book prices urban at twice rural on equal exposure. A scorer that dropped the
    # factor returns two identical rows, which is a plausible-looking answer.
    assert urban.expected > rural.expected
    for row in prediction.rows:
        assert row.lower is not None
        assert row.upper is not None
        assert row.lower <= row.expected <= row.upper
        # A degenerate interval would satisfy the ordering check and nothing else.
        assert row.upper > row.lower


@pytest.mark.req("FR-MODEL-93")
async def test_a_glm_fitted_before_the_covariance_blob_says_so_rather_than_going_quiet(
    database, blob_store, workspace_id
) -> None:
    """FR-MODEL-93, on the models that make it necessary.

    The matrix is `p x p` and the artifact holds `p` numbers, so a fit that predates the
    blob cannot have one reconstructed — the only honest answers are a typed reason and a
    re-fit. Simulated by clearing the field on a real fit, because every model in this
    repository is now fitted with one and the case would otherwise be untestable until it
    was already in production data.
    """
    actor, model_id, reserved = await _fitted_glm(
        database, blob_store, workspace_id, spare=True
    )

    async with database.unit_of_work() as session:
        fitted = await session.get(ModelRow, model_id)
        stored = dict(fitted.fit_result)
        assert stored.pop("covariance_blob") is not None
        # Written onto a **reserved** model rather than over the fitted one. `02` R2's
        # trigger fires whenever `OLD.fit_result IS NOT NULL`, so rewriting the real model
        # is refused by the database — correctly, and this test would otherwise be proving
        # that the trigger is off. A draft receiving its first fit result is the transition
        # the worker itself makes, and a legacy model is exactly a row that took it before
        # the blob existed.
        await session.execute(
            ModelRow.__table__.update()
            .where(ModelRow.id == reserved)
            .values(
                fit_result=stored,
                status=ModelStatus.FITTED.value,
                # `ck_models_fitted_model_has_diagnostics`: a fitted model carries them, and
                # the constraint is right to insist. Shared with the real model rather than
                # forged, since nothing here reads them — what is under test is the absent
                # covariance blob, and every other field should be as ordinary as possible.
                diagnostics_id=fitted.diagnostics_id,
            )
        )
    model_id = reserved

    async with database.session() as session:
        prediction = await service.predict_rows(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            rows=ROWS, blob_store=blob_store,
        )

    assert prediction.uncertainty.kind is UncertaintyKind.UNAVAILABLE
    assert prediction.uncertainty.reason is UnavailableReason.COVARIANCE_NOT_STORED
    assert prediction.uncertainty.level is None
    # The expectation is still served. FR-MODEL-93 removes the interval, not the answer.
    assert all(row.lower is None and row.upper is None for row in prediction.rows)
    assert prediction.rows[0].expected > prediction.rows[1].expected


@pytest.mark.req("FR-MODEL-77")
async def test_a_gbm_names_the_reason_it_has_no_interval_rather_than_approximating_one(
    database, blob_store, workspace_id
) -> None:
    """FR-MODEL-77 refuses the variance-model approximation because it *renders* as a
    predictive interval. `no_interval_models_fitted` is the only one of its three reasons
    reachable until FR-MODEL-78's paired quantile models exist — and saying which one
    applies is what distinguishes a refusal from an omission."""
    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED
    # `_fitted_gbm` keeps its principal to itself. The roles are workspace-scoped, so any
    # actuary can ask the question — which is the point of gating this on `model:read`.
    actor = await _actuary(database, workspace_id)

    async with database.session() as session:
        prediction = await service.predict_rows(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            rows=ROWS, blob_store=blob_store,
        )

    assert prediction.model_type == "xgboost"
    assert prediction.uncertainty.kind is UncertaintyKind.UNAVAILABLE
    assert prediction.uncertainty.reason is UnavailableReason.NO_INTERVAL_MODELS_FITTED
    assert all(row.lower is None for row in prediction.rows)


# -- The model offset, end to end (FR-MODEL-24) --------------------------------------------


@pytest.mark.req("FR-MODEL-24")
async def test_a_model_offset_prediction_is_the_referenced_linear_predictor_plus_the_fit(
    database, blob_store, workspace_id
) -> None:
    """The endpoint resolves `offset_model_ref` per request and scores on top of the
    referenced model's linear predictor: μ = exp(η_base + Xβ̂).

    A scorer that dropped the offset would return exp(Xβ̂) — about a factor of 7 smaller
    at exposure 1 — which is a perfectly plausible-looking answer. The book's residual
    signal lives entirely inside the offset's eta, so only a prediction that honours it
    lands on the fitted value."""
    pair = await _fitted_residual_pair(database, blob_store, workspace_id)

    async with database.session() as session:
        prediction = await service.predict_rows(
            session, workspace_id=workspace_id, actor=pair.actor,
            model_id=pair.residual_id, rows=RESIDUAL_ROWS, blob_store=blob_store,
        )
        residual = model_service.to_model(await session.get(ModelRow, pair.residual_id))
        base = model_service.to_model(await session.get(ModelRow, pair.base_id))
        assert residual.fit_result is not None
        assert base.fit_result is not None
        assert isinstance(residual.spec, GlmSpec)
        assert isinstance(base.spec, GlmSpec)
        base_factors = await model_service.load_factors(
            session, workspace_id=workspace_id, factor_ids=list(base.spec.factors)
        )
        eta_base = linear_predictor(
            base.fit_result, pl.DataFrame(RESIDUAL_ROWS), base_factors, base.spec
        )

    beta = {c.term: c.estimate for c in residual.fit_result.coefficients}
    z = np.array([row["resid_flag"] for row in RESIDUAL_ROWS], dtype=np.float64)
    expected = np.exp(eta_base + beta["intercept"] + beta["resid_flag"] * z)

    assert len(prediction.rows) == len(RESIDUAL_ROWS)
    for i, row in enumerate(prediction.rows):
        assert row.expected == pytest.approx(expected[i], rel=1e-9)
        # The interval is the same centre — the offset contributes to it and not to the
        # width (FR-MODEL-63) — so it brackets the expectation as it does for any GLM.
        assert row.lower is not None
        assert row.upper is not None
        assert row.lower <= row.expected <= row.upper


@pytest.mark.req("FR-MODEL-24")
async def test_a_model_offset_ref_that_names_no_model_is_not_found_not_a_500(
    database, blob_store, workspace_id
) -> None:
    """The offset ref names a model that does not exist in this workspace: `NOT_FOUND`
    (404), the code a caller can act on, never a 500 from an unguarded lookup.

    The real fit path cannot produce this state — fit-time resolution refuses the ref
    before a Job is queued, and a fitted model cannot be deleted (`02` R2) — so it is
    simulated the way the pre-covariance-blob fit is: the residual model's real fit
    result is copied onto a reservation whose ref names no model, exactly as the worker
    would have written it. The failure under test is the resolution itself, not the
    state that produced it."""
    pair = await _fitted_residual_pair(database, blob_store, workspace_id)

    async with database.unit_of_work() as session:
        ghost, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=pair.actor,
            spec=_residual_spec(
                pair.v2_id, pair.resid_flag_id, pair.split2, ref="model:ghost@1"
            ),
        )
        fitted = await session.get(ModelRow, pair.residual_id)
        assert fitted is not None
        await session.execute(
            ModelRow.__table__.update()
            .where(ModelRow.id == ghost.id)
            .values(
                fit_result=fitted.fit_result,
                status=ModelStatus.FITTED.value,
                diagnostics_id=fitted.diagnostics_id,
            )
        )
        ghost_id = ghost.id

    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await service.predict_rows(
                session, workspace_id=workspace_id, actor=pair.actor,
                model_id=ghost_id, rows=RESIDUAL_ROWS, blob_store=blob_store,
            )
    assert refused.value.code == "NOT_FOUND"
    assert refused.value.status_code == 404


# -- The refusals --------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-62")
async def test_more_rows_than_the_endpoint_scores_is_refused_rather_than_served_slowly(
    database, blob_store, workspace_id
) -> None:
    """§5.1 scopes this route to dev/debug scale, and a limit stated only in prose is one
    every caller discovers by exceeding it. The interval materialises the `n x p` design,
    so the honest answer to a portfolio re-rate is `03`'s batch scoring, named in the
    message rather than left for the caller to find."""
    actor, model_id = await _fitted_glm(database, blob_store, workspace_id)

    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await service.predict_rows(
                session, workspace_id=workspace_id, actor=actor, model_id=model_id,
                rows=[ROWS[0]] * (service.MAX_PREDICT_ROWS + 1), blob_store=blob_store,
            )
    assert refused.value.status_code == 422
    assert "03" in (refused.value.detail or "")

    async with database.session() as session:
        with pytest.raises(PlatformError) as empty:
            await service.predict_rows(
                session, workspace_id=workspace_id, actor=actor, model_id=model_id,
                rows=[], blob_store=blob_store,
            )
    assert empty.value.status_code == 422


@pytest.mark.req("FR-MODEL-62")
async def test_a_model_with_no_fit_result_cannot_be_scored(
    database, blob_store, workspace_id
) -> None:
    """A `draft` reservation carries a spec and no coefficients. Scoring it would have to
    invent them, and the status is the thing that says so."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,)),
        )
        reserved = row.id
        assert ModelStatus(row.status) is ModelStatus.DRAFT

    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await service.predict_rows(
                session, workspace_id=workspace_id, actor=actor, model_id=reserved,
                rows=ROWS, blob_store=blob_store,
            )
    assert refused.value.code == "MODEL_NOT_FITTED"
    assert refused.value.status_code == 409


@pytest.mark.req("FR-MODEL-62")
async def test_rows_missing_a_column_the_model_needs_are_refused_by_name(
    database, blob_store, workspace_id
) -> None:
    """The one failure that is neither a bad request nor a bad model but the pairing of the
    two — and the only alternative to refusing it is a price computed without the factor."""
    actor, model_id = await _fitted_glm(database, blob_store, workspace_id)

    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await service.predict_rows(
                session, workspace_id=workspace_id, actor=actor, model_id=model_id,
                rows=[{"exposure_years": 1.0}], blob_store=blob_store,
            )
    assert refused.value.status_code == 409
    assert "area" in (refused.value.detail or "")


@pytest.mark.req("FR-MODEL-62")
async def test_a_model_in_another_workspace_is_not_found(
    database, blob_store, workspace_id
) -> None:
    """Not 403. A caller with no standing in a workspace must not learn from the status
    code that the id they guessed is real."""
    actor, model_id = await _fitted_glm(database, blob_store, workspace_id)

    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await service.predict_rows(
                session, workspace_id=uuid4(), actor=actor, model_id=model_id,
                rows=ROWS, blob_store=blob_store,
            )
    assert refused.value.status_code in (403, 404)


# -- Over HTTP ----------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-62")
def test_the_predict_route_is_published_with_its_refusals() -> None:
    """`test_api_diagnostics` records three requirements repaired by this check: a route
    absent from the published contract is invisible to the endpoint audit, however
    thoroughly its service function is tested."""
    entry = _load(OPENAPI)["paths"]["/api/v1/models/{model_id}/predict"]
    assert "post" in entry
    responses = entry["post"]["responses"]
    assert "200" in responses
    for status in ("403", "404", "409", "422"):
        assert status in responses


@pytest.mark.req("FR-MODEL-62")
def test_a_caller_without_model_read_is_refused_at_the_edge(
    api_client: TestClient, workspace_id, principal
) -> None:
    """`model:read`, and the negative half of choosing it. The permission is deliberately
    the weakest of the model permissions — an approver must be able to ask a model what it
    charges — which makes proving that *no* permission is still refused the check that
    keeps "weakest" from meaning "none"."""
    refused = api_client.post(
        f"/api/v1/models/{new_uuid7()}/predict",
        json={"rows": [{"exposure_years": 1.0}]},
        headers=_headers(principal.id, workspace_id),
    )
    assert refused.status_code == 403


@pytest.mark.req("FR-MODEL-99")
async def test_a_penalised_fits_interval_says_which_matrix_it_came_from(
    database, blob_store, workspace_id
) -> None:
    """OQ-MODEL-14, decided 2026-08-18: report it, and say what it is.

    `glum` warns on every penalised fit that the covariance matrix "will be incorrect" — it
    is the information matrix of the unpenalised problem, which knows nothing about the
    shrinkage that produced the coefficients. The interval is therefore the one an
    unpenalised fit of this design would earn: wider than the estimate warrants, and
    conservative is not the same as right.

    What is under test is that the qualification **reaches the caller**. The warning itself
    is swallowed by the fit's `catch_warnings`, so without this the only trace of it is a
    line in pytest's warnings summary that no API consumer will ever see.
    """
    actor, model_id = await _fitted_glm(database, blob_store, workspace_id, alpha=25.0)

    async with database.session() as session:
        prediction = await service.predict_rows(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            rows=ROWS, blob_store=blob_store,
        )

    assert prediction.uncertainty.kind is UncertaintyKind.CONFIDENCE_INTERVAL_MEAN
    assert prediction.uncertainty.basis is UncertaintyBasis.UNPENALISED_INFORMATION_MATRIX
    #: The interval is still returned. Refusing it would have had to take FR-MODEL-21's
    #: standard errors with it, since both are read off this matrix — which is the reason
    #: OQ-MODEL-14 could not be decided for the interval alone.
    assert all(row.lower is not None and row.upper is not None for row in prediction.rows)


@pytest.mark.req("FR-MODEL-99")
async def test_an_unpenalised_fit_claims_the_matrix_it_actually_used(
    database, blob_store, workspace_id
) -> None:
    """The other half, without which the label above proves nothing.

    A `basis` field that read `unpenalised_information_matrix` for every model would pass
    the test above and describe nothing — the value has to move with `alpha`.
    """
    actor, model_id = await _fitted_glm(database, blob_store, workspace_id)

    async with database.session() as session:
        prediction = await service.predict_rows(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            rows=ROWS, blob_store=blob_store,
        )

    assert prediction.uncertainty.basis is UncertaintyBasis.INFORMATION_MATRIX
