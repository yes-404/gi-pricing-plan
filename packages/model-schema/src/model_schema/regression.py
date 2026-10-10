"""Regression Suites, Golden Quotes and the golden-quote evidence (03 §4.3, §4.7, §4.9).

A Regression Suite is its own versioned artifact, bound to one Rating Algorithm by
`algorithm_slug` and never approvable (the deputy's DP-S2-1 (A), `PL-1189`). FR-261's five
property classes are stored as a structured union discriminated on `kind` — declarative
JSON, never a free-text assertion (the F4 assertion-language ruling). This slice stores
them; WK-672 Slice 3 evaluates them.

`GoldenQuoteEvidence` is what the submit gate writes into a Rating Version's
`evidence.golden_quotes` (FR-260, amended 2026-09-28): either the checked form, which pins
the suite by content hash and carries the delta since the previous approved version, or the
explicit not-checked form — never an empty result list that reads as "0 mismatches".
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime
from typing import Annotated, Any, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.input_free import InputFreeError
from model_schema.money import DecimalStr, MoneyMinor
from model_schema.refs import ArtifactRef, BlobRef, Slug
from model_schema.scoring import QuoteContext, ScoringOutcome

_FROZEN = ConfigDict(frozen=True, extra="forbid")

#: `sha256:` plus 64 lowercase hex digits — the content-hash form every hash here takes.
Sha256Hash = Annotated[str, Field(pattern=r"^sha256:[a-f0-9]{64}$")]


def _canonical_sha256(payload: Any) -> str:
    """`sha256:` over the canonical JSON form: sorted keys, no whitespace."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _duplicates(names: list[str]) -> list[str]:
    return sorted(name for name, count in Counter(names).items() if count > 1)


class GoldenQuoteExpected(BaseModel):
    """What a golden quote must reproduce: the payable premium and the outcome only.

    Never `timing_ms` (RL-931). `payable_premium_minor` is the `payable_premium` ladder
    rung's `value_minor`, and it is null exactly when `outcome` is not `quoted`.
    """

    model_config = _FROZEN

    payable_premium_minor: MoneyMinor | None
    outcome: ScoringOutcome

    @model_validator(mode="after")
    def _premium_exactly_when_quoted(self) -> Self:
        if (self.outcome == "quoted") != (self.payable_premium_minor is not None):
            raise InputFreeError(
                "payable_premium_minor is set exactly when outcome is 'quoted'"
            )
        return self


class GoldenQuoteTolerance(BaseModel):
    """The declared tolerance, in integer minor units. Default exact (FR-260)."""

    model_config = _FROZEN

    money_minor: int = Field(default=0, ge=0, strict=True)


class GoldenQuote(BaseModel):
    """A named Quote Context with its expected outputs (03 §2, FR-260)."""

    model_config = _FROZEN

    name: Slug
    context: QuoteContext
    expected: GoldenQuoteExpected
    tolerance: GoldenQuoteTolerance = GoldenQuoteTolerance()
    note: str | None = None


# FR-261's five property classes, a union discriminated on `kind`.


class PremiumPositive(BaseModel):
    model_config = _FROZEN

    kind: Literal["premium_positive"]


class MonotoneInInput(BaseModel):
    model_config = _FROZEN

    kind: Literal["monotone"]
    input: str = Field(min_length=1)
    direction: Literal["increasing", "decreasing"]
    strict: bool = False
    lower: DecimalStr | None = None
    upper: DecimalStr | None = None

    @model_validator(mode="after")
    def _ordered_range(self) -> Self:
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise InputFreeError("monotone: lower must not exceed upper")
        return self


class NoNullOutput(BaseModel):
    model_config = _FROZEN

    kind: Literal["no_null_output"]


class LadderReconciles(BaseModel):
    """The premium ladder reconciles (FR-248)."""

    model_config = _FROZEN

    kind: Literal["ladder_reconciles"]


class PremiumBounded(BaseModel):
    """An absolute bound, in minor units — never relative to another output."""

    model_config = _FROZEN

    kind: Literal["premium_bounded"]
    lower_minor: MoneyMinor | None = None
    upper_minor: MoneyMinor | None = None

    @model_validator(mode="after")
    def _at_least_one_ordered_bound(self) -> Self:
        if self.lower_minor is None and self.upper_minor is None:
            raise InputFreeError("premium_bounded needs lower_minor, upper_minor, or both")
        if (
            self.lower_minor is not None
            and self.upper_minor is not None
            and self.lower_minor > self.upper_minor
        ):
            raise InputFreeError("premium_bounded: lower_minor must not exceed upper_minor")
        return self


PropertyCheck = Annotated[
    PremiumPositive | MonotoneInInput | NoNullOutput | LadderReconciles | PremiumBounded,
    Field(discriminator="kind"),
]


class RegressionProperty(BaseModel):
    model_config = _FROZEN

    name: Slug
    check: PropertyCheck


