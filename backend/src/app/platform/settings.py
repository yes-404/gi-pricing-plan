"""The settings registry and its four-layer resolver (FR-446, FR-447, FR-448, FR-449, `07` §4.4).

    process variable  →  Environment setting  →  workspace setting  →  platform default

The Environment layer applies only when the caller names an Environment, and only to a key
whose declared scope permits it (`RL-1311`). A process variable never supplies an
Environment-only key.

Every setting is **declared** here with a type, a default and its constraints. That is what
makes FR-447 possible: an unknown key or an out-of-range value is rejected when it is
written, not discovered halfway through a validation run six weeks later.

Feature flags live in the same registry rather than a parallel one. They are settings with
a boolean type and a rule attached — FR-449 requires them to **default to the safe
value**, and `SAFE_DEFAULT` records which direction that is for each, because "off" is not
automatically the safe answer.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ConfigInvalidError, Settings
from app.db.models import EnvironmentRow, EnvironmentSettingRow, WorkspaceSettingRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from model_schema import (
    SettingCandidate,
    SettingResolution,
    SettingSource,
    SettingType,
)

__all__ = [
    "REGISTRY",
    "SettingDefinition",
    "SettingScope",
    "require_environment",
    "resolve",
    "resolve_all",
    "set_environment_setting",
    "set_workspace_setting",
    "validate_setting_overrides",
]

_log = get_logger("app.platform.settings")


class SettingScope(enum.StrEnum):
    """The levels a setting may be set at (FR-446, `RL-1311` item 1)."""

    WORKSPACE = "workspace"
    WORKSPACE_OR_ENVIRONMENT = "workspace_or_environment"
    ENVIRONMENT = "environment"


@dataclass(frozen=True)
class SettingDefinition:
    """One declared setting."""

    key: str
    type: SettingType
    default: Any
    description: str
    constraints: dict[str, Any] = field(default_factory=dict)
    feature_flag: bool = False
    scope: SettingScope = SettingScope.WORKSPACE

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


#: FR-448 names the categories this must cover: currency, locale/timezone for display,
#: default validation thresholds, trace sampling rate, approval policy reference, retention
#: windows, and feature flags.
REGISTRY: dict[str, SettingDefinition] = _define(
    SettingDefinition(
        key="workspace.currency",
        type=SettingType.STRING,
        default="GBP",
        description="The workspace's single operating currency, ISO 4217 (FR-10, "
        "OQ-542). Not a display preference: money is stored in minor units of *this* "
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
        key="modelling.max_factor_count",
        type=SettingType.INT,
        default=None,
        description="Maximum factors a Model Spec may declare (`02` FR-185, "
        "OQ-580). **Unset by default, and that is the decision** — a large book "
        "legitimately supports a large model, so there is no platform-wide constant. Where "
        "a workspace sets one, a breaching spec is refused with "
        "`MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT` before any compute is spent, and the "
        "refusal is audited. Whether *this* model is overfitted stays a judgement for the "
        "Approver holding the diagnostic (`06`).",
        constraints={"min": 1},
    ),
    SettingDefinition(
        key="modelling.min_exposure_per_parameter",
        type=SettingType.FLOAT,
        default=None,
        description="Minimum exposure per fitted parameter a Model Spec may leave (`02` "
        "FR-185). Unset by default, for the reason above. Checked against the "
        "version's recorded totals and its profile's distinct counts rather than by "
        "reading the data, so the refusal costs nothing — which is what makes 'before any "
        "compute is spent' true rather than aspirational.",
        constraints={"min": 0.0},
    ),
    SettingDefinition(
        key="rating.batch_abort_failure_rate",
        type=SettingType.FLOAT,
        default=None,
        description="Above what per-quote failure rate a `score.batch` run aborts rather "
        "than continuing (`03` FR-255, RL-889: "
        "`docs/plans/2026-08-29-w11-slices-3-4-rulings.md`). **Unset by default** — "
        "FR-255's own construction, 'does not abort … unless the failure rate exceeds "
        "a declared threshold', makes an undeclared threshold mean no rate-based abort, "
        "with the counts-and-samples half still accruing. A batch request may carry its "
        "own value as a Job argument, never a fourth resolution tier here, and it may "
        "only *lower* the effective threshold — never raise it (`01` FR-56's "
        "`severity_override` precedent). When a run aborts it records both the threshold "
        "in force and the observed failure rate.",
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
        key="rating.trace_sample_rate",
        type=SettingType.FLOAT,
        default=0.01,
        description="`03` FR-259's sampled-production-traces rate: the fraction of "
        "*quoted* real-time scoring outcomes persisted as a `ScoringTrace` (`03` §4.5, WK-671 "
        "Task 4B). Default 1 %, per the requirement's own text. **Not the same setting as "
        "`observability.trace_sample_rate` above** — that one is R4's distributed-tracing "
        "`trace_id` sample rate, an unrelated concept the name collides with; this one "
        "governs FR-259's persisted `Trace` artifacts and feeds `05-monitoring.md`. "
        "Declines and errors are always persisted regardless of this rate (FR-259's "
        "100 % floor) — `app.platform.traces.decide_sampling` applies that floor before "
        "this fraction is even consulted.",
        constraints={"min": 0.0, "max": 1.0},
        scope=SettingScope.WORKSPACE_OR_ENVIRONMENT,
    ),
    SettingDefinition(
        key="scoring.default_client_rate_limit_rps",
        type=SettingType.INT,
        default=None,
        description="`07` FR-452's default rate limit for `POST /api/v1/score`, in requests "
        "per second per (Environment, Principal), for a caller whose Service Account sets no "
        "`rate_limit_rps` of its own. Unset by default: with no limit the request is "
        "admitted without a counter call (`RL-1347` rule 2).",
        constraints={"min": 1},
        scope=SettingScope.WORKSPACE_OR_ENVIRONMENT,
    ),
    SettingDefinition(
        key="platform.default_management_rate_limit_rps",
        type=SettingType.INT,
        default=None,
        description="`07` FR-452's management-API rate limit, in requests per second per "
        "(Environment, Principal), counted across every authenticated `/api/v1` request "
        "outside the `/score` family (`RL-1687`). Unset by default: with no limit the request "
        "is admitted without a counter call. A Service Account's `rate_limit_rps` never "
        "applies to it.",
        constraints={"min": 1},
        scope=SettingScope.WORKSPACE_OR_ENVIRONMENT,
    ),
    SettingDefinition(
        key="governance.approval_policy_ref",
        type=SettingType.STRING,
        default="",
        description="Reference to the workspace's approval policy (`06` FR-354). Empty "
        "until governance is configured.",
    ),
    SettingDefinition(
        key="retention.job_history_days",
        type=SettingType.INT,
        default=400,
        description="How long Job history is kept. FR-410 requires at least 13 months; "
        "400 days is that with margin, and the floor is enforced by the constraint.",
        constraints={"min": 396},
    ),
    SettingDefinition(
        key="retention.blob_gc_grace_days",
        type=SettingType.INT,
        default=30,
        description="A blob is collectable only when unreferenced and older than this "
        "(FR-420).",
        constraints={"min": 1, "max": 3650},
    ),
    SettingDefinition(
        key="rate_tables.cell_threshold",
        type=SettingType.INT,
        default=250_000,
        description="The cell count above which a rate table version's cells spill from "
        "PostgreSQL rows to a content-addressed parquet blob (FR-232, 03 §4.2). "
        "Decided at version-creation time only and immutable with the version — a "
        "threshold change never re-homes existing versions (DP2 ruling 2026-08-28).",
        constraints={"min": 1},
    ),
    # -- feature flags (FR-449) ---------------------------------------------------
    SettingDefinition(
        key="features.expression_objectives_enabled",
        type=SettingType.BOOL,
        default=False,
        description="Custom objectives written as expressions (`02` FR-150, WF-702 "
        "Route B). Off by default: an arbitrary-code objective is a governance risk, so "
        "the safe value is the one that does not evaluate user input. OQ-573 was "
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
        "executes user-authored code against the dataset. OQ-559 was decided on "
        "2026-08-14 — the check is kept, but Admin-authored, single-Approver, and behind "
        "this flag, so a workspace that never needs the escape hatch never carries its "
        "risk.",
        feature_flag=True,
    ),
    # Environment-only (`RL-1311` item 3; `RL-1834` D2): a workspace-level write is refused and a
    # process variable never supplies one, so a flag is switched on in one Environment at a time.
    SettingDefinition(
        key="features.date_routing_enabled",
        type=SettingType.BOOL,
        default=False,
        description="Date-based routing (`03` FR-270): a default-live quote is scored by the "
        "Rating Version whose date range, in the Environment's routing rule, holds its "
        "effective date. Selection is only among versions already deployed to the "
        "Environment, so turning it on never makes an unpromoted version live.",
        feature_flag=True,
        scope=SettingScope.ENVIRONMENT,
    ),
    SettingDefinition(
        key="features.shadow_scoring_enabled",
        type=SettingType.BOOL,
        default=False,
        description="Shadow scoring (`03` FR-271): a fraction of default-live quotes is also "
        "scored against the Environment's shadow candidate after the response is sent, and "
        "the result recorded, never returned to the caller.",
        feature_flag=True,
        scope=SettingScope.ENVIRONMENT,
    ),
)

#: The safe value for each flag, recorded separately from the default so that a change to
#: one is visible as a change to the other. FR-449 requires flags to default to the
#: safe value; a test asserts the two agree, so flipping a default silently is not possible.
SAFE_DEFAULT: dict[str, bool] = {
    "features.expression_objectives_enabled": False,
    "features.sql_validation_check_enabled": False,
    "features.date_routing_enabled": False,
    "features.shadow_scoring_enabled": False,
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
        "type and constraints exist before a value does (FR-447).",
    )


def validate_setting_overrides(settings: Settings) -> None:
    """Refuse to start on a `GIP_SETTING_*` variable the registry cannot honour (FR-447).

    Run from the lifespan, so a bad override stops the process with the variable named
    rather than failing at first use. Three refusals: an unknown key, a value that does not
    parse or violates its constraints, and a key declared Environment-only (`RL-1311`
    item 3a), which a process variable never supplies.
    """
    by_variable = {_env_name(k): d for k, d in REGISTRY.items()}
    problems: list[str] = []
    for variable, raw in sorted(settings.setting_overrides.items()):
        definition = by_variable.get(variable)
        if definition is None:
            problems.append(f"  {variable}: not a declared setting")
        elif definition.scope is SettingScope.ENVIRONMENT:
            problems.append(
                f"  {variable}: {definition.key} is an Environment-only setting and a "
                "process variable never supplies one"
            )
        else:
            try:
                definition.coerce(_parse_env(definition, raw))
            except PlatformError as exc:
                problems.append(f"  {variable}: {exc.detail}")
    if problems:
        raise ConfigInvalidError(
            "setting overrides are invalid, refusing to start:\n" + "\n".join(problems)
        )


async def _environment_value(
    session: AsyncSession, environment: str | None, key: str
) -> Any:
    if environment is None:
        return None
    return (
        await session.execute(
            select(EnvironmentSettingRow.value)
            .join(EnvironmentRow, EnvironmentRow.id == EnvironmentSettingRow.environment_id)
            .where(EnvironmentRow.slug == environment, EnvironmentSettingRow.key == key)
        )
    ).scalar_one_or_none()


async def resolve(
    session: AsyncSession,
    settings: Settings,
    workspace_id: UUID | None,
    key: str,
    environment: str | None = None,
) -> SettingResolution:
    """Resolve one setting through the four layers (FR-446).

    With no `environment` the Environment layer is skipped and not reported. With no
    `workspace_id` the workspace layer is skipped (the management count of the two identity
    routes, before a workspace is selected); it is still reported, with no value.
    """
    definition = REGISTRY.get(key)
    if definition is None:
        raise _unknown(key)

    env_value = _env_candidate(settings, definition)
    environment_value = await _environment_value(session, environment, key)
    workspace_value = None
    if workspace_id is not None:
        workspace_value = (
            await session.execute(
                select(WorkspaceSettingRow.value).where(
                    WorkspaceSettingRow.workspace_id == workspace_id,
                    WorkspaceSettingRow.key == key,
                )
            )
        ).scalar_one_or_none()

    return _resolution(definition, env_value, workspace_value, environment, environment_value)


async def resolve_all(
    session: AsyncSession,
    settings: Settings,
    workspace_id: UUID,
    environment: str | None = None,
) -> list[SettingResolution]:
    """Resolve every declared setting. One query per layer, not one per key."""
    rows = (
        await session.execute(
            select(WorkspaceSettingRow.key, WorkspaceSettingRow.value).where(
                WorkspaceSettingRow.workspace_id == workspace_id
            )
        )
    ).all()
    overrides: dict[str, Any] = {row[0]: row[1] for row in rows}
    environment_overrides: dict[str, Any] = {}
    if environment is not None:
        environment_overrides = {
            row[0]: row[1]
            for row in (
                await session.execute(
                    select(EnvironmentSettingRow.key, EnvironmentSettingRow.value)
                    .join(
                        EnvironmentRow,
                        EnvironmentRow.id == EnvironmentSettingRow.environment_id,
                    )
                    .where(EnvironmentRow.slug == environment)
                )
            ).all()
        }
    return [
        _resolution(
            d,
            _env_candidate(settings, d),
            overrides.get(key),
            environment,
            environment_overrides.get(key),
        )
        for key, d in sorted(REGISTRY.items())
    ]


def _env_candidate(settings: Settings, definition: SettingDefinition) -> Any:
    raw = settings.setting_overrides.get(_env_name(definition.key))
    if raw is None:
        return None
    if definition.scope is SettingScope.ENVIRONMENT:
        # RL-1311 item 3a: startup refuses this, so seeing it here means the variable
        # appeared after startup. Skipped, and the variable named; its value is not logged.
        _log.warning(
            "ignoring %s: %s is an Environment-only setting", _env_name(definition.key),
            definition.key,
        )
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
            f"{_env_name(definition.key)} cannot be parsed as {definition.type.value}",
        ) from exc


def _resolution(
    definition: SettingDefinition,
    env_value: Any,
    workspace_value: Any,
    environment: str | None = None,
    environment_value: Any = None,
) -> SettingResolution:
    if workspace_value is not None:
        workspace_value = definition.coerce(workspace_value)
    if environment_value is not None:
        environment_value = definition.coerce(environment_value)

    if env_value is not None:
        effective, source = env_value, SettingSource.ENV
    elif environment_value is not None:
        effective, source = environment_value, SettingSource.ENVIRONMENT_SETTING
    elif workspace_value is not None:
        effective, source = workspace_value, SettingSource.WORKSPACE
    else:
        effective, source = definition.default, SettingSource.DEFAULT

    candidates = [SettingCandidate(source=SettingSource.ENV, value=env_value)]
    if environment is not None:
        candidates.append(
            SettingCandidate(source=SettingSource.ENVIRONMENT_SETTING, value=environment_value)
        )
    candidates += [
        SettingCandidate(source=SettingSource.WORKSPACE, value=workspace_value),
        SettingCandidate(source=SettingSource.DEFAULT, value=definition.default),
    ]
    return SettingResolution(
        key=definition.key,
        effective_value=effective,
        resolved_from=source,
        candidates=tuple(candidates),
        type=definition.type,
        constraints=definition.constraints,
        feature_flag=definition.feature_flag,
        description=definition.description,
    )


async def set_workspace_setting(
    session: AsyncSession, workspace_id: UUID, key: str, value: Any
) -> SettingDefinition:
    """Write a workspace override, validating it first (FR-447).

    The caller audits the change; this function does not, because the audit event needs the
    actor and the before-value, and passing both here would put the governance decision in
    the persistence layer.
    """
    definition = REGISTRY.get(key)
    if definition is None:
        raise _unknown(key)
    if definition.scope is SettingScope.ENVIRONMENT:
        raise PlatformError(
            "SETTING_INVALID",
            "Setting cannot be set at workspace level",
            422,
            f"{key}: declared Environment-only (FR-446), so it takes a value per Environment.",
        )

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


async def require_environment(session: AsyncSession, slug: str) -> UUID:
    """The id of the Environment with this slug, retired ones included, or a 404."""
    environment_id = (
        await session.execute(select(EnvironmentRow.id).where(EnvironmentRow.slug == slug))
    ).scalar_one_or_none()
    if environment_id is None:
        raise PlatformError(
            "NOT_FOUND", "Environment not found", 404, f"No environment with slug {slug!r}."
        )
    return environment_id


async def set_environment_setting(
    session: AsyncSession,
    environment: str,
    key: str,
    value: Any,
    updated_by: UUID | None,
) -> tuple[SettingDefinition, Any]:
    """Write an Environment setting, validating it first (FR-431, FR-446, FR-447).

    Returns the definition and the value the Environment held before (`None` when unset), for
    the caller's audit event: as with `set_workspace_setting`, the caller audits.
    """
    definition = REGISTRY.get(key)
    if definition is None:
        raise _unknown(key)
    if definition.scope is SettingScope.WORKSPACE:
        raise PlatformError(
            "SETTING_INVALID",
            "Setting cannot be set at Environment level",
            422,
            f"{key}: declared workspace-only (FR-446), so it takes no Environment value.",
        )
    coerced = definition.coerce(value)

    environment_id = await require_environment(session, environment)
    row = (
        await session.execute(
            select(EnvironmentSettingRow).where(
                EnvironmentSettingRow.environment_id == environment_id,
                EnvironmentSettingRow.key == key,
            )
        )
    ).scalar_one_or_none()
    before = None if row is None else row.value
    if row is None:
        session.add(
            EnvironmentSettingRow(
                environment_id=environment_id, key=key, value=coerced, updated_by=updated_by
            )
        )
    else:
        row.value = coerced
        row.updated_by = updated_by
        row.updated_at = func.now()
    await session.flush()
    return definition, before
