"""Property-case generation and `run_regression` (03 §5.2, FR-260, FR-261; `PL-1205`).

The one module that imports `hypothesis`. `generate_contexts` draws Quote Contexts from an
input contract under a persisted seed and fixed settings (RS-1176 conditions 1, 2, 3 and
6). `run_regression` composes `evaluate_golden_quotes` (`golden.py`, re-exported here under
its declared name) with the five property classes (`properties.py`), shrinks each failing
property through `hypothesis` to a counterexample, and records whether that shrink ended
or was stopped on a limit (condition 5). It is plain `def`, on the synchronous
`evaluate()` path (RL-868, RL-858), and holds no persistence: the case log and the
`RegressionRun` are returned for the backend to store (FR-1214). Its replay twin,
`replay.replay_cases`, re-scores them without ever reaching this module.
"""

from __future__ import annotations

import contextlib
import string
from collections.abc import Callable, Sequence
from datetime import date, datetime
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from typing import Any, Literal

import hypothesis
from hypothesis import given, settings
from hypothesis import seed as hypothesis_seed
from hypothesis import strategies as st
from hypothesis.internal.conjecture.engine import ExitReason
from hypothesis.statistics import collector

from model_schema.rating import InputContractField, RatingInputType
from model_schema.refs import ArtifactRef
from model_schema.regression import (
    CasesLog,
    PropertyResult,
    RegressionRun,
    RegressionSuite,
    RunGeneration,
)
from model_schema.scoring import QuoteContext
from pricing_core.rating.golden import evaluate_golden_quotes
from pricing_core.rating.properties import (
    NO_COMPARABLE_PAIRS,
    PROPERTY_FAILED,
    Scorer,
    build_run,
    case_holds,
    counterexample_points,
    make_scorer,
    monotone_field,
    monotone_has_comparable_pair,
)
from pricing_core.rating.runtime import CompiledBundle

__all__ = [
    "GeneratorVersionMismatch",
    "evaluate_golden_quotes",  # re-exported from `golden.py` under its declared name
    "generate_contexts",
    "generation_settings",
    "run_regression",
]

#: Fixed on every generated Quote Context, so a case log depends on the seed and the input
#: contract alone — never on the clock (RS-1176 condition 6).
_QUOTED_AT = datetime(2026, 1, 1, 12, 0, 0)
_EFFECTIVE_DATE = date(2026, 1, 1)

#: An `int` or `decimal` input with no declared bound is sampled over `-1_000_000..1_000_000`,
#: symmetric about zero, so a property that fails only for negatives is reachable.
_DEFAULT_BOUND = 1_000_000


class GeneratorVersionMismatch(ValueError):  # noqa: N818 - declared name, 03 §5.2
    """The installed `hypothesis` is not the version a run was generated under (condition 3)."""

    def __init__(self, expected: str, actual: str) -> None:
        super().__init__(
            f"generator version mismatch: the run recorded hypothesis {expected!r}, "
            f"but hypothesis {actual!r} is installed"
        )
        self.expected = expected
        self.actual = actual


def generation_settings(cases: int) -> settings:
    """The one settings object `generate_contexts` and `run_regression` both apply.

    RS-1176 condition 2: no example database (a run must not depend on state left by a
    previous one), no deadline (the engine call's speed is not a property), one reported
    failure, and no derandomisation (the persisted seed is the reproduction handle).
    """
    return settings(
        database=None,
        deadline=None,
        report_multiple_bugs=False,
        derandomize=False,
        max_examples=cases,
    )


