"""The exact Premium Ladder (`RL-1329`, FD-1336, FD-1330): WK-674 Slice 3, Task 6.

Each test names the `RL-1329` Acceptance item it carries. The realistic-scale cases run
through a real ZEN evaluation and `score_one(trace=True)`, never a reimplementation.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal, localcontext
from typing import Any

import pytest
from test_rating_score import _RATING_VERSION_REF, _algorithm_payload, _FakeResolver, _version

from model_schema.scoring import QuoteContext, QuoteContextOptions
from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_one

_HALF_EVEN = {"mode": "half_even", "dp": 0}


def _out(step_id: str, name: str, consumes: str, mode: str = "half_even") -> dict[str, Any]:
    return {
        "step_id": step_id, "type": "output", "label": name, "output_name": name,
        "rounding": {"mode": mode, "dp": 0}, "consumes": [consumes],
    }


def _chain_algorithm(
    *, factors: list[tuple[str, str, str]], extra_outputs: tuple[str, ...] = ()
) -> dict[str, Any]:
    """`risk_premium_minor` is an input; each `(rung, expression, mode)` is one expression
    step followed by its output step; the last rung present is `payable_premium`."""
    steps: list[dict[str, Any]] = [
        {"step_id": "s_in_risk", "type": "input", "label": "Risk premium",
         "input_name": "risk_premium_minor", "on_missing": "error",
         "produces": "risk_premium_minor"},
        _out("s_out_risk", "risk_premium_minor", "risk_premium_minor"),
    ]
    previous = "risk_premium_minor"
    outputs = [{"name": "payable_premium_minor", "type": "money_minor", "required": True}]
    for rung, expression, mode in factors:
        name = f"{rung}_minor"
        steps.append({
            "step_id": f"s_{rung}", "type": "expression", "label": rung,
            "expr": expression.replace("{prev}", previous), "result_type": "money_minor",
            "consumes": [previous], "produces": name,
        })
        steps.append(_out(f"s_out_{rung}", name, name, mode))
        previous = name
    steps.append(_out("s_out_payable", "payable_premium_minor", previous))
    for extra in extra_outputs:
        outputs.append({"name": extra, "type": "money_minor", "required": True})
    return {
        "slug": "score-fixture", "version": 1,
        "input_contract": [{"name": "risk_premium_minor", "type": "decimal", "nullable": False}],
        "outputs": outputs, "steps": steps, "sub_graphs": [],
    }


async def _compile_payload(payload: dict[str, Any]) -> CompiledBundle:
    resolver = _FakeResolver()
    resolver._payloads["rating_algorithm:score-fixture@1"] = payload
    return load_bundle(await compile_bundle(_version(), resolver))


def _context(**inputs: Any) -> QuoteContext:
    return QuoteContext.model_validate({
        "purpose": "new_business", "quoted_at": datetime(2026, 8, 29, 12, 0, 0),
        "effective_date": date(2026, 9, 1), "inputs": inputs,
        "options": QuoteContextOptions(rating_version_ref=_RATING_VERSION_REF),
    })


@pytest.mark.req("FR-248")
async def test_the_realistic_scale_case_reconciles_and_prices_70726() -> None:
    """Acceptance 1 (`RL-1329`): risk 61234.5, office = risk x 1.1, instalment = office x 1.05.
    Red on `origin/main`: `ladder_reconciled` is True while the ladder replays to 70725
    against a payable of 70726, and office is 67357."""
    payload = _chain_algorithm(
        factors=[
            ("office_premium", "{prev} * 1.1", "half_even"),
            ("instalment_loading", "{prev} * 1.05", "half_even"),
        ],
        extra_outputs=("office_premium_minor",),
    )
    bundle = await _compile_payload(payload)
    result = await score_one(bundle, _context(risk_premium_minor=61234.5), trace=True)

    ladder = {r.rung: r for r in result.premium_ladder}
    assert [r.value_minor for r in result.premium_ladder] == [
        61234, 67358, 67358, 70726, 70726,
    ]
    assert ladder["office_premium"].operation is not None
    assert ladder["office_premium"].operation.factor == Decimal("1.1")
    assert ladder["office_premium"].unrounded_minor == Decimal("67357.95")
    assert result.outputs["office_premium_minor"] == 67358
    assert result.outputs["payable_premium_minor"] == 70726
    assert result.trace is not None
    assert result.trace.ladder_reconciled is True


@pytest.mark.req("FR-248")
async def test_the_auditors_case_at_unit_level() -> None:
    """Acceptance 1, second half: 60000.4 -> 66000.44 -> 69402.0."""
    payload = _chain_algorithm(
        factors=[
            ("office_premium", "{prev} * 1.1", "half_even"),
            ("instalment_loading", "{prev} + 3401.56", "half_even"),
        ],
    )
    result = await score_one(
        await _compile_payload(payload), _context(risk_premium_minor=60000.4), trace=True
    )
    assert [r.value_minor for r in result.premium_ladder] == [60000, 66000, 66000, 69402, 69402]
    assert result.premium_ladder[1].unrounded_minor == Decimal("66000.44")
    assert result.premium_ladder[3].unrounded_minor == Decimal("69402")
    assert result.trace is not None
    assert result.trace.ladder_reconciled is True


# ---------------------------------------------------------------------------
# Helpers that expose the engine's raw result and the predicate's independent inputs.
# ---------------------------------------------------------------------------


async def _built(payload: dict[str, Any], **inputs: Any):  # type: ignore[no-untyped-def]
    """`(ladder, ladder_inputs, result)` for one quote, from the real engine and the real
    builder, so a test can mutate the ladder and ask the predicate."""
    from pricing_core.rating import score as score_module

    bundle = await _compile_payload(payload)
    context = {"effective_date": "2026-09-01", "purpose": "new_business", **inputs}
    out = await bundle.decision.async_evaluate(context, {"trace": False})
    result = out["result"]
    _, codes = score_module._apply_constraints(bundle.algorithm, result)
    ladder_inputs = score_module._ladder_inputs(bundle.algorithm, result, codes)
    ladder = score_module._build_ladder(ladder_inputs, codes)
    return ladder, ladder_inputs, result


_TWO_RUNGS = [
    ("expense_loading", "{prev} * 1.15", "half_even"),
    ("office_premium", "{prev} * 1.131", "half_even"),
    ("instalment_loading", "0.875 > 0 ? {prev} / 0.875 : 0", "half_even"),
]


@pytest.mark.req("FR-248")
async def test_every_single_operation_rung_records_its_operand_exactly() -> None:
    """Acceptance 2: x1.15 stays x1.15, /0.875 stays /0.875 (never quantised to 4 dp)."""
    ladder, inputs, _ = await _built(
        _chain_algorithm(factors=_TWO_RUNGS), risk_premium_minor=24150.4
    )
    from pricing_core.rating.ladder import reconcile_ladder

    operations = {r.rung: r.operation for r in ladder}
    assert operations["expense_loading"] is not None
    assert operations["expense_loading"].factor == Decimal("1.15")
    assert operations["office_premium"] is not None
    assert operations["office_premium"].factor == Decimal("1.131")
    assert operations["instalment_loading"] is not None
    assert operations["instalment_loading"].kind == "divide"
    assert operations["instalment_loading"].divisor == Decimal("0.875")
    assert reconcile_ladder(ladder, inputs)


@pytest.mark.req("FR-248")
async def test_planted_defects_each_fail_the_predicate() -> None:
    """Acceptance 3: the six planted-defect controls. A check that has never printed a
    failure has not been tested (CLAUDE.md §13)."""
    from pricing_core.rating.ladder import ladder_violations

    ladder, inputs, _ = await _built(
        _chain_algorithm(factors=_TWO_RUNGS), risk_premium_minor=24150.4
    )
    assert ladder_violations(ladder, inputs) == []

    def replace(index: int, **fields: Any) -> list[Any]:
        changed = list(ladder)
        changed[index] = ladder[index].model_copy(update=fields)
        return changed

    def with_operation(index: int, **fields: Any) -> list[Any]:
        operation = ladder[index].operation
        assert operation is not None
        return replace(index, operation=operation.model_copy(update=fields))

    for index, rung in enumerate(ladder):
        # a displayed value + 1 on any rung
        assert ladder_violations(replace(index, value_minor=rung.value_minor + 1), inputs), rung
    for index, rung in enumerate(ladder):
        operation = rung.operation
        if operation is None:
            continue
        if operation.kind == "multiply":
            assert operation.factor is not None
            planted = with_operation(index, factor=operation.factor * Decimal("1.000001"))
        elif operation.kind == "divide":
            assert operation.divisor is not None
            planted = with_operation(index, divisor=operation.divisor * Decimal("1.000001"))
        else:
            continue
        assert ladder_violations(planted, inputs), f"{rung.rung}: factor/divisor x 1.000001"
    # the payable's displayed value + 1 (also covered above), the first rung's unrounded value
    first = ladder[0].unrounded_minor
    assert first is not None
    assert ladder_violations(replace(0, unrounded_minor=first + Decimal("0.001")), inputs)


@pytest.mark.req("FR-248")
async def test_an_added_amount_plus_a_cent_fails_the_predicate() -> None:
    from pricing_core.rating.ladder import ladder_violations

    payload = _chain_algorithm(factors=[("ipt_and_fees", "{prev} + 38.4", "half_even")])
    ladder, inputs, _ = await _built(payload, risk_premium_minor=1000.25)
    index = next(i for i, r in enumerate(ladder) if r.rung == "ipt_and_fees")
    added = ladder[index]
    assert added.operation is not None
    assert added.operation.kind == "add"
    assert added.operation.amount_unrounded_minor == Decimal("38.4")
    planted = list(ladder)
    planted[index] = added.model_copy(
        update={"operation": added.operation.model_copy(
            update={"amount_unrounded_minor": Decimal("38.41")})}
    )
    assert ladder_violations(ladder, inputs) == []
    assert ladder_violations(planted, inputs)


@pytest.mark.req("FR-248")
async def test_a_payable_source_off_the_previous_rung_fails_the_predicate() -> None:
    """Acceptance 3, sixth control: a payable source 0.6 away from the previous rung is a
    jump the ladder cannot explain as `round`."""
    from pricing_core.rating.ladder import ladder_violations

    payload = _chain_algorithm(factors=[("office_premium", "{prev} * 1.1", "half_even")])
    steps = payload["steps"]
    steps.insert(-1, {
        "step_id": "s_off", "type": "expression", "label": "off", "expr":
        "office_premium_minor + 0.6", "result_type": "money_minor",
        "consumes": ["office_premium_minor"], "produces": "payable_source",
    })
    steps[-1] = {**steps[-1], "consumes": ["payable_source"]}
    ladder, inputs, _ = await _built(payload, risk_premium_minor=1000)
    violations = ladder_violations(ladder, inputs)
    assert any("R3" in v and "payable_premium" in v for v in violations), violations


@pytest.mark.req("FR-248")
async def test_the_near_tie_prices_1235_not_1234() -> None:
    """Acceptance 4: engine value 1234.50000000000000012345 is 1235 rounded once; the float
    path (1234.5 -> half_even 1234) misprices it."""
    payload = _chain_algorithm(
        factors=[("office_premium", "{prev} * 1.0000000000000000001", "half_even")]
    )
    result = await score_one(
        await _compile_payload(payload), _context(risk_premium_minor=1234.5), trace=True
    )
    assert result.outputs["payable_premium_minor"] == 1235
    assert result.premium_ladder[-1].value_minor == 1235
    assert result.trace is not None
    assert result.trace.ladder_reconciled is True


@pytest.mark.req("FR-248")
async def test_a_ladder_is_never_built_from_floats_alone() -> None:
    """Acceptance 4, second half: `_build_ladder` takes exact decimals (`LadderInputs`), and
    a result lacking the engine's `string()` reads yields no rung at all, so the builder
    cannot fall back to the float in `result[name]`."""
    from pricing_core.rating import score as score_module

    payload = _chain_algorithm(factors=[("office_premium", "{prev} * 1.1", "half_even")])
    _, inputs, result = await _built(payload, risk_premium_minor=1000.5)
    assert all(isinstance(v, Decimal) for v in inputs.exact.values())
    floats_only = {k: v for k, v in result.items() if not k.startswith("__exact__")}
    bundle = await _compile_payload(payload)
    stripped = score_module._ladder_inputs(bundle.algorithm, floats_only, [])
    assert stripped.exact == {}
    assert score_module._build_ladder(stripped, []) == []


@pytest.mark.req("FR-248")
async def test_rung_shapes_first_rung_payable_only_and_no_payable() -> None:
    """Acceptance 6: a first rung that is not `risk_premium`; a payable-only ladder; a ladder
    with rungs but no payable rung."""
    from pricing_core.rating.ladder import ladder_violations

    # first rung is office_premium (no risk_premium output step): reconciles
    payload = _chain_algorithm(factors=[("office_premium", "{prev} * 1.1", "half_even")])
    payload["steps"] = [s for s in payload["steps"] if s["step_id"] != "s_out_risk"]
    ladder, inputs, _ = await _built(payload, risk_premium_minor=1000)
    assert [r.rung for r in ladder] == ["office_premium", "constraints", "payable_premium"]
    assert ladder_violations(ladder, inputs) == []

    # payable-only ladder reconciles
    only = _chain_algorithm(factors=[])
    only["steps"] = [s for s in only["steps"] if s["step_id"] != "s_out_risk"]
    ladder, inputs, _ = await _built(only, risk_premium_minor=1000)
    assert [r.rung for r in ladder] == ["payable_premium"]
    assert ladder_violations(ladder, inputs) == []

    # rungs but no payable rung do not reconcile
    full, inputs, _ = await _built(
        _chain_algorithm(factors=[("office_premium", "{prev} * 1.1", "half_even")]),
        risk_premium_minor=1000,
    )
    assert any("payable_premium" in v for v in ladder_violations(full[:-1], inputs))
    # an empty ladder reconciles, for that case alone
    assert ladder_violations([], inputs) == []


# ---------------------------------------------------------------------------
# FD-1330 / RL-1329 Acceptance 10: a binding clamp is attributed to `constraints`.
# ---------------------------------------------------------------------------

_CLAMP_INPUTS = {
    "driver_age": 34, "channel": "direct", "min_premium_minor": 5000,
    "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
}


def _score_fixture(*, outputs: tuple[str, ...] = ()) -> dict[str, Any]:
    payload = _algorithm_payload()
    for name in outputs:
        payload["outputs"].append({"name": name, "type": "money_minor", "required": True})
    return payload


@pytest.mark.req("FR-247")
async def test_a_min_premium_clamp_sits_on_the_constraints_rung() -> None:
    from pricing_core.rating.ladder import ladder_violations

    result = await score_one(
        await _compile_payload(_score_fixture()), _context(**_CLAMP_INPUTS), trace=True
    )
    rungs = {r.rung: r for r in result.premium_ladder}
    assert rungs["office_premium"].value_minor == 1436  # its own value, not the clamp's
    assert rungs["office_premium"].operation is not None
    assert rungs["office_premium"].operation.factor == Decimal("1.1")  # RL-1329, not "1.1000"
    assert str(rungs["office_premium"].operation.factor) == "1.1"
    constraints = rungs["constraints"]
    assert constraints.value_minor == 5000
    assert constraints.operation is not None
    assert constraints.operation.kind == "clamp"
    assert constraints.operation.bound == "min"
    assert constraints.operation.bound_unrounded_minor == Decimal("5000")
    assert constraints.operation.applied == ["MIN_PREMIUM_APPLIED"]
    assert rungs["instalment_loading"].value_minor == 5250
    assert rungs["payable_premium"].value_minor == 5250
    assert result.trace is not None
    assert result.trace.ladder_reconciled is True

    ladder, inputs, _ = await _built(_score_fixture(), **_CLAMP_INPUTS)
    assert ladder_violations(ladder, inputs) == []
    index = next(i for i, r in enumerate(ladder) if r.rung == "constraints")
    operation = ladder[index].operation
    assert operation is not None
    planted_bound = list(ladder)
    planted_bound[index] = ladder[index].model_copy(update={
        "operation": operation.model_copy(
            update={"bound_unrounded_minor": Decimal("5000.001")})
    })
    planted_none = list(ladder)
    planted_none[index] = ladder[index].model_copy(
        update={"operation": operation.model_copy(update={"kind": "none"})}
    )
    assert ladder_violations(planted_bound, inputs)
    assert ladder_violations(planted_none, inputs)


@pytest.mark.req("FR-247")
async def test_an_unclamped_quote_is_unchanged_and_constraints_is_none() -> None:
    result = await score_one(
        await _compile_payload(_score_fixture()),
        _context(**{**_CLAMP_INPUTS, "min_premium_minor": 0}), trace=True,
    )
    constraints = next(r for r in result.premium_ladder if r.rung == "constraints")
    assert constraints.operation is not None
    assert constraints.operation.kind == "none"
    assert constraints.operation.applied == []
    assert result.trace is not None
    assert result.trace.ladder_reconciled is True


def _clamp_variant(
    bounds: dict[str, str], condition: str, consumes: list[str] | None = None
) -> dict[str, Any]:
    payload = _score_fixture()
    for step in payload["steps"]:
        if step["step_id"] == "s_clamp":
            step["clamp_bounds"] = bounds
            step["condition"] = condition
            if consumes is not None:
                step["consumes"] = consumes  # FR-246: the names the variant reads
    return payload


@pytest.mark.req("FR-247")
async def test_a_max_clamp_and_a_step_declaring_both_bounds() -> None:
    """The finding measured no `max` clamp, so it is covered here, and so is a step that
    declares both bounds (the side that set the final value is the one recorded)."""
    from pricing_core.rating.ladder import ladder_violations

    cap = _clamp_variant(
        {"max": "sanity_floor_minor"}, "office_premium_minor <= sanity_floor_minor",
        ["office_premium_minor", "sanity_floor_minor"],
    )
    ladder, inputs, _ = await _built(cap, **{**_CLAMP_INPUTS, "sanity_floor_minor": 1000})
    constraints = next(r for r in ladder if r.rung == "constraints")
    assert constraints.operation is not None
    assert (constraints.operation.kind, constraints.operation.bound) == ("clamp", "max")
    assert constraints.value_minor == 1000
    assert ladder_violations(ladder, inputs) == []

    both = _clamp_variant(
        {"min": "min_premium_minor", "max": "sanity_floor_minor"},
        "office_premium_minor >= min_premium_minor",
        ["office_premium_minor", "min_premium_minor", "sanity_floor_minor"],
    )
    ladder, inputs, _ = await _built(both, **{**_CLAMP_INPUTS, "sanity_floor_minor": 1000})
    constraints = next(r for r in ladder if r.rung == "constraints")
    assert constraints.operation is not None
    assert (constraints.operation.kind, constraints.operation.bound) == ("clamp", "max")
    assert ladder_violations(ladder, inputs) == []


@pytest.mark.req("FR-247")
async def test_a_disposition_that_disagrees_with_the_comparison_fails_r0() -> None:
    """W-a: the authored condition says the quote is fine while the bound binds. The ladder
    records `applied` from the disposition and the operation from the comparison, and R0
    fails: the platform cannot say which one priced the quote."""
    from pricing_core.rating.ladder import ladder_violations

    always_ok = _clamp_variant(
        {"min": "min_premium_minor"}, "office_premium_minor >= 0",
        ["office_premium_minor", "min_premium_minor"],
    )
    ladder, inputs, _ = await _built(always_ok, **_CLAMP_INPUTS)
    violations = ladder_violations(ladder, inputs)
    assert any("disagree" in v for v in violations), violations

    never_ok = _clamp_variant(
        {"min": "min_premium_minor"}, "office_premium_minor < 0",
        ["office_premium_minor", "min_premium_minor"],
    )
    ladder, inputs, _ = await _built(never_ok, **{**_CLAMP_INPUTS, "min_premium_minor": 0})
    assert any("disagree" in v for v in ladder_violations(ladder, inputs))


# ---------------------------------------------------------------------------
# RL-1329 §4 (C2, S6) / Acceptance 13: served outputs, exact and rounded once.
# ---------------------------------------------------------------------------


def _assert_clamped_output_is_the_bound(outputs: dict[str, Any]) -> None:
    assert outputs["office_premium_minor"] == 5000  # the bound, not the office rung's 1436


@pytest.mark.req("FR-273")
async def test_a_clamped_declared_output_serves_the_bound() -> None:
    bundle = await _compile_payload(_score_fixture(outputs=("office_premium_minor",)))
    result = await score_one(bundle, _context(**_CLAMP_INPUTS))
    _assert_clamped_output_is_the_bound(result.outputs)
    assert isinstance(result.outputs["office_premium_minor"], int)


@pytest.mark.req("FR-273")
async def test_serving_the_rungs_value_instead_would_be_caught(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RL-1329 Acceptance 13: the clamped case is green today, so its red is against a planted
    mutation: a `_build_outputs` that serves the rung's `value_minor` gives 1436."""
    from pricing_core.rating import score as score_module

    real = score_module._build_outputs

    def serves_the_rung(algorithm: Any, result: Any) -> dict[str, Any]:
        outputs = real(algorithm, result)
        ladder_inputs = score_module._ladder_inputs(algorithm, result, ["MIN_PREMIUM_APPLIED"])
        outputs["office_premium_minor"] = score_module.round_once(
            ladder_inputs.exact["office_premium"], ladder_inputs.rounding["office_premium"]
        )
        return outputs

    monkeypatch.setattr(score_module, "_build_outputs", serves_the_rung)
    bundle = await _compile_payload(_score_fixture(outputs=("office_premium_minor",)))
    result = await score_one(bundle, _context(**_CLAMP_INPUTS))
    assert result.outputs["office_premium_minor"] == 1436
    with pytest.raises(AssertionError):
        _assert_clamped_output_is_the_bound(result.outputs)


