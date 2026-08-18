"""What `POST /models/{id}/predict` answers (`02` FR-MODEL-62/63/77/93, §5.1).

Not a persisted artifact. `Diagnostics`, `Backtest` and `ModelComparison` are measurements
the platform keeps and an approval cites; a prediction is a question asked and answered at
dev/debug scale, and `03-rating-engine.md` owns the production path. It lives in
`model-schema` all the same, because it crosses the API boundary and ADR-0002 admits no
second definition of a shape that does.

**The uncertainty block is the point of this module, and its name is load-bearing.**

FR-MODEL-63 asks for "GLM prediction intervals from the covariance matrix". Those are two
different quantities and the covariance matrix yields only the first of them:

* `x'Vx` is the sampling variance of the estimated linear predictor, so
  `g⁻¹(η̂ ± z·√(x'Vx))` is a **confidence interval for the expectation** `E[Y|x]` — how
  precisely the fit located the mean.
* A **prediction interval** for an individual outcome `Y` adds the process variance
  `φ·V(μ)`, which the covariance matrix does not contain. For a frequency model on a single
  policy that term dominates, and the honest interval is very nearly `[0, 1]` claims —
  which is true, and prices nothing.

Pricing reads the expectation, so the useful uncertainty is the one on the expectation, and
this module reports it under that name: `UncertaintyKind.CONFIDENCE_INTERVAL_MEAN`, never
`prediction_interval`. FR-MODEL-77 already refuses a GBM variance-model approximation on
exactly this reasoning — *it renders as a predictive interval and is not one* — and a
correctly-computed interval carrying the wrong name fails the same test one step later, in
the reader rather than in the arithmetic.

**Absence is typed, never implied by a null.** Three of `02`'s reasons are FR-MODEL-77's
GBM vocabulary and one is FR-MODEL-93's, and a caller that receives no interval is told
which of them applies rather than left to guess whether the model has no uncertainty or the
platform declined to compute it.
"""

from __future__ import annotations

import enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "PredictedRow",
    "Prediction",
    "UnavailableReason",
    "Uncertainty",
    "UncertaintyBasis",
    "UncertaintyKind",
]


class UncertaintyBasis(enum.StrEnum):
    """What the covariance matrix behind an interval actually is (FR-MODEL-99).

    `UncertaintyKind` says which *quantity* the interval covers; this says what the matrix
    it came from **is**, which for a penalised fit is not the matrix the estimate deserves.

    One vocabulary for both halves of `02`'s uncertainty, deliberately: FR-MODEL-21's
    coefficient standard errors and FR-MODEL-63's interval are read off the same `V`, so a
    qualification that applied to one and not the other would be describing a matrix that
    does not exist (OQ-MODEL-14, decided 2026-08-18).
    """

    #: An unpenalised fit (`alpha == 0`): the model-based information matrix, and the
    #: standard errors and interval it yields are the ones the estimate deserves.
    INFORMATION_MATRIX = "information_matrix"
    #: A **penalised** fit (`alpha > 0`). `glum` warns on every one of them that "the
    #: covariance matrix will be incorrect", and it is right: what it returns is the
    #: information matrix of the *unpenalised* problem, which knows nothing about the
    #: shrinkage that produced the coefficients beside it. The error has a known direction —
    #: the interval is the one an unpenalised fit of the same design would earn, so it is
    #: **wider** than the shrunk estimate warrants — which makes it conservative and still
    #: wrong. With `l1_ratio > 0` it additionally ignores that the penalty *selected* the
    #: terms; the member is the same because the remedy is (FR-MODEL-99's bootstrap).
    UNPENALISED_INFORMATION_MATRIX = "unpenalised_information_matrix"


