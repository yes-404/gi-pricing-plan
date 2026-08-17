"""Requesting, recording and reading a model comparison (`02` FR-MODEL-56, §5.1).

`pricing-core` owns the maths; this owns the rules that make a comparison mean something,
and there is really only one: **the models must be comparable, and that is decided before a
Job is queued.**

`reserve_model` set both the precedent and the reason. Refusing after the queue hop means a
worker discovers the models cite two different splits and the caller learns it from a failed
job twenty seconds later — a worse answer to the same question. And the check runs *again*
inside `pricing-core`, because a Job sits in a queue while the world moves, and because
`compare_models` is reachable from a notebook where this module is not (ADR-0001).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ModelComparisonRow, ModelRow
from app.errors import PlatformError
from app.platform import audit, rbac
from model_schema import (
    ComparisonSummary,
    JobSource,
    ModelComparison,
    ModelStatus,
    Permission,
    Principal,
    new_uuid7,
)

__all__ = [
    "compare_payload",
    "load_comparison",
    "record_comparison",
    "request_comparison",
    "to_comparison",
]

#: The statuses that carry coefficients. A `draft` has not been fitted and an `archived` one
#: may never have been (`02` §4.8's CHECK exempts both), so neither can score a holdout.
_COMPARABLE_STATUSES = frozenset(
    {
        ModelStatus.FITTED,
        ModelStatus.REVIEW,
        ModelStatus.APPROVED,
        ModelStatus.SUPERSEDED,
    }
)


async def request_comparison(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    model_ids: list[UUID],
    baseline_id: UUID | None = None,
) -> list[ModelRow]:
    """Validate a comparison request and return the models, in the order asked for.

    Gated on `model:fit` rather than `model:read`: this queues a compute Job that scores
    every candidate over the holdout. Reading a comparison someone else produced needs only
    `model:read`, which is what `load_comparison`'s route requires.

    Four refusals, all `MODELS_NOT_COMPARABLE`, each naming the specific thing that differs —
    "these are not comparable" without saying *which two things* is a refusal nobody can act
    on.
    """
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor, permission=Permission.MODEL_FIT
    )

    if len(model_ids) < 2:
        raise PlatformError(
            "MODELS_NOT_COMPARABLE",
            "A comparison needs two or more models",
            422,
            f"{len(model_ids)} model(s) were given. FR-MODEL-56 compares two or more; one "
            "model measured against nothing is a diagnostics read, and calling it a "
            "comparison would let an approval cite it as evidence a candidate was weighed.",
        )
    if len(set(model_ids)) != len(model_ids):
        raise PlatformError(
            "MODELS_NOT_COMPARABLE",
            "A model cannot be compared with itself",
            422,
            "The request names the same model twice. A version compared with itself "
            "produces agreement it did not have to earn.",
        )

    rows = (
        await session.execute(
            select(ModelRow).where(
                ModelRow.workspace_id == workspace_id, ModelRow.id.in_(model_ids)
            )
        )
    ).scalars().all()
    by_id = {row.id: row for row in rows}
    missing = [str(i) for i in model_ids if i not in by_id]
    if missing:
        raise PlatformError(
            "NOT_FOUND",
            "The comparison names models that do not exist",
            404,
            f"Unknown model id(s): {', '.join(missing)}.",
        )
    ordered = [by_id[i] for i in model_ids]

    unfitted = [r for r in ordered if ModelStatus(r.status) not in _COMPARABLE_STATUSES]
    if unfitted:
        detail = ", ".join(
            f"{r.model_family_slug}@{r.version} is {r.status!r}" for r in unfitted
        )
        raise PlatformError(
            "MODELS_NOT_COMPARABLE",
            "A model with no coefficients cannot be compared",
            409,
            f"{detail}. There is nothing to score the holdout with — fit it first "
            "(`02` §4.8: only a model at `fitted` or beyond carries a fit result).",
        )

    _refuse_unshared_splits(ordered)

    if baseline_id is not None and baseline_id not in by_id:
        raise PlatformError(
            "MODELS_NOT_COMPARABLE",
            "The baseline is not one of the models compared",
            422,
            f"Baseline {baseline_id} is not among {[str(i) for i in model_ids]}. Double "
            "lift is measured against the baseline, so a reference line from outside the "
            "set is one the reader cannot look up.",
        )
    return ordered


def _refuse_unshared_splits(rows: list[ModelRow]) -> None:
    """FR-MODEL-56's "same holdout", made checkable by `01` FR-DATA-36.

    The split is recorded on the parent version precisely so that "trained on the same
    split" is *one artifact two models cite* rather than two derivations believed to match.
    Comparing across two splits compares two models on different rows and reports the
    difference as performance — which is the failure this check exists for, and it is not
    hypothetical: `01`'s derived versions inherited their parent's rows for a whole slice.
    """
    seen: dict[tuple[str, str], list[str]] = {}
    for row in rows:
        ref = (row.spec or {}).get("split_ref")
        label = f"{row.model_family_slug}@{row.version}"
        if not ref:
            raise PlatformError(
                "MODELS_NOT_COMPARABLE",
                "A model cites no split",
                409,
                f"{label} declares no `split_ref`, so it has no named holdout to be "
                "compared on (`01` FR-DATA-36).",
            )
        seen.setdefault(
            (str(ref["split_artifact_id"]), str(ref.get("holdout_part", "test"))), []
        ).append(label)

    if len(seen) > 1:
        detail = "; ".join(
            f"{', '.join(labels)} on split {split} part {part!r}"
            for (split, part), labels in seen.items()
        )
        raise PlatformError(
            "MODELS_NOT_COMPARABLE",
            "The models were not fitted on the same holdout",
            409,
            f"{detail}. FR-MODEL-56 compares models fitted on the same holdout; on "
            "different splits the metrics are computed over different rows and the "
            "difference reads as performance.",
        )


def compare_payload(rows: list[ModelRow], *, baseline_id: UUID | None = None) -> dict[str, Any]:
    """What the `model.compare` Job carries: which models, and which is the baseline."""
    return {
        "model_ids": [str(r.id) for r in rows],
        "baseline_id": str(baseline_id) if baseline_id else str(rows[0].id),
    }


async def record_comparison(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    summary: ComparisonSummary,
    job_id: UUID | None = None,
) -> ModelComparisonRow:
    """Persist the artifact and audit it (`06` R2 — the caller's transaction).

    Audited because a comparison is what an approval cites: "which comparison, produced when,
    over which models" is a question a reviewer asks months later, and the artifact alone
    cannot say who asked for it.
    """
    row = ModelComparisonRow(
        id=new_uuid7(),
        workspace_id=workspace_id,
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
        action="model_comparison.recorded",
        entity_ref=f"model_comparison:{row.id}",
        after={
            "model_refs": list(summary.model_refs),
            "baseline_ref": summary.baseline_ref,
            "holdout_rows": summary.holdout_rows,
            # The leaders, not every number: an audit event is a record of what happened,
            # and the artifact is where the figures live.
            "leaders": {
                m.metric: m.leader for m in summary.metrics if m.leader is not None
            },
        },
    )
    return row


def to_comparison(row: ModelComparisonRow) -> ModelComparison:
    """The stored document, re-validated on the way out — `to_diagnostics`' reason.

    The payload was written by a build that may not be this one, and a shape change that
    slipped past a migration should surface loudly here rather than as a screen with missing
    numbers.
    """
    return ModelComparison(
        id=row.id,
        computed_at=row.computed_at,
        job_id=row.job_id,
        summary=ComparisonSummary.model_validate(row.payload),
    )


async def load_comparison(
    session: AsyncSession, *, workspace_id: UUID, comparison_id: UUID
) -> ModelComparison:
    row = (
        await session.execute(
            select(ModelComparisonRow).where(
                ModelComparisonRow.id == comparison_id,
                ModelComparisonRow.workspace_id == workspace_id,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "Comparison not found",
            404,
            f"No comparison {comparison_id} in this workspace.",
        )
    return to_comparison(row)
