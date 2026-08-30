"""`POST /api/v1/score` — real-time scoring (03 §5.1, FR-RATE-34/35/38/39; W11 Task 2B).

**`async def`, and not incidentally.** `BundleSlot` is unsynchronised and confined to one
worker's event loop; FastAPI runs a plain `def` handler in a threadpool, which would put two
threads on that object and reach the race its docstring documents. A synchronous handler here
is a defect, not a style choice.

**No `response_model=`, and no Pydantic return annotation** (NFR-RATE-13 as amended by
Ruling 17). The requirement is *validate inbound, never outbound*: `QuoteContext` is untrusted
and is validated; `ScoringResult` is built by `pricing-core` and is already trusted, so it is
serialised with Pydantic v2's compiled encoder and returned in a raw `Response`. A return-type
annotation is precisely what FastAPI's own `ORJSONResponse` deprecation notice recommends, and
precisely what this requirement forbids — an annotated route filters extra keys and answers
500 on a shape that violates its model, which is outbound validation by another name.

**The error boundary is this module's.** `pricing-core` cannot import `PlatformError`
(ADR-0001), so `score_one` raises a code-named bare `ValueError` — `f"{code}: {message}"`. The
codes are parsed off the front and mapped here. Deliberately *not* mapped: a firing
`on_violation="error"` constraint raises a plain `NotImplementedError`, which is undesigned and
must stay visible as a 500 rather than be dressed as a typed per-quote error.
"""

from __future__ import annotations

from typing import Annotated, Final
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response

from app.api.authz import requires
from app.api.deps import Caller
from app.api.responses import problems
from app.db.models import BlobRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import rating_versions as rating_versions_service
from app.platform.blobs import BlobStore, to_ref
from app.platform.bundle_slot import BundleSlot
from model_schema import ArtifactRef, Permission, QuoteContext
from pricing_core.rating.compile import Bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_one

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


def _required_ref(ctx: QuoteContext) -> ArtifactRef:
    """The explicit ref, or Ruling 14's refusal.

    Raised *here*, before `score_one`, and that ordering is the whole point. `score_one`
    also refuses a missing ref — with `INPUT_CONTRACT_VIOLATION`, its own input-contract
    error — and forwarding to it would answer a caller who omitted the ref by telling them
    their input was malformed, when the truth is that this platform has no live Rating
    Version to score against. `live` is a property of a Deployment (FR-RATE-23), which is
    W14's; until then the endpoint refuses rather than guessing which version is live.

    The branch is permanent rather than a stub: after W14 it is what an environment holding
    no Deployment answers, and W14 narrows the trigger instead of deleting a placeholder.
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
    *,
    workspace_id: UUID,
    ref: ArtifactRef,
) -> Bundle:
    """Resolve a ref to its compiled `Bundle`: one metadata read, then the blob store.

    The blob key lives on the version's own metadata (Ruling 37), so this is a single
    keyed read rather than a scan of Job history for the latest successful compile — which
    would put an un-indexed JSONB lookup inside NFR-RATE-1's budget and, worse, decide
    *which* compiled artifact a version is inside a query nobody had to defend.
    """
    async with database.session() as session:
        row = await rating_versions_service.resolve_rating_version_ref(
            session, workspace_id=workspace_id, ref=ref
        )
        metadata = row.bundle or {}
        blob_sha256 = metadata.get("blob_sha256")
        if not blob_sha256:
            raise PlatformError(
                "BUNDLE_COMPILE_FAILED",
                "Rating version is not compiled",
                409,
                f"{ref} has no compiled bundle to score against. Compile it first.",
            )
        blob_row = await session.get(BlobRow, blob_sha256)
        if blob_row is None:
            raise PlatformError(
                "BUNDLE_COMPILE_FAILED",
                "Compiled bundle is missing",
                409,
                f"{ref}'s compiled bundle is no longer in the blob store.",
            )
        payload = await blob_store.read(to_ref(blob_row))
    return Bundle.model_validate_json(payload)


async def _compiled_for(
    database: Database,
    blob_store: BlobStore,
    slot: BundleSlot,
    *,
    workspace_id: UUID,
    ref: ArtifactRef,
) -> CompiledBundle:
    """The hydrated bundle for `ref`, degrading to the slot when metadata storage is down.

    NFR-RATE-9 requires degradation to *"the last-known-good cached bundle if metadata
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
        bundle = await _fetch_bundle(
            database, blob_store, workspace_id=workspace_id, ref=ref
        )
    except PlatformError:
        raise
    except Exception:
        held_hash = slot.hash_for(ref)
        compiled = slot.get(held_hash) if held_hash is not None else None
        if compiled is None:
            raise
        return compiled

    compiled = slot.get(bundle.content_hash)
    if compiled is None:
        compiled = load_bundle(bundle)
    slot.put(ref, compiled)
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
    # named version has no compiled bundle — and 422 carries FR-RATE-38's four per-quote
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
) -> Response:
    """Score one quote (FR-RATE-34/35).

    W11 imposes neither of FR-RATE-35's restrictions — approved-only versions, and a
    rewritten `what_if` purpose — because both sit inside that requirement's own `prod`
    clause and W11 has no environments (Ruling 14 clause 3). Scoring a `draft` version by
    explicit reference is the "what-if and testing" the requirement permits.

    A decline is **not** an error: `build_scoring_result` sets `outcome = "declined"` with a
    populated ladder, and FR-RATE-39 makes that a 200.
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

    return Response(content=result.model_dump_json(), media_type="application/json")
