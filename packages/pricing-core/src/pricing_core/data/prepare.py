"""Preparation recipes (`01` §3.2, §5.2, FR-35, FR-36, FR-37, FR-38, FR-39, FR-41).

> A **Preparation Recipe** is an ordered list of declarative steps applied during
> ingestion. Supported step types are exactly: … **No free-form code.**

Declarative because a recipe is *evidence*. FR-41 requires it to be replayable — the
same recipe over the same bytes reproduces the same version — and a step that could run
arbitrary code is a step whose replay depends on what that code could reach on the day.

Three steps carry real actuarial weight and are implemented as named functions rather than
recipe entries, because `02` and the ingestion path both call them:

* **`explode_period`** preserves `sum(exposure)` **exactly**, in `Decimal` (FR-37).
  Splitting a mid-term change into two rows with floats loses fractions of a policy-year
  per split; across a million policies that is a visible error in the frequency
  denominator, arrived at by arithmetic nobody questioned.
* **`attach_claims`** reports unlinked and multi-linked claims rather than dropping them
  (FR-38) — a claim that fails to link is the most important row in the file.
* **`pseudonymise`** maps a customer to a stable token per workspace (FR-39), so the
  same person is recognisable across versions and meaningless outside.
"""

from __future__ import annotations

import hashlib
import hmac
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Final

import polars as pl

from pricing_core.data.expressions import GrammarProfile, compile_expression
from pricing_core.data.ingest import (
    REJECT_COLUMN_COLUMN,
    REJECT_REASON_COLUMN,
    REJECT_STEP_COLUMN,
)
from pricing_core.progress import ProgressCallback

__all__ = [
    "STEP_TYPES",
    "AttachResult",
    "PreparationResult",
    "RecipeError",
    "apply_recipe",
    "attach_claims",
    "decimal_sum",
    "explode_period",
    "pseudonymise",
]

#: FR-35 says *exactly* these. A recipe naming anything else is refused rather than
#: ignored: a step that silently does nothing is worse than one that fails, because the
#: version it produces looks prepared.
STEP_TYPES: Final[frozenset[str]] = frozenset(
    {
        "rename",
        "cast",
        "parse_date",
        "trim_whitespace",
        "normalise_case",
        "map_values",
        "fill_null",
        "derive_expression",
        "filter_rows",
        "deduplicate",
        "join_table",
        "derive_exposure",
        "explode_period",
        "attach_claims",
        "pseudonymise",
    }
)

DAYS_PER_YEAR: Final = Decimal("365.25")


class RecipeError(ValueError):
    """A recipe step is malformed or names something outside the declared vocabulary."""


@dataclass(frozen=True)
class PreparationResult:
    """What a recipe produced (`01` §5.2)."""

    tables: dict[str, pl.DataFrame]
    rejected: pl.DataFrame | None = None
    stats: dict[str, Any] = field(default_factory=dict)


#: A private row index carried through every step (FR-32). Normalised source columns never
#: start with `_` (`ingest.py`), so it cannot collide; it is dropped before `apply_recipe`
#: returns.
_SOURCE_ROW: Final = "_source_row"

#: The steps whose job is to parse, and so the only ones that can turn a value into a null.
_PARSING_STEPS: Final = frozenset({"cast", "parse_date"})


