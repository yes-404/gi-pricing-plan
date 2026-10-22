"""`POST /api/v1/score` — real-time scoring (03 §5.1, FR-250/251/255/256; WK-671 Task 2B) and
`POST /api/v1/score/batch` — batch re-rating (03 §5.1:517, FR-253/254/255; WK-671 Task 3C).

**`/score` scores untraced and never sets `trace=True` for FR-259's sake** (WK-671 Task
4B; RL-862,
`docs/rulings/RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md`).
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
The 200 is documented through `responses=`, which FastAPI reads only when it builds the
OpenAPI document: the contract carries the shape and nothing validates the body (FD-1335).

**The error boundary is this module's.** `pricing-core` cannot import `PlatformError`
(ADR-703), so `score_one` raises a code-named bare `ValueError` — `f"{code}: {message}"`. The
codes are parsed off the front and mapped here. Deliberately *not* mapped: a firing
`on_violation="error"` constraint raises a plain `NotImplementedError`, which is undesigned and
must stay visible as a 500 rather than be dressed as a typed per-quote error.

**`/score/batch` submits a Job and nothing else.** It carries no bundle-resolution logic of
its own — that lives in `_compiled_for`/`_fetch_bundle` above, reused (not duplicated,
RL-922) by `app.worker.scoring_handlers`. The route's only responsibilities are to
authorise the caller against `Permission.SCORE_BATCH` (granted by no builtin role, deliberately
— FR-347, C3 of
`docs/plans/PL-00849-wk-671-slice-3-batch-scoring-the-pure-transform-the-checkpointing-handler-and-the-route.md`)
and to translate the request body into the `score.batch` handler's parameter shape.
"""

from __future__ import annotations

import random
from typing import Annotated, Any, Final
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTask

from app.api.authz import requires
from app.api.deps import Caller, RequestSessionDep, SettingsDep, job_identity
from app.api.rating_algorithms import RatingReadDep
from app.api.responses import problems
from app.config import Settings
from app.db.models import BlobRow
from app.db.session import Database, reading
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.observability.metrics import ladder_reconciliation_failed
from app.platform import jobs as job_service
from app.platform import rate_limit
from app.platform import rating_versions as rating_versions_service
from app.platform import routing as routing_service
from app.platform import settings as settings_service
from app.platform import shadow as shadow_service
from app.platform import traces as traces_service
from app.platform.blobs import BlobStore, to_ref
from app.platform.bundle_slot import BundleSlot
from app.platform.deployment_switch import LiveRefs, SwitchMessage
from app.platform.safe_exception import safe_job_exc_info
from model_schema import (
    ArtifactRef,
    Job,
    JobKind,
    Permission,
    QuoteContext,
    QuoteContextOptions,
    RatingAlgorithm,
    ScoreCompareRequest,
    ScoreComparison,
    ScoringResult,
)
from pricing_core.rating.compile import Bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_one
from pricing_core.rating.trace_diff import diff_traces
from pricing_core.safe_error import CodedError

_log = get_logger("app.api.score")

router = APIRouter(tags=["rating"])

#: The per-quote codes `score_one` raises as code-named `ValueError`s, each already owned by
#: `03` §5.1 and registered in `app.errors`. A code outside this set is not a per-quote
#: refusal and must not be turned into one — it reaches the caller as a 500, with one named
#: exception: `LADDER_RECONCILIATION_FAILED` (`RL-1346`), mapped explicitly to a 500 that
#: carries its code, in `_as_platform_error`.
_PER_QUOTE_CODES: Final[frozenset[str]] = frozenset(
    {
        "INPUT_CONTRACT_VIOLATION",
        "RATE_TABLE_MISS",
        "REFERENCE_LOOKUP_MISS",
        "MODEL_CALL_FAILED",
    }
)

