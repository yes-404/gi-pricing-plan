"""The Model lifecycle, at the layers that can be reached independently (FR-MODEL-64).

`packages/model-schema/tests/test_model_lifecycle.py` proves the transition table refuses
the edges that must not exist. This file proves the three layers *below* the table hold:

* **the database** — a CHECK that survives a direct `UPDATE`, which is the only layer an
  audit rewriting rows with SQL cannot walk past;
* **the service** — the transitions, their refusals, and the audit event each one writes in
  the caller's transaction (`06` R2);
* **the seam to governance** — a decision on an approval request reaching the artifact,
  which is `wf-01` E9 → E10 and the arm of the journey that did not exist before this slice.

Every test that matters here is a **prohibition**. For a governed system the suite has to
prove the wrong thing cannot happen: a model reaching an approver with no evidence, a
submitter approving their own work, a rejected model claiming to have un-fitted itself.
"""

from __future__ import annotations

import pytest
from backend.tests.test_diagnostics import _fit
from sqlalchemy import select, text

from app.db.models import ModelRow
from app.platform import modelling as service
from model_schema import ModelStatus

# -- The database -------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-64")
async def test_the_database_refuses_a_status_outside_the_lifecycle(
    database, workspace_id
) -> None:
    """`models.status` is a `String(16)`, so before this constraint the column accepted
    `'aproved'`, `'live'`, or any other sixteen characters — and a typo in a status is a
    model that every lifecycle query silently skips.

    The type enumerates the six states and the transition table refuses the wrong edges;
    neither is reachable from `psql`. This is the layer that is.

    `fit_result` and `diagnostics_id` are supplied deliberately. Without them the two
    constraints the diagnostics slice added refuse the row first — for the *right* reason
    but the wrong one to be testing — and the test would pass against a table with no
    status constraint at all, which is what it did before this note was written.
    """
    async with database.unit_of_work() as session:
        with pytest.raises(Exception, match="model_status_is_in_the_lifecycle"):
            await session.execute(
                text(
                    "INSERT INTO models (id, workspace_id, model_family_slug, version, "
                    "status, dataset_version_id, spec, spec_hash, fit_result, "
                    "diagnostics_id) VALUES "
                    "(gen_random_uuid(), :ws, 'direct', 1, 'live', gen_random_uuid(), "
                    "'{}'::jsonb, 'v2:sha256:direct-status', '{}'::jsonb, "
                    "gen_random_uuid())"
                ),
                {"ws": workspace_id},
            )


@pytest.mark.req("FR-MODEL-64")
async def test_every_lifecycle_status_is_accepted_by_the_constraint(
    database, workspace_id
) -> None:
    """The other half, and the one a CHECK gets wrong more often: a constraint that
    enumerates five of six states reads as working until the sixth model arrives.

    `draft` and `archived` are the only two a bare insert can use — the other four require
    a `fit_result` and diagnostics, which the constraints added with the diagnostics slice
    already enforce — so the enumeration is asserted from the constraint's own definition
    rather than by inserting six rows that other invariants would rightly refuse.
    """
    async with database.session() as session:
        clause = (
            await session.execute(
                text(
                    "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                    "WHERE conrelid = 'models'::regclass "
                    "AND conname LIKE '%%model_status_is_in_the_lifecycle'"
                )
            )
        ).scalar_one()
    for status in ModelStatus:
        assert f"'{status.value}'" in clause, f"{status.value} missing from {clause}"


# -- The service: `fitted → review` -------------------------------------------------------


@pytest.mark.req("FR-MODEL-64")
async def test_a_draft_model_cannot_be_submitted_for_review(
    database, blob_store, workspace_id
) -> None:
    """`draft → review` is not an edge (FR-MODEL-64), and the refusal must arrive at the
    caller rather than at an approver: a model in `draft` has no coefficients, so the
    approval request would carry nothing to review."""
    actor, model_id = await _fit(database, blob_store, workspace_id)
    async with database.unit_of_work() as session:
        row = (
            await session.execute(select(ModelRow).where(ModelRow.id == model_id))
        ).scalar_one()
        row.status = ModelStatus.DRAFT.value
        row.fit_result = None
        row.diagnostics_id = None

    async with database.unit_of_work() as session:
        with pytest.raises(Exception, match="cannot move"):
            await service.submit_for_review(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                change_summary="first frequency model for AD",
            )
