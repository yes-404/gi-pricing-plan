"""The validation engine (`01` §3.3, §5.2, FR-DATA-15/16/19/20/22).

> **`01` §1.3** — A Model may only be fitted on a Dataset Version whose status is
> `validated`. There is no override, no "force fit", and no admin bypass.

This is the engine that decides. Four properties of it are load-bearing:

* **Rules are independent** (FR-DATA-19). Each runs inside its own guard; one rule raising
  does not stop the rest. A run that abandoned the remaining rules after the first error
  would report a dataset as having one problem when it has nine.
* **An unrun rule is never a pass** (FR-DATA-19). A timeout or an exception is recorded as
  `error`, and an `error` anywhere makes the report `error`. "The rule that would have
  caught it timed out" and "the rule passed" must never look the same.
* **Every non-pass carries its evidence** (FR-DATA-20): the measured value against the
  threshold, the affected row count, and up to 100 offending keys — enough for an actuary
  to decide whether the rule or the data is wrong.
* **It is pure.** Frames in, report out (ADR-0001). The same rule set can be run against a
  CSV in a notebook, which is how a disputed failure gets settled.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Final
from uuid import UUID, uuid4

import polars as pl

from model_schema import (
    RuleOutcome,
    RuleResult,
    Severity,
    ValidationReport,
    ValidationRule,
    ValidationRuleSet,
)
from pricing_core.progress import ProgressCallback

__all__ = ["CHECKS", "CheckOutcome", "register_check", "run_validation"]

#: FR-DATA-20 caps the Offending Sample at 100 keys. A failing rule on five million rows
#: would otherwise put five million keys into a report somebody has to open.
MAX_OFFENDING_SAMPLE: Final = 100

#: Per-rule budget (FR-DATA-19). Exceeding it is an `error` with reason `timeout`, not a
#: pass and not a silent skip.
DEFAULT_RULE_BUDGET_S: Final = 60.0


@dataclass(frozen=True)
class CheckOutcome:
    """What a check function reports. The engine turns this into a `RuleResult`.

    A check says *what it measured*, never what it means: whether 17 violating rows is a
    warning or a failure is the rule's severity and the rule set's override, and a check
    that decided for itself would make those settings decorative.
    """

    violating_rows: int = 0
    measured: dict[str, Any] | None = None
    threshold: dict[str, Any] | None = None
    detail: str = ""
    offending_sample: tuple[str, ...] = ()
    affected_exposure_fraction: float | None = None
    skipped: bool = False
    skip_reason: str = ""


CheckFunction = Callable[
    [ValidationRule, Mapping[str, pl.DataFrame], "ValidationContext"], CheckOutcome
]


@dataclass(frozen=True)
class ValidationContext:
    """Everything a check may consult beyond the tables under test."""

    reference_tables: Mapping[str, pl.DataFrame]
    reference_frames: Mapping[str, pl.DataFrame]
    exposure_column: str = "exposure_years"


CHECKS: dict[str, CheckFunction] = {}


def register_check(name: str) -> Callable[[CheckFunction], CheckFunction]:
    """Register a check implementation under the name rules refer to.

    Refuses a duplicate: two implementations of one check name means the behaviour depends
    on import order, and a validation engine whose meaning depends on import order is one
    nobody can reason about.
    """

    def decorator(function: CheckFunction) -> CheckFunction:
        if name in CHECKS:
            raise ValueError(f"a check named {name!r} is already registered")
        CHECKS[name] = function
        return function

    return decorator


def _table(tables: Mapping[str, pl.DataFrame], rule: ValidationRule) -> pl.DataFrame:
    name = rule.target.get("table")
    if name is None:
        raise KeyError(f"rule {rule.slug!r} declares no target table")
    if name not in tables:
        raise KeyError(f"rule {rule.slug!r} targets table {name!r}, which is not present")
    return tables[name]


def _sample(frame: pl.DataFrame, keys: Sequence[str]) -> tuple[str, ...]:
    """Up to 100 primary keys from the offending rows (FR-DATA-20)."""
    usable = [k for k in keys if k in frame.columns]
    if not usable or frame.height == 0:
        return ()
    head = frame.select(usable).head(MAX_OFFENDING_SAMPLE)
    return tuple(
        "|".join("" if v is None else str(v) for v in row)
        for row in head.iter_rows()
    )


# -- Layer 1: structural -------------------------------------------------------------------


@register_check("column_presence")
def _column_presence(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-STR-1: every declared column exists."""
    frame = _table(tables, rule)
    expected = list(rule.params.get("columns", []))
    missing = [c for c in expected if c not in frame.columns]
    return CheckOutcome(
        violating_rows=len(missing),
        measured={"missing": missing},
        threshold={"missing": 0},
        detail="" if not missing else f"absent columns: {missing}",
    )


