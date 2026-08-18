"""ORM models for the platform tables (FR-PLAT-17).

Three tables, and the relationship between them is the point of this module:

* `jobs` — the tracked unit of work (FR-PLAT-7).
* `audit_events` — append-only, hash-chained, written in the caller's transaction (`06` R2).
* `outbox` — the transactional outbox that makes Celery enqueue safe (FR-PLAT-51).

All three are written by the *same* transaction. That is what makes the guarantee real:
either a job exists, its audit event exists, and its publish intent exists — or none do.
"""

from __future__ import annotations

import enum
from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Float,
    Identity,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID  # noqa: N811
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from model_schema import JobKind, JobQueue, JobSource, JobStatus, new_uuid7

__all__ = [
    "AcknowledgementRow",
    "ApiKeyRow",
    "ApprovalDecisionRow",
    "ApprovalPolicyRow",
    "ApprovalRequestRow",
    "AuditEventRow",
    "BlobRow",
    "DatasetRow",
    "DatasetSplitRow",
    "DatasetVersionRow",
    "DiagnosticsRow",
    "IngestionRunRow",
    "JobLogRow",
    "JobRow",
    "OutboxRow",
    "OutboxStatus",
    "ReferenceRowRow",
    "ReferenceTableRow",
    "ReferenceTableVersionRow",
    "RoleAssignmentRow",
    "RoleRow",
    "ServiceAccountRow",
    "SourceRow",
    "SubjectPurgeRow",
    "UserRow",
    "WorkspaceMemberRow",
    "WorkspaceSettingRow",
]


def _pg_enum(python_enum: type[enum.Enum], name: str, *, create: bool = True) -> Enum:
    """A PostgreSQL enum keyed by the member *value*, not the member name.

    Without `values_callable`, SQLAlchemy stores `MODEL_FIT` while the API, the contract
    and every log line say `model.fit`. The mismatch only surfaces when someone queries the
    database directly and finds a vocabulary nothing else uses.
    """
    return Enum(
        python_enum,
        name=name,
        values_callable=lambda e: [m.value for m in e],
        create_type=create,
    )


class JobRow(Base):
    """A Job (`07` §4.1). The lifecycle itself is enforced in the service layer."""

    __tablename__ = "jobs"

    # UUIDv7 (ID-1): time-ordered, so inserts append to the index instead of scattering
    # across it. On the audit table — append-only and the largest in the system — that is
    # the difference between a hot index and a cold one.
    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    kind: Mapped[JobKind] = mapped_column(_pg_enum(JobKind, "job_kind"), nullable=False)
    status: Mapped[JobStatus] = mapped_column(_pg_enum(JobStatus, "job_status"), nullable=False)
    queue: Mapped[JobQueue] = mapped_column(_pg_enum(JobQueue, "job_queue"), nullable=False)
    source: Mapped[JobSource] = mapped_column(_pg_enum(JobSource, "job_source"), nullable=False)

    submitted_by: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(255))
    parameters: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    progress: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    error: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    resource_budget: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    retries: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    trace_id: Mapped[str | None] = mapped_column(String(32))

    queued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Cooperative cancellation (FR-PLAT-9): the API sets this, and the worker's progress
    # callback observes it at the next checkpoint. A separate column from `status` because
    # a running job stays `running` until it actually stops — reporting `cancelled` while
    # the work is still burning CPU is how a cancelled job appears to have freed a slot it
    # has not.
    cancellation_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # NFR-PLAT-3: a running job with no progress for longer than the configured window is
    # treated as stalled. That needs the time of the last *progress report*, which is not
    # `started_at` and not `queued_at` — a job can run for an hour legitimately, and the
    # question is whether it is still saying anything.
    progress_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        # FR-PLAT-12: a repeat submission within the window returns the original job.
        # Partial, because most jobs carry no key — and NULLs never conflict in a unique
        # index anyway, so the predicate keeps the index small rather than changing meaning.
        Index(
            "uq_jobs_workspace_id_idempotency_key",
            "workspace_id",
            "idempotency_key",
            unique=True,
            postgresql_where=idempotency_key.isnot(None),
        ),
        Index("ix_jobs_workspace_id_status", "workspace_id", "status"),
        Index("ix_jobs_queue_status", "queue", "status"),
        CheckConstraint(
            "(status IN ('succeeded','failed','cancelled')) = (finished_at IS NOT NULL)",
            name="terminal_iff_finished",
        ),
        CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="finished_after_started",
        ),
        CheckConstraint(
            "trace_id IS NULL OR trace_id ~ '^[0-9a-f]{32}$'",
            name="trace_id_is_w3c_hex",
        ),
    )


class AuditEventRow(Base):
    """An Audit Event (`06` §4.5).

    **Never updated, never deleted.** FR-GOV-22 enforces that at the database privilege
    level; the migration revokes `UPDATE`/`DELETE` from the application role and installs a
    trigger that rejects both. The ORM offers no update path, but the ORM is not the
    protection — a privilege is.
    """

    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    actor: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    source: Mapped[JobSource] = mapped_column(
        _pg_enum(JobSource, "job_source", create=False), nullable=False
    )
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_ref: Mapped[str] = mapped_column(String(512), nullable=False)

    before: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    justification: Mapped[str | None] = mapped_column(Text)

    trace_id: Mapped[str | None] = mapped_column(String(32))
    job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    # The chain (FR-GOV-24). `prev_event_hash` is null only for a workspace's first event.
    prev_event_hash: Mapped[str | None] = mapped_column(String(71))
    event_hash: Mapped[str] = mapped_column(String(71), nullable=False)

    # Monotonic per workspace, assigned under the chain lock. Ordering by `at` is not
    # enough: two events in the same millisecond have no defined order, and a chain whose
    # order cannot be reconstructed cannot be verified.
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("workspace_id", "sequence", name="uq_audit_events_workspace_sequence"),
        UniqueConstraint("event_hash", name="uq_audit_events_event_hash"),
        Index("ix_audit_events_workspace_id_at", "workspace_id", "at"),
        Index("ix_audit_events_entity_ref", "entity_ref"),
        Index("ix_audit_events_action", "action"),
        CheckConstraint("event_hash ~ '^sha256:[a-f0-9]{64}$'", name="event_hash_format"),
        CheckConstraint(
            "prev_event_hash IS NULL OR prev_event_hash ~ '^sha256:[a-f0-9]{64}$'",
            name="prev_event_hash_format",
        ),
        CheckConstraint("sequence >= 1", name="sequence_positive"),
    )


