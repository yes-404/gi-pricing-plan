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
    ResolvedArtifact,
    compile_bundle,
)
from pricing_core.rating.runtime import CompiledBundle, load_bundle  # noqa: E402
from pricing_core.rating.score import score_one  # noqa: E402

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


async def _compiled(*, with_gbm: bool, n_expr: int, rounds: int, rows: int) -> CompiledBundle:
    resolver: ArtifactResolver = _FakeResolver(
        with_gbm=with_gbm, n_expr=n_expr, rounds=rounds, rows=rows
    )
    bundle = await compile_bundle(_version(with_gbm=with_gbm), resolver)
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


def _report(label: str, run: Measurement, *, budget_ms: float | None) -> None:
    samples = run.samples
    p50, p90, p99 = (_percentile(samples, p) for p in (0.50, 0.90, 0.99))
    mean = statistics.fmean(samples)
    stdev = statistics.pstdev(samples)
    print(f"\n{label} — {len(samples)} calls at 1-min load {run.load_span}")
    print(
        f"    mean {mean:7.3f} ms   stdev {stdev:6.3f} ms   "
        f"p50 {p50:7.3f} ms   p90 {p90:7.3f} ms   p99 {p99:7.3f} ms   max {max(samples):7.3f} ms"
    )
    if budget_ms is not None:
        verdict = "PASS" if p99 <= budget_ms else "OVER"
        print(
            f"    p99 {p99:.3f} ms / {budget_ms:.1f} ms budget — {verdict} "
            f"at 1-min load {run.load_span}"
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
    print(f"\n1-minute load average at exit: {loadavg():.2f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
