"""The Custom Objective preview (`02` FR-1840, `RL-1616` DP-S5-1): stateless, bounded, governed
by the route, and the same `derive` and `compile_kernel` a fit uses.

Nothing here touches a database or the audit log: a preview is not a derivation (NFR-484's
“objective derivation” is the one `/derive` stores). The work runs in this module's own
executor, shared with nothing, so it cannot queue ahead of `/score` (clause 3c), with a fixed
worker count and a wall-clock timeout (clause 3b).
"""

from __future__ import annotations

import asyncio
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from app.errors import PlatformError
from app.platform.objectives import grammar_refusal
from model_schema import (
    FieldError,
    ObjectivePreview,
    ObjectivePreviewCurve,
    ObjectivePreviewError,
    ObjectivePreviewRequest,
)
from pricing_core.data.expression_sympy import OBJECTIVE_SYMBOLS
from pricing_core.data.expressions import DEFAULT_LIMITS, ExpressionError, measure_expression
from pricing_core.modelling.expression_objective import compile_kernel, derive
from pricing_core.safe_error import safe_error_detail

__all__ = [
    "PREVIEW_TIMEOUT_SECONDS",
    "PREVIEW_WORKERS",
    "preview",
    "refuse_over_bound",
    "wait_idle",
]

#: FR-1840 clause 3b: the executor's fixed worker count and the wall-clock timeout.
PREVIEW_WORKERS = 2
PREVIEW_TIMEOUT_SECONDS = 5.0

_executor = ThreadPoolExecutor(max_workers=PREVIEW_WORKERS, thread_name_prefix="objective-preview")
_pending = 0  # submitted and not yet finished or cancelled: running or queued
_pending_lock = threading.Lock()


def _settled(_: object) -> None:
    global _pending
    with _pending_lock:
        _pending -= 1


def refuse_over_bound(request: ObjectivePreviewRequest) -> None:
    """FR-1840 clause 3a: a loss over FR-145's node or depth limit is 422 `VALIDATION_FAILED`.

    Checked before any parse-and-derive work. A loss that does not parse as Python at all is not
    over a bound: it is the editor's 200 `ok: false` (`_run`), so a `SyntaxError` passes here.
    (The grid's own bound is `ObjectivePreviewGrid`'s, refused by the request model.)
    """
    try:
        size = measure_expression(request.loss)
    except SyntaxError:
        return
    limits = DEFAULT_LIMITS
    if size.nodes > limits.max_nodes or size.depth > limits.max_depth:
        raise PlatformError(
            "VALIDATION_FAILED",
            "The loss is over the expression limits",
            422,
            f"the loss has {size.nodes} nodes and depth {size.depth}; the limits are "
            f"{limits.max_nodes} nodes and depth {limits.max_depth} (02 §4.6, FR-145).",
            errors=(
                FieldError(
                    field="loss",
                    code="VALIDATION_FAILED",
                    message=f"over the FR-145 limits ({limits.max_nodes} nodes, "
                    f"depth {limits.max_depth})",
                ),
            ),
        )


def _finite(values: np.ndarray) -> tuple[float | None, ...]:
    return tuple(float(v) if math.isfinite(v) else None for v in values)


def _run(request: ObjectivePreviewRequest) -> ObjectivePreview:
    """Parse, then (with a grid) derive and evaluate. Synchronous and pure."""
    names = [p.name for p in request.parameters]
    refusal = grammar_refusal(request.loss, symbols=OBJECTIVE_SYMBOLS | frozenset(names))
    if refusal is not None:
        line, column, reason = refusal
        return ObjectivePreview(
            ok=False,
            error=ObjectivePreviewError(reason="grammar", message=reason, line=line, column=column),
        )
    grid = request.grid
    if grid is None:
        return ObjectivePreview(ok=True)

    values = {p.name: request.values.get(p.name, p.default) for p in request.parameters}
    try:
        derived = derive(request.loss, parameters=names)
    except ExpressionError as exc:
        # After the loss parsed there is no source position (`RL-1410`'s derive refusal).
        return ObjectivePreview(
            ok=False, error=ObjectivePreviewError(reason="grammar", message=safe_error_detail(exc))
        )
    f = np.linspace(grid.f_range[0], grid.f_range[1], grid.n_points)
    y = np.full(grid.n_points, grid.y)
    w = np.full(grid.n_points, grid.w)

    def evaluate(text: str) -> tuple[float | None, ...]:
        return _finite(compile_kernel(text, parameters=values)(y, f, w))

    return ObjectivePreview(
        ok=True,
        gradient=derived.gradient,
        hessian=derived.hessian,
        derivation_version=derived.derivation_version,
        curve=ObjectivePreviewCurve(
            f=tuple(float(v) for v in f),
            loss=evaluate(request.loss),
            gradient=evaluate(derived.gradient),
            hessian=evaluate(derived.hessian),
        ),
    )


async def preview(
    request: ObjectivePreviewRequest, *, timeout: float | None = None
) -> ObjectivePreview:
    """Run `request` off the event loop, bounded. A timeout is an answer (`ok: false`), not a 500.

    The timeout counts from submission, so waiting in the queue is bounded too. `wait_for`
    cancels the future at the timeout: work not yet started never starts; work that has
    started is bounded by FR-145's limits, and its result is discarded.
    """
    global _pending
    timeout = PREVIEW_TIMEOUT_SECONDS if timeout is None else timeout
    with _pending_lock:
        _pending += 1
    # The concurrent future (not the asyncio one) settles when the work ends *or* is cancelled
    # before it starts, which is exactly when a worker is no longer committed to it.
    concurrent = _executor.submit(_run, request)
    concurrent.add_done_callback(_settled)
    future = asyncio.wrap_future(concurrent)
    try:
        return await asyncio.wait_for(future, timeout)
    except TimeoutError:
        return ObjectivePreview(
            ok=False,
            error=ObjectivePreviewError(
                reason="timeout",
                message=f"the preview did not finish within {timeout:g} seconds",
            ),
        )


def wait_idle(timeout: float) -> bool:
    """Whether no preview is running or queued, waiting up to `timeout` seconds (for tests)."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with _pending_lock:
            if _pending == 0:
                return True
        time.sleep(0.02)
    return False