class OutboxStatus(enum.StrEnum):
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"


class OutboxRow(Base):
    """A publish intent, written in the caller's transaction (FR-PLAT-51).

    Celery does not enlist in the database transaction: a task published to Redis survives
    a rollback, leaving a worker acting on state that was never committed — and, because
    audit writes share that transaction, doing so with no audit record.

    So nothing is published from inside a transaction. The intent is *written* with the
    change, and a relay publishes it after commit. The cost is at-least-once delivery,
    which is why the consumer is keyed by `job_id` and must be idempotent.
    """

    __tablename__ = "outbox"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    job_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    queue: Mapped[JobQueue] = mapped_column(
        _pg_enum(JobQueue, "job_queue", create=False), nullable=False
    )
    task: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    status: Mapped[OutboxStatus] = mapped_column(
        _pg_enum(OutboxStatus, "outbox_status"), nullable=False, default=OutboxStatus.PENDING
    )
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        # The relay's only query: oldest pending first. Partial, because published rows
        # dominate the table within minutes and must not be scanned.
        Index(
            "ix_outbox_pending_created_at",
            "created_at",
            postgresql_where=status == OutboxStatus.PENDING,
        ),
        UniqueConstraint("job_id", name="uq_outbox_job_id"),
        CheckConstraint(
            "(status = 'published') = (published_at IS NOT NULL)",
            name="published_iff_timestamped",
        ),
    )


class BlobRow(Base):
    """The PostgreSQL side of a content-addressed blob (FR-PLAT-18).

    The object body lives in S3 at `blob/{sha256[:2]}/{sha256}`; size, media type and
    **reference count** live here, because a reference count is a transactional quantity
    and S3 has no transactions.

    The primary key is the digest itself. That is what makes FR-PLAT-19 free rather than
    something to remember: writing identical content twice is a primary-key conflict, not
    a second object.
    """

    __tablename__ = "blobs"

    sha256: Mapped[str] = mapped_column(String(64), primary_key=True)
    bytes_: Mapped[int] = mapped_column("bytes", BigInteger, nullable=False)
    media_type: Mapped[str] = mapped_column(String(255), nullable=False)
    part_count: Mapped[int | None] = mapped_column(Integer)

    # FR-PLAT-20. Incremented when an artifact takes a reference, decremented when one is
    # released. GC only ever considers rows at zero — and even then, only old ones.
    ref_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint("sha256 ~ '^[a-f0-9]{64}$'", name="sha256_is_lowercase_hex"),
        CheckConstraint("bytes >= 0", name="bytes_non_negative"),
        # A negative reference count means a release without a matching retain — a bug
        # that would otherwise surface as a deleted blob some weeks later, with nothing
        # left to explain it.
        CheckConstraint("ref_count >= 0", name="ref_count_non_negative"),
        Index("ix_blobs_ref_count_created_at", "ref_count", "created_at"),
    )


class JobLogRow(Base):
    """One captured log line for a Job (FR-PLAT-10).

    Retained with the Job and carrying its `trace_id`, so "what happened in this run?" is
    answerable from the Job page rather than by correlating timestamps against a cluster's
    log aggregator — which the actuary reading the failure does not have access to.

    **Secrets must never reach this table** (R3, FR-GOV-26). Only the formatted message is
    stored, never a record's arbitrary attributes, so a structured field holding a
    credential cannot be swept in by accident.
    """

    __tablename__ = "job_logs"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)

    # Insertion order, assigned by the database. **Not** the UUIDv7 id: two ids generated
    # in the same millisecond have no defined order relative to each other (see
    # `model_schema.ids`), and `at` ties too because every row written in one transaction
    # shares its transaction timestamp. Ordering log lines by either returns them
    # scrambled, which was the first thing the API test caught.
    seq: Mapped[int] = mapped_column(BigInteger, Identity(), nullable=False, unique=True)

    job_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    level: Mapped[str] = mapped_column(String(16), nullable=False)
    logger: Mapped[str] = mapped_column(String(128), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(32))

    __table_args__ = (
        # The only query: one job's lines in insertion order.
        Index("ix_job_logs_job_id_seq", "job_id", "seq"),
    )


