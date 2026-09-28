"""Golden-quote re-scoring and property-case generation (03 §5.2, FR-260, FR-261, FR-273).

`generate_contexts` draws Quote Contexts from an input contract with `hypothesis`, under a
persisted seed and fixed settings (RS-1176 conditions 1, 2, 3 and 6, `PL-1205`). It is the
one module that imports `hypothesis`.

`evaluate_golden_quotes` is the pure re-score the backend's submit gate calls, and the
piece WK-672 Slice 3's `run_regression` composes (the deputy's DP-S2-3 (a), `PL-1189`). It
holds no persistence, no clock and no I/O (`CLAUDE.md` §2; `.importlinter`'s
`core-has-no-infrastructure`): the suite store, the audit events and the gate are the
backend's (RL-1172 item 3c).

It is plain `def`, on the same synchronous `evaluate()` path `score_batch` uses (RL-868),
through `score._score_context_sync` and so through the same `build_scoring_result` tail as
`score_one` (RL-858). The comparison is integer subtraction in minor units — never a float
(FR-273).
"""

from __future__ import annotations

import string
from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import hypothesis
from hypothesis import HealthCheck, given, settings
from hypothesis import seed as hypothesis_seed
from hypothesis import strategies as st

from model_schema.rating import InputContractField, RatingInputType
from model_schema.refs import ArtifactRef
from model_schema.regression import GoldenQuote, GoldenQuoteResult
from model_schema.scoring import QuoteContext, ScoringResult
from pricing_core.rating.runtime import CompiledBundle
from pricing_core.rating.score import _score_context_sync

__all__ = [
    "GeneratorVersionMismatch",
    "evaluate_golden_quotes",
    "generate_contexts",
    "generation_settings",
]

#: Fixed on every generated Quote Context, so a case log depends on the seed and the input
#: contract alone — never on the clock (RS-1176 condition 6).
_QUOTED_AT = datetime(2026, 1, 1, 12, 0, 0)
_EFFECTIVE_DATE = date(2026, 1, 1)

#: The ladder rung whose `value_minor` a golden quote's `payable_premium_minor` is.
_PAYABLE_RUNG = "payable_premium"


def _payable_minor(scored: ScoringResult) -> int | None:
    """The `payable_premium` rung's `value_minor` for a quoted result, else `None`."""
    if scored.outcome != "quoted":
        return None
    for rung in scored.premium_ladder:
        if rung.rung == _PAYABLE_RUNG:
            return rung.value_minor
    return None


def _evaluate_one(
    bundle: CompiledBundle, quote: GoldenQuote, rating_version_ref: ArtifactRef
) -> GoldenQuoteResult:
    expected = quote.expected
    try:
        scored = _score_context_sync(bundle, quote.context, rating_version_ref)
    except NotImplementedError:
        # A genuinely undesigned engine case, not a per-quote data error — the same
        # carve-out `score_batch` makes.
        raise
    except (ValueError, RuntimeError):
        # An engine refusal (input contract, purpose mount, engine failure) is this
        # quote's `fail`, never an abort of the rest.
        return GoldenQuoteResult(
            name=quote.name, status="fail",
            expected_minor=expected.payable_premium_minor, actual_minor=None,
            difference_minor=None,
        )

    actual = _payable_minor(scored)
    wanted = expected.payable_premium_minor
    difference = actual - wanted if actual is not None and wanted is not None else None
    passed = scored.outcome == expected.outcome and (
        expected.outcome != "quoted"
        or (difference is not None and abs(difference) <= quote.tolerance.money_minor)
    )
    return GoldenQuoteResult(
        name=quote.name, status="pass" if passed else "fail",
        expected_minor=wanted, actual_minor=actual, difference_minor=difference,
    )


def evaluate_golden_quotes(
    bundle: CompiledBundle,
    golden_quotes: Sequence[GoldenQuote],
    *,
    rating_version_ref: ArtifactRef,
) -> list[GoldenQuoteResult]:
    """Re-score every golden quote against `bundle`; one result per quote, in input order.

    A quote passes when its outcome equals the expected outcome and, when both are
    `quoted`, `abs(actual - expected) <= tolerance.money_minor` in integer minor units.
    `difference_minor` is `actual - expected` when both are integers, else `None`.
    """
    return [_evaluate_one(bundle, quote, rating_version_ref) for quote in golden_quotes]


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
    Health checks are suppressed: a contract with a small domain legitimately exhausts
    the strategy before `cases` distinct examples exist.
    """
    return settings(
        database=None,
        deadline=None,
        report_multiple_bugs=False,
        derandomize=False,
        max_examples=cases,
        suppress_health_check=list(HealthCheck),
    )


def _field_strategy(field: InputContractField) -> st.SearchStrategy[Any]:
    kind = field.type
    if kind is RatingInputType.BOOL:
        base: st.SearchStrategy[Any] = st.booleans()
    elif kind is RatingInputType.INT:
        low = int(field.min) if field.min is not None else 0
        high = int(field.max) if field.max is not None else low + 1_000_000
        base = st.integers(min_value=low, max_value=high)
    elif kind is RatingInputType.DECIMAL:
        low_d = Decimal(field.min) if field.min is not None else Decimal(0)
        high_d = Decimal(field.max) if field.max is not None else low_d + 1_000_000
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
    return [
        QuoteContext(
            purpose="new_business", quoted_at=_QUOTED_AT, effective_date=_EFFECTIVE_DATE,
            inputs=inputs,
        )
        for inputs in drawn[:n]
    ]


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
