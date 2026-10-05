"""`origin/main`'s ladder builder at `36b2a121`, verbatim — the BASELINE of `RL-1329`.

Acceptance 8 measures the ruled builder against "`origin/main`'s builder run on the same
golden contexts at S3's base tree", and Acceptance 2 requires the scale sweep to be shown red
over that builder. This file is that builder, copied from `score.py` (`_RUNG_ORDER`,
`_MULTIPLY_RUNGS`, `_ADD_RUNGS`, `_round_minor`, `_output_steps_by_name`, `_build_ladder`,
`_build_outputs`, `_as_list`) with no edit to a function body. It is frozen: it is a
measurement instrument, not a second implementation, and nothing in `src/` imports it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any

from model_schema.rating import RatingAlgorithm, RatingOutputStep
from model_schema.scoring import LadderOperation, LadderRung, LadderRungName
from pricing_core.money import ROUNDING_MODES, RoundingMode, apply_factor

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

def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else [value]


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
