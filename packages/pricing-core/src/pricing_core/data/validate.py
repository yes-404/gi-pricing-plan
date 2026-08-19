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
from datetime import UTC, date, datetime, timedelta
from typing import Any, Final
from uuid import UUID, uuid4

import polars as pl

from model_schema import (
    Profile,
    RuleOutcome,
    RuleResult,
    Severity,
    ValidationReport,
    ValidationRule,
    ValidationRuleSet,
)
from pricing_core.data.profile import TOP_LEVELS
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
    #: The reference version's stored Profile (FR-DATA-24). Distributional rules answer
    #: from these aggregates rather than re-scanning the reference dataset — a null rate
    #: and a row count are both already in a Profile, and loading ten million rows to
    #: recompute one of them is the re-scan the requirement exists to avoid.
    reference_profile: Profile | None = None


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


def _as_date(value: Any) -> date:
    """A rule parameter's as-at value as a date. JSON has no date type, so it arrives as a
    string and comparing it to a `date` would silently never match."""
    return value if isinstance(value, date) else date.fromisoformat(str(value))


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
    """VR-STR-1: every declared column exists.

    Skips when nothing is declared rather than passing. A rule with an empty column list
    checked nothing, and reporting that as a pass puts a green tick against a question
    nobody asked — which is indistinguishable, on the report, from the column being there.
    """
    frame = _table(tables, rule)
    expected = list(rule.params.get("columns", []))
    if not expected:
        return CheckOutcome(skipped=True, skip_reason="no columns declared to check for")
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
    """VR-STR-7 / `set_membership`: categorical columns contain only declared values.

    `allowed` is the name `01` §4.5 gives the parameter; `values` is accepted because the
    first implementation used it and rule sets may already carry it.

    **Skips when no domain is declared, rather than failing every row.** It read the wrong
    parameter name for its whole life, so the declared domain was always empty and every
    value was "outside" it — a rule that refuses an entire dataset while naming, as
    offenders, values the author had explicitly allowed. Found by seeding freMTPL2.
    """
    frame = _table(tables, rule)
    column = rule.target["column"]
    declared = rule.params.get("allowed", rule.params.get("values"))
    if not declared:
        return CheckOutcome(
            skipped=True,
            skip_reason=(
                "no allowed values declared — an empty domain would refuse every row "
                "(`01` §4.5 names this parameter `allowed`)"
            ),
        )
    allowed = {str(value) for value in declared}
    if not rule.params.get("case_sensitive", True):
        allowed = {value.casefold() for value in allowed}
        frame = frame.with_columns(pl.col(column).str.to_lowercase().alias(column))
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