class RegressionGeneration(BaseModel):
    model_config = _FROZEN

    #: The bound (RS-1176 condition 2): a run persists every generated case (FR-1221).
    cases: int = Field(ge=1, le=10_000)
    seed: int = Field(ge=0)
    strategy: Literal["input_contract_sampling"]


class RegressionSuiteContent(BaseModel):
    """The content a suite version's `content_hash` is computed over."""

    model_config = _FROZEN

    algorithm_slug: Slug
    golden_quotes: list[GoldenQuote]
    properties: list[RegressionProperty]
    generation: RegressionGeneration

    @model_validator(mode="after")
    def _unique_names(self) -> Self:
        for label, names in (
            ("golden quote", [quote.name for quote in self.golden_quotes]),
            ("property", [prop.name for prop in self.properties]),
        ):
            if duplicated := _duplicates(names):
                raise ValueError(f"duplicate {label} names: {duplicated}")
        return self


class RegressionSuite(RegressionSuiteContent):
    """One version of a Regression Suite (03 §4.7). Versioned, not approvable."""

    slug: Slug
    version: int = Field(ge=1)
    change_note: str = Field(min_length=1)
    content_hash: Sha256Hash
    created_at: datetime
    created_by: UUID

    def content(self) -> RegressionSuiteContent:
        """The hashed part of this version, without its metadata."""
        return RegressionSuiteContent.model_validate(
            self.model_dump(include=set(RegressionSuiteContent.model_fields))
        )


class RegressionSuiteVersionCreate(RegressionSuiteContent):
    """The request body of `POST /api/v1/regression-suites/{slug}/versions` (03 §5.1).

    The content plus the required change note; the slug comes from the path, and the
    version, hash, author and time are the server's.
    """

    change_note: str = Field(min_length=1)


def suite_content_hash(content: RegressionSuiteContent) -> str:
    """`sha256:` over the canonical JSON of the suite's content fields only."""
    payload = content.model_dump(mode="json", include=set(RegressionSuiteContent.model_fields))
    return _canonical_sha256(payload)


def context_hash(context: QuoteContext) -> str:
    """The same canonical form as `suite_content_hash`, over one Quote Context.

    The delta records a context change by this hash, never by copying the context
    (NFR-499: a full quote input lives only in the access-controlled suite).
    """
    return _canonical_sha256(context.model_dump(mode="json"))


class GoldenQuoteResult(BaseModel):
    """One golden quote's re-score — 03 §4.9's `golden_results[]` item, field for field."""

    model_config = _FROZEN

    name: str
    status: Literal["pass", "fail"]
    expected_minor: MoneyMinor | None = None
    actual_minor: MoneyMinor | None = None
    difference_minor: int | None = None


class CasesLog(BaseModel):
    """A run's reproduction record: every generated case and every counterexample (FR-261).

    Persisted as one content-addressed canonical JSON blob (FR-1221) and replayed by
    re-scoring, never regenerated. `counterexamples` is keyed by property name.
    """

    model_config = _FROZEN

    cases: list[QuoteContext]
    counterexamples: dict[str, QuoteContext]


def cases_log_bytes(log: CasesLog) -> bytes:
    """The blob's content: canonical JSON, sorted keys, no whitespace (as `suite_content_hash`)."""
    return json.dumps(
        log.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    ).encode()


def cases_log_sha256(log: CasesLog) -> str:
    """The bare 64-hex digest of `cases_log_bytes` — the `BlobRef.sha256` form."""
    return hashlib.sha256(cases_log_bytes(log)).hexdigest()


class RunGeneration(BaseModel):
    """How a run generated its cases (03 §4.9); the seed serves same-version regeneration."""

    model_config = _FROZEN

    seed: int = Field(ge=0)
    cases: int = Field(ge=1, le=10_000)
    hypothesis_version: str


class PropertyResult(BaseModel):
    """One property's outcome — 03 §4.9's `property_results[]` item.

    A failing property records how its shrink ended; a shrink stopped on a limit is
    reported as unminimised, never as a minimal counterexample (RS-1176 condition 5).
    """

    model_config = _FROZEN

    name: str
    status: Literal["pass", "fail"]
    cases_run: int = Field(ge=0)
    counterexample: dict[str, Any] | None = None
    counterexample_minimal: bool = False
    shrink: Literal["completed", "stopped_on_limit"] | None = None
    error_code: str | None = None
    #: How a `monotone` property's grid was built (DP-S3-6): the uniform grid plus
    #: seeded samples, the weaker form — an inversion narrower than the spacing may not be
    #: detected until Bandings are pinned in the bundle. `None` for every other class.
    grid: Literal["uniform+sampled"] | None = None
    #: The two adjacent grid values, in order, at which a `monotone` counterexample's premium
    #: broke the property (`counterexample` is the base context; DP-S3-5).
    counterexample_points: list[int | str] | None = None

    @model_validator(mode="after")
    def _shrink_iff_failed(self) -> Self:
        if (self.status == "fail") != (self.shrink is not None):
            raise InputFreeError("`shrink` is recorded exactly when the property failed")
        if self.status == "pass" and (self.counterexample is not None or self.error_code):
            raise InputFreeError("a passing property carries no counterexample or error_code")
        if self.counterexample_minimal and self.shrink != "completed":
            raise InputFreeError("a counterexample is minimal only when its shrink completed")
        return self


