---
id: FD-1508
family: finding
title: A deployment policy entry naming an Environment with no predecessor is accepted at policy save and refused at every Deployment Request into it
status: active
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: auditor
tree: 47d770e8fcbd2410fa101019ed8cf3aae69a1baa
corrected_by: []
relates: [WK-674, FR-429, FR-364, RL-1301, RL-1401, RL-1404]
---

# FD-1508 — a gated entry with no predecessor is refused late

**Filed** by auditor-fdc2 on 2026-10-05, from the lead's routing R1 (`~/gi-pricing-plan.local/channel/from-lead-2026-10-04.md`,
line 87: "(R1) refusing a gated policy entry with no predecessor at policy save (instead of at every request): to the
next FD batch, owner WK-674"). Every line number below was read at `origin/main` =
`47d770e8fcbd2410fa101019ed8cf3aae69a1baa`, the `tree:` above. The id is a working id until the lead mints it.

*Re-checked 2026-10-05 at main `caa4e411a9c07a389cf47092a923c7761b2b92dc`: every code, spec and test cite below
still resolves at the same lines, and the defect still stands there. `set_policy` (`approvals.py:174`) still checks
only that a `deployment` entry's Environment exists (`:209-215`), `submit_request` still refuses a predecessor-less
gated target at `:264-279`, and `EnvironmentUpdate` still forbids `requires_prior_environment` (`extra="forbid"`).
The maintainer's (by delegation) corrected reason in "Severity (the maintainer's (by delegation))" was compared with the entry "2026-10-05 09:51:31 BST —
CORRECTION (mine) …" in `to-lead.md` (line 16894 and its "Corrected reason" bullet, line 16895) and is verbatim.*

## Finding

An Approval Policy `deployment` entry that names an Environment whose `requires_prior_environment` is `null` is
**accepted** by `PUT /api/v1/approval-policy`, and from then on **every** Deployment Request into that Environment is
refused 422 `EVIDENCE_INCOMPLETE`. The refusal is at request time, not at save time, and the request-time detail now
names the remedy (remove the entry). Nothing at save tells the administrator that the entry they just saved makes the
Environment undeployable.

**The save path checks the name and nothing else.** `set_policy` (`backend/src/app/platform/approvals.py:174`) refuses a
policy below the evidence floor (`:189`) and a `deployment` entry whose Environment does not exist or is retired
(`:209-215`, `environments.require_existing`). It does not read `requires_prior_environment`.

