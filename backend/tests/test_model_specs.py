"""Spec validation, and FR-MODEL-81's gate (`02` FR-MODEL-44, FR-MODEL-81, `wf-01` D2).

Two things are being proved, and the second is the one that was missing:

* a spec that cannot be fitted is refused **before any compute**, reporting every reason at
  once rather than the first;
* the complexity limits are a **gate**, not only a diagnostic. The diagnostics slice
  recorded the counts and shipped no gate, and FR-MODEL-81 counted as evidenced anyway
  because a test marked it — `CLAUDE.md` §13's "a marker is a claim, not a proof".
"""

from __future__ import annotations

import pytest
from backend.tests.test_model_jobs import (
    _actuary,
    _dataset,
    _factor,
    _spec,
    _split,
    _validated_version,
)
from backend.tests.test_model_offset_jobs import (
    _base_spec,
    _residual_spec,
    _residual_version,
)
from backend.tests.test_prediction import _fitted_residual_pair

from app.config import Settings
from app.errors import PlatformError
from app.platform import model_specs as spec_service
from app.platform import modelling as model_service
from app.platform import settings as settings_service
from app.platform import workspaces
from model_schema import (
    SURROGATE_RESPONSE_COLUMN,
    Factor,
    FactorType,
    SpecProblemKind,
    new_uuid7,
)


async def _set(database, workspace_id, actor, key, value) -> None:
    async with database.unit_of_work() as session:
        # `workspace_settings` references `workspaces` (FR-PLAT-62) and this helper does
        # not go through `grant`, so the workspace row arrives here.
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        await settings_service.set_workspace_setting(session, workspace_id, key, value)


async def _ready(database, blob_store, workspace_id):
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)
    return actor, dataset_id, version_id, area, split


async def _validate(database, workspace_id, actor, spec):
    async with database.unit_of_work() as session:
        return await spec_service.validate_spec(
            session, Settings(), workspace_id=workspace_id, actor=actor, spec=spec
        )


@pytest.mark.req("FR-MODEL-102")
async def test_a_surrogate_spec_is_not_reported_as_missing_its_response(
    database, blob_store, workspace_id
) -> None:
    """`__gbm_prediction__` is not in any dataset version, and never will be."""
    actor, _, version_id, area, split = await _ready(database, blob_store, workspace_id)
    spec = _spec(
        version_id,
        (area,),
        split_ref=split,
        response_column=SURROGATE_RESPONSE_COLUMN,
        approximates_model_id=new_uuid7(),
    )
    result = await _validate(database, workspace_id, actor, spec)
    assert not [p for p in result.problems if p.kind is SpecProblemKind.RESPONSE_MISSING]


@pytest.mark.req("FR-MODEL-102")
async def test_an_ordinary_spec_still_reports_a_response_column_it_does_not_have(
    database, blob_store, workspace_id
) -> None:
    """The carve-out is for surrogates only — the check it relaxes is the one that catches
    a typo in a response column, and losing it wholesale would be a worse defect than the
    one it fixes."""
    actor, _, version_id, area, split = await _ready(database, blob_store, workspace_id)
    spec = _spec(version_id, (area,), split_ref=split, response_column="claims_kount")
    result = await _validate(database, workspace_id, actor, spec)
    assert [p for p in result.problems if p.kind is SpecProblemKind.RESPONSE_MISSING]


@pytest.mark.req("FR-MODEL-44")
async def test_a_sound_spec_validates(database, blob_store, workspace_id) -> None:
    actor, _, version_id, area, split = await _ready(database, blob_store, workspace_id)
    result = await _validate(
        database, workspace_id, actor, _spec(version_id, (area,), split_ref=split)
    )
    assert result.ok is True
    assert result.problems == ()
    assert result.factor_count == 1
    assert result.estimated_parameter_count >= 2  # intercept + at least one level


@pytest.mark.req("FR-MODEL-44")
async def test_every_problem_is_reported_not_only_the_first(
    database, blob_store, workspace_id
) -> None:
    """`02` §5.3 wants live validation as the form is edited. A validator that stopped at
    the first failure would make a ten-factor spec a ten-round conversation."""
    actor, dataset_id, version_id, _, split = await _ready(
        database, blob_store, workspace_id
    )
    ghost = await _factor(
        database, workspace_id, actor, dataset_id, "ghost", "no_such_column"
    )
    spec = _spec(
        version_id, (ghost, new_uuid7()), split_ref=split, response_column="not_a_column"
    )
    result = await _validate(database, workspace_id, actor, spec)

    kinds = {p.kind for p in result.problems}
    assert result.ok is False
    assert SpecProblemKind.FACTOR_MISSING in kinds
    assert SpecProblemKind.FACTOR_UNRESOLVABLE in kinds
    assert SpecProblemKind.RESPONSE_MISSING in kinds


