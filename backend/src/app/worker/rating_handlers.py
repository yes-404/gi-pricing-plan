"""What the `rating.compile` Job actually does (`03` §5.1:514, FR-239/240, WK-671 Task 1.2).

The 202 endpoint submits these. `compile_rating_version` resolves the pinned algorithm
and every pin to real content and returns the full, self-contained `Bundle`; this handler
persists it as a blob and returns `JobResult(kind="blob")` with the sha256 as the ref —
the same shape `rate_table.diff` established for its own artifact. `GET /blobs/{sha256}`
is what a client fetches it back through.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.db.models import BlobRow
from app.errors import PlatformError
from app.platform import audit
from app.platform import rating_versions as rating_versions_service
from app.platform import regression_runs as regression_runs_service
from app.platform import regression_suites as regression_suites_service
from app.platform.blobs import to_ref
from app.worker.data_handlers import _actor, _bridge, _workspace
from app.worker.handlers import HANDLERS, register_handler
from app.worker.progress import JobBudgetExceededError
from model_schema import ArtifactRef, JobKind, JobResult, JobSource, cases_log_bytes
from pricing_core.progress import JobCancelled, ProgressCallback
from pricing_core.rating.compile import Bundle
from pricing_core.rating.properties import UnsweepableProperty
from pricing_core.rating.runtime import load_bundle
from pricing_core.rating.testing import run_regression

__all__ = ["register_rating_handlers"]


def _rating_compile(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`rating.compile` — resolve pins to real content and persist the compiled Bundle.

    `job_identity` supplies `workspace_id`/`actor`; the 202 endpoint adds
    `rating_version_id`. The resolution itself may do real I/O (a rate table's cells, a
    reference table's rows, a GBM's booster blob), which is why this runs as a Job rather
    than inline on the request (RL-865).
    """
    progress = _bridge(callback)
    workspace_id = _workspace(parameters)
    actor = _actor(parameters)
    rating_version_id = UUID(parameters["rating_version_id"])
    progress.update(0.05, "compiling")

    async def work() -> str:
        async with progress.database.unit_of_work() as session:
            # Read the outgoing hash *before* compiling: `compile_rating_version` rebinds
            # `row.bundle` to the new summary on its way out, so after the call there is
            # nothing left to report as `before`. Captured as a value, not a reference to
            # the dict, for the same reason.
            row = await rating_versions_service.load_rating_version(
                session, workspace_id=workspace_id, rating_version_id=rating_version_id
            )
            prior_hash = (row.bundle or {}).get("content_hash")
            entity_ref = f"rating_version:{row.slug}@{row.version}"

            bundle = await rating_versions_service.compile_rating_version(
                session,
                workspace_id=workspace_id,
                rating_version_id=rating_version_id,
                blob_store=progress.blob_store,
            )
            payload = bundle.model_dump_json().encode()
            ref = await progress.blob_store.put(session, payload, "application/json")
            # RL-915: the key goes on the version's own metadata, in this same
            # transaction. Without it the only record of where the bundle lives is this
            # Job's result — an operational row with its own pruning, so a trimmed Job
            # history would leave a compiled version unresolvable.
            #
            # **Before the audit write, deliberately**: the row reaches its final state
            # first, so the event that records the compile describes a completed one. It is
            # safe in either order — `prior_hash` and `entity_ref` were captured as values
            # above, and `after` reads locals rather than the row — but "finish the row,
            # then record what happened" is the sequence that stays correct if the audit
            # payload ever widens to include the key.
            #
            # This re-loads the row through the service that owns `row.bundle`'s shape;
            # within one session SQLAlchemy's identity map returns the object the handler
            # already holds, so there is no second query and no second copy to diverge.
            await rating_versions_service.record_bundle_blob(
                session,
                workspace_id=workspace_id,
                rating_version_id=rating_version_id,
                blob_sha256=ref.sha256,
            )

            # NFR-498: compilations emit an Audit Event with before/after state.
            # Inside this `unit_of_work`, never its own: `06` R2 makes the audit write
            # share the caller's transaction, and `audit.record` refuses outright if there
            # is none — an event that committed independently could outlive a compile that
            # rolled back, and the chain would record something that never happened.
            await audit.record(
                session,
                workspace_id=workspace_id,
                actor=actor,
                # `JobSource` names where the *request* came from — its members are UI,
                # API, SCHEDULE, SYSTEM, all origins, none an executor — so a compile
                # submitted through `POST /rating-versions/{id}/compile` is `API` even
                # though the worker runs it. `dataset_version.ingested` sets the same
                # precedent from inside a worker handler (`data/ingestion.py:260`).
                source=JobSource.API,
                action="rating_version.compiled",
                entity_ref=entity_ref,
                before={"bundle_hash": prior_hash},
                # `blob_sha256` joins the after-state because RL-915 put it on the row
                # this event describes: without it the trail can say a compile happened and
                # what it hashed to, but not *which stored artifact* it produced — and
                # "which blob did this compile write" is exactly the question an audit of a
                # priced quote has to answer. Note it is the blob key, not
                # `bundle.content_hash`: different hashes of different things, and the
                # patterns keep them apart.
                after={
                    "bundle_hash": bundle.content_hash,
                    "bytes": len(payload),
                    "blob_sha256": ref.sha256,
                },
                job_id=progress.job_id,
            )
            return ref.sha256

    sha256 = progress.run_on_loop(work())
    progress.update(1.0, "done")
    return JobResult(kind="blob", ref=sha256)


