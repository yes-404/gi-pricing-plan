"""The FR-240 family at the platform seam (`PL-1471`, SL-1472).

Approval refuses a model over an unapproved custom objective (`02` R4, `06` FR-359); the
compile Job refuses what approval could not catch (`03` FR-240); a `control`-intent Factor
never reaches a rateable path (`02` FR-88). Each test names the cause it is red by at the
slice's base in the ledger (`LG-1533`, build log).
"""

from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid5

import pytest
from backend.tests.approved_rows import mark_approved
from backend.tests.test_api_rate_tables import (
    _LEVELS,
    _run_with_database,
    _seed_approved_model,
    _seed_body,
    _table_slug,
)
from backend.tests.test_custom_objectives_api import _advance, _create
from backend.tests.test_expression_objective_fit import _expression_objective, _fit
from backend.tests.test_glm_approximation_model import _transparency_job
from backend.tests.test_model_jobs import _actuary
from backend.tests.test_model_jobs_gbm import _fitted_gbm
from backend.tests.test_model_lifecycle import _principal_with
from backend.tests.test_rate_tables_service import _seed as _seed_rate_table
from backend.tests.test_rate_tables_service import _table_slug as _compile_table_slug
from backend.tests.test_rating_version_compile import (
    _headers,
    _insert_version,
    _minimal_algorithm,
    _read_blob,
    _run_compile_job,
)
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    FactorRow,
    ModelRow,
    RateTableCellRow,
    RateTableRow,
    RateTableVersionRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as approval_service
from app.platform import modelling as service
from app.platform.blobs import BlobStore
from app.worker.rating_handlers import register_rating_handlers
from model_schema import (
    DecisionKind,
    Factor,
    FactorIntent,
    FactorType,
    JobStatus,
    ModelFlag,
    ModelStatus,
    ObjectiveStatus,
    new_uuid7,
)
from pricing_core.rating.compile import Bundle
from pricing_core.rating.runtime import load_bundle


@pytest.fixture(autouse=True)
def _handlers() -> None:
    register_rating_handlers()



async def _set_objective_status(database: Database, ref: str, status: str) -> None:
    """Move a certified objective to `status`; the certificate stays, so the CHECK holds."""
    slug, version = ref.removeprefix("custom_objective:").split("@")
    async with database.unit_of_work() as session:
        await session.execute(
            text("UPDATE custom_objectives SET status = :s WHERE slug = :slug AND version = :v"),
            {"s": status, "slug": slug, "v": int(version)},
        )


async def _gbm_over_objective(
    database: Database, blob_store: BlobStore, workspace_id: Any, *, objective_status: str
) -> tuple[UUID, str]:
    """A fitted GBM whose custom objective is `objective_status` at the end."""
    # `approved` is written only through `mark_approved` (the 06 FR-351 trigger); any other
    # status is moved by SQL from the `certified` the fixture's Job leaves.
    ref = await _expression_objective(
        database, blob_store, workspace_id, approve=objective_status == "approved"
    )
    model_id, fit_status = await _fit(database, blob_store, workspace_id, ref)
    assert fit_status is JobStatus.SUCCEEDED
    if objective_status not in ("approved", "certified"):
        await _set_objective_status(database, ref, objective_status)
    return model_id, ref


async def _submit_and_decide(
    database: Database, blob_store: BlobStore, workspace_id: Any, model_id: UUID
) -> Any:
    actor = await _actuary(database, workspace_id)
    approver = await _principal_with(database, workspace_id, "approver")
    await _transparency_job(database, blob_store, workspace_id, model_id, actor)
    async with database.unit_of_work() as session:
        _, request = await service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            change_summary="ready for review",
        )
        request_id = request.id
    async with database.unit_of_work() as session:
        decided = await approval_service.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE, comment="looks fine to me",
        )
    return approver, decided


