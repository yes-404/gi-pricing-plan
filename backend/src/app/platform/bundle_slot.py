"""The per-worker bundle slot (FR-RATE-65, NFR-RATE-9; W11 Slice 2, Ruling 16 option (b)).

**The first in-process cache in this backend**, which is why it is a dedicated module
rather than a dict on a router. Nothing else here holds cross-request state except
FastAPI's `app.state`, set once at startup, so there is no established pattern to follow
and a dict grown quietly inside `api/score.py` would have been one.

What it holds is a hydrated `CompiledBundle`. `Bundle` is the record — serialisable,
content-hashed, cacheable in Redis; `CompiledBundle` is the executable form and is never
serialised (FR-RATE-65, Ruling 4), so it can be held per worker and nowhere else. Holding
one is worth doing because `predict_gbm` deserialises a fresh booster handle on every
call, and NFR-RATE-1 allows 50 ms p99 for a ~200-step structure with one `exact` GBM call.

**Two indices, and the second one is not an optimisation.**

- `content_hash` → `CompiledBundle`, bounded by a **count** and evicted
  least-recently-used. Capacity is a count rather than a byte budget because nothing in
  this repository measures a hydrated bundle's footprint and NFR-RATE-4 permits 500 MB
  including boosters, so a byte bound would be an estimate wearing a number's clothes.
- `ArtifactRef` → `content_hash`, the resolution **this worker itself performed**. Without
  it NFR-RATE-9's *"degrading to the last-known-good cached bundle if metadata storage is
  unavailable"* is unreachable: the request carries a `rating_version_ref` (Ruling 14) and
  ref → `Bundle` → hash *is* a metadata read, so with metadata down there would be no hash
  to look up. This is a memo of a resolution already performed, **not** the
  `environment → current hash` pointer Ruling 10 reserves for W14 — nothing about an
  environment appears here, and environments select nothing in W11.

**Corrected 2026-08-30 (F50, Ruling 41 §3,
`docs/plans/2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md`) — the memo's
safety does not rest on the mapping being immutable, because it is not.** This paragraph
used to argue *"artifacts are immutable (FR-OVR-1), so a given `rating_version` ref names
one immutable version and compiles to one `Bundle` content hash. The mapping cannot change
under the memo."* **That is false**: `row.bundle` is mutable, and
`compile_rating_version` (`backend/src/app/platform/rating_versions.py:440-444`) rewrites
`content_hash` on every recompile of an already-compiled version — nothing refuses a
recompile, and `_rating_compile` (`backend/src/app/worker/rating_handlers.py:41-48`)
captures `prior_hash` **before** compiling precisely because the call is about to
overwrite it, then audits `before`/`after`. The system already treats *"a changed content
hash under an unchanged pinned ref"* as a normal, audited event — the sentence above denied
that this ever happens.

**The memo is safe today for a narrower, real reason: `hash_for(ref)` is read from exactly
one call site, inside the NFR-RATE-9 degradation branch** (`backend/src/app/api/score.py`,
`_compiled_for`'s `except Exception:` clause) — never on the happy path. Serving a
last-known-good bundle there is the specified behaviour even if the ref has since been
recompiled to a different hash elsewhere, because the alternative is refusing the request
outright while metadata storage is down. **This safety does not generalise**: a caller
that reads `hash_for(ref)` on the happy path, without a fresh metadata read confirming the
hash still matches, would serve a stale bundle under a window bounded by nothing — exactly
the shortcut Ruling 41 refuses. The hot-path shortcut Ruling 41 §2 does authorise
(`_compiled_for`) re-reads the version row on every call and checks the *freshly read*
hash against `get(content_hash)`, never `hash_for(ref)` — see that function's own
docstring.

**What this deliberately does not have: refresh, poll, pub/sub, or an environment
pointer.** All four are W14's (Ruling 16 clause 4, and Ruling 10 before it). A slot that
acquires any of them has overridden the ruling.

**Two of the four are held structurally; two are not, and that is the limit rather than a
gap to close here.** `backend/tests/test_bundle_slot.py` asserts this module's import roots
against an allowlist. That catches **poll** (a clock plus a task or thread) and **pub/sub**
(a broker client), because neither can be built without a dependency the check can see. It
does not catch the other two, and both escape for the same reason — they are pure data and
method surface, needing no import at all:

- **An environment pointer** is `dict[str, str]`, structurally identical to `_resolved`.
  The difference is entirely in what the key means, so no dependency-keyed check can
  separate a memo of a resolution already performed from a pointer to what should be live.
- **A refresh**, in the form the ruling itself expects, is a method a caller invokes.
  Clause 4's own note says *"W14 starts from a deploy-time push and argues its way to poll,
  not the reverse"* — which makes the push form the live one rather than a hypothetical,
  and a push is a call, not an import.

For those two the ruling is held by review, not by a check. Whoever adds a public method
here owes an answer to which of the four it is not.

**Failure posture: there is none to degrade to.** Unlike `DiffCache`, whose Redis outage
falls back to a recompute, this slot cannot fail independently of the process that owns
it — a miss is a miss and the caller hydrates. It is also **per worker and per process**:
nothing is shared, nothing is warmed at startup (that is FR-RATE-51's pre-warming, W14's),
and a fresh worker starts empty.
"""

