"""The Dislocation Run's portfolio reader (03 §4.8's frame, §5.2; FR-263, FR-264).

WK-673 Slice 2, `RL-1402`. `read_portfolio` checks the frame when it is called, so a caller gets
the refusal before it builds anything on the result. Messages name a column and a count, or a
column and its dtype, and never a portfolio value.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal
from fractions import Fraction
from itertools import pairwise
from math import factorial
from typing import Any, Final

import polars as pl

from model_schema.dislocation import (
    Attribution,
    AttributionItem,
    AttributionSummary,
    BundleDelta,
    ChangeGroup,
    DeltaKind,
    DislocationBand,
    DislocationOutcomes,
    DislocationRun,
    DislocationSpec,
    DislocationTotals,
    ErrorSample,
    ErrorTally,
    RungContribution,
    SegmentSlice,
)
from model_schema.rating import (
    InterfaceDelta,
    Pins,
    RatingAlgorithm,
    RatingInputStep,
    RatingLookupStep,
    RatingModelCallStep,
    RatingOutputStep,
    RatingStepBase,
    RatingTableStep,
    RatingVersion,
    diff_algorithms,
)
from model_schema.refs import ArtifactRef
from model_schema.scoring import LadderRung
from pricing_core.rating.compile import ArtifactResolver, ResolvedArtifact, compile_bundle
from pricing_core.rating.ladder import RUNG_ORDER
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_batch

__all__ = [
    "AttributionError",
    "PortfolioFrameError",
    "attribute",
    "derive_changes",
    "dislocate",
    "dislocation_frame",
    "estimate_attribution_ratings",
    "read_portfolio",
    "select_movers",
    "summarise_dislocation",
]

_STAMPED: Final[tuple[str, ...]] = ("purpose", "effective_date", "rating_version_ref")
_EXPOSURE_SCALE: Final = 6
#: The frame's own columns (RL-1402 S2) but `quote_id`; a portfolio column named as one is refused.
_FRAME_COLUMNS: Final[tuple[str, ...]] = (
    "baseline_outcome",
    "candidate_outcome",
    "baseline_minor",
    "candidate_minor",
    "change_minor",
    "baseline_error_code",
    "candidate_error_code",
    "origin_rung",
)


class PortfolioFrameError(ValueError):
    """A portfolio that breaks §4.8's frame; the platform maps it to `VALIDATION_FAILED`."""

    code = "VALIDATION_FAILED"


def _is_segment_dtype(dtype: pl.DataType) -> bool:
    return (
        dtype.is_integer()
        or dtype in (pl.String, pl.Boolean, pl.Date, pl.Categorical)
        or isinstance(dtype, pl.Enum)
    )


def _exposure_decimal(value: float) -> Decimal:
    return Decimal(str(round(value, _EXPOSURE_SCALE)))


def read_portfolio(portfolio: pl.LazyFrame, *, segments: Sequence[str] = ()) -> pl.LazyFrame:
    """Check §4.8's frame now; return it, every column kept, `exposure_years` read as a Decimal."""
    schema = portfolio.collect_schema()
    for name in _STAMPED:
        if name in schema:
            raise PortfolioFrameError(
                f"portfolio column {name!r} is reserved and stamped, never read"
            )
    for name in ("quote_id", "exposure_years"):
        if name not in schema:
            raise PortfolioFrameError(f"portfolio column {name!r} is missing")
    exposure_dtype = schema["exposure_years"]
    is_float = exposure_dtype.is_float()
    if not (is_float or exposure_dtype.is_integer() or exposure_dtype.is_decimal()):
        raise PortfolioFrameError(f"column 'exposure_years' has dtype {exposure_dtype}")
    for name in segments:
        if name not in schema:
            raise PortfolioFrameError(f"segment column {name!r} is missing from the portfolio")
        if not _is_segment_dtype(schema[name]):
            raise PortfolioFrameError(f"segment column {name!r} has dtype {schema[name]}")

    exposure = pl.col("exposure_years")
    unusable = exposure.is_null()
    if is_float:
        unusable = unusable | exposure.is_nan() | exposure.is_infinite()
    counts = portfolio.select(
        quote_null=pl.col("quote_id").is_null().sum(),
        quote_duplicated=pl.col("quote_id").is_duplicated().sum(),
        exposure_unusable=unusable.sum(),
        exposure_negative=(exposure < 0).sum(),
    ).collect()
    for column, key, what in (
        ("quote_id", "quote_null", "null"),
        ("quote_id", "quote_duplicated", "duplicated"),
        ("exposure_years", "exposure_unusable", "null, NaN or infinite"),
        ("exposure_years", "exposure_negative", "negative"),
    ):
        count = counts[key][0]
        if count:
            raise PortfolioFrameError(f"column {column!r} has {count} {what} row(s)")

    if not is_float:
        return portfolio.with_columns(
            exposure.cast(pl.Decimal(None, _EXPOSURE_SCALE)).alias("exposure_years")
        )
    return portfolio.with_columns(
        exposure.map_elements(_exposure_decimal, return_dtype=pl.Decimal(None, _EXPOSURE_SCALE))
    )


