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
    "ApiKeyRow",
    "ApprovalDecisionRow",
    "ApprovalPolicyRow",
    "ApprovalRequestRow",
    "AuditEventRow",
    "BlobRow",
    "DatasetRow",
    "DatasetVersionRow",
    "JobLogRow",
    "JobRow",
    "OutboxRow",
    "OutboxStatus",
    "RoleAssignmentRow",
    "RoleRow",
    "ServiceAccountRow",
    "SourceRow",
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
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("workspace_id", "slug", name="uq_datasets_workspace_slug"),
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
