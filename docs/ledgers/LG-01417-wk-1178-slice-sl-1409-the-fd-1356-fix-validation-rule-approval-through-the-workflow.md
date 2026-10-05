---
id: LG-1417
family: ledger
title: WK-1178 slice SL-1409 — the FD-1356 fix, a validation rule is approved only through the approval workflow (PL-1408), Task 0 containment and preconditions
status: closed
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

# LG-1417 — WK-1178 slice SL-1409, the FD-1356 fix

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
  Typing the `200` stays with FD-1416.
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

**Holds.** FD-1416: this slice changes no `to_dict` approval route's response and reads none anew (Task 0 read no
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

### Task 4 — the routes typed, the contract regenerated (2026-10-05, executor-1409-t4)

Base `3a431bcb6afe605b0fafaa0589c307cc1ee5d680` (Steps 2–3 were done there, Delta 7).
Red first, the two new tests in `backend/tests/test_validation_rule_approval.py`:
- `test_every_body_this_slice_edits_is_a_model_schema_type`, both parametrised paths red:
  `AssertionError: Decide is a route-local body, not a model_schema type` (the plan's cause)
  and `AssertionError: ValidationRuleSubmission is a route-local body, not a model_schema type`.
  **Cause differs from the plan's "the submit has no body"**: Steps 2–3 were pulled forward
  into Task 2+3's commit, so the body exists and is only unexported (`hasattr` is False).
- `test_the_decide_response_keeps_its_key_set`: green on first run (it pins existing
  behaviour); the plan's scratch proof: renaming `approvers_recorded` → `approvers_seen` in
  `to_dict` made it fail (`1 failed`), reverted (`git checkout`).
Green: `268 passed, 2 skipped` over `test_validation_rule_approval.py`, `test_contracts.py`,
`test_api_approvals.py`; `generate-contracts.py --check` exit 0 ("45 generated contracts
match the models"); `pnpm --dir frontend generate:api` and `type-check` exit 0; ruff check
clean; mypy clean (226 files); lint-imports 4 kept.
Files: `model_schema/approvals.py` (`Decide`, moved, name/fields/config kept),
`model_schema/__init__.py` (import lines + `__all__`: `Decide`, `ValidationRuleSubmission`
only), `backend/src/app/api/approvals.py` (route-local `Decide` and unused pydantic import
removed), `docs/contracts/openapi/generated.json` (regenerated), the test file, this ledger.
No `PL-1364` untyped-body guard entry was touched (none present). Decide's `200` unchanged.

### Task 5 — the frontend, red first (2026-10-05, executor-1409-t5)

Red (`pnpm --dir frontend exec vitest run` on `RuleSetView.test.ts`, `RuleBuilder.test.ts`, `src/api`), before any code: `Tests  8 failed | 16 passed (24)` in the two view files. Cause: no change-summary input exists — seven `Unable to find a label with the text of: Change summary`, and `will not submit without a change summary` failing on `toBeDisabled()` (the Submit button was enabled with an empty summary, and no body was sent). Cause matches the plan's prediction.

Code: `submitRule(ruleId, body)` takes `ValidationRuleSubmission` (generated, `schema.requests.d.ts`, aliased in `frontend/src/api/rules.ts`); `RuleBuilder.vue` gains a required "Change summary" input and disables its button while it is blank; `RuleSetView.vue` gains one "Change summary for <slug>" input per draft row, Submit disabled while blank, and `act` now reports through `explain`, which gains an `EVIDENCE_INCOMPLETE` message ("the rule's dry run did not execute"); `SUBMITTER_CANNOT_APPROVE` stays keyed on `code`. Deviation: the plan names `explain` only implicitly; folding `act`'s duplicate inline message into `explain` removes a second copy of the same code-keyed text.

Green: the three files above `Test Files  26 passed (26) / Tests  119 passed (119)`; full frontend `pnpm test` `97 passed / 615 passed`; `lint`, `type-check`, `build` exit 0. Files: `frontend/src/api/rules.ts`, `frontend/src/components/RuleBuilder.vue`, `frontend/src/views/RuleSetView.vue`, `frontend/src/components/__tests__/RuleBuilder.test.ts`, `frontend/src/views/__tests__/RuleSetView.test.ts`, this ledger.

### Task 6 — the spec texts, verbatim from RL-1407 (2026-10-05, executor-1409-t6)

Reading applied: PL-1408 Task 6 says "one commit with the code they describe". The code is already committed in Tasks 2–5 (`3a431bcb`, `c65a25fd`, `ec475a0a`), so this commit carries the six texts, the regenerated `docs/INDEX.md` and this entry. `<Task 6 date>` = 2026-10-05; `RL-<minted id>` = `RL-1407`. The texts were extracted by script from the minted record's §"The spec texts" (the fenced `text` blocks), not retyped; no wording of the executor's own.

Anchors, re-found by anchor text on the branch head `ec475a0a` (the plan's line numbers are stale for `06`; `01` still matched):
- text 1: after `> WK-677). This is the module's own step in the module's own terms, which is what §4.5 states.` (`01:927`), as a `>` line and the paragraph;
- text 2: `01:935` `` `REJECT_RATE_EXCEEDED`, `DERIVATION_NOT_MATERIALISED`. `` replaced;
- text 3: the `| **FR-351** |` row (`06:92`), end of the second cell. WK-674 S2 had not appended to it: the cell ended `…does not move the version's row.`, so text 3 follows that;
- text 4: the `| **Validation Rule** |` row in FR-363's table (`06:114`), after `` (`01` FR-50) ``;
- text 5: `01:523`, the end of §4.5 step 4;
- text 6: the `| **FR-50** |` row (`01:112`), after `` feeding an `approved` Model. ``.

Step 2: `git diff ec475a0a -- docs/specs/01-data-management.md docs/specs/06-governance.md` shows 4 appended rows or lines, 1 replaced line (text 2) and the 2 added lines (text 1). Each of the 4 removed lines that are appended-to starts, byte for byte, the line that replaces it (checked by script); no other line changed.

`python3 scripts/audit-docs.py`: first run failed check 31 (expected, LG 9719 working id) and check 39 (`docs/INDEX.md` stale, as the FR-50 and FR-351 rows are indexed). `python3 scripts/doc-index.py` regenerated it (two rows changed). Second run: `FAILED (1): check 31: gap in the full allocation between 1411 and 9719` only; check 10 passes.

Files: `docs/specs/01-data-management.md`, `docs/specs/06-governance.md`, `docs/INDEX.md`, this ledger. No test was run.

### Task 7, Steps 1–3 — the fixtures, the seed through the workflow, the reset script (2026-10-05, executor-1409-t7)

Scratch databases only; nothing was written to any `gipricing*` database, and `examples/fremtpl2/data/` of the root checkout
was only read (the two `.arff` files were **copied** into this worktree's gitignored `examples/fremtpl2/data/`;
`git check-ignore -v` names `.gitignore:61`). Created and dropped: `scratch_sl1409_base`, `scratch_sl1409_after` (see the end of the entry).

**Step 1 — the fixtures (Acceptance 14).** `ValidationRuleRow` moved into `_EVIDENCE` as `("validation_rule", "slug")` and out of
`_FLAG_ONLY` in `backend/tests/approved_rows.py`; the docstring's first paragraph reads "six evidence-only tables" and names a rule set,
not "a validation table", as flag-only. `pytest -q backend/tests/test_data_jobs.py backend/tests/test_reference_pin.py backend/tests/test_wf01_journey.py`: `8 passed, 1 warning in 14.94s`.

**Step 2 — the seed, red first (DP-5, Acceptance 21).**

1. The `("examples/fremtpl2/seed.py", "run")` entry is out of `ALLOWANCE_SITES`. Red, `pytest -q backend/tests/test_approval_guard_static.py`: `4 failed, 13 passed`.
   Each failure names exactly `examples/fremtpl2/seed.py::run`, the cause the plan states (the file still enters `approval_decision()` at `run`, now unpinned):
   - `test_approval_decision_is_entered_only_at_the_sanctioned_and_allowance_sites`: `Left contains one more item: 'examples/fremtpl2/seed.py::run'`
   - `test_every_pinned_site_really_enters_the_context`: `Extra items in the left set: ('examples/fremtpl2/seed.py', 'run')`
   - `test_a_planted_new_entry_site_is_refused` and `test_a_planted_second_function_in_an_allowed_file_is_refused`: `Left contains one more item: 'examples/fremtpl2/seed.py::run'`
2. `run` in `examples/fremtpl2/seed.py` now authors each rule with `rule_service.create_rule(..., actor=analyst, catalogue_id=catalogue_id_by_slug.get(slug))`
   (no `ValidationRuleRow` insert, no hand-recorded event, no `approval_decision` import).
3. The first version is ingested **before** the rule set is bound. Each rule is dry-run with the real `DATASET_VALIDATE` job and `dry_run_rule_id`, as the analyst;
   the seed stops (`SystemExit`, naming the rule) if the job does not succeed or the stored report has `error_count > 0`.
4. `submit_for_review(..., actor=analyst, change_summary=f"{rule_slug}: a freMTPL2 demo rule, dry-run against version 1")`, then, in one `unit_of_work`,
   `approval_service.decide(..., approver=approver, decision=DecisionKind.APPROVE, comment=...)` and `rule_service.apply_approval_decision(..., actor=approver, request=decided)`
   (the request id comes from `rule_service.open_request_for`, because `submit_for_review` returns the rule row, not the request: **the plan's "as `model.py:296-308` does" differs only there**).
   No `approval_decision()` block.
5. Then `replace_rule_set` and the unchanged `validate(first)`.
6. **No stop.** The reorder did not change what the seed demonstrates: base and after print the same `validate(first)` and `validate(second)` reports (the diff of the `validation:`, `fail`, `warn`, `skipped`, `promotion`, `version N is` lines is empty), and `ingest` did not refuse a dataset with no rule set.

Seed runs, `--rows 50000` (a sample; `seed.py --rows` is the script's own option), both rc 0, load average before each run 1.30 and 3.80 (`uptime`), gate slots 1 and 2 free (`flock -n`):

| Run | Tree | Seed.py | Database | Started (BST) | rc |
|---|---|---|---|---|---|
| before | detached worktree at `bf33eea6` (the merge base with `origin/main`, the slice's base tree), own `uv sync --all-packages`, removed after | that tree's | `scratch_sl1409_base` | 2026-10-05 11:45:12 | 0 |
| after | this worktree | this tree's | `scratch_sl1409_after` | 2026-10-05 11:45:46 | 0 |

**Which base I used, and why it differs from the lead's wording.** The lead's point 3 said "`ec475a0a`'s parent tree". That parent is `c65a25fd`, which already holds the enforcement, so a seed run on it would not be the base the plan means ("the same run at the base tree prints the seed's rule count"). I used the merge base `bf33eea6` with its own backend (the run needed the base `validation_rules.py`, because the base seed passes a fabricated `dry_run_report_id`).

FD-1356's follow-on script, restricted to the scratch database (its per-database query, verbatim, with `datname` fixed to the named database):

```text
scratch_sl1409_base builtin_approved=38 user_approved=9 user_approved_no_approved_request=9
scratch_sl1409_after builtin_approved=38 user_approved=9 user_approved_no_approved_request=0
```

The base line prints the seed's rule count (9) for `user_approved_no_approved_request` (the plan's red), the after line prints 0 with `user_approved` equal to the seed's rule count 9.

`git grep -nE '(^|[^_])approval_decision\b' -- examples/` prints nothing (exit 1 from `git grep`, no match).

`ruff check` (examples, scripts, backend/tests) and `mypy` (226 files) are clean.

**Step 3 — the reset script, red first (DP-6 (b), Acceptance 13).** `backend/tests/test_reset_unbacked_rule_approvals.py` written first (A, B, C in one workspace as A and C, and B built-in; D in a second workspace).
The test database is shared, so the assertions name the test's own rows and workspaces: the script's `reset(database)` returns the rows reset per workspace.

- Red (script absent): `4 failed`, each `FileNotFoundError: [Errno 2] No such file or directory: '…/scripts/reset-unbacked-rule-approvals.py'`. The cause is the plan's ("the script does not exist").
- Green with `scripts/reset-unbacked-rule-approvals.py`: `4 passed, 1 warning in 2.00s`. The literals are RL-1407 DP-6's: population as FD-1356's predicate (NOT EXISTS with the same workspace, `artifact_type`, ref, `approved`), `FOR UPDATE` (`with_for_update(of=ValidationRuleRow)`), per row `status = 'review'` and `approved_by = NULL`, then `audit.record(... actor=Principal(kind=ActorKind.SYSTEM, display="fd-1356-reset"), source=JobSource.SYSTEM, action="validation_rule.approval_reset", entity_ref=f"validation_rule:{row.slug}@{row.version}", before={"status": "approved", "approved_by": str(approved_by)}, after={"status": "review", "approved_by": None}, justification=...)`; `<RL-<minted id>>` is `RL-1407`; one `unit_of_work`; `audit.verify_chain` for every workspace written, inside it.
- Broken-input red 1 (the `NOT EXISTS` clause removed in a scratch edit): `1 failed, 3 passed`, `FAILED …::test_the_reset_leaves_a_built_in_and_a_backed_approval_alone` with `AssertionError: c was reset` / `assert 'review' == 'approved'` (C, the backed approval, is reset). Reverted (`cp` of the saved file; the green re-run `4 passed`).
- Broken-input red 2 (the `audit.record` call removed): `2 failed, 2 passed`: `…::test_the_reset_returns_an_unbacked_approval_to_review_with_one_event_each` (`AssertionError: a` / `assert 0 == 1` / `where 0 = len([])`) and `…::test_the_chain_of_every_workspace_written_still_verifies`. Reverted, `4 passed`.
- The script's own output, run on the scratch database `scratch_sl1409_base` (nine unbacked rules, one workspace; the DSN override is `GIP_DATABASE_URL`): first run `scratch_sl1409_base reset=9 workspaces=1 chain_verified=1`, rc 0; second run `scratch_sl1409_base reset=0 workspaces=0 chain_verified=0`, rc 0.

**Doubt, for the lead (not a stop).** RL-1407 says the script "runs on the database named `gipricing`, always" and also asks for the style of `revalidate-artifacts.py` with its `GIP_DATABASE_URL` override; I kept the override (the style the ruling names), so the script writes whatever DSN it is given and defaults to `gipricing`. Step 4's executor passes no override.

**Scratch databases:** created `scratch_sl1409_base`, `scratch_sl1409_after`; dropped at the end of the task (the Step 3a entry records the drop).

### Task 7, Step 3a — the pre-flight, red first (2026-10-05, executor-1409-t7)

`backend/tests/test_check_rule_sets_runnable.py` (new) and the wiring assertion in `backend/tests/test_demo_command.py`
(`test_the_rule_set_pre_flight_runs_after_the_seed_record_and_before_the_api_starts`) were written first.

- Red, `pytest -q backend/tests/test_check_rule_sets_runnable.py backend/tests/test_demo_command.py`: `4 failed, 13 passed`. Three failures are
  `FileNotFoundError: [Errno 2] No such file or directory: '…/scripts/check-rule-sets-runnable.py'` (the script does not exist) and the wiring test fails at
  `assert 'check-rule-sets-runnable.py' in 'def demo(*, rows: int | None, skip_seed: bool, frontend: bool) -> int: …'` (the step is absent). Both are the plan's causes.
- Green after `scripts/check-rule-sets-runnable.py` and the `run([...], step="pre-flight: the demo workspace's rule sets are runnable", env=env)` step in `scripts/demo.py`
  (immediately after `record = read_seed_record()`, before the API command, outside the `if not skip_seed:` block): `17 passed, 1 warning in 3.60s`.
  The script's literals are RL-1407 condition 2's: the stderr text for no rule set (`Workspace <workspace_id> has no rule set: the seed did not finish. Re-run the seed.`),
  `rule sets runnable: <n>`, exit 1 on a `PlatformError` with the error's detail on stderr; it calls `rule_service.rule_set_to_run` per dataset that has a rule set, in a read-only session.
  The test seam is `check(database, workspace_id, *, out, err)`, which returns the exit status.
- `ruff check` (scripts, backend/tests, examples) and `mypy` (226 files) clean.
- Real runs on the scratch databases (Step 4 takes the `gipricing` ones): on `scratch_sl1409_after` (the new seed) `rule sets runnable: 1`, rc 0;
  on `scratch_sl1409_base` after the reset script (`reset=9`) the run printed `Not approved: 01a10bab-11bb-7466-8b4f-71ecfbee30b4 (claim-count-non-negative@2, review), …` (nine members, each `review`) and rc 1;
  on a workspace id with no rule set `Workspace 01a10bab-0000-7000-8000-000000000000 has no rule set: the seed did not finish. Re-run the seed.`, rc 1.

**Scratch databases:** `scratch_sl1409_base` and `scratch_sl1409_after` created, used and dropped (`dropdb` ok; a count of `pg_database` rows `like 'scratch_sl1409%'` afterwards prints 0).
The temporary detached worktree `.claude/worktrees/sl-1409/.claude/worktrees/sl1409-base` was removed (`git worktree remove`). The two copied `.arff` files and the seed's `last-seed.json`
stay in this worktree's gitignored `examples/fremtpl2/data/`; the root checkout's `data/` was never written. `git status` shows nothing under `data/`.

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

### Task 7c (named deviation, Delta 16–17) — the seed re-runs against a seeded database (2026-10-05, executor-1409-t7c)

The defect, verified in code: `platform/workspaces.py` `ensure_member` looks the user up by `user_id` alone, and `run` in `examples/fremtpl2/seed.py` minted a fresh analyst id every run while passing the realm's fixed `(REALM_ISSUER, REALM_SUBJECT)`. Not edited here: `workspaces.py` (outside the write set; its docstring goes to FD 9717).

**Red first** (`test_the_seed_reruns_against_a_seeded_database`, two `seed.run(2000)` calls into one fresh scratch database, against the pre-fix seed), `pytest -q examples/fremtpl2/test_seed.py -k reruns`: `1 failed, 7 deselected in 20.15s`;
`sqlalchemy.exc.IntegrityError` wrapping `asyncpg.exceptions.UniqueViolationError: duplicate key value violates unique constraint "uq_users_issuer_subject"`,
`DETAIL:  Key (issuer, subject)=(http://localhost:8080/realms/gi-pricing, 84eea68e-a19e-46a0-9f35-a27cbd51c795) already exists.`

**Fix** (`run` in `examples/fremtpl2/seed.py`): read the `users` row for `(REALM_ISSUER, REALM_SUBJECT)`; the analyst's id is that row's id, else a minted one. Every later use (grants, `ensure_member`, rule actions, `last-seed.json`'s `analyst_id`) reads `analyst.id`, so all use the resolved id.
The test also asserts the second `last-seed.json` has a different `workspace_id` and the **same** `analyst_id` as the first. It runs on a scratch data directory (symlinks to the ARFFs; `DATA_DIR` monkeypatched), so no `last-seed.json` of this worktree or the root was touched, and skips when the ARFFs are absent.

**Green:** `pytest -q examples/fremtpl2/test_seed.py`: `8 passed in 30.15s`. Task 7a's touched tests (`test_approval_guard_static.py`, `test_reset_unbacked_rule_approvals.py`, `test_check_rule_sets_runnable.py`, `test_demo_command.py`): `38 passed, 1 warning in 10.19s`. `ruff check examples/fremtpl2/` clean (one import-order fix applied to the new test); `mypy` over 226 source files: no issues.

Scratch databases: `scratch_sl1409c_<8 hex>`, created and dropped by the test itself on every run (`DROP DATABASE … WITH (FORCE)` in `finally`); a query for `scratch_sl1409c%` after the last run returned no rows. No `gipricing*` database was written. Gate slots all four free (`flock -n`) before the first seed run.

Files: `examples/fremtpl2/seed.py`, `examples/fremtpl2/test_seed.py`, this ledger.

### Task 7, Step 4 — recovery, reset and the demo check on `gipricing` (2026-10-05, executor-1409-t7b then executor-1409-t7d)

All times are BST from `date`. The earlier executor (t7b) did Step 4.1's before-counts, the backup, A1, A3 and B1–B3, then stopped twice; this entry quotes its outputs by reference to the lead's dispatch record (`DISPATCH-WK-1178-SL1409-2026-10-04.md`, Deltas 14–16, local, not in the repository) and to the job tmp files named below, which are also local. I (t7d) re-verified the state before writing anything and then ran B4 onwards.

**The enforcement commits.** The rule approve route is a client of the approval workflow from `3a431bcb6afe605b0fafaa0589c307cc1ee5d680` (Tasks 1–3). Task 7a's seed and reset are `768ff6c3`, its pre-flight `df301c18d354d446606be11ed2b3251d37422560` (the amendment's A4 floor). Task 7c's seed fix is `d9b069fc8aa6ff820e38a7432cba22abc64d71f2`. Step 4 ran at `d9b069fc` for 4.2–4.5 and at the merge `c156e7274e8d07bc0e9eb1112590c2a259e2db94` (below) for 4.6–4.8.

**Preconditions at the resume (12:05–12:06).** gipricing's `alembic_version` was `c4a81f6d2e95`, equal to `uv run alembic heads` there. The root's `last-seed.json` and `last-seed.json.bak-20261005` both hashed to `ffc32f4ac31e43270323da7e2227a08a322fddc6d67748378266cf5620be71f3`. The worktree's `examples/fremtpl2/data/` held the two ARFF symlinks and no `last-seed.json`. `flock -n /tmp/slots/gate-1 true` and the same for `gate-2` both succeeded. No benchmark or pytest process ran (`pgrep -af '[b]ench|[p]ytest'` printed nothing). `uptime` read `load average: 1.06, 1.37, 1.55`. `GIP_DATABASE_URL` was unset (`env | grep -c GIP_DATABASE_URL` printed 0).

**4.1 Before (t7b, Delta 14).** gipricing `builtin_approved=532 user_approved=10 user_approved_no_approved_request=10`; follow-on script `TOTAL 5890/324/324` over 93 databases; the residual query (Acceptance 23, verbatim in `sl1409-residual.sh`) printed 0. **Gap, recorded:** the per-database before lines were not kept, so "every other database unchanged" rests on the aggregate check in 4.4.

**Backup (condition 1, t7b).** `cp -p` of the root record to `last-seed.json.bak-20261005`; both hashed to `ffc32f4a…71f3`, re-read by me at 12:06.

**B1 — migrate first (t7b, Delta 16).** From the worktree with demo.py's env (`GIP_DATABASE_URL=postgresql+asyncpg://gipricing:***@localhost:5432/gipricing`), `uv run alembic upgrade head`, 11:58:44–11:58:46, rc 0. Revision before `d3b955a63d6a`, after `c4a81f6d2e95`, equal to the branch's `alembic heads`; 8 revisions; upgrade only. This was needed because the first seed attempt (11:55:56–11:56:03, exit 1) failed with `column "platform_build" of relation "jobs" does not exist`, and `scripts/demo.py` runs `alembic upgrade head` before its seed where Step 4.2 did not.

**B2 — the abandoned partial seed.** Workspace `01a10bb4-c446-7b56-bb64-6ce3ff94ea6f` is an **abandoned partial seed of 2026-10-05 11:55:56 BST**. It stays; nothing was deleted. Recount at 12:05 and again at 12:06 (`sl1409-recount.sh`): 38 built-in rules (`approved`) and 9 user rules (`draft`), 1 dataset, 0 dataset versions, 0 jobs, 0 rule sets. This corrects the first report's "47 built-ins".

**Second stop (11:59:07–11:59:10).** The full seed exited 1 on `uq_users_issuer_subject`: the partial seed had created the realm user (issuer `http://localhost:8080/realms/gi-pricing`), and `examples/fremtpl2/seed.py` minted a fresh analyst id on every run. Task 7c (the section above) fixed this in `seed.py`, red first.

**B3 / A1 — the data directory.** Before the recovery seed, `ls -la` of the worktree's `examples/fremtpl2/data/` showed two symlinks (`freMTPL2freq.arff`, `freMTPL2sev.arff`, each to the root's file) and no `last-seed.json`.

**B4 — the full seed (4.2, conditions 2 and 3).** DSN `postgresql+asyncpg://gipricing:***@localhost:5432/gipricing` (demo.py's, as `GIP_DATABASE_URL`; `sl1409-seed-full.sh`), no `--rows` (all 678,013), `timeout 3000 uv run … python examples/fremtpl2/seed.py`. **Start 12:06:15, end 12:07:05, duration 50 s, exit code 0** (`sl1409-seed-full.out`: `seed exit code: 0`). New workspace `01a10bbe-3a03-740c-8d4b-a6af38d2dd4b`. Its `dataset_versions` count is 4 (2 `draft`, 1 `failed`, 1 `validated`; version 1 is refused with `VALIDATION_HAS_FAILURES`, version 2 holds 677,442 rows). The seed output says "9 rules approved through the workflow across four layers, and `01` §4.4's 38-rule catalogue". gipricing's workspace count went from 29 to 30.

**A2 — the new record is this seed's.** The worktree's `last-seed.json` had mtime `2026-10-05 11:06:18 UTC` (12:06:18 BST), after the seed's 12:06:15 start. The workspace exists in gipricing: `select id, name, created_at from workspaces where id='01a10bbe-…'` printed `01a10bbe-3a03-740c-8d4b-a6af38d2dd4b|freMTPL2 demo|2026-10-05 11:06:18.690084+00`.

**The analyst id.** After Task 7c the seed resolves the analyst to the existing realm user `01a10bb4-c446-7b66-b87c-dc1ae01246a3` (created by the abandoned partial seed). The new `last-seed.json`'s `analyst_id` equals it:

```text
{
  "workspace_id": "01a10bbe-3a03-740c-8d4b-a6af38d2dd4b",
  "analyst_id": "01a10bb4-c446-7b66-b87c-dc1ae01246a3",
  "actuary_id": "01a10bbe-3a6c-7123-9f8d-1a3f989bd452"
}
```

**The copy (condition 4), 12:07:32.** Old record, sha256 `ffc32f4ac31e43270323da7e2227a08a322fddc6d67748378266cf5620be71f3`:

```text
{
  "workspace_id": "01a044dc-4e8f-7d58-a39e-1271642267c9",
  "analyst_id": "01a044dc-4e8f-7b69-8aa5-46ad0aa445da",
  "actuary_id": "01a044dc-4e8f-78f7-9a76-97638e69da6c"
}
```

New record: sha256 `9b3aada8b5f0433cca4095589812935954bf7e05878d07392286f1e8ecf1807c`, identical in the worktree and the root after `cp`. **Id diff:** a new workspace was minted; the old `01a044dc-…` was not kept, because it was already absent from gipricing (Delta 14: `count(*)` 0; the earliest workspace is 2026-09-17), so there was nothing runnable to keep. The analyst id changed from `01a044dc-4e8f-7b69-8aa5-46ad0aa445da` to the realm user's; the actuary id changed to `01a10bbe-3a6c-7123-9f8d-1a3f989bd452`. **Premise correction (Delta 15):** PL-1408 Task 7 and RL-1407 say the recovery seed "keeps the workspace the demo uses runnable"; that was false on 2026-10-05, for the reason just given. **Rollback:** `cp -p /home/puzhenhao1989/gi-pricing-plan/examples/fremtpl2/data/last-seed.json.bak-20261005 /home/puzhenhao1989/gi-pricing-plan/examples/fremtpl2/data/last-seed.json`, then `sha256sum` it and expect `ffc32f4a…71f3`. The `.bak` still hashed to that value at 12:07:32.

**4.3 Reset, 12:07:40–12:07:42, rc 0** (`GIP_DATABASE_URL` unset, so the script used its gipricing default; A3):

```text
gipricing reset=10 workspaces=9 chain_verified=9
```

**4.4 After, 12:07:51–12:08:17.** Follow-on script (`followon.sh`; `sl1409-after-followon.out`):

```text
gipricing builtin_approved=608 user_approved=9 user_approved_no_approved_request=0
gipricing_agent-abcc22f1053f096f6_8287cba2 builtin_approved=532 user_approved=10 user_approved_no_approved_request=10
gipricing_tree-s3 builtin_approved=532 user_approved=10 user_approved_no_approved_request=10
gipricing_w37-6-run2-gate-1789690960 builtin_approved=532 user_approved=10 user_approved_no_approved_request=10
gipricing_wt-d9d13-redo builtin_approved=1710 user_approved=101 user_approved_no_approved_request=101
gipricing_wt-paths-d9-d13 builtin_approved=2052 user_approved=183 user_approved_no_approved_request=183
databases=93 with_tables=90 without_table_or_error=3
TOTAL builtin_approved=5966 user_approved=323 user_approved_with_no_approved_request=314
```

`gipricing` prints `user_approved_with_no_approved_request=0` (Acceptance 13). **`builtin_approved` 608 = 532 + 38 + 38**, the first the before figure, the second the abandoned partial seed `01a10bb4`, the third the new workspace `01a10bbe`. The per-workspace queries, each run read-only in the `gipricing` database:

```text
select '01a10bbe-3a03-740c-8d4b-a6af38d2dd4b builtin_approved='||count(*) from validation_rules where workspace_id='01a10bbe-3a03-740c-8d4b-a6af38d2dd4b' and builtin and status='approved'
→ 01a10bbe-3a03-740c-8d4b-a6af38d2dd4b builtin_approved=38
select '01a10bb4-c446-7b56-bb64-6ce3ff94ea6f builtin_approved='||count(*) from validation_rules where workspace_id='01a10bb4-c446-7b56-bb64-6ce3ff94ea6f' and builtin and status='approved'
→ 01a10bb4-c446-7b56-bb64-6ce3ff94ea6f builtin_approved=38
```

The new workspace's 9 user rules are all `approved` (through the workflow); `01a10bb4`'s 9 are all `draft`. **Every other database unchanged, as an aggregate** (the per-database before lines are the gap above): the TOTAL minus gipricing is `5890−532, 324−10, 324−10` before and `5966−608, 323−9, 314−0` after, which is `5358/314/314` both times.

Task 0's script (`task0.sh`, `sl1409-after-task0.out`), last line, after the reset:

```text
databases=93 with_tables=90 without_table_or_error=3
TOTAL route_approved=0 self_approved=0 user_approved_no_approved_request=314
```

**The residual query (Acceptance 23), verbatim (`sl1409-residual.sh`), before 0, after 15.** Run in `BEGIN READ ONLY … ROLLBACK` on `gipricing`:

```sql
select count(*) from dataset_versions dv where dv.status='validated' and exists (select 1 from (select r.body from validation_reports r where r.dataset_version_id=dv.id and r.workspace_id=dv.workspace_id order by r.created_at desc limit 1) latest cross join lateral jsonb_array_elements(latest.body->'results') res join validation_rules v on v.id=(res->>'rule_id')::uuid where v.status<>'approved' and v.builtin is not true);
```

The 15 are pre-fix workspaces' validated versions whose latest report used the 10 rules the reset has now returned to `review`: 10 distinct rules (`exposure-positive-3149b9`, `-f8d380`, `-729c73`, `-94f560`, `-ef38a8`, `-36f698`, `-e711ae`, `-ebc8bf`, `-16383b`, `-9cbc27`) in 9 workspaces, `01a0aece-e697-…`, `-ee07-…`, `-f3bc-…` (2 versions), `-fcbb-…` and `01a0aecf-047b-…`, `-0bc8-…` (2), `-18db-…` (2), `-2388-…` (3), `-3595-…` (2). The lead's verdict (2026-10-05): this is the ruling's stated end state, measured and not refused (RL-1407 §"FD 9748"); it is recorded and not fixed here, and it opens no new finding.

**The 15 Dataset Versions (the maintainer's (by delegation) condition, added after the first commit of this entry).** Listed as `workspace_id|dataset_version_id` from the residual query above (`sl1409-d9.out`):

```text
01a0aece-e697-72a9-a8bd-0f02d88399f1|01a0aece-e894-7746-b263-44f0451bf223
01a0aece-ee07-7438-9cf0-fe9fa7484b9a|01a0aece-ef52-702f-bb6b-4ac0e01939a2
01a0aece-f3bc-7e4e-b95b-dc3c6e416f76|01a0aece-f522-79e8-b3a3-264df5ad7e7f
01a0aece-f3bc-7e4e-b95b-dc3c6e416f76|01a0aece-fa5b-7365-bbf3-fc83c6b5bb70
01a0aece-fcbb-79a0-abfe-8ade478d5d91|01a0aece-fe22-7b58-b03c-6f81b77085d9
01a0aecf-047b-7dea-951a-98f796313e87|01a0aecf-061b-7103-943f-209fb246eadc
01a0aecf-0bc8-7cd5-a955-ed07b42b7053|01a0aecf-0dab-752b-9d22-8e4a2cfa1e0f
01a0aecf-0bc8-7cd5-a955-ed07b42b7053|01a0aecf-154e-7677-8d0e-ded36445a715
01a0aecf-18db-7a38-8dcb-7ef28288f4dd|01a0aecf-1a8f-7831-80c0-24f67dbd865c
01a0aecf-18db-7a38-8dcb-7ef28288f4dd|01a0aecf-20ca-7d7c-8aaa-4b171cd62c6f
01a0aecf-2388-7b85-bdf8-8b50647e2c9d|01a0aecf-24f4-754a-8064-a5d815f0d107
01a0aecf-2388-7b85-bdf8-8b50647e2c9d|01a0aecf-2b26-7153-8f32-964dd59251fc
01a0aecf-2388-7b85-bdf8-8b50647e2c9d|01a0aecf-3243-7fc2-bda0-5c6be1a33a26
01a0aecf-3595-7494-9ffa-6e4f22e9bd65|01a0aecf-3765-7c00-b41f-84c2f2307515
01a0aecf-3595-7494-9ffa-6e4f22e9bd65|01a0aecf-3c31-7844-a07e-c98bb27bf924
```

**Are any referenced by an approved model or a deployed rating version?** Read from `backend/src/app/db/models.py`: `ModelRow` (`models.dataset_version_id`, `models.status`), `RatingVersionRow` (`rating_versions.dataset_version_id`) and `DeploymentRow` (`deployments.environment_id`, `deployments.rating_version_ref`, which holds `<rating version slug>@<version>`, e.g. `fremtpl2-demo@1`). Run on `gipricing`, `BEGIN READ ONLY … ROLLBACK`, run after the ledger's first commit. The query (`d9.sql`; the second statement prints the list above):

```sql
WITH residual_dv AS (
  SELECT dv.id, dv.workspace_id FROM dataset_versions dv WHERE dv.status='validated' AND EXISTS (SELECT 1 FROM (SELECT r.body FROM validation_reports r WHERE r.dataset_version_id=dv.id AND r.workspace_id=dv.workspace_id ORDER BY r.created_at DESC LIMIT 1) latest CROSS JOIN LATERAL jsonb_array_elements(latest.body->'results') res JOIN validation_rules v ON v.id=(res->>'rule_id')::uuid WHERE v.status<>'approved' AND v.builtin IS NOT TRUE))
SELECT 'residual_dataset_versions='||(SELECT count(*) FROM residual_dv)
 ||' approved_models_referencing='||(SELECT count(*) FROM models m JOIN residual_dv d ON d.id=m.dataset_version_id AND d.workspace_id=m.workspace_id WHERE m.status='approved')
 ||' models_any_status_referencing='||(SELECT count(*) FROM models m JOIN residual_dv d ON d.id=m.dataset_version_id AND d.workspace_id=m.workspace_id)
 ||' rating_versions_referencing='||(SELECT count(*) FROM rating_versions rv JOIN residual_dv d ON d.id=rv.dataset_version_id AND d.workspace_id=rv.workspace_id)
 ||' deployed_rating_versions_referencing='||(SELECT count(*) FROM deployments dp JOIN environments e ON e.id=dp.environment_id JOIN rating_versions rv ON dp.rating_version_ref=rv.slug||'@'||rv.version AND dp.workspace_id=rv.workspace_id JOIN residual_dv d ON d.id=rv.dataset_version_id AND d.workspace_id=rv.workspace_id)
 ||' deployments_total='||(SELECT count(*) FROM deployments);
```

```text
residual_dataset_versions=15 approved_models_referencing=0 models_any_status_referencing=11 rating_versions_referencing=0 deployed_rating_versions_referencing=0 deployments_total=0
```

**None of the 15 is referenced by an approved model or by a rating version deployed in an Environment** (0 and 0; `gipricing` holds no deployment at all). 11 `models` rows in other statuses reference some of them (not asked, recorded).

**The root checkout's HEAD for the condition 5 retry.** The root's reflog (`git -C /home/puzhenhao1989/gi-pricing-plan reflog`) shows `5ff49c6d` until a fast-forward to `072c56e1ba386a790160ac4d90ad667f611df67c` at 12:10:45 BST, and `rev-parse HEAD` printed `072c56e1ba386a790160ac4d90ad667f611df67c` afterwards. So the first (failed) run began at `5ff49c6d`, and the retry (12:12:57–12:17:57) ran at `072c56e1ba386a790160ac4d90ad667f611df67c`. The first run's 12:09:02 start and its `Running upgrade` line are as stated above; the root moved to `072c56e1` while that run was still in progress.

**4.5 Second reset, 12:08:44, rc 0:**

```text
gipricing reset=0 workspaces=0 chain_verified=0
```

**Condition 5 — the demo check from the root checkout.** Mode: `uv run --directory /home/puzhenhao1989/gi-pricing-plan python scripts/demo.py --skip-seed --no-frontend` (the lightest: no seed, no frontend; it reads `last-seed.json`, migrates, starts the API and queries `GET /api/v1/models?status=approved` as the record's analyst in the record's workspace). **First run, 12:09:02–12:11:27, exit 1.** The root is on main (`5ff49c6d`) and its demo ran `alembic upgrade head` on `gipricing`, moving it from `c4a81f6d2e95` to `e5b7d9f1a3c6` (WK-690 Slice 3's migration, which this branch lacked): `Running upgrade c4a81f6d2e95 -> e5b7d9f1a3c6, custom_objectives: store the expression arm`. The API then died on import, `ModuleNotFoundError: No module named 'sympy'`, because the root venv was stale; the demo also started the `gi-pricing-keycloak-1` container (part of the demo's `auth` profile), which stays up because the demo uses it. **Lead decision D1 authorised `uv sync --all-packages` in the root**, run 12:12:53 (rc 0): `+ mpmath==1.3.0`, `+ sympy==1.14.0`, `~ pricing-core==0.1.0`, `- pyjwt==2.13.0`, `+ pyjwt==2.14.0`. **Second run, 12:12:57–12:17:57** (killed by my `timeout -s INT 300` once the API was ready; `rc=124` is that timeout): the migrations step printed no `Running upgrade` line (a no-op), then `WF-698 demo subset: 1 approved model(s)` and `API ready`. That request used the root's new `last-seed.json`, so it resolved the new workspace `01a10bbe-3a03-740c-8d4b-a6af38d2dd4b`. No uvicorn process was left and port 8000 was free afterwards. The root's `scripts/demo.py` is main's and has no pre-flight step, so this check proves the record, not the pre-flight.

**The merge (D2), committed 12:18:37.** gipricing was now one migration ahead of the branch, so `origin/main` (`072c56e1ba386a790160ac4d90ad667f611df67c`) was merged into the branch: `c156e7274e8d07bc0e9eb1112590c2a259e2db94`, parents `d9b069fc8aa6ff820e38a7432cba22abc64d71f2` and `072c56e1`. One conflict, `docs/INDEX.md`, resolved by `python3 scripts/doc-index.py` (then `--check`: `OK (byte-stable)`). `packages/model-schema/src/model_schema/__init__.py` merged cleanly and holds all four names (`Decide`, `ValidationRuleSubmission`, `DerivedBlock`, `ObjectiveParameter`), each in its import block and `__all__`. `uv run python scripts/generate-contracts.py --check`: `45 generated contracts match the models`. `uv run alembic heads` prints `e5b7d9f1a3c6 (head)`, equal to gipricing's `alembic_version`. Targeted tests after the merge, `pytest -q backend/tests/test_reset_unbacked_rule_approvals.py backend/tests/test_demo_command.py backend/tests/test_check_rule_sets_runnable.py examples/fremtpl2/test_seed.py`: `29 passed, 1 warning in 33.80s`. No full suite (Task 8 gates).

**4.6 The demo check (Acceptance 22).** The query (`acc22.sql`, `BEGIN READ ONLY … ROLLBACK`, parameter `ws`) reads: `declared` = the members in the `rules` array of the workspace's latest rule set; `executed` = the distinct `rule_id` values in the `results` of the latest validation report of the workspace's `validated` dataset version; per member, `validation_rules.status` and whether `dry_run_report_id` resolves to a `validation_reports` row of the workspace, with its `error_count`; the two set differences. **On `gipricing`** (workspace `01a10bbe-3a03-740c-8d4b-a6af38d2dd4b`; `sl1409-acc22-gipricing.out`):

```text
rule_set=01a10bbe-4be0-7ffe-943f-0424451e2f9b@1 status=approved declared=9
report=515c46c7-6fa0-478e-8f74-e5fda0d9944e executed=9
f|approved|f|t|0|9
declared_not_executed=0 executed_not_declared=0
```

The third row is `builtin|status|no_report_id|report_resolves|error_count|count`: 9 members, none built-in, all `approved`, each with a `dry_run_report_id` that resolves to a report with `error_count = 0`. **executed == declared (9 == 9).** **On a fresh database** (`scratch_sl1409_acc22`, `createdb` then `alembic upgrade head` at `e5b7d9f1a3c6`, then the seed from the merged tree with `--rows 50000`, 12:20:07–12:20:37, exit 0, workspace `01a10bca-eab0-744f-a0f2-ff56208d0901`; `sl1409-acc22-scratch.out`):

```text
rule_set=01a10bca-fb27-7cdd-9281-f816f1026b5c@1 status=approved declared=9
report=831183bd-13cd-4da1-a176-22de2387972f executed=9
f|approved|f|t|0|9
declared_not_executed=0 executed_not_declared=0
```

**4.7 The pre-flight.** **Red, on a scratch database** (`scratch_sl1409_red`, a `createdb -T gipricing` clone taken after the reset, so it holds the reset workspaces). The worktree's `last-seed.json` named the pre-fix workspace `01a0aece-e697-72a9-a8bd-0f02d88399f1` for this run only, then was restored. `GIP_DATABASE_URL=…/scratch_sl1409_red uv run python scripts/demo.py --skip-seed --no-frontend`, 12:21:02–12:21:49, **exit 1**:

```text
── pre-flight: the demo workspace's rule sets are runnable ─────
Not approved: 01a0aece-e765-7f90-9a60-43190d20e77d (exposure-positive-3149b9@1, review). A rule set runs only approved rules (`01` FR-50). The way back, for each rule: attach a new dry run (POST /api/v1/validation-rules/{id}/dry-run), then submit an approval request (POST /api/v1/validation-rules/{id}/submit for a draft rule, POST /api/v1/approval-requests for a rule in review), and have an approv…

  pre-flight: the demo workspace's rule sets are runnable failed (uv run python scripts/check-rule-sets-runnable.py 01a0aece-e697-72a9-a8bd-0f02d88399f1 → 1).
```

(The printed detail is cut at 400 characters here; `sl1409-preflight-red.out` holds the whole line.) **Green, on `gipricing`** with the new record, from the worktree, 12:21:53–12:23:53 (killed by my `timeout -s INT 120` after the API was ready; `rc=124`):

```text
── pre-flight: the demo workspace's rule sets are runnable ─────
rule sets runnable: 1
── API on :8000 ────────────────────────────────────────────────
  WF-698 demo subset: 1 approved model(s)
```

**4.8 The release note's pre-upgrade query** (RL-1407 §"The maintainer's three conditions", condition 3, the `sql` block, verbatim; `relnote.sql`), on `gipricing`, `BEGIN READ ONLY … ROLLBACK`. It prints **10 rows**, one per reset rule, each `review`, none in the new workspace (0 rows for `01a10bbe-…`). The ruling's pre-reset run printed 0 rows; the 10 are the reset's own result, the same 10 rules as the residual. First three rows (`sl1409-relnote-base.out` holds all ten):

```text
01a0aece-e697-72a9-a8bd-0f02d88399f1|01a0aece-e70a-7fa1-9ae7-580775b49327|1|01a0aece-e765-7f90-9a60-43190d20e77d|exposure-positive-3149b9|1|review
01a0aece-ee07-7438-9cf0-fe9fa7484b9a|01a0aece-ee52-7b7e-99d0-2f3c363b15ee|1|01a0aece-ee91-70cb-9c01-6f92c5f008a9|exposure-positive-f8d380|1|review
01a0aece-f3bc-7e4e-b95b-dc3c6e416f76|01a0aece-f40e-740b-824d-0cee66b16c0a|1|01a0aece-f459-721b-9f6a-80fa49aac3fb|exposure-positive-729c73|1|review
```

**The two controls, on the `rules`-form set** (the new workspace's rule set holds `body -> 'rules'`, not `rule_ids`), each in a rolled-back transaction, the query output filtered to the new workspace. One member moved to `review` (`UPDATE validation_rules SET status='review' WHERE id='01a10bbe-4c4a-707e-87b8-5bcc07ea757e'` → `UPDATE 1`):

```text
01a10bbe-3a03-740c-8d4b-a6af38d2dd4b|01a10bbe-4be0-7ffe-943f-0424451e2f9b|1|01a10bbe-4c4a-707e-87b8-5bcc07ea757e|columns-present|1|review
```

One stored set re-pointed at a missing id (`UPDATE validation_rule_sets SET body=jsonb_set(body,'{rules,0,rule_id}', to_jsonb('00000000-0000-7000-8000-000000000000'::text)) WHERE workspace_id='01a10bbe-…'` → `UPDATE 1`):

```text
01a10bbe-3a03-740c-8d4b-a6af38d2dd4b|01a10bbe-4be0-7ffe-943f-0424451e2f9b|1|00000000-0000-7000-8000-000000000000|||missing
```

Both rolled back (afterwards the rule reads `approved` and the set's first `rule_id` is `01a10bbe-4c4a-707e-87b8-5bcc07ea757e`). The ruling's two controls on the legacy `rule_ids` form were its own run and are not repeated; the 10 base rows above are that form's live `review` result.

**Scratch databases.** Created: `scratch_sl1409_acc22` (12:20:02), `scratch_sl1409_red` (12:20:53). Dropped, both, after 4.8 (`dropped scratch_sl1409_acc22`, `dropped scratch_sl1409_red`); `select count(*) from pg_database where datname like 'scratch_sl1409%'` printed 0.

**A5.** The worktree's two ARFF symlinks and `last-seed.json` were removed; `ls -la examples/fremtpl2/data/` then shows an empty directory and `git status --short` shows nothing under `data/`. The new record lives at the root's path.

**State left.** gipricing at `e5b7d9f1a3c6`; workspaces `01a10bb4-c446-7b56-bb64-6ce3ff94ea6f` (abandoned partial seed) and `01a10bbe-3a03-740c-8d4b-a6af38d2dd4b` (the demo workspace); the root's venv synced; the keycloak container up.

### Task 8 Step 2 — the slice summary (2026-10-05 12:29 BST, executor-1409-t8a)

Compiled at branch head `649916941322d42b1b8935a2e98e61ec4cd4a1ec` against `origin/main`
`072c56e1ba386a790160ac4d90ad667f611df67c` (`git fetch origin` first, then `git rev-parse origin/main`). It cites the entries above
and does not copy them. **Task 8 Step 1, the full gate, is not run here**: it runs once, at the minted head, after the slice audit
(the order of the lead's brief). No test and no gate was run for this entry.

**1. Task 0's run.** Section "Task 0": containment, 2026-10-05 10:57:54 to 10:58:15 BST, exit code 0, last line
`TOTAL route_approved=0 self_approved=0 user_approved_no_approved_request=373`. The DP-0 export's `sha256sum -c` printed OK for six of six.

**2. The reds of Acceptance 2–10 and 15.** Each red was recorded before the code that turned it green. The printed lines are in the
sections named; the rows below name the Acceptance, the printed line and the anchor.

| Acc. | Test (base tree) | Printed line | Cause (ledger) | Anchor |
|---|---|---|---|---|
| 2 | `test_one_approval_under_a_quorum_of_two_leaves_the_rule_in_review` | `assert 'approved' == 'review'` | the direct route approves on one call | Tasks 2 and 3, red table |
| 2 | `test_an_approver_without_a_policy_role_is_refused` | `assert 200 == 403` | the direct route checks no policy role | same |
| 2 | `…first_of_two` rows of `test_a_decision_moves_the_version…` | none: they passed on the base tree | the plan expected them red; recorded as controls | same, "Passed on the base tree" |
| 3 | `…records_it_truly[validation_rule-approve]` | `assert 'review' == 'approved'` | the carry has no `validation_rule` branch | same |
| 3 | `…[validation_rule-reject]`, `[…-request_changes]` | `assert 'review' == 'draft'` | same | same |
| 4 | `test_the_approve_route_decides_through_the_workflow` | `ValueError: not enough values to unpack (expected 1, got 0)` | the submit files 0 requests | same |
| 4 | `test_the_carry_records_the_request_it_carried` | same line | same | same |
| 5 | `test_an_error_dry_run_is_refused_at_submit` (3 cases) | `assert 200 == 422` | submit does not read the report | same |
| 6 | `test_an_error_dry_run_is_refused_at_approve` (3 cases) | `assert 200 == 422` | the generic decide has no evidence check | same |
| 7 | `test_a_fail_dry_run_is_still_approvable` | `ValueError: not enough values to unpack (expected 1, got 0)` | **red on the base tree, not the plan's "passes on the base tree"**: the base submit files no request (a plan defect, Delta 7 item 3) | same, Deviation 3 |
| 8 | `test_the_generic_submit_refuses_an_error_dry_run` | `assert 201 == 422` | the resolver checks the status only | same |
| 9 | `test_a_dry_run_report_that_cannot_be_read_is_refused` | `assert 200 == 422` | a dangling report id is accepted | same |
| 10 | `test_approval_decision_is_entered_only_at_the_sanctioned_and_allowance_sites` | `AssertionError: assert ['backend/src...approve_rule'] == []` | `approve_rule` still enters `approval_decision()`, no longer pinned | Task 1 |
| 10 | `test_every_pinned_site_really_enters_the_context` | `AssertionError: assert {('backend/sr...d.py', 'run')} == frozenset({('....p...` | same site, entered and not pinned | Task 1 |
| 15 | `test_every_body_this_slice_edits_is_a_model_schema_type` (both paths) | `AssertionError: Decide is a route-local body, not a model_schema type`; `AssertionError: ValidationRuleSubmission is a route-local body, not a model_schema type` | the bodies were not `model-schema` exports (cause differs from the plan's "no body": Delta 7 item 1) | Task 4 |
| 15 | `test_the_decide_response_keeps_its_key_set` | green on first run (it characterises existing behaviour; PL-1408 DP-4); a scratch rename in `to_dict` failed it (`1 failed`), reverted | planned | Task 4 |

Totals of the red runs: Tasks 2 and 3 `21 failed, 125 passed, 3 warnings in 121.59s` (also carries the Acceptance 11, 12, 19 and 25 reds, listed
in that table); Task 1 `2 failed, 15 deselected, 2 warnings in 1.95s`. Green after Task 3: `212 passed, 4 warnings in 142.33s`; after Task 4:
`268 passed, 2 skipped`. The reds of Acceptance 13, 14, 21 and 26 are in the Task 7 entries and are not part of this list.

**3. Task 7's three counts, and the residual.** The follow-on script's predicate is FD-1356's (`user_approved_no_approved_request`).
- **Before:** `gipricing` `user_approved_no_approved_request=10` (`builtin_approved=532 user_approved=10`); all databases `TOTAL 5890/324/324` over 93 databases
  (Task 7, Step 4, "4.1"). On the scratch base database of the seed run (Acceptance 21): `9`.
- **After:** `gipricing` `user_approved_with_no_approved_request=0`; `TOTAL 5966/323/314` (Step 4, "4.4"). `builtin_approved` 608 = 532 + 38 + 38. On the scratch
  after database: `0` with `user_approved=9`.
- **Reset, as the plan defines it** (DP-6 (b), the script's own output): `gipricing reset=10 workspaces=9 chain_verified=9`, then the second run `reset=0 workspaces=0 chain_verified=0`.
  Task 0's script after the reset ends `TOTAL route_approved=0 self_approved=0 user_approved_no_approved_request=314`.
- **Residual (Acceptance 23): 15** Dataset Versions (before the seed and reset: 0). **D9 result** (the maintainer's (by delegation) condition): `residual_dataset_versions=15
  approved_models_referencing=0 models_any_status_referencing=11 rating_versions_referencing=0 deployed_rating_versions_referencing=0 deployments_total=0`.
  Per the lead's Delta 21, the slice audit names the residual as accepted under RL-1407. The 15 ids and 9 workspace ids are listed in Step 4.

**4. Acceptance 18: the write-set reconciliation.** `git diff --stat origin/main...HEAD` at head `649916941322d42b1b8935a2e98e61ec4cd4a1ec`, with
`origin/main` = `072c56e1ba386a790160ac4d90ad667f611df67c`, verbatim (this entry's own commit then adds its lines to the ledger row):

```text
 backend/src/app/api/approvals.py                   |  51 +-
 backend/src/app/api/validation.py                  |  49 +-
 backend/src/app/errors.py                          |   4 +
 backend/src/app/platform/validation_rules.py       | 405 ++++++---
 backend/src/app/worker/data_handlers.py            |   9 +-
 backend/tests/approved_rows.py                     |   7 +-
 backend/tests/dry_run_reports.py                   |  78 ++
 backend/tests/test_api_approvals.py                |  32 +-
 backend/tests/test_api_datasets.py                 |  23 +-
 backend/tests/test_approval_guard.py               |   4 +-
 backend/tests/test_approval_guard_allowance.py     |  23 +-
 backend/tests/test_approval_guard_static.py        |   4 +-
 backend/tests/test_check_rule_sets_runnable.py     | 155 ++++
 backend/tests/test_demo_command.py                 |  25 +
 .../tests/test_reset_unbacked_rule_approvals.py    | 188 +++++
 backend/tests/test_validation_rule_approval.py     | 805 +++++++++++++++++++++
 docs/INDEX.md                                      |   7 +-
 docs/contracts/openapi/generated.json              |  31 +-
 ...alidation-rule-approval-through-the-workflow.md | 721 ++++++++++++++++++
 docs/specs/01-data-management.md                   |   8 +-
 docs/specs/06-governance.md                        |   4 +-
 examples/fremtpl2/seed.py                          | 146 ++--
 examples/fremtpl2/test_seed.py                     |  63 ++
 frontend/src/api/rules.ts                          |  11 +-
 frontend/src/components/RuleBuilder.vue            |  13 +-
 .../src/components/__tests__/RuleBuilder.test.ts   |  17 +-
 frontend/src/views/RuleSetView.vue                 |  37 +-
 frontend/src/views/__tests__/RuleSetView.test.ts   |  26 +
 packages/model-schema/src/model_schema/__init__.py |   4 +
 .../model-schema/src/model_schema/approvals.py     |  10 +
 .../model-schema/src/model_schema/validation.py    |   9 +
 scripts/check-rule-sets-runnable.py                | 102 +++
 scripts/demo.py                                    |   8 +
 scripts/reset-unbacked-rule-approvals.py           | 140 ++++
 34 files changed, 2966 insertions(+), 253 deletions(-)
```

Reconciled file by file against PL-1408 §"Write set". 34 files: 30 in the write set (the ledger included), 2 generated, 2 named additions, none outside.

| File | Verdict | Write-set row |
|---|---|---|
| `backend/src/app/platform/validation_rules.py` | in | its own row (edited and added functions) |
| `backend/src/app/api/approvals.py` | in | its own row (`decide_and_carry`, `Decide` removed) |
| `backend/src/app/worker/data_handlers.py` | in | its own row |
| `backend/src/app/errors.py` | in | its own row (`RULE_VERSION_IMMUTABLE`) |
| `backend/src/app/api/validation.py` | in | its own row |
| `packages/model-schema/src/model_schema/validation.py` | in | the `validation.py` / `__init__.py` row |
| `packages/model-schema/src/model_schema/approvals.py` | in | the `approvals.py` / `__init__.py` row (`Decide`) |
| `packages/model-schema/src/model_schema/__init__.py` | in | both rows (`ValidationRuleSubmission`, `Decide`) |
| `scripts/check-rule-sets-runnable.py`, `backend/tests/test_check_rule_sets_runnable.py` | in | the condition 2 row |
| `scripts/demo.py`, `backend/tests/test_demo_command.py` | in | the demo row |
| `scripts/reset-unbacked-rule-approvals.py`, `backend/tests/test_reset_unbacked_rule_approvals.py` | in | the two DP-6 (b) rows |
| `examples/fremtpl2/seed.py` | in | the seed row |
| `backend/tests/test_approval_guard_static.py` | in | its row (`ALLOWANCE_SITES`) |
| `backend/tests/test_approval_guard_allowance.py` | in | its row |
| `backend/tests/approved_rows.py` | in | its row |
| `backend/tests/test_api_approvals.py` | in | its row |
| `backend/tests/test_api_datasets.py` | in | its row |
| `backend/tests/test_validation_rule_approval.py`, `backend/tests/dry_run_reports.py` | in | the two "added" rows |
| `frontend/src/api/rules.ts`, `frontend/src/components/RuleBuilder.vue`, `frontend/src/views/RuleSetView.vue`, `frontend/src/components/__tests__/RuleBuilder.test.ts`, `frontend/src/views/__tests__/RuleSetView.test.ts` | in | the frontend row ("their tests") |
| `docs/specs/01-data-management.md`, `docs/specs/06-governance.md` | in | the spec-texts row |
| `docs/ledgers/LG-1417-…` | in | the ledger row |
| `docs/INDEX.md`, `docs/contracts/openapi/generated.json` | generated | the `docs/contracts/` row; `docs/INDEX.md` the registry row |
| `backend/tests/test_approval_guard.py` | **named addition** | Delta 7 item 2 (the carry-walker's expected set gains `validation_rules`) |
| `examples/fremtpl2/test_seed.py` | **named addition** | Delta 17 (the seed-twice test) |

Not in the diff, as the plan requires: `backend/src/app/platform/approvals.py` (read only) and `backend/tests/test_contracts.py` (conditional on an untyped-body guard that is not on main).
Every file outside the write set is one of the two named additions or generated: 30 + 2 + 2 = 34. Nothing else is outside it, so there is no STOP.

**5. Named deviations and lead verdicts, by Delta number** (the dispatch record is local and not in the repository; the verdicts are quoted from it by Delta).
- **Delta 6:** Task 1's test edit left uncommitted (plan Task 1 Step 3); Tasks 2 and 3 go to one executor. Check 32 red inside the DP-0 quote, fixed by fencing it as `text`, byte-identical (6 of 6 `sha256sum`). ACCEPTED.
- **Delta 7:** Tasks 2 and 3 done. (1) Task 4 Steps 2–3 pulled forward (`ValidationRuleSubmission`, the thin-client approve route); `generate-contracts --check` red at that head until Task 4: ACCEPTED. (2) `backend/tests/test_approval_guard.py` outside the write set, a named forced expectation change: ACCEPTED. (3) Plan defect: `test_a_fail_dry_run_is_still_approvable` cannot pass on base: recorded. (4) `data_handlers._validate` passes the dataset slug in the refusal text: recorded.
- **Delta 8:** Task 4 done. The body-type test's cause differs from the plan's (Steps 2–3 pulled forward); the decide key-set test is planned and passed first run, its failure proved by a scratch rename, reverted. ACCEPTED.
- **Delta 9:** Task 5 done. `act` reports through `explain`; the per-row label carries the rule slug; the "rejects unparseable parameters" test fills the summary. ACCEPTED.
- **Delta 13:** Task 7 Steps 1–3a done. The lead's brief was wrong about the base tree (the base run used the merge base `bf33eea6`); the request id comes via `open_request_for`; the reset script keeps the `GIP_DATABASE_URL` override; the reset test asserts on its own rows only. ACCEPTED.
- **Delta 15 (the PL-1408 premise correction; a delta, not a plan edit):** PL-1408 Task 7 and RL-1407 say the recovery seed keeps the demo's workspace runnable at every moment after the slice's code exists. That was false on 2026-10-05: the record's workspace was absent from `gipricing`, so there was nothing runnable to keep. Step 4.2 also omitted the demo's own `alembic upgrade head`. Binding for the resume: migrate first (upgrade only, revisions recorded), keep the abandoned partial seed (no deletes), full 678,013 rows with no slot held, and the finding goes to FD 9717 (MEDIUM, its own queue, not blocking this slice).
- **Delta 16:** Step 4 second stop: the second seed failed on `uq_users_issuer_subject`, a defect on main (`ensure_member` looks up by user id only), not this slice's. Put to the maintainer (by delegation).
- **Delta 17:** the seed resolves the analyst id from an existing realm user, else mints one; red first by a seed-twice test; inside the write set (`examples/fremtpl2/seed.py`); `examples/fremtpl2/test_seed.py` a **named write-set addition**; `platform/workspaces.py` not edited, its docstring defect is in FD 9717's scope. APPROVED.
- **Delta 18:** Task 7c done (the seed-twice red quoted verbatim, green `8 passed`). ACCEPTED.
- **Delta 19:** Step 4 resumed: full seed rc 0, the cond. 4 copy of the record, reset `reset=10`, residual `0` to `15`. The demo then died on a stale root venv (`sympy`); D1 `uv sync --all-packages` at the root authorised; D2 merge `origin/main` into the branch; D4 residual 15 recorded, no new FD; D5 the per-database before lines were not kept (a disclosed gap, the aggregate check instead); D6 the 608 breakdown quoted. No objection from the maintainer (by delegation); D7–D9 added.
- **Delta 20:** Step 4 done on merge `c156e7274e8d07bc0e9eb1112590c2a259e2db94` (branch plus `origin/main` `072c56e1`; INDEX regenerated, `__all__` merged cleanly with all four names). Lead found D7–D9 missing from the ledger and sent the entry back.
- **Delta 21:** Task 7 complete. D7 (the root HEAD for the retry), D8 (the full ids), D9 (zero approved or deployed references) present. Per the maintainer's (by delegation) condition, the slice audit names the residual of 15 as ACCEPTED under RL-1407. Next: the slice audit, then the mint, then Task 8 Step 1 at the minted head.
- **Deltas 10, 11, 12, 14 (no deviation from the plan):** Delta 10 (Task 6) the lead's byte-check of the spec texts against RL-1407, ACCEPTED, with INDEX regenerated as the expected follow-on; Delta 11 split Task 7; Delta 12 the maintainer's (by delegation) approval of the record handling, ARFF files symlinked as files; Delta 14 the first Step 4 stop (the missing migration). Listed for completeness.

`python3 scripts/audit-docs.py` after this entry: `FAILED (1): check 31: gap in the full allocation between 1413 and 9719`, the expected one (LG 9719 is a working id). No other check failed.

### Slice-audit fix 1/2 (Delta 23) — findings A, B and C (2026-10-05 12:45 BST, executor-1409-t9)

Base head `f85be6724b26b90a9c0c6e93ec0160bd61cde076`. Both gate slots (`gate-1`, `gate-2`) were free before the first run.

**A — Acceptance 24.** `test_a_rule_reset_by_dp6_does_not_execute_in_its_sets_next_run`, in `backend/tests/test_reset_unbacked_rule_approvals.py`: an approved, non-built-in rule A with no request, in a dataset's rule set; the reset script; then `DATASET_VALIDATE` on an ingested version. It asserts the job is not `SUCCEEDED`, `error["code"] == "RULE_NOT_APPROVED"`, `error["message"]` **equal** to RL-1407's condition-1 text for rule A (`Not approved: <id> (<slug>@1, review). …`, read from the minted RL-1407 at `docs/rulings/`), and that the version's status and its `validation_reports` count are unchanged.
- Red, by a scratch revert of `backend/src/app/worker/data_handlers.py:250` (`rule_service.rule_set_to_run(` to `rule_service.rule_set_for(`), backed up first:
  ```text
  >       assert await execute_job(database, job.id, blob_store) is not JobStatus.SUCCEEDED
  E       AssertionError: assert <JobStatus.SUCCEEDED: 'succeeded'> is not <JobStatus.SUCCEEDED: 'succeeded'>
  E        +  where <JobStatus.SUCCEEDED: 'succeeded'> = JobStatus.SUCCEEDED
  backend/tests/test_reset_unbacked_rule_approvals.py:270: AssertionError
  1 failed, 1 warning in 2.15s
  ```
  The report has a result for A on the reverted tree (a scratch print, itself reverted: `SCRATCH 1 ['01a10bdd-1861-7f91-8e51-325ee4c24873'] 01a10bdd-1861-7f91-8e51-325ee4c24873`: one report, its one result is rule A). The cause is the plan's.
- A first run before this one failed for a different cause, a test-setup defect of mine: `PermissionDeniedError: This action requires dataset:write.` (no `grant("analyst")`). It was fixed in the test, and the red above was taken after the fix.
- Restore: `cmp` of the backup against `data_handlers.py` exit 0; the diff of `backend/src` quiet, exit 0. Green: `backend/tests/test_reset_unbacked_rule_approvals.py` `5 passed, 1 warning in 2.66s`.

**B — Acceptance 4, first clause.** `test_the_approve_route_decides_through_the_workflow` (`backend/tests/test_validation_rule_approval.py`, the module Acceptance 4 names) now also posts `/approve` to a `draft` rule and to the `approved` rule it just approved: each is 409, `code == "RULE_NOT_APPROVED"`, `title == "Only a rule in review can be approved; this one is '<status>'"`, status unchanged.
- Red, by a scratch mutation of the guard in `backend/src/app/api/validation.py:381` (`if row.status != "review":` to `if False:`), backed up first. The status and code asserts still hold on that tree, because `open_request_for` raises the same 409 `RULE_NOT_APPROVED`; the title assert is what separates the two guards:
  ```text
  E           assert 'This rule ha...roval request' == "Only a rule ...ne is 'draft'"
  E             - Only a rule in review can be approved; this one is 'draft'
  E             + This rule has no open approval request
  backend/tests/test_validation_rule_approval.py:471: AssertionError
  1 failed, 1 warning in 3.06s
  ```
- Restore: `cmp` of the backup against `api/validation.py` exit 0; the diff of `backend/src` quiet, exit 0.

**Green after both:** `backend/tests/test_reset_unbacked_rule_approvals.py` and `backend/tests/test_validation_rule_approval.py` together `26 passed, 2 warnings in 33.19s`. `ruff check` on the two files: `All checks passed!`. `mypy`: `Success: no issues found in 226 source files`.

**C — the two ledger gaps.**
- Acceptance 11's custom role is `decider`, holding only `approval:decide` (`RoleRow(workspace_id=workspace_id, slug="decider", permissions=["approval:decide"])`, `backend/tests/test_validation_rule_approval.py:509`, in `test_an_approver_without_a_policy_role_is_refused`).
- DP-2 produced **only an OpenAPI component** (`ValidationRuleSubmission`), no new schema artifact: `git diff --name-only origin/main...HEAD -- docs/contracts/` prints one path, `docs/contracts/openapi/generated.json`.

## Closing note

This ledger is closed under the executor charter's mint-step clause (`.claude/roles/executor.md`, "As the mint step…", added 2026-10-04) and `docs/process/document-ids.md` §1.6's 2026-10-04 amendment to the SL and LG close cells: on 2026-10-05 the executor performed the closing acts in the mint commit on the auditor's behalf, after the slice audit — the front matter `status: closed`, the roadmap SL-1409 row `status: closed` with its dated line, `docs/INDEX.md` regenerated, `audit-docs` green. The audit it cites is `handover/audit-sl1409-2026-10-05.md`, with its "Re-check of fix 1/2" section (local, not in the repository). The working id `LG 9719` was minted as `LG-1417` at `python3 scripts/doc-id.py next` = 1417 on origin/main `99afcde215c0817c5ac4db55332ab7a69e4752a0`. The two lines of this ledger that quote `audit-docs` output naming `LG 9719` (the Task 0 and Task 8 entries) stay as quoted; they record what that run printed. The minted-head gate's record and the PR number are appended after the gate.

### Correction to the Slice-audit fix 1/2 entry's finding C (2026-10-05, mint)

Finding C above says DP-2 produced "only an OpenAPI component". That is imprecise, and this line corrects it without rewriting the entry. DP-2 produced **no new schema artifact**: `git diff --name-only origin/main...HEAD -- docs/contracts/` prints one path, `docs/contracts/openapi/generated.json`. What that file gains, measured with `git diff -U0 origin/main -- docs/contracts/openapi/generated.json` (five hunks): the `ValidationRuleSubmission` component; a `description` on the existing `Decide` component; the `/submit` route's `requestBody` (a `$ref` to `ValidationRuleSubmission`); and the rewritten route descriptions of `approve` and `submit`.

### Minted-head gate red 1 and fix 2/2 (2026-10-05 14:11 BST, executor-1409-gatefix)

The gate at minted head `7b3ee5515b0486c550ec4023095d6eaf04ab8549` (gate-1, 12:32:37Z–13:07:45Z) read `124 failed, 4815 passed, 4 skipped` (log `~/.claude/jobs/6cad77f9/tmp/gatelogs/p.txt`, local). Causes, each found before any change:

1. **121 failures: a stale test database (environment, not code).** The worktree's `gipricing_sl-1409_8f3bb0b4` was at alembic `c4a81f6d2e95`; the head is `e5b7d9f1a3c6` (WK-690 Slice 3's migration, arrived by the `origin/main` merge). Recreated with the S-14 block of `.claude/skills/dev-commands` (`dropdb`, `createdb -T gipricing`, `alembic upgrade head`); `alembic_version` reads `e5b7d9f1a3c6` after. `backend/tests/test_custom_objectives_api.py`, one of the failing files: `24 passed`.
2. **(d) `backend/tests/test_api_authorisation_sweep.py::test_the_handler_guarded_routes_still_check_at_their_site`.** Red, verbatim: `AssertionError: POST /api/v1/validation-rules: platform/validation_rules.py:200 no longer holds 'require_permission(': ') -> ValidationRuleRow:'`. The branch added lines to `create_rule`, so the two `require_permission(` calls moved from 200 and 207 to 212 and 219. Re-pinned `HANDLER_GUARDED`; the file reads `9 passed`. The sweep's line-pin design is intended (its docstring: "An allow-list entry is a claim about a line of code; read the line") and is not redesigned; a finding is not raised.
3. **(c) `tests/test_repository_invariants.py::test_the_error_code_registry_matches_the_specs`.** Red, verbatim: `AssertionError: 01-data-management.md: spec-only ['EVIDENCE_INCOMPLETE'], …`. `01`'s owned-codes line carries `EVIDENCE_INCOMPLETE` annotated `(re-raised from `06`)` (RL-1407 text 2). The test took every backticked code in the block as owned; the spec form has precedent (`02` line 2101, `03` line 934) and `scripts/audit-docs.py` check 10 already skips an annotated code as borrowed. **Side (ii): the test.** It now applies the same carve-out; the code and RL-1407's text are unchanged. Test: `1 passed`.
4. **(b) `tests/test_doc_id_migrate.py::test_reference_stamp_census_is_silent_on_the_real_corpus`.** Red, verbatim: `NotImplementedError: migrate: .claude/ (every top-level entry — is it in a scope?) -- 1 unit(s) an independent census found are neither a produced record, a derived body line, nor a declared exception (RL-985): - .claude/worktrees/: worktrees/`. Cause: an **empty, untracked `.claude/worktrees/` directory** (made 10:46) inside this worktree's own `.claude/`; git does not track an empty directory, so no checkout has it, and `sl-1273-fixes` has none. After `rmdir .claude/worktrees` the test reads `1 passed`; with the directory present it failed (the control, above). Environmental; the migrate tool is untouched. **Gate treatment:** before a gate, run `ls -A .claude/` in the worktree and `rmdir` an empty `.claude/worktrees`; do not compare against `origin/main`, which has no such directory either.

### Merge of origin/main into the branch (2026-10-05 14:5x BST, executor-1409-gatefix)

The re-gate ran at tree `ae78023e5de47c8c49e64283c91682a9f52865f2` (green: pytest `4939 passed, 4 skipped`, frontend 615 passed, every stage exit 0). `origin/main` then moved; it was merged into the branch at `bc92bb7ef318edcf8c721dc68368746da0df5ca4` by the maintainer's conditions (by delegation) of 2026-10-05 ~14:49 BST. **No local gate was run on the merged head; PR CI on it is the integration gate, and its run ids follow in the PR.** The merged head is the commit carrying this entry (the PR names its SHA).

What main brought in since `99afcde2`, from `git log --first-parent --format='%h %s' 99afcde2..origin/main`: `83ea5090` (#987, FD-1281 owner), `68c07975` (#1123, pyjwt 2.15.0), `4857826c` (#1124, urllib3 2.8.0), `c37bf921` (#1139, FD-1282 register row), `bc92bb7e` (#1150, minted-id re-point FD-1415/FD-1414 on the roadmap and FD-1393 in `03`). #1073, #1071 and #1066 were already ancestors of `99afcde2` and are not in that range.

The one conflict was `docs/roadmap.md`, the SL-1409 row: the resolution keeps main's text (FD-1415, FD-1414) and the branch's "Closed 2026-10-05" line; `git diff origin/main -- docs/roadmap.md` shows only the branch's two lines (status and Closed). Post-mint sweep (`LG 9719`, space form): the three hits in this ledger are quotations of `audit-docs` output and stay as quoted; open PRs #1149 (lines naming "LG 9719" / "LG 1417") and #1125 (three lines) carry live hits, for their owners to re-point.

## PRs

Not yet opened (the lead decides when).