def _origin_rung(baseline: Sequence[LadderRung], candidate: Sequence[LadderRung]) -> str | None:
    """The first rung, in `RUNG_ORDER`, present in one ladder only or differing in `value_minor`
    or in `unrounded_minor` (a `Decimal`: `Decimal("100") == Decimal("100.0")`)."""
    base = {r.rung: r for r in baseline}
    cand = {r.rung: r for r in candidate}
    for name in RUNG_ORDER:
        b, c = base.get(name), cand.get(name)
        if b is None and c is None:
            continue
        if b is None or c is None or b.value_minor != c.value_minor:
            return name
        if b.unrounded_minor != c.unrounded_minor:  # Decimal values; None only equals None
            return name
    return None


def _score_pass(
    bundle: CompiledBundle,
    portfolio: pl.LazyFrame,
    columns: Sequence[str],
    spec: DislocationSpec,
    ref: object,
) -> dict[str, dict[str, Any]]:
    """One pass: only `quote_id` and the contract's declared inputs reach the engine (RL-1394)."""
    declared = [f.name for f in bundle.algorithm.input_contract if f.name in columns]
    frame = portfolio.select(["quote_id", *declared]).with_columns(
        pl.lit(spec.purpose).alias("purpose"),
        pl.lit(spec.as_at.isoformat()).alias("effective_date"),
        pl.lit(str(ref)).alias("rating_version_ref"),
    )
    out: dict[str, dict[str, Any]] = {}
    for row in score_batch(bundle, frame).collect().iter_rows(named=True):
        ladder: list[LadderRung] = []
        premium: int | None = None
        if row["outcome"] == "quoted":
            ladder = [LadderRung.model_validate(r) for r in json.loads(row["premium_ladder_json"])]
            payable = [r for r in ladder if r.rung == "payable_premium"]
            if not payable:
                raise ValueError("dislocation: a quoted row carries no payable_premium rung")
            premium = int(payable[0].value_minor)
        out[row["quote_id"]] = {
            "outcome": row["outcome"],
            "error_code": row["error_code"],
            "minor": premium,
            "ladder": ladder,
        }
    return out


def dislocation_frame(
    baseline: CompiledBundle,
    candidate: CompiledBundle,
    portfolio: pl.LazyFrame,
    spec: DislocationSpec,
) -> pl.DataFrame:
    """One row per policy, sorted by `quote_id` (RL-1402 DP-S2-1, S2): both passes' outcome,
    payable premium in integer minor units, the change, the rung it originated at, then every
    portfolio column. Each pass is given only its own contract's declared inputs."""
    schema = portfolio.collect_schema()
    for name in _FRAME_COLUMNS:
        if name in schema:
            raise PortfolioFrameError(f"portfolio column {name!r} collides with the run's frame")
    checked = read_portfolio(portfolio, segments=spec.segments).collect()
    columns = schema.names()
    base = _score_pass(baseline, portfolio, columns, spec, spec.baseline_ref)
    cand = _score_pass(candidate, portfolio, columns, spec, spec.candidate_ref)

    rows: list[dict[str, Any]] = []
    for quote_id in sorted(base):
        b, c = base[quote_id], cand[quote_id]
        both = b["minor"] is not None and c["minor"] is not None
        rows.append(
            {
                "quote_id": quote_id,
                "baseline_outcome": b["outcome"],
                "candidate_outcome": c["outcome"],
                "baseline_minor": b["minor"],
                "candidate_minor": c["minor"],
                "change_minor": c["minor"] - b["minor"] if both else None,
                "baseline_error_code": b["error_code"],
                "candidate_error_code": c["error_code"],
                "origin_rung": _origin_rung(b["ladder"], c["ladder"]) if both else None,
            }
        )
    frame = pl.DataFrame(
        rows,
        schema={
            "quote_id": pl.String,
            "baseline_outcome": pl.String,
            "candidate_outcome": pl.String,
            "baseline_minor": pl.Int64,
            "candidate_minor": pl.Int64,
            "change_minor": pl.Int64,
            "baseline_error_code": pl.String,
            "candidate_error_code": pl.String,
            "origin_rung": pl.String,
        },
    )
    return frame.join(checked, on="quote_id", how="left", maintain_order="left").sort("quote_id")


# ---------------------------------------------------------------------------
# The summary (RL-1402 S1, S3-S5, Amendment N2; 03 §4.6). Money is an `int`; every ratio is a
# `Fraction` of ints rounded once; a float appears only at the model boundary.
# ---------------------------------------------------------------------------

_SAMPLE_SIZE: Final = 10
_SHARE_PLACES: Final = 6


def _rounded_float(ratio: Fraction, places: int) -> float:
    """Round the exact ratio once (half-even), exactly to a `Decimal`, and only then to a float."""
    r = round(ratio, places)
    return float(Decimal(r.numerator) / Decimal(r.denominator))


def _pct(change: int, baseline: int) -> float | None:
    """Σ change ÷ Σ baseline x 100 to 2 places; null when the denominator is 0."""
    return None if baseline == 0 else _rounded_float(Fraction(change, baseline) * 100, 2)


def _share(part: Decimal, whole: Decimal) -> float | None:
    return None if whole == 0 else _rounded_float(Fraction(part) / Fraction(whole), _SHARE_PLACES)


def _compared(frame: pl.DataFrame) -> pl.DataFrame:
    return frame.filter(
        (pl.col("baseline_outcome") == "quoted") & (pl.col("candidate_outcome") == "quoted")
    )


def _banded(frame: pl.DataFrame) -> pl.DataFrame:
    """The compared policies with a positive baseline (RL-1402, Amendment N2)."""
    return _compared(frame).filter(pl.col("baseline_minor") > 0)


