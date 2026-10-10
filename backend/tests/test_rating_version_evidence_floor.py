"""The approval gate, part two: `submit_for_review` checks the `rating_version` evidence floor
(`06` FR-364, PL-1499).

Submission reads `policy.effective_evidence("rating_version")` — the union of the floor and the
workspace's policy entry — and verifies each kind, so a policy that names a kind this build
cannot verify is refused by name rather than passed. Written before the code, as `PL-1499`
§"Tasks" orders. Every test needs Postgres.

The shared submit fixture (`test_rating_versions._Gate.submit`) fixes the change summary at
"golden"; the policy tests that vary it provision with `_provision` and call the service
directly.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_rating_versions import (
    _approved_baseline,
    _Gate,
    _gate,
    _quote,
    _requests_for,
    _suite,
)

from app.db.models import ApprovalPolicyRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import rating_versions as rating_versions_service
from model_schema import DEFAULT_POLICY, ApprovalPolicy

_FLOOR = ("structural_diff", "regression_run", "dislocation_run")


async def _store_policy(
    database: Database, workspace_id: UUID, rating_version_evidence: tuple[str, ...]
) -> None:
    """Store a policy whose `rating_version` entry lists exactly `rating_version_evidence`,
    written directly: `set_policy` refuses an entry below the floor (FR-364 (ii)), and a policy
    stored before that requirement is what the floor must still hold."""
    entries = [
        entry.model_copy(update={"evidence": rating_version_evidence})
        if entry.artifact_type == "rating_version"
        else entry
        for entry in DEFAULT_POLICY.policies
    ]
    document = ApprovalPolicy(policies=tuple(entries)).model_dump(mode="json")
    async with database.unit_of_work() as session:
        stored = await session.get(ApprovalPolicyRow, workspace_id)
        if stored is None:
            session.add(ApprovalPolicyRow(workspace_id=workspace_id, policy=document))
        else:
            stored.policy = document


async def _provision(gate: _Gate, rating_id: UUID) -> None:
    """Everything `_Gate.submit` records by default: a suite, a passing Regression Run and,
    where there is a baseline, the Dislocation Run."""
    await gate.ensure_suite(rating_id)
    await gate.record_run(rating_id, "pass")
    await gate.ensure_dislocation_run(rating_id)


async def _submit(gate: _Gate, rating_id: UUID, change_summary: str = "golden") -> None:
    async with gate.database.unit_of_work() as session:
        await rating_versions_service.submit_for_review(
            session, workspace_id=gate.workspace_id, actor=gate.actuary,
            rating_version_id=rating_id, change_summary=change_summary,
            blob_store=gate.blob_store, load_compiled=gate.load,
        )


def _assert_incomplete(error: PlatformError, *needles: str) -> None:
    assert error.code == "EVIDENCE_INCOMPLETE"
    assert error.status_code == 422
    assert error.detail is not None
    for needle in needles:
        assert needle in error.detail, error.detail


@pytest.mark.req("FR-364")
@pytest.mark.parametrize(
    ("missing", "detail"),
    [
        ("structural_diff", "FR-219: a version with no saved Rating Algorithm"),
        ("regression_run", "no Regression Run exists"),
        ("dislocation_run", "FR-257 limb (2): no Dislocation Run names this version"),
    ],
)
async def test_a_policy_at_the_floor_refuses_each_missing_kind(
    database: Database, workspace_id, missing: str, detail: str
) -> None:
    """The default policy is exactly the floor; with each kind withheld in turn, submission is
    422 `EVIDENCE_INCOMPLETE` carrying that kind's own refusal text, and the version stays a
    draft with no request created."""
    gate = await _gate(database, workspace_id)
    if missing == "dislocation_run":
        await _approved_baseline(gate, _suite(_quote()))
    else:
        await gate.suite(gate.analyst, _suite(_quote()))
    rv_id = await gate.version()
    if missing == "structural_diff":
        async with database.unit_of_work() as session:
            row = await rating_versions_service.load_rating_version(
                session, workspace_id=workspace_id, rating_version_id=rv_id
            )
            row.algorithm_ref = None
    if missing == "regression_run":
        await gate.ensure_suite(rv_id)
    elif missing == "dislocation_run":
        await gate.record_run(rv_id, "pass")
    before = await _requests_for(database, workspace_id)

    with pytest.raises(PlatformError) as refused:
        await _submit(gate, rv_id)

    _assert_incomplete(refused.value, detail)
    assert (await gate.row(rv_id)).status == "draft"
    assert await _requests_for(database, workspace_id) == before


@pytest.mark.req("FR-364")
async def test_a_stored_policy_below_the_floor_is_still_held_to_it(
    database: Database, workspace_id
) -> None:
    """A `rating_version` entry listing only `regression_run`, as a pre-FR-364 policy would:
    submission still refuses a version with no Dislocation Run, because the check reads the
    union (`effective_evidence`) and never `entry.evidence` alone."""
    gate = await _gate(database, workspace_id)
    await _store_policy(database, workspace_id, ("regression_run",))
    await _approved_baseline(gate, _suite(_quote()))
    rv_id = await gate.version()
    await gate.record_run(rv_id, "pass")

    with pytest.raises(PlatformError) as refused:
        await _submit(gate, rv_id)

    _assert_incomplete(refused.value, "FR-257 limb (2)")


@pytest.mark.req("FR-364")
async def test_a_policy_above_the_floor_adds_a_verifiable_kind(
    database: Database, workspace_id
) -> None:
    """DP-S6-1 (c), RL-1504 item 11: `change_summary` is verified when the summary is
    non-blank, so an entry naming it refuses a blank summary by name; `gipp_check_if_enabled`
    is verified while no workspace can enable GIPP, so naming it refuses nothing."""
    gate = await _gate(database, workspace_id)
    await _store_policy(
        database, workspace_id, (*_FLOOR, "change_summary", "gipp_check_if_enabled")
    )
    await gate.suite(gate.analyst, _suite(_quote()))
    rv_id = await gate.version()
    await _provision(gate, rv_id)

    with pytest.raises(PlatformError) as refused:
        await _submit(gate, rv_id, change_summary="  ")
    _assert_incomplete(refused.value, "change_summary")
    assert (await gate.row(rv_id)).status == "draft"

    await _submit(gate, rv_id, change_summary="a real summary")
    assert (await gate.row(rv_id)).status == "review"


@pytest.mark.req("FR-364")
async def test_a_policy_naming_an_unverifiable_kind_is_refused_by_name(
    database: Database, workspace_id
) -> None:
    """Fail closed: a kind with no verifier is refused, naming it and saying this build cannot
    verify it, even when every verifiable kind is satisfied. Never skipped, never passed."""
    gate = await _gate(database, workspace_id)
    await _store_policy(database, workspace_id, (*_FLOOR, "telepathy_check"))
    await gate.suite(gate.analyst, _suite(_quote()))
    rv_id = await gate.version()
    await _provision(gate, rv_id)

    with pytest.raises(PlatformError) as refused:
        await _submit(gate, rv_id)

    _assert_incomplete(refused.value, "telepathy_check", "cannot verify")
    assert (await gate.row(rv_id)).status == "draft"


@pytest.mark.req("FR-364")
async def test_a_policy_naming_rate_table_diffs_is_refused_naming_the_kind(
    database: Database, workspace_id
) -> None:
    """DP-S6-1 (c), RL-1504 item 11: `rate_table_diffs` has no persisted artifact and fails
    closed, naming the kind. The same policy without it, and with `change_summary` and a
    non-blank summary, does not refuse."""
    gate = await _gate(database, workspace_id)
    await _store_policy(database, workspace_id, (*_FLOOR, "rate_table_diffs"))
    await gate.suite(gate.analyst, _suite(_quote()))
    rv_id = await gate.version()
    await _provision(gate, rv_id)

    with pytest.raises(PlatformError) as refused:
        await _submit(gate, rv_id)
    _assert_incomplete(refused.value, "rate_table_diffs")
    assert "cannot verify" not in (refused.value.detail or ""), (
        "the kind has its own refusal, not the unknown-kind one"
    )

    await _store_policy(database, workspace_id, (*_FLOOR, "change_summary"))
    await _submit(gate, rv_id, change_summary="a real summary")
    assert (await gate.row(rv_id)).status == "review"


@pytest.mark.req("FR-364")
async def test_evidence_keys_match_the_direct_checks_for_a_first_version(
    database: Database, workspace_id
) -> None:
    """Routing through the floor changes no evidence: a first version records
    `regression_suite_run_id`, `structural_diff_blob`, `golden_quotes` and `no_baseline`."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rv_id = await gate.version()
    await gate.submit(rv_id)
    evidence: dict[str, Any] = (await gate.row(rv_id)).evidence or {}
    assert set(evidence) == {
        "golden_quotes", "regression_suite_run_id", "structural_diff_blob", "no_baseline",
    }
    assert evidence["no_baseline"] == "first_version"


@pytest.mark.req("FR-364")
async def test_evidence_keys_match_the_direct_checks_for_a_version_with_a_baseline(
    database: Database, workspace_id
) -> None:
    """A version with a baseline records `dislocation_run_id` in place of `no_baseline`."""
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote()))
    rv_id = await gate.version()
    await gate.submit(rv_id)
    evidence: dict[str, Any] = (await gate.row(rv_id)).evidence or {}
    assert set(evidence) == {
        "golden_quotes", "regression_suite_run_id", "structural_diff_blob", "dislocation_run_id",
    }
