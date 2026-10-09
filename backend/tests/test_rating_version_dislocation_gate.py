"""The approval gate, part one: FR-257 limb (2), `structural_diff` and FR-224 (PL-1500).

`submit_for_review` refuses a version with no Dislocation Run against its baseline (limb (2)),
persists FR-219's structural diff as evidence, and gates an `approximation`-mode version on
FR-224's threshold. Written before the code, as `PL-1500` §"Tasks" orders; each section is one
task's. Every test needs Postgres.

The shared submit fixture (`test_rating_versions._Gate.submit`) records the limb (2) run by
default; these tests pass `dislocation=False` and record, or withhold, the run themselves.
"""

from __future__ import annotations

from uuid import UUID

import pytest
from backend.tests.test_rating_versions import (
    _approved_baseline,
    _Gate,
    _gate,
    _quote,
    _requests_for,
    _suite,
    record_dislocation_run,
)

from app.db.models import DeploymentRow, EnvironmentRow
from app.db.session import Database
from app.errors import PlatformError

_STALE_HASH = "sha256:" + "0" * 64


def _ref(slug: str, version: int) -> str:
    return f"rating_version:{slug}@{version}"


async def _candidate(gate: _Gate) -> tuple[UUID, str, str]:
    """A second version on an approved baseline: its id, its ref and its bundle hash."""
    rv_id = await gate.version()
    row = await gate.row(rv_id)
    return rv_id, _ref(row.slug, row.version), str(row.bundle["content_hash"])  # type: ignore[index]


async def _refused(gate: _Gate, rating_id: UUID) -> PlatformError:
    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id, dislocation=False)
    return refused.value


def _assert_limb_2_refusal(error: PlatformError, reason: str) -> None:
    assert error.code == "EVIDENCE_INCOMPLETE"
    assert error.status_code == 422
    assert error.detail is not None
    assert "FR-257 limb (2)" in error.detail
    assert reason in error.detail


# ---- Task 3: FR-257 limb (2) -------------------------------------------------------


@pytest.mark.req("FR-257")
async def test_limb_2_refuses_with_no_dislocation_run(database: Database, workspace_id) -> None:
    """Limb (2) only: the baseline exists (an approved version), no run names the candidate."""
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote()))
    rv_id, _, _ = await _candidate(gate)
    before = await _requests_for(database, workspace_id)

    _assert_limb_2_refusal(await _refused(gate, rv_id), "no Dislocation Run names this version")
    assert (await gate.row(rv_id)).status == "draft"
    assert await _requests_for(database, workspace_id) == before


@pytest.mark.req("FR-257")
async def test_limb_2_refuses_a_run_on_a_stale_candidate_bundle_hash(
    database: Database, workspace_id
) -> None:
    """Limb (2) only: a run exists, but on an earlier bundle hash than the version's current."""
    gate = await _gate(database, workspace_id)
    rv_a = await _approved_baseline(gate, _suite(_quote()))
    rv_id, ref, _ = await _candidate(gate)
    baseline = _ref("minimal-rv", (await gate.row(rv_a)).version)
    await record_dislocation_run(
        database, workspace_id, candidate_ref=ref, candidate_hash=_STALE_HASH,
        baseline_ref=baseline, actor_id=gate.analyst.id,
    )
    before = await _requests_for(database, workspace_id)

    _assert_limb_2_refusal(await _refused(gate, rv_id), "(stale)")
    assert await _requests_for(database, workspace_id) == before


@pytest.mark.req("FR-257")
async def test_limb_2_refuses_a_run_whose_baseline_is_not_the_current_live_version(
    database: Database, workspace_id
) -> None:
    """Limb (2) only: a run at the current hash, against a baseline that is not the one."""
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote()))
    rv_id, ref, current_hash = await _candidate(gate)
    await record_dislocation_run(
        database, workspace_id, candidate_ref=ref, candidate_hash=current_hash,
        baseline_ref=_ref("some-other-version", 9), actor_id=gate.analyst.id,
    )
    before = await _requests_for(database, workspace_id)

    _assert_limb_2_refusal(await _refused(gate, rv_id), "as its baseline")
    assert await _requests_for(database, workspace_id) == before


@pytest.mark.req("FR-257")
async def test_limb_2_accepts_a_run_against_the_live_version_and_records_it(
    database: Database, workspace_id
) -> None:
    """Limb (2) only: the right run is accepted and its id is written to the evidence."""
    gate = await _gate(database, workspace_id)
    rv_a = await _approved_baseline(gate, _suite(_quote()))
    rv_id, ref, current_hash = await _candidate(gate)
    run_id = await record_dislocation_run(
        database, workspace_id, candidate_ref=ref, candidate_hash=current_hash,
        baseline_ref=_ref("minimal-rv", (await gate.row(rv_a)).version),
        actor_id=gate.analyst.id,
    )

    await gate.submit(rv_id, dislocation=False)

    row = await gate.row(rv_id)
    assert row.status == "review"
    assert row.evidence["dislocation_run_id"] == str(run_id)  # type: ignore[index]
    assert "no_baseline" not in row.evidence  # type: ignore[operator]


@pytest.mark.req("FR-257")
async def test_limb_2_with_nothing_live_or_approved_records_the_first_version(
    database: Database, workspace_id
) -> None:
    """DP-S5-1 (a), RL-1504 T3: a first version needs no run; the evidence records why."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rv_id = await gate.version()

    await gate.submit(rv_id, dislocation=False)

    row = await gate.row(rv_id)
    assert row.status == "review"
    assert row.evidence["no_baseline"] == "first_version"  # type: ignore[index]
    assert "dislocation_run_id" not in row.evidence  # type: ignore[operator]


@pytest.mark.req("FR-257")
async def test_limb_2_prefers_the_version_live_in_the_baseline_environment(
    database: Database, workspace_id
) -> None:
    """DP-S5-1 (a): the live version in `prod` is the baseline, ahead of the most recently
    approved one. A run against the approved version is refused; one against the live is not."""
    gate = await _gate(database, workspace_id)
    rv_a = await _approved_baseline(gate, _suite(_quote()))
    rv_b = await gate.version()
    await gate.approve((await gate.submit(rv_b)).id)
    live_ref = _ref("minimal-rv", (await gate.row(rv_a)).version)
    approved_ref = _ref("minimal-rv", (await gate.row(rv_b)).version)
    async with database.unit_of_work() as session:
        environment = EnvironmentRow(
            workspace_id=workspace_id, slug="prod", name="Production", promotion_order=1
        )
        session.add(environment)
        await session.flush()
        session.add(
            DeploymentRow(
                workspace_id=workspace_id, environment_id=environment.id,
                rating_version_ref=live_ref,
                bundle_hash=str((await gate.row(rv_a)).bundle["content_hash"]),  # type: ignore[index]
                deployed_by=gate.analyst.id, reason="fixture",
            )
        )
    rv_c, ref, current_hash = await _candidate(gate)
    await record_dislocation_run(
        database, workspace_id, candidate_ref=ref, candidate_hash=current_hash,
        baseline_ref=approved_ref, actor_id=gate.analyst.id,
    )
    _assert_limb_2_refusal(await _refused(gate, rv_c), "as its baseline")

    run_id = await record_dislocation_run(
        database, workspace_id, candidate_ref=ref, candidate_hash=current_hash,
        baseline_ref=live_ref, actor_id=gate.analyst.id,
    )
    await gate.submit(rv_c, dislocation=False)
    assert (await gate.row(rv_c)).evidence["dislocation_run_id"] == str(run_id)  # type: ignore[index]