def select_movers(frame: pl.DataFrame, spec: DislocationSpec) -> pl.DataFrame:
    """FR-263's movers: banded policies whose |change %| is at least `mover_threshold_pct`,
    decided on ints; by |pct| descending, |change_minor| descending, then `quote_id`."""
    threshold = Fraction(str(spec.mover_threshold_pct))
    kept = [
        row
        for row in _banded(frame).iter_rows(named=True)
        if 100 * abs(row["change_minor"]) >= threshold * row["baseline_minor"]
    ]
    kept.sort(
        key=lambda r: (
            -Fraction(abs(r["change_minor"]), r["baseline_minor"]),
            -abs(r["change_minor"]),
            r["quote_id"],
        )
    )
    return pl.DataFrame(kept, schema=frame.schema)


def _edge_text(edge: Decimal) -> str:
    text = format(edge.normalize(), "f")
    return f"+{text}" if edge > 0 else text


def _band_labels(edges: Sequence[Decimal]) -> list[str]:
    text = [_edge_text(e) for e in edges]
    return [
        f"< {text[0]}%",
        *(f"{a}% to {b}%" for a, b in pairwise(text)),
        f"≥ {text[-1]}%",
    ]


def _sum_decimal(values: Iterable[Decimal]) -> Decimal:
    return sum(values, Decimal(0))


def _level_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _level_sort_key(value: object) -> tuple[Any, ...]:
    """Native order, the null level last (`false` before `true` falls out of `bool`'s order)."""
    return (value is None, value) if value is not None else (True,)


def _group_stats(rows: Sequence[dict[str, Any]]) -> tuple[int, int, int, Decimal]:
    return (
        len(rows),
        sum(r["change_minor"] for r in rows),
        sum(r["baseline_minor"] for r in rows),
        _sum_decimal(r["exposure_years"] for r in rows),
    )


def summarise_dislocation(frame: pl.DataFrame, spec: DislocationSpec) -> DislocationRun:
    """Fold the per-policy frame into the run's summary (03 §4.6; RL-1402 S3-S5)."""
    rows = list(frame.iter_rows(named=True))
    compared = list(_compared(frame).iter_rows(named=True))
    banded = [r for r in compared if r["baseline_minor"] > 0]

    # Totals: integer sums over the compared set.
    base_total = int(sum(r["baseline_minor"] for r in compared))
    cand_total = int(sum(r["candidate_minor"] for r in compared))
    totals = DislocationTotals(
        baseline_premium_minor=base_total,
        candidate_premium_minor=cand_total,
        change_pct=_pct(cand_total - base_total, base_total),
    )

    # Outcomes: each policy once.
    errored = [r for r in rows if "error" in (r["baseline_outcome"], r["candidate_outcome"])]
    pair = [(r["baseline_outcome"], r["candidate_outcome"]) for r in rows]
    outcomes = DislocationOutcomes(
        quoted_both=len(compared),
        quoted_to_declined=sum(p == ("quoted", "declined") for p in pair),
        declined_to_quoted=sum(p == ("declined", "quoted") for p in pair),
        declined_both=sum(p == ("declined", "declined") for p in pair),
        error=len(errored),
        zero_baseline=sum(r["baseline_minor"] == 0 for r in compared),
        negative_baseline=sum(r["baseline_minor"] < 0 for r in compared),
    )

    # Errors: one tally per code, under the baseline's code where that pass errored.
    by_code: dict[str, list[str]] = {}
    for r in errored:
        code = (
            r["baseline_error_code"]
            if r["baseline_outcome"] == "error"
            else r["candidate_error_code"]
        )
        by_code.setdefault(code, []).append(r["quote_id"])
    errors = [
        ErrorTally(
            code=code,
            count=len(ids),
            sample=[ErrorSample(quote_id=i) for i in sorted(ids)[:_SAMPLE_SIZE]],
        )
        for code, ids in sorted(by_code.items())
    ]

    # Bands over the banded set, half-open [lo, hi); an edge belongs to the band above it.
    edges = [Fraction(str(edge)) for edge in spec.band_edges_pct]
    labels = _band_labels(spec.band_edges_pct)
    members: list[list[dict[str, Any]]] = [[] for _ in labels]
    for r in banded:
        pct = Fraction(r["change_minor"], r["baseline_minor"]) * 100
        members[sum(pct >= e for e in edges)].append(r)
    banded_exposure = _sum_decimal(r["exposure_years"] for r in banded)
    distribution = []
    for label, group in zip(labels, members, strict=True):
        n, change, baseline, exposure = _group_stats(group)
        distribution.append(
            DislocationBand(
                band=label,
                policies=n,
                exposure_share=_share(exposure, banded_exposure),
                mean_change_pct=_pct(change, baseline),
            )
        )

    # Segments over the compared set: native level order, the null level last.
    compared_exposure = _sum_decimal(r["exposure_years"] for r in compared)
    by_segment: list[SegmentSlice] = []
    for factor in spec.segments:
        levels = {r[factor] for r in compared}
        for level in sorted(levels, key=_level_sort_key):
            n, change, baseline, exposure = _group_stats(
                [r for r in compared if r[factor] == level]
            )
            by_segment.append(
                SegmentSlice(
                    factor=factor,
                    level=_level_text(level),
                    policies=n,
                    mean_change_pct=_pct(change, baseline),
                    exposure_share=_share(exposure, compared_exposure),
                )
            )

    # Rungs: the change of the compared policies each rung originates, over Σ baseline.
    by_ladder_rung = [
        RungContribution(
            rung=rung,
            contribution_pct=_pct(
                sum(r["change_minor"] for r in compared if r["origin_rung"] == rung), base_total
            ),
        )
        for rung in RUNG_ORDER
        if any(r["origin_rung"] == rung for r in compared)
    ]

    total_exposure = _sum_decimal(r["exposure_years"] for r in rows)
    return DislocationRun(
        baseline_ref=spec.baseline_ref,
        candidate_ref=spec.candidate_ref,
        portfolio_dataset_version_id=spec.portfolio_dataset_version_id,
        policy_count=len(rows),
        exposure_years=total_exposure.quantize(Decimal("0.000001"), ROUND_HALF_EVEN),
        totals=totals,
        outcomes=outcomes,
        distribution=distribution,
        by_segment=by_segment,
        by_ladder_rung=by_ladder_rung,
        errors=errors,
    )


