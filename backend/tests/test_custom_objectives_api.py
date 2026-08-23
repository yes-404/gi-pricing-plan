"""The seven Custom Objective routes over HTTP (`02` §5.1, FR-MODEL-95).

`test_custom_objectives.py` covers the platform layer. This file covers the routes: who may
call each one, what comes back, the workspace boundary, and the conflicts a route can report
as a 500 without any platform test noticing.

The prior route evidence was one OpenAPI-presence assertion — the seven paths are spelled
correctly in the published contract. A route returning 500 on every call would have kept it
green.

**Three things the plan for this file expected are not what the code does**, found by reading
the raising sites rather than trusting the plan, and recorded in `02` §5.1 with this slice:

- **There is no list route.** Seven routes, and none of them lists. The workspace boundary is
  therefore proved on `GET /{id}` *and* on `GET /{id}/usage` — `usage` is the route that
  answers "what does this reach", so a lost workspace fold there leaks another workspace's
  models rather than one objective.
- **Re-certifying an objective that is already `certified` does not conflict.**
  `certifiable_or_refuse` admits `{draft, certified}` on purpose: re-certification after a
  library upgrade is how a finding is found. The conflict is `review` and past — where a
  certificate an approver is reading would move underneath the decision.
- **`_require_evidence` guards `submit`, not `certify`.** Certification *produces* the
  evidence; requiring it beforehand would be circular.

**Rows are created through the API and then advanced by UPDATE.** `POST /custom-objectives`
resolves the template's applicability, so seeding a `certified` row by hand would mean writing
an `Applicability` shape that `model-schema` already owns (`CLAUDE.md` §2). Only the lifecycle
columns are moved, which is exactly what `custom_objectives_definition_immutable` permits.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from backend.tests.test_api_datasets import _headers
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.models import ApprovalPolicyRow, CustomObjectiveRow
from app.db.session import Database
from app.platform.objectives import default_sampling
from model_schema import (
    DEFAULT_POLICY,
    ApprovalPolicy,
    CustomObjective,
    ObjectiveStatus,
    new_uuid7,
)


@pytest.fixture
def client(api_client: TestClient) -> TestClient:
    """The shared DB-backed client, under the name this module's tests use."""
    return api_client


@pytest_asyncio.fixture
async def author(workspace_id, principal, grant) -> dict[str, str]:
    """`model:fit` and `model:read`, and **not** `model:submit`.

    `analyst` is the role that authors and certifies. That it stops short of submission is
    what makes the submit refusal below a test of the permission rather than of the header:
    this principal can create the objective it is then refused permission to submit.
    """
    await grant("analyst")
    return _headers(principal.id, workspace_id)


@pytest_asyncio.fixture
async def submitter(workspace_id, grant) -> dict[str, str]:
    """`model:submit` as well — `pricing_actuary` is `analyst` plus the submit permissions."""
    submitter_id = new_uuid7()
    await grant("pricing_actuary", principal_id=submitter_id)
    return _headers(submitter_id, workspace_id)


@pytest_asyncio.fixture
async def reader(workspace_id, grant) -> dict[str, str]:
    """`model:read` and **not** `model:fit` — `auditor` is `READ_PERMISSIONS`."""
    reader_id = new_uuid7()
    await grant("auditor", principal_id=reader_id)
    return _headers(reader_id, workspace_id)


@pytest.fixture
def stranger(workspace_id) -> dict[str, str]:
    """Authenticated into this workspace, holding nothing."""
    return _headers(new_uuid7(), workspace_id)


def _run[T](work: Callable[[Database], Awaitable[T]]) -> T:
    """Run one coroutine on a loop of our own, disposing the engine it opened.

    `TestClient` is blocking, so an async fixture cannot be requested from the synchronous
    tests below — `test_api_models._seed` reaches for the same construction and records why.
    **`dispose()` is mandatory**: an engine left open exhausts the pool across a file.
    """
    from backend.tests.conftest_db import test_database_url

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        try:
            return loop.run_until_complete(work(database))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()


def _slug() -> str:
    return f"loss-{new_uuid7().hex[-10:]}"


def _create(
    client: TestClient, headers: dict[str, str], **overrides: Any
) -> dict[str, Any]:
    """One `draft` template objective, through the route that makes them."""
    body: dict[str, Any] = {"slug": _slug(), "template": "poisson", **overrides}
    response = client.post("/api/v1/custom-objectives", json=body, headers=headers)
    assert response.status_code == 201, response.text
    return dict(response.json())