class UserRow(Base):
    """A platform user, created on first login from identity-provider claims (FR-PLAT-4).

    **No password column, and there never will be one** — FR-PLAT-1 puts authentication
    entirely with the identity provider. `subject` is the provider's `sub` claim, which is
    stable across email changes; keying on email instead would silently reassign a user's
    history when they change name.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    issuer: Mapped[str] = mapped_column(String(512), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320))
    display_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        # Scoped to the issuer: two providers may legitimately use the same `sub`.
        UniqueConstraint("issuer", "subject", name="uq_users_issuer_subject"),
    )


class ServiceAccountRow(Base):
    """A non-human principal (`07` §4.3, FR-PLAT-3)."""

    __tablename__ = "service_accounts"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # FR-PLAT-3: scoped to named environments and the scoring permission set only. A `uat`
    # key can never score against `prod` (FR-PLAT-30), and that is enforced by comparing
    # this list, not by trusting the environment embedded in the key string.
    environments: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    permissions: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    rate_limit_rps: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("workspace_id", "slug", name="uq_service_accounts_workspace_slug"),
    )


class ApiKeyRow(Base):
    """One key belonging to a Service Account.

    The **secret is never stored** — only its hash (FR-PLAT-3). The prefix is stored in
    clear so a leaked key can be identified and revoked from the prefix alone, without
    anyone holding the secret.

    Several rows may be active for one account at once: that is the rotation overlap
    window, which lets a deployment pick up the new key before the old one stops working.
    """

    __tablename__ = "api_keys"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    service_account_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    secret_hash: Mapped[str] = mapped_column(String(71), nullable=False)
    environment: Mapped[str] = mapped_column(String(32), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("prefix", name="uq_api_keys_prefix"),
        Index("ix_api_keys_service_account_id", "service_account_id"),
        CheckConstraint("secret_hash ~ '^sha256:[a-f0-9]{64}$'", name="secret_hash_format"),
    )


class WorkspaceMemberRow(Base):
    """Which workspaces a user may act in.

    FR-PLAT-4: *a user with no mapped role gets no access, not default access.* Roles
    themselves belong to `06` and arrive with W3; this is the coarsest form of the same
    rule, and the one W2 can enforce honestly — an authenticated user with no membership
    row can reach no workspace at all.

    There is deliberately **no API to create these in W2**. Self-service membership would
    make authentication sufficient for access, which is precisely what FR-PLAT-4 forbids.
    Provisioning arrives with the governance write path (W3, FR-GOV-4).
    """

    __tablename__ = "workspace_members"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "workspace_id", name="uq_workspace_members_user_workspace"),
        Index("ix_workspace_members_user_id", "user_id"),
    )


class WorkspaceSettingRow(Base):
    """A workspace-level override for one setting (FR-PLAT-43, FR-PLAT-45).

    The middle layer of the precedence chain: an environment variable still wins, and the
    platform default still applies when no row exists. Only overrides are stored — writing
    a row for every setting in every workspace would make the platform default
    unchangeable in practice, because nothing would ever fall through to it.
    """

    __tablename__ = "workspace_settings"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    key: Mapped[str] = mapped_column(String(128), nullable=False)

    # JSONB rather than text: a setting is typed (FR-PLAT-44), and storing 0.10 as "0.10"
    # would put the parsing — and the chance of parsing it differently in two places — on
    # every reader.
    value: Mapped[Any] = mapped_column(JSONB, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("workspace_id", "key", name="uq_workspace_settings_workspace_key"),
    )


class RoleRow(Base):
    """A role: a named set of permissions (FR-GOV-3).

    Built-in roles are seeded per workspace from `model_schema.BUILTIN_ROLES` rather than
    referenced by name, so a workspace can *see* what its Approver role grants and a custom
    role sits beside them in the same table. Seeding a copy also means changing the shipped
    defaults never silently changes what an existing workspace's approvers can do — which
    would be a permission change with no audit event.
    """

    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    permissions: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (UniqueConstraint("workspace_id", "slug", name="uq_roles_workspace_slug"),)


class RoleAssignmentRow(Base):
    """A role granted to a principal, within a scope (FR-GOV-4, FR-GOV-8).

    Scope is what stops a motor actuary approving home pricing: an assignment is
    workspace-wide only when someone chose that, and otherwise names one Dataset, Model
    Family or Rating Algorithm.

    **Break-glass is the same row with an expiry and a reason** (FR-GOV-8) rather than a
    separate mechanism. One table means one place where expiry is checked; a parallel
    emergency-grant table is a second path into the same decision, and the second path is
    the one that gets forgotten when the check is tightened.
    """

    __tablename__ = "role_assignments"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    principal_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    principal_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    role_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    scope_type: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    granted_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Break-glass (FR-GOV-8): time-boxed, reason-required, prominently flagged.
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reason: Mapped[str | None] = mapped_column(Text)
    break_glass: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_role_assignments_principal", "workspace_id", "principal_id"),
        # A scoped assignment names its resource; a workspace-wide one must not, or the
        # scope means two different things depending on which column you read.
        CheckConstraint(
            "(scope_type = 'workspace') = (scope_id IS NULL)",
            name="scope_id_iff_scoped",
        ),
        # FR-GOV-8: an emergency grant with no expiry is a permanent grant with a story.
        CheckConstraint(
            "NOT break_glass OR (expires_at IS NOT NULL AND reason IS NOT NULL)",
            name="break_glass_is_time_boxed_and_justified",
        ),
    )


class ApprovalRequestRow(Base):
    """An artifact submitted for approval (`06` §4.3, FR-GOV-9).

    `artifact_ref` is the canonical `{type}:{slug}@{version}` string, which is what makes
    approvals pinned without a staleness check (FR-GOV-14): artifacts are immutable
    (FR-OVR-1), so a changed artifact is a *different* reference and this row does not
    describe it.
    """

    __tablename__ = "approval_requests"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    artifact_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False)
    environment: Mapped[str | None] = mapped_column(String(32))

    submitted_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    change_summary: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(32), nullable=False)
    approvers_required: Mapped[int] = mapped_column(Integer, nullable=False)

    withdrawn_reason: Mapped[str | None] = mapped_column(Text)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        # One open request per artifact version. A second would let two reviews of the same
        # thing reach different answers, with nothing to say which one deployment obeys.
        Index(
            "uq_approval_requests_open_artifact",
            "workspace_id",
            "artifact_ref",
            unique=True,
            postgresql_where=status.in_(("draft", "review")),
        ),
        Index("ix_approval_requests_workspace_status", "workspace_id", "status"),
        CheckConstraint("approvers_required >= 1", name="approvers_required_positive"),
    )


class ApprovalDecisionRow(Base):
    """One approver's decision on one request (FR-GOV-11).

    The unique constraint on `(request, approver)` is separation of duties made structural:
    "where two approvals are required they must be distinct Principals" is not a rule the
    service can forget, because a second decision from the same person cannot be stored.
    """

    __tablename__ = "approval_decisions"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    request_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    approver_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("request_id", "approver_id", name="uq_approval_decisions_one_each"),
        Index("ix_approval_decisions_request", "request_id"),
    )


class ApprovalPolicyRow(Base):
    """The workspace's approval policy (FR-GOV-12). One row per workspace."""

    __tablename__ = "approval_policies"

    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    policy: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class SourceRow(Base):
    """Where a Dataset's data comes from (FR-DATA-1).

    `credentials_secret_ref` holds a `secret:<slug>` **reference**, never a value
    (`07` FR-PLAT-25/26). The column is deliberately named for what it stores, so a future
    reader cannot mistake it for somewhere a password may go.
    """

    __tablename__ = "sources"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    credentials_secret_ref: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("workspace_id", "slug", name="uq_sources_workspace_slug"),
        # R3: a secret reference, not a secret. `secret:` is the only accepted form.
        CheckConstraint(
            "credentials_secret_ref IS NULL OR credentials_secret_ref LIKE 'secret:%'",
            name="credentials_are_referenced_not_stored",
        ),
    )