def apply_recipe(
    tables: Mapping[str, pl.DataFrame],
    recipe: Sequence[Mapping[str, Any]],
    *,
    progress: ProgressCallback | None = None,
) -> PreparationResult:
    """Apply an ordered list of declarative steps (FR-35).

    Steps are applied in order and each sees the previous one's output — a recipe is a
    pipeline, and reordering it is a different recipe rather than the same one written
    differently.

    **A cell that does not parse is never silently nulled (FR-32).** A `cast` or
    `parse_date` that turns a non-null cell into a null quarantines the whole *source* row:
    it leaves every working table and is returned in `.rejected` as the input's text, with
    the column and step that failed it. The quarantine is complete for each row — no partly
    cast row and no row derived from it is written. `stats["steps"]` records each step's
    heights and its `rows_rejected`, `rows_removed` and `rows_added`, so that
    `rows_read - sum(rejected) - sum(removed) + sum(added) == rows written`.
    """
    sources = dict(tables)
    working = {name: _with_source_row(name, frame) for name, frame in sources.items()}
    rejects: list[pl.DataFrame] = []
    stats: dict[str, Any] = {"steps": []}

    for index, step in enumerate(recipe):
        kind = step.get("step")
        if kind not in STEP_TYPES:
            raise RecipeError(
                f"step {index} is {kind!r}, which is not one of the declared step types "
                f"(FR-35). Permitted: {sorted(STEP_TYPES)}."
            )
        if progress is not None:
            progress.check_cancelled()
            progress.update(index / max(len(recipe), 1), f"preparing: {kind}", steps=index)

        table = step.get("table", next(iter(working)))
        if table not in working:
            raise RecipeError(f"step {index} targets table {table!r}, which is not present")

        before_frame = working[table]
        before = before_frame.height
        after_frame = _apply_step(kind, before_frame, step)

        rejected_rows = quarantined = 0
        if kind in _PARSING_STEPS:
            failed = _coercion_failures(kind, before_frame, after_frame, step)
            if failed is not None:
                indices = failed[_SOURCE_ROW]
                rejects.append(_quarantine_frame(sources[table], failed, indices))
                rejected_rows = indices.n_unique()
                kept = ~after_frame[_SOURCE_ROW].is_in(indices.implode())
                quarantined = after_frame.height - int(kept.sum())
                after_frame = after_frame.filter(kept)
        working[table] = after_frame

        after = after_frame.height
        delta = after - (before - quarantined)
        stats["steps"].append(
            {
                "step": kind,
                "table": table,
                "rows_before": before,
                "rows_after": after,
                "rows_rejected": rejected_rows,
                "rows_removed": max(-delta, 0) + (quarantined - rejected_rows),
                "rows_added": max(delta, 0),
            }
        )

    rejected = pl.concat(rejects, how="diagonal") if rejects else None
    return PreparationResult(
        tables={name: frame.drop(_SOURCE_ROW) for name, frame in working.items()},
        rejected=rejected,
        stats=stats,
    )


def _with_source_row(name: str, frame: pl.DataFrame) -> pl.DataFrame:
    if _SOURCE_ROW in frame.columns:
        raise RecipeError(f"table {name!r} already has a column named {_SOURCE_ROW!r}")
    return frame.with_row_index(_SOURCE_ROW)


def _coercion_failures(
    kind: str, before: pl.DataFrame, after: pl.DataFrame, step: Mapping[str, Any]
) -> pl.DataFrame | None:
    """The rows where a named column was non-null before the step and is null after it.

    Returns `_source_row`, the first failing column (in the step's declared order), the
    reason, and the pre-step text of that cell; or `None` when nothing failed. The steps
    here are row-preserving, so `before` and `after` line up row for row.
    """
    params = step.get("params", {})
    if kind == "cast":
        targets = [(column, str(dtype)) for column, dtype in params["columns"].items()]
    else:
        targets = [(params["column"], params["format"])]

    # Narrow to the failing rows first: the reason text is built per value in Python, which is
    # affordable for a handful of rejects and not for a whole book that parsed cleanly.
    any_failed = pl.Series([False] * before.height)
    for column, _ in targets:
        any_failed = any_failed | (before[column].is_not_null() & after[column].is_null())
    if not any_failed.any():
        return None
    before, after = before.filter(any_failed), after.filter(any_failed)

    reason: pl.Expr = pl.lit(None, dtype=pl.String)
    column_of: pl.Expr = pl.lit(None, dtype=pl.String)
    for column, target in reversed(targets):
        failed = before[column].is_not_null() & after[column].is_null()
        text = before[column].cast(pl.String)
        message = pl.concat_str(
            pl.lit(f"{column}: {kind} could not parse "),
            text.map_elements(repr, return_dtype=pl.String),
            pl.lit(f" as {target}"),
        )
        reason = pl.when(failed).then(message).otherwise(reason)
        column_of = pl.when(failed).then(pl.lit(column)).otherwise(column_of)
    frame = pl.DataFrame({_SOURCE_ROW: before[_SOURCE_ROW]}).with_columns(
        reason.alias(REJECT_REASON_COLUMN), column_of.alias(REJECT_COLUMN_COLUMN)
    )
    return frame.filter(pl.col(REJECT_COLUMN_COLUMN).is_not_null()).with_columns(
        pl.lit(kind).alias(REJECT_STEP_COLUMN)
    )


def _quarantine_frame(
    source: pl.DataFrame, failed: pl.DataFrame, indices: pl.Series
) -> pl.DataFrame:
    """The failed rows as the *input's* text (never a step's output), with their reasons.

    One row per source row: a row a later step has duplicated is quarantined once.
    """
    failed = failed.unique(subset=_SOURCE_ROW, keep="first", maintain_order=True)
    text = source.with_row_index(_SOURCE_ROW).select(
        pl.col(_SOURCE_ROW), pl.all().exclude(_SOURCE_ROW).cast(pl.String)
    )
    return failed.join(text, on=_SOURCE_ROW, how="left", maintain_order="left").select(
        pl.all().exclude(
            _SOURCE_ROW, REJECT_REASON_COLUMN, REJECT_COLUMN_COLUMN, REJECT_STEP_COLUMN
        ),
        REJECT_REASON_COLUMN,
        REJECT_COLUMN_COLUMN,
        REJECT_STEP_COLUMN,
    )