def _rating_regression(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`rating.regression` — run the algorithm's Regression Suite against a compiled version
    (`03` FR-260, FR-261, FR-1214, `PL-1205` Task 5).

    Loads the compiled bundle and the algorithm's current suite, runs `run_regression` (plain
    `def`, on this worker thread — RL-868), writes the case log as one content-addressed blob
    and persists the `RegressionRun` row in one transaction. A run that fails still persists;
    the Job then ends `failed` with the problem code (`PROPERTY_ASSERTION_FAILED`, or
    `GOLDEN_QUOTE_MISMATCH` when a golden quote failed). No log line, error message or audit
    payload carries a Quote Context (NFR-499): failures name quotes and properties only.
    """
    progress = _bridge(callback)
    workspace_id = _workspace(parameters)
    rating_version_id = UUID(parameters["rating_version_id"])
    progress.update(0.05, "loading")

    async def prepare() -> tuple[Any, Any, ArtifactRef]:
        async with progress.database.session() as session:
            row = await rating_versions_service.load_rating_version(
                session, workspace_id=workspace_id, rating_version_id=rating_version_id
            )
            ref = ArtifactRef(type="rating_version", slug=row.slug, version=row.version)
            blob_sha256 = (row.bundle or {}).get("blob_sha256")
            if not blob_sha256 or row.algorithm_ref is None:
                raise PlatformError(
                    "BUNDLE_COMPILE_FAILED", "Rating version is not compiled", 409,
                    f"{ref} has no compiled bundle to run the Regression Suite against.",
                )
            algorithm_slug = ArtifactRef.model_validate(row.algorithm_ref).slug
            found = await regression_suites_service.current_suite_for_algorithm(
                session, workspace_id=workspace_id, algorithm_slug=algorithm_slug
            )
            if found is None:
                raise PlatformError(
                    "NOT_FOUND", "Regression Suite not found", 404,
                    f"Algorithm {algorithm_slug!r} has no Regression Suite to run.",
                )
            suite = regression_suites_service.to_schema(*found)
            blob_row = await session.get(BlobRow, blob_sha256)
            if blob_row is None:
                raise PlatformError(
                    "BUNDLE_COMPILE_FAILED", "Compiled bundle is missing", 409,
                    f"{ref}'s compiled bundle is no longer in the blob store.",
                )
            payload = await progress.blob_store.read(to_ref(blob_row))
        return load_bundle(Bundle.model_validate_json(payload)), suite, ref

    bundle, suite, ref = progress.run_on_loop(prepare())
    progress.update(0.2, "running")
    try:
        run, log = run_regression(
            bundle, suite, rating_version_ref=ref, now=lambda: datetime.now(UTC)
        )
    except UnsweepableProperty as exc:  # a named refusal; its message names no quote input
        raise PlatformError(
            "REGRESSION_PROPERTY_INVALID", "Regression property invalid", 422, str(exc)
        ) from exc
    except (PlatformError, JobCancelled, JobBudgetExceededError):
        raise  # the runner's own clauses handle these; never re-labelled or withheld
    except Exception as exc:
        # NFR-499: any other exception's message may carry a quote input (Pydantic's
        # `ValidationError` is a `ValueError` and prints `input_value`), and the generic
        # `JOB_HANDLER_FAILED` path stores `str(exc)` and logs the traceback. Re-raise with
        # the exception's type alone, cutting the chain.
        raise RuntimeError(
            f"the regression run failed with {type(exc).__name__}; details are withheld "
            "because they may contain a quote input (NFR-499)"
        ) from None
    progress.update(0.9, "persisting")

    async def persist() -> Any:
        async with progress.database.unit_of_work() as session:
            blob = await progress.blob_store.put(
                session, cases_log_bytes(log), "application/json"
            )
            if blob.sha256 != run.cases_blob.sha256:
                raise RuntimeError("the stored case log does not match its content address")
            stored = run.model_copy(update={"job_id": progress.job_id})
            return await regression_runs_service.persist_run(
                session, workspace_id=workspace_id, rating_version_id=rating_version_id,
                run=stored, actor_id=UUID(parameters["actor"]["id"]),
            )

    saved = progress.run_on_loop(persist())
    progress.update(1.0, "done")
    if run.overall == "fail":
        failed_golden = [g.name for g in run.golden_results if g.status == "fail"]
        failed_props = [p.name for p in run.property_results if p.status == "fail"]
        code = "GOLDEN_QUOTE_MISMATCH" if failed_golden else "PROPERTY_ASSERTION_FAILED"
        raise PlatformError(
            code, "Regression Suite failed", 409,
            f"{ref} failed golden quote(s) {failed_golden} and property(ies) {failed_props} "
            f"of {run.suite_ref}; regression run {saved.id} is recorded.",
        )
    return JobResult(kind="artifact", ref=f"regression_run:{saved.id}")


def register_rating_handlers() -> None:
    """Register the `rating.*` handlers.

    A function rather than import-time side effects: `register_handler` refuses a
    duplicate (rightly), and a module that registers on import cannot be imported twice —
    which a test importing this module for a type would do. The `dataset.*`, `model.*`
    and `rate_table.*` handlers set the same precedent.
    """
    for kind, handler in (
        (JobKind.RATING_COMPILE, _rating_compile),
        (JobKind.RATING_REGRESSION, _rating_regression),
    ):
        if kind not in HANDLERS:
            register_handler(kind, handler)