class DatasetRow(Base):
    """A named body of data with versions (`01` §4.1)."""

    __tablename__ = "datasets"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    description: Mapped[str | None] = mapped_column(Text)

    line_of_business: Mapped[str | None] = mapped_column(String(64))
    territory: Mapped[str | None] = mapped_column(String(64))
    #: `07` FR-PLAT-46 sets the workspace default; a dataset may differ, because a group
    #: writing GB and IE business holds both in one workspace.
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GBP")
    default_record_grain: Mapped[str | None] = mapped_column(String(32))

    #: Authored, not inferred (`01` §4.1). A Profile can say a column is 98 % distinct
    #: integers; only a person can say it is a special category.
    data_dictionary: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    validation_rule_set_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("workspace_id", "slug", name="uq_datasets_workspace_slug"),
        CheckConstraint("currency ~ '^[A-Z]{3}$'", name="currency_is_iso_4217"),
    )


class DatasetVersionRow(Base):
    """An immutable snapshot (`01` §4.2, FR-DATA-2, FR-DATA-40).

    Two constraints carry `01` §1.3 — *a Model may only be fitted on a `validated`
    version* — down to where it cannot be argued with:

    * `version` is unique per dataset and never reused (ID-2), so a reference to `@12`
      means one body of data for ever.
    * `validated` requires `validation_report_id`. The report's *contents* are checked by
      the service; that it exists at all is checked here, because a validated version with
      no report is the state that would let the gate be skipped by an UPDATE.
    """

    __tablename__ = "dataset_versions"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[str] = mapped_column(String(32), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="ingested")

    tables: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    source_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    source_fingerprint: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    ingestion_run_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    preparation_recipe_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    period_from: Mapped[date | None] = mapped_column(Date)
    period_to: Mapped[date | None] = mapped_column(Date)
    totals: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    validation_report_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    profile_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    derived_from: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    library_versions: Mapped[dict[str, str]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("dataset_id", "version", name="uq_dataset_versions_dataset_version"),
        Index("ix_dataset_versions_workspace_status", "workspace_id", "status"),
        CheckConstraint("version >= 1", name="version_starts_at_one"),
        CheckConstraint(
            "status <> 'validated' OR validation_report_id IS NOT NULL",
            name="validated_names_its_report",
        ),
        CheckConstraint(
            "kind <> 'derived' OR derived_from IS NOT NULL",
            name="derived_names_its_parent",
        ),
        CheckConstraint(
            "period_to IS NULL OR period_from IS NULL OR period_to >= period_from",
            name="period_is_ordered",
        ),
    )


class IngestionRunRow(Base):
    """What one ingestion did (FR-DATA-6, FR-DATA-8).

    Kept whether the run succeeded or failed. A failed run that leaves no record is a
    question nobody can answer later — "why is there no version 12?" — and FR-DATA-6's list
    is precisely the evidence needed to answer it: what was read, what was written, what
    was rejected and why, and which build of which libraries did it.
    """

    __tablename__ = "ingestion_runs"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_version_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    source_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    status: Mapped[str] = mapped_column(String(32), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(255))

    # FR-DATA-8: the same key with a *changed* source is a different ingestion, so the
    # fingerprint is part of the identity rather than a detail recorded beside it.
    source_fingerprint: Mapped[str | None] = mapped_column(String(128))

    rows_read: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_written: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reject_sample: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    bytes_read: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    library_versions: Mapped[dict[str, str]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    error: Mapped[str | None] = mapped_column(Text)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index(
            "uq_ingestion_runs_idempotency",
            "workspace_id",
            "dataset_id",
            "idempotency_key",
            "source_fingerprint",
            unique=True,
            postgresql_where=idempotency_key.isnot(None),
        ),
        Index("ix_ingestion_runs_dataset", "dataset_id"),
        CheckConstraint("rows_read >= 0 AND rows_written >= 0 AND rows_rejected >= 0",
                        name="row_counts_non_negative"),
    )


class ReferenceTableRow(Base):
    """An effective-dated lookup table (FR-DATA-29)."""

    __tablename__ = "reference_tables"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    key_columns: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    payload_columns: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("workspace_id", "slug", name="uq_reference_tables_workspace_slug"),
    )


class ReferenceTableVersionRow(Base):
    """An immutable, independently approvable version (FR-DATA-30).

    Pinned explicitly by both validation and the rating engine — never "latest". A lookup
    that silently followed the newest version would change a quote's answer without any
    artifact changing, which is the one thing a rating version's immutability exists to
    prevent.
    """

    __tablename__ = "reference_table_versions"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    reference_table_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    source_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("reference_table_id", "version", name="uq_reference_versions"),
        CheckConstraint("version >= 1", name="reference_version_starts_at_one"),
    )


