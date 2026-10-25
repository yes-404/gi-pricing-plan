---
id: LG-8208
family: ledger
title: WK-675 slice SL-1552 — Slice 10, the Rating version list at /rating (FR 8209) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-23
owner: executor
tree: 4e399fd01e8de2fe55d2f128b0e09ee2b2735c6a
phase: P2
work: WK-675
slice: SL-1552
plans: [PL-1546]
corrected_by: []
relates: [SL-1552, PL-1546, PL-1286, RL-8163, FR-1531, FR-241, FD-1283]
---

# LG-8208 — WK-675 slice SL-1552, Slice 10: the Rating version list at /rating

**GO:** "2026-10-23 11:14:56 BST — Maintainer: SL-1552 (WK-675 S10) GO under L1; RL 8163 ADOPTED; DP-S10-4 and DP-S11-3 decided" (`to-lead.md`), item (D): GO under Lean P2 L1; `router/index.ts` and `App.vue` stay HELD until SL-1551's squash is on `origin/main`, then re-merge and re-run the frontend half.
**MERGE-ACK:** not yet.

## Tasks

### Scope

Plan: `PL-1546` row 6 (Work plan for WK-675 Slices 5 to 11); roadmap row `SL-1552` (`docs/roadmap.md`, "Slice 10: Rating version list (FD-1283 option A; a new `03` §3.4 FR, spec first)"), quoted from prep §1.1 (`scratch/sl-1552/prep-2026-10-23.md`, read at `4e399fd0`): "The `/rating` list: versions by status, live badges, effective dates, rows linking to `:slug/v/:version`; spec first, amending the existing `GET /api/v1/rating-versions` §5.1 row per `RL-1483`." PL-1546 R10.1: one new `03` §3.4 FR, amend the existing §5.1 row and add none.

Requirement covered: `03` FR 8209 (new, working id reserved by the lead, `eta.md` 11:17 BST), with `FR-241`, `FR-1531`, `FR-25`. Open question raised: OQ 8206 (server-side pagination and filtering of `GET /api/v1/rating-versions`), mirrored in `03` §10 and `open-questions.md`.

Decisions that bind the slice (RL 8163 (working id), adopted to-lead 2026-10-23 11:14:56 BST, item (A); folded into this PR with its adoption line):
- DP-S10-1: `RatingVersionView` stays; `/rating` is the FR-25 entry.
- DP-S10-2: live badges are a client-side join over every page of `GET /api/v1/environments`, keyed `rating_version:{slug}@{version}`; any 403, failed page or truncated read gives "unavailable" on every row, never "not live".
- DP-S10-3: option (a), the route stays unpaginated; filter and group in the view; OQ 8206 owns the bound.
- DP-S10-4 (to-lead 11:14:56, item (B)): the view's order. Slug groups; `version` desc within a group; groups by the newest version's `effective_from` desc, a group whose newest version has none LAST, ties by slug asc. The §5.1 row keeps "ordered by `version`". Pinned by one view test.

Link cite (maintainer 2026-10-21 16:23:35, item 2(b)): the existing link to the dislocation view is `frontend/src/views/RatingVersionView.vue:100-107` (SL-1551, c8be222b); list rows link to `/rating/:slug/v/:version/dislocation` the same way. The `/dislocation` route lands with SL-1551, so the reachability check is expected red until the re-merge.

Holds: `frontend/src/router/index.ts`, `frontend/src/App.vue` and the reachability expectation wait for SL-1551's squash on `origin/main` (merge-dependency verdict, prep §1.4: both slices edit the router block). Not mine: DP-S11-3 (S11 serialised after S10's squash).

Pairing record (`delivery-process.md` §8 (a)+(b)): same-Work pair with SL-1554 permitted by the 11:14:56 entry; write sets are name-disjoint per prep §1.6 (SL-1554: `components/dag/*`, `RatingDesignView.vue`, `api/subGraphs.ts`; this slice: spec `03`, `api/environments.ts`, `RatingVersionListView.vue` and its test, later router/App.vue).

### Task list

1. Spec first, `b657386f`: FR 8209, §5.1 row note, OQ 8206 both ways. Check: audit-docs, req-coverage rc 0.
2. RED, `6968bba2`: cases (a)-(f), 10 tests.
3. GREEN, `5cb21f6b`: `api/environments.ts`, `RatingVersionListView.vue`.
4. Id forms (`be2436b3`) and RL 8163 fold (`cd855d65`).
5. DP-S10-4: RED `05c151f2`, GREEN `7164a61e`.
6. Held: `/rating` route, nav link, reachability, closure re-run, accessibility-tester, gate.

### Gate

Not run (held).

### Audit

Not yet.

### Build log

