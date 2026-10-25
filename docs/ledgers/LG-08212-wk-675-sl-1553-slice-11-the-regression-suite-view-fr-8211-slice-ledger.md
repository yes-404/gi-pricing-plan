---
id: LG-8212
family: ledger
title: WK-675 slice SL-1553 — Slice 11, the Regression suite view at /rating/:slug/v/:version/tests (FR 8211) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-25
owner: executor
tree: 951af0719d155ac58afce69c46e485dbb7a7a49c
phase: P2
work: WK-675
slice: SL-1553
plans: [PL-1546]
corrected_by: []
relates: [SL-1553, PL-1546, PL-1286, RL-1900, RL-8217, FR-8211, FR-260, FR-261, FR-1221, FR-1531, FR-25, FD-1283]
---

# LG-8212 — WK-675 slice SL-1553, Slice 11: the Regression suite view at /rating/:slug/v/:version/tests

Status: **active** — activated 2026-10-25 in the commit that sets the roadmap SL-1553 row `draft` to `active`. Nothing below Tasks has been run before this commit.

**GO:** to-lead "2026-10-25 22:33:28 GMT — Maintainer: GO — SL-1553 (WK-675 S11, LG 8212, PL-1546 row 7) on `sl-1553-wk675-s11` @e64c4568" — conditions (1)–(6) as in that entry. DP-S11-3 (to-lead "2026-10-23 11:14:56 BST", item (C)) met: SL-1552's squash `85eac5b2` is an ancestor of origin/main. Follow-on `rating.py` row: "none at 01a28e6d" (to-lead "2026-10-25 15:38:26 GMT").
**MERGE-ACK:** not yet.

## Tasks

### Scope

**Plan row.** `PL-1546` row 7 (`docs/plans/PL-01546-wk-675-slices-5-to-11-work-plan-delta.md`, the "Slices" table): "| 7 | SL-1553 — S11: Regression suite view | `PL-1286` S11 row | `03` §3.8: FR-260, FR-261, FR-1221; `FD-1283` option A; a run-list read route under DP-4 (a) only if the version's evidence gives no run id | S10 (order); DP-5 (met) | at GO | 1 | **candidate, rung 2** (with S10) |". Roadmap row: `SL-1553` in `docs/roadmap.md`, "Slice 11: Regression suite view (FR-260, FR-261, FR-1221; FD-1283 option A)", cut-ladder rung 2.

**Requirements.** `03` FR 8211 (new, working id; its spec text is already on this branch: §3.8 row, §4.9 `RegressionRunSummary` paragraph with the RL 8217 point 3 sentence, the §5.1 `GET …/regression-runs` row with the 400, the §5.3 row note). View limbs: FR-260, FR-261, FR-1221. Also FR-1531 (404 posture), FR-25 (reachability by links), FR-1903 item (4) (the dated clause, below).

**Why a list (FR 8211 item (1)).** The submit gate alone writes `evidence.regression_suite_run_id`; a failing run's id appears only in the prose of the 409; the persisted `RegressionRun` has no `id`. A draft version, and any failing run, has no machine-readable run id.

