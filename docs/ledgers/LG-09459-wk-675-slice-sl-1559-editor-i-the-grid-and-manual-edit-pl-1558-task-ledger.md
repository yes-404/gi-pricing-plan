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
| 2 | the two reads, RL-1475 T3 and T4 | 1–5 | open |
| 3 | the manual-edit route, RL-1555 T1 to T4 | 6–8 | open |
| 4 | the dependency and its records | 17 | open |
| 5 | `rateTables.ts` | — | open |
| 6 | `DecimalCellInput.vue`, `RateTableGrid.vue` | 11, 12 | open |
| 7 | `RateTableEditorView.vue`, route, FR-25 link | 11, 13–16 | open |
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

## PRs

None yet.
