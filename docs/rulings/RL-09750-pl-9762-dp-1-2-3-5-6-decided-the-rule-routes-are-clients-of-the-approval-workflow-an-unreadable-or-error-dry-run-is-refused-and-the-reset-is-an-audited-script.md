---
id: RL-9750
family: ruling
title: PL 9762 DP-1, DP-2, DP-3, DP-5 and DP-6 decided — the rule routes are clients of the approval workflow, an unreadable or `error` dry-run is refused, the demo seed goes through the workflow, and the unbacked-approval reset is an audited script
status: draft                  # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-01
owner: decision-maker
tree: 49cd25be441382aebc1cc9c9ff325bd73fd81bc1
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FD-1356, RL-1301, RL-1263, FD-1366, FR-48, FR-50, FR-68, FR-351, FR-352, FR-353, FR-354, FR-355, FR-363, FR-386]
---

# RL 9750 (working id) — PL 9762 DP-1, DP-2, DP-3, DP-5 and DP-6 decided: the rule routes are clients of the approval workflow, an unreadable or `error` dry-run is refused, the demo seed goes through the workflow, and the unbacked-approval reset is an audited script

## How this was ruled

**Written 2026-10-01, started 10:49:07 BST, at effort `medium`** (`echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"`
printed `CLAUDE_EFFORT=medium`), by the decision-maker session `dm-1356`, spawned fresh on
the maintainer's entry headed *"2026-10-01 10:47:03 BST — #1063 @1c4e6a2b: the DP-0 record
in the plan text accepted (discharged on the plan's merge); PL 9762's open DPs to a FRESH DM
now, not Saturday, not dm-675dp56"* in the lead's channel (`to-lead.md`), read by this
session.

**Working id 9750**, allocated by the lead, the only allocator. **Working id 9749 was also
reserved and is not used: one record carries all five rulings**, because they interlock
(DP-1's no-request path is DP-6's reset target; DP-3 (iii) and DP-5 both close the same
fabricated `dry_run_report_id`). The plan it rules is **PL 9762** (working id), draft PR
#1063, ruled **against head `1c4e6a2bd0080ce1990d0016785ef2332268570a`**, which the
maintainer's 10:47:03 entry names. Unminted records are cited in working-id form and are
kept out of `relates:` (check 32).

**The questions, as filed** (PL 9762 §"Decision points"): DP-1, the direct approve route
(remove it, or make it a thin client); DP-2, where the approval request is created; DP-3's
open part, (i) a DB CHECK, (ii) the error code, (iii) a dangling or unreadable report id;
DP-5, the demo seed's approved rules; DP-6, how the follow-on-2 reset is applied and
recorded. DP-0 and DP-4 are the maintainer's, decided, and are not reopened here.

**Binding inputs, read by this session** (all in `to-lead.md`):
- *"2026-09-30 11:23:26 BST — DECISION: validation-rule approval bypass: HIGH (not
  CRITICAL); owner and order; two follow-ons"*: the fix's scope, "remove the direct approve
  route (or make it a thin client of the workflow)";
- *"2026-09-30 11:27:20 BST — correction to the failed-dry-run follow-on: the spec means
  EXECUTED successfully; measure the `error` outcome instead"*: `06:114`'s "successful"
  means the run executed; and the reset obligation, "resets non-builtin approved rules
  without an approved approval_request to `review` in the template and fixtures, rather than
  grandfathering them, and records the count";
- *"2026-09-30 11:32:49 BST — three rulings: the error-outcome gap; #971 A.4 method; the
  WK-690 S1 baseline"*, item 1: refused at submit and at approve, one case per cause;
- *"2026-10-01 10:34:13 BST — The DP-S2-6 header for quoting; #1063 DP-0 HELD until
  auditor-1063's provenance check (and the evidence rule if (c)); DP-4 (a) accepted; status
  noted"*: decide's body typed here, its `200` to FD 9752 with a key-set characterisation
  test;
- *"2026-10-01 10:38:52 BST — FD 9752 (#1066 @24933167, the approval request's three
  disagreeing shapes): MEDIUM, owner WK-1178, deadline BEFORE the P2 exit demo, plus a
  consumer hold"*: **the HOLD**, no code that reads any of the four `to_dict` approval-route
  responses until the enum ruling;
- *"2026-10-01 10:39:13 BST — #1063 DP-0 DECIDED: (c) export, then drop, then re-run
  expecting 0; …"*: its finding-2 paragraph, Task 0 judges each rule by its **latest**
  approval event, "so a DP-6 reset plus workflow re-approval is not a false positive".

## Verified first, at `origin/main` `92b4e4ac155536f80a5be183ad21be88cc92868f`

Each locator below was read at that tree in this session (bodies, not names). `origin/main`
moved to `49cd25be441382aebc1cc9c9ff325bd73fd81bc1` (#1058, 11:02:04 BST check) before the
commit; `git diff --stat 92b4e4ac 49cd25be` touches only `docs/INDEX.md`, `docs/roadmap.md`
and the new `PL-1368` file, none of them cited below, so the table holds at both trees. This
branch is cut from `49cd25be`, and the front matter's `tree:` names it.

**Two functions this ruling builds on do not exist at either tree:** `decide_and_carry`
and `open_request_for` are PL 9762's new functions (`git grep -n 'def decide_and_carry\|def open_request_for' 49cd25be -- backend`
prints nothing). Their specification is the plan's (Task 3 Interfaces and Step 5,
`decide_and_carry(session, *, caller, request_id, decision, comment) -> ApprovalRequestRow`;
Step 6, `open_request_for`), which this ruling adopts with DP-1's one change. What they are
built from does exist: `service.decide` and `_carry_to_the_artifact` in one `unit_of_work`
(`api/approvals.py:250-260`). *(Amended 2026-10-01 11:06:58 BST, auditor-1070 F1–F4, adopted by the lead.)*

