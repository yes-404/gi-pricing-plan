"""WK-2113 S3, conditions (2) and (8): every path that hydrates a stored bundle refuses the same
planted offender with the named code, once-audited, never a 500, and the shadow arm never changes
the live response (DP-3).

DB-backed (the stored version, its blob and the audit chain are real); runs in the window the lead
grants. The scoring entry points (`/score`, `/score/compare`, the batch and trace Jobs, the shadow
arm) all hydrate through `_compiled_for`, so it is the unit under test here; the HTTP shape of a
409 problem is `test_stored_bundle_revalidation.py`'s (`assert_problem`).
The dislocation Job's `_compiled` and the governance gate's `_fetch_bundle` are the other doors
(aud-intent2's 20-path table).
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_stored_bundle_revalidation import (
    CODE,
    assert_one_event,
    stored_version,
)

from app.api.score import _compiled_for, _fetch_bundle, _shadow_score
from app.db.session import Database
from app.errors import PlatformError
from app.platform import rating_versions as rating_versions_service
from app.platform.bundle_slot import BundleSlot
from app.worker.dislocation_handlers import _compiled
from model_schema import ArtifactRef


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.req("FR-243")
@pytest.mark.asyncio
async def test_every_scoring_entry_refuses_a_stored_offender_once_audited(
    database: Database, blob_store: Any, workspace_id: UUID
) -> None:
    """`_compiled_for` serves /score, /score/compare, the batch and trace Jobs and the shadow arm.
    Two requests on one process: both refused with the code (409, never a raw exception), one
    event (DP-1)."""
    ref_str, content_hash = await stored_version(
        database, blob_store, workspace_id, "offender.bundle.json"
    )
    ref = ArtifactRef.parse(ref_str)
    slot = BundleSlot()
    for _ in range(2):
        with pytest.raises(PlatformError) as refused:
            await _compiled_for(
                database, blob_store, slot, database=database, workspace_id=workspace_id, ref=ref
            )
        assert (refused.value.code, refused.value.status_code) == (CODE, 409)
    await assert_one_event(database, workspace_id, ref_str, content_hash)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.req("FR-243")
@pytest.mark.asyncio
async def test_score_and_the_dislocation_run_refuse_the_same_planted_offender(
    database: Database, blob_store: Any, workspace_id: UUID
) -> None:
    """Condition (8): after S3, /score of the version refuses as the dislocation prepare does."""
    ref_str, _ = await stored_version(database, blob_store, workspace_id, "offender.bundle.json")
    ref = ArtifactRef.parse(ref_str)
    with pytest.raises(PlatformError) as scored:
        await _fetch_bundle(
            database,
            blob_store,
            BundleSlot(),
            database=database,
            workspace_id=workspace_id,
            ref=ref,
        )
    progress = SimpleNamespace(database=database, blob_store=blob_store)
    async with database.session() as session:
        row = await rating_versions_service.resolve_rating_version_ref(
            session, workspace_id=workspace_id, ref=ref
        )
        with pytest.raises(PlatformError) as dislocated:
            await _compiled(progress, session, workspace_id, row, ref)  # type: ignore[arg-type]
    assert scored.value.code == dislocated.value.code == CODE


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.req("FR-271")
@pytest.mark.asyncio
async def test_a_shadow_arm_over_a_stored_offender_records_the_event_and_raises_nothing(
    database: Database, blob_store: Any, workspace_id: UUID
) -> None:
    """DP-3: the shadow arm runs after the live response is sent and logs its failure; the event is
    recorded and the live answer is untouched."""
    ref_str, content_hash = await stored_version(
        database, blob_store, workspace_id, "offender.bundle.json"
    )
    await _shadow_score(
        database,
        blob_store,
        BundleSlot(),
        workspace_id,
        "dev",
        None,
        None,
        None,
        ArtifactRef.parse(ref_str),  # type: ignore[arg-type]
    )
    await assert_one_event(database, workspace_id, ref_str, content_hash)
