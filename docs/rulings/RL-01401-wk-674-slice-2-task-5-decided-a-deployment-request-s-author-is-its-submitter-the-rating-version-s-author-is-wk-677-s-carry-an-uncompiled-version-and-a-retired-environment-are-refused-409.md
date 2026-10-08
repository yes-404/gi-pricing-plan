---
id: RL-1401
family: ruling
title: WK-674 Slice 2 Task 5 decided — a Deployment Request's Author is the actor of its deployment_request.created event, so FR-353 gains an eighth type and is not weakened; the deployed Rating Version's Author is a pinned component's Author and stays WK-677's carry; an uncompiled version is refused 409 BUNDLE_COMPILE_FAILED and a retired Environment 409 VALIDATION_FAILED
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-03              # the mint date (check 31); ruled 2026-10-03
owner: decision-maker
tree: 8252741cc3849058b6fc6836967448d88ff9821c
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: [RL-1497]
corrects: ~
relates: [PL-1392, SL-1256, RL-1301, RL-1296, RL-1379, RL-1236, FR-353, FR-267, FR-238, FR-239, FR-272, FR-428, FR-429]
---

# RL-1401 — WK-674 Slice 2 Task 5 decided: the deployment request's Author, the uncompiled-version refusal, the retired-Environment refusal

## How this was ruled

- **Filed under working id 9736, allocated by the lead.** The mint replaces the working id (RL 9736) with
  the minted id everywhere it appears, in this record and in the texts of §"Spec texts".
