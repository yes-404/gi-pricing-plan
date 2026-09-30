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

**A measured non-defect: a rule whose dry-run outcome is `fail` is approvable.** auditor-922
ingested a dirty dataset version (one negative `exposure_years`), created a draft `range` rule
(`min_exclusive: 0`, severity `fail`) and ran the real `DATASET_VALIDATE` job with
`dry_run_rule_id` (the job `succeeded`). `dry_run_report_id` was set, the report's overall outcome
was `fail`, and the rule's own outcome `['fail']`; `submit_for_review` then gave `review`, and a
second approver's `approve_rule` gave `approved`, the failing report still attached (the worker
attaches the report whatever the outcome, `data_handlers.py:292-296`; `validation_rules.py:371`
and the DB check `approved_rule_dry_run_and_separate_approver` test only non-null).
**Measured through the service functions the routes call, not through HTTP.** **This is not a
defect**, per the maintainer's correction (`to-lead.md` "2026-09-30 11:27:20 BST — correction to
the failed-dry-run follow-on: the spec means EXECUTED successfully; measure the `error` outcome
instead"): `01` §4.5 step 2 (`01-data-management.md:520-521`) requires the rule to **execute**
successfully against at least one existing Dataset Version, and `01:470-473` says an unknown
`check` produces an `error` outcome that FR-48 refuses to count as a pass, and *"the
mandatory dry-run (step 2 below) is what stops it reaching approval"*; step 2 also says the
dry-run result *"is attached to the approval request"*. So `06:114`'s "successful dry-run result" means the run **executed (no `error`
outcome)**, not that the data passed: that rule worked and caught bad rows. It is **not** a gap
in this FD and has **no** red-first acceptance item.

**The `06:114` gap, measured: a rule whose dry-run outcome is `error` is submitted and approved.**
Measured by auditor-922 (attributed; reproduction by auditor-924d pending; not re-run by this
record's author) on a per-worktree database at `9f63d0fe`, alembic head. Method: a real
`DATASET_VALIDATE` job with `dry_run_rule_id` on an ingested dataset version, then
`submit_for_review` and `approve_rule` by a second approver, **through the service functions the
routes call, not HTTP**. Three variants, each with the same result:

| Variant | Job | `dry_run_report_id` | Report and rule outcome | Submit | Approve |
|---|---|---|---|---|---|
| missing column (`range` on `no_such_column`) | succeeded | attached | `error`, rule `['error']` | `review` | **`approved`** |
| unknown check (`no_such_check`) | succeeded | attached | `error`, rule `['error']` | `review` | **`approved`** (`create_rule` did not refuse it) |
| missing table (`no_such_table`) | succeeded | attached | `error`, rule `['error']` | `review` | **`approved`** |

**Cause:** `attach_dry_run` (`data_handlers.py:292-296`) attaches the report whatever its outcome;
`submit_for_review` (`validation_rules.py:371`) and the DB check
`approved_rule_dry_run_and_separate_approver` test only that `dry_run_report_id` is non-null. **A
rule that never executed reaches `approved`**, against `01` §4.5 step 2 ("must execute
successfully") and `01:470-473`, where the mandatory dry-run is what stops an `error` outcome
reaching approval. This is the `06:114` gap, and it is in this FD's acceptance. Not tested: a
dry-run against a version with zero rows. **HIGH stands either way** (the quorum bypass).

**Not measured, stated as such:** the **FR-363 evidence floor** (`06:109`, "enforced at
submission") on the generic path: the submit body has no evidence field, so what enforces it
there was not tested.

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
- **a rule whose dry-run outcome is `error` is refused at submit** (and at approve): the three
  variants above (missing column, unknown check, missing table) each become a refusal, red
  first; a `fail` outcome stays accepted (the measured non-defect);
- the creation sites stay as triaged above (the built-in exemption is named, not silent);
- **remove S2's temporary A.4 exemption**, red first: the *one named, dated, temporary
  exemption* for `validation_rules` in #971's (RL working id 9906) model-derived one-writer
  check over every approval-status table, which cites this FD by working id and is shrink-only.

**Follow-ons** (the maintainer's 11:23:26 entry names both):

1. **The `error`-outcome dry-run**: measured above, and in the acceptance; auditor-924d's
   reproduction is pending.
2. **Data check: approved rules with no approved approval request.** **The fix's obligation, per
   the maintainer's 11:27:20 entry:** there is no production, so the fix slice **resets
   non-built-in approved rules that have no approved approval request to `review`** in the
   template and the fixtures, rather than grandfathering them, **and records the count**.
   Built-ins (`01` FR-68) are untouched. The measurements follow. First, this record's author's
   own, read-only (`BEGIN READ ONLY ... ROLLBACK`), over every database on the local
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
   approved after the fix unless reset**, hence the obligation above.

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

**auditor-922's later count (attributed, not re-run by this record's author)**, over a different
database set: `select datname from pg_database where not datistemplate and datallowconn` gave
**80 databases, 76 with `validation_rules`, 4 without**, with this predicate, verbatim:

```sql
select count(*) filter (where status='approved' and builtin is not true), count(*) filter (where status='approved' and builtin is not true and not exists (select 1 from approval_requests a where a.workspace_id=r.workspace_id and a.artifact_ref='validation_rule:'||r.slug||'@'||r.version and a.status='approved')), count(*) filter (where status='approved' and builtin is true), count(*) from validation_rules r
```

Totals over the 76: **749 approved non-built-in rules, all 749 with no approved
`approval_request`** (0 with one), **19,494 approved built-ins** (`01` FR-68, counted separately)
and 20,245 rules in all. The 9 databases holding approved non-built-in rules: `gipricing` 10,
`gipricing_aud976b` 10, `gipricing_exec-690s1_9bcacb9a` 205, `gipricing_tree-s3` 10,
`gipricing_w37-6-run2-gate-1789676768` 15, `gipricing_w37-6-run2-gate-1789690960` 10,
`gipricing_wt-ci-structure` 205, `gipricing_wt-d9d13-redo` 101 and `gipricing_wt-paths-d9-d13`
183. **All are scratch or test databases, including the `gipricing` template's 10, which every
scratch database inherits.** **Reconciling the two counts: they are two different populations
measured at two different times, not a count that fell.**

| | This record's author | auditor-922 |
|---|---|---|
| Database list predicate | `datname like 'gipricing%' and not datistemplate` | `not datistemplate and datallowconn` |
| Databases | 77 (74 with the table, 3 without or errored) | 80 (76 with the table, 4 without) |
| Approved non-built-in rules, none with an approved request | 739 of 739, in 8 databases | 749 of 749, in 9 databases |
| Row predicate | the script above | the SQL above, verbatim |
| When | 2026-09-30, before 11:30 BST (the run was not timestamped) | 2026-09-30, later; its list includes `gipricing_aud976b` (10 rules), created during an audit |

The 10 extra rules are `gipricing_aud976b`'s. **Provenance
was not checked:** whether any row came from a real approval route or a test or seed insert.
749 of 749 is what the bypass predicts, since the direct route never writes an `approval_request`.

*Drafted under working id 9892.*
