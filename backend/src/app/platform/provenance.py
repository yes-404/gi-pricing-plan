"""Composing the read-side `Provenance` of the ten governed shapes (`00` FR-2159, FR-6).

`Provenance` is composed here, at the read edge, on every read, and never persisted
(#1519 (b)). Each function takes what its route has already loaded and returns the shape's
read class: the persisted shape unchanged, plus one `provenance` key. Nothing here writes,
and nothing changes a stored row, a stored body or a stored hash.

The rules FR-2159 states, kept in one place so that a reviewer reads them once:

* `entity_type` is the shape's name, and `entity_id` its UUID. `RegressionRun` and
  `DislocationRun` carry no `id` field, so theirs is the row's id, the one the route was
  asked for.
* `produced_by_job_id` is the shape's own stored `job_id`, the value the response already
  shows beside it. Null means none was recorded. For a Validation Report the row is the
  Job id's home: the read takes it from `validation_reports.job_id`, never from the stored
  body (#1506 item 4; see `validation_report_read`).
* `subject_refs` is in the `refs` form and never empty, since each of the ten has a
  governed parent. One reference for the seven shapes with a single parent (the Dataset
  Version for `ValidationReport` and `Profile`; the Model for `Diagnostics`,
  `TransparencyArtifact` and `Backtest`; the Custom Metric version for `MetricCertificate`;
  the Custom Objective version for `ObjectiveCertificate`). Two or more, in a stated order,
  for the other three: `ModelComparison` in `summary.model_refs` order, `DislocationRun`
  baseline then candidate, `RegressionRun` suite then rating version.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CustomMetricRow,
    CustomObjectiveRow,
    DatasetVersionRow,
    DislocationRunRow,
    ModelRow,
    RegressionRunRow,
    ValidationReportRow,
)
from app.errors import PlatformError
from app.platform.backtests import version_ref
from model_schema import (
    ArtifactRef,
    Backtest,
    BacktestRead,
    Diagnostics,
    DiagnosticsRead,
    DislocationRun,
    DislocationRunRead,
    MetricCertificate,
    MetricCertificateRead,
    ModelComparison,
    ModelComparisonRead,
    ObjectiveCertificate,
    ObjectiveCertificateRead,
    Profile,
    ProfileRead,
    Provenance,
    ProvenanceEntityType,
    RegressionRun,
    RegressionRunRead,
    TransparencyArtifact,
    TransparencyArtifactRead,
    ValidationReportRead,
    ValidationReportView,
)

__all__ = [
    "backtest_read",
    "compose",
    "diagnostics_read",
    "dislocation_run_read",
    "metric_certificate_read",
    "model_comparison_read",
    "objective_certificate_read",
    "profile_read",
    "regression_run_read",
    "transparency_artifact_read",
    "validation_report_read",
]


def compose(
    entity_type: ProvenanceEntityType,
    entity_id: UUID,
    produced_by_job_id: UUID | None,
    subject_refs: Iterable[str | ArtifactRef | None],
) -> Provenance:
    """One `Provenance`, its subject refs in the order given.

    A string is parsed. A parent that cannot be written as a reference (`None` from a builder,
    or a stored string outside the `refs` grammar) is left out of `subject_refs` and counted in
    `unnamed_subjects` (`00` FR-2159's amendment of 2026-11-21; ADR-2170). A read that worked
    before provenance existed never fails on it, and
    never drops the parent silently.
    """
    named: list[ArtifactRef] = []
    unnamed = 0
    for ref in subject_refs:
        if isinstance(ref, ArtifactRef):
            named.append(ref)
        elif ref is None:
            unnamed += 1
        else:
            try:
                named.append(ArtifactRef.parse(ref))
            except ValueError:
                unnamed += 1
    return Provenance(
        entity_type=entity_type,
        entity_id=entity_id,
        produced_by_job_id=produced_by_job_id,
        subject_refs=tuple(named),
        unnamed_subjects=unnamed or None,
    )


def _read[R: BaseModel](read_cls: type[R], stored: Mapping[str, Any], provenance: Provenance) -> R:
    """The read class, validated from the stored shape's JSON plus `provenance`.

    `stored` is the JSON form, by alias (`RegressionRun`'s `BlobRef` serialises `bytes`), so
    the read validates exactly what the persisted class would and adds `provenance`. A
    caller may merge read-side keys into `stored` first, as `diagnostics_read` does with
    `chained_factors`.
    """
    return read_cls.model_validate({**stored, "provenance": provenance})


def _model_ref(model: ModelRow) -> ArtifactRef | None:
    """`model:{slug}@{n}`, or `None` when the family slug is outside the `refs` grammar (nothing
    holds family slugs to it), which `compose` counts as a parent it cannot name."""
    try:
        return ArtifactRef(type="model", slug=model.model_family_slug, version=model.version)
    except ValueError:
        return None


async def _dataset_version_ref(
    session: AsyncSession, *, workspace_id: UUID, version_id: UUID
) -> str:
    version = await session.get(DatasetVersionRow, version_id)
    if version is None or version.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Dataset version not found", 404, f"No version {version_id}."
        )
    # The backtest builder, imported rather than copied: two builders of one ref are two
    # strings that can come to differ.
    return await version_ref(session, workspace_id=workspace_id, version=version)


async def validation_report_read(
    session: AsyncSession, *, workspace_id: UUID, view: ValidationReportView
) -> ValidationReportRead:
    """`dataset_version:{slug}@{n}` of the version the report validated.

    **The Job id is the row's** (#1506 item 4, the maintainer's condition). Two runs on the
    same Dataset Version must give equal bodies (NFR-469, `test_validation_is_deterministic`
    compares two report bodies with the Job id included), so `dataset.validate` records its
    Job on `validation_reports.job_id` and not in the body. The read therefore takes
    `job_id`, and `produced_by_job_id`, from the row. `store_report` writes the column as
    `job_id or report.job_id`, so a body that carries an id never disagrees with it. A report
    stored before this change has neither and reads "not recorded"; there is no backfill.
    """
    row = await session.get(ValidationReportRow, view.id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Validation report not found", 404, f"No report {view.id}."
        )
    ref = await _dataset_version_ref(
        session, workspace_id=workspace_id, version_id=view.dataset_version_id
    )
    stored = {**view.model_dump(mode="json"), "job_id": row.job_id}
    return _read(
        ValidationReportRead,
        stored,
        compose("validation_report", view.id, row.job_id, [ref]),
    )


async def profile_read(
    session: AsyncSession, *, workspace_id: UUID, profile: Profile
) -> ProfileRead:
    """`dataset_version:{slug}@{n}` of the profiled version."""
    ref = await _dataset_version_ref(
        session, workspace_id=workspace_id, version_id=profile.dataset_version_id
    )
    return _read(
        ProfileRead,
        profile.model_dump(mode="json", by_alias=True),
        compose("profile", profile.id, profile.job_id, [ref]),
    )


def diagnostics_read(
    diagnostics: Diagnostics, *, model: ModelRow, chained_factors: Sequence[str]
) -> DiagnosticsRead:
    """`model:{slug}@{n}` of the fitted model, the row the route resolved; `chained_factors` is
    what `platform.diagnostics.chained_factor_slugs` read from that model's definition."""
    return _read(
        DiagnosticsRead,
        {
            **diagnostics.model_dump(mode="json", by_alias=True),
            "chained_factors": list(chained_factors),
        },
        compose("diagnostics", diagnostics.id, diagnostics.job_id, [_model_ref(model)]),
    )


def model_comparison_read(comparison: ModelComparison) -> ModelComparisonRead:
    """The compared models, in `summary.model_refs` order exactly: the baseline is wherever
    the stored summary put it, never moved to the front."""
    return _read(
        ModelComparisonRead,
        comparison.model_dump(mode="json", by_alias=True),
        compose(
            "model_comparison",
            comparison.id,
            comparison.job_id,
            comparison.summary.model_refs,
        ),
    )


def backtest_read(backtest: Backtest) -> BacktestRead:
    """`summary.model_ref`, the model backtested: FR-2159 names the Model as a Backtest's
    single governed parent. The version it ran against stays in `summary`."""
    return _read(
        BacktestRead,
        backtest.model_dump(mode="json", by_alias=True),
        compose("backtest", backtest.id, backtest.job_id, [backtest.summary.model_ref]),
    )


def regression_run_read(row: RegressionRunRow) -> RegressionRunRead:
    """The suite, then the rating version. `run.job_id` is the Job id's only home: the table
    has no `job_id` column. `entity_id` is the row's id, since the run has no `id` field."""
    run = RegressionRun.model_validate(row.run)
    return _read(
        RegressionRunRead,
        row.run,
        compose("regression_run", row.id, run.job_id, [run.suite_ref, run.rating_version_ref]),
    )


def dislocation_run_read(row: DislocationRunRow) -> DislocationRunRead:
    """The baseline, then the candidate. `entity_id` is the row's id, since the run has no
    `id` field."""
    run = DislocationRun.model_validate(row.run)
    return _read(
        DislocationRunRead,
        row.run,
        compose("dislocation_run", row.id, run.job_id, [run.baseline_ref, run.candidate_ref]),
    )


async def objective_certificate_read(
    session: AsyncSession, *, workspace_id: UUID, certificate: ObjectiveCertificate
) -> ObjectiveCertificateRead:
    """`custom_objective:{slug}@{n}`, at the version the certificate certified."""
    objective = await session.get(CustomObjectiveRow, certificate.custom_objective_id)
    if objective is None or objective.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND",
            "Custom objective not found",
            404,
            f"No custom objective {certificate.custom_objective_id}.",
        )
    ref = ArtifactRef(
        type="custom_objective", slug=objective.slug, version=certificate.objective_version
    )
    return _read(
        ObjectiveCertificateRead,
        certificate.model_dump(mode="json", by_alias=True),
        compose("objective_certificate", certificate.id, certificate.job_id, [ref]),
    )


