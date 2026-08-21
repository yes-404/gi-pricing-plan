"""The Transparency Artifact (`02` §3.6, §4.9, R3).

Fitting a black box is allowed; pricing with an unexplained one is not. This is the shape
that makes the second half enforceable: a non-GLM Model carries at least one of these
before a Rating Version may reference it (FR-MODEL-33).

**Three corrections to §4.9, made by building it** and recorded in the spec with the same
date:

* the artifact has an `id`, a `model_id` and a `created_at`. As printed it was a payload,
  not a stored artifact — the same gap `#81` found in the comparison artifact;
* `approximating_model_id` is populated from 2026-08-19 (FR-MODEL-96, resolving
  OQ-MODEL-10): the GLM approximation is a first-class Model, with its own spec
  (`GlmSpec.approximates_model_id`, FR-MODEL-102), `spec_hash`, version and diagnostics.
  Artifacts written before that date carry the coefficients and relativities inline
  instead, because the approximation had nowhere else to live — the two eras are
  mutually exclusive, enforced below;
* `kinds` is derived from which blocks are present rather than declared beside them. Two
  statements of one fact disagree, and §4.9's own invariant note ("`glm_approximation` in
  kinds implies the block is present") is that disagreement written down as a rule.
"""

from __future__ import annotations

import datetime as _datetime
import enum
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.modelling import Coefficient, RelativityLevel
from model_schema.refs import BlobRef

__all__ = [
    "EbmShapeFunctions",
    "GlmApproximation",
    "ShapContribution",
    "ShapInteraction",
    "ShapSummary",
    "TransparencyArtifact",
    "TransparencyKind",
    "WorstRegion",
]


class TransparencyKind(enum.StrEnum):
    """FR-MODEL-33's two forms, plus FR-MODEL-37's EBM export.

    `ebm_shape_functions` is produced by `build_ebm_shape_functions` (2026-08-21, W5,
    the EBM slice): an EBM needs no approximation — its shape functions ARE the rateable
    model, so this kind alone satisfies FR-MODEL-33. Declared before any slice produced
    one because the kind is what a reader of an artifact would look for, and adding it
    later would change the meaning of an artifact that listed only two.
    """

    GLM_APPROXIMATION = "glm_approximation"
    SHAP_SUMMARY = "shap_summary"
    EBM_SHAPE_FUNCTIONS = "ebm_shape_functions"


class WorstRegion(BaseModel):
    """Where the approximation is worst, and over how much of the book (FR-MODEL-36).

    The exposure share is required rather than optional. "The approximation is 11 % out for
    young high-mileage drivers" is a different sentence depending on whether that is 0.8 %
    of exposure or 8 %, and a fidelity statement without it invites the wrong one.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    description: str = Field(min_length=1)
    exposure_share: float = Field(ge=0.0, le=1.0)
    mean_abs_error_pct: float = Field(ge=0.0)


class GlmApproximation(BaseModel):
    """FR-MODEL-34 — a GLM fitted to the GBM's own predictions.

    What turns a GBM into something rateable as a table, so the coefficients and
    relativities are *here*: a fidelity score with no table behind it says the
    approximation was good without saying what it was.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    target: str = "gbm_prediction"
    #: FR-MODEL-96 — the Model that holds the approximation's table. Set on every artifact
    #: written from 2026-08-19; `None` on artifacts written before, which carry the table
    #: inline instead.
    approximating_model_id: UUID | None = None
    family: str = "gamma"
    link: str = "log"
    #: Both bounded above by 1 and **not** below: a fit can be worse than the mean, and
    #: clamping a negative R² to zero would report a useless approximation as a mediocre one.
    r_squared: float = Field(le=1.0)
    deviance_explained: float = Field(le=1.0)
    #: **Legacy era.** Populated only on artifacts written before FR-MODEL-96 was built
    #: (2026-08-19), where the table had nowhere else to live. New artifacts name a Model
    #: and leave these empty; the validator below refuses the mixture.
    coefficients: tuple[Coefficient, ...] = ()
    relativities: dict[str, tuple[RelativityLevel, ...]] = Field(default_factory=dict)
    worst_regions: tuple[WorstRegion, ...] = ()
    relativity_table_blob: BlobRef | None = None

    @model_validator(mode="after")
    def _the_table_is_in_exactly_one_place(self) -> Self:
        """FR-MODEL-96: a model reference, or an inline table, never both and never neither.

        Both is two answers to "where are the coefficients?", and the reader who takes the
        wrong one is reading a table that was not approved. Neither is a fidelity score with
        no table behind it — the approximation reported as good without saying what it was.
        """
        inline = bool(self.coefficients) or bool(self.relativities)
        if inline == (self.approximating_model_id is not None):
            raise ValueError(
                "a GLM approximation carries exactly one table: `approximating_model_id` "
                "naming the Model that holds it (FR-MODEL-96), or the inline "
                "`coefficients`/`relativities` of an artifact written before 2026-08-19."
            )
        return self


