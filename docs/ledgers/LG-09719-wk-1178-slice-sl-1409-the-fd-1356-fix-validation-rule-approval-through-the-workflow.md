---
id: LG-9719
family: ledger
title: WK-1178 slice SL-1409 — the FD-1356 fix, a validation rule is approved only through the approval workflow (PL-1408), Task 0 containment and preconditions
status: active
created: 2026-10-05
owner: executor
tree: bf33eea622e849672e02154b10026595b6e0ba5a
phase: P2
work: WK-1178
slice: SL-1409
plans: [PL-1408]
corrected_by: []
relates: [RL-1407, RL-1263, FD-1356, WK-1178]
---

# LG 9719 (working id) — WK-1178 slice SL-1409, the FD-1356 fix

Executed from `PL-1408` by `executor-1409`. `echo $CLAUDE_EFFORT` printed `medium`; the model is Sonnet 5.5
(`claude-sonnet-5-5`). The executor charter's Model / effort line, verbatim: "`sonnet` (currently Sonnet 5); medium,
inherited from the lead — the highest-volume role; per-slice gates and the auditor's re-check bound the risk of a
cheaper setting." Branch `sl-1409-validation-rule-approval-through-the-workflow`, worktree
`.claude/worktrees/sl-1409`. Stamps are BST (`TZ=Europe/London date`).

The dispatch record is `gi-pricing-plan.local/handover/DISPATCH-WK-1178-SL1409-2026-10-04.md` (FINAL; Deltas 1 to 4
bind). It is a local file and is not in the repository.

## Tasks

### Task 0 — preconditions and containment (no code)

