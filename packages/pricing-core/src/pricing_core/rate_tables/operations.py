"""Rate-table operations (03 §3.3, slice W10-2): seeding, validation, cell diffs.

The pricing actions behind FR-RATE-16 (seed a table from an approved model),
FR-RATE-19 (validation on save, checked before the version persists) and FR-RATE-17
(cell-level diffs with exposure weighting). Pure operations: cells are rows of
decimal strings (R2), exposure weights are supplied by the caller at diff-fetch time
(DP1), and no persistence happens here.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from itertools import product

from model_schema.modelling import GlmFitResult, Model, RelativityLevel
from model_schema.rating import (
    RateTable,
    RateTableDiff,
    RateTableKey,
    RateTableKeyType,
    RateTableStorageMode,
    RateTableValue,
    RateTableValueType,
    SeededFrom,
)
from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import ValidationIssue

_APPROVED_OR_BETTER = frozenset({"approved", "live", "retired"})

#: The plan's named validation failure codes (plan §Slice W10-2 T3). Internal codes:
#: the API maps them onto 03 §5.1's module error codes at the boundary.
INCOMPLETE_KEY_DOMAIN = "INCOMPLETE_KEY_DOMAIN"
NULL_VALUE = "NULL_VALUE"
OUT_OF_BOUNDS = "OUT_OF_BOUNDS"
DUPLICATE_KEY = "DUPLICATE_KEY"

#: One cell row: the declared key columns plus the value column, all decimal strings.
CellRow = dict[str, str]
Cells = Sequence[CellRow]

#: The key of a row: one value per declared key column, in key-declaration order.
KeyTuple = tuple[str, ...]

#: Per-cell exposure weights, keyed by row key (DP1: supplied at diff-fetch time).
Weights = Mapping[KeyTuple, Decimal | int | float]


@dataclass(frozen=True)
class SeedResult:
    """What seeding produces: the table definition, the cells, and the seed origin."""

    table: RateTable
    cells: tuple[CellRow, ...]
    seeded_from: SeededFrom


def check_model_approved(model: Model) -> None:
    """FR-OVR-14: only an approved (or better) model may seed a rate table."""
    if model.status not in _APPROVED_OR_BETTER:
        raise ValueError(
            f"PIN_NOT_APPROVED: model {model.model_family_slug}@{model.version} "
            f"is {model.status}, not approved"
        )


def _glm_relativities(
    model: Model,
) -> dict[str, tuple[RelativityLevel, ...]]:
    """The GLM relativity table, or a named refusal for any other fit kind.

    Only `GlmFitResult` carries per-level relativities (ADR-0003): a GBM or EBM fit has
    nothing to seed a rate table from. Raised as a plain message rather than a coded
    one so the API's boundary maps it to `VALIDATION_FAILED` — the code shape is
    reserved for codes the owning spec enumerates.
    """
    fit = model.fit_result
    if not isinstance(fit, GlmFitResult):
        kind = fit.model_type if fit is not None else "absent"
        raise ValueError(
            f"model {model.model_family_slug}@{model.version} carries a {kind} fit "
            "result; rate-table seeding reads GLM relativities"
        )
    return fit.relativities


def extract_relativity_table(
    model: Model, *, value_name: str = "relativity"
) -> list[CellRow]:
    """The model's factor relativities as cell rows (FR-RATE-16).

    Levels without a relativity (non-log links) are skipped: they have nothing to
    seed, and seeding 1.0 there would fabricate a technical rate. Values are
    rendered as decimal strings, never JSON floats (R2).
    """
    rows: list[CellRow] = []
    for factor, levels in _glm_relativities(model).items():
        for level in levels:
            if level.relativity is None:
                continue
            rows.append({factor: level.level, value_name: str(Decimal(str(level.relativity)))})
    return rows


def _key_domains_of(model: Model) -> dict[str, frozenset[str]]:
    """One domain per factor: the levels that carry a seeded relativity."""
    return {
        factor: frozenset(level.level for level in levels if level.relativity is not None)
        for factor, levels in _glm_relativities(model).items()
    }


def seed_from_model(
    model: Model,
    *,
    table_slug: str,
    change_note: str,
    seeded_at: datetime,
    rateable: bool = True,
    value_name: str = "relativity",
) -> SeedResult:
    """Seed a rate table from an approved model (FR-RATE-16, plan §Slice W10-2 T1).

    Builds the table definition from the model's factor relativities, validates the
    extracted cells (T3's check runs before the version persists), and pins the seed
    origin so "how far from the technical rate?" is answerable.
    """
    check_model_approved(model)
    cells = tuple(extract_relativity_table(model, value_name=value_name))
    if not cells:
        raise ValueError(
            f"NO_RELATIVITIES: model {model.model_family_slug}@{model.version} "
            "carries no relativities"
        )

    keys = [
        RateTableKey(name=factor, type=RateTableKeyType.STRING, banding_ref=None)
        for factor in _glm_relativities(model)
    ]
    value = RateTableValue(
        name=value_name,
        type=RateTableValueType.RELATIVITY,
        unit="factor",
        min=None,
        max=None,
    )
    issues = validate_rate_table(cells, keys, value, key_domains=_key_domains_of(model))
    if issues:
        raise ValueError(f"{issues[0].code}: {issues[0].message}")

    table = RateTable(
        slug=table_slug,
        version=1,
        rateable=rateable,
        storage=RateTableStorageMode.ROWS,
        keys=keys,
        value=value,
        default_row=None,
    )
    seeded_from = SeededFrom(
        model_ref=ArtifactRef(
            type="model", slug=model.model_family_slug, version=model.version
        ),
        seeded_at=seeded_at,
    )
    return SeedResult(table=table, cells=cells, seeded_from=seeded_from)


def validate_rate_table(
    cells: Cells,
    keys: Sequence[RateTableKey],
    value: RateTableValue,
    *,
    key_domains: Mapping[str, frozenset[str]],
    default_row: CellRow | None = None,
) -> list[ValidationIssue]:
    """FR-RATE-19: named validation, checked before the version persists.

    Coverage is the Cartesian product of the declared key domains unless an explicit
    `default_row` waives it. Every row must have a non-null, in-bounds decimal value,
    and no duplicate keys. Failures are named per plan T3: INCOMPLETE_KEY_DOMAIN,
    NULL_VALUE, OUT_OF_BOUNDS, DUPLICATE_KEY.
    """
    issues: list[ValidationIssue] = []
    key_names = [key.name for key in keys]
    lower_bound, upper_bound = value.min, value.max

    seen: set[KeyTuple] = set()
    for row in cells:
        key_values = tuple(row[key] for key in key_names)
        if key_values in seen:
            issues.append(
                ValidationIssue(
                    code=DUPLICATE_KEY,
                    message=f"key {key_values} appears more than once",
                    field=".".join(key_names),
                )
            )
            continue
        seen.add(key_values)

        raw = row.get(value.name)
        if raw is None or raw == "":
            issues.append(
                ValidationIssue(
                    code=NULL_VALUE,
                    message=f"no value for key {key_values}",
                    field=value.name,
                )
            )
            continue
        try:
            decimal_value = Decimal(raw)
        except InvalidOperation:
            issues.append(
                ValidationIssue(
                    code=OUT_OF_BOUNDS,
                    message=f"value {raw!r} for key {key_values} is not a decimal number",
                    field=value.name,
                )
            )
            continue
        if lower_bound is not None and decimal_value < lower_bound:
            issues.append(
                ValidationIssue(
                    code=OUT_OF_BOUNDS,
                    message=(
                        f"value {raw} for key {key_values} is below the declared "
                        f"minimum {lower_bound}"
                    ),
                    field=value.name,
                )
            )
        elif upper_bound is not None and decimal_value > upper_bound:
            issues.append(
                ValidationIssue(
                    code=OUT_OF_BOUNDS,
                    message=(
                        f"value {raw} for key {key_values} is above the declared "
                        f"maximum {upper_bound}"
                    ),
                    field=value.name,
                )
            )

    if default_row is None:
        missing = [
            combination
            for combination in product(*(key_domains[key] for key in key_names))
            if combination not in seen
        ]
        for combination in missing:
            issues.append(
                ValidationIssue(
                    code=INCOMPLETE_KEY_DOMAIN,
                    message=f"missing value for key combination {combination}",
                    field=".".join(key_names),
                )
            )
    return issues


def _index_rows(
    cells: Cells, key_names: Sequence[str], value_name: str
) -> dict[KeyTuple, Decimal]:
    """Map each row's key to its value. Callers hand validated cells (unique keys)."""
    return {
        tuple(row[key] for key in key_names): Decimal(row[value_name]) for row in cells
    }


def _compute_diff(
    baseline: Cells,
    current: Cells,
    keys: Sequence[RateTableKey],
    value: RateTableValue,
    weights: Weights | None,
) -> RateTableDiff:
    """The shared core of diff_vs_previous and diff_vs_seed (FR-RATE-17).

    A cell counts as changed when its value differs from the baseline; an added or
    removed key counts. Percentage statistics cover cells comparable in both
    directions with a non-zero baseline, so a cell born from or into zero never
    fabricates an infinite change. The exposure-weighted mean covers the comparable
    cells that carry a weight (DP1: weights at fetch time).
    """
    key_names = [key.name for key in keys]
    before = _index_rows(baseline, key_names, value.name)
    after = _index_rows(current, key_names, value.name)

    changed = sorted(
        key for key in before.keys() | after.keys() if before.get(key) != after.get(key)
    )
    comparable: list[Decimal] = []
    weighted: list[tuple[Decimal, Decimal]] = []
    for key in changed:
        old, new = before.get(key), after.get(key)
        if old is None or new is None or old == 0:
            continue
        pct = (new - old) / old * 100
        comparable.append(pct)
        if weights is not None:
            raw_weight = weights.get(key)
            if raw_weight is not None:
                weighted.append((Decimal(str(raw_weight)), pct))

    max_abs = max(abs(pct) for pct in comparable) if comparable else None
    if weighted:
        # An explicit Decimal start keeps the sum Decimal — `sum` starts at int 0,
        # and a Decimal|int mean would not fit RateTableDiff's Decimal field.
        total_weight = sum((weight for weight, _ in weighted), Decimal(0))
        mean = (
            sum((weight * pct for weight, pct in weighted), Decimal(0)) / total_weight
        )
    else:
        mean = None
    return RateTableDiff(
        changed_cells=len(changed),
        max_abs_change_pct=max_abs,
        exposure_weighted_mean_change_pct=mean,
    )


def diff_vs_previous(
    previous_cells: Cells,
    current_cells: Cells,
    keys: Sequence[RateTableKey],
    value: RateTableValue,
    *,
    weights: Weights | None = None,
) -> RateTableDiff:
    """Diff against the immediately prior version (FR-RATE-17)."""
    return _compute_diff(previous_cells, current_cells, keys, value, weights)


def diff_vs_seed(
    seed_cells: Cells,
    current_cells: Cells,
    keys: Sequence[RateTableKey],
    value: RateTableValue,
    *,
    weights: Weights | None = None,
) -> RateTableDiff:
    """Diff against the seed origin, the technical rate (FR-RATE-16/17)."""
    return _compute_diff(seed_cells, current_cells, keys, value, weights)
