---
id: RL-9733
family: ruling
title: WK-674 Slice 2 Task 5 flags D1 to D5 decided — the Deployment history reads under rating:read and that row says so; a gated Environment with no predecessor refuses every request 422 EVIDENCE_INCOMPLETE, naming the remedy; a request reference named for an ungated target is refused 422 VALIDATION_FAILED; FR-355 gains a dated amendment and a request for changes ends a Deployment Request rejected; RL-1401's retired-before-execution sentence stands and is tested through the routes
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-04              # the mint date (check 31); ruled 2026-10-04
owner: decision-maker
tree: 7e2ee2ba57800e39cbd2f4df1a9fc3402625cd8a
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1392, SL-1256, RL-1401, RL-1301, RL-1296, RL-1379, FR-355, FR-351, FR-353, FR-356, FR-364, FR-267, FR-382, FR-428, FR-429]
---

# RL 9733 (working id) — WK-674 Slice 2 Task 5 flags D1 to D5 decided

## How this was ruled

- **Filed under working id 9733, allocated by the lead.** The id is renumbered at the mint
  turn (`python3 scripts/doc-id.py next --ref origin/main`); until then `audit-docs.py`
  check 31 reds this file by design. The frontmatter `id` field and the file name carry the
  hyphenated form only because the tooling parses them; the text names this record RL 9733,
  and every spec text below writes `<RL id>`, which reads as the minted id.
- **Mandate:** the lead's GO in `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed
  "2026-10-04 12:46:00 BST — GO: dm-674 (opus/medium, WK-674's DM for 4 Oct) rules D1–D5 in
  ONE record (working id from you); …", verbatim in the part that binds this record:

  > - **D4 (spec vs code, CLAUDE.md §0):** decide which side is wrong. Either 06 FR-355 gains a dated amendment for artifacts with no pre-submission state (a Deployment Request), or the code changes. Quote FR-355 in full, including its dated amendments, and name the consequence for any other approvable type without a pre-submission state.
  > - **D1:** the history route's permission. Read it against 06's catalogue rows and my settings:read decision ("2026-10-03 23:10:17 BST — DECIDED (a): GET /api/v1/environments requires settings:read …"); reuse an existing permission where its row covers the read, and amend that row's text if needed.
  > - **D2/D3:** the refusal codes. Reuse registered codes; VALIDATION_FAILED is generic.
  > - **D5:** if RL-1401 T3's last sentence is untestable through the routes, test it at the service layer (name the test), or rule a narrowed sentence with which side was wrong. Do not drop it silently.
  > - Exact texts and placement throughout, which side was wrong per item, and nothing beyond D1–D5.

- **The questions** are the lead's, in `~/gi-pricing-plan.local/channel/from-lead-2026-10-04.md`,
  the entry headed "2026-10-04 12:45:37 BST — Lane A: Task 5 DONE at 2ef9f675 (targeted); …",
  item "To a decision-maker", restating flags 1–4 of the Task 5 section of
  the slice ledger LG 9737 (working id; its file is under `docs/ledgers/` on the S2 branch) at
  `2ef9f675f9eaddd3d078e167df783e58bbe222a6` (`:452-467`, "Deviations and flags, stated") and its
  T3 note (`:492-495`).
- **Evidence read**, all at `2ef9f675` unless named: `backend/src/app/platform/deployments.py`
  (`submit_request` `:206-327`, `apply_approval_decision` `:375-433`, `deploy` `:436-…`,
  `_executable_request` `:572-606`); `backend/src/app/api/deployments.py:39`
  (`ReadHistoryDep = … requires(Permission.RATING_READ)`); `backend/src/app/platform/environments.py`
  (`retire_environment`, `_blockers`); `packages/model-schema/src/model_schema/permissions.py`
  (`READ_PERMISSIONS` `:79-88`, `_analyst` `:108-122`, `BUILTIN_ROLES` `:134-145`);
  `packages/model-schema/src/model_schema/deployments.py` (`EnvironmentUpdate` `:87-96`,
  `DeploymentRequestStatus` `:136-145`); `model_schema/approvals.py`
  (`promotion_order_refusal` `:247-277`); `backend/src/app/errors.py` (`PROMOTION_ORDER_VIOLATION`
  `:70`, `EVIDENCE_INCOMPLETE` `:273`, `DEPLOY_REQUIRES_APPROVAL` `:313`, `_GENERIC_ERROR_CODES`
  `:386-388`); `backend/tests/test_deployments.py`. Specs at `origin/main` `7e2ee2ba`, and the
  slice's own §4.12 text at `2ef9f675`. The dispatch record
  `~/gi-pricing-plan.local/handover/DISPATCH-WK-674-SL1256-2026-10-03.md`, Deltas 5–7 (`:201-215`).
  `06` FR-355 and the `rating:read` row are byte-identical at `7e2ee2ba` and `2ef9f675`
  (checked by `diff`).

