"""`score_one` (WK-671 Task 1.4, FR-250/254/255/256/258/273/218/252, NFR-491/495/496/501).

Fixture shape: `input(driver_age, channel) -> table(expense_factor) -> model_call(risk_
premium_minor) -> expression(office_premium_minor) -> constraint(clamp on min_premium) ->
constraint(decline x2, sanity cap/floor) -> expression(instalment_loading_minor) ->
output(payable_premium_minor)`. Every ladder rung this fixture exposes is opted in via its
own `output` step (`score.py`'s own design note: an `output`-type step is never a wire
node, so a rung's raw value lives under whatever name its output step `consumes`, never
under the rung's own name) — `risk_premium`, `office_premium`, `instalment_loading`,
`payable_premium`; `constraints` is always synthesised.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import socket
import subprocess
import sys
from datetime import date, datetime
from typing import Any
from uuid import uuid4

import pytest

# Reuse Task 1.3's own fixtures rather than duplicating them — an established convention
# in this test suite (e.g. `test_transparency.py` imports from `test_gbm`/`test_ebm`).
from test_rating_runtime import (
    _gbm_model_payload,
    _glm_model_payload,
    _rate_table_payload,
    _train_tiny_booster,
)

from model_schema.rating import RatingVersion, SubGraphRef
from model_schema.refs import ArtifactRef
from model_schema.scoring import QuoteContext, QuoteContextOptions
from pricing_core.rating.compile import ArtifactResolver, ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_one

_RATING_VERSION_REF = ArtifactRef(type="rating_version", slug="score-fixture", version=1)


def _algorithm_payload(*, model_ref: str = "model:motor-freq@1") -> dict[str, Any]:
    return {
        "slug": "score-fixture",
        "version": 1,
        "input_contract": [
            {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99},
            {"name": "channel", "type": "enum", "domain": ["direct", "broker"], "nullable": False},
            {"name": "min_premium_minor", "type": "int", "nullable": False},
            {"name": "sanity_cap_minor", "type": "int", "nullable": False},
            {"name": "sanity_floor_minor", "type": "int", "nullable": False},
        ],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in_age", "type": "input", "label": "Driver age",
             "input_name": "driver_age", "on_missing": "error", "produces": "driver_age"},
            {"step_id": "s_in_channel", "type": "input", "label": "Channel",
             "input_name": "channel", "on_missing": "error", "produces": "channel"},
            {"step_id": "s_expense", "type": "table", "label": "Expense factor",
             "rate_table_ref": "rate_table:motor-expense@1", "key_expr": ["channel"],
             "on_miss": "error", "consumes": ["channel"], "produces": "expense_factor"},
            {"step_id": "s_risk", "type": "model_call", "label": "Risk premium",
             "model_ref": model_ref, "mode": "exact", "feature_map": {"driver_age": "age_years"},
             "consumes": ["driver_age"], "produces": ["risk_premium_minor"]},
            {"step_id": "s_out_risk", "type": "output", "label": "Risk premium (ladder)",
             "output_name": "risk_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["risk_premium_minor"]},
            {"step_id": "s_office", "type": "expression", "label": "Office premium",
             "expr": "risk_premium_minor * expense_factor", "result_type": "money_minor",
             "consumes": ["risk_premium_minor", "expense_factor"],
             "produces": "office_premium_minor"},
            {"step_id": "s_clamp", "type": "constraint", "label": "Minimum premium",
             "condition": "office_premium_minor >= min_premium_minor", "on_violation": "clamp",
             "clamp_bounds": {"min": "min_premium_minor"}, "reason_code": "MIN_PREMIUM_APPLIED",
             "consumes": ["office_premium_minor"], "produces": ["office_premium_minor"]},
            {"step_id": "s_decl_cap", "type": "constraint", "label": "Sanity cap",
             "condition": "office_premium_minor <= sanity_cap_minor", "on_violation": "decline",
             "reason_code": "SANITY_CAP", "consumes": ["office_premium_minor"]},
            {"step_id": "s_decl_floor", "type": "constraint", "label": "Sanity floor",
             "condition": "office_premium_minor >= sanity_floor_minor", "on_violation": "decline",
             "reason_code": "SANITY_FLOOR", "consumes": ["office_premium_minor"]},
            {"step_id": "s_out_office", "type": "output", "label": "Office premium (ladder)",
             "output_name": "office_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["office_premium_minor"]},
            {"step_id": "s_instalment", "type": "expression", "label": "Instalment loading",
             "expr": "office_premium_minor * 1.05", "result_type": "money_minor",
             "consumes": ["office_premium_minor"], "produces": "instalment_loading_minor"},
            {"step_id": "s_out_instalment", "type": "output",
             "label": "Instalment loading (ladder)", "output_name": "instalment_loading_minor",
             "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["instalment_loading_minor"]},
            {"step_id": "s_out_payable", "type": "output", "label": "Payable premium",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["instalment_loading_minor"]},
        ],
        "sub_graphs": [],
    }


class _FakeResolver:
    def __init__(self, *, glm: bool = False) -> None:
        booster = _train_tiny_booster()
        model_ref = "model:motor-freq-glm@1" if glm else "model:motor-freq@1"
        self._payloads: dict[str, dict[str, Any]] = {
            "rating_algorithm:score-fixture@1": _algorithm_payload(model_ref=model_ref),
            "rate_table:motor-expense@1": _rate_table_payload(),
            "model:motor-freq@1": _gbm_model_payload(booster),
            "model:motor-freq-glm@1": _glm_model_payload(),
        }

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        return ResolvedArtifact(status="approved", payload=self._payloads[str(ref)])


def _version(*, glm: bool = False) -> RatingVersion:
    return RatingVersion.model_validate(
        {
            "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": "score-fixture", "version": 1,
            "status": "draft", "dataset_version_id": str(uuid4()),
            "model_ref": "model:motor-freq-glm@1" if glm else "model:motor-freq@1",
            "created_at": "2026-08-29T12:00:00Z", "created_by": str(uuid4()),
            "updated_at": "2026-08-29T12:00:00Z",
            "algorithm_ref": "rating_algorithm:score-fixture@1",
            "pins": {
                "rate_tables": ["rate_table:motor-expense@1"],
                "models": ["model:motor-freq-glm@1"] if glm else ["model:motor-freq@1"],
                "reference_tables": [], "custom_objectives": [],
            },
            "model_reference_mode": "exact",
        }
    )


async def _compiled(*, glm: bool = False) -> CompiledBundle:
    resolver: ArtifactResolver = _FakeResolver(glm=glm)
    bundle = await compile_bundle(_version(glm=glm), resolver)
    return load_bundle(bundle)


def _ctx(**overrides: Any) -> QuoteContext:
    defaults: dict[str, Any] = {
        "purpose": "new_business",
        "quoted_at": datetime(2026, 8, 29, 12, 0, 0),
        "effective_date": date(2026, 9, 1),
        "inputs": {
            "driver_age": 34, "channel": "direct", "min_premium_minor": 0,
            "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
        },
        "options": QuoteContextOptions(rating_version_ref=_RATING_VERSION_REF),
    }
    defaults.update(overrides)
    return QuoteContext.model_validate(defaults)


# ---------------------------------------------------------------------------
# FR-250: the golden test.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-250")
async def test_a_known_quote_prices_to_a_known_premium() -> None:
    """A known `Bundle` (Task 1.3's own tiny fixed booster, age 34 -> 1304.8) + a known
    `QuoteContext` gives an exact, pre-computed `ScoringResult`. The golden numbers below
    were captured from one deterministic run of this exact fixture, not invented — fixed
    training data, fixed hyperparameters, no randomness anywhere in the path."""
    compiled = await _compiled()
    result = await score_one(compiled, _ctx())

    assert result.outcome == "quoted"
    assert result.outputs["payable_premium_minor"] == 1_507
    assert [r.rung for r in result.premium_ladder] == [
        "risk_premium", "office_premium", "constraints", "instalment_loading", "payable_premium",
    ]
    assert result.premium_ladder[0].value_minor == 1_305  # round(1304.8)
    assert result.premium_ladder[-1].rung == "payable_premium"
    assert result.premium_ladder[-1].value_minor == result.outputs["payable_premium_minor"]
    assert result.decline_reasons == []
    assert result.rating_version_ref == _RATING_VERSION_REF
    assert result.bundle_hash == compiled.content_hash


# ---------------------------------------------------------------------------
# NFR-496: the ladder reconciles — both the library check and a manual re-derivation.
# ---------------------------------------------------------------------------


@pytest.mark.req("NFR-496")
async def test_the_ladder_reconciles_over_a_battery_of_generated_contexts() -> None:
    """Not one example: driver age and channel vary, and a from-scratch re-derivation
    (`RL-1329` R4: apply every recorded operation, with no rounding, to the first rung's
    unrounded value, then round once at `payable_premium`) must reproduce the payable
    exactly. Replaces the old re-derivation, whose `round` branch *assigned*
    `rung.value_minor` instead of replaying, and so passed over the 4 dp drift (FD-1336 F4;
    its NFR-496 round weakness)."""
    from decimal import Decimal, localcontext

    from pricing_core.money import ROUNDING_MODES

    compiled = await _compiled()
    for age in (18, 25, 34, 50, 70, 99):
        for channel in ("direct", "broker"):
            ctx = _ctx(inputs={
                "driver_age": age, "channel": channel, "min_premium_minor": 0,
                "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
            })
            result = await score_one(compiled, ctx)
            assert result.trace is None  # untraced by default; reconciliation still holds
            ladder = result.premium_ladder
            assert ladder, f"age={age} channel={channel}: empty ladder"

            assert ladder[0].unrounded_minor is not None
            value = ladder[0].unrounded_minor
            with localcontext() as ctx100:
                ctx100.prec = 100
                for rung in ladder[1:]:
                    op = rung.operation
                    assert op is not None, f"{rung.rung}: no recorded operation"
                    if op.kind == "multiply":
                        assert op.factor is not None
                        value = value * op.factor
                    elif op.kind == "divide":
                        assert op.divisor is not None
                        value = value / op.divisor
                    elif op.kind == "add":
                        assert op.amount_unrounded_minor is not None
                        value = value + op.amount_unrounded_minor
                    elif op.kind == "round":
                        # the replay ROUNDS here, once; it never assigns the recorded value
                        assert op.mode is not None
                        replayed = int(
                            value.quantize(Decimal(1), rounding=ROUNDING_MODES[op.mode])
                        )
                        assert replayed == rung.value_minor, (
                            f"age={age} channel={channel}: replay rounds to {replayed}, "
                            f"recorded {rung.value_minor}"
                        )
                        assert replayed == result.outputs["payable_premium_minor"]
                        continue
                    assert rung.unrounded_minor is not None
                    assert abs(value - rung.unrounded_minor) <= Decimal("1e-26") * abs(
                        rung.unrounded_minor
                    ), f"age={age} channel={channel} rung={rung.rung}: operation does not replay"
            assert ladder[-1].operation is not None
            assert ladder[-1].operation.kind == "round"


# ---------------------------------------------------------------------------
# RL-875: the decline representation — collect-all, ladder stays populated.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-256")
async def test_two_firing_constraints_both_appear_in_decline_reasons() -> None:
    """The acceptance test stated as the violation (RL-875): a single-decline test
    passes under short-circuit and collect-all alike and proves nothing — this fires
    *two* independent constraint steps and requires both codes and a still-reconciling,
    fully-populated ladder."""
    compiled = await _compiled()
    ctx = _ctx(inputs={
        "driver_age": 34, "channel": "direct", "min_premium_minor": 0,
        "sanity_cap_minor": 100, "sanity_floor_minor": 999_999_999,
    })
    result = await score_one(compiled, ctx)

    assert result.outcome == "declined"
    assert sorted(result.decline_reasons) == ["SANITY_CAP", "SANITY_FLOOR"]
    assert len(result.decline_reasons) == 2
    assert [r.rung for r in result.premium_ladder] == [
        "risk_premium", "office_premium", "constraints", "instalment_loading", "payable_premium",
    ], "a declined quote's ladder must stay fully populated (FR-256)"
    assert result.premium_ladder[-1].value_minor > 0


@pytest.mark.req("FR-256")
async def test_a_binding_clamp_is_attributed_to_the_constraints_rung() -> None:
    """Replaces `test_a_clamp_overrides_the_ladder_and_is_recorded_on_the_constraints_rung`,
    which asserted `office.value_minor == 999_999` and so fixed FD-1330's misattribution:
    the clamp's effect was carried by the rung it overwrote, and `constraints` said `none`.
    Now `office_premium` keeps its own pre-clamp value and x1.1, and `constraints` is the
    clamp (`RL-1329` §2 step 5)."""
    compiled = await _compiled()
    ctx = _ctx(inputs={
        "driver_age": 34, "channel": "direct", "min_premium_minor": 999_999,
        "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
    })
    result = await score_one(compiled, ctx, trace=True)

    assert result.outcome == "quoted"
    office = next(r for r in result.premium_ladder if r.rung == "office_premium")
    assert office.value_minor != 999_999
    constraints = next(r for r in result.premium_ladder if r.rung == "constraints")
    assert constraints.value_minor == 999_999
    assert constraints.operation is not None
    assert constraints.operation.kind == "clamp"
    assert constraints.operation.bound == "min"
    assert constraints.operation.bound_unrounded_minor == 999_999
    assert constraints.operation.applied == ["MIN_PREMIUM_APPLIED"]
    assert result.trace is not None
    assert result.trace.ladder_reconciled is True


@pytest.mark.req("FR-256")
async def test_removing_the_constraint_check_would_be_caught(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifies the negative test above actually exercises the guard: patching
    `_apply_constraints` to always report no violations must turn the two-decline test's
    own assertion red — proving the guard, not merely a test that has never been seen to
    fail (`CLAUDE.md` §13)."""
    import pricing_core.rating.score as score_module

    monkeypatch.setattr(score_module, "_apply_constraints", lambda algorithm, result: ([], []))
    compiled = await _compiled()
    ctx = _ctx(inputs={
        "driver_age": 34, "channel": "direct", "min_premium_minor": 0,
        "sanity_cap_minor": 100, "sanity_floor_minor": 999_999_999,
    })
    result = await score_one(compiled, ctx)
    assert result.outcome == "quoted", "the patched double should have declined and did not"


# ---------------------------------------------------------------------------
# FR-255: one typed-error test per category.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-255")
async def test_a_contract_violation_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    compiled = await _compiled()
    ctx = _ctx(inputs={
        "driver_age": 5,  # below the declared minimum of 17
        "channel": "direct", "min_premium_minor": 0, "sanity_cap_minor": 1, "sanity_floor_minor": 0,
    })
    with pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION"):
        await score_one(compiled, ctx)


@pytest.mark.req("FR-255")
async def test_a_rate_table_miss_is_refused() -> None:
    """`on_miss="error"` (Task 1.3's own fixture default) and a key the seeded table does
    not carry."""
    compiled = await _compiled()
    ctx = _ctx(inputs={
        "driver_age": 34, "channel": "aggregator",  # not in {"direct", "broker"}
        "min_premium_minor": 0, "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
    })
    # "aggregator" also fails the enum domain check (INPUT_CONTRACT_VIOLATION) before the
    # table is ever consulted — a stronger refusal earlier in the pipeline is not a defect,
    # but it means this test needs a channel the *input contract* accepts and the *table*
    # does not carry, to isolate RATE_TABLE_MISS specifically.
    with pytest.raises(ValueError, match=r"INPUT_CONTRACT_VIOLATION|RATE_TABLE_MISS"):
        await score_one(compiled, ctx)


@pytest.mark.req("FR-255")
async def test_a_rate_table_miss_is_refused_with_the_right_code() -> None:
    """The isolated form of the test above: a channel the input contract accepts but the
    seeded rate table does not carry a row for."""
    from model_schema.rating import RatingAlgorithm

    resolver = _FakeResolver()
    payload = _algorithm_payload()
    for field in payload["input_contract"]:
        if field["name"] == "channel":
            field["domain"] = ["direct", "broker", "unseeded"]
    resolver._payloads["rating_algorithm:score-fixture@1"] = payload
    RatingAlgorithm.model_validate(payload)  # sanity: still a valid algorithm shape
    bundle = await compile_bundle(_version(), resolver)
    compiled = load_bundle(bundle)

    ctx = _ctx(inputs={
        "driver_age": 34, "channel": "unseeded",
        "min_premium_minor": 0, "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
    })
    with pytest.raises(ValueError, match="RATE_TABLE_MISS"):
        await score_one(compiled, ctx)


@pytest.mark.req("FR-255")
async def test_a_reference_lookup_miss_is_refused() -> None:
    """A minimal, separate algorithm exercising only a `lookup` step with `on_miss="error"`
    — the fixture's own scope is this one error category."""
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.compile import to_jdm
    from pricing_core.rating.runtime import to_wire

    algo_payload = {
        "slug": "lookup-miss-fixture", "version": 1,
        "input_contract": [{"name": "postcode", "type": "string", "nullable": False}],
        "outputs": [{"name": "area_out", "type": "string", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "Postcode", "input_name": "postcode",
             "on_missing": "error", "produces": "postcode"},
            {"step_id": "s_area", "type": "lookup", "label": "Area",
             "reference_table_ref": "reference_table:ons@1", "key_expr": ["postcode"],
             "as_at": "effective_date", "on_miss": "error", "consumes": ["postcode"],
             "produces": "area_code"},
            {"step_id": "s_out", "type": "output", "label": "Area out",
             "output_name": "area_out", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["area_code"]},
        ],
        "sub_graphs": [],
    }
    algo = RatingAlgorithm.model_validate(algo_payload)
    graph = to_jdm(algo)
    payloads = {
        "reference_table:ons@1": {
            "rows": [
                {
                    "key": "SW1A",
                    "payload": {"area_code": "LDN"},
                    "effective_from": "2020-01-01",
                    "effective_to": None,
                }
            ]
        }
    }
    from pricing_core.rating.score import _check_lookup_misses

    wire = to_wire(graph, payloads)
    import zen

    decision = zen.ZenEngine().create_decision(json.dumps(wire))
    decision.validate()
    result = decision.evaluate({"postcode": "UNKNOWN", "effective_date": "2026-06-01"})["result"]
    with pytest.raises(ValueError, match="REFERENCE_LOOKUP_MISS"):
        _check_lookup_misses(algo, result)
    # Positive control: a key the table does carry does not raise.
    matched = decision.evaluate({"postcode": "SW1A", "effective_date": "2026-06-01"})["result"]
    _check_lookup_misses(algo, matched)  # must not raise


@pytest.mark.req("FR-255")
async def test_a_model_call_failure_is_refused_with_the_real_message() -> None:
    """`MODEL_CALL_FAILED` — via the GLM refusal `runtime.py` already establishes, now
    surfaced by `score_one` reading the sentinel rather than the engine's own generic
    wrapper (see `score.py`'s module docstring)."""
    compiled = await _compiled(glm=True)
    with pytest.raises(ValueError, match="MODEL_CALL_FAILED"):
        await score_one(compiled, _ctx())


# ---------------------------------------------------------------------------
# FR-218: the purpose-gated sub-graph refusal, parametrised over both members.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-218")
@pytest.mark.parametrize("purpose", ["mid_term_adjustment", "cancellation"])
async def test_a_purpose_needing_a_sub_graph_is_refused_when_none_is_mounted(purpose: str) -> None:
    """RL-878: both members, not one — `cancellation` is `mid_term_adjustment`'s
    stranded list-mate, and a guard proven on one limb alone is half-proven."""
    compiled = await _compiled()
    ctx = _ctx(purpose=purpose)
    with pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION"):
        await score_one(compiled, ctx)


async def _compiled_with_bogus_sub_graph() -> CompiledBundle:
    """The same bundle, its algorithm naming a sub-graph that does not exist (the finding
    "CR-838 marks FR-217 delivered, but its pin and bundle-time inlining are not built")."""
    compiled = await _compiled()
    bogus = SubGraphRef(
        ref=ArtifactRef(type="sub_graph", slug="does-not-exist", version=1),
        mount_point="s_nowhere",
    )
    algorithm = compiled.algorithm.model_copy(update={"sub_graphs": [bogus]})
    return dataclasses.replace(compiled, algorithm=algorithm)


@pytest.mark.req("FR-218")
@pytest.mark.parametrize("purpose", ["mid_term_adjustment", "cancellation"])
async def test_a_bogus_sub_graph_ref_does_not_satisfy_the_purpose_guard(purpose: str) -> None:
    """A non-empty `sub_graphs` is a declared reference, not a mounted sub-graph (the finding
    "CR-838 marks FR-217 delivered, but its pin and bundle-time inlining are not built").
    With `sub_graph:does-not-exist@1` named, these purposes were priced as new business
    (1507); they are refused whatever `sub_graphs` holds, until FR-217's inlining exists."""
    compiled = await _compiled_with_bogus_sub_graph()
    with pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION") as refused:
        await score_one(compiled, _ctx(purpose=purpose))
    assert "interim" in str(refused.value)


@pytest.mark.req("FR-218")
@pytest.mark.parametrize("purpose", ["new_business", "renewal", "what_if"])
async def test_the_other_purposes_are_unaffected_on_the_same_algorithm(purpose: str) -> None:
    """Positive control for the test above: the same bogus-ref algorithm still quotes the
    purposes that need no mounted sub-graph."""
    compiled = await _compiled_with_bogus_sub_graph()
    result = await score_one(compiled, _ctx(purpose=purpose))
    assert result.outcome == "quoted"


@pytest.mark.req("FR-218")
async def test_new_business_is_not_refused_by_the_purpose_guard() -> None:
    """Positive control: the guard fires on the two gated purposes only."""
    compiled = await _compiled()
    result = await score_one(compiled, _ctx(purpose="new_business"))
    assert result.outcome == "quoted"


@pytest.mark.req("FR-218")
async def test_the_purpose_guard_would_be_caught_if_removed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A check that has never been seen to fail has not been tested (`CLAUDE.md` §13)."""
    import pricing_core.rating.score as score_module

    monkeypatch.setattr(score_module, "_check_purpose_mount", lambda algorithm, ctx: None)
    compiled = await _compiled()
    result = await score_one(compiled, _ctx(purpose="mid_term_adjustment"))
    assert result.outcome == "quoted", "the patched guard should have let this price silently"


# ---------------------------------------------------------------------------
# FR-252: the instalment_loading rung, and the billing-surface refusal.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-252")
async def test_the_instalment_loading_rung_reconciles() -> None:
    compiled = await _compiled()
    result = await score_one(compiled, _ctx())
    rungs = {r.rung: r.value_minor for r in result.premium_ladder}
    assert "instalment_loading" in rungs
    assert rungs["instalment_loading"] != rungs["office_premium"], "the loading did nothing"


@pytest.mark.req("FR-252")
@pytest.mark.parametrize("key", ["payment_schedule", "apr", "credit_agreement_term"])
async def test_a_billing_surface_request_is_refused(key: str) -> None:
    """The second half of FR-252: never answered approximately."""
    compiled = await _compiled()
    ctx = _ctx(inputs={
        "driver_age": 34, "channel": "direct", "min_premium_minor": 0,
        "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0, key: True,
    })
    with pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION"):
        await score_one(compiled, ctx)


@pytest.mark.req("FR-252")
async def test_the_billing_surface_guard_would_be_caught_if_removed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import pricing_core.rating.score as score_module

    monkeypatch.setattr(score_module, "_check_billing_surface", lambda ctx: None)
    compiled = await _compiled()
    ctx = _ctx(inputs={
        "driver_age": 34, "channel": "direct", "min_premium_minor": 0,
        "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0, "apr": True,
    })
    result = await score_one(compiled, ctx)
    assert result.outcome == "quoted", "the patched guard should have priced this silently"


# ---------------------------------------------------------------------------
# FR-258: the trace.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-258")
@pytest.mark.req("NFR-490")
async def test_trace_true_returns_a_populated_trace_and_the_identical_premium() -> None:
    compiled = await _compiled()
    ctx = _ctx()
    untraced = await score_one(compiled, ctx, trace=False)
    traced = await score_one(compiled, ctx, trace=True)

    assert untraced.trace is None
    assert traced.trace is not None
    assert traced.trace.ladder_reconciled is True
    # `input`/`output`-typed steps never appear individually: `to_wire` collapses every
    # `input` step into one wire `inputNode` and has no wire node for `output` steps at
    # all (`score.py`'s own "Ladder construction" design note) — only the interior step
    # types (table/lookup/expression/model_call/constraint) get their own trace entry.
    assert {s.step_id for s in traced.trace.steps} >= {
        "s_expense", "s_risk", "s_office", "s_clamp", "s_decl_cap", "s_decl_floor", "s_instalment",
    }
    assert {"s_in_age", "s_in_channel", "s_out_risk", "s_out_office", "s_out_payable"}.isdisjoint(
        {s.step_id for s in traced.trace.steps}
    )
    assert all(step.elapsed_us >= 0 for step in traced.trace.steps)

    # NFR-490 / R3: tracing never changes the result.
    assert traced.model_copy(update={"trace": None, "timing_ms": {}}) == untraced.model_copy(
        update={"timing_ms": {}}
    )


# ---------------------------------------------------------------------------
# NFR-491: zero database or network access, proven on broken input.
# ---------------------------------------------------------------------------


@pytest.mark.req("NFR-491")
async def test_score_one_makes_no_network_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patches `socket.socket` to raise for the duration of one `score_one` call and
    asserts no exception — then, in the same test, proves the patch actually catches a
    real attempt (a mock that catches nothing passes silently, `CLAUDE.md` §13)."""

    def _forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("score_one attempted to open a network socket (NFR-491)")

    compiled = await _compiled()
    monkeypatch.setattr(socket, "socket", _forbidden)
    result = await score_one(compiled, _ctx())
    assert result.outcome == "quoted"

    with pytest.raises(AssertionError, match="NFR-491"):
        socket.socket()  # the deliberate call the guard must catch


# ---------------------------------------------------------------------------
# NFR-495: determinism, in-process and across a subprocess.
# ---------------------------------------------------------------------------


@pytest.mark.req("NFR-495")
async def test_scoring_is_deterministic_in_process() -> None:
    compiled = await _compiled()
    ctx = _ctx()
    first = await score_one(compiled, ctx)
    second = await score_one(compiled, ctx)
    assert first.model_copy(update={"timing_ms": {}}) == second.model_copy(update={"timing_ms": {}})


# The child of `test_scoring_is_deterministic_across_a_subprocess`. It reads the fixture's
# inputs from stdin (the parent builds them; the test module is never imported here), compiles
# and scores with `pricing_core.rating` alone, prints one JSON line, flushes, and leaves with
# `os._exit(0)` — no interpreter teardown (FD-1199). Kept as plain source so the child's
# imports are exactly what is written below.
_DETERMINISM_CHILD = """
import asyncio, json, os, sys
from datetime import date, datetime
from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from model_schema.scoring import QuoteContext, QuoteContextOptions
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import load_bundle
from pricing_core.rating.score import score_one

spec = json.load(sys.stdin)


class Resolver:
    async def resolve(self, ref):
        return ResolvedArtifact(status='approved', payload=spec['payloads'][str(ref)])


async def main():
    version = RatingVersion.model_validate(spec['version'])
    compiled = load_bundle(await compile_bundle(version, Resolver()))
    ctx = QuoteContext.model_validate({
        'purpose': 'new_business', 'quoted_at': datetime(2026, 8, 29, 12, 0, 0),
        'effective_date': date(2026, 9, 1), 'inputs': spec['inputs'],
        'options': QuoteContextOptions(rating_version_ref=ArtifactRef(
            type='rating_version', slug='score-fixture', version=1)),
    })
    result = await score_one(compiled, ctx)
    return {'hash': compiled.content_hash,
            'payable': result.outputs['payable_premium_minor'], 'outcome': result.outcome}


out = asyncio.run(main())
out['modules'] = sorted({name.split('.')[0] for name in sys.modules})
print(json.dumps(out))
sys.stdout.flush()
os._exit(0)
"""


@pytest.mark.req("NFR-495")
def test_scoring_is_deterministic_across_a_subprocess() -> None:
    """The same bundle recompiled and scored in a fresh interpreter reproduces the same
    `content_hash` and the same premium — byte-for-byte, across processes (FR-11).

    **This proves the determinism of the RESULT, not a clean interpreter shutdown.** The
    child prints its result, flushes, and leaves with `os._exit(0)`, so no finalisation runs.
    An earlier child that exited normally aborted natively once in CI, at finalisation, with
    `PyGILState_Release ... must be current` and return code -6 (FD-1199); that abort happens
    after the result is written, and it says nothing about scoring. A child that fails for
    any reason, including a non-zero exit, still fails this test.

    The child imports `pricing_core.rating` and `model_schema` only, not this module or
    pytest: the parent hands it the fixture's artifacts and quote inputs as JSON on stdin.
    (Scoring an XGBoost booster still loads xgboost's own dependencies in the child.)
    """
    resolver = _FakeResolver()
    inputs = _ctx().inputs
    payload = json.dumps({
        "version": _version().model_dump(mode="json"),
        "payloads": resolver._payloads,
        "inputs": inputs,
    })
    proc = subprocess.run(
        [sys.executable, "-c", _DETERMINISM_CHILD],
        input=payload, capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    child = json.loads(proc.stdout.strip().splitlines()[-1])
    modules = child.pop("modules")
    assert not {"pytest", "test_rating_score", "test_rating_runtime"} & set(modules), (
        "the child must not import the test module or pytest"
    )

    async def _in_process() -> dict[str, Any]:
        compiled = await _compiled()
        result = await score_one(compiled, _ctx())
        return {
            "hash": compiled.content_hash,
            "payable": result.outputs["payable_premium_minor"],
            "outcome": result.outcome,
        }

    in_process_result = asyncio.run(_in_process())
    assert child == in_process_result


# ---------------------------------------------------------------------------
# Step 13: the concurrency smoke test.
# ---------------------------------------------------------------------------


@pytest.mark.req("NFR-489")
async def test_concurrent_scoring_against_one_shared_bundle_does_not_cross_talk() -> None:
    """`asyncio.gather` over many `score_one` calls against one shared `CompiledBundle` —
    the shape a real worker process serves, not a bare `asyncio.run` per call. Each quote
    carries a distinct `driver_age`; if any two calls corrupted or crossed each other's
    state, at least one result would not match its own deterministic single-call
    equivalent, or two distinct ages would report the same premium as a *coincidence*
    rather than because they happen to fall in the same booster leaf — checked by
    comparing every concurrent result against a freshly, independently computed one."""
    compiled = await _compiled()
    ages = list(range(18, 18 + 40))

    async def _one(age: int) -> Any:
        ctx = _ctx(inputs={
            "driver_age": age, "channel": "direct" if age % 2 else "broker",
            "min_premium_minor": 0, "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
        })
        return await score_one(compiled, ctx)

    concurrent_results = await asyncio.gather(*(_one(age) for age in ages))
    sequential_results = [await _one(age) for age in ages]

    triples = zip(ages, concurrent_results, sequential_results, strict=True)
    for age, concurrent, sequential in triples:
        assert concurrent.model_copy(update={"timing_ms": {}}) == sequential.model_copy(
            update={"timing_ms": {}}
        ), f"age={age}: concurrent scoring diverged from sequential — cross-talk"


# ---------------------------------------------------------------------------
# WK-1178 code slice (PL-1314, RL-1313 DP-G4, FD-1317): a division in a decline condition or a
# clamp bound is refused at save; a residual evaluation failure has its own code.
# ---------------------------------------------------------------------------


def _with_step(step_id: str, **fields: Any) -> dict[str, Any]:
    payload = _algorithm_payload()
    for step in payload["steps"]:
        if step["step_id"] == step_id:
            step.update(fields)
    return payload


async def _compile_with(payload: dict[str, Any]) -> CompiledBundle:
    resolver = _FakeResolver()
    resolver._payloads["rating_algorithm:score-fixture@1"] = payload
    return load_bundle(await compile_bundle(_version(), resolver))


#: FD-1317 D2: a `??` "guard" on a decline condition that fails open when the divisor is 0.
_D2_CONDITION = "((office_premium_minor / sanity_floor_minor) ?? 0) <= 2"
#: FD-1317 E3/E4: a `??` "guard" on a clamp bound that silently loses the cap at divisor 0.
_E4_BOUND = "(sanity_cap_minor / sanity_floor_minor) ?? 999999999999"


@pytest.mark.req("FR-274")
@pytest.mark.parametrize(("step_id", "fields"), [
    pytest.param("s_decl_cap", {"condition": _D2_CONDITION}, id="D2_decline_condition"),
    pytest.param("s_clamp", {"clamp_bounds": {"min": "min_premium_minor", "max": _E4_BOUND}},
                 id="E4_clamp_bound"),
])
async def test_a_masked_division_in_a_condition_or_bound_is_refused_at_compile(
    step_id: str, fields: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match=r"^EXPRESSION_UNGUARDED_DIVISION:"):
        await _compile_with(_with_step(step_id, **fields))


def _hand_compiled(payload: dict[str, Any]) -> CompiledBundle:
    """A bundle built without `compile_bundle`, since after this slice these cannot be saved."""
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.compile import Bundle, bundle_hash, to_jdm

    resolver = _FakeResolver()
    algorithm = RatingAlgorithm.model_validate(payload)
    pins = _version().pins
    assert pins is not None
    graph = to_jdm(algorithm)
    payloads = {"rating_algorithm:score-fixture@1": payload,
                **{str(ref): resolver._payloads[str(ref)]
                   for ref in (*pins.rate_tables, *pins.models)}}
    return load_bundle(Bundle(
        algorithm_ref="rating_algorithm:score-fixture@1", graph=graph, resolved_payloads=payloads,
        pins=pins, content_hash=bundle_hash(graph, pins),
        compiled_at=datetime(2026, 8, 29, 12, 0, 0),
    ))


_ZERO_FLOOR = {
    "driver_age": 34, "channel": "direct", "min_premium_minor": 0,
    "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
}


@pytest.mark.req("FR-255")
@pytest.mark.parametrize(("step_id", "fields"), [
    pytest.param("s_decl_cap", {"condition": "office_premium_minor / sanity_floor_minor <= 2"},
                 id="A2_decline_condition"),
    pytest.param("s_clamp", {"clamp_bounds": {"min": "min_premium_minor",
                                              "max": "sanity_cap_minor / sanity_floor_minor"}},
                 id="C1_clamp_bound"),
])
async def test_a_residual_evaluation_failure_is_not_a_table_miss(
    step_id: str, fields: dict[str, Any]
) -> None:
    """RL-1313 DP-G4: these steps consume `office_premium_minor`, not a table's output."""
    compiled = _hand_compiled(_with_step(step_id, **fields))
    with pytest.raises(ValueError, match=r"^RATING_EVALUATION_FAILED:"):
        await score_one(compiled, _ctx(inputs=_ZERO_FLOOR))


@pytest.mark.req("FR-255")
async def test_the_stated_residual_still_reports_the_miss_code() -> None:
    """RL-1313 DP-G4's stated limit, pinned so a change to it is visible: a failing step that
    itself directly consumes an `on_miss="error"` output reports the miss code (the engine's
    error has the same shape as a genuine miss). FD working id 9888 owns the fix."""
    payload = _with_step(
        "s_office",
        expr="risk_premium_minor * expense_factor * (1 / (expense_factor - expense_factor))",
    )
    compiled = _hand_compiled(payload)
    with pytest.raises(ValueError, match=r"^RATE_TABLE_MISS:"):
        await score_one(compiled, _ctx())


@pytest.mark.req("FR-255")
@pytest.mark.parametrize("engine_error", [
    "boom",
    '{"type":"NodeError","source":"x"}',
    '{"type":"NodeError","source":"x","nodeId":"not_a_step"}',
    '{"type":"NodeError","source":"x","nodeId":"s_out_payable"}',
])
def test_no_engine_failure_escapes_as_a_bare_runtime_error(engine_error: str) -> None:
    """RL-1313 DP-G4: a missing or unparseable `nodeId` also takes the new code."""
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.score import _reraise_engine_failure

    algorithm = RatingAlgorithm.model_validate(_algorithm_payload())
    with pytest.raises(ValueError, match=r"^RATING_EVALUATION_FAILED:"):
        _reraise_engine_failure(algorithm, RuntimeError(engine_error))


@pytest.mark.req("FR-255")
def test_an_engine_failure_with_no_table_or_lookup_to_blame_is_coded() -> None:
    """The former bare `raise exc` fallthrough: no `on_miss="error"` step exists at all."""
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.score import _reraise_engine_failure

    algorithm = RatingAlgorithm.model_validate(_with_step("s_expense", on_miss="default"))
    with pytest.raises(ValueError, match=r"^RATING_EVALUATION_FAILED:"):
        _reraise_engine_failure(algorithm, RuntimeError("boom"))


@pytest.mark.req("NFR-499")
def test_an_engine_error_text_never_reaches_the_raised_message() -> None:
    """The sentinel for `_failing_node`'s read of the engine error (`test_error_sinks.py`): the
    engine's text can carry anything, and only a matched step's own id may be named."""
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.score import _reraise_engine_failure

    sentinel = "SENTINEL-quote-input-d7e3c518"
    algorithm = RatingAlgorithm.model_validate(_algorithm_payload())
    for nodeid in ("s_decl_cap", sentinel):
        engine_error = f'{{"type":"NodeError","source":"{sentinel}","nodeId":"{nodeid}"}}'
        with pytest.raises(ValueError, match=r"^RATING_EVALUATION_FAILED:") as raised:
            _reraise_engine_failure(algorithm, RuntimeError(engine_error))
        assert sentinel not in str(raised.value)
