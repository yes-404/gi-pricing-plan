"""The read-side `Provenance` object and the ten read classes that carry it (`00` FR-2159, FR-6).

Decided on #1506 and its questions:

* **#1519 (b).** `Provenance` is a read-side class. The API composes it from the artifact's
  stored identity and its stored `job_id` on every read, and it is **never persisted**. No
  persisted class, stored row, migration or stored hash changes because of it.
* **#1868 (a).** It names two kinds of identity: the shape's own (`entity_type`, and
  `entity_id` as a UUID, since none of the ten has a slug or a version of its own), and the
  governed artifacts the shape is about (`subject_refs`, in the `refs` form,
  `{type}:{slug}@{version}`, `00` ID-3). The order of two or more subject refs is stated per
  shape by FR-2159 and is the composer's to keep: a `tuple`, never a set.
* **No `computed_at`.** Composed on every read, so nothing in it is an honest source for
  that value (slice 1's accepted text). `extra="forbid"` refuses it on the way in as well.
* **#1810 B.** The JSON Schema generated from this class replaces the hand-authored
  `docs/contracts/schemas/common/provenance.schema.json`.

Each read class is its persisted class plus one required `provenance` field, so the read
dumps as the stored shape plus one key. It inherits `frozen` and `extra="forbid"`, so the
stored class refuses a read's JSON and a read can never be written back as the artifact.
`ValidationReportRead` extends `ValidationReportView`, the report **as presented** (`01`
§4.6), because that is what `GET /validation-reports/{report_id}` returns: on the stored
`ValidationReport`, `overall` and `counts` are properties and never serialised.
"""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from model_schema.backtests import Backtest
from model_schema.comparison import ModelComparison
from model_schema.diagnostics import Diagnostics
from model_schema.dislocation import DislocationRun
from model_schema.metrics import MetricCertificate
from model_schema.objectives import ObjectiveCertificate
from model_schema.profiles import Profile
from model_schema.refs import ArtifactRef
from model_schema.regression import RegressionRun
from model_schema.transparency import TransparencyArtifact
from model_schema.validation import ValidationReportView

__all__ = [
    "BacktestRead",
    "DiagnosticsRead",
    "DislocationRunRead",
    "MetricCertificateRead",
    "ModelComparisonRead",
    "ObjectiveCertificateRead",
    "ProfileRead",
    "Provenance",
    "ProvenanceEntityType",
    "RegressionRunRead",
    "TransparencyArtifactRead",
    "ValidationReportRead",
]

#: The ten governed shapes FR-2159 names, in snake_case. A closed set: a name outside it is
#: refused, so a composer's typo fails in a test rather than publishing a badge that names
#: nothing. Declared as a `Literal` so the generated contract carries the set inline as a
#: string `enum` (FR-24), without a second component the frontend would also have to type.
ProvenanceEntityType = Literal[
    "validation_report",
    "profile",
    "diagnostics",
    "model_comparison",
    "backtest",
    "regression_run",
    "objective_certificate",
    "dislocation_run",
    "metric_certificate",
    "transparency_artifact",
]


class Provenance(BaseModel):
    """Where a governed artifact came from: itself, the Job that produced it, and its subjects.

    Read-side (`00` FR-2159): composed by the API on every read of the ten shapes, and never
    persisted. `produced_by_job_id` is the artifact's stored `job_id`; null means none was
    recorded, which a view shows as "not recorded". It is required and has no default, so a
    composer that forgets it fails rather than silently stating "not recorded".
    `subject_refs` is never empty for a shape with a governed parent, and its order is
    FR-2159's: `ModelComparison` in `summary.model_refs` order, `DislocationRun` baseline then
    candidate, `RegressionRun` suite then rating version.

    `unnamed_subjects` counts the governed parents whose stored reference cannot be read, for
    example a model whose family slug is outside the `refs` grammar (nothing holds family
    slugs to it). Such a parent is left out of `subject_refs` and counted here, so a read that
    worked before provenance never fails on it and never drops it silently. It is null when
    every parent is named. Decided on #1961 (comment 7060609084, point 2) and recorded as
    ADR-2170: #1868's "never empty" stands for every parent the reference form can name.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    entity_type: ProvenanceEntityType
    entity_id: UUID
    produced_by_job_id: UUID | None
    subject_refs: tuple[ArtifactRef, ...]
    unnamed_subjects: int | None = Field(default=None, ge=1)


class ValidationReportRead(ValidationReportView):
    """A Validation Report as presented (`01` §4.6), with its `Provenance` (`00` FR-2159)."""

    provenance: Provenance


class ProfileRead(Profile):
    """A Profile (`01` §4.7), with its `Provenance` (`00` FR-2159)."""

    provenance: Provenance


class DiagnosticsRead(Diagnostics):
    """A model's Diagnostics (`02` FR-170), with its `Provenance` (`00` FR-2159).

    `chained_factors` (`02` FR-109, §5.1): the slugs of the model's Factors on a chained
    grouping, those that have a finer level. The read composes it from the model's definition
    by the rule the fit uses, never from data (FR-170), so a client can tell "no finer level"
    from "fitted before the finer level was stored" without a rule of its own. The route always
    sets it, to an empty tuple when no Factor has a finer level; the `None` default only keeps
    the field optional in the contract and the generated client, as `finer_level_ae` is.
    """

    provenance: Provenance
    chained_factors: tuple[str, ...] | None = None


class ModelComparisonRead(ModelComparison):
    """A Model Comparison (`02` §4.11), with its `Provenance` (`00` FR-2159)."""

    provenance: Provenance


class BacktestRead(Backtest):
    """A Backtest (`02` §4.12), with its `Provenance` (`00` FR-2159)."""

    provenance: Provenance


class RegressionRunRead(RegressionRun):
    """A Regression Run (`03` §4.9), with its `Provenance` (`00` FR-2159)."""

    provenance: Provenance


class ObjectiveCertificateRead(ObjectiveCertificate):
    """A Custom Objective's certificate (`02` §4.7), with its `Provenance` (`00` FR-2159)."""

    provenance: Provenance


class DislocationRunRead(DislocationRun):
    """A Dislocation Run (`03` §4.6), with its `Provenance` (`00` FR-2159)."""

    provenance: Provenance


class MetricCertificateRead(MetricCertificate):
    """A Custom Metric's certificate (`02` §4.13), with its `Provenance` (`00` FR-2159)."""

    provenance: Provenance


class TransparencyArtifactRead(TransparencyArtifact):
    """A Transparency Artifact (`02` §4.9), with its `Provenance` (`00` FR-2159)."""

    provenance: Provenance