@pytest.mark.req("FR-273")
async def test_an_unclamped_declared_output_equals_its_rungs_value() -> None:
    """Red on `origin/main`: office 67357 against the exact 67358, and FD-1336's served-output
    case (a scratch algorithm declaring `instalment_loading_minor`): 69399 against 69402."""
    payload = _chain_algorithm(
        factors=[
            ("office_premium", "{prev} * 1.1", "half_even"),
            ("instalment_loading", "{prev} + 3401.56", "half_even"),
        ],
        extra_outputs=("office_premium_minor", "instalment_loading_minor"),
    )
    result = await score_one(await _compile_payload(payload), _context(risk_premium_minor=60000.4))
    ladder = {r.rung: r.value_minor for r in result.premium_ladder}
    assert result.outputs["instalment_loading_minor"] == ladder["instalment_loading"] == 69402
    assert result.outputs["office_premium_minor"] == ladder["office_premium"] == 66000

    chain = _chain_algorithm(
        factors=[
            ("office_premium", "{prev} * 1.1", "half_even"),
            ("instalment_loading", "{prev} * 1.05", "half_even"),
        ],
        extra_outputs=("office_premium_minor",),
    )
    scored = await score_one(await _compile_payload(chain), _context(risk_premium_minor=61234.5))
    assert scored.outputs["office_premium_minor"] == 67358  # today 67357


