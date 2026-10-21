"""WF-699 — approved Models to an approved Rating Version, walked over HTTP (PL-1544, SL-1527).

`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md` is the journey this
file proves: `examples/fremtpl2/journey.py` is an `httpx` client of `/api/v1` that walks its
phases A to E and its deploy step, and these tests run that module against the app in process.

The journey is a cheap-to-fake thing: a client that returns `ok` for every step proves nothing.
So each test below asserts a *code* the API returned, not only that a call succeeded, and the
skip lines are asserted by their exact text (PL-1544 Acceptance 2).

Marker form: `scripts/req-coverage.py` reads only the decorator form of the `req` marker with an
FR or NFR id, and a workflow id is not one, so (as `test_wf01_journey.py` does for `WF-698`)
the requirement ids the journey exercises are the markers and `WF-699` is named here and in
the test names.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Final

import httpx
import pytest

_EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "fremtpl2"
sys.path.insert(0, str(_EXAMPLE))  # `journey.py` imports its sibling `algorithm`
_SPEC = importlib.util.spec_from_file_location("demo_journey", _EXAMPLE / "journey.py")
assert _SPEC is not None
assert _SPEC.loader is not None
journey = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = journey
_SPEC.loader.exec_module(journey)


@pytest.mark.req("FR-257")
def test_wf699_the_skip_and_known_gap_lines_are_exactly_the_ruled_ones() -> None:
    """PL-1544 Acceptance 2 (Amendment 1, DP-b2 (a)): each line names its phase and owner, and
    none names `FD-1456` as a `KNOWN GAP`."""
    assert [entry.line for entry in journey.SKIPS] == [
        "SKIPPED D9: GIPP check; Phase 4; WK-685",
        "SKIPPED E5 inline review: Phase 3; WK-678",
        "SKIPPED E7 Commentary Block: Phase 3; WK-680",
        "KNOWN GAP A6: FD-1491",
        "KNOWN GAP B9: FD-1490",
    ]
    assert not [e for e in journey.SKIPS if e.line.startswith("KNOWN GAP") and "FD-1456" in e.line]
    # `SKIPPED B7: SL-1340` is moot: SL-1340 merged (PL-1544 activation need 18).
    assert not [e for e in journey.SKIPS if "B7" in e.line]


@pytest.mark.req("FR-257")
def test_an_unowned_skip_fails_the_journey() -> None:
    """PL-1544 Acceptance 13: a skip or known gap that names neither an owned finding nor a
    later-phase Work fails the journey for that step, and an owned one does not."""
    owned = journey.Skip(step="D9", line="SKIPPED D9: GIPP check; Phase 4; WK-685")
    unowned = journey.Skip(step="X1", line="SKIPPED X1: not built yet")
    journey.check_skip_owners([owned])
    with pytest.raises(journey.JourneyStepFailed) as failure:
        journey.check_skip_owners([owned, unowned])
    assert failure.value.step == "X1"
    assert str(failure.value).startswith("X1:")


@pytest.mark.req("FR-257")
def test_a_journey_failure_names_its_step() -> None:
    """PL-1544 Acceptance 6: an unexpected status raises `JourneyStepFailed` whose message starts
    with the step id and carries the problem's `code`, so the demo can print one line."""

    def refuse(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422, json={"code": "VALIDATION_FAILED", "detail": "pins: a rate table is missing"}
        )

    with (
        httpx.Client(
            transport=httpx.MockTransport(refuse), base_url="http://journey.test/api/v1"
        ) as client,
        pytest.raises(journey.JourneyStepFailed) as failure,
    ):
        journey.call(client, "C1", "POST", "/rating-versions", json={}, expect=201)
    assert failure.value.step == "C1"
    assert failure.value.code == "VALIDATION_FAILED"
    assert str(failure.value).startswith("C1: VALIDATION_FAILED")


@pytest.mark.req("FR-257")
def test_a_refusal_that_was_expected_is_returned_with_its_code() -> None:
    """The deliberate failures (B6, C4, E3, E8) are asserted by code: a call that expects a
    refusal passes only when both the status and the problem's `code` match."""

    def refuse(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"code": "RATING_GRAPH_UNRESOLVED_REF", "detail": "x"})

    with httpx.Client(
        transport=httpx.MockTransport(refuse), base_url="http://journey.test/api/v1"
    ) as client:
        problem = journey.call(
            client,
            "B6",
            "POST",
            "/rating-algorithms",
            json={},
            expect=422,
            code="RATING_GRAPH_UNRESOLVED_REF",
        )
        assert problem["code"] == "RATING_GRAPH_UNRESOLVED_REF"
        with pytest.raises(journey.JourneyStepFailed) as failure:
            journey.call(
                client,
                "B6",
                "POST",
                "/rating-algorithms",
                json={},
                expect=422,
                code="RATING_GRAPH_CYCLIC",
            )
    assert failure.value.code == "RATING_GRAPH_UNRESOLVED_REF"


