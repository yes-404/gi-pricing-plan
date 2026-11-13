"""WK-2113 S3, condition (3): what makes a hash a running worker already holds re-validate.

**The mechanism is RESTART** (ruling 2026-11-13 21:17:39; plan §2 row 3). `BundleSlot` is process
memory and nothing persists it, and after this slice the only path that puts a blob-loaded bundle
into it is `_fetch_bundle` through `hydrate` (the census test, `test_bundle_hydration.py`): a
process on this code holds only a bundle that passed the guard, and a process on older code holds
what it held until it is restarted, which the upgrade note (CHANGELOG, deploy/README) says. A
guard-version key on the slot was rejected: the slot never outlives the code that filled it.

A hash is NOT a validation (it covers the pins, not the carried payloads), so no test here treats
one as such. DB-backed; runs in the window the lead grants.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_stored_bundle_revalidation import (
    CODE,
    assert_one_event,
    stored_version,
)

from app.api.score import _fetch_bundle
from app.db.session import Database
from app.errors import PlatformError
from app.platform.bundle_slot import BundleSlot
from model_schema import ArtifactRef


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.req("FR-243")
def test_a_new_process_starts_with_an_empty_slot() -> None:
    """The restart premise: nothing carries a hold from the previous code into a new process."""
    slot = BundleSlot()
    assert slot.get("sha256:" + "0" * 64) is None
    assert slot.hash_for(ArtifactRef(type="rating_version", slug="x", version=1)) is None


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.req("FR-243")
@pytest.mark.asyncio
async def test_a_refused_fetch_leaves_nothing_in_the_slot_and_is_refused_again(
    database: Database, blob_store: Any, workspace_id: UUID
) -> None:
    ref_str, content_hash = await stored_version(
        database, blob_store, workspace_id, "offender.bundle.json"
    )
    ref = ArtifactRef.parse(ref_str)
    slot = BundleSlot()
    for _ in range(2):  # every request is refused; the event is written once (DP-1)
        with pytest.raises(PlatformError) as refused:
            await _fetch_bundle(
                database, blob_store, slot, database=database, workspace_id=workspace_id, ref=ref
            )
        assert refused.value.code == CODE
        assert slot.get(content_hash) is None
        assert slot.hash_for(ref) is None
    await assert_one_event(database, workspace_id, ref_str, content_hash)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.req("FR-243")
@pytest.mark.asyncio
async def test_a_clean_hash_held_in_the_slot_is_still_a_hit(
    database: Database, blob_store: Any, workspace_id: UUID
) -> None:
    """Instrument-red cell, and FR-239 / NFR-489: a clean version loaded through the guard is
    served from the slot, not re-read from the blob store."""
    ref_str, _ = await stored_version(database, blob_store, workspace_id, "clean.bundle.json")
    ref = ArtifactRef.parse(ref_str)
    slot = BundleSlot()
    first = await _fetch_bundle(
        database, blob_store, slot, database=database, workspace_id=workspace_id, ref=ref
    )
    second = await _fetch_bundle(
        database, blob_store, slot, database=database, workspace_id=workspace_id, ref=ref
    )
    assert second is first