| What | Where | Read |
|---|---|---|
| The direct approve route | `backend/src/app/api/validation.py:354-380` | `approve_rule(rule_id, caller: DecideApprovals, …) -> ValidationRule`; docstring ends "This is the module's own step, in the terms `01` §4.5 states it." |
| The module submit route | `api/validation.py:335-351` | no request body; calls `rule_service.submit_for_review` |
| The service approve | `backend/src/app/platform/validation_rules.py:403-447` | `RULE_NOT_APPROVED` 409 if not `review` (`:415-421`); `SUBMITTER_CANNOT_APPROVE` **409** for the author (`:422-430`); writes `APPROVED`/`approved_by` inside `approvals.approval_decision(session)` under the comment `ALLOWANCE (PL-1303 Acceptance 7): temporary` (`:431-436`); audit `validation_rule.approved` with no `approval_request_id` |
| The service submit | `validation_rules.py:366-400` | `draft` only; `dry_run_report_id` non-null only; never reads the report; never calls `approvals.submit` |
| The generic resolver | `validation_rules.py:317-349` | selects `status` only, then `approvals.require_in_review` |
| `attach_dry_run` | `validation_rules.py:352-363` | sets `dry_run_report_id` with **no status check** |
| The decide route | `backend/src/app/api/approvals.py:227-270` | body `Decide` (route-local, `:83-87`); `service.decide` then `_carry_to_the_artifact` in one `unit_of_work`; returns `service.to_dict` |
| The carry | `api/approvals.py:488-` | inside `service.approval_decision(session)`: `modelling`, `objectives`, `metrics`, `rating_versions`; **no validation-rule branch** |
| `approvals.submit` | `backend/src/app/platform/approvals.py:225-310` | `VALIDATION_FAILED` 422 on an empty `change_summary` (FR-352); one open request per ref (409); audit `approval_request.submitted` with `justification=change_summary` |
| `require_in_review` | `platform/approvals.py:118-140` | `APPROVAL_SUBJECT_NOT_IN_REVIEW` 409, "Only a version in review can be put to a decision" |
| Separation of duties in `decide` | `platform/approvals.py:359-389` | `SUBMITTER_CANNOT_APPROVE` **403**; `APPROVAL_AUTHOR_UNRESOLVED` 403; `AUTHOR_CANNOT_APPROVE` 403; author from `CREATION_ACTIONS` (`:107-115`, `"validation_rule": "validation_rule.created"`) |
| The approver-role check | `platform/approvals.py:603-623`, called at `:415` | `PERMISSION_DENIED` 403 when the approver holds none of the policy entry's `approver_roles` |
| The default policy | `packages/model-schema/src/model_schema/approvals.py:201-208` | `validation_rule`: `approvers_required=1`, `approver_roles=("approver", "admin")`, `evidence=("dry_run_result",)` |
| The module-submit model | `backend/src/app/platform/objectives.py:558-618` | checks, then `approvals.submit(..., change_summary=...)`, then `REVIEW`, audit `after` carries `approval_request_id`, `justification=change_summary` |
| Sibling submit bodies | `api/custom_objectives.py:128`, `api/custom_metrics.py:109`, `api/peril_structures.py:126`, `api/models.py:720` | all route-local `BaseModel`s, none in `model_schema` |
| `EVIDENCE_INCOMPLETE` | `backend/src/app/errors.py:273`, in `GOVERNANCE_ERROR_CODES` (`:255-`, "owned by `06`"); `06-governance.md:585` | raised 422 by `objectives.py:860`, `metrics.py:812`, `modelling.py:1221`, `rating_versions.py:660`, `perils.py:319`; listed "(re-raised from `06`)" in `03`'s codes (`03:816`) |
| `01`'s owned codes | `docs/specs/01-data-management.md:929-935` | `RULE_NOT_APPROVED` is `01`'s; `EVIDENCE_INCOMPLETE` is absent |
| Check 10 (ownership) | `scripts/audit-docs.py:3895-3920` | a code in two modules' blocks fails unless one is annotated `(re-raised from …)` |
| The report row | `backend/src/app/db/models.py:1027-`, `error_count` `:1057` | immutable report, `error_count` indexed |
| `dry_run_report_id` | `models.py:1170` | `PgUUID`, **no foreign key** |
| The CHECK | `models.py:1201-1205` | `builtin IS TRUE OR status <> 'approved' OR (approved_by IS NOT NULL AND approved_by <> authored_by AND dry_run_report_id IS NOT NULL)`; its comment (`:1196-1200`) calls a `dry_run_report_id` "naming no report" **fabricated evidence**, "a worse governance outcome than naming the exemption" |
| The dry-run job | `api/validation.py:302-330`; `backend/src/app/worker/data_handlers.py:220-296` | stores a real report (`store_report`, `:289`) and attaches it (`attach_dry_run`, `:293-296`); the one-rule set's id is the rule's id (`:241-244`) |
| The demo seed's rules | `examples/fremtpl2/seed.py:395-470` | builds each `ValidationRuleRow` directly `status="approved"`, `approved_by=actuary.id`, **`dry_run_report_id=new_uuid7()`** (`:443`), inside `approval_decision(session)` (`:451-455`); runs **before** any Dataset Version exists (first `ingest` at `:536`); then `replace_rule_set` (`:463`) |
| The seed's model approval | `examples/fremtpl2/model.py:288-308` | `model_service.submit_for_review`, then `approval_service.decide` by `approver`, then `model_service.apply_approval_decision`, **without** `approval_decision()` (the trigger's evidence condition is met by the request `decide` wrote) |
| The seed's principals | `seed.py:311-347` | `analyst` (role `analyst`), `actuary` (`pricing_actuary`), `approver` and `second_approver` (`approver`) |
| `create_rule` | `validation_rules.py:173-` | takes `catalogue_id`, allocates the next version, records `validation_rule.created` |
| `ALLOWANCE_SITES` | `backend/tests/test_approval_guard_static.py:37-46` | `approve_rule`, `replace_rule_set` (temporary); `seed_builtin_rules`, `("examples/fremtpl2/seed.py", "run")` (seed writers) |
| The trigger's rule | `RL-1301` A.4 sub-item 2 | fires only when `NEW.status = 'approved'`; on `validation_rules`, evidence **or** the flag |
| The audit writer | `backend/src/app/platform/audit.py:52-147` | `record(...)` refuses outside a transaction; `pg_advisory_xact_lock` per workspace (`:79-84`); `sequence` = head + 1; `event_hash = compute_event_hash(core, prev_event_hash=…)` computed **in Python** over `AuditEventCore`; `verify_chain` (`:158-`) |
| Migrations and the audit chain | `git grep -l audit_events -- backend/migrations/versions` at this tree | 5 files; `2057e7372a9a` (`:74`) and `82edffbe1dce` (`:40`) only **read** `audit_events`; **no migration writes an Audit Event** |
| A system actor | `backend/src/app/worker/tasks.py:58` | `Principal(kind=ActorKind.SYSTEM, display="worker")`; `JobSource.SYSTEM` exists (`model_schema/jobs.py:93`) |
| A DB-writing script precedent | `scripts/revalidate-artifacts.py:1-40`, `:179` | imports `backend/src`, `DEFAULT_DSN` (`GIP_DATABASE_URL` override), `Database(_settings())` |
| Script-under-test precedent | `backend/tests/test_demo_postconditions.py:22`, `test_lineage.py:601` | `importlib.util.spec_from_file_location` |
| The frontend callers | `frontend/src/api/rules.ts:86` (`submitRule`), `:97` (`approveRule`); `views/RuleSetView.vue:126`; `components/RuleBuilder.vue:111` | no approvals client exists under `frontend/src/api/` |
| `06` FR-351 | `docs/specs/06-governance.md:92` | ends "`peril_structure`, `validation_rule` and `dataset_version` have no decision hook: approving one records the governance decision and does not move the version's row." **This fix makes that false for `validation_rule`** |
| `06` FR-363's table | `06-governance.md:109-`, Validation Rule row `:114` | "Successful dry-run result against a real Dataset Version (`01` FR-50)" |
| `01` §4.5 | `01-data-management.md:470-473`, `:520-523` | step 2 "must execute successfully … and the dry-run result is attached to the approval request"; step 3 "Submitted → `review` → approved by an Approver (never the author)" |
| `01` §5.1 | `01:878-879` (the two rule rows), note `:919-927` | the note ends "This is the module's own step in the module's own terms, which is what §4.5 states." |
| `06` §5.1 | `06-governance.md:540` | `POST /api/v1/approval-requests` |

