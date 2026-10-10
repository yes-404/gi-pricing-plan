"""FD-1420: a `lookup` step reads the row in force as at its declared date.

FR-221 and `01` FR-69: the window is half-open, `[effective_from, effective_to)`. DP-1, DP-2
and DP-3 are decided in PL-1447.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any

import polars as pl
import pytest
from test_rating_score import _ctx, _FakeResolver, _version
from test_rating_score_batch import _ctx_to_row

from model_schema.rating import Pins
from model_schema.scoring import QuoteContext, QuoteContextOptions
from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_batch, score_one
from pricing_core.safe_error import CodedError

REF = "reference_table:area@1"
SUPERSEDED = "the superseded row's rate returned"

#: Two windows for one key: OLD until 2026-01-01 (exclusive), NEW from it, open-ended.
ROWS = [
    {
        "key": "SW1A",
        "payload": {"area_loading": "1.30"},
        "effective_from": "2020-01-01",
        "effective_to": "2026-01-01",
    },
    {
        "key": "SW1A",
        "payload": {"area_loading": "1.80"},
        "effective_from": "2026-01-01",
        "effective_to": None,
    },
]

_CONTRACT = [
    {"name": "base_minor", "type": "int", "nullable": False},
    {"name": "postcode", "type": "string", "nullable": False},
]


def _algo(
    *, as_at: str = "effective_date", contract: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    contract = contract if contract is not None else _CONTRACT
    # FR-246 (FD-1374): a lookup whose `as_at` names a declared date input reads it, so it
    # declares it and an input step produces it. The stamped `effective_date` needs neither.
    as_at_input = [
        {"step_id": f"s_in_{as_at}", "type": "input", "label": as_at, "input_name": as_at,
         "on_missing": "error", "produces": as_at}
        for c in contract
        if c["name"] == as_at and as_at not in ("effective_date", "base_minor", "postcode")
    ]
    return {
        "slug": "score-fixture",
        "version": 1,
        "input_contract": contract,
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {
                "step_id": "s_in_base",
                "type": "input",
                "label": "Base",
                "input_name": "base_minor",
                "on_missing": "error",
                "produces": "base_minor",
            },
            {
                "step_id": "s_in_pc",
                "type": "input",
                "label": "Postcode",
                "input_name": "postcode",
                "on_missing": "error",
                "produces": "postcode",
            },
            *as_at_input,
            {
                "step_id": "s_area",
                "type": "lookup",
                "label": "Area loading",
                "reference_table_ref": REF,
                "key_expr": ["postcode"],
                "as_at": as_at,
                "on_miss": "error",
                "consumes": ["postcode", *(i["produces"] for i in as_at_input)]
,
                "produces": "area_loading",
            },
            {
                "step_id": "s_expr",
                "type": "expression",
                "label": "Apply",
                "expr": "base_minor * number(area_loading)",
                "result_type": "money_minor",
                "consumes": ["base_minor", "area_loading"],
                "produces": "payable",
            },
            {
                "step_id": "s_out",
                "type": "output",
                "label": "Out",
                "output_name": "payable_premium_minor",
                "rounding": {"mode": "half_even", "dp": 0},
                "consumes": ["payable"],
            },
        ],
        "sub_graphs": [],
    }


async def _compiled(algo: dict[str, Any] | None = None) -> CompiledBundle:
    pins = {"rate_tables": [], "models": [], "reference_tables": [REF], "custom_objectives": []}
    version = _version().model_copy(update={"pins": Pins.model_validate(pins)})
    resolver = _FakeResolver()
    resolver._payloads["rating_algorithm:score-fixture@1"] = algo if algo is not None else _algo()
    resolver._payloads[REF] = {"rows": ROWS}
    return load_bundle(await compile_bundle(version, resolver))


def _quote(effective: date, *, extra_inputs: dict[str, Any] | None = None) -> QuoteContext:
    return QuoteContext.model_validate(
        {
            **_ctx().model_dump(),
            "effective_date": effective,
            "inputs": {"base_minor": 100_000, "postcode": "SW1A", **(extra_inputs or {})},
            "options": QuoteContextOptions(rating_version_ref=_ctx().options.rating_version_ref),
        }
    )


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-69")
@pytest.mark.parametrize(
    ("effective", "price"),
    [
        pytest.param(date(2020, 1, 1), 130_000, id="2020-01-01-at-from"),
        pytest.param(date(2025, 12, 31), 130_000, id="2025-12-31-before-to"),
        pytest.param(date(2026, 1, 1), 180_000, id="2026-01-01-at-from"),
        pytest.param(date(2026, 6, 1), 180_000, id="2026-06-01"),
        pytest.param(date(2099, 1, 1), 180_000, id="2099-01-01-open-ended"),
    ],
)
async def test_score_one_prices_on_the_row_in_force(effective: date, price: int) -> None:
    result = await score_one(await _compiled(), _quote(effective))
    assert result.outcome == "quoted"
    assert int(result.outputs["payable_premium_minor"]) == price, SUPERSEDED


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-255")
async def test_score_one_misses_before_every_row() -> None:
    """`2019-12-31` is before the first row's `effective_from`: no row is in force."""
    with pytest.raises(ValueError, match=r"^REFERENCE_LOOKUP_MISS:"):
        await score_one(await _compiled(), _quote(date(2019, 12, 31)))