def dislocate(
    baseline: CompiledBundle,
    candidate: CompiledBundle,
    portfolio: pl.LazyFrame,
    spec: DislocationSpec,
) -> DislocationRun:
    """Both passes, then the summary (RL-1402 S1)."""
    return summarise_dislocation(dislocation_frame(baseline, candidate, portfolio, spec), spec)


# ---------------------------------------------------------------------------
# Attribution (03 §4.6, §5.2; FR-266, FR-1397, FR-1398, FR-1399). WK-673 Slice 3, PL-1452,
# RL-1449, RL-1451. Subset bundles are in-memory and discarded when `attribute` returns; every
# figure is a Python `int` taken from the `payable_premium` rung (FR-1397).
# ---------------------------------------------------------------------------

_MAX_SHAPLEY_GROUPS: Final = 6
_ORDERS_SAMPLED: Final = 2  # DP-S3-5: the declared order and its reverse
_PIN_KINDS: Final[tuple[str, ...]] = (
    "rate_tables",
    "models",
    "reference_tables",
    "custom_objectives",
)
_ATTRIBUTION_FAILED: Final = "ATTRIBUTION_RECONCILIATION_FAILED"


class AttributionError(ValueError):
    """A refusal of `derive_changes` or `attribute`, carrying the code the platform maps:
    `VALIDATION_FAILED`, `BUNDLE_COMPILE_FAILED` or `ATTRIBUTION_RECONCILIATION_FAILED`."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class _Change:
    """One derived change and the payload its substitution needs."""

    delta: BundleDelta
    step_id: str | None = None
    old_step: RatingStepBase | None = None  # the baseline's step (changed or removed)
    new_step: RatingStepBase | None = None  # the candidate's step (added or changed)
    pin: tuple[str, ArtifactRef, bool] | None = None  # (pin list, ref, added) of a `pin` change
    fields: tuple[InterfaceDelta, ...] = ()  # input-contract deltas this change carries
    outputs: tuple[InterfaceDelta, ...] = ()  # output deltas this change carries

    @property
    def id(self) -> str:
        return self.delta.id

    def step(self) -> RatingStepBase | None:
        """The step as the side that declares it holds it (the candidate's, else the baseline's)."""
        return self.new_step or self.old_step


@dataclass(frozen=True)
class _Derivation:
    baseline: RatingAlgorithm
    candidate: RatingAlgorithm
    changes: tuple[_Change, ...]


def _as_names(value: str | list[str]) -> list[str]:
    return [value] if isinstance(value, str) else list(value)


def _step_ref(step: RatingStepBase) -> tuple[str, ArtifactRef] | None:
    """The artifact a `table`, `lookup` or `model_call` step names, with its pin list."""
    if isinstance(step, RatingTableStep):
        return "rate_tables", step.rate_table_ref
    if isinstance(step, RatingLookupStep):
        return "reference_tables", step.reference_table_ref
    if isinstance(step, RatingModelCallStep):
        ref = step.model_ref or step.peril_structure_ref
        assert ref is not None  # exactly one is set (FR-222)
        return "models", ref
    return None


async def _resolve_algorithm(version: RatingVersion, resolver: ArtifactResolver) -> RatingAlgorithm:
    if version.algorithm_ref is None:
        raise AttributionError("VALIDATION_FAILED", "a rating version has no algorithm_ref")
    return RatingAlgorithm.model_validate((await resolver.resolve(version.algorithm_ref)).payload)


def _render(value: object) -> str:
    if isinstance(value, dict | list):
        return json.dumps(value, sort_keys=True, default=str)
    return str(value)


async def _derive(
    baseline: RatingVersion, candidate: RatingVersion, resolver: ArtifactResolver
) -> _Derivation:
    """FR-1399 with RL-1449 T2 and RL-1451 P6: the changes, numbered c1, c2, … in derived order."""
    if baseline.model_reference_mode != candidate.model_reference_mode:
        raise AttributionError(
            "VALIDATION_FAILED",
            "the baseline and the candidate differ in model_reference_mode, which no derived "
            "change can carry",
        )
    base_alg = await _resolve_algorithm(baseline, resolver)
    cand_alg = await _resolve_algorithm(candidate, resolver)
    diff = diff_algorithms(base_alg, cand_alg)
    base_steps = {s.step_id: s for s in base_alg.steps}
    cand_steps = {s.step_id: s for s in cand_alg.steps}

    fields_by_step: dict[str, list[Any]] = {}
    for change in diff.changed_steps:
        fields_by_step.setdefault(change.step_id, []).append(change)
    drafts: list[_Change] = []
    for step_id in sorted({*diff.added_steps, *diff.removed_steps, *fields_by_step}):
        if step_id in diff.added_steps:
            kind: DeltaKind = "step_added"
            text = f"{step_id}: step added"
            old, new = None, cand_steps[step_id]
        elif step_id in diff.removed_steps:
            kind = "step_removed"
            text = f"{step_id}: step removed"
            old, new = base_steps[step_id], None
        else:
            changed = fields_by_step[step_id]
            only_ref = {c.field for c in changed} <= {"rate_table_ref", "reference_table_ref"}
            kind = "table_repointed" if only_ref else "step_changed"
            text = f"{step_id}: " + "; ".join(
                f"{c.field} {_render(c.before)} → {_render(c.after)}" for c in changed
            )
            old, new = base_steps[step_id], cand_steps[step_id]
        drafts.append(
            _Change(
                BundleDelta(id="", kind=kind, description=text), step_id, old_step=old, new_step=new
            )
        )

    # Pin differences no step change accounts for are their own changes (FR-1399).
    step_refs = {
        ref
        for c in drafts
        for s in (c.old_step, c.new_step)
        if s is not None and (named := _step_ref(s)) is not None
        for ref in (named[1],)
    }
    pin_changes: list[_Change] = []
    if baseline.pins is not None and candidate.pins is not None:
        for name in _PIN_KINDS:
            before, after = getattr(baseline.pins, name), getattr(candidate.pins, name)
            for ref in before:
                if ref not in after and ref not in step_refs:
                    pin_changes.append(_pin_change(name, ref, added=False))
            for ref in after:
                if ref not in before and ref not in step_refs:
                    pin_changes.append(_pin_change(name, ref, added=True))
    pin_changes.sort(key=lambda c: (str(c.pin[1]) if c.pin else "", c.delta.description))

    # A contract or output difference joins the one change whose step reads or writes it.
    def attach(
        deltas: Sequence[InterfaceDelta], reads: Callable[[RatingStepBase, str], bool]
    ) -> tuple[dict[int, list[InterfaceDelta]], list[InterfaceDelta]]:
        joined: dict[int, list[InterfaceDelta]] = {}
        own: list[InterfaceDelta] = []
        for d in deltas:
            use_new = d.change != "removed"
            readers = [
                i
                for i, c in enumerate(drafts)
                if (s := (c.new_step if use_new else c.old_step)) is not None and reads(s, d.name)
            ]
            if len(readers) == 1:
                joined.setdefault(readers[0], []).append(d)
            else:
                own.append(d)
        return joined, own

    joined_in, own_in = attach(
        diff.input_contract_deltas,
        lambda s, n: isinstance(s, RatingInputStep) and s.input_name == n,
    )
    joined_out, own_out = attach(
        diff.output_deltas,
        lambda s, n: isinstance(s, RatingOutputStep) and s.output_name == n,
    )
    steps = [
        replace(
            c,
            fields=tuple(joined_in.get(i, ())),
            outputs=tuple(joined_out.get(i, ())),
        )
        for i, c in enumerate(drafts)
    ]
    own = [
        _Change(
            BundleDelta(id="", kind="input_field", description=f"field {d.name} {d.change}"),
            fields=(d,),
        )
        for d in sorted(own_in, key=lambda d: d.name)
    ] + [
        _Change(
            BundleDelta(id="", kind="output", description=f"output {d.name} {d.change}"),
            outputs=(d,),
        )
        for d in sorted(own_out, key=lambda d: d.name)
    ]
    numbered = tuple(
        replace(c, delta=c.delta.model_copy(update={"id": f"c{n}"}))
        for n, c in enumerate([*steps, *pin_changes, *own], start=1)
    )
    return _Derivation(base_alg, cand_alg, numbered)


def _pin_change(name: str, ref: ArtifactRef, *, added: bool) -> _Change:
    word = "added" if added else "removed"
    return _Change(
        BundleDelta(id="", kind="pin", description=f"{name} pin {ref} {word}"),
        pin=(name, ref, added),
    )


async def derive_changes(
    baseline: RatingVersion, candidate: RatingVersion, resolver: ArtifactResolver
) -> list[BundleDelta]:
    """The declared changes between two Rating Versions (FR-1399, RL-1449 T2)."""
    return [c.delta for c in (await _derive(baseline, candidate, resolver)).changes]


# --- groups, dependence, subset construction ---------------------------------------------------

_Group = tuple[str, tuple[_Change, ...]]
_APPLIED: Final = {"step_added": "added", "step_removed": "removed"}  # else "changed"


def _check_groups(changes: Sequence[_Change], groups: Sequence[ChangeGroup] | None) -> list[_Group]:
    """No groups: one group per change, named by its id. Else a partition of the derived list."""
    by_id = {c.id: c for c in changes}
    if groups is None:
        return [(c.id, (c,)) for c in changes]
    seen: dict[str, int] = {}
    unknown: list[str] = []
    for group in groups:
        for cid in group.changes:
            seen[cid] = seen.get(cid, 0) + 1
            if cid not in by_id:
                unknown.append(cid)
    left_out = [c.id for c in changes if c.id not in seen]
    twice = sorted(cid for cid, n in seen.items() if n > 1)
    if left_out or twice or unknown:
        parts = []
        if left_out:
            parts.append("left out: " + ", ".join(left_out))
        if twice:
            parts.append("placed twice: " + ", ".join(twice))
        if unknown:
            parts.append("not derived changes: " + ", ".join(sorted(set(unknown))))
        raise AttributionError(
            "VALIDATION_FAILED",
            "change groups must partition the derived changes exactly (" + "; ".join(parts) + ")",
        )
    return [(g.name, tuple(by_id[cid] for cid in g.changes)) for g in groups]


def _merged(
    base: Sequence[Any], cand: Sequence[Any], key: Callable[[Any], str], applied: Mapping[str, str]
) -> list[Any]:
    """The baseline's list with each applied difference substituted: a removal dropped, a change
    taken from the candidate in place, an addition appended in the candidate's order."""
    cand_by = {key(x): x for x in cand}
    out = [
        cand_by[key(x)] if applied.get(key(x)) == "changed" else x
        for x in base
        if applied.get(key(x)) != "removed"
    ]
    out += [x for x in cand if applied.get(key(x)) == "added"]
    return out