**The request path refuses every time.** In `submit_request` (`backend/src/app/platform/deployments.py:206`), the
`uat_deployment` item is `deployed.id if deployed is not None else body.skip if predecessor is not None else None`
(`:264-266`). With no predecessor both arms are empty, `pinned` is `None`, and `:267` raises 422 `EVIDENCE_INCOMPLETE`
with the detail at `:276-279` ("… has no predecessor Environment to pin a deployment or a skip of, so every request
into it is refused. Remove the `deployment` policy entry for … to make it an ungated target
(`requires_prior_environment` cannot be changed after creation)."). The deploy route cannot rescue it: for an Environment
with an entry, `deploy` (`:438`) takes the `else` branch and requires an executable approved Deployment Request
(`_executable_request`, `:574`), and none can exist.

**`requires_prior_environment` cannot be corrected.** `EnvironmentUpdate` admits `name` and `description` only
(`packages/model-schema/src/model_schema/deployments.py:87-95`, `extra="forbid"`). So the only ways out are removing the
entry (another policy PUT) or creating a new Environment.

This is **ruled behaviour at request time**, and this finding does not dispute it. `RL-1404` D2 decided that "the refusal
at `submit_request` … stands, with its registered code `EVIDENCE_INCOMPLETE`" and added the remedy to the detail, and
`03` §4.12 (`docs/specs/03-rating-engine.md:882`) says "A gated target with no predecessor … has no predecessor item to
pin, so every Deployment Request into it is refused with 422 `EVIDENCE_INCOMPLETE`". `RL-1404` left the save-time
question explicitly unruled:

> **Not ruled here** (beyond D2): whether `PUT /api/v1/approval-policy` should refuse, at save, a `deployment` entry
> naming an Environment with no predecessor. That is a new refusal on another route; it is the lead's to route if wanted.

The lead routed it here (R1).

## Evidence

At `47d770e8fcbd2410fa101019ed8cf3aae69a1baa` (`git rev-parse HEAD` in the worktree):

```
$ sed -n 209,215p backend/src/app/platform/approvals.py
    for entry in policy.policies:
        if entry.artifact_type == "deployment" and entry.environment is not None:
            await environments.require_existing(
                session,
                entry.environment,
                subject="An approval policy `deployment` entry",
            )

$ sed -n 264,267p backend/src/app/platform/deployments.py
    pinned: UUID | PromotionSkip | None = (
        deployed.id if deployed is not None else body.skip if predecessor is not None else None
    )
    if reason is not None or approval is None or pinned is None:

$ grep -rn "set_policy(" backend/src
backend/src/app/api/approvals.py:334:        return await service.set_policy(
backend/src/app/platform/approvals.py:174:async def set_policy(
```

`set_policy` has one caller, so one check at its entry covers the route.

**An existing test already exercises the accepted-save half.** `backend/tests/test_deployments.py:781-799`
(`_gated_environment`) creates an Environment with `requires_prior_environment: None` (`:793`) and then calls
`_set_policy_entry` (`:802-818`), which PUTs the policy and asserts `status_code == 200` (`:816`). The refusal then
asserted at `:823-845`
(`test_a_gated_environment_with_no_predecessor_refuses_every_request_naming_the_remedy`) is the late one. I did not
run these tests: this environment has no Postgres client (`createdb: command not found`) and no per-worktree test
database, so a targeted run is skipped. The claims above are code readings plus what the existing test asserts.

### The requirement

`07` FR-429 (promotion order, as amended 2026-09-28, `RL-1232` DP-7) and `06` FR-364 (the evidence floor: a floor kind
is never removed) are what make the request-time refusal right (`RL-1404` D2). Neither says when the contradiction
between "entry present" and "no predecessor to pin" is detected. `RL-1301` A.6 already puts one policy-save check on a
`deployment` entry: the named Environment must exist, "a name no Environment has (`prd` for `prod`) would leave the real
target ungated" (comment at `approvals.py:204-208`). A predecessor check is the same kind of check on the same line.

## Severity (the maintainer's (by delegation))

**LOW (the maintainer's (by delegation)).** Nothing is mispriced and nothing deploys that should not: the refusal is
fail-closed, loud, and names its remedy (`RL-1404` D2). The cost is that an administrator discovers the mistake at the
first deployment attempt instead of at the policy edit. It is not NONE because the state is permanent for the
Environment (the field is immutable) and the only discovery point is a user trying to deploy.

**The maintainer's (by delegation) reason, recorded as a dated correction.** Amended 2026-10-05 before mint: the entry
"2026-10-05 09:51:31 BST — CORRECTION (mine) to the R1 reason in \"2026-10-05 09:44:39 BST — DISPATCH GO: FD-1356 fix …\"" in
`~/gi-pricing-plan.local/channel/to-lead.md` (a local file) says, quoted from it: "R1 = a gated policy entry with no
predecessor Environment, accepted at policy save (from-lead-2026-10-04.md:87), NOT a retired Environment. Severity LOW
re-confirmed", and gives the **Corrected reason**: "each deployment request to such a target is already refused 422
EVIDENCE_INCOMPLETE, with a detail naming the remedy (RL-1404 D2). So the misconfiguration fails closed at use; refusing it
at save time is an earlier-feedback improvement. FD-1508 carries this reason." Severity is therefore LOW, confirmed, not
provisional. That is the same reason as the paragraph above: the target is not live-deployable by mistake, because the
refusal is already in force at every request.

**Owner: WK-674.**

## Disposition

**Proposed: a decision for the decision-maker, then a fix owned by WK-674.** Options, not a pick:

1. **Refuse at save** (the lead's R1): in `set_policy`, for each `deployment` entry naming an Environment, read
   `requires_prior_environment` and refuse the policy when it is `null`, with a registered code (`VALIDATION_FAILED`
   at 422, as the existence check does; the code is the decision-maker's) and the same remedy sentence. This needs a
   dated amendment to `06` FR-364's or `07` FR-429's text, because it is a new refusal on a route (`RL-1404`).
2. **Leave as ruled.** The request-time refusal with its remedy already stands.

If (1) is chosen, a red test belongs at the policy route (a PUT naming a predecessor-less Environment is 422 and writes
no policy row), and `_gated_environment` at `test_deployments.py:781` is the helper that needs to change, since it
currently relies on the save being accepted.

## What this finding does NOT claim

- It does not claim the request-time refusal is wrong. `RL-1404` D2 rules it right, and `03` §4.12 says so.
- It does not claim a run. The accepted-save half is read from `set_policy` and from an existing test's `200` assertion;
  I did not execute that test here.
- It does not claim anything about unqualified `deployment` entries (`environment is None`). `entry_for`
  (`packages/model-schema/src/model_schema/approvals.py:177-`) falls back to such an entry for any Environment, and
  `set_policy`'s check at `approvals.py:209` skips entries with no `environment`. Whether an unqualified entry would
  also gate a predecessor-less Environment such as `dev` is unexamined here and would belong to the same decision.
- It does not claim a second route is affected. `set_policy` is the only caller of the policy write at `47d770e8`.
