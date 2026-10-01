---
id: PL-9762
family: plan
kind: leaf
title: WK-1178 — FD-1356 fix, validation-rule approval through the approval workflow (FR-50, FR-351, FR-353, FR-354, FR-355, FR-363): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-01
owner: planner
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1356, RL-1301, PL-1303, PL-1306, SL-1256, SL-1302, RL-1263, FD-1357, PL-1359, SL-1360, PL-1364, RL-1365, SL-1367]
---

# PL 9762 (working id) — WK-1178: the FD-1356 fix, validation-rule approval through the approval workflow, leaf plan

Filed under working id 9762 (this plan) and slice working id 9761 (its `SL-` row under
WK-1178 in [`../roadmap.md`](../roadmap.md), `draft`), both reserved by the lead. Both are
minted at the plan PR's merge turn. Unminted ids are cited in working-id form in prose and
are kept out of `relates:` (check 32).

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item is seen red, by its cause, before
> the code that turns it green), `fastapi-service` (Tasks 3 and 4), `contract-schema` and
> `contract-guard` (Task 4's typed bodies and the regenerated contract), `vue-frontend`
> (Task 5, only under DP-2 (a)), `spec-change` (Task 6, only where a ruling carries text),
> `dev-commands` (the two-half gate, the alembic DSN) and `git-hygiene`. Read
> [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

## Goal

A Validation Rule reaches `approved` only through `06`'s approval workflow:
`approvals.submit` creates the request, `approvals.decide` records each decision against the
workspace's Approval Policy, and `_carry_to_the_artifact` moves the rule. The direct
`POST /api/v1/validation-rules/{id}/approve` route stops writing `approved` itself. A rule whose
dry-run outcome is `error` is refused at submit and at approve. A `fail` outcome stays
accepted. This discharges `FD-1356` (HIGH, WK-1178).

**Architecture:** the rule's module keeps its own lifecycle and gains the two seams every
other approvable type already has: a module submit that calls `approvals.submit`
(`objectives.submit_for_review`, `backend/src/app/platform/objectives.py:558-618`, is the
model), and an `apply_approval_decision` that `_carry_to_the_artifact` drives
(`objectives.apply_approval_decision`, `:621-690`). One helper, `_require_executed_dry_run`,
reads the attached report's outcome and is called at the module submit, at the generic
submit's resolver and at the carry. The direct route becomes a thin client of the decide
path, or is removed (DP-1). The temporary allowance that let `approve_rule` write `approved`
outside the decision path (`RL-1301` A.4.5) is removed, red first.

**Tech Stack:** Python 3.12, FastAPI + Pydantic v2, SQLAlchemy 2 async, PostgreSQL 16
(the `approval_guard()` trigger of migration `a9f3c6d21b87`), Alembic, pytest; Vue 3 +
the generated API client (Task 5 only).

**Spec, finding and rulings:**
- `docs/findings/FD-01356-a-validation-rule-is-approved-by-its-own-route-outside-the-approval-workflow-so-policy-quorum-and-the-uniform-decision-path-do-not-apply.md`,
  §"Disposition" ("Scope and acceptance, red first", and "Follow-ons"). **That section is
  this slice's scope**;
- [`../specs/06-governance.md`](../specs/06-governance.md) §3.1 (FR-351, FR-352, FR-353,
  FR-354, FR-355), §3.3 (FR-363 and its evidence table, `06:114`), §4.2, FR-386;
- [`../specs/01-data-management.md`](../specs/01-data-management.md) FR-48, FR-50, FR-68,
  §4.5 "Governance of custom rules" steps 1–4 (`01:520-523`), the vocabulary paragraph
  (`01:470-474`), §5.1's two rule routes (`01:878-879`) and the dated note at `01:919-927`;
- `docs/rulings/RL-01301-wk-674-slice-2-dp-s2-2-and-dp-s2-3-decided-a-deployment-request-owns-its-pinned-evidence-and-deployment-promote-takes-an-environment-scope.md`
  item A.4, sub-items 2, 5, 6 and 9 (the trigger, the allowance, the fixtures, the order).

## The maintainer's decisions this plan rests on, quoted

From the maintainer's entries of 2026-10-01, about 10:10 BST, as relayed by the lead:

> "Decision: (b) S2 → FD-1356 fix. This SUPERSEDES item 1 of my '2026-09-30 11:56:33 BST'
> entry … The two are serial (approvals.py). FD-1356's minted Disposition is correct again."

> "Containment: the FD-1356 fix plan's Task 0 = a query over every gipricing* DB counting VR
> versions approved via the self-approval route (expect 0), re-run before the exit demo and
> recorded in its checklist; > 0 = stop."

> "the FD-1356 fix plan instead carries 'WK-674 S2 merged' as its own activation need."

So the order is WK-674 Slice 2a (`SL-1302`, closed) → **WK-674 Slice 2 (`SL-1256`)** → this
slice. `PL-1306` §"Write set" (`:511`) still states the superseded order "S2a → the fix → S2".
It is frozen, and the superseding S2 plan, PL 9765 (working id), carries the new order. This
plan does not edit `PL-1306`.

## Status

`draft`. **Blocking decision points are open** (§"Decision points": DP-1, DP-2, DP-3's open
part, DP-5 and DP-6). DP-0 and DP-4 are decided by the maintainer (dated 2026-10-01; the
entries are quoted in their rows). The plan
moves to `active` only through a separate activation PR, after every activation need below
holds. That PR carries the `SL-` row's status flip and this plan's.

### Activation needs, in order

1. **WK-674 S2 (`SL-1256`) merged** on `main` (the maintainer, above). Both slices edit
   `backend/src/app/api/approvals.py` (`_carry_to_the_artifact`), and S2 also edits
   `submit_for_approval`, `Withdraw` and `_resolve_the_artifact` there; they serialise under
   `RL-1263`.
2. **Lane B order:** `SL-1360` (the permission-parity check, `PL-1359`) merged, then the
   FD-1357 fix (PL 9764, working id) merged. This slice is third in lane B, before the
   `RL-1343` decimal-output fix and `PL-1364` (FD-1335 Part A, minted at `92b4e4ac` with `RL-1365` and `SL-1367`).
3. **DP-1, DP-2, DP-3 (its open part), DP-5 and DP-6 ruled**, each by its owner in
   §"Decision points", as dated records.
4. **Task 0's containment query prints `TOTAL route_approved=0`, re-confirmed at dispatch.**
   It printed **5** at planning time (§"Task 0 at planning time"). DP-0 is decided as (c):
   the 5 rows and their audit events are exported verbatim with their provenance evidence,
   then the scratch database is dropped, then Task 0 is re-run and must print 0. auditor-dp0
   is executing that into
   `/home/puzhenhao1989/gi-pricing-plan.local/handover/fd1356-dp0-export-2026-10-01/`.
5. **The maintainer's agreement**, and **the lead's go in a separate activation PR**.

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red
first" means the named test was run and failed **for the stated cause** before the code that
turns it green; a failure with the right status and a different cause is a plan defect
([`README.md`](README.md) rule 2). Each red is recorded in the slice's ledger, with the
failure line as printed.

1. **Containment (Task 0).** `bash` of the Task 0 script exits 0 and its last line reads
   `TOTAL route_approved=0`, at dispatch and again before the P2 exit demo (Hand-off item 2).
   The two runs are recorded in the ledger with their timestamps (BST) and the database count,
   and the DP-0 export is quoted verbatim in the ledger (Task 0 Step 2).
2. **Quorum 2 (FD-1356 case 4 becomes a refusal).** With the workspace policy's
   `validation_rule` entry at `approvers_required=2`, one approver's approval leaves the rule
   in `review` and the request in `review`; a second, distinct approver's approval moves both
   to `approved`, with `approved_by` set to the second approver. Test:
   `test_a_decision_moves_the_version_as_fr_355_says_and_records_it_truly[first_of_two-validation_rule]`
   and `[approve-validation_rule]` in `backend/tests/test_api_approvals.py`, and
   `test_one_approval_under_a_quorum_of_two_leaves_the_rule_in_review` (thin-client route,
   DP-1 (b)) in the new module. Red first on the base tree: the direct route approves on one
   approval.
3. **The generic decide carries (FD-1356 case 5).** `POST /approval-requests` then another
   approver's `POST /approval-requests/{id}/decide` moves the rule to `approved`; reject and
   request-changes move it to `draft` (FR-355, pre-submission state, `01` §4.5 step 1). Test:
   the four `validation_rule` cases of
   `test_a_decision_moves_the_version_as_fr_355_says_and_records_it_truly`, after `_AFTER`
   and `_MOVE_ACTION` gain the rule's row (Task 2). Red first: `_AFTER["validation_rule"]` is
   `dict.fromkeys(_OUTCOMES, "review")` at `1dd5e264`, the reverse gap pinned as behaviour.
4. **The direct route no longer writes `approved` (FD-1356 case 3 inverted).** Under DP-1
   (b): every `approved` reached through `POST /validation-rules/{id}/approve` has an
   `approval_decisions` row and an `approved` `approval_requests` row for its ref, and the
   route returns `409 APPROVAL_SUBJECT_NOT_IN_REVIEW` for a rule with no open request. Under
   DP-1 (a): the path is absent from `app.openapi()["paths"]` and a call returns 404 or 405.
   Test: `test_the_approve_route_decides_through_the_workflow` (or
   `test_the_approve_route_is_gone`). Red first: on the base tree the route approves with 0
   `approval_requests` rows.
5. **An `error` dry-run is refused at submit, one case per cause.** A real `DATASET_VALIDATE`
   dry-run job (`dry_run_rule_id`) gives each of a `range` rule on `no_such_column`, a rule
   with `check: no_such_check` and a rule targeting table `no_such_table` an attached report
   with `error_count > 0`; `POST /validation-rules/{id}/submit` then answers `422
   EVIDENCE_INCOMPLETE` (DP-3's code) and the rule stays `draft`. Test:
   `test_an_error_dry_run_is_refused_at_submit[missing_column|unknown_check|missing_table]`.
   Red first on the base tree: each submit returns 200 `review` (FD-1356's measured table).
6. **An `error` dry-run is refused at approve, one case per cause.** The same three rules,
   each put in `review` with an open request by test-only writes (the path a pre-fix rule
   takes), are refused at decide with `422 EVIDENCE_INCOMPLETE`; the rule stays `review`,
   the request stays `review`, and no `approval_decisions` row survives (the decision rolls
   back with the carry). Test:
   `test_an_error_dry_run_is_refused_at_approve[missing_column|unknown_check|missing_table]`,
   which drives the generic `POST /approval-requests/{id}/decide`. Red first, by its cause: on
   the base tree decide returns `200` and the rule **stays `review`** (the carry has no
   validation-rule branch, FD-1356 case 5), so each case fails on its status-code assertion
   (`422` expected, `200` received) with the request moved to `approved`. A failure because
   the rule became `approved` would mean the test drove the direct route: a test defect.
7. **A `fail` dry-run stays accepted (the measured non-defect).** A `range` rule
   (`min_exclusive: 0`, severity `fail`) dry-run on a version with one negative
   `exposure_years` gets a report with `overall` `fail` and `error_count` 0; submit gives
   `review`, and a second approver's decision gives `approved`. Test:
   `test_a_fail_dry_run_is_still_approvable`. It passes on the base tree too; it is the
   control that the refusal reads `error`, not `fail`.
8. **The generic submit enforces the same floor.** A rule in `review` whose attached report
   has `error_count > 0` is refused at `POST /approval-requests` with `422
   EVIDENCE_INCOMPLETE` (FR-363 "enforced at submission"). Test:
   `test_the_generic_submit_refuses_an_error_dry_run`. Red first: 201 on the base tree.
9. **A dangling report id fails closed (DP-3's open part; scope growth beyond FD-1356, only
   if the decision-maker rules it in).** A rule whose `dry_run_report_id` names no
   `validation_reports` row in its workspace is refused at submit with `422
   EVIDENCE_INCOMPLETE`. Test: `test_a_dry_run_report_that_cannot_be_read_is_refused`. Red
   first: 200 on the base tree (the existing tests attach `new_uuid7()` and pass).
10. **The temporary allowance is removed, red first.** `("backend/src/app/platform/validation_rules.py",
    "approve_rule")` is gone from `ALLOWANCE_SITES` (`backend/tests/test_approval_guard_static.py:40`),
    with its comment line `:39` reduced to the `replace_rule_set` entry it still covers;
    `test_approve_rule_writes_approved_only_through_its_entry`
    (`backend/tests/test_approval_guard_allowance.py:159-176`) is deleted with the function it
    tests, or rewritten to the thin client's no-flag behaviour. Red first (Task 1 Step 2):
    with the literal edited and the code not, `test_approval_decision_is_entered_only_at_the_sanctioned_and_allowance_sites`
    fails naming exactly `backend/src/app/platform/validation_rules.py::approve_rule`. After
    Task 3, `git grep -n 'approval_decision' -- backend/src/app/platform/validation_rules.py`
    prints the `seed_builtin_rules` and `replace_rule_set` sites only.
11. **Separation of duties holds on the new path.** The rule's author deciding on a request
    they submitted gets `403 SUBMITTER_CANNOT_APPROVE`; the author deciding on a request
    someone else submitted gets `403 AUTHOR_CANNOT_APPROVE` (`06` FR-353, through the
    `validation_rule.created` event, `platform/approvals.py` `CREATION_ACTIONS`). The existing
    `test_a_rule_walks_draft_to_approved_and_never_by_its_author`
    (`backend/tests/test_api_datasets.py:603-676`) is updated from 409 to 403 under DP-1 (b),
    which is a wire change the DP-1 ruling must accept by name.
12. **The carry's audit event names its request.** The `validation_rule.approved` event that
    `apply_approval_decision` records has `after.approval_request_id`. Task 0's predicate
    relies on it to tell a workflow approval from a direct-route one after the fix. Test:
    `test_the_carry_records_the_request_it_carried`.
13. **The data reset (FD-1356 follow-on 2).** After `alembic upgrade head` (DP-6 (a)), FD-1356's
    own follow-on predicate (its runnable script, unchanged) prints, on the database named
    `gipricing`, `user_approved_with_no_approved_request=0`, and its `builtin_approved` figure
    equals the figure it printed before the upgrade. The count reset is recorded in the
    ledger with the database list and the timestamp.
14. **The fixtures carry the evidence.** `backend/tests/approved_rows.py` maps
    `ValidationRuleRow` to `("validation_rule", "slug")` in `_EVIDENCE` and no longer lists it
    in `_FLAG_ONLY`, so every fixture-approved rule has a decided request. Test: the whole
    backend suite passes with it.
15. **Every request body this slice edits is typed; decide's `200` is characterised, not
    typed** (DP-4, decided by the maintainer: "2026-10-01 10:34:13 BST — The DP-S2-6 header for quoting; #1063 DP-0 HELD until auditor-1063's provenance check (and the evidence rule if (c)); DP-4 (a) accepted; status noted",
    which says to "type decide_request's BODY in this slice; its 200 goes to FD 9752 / FD-1335
    Part B with a key-set characterisation test". Under WK-674 S2's DP-S2-6 (c), "2026-10-01 10:32:26 BST — #1062 DP-S2-6: option (c) ACCEPTED with three conditions; it narrows my item (3) for the 2 CHANGED routes' 2xx only; the three-shape disagreement becomes its own FD",
    no approval route's 2xx is `$ref`-typed; FD 9752 (working id, #1066) owns that 2xx.)
    The typing rule comes from the lead's holds register,
    `holds-2026-10-01.md`, `FD-1366` per-route rule (filed as FD 9779) as made precise by the maintainer, and `FD-1366`'s
    dispatch line "every new or changed JSON route has typed request and 2xx response
    schemas"), limbed by DP-4 for the approval routes:
    - **Bodies.** For each route in §"Write set" marked "edited" that takes a JSON body
      (`POST /api/v1/validation-rules/{rule_id}/submit` under DP-2 (a), and
      `POST /api/v1/approval-requests/{request_id}/decide`), `app.openapi()` shows the request
      body as a `$ref` to a `model-schema` type, never `{}` or an open object. `Decide` moves
      from `backend/src/app/api/approvals.py:83-87` into `model-schema`. Test:
      `test_every_body_this_slice_edits_is_a_model_schema_type`, red first on decide's body
      (a `$ref` to the route-local `Decide`, which is not a `model-schema` name) and, under
      DP-2 (a), on the submit's absent body.
    - **Non-approval 2xx.** The rule routes this slice edits keep their `ValidationRule` 2xx,
      a `$ref` to a `model-schema` type (unchanged at `1dd5e264`).
    - **Decide's `200` is characterised, not typed.**
      `test_the_decide_response_keeps_its_key_set` asserts the exact set of top-level keys of
      decide's `200` body against a literal set read at the dispatch tree, and fails on any
      undeclared addition, removal or rename. Red first: with one key renamed in a scratch
      copy of `service.to_dict` (`backend/src/app/platform/approvals.py:648`), the test fails
      naming both the missing and the unexpected key; the edit is reverted. Typing that `200`
      is FD 9752's (working id, #1066), not this slice's.
16. **The built-in exemption is named, not silent.** `seed_builtin_rules` is unchanged and
    keeps its `ALLOWANCE_SITES` entry (`01` FR-68; FD-1356 §"Triage"). A workspace's built-in
    rules are `approved` with no request, and the data reset of item 13 leaves them so.
17. **The full two-half gate of `CLAUDE.md` §11 exits 0 on the merge tree**, each command's
    rc recorded: `uv run ruff check .`, `uv run mypy`, `uv run lint-imports`,
    `uv run pytest -q`, `python3 scripts/audit-docs.py`,
    `uv run python scripts/req-coverage.py`,
    `uv run python scripts/generate-contracts.py --check`, and the five `pnpm --dir frontend`
    commands.
18. **`git diff --stat origin/main...HEAD` names only the files of §"Write set"** that the
    ruled DP options select, plus the ledger and `docs/INDEX.md`.

## Global Constraints

- **Money and maths are untouched**; this slice changes governance only.
- **No pandas** (`CLAUDE.md` §3).
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2); a new
  request body is a `model-schema` type (Acceptance 15), and the frontend uses the generated
  client type for it, never a hand-written one (`CLAUDE.md` §3).
- **The approval guard is preserved** (`RL-1301` A.4): the carry writes `approved` inside
  `_carry_to_the_artifact`'s existing `approval_decision()` block, one of the two sanctioned
  sites; no new site enters `approval_decision()`; the literal `app.approval_decision` is
  named nowhere new.
- **Built-in rules stay exempt by `01` FR-68 only** (`01:169`), and no `06` clause is cited
  for them.
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13): Acceptance 2–6,
  8–10 and 15 are each red first.
- **Shared files** (`RL-1263` option (c)): two concurrent build slices may not both change the
  same existing function, class, spec section or policy table. `docs/INDEX.md` and
  `backend/migrations/versions/` are registries: regenerate or append, never hand-merge.
- **No spec text is written by this slice unless a ruling carries it verbatim** (Task 6).

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `01` | FR-50 | A custom rule's `draft → review → approved` runs through the workflow; the dry-run must have executed (§4.5 step 2) | `req("FR-50")` on Acceptance 5–9 tests |
| `01` | FR-48 | An `error` outcome is not a pass: it blocks approval | `req("FR-48")` on Acceptance 5, 6 |
| `01` | FR-68 | Built-ins stay seeded `approved`, exempt (Acceptance 16) | existing tests; no new marker |
| `06` | FR-351 | One uniform lifecycle; only `decide` + the carry move a rule to `approved` | `req("FR-351")` on Acceptance 3, 4, 10 |
| `06` | FR-352 | Submission carries a change summary (DP-2) | `req("FR-352")` on the module-submit test |
| `06` | FR-353 | Submitter and author cannot decide | `req("FR-353")` on Acceptance 11 |
| `06` | FR-354 | The policy's approver count binds a rule | `req("FR-354")` on Acceptance 2 |
| `06` | FR-355 | Non-approvals return the rule to `draft` | `req("FR-355")` on Acceptance 3 |
| `06` | FR-363 | The `dry_run_result` evidence means a run that executed; enforced at submission | `req("FR-363")` on Acceptance 5, 8, 9 |
| `06` | FR-386 | The generic submit's resolver still refuses a missing version (unchanged; regression only) | existing tests |

### Task 0 at planning time (measured, not asserted)

Run by this plan's author at `2026-10-01 10:23:33 BST`, against the compose server
`gi-pricing-postgres-1` (`docker ps`: up 36 hours). This run used the script's first form,
at `46dea9a4`: it matched **any** `validation_rule.approved` event without
`approval_request_id`, not only the latest one. Otherwise the script is the same as Task 0
Step 1's. Output, verbatim:

```text
gipricing route_approved=0 self_approved=0 user_approved_no_approved_request=10
gipricing_clone_m2 no_table_or_error
gipricing_tree-s3 route_approved=0 self_approved=0 user_approved_no_approved_request=10
gipricing_w37-6-run2 no_table_or_error
gipricing_w37-6-run2-gate-1789676768 route_approved=5 self_approved=0 user_approved_no_approved_request=15
gipricing_w37-6-run2-gate-1789690960 route_approved=0 self_approved=0 user_approved_no_approved_request=10
gipricing_w37_6_d7_g_executor no_table_or_error
gipricing_wt-d9d13-redo route_approved=0 self_approved=0 user_approved_no_approved_request=101
gipricing_wt-paths-d9-d13 route_approved=0 self_approved=0 user_approved_no_approved_request=183
databases=81 with_tables=78 without_table_or_error=3
TOTAL route_approved=5 self_approved=0 user_approved_no_approved_request=329
STOP: route_approved > 0
```

- **The 3 `no_table_or_error` databases are empty**: `select count(*) from pg_tables where
  schemaname='public'` printed `0` for `gipricing_w37-6-run2` and
  `gipricing_w37_6_d7_g_executor`, and the three-table probe printed nothing for
  `gipricing_clone_m2`. They are "no table", not errors.
- **The 5 rows**, read with
  `select v.slug, v.version, v.workspace_id, e.at, e.actor->>'id', e.source from validation_rules v join audit_events e on e.workspace_id=v.workspace_id and e.action='validation_rule.approved' and e.entity_ref='validation_rule:'||v.slug||'@'||v.version where v.status='approved' and v.builtin is not true order by e.at`
  in `gipricing_w37-6-run2-gate-1789676768`, are slugs `rng-bf487669`, `rng-c1c106c8`,
  `rng-f8e9b7c4`, `rng-2f0a876d` and `rng-b73d354e`, version 1, in three workspaces, source
  `api`, all between `2026-09-17 20:27:56` and `20:27:58` UTC. The `rng-<8 hex>` slug is the
  form `test_api_datasets.py`'s `_approved_rule` and its chain test author (`:628`, `:685`),
  and that database's name is a W37-6 gate run's. **So they read as test-run residue in a
  scratch gate database. That is an inference from the slug, the timing and the name, not a
  provenance check.**
- **`self_approved=0` everywhere**, as the DB check `approved_rule_dry_run_and_separate_approver`
  (`backend/src/app/db/models.py:1201-1205`) requires.
- **The STOP fired.** The maintainer expected 0. This plan did not narrow the population or
  the predicate to make it pass. The maintainer decided DP-0 as (c) (its row).
- **Re-run with the revised predicate** (Task 0 Step 1 as it now stands: each rule judged by
  its **latest** `validation_rule.approved` event, auditor-1063's finding 2), finished at about
  `2026-10-01 10:41:59 BST`, after `gipricing_w37-6-run2-gate-1789676768` had already been
  dropped under DP-0 (c):

```text
gipricing route_approved=0 self_approved=0 user_approved_no_approved_request=10
gipricing_clone_m2 no_table_or_error
gipricing_tree-s3 route_approved=0 self_approved=0 user_approved_no_approved_request=10
gipricing_w37-6-run2 no_table_or_error
gipricing_w37-6-run2-gate-1789690960 route_approved=0 self_approved=0 user_approved_no_approved_request=10
gipricing_w37_6_d7_g_executor no_table_or_error
gipricing_wt-d9d13-redo route_approved=0 self_approved=0 user_approved_no_approved_request=101
gipricing_wt-paths-d9-d13 route_approved=0 self_approved=0 user_approved_no_approved_request=183
databases=80 with_tables=77 without_table_or_error=3
TOTAL route_approved=0 self_approved=0 user_approved_no_approved_request=314
```

  **What this does and does not show.** The revised predicate was not run while the 5 rows
  existed, so it was not seen to count them. By reading: the join query above returned one
  event per rule for the 5 (5 rows for 5 refs), so each rule's latest approval event was a
  direct-route one with no `approval_request_id`, and the revised predicate counts each. The
  re-confirmation at dispatch (activation need 4) is the binding run.

### Write set, and its contention (`RL-1263`)

"Edited" means an existing definition changes; "added" means a new definition in an existing
file. Rows marked *(DP-n x)* exist only under that option.

| Path | Change | Other slices touching it | Consequence |
|---|---|---|---|
| `backend/src/app/platform/validation_rules.py` | edited: `submit_for_review` (`:366-400`), `resolve_artifact_ref` (`:317-349`), `__all__`; removed: `approve_rule` (`:403-447`) under DP-1 (b) or (a); added: `_require_executed_dry_run`, `apply_approval_decision`, `open_request_for` *(DP-1 b)* | none in flight (`PL-1306` reads `:192`, `:199` only) | none |
| `backend/src/app/api/approvals.py` | edited: `_carry_to_the_artifact` (`:488-523`, one call added), `decide_request` (`:232-270`: its body calls the new helper, and its request body is the `model-schema` `Decide` type, DP-4 decided; its `200` stays as it is, owned by FD 9752); removed: the route-local class `Decide` (`:83-87`); added: `decide_and_carry` | **WK-674 S2** edits `_carry_to_the_artifact` (deployment call), `submit_for_approval`, `Withdraw`, `withdraw_request`, `_resolve_the_artifact` (`PL-1306` `:511-515`; PL 9765, working id) | **serial: S2 first** (activation need 1). This slice rebases on S2's merge and re-reads the file |
| `backend/src/app/platform/approvals.py` | **read only.** No function here changes | WK-674 S2 (`set_policy`, A.6) | none. If the executor finds a change is needed here, that is a replan trigger to the lead, not a silent widening |
| `backend/src/app/api/validation.py` | edited: `approve_rule` route (`:354-380`, thin client) *(DP-1 b)* or removed *(DP-1 a)*; `submit_rule` (`:335-351`, typed body) *(DP-2 a)* | none found | none |
| `packages/model-schema/src/model_schema/validation.py`, `__init__.py` | added: `ValidationRuleSubmission` *(DP-2 a)* | none found | none |
| `packages/model-schema/src/model_schema/approvals.py`, `__init__.py` | added: the `Decide` request body, moved from `backend/src/app/api/approvals.py:83-87` (DP-4, decided), unless WK-674 S2 has already moved it (Task 0 Step 4 records which) | **WK-674 S2** (PL 9765, working id) edits `approvals.py` (`ApprovalPolicyEntry`, `DEFAULT_POLICY`, the predicate; `PL-1306` `:500`) | serial (S2 first); a new class, not an edit to S2's definitions |
| `docs/contracts/` (generated) | regenerated | **`PL-1364`** (FD-1335 Part A) regenerates; WK-674 S2 regenerates | generated: regenerate on the merge base, never hand-merge |
| `backend/tests/test_contracts.py` | edited only if `PL-1364`'s untyped-body guard is on `main` at dispatch (it is not at `92b4e4ac`) and lists the `decide` request body: that entry is removed in the same commit (the guard's "typed route still listed fails" rule). Decide's `200` stays on whatever list owns it (FD 9752) | **`PL-1364`** (after this slice in lane B) | conditional; recorded for whichever merges second |
| `backend/migrations/versions/<rev>_reset_rule_approvals_without_a_request.py` | added *(DP-6 a)*; `down_revision` = the head at dispatch (after S2's migration) | WK-674 S2 adds a migration | registry, append-only; serial anyway |
| `examples/fremtpl2/seed.py` (`run`, its rule write at `:437-455`) | edited *(DP-5 a)* | **FD-1357 fix** (PL 9764, working id; multi-factor seeding) is expected to edit `seed.py` | serial: FD-1357 fix first (activation need 2); this slice re-reads `seed.py` after it |
| `backend/tests/test_approval_guard_static.py` | edited: `ALLOWANCE_SITES` (`:37-46`); and `("examples/fremtpl2/seed.py", "run")` removed *(DP-5 a)* | none | none |
| `backend/tests/test_approval_guard_allowance.py` | edited: the `approve_rule` test (`:159-176`) | none | none |
| `backend/tests/approved_rows.py` | edited: `_EVIDENCE`, `_FLAG_ONLY` | none | none |
| `backend/tests/test_api_approvals.py` | edited: `_AFTER`, `_MOVE_ACTION` (`:979-997`), `_create_authored`'s `validation_rule` branch (`:228-240`) | **WK-674 S2** edits this file (`PL-1306` Task 6, `:500`) | serial (S2 first); different definitions |
| `backend/tests/test_api_datasets.py` | edited: `test_a_rule_walks_draft_to_approved_and_never_by_its_author` (`:603-676`), `_approved_rule` (`:679-708`) | none found | none |
| `backend/tests/test_validation_rule_approval.py` | added (new module) | none | none |
| `backend/tests/dry_run_reports.py` | added (new helper) | none | none |
| `frontend/src/api/rules.ts`, `frontend/src/components/RuleBuilder.vue`, `frontend/src/views/RuleSetView.vue`, their tests | edited *(DP-2 a)*: the submit call sends the typed body; the views collect a change summary | none found | none |
| `docs/specs/01-data-management.md` §5.1 (`:878-879`, the note at `:919-927`) | edited only with a ruling's verbatim text (Task 6) | the WK-1178 §5.1 Permission-column slice (ruling working id 9907, #977, not minted) edits every module's §5.1 table | if both are in flight, the second re-reads; a dated note below the table does not edit the table |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | every PR | registry |

**Open PRs read at `1dd5e264` (`gh pr list --state open`, 2026-10-01 10:1x BST), none
rules on this slice's subject:** #1049 (`SL-1360`, the parity check: it reads `requires()`
sites; DP-1 (a) removes one `approval:decide` site and leaves others, so parity is unchanged);
#1036 (merged as `PL-1364` at `92b4e4ac`; contention above); #979 (OQ 9987, working id: is a Validation
Rule Set governed; it decides `replace_rule_set`'s allowance, which this slice leaves alone);
#977 (§5.1 Permission column, above); #976 (FD 9890, S2's withdraw); #975 (FD 9988, the
authorisation sweep); the rest are findings and plans on other subjects. **PL 9765 and PL 9764
were not pushed at `1dd5e264`**, so their write sets were read from the lead's reservation
table (`eta.md`) and `PL-1306`, not from the plans. Task 0 Step 4 re-reads both at dispatch.

### Size

Medium: about one and a half executor days. Six tasks after the preconditions, a database
migration, real dry-run jobs in the tests, and a frontend change under DP-2 (a). One full
two-half gate run (a gate slot under `RL-1263`). No NFR measurement, so it need not run
exclusive.

## Decision points

None is decided here. Each owner rules by a dated record.

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-0** | Task 0 printed `TOTAL route_approved=5` (§"Task 0 at planning time"): 5 rules in one scratch W37-6 gate database. Which reading of "self-approval route" does the containment check encode, and how is the STOP disposed? | Readings: ROUTE_APPROVED (approved through the rule's own direct route; 5 at planning time) or `approved_by = authored_by` (0 by the CHECK, so a check that can never fire). Dispositions: (a) the STOP stands until a re-run prints 0; (b) a dated line accepts the 5 refs; (c) export, then drop the scratch database, then re-run expecting 0; (d) narrow the population | the plan recommended (c) and refused (d) | **DECIDED by the maintainer**, "2026-10-01 10:39:13 BST — #1063 DP-0 DECIDED: (c) export, then drop, then re-run expecting 0; the reading question: the PLAN's reading is mine (route_approved); my wording was ambiguous": the reading is ROUTE_APPROVED; **(c), in order**: (1) export the 5 rows (every column) plus their audit events, verbatim, with the provenance evidence, into the FD-1356 fix ledger; (2) drop `gipricing_w37-6-run2-gate-1789676768`; (3) re-run Task 0 and expect 0. (d) "is not on the table". The 5 rows also show the direct route was reachable and exercised by the test suite, consistent with FD-1356's HIGH. Record: §"DP-0's decided record" | activation need 4 (re-confirmed at dispatch) |
| **DP-1** | The direct route: removed, or a thin client of the workflow (FD-1356 Disposition, bullet 1) | (a) **Remove** `POST /validation-rules/{id}/approve`, the service `approve_rule`, the frontend `approveRule`, and strike the `01` §5.1 row with a dated note. The rule-set view then needs an approvals client (find the open request; decide). (b) **Thin client**: the route resolves the rule's open request (`open_request_for`) and calls `decide_and_carry(..., decision=APPROVE)`, the decide route's own path; it never writes `approved`; no open request → `409 APPROVAL_SUBJECT_NOT_IN_REVIEW`; self-approval becomes `403` (Acceptance 11) | **(b).** It removes the bypass (the route has no write of its own) while keeping the rule-set view's one-button flow, which has no approvals client today (`frontend/src/api/` has none). (a) pulls a new approvals client into this slice, and the list and decide routes it would call return `dict[str, Any]` today. The `01` §5.1 row survives under (b), but the `01:919-927` note ("This is the module's own step") becomes false and needs a dated note | **decision-maker** (spec text in Task 6 comes from the ruling) | Tasks 3, 4, 5, 6 |
| **DP-2** | Where the approval request is created | (a) The module submit (`POST /validation-rules/{id}/submit`) calls `approvals.submit` with a `change_summary` from a typed `model-schema` body (`ValidationRuleSubmission`), as `objectives.submit_for_review` does; the frontend collects the summary. (b) The module submit stays `draft → review` only; the client then calls `POST /approval-requests` (the generic path, which works today, case 5). (c) As (a), with the summary taken from the rule's own `rationale` field, so the route keeps no body | **(a).** It is the existing pattern of all four sibling modules (`approvals.submit` docstring, `platform/approvals.py:237-241`), and FR-352 requires a change summary from the submitter. (b) leaves a rule in `review` with no request, "reviewable by nobody" (the comment at `api/approvals.py:290-292`). (c) mistakes a rule's rationale for a statement of what changed, which is wrong for version 2 onward | **decision-maker** | Tasks 3, 4, 5 |
| **DP-3** | The `error`-outcome refusal. **Decided by FD-1356 itself** (its §"Disposition", the maintainer's "2026-09-30 11:32:49 BST" entry, item 1): the refusal is at the service layer, at submit and at approve, each reading the attached report's outcome, with one red-first case per cause and `fail` accepted. **Open:** (i) whether a DB CHECK backs it; (ii) the error code; (iii) whether a report that cannot be read is refused | (i-a) no DB CHECK; (i-b) a `dry_run_outcome` column on `validation_rules`, written by `attach_dry_run`, and the CHECK extended with `AND dry_run_outcome <> 'error'`. (ii-a) `EVIDENCE_INCOMPLETE` (422, `06`-owned and registered, `backend/src/app/errors.py:273`, as `objectives._require_evidence` raises it); (ii-b) a new module code (a spec change to `01`'s owned codes). (iii-a) refuse a dangling `dry_run_report_id` (fail closed; Acceptance 9); (iii-b) leave it as today (only `error_count` is read when a report exists) | **(i-a), (ii-a), (iii-a).** (i): the report is immutable and already indexed (`error_count`, `backend/src/app/db/models.py:1057`); a copy on the rule row is a second source that can disagree with it (`CLAUDE.md` §2), and it adds a migration to a table S2's trigger also covers; (i-b) is the stronger guard against a future writer that skips the service, so it is offered as a follow-on. (iii) **is scope growth beyond FD-1356**, which names the `error` outcome only. It is recommended because the platform refuses what it cannot check (`APPROVAL_AUTHOR_UNRESOLVED`), but it forces every fixture that attaches `new_uuid7()` to store a real report (Task 2), so it is the decision-maker's choice, not the plan's. `RULE_NOT_APPROVED` stays the code for "no dry-run at all" | **decision-maker** (open parts only) | Tasks 2, 3 |
| **DP-4** | The decide route's handler body changes (it calls `decide_and_carry`), and at `1dd5e264` its body is the route-local `Decide` and its `200` is `dict[str, Any]`. Does the holds rule reach it? | (a) type it in this slice; (b) leave it | the plan recommended (a) | **DECIDED by the maintainer**, "2026-10-01 10:34:13 BST — The DP-S2-6 header for quoting; #1063 DP-0 HELD until auditor-1063's provenance check (and the evidence rule if (c)); DP-4 (a) accepted; status noted": "type decide_request's BODY in this slice; its 200 goes to FD 9752 / FD-1335 Part B with a key-set characterisation test, as for DP-S2-6 (c). FD 9752 names this route too." So: `Decide` moves to `model-schema` (Task 4 Step 4); decide's `200` gets `test_the_decide_response_keeps_its_key_set` (Acceptance 15) and is owned by FD 9752 (working id, #1066) | Task 4 |
| **DP-5** | The demo seed writes `approved` user rules with no request, through the allowance entry `("examples/fremtpl2/seed.py", "run")` (`RL-1301` A.4.5 calls it legitimate "while legitimate", "re-read by that finding's triage"; FD-1356's triage re-read only `seed_builtin_rules` and `replace_rule_set`). Without a change, the next seed re-creates what item 13 resets | (a) The seed walks its rules through the workflow (its analyst authors and submits, its actuary decides) and its allowance entry is removed, red first, as the `approve_rule` entry is. (b) The entry stays as a named demo-data exemption; the reset of item 13 and Task 0's population exclude the seed's slugs (`exposure-positive-*`), each named | **(a).** "Approved rules with no approved request" then has no writer outside the built-ins, so item 13's count stays 0 after a reseed. (b) keeps a second population that every later check must remember to subtract | **decision-maker** | Task 7 |
| **DP-6** | How follow-on 2's reset is applied, and with what record | (a) **An Alembic data migration**: `UPDATE validation_rules SET status='review', approved_by=NULL WHERE status='approved' AND builtin IS NOT TRUE AND NOT EXISTS (<FD-1356's approved-request predicate>)`. It is **permanent in the chain**, its `downgrade()` is a no-op, it **reaches every database that upgrades, non-scratch ones included** (any future real deployment too), and it **writes no Audit Event**: the count goes to stdout only, and the ledger records it. (a') As (a), but the migration also writes one `validation_rule.reset_to_review` Audit Event per row (actor: a named system principal, `source` the migration's, `before`/`after` the statuses), so each reset row carries its own record in the hash chain. (b) **A scoped one-off script** under `scripts/`, run by the executor against the named databases only (`gipricing` and the fixtures' template), which can write the same Audit Events through `audit.record`, leaves no migration in the chain, and does nothing on a database it is not pointed at | **(a')**: reproducible and reviewed like (a) (`RL-1301` A.4.4 has the auditor read every new migration), but no approval is silently withdrawn, since every reset is in the audit chain (`06`'s audit rules apply to post-approval states, FR-351). Its cost is a migration that knows the audit writer's chain lock (`sequence`, `prev_event_hash`); if that is judged too heavy for a migration, (b) is the next choice and (a) the last. The trigger does not fire on a write to `review` (it checks only `NEW.status = 'approved'`), and the CHECK holds for a non-approved row | **decision-maker** | Task 7 |

### DP-0's decided record

Executed by auditor-dp0 on the maintainer's DP-0 (c) decision, as relayed by the lead at about
10:4x BST on 2026-10-01 (no minute stamp on the relay). It is written into the plan because the
export directory is local to this VM; the plan's copy survives when the plan merges.

- **Export directory** (local; **kept until the slice ledger merges**, Task 0 Step 2):
  `/home/puzhenhao1989/gi-pricing-plan.local/handover/fd1356-dp0-export-2026-10-01/`.
- **`SHA256SUMS`, verbatim** (re-verified by the lead with absolute paths, 6 of 6 OK; re-run by
  this plan's author with `sha256sum` on the six files, all six match):

```text
42e9503b08c147a1439684ddb892b61a466af47f9cc4b624a03e547b5ab64c3b  audit_events.csv
ee074f2b78196f0572182f2b52b16a77faf2b5cf1eb26c6f83428071af52afb2  audit_events.jsonl
aa7dbc4e531a80913c9931936e5a4de8daab4ec1f20d53a090de41bc77d2a650  validation_rules.csv
8c9e57ca173ad7018c853fd17b3c6cd7f664d36b5d3e207092295ab8c44361e0  validation_rules.jsonl
9c4f945c7d366d15969150afc64bbde4f6759d3f0d42d183bf4106add0e7c119  provenance.md
948404e2a2f99cccf6d5582eb05947763c8bee1eb2fa56727f9962bd016493e5  drop-and-rerun.md
```

- **Counts:** 5 rules (every column) and 15 Audit Events (for each rule, one
  `validation_rule.created`, one `validation_rule.submitted` and one
  `validation_rule.approved`), confirmed by count queries and a re-read (auditor-dp0).
- **Key columns**, tabulated by this plan's author from `validation_rules.jsonl` and
  `audit_events.jsonl`. Each approval event was joined to its rule on `workspace_id` and
  `entity_ref = 'validation_rule:<slug>@<version>'`:

| slug | version | workspace_id | authored_by | approved_by | approval event id | event `at` | actor.display | `after` has `approval_request_id` |
|---|---|---|---|---|---|---|---|---|
| `rng-bf487669` | 1 | `01a0b10d-ee00-70fe-af35-35501548dafd` | `01a0b10d-ee00-7485-a86b-8d9f6154fc92` | `01a0b10d-f27b-72b9-ba4e-f84d30f07079` | `01a0b10d-f29e-7699-bf5f-da06a2bf443a` | `2026-09-17T20:27:56.441279+00:00` | `dev@localhost` | no |
| `rng-c1c106c8` | 1 | `01a0b10d-f2c7-7f29-8863-ee6daa940b72` | `01a0b10d-f2c7-78d1-8a43-628bdd866ace` | `01a0b10d-f329-70d6-a423-67ff9f9184a6` | `01a0b10d-f53a-77e8-a0d6-e33432e99837` | `2026-09-17T20:27:57.107788+00:00` | `dev@localhost` | no |
| `rng-f8e9b7c4` | 1 | `01a0b10d-f2c7-7f29-8863-ee6daa940b72` | `01a0b10d-f2c7-78d1-8a43-628bdd866ace` | `01a0b10d-f329-70d6-a423-67ff9f9184a6` | `01a0b10d-f592-7861-abe0-439f40713aa8` | `2026-09-17T20:27:57.197872+00:00` | `dev@localhost` | no |
| `rng-2f0a876d` | 1 | `01a0b10d-f601-7f80-a811-d9f96b9ed567` | `01a0b10d-f601-7981-8fd3-e6439d68b787` | `01a0b10d-f667-7f3d-98fc-d2ce538a3e60` | `01a0b10d-f868-7f0c-afe7-d0c6bdaed70f` | `2026-09-17T20:27:57.91956+00:00` | `dev@localhost` | no |
| `rng-b73d354e` | 1 | `01a0b10d-f601-7f80-a811-d9f96b9ed567` | `01a0b10d-f601-7981-8fd3-e6439d68b787` | `01a0b10d-f667-7f3d-98fc-d2ce538a3e60` | `01a0b10d-f8dd-759b-afc5-3abbf95b8c3b` | `2026-09-17T20:27:58.036136+00:00` | `dev@localhost` | no |

- **The drop:** `DROP DATABASE "gipricing_w37-6-run2-gate-1789676768";` at 10:41:04–10:41:05
  BST, with 0 connections at 10:41:04 (auditor-dp0).
- **The re-run (auditor-dp0):** Task 0, 10:41:08–10:41:19 BST, exit 0, its last two lines:

```text
databases=80 with_tables=77 without_table_or_error=3
TOTAL route_approved=0 self_approved=0 user_approved_no_approved_request=314
```

  329 → 314 because the dropped database held 15 of the follow-on-2 population. This plan's
  author's own re-run at about 10:41:59 BST (§"Task 0 at planning time") printed the same two
  lines.
- **Caveats, recorded as such:** the timing is evidence, not proof; the per-test 1+2+2
  workspace mapping was matched to quoted lines of `test_api_datasets.py` but not re-derived;
  the gate log's `STOPPED` line has no date, and 17 September is assumed. The 5 rows also show
  that the direct route was reachable and exercised by the test suite, which is consistent
  with FD-1356's HIGH, not a reason to doubt it (the maintainer's entry).
- **`FD-1241`'s database list** (minted and frozen, not edited) is a one-off snapshot of 81
  databases that names `gipricing_w37-6-run2-gate-1789676768`. That database was dropped on
  2026-10-01 under this DP, which is why the snapshot's count no longer matches the server.

**A rule reset to `review` with no request (Task 7) has no path through the DP-1 (b) thin
client.** `open_request_for` finds no open request and answers `409
APPROVAL_SUBJECT_NOT_IN_REVIEW`, whose name is misleading there (the rule **is** in `review`;
what is missing is the request), and the module submit refuses a non-`draft` rule. The only
way forward is a raw `POST /approval-requests` naming the rule's ref, which the generic
resolver accepts for a rule in `review` whose dry-run executed. The DP-1 and DP-6 rulings may
want to say whether that is acceptable or whether the reset should go to `draft` instead.

**Observed, not a decision point of this slice:** a dry-run whose only result is `skipped`
(for example a distributional rule with no reference profile) did not execute either.
FD-1356's acceptance names `error` only (the maintainer's "2026-09-30 11:27:20 BST" and
"11:32:49 BST" entries). This plan does not widen the refusal to `skipped`; it is offered to
the lead as a possible question for the decision-maker.

**Not in this slice, with an owner:** `replace_rule_set`'s allowance entry stays; its fate is
OQ 9987's (working id, #979, the decision-maker's), per `RL-1301` A.4.5 and FD-1356
§"Triage".

## Tasks

### Task 0: Preconditions and containment (no code)

- [ ] **Step 1: Run the containment query.** Copy this script, verbatim, to a scratch path
  outside the repository and run it with `bash`, with `gi-pricing-postgres-1` up. Record
  its whole output, its exit code and the time (`TZ=Europe/London date '+%F %T %Z'`) in the
  ledger.

```bash
#!/bin/bash
# PL 9762 Task 0: ROUTE_APPROVED VR versions (approved through the rule's own direct approve route,
# outside the approval workflow), judged by each rule's LATEST approval event, every gipricing* DB.
# STOP if TOTAL route_approved > 0.
Q="BEGIN READ ONLY; select count(*) filter (where v.builtin is not true and exists (select 1 from (select e.after from audit_events e where e.workspace_id=v.workspace_id and e.action='validation_rule.approved' and e.entity_ref='validation_rule:'||v.slug||'@'||v.version order by e.sequence desc limit 1) last_approval where not (coalesce(last_approval.after, '{}'::jsonb) ? 'approval_request_id'))), count(*) filter (where v.builtin is not true and v.approved_by = v.authored_by), count(*) filter (where v.builtin is not true and not exists (select 1 from approval_requests a where a.workspace_id=v.workspace_id and a.artifact_type='validation_rule' and a.artifact_ref='validation_rule:'||v.slug||'@'||v.version and a.status='approved')) from validation_rules v where v.status='approved'; ROLLBACK;"
dbs=$(docker exec gi-pricing-postgres-1 psql -U gipricing -d postgres -Atc "select datname from pg_database where datname like 'gipricing%' and not datistemplate order by 1")
n=0; has=0; nohas=0; r=0; s=0; z=0
for d in $dbs; do
  n=$((n+1))
  out=$(docker exec gi-pricing-postgres-1 psql -U gipricing -d "$d" -At -F, -c "$Q" 2>&1 | grep -E '^[0-9]+,[0-9]+,[0-9]+$')
  if [ -z "$out" ]; then nohas=$((nohas+1)); echo "$d no_table_or_error"; continue; fi
  has=$((has+1))
  IFS=, read -r rr ss zz <<< "$out"
  r=$((r+rr)); s=$((s+ss)); z=$((z+zz))
  if [ "$rr" != 0 ] || [ "$ss" != 0 ] || [ "$zz" != 0 ]; then
    echo "$d route_approved=$rr self_approved=$ss user_approved_no_approved_request=$zz"
  fi
done
echo "databases=$n with_tables=$has without_table_or_error=$nohas"
echo "TOTAL route_approved=$r self_approved=$s user_approved_no_approved_request=$z"
if [ "$r" -ne 0 ]; then echo "STOP: route_approved > 0"; exit 1; fi
```

  **What each column counts, and why the first is the STOP predicate.**
  - `route_approved` (**ROUTE_APPROVED**, the maintainer's reading in "2026-10-01 10:39:13 BST — #1063 DP-0 DECIDED: (c) export, then drop, then re-run expecting 0; the reading question: the PLAN's reading is mine (route_approved); my wording was ambiguous": "a VR version approved through its own direct approve route,
    outside the approval workflow"): non-built-in `approved` rules whose **latest**
    `validation_rule.approved` Audit Event for the same workspace and ref (by the workspace's
    monotonic `sequence`) has **no** `approval_request_id` in its `after`. The latest event is
    used so that a rule reset to `review` by Task 7 and re-approved through the workflow is not
    counted for its old direct-route event (auditor-1063 finding 2, accepted in the same entry). At
    `1dd5e264` that event has exactly one writer, `approve_rule`
    (`git grep -n 'validation_rule.approved' -- backend/src examples backend/migrations`
    prints only `backend/src/app/platform/validation_rules.py:442`), and its `after` is
    `{"status", "approved_by"}` (`:445`). After this slice the carry writes the same action
    **with** `approval_request_id` (Acceptance 12), so the predicate keeps meaning "approved
    by the direct route" at the exit-demo re-run. Seeds and fixtures record no such event,
    so they are not counted.
  - `self_approved`: `approved_by = authored_by`, the other reading of "self-approval", which
    the maintainer's entry rules is **not** the containment reading; the CHECK refuses it, so it
    must print 0. A non-zero here is a broken constraint: stop and
    report.
  - `user_approved_no_approved_request`: FD-1356 follow-on 2's population, for context and
    for Task 7's before-count. It is not a STOP condition.
  - `no_table_or_error`: an empty database or a query error; Step 1 records which.

  **STOP** if the last line is `STOP: route_approved > 0`. Report to the lead with the output.
  Do not proceed, and do not edit the predicate or the population (the maintainer: narrowing
  the population "is the shape of a check edited until it passes").
- [ ] **Step 2: Quote the DP-0 export into the ledger, and verify it.** Copy every file of
  `/home/puzhenhao1989/gi-pricing-plan.local/handover/fd1356-dp0-export-2026-10-01/` verbatim into the slice's
  `LG-` ledger (the 5 rows with every column, their audit events, the creating actors, the
  approving requests, and the provenance evidence). Run `sha256sum` on each file and compare
  each line with §"DP-0's decided record"'s `SHA256SUMS` lines; record the comparison. Any
  mismatch, or a missing file: **stop** and report to the lead. **The local export directory is
  not deleted until that ledger has merged**: it is the only copy of the bypass having fired
  outside the plan's own key columns.
- [ ] **Step 3: Confirm the order.** `git log --oneline origin/main` shows WK-674 S2
  (`SL-1256`), `SL-1360` and the FD-1357 fix merged. Read `alembic heads` on the merge base and
  record it; it is Task 7's `down_revision`.
- [ ] **Step 4: Re-read the shared files after S2 and the FD-1357 fix.** Record the line
  ranges, at the dispatch tree, of `_carry_to_the_artifact`, `decide_request`,
  `submit_for_approval` and `_resolve_the_artifact` (`backend/src/app/api/approvals.py`),
  `approve_rule`, `submit_for_review` and `resolve_artifact_ref`
  (`backend/src/app/platform/validation_rules.py`), `ALLOWANCE_SITES`, and `seed.py`'s rule
  write. Record whether S2 typed `POST /approval-requests`' body and `201`, and under which
  `model-schema` names (DP-4 uses them). **Any temporary validation-rule exemption S2 added
  to a one-writer check** (`git grep -n -i 'FD-1356\|9892\|validation-rule fix slice' -- backend
  tests`) is listed and joins Task 1's removals.
- [ ] **Step 5:** `gh pr list --state open`, and read any PR touching
  `api/approvals.py`, `platform/approvals.py`, `validation_rules.py`, `api/validation.py`,
  `seed.py`, `01` §5.1 or `test_contracts.py`; name each head SHA in the ledger.

### Task 1: The allowance removal, red first (Acceptance 10)

**Files:**
- Modify: `backend/tests/test_approval_guard_static.py` (`ALLOWANCE_SITES`, `:37-46`)

- [ ] **Step 1:** Delete the line `("backend/src/app/platform/validation_rules.py", "approve_rule"),`
  and keep the comment `# Temporary: removed, red first, by the WK-1178 validation-rule fix slice.`
  above the `replace_rule_set` entry, rewritten to
  `# Temporary: pending OQ 9987 (working id), per RL-1301 A.4.5.`
- [ ] **Step 2: Run it red.**
  `uv run pytest -q backend/tests/test_approval_guard_static.py -k sanctioned_and_allowance_sites`.
  Expected: **1 failed**, the assertion's left side exactly
  `['backend/src/app/platform/validation_rules.py::approve_rule']`. A different list is a
  plan defect: stop. `test_every_pinned_site_really_enters_the_context` fails too, for the
  same site; record both.
- [ ] **Step 3:** Do not commit yet. Task 3 turns these green; the two commit together.

### Task 2: The tests, red first (Acceptance 2, 3, 5–9, 11, 12)

**Files:**
- Create: `backend/tests/dry_run_reports.py`
- Create: `backend/tests/test_validation_rule_approval.py`
- Modify: `backend/tests/test_api_approvals.py` (`_AFTER`, `_MOVE_ACTION`, `_create_authored`)
- Modify: `backend/tests/test_api_datasets.py` (`:603-708`)

**Interfaces:**
- Produces: `stored_dry_run_report(session, *, workspace_id: UUID, rule: ValidationRuleRow, outcome: RuleOutcome) -> UUID`,
  which inserts one `ValidationReportRow` for a one-rule run of `rule` and sets
  `rule.dry_run_report_id`; used by every fixture that previously attached `new_uuid7()`.

- [ ] **Step 1: The report helper.** It writes the row directly, without `store_report`
  (`backend/src/app/platform/validation.py:77-112`), because `store_report` requires a real
  Dataset Version and these fixtures have none. The body is a real `ValidationReport`, so
  anything that reads it back validates.

```python
"""A stored dry-run report with a chosen outcome, for fixtures that need one.

`_require_executed_dry_run` reads the attached report, so the old fixture idiom
`row.dry_run_report_id = new_uuid7()` now reads as "a report that cannot be read" and is
refused (PL 9762, DP-3). The real dry-run job is used where the outcome's cause matters
(`test_validation_rule_approval.py`); this is for the rest.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ValidationReportRow, ValidationRuleRow
from model_schema import (
    RuleOutcome,
    RuleResult,
    Severity,
    ValidationLayer,
    ValidationReport,
    new_uuid7,
)

__all__ = ["stored_dry_run_report"]


async def stored_dry_run_report(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    rule: ValidationRuleRow,
    outcome: RuleOutcome = RuleOutcome.PASS,
) -> UUID:
    now = datetime.now(UTC)
    report = ValidationReport(
        id=new_uuid7(),
        dataset_version_id=new_uuid7(),
        rule_set_id=rule.id,
        rule_set_version=rule.version,
        started_at=now,
        finished_at=now,
        results=(
            RuleResult(
                rule_id=rule.id,
                rule_slug=rule.slug,
                rule_version=rule.version,
                layer=ValidationLayer(rule.layer),
                severity=Severity(rule.severity),
                outcome=outcome,
            ),
        ),
    )
    counts = report.counts
    session.add(
        ValidationReportRow(
            id=report.id,
            workspace_id=workspace_id,
            dataset_version_id=report.dataset_version_id,
            rule_set_id=report.rule_set_id,
            rule_set_version=report.rule_set_version,
            overall=report.overall.value,
            rule_count=len(report.results),
            fail_count=counts[RuleOutcome.FAIL.value],
            warn_count=counts[RuleOutcome.WARN.value],
            error_count=counts[RuleOutcome.ERROR.value],
            body=report.model_dump(mode="json"),
            started_at=now,
            finished_at=now,
        )
    )
    await session.flush()
    rule.dry_run_report_id = report.id
    await session.flush()
    return report.id
```

  Verify each `model_schema` name against `packages/model-schema/src/model_schema/__init__.py`
  before use; if `rule.id` is unset (an unflushed row), flush the rule first.
- [ ] **Step 2: The generic table test.** In `backend/tests/test_api_approvals.py`:
  - `_AFTER["validation_rule"]` becomes `_moves("approved", "review", "draft")` (FR-355:
    the pre-submission state of a rule is `draft`, `01` §4.5 step 1);
  - `_MOVE_ACTION` gains `"validation_rule": lambda to: f"validation_rule.{to}"`;
  - `_create_authored`'s `validation_rule` branch (`:228-240`) flushes the row and calls
    `stored_dry_run_report(session, workspace_id=workspace_id, rule=row)` when `status` is
    not `"draft"`, and creates the rule through a path that records the
    `validation_rule.created` event, as its siblings do (read `_create_authored` whole; FR-353's
    author check needs that event, or decide answers `APPROVAL_AUTHOR_UNRESOLVED`).

  Run `uv run pytest -q backend/tests/test_api_approvals.py -k "decision_moves and validation_rule"`.
  Expected: `approve`, `reject` and `request_changes` **fail**, each because the rule's
  status is still `review` (the carry has no branch); `first_of_two` passes. A failure for
  another reason (an `APPROVAL_AUTHOR_UNRESOLVED`, a 422) is a fixture defect: fix the fixture,
  not the expectation.
- [ ] **Step 3: The new module.** `backend/tests/test_validation_rule_approval.py`, with
  these tests (names are the Acceptance map's). Mirror `backend/tests/test_data_jobs.py`'s
  fixtures for real jobs (`actuary`, `_ingest`, `CAST_RECIPE`, `execute_job`,
  `register_data_handlers`, `:84-228`) rather than inventing new ones; copy what you need,
  since its helpers are module-private. The dry-run job's payload is
  `{"workspace_id", "actor", "dataset_version_id", "dry_run_rule_id"}` (`backend/src/app/api/validation.py:319-327`,
  read by `backend/src/app/worker/data_handlers.py:220`). Rules are created through
  `POST /api/v1/validation-rules`, so each has its `validation_rule.created` event.

  | Test | Setup | Expected after the fix | Expected on the base tree (red) |
  |---|---|---|---|
  | `test_an_error_dry_run_is_refused_at_submit[missing_column]` | `range` on `{"table": "policy_exposure", "column": "no_such_column"}`; real dry-run | report `error_count >= 1`; submit `422`, `code == "EVIDENCE_INCOMPLETE"`; rule `draft` | submit `200`, `review` |
  | `…[unknown_check]` | `check: "no_such_check"` (authoring is per spec, `01:470`) | as above | as above |
  | `…[missing_table]` | target table `no_such_table` | as above | as above |
  | `test_an_error_dry_run_is_refused_at_approve[…]` (same three) | the rule's status set to `review` and an `ApprovalRequestRow` (`status="review"`, `approvers_required=1`) added by test-only writes; another approver decides `approve` | decide `422 EVIDENCE_INCOMPLETE`; rule `review`; request `review`; `approval_decisions` count for it `0` | decide `200`, the request `approved` and the rule **still `review`** (no carry branch): fails on the status-code assertion |
  | `test_a_fail_dry_run_is_still_approvable` | `range` `min_exclusive: 0` severity `fail` on `exposure_years`, a version with one negative row | report `overall == "fail"`, `error_count == 0`; submit `200 review`; second approver `approved` | passes (control) |
  | `test_the_generic_submit_refuses_an_error_dry_run` | an `error` rule set to `review` by a test-only write; `POST /approval-requests` | `422 EVIDENCE_INCOMPLETE` | `201` |
  | `test_a_dry_run_report_that_cannot_be_read_is_refused` | `dry_run_report_id = new_uuid7()`, no row | submit `422 EVIDENCE_INCOMPLETE` | `200` |
  | `test_one_approval_under_a_quorum_of_two_leaves_the_rule_in_review` *(DP-1 b)* | policy `approvers_required=2` (mirror `_require_two_approvals`, `test_api_approvals.py:999-1012`); submit; one approver's `POST /validation-rules/{id}/approve` | `200`, rule `review`, request `review`, 1 decision; a second approver's call: `approved`, `approved_by` the second | first call `200 approved` |
  | `test_the_approve_route_decides_through_the_workflow` *(DP-1 b)* | submit; approve via the route | an `approved` `approval_requests` row and an `approval_decisions` row for the ref; with no open request, `409 APPROVAL_SUBJECT_NOT_IN_REVIEW` | `approved` with 0 requests |
  | `test_the_approve_route_is_gone` *(DP-1 a, instead)* | — | path not in `app.openapi()["paths"]`; call `404` or `405` | `200` |
  | `test_the_carry_records_the_request_it_carried` | approve through decide | the `validation_rule.approved` event's `after["approval_request_id"] == str(request_id)` | no such event key (direct route) |
  | `test_the_submitter_and_the_author_cannot_decide` | author submits and decides; then another submits and the author decides | `403 SUBMITTER_CANNOT_APPROVE`; `403 AUTHOR_CANNOT_APPROVE` | `409` from the direct route |

  Each test carries the `req` markers of §"Requirement coverage".
- [ ] **Step 4: The existing API tests.** In `test_api_datasets.py`, replace both
  `row.dry_run_report_id = new_uuid7()` sites (`:650`, `:700`) with
  `stored_dry_run_report`; under DP-2 (a), every submit call sends
  `json={"change_summary": "…"}`; under DP-1 (b), the self-approval assertion becomes `403`
  (`:663-664`). Under DP-1 (a), `_approved_rule` and the chain test approve through
  `POST /approval-requests/{id}/decide`, the request id read from the submit's request (or
  from `GET /approval-requests?artifact_type=validation_rule&status=review`).
- [ ] **Step 5: Run red.** `uv run pytest -q backend/tests/test_validation_rule_approval.py backend/tests/test_api_approvals.py backend/tests/test_api_datasets.py`.
  Record every red with its cause, as the table predicts. Commit the tests with Task 3.

### Task 3: The service and the carry (Acceptance 2–12)

**Files:**
- Modify: `backend/src/app/platform/validation_rules.py`
- Modify: `backend/src/app/api/approvals.py`
- Modify: `backend/tests/test_approval_guard_allowance.py` (`:159-176`)

**Interfaces:**
- Produces: `validation_rules.apply_approval_decision(session, *, workspace_id: UUID, actor: Principal, request: ApprovalRequestRow) -> ValidationRuleRow | None`;
  `validation_rules.submit_for_review(session, *, workspace_id, actor, rule_id, change_summary: str) -> ValidationRuleRow` *(DP-2 a)*;
  `validation_rules.open_request_for(session, *, workspace_id: UUID, row: ValidationRuleRow) -> UUID` *(DP-1 b)*;
  `api.approvals.decide_and_carry(session, *, caller: Caller, request_id: UUID, decision: DecisionKind, comment: str | None) -> ApprovalRequestRow`.

- [ ] **Step 1: `_require_executed_dry_run`** (DP-3 (a)), private, in `validation_rules.py`:

```python
async def _require_executed_dry_run(
    session: AsyncSession, *, workspace_id: UUID, row: ValidationRuleRow
) -> None:
    """The dry run executed: its report exists here and has no `error` (FR-363, `06:114`).

    `01` §4.5 step 2 says the rule "must execute successfully", and `01:470-473` says the
    mandatory dry run is what stops an `error` outcome reaching approval. A `fail` is a rule
    that ran and caught rows, so it passes. A report that cannot be read is refused, never
    assumed (the platform's fail-closed rule, as `APPROVAL_AUTHOR_UNRESOLVED`).
    """
    report = (
        None
        if row.dry_run_report_id is None
        else await session.get(ValidationReportRow, row.dry_run_report_id)
    )
    if report is None or report.workspace_id != workspace_id:
        raise PlatformError(
            "EVIDENCE_INCOMPLETE",
            "Required evidence is missing",
            422,
            f"validation_rule:{row.slug}@{row.version}: its dry-run report "
            f"{row.dry_run_report_id} cannot be read in this workspace. `06` FR-363.",
        )
    if report.error_count > 0:
        raise PlatformError(
            "EVIDENCE_INCOMPLETE",
            "Required evidence is missing",
            422,
            f"validation_rule:{row.slug}@{row.version}: its dry run did not execute "
            f"({report.error_count} `error` result(s)). `01` §4.5 step 2 requires a run "
            "that executed; a `fail` outcome would be accepted. `06` FR-363.",
        )
```

- [ ] **Step 2: The module submit** (DP-2 (a)). `submit_for_review` keeps its two existing
  refusals (`:371-386`), then calls `_require_executed_dry_run`, then
  `approvals.submit(session, workspace_id=…, submitter=actor, artifact_ref=ArtifactRef(type="validation_rule", slug=row.slug, version=row.version), change_summary=change_summary)`,
  then sets `REVIEW`; its audit event's `after` gains `"approval_request_id": str(request.id)`
  and `justification=change_summary`. Mirror `objectives.submit_for_review`
  (`platform/objectives.py:558-618`) line for line in order. Under DP-2 (b), only the
  `_require_executed_dry_run` call is added.
- [ ] **Step 3: The generic resolver.** `resolve_artifact_ref` (`:317-349`) selects the row,
  not only its status, and after `approvals.require_in_review` calls
  `_require_executed_dry_run`.
- [ ] **Step 4: The carry branch.** `apply_approval_decision` mirrors
  `objectives.apply_approval_decision` (`:621-690`): `None` for another type; the row by
  workspace, slug and version `with_for_update()`; `None` if absent (FR-386 tolerance, as
  objectives); the target from `{APPROVED: APPROVED, CHANGES_REQUESTED: DRAFT, REJECTED: DRAFT, WITHDRAWN: DRAFT}`;
  a partial approval (`target is None`) returns the row unmoved. Before writing `APPROVED` it
  calls `_require_executed_dry_run` and sets `row.approved_by = actor.id`; it never enters
  `approval_decision()` itself (the caller is inside it). Its audit event: action
  `f"validation_rule.{target}"`, `before {"status": REVIEW}`, `after {"status": target,
  "approval_request_id": str(request.id)}` plus `"approved_by"` on approval.
- [ ] **Step 5: Wire it.** In `api/approvals.py`, `_carry_to_the_artifact` gains
  `await validation_rules_service.apply_approval_decision(...)` beside its siblings, inside the
  existing block; add the public `decide_and_carry` (the body of `decide_request`'s
  `service.decide(...)` call plus `_carry_to_the_artifact`), and make `decide_request` call it.
  The decide route's docstring keeps its one-transaction argument.
- [ ] **Step 6: Remove `approve_rule`'s write.** Delete the service `approve_rule`
  (`:403-447`), its `ALLOWANCE` comment and its `__all__` entry. Under DP-1 (b), add
  `open_request_for`: the `id` of the `ApprovalRequestRow` with this workspace,
  `artifact_ref == str(ArtifactRef(...))` and `status == "review"`, else `PlatformError("APPROVAL_SUBJECT_NOT_IN_REVIEW", …, 409, …)`.
- [ ] **Step 7:** `test_approval_guard_allowance.py:159-176`: delete
  `test_approve_rule_writes_approved_only_through_its_entry`, and the `approve_rule` mention
  in the module docstring (`:4`).
- [ ] **Step 8: Run green.** Task 1's two static tests, Task 2's modules,
  `backend/tests/test_approval_guard*.py` and `backend/tests/test_validation_reports.py`.
  Commit Tasks 1–3 together:
  `git commit -m "fix(governance): a validation rule is approved only through the approval workflow (FD-1356, WK-1178)"`.

### Task 4: The routes, typed (Acceptance 4, 15)

**Files:**
- Modify: `backend/src/app/api/validation.py` (`submit_rule`, `approve_rule`)
- Modify: `packages/model-schema/src/model_schema/validation.py`, `__init__.py` *(DP-2 a)*
- Modify: `backend/src/app/api/approvals.py` (`Decide` removed; `decide_request`'s body parameter, DP-4 decided)
- Modify: `packages/model-schema/src/model_schema/approvals.py`, `__init__.py` (`Decide`, DP-4 decided)
- Regenerate: `docs/contracts/`

- [ ] **Step 1: Red first.** Add two tests to `test_validation_rule_approval.py`. Build
  `create_app(...).openapi()` as `scripts/generate-contracts.py` does, without a database.
  - `test_every_body_this_slice_edits_is_a_model_schema_type`: for
    `POST /api/v1/approval-requests/{request_id}/decide` and, under DP-2 (a),
    `POST /api/v1/validation-rules/{rule_id}/submit`, the JSON request body is a `$ref` whose
    target name is an attribute of `model_schema`. Red: decide's body names the route-local
    `Decide`, which `model_schema` does not export (check with `hasattr(model_schema, "Decide")`
    at the dispatch tree; if S2 already moved it, this case is green and the ledger says so);
    the submit has no body.
  - `test_the_decide_response_keeps_its_key_set`: drive one decision and assert
    `set(response.json()) == DECIDE_RESPONSE_KEYS`, a literal set read from `service.to_dict`
    (`backend/src/app/platform/approvals.py:648-`) at the dispatch tree. Red: rename one key in
    a scratch edit of `to_dict`, run, record the failure naming both keys, revert.
  Record each failure line.
- [ ] **Step 2: The body** *(DP-2 a)*. In `model_schema/validation.py`:

```python
class ValidationRuleSubmission(BaseModel):
    """The body of `POST /validation-rules/{id}/submit` (`06` FR-352: a change summary)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    change_summary: str = Field(min_length=1)
```

  Export it from `model_schema/__init__.py`. `submit_rule` takes
  `body: ValidationRuleSubmission` and passes `change_summary=body.change_summary`.
- [ ] **Step 3: The thin client** *(DP-1 b)*. `approve_rule` keeps its path, its
  `DecideApprovals` dependency and `-> ValidationRule`; its body loads the rule,
  calls `open_request_for`, then `decide_and_carry(session, caller=caller, request_id=…, decision=DecisionKind.APPROVE, comment=None)`,
  refreshes the row and returns `to_schema(row)`. Its docstring loses "This is the module's
  own step" and says it is a client of the decide path. Under DP-1 (a), delete the route.
- [ ] **Step 4: Decide's body** (DP-4, decided). Move `Decide` (`backend/src/app/api/approvals.py:83-87`:
  `decision: DecisionKind`, `comment: str | None = None`, `extra="forbid"`) to
  `packages/model-schema/src/model_schema/approvals.py`, keeping its name, fields and config,
  and export it from `model_schema/__init__.py`; `decide_request` imports it. If Task 0 Step 4
  recorded that S2 already moved it, this step is a no-op. Decide's `200` is **not** changed
  (FD 9752's).
- [ ] **Step 5:** `uv run python scripts/generate-contracts.py` then `--check`; run Step 1's
  tests green and `uv run pytest -q backend/tests/test_contracts.py`. **Only if** `PL-1364`'s
  untyped-body guard is on `main` at dispatch (it is not at `92b4e4ac`) and lists decide's
  request body, remove that entry in this commit; decide's `200` stays wherever FD 9752 puts
  it. Commit:
  `git commit -m "feat(validation): the rule routes are clients of the approval workflow; decide's body typed (FD-1356)"`.

### Task 5: The frontend (DP-2 (a); DP-1 (a) if ruled)

**Files:**
- Modify: `frontend/src/api/rules.ts` (`submitRule`, `:86-88`; `approveRule`, `:97-99`)
- Modify: `frontend/src/components/RuleBuilder.vue` (`:110-111`), `frontend/src/views/RuleSetView.vue` (`:122-140`, `:385`)
- Modify: their tests under `frontend/src/**/__tests__/`

- [ ] **Step 1: Red first.** In the RuleBuilder and RuleSetView tests, assert that submitting
  posts `{"change_summary": <the entered text>}` and that the submit control is disabled while
  the summary is empty. Run `pnpm --dir frontend test`; expected: both fail (no body is sent).
- [ ] **Step 2:** `submitRule(ruleId, body)` takes the generated type for
  `ValidationRuleSubmission` (`pnpm --dir frontend generate:api` first; never hand-write it)
  and sends it. Each view gains a required change-summary input. The message for
  `SUBMITTER_CANNOT_APPROVE` stays keyed on the code, not the status (it becomes 403 under
  DP-1 (b)); add one for `EVIDENCE_INCOMPLETE` that says the dry run did not execute.
- [ ] **Step 3:** The five `pnpm --dir frontend` commands green. Commit:
  `git commit -m "feat(frontend): a rule is submitted with a change summary (FD-1356)"`.

### Task 6: The spec text, only from a ruling

- [ ] **Step 1:** If the DP-1 or DP-2 ruling carries text for `01` §5.1 (`:878-879`) or the
  note at `:919-927`, apply it **verbatim**, in one commit, following `spec-change`, and run
  `python3 scripts/audit-docs.py`. If no ruling carries text, edit no spec, and record in the
  ledger that `01:919-927` now describes a superseded design, as an owed spec change for the
  decision-maker.

### Task 7: The seed and the data reset (follow-on 2; DP-5, DP-6)

**Files:**
- Modify: `examples/fremtpl2/seed.py` *(DP-5 a)*; `backend/tests/test_approval_guard_static.py` (`ALLOWANCE_SITES`) *(DP-5 a)*
- Create: `backend/migrations/versions/<rev>_reset_rule_approvals_without_a_request.py` *(DP-6 a)*
- Modify: `backend/tests/approved_rows.py`

- [ ] **Step 1: The fixtures** (Acceptance 14). Move `ValidationRuleRow` into `_EVIDENCE` as
  `("validation_rule", "slug")` and out of `_FLAG_ONLY`; update the module docstring's last
  sentence of its first paragraph. Run `uv run pytest -q backend/tests/test_data_jobs.py backend/tests/test_reference_pin.py backend/tests/test_wf01_journey.py`
  green.
- [ ] **Step 2: The seed, red first** *(DP-5 a)*. Remove `("examples/fremtpl2/seed.py", "run")`
  from `ALLOWANCE_SITES`; run the two static tests and record the red naming
  `examples/fremtpl2/seed.py::run`. Then change the seed's rule write (`:437-455`) to: create
  the rule `draft` with its analyst, attach a stored dry-run report through the real dry-run
  job if the seed has a dataset version at that point, or else run that job, submit with a
  change summary, and decide with its actuary through `approvals.decide` and the carry (import
  `decide_and_carry`'s pieces, or call the HTTP routes as the rest of the seed does; read the
  seed whole first and follow its own style). If the seed's `approval_decision` block wraps
  anything other than the rule write, stop and report: the entry cannot go.
- [ ] **Step 3: The before-count.** Run FD-1356's follow-on script (its `## Disposition`,
  "The runnable predicate for open item 2", verbatim) and record its last line and the time.
- [ ] **Step 4: The migration** *(DP-6 a)*. One `upgrade()` executing, in order:
  a `SELECT count(*)` of the target rows, printed with `print()` or `logging` so the count
  appears in the migration's output; then

```sql
UPDATE validation_rules v
   SET status = 'review', approved_by = NULL
 WHERE v.status = 'approved'
   AND v.builtin IS NOT TRUE
   AND NOT EXISTS (
     SELECT 1 FROM approval_requests a
      WHERE a.workspace_id = v.workspace_id
        AND a.artifact_type = 'validation_rule'
        AND a.artifact_ref = 'validation_rule:' || v.slug || '@' || v.version
        AND a.status = 'approved')
```

  `downgrade()` is a no-op with a comment: an approval made outside the workflow is not
  restored. `down_revision` is Task 0 Step 3's head. Run
  `uv run alembic upgrade head` with the DSN `dev-commands` names, against the `gipricing`
  database, and record the printed count.
- [ ] **Step 5: The after-count** (Acceptance 13). Re-run Step 3's script; `gipricing` must
  print `user_approved_with_no_approved_request=0`, and `builtin_approved` must equal Step 3's
  figure for that database. Record both lines. Commit:
  `git commit -m "fix(data): reset rule approvals that no approval request backs (FD-1356 follow-on 2)"`.

### Task 8: The gate and the ledger

- [ ] **Step 1:** The full two-half gate (Acceptance 17) through the gate-runner, which holds
  a gate slot under `RL-1263`. Record each rc and the tree.
- [ ] **Step 2:** In the slice's `LG-` ledger: Task 0's run, every red of Acceptance 2–10 and
  15 with its printed line (paraphrase any line naming an undefined id, [`README.md`](README.md)
  rule 2), Task 7's three counts, and `git diff --stat origin/main...HEAD` against
  §"Write set" (Acceptance 18).

## Hand-off

1. The lead mints PL 9762 and SL 9761 (working ids) at the merge turn, and dispatches only
   after §"Activation needs" hold, in a separate activation PR.
2. **The exit-demo checklist line** (for the auditor, who owns `docs/process/checklists/`;
   the planner does not write it): *"FD-1356 containment: re-run PL 9762's Task 0 script
   verbatim; its last line must read `TOTAL route_approved=0` (or exactly the set the
   maintainer's DP-0 ruling accepted). Record the output, the time (BST) and the database
   count. Any other result: stop the exit demo and report to the maintainer."* The lead
   routes this line to the auditor at this slice's close.
3. When this slice merges, `FD-1356`'s event is discharged (its §"Disposition": "Event that
   discharges it: that slice's merge"); the auditor closes it.
4. Follow-ons not built here, each with an owner: the `dry_run_outcome` column and DB CHECK
   (DP-3 (b), the decision-maker, if wanted); the `skipped`-only dry-run question (the lead);
   `replace_rule_set`'s allowance (OQ 9987, working id, the decision-maker).
5. `PL-1364` (lane B, after this slice) re-derives its guard's lists at its own dispatch:
   decide's **request body** is typed here (DP-4), and its `200` is not; that `200` is owned
   by FD 9752 (working id, #1066), as are the other approval routes' 2xx under WK-674 S2's
   DP-S2-6 (c).

## Self-review

1. **Coverage of FD-1356's Disposition, clause by clause.**
   - "route rule approval through `approvals.submit` and `approvals.decide`": Task 3 Steps 2,
     4, 5; DP-2.
   - "remove the direct approve route, or make it a thin client": DP-1; Task 3 Step 6, Task 4
     Step 3.
   - "add the `_carry_to_the_artifact` validation-rule branch": Task 3 Steps 4–5;
     Acceptance 3.
   - "with a quorum of 2, one approval leaves the rule in `review`": Acceptance 2.
   - "the direct route is gone or refused": Acceptance 4.
   - "the generic decide carries": Acceptance 3.
   - the `error` outcome "refused at submit and at approve, one red-first case per cause",
     with `fail` accepted: Acceptance 5, 6, 7.
   - "the refusal is at the service layer, at submit and at approve": Task 3 Steps 1–4; "the
     evidence floor once approval goes through `approvals.submit`": Acceptance 8.
   - the DB CHECK "left to the fix slice": DP-3, not picked.
   - "the creation sites stay as triaged": Acceptance 16; `replace_rule_set` untouched.
   - "remove S2's temporary A.4 exemption, red first": Task 1, Acceptance 10; Task 0 Step 4
     catches any further exemption S2 adds.
   - follow-on 1: Acceptance 5–7 (it is in the acceptance); follow-on 2: Task 7,
     Acceptance 13, 14; DP-5, DP-6.
2. **Every design choice the Disposition leaves open is a DP with an owner** (DP-1, DP-3,
   DP-6); so are the three this plan found (DP-2, DP-4, DP-5) and the Task 0 STOP (DP-0).
   DP-0 and DP-4 have since been decided by the maintainer, and their rows quote the entries.
   No spec text is written without a ruling (Task 6).
3. **Repository literals checked at `1dd5e264`:** the line ranges in §"Write set";
   `ALLOWANCE_SITES` `test_approval_guard_static.py:37-46`; `approved_rows.py` `_EVIDENCE`
   and `_FLAG_ONLY`; `_AFTER["validation_rule"] = dict.fromkeys(_OUTCOMES, "review")`
   (`test_api_approvals.py:986`); `EVIDENCE_INCOMPLETE` registered (`errors.py:273`) and
   raised with 422 by `objectives.py:860`; `ValidationReportRow.error_count`
   (`models.py:1057`); the CHECK `approved_rule_dry_run_and_separate_approver`
   (`models.py:1201-1205`); `RuleOutcome.ERROR`, `RuleResult`'s required fields and
   `ValidationReport.counts`/`overall` (`model_schema/validation.py:65-77`, `:499-560`);
   `DEFAULT_POLICY`'s `validation_rule` entry (`model_schema/approvals.py:205-209`);
   `dry_run_rule_id` (`data_handlers.py:220`); the frontend callers (`rules.ts:86-99`).
4. **What was not executed.** Task 0's script was run (output above). The `python` samples
   were **not** assembled and run: they depend on DP-1 and DP-2, and on S2's shapes,
   none of which exist yet. The executor runs each red-first step and records it; a sample
   that does not run as written is a plan defect to report, not to work around.
5. **Type consistency.** `_require_executed_dry_run(session, *, workspace_id, row)` is called
   with that signature in Task 3 Steps 2, 3 and 4; `decide_and_carry` is defined in Task 3
   Step 5 and consumed in Task 4 Step 3 and Task 7 Step 2; `stored_dry_run_report` is
   defined in Task 2 Step 1 and consumed in Steps 2 and 4.