class ReferenceRowRow(Base):
    """One effective-dated row of a reference version (FR-DATA-29).

    The half-open `[effective_from, effective_to)` interval and the exclusion constraint
    below are what make "as at" lookups single-valued. Overlapping intervals for one key
    mean a lookup has two answers, and which one a quote gets would depend on row order —
    a rating difference nobody could reproduce.
    """

    __tablename__ = "reference_rows"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    reference_table_version_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), nullable=False
    )
    key: Mapped[str] = mapped_column(String(256), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    #: NULL means open-ended. The exclusion constraint treats it as infinity.
    effective_to: Mapped[date | None] = mapped_column(Date)

    __table_args__ = (
        Index("ix_reference_rows_version_key", "reference_table_version_id", "key"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="effective_interval_is_ordered",
        ),
    )


class ValidationReportRow(Base):
    """One validation run's result (`01` §4.6, FR-DATA-15, FR-DATA-20).

    The report **is** the artifact: the body is the `ValidationReport` model serialised
    whole, not a shredded set of columns to be reassembled. Two reasons, and both are
    about disputes. A report is evidence that a version was or was not fit to model on,
    and evidence that the platform rewrote on read — because a column was added, or an
    enum gained a member — is not evidence. And NFR-DATA-5 requires byte-identical bodies
    across runs, which can only be checked against a body that was stored as bytes.

    The summary columns beside it are indexes, never the source of truth. `overall` is
    stored because "show me every version that failed validation" must not deserialise
    every report in the workspace to answer.
    """

    __tablename__ = "validation_reports"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_version_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    rule_set_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    rule_set_version: Mapped[int] = mapped_column(Integer, nullable=False)
    job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    # 24, not 16: 'pass_with_warnings' is 18 characters. The narrower column accepted every
    # verdict except the one a report with warnings actually gets.
    overall: Mapped[str] = mapped_column(String(24), nullable=False)
    rule_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warn_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    body: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_validation_reports_version", "dataset_version_id", "created_at"),
        CheckConstraint("finished_at >= started_at", name="report_is_ordered"),
        CheckConstraint(
            "rule_count >= fail_count + warn_count + error_count",
            name="counts_do_not_exceed_the_rules",
        ),
    )


class AcknowledgementRow(Base):
    """An actuary accepting a `warn` (FR-DATA-17, FR-DATA-18).

    Scoped to `(dataset_version_id, rule_id, report_id)` by a unique constraint, which is
    FR-DATA-18's rule made unarguable: an acknowledgement does not carry forward to the
    next version or the next report. Re-running validation asks the question again, which
    is the entire point — a warn that was acceptable on last month's data is a fresh
    judgement on this month's.
    """

    __tablename__ = "validation_acknowledgements"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_version_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    report_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    rule_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    acknowledged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "report_id", "rule_id", name="uq_acknowledgement_scope"
        ),
        Index("ix_acknowledgements_version", "dataset_version_id"),
        CheckConstraint("length(justification) > 0", name="justification_is_not_empty"),
    )


class ProfileRow(Base):
    """A dataset version's profile (`01` §4.7, FR-DATA-25, FR-DATA-27).

    Stored whole for the same reason as a validation report, plus one of its own:
    FR-DATA-27 forbids the UI recomputing a one-way, and NFR-DATA-4 gives it 300 ms. Both
    are only true if the answer is *read*. A profile assembled from normalised rows on
    each request is a recomputation with extra steps.
    """

    __tablename__ = "profiles"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_version_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    row_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    body: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_profiles_version", "dataset_version_id", "created_at"),
        CheckConstraint("row_count >= 0", name="profile_row_count_is_not_negative"),
    )


class ValidationRuleRow(Base):
    """A custom validation rule, versioned and governed (FR-DATA-21, §4.5).

    `(slug, version)` is unique per workspace and an approved row is never edited —
    `01` §4.5 step 4 makes an edit a new version needing its own approval. A rule is what
    a report's verdict *means*, so a rule mutated after the fact silently rewrites the
    meaning of every report that cites it.

    `authored_by` is kept beside `status` because §4.5 step 3 requires the approver not be
    the author, and an approval check that cannot see the author cannot enforce it.
    """

    __tablename__ = "validation_rules"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    layer: Mapped[str] = mapped_column(String(32), nullable=False)
    check: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    body: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")
    authored_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    approved_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    dry_run_report_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("workspace_id", "slug", "version", name="uq_validation_rule_version"),
        CheckConstraint("version >= 1", name="rule_version_starts_at_one"),
        # §4.5 step 2: approval requires a dry run, and step 3 requires an approver who is
        # not the author. Both are enforced by the service; the pair that cannot be
        # expressed any other way is enforced here.
        CheckConstraint(
            "status <> 'approved' OR (approved_by IS NOT NULL "
            "AND approved_by <> authored_by AND dry_run_report_id IS NOT NULL)",
            name="approved_rule_dry_run_and_separate_approver",
        ),
    )


class ValidationRuleSetRow(Base):
    """The rule set a dataset is validated against (FR-DATA-22).

    Versioned, because a Validation Report records the exact `rule_set_version` it ran.
    Without that a report says "it passed" without saying what it passed, and the two
    readings — "passed our rules" and "passed the rules we had in March" — differ exactly
    when someone is asking why a model was allowed.
    """

    __tablename__ = "validation_rule_sets"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    body: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    reference_dataset_version_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="approved")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("workspace_id", "slug", "version", name="uq_rule_set_version"),
        CheckConstraint("version >= 1", name="rule_set_version_starts_at_one"),
    )


