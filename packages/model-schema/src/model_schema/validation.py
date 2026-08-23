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
from collections.abc import Mapping
from datetime import datetime
from types import MappingProxyType
from typing import Any, Final
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

__all__ = [
    "ALL_LAYERS",
    "BUILTIN_RULES",
    "Acknowledgement",
    "BuiltinRule",
    "OverallOutcome",
    "RuleOutcome",
    "RuleResult",
    "RuleSetEntry",
    "Severity",
    "ValidationLayer",
    "ValidationReport",
    "ValidationRule",
    "ValidationRuleSet",
    "builtin_rule",
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

    @computed_field  # type: ignore[prop-decorator]
    @property
    def empty_layers(self) -> tuple[ValidationLayer, ...]:
        """FR-DATA-16: every layer must be present; an empty one is a configuration warning.

        A warning rather than an error because a dataset with no reference tables genuinely
        has nothing referential to check — but silence would let a rule set lose its whole
        distributional layer in an edit and look complete.

        **Computed, so it reaches the API.** A plain `@property` is not serialised, so the
        contract carried no such field and the screen FR-DATA-16 names as the place to
        surface the warning had nothing to surface — while `ValidationReport` beside it
        carried the same list as an ordinary field. A client deriving it from `entries`
        would be a second implementation of the rule, which is what `CLAUDE.md` §2 forbids.

        Sorted, and a tuple rather than a set, because a JSON array has an order and an
        unordered one would make two identical rule sets serialise differently.
        """
        return tuple(sorted(ALL_LAYERS - self.covered_layers))


#: The layer each catalogue-id prefix belongs to. Derived rather than listed per rule: the
#: prefix *is* the layer (`01` §4.4's four tables are the four layers of FR-DATA-16), and a
#: rule carrying both could carry them inconsistently.
_LAYER_BY_PREFIX: Final[Mapping[str, ValidationLayer]] = MappingProxyType(
    {
        "STR": ValidationLayer.STRUCTURAL,
        "REF": ValidationLayer.REFERENTIAL,
        "ACT": ValidationLayer.ACTUARIAL_SANITY,
        "DST": ValidationLayer.DISTRIBUTIONAL,
    }
)


class BuiltinRule(BaseModel):
    """One rule the platform ships, from `01` §4.4's catalogue (FR-DATA-53).

    Distinct from `ValidationRule`, which is a *stored* rule: it carries a workspace-scoped
    `id` and a `version`, and a built-in rule has neither until it is seeded into a
    workspace. Keeping them apart is what stops the catalogue needing a fabricated UUID at
    import time.

    Thresholds are deliberately absent. `01` §4.4 — "Thresholds are Rule Set configuration,
    not code. Every threshold shown is a default." — and a catalogue that carried them
    would be a second place a threshold is written.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    catalogue_id: str = Field(pattern=r"^VR-(STR|REF|ACT|DST)-\d{1,2}$")
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")
    #: The registered check this rule runs — `pricing_core.data.validate.CHECKS`. **Not**
    #: derivable from the slug: nine of the 38 differ, and `range` backs three of them.
    check: str
    severity: Severity
    #: `01` §4.4's third column, trimmed to one line. The spec's own wording, so that a
    #: reader comparing the two can see they are the same rule.
    summary: str

    @property
    def layer(self) -> ValidationLayer:
        return _LAYER_BY_PREFIX[self.catalogue_id.split("-")[1]]


def _rule(
    catalogue_id: str, slug: str, check: str, severity: Severity, summary: str
) -> BuiltinRule:
    return BuiltinRule(
        catalogue_id=catalogue_id, slug=slug, check=check, severity=severity, summary=summary
    )


_W, _F = Severity.WARN, Severity.FAIL

#: `01` §4.4's catalogue, in the order the spec lists it. Keyed by catalogue id because that
#: is the identifier `01` §4.4 calls stable and says workflows and the UI reference.
#:
#: A rule appears here and nowhere else. Before this constant existed the ids lived only in
#: prose, and `scripts/scope-audit.py DATA --catalogue VR` scored 1 of 38 — the one hit being
#: a `VR-STR-5` mention inside another rule's skip message, which is to say zero.
BUILTIN_RULES: Final[Mapping[str, BuiltinRule]] = MappingProxyType(
    {
        r.catalogue_id: r
        for r in (
            _rule(
                "VR-STR-1", "column-presence", "column_presence", _F,
                "Every column declared in the schema exists",
            ),
            _rule(
                "VR-STR-2", "dtype-match", "dtype_match", _F,
                "Each column's Arrow dtype matches the declaration (no silent coercion)",
            ),
            _rule(
                "VR-STR-3", "nullability", "not_null", _F,
                "Columns declared non-nullable contain no nulls",
            ),
            _rule(
                "VR-STR-4", "primary-key-unique", "unique_key", _F,
                "Declared primary key is unique and non-null (policy id x exposure period)",
            ),
            _rule(
                "VR-STR-5", "date-parse", "date_parsed", _F,
                "All date columns parsed to date32/timestamp with no fallback-to-string",
            ),
            _rule(
                "VR-STR-6", "encoding", "encoding", _W,
                "No mojibake / invalid UTF-8 sequences in string columns",
            ),
            _rule(
                "VR-STR-7", "allowed-values", "allowed_values", _F,
                "Categorical columns contain only values in the declared domain",
            ),
            _rule(
                "VR-STR-8", "no-unexpected-columns", "no_unexpected_columns", _W,
                "No columns present that are absent from the schema",
            ),
            _rule(
                "VR-STR-9", "reject-rate", "reject_rate", _F,
                "Quarantined rows <= threshold (default 0.1 % of rows read) - FR-DATA-7",
            ),
            _rule(
                "VR-REF-1", "reference-resolve", "reference_lookup", _F,
                "Every value of a reference-backed column resolves in the pinned Reference "
                "Table Version, evaluated as at the declared date column (FR-DATA-31)",
            ),
            _rule(
                "VR-REF-2", "reference-coverage", "reference_coverage", _W,
                "At least X % of reference table keys are exercised by the data (catches a "
                "stale or wrong reference version)",
            ),
            _rule(
                "VR-REF-3", "effective-date-in-range", "effective_date_in_range", _F,
                "The declared as-at date lies within the Reference Table Version's covered "
                "period",
            ),
            _rule(
                "VR-REF-4", "cross-table-key", "cross_table_key", _F,
                "Every claim.policy_id exists in policy_exposure",
            ),
            _rule(
                "VR-REF-5", "code-list-drift", "code_list_drift", _W,
                "New codes present that did not exist in the reference dataset version",
            ),
            _rule(
                "VR-ACT-1", "exposure-positive", "range", _F,
                "exposure_years > 0 for every row",
            ),
            _rule(
                "VR-ACT-2", "exposure-plausible", "range", _F,
                "exposure_years <= 1.05 per row; annual policies sum to about 1.0 per "
                "policy year",
            ),
            _rule(
                "VR-ACT-3", "exposure-period-consistent", "period_consistent", _F,
                "exposure_end > exposure_start; exposure_years is about "
                "(end - start)/365.25 within tolerance",
            ),
            _rule(
                "VR-ACT-4", "no-overlapping-exposure", "no_overlap", _F,
                "A single policy_id has no overlapping exposure intervals",
            ),
            _rule(
                "VR-ACT-5", "claim-date-in-exposure", "claim_date_in_exposure", _F,
                "date_of_loss is in [exposure_start, exposure_end) for the linked row "
                "(FR-DATA-12)",
            ),
            _rule(
                "VR-ACT-6", "claim-linkage-complete", "claim_linkage_complete", _F,
                "100 % of claims link to exactly one exposure row",
            ),
            _rule(
                "VR-ACT-7", "claim-not-multi-linked", "claim_not_multi_linked", _F,
                "No claim links to more than one exposure row",
            ),
            _rule(
                "VR-ACT-8", "claim-count-non-negative", "range", _F,
                "claim_count >= 0, integer",
            ),
            _rule(
                "VR-ACT-9", "claim-amount-sign", "claim_amount_sign", _W,
                "Negative incurred amounts exist only where recoveries/reversals are "
                "expected; flagged with counts",
            ),
            _rule(
                "VR-ACT-10", "severity-outlier", "severity_outlier", _W,
                "Claims above a configurable threshold (absolute, or a percentile of the "
                "peril's own distribution) are flagged for large-loss treatment - never "
                "auto-removed",
            ),
            _rule(
                "VR-ACT-11", "frequency-plausible", "frequency_plausible", _W,
                "Portfolio and per-peril frequency within a configured band (e.g. motor AD "
                "0.02-0.25)",
            ),
            _rule(
                "VR-ACT-12", "severity-plausible", "severity_plausible", _W,
                "Portfolio and per-peril mean severity within a configured band",
            ),
            _rule(
                "VR-ACT-13", "zero-claim-cohort", "zero_claim_cohort", _W,
                "No factor level with material exposure (> 1 % of total) has exactly zero "
                "claims where the prior version had claims",
            ),
            _rule(
                "VR-ACT-14", "development-maturity", "development_maturity", _W,
                "The most recent N months of experience are flagged as immature (IBNR risk) "
                "with the configured development pattern; modelling on them without an "
                "adjustment is a warning",
            ),
            _rule(
                "VR-ACT-15", "currency-consistency", "currency_consistency", _F,
                "All monetary columns share the Dataset's declared currency; no "
                "mixed-currency rows",
            ),
            _rule(
                "VR-ACT-16", "duplicate-claim", "duplicate_claim", _W,
                "No two claims share (policy, date_of_loss, peril, amount) - a classic "
                "double-load signature",
            ),
            # `01` §4.4 gives this rule's severity cell as "the rule's own severity, at
            # `warn_above`" rather than a plain token. The 2026-08-15 amendment immediately
            # below the tables settled that a rule carries **one** severity and that neither
            # two-band form is reachable — a check reports pass or fail and `_run_one` maps
            # that through the rule's static severity. The catalogue therefore records
            # `warn`; nothing is lost in the transcription.
            _rule(
                "VR-DST-1", "psi-column", "psi_column", _W,
                "Per-column PSI against the reference version, for categorical, ordinal and "
                "boolean columns only",
            ),
            _rule(
                "VR-DST-2", "new-level", "new_level", _W,
                "Categorical levels present now, absent in reference",
            ),
            _rule(
                "VR-DST-3", "vanished-level", "vanished_level", _W,
                "Levels with material reference exposure now absent",
            ),
            _rule(
                "VR-DST-4", "null-rate-shift", "null_rate_shift", _W,
                "Null rate moved by more than X percentage points (a broken feed's clearest "
                "signal)",
            ),
            _rule(
                "VR-DST-5", "volume-shift", "volume_shift", _W,
                "Row count against the reference version's row count",
            ),
            _rule(
                "VR-DST-6", "mean-shift", "mean_shift", _W,
                "Numeric column mean moved more than N reference standard errors",
            ),
            _rule(
                "VR-DST-7", "target-rate-shift", "target_rate_shift", _W,
                "Observed frequency / severity / burning cost moved more than X % vs "
                "reference",
            ),
            _rule(
                "VR-DST-8", "mix-shift-exposure", "mix_shift_exposure", _W,
                "Exposure distribution across a declared key factor moved (PSI on the "
                "exposure weights, not the row counts)",
            ),
        )
    }
)


def builtin_rule(catalogue_id: str) -> BuiltinRule:
    """One catalogue entry by its `01` §4.4 id.

    Raises rather than returning `None` because every call site has a specific id in hand;
    a missing one means the caller's id is wrong, not that there is nothing to return.
    """
    try:
        return BUILTIN_RULES[catalogue_id]
    except KeyError:
        raise ValueError(
            f"unknown built-in rule {catalogue_id!r}; the catalogue is `01` §4.4's 38 rules, "
            "and a workspace's own rules are stored, not defined here"
        ) from None


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
        """Derived, never assigned, and **from the rule results alone** (`01` §4.6).

        An `error` is not a pass: FR-DATA-19 is explicit that an unrun rule is never
        treated as a pass, because "the rule that would have caught it timed out" and "the
        rule passed" must never look the same in a report an actuary relies on. `fail`
        outranks `error` when both are present — a definite failure is more actionable than
        "a rule could not tell", and both block promotion identically.

        **Corrected 2026-08-17 (W5, the `wf-01` journey test).** This property had been
        wrong since `01` §4.6 was amended on 2026-08-14: it ranked `error` above `fail`, and
        it folded acknowledgements in, returning `fail` for a report whose warnings were not
        yet acknowledged. That is the *"pass_with_warnings iff every warn has an
        acknowledgement"* rule the amendment removed, for the reason it gives — a verdict
        that changes when somebody clicks acknowledge cannot live in an immutable artifact.

        The consequence was a **deadlock**, and nothing had produced the state that reveals
        it. `dataset.validate` concludes a failed validation from `permits_validation`, so a
        report with any warning drove its version to `failed`; acknowledgement happens
        afterwards, against a report whose version can no longer be promoted, and
        re-validating produces a new report whose warnings are unacknowledged again. **Any
        dataset version with a single warning could never reach `validated`.** Every fixture
        in the suite produced all-pass or a hard fail; `wf-01` B8/B9 is the first thing that
        asked for a warning and an acknowledgement, which is what a journey test is for.

        Acknowledgement remains what it always was: a fact *about* a report, checked at
        promotion (FR-DATA-17) through `unacknowledged_warnings`, never inside `overall`.
        """
        outcomes = {r.outcome for r in self.results}
        if RuleOutcome.FAIL in outcomes:
            return OverallOutcome.FAIL
        if RuleOutcome.ERROR in outcomes:
            return OverallOutcome.ERROR
        if RuleOutcome.WARN in outcomes:
            return OverallOutcome.PASS_WITH_WARNINGS
        return OverallOutcome.PASS

    @property
    def permits_validation(self) -> bool:
        """`01` §4.6: the transition to `validated` is permitted for `pass` and
        `pass_with_warnings` only — the single question `01` §1.3 asks of a report."""
        return self.overall in {OverallOutcome.PASS, OverallOutcome.PASS_WITH_WARNINGS}
