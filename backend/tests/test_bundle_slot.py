"""The per-worker bundle slot (W11 Slice 2 Task 2A, Ruling 16).

The slot is the first in-process cache in this backend, so these tests pin the four
properties the ruling names and nothing else: it holds a hydrated `CompiledBundle` so a
second request for the same bundle does not re-hydrate; the **held index** is bounded by a
**count**, evicting least-recently-used — the memo is bounded differently, and
`test_evicting_a_bundle_forgets_the_refs_that_pointed_at_it` says how; it memoises the
ref → hash resolution this worker itself performed, which is what makes NFR-RATE-9's
degraded read reachable at all; and it
acquires none of the four mechanisms Ruling 16 clause 4 reserves for W14.

The end-to-end degraded read — a second request for an already-served ref answered 200
with the rating-version load patched to raise — is Task 2B's, over HTTP. What is provable
here is the slot half: the memo exists, it never answers for a ref this worker has not
resolved, and it never outlives the bundle it points at.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.config import Settings
from app.platform import bundle_slot as bundle_slot_module
from app.platform.bundle_slot import BundleSlot
from model_schema.rating import RatingAlgorithm
from model_schema.refs import ArtifactRef
from pricing_core.rating.runtime import CompiledBundle

# --------------------------------------------------------------------------------------
# Fixtures. The slot stores `CompiledBundle`s and never looks inside one, so these are
# real instances of the shipped frozen dataclass with a minimal but *valid*
# `RatingAlgorithm` — not a stand-in, so a future field addition breaks here loudly.
# --------------------------------------------------------------------------------------

_ALGORITHM_PAYLOAD: dict[str, Any] = {
    "slug": "bundle-slot-fixture",
    "version": 1,
    "input_contract": [
        {
            "name": "risk_premium_minor",
            "type": "int",
            "nullable": False,
            "min": 0,
            "max": 1_000_000,
        }
    ],
    "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
    "steps": [
        {
            "step_id": "s_in",
            "type": "input",
            "label": "Risk premium",
            "input_name": "risk_premium_minor",
            "on_missing": "error",
            "produces": "risk_premium_minor",
        },
        {
            "step_id": "s_out",
            "type": "output",
            "label": "Payable premium",
            "output_name": "payable_premium_minor",
            "rounding": {"mode": "half_even", "dp": 0},
            "consumes": ["risk_premium_minor"],
        },
    ],
    "sub_graphs": [],
}


def _compiled(content_hash: str) -> CompiledBundle:
    """A `CompiledBundle` carrying `content_hash`.

    `decision` is a sentinel: it is the ZEN handle in production and the slot never
    touches it, so hydrating a real engine here would test the engine rather than the
    slot.
    """
    return CompiledBundle(
        content_hash=content_hash,
        decision=object(),
        algorithm=RatingAlgorithm.model_validate(_ALGORITHM_PAYLOAD),
        boosters={},
    )


def _ref(version: int) -> ArtifactRef:
    return ArtifactRef.model_validate(f"rating_version:motor-slot-fixture@{version}")


class _Hydrations:
    """Counts how often the caller had to hydrate — the miss path of Task 2B step 5.

    The slot itself never hydrates (`load_bundle` stays the caller's, and Ruling 10 keeps
    it pure), so "returned without re-hydrating" is only observable from the outside, in
    the shape the route will actually use it.
    """

    def __init__(self, slot: BundleSlot) -> None:
        self.slot = slot
        self.count = 0

    def serve(self, ref: ArtifactRef, content_hash: str) -> CompiledBundle:
        held = self.slot.get(content_hash)
        if held is None:
            self.count += 1
            held = _compiled(content_hash)
        self.slot.put(ref, held)
        return held


# --------------------------------------------------------------------------------------
# Holding and reuse (FR-RATE-65: a `CompiledBundle` is held per worker process).
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-65")
def test_a_held_bundle_is_returned_without_rehydrating() -> None:
    """The point of the slot: hydration happens once per bundle per worker.

    `predict_gbm` deserialises a fresh booster handle on every call, so without this the
    50 ms of NFR-RATE-1 pays for a deserialise it did not need.
    """
    hydrations = _Hydrations(BundleSlot(capacity=1))

    first = hydrations.serve(_ref(1), "hash-a")
    second = hydrations.serve(_ref(1), "hash-a")

    assert second is first
    assert hydrations.count == 1


@pytest.mark.req("FR-RATE-65")
def test_at_capacity_one_a_second_hash_evicts_the_first() -> None:
    """Bounded by a count, and at the default capacity of 1 that bound is replacement."""
    slot = BundleSlot(capacity=1)

    slot.put(_ref(1), _compiled("hash-a"))
    slot.put(_ref(2), _compiled("hash-b"))

    assert slot.get("hash-b") is not None
    assert slot.get("hash-a") is None


@pytest.mark.req("FR-RATE-65")
def test_eviction_is_least_recently_used_not_insertion_order() -> None:
    """LRU, not FIFO — a first-in-first-out slot passes the capacity-1 test above.

    At capacity 2, holding A then B and then *reading* A must evict B on the next
    insert. A FIFO implementation evicts A and fails here, which is the whole point of
    the case.
    """
    slot = BundleSlot(capacity=2)

    slot.put(_ref(1), _compiled("hash-a"))
    slot.put(_ref(2), _compiled("hash-b"))
    assert slot.get("hash-a") is not None  # A is now the most recently used
    slot.put(_ref(3), _compiled("hash-c"))

    assert slot.get("hash-a") is not None
    assert slot.get("hash-c") is not None
    assert slot.get("hash-b") is None


# --------------------------------------------------------------------------------------
# The ref -> hash memo (Ruling 16 clause 5; NFR-RATE-9's degraded read).
# --------------------------------------------------------------------------------------


@pytest.mark.req("NFR-RATE-9")
def test_a_served_ref_resolves_to_its_hash_without_a_metadata_read() -> None:
    """Ruling 16 clause 5's second index, and why the slot needs one.

    A slot keyed only by `content_hash` cannot be reached when metadata storage is down,
    because the request carries a `rating_version_ref` and ref -> `Bundle` -> hash *is*
    a metadata read. The memo records the resolution this worker itself performed, so the
    degraded path needs no database at all.
    """
    slot = BundleSlot(capacity=1)
    slot.put(_ref(1), _compiled("hash-a"))

    assert slot.hash_for(_ref(1)) == "hash-a"
    assert slot.get("hash-a") is not None


@pytest.mark.req("NFR-RATE-9")
def test_an_unserved_ref_resolves_to_nothing() -> None:
    """Negative: the slot never invents a resolution.

    Ruling 16's acceptance item 2 is overridden by any build that serves a ref it has
    never resolved while metadata storage is down — "that is not degradation, it is
    invention". A worker that has served version 1 knows nothing about version 2, even
    though it holds a bundle.
    """
    slot = BundleSlot(capacity=1)
    slot.put(_ref(1), _compiled("hash-a"))

    assert slot.hash_for(_ref(2)) is None


@pytest.mark.req("NFR-RATE-9")
def test_evicting_a_bundle_forgets_the_refs_that_pointed_at_it() -> None:
    """A resolvable ref always has its bundle: `hash_for` and `get` never disagree.

    A memo outliving its bundle would be an entry that can only ever produce a refusal.
    That is what this forbids, and it is *all* it forbids.

    **The two indices are not bounded the same way, and an earlier version of this
    docstring claimed they were.** `_held` is capped at `capacity`; `_resolved` is not.
    Several refs can point at one held hash — identical content compiles to one hash
    (FR-RATE-24) — so at capacity 1 the memo can hold many entries at once: 50,000
    distinct refs resolving to one held bundle keeps 50,000 memo entries, every one of
    them valid and none of them capped. What this test pins is the property that does
    hold — every entry dies with its bundle — not a symmetry that does not.
    """
    slot = BundleSlot(capacity=1)
    slot.put(_ref(1), _compiled("hash-a"))
    slot.put(_ref(2), _compiled("hash-b"))

    assert slot.hash_for(_ref(1)) is None
    assert slot.hash_for(_ref(2)) == "hash-b"


@pytest.mark.req("NFR-RATE-9")
def test_two_refs_may_memo_the_same_bundle() -> None:
    """Two Rating Versions with identical content compile to one hash (FR-RATE-24).

    Both refs must resolve, and evicting the bundle must forget both — a per-hash memo
    that held only the last ref would silently drop the first caller's degraded read.
    """
    slot = BundleSlot(capacity=2)
    slot.put(_ref(1), _compiled("hash-a"))
    slot.put(_ref(2), _compiled("hash-a"))

    assert slot.hash_for(_ref(1)) == "hash-a"
    assert slot.hash_for(_ref(2)) == "hash-a"

    slot.put(_ref(3), _compiled("hash-b"))
    slot.put(_ref(4), _compiled("hash-c"))

    assert slot.hash_for(_ref(1)) is None
    assert slot.hash_for(_ref(2)) is None


# --------------------------------------------------------------------------------------
# Ruling 16 clause 3 (capacity is a count, default 1) and clause 4 (four exclusions).
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-65")
def test_capacity_is_a_count_defaulting_to_one() -> None:
    """Clause 3: a count, not a byte budget, and 1 until a measurement raises it.

    Nothing in this repository measures a hydrated `CompiledBundle`'s footprint — NFR-RATE-4
    permits 500 MB including boosters — so a byte bound would be an estimate wearing a
    number's clothes, and 1 is the only default that cannot regress a worker's memory
    against holding none at all.
    """
    assert Settings().bundle_slot_capacity == 1


@pytest.mark.req("FR-RATE-65")
@pytest.mark.parametrize("capacity", [0, -1])
def test_a_slot_that_can_hold_nothing_is_refused(capacity: int) -> None:
    """Negative: capacity 0 would be a slot that silently holds nothing.

    It would pass every hit test by never hitting, and read as "the cache is not helping"
    rather than as a misconfiguration. Refused in both places it can be set.
    """
    with pytest.raises(ValueError, match="capacity must be at least 1"):
        BundleSlot(capacity=capacity)
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        Settings(bundle_slot_capacity=capacity)


def _imported_roots(source: str) -> set[str]:
    """The top-level package of every import in `source`.

    A relative import is reported as `.` rather than resolved: it cannot appear in this
    module legitimately, and silently skipping it would leave the check with a hole
    exactly the shape of the thing it exists to catch.
    """
    roots: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            roots |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                roots.add(".")
            elif node.module:
                roots.add(node.module.split(".")[0])
    return roots


#: Everything the slot may reach. Each of Ruling 16 clause 4's four reserved mechanisms
#: needs something outside it: a poll needs a clock and a task or thread (`asyncio`,
#: `threading`, `time`), a pub/sub subscription needs a broker client (`redis`), an
#: environment pointer needs the metadata store (`sqlalchemy`, `app.db`), and a refresh
#: trigger needs at least one of those. None can be added invisibly.
_PERMITTED_IMPORT_ROOTS = frozenset(
    {"__future__", "collections", "typing", "model_schema", "pricing_core"}
)


def _module_source() -> str:
    """The slot module's own source, located through the imported module.

    Read from `__file__` rather than from a path spelled out here, so moving the module
    cannot leave this check silently reading a file that no longer exists.
    """
    assert bundle_slot_module.__file__ is not None
    return Path(bundle_slot_module.__file__).read_text()


@pytest.mark.req("FR-RATE-65")
def test_the_slot_reaches_no_broker_scheduler_or_metadata_store() -> None:
    """Ruling 16 clause 4: no refresh, no poll, no pub/sub, no environment pointer.

    All four are W14's, and a slot that acquires any of them has overridden the ruling.
    None can be built out of nothing, so this checks for the dependency each would need
    rather than for a method named `refresh` — a name the violating code is free not to
    use.
    """
    assert _imported_roots(_module_source()) <= _PERMITTED_IMPORT_ROOTS


def _violations() -> Iterable[str]:
    """Deliberately broken inputs for the check above, one per reserved mechanism."""
    yield "import asyncio"
    yield "import threading"
    yield "import redis.asyncio"
    yield "from sqlalchemy.ext.asyncio import AsyncSession"
    yield "from app.db.session import get_session"
    yield "from .diff_cache import DiffCache"


@pytest.mark.req("FR-RATE-65")
@pytest.mark.parametrize("statement", list(_violations()))
def test_the_clause_four_check_fails_on_a_broken_module(statement: str) -> None:
    """Positive control, run through the check's own extraction rather than a lookalike.

    A structural check that has never printed a failure has not been tested, and this one
    guards a rule whose violations are all additions — so the control adds each of them
    to the real module's source and requires the assertion to go red.
    """
    assert not _imported_roots(f"{_module_source()}\n{statement}\n") <= _PERMITTED_IMPORT_ROOTS
