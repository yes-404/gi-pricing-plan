"""`POST /api/v1/score` — real-time scoring (03 §5.1, FR-250/251/255/256; WK-671 Task 2B) and
`POST /api/v1/score/batch` — batch re-rating (03 §5.1:517, FR-253/254/255; WK-671 Task 3C).

**`/score` scores untraced and never sets `trace=True` for FR-259's sake** (WK-671 Task
4B; RL-862, `docs/rulings/RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md`).
`ctx.options.trace` is unchanged and still what decides whether `score_one` captures a
trace *for FR-258's on-request return* — a caller who asks for one gets one inline and
knowingly pays for it. FR-259's *sampled, persisted* trace is a different thing: after
scoring, `decide_sampling(result.outcome, ...)` decides whether this outcome is sampled,
and a sampled one is recorded as a **pending** `scoring_traces` row and handed to an
off-path `score.trace_produce` Job (`app.worker.trace_handlers`) to reproduce and persist —
never captured inline, because always capturing pinned the traced fraction at 1 and put
every request over NFR-489's 50 ms budget.

**`async def`, and not incidentally.** `BundleSlot` is unsynchronised and confined to one
worker's event loop; FastAPI runs a plain `def` handler in a threadpool, which would put two
threads on that object and reach the race its docstring documents. A synchronous handler here
is a defect, not a style choice.

**No `response_model=`, and no Pydantic return annotation** (NFR-502 as amended by
RL-883). The requirement is *validate inbound, never outbound*: `QuoteContext` is untrusted
and is validated; `ScoringResult` is built by `pricing-core` and is already trusted, so it is
serialised with Pydantic v2's compiled encoder and returned in a raw `Response`. A return-type
annotation is precisely what FastAPI's own `ORJSONResponse` deprecation notice recommends, and
precisely what this requirement forbids — an annotated route filters extra keys and answers
500 on a shape that violates its model, which is outbound validation by another name.

**The error boundary is this module's.** `pricing-core` cannot import `PlatformError`
(ADR-703), so `score_one` raises a code-named bare `ValueError` — `f"{code}: {message}"`. The
codes are parsed off the front and mapped here. Deliberately *not* mapped: a firing
`on_violation="error"` constraint raises a plain `NotImplementedError`, which is undesigned and
must stay visible as a 500 rather than be dressed as a typed per-quote error.

**`/score/batch` submits a Job and nothing else.** It carries no bundle-resolution logic of
its own — that lives in `_compiled_for`/`_fetch_bundle` above, reused (not duplicated,
RL-922) by `app.worker.scoring_handlers`. The route's only responsibilities are to
authorise the caller against `Permission.SCORE_BATCH` (granted by no builtin role, deliberately
— FR-347, C3 of `docs/plans/PL-00849-wk-671-slice-3-batch-scoring-the-pure-transform-the-checkpointing-handler-and-the-route.md`) and to translate the request
body into the `score.batch` handler's parameter shape.
"""

from __future__ import annotations

import random
from typing import Annotated, Any, Final
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.authz import requires
from app.api.deps import Caller, SettingsDep, job_identity
from app.api.responses import problems
from app.config import Settings
from app.db.models import BlobRow
from app.db.session import Database
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import jobs as job_service
from app.platform import rating_versions as rating_versions_service
from app.platform import settings as settings_service
from app.platform import traces as traces_service
from app.platform.blobs import BlobStore, to_ref
from app.platform.bundle_slot import BundleSlot
from model_schema import ArtifactRef, Job, JobKind, Permission, QuoteContext, ScoringResult
from pricing_core.rating.compile import Bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_one

_log = get_logger("app.api.score")

router = APIRouter(tags=["rating"])

#: The per-quote codes `score_one` raises as code-named `ValueError`s, each already owned by
#: `03` §5.1 and registered in `app.errors`. A code outside this set is not a per-quote
#: refusal and must not be turned into one — it reaches the caller as a 500.
_PER_QUOTE_CODES: Final[frozenset[str]] = frozenset(
    {
        "INPUT_CONTRACT_VIOLATION",
        "RATE_TABLE_MISS",
        "REFERENCE_LOOKUP_MISS",
        "MODEL_CALL_FAILED",
    }
)

#: 422: the quote is well-formed but cannot be priced as given. `03` §5.1 owns the codes.
_PER_QUOTE_STATUS: Final[int] = 422


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


def _blob_store(request: Request) -> BlobStore:
    store: BlobStore = request.app.state.blob_store
    return store


def _bundle_slot(request: Request) -> BundleSlot:
    slot: BundleSlot = request.app.state.bundle_slot
    return slot


