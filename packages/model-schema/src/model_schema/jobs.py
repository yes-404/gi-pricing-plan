"""The Job shape — one lifecycle for every slow operation (`07` §4.1).

> **R1** — Everything slow is a Job. Any operation that can exceed 2 s returns `202` with
> a Job, has progress, is cancellable, and persists its result.

The enums are closed on purpose. `kind` and `queue` decide which worker pool runs the work
(FR-405), and a free-string kind means a typo routes to a queue that does not exist and
the job sits `queued` forever with nothing to explain why.
"""

from __future__ import annotations

import enum
from collections.abc import Mapping
from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from model_schema.input_free import InputFreeError
from model_schema.perils import PerilCode
from model_schema.refs import REF_PATTERN

__all__ = [
    "TERMINAL_STATUSES",
    "VALID_TRANSITIONS",
    "ActorKind",
    "Job",
    "JobError",
    "JobErrorLocation",
    "JobKind",
    "JobQueue",
    "JobResult",
    "JobSource",
    "JobStatus",
    "Principal",
    "Progress",
    "ResourceBudget",
    "RetryPolicy",
    "RetryState",
]


class JobKind(enum.StrEnum):
    """The typed operation a Job performs (`07` §2, job.schema.json)."""

    DATASET_INGEST = "dataset.ingest"
    DATASET_VALIDATE = "dataset.validate"
    DATASET_PROFILE = "dataset.profile"
    DATASET_DERIVE = "dataset.derive"
    BLOB_PROMOTE = "blob.promote"
    MODEL_FIT = "model.fit"
    MODEL_TRANSPARENCY = "model.transparency"
    MODEL_BACKTEST = "model.backtest"
    MODEL_COMPARE = "model.compare"
    PERIL_STRUCTURE_RECONCILE = "peril_structure.reconcile"
    OBJECTIVE_CERTIFY = "objective.certify"
    METRIC_CERTIFY = "metric.certify"
    RATING_COMPILE = "rating.compile"
    RATING_REGRESSION = "rating.regression"
    RATE_TABLE_DIFF = "rate_table.diff"
    #: `RL-1418`, FD-1358: the paged diff-cells route's 202 Job, a kind of its own so that
    #: `rate_table.diff` and the artifact its summary route returns do not change.
    RATE_TABLE_DIFF_CELLS = "rate_table.diff_cells"
    SCORE_BATCH = "score.batch"
    #: WK-671 Task 4B, RL-862 (`docs/plans/2026-08-29-w11-nfr-rate-1-trace-capture-remedy-
    #: ruling.md`): the off-path re-score that fills in a sampled real-time trace's body.
    #: `app.worker.trace_handlers`. Parameters carry only the pending `scoring_traces` row
    #: id — never the Quote Context, which is an access-controlled carrier the trace row
    #: is, and `JobRow.parameters` is not (RL-862 §8.4).
    SCORE_TRACE_PRODUCE = "score.trace_produce"
    DISLOCATION_RUN = "dislocation.run"
    OPTIMISATION_RUN = "optimisation.run"
    GIPP_CHECK = "gipp.check"
    MONITOR_RUN = "monitor.run"
    DOSSIER_GENERATE = "dossier.generate"
    EXPORT_REGULATORY = "export.regulatory"
    BLOB_GC = "blob.gc"


class JobStatus(enum.StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobQueue(enum.StrEnum):
    """Named Celery queues with independently sized worker pools (FR-405)."""

    DEFAULT = "default"
    COMPUTE = "compute"
    SCORING = "scoring"
    IO = "io"


class JobSource(enum.StrEnum):
    UI = "ui"
    API = "api"
    SCHEDULE = "schedule"
    SYSTEM = "system"


class ActorKind(enum.StrEnum):
    USER = "user"
    SERVICE_ACCOUNT = "service_account"
    SYSTEM = "system"


#: Statuses from which no further transition is allowed. A Job that has finished is a
#: historical record — FR-410 keeps it for ≥ 13 months as part of the provenance chain
#: (FR-6), and a record that can still change is not provenance.
TERMINAL_STATUSES: frozenset[JobStatus] = frozenset(
    {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}
)

#: The lifecycle of FR-399, as data rather than as scattered `if` statements.
#: `queued → cancelled` is allowed: cancelling before a worker picks the job up is the
#: common case, and it needs no cooperation from `pricing-core`.
VALID_TRANSITIONS: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.QUEUED: frozenset({JobStatus.RUNNING, JobStatus.CANCELLED, JobStatus.FAILED}),
    JobStatus.RUNNING: frozenset(
        {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}
    ),
    JobStatus.SUCCEEDED: frozenset(),
    JobStatus.FAILED: frozenset(),
    JobStatus.CANCELLED: frozenset(),
}


