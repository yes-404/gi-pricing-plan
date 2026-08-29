"""`QuoteContext`, `ScoringResult`, `Trace` (03 §4.4/§4.5, W11 Task 1.4).

Built against `docs/contracts/schemas/scoring.schema.json`'s `$defs`, not the spec's own
§4.4 JSON example — `CLAUDE.md` §2 forbids hand-writing a shape `model-schema` owns, and
these are the first code for any of the three (`git grep -n QuoteContext` returned zero
Python hits before this task; Ruling 12's addendum, `docs/plans/2026-08-29-w11-slice1-
rulings.md`). Two traps the §4.4 example carries that the contract does not, named there
and not repeated here: its numeric literals use `24_150`-style underscores (not valid
JSON), and its ladder omits `instalment_loading`, which post-dates the example
(FR-RATE-64). The contract's `LadderRung.rung` enum is the authority for both.

**`purpose` is five members, `cancellation` included** (Ruling 12; `03-rating-engine.md`
§2's dated glossary note, `:63`). `scoring.schema.json:12` is corrected to the same five in
the same commit that adds this module — the two must never diverge again the way they did
between 2026-08-18 and today.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from model_schema.money import MoneyMinor
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

#: FR-RATE-63 / Ruling 12. `cancellation` was added 2026-08-18 with FR-RATE-63: OQ-RATE-4's
#: answer mounts the refund sub-graph on `purpose`, and the value it keys on has to exist.
QuotePurpose = Literal["new_business", "renewal", "mid_term_adjustment", "cancellation", "what_if"]

#: `scoring.schema.json`'s closed `LadderRung.rung` enum (FR-RATE-31, widened by FR-RATE-64
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

#: `LadderRung.operation.kind` (`scoring.schema.json:36`).
LadderOperationKind = Literal["multiply", "add", "round", "none"]

#: `ScoringResult.outcome` (`scoring.schema.json:50`). `error` is not produced by
#: `score_one` today — a per-quote refusal is a raised, code-named `ValueError` (Ruling 11),
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
    source (`03` §5.2's already-ruled signature, Ruling 5); this field exists because the
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


class LadderOperation(BaseModel):
    """`LadderRung.operation` (`scoring.schema.json:33-42`).

    `factor` is a `Decimal`-exact string (R2 — never a JSON float); `amount_minor` is an
    integer minor unit (FR-RATE-56). `applied` carries the reason codes of every firing
    `constraint` step recorded at this rung — non-empty only on the `constraints` rung, and
    empty rather than absent when nothing fired, matching `03:412`'s worked example.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: LadderOperationKind
    factor: str | None = None
    amount_minor: MoneyMinor | None = None
    mode: str | None = None
    dp: int | None = None
    applied: list[str] = Field(default_factory=list)


class LadderRung(BaseModel):
    """One rung of the Premium Ladder (FR-RATE-31/32, `scoring.schema.json:25-45`)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung: LadderRungName
    value_minor: MoneyMinor
    operation: LadderOperation | None = None
    components: dict[str, MoneyMinor] | None = None


class TraceStep(BaseModel):
    """One node of a `Trace` (FR-RATE-41, `scoring.schema.json:71-86`).

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
    """`Trace` (FR-RATE-41, `scoring.schema.json:64-90`). Real-time and batch share the
    identical structure (`03:172`)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rating_version_ref: ArtifactRef
    bundle_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    quote_id: str | None = None
    steps: list[TraceStep]
    ladder_reconciled: bool


class ScoringResult(BaseModel):
    """`ScoringResult` (`scoring.schema.json:46-63`, `03` §4.4).

    Invariants (`scoring.schema.json:59-62`, enforced by `pricing_core.rating.score`, not
    re-validated here): applying every rung's recorded operation to `risk_premium`
    reproduces `payable_premium` exactly (FR-RATE-32); a traced and an untraced call on the
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
