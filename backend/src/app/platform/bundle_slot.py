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

Recording the ref is safe against staleness for a structural reason rather than a timing
one: artifacts are immutable (FR-OVR-1), so a given `rating_version` ref names one
immutable version and compiles to one `Bundle` content hash. The mapping cannot change
under the memo; only whether the bundle is still held can.

**What this deliberately does not have: refresh, poll, pub/sub, or an environment
pointer.** All four are W14's (Ruling 16 clause 4, and Ruling 10 before it). A slot that
acquires any of them has overridden the ruling. `backend/tests/test_bundle_slot.py` holds
that structurally — none of the four can be built without a broker client, a scheduler, a
thread, or the metadata store, and this module imports none of them.

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