DatabaseDep = Annotated[Database, Depends(_database)]
BlobStoreDep = Annotated[BlobStore, Depends(_blob_store)]
BundleSlotDep = Annotated[BundleSlot, Depends(_bundle_slot)]
ScoreExecuteDep = Annotated[Caller, Depends(requires(Permission.SCORE_EXECUTE))]
ScoreBatchDep = Annotated[Caller, Depends(requires(Permission.SCORE_BATCH))]


def _required_ref(ctx: QuoteContext) -> ArtifactRef:
    """The explicit ref, or RL-880's refusal.

    Raised *here*, before `score_one`, and that ordering is the whole point. `score_one`
    also refuses a missing ref — with `INPUT_CONTRACT_VIOLATION`, its own input-contract
    error — and forwarding to it would answer a caller who omitted the ref by telling them
    their input was malformed, when the truth is that this platform has no live Rating
    Version to score against. `live` is a property of a Deployment (FR-238), which is
    WK-674's; until then the endpoint refuses rather than guessing which version is live.

    The branch is permanent rather than a stub: after WK-674 it is what an environment holding
    no Deployment answers, and WK-674 narrows the trigger instead of deleting a placeholder.
    """
    ref = ctx.options.rating_version_ref if ctx.options is not None else None
    if ref is None:
        raise PlatformError(
            "NO_LIVE_RATING_VERSION",
            "No live Rating Version",
            409,
            "This platform has no live Rating Version to score against. Supply "
            "options.rating_version_ref explicitly.",
        )
    return ref


async def _fetch_bundle(
    database: Database,
    blob_store: BlobStore,
    slot: BundleSlot,
    *,
    workspace_id: UUID,
    ref: ArtifactRef,
) -> CompiledBundle:
    """Resolve a ref to its hydrated `CompiledBundle`: one metadata read, then either a
    slot hit or the blob store (RL-921,
    `docs/rulings/INDEX.md#2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulingsmd`).

    The blob key lives on the version's own metadata (RL-915), so this is a single
    keyed read rather than a scan of Job history for the latest successful compile — which
    would put an un-indexed JSONB lookup inside NFR-489's budget and, worse, decide
    *which* compiled artifact a version is inside a query nobody had to defend.

    **The content hash is read from that same row and checked against the slot before the
    blob is touched at all.** RL-921 found `compile_rating_version` already writes
    `content_hash` into `row.bundle` and this function used to discard it, paying the blob
    primary-key lookup, a ~2 MB object-store read and a full `Bundle.model_validate_json`
    on every request even when this worker already holds the exact bundle that hash names.
    **This carries zero staleness window** — unlike `slot.hash_for(ref)` (used only in
    `_compiled_for`'s degradation branch below), the hash checked here was re-derived from
    the authoritative row on *this* call, never served from a memo of an earlier one. A
    slot hit still calls `slot.put` to refresh the ref→hash memo `_compiled_for`'s
    degradation path depends on; a miss falls through to the blob read exactly as before.
    """
    async with database.session() as session:
        row = await rating_versions_service.resolve_rating_version_ref(
            session, workspace_id=workspace_id, ref=ref
        )
        metadata = row.bundle or {}
        content_hash = metadata.get("content_hash")
        blob_sha256 = metadata.get("blob_sha256")
        if not blob_sha256:
            raise PlatformError(
                "BUNDLE_COMPILE_FAILED",
                "Rating version is not compiled",
                409,
                f"{ref} has no compiled bundle to score against. Compile it first.",
            )

        if content_hash is not None:
            compiled = slot.get(content_hash)
            if compiled is not None:
                slot.put(ref, compiled)
                return compiled

        blob_row = await session.get(BlobRow, blob_sha256)
        if blob_row is None:
            raise PlatformError(
                "BUNDLE_COMPILE_FAILED",
                "Compiled bundle is missing",
                409,
                f"{ref}'s compiled bundle is no longer in the blob store.",
            )
        payload = await blob_store.read(to_ref(blob_row))

    bundle = Bundle.model_validate_json(payload)
    compiled = slot.get(bundle.content_hash)
    if compiled is None:
        compiled = load_bundle(bundle)
    slot.put(ref, compiled)
    return compiled