async def _status_of(database: Database, model_id: UUID) -> str:
    async with database.session() as session:
        return (
            await session.execute(select(ModelRow.status).where(ModelRow.id == model_id))
        ).scalar_one()


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
@pytest.mark.req("FR-359")
async def test_a_model_whose_custom_objective_is_in_review_cannot_be_approved(
    database, blob_store, workspace_id
) -> None:
    """FD-1469 §3: the approval went through over a `review` objective (`02` R4)."""
    model_id, ref = await _gbm_over_objective(
        database, blob_store, workspace_id, objective_status="review"
    )
    approver, decided = await _submit_and_decide(database, blob_store, workspace_id, model_id)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.apply_approval_decision(
                session, workspace_id=workspace_id, actor=approver, request=decided
            )
    assert refused.value.code == "ARTIFACT_FLAGGED"
    assert refused.value.status_code == 409
    assert "custom_objective_not_approved" in str(refused.value.detail)
    assert ref in str(refused.value.detail)
    assert await _status_of(database, model_id) == ModelStatus.REVIEW.value


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
@pytest.mark.req("FR-359")
async def test_an_approved_objective_can_be_approved(
    database, blob_store, workspace_id
) -> None:
    """The control: the same chain over an `approved` objective reaches `approved`."""
    model_id, _ = await _gbm_over_objective(
        database, blob_store, workspace_id, objective_status="approved"
    )
    approver, decided = await _submit_and_decide(database, blob_store, workspace_id, model_id)
    async with database.unit_of_work() as session:
        await service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=decided
        )
    assert await _status_of(database, model_id) == ModelStatus.APPROVED.value


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
@pytest.mark.req("FR-359")
async def test_flags_for_names_an_unapproved_objective(
    database, blob_store, workspace_id
) -> None:
    model_id, _ = await _gbm_over_objective(
        database, blob_store, workspace_id, objective_status="review"
    )
    async with database.session() as session:
        row = (await session.execute(select(ModelRow).where(ModelRow.id == model_id))).scalar_one()
        flags = await service.flags_for(session, workspace_id=workspace_id, row=row)
    assert flags == (ModelFlag.CUSTOM_OBJECTIVE_NOT_APPROVED,)


# -- Compile: the Job refuses what approval could not catch (FR-240) ----------------------


def _run(coro: Any) -> Any:
    return asyncio.get_event_loop().run_until_complete(coro)


def _compile_with_pins(
    api_client, principal, workspace_id, database, blob_store, *, models=(), objectives=(),
    rate_tables=(), algorithm=None,
) -> Any:
    headers = _headers(principal, workspace_id)
    algorithm = algorithm or _minimal_algorithm()
    created = api_client.post("/api/v1/rating-algorithms", json=algorithm, headers=headers)
    assert created.status_code == 201, created.text
    row = _run(
        _insert_version(
            database, workspace_id, principal.id,
            algorithm_ref=f"rating_algorithm:{algorithm['slug']}@1",
            pins={
                "rate_tables": list(rate_tables), "models": list(models), "reference_tables": [],
                "custom_objectives": list(objectives),
            },
        )
    )
    return _run_compile_job(api_client, headers, database, blob_store, row.id)


