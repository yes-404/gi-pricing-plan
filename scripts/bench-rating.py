#!/usr/bin/env python3
"""Measure NFR-RATE-1 (component) and NFR-RATE-2 — W11 Slice 1 Task 1.5.

`score_one` measured directly: no HTTP, no FastAPI, no database, no cache. The full-path
and sustained-200-rps halves of NFR-RATE-1 are Slice 2's Task 2.1
(`docs/plans/2026-08-29-w11-1-evaluator-core.md`); this discharges the *component* half —
`docs/roadmap.md`'s "build the latency harness in W11 alongside the evaluator, not after".

`bench-model.py`'s and `bench-data.py`'s sibling, and it inherits their governance rule
verbatim (Ruling 6, `docs/plans/2026-08-29-w11-slice1-rulings.md`):

    Not a CI gate. A timing assertion on a shared runner fails for reasons that have
    nothing to do with the code, and a check that fails randomly teaches everyone to
    re-run it. This produces numbers for a workstream closure record instead, where a
    human reads them once against the budget.

    uv run python scripts/bench-rating.py

**Stdlib-only tooling, per Ruling 6's disposition.** `time.perf_counter` for timing, one
`asyncio` event loop driving a sequential await loop (no concurrency measurement here —
Task 1.4's own `docs/research/w11-task-1-4-model-call-concurrency.md` already covers
`async_evaluate()`'s concurrency behaviour; this is a single-caller latency distribution).
No load-generation library and no HTTP client: DP3's load generator (`asyncio` + `httpx`)
is Task 2.1's, for the sustained-rps full-path measurement, not this component one.
`pricing_core`, `model_schema` and `xgboost` are already-declared workspace dependencies
used to build the fixture, exactly as `bench-model.py` already imports `numpy`/`polars` for
the same purpose — Ruling 6's acceptance test is about a *load-generation* dependency
(`locust`/`k6`/`hey`/`wrk` in a `pyproject.toml`, `uv.lock`, CI workflow or setup
instruction), never about these.

Fixtures are built here rather than imported from `packages/pricing-core/tests/`, so this
script stays a `pricing-core` *client* (ADR-0001's boundary) rather than a second entry
point into the test suite's private fixtures — `bench-model.py`'s own
`bench_certify`/`_default_sampling` docstring states the same rule for the same reason.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import xgboost as xgb

_PACKAGES = Path(__file__).resolve().parent.parent / "packages"
sys.path.insert(0, str(_PACKAGES / "pricing-core" / "src"))
sys.path.insert(0, str(_PACKAGES / "model-schema" / "src"))

from model_schema.rating import RatingVersion  # noqa: E402
from model_schema.refs import ArtifactRef  # noqa: E402
from model_schema.scoring import QuoteContext, QuoteContextOptions  # noqa: E402
from pricing_core.rating.compile import (  # noqa: E402
    ArtifactResolver,
    Bundle,
    ResolvedArtifact,
    compile_bundle,
)
from pricing_core.rating.runtime import CompiledBundle, load_bundle  # noqa: E402
from pricing_core.rating.score import build_scoring_result, score_one  # noqa: E402

_RATING_VERSION_REF = ArtifactRef(type="rating_version", slug="bench-rating", version=1)

#: NFR-RATE-1/2 (`docs/specs/03-rating-engine.md` §9), in milliseconds / as a fraction.
BUDGET_WITH_GBM_P99_MS = 50.0
BUDGET_WITHOUT_GBM_P99_MS = 15.0
BUDGET_TRACE_OVERHEAD = 0.20

#: `w8-spike-resolution.md` / `w11-task-1-4-model-call-concurrency.md`'s own shape: discard
#: a warmup, then measure a fixed count.
WARMUP_CALLS = 200
MEASURED_CALLS = 1000

#: A ~200-step motor structure (NFR-RATE-1's own phrase), split as Task 1.3's own
#: NFR-RATE-4 fixture was: a double-digit input block, one table lookup, one `exact` GBM
#: `model_call`, and a long chained-expression tail. `N_EXPR_STEPS` is picked so
#: `2 (age, channel) + len(FEATURE_ORDER) + 1 (table) + [1 model_call] + N + 1 (output)`
#: lands at 200 with the GBM step and 199 without it — both "~200" against NFR-RATE-1's
#: own approximation.
FEATURE_ORDER = [f"f{i}" for i in range(8)]
N_EXPR_STEPS = 187


def loadavg() -> float:
    """The 1-minute load average, read at the moment of the call.

    Read per measured block rather than once at startup. NFR-RATE-1 states its budget
    "at 200 rps per replica", so the contention the box was under is part of the
    measurement's meaning, not context for it — and a single reading taken before a run
    that then trains a booster and issues 3,000 timed calls describes a machine that no
    longer exists by the time the first sample is taken. The audit of PR #416 found
    NFR-RATE-1's without-GBM half PASSing at load 0.39 and OVER on re-runs at load
    1.6-6.4; nothing in this script's output had recorded which condition produced which
    number.
    """
    with open("/proc/loadavg") as handle:
        return float(handle.read().split()[0])


def machine() -> str:
    """`bench-model.py`'s own reader, replicated: the load average is part of the
    measurement, not colour, on a development machine shared between concurrent
    sessions."""
    cores = os.cpu_count() or 0
    with open("/proc/meminfo") as handle:
        total_kb = int(handle.readline().split()[1])
    model = "unknown"
    with open("/proc/cpuinfo") as handle:
        for line in handle:
            if line.startswith("model name"):
                model = line.split(":", 1)[1].strip()
                break
    return (
        f"{model}, {cores} cores, {total_kb / 1e6:.1f} GB RAM, "
        f"1-minute load average {loadavg():.2f} at startup"
    )


# -- fixtures --------------------------------------------------------------------------


def _train_booster(*, rows: int = 5_000, rounds: int = 300, seed: int = 20260829) -> bytes:
    """A real, trained XGBoost booster on `FEATURE_ORDER` — sized like Task 1.3's own
    NFR-RATE-4 "real large" fixture (300 rounds), not a 3-round toy: NFR-RATE-1 is a
    latency budget on the *real* `model_call` path, and NFR-RATE-14's own re-measurement
    already showed tree count barely moves single-row XGBoost latency at `nthread=1` — but
    asserting that from a toy booster here would be begging the question this harness
    exists to measure.
    """
    rng = random.Random(seed)
    x = [[rng.uniform(0.0, 1.0) for _ in FEATURE_ORDER] for _ in range(rows)]
    y = [sum(row) + rng.uniform(-0.1, 0.1) for row in x]
    dtrain = xgb.DMatrix(x, label=y, feature_names=FEATURE_ORDER)
    params = {"objective": "reg:squarederror", "max_depth": 6, "eta": 0.1}
    booster = xgb.train(params, dtrain, num_boost_round=rounds)
    return bytes(booster.save_raw(raw_format="json"))


def _gbm_model_payload(booster_bytes: bytes, *, rounds: int, rows: int) -> dict[str, Any]:
    """Shaped like Task 1.2's real resolver produces it (Ruling 7): the `Model` dump's
    `fit_result`, plus `booster_content` carried inline rather than as a blob reference —
    the same shape `test_rating_runtime._gbm_model_payload` uses, replicated rather than
    imported (see module docstring)."""
    return {
        "model_family_slug": "bench-freq",
        "version": 1,
        "status": "approved",
        "fit_result": {
            "model_type": "xgboost",
            "booster_blob": {
                "sha256": "a" * 64, "bytes": len(booster_bytes),
                "media_type": "application/json",
            },
            "booster_format": "xgboost_json",
            "feature_order": FEATURE_ORDER,
            "feature_dtypes": {},
            "categorical_maps": {},
            "monotone_constraints": [],
            "base_margin": {"kind": "none"},
            "best_iteration": rounds,
            "inverse_link": None,
            "rows": rows,
            "fit_seconds": 0.0,
            "library_versions": {},
            "dropped_eval_metrics": [],
            "booster_content": booster_bytes.decode("utf-8"),
        },
    }


def _rate_table_payload() -> dict[str, Any]:
    return {
        "slug": "bench-expense", "version": 1, "rateable": True, "storage": "rows",
        "keys": [{"name": "channel", "type": "string", "banding_ref": None}],
        "value": {
            "name": "expense_factor", "type": "relativity", "unit": "factor",
            "min": None, "max": None,
        },
        "default_row": None,
        "rows": [
            {"channel": "direct", "expense_factor": "1.1"},
            {"channel": "broker", "expense_factor": "1.25"},
        ],
    }


def _algorithm_payload(*, with_gbm: bool, n_expr: int) -> dict[str, Any]:
    """A ~200-step motor structure. See the module-level constants' docstring for the
    step-count accounting.

    Every declared input is wired to something a downstream step actually consumes —
    `driver_age`/`channel` and all of `FEATURE_ORDER` — rather than left decorative: the
    `RatingAlgorithm` graph-invariant check does not require this (an input step is
    trivially "reachable from an input" by being one), but a benchmark fixture claiming to
    be a "motor structure" should not have inputs nothing downstream ever reads.
    """
    slug = "bench-rating-gbm" if with_gbm else "bench-rating-no-gbm"
    input_contract: list[dict[str, Any]] = [
        {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99},
        {"name": "channel", "type": "enum", "domain": ["direct", "broker"], "nullable": False},
    ]
    input_contract += [
        {"name": name, "type": "decimal", "nullable": False} for name in FEATURE_ORDER
    ]

    steps: list[dict[str, Any]] = [
        {"step_id": "s_in_age", "type": "input", "label": "Driver age",
         "input_name": "driver_age", "on_missing": "error", "produces": "driver_age"},
        {"step_id": "s_in_channel", "type": "input", "label": "Channel",
         "input_name": "channel", "on_missing": "error", "produces": "channel"},
    ]
    for name in FEATURE_ORDER:
        steps.append({
            "step_id": f"s_in_{name}", "type": "input", "label": f"Rating factor {name}",
            "input_name": name, "on_missing": "error", "produces": name,
        })
    steps.append({
        "step_id": "s_expense", "type": "table", "label": "Expense factor",
        "rate_table_ref": "rate_table:bench-expense@1", "key_expr": ["channel"],
        "on_miss": "error", "consumes": ["channel"], "produces": "expense_factor",
    })

    if with_gbm:
        steps.append({
            "step_id": "s_risk", "type": "model_call", "label": "Risk premium",
            "model_ref": "model:bench-freq@1", "mode": "exact",
            "feature_map": {name: name for name in FEATURE_ORDER},
            "consumes": list(FEATURE_ORDER), "produces": ["risk_premium_minor"],
        })
        seed_expr = "(risk_premium_minor * expense_factor) + driver_age"
        seed_consumes = ["risk_premium_minor", "expense_factor", "driver_age"]
    else:
        seed_expr = "(driver_age * expense_factor * 100) + driver_age"
        seed_consumes = ["driver_age", "expense_factor"]

    steps.append({
        "step_id": "s_v000", "type": "expression", "label": "v000",
        "expr": seed_expr, "result_type": "money_minor",
        "consumes": seed_consumes, "produces": "v000",
    })
    for i in range(1, n_expr):
        steps.append({
            "step_id": f"s_v{i:03d}", "type": "expression", "label": f"v{i:03d}",
            "expr": f"v{i - 1:03d} * 1.0001 + {i}", "result_type": "money_minor",
            "consumes": [f"v{i - 1:03d}"], "produces": f"v{i:03d}",
        })
    final_var = f"v{n_expr - 1:03d}"
    steps.append({
        "step_id": "s_out_payable", "type": "output", "label": "Payable premium",
        "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
        "consumes": [final_var],
    })

    return {
        "slug": slug, "version": 1,
        "input_contract": input_contract,
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": steps,
        "sub_graphs": [],
    }


class _FakeResolver:
    """In-process resolver, shaped like `test_rating_score.py`'s own `_FakeResolver` —
    every pin is `"approved"`; this harness measures `score_one`, not the maturity gate."""

    def __init__(self, *, with_gbm: bool, n_expr: int, rounds: int, rows: int) -> None:
        slug = "bench-rating-gbm" if with_gbm else "bench-rating-no-gbm"
        self._payloads: dict[str, dict[str, Any]] = {
            f"rating_algorithm:{slug}@1": _algorithm_payload(with_gbm=with_gbm, n_expr=n_expr),
            "rate_table:bench-expense@1": _rate_table_payload(),
        }
        if with_gbm:
            booster_bytes = _train_booster(rows=rows, rounds=rounds)
            self._payloads["model:bench-freq@1"] = _gbm_model_payload(
                booster_bytes, rounds=rounds, rows=rows
            )

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        return ResolvedArtifact(status="approved", payload=self._payloads[str(ref)])


def _version(*, with_gbm: bool) -> RatingVersion:
    slug = "bench-rating-gbm" if with_gbm else "bench-rating-no-gbm"
    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": slug, "version": 1,
        "status": "draft", "dataset_version_id": str(uuid4()),
        # Never resolved by `compile_bundle` (it walks `pins`, not `model_ref` —
        # verified live in `packages/pricing-core/src/pricing_core/rating/compile.py`);
        # required by the schema regardless, so it is set to a well-formed ref even when
        # the algorithm itself has no `model_call` step.
        "model_ref": "model:bench-freq@1",
        "created_at": "2026-08-29T12:00:00Z", "created_by": str(uuid4()),
        "updated_at": "2026-08-29T12:00:00Z",
        "algorithm_ref": f"rating_algorithm:{slug}@1",
        "pins": {
            "rate_tables": ["rate_table:bench-expense@1"],
            "models": ["model:bench-freq@1"] if with_gbm else [],
            "reference_tables": [], "custom_objectives": [],
        },
        "model_reference_mode": "exact",
    })


async def _serialisable(*, with_gbm: bool, n_expr: int, rounds: int, rows: int) -> Bundle:
    """The `Bundle` *before* `load_bundle` — the artifact the blob store holds.

    Split out of `_compiled` for Task 2D: the full-path measurement must score the **same**
    bundle the component measurement scores, or the layer-by-layer subtraction that
    attributes latency between fetch, framework and `score_one` is comparing four numbers
    taken on four different fixtures.
    """
    resolver: ArtifactResolver = _FakeResolver(
        with_gbm=with_gbm, n_expr=n_expr, rounds=rounds, rows=rows
    )
    return await compile_bundle(_version(with_gbm=with_gbm), resolver)


async def _compiled(*, with_gbm: bool, n_expr: int, rounds: int, rows: int) -> CompiledBundle:
    bundle = await _serialisable(
        with_gbm=with_gbm, n_expr=n_expr, rounds=rounds, rows=rows
    )
    return load_bundle(bundle)


def _ctx() -> QuoteContext:
    from datetime import date, datetime

    inputs: dict[str, Any] = {"driver_age": 34, "channel": "direct"}
    rng = random.Random(20260829)
    inputs.update({name: rng.uniform(0.0, 1.0) for name in FEATURE_ORDER})
    return QuoteContext.model_validate({
        "purpose": "new_business",
        "quoted_at": datetime(2026, 8, 29, 12, 0, 0),
        "effective_date": date(2026, 9, 1),
        "inputs": inputs,
        "options": QuoteContextOptions(rating_version_ref=_RATING_VERSION_REF),
    })


# -- measurement -------------------------------------------------------------------------


def _percentile(samples: list[float], p: float) -> float:
    """`w8-spike-resolution.md`'s own convention: "p99 = the 990th sorted value" of 1000
    samples — ``sorted(samples)[int(len(samples) * p)]``."""
    ordered = sorted(samples)
    index = min(int(len(ordered) * p), len(ordered) - 1)
    return ordered[index]


@dataclass(frozen=True)
class Measurement:
    """A block of timed calls together with the load the box carried while it ran.

    The load is part of the measurement, not metadata about it: the same block of this
    harness has returned both a PASS and an OVER against NFR-RATE-1's 15 ms bound on this
    machine, and the load average is the variable that moved. A `Measurement` cannot be
    reported without its condition because the two travel together.
    """

    samples: list[float]
    load_start: float
    load_end: float

    @property
    def load_span(self) -> str:
        """`0.39` when the load held, `1.63 → 6.42` when it moved during the block."""
        if abs(self.load_end - self.load_start) < 0.005:
            return f"{self.load_start:.2f}"
        return f"{self.load_start:.2f} → {self.load_end:.2f}"


async def _measure(
    bundle: CompiledBundle, ctx: QuoteContext, *, trace: bool, warmup: int, iterations: int
) -> Measurement:
    """Sequential `await score_one(...)` calls on one event loop — a single-caller latency
    distribution, not a concurrency or throughput measurement (Task 1.4's own research note
    already covers `async_evaluate()`'s concurrency behaviour).

    The 1-minute load average is read either side of the timed block, so every reported
    figure carries the condition it was taken under rather than one startup reading shared
    by every block in the run.
    """
    for _ in range(warmup):
        await score_one(bundle, ctx, trace=trace)
    load_start = loadavg()
    samples: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        await score_one(bundle, ctx, trace=trace)
        samples.append((time.perf_counter() - start) * 1000)
    return Measurement(samples=samples, load_start=load_start, load_end=loadavg())


#: The ladder `_report` prints and `_ratio_ladder` compares across. Wide enough to show
#: whether an effect is distribution-wide or lives only in the tail — a ratio that holds
#: from p10 to p99 is multiplicative; one that appears only at p99 is a tail artifact, and
#: the p99 alone cannot tell them apart.
QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99)


async def _measure_abc(
    bundle: CompiledBundle, ctx: QuoteContext, *, warmup: int, iterations: int
) -> tuple[Measurement, Measurement, Measurement]:
    """Split traced overhead into the engine's share and ours, on the shipped code path.

    `score_one` evaluates and then calls `build_scoring_result(..., engine_trace)`, which
    gates `_build_trace` on that argument being non-`None`. Varying the two independently
    is what separates the costs:

      **A** untraced eval + `engine_trace=None`   — the baseline
      **B** *traced* eval + `engine_trace=None`   — engine-side share is **B - A**
      **C** traced eval + the trace              — our own share is **C - B**

    B is the load-bearing one: it pays for the engine to build and marshal the trace
    payload and then throws it away, so B - A is the cost of asking for a trace at all,
    before `_build_trace` copies anything.

    **Interleaved round-robin, reported at the median.** The three configurations are
    measured one call each per iteration rather than in three blocks, so drift on a shared
    machine hits all three equally instead of landing on whichever ran last. Absolute p99s
    cannot be compared across blocks minutes apart; interleaved medians can.
    """
    rating_version_ref = ctx.options.rating_version_ref if ctx.options is not None else None
    assert rating_version_ref is not None, "_ctx() must set options.rating_version_ref"
    context = {
        "effective_date": ctx.effective_date.isoformat(), "purpose": ctx.purpose, **ctx.inputs
    }

    async def one(*, trace: bool, keep_trace: bool) -> float:
        start = time.perf_counter()
        out = await bundle.decision.async_evaluate(context, {"trace": trace})
        build_scoring_result(
            bundle, ctx, rating_version_ref, out["result"],
            out.get("trace") if keep_trace else None,
        )
        return (time.perf_counter() - start) * 1000

    for _ in range(warmup):
        await one(trace=False, keep_trace=False)
        await one(trace=True, keep_trace=False)
        await one(trace=True, keep_trace=True)

    load_start = loadavg()
    a: list[float] = []
    b: list[float] = []
    c: list[float] = []
    for _ in range(iterations):
        a.append(await one(trace=False, keep_trace=False))
        b.append(await one(trace=True, keep_trace=False))
        c.append(await one(trace=True, keep_trace=True))
    load_end = loadavg()
    return tuple(  # type: ignore[return-value]
        Measurement(samples=s, load_start=load_start, load_end=load_end) for s in (a, b, c)
    )


def _report(label: str, run: Measurement, *, budget_ms: float | None) -> None:
    samples = run.samples
    mean = statistics.fmean(samples)
    stdev = statistics.pstdev(samples)
    print(f"\n{label} — {len(samples)} calls at 1-min load {run.load_span}")
    print(f"    mean {mean:7.3f} ms   stdev {stdev:6.3f} ms")
    ladder = "   ".join(
        f"p{int(q * 100)} {_percentile(samples, q):7.3f}" for q in QUANTILES
    )
    print(f"    min {min(samples):7.3f}   {ladder}   max {max(samples):7.3f}  (ms)")
    if budget_ms is not None:
        p99 = _percentile(samples, 0.99)
        verdict = "PASS" if p99 <= budget_ms else "OVER"
        print(
            f"    p99 {p99:.3f} ms / {budget_ms:.1f} ms budget — {verdict} "
            f"at 1-min load {run.load_span}"
        )


def _ratio_ladder(label: str, numerator: Measurement, denominator: Measurement) -> None:
    """Print the ratio at every quantile, not only at the one the budget names.

    NFR-RATE-2's overhead was reported at p99 alone, which cannot distinguish a cost that
    multiplies the whole distribution from one that only fattens the tail. If the ratios
    below are flat across the ladder the effect is multiplicative; if they climb, it is not.
    """
    print(f"\n{label}")
    cells = []
    for q in QUANTILES:
        num = _percentile(numerator.samples, q)
        den = _percentile(denominator.samples, q)
        cells.append(f"p{int(q * 100)} {num / den:5.2f}x" if den else f"p{int(q * 100)}   n/a")
    print("    " + "   ".join(cells))


# -- the full HTTP path at a sustained offered rate — W11 Slice 2 Task 2D ------------------
#
# Everything above measures `score_one` directly. NFR-RATE-1 says **"p99 < 50 ms server-side
# at 200 rps per replica"**, which is two clauses the section above cannot reach: it runs
# sequentially on one event loop, and it never enters the route. Both untested dimensions of
# the requirement are untested *by construction*, not by oversight.
#
# Ruling 6 reserved `asyncio` + `httpx` for exactly this measurement and drew its forbidden
# line at *load-generation dependencies* — `locust`/`k6`/`hey`/`wrk` in a `pyproject.toml`,
# `uv.lock`, CI workflow or setup instruction. `httpx` is already a workspace dependency.
#
# Reaching into `backend/src` is new for this file and is confined to this section: the
# component half above stays a `pricing-core` client (ADR-0001), and the full-path half
# cannot, because the backend's route is the thing under measurement.
# `scripts/generate-contracts.py:30` is the precedent for a script doing this.

#: Offered rates for the sweep. NFR-RATE-1 names 200; the rungs below it are why this is a
#: sweep rather than a point. A single measurement at 200 rps cannot separate "the code is
#: slow" from "the box saturates near here", and those have different owners. Latency
#: against offered rate has a knee, and **where the knee sits is the finding**.
RATE_RUNGS = (25, 50, 100, 150, 200)

#: Seconds of offered load per rung, after a warmup rung that is measured and discarded.
RUNG_SECONDS = 20


def _backend_on_path() -> None:
    """Put `backend/src` on `sys.path`, as `scripts/generate-contracts.py:30` does."""
    backend = str(Path(__file__).resolve().parent.parent / "backend" / "src")
    if backend not in sys.path:
        sys.path.insert(0, backend)


@dataclass(frozen=True)
class Rung:
    """One offered rate, with everything needed to read its result honestly.

    `offered` is what the generator scheduled; `achieved` is what it managed to issue. They
    diverge when the generator itself falls behind, which is a **void rung** rather than a
    slow server — the distinction the `load_*` fields exist to make, and the reason a rung
    carries its condition rather than being reported bare.
    """

    offered_rps: int
    achieved_rps: float
    samples: list[float]
    errors: int
    load_start: float
    load_end: float

    @property
    def load_span(self) -> str:
        if abs(self.load_end - self.load_start) < 0.005:
            return f"{self.load_start:.2f}"
        return f"{self.load_start:.2f} → {self.load_end:.2f}"

    @property
    def mean_ms(self) -> float:
        return statistics.fmean(self.samples) if self.samples else float("nan")

    def implied_ceiling_rps(self, speedup: float) -> float:
        """Capacity implied by **this rung's own** mean service time.

        A ceiling computed once from a prior quiet run is circular: mean service time rises
        with load, so the number needed to compute utilisation is the thing being measured.
        Recomputed per rung, the three readings separate — a mean that stays flat while the
        p99 blows up is tail behaviour in the code; a mean climbing toward the rung's own
        service budget is saturation; a mean climbing at a low offered rate means something
        else on the box is competing, and the rung is void.
        """
        mean_s = self.mean_ms / 1000.0
        return speedup / mean_s if mean_s > 0 else float("nan")


async def _seed(bundle: Bundle, *, dsn: str, bucket: str) -> tuple[str, str]:
    """Insert exactly what `POST /api/v1/score` reads, and return `(workspace_id, api_key)`.

    Deliberately **not** `compile_rating_version`: that path compiles from a stored
    `RatingAlgorithmRow` through the real resolver, which would need Model and RateTable rows
    and would produce a *different* bundle from the one the component half measured. The
    layer-by-layer subtraction below is only legitimate if every layer scores the same
    artifact, so the bundle is built once, in-process, and persisted as-is.

    `resolve_rating_version_ref` has no status predicate (`rating_versions.py:105-132`), so a
    `draft` row is scoreable and no submit/approve cycle is needed. `score:execute` is
    granted by no builtin role (FR-GOV-6), so the credential is a Service Account whose own
    `permissions` satisfy the check through Ruling 38's `credential_permissions` union.
    """
    _backend_on_path()
    from datetime import UTC, datetime, timedelta

    from pydantic import SecretStr

    from app.auth.api_keys import generate_key
    from app.config import Environment, Settings
    from app.db.models import ApiKeyRow, RatingVersionRow, ServiceAccountRow
    from app.db.session import Database
    from app.platform.blobs import BlobStore

    settings = Settings(
        environment=Environment.LOCAL,
        version="bench",
        database_url=SecretStr(dsn),
        blob_bucket=bucket,
    )
    database = Database(settings)
    blob_store = BlobStore(settings)
    await blob_store.ensure_bucket()

    workspace_id = uuid4()
    created_by = uuid4()
    payload = bundle.model_dump_json().encode()

    # One transaction: `BlobStore.put` refuses outside one, and the `blobs` row it adds must
    # commit with the `rating_versions` row that names it or the route resolves a key to
    # nothing.
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, payload, "application/json")
        session.add(
            RatingVersionRow(
                workspace_id=workspace_id,
                slug=_RATING_VERSION_REF.slug,
                version=_RATING_VERSION_REF.version,
                status="draft",
                dataset_version_id=uuid4(),
                model_ref="model:bench-freq@1",
                created_by=created_by,
                algorithm_ref=f"rating_algorithm:{_RATING_VERSION_REF.slug}@1",
                pins={
                    "rate_tables": [],
                    "models": [],
                    "reference_tables": [],
                    "custom_objectives": [],
                },
                bundle={
                    "content_hash": bundle.content_hash,
                    "bytes": len(payload),
                    "compiled_at": datetime.now(UTC).isoformat(),
                    "blob_sha256": ref.sha256,
                },
            )
        )

    generated = generate_key("uat")
    async with database.unit_of_work() as session:
        account = ServiceAccountRow(
            workspace_id=workspace_id,
            slug="bench-scorer",
            description=None,
            environments=["uat"],
            permissions=["score:execute"],
            rate_limit_rps=None,
        )
        session.add(account)
        await session.flush()
        session.add(
            ApiKeyRow(
                service_account_id=account.id,
                prefix=generated.prefix,
                secret_hash=generated.secret_hash,
                environment=generated.environment,
                expires_at=datetime.now(UTC) + timedelta(days=1),
            )
        )

    await database.dispose()
    print(f"  seeded workspace {workspace_id}, bundle blob {ref.sha256[:12]}…, "
          f"{len(payload):,} B")
    return str(workspace_id), generated.value


async def _measure_fetch(
    *, dsn: str, bucket: str, workspace_id: str, iterations: int
) -> Measurement:
    """`_fetch_bundle` alone — the per-request cost the slot does **not** avoid.

    `_compiled_for` (`api/score.py:181`) consults the slot only *after* `_fetch_bundle` has
    returned, because the slot is keyed on `content_hash` and the only way to learn a ref's
    content hash is to fetch the bundle. So every happy-path request pays two SELECTs, a full
    object read and `Bundle.model_validate_json` of the whole booster; the slot saves
    `load_bundle` and nothing else. The ref-to-hash memo that would break that circularity
    exists (Task 2A) but is reachable only from the `except Exception` degradation branch.
    Measured separately here so the full-path figure can be attributed rather than asserted.
    """
    _backend_on_path()
    from uuid import UUID

    from pydantic import SecretStr

    from app.api.score import _fetch_bundle
    from app.config import Environment, Settings
    from app.db.session import Database
    from app.platform.blobs import BlobStore

    settings = Settings(
        environment=Environment.LOCAL,
        version="bench",
        database_url=SecretStr(dsn),
        blob_bucket=bucket,
    )
    database = Database(settings)
    blob_store = BlobStore(settings)
    ws = UUID(workspace_id)

    for _ in range(20):
        await _fetch_bundle(database, blob_store, workspace_id=ws, ref=_RATING_VERSION_REF)
    load_start = loadavg()
    samples: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        await _fetch_bundle(database, blob_store, workspace_id=ws, ref=_RATING_VERSION_REF)
        samples.append((time.perf_counter() - start) * 1000)
    load_end = loadavg()
    await database.dispose()
    return Measurement(samples=samples, load_start=load_start, load_end=load_end)


def _serve(*, dsn: str, bucket: str, log_path: Path, port: int) -> Any:
    """`uvicorn app.main:create_app --factory` in its own process — one replica.

    A subprocess rather than an in-process ASGI transport because NFR-RATE-1 measures a
    *replica*, and an in-process server would have the load generator's own work competing
    for the same event loop and counting inside the latency it is trying to measure.
    `scripts/demo.py:237` launches it exactly this way.
    """
    import subprocess

    root = Path(__file__).resolve().parent.parent
    env = {
        **os.environ,
        "GIP_ENVIRONMENT": "local",
        "GIP_VERSION": "bench",
        "GIP_DATABASE_URL": dsn,
        "GIP_BLOB_BUCKET": bucket,
    }
    handle = log_path.open("wb")
    return subprocess.Popen(
        [
            "uv", "run", "uvicorn", "app.main:create_app", "--factory",
            "--host", "127.0.0.1", "--port", str(port),
            "--log-level", "warning", "--no-access-log",
        ],
        cwd=str(root),
        env=env,
        stdout=handle,
        stderr=subprocess.STDOUT,
    )


async def _await_ready(url: str, *, seconds: float = 60.0) -> None:
    import httpx

    deadline = time.perf_counter() + seconds
    async with httpx.AsyncClient(timeout=2.0) as client:
        while time.perf_counter() < deadline:
            try:
                if (await client.get(url)).status_code == 200:
                    return
            except Exception:
                pass
            await asyncio.sleep(0.25)
    raise RuntimeError(f"server did not become ready at {url} within {seconds:.0f}s")


async def _drive(
    url: str, headers: dict[str, str], body: dict[str, Any], *, rate: int, seconds: int
) -> Rung:
    """Issue requests on the clock at `rate`/s — **open loop**, and that is load-bearing.

    A closed-loop generator (N workers each looping request → await → request) throttles
    itself when the server slows: it issues fewer requests, and the ones that would have been
    slowest are never sent at all. That is coordinated omission, and its effect is to make a
    saturating system return a *passing* p99. At an offered rate near this box's measured
    ceiling that is not a theoretical risk, it is the likely outcome.

    NFR-RATE-1 also says "at 200 rps" — an **offered** rate, not an achieved one — so
    scheduling on the clock is the literal reading as well as the honest one. When the server
    cannot keep up, the queue grows and the tail records it, which is the signal wanted.
    """
    import httpx

    interval = 1.0 / rate
    total = rate * seconds
    samples: list[float] = []
    errors = 0

    limits = httpx.Limits(max_connections=1024, max_keepalive_connections=1024)
    async with httpx.AsyncClient(timeout=60.0, limits=limits) as client:

        async def one() -> None:
            nonlocal errors
            start = time.perf_counter()
            try:
                response = await client.post(url, json=body, headers=headers)
            except Exception:
                errors += 1
                return
            elapsed = (time.perf_counter() - start) * 1000
            if response.status_code == 200:
                samples.append(elapsed)
            else:
                errors += 1

        load_start = loadavg()
        begin = time.perf_counter()
        tasks: list[asyncio.Task[None]] = []
        for index in range(total):
            target = begin + index * interval
            delay = target - time.perf_counter()
            if delay > 0:
                await asyncio.sleep(delay)
            tasks.append(asyncio.create_task(one()))
        issued_for = time.perf_counter() - begin
        await asyncio.gather(*tasks)
        load_end = loadavg()

    return Rung(
        offered_rps=rate,
        achieved_rps=total / issued_for if issued_for > 0 else float("nan"),
        samples=samples,
        errors=errors,
        load_start=load_start,
        load_end=load_end,
    )


def _handler_ms(log_path: Path, *, path: str = "/api/v1/score") -> list[float]:
    """Server-side handler time, from the request middleware's own `duration_ms`.

    The app already logs one JSON line per completed request. Reading it costs no production
    change and gives the other half of the attribution: client round-trip minus handler time
    is queue wait plus loopback, which is what separates a slow handler from a saturated one.
    """
    import json

    out: list[float] = []
    for line in log_path.read_text(errors="replace").splitlines():
        if '"duration_ms"' not in line or path not in line:
            continue
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get("path") == path and record.get("status") == 200:
            out.append(float(record["duration_ms"]))
    return out


def _report_rung(rung: Rung, handler: list[float], *, budget_ms: float, speedup: float) -> None:
    if not rung.samples:
        print(f"  {rung.offered_rps:>4} rps — no successful responses ({rung.errors} errors)")
        return
    p99 = _percentile(rung.samples, 0.99)
    verdict = "PASS" if p99 < budget_ms else "OVER"
    handler_p99 = _percentile(handler, 0.99) if handler else float("nan")
    handler_mean = statistics.fmean(handler) if handler else float("nan")
    print(
        f"  {rung.offered_rps:>4} rps offered / {rung.achieved_rps:6.1f} issued  "
        f"load {rung.load_span:>13}  "
        f"mean {rung.mean_ms:7.3f}  p50 {_percentile(rung.samples, 0.50):7.3f}  "
        f"p99 {p99:8.3f} / {budget_ms:.0f} ms — {verdict}"
    )
    print(
        f"        handler mean {handler_mean:7.3f}  p99 {handler_p99:8.3f}   "
        f"queue+loopback at p99 {p99 - handler_p99:8.3f}   "
        f"implied ceiling {rung.implied_ceiling_rps(speedup):6.1f} rps   "
        f"errors {rung.errors}   n={len(rung.samples)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--warmup", type=int, default=WARMUP_CALLS)
    parser.add_argument("--iterations", type=int, default=MEASURED_CALLS)
    parser.add_argument("--expr-steps", type=int, default=N_EXPR_STEPS)
    parser.add_argument(
        "--rounds", type=int, default=300, help="XGBoost boosting rounds (Task 1.3's own "
        "NFR-RATE-4 fixture used 300)"
    )
    parser.add_argument("--rows", type=int, default=5_000, help="Synthetic training rows")
    parser.add_argument(
        "--abc-iterations", type=int, default=200,
        help="Rounds for the A/B/C decomposition. Each round runs all three "
             "configurations, so this costs roughly 3x its own count in calls; 200 is "
             "the count the PR #416 audit used.",
    )
    parser.add_argument(
        "--http", action="store_true",
        help="Task 2D: also measure the full route at a sustained offered rate. Needs the "
             "compose stack up (PostgreSQL and MinIO) and holds it exclusively.",
    )
    parser.add_argument(
        "--rates", default=",".join(str(r) for r in RATE_RUNGS),
        help="Comma-separated offered rates for the --http sweep.",
    )
    parser.add_argument("--rung-seconds", type=int, default=RUNG_SECONDS)
    parser.add_argument("--port", type=int, default=8099)
    parser.add_argument(
        "--speedup", type=float, default=2.10,
        help="Concurrent speedup used to turn a rung's mean service time into an implied "
             "ceiling. 2.10-2.25x measured in zen-evaluate-concurrency.md:65,:75 on this "
             "box; the low end is used so the implied ceiling is not flattered.",
    )
    parser.add_argument(
        "--dsn",
        default=os.environ.get(
            "GIP_TEST_DATABASE_URL",
            "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing",
        ),
    )
    parser.add_argument(
        "--bucket", default=os.environ.get("GIP_TEST_BUCKET", "gip-test-blobs")
    )
    args = parser.parse_args()

    print(f"machine: {machine()}")
    print(
        f"warmup {args.warmup} calls, measured {args.iterations} calls, "
        f"{args.expr_steps} chained expression steps"
    )

    ctx = _ctx()

    print("\ncompiling the with-GBM bundle (~200 steps, one exact model_call)...")
    bundle_gbm = asyncio.run(
        _compiled(with_gbm=True, n_expr=args.expr_steps, rounds=args.rounds, rows=args.rows)
    )
    step_count_gbm = len(bundle_gbm.algorithm.steps)
    print(f"  {step_count_gbm} steps, boosters loaded: {list(bundle_gbm.boosters)}")

    print("compiling the without-GBM bundle (~200 steps, no model_call)...")
    bundle_no_gbm = asyncio.run(
        _compiled(with_gbm=False, n_expr=args.expr_steps, rounds=args.rounds, rows=args.rows)
    )
    step_count_no_gbm = len(bundle_no_gbm.algorithm.steps)
    print(f"  {step_count_no_gbm} steps")

    run_gbm = asyncio.run(
        _measure(bundle_gbm, ctx, trace=False, warmup=args.warmup, iterations=args.iterations)
    )
    _report(
        f"NFR-RATE-1 with GBM ({step_count_gbm} steps, one exact model_call, trace=False)",
        run_gbm, budget_ms=BUDGET_WITH_GBM_P99_MS,
    )

    run_no_gbm = asyncio.run(
        _measure(
            bundle_no_gbm, ctx, trace=False, warmup=args.warmup, iterations=args.iterations
        )
    )
    _report(
        f"NFR-RATE-1 without GBM ({step_count_no_gbm} steps, trace=False)",
        run_no_gbm, budget_ms=BUDGET_WITHOUT_GBM_P99_MS,
    )

    run_traced = asyncio.run(
        _measure(bundle_gbm, ctx, trace=True, warmup=args.warmup, iterations=args.iterations)
    )
    _report(
        f"NFR-RATE-2 with GBM, trace=True ({step_count_gbm} steps)",
        run_traced, budget_ms=None,
    )

    p99_untraced = _percentile(run_gbm.samples, 0.99)
    p99_traced = _percentile(run_traced.samples, 0.99)
    overhead = (p99_traced - p99_untraced) / p99_untraced if p99_untraced else float("nan")
    verdict = "PASS" if overhead <= BUDGET_TRACE_OVERHEAD else "OVER"
    print(
        f"\nNFR-RATE-2 — trace overhead at p99: {p99_traced:.3f} ms vs {p99_untraced:.3f} ms "
        f"untraced = {overhead:+.1%} / {BUDGET_TRACE_OVERHEAD:.0%} budget — {verdict}"
    )
    # The two blocks being subtracted ran minutes apart. Naming both loads keeps a reader
    # from reading a difference in contention as a difference in tracing cost.
    print(
        f"    (traced block at 1-min load {run_traced.load_span}, untraced at "
        f"{run_gbm.load_span})"
    )
    mean_untraced = statistics.fmean(run_gbm.samples)
    mean_traced = statistics.fmean(run_traced.samples)
    mean_overhead = (mean_traced - mean_untraced) / mean_untraced if mean_untraced else float("nan")
    print(
        f"    (at the mean, informational only — the budget is stated at p99: "
        f"{mean_traced:.3f} ms vs {mean_untraced:.3f} ms untraced = {mean_overhead:+.1%})"
    )

    _ratio_ladder(
        "NFR-RATE-2 — traced / untraced at each quantile (flat = multiplicative and "
        "distribution-wide; climbing = a tail effect the p99 alone would misreport)",
        run_traced, run_gbm,
    )

    print(
        f"\ncompiling the A/B/C decomposition ({args.abc_iterations} interleaved rounds)..."
    )
    run_a, run_b, run_c = asyncio.run(
        _measure_abc(bundle_gbm, ctx, warmup=args.warmup, iterations=args.abc_iterations)
    )
    _report("A — untraced eval + engine_trace=None", run_a, budget_ms=None)
    _report("B — traced eval + engine_trace=None", run_b, budget_ms=None)
    _report("C — traced eval + the trace built", run_c, budget_ms=None)

    med_a, med_b, med_c = (statistics.median(r.samples) for r in (run_a, run_b, run_c))
    engine_side, ours = med_b - med_a, med_c - med_b
    added = engine_side + ours
    print(
        f"\nNFR-RATE-2 — where the added cost sits (medians, interleaved): "
        f"A {med_a:.3f} ms, B {med_b:.3f} ms, C {med_c:.3f} ms"
    )
    if added > 0:
        print(
            f"    engine-side (B-A) {engine_side:7.3f} ms = {engine_side / added:.1%}   "
            f"ours (C-B) {ours:7.3f} ms = {ours / added:.1%}   of {added:.3f} ms added"
        )
        print(
            "    'Ours' is `_build_trace`'s copying. 'Engine-side' is what asking for a "
            "trace costs before we touch it — the share that a payload change addresses."
        )

    if args.http:
        _run_http_sweep(args)

    print(f"\n1-minute load average at exit: {loadavg():.2f}")

    return 0


def _run_http_sweep(args: Any) -> None:
    """The full-path, sustained-rate half of NFR-RATE-1 — both GBM conditions.

    Each condition gets its own server process, its own seeded workspace and its own bundle,
    because the two have materially different capacity on this box and a shared ceiling would
    misattribute a breach on whichever half it did not come from.
    """
    import shutil
    import signal

    rates = [int(r) for r in str(args.rates).split(",") if r.strip()]
    logs = Path(__file__).resolve().parent.parent / ".bench-logs"
    if logs.exists():
        shutil.rmtree(logs)
    logs.mkdir()

    for with_gbm, budget in (
        (True, BUDGET_WITH_GBM_P99_MS),
        (False, BUDGET_WITHOUT_GBM_P99_MS),
    ):
        label = "with GBM" if with_gbm else "without GBM"
        print(f"\n=== NFR-RATE-1 full path, {label} (budget p99 < {budget:.0f} ms) ===")

        bundle = asyncio.run(
            _serialisable(
                with_gbm=with_gbm, n_expr=args.expr_steps, rounds=args.rounds, rows=args.rows
            )
        )
        workspace_id, api_key = asyncio.run(
            _seed(bundle, dsn=args.dsn, bucket=args.bucket)
        )

        fetch = asyncio.run(
            _measure_fetch(
                dsn=args.dsn, bucket=args.bucket, workspace_id=workspace_id, iterations=200
            )
        )
        _report(f"_fetch_bundle alone, {label} (every request pays this)", fetch,
                budget_ms=None)

        log_path = logs / f"server-{'gbm' if with_gbm else 'nogbm'}.log"
        proc = _serve(dsn=args.dsn, bucket=args.bucket, log_path=log_path, port=args.port)
        base = f"http://127.0.0.1:{args.port}"
        try:
            asyncio.run(_await_ready(f"{base}/healthz"))
            headers = {"X-API-Key": api_key, "Workspace-Id": workspace_id}
            body = json.loads(_ctx().model_dump_json())

            # A measured-and-discarded warmup rung: the first requests pay connection setup,
            # the empty bundle slot and the first `load_bundle`, none of which the steady
            # state pays. Reporting them would blend a cold cost into a warm figure, which is
            # the shape confusion the plan's own acceptance calls out.
            asyncio.run(_drive(f"{base}/api/v1/score", headers, body, rate=25, seconds=4))
            log_path.write_bytes(b"")

            for rate in rates:
                before = len(_handler_ms(log_path))
                rung = asyncio.run(
                    _drive(
                        f"{base}/api/v1/score", headers, body,
                        rate=rate, seconds=args.rung_seconds,
                    )
                )
                handler = _handler_ms(log_path)[before:]
                _report_rung(rung, handler, budget_ms=budget, speedup=args.speedup)
        finally:
            proc.send_signal(signal.SIGINT)
            try:
                proc.wait(timeout=20)
            except Exception:
                proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