def _subset_algorithm(
    derivation: _Derivation, members: Sequence[_Change], *, every_change: bool
) -> RatingAlgorithm:
    """RL-1449 DP-1 (c): the baseline with each member's step, contract and output differences
    applied, so no members is the baseline and every change the candidate (T3)."""
    base, cand = derivation.baseline, derivation.candidate
    if not members:
        return base
    if every_change:
        return cand
    steps_applied = {
        c.step_id: _APPLIED.get(c.delta.kind, "changed") for c in members if c.step_id is not None
    }
    fields = {d.name: d.change for c in members for d in c.fields}
    outputs = {d.name: d.change for c in members for d in c.outputs}
    return base.model_copy(
        update={
            "steps": _merged(base.steps, cand.steps, lambda s: s.step_id, steps_applied),
            "input_contract": _merged(
                base.input_contract, cand.input_contract, lambda f: f.name, fields
            ),
            "outputs": _merged(base.outputs, cand.outputs, lambda o: o.name, outputs),
        }
    )


def _subset_pins(
    baseline: Pins,
    candidate: Pins,
    algorithm: RatingAlgorithm,
    members: Sequence[_Change],
    *,
    every_change: bool,
) -> Pins:
    """The baseline's pins, with a pin the candidate dropped removed once no step in the subset
    names it, each ref a subset step names added, and the `pin` changes in the subset applied."""
    if not members:
        return baseline
    if every_change:
        return candidate
    needed: dict[str, list[ArtifactRef]] = {name: [] for name in _PIN_KINDS}
    for step in algorithm.steps:
        if (named := _step_ref(step)) is not None:
            needed[named[0]].append(named[1])
    pin_removed = {(c.pin[0], c.pin[1]) for c in members if c.pin and not c.pin[2]}
    pin_added = {(c.pin[0], c.pin[1]) for c in members if c.pin and c.pin[2]}
    lists: dict[str, list[ArtifactRef]] = {}
    for name in _PIN_KINDS:
        before, after = getattr(baseline, name), getattr(candidate, name)
        kept = [
            ref
            for ref in before
            if (name, ref) not in pin_removed and (ref in after or ref in needed[name])
        ]
        extra = [ref for ref in needed[name] if ref not in kept]
        extra += sorted((r for n, r in pin_added if n == name and r not in kept), key=str)
        lists[name] = [*kept, *dict.fromkeys(extra)]
    return Pins(**lists)