@pytest.mark.req("FR-261")
def test_the_d4_property_does_not_depend_on_the_fit() -> None:
    """PL-1544's delta (working id 9799), D4 item 6, and the maintainer's 18:59:23 rule: a
    property chosen from the fit it is checked against can never fail. D4's declaration takes no
    fit at all, equals the ruled constant (premium increasing in `bonus_malus` on 50..230,
    spacing 45) and is valid suite content. Two different fits therefore give the identical
    property: there is nothing to pass one to."""
    import inspect

    from model_schema import RegressionSuiteContent

    assert not inspect.signature(journey.declared_d4_property).parameters
    first, second = journey.declared_d4_property(), journey.declared_d4_property()
    assert (
        first
        == second
        == {
            "name": "premium-increasing-in-bonus-malus",
            "check": {
                "kind": "monotone",
                "input": "bonus_malus",
                "direction": "increasing",
                "strict": False,
                "lower": "50",
                "upper": "230",
            },
        }
    )
    assert journey.D4_GRID_SPACING == 45  # (230 - 50) / 4: the engine's 5-point uniform grid
    RegressionSuiteContent.model_validate(
        {
            "algorithm_slug": "fremtpl2-rate",
            "golden_quotes": [],
            "properties": [first],
            "generation": {"cases": 25, "seed": 1, "strategy": "input_contract_sampling"},
        }
    )
    # the deliberate defect: a middle band wider than the grid spacing
    low, high = journey.LADDER_MIDDLE_EDGES
    assert high - low > journey.D4_GRID_SPACING


@pytest.mark.req("FR-217")
def test_the_ncd_ladder_body_is_a_valid_sub_graph_and_the_defect_differs_only_in_the_middle() -> (
    None
):
    """The ladder is built from `ladder_body` over HTTP (B7); the same body with the defect
    differs from the good one in the middle band alone."""
    from model_schema.sub_graphs import SubGraphBody

    good = journey.ladder_body(journey.LADDER_BANDS["middle"], "good")
    bad = journey.ladder_body(journey.LADDER_DEFECT_MIDDLE, "bad")
    SubGraphBody.model_validate(good)
    SubGraphBody.model_validate(bad)
    assert good["steps"][0]["expr"] != bad["steps"][0]["expr"]
    assert "1.20" in good["steps"][0]["expr"]
    assert "0.90" in bad["steps"][0]["expr"]
    assert bad["steps"][0]["expr"].replace("0.90", "1.20") == good["steps"][0]["expr"]


# -- the journey, end to end, in process ---------------------------------------------------------
#
# The platform under test is the real app on the real database; what is not real is the Celery
# worker, which does not run in a test, so the journey's `run_job` hook executes each accepted Job
# in process (`execute_job`). The principals are the seed's own (`grant_demo_principals`): one
# definition of the set, and RL-1521 binds the journey's steps, not its setup.


def _seed_module() -> Any:
    spec = importlib.util.spec_from_file_location("demo_seed", _EXAMPLE / "seed.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


async def _approved_severity(database: Any, workspace_id: Any, frequency_id: Any) -> Any:
    """An approved severity GLM over the frequency GLM's Factors (as `fit_severity_glm` copies
    them), gamma/log with no offset. Its intercept is `ln(_BASE_MINOR) - the frequency intercept`
    and every level carries relativity 1, so frequency x severity prices a quote exactly as
    `_BASE_MINOR x Π relativities` did: the journey's premiums keep their magnitude."""
    import math
    from copy import deepcopy
    from decimal import Decimal
    from uuid import uuid4

    from backend.tests.approved_rows import add_approved
    from backend.tests.test_demo_rating_evidence import _BASE_MINOR, _INTERCEPT, _fit_result

    from app.db.models import ModelRow
    from model_schema import GlmSpec, ModelStatus, OffsetSpec, ResponseKind

    intercept = float(Decimal(_BASE_MINOR).ln() - _INTERCEPT)
    fit = deepcopy(_fit_result())
    for coefficient in fit["coefficients"]:  # type: ignore[attr-defined]
        if coefficient["term"] == "intercept":
            coefficient.update(
                estimate=intercept, relativity=math.exp(intercept),
                ci_95=[intercept - 0.02, intercept + 0.02],
            )
        else:
            coefficient.update(estimate=0.0, relativity=1.0, ci_95=[-0.02, 0.02])
    for levels in fit["relativities"].values():  # type: ignore[attr-defined]
        for level in levels:
            level.update(relativity=1.0, estimate=0.0)
    family = f"fremtpl2-sev-{uuid4().hex[:6]}"
    async with database.unit_of_work() as session:
        frequency = await session.get(ModelRow, frequency_id)
        assert frequency is not None
        spec = GlmSpec.model_validate(frequency.spec).model_copy(update={
            "model_family_slug": family, "response": ResponseKind.CLAIM_SEVERITY,
            "response_column": "claim_severity", "offset": OffsetSpec(), "family": "gamma",
        })
        row = await add_approved(
            session,
            ModelRow(
                workspace_id=workspace_id, model_family_slug=family, version=1,
                status=ModelStatus.APPROVED.value,
                dataset_version_id=frequency.dataset_version_id,
                spec=spec.model_dump(mode="json"),
                spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}", fit_result=fit,
                diagnostics_id=uuid4(),
            ),
        )
        return row.id