async def _compiled_for(
    database: Database,
    blob_store: BlobStore,
    slot: BundleSlot,
    *,
    workspace_id: UUID,
    ref: ArtifactRef,
) -> CompiledBundle:
    """The hydrated bundle for `ref`, degrading to the slot when metadata storage is down.

    NFR-497 requires degradation to *"the last-known-good cached bundle if metadata
    storage is unavailable"*, and the slot's ref-to-hash memo is what makes that reachable:
    the request carries a ref, and ref to hash is itself a metadata read.

    **Only an unexpected failure degrades.** A `PlatformError` is a *decided* answer — the
    store was reachable and said the version does not exist, or is not compiled — and
    serving a held bundle over a decided refusal would be answering a question the caller
    did not ask. A raw exception means the store failed to answer at all, and that is the
    condition the requirement names. A ref this worker has never resolved is refused either
    way: serving one would not be degradation, it would be invention.
    """
    try:
        return await _fetch_bundle(
            database, blob_store, slot, workspace_id=workspace_id, ref=ref
        )
    except PlatformError:
        raise
    except Exception:
        held_hash = slot.hash_for(ref)
        compiled = slot.get(held_hash) if held_hash is not None else None
        if compiled is None:
            raise
        return compiled


def _as_platform_error(exc: ValueError) -> PlatformError | None:
    """Map `pricing-core`'s code-named `ValueError` onto its registered code.

    The code is parsed off the front rather than matched against the whole message: the
    convention is `f"{code}: {message}"` and the message half is prose that will change.
    Anything whose prefix is not a per-quote code is left alone — returning `None` lets the
    caller re-raise, so an unrecognised failure surfaces as a 500 instead of being labelled
    with whichever code happened to be nearest.
    """
    code, separator, detail = str(exc).partition(": ")
    if not separator or code not in _PER_QUOTE_CODES:
        return None
    return PlatformError(
        code, code.replace("_", " ").title(), _PER_QUOTE_STATUS, detail or None
    )


@router.post(
    "/score",
    summary="Score one Quote Context against an explicit Rating Version",
    status_code=200,
    # Every status this operation can actually produce, because a client cannot handle one
    # the contract does not mention. 409 carries two distinct codes —
    # `NO_LIVE_RATING_VERSION` when no ref is supplied, and `BUNDLE_COMPILE_FAILED` when the
    # named version has no compiled bundle — and 422 carries FR-255's four per-quote
    # codes. 404 is a ref naming no version; 401 and 403 are authentication and the
    # `score:execute` check.
    responses=problems(401, 403, 404, 409, 422),
)
async def score(
    ctx: QuoteContext,
    caller: ScoreExecuteDep,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
    slot: BundleSlotDep,
    settings: SettingsDep,
) -> Response:
    """Score one quote (FR-250/251).

    WK-671 imposes neither of FR-251's restrictions — approved-only versions, and a
    rewritten `what_if` purpose — because both sit inside that requirement's own `prod`
    clause and WK-671 has no environments (RL-880 clause 3). Scoring a `draft` version by
    explicit reference is the "what-if and testing" the requirement permits.

    A decline is **not** an error: `build_scoring_result` sets `outcome = "declined"` with a
    populated ladder, and FR-256 makes that a 200.
    """
    ref = _required_ref(ctx)
    compiled = await _compiled_for(
        database, blob_store, slot, workspace_id=caller.workspace_id, ref=ref
    )
    trace = ctx.options.trace if ctx.options is not None else False
    try:
        result = await score_one(compiled, ctx, trace=trace)
    except ValueError as exc:
        problem = _as_platform_error(exc)
        if problem is None:
            raise
        raise problem from exc

    await _maybe_sample_trace(database, settings, caller, ctx, result)

    return Response(content=result.model_dump_json(), media_type="application/json")


async def _maybe_sample_trace(
    database: Database,
    settings: Settings,
    caller: Caller,
    ctx: QuoteContext,
    result: ScoringResult,
) -> None:
    """FR-259's sampling decision, and the pending-row write it leads to (WK-671 Task 4B,
    RL-862). `result` is already untraced — this never sets `trace=True`; a sampled
    outcome is completed off the request path by `score.trace_produce`
    (`app.worker.trace_handlers`), not here.

    **Failures here are logged, never raised.** A caller who received a correctly-priced,
    already-serialised quote must not see it turn into a 500 because an unrelated audit
    write failed — FR-259's persistence is a monitoring concern (`03`:175), and losing
    one sample is a smaller failure than refusing to answer a quote the platform already
    successfully priced.
    """
    try:
        async with database.unit_of_work() as session:
            rate = await settings_service.resolve(
                session, settings, caller.workspace_id, "rating.trace_sample_rate"
            )
            sampled, reason = traces_service.decide_sampling(
                result.outcome, rate.effective_value, roll=random.random()
            )
            if not sampled or reason is None:
                return
            if caller.environment is None:
                # RL-916 part 3: `None` here is an impossible state, not a value to
                # stamp — it is indistinguishable from Correction 2's batch marker
                # (Task 4A), and a mislabelled row is permanent (`TRACE_RETENTION_FLOOR`,
                # `UPDATE` revoked). Unreachable under the current permission model
                # (`score:execute` has no builtin role and no roles API grants it), but
                # raising rather than stamping keeps it unreachable by construction. The
                # enclosing `try` degrades this to "logged, quote still served" — the
                # correct outcome for a caller this should never happen to.
                raise RuntimeError(
                    "sampled real-time trace has no caller.environment; refusing to write "
                    "a row indistinguishable from a batch-produced one"
                )
            row = await traces_service.write_pending_trace(
                session,
                workspace_id=caller.workspace_id,
                quote_id=ctx.quote_id,
                rating_version_ref=str(result.rating_version_ref),
                bundle_hash=result.bundle_hash,
                sample_reason=reason,
                environment=caller.environment,
                quote_context=ctx.model_dump(mode="json"),
                served_summary=traces_service.summarise_result(result),
            )
            await job_service.submit(
                session,
                JobKind.SCORE_TRACE_PRODUCE,
                {**job_identity(caller), "scoring_trace_id": str(row.id)},
                caller.principal,
                workspace_id=caller.workspace_id,
            )
    except Exception:
        _log.exception(
            "trace sampling failed; the quote was still served",
            extra={"workspace_id": str(caller.workspace_id), "outcome": result.outcome},
        )


