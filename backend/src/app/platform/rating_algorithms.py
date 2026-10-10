"""Rating Algorithm persistence and save-time validation (03 §4.1, slice W9-2).

A saved algorithm is stored as its validated JSON content. Save-time validation runs
before a row is written: the shape's own invariants (FR-212) and the deeper checks
in `pricing_core.rating.compile.validate_algorithm` (FR-216/227/273/274/275/276).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ModelRow, RatingAlgorithmRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform.modelling import load_factors
from app.platform.perils import load_structure_by_ref
from model_schema import (
    MODEL_SPEC_ADAPTER,
    ArtifactRef,
    GraphCycleError,
    GraphUnresolvedRefError,
    RatingAlgorithmDraft,
    ValidationIssue,
)
from model_schema.perils import PerilComponent
from model_schema.rating import (
    AlgorithmDiff,
    AlgorithmValidationReport,
    RatingAlgorithm,
    RatingModelCallStep,
    RatingStepBase,
    diff_algorithms,
    graph_invariant_issues,
)
from pricing_core.modelling.factors import required_model_inputs
from pricing_core.rating.compile import validate_algorithm

__all__ = [
    "create_algorithm",
    "diff_between",
    "get_algorithm",
    "graph_validation_error",
    "raise_first_issue",
    "validate_draft",
]


def graph_validation_error(exc: ValidationError, *, artifact: str) -> PlatformError:
    """Map a shape refusal to its named code, rather than Pydantic's generic 422.

    The shapes enforce the graph invariants (FR-212) in their own validators and raise a
    typed signal (`GraphCycleError`, `GraphUnresolvedRefError`); the code is chosen by that
    class, in `exc.errors()`, and never by the message text, which echoes the input.
    `artifact` names the thing in the two strings that say what it is ("rating algorithm",
    "sub-graph"); every other string is fixed. One mapping for both artifacts, never a copy.
    """
    raised = [
        error["ctx"]["error"]
        for error in exc.errors()
        if error["type"] == "value_error" and "error" in error.get("ctx", {})
    ]
    if any(isinstance(error, GraphCycleError) for error in raised):
        return PlatformError(
            "RATING_GRAPH_CYCLIC",
            "Rating graph is cyclic",
            422,
            f"A {artifact} is a directed acyclic graph (FR-212).",
        )
    if any(isinstance(error, GraphUnresolvedRefError) for error in raised):
        return PlatformError(
            "RATING_GRAPH_UNRESOLVED_REF",
            "Rating graph references an undefined value",
            422,
            "Every consumed value is produced by a step (FR-212).",
        )
    return PlatformError(
        "VALIDATION_FAILED",
        f"{artifact.capitalize()} is invalid",
        422,
        str(exc),
    )


def _parse_algorithm(content: dict[str, Any]) -> RatingAlgorithm:
    """Parse the submitted JSON, mapping a shape-invariant refusal to its named code."""
    try:
        return RatingAlgorithm.model_validate(content)
    except ValidationError as exc:
        raise graph_validation_error(exc, artifact="rating algorithm") from exc


def raise_first_issue(issues: list[ValidationIssue]) -> None:
    """Refuse on the first validation issue, with its own code; return on an empty list."""
    if not issues:
        return
    issue = issues[0]
    raise PlatformError(
        issue.code,
        issue.code.replace("_", " ").title(),
        422,
        issue.message,
    )


def _issues_to_error(algorithm: RatingAlgorithm) -> None:
    """Refuse an algorithm whose deeper checks fail, naming the first issue."""
    raise_first_issue(validate_algorithm(algorithm))


async def _accepted_feature_map_values(
    session: AsyncSession, workspace_id: UUID, ref: ArtifactRef, seen: set[str]
) -> set[str] | None:
    """What a `model_call`'s `feature_map` may name for `ref`: its Model's required inputs
    (`required_model_inputs`, FR-222 as amended) plus the column its spec declares as the
    offset (R2), plus a model-offset source's own (DP-3 (a)). `None` when the Model does not
    exist yet (R1): an algorithm saves before its models do, and compile refuses a missing pin.
    """
    if str(ref) in seen:
        return set()
    seen.add(str(ref))
    row = await session.scalar(
        select(ModelRow).where(
            ModelRow.workspace_id == workspace_id,
            ModelRow.model_family_slug == ref.slug,
            ModelRow.version == ref.version,
        )
    )
    if row is None:
        return None
    spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
    factors = await load_factors(session, workspace_id=workspace_id, factor_ids=list(spec.factors))
    feature_order = (row.fit_result or {}).get("feature_order", ())
    accepted = set(required_model_inputs(factors, feature_order))
    offset = spec.offset
    if offset.kind in ("log_column", "column") and offset.column is not None:
        accepted.add(offset.column)
    if offset.kind == "model" and offset.offset_model_ref is not None:
        source = await _accepted_feature_map_values(
            session, workspace_id, ArtifactRef.model_validate(offset.offset_model_ref), seen
        )
        accepted |= source or set()
    return accepted


async def _accepted_by_a_component(
    session: AsyncSession, workspace_id: UUID, ref: ArtifactRef
) -> set[str] | None:
    """What a `peril_structure_ref` step's `feature_map` may name: the UNION of what each
    component model accepts (`RL-1459` DP-A3-7 (a)). One map feeds every component, and the
    frequency GLM's offset column is not a severity input, so a value passes when at least one
    component accepts it. `None` when the structure, or any of its components, does not exist
    yet (R1): then no value can be judged, and compile refuses a missing pin.
    """
    row = await load_structure_by_ref(
        session, workspace_id=workspace_id, slug=ref.slug, version=ref.version
    )
    if row is None:
        return None
    components: list[ArtifactRef] = []
    for raw in row.perils:
        peril = PerilComponent.model_validate(raw)
        for model_ref in (peril.frequency_model, peril.severity_model, peril.burning_cost_model):
            if model_ref is not None and model_ref not in components:
                components.append(model_ref)
    seen: set[str] = set()
    accepted: set[str] = set()
    for model_ref in components:
        values = await _accepted_feature_map_values(session, workspace_id, model_ref, seen)
        if values is None:
            return None
        accepted |= values
    return accepted


async def check_model_call_feature_maps(
    session: AsyncSession, workspace_id: UUID, steps: Sequence[RatingStepBase]
) -> None:
    """FR-222 as amended (PL-1464 item 13, R1 to R5): a `feature_map` value that is neither a
    pinned Model's required input nor its offset column is refused with
    `MODEL_CALL_FEATURE_MAP_INVALID` (422) before anything is written.

    A `peril_structure_ref` step is checked against the union of its component models
    (`PL-1465` item 16, `RL-1459` DP-A3-7 (a)).

    **Membership only, not completeness**: an unmapped Factor is compile's to refuse (PL 9494).
    """
    for step in steps:
        if not isinstance(step, RatingModelCallStep):
            continue
        if step.model_ref is not None:
            subject, whose = step.model_ref, "Factor slugs or its offset column"
            accepted = await _accepted_feature_map_values(session, workspace_id, subject, set())
        else:
            assert step.peril_structure_ref is not None  # exactly one is set (FR-222)
            subject = step.peril_structure_ref
            whose = "component models' Factor slugs or offset columns"
            accepted = await _accepted_by_a_component(session, workspace_id, subject)
        if accepted is None:
            continue
        for graph_name, value in step.feature_map.items():
            if value not in accepted:
                raise PlatformError(
                    "MODEL_CALL_FEATURE_MAP_INVALID",
                    "A model_call feature_map names something its model does not take",
                    422,
                    f"Step {step.step_id!r} maps {graph_name!r} to {value!r}, which is not one "
                    f"of {subject}'s {whose} "
                    f"({sorted(accepted)}). A feature_map names the model's own vocabulary, "
                    "not a raw dataset column (FR-222).",
                )


async def create_algorithm(
    database: Database,
    workspace_id: UUID,
    created_by: UUID,
    content: dict[str, Any],
) -> RatingAlgorithmRow:
    """Parse, validate, and persist a rating algorithm (03 §5.1).

    A conflicting (slug, version) is refused as a conflict; save-time validation runs
    before the row is written.
    """
    algorithm = _parse_algorithm(content)
    _issues_to_error(algorithm)

    async with database.unit_of_work() as session:
        await check_model_call_feature_maps(session, workspace_id, algorithm.steps)
        existing = await session.scalar(
            select(RatingAlgorithmRow).where(
                RatingAlgorithmRow.workspace_id == workspace_id,
                RatingAlgorithmRow.slug == algorithm.slug,
                RatingAlgorithmRow.version == algorithm.version,
            )
        )
        if existing is not None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Rating algorithm version already exists",
                409,
                f"{algorithm.slug}@{algorithm.version} already exists in this workspace.",
            )
        row = RatingAlgorithmRow(
            workspace_id=workspace_id,
            slug=algorithm.slug,
            version=algorithm.version,
            content=content,
            created_by=created_by,
        )
        session.add(row)
        await session.flush()
        return row


async def get_algorithm(
    database: Database, workspace_id: UUID, slug: str, version: int
) -> RatingAlgorithm:
    """Load one algorithm version by its canonical `slug@version`."""
    async with database.session() as session:
        row = await session.scalar(
            select(RatingAlgorithmRow).where(
                RatingAlgorithmRow.workspace_id == workspace_id,
                RatingAlgorithmRow.slug == slug,
                RatingAlgorithmRow.version == version,
            )
        )
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "Rating algorithm not found",
            404,
            f"No rating algorithm {slug}@{version} in this workspace.",
        )
    return RatingAlgorithm.model_validate(row.content)


async def diff_between(
    database: Database, workspace_id: UUID, slug: str, version: int, against: int
) -> AlgorithmDiff:
    """The structural diff between two versions of one algorithm (FR-219)."""
    current = await get_algorithm(database, workspace_id, slug, version)
    base = await get_algorithm(database, workspace_id, slug, against)
    return diff_algorithms(base, current)


def validate_draft(draft: RatingAlgorithmDraft) -> AlgorithmValidationReport:
    """FR-1607: every issue saving `draft` would refuse on, located; nothing is persisted.

    The graph invariants first, all of them; only once they hold are the deeper checks
    (`validate_algorithm`, FR-227 and the expression checks) run, as save runs them.
    """
    issues = graph_invariant_issues(draft)
    if issues:
        return AlgorithmValidationReport(issues=issues)
    algorithm = RatingAlgorithm.model_validate(draft.model_dump(mode="json", exclude_unset=True))
    return AlgorithmValidationReport(issues=validate_algorithm(algorithm))