def _field_strategy(field: InputContractField) -> st.SearchStrategy[Any]:
    kind = field.type
    if kind is RatingInputType.BOOL:
        base: st.SearchStrategy[Any] = st.booleans()
    elif kind is RatingInputType.INT:
        low = int(field.min) if field.min is not None else -_DEFAULT_BOUND
        high = int(field.max) if field.max is not None else max(_DEFAULT_BOUND, low)
        base = st.integers(min_value=low, max_value=high)
    elif kind is RatingInputType.DECIMAL:
        cent = Decimal("0.01")
        low_d = (
            Decimal(field.min).quantize(cent, rounding=ROUND_CEILING)
            if field.min is not None else Decimal(-_DEFAULT_BOUND)
        )
        high_d = (
            Decimal(field.max).quantize(cent, rounding=ROUND_FLOOR)
            if field.max is not None else max(Decimal(_DEFAULT_BOUND), low_d)
        )
        if low_d > high_d:
            raise ValueError(
                f"decimal input {field.name!r} has no 2-place value between its bounds"
            )
        base = st.decimals(min_value=low_d, max_value=high_d, places=2)
    elif kind is RatingInputType.ENUM:
        if not field.domain:
            raise ValueError(f"enum input {field.name!r} declares no domain to sample from")
        base = st.sampled_from(field.domain)
    elif kind is RatingInputType.DATE:
        base = st.dates(min_value=date(2000, 1, 1), max_value=date(2100, 12, 31)).map(
            lambda d: d.isoformat()
        )
    elif field.pattern is not None:
        base = st.from_regex(field.pattern, fullmatch=True)
    else:
        base = st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=12)
    return st.none() | base if field.nullable else base


def _context(inputs: dict[str, Any]) -> QuoteContext:
    return QuoteContext(
        purpose="new_business", quoted_at=_QUOTED_AT, effective_date=_EFFECTIVE_DATE,
        inputs=inputs,
    )


def _draw_contexts(
    contract: Sequence[InputContractField], n: int, seed: int | None
) -> list[QuoteContext]:
    """Draw up to `n` contexts; `seed=None` is the unseeded negative control only."""
    if n <= 0:
        return []
    drawn: list[dict[str, Any]] = []

    @given(st.fixed_dictionaries({f.name: _field_strategy(f) for f in contract}))
    def collect(inputs: dict[str, Any]) -> None:
        drawn.append(inputs)

    collect = generation_settings(n)(collect)
    if seed is not None:
        collect = hypothesis_seed(seed)(collect)
    collect()
    return [_context(inputs) for inputs in drawn[:n]]


def generate_contexts(
    contract: Sequence[InputContractField],
    n: int,
    seed: int,
    *,
    expect_version: str | None = None,
) -> list[QuoteContext]:
    """`n` Quote Contexts sampled from `contract` under the persisted `seed` (FR-261).

    Same seed, same `hypothesis` version and same contract give the same list in every
    process. `expect_version`, when given, must equal the installed `hypothesis` version
    or `GeneratorVersionMismatch` is raised before anything is drawn. A contract whose
    domain holds fewer than `n` distinct examples returns fewer.
    """
    if expect_version is not None and expect_version != hypothesis.__version__:
        raise GeneratorVersionMismatch(expect_version, hypothesis.__version__)
    return _draw_contexts(contract, n, seed)


class _PropertyFailedError(AssertionError):
    """Raised inside a `hypothesis` test so the engine shrinks the failing context."""


#: `stopped-because` texts meaning the shrink ended on a limit, not because it was done.
_SHRINK_LIMITS = frozenset(
    {ExitReason.very_slow_shrinking.value, ExitReason.max_shrinks.value}
)


def _shrink(
    prop_check: Any,
    contract: Sequence[InputContractField],
    n: int,
    seed: int,
    score: Scorer,
    outputs: Sequence[str],
) -> tuple[QuoteContext | None, bool]:
    """Shrink one failing property to a counterexample; `(context, stopped_on_limit)`.

    Re-runs the generator under the same seed and settings, so the first failure it meets
    is the one the case list already holds, then lets `hypothesis` minimise it. The stop
    reason is read from `hypothesis.statistics.collector`, **internal API** that the exact
    pin and the forced-limit test keep honest (RS-1176 condition 5). When no reason is
    reported the shrink is treated as stopped: minimality is never claimed unproven.
    """
    stats: list[Any] = []
    failing: list[QuoteContext] = []

    @given(st.fixed_dictionaries({f.name: _field_strategy(f) for f in contract}))
    def run(inputs: dict[str, Any]) -> None:
        context = _context(inputs)
        if not case_holds(prop_check, context, score, contract, seed=seed, outputs=outputs):
            failing.append(context)
            raise _PropertyFailedError

    run = hypothesis_seed(seed)(generation_settings(n)(run))
    with collector.with_value(stats.append), contextlib.suppress(_PropertyFailedError):  # type: ignore[arg-type]
        run()
    if not failing:
        return None, True
    reason = stats[-1].get("stopped-because") if stats else None
    return failing[-1], reason is None or reason in _SHRINK_LIMITS