@register_check("not_null")
def _not_null(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-STR-3: columns declared non-nullable contain no nulls."""
    frame = _table(tables, rule)
    column = rule.target["column"]
    offending = frame.filter(pl.col(column).is_null())
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"null_rows": offending.height},
        threshold={"null_rows": 0},
        detail=f"{offending.height} null value(s) in {column!r}",
        offending_sample=_sample(offending, rule.params.get("key_columns", [])),
    )


@register_check("unique_key")
def _unique_key(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-STR-4: the declared primary key is unique and non-null."""
    frame = _table(tables, rule)
    key = list(rule.params.get("columns", []))
    if not key:
        raise ValueError(f"rule {rule.slug!r} declares no key columns")
    duplicated = frame.filter(frame.select(key).is_duplicated())
    return CheckOutcome(
        violating_rows=duplicated.height,
        measured={"duplicate_rows": duplicated.height},
        threshold={"duplicate_rows": 0},
        detail=f"{duplicated.height} row(s) share a primary key {key}",
        offending_sample=_sample(duplicated, key),
    )


@register_check("allowed_values")
def _allowed_values(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-STR-7: categorical columns contain only declared values."""
    frame = _table(tables, rule)
    column = rule.target["column"]
    allowed = set(rule.params.get("values", []))
    offending = frame.filter(
        pl.col(column).is_not_null() & ~pl.col(column).is_in(list(allowed))
    )
    unexpected = sorted(
        {str(v) for v in offending.get_column(column).unique().to_list()}
    )[:20]
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"unexpected_values": unexpected},
        threshold={"allowed": sorted(allowed)},
        detail="" if not unexpected else f"values outside the declared domain: {unexpected}",
        offending_sample=_sample(offending, rule.params.get("key_columns", [])),
    )


# -- Layer 2: referential ------------------------------------------------------------------


@register_check("cross_table_key")
def _cross_table_key(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-REF-4: every `claim.policy_id` exists in `policy_exposure`."""
    frame = _table(tables, rule)
    column = rule.target["column"]
    other_name = rule.params["references_table"]
    other_column = rule.params["references_column"]
    if other_name not in tables:
        return CheckOutcome(skipped=True, skip_reason=f"{other_name!r} is not present")

    known = tables[other_name].get_column(other_column).unique()
    offending = frame.filter(pl.col(column).is_not_null() & ~pl.col(column).is_in(known))
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"unresolved_rows": offending.height},
        threshold={"unresolved_rows": 0},
        detail=(
            f"{offending.height} row(s) reference a {other_name}.{other_column} "
            "that does not exist"
        ),
        offending_sample=_sample(offending, [column]),
    )


# -- Layer 3: actuarial sanity ---------------------------------------------------------------


@register_check("range")
def _range(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-1/2/8: a numeric column inside declared bounds.

    Bounds are named for their inclusivity because `exposure_years > 0` and
    `exposure_years >= 0` differ by exactly the rows that break a frequency offset.
    """
    frame = _table(tables, rule)
    column = rule.target["column"]
    params = rule.params
    predicate = pl.lit(False)

    if (value := params.get("min_exclusive")) is not None:
        predicate = predicate | (pl.col(column) <= value)
    if (value := params.get("min_inclusive")) is not None:
        predicate = predicate | (pl.col(column) < value)
    if (value := params.get("max_exclusive")) is not None:
        predicate = predicate | (pl.col(column) >= value)
    if (value := params.get("max_inclusive")) is not None:
        predicate = predicate | (pl.col(column) > value)

    offending = frame.filter(pl.col(column).is_not_null() & predicate)
    exposure_fraction = _exposure_fraction(frame, offending, ctx.exposure_column)
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"violating_rows": offending.height},
        threshold={k: v for k, v in params.items() if k.startswith(("min_", "max_"))},
        detail=f"{offending.height} row(s) outside the declared range for {column!r}",
        offending_sample=_sample(offending, params.get("key_columns", [])),
        affected_exposure_fraction=exposure_fraction,
    )


@register_check("period_consistent")
def _period_consistent(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-3: `exposure_end > exposure_start`."""
    frame = _table(tables, rule)
    start, end = rule.params["start_column"], rule.params["end_column"]
    offending = frame.filter(
        pl.col(start).is_not_null() & pl.col(end).is_not_null() & (pl.col(end) <= pl.col(start))
    )
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"violating_rows": offending.height},
        threshold={"rule": f"{end} > {start}"},
        detail=f"{offending.height} row(s) end on or before they start",
        offending_sample=_sample(offending, rule.params.get("key_columns", [])),
    )


