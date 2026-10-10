"""FD-1425: wiring follows dependency order, never list order (FR-212), and no side branch
carries a stale copy of a produced value into the sink.

The algorithms and values are FD-1425's own reproduction (its Evidence §2 and §3)."""

from __future__ import annotations

import copy
from typing import Any
from uuid import uuid4

import pytest
from test_rating_score import _FakeResolver, _version

from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import Bundle, ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle, to_wire
from pricing_core.rating.score import score_one

_IN = {"step_id": "s_in", "type": "input", "label": "x", "input_name": "x",
       "on_missing": "error", "produces": "x"}
_A = {"step_id": "s_a", "type": "expression", "label": "A: base = x*100",
      "expr": "x * 100", "result_type": "money_minor", "consumes": ["x"], "produces": "base"}
_B = {"step_id": "s_b", "type": "expression", "label": "B: premium = base + 50",
      "expr": "base + 50", "result_type": "money_minor", "consumes": ["base"],
      "produces": "premium"}
_D = {"step_id": "s_d", "type": "expression", "label": "D: fee = x + 1",
      "expr": "x + 1", "result_type": "money_minor", "consumes": ["x"], "produces": "fee"}
_OUT = {"step_id": "s_out", "type": "output", "label": "out", "output_name": "premium_out",
        "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["premium"]}
_OUT_FEE = {"step_id": "s_out_fee", "type": "output", "label": "fee", "output_name": "fee_out",
            "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["fee"]}


def _algo(steps: list[dict[str, Any]]) -> dict[str, Any]:
    outputs = [{"name": "premium_out", "type": "money_minor", "required": True}]
    if any(s["step_id"] == "s_out_fee" for s in steps):
        outputs.append({"name": "fee_out", "type": "money_minor", "required": True})
    return {"slug": "order-test", "version": 1,
            "input_contract": [{"name": "x", "type": "int", "nullable": False,
                                "min": 0, "max": 1000}],
            "outputs": outputs, "steps": steps, "sub_graphs": []}


def _order_version() -> RatingVersion:
    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": "order-test", "version": 1,
        "status": "draft", "dataset_version_id": str(uuid4()), "model_ref": "model:none@1",
        "created_at": "2026-08-29T12:00:00Z", "created_by": str(uuid4()),
        "updated_at": "2026-08-29T12:00:00Z",
        "algorithm_ref": "rating_algorithm:order-test@1",
        "pins": {"rate_tables": [], "models": [], "reference_tables": [],
                 "custom_objectives": []},
        "model_reference_mode": "exact"})


class _OneAlgorithm:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        return ResolvedArtifact(status="approved", payload=self._payload)


async def _bundle(steps: list[dict[str, Any]]) -> Bundle:
    return await compile_bundle(_order_version(), _OneAlgorithm(_algo(steps)))


def _permute(steps: list[dict[str, Any]], move: str, before: str) -> list[dict[str, Any]]:
    steps = list(steps)
    step = next(s for s in steps if s["step_id"] == move)
    steps.remove(step)
    at = next(i for i, s in enumerate(steps) if s["step_id"] == before)
    steps.insert(at, step)
    return steps


async def _score_fixture(*, move: str | None = None, before: str | None = None) -> CompiledBundle:
    resolver = _FakeResolver()
    key = "rating_algorithm:score-fixture@1"
    payload = copy.deepcopy(resolver._payloads[key])
    if move is not None and before is not None:
        payload["steps"] = _permute(payload["steps"], move, before)
    resolver._payloads[key] = payload
    return load_bundle(await compile_bundle(_version(), resolver))


_BASE_INPUTS: dict[str, Any] = {
    "driver_age": 34, "channel": "direct", "min_premium_minor": 0,
    "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0,
}


# --- wiring follows dependency order ----------------------------------------------------


