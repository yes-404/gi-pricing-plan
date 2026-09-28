"""The five FR-261 property classes as pure checks, and the run record they assemble.

Everything here is a function of a Quote Context, a compiled bundle's scores and a declared
`PropertyCheck` — no generator, no shrinker, no clock. `testing.run_regression` (which owns
`hypothesis`) and `replay.replay_cases` (which must never reach it) both call these, so a
property means the same thing when a run is made and when it is replayed (`PL-1205` Task 4,
RS-1176 condition 4). **This module never imports `hypothesis`.**

`monotone` is evaluated *ceteris paribus*: a case's other inputs are held fixed while the
named input is varied over a grid spanning the property's `lower`/`upper` (or, absent
those, the input contract's own `min`/`max`). Comparing premiums across random contexts
that differ in every input would test nothing about one input's effect.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from decimal import Decimal
from itertools import pairwise
from typing import Any

from model_schema.rating import InputContractField, RatingInputType
from model_schema.refs import ArtifactRef, BlobRef
from model_schema.regression import (
    CasesLog,
    GoldenQuoteResult,
    LadderReconciles,
    MonotoneInInput,
    NoNullOutput,
    PremiumBounded,
    PremiumPositive,
    PropertyCheck,
    PropertyResult,
    RegressionRun,
    RegressionSuite,
    RunGeneration,
    cases_log_bytes,
    cases_log_sha256,
)
from model_schema.scoring import QuoteContext, ScoringResult
from pricing_core.money import reconcile_ladder
from pricing_core.rating.runtime import CompiledBundle
from pricing_core.rating.score import _score_context_sync

__all__ = [
    "PROPERTY_FAILED",
    "Scorer",
    "build_run",
    "case_holds",
    "coerce_inputs",
    "make_scorer",
    "monotone_field",
    "payable_minor",
]

#: The code a failing property result carries (03 §4.9, `PROPERTY_ASSERTION_FAILED`).
PROPERTY_FAILED = "PROPERTY_ASSERTION_FAILED"

#: Points on a `monotone` grid, ends included.
_GRID_POINTS = 5

#: A scorer returns the result, or `None` when the engine refuses a context that satisfies
#: the input contract — which every check treats as a failure, never a pass.
Scorer = Callable[[QuoteContext], ScoringResult | None]

_PAYABLE_RUNG = "payable_premium"


def payable_minor(scored: ScoringResult) -> int | None:
    """The `payable_premium` rung's `value_minor` for a quoted result, else `None`."""
    if scored.outcome != "quoted":
        return None
    for rung in scored.premium_ladder:
        if rung.rung == _PAYABLE_RUNG:
            return rung.value_minor
    return None


def make_scorer(
    bundle: CompiledBundle,
    rating_version_ref: ArtifactRef,
    contract: Sequence[InputContractField],
) -> Scorer:
    """A memoising scorer on the synchronous `evaluate()` path (RL-868), as
    `evaluate_golden_quotes` uses. An engine refusal (`ValueError`, `RuntimeError`) is
    `None`; `NotImplementedError` — a genuinely undesigned case — propagates."""
    cache: dict[str, ScoringResult | None] = {}

    def score(context: QuoteContext) -> ScoringResult | None:
        prepared = coerce_inputs(contract, context)
        key = prepared.model_dump_json()
        if key not in cache:
            try:
                cache[key] = _score_context_sync(bundle, prepared, rating_version_ref)
            except NotImplementedError:
                raise
            except (ValueError, RuntimeError):
                cache[key] = None
        return cache[key]

    return score


def coerce_inputs(
    contract: Sequence[InputContractField], context: QuoteContext
) -> QuoteContext:
    """`decimal` inputs read back from JSON are strings; the engine path takes `Decimal`."""
    coerced = dict(context.inputs)
    for field in contract:
        value = coerced.get(field.name)
        if field.type is RatingInputType.DECIMAL and isinstance(value, str):
            coerced[field.name] = Decimal(value)
    return context.model_copy(update={"inputs": coerced})