class ShapContribution(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    factor: str
    #: Mean |contribution| on the raw score scale, exposure-weighted (FR-MODEL-35).
    value: float = Field(ge=0.0)


class ShapInteraction(BaseModel):
    """One candidate interaction pair, and what it is worth (FR-MODEL-79).

    A **suggestion**, never an addition. The platform never writes a Factor into a Model
    Spec: an interaction becomes rateable only as an explicit `interaction` Factor carrying
    an intent and a written rationale, and the model document names it as an authored
    decision. Auto-detected structure entering a rating basis unreviewed is the overfitting
    route FR-MODEL-79 refuses.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    pair: tuple[str, str]
    strength: float = Field(ge=0.0)
    exposure_share: float = Field(default=1.0, ge=0.0, le=1.0)


class ShapSummary(BaseModel):
    """FR-MODEL-35 — TreeSHAP over the booster, on a reproducible sample."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    sample_rows: int = Field(ge=1)
    seed: int
    algorithm: str = "tree_shap"
    mean_abs_contribution: tuple[ShapContribution, ...] = ()
    dependence_blob: BlobRef | None = None
    #: Empty on LightGBM, which computes SHAP values and **not** SHAP interaction values.
    #: Empty rather than absent, and the reason is in `interactions_available`: a missing
    #: list reads as "no interactions found", which is a finding this backend cannot make.
    top_interactions: tuple[ShapInteraction, ...] = ()
    interactions_available: bool = True


class EbmShapeFunctions(BaseModel):
    """FR-MODEL-37's export: the model itself, as tables.

    A JSON document, deliberately: the artifact row stores a JSONB payload and the
    tables ARE the model — this block is a pointer to the document rather than a
    nested copy that could drift from it. Built by `build_ebm_shape_functions`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    terms_blob: str = Field(min_length=1)


class TransparencyArtifact(BaseModel):
    """The persisted artifact (`02` §4.9, FR-MODEL-33..37).

    Immutable once written, like every other artifact here: it is the evidence a Rating
    Version's approval was granted against (FR-MODEL-36), and evidence that can change
    after the decision is not evidence.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    model_id: UUID
    created_at: _datetime.datetime
    job_id: UUID | None = None
    glm_approximation: GlmApproximation | None = None
    shap_summary: ShapSummary | None = None
    ebm_shape_functions: EbmShapeFunctions | None = None
    #: FR-MODEL-36. Prose, deliberately: how well the approximation reproduces the model,
    #: **where it does not**, and the exposure share of that region. A number cannot say
    #: the second thing, and the second thing is what an approver needs.
    fidelity_statement: str = Field(min_length=1)
    #: FR-MODEL-52's monotonicity check, carried upward. `None` where the model declared no
    #: constrained factor — distinct from `False`, which would say a constraint was checked
    #: and failed.
    monotonicity_verified: bool | None = None

    @property
    def kinds(self) -> tuple[TransparencyKind, ...]:
        """Derived, never stored — §4.9's invariant made unable to be violated."""
        present: list[TransparencyKind] = []
        if self.glm_approximation is not None:
            present.append(TransparencyKind.GLM_APPROXIMATION)
        if self.shap_summary is not None:
            present.append(TransparencyKind.SHAP_SUMMARY)
        if self.ebm_shape_functions is not None:
            present.append(TransparencyKind.EBM_SHAPE_FUNCTIONS)
        return tuple(present)

    @model_validator(mode="after")
    def _an_artifact_explains_something(self) -> Self:
        """FR-MODEL-33: *at least one* form. An artifact with no block is a
        fidelity statement about nothing — and it would satisfy R3."""
        if not self.kinds:
            raise ValueError(
                "a transparency artifact carries neither a GLM approximation, a SHAP "
                "summary nor an EBM shape-functions export (FR-MODEL-33). It would "
                "satisfy R3 while explaining nothing."
            )
        return self
