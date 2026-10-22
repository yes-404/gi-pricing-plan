"""The objective preview service (FR-1840, `RL-1616` DP-S5-1) — the part that needs no database.

The route's permission, flag and persistence behaviour is `test_objective_preview_api.py`; this
file is the pure core: what parses, what the curve is, the bound on the grid, the time bound.
"""

from __future__ import annotations

import asyncio
import threading

import numpy as np
import pytest
from pydantic import ValidationError

from app.platform import objective_preview as preview_service
from model_schema import (
    PREVIEW_MAX_GRID_POINTS,
    ObjectiveParameter,
    ObjectivePreviewGrid,
    ObjectivePreviewRequest,
)
from pricing_core.modelling.expression_objective import compile_kernel, derive

# §4.6's example (`asymmetric-burning-cost`), the loss WF-702 Route B authors.
LOSS = "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2"
PARAMETERS = (
    ObjectiveParameter(name="w_under", type="float", default=2.0, min=1, max=10),
    ObjectiveParameter(name="w_over", type="float", default=1.0, min=0.1, max=10),
)
GRID = ObjectivePreviewGrid(y=100.0, w=1.0, f_range=(3.0, 6.0), n_points=50)


def _request(**changes: object) -> ObjectivePreviewRequest:
    fields: dict[str, object] = {"loss": LOSS, "parameters": PARAMETERS}
    return ObjectivePreviewRequest.model_validate(fields | changes)


@pytest.mark.req("FR-1840")
def test_with_no_grid_a_loss_that_parses_is_ok_and_nothing_is_derived() -> None:
    answer = asyncio.run(preview_service.preview(_request()))
    assert answer.ok
    assert answer.curve is None
    assert answer.gradient is None


@pytest.mark.req("FR-1840")
@pytest.mark.parametrize(
    "loss",
    [
        pytest.param("numpy.where(f < y, 1, 2)", id="WF-702-B1.5-attribute-access"),
        pytest.param("w * (y - f", id="not-python-at-all"),
    ],
)
def test_a_loss_outside_the_grammar_is_ok_false_with_a_position_not_an_exception(
    loss: str,
) -> None:
    answer = asyncio.run(preview_service.preview(_request(loss=loss, parameters=())))
    assert not answer.ok
    assert answer.error is not None
    assert answer.error.reason == "grammar"
    assert answer.error.line == 1
    assert answer.error.column is not None


@pytest.mark.req("FR-1840")
def test_the_curve_is_the_fits_own_kernel_over_the_same_loss_values_and_grid() -> None:
    answer = asyncio.run(preview_service.preview(_request(grid=GRID)))
    assert answer.ok
    assert answer.curve is not None

    values = {"w_under": 2.0, "w_over": 1.0}
    derived = derive(LOSS, parameters=list(values))
    assert (answer.gradient, answer.hessian) == (derived.gradient, derived.hessian)

    f = np.linspace(3.0, 6.0, 50)
    y, w = np.full(50, 100.0), np.ones(50)
    for name, text in (
        ("loss", LOSS),
        ("gradient", derived.gradient),
        ("hessian", derived.hessian),
    ):
        expected = compile_kernel(text, parameters=values)(y, f, w)
        assert getattr(answer.curve, name) == pytest.approx(tuple(expected))
    assert answer.curve.f == pytest.approx(tuple(f))


@pytest.mark.req("FR-1840")
def test_chosen_values_replace_the_defaults() -> None:
    chosen = asyncio.run(preview_service.preview(_request(grid=GRID, values={"w_under": 5.0})))
    default = asyncio.run(preview_service.preview(_request(grid=GRID)))
    assert chosen.curve is not None
    assert default.curve is not None
    assert chosen.curve.loss != default.curve.loss


@pytest.mark.req("FR-1840")
def test_a_non_finite_point_is_null_not_a_json_error() -> None:
    answer = asyncio.run(
        preview_service.preview(
            _request(
                loss="log(f)", parameters=(), grid=GRID.model_copy(update={"f_range": (-1.0, 1.0)})
            )
        )
    )
    assert answer.ok
    assert answer.curve is not None
    assert answer.curve.loss[0] is None