class Principal(BaseModel):
    """An authenticated identity: User, Service Account, or the platform itself."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: ActorKind
    id: UUID | None = Field(
        default=None, description="Null only for `system`, which has no principal row."
    )
    display: str | None = Field(
        default=None, description="Human-readable label recorded at the time of the action."
    )

    @model_validator(mode="after")
    def _non_system_principals_are_identified(self) -> Principal:
        if self.kind is not ActorKind.SYSTEM and self.id is None:
            raise InputFreeError("a principal that is not a system principal must carry an id")
        return self


class Progress(BaseModel):
    """Structured progress (FR-400) — a fraction, a stage label, and counters."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    fraction: Annotated[float, Field(ge=0.0, le=1.0)] = 0.0
    stage: str = ""
    counters: dict[str, int] = Field(default_factory=dict)


class JobResult(BaseModel):
    """Where a succeeded Job put its output."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: str = Field(pattern="^(artifact|blob|none)$")
    ref: str | None = None

    @model_validator(mode="after")
    def _reference_required_unless_none(self) -> JobResult:
        if self.kind != "none" and not self.ref:
            raise ValueError(f"a result of kind {self.kind!r} must carry a ref")
        return self


#: Where a location is stored inside a Job error's `detail`: the one place the previous version's
#: reader (`extra="forbid"`, `detail: dict[str, Any]`) already accepts free content (`07` NFR-531).
LOCATION_DETAIL_KEY = "_location"


class JobErrorLocation(BaseModel):
    """Where in the caller's own artifact a deterministic refusal points (#1917, `07` §4.1).

    Identifiers only: a step id, a path inside that step, a reference, a name the artifact
    itself declares. **Never a submitted value** is what the raise sites guarantee, by filling
    this only from the caller's own artifact; no pattern can prove it. The model gives `ref` and
    `structure` the wire form of an artifact reference (`REF_PATTERN`), `peril` a `PerilCode`
    and every other key a non-empty `str`; it refuses any other key, a JSON number and a location
    with no key set. A digit string such as `"42"` is a valid value and is NOT refused. The key
    set is the one #1911 accepted.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str | None = Field(default=None, min_length=1)
    field: str | None = Field(default=None, min_length=1)
    ref: str | None = Field(default=None, pattern=REF_PATTERN)
    objective: str | None = Field(default=None, min_length=1)
    structure: str | None = Field(default=None, pattern=REF_PATTERN)
    factor: str | None = Field(default=None, min_length=1)
    key: str | None = Field(default=None, min_length=1)
    feature: str | None = Field(default=None, min_length=1)
    interaction: str | None = Field(default=None, min_length=1)
    operand: str | None = Field(default=None, min_length=1)
    peril: PerilCode | None = None

    @model_validator(mode="after")
    def _points_somewhere(self) -> JobErrorLocation:
        if all(value is None for value in self.model_dump().values()):
            raise InputFreeError("a location must name at least one identifier")
        return self


