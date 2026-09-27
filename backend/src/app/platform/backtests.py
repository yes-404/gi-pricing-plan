"""Requesting, recording and reading a backtest (`02` FR-187, §4.12, §5.1).

`pricing-core` owns the maths. This owns the rules that make a backtest mean what its name
says, and there are two that carry the weight:

* **It is not run on the data the model learned on.** The glossary defines a backtest as
  evaluation on a Dataset Version *other than* the one it was fitted on, and the refusal has
  to reach further than the parent version: the split's train and holdout parts are
  themselves versions, so backtesting "the holdout" would reproduce the fit-time number and
  present it as out-of-time performance. `BacktestSummary` enforces the parent case at the
  type; this is where the split parts are known.

* **The target version can actually be scored.** A later version with a renamed column
  fails inside `resolve_factors` — correctly, but twenty seconds later and as a failed Job.
  `request_comparison` set the precedent and the reason: refusing after the queue hop is a
  worse answer to the same question. The version's `arrow_schema` already knows its columns,
  so the check costs a read the request is doing anyway.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BacktestRow, DatasetSplitRow, DatasetVersionRow, ModelRow
from app.errors import PlatformError
from app.platform import audit, rbac
from app.platform import datasets as dataset_service
from model_schema import (
    MODEL_SPEC_ADAPTER,
    SCOREABLE_MODEL_STATUSES,
    Backtest,
    BacktestSummary,
    Factor,
    JobSource,
    ModelSpec,
    ModelStatus,
    Permission,
    Principal,
    new_uuid7,
)

__all__ = [
    "backtest_payload",
    "load_backtest",
    "record_backtest",
    "refuse_missing_columns",
    "request_backtest",
    "to_backtest",
    "version_ref",
]


async def version_ref(
    session: AsyncSession, *, workspace_id: UUID, version: DatasetVersionRow
) -> str:
    """`dataset_version:{slug}@{n}` — `00` ID-3's canonical form for a version.

    The slug lives on the dataset, not the version, so this is a join and not a format
    string. It is here rather than inlined at both call sites because the two refs a
    backtest compares must be built the same way: one built differently would differ from
    the other as a string, and `BacktestSummary`'s "not the data it learned on" invariant is
    a string comparison.
    """
    dataset = await dataset_service.load_dataset_by_id(
        session, workspace_id=workspace_id, dataset_id=version.dataset_id
    )
    return f"dataset_version:{dataset.slug}@{version.version}"


async def request_backtest(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    model_id: UUID,
    dataset_version_id: UUID,
) -> tuple[ModelRow, DatasetVersionRow]:
    """Validate a backtest request and return the model and the version to run it on.

    Gated on `model:fit` rather than `model:read`: this queues a compute Job that scores the
    whole of another dataset version. Reading a backtest someone else produced needs only
    `model:read`, which is what `load_backtest`'s route requires.
    """
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor, permission=Permission.MODEL_FIT
    )

    model = await session.get(ModelRow, model_id)
    if model is None or model.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Model not found", 404, f"No model {model_id} in this workspace."
        )
    if ModelStatus(model.status) not in SCOREABLE_MODEL_STATUSES or model.fit_result is None:
        raise PlatformError(
            "MODEL_NOT_FITTED",
            "A model with no fit result cannot be backtested",
            409,
            f"{model.model_family_slug}@{model.version} is {model.status!r}. There is "
            "nothing to score the later period with — fit it first (`02` §4.8: only a "
            "model at `fitted` or beyond carries a fit result).",
        )

    # **This order is load-bearing.** The definitional refusal comes first, before `01`
    # §1.3's validated gate: a split's parts are derived versions and stay `draft`, so the
    # gate answers a request to backtest the model's own holdout with "that version is not
    # validated" — which is true, unhelpful, and an instruction to go and validate the
    # holdout, after which the request would be allowed. Found by the test that expected
    # the other message.
    version = await dataset_service.load_version(
        session, workspace_id=workspace_id, version_id=dataset_version_id
    )
    spec = MODEL_SPEC_ADAPTER.validate_python(model.spec)
    await _refuse_the_data_it_learned_on(
        session, workspace_id=workspace_id, model=model, spec=spec, version=version
    )

    # Then the gate. A backtest scores rather than fits, and the reason is the same either
    # way: a number measured on data that never passed validation is not evidence anything
    # may be approved against.
    await dataset_service.fittable_or_refuse(
        session, workspace_id=workspace_id, version_id=dataset_version_id
    )
    return model, version


async def _refuse_the_data_it_learned_on(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    model: ModelRow,
    spec: ModelSpec,
    version: DatasetVersionRow,
) -> None:
    """The definitional refusal, over the parent version **and** its split parts.

    The parent case alone would be a check that looks right and misses the likeliest
    mistake. A model's `dataset_version_id` is the parent; the frames it was fitted and
    judged on are *derived versions* with ids of their own (`01` FR-76), so a request
    naming the holdout passes a parent-only check and produces the fit-time holdout figure
    under a heading that says out-of-time.
    """
    label = f"{model.model_family_slug}@{model.version}"
    if version.id == spec.dataset_version_id:
        raise PlatformError(
            "VALIDATION_FAILED",
            "A backtest cannot run on the version the model was fitted on",
            409,
            f"{label} was fitted on this version. A model measured on its own training "
            "data reports how well it memorised, and that number renders identically to "
            "out-of-time performance (`02` §2, FR-187).",
        )

    if spec.split_ref is None:
        return
    split = await session.get(DatasetSplitRow, spec.split_ref.split_artifact_id)
    if split is None or split.workspace_id != workspace_id:
        return
    for part, part_version_id in split.parts.items():
        if UUID(str(part_version_id)) != version.id:
            continue
        raise PlatformError(
            "VALIDATION_FAILED",
            "A backtest cannot run on a part of the split the model was fitted on",
            409,
            f"This version is the {part!r} part of split {split.name!r}, which {label} "
            "was fitted and judged on (`01` FR-76). Backtesting the holdout "
            "reproduces the fit-time holdout figure and presents it as a later period.",
        )


def refuse_missing_columns(
    *, model: ModelRow, spec: ModelSpec, version: DatasetVersionRow, factors: list[Factor]
) -> None:
    """Every column the score needs, checked against the version's own schema.

    Named separately from the refusals above because it needs the resolved factors, which
    the caller loads. Checking the *declared* schema rather than the parquet: the schema is
    what the version records about itself, and reading the file to answer a request is the
    cost this check exists to avoid.
    """
    available = {
        column for table in version.tables for column in (table.get("arrow_schema") or {})
    }
    if not available:
        # A version that declares no schema is not evidence of a missing column. Let the
        # Job find out from the parquet rather than refusing a request that may be fine.
        return

    needed: dict[str, str] = {spec.response_column: "the response"}
    if spec.offset.kind in {"log_column", "column"} and spec.offset.column:
        needed[spec.offset.column] = "the offset"
    if spec.weight.kind == "column" and spec.weight.column:
        needed[spec.weight.column] = "the weight"
    for factor in factors:
        for column in factor.source_columns:
            needed.setdefault(column, f"factor {factor.slug!r}")

    missing = {c: why for c, why in needed.items() if c not in available}
    if missing:
        detail = ", ".join(f"{c!r} ({why})" for c, why in sorted(missing.items()))
        raise PlatformError(
            "VALIDATION_FAILED",
            "The version does not carry the columns this model scores on",
            409,
            f"{model.model_family_slug}@{model.version} needs {detail}, which this version "
            "does not declare. A later period with a renamed column is the ordinary way a "
            "backtest fails, and it should fail as a refused request rather than as a Job "
            "that dies inside factor resolution.",
        )


def backtest_payload(model: ModelRow, version: DatasetVersionRow) -> dict[str, Any]:
    """What the `model.backtest` Job carries: which model, against which version."""
    return {"model_id": str(model.id), "dataset_version_id": str(version.id)}


async def record_backtest(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    model_id: UUID,
    dataset_version_id: UUID,
    summary: BacktestSummary,
    job_id: UUID | None = None,
) -> BacktestRow:
    """Persist the artifact and audit it (`06` R2 — the caller's transaction).

    Audited because a backtest is what a monitoring review and a re-approval argue from:
    "which model, against which period, measured when and at whose request" is the question
    asked six months later, and the artifact alone cannot answer the last part.
    """
    row = BacktestRow(
        id=new_uuid7(),
        workspace_id=workspace_id,
        model_id=model_id,
        dataset_version_id=dataset_version_id,
        job_id=job_id,
        computed_at=datetime.now(UTC),
        payload=summary.model_dump(mode="json"),
    )
    session.add(row)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.SYSTEM if job_id else JobSource.API,
        action="backtest.recorded",
        entity_ref=f"backtest:{row.id}",
        after={
            "model_ref": summary.model_ref,
            "dataset_version_ref": summary.dataset_version_ref,
            "rows": summary.partition.rows,
            # The headline, not the whole partition: an audit event records that something
            # happened, and the artifact is where the figures live. A/E is the one number a
            # reader scanning the log is looking for.
            "ae_overall": summary.partition.ae_overall,
        },
    )
    return row


def to_backtest(row: BacktestRow) -> Backtest:
    """The stored document, re-validated on the way out — `to_diagnostics`' reason.

    The payload was written by a build that may not be this one, and a shape change that
    slipped past a migration should surface loudly here rather than as a screen with
    missing numbers.
    """
    return Backtest(
        id=row.id,
        model_id=row.model_id,
        dataset_version_id=row.dataset_version_id,
        computed_at=row.computed_at,
        job_id=row.job_id,
        summary=BacktestSummary.model_validate(row.payload),
    )


async def load_backtest(
    session: AsyncSession, *, workspace_id: UUID, backtest_id: UUID
) -> Backtest:
    row = (
        await session.execute(
            select(BacktestRow).where(
                BacktestRow.id == backtest_id, BacktestRow.workspace_id == workspace_id
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "Backtest not found",
            404,
            f"No backtest {backtest_id} in this workspace.",
        )
    return to_backtest(row)