**Decisions that bind the slice.**
- RL-1900 (working id; adopted to-lead "2026-10-23 11:14:56 BST", item (A)): DP-S11-1 (a) a new `RegressionRunSummary` (`id`, `job_id`, `overall`, `bundle_hash`, `suite_ref`, `suite_content_hash`, `started_at`, `finished_at`), listed newest first by `finished_at desc, id desc`, cursor-paginated; the view opens the newest run by default, accepts `?run=<id>`, marks the run `evidence.regression_suite_run_id` names. DP-S11-2 (a) read-only: the view makes no `POST …/regression-runs` request and offers no control that does.
- RL 8217 (working id; adopted whole, to-lead "2026-10-25 11:22:13 GMT — Maintainer: SL-1569 window re-run GO in the slot gap; RL 8217 ADOPTED whole; exec-clean read-back verified and the three cleanup rulings", item (B)): "Point 1 (a): S11 adds the `/tests` link and amends FR 8209 item (4) by a dated clause naming FR 8211, in the same commit as its router entry. Point 2 (a): `limit` + `cursor` with `DEFAULT_LIMIT`/`MAX_LIMIT` by symbol, `Page[RegressionRunSummary]`; no spec edit. Point 3 (a): tie-break = the run's UUIDv7 primary key; order `finished_at desc, id desc` as RL 8163 adopted; `next_cursor` = the last row's id; the handler resolves it with one indexed lookup under the same workspace + version filters and resumes by row-value comparison; a foreign id answers 400 `VALIDATION_FAILED`; `pagination.py` unchanged."
- DP-S11-3 (item (C) above): S11 activates only after S10's squash. Pairing: none.

**RL 8217 "What it obliges", verbatim** (`origin/draft/rl-8217` @2f205360, the section "What it obliges"):


In S11 (SL-1553), spec first, once this record is adopted:

- **Point 1 (the `/tests` link).** (i) FR-1903 item (4) gets a dated clause: *"Amended
<date>, WK-675 S11 `SL-1553`, FR 8211: and to `/rating/:slug/v/:version/tests`."* The row text
is not rewritten. (ii) The S10 list view gains the link, built from `slug@version` with no
second lookup. (iii) `router/index.ts` registers `/tests`, and `reachability.test.ts` stays
green with **no** entry added to its unreachable-routes list. (iv) S11's view-test set adds the
list view's own test file, because it changes that file (import closure, common item 29).
- **Point 2 (parameter names).** The handler signature is
`cursor: str | None = None, limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT`.
The response is `Page[RegressionRunSummary]`, with `total_estimate` counted up to `COUNT_CAP`.
The client reads through the generated API types: it uses `pageThrough` or a single page with
"load more", never a hand-written page shape (CLAUDE.md §2). No spec edit is needed.
- **Point 3 (tie-break and cursor).** (i) The §4.9 paragraph (`03:921-927`) gets one dated sentence:
*"`id` is the run's UUID (the `regression_runs` primary key, UUIDv7); it is the order's
tie-break and the cursor's key."* (ii) The §5.1 row (`03:1113`) gains *"; 400
`VALIDATION_FAILED` for a cursor that is not a run of this version"*. (iii) The handler
follows (a): one UUID cursor, a `(finished_at, id)` row-value comparison, and the cursor run
loaded under the same workspace and version filters, so a foreign run id cannot be used to
probe another version (FR-1531 posture). (iv) S11's backend test, carrying
`@pytest.mark.req` on FR 8211, pins: two runs with equal `finished_at` order by `id`
descending; paging with `limit=1` across them returns each exactly once; a cursor naming
another version's run answers 400. The test is red at its test commit.

**Rendering rules decided elsewhere** (RL-1900 "What it obliges"; not re-ruled): money from minor-unit integers (FR-10, FR-21); `counterexample_minimal: false` shown as unminimised (`03:908` at main); no empty counterexample for `MONOTONE_NO_COMPARABLE_PAIRS`; `not_checked` golden evidence shown as "no golden quotes were checked" (FR-260); the cases blob is read only via `…/cases` (FR-1221), never `/blobs`.

