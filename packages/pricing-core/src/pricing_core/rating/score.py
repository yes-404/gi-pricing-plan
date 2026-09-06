"""`score_one` on `async_evaluate()` (03 §3.7/§3.8, FR-250/254/255/256/258/273/218/252,
NFR-491/495/496/501, WK-671 Task 1.4).

**RL-868, not re-argued here.** The real-time path is built directly on
`CompiledBundle.decision.async_evaluate()` — never `evaluate()` plus a thread-pool
offload, measured twice to be strictly worse than doing nothing
(`docs/research/zen-evaluate-concurrency.md`). `score_one` is therefore `async def`;
`score_batch` (Slice 3, `03` §5.2, WK-671 Task 3A) stays plain `def` and drives
`CompiledBundle.decision.evaluate()`, the engine's synchronous path — see "What
`score_batch` is, and what it deliberately does not do", below.

## Three design choices this module resolves — two flagged findings from Task 1.3, and
## one found while building this task's own test suite

**1. Recovering *why* a `model_call` failed.** `zen`'s binding swallows whatever a
`customHandler` raises, replacing it with a generic `RuntimeError` that discards the
original code and message (verified live in Task 1.3, `runtime.py`'s docstrings).
`pricing_core.rating.runtime._model_call_handler` no longer raises at all: it returns a
sentinel key (`runtime.MODEL_CALL_ERROR_KEY`) in its own `output`, which — because
`passThrough` merges a node's whole returned dict forward — reaches `async_evaluate()`'s
`result` as ordinary data, with no exception anywhere in the path. `score_one` checks for
that key immediately after evaluating and raises `MODEL_CALL_FAILED` with the *real*
captured message. A mutable side-channel (the docstring's other suggested design) was
considered and rejected: `CompiledBundle` is held once and scored many times, including
*concurrently* (this module's own concurrency smoke test runs many `score_one` calls
against one shared `CompiledBundle` via `asyncio.gather`, and `async_evaluate`'s own
throughput gain comes from releasing the GIL during native execution) — a slot shared by
every call through the same handler closure would race the moment two quotes hit a
failing `model_call` at once, and nothing in this codebase has verified which OS thread a
`customHandler` callback actually runs on. The sentinel travels through the same
per-call-isolated mechanism every other produced value already uses.

**2. `predict_glm` is not called from a real Bundle today, and that is confirmed correct,
not a bug this task fixes.** `Bundle.resolved_payloads` carries a GLM's own dump but not
the `Factor`/`Banding`/`Grouping` objects `predict_glm` structurally requires — a genuine
gap `runtime.py`'s `_model_call_failure` docstring already names, refusing the quote with
`MODEL_CALL_FAILED` rather than silently mis-scoring it. Building real `Factor` resolution
into `Bundle.resolved_payloads` is a resolver-level (Task 1.2) or Bundle-shape change, out
of Task 1.4's scope (`score_one` takes an already-compiled `CompiledBundle` and cannot
retroactively enrich what it was built from) — this module's own tests exercise the GBM
path and rely on the already-tested GLM refusal (`test_rating_runtime.py`), rather than
re-proving it.

**3. A `set_param`/`predict()` race inside XGBoost, found by this task's own concurrency
smoke test, not assumed away.** `predict_gbm`'s first cut (this task) called
`Booster.set_param({"nthread": 1})` on every prediction, including against the
**already-loaded**, **shared** booster `CompiledBundle.boosters` holds. Running many
concurrent `score_one` calls against one bundle reproduced a real crash —
`XGBoostError: Check failed: !this->need_configuration_` — XGBoost's own assertion against
reconfiguring a `Booster` while a `predict()` on that *same object* is in flight from
another call. Fixed by moving `nthread`'s application into
`pricing_core.modelling.gbm.load_gbm_booster`, called once by `runtime.py`'s
`_load_boosters` at hydration time — synchronously, before any concurrent scoring begins;
`predict_gbm`'s own `nthread` now applies via `set_param` only
when it performs the load itself (a fresh, unshared `Booster`), and is a documented no-op
against an already-loaded one. See `gbm.py`'s `predict_gbm`/`load_gbm_booster` docstrings
for the full mechanism. Named here because it is exactly the class of bug RL-868's own
"instrumented default, not a closed question" warned about — an untested assumption about
what runs safely under real concurrency — and this one would not have been caught without
building the concurrency smoke test Task 1.4's own acceptance criteria require.

## Ladder construction — a documented convention, not a `03` mandate

`03` names the ladder's fixed rung sequence and the reconciliation property (FR-247/248)
but does not name a mechanism for deriving it from an arbitrary `RatingAlgorithm` graph —
verified by a full sweep of §3/§4 for a "rung" field on any step type; there is none.
This module adopts one, stated here because a future reader must not mistake it for a
requirement. **The starting fact, verified live and not assumed: an `output`-type step is
never a wire node at all.** `to_wire` handles `input`/`output` steps separately from every
other type (Step 3, rule 2) and only `RatingOutputStep`'s presence is checked, by
`RatingAlgorithm._graph_invariants`, for "every declared output has an output step" — the
engine never computes a value under the step's own `output_name`. Task 1.3's own fixture
already relies on this: its `output` step declares `output_name="payable_premium_minor"`
but `consumes=["office_premium_minor"]`, two different strings, and nothing on the wire
ever produces the first one directly. So:

- **A rung is present when the algorithm declares a `RatingOutputStep` whose
  `output_name == f"{rung}_minor"`.** That step's single `consumes` name is where the
  rung's *raw* value actually lives in the evaluated result (an `expression`, `table`, or
  `model_call` step's own `produces`); its `RoundSpec` is the rung's declared rounding
  (FR-226 — read, never defaulted, when a step exists to declare it). An algorithm
  opts a rung into the ladder by adding this one small step; omitting it means the rung is
  simply absent, exactly as an algorithm not implementing an optional loading should be.
- **`constraints` is always synthesised, never read from its own key.** It carries forward
  whatever the immediately preceding present rung settled on (a clamp already overrode
  that rung's own value in place — see `runtime._constraint_node`), annotated with every
  firing clamp's `reason_code` in `operation.applied`, matching `03:412`'s worked example
  (`{"kind": "none", "applied": []}` when nothing fired).
- **The operation `kind` per rung is a fixed table** (`_MULTIPLY_RUNGS`, `_ADD_RUNGS`
  below), matching `03:404-414`'s own worked example: expense/commission/profit/
  optimisation/instalment loadings are relativities (`multiply`); IPT and fees is a flat
  amount (`add`); the terminal rung is the algorithm's own declared rounding (`round`). A
  rung whose raw value is unchanged from the previous present rung is `none` — a
  checkpoint, not a computation (`office_premium` and `constraints`, ordinarily) — *unless*
  its value differs, in which case it degrades to `multiply` so a simpler algorithm that
  skips the named loading rungs still reconciles correctly.
- **The recorded `factor`/`amount_minor` is derived from the ratio or delta between
  consecutive present rungs, quantized to 4 decimal places, and then *reapplied* via
  `pricing_core.money.apply_factor`/addition to produce `value_minor`.** This is
  deliberate and important: `value_minor` is the *output* of applying the recorded
  operation, never an independently-sourced number the operation is asked to explain after
  the fact — so the ladder reconciles **by construction**, to the penny, and not merely
  according to `reconcile_ladder`'s own (shallow — first-rung and int-ness only) check.

**`on_violation="error"` is deliberately left undesigned, matching `runtime.to_wire`'s own
precedent.** `03-rating-engine.md`'s constraint-step table row names three modes but
defines `error`'s operational semantics no further than the word itself — verified by a
full sweep of §3/§4 for prose distinguishing it from `decline`; there is none, and no Task
1.4 acceptance criterion exercises it. A *firing* `on_violation="error"` step raises
`NotImplementedError` naming the gap, the same choice `runtime.to_wire` already made for a
`constraint` step's whole translation before this task, and for `interpolation="linear"`
still today — inventing a disposition here would silently answer a `CLAUDE.md` §0 question
this module has no authority to decide. A step *declaring* `on_violation="error"` that
never fires scores normally; only a firing one raises.

## What `score_batch` is, and what it deliberately does not do

**`score_batch` (WK-671 Task 3A) reuses `build_scoring_result` below** — the shared tail that
turns one already-evaluated engine `result` into a `ScoringResult` — after its own
row-by-row, **synchronous** evaluation of the same compiled graph (`bundle.decision.
evaluate()`, never `async_evaluate()` — RL-868). It also reuses `score_one`'s own
pre-evaluation checks (`_validate_inputs`, `_check_purpose_mount`, `_check_billing_surface`)
and its engine-failure translation (`_reraise_engine_failure`), unmodified, so the two
paths diverge nowhere except the method used to reach the engine — which is exactly what
FR-254's byte-identity proves is safe to diverge on.

**The frame contract `score_batch` reads and writes is this task's own design** — `03`
§5.2 fixes the function's signature (`bundle`, `frame`, `chunk_rows`, `progress`) but not
a row schema, and no precedent exists anywhere in this repository for one (Verified facts,
the plan's own). **Input row**, one column per reserved key below plus one column per
name in `bundle.algorithm.input_contract` (extra columns are tolerated, exactly as
`_validate_inputs` already tolerates extra `ctx.inputs` keys):

- `quote_id` (nullable) — FR-253's "quote key". Carried straight into the output row;
  never read off `ScoringResult`, which has no such field (RL-857 §3).
- `purpose` — one of `QuotePurpose`'s five members.
- `effective_date` — an ISO date string.
- `rating_version_ref` — the canonical `ArtifactRef` string (`"{type}:{slug}@{version}"`).
  Constant for one `score_batch` call in practice (one call scores against one compiled
  `bundle`), but read per row rather than taken as a fifth keyword argument, so the
  signature above stays exactly what `03` publishes — widening it was ruled out (the plan's
  own "Do not widen this signature").

**Output row** carries `quote_id`, `outcome` — one of `ScoringOutcome`'s own three members
(`model_schema.scoring.ScoringOutcome = Literal["quoted", "declined", "error"]`; `"error"` is
a contract member already, not a batch-only invention — `_score_batch_row` is simply the
first caller to produce it), `rating_version_ref`, `bundle_hash`, the premium ladder and the
selected outputs each **pre-serialised to JSON** (`_ladder_json`/`_outputs_json` below —
this is what Task 3A's byte-identity test compares: the *serialised* ladder, not a
polars-native nested column), `decline_reasons`, and — populated only on an `"error"`
row — `error_code`/`error_message`. The handler (Task 3B) reassembles the final parquet
from this, and aggregates `error_code` into FR-255's per-category counts and samples;
neither is this task's to build. The full column set, its dtypes and the two `ScoringResult`
fields it deliberately excludes are published at `03` §4.8 — a cross-module data contract,
not only this docstring (RL-923).

**One failing row does not raise out of `score_batch`.** Everything `_validate_inputs`,
`_check_purpose_mount`, `_check_billing_surface` and the engine itself can raise for a row
is a `ValueError` (the `_raise_named` convention) or, from `_reraise_engine_failure`'s
final `raise exc`, a bare untyped `RuntimeError` — both are caught per row and turned into
an `"error"` output row rather than aborting the chunk, which is the structural half of
FR-255 ("does not abort on individual failures") that a chunked transform has to
provide regardless of who is charged with the requirement id; **the threshold policy that
decides whether the *run* aborts is explicitly not built here** (3B's). **`NotImplementedError`
is deliberately excluded from that catch** — it is a Python subclass of `RuntimeError`, but
it marks a genuinely undesigned case (an `on_violation="error"` constraint firing, or a
non-zero-dp output step) that `score_one` does not catch either; catching it here would
silently paper over a design gap `CLAUDE.md` §0 reserves for a spec change, not a batch
row.

**Chunking is an eager loop wrapped in `.lazy()` at the end, not genuine polars
streaming.** `frame.slice(offset, chunk_rows).collect()` per chunk, `bundle.decision.
evaluate()` has no vectorised form to exploit, and there is no `scan_parquet` precedent in
this repository for the input side to stream from either (Verified facts). `progress.
check_cancelled()` is checked once per chunk boundary, before that chunk's rows are
scored — a signalled cancellation therefore lets `JobCancelled` propagate having scored
every *complete* chunk before it and none after, matching every other `check_cancelled()`
call site in this package (`modelling/*.py`): the exception is not caught here: cooperative
cancellation is a hand-off to whichever caller can make the platform-level Job transition
(FR-401), and `pricing-core` cannot import what makes it durable (ADR-703).
"""