- **Mandate:** the lead's GO in `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed
  "2026-10-03 23:13:48 BST — GO: dm-1256 (opus/medium, WK-674's one DM today) rules RL 9736 —
  the deployment request's author resolution, the uncompiled-version refusal, the
  retired-Environment refusal — in ONE record". Its conditions 1–3 are answered item by item
  below; condition 4 (one audit, then the mint; Task 5's positive control red first) is the
  lead's sequence and is restated in the delta.
- **The stop being ruled:** `~/gi-pricing-plan.local/channel/from-lead-2026-10-03.md`, the
  entry headed "2026-10-03 23:13:32 BST — WK-674 S2 Task 5 STOPPED on an open design choice
  (correctly); …". It gives the executor's options (a) add `"deployment":
  "deployment_request.created"`, (b) skip the author check; and the two gaps (c) the
  uncompiled-version code, (d) the retired-Environment refusal.
- **Decided by the decision-maker, 2026-10-03**, drafted from 23:17:28 BST
  (`TZ=Europe/London date`), on branch `rl-9736-wk-674-s2-deploy-author-and-refusals` cut
  from origin/main `8252741c`. **Effort: medium** (`echo $CLAUDE_EFFORT` printed `medium`;
  the charter's "Model / effort" line, inherited from the lead; no raise to high was given).
- **Two trees were read.** Spec and ruling text at origin/main `8252741c`; the slice's code
  and its unmerged spec text at the S2 branch `sl-1256-environment-and-deployment-record`,
  commit `14c7e805` (Tasks 0–4). A locator below carries `@14c7e805` when it is read there,
  and is at `8252741c` otherwise.

## Premises, verified

| Claim | Verdict | Where |
|---|---|---|
| `CREATION_ACTIONS` has seven keys and no `deployment`; an absent type fails closed | **true** | `backend/src/app/platform/approvals.py:102-115` @14c7e805: keys `model`, `custom_objective`, `custom_metric`, `peril_structure`, `validation_rule`, `dataset_version`, `rating_version`; comment `:106` *"A type absent here has no author the check can find, and fails closed."* |
| The author lookup matches the event's `entity_ref` to the approval request's `artifact_ref` | **true** | `_author_of`, `approvals.py:553-577` @14c7e805: `AuditEventRow.entity_ref == row.artifact_ref`, `AuditEventRow.action == action`, earliest first; `action is None` returns `None` (`:562-564`) |
| `decide` checks R1, then the Author, then refuses an unresolved Author | **true** | `approvals.py:372-401` @14c7e805: `SUBMITTER_CANNOT_APPROVE` 403, then `APPROVAL_AUTHOR_UNRESOLVED` 403, then `AUTHOR_CANNOT_APPROVE` 403 |
| `deployment` is an approvable type in the policy and the floor | **true** | `packages/model-schema/src/model_schema/approvals.py:109` (`EVIDENCE_FLOOR`) and `:343` (`DEFAULT_POLICY` entry) @14c7e805 — the only `DEFAULT_POLICY` type absent from `CREATION_ACTIONS` |
| FR-353 names seven types | **true** | `docs/specs/06-governance.md:94`, quoted in item 1 |
| PL-1392 names no `deployment_request.created` event and no author resolution for `deployment` | **true** | `grep -n "deployment_request\.\|CREATION_ACTIONS\|FR-353" docs/plans/PL-01392-*.md` prints no such line; Task 5 (`:1224-1307`) writes the request and calls `approvals.submit`, and records only `deployment.created` |
| An `approved` Rating Version can have no compiled bundle | **true** | `submit_for_review` (`backend/src/app/platform/rating_versions.py:250-300` @14c7e805) requires a bundle only inside `_golden_quote_gate`, and only when the algorithm has a Regression Suite (`:551-578`; the no-suite return is `:569`); with no suite it returns `_not_checked(...)` before the `row.bundle is None` refusal |
| Such a version can never be compiled afterwards | **true** | RL-1379 (title): *"a Rating Version compiles only while draft; any other status is refused 409 RATING_VERSION_IMMUTABLE"* |
| A "not compiled" refusal already has a registered code | **true** | `03-rating-engine.md:816`, `/score/compare`: *"409 `BUNDLE_COMPILE_FAILED` when either is not compiled"*; in code, `rating_versions.py:572-578` @14c7e805 (409 `BUNDLE_COMPILE_FAILED`, "Compile before submitting"); in `03`'s catalogue, `03-rating-engine.md:833` |
| A retired Environment's state refusal already exists in the same module | **true** | `_require_not_retired`, `backend/src/app/platform/environments.py:259-267` @14c7e805: 409 `VALIDATION_FAILED`, "Environment is retired"; used for rename (`:238`) and re-retire (`:342`) |
| `VALIDATION_FAILED` is generic, owned by no module | **true** | `backend/src/app/errors.py:382-385`, `_GENERIC_ERROR_CODES` |

## Ruled

### 1. A deployment request's Author: option (a). FR-353 gains an eighth type; option (b) is refused

**The clause ruled on**, `06-governance.md:94`, FR-353's amendment of 2026-09-28, verbatim:

> neither the submitter nor the Author of an artifact version may decide on it — approve, reject or request changes — exactly as R1 bars the submitter.** The **Author** is the actor of the version's **creation Audit Event** (`00` §2.5), one definition for all seven approvable types

and its scope limit, verbatim:

> **Scope limit: the Authors of the components a version pins** — a rate table version's or a model version's creator, reaching approval inside a Rating Version — **are not covered here.** That is the harder maker-checker question and is carried to **WK-677**, this requirement's owner

**Option (b) is refused.** FR-353's text exempts no type: the Author definition is "one
definition for all" approvable types, and the check "fails closed — a version with no
creation Audit Event is refused". Nothing in it permits an approvable type with no Author.
Skipping the check for `deployment` would weaken the requirement, which the GO's condition 1
forbids.

**Option (a) is ruled, as a spec change.** The spec is the side that was incomplete.
RL-1301 A.1 (2026-09-30) made `deployment` an approvable type, with a Deployment Request as
its subject. FR-353's list of seven (2026-09-28) was written before that, and nobody
extended it. The code is correct: it fails closed exactly as FR-353 says. So the code
follows the amended spec, and the code was not wrong.

- **The creation event is `deployment_request.created`.** The deployment module records it
  in the transaction that writes the Deployment Request row and calls `approvals.submit`
  (PL-1392 Task 5, the request route, step 4).
  - Its `entity_ref` is **exactly** the request's reference `deployment:<environment
    slug>@<n>`, the string the approval request's `artifact_ref` holds. `_author_of`
    matches on that equality.
  - Its actor is the submitting Principal.
  - `CREATION_ACTIONS` gains `"deployment": "deployment_request.created"`.
- **Limb (i): the request's submitter may not decide.** For a Deployment Request, the
  Author (the `deployment_request.created` actor) and the submitter (`submitted_by`) are the
  same Principal, because one route call creates and submits. R1 refuses that Principal first
  with `SUBMITTER_CANNOT_APPROVE`, as `decide` orders the checks. The Author check is not
  dropped because it repeats R1: its fail-closed half is what refuses a request with no
  creation event (`APPROVAL_AUTHOR_UNRESOLVED`), for example one planted without the module.
- **Limb (ii): a deployment request is not "on" the Rating Version it deploys.** The clause
  bars the Author "of an artifact version" from deciding "on it": on the approval request's
  own subject. A `deployment` approval request's subject is the Deployment Request
  (`artifact_ref` `deployment:prod@3`; RL-1301 A.1). The Rating Version is not its subject: it
  is **pinned** by the request (RL-1301 A.1, "The row pins the approved Rating Version it
  deploys"). That is the scope limit's case: the Author of a component that a version pins,
  reaching approval inside it. So **FR-353 does not bar the Rating Version's Author from
  deciding its deployment request**. This ruling does not widen FR-353 to bar them either:
  that would be a new control, and the scope limit gives it to WK-677 by name. The
  amendment below says so, so that no reader infers it.
  - **Not a gap in separation of duties.** The Rating Version's content was already decided
    under FR-353 by someone other than its Author and its submitter (its own `rating_version`
    request, pinned as the `rating_version_approval` evidence item). What a Deployment
    Request asks is whether this approved version may go into this Environment now. Its maker
    (the submitter) and its checker (the decider) are distinct Principals.
  - **WK-677's carry now names this case explicitly**, beside the rate-table and model
    component Authors.

### 2. Deploying a Rating Version that was never compiled: refused 409 `BUNDLE_COMPILE_FAILED`, at request and at deploy

**The gap is real and permanent for that version.** An `approved` Rating Version whose
algorithm has no Regression Suite can pass submission with no bundle (premise table). RL-1379
then refuses every later compile. Such a version can never be deployed: a Deployment records
the version's compiled Bundle hash (`03` FR-239; `03` §4.12 @14c7e805, `bundle_hash`), and
there is none.

- **"Compiled"** means the Rating Version's `bundle` metadata is present and carries a
  `content_hash`. The Deployment's `bundle_hash` copies that field.
- **The code is `BUNDLE_COMPILE_FAILED`, 409, which is registered** (`03`'s catalogue,
  `03:833`). `03` §5.1 already uses it for "not compiled" (`/score/compare`, `03:816`), and the
  rating module raises it for "Compile before submitting" (`rating_versions.py:572-578`
  @14c7e805). The name is narrower than the use. `VALIDATION_FAILED`, the executor's
  suggestion, is generic: it would tell a client nothing that it can act on. A new code would
  duplicate one that the spec already defines for this condition. **No new code is
  registered.**
- **Where it is refused:**
  - **at Deployment Request submission**, right after the `approved` check (PL-1392 Task 5,
    the request route, step 2), so that no approver is asked to decide a request that cannot
    execute; and
  - **at the deploy route**, right after its `approved` check (the deploy route, step 3), as
    defence in depth, and for an ungated target, which has no request.
  - The message names the ref and says that the version cannot be compiled now because it is
    not `draft` (RL-1379). A new draft version is the way forward.
- **Which side was wrong:** neither contradicts the other. The plan and `03` §4.12 are both
  silent. `03` §4.12 gains the invariant (below), and the plan's Task 5 gains the steps
  through the delta.

### 3. Deploying to a retired Environment: refused 409 `VALIDATION_FAILED`, at request and at deploy

- **409, not 404.** A retired Environment keeps its row and its slug (`07` §4.2's
  clarification @14c7e805; RL-1301 A.6). It exists, and its state forbids the act. An
  unknown slug stays 404 `NOT_FOUND` (`environments.py` `_load`/`_not_found` @14c7e805).
- **The code is `VALIDATION_FAILED`, the module's existing refusal for this state.** The
  slice's own `_require_not_retired` already refuses a rename or a re-retire of a retired
  Environment with 409 `VALIDATION_FAILED` "Environment is retired" (premise table). The
  deploy refusal reuses that helper, with the verb "deployed to". A dedicated code would make
  the module refuse one state with two codes. The code is generic, so nothing is registered.
  The `detail` names the slug and `retired_at`.
- **Where it is refused:**
  - **at Deployment Request submission**, after the permission check (PL-1392 Task 5, the
    request route, step 1), before the Rating Version is read; and
  - **at the deploy route**, after its permission check (step 2), before the Rating Version
    is read (step 3).
  - The order keeps the plan's rule: authorisation with the Environment as the resource
    (RL-1301 B.2) comes before any state refusal on that Environment.
  - A retired Environment's row still has its id, so the permission check is unchanged.
- **No refusal at `decide`.** An approved request whose target is retired afterwards is
  refused when it is executed, by the deploy-route check. One check at the point of effect is
  enough, and `approvals.decide` stays free of imports from the deployment module (Acceptance
  5).
- **Which side was wrong:** neither. Both are silent. `03` §4.12 gains the invariant, and
  the plan gains the steps through the delta.

## Spec texts, with placement

**All four texts are carried by Slice 2, in Task 5's commit that changes `CREATION_ACTIONS`
and adds the two refusals** — spec, code and tests in one commit (`CLAUDE.md` §2). They are
not edited on main by this record. Three of the four places (`03` §4.12, its Deployment
Request subsection, and the `deployment-requests` row) exist only on the S2 branch. And an
FR-353 that names eight types while main's code holds seven would be a disagreement between
spec and code, on main, until the slice merged. This follows the precedent of RL-1301 A.6 and
RL-1379, whose spec dispositions were carried by the slice.

**T1 — `06` FR-353, appended to the end of its Requirement cell** (`06-governance.md:94`,
after the sentence ending "…is in that record's section of this date.)*"). Nothing is
renumbered. The list of seven is not rewritten.

> *(Amended 2026-10-03, `RL-1401` (WK-674 Slice 2): an eighth approvable type, `deployment`, whose subject is a Deployment Request (`03` §4.12; `RL-1301` A.1). Its creation Audit Event is `deployment_request.created`, recorded by the deployment module in the transaction that writes the request and submits it, with `entity_ref` exactly the request's reference `deployment:<environment slug>@<n>` and the submitting Principal as actor. The Author of a Deployment Request is therefore its submitter, whom R1 refuses first; the fail-closed half is unchanged, so a Deployment Request with no `deployment_request.created` event is refused with `APPROVAL_AUTHOR_UNRESOLVED`. A deployment approval request is on the Deployment Request, not on the Rating Version it pins: the Author of that Rating Version is the Author of a component the request pins, and is within the scope limit above, carried to WK-677 beside the rate-table and model-version Authors, not barred by this clause.)* 

**T2 — `03` §4.12, the "Audit actions this Work emits" bullet** (`03-rating-engine.md:816`
@14c7e805), **replaced whole**. This is the slice's own unmerged text, so it is edited and
not amended:

> - **Audit actions this Work emits**, each named here once so that no later slice appends to the catalogue. **The deployment request:** `deployment_request.created` (WK-674 Slice 2: a Deployment Request is written and submitted; `before` `null`, `after` the request with its pins and its pinned evidence; `entity_ref` exactly the request's reference `deployment:<environment slug>@<n>`; the submitting Principal as actor; in the same transaction as the row and its approval request). Its actor is the request's Author for `06` FR-353, as amended 2026-10-03 (`RL-1401`). **FR-272's four:** `deployment.created` (WK-674 Slice 2: a Deployment row is written, `before` the previous live Deployment of the Environment or `null`, `after` this one, in the same transaction as the row); `deployment.rolled_back` (Slice 5, FR-269); `deployment.routing_changed` and `deployment.shadow_configured` (Slice 6, FR-270 and FR-271). The `entity_ref` of each of FR-272's four names the Deployment or the Environment it changes.

**T3 — `03` §4.12, two invariant bullets inserted directly after "`approved` Rating Versions
only"** (`03-rating-engine.md:814` @14c7e805):

> - **Compiled Rating Versions only** (FR-239; `RL-1401`). A version whose `bundle` metadata is absent, or has no `content_hash`, has no Bundle hash to record and is refused with 409 `BUNDLE_COMPILE_FAILED`, at Deployment Request submission and at deploy. It cannot be compiled once it has left `draft` (`RL-1379`). The way forward is a new draft version.
> - **Not into a retired Environment** (`07` FR-428; `RL-1301` A.6; `RL-1401`). A deploy or a Deployment Request whose target Environment is retired is refused with 409 `VALIDATION_FAILED`, naming the slug and when it was retired. The refusal comes after the permission check and before the Rating Version is read. An unknown slug is 404 `NOT_FOUND`. A request approved before its target was retired is refused when it is executed.

**T4 — `03` §5.1, two rows' Purpose cells, each with a dated parenthetical appended**:

- the `POST` `/api/v1/environments/{env}/deployments` row (`03-rating-engine.md:822`;
  `:863` @14c7e805), after "Deploy an approved version (FR-267)":

  > *(Refusals added 2026-10-03, `RL-1401`: 409 `VALIDATION_FAILED` when the Environment is retired; 409 `BUNDLE_COMPILE_FAILED` when the Rating Version has no compiled bundle; §4.12.)*

- the `POST` `/api/v1/environments/{env}/deployment-requests` row (`:868` @14c7e805), after
  "Submit a deployment request for approval (FR-267, FR-429)":

  > *(Refusals added 2026-10-03, `RL-1401`: 409 `VALIDATION_FAILED` when the Environment is retired; 409 `BUNDLE_COMPILE_FAILED` when the Rating Version has no compiled bundle; §4.12.)*

**Error codes: none is new.** `BUNDLE_COMPILE_FAILED` is `03`'s (`03:833`).
`VALIDATION_FAILED` is generic (`errors.py:382-385`). `APPROVAL_AUTHOR_UNRESOLVED`,
`SUBMITTER_CANNOT_APPROVE` and `AUTHOR_CANNOT_APPROVE` are `06`'s (`06:582-583`). No
catalogue changes.

## Which side was wrong, per item

| Item | Side wrong | Why |
|---|---|---|
| 1. Author resolution | **The spec (`06` FR-353) was incomplete. The plan was silent. The code was right.** | RL-1301 A.1 made `deployment` approvable two days after FR-353 closed its list at seven. The fail-closed code did what FR-353 says. PL-1392 Task 5 writes the request without naming its creation event |
| 2. Uncompiled version | **Neither was wrong. Both were silent** | `03` §4.12 and PL-1392 state the `approved` invariant only. RL-1379 is what makes an uncompiled approved version permanent |
| 3. Retired Environment | **Neither was wrong. Both were silent** | PL-1392 Task 4 refuses rename and re-retire of a retired Environment, and Task 5 has no matching deploy step |

## Findings to file

- **One finding, for the lead to file (LOW; owner WK-673):** *an `approved` Rating Version
  can have no compiled bundle, and under RL-1379 can never get one.* Submission requires a
  bundle only when the algorithm has a Regression Suite (`rating_versions.py:551-578`
  @14c7e805). Such a version is approvable but never deployable. Item 2's refusal makes the
  dead end explicit. It does not remove it.
  - **The proposed owner is WK-673,** whose wiring of `03` FR-257's submission gate
    (`06` FR-364's 2026-08-29 and 2026-09-28 amendments: `regression_run`,
    `dislocation_run`, `structural_diff`) is where a compiled bundle can become a condition of
    submission.
  - This record does not decide that it should.
- **No finding against PL-1392.** Task 5 stopped, as `CLAUDE.md` §0 requires, and the fail-closed
  guard is what found the gap. The parity test in the delta (item 1 (d)) stops the next
  approvable type from repeating it.

## What it obliges

WK-674 Slice 2 builds this in Task 5: texts T1–T4 above, and the code and tests of the
dispatch-record delta below. PL-1392 is frozen and is not edited. The lead's dispatch record
of SL-1256 carries the delta, which is binding on Task 5 once this record is minted:

> **Task 5, per `RL-1401` (minted id substituted).** In the commit that adds the deployment module's submission:
> 1. **Author resolution.** `CREATION_ACTIONS` (`backend/src/app/platform/approvals.py`) gains `"deployment": "deployment_request.created"`. The request route records `audit.record(..., action="deployment_request.created", entity_ref=<the request's reference, the same string passed to approvals.submit as artifact_ref>, before=None, after=<the request with its pins and evidence>)` in the transaction that writes the row and calls `approvals.submit`, with the submitting Principal as actor. Apply T1 (`06` FR-353) and T2 (`03` §4.12) in this commit.
>    - **Red first, each run and quoted:**
>      - (a) the positive control: a Deployment Request approved through `decide` by a Deployer who is neither submitter nor Author. It is red at `14c7e805` with 403 `APPROVAL_AUTHOR_UNRESOLVED`, and green after.
>      - (b) the submitter deciding their own request is refused 403 `SUBMITTER_CANNOT_APPROVE`.
>      - (c) a Deployment Request whose `deployment_request.created` event is deleted by a fixture is refused 403 `APPROVAL_AUTHOR_UNRESOLVED`.
>      - (d) **the parity test**: every `artifact_type` of `DEFAULT_POLICY` and every key of `EVIDENCE_FLOOR` is a key of `CREATION_ACTIONS`. It is red at `14c7e805`, naming `deployment`.
>      - (e) **limb (ii), pinned as ruled**: the Author of the deployed Rating Version, holding the Deployer role, is not refused by the author check on the deployment request. The test's docstring cites `RL-1401` item 1 and WK-677's carry, so a later widening changes it deliberately.
> 2. **Uncompiled version.** The request route (after step 2's `approved` check) and the deploy route (after step 3's `approved` check) refuse a Rating Version whose `bundle` metadata is absent or has no `content_hash`, with 409 `BUNDLE_COMPILE_FAILED`. Red first at both routes, with a version approved through a no-suite submission and never compiled.
> 3. **Retired Environment.** The request route (after step 1's permission check) and the deploy route (after step 2's permission check) call `environments._require_not_retired(row, "deployed to")`, which gives 409 `VALIDATION_FAILED`. Red first at both routes: retire `uat` (it has no live Deployment and no policy entry), then deploy to it, and submit a request into it.
> 4. Apply T3 (`03` §4.12 invariants) and T4 (`03` §5.1 rows) in the commit that adds items 2 and 3.
> 5. No new error code. `errors.py` registers only the `DEPLOY_REQUIRES_APPROVAL` that Task 5 already names.

## Acceptance — the violation that must become detectable

Each case is shown failing on the broken input before the fix, and passing after, in
Slice 2's ledger:

1. **A deployment request approved without an Author check.** With the
   `"deployment"` key removed from `CREATION_ACTIONS`, the positive control (delta item 1 (a))
   is refused 403 `APPROVAL_AUTHOR_UNRESOLVED`. With the key present but the
   `deployment_request.created` event deleted, case 1 (c) is refused the same way. Under
   option (b), case 1 (c) would be approved, and the test fails.
2. **An approvable type with no Author.** The parity test (delta item 1 (d)) fails at
   `14c7e805`, naming `deployment`, and fails again on any future `DEFAULT_POLICY` type or
   `EVIDENCE_FLOOR` key that is added without a `CREATION_ACTIONS` entry.
3. **A deploy that records no Bundle hash.** With the compiled check removed, a never-compiled
   `approved` version is deployed (or its request is submitted), and the test fails. With the
   check present, both routes refuse 409 `BUNDLE_COMPILE_FAILED`.
4. **A deploy into a retired Environment.** With the retired check removed, a deploy to the
   retired `uat` writes a Deployment row, and the test fails. With the check present, both
   routes refuse 409 `VALIDATION_FAILED`, and no Deployment row or audit event is written.
5. **Limb (ii) changed by accident.** Delta item 1 (e) fails if a later change bars the
   Rating Version's Author without amending FR-353 and WK-677's carry.

### Mint-pass note, 2026-10-03 (the maintainer's decision on A1 and A2)

*Dated 2026-10-03, at the mint of `RL-1401`.*
The maintainer accepted limb (ii) ("not barred") and applied two audit advisories, in the entry headed "2026-10-03 23:24:30 BST — RL 9736 (→ RL-1401): A1 and A2 APPLIED as a dated mint-pass note" (`~/gi-pricing-plan.local/channel/to-lead.md`). The ruling body above is not otherwise edited.

- (A1) FR-353's amendment ("neither the submitter nor the Author of an artifact version may decide on it") admits a second reading: a Rating Version is an artifact version, and approving its deployment is a decision about it, so its Author would be barred. This ruling rejects that reading. The object of "decide on it" is the approval request's own subject, here the Deployment Request (RL-1301 A.1: "its own artifact"). The Rating Version's own approval already applied FR-353 to its Author, so barring that Author again at deploy time adds no separation the version's approval lacked.
- (A2) Where this ruling and T1 say the Rating Version's Author "is within the scope limit", read: "is treated by analogy to the scope limit". The limit's words name the Authors of components reaching approval inside a Rating Version. A Rating Version pinned by a Deployment Request has the same shape, but it is not literally named. The question is carried to WK-677 by name.

*Drafted as working id 9736; minted 2026-10-03 as RL-1401.*