async def _approved_structure(
    database: Any, workspace_id: Any, frequency_id: Any, severity_id: Any
) -> Any:
    """The approved AD Peril Structure the seed leaves (`fremtpl2-ad@1`, large loss uncapped), as
    an `approved` row with its evidence written first; the platform's own composition and
    approval path is held by `test_demo_peril_structure.py`. Returns its ref."""
    from datetime import UTC, datetime
    from decimal import Decimal

    from backend.tests.approved_rows import add_approved
    from backend.tests.test_demo_rating_evidence import demo_model

    from app.db.models import PerilStructureRow
    from model_schema import ArtifactRef, LargeLossKind, LargeLossTreatment, new_uuid7
    from model_schema.perils import PerilComponent, PerilMethod, ReconciledPeril, Reconciliation

    frequency_ref, _ = await demo_model.load_approved_glm(database, workspace_id, frequency_id)
    severity_ref, _ = await demo_model.load_approved_glm(database, workspace_id, severity_id)
    component = PerilComponent(
        peril="AD", method=PerilMethod.FREQUENCY_SEVERITY, frequency_model=frequency_ref,
        severity_model=severity_ref, large_loss=LargeLossTreatment(kind=LargeLossKind.NONE),
    )
    reconciliation = Reconciliation(
        dataset_version_id=new_uuid7(), part="holdout",
        perils=(ReconciledPeril(
            peril="AD", large_loss_kind=LargeLossKind.NONE, modelled_burning_cost=1000
        ),),
        observed_burning_cost=1000, modelled_burning_cost=1000, tolerance=Decimal("0.05"),
        computed_at=datetime.now(UTC),
    )
    async with database.unit_of_work() as session:
        await add_approved(
            session,
            PerilStructureRow(
                workspace_id=workspace_id, slug=demo_model.AD_STRUCTURE_SLUG, version=1,
                status="approved", perils=[component.model_dump(mode="json")],
                excluded_perils=[], reconciliation=reconciliation.model_dump(mode="json"),
            ),
        )
    return ArtifactRef(type="peril_structure", slug=demo_model.AD_STRUCTURE_SLUG, version=1)


