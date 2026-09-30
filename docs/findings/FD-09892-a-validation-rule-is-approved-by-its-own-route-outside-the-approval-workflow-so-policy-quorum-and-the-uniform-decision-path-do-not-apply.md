---
id: FD-9892
family: finding
title: A validation rule is approved by its own route outside the approval workflow, so policy quorum and the uniform decision path do not apply
status: active
created: 2026-09-30
owner: auditor
tree: 65b334792e65704206d2c21015690d7c613092cc
corrected_by: []
relates: [WK-1178]
---

# FD-9892 — A validation rule is approved by its own route outside the approval workflow, so policy quorum and the uniform decision path do not apply

## Finding

**Severity: high**, proposed under the maintainer's severity rule, whose third condition holds
(below); the register row's `decision:` is the lead's. A Validation Rule is a Governed Artifact,
but `POST /api/v1/validation-rules/{rule_id}/approve` (`backend/src/app/api/validation.py:355-`)
calls `approve_rule` (`backend/src/app/platform/validation_rules.py:395-431`), which writes
`APPROVED` and `approved_by` itself (`:423-424`). It never goes through `approvals.submit` and
`approvals.decide`. It is the same class as FD-1200: a second writer of an approval status. What
the direct route enforces is `approval:decide`, the row being in `review`, and the approver not
being the author. What it does not enforce is everything else `06` gives an approval: the
workspace's Approval Policy (approver count, approver roles, evidence), the decision record, and
the uniform request. The maintainer decided this is a **defect** (`to-lead.md` "2026-09-30
11:14:48 BST — DECISION: validation-rule approval outside the workflow is a DEFECT (b); FD,
severity rule, owner; #971's test scope").

## Requirements read

- **`06:64`** lists **Validation Rule** as a Governed Artifact.
- **`06:22`**: *"approved" means the same thing* for a Model, a Custom Objective, a Validation
  Rule and the rest.
- **`06:114`**: a Validation Rule's evidence floor is *"Successful dry-run result against a real
  Dataset Version (`01` FR-50)"*.
- **FR-354** (`06:95`): a per-workspace **Approval Policy** defines, per artifact type, the
  required approver count, permitted approver roles and required evidence.
- **FR-353**: the submitter and the author may not decide.
- **`01` FR-68** (`01-data-management.md:169`): the 38 built-in rules are *"seeded into every
  workspace as approved rules"* (the exemption below).

## Evidence

Measured by **auditor-922** on a real database at `origin/main` `9f63d0fe`; `git diff --stat
9f63d0fe 65b33479 -- backend/src` is empty, so the code is the same at this record's tree
`65b33479`. **Attributed, and not re-run by this record's author.** Each is a real HTTP call in a
scratch test (now deleted); the acting principal held analyst and approver, a second principal
held approver.

| # | Case | Result |
|---|---|---|
| 1 | The author approves their own rule by the direct route | **409** `SUBMITTER_CANNOT_APPROVE`; the rule stays `review` (also the DB check `approved_rule_dry_run_and_separate_approver`, `backend/src/app/db/models.py:1155-1157`; existing test `test_api_datasets.py:603`) |
| 2 | A draft rule (no dry-run, not submitted) approved by another approver; submit with no dry-run | **409** `RULE_NOT_APPROVED`, still `draft`, both. Only the worker writes `dry_run_report_id` (`backend/src/app/worker/data_handlers.py:292-293`). `attach_dry_run` attaches whatever the report outcome; a *failed* dry-run was not tested |
| 3 | Another approver's direct approve; then `PUT /datasets/{slug}/rule-set` with that rule | **200** `approved`, then **200** and the rule set is `approved`. `approval_requests` rows: **0**. An approved rule enters a Rule Set without `approvals.decide`. The validation job loads the set at `data_handlers.py:247`; not run end to end |
| 4 | **Policy bypass.** After `PUT /approval-policy` sets `validation_rule` to `approvers_required=2` (`approver_roles` `[approver, admin]`, evidence `[dry_run_result]`), one approver's direct approve | **200** `approved`. `approve_rule` checks only `approval:decide`, `review` and the author |
| 5 | **The proper workflow, as a control.** `POST /approval-requests` for a rule in review: **201** `review`; the author's `/decide`: **403** `SUBMITTER_CANNOT_APPROVE`; another approver's decide: **200**, the request `approved`, **the rule stays `review`** | `_carry_to_the_artifact` (`api/approvals.py`, about `:500-525`) has no validation-rule branch. Submit for a `draft` rule: **409** `APPROVAL_SUBJECT_NOT_IN_REVIEW`. Missing evidence on the generic path was not tested (the submit body has no evidence field) |

**Reading it against the maintainer's rule** (`to-lead.md`, the 11:14:48 entry): **HIGH** if the
direct route lets the submitter approve their own rule (case 1: **no**, enforced), or approves
without the dry-run evidence (case 2: **no**, enforced), or yields an approved rule that then
runs in a Rule Set without passing `approvals.decide` (case 3: **yes**). **The third condition
holds literally, so HIGH.** **Case 4 is the substantive gap**: a policy that says two approvers
is bypassed by one. Case 5 shows the proper workflow cannot approve a rule at all, since it
records the request and leaves the rule in `review`: the direct route is the **only** way a rule
reaches `approved` today, so the workflow bypass is total.

**Cause, by code reading.** `approve_rule` (`validation_rules.py:395-431`) loads the rule, checks
`approval:decide` (`:400-405`), `row.status != REVIEW` (`:406`, `RULE_NOT_APPROVED`) and
`row.authored_by == actor.id` (`:413`, `SUBMITTER_CANNOT_APPROVE`), then sets `row.status =
APPROVED` and `row.approved_by` (`:423-424`) and records the audit event. The route docstring
(`api/validation.py:359-`) says so: *"Approval policies — quorum, escalation, evidence bundles —
are `06`'s (WK-677). This is the module's own step."* That step is what `06` FR-354 and FR-351
say the uniform machine owns.

## Triage of the two creation-time sites

- **`seed_builtin_rules`** (`validation_rules.py:89-`): **exempt by a spec clause**, `01` FR-68
  (`01-data-management.md:169`, *"seeded into every workspace as approved rules"*) plus the DB
  check's `builtin IS TRUE` arm (`models.py:1155`). Users cannot set `builtin`, `status`,
  `approved_by` or `dry_run_report_id` on create (422 `VALIDATION_FAILED` each, measured).
- **`replace_rule_set`** (`validation_rules.py:538-`; the row is built at `:621`): creates an
  `approved` **Rule Set** (`models.py:1195`, `default="approved"`), but **refuses unapproved
  member rules** (409 `RULE_NOT_APPROVED`, `:585`) and rejects a body `status` (422). So it
  **cannot approve a new user rule with no review**: no hole there. A Rule Set is not a Governed
  Artifact in `06:64`, which lists the Validation Rule.

## Disposition

**Deferred with an owner: a WK-1178 fix slice.** At HIGH it takes the **next free build slot**
after the mispricing fix pair's slice; at MEDIUM it would be in the maintenance queue (the
maintainer's entry above). Event that discharges it: that slice's merge.

**Acceptance, red first:**

- the direct route goes through `approvals.submit` and `approvals.decide`, and **the direct write
  is removed** (`validation_rules.py:423-424`);
- a workspace policy of two approvers is honoured for a rule: **case 4 becomes a refusal**, and
  the proper workflow (case 5) now **moves the rule to `approved`**, through a validation-rule
  decision hook like its four siblings;
- the creation sites stay as triaged above (the built-in exemption is named, not silent);
- **it removes, red first, the temporary `validation_rules` exemption** in #971's (RL working id
  9906) model-derived one-writer check over every approval-status table: the maintainer's
  entry gives that exemption as *one named, dated, temporary exemption ... citing this FD by
  working id*, shrink-only, and this slice removes it.

*Drafted under working id 9892.*
