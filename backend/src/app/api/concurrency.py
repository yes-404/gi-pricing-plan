"""`If-Match` optimistic concurrency (`00` §5.4, FR-PLAT-47).

> Mutating requests on versioned entities require `If-Match: <etag>`; a mismatch yields
> `409 CONFLICT_STALE_WRITE`.

**What this guards, stated precisely, because two workstreams deferred it for being
misdescribed.** W2 recorded it as not applicable — no W2 resource is a versioned entity —
and W4 recorded it as "a second, weaker guard over the same field", which was true of W4's
routes: they mutate a status, and the transition state machine already refuses every unsafe
move by reading that status under a row lock.

Neither reason makes the header decoration. What it adds is a **precondition on the caller's
view**, which a state machine cannot supply: without it a stale client is told "your
transition is invalid", and it cannot tell that answer apart from "you asked for something
that was never legal". With it the answer is "what you read is stale, read it again" — the
only one of the two a screen can act on without guessing.

So: the ETag is over the fields a transition changes, and the mechanism lives here rather
than in one module's routes, because `00` §5.4 is a convention every versioned entity obeys.
"""

from __future__ import annotations

from app.errors import PlatformError

__all__ = ["IF_MATCH_DESCRIPTION", "etag_for", "require_if_match"]

#: Reused in every route's OpenAPI parameter description, so the published contract says the
#: same thing in each place. A generated client is written against this text.
IF_MATCH_DESCRIPTION = (
    "The entity's current `ETag`, from a prior `GET`. Required (`00` §5.4); a mismatch or "
    "an absent header yields `409 CONFLICT_STALE_WRITE`."
)


def etag_for(*parts: object) -> str:
    """A weak ETag over the parts that a mutation changes.

    Readable rather than opaque — `W/"model:motor-ad-frequency@7:fitted"` — for the reason
    `spec_hash` carries a `v2:sha256:` prefix instead of bare hex: the value appears in
    logs, in dashboards and in support conversations, and one a person can read is one they
    can reason about. Nothing sensitive is in it that a caller who can `GET` the entity does
    not already have.

    **Weak** (`W/`) is correct here and not a hedge: the tag identifies the entity's state
    for the purposes of a precondition, not a byte-identical representation, and the
    response body varies with the caller's serialisation (`?version=`, field selection).
    """
    return 'W/"' + ":".join(str(part) for part in parts) + '"'


def require_if_match(supplied: str | None, current: str) -> None:
    """Refuse the request unless the caller's `If-Match` names the current state.

    Takes the header's **value**, not the `Request`. The route declares `If-Match` as a
    parameter so that it appears in the published contract a client generates from, and a
    helper that then went behind the route's back to read the raw request would leave that
    declared parameter unused — which is how a documented header stops being the one the
    server actually reads.

    `If-Match: *` is **refused**, not honoured. RFC 9110 gives it the meaning "if the
    resource exists at all", which is precisely the precondition `00` §5.4 exists to
    replace — accepting it would let any client opt out of concurrency control by sending
    one character, and a rule a caller can disable is not one.
    """
    supplied = (supplied or "").strip()
    if not supplied:
        raise PlatformError(
            "CONFLICT_STALE_WRITE",
            "This request requires an If-Match header",
            409,
            f"`00` §5.4: mutating requests on versioned entities require "
            f"`If-Match: <etag>`. The entity's current ETag is {current}, available from a "
            "`GET` of the same resource.",
        )
    if supplied == "*":
        raise PlatformError(
            "CONFLICT_STALE_WRITE",
            "If-Match: * is not accepted here",
            409,
            "RFC 9110 gives `*` the meaning 'if the resource exists', which is the "
            "precondition `00` §5.4 replaces rather than the one it asks for. Send the "
            f"entity's ETag: {current}.",
        )
    if supplied != current:
        raise PlatformError(
            "CONFLICT_STALE_WRITE",
            "The entity has changed since you read it",
            409,
            f"You supplied {supplied}; the current ETag is {current}. Re-read the entity "
            "and decide again — the state you acted on is not the state that exists.",
        )
