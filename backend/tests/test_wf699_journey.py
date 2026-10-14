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
from typing import Any

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
        "SKIPPED B4 model_call: FD-1456; SL-1543",
        "SKIPPED C1′: FD-1456; SL-1543",  # noqa: RUF001
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
    )

    # The fitted model stands on the validated portfolio Dataset Version: a model on a Dataset
    # Version that does not exist is flagged, and approval refuses it (ARTIFACT_FLAGGED).
    portfolio_id = new_uuid7()
    family = f"fremtpl2-gbm-{uuid4().hex[:6]}"
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
    for step in ("B6", "C4", "E3", "D4", "E8"):
        assert status[step] == "ok", step
    assert result.rating_version_id is not None
    assert result.bundle_hash.startswith("sha256:")
    assert result.prod_premium_minor > 0
    assert any("20,000-policy sample" in line for line in lines)


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


@pytest.mark.req("FR-264")
def test_d7_is_not_a_skip_and_a_skip_without_an_owner_still_fails() -> None:
    """D7 decomposes now (FD-1660, SL-1696): the skip table no longer carries it, so
    `test_wf699_journey_runs_end_to_end` records it `ok` only because its two-group run
    reconciled; and the owner check still refuses a skip that names no finding or Work."""
    assert not [e for e in journey.SKIPS if e.step == "D7"]
    with pytest.raises(journey.JourneyStepFailed):
        journey.check_skip_owners([journey.Skip(step="D7", line="SKIPPED D7 decomposition")])


@pytest.mark.req("FR-264")
def test_d7_splits_the_derived_changes_into_the_journeys_own_effects() -> None:
    """The maintainer's D7 ruling (to-lead "2026-10-12 01:25:10 BST"): attribution decomposes the
    change. The derived changes of a run (`id`, `kind`, `description`) become two groups: what the
    journey did to the rate tables, and the structure it added, the ladder's mount among it (DP-1:
    `step_added`, `<mount_point>: mount added (<ref>)`). The list below is the real
    `derived_changes` of the journey's D7 run at the SL-1696 gate (demo run `01a13bca-2560-…`,
    2026-10-14); the mount is `c1` and no `sub_graphs` pin appears, the mount change accounting for
    it. If either effect is empty there is nothing to decompose and the journey stops."""
    columns = [
        "base_premium_minor",
        "rel_driv_age_band",
        "rel_veh_age_band",
        "rel_veh_power_band",
        "rel_veh_brand",
        "rel_veh_gas",
        "rel_area",
        "rel_region",
    ]
    after = [*columns, "ncd_factor", "expense_loading"]
    product = " * ".join(columns)
    premium = (
        f"s_premium: consumes {json.dumps(columns)} → {json.dumps(after)}; "
        f"expr {product} → {product} * ncd_factor * number(expense_loading)"
    )
    repoints = [
        ("c4", "s_t_area", "area@1", "wf699-area@2"),
        ("c5", "s_t_driv_age_band", "driv-age-band@1", "wf699-driv-age-band@1"),
        ("c6", "s_t_region", "region@1", "wf699-region@2"),
        ("c7", "s_t_veh_age_band", "veh-age-band@1", "wf699-veh-age-band@1"),
        ("c8", "s_t_veh_brand", "veh-brand@1", "wf699-veh-brand@1"),
        ("c9", "s_t_veh_gas", "veh-gas@1", "wf699-veh-gas@1"),
        ("c10", "s_t_veh_power_band", "veh-power-band@1", "wf699-veh-power-band@1"),
    ]
    derived = [
        {
            "id": "c1",
            "kind": "step_added",
            "description": "m_ncd: mount added (sub_graph:ncd-ladder@3)",
        },
        {"id": "c2", "kind": "step_added", "description": "s_loading: step added"},
        {"id": "c3", "kind": "step_changed", "description": premium},
        *(
            {
                "id": cid,
                "kind": "table_repointed",
                "description": (
                    f"{step}: rate_table_ref rate_table:fremtpl2-{old} → rate_table:{new}"
                ),
            }
            for cid, step, old, new in repoints
        ),
        {
            "id": "c11",
            "kind": "pin",
            "description": "models pin model:fremtpl2-gbm-130a2e@1 added",
        },
    ]
    effects = journey.split_effects(derived)
    assert effects == {
        journey.EFFECT_RATE_TABLES: [f"c{n}" for n in range(4, 11)],
        journey.EFFECT_STRUCTURE: ["c1", "c2", "c3", "c11"],
    }
    flat = [cid for ids in effects.values() for cid in ids]
    assert sorted(flat) == sorted(d["id"] for d in derived)  # a partition: none lost, none twice
    assert journey.split_effects(derived[3:10]) is None  # tables only: nothing else to decompose
    assert journey.split_effects([derived[0], derived[1], derived[2], derived[10]]) is None
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