from __future__ import annotations

import json
import re
import time
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import Any, NoReturn

import polars as pl

from model_schema.rating import (
    RatingAlgorithm,
    RatingConstraintStep,
    RatingInputType,
    RatingLookupStep,
    RatingOutputStep,
    RatingTableStep,
)
from model_schema.refs import ArtifactRef
from model_schema.scoring import (
    LadderOperation,
    LadderRung,
    LadderRungName,
    QuoteContext,
    QuoteContextOptions,
    ScoringOutcome,
    ScoringResult,
    Trace,
    TraceStep,
)
from pricing_core.money import ROUNDING_MODES, RoundingMode, apply_factor, reconcile_ladder
from pricing_core.progress import ProgressCallback
from pricing_core.rating.runtime import MODEL_CALL_ERROR_KEY, CompiledBundle

__all__ = ["build_scoring_result", "score_batch", "score_one"]

#: FR-247/252's fixed rung sequence — `scoring.schema.json`'s own `LadderRung.rung`
#: enum order, which post-dates and supersedes FR-247's prose order by adding
#: `instalment_loading` (FR-252). The ladder's order is fixed by the platform; it is
#: never derived from an algorithm's own step order.
_RUNG_ORDER: tuple[LadderRungName, ...] = (
    "risk_premium",
    "expense_loading",
    "commission",
    "profit_loading",
    "office_premium",
    "optimisation_adjustment",
    "constraints",
    "instalment_loading",
    "ipt_and_fees",
    "payable_premium",
)

