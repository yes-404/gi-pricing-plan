---
id: RS-8253
family: research
kind: audit
title: SL-1553 (WK-675 S11) slice audit — the Regression suite view and the regression-runs list route (FR 8211), red-first order, the FD-1919 re-point disclosure
status: draft
created: 2026-10-25
owner: auditor
tree: 7dcc478778b6c76fd66deaa6a5a9b7e57909492a
phase: P2
work: WK-675
corrected_by: []
relates: [SL-1553, LG-8212, PL-1546, RL-1900, RL-8217, FR-260, FR-261, FR-1221, FR-1531, FR-25]
---

# RS-8253 — SL-1553 slice audit (WK-675 S11, the Regression suite view)

*(Working id 8253, written by `aud-1553b` (auditor, sonnet), 2026-10-25, from `brief-aud-1553b-2026-10-25.md` (lead 28). Docs and diff reading only: no test, DB, docker or gate was run. Check 31/32 on this id and on the slice's own working ids (FR 8211, RL 8217, LG 8212) are expected until the mint. The auditor proposes; the lead adopts.)*

## Question

Does `merge-base(origin/main, 57bf2fbb)...57bf2fbb` meet the scope of `PL-1546` row 7, the GO "2026-10-25 22:33:28 GMT" conditions (1)–(6), RL-1900 DP-S11-1/2 (a) and RL 8217 points 1–3 (to-lead "2026-10-25 11:22:13 GMT" item (B)), and is the evidence for each item reachable and honest — including the accepted disclosure of the `sed` re-point (to-lead "2026-10-25 22:57:25 GMT")?

## Method

Object: branch `sl-1553-wk675-s11` at `57bf2fbba9dc70084dcbfa889b02ea29c6e56493`, tree `7dcc478778b6c76fd66deaa6a5a9b7e57909492a`. Own worktree `aud-1553b` at that sha. Range base `8c3d3013c3205fbecd6335e9db182a469426bdb2` (`git merge-base 57bf2fbb origin/main`): 17 files, +1272/−9 (`git diff <base> 57bf2fbb --stat`).

Scope was taken from the GO conditions, the `PL-1546` row 7 text, RL-1900 and RL 8217 (`origin/draft/rl-8217`, "What it obliges") first, then evidenced from: `git merge-base --is-ancestor` on every red/code pair and every ledger sha against the head; `git diff -U0 c124e6d9 d3b35fae` and `d3b35fae aab3e3ef` for the re-point; a `diff` of LG 8212's RL 8217 block against the RL file at `origin/draft/rl-8217`; a read of the backend, model-schema, frontend and spec hunks. The tests were not re-run: the red/green lines are LG 8212's, checked for sha, rc and reachability only.

## Scope and GO conditions

| # | Condition | Verdict | Evidence |
|---|---|---|---|
| (1) | docs-only re-merge of `e64c4568` onto `8c3d3013` under K1/K2/K3, INDEX regenerated, FR 8211 still a working id | met | `c124e6d9` is the re-merge; `FR-8211` is a working id in INDEX and the spec at head |
| (2) | build per row 7 + RL-1900 DP-S11-1/2 (a) + RL 8217 points 1–3; red-first; `<script setup lang="ts">` only; generated API types only | met | see below |
| (3) | slice's own frontend tests + eslint/vitest/type-check lines in LG 8212 before the auditor | met | LG 8212 Build log: vitest "Test Files 3 passed (3)", "Tests 30 passed (30)", rc 0; eslint rc 0; `pnpm type-check` rc 0 |
| (4) | full gate in a free slot | owed (the lead's; gate-1b running) | not an audit item |
| (5) | ids minted at the merge turn | not yet due | FR 8211, RL 8217, LG 8212 still working ids |
| (6) | one building seat | not auditable from the repository | n/a |

**Row 7 / RL-1900:** `RegressionRunSummary` has exactly the 8 fields DP-S11-1 (a) lists (`packages/model-schema/src/model_schema/regression.py`); the list is `finished_at desc, id desc`; the view opens the newest run, honours `?run=`, marks `evidence.regression_suite_run_id` (the label's "approval evidence" suffix); DP-S11-2: `api/regressionRuns.ts` has only `GET`s, and a view test asserts no `POST`, no `/cases`, no `/blobs`.
**RL 8217 point 1:** `/tests` link in `RatingVersionListView.vue` built from `version.slug`/`version.version`, no second lookup; `router/index.ts` entry `rating-tests`; the dated clause "Amended 2026-10-25, WK-675 S11 `SL-1553`, FR 8211: and to `/rating/:slug/v/:version/tests`." is in the same commit `1eed6642` as the router entry; `reachability.test.ts` was run green and is not in the diff. **Point 2:** the handler signature is the ruled one (`cursor: str | None = None, limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT`), `Page[RegressionRunSummary]`, `total_estimate` counted up to `COUNT_CAP`, `pagination.py` not in the diff; the client uses `pageThrough` with the generated types. **Point 3:** `list_runs` loads the cursor run under the same workspace + version filters, resumes by `tuple_(finished_at, id) <` row-value comparison, answers 400 `VALIDATION_FAILED` for a foreign or unknown id; the §4.9 sentence and the §5.1 400 clause are in the spec diff.
**Frontend rules:** `RegressionSuiteView.vue` is `<script setup lang="ts">`; its types come from `@/api/generated/schema` via `regressionRuns.ts`; the test fixtures are typed from `components["schemas"]` (no hand-written shape).

## Red-first and ledger reachability

`git merge-base --is-ancestor <red> <code>`: `c07ad757`→`13c1a0bd` rc 0; `892a2f74`→`bb564bdb` rc 0; `da819fde`→`1eed6642` rc 0. Every other sha the ledger cites (`238b85ca`, `b9b8ee7c`, `963f97a7`, `3780fbdd`, `93bd427b`, `aab3e3ef`) is an ancestor of `57bf2fbb` (rc 0 each). Red/green lines carry sha + rc: model-schema "1 failed, 26 passed" rc 1 → "27 passed" rc 0; backend "4 failed, 1 passed, 13 deselected" rc 1 at `892a2f74` → "10 passed, 8 deselected" rc 0 at `b9b8ee7c`; frontend red "Test Files 2 failed (2)", rc 1 → green rc 0. Disclosed limits (not findings): the frontend red/green logs name `…-plus-uncommitted` trees; the backend red is the DB-window run, not the `run-small` 18-error run.

## Findings

Classes: B = blocking, N = non-blocking. Not yet filed as `FD-`; the lead decides (a process or docs-only forward fix in the slice needs none).

**F1 (B) — a fourth in-quote re-point: the "RL 8217 What it obliges, verbatim" block in LG 8212 reads "FR-1903 item (4)", the source reads "FR 8209 item (4)".** Evidence: `git diff -U0 c124e6d9 d3b35fae` rewrites the line `- **Point 1 (the /tests link).** (i) FR 8209 item (4) gets a dated clause: *"Amended` to `FR-1903`; `aab3e3ef` (`git diff d3b35fae aab3e3ef`) restores only the three `to-lead` spans (the "2026-10-23 11:14:56 BST" heading and, twice, item (B) of the 11:22:13 GMT entry); line 44 of LG 8212 at `57bf2fbb` still reads `FR-1903`, while `origin/draft/rl-8217` line 178 and LG 8212 at `e64c4568` read `FR 8209`. A `diff` of the block against the RL file shows that one line as the only difference. The block is introduced as "verbatim (`origin/draft/rl-8217` @2f205360)". The `93bd427b` disclosure and the maintainer's acceptance (to-lead "2026-10-25 22:57:25 GMT") speak of three `to-lead` spans; this is a fourth span of the same class (FD-1919: a quoted passage altered by a re-point), in a file quote, so the disclosure undercounts. All other changed lines of `d3b35fae` (11 in LG 8212, 4 in `03-rating-engine.md`, 1 in INDEX) are prose, front matter or spec text, not quotes: checked line by line. Fix (docs-only, forward, no rewrite): restore `FR 8209` on that line and add the span to the disclosure line in the FD-1919 form, then the decider `audit-docs` at that head. Blocking because the record is wrong about its own accepted disclosure; the repair is one line.

**F2 (N) — the route declares `problems(401, 403, 404, 422)` but returns 400.** Evidence: `backend/src/app/api/models.py` `list_regression_runs` (`responses=problems(401, 403, 404, 422)`) beside the docstring and `03` §5.1 ("**400** `VALIDATION_FAILED`"); `decode_cursor` and `list_runs` both raise 400; other cursor-list routes declare it (`datasets.py:302` `problems(400, 401, 403, 422)`). The generated OpenAPI therefore omits a status the spec lists. Fix: add `400`, regenerate `docs/contracts`, `generate-contracts.py --check`. Not blocking: the body shape is the platform's RFC 9457 either way; the lead may fold it into the gate repair.

**F3 (N) — the seat's observation that no index matches the list order (`finished_at`, `id`): classified N.** Evidence: `RegressionRunRow.__table_args__` (`backend/src/app/db/models.py:2586`) holds `ix_regression_runs_latest (rating_version_id, bundle_hash, suite_content_hash, finished_at)` and the cases-blob index; the list filters `workspace_id` and `rating_version_id` and orders by `finished_at desc, id desc`. The query uses the `rating_version_id` prefix and sorts the version's rows in memory. A version's runs are few (one per submit gate or manual run) and the response is capped by `limit ≤ MAX_LIMIT`; no NFR budget names this route and none was measured here, so no perf claim is made. Not a defect against the build; a covering index `(rating_version_id, finished_at desc, id desc)` is a later migration only if a measurement asks for it. Owed: none for this slice.

**F4 (N) — plan task 3's list is not fully pinned by tests.** Evidence: `backend/tests/test_regression_runs.py` (lines 558–640) covers the version filter, order, summary key set, 404s, the equal-`finished_at` tie-break with `limit=1` paging, the 400 for another version's, another workspace's, an unknown and a malformed cursor, and no shadowing of the `{run_id}` read. It has no test that `total_estimate` stops at `COUNT_CAP`, and `test_api_authorisation_sweep.py` is not touched (the file does not mention the route). Not a requirement of FR 8211 as written (RL 8217 (iv) lists only the tie-break, paging and foreign cursor): residue for the gate to show whether the sweep enumerates routes.

**F5 (N) — `1eed6642` edits the red frontend test file after its red commit.** Evidence: `git show 1eed6642 -- RegressionSuiteView.test.ts`: two fixtures gain `counterexample_minimal: false`, and the problem test replaces `findByRole("alert")` by `waitFor(getByRole("alert"))`. No assertion is weakened or removed; LG 8212 discloses both changes as the test's own defects. Recorded, no action.

## Checks asked for by the brief

(a) The sed slip: `d3b35fae` changed only the ids; `aab3e3ef` and `93bd427b` are as disclosed for the three `to-lead` spans, **but see F1** for the fourth. (b) The 8 deselected `run_world` tests of `test_regression_runs.py` are owed to gate-1b; they pass the build only if the gate shows them green; not a finding. (c) Index observation: F3 (N).

## Proposed verdict

**NOT-CLEAN** on F1 only (B). With F1 repaired by the forward fix above and the decider `audit-docs` clean except the slice's own working-id checks 31/32, the proposed verdict becomes CLEAN; F2–F5 are N.

## Owed

1. F1 repair (docs-only) + `audit-docs` decider at the new head. 2. Gate-1b result for the 8 deselected tests, `mypy`, `lint-imports`, `ruff check .`, `req-coverage.py`, the full frontend half. 3. Plan task 7 (accessibility review of the view, NFR-463) and task 8 (the import-closure GREEN set, item 29) are not yet in LG 8212: owed before the PR. 4. The mint (item 34): RS 8253 into the slice PR with FR 8211, RL 8217 (with its adoption line) and LG 8212.

## Addendum — delta audit at 08ae3a72 (2026-10-26)

Range: `57bf2fbb..08ae3a72` on `sl-1553-wk675-s11` (ls-remote = `08ae3a724f89cdd6fd396603f5a99cde75e57fa8`). Authority: `to-lead.md` "2026-10-25 23:40:16 GMT" (F2 ruled (a), named exception), "2026-10-26 01:06:59 GMT" (exception extended to `regression_runs.py`), "2026-10-26 01:14:30 GMT" ("**Exception MET: the 57bf2fbb gate stands for 08ae3a72.**"). Read-only diff reading; no test, gate or audit-docs was run (audit-docs is owed at the mint).

**Scope.** `git diff --stat 57bf2fbb 08ae3a72` = `backend/src/app/api/models.py` 2, `backend/src/app/platform/regression_runs.py` 7, `backend/tests/test_contracts.py` 27, `docs/contracts/openapi/generated.json` 15, LG 8212 4 — 5 files, +51/−4: exactly the exception's scope; no other path. Commits: `d7617c94` F1, `f2655400` F2 guard, `cd24f985` route 400, `eb269d53` mypy, `08ae3a72` contracts.

**F1 — CLOSED.** LG 8212 lines 42–64 at 08ae3a72 (the 23-line "What it obliges" verbatim block) against `origin/draft/rl-8217` @2f205360 lines 176–198: `diff` prints nothing (rc 0); line 44 reads "(i) FR 8209 item (4) gets a dated clause". The LG diff `57bf2fbb 08ae3a72` is two hunks only: `@@ -44 +44` (that one span, `FR-1903` → `FR 8209`) and `@@ -112,0 +113,2` (the appended "Disclosure addendum (2026-10-25 23:40 GMT …)" paragraph, count corrected three → four); no earlier line is otherwise edited.

**F2 — CLOSED.** Route at 08ae3a72: `@router.get("/rating-versions/{rating_version_id}/regression-runs", … responses=problems(400, 401, 403, 404, 422),)`. Spec row `03` §5.1 line 1115 lists 200, 401, 403, 400, 404. Guard `test_the_regression_runs_list_route_declares_every_status_03_lists` reads that row from the spec (not hard-coded), strips parentheticals, and asserts `listed <= declared` ("03 §5.1 lists {…} the route does not declare"), plus a sanity assert `{"200","400","404"} <= listed` so an unread row cannot pass vacuously. `generated.json` hunk `@@ -37119` adds the `"400"` response (`ProblemDetail`, both media types, "Malformed request") under that route's `get`. Red/green as quoted by the lead (not re-run): RED at `f2655400` "1 failed, 176 passed, 2 skipped" ("03 §5.1 lists ['400'] the route does not declare") → GREEN at 08ae3a72 "177 passed, 2 skipped"; `generate-contracts --check` rc 0 ("58 generated contracts match the models"). This meets the 23:40:16 ruling (red at the pre-fix tree, green after; declared problems include every status `03` §5.1 lists; contracts regenerated).

**mypy — CLOSED.** `regression_runs.py` at 08ae3a72: `tuple_(RegressionRunRow.finished_at, RegressionRunRow.id) < tuple_(literal(anchor.finished_at, DateTime(timezone=True)), literal(anchor.id, Uuid()))`; imports `DateTime, Uuid, literal` added. Same comparison, same operands, same operator and direction; only the right-hand values gain a typed bind-parameter wrapper — no behaviour change by reading. Evidence (lead's entry, not re-run): project mypy rc 0 "Success: no issues found in 250 source files" at `eb269d53`; `test_regression_runs.py` "18 passed" at 08ae3a72.

**Earlier findings.** F3 (no index on `finished_at, id`) — still holds as N, unchanged by this delta (no migration in range). F4 (no `COUNT_CAP` / authorisation-sweep test) — still holds as N; the delta adds no such test. F5 (`1eed6642` edits) — N, recorded, no action. Owed items 2–4 of the original list (task 7 accessibility review, task 8 GREEN set in LG 8212, mint of RS/FR/RL/LG) carry to the mint unchanged; item 2's gate parts are covered by the 01:14:30 "gate stands" ruling. Not mine: the lead's owed one-line gip-test-blobs teardown check (01:14:30).

**Proposed verdict: CLEAN** for the delta `57bf2fbb..08ae3a72` — F1, F2 and the mypy defect closed, scope exactly the exception's; the original NOT-CLEAN (F1 only) is discharged. The lead adopts.
