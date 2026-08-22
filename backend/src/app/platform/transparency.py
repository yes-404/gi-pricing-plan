"""Persisting and reading transparency artifacts (`02` FR-MODEL-33..37, R3, §5.1).

Unlike diagnostics, a model may carry **several**: FR-MODEL-33 says *at least one* and
allows any of three forms — a GLM approximation, a SHAP summary, or an EBM's exported
shape functions (FR-MODEL-37) — and a SHAP summary recomputed on a larger sample is a
second artifact rather than a correction of the first. So the write appends and the read
takes the latest — older rows stay because an approval that cited one must still resolve
to it.

The row is insert-only at the privilege layer (FR-DATA-42) for FR-MODEL-36's reason: this
is the evidence a Rating Version's approval is granted against, and evidence that can change
after the decision is not evidence.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ModelRow, TransparencyArtifactRow
from app.errors import PlatformError
from app.platform import audit
from model_schema import JobSource, Principal, TransparencyArtifact, new_uuid7

__all__ = [
    "fitted_gbm_or_refuse",
    "load_transparency",
    "record_transparency",
    "to_artifact",
]


def to_artifact(row: TransparencyArtifactRow) -> TransparencyArtifact:
    """The stored document, re-validated on the way out — same reasoning as diagnostics."""
    return TransparencyArtifact.model_validate(
        {
            **row.payload,
            "id": str(row.id),
            "model_id": str(row.model_id),
            "created_at": row.created_at.isoformat(),
            "job_id": str(row.job_id) if row.job_id else None,
        }
    )


async def record_transparency(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    model_id: UUID,
    artifact: TransparencyArtifact,
    job_id: UUID | None = None,
) -> TransparencyArtifactRow:
    """Append an artifact and audit it (NFR-MODEL-9).

    Audited because R3 turns this row into a precondition for pricing: the event that
    created the evidence is part of the trail an approver's decision hangs from.
    """
    row = TransparencyArtifactRow(
        id=new_uuid7(),
        workspace_id=workspace_id,
        model_id=model_id,
        job_id=job_id,
        payload=artifact.model_dump(
            mode="json", exclude={"id", "model_id", "created_at", "job_id"}
        ),
    )
    session.add(row)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.SYSTEM if job_id else JobSource.API,
        action="model.transparency_built",
        entity_ref=f"model:{model_id}",
        after={
            "artifact": str(row.id),
            "kinds": [kind.value for kind in artifact.kinds],
            "monotonicity_verified": artifact.monotonicity_verified,
        },
    )
    return row


async def load_transparency(
    session: AsyncSession, *, workspace_id: UUID, model_id: UUID
) -> TransparencyArtifact:
    """The most recent artifact for a model, or a 404 that says which model.

    "Most recent" rather than "the one": a model with two artifacts has been explained
    twice, and the later explanation is the one a reader means. Citing a specific artifact
    is what an approval record does, by id, and that path resolves the row directly.
    """
    row = (
        await session.execute(
            select(TransparencyArtifactRow)
            .where(
                TransparencyArtifactRow.model_id == model_id,
                TransparencyArtifactRow.workspace_id == workspace_id,
            )
            .order_by(TransparencyArtifactRow.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "No transparency artifact for this model",
            404,
            f"Model {model_id} carries no transparency artifact. `02` R3 requires one "
            "before a Rating Version may reference a non-GLM model (FR-MODEL-33) — a "
            "GLM approximation, a SHAP summary, or an EBM's shape functions "
            "(FR-MODEL-37). `POST /api/v1/models/{id}/transparency` builds it.",
        )
    return to_artifact(row)


async def fitted_gbm_or_refuse(
    session: AsyncSession, *, workspace_id: UUID, model_id: UUID
) -> ModelRow:
    """The model a transparency build may run against.

    Two refusals, both before a Job exists, and both applying to any non-GLM
    transparency build. A model that is not fitted has no predictions to approximate, no
    trees to walk and no tables to export; a **GLM** needs no artifact at all, and
    building one would produce a GLM approximating itself — a fidelity statement reading
    100 % that means nothing, which is worse than no artifact because it looks like
    evidence.

    An **EBM** passes through unchanged: its exported tables are the model (FR-MODEL-37),
    so the builder needs nothing more than the fit result and the spec.
    """
    row = await session.get(ModelRow, model_id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError("NOT_FOUND", "Model not found", 404, f"No model {model_id}.")
    if row.fit_result is None:
        raise PlatformError(
            "MODEL_NOT_FITTED",
            "This model has no fit to explain",
            409,
            "A transparency artifact approximates a model's predictions and walks its "
            "trees (FR-MODEL-34, FR-MODEL-35). A model at `draft` has neither.",
        )
    if str(row.spec.get("model_type")) == "glm":
        raise PlatformError(
            "MODEL_ALREADY_TRANSPARENT",
            "A GLM needs no transparency artifact",
            409,
            "FR-MODEL-33 applies to **non-GLM** models. A GLM's coefficients are the "
            "explanation; approximating one with another GLM would report 100 % fidelity, "
            "which looks like evidence and is not.",
        )
    return row