def _apply_step(kind: str, frame: pl.DataFrame, step: Mapping[str, Any]) -> pl.DataFrame:
    params = step.get("params", {})
    match kind:
        case "rename":
            return frame.rename(dict(params["columns"]))
        case "cast":
            return frame.with_columns(
                pl.col(column).cast(_dtype(dtype), strict=False)
                for column, dtype in params["columns"].items()
            )
        case "parse_date":
            return frame.with_columns(
                pl.col(params["column"])
                .str.strptime(pl.Date, params["format"], strict=False)
                .alias(params["column"])
            )
        case "trim_whitespace":
            return frame.with_columns(
                pl.col(c).str.strip_chars() for c in params["columns"]
            )
        case "normalise_case":
            upper = params.get("case", "lower") == "upper"
            return frame.with_columns(
                (pl.col(c).str.to_uppercase() if upper else pl.col(c).str.to_lowercase())
                for c in params["columns"]
            )
        case "map_values":
            mapping = params["mapping"]
            column = params["column"]
            return frame.with_columns(
                pl.col(column).replace(mapping).alias(column)
            )
        case "fill_null":
            return frame.with_columns(
                pl.col(params["column"]).fill_null(params["value"]).alias(params["column"])
            )
        case "derive_expression":
            return frame.with_columns(
                compile_expression(params["expression"], profile=GrammarProfile.RECIPE).alias(
                    params["column"]
                )
            )
        case "filter_rows":
            return frame.filter(
                compile_expression(params["expression"], profile=GrammarProfile.RECIPE)
            )
        case "deduplicate":
            subset = params.get("columns") or [c for c in frame.columns if c != _SOURCE_ROW]
            return frame.unique(subset=subset, keep="first", maintain_order=True)
        case "pseudonymise":
            return pseudonymise(frame, column=params["column"], key=params["key"])
        case _:
            raise RecipeError(
                f"{kind!r} is a declared step type but has no implementation in this build"
            )


def _dtype(name: str) -> Any:
    """The Polars dtype for a cast target. `Any` because Polars types these as classes,
    not instances, and the distinction is not one this function can resolve."""
    mapping: dict[str, Any] = {
        "int": pl.Int64, "int64": pl.Int64, "int32": pl.Int32,
        "float": pl.Float64, "float64": pl.Float64,
        "string": pl.String, "str": pl.String, "bool": pl.Boolean, "date": pl.Date,
    }
    if name not in mapping:
        raise RecipeError(f"{name!r} is not a supported cast target")
    return mapping[name]


def explode_period(
    frame: pl.DataFrame,
    *,
    key_column: str = "policy_id",
    start_column: str = "exposure_start",
    end_column: str = "exposure_end",
    exposure_column: str = "exposure_years",
    boundaries: Sequence[date] = (),
) -> pl.DataFrame:
    """Split exposure rows at declared boundaries, preserving the total exactly (FR-37).

    The post-condition is checked, not assumed: `sum(exposure)` before must equal
    `sum(exposure)` after, in `Decimal`. Apportioning with floats loses fractions of a
    policy-year per split, and across a million policies that is a visible error in every
    frequency denominator — arrived at by arithmetic nobody thought to question.

    The last fragment absorbs the rounding remainder rather than each fragment rounding
    independently, which is what makes the sum exact rather than nearly exact.
    """
    if frame.height == 0:
        return frame

    total_before = decimal_sum(frame, exposure_column)
    rows: list[dict[str, Any]] = []

    for record in frame.iter_rows(named=True):
        start, end = record[start_column], record[end_column]
        exposure = Decimal(str(record[exposure_column]))
        cuts = sorted(b for b in boundaries if start < b < end)

        if not cuts:
            rows.append(dict(record))
            continue

        edges = [start, *cuts, end]
        span_days = Decimal((end - start).days)
        allocated = Decimal("0")

        for index in range(len(edges) - 1):
            fragment_start, fragment_end = edges[index], edges[index + 1]
            if index == len(edges) - 2:
                # The remainder, so the fragments sum to the original exactly.
                share = exposure - allocated
            else:
                fragment_days = Decimal((fragment_end - fragment_start).days)
                share = (
                    (exposure * fragment_days / span_days).quantize(Decimal("0.000001"))
                    if span_days
                    else Decimal("0")
                )
                allocated += share
            rows.append(
                {
                    **record,
                    start_column: fragment_start,
                    end_column: fragment_end,
                    exposure_column: float(share),
                }
            )

    exploded = pl.DataFrame(rows, schema=frame.schema)
    total_after = decimal_sum(exploded, exposure_column)
    if total_before != total_after:
        raise RecipeError(
            f"explode_period changed total exposure from {total_before} to {total_after}. "
            "FR-37 requires sum(exposure) preserved exactly; a difference here is a "
            "silent error in every frequency denominator downstream."
        )
    return exploded