@pytest.mark.req("FR-273")
async def test_outputs_are_built_from_the_exact_string_not_the_float() -> None:
    from pricing_core.rating import score as score_module

    payload = _chain_algorithm(
        factors=[("office_premium", "{prev} * 1.1", "half_even")],
        extra_outputs=("office_premium_minor",),
    )
    bundle = await _compile_payload(payload)
    # the float says 1.0, the engine's exact string says 70725.8475: the string governs
    result = {
        "office_premium_minor": 1.0, "__exact__office_premium_minor": "70725.8475",
        "risk_premium_minor": 1.0, "__exact__risk_premium_minor": "100",
    }
    outputs = score_module._build_outputs(bundle.algorithm, result)
    assert outputs["office_premium_minor"] == 70726


@pytest.mark.req("FR-273")
async def test_a_non_rung_money_minor_output_is_an_integer_from_the_exact_string() -> None:
    """S6: red first because today it is the float from `result`. A JSON type change
    (number with a fraction -> integer), named in the release-note line."""
    payload = _chain_algorithm(
        factors=[("office_premium", "{prev} * 1.1", "half_even")],
        extra_outputs=("loaded_extra_minor",),
    )
    payload["steps"].insert(-1, {
        "step_id": "s_extra", "type": "expression", "label": "extra",
        "expr": "office_premium_minor * 1.0137", "result_type": "money_minor",
        "consumes": ["office_premium_minor"], "produces": "extra_value",
    })
    payload["steps"].insert(-1, _out("s_out_extra", "loaded_extra_minor", "extra_value"))
    result = await score_one(await _compile_payload(payload), _context(risk_premium_minor=61234.5))
    value = result.outputs["loaded_extra_minor"]
    assert isinstance(value, int)
    assert not isinstance(value, bool)
    assert value == 68281  # 61234.5 * 1.1 * 1.0137 = 68280.7..., rounded once