from __future__ import annotations

from collections import OrderedDict

from model_schema.refs import ArtifactRef
from pricing_core.rating.runtime import CompiledBundle

__all__ = ["BundleSlot"]


class BundleSlot:
    """A bounded, per-worker holding tier for hydrated bundles.

    Synchronous on purpose: `load_bundle` is synchronous and pure (Ruling 10), and the
    slot itself does no I/O, so an `async` surface here would only add await points to a
    path NFR-RATE-1 budgets in milliseconds.

    **Confined to one worker's event loop, and not safe under concurrent mutation from
    threads.** Every mutation is a plain dict write with no lock, so two threads calling
    `put` can leave `_forget` walking `_resolved` while the other mutates it — reproduced
    at 8 threads x 20k puts as `RuntimeError: OrderedDict mutated during iteration`.

    The blast radius is a failed request, never a wrong premium: the worst a torn `_forget`
    can leave behind is a memo entry whose bundle is already evicted, and that resolves to
    a `get` miss, which the caller must refuse. A lock is not taken because it would cost
    every request on a path NFR-RATE-1 budgets at 50 ms p99, to remove a race that cannot
    arise on a single event loop.

    **The precondition that makes that true is that callers are `async`.** FastAPI runs a
    plain `def` route handler in a threadpool, so a synchronous caller would put two
    threads on this object and reach the race above. Task 2B's route is `async def`; a
    later sync caller needs a lock added here first, and this paragraph is the notice.
    """

    def __init__(self, capacity: int = 1) -> None:
        """Hold at most `capacity` bundles, evicting least-recently-used.

        The default is 1 — the only value that cannot regress a worker's memory against
        holding none at all. Raising it is a measurement, not a preference (Ruling 16
        clause 3): it belongs with a figure from the latency harness in a
        `docs/research/` note.
        """
        if capacity < 1:
            raise ValueError(
                f"bundle slot capacity must be at least 1, not {capacity}. A slot that "
                "can hold nothing passes every hit test by never hitting, and reads as "
                "'the cache is not helping' rather than as a misconfiguration."
            )
        self._capacity = capacity
        #: hash -> bundle, most-recently-used last.
        self._held: OrderedDict[str, CompiledBundle] = OrderedDict()
        #: canonical ref string -> the hash this worker resolved it to. Every entry
        #: points at a *held* bundle: `_forget` drops a hash's refs when it is evicted,
        #: so the index cannot accumulate entries that could only ever produce a refusal.
        #:
        #: **Bounded by the refs pointing at held hashes, not by `capacity`.** Identical
        #: rating-version content compiles to one `Bundle` hash (FR-RATE-24), so several
        #: refs can share one held entry — a reader who sees `capacity` and assumes it
        #: caps this index too would be wrong. Each entry is two short strings and dies
        #: with its bundle, so this is a bound worth stating rather than a leak worth
        #: fixing. Capping it separately at `capacity` was rejected: at capacity 1 that
        #: would drop the first caller's degraded read while the bundle was still held
        #: (`test_two_refs_may_memo_the_same_bundle`).
        self._resolved: OrderedDict[str, str] = OrderedDict()

    @property
    def capacity(self) -> int:
        return self._capacity

    def get(self, content_hash: str) -> CompiledBundle | None:
        """The bundle held for `content_hash`, or `None`. A hit is a use, so it counts
        for the recency order."""
        held = self._held.get(content_hash)
        if held is None:
            return None
        self._held.move_to_end(content_hash)
        return held

    def put(self, ref: ArtifactRef, compiled: CompiledBundle) -> None:
        """Hold `compiled` under its own hash, and memo `ref` as resolving to it.

        Both indices are written by this one call, and that is the point: the memo exists
        only so the degraded read is reachable, and a caller that could hold a bundle
        without recording the ref it came from would leave NFR-RATE-9's path unreachable
        exactly when it is needed.
        """
        self._held[compiled.content_hash] = compiled
        self._held.move_to_end(compiled.content_hash)
        self._resolved[str(ref)] = compiled.content_hash
        while len(self._held) > self._capacity:
            evicted, _ = self._held.popitem(last=False)
            self._forget(evicted)

    def hash_for(self, ref: ArtifactRef) -> str | None:
        """The hash this worker resolved `ref` to, or `None` if it never did.

        `None` is the honest answer for a ref this worker has not served, and the caller
        must refuse rather than reach for whatever it happens to be holding: serving a ref
        that was never resolved is not degradation, it is invention (Ruling 16's
        acceptance item 2).
        """
        return self._resolved.get(str(ref))

    def _forget(self, content_hash: str) -> None:
        """Drop every ref memoed to an evicted hash, so `hash_for` and `get` agree."""
        for ref in [r for r, h in self._resolved.items() if h == content_hash]:
            del self._resolved[ref]
