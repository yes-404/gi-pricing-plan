---
id: LG-9459
family: ledger
title: WK-675 slice SL-1559 — Editor I, the rate table grid and manual edit (PL-1558), task ledger
status: active
created: 2026-10-10
owner: executor
tree: 26f93be0727d7b028d9b73143d41b05b472e57b3
phase: P2
work: WK-675
slice: SL-1559
plans: [PL-1558]
corrected_by: []
relates: [PL-1558, RL-1555, RL-1475, RL-1184, RL-1445, RL-1263, FD-1366, SL-1477, SL-1391, WK-675]
---

# LG-9459 — WK-675 slice SL-1559: Editor I, the rate table grid and manual edit

*(LG-9459 is a working id reserved by the lead; the lead mints it. Authored ahead of the GO at the lead's order of 2026-10-10 (brief `brief-executor-wk675s4-authoring-2026-10-10.md`, local).)*

**GO:** not yet given. This slice is authored, not gated: no PR and no gate until the GO. Nothing merges without its GO, its full gate and the maintainer's MERGE-ACK.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

Executed from `PL-1558` (WK-675 Slice 4, leaf plan) by `executor-675s4` (sonnet). Branch
`sl-1559-wk675-s4`, worktree `.claude/worktrees/sl-1559`, cut from `origin/main`
`26f93be0727d7b028d9b73143d41b05b472e57b3` (#1255, the D3 mint; author date
`2026-10-10T03:59:50+01:00`). Row: `SL-1559` in `docs/roadmap.md`; plan `PL-1558`; rulings
`RL-1555` (DP-S4-1, DP-S4-1c, DP-S4-2) and `RL-1475` (the reads, T3 to T5). Requirements:
FR-228, FR-229, FR-231 (confirmation limb), FR-232, FR-234, FR-1186, FR-10, FR-21, FR-25, the FR
that RL-1475 T3 creates (FR-<b>), and register row F-W10-3. Not this slice: the exposure weight
column, diff shading, bulk operations, import and export (S5).

`PL-1558`'s `status:` is set `active` in this ledger's first commit (the standing ruling of
`to-lead.md` "2026-10-09 13:29:49 BST", item 3); its body is not edited. The `SL-1559` row stays
`draft` until the lead's GO.

### Task list

| Task | Plan step | Acceptance | Status |
|---|---|---|---|
| 0 | preconditions | Acceptance 10 (stored-data query) | steps 1, 2, 3, 5 done; step 4 OWED (no database on the box) |
| 1 | `RateTableCell`, retype, `ManualEdit`, `RateTableManualEdit`, `created_by_edit` | Acceptance 7 (provenance limb, model level) | done, commit 2 |
| 2 | the two reads, RL-1475 T3 and T4 | 1–5 | authored, commit 3; the 5 DB tests are UNRUN (OWED at the gate) |
| 3 | the manual-edit route, RL-1555 T1 to T4, and `created_by_edit` persisted | 6–8 | authored, commit 4; pure level red→green; the DB tests are UNRUN (OWED at the gate) |
| 4 | the dependency and its records | 17 | done, commit 5 (`e92ce26d`) |
| 5 | `rateTables.ts` | — | done, commit 6 |
| 6 | `DecimalCellInput.vue`, `RateTableGrid.vue` | 11, 12 | done, commit 8 |
| 7 | `RateTableEditorView.vue`, route, FR-25 link | 11, 13–16 | done, commit 11 |
| 8 | gate and ledger | 18 | waits for the GO and the gate slot |

### Gate

Not run.

### Audit

Not yet. The auditor writes it.

### Build log

#### Task 0 — preconditions (2026-10-10, from 04:00 BST)

**Dispatch tree.** `26f93be0727d7b028d9b73143d41b05b472e57b3`, `2026-10-10T03:59:50+01:00`.

**Step 2, the activation needs.** (1) RL-1475 is on main
(`docs/rulings/RL-01475-…`). (2) RL-1555 is on main (`docs/rulings/RL-01555-…`, #1255). (3)
`SL-1477` is `status: closed` in `docs/roadmap.md`. (4) `SL-1391` is `status: closed`, so not
running. (5) this Task 0. (6) the GO: not given, merge-only.

**Step 3, the spec find strings** (`grep -cF -- '<string>' docs/specs/03-rating-engine.md`),
each count 1:

| Text | Find string | Count |
|---|---|---|
| RL-1555 T1 | `Owner: WK-675's editor slice. \|` | 1 |
| RL-1555 T2 | `  "created_by_import": null,` | 1 |
| RL-1555 T3 | ``hand, so both are `null`.`` | 1 |
| RL-1555 T4 (a) | ``> the resolved baseline — `BulkOperation.applied_to` or `created_by_import.applied_to` —`` | 1 |
| RL-1555 T4 (b) | ``> `created_by_import` remain mutually exclusive.`` | 1 |
| RL-1475 T4 | `` \| `GET` \| `/api/v1/rate-tables/{slug}@{version}/diff?against= `` | 1 |
| RL-1475 T5 anchor | ``### 4.3 `RatingVersion` `` | 1 |
| RL-1475 T3 anchor | `### 3.4 Rating versions and bundles` (after the `**FR-1186**` row, count 1) | 1 |

**Differences from the plan.** The plan's line hints are `137bc817`'s. At this tree: `03` §5.1's
header is still `| Method | Path | Purpose |` (line 931), so the three-cell row forms apply. The
manual-edit row is line 940. The diff row is line 943 and already begins
``| `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against=&portfolio=` |`` (`SL-1391`
merged), and the `…/diff/cells` row (line 944) sits after it; RL-1475 T4's re-set anchor still
counts 1, as the amendment of 17:29 BST says.
In `packages/model-schema/src/model_schema/rating.py`: `RateTable` is line 800 and its
`default_row` line 816; `RateTableVersion` is line 1028, `default_row` line 1047, `rows` line
1048, `created_by_import` line 1053, `_one_creation_path` line 1071; `RateTableDiff` line 833;
`ImportVerdict` line 971. In `backend/src/app/platform/rate_tables.py`: `_wire_rows` line 263,
`_load_table` 268, `import_preview` 861, `import_confirmed` 889, `_load_version` 998,
`_load_cells` 1020, `_load_cells_of` 1069, `_persist_new_version` 1140, `_guard_seed_lineage` 1113,
`_map_operation_error` 109. `RateTableCellRow` is `backend/src/app/db/models.py:2099`. The
frontend `request` is `frontend/src/api/client.ts:50`, `request<T>(path, options: RequestOptions)`.
S2's read of a Rating Version by its address is `getRatingVersionByRef(slug, version)` in
`frontend/src/api/ratingVersions.ts:16` (Task 7 consumes it under that name).

**Step 4 (the stop in RL-1475): OWED.** No Postgres on the box (`pg_isready` is not installed and
`GIP_TEST_DATABASE_URL` is unset), so the two `jsonb_typeof` counts cannot be run here. They are
run at the gate, on the test database after `alembic upgrade head` and the seed, with the table
names `rate_table_versions` and `RateTableCellRow`'s table. A non-zero count is a stop for the
lead.

**Step 5.** `pnpm view @tanstack/vue-table@9.2.6 license peerDependencies` prints `license =
'MIT'` and `peerDependencies = {"vue":">=3.2"}`.

**Open for the lead.** The FR id for RL-1475 T3 (`FR-<b>`) is minted by the lead, who is the sole
allocator of ids; Task 2 needs it before its spec commit.

#### Task 1 — `RateTableCell`, the retype, `ManualEdit`, `created_by_edit` (2026-10-10, 03:07–03:12 BST)

**Red first** (`nice -n 19 flock -w 300 /tmp/slots/small-test -c "timeout 150 uv run --directory <wt> pytest -q
-p no:xdist packages/model-schema/tests/test_rate_tables.py -k 'cell or ManualEdit' -x"`, load 5.41 at that run, above the
4.0 line; later runs waited for load <= 4.0): rc 1, `ImportError: cannot import name 'RateTableCell' from
'model_schema.rating'` at `test_rate_table_cell_refuses_a_non_string_value`. (`-x` stopped the run there; the other new tests
import `ManualEdit` and `RateTableManualEdit`, absent for the same cause.)

**Green:** `pytest -q -p no:xdist packages/model-schema/tests/test_rate_tables.py` → `61 passed`. New tests: the cell refuses
a float and an int value (FR-10); `default_row` (both models) and `rows` carry `#/$defs/RateTableCell` in their JSON
Schema; `RateTableManualEdit` parses and defaults `confirm` false, and refuses a blank note, empty edits, `base_version` 0,
a float value, an unknown field; `ManualEdit` needs `edited_cells >= 1` and forbids extras; a version carries
`created_by_edit` and a seeded one none; `created_by_edit` with `created_by_import` or with `created_by_operation` is
refused.

**Ripple of the retype** (the plan's write set names `rating.py`, `__init__.py` and `_wire_rows`; these follow from the
retype and are listed here): `pricing_core/rate_tables/operations.py` `_rows_of`, `_new_version` (`model_copy` skips
validation, so it now wraps each row in `RateTableCell`), and a `_default_row_of` helper for the two `default_row`
arguments to `validate_rate_table`; `backend/src/app/platform/rate_tables.py` `_wire_rows` and the `cast` in
`_persist_new_version`; tests `test_rate_table_bulk_ops.py` (a `_cells` helper for 8 row comparisons) and
`backend/tests/test_rate_tables_service.py` (two `row.root[...]` reads; DB test, UNRUN). Green: 109 passed over
`test_rate_table_bulk_ops.py`, `test_rate_table_operations.py`, `test_rating_pin_membership.py`,
`test_rating_runtime.py`; `ruff check packages backend/src` clean; `mypy` over the three changed source files clean.

**Spec:** RL-1475 T5 applied byte for byte before `### 4.3` with `<date>` = 2026-10-10, `RL-<this>` = `RL-1475` and
`FR-<b>` = the working id `FR 9940` (the lead's ruling of this date). `scripts/generate-contracts.py` run: `generated.json`
and `rate-table-version.schema.json` changed. `RateTableManualEdit` reaches the contract only when Task 3's route uses it.

**Observation, not acted on.** T5's list of what `RateTable` lacks does not name `created_by_edit`; the text is the
decision-maker's, byte for byte, and `created_by_edit` is RL-1555's addition. Reported to the lead.

#### Task 2 — the two reads (2026-10-10)

**Authored, red not shown.** The five test groups (`definition_read`, `cell_pages`, `cell_paging`, `rate_table_isolation`,
`cells_bound`; appended to `backend/tests/test_api_rate_tables.py`) need Postgres and the blob store, which the box lacks, so
no red/green is possible here: **OWED at the gate**, red first by the plan's causes (the routes absent → 404/405; leave a
path unsorted → the sequences differ). `cell_pages` writes the expected order out: `"10"`, `"9"`, `"B"`, `"a"`. They carry
`@pytest.mark.req("FR-9940")` / `("FR-232")`.

**Code.** `platform/rate_tables.py`: `read_definition`, `_cells_in_key_order` (the one sort, Python, both storages) and
`cells_page` (a malformed cursor → 400 through `decode_int_cursor`; a cursor outside `0 < start < total` → the existing
`_bad_cursor`, as `diff_cells_page` does). `api/rate_tables.py`: `read_rate_table` (`-> RateTable`) and
`read_rate_table_cells` (`-> Page[RateTableCell]`, `limit` as the diff-cells route declares it), both `rating:read`. The plan's
sketch decoded the cursor in the handler and took `limit: Limit = MAX_LIMIT`; I followed the diff-cells route (decode in the
service, `Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT`) so the two cursor routes read alike.

**Spec.** RL-1475 T3 (the FR row, id cell `FR-9940`, prose `FR 9940`) and T4 (two §5.1 rows, three-cell form, before the diff
row) applied with `<date>` = 2026-10-10 and `RL-<this>` = `RL-1475`. **Contract** regenerated: the definition read's 200 is a
`$ref` to `RateTable`, the cells read's to `Page_RateTableCell_`, and `RateTable.default_row` is `anyOf [RateTableCell, null]`.
`ruff check backend packages` clean; `mypy` over the two route/service files clean.

#### Task 3 — the manual-edit route and the persisted `created_by_edit` (2026-10-10)

**Write-set delta, on the maintainer's rulings "2026-10-10 04:11:58" (A: persist `created_by_edit` as a nullable JSONB
column, one Alembic migration, existing rows NULL, a red-first read-back test) and "04:12:41" (condition 5 settled as (i):
RL-1555's `ManualEdit` shape `{applied_to, edited_cells}` stands; the base reference is stored on the row, not null for an
edit-created version, pointing at an immutable version; the red-first test also diffs the stored version against its base),
relayed by the lead.** Paths added beyond PL-1558's write set: `backend/src/app/db/models.py` (the column on
`RateTableVersionRow`) and `backend/migrations/versions/d4e81b7a2c95_rate_table_version_created_by_edit.py` (one
migration, `down_revision` `f3a7c1d9e2b4`, main's head at `26f93be0`; `alembic heads` prints `d4e81b7a2c95 (head)`, one
head). **At the merge turn it re-chains on `b8d2f4a6c0e1`**, which WK-673 S4 (#1256) adds on `f3a7c1d9e2b4` and merges
first. Upgrade and downgrade both run in the gate's database step: OWED.

**Pure level, red then green.** `TestApplyCellEdits` (6 tests, `test_rate_table_bulk_ops.py`): red, rc 2,
`ImportError: cannot import name 'apply_cell_edits'` (load 1.65, below the 4.0 line); green after the code, `45 passed`
for the file, `106 passed` with `test_rate_tables.py`.

**Code.** `pricing_core/rate_tables/operations.py`: `apply_cell_edits(table, edits) -> EditResult` with `EditIssue`
(index, code, message); it collects every failure instead of raising (`EDIT_COLUMNS`, `UNKNOWN_KEY`, `DUPLICATE_KEY`, and
FR-234's `NULL_VALUE`/`OUT_OF_BOUNDS` from the shared `_value_issue`, so the value check is defined once). The new
messages name the constraint and never a value. `platform/rate_tables.py`: `_edit_failure` (one `FieldError` per failure,
`field` `edits.<i>.<value name>`, `code` its own), `_edit_derived`, `manual_edit_preview` (a bare `RateTableDiff` from
`diff_vs_previous`, nothing created) and `manual_edit_confirmed` (`_guard_seed_lineage`, threshold, `_persist_new_version`,
which now writes and returns `created_by_edit`). `api/rate_tables.py`: `POST /rate-tables/{slug}/versions`, `rating:write`,
200 `RateTableDiff` / 201 `RateTableVersion` declared in `responses=`, set 201 on confirm. Contract regenerated: the
route's request body and the two responses are `$ref`s to the typed shapes; `problem.py` and `errors.py` are unchanged.

**Spec.** RL-1555 T1 to T4 applied byte for byte (`<date>` 2026-10-10, `RL-<this>` `RL-1555`); the permission column has
not landed, so T1 keeps "Requires `rating:write`."

**DB tests authored, UNRUN (OWED at the gate):** `manual_edit_preview` (bare diff, row count unchanged),
`manual_edit_confirm` (201, `base + 1`, change note, cells, a second confirm 409, **`created_by_edit` read back from the
stored row equals what was submitted, and version 1 stores NULL**), the diff test (**the stored version against its base
differs by exactly the edited cells, the count is `edited_cells`, each old → new pair is the submitted one**), the
refusal cases (blank and whitespace note, empty edits, unknown field, float value, unknown key, duplicated key, wrong
columns), out-of-bounds values each named, and isolation on the edit route. Red by cause at the parent: no column and no
route (405).

**Deviations and questions for the lead.**
1. `apply_cell_edits` returns `EditResult` rather than the plan's `list[CellRow]` that raises, because RL-1555 item 3
   needs every failure located by edit index.
2. **Spec and code disagree on the unknown-table code.** RL-1555 T1 says **404 `NOT_FOUND`** for an unknown table or
   `base_version`; the loaders (`_load_table`, `_load_version`), RL-1475's reads and PL-1558's Acceptance 4 all answer
   404 `RATE_TABLE_MISS`. The route answers `RATE_TABLE_MISS` (as Acceptance 4 requires); T1 is applied as the
   decision-maker wrote it. Reported to the lead for the decision-maker.
3. The problem's own `code` on a 422 is `RATE_TABLE_INCOMPLETE` when every failure is an FR-234 value issue and
   `VALIDATION_FAILED` otherwise (T1's wording, "under code", names no mixed case); each field error carries its own code.
4. The lead's load rule (wait for load1 <= 4.0 before every small test) was not met at the start of Task 1's red run
   (load 5.41); the runs since waited.

#### Tasks 4 and 5 — the dependency; `rateTables.ts` (2026-10-10)

**Task 4** (`e92ce26d`): `@tanstack/vue-table` `9.2.6` added with `--save-exact`; its `index.d.ts` was read after install:
`useTable` takes `{ features, columns, data }` with `data` a `MaybeRef`, and the package re-exports `tableFeatures` and
`FlexRender` from table-core. `git show --stat` lists `frontend/package.json`, `frontend/pnpm-lock.yaml`,
`docs/skills-map.md` (the row marked verified) and `docs/specs/03-rating-engine.md` (§8's row) (Acceptance 17), plus
`backend/tests/test_api_rate_tables.py`: the S4 404 tests now read one constant, `_UNKNOWN_TABLE_CODE`, to flip when the
maintainer rules `NOT_FOUND` against `RATE_TABLE_MISS` (the lead's order, after the 3372f5ce report).

**Task 5.** Red: `vitest run src/api/__tests__/rateTables.test.ts`, the module absent (a transform failure, no tests run);
load 3.99. Green: `4 passed`. `frontend/src/api/rateTables.ts` follows the real client: `request` already prefixes
`/api/v1` and takes `query`, the generated types come from `./generated/schema`, and the edit body from
`./generated/schema.requests` (the permissive set, as `ratingAlgorithms.ts` does) minus `confirm`. `pnpm generate:api` was
run; `generated/` is VCS-ignored.

#### Plan delta, 2026-10-10 — the unknown-table code (the maintainer's ruling "04:19:42", relayed by the lead)

**Ruling: the spec governs.** PL-1558 Acceptance 4 says the manual-edit route answers 404 `RATE_TABLE_MISS` for another
workspace's table. RL-1555 T1 (03 §5.1) says **404 `NOT_FOUND`**. The ruling corrects the acceptance as a delta here (the
plan body is not edited): **on the manual-edit route an unknown table, version or `base_version` is 404 `NOT_FOUND`.**
Implemented at the route layer only: `spec_not_found()` in `api/rate_tables.py` maps the loaders' `RATE_TABLE_MISS` and
wraps the manual-edit handler's two service calls; the shared loader (`rate_tables.py` `_load_table`/`_load_version`) is
unchanged, because `RATE_TABLE_MISS` stays right on the scoring path.
**Scope as I read the spec:** the two **reads** keep `RATE_TABLE_MISS`, because RL-1475 T3 and T4 (applied byte for byte)
and RL-1475 Acceptance 5 say so; the lead's message said "your routes", and the spec text is explicit per route. If the
maintainer meant the reads too, the change is the same wrapper on two handlers, plus the two constants below.
**Red first:** `backend/tests/test_rate_table_route_codes.py` (DB-free): collection error, `ImportError: cannot import name
'spec_not_found'` (load 2.78); green `2 passed`. The DB route tests read `_READ_MISS_CODE` and `_EDIT_MISS_CODE`; the edit
isolation test asserts `NOT_FOUND` (DB, OWED at the gate).
**The existing diff routes (`:943`/`:944`)** say `NOT_FOUND` in the spec while their loader answers `RATE_TABLE_MISS`: the
drift is the lead's finding. Not fixed here: the fix would also change the existing diff tests that assert
`RATE_TABLE_MISS`, so it is not a ~20-line, test-neutral change.

#### Task 6 — `DecimalCellInput.vue`, `RateTableGrid.vue` (2026-10-10)

**Red:** `vitest run src/components/rating`, both test files failing to load, the components absent (load 1.36). **Green:**
`2 files, 10 tests passed`. Acceptance 12's `git grep -n -E 'Number\(|parseFloat|parseInt' -- frontend/src/components/rating/`
prints nothing (rc 1).
**Deviations from the plan's sketch.** (1) The header reads `name (unit)`, the unit of `RateTableValue` (Acceptance 11 and
FR-228 say "unit"; the sketch's test expected the type, `relativity (relativity)`). (2) `DecimalCellInput` gains two optional
props, `integer` (money in minor units and counts take whole numbers only, FR-10) and `label` (an accessible name per cell);
the grid sets both. (3) The server's error is shown as text beside the input and tied by `aria-describedby`, so it does not
rely on colour. (4) The grid passes `getRowId`, so the row id is the `\u001f`-joined key the parent's `edits` and `errors`
use. `whole-tree vue-tsc`, `eslint` and the build wait for the gate.

#### Plan delta, 2026-10-10 — the reads answer `NOT_FOUND` too (the maintainer's ruling "04:23:36", relayed by the lead)

**Ruling (a): the two reads answer 404 `NOT_FOUND`**, like the manual-edit route (04:19:42). This corrects RL-1475 T3 and T4
(`RATE_TABLE_MISS`) and PL-1558 Acceptance 4 and RL-1475 Acceptance 5; the plan body and the ruling are not edited. Done at the
route layer: `spec_not_found()` now wraps `read_rate_table` and `read_rate_table_cells`; the loader is unchanged.
**Spec:** in `03`, the FR 9940 row and the two §5.1 rows say `NOT_FOUND`, each with a dated line citing 04:19:42 and 04:23:36
and the correcting ruling **`RL 9942`** (a working id reserved by the lead; a decision-maker drafts it; it corrects RL-1475
T3 and T4).
**Merge need: `RL 9942` minted on main before S4's ACK.** Until it is, the dated lines cite a working id.
**Red by cause, then green** (DB-free, `test_rate_table_route_codes.py`): with the wrappers off, both parametrised cases fail
`assert ('RATE_TABLE_MISS', 404) == ('NOT_FOUND', 404)`; with them on, `4 passed`. (A first red run failed for a wrong cause,
a `None` caller, and was discarded.) The DB route tests read `_READ_MISS_CODE` and `_EDIT_MISS_CODE`, both `NOT_FOUND`: OWED
at the gate.

#### Task 7 — `RateTableEditorView.vue`, the route, the FR-25 link (2026-10-10)

**Red first.** With the route added and the view absent: `vitest run src/router/__tests__/reachability.test.ts` →
2 failed (`/rating/:slug/v/:version/tables/:tableSlug` named unreachable; and a dead-link check), the editor test file
failing to load (load 1.38). With the view written, the pinned-table link test in `RatingVersionView.test.ts` was red
(`Unable to find role="link" and name "area@3"`) before the view's links. **Green:** `RateTableEditorView.test.ts` 8 passed;
`RatingVersionView.test.ts` and `src/router` 29 passed (5 files).
**Coverage of the plan's acceptance.** 11: columns and unit (grid tests), Next/Previous follow the cursor, one page read on
mount, no `pageThrough`. 13: save disabled until a non-blank note and an edit; Review posts the full edited row and shows the
diff with each old → new value; Confirm posts `confirm: true` and loads `area@4`; a 422's `edits.<i>.<value>` marks the
cell it names (kept edit), and a refusal naming no cell is an alert. 14: no approval, lifecycle or status text renders, and
`git grep -n -i status -- frontend/src/views/RateTableEditorView.vue` prints nothing (the created-notice uses
`aria-live`, not a `role` with that word). 15: `RatingVersionView` renders one link per `pins.rate_tables` entry and makes
the one read (`getRatingVersion` once; no list call). 16: reachability passes with the new route reached by that link and no
exception added.
**Deviations.** (1) The Rating Version page is routed by id (`/rating-versions/:id`), so Acceptance 15's "exactly one
`GET /rating-versions/{slug}@{version}`" is, there, its one by-id read, which returns the same `RatingVersion` with `pins`.
The editor itself reads `getRatingVersionByRef` (S2's name) once. (2) The view gates Review on an edit and a non-blank note,
not on decimal syntax: the cell flags a bad entry, and the server's FieldError (FR-234) marks it on save, so the syntax
rule is not defined a third time. (3) The confirm diff shows the server's summary (`changed_cells`, largest relative
change) and each edited cell's old → new strings; no per-cell absolute or relative arithmetic is done in the browser, which
would need decimal arithmetic the platform does not yet ship to the client. (4) After a confirm the view loads the new
version (`area@4`) though the Rating Version still pins `area@3` (versions are immutable pins).
**Not run:** whole-tree `vue-tsc`, `eslint`, `pnpm build`, `generate-contracts --check`, `audit-docs`, `req-coverage`, the
full `pytest`, `migrate --verify` and the DB tests wait for the GO and the gate slot.

#### Task 0 re-run and the C-conditions as authoring (2026-10-10, 08:52 BST, 07:52 UTC)

**Task 0, re-run.** `git fetch origin`; `origin/main` is `db0642c4b4f87e71dceff36d1ebd7c7ba4ef68f9`,
`2026-10-10T08:41:02+01:00`. The branch is not merged with it (the merge is the merge turn's). Each RL-1555
T1/T3/T4 find string and RL-1475 T4/T5 anchor of the table above was counted with
`grep -cF -- '<string>'` on `git show origin/main:docs/specs/03-rating-engine.md`: **each is 1**. The same
strings on the branch's `03` print 0 for the five this branch's commits consumed (T1 `Owner: WK-675's editor
slice. |`, T3 ``hand, so both are `null`.``, T4 (a) and (b)) and 1 for the rest (RL-1555 T2, RL-1475 T4, T5
and T3 anchors, `**FR-1186**`): a consumed anchor reads 0 on the branch because the edit landed, not because it
is missing. Step 4 (the two `jsonb_typeof` counts) stays owed to the gate (no Postgres here; unchanged).

**Plan delta, 2026-10-10: the production `assert` (the maintainer's ruling "2026-10-10 08:49:39 BST", (C),
relayed by the lead).** `_persist_new_version`'s bare `assert derived.rows is not None` is replaced by an explicit
`if derived.rows is None: raise PlatformError("INTERNAL_ERROR", "Internal server error", 500, <static text>)`
at `backend/src/app/platform/rate_tables.py:1332`. `INTERNAL_ERROR` is in the catalogue already
(`backend/src/app/errors.py`, `_GENERIC_ERROR_CODES`, a code of the shared request machinery), so no new code and
no spec change. The text is static (NFR-499). Red-first test:
`test_persisting_a_derived_version_without_rows_is_an_internal_error` (`backend/tests/test_rate_tables_service.py:624`,
DB-free: a `storage="parquet"` version carries `rows=None`, and the check fires before the session or table row is
touched). **Red/green not run:** gate-1 was held, so no test ran. Under the old `assert` that call raises
`AssertionError`, not `PlatformError`, so the `pytest.raises(PlatformError)` could not pass; the run is owed to the
gate. `ruff check` on the two files: passed.

**Plan delta, 2026-10-10: the retype ripple edits (the same ruling, (C) 2nd bullet: accepted).** RL-1475 T5 types
`default_row` and `rows` as `RateTableCell`, which breaks every site that read them as a bare `dict`. Each edit
below is that retype and nothing else; the line is the branch head's, and `git diff -U0 26f93be0` per file
(`26f93be0` the merge-base) shows no hunk of the retype outside this list.

| File:line | Edit | Reason |
|---|---|---|
| `backend/src/app/platform/rate_tables.py:1332` | `cells = cast(list[dict[str, str]], derived.rows)` → the explicit check above, then `cells = [dict(row.root) for row in derived.rows]` | `rows` is `list[RateTableCell] \| None`; a cast no longer describes it |
| `packages/pricing-core/src/pricing_core/rate_tables/operations.py:541` | `_rows_of` → `[dict(row.root) for row in table.rows]` (was `{key: str(value) …}` per row) | a `RateTableCell` is a `RootModel`, read by `.root`; the `str()` coercion is what the retype retires |
| `…/operations.py:544` | new `_default_row_of(table)` | `default_row` is a `RateTableCell`, so the callers below need a dict form |
| `…/operations.py:561` | `default_row=table.default_row` → `default_row=_default_row_of(table)` in `_validate_result` | as :544 |
| `…/operations.py:649` | `"rows": rows` → `"rows": [RateTableCell(row) for row in rows]` in `_new_version` | the new version's `rows` must be cells |
| `…/operations.py:958` | `default_row=version.default_row` → `default_row=_default_row_of(version)` in `_checked_import` | as :544 |
| `backend/src/app/platform/rate_tables.py:271`, `:273` | `_wire_rows` returns `list[RateTableCell]`: `[RateTableCell(row) for row in cells]` (was a `cast`) | the wire rows are cells. **Covered by PL-1558 :261 (in its write set), not a ripple edit; the lead ruled so on 2026-10-10.** |
| `backend/tests/test_rate_tables_service.py:145`, `:450` | `row["driver_age_band"]: row["relativity"]` → `row.root[…]: row.root[…]` | the test reads the wire rows, now cells |
| `packages/pricing-core/tests/test_rate_table_bulk_ops.py:142, 158, 175, 198, 213, 246, 259, 282` | `result.rows ==` / `baseline.rows ==` → `_cells(result) ==` / `_cells(baseline) ==` (eight lines; `:75` adds the helper `_cells`, which returns `[row.root for row in version.rows]`) | `rows` holds cells, which do not compare equal to a dict. **The expected value on each right-hand side is unchanged** (`-U0` shows only the left-hand side edited). |

The other hunks of these files (the manual-edit route, `apply_cell_edits`, `EditIssue`, the imports, `created_by_edit`
persistence) are Task 3's feature code, not ripple.

**Plan delta, 2026-10-10: the two `assert`s in `manual_edit_preview` (the lead's ruling after 55a460db, inside the
reason of 08:49:39 (C)).** `assert base.rows is not None` / `assert derived.rows is not None` (`rate_tables.py`,
formerly :1023/:1024) become one `if base.rows is None or derived.rows is None: raise _rows_form_violated()`. The
helper `_rows_form_violated` (new, above `manual_edit_preview`) returns the `INTERNAL_ERROR` 500 `PlatformError` with
static text (NFR-499), and the :1332 guard now raises the same helper, so the text is written once. **No DB-free red
test:** the condition is reachable only through `_edit_derived`, which reads the database, so its red-first test is
owed to the gate (the :1332 test still covers the helper). `ruff check` passed.

**Observed, not changed.** Two bare `assert`s pre-existing on main, outside S4's scope: `rate_tables.py:537`
(`assert cache is not None`, in the diff-cells path) and `:736` (`assert start is not None`, after
`decode_int_cursor`). The lead raises them at the ACK.

**Gate-1 run, 2026-10-10 (head 56ffdbdb), recorded.** (a) `fe7fd56e`'s `test_rate_table_isolation_another_workspace_answers_404`
is a GUARD, not a red-first: the 404 held on the parent (maintainer's "2026-10-10 22:16:18 BST" entry, item 4). (b) `3372f5ce` and
`20a220fd` were UNPROVEN in that run (collection errors on the reverted files); they are re-run red on the revert (backend src
only, the DB files alone) in the next slot. (c) BREACH: an `audit-docs` run on a detached `origin/main` tree while another seat
held gate-1, a sweep-pause breach (same entry, item 5). (d) The census row for `_edit_failure` and the docstrings state what the
messages carry: FR-234's value issues name the table key and the submitted value, which is pricing configuration and not a quote
input under NFR-499 (same entry, item 1); the count message interpolates only `len(errors)`. (e) The 13 audit-docs-driven pytest
reds at 56ffdbdb are a hypothesis (working ids unminted); proof is CI on the minted head with those 13 named and green.

## PRs

None yet.
