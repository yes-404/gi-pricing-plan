"""Golden-quote re-scoring (03 §5.2, FR-260, FR-273).

`evaluate_golden_quotes` is the pure re-score the backend's submit gate calls, and the
piece `run_regression` and `replay_cases` compose (the deputy's DP-S2-3 (a), `PL-1189`). It
holds no persistence, no clock and no I/O (`CLAUDE.md` §2; `.importlinter`'s
`core-has-no-infrastructure`): the suite store, the audit events and the gate are the
backend's (RL-1172 item 3c).

It is plain `def`, on the same synchronous `evaluate()` path `score_batch` uses (RL-868),
through `score._score_context_sync` and so through the same `build_scoring_result` tail as
`score_one` (RL-858). The comparison is integer subtraction in minor units — never a float
(FR-273). **This module never imports `hypothesis`** (`PL-1205` Task 4): it moved here,
unchanged, from `testing.py` so that `replay.py` can reach it, and `testing.py` re-exports
it under its declared name.
"""

from __future__ import annotations

from collections.abc import Sequence

from model_schema.refs import ArtifactRef
from model_schema.regression import GoldenQuote, GoldenQuoteResult
from model_schema.scoring import ScoringResult
from pricing_core.rating.runtime import CompiledBundle
from pricing_core.rating.score import _score_context_sync

__all__ = ["evaluate_golden_quotes"]

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