class RegressionRun(BaseModel):
    """The execution record of a Regression Suite run (03 §4.9, FR-260, FR-261)."""

    model_config = _FROZEN

    suite_ref: ArtifactRef
    suite_content_hash: Sha256Hash
    rating_version_ref: ArtifactRef
    bundle_hash: Sha256Hash
    job_id: UUID | None = None
    started_at: datetime
    finished_at: datetime
    overall: Literal["pass", "fail"]
    generation: RunGeneration
    cases_blob: BlobRef
    golden_results: list[GoldenQuoteResult]
    property_results: list[PropertyResult]


class GoldenQuoteChangeStep(BaseModel):
    """One suite version that added, removed or substantively changed a golden quote.

    `author` is the actor of that version's `regression_suite.created` Audit Event
    (`06` FR-368) — never the row's `created_by` copy. A version that changed only
    `note` is no step.
    """

    model_config = _FROZEN

    version: int = Field(ge=1)
    changed_fields: list[Literal["added", "removed", "expected", "tolerance", "context"]] = (
        Field(min_length=1)
    )
    author: UUID


class GoldenQuoteChange(BaseModel):
    """A golden quote added, removed or changed since the baseline suite."""

    model_config = _FROZEN

    name: str
    change: Literal["added", "removed", "changed"]
    changed_fields: list[Literal["expected", "tolerance", "context"]] = Field(
        default_factory=list
    )
    before: GoldenQuoteExpected | None = None
    after: GoldenQuoteExpected | None = None
    before_tolerance: GoldenQuoteTolerance | None = None
    after_tolerance: GoldenQuoteTolerance | None = None
    before_context_hash: Sha256Hash | None = None
    after_context_hash: Sha256Hash | None = None
    steps: list[GoldenQuoteChangeStep] = Field(min_length=1)

    @model_validator(mode="after")
    def _consistent(self) -> Self:
        if (self.change == "changed") != bool(self.changed_fields):
            raise InputFreeError("changed_fields is non-empty exactly when change is 'changed'")
        versions = [step.version for step in self.steps]
        if versions != sorted(set(versions)):
            raise InputFreeError("steps are in strictly ascending version order")
        return self


class GoldenQuoteDelta(BaseModel):
    """What changed in the suite since the previous approved Rating Version's pin."""

    model_config = _FROZEN

    baseline_rating_version_ref: ArtifactRef | None = None
    baseline_suite_ref: ArtifactRef | None = None
    baseline_suite_content_hash: Sha256Hash | None = None
    changes: list[GoldenQuoteChange] = Field(default_factory=list)


class GoldenQuoteCheck(BaseModel):
    """The submit gate's record of a checked suite (FR-260)."""

    model_config = _FROZEN

    status: Literal["checked"]
    suite_ref: ArtifactRef
    suite_content_hash: Sha256Hash
    bundle_hash: Sha256Hash
    results: list[GoldenQuoteResult]
    delta: GoldenQuoteDelta


class GoldenQuoteNotChecked(BaseModel):
    """The explicit record that no golden quote was checked (DP-S2-4's interim rule)."""

    model_config = _FROZEN

    status: Literal["not_checked"]
    regression_suite: Literal["none"]
    message: Literal["no golden quotes were checked"]
    reason: Literal["no_algorithm_ref", "no_suite_for_algorithm"]


GoldenQuoteEvidence = Annotated[
    GoldenQuoteCheck | GoldenQuoteNotChecked, Field(discriminator="status")
]

__all__ = [
    "CasesLog",
    "GoldenQuote",
    "GoldenQuoteChange",
    "GoldenQuoteChangeStep",
    "GoldenQuoteCheck",
    "GoldenQuoteDelta",
    "GoldenQuoteEvidence",
    "GoldenQuoteExpected",
    "GoldenQuoteNotChecked",
    "GoldenQuoteResult",
    "GoldenQuoteTolerance",
    "LadderReconciles",
    "MonotoneInInput",
    "NoNullOutput",
    "PremiumBounded",
    "PremiumPositive",
    "PropertyCheck",
    "PropertyResult",
    "RegressionGeneration",
    "RegressionProperty",
    "RegressionRun",
    "RegressionSuite",
    "RegressionSuiteContent",
    "RegressionSuiteVersionCreate",
    "RunGeneration",
    "Sha256Hash",
    "cases_log_bytes",
    "cases_log_sha256",
    "context_hash",
    "suite_content_hash",
]