async def _near_tie_fee_result(monkeypatch: pytest.MonkeyPatch | None = None) -> Any:
    """`fee_minor`, a declared non-rung `money_minor` output whose source is, in the engine,
    exactly `1234.50000000000000012345` (`RL-1329` part 1): half_even, dp 0."""
    if monkeypatch is not None:  # the planted float path: `_build_outputs` reads `result[name]`
        from pricing_core.rating import score as score_module

        monkeypatch.setattr(score_module, "_exact", lambda result, name: None)
    payload = _chain_algorithm(
        factors=[("office_premium", "{prev} * 1.1", "half_even")], extra_outputs=("fee_minor",)
    )
    payload["steps"].insert(-1, {
        "step_id": "s_fee", "type": "expression", "label": "fee",
        "expr": "risk_premium_minor + 0.5000000000000000001", "result_type": "money_minor",
        "consumes": ["risk_premium_minor"], "produces": "fee_value",
    })
    payload["steps"].insert(-1, _out("s_out_fee", "fee_minor", "fee_value"))
    return await score_one(await _compile_payload(payload), _context(risk_premium_minor=1234))


def _assert_the_fee_is_the_integer_1235(result: Any) -> None:
    value = result.outputs["fee_minor"]
    assert type(value) is int
    assert value == 1235  # 1234.5000000000000001 rounded once; the float 1234.5 gives 1234
    assert '"fee_minor":1235' in result.model_dump_json()