#: See the module docstring's "Ladder construction" note for why these two sets exist and
#: what a rung outside them defaults to.
_MULTIPLY_RUNGS = frozenset(
    {
        "expense_loading", "commission", "profit_loading",
        "optimisation_adjustment", "instalment_loading",
    }
)
_ADD_RUNGS = frozenset({"ipt_and_fees"})

_DEFAULT_ROUND_MODE: RoundingMode = "half_even"
_DEFAULT_ROUND_DP = 0

#: FR-252's second refusal: a `QuoteContext` asking for a payment schedule, an APR
#: figure or a credit-agreement term is refused, never answered approximately. `03` names
#: no wire shape for "asking", so this is a documented, provisional convention: any of
#: these reserved keys present (regardless of value) in `ctx.inputs` triggers the refusal.
_BILLING_SURFACE_KEYS = frozenset(
    {"payment_schedule", "apr", "credit_agreement_term", "instalment_schedule", "instalment_count"}
)

_ELAPSED_UNITS: tuple[tuple[str, float], ...] = (
    ("µs", 1.0), ("us", 1.0), ("ms", 1_000.0), ("ns", 0.001), ("s", 1_000_000.0),
)

#: `score_batch`'s own frame contract (module docstring, "What `score_batch` is"). Every
#: other column in an input row is an algorithm input, forwarded into `ctx.inputs`
#: verbatim — the same tolerance `_validate_inputs` already gives extra `QuoteContext`
#: keys.
_BATCH_RESERVED_COLUMNS = frozenset({"quote_id", "purpose", "effective_date", "rating_version_ref"})

#: `score_batch`'s output row schema, fixed so an empty chunk and a scored chunk always
#: concatenate cleanly (`pl.concat` requires matching dtypes, not just matching names).
#: `polars`' own stubs do not export a top-level name for "a dtype or a dtype class"
#: (`DataTypeClass` is a deprecated, unstubbed top-level attribute), so this stays `Any`
#: rather than fighting the third-party surface for a nine-entry constant.
_BATCH_OUTPUT_COLUMNS: list[tuple[str, Any]] = [
    ("quote_id", pl.Utf8),
    ("outcome", pl.Utf8),
    ("rating_version_ref", pl.Utf8),
    ("bundle_hash", pl.Utf8),
    ("premium_ladder_json", pl.Utf8),
    ("outputs_json", pl.Utf8),
    ("decline_reasons", pl.List(pl.Utf8)),
    ("error_code", pl.Utf8),
    ("error_message", pl.Utf8),
]
_BATCH_OUTPUT_SCHEMA: pl.Schema = pl.Schema(_BATCH_OUTPUT_COLUMNS)

#: `ScoringResult`'s own fields, mapped to the batch output column that carries them, or
#: named on the exclusion list (`03` §4.8, RL-923 §4). A field of `ScoringResult` that is
#: neither a value in this mapping nor in `_SCORING_RESULT_BATCH_EXCLUDED_FIELDS` has
#: appeared with no batch column to carry it — the drift `test_rating_score_batch.py`'s own
#: guard exists to catch (`CLAUDE.md` §2: "a shape defined twice will diverge").
_SCORING_RESULT_TO_BATCH_COLUMN: dict[str, str] = {
    "outcome": "outcome",
    "rating_version_ref": "rating_version_ref",
    "bundle_hash": "bundle_hash",
    "premium_ladder": "premium_ladder_json",
    "outputs": "outputs_json",
    "decline_reasons": "decline_reasons",
}

#: The two `ScoringResult` fields a batch run has no use for: `trace` (batch takes no
#: sampling parameter — RL-890 — and `score_batch` never requests an engine trace, so
#: this is always `None`) and `timing_ms` (per-call wall-clock timing that means nothing
#: aggregated across a chunk, and `score_batch` does not set it the way `score_one` does).
_SCORING_RESULT_BATCH_EXCLUDED_FIELDS = frozenset({"trace", "timing_ms"})


def _raise_named(code: str, message: str) -> NoReturn:
    """`pricing-core`'s established convention (`compile.py`'s `_raise_named`): a
    code-named bare `ValueError`, never `PlatformError` — `pricing-core` cannot import
    `app` (`.importlinter`'s `core-has-no-infrastructure`). RL-877: the mapping to a
    `PlatformError` at the backend boundary is Slice 2's."""
    raise ValueError(f"{code}: {message}")


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else [value]


