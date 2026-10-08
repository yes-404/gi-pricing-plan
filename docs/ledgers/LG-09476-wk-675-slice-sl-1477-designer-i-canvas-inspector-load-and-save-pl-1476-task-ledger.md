---
id: LG-9476
family: ledger
title: WK-675 slice SL-1477 — Designer I, canvas, inspector, load and save (PL-1476), task ledger
status: active
created: 2026-10-08
owner: executor
tree: adfa6e7671d98aadf41536714b2da41b1e00c1ae
phase: P2
work: WK-675
slice: SL-1477
plans: [PL-1476]
corrected_by: []
relates: [RL-1473, RL-1474, RL-1475, RL-1263, FD-1366, RS-1269, WK-675]
---

# WK-675 slice SL-1477 — Designer I: canvas, inspector, load and save

Executed from `PL-1476` by `executor-s2` (sonnet). Branch `sl-1477-designer-i-canvas-inspector-load-and-save`, worktree
`.claude/worktrees/sl-1477`, from `origin/main` `d10420df` (#1241, the activation; tree `adfa6e76`). The dispatch record is
`gi-pricing-plan.local/handover/DISPATCH-WK-675-SL1477-2026-10-08.md` (FINAL; a local file, not in the repository). Stamps
are BST (`TZ=Europe/London date`). `uv sync --all-packages` and `pnpm --dir frontend install --frozen-lockfile` ran.
Test database `gipricing_sl-1477_d7eee10d`, made with `docker exec gi-pricing-postgres-1 createdb -U gipricing -T gipricing …`
and migrated with `alembic upgrade head`.

## Tasks

### Task 0 — preconditions (2026-10-08 12:17 BST)

Rows 0.1–0.11 re-run at `d10420df`; every row matches, with these line moves (the dispatch record's table, confirmed):

| Anchor | At `d10420df` |
|---|---|
| `class RatingAlgorithm` | `rating.py:423` |
| `list_rating_versions` / `get_rating_version` | `models.py:1110` / `:1136`; its decorator `:1131`; insert between `:1128` and `:1131` |
| `rating_algorithms.py` | 69 lines; `Any` `:10`, import `:18`, `body: dict[str, Any]` `:35`, return `:38` |
| `resolve_rating_version_ref` / `to_schema` | `rating_versions.py:172` / `:96` |
| `get_algorithm` / `create_algorithm` | `platform/rating_algorithms.py:135` / `:94` (unchanged) |
| `03` anchors, each `grep -cF` = 1 | FR-243 `:140`, FR-219 `:88`, `POST /sub-graphs` `:931`, `POST /rating-versions` `:943`, Vue Flow row `:1365`; header `:927`, diff row `:930`, compile row `:944` |
| `manualChunks` | function form `vite.config.ts:26`, echarts only |
| `skills-map.md` Vue Flow row | `:121` |

- **0.1:** `[False, False, False]`. **0.3:** `grep -rn UNTYPED_REQUEST_PENDING backend scripts` prints nothing: SL-1367 has not
  landed, so there is no guard entry to remove in Task 2. **0.4:** `vue-flow` count 0. **0.6:** no `/rating/` route.
  **0.8:** the header is three-cell, and `grep -n 'Purpose . Permission'` prints nothing: the three-cell forms apply.
  **0.10:** `seed.py` has no `algorithm_ref` or `rating-algorithms`.
- **0.7:** `uv run pytest backend/tests/test_rating_algorithms.py -q`: **10 passed**, 1 warning (both gate slots free).
- **Step 4:** `grep -c 'Read one Rating Version by .id., the handle' docs/specs/03-rating-engine.md` prints 0: Task 4 applies
  the by-id row as well as the `slug@version` row.
- **`pnpm-lock.yaml`** differs from goC's tree `0ee8f414` (#1237); the branch is cut after it, and `pnpm add` writes the lock.

**Step 2 — the minted rulings against the cited heads.** RL-1473 against `39bd865b`, RL-1474 against
`39bd865b`, RL-1475 against `96fa35bf`, by `git diff` of the two blobs after the id
substitution. Differences, and only these: the `created:` line, the mint note, working-id citations re-pointed to minted ids,
and dated amendments of 2026-10-05 (citation re-reads at `809a3794`; RL-1475's T4 re-anchor, which is S4's). The T-texts S2
applies — RL-1473 T1 and T2, RL-1475 T1 and T2 — are unchanged. RL-1474's ruled item 1 is unchanged.

**Step 3 — SL-1391 (S7).** It has merged (`a9ef6777`, #1206), so its `03` edits are in the base tree: the anchors above were
found once each at `d10420df`. No conflict with S2's `03` hunks.

**SL-1448 (#1236).** Not merged at the dispatch tree: FR-221 still reads unamended. The inspector's `as_at` tests are
written after it lands, to its narrowed FR-221.
### Task 1 — `RatingAlgorithmDraft` and `RatingAlgorithmSaved` (model-schema)

Test module `packages/model-schema/tests/test_rating_algorithm_draft.py` as PL-1476 gives it; the fixture's literals checked
against `rating.py` (`decimal`, `money_minor` and the step fields are accepted). Slots free before each run.

- **Red** (before any code): `uv run pytest packages/model-schema/tests/test_rating_algorithm_draft.py -q` — collection error:
  `ImportError: cannot import name 'RatingAlgorithmDraft' from 'model_schema'`. The stated cause.
- **Green:** the field set moved to `RatingAlgorithmDraft`; `RatingAlgorithm(RatingAlgorithmDraft)` keeps its validator and
  helpers; `RatingAlgorithmSaved` added; both appended to `__init__.py` and `__all__`.
  `test_the_draft_accepts_a_graph_the_algorithm_refuses`, `test_the_field_set_is_written_once`,
  `test_the_draft_still_refuses_an_unknown_field`, `test_the_saved_shape_is_the_201_wire` pass.
  `pytest packages/model-schema -q`: 514 passed. `test_sub_graphs_api.py` + `test_sub_graphs_service.py` + the new module:
  45 passed. `ruff check packages/model-schema` and `mypy` clean.

**Correction to Task 1's evidence:** the 514-passed run was a whole-package run (`pytest packages/model-schema -q`), made with both
gate slots free; outside a granted gate only named modules run (the lead's ruling, 2026-10-08).

### Tasks 2 and 5 — the typed save route and the contract

Tests appended to `backend/tests/test_rating_algorithms.py` (own database `GIP_TEST_DATABASE_URL`, slots probed free). The plan's
cyclic and unresolved bodies index `valid_algorithm()` steps 6 and 7 (`s_office`, `s_minprem`) and match the file's fixture.

- **Red** (`-k "typed or publishes"`): 1 failed, 2 passed. `test_the_save_route_publishes_typed_bodies`:
  `AssertionError: assert {'type': 'obj…tle': 'Body'} == {'$ref': '#/c…gorithmDraft'}` — the open object
  `{'additionalProperties': True, 'title': 'Body', 'type': 'object'}`. The other two pass on the base (the regression net).
- **Green:** body `RatingAlgorithmDraft`, 201 `RatingAlgorithmSaved`, handler passes `body.model_dump(mode="json",
  exclude_unset=True)`. `pytest backend/tests/test_rating_algorithms.py -q`: 13 passed.
- **Broken input** (annotation temporarily `body: RatingAlgorithm`, then restored): the failure lines as printed —
  `assert 'VALIDATION_FAILED' == 'RATING_GRAPH_CYCLIC'` (twice: `test_a_cyclic_algorithm_is_refused_at_save_time` and
  `test_the_typed_save_body_keeps_the_graph_codes`), `assert 'VALIDATION_FAILED' == 'RATING_GRAPH_UNRESOLVED_REF'`,
  `assert 'Request validation failed' == 'Rating algorithm is invalid'` (`test_another_shape_refusal_is_validation_failed`,
  `test_a_declared_output_without_an_output_step_is_validation_failed`), and the `$ref` to `RatingAlgorithm` against
  `RatingAlgorithmDraft` in `test_the_save_route_publishes_typed_bodies`.
- **Guard entry:** `UNTYPED_REQUEST_PENDING` does not exist on this tree (SL-1367 not landed): nothing to remove.
- **Contract:** `generate-contracts.py` wrote `generated.json`; `--check` rc 0 (46 up to date); `pnpm --dir frontend generate:api` rc 0.
  The Acceptance 5 `python3 -c` prints `[False, True, True]`: `RatingAlgorithm` joins `components.schemas` only with Task 3's
  `GET` (its 200), so the `[True, True, True]` reading is Task 3's. `test_contracts.py`: 152 passed, 2 skipped. `ruff`, `mypy` clean.

### Task 6 — the dependency, the chunk and the records

- `pnpm --dir frontend add @vue-flow/core@1.48.2` (exact pin in `package.json`; lock written by pnpm). `vite.config.ts`: a
  `vueflow` branch first in the `manualChunks` function. `03` §8 Vue Flow row's first cell and `docs/skills-map.md:121`'s notes
  cell carry package, version and licence. `audit-docs`: only check 31 (working id) fails.
- **STOP raised to the lead — a path outside the write set.** `pnpm add` stops with `ERR_PNPM_IGNORED_BUILDS` (`vue-demi@0.14.10`,
  a dependency of `@vue-flow/core`) and creates `frontend/pnpm-workspace.yaml` holding `allowBuilds: vue-demi: set this to true or
  false`. Measured: with `package.json` and `pnpm-lock.yaml` copied to a scratch dir, a fresh `pnpm install --frozen-lockfile`
  exits 1 with that error and writes the same placeholder file; so CI's fresh install would fail without a committed decision.
  The file is not in PL-1476's write set (:378-409). It is held uncommitted until the lead rules.

### Task 3 — the algorithm read (code and tests; the `03` rows and `req` markers wait for the FR id form)

Five tests appended to `backend/tests/test_rating_algorithms.py` (read-back, unknown version, another workspace, 403 without
`rating:read`, the contract `$ref`). Own database, slots probed free. **Red** (before the route): all five failed — the router's
404 for an unrouted path (`assert 404 == 200`; `assert 404 == 403`) and `KeyError: '/api/v1/rating-algorithms/{slug}@{version}'`.
The app answers an unrouted path with code `NOT_FOUND` as well, so the two 404 tests also pin the handler's own detail
(`No rating algorithm motor-gb@99 in this workspace.`) and failed with `assert 'Not Found' == 'No rating al…is workspace.'`.
**Green:** `pytest backend/tests/test_rating_algorithms.py -q`: 18 passed. **Broken input** (handler returns
`RatingAlgorithmDraft`): `assert {'$ref': '#/c…Draft-Output'} == {'$ref': '#/c…ingAlgorithm'}`, reverted. Contract
regenerated, `--check` rc 0; Acceptance 5's `python3 -c` now prints `[True, True, True]`. `ruff`, `mypy` clean.

### Task 4 — the Rating Version read by pair (code and tests; `03` rows and markers wait)

Four tests in `backend/tests/test_rating_versions.py`. Delta from the plan: SL-1430 (`5351f116`) added `algorithm_ref` to
`create_rating_version`, so the plan's `_set_algorithm_ref` helper is not needed; `_draft_with_algorithm` passes it directly
(version 5 against the Rating Version's 1). **Red:** `assert 422 == 200` (pair) and `assert 422 == 404` (isolation), and the
`KeyError` for the contract test — the by-id handler's `uuid_parsing` 422, the stated cause. The 403 test passes on the base
(permission is checked before path parsing), so it is a regression net, not a red. **Green:** 8 passed
(`-k "own_slug_at_version or another_workspaces_rating or pair_read_needs or read_publishes_rating_version or over_http"`).
**Broken input:** the new route registered after the by-id read — `assert 422 == 200` and `assert 422 == 404`; the version
matched against the algorithm's number — `assert 404 == 200` on the pair read (the "algorithm's number answers 404" assertion
is not reached, it fails at the first); both reverted (`git status` shows only the route and the tests).

### Task 6 addendum — the STOP ruled (option A)

The lead's ruling, `to-lead.md`, header: "## 2026-10-08 12:30:31 BST — S2 (SL-1477, #1245) STOP RULED: (A) frontend/pnpm-workspace.yaml with allowBuilds vue-demi false joins the write set; FR working ids in the hyphen form at the two mechanical sites ALLOWED". `frontend/pnpm-workspace.yaml` (`allowBuilds:` / `vue-demi: false`) **joins the write set by name** (PR body too); options B and C refused.

- **Condition 1:** a fresh scratch copy of the committed `frontend/` plus the yaml, `pnpm --dir <scratch>/frontend install --frozen-lockfile`:
  rc 0 (`pnpm --version` 11.21.0). Without the yaml the same fresh install exits 1 (`ERR_PNPM_IGNORED_BUILDS`).
- **Condition 3:** the lockfile diff against `d10420df` is 141 insertions, 0 deletions, and only `@vue-flow/core` 1.48.2 and its
  closure: 15 `packages:` entries (`@types/web-bluetooth`, `@vue-flow/core`, `@vueuse/core|metadata|shared` 10.11.1, `vue-demi`
  0.14.10, and `d3-color|dispatch|drag|ease|interpolate|selection|timer|transition|zoom`) and 8 `snapshots:` entries. The `03`
  §8 and `skills-map` rows ride this PR (commit `86518b18`).
- **Condition 2** (lint, type-check, test, build green; a test that mounts a component importing `@vue-flow/core`): pending, Tasks 7–11.

### Tasks 3 and 4 addendum — spec rows, markers, and one dropped step

- RL-1475 T1 and T2 and RL-1473 T1 and T2 (three-cell forms; header has no `Permission` column) applied to `03` from the minted
  rulings' code blocks, byte for byte, with only `<date>` = 2026-10-08, `RL-<this>` = RL-1475 / RL-1473 and the FR ids filled; the
  by-id row too (its grep was 0). The ruled FORM: the hyphen form (`FR-9474`, `FR-9473`) only in the FR row's bold id cell and in
  `@pytest.mark.req`; the space form (`FR 9474`, `FR 9473`) elsewhere. `FR 9474` is the algorithm read, `FR 9473` the Rating
  Version address (the lead's working ids; the minter re-points every site, and `git grep -nE` for the two working ids (hyphen form) is 0 at the merge head).
  `req-coverage` lists both ids with test files. `audit-docs`: only check 31 (two gaps between the working ids and 1477/9476),
  expected until the mint.
- **Dropped step (not a write-set change):** PL-1476 Task 4 Step 2's `_set_algorithm_ref` helper. `create_rating_version` takes
  `algorithm_ref` since SL-1430 (`5351f116`, #1227): `platform/rating_versions.py`, the `algorithm_ref: ArtifactRef | None = None`
  parameter of `create_rating_version`; `_draft_with_algorithm` in `test_rating_versions.py` passes it directly.

### Task 7 — API modules and `graph.ts`

`frontend/src/api/ratingAlgorithms.ts`, `getRatingVersionByRef` in `ratingVersions.ts`, `components/dag/graph.ts`,
`__tests__/fixtures.ts` (the server fixture `valid_algorithm()`, dumped to JSON by the real function and typed
`RatingAlgorithmDraft`; it has **11** steps. The plan's "twelve" does not reproduce: `PRE_EDIT_VALID_ALGORITHM` has 9, and no step
is missing from the 11 that the plan's own `s_*` references name) and `__tests__/graph.test.ts` (7 tests: edges, no edge for
an unresolved name or a self-edge, graph order, a cycle terminating, layout columns and determinism, the pinned cycle depth,
`parseRef`).

- **Order slip, ledgered:** I wrote `graph.ts` before its test. The test is proven red on the base by removing the module:
  `Error: Failed to resolve import "../graph" from "src/components/dag/__tests__/graph.test.ts"`; restored, green.
- **Run scope slip, ledgered:** `pnpm --dir frontend test -- graph` ran the whole frontend suite (the filter did not apply
  through pnpm): 622 passed, both gate slots free at the probe. Later runs use `pnpm exec vitest run <path>`.
- `pnpm generate:api`, `type-check` and `lint` clean.

### Task 8 — `StepNode.vue`, `StepInspector.vue`, `problems.ts`

Plan delta: the required-field gaps are a pure `stepProblems(step)` in `components/dag/problems.ts`, not an exposed ref of the
inspector, because `DagDesigner` needs them for every step, not only the selected one; the inspector lists them for its step.
`as_at` is a select over the declared `date` inputs (FR-221 as it stands at the dispatch tree; SL-1448 #1236 not merged — the
test is revisited after it lands). 9 tests in `StepInspector.test.ts`, one per FR (213, 215, 220, 221, 222/223, 223 new-step,
225, 226, 244). **Red:** before any component, the file failed at import: `Error: Failed to resolve import "../problems" from
"src/components/dag/__tests__/StepInspector.test.ts"`. **Green:** `pnpm exec vitest run src/components/dag`: 16 passed (7 graph +
9 inspector). `type-check` and `lint` clean. One test-side correction after the first green run: the `as_at` option list holds a
disabled placeholder, so the assertion filters the empty value. `StepNode.vue` imports `Handle` from `@vue-flow/core`; the mount
test for it (condition 2) comes with Task 9's `DagDesigner`.

### Task 9 — `NodeNavigator.vue` and `DagDesigner.vue`

- **Navigator:** 6 tests in `NodeNavigator.test.ts` (options in graph order; arrows; Home/End; typed `step_id` prefix; Enter emits
  `select`; Delete opens `role="alertdialog"` and `remove` is emitted only after "Remove step", not after Cancel). **Red:** import
  failure, `Failed to resolve import "../NodeNavigator.vue"`. **Green** after the component. The plan's typeahead example `s_o`
  does not select `s_out` on the real fixture (`s_out_office` precedes it in graph order); the test types `s_pay` → `s_payable`.
- **Designer:** 4 tests in `DagDesigner.test.ts`. **Red:** import failure for `../DagDesigner.vue`. **Green:** 26 passed over
  `src/components/dag` (`pnpm exec vitest run src/components/dag`).
- **Condition 2 — the `@vue-flow/core` mount test:** `DagDesigner.test.ts` mounts `DagDesigner` with the **real** `VueFlow` (no
  stub of `@vue-flow/core`; `StepNode` renders its `Handle` through it) in happy-dom, and finds one node per step by its
  `aria-label`. The only shim is a no-op `ResizeObserver` class, a browser API happy-dom lacks (not the library). The canvas's pan
  and zoom are measured in Task 11. `type-check` and `lint` clean.
- Plan deltas: `DagDesigner` exposes `problems` as `"<step_id>: <message>"` over every step (from `stepProblems`); the canvas
  nodes are not draggable and not selectable (selection is by the navigator).

### Task 10 — `RatingDesignView.vue`, the route and the FR-25 link

- **View:** 7 tests in `src/views/__tests__/RatingDesignView.test.ts` (the pair resolved from the URL; the algorithm read through the
  parsed `algorithm_ref` and one node per step, on the **real** `@vue-flow/core`; save with the version pre-filled to loaded + 1;
  a refused save shown with its `code` and `detail`; a 409 shown the same way; save disabled and the gap listed while a step's
  required field is empty; DP-S2-3 (a): the "pins no algorithm" `role="status"` text, no algorithm read, a save body with the
  version's slug and version 1). Test names carry the working ids in the space form (`FR 9473`, `FR 9474`). **Red:** import
  failure, `Failed to resolve import "../RatingDesignView.vue"`. **Green:** 7 passed.
- **Delta:** the view derives the save-blocking gaps itself from `stepProblems` over the draft, so `DagDesigner`'s `defineExpose({
  problems })` (Task 9) was removed rather than left as an unused surface. `RatingDesignView` mounts `DagDesigner` through
  `defineAsyncComponent(() => import(…))`, so `@vue-flow` stays in the lazy chunk.
- **Route and link:** route `rating-design` after `rating-version` in `router/index.ts`; `RatingVersionView.vue` links
  "Open in the designer" to `/rating/<slug>/v/<version>/design`; its test's `RouterLink` stub passes `to` through as `href`.
  **Broken input** (the view reverted to HEAD, link absent): `reachability.test.ts` — `expected [ '/rating/:slug/v/:version/design' ]
  to deeply equal []`, and the link test — `Unable to find role="link" and name "Open in the designer"`; restored, both green,
  with no whitelist change. `vitest run` over the view, router and `components/dag` files: 60 passed. `type-check` and `lint`
  clean (one test-side type fix: `ProblemDetail` requires `errors`).

### Task 11 Step 1 — the bundle delta (Acceptance 13)

Method: `git worktree add --detach` of `origin/main` `60e9254c` under `/home/puzhenhao1989/.cache` (removed after), `pnpm install
--frozen-lockfile`, `pnpm generate:api`; then `pnpm --dir frontend build` there and in this worktree at `207de8f0`; both with the gate
slots free at the probe and load 3. Gzip is zlib level 9 over each `dist/assets/*.js`. `grep -l 'vue-flow' dist/assets/index-*.js`
prints nothing (rc 1): no `@vue-flow` module is in the entry chunk.

| chunk | before raw / gzip | after raw / gzip |
|---|---|---|
| `index-*.js` (the shared entry, always shown) | 18,637 / 6,734 | 17,672 / 6,241 |
| `vueflow-*.js` (new) | — | 150,421 / 48,038 |
| `DagDesigner-*.js` (new) | — | 18,598 / 5,785 |
| `RatingDesignView-*.js` (new) | — | 4,734 / 2,141 |
| `problems-*.js`, `preload-helper-*.js` (new, shared helpers) | — | 1,775 / 848 and 1,383 / 751 |
| `RatingVersionView-*.js` | 2,146 / 1,018 | 2,327 / 1,085 |
| `ratingVersions-*.js` | 173 / 146 | 255 / 164 |
| `runtime-dom.esm-bundler-*.js` | 9,603 / 4,224 | 9,886 / 4,341 |
| `echarts-*.js` | 714,256 / 240,778 | 716,948 / 241,732 |

44 other chunks differ by at most 19 gzip bytes each (re-ordered shared helpers; no source change). The designer is
`vueflow` + `DagDesigner` is 53,823 B gzip; RS-1269's figure for the designer chunk was 49,445 B gzip: this build's `vueflow` is
48,038 B gzip, 1,407 B less, reported as a difference, not a verdict. The `echarts` chunk moves by 2,692 raw bytes with no
`echarts` source change in the slice (a shared-module placement difference), noted here rather than explained.

### Task 11 Step 3 — the accessibility check (Acceptance 10)

`accessibility-tester`, read-only, run on `207de8f0`; it read source and ran the dag/view vitest files (33 passed); **no browser,
screen reader or axe was run** (axe/Playwright are not installed), so nothing is browser-confirmed. Its findings and their
dispositions:

| # | finding | disposition |
|---|---|---|
| 1 | on-node errors absent (§5.3 "error on the node"; problems shown only in the inspector and the view list) | **FD candidate to the lead**: on-node live validation is S3's (RL-1474; `00` FR-24's designer exception stays undischarged until S3) — not fixed here |
| 2 | selected option unmarked; active option by background colour only | **fixed**: selected = left border + bold, active = outline (test `1.4.1`) |
| 3 | weak focus indicator (listbox and `control` class) | **fixed**: `focus-visible` outline on both |
| 4 | `aria-modal` without a trap | **fixed**: `aria-modal` dropped (inline confirmation), `aria-describedby` added |
| 5 | removal not announced; active reset to first | **fixed**: persistent `role="status"` "Removed step …", active moves to the neighbour (test `4.1.3`) |
| 6 | active option can scroll out of view | **fixed**: `scrollIntoView({ block: "nearest" })` on change (no jsdom assertion; needs a browser) |
| 7 | `aria-label` on role-less `div`s | **fixed**: `role="group"` on the canvas wrapper (names the navigator as the way through) and on the node |
| 8 | status/alert announcements inconsistent; disabled Save unreachable | **fixed**: "Loading…" `role="status"`, a persistent saved-status region, Save uses `aria-disabled` + `aria-describedby` the problems list (test) |
| 9 | mode-mismatch `role="status"` conditionally rendered | **carried, low**: text carries the meaning (1.4.1 met); announcement needs a browser |
| 10 | problems not tied to fields | **fixed** for the five required fields: `aria-invalid` + `aria-describedby` (test `3.3.1`) |
| 11 | read-only `step_id` unexplained | **fixed**: help text |
| 12 | link outside `dd`; colour-only link | **fixed**: link in a `dd`, underlined |
| 13, 14 | checkbox target size; slate-500 contrast | **carried, low**: needs a browser/contrast tool |
| 15 | typeahead matches `step_id` only | **informational** |

Needs a browser or assistive technology (carried to the lead for the exit-demo check, not waived): option-change announcements
from `aria-activedescendant`, `alertdialog` reading, Vue Flow's own DOM roles, 320 px / 400 % reflow, measured contrast and
target sizes.

### Task 11 — the lead's ruling on Steps 1 and 3 (to-lead.md, "… S2 (#1245 @1d3ab0c0) Task 11 …")

- **No FD for finding 1.** On-node validation is WK-675 S3's, per `RL-1474` :36–46 (the question, and the §5.3 "error on the node"
  obligation, which `00` FR-24's designer exception keeps binding until S3 discharges it); it stays in P2. Carried, not waived.
- **The `echarts` chunk +2,692 B raw — cause (diffing the base and head chunk text, base rebuilt at `60e9254c`):** the head chunk
  carries Vue runtime code the base lacks — `customRef` (via `@vueuse/core` under `@vue-flow/core`) and the async-component and
  hydration helpers `defineAsyncComponent` needs (`loadingComponent`, `__asyncHydrate`, `isUnmounted`, `setTimeout`/`clearTimeout`
  paths) — which Rollup places in the shared vendor chunk that also holds `echarts`; the `manualChunks` arm did not move the
  `echarts` boundary. The rest of the chunk's text differs only by minifier renames.
- **Browser-only accessibility items, each carried with the owner WK-675 S3's audit (a browser pass, axe/Playwright, on the
  designer); none is claimed browser-confirmed:** (a) option-change announcements from `aria-activedescendant` on the listbox;
  (b) the `alertdialog` read on open and Escape/Tab order around it; (c) Vue Flow's own DOM roles and any focusable element it adds;
  (d) 320 px / 400 % reflow of the two-column layout; (e) measured contrast (`bg-sky-100` active option, slate-500 on slate-50, the
  focus outline); (f) target sizes (nullable checkbox, Save); (g) the mode-mismatch `role="status"` announcement; (h) the
  `scrollIntoView` behaviour of the active option.

### Merge of main (SL-1448, #1236 at `680fb9ac`) and the `as_at` test redone

`git merge origin/main` (never a rebase): the only conflict was `docs/INDEX.md` (generated; taken from main's side and regenerated
with `scripts/doc-index.py`, no markers left); `03` merged clean. `audit-docs` after the merge: only check 31's two working-id gaps
(an earlier run also failed check 2 on a truncated working id written as a regex in this ledger, which the check parsed as a requirement id; reworded).
FR-221 at main now reads (amended 2026-10-08, RL-1446): **`as_at` names `effective_date` — the quote's stamped date — or a declared
`date` input, and nothing else.** The inspector's `as_at` control now offers `effective_date` plus the declared `date` inputs
(`StepInspector.vue`, `asAtOptions`); it repeats no server check. Tests (2, in `StepInspector.test.ts`): a lookup over an
algorithm with an extra `date` input and a `string` input offers exactly `effective_date` and the extra `date` input; a **new**
lookup (`as_at` empty) on an algorithm that does not declare `effective_date` still offers it. **Red** (the pre-merge component
restored): `AssertionError: expected [] to deeply equal [ 'effective_date' ]`; restored, 11 passed. Re-run after the merge, named
modules behind the slot probe, own database: `test_rating_algorithms.py`, `test_rating_versions.py`,
`test_rating_algorithm_draft.py`, `test_contracts.py` — 221 passed, 2 skipped; `generate-contracts.py --check` rc 0; `ruff`, `mypy`,
frontend `type-check` and `lint` clean; `vitest` over `src/components/dag` and the view and router files green.

### Task 11 Step 2 and Task 12 — the held slot (GATE-1 granted for head `c788de9b`)

Slot `/tmp/slots/gate-1`, one `flock` over both parts (`env -C <worktree> bash gate.sh`, `timeout 3600`), harness and script under
`/home/puzhenhao1989/.cache/fps-harness` (outside the repository). **Slot incident, mine:** a debug run of the harness an hour
earlier left its `pnpm … vite` wrapper alive (the wrapper inherited the lock's file descriptor), which held `gate-1` and made the
first granted attempt time out (`flock -w 900`, rc 98, nothing run). Found by `fuser`, the process (pid 1166743, command line naming
this worktree, started by my debug run) stopped by pid; `run.sh` now stops its server by the pid it started. No other session's
process was touched.

**fps (Acceptance 15), the Vite DEV build** (`vite --port 5391`), the real `/rating/fps-demo/v/1/design` view, 200 steps in RS-1269's
mix (30 input, 10 lookup, 70 table, 5 model_call, 60 expression, 20 constraint, 5 output), chrome-headless-shell 153.0.8010.12
(Playwright 1.63.0 from the lockfile of `a3862e01`'s `pw/`), SwiftShader software renderer, 1600×900, instrument = RS-1269's
`DrawFrame` trace count. **Deviations, stated:** (a) the 200-step algorithm passed the platform's own save-time path
(`_parse_algorithm` + `_issues_to_error`, the first two statements of `create_algorithm`) but was **not persisted to a database**;
the browser's `/api/v1` reads were served by the harness (route interception) with the algorithm JSON, and the auth guard's
`isSignedIn` was served as true (a route-rewritten copy of `src/auth/session.ts`); Vue Flow, the designer and the dev build are the
repository's. (b) Load: 1.4 → 3.6 (limit 12); `uptime` before `1.40`, after `3.18`; the run ran alone in the held slot
(12:34:23–12:38:18 UTC, 13:34:23–13:38:18 BST). Per-run starts/ends and load are in the harness output (kept with the harness).

| form (N=5) | presented-frame fps per run | notes |
|---|---|---|
| pan-drag (400 moves out, 400 back) | 31.8, 34.5, 35.6, 35.8, 34.7 | 401 distinct viewport transforms each; DrawFrame 487 each; every run has one 5.25 s frame gap (unexplained; included in the span) |
| programmatic zoom (`setViewport`, 3 s) | 58.5, 59.8, 59.8, 59.7, 60.1 | 173–178 frames, 176–181 distinct transforms |
| wheel zoom, back-to-back (240 events) | not measurable by this instrument | the trace holds 1 `DrawFrame` while 31 distinct viewport transforms were applied |
| wheel zoom, paced 8 ms (240 events) | not measurable by this instrument | the trace holds 2 `DrawFrame`; paced fps figures printed (57–137) are two-frame spans and are not reported as fps |

**The second form cannot be driven faster than one event per ~33 ms here:** Playwright's `page.mouse.wheel` awaits each event, 240
events took 8.0–8.1 s back-to-back (33.5 ms per event) and 12.0 s with an 8 ms wait (50 ms per event), so the harness cannot send the
wheel faster than the one event per ~30 ms RS-1269's amendment names; wheel-zoom fps is therefore not claimed.

**Task 12, the full two-half gate (GATE START 13:38:18 BST, END 14:21:50 BST; alembic current = heads = `f3a7c1d9e2b4`):**

| stage | rc |
|---|---|
| ruff | 0 |
| mypy | 0 |
| lint-imports | 0 |
| audit-docs | **1** — then: the check-31 working-id gaps, and a truncated working id in my own ledger text (below) |
| req-coverage | 0 |
| generate-contracts --check | 0 |
| pytest | **1** — 14 failed, 5113 passed, 4 skipped (2506 s) |
| frontend install --frozen-lockfile / generate:api / lint / type-check | 0 / 0 / 0 / 0 |
| frontend test | 0 — 102 files, 653 tests passed |
| frontend build | 0 |

The 14 pytest failures: **12** fail only because `audit-docs` fails on the real tree (they assert it passes: `test_audit_docs_ids`,
`test_audit_docs_finding_citations`, `test_audit_docs_process_core_digest` ×2, `test_audit_docs_w37_11_ceiling`, `test_register_lint`
×3, `test_register_owed`, `test_repository_invariants` ×2) and `test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`
(the working-id allocation is not contiguous): the check-31 working-id set, expected until the mint. **Two were mine**, found by this
gate and fixed after it (new head, so a re-run needs a new grant): (i) the ledger carried a `git grep` regex of the working ids
(a character class cut the id short) that `audit-docs` check 2 parsed as a different, undefined requirement id; reworded. (ii) `packages/pricing-core/tests/
test_rating_committed_strings.py::test_every_committed_string_is_accepted_or_a_declared_negative` — `AttributeError: 'NoneType' object
has no attribute 'lower'`: that test greps every tracked file for `expr`/`condition`/`key_expr` followed by a quoted string, and an
**empty** literal (`expr: ""`, `condition: ""` in `DagDesigner.vue`'s `blank()`) yields `None` (`group(2) or group(3)`) and crashes it;
the designer now uses a named empty constant, the test passes (4 passed). The test's own `or` on an empty match is a defect in a
test outside this slice's write set: **FD candidate to the lead.**

## PRs

The slice PR is a draft, opened by the executor; the executor does not merge it.