class UncertaintyKind(enum.StrEnum):
    """What the interval on a prediction *is*, or that there is not one.

    Deliberately not `prediction_interval`: see the module docstring. The value a caller
    reads is the claim the platform is making about the number beside it.
    """

    #: `g⁻¹(η̂ ± z·√(x'Vx))` — a confidence interval for `E[Y|x]` (FR-MODEL-63).
    CONFIDENCE_INTERVAL_MEAN = "confidence_interval_mean"
    #: No interval, with a `reason` (FR-MODEL-77, FR-MODEL-93). `02` R5 is satisfied by
    #: saying so, and only by saying so.
    UNAVAILABLE = "unavailable"


class UnavailableReason(enum.StrEnum):
    """Why a prediction carries no interval — FR-MODEL-77's vocabulary, plus FR-MODEL-93's.

    **Only two of these are reachable today**, and FR-MODEL-87's staging rule requires that
    to be said in place rather than discovered:

    * `NO_INTERVAL_MODELS_FITTED` — every GBM, since FR-MODEL-78's `interval_for` is not
      built and so no paired quantile model can exist to be found.
    * `COVARIANCE_NOT_STORED` — a GLM fitted before the covariance blob was written
      (FR-MODEL-93).

    `INTERVAL_MODELS_NOT_APPROVED` and `INTERVAL_MODELS_STALE` are declared and unreachable
    until FR-MODEL-78's paired quantile models land (Phase 1b). They are declared now
    because they are FR-MODEL-77's contract and a caller matching on this enum should not
    have to widen its match when the slice that fits one arrives.
    """

    #: FR-MODEL-77. No paired quantile models (FR-MODEL-78) exist for this model.
    NO_INTERVAL_MODELS_FITTED = "no_interval_models_fitted"
    #: FR-MODEL-77. Declared, unreachable until FR-MODEL-78 lands.
    INTERVAL_MODELS_NOT_APPROVED = "interval_models_not_approved"
    #: FR-MODEL-77. Declared, unreachable until FR-MODEL-78 lands.
    INTERVAL_MODELS_STALE = "interval_models_stale"
    #: FR-MODEL-93. A GLM whose fit predates the covariance blob. Distinct from the GBM
    #: reasons because nothing about this model makes an interval impossible — the inputs
    #: to one were not kept, and cannot be recovered from an artifact holding `p` numbers
    #: where the matrix is `p x p`. A blob that *should* exist and does not is a platform
    #: fault and surfaces as one; it is not this reason.
    COVARIANCE_NOT_STORED = "covariance_not_stored"


