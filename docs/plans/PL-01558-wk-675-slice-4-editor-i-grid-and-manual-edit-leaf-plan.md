---
id: PL-1558
family: plan
kind: leaf
title: WK-675 Slice 4 — Editor I, the rate table grid and manual edit (FR-228, FR-229, FR-231, FR-232, FR-234, FR-1186, FR-10, FR-21, FR-25): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-09            # original date 2026-10-05, set at the draft; minted 2026-10-09
owner: planner
tree: 9489405370a1ce06c2b985ad88c7d471438febb1
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1286, PL-1371, SL-1369, RL-1184, RL-1263, FD-1366, PL-1364, SL-1367, SL-1391, PL-1419]
---

# PL-1558 — WK-675 Slice 4: Editor I, the rate table grid and manual edit, leaf plan

*(Minted 2026-10-09 as PL-1558 from working id 9582, in the D3 batch mint; citations of the ids minted in this batch, and of ids already minted on main (RL-1474, RL-1475, RL-1473, RL-1445, PL-1476, SL-1477, FD-1437, RL-1438), are re-pointed outside quotes, quoted text and quoted channel entries stay as quoted, and cites of PL 9576, PL 9574, SL 9577 and SL 9575 stay working ids. (Re-minted +1 on 2026-10-09 by the minting rewrite, on the lead's 13:09:28 BST ruling (1): first minted as PL 1557, before the D1 mint moved the allocation.))*

This plan is filed under working id 9582. Its `SL-` row under WK-675 in
[`../roadmap.md`](../roadmap.md) is slice working id 9583, `draft`. The lead reserved both on
2026-10-05, with the rows and leaf plans of S3 (SL-1557, PL-1556), S13 (SL 9577, PL 9576) and
S14 (SL 9575, PL 9574), and mints them at the merge turn. This PR carries all four rows. The
plan was written by the planner (planner-675) on the lead's prep-wave brief of 2026-10-05,
section AW. Evidence was read at origin/main `137bc817`, tree `94894053`, on 2026-10-05
16:44–17:10 BST, and re-checked at `4d3be141` (17:14:42 BST), which adds only `PL-1419` (#1127)
over `137bc817`: no file this plan cites changed.

The rulings this plan rests on are still working ids on unmerged PRs: RL-1475 (#1067), RL-1473
(#1055), and RL-1445 (#1162). Each is cited by its working id and PR, and each is re-anchored
at the mint.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds:
> - `test-driven-development`: every acceptance item is seen red, by its cause, before the
>   code that turns it green;
> - `python-test`: the `req` marker and negative tests;
> - `python-package`: Task 1's model-schema change;
> - `fastapi-service`: Tasks 2 and 3;
> - `contract-schema` and `contract-guard`: the regenerated contract;
> - `spec-change`: Tasks 1–3, with the decision-maker's texts byte for byte;
> - `vue-frontend`, `vue-best-practices` and `vue-testing-best-practices`: Tasks 5–7;
> - `dev-commands`: the two-half gate and the pnpm install;
> - `git-hygiene`.
>
> The executor is spawned from `.claude/roles/executor.md`.

## Goal

An actuary opens a Rate Table that a Rating Version pins, at
`/rating/:slug/v/:version/tables/:tableSlug`. The grid is typed by the table's declared key
and value columns (FR-228). It pages through the cells from the server for either storage,
with no Job (FR-232). The actuary edits values inline as exact decimals (FR-10, FR-21), writes
the required change note (FR-229), reviews the cell diff against the base version (FR-231's
confirmation diff), and confirms. The server creates the new version, or it refuses with
FR-234's errors, each shown on the cell it names. A Rate Table Version shows no approval
state (FR-1186).

**Architecture.** The backend comes first, spec-first:
- RL-1475's two reads: the definition `GET /api/v1/rate-tables/{slug}@{version}` → `RateTable`,
  and `GET /api/v1/rate-tables/{slug}@{version}/cells` → `Page[RateTableCell]`, ordered by key
  in one Python function for both storages;
- the new model-schema type `RateTableCell`, with `rows` and both `default_row` fields
  retyped to it;
- the manual-edit route `POST /api/v1/rate-tables/{slug}/versions` (register F-W10-3), typed
  in both directions (FD-1366's dispatch template line), built on the import route's
  preview-then-confirm path, with its request and error shapes as DP-S4-1 and DP-S4-2 rule.

Then the frontend:
- `@tanstack/vue-table` 9.2.6 (MIT), used core-only (`tableFeatures({})`), with the server's
  cursor doing the paging;
- `frontend/src/api/rateTables.ts` over the generated client;
- `RateTableEditorView.vue`, the route, and the FR-25 link from the Rating Version page.

**Tech stack.** FastAPI + Pydantic v2; model-schema; Vue 3 `<script setup lang="ts">`;
`@tanstack/vue-table`; Vitest + Testing Library; pytest.

**Spec:** `docs/specs/03-rating-engine.md` §3.3 (FR-228–FR-235, FR-1186), §4.2, §5.1 (the
rate-table rows `:901-907` at `137bc817`), §5.3 (the Rate table editor row, `:1232`), §8
(`:1316`); `docs/specs/00-overview.md` FR-10 (`:221`), FR-21 (`:232`), FR-25 (`:236`). Map
plan: `PL-1286` S4 (`:306`).

## The decisions this plan rests on, quoted

1. **DP-4 (a)**, `PL-1286` `:243`: "the rate-table cells and a version's table list in
   **S4**", ruled by the maintainer (by delegation), "2026-09-30 05:34:33 BST — SCOPE
   DECISION: #920 DP-4, option (a)". **(a′) is pre-authorised as a fallback:** "if S2's or
   S4's leaf plan must split, the split, or one read-routes slice before S2, needs no further
   scope call; the planner records it at that leaf plan's ACK". This plan does not split
   (DP-S4-4).
2. **RL-1475** (#1067, head `15e1bfde`), *Ruled* item 2 and item 3, and T3, T4 and
   T5. Item 3: "**No route for a version's table list.** It is `pins.rate_tables` on the
   Rating Version, which RL 9766's read returns."
3. **RL-1473** (#1055, head `07d9d230`), DP-5 (a): "A Rating Version is
   **addressed** by its `slug@version` and read by it. … In `/rating/:slug/v/:version/…`,
   the slug and version are the **Rating Version's own**, never its algorithm's." S2 builds
   that read (SL-1477, PL-1476, #1131).
4. **RL-1184 E5** (`docs/rulings/RL-01184-*.md:122-127`): the manual-edit row "now carries a
   request shape that follows the import route (edited cells against a named base, a diff for
   confirmation, `confirm: true` creates), the FR-229 change note, and the owner." The row is
   `03:901`. It names no type, so DP-S4-1 asks for one.
5. **FD-1366** *Disposition*: "**Dispatch-record template line for WK-1178:** 'every new or
   changed JSON route has typed request and 2xx response schemas.'" This slice adds three JSON
   routes, and holds itself to that line.
6. **RL-1263** item 4 and **RL-1445** (#1162, head `381254c3`) items 1–2: at most
   one full gate at a time; two slices from the same Work run at once only when the dispatch
   record shows (a) the file sets resolved and (b) no plan dependency either way.

## Status

`draft`. It goes `active` only through its Activation needs, in a separate activation PR.

*Dated note, 2026-10-05 (written 18:40:25 BST, pre-mint): P-texts of RL-1555
applied 2026-10-05. RL-1555 (working id; #1198 at `0e872448d7dde4d652ae15bafa097983909441bc`), §"The plan texts" lines 204–230, gives P1–P6 for this plan; each is
applied byte for byte and nothing else changed. Counts (Python `str.count` over this file):
every find string 1 before and 0 after, every new text 0 before and 1 after — P1 (after the
DP-S4-4 row of the decision-point table; that anchor stays, by design), P2 (the write-set row replaced, and the
`model_schema/__init__.py` row inserted after it; that anchor stays, by design), P3 (Acceptance
7, appended), P4 (Acceptance 8), P5 (the test's assert), P6 (Task 3 Step 3, two finds). The
rulings of activation need 2 are RL-1555 items 1–3; need 2 is met when RL-1555 mints. RL-1555
item 4 (serialise with `SL-1391`) is need 4 already.*

### Activation needs, in order

1. **RL-1475 minted** (#1067), so FR-<b> and T3–T5 have their minted ids.
2. **DP-S4-1 and DP-S4-2 ruled** by the decision-maker, with the spec texts for the
   manual-edit row's request and response types and its located-error extension. This is a
   new `RL-`. No working id is reserved for it yet: the lead reserves one and spawns the DM.
3. **S2 (SL-1477) merged.** This slice consumes S2's `GET /api/v1/rating-versions/{slug}@{version}`
   and its `/rating/:slug/v/:version` route form (DP-S4-3). Under RL-1445 item 2(b), S2 and S4
   cannot run at once.
4. **`SL-1391` (WK-673 S7) not running.** It edits the same files (*Write set*). The two
   serialise; whichever merges second merges main and re-gates.
5. **Task 0 re-run** at the dispatch tree, with every anchor in this plan found exactly once.
6. **The maintainer's agreement and the lead's go**, recorded in the dispatch record.

## Acceptance Standard

Every item is a command a fresh reviewer can run on the slice's branch. Every new test
carries `@pytest.mark.req("<FR>")` (backend) or names its FR in the `describe` title
(frontend), and each was seen red, by its cause, before the code that turns it green.

1. **Definition read (FR-<b>).** `uv run pytest backend/tests/test_api_rate_tables.py -k
   definition_read -q` passes. The 200 body validates as `RateTable` and has no `rows` and
   no `cells` key. Red: the handler returns the `RateTableVersion`.
2. **Cell pages, both storages, in key order (FR-<b>, FR-232).** `uv run pytest
   backend/tests/test_api_rate_tables.py -k cell_pages -q` passes. A table written as `rows`
   and the same cells written as `parquet` (threshold lowered in the test) page to identical
   sequences. The expected order is written out in the test: `"10"` before `"9"`, `"B"`
   before `"a"`. No Job row is created. Red: leave either path unsorted, or sort the rows path
   in SQL.
3. **Paging.** `-k cell_paging` passes: concatenated pages equal the full cell set with no
   duplicates; a malformed cursor answers 400 `VALIDATION_FAILED`; `limit=201` answers 422.
4. **Isolation.** `-k rate_table_isolation` passes: another workspace's `slug@version`
   answers 404 `RATE_TABLE_MISS` on both reads, and on the manual-edit route.
5. **The FR-232 bound, stated under test.** `-k cells_bound` passes. It pins that one page
   of a rows-stored version loads at most the version's cell count, and that count is at
   most the workspace threshold (default 250 000). A parquet version reads its blob once per
   page.
6. **Manual edit, preview (FR-229, FR-231).** `-k manual_edit_preview` passes: a valid body
   with `confirm: false` answers 200 with the DP-S4-1 diff type; nothing is created
   (`rate_table_versions` row count unchanged). Red: create on preview.
7. **Manual edit, confirm.** `-k manual_edit_confirm` passes: the same body with
   `confirm: true` answers 201; the new version is `base + 1`, carries the change note, and
   its cells equal the base's cells with the edited values. A second confirm against the same
   base answers 409 (the existing `_persist_new_version` refusal). The new version carries `created_by_edit` `{applied_to: <the base>, edited_cells: <the number of edits>}`, and a seeded version carries none (red first, RL-1555 item 2).
8. **Manual edit refusals (FR-229, FR-234).** `-k manual_edit_refusals` passes, one test per
   case: an empty or whitespace change note → 422; an edit whose key is not in the base → 422;
   a duplicated key in the edits → 422; a value out of the declared bounds → 422 whose located
   errors are `FieldError`s with `field` `edits.<i>.<value name>` (RL-1555 item 3); an unknown-key edit → 422 with a `FieldError` coded `UNKNOWN_KEY`, never 500; a float-typed JSON value → 422 (FR-21); an unknown
   field → 422 (`extra="forbid"`).
9. **Contract.** `uv run python scripts/generate-contracts.py --check` exits 0. In
   `docs/contracts/` the cells read's 200 is a `$ref` to `Page_RateTableCell_`, the
   definition read's is a `$ref` to `RateTable`, the manual-edit route's request body and its
   200 and 201 responses are `$ref`s to the DP-S4-1 types, and `RateTable.default_row` is no
   longer `additionalProperties: true`. If `SL-1367`'s guard is on main by then, the guard
   passes with no new exclusion entry.
10. **The stored-data stop (RL-1475 *What it obliges*).** Task 0 step 4's query output is
    pasted in the ledger. It shows no persisted non-`str` row or `default_row` value.
11. **Grid (FR-228, FR-232).** `pnpm --dir frontend test -- RateTableEditorView` passes:
    the columns are the table's key columns then its value column, in declared order, with
    the value's unit in its header; Next and Previous follow the server cursor; the view never
    calls `pageThrough` and never fetches a second page before the user asks.
12. **Inline decimal editing (FR-10, FR-21).** `pnpm --dir frontend test --
    DecimalCellInput` passes: the edited value is sent as the exact string typed; the value
    never passes through `Number`/`parseFloat` (`git grep -n -E 'Number\(|parseFloat|parseInt'
    -- frontend/src/components/rating/` prints nothing); a syntactically invalid entry is
    flagged before send.
13. **Confirm flow (FR-229, FR-231, FR-234).** `-- RateTableEditorView` passes: save is
    disabled until a non-blank change note exists; save posts `confirm: false` and shows the
    diff; confirm posts `confirm: true`; a 422 with located errors marks each named cell.
14. **No approval state (FR-1186).** The editor test asserts that no status, approval or
    lifecycle text renders, and the view's source holds no `status` read
    (`git grep -n 'status' -- frontend/src/views/RateTableEditorView.vue` prints nothing).
15. **Table list from the pins (RL-1475 item 3).** The Rating Version view test asserts one
    link per `pins.rate_tables` entry, and no list call is made (the mocked client records
    exactly one `GET /rating-versions/{slug}@{version}` and nothing else).
16. **Reachability (FR-25).** `pnpm --dir frontend test -- reachability` passes with the new
    route reachable from the entry by links alone, and no new exception added.
17. **The dependency record (CLAUDE.md §10).** The commit that adds `@tanstack/vue-table`
    to `frontend/package.json` also edits `docs/skills-map.md`'s TanStack Table row and
    `03` §8's row (`:1316`); `git show --stat <that commit>` lists all four paths
    (`package.json`, `pnpm-lock.yaml`, `skills-map.md`, `03-rating-engine.md`).
18. **Gate.** Both halves of `CLAUDE.md` §11 pass on the slice tree, run once, in the single
    gate slot (RL-1445 item 1), and `python3 scripts/audit-docs.py` fails nothing but the
    working-id check until the mint.

## Global Constraints

- **Money and decimals:** "Monetary values are integer minor units (pence/cents) or `Decimal`
  throughout the rating path and all persisted rate tables" (`00` FR-10). "`DecimalStr` and
  `Relativity` reject a `float` outright" (`00` FR-21). Cell values cross the wire and the
  frontend as strings.
- **One contract, one way:** "Nobody hand-writes a shape that already exists in
  `model-schema`" (`CLAUDE.md` §2). The frontend types come from
  `frontend/src/api/generated` only.
- **Vue:** "Vue 3 Composition API with `<script setup lang="ts">` only" (`CLAUDE.md` §3).
- **No pandas** in new code (`CLAUDE.md` §3).
- **Spec first:** each new route's FR and §5.1 row land in the same commit as its code
  (`CLAUDE.md` §2). The texts are the decision-maker's, applied byte for byte; any executor
  wording is a stop (RL-1475, after T5).
- **Paging is never a Job** (FR-232; RL-1475 item 2).
- **Typed routes:** "every new or changed JSON route has typed request and 2xx response
  schemas" (FD-1366 *Disposition*).
- **Contention:** one full gate at a time; no shared file with a running slice (RL-1263
  item 4; RL-1445 items 1–2).

## Scope

### Requirement coverage, each id individually

| Id | Limb this slice delivers | Not this slice |
|---|---|---|
| FR-228 | The grid is typed by the declared keys and value (type, unit) | — |
| FR-229 | The manual-edit route requires a change note; the view enforces it before save | — |
| FR-231 | The confirmation diff of a manual edit (absolute and relative change) | The exposure weight column: `SL-1391` (backend), then S5 (view) |
| FR-232 | Cells page through one route for both storages, with no Job; the bound stated under test | The 202 diff path: S5 |
| FR-234 | Save-time validation errors shown on the cell they name | — |
| FR-1186 | No approval or status state shown for a Rate Table Version | — |
| FR-10 | Values stay exact decimal strings end to end | — |
| FR-21 | A float-typed value is refused at the route | — |
| FR-25 | The editor is reachable from the entry by links | — |
| FR-<b> | RL-1475's new FR (`03` §3.3): both reads | — |
| F-W10-3 | The manual-edit route, built (register row `:67`) | — |

**Out of scope, owned elsewhere:** diff-vs-previous and diff-vs-seed shading (FR-230,
FR-231), the bulk-operation dialog (FR-233), CSV/XLSX import and export (FR-235), and F-W10-1
are S5's (`PL-1286` `:307`).

### Write set, by file and symbol, at `137bc817`

| Path | Symbol | Change |
|---|---|---|
| `packages/model-schema/src/model_schema/rating.py` | `RateTable.default_row` (`:718`), `RateTableVersion.default_row` (`:918`), `RateTableVersion.rows` (`:919`) | retyped to `RateTableCell` |
| same | new `RateTableCell`, `RateTableManualEdit` and `ManualEdit`; `RateTableVersion.created_by_edit` and `_one_creation_path` widened (RL-1555) | added |
| `packages/model-schema/src/model_schema/__init__.py` | the new types' exports (RL-1555 item 4) | changed |
| `backend/src/app/api/rate_tables.py` | three new handlers | added |
| `backend/src/app/platform/rate_tables.py` | `_wire_rows` (`:238`) retyped; new `cells_page`, `_cells_in_key_order`, `read_definition`, `manual_edit_preview`, `manual_edit_confirmed` | added beside `import_preview` (`:391`) and `import_confirmed` (`:419`) |
| `packages/pricing-core/src/pricing_core/rate_tables/operations.py` | new `apply_cell_edits`; `validate_rate_table` (`:323`) reused unchanged | added |
| `docs/specs/03-rating-engine.md` | §3.3 (T3), §4.2 (T5), §5.1 (T4 and the DP-S4-1 text on `:901`), §8 (`:1316`) | DM texts |
| `docs/contracts/*` | regenerated | generated |
| `docs/skills-map.md` | the TanStack Table row (`:120`) | verified |
| `frontend/package.json`, `frontend/pnpm-lock.yaml` | `@tanstack/vue-table` `9.2.6` | added |
| `frontend/src/api/rateTables.ts` | new module | added |
| `frontend/src/components/rating/RateTableGrid.vue`, `DecimalCellInput.vue` | new | added |
| `frontend/src/views/RateTableEditorView.vue` | new | added |
| `frontend/src/router/index.ts` | one route | added |
| `frontend/src/views/RatingVersionView.vue` | the pinned-tables links (FR-25) | changed |
| `backend/tests/test_api_rate_tables.py`, `packages/pricing-core/tests/…`, `frontend/src/**/__tests__/…` | the tests above | added |

### Write set, and its contention (`RL-1263`, RL-1445)

- **`SL-1391` (WK-673 S7, lane A, leaf `PL-1419`): serialise.** `PL-1419` names
  `backend/src/app/api/rate_tables.py`, `backend/src/app/platform/rate_tables.py`,
  `packages/pricing-core/src/pricing_core/rate_tables/operations.py`,
  `packages/model-schema/src/model_schema/rating.py` and
  `packages/model-schema/tests/test_rate_tables.py`, all in this slice's write set, and the
  `03` §5.1 diff row. That diff row is RL 9753 T4's anchor. If `SL-1391` merges first and the row no
  longer begins `` | `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against=` | ``, that
  is a stop for the decision-maker, not an executor re-anchor.
- **S2 (SL-1477): serialise, and S4 consumes its output** (DP-S4-3). S2 also edits
  `RatingVersionView.vue`, `router/index.ts` and `03` §5.1.
- **S5: after S4** (`PL-1286` `:307`): it extends the same view and module.
- **`SL-1367` (FD-1335 Part A, draft): file-disjoint.** It edits `score.py` and
  `backend/tests/test_contracts.py`; this slice regenerates `docs/contracts/`, which is
  regenerate-only. Whichever lands second regenerates.
- **WK-1250 S2/S3, WK-673 S3: no shared file** (they hold `compile.py`).
- **`docs/INDEX.md`:** regenerate only.

### Size

`PL-1286` band: 1 / 2 days (likely / worst). It reads toward the worst: two reads, one typed
write route, one shared type retype, the dependency, and one view. DP-S4-4 keeps it as one
slice.

## Decision points

| DP | Question | Options | Recommendation | Blocking |
|---|---|---|---|---|
| **DP-S4-1** | The manual-edit route's request and response types. `03:901` describes them in prose only (RL-1184 E5), and FD-1366's template line needs them typed | (a) **Edits only:** `RateTableManualEdit { base_version: int ≥ 1, edits: list[RateTableCell] (1 or more, each an existing key's full row), change_note: str (non-blank), confirm: bool = false }`, `extra="forbid"`; **200** → `RateTableDiff` (the existing diff type, `rating.py:735`); **201** → `RateTableVersion`. (b) **The full cell set**, as an import file carries it: same envelope with `cells` in place of `edits`. (c) **Address the base in the path**, `POST /rate-tables/{slug}@{version}/edit`, matching the import route's path | **(a).** The editor holds a handful of edits, and the base can exceed the 250 000-cell threshold (FR-232), so (b) would send the whole table back for one changed cell. (a) still "follows the import route" (E5): named base, diff for confirmation, `confirm: true` creates. (c) moves a declared route, which E5 kept | yes: the DM rules it, with the `03` §5.1 text |
| **DP-S4-2** | How FR-234's failures reach the cell ("validation errors shown on the cell", `PL-1286` `:306`). Today `_validate_result` (`operations.py:483`) raises only the first issue, as text | (a) **A typed extension on the 422 problem:** `errors: list[RateTableIssue { code, message, key: RateTableCell \| null }]`, carrying every issue `validate_rate_table` returns, each located by its key columns; (b) the first issue only, parsed from `detail`; (c) the client re-validates bounds and coverage | **(a).** (b) parses prose and shows one error at a time. (c) defines FR-234 twice, which `CLAUDE.md` §2 forbids. RL 9767 (DP-6) rules the same shape of answer for the designer: every located issue, through the server's own checks | yes: the DM rules it, with the text |
| **DP-S4-3** | S4 needs the Rating Version by `slug@version` (RL-1473) and its `pins.rate_tables` (RL-1475 item 3). S2 builds that read. `PL-1371` §3.3 lists S4 as depending on S1 and DP-4 only | (a) **S4 after S2 merges**, and consumes it; (b) S4 builds the read itself if it dispatches first | **(a).** PL-1371's own order is S2 then S4 (§5, week of 10 Oct). (b) would make two slices own one route. This is a sequencing fact; it narrows no scope | no: recorded for the lead's dispatch |
| **DP-S4-4** | Split S4 under DP-4 (a′)? | (a) one slice; (b) a backend read-and-edit slice, then the view | **(a).** The view is the only consumer, and its tests are what prove the routes' shapes serve it. Re-open only if Task 0 measures the band above 2 days | no |

**Ruled 2026-10-05 (RL-1555, working id):** DP-S4-1 (a), its 200 a bare `RateTableDiff` and a 409 for a base that is not the latest; DP-S4-1c (ii), `created_by_edit`; DP-S4-2 (d), every failure a `FieldError` in the problem's existing `errors`; DP-S4-3 and DP-S4-4 as recommended.

## Tasks

### Task 0: Preconditions (no code)

**Files:** none.

- [ ] **Step 1:** `git fetch origin && git log -1 --format='%H %aI' origin/main`. Record it.
- [ ] **Step 2:** confirm the activation needs: RL-1475 and the DP-S4-1/2 ruling are minted
  on main (`git -C <wt> ls-tree --name-only origin/main docs/rulings/ | grep -c <slug>`), and
  SL-1477 is `closed` in `docs/roadmap.md`.
- [ ] **Step 3:** re-find every anchor: each of RL-1475 T3, T4 and T5 is found exactly once
  (`grep -c -F` on the anchor string prints `1`), and the *Write set* symbols resolve
  (`grep -n 'default_row\|rows:' packages/model-schema/src/model_schema/rating.py`).
- [ ] **Step 4 (the stop in RL-1475):** on the test database after `alembic upgrade head`
  and the seed, run
  ```sql
  SELECT count(*) FROM rate_table_versions
  WHERE EXISTS (SELECT 1 FROM jsonb_each(definition->'default_row') e
                WHERE jsonb_typeof(e.value) <> 'string');
  SELECT count(*) FROM rate_table_cells WHERE jsonb_typeof(value) <> 'string';
  ```
  Both must print `0`. Adjust the table and column names to `db/models.py` (`RateTableCellRow`,
  `:2099` at `809a3794`) first. A non-zero count is a **stop**, reported to the lead.
- [ ] **Step 5:** `pnpm view @tanstack/vue-table@9.2.6 license` prints `MIT`; the peer is
  `vue >=3.2`.

### Task 1: `RateTableCell` and the retype (model-schema; RL-1475 T5)

**Files:** Modify `packages/model-schema/src/model_schema/rating.py`; Modify
`docs/specs/03-rating-engine.md` (T5); Test `packages/model-schema/tests/test_rate_tables.py`.

**Interfaces:** Produces `RateTableCell = RootModel[dict[str, str]]`; `RateTable.default_row:
RateTableCell | None`; `RateTableVersion.rows: list[RateTableCell] | None`.

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.req("FR-10")
def test_rate_table_cell_refuses_a_non_string_value() -> None:
    with pytest.raises(ValidationError):
        RateTableCell.model_validate({"area": "A", "relativity": 1.1})
    assert RateTableCell.model_validate({"area": "A", "relativity": "1.1"}).root == {
        "area": "A",
        "relativity": "1.1",
    }


def test_default_row_is_typed_as_a_cell() -> None:
    default_row = RateTable.model_json_schema()["properties"]["default_row"]
    refs = [arm.get("$ref") for arm in default_row["anyOf"]]
    assert "#/$defs/RateTableCell" in refs
```

- [ ] **Step 2:** `uv run pytest packages/model-schema/tests/test_rate_tables.py -k cell -q`.
  Expected: FAIL, `ImportError: cannot import name 'RateTableCell'`.
- [ ] **Step 3: Implement**

```python
class RateTableCell(RootModel[dict[str, str]]):
    """One rate table row in §4.2's form: key columns and the value column, every value a
    string (a key level or a decimal string). RL-1475 item 2; FR-228's columns are data,
    so the keys are open and the value type is closed."""
```

  Retype `RateTable.default_row`, `RateTableVersion.default_row` and `RateTableVersion.rows`
  to it, and `_wire_rows` (`backend/src/app/platform/rate_tables.py:238`) to return
  `list[RateTableCell]`. Apply T5 byte for byte, with FR-<b> and `RL-<this>` replaced by the
  minted ids.
- [ ] **Step 4:** the test passes; `uv run mypy` passes on the package.
- [ ] **Step 5:** commit `feat(model-schema): RateTableCell, and the rate table rows typed as it (RL-<9753>)`.

### Task 2: The two reads (RL-1475 T3, T4; FR-<b>, FR-232)

**Files:** Modify `backend/src/app/platform/rate_tables.py`, `backend/src/app/api/rate_tables.py`,
`docs/specs/03-rating-engine.md` (T3, T4); Test `backend/tests/test_api_rate_tables.py`.

**Interfaces:** Consumes Task 1's `RateTableCell`. Produces `service.read_definition(database,
workspace_id, slug, version) -> RateTable`; `service.cells_page(database, workspace_id, slug,
version, blob_store, *, cursor: int | None, limit: int) -> Page[RateTableCell]`.

- [ ] **Step 1: Write the failing tests** (in `test_api_rate_tables.py`, with its existing
  fixtures for a seeded table and a lowered threshold):

```python
MIXED = [("B", "1.0"), ("a", "1.1"), ("10", "1.2"), ("9", "1.3")]
EXPECTED_ORDER = ["10", "9", "B", "a"]


@pytest.mark.req("FR-232")
async def test_cell_pages_agree_across_storages_in_key_order(client, make_table) -> None:
    rows_ref = await make_table(MIXED, storage="rows")
    parquet_ref = await make_table(MIXED, storage="parquet")
    seen = {}
    for ref in (rows_ref, parquet_ref):
        items, cursor = [], None
        while True:
            q = {"limit": 2} | ({"cursor": cursor} if cursor else {})
            r = await client.get(f"/api/v1/rate-tables/{ref}/cells", params=q)
            assert r.status_code == 200
            items += r.json()["items"]
            cursor = r.json()["next_cursor"]
            if cursor is None:
                break
        seen[ref] = [row["area"] for row in items]
    assert seen[rows_ref] == seen[parquet_ref] == EXPECTED_ORDER
    assert await count_jobs() == 0


@pytest.mark.req("FR-232")
async def test_definition_read_carries_no_cells(client, make_table) -> None:
    ref = await make_table(MIXED, storage="rows")
    body = (await client.get(f"/api/v1/rate-tables/{ref}")).json()
    assert "rows" not in body and "cells" not in body
    RateTable.model_validate(body)
```

  Plus `cell_paging` (malformed cursor → 400, `limit=201` → 422, pages concatenate to the full
  set), `rate_table_isolation` (another workspace → 404 `RATE_TABLE_MISS`), and `cells_bound`.
- [ ] **Step 2:** run `-k "cell_pages or definition_read or cell_paging or rate_table_isolation
  or cells_bound"`. Expected: FAIL with 404/405, the routes absent.
- [ ] **Step 3: Implement**

```python
def _cells_in_key_order(
    cells: Sequence[dict[str, str]], key_names: Sequence[str]
) -> list[dict[str, str]]:
    """RL-1475 item 2: code-point order per key column in declared order, compared as
    strings, for both storages. The one place cells are sorted; never a SQL ORDER BY,
    whose collation could differ from the parquet path's."""
    return sorted(cells, key=lambda row: tuple(row[name] for name in key_names))


async def cells_page(
    database: Database, workspace_id: UUID, slug: str, version: int,
    blob_store: BlobStore, *, cursor: int | None, limit: int,
) -> Page[RateTableCell]:
    """FR-<b>: one page of an immutable version's cells; never a Job (FR-232). The rows
    path loads the version's cells per page, bounded by the FR-232 threshold."""
    async with database.unit_of_work() as session:
        table_row = await _load_table(session, workspace_id, slug)
        version_row = await _load_version(session, table_row.id, version, slug)
        table = RateTable.model_validate(version_row.definition)
        cells = await _load_cells_of(session, version_row, table, blob_store)
    ordered = _cells_in_key_order(cells, [key.name for key in table.keys])
    start = cursor or 0
    chunk = ordered[start : start + limit]
    end = start + len(chunk)
    return Page[RateTableCell](
        items=[RateTableCell(row) for row in chunk],
        next_cursor=encode_cursor(end) if end < len(ordered) else None,
        total_estimate=min(len(ordered), COUNT_CAP),
    )
```

  The handlers, `rating:read`, typed returns:

```python
@router.get(
    "/rate-tables/{slug}@{version}",
    summary="Read one Rate Table Version's definition, without its cells",
    responses=problems(401, 403, 404),
)
async def read_rate_table(
    slug: str, version: int, caller: RatingReadDep, database: DatabaseDep
) -> RateTable:
    return await service.read_definition(database, caller.workspace_id, slug, version)


@router.get(
    "/rate-tables/{slug}@{version}/cells",
    summary="Page through one Rate Table Version's cells, either storage, no Job",
    responses=problems(400, 401, 403, 404, 422),
)
async def read_rate_table_cells(
    slug: str, version: int, caller: RatingReadDep, database: DatabaseDep,
    blob_store: BlobStoreDep, limit: Limit = MAX_LIMIT, cursor: str | None = None,
) -> Page[RateTableCell]:
    return await service.cells_page(
        database, caller.workspace_id, slug, version, blob_store,
        cursor=decode_int_cursor(cursor), limit=limit,
    )
```

  Apply T3 and T4 byte for byte, in the three-cell or four-cell form RL-1475 names for the
  §5.1 header found at Task 0.
- [ ] **Step 4:** the five tests pass.
- [ ] **Step 5:** `uv run python scripts/generate-contracts.py`; commit
  `feat(rating): read a rate table version's definition and its cell pages (FR-<b>)` with
  the spec rows and `docs/contracts/` in the same commit.

### Task 3: The manual-edit route (F-W10-3; DP-S4-1, DP-S4-2)

**Files:** Modify `packages/pricing-core/src/pricing_core/rate_tables/operations.py`,
`packages/model-schema/src/model_schema/rating.py`, `backend/src/app/platform/rate_tables.py`,
`backend/src/app/api/rate_tables.py`, `docs/specs/03-rating-engine.md` (the DM's texts);
Test `packages/pricing-core/tests/test_rate_table_operations.py`,
`backend/tests/test_api_rate_tables.py`.

**Interfaces:** Consumes the DP-S4-1 types, written here under the recommended option (a)
names; if the DM rules otherwise, the ruled names replace these before Step 1. Produces
`apply_cell_edits(table: RateTableVersion, edits: Sequence[RateTableCell]) -> list[CellRow]`.

- [ ] **Step 1: Write the failing tests**

```python
@pytest.mark.req("FR-234")
def test_apply_cell_edits_refuses_an_unknown_key(table_ab) -> None:
    with pytest.raises(ValueError, match="^UNKNOWN_KEY: "):
        apply_cell_edits(table_ab, [RateTableCell({"area": "Z", "relativity": "1.0"})])


@pytest.mark.req("FR-234")
def test_apply_cell_edits_refuses_a_duplicated_edit(table_ab) -> None:
    edit = RateTableCell({"area": "A", "relativity": "1.5"})
    with pytest.raises(ValueError, match="^DUPLICATE_KEY: "):
        apply_cell_edits(table_ab, [edit, edit])


@pytest.mark.req("FR-229")
async def test_manual_edit_preview_creates_nothing(client, table_ref) -> None:
    before = await count_versions(table_ref.slug)
    r = await client.post(
        f"/api/v1/rate-tables/{table_ref.slug}/versions",
        json={"base_version": table_ref.version, "change_note": "area A +5%",
              "edits": [{"area": "A", "relativity": "1.05"}]},
    )
    assert r.status_code == 200
    RateTableDiff.model_validate(r.json())
    assert await count_versions(table_ref.slug) == before


@pytest.mark.req("FR-234")
async def test_manual_edit_out_of_bounds_names_the_cell(client, table_ref) -> None:
    r = await client.post(
        f"/api/v1/rate-tables/{table_ref.slug}/versions",
        json={"base_version": table_ref.version, "change_note": "x", "confirm": True,
              "edits": [{"area": "A", "relativity": "-1"}]},
    )
    assert r.status_code == 422
    assert [(e["field"], e["code"]) for e in r.json()["errors"]] == [("edits.0.relativity", "OUT_OF_BOUNDS")]
```

  Plus `manual_edit_confirm` (201, `base + 1`, cells equal base with the edit, a second
  confirm → 409) and the rest of `manual_edit_refusals` (blank note, float value, unknown
  field).
- [ ] **Step 2:** run them. Expected: FAIL, `apply_cell_edits` missing and the route 405.
- [ ] **Step 3: Implement.** `apply_cell_edits` indexes the base rows by key tuple
  (`_index_rows`, `operations.py:376`), refuses an edit whose key is absent (`UNKNOWN_KEY`)
  or repeated (`DUPLICATE_KEY`), replaces the value column, and returns the new rows. The
  service mirrors `import_preview` / `import_confirmed`: preview returns `diff_vs_previous`
  of the would-be version, with nothing persisted; confirm builds the `RateTableVersion` at
  `base + 1` with the body's `change_note` and `seeded_from` inherited, calls
  `_guard_seed_lineage`, resolves the threshold, and calls `_persist_new_version`. FR-234
  runs through `validate_rate_table` (`:323`); every issue becomes one `FieldError` (RL-1555 item 3),
  `field` `edits.<i>.<value name>`; `UNKNOWN_KEY` and `DUPLICATE_KEY` are collected the same way under `VALIDATION_FAILED` and never reach `_map_operation_error`, which would raise a 500 (`UNKNOWN_KEY` is not in `_KNOWN_CODES`); the confirmed version sets `created_by_edit`. The handler is typed `-> RateTableDiff` and sets 201 on confirm with a
  `RateTableVersion` body, declared in `responses=`. Apply the DM's `03` texts byte for byte.
- [ ] **Step 4:** the tests pass; `generate-contracts.py --check` exits 0 after regeneration.
- [ ] **Step 5:** commit `feat(rating): the manual-edit route, preview then confirm (FR-229, FR-234; F-W10-3)`.
  Register row F-W10-3's discharge is the auditor's, at close.

### Task 4: The dependency and its records (CLAUDE.md §10)

**Files:** Modify `frontend/package.json`, `frontend/pnpm-lock.yaml`, `docs/skills-map.md`
(`:120`), `docs/specs/03-rating-engine.md` (`:1316`).

- [ ] **Step 1:** `pnpm --dir frontend add @tanstack/vue-table@9.2.6 --save-exact`.
- [ ] **Step 2:** mark the skills-map row verified, in the Vue Flow row's form: `TanStack
  Table ✔` and, in its notes, "**Verified 2026-10-<dd> at `<tree>`:** v9 (`9.2.6`, MIT, peer
  `vue >=3.2`); `useTable({ features: tableFeatures({}), columns, data })`, core-only;
  paging is the server's cursor, not the pagination feature; `data` passed as a ref, never
  `.value`." Extend `03` §8's row with the pinned version.
- [ ] **Step 3:** commit all four paths in one commit:
  `build(frontend): @tanstack/vue-table 9.2.6 for the rate table editor (03 §8, skills-map)`.

### Task 5: `rateTables.ts`

**Files:** Create `frontend/src/api/rateTables.ts`; Test
`frontend/src/api/__tests__/rateTables.test.ts`.

**Interfaces:** Produces `getRateTable(ref: string): Promise<RateTable>`;
`getCellPage(ref: string, cursor?: string): Promise<RateTableCellPage>`;
`previewEdit(slug: string, body: RateTableManualEdit): Promise<RateTableDiff>`;
`confirmEdit(slug: string, body: RateTableManualEdit): Promise<RateTableVersion>`. Every type
is `components["schemas"][…]` from `./generated`.

- [ ] **Step 1: Write the failing test**

```ts
describe("rateTables (FR-232)", () => {
  it("requests one cell page with the server cursor", async () => {
    const calls = mockRequest({ items: [], next_cursor: null, total_estimate: 0 });
    await getCellPage("area@3", "MTA");
    expect(calls).toEqual(["/api/v1/rate-tables/area@3/cells?cursor=MTA"]);
  });
});
```

- [ ] **Step 2:** `pnpm --dir frontend test -- rateTables`. Expected: FAIL, module missing.
- [ ] **Step 3: Implement**

```ts
import { request } from "./client";
import type { components } from "./generated";

export type RateTable = components["schemas"]["RateTable"];
export type RateTableCell = components["schemas"]["RateTableCell"];
export type RateTableCellPage = components["schemas"]["Page_RateTableCell_"];
export type RateTableDiff = components["schemas"]["RateTableDiff"];
export type RateTableVersion = components["schemas"]["RateTableVersion"];
export type RateTableManualEdit = components["schemas"]["RateTableManualEdit"];

export function getRateTable(ref: string): Promise<RateTable> {
  return request<RateTable>(`/api/v1/rate-tables/${ref}`);
}

export function getCellPage(ref: string, cursor?: string): Promise<RateTableCellPage> {
  const query = cursor ? `?cursor=${encodeURIComponent(cursor)}` : "";
  return request<RateTableCellPage>(`/api/v1/rate-tables/${ref}/cells${query}`);
}

export function previewEdit(slug: string, body: RateTableManualEdit): Promise<RateTableDiff> {
  return request<RateTableDiff>(`/api/v1/rate-tables/${slug}/versions`, {
    method: "POST",
    body: { ...body, confirm: false },
  });
}

export function confirmEdit(slug: string, body: RateTableManualEdit): Promise<RateTableVersion> {
  return request<RateTableVersion>(`/api/v1/rate-tables/${slug}/versions`, {
    method: "POST",
    body: { ...body, confirm: true },
  });
}
```

  Match `request`'s actual signature in `frontend/src/api/client.ts` at Task 0.
- [ ] **Step 4:** passes. **Step 5:** commit `feat(frontend): rateTables API module over the generated client`.

### Task 6: `DecimalCellInput.vue` and `RateTableGrid.vue` (FR-10, FR-21, FR-228)

**Files:** Create `frontend/src/components/rating/DecimalCellInput.vue`,
`frontend/src/components/rating/RateTableGrid.vue`; Test both under
`frontend/src/components/rating/__tests__/`.

**Interfaces:** `DecimalCellInput` props `{ modelValue: string; invalid?: string }`, emits
`update:modelValue(string)`. `RateTableGrid` props `{ table: RateTable; rows: RateTableCell[];
edits: Record<string, string>; errors: Record<string, string> }`, emits `edit(key: string,
value: string)`; `key` is the row's key values joined by `\u001f`.

- [ ] **Step 1: Write the failing tests**

```ts
describe("DecimalCellInput (FR-10, FR-21)", () => {
  it("emits exactly the string typed", async () => {
    const { emitted } = render(DecimalCellInput, { props: { modelValue: "1.10" } });
    await userEvent.clear(screen.getByRole("textbox"));
    await userEvent.type(screen.getByRole("textbox"), "1.100000000000000001");
    expect(emitted()["update:modelValue"].at(-1)).toEqual(["1.100000000000000001"]);
  });
  it("flags a non-decimal entry", async () => {
    render(DecimalCellInput, { props: { modelValue: "" } });
    await userEvent.type(screen.getByRole("textbox"), "1.2.3");
    expect(screen.getByRole("textbox")).toHaveAttribute("aria-invalid", "true");
  });
});

describe("RateTableGrid (FR-228)", () => {
  it("orders columns as declared, value last, unit in the header", () => {
    render(RateTableGrid, { props: { table: AREA_BY_BAND, rows: [], edits: {}, errors: {} } });
    expect(screen.getAllByRole("columnheader").map((h) => h.textContent)).toEqual([
      "area", "band", "relativity (relativity)",
    ]);
  });
});
```

- [ ] **Step 2:** run. Expected: FAIL, components missing.
- [ ] **Step 3: Implement.** `DecimalCellInput` is a text input with
  `inputmode="decimal"`, `/^-?\d+(\.\d+)?$/` as a syntax check only (bounds stay the
  server's, FR-234), `aria-invalid` and `aria-describedby` for the server's error.
  `RateTableGrid`:

```vue
<script setup lang="ts">
import { computed } from "vue";
import { FlexRender, tableFeatures, useTable } from "@tanstack/vue-table";
import type { RateTable, RateTableCell } from "@/api/rateTables";
import DecimalCellInput from "./DecimalCellInput.vue";

const props = defineProps<{
  table: RateTable;
  rows: RateTableCell[];
  edits: Record<string, string>;
  errors: Record<string, string>;
}>();
const emit = defineEmits<{ edit: [key: string, value: string] }>();

const features = tableFeatures({});
const keyNames = computed(() => props.table.keys.map((k) => k.name));
const rowKey = (row: RateTableCell) => keyNames.value.map((n) => row[n]).join("\u001f");
const columns = computed(() => [
  ...keyNames.value.map((name) => ({ accessorKey: name, header: name })),
  {
    id: "value",
    header: `${props.table.value.name} (${props.table.value.type})`,
    accessorFn: (row: RateTableCell) => row[props.table.value.name],
  },
]);
const data = computed(() => props.rows);
const grid = useTable({ features, columns, data });
</script>
```

  The template renders `<table>` with `<th scope="col">` headers, key cells as
  `<th scope="row">` text, and the value cell as `DecimalCellInput` bound to
  `edits[rowKey(row)] ?? row[value]`, with `errors[rowKey(row)]` as its `invalid`.
  Confirm the value-type field name (`type` or `unit`) on the generated `RateTableValue`
  at Task 0, and render the unit FR-228 names.
- [ ] **Step 4:** passes. **Step 5:** commit `feat(frontend): the typed rate table grid with exact decimal cells`.

### Task 7: `RateTableEditorView.vue`, the route and the FR-25 link

**Files:** Create `frontend/src/views/RateTableEditorView.vue`; Modify
`frontend/src/router/index.ts`, `frontend/src/views/RatingVersionView.vue`; Test
`frontend/src/views/__tests__/RateTableEditorView.test.ts`,
`frontend/src/views/__tests__/RatingVersionView.test.ts`,
`frontend/src/router/__tests__/reachability.test.ts`.

**Interfaces:** Consumes Task 5 and Task 6, and S2's `getRatingVersionBySlug(slug, version)`
(the RL-1473 read; take its name from S2's merged code at Task 0).

- [ ] **Step 1: Write the failing tests:** the route resolves `:tableSlug` through the
  Rating Version's `pins.rate_tables` (no list call); Next/Previous follow `next_cursor`
  and a held cursor stack; save is disabled with a blank change note; save calls
  `previewEdit` and renders the diff; confirm calls `confirmEdit` and loads the new version;
  a 422 with `errors` marks each named cell; no status or approval text renders (FR-1186);
  `RatingVersionView` renders one link per pinned table; reachability passes for
  `/rating/:slug/v/:version/tables/:tableSlug`.
- [ ] **Step 2:** run. Expected: FAIL, the view and route missing.
- [ ] **Step 3: Implement** the view in `<script setup lang="ts">`: read the Rating
  Version, find the pin whose slug is `:tableSlug` (a 404 state if none), load the
  definition and the first cell page, hold `edits` in a `ref<Record<string, string>>`,
  hold `cursors` as a stack for Previous, and post `{ base_version, edits, change_note }`.
  Add the route with the same lazy `component: () => import(…)` form the router uses, and
  the pinned-table links on `RatingVersionView`.
- [ ] **Step 4:** passes, including `reachability`. **Step 5:** commit
  `feat(frontend): the rate table editor view, grid and manual edit (FR-228, FR-229, FR-234, FR-1186)`.

### Task 8: The gate and the ledger

- [ ] **Step 1:** check that no gate is held (`flock -n` on the gate slot, per RL-1445
  item 1), then run both halves of `CLAUDE.md` §11 once, through `gate-runner`.
- [ ] **Step 2:** `python3 scripts/audit-docs.py` and `uv run python scripts/req-coverage.py`.
- [ ] **Step 3:** the slice ledger records every acceptance item with its red-then-green
  evidence, Task 0's query output, and the merge-tree rc against main.

## Hand-off

The executor reports to the lead the branch range `origin/main...<branch>`, the gate table,
and the ledger. The slice auditor checks the acceptance list against that range
(`CLAUDE.md` §13). F-W10-3's register discharge and SL-1559's close are the auditor's and the
lead's.

## Self-review

1. **Spec coverage.** Every row of *Requirement coverage* maps to a task: FR-228 → 6;
   FR-229 → 3, 7; FR-231 (confirmation limb) → 3, 7; FR-232 → 2; FR-234 → 3, 7; FR-1186 → 7;
   FR-10 and FR-21 → 1, 3, 6; FR-25 → 7; FR-<b> → 2; F-W10-3 → 3. `PL-1286` S4's row
   (`:306`) names each of these and nothing else.
2. **Placeholders.** The DP-S4-1 type names are the recommended option's and are marked as
   such. If the DM rules otherwise, they are replaced before Task 3 starts. FR-<b> and
   `RL-<this>` are RL 9753's own placeholders, filled at its mint.
3. **Type consistency.** `RateTableCell`, `RateTableManualEdit`, `RateTableDiff` and
   `RateTableVersion` are the same names in Tasks 1, 3, 5, 6 and 7. `Page_RateTableCell_`
   is the generated name RL-1475 gives.
4. **Dependencies named both ways (RL-1445 item 2(b)).** S4 consumes S2's Rating Version
   read; S2 does not consume S4. S4 consumes nothing of `SL-1391`, and `SL-1391` consumes
   nothing of S4, but they share files, so they serialise under item 2(a).
