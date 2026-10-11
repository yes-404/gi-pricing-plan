"""FD-1561's fix (WK-1178, SL-1566): a row's serialisation failure is that row's error row
(FR-255), and batch writes every declared output type `/score` serves (FR-254).

Fixture shape: reuses `test_rating_score`'s and `test_rating_score_batch`'s own fixtures
rather than duplicating them, the established convention in this suite.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable
from typing import Any

import polars as pl
import pytest
from test_rating_score import _compiled
from test_rating_score_batch import _contexts, _ctx_to_row

import pricing_core.rating.score as score_module
from pricing_core.rating.score import score_batch


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
