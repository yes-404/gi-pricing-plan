"""The Premium Ladder's rung mapping, and the exact reconciliation predicate (FR-247, FR-248).

Two things live here because `score.py` (which builds a ladder) and `compile.py` (which
refuses a clamp the ladder cannot place) both need the first, and because the second must
not depend on either:

1. **The rung mapping** — `RUNG_ORDER`, `output_steps_by_name` and `rung_output_name`: which
   output step names a rung (`f"{rung}_minor"`). Moved out of `score.py` by `RL-1329` §2
   (`compile.py` cannot import `score.py`: `score` imports `runtime`, which imports
   `compile`).
2. **The exact predicate** — `recover_operation` (the operation a rung applied, recovered
   from two unrounded values) and `ladder_violations` / `reconcile_ladder` (`RL-1329` §5,
   R0 to R4). Every value is an exact `Decimal` in a context of 100 significant digits, never a
   float (FR-273's string limb, `CLAUDE.md` §7).

The predicate's inputs are **not** read from the ladder it checks (`FD-1336` limb 1): the
caller hands over the engine's exact value of each rung's source (`E`), each rung's declared
rounding (`D`), and what each clamp step read, all taken from the evaluated result and the
algorithm.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Context, Decimal, localcontext
from fractions import Fraction
from itertools import pairwise
from typing import Final, Literal

from model_schema.rating import RatingAlgorithm, RatingOutputStep
from model_schema.scoring import LadderOperation, LadderRounding, LadderRung, LadderRungName
from pricing_core.money import ROUNDING_MODES

__all__ = [
    "RUNG_ORDER",
    "ClampReading",
    "LadderInputs",
    "binding_side",
    "ladder_violations",
    "output_steps_by_name",
    "reconcile_ladder",
    "recover_operation",
    "round_once",
    "rung_output_name",
]

#: FR-247/252's fixed rung sequence — `scoring.schema.json`'s own `LadderRung.rung` enum
#: order, which post-dates and supersedes FR-247's prose order by adding `instalment_loading`
#: (FR-252). The ladder's order is fixed by the platform; it is never derived from an
#: algorithm's own step order.
RUNG_ORDER: Final[tuple[LadderRungName, ...]] = (
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

#: `RL-1329` §5: "a context of at least 100 significant digits" — addition and
#: multiplication of engine-sized values are exact, division is exact when it terminates.
_PREC: Final = 100
#: `RL-1329` §1 departure 2: each operation reproduces its rung's unrounded value within
#: 1e-26, relative (one engine rounding is about 10⁻²⁸).
_TOLERANCE: Final = Decimal("1e-26")
#: `RL-1329` §2 step 3: a recovered operand with this many significant digits or more is
#: not "a terminating operation whose result the engine rounded".
_MAX_OPERAND_DIGITS: Final = 20


def rung_output_name(rung: str) -> str:
    """The declared output a rung is read from: `f"{rung}_minor"` (FR-247)."""
    return f"{rung}_minor"


def output_steps_by_name(algorithm: RatingAlgorithm) -> dict[str, RatingOutputStep]:
    return {
        step.output_name: step for step in algorithm.steps if isinstance(step, RatingOutputStep)
    }


def _ctx() -> Context:
    return Context(prec=_PREC)


def round_once(value: Decimal, rounding: LadderRounding) -> int:
    """`value` rounded once with a rung's declared rounding (FR-226). Only `dp == 0` is
    built (`score.py` refuses any other)."""
    if rounding.dp != 0:
        raise NotImplementedError(
            f"a ladder rung rounds to whole minor units, not dp={rounding.dp}"
        )
    with localcontext(_ctx()):
        return int(value.quantize(Decimal(1), rounding=ROUNDING_MODES[rounding.mode]))


def _terminating_quotient(numerator: Decimal, denominator: Decimal) -> Decimal | None:
    """`numerator / denominator` if it terminates (and fits the context exactly), else None.

    Decided on the exact fraction, not on a rounded quotient: a non-terminating ratio
    rounded to 100 digits could multiply back to a 28-digit value by coincidence.
    """
    if denominator == 0:
        return None
    ratio = Fraction(numerator) / Fraction(denominator)
    remaining = ratio.denominator
    for prime in (2, 5):
        while remaining % prime == 0:
            remaining //= prime
    if remaining != 1:
        return None
    with localcontext(_ctx()):
        quotient = Decimal(ratio.numerator) / Decimal(ratio.denominator)
    return quotient if Fraction(quotient) == ratio else None


def _shortest_operand(full: Decimal, reproduces: Callable[[Decimal], bool]) -> Decimal | None:
    """The fewest-significant-digit rounding of `full` (under 20 digits) for which
    `reproduces` holds, else None."""
    for digits in range(1, _MAX_OPERAND_DIGITS):
        candidate = Context(prec=digits).create_decimal(full)
        if reproduces(candidate):
            return candidate
    return None


def _within_tolerance(replayed: Decimal, rung_value: Decimal) -> bool:
    with localcontext(_ctx()):
        if rung_value == 0:
            return replayed == 0
        return abs(replayed - rung_value) <= _TOLERANCE * abs(rung_value)


def recover_operation(prev: Decimal, cur: Decimal, *, force_add: bool = False) -> LadderOperation:
    """The operation that took `prev` to `cur`, both unrounded (`RL-1329` §2 step 3).

    In order: the exact factor; the exact divisor; the shortest factor, then the shortest
    divisor, that reproduces `cur` within 1e-26 relative while having fewer than 20
    significant digits (a terminating operation whose result the engine rounded); else `add`
    of the exact difference (a rung that applied more than one operation — the ladder says
    what the rung did and never invents a factor). `force_add` is for `ipt_and_fees`. An
    unchanged value is `x1`; the caller decides `none` for a non-multiply rung.
    """
    with localcontext(_ctx()):
        if force_add or prev == 0:
            return LadderOperation(kind="add", amount_unrounded_minor=cur - prev)
        if cur == prev:
            return LadderOperation(kind="multiply", factor=Decimal(1))
        factor = _terminating_quotient(cur, prev)
        if factor is not None:
            return LadderOperation(kind="multiply", factor=factor.normalize())
        divisor = _terminating_quotient(prev, cur) if cur != 0 else None
        if divisor is not None:
            return LadderOperation(kind="divide", divisor=divisor.normalize())
        if cur != 0:
            full_factor = cur / prev
            found = _shortest_operand(full_factor, lambda f: _within_tolerance(prev * f, cur))
            if found is not None:
                return LadderOperation(kind="multiply", factor=found.normalize())
            full_divisor = prev / cur
            found = _shortest_operand(
                full_divisor, lambda d: d != 0 and _within_tolerance(prev / d, cur)
            )
            if found is not None:
                return LadderOperation(kind="divide", divisor=found.normalize())
        return LadderOperation(kind="add", amount_unrounded_minor=cur - prev)


@dataclass(frozen=True)
class ClampReading:
    """What one `constraint` step with `on_violation="clamp"` read from the engine.

    `before` is the exact value of the name it consumes before the clamp (`__before`),
    `minimum` and `maximum` the exact bounds present (`__min`, `__max`), `in_disposition`
    whether the disposition lists its reason code (`_apply_constraints`).
    """

    step_id: str
    reason_code: str
    source: str
    before: Decimal
    minimum: Decimal | None
    maximum: Decimal | None
    in_disposition: bool


def binding_side(clamp: ClampReading) -> tuple[Literal["min", "max"], Decimal] | None:
    """`("min" | "max", bound)` if the clamp moves the value, else None. The comparison the
    generated clamp makes (`runtime._constraint_node`): the `min` side binds when
    `before < min`; the `max` side binds when the value after the `min` side is `> max`.
    When both bind, the `max` one set the final value."""
    value = clamp.before
    side: tuple[Literal["min", "max"], Decimal] | None = None
    if clamp.minimum is not None and value < clamp.minimum:
        value = clamp.minimum
        side = ("min", clamp.minimum)
    if clamp.maximum is not None and value > clamp.maximum:
        side = ("max", clamp.maximum)
    return side


@dataclass(frozen=True)
class LadderInputs:
    """The predicate's independent inputs (`RL-1329` §5), never read from the ladder.

    `exact[rung]` is `E(rung)`: the engine's exact value of the rung's output-step source
    (the value *before* the clamp, for the rung a clamp binds on); `rounding[rung]` is
    `D(rung)`. `constraints_exact` is the engine's value of the clamp source after the clamps
    (None when no clamp step exists), and `clamp_source` the name the last rung present
    before `constraints` is read from.
    """

    exact: Mapping[str, Decimal]
    rounding: Mapping[str, LadderRounding]
    constraints_exact: Decimal | None = None
    clamp_source: str | None = None
    clamps: Sequence[ClampReading] = ()


def _replay_step(running: Decimal, operation: LadderOperation) -> Decimal | None:
    """Apply one recorded operation with no rounding; None if its operand is missing."""
    with localcontext(_ctx()):
        if operation.kind == "multiply" and operation.factor is not None:
            return running * operation.factor
        if operation.kind == "divide" and operation.divisor not in (None, 0):
            assert operation.divisor is not None
            return running / operation.divisor
        if operation.kind == "add" and operation.amount_unrounded_minor is not None:
            return running + operation.amount_unrounded_minor
        if operation.kind == "clamp" and operation.bound_unrounded_minor is not None:
            return operation.bound_unrounded_minor
        if operation.kind in ("none", "round"):
            return running
    return None


def ladder_violations(ladder: Sequence[LadderRung], inputs: LadderInputs) -> list[str]:
    """Every way `ladder` fails `RL-1329` §5's R0-R4, as messages naming rungs and the
    difference (a decimal string in minor units). Empty when it reconciles.

    An empty ladder arises only for an algorithm that declares no rung output step at all;
    it has nothing to reconcile and returns no violation, **for that case alone**.
    """
    if not ladder:
        return []
    out: list[str] = []
    last = ladder[-1]

    # R0 — shape.
    if last.rung != "payable_premium":
        out.append(f"R0: the last rung is {last.rung!r}, not payable_premium")
    if ladder[0].operation is not None:
        out.append(f"R0: first rung {ladder[0].rung!r} carries an operation")
    for index, rung in enumerate(ladder):
        if index > 0 and rung.operation is None:
            out.append(f"R0: rung {rung.rung!r} carries no operation")
        kind = rung.operation.kind if rung.operation is not None else None
        if kind == "round" and index != len(ladder) - 1:
            out.append(f"R0: round on rung {rung.rung!r}, which is not the last")
        if kind == "clamp" and rung.rung != "constraints":
            out.append(f"R0: clamp on rung {rung.rung!r}, not constraints")
    binding: list[tuple[ClampReading, str, Decimal]] = []
    for clamp in inputs.clamps:
        side = binding_side(clamp)
        if side is not None:
            binding.append((clamp, side[0], side[1]))
            if clamp.source != inputs.clamp_source:
                out.append(
                    f"R0: clamp {clamp.step_id!r} binds on {clamp.source!r}, which is not "
                    f"the source of the last rung before constraints ({inputs.clamp_source!r})"
                )
        if (side is not None) != clamp.in_disposition:
            out.append(
                f"R0: clamp {clamp.step_id!r} comparison "
                f"({'binds' if side is not None else 'does not bind'}) and disposition "
                f"({'lists' if clamp.in_disposition else 'omits'} {clamp.reason_code!r}) disagree"
            )

    # R1 — sources; R2 — display.
    previous: LadderRung | None = None
    for rung in ladder:
        name = rung.rung
        if rung.unrounded_minor is None or rung.rounding is None:
            out.append(f"R1: rung {name!r} lacks unrounded_minor or rounding")
            previous = rung
            continue
        if name == "constraints":
            if binding:
                expected = inputs.constraints_exact
            else:
                expected = previous.unrounded_minor if previous is not None else None
            if previous is not None and rung.rounding != previous.rounding:
                out.append("R1: constraints rounding differs from the previous rung's")
        else:
            expected = inputs.exact.get(name)
            if inputs.rounding.get(name) != rung.rounding:
                out.append(f"R1: rung {name!r} rounding is not its output step's")
        if expected is None or rung.unrounded_minor != expected:
            out.append(
                f"R1: rung {name!r} unrounded_minor {_fmt(rung.unrounded_minor)} is not the "
                f"engine's value {_fmt(expected)}"
            )
        if round_once(rung.unrounded_minor, rung.rounding) != rung.value_minor:
            out.append(
                f"R2: rung {name!r} value_minor {rung.value_minor} is not its unrounded "
                f"value rounded once ({round_once(rung.unrounded_minor, rung.rounding)})"
            )
        previous = rung

    # R3 — each operation explains its rung.
    for before, rung in pairwise(ladder):
        operation = rung.operation
        if operation is None or before.unrounded_minor is None or rung.unrounded_minor is None:
            continue
        if operation.kind == "clamp":
            out.extend(_clamp_violations(before, rung, operation, binding))
            continue
        if operation.kind in ("none", "round"):
            if rung.unrounded_minor != before.unrounded_minor:
                out.append(
                    f"R3: rung {rung.rung!r} is {operation.kind} but differs from the previous "
                    f"rung by {_fmt(rung.unrounded_minor - before.unrounded_minor)}"
                )
            continue
        replayed = _replay_step(before.unrounded_minor, operation)
        if replayed is None or not _within_tolerance(replayed, rung.unrounded_minor):
            off = None if replayed is None else replayed - rung.unrounded_minor
            out.append(
                f"R3: rung {rung.rung!r} operation {operation.kind} does not reproduce its "
                f"unrounded value (off by {_fmt(off)})"
            )

    # R4 — the replay: every recorded operation with no rounding, then one rounding.
    first = ladder[0]
    if first.unrounded_minor is not None and last.rounding is not None:
        running: Decimal | None = first.unrounded_minor
        for rung in ladder[1:]:
            if running is None or rung.operation is None:
                running = None
                break
            running = _replay_step(running, rung.operation)
        priced_source = inputs.exact.get("payable_premium")
        if running is None:
            out.append("R4: an operation could not be replayed")
        elif last.rung == "payable_premium":
            replayed_payable = round_once(running, last.rounding)
            priced = (
                round_once(priced_source, inputs.rounding.get("payable_premium", last.rounding))
                if priced_source is not None
                else None
            )
            if replayed_payable != last.value_minor or replayed_payable != priced:
                out.append(
                    f"R4: the replay rounds to {replayed_payable}, the payable rung shows "
                    f"{last.value_minor} and the priced payable is {priced}"
                )
    return out


def _clamp_violations(
    before: LadderRung,
    rung: LadderRung,
    operation: LadderOperation,
    binding: Sequence[tuple[ClampReading, str, Decimal]],
) -> list[str]:
    assert before.unrounded_minor is not None
    assert rung.unrounded_minor is not None
    bound = operation.bound_unrounded_minor
    if operation.bound is None or bound is None:
        return [f"R3: clamp on {rung.rung!r} lacks bound or bound_unrounded_minor"]
    problems: list[str] = []
    if rung.unrounded_minor != bound:
        problems.append(
            f"R3: clamp value {_fmt(rung.unrounded_minor)} is not its bound {_fmt(bound)}"
        )
    if not binding:
        problems.append("R3: a clamp is recorded but no clamp step binds")
    else:
        _, side, engine_bound = binding[-1]
        if side != operation.bound or engine_bound != bound:
            problems.append(
                f"R3: clamp bound {operation.bound} {_fmt(bound)} is not the engine's "
                f"{side} {_fmt(engine_bound)}"
            )
    prior = before.unrounded_minor
    far_side_ok = prior < bound if operation.bound == "min" else prior > bound
    if not far_side_ok:
        problems.append(
            f"R3: the previous value {_fmt(before.unrounded_minor)} is not strictly on the far "
            f"side of the {operation.bound} bound {_fmt(bound)}"
        )
    return problems


def _fmt(value: Decimal | None) -> str:
    return "None" if value is None else format(value, "f")


def reconcile_ladder(ladder: Sequence[LadderRung], inputs: LadderInputs) -> bool:
    """Whether the ladder reconciles (FR-248 as amended by `RL-1329`): `ladder_violations`
    is empty. Asserted on every scored quote in every Environment, never sampled."""
    return not ladder_violations(ladder, inputs)
