"""FR-111's weight rule, in one place (SL-1675, 2026-10-12).

A row whose declared weight is exactly 0 carries no information — a non-claimant under
severity's `weight = claim_count`, a zero-exposure row under burning cost's
`weight = exposure` — so it is absent from the fit and from every diagnostic. A negative, null
or non-finite weight is not 0 and is refused, loudly, before any backend sees it: LightGBM
fitted on one silently, XGBoost raised a library error with no platform code and the EBM
named it with an unrelated one.

Every fit and every diagnostic entry point calls this **at its entry, before factor
resolution**, so an excluded row can influence nothing downstream: not the base level `_levels`
picks, the cross-validation folds, the Tweedie profile, the dispersion, GBM or EBM binning,
nor a partition's row count. That is also why the response of an excluded row is never read —
a non-claimant's 0 never reaches the Gamma family.

The rule reads `spec.weight` and nothing else. FR-111's frequency offset is not a weight.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import polars as pl

from model_schema import ModelSpecCommon, ResponseKind

#: The platform error code for a weight column that cannot be fitted on (`02` §5.1).
WEIGHT_INVALID_CODE = "DECLARED_WEIGHT_INVALID"


@dataclass(frozen=True)
class WeightExclusion:
    """`data` without its weight-0 rows, and what was removed.

    `keep` is the boolean row mask over the *original* frame, so a caller holding another
    per-row array aligned to it (FR-116's model offset) filters it with `take`.
    """

    data: pl.DataFrame
    keep: npt.NDArray[np.bool_]
    #: Rows removed for weight 0.
    excluded: int
    #: Rows removed because the response is unknown (FR-111, SL-1543): `None` when the spec
    #: is not a `claim_severity` fit, where the rule does not apply.
    excluded_unknown: int | None = None

    def take(self, array: np.ndarray | None) -> np.ndarray | None:
        """`array` restricted to the kept rows; `None` stays `None`.

        An array that is not aligned to the original frame is returned as it came, so the
        caller's own length check still refuses it by name (`_model_offset`, FR-116) rather
        than numpy raising an index error from here.
        """
        if array is None or array.shape != self.keep.shape:
            return array
        return array[self.keep]


def _weights(data: pl.DataFrame, spec: ModelSpecCommon) -> npt.NDArray[np.float64] | None:
    """The declared weight as floats (a null becomes NaN), or `None` when none is declared.

    A declared column the frame lacks raises Polars' own `ColumnNotFoundError`, exactly as
    each fit's own read of it always did.
    """
    if spec.weight.kind != "column":
        return None
    return data[str(spec.weight.column)].cast(pl.Float64).to_numpy()


def _exclude(
    data: pl.DataFrame, keep: npt.NDArray[np.bool_], spec: ModelSpecCommon
) -> WeightExclusion:
    """`keep` is the weight mask; a `claim_severity` fit also drops its unknown-amount rows.

    FR-111's severity population is `claim_count > 0` and a known amount. A weight-0 row is
    counted as weight-0 and its response is never read; of the rest, a null response is
    unknown and excluded. A known amount that is not positive is left in, for the family's
    response-domain check to refuse — it is not unknown, and is never dropped here.
    """
    zero_weight = int(keep.size - np.count_nonzero(keep))
    unknown: int | None = None
    if spec.response is ResponseKind.CLAIM_SEVERITY and spec.response_column in data.columns:
        null = data[spec.response_column].is_null().to_numpy()
        unknown_rows = keep & null
        unknown = int(np.count_nonzero(unknown_rows))
        keep = keep & ~null
    return WeightExclusion(
        data=data.filter(pl.Series(keep)) if not keep.all() else data,
        keep=keep,
        excluded=zero_weight,
        excluded_unknown=unknown,
    )


def drop_zero_weight_rows(data: pl.DataFrame, spec: ModelSpecCommon) -> WeightExclusion:
    """Remove the rows whose declared weight is exactly 0.0; refuse nothing.

    For the diagnostic entry points, which describe a fit that has already been accepted. A
    frame without the weight column is passed through, as `diagnostics._weights` always
    treated one. The mask is `== 0.0` — never `<= 0`, never a tolerance, never a null test.
    """
    if spec.weight.kind == "column" and str(spec.weight.column) in data.columns:
        weights = _weights(data, spec)
        assert weights is not None
        return _exclude(data, weights != 0.0, spec)
    return _exclude(data, np.ones(data.height, dtype=np.bool_), spec)


def require_usable_weights(
    data: pl.DataFrame,
    spec: ModelSpecCommon,
    error: Callable[[str, str], Exception],
    *,
    what: str = "this fit",
) -> WeightExclusion:
    """Refuse an unusable weight column, then remove the weight-0 rows (FR-111).

    `error` is the calling arm's own fit-error class (`GlmFitError`, `GbmFitError`,
    `EbmFitError`), so the platform's handler maps the one code whichever arm raised it.
    """
    weights = _weights(data, spec)
    if weights is None:
        return _exclude(data, np.ones(data.height, dtype=np.bool_), spec)
    column = str(spec.weight.column)

    unusable = ~np.isfinite(weights) | (weights < 0.0)
    if unusable.any():
        first = int(np.argmax(unusable))
        raise error(
            WEIGHT_INVALID_CODE,
            f"the declared weight column {column!r} holds {int(unusable.sum())} negative, "
            f"null or non-finite value(s) in {what} (first at row {first}). Only a weight of "
            "exactly 0 is excluded (FR-111); anything else cannot be fitted on and is not "
            "guessed at. Nothing was estimated.",
        )

    kept = _exclude(data, weights != 0.0, spec)
    if kept.data.height == 0:
        raise error(
            WEIGHT_INVALID_CODE,
            f"every row of {what} was excluded (FR-111): for weight 0, or for an unknown "
            f"severity amount. The declared weight column {column!r} leaves nothing else to "
            "fit. Nothing was estimated.",
        )
    return kept