## Ruled

### D1. The Deployment history route reads under `rating:read`; that row is amended to say so. The code was right; the spec was silent

**Decision.** `GET /api/v1/environments/{env}/deployments` stays on `rating:read`, the
executor's pick. `06`'s `rating:read` catalogue row gains the route.

**Why this row and not another.** Four catalogue rows were candidates (`06-governance.md`
permission catalogue, `:269-294` at `7e2ee2ba`):

- `rating:read` — *"Reading Rating Algorithms, Sub-graphs, Regression Suites, Rate Tables, Rating
  Versions and scoring traces"*. A Deployment is `03`'s record (§4.12, on the slice), it binds a
  Rating Version to an Environment, and its route is in `03` §5.1. Scoring traces, which this row
  already governs, are the nearest sibling: both say which Rating Version priced where.
- `settings:read` — the lead's decision of 2026-10-03 23:10:17 BST (Delta 6) gives it **the
  Environment's own record**: "listing and reading Environments (`07` FR-428, FR-431;
  `GET /api/v1/environments`)". The line this ruling draws is the one Delta 6 already drew: an
  Environment, with its derived `live_deployments` projection (`07` §4.2), is `07`'s
  configuration and `settings:read`'s; the Deployment rows the projection is derived from are
  `03`'s and `rating:read`'s. Moving the history under `settings:read` would make one rating
  record family readable under a settings permission.
- `audit:read` — *"Reading the audit log"*. `06` FR-382 reads the history, but a Deployment is
  not an Audit Event (`deployment.created` is, and stays under `audit:read`).
- `deployment:promote` — a write permission; a read under it would deny an Auditor the history
  FR-382 assembles.

Every built-in role holds both `rating:read` and `settings:read` (`READ_PERMISSIONS`,
`permissions.py:79-88`; `_analyst`, `:108-122`), so the choice changes no built-in role's
access. It matters for an FR-344 custom role, which is why the row must say it.

**Which side was wrong:** the spec, by silence. PL-1392's route table (`:788`) names the route
and no permission, and no catalogue row named the read.

### D2. A gated Environment with no predecessor refuses every Deployment Request 422 `EVIDENCE_INCOMPLETE`, and the refusal names the remedy. The code's refusal was right; its detail and the spec were short

**Decision.** The refusal at `submit_request` (`deployments.py:268-279`) stands, with its
registered code `EVIDENCE_INCOMPLETE` (`errors.py:273`) and status 422. Its detail gains the
remedy. No new code.

**Why.** A target with `requires_prior_environment` `null` satisfies `07` FR-429's predicate
vacuously (`promotion_order_refusal`, `approvals.py:264`: `if predecessor is None or predecessor_deployed: return
None`), but the `deployment` floor's `uat_deployment` item (`06` FR-364; §4.2's restatement
"`deployment` — `rating_version_approval` and `uat_deployment`") has nothing to pin: neither a
predecessor Deployment nor a `PromotionSkip`, which must name a predecessor. FR-364 forbids
removing a floor kind and fails closed on a kind it cannot verify (R4); `07` FR-429 names
`EVIDENCE_INCOMPLETE` as the submission's refusal. So the code is right to refuse, and right in
its code. What it lacks is a way forward: `requires_prior_environment` cannot be changed after
creation (`EnvironmentUpdate` admits `name` and `description` only, `deployments.py:87-96` in
`model-schema`), so the only remedy is removing the policy's `deployment` entry for that
Environment, which makes it ungated (`RL-1301` A.5). The detail must say so, or the refusal is
an error nobody can act on (the objection FR-364 itself answers with mechanism (i)).

**Not ruled here** (beyond D2): whether `PUT /api/v1/approval-policy` should refuse, at save, a
`deployment` entry naming an Environment with no predecessor. That is a new refusal on another
route; it is the lead's to route if wanted.

**Which side was wrong:** the spec, by silence (§4.12 does not name the case), and the code's
detail, which names the fact and not the remedy.