@pytest.mark.req("FR-212")
@pytest.mark.parametrize("ctx", [{"x": 3}, {"x": 3, "base": 7}])
async def test_a_misordered_algorithm_prices_as_its_topological_twin(
    ctx: dict[str, Any],
) -> None:
    """FD-1425 Evidence §2: `[in, B, A, out]` raised a NodeError with ctx {x: 3} and gave 57
    with ctx {x: 3, base: 7}. Its topological twin gives 350."""
    compiled = load_bundle(await _bundle([_IN, _B, _A, _OUT]))
    out = await compiled.decision.async_evaluate(ctx)
    assert out["result"]["premium"] == 350


@pytest.mark.req("FR-212")
async def test_a_clamp_listed_before_its_producer_still_binds() -> None:
    """FD-1425 Evidence §3, C1: the clamp listed before `s_office` was wired to the input and
    skipped the minimum premium (payable 1507). Topological: 5250."""
    from test_rating_score import _ctx

    compiled = await _score_fixture(move="s_clamp", before="s_office")
    ctx = _ctx(inputs={**_BASE_INPUTS, "min_premium_minor": 5000})
    result = await score_one(compiled, ctx)
    assert result.outputs["payable_premium_minor"] == 5250
    rungs = {rung.rung: rung.value_minor for rung in result.premium_ladder}
    assert rungs["constraints"] == 5000


# --- pins: an ordered list wires exactly as before --------------------------------------


@pytest.mark.req("FR-212")
async def test_a_topologically_listed_algorithm_wires_exactly_as_listed() -> None:
    """The tie-break is list position. `[in, A, B, D, out, out_fee]` is topological; a FIFO
    Kahn would emit D before B (both ready after A), a heap on list position does not."""
    bundle = await _bundle([_IN, _A, _B, _D, _OUT, _OUT_FEE])
    wire = to_wire(bundle.graph, bundle.resolved_payloads)
    interior = [n["id"] for n in wire["nodes"] if n["id"] in {"s_a", "s_b", "s_d"}]
    assert interior == ["s_a", "s_b", "s_d"]
    bundle_ab = await _bundle([_IN, _A, _B, _OUT])
    edges = [(e["sourceId"], e["targetId"])
             for e in to_wire(bundle_ab.graph, bundle_ab.resolved_payloads)["edges"]]
    assert edges == [("input", "s_a"), ("s_a", "s_b"), ("s_b", "__exact_reads"),
                     ("__exact_reads", "output")]


#: Recorded at the slice's base commit, before any code change (two runs, equal).
#: Re-recorded 2026-10-10 (FD-1374, RL-1519): was sha256:86abdb81…039073d; the fixture graph gained
#: its FR-246 declarations (consumes, input steps), so its content hash moved; no price changed.
_SCORE_FIXTURE_HASH = "sha256:6458c7c80627d20602a8d82821a80e3fb7500c75c1d3bf9bc1033ba74f7a918e"


@pytest.mark.req("FR-212")
async def test_the_bundle_hash_is_unchanged() -> None:
    """The ruling: "a test asserts the hash of a topologically listed algorithm is unchanged"."""
    resolver = _FakeResolver()
    bundle = await compile_bundle(_version(), resolver)
    assert bundle.content_hash == _SCORE_FIXTURE_HASH


# --- (R-b): one ordered path, no stale copy through the sink ------------------------------


@pytest.mark.req("FR-212")
async def test_no_side_branch_carries_a_stale_copy_into_the_sink() -> None:
    """(R-b): the score fixture, correctly ordered, evaluated at the engine with a raw
    `instalment_loading_minor`. Through the sink fan-in the last branch's stale copy won; on
    one ordered path the producer's value is the last write."""
    compiled = await _score_fixture()
    context = {"effective_date": "2026-09-01", "purpose": "new_business",
               **_BASE_INPUTS, "min_premium_minor": 5000, "instalment_loading_minor": 777}
    out = await compiled.decision.async_evaluate(context)
    assert out["result"]["instalment_loading_minor"] == 5250