def run_regression(
    bundle: CompiledBundle,
    suite: RegressionSuite,
    *,
    rating_version_ref: ArtifactRef,
    now: Callable[[], datetime],
) -> tuple[RegressionRun, CasesLog]:
    """Run `suite` against `bundle`: golden quotes, then FR-261's properties over
    `suite.generation.cases` contexts drawn under `suite.generation.seed` — the persisted
    seed, with no override: a run cannot be made under one seed and recorded as another.

    Returns the run (`job_id` unset, `cases_blob` the case log's content address) and the
    `CasesLog` the backend persists as that blob (FR-1214). `now` is the caller's clock,
    read at the start and the end. A `monotone` naming an input the contract lacks is
    refused before anything is generated.
    """
    started_at = now()
    contract = bundle.algorithm.input_contract
    for prop in suite.properties:
        if prop.check.kind == "monotone":
            monotone_field(contract, prop.check)

    outputs = [o.name for o in bundle.algorithm.outputs]
    score = make_scorer(bundle, rating_version_ref, contract)
    golden = evaluate_golden_quotes(
        bundle, suite.golden_quotes, rating_version_ref=rating_version_ref
    )
    n = suite.generation.cases
    seed = suite.generation.seed
    cases = generate_contexts(contract, n, seed)

    results: list[PropertyResult] = []
    counterexamples: dict[str, QuoteContext] = {}
    for prop in suite.properties:
        check = prop.check
        grid: Literal["uniform+sampled"] | None = (
            "uniform+sampled" if check.kind == "monotone" else None
        )
        if all(case_holds(check, c, score, contract, seed=seed, outputs=outputs) for c in cases):
            if check.kind == "monotone" and not monotone_has_comparable_pair(
                check, contract, cases, score, seed
            ):
                # DP-S3-7: every sweep declined all but at most one point — nothing was
                # compared, so the property must not pass.
                results.append(PropertyResult(
                    name=prop.name, status="fail", cases_run=len(cases), shrink="completed",
                    error_code=NO_COMPARABLE_PAIRS, grid=grid,
                ))
                continue
            results.append(PropertyResult(
                name=prop.name, status="pass", cases_run=len(cases), grid=grid
            ))
            continue
        found, stopped = _shrink(check, contract, n, seed, score, outputs)
        if found is None:  # the generator did not re-find it: report the first failing case
            found = next(
                c for c in cases
                if not case_holds(check, c, score, contract, seed=seed, outputs=outputs)
            )
            stopped = True
        counterexamples[prop.name] = found
        results.append(PropertyResult(
            name=prop.name, status="fail", cases_run=len(cases),
            counterexample=dict(found.inputs), counterexample_minimal=not stopped,
            shrink="stopped_on_limit" if stopped else "completed",
            error_code=PROPERTY_FAILED, grid=grid,
            counterexample_points=counterexample_points(check, contract, found, score, seed),
        ))

    log = CasesLog(cases=cases, counterexamples=counterexamples)
    run = build_run(
        suite=suite, bundle_hash=bundle.content_hash, rating_version_ref=rating_version_ref,
        started_at=started_at, finished_at=now(),
        generation=RunGeneration(seed=seed, cases=n, hypothesis_version=hypothesis.__version__),
        cases=log, golden_results=golden, property_results=results,
    )
    return run, log