@pytest.mark.req("FR-273")
async def test_a_near_tie_non_rung_money_minor_output_is_the_integer_1235() -> None:
    """PL-1348 Acceptance 7 (R2): the exact string rounded once, as an integer."""
    _assert_the_fee_is_the_integer_1235(await _near_tie_fee_result())


@pytest.mark.req("FR-273")
async def test_the_float_path_fails_the_near_tie_fee_case(monkeypatch: pytest.MonkeyPatch) -> None:
    """Red first, by planting the float path: the value is the float 1234.5."""
    result = await _near_tie_fee_result(monkeypatch)
    assert result.outputs["fee_minor"] == 1234.5
    assert type(result.outputs["fee_minor"]) is float
    with pytest.raises(AssertionError):
        _assert_the_fee_is_the_integer_1235(result)


@pytest.mark.req("FR-273")
async def test_a_decimal_output_is_served_exactly_as_before_rl_1343() -> None:
    """`RL-1343` items 2 and 3, which bind this slice because it carries the `_build_outputs`
    change: a declared non-rung `decimal` output keeps its value and its JSON type (a number).
    Green on the base and after. It is red if `_build_outputs` served the `string()` read."""
    payload = _chain_algorithm(factors=[("office_premium", "{prev} * 1.1", "half_even")])
    payload["outputs"].append({"name": "loaded_ratio", "type": "decimal", "required": True})
    payload["steps"].insert(-1, {
        "step_id": "s_ratio", "type": "expression", "label": "ratio",
        "expr": "office_premium_minor * 1.0137", "result_type": "decimal",
        "consumes": ["office_premium_minor"], "produces": "ratio_value",
    })
    payload["steps"].insert(-1, _out("s_out_ratio", "loaded_ratio", "ratio_value"))
    result = await score_one(await _compile_payload(payload), _context(risk_premium_minor=61234.5))
    value = result.outputs["loaded_ratio"]
    assert isinstance(value, float)  # a JSON number, never the exact string and never an int
    assert value == pytest.approx(68280.7, abs=1)
    assert json.loads(result.model_dump_json())["outputs"]["loaded_ratio"] == value