async def _world(database: Any, blob_store: Any, workspace_id: Any) -> dict[str, str]:
    """The state `scripts/demo.py` finds after the seed: the principals, an approved GLM and a
    fitted-but-unapproved model, the seeded Rating Version `fremtpl2-demo@1` (the dislocation
    baseline) with its algorithm and suite, and a 40-policy portfolio standing in for the
    seed's 20,000-policy sample. Nothing here is journey code."""
    import io
    from uuid import uuid4

    import polars as pl
    from backend.tests.test_api_rate_tables import _glm_spec
    from backend.tests.test_demo_rating_evidence import (
        _BASE_MINOR,
        _approved_model,
        _bandings,
        _fit_result,
        demo_model,
    )
    from backend.tests.test_fremtpl2_algorithm import _BANDED, _DOMAINS

    from app.config import Settings
    from app.db.models import DatasetVersionRow, DiagnosticsRow, ModelRow
    from model_schema import ModelStatus, new_uuid7

    seed = _seed_module()
    people = await seed.grant_demo_principals(database, workspace_id)
    record = {"workspace_id": str(workspace_id)}
    record |= {f"{name}_id": str(who.id) for name, who in people.items()}

    # ONE definition of the principal set (the maintainer's 23:27:48 condition 2): the seed's own,
    # for the baseline's author, submitter and approvers as well as for the journey. No principal
    # is built here.
    analyst, actuary = people["analyst"], people["actuary"]
    approver, second = people["approver"], people["second_approver"]
    model_id = await _approved_model(database, workspace_id)
    tables = await demo_model.seed_demo_rate_tables(
        database, Settings(), blob_store, workspace_id, analyst, model_id
    )
    severity_id = await _approved_severity(database, workspace_id, model_id)
    structure_ref = await _approved_structure(database, workspace_id, model_id, severity_id)
    await demo_model.create_approved_rating_version(
        database,
        blob_store,
        workspace_id,
        analyst,
        actuary,
        approver,
        second,
        new_uuid7(),
        model_id,
        tables,
        _bandings(),
        _BASE_MINOR,
        severity_id=severity_id,
        structure_ref=structure_ref,
    )

    # The fitted model stands on the validated portfolio Dataset Version: a model on a Dataset
    # Version that does not exist is flagged, and approval refuses it (ARTIFACT_FLAGGED).
    portfolio_id = new_uuid7()
    family = f"fremtpl2-gbm-{uuid4().hex[:6]}"
    record["gbm_family"] = family
    async with database.unit_of_work() as session:
        model = ModelRow(
            workspace_id=workspace_id,
            model_family_slug=family,
            version=1,
            status=ModelStatus.DRAFT.value,
            dataset_version_id=portfolio_id,
            spec=_glm_spec(family, portfolio_id),
            spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}",
        )
        session.add(model)
        await session.flush()
        # A REAL diagnostics row, in `record_fit`'s order (the row, then the pointer and the status
        # in one UPDATE, the only shape `models_fit_immutable` admits). It is an empty payload: the
        # gate checks that evidence exists, and this fixture does not fit a model.
        diagnostics = DiagnosticsRow(workspace_id=workspace_id, model_id=model.id, payload={})
        session.add(diagnostics)
        await session.flush()
        model.fit_result = _fit_result()
        model.diagnostics_id = diagnostics.id
        model.status = ModelStatus.FITTED.value
        # `modelling.reserve`'s creation event, which this direct insert stands in for: its actor
        # is the version's author, and without it approval fails closed as
        # APPROVAL_AUTHOR_UNRESOLVED (the seed's fitted GBM has it from the fit).
        from app.platform import audit
        from model_schema import JobSource

        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=analyst,
            source=JobSource.API,
            action="model.reserved",
            entity_ref=f"model:{family}@1",
        )

    n = 40
    columns: dict[str, list[object]] = {
        "quote_id": [f"Q{i:03d}" for i in range(n)],
        "exposure_years": [1.0] * n,
        "bonus_malus": [50 + (180 * i) // (n - 1) for i in range(n)],
    }
    for banding in _BANDED.values():
        low, high = int(banding.boundaries[0]), int(banding.boundaries[-1]) - 1
        columns[banding.column] = [low + (i * 7) % (high - low + 1) for i in range(n)]
    for factor, levels in _DOMAINS.items():
        columns[factor] = [levels[i % len(levels)] for i in range(n)]
    buffer = io.BytesIO()
    pl.DataFrame(columns).write_parquet(buffer, compression="zstd")
    async with database.unit_of_work() as session:
        blob = await blob_store.put(session, buffer.getvalue(), "application/vnd.apache.parquet")
        version = DatasetVersionRow(
            id=portfolio_id,
            slug="wf699-portfolio",
            workspace_id=workspace_id,
            dataset_id=uuid4(),
            version=1,
            status="validated",
            validation_report_id=new_uuid7(),
            created_by=analyst.id,
            currency="GBP",
            tables=[{"name": "portfolio", "row_count": n, "blob": {"sha256": blob.sha256}}],
        )
        session.add(version)
        await session.flush()
        record["portfolio_dataset_version_id"] = str(version.id)
        record["portfolio_rows"] = str(n)
    return record


@pytest.mark.req("FR-229")
@pytest.mark.req("FR-230")
@pytest.mark.req("FR-237")
@pytest.mark.req("FR-240")
@pytest.mark.req("FR-257")
@pytest.mark.req("FR-260")
@pytest.mark.req("FR-261")
@pytest.mark.req("FR-263")
@pytest.mark.req("FR-355")
@pytest.mark.req("FR-429")
def test_wf699_journey_runs_end_to_end(api_client, database, blob_store, workspace_id) -> None:  # type: ignore[no-untyped-def]
    """PL-1544 Acceptance 2, 3 and 4 and the delta's Acceptance 2: every step of `WF-699` A to E
    and the deploy step over HTTP, each deliberate failure asserted by its code, the D4 property
    failing between two adjacent grid values and then passing, and the version deployed
    `dev -> uat -> prod` and scored from `prod`'s live deployment.

    **This covers the post-approval plumbing only.** The stand-in for the unapproved GBM is a
    GLM-typed Model with a real (empty) diagnostics row: it satisfies `02` R3 by its type, so the
    transparency build is never run here. The GBM transparency/submit gate for a real xgboost
    model is covered by the Acceptance 5 rehearsal (`scripts/demo.py --journey wf-699`, full
    seed) and not by CI. `test_a_non_glm_stand_in_without_a_transparency_artifact_is_refused` is
    the guard on the gate itself."""
    import asyncio
    from uuid import UUID

    from app.worker.dislocation_handlers import register_dislocation_handlers
    from app.worker.rate_table_handlers import register_rate_table_handlers
    from app.worker.rating_handlers import register_rating_handlers
    from app.worker.tasks import execute_job

    loop = asyncio.get_event_loop()
    record = loop.run_until_complete(_world(database, blob_store, workspace_id))
    register_rating_handlers()
    register_dislocation_handlers()
    register_rate_table_handlers()
    api_client.base_url = "http://testserver/api/v1"
    lines: list[str] = []

    def run_job(job_id: str) -> None:
        loop.run_until_complete(execute_job(database, UUID(job_id), blob_store))

    try:
        result = journey.run_wf699_journey(api_client, record, log=lines.append, run_job=run_job)
    except journey.JourneyStepFailed as failure:
        # The exception's text is the step and code only; the server's detail is on the attribute.
        pytest.fail(f"{failure} :: {failure.detail} :: after {lines[-1:]}")

    status = result.step_status
    # PL-1544 Acceptance 2: EVERY WF-699 step is recorded, once, in the documented order. A step
    # missing from the record, or recorded out of that order, fails here.
    assert list(status) == list(journey.STEP_ORDER)
    skipped = {entry.step: f"SKIPPED: {entry.line}" for entry in journey.SKIPS}
    for step, outcome in status.items():
        # Each step is either asserted by the journey (`ok`) or a ruled skip, whose exact line is
        # the recorded status. Nothing else is a status.
        assert outcome == skipped.get(step, "ok"), (step, outcome)
    assert set(skipped) <= set(status)
    # The deliberate failures were asserted by their codes inside the journey; their statuses are
    # `ok` only because the platform answered exactly that code.
    for step in ("B4", "C1′", "B6", "C4", "E3", "D4", "E8"):  # noqa: RUF001
        assert status[step] == "ok", step
    assert result.rating_version_id is not None
    assert result.bundle_hash.startswith("sha256:")
    assert result.prod_premium_minor > 0
    assert any("20,000-policy sample" in line for line in lines)

    # PL-1694 Acceptance 18 (PL 8055 Task A): the split test's list IS this run's derived list.
    # The world's random model family is the ONE token substituted, by its exact value from
    # `record` (RL 8060; the maintainer's 2026-10-16 09:54:43 BST condition 2): no pattern.
    run = result.d7_run
    real = [
        {key: str(change[key]) for key in ("id", "kind", "description")}
        for change in run["derived_changes"]
    ]
    expected = [
        {**row, "description": row["description"].replace("{gbm_family}", record["gbm_family"])}
        for row in D7_DERIVED_CHANGES
    ]
    print(f"D7 gbm_family: {record['gbm_family']}")  # RL 8060 precision 2: the LG records it
    assert real == expected, json.dumps(real, ensure_ascii=False, indent=1)
    # The four checks of Acceptance 18, on the real run as stored.
    effects = journey.split_effects(real)
    assert effects is not None
    assert {group["name"]: group["changes"] for group in run["change_groups"]} == effects
    placed = [cid for ids in effects.values() for cid in ids]
    assert sorted(placed) == sorted(row["id"] for row in real)
    assert len(set(placed)) == len(placed)
    summary = run["attribution_summary"]
    total = int(summary["total_change_minor"])
    assert summary["method"] == "shapley"
    assert sum(int(item["shapley_minor"]) for item in run["attribution"]) == total
    isolated = sum(int(item["isolated_minor"]) for item in run["attribution"])
    assert isolated + int(summary["residual_minor"]) == total


@pytest.mark.req("FR-221")
def test_b3_the_fork_puts_a_pinned_as_at_lookup_in_the_premium() -> None:
    """The maintainer's B3 ruling (to-lead "2026-10-11 23:46:22 BST"): the algorithm carries a
    lookup step on the reference table, as at `effective_date`, whose result the premium consumes,
    and a miss is an error (a quote dated before the row's `effective_from` is refused, not priced
    without the loading). Without a reference table the fork has no lookup (the B6/B9 probes)."""
    seeded = {
        "slug": "fremtpl2-rate",
        "input_contract": [],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "sub_graphs": [],
        "steps": [
            {
                "step_id": "s_t_region",
                "type": "table",
                "rate_table_ref": "rate_table:x@1",
                "key_expr": ["region"],
                "consumes": ["region"],
                "produces": "rel_region",
            },
            {
                "step_id": "s_premium",
                "type": "expression",
                "expr": "base_premium_minor * rel_region",
                "result_type": "decimal",
                "consumes": ["base_premium_minor", "rel_region"],
                "produces": "premium_unrounded",
            },
            {
                "step_id": "s_out",
                "type": "output",
                "output_name": "payable_premium_minor",
                "rounding": {"mode": "half_even", "dp": 0},
                "consumes": ["premium_unrounded"],
            },
        ],
    }
    walk = journey._Journey(None, {}, print, None, 1.0)  # type: ignore[arg-type]
    walk.seeded = seeded
    walk.table_refs = {"region": "rate_table:wf699-region@2"}
    plain = walk.fork(version=2, ladder_ref="sub_graph:ncd-ladder@1")
    assert [s["step_id"] for s in plain["steps"]] == ["s_t_region", "s_premium", "s_out"]
    assert plain["steps"][0]["rate_table_ref"] == "rate_table:wf699-region@2"

    walk.loading_ref = "reference_table:wf699-region-loading@1"
    forked = walk.fork(version=2, ladder_ref="sub_graph:ncd-ladder@1")
    ids = [s["step_id"] for s in forked["steps"]]
    assert ids == ["s_t_region", "s_loading", "s_premium", "s_out"]
    by_id = {s["step_id"]: s for s in forked["steps"]}
    lookup = by_id["s_loading"]
    assert lookup["type"] == "lookup"
    assert lookup["reference_table_ref"] == "reference_table:wf699-region-loading@1"
    assert lookup["as_at"] == "effective_date"
    assert lookup["on_miss"] == "error"
    # The premium step multiplies by the loading: it is the one step that consumes the rate-table
    # outputs, the ladder's factor and the lookup's output (so a lookup miss is reported as
    # RATE_TABLE_MISS today; the journey asserts that exactly and names the finding).
    premium = by_id["s_premium"]
    assert "number(expense_loading)" in premium["expr"]
    assert "expense_loading" in premium["consumes"]
    assert "ncd_factor" in premium["consumes"]
    assert by_id["s_out"]["consumes"] == ["premium_unrounded"]
    assert seeded["steps"][1]["expr"] == "base_premium_minor * rel_region"  # the seed is untouched


def test_discover_picks_the_frequency_glm_by_its_declared_response_not_by_order() -> None:
    """SL-1543 (maintainer, 2026-10-17 21:09:30 BST): `/models` is newest first, and the B4 world
    approves a severity GLM AFTER the frequency GLM. `discover()` must still return the
    frequency GLM: the one whose spec declares the claim-count response. Fed a stub list, no DB."""

    def model(family: str, response_column: str, response: str | None) -> dict[str, Any]:
        return {
            "model_family_slug": family, "version": 1,
            "spec": {"response": response, "response_column": response_column},
            "fit_result": {"model_type": "glm", "relativities": {"area": []}},
        }

    severity = model("fremtpl2-sev-aaaaaa", "claim_severity", "claim_severity")
    frequency = model("fremtpl2-glm-bbbbbb", "claim_count", None)
    gbm = {
        "model_family_slug": "fremtpl2-gbm-cccccc", "version": 1,
        "fit_result": {"model_type": "xgboost"},
    }

    def stub(step: str, who: str, method: str, path: str, **kw: Any) -> dict[str, Any]:
        status = kw["params"]["status"]
        return {"items": [severity, frequency] if status == "approved" else [gbm]}

    walk = object.__new__(journey._Journey)
    walk.req = stub  # type: ignore[method-assign]
    walk.discover()
    assert walk.glm_ref == "model:fremtpl2-glm-bbbbbb@1"


@pytest.mark.req("FR-264")
def test_d7_is_not_a_skip_and_a_skip_without_an_owner_still_fails() -> None:
    """D7 decomposes now (FD-1660, SL-1696): the skip table no longer carries it, so
    `test_wf699_journey_runs_end_to_end` records it `ok` only because its two-group run
    reconciled; and the owner check still refuses a skip that names no finding or Work."""
    assert not [e for e in journey.SKIPS if e.step == "D7"]
    with pytest.raises(journey.JourneyStepFailed):
        journey.check_skip_owners([journey.Skip(step="D7", line="SKIPPED D7 decomposition")])


#: The `derived_changes` of the journey's decomposing D7 run in `_world`, as `id`, `kind` and
#: `description` (`PL-1694` Acceptance 18; PL 8055). `{gbm_family}` stands for `_world`'s
#: random model family; `test_wf699_journey_runs_end_to_end` asserts this list IS the run's.
D7_DERIVED_CHANGES: Final[list[dict[str, str]]] = [
    {
        "id": "c1",
        "kind": "step_added",
        "description": (
            "m_ncd: mount added (sub_graph:ncd-ladder@3)"
        ),
    },
    {
        "id": "c2",
        "kind": "step_added",
        "description": (
            "s_loading: step added"
        ),
    },
    {
        "id": "c3",
        "kind": "table_repointed",
        "description": (
            "s_o_area: rate_table_ref rate_table:fremtpl2-area@1 → rate_table:wf699-area@1"
        ),
    },
    {
        "id": "c4",
        "kind": "table_repointed",
        "description": (
            "s_o_driv_age_band: rate_table_ref rate_table:fremtpl2-driv-age-band@1 → rate_table:wf699-driv-age-band@1"  # noqa: E501
        ),
    },
    {
        "id": "c5",
        "kind": "table_repointed",
        "description": (
            "s_o_region: rate_table_ref rate_table:fremtpl2-region@1 → rate_table:wf699-region@1"
        ),
    },
    {
        "id": "c6",
        "kind": "table_repointed",
        "description": (
            "s_o_veh_age_band: rate_table_ref rate_table:fremtpl2-veh-age-band@1 → rate_table:wf699-veh-age-band@1"  # noqa: E501
        ),
    },
    {
        "id": "c7",
        "kind": "table_repointed",
        "description": (
            "s_o_veh_brand: rate_table_ref rate_table:fremtpl2-veh-brand@1 → rate_table:wf699-veh-brand@1"  # noqa: E501
        ),
    },
    {
        "id": "c8",
        "kind": "table_repointed",
        "description": (
            "s_o_veh_gas: rate_table_ref rate_table:fremtpl2-veh-gas@1 → rate_table:wf699-veh-gas@1"
        ),
    },
    {
        "id": "c9",
        "kind": "table_repointed",
        "description": (
            "s_o_veh_power_band: rate_table_ref rate_table:fremtpl2-veh-power-band@1 → rate_table:wf699-veh-power-band@1"  # noqa: E501
        ),
    },
    {
        "id": "c10",
        "kind": "step_changed",
        "description": (
            "s_premium: consumes [\"model_premium\", \"rel_driv_age_band\", \"rel_veh_age_band\", \"rel_veh_power_band\", \"rel_veh_brand\", \"rel_veh_gas\", \"rel_area\", \"rel_region\", \"origin_driv_age_band\", \"origin_veh_age_band\", \"origin_veh_power_band\", \"origin_veh_brand\", \"origin_veh_gas\", \"origin_area\", \"origin_region\"] → [\"model_premium\", \"rel_driv_age_band\", \"rel_veh_age_band\", \"rel_veh_power_band\", \"rel_veh_brand\", \"rel_veh_gas\", \"rel_area\", \"rel_region\", \"origin_driv_age_band\", \"origin_veh_age_band\", \"origin_veh_power_band\", \"origin_veh_brand\", \"origin_veh_gas\", \"origin_area\", \"origin_region\", \"ncd_factor\", \"expense_loading\"]; expr ((origin_driv_age_band != 0 and origin_veh_age_band != 0 and origin_veh_power_band != 0 and origin_veh_brand != 0 and origin_veh_gas != 0 and origin_area != 0 and origin_region != 0) ? model_premium * (rel_driv_age_band / origin_driv_age_band) * (rel_veh_age_band / origin_veh_age_band) * (rel_veh_power_band / origin_veh_power_band) * (rel_veh_brand / origin_veh_brand) * (rel_veh_gas / origin_veh_gas) * (rel_area / origin_area) * (rel_region / origin_region) : 0) → ((origin_driv_age_band != 0 and origin_veh_age_band != 0 and origin_veh_power_band != 0 and origin_veh_brand != 0 and origin_veh_gas != 0 and origin_area != 0 and origin_region != 0) ? model_premium * (rel_driv_age_band / origin_driv_age_band) * (rel_veh_age_band / origin_veh_age_band) * (rel_veh_power_band / origin_veh_power_band) * (rel_veh_brand / origin_veh_brand) * (rel_veh_gas / origin_veh_gas) * (rel_area / origin_area) * (rel_region / origin_region) : 0) * ncd_factor * number(expense_loading)"  # noqa: E501
        ),
    },
    {
        "id": "c11",
        "kind": "table_repointed",
        "description": (
            "s_t_area: rate_table_ref rate_table:fremtpl2-area@1 → rate_table:wf699-area@2"
        ),
    },
    {
        "id": "c12",
        "kind": "table_repointed",
        "description": (
            "s_t_driv_age_band: rate_table_ref rate_table:fremtpl2-driv-age-band@1 → rate_table:wf699-driv-age-band@1"  # noqa: E501
        ),
    },
    {
        "id": "c13",
        "kind": "table_repointed",
        "description": (
            "s_t_region: rate_table_ref rate_table:fremtpl2-region@1 → rate_table:wf699-region@2"
        ),
    },
    {
        "id": "c14",
        "kind": "table_repointed",
        "description": (
            "s_t_veh_age_band: rate_table_ref rate_table:fremtpl2-veh-age-band@1 → rate_table:wf699-veh-age-band@1"  # noqa: E501
        ),
    },
    {
        "id": "c15",
        "kind": "table_repointed",
        "description": (
            "s_t_veh_brand: rate_table_ref rate_table:fremtpl2-veh-brand@1 → rate_table:wf699-veh-brand@1"  # noqa: E501
        ),
    },
    {
        "id": "c16",
        "kind": "table_repointed",
        "description": (
            "s_t_veh_gas: rate_table_ref rate_table:fremtpl2-veh-gas@1 → rate_table:wf699-veh-gas@1"
        ),
    },
    {
        "id": "c17",
        "kind": "table_repointed",
        "description": (
            "s_t_veh_power_band: rate_table_ref rate_table:fremtpl2-veh-power-band@1 → rate_table:wf699-veh-power-band@1"  # noqa: E501
        ),
    },
    {
        "id": "c18",
        "kind": "pin",
        "description": (
            "models pin model:{gbm_family}@1 added"
        ),
    },
]


@pytest.mark.req("FR-264")
def test_d7_splits_the_derived_changes_into_the_journeys_own_effects() -> None:
    """The maintainer's D7 ruling (to-lead "2026-10-12 01:25:10 BST"): attribution decomposes the
    change. The derived changes of a run (`id`, `kind`, `description`) become two groups: what the
    journey did to the rate tables, and the structure it added, the ladder's mount (DP-1:
    `step_added`, `<mount_point>: mount added (<ref>)`) among it; a pin on a rate table belongs
    with the first. If either effect is empty there is nothing to decompose and the journey
    stops."""
    derived = D7_DERIVED_CHANGES
    effects = journey.split_effects(derived)
    assert effects == {
        journey.EFFECT_RATE_TABLES: [f"c{n}" for n in (*range(3, 10), *range(11, 18))],
        journey.EFFECT_STRUCTURE: ["c1", "c2", "c10", "c18"],
    }
    flat = [cid for ids in effects.values() for cid in ids]
    assert sorted(flat) == sorted(d["id"] for d in derived)  # a partition: none lost, none twice
    ids = {row["id"]: row for row in derived}
    tables = [ids[cid] for cid in effects[journey.EFFECT_RATE_TABLES]]
    structure = [ids[cid] for cid in effects[journey.EFFECT_STRUCTURE]]
    assert journey.split_effects(tables) is None  # tables only: nothing else to decompose
    assert journey.split_effects(structure) is None  # structure only
    (mount,) = [row for row in derived if row["description"].startswith("m_ncd: mount")]
    assert mount["id"] in effects[journey.EFFECT_STRUCTURE]
    assert mount["kind"] != "table_repointed"
    assert journey.split_effects([]) is None


@pytest.mark.req("FR-257")
def test_the_step_order_names_every_wf699_step_once() -> None:
    """PL-1544 Acceptance 2: the journey's recorded order has every step of `WF-699` A to E once,
    plus the two steps this slice adds (`DEP`, `S1`) and `C1'`. The only departures from the
    workflow's own order are the declared ones."""
    import re

    workflow = (_EXAMPLE.parents[1] / "docs" / "workflows").glob("WF-00699-*.md")
    text = next(workflow).read_text(encoding="utf-8")
    ids = re.findall(r"^\| ([A-E]\d) \|", text, flags=re.MULTILINE)
    assert len(ids) == len(set(ids))
    expected = set(ids) | {"C1′", "DEP", "S1"}  # noqa: RUF001
    assert set(journey.STEP_ORDER) == expected
    assert len(journey.STEP_ORDER) == len(set(journey.STEP_ORDER))
    positions = {step: i for i, step in enumerate(journey.STEP_ORDER)}
    # D6 to D9 run between E3 and E4; B3 and B7 come before B1; all else follows the workflow.
    assert positions["E3"] < positions["D6"] < positions["D9"] < positions["E4"]
    assert positions["B3"] < positions["B7"] < positions["B1"]
    assert positions["C5"] < positions["C3"] < positions["C6"]  # C3 follows the compile that passes
    for phase in "ADE":
        in_phase = [s for s in journey.STEP_ORDER if s[0] == phase]
        if phase == "D":
            in_phase = [s for s in in_phase if s in {"D1", "D2", "D3", "D4", "D5"}]
        assert in_phase == sorted(in_phase), phase


@pytest.mark.req("FR-211")
async def test_a_non_glm_stand_in_without_a_transparency_artifact_is_refused(
    database, workspace_id  # type: ignore[no-untyped-def]
) -> None:
    """A GUARD, not a red-first: it passes on `main` too. It pins the refusal the journey's C5 step
    now satisfies by building the artifact. A non-GLM Model with diagnostics but no transparency
    artifact is refused `422 EVIDENCE_INCOMPLETE` at submission (`modelling._require_evidence`),
    so the journey's old C5 (submit with no build) could not have passed for a real GBM."""
    from uuid import uuid4

    from backend.tests.test_api_rate_tables import _glm_spec

    from app.db.models import DiagnosticsRow, ModelRow
    from app.errors import PlatformError
    from app.platform import modelling as model_service
    from model_schema import ModelStatus, new_uuid7

    people = await _seed_module().grant_demo_principals(database, workspace_id)
    family = f"fremtpl2-gbm-{uuid4().hex[:6]}"
    portfolio_id = new_uuid7()
    async with database.unit_of_work() as session:
        model = ModelRow(
            workspace_id=workspace_id,
            model_family_slug=family,
            version=1,
            status=ModelStatus.DRAFT.value,
            dataset_version_id=portfolio_id,
            spec={**_glm_spec(family, portfolio_id), "model_type": "xgboost"},
            spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}",
        )
        session.add(model)
        await session.flush()
        diagnostics = DiagnosticsRow(workspace_id=workspace_id, model_id=model.id, payload={})
        session.add(diagnostics)
        await session.flush()
        model.fit_result = {}
        model.diagnostics_id = diagnostics.id
        model.status = ModelStatus.FITTED.value
        model_id = model.id

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await model_service.submit_for_review(
                session,
                workspace_id=workspace_id,
                actor=people["actuary"],
                model_id=model_id,
                change_summary="a non-GLM model submitted with no transparency artifact",
            )
    assert refused.value.code == "EVIDENCE_INCOMPLETE"
    assert "transparency artifact names it" in (refused.value.detail or "")


@pytest.mark.req("FR-222")
def test_b4_and_c1_are_walked_not_skipped() -> None:
    """PL-1542 Acceptance 6: the journey no longer declares B4 or C1' as skips, and no skip
    line names SL-1543 as its owner. Red first, by cause: on the base tree `journey.SKIPS`
    still carries `SKIPPED B4 model_call: FD-1456; SL-1543` and `SKIPPED C1': ...`."""
    assert not [e for e in journey.SKIPS if e.step in {"B4", "C1′"}]  # noqa: RUF001
    assert not [e for e in journey.SKIPS if "SL-1543" in e.line]