#: `RL-1346`: a ladder that does not reconcile is a platform fault, not the caller's input.
_LADDER_REFUSAL_CODE: Final[str] = "LADDER_RECONCILIATION_FAILED"
_LADDER_REFUSAL_STATUS: Final[int] = 500
_LADDER_REFUSAL_NOTE: Final[str] = (
    "The failure is deterministic for this Rating Version and quote: a retry fails the same way."
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


def _live_refs(request: Request) -> LiveRefs:
    live: LiveRefs = request.app.state.live_refs
    return live


LiveRefsDep = Annotated[LiveRefs, Depends(_live_refs)]
#: `keep_session`: `/score`'s own reads continue on the request session the check used, so a
#: warm quote takes one pool checkout (RL-1685, PL-1454 DP-1 (a)). `management_counted=False`:
#: the scoring limit counts this route, not FR-452's management limit (`RL-1687`).
ScoreExecuteDep = Annotated[
    Caller,
    Depends(requires(Permission.SCORE_EXECUTE, keep_session=True, management_counted=False)),
]


async def _enforce_score_rate_limit(
    request: Request, caller: ScoreExecuteDep, session: RequestSessionDep, settings: SettingsDep
) -> None:
    """FR-452's scoring limit: after authentication and `score:execute`, before any scoring,
    so a 401 or 403 is never counted and a refused request scores nothing (RL-1347 rule 4)."""
    await rate_limit.enforce(
        request.app.state.rate_limiter,
        session,
        settings,
        route="score",
        default_setting="scoring.default_client_rate_limit_rps",
        workspace_id=caller.workspace_id,
        environment=caller.environment,
        principal=caller.principal,
        account_limit=caller.rate_limit_rps,
    )


#: The route declares `ScoreExecuteDep` itself, so the authorisation sweep sees its
#: permission; the limiter reuses that one resolved dependency and adds no second check.
ScoreRateLimitDep = Annotated[None, Depends(_enforce_score_rate_limit)]
ScoreBatchDep = Annotated[
    Caller, Depends(requires(Permission.SCORE_BATCH, management_counted=False))
]


def _required_ref(ctx: QuoteContext, live_ref: ArtifactRef | None = None) -> ArtifactRef:
    """The explicit ref, else the environment's live Rating Version, else RL-880's refusal.

    Raised *here*, before `score_one`, and that ordering is the whole point. `score_one`
    also refuses a missing ref — with `INPUT_CONTRACT_VIOLATION`, its own input-contract
    error — and forwarding to it would answer a caller who omitted the ref by telling them
    their input was malformed, when the truth is that this platform has no live Rating
    Version to score against. `live` is a property of a Deployment (FR-238).

    *(Dated 2026-10-04, WK-674 Slice 2 Task 6: the original text read "which is WK-674's;
    until then the endpoint refuses rather than guessing which version is live".)* WK-674
    has landed the Deployment, so `live_ref` is the Rating Version of the caller's
    Environment's live Deployment (`_serving_ref` resolves it). The refusal is unchanged and
    permanent: it is what an environment holding no Deployment, or a caller holding no
    environment, answers, and WK-674 narrowed the trigger instead of deleting a placeholder.
    """
    ref = ctx.options.rating_version_ref if ctx.options is not None else None
    if ref is None:
        ref = live_ref
    if ref is None:
        raise PlatformError(
            "NO_LIVE_RATING_VERSION",
            "No live Rating Version",
            409,
            "This environment has no live Rating Version to score against. Supply "
            "options.rating_version_ref explicitly, or deploy a Rating Version to it.",
        )
    return ref


def _serving_ref(
    live_refs: LiveRefs, caller: Caller, ctx: QuoteContext
) -> tuple[ArtifactRef, UUID | None]:
    """The ref to score and the Deployment that serves it, resolved together and once.

    `live` is this process's own reference (`platform.deployment_switch.LiveRefs`), read once
    here at request start and never re-read (FR-268, `PL-1766` D5.8, the maintainer's
    "2026-10-18 23:03:15 BST" ruling (A)): a switch committing while the quote is in flight
    does not relink its trace. For a default-live quote it is the caller's Environment's live
    Deployment; for an explicit ref it is that Deployment only when it serves exactly that
    Rating Version (type, slug and version), else `None`: a what-if quote is not pretended to be
    a served one. A caller with no Environment (a bearer caller) has no live Deployment.

    **The trade-off that ruling states:** this used to read the latest committed Deployment
    from Postgres on every request, so a deployment converged at once. A process that is alive
    but missed the COMMIT now serves the previous version until it restarts and loads the latest
    committed Deployment. The deploy response and `deployment.switched` name such a process;
    the remedy is FD-1823 (MEDIUM, WK-674, before the 12 Nov exit demo).

    Deliberately **not** inside `_fetch_bundle` or `_compiled_for`: the governance gate and
    both workers call those and must not change with this (`PL-1392` Acceptance 17).
    """
    entry = (
        live_refs.get(caller.workspace_id, caller.environment)
        if caller.environment is not None
        else None
    )
    ref = _required_ref(ctx, ArtifactRef.parse(entry.rating_version_ref) if entry else None)
    served_by = (
        entry.deployment_id if entry is not None and entry.rating_version_ref == str(ref) else None
    )
    return ref, served_by


def _names_no_version(ctx: QuoteContext) -> bool:
    """A default-live quote: it names no Rating Version, so the Environment serves it."""
    return ctx.options is None or ctx.options.rating_version_ref is None


async def _shadow_task(
    session: AsyncSession,
    settings: Settings,
    caller: Caller,
    ctx: QuoteContext,
    live: ScoringResult,
    live_deployment_id: UUID | None,
    database: Database,
    blob_store: BlobStore,
    slot: BundleSlot,
) -> BackgroundTask | None:
    """The shadow scoring to run after the response is sent, or `None` (`03` FR-271,
    `RL-1834` D2 item 4).

    Attached only for a default-live quote, when the Environment's shadow flag resolves true, a
    configuration exists and a draw falls below its fraction. With the flag off nothing more is
    read. A failure of the decision is logged and never raised: the quote is already priced.
    """
    if caller.environment is None:
        return None
    try:
        flag = await settings_service.resolve(
            session,
            settings,
            caller.workspace_id,
            "features.shadow_scoring_enabled",
            caller.environment,
        )
        if flag.effective_value is not True:
            return None
        config = await shadow_service.current(
            session, workspace_id=caller.workspace_id, environment=caller.environment
        )
        if config is None or random.random() >= config[1]:
            return None
    except Exception as exc:
        _log.error(
            "shadow scoring decision failed; the quote was still served",
            exc_info=safe_job_exc_info(exc),
            extra={"workspace_id": str(caller.workspace_id)},
        )
        return None
    return BackgroundTask(
        _shadow_score,
        database,
        blob_store,
        slot,
        caller.workspace_id,
        caller.environment,
        ctx,
        live,
        live_deployment_id,
        config[0],
    )


async def _shadow_score(
    database: Database,
    blob_store: BlobStore,
    slot: BundleSlot,
    workspace_id: UUID,
    environment: str,
    ctx: QuoteContext,
    live: ScoringResult,
    live_deployment_id: UUID | None,
    candidate_ref: ArtifactRef,
) -> None:
    """Score the same quote against the candidate and append one `shadow_results` row. Runs
    after the response; a failure is logged and never raised (the `_maybe_sample_trace`
    precedent, sanitised because the failing call carries the quote context, NFR-499)."""
    try:
        compiled = await _compiled_for(
            database, blob_store, slot, workspace_id=workspace_id, ref=candidate_ref
        )
        options = (ctx.options or QuoteContextOptions()).model_copy(
            update={"rating_version_ref": candidate_ref, "trace": False}
        )
        candidate = await score_one(
            compiled, ctx.model_copy(update={"options": options}), trace=False
        )
        async with database.unit_of_work() as session:
            await shadow_service.record_result(
                session,
                workspace_id=workspace_id,
                environment=environment,
                live_deployment_id=live_deployment_id,
                live=live,
                candidate=candidate,
            )
    except Exception as exc:
        _log.error(
            "shadow scoring failed; the response was already sent",
            exc_info=safe_job_exc_info(exc),
            extra={"workspace_id": str(workspace_id), "candidate": str(candidate_ref)},
        )


async def _routed(
    session: AsyncSession, settings: Settings, caller: Caller, ctx: QuoteContext
) -> tuple[ArtifactRef, UUID] | None:
    """The Rating Version and Deployment date routing selects, or `None` to keep what
    `_serving_ref` resolved (`03` FR-270, `RL-1834` D1 item 5).

    Entered only for a default-live quote (no explicit ref) of a caller with an Environment,
    and only when the Environment's routing flag resolves true: with the flag off the selector
    is not called and the path is `_serving_ref`'s alone. The flag is read per request through
    the request's session (the `RL-1685` pattern), so a flag write takes effect at once.
    """
    if caller.environment is None or not _names_no_version(ctx):
        return None
    flag = await settings_service.resolve(
        session, settings, caller.workspace_id, "features.date_routing_enabled", caller.environment
    )
    if flag.effective_value is not True:
        return None
    return await routing_service.select_range(
        session,
        workspace_id=caller.workspace_id,
        environment=caller.environment,
        effective_date=ctx.effective_date,
    )


def _with_resolved_ref(ctx: QuoteContext, ref: ArtifactRef) -> QuoteContext:
    """`ctx` carrying `ref` as `options.rating_version_ref`, as a copy. An explicit ref is
    already `ref` (`_required_ref` returns it) and is returned untouched."""
    if ctx.options is not None and ctx.options.rating_version_ref is not None:
        return ctx
    options = (
        ctx.options.model_copy(update={"rating_version_ref": ref})
        if ctx.options is not None
        else QuoteContextOptions(rating_version_ref=ref)
    )
    return ctx.model_copy(update={"options": options})


async def _fetch_bundle(
    source: Database | AsyncSession,
    blob_store: BlobStore,
    slot: BundleSlot,
    *,
    workspace_id: UUID,
    ref: ArtifactRef,
) -> CompiledBundle:
    """Resolve a ref to its hydrated `CompiledBundle`: one metadata read, then either a
    slot hit or the blob store (RL-921,
    `docs/plans/2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md`).

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

    `source` is the request's session on `/score` (one pool checkout for the whole request,
    RL-1685) and the `Database` for a worker or the governance gate, which have no request.
    """
    async with reading(source) as session:
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


async def hydrate_for_switch(
    database: Database, blob_store: BlobStore, slot: BundleSlot, message: SwitchMessage
) -> None:
    """PREPARE's hydration (`PL-1766` D5.9): load the bundle a Deployment names into this
    process's slot, and refuse (so the process does not acknowledge) when what was loaded is
    not the bundle the Deployment recorded."""
    compiled = await _fetch_bundle(
        database,
        blob_store,
        slot,
        workspace_id=message.workspace_id,
        ref=ArtifactRef.parse(message.rating_version_ref),
    )
    if f"sha256:{compiled.content_hash.removeprefix('sha256:')}" != message.bundle_hash:
        raise PlatformError(
            "BUNDLE_COMPILE_FAILED",
            "The bundle does not match the Deployment",
            409,
            f"{message.rating_version_ref} hydrated to {compiled.content_hash}, but the "
            f"Deployment records {message.bundle_hash}.",
        )


async def _compiled_for(
    source: Database | AsyncSession,
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
        return await _fetch_bundle(source, blob_store, slot, workspace_id=workspace_id, ref=ref)
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

    Only a `CodedError` qualifies (NFR-499): it is the class `pricing-core` raises for its own
    input-free `f"{code}: {message}"` text, so a library's `ValueError("RATE_TABLE_MISS: <value>")`
    is never parsed and never echoed into a response. The code is parsed off the front rather than
    matched against the whole message: the message half is prose that will change. Anything else,
    or a prefix that is not a per-quote code, is left alone — returning `None` lets the caller
    re-raise, so an unrecognised failure surfaces as a 500 instead of being labelled with
    whichever code happened to be nearest.
    """
    if not isinstance(exc, CodedError):
        return None
    code, separator, detail = str(exc).partition(": ")
    if separator and code == _LADDER_REFUSAL_CODE:
        # RL-1346 §4: a named 500 beside the per-quote 422s, so no other unmapped code gains a
        # status. The text is `build_scoring_result`'s own input-free clause, rungs and difference.
        return PlatformError(
            code,
            "Ladder reconciliation failed",
            _LADDER_REFUSAL_STATUS,
            f"{detail}. {_LADDER_REFUSAL_NOTE}",
        )
    if not separator or code not in _PER_QUOTE_CODES:
        return None
    return PlatformError(code, code.replace("_", " ").title(), _PER_QUOTE_STATUS, detail or None)


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
    responses={**problems(401, 403, 404, 409, 422, 429, 500), 200: {"model": ScoringResult}},
)
async def score(
    ctx: QuoteContext,
    caller: ScoreExecuteDep,
    _rate_limit: ScoreRateLimitDep,
    session: RequestSessionDep,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
    slot: BundleSlotDep,
    live_refs: LiveRefsDep,
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
    ref, deployment_id = _serving_ref(live_refs, caller, ctx)
    routed = await _routed(session, settings, caller, ctx)
    if routed is not None:
        ref, deployment_id = routed
    compiled = await _compiled_for(
        session, blob_store, slot, workspace_id=caller.workspace_id, ref=ref
    )
    trace = ctx.options.trace if ctx.options is not None else False
    # `score_one` refuses a context without `options.rating_version_ref` and reads the ref it
    # reports from there. A default-live quote has none, so it is stamped on an immutable copy
    # (never the request); the copy is also what a sampled trace stores, so the off-path
    # re-score (`score.trace_produce`) is not refused for the same gap.
    default_live = _names_no_version(ctx)
    ctx = _with_resolved_ref(ctx, ref)
    try:
        result = await score_one(compiled, ctx, trace=trace)
    except ValueError as exc:
        problem = _as_platform_error(exc)
        if problem is None:
            raise
        if problem.code == _LADDER_REFUSAL_CODE:
            _record_ladder_refusal(caller, compiled, ref, problem)
        raise problem from exc

    # Decided before the trace step, which may close the request's read session.
    shadow = (
        await _shadow_task(
            session, settings, caller, ctx, result, deployment_id, database, blob_store, slot
        )
        if default_live
        else None
    )
    await _maybe_sample_trace(
        database, settings, caller, ctx, result, deployment_id, read_session=session
    )

    return Response(
        content=result.model_dump_json(), media_type="application/json", background=shadow
    )


def _record_ladder_refusal(
    caller: Caller, compiled: CompiledBundle, ref: ArtifactRef, problem: PlatformError
) -> None:
    """`RL-1346` §5: one `ERROR` line and one counter increment per refusal on `/score`. Only the
    code, the input-free message, the version, the bundle, the workspace and the Environment —
    nothing from the Quote Context (NFR-499)."""
    environment = caller.environment or ""
    ladder_reconciliation_failed.labels(environment=environment).inc()
    _log.error(
        f"{problem.code}: {problem.detail}",
        extra={
            "code": problem.code,
            "rating_version_ref": str(ref),
            "bundle_hash": compiled.content_hash,
            "workspace_id": str(caller.workspace_id),
            "environment": environment,
        },
    )


def _naming_side(problem: PlatformError, side: str) -> PlatformError:
    """`problem` with its detail prefixed by the failing side, `base` or `comparison` (DP-S4-5)."""
    detail = f"{side}: {problem.detail}" if problem.detail else side
    return PlatformError(problem.code, problem.title, problem.status_code, detail)


@router.post(
    "/score/compare",
    summary="Score one Quote Context against two Rating Versions, with a step-level diff",
    status_code=200,
    # 429: `RatingReadDep` is `requires(RATING_READ)`, which counts against the management limit
    # (FR-452); `score.router` is not included through `app.main`'s `counted()`, so it says so here.
    responses={**problems(401, 403, 404, 409, 422, 429, 500), 200: {"model": ScoreComparison}},
)
async def score_compare(
    body: ScoreCompareRequest,
    caller: RatingReadDep,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
    slot: BundleSlotDep,
) -> Response:
    """FR-262: one quote, two versions, two `score_one` calls, one step diff.

    Nothing is persisted or logged (NFR-499): unlike `/score`, this never calls
    `_maybe_sample_trace`. The two calls run one after the other, never concurrently
    (FD-1199). A per-quote error on either side answers 422 with that code and the failing
    side named in the problem (DP-S4-5).
    """
    results: list[ScoringResult] = []
    algorithms: list[RatingAlgorithm] = []
    for side, ref in (("base", body.base), ("comparison", body.comparison)):
        try:
            compiled = await _compiled_for(
                database, blob_store, slot, workspace_id=caller.workspace_id, ref=ref
            )
        except PlatformError as exc:
            raise _naming_side(exc, side) from exc
        # The algorithm that is evaluated for this purpose (RL-1628 condition 1), which the
        # trace's step ids and the diff are read against.
        algorithms.append(compiled.evaluation_for(body.context.purpose).algorithm)
        ctx = body.context.model_copy(
            update={"options": QuoteContextOptions(trace=True, rating_version_ref=ref)}
        )
        try:
            results.append(await score_one(compiled, ctx, trace=True))
        except ValueError as exc:
            problem = _as_platform_error(exc)
            if problem is None:
                raise
            raise _naming_side(problem, side) from exc
    base_result, comparison_result = results
    base_algorithm, comparison_algorithm = algorithms
    if base_result.trace is None or comparison_result.trace is None:
        raise RuntimeError("score_one(trace=True) returned no trace")
    comparison = ScoreComparison(
        base=base_result,
        comparison=comparison_result,
        diff=diff_traces(
            base_result.trace,
            comparison_result.trace,
            base_algorithm,
            comparison_algorithm,
        ),
    )
    return Response(content=comparison.model_dump_json(), media_type="application/json")


async def _maybe_sample_trace(
    database: Database,
    settings: Settings,
    caller: Caller,
    ctx: QuoteContext,
    result: ScoringResult,
    deployment_id: UUID | None = None,
    *,
    read_session: AsyncSession | None = None,
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

    The sampling rate is a read, and goes through `read_session`, the request's own, when the
    route has one (RL-1685, PL-1454 DP-1 (a)); only a sampled outcome opens the write's own
    `unit_of_work`, which keeps FR-259's failure isolation: the write commits or fails on its
    own connection, never on the session the quote's reads used.
    """
    try:
        async with reading(read_session or database) as session:
            # FR-430/FR-431: monitoring configuration is per Environment (DP-S3-3 (a)).
            rate = await settings_service.resolve(
                session,
                settings,
                caller.workspace_id,
                "rating.trace_sample_rate",
                caller.environment,
            )
        sampled, reason = traces_service.decide_sampling(
            result.outcome, rate.effective_value, roll=random.random()
        )
        if not sampled or reason is None:
            return
        if read_session is not None:
            # Release the read connection before the write takes its own: a request holds at
            # most one (audit of SL-1455, F2). The quote's reads are finished.
            await read_session.close()
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
        async with database.unit_of_work() as session:
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
                deployment_id=deployment_id,
            )
            await job_service.submit(
                session,
                JobKind.SCORE_TRACE_PRODUCE,
                {**job_identity(caller), "scoring_trace_id": str(row.id)},
                caller.principal,
                workspace_id=caller.workspace_id,
            )
    except Exception as exc:
        # Sanitised: the failing insert carries the quote context (NFR-499, RL-917).
        _log.error(
            "trace sampling failed; the quote was still served",
            exc_info=safe_job_exc_info(exc),
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
    -batch-scoring-the-pure-transform-the-checkpointing-handler-and-the-route.md` Task 3B). Widening
    this route to score inline would duplicate that machinery, exactly what `CLAUDE.md` §2 forbids.
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