## Ruled

### DP-1 — option (b), the thin client, with the no-request path named

**Ruling.** `POST /api/v1/validation-rules/{rule_id}/approve` stays and becomes a client of
the decide path. Its handler loads the rule; **refuses a rule not in `review`** with
`RULE_NOT_APPROVED` (409), as it does today; finds the rule's open request with
`open_request_for` and **refuses a rule in `review` with no open request** with
`RULE_NOT_APPROVED` (409), whose detail names the missing request and
`POST /api/v1/approval-requests`; then calls `decide_and_carry(..., decision=APPROVE,
comment=None)`, refreshes the row, and returns `to_schema(row)` (a `ValidationRule`, as
today). It writes nothing itself. It keeps its `DecideApprovals` dependency
(`approval:decide`, the decide route's own permission, `api/approvals.py:63`).

**Options weighed.**
- **(a) remove the route.** Removes the bypass. But the rule-set view would need an
  approvals client that finds the open request and decides it, and **finding the request id
  means reading an approval-route response** (`GET /approval-requests` or the submit's), which
  **the FD 9752 HOLD forbids** until the enum ruling. (a) is therefore not buildable in this
  slice without breaching the HOLD. It also strikes a `01` §5.1 row that #977's Permission-
  column slice is editing.
- **(b) thin client.** Removes the bypass (no write of its own), keeps the one-button flow,
  and reads no approval-route response: `decide_and_carry` returns the `ApprovalRequestRow`, and the
  route returns the typed `ValidationRule`. HOLD-clean.
- **The plan's no-request code, `APPROVAL_SUBJECT_NOT_IN_REVIEW`, is rejected for that
  case.** Its defined meaning (`platform/approvals.py:133-140`) is "only a version in review
  can be put to a decision", and the rule **is** in review. A refusal that names the wrong
  missing thing sends the caller to fix a state that is already right. `RULE_NOT_APPROVED`
  is `01`'s own code for the rule's lifecycle refusals (`validation_rules.py:372-387`,
  `:415-421`), so no new code and no `06` change is needed; the detail carries the
  difference. Keeping `RULE_NOT_APPROVED` for "not in `review`" also keeps that case's wire
  code unchanged.

**The plan's paragraph** ("a rule reset to `review` with no request has no thin-client
path"). **Accepted as a state, with its path named.** The state is not new: every rule
submitted before the fix is in `review` with no request, and DP-6's reset adds more. The
path is `POST /api/v1/approval-requests` with the rule's ref, which the generic resolver
accepts for a rule in `review` whose dry run executed (Step 3 of PL 9762 Task 3, and DP-3
below), and then a decision through either route. A rule whose `dry_run_report_id` is
dangling (every seed-written rule, DP-3 (iii)) is first dry-run again; the dry-run route has
no status check (`api/validation.py:302-330`), so this works from `review`. The reset target
stays `review`, as the maintainer decided in *"2026-09-30 11:27:20 BST — correction to the failed-dry-run follow-on: the spec means EXECUTED successfully; measure the `error` outcome instead"*; this ruling does not move it.

**Wire changes, ruled here.** No maintainer acceptance of them is on record; they are ruled on `06`'s ownership of `SUBMITTER_CANNOT_APPROVE` as a 403 (`platform/approvals.py:361-367`; `06-governance.md:583`), and `01` never states 409 for self-approval (the 409 is the service's, `validation_rules.py:422-430`). (1) Self-approval through the route answers `06`'s
`SUBMITTER_CANNOT_APPROVE` **403** (the author submitted) or `AUTHOR_CANNOT_APPROVE` **403**
(another member submitted), not `SUBMITTER_CANNOT_APPROVE` 409: `decide` owns the separation
of duties. `test_a_rule_walks_draft_to_approved_and_never_by_its_author`
(`backend/tests/test_api_datasets.py:603-676`) changes its expectation from 409 to 403
(PL 9762 Acceptance 11). (2) A rule in `review` with no open request, today approved, is
refused with `RULE_NOT_APPROVED` 409. (3) An approver without a policy role
(`approver`/`admin`) is refused with `PERMISSION_DENIED` 403 (`_check_approver_role`), which
the direct route never checked. (4) An `error` or unreadable dry run is refused with 422
(DP-3).

**What it obliges.** PL 9762 Task 3 Step 6 and Task 4 Step 3 as written for DP-1 (b),
**except** that `open_request_for` raises `RULE_NOT_APPROVED` (409), not
`APPROVAL_SUBJECT_NOT_IN_REVIEW`, and Acceptance 4's no-request case expects
`RULE_NOT_APPROVED`. Task 6 applies **text 1 and text 3** below. The frontend keys its
messages on the code, never the status (Task 5 Step 2).

**Acceptance, red first** (PL 9762 Acceptance 2, 4, 11, with the code above):
- `test_one_approval_under_a_quorum_of_two_leaves_the_rule_in_review`: red on the base tree
  (one call approves).
- `test_the_approve_route_decides_through_the_workflow`: after an approval through the
  route, an `approved` `approval_requests` row and an `approval_decisions` row exist for the
  ref, and the `validation_rule.approved` event carries `after.approval_request_id`; a rule
  in `review` with no request gets 409 with `code == "RULE_NOT_APPROVED"` and a `detail`
  containing `/api/v1/approval-requests`. Red on the base tree (approved with 0 requests).
- `test_the_submitter_and_the_author_cannot_decide`: 403 `SUBMITTER_CANNOT_APPROVE`, then
  403 `AUTHOR_CANNOT_APPROVE`. Red on the base tree (409).
- `test_an_approver_without_a_policy_role_is_refused` (added by this ruling): a member
  holding `approval:decide` but neither `approver` nor `admin` approves through the route and
  gets 403 `PERMISSION_DENIED`; the rule stays `review`. Red on the base tree (200
  `approved`), if the base tree has such a role holder; if no built-in role holds
  `approval:decide` without `approver` or `admin`, the test grants a custom role, and the
  ledger records which.

### DP-2 — option (a): the module submit creates the request, from a typed change summary

**Ruling.** `POST /api/v1/validation-rules/{rule_id}/submit` takes the body
`ValidationRuleSubmission{change_summary: str}` (a `model_schema` type, `frozen`,
`extra="forbid"`, `change_summary` `min_length=1`), and `submit_for_review` calls
`approvals.submit(..., artifact_ref=ArtifactRef(type="validation_rule", slug=row.slug,
version=row.version), change_summary=change_summary)` after its existing refusals and the
DP-3 check, then sets `review`, mirroring `objectives.submit_for_review`
(`platform/objectives.py:558-618`) in order. Its `validation_rule.submitted` event's `after`
gains `approval_request_id`, and its `justification` is the change summary. The frontend
collects a required change summary in `RuleBuilder.vue` and `RuleSetView.vue` and sends the
**generated** type.

**Options weighed.**
- **(a)** makes `01` §4.5 step 2's "the dry-run result is attached to the approval request"
  true for the first time (there is no request today), satisfies `06` FR-352 ("submission
  requires a change summary"), and is the pattern of every sibling module.
- **(b)** (module submit moves to `review` only; the client calls the generic route)
  creates, on every submission, the `review`-with-no-request state DP-1 treats as legacy,
  and makes the request depend on a second client call.
- **(c)** (the summary taken from the rule's `rationale`) reads a statement of why the rule
  exists as a statement of what changed; wrong from version 2 on.
- **The body's home.** Sibling submit bodies are route-local (table above), but every route
  this slice edits takes a `model_schema` body (`FD-1366`'s per-route rule, as the lead's
  holds register applies it, and the brief's typing rule). `ValidationRuleSubmission` follows
  the naming of WK-674 S2's `ApprovalSubmission`/`ApprovalWithdrawal` (the maintainer's
  10:32:26 entry). The route's 2xx stays `ValidationRule`, already a `model_schema` `$ref`.
- **The HOLD.** The frontend reads the submit's `ValidationRule`, not an approval-route
  response. HOLD-clean.

**What it obliges.** PL 9762 Task 3 Step 2, Task 4 Step 2, Task 5, as written for DP-2 (a).
If `scripts/generate-contracts.py` emits a new generated schema artifact for
`ValidationRuleSubmission` (not only an OpenAPI component), the slice follows the procedure
the maintainer's *"2026-10-01 10:43:56 BST — #1065 audit noted; F1 (a new generated schema
needs a _CONTRACT_ARTIFACT_PATHS row and a hard-coded test count bump): …"* entry requires;
if it emits only a component, the ledger says so.

**Acceptance, red first.**
- `test_every_body_this_slice_edits_is_a_model_schema_type` (PL 9762 Acceptance 15): red on
  the submit's absent body.
- `test_the_module_submit_creates_the_request` (added by this ruling): after a submit with
  `{"change_summary": "first cut"}`, exactly one `approval_requests` row exists for the ref,
  `status == "review"`, `change_summary == "first cut"`, `approvers_required` from the
  workspace policy; the `validation_rule.submitted` event's `after.approval_request_id` is
  that row's id. A submit with `{"change_summary": ""}` gets 422 and the rule stays `draft`;
  a submit with no body gets 422. Red on the base tree (0 requests; the empty and absent
  bodies give 200).
- The frontend red of PL 9762 Task 5 Step 1.

### DP-3 — the open part: (i-a) no DB CHECK, (ii-a) `EVIDENCE_INCOMPLETE` 422, (iii-a) a dangling or unreadable report is refused — **ruled in, as scope growth, for the reason below**

The service-layer refusal of an `error` dry run at submit and at approve is FD-1356's, not
this ruling's. This ruling decides only (i)–(iii).

**(i) — option (i-a): no DB CHECK in this slice.** The outcome lives in the immutable
report (`error_count`, `models.py:1057`). A copy on the rule row is a second source of the
same fact that can disagree with it (`CLAUDE.md` §2), and it adds a migration and a column to
a table the approval trigger covers. The service check sits at the three points where a rule
enters review or approval (module submit, generic resolver, carry), and the carry check runs
on the row it holds `FOR UPDATE`. (i-b), the `dry_run_outcome` column and an extended CHECK,
is the stronger guard against a future writer that skips the service; it stays a follow-on
(PL 9762 Hand-off 4), and so does a foreign key on `dry_run_report_id` (below).

**(ii) — option (ii-a): `EVIDENCE_INCOMPLETE`, 422, re-raised from `06`.** It exists and is
`06`'s (`errors.py:273`; `06:585`). It is what five sibling modules raise when FR-363's
evidence is missing (table above), and the dry-run result is FR-363's `dry_run_result`
evidence for a Validation Rule (`06:114`; the default policy). A new `01` code (ii-b) would
be a second name for one condition. `RULE_NOT_APPROVED` stays the code for "no dry run
attached at all" (`validation_rules.py:380-387`), which is unchanged. `01`'s owned-codes list
gains `EVIDENCE_INCOMPLETE` annotated as re-raised (text 2), as `03` does (`03:816`), so check
10 stays green and a reader of `01` §5.1 finds the code its routes return.

**(iii) — option (iii-a): a `dry_run_report_id` that names no `validation_reports` row in the
rule's workspace is refused with `EVIDENCE_INCOMPLETE`, at the same three points.**
**This is scope growth beyond FD-1356**, which names the `error` outcome only. **It is ruled
in**, for three reasons verified at this tree:
1. **The check FD-1356 orders has to read the report, and a read has a missing-report
   branch.** "Each reading the attached report's outcome" (FD-1356 §"Disposition") cannot be
   built without deciding what happens when there is no report to read. Failing open there
   means "no report" passes as "no `error`", the opposite of `06`'s rule that an approval
   that cannot be checked is refused (`APPROVAL_AUTHOR_UNRESOLVED`, `platform/approvals.py:375`).
2. **The case is live, not hypothetical.** `dry_run_report_id` has no foreign key
   (`models.py:1170`), and a sanctioned writer at `main` writes a report id naming no
   report: the demo seed's `dry_run_report_id=new_uuid7()` (`seed.py:443`). The repository's
   own comment at `models.py:1196-1200` calls exactly that "fabricating the evidence … a worse
   governance outcome". Every test fixture that attaches `new_uuid7()` does the same.
3. **It costs one branch, not a mechanism.** The dry-run job always stores a real report
   before attaching it (`data_handlers.py:289-296`), and users cannot set
   `dry_run_report_id` on create (FD-1356 §"Triage", measured 422), so no real path is
   refused. The cost is in the tests: every fixture that attaches `new_uuid7()` stores a real
   report instead (PL 9762 Task 2's `stored_dry_run_report`).

**Considered and not ruled in:** checking that the attached report is **this rule's** dry
run (`report.rule_set_id == row.id`, which the handler sets, `data_handlers.py:241-244`).
No writer attaches another rule's report (`attach_dry_run` is called only by the dry-run
handler with its own rule), so it guards no reachable case today. A foreign key on
`dry_run_report_id`: it would fail on the existing dangling rows without a data fix first,
and does not check the workspace. Both are follow-on options, not this slice.

**What it obliges.** PL 9762 Task 3 Steps 1–4 as written (`_require_executed_dry_run`
with both branches), Acceptance 5, 6, 8 and 9. Task 6 applies **text 2 and text 4**.

**Acceptance, red first.** PL 9762 Acceptance 5, 6, 7 (the `fail` control), 8 and 9, each
red on the base tree by the cause the plan states. Acceptance 9 is **in scope**.

### DP-5 — option (a): the seed walks its rules through the workflow; its allowance entry is removed, red first

**Ruling.** `examples/fremtpl2/seed.py`'s user rules are authored, dry-run, submitted and
decided through the platform's own path, and `("examples/fremtpl2/seed.py", "run")` leaves
`ALLOWANCE_SITES`.

**Options weighed.** (b), a named demo-data exemption, has no spec basis: `01` FR-68
exempts the **built-ins** only, and the seed's own comment says its rules are "workspace
data, not a shipped row … `builtin` stays false, because the approval exemption belongs to
the reviewed definition and not to a workspace's configuration of it" (`seed.py:444-449`).
(b) would also keep a fabricated report id in the demo (DP-3 (iii)) and a second population
every later count must subtract. (a) leaves `seed_builtin_rules` as the only writer of an
approved rule with no request, which is `01` FR-68's exemption, named.

**Two corrections to PL 9762's DP-5 (a) text, verified.**
1. **The decider is the seed's `approver`, not its `actuary`.** The `validation_rule` policy
   entry's `approver_roles` are `("approver", "admin")` (`model_schema/approvals.py:205-208`)
   and `decide` checks them (`platform/approvals.py:415`); the actuary holds
   `pricing_actuary` (`seed.py:345`) and would get 403 `PERMISSION_DENIED`. The seed's model
   approval already uses `approver` (`model.py:297-300`).
2. **The seed has no Dataset Version when it writes its rules** (rules at `:395-470`, first
   `ingest` at `:536`), so a real dry run needs the order changed.

**What it obliges** (PL 9762 Task 7 Step 2, replaced by this):
1. Remove the `ALLOWANCE_SITES` entry; run the two static tests; record the red naming
   exactly `examples/fremtpl2/seed.py::run`.
2. Create each of the seed's rules through `rule_service.create_rule(..., actor=analyst,
   catalogue_id=…)`, so its `validation_rule.created` event exists (FR-353's author check
   reads it; without it `decide` answers `APPROVAL_AUTHOR_UNRESOLVED`). No direct
   `ValidationRuleRow` insert and no hand-recorded event.
3. Ingest the first version before the rule set is bound; dry-run each rule against it with
   the real `DATASET_VALIDATE` job and `dry_run_rule_id` (the payload
   `api/validation.py:319-327` builds), as the analyst; **stop the seed** (`SystemExit`)
   if a job does not succeed or a report has `error_count > 0`, naming the rule.
4. `submit_for_review(..., actor=analyst, change_summary=<a fixed sentence naming the rule
   and the demo>)`; then `approvals.decide(..., approver=approver,
   decision=DecisionKind.APPROVE, comment=…)` and
   `rule_service.apply_approval_decision(...)` in one `unit_of_work`, as `model.py:296-308`
   does for the model. **No `approval_decision()` block:** the request `decide` writes
   satisfies the trigger's evidence condition, as it does for the model.
5. Then `replace_rule_set` and the existing `validate(first)`, unchanged.
6. **Stop and report** if the reorder changes what the seed demonstrates (for example, if
   `ingest` refuses a dataset with no rule set, or if `validate(first)`'s report changes);
   do not work around it.

**Acceptance, red first.**
- The static red of step 1, recorded.
- A seed run against a scratch database (`dev-commands`' DSN form), then FD-1356's
  follow-on script (unchanged) against that database: `user_approved_with_no_approved_request=0`
  and `user_approved` equal to the seed's rule count. Red first: the same run at the base
  tree prints the seed's rule count for `user_approved_with_no_approved_request`. Both lines
  go to the ledger with the database name and the time (BST).
- `git grep -nE '(^|[^_])approval_decision\b' -- examples/` prints nothing (the pattern
  excludes `apply_approval_decision`; at `92b4e4ac` it prints `seed.py:283` and
  `seed.py:453`). The ledger quotes the output.

### DP-6 — option (b): a scoped script that writes one Audit Event per reset row through the one audit writer

**Ruling.** The follow-on-2 reset is `scripts/reset-unbacked-rule-approvals.py`, run by the
executor. It reuses `audit.record` and `Database.unit_of_work()`; no migration is added.

**Options weighed** (the maintainer: "DP-6 (a') is the DM's call (chain lock vs audit
trail)"):
- **(a) a data migration with no Audit Event** is rejected. It withdraws approvals of
  Governed Artifacts and leaves no record in the chain of who, when or why. `06` FR-351 puts
  post-approval states under "the same audit rules", and `CLAUDE.md` §1 makes auditability a
  design priority. A count on stdout is not a governed record.
- **(a') an audited migration** gets the trail, at a cost that is more than the lock. The
  chain's `event_hash` is computed **in Python** over `AuditEventCore`
  (`audit.py:96-118`), under a per-workspace advisory lock and a `sequence` read. A migration
  can get that only by (1) importing `app.platform.audit` into a permanent migration, whose
  behaviour then changes whenever the audit writer changes, across a sync Alembic connection
  and an async writer; or (2) re-implementing the hash, the lock and the sequence in SQL, a
  second writer of the chain format (`CLAUDE.md` §2), where one divergence makes
  `verify_chain` fail the workspace (`AUDIT_CHAIN_BROKEN`). **No migration in the chain writes
  an Audit Event today** (table above), so (a') would set that precedent. And its
  permanence buys nothing: after DP-1 and DP-5 there is no writer of an approved non-built-in
  rule without an approved request, so on every database created after the fix the
  migration is a no-op; its only effect is on the local pre-fix databases a script reaches.
- **(b) a scoped script** gets the same trail **through the existing writer**: one
  `audit.record` per row inside one `unit_of_work`, with the writer's own lock, sequence and
  hash. It matches the maintainer's scope ("in the template and fixtures", *"2026-09-30 11:27:20 BST — correction to the failed-dry-run follow-on: the spec means EXECUTED successfully; measure the `error` outcome instead"*) rather
  than every database that will ever upgrade. Its cost: it is not replayed on a database
  restored from a pre-fix dump. That is acceptable with no production, and it is detectable:
  FD-1356's follow-on predicate and Task 0 are the instruments.

So the choice the maintainer framed dissolves: (b) has the full audit trail, and the chain
lock is handled by the code that already owns it.

**The script, fixed here** (every literal below is the ruling's; executor wording is a stop):
- **Path:** `scripts/reset-unbacked-rule-approvals.py`, written in the style of
  `scripts/revalidate-artifacts.py` (its `sys.path` shim, `DEFAULT_DSN`, the
  `GIP_DATABASE_URL` override, `Database(_settings())`).
- **Population:** exactly FD-1356's follow-on predicate:
  `validation_rules` rows with `status = 'approved'` and `builtin IS NOT TRUE` and no
  `approval_requests` row with the same `workspace_id`, `artifact_type = 'validation_rule'`,
  `artifact_ref = 'validation_rule:' || slug || '@' || version` and `status = 'approved'`.
  Selected `FOR UPDATE`.
- **Per row:** `status = 'review'`, `approved_by = NULL`, then
  `audit.record(session, workspace_id=row.workspace_id, actor=Principal(kind=ActorKind.SYSTEM,
  display="fd-1356-reset"), source=JobSource.SYSTEM, action="validation_rule.approval_reset",
  entity_ref=f"validation_rule:{row.slug}@{row.version}", before={"status": "approved",
  "approved_by": str(row.approved_by)}, after={"status": "review", "approved_by": None},
  justification="FD-1356 follow-on 2: approved outside the approval workflow; no approved
  approval request backs this approval (RL-<minted id> DP-6).")`.
- **One `unit_of_work` per database:** a failure rolls that database back and the script
  exits non-zero.
- **After the writes, in the same run:** `audit.verify_chain` for every workspace it wrote to;
  a broken chain exits non-zero.
- **Output:** one line per database, `<database> reset=<n> workspaces=<m> chain_verified=<m>`.
  No flags: the read-only count is FD-1356's own script.
- **Where it runs:** the database named `gipricing` (the maintainer's "template"), always.
  Scratch databases are **not** written (they are disposable, and a running gate may hold
  one); their counts are recorded, not changed (below).
- **What the reset does not do.** It corrects the governed record; it does **not** stop a
  Rule Set running the rule. A validation run never checks member status, so `01` FR-50's
  run-time clause (`01:112`) is enforced only when a set is written (`replace_rule_set`),
  verified by auditor-1070 (observation (1) below).
- **Target state `review`**, the maintainer's (*"2026-09-30 11:27:20 BST — correction to the failed-dry-run follow-on: the spec means EXECUTED successfully; measure the `error` outcome instead"*). The trigger does not fire on a write
  to `review`, and the CHECK holds for a non-approved row (PL 9762 DP-6 row, verified against
  `RL-1301` A.4 sub-item 2 and `models.py:1201-1205`).

**What it obliges** (PL 9762 Task 7 Steps 3–5 and Acceptance 13, replaced by this; the
write set loses the migration row and gains the script and its test):
1. **Before:** FD-1356's follow-on script, verbatim, over every `gipricing*` database
   (read-only); last two lines and the per-database lines to the ledger, with the time (BST).
2. Run the reset script against `gipricing`; its output to the ledger.
3. **After:** the follow-on script again: `gipricing` prints
   `user_approved_with_no_approved_request=0` and its `builtin_approved` equals step 1's
   figure; every other database's line is unchanged from step 1. Then Task 0's script: its
   last line still reads `TOTAL route_approved=0`.
4. A second run of the reset script prints `reset=0` for `gipricing`.

**Acceptance, red first.** `backend/tests/test_reset_unbacked_rule_approvals.py` loads the
script with `importlib.util.spec_from_file_location` (as `test_demo_postconditions.py:22`
does) and runs its reset function on the test database:
- Setup, in two workspaces: an approved non-built-in rule with no request (A); an approved
  built-in (B); an approved rule with an approved request (C); and in the second workspace
  another rule like A (D).
- Expected: A and D are `review` with `approved_by` NULL, each with exactly one
  `validation_rule.approval_reset` event carrying the `before`/`after` above; B and C are
  unchanged with no new event; `audit.verify_chain` passes for both workspaces; a second run
  resets 0 and writes 0 events.
- **Red first, on broken input, both recorded:** (1) with the `NOT EXISTS` clause removed in
  a scratch edit, C is reset and the test fails naming it; (2) with the `audit.record` call
  removed in a scratch edit, the event assertion fails. Each edit is reverted.

## The spec texts

Four texts. Task 6 of PL 9762 applies them **in one commit with the code** (`CLAUDE.md` §2),
following `spec-change`, then runs `python3 scripts/audit-docs.py`. The placeholders are
`<Task 6 date>`, the date of that commit, and `RL-<minted id>`, this ruling's minted id.
Every other character is fixed.

**Text 1** — placement: `docs/specs/01-data-management.md` §5.1, inside the blockquote note
that begins ``> **`POST /validation-rules/{id}/approve` added 2026-08-15 (WK-663).**``
(`01:919` at `92b4e4ac`). Inserted **after** its last line, the one ending
`which is what §4.5 states.` (`01:927`), as two new lines: a line holding only `>`, then the
paragraph below as one line. The note's existing lines and the §5.1 table are unchanged.

```text
> **Amended <Task 6 date>, `RL-<minted id>` DP-1, DP-2 and DP-3 (WK-1178, the `FD-1356` fix).** The last sentence above is superseded: the approve route is no longer the module's own step. It is a client of `06`'s decision path. It finds the rule's open approval request and records an `approve` decision on it, as `POST /api/v1/approval-requests/{id}/decide` does, so the workspace's Approval Policy (`06` FR-354: approver count, approver roles, evidence) and the separation of duties (`06` FR-353) apply, and the rule reaches `approved` only when its request does (`06` FR-355). A self-approval is refused with `06`'s `SUBMITTER_CANNOT_APPROVE` or `AUTHOR_CANNOT_APPROVE` (`403`), no longer `409`. A rule not in `review`, and a rule in `review` with no open approval request, are each refused with `RULE_NOT_APPROVED` (`409`); the second is put to a decision by submitting a request through `POST /api/v1/approval-requests` (`06` §5.1). `POST /validation-rules/{id}/submit` creates the request (§4.5 steps 2 and 3), and its body carries the change summary `06` FR-352 requires. Both submission routes and both approval routes refuse a rule whose attached dry-run report cannot be read in the workspace, or records an `error` outcome, with `06`'s `EVIDENCE_INCOMPLETE` (`422`): §4.5 step 2 requires a dry run that executed. A `fail` outcome is a run that executed, and is accepted.
```

**Text 2** — placement: `docs/specs/01-data-management.md`, the `**Error codes owned by this
module:**` paragraph (`01:929-935`). Its last line, `` `REJECT_RATE_EXCEEDED`, `DERIVATION_NOT_MATERIALISED`. ``
(`01:935`), is replaced by the line below. No other line changes.

```text
`REJECT_RATE_EXCEEDED`, `DERIVATION_NOT_MATERIALISED`, `EVIDENCE_INCOMPLETE` (re-raised from `06`).
```

**Text 3** — placement: `docs/specs/06-governance.md`, the `FR-351` row (`06:92`). Appended
at the **end of the row's second cell**, after the cell's current last character and one
space, before the closing ` |`. Nothing in the cell is struck or reworded; if WK-674 Slice 2
has appended to the cell first, this text goes after S2's.

```text
**Amended <Task 6 date>, `RL-<minted id>` DP-1 (WK-1178, the `FD-1356` fix):** `validation_rule` now has a decision hook. A decision on a validation rule's request moves the rule as FR-355 says: `approved` on approval, and `draft` on a rejection, a request for changes or a withdrawal. Before it writes `approved`, the hook refuses a rule whose attached dry-run report cannot be read in the workspace, or records an `error` outcome, with `EVIDENCE_INCOMPLETE` (FR-363). The sentence of this requirement that names the types with no decision hook now holds for `peril_structure` and `dataset_version` only. `01`'s `POST /validation-rules/{id}/approve` records its decision through this path and moves nothing itself.
```

**Text 4** — placement: `docs/specs/06-governance.md`, FR-363's evidence table, the
`**Validation Rule**` row (`06:114`). Appended at the **end of the row's second cell**, after
`` (`01` FR-50) `` and one space, before the closing ` |`.

```text
*(Clarified <Task 6 date>, `RL-<minted id>` DP-3, on the maintainer's reading of `01` §4.5 step 2 of 2026-09-30: "successful" means the dry run executed. Its report can be read in the workspace and records no `error` outcome. A `fail` outcome is a run that executed and caught rows, and is accepted. A refusal is `EVIDENCE_INCOMPLETE`.)*
```

The executor applies each text above byte-for-byte; authorship stays with the decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296 precedent). Any executor wording is a stop.

## Acceptance — the violation that must become detectable

Per DP above, each red first on the base tree by its stated cause, plus, for the texts:
- `git diff <base>..HEAD -- docs/specs/01-data-management.md docs/specs/06-governance.md`
  shows exactly: two added lines after `01:927` (text 1), one replaced line at `01:935`
  (text 2), and one appended run at the end of each of the `FR-351` and Validation Rule rows
  (texts 3 and 4); every earlier character of those rows is byte-identical.
- `python3 scripts/audit-docs.py` exits 0 on the slice's tree (check 10 included: text 2's
  annotation keeps ownership exclusive).

## What it obliges

- **PL 9762**: where the plan and this ruling differ (DP-1's no-request code; DP-5's decider
  and order; DP-6's script in place of the migration, Task 7 Steps 3–5 and Acceptance 13; the
  three tests this ruling adds), **the ruling wins**. The planner aligns the plan before its
  first merge, or the dispatch record names each difference.
- **Task 6** applies texts 1–4 with the code, in one commit.
- **The HOLD (FD 9752)**: no ruling here needs code that reads any of the four `to_dict`
  approval-route responses. `decide_and_carry` returns the `ApprovalRequestRow`; the rule routes return
  `ValidationRule`; the seed and the reset script call services. Decide's `200` stays untyped
  and owned by FD 9752, with `test_the_decide_response_keeps_its_key_set` (DP-4, PL 9762
  Acceptance 15).
- **Every route this slice edits** takes a `model_schema` request body
  (`ValidationRuleSubmission`; `Decide`, moved under DP-4); the thin-client approve route
  takes no body, as today.

## Spec changes in this commit

**None.** Texts 1–4 are recorded here and applied by the slice (PL 9762 Task 6), because the
code they describe does not exist until then.

## Observed, not ruled (for the lead)

- **A Rule Set keeps running a rule that is no longer `approved`.** Neither the validation
  handler nor `platform/validation.py` checks member status at run time (a `git grep` for
  `APPROVED`/`"approved"` in both prints nothing at `92b4e4ac`); `01` FR-50 ("only `approved`
  rules may run in a Rule Set …") is enforced only when the set is written
  (`replace_rule_set`, `RULE_NOT_APPROVED`). After DP-6's reset, the `gipricing` database's
  approved Rule Sets will hold `review` members that still run. A possible finding; not this
  slice's.
- **`attach_dry_run` has no status check** (`validation_rules.py:352-363`; the dry-run route
  `api/validation.py:302-330` has none either), so a rule's evidence can be replaced while it
  is in `review` or after it is `approved` (`01` §4.5 step 4 calls an approved rule
  immutable). DP-1's legacy path relies on it from `review`; whether it should be refused
  after approval is a question for the lead, not ruled here.
- **The `skipped`-only dry run** (PL 9762 §"Decision points", the observed paragraph) is
  unchanged by this ruling: the refusal reads `error` only, as FD-1356 says.
- **Working id 9749** is not used; the lead may release it.