@pytest.mark.req("FR-MODEL-5")
async def test_a_prohibited_factor_is_named_in_the_problems(
    database, blob_store, workspace_id
) -> None:
    actor, dataset_id, version_id, _, split = await _ready(
        database, blob_store, workspace_id
    )
    async with database.unit_of_work() as session:
        row = await model_service.create_factor(
            session,
            workspace_id=workspace_id,
            actor=actor,
            factor=Factor(
                id=new_uuid7(), slug="postcode", dataset_id=dataset_id, version=1,
                type=FactorType.IDENTITY, source_columns=("area",),
                prohibited=True, prohibited_reason="a protected-characteristic proxy",
            ),
        )
        prohibited = row.id

    result = await _validate(
        database, workspace_id, actor, _spec(version_id, (prohibited,), split_ref=split)
    )
    assert result.ok is False
    problem = next(p for p in result.problems if p.kind is SpecProblemKind.FACTOR_PROHIBITED)
    assert problem.subject == "postcode"


@pytest.mark.req("FR-MODEL-54")
async def test_a_spec_with_no_split_is_reported_before_the_job(
    database, blob_store, workspace_id
) -> None:
    """The fit handler refuses this too, but only after the Job has been queued, accepted
    and started. A `202` followed by a failure is a worse answer to "is this valid?"."""
    actor, _, version_id, area, _ = await _ready(database, blob_store, workspace_id)
    result = await _validate(database, workspace_id, actor, _spec(version_id, (area,)))
    assert result.ok is False
    assert {p.kind for p in result.problems} == {SpecProblemKind.SPLIT_MISSING}


# -- FR-MODEL-81: the gate, not only the diagnostic -----------------------------------------


@pytest.mark.req("FR-MODEL-81")
async def test_no_limit_is_set_by_default(database, blob_store, workspace_id) -> None:
    """OQ-MODEL-6 refused a platform-wide constant. Unset means no gate — not a gate at
    zero, which nothing could satisfy."""
    actor, _, version_id, area, split = await _ready(database, blob_store, workspace_id)
    result = await _validate(
        database, workspace_id, actor, _spec(version_id, (area,), split_ref=split)
    )
    assert result.max_factor_count is None
    assert result.min_exposure_per_parameter is None
    assert result.ok is True


@pytest.mark.req("FR-MODEL-81")
async def test_a_workspace_factor_limit_refuses_a_breaching_spec(
    database, blob_store, workspace_id
) -> None:
    """The same spec, accepted and then refused when the limit moves below it.

    Both directions matter: a test that only saw the refusal would pass against a gate
    that refused everything, and one that only saw the acceptance would pass against a
    gate that never fired."""
    actor, dataset_id, version_id, area, split = await _ready(
        database, blob_store, workspace_id
    )
    second = await _factor(
        database, workspace_id, actor, dataset_id, "amount", "claim_amount_minor"
    )
    spec = _spec(version_id, (area, second), split_ref=split)

    assert (await _validate(database, workspace_id, actor, spec)).ok is True

    await _set(database, workspace_id, actor, "modelling.max_factor_count", 1)
    refused = await _validate(database, workspace_id, actor, spec)

    assert refused.ok is False
    problem = next(p for p in refused.problems if p.kind is SpecProblemKind.COMPLEXITY_LIMIT)
    assert problem.subject == "modelling.max_factor_count"
    assert refused.factor_count == 2
    assert refused.max_factor_count == 1


@pytest.mark.req("FR-MODEL-81")
async def test_an_exposure_per_parameter_limit_refuses_and_is_audited(
    database, blob_store, workspace_id
) -> None:
    """The gate half of FR-MODEL-81, which the diagnostics slice did not deliver.

    The threshold is set absurdly high rather than the spec made absurdly complex, because
    what is under test is that the limit *fires*, not that a large spec can be built."""
    from sqlalchemy import select

    from app.db.models import AuditEventRow

    actor, _, version_id, area, split = await _ready(database, blob_store, workspace_id)
    spec = _spec(version_id, (area,), split_ref=split)

    assert (await _validate(database, workspace_id, actor, spec)).ok is True

    await _set(database, workspace_id, actor, "modelling.min_exposure_per_parameter", 1e9)
    refused = await _validate(database, workspace_id, actor, spec)

    assert refused.ok is False
    problem = next(p for p in refused.problems if p.kind is SpecProblemKind.COMPLEXITY_LIMIT)
    assert problem.subject == "modelling.min_exposure_per_parameter"
    assert refused.exposure_per_parameter is not None

    # FR-MODEL-81 requires the refusal to be audited.
    async with database.session() as session:
        actions = (
            await session.execute(
                select(AuditEventRow.action).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "model_spec.refused_for_complexity",
                )
            )
        ).scalars().all()
    assert actions, "the complexity refusal is audited"


