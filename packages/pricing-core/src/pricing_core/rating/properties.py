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

import random
from collections.abc import Callable, Sequence
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from typing import Any, NamedTuple

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
    "NO_COMPARABLE_PAIRS",
    "PROPERTY_FAILED",
    "Scorer",
    "UnsweepableProperty",
    "build_run",
    "case_holds",
    "coerce_inputs",
    "counterexample_points",
    "make_scorer",
    "monotone_field",
    "monotone_grid",
    "monotone_has_comparable_pair",
    "monotone_sweep",
    "payable_minor",
]

class UnsweepableProperty(ValueError):  # noqa: N818 - named in 03 section 5.2
    """A `monotone` property whose input or range cannot be swept: absent from the input
    contract, not orderable, no range, empty after the contract's own bounds, or no two-place
    decimal value. The one exception the platform maps to `REGRESSION_PROPERTY_INVALID`; it
    names an input and a range, never a Quote Context (NFR-499)."""


#: The code a failing property result carries (03 §4.9, `PROPERTY_ASSERTION_FAILED`).
PROPERTY_FAILED = "PROPERTY_ASSERTION_FAILED"

#: A `monotone` whose every sweep had fewer than two quoted points compared nothing (DP-S3-7).
NO_COMPARABLE_PAIRS = "MONOTONE_NO_COMPARABLE_PAIRS"

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
        raise UnsweepableProperty(
            f"monotone names input {check.input!r}, absent from the input contract"
        )
    if field.type not in (RatingInputType.INT, RatingInputType.DECIMAL):
        raise UnsweepableProperty(
            f"monotone input {check.input!r} is {field.type.value}, not orderable"
        )
    if _bounds(field, check) is None:
        raise UnsweepableProperty(
            f"monotone input {check.input!r} has no range: declare `lower` and `upper`, or "
            "`min` and `max` on the input contract"
        )
    _swept_range(field, check)  # refuses an empty or unquantisable range, by name
    return field


def _bounds(field: InputContractField, check: MonotoneInInput) -> tuple[Decimal, Decimal] | None:
    """The property's range intersected with the contract's own (`min`, `max`), or `None`
    when neither the property nor the contract gives one end."""
    lows = [b for b in (Decimal(check.lower) if check.lower is not None else None, field.min)
            if b is not None]
    highs = [b for b in (Decimal(check.upper) if check.upper is not None else None, field.max)
             if b is not None]
    if not lows or not highs:
        return None
    return max(Decimal(b) for b in lows), min(Decimal(b) for b in highs)


def _swept_range(field: InputContractField, check: MonotoneInInput) -> tuple[Any, Any]:
    """The lowest and highest value a sweep can take, on the input's own lattice (integers,
    or cents), refusing by name a range with none: empty after the intersection, or with no
    two-place decimal value between its ends."""
    bounds = _bounds(field, check)
    assert bounds is not None  # `monotone_field` refused otherwise
    low, high = bounds
    if field.type is RatingInputType.INT:
        lo, hi = int(low.to_integral_value(ROUND_CEILING)), int(high.to_integral_value(ROUND_FLOOR))
        if lo > hi:
            raise UnsweepableProperty(
                f"monotone input {field.name!r}: the range {low}..{high} is empty"
            )
        return lo, hi
    cent = Decimal("0.01")
    lo_c = low.quantize(cent, rounding=ROUND_CEILING)
    hi_c = high.quantize(cent, rounding=ROUND_FLOOR)
    if lo_c > hi_c:
        raise UnsweepableProperty(
            f"monotone input {field.name!r}: no two-place decimal value between {low} and {high}"
            " (the range is empty)"
        )
    return lo_c, hi_c


#: The sampled points added to the uniform grid, fixed here and recorded as the run's `grid`
#: kind; the seed is the suite's, so a replay reproduces exactly the same points.
_SAMPLED_POINTS = 5