class Uncertainty(BaseModel):
    """The claim attached to every prediction in a response, once, for all its rows.

    On the response rather than on each row because it is a property of the *model* and the
    scoring path, not of a row: either the covariance matrix was available for this model or
    it was not, and repeating that verdict per row invites a reader to look for a row where
    it differs.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: UncertaintyKind
    #: Required when `kind` is `unavailable`, forbidden otherwise — see the validator.
    reason: UnavailableReason | None = None
    #: The two-sided confidence level, when there is an interval. 0.95 throughout, matching
    #: `Coefficient.ci_95`: an interval on a prediction and an interval on the coefficient
    #: it came from reported at different levels is a comparison nobody can make.
    level: float | None = Field(default=None, gt=0.0, lt=1.0)
    #: What the matrix behind the interval is (FR-MODEL-99). Required alongside a `level`
    #: and forbidden without one, by the same validator and for the same reason: an
    #: interval whose basis is unstated is one a reader will assume is exact, and for a
    #: penalised fit that assumption is the defect OQ-MODEL-14 was raised about.
    basis: UncertaintyBasis | None = None

    @model_validator(mode="after")
    def _the_kind_and_its_evidence_agree(self) -> Uncertainty:
        """An unavailable uncertainty carries its reason; an available one carries a level.

        Enforced rather than documented because the whole value of a typed absence is that
        the caller cannot receive one with the reason left off — which is a null by a
        longer name, and `02` R5 is not satisfied by a null.
        """
        if self.kind is UncertaintyKind.UNAVAILABLE:
            if self.reason is None:
                raise ValueError(
                    "uncertainty is 'unavailable' with no reason. `02` R5 is satisfied by "
                    "an explicit statement of why an interval is absent, never by its "
                    "absence."
                )
            if self.level is not None:
                raise ValueError(
                    f"uncertainty is 'unavailable' and carries level={self.level}. A "
                    "confidence level on an interval that does not exist reads as one that "
                    "does."
                )
            if self.basis is not None:
                raise ValueError(
                    f"uncertainty is 'unavailable' and carries basis={self.basis!r}. A "
                    "basis describes the matrix an interval came from; there is no "
                    "interval here."
                )
        else:
            if self.level is None:
                raise ValueError(
                    f"uncertainty is {self.kind!r} with no level. An interval whose "
                    "coverage is unstated cannot be compared with any other interval."
                )
            if self.reason is not None:
                raise ValueError(
                    f"uncertainty is {self.kind!r} and carries reason={self.reason!r}. A "
                    "reason explains an absence; there is no absence here."
                )
            if self.basis is None:
                raise ValueError(
                    f"uncertainty is {self.kind!r} with no basis. FR-MODEL-99: an interval "
                    "read off a penalised fit's covariance matrix is not the interval that "
                    "fit deserves, and a response that does not say which matrix it used "
                    "leaves the reader to assume the flattering one."
                )
        return self


class PredictedRow(BaseModel):
    """One scored row: the expectation, and its bounds where there are any.

    `lower` and `upper` are `None` together or set together, and which it is follows the
    response's single `Uncertainty` — the validator on `Prediction` is what ties them, since
    neither claim is checkable from a row alone.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: `μ = g⁻¹(η)` on the response scale, offset included (FR-MODEL-62).
    expected: float
    lower: float | None = None
    upper: float | None = None

    @model_validator(mode="after")
    def _the_bounds_are_a_pair_and_ordered(self) -> PredictedRow:
        """Half an interval is not an interval, and a reversed one is not the one computed.

        The ordering check is not decoration: `g⁻¹` for the `inverse` link is *decreasing*,
        so transforming the endpoints of a symmetric interval on `η` returns them swapped.
        A scorer that forgets to re-order produces `lower > upper` on exactly one link, and
        this is what refuses to serialise it.
        """
        if (self.lower is None) != (self.upper is None):
            raise ValueError(
                f"a one-sided interval (lower={self.lower}, upper={self.upper}). Both "
                "bounds or neither."
            )
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ValueError(
                f"interval bounds are reversed: lower={self.lower} > upper={self.upper}. "
                "Under a decreasing inverse link the transformed endpoints swap, and the "
                "scorer must re-order them rather than report them as computed."
            )
        return self


class Prediction(BaseModel):
    """The response to `POST /models/{id}/predict` (FR-MODEL-62, §5.1).

    Carries the model it came from by id *and* by family/version, because a prediction
    pasted into a review is unreadable without knowing which version produced it, and the
    id alone is not something a human recognises.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: UUID
    model_family_slug: str
    version: int = Field(ge=1)
    model_type: Literal["glm", "xgboost", "lightgbm"]
    uncertainty: Uncertainty
    rows: tuple[PredictedRow, ...]

    @model_validator(mode="after")
    def _every_row_matches_the_declared_uncertainty(self) -> Prediction:
        """The response's one claim, checked against all of its rows.

        Without this the two halves can disagree — an `unavailable` verdict beside rows
        carrying bounds, or an interval kind beside rows with none — and a caller reading
        one half would be reading a different response from a caller reading the other.
        """
        expected_bounds = self.uncertainty.kind is not UncertaintyKind.UNAVAILABLE
        for index, row in enumerate(self.rows):
            if (row.lower is not None) != expected_bounds:
                verdict = "carries bounds" if expected_bounds else "carries no bounds"
                raise ValueError(
                    f"uncertainty is {self.uncertainty.kind!r}, so every row {verdict}, "
                    f"but row {index} does not."
                )
        return self