### D3. A `deployment_request_ref` named for an ungated target is refused 422 `VALIDATION_FAILED`. The code was right; the spec was silent

**Decision.** The refusal at `deploy` (`deployments.py:463-471`) stands: 422, the generic
`VALIDATION_FAILED` (`errors.py:386-388`). No new code.

**Why.** Ignoring the reference would accept a body that names a Deployment Request the
Deployment did not execute; the row would carry `deployment_request_ref` `null` while the
caller believed it had executed the request. Refusing keeps the record and the request's
`approved` state honest. The status matches the sibling refusal on the other route: a
Deployment Request submitted into an ungated target is refused 422 `VALIDATION_FAILED`
(`submit_request`, `deployments.py:232-240`; tested at `test_deployments.py:742-760`). Neither
`DEPLOY_REQUIRES_APPROVAL` (the target needs no approval) nor `PROMOTION_ORDER_VIOLATION` (the
order is not the fault) describes it.

**Which side was wrong:** the spec, by silence. The existing test (`test_deployments.py:736-737`)
asserts only the status; the delta below completes it.

### D4. `06` FR-355 gains a dated amendment: a request for changes ends a Deployment Request `rejected`. The spec was the side that was wrong

**FR-355, in full at `origin/main` `7e2ee2ba` (`06-governance.md:96`), with its two dated
amendments:**

> | **FR-355** | `changes_requested` returns the artifact to **its pre-submission state** and requires a comment. The request and the subsequent resubmission are both audited, so a reviewer's concerns and their resolution are traceable. *(Amended 2026-08-17, WK-661. This said `draft`, and for a Model that is wrong: `02` uses `draft` for a specification reserved but not yet fitted, and `02` R2 makes a fitted model's coefficients immutable — so a model returned from review cannot un-fit, and `draft` would describe an artifact with numbers as one without. A Model returns to `fitted`; `rejected` and `withdrawn` return it there too. For artifact types whose pre-submission state **is** `draft`, nothing changes. **Extended 2026-08-18, WK-661: a Custom Objective returns to `certified`**, for the same reason and with a sharper edge — a certificate is pinned to the objective version (`02` FR-146), the version did not change when an approver asked for one, and returning it to `draft` would discard evidence that is still valid and make re-certification the price of a comment.)* |

**Decision: the spec moves, the code stands** (`apply_approval_decision`,
`deployments.py:404-411`: `ApprovalStatus.CHANGES_REQUESTED: DeploymentRequestStatus.REJECTED`).

