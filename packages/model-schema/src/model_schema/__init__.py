"""Single source of truth for every shape crossing a module boundary (ADR-0002).

Depends on Pydantic and nothing else. No SQLAlchemy, no FastAPI, no Polars — the
`.importlinter` contract enforces it, because a convenience import here would quietly make
this package un-generatable and un-shareable.
"""

from model_schema.audit import (
    AuditEvent,
    AuditEventCore,
    canonical_payload,
    compute_event_hash,
)
from model_schema.envelope import ArtifactEnvelope
from model_schema.ids import new_uuid7, uuid7_timestamp_ms
from model_schema.jobs import (
    TERMINAL_STATUSES,
    VALID_TRANSITIONS,
    ActorKind,
    Job,
    JobError,
    JobKind,
    JobQueue,
    JobResult,
    JobSource,
    JobStatus,
    Principal,
    Progress,
    ResourceBudget,
    RetryPolicy,
    RetryState,
)
from model_schema.money import Currency, DecimalStr, MoneyMinor, Relativity, apply_factor, to_minor
from model_schema.permissions import (
    BUILTIN_ROLES,
    READ_PERMISSIONS,
    Permission,
    ScopeType,
    role_permissions,
)
from model_schema.problem import FieldError, ProblemDetail
from model_schema.refs import ARTIFACT_TYPES, ArtifactRef, BlobRef, Slug
from model_schema.settings import (
    SettingCandidate,
    SettingResolution,
    SettingSource,
    SettingType,
)

__all__ = [
    "ARTIFACT_TYPES",
    "BUILTIN_ROLES",
    "READ_PERMISSIONS",
    "TERMINAL_STATUSES",
    "VALID_TRANSITIONS",
    "ActorKind",
    "ArtifactEnvelope",
    "ArtifactRef",
    "AuditEvent",
    "AuditEventCore",
    "BlobRef",
    "Currency",
    "DecimalStr",
    "FieldError",
    "Job",
    "JobError",
    "JobKind",
    "JobQueue",
    "JobResult",
    "JobSource",
    "JobStatus",
    "MoneyMinor",
    "Permission",
    "Principal",
    "ProblemDetail",
    "Progress",
    "Relativity",
    "ResourceBudget",
    "RetryPolicy",
    "RetryState",
    "ScopeType",
    "SettingCandidate",
    "SettingResolution",
    "SettingSource",
    "SettingType",
    "Slug",
    "apply_factor",
    "canonical_payload",
    "compute_event_hash",
    "new_uuid7",
    "role_permissions",
    "to_minor",
    "uuid7_timestamp_ms",
]
