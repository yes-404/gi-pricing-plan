"""FD-1610 limb 2 (PL-1927 S2): a `model_call` key the runtime drops is traced (d), then refused.

`runtime._model_call_handler` builds the model's feature row from the `feature_map` keys found in
the scoring context and silently skips the rest (`runtime.py:758-762` at `102341aa`). The
maintainer's (by delegation) entry "2026-10-25 11:40:12 GMT" rules (d) then (c), in one slice:
"every `feature_map` key the runtime drops ... is recorded in the trace as an additive field; price
and hash unchanged (FR-239 holds by construction). Then (c): a dropped key that feeds a **required**
model input raises a coded, input-free scoring error". Its entry "2026-10-25 11:53:23 GMT" (DP-S2
(i)/(i)/(i)) names them: the field is `TraceStep.dropped_inputs: list[str] | None` on the
model-schema type, the refusal a new `MODEL_CALL_REQUIRED_INPUT_ABSENT` surfaced through
`_model_call_failure`. PL-1927's Acceptance 12 ((d) red) and 15 ((c) red, both cases).

The bundles here are built as a pre-SL-1541 bundle was: compiled normally, then the stored
algorithm payload's `feature_map` is rewritten, because `compile_bundle`'s FR-240 coverage check
(`check_model_call_coverage`) refuses an unmapped required input and these bundles must reach the
runtime.

UNRUN draft (gate-1 held): each test's docstring states the red mode expected at `102341aa`.
"""

from __future__ import annotations

from typing import Any

import pytest
from test_rating_score import _compiled, _ctx, _FakeResolver, _version

from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_one

_ABSENT = "MODEL_CALL_REQUIRED_INPUT_ABSENT"
_STRAY = "stray_key"
# A value no message or code should contain by accident (NFR-499 probe).
_AGE = 47


async def _compiled_with_feature_map(feature_map: dict[str, str]) -> CompiledBundle:
    """A bundle whose `s_risk` step carries `feature_map` as stored, bypassing compile's check."""
    bundle = await compile_bundle(_version(), _FakeResolver())
    algorithm = bundle.resolved_payloads[bundle.algorithm_ref]
    step: dict[str, Any] = next(s for s in algorithm["steps"] if s["step_id"] == "s_risk")
    step["feature_map"] = feature_map
    return load_bundle(bundle)


def _risk_step(result: Any) -> Any:
    assert result.trace is not None
    return next(s for s in result.trace.steps if s.step_id == "s_risk")


@pytest.mark.req("FR-222")
async def test_a_dropped_key_that_feeds_no_required_input_is_traced() -> None:
    """(d) red — PL-1927 Acceptance 12. A `feature_map` key no step produces, beside the one
    that maps the model's only input, is dropped by the runtime.

    RED at `102341aa`: `AttributeError: 'TraceStep' object has no attribute 'dropped_inputs'`
    (the field does not exist yet). After (d): the step lists exactly that key."""
    compiled = await _compiled_with_feature_map({"driver_age": "age_years", _STRAY: "unused_slug"})
    result = await score_one(compiled, _ctx(), trace=True)
    assert _risk_step(result).dropped_inputs == [_STRAY]


@pytest.mark.req("FR-222")
@pytest.mark.req("FR-239")
async def test_tracing_a_dropped_key_changes_neither_price_nor_hash() -> None:
    """(d) no reprice, and the (c)/(d) boundary — Acceptance 12 and 15's last sentence. A dropped
    key that feeds NO required input still scores, at the price of the same bundle without it.

    RED at `102341aa`: the price assertions pass (the base drops it silently); the test fails
    on `.dropped_inputs` with the same `AttributeError` as the test above. The `content_hash`
    assertion is the by-construction hold of FR-239, not a red."""
    clean = await _compiled()
    stray = await _compiled_with_feature_map({"driver_age": "age_years", _STRAY: "unused_slug"})
    priced_clean = await score_one(clean, _ctx(), trace=True)
    priced_stray = await score_one(stray, _ctx(), trace=True)

    assert priced_stray.outcome == "quoted"
    assert priced_stray.outputs == priced_clean.outputs
    assert priced_stray.premium_ladder == priced_clean.premium_ladder
    assert stray.content_hash == clean.content_hash
    assert _risk_step(priced_stray).dropped_inputs == [_STRAY]


@pytest.mark.req("FR-222")
async def test_a_step_that_drops_nothing_records_none() -> None:
    """(d) — `dropped_inputs` is `None`, not `[]`, when every key was in the context (DP-S2 (i):
    `list[str] | None`, "set only on a `model_call` step", `None` when there are none).

    RED at `102341aa`: `AttributeError: 'TraceStep' object has no attribute 'dropped_inputs'`."""
    result = await score_one(await _compiled(), _ctx(), trace=True)
    assert _risk_step(result).dropped_inputs is None
    other = next(s for s in result.trace.steps if s.step_id == "s_expense")  # type: ignore[union-attr]
    assert other.dropped_inputs is None


@pytest.mark.req("FR-222")
async def test_a_dropped_key_that_feeds_a_required_input_is_refused() -> None:
    """(c) red — PL-1927 Acceptance 15, first case; the 11:40:12 condition "a pre-SL-1541 bundle
    with an unmapped required key scores green on base, must refuse after (c)". `feature_map`
    maps a name the context never holds onto the model's only input, `age_years`, so the
    feature row is empty and the runtime scores anyway.

    RED at `102341aa`: `Failed: DID NOT RAISE` — the quote scores (green on base). After (c):
    `ValueError` (a `CodedError`) matching `MODEL_CALL_FAILED.*MODEL_CALL_REQUIRED_INPUT_ABSENT`,
    its message naming the step and the graph name and carrying no quote value (NFR-499)."""
    compiled = await _compiled_with_feature_map({"driver_years": "age_years"})
    ctx = _ctx(
        inputs={
            "driver_age": _AGE,
            "channel": "direct",
            "min_premium_minor": 0,
            "sanity_cap_minor": 999_999_999,
            "sanity_floor_minor": 0,
        }
    )
    with pytest.raises(ValueError, match=rf"MODEL_CALL_FAILED.*{_ABSENT}") as caught:
        await score_one(compiled, ctx)
    message = str(caught.value)
    assert "s_risk" in message
    assert "driver_years" in message
    assert str(_AGE) not in message


@pytest.mark.req("FR-222")
async def test_the_refusal_names_the_code_through_the_failure_path_with_trace_on() -> None:
    """(c) — the refusal is the same with `trace=True` (the sentinel path does not depend on it).

    RED at `102341aa`: `Failed: DID NOT RAISE`."""
    compiled = await _compiled_with_feature_map({"driver_years": "age_years"})
    with pytest.raises(ValueError, match=rf"MODEL_CALL_FAILED.*{_ABSENT}"):
        await score_one(compiled, _ctx(), trace=True)
