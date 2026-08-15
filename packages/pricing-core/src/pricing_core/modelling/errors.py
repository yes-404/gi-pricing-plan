"""The named failures modelling raises, and the platform error codes they carry.

`02` §5.1 owns a catalogue of error codes; `pricing-core` cannot import the backend's
registry (ADR-0001), so each exception carries its code as data and the backend maps it to
an HTTP problem. FR-MODEL-23's principle generalises beyond fitting: a failure a caller can
act on is a **named** one, never a library traceback and never a silently degraded result.

They live here rather than beside the code that raises them because a banding is applied
while a factor is resolved, and a factor may be a banding — so a module-local exception
would have the two importing each other.
"""

from __future__ import annotations

from collections.abc import Sequence

__all__ = ["BandingError", "FactorResolutionError", "GroupingError", "ModellingError"]


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