class SubjectPurgeRow(Base):
    """A GDPR erasure of a pseudonymous subject token (FR-DATA-39).

    The purge is recorded even though the data is gone — especially because it is. An
    erasure with no record is indistinguishable from data that was never there, and a
    regulator asking "did you action this request?" needs an answer that is not a shrug.
    """

    __tablename__ = "subject_purges"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    subject_token: Mapped[str] = mapped_column(String(64), nullable=False)
    requested_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    versions_affected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    purged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_subject_purges_dataset", "workspace_id", "dataset_id"),
    )


class DatasetSplitRow(Base):
    """A named train/test split, recorded on the **parent** version (FR-DATA-36).

    On the parent, not the parts, so that two models can be compared on provably identical
    data: "trained on the same split" is then a single reference both models cite, rather
    than two derivations that were *believed* to match. A split recorded on the parts would
    make that claim unverifiable the moment either part was rebuilt.
    """

    __tablename__ = "dataset_splits"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    parent_version_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    method: Mapped[str] = mapped_column(String(32), nullable=False)
    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    params: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    parts: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("parent_version_id", "name", name="uq_dataset_splits_parent_name"),
    )


class FactorRow(Base):
    """A Factor definition, versioned independently of any Model (`02` FR-MODEL-1/7).

    Keyed to a **Dataset**, not a version: FR-MODEL-2 makes resolution against a specific
    version a fit-time act, so a factor outlives the version it was first used on.
    """

    __tablename__ = "factors"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    body: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("workspace_id", "slug", "version", name="uq_factors_slug_version"),
        CheckConstraint("version >= 1", name="factor_version_starts_at_one"),
        Index("ix_factors_dataset", "workspace_id", "dataset_id"),
    )


class BandingRow(Base):
    """A Banding, versioned independently of any Factor (`02` FR-MODEL-12).

    Same shape as `FactorRow` and for the same reason: editing a banding creates a new
    version and does not alter any Model already fitted with the old one. The body is the
    whole artifact as JSON — boundaries, labels, policies and the derivation evidence —
    because `model-schema` owns that shape (ADR-0002) and a second column-per-field
    definition here is the divergence `CLAUDE.md` §2 forbids.
    """

    __tablename__ = "bandings"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    column_name: Mapped[str] = mapped_column(String(128), nullable=False)
    body: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("workspace_id", "slug", "version", name="uq_bandings_slug_version"),
        CheckConstraint("version >= 1", name="banding_version_starts_at_one"),
        Index("ix_bandings_dataset", "workspace_id", "dataset_id"),
    )


class GroupingRow(Base):
    """A Grouping, versioned like a Banding (`02` FR-MODEL-13..17).

    `parent_grouping_id` carries FR-MODEL-17's chain — outcode rolled to area rolled to
    region — so the finer level stays available for diagnostics while rating happens on the
    coarser one.
    """

    __tablename__ = "groupings"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    column_name: Mapped[str] = mapped_column(String(128), nullable=False)
    parent_grouping_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    body: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("workspace_id", "slug", "version", name="uq_groupings_slug_version"),
        CheckConstraint("version >= 1", name="grouping_version_starts_at_one"),
        Index("ix_groupings_dataset", "workspace_id", "dataset_id"),
    )


class ModelRow(Base):
    """A fitted Model (`02` §4.8), immutable once fitted (R2).

    `spec_hash` is unique per workspace: FR-MODEL-66 returns the existing model rather than
    fitting the same specification twice, which is what makes a fit idempotent without an
    idempotency key. `parent_model_id` carries the refit lineage — there is no operation
    that edits a coefficient, so a change is always a new row.
    """

    __tablename__ = "models"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    model_family_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")

    dataset_version_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    spec: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    #: `v<n>:sha256:<64 hex>`. Widened from 71 when the algorithm version was prefixed —
    #: without the extra room the first tagged digest is truncated to a *different* valid
    #: digest, which is the failure mode a length limit is least able to report.
    spec_hash: Mapped[str] = mapped_column(String(80), nullable=False)
    fit_result: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    #: `02` §4.8: `status >= fitted` implies this is set. Written in the same transaction
    #: as `fit_result` and `status`, because a model that is `fitted` for even one
    #: transaction without its diagnostics is a model something could read in that state.
    diagnostics_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    parent_model_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    change_reason: Mapped[str | None] = mapped_column(Text)
    job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    #: `02` §4.8's `approval_request_id`, live from the lifecycle slice. Not a foreign key:
    #: `MODEL` depends on `GOV` and never the reverse (DEP-1), and a FK here would make
    #: governance's tables undroppable by a modelling migration.
    approval_request_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "workspace_id", "model_family_slug", "version", name="uq_models_family_version"
        ),
        UniqueConstraint("workspace_id", "spec_hash", name="uq_models_spec_hash"),
        CheckConstraint("version >= 1", name="model_version_starts_at_one"),
        # `02` §4.8: a model at `fitted` or beyond carries its numbers. The type refuses it
        # too; this is the layer that survives a direct `UPDATE`.
        CheckConstraint(
            "status IN ('draft', 'archived') OR fit_result IS NOT NULL",
            name="fitted_model_has_a_fit_result",
        ),
        # `02` §4.8's other invariant, at the same layer and for the same reason. The
        # spine could not state it because diagnostics did not exist; a model that reaches
        # `review` with no evidence is an approval request with nothing in it.
        CheckConstraint(
            "status IN ('draft', 'archived') OR diagnostics_id IS NOT NULL",
            name="fitted_model_has_diagnostics",
        ),
        # FR-MODEL-64's six states, at the layer a direct `UPDATE` cannot walk past. The
        # column is a `String(16)`: without this, `'live'` was a legal status and a model
        # holding one is skipped by every lifecycle query rather than refused.
        CheckConstraint(
            "status IN ('draft', 'fitted', 'review', 'approved', 'superseded', 'archived')",
            name="model_status_is_in_the_lifecycle",
        ),
        Index("ix_models_dataset_version", "workspace_id", "dataset_version_id"),
        # Supersession asks "which earlier versions of this family are approved?" on every
        # approval, and archiving asks the same question of one family.
        Index("ix_models_family_status", "workspace_id", "model_family_slug", "status"),
    )


