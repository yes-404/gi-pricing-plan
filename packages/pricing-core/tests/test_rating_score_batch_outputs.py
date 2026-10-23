"""FD-1561's fix (WK-1178, SL-1566): a row's serialisation failure is that row's error row
(FR-255), and batch writes every declared output type `/score` serves (FR-254).

Fixture shape: reuses `test_rating_score`'s and `test_rating_score_batch`'s own fixtures
rather than duplicating them, the established convention in this suite.
"""

from __future__ import annotations

import copy
import itertools
import json
from collections.abc import Callable
from decimal import Decimal
from typing import Any

import polars as pl
import pytest
from test_rating_runtime import _gbm_model_payload, _rate_table_payload, _train_tiny_booster
from test_rating_score import _algorithm_payload, _compiled, _version
from test_rating_score_batch import _contexts, _ctx_to_row

import pricing_core.rating.score as score_module
from model_schema.refs import ArtifactRef
from pricing_core.rating import compile as compile_module
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import (
    _KNOWN_OUTPUT_TYPES,
    _coerce_output_value,
    score_batch,
    score_one,
)


def _fail_on_second_call(
    original: Callable[..., str], exc: BaseException
) -> Callable[..., str]:
    """`original`, except its second call raises `exc`. The rows of one chunk are scored in
    order (`_score_batch_chunk`), so the second call is the row `Q1`."""
    calls = itertools.count()

    def wrapper(*args: Any, **kwargs: Any) -> str:
        if next(calls) == 1:
            raise exc
        return original(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------------------------
# Task 1: the row escape (PL-1565 items 1-3).
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-255")
@pytest.mark.parametrize(
    ("target", "exc"),
    [
        ("_outputs_json", ValueError("injected serialisation failure")),
        ("_outputs_json", TypeError("injected serialisation failure")),
        ("_ladder_json", KeyError("injected serialisation failure")),
    ],
)
async def test_a_row_whose_serialisation_raises_is_an_error_row_and_the_batch_continues(
    monkeypatch: pytest.MonkeyPatch, target: str, exc: BaseException
) -> None:
    compiled = await _compiled()
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(4)]).lazy()
    clean = {r["quote_id"]: r for r in score_batch(compiled, frame).collect().to_dicts()}

    monkeypatch.setattr(
        score_module, target, _fail_on_second_call(getattr(score_module, target), exc)
    )
    out = score_batch(compiled, frame).collect().to_dicts()
    by_quote_id = {r["quote_id"]: r for r in out}

    assert len(out) == 4
    bad = by_quote_id["Q1"]
    assert bad["outcome"] == "error"
    assert bad["error_code"] == type(exc).__name__
    assert bad["premium_ladder_json"] is None
    assert bad["outputs_json"] is None
    for quote_id in ("Q0", "Q2", "Q3"):
        good = by_quote_id[quote_id]
        assert good["error_code"] is None
        assert good["premium_ladder_json"] == clean[quote_id]["premium_ladder_json"]
        assert good["outputs_json"] == clean[quote_id]["outputs_json"]


@pytest.mark.req("NFR-499")
async def test_an_error_row_from_serialisation_carries_no_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = await _compiled()
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(4)]).lazy()
    monkeypatch.setattr(
        score_module,
        "_outputs_json",
        _fail_on_second_call(
            score_module._outputs_json, ValueError("premium_in=SENTINEL-9513")
        ),
    )
    out = score_batch(compiled, frame).collect().to_dicts()
    bad = next(r for r in out if r["quote_id"] == "Q1")
    assert bad["outcome"] == "error"
    assert "SENTINEL-9513" not in (bad["error_message"] or "")