@register_check("dtype_match")
def _dtype_match(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-STR-2: each column's dtype matches the declaration, with no silent coercion.

    A whole-table check, so `violating_rows` counts *columns* — a dtype is a property of a
    column and reporting "3 400 000 rows are Int64" would be true and useless.

    The failure this exists for is quiet: a policy id read as `Int64` in one version and
    `String` in the next joins to nothing, and the symptom appears three steps later as a
    claim linkage rate of zero.
    """
    frame = _table(tables, rule)
    declared: Mapping[str, str] = rule.params.get("columns", {})
    if not declared:
        return CheckOutcome(skipped=True, skip_reason="no dtypes declared to match against")

    mismatched = {
        name: {"declared": expected, "actual": str(frame.schema[name])}
        for name, expected in declared.items()
        if name in frame.columns and str(frame.schema[name]).lower() != expected.lower()
    }
    return CheckOutcome(
        violating_rows=len(mismatched),
        measured={"mismatched_columns": mismatched},
        threshold={"columns": dict(declared)},
        detail=(
            f"{len(mismatched)} column(s) do not match their declared dtype"
            if mismatched
            else "every declared column matches its dtype"
        ),
        offending_sample=tuple(sorted(mismatched)),
    )


@register_check("date_parsed")
def _date_parsed(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-STR-5: date columns parsed to a date type, with no fallback to string.

    Counts columns, not rows. A date column left as a string sorts lexically, so
    `10/01/2024` precedes `02/01/2025` and every period comparison downstream is wrong
    without ever raising.
    """
    frame = _table(tables, rule)
    columns: Sequence[str] = rule.params.get("columns", [])
    if not columns:
        return CheckOutcome(skipped=True, skip_reason="no date columns declared")

    unparsed = sorted(
        name
        for name in columns
        if name in frame.columns and frame.schema[name] not in (pl.Date, pl.Datetime)
    )
    return CheckOutcome(
        violating_rows=len(unparsed),
        measured={
            "unparsed_columns": {name: str(frame.schema[name]) for name in unparsed}
        },
        threshold={"columns": list(columns)},
        detail=f"{len(unparsed)} declared date column(s) did not parse to a date type",
        offending_sample=tuple(unparsed),
    )


#: Codepoints that mean a byte sequence was decoded with the wrong codec. U+FFFD is the
#: replacement character a lossy decode leaves behind; the C1 block is what Windows-1252
#: text decoded as Latin-1 produces, and it is how `Ã©` arrives where `é` was meant.
_MOJIBAKE = ("\ufffd", *(chr(c) for c in range(0x80, 0xA0)))


@register_check("encoding")
def _encoding(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-STR-6: no mojibake in string columns.

    Warn rather than fail by default: a mis-decoded name is a data-quality problem, not a
    reason to block modelling on a portfolio. But it is worth surfacing, because a broker
    feed that starts arriving in the wrong codec produces new "levels" that look like
    genuine categories and quietly split a factor.
    """
    frame = _table(tables, rule)
    columns = [
        name
        for name in (rule.params.get("columns") or frame.columns)
        if name in frame.columns and frame.schema[name] == pl.String
    ]
    if not columns:
        return CheckOutcome(skipped=True, skip_reason="no string columns to check")

    pattern = "|".join(_MOJIBAKE)
    predicate = pl.lit(False)
    for name in columns:
        predicate = predicate | pl.col(name).fill_null("").str.contains(pattern)
    offending = frame.filter(predicate)

    return CheckOutcome(
        violating_rows=offending.height,
        measured={"violating_rows": offending.height, "columns_checked": len(columns)},
        threshold={"replacement_char_or_c1_controls": True},
        detail=f"{offending.height} row(s) contain characters typical of a mis-decoded feed",
        offending_sample=_sample(offending, rule.params.get("key_columns", [])),
    )


@register_check("no_unexpected_columns")
def _no_unexpected_columns(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-STR-8: no columns present that the schema does not declare.

    Warn, not fail. An extra column breaks nothing on its own — but it is the clearest
    signal that the upstream extract changed, and the change that added it usually
    changed something else too.
    """
    frame = _table(tables, rule)
    declared = set(rule.params.get("columns", []))
    if not declared:
        return CheckOutcome(skipped=True, skip_reason="no schema declared to compare against")

    unexpected = sorted(set(frame.columns) - declared)
    return CheckOutcome(
        violating_rows=len(unexpected),
        measured={"unexpected_columns": unexpected},
        threshold={"declared_columns": sorted(declared)},
        detail=f"{len(unexpected)} column(s) are present but not declared",
        offending_sample=tuple(unexpected),
    )


@register_check("reject_rate")
def _reject_rate(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-STR-9 / FR-DATA-7: quarantined rows within the permitted share of rows read.

    The default is 0.1 %, and it is deliberately tight. A reject rate that drifts upward
    is the single most reliable sign that a feed has changed shape, and a threshold loose
    enough never to fire is one nobody would notice going wrong.

    Reads the version's `_rejected` table, which is where FR-DATA-7 puts the quarantine —
    a table on the version, not a log line.
    """
    frame = _table(tables, rule)
    rejected = tables.get(rule.params.get("rejected_table", "_rejected"))
    rejected_rows = rejected.height if rejected is not None else 0
    rows_read = frame.height + rejected_rows
    if not rows_read:
        return CheckOutcome(skipped=True, skip_reason="no rows were read")

    rate = rejected_rows / rows_read
    limit = float(rule.params.get("max_reject_rate", 0.001))
    return CheckOutcome(
        violating_rows=rejected_rows if rate > limit else 0,
        measured={
            "rejected_rows": rejected_rows,
            "rows_read": rows_read,
            "reject_rate": round(rate, 6),
        },
        threshold={"max_reject_rate": limit},
        detail=f"{rejected_rows} of {rows_read} rows were quarantined ({rate:.3%})",
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


def _reference_rows(
    ctx: ValidationContext, rule: ValidationRule
) -> list[dict[str, Any]] | None:
    """The pinned Reference Table Version's rows, as mappings `reference.py` understands."""
    name = rule.params.get("reference_table")
    if name is None or name not in ctx.reference_tables:
        return None
    frame = ctx.reference_tables[name]
    return frame.to_dicts()


@register_check("reference_lookup")
def _reference_lookup(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-REF-1: every value resolves in the pinned reference version, as at a date.

    Effective-dated, which is the whole difficulty. A postcode that resolves today may not
    have existed at the policy's inception, and a lookup that ignores the date silently
    rates a 2019 risk on a 2025 territory map.

    Unresolved keys are collected rather than raised on the first one: an actuary needs the
    list, and a feed that broke usually broke for four thousand postcodes rather than one.
    """
    from pricing_core.data.reference import resolve_all

    frame = _table(tables, rule)
    column = rule.target["column"]
    rows = _reference_rows(ctx, rule)
    if rows is None:
        return CheckOutcome(
            skipped=True,
            skip_reason=(
                f"reference table {rule.params.get('reference_table')!r} is not pinned to "
                "this rule set"
            ),
        )

    as_at_column = rule.params.get("as_at_column")
    if as_at_column and as_at_column in frame.columns:
        # One resolve per distinct (key, date): a book of ten million rows holds a few
        # thousand distinct postcode-inception pairs, and resolving per row would turn a
        # lookup into a scan.
        pairs = (
            frame.select(pl.col(column).alias("_k"), pl.col(as_at_column).alias("_d"))
            .drop_nulls()
            .unique()
        )
        missing: list[str] = []
        for group_key, group in pairs.group_by("_d"):
            # Polars hands back a one-element tuple for a single group-by column.
            date_value = group_key[0] if isinstance(group_key, tuple) else group_key
            _, unresolved = resolve_all(
                [str(k) for k in group.get_column("_k").to_list()],
                rows,
                as_at=date_value,
            )
            missing.extend(f"{key}@{date_value}" for key in unresolved)
    else:
        literal = rule.params.get("as_at")
        if literal is None:
            return CheckOutcome(
                skipped=True,
                skip_reason="no as-at date column or literal declared (FR-DATA-31)",
            )
        keys = [
            str(k) for k in frame.get_column(column).drop_nulls().unique().to_list()
        ]
        _, unresolved = resolve_all(keys, rows, as_at=_as_date(literal))
        missing = list(unresolved)

    return CheckOutcome(
        violating_rows=len(missing),
        measured={"unresolved_keys": len(missing)},
        threshold={"reference_table": rule.params.get("reference_table")},
        detail=f"{len(missing)} value(s) of {column!r} do not resolve in the reference table",
        offending_sample=tuple(sorted(missing)[:MAX_OFFENDING_SAMPLE]),
    )


@register_check("reference_coverage")
def _reference_coverage(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-REF-2: enough of the reference table's keys are exercised by the data.

    The inverse of `reference_lookup`, and it catches the failure that one cannot: every
    value resolving while only 4 % of a vehicle-group table is used means the *wrong*
    reference version is pinned — one whose keys happen to be a superset.
    """
    frame = _table(tables, rule)
    column = rule.target["column"]
    rows = _reference_rows(ctx, rule)
    if rows is None:
        return CheckOutcome(skipped=True, skip_reason="reference table is not pinned")

    reference_keys = {str(row["key"]) for row in rows}
    if not reference_keys:
        return CheckOutcome(skipped=True, skip_reason="the reference version has no rows")

    used = {str(v) for v in frame.get_column(column).drop_nulls().unique().to_list()}
    covered = len(used & reference_keys) / len(reference_keys)
    minimum = float(rule.params.get("min_coverage", 0.5))

    return CheckOutcome(
        violating_rows=0 if covered >= minimum else 1,
        measured={
            "coverage": round(covered, 4),
            "reference_keys": len(reference_keys),
            "keys_used": len(used & reference_keys),
        },
        threshold={"min_coverage": minimum},
        detail=f"the data exercises {covered:.1%} of the reference table's keys",
    )


@register_check("effective_date_in_range")
def _effective_date_in_range(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-REF-3: the as-at dates lie inside the reference version's covered period.

    A date before the earliest `effective_from` resolves to nothing; one after the latest
    `effective_to` resolves to the last row for ever, which is worse — it looks like an
    answer. Both are the same mistake: pinning a reference version that does not cover the
    period being rated.
    """
    frame = _table(tables, rule)
    rows = _reference_rows(ctx, rule)
    if rows is None:
        return CheckOutcome(skipped=True, skip_reason="reference table is not pinned")

    as_at_column = rule.params["as_at_column"]
    if as_at_column not in frame.columns:
        return CheckOutcome(
            skipped=True, skip_reason=f"{as_at_column!r} is not present in the data"
        )

    starts = [row["effective_from"] for row in rows if row.get("effective_from")]
    ends = [row["effective_to"] for row in rows if row.get("effective_to")]
    if not starts:
        return CheckOutcome(skipped=True, skip_reason="the reference version has no intervals")

    covered_from = min(starts)
    # An open-ended row covers everything after it, so the version has no upper bound.
    covered_to = None if len(ends) < len(rows) else max(ends)

    predicate = pl.col(as_at_column) < covered_from
    if covered_to is not None:
        predicate = predicate | (pl.col(as_at_column) >= covered_to)
    offending = frame.filter(pl.col(as_at_column).is_not_null() & predicate)

    return CheckOutcome(
        violating_rows=offending.height,
        measured={
            "violating_rows": offending.height,
            "covered_from": str(covered_from),
            "covered_to": str(covered_to) if covered_to else None,
        },
        threshold={"reference_table": rule.params.get("reference_table")},
        detail=(
            f"{offending.height} row(s) have an as-at date outside the reference version's "
            "covered period"
        ),
        offending_sample=_sample(offending, rule.params.get("key_columns", [])),
    )


@register_check("code_list_drift")
def _code_list_drift(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-REF-5: codes present now that the reference dataset version did not contain.

    Distinct from `new_level` (VR-DST-2) despite looking similar: this compares against the
    *code list* an upstream system publishes, so a new code means the upstream taxonomy
    changed. VR-DST-2 compares against the previous dataset and means the *book* changed.
    The remedies differ — one is a mapping update, the other is a conversation about mix.
    """
    frame = _table(tables, rule)
    column = rule.target["column"]
    name = rule.target["table"]

    known: set[str] | None = None
    rows = _reference_rows(ctx, rule)
    if rows is not None:
        known = {str(row["key"]) for row in rows}
    else:
        reference = ctx.reference_frames.get(name)
        if reference is not None and column in reference.columns:
            known = {
                str(v) for v in reference.get_column(column).drop_nulls().unique().to_list()
            }
    if known is None:
        return CheckOutcome(
            skipped=True, skip_reason="no reference version or code list to compare against"
        )

    present = {str(v) for v in frame.get_column(column).drop_nulls().unique().to_list()}
    new_codes = sorted(present - known)
    return CheckOutcome(
        violating_rows=len(new_codes),
        measured={"new_codes": len(new_codes)},
        threshold={"known_codes": len(known)},
        detail=f"{len(new_codes)} code(s) in {column!r} were not present in the reference",
        offending_sample=tuple(new_codes[:MAX_OFFENDING_SAMPLE]),
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


def _linked(
    tables: Mapping[str, pl.DataFrame], rule: ValidationRule
) -> tuple[pl.DataFrame, pl.DataFrame, str] | None:
    """The claims table, the exposure table, and the key that links them."""
    claims_name = rule.params.get("claims_table", "claim")
    exposure_name = rule.params.get("exposure_table", "policy_exposure")
    key = rule.params.get("link_key", "policy_id")
    if claims_name not in tables or exposure_name not in tables:
        return None
    claims, exposure = tables[claims_name], tables[exposure_name]
    if key not in claims.columns or key not in exposure.columns:
        return None
    return claims, exposure, key


@register_check("claim_date_in_exposure")
def _claim_date_in_exposure(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-5 / FR-DATA-12: the loss date falls inside the linked exposure period.

    Half-open `[start, end)`, matching how exposure is split: a loss on the renewal date
    belongs to the new term, and counting it against both would inflate the frequency of
    the expiring one and deflate the new one by the same claims.

    A claim outside its own exposure period is usually a linkage error rather than a date
    error, and it is the one that silently lowers frequency — the claim is counted, the
    exposure it belongs to is elsewhere.
    """
    linked = _linked(tables, rule)
    if linked is None:
        return CheckOutcome(skipped=True, skip_reason="no linked claim and exposure tables")
    claims, exposure, key = linked

    loss = rule.params.get("loss_date_column", "date_of_loss")
    start = rule.params.get("start_column", "exposure_start")
    end = rule.params.get("end_column", "exposure_end")
    if any(c not in claims.columns for c in (loss,)) or any(
        c not in exposure.columns for c in (start, end)
    ):
        return CheckOutcome(skipped=True, skip_reason="date columns are absent")

    joined = claims.join(exposure.select(key, start, end), on=key, how="left")
    offending = joined.filter(
        pl.col(loss).is_not_null()
        & pl.col(start).is_not_null()
        & (
            (pl.col(loss) < pl.col(start))
            | (pl.col(end).is_not_null() & (pl.col(loss) >= pl.col(end)))
        )
    )
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"violating_rows": offending.height, "claims": claims.height},
        threshold={"interval": f"[{start}, {end})"},
        detail=f"{offending.height} claim(s) fall outside their linked exposure period",
        offending_sample=_sample(offending, rule.params.get("key_columns", [key])),
    )


@register_check("claim_linkage_complete")
def _claim_linkage_complete(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-6: every claim links to an exposure row.

    An unlinked claim is not a missing row in a report — it is a claim whose exposure is
    counted nowhere, so the portfolio frequency it contributes to is computed over a
    denominator that excludes it.
    """
    linked = _linked(tables, rule)
    if linked is None:
        return CheckOutcome(skipped=True, skip_reason="no linked claim and exposure tables")
    claims, exposure, key = linked

    known = exposure.select(key).unique()
    offending = claims.join(known.with_columns(pl.lit(True).alias("_found")), on=key, how="left")
    offending = offending.filter(pl.col("_found").is_null())
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"unlinked_claims": offending.height, "claims": claims.height},
        threshold={"required_linkage": 1.0},
        detail=f"{offending.height} of {claims.height} claim(s) link to no exposure row",
        offending_sample=_sample(offending, rule.params.get("key_columns", [key])),
    )


@register_check("claim_not_multi_linked")
def _claim_not_multi_linked(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-7: no claim links to more than one exposure row.

    The other half of VR-ACT-6, and the more dangerous one. A claim matching two exposure
    rows is counted twice by any join, so the frequency it feeds is overstated — and
    unlike an unlinked claim it produces no missing total anywhere to notice.

    Multi-linkage on `policy_id` alone is normal for a policy with several terms; the
    honest link is the key *and* the period, which is why the loss date is used when it is
    available.
    """
    linked = _linked(tables, rule)
    if linked is None:
        return CheckOutcome(skipped=True, skip_reason="no linked claim and exposure tables")
    claims, exposure, key = linked

    loss = rule.params.get("loss_date_column", "date_of_loss")
    start = rule.params.get("start_column", "exposure_start")
    end = rule.params.get("end_column", "exposure_end")
    use_period = all(
        column in table.columns
        for column, table in ((loss, claims), (start, exposure), (end, exposure))
    )

    joined = claims.join(
        exposure.select([key, *( [start, end] if use_period else [])]), on=key, how="left"
    )
    if use_period:
        joined = joined.filter(
            pl.col(start).is_null()
            | (
                (pl.col(loss) >= pl.col(start))
                & (pl.col(end).is_null() | (pl.col(loss) < pl.col(end)))
            )
        )

    claim_key = rule.params.get("claim_key", "claim_id")
    group_on = claim_key if claim_key in joined.columns else key
    counts = joined.group_by(group_on).len()
    offending = counts.filter(pl.col("len") > 1)
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"multi_linked_claims": offending.height},
        threshold={"max_links_per_claim": 1},
        detail=f"{offending.height} claim(s) link to more than one exposure row",
        offending_sample=_sample(offending, [group_on]),
    )


@register_check("claim_amount_sign")
def _claim_amount_sign(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-9: negative incurred amounts, counted rather than removed.

    Warn, never fail, and never auto-corrected. Negative incurred is *legitimate* where
    recoveries and reversals are expected — a subrogation recovery on a settled claim is a
    negative movement, and a platform that deleted those would understate recoveries and
    overstate severity. What it must not do is let them pass unremarked, because the same
    number is also what a sign error looks like.
    """
    frame = _table(tables, rule)
    column = rule.target.get("column", "claim_amount_minor")
    if column not in frame.columns:
        return CheckOutcome(skipped=True, skip_reason=f"{column!r} is not present")

    negative = frame.filter(pl.col(column) < 0)
    total = frame.filter(pl.col(column).is_not_null()).height
    share = negative.height / total if total else 0.0
    limit = float(rule.params.get("max_negative_share", 0.01))
    return CheckOutcome(
        violating_rows=negative.height if share > limit else 0,
        measured={
            "negative_rows": negative.height,
            "share": round(share, 6),
            "total_negative_minor": int(
                negative.get_column(column).sum() or 0
            ),
        },
        threshold={"max_negative_share": limit},
        detail=(
            f"{negative.height} row(s) carry a negative {column} ({share:.2%}) — expected "
            "where recoveries and reversals occur, flagged so a sign error is not mistaken "
            "for one"
        ),
        offending_sample=_sample(negative, rule.params.get("key_columns", [])),
    )


@register_check("severity_outlier")
def _severity_outlier(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-10: large losses flagged for large-loss treatment — **never auto-removed**.

    The spec is emphatic and so is this: capping is a modelling decision (OQ-DATA-1,
    decided) made where its effect on the fitted result is visible, not a data-cleaning
    step applied silently at ingestion. A platform that dropped the top tail here would
    change every severity model fitted afterwards, and nothing in the model's lineage
    would say so.

    The threshold is absolute or a percentile of the column's own distribution — the
    latter because "large" for household escape-of-water and for motor bodily injury are
    three orders of magnitude apart.
    """
    frame = _table(tables, rule)
    column = rule.target.get("column", "claim_amount_minor")
    if column not in frame.columns:
        return CheckOutcome(skipped=True, skip_reason=f"{column!r} is not present")

    values = frame.filter(pl.col(column) > 0)
    if values.height == 0:
        return CheckOutcome(skipped=True, skip_reason="no positive amounts to assess")

    declared = rule.params.get("threshold_minor")
    if declared is None:
        quantile = float(rule.params.get("percentile", 0.995))
        computed = values.get_column(column).cast(pl.Float64).quantile(
            quantile, interpolation="linear"
        )
        if computed is None:
            return CheckOutcome(
                skipped=True, skip_reason="no threshold could be established"
            )
        absolute = float(computed)
        basis: dict[str, Any] = {"percentile": quantile}
    else:
        absolute = float(declared)
        basis = {"threshold_minor": absolute}

    large = values.filter(pl.col(column) >= absolute)
    return CheckOutcome(
        violating_rows=large.height,
        measured={
            "large_losses": large.height,
            "threshold_minor": absolute,
            # Polars types `max()` as any value a frame can hold; the cast above
            # guarantees Float64, so narrowing here is a typing statement rather than a
            # conversion — the same note as `profile.py`'s quantile block.
            "largest_minor": float(
                values.get_column(column).cast(pl.Float64).max() or 0  # type: ignore[arg-type]
            ),
        },
        threshold=basis,
        detail=(
            f"{large.height} claim(s) at or above {absolute:,.0f} minor units — "
            "flagged for large-loss treatment, not removed"
        ),
        offending_sample=_sample(large, rule.params.get("key_columns", [])),
    )


def _portfolio_rates(
    frame: pl.DataFrame, ctx: ValidationContext, rule: ValidationRule
) -> dict[str, float] | None:
    """Frequency, mean severity and burning cost over the whole table."""
    exposure_column = rule.params.get("exposure_column", ctx.exposure_column)
    count_column = rule.params.get("claim_count_column", "claim_count")
    amount_column = rule.params.get("claim_amount_column", "claim_amount_minor")
    if exposure_column not in frame.columns or count_column not in frame.columns:
        return None

    exposure = float(frame.get_column(exposure_column).cast(pl.Float64).sum() or 0.0)
    claims = float(frame.get_column(count_column).cast(pl.Float64).sum() or 0.0)
    if exposure <= 0:
        return None
    amount = (
        float(frame.get_column(amount_column).cast(pl.Float64).sum() or 0.0)
        if amount_column in frame.columns
        else 0.0
    )
    return {
        "exposure": exposure,
        "claims": claims,
        "frequency": claims / exposure,
        "severity": amount / claims if claims else 0.0,
        "burning_cost": amount / exposure,
    }


@register_check("frequency_plausible")
def _frequency_plausible(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-11: portfolio frequency inside a configured band.

    The band is configuration, not code, because plausible frequency is a property of the
    peril and the market: motor accidental damage sits around 0.02 to 0.25, household escape
    of water elsewhere entirely, and a single hard-coded range would be wrong for every
    portfolio but one.

    What this catches is the class of error no column-level rule can: exposure in months
    where the model expects years shifts frequency by a factor of twelve, and every
    individual value looks entirely reasonable.
    """
    frame = _table(tables, rule)
    rates = _portfolio_rates(frame, ctx, rule)
    if rates is None:
        return CheckOutcome(skipped=True, skip_reason="no exposure and claim-count columns")

    low = float(rule.params.get("min_frequency", 0.0))
    high = float(rule.params.get("max_frequency", 1.0))
    frequency = rates["frequency"]
    return CheckOutcome(
        violating_rows=0 if low <= frequency <= high else 1,
        measured={
            "frequency": round(frequency, 6),
            "claims": rates["claims"],
            "exposure": round(rates["exposure"], 4),
        },
        threshold={"min_frequency": low, "max_frequency": high},
        detail=f"portfolio frequency is {frequency:.4f} per unit exposure",
    )


@register_check("severity_plausible")
def _severity_plausible(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-12: portfolio mean severity inside a configured band.

    Catches the counterpart of VR-ACT-11's units error: amounts loaded in pounds where the
    platform stores minor units are out by a hundred, and every row still looks like money.
    """
    frame = _table(tables, rule)
    rates = _portfolio_rates(frame, ctx, rule)
    if rates is None or not rates["claims"]:
        return CheckOutcome(skipped=True, skip_reason="no claims to compute a severity from")

    low = float(rule.params.get("min_severity_minor", 0.0))
    high = float(rule.params.get("max_severity_minor", 1e12))
    severity = rates["severity"]
    return CheckOutcome(
        violating_rows=0 if low <= severity <= high else 1,
        measured={"mean_severity_minor": round(severity, 2), "claims": rates["claims"]},
        threshold={"min_severity_minor": low, "max_severity_minor": high},
        detail=f"mean severity is {severity:,.0f} minor units",
    )


@register_check("zero_claim_cohort")
def _zero_claim_cohort(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-13: a material factor level with claims before and none now.

    Material means it carries real exposure — a level with 0.01 % of the book having no
    claims is arithmetic, not a signal. A level with 3 % of the exposure and claims last
    version and none this one is almost always a join that stopped matching, and it is
    invisible at portfolio level because the totals barely move.
    """
    frame = _table(tables, rule)
    column = rule.target["column"]
    exposure_column = rule.params.get("exposure_column", ctx.exposure_column)
    count_column = rule.params.get("claim_count_column", "claim_count")
    if any(c not in frame.columns for c in (column, exposure_column, count_column)):
        return CheckOutcome(skipped=True, skip_reason="factor, exposure or claim column absent")

    reference_levels: set[str] = set()
    if ctx.reference_profile is not None:
        for summary in ctx.reference_profile.one_ways:
            if summary.column == column:
                reference_levels = {
                    row.level for row in summary.rows if row.claim_count > 0
                }
    if not reference_levels:
        reference = ctx.reference_frames.get(rule.target["table"])
        if reference is None or column not in reference.columns:
            return CheckOutcome(
                skipped=True, skip_reason="no reference version to compare claims against"
            )
        grouped = reference.group_by(column).agg(
            pl.col(count_column).cast(pl.Float64).sum().alias("_claims")
        )
        reference_levels = {
            str(level) for level, claims in grouped.iter_rows() if (claims or 0) > 0
        }

    current = frame.group_by(column).agg(
        pl.col(exposure_column).cast(pl.Float64).sum().alias("_exposure"),
        pl.col(count_column).cast(pl.Float64).sum().alias("_claims"),
    )
    total_exposure = float(frame.get_column(exposure_column).cast(pl.Float64).sum() or 0.0)
    if total_exposure <= 0:
        return CheckOutcome(skipped=True, skip_reason="the table carries no exposure")

    minimum_share = float(rule.params.get("min_exposure_share", 0.01))
    offending = sorted(
        str(level)
        for level, exposure, claims in current.iter_rows()
        if str(level) in reference_levels
        and (claims or 0) == 0
        and (exposure or 0.0) / total_exposure > minimum_share
    )
    return CheckOutcome(
        violating_rows=len(offending),
        measured={"levels_lost_claims": len(offending)},
        threshold={"min_exposure_share": minimum_share},
        detail=(
            f"{len(offending)} level(s) of {column!r} carry material exposure and no claims, "
            "having had claims in the reference version"
        ),
        offending_sample=tuple(offending[:MAX_OFFENDING_SAMPLE]),
    )


@register_check("development_maturity")
def _development_maturity(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-14: the most recent months are immature, and fitting on them is a choice.

    **This is the platform's only treatment of development** (§1.2, OQ-DATA-4 decided
    2026-08-14: the user supplies developed data). The warning exists so that modelling on
    a period that has not run off is a visible decision rather than an accident — the
    accident being a frequency model fitted through the last three months, which reads
    them as a genuine improvement in claims experience rather than as IBNR.

    It never adjusts. Adjustment is out of scope, and a platform that quietly developed
    the tail would be making a reserving assumption inside a pricing dataset.
    """
    frame = _table(tables, rule)
    column = rule.params.get("period_column", "exposure_start")
    if column not in frame.columns:
        return CheckOutcome(skipped=True, skip_reason=f"{column!r} is not present")

    if frame.schema[column] not in (pl.Date, pl.Datetime):
        # Not a narrowing convenience: a period column still held as a string sorts
        # lexically, so "the most recent three months" would select whatever sorts last.
        # VR-STR-5 is the rule that catches the parse; this one declines to guess.
        return CheckOutcome(
            skipped=True,
            skip_reason=(
                f"{column!r} is {frame.schema[column]}, not a date — see VR-STR-5"
            ),
        )
    latest = frame.get_column(column).max()
    if not isinstance(latest, date | datetime):
        return CheckOutcome(skipped=True, skip_reason="no dated rows")

    months = int(rule.params.get("immature_months", 3))
    exposure_column = rule.params.get("exposure_column", ctx.exposure_column)
    # Measured from the data's own latest period unless the caller pins one. A check that
    # read the wall clock would give a different answer on a re-run of the same version,
    # and NFR-DATA-5 requires byte-identical reports.
    as_of = _as_date(rule.params["as_of"]) if "as_of" in rule.params else latest
    # Approximate a month as 30 days: the boundary is a judgement anyway ("the last three
    # months are immature"), and a calendar-exact cut would imply a precision the
    # underlying development assumption does not have.
    cutoff = as_of - timedelta(days=30 * months)
    immature = frame.filter(pl.col(column) > cutoff)

    share = 0.0
    if exposure_column in frame.columns:
        total = float(frame.get_column(exposure_column).cast(pl.Float64).sum() or 0.0)
        if total > 0:
            share = float(
                immature.get_column(exposure_column).cast(pl.Float64).sum() or 0.0
            ) / total

    # Materiality, not mere presence. Measured against the data's own latest period, the
    # most recent rows are *always* immature — so a rule that fired on any of them would
    # fire on every dataset ever validated, and a warning that always fires is one people
    # learn to rubber-stamp. It warns when the immature tail is big enough to move a fit.
    limit = float(rule.params.get("max_immature_exposure_share", 0.05))
    return CheckOutcome(
        violating_rows=immature.height if share > limit else 0,
        measured={
            "immature_rows": immature.height,
            "immature_exposure_share": round(share, 6),
            "latest_period": str(latest),
            "cutoff": str(cutoff),
        },
        threshold={
            "immature_months": months,
            "max_immature_exposure_share": limit,
        },
        detail=(
            f"{immature.height} row(s) fall in the most recent {months} month(s) and have "
            f"not run off, carrying {share:.1%} of the exposure; modelling on them without "
            "a development adjustment is a choice"
        ),
    )


@register_check("currency_consistency")
def _currency_consistency(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-15: every monetary row carries the Dataset's declared currency.

    Fail, not warn. Mixed currency in one monetary column is not a quality issue to note —
    it makes every sum in the dataset meaningless, and the sums are what the model is
    fitted on. A GB book with a handful of EUR rows produces a severity that is
    approximately right and definitely wrong.
    """
    frame = _table(tables, rule)
    column = rule.params.get("currency_column", "currency")
    declared = rule.params.get("currency")
    if column not in frame.columns:
        return CheckOutcome(
            skipped=True,
            skip_reason=f"{column!r} is not present; the dataset declares a single currency",
        )

    present = sorted(
        str(v) for v in frame.get_column(column).drop_nulls().unique().to_list()
    )
    if declared is None:
        offending_rows = 0 if len(present) <= 1 else frame.height
        detail = (
            f"the table carries {len(present)} currencies: {', '.join(present)}"
            if len(present) > 1
            else f"a single currency throughout ({present[0] if present else 'none'})"
        )
    else:
        offending = frame.filter(
            pl.col(column).is_not_null() & (pl.col(column) != declared)
        )
        offending_rows = offending.height
        detail = f"{offending.height} row(s) are not in the declared currency {declared!r}"

    return CheckOutcome(
        violating_rows=offending_rows,
        measured={"currencies_present": present},
        threshold={"declared_currency": declared},
        detail=detail,
        offending_sample=tuple(present[:MAX_OFFENDING_SAMPLE]),
    )


@register_check("duplicate_claim")
def _duplicate_claim(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-ACT-16: no two claims share (policy, loss date, peril, amount).

    The double-load signature. Two identical claims can be genuine — a policy can have two
    losses of the same amount on the same day under the same peril — which is why this
    warns rather than fails. But it is rare enough that a spike in it means a file was
    ingested twice, and that inflates frequency by exactly the proportion re-loaded while
    leaving every individual row valid.
    """
    frame = _table(tables, rule)
    columns = [
        column
        for column in rule.params.get(
            "columns", ["policy_id", "date_of_loss", "peril", "claim_amount_minor"]
        )
        if column in frame.columns
    ]
    if len(columns) < 2:
        return CheckOutcome(
            skipped=True, skip_reason="too few of the duplicate-signature columns are present"
        )

    counts = frame.group_by(columns).len()
    duplicated = counts.filter(pl.col("len") > 1)
    extra_rows = int((duplicated.get_column("len").sum() or 0) - duplicated.height)
    return CheckOutcome(
        violating_rows=extra_rows,
        measured={
            "duplicate_groups": duplicated.height,
            "excess_rows": extra_rows,
            "signature": columns,
        },
        threshold={"max_duplicates": 0},
        detail=(
            f"{duplicated.height} claim signature(s) appear more than once, {extra_rows} "
            "row(s) beyond the first of each"
        ),
        offending_sample=_sample(duplicated, columns),
    )

# -- Layer 4: distributional -----------------------------------------------------------------


@register_check("null_rate_shift")
def _null_rate_shift(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-DST-4: the null rate moved — a broken feed's clearest signal."""
    frame = _table(tables, rule)
    name = rule.target["table"]
    column = rule.target["column"]
    current = frame.get_column(column).null_count() / max(frame.height, 1)

    profiled = ctx.reference_profile.column(column) if ctx.reference_profile else None
    if profiled is not None:
        before = profiled.null_rate
    else:
        reference = ctx.reference_frames.get(name)
        if reference is None or column not in reference.columns:
            return CheckOutcome(
                skipped=True, skip_reason="no reference version to compare against"
            )
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
    if ctx.reference_profile is not None and ctx.reference_profile.row_count:
        reference_rows = ctx.reference_profile.row_count
    else:
        reference = ctx.reference_frames.get(name)
        if reference is None or reference.height == 0:
            return CheckOutcome(
                skipped=True, skip_reason="no reference version to compare against"
            )
        reference_rows = reference.height

    ratio = frame.height / reference_rows
    limit = float(rule.params.get("max_shift_fraction", 0.2))
    return CheckOutcome(
        violating_rows=1 if abs(ratio - 1.0) > limit else 0,
        measured={"rows": frame.height, "reference_rows": reference_rows,
                  "ratio": round(ratio, 4)},
        threshold={"max_shift_fraction": limit},
        detail=f"row count is {ratio:.2f} times the reference version",
    )


def _reference_column(ctx: ValidationContext, rule: ValidationRule, column: str) -> Any:
    """The reference version's `ColumnProfile`, or `None`.

    FR-DATA-24 prefers the stored Profile: a null rate, a mean and a level distribution are
    all in it already, and re-scanning ten million reference rows to recompute one is the
    scan the requirement exists to avoid.
    """
    if ctx.reference_profile is None:
        return None
    return ctx.reference_profile.column(column)


def _level_counts(frame: pl.DataFrame, column: str, *, top: int = TOP_LEVELS) -> dict[str, float]:
    """The current frame's top level counts, shaped like a Profile's `top_levels`.

    Capped at the same `TOP_LEVELS` the Profile keeps, or the two sides of a PSI would be
    computed over different level sets and the number would mean nothing. `nulls_last=True`
    matches both profiling engines' `NULLS LAST` tie-break, so a level tied on count with a
    null lands in the same top-20 cut here as it would in a `ColumnProfile`.
    """
    counts = (
        frame.group_by(column)
        .len()
        .sort(["len", column], descending=[True, False], nulls_last=True)
        .head(top)
    )
    # A null level is excluded from the weight map — the same treatment `_psi` in
    # `profile.py` gives `top_levels` (Ruling 2b). Keeping it here under the coerced key
    # "None" while the reference side has already dropped the null would make the two
    # sides of a PSI disagree about their totals and shares for no reason but that
    # coercion, inventing drift on every column that has a null.
    return {
        str(level): float(count) for level, count in counts.iter_rows() if level is not None
    }


@register_check("psi_column")
def _psi_column(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-DST-1: per-column PSI against the reference version.

    Warn at 0.10 and fail at 0.25 by default — the conventional bands, and configuration
    rather than code. The severity is the rule's, so the two thresholds are expressed as
    the `fail_above` boundary here and the rule's own severity governs the rest.

    Computed with the same `psi_from_weights` the comparison screen uses, so a `VR-DST-1`
    verdict and the screen an actuary is reading cannot disagree about one pair of
    versions.
    """
    from pricing_core.data.profile import psi_from_weights

    frame = _table(tables, rule)
    column = rule.target["column"]
    if column not in frame.columns:
        return CheckOutcome(skipped=True, skip_reason=f"{column!r} is not present")

    profiled = _reference_column(ctx, rule, column)
    if profiled is not None and profiled.top_levels:
        # Ruling 2a: PSI stays on count, deliberately — VR-DST-1 must not silently start
        # weighting by exposure, or every drift figure already published would change
        # meaning underneath the people who read it. (VR-DST-8, `mix_shift_exposure`, is
        # the exposure-weighted PSI.) Nulls excluded to match `_level_counts` below and
        # `_psi` in `profile.py` (Ruling 2b) — otherwise this side would carry a null
        # under the reference's dropped key and invent drift on every column with one.
        reference_weights = {
            lc.level: float(lc.count) for lc in profiled.top_levels if lc.level is not None
        }
    else:
        reference = ctx.reference_frames.get(rule.target["table"])
        if reference is None or column not in reference.columns:
            return CheckOutcome(
                skipped=True, skip_reason="no reference version to compare against"
            )
        reference_weights = _level_counts(reference, column)

    psi = psi_from_weights(_level_counts(frame, column), reference_weights)
    if psi is None:
        return CheckOutcome(skipped=True, skip_reason="not enough levels to compute a PSI")

    warn_above = float(rule.params.get("warn_above", 0.10))
    fail_above = float(rule.params.get("fail_above", 0.25))
    return CheckOutcome(
        violating_rows=1 if psi > warn_above else 0,
        measured={"psi": round(psi, 6), "column": column},
        threshold={"warn_above": warn_above, "fail_above": fail_above},
        detail=f"PSI for {column!r} is {psi:.4f} against the reference version",
    )


@register_check("new_level")
def _new_level(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-DST-2: categorical levels present now and absent in the reference version.

    Means the *book* changed — a new broker, a new vehicle group, a territory that did not
    write before. Distinct from `code_list_drift` (VR-REF-5), which compares against a
    published code list and means the *taxonomy* changed. The remedies differ: this one is
    a conversation about mix, that one is a mapping update.
    """
    frame = _table(tables, rule)
    column = rule.target["column"]
    if column not in frame.columns:
        return CheckOutcome(skipped=True, skip_reason=f"{column!r} is not present")

    profiled = _reference_column(ctx, rule, column)
    if profiled is not None and profiled.top_levels:
        # A null level is a real category, not a level that could be "new" or "gone" in
        # the sense this rule reports (the same exclusion `compare_profiles` gives
        # `new_levels`/`vanished_levels` in `profile.py`) — excluded so it can never be
        # reported as a phantom new level.
        known = {lc.level for lc in profiled.top_levels if lc.level is not None}
    else:
        reference = ctx.reference_frames.get(rule.target["table"])
        if reference is None or column not in reference.columns:
            return CheckOutcome(
                skipped=True, skip_reason="no reference version to compare against"
            )
        known = set(_level_counts(reference, column))

    present = _level_counts(frame, column)
    new_levels = sorted(set(present) - known)
    return CheckOutcome(
        violating_rows=len(new_levels),
        measured={"new_levels": len(new_levels)},
        threshold={"reference_levels": len(known)},
        detail=f"{len(new_levels)} level(s) of {column!r} are new since the reference version",
        offending_sample=tuple(new_levels[:MAX_OFFENDING_SAMPLE]),
    )


@register_check("vanished_level")
def _vanished_level(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-DST-3: levels that carried material reference exposure and are now absent.

    Material, because a rare level disappearing is noise. A level that held 3 % of the book
    and is now missing entirely is a join that stopped matching or a feed that stopped
    sending — and the portfolio totals move so little that nothing else notices.
    """
    frame = _table(tables, rule)
    column = rule.target["column"]
    if column not in frame.columns:
        return CheckOutcome(skipped=True, skip_reason=f"{column!r} is not present")

    reference_weights: dict[str, float] = {}
    if ctx.reference_profile is not None:
        for summary in ctx.reference_profile.one_ways:
            if summary.column == column:
                # `OneWayRow.level` still coerces a null level to the string "None"
                # (unlike `LevelCount.level`, which FR-DATA-49 left nullable — see the
                # fallback below). Excluded here for the same reason the `top_levels`
                # fallback excludes a real null: `_level_counts` on the present side has
                # already dropped nulls, so keeping a "None" key here would make a
                # byte-identical current frame report its own null share as vanished.
                reference_weights = {
                    row.level: float(row.exposure_years)
                    for row in summary.rows
                    if row.level != "None"
                }
    if not reference_weights:
        profiled = _reference_column(ctx, rule, column)
        if profiled is not None and profiled.top_levels:
            # FR-DATA-49: per-level exposure now exists on `top_levels`, so this fallback
            # no longer has to stand a count in for it. A null level is excluded — the
            # same treatment `new_level` and `compare_profiles` give it — so it can never
            # be reported as a vanished level.
            reference_weights = {
                lc.level: (
                    # The version's profile carries real exposure for this level: use it.
                    float(lc.exposure_years)
                    if lc.exposure_years is not None
                    # No exposure column on that version — count is all `top_levels` has,
                    # same as before FR-DATA-49.
                    else float(lc.count)
                )
                for lc in profiled.top_levels
                if lc.level is not None
            }
    if not reference_weights:
        reference = ctx.reference_frames.get(rule.target["table"])
        if reference is None or column not in reference.columns:
            return CheckOutcome(
                skipped=True, skip_reason="no reference version to compare against"
            )
        reference_weights = _level_counts(reference, column)

    total = sum(reference_weights.values())
    if total <= 0:
        return CheckOutcome(skipped=True, skip_reason="the reference version has no weight")

    present = set(_level_counts(frame, column))
    minimum_share = float(rule.params.get("min_exposure_share", 0.01))
    vanished = sorted(
        level
        for level, weight in reference_weights.items()
        if level not in present and weight / total > minimum_share
    )
    return CheckOutcome(
        violating_rows=len(vanished),
        measured={"vanished_levels": len(vanished)},
        threshold={"min_exposure_share": minimum_share},
        detail=(
            f"{len(vanished)} level(s) of {column!r} carried material reference weight and "
            "are now absent"
        ),
        offending_sample=tuple(vanished[:MAX_OFFENDING_SAMPLE]),
    )


@register_check("mean_shift")
def _mean_shift(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-DST-6: a numeric mean moved by more than N reference standard errors.

    Standard errors rather than a percentage, because the same 2 % move means very
    different things on a column with ten million observations and one with four hundred.
    Expressing the threshold in units of sampling noise makes one setting right for both.
    """
    frame = _table(tables, rule)
    column = rule.target["column"]
    if column not in frame.columns:
        return CheckOutcome(skipped=True, skip_reason=f"{column!r} is not present")

    profiled = _reference_column(ctx, rule, column)
    if profiled is None or profiled.mean is None or profiled.std is None:
        return CheckOutcome(
            skipped=True, skip_reason="the reference profile has no mean for this column"
        )
    if not profiled.row_count:
        return CheckOutcome(skipped=True, skip_reason="the reference profile has no rows")

    current = frame.get_column(column).cast(pl.Float64, strict=False).drop_nulls()
    if current.len() == 0:
        return CheckOutcome(skipped=True, skip_reason="no non-null values to compare")

    import math

    standard_error = profiled.std / math.sqrt(profiled.row_count)
    if standard_error <= 0:
        return CheckOutcome(
            skipped=True, skip_reason="the reference column has no variation to measure against"
        )

    observed = float(current.mean())  # type: ignore[arg-type]
    moved = abs(observed - profiled.mean) / standard_error
    limit = float(rule.params.get("max_standard_errors", 5.0))
    return CheckOutcome(
        violating_rows=1 if moved > limit else 0,
        measured={
            "mean": round(observed, 6),
            "reference_mean": round(profiled.mean, 6),
            "standard_errors": round(moved, 3),
        },
        threshold={"max_standard_errors": limit},
        detail=f"the mean of {column!r} moved {moved:.1f} reference standard errors",
    )


@register_check("target_rate_shift")
def _target_rate_shift(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-DST-7: observed frequency, severity or burning cost moved against reference.

    The rule an actuary would look at first, and the one most likely to be a real finding
    rather than a data fault: if the burning cost has moved 15 % and nothing structural
    explains it, the book has changed and the rates have not.
    """
    frame = _table(tables, rule)
    rates = _portfolio_rates(frame, ctx, rule)
    if rates is None:
        return CheckOutcome(skipped=True, skip_reason="no exposure and claim-count columns")

    metric = rule.params.get("metric", "frequency")
    if metric not in rates:
        return CheckOutcome(skipped=True, skip_reason=f"unknown metric {metric!r}")

    reference_rates: dict[str, float] | None = None
    reference = ctx.reference_frames.get(rule.target["table"])
    if reference is not None:
        reference_rates = _portfolio_rates(reference, ctx, rule)
    elif ctx.reference_profile is not None:
        # From the Profile's column means: mean(claims)/mean(exposure) equals
        # total(claims)/total(exposure), because both scale by the same row count.
        exposure_column = rule.params.get("exposure_column", ctx.exposure_column)
        count_column = rule.params.get("claim_count_column", "claim_count")
        amount_column = rule.params.get("claim_amount_column", "claim_amount_minor")
        exposure_profile = ctx.reference_profile.column(exposure_column)
        count_profile = ctx.reference_profile.column(count_column)
        amount_profile = ctx.reference_profile.column(amount_column)
        if (
            exposure_profile is not None
            and count_profile is not None
            and exposure_profile.mean
            and count_profile.mean is not None
        ):
            frequency = count_profile.mean / exposure_profile.mean
            severity = (
                amount_profile.mean / count_profile.mean
                if amount_profile is not None
                and amount_profile.mean is not None
                and count_profile.mean
                else 0.0
            )
            reference_rates = {
                "frequency": frequency,
                "severity": severity,
                "burning_cost": frequency * severity,
            }
    if reference_rates is None or not reference_rates.get(metric):
        return CheckOutcome(
            skipped=True, skip_reason="no reference version to compare the rate against"
        )

    before, now = reference_rates[metric], rates[metric]
    moved = abs(now - before) / before
    limit = float(rule.params.get("max_shift_fraction", 0.15))
    return CheckOutcome(
        violating_rows=1 if moved > limit else 0,
        measured={metric: round(now, 6), f"reference_{metric}": round(before, 6),
                  "shift": round(moved, 4)},
        threshold={"max_shift_fraction": limit, "metric": metric},
        detail=f"{metric} moved {moved:.1%} against the reference version",
    )


@register_check("mix_shift_exposure")
def _mix_shift_exposure(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """VR-DST-8: PSI on the **exposure** across a key factor, not on row counts.

    The distinction is the whole rule. A book that writes the same number of young-driver
    policies at half the exposure has shifted its mix, and a PSI over row counts sees
    nothing — while every rate that depends on that mix has moved.
    """
    from pricing_core.data.profile import psi_from_weights

    frame = _table(tables, rule)
    column = rule.target["column"]
    exposure_column = rule.params.get("exposure_column", ctx.exposure_column)
    if column not in frame.columns or exposure_column not in frame.columns:
        return CheckOutcome(skipped=True, skip_reason="factor or exposure column is absent")

    def weights(table: pl.DataFrame) -> dict[str, float]:
        grouped = table.group_by(column).agg(
            pl.col(exposure_column).cast(pl.Float64).sum().alias("_exposure")
        )
        return {str(level): float(value or 0.0) for level, value in grouped.iter_rows()}

    reference_weights: dict[str, float] = {}
    if ctx.reference_profile is not None:
        for summary in ctx.reference_profile.one_ways:
            if summary.column == column:
                reference_weights = {
                    row.level: float(row.exposure_years) for row in summary.rows
                }
    if not reference_weights:
        reference = ctx.reference_frames.get(rule.target["table"])
        if reference is None or column not in reference.columns:
            return CheckOutcome(
                skipped=True,
                skip_reason="no reference one-way or frame to compare exposure mix against",
            )
        reference_weights = weights(reference)

    psi = psi_from_weights(weights(frame), reference_weights)
    if psi is None:
        return CheckOutcome(skipped=True, skip_reason="not enough levels to compute a PSI")

    warn_above = float(rule.params.get("warn_above", 0.10))
    return CheckOutcome(
        violating_rows=1 if psi > warn_above else 0,
        measured={"exposure_psi": round(psi, 6), "factor": column},
        threshold={"warn_above": warn_above},
        detail=f"exposure mix across {column!r} has a PSI of {psi:.4f}",
    )

# -- `01` §4.5's custom-rule vocabulary ------------------------------------------------
#
# FR-DATA-21 lets a user author a rule with `check` drawn from a fixed list, and §4.5 is
# that list. Seven of its eleven names were unregistered — a rule authored exactly as the
# spec documents produced `unknown_check`, which the engine reports as an `error`. The
# `--catalogue VR` audit could not see it: that check covers the built-in *rule ids*, and
# this is the *check vocabulary*. Found by seeding freMTPL2.


def _alias(name: str, target: str) -> None:
    """Register `name` as another way to spell an existing check.

    `01` §4.4 names the built-in rules and §4.5 names the checks a custom rule may use, and
    the two spellings for the same behaviour predate each other. Both resolve here rather
    than one being renamed, because a rule set already citing either must keep working —
    a rule is what a report's verdict *means*.
    """
    CHECKS[name] = CHECKS[target]


@register_check("regex")
def _regex(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """`01` §4.5 `regex`: a string column matches a declared pattern.

    Nulls are not violations — a missing postcode is `not_null`'s business, and a rule that
    reported both would double-count the same row in two layers.
    """
    frame = _table(tables, rule)
    column = rule.target["column"]
    pattern = rule.params.get("pattern")
    if not pattern:
        return CheckOutcome(skipped=True, skip_reason="no pattern declared")

    offending = frame.filter(
        pl.col(column).is_not_null()
        & ~pl.col(column).cast(pl.String).str.contains(pattern)
    )
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"violating_rows": offending.height},
        threshold={"pattern": pattern},
        detail=f"{offending.height} value(s) of {column!r} do not match {pattern!r}",
        offending_sample=_sample(offending, rule.params.get("key_columns", [])),
    )


#: The comparisons `relationship` permits between two columns. A closed set, because the
#: alternative is `eval` on a user-supplied operator.
_OPERATORS: Final[dict[str, Any]] = {
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}


@register_check("relationship")
def _relationship(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """`01` §4.5 `relationship`: a comparison between two columns holds on every row.

    `exposure_end > exposure_start` is the motivating case, and the general form is worth
    having: `sum_insured >= excess`, `date_reported >= date_of_loss`.
    """
    frame = _table(tables, rule)
    left, right = rule.params.get("left"), rule.params.get("right")
    operator = rule.params.get("operator", ">")
    if not left or not right:
        return CheckOutcome(skipped=True, skip_reason="`left` and `right` are both required")
    if operator not in _OPERATORS:
        raise ValueError(
            f"{operator!r} is not a permitted comparison; `01` §4.5 allows "
            f"{sorted(_OPERATORS)}"
        )

    holds = _OPERATORS[operator](pl.col(left), pl.col(right))
    offending = frame.filter(
        pl.col(left).is_not_null() & pl.col(right).is_not_null() & ~holds
    )
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"violating_rows": offending.height},
        threshold={"rule": f"{left} {operator} {right}"},
        detail=f"{offending.height} row(s) where `{left} {operator} {right}` does not hold",
        offending_sample=_sample(offending, rule.params.get("key_columns", [])),
    )


@register_check("expression")
def _expression(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """`01` §4.5 `expression`: a row-level predicate in the restricted grammar.

    The **same** grammar `derive_expression` uses in a Preparation Recipe — compiled from
    an AST into Polars, never `eval`. One grammar, so a user who has written a derivation
    can write a rule without learning a second language, and neither can reach the
    interpreter.
    """
    from pricing_core.data.expressions import compile_expression

    frame = _table(tables, rule)
    expression = rule.params.get("expr") or rule.params.get("expression")
    if not expression:
        return CheckOutcome(skipped=True, skip_reason="no expression declared")

    predicate = compile_expression(str(expression))
    expect = bool(rule.params.get("expect", True))
    offending = frame.filter(predicate.not_() if expect else predicate)
    return CheckOutcome(
        violating_rows=offending.height,
        measured={"violating_rows": offending.height},
        threshold={"expr": expression, "expect": expect},
        detail=f"{offending.height} row(s) where `{expression}` is not {expect}",
        offending_sample=_sample(offending, rule.params.get("key_columns", [])),
    )


@register_check("aggregate")
def _aggregate(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """`01` §4.5 `aggregate`: a group-level assertion.

    Counts *groups* that breach the bound, not rows. "Three vehicle groups have a mean
    premium above the cap" is the finding; "four hundred thousand rows belong to a group
    that does" is the same fact, told in a way nobody can act on.
    """
    frame = _table(tables, rule)
    column = rule.target.get("column")
    how = rule.params.get("agg", "sum")
    group_by = [g for g in rule.params.get("group_by", []) if g in frame.columns]
    if column is None or column not in frame.columns:
        return CheckOutcome(skipped=True, skip_reason=f"{column!r} is not present")

    aggregations = {
        "sum": pl.col(column).cast(pl.Float64).sum(),
        "mean": pl.col(column).cast(pl.Float64).mean(),
        "count": pl.col(column).count(),
        "min": pl.col(column).cast(pl.Float64).min(),
        "max": pl.col(column).cast(pl.Float64).max(),
    }
    if how == "quantile":
        aggregations["quantile"] = pl.col(column).cast(pl.Float64).quantile(
            float(rule.params.get("quantile", 0.5)), interpolation="linear"
        )
    if how not in aggregations:
        raise ValueError(
            f"{how!r} is not a permitted aggregate; §4.5 allows {sorted(aggregations)}"
        )

    measure = aggregations[how].alias("_value")
    grouped = frame.group_by(group_by).agg(measure) if group_by else frame.select(measure)

    predicate = pl.lit(False)
    if (bound := rule.params.get("min")) is not None:
        predicate = predicate | (pl.col("_value") < bound)
    if (bound := rule.params.get("max")) is not None:
        predicate = predicate | (pl.col("_value") > bound)
    if (bound := rule.params.get("equals")) is not None:
        predicate = predicate | (pl.col("_value") != bound)

    offending = grouped.filter(predicate)
    return CheckOutcome(
        violating_rows=offending.height,
        measured={
            "groups": grouped.height,
            "breaching_groups": offending.height,
            "agg": how,
        },
        threshold={k: v for k, v in rule.params.items() if k in ("min", "max", "equals")},
        detail=(
            f"{offending.height} of {grouped.height} group(s) breach the {how} bound on "
            f"{column!r}"
        ),
        offending_sample=_sample(offending, group_by),
    )


@register_check("distribution_compare")
def _distribution_compare(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], ctx: ValidationContext
) -> CheckOutcome:
    """`01` §4.5 `distribution_compare`: PSI, KS or mean shift against the reference.

    A façade over the built-in distributional checks rather than a fourth implementation of
    the same statistic — `metric: psi` is VR-DST-1 and `metric: mean_shift` is VR-DST-6, so
    a custom rule and a built-in one cannot report different numbers for the same column.
    """
    metric = rule.params.get("metric", "psi")
    delegate = {"psi": "psi_column", "mean_shift": "mean_shift"}.get(metric)
    if delegate is None:
        return CheckOutcome(
            skipped=True,
            skip_reason=(
                f"metric {metric!r} is not implemented; `psi` and `mean_shift` are. KS "
                "needs the reference column's values, which a stored Profile does not keep "
                "(FR-DATA-24 reads aggregates, not rows)"
            ),
        )
    return CHECKS[delegate](rule, tables, ctx)


_alias("set_membership", "allowed_values")
_alias("uniqueness", "unique_key")

# -- the engine ------------------------------------------------------------------------------


#: The `sql` check's hard ceiling, independent of the rule budget. The engine's budget is
#: checked *after* a check returns, which is fine for a Polars expression and useless
#: against `SELECT * FROM a, b` — that has to be interrupted, not reported on afterwards.
SQL_TIMEOUT_S: Final = 30.0

#: DuckDB settings that make a user's query safe to run. Every one of them is load-bearing:
#: without `enable_external_access` a query reads `/etc/passwd`, and without the extension
#: settings it installs and loads one that does.
_SQL_SANDBOX: Final[dict[str, str]] = {
    "enable_external_access": "false",
    "autoinstall_known_extensions": "false",
    "autoload_known_extensions": "false",
    "allow_unsigned_extensions": "false",
    "lock_configuration": "true",
}


class SqlCheckError(RuntimeError):
    """A `sql` check that could not be run safely. Never a pass (FR-DATA-19)."""


def _reject_unless_single_select(query: str) -> None:
    """`01` §4.5: a single `SELECT`, parsed rather than pattern-matched.

    Parsed by DuckDB itself, because a regex over SQL is a guess. `SELECT 1; DROP TABLE t`
    is two statements and a comment can hide the semicolon from anything but a parser.
    """
    import duckdb

    try:
        statements = duckdb.extract_statements(query)
    except Exception as exc:
        raise SqlCheckError(f"the query does not parse: {exc}") from exc

    if len(statements) != 1:
        raise SqlCheckError(
            f"a sql check is exactly one statement; this is {len(statements)}. "
            "`01` §4.5 permits a single SELECT."
        )
    kind = statements[0].type
    # `==`, not `is`: DuckDB's `StatementType` comes from the `_duckdb` extension module
    # and the value returned is not the same object as the one on the Python enum, so
    # identity is always False and every query would be refused as "not a SELECT".
    if kind != duckdb.StatementType.SELECT:
        raise SqlCheckError(
            f"a sql check must be a SELECT; this is {getattr(kind, 'name', kind)}. "
            "A validation rule reads — one that writes would change the data it is "
            "judging."
        )


@register_check("sql")
def _sql(
    rule: ValidationRule, tables: Mapping[str, pl.DataFrame], context: ValidationContext
) -> CheckOutcome:
    """The escape hatch, sandboxed (`01` §4.5, NFR-DATA-9, OQ-DATA-3).

    Four controls, and the query is refused unless all four hold:

    * **One `SELECT`**, established by DuckDB's own parser.
    * **No filesystem and no extensions**, by connection configuration that is then locked.
      The tables under test are registered as views from frames already in memory, so the
      query has data to read without the connection having a path to anything else.
    * **A hard timeout**, enforced by interrupting the connection from a watchdog thread.
      The engine's per-rule budget is checked after a check returns, which cannot stop a
      cartesian join.
    * **A scalar result** — a count or a boolean. A rule reports a number of violating
      rows; a query returning a table has not answered the question the rule asks.

    Authoring is Admin-only and the whole check is behind a workspace flag that defaults to
    off; both are enforced by the platform, because `pricing-core` has no notion of either
    (ADR-0001).
    """
    import threading

    import duckdb

    query = str(rule.params.get("query", "")).strip()
    if not query:
        raise SqlCheckError("a sql check needs a `query` parameter")
    _reject_unless_single_select(query)

    timeout_s = float(rule.params.get("timeout_s", SQL_TIMEOUT_S))
    connection = duckdb.connect(":memory:", config=dict(_SQL_SANDBOX))
    watchdog = threading.Timer(timeout_s, connection.interrupt)
    try:
        for name, frame in tables.items():
            # `register` takes the frame by reference; the view is the only thing the query
            # can see, and it disappears with the connection.
            connection.register(name, frame)
        for name, frame in context.reference_frames.items():
            connection.register(f"ref_{name}", frame)

        watchdog.start()
        try:
            row = connection.execute(query).fetchone()
        except duckdb.InterruptException as exc:
            raise SqlCheckError(
                f"the query exceeded its {timeout_s:g}s budget and was interrupted "
                "(NFR-DATA-9). Recorded as an error, because an unrun rule is never a "
                "pass (FR-DATA-19)."
            ) from exc
        except duckdb.Error as exc:
            raise SqlCheckError(f"{type(exc).__name__}: {exc}") from exc
    finally:
        watchdog.cancel()
        connection.close()

    if row is None or len(row) != 1:
        raise SqlCheckError(
            "a sql check must return exactly one value — a violating-row count or a "
            "boolean. `01` §4.5: the query answers the rule's question, it does not "
            "produce a report of its own."
        )

    value = row[0]
    if isinstance(value, bool):
        # `true` means the assertion holds, so violations are zero.
        return CheckOutcome(
            violating_rows=0 if value else 1,
            measured={"result": value},
            detail=rule.message or "custom sql assertion",
        )
    if isinstance(value, int):
        if value < 0:
            raise SqlCheckError(f"a violating-row count cannot be negative; got {value}")
        return CheckOutcome(
            violating_rows=value,
            measured={"violating_rows": value},
            detail=rule.message or "custom sql count",
        )
    raise SqlCheckError(
        f"a sql check returns a count or a boolean; got {type(value).__name__}"
    )


def run_validation(
    tables: Mapping[str, pl.DataFrame],
    rule_set: ValidationRuleSet,
    *,
    dataset_version_id: UUID,
    reference_tables: Mapping[str, pl.DataFrame] | None = None,
    reference_frames: Mapping[str, pl.DataFrame] | None = None,
    reference_profile: Profile | None = None,
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
        reference_profile=reference_profile,
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
