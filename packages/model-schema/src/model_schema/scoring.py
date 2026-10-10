"""`QuoteContext`, `ScoringResult`, `Trace` (03 §4.4/§4.5, WK-671 Task 1.4).

Built against `docs/contracts/schemas/scoring.schema.json`'s `$defs`, not the spec's own
§4.4 JSON example — `CLAUDE.md` §2 forbids hand-writing a shape `model-schema` owns, and
these are the first code for any of the three (`git grep -n QuoteContext` returned zero
Python hits before this task; RL-878's addendum,
`docs/rulings/RL-00878-quotecontext-purpose-the-spec-is-right-and-the-hand-authored-contract-is-stale-and-the-fix-belongs-to-task-1-4.md`).
Two traps the §4.4 example carries that the contract does not, named there
and not repeated here: its numeric literals use `24_150`-style underscores (not valid
JSON), and its ladder omits `instalment_loading`, which post-dates the example
(FR-252). The contract's `LadderRung.rung` enum is the authority for both.

**`purpose` is five members, `cancellation` included** (RL-878; `03-rating-engine.md`
§2's dated glossary note, `:63`). `scoring.schema.json:12` is corrected to the same five in
the same commit that adds this module — the two must never diverge again the way they did
between 2026-08-18 and today.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.input_free import InputFreeError
from model_schema.money import MoneyMinor, PositionalDecimalStr
from model_schema.refs import ArtifactRef

__all__ = [
    "LadderOperation",
    "LadderRung",
    "LadderRungName",
    "QuoteContext",
    "QuoteContextOptions",
    "QuotePurpose",
    "ScoringOutcome",
    "ScoringResult",
    "Trace",
    "TraceStep",
]

#: FR-218 / RL-878. `cancellation` was added 2026-08-18 with FR-218: OQ-617's
#: answer mounts the refund sub-graph on `purpose`, and the value it keys on has to exist.
QuotePurpose = Literal["new_business", "renewal", "mid_term_adjustment", "cancellation", "what_if"]

#: `scoring.schema.json`'s closed `LadderRung.rung` enum (FR-247, widened by FR-252
#: to add `instalment_loading`). The contract's declared order is the ladder's own order —
#: `pricing_core.rating.score` walks this sequence, never the algorithm's own step order.
LadderRungName = Literal[
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
]

#: `LadderRung.operation.kind` (`scoring.schema.json`). `divide` and `clamp` were added by
#: `RL-1329` §3: a gross-up is recorded as its true divisor, and a binding clamp as what it did.
LadderOperationKind = Literal["multiply", "divide", "add", "clamp", "round", "none"]

#: `LadderRung.rounding.mode`, the modes `RoundSpec` declares (`common/money.schema.json`).
LadderRoundingMode = Literal["half_even", "half_up", "ceiling", "floor", "down"]

#: `ScoringResult.outcome` (`scoring.schema.json:50`). `error` is not produced by
#: `score_one` today — a per-quote refusal is a raised, code-named `ValueError` (RL-877),
#: mapped to a `PlatformError` at the backend boundary in Slice 2 — but the member is kept
#: because the contract already declares it and a future consumer (batch row status,
#: Slice 3) may use it without a second enum needing to be defined.
ScoringOutcome = Literal["quoted", "declined", "error"]

#: `03` §3.7's step-type vocabulary, restated on `Trace.steps[].type`.
TraceStepType = Literal[
    "input", "lookup", "table", "expression", "model_call", "constraint", "output"
]


class QuoteContextOptions(BaseModel):
    """`QuoteContext.options` (`scoring.schema.json:16-22`).

    `trace` is **not** read by `score_one` — its own `trace: bool` keyword is the single
    source (`03` §5.2's already-ruled signature, RL-868); this field exists because the
    wire contract declares it, for a caller (Slice 2's HTTP layer) that maps a request body
    onto the `trace=` argument. `rating_version_ref` is required in practice at this layer:
    Slice 1 builds no default-live resolution (DP1, Slice 2), so `score_one` refuses a
    context that omits it rather than guessing which version to report scoring against.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    trace: bool = False
    rating_version_ref: ArtifactRef | None = None


class QuoteContext(BaseModel):
    """`QuoteContext` (`scoring.schema.json:7-24`, `03` §4.4)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    quote_id: str | None = None
    purpose: QuotePurpose
    quoted_at: datetime
    effective_date: date
    inputs: dict[str, object] = Field(default_factory=dict)
    options: QuoteContextOptions | None = None


class LadderRounding(BaseModel):
    """A rung's declared rounding (`common/money.schema.json#/$defs/Rounding`, `RL-1329` §3)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: LadderRoundingMode
    dp: int = Field(ge=0)


class LadderOperation(BaseModel):
    """`LadderRung.operation` (`scoring.schema.json`, FR-248 as amended by `RL-1329`).

    The operation a rung applied to the previous rung's **unrounded** value. Operands are
    exact and never quantised: `factor` (`multiply`), `divisor` (`divide`),
    `amount_unrounded_minor` (`add`), and `bound` with `bound_unrounded_minor` (`clamp`,
    on the `constraints` rung only). `mode` and `dp` are emitted only on `round`.
    `applied` carries the reason codes of the binding clamps on the `constraints` rung
    (`clamp` or `none`), empty rather than absent when nothing fired. `amount_minor` is
    **legacy**: kept so a stored pre-ruling ladder still validates; the builder no longer
    emits it. Every field added by `RL-1329` is optional, because stored ladders are
    write-once and lack them.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: LadderOperationKind
    factor: PositionalDecimalStr | None = None
    divisor: PositionalDecimalStr | None = None
    amount_minor: MoneyMinor | None = None
    amount_unrounded_minor: PositionalDecimalStr | None = None
    bound: Literal["min", "max"] | None = None
    bound_unrounded_minor: PositionalDecimalStr | None = None
    mode: str | None = None
    dp: int | None = None
    applied: list[str] = Field(default_factory=list)


class LadderRung(BaseModel):
    """One rung of the Premium Ladder (FR-247/248, `scoring.schema.json`).

    `unrounded_minor` is the engine's exact value for the rung; `value_minor` is that value
    rounded once with `rounding` (`RL-1329` §2). Displayed values do not multiply into each
    other; the unrounded column is the one that replays (FR-248).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung: LadderRungName
    value_minor: MoneyMinor
    unrounded_minor: PositionalDecimalStr | None = None
    rounding: LadderRounding | None = None
    operation: LadderOperation | None = None
    components: dict[str, MoneyMinor] | None = None


class TraceStep(BaseModel):
    """One node of a `Trace` (FR-258, `scoring.schema.json:71-86`).

    `consumed`/`produced` are the engine's own `trace[node_id].input`/`.output` dicts,
    passed through rather than re-derived — `03` does not specify a narrower shape than
    "consumed values, produced value" and the engine's own record already satisfies it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str
    type: TraceStepType
    label: str | None = None
    consumed: dict[str, object] = Field(default_factory=dict)
    produced: dict[str, object] = Field(default_factory=dict)
    matched: dict[str, object] | None = None
    violation: dict[str, object] | None = None
    elapsed_us: int = Field(ge=0, default=0)


class Trace(BaseModel):
    """`Trace` (FR-258, `scoring.schema.json:64-90`). Real-time and batch share the
    identical structure (`03:172`)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rating_version_ref: ArtifactRef
    bundle_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    quote_id: str | None = None
    steps: list[TraceStep]
    ladder_reconciled: bool
    # Which check produced `ladder_reconciled` (PL-1342 Acceptance 10, RL-1346 §2). Absent or 1:
    # first rung and int-ness only, before FR-248's full check, so not a reconciliation. 2: the
    # RL-1329 §5 predicate over RL-1329's ladder shape. Optional because stored traces lack it.
    ladder_check_version: int | None = Field(default=None, ge=1)


class ScoringResult(BaseModel):
    """`ScoringResult` (`scoring.schema.json:46-63`, `03` §4.4).

    Invariants (`scoring.schema.json:59-62`, enforced by `pricing_core.rating.score`, not
    re-validated here): applying every rung's recorded operation to `risk_premium`
    reproduces `payable_premium` exactly (FR-248); a traced and an untraced call on the
    same bundle and context return an identical premium (`03` R3).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    outcome: ScoringOutcome
    rating_version_ref: ArtifactRef
    bundle_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    premium_ladder: list[LadderRung]
    outputs: dict[str, object] = Field(default_factory=dict)
    decline_reasons: list[str] = Field(default_factory=list)
    trace: Trace | None = None
    timing_ms: dict[str, float] = Field(default_factory=dict)


StepChangeKind = Literal["added", "removed", "changed"]
TraceStepField = Literal["type", "label", "consumed", "produced", "matched", "violation"]


class StepChange(BaseModel):
    """One step that differs between two Traces (FR-262, `03` §4.10). `own_change` is true
    when the step was added, removed, or changed while consuming identical inputs. False
    means no own change attributable from the traces, which is not a claim that the step
    was not edited."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str
    change: StepChangeKind
    changed_fields: list[TraceStepField] = Field(default_factory=list)
    own_change: bool = Field(
        description=(
            "True for an added or removed step, and for a changed step whose consumed inputs "
            "are identical on both sides. False means no own change attributable from the "
            "traces; it is not a claim that the step was not edited (a downstream step can be "
            "edited and also consume a moved value)."
        )
    )
    base: TraceStep | None = None
    comparison: TraceStep | None = None


class TraceDiff(BaseModel):
    """The step-level difference of two executed Traces (FR-262, `03` §4.10). Distinct from
    FR-219's structural `AlgorithmDiff`, which compares two algorithm definitions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    steps: list[StepChange]
    unchanged: int = Field(ge=0)


class ScoreCompareRequest(BaseModel):
    """`POST /api/v1/score/compare` body (FR-262, `03` §4.10): one quote, two versions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    context: QuoteContext
    base: ArtifactRef
    comparison: ArtifactRef

    @model_validator(mode="after")
    def _context_names_no_version(self) -> Self:
        options = self.context.options
        if options is not None and options.rating_version_ref is not None:
            raise InputFreeError(
                "context.options.rating_version_ref must be omitted: "
                "`base` and `comparison` name the two versions"
            )
        return self


class ScoreComparison(BaseModel):
    """`POST /api/v1/score/compare` response (FR-262, `03` §4.10): both traced results and
    the diff of their traces."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    base: ScoringResult
    comparison: ScoringResult
    diff: TraceDiff