@pytest.mark.req("FR-255")
async def test_not_implemented_still_propagates_from_serialisation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Control, not a red: a genuinely undesigned case is not a per-row data error, as one
    raised inside the first `try` is not today. It passes before and after Task 1."""
    compiled = await _compiled()
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(4)]).lazy()
    monkeypatch.setattr(
        score_module,
        "_outputs_json",
        _fail_on_second_call(score_module._outputs_json, NotImplementedError("undesigned")),
    )
    with pytest.raises(NotImplementedError):
        score_batch(compiled, frame).collect()


# ---------------------------------------------------------------------------
# Task 2: the four declared types (PL-1565 items 5-8, 12, 13; RL-1567 T1).
# ---------------------------------------------------------------------------


def _probe_payload(declared_type: str, expr: str) -> dict[str, Any]:
    """Task 1.4's fixture plus one `expression` step and one `output` step declaring
    `probe_out` of the type under test. `driver_age` is 18 on row `Q0`."""
    payload = copy.deepcopy(_algorithm_payload())
    payload["outputs"].append({"name": "probe_out", "type": declared_type, "required": False})
    payload["steps"].append(
        {
            "step_id": "s_probe", "type": "expression", "label": "Probe",
            "expr": expr, "result_type": declared_type,
            "consumes": ["driver_age"], "produces": "probe_raw",
        }
    )
    payload["steps"].append(
        {
            "step_id": "s_out_probe", "type": "output", "label": "Probe output",
            "output_name": "probe_out", "rounding": {"mode": "half_even", "dp": 2},
            "consumes": ["probe_raw"],
        }
    )
    return payload


class _ProbeResolver:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payloads = {
            "rating_algorithm:score-fixture@1": payload,
            "rate_table:motor-expense@1": _rate_table_payload(),
            "model:motor-freq@1": _gbm_model_payload(_train_tiny_booster()),
        }

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        return ResolvedArtifact(status="approved", payload=self._payloads[str(ref)])


async def _probe_bundle(declared_type: str, expr: str) -> CompiledBundle:
    bundle = await compile_bundle(_version(), _ProbeResolver(_probe_payload(declared_type, expr)))
    return load_bundle(bundle)


@pytest.mark.req("FR-254")
@pytest.mark.parametrize("declared_type", ["int", "count"])
async def test_an_integer_declared_output_is_the_same_json_integer_in_batch_and_on_score(
    declared_type: str,
) -> None:
    compiled = await _probe_bundle(declared_type, "driver_age")
    contexts = _contexts(10)
    out = score_batch(compiled, pl.DataFrame([_ctx_to_row(c) for c in contexts]).lazy())
    by_quote_id = {r["quote_id"]: r for r in out.collect().to_dicts()}
    for ctx in contexts:
        row = by_quote_id[ctx.quote_id]
        assert row["error_code"] is None, row["error_code"]
        batch_value = json.loads(row["outputs_json"])["probe_out"]
        served = json.loads((await score_one(compiled, ctx)).model_dump_json())["outputs"]
        assert batch_value == served["probe_out"]
        assert type(batch_value) is int
        assert type(served["probe_out"]) is int


@pytest.mark.req("FR-255")
@pytest.mark.parametrize("declared_type", ["int", "count"])
async def test_a_non_integral_value_for_an_integer_output_is_an_error_row(
    declared_type: str,
) -> None:
    # Until SL-1569 merges the row's code is the class name (RL-1567 item 10, DP-3); after
    # it, `RATING_TYPE_MISMATCH` from the single producer (SL-1569 re-expects this line).
    compiled = await _probe_bundle(declared_type, "driver_age * 1.1")
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(4)]).lazy()
    out = score_batch(compiled, frame).collect().to_dicts()
    assert len(out) == 4
    q0 = next(r for r in out if r["quote_id"] == "Q0")  # driver_age 18 -> 19.8
    assert q0["outcome"] == "error"
    assert q0["error_code"] == "ValueError"
    assert q0["outputs_json"] is None
    assert "19.8" not in (q0["error_message"] or "")  # NFR-499: no value in the message


@pytest.mark.req("FR-214")
@pytest.mark.parametrize("declared_type", ["relativity", "percentage"])
@pytest.mark.parametrize(
    ("expr", "expected"), [("driver_age * 1.5", "27.00"), ("driver_age * 1.1", "19.80")]
)
async def test_a_fractional_declared_output_is_a_decimal_string_in_batch(
    declared_type: str, expr: str, expected: str
) -> None:
    """`RL-1343` rule 3, both paths (SL-1569): the exact string at the output step's declared
    dp (2 here), the same string `score_one` serves."""
    compiled = await _probe_bundle(declared_type, expr)
    (context,) = _contexts(1)  # driver_age 18
    frame = pl.DataFrame([_ctx_to_row(context)]).lazy()
    (row,) = score_batch(compiled, frame).collect().to_dicts()
    assert row["error_code"] is None, row["error_code"]
    assert json.loads(row["outputs_json"])["probe_out"] == expected
    assert (await score_one(compiled, context)).outputs["probe_out"] == expected


@pytest.mark.req("FR-254")
def test_the_known_output_types_name_every_numeric_family_member() -> None:
    missing = (compile_module._NUMERIC | {"bool", "string", "date"}) - _KNOWN_OUTPUT_TYPES
    assert not missing, sorted(missing)


@pytest.mark.req("FR-254")
@pytest.mark.parametrize("declared_type", ["int", "count"])
async def test_a_whole_valued_value_under_an_integral_type_is_its_integer_in_batch(
    declared_type: str,
) -> None:
    """`driver_age * 1.5` at age 18 is the whole value 27 (FD-1561's probe)."""
    compiled = await _probe_bundle(declared_type, "driver_age * 1.5")
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(1)]).lazy()
    (row,) = score_batch(compiled, frame).collect().to_dicts()
    assert row["error_code"] is None, row["error_code"]
    assert '"probe_out": 27' in row["outputs_json"]  # an integer token: no "." and no quotes
    assert type(json.loads(row["outputs_json"])["probe_out"]) is int