**Why the spec is wrong, not the code.** FR-355 presumes every approvable subject exists
before it is submitted. For the seven types it was written over, that is true: the generic
`POST /approval-requests` resolves an existing subject (FR-386) in its reviewable state
(FR-351). A Deployment Request is different in kind: `submit_request` writes the row in
`review` and submits it in one transaction (`RL-1301` A; `03` §4.12 "Submission"), and its
evidence is written once and never updated (FR-356, `RL-1301` A.4). There is no earlier state
to return to, and nothing a resubmission could change: a re-pinned predecessor item or approval
is a new request. Changing the code to "return" the row would mean inventing a state and a
resubmission route that would have to re-pin evidence FR-356 makes immutable — a new capability,
not a fix. `DeploymentRequestStatus` does list `draft` (from PL-1392 Task 3's column list, and
the migration's check constraint), but no path writes it, so it is not a pre-submission state
the row ever holds. Whether that unwritten member stays is not ruled here.

**The consequence for every other approvable type: none.** The eight types are `06` FR-353's as
amended by `RL-1401` T1. Each of the other seven has a subject that exists before submission:
`rating_version` returns to `draft`, `model` to `fitted`, `custom_objective` and
`custom_metric` to `certified` (their decision hooks at `2ef9f675`: `rating_versions.py:383`,
`modelling.py:1387`, `objectives.py:874`, `metrics.py:826`); `peril_structure`,
`validation_rule` and `dataset_version` have no decision hook and their rows are not moved
(FR-351's 2026-09-28 clause). **`deployment` is the only approvable type without a
pre-submission state.** A type added later whose subject is created by its own submission states
its `changes_requested` outcome in the commit that adds it (the amendment's last sentence).

### D5. RL-1401 T3's last sentence stands unnarrowed and is tested through the routes. Neither spec nor code was wrong; the ledger's "cannot be built" was

**Decision.** "A request approved before its target was retired is refused when it is executed"
stays as written. It is testable through the routes, so no service-layer test and no narrowing.

**Why the ledger's claim fails.** The ledger (`:492-495` at `2ef9f675`) reasons that retiring an
Environment a policy entry names is refused, and without the entry the target takes no request.
Both premises are true, but the sequence it missed is the one a workspace would actually run:
approve the request while the entry exists, **then** remove the entry with
`PUT /api/v1/approval-policy`, **then** retire the Environment (`_blockers` now finds no entry,
no live Deployment and no key), **then** execute. The deploy route runs the retired check in
`_authorised_environment` (`deployments.py:77-92`), after the permission and before the request
or the version is read, so the approved request is refused 409 `VALIDATION_FAILED`. That is the
sentence's case exactly, reached only through routes. `prod` is not the fixture: `_blockers`
scans every workspace's stored policy and `DEFAULT_POLICY` for workspaces with none, so the test
uses a fresh Environment as item 3's test already does (`_retired_environment`,
`test_deployments.py:960`).

**Which side was wrong:** neither the spec nor the code; the evidence gap was the ledger's.

## Spec texts, with placement

**All four texts are carried by Slice 2, in the commit that adds the delta's tests** — spec,
code and tests in one commit (`CLAUDE.md` §2). They are not edited on `main` by this record:
S1–S3's targets and D4's cross-reference (`03` §4.12) exist only on the S2 branch, as
`RL-1401`'s texts did. `<RL id>` reads as this record's minted id.

**S1 (D1) — `06` permission catalogue, the `rating:read` row, its Governs cell replaced**
(`06-governance.md:278` at `7e2ee2ba`; `:280` at `2ef9f675`). The Check owner cell stays empty.
The row, verbatim:

    > | `rating:read` | Reading Rating Algorithms, Sub-graphs, Regression Suites, Rate Tables, Rating Versions and scoring traces, and an Environment's Deployment history (`03` §4.12; `GET /api/v1/environments/{env}/deployments`, WK-674 Slice 2). *(Amended 2026-10-04, `<RL id>`: a Deployment is a rating record; the Environment's own record is `settings:read`'s.)* |  |

**S2 (D2) — `03` §4.12, Deployment Request subsection, the "Two pinned evidence items" bullet**
(`03-rating-engine.md:865` at `2ef9f675`), this sentence appended at the end of the bullet:

    **A gated target with no predecessor** — an Environment whose `requires_prior_environment` is `null` and which a `deployment` entry names — has no predecessor item to pin, so every Deployment Request into it is refused with 422 `EVIDENCE_INCOMPLETE` (`07` FR-429; `06` FR-364: the floor kind is never removed). The refusal names the remedy: remove the entry, which makes the target ungated (`RL-1301` A.5), because `requires_prior_environment` cannot be changed after creation. *(Added 2026-10-04, `<RL id>`.)*

**S3 (D3) — `03` §4.12, Deployment Request subsection, the "The deploy route executes only an
approved request" bullet** (`03-rating-engine.md:866` at `2ef9f675`), appended after "…and no
skip is possible (`RL-1301` A.5).":

    A deploy into such a target that names a `deployment_request_ref` is refused with 422 `VALIDATION_FAILED`, naming the Environment, and writes nothing: the Deployment would otherwise record a request it did not execute. *(Added 2026-10-04, `<RL id>`.)*

**S4 (D4) — `06` FR-355, appended to the end of its Requirement cell** (`06-governance.md:96` at
`7e2ee2ba` and at `2ef9f675`), after "…make re-certification the price of a comment.)*".
Nothing is renumbered and the existing text is not reworded:

    *(Amended 2026-10-04, `<RL id>` (WK-674 Slice 2): **a subject created by its own submission has no pre-submission state, and a request for changes ends it `rejected`.** A Deployment Request (`03` §4.12; `RL-1301` A.1) is written in `review` by the transaction that submits it, and its evidence is pinned once (FR-356), so there is no state to return it to and nothing a resubmission could change. A request for changes on a `deployment` approval request therefore ends the Deployment Request `rejected`, as a rejection does, and the way forward is a new Deployment Request, which pins its evidence afresh. The comment is still required. The reviewer's concern stays traceable through the decision's Audit Event; its resolution is the new request for the same Rating Version and Environment. Every other approvable type's subject exists before its submission (FR-351, FR-386) and is unaffected. An approvable type added later whose subject is created by its own submission states its `changes_requested` outcome in the commit that adds it.)*

**Error codes: none is new.** `EVIDENCE_INCOMPLETE` is `06`'s (`errors.py:273`);
`VALIDATION_FAILED` is generic (`errors.py:386-388`). No catalogue changes.

## Which side was wrong, per item

| Item | Spec | Code | Disposition |
|---|---|---|---|
| D1 | wrong by silence | right | S1 |
| D2 | wrong by silence | refusal right; detail short | S2; detail names the remedy |
| D3 | wrong by silence | right | S3; test completed |
| D4 | **wrong** (FR-355 presumes a pre-existing subject) | right | S4 |
| D5 | right | right | the ledger's "cannot be built" was wrong; route test |

## What it obliges

WK-674 Slice 2 builds this. PL-1392 is frozen and is not edited. The lead's dispatch record of
SL-1256 carries the delta, binding on the executor once this record is minted:

> **Delta (RL 9733, minted id substituted): Task 5's flags D1–D5.** In one commit, red first on each test, every red quoted in LG 9737 with the broken input named. The FD 9752 hold stands: no test reads an approval response's decision values; a Deployment Request's state is read from its row.
> 1. **D1.** Apply S1. No code change (`api/deployments.py:39` stays `Permission.RATING_READ`).
> 2. **D2.** The `submit_request` detail for the no-predecessor case names the remedy (remove the `deployment` policy entry for the slug; `requires_prior_environment` cannot change). Test `test_a_gated_environment_with_no_predecessor_refuses_every_request_naming_the_remedy`: create a fresh Environment with `requires_prior_environment` `null`, add a `deployment` entry for it through `PUT /api/v1/approval-policy`, submit a request for an approved, compiled version into it → 422, `code == "EVIDENCE_INCOMPLETE"`, detail names the slug and the entry's removal, no `deployment_requests` row. Red at `2ef9f675` on the detail assertion. Apply S2.
> 3. **D3.** Complete `test_a_request_for_another_version_or_environment_does_not_authorise_a_deploy` (`test_deployments.py:736-737`): the ungated deploy also asserts `code == "VALIDATION_FAILED"`, no new Deployment row in `uat`'s history, and the request still `approved`. Broken-input proof: with the `entry is None and body.deployment_request_ref is not None` refusal removed, the test fails. Apply S3.
> 4. **D4.** Test `test_a_request_for_changes_ends_a_deployment_request_rejected`: a Deployer requests changes with a comment → the `deployment_requests` row is `rejected` and a `deployment_request.rejected` Audit Event is written; a deploy naming it is refused 409 `DEPLOY_REQUIRES_APPROVAL`; a new request for the same version into the same Environment is accepted as the next `@n`. Broken-input proof: with the `CHANGES_REQUESTED` entry removed from `apply_approval_decision`'s map, the row stays `review` and the test fails. Apply S4.
> 5. **D5.** Test `test_a_request_approved_before_its_target_was_retired_is_refused_at_execution`: a fresh Environment with `requires_prior_environment` `uat` and a `deployment` policy entry; the version deployed to `uat`; a request submitted and approved; the entry removed through `PUT /api/v1/approval-policy`; the Environment retired through its route; then (i) a deploy naming the approved request and (ii) a deploy naming none are each refused 409 `VALIDATION_FAILED` naming the retirement; no Deployment row; the request still `approved`. Broken-input proof: with `_require_not_retired` removed from `_authorised_environment`, (i) is refused 422 by D3's check, not 409, and (ii) writes a Deployment; the test fails on both. The docstring cites `RL-1401` T3 and this record's D5.
> 6. No new error code. No other file in the write set beyond `deployments.py`, `test_deployments.py`, `06-governance.md` and `03-rating-engine.md`.

## Acceptance — the violation that must become detectable

1. **A permission catalogue that does not name a route's read.** S1 makes the `rating:read` row
   name the history route; a later move of the route to another permission contradicts the row.
2. **A gated first Environment that refuses with no way forward.** D2's test fails on a detail
   that does not name the entry's removal.
3. **A request reference silently ignored.** D3's completed test fails when the refusal is
   removed.
4. **A Deployment Request left in `review` after a request for changes.** D4's test fails.
5. **A request executed into a retired Environment.** D5's test fails with the retired check
   removed.

*Drafted as working id 9733; minted at the lead's mint turn.*
