"""FR-237 "Nothing is unpinned" (WK-1178 fix slice, PL-1299; FD-1297, RL-1298).

`compile_bundle` refuses a `table`, `lookup` or `model_call` step whose ref the version's pins
do not carry at that exact version, with `RATING_VERSION_UNPINNED`. `load_bundle` re-checks the
same rule for a bundle not produced by the fixed `compile_bundle`, and the model path's missing
payload is a coded refusal, not a bare `KeyError`.

Every priced case uses the `??` consumer only (`coalesce(` is refused at compile, so it is not
a case here). Fixtures are built by copying the score fixture's dicts, never mutating its helpers.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest
from test_rating_runtime import _rate_table_payload
from test_rating_score import _algorithm_payload, _ctx, _FakeResolver, _version

from model_schema.rating import Pins, RatingAlgorithm, RatingVersion
from model_schema.scoring import QuoteContext, QuoteContextOptions
from pricing_core.rating.compile import (
    Bundle,
    bundle_hash,
    compile_bundle,
    to_jdm,
)
from pricing_core.rating.runtime import load_bundle
from pricing_core.rating.score import score_one
from pricing_core.safe_error import CodedError

# ---------------------------------------------------------------------------
# Fixture builders (copies of the score fixture; the shared helpers are not mutated).
# ---------------------------------------------------------------------------

_TOLERANT_TABLE_EXPR = "risk_premium_minor * (expense_factor ?? 1.0)"
#: A lookup's output is always a string, so arithmetic on it goes through `number()`
#: (FR-244 as corrected by RL-1322).
_TOLERANT_LOOKUP_EXPR = "risk_premium_minor * number(expense_factor ?? '1.0')"


def _step(algo: dict[str, Any], step_id: str) -> dict[str, Any]:
    return next(s for s in algo["steps"] if s["step_id"] == step_id)


def _table_algo(*, table_ref: str = "rate_table:motor-expense@1") -> dict[str, Any]:
    """FD-1297 "Table step through a tolerant consumer": on_miss=default and a `??` consumer."""
    algo = copy.deepcopy(_algorithm_payload())
    step = _step(algo, "s_expense")
    step["rate_table_ref"] = table_ref
    step["on_miss"] = "default"
    _step(algo, "s_office")["expr"] = _TOLERANT_TABLE_EXPR
    return algo


def _lookup_algo(*, ref: str = "reference_table:expense@1") -> dict[str, Any]:
    """FD-1297 Table 2: the table step replaced by a lookup, with a `??` consumer."""
    algo = copy.deepcopy(_algorithm_payload())
    algo["steps"] = [
        {"step_id": "s_expense", "type": "lookup", "label": "Expense factor",
         "reference_table_ref": ref, "key_expr": ["channel"], "as_at": "effective_date",
         "on_miss": "default", "consumes": ["channel"], "produces": "expense_factor"}
        if s["step_id"] == "s_expense" else s
        for s in algo["steps"]
    ]
    _step(algo, "s_office")["expr"] = _TOLERANT_LOOKUP_EXPR
    return algo


def _ref_table_payload(direct: str, broker: str) -> dict[str, Any]:
    def row(key: str, factor: str) -> dict[str, Any]:
        return {"key": key, "payload": {"expense_factor": factor},
                "effective_from": "2020-01-01", "effective_to": None}

    return {"rows": [row("direct", direct), row("broker", broker)]}


def _rate_table_v2() -> dict[str, Any]:
    payload = _rate_table_payload()
    payload["version"] = 2
    payload["rows"] = [
        {"channel": "direct", "expense_factor": "2.0"},
        {"channel": "broker", "expense_factor": "2.5"},
    ]
    return payload


def _resolver(extra: dict[str, dict[str, Any]], algo: dict[str, Any]) -> _FakeResolver:
    resolver = _FakeResolver()
    resolver._payloads["rating_algorithm:score-fixture@1"] = algo
    resolver._payloads.update(extra)
    return resolver


def _with_pins(
    *, rate_tables: list[str], reference_tables: list[str], models: list[str] | None = None
) -> RatingVersion:
    return _version().model_copy(update={"pins": Pins.model_validate({
        "rate_tables": rate_tables,
        "models": models if models is not None else ["model:motor-freq@1"],
        "reference_tables": reference_tables,
        "custom_objectives": [],
    })})


_EXTRA = {
    "rate_table:motor-expense@2": _rate_table_v2(),
    "reference_table:expense@1": _ref_table_payload("1.1", "1.25"),
    "reference_table:expense@2": _ref_table_payload("2.0", "2.5"),
}


async def _price(version: RatingVersion, algo: dict[str, Any]) -> int:
    bundle = await compile_bundle(version, _resolver(_EXTRA, algo))
    result = await score_one(load_bundle(bundle), _ctx())
    assert result.outcome == "quoted"
    return int(result.outputs["payable_premium_minor"])


# ---------------------------------------------------------------------------
# Acceptance 2: one refusal per kind, unpinned and wrong-version.
# ---------------------------------------------------------------------------

_CASES: dict[str, tuple[dict[str, Any], RatingVersion, str]] = {}


def _cases() -> dict[str, tuple[dict[str, Any], RatingVersion, str]]:
    if _CASES:
        return _CASES
    peril = _algorithm_payload()
    _step(peril, "s_risk").pop("model_ref")
    _step(peril, "s_risk")["peril_structure_ref"] = "peril_structure:motor-gb@1"
    _CASES.update({
        "table_absent": (
            _algorithm_payload(), _with_pins(rate_tables=[], reference_tables=[]),
            "rate_table:motor-expense@1"),
        "table_wrong_version": (
            _algorithm_payload(),
            _with_pins(rate_tables=["rate_table:motor-expense@2"], reference_tables=[]),
            "rate_table:motor-expense@1"),
        "lookup_absent": (
            _lookup_algo(), _with_pins(rate_tables=[], reference_tables=[]),
            "reference_table:expense@1"),
        "lookup_wrong_version": (
            _lookup_algo(),
            _with_pins(rate_tables=[], reference_tables=["reference_table:expense@2"]),
            "reference_table:expense@1"),
        "model_absent": (
            _algorithm_payload(),
            _with_pins(rate_tables=["rate_table:motor-expense@1"], reference_tables=[],
                       models=[]),
            "model:motor-freq@1"),
        "model_wrong_version": (
            _algorithm_payload(),
            _with_pins(rate_tables=["rate_table:motor-expense@1"], reference_tables=[],
                       models=["model:motor-freq@2"]),
            "model:motor-freq@1"),
        "peril_structure_absent": (
            peril,
            _with_pins(rate_tables=["rate_table:motor-expense@1"], reference_tables=[],
                       models=[]),
            "peril_structure:motor-gb@1"),
    })
    return _CASES


@pytest.mark.req("FR-237")
@pytest.mark.parametrize("case", [
    "table_absent", "table_wrong_version", "lookup_absent", "lookup_wrong_version",
    "model_absent", "model_wrong_version", "peril_structure_absent",
])
async def test_a_step_ref_not_pinned_at_its_exact_version_is_refused_at_compile(case: str) -> None:
    algo, version, ref = _cases()[case]
    resolver = _resolver({**_EXTRA, "model:motor-freq@2": _FakeResolver()._payloads[
        "model:motor-freq@1"]}, algo)
    with pytest.raises(CodedError, match=r"^RATING_VERSION_UNPINNED:") as raised:
        await compile_bundle(version, resolver)
    text = str(raised.value)
    assert ref in text
    step_id = "s_risk" if "model" in case or "peril" in case else "s_expense"
    assert step_id in text


# ---------------------------------------------------------------------------
# Acceptance 3 and 4: the `??` consumer cases that priced wrong, and their controls.
# ---------------------------------------------------------------------------

_TABLE_1 = ["rate_table:motor-expense@1"]
_TABLE_2 = ["rate_table:motor-expense@2"]
_LOOKUP_1 = ["reference_table:expense@1"]
_LOOKUP_2 = ["reference_table:expense@2"]


@pytest.mark.req("FR-237")
@pytest.mark.parametrize(("algo_factory", "pinned_tables", "pinned_lookups"), [
    pytest.param(_table_algo, [], [], id="table_unpinned"),
    pytest.param(_lookup_algo, [], [], id="lookup_unpinned"),
    pytest.param(_lookup_algo, [], _LOOKUP_2, id="lookup_step_1_pin_2"),
])
async def test_a_tolerant_consumer_no_longer_prices_an_unpinned_step(
    algo_factory: Any, pinned_tables: list[str], pinned_lookups: list[str]
) -> None:
    version = _with_pins(rate_tables=pinned_tables, reference_tables=pinned_lookups)
    with pytest.raises(CodedError, match=r"^RATING_VERSION_UNPINNED:"):
        await _price(version, algo_factory())


@pytest.mark.req("FR-237")
@pytest.mark.parametrize(("algo_factory", "pinned_tables", "pinned_lookups", "price"), [
    pytest.param(_table_algo, _TABLE_1, [], 1_507, id="table_1_1"),
    pytest.param(lambda: _table_algo(table_ref="rate_table:motor-expense@2"),
                 _TABLE_2, [], 2_740, id="table_2_2"),
    pytest.param(_table_algo, _TABLE_1 + _TABLE_2, [], 1_507, id="table_extra_pin_allowed"),
    pytest.param(_lookup_algo, [], _LOOKUP_1, 1_507, id="lookup_1_1"),
    pytest.param(lambda: _lookup_algo(ref="reference_table:expense@2"),
                 [], _LOOKUP_2, 2_740, id="lookup_2_2"),
])
async def test_a_correctly_pinned_tolerant_consumer_still_prices(
    algo_factory: Any, pinned_tables: list[str], pinned_lookups: list[str], price: int
) -> None:
    version = _with_pins(rate_tables=pinned_tables, reference_tables=pinned_lookups)
    assert await _price(version, algo_factory()) == price


# auditor-933's cases: FD-1297 Table 3, base 100000 and a 1.30 / 1.80 relativity.


def _veh_algo(kind: str, ref: str) -> dict[str, Any]:
    if kind == "lookup":
        step = {"step_id": "s_veh", "type": "lookup", "label": "Vehicle loading",
                "reference_table_ref": ref, "key_expr": ["veh"], "as_at": "effective_date",
                "on_miss": "default", "consumes": ["veh"], "produces": "veh_loading"}
        expr = "base_minor * number(veh_loading ?? '1.0')"
        produced = "veh_loading"
    else:
        step = {"step_id": "s_veh", "type": "table", "label": "Vehicle factor",
                "rate_table_ref": ref, "key_expr": ["veh"], "on_miss": "default",
                "consumes": ["veh"], "produces": "veh_factor"}
        expr = "base_minor * (veh_factor ?? 1.0)"
        produced = "veh_factor"
    return {
        "slug": "score-fixture", "version": 1,
        "input_contract": [
            {"name": "base_minor", "type": "int", "nullable": False},
            {"name": "veh", "type": "enum", "domain": ["x"], "nullable": False},
        ],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in_base", "type": "input", "label": "Base", "input_name": "base_minor",
             "on_missing": "error", "produces": "base_minor"},
            {"step_id": "s_in_veh", "type": "input", "label": "Veh", "input_name": "veh",
             "on_missing": "error", "produces": "veh"},
            step,
            {"step_id": "s_expr", "type": "expression", "label": "Apply", "expr": expr,
             "result_type": "money_minor", "consumes": ["base_minor", produced],
             "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }


def _veh_payloads() -> dict[str, dict[str, Any]]:
    def rate(version: int, factor: str) -> dict[str, Any]:
        return {"slug": "veh", "version": version, "rateable": True, "storage": "rows",
                "keys": [{"name": "veh", "type": "string", "banding_ref": None}],
                "value": {"name": "veh_factor", "type": "relativity", "unit": "factor",
                          "min": None, "max": None},
                "default_row": None, "rows": [{"veh": "x", "veh_factor": factor}]}

    def ref(loading: str) -> dict[str, Any]:
        return {"rows": [{"key": "x", "payload": {"veh_loading": loading},
                          "effective_from": "2020-01-01", "effective_to": None}]}

    return {
        "rate_table:veh@1": rate(1, "1.30"), "rate_table:veh@2": rate(2, "1.80"),
        "reference_table:veh@1": ref("1.30"), "reference_table:veh@2": ref("1.80"),
    }


async def _veh_price(kind: str, step_ref: str, pin: str | None) -> int:
    pins = {"rate_tables": [], "models": [], "reference_tables": [], "custom_objectives": []}
    if pin is not None:
        pins["rate_tables" if kind == "table" else "reference_tables"].append(pin)
    version = _version().model_copy(update={"pins": Pins.model_validate(pins)})
    resolver = _FakeResolver()
    resolver._payloads["rating_algorithm:score-fixture@1"] = _veh_algo(kind, step_ref)
    resolver._payloads.update(_veh_payloads())
    bundle = await compile_bundle(version, resolver)
    ctx = QuoteContext.model_validate({
        **_ctx().model_dump(), "inputs": {"base_minor": 100_000, "veh": "x"},
        "options": QuoteContextOptions(rating_version_ref=_ctx().options.rating_version_ref),
    })
    result = await score_one(load_bundle(bundle), ctx)
    assert result.outcome == "quoted"
    return int(result.outputs["payable_premium_minor"])


@pytest.mark.req("FR-237")
@pytest.mark.parametrize(("kind", "pin"), [
    pytest.param("lookup", None, id="lookup_unpinned"),
    pytest.param("table", None, id="table_unpinned"),
])
async def test_auditor_933_unpinned_cases_are_refused(kind: str, pin: str | None) -> None:
    with pytest.raises(CodedError, match=r"^RATING_VERSION_UNPINNED:"):
        await _veh_price(kind, f"{'reference' if kind == 'lookup' else 'rate'}_table:veh@1", pin)


@pytest.mark.req("FR-237")
@pytest.mark.parametrize(("kind", "version_no", "price"), [
    ("lookup", 1, 130_000), ("table", 1, 130_000), ("lookup", 2, 180_000), ("table", 2, 180_000),
])
async def test_auditor_933_controls_price(kind: str, version_no: int, price: int) -> None:
    ref = f"{'reference' if kind == 'lookup' else 'rate'}_table:veh@{version_no}"
    assert await _veh_price(kind, ref, ref) == price


# ---------------------------------------------------------------------------
# Acceptance 5 and 5a: hand-built bundles at load (DP-F2 (c), RL-1298).
# ---------------------------------------------------------------------------


def _hand_bundle(*, glm: bool, pins: dict[str, list[str]], carry: list[str]) -> Bundle:
    """A pre-fix bundle built without `compile_bundle`: the algorithm plus only `carry`."""
    fake = _FakeResolver(glm=glm)
    algo_payload = fake._payloads["rating_algorithm:score-fixture@1"]
    algo_payload = copy.deepcopy(algo_payload)
    _step(algo_payload, "s_expense")["on_miss"] = "default"
    _step(algo_payload, "s_office")["expr"] = _TOLERANT_TABLE_EXPR
    algo = RatingAlgorithm.model_validate(algo_payload)
    pinned = Pins.model_validate({"reference_tables": [], "custom_objectives": [], **pins})
    graph = to_jdm(algo)
    payloads = {"rating_algorithm:score-fixture@1": algo_payload}
    payloads.update({ref: fake._payloads[ref] for ref in carry})
    return Bundle(
        algorithm_ref="rating_algorithm:score-fixture@1", graph=graph,
        resolved_payloads=payloads, pins=pinned, content_hash=bundle_hash(graph, pinned),
        compiled_at=_ctx().quoted_at,
    )


@pytest.mark.req("FR-237")
@pytest.mark.parametrize(("glm", "model"), [
    pytest.param(False, "model:motor-freq@1", id="gbm"),
    pytest.param(True, "model:motor-freq-glm@1", id="glm"),
])
def test_a_pinned_model_missing_from_the_payloads_is_a_coded_refusal_at_load(
    glm: bool, model: str
) -> None:
    bundle = _hand_bundle(
        glm=glm, pins={"rate_tables": _TABLE_1, "models": [model]}, carry=_TABLE_1)
    with pytest.raises(CodedError, match=r"^RATING_VERSION_UNPINNED:") as raised:
        load_bundle(bundle)
    assert model in str(raised.value)
    assert "s_risk" in str(raised.value)


@pytest.mark.req("FR-237")
async def test_a_hand_built_bundle_pinning_its_table_loads_and_prices() -> None:
    bundle = _hand_bundle(
        glm=False, pins={"rate_tables": _TABLE_1, "models": ["model:motor-freq@1"]},
        carry=[*_TABLE_1, "model:motor-freq@1"])
    result = await score_one(load_bundle(bundle), _ctx())
    assert result.outputs["payable_premium_minor"] == 1_507


@pytest.mark.req("FR-237")
@pytest.mark.parametrize("pinned", [
    pytest.param([], id="unpinned"),
    pytest.param(_TABLE_2, id="step_1_pin_2"),
])
def test_a_pre_fix_bundle_with_an_unpinned_table_is_refused_at_load(pinned: list[str]) -> None:
    bundle = _hand_bundle(
        glm=False, pins={"rate_tables": pinned, "models": ["model:motor-freq@1"]},
        carry=["model:motor-freq@1"])
    if pinned:  # a pin at @2 has its @2 payload resolved, as compile would have done
        bundle = bundle.model_copy(update={"resolved_payloads": {
            **bundle.resolved_payloads, "rate_table:motor-expense@2": _rate_table_v2()}})
    with pytest.raises(CodedError, match=r"^RATING_VERSION_UNPINNED:"):
        load_bundle(bundle)