All logs under `~/gi-pricing-plan.local/scratch/sl-1552/`.
- 2026-10-23, `b657386f` spec; `audit-spec2.log` (check 31 gaps only), `reqcov-spec.log` rc 0.
- 2026-10-23, RED at `6968bba2`: `Test Files  1 failed (1)` / `Tests  10 failed (10)`, `red-6968bba2.log`.
- 2026-10-23, GREEN at `5cb21f6b`: `Test Files  1 passed (1)` / `Tests  10 passed (10)` / `Type Errors  no errors`, `green-5cb21f6b.log`; `pnpm type-check` rc 0; `generate:api` clean (`git status --short frontend/src/api/generated` empty); closure `closure-5cb21f6b.log`: L0 = environments.ts, the view, its test; one closure test.
- 2026-10-23, `be2436b3` id forms (space form in prose and tables: RL 8163, OQ 8206, FR 8209; hyphen form kept in the `RL-8163` / `LG-8208` front matter and in the OQ and FR table-row ids, as the existing working-id rows at `4e399fd0` are written), `cd855d65` RL 8163 folded from draft `d4258b95`, adoption line appended, INDEX regenerated (`doc-index --check` rc 0, `indexchk-b1.log`).
- 2026-10-23, DP-S10-4 RED at `05c151f2`: `Tests  2 failed | 9 passed (11)` (the new order test, and case (a)'s heading order, which DP-S10-4 changes: motor-gb has an `effective_from`, fremtpl2-demo none, so motor-gb now leads), `red-dp4-cd855d65.log`. Case (a)'s expectation was updated to the ruled order in the RED commit; no assertion removed.
- 2026-10-23, DP-S10-4 GREEN at `7164a61e`: `Test Files  1 passed (1)` / `Tests  11 passed (11)` / `Type Errors  no errors`, `green-dp4-7164a61e.log`; type-check rc 0, eslint rc 0.
- 2026-10-25, re-merge of origin/main `034781b3` (#1372, SL-1551) at `1c6c2e4a`: the only conflict was `docs/INDEX.md` (theirs taken, regenerated, `doc-index --check` rc 0); `router/index.ts` and `App.vue` untouched by this branch before the merge. Logs under `~/gi-pricing-plan.local/scratch/sl-1552b2/`.
- 2026-10-25, RED at `fff804c9`: reachability case "registers /rating and links it from the shell (FR-8209, 03 §5.3)" in `router/__tests__/reachability.test.ts`: `Test Files  1 failed (1)` / `Tests  1 failed | 2 passed (3)`, failing on `expected [...] to include '/rating'`; `red-reach.log` (`head=1c6c2e4a` plus the uncommitted test edit, `rc=1`).
- 2026-10-25, GREEN at `06303cda`: `/rating` route record (name `rating-versions`, after `/rating-versions/:id`) in `router/index.ts`, "Rating" nav link before "Demo" in `App.vue`. The first run exposed that `RatingVersionListView.vue` built its four per-version links through `base(version)`, which `routeGraph.ts`'s `resolveTarget` cannot resolve, so `finds no literal link to an unregistered route` failed on the now-scanned view; the links were inlined as literal path templates (`/rating/${version.slug}/v/${version.version}/...`) and `base()` removed, the checker left as is. `reachability.test.ts`: `Test Files  1 passed (1)` / `Tests  3 passed (3)`; `RatingVersionListView.test.ts`: `Tests  11 passed (11)`.
- 2026-10-25, import closure (item 29) at `06303cda`: changed modules = `git diff --name-only origin/main...HEAD -- frontend/src` (App.vue, api/environments.ts, router/index.ts, views/RatingVersionListView.vue and the two test files); closure by `python3 -I ~/gi-pricing-plan.local/scratch/sl-1552/closure1552.py` = those + importer `src/main.ts`; GREEN = every test file importing anything in it (8) plus `reachability.test.ts`, which reads the router and shell by `fs` rather than import. Runs of 3 files, load1 < 6, 30 s apart (`closure-green-06303cda16c3007c7451a67d11d9c9f5d2ec77a7.log`): guard, index, objectiveEditorRoute: `Test Files  3 passed (3)` / `Tests  15 passed (15)`; routeGraph, reachability, DiagnosticsView: `Test Files  3 passed (3)` / `Tests  28 passed (28)`; ModelComparisonView, ModelDetailView, RatingVersionListView: `Test Files  3 passed (3)` / `Tests  37 passed (37)`.
- 2026-10-25, `pnpm --dir frontend generate:api` rc 0 (needed after the merge: the first `type-check` rc 2 was a stale generated client, `GlmDiagnosticsPanel.test.ts` `monotonicity`), then `type-check` rc 0, `lint` rc 0 at `06303cda`.
- 2026-10-25, accessibility-review fixes (4 should-fix, in-slice) at base `3384934c`: RED `RatingVersionListView.test.ts` alone, `Test Files  1 failed (1)`, `Tests  5 failed | 11 passed (16)`; GREEN after the fix `Test Files  1 passed (1)`, `Tests  16 passed (16)` rc 0; `src/router/__tests__/reachability.test.ts` alone `Tests  3 passed (3)` rc 0; `pnpm --dir frontend lint` rc 0, `type-check` rc 0. Fixes: per-slug table `<caption class="sr-only">`, `role="status"` on Loading/empty, row links `aria-label` "Design slug@version" with `inline-block py-1`, `none` for a version live nowhere, shared focus-visible outline on the select and links. Test (f) names updated to the new accessible names.
- 2026-10-25, item 13 grant for test (f), the maintainer's entry "2026-10-25 14:34:34 GMT — Maintainer: SL-1552 gate head 697a92f8 accepted; item 13 OK GRANTED (maintainer's, not the lead's); RED rc note" in `to-lead.md`, quoted: "**GRANTED:** test (f) adopts the new accessible link names and tightens its "no pinned-table links" pattern to `/^\S+@\d+$/`; no assertion dropped or weakened (stated; the auditor verifies it in the slice audit by diffing (f)'s asserts). LG 8208 quotes this line." The same entry accepts `697a92f8` as the gate head and asks that a RED run's rc be captured next to its summary line (`set -o pipefail` or `${PIPESTATUS[0]}`).
- 2026-10-25, re-merge of origin/main `01a28e6d` (includes #1370) into `697a92f8`: the only conflict was `docs/INDEX.md` (theirs taken, regenerated, `doc-index --check` rc 0); no test run (the maintainer, "2026-10-25 15:33:58 GMT").

## PRs

None yet.