@pytest.mark.req("FR-MODEL-81")
async def test_the_gate_also_refuses_at_post_models(
    database, blob_store, workspace_id
) -> None:
    """The requirement names **both** entry points. A gate on the validator alone would be
    advisory — a caller can skip validation and post the spec."""
    actor, _, version_id, area, split = await _ready(database, blob_store, workspace_id)
    spec = _spec(version_id, (area,), split_ref=split)

    await _set(database, workspace_id, actor, "modelling.min_exposure_per_parameter", 1e9)

    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await spec_service.enforce_complexity(
                session, Settings(), workspace_id=workspace_id, actor=actor, spec=spec
            )
    assert refused.value.code == "MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT"
    assert refused.value.status_code == 422


@pytest.mark.req("FR-MODEL-81")
async def test_the_gate_costs_nothing_when_no_limit_is_set(
    database, blob_store, workspace_id
) -> None:
    """Negative of the gate: with both settings unset it must not refuse, and must not
    read the version or its profile to decide that."""
    actor, _, version_id, area, split = await _ready(database, blob_store, workspace_id)
    async with database.unit_of_work() as session:
        await spec_service.enforce_complexity(
            session, Settings(), workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), split_ref=split),
        )


# -- FR-MODEL-24: a `kind="model"` offset's ref resolves before a job is queued ------------


async def _residual_ready(database, blob_store, workspace_id):
    """`_ready` for a model-offset spec: the residual book's validated version, its
    `resid_flag` factor and its split (FR-MODEL-24)."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _residual_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    resid_flag = await _factor(
        database, workspace_id, actor, dataset_id, "resid_flag", "resid_flag"
    )
    split = await _split(database, blob_store, workspace_id, actor, version_id)
    return actor, dataset_id, version_id, resid_flag, split


@pytest.mark.req("FR-MODEL-24")
async def test_a_ref_naming_no_model_is_reported_before_the_job(
    database, blob_store, workspace_id
) -> None:
    """`model:ghost@1` resolves to nothing. The problem is reported here, before a Job is
    queued — the fit handler's refusal would arrive after a 202 (`wf-01` D2, FR-MODEL-44)."""
    actor, _, version_id, resid_flag, split = await _residual_ready(
        database, blob_store, workspace_id
    )
    result = await _validate(
        database, workspace_id, actor,
        _residual_spec(version_id, resid_flag, split, ref="model:ghost@1"),
    )
    assert result.ok is False
    problem = next(
        p for p in result.problems
        if p.kind is SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE
    )
    assert problem.subject == "model:ghost@1"


@pytest.mark.req("FR-MODEL-24")
async def test_a_ref_naming_an_unfitted_model_is_reported_before_the_job(
    database, blob_store, workspace_id
) -> None:
    """A reservation with no fit has no linear predictor to offset against: the ref's
    problem, reported here rather than as a failed job."""
    actor, _, version_id, resid_flag, split = await _residual_ready(
        database, blob_store, workspace_id
    )
    async with database.unit_of_work() as session:
        unfitted, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_base_spec(version_id, resid_flag, split),
        )
        unfitted_ref = f"model:{unfitted.model_family_slug}@{unfitted.version}"

    result = await _validate(
        database, workspace_id, actor,
        _residual_spec(version_id, resid_flag, split, ref=unfitted_ref),
    )
    assert result.ok is False
    problem = next(
        p for p in result.problems
        if p.kind is SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE
    )
    assert problem.subject == unfitted_ref


@pytest.mark.req("FR-MODEL-24")
async def test_a_link_mismatch_is_reported_before_the_job(
    database, blob_store, workspace_id
) -> None:
    """The offset would be a number from another scale: the referenced model's link must
    equal the new spec's, and the validator says so before the job is queued."""
    pair = await _fitted_residual_pair(database, blob_store, workspace_id)
    result = await _validate(
        database, workspace_id, pair.actor,
        _residual_spec(
            pair.v2_id, pair.resid_flag_id, pair.split2, ref=pair.ref, link="identity"
        ),
    )
    assert result.ok is False
    problem = next(
        p for p in result.problems
        if p.kind is SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE
    )
    assert problem.subject == pair.ref


@pytest.mark.req("FR-MODEL-24")
async def test_a_valid_offset_ref_is_not_reported_as_unresolvable(
    database, blob_store, workspace_id
) -> None:
    """The clean case: the ref names a fitted GLM whose link is the new spec's, so the
    validator resolves it and reports nothing about the offset."""
    pair = await _fitted_residual_pair(database, blob_store, workspace_id)
    result = await _validate(
        database, workspace_id, pair.actor,
        _residual_spec(pair.v2_id, pair.resid_flag_id, pair.split2, ref=pair.ref),
    )
    assert result.ok is True
    assert [p for p in result.problems
            if p.kind is SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE] == []
