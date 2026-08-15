"""The settings registry and its three-layer resolver (FR-PLAT-43..46, `07` §4.4).

    environment variable  →  workspace setting  →  platform default

Every setting is **declared** here with a type, a default and its constraints. That is what
makes FR-PLAT-44 possible: an unknown key or an out-of-range value is rejected when it is
written, not discovered halfway through a validation run six weeks later.

Feature flags live in the same registry rather than a parallel one. They are settings with
a boolean type and a rule attached — FR-PLAT-46 requires them to **default to the safe
value**, and `SAFE_DEFAULT` records which direction that is for each, because "off" is not
automatically the safe answer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models import WorkspaceSettingRow
from app.errors import PlatformError
from model_schema import (
    SettingCandidate,
    SettingResolution,
    SettingSource,
    SettingType,
)

__all__ = [
    "REGISTRY",
    "SettingDefinition",
    "resolve",
    "resolve_all",
    "set_workspace_setting",
]


@dataclass(frozen=True)
class SettingDefinition:
    """One declared setting."""

    key: str
    type: SettingType
    default: Any
    description: str
    constraints: dict[str, Any] = field(default_factory=dict)
    feature_flag: bool = False

    def coerce(self, value: Any) -> Any:
        """Validate and normalise a candidate value, or raise `SETTING_INVALID`."""
        try:
            match self.type:
                case SettingType.BOOL:
                    if not isinstance(value, bool):
                        raise TypeError(f"expected a boolean, got {type(value).__name__}")
                    coerced: Any = value
                case SettingType.INT:
                    if isinstance(value, bool) or not isinstance(value, int):
                        raise TypeError(f"expected an integer, got {type(value).__name__}")
                    coerced = value
                case SettingType.FLOAT:
                    if isinstance(value, bool) or not isinstance(value, int | float):
                        raise TypeError(f"expected a number, got {type(value).__name__}")
                    coerced = float(value)
                case SettingType.STRING:
                    if not isinstance(value, str):
                        raise TypeError(f"expected a string, got {type(value).__name__}")
                    coerced = value
        except TypeError as exc:
            raise PlatformError(
                "SETTING_INVALID", "Setting has the wrong type", 422, f"{self.key}: {exc}"
            ) from exc

        minimum, maximum = self.constraints.get("min"), self.constraints.get("max")
        if minimum is not None and coerced < minimum:
            raise self._out_of_range(coerced)
        if maximum is not None and coerced > maximum:
            raise self._out_of_range(coerced)
        allowed = self.constraints.get("enum")
        if allowed is not None and coerced not in allowed:
            raise PlatformError(
                "SETTING_INVALID",
                "Setting value is not permitted",
                422,
                f"{self.key}: {coerced!r} is not one of {allowed}.",
            )
        return coerced

    def _out_of_range(self, value: Any) -> PlatformError:
        return PlatformError(
            "SETTING_INVALID",
            "Setting value is out of range",
            422,
            f"{self.key}: {value!r} violates {self.constraints}.",
        )


def _define(*definitions: SettingDefinition) -> dict[str, SettingDefinition]:
    return {d.key: d for d in definitions}


#: FR-PLAT-45 names the categories this must cover: currency, locale/timezone for display,
#: default validation thresholds, trace sampling rate, approval policy reference, retention
#: windows, and feature flags.
REGISTRY: dict[str, SettingDefinition] = _define(
    SettingDefinition(
        key="workspace.currency",
        type=SettingType.STRING,
        default="GBP",
        description="The workspace's single operating currency, ISO 4217 (FR-OVR-7, "
        "OQ-OVR-3). Not a display preference: money is stored in minor units of *this* "
        "currency and every artifact records it, so multi-currency in Phase 4 adds FX "
        "effective-dating rather than migrating every monetary column.",
        constraints={"enum": ["GBP", "EUR", "USD", "CHF", "SEK", "NOK", "DKK", "PLN"]},
    ),
    SettingDefinition(
        key="display.locale",
        type=SettingType.STRING,
        default="en-GB",
        description="BCP 47 locale for number and date formatting.",
    ),
    SettingDefinition(
        key="display.timezone",
        type=SettingType.STRING,
        default="Europe/London",
        description="IANA timezone for display. Stored timestamps are always UTC.",
    ),
    SettingDefinition(
        key="validation.psi_warn_threshold",
        type=SettingType.FLOAT,
        default=0.10,
        description="PSI above which a distributional check warns (`01` §6).",
        constraints={"min": 0.0, "max": 1.0},
    ),
    SettingDefinition(
        key="validation.psi_fail_threshold",
        type=SettingType.FLOAT,
        default=0.25,
        description="PSI above which a distributional check fails.",
        constraints={"min": 0.0, "max": 1.0},
    ),
    SettingDefinition(
        key="observability.trace_sample_rate",
        type=SettingType.FLOAT,
        default=1.0,
        description="Fraction of requests traced. 1.0 until volume makes it costly — an "
        "untraced request is one whose trace_id joins to nothing (R4).",
        constraints={"min": 0.0, "max": 1.0},
    ),
    SettingDefinition(
        key="governance.approval_policy_ref",
        type=SettingType.STRING,
        default="",
        description="Reference to the workspace's approval policy (`06` FR-GOV-12). Empty "
        "until governance is configured.",
    ),
    SettingDefinition(
        key="retention.job_history_days",
        type=SettingType.INT,
        default=400,
        description="How long Job history is kept. FR-PLAT-14 requires at least 13 months; "
        "400 days is that with margin, and the floor is enforced by the constraint.",
        constraints={"min": 396},
    ),
    SettingDefinition(
        key="retention.blob_gc_grace_days",
        type=SettingType.INT,
        default=30,
        description="A blob is collectable only when unreferenced and older than this "
        "(FR-PLAT-20).",
        constraints={"min": 1, "max": 3650},
    ),
    # -- feature flags (FR-PLAT-46) ---------------------------------------------------
    SettingDefinition(
        key="features.expression_objectives_enabled",
        type=SettingType.BOOL,
        default=False,
        description="Custom objectives written as expressions (`02` FR-MODEL-75, wf-05 "
        "Route B). Off by default: an arbitrary-code objective is a governance risk, so "
        "the safe value is the one that does not evaluate user input. OQ-MODEL-1 was "
        "decided on 2026-08-15 — expressions ship in Phase 2, so through Phase 1 this "
        "flag has nothing to enable and stays off; the certification machinery it will "
        "front is built now against templates.",
        feature_flag=True,
    ),
    SettingDefinition(
        key="features.sql_validation_check_enabled",
        type=SettingType.BOOL,
        default=False,
        description="Validation rules expressed as SQL (`01` §4.5). Off by default: it "
        "executes user-authored code against the dataset. OQ-DATA-3 was decided on "
        "2026-08-14 — the check is kept, but Admin-authored, single-Approver, and behind "
        "this flag, so a workspace that never needs the escape hatch never carries its "
        "risk.",
        feature_flag=True,
    ),
)

#: The safe value for each flag, recorded separately from the default so that a change to
#: one is visible as a change to the other. FR-PLAT-46 requires flags to default to the
#: safe value; a test asserts the two agree, so flipping a default silently is not possible.
SAFE_DEFAULT: dict[str, bool] = {
    "features.expression_objectives_enabled": False,
    "features.sql_validation_check_enabled": False,
}

#: Which settings an environment variable may override, and under what name.
def _env_name(key: str) -> str:
    return "GIP_SETTING_" + key.replace(".", "_").upper()


def _unknown(key: str) -> PlatformError:
    return PlatformError(
        "SETTING_INVALID",
        "Unknown setting",
        404,
        f"{key!r} is not a declared setting. Declaring it is a code change, so that its "
        "type and constraints exist before a value does (FR-PLAT-44).",
    )


async def resolve(
    session: AsyncSession, settings: Settings, workspace_id: UUID, key: str
) -> SettingResolution:
    """Resolve one setting through the three layers (FR-PLAT-43)."""
    definition = REGISTRY.get(key)
    if definition is None:
        raise _unknown(key)

    env_value = _env_candidate(settings, definition)
    workspace_value = (
        await session.execute(
            select(WorkspaceSettingRow.value).where(
                WorkspaceSettingRow.workspace_id == workspace_id,
                WorkspaceSettingRow.key == key,
            )
        )
    ).scalar_one_or_none()

    return _resolution(definition, env_value, workspace_value)


async def resolve_all(
    session: AsyncSession, settings: Settings, workspace_id: UUID
) -> list[SettingResolution]:
    """Resolve every declared setting. One query, not one per key."""
    rows = (
        await session.execute(
            select(WorkspaceSettingRow.key, WorkspaceSettingRow.value).where(
                WorkspaceSettingRow.workspace_id == workspace_id
            )
        )
    ).all()
    overrides: dict[str, Any] = {row[0]: row[1] for row in rows}
    return [
        _resolution(d, _env_candidate(settings, d), overrides.get(key))
        for key, d in sorted(REGISTRY.items())
    ]


def _env_candidate(settings: Settings, definition: SettingDefinition) -> Any:
    raw = settings.setting_overrides.get(_env_name(definition.key))
    if raw is None:
        return None
    return definition.coerce(_parse_env(definition, raw))


def _parse_env(definition: SettingDefinition, raw: str) -> Any:
    """Environment variables are strings; the registry says what they mean."""
    try:
        match definition.type:
            case SettingType.BOOL:
                return raw.strip().lower() in {"1", "true", "yes", "on"}
            case SettingType.INT:
                return int(raw)
            case SettingType.FLOAT:
                return float(raw)
            case SettingType.STRING:
                return raw
    except ValueError as exc:
        raise PlatformError(
            "SETTING_INVALID",
            "Environment override cannot be parsed",
            422,
            f"{_env_name(definition.key)}={raw!r}: {exc}",
        ) from exc


def _resolution(
    definition: SettingDefinition, env_value: Any, workspace_value: Any
) -> SettingResolution:
    if workspace_value is not None:
        workspace_value = definition.coerce(workspace_value)

    if env_value is not None:
        effective, source = env_value, SettingSource.ENV
    elif workspace_value is not None:
        effective, source = workspace_value, SettingSource.WORKSPACE
    else:
        effective, source = definition.default, SettingSource.DEFAULT

    return SettingResolution(
        key=definition.key,
        effective_value=effective,
        resolved_from=source,
        candidates=(
            SettingCandidate(source=SettingSource.ENV, value=env_value),
            SettingCandidate(source=SettingSource.WORKSPACE, value=workspace_value),
            SettingCandidate(source=SettingSource.DEFAULT, value=definition.default),
        ),
        type=definition.type,
        constraints=definition.constraints,
        feature_flag=definition.feature_flag,
        description=definition.description,
    )


async def set_workspace_setting(
    session: AsyncSession, workspace_id: UUID, key: str, value: Any
) -> SettingDefinition:
    """Write a workspace override, validating it first (FR-PLAT-44).

    The caller audits the change; this function does not, because the audit event needs the
    actor and the before-value, and passing both here would put the governance decision in
    the persistence layer.
    """
    definition = REGISTRY.get(key)
    if definition is None:
        raise _unknown(key)

    coerced = definition.coerce(value)
    row = (
        await session.execute(
            select(WorkspaceSettingRow).where(
                WorkspaceSettingRow.workspace_id == workspace_id,
                WorkspaceSettingRow.key == key,
            )
        )
    ).scalar_one_or_none()

    if row is None:
        session.add(WorkspaceSettingRow(workspace_id=workspace_id, key=key, value=coerced))
    else:
        row.value = coerced
    await session.flush()
    return definition