@pytest.mark.req("FR-212")
@pytest.mark.parametrize("instalment_early", [True, False])
async def test_the_r5_reorder_pair_prices_alike(instalment_early: bool) -> None:
    """auditor-premise r5: with a raw `instalment_loading_minor`, `s_instalment` moved before
    the decline steps gave 5250, and listed after them (the fixture's order) gave 777."""
    compiled = await (
        _score_fixture(move="s_instalment", before="s_decl_cap") if instalment_early
        else _score_fixture()
    )
    context = {"effective_date": "2026-09-01", "purpose": "new_business",
               **_BASE_INPUTS, "min_premium_minor": 5000, "instalment_loading_minor": 777}
    out = await compiled.decision.async_evaluate(context)
    assert out["result"]["instalment_loading_minor"] == 5250


# Limit (ii): no ladder. `base` is clamped up to a declared `floor`, and the output reads
# `base` itself, so no rung reconciliation can refuse a stale value.
_NL_IN_X = {"step_id": "s_in_x", "type": "input", "label": "x", "input_name": "x",
            "on_missing": "error", "produces": "x"}
_NL_IN_F = {"step_id": "s_in_f", "type": "input", "label": "floor", "input_name": "floor",
            "on_missing": "error", "produces": "floor"}
_NL_A = {"step_id": "s_a", "type": "expression", "label": "base = x*100", "expr": "x * 100",
         "result_type": "money_minor", "consumes": ["x"], "produces": "base"}
_NL_CLAMP = {"step_id": "s_clamp", "type": "constraint", "label": "Floor",
             "condition": "base >= floor", "on_violation": "clamp",
             "clamp_bounds": {"min": "floor"}, "reason_code": "FLOOR",
             "consumes": ["base", "floor"], "produces": ["base"]}
_NL_OUT = {"step_id": "s_out", "type": "output", "label": "out", "output_name": "base_out",
           "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["base"]}
# Limit (i): produce-nothing or terminal side branches other than a decline constraint.
_NL_SIDE = {
    "decline": {"step_id": "s_side", "type": "constraint", "label": "Cap",
                "condition": "base <= 100000", "on_violation": "decline",
                "reason_code": "CAP", "consumes": ["base"]},
    "error": {"step_id": "s_side", "type": "constraint", "label": "Cap",
              "condition": "base <= 100000", "on_violation": "error",
              "reason_code": "CAP", "consumes": ["base"]},
    "terminal_expression": {"step_id": "s_side", "type": "expression", "label": "Tap",
                            "expr": "base + 0", "result_type": "money_minor",
                            "consumes": ["base"], "produces": "tap"},
}


def _no_ladder(side: dict[str, Any], side_first: bool) -> dict[str, Any]:
    middle = [side, _NL_CLAMP] if side_first else [_NL_CLAMP, side]
    return {"slug": "order-test", "version": 1,
            "input_contract": [{"name": "x", "type": "int", "nullable": False, "min": 0,
                                "max": 1000},
                               {"name": "floor", "type": "int", "nullable": False}],
            "outputs": [{"name": "base_out", "type": "money_minor", "required": True}],
            "steps": [_NL_IN_X, _NL_IN_F, _NL_A, *middle, _NL_OUT], "sub_graphs": []}


@pytest.mark.req("FR-212")
@pytest.mark.parametrize("kind", ["decline", "error", "terminal_expression"])
@pytest.mark.parametrize("side_first", [True, False])
async def test_no_ladder_side_branch_never_carries_the_pre_clamp_value(
    kind: str, side_first: bool
) -> None:
    """auditor-fanin's limits: other produce-nothing kinds, and no ladder backstop. With no
    caller key, the clamped value (5000) reaches the result whatever the list order."""
    compiled = load_bundle(await compile_bundle(
        _order_version(), _OneAlgorithm(_no_ladder(_NL_SIDE[kind], side_first))))
    out = await compiled.decision.async_evaluate({"x": 3, "floor": 5000})
    assert out["result"]["base"] == 5000
