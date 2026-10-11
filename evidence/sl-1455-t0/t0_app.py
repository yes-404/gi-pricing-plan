"""SL-1455 Task 0 instruments (PL-1454 Task 0 Step 2) — SCRATCH, never committed.

An out-of-tree stand-in for the plan's patch to `score` and its dependencies: this module
wraps the functions the served request goes through *at import time of the server process*,
so the repository's source is not edited and `main`'s code is exactly what runs. Start the
server with `PYTHONPATH=<this dir> python -m uvicorn t0_app:create_app --factory`.

What it records, to `$T0_OUT/requests.jsonl` (one line per `/api/v1/score` request) and
`$T0_OUT/events.jsonl` (process-wide events), wall clock `time.time()` for both so the two
files line up:

* per-phase milliseconds: rate_limit (`rate_limit.enforce`, FR-452), auth (`authenticate_api_key`), auth_scope (the whole
  `unit_of_work` in `require_caller`, commit included), rbac, rbac_scope, rate_limit, serving_ref,
  fetch_bundle, compiled_for (the two together plus the slot memo), score_one,
  sample_trace, serialise, and `total` (outermost ASGI wrapper);
* DB cost: pool checkouts (`_ConnectionFairy._checkout`, which includes `pool_pre_ping`) with
  their summed milliseconds and the longest, statements, commits;
* slot hits and misses (`BundleSlot.get`);
* events: each GC collection (generation, ms), every event-loop overshoot of 50 ms or more
  (a 10 ms ticker), and `asyncio` debug mode with `slow_callback_duration = 0.05` (those
  lines go to the server's stderr log, which the driver keeps).

Attribution, not an NFR reading: every wrapper below perturbs latency (Step 4).
"""

from __future__ import annotations

import asyncio
import gc
import json
import os
import sys
import time
from contextvars import ContextVar
from pathlib import Path
from typing import Any