# ---------------------------------------------------------------------------
# RL-1329 Acceptance 11 (W3/W-e): the engine-precision guard the 1e-26 tolerance rests on.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-273")
def test_the_engines_precision_is_what_the_tolerance_rests_on() -> None:
    """On `zen-engine` 0.53.0 the eighth product of the `RL-1329` chain has 29 significant
    digits, `2095.3120014523377649903134154`, which differs from the exact 30-digit product
    `2095.31200145233776499031341545`. If an engine upgrade changes this, this fails and the
    10^-26 tolerance is re-ruled before the upgrade lands."""
    import json
    from importlib.metadata import version

    import zen

    factors = ["1.15", "1.131", "1.07", "0.9601", "1.05", "1.12", "1.0375", "0.985"]
    nodes: list[dict[str, Any]] = [
        {"id": "in", "type": "inputNode", "name": "in", "position": {"x": 0, "y": 0}}
    ]
    edges: list[dict[str, Any]] = []
    source, name = "in", "r"
    for index, factor in enumerate(factors):
        node_id = f"n{index}"
        nodes.append({
            "id": node_id, "type": "expressionNode", "name": node_id,
            "position": {"x": 0, "y": 0},
            "content": {
                "expressions": [
                    {"id": f"x{index}", "key": f"k{index}", "value": f"{name} * {factor}"}
                ],
                "passThrough": True,
            },
        })
        edges.append({"id": f"e{index}", "sourceId": source, "targetId": node_id, "type": "edge"})
        source, name = node_id, f"k{index}"
    nodes.append({
        "id": "exact", "type": "expressionNode", "name": "exact", "position": {"x": 0, "y": 0},
        "content": {"expressions": [{"id": "s", "key": "k7s", "value": "string(k7)"}],
                    "passThrough": True},
    })
    nodes.append({"id": "out", "type": "outputNode", "name": "out", "position": {"x": 0, "y": 0}})
    edges.append({"id": "ex", "sourceId": source, "targetId": "exact", "type": "edge"})
    edges.append({"id": "eo", "sourceId": "exact", "targetId": "out", "type": "edge"})
    decision = zen.ZenEngine().create_decision(json.dumps({"nodes": nodes, "edges": edges}))
    result = decision.evaluate({"r": 1304.837261934})["result"]

    with localcontext() as ctx:
        ctx.prec = 100
        exact = Decimal("1304.837261934")
        for factor in factors:
            exact = exact * Decimal(factor)
    assert version("zen-engine") == "0.53.0"
    assert result["k7s"] == "2095.3120014523377649903134154"
    assert format(exact, "f").rstrip("0") == "2095.31200145233776499031341545"
    assert Decimal(result["k7s"]) != exact


