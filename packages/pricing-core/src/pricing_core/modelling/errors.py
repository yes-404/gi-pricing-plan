"""The named failures modelling raises, and the platform error codes they carry.

`02` §5.1 owns a catalogue of error codes; `pricing-core` cannot import the backend's
registry (ADR-703), so each exception carries its code as data and the backend maps it to
an HTTP problem. FR-115's principle generalises beyond fitting: a failure a caller can
act on is a **named** one, never a library traceback and never a silently degraded result.

They live here rather than beside the code that raises them because a banding is applied
while a factor is resolved, and a factor may be a banding — so a module-local exception
would have the two importing each other.
"""

from __future__ import annotations

from collections.abc import Sequence

from pricing_core.safe_error import CodedError

__all__ = [
    "BandingError",
    "FactorResolutionError",
    "GroupingError",
    "ModellingError",
    "NonFiniteDerivativeError",
    "ObjectiveError",
    "RoundBudgetExceededError",
]


class ModellingError(RuntimeError):
    """A modelling failure with a `02` §5.1 error code attached."""

    #: Overridden by subclasses that always raise one code.
    code = "FACTOR_RESOLUTION_FAILED"

    def __init__(self, code: str, message: str, *, terms: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.code = code
        self.terms = tuple(terms)


class FactorResolutionError(ModellingError):
    """A factor could not be resolved against this version (`FACTOR_RESOLUTION_FAILED`).

    Constructed from a message alone, because it only ever carries the one code — it
    predates the others and every call site passes prose.
    """

    def __init__(self, message: str, *, terms: Sequence[str] = ()) -> None:
        super().__init__("FACTOR_RESOLUTION_FAILED", message, terms=terms)


class BandingError(ModellingError):
    """A Banding that cannot be proposed, applied or fitted on (`BAND_*`)."""


class GroupingError(ModellingError):
    """A Grouping that is not exhaustive, or cannot be proposed (`GROUPING_*`)."""


class ObjectiveError(ModellingError):
    """A Custom Objective that cannot be compiled, certified or used (`OBJECTIVE_*`)."""


class _CodedObjectiveError(ObjectiveError, CodedError):
    """An `ObjectiveError` whose text is `CODE: message` and holds no input value.

    Also a `CodedError`, so the worker's error reduction keeps its text (`safe_error`): the
    text is persisted, so it names no value (FD-1219, DP-S2-4). Whatever a caller needs to
    locate the failure is a structured attribute, which the caller chooses where to keep.
    """

    def __init__(self, code: str, message: str, *, terms: Sequence[str] = ()) -> None:
        super().__init__(code, f"{code}: {message}", terms=terms)


class NonFiniteDerivativeError(_CodedObjectiveError):
    """A gradient or hessian went NaN/inf during a fit (`OBJECTIVE_NONFINITE_DERIVATIVE`).

    FR-165 requires the abort to name the boosting **round** and the **offending input
    range**: "the objective produced NaN" tells an author nothing, and the input that
    produced it is what tells a bad parameter from a bad domain from a bad y.

    **The range is not in the text** (DP-S2-4 (b)): `y` and `f` are dataset values, and this
    error is a `CodedError`, whose text a job record keeps. The text names the round, the
    row count and the fields. The ranges are `y_range` and `f_range`, for a record that is
    access-controlled.
    """

    def __init__(
        self,
        message: str,
        *,
        round_index: int,
        rows: int,
        y_range: tuple[float, float],
        f_range: tuple[float, float],
        terms: Sequence[str] = (),
    ) -> None:
        super().__init__("OBJECTIVE_NONFINITE_DERIVATIVE", message, terms=terms)
        self.round_index = round_index
        self.rows = rows
        self.y_range = y_range
        self.f_range = f_range


class RoundBudgetExceededError(_CodedObjectiveError):
    """One boosting round's objective evaluation ran past its budget (FR-165, NFR-483).

    The numbers it carries are times, not inputs.
    """

    def __init__(
        self, message: str, *, round_index: int, elapsed_s: float, budget_s: float
    ) -> None:
        super().__init__("OBJECTIVE_ROUND_BUDGET_EXCEEDED", message)
        self.round_index = round_index
        self.elapsed_s = elapsed_s
        self.budget_s = budget_s