@pytest.mark.req("FR-221")
async def test_score_batch_prices_on_the_row_in_force() -> None:
    frame = pl.DataFrame([_ctx_to_row(_quote(d)) for d in (date(2025, 6, 1), date(2026, 6, 1))])
    out = score_batch(await _compiled(), frame.lazy()).collect()
    prices = [json.loads(v)["payable_premium_minor"] for v in out["outputs_json"]]
    assert prices == [130_000, 180_000], SUPERSEDED


_DATE_INPUT = {"name": "inception", "type": "date", "nullable": False}


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-227")
async def test_as_at_naming_a_non_date_input_is_refused_at_compile() -> None:
    with pytest.raises(CodedError, match=r"^RATING_TYPE_MISMATCH:.*s_area.*postcode"):
        await _compiled(_algo(as_at="postcode"))


@pytest.mark.req("FR-221")
async def test_as_at_naming_an_undeclared_value_is_refused_at_compile() -> None:
    with pytest.raises(CodedError, match=r"^RATING_GRAPH_UNRESOLVED_REF:.*s_area.*inception"):
        await _compiled(_algo(as_at="inception"))


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-227")
async def test_a_declared_effective_date_must_be_date_typed() -> None:
    contract = [*_CONTRACT, {"name": "effective_date", "type": "string", "nullable": False}]
    with pytest.raises(CodedError, match=r"^RATING_TYPE_MISMATCH:.*s_area.*effective_date"):
        await _compiled(_algo(contract=contract))


@pytest.mark.req("FR-221")
async def test_a_date_input_named_by_as_at_selects_the_row() -> None:
    algo = _algo(as_at="inception", contract=[*_CONTRACT, _DATE_INPUT])
    ctx = _quote(date(2025, 6, 1), extra_inputs={"inception": "2026-06-01"})
    result = await score_one(await _compiled(algo), ctx)
    assert int(result.outputs["payable_premium_minor"]) == 180_000, SUPERSEDED


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-213")
@pytest.mark.req("FR-255")
@pytest.mark.parametrize(
    "raw",
    [
        "2026-01-01T00:30:00+01:00",
        "2026-01-01T00:00:00",
        "2026-1-1",
        "20260101",
        "2026-02-30",
        "nonsense",
    ],
)
async def test_a_malformed_as_at_value_is_refused_not_missed(raw: str) -> None:
    algo = _algo(as_at="inception", contract=[*_CONTRACT, _DATE_INPUT])
    compiled = await _compiled(algo)
    with pytest.raises(CodedError, match=r"^INPUT_CONTRACT_VIOLATION:.*s_area"):
        await score_one(compiled, _quote(date(2026, 6, 1), extra_inputs={"inception": raw}))


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-213")
async def test_an_input_shadowing_effective_date_is_checked() -> None:
    ctx = _quote(date(2026, 6, 1), extra_inputs={"effective_date": "2026-01-01T00:30:00+01:00"})
    with pytest.raises(CodedError, match=r"^INPUT_CONTRACT_VIOLATION:.*s_area"):
        await score_one(await _compiled(), ctx)


_SENTINEL = "SENTINEL-quote-input-as-at-5e1f"


@pytest.mark.req("NFR-499")
@pytest.mark.req("FR-221")
async def test_the_as_at_refusal_never_carries_the_value() -> None:
    algo = _algo(as_at="inception", contract=[*_CONTRACT, _DATE_INPUT])
    compiled = await _compiled(algo)
    ctx = _quote(date(2026, 6, 1), extra_inputs={"inception": _SENTINEL})
    with pytest.raises(CodedError) as caught:
        await score_one(compiled, ctx)
    assert _SENTINEL not in str(caught.value)
    assert "'s_area'" in str(caught.value)
    assert "'inception'" in str(caught.value)
    frame = pl.DataFrame([_ctx_to_row(ctx)])
    out = score_batch(compiled, frame.lazy()).collect()
    assert out["error_code"].to_list() == ["INPUT_CONTRACT_VIOLATION"]
    assert _SENTINEL not in (out["error_message"][0] or "")
