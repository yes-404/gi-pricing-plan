"""The approval state machine (`06` §3.2, R1, FR-GOV-9/11/12/13/14/15)."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.db.models import ApprovalDecisionRow, AuditEventRow, RoleAssignmentRow, RoleRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals, rbac
from model_schema import (
    DEFAULT_POLICY,
    ActorKind,
    ApprovalStatus,
    ArtifactRef,
    DecisionKind,
    Principal,
    ScopeType,
    new_uuid7,
)

MODEL = ArtifactRef.parse("model:motor-ad-frequency@7")
RATING = ArtifactRef.parse("rating_version:motor-gb@27")


def _user(label: str = "u") -> Principal:
    return Principal(kind=ActorKind.USER, id=new_uuid7(), display=f"{label}@insurer.example")


async def _with_role(database: Database, workspace_id, principal: Principal, role: str):
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        row = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == role
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=principal.id,
                role_id=row.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )


async def _submit(database: Database, workspace_id, submitter: Principal, ref=MODEL):
    async with database.unit_of_work() as session:
        row = await approvals.submit(
            session,
            workspace_id=workspace_id,
            submitter=submitter,
            artifact_ref=ref,
            change_summary="AD frequency refit on 2026H1 data.",
        )
        return row.id


# -- separation of duties (R1, FR-GOV-11) ------------------------------------------------


@pytest.mark.req("FR-GOV-11")
async def test_the_submitter_cannot_approve_their_own_work(
    database: Database, workspace_id
) -> None:
    """`06` R1. Checked before the permission, so a submitter who *is* an approver gets the
    true reason rather than a misleading one about permissions."""
    submitter = _user("submitter")
    await _with_role(database, workspace_id, submitter, "approver")
    request_id = await _submit(database, workspace_id, submitter)

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await approvals.decide(
                session,
                workspace_id=workspace_id,
                request_id=request_id,
                approver=submitter,
                decision=DecisionKind.APPROVE,
            )
    assert exc.value.code == "SUBMITTER_CANNOT_APPROVE"
    assert exc.value.status_code == 403


@pytest.mark.req("FR-GOV-11")
async def test_two_approvals_must_come_from_distinct_principals(
    database: Database, workspace_id
) -> None:
    """Negative, enforced by a unique constraint rather than by a check that can be
    forgotten: a second decision from the same person cannot be stored."""
    submitter, approver = _user("s"), _user("a")
    await _with_role(database, workspace_id, approver, "approver")
    request_id = await _submit(database, workspace_id, submitter, ref=RATING)

    async with database.unit_of_work() as session:
        await approvals.decide(
            session,
            workspace_id=workspace_id,
            request_id=request_id,
            approver=approver,
            decision=DecisionKind.APPROVE,
        )
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await approvals.decide(
                session,
                workspace_id=workspace_id,
                request_id=request_id,
                approver=approver,
                decision=DecisionKind.APPROVE,
            )
    assert exc.value.code == "DUPLICATE_APPROVER"


@pytest.mark.req("FR-GOV-11")
def test_separation_of_duties_cannot_be_configured_away() -> None:
    """`06` §4.2 marks it `configurable: false`; a rule configuration can disable is not one."""
    from model_schema import ApprovalPolicy

    with pytest.raises(ValueError, match="cannot be true"):
        ApprovalPolicy(submitter_may_approve=True)


# -- the lifecycle (FR-GOV-9) -------------------------------------------------------------


@pytest.mark.req("FR-GOV-9")
async def test_one_approval_approves_a_model(database: Database, workspace_id) -> None:
    submitter, approver = _user("s"), _user("a")
    await _with_role(database, workspace_id, approver, "approver")
    request_id = await _submit(database, workspace_id, submitter)

    async with database.unit_of_work() as session:
        row = await approvals.decide(
            session,
            workspace_id=workspace_id,
            request_id=request_id,
            approver=approver,
            decision=DecisionKind.APPROVE,
            comment="Diagnostics are clean.",
        )
    assert row.status == ApprovalStatus.APPROVED
    assert row.decided_at is not None


@pytest.mark.req("FR-GOV-12")
async def test_a_rating_version_needs_two_approvals(
    database: Database, workspace_id
) -> None:
    """The policy, not the machine, decides how many (`06` §4.2)."""
    submitter, first, second = _user("s"), _user("a1"), _user("a2")
    for approver in (first, second):
        await _with_role(database, workspace_id, approver, "approver")
    request_id = await _submit(database, workspace_id, submitter, ref=RATING)

    async with database.unit_of_work() as session:
        row = await approvals.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=first, decision=DecisionKind.APPROVE,
        )
    assert row.status == ApprovalStatus.REVIEW  # still open after one

    async with database.unit_of_work() as session:
        row = await approvals.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=second, decision=DecisionKind.APPROVE,
        )
    assert row.status == ApprovalStatus.APPROVED


@pytest.mark.req("FR-GOV-13")
async def test_requesting_changes_needs_a_comment_and_returns_to_draft(
    database: Database, workspace_id
) -> None:
    submitter, approver = _user("s"), _user("a")
    await _with_role(database, workspace_id, approver, "approver")
    request_id = await _submit(database, workspace_id, submitter)

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await approvals.decide(
                session, workspace_id=workspace_id, request_id=request_id,
                approver=approver, decision=DecisionKind.REQUEST_CHANGES,
            )
    assert exc.value.title == "Requesting changes requires a comment"

    async with database.unit_of_work() as session:
        row = await approvals.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.REQUEST_CHANGES,
            comment="Young-driver relativities need the GIPP evidence attached.",
        )
    assert row.status == ApprovalStatus.CHANGES_REQUESTED


@pytest.mark.req("FR-GOV-9")
async def test_a_decided_request_cannot_be_decided_again(
    database: Database, workspace_id
) -> None:
    """Negative: an approved request reopened is an approval nobody granted."""
    submitter, first, second = _user("s"), _user("a1"), _user("a2")
    for approver in (first, second):
        await _with_role(database, workspace_id, approver, "approver")
    request_id = await _submit(database, workspace_id, submitter)

    async with database.unit_of_work() as session:
        await approvals.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=first, decision=DecisionKind.APPROVE,
        )
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await approvals.decide(
                session, workspace_id=workspace_id, request_id=request_id,
                approver=second, decision=DecisionKind.REJECT,
            )
    assert exc.value.code == "APPROVAL_ALREADY_DECIDED"


# -- pinning (FR-GOV-14) -----------------------------------------------------------------


@pytest.mark.req("FR-GOV-14")
async def test_an_approval_does_not_carry_over_to_a_new_version(
    database: Database, workspace_id
) -> None:
    """FR-GOV-14, structural rather than checked.

    The request names `model:…@7`; a changed artifact is `@8` and a different reference, so
    there is no staleness check to forget. The proof is that `@8` can be submitted while
    `@7` is approved — they are separate requests, not one carried forward.
    """
    submitter, approver = _user("s"), _user("a")
    await _with_role(database, workspace_id, approver, "approver")
    first = await _submit(database, workspace_id, submitter, ref=MODEL)

    async with database.unit_of_work() as session:
        await approvals.decide(
            session, workspace_id=workspace_id, request_id=first,
            approver=approver, decision=DecisionKind.APPROVE,
        )

    successor = ArtifactRef.parse("model:motor-ad-frequency@8")
    second = await _submit(database, workspace_id, submitter, ref=successor)
    assert second != first

    async with database.session() as session:
        from app.db.models import ApprovalRequestRow

        row = await session.get(ApprovalRequestRow, second)
    assert row.status == ApprovalStatus.REVIEW
    assert row.artifact_ref == "model:motor-ad-frequency@8"


@pytest.mark.req("FR-GOV-9")
async def test_one_artifact_version_cannot_have_two_open_requests(
    database: Database, workspace_id
) -> None:
    """Negative: two open reviews can reach different answers, with nothing to say which
    one a deployment obeys."""
    submitter = _user("s")
    await _submit(database, workspace_id, submitter)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await approvals.submit(
                session,
                workspace_id=workspace_id,
                submitter=submitter,
                artifact_ref=MODEL,
                change_summary="again",
            )
    assert exc.value.title == "This artifact version is already under review"


# -- withdrawal (FR-GOV-15) ---------------------------------------------------------------


@pytest.mark.req("FR-GOV-15")
async def test_an_approval_can_be_withdrawn_before_deployment(
    database: Database, workspace_id
) -> None:
    submitter, approver = _user("s"), _user("a")
    await _with_role(database, workspace_id, approver, "approver")
    request_id = await _submit(database, workspace_id, submitter)

    async with database.unit_of_work() as session:
        await approvals.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE,
        )
    async with database.unit_of_work() as session:
        row = await approvals.withdraw(
            session, workspace_id=workspace_id, request_id=request_id,
            actor=approver, reason="Superseded by a corrected refit.",
        )
    assert row.status == ApprovalStatus.WITHDRAWN
    assert row.withdrawn_reason.startswith("Superseded")


@pytest.mark.req("FR-GOV-15")
async def test_an_approval_cannot_be_withdrawn_once_the_artifact_is_live(
    database: Database, workspace_id
) -> None:
    """Negative: it would leave live behaviour with no approval behind it."""
    submitter, approver = _user("s"), _user("a")
    await _with_role(database, workspace_id, approver, "approver")
    request_id = await _submit(database, workspace_id, submitter)

    async with database.unit_of_work() as session:
        await approvals.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE,
        )
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await approvals.withdraw(
                session, workspace_id=workspace_id, request_id=request_id,
                actor=approver, reason="changed my mind", artifact_is_live=True,
            )
    assert exc.value.code == "WITHDRAW_AFTER_DEPLOY_FORBIDDEN"


@pytest.mark.req("FR-GOV-15")
async def test_withdrawal_requires_a_reason(database: Database, workspace_id) -> None:
    submitter, approver = _user("s"), _user("a")
    await _with_role(database, workspace_id, approver, "approver")
    request_id = await _submit(database, workspace_id, submitter)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await approvals.withdraw(
                session, workspace_id=workspace_id, request_id=request_id,
                actor=approver, reason="  ",
            )
    assert exc.value.title == "Withdrawal requires a reason"


# -- policy (FR-GOV-12) --------------------------------------------------------------------


@pytest.mark.req("FR-GOV-12")
async def test_a_role_the_policy_does_not_name_cannot_approve(
    database: Database, workspace_id
) -> None:
    """Negative: `approval:decide` is necessary, not sufficient — the policy names roles."""
    submitter, deployer = _user("s"), _user("d")
    await _with_role(database, workspace_id, deployer, "deployer")
    # Give the deployer the raw permission so the refusal is about the *role*, not the
    # permission — otherwise this test passes for the wrong reason.
    await _with_role(database, workspace_id, deployer, "approver")
    request_id = await _submit(database, workspace_id, submitter)

    async with database.unit_of_work() as session:
        policy = await approvals.policy_for(session, workspace_id)
        from model_schema import ApprovalPolicy, ApprovalPolicyEntry

        narrowed = ApprovalPolicy(
            policies=(
                ApprovalPolicyEntry(
                    artifact_type="model",
                    approvers_required=1,
                    approver_roles=("admin",),
                ),
                *[p for p in policy.policies if p.artifact_type != "model"],
            )
        )
        from app.db.models import ApprovalPolicyRow as PolicyRow

        session.add(
            PolicyRow(workspace_id=workspace_id, policy=narrowed.model_dump(mode="json"))
        )

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await approvals.decide(
                session, workspace_id=workspace_id, request_id=request_id,
                approver=deployer, decision=DecisionKind.APPROVE,
            )
    assert exc.value.code == "PERMISSION_DENIED"
    assert "admin" in (exc.value.detail or "")


@pytest.mark.req("FR-GOV-12")
async def test_an_artifact_type_with_no_policy_cannot_be_submitted(
    database: Database, workspace_id
) -> None:
    """Approving against no policy is approving against no requirement."""
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await approvals.submit(
                session,
                workspace_id=workspace_id,
                submitter=_user("s"),
                artifact_ref=ArtifactRef.parse("dataset:motor-gb@3"),
                change_summary="new snapshot",
            )
    assert exc.value.title == "No approval policy for this artifact type"


# -- auditing (FR-GOV-20) --------------------------------------------------------------------


@pytest.mark.req("FR-GOV-20")
async def test_every_step_is_audited_and_the_chain_verifies(
    database: Database, workspace_id
) -> None:
    from app.platform import audit as audit_service

    submitter, approver = _user("s"), _user("a")
    await _with_role(database, workspace_id, approver, "approver")
    request_id = await _submit(database, workspace_id, submitter)
    async with database.unit_of_work() as session:
        await approvals.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE, comment="clean",
        )
    async with database.unit_of_work() as session:
        await approvals.withdraw(
            session, workspace_id=workspace_id, request_id=request_id,
            actor=approver, reason="superseded",
        )

    async with database.session() as session:
        actions = [
            e.action
            for e in (
                await session.execute(
                    select(AuditEventRow)
                    .where(AuditEventRow.workspace_id == workspace_id)
                    .order_by(AuditEventRow.sequence)
                )
            ).scalars()
        ]
        checked = await audit_service.verify_chain(session, workspace_id)

    assert "approval_request.submitted" in actions
    assert "approval_request.approve" in actions
    assert "approval_request.withdrawn" in actions
    assert checked == len(actions)


@pytest.mark.req("FR-GOV-11")
async def test_a_decision_is_recorded_against_its_approver(
    database: Database, workspace_id
) -> None:
    submitter, approver = _user("s"), _user("a")
    await _with_role(database, workspace_id, approver, "approver")
    request_id = await _submit(database, workspace_id, submitter)
    async with database.unit_of_work() as session:
        await approvals.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE, comment="ok",
        )
    async with database.session() as session:
        decision = (
            await session.execute(
                select(ApprovalDecisionRow).where(
                    ApprovalDecisionRow.request_id == request_id
                )
            )
        ).scalar_one()
    assert decision.approver_id == approver.id
    assert decision.comment == "ok"

@pytest.mark.req("FR-GOV-37")
async def test_a_policy_below_the_evidence_floor_is_refused(
    database: Database, workspace_id
) -> None:
    """Negative: `06` §3.3 is a floor and §4.2 may only add to it (OQ-GOV-7).

    The deciding case, run as written: an admin editing the transparency kind out of the
    model policy. Submission would enforce the union regardless, so what this refusal
    protects is the policy *document* — an insurer reading its own policy is entitled to see
    what a submission will be held to, and one that says less than the platform enforces
    misleads the only person who can change it.
    """
    from model_schema import ApprovalPolicy, ApprovalPolicyEntry

    admin = _user("a")
    await _with_role(database, workspace_id, admin, "admin")

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await approvals.set_policy(
                session,
                workspace_id=workspace_id,
                actor=admin,
                policy=ApprovalPolicy(
                    policies=(
                        ApprovalPolicyEntry(
                            artifact_type="model",
                            approvers_required=1,
                            approver_roles=("approver",),
                            evidence=("diagnostics",),
                        ),
                    )
                ),
            )
    assert exc.value.code == "POLICY_BELOW_EVIDENCE_FLOOR"
    assert "transparency_artifact_if_non_glm" in (exc.value.detail or "")

    #: And nothing was stored: a refused edit must leave the previous policy in force,
    #: rather than a workspace ending up with neither the old policy nor the new one.
    async with database.unit_of_work() as session:
        assert await approvals.policy_for(session, workspace_id) == DEFAULT_POLICY


@pytest.mark.req("FR-GOV-37")
async def test_a_policy_stored_below_the_floor_is_still_submitted_against_the_floor(
    database: Database, workspace_id
) -> None:
    """A policy written before FR-GOV-37 cannot dodge the floor by being old.

    Written straight into the table, which is how a pre-2026-08-18 row got there: `set_policy`
    would refuse it now. Loading it is deliberate — refusing at read time would lock a
    workspace out of its own approvals — so the floor is applied at the point of use instead.
    """
    from app.db.models import ApprovalPolicyRow as PolicyRow
    from model_schema import ApprovalPolicy, ApprovalPolicyEntry

    legacy = ApprovalPolicy(
        policies=(
            ApprovalPolicyEntry(
                artifact_type="model",
                approvers_required=1,
                approver_roles=("approver",),
                evidence=(),
            ),
        )
    )
    async with database.unit_of_work() as session:
        session.add(
            PolicyRow(workspace_id=workspace_id, policy=legacy.model_dump(mode="json"))
        )

    async with database.unit_of_work() as session:
        stored = await approvals.policy_for(session, workspace_id)
    assert stored.entry_for("model").evidence == ()
    assert stored.effective_evidence("model") == (
        "diagnostics",
        "transparency_artifact_if_non_glm",
    )
