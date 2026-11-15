"""Scoring a fitted GLM or EBM from its artifact alone (`02` FR-193/140, ADR-705).

The point of this module is what it does **not** import. `glum` fits and `interpret`
fits; nothing here needs either. A GLM is a set of named coefficients, and scoring is
rebuilding the design columns those names describe and taking a dot product; an EBM is
its additive lookup tables, and scoring is the lookups themselves — both things a
process that never ran the fitting library can do, which is the whole of ADR-705.

The term naming is the contract between `glm._design` and this module: a categorical
contributes `slug[level]` for every level except the base, and a continuous factor
contributes `slug`. A term this module cannot parse is an error rather than a zero,
because a coefficient silently dropped is a prediction that looks fine and is wrong.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from statistics import NormalDist
from typing import Any
from uuid import UUID

import numpy as np
import numpy.typing as npt
import polars as pl

from model_schema import (
    Banding,
    Coefficient,
    EbmFitResult,
    EbmNumericBins,
    Factor,
    FactorType,
    FitResult,
    GbmFitResult,
    GlmFitResult,
    GlmSpec,
    Grouping,
    ModelSpec,
    UnseenLevelBehaviour,
)
from pricing_core.modelling.factors import (
    CROSS_SEPARATOR,
    resolve_factor_columns,
    resolve_factors,
)

__all__ = [
    "ALL_ROWS_UNSEEN_TEXT",
    "AllRowsUnseenError",
    "GlmRowPlan",
    "PredictionError",
    "UnseenLevelExclusion",
    "check_term_domains",
    "detect_quantile_crossing",
    "drop_unseen_level_rows",
    "fitted_levels",
    "linear_predictor",
    "linear_predictor_row",
    "predict_ebm",
    "predict_glm",
    "predict_glm_interval",
    "predict_glm_row",
    "score_fitted",
    "unseen_level_mask",
]

#: `slug[level]` — the shape `glm._design` writes for a categorical dummy.
_DUMMY = re.compile(r"^(?P<slug>.+)\[(?P<level>.*)\]$")


class PredictionError(RuntimeError):
    """A model that cannot be scored against this frame.

    Distinct from a fit error: the model is fine, the data it was pointed at is not.
    """

    def __init__(self, code: str, message: str, *, terms: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.code = code
        self.terms = tuple(terms)


#: The sentence for a partition every row of which is excluded (FR-2143), built from a partition
#: name and a count only. The exception and a handler's stored detail both format it; neither
#: stores the exception's own text.
ALL_ROWS_UNSEEN_TEXT = (
    "every one of the {count} {partition} rows carries a level that the fit has no relativity "
    "for, on a factor that does not declare “map to base”, so no row is left to measure. "
    "Declare “map to base” on that factor, or re-split the data."
)


class AllRowsUnseenError(PredictionError):
    """Every row of a partition carries a level the fit has no relativity for, on a Factor that does
    not declare `map_to_base` (FR-2143): excluding them leaves nothing to measure.

    A diagnostics read or a backtest raises this rather than report a zero-row partition. It carries
    the partition's name and a COUNT as attributes; a handler builds the stored detail from those
    with `ALL_ROWS_UNSEEN_TEXT` and never from the exception's own text.
    """

    def __init__(self, *, partition: str, rows: int) -> None:
        # Keyword-only: a positional string first argument would read, to the repository's
        # error-code scan, as an error code.
        super().__init__(
            "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED",
            ALL_ROWS_UNSEEN_TEXT.format(count=rows, partition=partition),
        )
        self.partition = partition
        self.count = rows


def _inverse_link(eta: npt.NDArray[np.float64], link: str) -> npt.NDArray[np.float64]:
    """`g⁻¹`, the only place the link is inverted.

    Written out rather than taken from the fitting library so that scoring and fitting
    cannot drift apart — and so that a reader can check the arithmetic against the spec
    without installing `glum`.
    """
    if link == "log":
        return np.exp(eta)
    if link == "identity":
        return eta
    if link == "logit":
        return 1.0 / (1.0 + np.exp(-eta))
    if link == "inverse":
        with np.errstate(divide="ignore"):
            return 1.0 / eta
    raise PredictionError(
        "MODEL_LINK_UNSUPPORTED",
        f"link {link!r} has no inverse in this module. A prediction cannot be produced "
        "from a link the scorer does not implement, and guessing would be a price.",
    )


def _term_vectors(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding] | None,
    groupings: Mapping[UUID, Grouping] | None,
) -> Iterator[tuple[Coefficient, npt.NDArray[np.float64]]]:
    """One column of `X` per coefficient, **in coefficient order**, intercept included.

    Extracted so that `linear_predictor` and `predict_glm_interval` cannot build different
    design matrices from the same model: `η̂` and `x'Vx` are the centre and the width of one
    interval, and a term resolved one way for the first and another way for the second
    produces a width that does not belong to the centre it is drawn around.

    A generator rather than a matrix because the accumulating caller is the hot one — the
    backtest scores the full dataset, and materialising `n x p` there would be hundreds of
    megabytes to compute a dot product that needs one column at a time.
    """
    check_term_domains(fit, factors, bandings=bandings, groupings=groupings)
    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)
    yield from _design_columns(
        fit, matrix.terms, lambda name: matrix.frame[name], data.height, factors
    )


def _level_domain(
    factor: Factor,
    bandings: Mapping[UUID, Banding] | None,
    groupings: Mapping[UUID, Grouping] | None,
) -> frozenset[str] | None:
    """The levels `factor` can produce, or `None` when its domain is open (an IDENTITY or an
    unbanded expression: a level there is the data's, and `_refuse_unproducible_numeric_level`
    holds the numeric case). A pinned artifact the caller did not supply is also `None`:
    `resolve_factor_columns` refuses that, by its own name."""
    if factor.banding_id is not None and factor.type in (
        FactorType.BANDING,
        FactorType.EXPRESSION,
    ):
        banding = (bandings or {}).get(factor.banding_id)
        return None if banding is None else frozenset(banding.levels)
    if factor.type is FactorType.GROUPING and factor.grouping_id is not None:
        grouping = (groupings or {}).get(factor.grouping_id)
        return None if grouping is None else frozenset(grouping.target_levels)
    return None


def check_term_domains(
    fit: GlmFitResult,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> None:
    """Refuse a level indicator its Factor cannot produce (`MODEL_TERM_UNRESOLVED`, FR-193).

    Every `slug[level]` the fit names must be a level that Factor's artifact yields: a Banding's
    labels and null level, a Grouping's target levels, or, for an interaction, each part against
    its operand's domain (checked only when the split count equals the operand count, because a
    level may itself contain the separator). Scoring such a term would give every row an indicator
    of 0, drop its coefficient and move the prediction toward the base level with no error. Reads
    the artifacts only, never a row, so the text names the term and the Factor and no quote value
    (NFR-499).
    """
    by_id = {f.id: f for f in factors}
    by_slug = {f.slug: f for f in factors}
    for coefficient in fit.coefficients:
        match = _DUMMY.match(coefficient.term)
        factor = by_slug.get(match.group("slug")) if match is not None else None
        if match is None or factor is None:
            continue
        level = match.group("level")
        if factor.type is FactorType.INTERACTION:
            operands = [by_id.get(i) for i in factor.operand_factor_ids]
            cells = level.split(CROSS_SEPARATOR)
            if len(cells) != len(operands):
                continue
            unproducible = any(
                (domain := _level_domain(o, bandings, groupings)) is not None
                and cell not in domain
                for o, cell in zip(operands, cells, strict=True)
                if o is not None
            )
        else:
            domain = _level_domain(factor, bandings, groupings)
            unproducible = domain is not None and level not in domain
        if unproducible:
            raise PredictionError(
                "MODEL_TERM_UNRESOLVED",
                f"term {coefficient.term!r} names a level that factor {factor.slug!r} cannot "
                "produce. Scoring with the term at 0 would silently move every prediction "
                "toward the base level.",
                terms=[coefficient.term],
            )


def _numeric_level_producible(level: str, dtype: pl.DataType) -> bool:
    """Whether a column of `dtype` can produce `level` as text: a level on a numeric column must
    survive Polars' own round trip (`level` → dtype → `String`). A non-numeric column produces any
    level. The answer depends on `(level, dtype)` and nothing else."""
    if not dtype.is_numeric():
        return True
    try:
        produced = pl.Series([level]).cast(dtype).cast(pl.String).item()
    except pl.exceptions.PolarsError:
        produced = None
    return bool(produced == level)


def _unproducible_error(term: str, slug: str, dtype: pl.DataType) -> PredictionError:
    return PredictionError(
        "MODEL_TERM_UNRESOLVED",
        f"term {term!r} names a level that factor {slug!r}, resolved as {dtype}, cannot "
        "produce. Scoring with the term at 0 would silently move every prediction "
        "toward the base level.",
        terms=[term],
    )


def _refuse_unproducible_numeric_level(
    term: str, slug: str, level: str, dtype: pl.DataType
) -> None:
    """A level on a numeric column must survive Polars' own round trip (`level` → dtype →
    `String`): `"25-39"` cannot come from an `Int64`, nor `"3"` from a `Float64` (`"3.0"`).
    Only a numeric column pays the test; a correctly fitted dummy never meets one."""
    if not _numeric_level_producible(level, dtype):
        raise _unproducible_error(term, slug, dtype)


def _unseen_error(slug: str, behaviour: UnseenLevelBehaviour | None) -> PredictionError:
    declared = (
        "declares 'error'" if behaviour is UnseenLevelBehaviour.ERROR
        else "declares no unseen-level behaviour"
    )
    return PredictionError(
        "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED",
        f"factor {slug!r} carries a level that the fitted model never saw, and the "
        f"Factor {declared} (FR-131).",
        terms=[slug],
    )


def fitted_levels(fit: GlmFitResult) -> dict[str, frozenset[str]]:
    """Every level the fit saw, per categorical factor slug, base included (`relativities`).

    Driven by the fitted level set and not by the dummies: a factor fitted on one level has
    no dummy at all, and a check keyed to the dummies would never look at it."""
    return {
        slug: frozenset(entry.level for entry in levels)
        for slug, levels in fit.relativities.items()
    }


@dataclass(frozen=True)
class UnseenLevelExclusion:
    """`data` without the rows that carry a level (or cell) the fit has no relativity for, on a
    Factor that does not declare `map_to_base` (FR-2143), and what was removed.

    For evidence (diagnostics, a comparison, a backtest): a quote with such a level is refused,
    and a metric must not score the row as another level. `keep` is the row mask over the original
    frame, so a caller holding another per-row array aligned to it filters it with `take`.
    """

    data: pl.DataFrame
    keep: npt.NDArray[np.bool_]
    excluded: int

    def take(self, array: np.ndarray | None) -> np.ndarray | None:
        """`array` restricted to the kept rows; `None`, or an array not aligned to the original
        frame, is returned as it came (the caller's own length check then refuses it by name)."""
        if array is None or array.shape != self.keep.shape:
            return array
        return array[self.keep]

    def exposure_of_excluded(self, exposure: np.ndarray) -> float:
        """The summed `exposure` (aligned to the original frame) of the removed rows."""
        return float(np.sum(exposure[~self.keep]))


def unseen_level_mask(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> npt.NDArray[np.bool_]:
    """`True` for each row carrying a level of an undeclared Factor that the fit never saw. A null
    is not a level; a `map_to_base` Factor is never flagged (it scores at the base level)."""
    flagged = np.zeros(data.height, dtype=np.bool_)
    seen = fitted_levels(fit)
    behaviours = {f.slug: f.unseen_level_behaviour for f in factors}
    if not seen:
        return flagged
    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)
    for slug, levels in seen.items():
        column = matrix.terms.get(slug)
        if column is None or behaviours.get(slug) is UnseenLevelBehaviour.MAP_TO_BASE:
            continue
        text = matrix.frame[column].cast(pl.String)
        unseen = text.is_not_null() & ~text.is_in(sorted(levels))
        flagged |= unseen.fill_null(False).to_numpy()
    return flagged


def drop_unseen_level_rows(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> UnseenLevelExclusion:
    """Remove the rows `unseen_level_mask` flags; refuse nothing, and count what was removed."""
    keep = ~unseen_level_mask(fit, data, factors, bandings=bandings, groupings=groupings)
    return UnseenLevelExclusion(
        data=data if keep.all() else data.filter(pl.Series(keep)),
        keep=keep,
        excluded=int(keep.size - np.count_nonzero(keep)),
    )


def _refuse_unseen_levels(
    terms: Mapping[str, str],
    column_of: Callable[[str], pl.Series],
    seen: Mapping[str, frozenset[str]],
    behaviours: Mapping[str, UnseenLevelBehaviour | None],
) -> None:
    """Refuse a level the fit never saw, unless its Factor declares `map_to_base`
    (`UNSEEN_LEVEL_BEHAVIOUR_REQUIRED`, FR-131 as the EBM and the GBM apply it).

    An unseen level matches no dummy, so every dummy of its factor is 0 and the row scores at
    the base level. That is the arithmetic `map_to_base` declares, so the declared case needs
    no replacement. Nulls are not levels and are not counted. The text names the factor and
    never the value (NFR-499)."""
    for slug, levels in seen.items():
        column = terms.get(slug)
        if column is None:
            continue
        behaviour = behaviours.get(slug)
        if behaviour is UnseenLevelBehaviour.MAP_TO_BASE:
            # All dummies 0 *is* the base level, so the zero row is the declared result.
            continue
        unseen = [
            value
            for value in column_of(column).cast(pl.String).drop_nulls().unique().to_list()
            if value not in levels
        ]
        if unseen:
            raise _unseen_error(slug, behaviour)


class GlmRowPlan:
    """What a loaded GLM's one-row path derives from the fit and its pinned Factors ONCE, so that a
    quote pays only a set test per categorical value and a lookup per numeric dummy term.

    Built once per scorer (`rating/runtime.py` `_GlmScorer`), never per quote:

    * `checked`: each fitted categorical slug with its fitted level set and declared behaviour,
      in `relativities` order, leaving out a `map_to_base` Factor (it scores at the base level);
    * `terms`: every dummy term parsed to `(term, slug, level)`, in coefficient order;
    * `parsed`: every non-intercept coefficient term parsed to `(slug, level)` or `None`;
    * `verdicts`: whether a column of a given dtype can produce a given level, keyed
      `(slug, level, dtype)`. The dtype in the key is the column's ACTUAL dtype at the call, so one
      scorer fed an `Int64` and then a `Float64` for the same input gets the right verdict each
      time; the cache belongs to this plan, so it cannot cross models.

    The same refusals, in the same order, with the same codes and texts as the vectorised checks
    the frame path keeps.
    """

    __slots__ = ("checked", "parsed", "terms", "verdicts")

    def __init__(self, fit: GlmFitResult, factors: Sequence[Factor]) -> None:
        behaviours = {f.slug: f.unseen_level_behaviour for f in factors}
        self.checked = tuple(
            (slug, levels, behaviours.get(slug))
            for slug, levels in fitted_levels(fit).items()
            if behaviours.get(slug) is not UnseenLevelBehaviour.MAP_TO_BASE
        )
        terms: list[tuple[str, str, str]] = []
        parsed: dict[str, tuple[str, str] | None] = {}
        for coefficient in fit.coefficients:
            if coefficient.term == "intercept":
                continue
            match = _DUMMY.match(coefficient.term)
            if match is None:
                parsed[coefficient.term] = None
                continue
            slug, level = match.group("slug"), match.group("level")
            parsed[coefficient.term] = (slug, level)
            terms.append((coefficient.term, slug, level))
        self.terms = tuple(terms)
        self.parsed = parsed
        self.verdicts: dict[tuple[str, str, pl.DataType], bool] = {}

    def refuse_unproducible_numeric_levels(
        self, terms: Mapping[str, str], column_of: Callable[[str], pl.Series]
    ) -> None:
        """`_refuse_unproducible_numeric_levels` for ONE quote: each column's dtype is read once,
        and the verdict for `(slug, level, dtype)` is looked up, computed only the first time."""
        dtypes: dict[str, pl.DataType] = {}
        for term, slug, level in self.terms:
            column = terms.get(slug)
            if column is None:
                continue
            if column not in dtypes:
                dtypes[column] = column_of(column).dtype
            dtype = dtypes[column]
            key = (slug, level, dtype)
            producible = self.verdicts.get(key)
            if producible is None:
                producible = self.verdicts[key] = _numeric_level_producible(level, dtype)
            if not producible:
                raise _unproducible_error(term, slug, dtype)

    def refuse_unseen_levels(
        self, terms: Mapping[str, str], column_of: Callable[[str], pl.Series]
    ) -> None:
        """`_refuse_unseen_levels` for ONE quote: the quote's value, as text, tested against the
        fitted level set (a null is not a level)."""
        for slug, levels, behaviour in self.checked:
            column = terms.get(slug)
            if column is None:
                continue
            value = column_of(column).cast(pl.String).item()
            if value is not None and value not in levels:
                raise _unseen_error(slug, behaviour)


def _refuse_unproducible_numeric_levels(
    fit: GlmFitResult, terms: Mapping[str, str], column_of: Callable[[str], pl.Series]
) -> None:
    """`_refuse_unproducible_numeric_level` for every dummy term of the fit, in coefficient order:
    each column's dtype is read once, and the check runs once per term. A term whose factor the
    frame does not resolve is left to the walk, which refuses it by name."""
    dtypes: dict[str, pl.DataType] = {}
    for coefficient in fit.coefficients:
        match = _DUMMY.match(coefficient.term)
        if match is None:
            continue
        slug, level = match.group("slug"), match.group("level")
        column = terms.get(slug)
        if column is None:
            continue
        if column not in dtypes:
            dtypes[column] = column_of(column).dtype
        _refuse_unproducible_numeric_level(coefficient.term, slug, level, dtypes[column])


def _design_columns(
    fit: GlmFitResult,
    terms: Mapping[str, str],
    column_of: Callable[[str], pl.Series],
    height: int,
    factors: Sequence[Factor],
    seen: Mapping[str, frozenset[str]] | None = None,
    plan: GlmRowPlan | None = None,
) -> Iterator[tuple[Coefficient, npt.NDArray[np.float64]]]:
    """The coefficient walk `_term_vectors` and `predict_glm_row` share: one column of `X` per
    coefficient, in coefficient order, from whichever resolved columns the caller reads.

    One definition of the term grammar (`_DUMMY`) and of `MODEL_TERM_UNRESOLVED`, so the frame
    path and the one-row path cannot build different designs from one model. The unseen-level
    refusal runs after the numeric-level check, for the same reason, once per call; `seen` is the
    caller's prebuilt `fitted_levels(fit)` when it scores many rows.

    The numeric-level check (`MODEL_TERM_UNRESOLVED`) runs for EVERY dummy term of a column, before
    the unseen-level rule and whatever a Factor declares: a term whose level the column's numeric
    type cannot produce has an indicator of 0 on every row, so a `map_to_base` declaration must not
    turn it into a base price, and the answer must not depend on the order of the coefficients.

    `plan` is the one-row path's per-scorer derivation (`GlmRowPlan`): given one, a one-row call
    does the same two checks, in the same order with the same refusals, from what the plan holds
    instead of re-deriving it. The frame path passes none and keeps the vectorised checks.
    """
    if plan is not None and height == 1:
        plan.refuse_unproducible_numeric_levels(terms, column_of)
        plan.refuse_unseen_levels(terms, column_of)
    else:
        _refuse_unproducible_numeric_levels(fit, terms, column_of)
        _refuse_unseen_levels(
            terms,
            column_of,
            fitted_levels(fit) if seen is None else seen,
            {f.slug: f.unseen_level_behaviour for f in factors},
        )
    #: A factor's levels as text, cast once however many of its dummies there are.
    as_text: dict[str, pl.Series] = {}
    for coefficient in fit.coefficients:
        term = coefficient.term
        if term == "intercept":
            yield coefficient, np.ones(height, dtype=np.float64)
            continue

        if plan is not None and term in plan.parsed:
            parsed = plan.parsed[term]
        else:
            match = _DUMMY.match(term)
            parsed = None if match is None else (match.group("slug"), match.group("level"))
        if parsed is not None:
            slug, level = parsed
            column = terms.get(slug)
            if column is None:
                raise PredictionError(
                    "MODEL_TERM_UNRESOLVED",
                    f"term {term!r} names factor {slug!r}, which this frame does not "
                    "resolve. Scoring with the term dropped would silently move every "
                    "prediction toward the base level.",
                    terms=[term],
                )
            if column not in as_text:
                as_text[column] = column_of(column).cast(pl.String)
            indicator = (as_text[column] == level).cast(pl.Float64)
            yield coefficient, indicator.to_numpy()
            continue

        column = terms.get(term)
        if column is None:
            raise PredictionError(
                "MODEL_TERM_UNRESOLVED",
                f"term {term!r} is neither a level indicator nor a factor this frame "
                "resolves.",
                terms=[term],
            )
        yield coefficient, column_of(column).cast(pl.Float64).to_numpy()


def _offset(
    data: pl.DataFrame, spec: GlmSpec, model_offset: np.ndarray | None = None
) -> npt.NDArray[np.float64] | None:
    """The offset column on the linear-predictor scale, or `None` when the spec has none.

    A known constant per row: it shifts `η̂` and contributes nothing to its variance, which
    is why `predict_glm_interval` adds it to the centre and not to the width.

    `kind="model"` takes the array the backend resolved — pricing-core cannot resolve
    the ref itself, and returning `None` here would score as though no offset were
    declared (FR-116): named, never silent.
    """
    if spec.offset.kind == "model":
        if model_offset is None:
            raise PredictionError(
                "MODEL_OFFSET_MISSING",
                "offset kind 'model' requires the resolved offset array (model_offset), "
                "and none was supplied (FR-116).",
            )
        if model_offset.shape != (data.height,):
            raise PredictionError(
                "MODEL_OFFSET_MISSING",
                f"model_offset has {model_offset.shape[0]} rows for {data.height} "
                "data rows (FR-116).",
            )
        if not np.all(np.isfinite(model_offset)):
            raise PredictionError(
                "MODEL_OFFSET_MISSING",
                "model_offset carries non-finite values (FR-116).",
            )
        return np.asarray(model_offset, dtype=np.float64)
    if spec.offset.kind not in {"log_column", "column"}:
        return None
    column = str(spec.offset.column)
    if column not in data.columns:
        raise PredictionError(
            "MODEL_OFFSET_MISSING",
            f"the spec declares an offset on {column!r} and the frame has no such "
            "column. A frequency model scored without its exposure offset returns a "
            "count per unit exposure as though it were a count.",
        )
    values = data[column].cast(pl.Float64).to_numpy()
    if spec.offset.kind == "column":
        return np.asarray(values, dtype=np.float64)
    if np.any(values <= 0):
        raise PredictionError(
            "MODEL_OFFSET_MISSING",
            f"{column!r} has non-positive values and the offset is log(exposure); "
            "such a row contributes no information and must be filtered, not "
            "logged.",
        )
    return np.log(values)


def linear_predictor(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    spec: GlmSpec,
    *,
    model_offset: np.ndarray | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> npt.NDArray[np.float64]:
    """`η = Xβ + offset`, on the scale the link maps from.

    Exposed separately because the diagnostics need `η` for residuals and `μ` for
    everything else, and computing the design twice to get both would double the cost of
    the expensive half.

    `model_offset` is the offset-from-another-model array (FR-116): the referenced
    fitted GLM's linear predictor, resolved by the backend and required when
    `spec.offset.kind == "model"`.
    """
    return _accumulate(
        _term_vectors(fit, data, factors, bandings=bandings, groupings=groupings),
        data.height,
        lambda: _offset(data, spec, model_offset),
    )


def _accumulate(
    vectors: Iterable[tuple[Coefficient, npt.NDArray[np.float64]]],
    height: int,
    offset: Callable[[], npt.NDArray[np.float64] | None],
) -> npt.NDArray[np.float64]:
    """`η = Σ βⱼxⱼ + offset`, in coefficient order — the one place the sum is written.

    The offset is a callable so that it is read **after** the terms, as it always was: a term
    that cannot be resolved is refused before an offset that cannot be read.
    """
    eta = np.zeros(height, dtype=np.float64)
    for coefficient, vector in vectors:
        eta += coefficient.estimate * vector
    offset_values = offset()
    if offset_values is not None:
        eta += offset_values
    return eta


def predict_glm(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    spec: GlmSpec,
    *,
    model_offset: np.ndarray | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> npt.NDArray[np.float64]:
    """`μ`, the expectation, for every row of `data` (FR-193).

    Uncertainty is **not** returned here, and deliberately still is not. FR-194's
    interval needs the covariance matrix, which the fit stores as a blob this signature
    does not take — `predict_glm_interval` is the entry point that does. Every caller that
    only wants `μ` (the diagnostics, the backtest, the comparison, the peril structure)
    keeps a signature that costs one column of the design at a time.

    `model_offset` is the offset-from-another-model array (FR-116), required when
    `spec.offset.kind == "model"`.
    """
    return _inverse_link(
        linear_predictor(
            fit, data, factors, spec,
            model_offset=model_offset, bandings=bandings, groupings=groupings,
        ),
        spec.link,
    )


def _row_frame(row: Mapping[str, Any]) -> pl.DataFrame:
    """The one-row frame of a quote. A non-finite `Decimal` is carried as the float it equals
    (a signaling NaN, which `float()` refuses, as a quiet NaN): `pl.DataFrame` panics (pyo3
    `PanicException`) building a Decimal NaN, where a float NaN is a missing value and reaches
    `apply_banding`'s coded refusal (FD-2043; FR-97)."""
    return pl.DataFrame(
        [
            {
                name: (float("nan") if value.is_nan() else float(value))
                if isinstance(value, Decimal) and not value.is_finite()
                else value
                for name, value in row.items()
            }
        ]
    )


def linear_predictor_row(
    fit: GlmFitResult,
    row: Mapping[str, Any],
    factors: Sequence[Factor],
    spec: GlmSpec,
    *,
    model_offset: np.ndarray | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    seen: Mapping[str, frozenset[str]] | None = None,
    plan: GlmRowPlan | None = None,
) -> npt.NDArray[np.float64]:
    """`linear_predictor` for one quote, as a shape-`(1,)` array, with no frame rebuilt.

    `seen` is `fitted_levels(fit)` built once by a caller that scores many quotes; `plan` is the
    scorer's `GlmRowPlan`, built once, which supplies the per-model checks (and the parsed terms)
    so that a quote does not re-derive them.

    Scoring one row through `linear_predictor` costs a lazy `with_columns` + `collect` in
    `resolve_factors` per call (FD-1797 (filed in D21): ~16.9 ms a quote on a loaded box, 59% of a
    dislocation run). This reads the same resolution (`resolve_factor_columns`), the same
    coefficient walk (`_design_columns`), the same sum (`_accumulate`) and the same offset
    (`_offset`) from the one-row frame `pl.DataFrame([row])` that path builds — it does not
    append the produced columns to it. Every operation is therefore the frame path's, on the
    same values in the same order: the result is bit-identical, which
    `test_glm_scalar_predict.py` holds exactly.
    """
    frame = _row_frame(row)
    resolved = resolve_factor_columns(frame, factors, bandings=bandings, groupings=groupings)
    return _accumulate(
        _design_columns(
            fit, resolved.terms, lambda name: resolved.column(frame, name), 1, factors, seen,
            plan,
        ),
        1,
        lambda: _offset(frame, spec, model_offset),
    )


def predict_glm_row(
    fit: GlmFitResult,
    row: Mapping[str, Any],
    factors: Sequence[Factor],
    spec: GlmSpec,
    *,
    model_offset: np.ndarray | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    seen: Mapping[str, frozenset[str]] | None = None,
    plan: GlmRowPlan | None = None,
) -> float:
    """`μ` for one quote: `predict_glm`'s value for a one-row frame, as a `float` (FR-193).

    The link is inverted by `_inverse_link` on the shape-`(1,)` `η` — never `math.exp`, whose
    last bit can differ from NumPy's.
    """
    eta = linear_predictor_row(
        fit, row, factors, spec, model_offset=model_offset, bandings=bandings,
        groupings=groupings, seen=seen, plan=plan,
    )
    return float(_inverse_link(eta, spec.link)[0])


def predict_glm_interval(
    fit: GlmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    spec: GlmSpec,
    *,
    covariance_bytes: bytes,
    level: float = 0.95,
    model_offset: np.ndarray | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> tuple[
    npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]
]:
    """`μ` and FR-194's interval around it: `(expected, lower, upper)`.

    **What this interval is.** `Var(η̂) = x'Vx`, the sampling variance of the *estimated*
    linear predictor, so `g⁻¹(η̂ ± z·√(x'Vx))` is a confidence interval for `E[Y|x]` — how
    precisely the fit located the mean. It is not a prediction interval for an individual
    outcome, which would add the process variance `φ·V(μ)` the covariance matrix does not
    contain. `model_schema.UncertaintyKind` carries that distinction into the response as
    `confidence_interval_mean`, and `02` FR-194 has the dated note.

    **The offset is in the centre and not in the width.** It is a known constant per row, so
    it shifts `η̂` and contributes no variance — the interval on a frequency prediction is
    the interval on the rate, scaled by exposure, which is what a reader of a per-policy
    expected count wants.

    **The bounds are re-ordered after the link, not before.** `g⁻¹` for `inverse` is
    decreasing, so the transformed endpoints of a symmetric interval on `η` come back
    swapped; `PredictedRow` refuses a reversed pair, and this is where the pair stops being
    reversed.

    Unlike `predict_glm` this materialises the `n x p` design, which is why it is a separate
    entry point rather than a flag: `02` §5.1 scopes `/predict` to "dev/debug scale", and
    the callers that score a whole dataset (backtest, diagnostics, comparison) must keep the
    streaming path.
    """
    if not 0.0 < level < 1.0:
        raise PredictionError(
            "MODEL_INTERVAL_UNAVAILABLE",
            f"a confidence level of {level} is not a probability strictly between 0 and 1.",
        )
    from pricing_core.modelling.glm import decode_covariance

    terms = [coefficient.term for coefficient in fit.coefficients]
    covariance = decode_covariance(covariance_bytes, terms)

    columns: list[npt.NDArray[np.float64]] = []
    beta: list[float] = []
    for coefficient, vector in _term_vectors(
        fit, data, factors, bandings=bandings, groupings=groupings
    ):
        columns.append(vector)
        beta.append(coefficient.estimate)

    design = np.column_stack(columns) if columns else np.zeros((data.height, 0))
    eta = design @ np.asarray(beta, dtype=np.float64)
    offset = _offset(data, spec, model_offset)
    if offset is not None:
        eta = eta + offset

    # `x'Vx` row by row without forming the `n x n` product `X V X'`, which for the 10 000
    # rows this endpoint allows would be 800 MB to read 10 000 numbers off its diagonal.
    variance = np.einsum("ij,jk,ik->i", design, covariance, design)
    # A variance that comes back very slightly negative is floating-point noise on a
    # near-zero quantity, not a negative variance; clipped so it becomes a zero-width
    # interval rather than a NaN bound that would serialise as `null` and read as absent.
    half = NormalDist().inv_cdf(1.0 - (1.0 - level) / 2.0) * np.sqrt(
        np.clip(variance, 0.0, None)
    )

    expected = _inverse_link(eta, spec.link)
    first = _inverse_link(eta - half, spec.link)
    second = _inverse_link(eta + half, spec.link)
    return expected, np.minimum(first, second), np.maximum(first, second)


def predict_ebm(
    fit: EbmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> npt.NDArray[np.float64]:
    """`μ` for an EBM, from its additive lookup tables alone (FR-140, ADR-705).

    No `interpret` import, no spec, no offset, no link inversion: the tables are the
    model, the link is identity, and `μ = intercept + Σ term scores`. The index rule
    is the one the fit recorded: numeric `np.searchsorted(cuts, v, side="right") + 1`
    (slot 0 is the unused base slot — below-range values land in bin 1, above-range
    in the last populated bin, no clamping), categorical by position in `levels` plus
    one. A level the fit never saw has no slot, and inventing one would score it as
    whichever level shares the number — `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` (the
    `gbm._encode` rule, FR-131).
    """
    matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)

    # One slot array per feature, positional against `fit.feature_order` — the same
    # relationship `fit.bins` and `EbmTerm.term_features` use, so a term's lookup can
    # only ever touch the feature it names.
    slots: list[npt.NDArray[np.int64]] = []
    for slug, bins in zip(fit.feature_order, fit.bins, strict=True):
        column = matrix.terms.get(slug)
        if column is None:
            raise PredictionError(
                "MODEL_TERM_UNRESOLVED",
                f"a term names factor {slug!r}, which this frame does not resolve. "
                "Scoring with the term dropped would silently move every prediction "
                "toward the intercept.",
                terms=[slug],
            )
        if isinstance(bins, EbmNumericBins):
            values = matrix.frame[column].cast(pl.Float64).to_numpy()
            # Non-finite values follow `np.searchsorted` semantics exactly — the same
            # rule the fitted estimator applied, so scoring agrees with `interpret`
            # on every input by construction.
            slots.append(
                np.searchsorted(np.asarray(bins.cuts), values, side="right") + 1
            )
        else:
            lookup = {level: i + 1 for i, level in enumerate(bins.levels)}
            text = matrix.frame[column].cast(pl.String)
            unknown = sorted({str(level) for level in text.unique().to_list()} - set(lookup))
            if unknown:
                raise PredictionError(
                    "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED",
                    f"factor {slug!r} carries level {unknown[0]!r} that the fitted "
                    "model never saw (FR-131).",
                    terms=[slug],
                )
            slots.append(text.replace_strict(lookup, return_dtype=pl.Int32).to_numpy())

    eta = np.full(data.height, fit.intercept, dtype=np.float64)
    for term in fit.terms:
        scores = np.asarray(term.scores)
        if len(term.term_features) == 2:
            first, second = term.term_features
            eta += scores[slots[first], slots[second]]
        else:
            (feature,) = term.term_features
            eta += scores[slots[feature]]
    return eta


def score_fitted(
    fit: FitResult,
    spec: ModelSpec,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    model_offset: np.ndarray | None = None,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    booster: bytes | None = None,
) -> npt.NDArray[np.float64]:
    """`μ` for a fitted model of **any** kind, on the mean scale.

    The dispatch is the only thing that separates scoring a GLM from scoring a GBM or an
    EBM, and the callers need it: the comparison (`WF-698` E1, an actuary weighing a
    booster's lift against a GLM's transparency), the peril structure (E4, where each
    peril's models are scored before they are summed), and the backtest (FR-187,
    where every arm is re-measured on data it never saw). It lives here rather than in
    any of them, because a second copy of a dispatch is a second place for the kinds to
    diverge — and a peril priced through the wrong branch is a silently wrong risk
    premium.

    `booster` is required only for a GBM: a GLM's fit result *is* its model, a GBM's is
    a reference to bytes the caller must fetch (ADR-703 keeps that fetch out of this
    package), and an EBM's *is* its model in the strongest sense — the exported lookup
    tables themselves, which `predict_ebm` scores without the fitting stack.

    `model_offset` is forwarded on the GLM arm only (FR-116): a `GbmSpec` or
    `EbmSpec` declaring `kind="model"` is schema-refused, so there is no arm that could
    use it.
    """
    if isinstance(fit, GbmFitResult):
        from pricing_core.modelling.gbm import predict_gbm

        if booster is None:
            raise PredictionError(
                "MODEL_NOT_FITTED",
                "a GBM cannot be scored without its booster bytes: its fit result is a "
                "reference to them, not the model itself",
            )
        return np.asarray(
            predict_gbm(
                fit, booster, data, factors, bandings=bandings, groupings=groupings
            ).to_numpy(),
            dtype=np.float64,
        )
    if isinstance(fit, EbmFitResult):
        return predict_ebm(fit, data, factors, bandings=bandings, groupings=groupings)
    assert isinstance(fit, GlmFitResult)
    assert isinstance(spec, GlmSpec)
    return predict_glm(
        fit, data, factors, spec,
        model_offset=model_offset, bandings=bandings, groupings=groupings,
    )


def detect_quantile_crossing(
    lower: npt.NDArray[np.float64], upper: npt.NDArray[np.float64]
) -> tuple[int, float]:
    """How often, and how badly, a quantile pair contradicts itself (FR-199).

    Returns `(rows_crossing, worst_gap)`. **It reorders nothing** — that is the
    requirement's own word, and the reason this returns numbers rather than a corrected
    pair: a reordered pair still does not describe one distribution, and hiding that is the
    failure mode OQ-574 was decided to avoid.

    Both figures, because either alone misleads. One crossing row in a million is a
    curiosity; one crossing row by a factor of ten is a bound nobody should quote, and a
    count describes them identically.

    `lower == upper` is **not** crossing: the two fits agreeing exactly at a row is
    degenerate, not inverted, and counting it would report a defect on every row where a
    bound is constant — which is what a booster returns for a leaf with one level.
    """
    if lower.shape != upper.shape:
        raise PredictionError(
            "MODEL_INTERVAL_UNAVAILABLE",
            f"the bounds have different lengths ({lower.shape} and {upper.shape}); they "
            "were scored over different row sets, and NumPy would broadcast them into a "
            "confident answer about a comparison nobody made.",
        )
    gaps = lower - upper
    crossing = gaps > 0.0
    return int(crossing.sum()), float(gaps.max()) if bool(crossing.any()) else 0.0