class ModelComparisonRow(Base):
    """A persisted model comparison (`02` §4.11, FR-MODEL-56).

    Insert-only at the privilege layer (FR-DATA-42): `06` §3.3 makes a comparison required
    evidence for a Model approval where a predecessor exists, and evidence that can change
    after the approval is not evidence.

    No slug and no version, for the reason `DiagnosticsRow` has none — a comparison has no
    independent life and is always reached by id, from the Job that produced it or the
    approval that cites it.
    """

    __tablename__ = "model_comparisons"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        Index("ix_model_comparisons_workspace", "workspace_id"),
        # One artifact per Job: a second row for one Job would mean the comparison was
        # recorded twice, with nothing to say which one an approval cited.
        Index(
            "uq_model_comparisons_job",
            "job_id",
            unique=True,
            postgresql_where=job_id.isnot(None),
        ),
    )



class BacktestRow(Base):
    """A model measured on a Dataset Version it was not fitted on (`02` §4.12, FR-MODEL-57).

    Insert-only, and here with **both** layers: privileges narrowed to `SELECT, INSERT`, and
    the `artifact_append_only` triggers. `a1b2c3d4e5f6` installed the trigger pattern and
    gave its reason — revoking from the *owner* does nothing, because ownership carries
    implicit privileges — so a table with privileges alone is protected against the
    application role and not against a direct connection.

    Unlike `DiagnosticsRow` this is **not** one per model. FR-MODEL-57's backtest is per
    dataset version, and a model measured against four successive quarters has four rows;
    that is the series `05-monitoring.md` reads. Uniqueness is therefore on
    `(model_id, dataset_version_id)`: re-running the same pair would produce a second answer
    to one question, with nothing to say which one a review cited.
    """

    __tablename__ = "backtests"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    model_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    dataset_version_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        Index("ix_backtests_workspace", "workspace_id"),
        # The series a model's backtests form, read newest-first.
        Index("ix_backtests_model", "model_id", "computed_at"),
        UniqueConstraint(
            "model_id", "dataset_version_id", name="uq_backtests_model_version"
        ),
        Index(
            "uq_backtests_job",
            "job_id",
            unique=True,
            postgresql_where=job_id.isnot(None),
        ),
    )


class TransparencyArtifactRow(Base):
    """A non-GLM model's explanation (`02` FR-MODEL-33..37, R3).

    An **artifact**: insert-only at the privilege layer (FR-DATA-42), because it is the
    evidence a Rating Version's approval is granted against (FR-MODEL-36) and evidence that
    can change after the decision is not evidence.

    **Many rows per model, unlike `diagnostics`.** FR-MODEL-33 says *at least one*, both
    forms may be present, and a SHAP summary recomputed on a larger sample is a second
    artifact rather than a correction of the first. The read path takes the most recent;
    the older ones stay because an approval that cited one must still resolve.
    """

    __tablename__ = "transparency_artifacts"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    model_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    #: The `TransparencyArtifact`, whole — same reasoning as `diagnostics.payload`.
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        Index("ix_transparency_model", "workspace_id", "model_id", "created_at"),
    )


class DiagnosticsRow(Base):
    """Model quality evidence, computed once at fit time (`02` FR-MODEL-49, §4).

    An **artifact**: insert-only at the privilege layer like every other one (FR-DATA-42),
    because FR-MODEL-49 says diagnostics are computed once and read thereafter. A
    diagnostics row that could be updated would let the evidence behind an approval change
    after the approval.

    One row per model, enforced: a second set of diagnostics for one model is either a
    recomputation the requirement forbids or a silent overwrite of the evidence.
    """

    __tablename__ = "diagnostics"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    model_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    #: The `Diagnostics` artifact, whole. Stored as one document rather than shredded into
    #: columns: nothing queries inside it, and a shredded artifact is one that can be
    #: partially written.
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        UniqueConstraint("model_id", name="uq_diagnostics_model"),
        Index("ix_diagnostics_workspace", "workspace_id"),
    )


class PerilStructureRow(Base):
    """A Peril Structure (`02` §4.10, FR-MODEL-58..61).

    Versioned and approvable in its own right, so it is shaped like `ModelRow` rather than
    like `ModelComparisonRow`: a slug and a version, a lifecycle, and an approval request —
    FR-MODEL-61 makes it the artifact a Rating Version references, and a referent reached
    only by id is one nothing can cite by name.

    **The composition freezes when the reconciliation is written**, enforced by a trigger
    rather than only by the service. The reconciliation measures a specific set of models;
    editing the set afterwards leaves a number attached to a composition that never produced
    it, which is the same failure `models_fit_immutable` exists to prevent one table over.
    """

    __tablename__ = "peril_structures"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")

    #: The `PerilComponent` list and the `ExcludedPeril` list, whole. Same reasoning as
    #: `models.spec`: the platform reads them back through the contract type, and a
    #: normalised peril table would be a second definition of a shape `model-schema` owns.
    perils: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    excluded_perils: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    #: FR-MODEL-60's persisted reconciliation. Null only while `draft` — the CHECK below is
    #: the layer a direct `UPDATE` cannot walk past.
    reconciliation: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    #: Not a foreign key, for the reason `models.approval_request_id` is not: `MODEL`
    #: depends on `GOV` and never the reverse (DEP-1).
    approval_request_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "workspace_id", "slug", "version", name="uq_peril_structures_slug_version"
        ),
        CheckConstraint("version >= 1", name="peril_structure_version_starts_at_one"),
        # FR-MODEL-61's lifecycle, at the layer a direct `UPDATE` cannot walk past. Without
        # it a structure could hold `live`, and a status no query branches on is skipped
        # rather than refused — `model_status_is_in_the_lifecycle`'s lesson.
        CheckConstraint(
            "status IN ('draft', 'reconciled', 'review', 'approved', 'superseded', "
            "'archived')",
            name="peril_structure_status_is_in_the_lifecycle",
        ),
        # FR-MODEL-60: the reconciliation is the evidence an approval reads, so every state
        # that can be approved or was approved carries one. `fitted_model_has_diagnostics`
        # is the same invariant about the same kind of evidence.
        CheckConstraint(
            "status IN ('draft', 'archived') OR reconciliation IS NOT NULL",
            name="reconciled_peril_structure_has_a_reconciliation",
        ),
        Index("ix_peril_structures_slug_status", "workspace_id", "slug", "status"),
    )