OUT = Path(os.environ["T0_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
_REQ = (OUT / "requests.jsonl").open("a", buffering=1)
_EVT = (OUT / "events.jsonl").open("a", buffering=1)

#: The current request's accumulator; `None` outside a `/score` request.
CUR: ContextVar[dict[str, Any] | None] = ContextVar("t0_cur", default=None)
#: Process-wide counters, so a miss outside any request (the warm-up) is still seen.
GLOBAL = {"slot_hit": 0, "slot_miss": 0}


def _event(kind: str, **fields: Any) -> None:
    _EVT.write(json.dumps({"t": time.time(), "kind": kind, **fields}) + "\n")


def _add(name: str, ms: float) -> None:
    cur = CUR.get()
    if cur is not None:
        phases = cur["phases"]
        phases[name] = phases.get(name, 0.0) + ms


def _bump(name: str, by: int = 1) -> None:
    cur = CUR.get()
    if cur is not None:
        cur[name] = cur.get(name, 0) + by


def _timed_async(owner: Any, attr: str, phase: str) -> None:
    original = getattr(owner, attr)

    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        try:
            return await original(*args, **kwargs)
        finally:
            _add(phase, (time.perf_counter() - started) * 1000)

    wrapper.__name__ = getattr(original, "__name__", attr)
    setattr(owner, attr, wrapper)


def _timed_sync(owner: Any, attr: str, phase: str) -> None:
    original = getattr(owner, attr)

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        try:
            return original(*args, **kwargs)
        finally:
            _add(phase, (time.perf_counter() - started) * 1000)

    wrapper.__name__ = getattr(original, "__name__", attr)
    setattr(owner, attr, wrapper)


# -- patches (applied before `create_app` is called) ---------------------------------------

_SCOPE_LABEL = {
    "require_caller": "auth_scope",
    "dependency": "rbac_scope",
    "_serving_ref": "serving_ref_scope",
    "_fetch_bundle": "fetch_bundle_scope",
    "_maybe_sample_trace": "sample_scope",
}


class _Scope:
    """Times a whole `Database.session()` / `unit_of_work()` block, commit included."""

    def __init__(self, inner: Any, label: str) -> None:
        self._inner = inner
        self._label = label

    async def __aenter__(self) -> Any:
        self._t = time.perf_counter()
        return await self._inner.__aenter__()

    async def __aexit__(self, *exc: Any) -> Any:
        try:
            return await self._inner.__aexit__(*exc)
        finally:
            _add(self._label, (time.perf_counter() - self._t) * 1000)


def _patch_scopes() -> None:
    from app.db.session import Database

    for name in ("session", "unit_of_work"):
        original = getattr(Database, name)

        def make(orig: Any) -> Any:
            def wrapper(self: Any) -> Any:
                label = _SCOPE_LABEL.get(sys._getframe(1).f_code.co_name)
                inner = orig(self)
                return _Scope(inner, label) if label else inner

            return wrapper

        setattr(Database, name, make(original))


def _patch_pool() -> None:
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    from sqlalchemy.pool import base

    fairy = base._ConnectionFairy
    original = fairy._checkout.__func__  # type: ignore[attr-defined]

    def checkout(cls: Any, *args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        try:
            return original(cls, *args, **kwargs)
        finally:
            ms = (time.perf_counter() - started) * 1000
            cur = CUR.get()
            if cur is not None:
                cur["checkouts"] = cur.get("checkouts", 0) + 1
                cur["checkout_ms"] = cur.get("checkout_ms", 0.0) + ms
                cur["checkout_max_ms"] = max(cur.get("checkout_max_ms", 0.0), ms)
            if ms >= 50:
                _event("slow_checkout", ms=ms)

    fairy._checkout = classmethod(checkout)  # type: ignore[assignment,method-assign]

    @event.listens_for(Engine, "before_cursor_execute")
    def _stmt(*_: Any) -> None:
        _bump("statements")

    @event.listens_for(Engine, "commit")
    def _commit(*_: Any) -> None:
        _bump("commits")

    @event.listens_for(Engine, "connect")
    def _connect(*_: Any) -> None:
        _event("new_connection")


def _patch_slot() -> None:
    from app.platform.bundle_slot import BundleSlot

    original = BundleSlot.get

    def get(self: Any, content_hash: str) -> Any:
        found = original(self, content_hash)
        key = "slot_hit" if found is not None else "slot_miss"
        GLOBAL[key] += 1
        _bump(key)
        return found

    BundleSlot.get = get  # type: ignore[method-assign]


def _stash_and_fill(score: Any) -> None:
    """Default-live quotes (Step 3b).

    On `main`, `score()` passes the request's `ctx` to `score_one` unchanged, and `score_one`
    refuses a `ctx` whose `options.rating_version_ref` is None (`pricing_core/rating/score.py`
    `score_one`, INPUT_CONTRACT_VIOLATION) - while `_serving_ref` has resolved the live ref.
    `T0_FILL_REF=1` (the default) injects that ref into `ctx` before `score_one`, i.e. measures
    the path a corrected handler would run; `T0_FILL_REF=0` leaves `main` as it is, which the
    driver's one-request probe uses to record what `main` answers. Either way the request
    records `ref_filled`.
    """
    fill = os.environ.get("T0_FILL_REF", "1") == "1"
    resolve = score._serving_ref
    inner = score.score_one

    async def serving_ref(*args: Any, **kwargs: Any) -> Any:
        result = await resolve(*args, **kwargs)
        cur = CUR.get()
        if cur is not None:
            cur["_ref"] = result[0]
        return result

    async def score_one(bundle: Any, ctx: Any, **kwargs: Any) -> Any:
        cur = CUR.get()
        needs = ctx.options is None or ctx.options.rating_version_ref is None
        if cur is not None:
            cur["ref_filled"] = bool(needs and fill)
        if needs and fill and cur is not None and "_ref" in cur:
            from model_schema.scoring import QuoteContextOptions

            ctx = ctx.model_copy(update={
                "options": QuoteContextOptions(
                    trace=kwargs.get("trace", False), rating_version_ref=cur["_ref"]
                )
            })
        started = time.perf_counter()
        try:
            return await inner(bundle, ctx, **kwargs)
        finally:
            _add("score_one", (time.perf_counter() - started) * 1000)

    score._serving_ref = serving_ref
    score.score_one = score_one


def _patch_phases() -> None:
    import app.api.deps as deps
    import app.api.score as score
    import app.platform.rate_limit as rate_limit
    import app.platform.rbac as rbac
    from model_schema.scoring import ScoringResult

    _timed_async(deps, "authenticate_api_key", "auth")
    _timed_async(rbac, "require_permission", "rbac")
    # Added 2026-10-11 for main f4587e48 (FR-452, #1280): score.py calls rate_limit.enforce on every
    # request - a Setting resolve in its own DB session, then a Redis INCR only if a limit is set.
    _timed_async(rate_limit, "enforce", "rate_limit")
    _stash_and_fill(score)
    _timed_async(score, "_serving_ref", "serving_ref")
    _timed_async(score, "_fetch_bundle", "fetch_bundle")
    _timed_async(score, "_compiled_for", "compiled_for")
    _timed_async(score, "_maybe_sample_trace", "sample_trace")
    _timed_sync(ScoringResult, "model_dump_json", "serialise")


def _patch_gc() -> None:
    state: dict[str, float] = {}

    def callback(phase: str, info: dict[str, int]) -> None:
        if phase == "start":
            state["t"] = time.perf_counter()
        else:
            ms = (time.perf_counter() - state.get("t", time.perf_counter())) * 1000
            _event("gc", generation=info["generation"], ms=ms, collected=info["collected"])

    gc.callbacks.append(callback)


async def _ticker() -> None:
    """A 10 ms ticker: any overshoot of 50 ms or more is a stall of the whole loop."""
    loop = asyncio.get_running_loop()
    expected = loop.time() + 0.01
    while True:
        await asyncio.sleep(0.01)
        late = (loop.time() - expected) * 1000
        if late >= 50:
            _event("loop_stall", late_ms=late)
        expected = loop.time() + 0.01


class _Middleware:
    """The outermost ASGI wrapper: owns the per-request accumulator and the output line."""

    def __init__(self, app: Any) -> None:
        self.app = app
        self._started = False

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http" or not scope["path"].endswith("/score"):
            await self.app(scope, receive, send)
            return
        if not self._started:
            self._started = True
            loop = asyncio.get_running_loop()
            loop.set_debug(True)
            loop.slow_callback_duration = 0.05
            asyncio.create_task(_ticker())
        cur: dict[str, Any] = {"t": time.time(), "phases": {}}
        token = CUR.set(cur)
        status = {"code": 0}

        async def capture(message: Any) -> None:
            if message["type"] == "http.response.start":
                status["code"] = message["status"]
            await send(message)

        started = time.perf_counter()
        try:
            await self.app(scope, receive, capture)
        finally:
            cur["phases"]["total"] = (time.perf_counter() - started) * 1000
            cur["status"] = status["code"]
            cur.pop("_ref", None)
            _REQ.write(json.dumps(cur) + "\n")
            CUR.reset(token)


def create_app() -> Any:
    _patch_pool()
    _patch_slot()
    _patch_scopes()
    _patch_phases()
    from app.main import create_app as real

    app = real()
    _patch_gc()  # last: import-time collections are not the served path
    app.add_middleware(_Middleware)
    _event("started", pid=os.getpid(), python=sys.version.split()[0])
    return app