# ---------------------------------------------------------------------------
# RL-1329 Acceptance 10 (W-c, S1): a clamp the ladder cannot place is refused.
# ---------------------------------------------------------------------------


def _clamped_chain(*, clamp_on: str, produces: str | None = None) -> dict[str, Any]:
    """risk -> office_premium -> optimisation_adjustment -> instalment_loading, with a
    min-premium clamp consuming `clamp_on` and producing `produces` (default: the same)."""
    payload = _chain_algorithm(
        factors=[
            ("office_premium", "{prev} * 1.1", "half_even"),
            ("optimisation_adjustment", "{prev} * 0.96", "half_even"),
            ("instalment_loading", "{prev} * 1.05", "half_even"),
        ]
    )
    clamp = {
        "step_id": "s_clamp", "type": "constraint", "label": "Min premium",
        "condition": f"{clamp_on} >= 100", "on_violation": "clamp",
        "clamp_bounds": {"min": "100"}, "reason_code": "MIN_APPLIED",
        "consumes": [clamp_on], "produces": [produces or clamp_on],
    }
    target = f"s_{clamp_on.removesuffix('_minor')}"
    index = next(i for i, s in enumerate(payload["steps"]) if s["step_id"] == target)
    payload["steps"].insert(index + 1, clamp)
    return payload