**Base.** Branched from `origin/main` `bf33eea622e849672e02154b10026595b6e0ba5a` (#1112, the activation of PL-1408
and SL-1409). `git fetch origin main` printed the same SHA at 2026-10-05 10:5x BST. `uv sync --all-packages` ran. No
test suite was run (another slice's gate holds a slot).

**Step 1 — containment.** The script is PL-1408 Task 0's fenced `bash` block, extracted verbatim to a scratch path
outside the repository (21 lines; `sha256sum` `5932de806be2c725c8d8b00aed7f432ef6e5f7f11b5fe71bdc6051c103338245`,
the digest the dispatch record's Delta 3 gives). Run with `bash`, `gi-pricing-postgres-1` up.

- Start 2026-10-05 10:57:54 BST; end 10:58:15 BST; **exit code 0**.
- Last two lines:

```text
databases=92 with_tables=89 without_table_or_error=3
TOTAL route_approved=0 self_approved=0 user_approved_no_approved_request=373
```

- The STOP predicate (`route_approved`) is 0, and `self_approved` is 0 (the CHECK holds). The third column, 373,
  is context only (it was 324 at the lead's 09:42:38 BST run, 314 on 2026-10-01); it is not a STOP condition. The
  three databases without the table are `gipricing_clone_m2`, `gipricing_w37-6-run2` and
  `gipricing_w37_6_d7_g_executor` (`no_table_or_error`).

**Step 2 — the DP-0 export.** `sha256sum -c SHA256SUMS` in
`gi-pricing-plan.local/handover/fd1356-dp0-export-2026-10-01/` printed `OK` for all six files. Compared line by line
with PL-1408 §"DP-0's decided record" (its `SHA256SUMS` block, verbatim): the six digests are identical, file for file:

| file | sha256 (matches the plan's recorded line) |
|---|---|
| `audit_events.csv` | `42e9503b08c147a1439684ddb892b61a466af47f9cc4b624a03e547b5ab64c3b` |
| `audit_events.jsonl` | `ee074f2b78196f0572182f2b52b16a77faf2b5cf1eb26c6f83428071af52afb2` |
| `validation_rules.csv` | `aa7dbc4e531a80913c9931936e5a4de8daab4ec1f20d53a090de41bc77d2a650` |
| `validation_rules.jsonl` | `8c9e57ca173ad7018c853fd17b3c6cd7f664d36b5d3e207092295ab8c44361e0` |
| `provenance.md` | `9c4f945c7d366d15969150afc64bbde4f6759d3f0d42d183bf4106add0e7c119` |
| `drop-and-rerun.md` | `948404e2a2f99cccf6d5582eb05947763c8bee1eb2fa56727f9962bd016493e5` |

No mismatch, no missing file. The local directory is **kept, unmodified**, until this ledger has merged (the
RETENTION hold). The full export follows, each file verbatim, in the section "The DP-0 export, verbatim" below.

**Step 3 — the order.** `git log origin/main` shows SL-1256 (`dfddfad8`, #1104), SL-1360 (`d8537220`, #1049) and the
FD-1357 fix SL-1377 (`8252741c`, #1087) merged. **The Alembic head on the merge base is `c4a81f6d2e95`**
(`backend/migrations/versions/c4a81f6d2e95_environments_and_deployments.py`; the only revision no `down_revision`
names, derived by a script over the 51 revision files, because `alembic heads` needs `-c alembic.ini` and a DSN). It
is Task 7's `down_revision`.

**Step 4 — the shared files at `bf33eea6`, by symbol.**

| symbol | file | line at `bf33eea6` |
|---|---|---|
| `_carry_to_the_artifact` | `backend/src/app/api/approvals.py` | `:512` |
| `decide_request` | `backend/src/app/api/approvals.py` | `:216` |
| `submit_for_approval` | `backend/src/app/api/approvals.py` | `:105` |
| `_resolve_the_artifact` | `backend/src/app/api/approvals.py` | `:443` |
| `approve_rule` | `backend/src/app/platform/validation_rules.py` | `:403` |
| `submit_for_review` | `backend/src/app/platform/validation_rules.py` | `:366` |
| `resolve_artifact_ref` | `backend/src/app/platform/validation_rules.py` | `:317` |
| `ALLOWANCE_SITES` | `backend/tests/test_approval_guard_static.py` | `:37` (the set's lines `:37-46`) |
| the rule write in the seed | `examples/fremtpl2/seed.py`, `run`, `ValidationRuleRow(` | `:437` |

(The plan names `seed.py` in the backend; the only seed module that writes a rule is `examples/fremtpl2/seed.py`, and
`backend/src/app/` has no `seed.py`. `platform/validation_rules.py::seed_builtin_rules` is the other seed writer.)

- **Did S2 type `POST /approval-requests`?** The **request body, yes**: `submit_for_approval` takes
  `ApprovalSubmission`, defined at `packages/model-schema/src/model_schema/approvals.py` (`class ApprovalSubmission`,
  `:355`), exported from `model_schema/__init__.py`, and `docs/contracts/openapi/generated.json` carries
  `#/components/schemas/ApprovalSubmission` as its `requestBody`. The **`201` is not typed**: the decorator has no
  `response_model`, and the OpenAPI `201` schema is `additionalProperties: true`, titled
  `Response Submit For Approval Api V1 Approval Requests Post`. The `decide` body is the component `Decide`, but it
  is **defined in the API module** (`class Decide(BaseModel)` at `backend/src/app/api/approvals.py:78`), not in
  `model-schema`; its `200` is untyped as well. PL-1408 moves `Decide` to `model-schema` (the `__all__` names below).
  Typing the `200` stays with FD 9752.
- **Temporary validation-rule exemptions** (`git grep -n -i 'FD-1356\|9892\|validation-rule fix slice' -- backend
  tests`): exactly two, both the allowance of `PL-1303` Acceptance 7, which Task 1 removes:
  `backend/tests/test_approval_guard_static.py` (the comment above the `approve_rule` entry in `ALLOWANCE_SITES`,
  and that entry) and `backend/src/app/platform/validation_rules.py` (the `ALLOWANCE` comment inside `approve_rule`,
  above the `approvals.approval_decision(session)` block). Neither is an exemption added by S2 to a one-writer check
  beyond these. `replace_rule_set`'s entry stays (OQ 9987).

**Step 5 — open PRs touching the plan's files.** `gh pr list --state open` at 2026-10-05 ~11:0x BST returned 31; the
`files` of each were filtered for `api/approvals.py`, `platform/approvals.py`, `validation_rules.py`,
`api/validation.py`, `seed`, `01-data-management` and `test_contracts`: **none matches**. All open PRs are either
docs-only (findings, rulings, plans) or dependency bumps (#1120, #1121), and the two dependency bumps touch only
manifests. No head SHA to name. (WK-690 S3, SL-1273, is on its branch and not yet a PR; the dispatch record's
RL-1263 table covers it.)

**Delta 1 — re-pointed by symbol** (the dispatch record's Delta 1; the plan's line numbers are stale after S2):

| plan citation | symbol | now |
|---|---|---|
| `approvals.py:648` (`backend/src/app/platform/approvals.py`) | `service.to_dict` | `def to_dict`, `backend/src/app/platform/approvals.py:663` |
| `test_api_approvals.py:999-1012` | `_require_two_approvals` | `backend/tests/test_api_approvals.py:1061` |
| `test_api_approvals.py:986` | `_AFTER["validation_rule"] = dict.fromkeys(_OUTCOMES, "review")` | `_AFTER` at `backend/tests/test_api_approvals.py:1040`, its `validation_rule` entry on `:1045` |
| `model_schema/approvals.py:205-209` | `DEFAULT_POLICY`'s `validation_rule` entry | `DEFAULT_POLICY` at `packages/model-schema/src/model_schema/approvals.py:282`, the entry `artifact_type="validation_rule"` at `:285` |

Tasks cite the symbols above, not these line numbers.

**Holds.** FD 9752: this slice changes no `to_dict` approval route's response and reads none anew (Task 0 read no
response body). RETENTION: the export directory was read, not touched.

### Task 1 — the allowance removal, red first (2026-10-05 10:0x UTC, executor-1409-t1)

Edit: `backend/tests/test_approval_guard_static.py`, `ALLOWANCE_SITES`: the entry
`("backend/src/app/platform/validation_rules.py", "approve_rule")` deleted; the comment above
`replace_rule_set` rewritten to `# Temporary: pending OQ 9987 (working id), per RL-1301 A.4.5.`
No other file touched. Step 1's old comment was the only validation-rule exemption in
`backend/tests` (`git grep -n -i 'FD-1356\|9892\|validation-rule fix slice' -- backend/tests`
returned only that comment).

Red run, `uv run pytest -q backend/tests/test_approval_guard_static.py -k "sanctioned_and_allowance_sites or every_pinned_site"`:

- `test_approval_decision_is_entered_only_at_the_sanctioned_and_allowance_sites`:
  `AssertionError: assert ['backend/src...approve_rule'] == []`, "Left contains one more item:
  'backend/src/app/platform/validation_rules.py::approve_rule'". Cause: `approve_rule` still
  enters `approval_decision()` and is no longer pinned. The plan's expected list, matched.
- `test_every_pinned_site_really_enters_the_context`:
  `AssertionError: assert {('backend/sr...d.py', 'run')} == frozenset({('....p...`, "Extra items in
  the left set: ('backend/src/app/platform/validation_rules.py', 'approve_rule')". Cause: same
  site, entered but not pinned.
- Totals: `2 failed, 15 deselected, 2 warnings in 1.95s`.

Deviation: per plan Task 1 Step 3 ("Do not commit yet. Task 3 turns these green; the two commit
together") the test edit is left uncommitted in the worktree; only this entry is committed.
Test-database warning (per-worktree DB absent) is unrelated to these two static tests.

### Tasks 2 and 3 — the tests red first, then the service and the carry (2026-10-05, executor-1409-t23)

One executor for both, one commit with Task 1's edit (lead's Delta 6; PL-1408 Task 1 Step 3 and Task 3 Step 8).
Per-worktree test database created first (`gipricing_sl-1409_8f3bb0b4`, `createdb -T gipricing`, `alembic upgrade head`).

**Check 32 fix (Delta 6).** The DP-0 export quote of `drop-and-rerun.md` sat in a `~~~~text` fence, which `audit-docs.py`
does not read as a fence (`_FENCE_LINE_RE` matches a leading ```` ``` ```` only), so the plan citation inside it read as a live one.
The pair of fence lines around that one quote is now ```` ```text ````; no byte inside it changed (`sed -n` of the block
`diff`s identical to `fd1356-dp0-export-2026-10-01/drop-and-rerun.md`, sha256 `948404e2…493e5`; `sha256sum -c SHA256SUMS`
there: 6 of 6 OK). `audit-docs` then reports check 31 alone.

**Task 2, red run, before any Task 3 code** (`uv run pytest -q backend/tests/test_validation_rule_approval.py
backend/tests/test_api_approvals.py backend/tests/test_api_datasets.py`): `21 failed, 125 passed, 3 warnings in 121.59s`.
Each failure, with its cause:

| test | failure line | cause |
|---|---|---|
| `test_a_decision_moves_the_version_as_fr_355_says_and_records_it_truly[validation_rule-approve]` | `assert 'review' == 'approved'` | the carry has no `validation_rule` branch; the status stays `review` |
| `…[validation_rule-reject]`, `…[validation_rule-request_changes]` | `assert 'review' == 'draft'` | same |
| `test_an_error_dry_run_is_refused_at_submit[missing_column\|unknown_check\|missing_table]` (3) | `assert 200 == 422` | submit does not read the report: an `error` dry run reaches `review` |
| `test_an_error_dry_run_is_refused_at_approve[…]` (3) | `assert 200 == 422` | the generic decide has no evidence check: it answers 200 |
| `test_the_generic_submit_refuses_an_error_dry_run` | `assert 201 == 422` | the resolver checks the status only |
| `test_a_dry_run_report_that_cannot_be_read_is_refused` | `assert 200 == 422` | a dangling `dry_run_report_id` is accepted |
| `test_one_approval_under_a_quorum_of_two_leaves_the_rule_in_review` | `assert 'approved' == 'review'` | the direct route approves on one call, with no quorum |
| `test_an_approver_without_a_policy_role_is_refused` | `assert 200 == 403` | the direct route checks no policy role |
| `test_the_module_submit_creates_the_request` | `assert 200 == 422` | the submit has no body and files no request |
| `test_the_approve_route_decides_through_the_workflow`, `test_the_carry_records_the_request_it_carried`, `test_a_fail_dry_run_is_still_approvable` | `ValueError: not enough values to unpack (expected 1, got 0)` on `_requests(...)` | the submit files **0 requests** (the plan's "approved with 0 requests"). The third is the plan's control: it cannot pass on the base tree, because it decides the request the base submit never files |
| `test_an_approved_rules_dry_run_cannot_be_replaced` | `assert <JobStatus.SUCCEEDED> is not <JobStatus.SUCCEEDED>` | `attach_dry_run` replaces an approved rule's report; the job succeeds (the plan's red) |
| `test_a_rule_set_run_refuses_a_member_with_no_rule` | `assert 200 == 404` | `GET …/rule-set` silently drops the member |
| `test_the_submitter_and_the_author_cannot_decide` | `assert 409 == 403` | the direct route answers 409 |
| `test_a_rule_walks_draft_to_approved_and_never_by_its_author` (`test_api_datasets.py`) | `assert 409 == 403` | same |

Passed on the base tree: `test_a_fail_dry_run_is_still_approvable` is NOT among them (above); the controls
`test_the_read_shows_a_member_in_review` and the `first_of_two` rows did pass.

**Task 3, green.** `uv run pytest -q backend/tests/test_approval_guard_static.py backend/tests/test_validation_rule_approval.py
backend/tests/test_api_approvals.py backend/tests/test_api_datasets.py backend/tests/test_approval_guard.py
backend/tests/test_approval_guard_allowance.py backend/tests/test_validation_reports.py backend/tests/test_data_jobs.py
backend/tests/test_api_validation_rules.py`: `212 passed, 4 warnings in 142.33s`. Task 1's two static tests are among them
and green. `ruff check backend packages scripts`: all checks passed. `mypy`: no issues in 226 source files. `lint-imports`: 4 kept, 0 broken.
`audit-docs`: check 31 alone. `generate-contracts.py --check`: **FAILS** (`docs/contracts/openapi/generated.json`), see Deviation 1.

Recorded facts: the dry-run job that the immutability refusal fails records `error.code == "RULE_VERSION_IMMUTABLE"`
(asserted). The dataset-slug in the refusal text is the dataset's own slug: `data_handlers._validate` now reads the
`DatasetRow` for it (it passed `str(dataset_id)` as the `slug` before, which the text's `PUT /datasets/<slug>/rule-set` cannot use).
`approved_rows.py` was not edited: `mark_approved` already covers `ValidationRuleRow`.

**Files touched** (against PL-1408 :472-506): `backend/src/app/platform/validation_rules.py`, `backend/src/app/api/approvals.py`
(`decide_and_carry`; the `validation_rule` carry call), `backend/src/app/worker/data_handlers.py`, `backend/src/app/errors.py`,
`backend/src/app/api/validation.py`, `packages/model-schema/src/model_schema/validation.py` (all in the write set); tests:
`backend/tests/dry_run_reports.py` and `test_validation_rule_approval.py` (new), `test_api_approvals.py`, `test_api_datasets.py`,
`test_approval_guard_static.py` (Task 1), `test_approval_guard_allowance.py`. `approvals.py` (platform) read only. No `to_dict` route touched.

**Deviations, for the lead.**
1. **Task 3 cannot leave the two rule routes alone.** Step 6 deletes `approve_rule` and Step 2 changes `submit_for_review`'s
   signature; both are called by `api/validation.py` (Task 4's file). Left alone, `mypy` fails and the routes 500, and none of
   Task 2's route-driven tests can go green. So this commit also carries **Task 4 Step 2 (the class) and Step 3 (the thin client)**
   only: `ValidationRuleSubmission` in `model_schema/validation.py` (its module `__all__`), imported by the route from
   `model_schema.validation`; the approve route calls `open_request_for` then `decide_and_carry`. **Not done (Task 4's):** the
   `model_schema/__init__.py` `__all__` appends (`ValidationRuleSubmission`, `Decide`), moving `Decide`, regenerating `docs/contracts/`
   (so the contracts `--check` is red at this head), and Task 4 Step 1's two new tests. Task 4's red-first case for the submit body
   is therefore already green; its other case (decide's body) is untouched.
2. **`backend/tests/test_approval_guard.py`** is outside the write set, but the plan's Step 8 runs `test_approval_guard*.py` green
   and `test_the_carry_walker_reaches_the_five_artifact_tables` now fails by design: the carry writes `validation_rules`. Its
   expected set gains `"validation_rules"` (as `deployment_requests` joined it); the test's name is kept because a frozen
   record cites it.
3. `test_a_fail_dry_run_is_still_approvable` is red on the base tree (table above), not a passing control.

### The write set under the `__all__` amendment (Delta 4, #1118)

Names this slice appends to `packages/model-schema/src/model_schema/__init__.py`, appended only, each with its import
line: **`ValidationRuleSubmission`** and **`Decide`**. WK-690 S3's names are `DerivedBlock` and `ObjectiveParameter`;
the sets are disjoint. Task 0 edits no file; this record is for the tasks that do. The second to merge re-gates.

### The DP-0 export, verbatim


#### `provenance.md`

~~~~text
# FD-1356 DP-0 export — provenance (exported 2026-10-01 10:41 BST by auditor-dp0)

Source DB: `gipricing_w37-6-run2-gate-1789676768` (compose server gi-pricing-postgres-1), exported BEFORE the drop.
Authority: maintainer, to-lead.md entry "2026-10-01 10:39:13 BST — #1063 DP-0 DECIDED: (c) export, then drop, then re-run expecting 0 ...". Reading: route_approved.

## The 5 rules (validation_rules, all columns: validation_rules.csv / .jsonl; 5 rows)
slug, version 1, status approved, builtin f, source `api`:
- rng-bf487669 — workspace 01a0b10d-ee00-70fe-af35-35501548dafd (1 rule)
- rng-c1c106c8, rng-f8e9b7c4 — workspace 01a0b10d-f2c7-7f29-8863-ee6daa940b72 (2 rules)
- rng-2f0a876d, rng-b73d354e — workspace 01a0b10d-f601-7f80-a811-d9f96b9ed567 (2 rules)
Workspace split 1+2+2.
In each workspace authored_by and approved_by are two different user ids (DB CHECK holds; self_approved=0).

## Audit events (audit_events, all columns: audit_events.csv / .jsonl; 15 rows = 5 x created, submitted, approved)
Actor on every event: kind user, display `dev@localhost` (six distinct user ids, an author and an approver per workspace). Source `api`.
Events span 2026-09-17 20:27:56.267510Z .. 20:27:58.036136Z (UTC).
Each `validation_rule.approved` event's `after` is {"status","approved_by"} only — no `approval_request_id`: the direct route (approve_rule), outside the approval workflow.
Selection: `entity_ref like 'validation_rule:'||slug||'@%'` for the 5 slugs; cross-check `entity_ref ~ 'rng-(...)'` count also 15.

## Match to test code at dee54ab8f8da5fc72d271fd7e69b91202d1f640d (`git show dee54ab8:backend/tests/test_api_datasets.py | sed -n 'N,Mp'`)
:513      `            "severity": "fail",`
:628      `            "params": {"min_inclusive": 18, "key_columns": ["policy_id"]},`
:685      `        "params": {"min_inclusive": 18, "key_columns": ["policy_id"]},`
:731-732  `    kept = _approved_rule(client, headers, approver_headers, database)` / `    parked = _approved_rule(`
:779      `    strict = _approved_rule(client, headers, approver_headers, database, severity="fail")`
:790      `    lenient = _approved_rule(client, headers, approver_headers, database, severity="warn")`
The `rng-<8 hex>` slug form is the one `_approved_rule` and its chain test author (:628, :685). Workspace counts 1+2+2 correspond to :628 (1), :731-732 (2), :779-790 (2) as read by the maintainer; the auditor did not re-derive the per-test workspace mapping beyond matching the quoted lines.

## Gate log (gate-logs-tmpfs-rescue/gate-dee54ab-1789676768.log, verbatim)
GATE START 2026-09-17T20:26:08Z tree=dee54ab8f8da5fc72d271fd7e69b91202d1f640d wt=/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/agent-a35a3eed724e9bc84 db=gipricing_w37-6-run2-gate-1789676768
createdb gipricing_w37-6-run2-gate-1789676768 ok
alembic EXIT=0 
GATE STOPPED (dry run abandoned) 21:27:43 BST
(21:27:43 BST on 2026-09-17 = 20:27:43Z; the log gives no date on that line — same-day assumed.)
Timing: first event 20:27:56.27Z is 13 s after the stop line; last 20:27:58.04Z is 15 s after.

## State at export
- Connections to the DB (pg_stat_activity datname = it): 0, read 2026-10-01 10:40:28 BST and again 10:40:46 BST.
- Worktree /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/agent-a35a3eed724e9bc84: absent; `git worktree list | grep a35a3eed` = 0 hits.
- Task 0 at export: this DB had 15 approved non-builtin rules, 5 route_approved (the exported ones).

## Caveats / reading
- TIMING IS NOT PROOF. Events landing 13–15 s after the gate's stop line fit a test run that was still executing after the "abandoned" mark; slug form, actor and name fit test residue. That is an inference, not a provenance check; no process record ties the writes to a test run.
- The rows show the direct route (approve_rule, no approval_request_id) was reachable and exercised by tests, which is consistent with FD-1356's HIGH.
~~~~

#### `drop-and-rerun.md`

```text
# DP-0 step 2/3 record (auditor-dp0)
- Connections 0 at 2026-10-01 10:41:04 BST; `DROP DATABASE "gipricing_w37-6-run2-gate-1789676768";` ran 10:41:04–10:41:05 BST; `\l` and pg_database show 0 rows for it.
- Task 0 re-run (script copied verbatim from PL-09762 Task 0 Step 1 at origin/fd1356-fix-leaf-plan), 10:41:08–10:41:19 BST, exit 0, last line:
  TOTAL route_approved=0 self_approved=0 user_approved_no_approved_request=314   (databases=80 with_tables=77 without_table_or_error=3)
- user_approved_no_approved_request fell 329 -> 314 (the dropped DB held 15).
```

#### `SHA256SUMS`

~~~~text
42e9503b08c147a1439684ddb892b61a466af47f9cc4b624a03e547b5ab64c3b  audit_events.csv
ee074f2b78196f0572182f2b52b16a77faf2b5cf1eb26c6f83428071af52afb2  audit_events.jsonl
aa7dbc4e531a80913c9931936e5a4de8daab4ec1f20d53a090de41bc77d2a650  validation_rules.csv
8c9e57ca173ad7018c853fd17b3c6cd7f664d36b5d3e207092295ab8c44361e0  validation_rules.jsonl
9c4f945c7d366d15969150afc64bbde4f6759d3f0d42d183bf4106add0e7c119  provenance.md
948404e2a2f99cccf6d5582eb05947763c8bee1eb2fa56727f9962bd016493e5  drop-and-rerun.md
~~~~

#### `validation_rules.csv`

~~~~text
id,workspace_id,slug,version,layer,check,severity,body,status,authored_by,approved_by,dry_run_report_id,created_at,builtin,catalogue_id
01a0b10d-f818-78f3-a0ac-571a17061fdf,01a0b10d-f601-7f80-a811-d9f96b9ed567,rng-2f0a876d,1,actuarial_sanity,range,fail,"{""scope"": {}, ""params"": {""key_columns"": [""policy_id""], ""min_inclusive"": 18}, ""target"": {""table"": ""policy_exposure"", ""column"": ""driv_age""}, ""message"": """", ""rationale"": """", ""tolerance"": {}}",approved,01a0b10d-f601-7981-8fd3-e6439d68b787,01a0b10d-f667-7f3d-98fc-d2ce538a3e60,01a0b10d-f827-7ade-9add-3a706d90355f,2026-09-17 20:27:57.84206+00,f,
01a0b10d-f897-71d3-95a3-a43fd8993b6e,01a0b10d-f601-7f80-a811-d9f96b9ed567,rng-b73d354e,1,actuarial_sanity,range,warn,"{""scope"": {}, ""params"": {""key_columns"": [""policy_id""], ""min_inclusive"": 18}, ""target"": {""table"": ""policy_exposure"", ""column"": ""driv_age""}, ""message"": """", ""rationale"": """", ""tolerance"": {}}",approved,01a0b10d-f601-7981-8fd3-e6439d68b787,01a0b10d-f667-7f3d-98fc-d2ce538a3e60,01a0b10d-f8a5-7cf3-812c-d61493a5d52f,2026-09-17 20:27:57.972881+00,f,
01a0b10d-f1fa-719c-9970-061bfaff6abc,01a0b10d-ee00-70fe-af35-35501548dafd,rng-bf487669,1,actuarial_sanity,range,warn,"{""scope"": {}, ""params"": {""key_columns"": [""policy_id""], ""min_inclusive"": 18}, ""target"": {""table"": ""policy_exposure"", ""column"": ""driv_age""}, ""message"": """", ""rationale"": """", ""tolerance"": {}}",approved,01a0b10d-ee00-7485-a86b-8d9f6154fc92,01a0b10d-f27b-72b9-ba4e-f84d30f07079,01a0b10d-f242-7dd6-9ff7-bad1d7b973aa,2026-09-17 20:27:56.26751+00,f,
01a0b10d-f4f0-7cd7-8d51-aee25d8ec64d,01a0b10d-f2c7-7f29-8863-ee6daa940b72,rng-c1c106c8,1,actuarial_sanity,range,warn,"{""scope"": {}, ""params"": {""key_columns"": [""policy_id""], ""min_inclusive"": 18}, ""target"": {""table"": ""policy_exposure"", ""column"": ""driv_age""}, ""message"": """", ""rationale"": """", ""tolerance"": {}}",approved,01a0b10d-f2c7-78d1-8a43-628bdd866ace,01a0b10d-f329-70d6-a423-67ff9f9184a6,01a0b10d-f501-793a-80c3-31f219ae307e,2026-09-17 20:27:57.031323+00,f,
01a0b10d-f551-73c9-8b54-ef8083e3c380,01a0b10d-f2c7-7f29-8863-ee6daa940b72,rng-f8e9b7c4,1,structural,not_null,warn,"{""scope"": {}, ""params"": {""key_columns"": [""policy_id""]}, ""target"": {""table"": ""policy_exposure"", ""column"": ""driv_age""}, ""message"": """", ""rationale"": """", ""tolerance"": {}}",approved,01a0b10d-f2c7-78d1-8a43-628bdd866ace,01a0b10d-f329-70d6-a423-67ff9f9184a6,01a0b10d-f55f-7ea5-ad49-e0e965b36361,2026-09-17 20:27:57.132625+00,f,
~~~~

#### `validation_rules.jsonl`

~~~~text
{"id":"01a0b10d-f818-78f3-a0ac-571a17061fdf","workspace_id":"01a0b10d-f601-7f80-a811-d9f96b9ed567","slug":"rng-2f0a876d","version":1,"layer":"actuarial_sanity","check":"range","severity":"fail","body":{"scope": {}, "params": {"key_columns": ["policy_id"], "min_inclusive": 18}, "target": {"table": "policy_exposure", "column": "driv_age"}, "message": "", "rationale": "", "tolerance": {}},"status":"approved","authored_by":"01a0b10d-f601-7981-8fd3-e6439d68b787","approved_by":"01a0b10d-f667-7f3d-98fc-d2ce538a3e60","dry_run_report_id":"01a0b10d-f827-7ade-9add-3a706d90355f","created_at":"2026-09-17T20:27:57.84206+00:00","builtin":false,"catalogue_id":null}
{"id":"01a0b10d-f897-71d3-95a3-a43fd8993b6e","workspace_id":"01a0b10d-f601-7f80-a811-d9f96b9ed567","slug":"rng-b73d354e","version":1,"layer":"actuarial_sanity","check":"range","severity":"warn","body":{"scope": {}, "params": {"key_columns": ["policy_id"], "min_inclusive": 18}, "target": {"table": "policy_exposure", "column": "driv_age"}, "message": "", "rationale": "", "tolerance": {}},"status":"approved","authored_by":"01a0b10d-f601-7981-8fd3-e6439d68b787","approved_by":"01a0b10d-f667-7f3d-98fc-d2ce538a3e60","dry_run_report_id":"01a0b10d-f8a5-7cf3-812c-d61493a5d52f","created_at":"2026-09-17T20:27:57.972881+00:00","builtin":false,"catalogue_id":null}
{"id":"01a0b10d-f1fa-719c-9970-061bfaff6abc","workspace_id":"01a0b10d-ee00-70fe-af35-35501548dafd","slug":"rng-bf487669","version":1,"layer":"actuarial_sanity","check":"range","severity":"warn","body":{"scope": {}, "params": {"key_columns": ["policy_id"], "min_inclusive": 18}, "target": {"table": "policy_exposure", "column": "driv_age"}, "message": "", "rationale": "", "tolerance": {}},"status":"approved","authored_by":"01a0b10d-ee00-7485-a86b-8d9f6154fc92","approved_by":"01a0b10d-f27b-72b9-ba4e-f84d30f07079","dry_run_report_id":"01a0b10d-f242-7dd6-9ff7-bad1d7b973aa","created_at":"2026-09-17T20:27:56.26751+00:00","builtin":false,"catalogue_id":null}
{"id":"01a0b10d-f4f0-7cd7-8d51-aee25d8ec64d","workspace_id":"01a0b10d-f2c7-7f29-8863-ee6daa940b72","slug":"rng-c1c106c8","version":1,"layer":"actuarial_sanity","check":"range","severity":"warn","body":{"scope": {}, "params": {"key_columns": ["policy_id"], "min_inclusive": 18}, "target": {"table": "policy_exposure", "column": "driv_age"}, "message": "", "rationale": "", "tolerance": {}},"status":"approved","authored_by":"01a0b10d-f2c7-78d1-8a43-628bdd866ace","approved_by":"01a0b10d-f329-70d6-a423-67ff9f9184a6","dry_run_report_id":"01a0b10d-f501-793a-80c3-31f219ae307e","created_at":"2026-09-17T20:27:57.031323+00:00","builtin":false,"catalogue_id":null}
{"id":"01a0b10d-f551-73c9-8b54-ef8083e3c380","workspace_id":"01a0b10d-f2c7-7f29-8863-ee6daa940b72","slug":"rng-f8e9b7c4","version":1,"layer":"structural","check":"not_null","severity":"warn","body":{"scope": {}, "params": {"key_columns": ["policy_id"]}, "target": {"table": "policy_exposure", "column": "driv_age"}, "message": "", "rationale": "", "tolerance": {}},"status":"approved","authored_by":"01a0b10d-f2c7-78d1-8a43-628bdd866ace","approved_by":"01a0b10d-f329-70d6-a423-67ff9f9184a6","dry_run_report_id":"01a0b10d-f55f-7ea5-ad49-e0e965b36361","created_at":"2026-09-17T20:27:57.132625+00:00","builtin":false,"catalogue_id":null}
~~~~

#### `audit_events.csv`

~~~~text
id,workspace_id,at,actor,source,action,entity_ref,before,after,justification,trace_id,job_id,prev_event_hash,event_hash,sequence
01a0b10d-f204-7819-98be-cdba7dfa91b4,01a0b10d-ee00-70fe-af35-35501548dafd,2026-09-17 20:27:56.26751+00,"{""id"": ""01a0b10d-ee00-7485-a86b-8d9f6154fc92"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.created,validation_rule:rng-bf487669@1,null,"{""slug"": ""rng-bf487669"", ""check"": ""range"", ""status"": ""draft"", ""version"": 1}",,4b316190761b1de91dd1618d494b760b,,,sha256:bc49b876aec3ddbe46a6dc39bd5e22f6fb6000e5c44b510094c27d1c45c65d7d,1
01a0b10d-f25f-7f25-9314-9a241028d2d2,01a0b10d-ee00-70fe-af35-35501548dafd,2026-09-17 20:27:56.375967+00,"{""id"": ""01a0b10d-ee00-7485-a86b-8d9f6154fc92"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.submitted,validation_rule:rng-bf487669@1,"{""status"": ""draft""}","{""status"": ""review"", ""dry_run_report_id"": ""01a0b10d-f242-7dd6-9ff7-bad1d7b973aa""}",,c339866a9ff3745535138b0d2203290b,,sha256:bc49b876aec3ddbe46a6dc39bd5e22f6fb6000e5c44b510094c27d1c45c65d7d,sha256:88c83ac22a8137778eaa70e9a16c3501a27d97aecc1ada164b96f8c867b2c550,2
01a0b10d-f29e-7699-bf5f-da06a2bf443a,01a0b10d-ee00-70fe-af35-35501548dafd,2026-09-17 20:27:56.441279+00,"{""id"": ""01a0b10d-f27b-72b9-ba4e-f84d30f07079"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.approved,validation_rule:rng-bf487669@1,"{""status"": ""review""}","{""status"": ""approved"", ""approved_by"": ""01a0b10d-f27b-72b9-ba4e-f84d30f07079""}",,03360bc4658d401690c20881d818c617,,sha256:88c83ac22a8137778eaa70e9a16c3501a27d97aecc1ada164b96f8c867b2c550,sha256:6983e92d7ddd8a4c64de5b6244f2433abc9ed74d20a4adb65a0ce0cd59575165,3
01a0b10d-f4f5-728a-ada1-222d9aa52040,01a0b10d-f2c7-7f29-8863-ee6daa940b72,2026-09-17 20:27:57.031323+00,"{""id"": ""01a0b10d-f2c7-78d1-8a43-628bdd866ace"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.created,validation_rule:rng-c1c106c8@1,null,"{""slug"": ""rng-c1c106c8"", ""check"": ""range"", ""status"": ""draft"", ""version"": 1}",,0546d056cc49f70788dcc0236e5a0a66,,sha256:5fcd0fa3e8a065e653d376031be1c11699a0abbad5e900c9728da6f161762ed2,sha256:8a9b684c2910c44d451f750ab58f271aafb4b882803411af0e22c790dae17469,2
01a0b10d-f51e-7f82-aca5-720f3228eb52,01a0b10d-f2c7-7f29-8863-ee6daa940b72,2026-09-17 20:27:57.07863+00,"{""id"": ""01a0b10d-f2c7-78d1-8a43-628bdd866ace"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.submitted,validation_rule:rng-c1c106c8@1,"{""status"": ""draft""}","{""status"": ""review"", ""dry_run_report_id"": ""01a0b10d-f501-793a-80c3-31f219ae307e""}",,e1bfe5f3728dfd21d1fd4e5bafad9fae,,sha256:8a9b684c2910c44d451f750ab58f271aafb4b882803411af0e22c790dae17469,sha256:d8ec4f267a1aaf650cd91f2ecad850ec81bd9fb923768fff0302ca6ff68b277f,3
01a0b10d-f53a-77e8-a0d6-e33432e99837,01a0b10d-f2c7-7f29-8863-ee6daa940b72,2026-09-17 20:27:57.107788+00,"{""id"": ""01a0b10d-f329-70d6-a423-67ff9f9184a6"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.approved,validation_rule:rng-c1c106c8@1,"{""status"": ""review""}","{""status"": ""approved"", ""approved_by"": ""01a0b10d-f329-70d6-a423-67ff9f9184a6""}",,7daf5e5d48d12d65d0fc9b3b4e64f88c,,sha256:d8ec4f267a1aaf650cd91f2ecad850ec81bd9fb923768fff0302ca6ff68b277f,sha256:b4a10eab13e51f3842dbf35f00c5afd0966b790a9baaea2896328c9b53d840b0,4
01a0b10d-f555-77b2-98b0-eee1fb8c8037,01a0b10d-f2c7-7f29-8863-ee6daa940b72,2026-09-17 20:27:57.132625+00,"{""id"": ""01a0b10d-f2c7-78d1-8a43-628bdd866ace"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.created,validation_rule:rng-f8e9b7c4@1,null,"{""slug"": ""rng-f8e9b7c4"", ""check"": ""not_null"", ""status"": ""draft"", ""version"": 1}",,d88615a9957f7b0a50db28651dc063c4,,sha256:b4a10eab13e51f3842dbf35f00c5afd0966b790a9baaea2896328c9b53d840b0,sha256:bd7aa38d2b1256f9fac6bcd19a8d20e3e5dbab5ee4c44e2cd81d96f4a4ae48aa,5
01a0b10d-f578-7591-a036-bb1f1ded6cff,01a0b10d-f2c7-7f29-8863-ee6daa940b72,2026-09-17 20:27:57.170768+00,"{""id"": ""01a0b10d-f2c7-78d1-8a43-628bdd866ace"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.submitted,validation_rule:rng-f8e9b7c4@1,"{""status"": ""draft""}","{""status"": ""review"", ""dry_run_report_id"": ""01a0b10d-f55f-7ea5-ad49-e0e965b36361""}",,4e30fc1193f73770655e2131c892d648,,sha256:bd7aa38d2b1256f9fac6bcd19a8d20e3e5dbab5ee4c44e2cd81d96f4a4ae48aa,sha256:3c5eac1955e68a07d2d2775b493e039a3eaa5250858268a197c8a121bc2a6d35,6
01a0b10d-f592-7861-abe0-439f40713aa8,01a0b10d-f2c7-7f29-8863-ee6daa940b72,2026-09-17 20:27:57.197872+00,"{""id"": ""01a0b10d-f329-70d6-a423-67ff9f9184a6"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.approved,validation_rule:rng-f8e9b7c4@1,"{""status"": ""review""}","{""status"": ""approved"", ""approved_by"": ""01a0b10d-f329-70d6-a423-67ff9f9184a6""}",,7e594efc6180f381de33fbf886712589,,sha256:3c5eac1955e68a07d2d2775b493e039a3eaa5250858268a197c8a121bc2a6d35,sha256:9315fb962422ea9a591c1688024b85af33024c5ddf4966754bc6927f5719d123,7
01a0b10d-f81b-72c3-a028-ea4000c8d246,01a0b10d-f601-7f80-a811-d9f96b9ed567,2026-09-17 20:27:57.84206+00,"{""id"": ""01a0b10d-f601-7981-8fd3-e6439d68b787"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.created,validation_rule:rng-2f0a876d@1,null,"{""slug"": ""rng-2f0a876d"", ""check"": ""range"", ""status"": ""draft"", ""version"": 1}",,a1a18d4d6f1e31991a13f3e07ac2254e,,sha256:5b0995b34d1f736e049be4bd12d7c171796828cc6e635a13cd4ec7c880077b8d,sha256:2cf1332963ff8f0e52063868404e7af821a0657d5beb3cf4b70ad8a60e610e60,2
01a0b10d-f848-73c5-90f3-aaadbf1466ab,01a0b10d-f601-7f80-a811-d9f96b9ed567,2026-09-17 20:27:57.886977+00,"{""id"": ""01a0b10d-f601-7981-8fd3-e6439d68b787"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.submitted,validation_rule:rng-2f0a876d@1,"{""status"": ""draft""}","{""status"": ""review"", ""dry_run_report_id"": ""01a0b10d-f827-7ade-9add-3a706d90355f""}",,879196dfea1fcc73516493eb5756306d,,sha256:2cf1332963ff8f0e52063868404e7af821a0657d5beb3cf4b70ad8a60e610e60,sha256:087f3845ce9e1e7b4136f17d4c994afa25a48f5dd936255c608ab58600c4f894,3
01a0b10d-f868-7f0c-afe7-d0c6bdaed70f,01a0b10d-f601-7f80-a811-d9f96b9ed567,2026-09-17 20:27:57.91956+00,"{""id"": ""01a0b10d-f667-7f3d-98fc-d2ce538a3e60"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.approved,validation_rule:rng-2f0a876d@1,"{""status"": ""review""}","{""status"": ""approved"", ""approved_by"": ""01a0b10d-f667-7f3d-98fc-d2ce538a3e60""}",,9555fd45978508ac9afa8761f758d58b,,sha256:087f3845ce9e1e7b4136f17d4c994afa25a48f5dd936255c608ab58600c4f894,sha256:43cda224a3cd127d01f58f7d048b294b5c5ad3a68e8c2f472fd44b68517f0a69,4
01a0b10d-f89a-700a-8224-1830c09e876f,01a0b10d-f601-7f80-a811-d9f96b9ed567,2026-09-17 20:27:57.972881+00,"{""id"": ""01a0b10d-f601-7981-8fd3-e6439d68b787"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.created,validation_rule:rng-b73d354e@1,null,"{""slug"": ""rng-b73d354e"", ""check"": ""range"", ""status"": ""draft"", ""version"": 1}",,e6057a83c6329784622754e3b1acb59d,,sha256:43cda224a3cd127d01f58f7d048b294b5c5ad3a68e8c2f472fd44b68517f0a69,sha256:c004a38969823f33d732ec3422cddf5de61495592f621cfde6761eee2d93bd6e,5
01a0b10d-f8ba-7e8a-a04f-b7447689ed11,01a0b10d-f601-7f80-a811-d9f96b9ed567,2026-09-17 20:27:58.006024+00,"{""id"": ""01a0b10d-f601-7981-8fd3-e6439d68b787"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.submitted,validation_rule:rng-b73d354e@1,"{""status"": ""draft""}","{""status"": ""review"", ""dry_run_report_id"": ""01a0b10d-f8a5-7cf3-812c-d61493a5d52f""}",,aa281d6ebc2dccaaa747743e8794781f,,sha256:c004a38969823f33d732ec3422cddf5de61495592f621cfde6761eee2d93bd6e,sha256:ebcf1df74c884f6f9fe90341418928fec4ba1825c8a671772a444fe85aadc32b,6
01a0b10d-f8dd-759b-afc5-3abbf95b8c3b,01a0b10d-f601-7f80-a811-d9f96b9ed567,2026-09-17 20:27:58.036136+00,"{""id"": ""01a0b10d-f667-7f3d-98fc-d2ce538a3e60"", ""kind"": ""user"", ""display"": ""dev@localhost""}",api,validation_rule.approved,validation_rule:rng-b73d354e@1,"{""status"": ""review""}","{""status"": ""approved"", ""approved_by"": ""01a0b10d-f667-7f3d-98fc-d2ce538a3e60""}",,2f6a8381d217e7f2310a3d751f6cc5e1,,sha256:ebcf1df74c884f6f9fe90341418928fec4ba1825c8a671772a444fe85aadc32b,sha256:5028e1db6742d902ed37ac7ef507f2c79dea691a28190411d9f57ceebc044e7c,7
~~~~

#### `audit_events.jsonl`

~~~~text
{"id":"01a0b10d-f204-7819-98be-cdba7dfa91b4","workspace_id":"01a0b10d-ee00-70fe-af35-35501548dafd","at":"2026-09-17T20:27:56.26751+00:00","actor":{"id": "01a0b10d-ee00-7485-a86b-8d9f6154fc92", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.created","entity_ref":"validation_rule:rng-bf487669@1","before":null,"after":{"slug": "rng-bf487669", "check": "range", "status": "draft", "version": 1},"justification":null,"trace_id":"4b316190761b1de91dd1618d494b760b","job_id":null,"prev_event_hash":null,"event_hash":"sha256:bc49b876aec3ddbe46a6dc39bd5e22f6fb6000e5c44b510094c27d1c45c65d7d","sequence":1}
{"id":"01a0b10d-f25f-7f25-9314-9a241028d2d2","workspace_id":"01a0b10d-ee00-70fe-af35-35501548dafd","at":"2026-09-17T20:27:56.375967+00:00","actor":{"id": "01a0b10d-ee00-7485-a86b-8d9f6154fc92", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.submitted","entity_ref":"validation_rule:rng-bf487669@1","before":{"status": "draft"},"after":{"status": "review", "dry_run_report_id": "01a0b10d-f242-7dd6-9ff7-bad1d7b973aa"},"justification":null,"trace_id":"c339866a9ff3745535138b0d2203290b","job_id":null,"prev_event_hash":"sha256:bc49b876aec3ddbe46a6dc39bd5e22f6fb6000e5c44b510094c27d1c45c65d7d","event_hash":"sha256:88c83ac22a8137778eaa70e9a16c3501a27d97aecc1ada164b96f8c867b2c550","sequence":2}
{"id":"01a0b10d-f29e-7699-bf5f-da06a2bf443a","workspace_id":"01a0b10d-ee00-70fe-af35-35501548dafd","at":"2026-09-17T20:27:56.441279+00:00","actor":{"id": "01a0b10d-f27b-72b9-ba4e-f84d30f07079", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.approved","entity_ref":"validation_rule:rng-bf487669@1","before":{"status": "review"},"after":{"status": "approved", "approved_by": "01a0b10d-f27b-72b9-ba4e-f84d30f07079"},"justification":null,"trace_id":"03360bc4658d401690c20881d818c617","job_id":null,"prev_event_hash":"sha256:88c83ac22a8137778eaa70e9a16c3501a27d97aecc1ada164b96f8c867b2c550","event_hash":"sha256:6983e92d7ddd8a4c64de5b6244f2433abc9ed74d20a4adb65a0ce0cd59575165","sequence":3}
{"id":"01a0b10d-f4f5-728a-ada1-222d9aa52040","workspace_id":"01a0b10d-f2c7-7f29-8863-ee6daa940b72","at":"2026-09-17T20:27:57.031323+00:00","actor":{"id": "01a0b10d-f2c7-78d1-8a43-628bdd866ace", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.created","entity_ref":"validation_rule:rng-c1c106c8@1","before":null,"after":{"slug": "rng-c1c106c8", "check": "range", "status": "draft", "version": 1},"justification":null,"trace_id":"0546d056cc49f70788dcc0236e5a0a66","job_id":null,"prev_event_hash":"sha256:5fcd0fa3e8a065e653d376031be1c11699a0abbad5e900c9728da6f161762ed2","event_hash":"sha256:8a9b684c2910c44d451f750ab58f271aafb4b882803411af0e22c790dae17469","sequence":2}
{"id":"01a0b10d-f51e-7f82-aca5-720f3228eb52","workspace_id":"01a0b10d-f2c7-7f29-8863-ee6daa940b72","at":"2026-09-17T20:27:57.07863+00:00","actor":{"id": "01a0b10d-f2c7-78d1-8a43-628bdd866ace", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.submitted","entity_ref":"validation_rule:rng-c1c106c8@1","before":{"status": "draft"},"after":{"status": "review", "dry_run_report_id": "01a0b10d-f501-793a-80c3-31f219ae307e"},"justification":null,"trace_id":"e1bfe5f3728dfd21d1fd4e5bafad9fae","job_id":null,"prev_event_hash":"sha256:8a9b684c2910c44d451f750ab58f271aafb4b882803411af0e22c790dae17469","event_hash":"sha256:d8ec4f267a1aaf650cd91f2ecad850ec81bd9fb923768fff0302ca6ff68b277f","sequence":3}
{"id":"01a0b10d-f53a-77e8-a0d6-e33432e99837","workspace_id":"01a0b10d-f2c7-7f29-8863-ee6daa940b72","at":"2026-09-17T20:27:57.107788+00:00","actor":{"id": "01a0b10d-f329-70d6-a423-67ff9f9184a6", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.approved","entity_ref":"validation_rule:rng-c1c106c8@1","before":{"status": "review"},"after":{"status": "approved", "approved_by": "01a0b10d-f329-70d6-a423-67ff9f9184a6"},"justification":null,"trace_id":"7daf5e5d48d12d65d0fc9b3b4e64f88c","job_id":null,"prev_event_hash":"sha256:d8ec4f267a1aaf650cd91f2ecad850ec81bd9fb923768fff0302ca6ff68b277f","event_hash":"sha256:b4a10eab13e51f3842dbf35f00c5afd0966b790a9baaea2896328c9b53d840b0","sequence":4}
{"id":"01a0b10d-f555-77b2-98b0-eee1fb8c8037","workspace_id":"01a0b10d-f2c7-7f29-8863-ee6daa940b72","at":"2026-09-17T20:27:57.132625+00:00","actor":{"id": "01a0b10d-f2c7-78d1-8a43-628bdd866ace", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.created","entity_ref":"validation_rule:rng-f8e9b7c4@1","before":null,"after":{"slug": "rng-f8e9b7c4", "check": "not_null", "status": "draft", "version": 1},"justification":null,"trace_id":"d88615a9957f7b0a50db28651dc063c4","job_id":null,"prev_event_hash":"sha256:b4a10eab13e51f3842dbf35f00c5afd0966b790a9baaea2896328c9b53d840b0","event_hash":"sha256:bd7aa38d2b1256f9fac6bcd19a8d20e3e5dbab5ee4c44e2cd81d96f4a4ae48aa","sequence":5}
{"id":"01a0b10d-f578-7591-a036-bb1f1ded6cff","workspace_id":"01a0b10d-f2c7-7f29-8863-ee6daa940b72","at":"2026-09-17T20:27:57.170768+00:00","actor":{"id": "01a0b10d-f2c7-78d1-8a43-628bdd866ace", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.submitted","entity_ref":"validation_rule:rng-f8e9b7c4@1","before":{"status": "draft"},"after":{"status": "review", "dry_run_report_id": "01a0b10d-f55f-7ea5-ad49-e0e965b36361"},"justification":null,"trace_id":"4e30fc1193f73770655e2131c892d648","job_id":null,"prev_event_hash":"sha256:bd7aa38d2b1256f9fac6bcd19a8d20e3e5dbab5ee4c44e2cd81d96f4a4ae48aa","event_hash":"sha256:3c5eac1955e68a07d2d2775b493e039a3eaa5250858268a197c8a121bc2a6d35","sequence":6}
{"id":"01a0b10d-f592-7861-abe0-439f40713aa8","workspace_id":"01a0b10d-f2c7-7f29-8863-ee6daa940b72","at":"2026-09-17T20:27:57.197872+00:00","actor":{"id": "01a0b10d-f329-70d6-a423-67ff9f9184a6", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.approved","entity_ref":"validation_rule:rng-f8e9b7c4@1","before":{"status": "review"},"after":{"status": "approved", "approved_by": "01a0b10d-f329-70d6-a423-67ff9f9184a6"},"justification":null,"trace_id":"7e594efc6180f381de33fbf886712589","job_id":null,"prev_event_hash":"sha256:3c5eac1955e68a07d2d2775b493e039a3eaa5250858268a197c8a121bc2a6d35","event_hash":"sha256:9315fb962422ea9a591c1688024b85af33024c5ddf4966754bc6927f5719d123","sequence":7}
{"id":"01a0b10d-f81b-72c3-a028-ea4000c8d246","workspace_id":"01a0b10d-f601-7f80-a811-d9f96b9ed567","at":"2026-09-17T20:27:57.84206+00:00","actor":{"id": "01a0b10d-f601-7981-8fd3-e6439d68b787", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.created","entity_ref":"validation_rule:rng-2f0a876d@1","before":null,"after":{"slug": "rng-2f0a876d", "check": "range", "status": "draft", "version": 1},"justification":null,"trace_id":"a1a18d4d6f1e31991a13f3e07ac2254e","job_id":null,"prev_event_hash":"sha256:5b0995b34d1f736e049be4bd12d7c171796828cc6e635a13cd4ec7c880077b8d","event_hash":"sha256:2cf1332963ff8f0e52063868404e7af821a0657d5beb3cf4b70ad8a60e610e60","sequence":2}
{"id":"01a0b10d-f848-73c5-90f3-aaadbf1466ab","workspace_id":"01a0b10d-f601-7f80-a811-d9f96b9ed567","at":"2026-09-17T20:27:57.886977+00:00","actor":{"id": "01a0b10d-f601-7981-8fd3-e6439d68b787", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.submitted","entity_ref":"validation_rule:rng-2f0a876d@1","before":{"status": "draft"},"after":{"status": "review", "dry_run_report_id": "01a0b10d-f827-7ade-9add-3a706d90355f"},"justification":null,"trace_id":"879196dfea1fcc73516493eb5756306d","job_id":null,"prev_event_hash":"sha256:2cf1332963ff8f0e52063868404e7af821a0657d5beb3cf4b70ad8a60e610e60","event_hash":"sha256:087f3845ce9e1e7b4136f17d4c994afa25a48f5dd936255c608ab58600c4f894","sequence":3}
{"id":"01a0b10d-f868-7f0c-afe7-d0c6bdaed70f","workspace_id":"01a0b10d-f601-7f80-a811-d9f96b9ed567","at":"2026-09-17T20:27:57.91956+00:00","actor":{"id": "01a0b10d-f667-7f3d-98fc-d2ce538a3e60", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.approved","entity_ref":"validation_rule:rng-2f0a876d@1","before":{"status": "review"},"after":{"status": "approved", "approved_by": "01a0b10d-f667-7f3d-98fc-d2ce538a3e60"},"justification":null,"trace_id":"9555fd45978508ac9afa8761f758d58b","job_id":null,"prev_event_hash":"sha256:087f3845ce9e1e7b4136f17d4c994afa25a48f5dd936255c608ab58600c4f894","event_hash":"sha256:43cda224a3cd127d01f58f7d048b294b5c5ad3a68e8c2f472fd44b68517f0a69","sequence":4}
{"id":"01a0b10d-f89a-700a-8224-1830c09e876f","workspace_id":"01a0b10d-f601-7f80-a811-d9f96b9ed567","at":"2026-09-17T20:27:57.972881+00:00","actor":{"id": "01a0b10d-f601-7981-8fd3-e6439d68b787", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.created","entity_ref":"validation_rule:rng-b73d354e@1","before":null,"after":{"slug": "rng-b73d354e", "check": "range", "status": "draft", "version": 1},"justification":null,"trace_id":"e6057a83c6329784622754e3b1acb59d","job_id":null,"prev_event_hash":"sha256:43cda224a3cd127d01f58f7d048b294b5c5ad3a68e8c2f472fd44b68517f0a69","event_hash":"sha256:c004a38969823f33d732ec3422cddf5de61495592f621cfde6761eee2d93bd6e","sequence":5}
{"id":"01a0b10d-f8ba-7e8a-a04f-b7447689ed11","workspace_id":"01a0b10d-f601-7f80-a811-d9f96b9ed567","at":"2026-09-17T20:27:58.006024+00:00","actor":{"id": "01a0b10d-f601-7981-8fd3-e6439d68b787", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.submitted","entity_ref":"validation_rule:rng-b73d354e@1","before":{"status": "draft"},"after":{"status": "review", "dry_run_report_id": "01a0b10d-f8a5-7cf3-812c-d61493a5d52f"},"justification":null,"trace_id":"aa281d6ebc2dccaaa747743e8794781f","job_id":null,"prev_event_hash":"sha256:c004a38969823f33d732ec3422cddf5de61495592f621cfde6761eee2d93bd6e","event_hash":"sha256:ebcf1df74c884f6f9fe90341418928fec4ba1825c8a671772a444fe85aadc32b","sequence":6}
{"id":"01a0b10d-f8dd-759b-afc5-3abbf95b8c3b","workspace_id":"01a0b10d-f601-7f80-a811-d9f96b9ed567","at":"2026-09-17T20:27:58.036136+00:00","actor":{"id": "01a0b10d-f667-7f3d-98fc-d2ce538a3e60", "kind": "user", "display": "dev@localhost"},"source":"api","action":"validation_rule.approved","entity_ref":"validation_rule:rng-b73d354e@1","before":{"status": "review"},"after":{"status": "approved", "approved_by": "01a0b10d-f667-7f3d-98fc-d2ce538a3e60"},"justification":null,"trace_id":"2f6a8381d217e7f2310a3d751f6cc5e1","job_id":null,"prev_event_hash":"sha256:ebcf1df74c884f6f9fe90341418928fec4ba1825c8a671772a444fe85aadc32b","event_hash":"sha256:5028e1db6742d902ed37ac7ef507f2c79dea691a28190411d9f57ceebc044e7c","sequence":7}
~~~~

## PRs

Not yet opened (the lead decides when).