**Write set (expected).** `packages/model-schema` (`RegressionRunSummary` + test; `docs/contracts/` regenerated); `backend/src/app/platform/regression_runs.py` (list query), `backend/src/app/api/models.py` (the `GET` beside line 1325's `POST`, not shadowing the `{run_id}` read), a backend test; `frontend/src/api/regressionRuns.ts`, `views/RegressionSuiteView.vue` and its components, tests, `router/index.ts`; the S10 list view (`RatingVersionListView.vue`) for the `/tests` link and its test file; `docs/specs/03-rating-engine.md` (FR-1903 item (4) dated clause); this ledger, the roadmap row, `docs/INDEX.md`.

**Mints in this PR (item 34, in merge order after RL-1900, which mints in S10's PR):** FR 8211, RL 8217 (with its adoption line citing the 11:22:13 GMT heading), LG 8212, and every cite of each, re-pointed with a whole-tree grep in both space and hyphen forms (item 26).

### Task list

Nothing below is run at drafting. "Red" is proven at the slice's GO under a DB window; the red tests are written before the code they pin.

0. **Activation** (after S10's squash; one commit): re-merge `origin/main`; the GO header; the roadmap `SL-1553` row `draft` to `active`; INDEX regenerated. Acceptance: `audit-docs.py` and `doc-index.py --check` rc 0 (items 31/32 only on this branch's own working ids).
1. **Spec check** (the spec text is already here): `git grep -n 'regression-runs' -- docs/specs/03-rating-engine.md` shows the §5.1 list row (with the 400) beside the `POST` and the `{run_id}` read; §4.9 carries the `RegressionRunSummary` paragraph and the RL 8217 point 3 sentence; `req-coverage.py` run.
2. **Red, model-schema:** a test in `packages/model-schema/tests/test_regression.py` asserts `RegressionRunSummary`'s field set is exactly `id`, `job_id`, `overall`, `bundle_hash`, `suite_ref`, `suite_content_hash`, `started_at`, `finished_at` (no `golden_results`, `property_results`, `generation`, `cases_blob`) and that `RegressionRun` gains no `id`. Acceptance: red at its test commit.
3. **Red, backend** (`backend/tests/test_regression_runs.py`, `@pytest.mark.req` on FR 8211; DB-backed, so written now and run only in a granted DB window): the list for version A excludes version B's runs; another workspace's version, and an unknown id, answer 404 `NOT_FOUND`; a failing run appears with its `id`; order is newest first; two runs with equal `finished_at` order by `id` descending (RL 8217 point 3 (iv)); `limit=1` paging across them returns each exactly once; a cursor naming another version's run answers 400 `VALIDATION_FAILED`; a cursor naming another workspace's run answers 400; `GET …/regression-runs/{run_id}` still resolves (no shadowing); the summary body carries no golden or property result; `total_estimate` is capped at `COUNT_CAP`. Also the authorisation sweep (`test_api_authorisation_sweep.py`) if it enumerates routes. Acceptance: red at its test commit, green at head.
4. **Build, backend:** `RegressionRunSummary` in `model-schema`; the list query in `platform/regression_runs.py` following `list_environments` (`platform/environments.py:174`); the route, handler signature `cursor: str | None = None, limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT`, response `Page[RegressionRunSummary]`; the cursor run loaded under the same workspace and version filters; `pagination.py` unchanged. Acceptance: `generate-contracts.py --check` rc 0; `pnpm --dir frontend generate:api` clean; `ruff`, `mypy`, `lint-imports` rc 0.
5. **Red, frontend** (tests written, not run): `frontend/src/views/__tests__/RegressionSuiteView.test.ts` — golden rows show pass/fail and expected, actual and difference as money from minor-unit integers; a property failure with `counterexample_minimal: false` reads as unminimised; `MONOTONE_NO_COMPARABLE_PAIRS` shows no counterexample; `not_checked` golden evidence reads "no golden quotes were checked"; the default run is the newest; `?run=<id>` selects a run; the run the version's evidence names is marked even when it is not the newest; the cases blob is read only via `…/cases`; the view makes no `POST …/regression-runs` request and renders no control that does (DP-S11-2); an empty run list reads as such; runs beyond one page load through the generated client's page type. The list view's own test file gains a case: the row carries a `/rating/:slug/v/:version/tests` link built from `slug@version` with no second lookup (RL 8217 point 1 (ii)). `reachability.test.ts` stays green with no entry added to its unreachable-routes list (point 1 (iii)).
6. **Build, frontend:** `api/regressionRuns.ts` (generated types only, `pageThrough` or "load more"), `RegressionSuiteView.vue` and its golden and property components, the `router/index.ts` `/tests` entry, the list view's link. **In the same commit as the router entry:** the FR-1903 item (4) dated clause (RL 8217 point 1 (i)), appended after "…for each rate table the version pins.", the row text not rewritten: *(Amended <date of that commit>, WK-675 S11 `SL-1553`, FR 8211: and to `/rating/:slug/v/:version/tests`.)* (FR-1903 is on S10's branch; the clause lands here once S10's squash is merged in.)
7. **Accessibility:** `accessibility-tester` on the view (tables, any chart with its table, NFR-463); report appended below.
8. **GREEN by import closure** (item 29), both halves: changed modules = `git diff --name-only origin/main...HEAD -- <src>`; closure = those + importers + one more level; GREEN = every test file importing any of them. The commands and the lists are quoted here when run. Frontend runs use the item 28 guard, at most 3 files.
9. **Gate and mint:** the full two-half gate on a grant for that head (S-13); the id sweep (`bash ~/gi-pricing-plan.local/scratch/idsweep.sh origin/<branch>`, item 26); the mint as its own commit after the main merge (item 19) with INDEX regenerated and `--check` rc 0 (item 17); RL 8217 and RL-1900 minted per item 34.

### Gate

Not run (draft).

### Audit

Not yet.

### Build log

- 2026-10-25 (exec-1553pr): drafted at `e572e0ae67130dc6df54fd6312f5d00c89750517` (the re-merge of `origin/main` @3cd5fcf7 into `03b087c0`; only `docs/INDEX.md` conflicted, regenerated). Spec text already on the branch from 2026-10-23 and 2026-10-25 (`03b087c0`). Nothing run; no code.

- 2026-10-25 (exec-1553build, GMT; every run below names the tree it ran on; logs under `/tmp/exec1553/`):
  - Re-merge `c124e6d9` (origin/main `8c3d3013`; only `docs/INDEX.md` conflicted, theirs taken and regenerated, `03-rating-engine.md` auto-merged); re-point `d3b35fae`, quote-span fix `aab3e3ef`, disclosure `93bd427b`, activation `3780fbdd`.
  - **Task 2, red then green, model-schema** (`run-small.sh` on `packages/model-schema/tests/test_regression.py`): red on `3780fbdd` plus the uncommitted test, "1 failed, 26 passed", rc 1 (ImportError `RegressionRunSummary`), committed as `c07ad757`; green at `13c1a0bd`, "27 passed", rc 0.
  - **Tasks 3–4, backend**: tests committed `892a2f74`, handler and service at `bb564bdb`. `run-small.sh backend/tests/test_regression_runs.py` on the test commit gave "18 errors" (the DB fixtures; no genuine red), so the backend red and green lines were run later in the DB window granted by to-lead "2026-10-25 23:04:28 GMT" (B), recorded in the next bullet. `generate-contracts.py --check` rc 0 at `bb564bdb`; `ruff check` on the changed files rc 0; `py_compile` rc 0.
  - **Tasks 5–6, frontend** (all under `run-heavy.sh --grant "2026-10-25 22:33:28 GMT"`): `pnpm install --frozen-lockfile` rc 0 and `pnpm generate:api` rc 0 at `bb564bdb`. Red (`/tmp/exec1553/red-fe.log`, first line `head=bb564bdb2846d9c21a368066dce73e9a46c6435c-plus-uncommitted-red`: the run was made before the test commit, so the log's first line is not a bare sha): `vitest run` on `RegressionSuiteView.test.ts` and `RatingVersionListView.test.ts`, "Test Files  2 failed (2)", "Tests  1 failed | 15 passed (16)", rc 1; committed as `da819fde`. Green (`green-fe3.log`, tree `da819fde` plus the uncommitted build, same limitation): `vitest run` on those two files and `src/router/__tests__/reachability.test.ts`, "Test Files  3 passed (3)", "Tests  30 passed (30)", "Type Errors  no errors", rc 0; `eslint` on the six changed frontend files rc 0 (`eslint2.log`); `pnpm type-check` rc 0 (`typecheck2.log`; the first run, `typecheck.log`, rc 2 on two fixture types, fixed). Committed as `1eed6642` with the FR-1903 item (4) dated clause in the same commit as the router entry. Between the red and the first green run `RegressionSuiteView.test.ts` changed twice (a `waitFor` on the alert, two fixture fields): the test's own defects, not a weakened assertion.
  - **Backend red and green, DB window** (grant to-lead "2026-10-25 23:04:28 GMT" (B), via `run-heavy.sh`; container `sl1553-pg-b9b8ee7c`, local `postgres:16-alpine` on `127.0.0.1:32775`, anonymous volume, `alembic upgrade head` to `9b3e7c15d4a2` rc 0, `GIP_TEST_DATABASE_URL` at it only, `GIP_REDIS_URL` db 14 with `dbsize` 0 before and after; load1 3.93 at start; `/tmp/exec1553/{red,green}-be.log`). Selected with `-k` to the file's list tests and its three DB-only persist/lookup tests; the 8 other tests of the file build a `run_world` that writes blobs to the shared MinIO, so they were **not run** (deselected, not skipped). Red at `892a2f74` (the test commit; log first line `head=892a2f746df7668bd8d36eada6c6d6d6787e5ba6 container=sl1553-pg-b9b8ee7c`): "4 failed, 1 passed, 13 deselected" (the four list tests answer 405; the shadow test passes, as it guards what already works), rc 1. Green at `b9b8ee7c` (log first line `head=b9b8ee7c29d3e22b56cad835c7bdc1333cbbe512 …`): "10 passed, 8 deselected", rc 0. Cleanup: `docker rm -fv sl1553-pg-b9b8ee7c`; `docker ps -a --filter name=sl1553-pg` empty after, none before; dangling volumes 16 before and 16 after; no prune.
  - **Decider audit-docs** (`run-heavy.sh --light`, `head=238b85cacbcca7cb3576e379c18cdb2db569deb8`): rc 1, FAILED (4): check 31 gap between 1904 and 8211; check 32 `RL-8217` (line 14, own working id, record on `origin/draft/rl-8217`); check 32 `FD-1919` ×2 (line 110, from `93bd427b`; fixed forward in `b9b8ee7c` by writing `FD 1919`). At `b9b8ee7c`: rc 1, FAILED (2): check 31 and check 32 `RL-8217`, both own working ids.
  - Owed: the import-closure GREEN set (item 29, task 8); the accessibility review (task 7); the full gate (task 9), the lead's.

## PRs

Not yet opened.

**Disclosure (2026-10-25, FD 1919 form; the maintainer's 22:55:13 GMT ruling relayed by the lead).** A `sed` over this ledger and `docs/specs/03-rating-engine.md`, re-pointing FR 8209, RL 8163 and LG 8208 to FR-1903, RL-1900 and LG-1902, ran in commit `d3b35fae` (pushed). It rewrote three spans inside verbatim `to-lead.md` quotes in this ledger: the "2026-10-23 11:14:56 BST" heading (RL 8163, `to-lead.md` :30182) and, twice, item (B) of the "2026-10-25 11:22:13 GMT" entry (FR 8209 and RL 8163, `to-lead.md` :30429). The forward fix `aab3e3ef` restored the three spans character for character from `to-lead.md`; no history was rewritten. `e64c4568` and the re-merge `c124e6d9` are unaffected, and no frozen record was touched. This is the quote-alteration class of FD 1919; the line is its accepted disclosure form.
