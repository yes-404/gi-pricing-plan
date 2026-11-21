"""The one place a stored Bundle is hydrated (FR-243, FR-240; WK-2113 S3).

`hydrate` is the only caller of `load_bundle` in `backend/src`, so a Bundle compiled before the
`control`-intent guard existed cannot price: `load_bundle` refuses it with a load-guard code
(`LOAD_GUARD_CODES`: `CONTROL_FACTOR_IN_RATEABLE_PATH`; `MODEL_TERM_UNRESOLVED` for a GLM level
its Factor cannot produce; `RATING_VERSION_UNPINNED` for a payload the Bundle pins and does not
carry), and this wrapper turns that into a decided answer — a 409 problem (the request is
valid; the stored artifact conflicts with the current rules), never a 500 — and records the
refusal as an Audit Event (NFR-498). `test_hydration_census` holds both "only caller" claims.

**The event survives the refusal**: it is written in its own transaction, because the request
that raises would otherwise roll it back. **One event per process per hash** (DP-1): the slot's
refused-hash memo de-duplicates the event and nothing else — every request is still refused,
because the guard runs on every hydrate (a hash covers the pins, not the carried payloads).
"""

from __future__ import annotations

from collections.abc import Awaitable, Mapping
from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BlobRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import audit
from app.platform import rating_versions as rating_versions_service
from app.platform.blobs import BlobStore, to_ref
from app.platform.bundle_slot import BundleSlot
from model_schema import ActorKind, ArtifactRef, JobSource, Principal
from pricing_core.rating.compile import Bundle, check_rateable_intent
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.safe_error import CodedError

__all__ = [
    "LOAD_GUARD_CODES",
    "REFUSAL_ACTION",
    "Revalidate",
    "hydrate",
    "revalidate",
    "revalidator",
]

#: The load-guard codes `load_bundle` refuses a stored Bundle with, each mapped to the 409's title.
#: A `CodedError` carrying any other code is not a decided answer and is re-raised (FD-1495 for the
#: first; FR-193 and FR-243 for the second). `test_bundle_hydration.py` fails when a code is added
#: here without a row there.
LOAD_GUARD_CODES: Mapping[str, str] = {
    "CONTROL_FACTOR_IN_RATEABLE_PATH": "A stored bundle prices on a control-intent Factor",
    "MODEL_TERM_UNRESOLVED": "A stored bundle prices a level its Factor cannot produce",
    "RATING_VERSION_UNPINNED": "A stored bundle does not carry what it pins",
}
#: The Audit Event action for a refused load (`03` §4.3, NFR-498).
REFUSAL_ACTION = "rating_version.load_refused"
_ACTOR = Principal(kind=ActorKind.SYSTEM, display="bundle-guard")


def unreadable_bundle(ref: ArtifactRef | str, why: str) -> PlatformError:
    """A version whose bundle cannot be read to be re-validated: refused, never served."""
    return PlatformError(
        "BUNDLE_COMPILE_FAILED",
        "The bundle cannot be re-validated",
        409,
        f"{ref}: the bundle cannot be re-validated ({why}).",
    )


async def _record_refusal(
    slot: BundleSlot,
    database: Database,
    *,
    workspace_id: UUID,
    ref: ArtifactRef,
    content_hash: str,
    refusal: str,
    acting: Principal | None,
    requester: Principal | None,
) -> None:
    """Evict the hash and write the refusal's Audit Event (`_refuse`'s first two acts).

    **A governance act** (`acting` set: submit, deploy, rollback) writes its OWN event with the
    acting principal as actor, every time, never de-duplicated and never touching the memo.
    **A load refusal** (scoring, regression, dislocation, PREPARE) is the platform's, so its actor
    is the system principal (the audit contract permits one: `Principal.kind` includes `system`,
    `model_schema/jobs.py`; `AuditEvent.actor` is a `Principal`; `06` FR-369's source has
    `system`), with the requesting principal recorded in `after` where the caller has one, and the
    event is written once per process per hash (DP-1).
    """
    slot.discard(content_hash)
    first = acting is not None or slot.first_refusal(content_hash)
    if first:
        after: dict[str, str] = {"bundle_hash": content_hash, "refusal": refusal}
        if acting is None:
            after["note"] = "first refusal in this worker"
            if requester is not None and requester.id is not None:
                after["requested_by"] = str(requester.id)
        try:
            async with database.unit_of_work() as session:
                await audit.record(
                    session,
                    workspace_id=workspace_id,
                    actor=acting or _ACTOR,
                    source=JobSource.API if acting is not None else JobSource.SYSTEM,
                    action=REFUSAL_ACTION,
                    entity_ref=str(ref),
                    before=None,
                    after=after,
                )
        except BaseException:
            if acting is None:
                slot.unrecord_refusal(content_hash)
            raise


async def _refuse(
    slot: BundleSlot,
    database: Database,
    *,
    workspace_id: UUID,
    ref: ArtifactRef,
    content_hash: str,
    code: str,
    refusal: str,
    acting: Principal | None,
    requester: Principal | None,
) -> PlatformError:
    """The refusal as a decided answer: evict the hash, audit it, return the 409."""
    await _record_refusal(
        slot,
        database,
        workspace_id=workspace_id,
        ref=ref,
        content_hash=content_hash,
        refusal=refusal,
        acting=acting,
        requester=requester,
    )
    return PlatformError(
        code,
        LOAD_GUARD_CODES[code],
        409,
        f"{ref} (bundle {content_hash}) is refused: {refusal}. Compile a new Rating Version; "
        "a compiled version is never mutated.",
    )