def monotone_field(
    contract: Sequence[InputContractField], check: MonotoneInInput
) -> InputContractField:
    """The contract field a `monotone` names; `ValueError` naming it when it cannot be used."""
    field = next((f for f in contract if f.name == check.input), None)
    if field is None:
        raise ValueError(f"monotone names input {check.input!r}, absent from the input contract")
    if field.type not in (RatingInputType.INT, RatingInputType.DECIMAL):
        raise ValueError(f"monotone input {check.input!r} is {field.type.value}, not orderable")
    if _bounds(field, check) is None:
        raise ValueError(
            f"monotone input {check.input!r} has no range: declare `lower` and `upper`, or "
            "`min` and `max` on the input contract"
        )
    return field


def _bounds(field: InputContractField, check: MonotoneInInput) -> tuple[Decimal, Decimal] | None:
    low = Decimal(check.lower) if check.lower is not None else field.min
    high = Decimal(check.upper) if check.upper is not None else field.max
    if low is None or high is None:
        return None
    return Decimal(low), Decimal(high)


def _grid(field: InputContractField, check: MonotoneInInput) -> list[Any]:
    bounds = _bounds(field, check)
    assert bounds is not None  # `monotone_field` refused otherwise
    low, high = bounds
    points = [low + (high - low) * i / (_GRID_POINTS - 1) for i in range(_GRID_POINTS)]
    if field.type is RatingInputType.INT:
        return sorted({int(p) for p in points})
    return sorted({p.quantize(Decimal("0.01")) for p in points})


def _monotone_holds(
    check: MonotoneInInput,
    field: InputContractField,
    context: QuoteContext,
    score: Scorer,
) -> bool:
    premiums: list[int] = []
    for value in _grid(field, check):
        scored = score(context.model_copy(update={"inputs": {**context.inputs, field.name: value}}))
        if scored is None:
            return False
        premium = payable_minor(scored)
        if premium is not None:
            premiums.append(premium)
    pairs = list(pairwise(premiums))
    if check.direction == "increasing":
        return all(a < b if check.strict else a <= b for a, b in pairs)
    return all(a > b if check.strict else a >= b for a, b in pairs)


def case_holds(
    check: PropertyCheck,
    context: QuoteContext,
    score: Scorer,
    contract: Sequence[InputContractField],
) -> bool:
    """Whether one Quote Context satisfies one property; a declined quote is vacuous where
    the property speaks of a premium."""
    if isinstance(check, MonotoneInInput):
        return _monotone_holds(check, monotone_field(contract, check), context, score)
    scored = score(context)
    if scored is None:
        return False
    if isinstance(check, PremiumPositive):
        premium = payable_minor(scored)
        return premium is None or premium > 0
    if isinstance(check, NoNullOutput):
        return all(value is not None for value in scored.outputs.values())
    if isinstance(check, LadderReconciles):
        steps: list[tuple[str, int]] = [
            (rung.rung, rung.value_minor) for rung in scored.premium_ladder
        ]
        risk = next((value for rung, value in steps if rung == "risk_premium"), None)
        return reconcile_ladder(risk if risk is not None else 0, steps) if steps else True
    assert isinstance(check, PremiumBounded)
    premium = payable_minor(scored)
    if premium is None:
        return True
    return (check.lower_minor is None or premium >= check.lower_minor) and (
        check.upper_minor is None or premium <= check.upper_minor
    )


def build_run(
    *,
    suite: RegressionSuite,
    bundle_hash: str,
    rating_version_ref: ArtifactRef,
    started_at: Any,
    finished_at: Any,
    generation: RunGeneration,
    cases: CasesLog,
    golden_results: list[GoldenQuoteResult],
    property_results: list[PropertyResult],
) -> RegressionRun:
    """Assemble the run; `cases_blob` is the case log's content address, computed here
    (pure), and `job_id` stays `None` for the backend to set."""
    passed = all(g.status == "pass" for g in golden_results) and all(
        p.status == "pass" for p in property_results
    )
    return RegressionRun(
        suite_ref=ArtifactRef(type="regression_suite", slug=suite.slug, version=suite.version),
        suite_content_hash=suite.content_hash,
        rating_version_ref=rating_version_ref,
        bundle_hash=bundle_hash,
        started_at=started_at,
        finished_at=finished_at,
        overall="pass" if passed else "fail",
        generation=generation,
        cases_blob=BlobRef(
            sha256=cases_log_sha256(cases),
            bytes=len(cases_log_bytes(cases)),
            media_type="application/json",
        ),
        golden_results=golden_results,
        property_results=property_results,
    )
