"""Validation rules, rule sets and reports (`01` §4.3, §4.6).

The shapes behind `01` §1.3 — *a Model may only be fitted on a `validated` Dataset Version*.
A report is what makes that sentence checkable, so two things are computed here rather than
by whoever writes the report:

* **`overall`** is derived from the results and the acknowledgements, never set. A field a
  caller could assign is a field a caller could assign wrongly, and this one decides whether
  a dataset may be modelled on.
* **`severity_override` may only raise severity** (`warn → fail`), never lower it. Lowering
  means editing the rule, which is a reviewed and audited change (FR-DATA-21). An override
  that could weaken a rule set is a way to pass validation without changing anything a
  reviewer would see.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Final
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "ALL_LAYERS",
    "Acknowledgement",
    "OverallOutcome",
    "RuleOutcome",
    "RuleResult",
    "RuleSetEntry",
    "Severity",
    "ValidationLayer",
    "ValidationReport",
    "ValidationRule",
    "ValidationRuleSet",
]


class ValidationLayer(enum.StrEnum):
    """The four layers of FR-DATA-16, all of which a Rule Set must cover."""

    STRUCTURAL = "structural"
    REFERENTIAL = "referential"
    ACTUARIAL_SANITY = "actuarial_sanity"
    DISTRIBUTIONAL = "distributional"


ALL_LAYERS: Final[frozenset[ValidationLayer]] = frozenset(ValidationLayer)


class Severity(enum.StrEnum):
    """What a violation means. `warn` is not "ignore" — it needs an acknowledgement."""

    WARN = "warn"
    FAIL = "fail"


class RuleOutcome(enum.StrEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    ERROR = "error"
    SKIPPED = "skipped"


class OverallOutcome(enum.StrEnum):
    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    FAIL = "fail"
    ERROR = "error"


class ValidationRule(BaseModel):
    """One rule (`01` §4.3). A tagged union on `layer` + `check`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")
    version: int = Field(ge=1)
    layer: ValidationLayer
    check: str
    severity: Severity
    target: dict[str, Any] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    scope: dict[str, Any] = Field(default_factory=dict)
    tolerance: dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    rationale: str = ""
    status: str = "approved"


class RuleSetEntry(BaseModel):
    """A rule's membership of a set, with the one override that is permitted."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule: ValidationRule
    enabled: bool = True
    severity_override: Severity | None = None

    @model_validator(mode="after")
    def _an_override_may_only_raise(self) -> RuleSetEntry:
        """`01` §4.3's invariant, enforced where the override is expressed.

        `warn → fail` is a workspace tightening a shipped rule, which needs no review.
        `fail → warn` is a workspace deciding a failure is acceptable, which is a change to
        the rule and must go through the rule's own review (FR-DATA-21). Allowing it here
        would be a way to pass validation without changing anything a reviewer sees.
        """
        if (
            self.severity_override is Severity.WARN
            and self.rule.severity is Severity.FAIL
        ):
            raise ValueError(
                f"severity_override on {self.rule.slug!r} would lower fail to warn. "
                "Lowering severity means editing the rule, which is a reviewed change "
                "(FR-DATA-21); an override may only raise."
            )
        return self

    @property
    def effective_severity(self) -> Severity:
        return self.severity_override or self.rule.severity


class ValidationRuleSet(BaseModel):
    """A versioned set of rules for a Dataset (`01` §4.3, FR-DATA-22)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: str
    version: int = Field(ge=1)
    dataset_id: UUID | None = None
    entries: tuple[RuleSetEntry, ...] = ()
    reference_dataset_version_id: UUID | None = None
    status: str = "approved"

    @property
    def enabled_entries(self) -> tuple[RuleSetEntry, ...]:
        return tuple(e for e in self.entries if e.enabled)

    @property
    def covered_layers(self) -> frozenset[ValidationLayer]:
        return frozenset(e.rule.layer for e in self.enabled_entries)

    @property
    def empty_layers(self) -> frozenset[ValidationLayer]:
        """FR-DATA-16: every layer must be present; an empty one is a configuration warning.

        A warning rather than an error because a dataset with no reference tables genuinely
        has nothing referential to check — but silence would let a rule set lose its whole
        distributional layer in an edit and look complete.
        """
        return ALL_LAYERS - self.covered_layers


class Acknowledgement(BaseModel):
    """A Principal accepting a warning, on this report (FR-DATA-17, FR-DATA-18)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    user_id: UUID
    at: datetime
    justification: str = Field(min_length=1)


class RuleResult(BaseModel):
    """One rule's outcome (`01` §4.6, FR-DATA-20)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: UUID
    rule_slug: str
    rule_version: int
    layer: ValidationLayer
    severity: Severity
    outcome: RuleOutcome

    measured: dict[str, Any] = Field(default_factory=dict)
    threshold: dict[str, Any] = Field(default_factory=dict)
    affected_rows: int | None = None
    affected_exposure_fraction: float | None = None
    detail: str = ""
    #: Up to 100 primary keys (FR-DATA-20). Capped because a failing rule on five million
    #: rows would otherwise put five million keys in a report somebody has to open.
    offending_sample: tuple[str, ...] = ()
    error_reason: str | None = None
    acknowledgement: Acknowledgement | None = None

    @property
    def needs_acknowledgement(self) -> bool:
        return self.outcome is RuleOutcome.WARN and self.acknowledgement is None


class ValidationReport(BaseModel):
    """The outcome of one validation run (`01` §4.6)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    dataset_version_id: UUID
    rule_set_id: UUID
    rule_set_version: int
    job_id: UUID | None = None
    started_at: datetime
    finished_at: datetime
    results: tuple[RuleResult, ...] = ()
    reference_dataset_version_id: UUID | None = None
    empty_layers: tuple[ValidationLayer, ...] = ()

    @property
    def counts(self) -> dict[str, int]:
        counts = dict.fromkeys((o.value for o in RuleOutcome), 0)
        for result in self.results:
            counts[result.outcome.value] += 1
        return counts

    @property
    def unacknowledged_warnings(self) -> int:
        return sum(1 for r in self.results if r.needs_acknowledgement)

    @property
    def overall(self) -> OverallOutcome:
        """Derived, never assigned (`01` §4.6's invariants).

        An `error` is not a pass: FR-DATA-19 is explicit that an unrun rule is never
        treated as a pass, because "the rule that would have caught it timed out" and "the
        rule passed" must never look the same in a report an actuary relies on.
        """
        outcomes = {r.outcome for r in self.results}
        if RuleOutcome.ERROR in outcomes:
            return OverallOutcome.ERROR
        if RuleOutcome.FAIL in outcomes:
            return OverallOutcome.FAIL
        if RuleOutcome.WARN in outcomes:
            return (
                OverallOutcome.PASS_WITH_WARNINGS
                if self.unacknowledged_warnings == 0
                else OverallOutcome.FAIL
            )
        return OverallOutcome.PASS

    @property
    def permits_validation(self) -> bool:
        """`01` §4.6: the transition to `validated` is permitted for `pass` and
        `pass_with_warnings` only — the single question `01` §1.3 asks of a report."""
        return self.overall in {OverallOutcome.PASS, OverallOutcome.PASS_WITH_WARNINGS}