class _SubsetResolver:
    """Serves one synthetic algorithm ref; every other ref goes to the wrapped resolver."""

    def __init__(
        self, inner: ArtifactResolver, ref: ArtifactRef, payload: dict[str, Any], status: str
    ) -> None:
        self._inner, self._ref, self._payload, self._status = inner, ref, payload, status

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        if ref == self._ref:
            return ResolvedArtifact(status=self._status, payload=self._payload)
        return await self._inner.resolve(ref)


def _check_dependence(derivation: _Derivation, groups: Sequence[_Group]) -> None:
    """RL-1449 T1: refuse, naming each dependent pair, a group that is not self-contained."""
    changes = derivation.changes
    pairs: set[tuple[str, str]] = set()
    base_steps = list(derivation.baseline.steps)
    for _, members in groups:
        ids = {c.id for c in members}
        applied = {
            c.step_id: _APPLIED.get(c.delta.kind, "changed")
            for c in members
            if c.step_id is not None
        }
        steps = _merged(base_steps, list(derivation.candidate.steps), lambda s: s.step_id, applied)
        produced = {n for s in steps for n in _as_names(s.produces)}
        for step in steps:
            for name in _as_names(step.consumes):
                if name in produced:
                    continue
                consumer = next((c for c in changes if c.step_id == step.step_id), None)
                producer = next(
                    (
                        c
                        for c in changes
                        if c.new_step is not None and name in _as_names(c.new_step.produces)
                    ),
                    None,
                ) or next(
                    (
                        c
                        for c in changes
                        if c.old_step is not None and name in _as_names(c.old_step.produces)
                    ),
                    None,
                )
                if consumer is not None and producer is not None:
                    pairs.add((consumer.id, producer.id))
        for c in members:
            step = c.step()
            if step is None:
                continue
            for other in changes:
                if other.id in ids:
                    continue
                if isinstance(step, RatingInputStep) and any(
                    d.name == step.input_name for d in other.fields
                ):
                    pairs.add((c.id, other.id))
                if isinstance(step, RatingOutputStep) and any(
                    d.name == step.output_name for d in other.outputs
                ):
                    pairs.add((c.id, other.id))
    if pairs:
        listed = ", ".join(f"({a}, {b})" for a, b in sorted(pairs))
        raise AttributionError(
            "VALIDATION_FAILED",
            f"dependent changes must share a group: {listed} (the first of each pair depends on "
            "the second); group them",
        )


