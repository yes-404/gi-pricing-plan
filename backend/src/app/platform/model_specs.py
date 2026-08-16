"""Validating a Model Spec without fitting it (`02` FR-MODEL-44, FR-MODEL-81, §5.1).

The point is **cost**. Every check here is answerable from artifacts the platform already
stores — the version's status and totals, its profile's distinct counts, the factor rows,
the split row — so a spec that cannot be fitted is refused in milliseconds instead of after
a compute job has read a parquet file and run a solver. `wf-01` step D2 is exactly this
moment, and FR-MODEL-81's "before any compute is spent" is only true if the check itself
spends none.

**Problems are collected, not raised at the first failure.** `02` §5.3 asks the spec
builder for live validation as the form is edited; a validator that stopped at the first
error would turn a ten-factor spec into a ten-round conversation.

The complexity gate is the same function `reserve_model` calls, so `POST /models` and
`POST /model-specs/validate` cannot disagree about whether a spec is acceptable — which
they would within a fortnight if each carried its own copy.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models import DatasetSplitRow, DatasetVersionRow, FactorRow, ProfileRow
from app.errors import PlatformError
from app.platform import audit
from app.platform import settings as settings_service
from app.platform.modelling import to_factor
from model_schema import (
    DatasetStatus,
    Factor,
    GlmSpec,
    JobSource,
    Principal,
    Profile,
    SpecProblem,
    SpecProblemKind,
    SpecValidation,
)

__all__ = ["complexity_or_refuse", "enforce_complexity", "validate_spec"]


async def _limits(
    session: AsyncSession, settings: Settings, workspace_id: UUID
) -> tuple[int | None, float | None]:
    """FR-MODEL-81's two thresholds, or `None` where the workspace sets none.

    `None` is the default and the decision — OQ-MODEL-6 refused a platform-wide constant,
    so an unset limit means "no gate", not "gate at zero".
    """
    max_factors = await settings_service.resolve(
        session, settings, workspace_id, "modelling.max_factor_count"
    )
    min_exposure = await settings_service.resolve(
        session, settings, workspace_id, "modelling.min_exposure_per_parameter"
    )
    return max_factors.effective_value, min_exposure.effective_value


def _estimated_parameters(factors: list[Factor], profile: Profile | None) -> int:
    """Fitted parameters a spec would spend, from the profile rather than the data.

    A categorical factor spends `levels - 1`; anything else spends 1; the intercept spends
    one more. The level count comes from the stored profile's `distinct_count`, which is
    why this costs nothing — reading the parquet to count them exactly would be the compute
    the gate exists to avoid.

    An **estimate**, and named one. A factor whose banding collapses forty levels into five
    is over-counted here, so the gate is conservative in the direction that refuses a spec
    which would in fact have fitted. The diagnostics record the true count after the fit
    (FR-MODEL-81), and that is the number a reviewer reads.
    """
    counts = {c.name: c.distinct_count for c in profile.columns} if profile else {}
    total = 1  # the intercept
    for factor in factors:
        source = factor.source_columns[0] if factor.source_columns else factor.slug
        distinct = counts.get(source)
        total += max(distinct - 1, 1) if distinct and distinct > 1 else 1
    return total


def complexity_or_refuse(
    *,
    factors: list[Factor],
    profile: Profile | None,
    exposure_years: Decimal | None,
    max_factor_count: int | None,
    min_exposure_per_parameter: float | None,
) -> tuple[list[SpecProblem], int, float | None]:
    """The FR-MODEL-81 gate, shared by spec validation and model reservation.

    Returns the problems it found rather than raising, because `validate_spec` reports a
    list and `reserve_model` turns the same list into a refusal. One implementation, two
    presentations — the alternative is two thresholds that drift.
    """
    problems: list[SpecProblem] = []
    parameters = _estimated_parameters(factors, profile)

    if max_factor_count is not None and len(factors) > max_factor_count:
        problems.append(
            SpecProblem(
                kind=SpecProblemKind.COMPLEXITY_LIMIT,
                subject="modelling.max_factor_count",
                message=(
                    f"the spec declares {len(factors)} factors and this workspace allows "
                    f"{max_factor_count} (FR-MODEL-81). The limit is a workspace setting, "
                    "not a platform constant — a larger book may warrant raising it."
                ),
            )
        )

    per_parameter: float | None = None
    if exposure_years is not None and parameters > 0:
        per_parameter = float(exposure_years) / parameters
        if min_exposure_per_parameter is not None and per_parameter < min_exposure_per_parameter:
            problems.append(
                SpecProblem(
                    kind=SpecProblemKind.COMPLEXITY_LIMIT,
                    subject="modelling.min_exposure_per_parameter",
                    message=(
                        f"about {parameters} parameters over {exposure_years} exposure "
                        f"years is {per_parameter:.1f} per parameter, below this "
                        f"workspace's {min_exposure_per_parameter} (FR-MODEL-81). The "
                        "parameter count is estimated from the version's profile, so a "
                        "banded factor is counted at its unbanded levels."
                    ),
                )
            )

    return problems, parameters, per_parameter


async def validate_spec(
    session: AsyncSession,
    settings: Settings,
    *,
    workspace_id: UUID,
    actor: Principal,
    spec: GlmSpec,
) -> SpecValidation:
    """Everything that can refuse this spec, answered before any compute (FR-MODEL-44).

    Structural rules the *type* already enforces — a Poisson model declaring no offset, a
    Tweedie power outside (1, 2) — are absent here on purpose: `GlmSpec` refuses to be
    constructed at all, so the request never reaches this function. Re-checking them would
    be a second statement of the same rule, and the two would disagree eventually.
    """
    problems: list[SpecProblem] = []

    version = (
        await session.execute(
            select(DatasetVersionRow).where(
                DatasetVersionRow.id == spec.dataset_version_id,
                DatasetVersionRow.workspace_id == workspace_id,
            )
        )
    ).scalar_one_or_none()

    if version is None:
        raise PlatformError(
            "NOT_FOUND",
            "Dataset version not found",
            404,
            f"No version {spec.dataset_version_id} in this workspace. A spec naming a "
            "version that does not exist is not an invalid spec, it is a bad reference.",
        )

    if DatasetStatus(version.status) is not DatasetStatus.VALIDATED:
        problems.append(
            SpecProblem(
                kind=SpecProblemKind.DATASET_NOT_VALIDATED,
                subject=str(version.id),
                message=(
                    f"the version is {version.status!r} and fitting requires 'validated' "
                    "(`01` §1.3, `02` R1). There is no override."
                ),
            )
        )

    factors = await _factors(session, workspace_id, spec)
    found = {f.id for f in factors}
    for factor_id in spec.factors:
        if factor_id not in found:
            problems.append(
                SpecProblem(
                    kind=SpecProblemKind.FACTOR_MISSING,
                    subject=str(factor_id),
                    message="the spec pins a factor that does not exist in this workspace.",
                )
            )

    columns = _columns(version)
    for factor in factors:
        if factor.prohibited:
            problems.append(
                SpecProblem(
                    kind=SpecProblemKind.FACTOR_PROHIBITED,
                    subject=factor.slug,
                    message=(
                        f"{factor.slug!r} is prohibited: {factor.prohibited_reason}. "
                        "FR-MODEL-5 refuses it in any Model Spec, and the attempt is "
                        "audited."
                    ),
                )
            )
        missing = [c for c in factor.source_columns if columns and c not in columns]
        if missing:
            problems.append(
                SpecProblem(
                    kind=SpecProblemKind.FACTOR_UNRESOLVABLE,
                    subject=factor.slug,
                    message=(
                        f"{factor.slug!r} reads {missing}, which this version does not "
                        "have. FR-MODEL-2: a Factor is defined against a Dataset and "
                        "resolved against a version, and this is that resolution failing "
                        "— before a job rather than inside one."
                    ),
                )
            )

    if columns and spec.response_column not in columns:
        problems.append(
            SpecProblem(
                kind=SpecProblemKind.RESPONSE_MISSING,
                subject=spec.response_column,
                message="the response column is not in this version.",
            )
        )
    if (
        columns
        and spec.offset.kind in {"log_column", "column"}
        and str(spec.offset.column) not in columns
    ):
        problems.append(
            SpecProblem(
                kind=SpecProblemKind.OFFSET_MISSING,
                subject=str(spec.offset.column),
                message=(
                    "the offset column is not in this version. A frequency model fitted "
                    "without its exposure offset is wrong in a way that looks reasonable."
                ),
            )
        )

    problems.extend(await _split_problems(session, workspace_id, spec))

    profile = await _profile(session, workspace_id, spec.dataset_version_id)
    max_factors, min_exposure = await _limits(session, settings, workspace_id)
    complexity, parameters, per_parameter = complexity_or_refuse(
        factors=factors,
        profile=profile,
        exposure_years=_exposure(version),
        max_factor_count=max_factors,
        min_exposure_per_parameter=min_exposure,
    )
    problems.extend(complexity)

    if complexity:
        # FR-MODEL-81 requires the refusal to be audited. Only the complexity refusal: a
        # spec that names a missing column is a typo, and auditing every keystroke of a
        # form with live validation would bury the governance events in noise.
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=actor,
            source=JobSource.API,
            action="model_spec.refused_for_complexity",
            entity_ref=f"model_family:{spec.model_family_slug}",
            after={
                "factor_count": len(factors),
                "estimated_parameter_count": parameters,
                "exposure_per_parameter": per_parameter,
                "max_factor_count": max_factors,
                "min_exposure_per_parameter": min_exposure,
            },
        )

    return SpecValidation(
        ok=not problems,
        problems=tuple(problems),
        factor_count=len(factors),
        estimated_parameter_count=parameters,
        exposure_per_parameter=per_parameter,
        max_factor_count=max_factors,
        min_exposure_per_parameter=min_exposure,
    )


async def _factors(
    session: AsyncSession, workspace_id: UUID, spec: GlmSpec
) -> list[Factor]:
    if not spec.factors:
        return []
    rows = (
        await session.execute(
            select(FactorRow).where(
                FactorRow.workspace_id == workspace_id, FactorRow.id.in_(list(spec.factors))
            )
        )
    ).scalars()
    return [to_factor(row) for row in rows]


def _columns(version: DatasetVersionRow) -> set[str]:
    """Column names the version carries, from its recorded schema rather than its data."""
    names: set[str] = set()
    for entry in version.tables or []:
        names.update((entry.get("arrow_schema") or {}).keys())
    return names


def _exposure(version: DatasetVersionRow) -> Decimal | None:
    """The version's recorded exposure, as `Decimal` (FR-OVR-7)."""
    totals = version.totals or {}
    raw = totals.get("exposure_years")
    if raw is None:
        return None
    try:
        return Decimal(str(raw))
    except (InvalidOperation, ValueError):  # pragma: no cover - defensive
        return None