class JobError(BaseModel):
    """A typed failure (FR-403).

    `code` is the contract and `retryable` decides whether the platform will try again;
    `detail` carries the field-level cause where the failure is deterministic, which is
    what lets the UI point at the offending input instead of showing a stack trace.
    `location` is the typed form of that pointer (#1917): identifiers of the caller's own
    artifact, never a submitted value.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(pattern="^[A-Z][A-Z0-9_]*$")
    message: str
    retryable: bool
    detail: dict[str, Any] = Field(default_factory=dict)
    location: JobErrorLocation | None = None
    trace_id: str | None = Field(default=None, pattern="^[0-9a-f]{32}$")

    @field_validator("detail")
    @classmethod
    def _detail_does_not_carry_the_reserved_key(cls, detail: dict[str, Any]) -> dict[str, Any]:
        if LOCATION_DETAIL_KEY in detail:
            raise InputFreeError(f"detail may not carry the reserved key {LOCATION_DETAIL_KEY!r}")
        return detail

    # Two forms. The wire form (`model_dump`) carries `location` and is what the API returns. The
    # stored form (`stored_form`) keeps the location inside `detail` under `LOCATION_DETAIL_KEY`,
    # so the previous version can read every row this one writes (`07` NFR-531); `from_stored` is
    # its one reader. The constructor refuses that key in `detail`, so only `from_stored` can
    # consume it.
    def stored_form(self) -> dict[str, Any]:
        """The mapping to store: no `location` key, the location folded into `detail`.

        A location is an aid and never costs the error its code: if folding fails, the mapping
        is returned without a location.
        """
        stored = self.model_dump(mode="json", exclude={"location"})
        if self.location is not None:
            try:
                folded = self.location.model_dump(mode="json", exclude_none=True)
            except Exception:  # a location is an aid: nothing about it may lose the error
                return stored
            stored["detail"] = {**stored["detail"], LOCATION_DETAIL_KEY: folded}
        return stored

    @classmethod
    def from_stored(cls, stored: Mapping[str, Any]) -> JobError:
        """Build the error from a stored row, lifting the folded location into `location`.

        Never raises on the location: a stored `_location` that is not a valid
        `JobErrorLocation` is dropped and the error carries none. A row stored before
        `location` existed has no such key and reads back with none.
        """
        fields = dict(stored)
        detail = fields.get("detail")
        if isinstance(detail, Mapping) and LOCATION_DETAIL_KEY in detail:
            rest = {k: v for k, v in detail.items() if k != LOCATION_DETAIL_KEY}
            fields["detail"] = rest
            try:
                fields["location"] = JobErrorLocation.model_validate(detail[LOCATION_DETAIL_KEY])
            except ValidationError:
                fields.pop("location", None)
        return cls.model_validate(fields)


class ResourceBudget(BaseModel):
    """Exceeding it yields a typed error naming the budget, not an opaque kill (FR-412)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    memory_gb: Annotated[float, Field(gt=0)] | None = None
    wall_clock_s: Annotated[int, Field(gt=0)] | None = None


class RetryPolicy(enum.StrEnum):
    """`infrastructure_only` retries a lost worker, never a rejected input.

    Retrying a deterministic failure burns a worker pool to produce the same error, and on
    a job that writes artifacts it risks producing them more than once.
    """

    INFRASTRUCTURE_ONLY = "infrastructure_only"
    NONE = "none"


class RetryState(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    attempted: Annotated[int, Field(ge=0)] = 0
    max: Annotated[int, Field(ge=0)] = 3
    policy: RetryPolicy = RetryPolicy.INFRASTRUCTURE_ONLY


class Job(BaseModel):
    """A tracked asynchronous unit of work, as returned by the API (`07` §4.1)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    workspace_id: UUID
    kind: JobKind
    status: JobStatus
    queue: JobQueue
    submitted_by: Principal
    source: JobSource
    idempotency_key: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    progress: Progress | None = None
    result: JobResult | None = None
    error: JobError | None = None
    trace_id: str | None = Field(default=None, pattern="^[0-9a-f]{32}$")
    platform_build: str | None = Field(
        default=None,
        description="The platform version and build the Job ran on, `{version}+{build}`, "
        "recorded when the worker moves it to `running`; null while `queued` (FR-18).",
    )
    progress_at: datetime | None = Field(
        default=None, description="Time of the last progress report (NFR-528)."
    )
    stalled: bool = Field(
        default=False,
        description="A running Job that has reported no progress within the configured "
        "window. Derived on read, never stored — a stored flag needs a sweeper to clear "
        "it and is wrong between sweeps (NFR-528).",
    )
    queued_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    resource_budget: ResourceBudget | None = None
    retries: RetryState = Field(default_factory=RetryState)

    @model_validator(mode="after")
    def _timestamps_match_status(self) -> Job:
        """A finished Job has a finish time; an unfinished one does not.

        Enforced on the shape rather than trusted to the writer: `finished_at` is what
        every duration metric and retention sweep reads, and a terminal Job without one is
        invisible to both.
        """
        if self.status in TERMINAL_STATUSES and self.finished_at is None:
            raise InputFreeError("a job in a terminal status must have finished_at set")
        if self.status not in TERMINAL_STATUSES and self.finished_at is not None:
            raise InputFreeError("a job not in a terminal status must not have finished_at set")
        if self.status is JobStatus.QUEUED and self.started_at is not None:
            raise InputFreeError("a queued job must not have started_at set")
        if (
            self.finished_at is not None
            and self.started_at is not None
            and self.finished_at < self.started_at
        ):
            raise InputFreeError("finished_at precedes started_at")
        return self