def monotone_grid(field: InputContractField, check: MonotoneInInput, seed: int) -> list[Any]:
    """The values a `monotone` sweep visits: a uniform grid of `_GRID_POINTS` points, bounds
    included, plus `_SAMPLED_POINTS` points drawn from `random.Random` seeded by the suite's
    seed and the input's name (stable across processes), all inside the bounds, sorted.

    **Weaker than band edges** (DP-S3-6): the bundle pins no Banding, so no edge is known
    and an inversion narrower than the spacing between these points may not be detected.
    """
    lo, hi = _swept_range(field, check)
    rng = random.Random(f"{seed}:{field.name}")
    if field.type is RatingInputType.INT:
        uniform = [lo + (hi - lo) * i // (_GRID_POINTS - 1) for i in range(_GRID_POINTS)]
        sampled = [rng.randint(lo, hi) for _ in range(_SAMPLED_POINTS)]
        return sorted(set(uniform) | set(sampled))
    cent = Decimal("0.01")
    cents = int((hi - lo) / cent)
    uniform_d = [lo + (cents * i // (_GRID_POINTS - 1)) * cent for i in range(_GRID_POINTS)]
    sampled_d = [lo + rng.randint(0, cents) * cent for _ in range(_SAMPLED_POINTS)]
    return sorted(set(uniform_d) | set(sampled_d))


class MonotoneSweep(NamedTuple):
    """One base context swept over the grid: the first adjacent quoted pair that breaks the
    property (`None` if none does), and how many quoted points were compared."""

    broken_at: tuple[Any, Any] | None
    quoted_points: int


def monotone_sweep(
    check: MonotoneInInput,
    field: InputContractField,
    context: QuoteContext,
    score: Scorer,
    seed: int,
) -> MonotoneSweep:
    """Sweep `context` over the grid; compare each quoted point with the next quoted point,
    across any declined gap (DP-S3-7 (b)), exactly in integer minor units (FR-273)."""
    previous: tuple[Any, int] | None = None
    quoted = 0
    for value in monotone_grid(field, check, seed):
        scored = score(context.model_copy(update={"inputs": {**context.inputs, field.name: value}}))
        if scored is None:
            return MonotoneSweep((value, value), quoted)
        premium = payable_minor(scored)
        if premium is None:
            continue
        quoted += 1
        if previous is not None:
            a, b = previous[1], premium
            if check.direction == "increasing":
                ok = a < b if check.strict else a <= b
            else:
                ok = a > b if check.strict else a >= b
            if not ok:
                return MonotoneSweep((previous[0], value), quoted)
        previous = (value, premium)
    return MonotoneSweep(None, quoted)


def monotone_has_comparable_pair(
    check: MonotoneInInput,
    contract: Sequence[InputContractField],
    contexts: Sequence[QuoteContext],
    score: Scorer,
    seed: int,
) -> bool:
    """Whether at least one base sweep compared two quoted points. When none did, the
    property compared nothing and must not pass (DP-S3-7)."""
    field = monotone_field(contract, check)
    return any(
        monotone_sweep(check, field, c, score, seed).quoted_points >= 2 for c in contexts
    )


def case_holds(
    check: PropertyCheck,
    context: QuoteContext,
    score: Scorer,
    contract: Sequence[InputContractField],
    *,
    seed: int,
    outputs: Sequence[str] = (),
) -> bool:
    """Whether one Quote Context satisfies one property; a declined quote is vacuous where
    the property speaks of a premium. `seed` is the suite's (it fixes a `monotone` grid);
    `outputs` names the algorithm's declared outputs, which `no_null_output` requires present
    and non-null — a null output is *omitted* from `ScoringResult.outputs`, so a check over
    the dict's values alone could never fail on a real result."""
    if isinstance(check, MonotoneInInput):
        field = monotone_field(contract, check)
        return monotone_sweep(check, field, context, score, seed).broken_at is None
    scored = score(context)
    if scored is None:
        return False
    if isinstance(check, PremiumPositive):
        premium = payable_minor(scored)
        return premium is None or premium > 0
    if isinstance(check, NoNullOutput):
        return all(value is not None for value in scored.outputs.values()) and all(
            scored.outputs.get(name) is not None for name in outputs
        )
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


def counterexample_points(
    check: PropertyCheck,
    contract: Sequence[InputContractField],
    context: QuoteContext,
    score: Scorer,
    seed: int,
) -> list[int | str] | None:
    """For a `monotone`, the two adjacent grid values where `context`'s sweep breaks."""
    if not isinstance(check, MonotoneInInput):
        return None
    field = monotone_field(contract, check)
    broken = monotone_sweep(check, field, context, score, seed).broken_at
    if broken is None:
        return None
    return [v if isinstance(v, int) else str(v) for v in broken]


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