def _as_decimal(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


# ---------------------------------------------------------------------------
# FR-255 category 1: contract violation.
# ---------------------------------------------------------------------------


def _validate_inputs(algorithm: RatingAlgorithm, inputs: Mapping[str, Any]) -> None:
    """FR-213/255: every declared input is present (unless nullable), typed, in range,
    and — for `enum` — in the declared domain. Extra keys `ctx.inputs` carries beyond the
    algorithm's own `input_contract` are tolerated; this checks only what the algorithm
    declares."""
    for field in algorithm.input_contract:
        value = inputs.get(field.name)
        if value is None:
            if not field.nullable:
                _raise_named(
                    "INPUT_CONTRACT_VIOLATION",
                    f"input {field.name!r} is required (FR-213)",
                )
            continue

        if field.type == RatingInputType.BOOL:
            if not isinstance(value, bool):
                _raise_named("INPUT_CONTRACT_VIOLATION", f"input {field.name!r} must be bool")
            continue
        if field.type == RatingInputType.INT:
            if not isinstance(value, int) or isinstance(value, bool):
                _raise_named("INPUT_CONTRACT_VIOLATION", f"input {field.name!r} must be int")
        elif field.type == RatingInputType.DECIMAL:
            if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
                _raise_named("INPUT_CONTRACT_VIOLATION", f"input {field.name!r} must be numeric")
        elif field.type == RatingInputType.STRING:
            if not isinstance(value, str):
                _raise_named("INPUT_CONTRACT_VIOLATION", f"input {field.name!r} must be a string")
            if field.pattern is not None and re.fullmatch(field.pattern, value) is None:
                _raise_named(
                    "INPUT_CONTRACT_VIOLATION",
                    f"input {field.name!r}={value!r} does not match {field.pattern!r}",
                )
        elif field.type == RatingInputType.DATE and not isinstance(value, str):
            _raise_named(
                "INPUT_CONTRACT_VIOLATION", f"input {field.name!r} must be a date string"
            )
        elif (
            field.type == RatingInputType.ENUM
            and field.domain is not None
            and value not in field.domain
        ):
            _raise_named(
                "INPUT_CONTRACT_VIOLATION",
                f"input {field.name!r}={value!r} is not in {field.domain!r}",
            )

        if field.type in (RatingInputType.INT, RatingInputType.DECIMAL) and not isinstance(
            value, bool
        ):
            if field.min is not None and _as_decimal(value) < _as_decimal(field.min):
                _raise_named(
                    "INPUT_CONTRACT_VIOLATION",
                    f"input {field.name!r}={value!r} is below the declared minimum {field.min!r}",
                )
            if field.max is not None and _as_decimal(value) > _as_decimal(field.max):
                _raise_named(
                    "INPUT_CONTRACT_VIOLATION",
                    f"input {field.name!r}={value!r} is above the declared maximum {field.max!r}",
                )


def _check_purpose_mount(algorithm: RatingAlgorithm, ctx: QuoteContext) -> None:
    """FR-218: a `purpose` requiring the MTA/cancellation sub-graph refuses rather than
    pricing as new business when this Rating Version mounts none.

    `algorithm.sub_graphs` non-empty is a documented, provisional stand-in for "this
    version mounts the sub-graph *this purpose* needs": sub-graph inlining
    (`SubGraphRef.mount_point` resolution, `compile_bundle`'s own TODO) is not built by any
    slice yet, so no rating version can meaningfully mount one today — checking for
    *any* mounted sub-graph is therefore a conservative, forward-safe approximation: it
    refuses everything a truthful check would refuse today, and a real future algorithm
    that does mount its MTA sub-graph will have a non-empty list, satisfying it correctly
    without this function needing to know the mount point's name.
    """
    if ctx.purpose in ("mid_term_adjustment", "cancellation") and not algorithm.sub_graphs:
        _raise_named(
            "INPUT_CONTRACT_VIOLATION",
            f"purpose={ctx.purpose!r} requires a mounted sub-graph (FR-218), and this "
            "rating version's algorithm mounts none — refused rather than priced as new "
            "business, which FR-218 names as the failure this refusal exists to "
            "prevent",
        )


def _check_billing_surface(ctx: QuoteContext) -> None:
    """FR-252's second half: refused, not answered approximately."""
    requested = sorted(_BILLING_SURFACE_KEYS & ctx.inputs.keys())
    if requested:
        _raise_named(
            "INPUT_CONTRACT_VIOLATION",
            f"{requested} asks for a payment schedule, an APR figure or a credit "
            "agreement term (FR-252) — refused rather than answered approximately",
        )


# ---------------------------------------------------------------------------
# FR-255 categories 2/3/5, and RL-875's decline representation.
# ---------------------------------------------------------------------------


def _check_model_call_sentinel(result: Mapping[str, Any]) -> None:
    """The other half of `runtime._model_call_failure`'s design: raise the *real* captured
    message, never the engine's own generic wrapper."""
    if MODEL_CALL_ERROR_KEY in result:
        raise ValueError(str(result[MODEL_CALL_ERROR_KEY]))


def _check_lookup_misses(algorithm: RatingAlgorithm, result: Mapping[str, Any]) -> None:
    """FR-255 categories 2/3: a `table`/`lookup` step with `on_miss="error"` whose
    `produces` name did not survive evaluation found no matching row — verified live
    (`docs/research/` spike, this task) that a `decisionTableNode` miss simply omits its
    declared output rather than signalling one, so a post-evaluation presence check is the
    only place this can be caught."""
    for step in algorithm.steps:
        if isinstance(step, RatingTableStep) and step.on_miss == "error":
            for name in _as_list(step.produces):
                if str(name) not in result:
                    _raise_named(
                        "RATE_TABLE_MISS",
                        f"table step {step.step_id!r} found no matching row (FR-255)",
                    )
        elif isinstance(step, RatingLookupStep) and step.on_miss == "error":
            for name in _as_list(step.produces):
                if str(name) not in result:
                    _raise_named(
                        "REFERENCE_LOOKUP_MISS",
                        f"lookup step {step.step_id!r} found no matching row (FR-255)",
                    )


def _reraise_engine_failure(algorithm: RatingAlgorithm, exc: RuntimeError) -> NoReturn:
    """A finding, not merely a fallback: a `table`/`lookup` miss whose `produces` name is
    then referenced by a downstream `expression` step crashes `async_evaluate()` itself
    (the engine's own "undefined variable" `NodeError`) **before any `result` is
    returned**, so `_check_lookup_misses`'s ordinary post-evaluation presence check never
    gets to run — verified live, reproduced by this module's own test suite. `model_call`
    failures no longer reach here at all (they are sentinelled — see the module
    docstring), so by the time this is called the cause is, with high confidence, exactly
    this: an unguarded on_miss='error' table/lookup step. This is reported as the
    corresponding typed code with the original engine error preserved in the message
    (rather than a bare re-raise of an untyped `RuntimeError`, which would violate
    FR-255's "typed" requirement), and it is honest about being an inference: a
    correctness gap for a later slice to close by making the wire translation itself
    fail gracefully, not by parsing engine error strings more cleverly.
    """
    has_table_miss = any(
        isinstance(s, RatingTableStep) and s.on_miss == "error" for s in algorithm.steps
    )
    has_lookup_miss = any(
        isinstance(s, RatingLookupStep) and s.on_miss == "error" for s in algorithm.steps
    )
    if has_table_miss or has_lookup_miss:
        code = "RATE_TABLE_MISS" if has_table_miss else "REFERENCE_LOOKUP_MISS"
        _raise_named(
            code,
            "the engine failed evaluating a downstream step, most likely because an "
            f"on_miss='error' step found no matching row and a later expression "
            f"referenced its output (FR-255); original engine error: {exc}",
        )
    raise exc


def _apply_constraints(
    algorithm: RatingAlgorithm, result: Mapping[str, Any]
) -> tuple[list[str], list[str]]:
    """RL-875: the whole DAG has already evaluated (no early exit exists to build) — this
    reads every constraint step's `{step_id}__violated` flag and returns
    `(decline_reasons, clamp_reason_codes)`. `on_violation="error"` firing raises
    `NotImplementedError` — see the module docstring."""
    decline_reasons: list[str] = []
    clamp_reason_codes: list[str] = []
    for step in algorithm.steps:
        if not isinstance(step, RatingConstraintStep):
            continue
        if not bool(result.get(f"{step.step_id}__violated", False)):
            continue
        if step.on_violation == "decline":
            decline_reasons.append(step.reason_code)
        elif step.on_violation == "clamp":
            clamp_reason_codes.append(step.reason_code)
        else:
            raise NotImplementedError(
                f"constraint step {step.step_id!r} fired with on_violation='error' "
                f"(reason_code={step.reason_code!r}). 03-rating-engine.md's constraint-step "
                "table row names this mode but does not define its operational semantics "
                "beyond the word 'errors' — undesigned rather than guessed at, matching "
                "runtime.to_wire's own precedent for genuinely unspecified business logic."
            )
    return decline_reasons, clamp_reason_codes


# ---------------------------------------------------------------------------
# The premium ladder (FR-247/248, NFR-496) — see the module docstring.
# ---------------------------------------------------------------------------


def _round_minor(raw: float, mode: RoundingMode) -> int:
    """`Decimal(repr(raw))`, never `Decimal(raw)` — the latter exposes the float's exact
    binary expansion (`Decimal(1.15)` is `1.1499999999999999...`), which is not what
    FR-273's "integer minor unit" crossing means. `repr()` is Python's own
    shortest-round-trip form, which is what the engine's float64 arithmetic actually meant
    to produce (Task 1.3 measured the cross-implementation noise at ~2e-13 relative,
    utterly negligible against one minor unit)."""
    return int(Decimal(repr(raw)).quantize(Decimal(1), rounding=ROUNDING_MODES[mode]))


def _output_steps_by_name(algorithm: RatingAlgorithm) -> dict[str, RatingOutputStep]:
    return {
        step.output_name: step for step in algorithm.steps if isinstance(step, RatingOutputStep)
    }


def _build_ladder(
    algorithm: RatingAlgorithm, result: Mapping[str, Any], clamp_reason_codes: Sequence[str]
) -> tuple[list[LadderRung], dict[str, int]]:
    """Returns `(rungs, value_minor_by_rung)` — the second lets `_build_outputs` reuse a
    rung's already-rounded value rather than re-deriving it from `result`."""
    output_steps = _output_steps_by_name(algorithm)
    rungs: list[LadderRung] = []
    by_rung: dict[str, int] = {}
    prev_minor: int | None = None

    for rung in _RUNG_ORDER:
        if rung == "constraints":
            if prev_minor is None:
                continue
            rungs.append(
                LadderRung(
                    rung="constraints",
                    value_minor=prev_minor,
                    operation=LadderOperation(kind="none", applied=list(clamp_reason_codes)),
                )
            )
            by_rung["constraints"] = prev_minor
            continue

        step = output_steps.get(f"{rung}_minor")
        if step is None:
            continue
        if step.rounding.dp != 0:
            raise NotImplementedError(
                f"output step {step.step_id!r} (rung {rung!r}) declares dp="
                f"{step.rounding.dp}; score_one only builds an integer-minor-unit ladder "
                "(dp=0)"
            )
        source = _as_list(step.consumes)
        if not source:
            raise NotImplementedError(
                f"output step {step.step_id!r} (rung {rung!r}) consumes nothing to report"
            )
        source_key = str(source[0])
        if source_key not in result:
            continue
        raw = float(result[source_key])
        mode: RoundingMode = step.rounding.mode

        if prev_minor is None:
            value_minor = _round_minor(raw, mode)
            operation = None
        elif rung == "payable_premium":
            value_minor = _round_minor(raw, mode)
            operation = LadderOperation(kind="round", mode=mode, dp=_DEFAULT_ROUND_DP)
        elif prev_minor == 0:
            value_minor = _round_minor(raw, mode)
            operation = LadderOperation(kind="add", amount_minor=value_minor - prev_minor)
        elif rung in _ADD_RUNGS:
            target = _round_minor(raw, mode)
            amount = target - prev_minor
            value_minor = prev_minor + amount
            operation = LadderOperation(kind="add", amount_minor=amount)
        elif rung in _MULTIPLY_RUNGS or _round_minor(raw, mode) != prev_minor:
            factor = (Decimal(repr(raw)) / Decimal(prev_minor)).quantize(Decimal("0.0001"))
            value_minor = apply_factor(prev_minor, factor, mode)
            operation = LadderOperation(
                kind="multiply", factor=str(factor), mode=mode, dp=_DEFAULT_ROUND_DP
            )
        else:
            value_minor = prev_minor
            operation = LadderOperation(kind="none")

        rungs.append(LadderRung(rung=rung, value_minor=value_minor, operation=operation))
        by_rung[rung] = value_minor
        prev_minor = value_minor

    return rungs, by_rung


def _build_outputs(
    algorithm: RatingAlgorithm, result: Mapping[str, Any], by_rung: Mapping[str, int]
) -> dict[str, Any]:
    """`ScoringResult.outputs` — one entry per `AlgorithmOutput`. A name that is also a
    ladder rung (`f"{rung}_minor"`) reuses the ladder's own once-rounded value, so the two
    structures never disagree by a rounding difference; anything else is read straight
    from the evaluated `result` via its output step's `consumes` name."""
    output_steps = _output_steps_by_name(algorithm)
    outputs: dict[str, Any] = {}
    for declared in algorithm.outputs:
        step = output_steps.get(declared.name)
        if step is None:
            continue
        rung_name = declared.name.removesuffix("_minor")
        if rung_name in by_rung:
            outputs[declared.name] = by_rung[rung_name]
            continue
        source = _as_list(step.consumes)
        if source and str(source[0]) in result:
            outputs[declared.name] = result[str(source[0])]
    return outputs


# ---------------------------------------------------------------------------
# FR-258: the trace.
# ---------------------------------------------------------------------------


def _parse_elapsed_us(performance: str) -> int:
    """`'4.2µs'` -> `4` — `Trace.steps[].elapsed_us` is an integer (`scoring.schema.json`);
    the engine's own `performance` is a formatted string (Verified facts item 4), parsed
    here, never passed through. Order matters: `ns`/`µs`/`us`/`ms` are checked before the
    bare `s` suffix they would otherwise also match."""
    performance = performance.strip()
    for suffix, to_us in _ELAPSED_UNITS:
        if performance.endswith(suffix):
            try:
                return max(0, int(float(performance[: -len(suffix)]) * to_us))
            except ValueError:
                return 0
    return 0


def _build_trace(
    algorithm: RatingAlgorithm,
    engine_trace: Mapping[str, Any],
    rating_version_ref: ArtifactRef,
    bundle_hash: str,
    quote_id: str | None,
    ladder_reconciled: bool,
) -> Trace:
    step_meta = {step.step_id: step for step in algorithm.steps}
    entries = sorted(engine_trace.values(), key=lambda entry: entry.get("order", 0))
    steps: list[TraceStep] = []
    for entry in entries:
        step = step_meta.get(entry.get("id"))
        if step is None:  # the synthetic input/output wire nodes, not an algorithm step
            continue
        output = entry.get("output") or {}
        violation: dict[str, object] | None = None
        violated_flag = bool(output.get(f"{step.step_id}__violated", False))
        if isinstance(step, RatingConstraintStep) and violated_flag:
            violation = {"reason_code": step.reason_code, "on_violation": step.on_violation}
        trace_data = entry.get("traceData")
        steps.append(
            TraceStep(
                step_id=step.step_id,
                type=step.type,
                label=step.label,
                consumed=dict(entry.get("input") or {}),
                produced=dict(output),
                matched=trace_data if isinstance(trace_data, dict) else None,
                violation=violation,
                elapsed_us=_parse_elapsed_us(str(entry.get("performance", "0"))),
            )
        )
    return Trace(
        rating_version_ref=rating_version_ref,
        bundle_hash=bundle_hash,
        quote_id=quote_id,
        steps=steps,
        ladder_reconciled=ladder_reconciled,
    )


# ---------------------------------------------------------------------------
# The shared tail (FR-254) and score_one itself.
# ---------------------------------------------------------------------------


def build_scoring_result(
    bundle: CompiledBundle,
    ctx: QuoteContext,
    rating_version_ref: ArtifactRef,
    result: Mapping[str, Any],
    engine_trace: Mapping[str, Any] | None,
) -> ScoringResult:
    """Turn one already-evaluated engine `result` (and, optionally, its `trace`) into a
    `ScoringResult`. The shared step evaluator FR-254 requires — see the module
    docstring's "What this module deliberately does not build". `timing_ms` is not set
    here; callers own their own timing (`score_one` sets it after this returns, via
    `model_copy`, since `ScoringResult` is frozen).
    """
    _check_model_call_sentinel(result)
    _check_lookup_misses(bundle.algorithm, result)
    decline_reasons, clamp_reason_codes = _apply_constraints(bundle.algorithm, result)

    ladder, by_rung = _build_ladder(bundle.algorithm, result, clamp_reason_codes)
    outputs = _build_outputs(bundle.algorithm, result, by_rung)

    ladder_steps: list[tuple[str, int]] = [(rung.rung, rung.value_minor) for rung in ladder]
    risk_premium_minor = ladder_steps[0][1] if ladder_steps else 0
    ladder_reconciled = reconcile_ladder(risk_premium_minor, ladder_steps)

    trace_obj: Trace | None = None
    if engine_trace is not None:
        trace_obj = _build_trace(
            bundle.algorithm, engine_trace, rating_version_ref, bundle.content_hash,
            ctx.quote_id, ladder_reconciled,
        )

    outcome: ScoringOutcome = "declined" if decline_reasons else "quoted"
    return ScoringResult(
        outcome=outcome,
        rating_version_ref=rating_version_ref,
        bundle_hash=bundle.content_hash,
        premium_ladder=ladder,
        outputs=outputs,
        decline_reasons=decline_reasons,
        trace=trace_obj,
        timing_ms={},
    )


async def score_one(
    bundle: CompiledBundle, ctx: QuoteContext, *, trace: bool = False
) -> ScoringResult:
    """The real-time evaluator (FR-250), built on `async_evaluate()` (RL-868).

    **`ctx.options.rating_version_ref` is required.** Slice 1 builds no default-live
    resolution (DP1, Slice 2's), so `score_one` has nothing else to populate
    `ScoringResult.rating_version_ref` — a contract-required field — from: `Bundle`/
    `CompiledBundle` carry an `algorithm_ref` and a `content_hash`, never a rating
    *version*'s own identity. A caller (Slice 2's HTTP layer, or a test) resolves the
    version and fills in `ctx.options.rating_version_ref` before calling this.

    NFR-491: performs no I/O of its own — every value it reads comes from `bundle`
    (already hydrated, no cache, no database, no network — `load_bundle`'s own
    guarantee) and `ctx` (already-parsed data). `pricing-core` cannot import a database or
    network client at all (`.importlinter`'s `core-has-no-infrastructure`), so this is
    enforced at the import level as well as behaviourally.
    """
    t_start = time.perf_counter()
    algorithm = bundle.algorithm

    _validate_inputs(algorithm, ctx.inputs)
    _check_purpose_mount(algorithm, ctx)
    _check_billing_surface(ctx)

    rating_version_ref = ctx.options.rating_version_ref if ctx.options is not None else None
    if rating_version_ref is None:
        _raise_named(
            "INPUT_CONTRACT_VIOLATION",
            "ctx.options.rating_version_ref is required — Slice 1 builds no default-live "
            "resolution (DP1, Slice 2), so score_one cannot guess which version it is "
            "scoring against",
        )

    context = {
        "effective_date": ctx.effective_date.isoformat(), "purpose": ctx.purpose, **ctx.inputs
    }

    t_eval = time.perf_counter()
    try:
        out = await bundle.decision.async_evaluate(context, {"trace": trace})
    except RuntimeError as exc:
        _reraise_engine_failure(algorithm, exc)
    eval_ms = (time.perf_counter() - t_eval) * 1000

    scored = build_scoring_result(
        bundle, ctx, rating_version_ref, out["result"], out.get("trace") if trace else None,
    )
    total_ms = (time.perf_counter() - t_start) * 1000
    return scored.model_copy(update={"timing_ms": {"total": total_ms, "evaluate": eval_ms}})


# ---------------------------------------------------------------------------
# `score_batch` (WK-671 Task 3A). See the module docstring, "What `score_batch` is, and what
# it deliberately does not do", for the frame contract and the design decisions below.
# ---------------------------------------------------------------------------


def _ladder_json(ladder: Sequence[LadderRung]) -> str:
    """The canonical serialised form Task 3A's byte-identity criterion compares. Each
    `LadderRung`'s own `model_dump_json()` — deterministic given the same field values, the
    same way every other byte-identity precedent in this repository (`test_blobs.py`,
    `test_data_nfrs.py`) compares stored bytes against freshly serialised ones rather than
    inventing a bespoke comparison."""
    return "[" + ",".join(rung.model_dump_json() for rung in ladder) + "]"


#: `AlgorithmOutput.type` names shapes this serialiser knows how to write losslessly
#: (FR-227). Anything else is refused rather than stringified — RL-923 §5(i): a
#: silent `default=str` catch-all put a `Decimal` output and an `int` output in the same
#: JSON column with no way to tell which was which by reading the text back.
_KNOWN_OUTPUT_TYPES = frozenset({"money_minor", "decimal", "bool", "string", "date"})


def _coerce_output_value(declared_type: str, value: Any) -> int | str | bool:
    """One declared output value -> its canonical, JSON-lossless form, by the algorithm's
    own declared `type` (FR-227) rather than by the value's incidental Python type —
    `_build_outputs` (unmodified, per the module docstring) hands back whatever the engine's
    raw evaluated result happened to be, which for a `decimal`-typed non-rung output is a
    Python `float` today (verified: nothing converts it, the same way `_build_ladder`'s own
    `raw = float(result[source_key])` treats every non-money-minor engine value as untyped
    until something here gives it a type). `money_minor` values already arrive as `int`
    (`_round_minor`, ladder-derived) and are checked, not re-derived. `decimal` values are
    converted via `Decimal(repr(value))` — `_round_minor`'s own established idiom in this
    module, `repr()` rather than the raw float constructor, because `Decimal(1.15)` exposes
    the float's exact binary expansion — and serialised as a **string**, never a JSON
    number: `CLAUDE.md` §7, money is integer minor units or `Decimal`, never float, and a
    JSON number column cannot distinguish an exact `Decimal` from a lossy `float`."""
    if declared_type not in _KNOWN_OUTPUT_TYPES:
        raise ValueError(f"score_batch: cannot serialise a declared output type {declared_type!r}")
    if declared_type == "money_minor":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(
                f"score_batch: a money_minor output must be int, got {type(value).__name__}"
            )
        return value
    if declared_type == "decimal":
        as_decimal = value if isinstance(value, Decimal) else Decimal(repr(value))
        return str(as_decimal)
    if declared_type == "bool":
        if not isinstance(value, bool):
            raise ValueError(
                f"score_batch: a bool output must be bool, got {type(value).__name__}"
            )
        return value
    if declared_type in ("string", "date"):
        if not isinstance(value, str):
            raise ValueError(
                f"score_batch: a {declared_type} output must be str, "
                f"got {type(value).__name__}"
            )
        return value
    raise AssertionError(f"unreachable: {declared_type!r} is in _KNOWN_OUTPUT_TYPES with no branch")


def _outputs_json(algorithm: RatingAlgorithm, outputs: Mapping[str, Any]) -> str:
    """`ScoringResult.outputs` -> a JSON object, total over every declared output type this
    module recognises (`_KNOWN_OUTPUT_TYPES`) and refusing — never silently stringifying —
    anything else, so a type this function does not know about fails loudly instead of
    reaching `05` FR-317's A/E computation as data of an unknown shape (RL-923 §5(i))."""
    declared_types = {output.name: output.type for output in algorithm.outputs}
    coerced: dict[str, int | str | bool] = {}
    for name, value in outputs.items():
        declared_type = declared_types.get(name)
        if declared_type is None:
            raise ValueError(f"score_batch: output {name!r} is not declared on the algorithm")
        coerced[name] = _coerce_output_value(declared_type, value)
    return json.dumps(coerced)


def _batch_error_code(exc: Exception) -> tuple[str, str]:
    """Parse the `_raise_named` convention (`f"{code}: {message}"`) back into its parts, so
    an `"error"` output row carries the same typed code FR-255 names — `test_worker.py`
    and `runtime.py`'s `MODEL_CALL_FAILED` sentinel both already follow it. An exception
    that does not (should not occur for anything this catches, but a fallback is cheap and
    honest) is reported under its own class name rather than mis-parsed."""
    message = str(exc)
    code, sep, rest = message.partition(": ")
    if sep and code.replace("_", "").isalnum() and code == code.upper():
        return code, rest
    return type(exc).__name__, message


def _row_to_ctx(row: Mapping[str, Any]) -> QuoteContext:
    """One input row -> the identical `QuoteContext` shape `score_one`'s own checks expect.
    `quoted_at` is not read by anything downstream of this call (`build_scoring_result`'s
    `ScoringResult` has no such field, and `score_batch` never requests an engine trace —
    RL-890 — so `_build_trace` is never reached); it is derived from `effective_date` at
    midnight only because `QuoteContext` requires *some* value, never because batch scoring
    means anything by it."""
    effective_date = date.fromisoformat(row["effective_date"])
    inputs = {k: v for k, v in row.items() if k not in _BATCH_RESERVED_COLUMNS}
    rating_version_ref = ArtifactRef.model_validate(row["rating_version_ref"])
    return QuoteContext(
        quote_id=row.get("quote_id"),
        purpose=row["purpose"],
        quoted_at=datetime.combine(effective_date, datetime.min.time()),
        effective_date=effective_date,
        inputs=inputs,
        options=QuoteContextOptions(rating_version_ref=rating_version_ref),
    )


def _score_batch_row(bundle: CompiledBundle, row: Mapping[str, Any]) -> dict[str, Any]:
    """Score one row, reusing `score_one`'s own pre-checks and `build_scoring_result`
    unmodified (the module docstring's "What `score_batch` is"). Never lets a `ValueError`
    (the `_raise_named` convention) or the untyped `RuntimeError` `_reraise_engine_failure`
    can re-raise escape past this row — an `"error"` output row instead, which is the
    structural half of FR-255 a chunked transform has to provide regardless of who is
    charged with the requirement id. `NotImplementedError` (a `RuntimeError` subclass) is
    deliberately let through: it marks a genuinely undesigned case `score_one` does not
    catch either, not a per-quote data error."""
    quote_id = row.get("quote_id")
    rating_version_ref_str = row.get("rating_version_ref")
    algorithm = bundle.algorithm
    try:
        ctx = _row_to_ctx(row)
        _validate_inputs(algorithm, ctx.inputs)
        _check_purpose_mount(algorithm, ctx)
        _check_billing_surface(ctx)

        context = {
            "effective_date": ctx.effective_date.isoformat(), "purpose": ctx.purpose, **ctx.inputs
        }
        try:
            out = bundle.decision.evaluate(context)
        except RuntimeError as exc:
            _reraise_engine_failure(algorithm, exc)

        assert ctx.options is not None
        assert ctx.options.rating_version_ref is not None
        scored = build_scoring_result(
            bundle, ctx, ctx.options.rating_version_ref, out["result"], None,
        )
    except NotImplementedError:
        raise
    except (ValueError, RuntimeError) as exc:
        code, message = _batch_error_code(exc)
        return {
            "quote_id": quote_id,
            "outcome": "error",
            "rating_version_ref": rating_version_ref_str,
            "bundle_hash": bundle.content_hash,
            "premium_ladder_json": None,
            "outputs_json": None,
            "decline_reasons": [],
            "error_code": code,
            "error_message": message,
        }

    return {
        "quote_id": quote_id,
        "outcome": scored.outcome,
        "rating_version_ref": rating_version_ref_str,
        "bundle_hash": scored.bundle_hash,
        "premium_ladder_json": _ladder_json(scored.premium_ladder),
        "outputs_json": _outputs_json(algorithm, scored.outputs),
        "decline_reasons": list(scored.decline_reasons),
        "error_code": None,
        "error_message": None,
    }


def _score_batch_chunk(bundle: CompiledBundle, chunk: pl.DataFrame) -> pl.DataFrame:
    rows = [_score_batch_row(bundle, row) for row in chunk.iter_rows(named=True)]
    return pl.DataFrame(rows, schema=_BATCH_OUTPUT_SCHEMA)


def score_batch(
    bundle: CompiledBundle,
    frame: pl.LazyFrame,
    *,
    chunk_rows: int = 100_000,
    progress: ProgressCallback | None = None,
) -> pl.LazyFrame:
    """Re-rate every row of `frame` against `bundle` (FR-253/254, `03` §5.2). A pure,
    chunked transform: it takes a frame and returns a frame, holds no durable state across
    or within calls, and reaches the identical `build_scoring_result` tail `score_one` does
    (RL-858) — see the module docstring for the frame contract and every design decision
    below.

    **This is not genuine polars streaming.** `bundle.decision.evaluate()` has no vectorised
    form, so each chunk is collected eagerly (`frame.slice(offset, chunk_rows).collect()`),
    scored row by row, and the concatenated result is wrapped in `.lazy()` only to satisfy
    the published return type — there is no `scan_parquet` precedent in this repository for
    the input side to stream from either (Verified facts, the plan's own).

    **Resumability, an output location, a Job identity and an abort threshold are not
    here** (Rulings 31 §3/§5) — `score_batch` may not acquire any of them, and
    `.importlinter`'s `core-has-no-infrastructure` makes that structural. The `score.batch`
    handler (Task 3B) owns all four.
    """
    if chunk_rows < 1:
        raise ValueError(f"score_batch: chunk_rows must be >= 1, got {chunk_rows}")

    total_rows = frame.select(pl.len()).collect().item()
    if total_rows == 0:
        return pl.DataFrame(schema=_BATCH_OUTPUT_SCHEMA).lazy()

    scored_chunks: list[pl.DataFrame] = []
    rows_done = 0
    chunk_index = 0
    while rows_done < total_rows:
        if progress is not None:
            progress.check_cancelled()

        chunk = frame.slice(rows_done, chunk_rows).collect()
        scored_chunks.append(_score_batch_chunk(bundle, chunk))
        rows_done += chunk.height
        chunk_index += 1

        if progress is not None:
            progress.update(
                rows_done / total_rows, "scoring",
                rows_scored=rows_done, chunk_index=chunk_index,
            )

    return pl.concat(scored_chunks).lazy()