@pytest.mark.req("FR-1840")
def test_3a_a_grid_over_the_maximum_is_refused_by_the_request_itself() -> None:
    with pytest.raises(ValidationError):
        ObjectivePreviewGrid(y=1.0, f_range=(0.0, 1.0), n_points=PREVIEW_MAX_GRID_POINTS + 1)
    assert (
        ObjectivePreviewGrid(y=1.0, f_range=(0.0, 1.0), n_points=PREVIEW_MAX_GRID_POINTS).n_points
        == PREVIEW_MAX_GRID_POINTS
    )


@pytest.mark.req("FR-1840")
@pytest.mark.parametrize(
    "values",
    [{"w_under": 11.0}, {"w_under": 0.5}, {"nope": 1.0}],
    ids=["above-max", "below-min", "undeclared"],
)
def test_a_chosen_value_outside_its_declared_range_is_refused(values: dict[str, float]) -> None:
    with pytest.raises(ValidationError):
        _request(values=values)


@pytest.mark.req("FR-1840")
def test_3b_a_slow_derivation_times_out_to_ok_false_and_leaves_no_worker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    release = threading.Event()
    started = threading.Event()

    def slow(*_: object, **__: object) -> object:
        started.set()
        release.wait(5)
        raise AssertionError("the timed-out derivation's result must be discarded")

    monkeypatch.setattr(preview_service, "derive", slow)
    answer = asyncio.run(preview_service.preview(_request(grid=GRID), timeout=0.2))
    assert started.is_set()
    assert not answer.ok
    assert answer.error is not None
    assert answer.error.reason == "timeout"

    release.set()
    assert preview_service.wait_idle(timeout=5), "a worker is still running after the timeout"


@pytest.mark.req("FR-1840")
def test_3b_work_not_yet_started_is_cancelled_at_the_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    release = threading.Event()
    ran = []

    def slow(*_: object, **__: object) -> object:
        ran.append(1)
        release.wait(5)
        raise RuntimeError("discarded")

    monkeypatch.setattr(preview_service, "derive", slow)

    async def saturate() -> list[object]:
        n = preview_service.PREVIEW_WORKERS + 2
        return list(
            await asyncio.gather(
                *(preview_service.preview(_request(grid=GRID), timeout=0.3) for _ in range(n))
            )
        )

    answers = asyncio.run(saturate())
    assert all(not a.ok for a in answers)  # type: ignore[attr-defined]
    release.set()
    assert preview_service.wait_idle(timeout=5)
    assert len(ran) == preview_service.PREVIEW_WORKERS  # the queued two never started


@pytest.mark.req("FR-1840")
def test_3c_the_preview_executor_is_its_own_and_shared_with_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PL-1665 5.7, last sentence: a preview never runs on a thread `/score` or any other
    `asyncio.to_thread` caller uses, and nothing else in `app` can reach the preview's pool."""
    from pathlib import Path

    seen: list[str] = []

    def record(*_: object, **__: object) -> object:
        seen.append(threading.current_thread().name)
        raise RuntimeError("stop after recording the thread")

    monkeypatch.setattr(preview_service, "derive", record)
    asyncio.run(preview_service.preview(_request(grid=GRID)))
    other = asyncio.run(asyncio.to_thread(lambda: threading.current_thread().name))
    assert seen
    assert seen[0].startswith("objective-preview")
    assert not other.startswith("objective-preview")

    executor = preview_service._executor
    assert executor._max_workers == preview_service.PREVIEW_WORKERS
    source = Path(preview_service.__file__).parents[1]
    users = [
        str(path.relative_to(source))
        for path in source.rglob("*.py")
        if path != Path(preview_service.__file__)
        and "_executor" in path.read_text()
        and "objective_preview" in path.read_text()
    ]
    assert users == []