def decimal_sum(frame: pl.DataFrame, column: str) -> Decimal:
    """Sum in `Decimal` via strings. Summing floats and comparing is the bug being caught."""
    return sum(
        (Decimal(str(v)) for v in frame.get_column(column).to_list() if v is not None),
        Decimal("0"),
    ).quantize(Decimal("0.000001"))


@dataclass(frozen=True)
class AttachResult:
    """Linked claims, plus the ones that could not be linked (FR-38)."""

    linked: pl.DataFrame
    unlinked: pl.DataFrame
    multi_linked: pl.DataFrame

    @property
    def counts(self) -> dict[str, int]:
        return {
            "linked": self.linked.height,
            "unlinked": self.unlinked.height,
            "multi_linked": self.multi_linked.height,
        }


def attach_claims(
    exposure: pl.DataFrame,
    claims: pl.DataFrame,
    *,
    key_column: str = "policy_id",
    loss_date_column: str = "date_of_loss",
    start_column: str = "exposure_start",
    end_column: str = "exposure_end",
) -> AttachResult:
    """Link claims to the exposure row covering the loss date (FR-38).

    Unlinked and multi-linked claims are **returned**, not dropped. A claim that fails to
    link is the most important row in the file: it is either a data error or a policy the
    exposure table does not know about, and both change what the model is fitted on.

    The period is half-open — `[start, end)` — so a loss on a renewal date belongs to the
    new term, matching how the policy was actually in force.
    """
    joined = claims.join(exposure, on=key_column, how="left", suffix="_exposure")
    within = joined.filter(
        pl.col(loss_date_column).is_not_null()
        & pl.col(start_column).is_not_null()
        & (pl.col(loss_date_column) >= pl.col(start_column))
        & (pl.col(loss_date_column) < pl.col(end_column))
    )

    claim_key = _claim_key(claims)
    match_counts = within.group_by(claim_key).len()
    exactly_one = match_counts.filter(pl.col("len") == 1).get_column(claim_key)
    more_than_one = match_counts.filter(pl.col("len") > 1).get_column(claim_key)

    linked = within.filter(pl.col(claim_key).is_in(exactly_one))
    multi = within.filter(pl.col(claim_key).is_in(more_than_one))
    unlinked = claims.filter(
        ~pl.col(claim_key).is_in(within.get_column(claim_key).unique())
    )
    return AttachResult(linked=linked, unlinked=unlinked, multi_linked=multi)


def _claim_key(claims: pl.DataFrame) -> str:
    for candidate in ("claim_id", "claim_reference", "id"):
        if candidate in claims.columns:
            return candidate
    raise RecipeError(
        "the claim table needs an identifying column (claim_id, claim_reference or id) "
        "so unlinked and multi-linked claims can be reported individually (FR-38)"
    )


def pseudonymise(frame: pl.DataFrame, *, column: str, key: str) -> pl.DataFrame:
    """Replace an identifier with a stable, workspace-scoped token (FR-39).

    HMAC-SHA256 rather than a bare hash: a plain `sha256(customer_id)` is reversible by
    anyone who can guess the id space, and customer ids are guessable. The workspace key
    makes the token meaningless outside the workspace that produced it, and stable within
    it — so the same customer is recognisable across versions, which is what makes
    longitudinal analysis possible without holding the identity.
    """
    if column not in frame.columns:
        raise RecipeError(f"pseudonymise targets {column!r}, which is not present")
    if not key:
        raise RecipeError(
            "pseudonymise needs a workspace key; without one the token is a plain hash and "
            "reversible by anyone who can guess the identifier space (FR-39)"
        )

    secret = key.encode()
    tokens = [
        None
        if value is None
        else hmac.new(secret, str(value).encode(), hashlib.sha256).hexdigest()[:32]
        for value in frame.get_column(column).to_list()
    ]
    return frame.with_columns(pl.Series(column, tokens, dtype=pl.String))
