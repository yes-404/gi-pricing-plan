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
    "IntervalModels",
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
    #: A paired-quantile interval on `Y` itself, from two Models fitted with the `quantile`
    #: template (FR-MODEL-78, FR-MODEL-101; OQ-MODEL-16, decided 2026-08-19).
    #:
    #: **Not** `confidence_interval_mean`, which covers `E[Y|x]` and is a much narrower
    #: claim; **not** FR-MODEL-98's reserved `prediction_interval`, which names a `φ·V(μ)`
    #: computation over aggregates and whose trigger would be left with no name to fire
    #: into if this took it. The value names the *estimator* as well as the quantity,
    #: because a reader comparing a GBM's bound with a GLM's must be able to see that they
    #: are not the same kind of claim.
    QUANTILE_PAIR_INTERVAL = "quantile_pair_interval"
    #: No interval, with a `reason` (FR-MODEL-77, FR-MODEL-93). `02` R5 is satisfied by
    #: saying so, and only by saying so.
    UNAVAILABLE = "unavailable"


class UnavailableReason(enum.StrEnum):
    """Why a prediction carries no interval — FR-MODEL-77's vocabulary, plus FR-MODEL-93's.

    **All four are reachable from 2026-08-19** (FR-MODEL-100, the paired-quantile slice).
    Two of them — `INTERVAL_MODELS_NOT_APPROVED` and `INTERVAL_MODELS_STALE` — were declared
    here and returned by nothing until that slice, named in place under FR-MODEL-87's
    staging rule. That note is removed with the state it described rather than left
    describing a platform which has moved on.

    What those two *mean* was not decided by FR-MODEL-77, which named them and stopped.
    FR-MODEL-100 decides both, as requirements rather than as implementation choices,
    because each had two defensible readings and the built one is the one a reader will
    assume was specified.
    """

    #: FR-MODEL-77. No paired quantile models (FR-MODEL-78) exist for this model.
    NO_INTERVAL_MODELS_FITTED = "no_interval_models_fitted"
    #: FR-MODEL-77 / FR-MODEL-100(ii). The pair exists but is less reviewed than the model
    #: it bounds — an approved Model would otherwise quote an unreviewed number beside a
    #: reviewed one. Not "unapproved outright": that reading would make the feature unusable
    #: at exactly the point an actuary is deciding whether the bounds are any good.
    INTERVAL_MODELS_NOT_APPROVED = "interval_models_not_approved"
    #: FR-MODEL-77 / FR-MODEL-100(iii). The central Model is `superseded`. It stays
    #: scoreable, so its bounds are quotable — and quoting them without saying the family
    #: has moved past this version is the silence FR-MODEL-77 exists to refuse.
    INTERVAL_MODELS_STALE = "interval_models_stale"
    #: FR-MODEL-93. A GLM whose fit predates the covariance blob. Distinct from the GBM
    #: reasons because nothing about this model makes an interval impossible — the inputs
    #: to one were not kept, and cannot be recovered from an artifact holding `p` numbers
    #: where the matrix is `p x p`. A blob that *should* exist and does not is a platform
    #: fault and surfaces as one; it is not this reason.
    COVARIANCE_NOT_STORED = "covariance_not_stored"


class IntervalModels(BaseModel):
    """The two Models a quantile-pair interval was computed from (FR-MODEL-78).

    Carried on the response because the bounds cost the actuary two extra fits and are
    Models in their own right — a reader who wants to know how the interval was made should
    reach them from the prediction rather than from a query they have to construct.

    The alphas are here as well as the ids because `level` is their difference and a reader
    checking a 0.90 interval should not have to open two artifacts to learn it came from
    0.05 and 0.95 rather than from 0.03 and 0.93.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    lower_model_id: UUID
    upper_model_id: UUID
    lower_alpha: float = Field(gt=0.0, lt=0.5)
    upper_alpha: float = Field(gt=0.5, lt=1.0)


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
    #: The two Models behind a quantile-pair interval. Required exactly when `kind` is
    #: `quantile_pair_interval` and forbidden otherwise, by the validator below.
    interval_models: IntervalModels | None = None

    @model_validator(mode="after")
    def _the_kind_and_its_evidence_agree(self) -> Uncertainty:
        """Each kind carries exactly its own evidence, and none of anyone else's.

        Enforced rather than documented because the whole value of a typed absence is that
        the caller cannot receive one with the reason left off — which is a null by a longer
        name, and `02` R5 is not satisfied by a null. The same argument applies in the other
        direction: an interval carrying a `reason`, or a quantile pair carrying a `basis`,
        describes evidence that does not exist.
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
            if self.interval_models is not None:
                raise ValueError(
                    "uncertainty is 'unavailable' and names interval models. If two bounds "
                    "were found and scored, this is not an absence."
                )
            return self

        if self.level is None:
            raise ValueError(
                f"uncertainty is {self.kind!r} with no level. An interval whose coverage is "
                "unstated cannot be compared with any other interval."
            )
        if self.reason is not None:
            raise ValueError(
                f"uncertainty is {self.kind!r} and carries reason={self.reason!r}. A reason "
                "explains an absence; there is no absence here."
            )

        if self.kind is UncertaintyKind.QUANTILE_PAIR_INTERVAL:
            if self.basis is not None:
                raise ValueError(
                    f"a quantile-pair interval carries basis={self.basis!r}. "
                    "`UncertaintyBasis` describes a covariance matrix, and a pair of "
                    "quantile fits has none — stating one would claim inference this "
                    "interval did not do (FR-MODEL-101)."
                )
            if self.interval_models is None:
                raise ValueError(
                    "a quantile-pair interval names no models. The bounds cost two extra "
                    "fits and are Models in their own right, so a reader must be able to "
                    "reach them (FR-MODEL-78)."
                )
            spread = self.interval_models.upper_alpha - self.interval_models.lower_alpha
            if abs(spread - self.level) > 1e-9:
                raise ValueError(
                    f"level={self.level} does not match the alphas it came from "
                    f"({self.interval_models.lower_alpha} to "
                    f"{self.interval_models.upper_alpha}, a spread of {spread}). A 0.05/0.95"
                    " pair covers 0.90, and a response claiming 0.95 from it overstates its"
                    " own coverage by exactly the amount a reader cannot see."
                )
            return self

        if self.basis is None:
            raise ValueError(
                f"uncertainty is {self.kind!r} with no basis. FR-MODEL-99: an interval read "
                "off a penalised fit's covariance matrix is not the interval that fit "
                "deserves, and a response that does not say which matrix it used leaves the "
                "reader to assume the flattering one."
            )
        if self.interval_models is not None:
            raise ValueError(
                f"uncertainty is {self.kind!r} and names interval models. This interval came "
                "from a covariance matrix, not from a pair of quantile fits."
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