async def _profile(
    session: AsyncSession, workspace_id: UUID, version_id: UUID
) -> Profile | None:
    row = (
        await session.execute(
            select(ProfileRow)
            .where(
                ProfileRow.workspace_id == workspace_id,
                ProfileRow.dataset_version_id == version_id,
            )
            .order_by(ProfileRow.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    return Profile.model_validate(row.body) if row is not None else None


async def _split_problems(
    session: AsyncSession, workspace_id: UUID, spec: GlmSpec
) -> list[SpecProblem]:
    """The split must exist and name two real parts (FR-DATA-36, FR-MODEL-54).

    Checked here rather than only in the fit handler because the handler's refusal arrives
    after the Job has been queued, accepted and started — a `202` followed by a failure is
    a worse answer to "is this spec valid?" than a `200` saying no.
    """
    if spec.split_ref is None:
        return [
            SpecProblem(
                kind=SpecProblemKind.SPLIT_MISSING,
                message=(
                    "the spec names no split, so the fit would have no holdout. "
                    "FR-MODEL-54 makes a diagnostic reported without its holdout "
                    "counterpart a defect, and `02` §4.8 makes diagnostics the condition "
                    "of reaching `fitted`."
                ),
            )
        ]

    ref = spec.split_ref
    split = (
        await session.execute(
            select(DatasetSplitRow).where(
                DatasetSplitRow.id == ref.split_artifact_id,
                DatasetSplitRow.workspace_id == workspace_id,
            )
        )
    ).scalar_one_or_none()
    if split is None:
        return [
            SpecProblem(
                kind=SpecProblemKind.SPLIT_INVALID,
                subject=str(ref.split_artifact_id),
                message="the spec names a split that does not exist in this workspace.",
            )
        ]

    missing = [p for p in (ref.train_part, ref.holdout_part) if p not in split.parts]
    if missing:
        return [
            SpecProblem(
                kind=SpecProblemKind.SPLIT_INVALID,
                subject=split.name,
                message=(
                    f"split {split.name!r} defines {sorted(split.parts)} and the spec asks "
                    f"for {missing}."
                ),
            )
        ]
    return []


async def enforce_complexity(
    session: AsyncSession,
    settings: Settings,
    *,
    workspace_id: UUID,
    actor: Principal,
    spec: GlmSpec,
) -> None:
    """Refuse a breaching spec before a Job is queued (FR-MODEL-81).

    `POST /models`' half of the gate. It runs the **same** `complexity_or_refuse` that
    `validate_spec` reports, so a spec the validator called acceptable cannot be refused
    here — the failure mode of two thresholds maintained separately.

    Only the complexity rules. `reserve_model` already answers R1 and the prohibited-factor
    rule with their own error codes, and re-answering them here would change what a caller
    sees for reasons that have nothing to do with this requirement.
    """
    max_factors, min_exposure = await _limits(session, settings, workspace_id)
    if max_factors is None and min_exposure is None:
        # The default. No limits set means no gate, so nothing is read and nothing is
        # audited — FR-MODEL-81's unset default costs a settings lookup and stops.
        return

    version = (
        await session.execute(
            select(DatasetVersionRow).where(
                DatasetVersionRow.id == spec.dataset_version_id,
                DatasetVersionRow.workspace_id == workspace_id,
            )
        )
    ).scalar_one_or_none()
    if version is None:  # pragma: no cover - reserve_model refuses first
        return

    factors = await _factors(session, workspace_id, spec)
    problems, parameters, per_parameter = complexity_or_refuse(
        factors=factors,
        profile=await _profile(session, workspace_id, spec.dataset_version_id),
        exposure_years=_exposure(version),
        max_factor_count=max_factors,
        min_exposure_per_parameter=min_exposure,
    )
    if not problems:
        return

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="model_spec.refused_for_complexity",
        entity_ref=f"model_family:{spec.model_family_slug}",
        after={
            "factor_count": len(factors),
            "estimated_parameter_count": parameters,
            "exposure_per_parameter": per_parameter,
            "max_factor_count": max_factors,
            "min_exposure_per_parameter": min_exposure,
        },
    )
    raise PlatformError(
        "MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT",
        "This model spec exceeds the workspace's complexity limits",
        422,
        " ".join(p.message for p in problems),
    )