class CustomObjectiveRow(Base):
    """A Custom Objective (`02` §4.5, FR-MODEL-38, FR-MODEL-46).

    Shaped like `PerilStructureRow` rather than like `DiagnosticsRow`: it is versioned,
    approvable, and referenced **by name** — a Model Spec carries
    `custom_objective:<slug>@<version>`, so a row reachable only by id could not be resolved
    from the spec that names it.

    Versioned rather than edited, because FR-MODEL-46 makes editing an approved objective a
    new version needing fresh certification. That is not a convention the service can be
    trusted to keep alone: a model fitted last month must still resolve its ref to the loss
    it was actually fitted under, so `uq_custom_objectives_slug_version` and the
    `custom_objectives_definition_immutable` trigger together make the definition columns
    unwritable once the row exists. Only the lifecycle columns move.
    """

    __tablename__ = "custom_objectives"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")

    #: `template` for the whole of Phase 1 (FR-MODEL-75). Stored rather than assumed,
    #: because Phase 2's `expression` rows will live in this table beside these and a
    #: column added later cannot say what the existing rows were.
    kind: Mapped[str] = mapped_column(String(16), nullable=False, default="template")
    #: §4.5's template name. Null is reserved for the `expression` kind the flag refuses.
    template: Mapped[str | None] = mapped_column(String(32))
    #: The author's chosen parameters — **not** §4.5's defaults resolved into them.
    #: `compile_objective` resolves defaults at fit time on purpose: a stored artifact that
    #: had silently absorbed them would let a later change to a default rewrite the meaning
    #: of an already-approved objective.
    params: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    #: FR-MODEL-44's declaration, whole, through the `Applicability` contract.
    applicability: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    hessian_strategy: Mapped[str] = mapped_column(String(16), nullable=False, default="clip_to_min")
    hessian_min: Mapped[float] = mapped_column(Float, nullable=False, default=1e-6)
    description: Mapped[str | None] = mapped_column(Text)

    #: FR-MODEL-42's evidence. Not a foreign key to `objective_certificates` only because
    #: the certificate points back the other way and one direction is enough; the CHECK
    #: below is what makes a status past `draft` mean something.
    certificate_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    #: Not a foreign key, for the reason `models.approval_request_id` is not: `MODEL`
    #: depends on `GOV` and never the reverse (DEP-1).
    approval_request_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "workspace_id", "slug", "version", name="uq_custom_objectives_slug_version"
        ),
        CheckConstraint("version >= 1", name="custom_objective_version_starts_at_one"),
        CheckConstraint("hessian_min > 0", name="custom_objective_hessian_min_is_positive"),
        # FR-MODEL-46's five states. `certified` sits between `draft` and `review` because
        # FR-MODEL-42 makes certification the condition of submission, not of approval.
        CheckConstraint(
            "status IN ('draft', 'certified', 'review', 'approved', 'deprecated')",
            name="custom_objective_status_is_in_the_lifecycle",
        ),
        # FR-MODEL-42, at the layer a direct `UPDATE` cannot walk past. `deprecated` joins
        # `draft` because it is reachable from `draft`: an objective abandoned before it was
        # ever certified is withdrawn, not certified. The type says the same thing; this is
        # the half that survives a migration or a fixture.
        CheckConstraint(
            "status IN ('draft', 'deprecated') OR certificate_id IS NOT NULL",
            name="certified_objective_has_a_certificate",
        ),
        # FR-MODEL-75 for the whole of Phase 1. A row whose `kind` is `expression` would
        # carry no loss at all — every field an expression objective needs is unbuilt — so
        # this is a refusal to persist an artifact nothing could evaluate, not a feature gate.
        CheckConstraint(
            "kind = 'template' AND template IS NOT NULL",
            name="custom_objective_is_a_template_in_phase_1",
        ),
        Index("ix_custom_objectives_slug_status", "workspace_id", "slug", "status"),
    )


class ObjectiveCertificateRow(Base):
    """An Objective Certificate (`02` §4.7, FR-MODEL-42).

    Insert-only at the privilege layer (FR-DATA-42), for `TransparencyArtifactRow`'s reason:
    `06` §4.2 makes it the required evidence for a Custom Objective's approval, and evidence
    that can change after the decision is not evidence.

    Several rows per objective version are expected, not prevented. Re-certifying after a
    library upgrade is the normal way a finding is found, and the earlier certificate is
    what an already-granted approval argued from — so the read takes the latest and the
    older rows stay.
    """

    __tablename__ = "objective_certificates"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    workspace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    custom_objective_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    #: Denormalised from the objective row on purpose: a certificate names the *version* it
    #: certifies, and FR-MODEL-46's "editing creates a new version" is only auditable if the
    #: evidence says which one it measured without a join to a row that may since have moved.
    objective_version: Mapped[int] = mapped_column(Integer, nullable=False)
    certified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    #: The `CertificateResult` — checks, sampling grid and library versions — whole.
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        CheckConstraint("objective_version >= 1", name="certificate_version_starts_at_one"),
        Index(
            "ix_objective_certificates_objective",
            "workspace_id",
            "custom_objective_id",
            "certified_at",
        ),
    )