def _load_guard_refusal(exc: CodedError) -> tuple[str, str] | None:
    """`(code, text after the code)` when `exc` is a load-guard refusal, else `None`."""
    code, separator, refusal = str(exc).partition(": ")
    return (code, refusal) if separator and code in LOAD_GUARD_CODES else None


async def hydrate(
    bundle: Bundle,
    *,
    slot: BundleSlot,
    database: Database,
    workspace_id: UUID,
    ref: ArtifactRef,
    requester: Principal | None = None,
    acting: Principal | None = None,
) -> CompiledBundle:
    """`load_bundle`, with its `control`-intent refusal mapped to a 409 and audited.

    `acting` is set only by `revalidate` (a governance act, audited every time as that principal);
    `requester` is the principal behind a scoring request, where there is one."""
    try:
        return load_bundle(bundle)
    except CodedError as exc:
        guard = _load_guard_refusal(exc)
        if guard is None:
            raise
        raise await _refuse(
            slot,
            database,
            workspace_id=workspace_id,
            ref=ref,
            content_hash=bundle.content_hash,
            code=guard[0],
            refusal=guard[1],
            acting=acting,
            requester=requester,
        ) from None


async def revalidate(
    session: AsyncSession,
    *,
    database: Database,
    blob_store: BlobStore,
    slot: BundleSlot,
    workspace_id: UUID,
    ref: ArtifactRef,
    actor: Principal,
) -> None:
    """Re-validate a stored version at submit, deploy and rollback (FR-88, FR-240, FR-267/269).

    Two halves, because a Bundle carries only some of what the guard reads: the stored blob goes
    through `hydrate` (the GLM Factors it carries), and the pins are re-resolved through
    `check_rateable_intent` (a rate table key's Factor and a GBM's features, which the Bundle
    does not carry). A version whose bundle cannot be read is refused, never skipped: a
    hash with no blob cannot be shown clean (ruling 2026-11-13 21:23:21).
    """
    row = await rating_versions_service.resolve_rating_version_ref(
        session, workspace_id=workspace_id, ref=ref
    )
    blob_sha256 = (row.bundle or {}).get("blob_sha256")
    blob_row = await session.get(BlobRow, blob_sha256) if blob_sha256 else None
    if blob_row is None:
        raise unreadable_bundle(ref, "it has no readable stored bundle")
    bundle = Bundle.model_validate_json(await blob_store.read(to_ref(blob_row)))
    await hydrate(
        bundle, slot=slot, database=database, workspace_id=workspace_id, ref=ref, acting=actor
    )
    version = rating_versions_service.to_schema(row)
    if version.algorithm_ref is None or version.pins is None:
        # A version that never declared pins has no rate table key or GBM pin to re-resolve, and
        # compile refuses to produce a bundle without them (FR-237): only a row that is not a real
        # compiled version reaches here, and the stored bundle was checked above.
        return
    resolver = rating_versions_service.WorkspaceResolver(session, workspace_id, blob_store)
    try:
        await check_rateable_intent(version, resolver)
    except CodedError as exc:
        guard = _load_guard_refusal(exc)
        if guard is None:
            raise
        raise await _refuse(
            slot,
            database,
            workspace_id=workspace_id,
            ref=ref,
            content_hash=bundle.content_hash,
            code=guard[0],
            refusal=guard[1],
            acting=actor,
            requester=None,
        ) from None
    except PlatformError as exc:
        # A pin the resolver refuses (a pinned model whose offset source has an offset of its own,
        # FR-116, a pin that no longer resolves): the resolver refuses it as a `PlatformError`,
        # which is already the answer's status, but a governance refusal also writes its own
        # event every time (FR-243). Every 4xx the resolver raises is a decided refusal and is
        # recorded, then re-raised unchanged. A 5xx is an outage, not a decision, and an outage is
        # never recorded as a refusal. None of these is a load-guard code, so `hydrate` never
        # sees them.
        if not 400 <= exc.status_code < 500:
            raise
        await _record_refusal(
            slot,
            database,
            workspace_id=workspace_id,
            ref=ref,
            content_hash=bundle.content_hash,
            refusal=f"{exc.code}: {exc.detail}",
            acting=actor,
            requester=None,
        )
        raise


class Revalidate(Protocol):
    """`revalidate` with the process's handles and the workspace bound (a route builds one)."""

    def __call__(self, session: AsyncSession, *, ref: ArtifactRef) -> Awaitable[None]: ...


def revalidator(
    *,
    database: Database,
    blob_store: BlobStore,
    slot: BundleSlot,
    workspace_id: UUID,
    actor: Principal,
) -> Revalidate:
    async def bound(session: AsyncSession, *, ref: ArtifactRef) -> None:
        await revalidate(
            session,
            database=database,
            blob_store=blob_store,
            slot=slot,
            workspace_id=workspace_id,
            ref=ref,
            actor=actor,
        )

    return bound