@pytest.mark.req("FR-255")
@pytest.mark.parametrize("declared_type", ["int", "count"])
async def test_a_near_integer_under_an_integral_type_is_an_error_row(
    declared_type: str,
) -> None:
    # `2.9999999999` is not integral: exact equality with the integer part, no tolerance
    # (RL-1567 item 6). The code is the class name until SL-1569 merges (item 10).
    compiled = await _probe_bundle(declared_type, "driver_age * 0 + 2.9999999999")
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(4)]).lazy()
    out = score_batch(compiled, frame).collect().to_dicts()
    assert len(out) == 4
    for row in out:
        assert row["outcome"] == "error"
        assert row["error_code"] == "ValueError"
        assert row["outputs_json"] is None


@pytest.mark.req("FR-254")
@pytest.mark.parametrize("declared_type", ["int", "count"])
@pytest.mark.parametrize(
    ("value", "expected"), [(3, 3), (3.0, 3), (-2.0, -2), (0.0, 0), (10**15 + 0.0, 10**15)]
)
def test_integral_means_exact_equality_with_the_integer_part(
    declared_type: str, value: float, expected: int
) -> None:
    """`3.0` -> `3` as the integer, not a float (RL-1567 item 6). Reverting the check to
    `isinstance(value, int)` turns the float cases red."""
    got = _coerce_output_value(declared_type, value)
    assert got == expected
    assert type(got) is int


@pytest.mark.req("FR-255")
@pytest.mark.parametrize("declared_type", ["int", "count"])
@pytest.mark.parametrize(
    "value",
    [2.9999999999, 3.0000000001, 0.5, -0.5, float("nan"), float("inf"), float("-inf"),
     True, False, "3", None],
)
def test_a_non_integral_or_non_numeric_value_for_an_integral_type_is_refused_without_the_value(
    declared_type: str, value: Any
) -> None:
    """No tolerance, no bool (`True` is an `int` to Python, not an integer output), no
    non-finite float (whose `int()` would raise `OverflowError`, not the `ValueError`), and
    the message never carries the value (NFR-499)."""
    with pytest.raises(ValueError, match="output must be integral") as caught:
        _coerce_output_value(declared_type, value)
    message = str(caught.value)
    assert declared_type in message
    assert "2.9999" not in message
    assert "3.0000" not in message


@pytest.mark.req("FR-214")
@pytest.mark.parametrize("declared_type", ["relativity", "percentage"])
def test_relativity_and_percentage_take_the_decimal_string_form_never_a_float(
    declared_type: str,
) -> None:
    for value in (27, 19.8, Decimal("1.15"), 0.1 + 0.2):
        got = _coerce_output_value(declared_type, value)
        assert type(got) is str
        assert got == _coerce_output_value("decimal", value)
    assert _coerce_output_value(declared_type, 0.1 + 0.2) == "0.30000000000000004"


@pytest.mark.req("FR-254")
def test_a_declared_type_the_row_does_not_name_is_refused_not_stringified() -> None:
    with pytest.raises(ValueError, match="cannot serialise"):
        _coerce_output_value("float", 1.5)
