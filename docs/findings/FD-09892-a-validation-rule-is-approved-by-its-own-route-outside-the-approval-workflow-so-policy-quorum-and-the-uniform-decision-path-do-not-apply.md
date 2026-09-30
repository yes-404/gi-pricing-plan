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

**Severity: HIGH, confirmed.** **HIGH rests on the third condition of the maintainer's severity
rule, read literally** (an approved rule reaches a Rule Set with 0 `approval_requests` rows;
below); the substantive gap is the policy-quorum bypass (case 4), and the maintainer may revise
the severity in the light of it. The maintainer confirmed HIGH, **not CRITICAL** (`to-lead.md`,
"2026-09-30 11:23:26 BST — DECISION: validation-rule approval bypass: HIGH (not CRITICAL); owner
and order; two follow-ons"): self-approval is refused (409 plus a DB CHECK), a dry-run is
required, the impact is data-validation governance rather than a direct price, and there is no
production. A Validation Rule is a Governed Artifact,
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

**Both directions, recorded** (the maintainer's 11:23:26 entry asks for both): the **bypass**
(case 4, and case 3's approved rule with no request), and **the reverse gap**, the same class as
`06` FR-386's: the generic decide never carries to the rule, because `_carry_to_the_artifact`
(`api/approvals.py`, about `:488-525`) has **no validation-rule branch** (case 5). Its four
siblings, `model`, `custom_objective`, `custom_metric` and `rating_version`, each have one.

**Not measured, stated as such:** (a) whether `approve_rule` accepts a rule whose dry-run report
records a **failure**: `06:114` says the evidence is a *successful* dry-run, and `attach_dry_run`
attaches whatever the outcome (open item 1 below); (b) the **FR-363 evidence floor** (`06:109`,
"enforced at submission") on the generic path: the submit body has no evidence field, so what
enforces it there was not tested.

**Cause, by code reading.** `approve_rule` (`validation_rules.py:395-431`) loads the rule, checks
`approval:decide` (`:400-405`), `row.status != REVIEW` (`:406`, `RULE_NOT_APPROVED`) and
`row.authored_by == actor.id` (`:413`, `SUBMITTER_CANNOT_APPROVE`), then sets `row.status =
APPROVED` and `row.approved_by` (`:423-424`) and records the audit event. The route docstring
(`api/validation.py:359-`) says so: *"Approval policies — quorum, escalation, evidence bundles —
are `06`'s (WK-677). This is the module's own step."* That step is what `06` FR-354 and FR-351
say the uniform machine owns.

## Triage of the two creation-time sites

- **`seed_builtin_rules`** (`validation_rules.py:89-`): **exempt under `01` FR-68 only**
  (`01-data-management.md:169`, *"seeded into every workspace as approved rules"*), plus the DB
  check's `builtin IS TRUE` arm (`models.py:1155`). **No `06` clause exempts it.** Users cannot set `builtin`, `status`,
  `approved_by` or `dry_run_report_id` on create (422 `VALIDATION_FAILED` each, measured).
- **`replace_rule_set`** (`validation_rules.py:538-`; the row is built at `:621`): creates an
  `approved` **Rule Set** (`models.py:1195`, `default="approved"`), but **refuses unapproved
  member rules** (409 `RULE_NOT_APPROVED`, `:585`) and rejects a body `status` (422). So it
  **cannot approve a new user rule with no review**: no hole there. A Rule Set is created
  approved but **is not in `06:64`'s Governed Artifact list**, which names the Validation Rule.
  Whether a Rule Set should be governed is **a separate spec question, not this defect**: per the
  maintainer's 11:23:26 entry the decision-maker files an open question (options: govern
  rule-set composition, or keep it derived from approved rules), owner WK-1178. This record does
  not decide it.

## Disposition

**Owner: a WK-1178 fix slice** (`to-lead.md` "2026-09-30 11:23:26 BST", above; and the 11:14:48
entry for the HIGH slot rule: at HIGH it takes the next free build slot after the mispricing fix
pair's slice). **Order: serialised after WK-674 Slice 2 under RL-1263**, because it edits the
same existing definition, `_carry_to_the_artifact` (`api/approvals.py`), not concurrent with it.
Event that discharges it: that slice's merge.

**Scope and acceptance, red first:**

- route rule approval through `approvals.submit` and `approvals.decide`; **remove the direct
  approve route, or make it a thin client of the workflow** (`api/validation.py:355-`,
  `validation_rules.py:423-424`);
- **add the `_carry_to_the_artifact` validation-rule branch** (the reverse gap);
- red-first cases: **with a quorum of 2, one approval leaves the rule in `review`** (case 4
  becomes a refusal); the direct route is gone or refused; **the generic decide carries** to the
  rule (case 5 now moves it to `approved`);
- the creation sites stay as triaged above (the built-in exemption is named, not silent);
- **remove S2's temporary A.4 exemption**, red first: the *one named, dated, temporary
  exemption* for `validation_rules` in #971's (RL working id 9906) model-derived one-writer
  check over every approval-status table, which cites this FD by working id and is shrink-only.

**Open items** (the maintainer's 11:23:26 entry names both):

1. **Does approve accept a failed dry-run?** `06:114` says the evidence is a *successful*
   dry-run. auditor-922 is measuring it; **not measured in this record**. If it does, it goes in
   this FD and the fix's acceptance.
2. **Data check: approved rules with no approved approval request.** Measured by this record's
   author, read-only (`BEGIN READ ONLY ... ROLLBACK`), over every database on the local
   Postgres whose name starts `gipricing` and is not a template (77 databases: 74 have a
   `validation_rules` table, 3 have none or errored). Per database, `validation_rules` rows with
   `status='approved'`, split by `builtin`, and the non-built-in ones with **no** `approval_requests`
   row (`artifact_type='validation_rule'`, `artifact_ref='validation_rule:<slug>@<version>'`,
   `status='approved'`, same workspace). The runnable script is under the list below.
   **Result:** 8 databases hold non-built-in
   approved rules; across all 74, **739 non-built-in approved rules, 739 of them with no approved
   approval request** (every one), plus 18,962 built-in approved rows (exempt by `01` FR-68).
   These are development and test databases (fixture and test-run residue: `gipricing` itself,
   worktree databases), not production data, and there is no production. Any such row **stays
   approved after the fix**, so **the fix slice decides between re-review and grandfathering, and
   records which**. This record does not decide it.

The runnable predicate for open item 2 (`bash script.sh`, with the `gi-pricing-postgres-1`
container up):

```bash
#!/bin/bash
Q="BEGIN READ ONLY; select count(*) filter (where builtin), count(*) filter (where not builtin), count(*) filter (where not builtin and not exists (select 1 from approval_requests a where a.artifact_type='validation_rule' and a.artifact_ref='validation_rule:'||v.slug||'@'||v.version and a.status='approved' and a.workspace_id=v.workspace_id)) from validation_rules v where status='approved'; ROLLBACK;"
dbs=$(docker exec gi-pricing-postgres-1 psql -U gipricing -d postgres -Atc "select datname from pg_database where datname like 'gipricing%' and not datistemplate order by 1")
n=0; has=0; nohas=0; b=0; u=0; z=0
for d in $dbs; do
  n=$((n+1))
  out=$(docker exec gi-pricing-postgres-1 psql -U gipricing -d "$d" -At -F, -c "$Q" 2>&1 | grep -E '^[0-9]+,[0-9]+,[0-9]+$')
  if [ -z "$out" ]; then nohas=$((nohas+1)); continue; fi
  has=$((has+1))
  IFS=, read -r bb uu zz <<< "$out"
  b=$((b+bb)); u=$((u+uu)); z=$((z+zz))
  if [ "$uu" != 0 ] || [ "$zz" != 0 ]; then echo "$d builtin_approved=$bb user_approved=$uu user_approved_no_approved_request=$zz"; fi
done
echo "databases=$n with_tables=$has without_table_or_error=$nohas"
echo "TOTAL builtin_approved=$b user_approved=$u user_approved_with_no_approved_request=$z"
```

Its last line printed `TOTAL builtin_approved=18962 user_approved=739
user_approved_with_no_approved_request=739`. **Limits:** a database whose query errored counts in
`without_table_or_error`, so the 3 are not separated into "no table" and "error"; the databases
are a moving set (worktree databases come and go), so this is a count at one moment.

*Drafted under working id 9892.*