def _advance(objective_id: UUID, *, status: ObjectiveStatus) -> None:
    """Move the lifecycle columns, and only those.

    `status IN ('draft','deprecated') OR certificate_id IS NOT NULL` is a CHECK, so a
    certificate id travels with the status — which is the invariant, not a fixture detail.
    """

    async def _update(database: Database) -> None:
        async with database.unit_of_work() as session:
            row = await session.get(CustomObjectiveRow, objective_id)
            assert row is not None
            row.certificate_id = new_uuid7()
            row.status = status.value

    _run(_update)


def _copy_into(workspace_id: UUID, objective: dict[str, Any]) -> UUID:
    """The same declaration, under another workspace.

    A direct insert because `grant` is workspace-scoped: no principal this test can build
    holds `model:fit` in a second workspace, so the row cannot be made through the route.
    The declaration is copied off a real response rather than hand-written — `applicability`
    is a `model-schema` shape and nothing here may define a second copy of it.
    """

    async def _insert(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            row = CustomObjectiveRow(
                id=new_uuid7(),
                workspace_id=workspace_id,
                slug=objective["slug"],
                version=objective["version"],
                status=ObjectiveStatus.DRAFT.value,
                kind=objective["kind"],
                template=objective["template"],
                params=objective["params"],
                applicability=objective["applicability"],
                hessian_strategy=objective["hessian_strategy"],
                hessian_min=objective["hessian_min"],
            )
            session.add(row)
            await session.flush()
            return row.id

    return _run(_insert)


def _require_an_unverifiable_evidence_kind(workspace_id: UUID) -> None:
    """A workspace policy naming evidence this build has no way to check.

    The only reachable route to `EVIDENCE_INCOMPLETE` over HTTP. `objective_certificate` —
    the floor's one kind — is verified as `certificate_id is not None`, and the CHECK above
    makes a `certified` row without one impossible; so a policy that asks for something else
    is what exercises `_require_evidence`'s fail-closed arm.
    """
    entry = DEFAULT_POLICY.entry_for("custom_objective")
    assert entry is not None
    tightened = ApprovalPolicy(
        policies=(
            entry.model_copy(
                update={"evidence": (*entry.evidence, "peer_review_note")}
            ),
        )
    )

    async def _insert(database: Database) -> None:
        async with database.unit_of_work() as session:
            session.add(
                ApprovalPolicyRow(
                    workspace_id=workspace_id,
                    policy=tightened.model_dump(mode="json"),
                )
            )

    _run(_insert)


# -- The permits ---------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-95")
def test_creating_a_template_objective_returns_201_as_a_draft(
    client: TestClient, author: dict[str, str]
) -> None:
    """201 and the artifact, not a Job — authoring is a declaration, certification is work.

    Asserts the declared kind and the resolved applicability on the way back out. A route
    that returned the request echoed, or a `Job`, would fail here rather than pass on 201.
    """
    slug = _slug()
    response = client.post(
        "/api/v1/custom-objectives",
        json={"slug": slug, "template": "poisson"},
        headers=author,
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["slug"] == slug
    assert body["version"] == 1
    assert body["kind"] == "template"
    assert body["template"] == "poisson"
    assert body["status"] == "draft"
    assert body["certificate_id"] is None
    #: Resolved from §4.5's catalogue, not sent by the caller — the field that proves the
    #: route did the template lookup rather than storing what it was handed.
    assert body["applicability"]["responses"]


@pytest.mark.req("FR-MODEL-95")
def test_an_objective_reads_back_with_its_declared_kind(
    client: TestClient, author: dict[str, str], reader: dict[str, str]
) -> None:
    """The get route, which `02` §5.1 gained with FR-MODEL-95.

    Authored by the `analyst` and read by the **`auditor`**, which holds `model:read` and
    not `model:fit`. Reading it back as the author would prove only that *some* authorised
    header works — the analyst holds both permissions, so a route re-gated on `model:fit`
    would keep this green while every read-only principal lost the artifact. Found by
    mutation on 2026-08-23 (W32-6).
    """
    created = _create(client, author)
    response = client.get(f"/api/v1/custom-objectives/{created['id']}", headers=reader)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["id"] == created["id"]
    assert body["slug"] == created["slug"]
    assert body["kind"] == "template"
    assert body["status"] == "draft"


@pytest.mark.req("FR-MODEL-95")
def test_usage_of_a_fresh_objective_is_empty_rather_than_missing(
    client: TestClient, author: dict[str, str], reader: dict[str, str]
) -> None:
    """FR-MODEL-47's blast radius, empty because nothing was fitted under it.

    The permit that makes the cross-workspace `usage` refusal below mean something: without
    it a 404 there could equally be a route that answers 404 to everyone. Read by the
    `auditor` for the reason the get above records — a blast-radius query is exactly what a
    read-only principal is expected to run.
    """
    created = _create(client, author)
    response = client.get(
        f"/api/v1/custom-objectives/{created['id']}/usage", headers=reader
    )
    assert response.status_code == 200, response.text
    assert response.json()["models"] == []


@pytest.mark.req("FR-MODEL-95")
def test_certifying_a_draft_returns_202_and_points_at_the_job(
    client: TestClient, author: dict[str, str]
) -> None:
    """202 and a `Location`. The checks end in a smoke fit, so nothing is answered inline."""
    created = _create(client, author)
    response = client.post(
        f"/api/v1/custom-objectives/{created['id']}/certify", json={}, headers=author
    )
    assert response.status_code == 202, response.text
    assert response.headers["Location"] == f"/api/v1/jobs/{response.json()['id']}"
    assert response.json()["kind"] == "objective.certify"


@pytest.mark.req("FR-MODEL-95")
def test_certify_stores_the_resolved_sampling_grid_not_the_absent_request(
    client: TestClient, author: dict[str, str]
) -> None:
    """A caller who names no grid gets `default_sampling`'s, **resolved at the route**.

    The worker must certify over the grid this response implies. If the Job carried no
    sampling and the worker re-derived it, a later change to the default rule would silently
    change what an already-queued Job measures — and the certificate would name a grid the
    approver never saw.

    `default_sampling` is imported rather than its result hard-coded: a literal here would
    keep passing after the default changed *and* the route stopped applying it.
    """
    created = _create(client, author)
    response = client.post(
        f"/api/v1/custom-objectives/{created['id']}/certify", json={}, headers=author
    )
    assert response.status_code == 202, response.text
    expected = default_sampling(CustomObjective.model_validate(created))
    assert response.json()["parameters"]["sampling"] == expected.model_dump(mode="json")


@pytest.mark.req("FR-MODEL-95")
def test_a_certified_objective_submits_into_review(
    client: TestClient, author: dict[str, str], submitter: dict[str, str]
) -> None:
    """`certified → review`, with the approval request the submission exists to create.

    The permit beside the three submit refusals below. Authored by the `analyst` and
    submitted by the `pricing_actuary`, which is the separation the two fixtures exist for.
    """
    created = _create(client, author)
    _advance(UUID(created["id"]), status=ObjectiveStatus.CERTIFIED)
    response = client.post(
        f"/api/v1/custom-objectives/{created['id']}/submit",
        json={"change_summary": "Tweedie power narrowed after the Q3 refresh."},
        headers=submitter,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "review"
    assert body["approval_request_id"] is not None


# -- The workspace boundary ------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-95")
def test_an_objective_in_another_workspace_is_not_found(
    client: TestClient, author: dict[str, str]
) -> None:
    """`_get_or_404` folds the workspace into its predicate, so the answer is 404 and not
    403 — the id must not be confirmed to exist.

    The caller is a **fully authorised principal of this workspace** asking for a row that
    lives in another. One holding no role would meet the RBAC refusal instead and prove
    nothing about scoping. A route that lost the fold would hand other workspaces' objectives
    to any authorised reader, and every single-workspace test would stay green.
    """
    elsewhere = _copy_into(new_uuid7(), _create(client, author))
    response = client.get(f"/api/v1/custom-objectives/{elsewhere}", headers=author)
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-MODEL-95")
def test_usage_of_an_objective_in_another_workspace_is_not_found(
    client: TestClient, author: dict[str, str]
) -> None:
    """The same boundary on the route that answers "what does this reach".

    Tested separately from the get because there is **no list route** — this is the one
    endpoint whose leak would be a set of another workspace's models rather than a single
    artifact, and it reaches the objective through its own call to `_get_or_404`.
    """
    elsewhere = _copy_into(new_uuid7(), _create(client, author))
    response = client.get(f"/api/v1/custom-objectives/{elsewhere}/usage", headers=author)
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "NOT_FOUND"


# -- The permission refusals -----------------------------------------------------------------


@pytest.mark.req("FR-MODEL-95")
def test_creating_an_objective_without_model_fit_is_refused(
    client: TestClient, reader: dict[str, str]
) -> None:
    """**Negative.** The body is the same valid one the permit above sends, so the refusal
    cannot be the 422 a malformed request would earn."""
    response = client.post(
        "/api/v1/custom-objectives",
        json={"slug": _slug(), "template": "poisson"},
        headers=reader,
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-MODEL-95")
def test_reading_an_objective_without_model_read_is_refused(
    client: TestClient, author: dict[str, str], stranger: dict[str, str]
) -> None:
    """**Negative.** The id exists, so the 403 is the permission's answer and not a 404
    wearing one."""
    created = _create(client, author)
    response = client.get(f"/api/v1/custom-objectives/{created['id']}", headers=stranger)
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-MODEL-95")
def test_certifying_without_model_fit_is_refused(
    client: TestClient, author: dict[str, str], reader: dict[str, str]
) -> None:
    """`model:read` is not enough to *start* a certification: it queues a compute Job that
    samples a grid and trains a smoke booster.

    The objective is a `draft`, which the permit above certifies successfully — so the 403 is
    the permission and not the state.
    """
    created = _create(client, author)
    response = client.post(
        f"/api/v1/custom-objectives/{created['id']}/certify", json={}, headers=reader
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-MODEL-95")
def test_submitting_without_model_submit_is_refused(
    client: TestClient, author: dict[str, str]
) -> None:
    """The sharpest pairing in this file: the caller **authored** this objective and is
    refused permission to submit it.

    Putting an artifact in front of an approver starts a governed process, and the role that
    may write is not automatically the role that may do that. The objective is `certified`,
    which the permit above submits successfully — so this is the permission and not the 409
    the wrong state would give.
    """
    created = _create(client, author)
    _advance(UUID(created["id"]), status=ObjectiveStatus.CERTIFIED)
    response = client.post(
        f"/api/v1/custom-objectives/{created['id']}/submit",
        json={"change_summary": "Ready for review."},
        headers=author,
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"


# -- The conflicts ---------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-95")
def test_certifying_an_objective_under_review_conflicts(
    client: TestClient, author: dict[str, str]
) -> None:
    """409, because a run that came back `failed` would move evidence a live decision rests
    on.

    Not "already certified" — `certifiable_or_refuse` admits `certified` deliberately, since
    re-certifying after a library upgrade is how a finding is found. `review` and past is
    where the certificate is being read.
    """
    created = _create(client, author)
    _advance(UUID(created["id"]), status=ObjectiveStatus.REVIEW)
    response = client.post(
        f"/api/v1/custom-objectives/{created['id']}/certify", json={}, headers=author
    )
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-MODEL-95")
def test_submitting_an_objective_twice_conflicts(
    client: TestClient, author: dict[str, str], submitter: dict[str, str]
) -> None:
    """The second submission meets a row already in `review`, and `review` is not a state
    FR-MODEL-46 reaches `review` from.

    Driven through the route twice rather than seeded into `review`, so what is observed is
    the transition the first call performed.
    """
    created = _create(client, author)
    _advance(UUID(created["id"]), status=ObjectiveStatus.CERTIFIED)
    body = {"change_summary": "Ready for review."}
    first = client.post(
        f"/api/v1/custom-objectives/{created['id']}/submit", json=body, headers=submitter
    )
    assert first.status_code == 200, first.text
    second = client.post(
        f"/api/v1/custom-objectives/{created['id']}/submit", json=body, headers=submitter
    )
    assert second.status_code == 409, second.text
    assert second.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-MODEL-95")
def test_submitting_without_the_required_evidence_is_refused(
    client: TestClient, author: dict[str, str], submitter: dict[str, str], workspace_id: UUID
) -> None:
    """422 `EVIDENCE_INCOMPLETE`, and the distinction from the 409 above matters to a caller:
    one means "not in a state that can be submitted", the other "in the right state and still
    short of what the policy asks for".

    `_require_evidence` fails **closed** on a kind it cannot verify — treating an uncheckable
    requirement as met would make a policy tightening do nothing. The refusal names the kind,
    which is the half a submitter can act on.
    """
    _require_an_unverifiable_evidence_kind(workspace_id)
    created = _create(client, author)
    _advance(UUID(created["id"]), status=ObjectiveStatus.CERTIFIED)
    response = client.post(
        f"/api/v1/custom-objectives/{created['id']}/submit",
        json={"change_summary": "Ready for review."},
        headers=submitter,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "EVIDENCE_INCOMPLETE"
    assert "peer_review_note" in response.json()["detail"]


# -- The expression kind, refused ------------------------------------------------------------


@pytest.mark.req("FR-MODEL-75")
def test_creating_an_expression_objective_is_refused_by_name(
    client: TestClient, author: dict[str, str]
) -> None:
    """409 `OBJECTIVE_KIND_NOT_ENABLED`, not a 422 about an unexpected key.

    The permit is `test_creating_a_template_objective_returns_201_as_a_draft` above: the same
    caller, the same route, the same body but for `kind` — so what is observed is the kind
    and not some other property of the request. Phase 1 ships template objectives only
    (FR-MODEL-75), and the difference between "no such concept" and "not until Phase 2" is
    exactly what a 404 here would destroy.
    """
    response = client.post(
        "/api/v1/custom-objectives",
        json={"slug": _slug(), "kind": "expression", "template": "poisson"},
        headers=author,
    )
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "OBJECTIVE_KIND_NOT_ENABLED"