@register_check("no_overlap")
def _no_overlap(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-4: one `policy_id` has no overlapping exposure intervals.

    Overlapping exposure double-counts a policy's time at risk, which inflates the
    denominator of every frequency and is invisible in a row count.
    """
    frame = _table(tables, rule)
    key = rule.params["key_column"]
    start, end = rule.params["start_column"], rule.params["end_column"]

    ordered = frame.sort([key, start])
    with_previous = ordered.with_columns(
        pl.col(end).shift(1).over(key).alias("_previous_end"),
        pl.col(key).shift(1).over(key).alias("_previous_key"),
    )
    offending = with_previous.filter(
        pl.col("_previous_key").is_not_null() & (pl.col(start) < pl.col("_previous_end"))
    )
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"overlapping_rows": offending.height},
        threshold={"overlapping_rows": 0},
        detail=f"{offending.height} exposure interval(s) overlap a previous one",
        offending_sample=_sample(offending, [key]),
    )


def _exposure_fraction(
    frame: pl.DataFrame, offending: pl.DataFrame, exposure_column: str
) -> float | None:
    """What share of exposure the violation touches (FR-DATA-20).

    Row counts mislead: 17 rows out of five million sounds negligible until they carry 8 %
    of the exposure, which is the number an actuary needs to judge the rule.
    """
    if exposure_column not in frame.columns or frame.height == 0:
        return None
    total = frame.get_column(exposure_column).cast(pl.Float64, strict=False).sum()
    if not total:
        return None
    affected = offending.get_column(exposure_column).cast(pl.Float64, strict=False).sum()
    return float(affected or 0.0) / float(total)


# -- Layer 4: distributional -----------------------------------------------------------------


@register_check("null_rate_shift")
def _null_rate_shift(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-DST-4: the null rate moved — a broken feed's clearest signal."""
    frame = _table(tables, rule)
    name = rule.target["table"]
    column = rule.target["column"]
    reference = ctx.reference_frames.get(name)
    if reference is None or column not in reference.columns:
        return CheckOutcome(skipped=True, skip_reason="no reference version to compare against")

    current = frame.get_column(column).null_count() / max(frame.height, 1)
    before = reference.get_column(column).null_count() / max(reference.height, 1)
    shift = abs(current - before)
    limit = float(rule.params.get("max_shift_pp", 5.0)) / 100.0
    return CheckOutcome(
        violating_rows=1 if shift > limit else 0,
        measured={"null_rate": round(current, 6), "reference_null_rate": round(before, 6),
                  "shift_pp": round(shift * 100, 3)},
        threshold={"max_shift_pp": rule.params.get("max_shift_pp", 5.0)},
        detail=f"null rate moved {shift * 100:.2f}pp against the reference version",
    )


@register_check("volume_shift")
def _volume_shift(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-DST-5: total row count or exposure moved more than X % against reference."""
    frame = _table(tables, rule)
    name = rule.target["table"]
    reference = ctx.reference_frames.get(name)
    if reference is None or reference.height == 0:
        return CheckOutcome(skipped=True, skip_reason="no reference version to compare against")

    ratio = frame.height / reference.height
    limit = float(rule.params.get("max_shift_fraction", 0.2))
    return CheckOutcome(
        violating_rows=1 if abs(ratio - 1.0) > limit else 0,
        measured={"rows": frame.height, "reference_rows": reference.height,
                  "ratio": round(ratio, 4)},
        threshold={"max_shift_fraction": limit},
        detail=f"row count is {ratio:.2f} times the reference version",
    )


# -- the engine ------------------------------------------------------------------------------


def run_validation(
    tables: Mapping[str, pl.DataFrame],
    rule_set: ValidationRuleSet,
    *,
    dataset_version_id: UUID,
    reference_tables: Mapping[str, pl.DataFrame] | None = None,
    reference_frames: Mapping[str, pl.DataFrame] | None = None,
    exposure_column: str = "exposure_years",
    rule_budget_s: float = DEFAULT_RULE_BUDGET_S,
    progress: ProgressCallback | None = None,
) -> ValidationReport:
    """Execute every enabled rule and produce exactly one report (FR-DATA-15).

    Rules run independently (FR-DATA-19): each is guarded, and a rule that raises or
    exceeds its budget becomes an `error` rather than stopping the run or being skipped.
    """
    started = datetime.now(UTC)
    context = ValidationContext(
        reference_tables=reference_tables or {},
        reference_frames=reference_frames or {},
        exposure_column=exposure_column,
    )
    entries = rule_set.enabled_entries
    results: list[RuleResult] = []

    for index, entry in enumerate(entries):
        if progress is not None:
            progress.check_cancelled()
            progress.update(
                index / max(len(entries), 1),
                f"validating: {entry.rule.slug}",
                rules=index,
            )
        results.append(_run_one(entry, tables, context, rule_budget_s))

    return ValidationReport(
        id=uuid4(),
        dataset_version_id=dataset_version_id,
        rule_set_id=rule_set.id,
        rule_set_version=rule_set.version,
        started_at=started,
        finished_at=datetime.now(UTC),
        results=tuple(results),
        reference_dataset_version_id=rule_set.reference_dataset_version_id,
        empty_layers=tuple(sorted(rule_set.empty_layers)),
    )


def _run_one(
    entry: Any,
    tables: Mapping[str, pl.DataFrame],
    context: ValidationContext,
    budget_s: float,
) -> RuleResult:
    rule = entry.rule
    severity = entry.effective_severity

    def failed(reason: str, detail: str) -> RuleResult:
        # FR-DATA-19: an unrun rule is never a pass. `error`, with the reason, so a report
        # can never make "the rule that would have caught it timed out" look like "passed".
        return RuleResult(
            rule_id=rule.id, rule_slug=rule.slug, rule_version=rule.version,
            layer=rule.layer, severity=severity, outcome=RuleOutcome.ERROR,
            detail=detail, error_reason=reason,
        )

    check = CHECKS.get(rule.check)
    if check is None:
        return failed("unknown_check", f"no implementation registered for {rule.check!r}")

    started = time.perf_counter()
    try:
        outcome = check(rule, tables, context)
    except Exception as exc:
        return failed(type(exc).__name__, f"{type(exc).__name__}: {exc}")

    elapsed = time.perf_counter() - started
    if elapsed > budget_s:
        return failed(
            "timeout",
            f"rule exceeded its {budget_s:g}s budget ({elapsed:.1f}s) — recorded as error "
            "because an unrun rule is never a pass (FR-DATA-19)",
        )

    if outcome.skipped:
        return RuleResult(
            rule_id=rule.id, rule_slug=rule.slug, rule_version=rule.version,
            layer=rule.layer, severity=severity, outcome=RuleOutcome.SKIPPED,
            detail=outcome.skip_reason,
        )

    tolerated = int(rule.tolerance.get("max_violating_rows", 0))
    violating = outcome.violating_rows
    passed = violating <= tolerated

    return RuleResult(
        rule_id=rule.id,
        rule_slug=rule.slug,
        rule_version=rule.version,
        layer=rule.layer,
        severity=severity,
        outcome=(
            RuleOutcome.PASS
            if passed
            else (RuleOutcome.WARN if severity is Severity.WARN else RuleOutcome.FAIL)
        ),
        measured=outcome.measured or {},
        threshold=outcome.threshold or {},
        affected_rows=None if passed else violating,
        affected_exposure_fraction=outcome.affected_exposure_fraction,
        detail=outcome.detail if not passed else "",
        offending_sample=outcome.offending_sample if not passed else (),
    )