@pytest.mark.req("FR-240")
@pytest.mark.parametrize(
    ("clamp_on", "produces"),
    [
        ("office_premium_minor", None),      # an earlier rung, with rungs after it
        ("instalment_loading_minor", None),  # a rung after `constraints`
    ],
)
async def test_an_unplaceable_clamp_is_refused_at_save_and_at_compile(
    clamp_on: str, produces: str | None
) -> None:
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.compile import validate_algorithm

    payload = _clamped_chain(clamp_on=clamp_on, produces=produces)
    issues = validate_algorithm(RatingAlgorithm.model_validate(payload))
    assert [i.code for i in issues if i.code == "LADDER_CLAMP_UNPLACEABLE"], issues
    with pytest.raises(ValueError, match="LADDER_CLAMP_UNPLACEABLE"):
        await _compile_payload(payload)


@pytest.mark.req("FR-240")
async def test_a_clamp_producing_a_different_name_from_the_one_it_consumes_is_refused() -> None:
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.compile import validate_algorithm

    payload = _clamped_chain(clamp_on="instalment_loading_minor", produces="clamped_value")
    # a last-rung clamp that renames: the payable now reads the renamed value
    payload["steps"][-1] = {**payload["steps"][-1], "consumes": ["clamped_value"]}
    payload["steps"].insert(-1, _out("s_out_clamped", "instalment_loading_minor", "clamped_value"))
    del payload["steps"][[s["step_id"] for s in payload["steps"]].index("s_out_instalment_loading")]
    issues = validate_algorithm(RatingAlgorithm.model_validate(payload))
    assert any(i.code == "LADDER_CLAMP_UNPLACEABLE" for i in issues), issues


@pytest.mark.req("FR-240")
async def test_the_score_fixture_clamp_still_saves_and_compiles() -> None:
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.compile import validate_algorithm

    payload = _algorithm_payload()
    assert not [
        i for i in validate_algorithm(RatingAlgorithm.model_validate(payload))
        if i.code == "LADDER_CLAMP_UNPLACEABLE"
    ]
    await _compile_payload(payload)