# --- Shapley, allocation, reconciliation -------------------------------------------------------


def _shapley_numerators(v: Mapping[int, int], k: int) -> list[int]:
    """p_i = sum over S not holding i of |S|!(k-|S|-1)! (v[S|i] - v[S]), subsets as bitmasks.
    The Shapley value of i is p_i / k!, and the sum of p_i = k!(v[N] - v[0])."""
    weights = [factorial(s) * factorial(k - s - 1) for s in range(k)]
    out = [0] * k
    for mask, base in v.items():
        size = mask.bit_count()
        for i in range(k):
            if not mask >> i & 1:
                out[i] += weights[size] * (v[mask | 1 << i] - base)
    return out


def _allocate(numerators: Sequence[int], k: int) -> list[int]:
    """Integer parts of p_i / k! by largest remainder: floors toward -∞, remainders in [0, k!),
    the leftover units to the largest remainders, ties in declared (index) order."""
    scale = factorial(k)
    floors = [p // scale for p in numerators]
    remainders = [p - f * scale for p, f in zip(numerators, floors, strict=True)]
    leftover = sum(numerators) // scale - sum(floors)
    ranked = sorted(range(len(numerators)), key=lambda i: (-remainders[i], i))
    parts = floors[:]
    for i in ranked[:leftover]:
        parts[i] += 1
    return parts


def _residual(total: int, isolated: Sequence[int]) -> int:
    """The interaction residual: total - sum of isolated (FR-266)."""
    return total - sum(isolated)


def _reconcile(
    label: str, parts: Sequence[int] | None, total: int, isolated: Sequence[int], residual: int
) -> None:
    """FR-1397: the parts sum to the total, and the isolated figures plus the residual do too."""
    if parts is not None and sum(parts) != total:
        raise AttributionError(
            _ATTRIBUTION_FAILED,
            f"attribution does not reconcile for {label}: the Shapley parts sum to "
            f"{sum(parts)} minor units, not the total change {total}",
        )
    if sum(isolated) + residual != total:
        raise AttributionError(
            _ATTRIBUTION_FAILED,
            f"attribution does not reconcile for {label}: the isolated figures plus the "
            f"residual sum to {sum(isolated) + residual} minor units, not the total change {total}",
        )


def estimate_attribution_ratings(k: int, policies: int, *, grouped: bool) -> int:
    """The ratings a run performs: 2^k * policies, or above k = 6 (3k - 2) * policies (n = 2)."""
    if grouped and k > _MAX_SHAPLEY_GROUPS:
        raise ValueError(f"change groups are at most {_MAX_SHAPLEY_GROUPS}, not {k}")
    masks = 2**k if k <= _MAX_SHAPLEY_GROUPS else 3 * k - 2
    return masks * policies


def _ratio_text(numerator: int, denominator: int) -> Decimal | None:
    """The exact ratio rounded once to 6 places, half-even; null when the denominator is 0."""
    if denominator == 0:
        return None
    scaled = round(Fraction(numerator, denominator) * 10**_SHARE_PLACES)
    return Decimal(scaled).scaleb(-_SHARE_PLACES)


def _masks_to_rate(k: int) -> list[int]:
    """All 2^k subsets for k ≤ 6; above, ∅, N, the singletons and the declared and reverse
    prefixes (3k - 2 in all)."""
    full = (1 << k) - 1
    if k <= _MAX_SHAPLEY_GROUPS:
        return list(range(full + 1))
    wanted = {0, full, *(1 << i for i in range(k))}
    for size in range(2, k):
        wanted.add((1 << size) - 1)  # g1..gsize
        wanted.add(full ^ ((1 << (k - size)) - 1))  # the last `size` groups
    return sorted(wanted)


def _members(groups: Sequence[_Group], mask: int) -> list[_Change]:
    return [c for i, (_, members) in enumerate(groups) if mask >> i & 1 for c in members]


# --- attribute ---------------------------------------------------------------------------------


def _subset_version(
    baseline: RatingVersion, ref: ArtifactRef, algorithm_pins: Pins
) -> RatingVersion:
    """DP-S3-8: an in-memory copy of the baseline whose algorithm is the subset's synthetic ref."""
    return baseline.model_copy(update={"algorithm_ref": ref, "pins": algorithm_pins})


async def attribute(
    baseline: RatingVersion,
    candidate: RatingVersion,
    portfolio: pl.LazyFrame,
    spec: DislocationSpec,
    resolver: ArtifactResolver,
) -> Attribution:
    """Exact Shapley over the declared change groups, allocated to minor units by largest
    remainder, with the isolated and cumulative views and the residual line (FR-266, FR-1397,
    FR-1398). Above 6 ungrouped changes: the order-dependent method with R and a bound on S."""
    read_portfolio(portfolio, segments=spec.segments)  # the frame's refusals come first
    columns = portfolio.collect_schema().names()
    derivation = await _derive(baseline, candidate, resolver)
    changes = derivation.changes
    groups = _check_groups(changes, spec.change_groups)
    _check_dependence(derivation, groups)
    k = len(groups)
    full = (1 << k) - 1
    shapley = k <= _MAX_SHAPLEY_GROUPS
    masks = _masks_to_rate(k)
    assert baseline.algorithm_ref is not None  # _derive resolved it
    assert baseline.pins is not None
    assert candidate.pins is not None
    # The baseline's status only, not DP-S3-8 (a)'s "lower of the two": `rating_algorithm` is
    # exempt from the maturity floor (RL-859), so the status cannot reach a check. If
    # `test_rating_algorithm_row_has_no_status_column` fires, DP-S3-8 is live again: revisit here.
    status = (await resolver.resolve(baseline.algorithm_ref)).status

    # Compile every subset before rating any: a subset that does not compile fails the run.
    mask_hash: dict[int, str] = {}
    compiled: dict[str, tuple[CompiledBundle, ArtifactRef]] = {}
    for mask in masks:
        members = _members(groups, mask)
        algorithm = _subset_algorithm(derivation, members, every_change=mask == full)
        pins = _subset_pins(
            baseline.pins, candidate.pins, algorithm, members, every_change=mask == full
        )
        ref = ArtifactRef(
            type="rating_algorithm",
            slug=f"{baseline.algorithm_ref.slug}-subset-{mask:0{k}b}",
            version=1,
        )
        subset_resolver = _SubsetResolver(resolver, ref, algorithm.model_dump(mode="json"), status)
        try:
            bundle = await compile_bundle(_subset_version(baseline, ref, pins), subset_resolver)
        except ValueError as exc:  # `CodedError` and a model validation error are both ValueErrors
            ids = ", ".join(c.id for c in members) or "no changes"
            raise AttributionError(
                "BUNDLE_COMPILE_FAILED",
                f"the subset bundle for changes [{ids}] did not compile: {exc}",
            ) from exc
        mask_hash[mask] = bundle.content_hash
        if bundle.content_hash not in compiled:
            compiled[bundle.content_hash] = (load_bundle(bundle), ref)

    rated = {
        h: _score_pass(bundle, portfolio, columns, spec, ref)
        for h, (bundle, ref) in compiled.items()
    }
    values = {mask: rated[mask_hash[mask]] for mask in masks}

    compared = sorted(
        q
        for q, row in values[0].items()
        if row["minor"] is not None and values[full][q]["minor"] is not None
    )
    for q in compared:  # DP-S3-7 (a): a v(S) never assumed, a policy never dropped
        for mask in masks:
            if values[mask][q]["minor"] is None:
                ids = ", ".join(c.id for c in _members(groups, mask)) or "no changes"
                raise AttributionError(
                    _ATTRIBUTION_FAILED,
                    f"policy {q} is quoted in the baseline and the candidate but has no premium "
                    f"under the subset bundle for changes [{ids}]",
                )

    isolated_sum = [0] * k
    cumulative_sum = [0] * k
    reverse_sum = [0] * k
    part_sum = [0] * k
    baseline_total = total_change = 0
    reverse_masks = [full ^ ((1 << i) - 1) for i in range(k + 1)]  # the last k-i groups
    for q in compared:
        v = {mask: int(values[mask][q]["minor"]) for mask in masks}
        total = v[full] - v[0]
        isolated = [v[1 << i] - v[0] for i in range(k)]
        cumulative = [v[(1 << (i + 1)) - 1] - v[(1 << i) - 1] for i in range(k)]
        parts = _allocate(_shapley_numerators(v, k), k) if shapley else None
        _reconcile(q, parts, total, isolated, _residual(total, isolated))
        baseline_total += v[0]
        total_change += total
        for i in range(k):
            isolated_sum[i] += isolated[i]
            cumulative_sum[i] += cumulative[i]
            reverse_sum[i] += v[reverse_masks[i]] - v[reverse_masks[i + 1]]
            if parts is not None:
                part_sum[i] += parts[i]
    residual = _residual(total_change, isolated_sum)
    _reconcile("the portfolio", part_sum if shapley else None, total_change, isolated_sum, residual)

    items = [
        AttributionItem(
            group=name,
            shapley_minor=part_sum[i] if shapley else None,
            isolated_minor=isolated_sum[i],
            cumulative_minor=cumulative_sum[i],
            mean_change_pct=_pct(part_sum[i] if shapley else isolated_sum[i], baseline_total),
            cumulative_change_pct=_pct(cumulative_sum[i], baseline_total),
        )
        for i, (name, _) in enumerate(groups)
    ]
    scale = sum(abs(x) for x in isolated_sum)  # D = sum of |isolated| (RS-1201)
    summary = AttributionSummary(
        method="shapley" if shapley else "order_dependent",
        total_change_minor=total_change,
        residual_minor=residual,
        order_sensitivity_lower_bound=(
            None
            if shapley
            else _ratio_text(
                max(
                    (abs(r - c) for r, c in zip(reverse_sum, cumulative_sum, strict=True)),
                    default=0,
                ),
                scale,
            )
        ),
        residual_share=None if shapley else _ratio_text(abs(residual), scale),
        orders_sampled=None if shapley else _ORDERS_SAMPLED,
        subset_bundle_count=len(compiled),
        subset_bundle_hashes=sorted(compiled),
        subset_valuation="rerate",
        replay_fell_back=False,
    )
    return Attribution(
        derived_changes=[c.delta for c in changes],
        change_groups=[
            ChangeGroup(name=g.name, changes=list(g.changes)) for g in (spec.change_groups or [])
        ],
        attribution=items,
        attribution_summary=summary,
    )