async def metric_certificate_read(
    session: AsyncSession, *, workspace_id: UUID, certificate: MetricCertificate
) -> MetricCertificateRead:
    """`custom_metric:{slug}@{n}`, at the version the certificate certified."""
    metric = await session.get(CustomMetricRow, certificate.custom_metric_id)
    if metric is None or metric.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND",
            "Custom metric not found",
            404,
            f"No custom metric {certificate.custom_metric_id}.",
        )
    ref = ArtifactRef(type="custom_metric", slug=metric.slug, version=certificate.metric_version)
    return _read(
        MetricCertificateRead,
        certificate.model_dump(mode="json", by_alias=True),
        compose("metric_certificate", certificate.id, certificate.job_id, [ref]),
    )


async def transparency_artifact_read(
    session: AsyncSession, *, workspace_id: UUID, artifact: TransparencyArtifact
) -> TransparencyArtifactRead:
    """`model:{slug}@{n}` of the model the artifact explains."""
    model = await session.get(ModelRow, artifact.model_id)
    if model is None or model.workspace_id != workspace_id:
        raise PlatformError("NOT_FOUND", "Model not found", 404, f"No model {artifact.model_id}.")
    return _read(
        TransparencyArtifactRead,
        artifact.model_dump(mode="json", by_alias=True),
        compose("transparency_artifact", artifact.id, artifact.job_id, [_model_ref(model)]),
    )