class BatchScoreRequest(BaseModel):
    """`POST /score/batch`'s body (`03` §5.1:517, FR-253).

    `rating_version_refs` accepts **one or more** refs (FR-253) — `score_batch`'s own
    signature (`03` §5.2) takes exactly one `CompiledBundle`, so multiple versions is this
    route/handler looping bundles, never a widened `score_batch` signature (RL-923 §3
    forbids that). `chunk_rows` and `abort_failure_rate` are left unset by default so the
    handler's own default (RL-889's workspace-setting resolution) applies rather than a
    route-level guess.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_version_id: UUID
    rating_version_refs: list[ArtifactRef] = Field(min_length=1)
    table_name: str | None = None
    chunk_rows: int | None = Field(default=None, gt=0)
    #: A request-supplied threshold may only *lower* the resolved workspace setting
    #: (`rating.batch_abort_failure_rate`, RL-889) — enforced by the handler
    #: (`BATCH_ABORT_THRESHOLD_ABOVE_SETTING`), not here.
    abort_failure_rate: float | None = Field(default=None, ge=0, le=1)


@router.post(
    "/score/batch",
    summary="Batch re-rate a Dataset Version against one or more Rating Versions",
    status_code=202,
    # 404: the Dataset Version, its scoring table, or a named `rating_version_ref` does not
    # resolve — raised inside the handler (`app.worker.scoring_handlers`), not this route;
    # listed because a client polling the Job can observe it as the terminal failure. 409:
    # `BUNDLE_COMPILE_FAILED`, also handler-side. 422:
    # `BATCH_ABORT_THRESHOLD_ABOVE_SETTING` (RL-889) and request-body validation.
    responses=problems(401, 403, 404, 409, 422),
)
async def score_batch(
    body: BatchScoreRequest,
    caller: ScoreBatchDep,
    database: DatabaseDep,
    response: Response,
) -> Job:
    """**202** with a Job (`03` §5.1:517, FR-253/254/255; WK-671 Task 3C).

    Submits a `JobKind.SCORE_BATCH` Job — chunked, progress-reporting, resumable
    (`app.worker.scoring_handlers`) — never scores inline. Polling the returned Job to
    completion yields a `JobResult(kind="blob")` whose `ref` is a small JSON summary
    naming, per Rating Version, the content-addressed output parquet's own blob ref, row
    and outcome counts, per-error-type counts and samples, and whether that ref's run
    aborted.

    This route resolves nothing itself: bundle resolution, the manifest, the abort
    threshold and the output are all the handler's (`docs/plans/PL-00849-wk-671-slice-3
    -batch-scoring-the-pure-transform-the-checkpointing-handler-and-the-route.md` Task 3B). Widening this route to score inline would duplicate that
    machinery, exactly what `CLAUDE.md` §2 forbids.
    """
    parameters: dict[str, Any] = {
        **job_identity(caller),
        "dataset_version_id": str(body.dataset_version_id),
        "rating_version_refs": [str(ref) for ref in body.rating_version_refs],
        "table_name": body.table_name,
        "chunk_rows": body.chunk_rows,
        "abort_failure_rate": body.abort_failure_rate,
    }
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.SCORE_BATCH,
            parameters,
            caller.principal,
            workspace_id=caller.workspace_id,
        )
    response.status_code = status.HTTP_202_ACCEPTED
    response.headers["Location"] = f"/api/v1/jobs/{job.id}"
    return job