@pytest.mark.req("FR-240")
@pytest.mark.parametrize("status", [ObjectiveStatus.CERTIFIED, ObjectiveStatus.REVIEW])
def test_a_version_pinning_an_unapproved_custom_objective_fails_to_compile(
    api_client, workspace_id, principal, grant, database, blob_store, status
) -> None:
    """Green at the base, by design: the direct refusal exists but had no negative test.
    Its proof is a broken-input run (Acceptance 8), recorded in the ledger."""
    _run(grant("analyst"))
    objective = _create(api_client, _headers(principal, workspace_id))
    _advance(UUID(objective["id"]), status=status)
    ref = f"custom_objective:{objective['slug']}@{objective['version']}"
    job_row = _compile_with_pins(
        api_client, principal, workspace_id, database, blob_store, objectives=[ref]
    )
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "PIN_NOT_APPROVED"


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-359")
def test_an_overridden_flag_never_reaches_compile(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """DP-1's condition: flag -> override -> approved -> compile still REFUSES.

    FR-359's Admin override is built for no flag (`apply_approval_decision` raises for every
    flag), so `approved` is reached with `mark_approved`, the one way an `approved` row over
    a flagged model can exist today (an override, or an approval from before the flag). The
    assertion that compile refuses does not depend on how `approved` was reached.
    """
    _run(grant("analyst"))

    async def _arrange() -> str:
        model_id, _ = await _gbm_over_objective(
            database, blob_store, workspace_id, objective_status="review"
        )
        async with database.unit_of_work() as session:
            row = await session.get(ModelRow, model_id)
            assert row is not None
            await mark_approved(session, row)
            return f"model:{row.model_family_slug}@{row.version}"

    model_ref = _run(_arrange())
    job_row = _compile_with_pins(
        api_client, principal, workspace_id, database, blob_store, models=[model_ref]
    )
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "PIN_NOT_APPROVED"


# -- A control-intent Factor: the seed route and the compile Job (FR-88, DP-3, DP-4) -------


async def _control_version(session: AsyncSession, workspace_id: Any, slug: str) -> int:
    """Insert the next version of the workspace's Factor `slug` with `intent: control`, the way a
    later edit would (`factors` is append-only at the database, SL-1770: a Factor is versioned,
    never flipped), and return its version number."""
    latest = await session.scalar(
        select(FactorRow)
        .where(FactorRow.workspace_id == workspace_id, FactorRow.slug == slug)
        .order_by(FactorRow.version.desc())
        .limit(1)
    )
    version = 1 if latest is None else latest.version + 1
    dataset_id = new_uuid7() if latest is None else latest.dataset_id
    factor = Factor(
        id=new_uuid7(), slug=slug, dataset_id=dataset_id, version=version,
        type=FactorType.IDENTITY, source_columns=(slug,), intent=FactorIntent.CONTROL,
    )
    session.add(
        FactorRow(
            workspace_id=workspace_id, dataset_id=dataset_id, slug=slug, version=version,
            body=factor.model_dump(mode="json", exclude={"id", "version", "dataset_id"}),
        )
    )
    await session.flush()
    return version


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-230")
@pytest.mark.req("FR-240")
def test_the_seed_route_refuses_a_control_factor_with_its_code(
    api_client, workspace_id, principal, grant
) -> None:
    _run(grant("pricing_actuary"))
    family = f"mf-{new_uuid7().hex[-8:]}"
    control: dict[str, int] = {}

    async def _insert(session: AsyncSession) -> None:
        control["version"] = await _control_version(session, workspace_id, "driver_age_band")

    _run_with_database(_insert)
    _seed_approved_model(
        workspace_id, family, _LEVELS, factor_versions={"driver_age_band": control["version"]}
    )
    response = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json=_seed_body(family),
        headers=_headers(principal, workspace_id),
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "CONTROL_FACTOR_IN_RATEABLE_PATH"


def _seed_over_an_interaction(
    api_client, workspace_id, principal, *, operand_intent: FactorIntent
) -> Any:
    """POST the seed route for a model that pins ONLY an interaction Factor whose operands are
    `crossed_a` (intent `operand_intent`) and `crossed_b` (risk). The operands are never in
    `spec.factors`, so the guard sees them only through `load_factors`' transitive load (SL 8429
    review LOW 3; the core analogues are `test_rating_compile_fr240.py`'s `_seed_cross` tests)."""
    suffix = new_uuid7().hex[-8:]
    cross_slug = f"crossed_{suffix}"

    async def _insert(session: AsyncSession) -> None:
        dataset_id = new_uuid7()
        operands = [
            Factor(
                id=new_uuid7(), slug=f"{name}_{suffix}", dataset_id=dataset_id, version=1,
                type=FactorType.IDENTITY, source_columns=(f"{name}_{suffix}",), intent=intent,
            )
            for name, intent in (("crossed_a", operand_intent), ("crossed_b", FactorIntent.RISK))
        ]
        cross = Factor(
            id=new_uuid7(), slug=cross_slug, dataset_id=dataset_id, version=1,
            type=FactorType.INTERACTION, source_columns=(),
            operand_factor_ids=tuple(operand.id for operand in operands),
        )
        for factor in (*operands, cross):
            session.add(
                FactorRow(
                    id=factor.id, workspace_id=workspace_id, dataset_id=dataset_id,
                    slug=factor.slug, version=1,
                    body=factor.model_dump(mode="json", exclude={"id", "version", "dataset_id"}),
                )
            )
        await session.flush()

    _run_with_database(_insert)
    family = f"mf-{suffix}"
    _seed_approved_model(workspace_id, family, {cross_slug: [("A | 2010", 1.1)]})
    return api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json=_seed_body(family, factor=cross_slug),
        headers=_headers(principal, workspace_id),
    )


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-230")
@pytest.mark.req("FR-240")
def test_the_seed_route_refuses_an_interaction_over_a_control_operand(
    api_client, workspace_id, principal, grant
) -> None:
    """The route refuses with the core path's named error, naming the OPERAND."""
    _run(grant("pricing_actuary"))
    response = _seed_over_an_interaction(
        api_client, workspace_id, principal, operand_intent=FactorIntent.CONTROL
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "CONTROL_FACTOR_IN_RATEABLE_PATH"
    assert "crossed_a_" in response.text


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-230")
@pytest.mark.req("FR-240")
def test_the_seed_route_seeds_an_interaction_over_risk_operands(
    api_client, workspace_id, principal, grant
) -> None:
    """The instrument control: the same shape over a RISK operand seeds, so the refusal above
    is the intent and not the interaction."""
    _run(grant("pricing_actuary"))
    response = _seed_over_an_interaction(
        api_client, workspace_id, principal, operand_intent=FactorIntent.RISK
    )
    assert response.status_code == 201, response.text


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_a_compile_over_a_control_keyed_table_fails_with_its_code(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """The table is seeded while its Factor is `risk`; the Factor is then `control`, so the
    pinned table's key is bound to a control Factor and compile is the backstop (DP-3)."""
    _run(grant("analyst"))
    family = f"mf-{new_uuid7().hex[-8:]}"
    seeded = _run(
        _seed_rate_table(
            database, workspace_id, principal, family, _compile_table_slug(), blob_store
        )
    )

    async def _rebind() -> int:
        """A new rate-table version whose key names a control version of its Factor."""
        async with database.unit_of_work() as session:
            control = await _control_version(session, workspace_id, "driver_age_band")
            table = await session.scalar(
                select(RateTableRow).where(
                    RateTableRow.workspace_id == workspace_id,
                    RateTableRow.slug == seeded.slug,
                )
            )
            assert table is not None
            source = await session.scalar(
                select(RateTableVersionRow).where(
                    RateTableVersionRow.rate_table_id == table.id,
                    RateTableVersionRow.version_number == seeded.version,
                )
            )
            assert source is not None
            definition = json.loads(json.dumps(source.definition))
            for key in definition["keys"]:
                key["factor_ref"] = f"factor:driver_age_band@{control}"
            session.add(
                RateTableVersionRow(
                    workspace_id=source.workspace_id,
                    rate_table_id=source.rate_table_id,
                    version_number=seeded.version + 1,
                    storage=source.storage,
                    definition=definition,
                    change_note=source.change_note,
                    seeded_from=source.seeded_from,
                    cells=source.cells,
                    created_by_operation=source.created_by_operation,
                    created_by_import=source.created_by_import,
                    created_by_edit=source.created_by_edit,
                    created_by=source.created_by,
                )
            )
            return seeded.version + 1

    rebound = _run(_rebind())
    job_row = _compile_with_pins(
        api_client, principal, workspace_id, database, blob_store,
        rate_tables=[f"rate_table:{seeded.slug}@{rebound}"],
    )
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "CONTROL_FACTOR_IN_RATEABLE_PATH"


def _model_call_algorithm(model_ref: str) -> dict[str, Any]:
    """Input -> a `model_call` over `model_ref` -> output."""
    return {
        "slug": "mc-control",
        "version": 1,
        "input_contract": [{"name": "area", "type": "string", "nullable": False}],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "Area", "input_name": "area",
             "on_missing": "error", "produces": "area"},
            {"step_id": "s_mc", "type": "model_call", "label": "Risk premium",
             "model_ref": model_ref, "mode": "exact", "feature_map": {"area": "area"},
             "consumes": ["area"], "produces": ["risk_premium_minor", "peril_risk_premium"]},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["risk_premium_minor"]},
        ],
        "sub_graphs": [],
    }


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_a_compile_over_a_gbm_fitted_on_a_control_factor_fails_with_its_code(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """FD 9639 (DP-7): the GBM is fitted on `area`, which is then a `control` Factor; the
    approved model is pinned by a `model_call` and the Job refuses it."""
    _run(grant("analyst"))

    async def _arrange() -> str:
        model_id, fit_status = await _fitted_gbm(
            database, blob_store, workspace_id, area_intent=FactorIntent.CONTROL
        )
        assert fit_status is JobStatus.SUCCEEDED
        async with database.unit_of_work() as session:
            row = await session.get(ModelRow, model_id)
            assert row is not None
            await mark_approved(session, row)
            return f"model:{row.model_family_slug}@{row.version}"

    model_ref = _run(_arrange())
    headers = _headers(principal, workspace_id)
    created = api_client.post(
        "/api/v1/rating-algorithms", json=_model_call_algorithm(model_ref), headers=headers
    )
    assert created.status_code == 201, created.text
    row = _run(
        _insert_version(
            database, workspace_id, principal.id,
            algorithm_ref="rating_algorithm:mc-control@1",
            pins={"rate_tables": [], "models": [model_ref], "reference_tables": [],
                  "custom_objectives": []},
        )
    )
    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "CONTROL_FACTOR_IN_RATEABLE_PATH"


# -- An interaction-keyed table through the REAL compile resolver (FD-1495, WK-2113 S1) ------
#
# The `factor` branch of `WorkspaceResolver` returns the Factor plus the operands it crosses
# (`load_factor_by_ref`), which is what lets the pricing-core key guard test every operand's
# intent. These two tests drive that branch end to end, not a hand-built `ResolvedArtifact`.


# Every id and value below is fixed or derived from the workspace id, so a run is repeatable: the
# bundle's content hash reads the pinned refs (slugs and versions) and the graph, never a row id.
_TABLE_SLUG = "sl8429-region-x-yoa"
_CELLS = (("north | 2010", "1.05"), ("north | 2011", "1.10"), ("south | 2010", "0.95"))
# The content hash of the risk-by-risk compile test's
# bundle, measured at 2ba0d0d5's code (before the control-intent guards read an interaction's
# operands) in the DB lane, 2026-11-13 21:50 GMT, for the lookup algorithm; the fixed head's
# first assertion printed the same value.
# A change to it is a change to what FR-239 promises: the same pins, the same hash.
_PRE_FIX_RISK_BY_RISK_HASH = (
    "sha256:3948d954eb79b84aa89f20dca3ecd8e5d9f8b56bf61981b24fa1899c923424f8"
)


_LOOKUP_ALGORITHM_SLUG = "sl8429-lookup"


def _lookup_algorithm(key_name: str) -> dict[str, Any]:
    """`premium_in * <relativity looked up on the cross's level>`: a real cell prices."""
    return {
        "slug": _LOOKUP_ALGORITHM_SLUG,
        "version": 1,
        "input_contract": [
            {"name": "premium_in", "type": "int", "nullable": False},
            {"name": key_name, "type": "string", "nullable": False},
        ],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "Premium", "input_name": "premium_in",
             "on_missing": "error", "produces": "premium_in"},
            {"step_id": "s_key", "type": "input", "label": "Level", "input_name": key_name,
             "on_missing": "error", "produces": key_name},
            {"step_id": "s_tbl", "type": "table", "label": "Relativity",
             "rate_table_ref": f"rate_table:{_TABLE_SLUG}@1", "key_expr": [key_name],
             "on_miss": "error", "consumes": [key_name], "produces": "relativity"},
            {"step_id": "s_expr", "type": "expression", "label": "Apply",
             "expr": "premium_in * relativity", "result_type": "decimal",
             "consumes": ["premium_in", "relativity"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }


def _factor_row(workspace_id: Any, dataset_id: UUID, factor: Factor) -> FactorRow:
    return FactorRow(
        id=factor.id, workspace_id=workspace_id, dataset_id=dataset_id, slug=factor.slug,
        version=1, body=factor.model_dump(mode="json", exclude={"id", "version", "dataset_id"}),
    )


async def _cross_factors(
    session: AsyncSession, workspace_id: Any, *, second_operand_intent: FactorIntent,
    nested: bool = False,
) -> str:
    """Factors `region` (risk) and `yoa` (`second_operand_intent`) and the interaction
    `region_x_yoa` crossing them; returns the interaction's ref.

    With `nested`, `region_x_yoa` is itself an operand of the pinned `outer_x_plan` (depth 2),
    the shape `load_factors` once loaded one level of only; the ref returned is the outer one."""
    dataset_id = uuid5(workspace_id, "dataset")

    def _id(name: str) -> UUID:
        return uuid5(workspace_id, name)

    operands = []
    for slug, intent in (("region", FactorIntent.RISK), ("yoa", second_operand_intent)):
        factor = Factor(
            id=_id(slug), slug=slug, dataset_id=dataset_id, version=1,
            type=FactorType.IDENTITY, source_columns=(slug,), intent=intent,
        )
        session.add(_factor_row(workspace_id, dataset_id, factor))
        operands.append(factor)
    cross = Factor(
        id=_id("region_x_yoa"), slug="region_x_yoa", dataset_id=dataset_id, version=1,
        type=FactorType.INTERACTION, source_columns=(),
        operand_factor_ids=tuple(operand.id for operand in operands),
    )
    session.add(_factor_row(workspace_id, dataset_id, cross))
    if not nested:
        await session.flush()
        return f"factor:{cross.slug}@{cross.version}"
    plan = Factor(
        id=_id("plan"), slug="plan", dataset_id=dataset_id, version=1,
        type=FactorType.IDENTITY, source_columns=("plan",),
    )
    outer = Factor(
        id=_id("outer_x_plan"), slug="outer_x_plan", dataset_id=dataset_id, version=1,
        type=FactorType.INTERACTION, source_columns=(),
        operand_factor_ids=(cross.id, plan.id),
    )
    session.add(_factor_row(workspace_id, dataset_id, plan))
    session.add(_factor_row(workspace_id, dataset_id, outer))
    await session.flush()
    return f"factor:{outer.slug}@{outer.version}"


async def _table_keyed_on(
    session: AsyncSession, workspace_id: Any, principal: Any, factor_ref: str, key_name: str
) -> str:
    """A rateable rows-stored table with real cells whose one key names `factor_ref`; returns
    its pin."""
    table_id, version_id = uuid5(workspace_id, "table"), uuid5(workspace_id, "table-version")
    session.add(
        RateTableRow(
            id=table_id, workspace_id=workspace_id, slug=_TABLE_SLUG, current_version=1,
            created_by=principal.id,
        )
    )
    await session.flush()
    session.add(
        RateTableVersionRow(
            id=version_id, workspace_id=workspace_id, rate_table_id=table_id, version_number=1,
            storage="rows",
            definition={
                "slug": _TABLE_SLUG, "version": 1, "rateable": True, "storage": "rows",
                "keys": [
                    {"name": key_name, "type": "string", "banding_ref": None,
                     "factor_ref": factor_ref}
                ],
                "value": {"name": "relativity", "type": "relativity", "unit": "factor",
                          "min": None, "max": None},
                "default_row": None,
            },
            change_note="interaction-keyed, FD-1495",
            created_by=principal.id,
        )
    )
    await session.flush()
    session.add_all(
        RateTableCellRow(version_id=version_id, key=[key], value=value) for key, value in _CELLS
    )
    await session.flush()
    return f"rate_table:{_TABLE_SLUG}@1"


def _compile_interaction_keyed(
    api_client, principal, workspace_id, database, blob_store, *,
    second_operand_intent: FactorIntent, nested: bool = False, lookup: bool = False,
) -> Any:
    async def _arrange() -> str:
        async with database.unit_of_work() as session:
            ref = await _cross_factors(
                session, workspace_id, second_operand_intent=second_operand_intent,
                nested=nested,
            )
            return await _table_keyed_on(
                session, workspace_id, principal, ref, ref.removeprefix("factor:").split("@")[0]
            )

    pin = _run(_arrange())
    return _compile_with_pins(
        api_client, principal, workspace_id, database, blob_store, rate_tables=[pin],
        algorithm=_lookup_algorithm("region_x_yoa") if lookup else None,
    )


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-239")
@pytest.mark.req("FR-240")
def test_a_risk_by_risk_interaction_keyed_table_compiles_with_an_unchanged_hash(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """The green guard: the fix must not refuse what was priceable, and must not move the hash
    (FR-239: the same pins and graph, the same content hash). The fixture is deterministic and the
    table has real cells; `_PRE_FIX_RISK_BY_RISK_HASH` is what 2ba0d0d5's code printed for it."""
    _run(grant("analyst"))
    job_row = _compile_interaction_keyed(
        api_client, principal, workspace_id, database, blob_store,
        second_operand_intent=FactorIntent.RISK, lookup=True,
    )
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    bundle = Bundle.model_validate_json(_read_blob(database, blob_store, job_row.result["ref"]))
    # What a bundle carries is the pinned artifacts only (`compile_bundle`: `payloads` is the
    # algorithm and every pin). The key's Factor is resolved for the guard and not carried, so
    # the interaction chain is NOT in `resolved_payloads`; the table, with its real cells, is.
    table = f"rate_table:{_TABLE_SLUG}@1"
    assert set(bundle.resolved_payloads) == {
        table, f"rating_algorithm:{_LOOKUP_ALGORITHM_SLUG}@1"
    }
    rows = bundle.resolved_payloads[table]["rows"]
    carried = {(row["region_x_yoa"], row["relativity"]) for row in rows}
    assert carried == set(_CELLS)
    assert bundle.content_hash == _PRE_FIX_RISK_BY_RISK_HASH
    # A real cell prices: `north | 2011` carries 1.10, so a premium of 1000 prices to 1100.
    scored = load_bundle(bundle).decision.evaluate(
        {"premium_in": 1000, "region_x_yoa": "north | 2011"}
    )["result"]
    assert Decimal(str(scored["payable"])) == Decimal(1100)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_a_clean_depth_two_interaction_keyed_table_compiles(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """F-3 (a): `outer_x_plan` crosses `region_x_yoa` crosses two risk leaves. Loading the whole
    chain means a legitimate table is not refused for a loader reason."""
    _run(grant("analyst"))
    job_row = _compile_interaction_keyed(
        api_client, principal, workspace_id, database, blob_store,
        second_operand_intent=FactorIntent.RISK, nested=True,
    )
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_a_depth_two_interaction_keyed_table_with_a_control_leaf_is_refused_by_the_guard(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """F-3: `outer_x_plan` crosses `region_x_yoa` crosses `yoa` (control). The real resolver loads
    the whole chain, so the refusal is the named control one and names `yoa`, not the
    fail-closed "not among the Factors supplied" a one-level load produced."""
    _run(grant("analyst"))
    job_row = _compile_interaction_keyed(
        api_client, principal, workspace_id, database, blob_store,
        second_operand_intent=FactorIntent.CONTROL, nested=True,
    )
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "CONTROL_FACTOR_IN_RATEABLE_PATH"
    assert "yoa" in json.dumps(job_row.error)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_an_interaction_keyed_table_with_a_control_operand_fails_to_compile_with_its_code(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """The same table as the test above with `yoa` declared `control`: refused with the named
    error, which is only possible because the resolver supplies the operand chain."""
    _run(grant("analyst"))
    job_row = _compile_interaction_keyed(
        api_client, principal, workspace_id, database, blob_store,
        second_operand_intent=FactorIntent.CONTROL,
    )
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "CONTROL_FACTOR_IN_RATEABLE_PATH"
