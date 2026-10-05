---
id: RL-9753
family: ruling
title: PL-1286 DP-4's texts — the algorithm read by slug@version (S2), and a rate table version's definition and cell-page reads (S4); a version's table list is its pins, not a route
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-01
owner: decision-maker
tree: 8bd782acbbdde8e3b4195b5a0acb89183b5a0253
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1286, FR-212, FR-228, FR-229, FR-232, FR-237, FD-1283, FD-1366]
---

# RL-9753 — PL-1286 DP-4's texts: the algorithm read by `slug@version` (S2), and a rate table version's definition and cell-page reads (S4); a version's table list is its pins, not a route

## How this was ruled

**Written 2026-10-01 10:35 BST at effort `medium`** by the decision-maker session
`dm-675dp56` (command line `claude --effort medium --model opus --name dm-675dp56`;
`CLAUDE_EFFORT=medium`). The lead commissioned it at 10:32:18 BST, with the stamp taken from
`date`. **Working id 9753**, reserved by the lead. It is minted at its merge turn, and every
`RL-<this>` below is then its minted id.

**What is decided and what is owed.** DP-4's **scope** was decided by the maintainer, by
delegation, on 2026-09-30 at 05:34:33 BST, as (a) (`PL-1286`:243, the *Resolved by* cell).
Each missing read route gets a spec change first, a new FR plus its `03` §5.1 row, and is
built in the WK-675 slice that consumes it: the algorithm load in **S2**, and the rate-table
cells and a version's table list in **S4**. This record does not reopen that scope. It
writes the owed texts, and it decides one thing inside them: **a version's table list needs
no route** (*Ruled*, item 3).

**Evidence tree:** origin/main `1dd5e264` (tree `8bd782ac`). Not touched: DP-3 (`OQ-1223`)
and DP-7 (`OQ-1285`).

## Evidence at `1dd5e264`

- **Algorithm load.**
  - `get_algorithm(database, workspace_id, slug, version) -> RatingAlgorithm` exists
    (`backend/src/app/platform/rating_algorithms.py:135-154`). It answers 404 `NOT_FOUND`
    for an unknown or foreign version (`:148`). No route calls it except the diff route
    (`:157-163`).
  - `RatingAlgorithm` is at `packages/model-schema/src/model_schema/rating.py:374`, and it
    is **absent** from `docs/contracts/openapi/generated.json` `components.schemas` (F2
    condition 1 is S2's).
  - The routes beside it: `POST /rating-algorithms` and
    `GET /rating-algorithms/{slug}@{version}/diff` (`backend/src/app/api/rating_algorithms.py:28`,
    `:53`). RL 9767 (working id) adds `POST /rating-algorithms/validate`. None clashes with
    a `GET` on `{slug}@{version}`: the diff route has a further segment, and `validate`
    is a `POST` with no `@`.
- **Rate table reads.**
  - The service loads a table, a version and the cells for either storage:
    `_load_table` (`backend/src/app/platform/rate_tables.py:189-205`, 404
    `RATE_TABLE_MISS`), `_load_version` (`:462-481`, 404 `RATE_TABLE_MISS`), `_load_cells`
    (`:484-499`, rows storage) and `_load_cells_of` (`:533-543`, parquet through the blob
    store). The wire-row conversion is `_wire_rows` (`:184-186`).
  - `_load_cells` selects **without an `ORDER BY`** (`:487-492`), so the stored order is
    not stable for paging.
  - The shapes: `RateTable` (`rating.py:684-700`) is the definition without cells, with
    `default_row: dict[str, Any] | None` (`:700`). `RateTableVersion` (`rating.py:851-900`)
    carries `rows: list[dict[str, str | int]] | None` and the storage validator.
  - Neither shape is in `generated.json` (`RateTableDiff` is). The DB model
    `RateTableCellRow` (`backend/src/app/db/models.py:2084`) takes that name, so the new
    model-schema type is **`RateTableCell`**, which is free.
  - Pagination: `Page[T]` (`backend/src/app/api/pagination.py:48-61`) has `items`,
    `next_cursor` and `total_estimate`. It is published as `Page_<T>_` (for example
    `Page_SubGraph_`, `GET /sub-graphs/{slug}/versions`, `backend/src/app/api/sub_graphs.py:83-97`).
    `decode_int_cursor` (`pagination.py:91`) answers a malformed cursor with **400**
    `VALIDATION_FAILED` (`:82-88`).
  - FR-232 (`03:123`) already says that "the editor pages without a job".
- **A version's table list.** `RatingVersion.pins.rate_tables: list[ArtifactRef]`
  (`rating.py:74`, `Pins`). RL 9766 (working id)'s `GET /rating-versions/{slug}@{version}`
  returns the `RatingVersion`, so the list arrives with it.
- **No duplicate row.** The rows below are new paths. RL 9766 (working id) T2 adds the two
  `rating-versions` reads. RL 9767 (working id) T2 adds `POST /rating-algorithms/validate`.
  RL 9907 (working id) item 3 describes only the two `rating-versions` reads, and item 1
  adds a column, not rows. None of them names `GET /rating-algorithms/{slug}@{version}`
  or any `rate-tables` read. `07` §5.1 needs no row: every route here is a `03` route.

## Ruled

1. **S2: `GET /api/v1/rating-algorithms/{slug}@{version}` → 200 `RatingAlgorithm`**
   (rating:read, 404 `NOT_FOUND`). It is served by `get_algorithm`, with no new query. The
   route is the first to publish `RatingAlgorithm` in the generated contract, which is F2
   condition 1.
2. **S4: two reads.**
   - `GET /api/v1/rate-tables/{slug}@{version}` → 200 **`RateTable`**, the existing
     definition shape, without cells.
   - `GET /api/v1/rate-tables/{slug}@{version}/cells?cursor=&limit=` → 200
     **`Page[RateTableCell]`**, for both storages, never a Job (FR-232). The order is the
     **code-point order of the key columns' string values, column by column in the declared
     key order**, sorted in one place for both storages.
   - A new model-schema **`RateTableCell`** is a `RootModel[dict[str, str]]`: §4.2's row
     form. `rows` and both `default_row` fields are retyped to it, so the row is defined
     once, and the `dict[str, Any]` in `RateTable.default_row` leaves the published shape.
     *(Amended 2026-10-01 10:43 BST, F1 and F2: the type said `dict[str, str | int]`, and
     the order was not defined. `RateTableVersion.rows` inherited the `| int` arm, which
     nothing produces: `CellRow = dict[str, str]` (`pricing_core/rate_tables/operations.py:81`),
     `_wire_rows` "every value is a decimal string" (`backend/src/app/platform/rate_tables.py:184-186`), and §4.2
     "Values are stored as decimal strings" (`03:310`). So the arm is dropped, not
     carried.)*
3. **No route for a version's table list.** It is `pins.rate_tables` on the Rating Version,
   which RL 9766's read returns. A list route would be a second source for the same fact.
   The editor reads each table's definition through item 2.

**Why `RateTableCell` is an open-keyed object.** A table's columns are data, declared per
table by FR-228, so no static type can name them. The value type is closed (`str`),
and the column set is checked against the version's declared keys on the server. This is
the narrowest type that is still §4.2's wire form. A positional alternative
(`{"keys": [...], "value": ...}`) would be a second row representation beside `rows`, and
`CLAUDE.md` §2 forbids that. *(Amended 2026-10-01 10:43 BST, accepted by the lead.)* **A
map with typed values whose keys are data (FR-228) is not an "open object" in FD-1366's
sense, and `RateTable.default_row`'s `dict[str, Any]` is removed.**

**The routes, and their types.**

| Method, path | Request body | 2xx response | Permission | Slice |
|---|---|---|---|---|
| `GET /api/v1/rating-algorithms/{slug}@{version}` | none | **200** `RatingAlgorithm` (`packages/model-schema/src/model_schema/rating.py:374`) | `rating:read` | S2 |
| `GET /api/v1/rate-tables/{slug}@{version}` | none | **200** `RateTable` (`rating.py:684`) | `rating:read` | S4 |
| `GET /api/v1/rate-tables/{slug}@{version}/cells` | none (query: `cursor`, `limit`) | **200** `Page[RateTableCell]`, published as `Page_RateTableCell_`; `RateTableCell` is **new** in `rating.py`, and `Page` is `backend/src/app/api/pagination.py:48` | `rating:read` | S4 |

No `dict[str, Any]` appears in any signature.

**FD-1366, rule (ii).** S2 saves through `POST /api/v1/rating-algorithms`, one
of that finding's five untyped request bodies (`body: dict[str, Any]`, the handler at
`rating_algorithms.py:34`). Under the finding's per-route hold, a slice that edits that
handler types its body (as `RatingAlgorithm`) in the same slice and removes the guard entry
in the same commit; a slice that only calls it waits until it is typed. This record does
not type it.

## Spec changes this ruling requires

**S2 applies T1 and T2. S4 applies T3, T4 and T5.** Each slice applies them with
`.claude/skills/spec-change`, in the same commit as its code (`CLAUDE.md` §2). Placement was
read at origin/main `1dd5e264`, and re-read at main `ef5dc6e7` on 2026-10-05: each anchor
below is found there exactly once, and each line hint is main's. Placeholders: `RL-<this>` is this record's minted id.
`FR-<a>` and `FR-<b>` are the requirement ids minted for T1 and T3 when they are applied.
`<date>` is the date of the applying commit. Nothing else is a placeholder.

**T1 — `03` §3.1, a new FR (S2).** Placement: `docs/specs/03-rating-engine.md`. Insert as
**the last row of the §3.1 table**, on the line immediately before the blank line that
precedes `### 3.2 Rating step types`. That is the last row whichever of this text and RL
9767 (working id)'s §3.1 FR is applied first. Nothing is struck.

```text
| **FR-<a>** | **A Rating Algorithm version is readable by its `slug@version`.** *(Added <date>, `RL-<this>`, `PL-1286` DP-4.)* `GET /api/v1/rating-algorithms/{slug}@{version}` returns the saved `RatingAlgorithm` (§4.1) exactly as it passed save-time validation (FR-212). The DAG designer loads a Rating Version's algorithm through the version's `algorithm_ref` (FR-237), and edits it into a new algorithm version, never in place. The read requires `rating:read` and answers **404** `NOT_FOUND` for an unknown version or another workspace's. |
```

**T2 — `03` §5.1, one row (S2).** Insert immediately **before** the row that begins
`| `POST` | `/api/v1/sub-graphs` |` (`:897`). Nothing is struck.

If RL 9907 (working id)'s `Permission` column has not landed in `03` §5.1 when a row is applied, the row is applied in its three-cell form:

```text
| `GET` | `/api/v1/rating-algorithms/{slug}@{version}` | Read one Rating Algorithm version (FR-<a>); requires `rating:read`. **200** with a `RatingAlgorithm` (§4.1); 401; 403; **404** `NOT_FOUND` on an unknown version or another workspace's. **Added <date>** (`RL-<this>`) |
```

If RL 9907 (working id)'s `Permission` column has landed in `03` §5.1 when a row is applied, the row carries a fourth cell, `rating:read`, and is applied in its four-cell form instead:

```text
| `GET` | `/api/v1/rating-algorithms/{slug}@{version}` | Read one Rating Algorithm version (FR-<a>); requires `rating:read`. **200** with a `RatingAlgorithm` (§4.1); 401; 403; **404** `NOT_FOUND` on an unknown version or another workspace's. **Added <date>** (`RL-<this>`) | `rating:read` |
```

**T3 — `03` §3.3, a new FR (S4).** Insert as **the last row of the §3.3 table**, on the line
immediately before the blank line that precedes `### 3.4 Rating versions and bundles`
(after the FR-1186 row at `:128` at this tree). Nothing is struck.

```text
| **FR-<b>** | **A Rate Table Version's definition and cells are readable by its `slug@version`, and its cells are paged in either storage without a Job.** *(Added <date>, `RL-<this>`, `PL-1286` DP-4.)* `GET /api/v1/rate-tables/{slug}@{version}` returns the version's definition as a `RateTable` (§4.2: keys, value, storage, rateable flag and default row), never its cells. `GET /api/v1/rate-tables/{slug}@{version}/cells` returns the cells as cursor-paginated pages of `RateTableCell` rows, each in §4.2's row form, in one fixed order: code-point order, per key column in declared order, compared as strings (so `"10"` sorts before `"9"`, and `"B"` before `"a"`), the same for both storages. The version is immutable, so a cursor stays valid across calls. Both storages, `rows` and `parquet`, answer **200** (FR-232): paging is never a Job. Both reads require `rating:read` and answer **404** `RATE_TABLE_MISS` for an unknown table or version, or another workspace's. The tables a Rating Version pins are not a separate read: they are `pins.rate_tables` on the Rating Version (§4.3, FR-237), read by its `slug@version` (§5.1). |
```

**T4 — `03` §5.1, two rows (S4).** Insert both, in this order, immediately **before** the
row that begins `` | `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against= `` (`:904`),
the find string ending before the path's closing backtick. Nothing is struck. *(Re-anchored
2026-10-05 17:29 BST, before mint: see the last amendment.)*

If RL 9907 (working id)'s `Permission` column has not landed in `03` §5.1 when a row is applied, the row is applied in its three-cell form:

```text
| `GET` | `/api/v1/rate-tables/{slug}@{version}` | Read one Rate Table Version's definition, without its cells (FR-<b>); requires `rating:read`. **200** with a `RateTable` (§4.2); 401; 403; **404** `RATE_TABLE_MISS` on an unknown table or version or another workspace's. **Added <date>** (`RL-<this>`) |
| `GET` | `/api/v1/rate-tables/{slug}@{version}/cells?cursor=&limit=` | Page through one Rate Table Version's cells in either storage, with no Job (FR-<b>, FR-232); requires `rating:read`. **200** with a page of `RateTableCell` rows; 401; 403; **400** `VALIDATION_FAILED` on a malformed cursor; **404** `RATE_TABLE_MISS` on an unknown table or version or another workspace's; **422** on a `limit` out of range. **Added <date>** (`RL-<this>`) |
```

If RL 9907 (working id)'s `Permission` column has landed in `03` §5.1 when a row is applied, the row carries a fourth cell, `rating:read`, and is applied in its four-cell form instead:

```text
| `GET` | `/api/v1/rate-tables/{slug}@{version}` | Read one Rate Table Version's definition, without its cells (FR-<b>); requires `rating:read`. **200** with a `RateTable` (§4.2); 401; 403; **404** `RATE_TABLE_MISS` on an unknown table or version or another workspace's. **Added <date>** (`RL-<this>`) | `rating:read` |
| `GET` | `/api/v1/rate-tables/{slug}@{version}/cells?cursor=&limit=` | Page through one Rate Table Version's cells in either storage, with no Job (FR-<b>, FR-232); requires `rating:read`. **200** with a page of `RateTableCell` rows; 401; 403; **400** `VALIDATION_FAILED` on a malformed cursor; **404** `RATE_TABLE_MISS` on an unknown table or version or another workspace's; **422** on a `limit` out of range. **Added <date>** (`RL-<this>`) | `rating:read` |
```

**The permission name exists.** Run at origin/main `1dd5e264`:
`git grep -n -E 'RATING_(READ|WRITE) = ' origin/main -- packages/model-schema/src/model_schema/permissions.py`
and `` git grep -n -E '^> \| `rating:(read|write)` \|' origin/main -- docs/specs/06-governance.md ``.
The second command's hits are rows of `06` §4.1's *Built and now specified* table, which starts at `06:260`. That table "has exactly one row per member of `model_schema.Permission`". Output, verbatim:

```text
origin/main:packages/model-schema/src/model_schema/permissions.py:47:    RATING_READ = "rating:read"
origin/main:packages/model-schema/src/model_schema/permissions.py:48:    RATING_WRITE = "rating:write"
origin/main:docs/specs/06-governance.md:278:> | `rating:read` | Reading Rating Algorithms, Sub-graphs, Regression Suites, Rate Tables, Rating Versions and scoring traces |  |
origin/main:docs/specs/06-governance.md:279:> | `rating:write` | Writing Rating Algorithms and Rate Tables, and creating a Rating Version (`RL-1236` DP-A) |  |
```

**T5 — `03` §4.2, a dated note (S4).** Insert one new paragraph, followed by a blank line,
immediately before the line `### 4.3 `RatingVersion`` (`:369`), after the blockquote that
ends `remain mutually exclusive.`. Nothing is struck. *(Re-read 2026-10-05 at `ef5dc6e7`:
`RL-1375`'s re-seeding blockquote (`:361-367`) now sits between that blockquote and
`### 4.3`. The anchor is still the `### 4.3` line, so the paragraph goes after both
blockquotes.)*

```text
*(Added <date>, `RL-<this>`.)* **`RateTableCell`** is one row in the form `rows` uses above: an object whose members are the table's key columns and its value column, each value a string (a key level or a decimal string). A Rate Table Version's `rows` and `default_row` are typed as `RateTableCell`, and the cells read (§5.1, FR-<b>) returns pages of it. The definition read returns a `RateTable`, which carries every field above except `rows`, `cells`, `change_note`, `seeded_from`, `created_by_operation`, `created_by_import`, `diff_vs_previous` and `diff_vs_seed`.
```

The executor applies each text above byte-for-byte; authorship stays with the decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296 precedent). Any executor wording is a stop. If a text's anchor is not found exactly once, that is a stop too, reported to the lead; the executor does not re-word it.

## What it obliges

- **This commit:** this record only. Neither `PL-1286` nor any spec is edited.
- **S2, in one commit with T1 and T2:**
  - the handler in `backend/src/app/api/rating_algorithms.py`, typed `-> RatingAlgorithm`
    and calling `get_algorithm`;
  - `docs/contracts/` regenerated, so `RatingAlgorithm` reaches `generated.json` (F2
    condition 1);
  - the designer loads through the generated client;
  - FD-1366 rule (ii), above.
- **S4, in one commit with T3, T4 and T5:**
  - `RateTableCell` in model-schema;
  - `RateTableVersion.rows`, `RateTableVersion.default_row` and `RateTable.default_row`
    retyped to it;
  - the two handlers in `backend/src/app/api/rate_tables.py`, typed `-> RateTable` and
    `-> Page[RateTableCell]`, built on `_load_table`, `_load_version` and `_load_cells_of`;
  - **the cell page ordered by key, sorted in one place.** *(Amended 2026-10-01 10:43 BST,
    F2.)* One function sorts the loaded cells of both storages, in Python, by code-point
    order per key column in declared order, compared as strings. The rows path does not
    rely on a database `ORDER BY`, whose collation could differ from the parquet path's.
    A test pins the result, red first on a fixture with mixed-case levels (`"B"`, `"a"`)
    and numeric strings (`"10"`, `"9"`). The rows path loads the version's cells per page,
    a cost bounded by FR-232's threshold, and S4 states that bound under test;
  - `docs/contracts/` regenerated.
  - **A stop, not a decision:** if any persisted `default_row` or row value is not a
    `str`, the retyping would reject stored data. S4 measures that against the
    test database's seeded tables before retyping, and stops and reports if there is one.
- **Contention** (`PL-1286` *Sequencing*): T1 is in §3.1, T3 in §3.3, T2 and T4 in §5.1,
  and T5 in §4.2. Each serialises as that table says. T1 and RL 9767 T1 both land at the
  end of §3.1, and the anchor above makes their order irrelevant.

## Acceptance — the violation that must become detectable

Each backend test carries `@pytest.mark.req` with its FR and is shown red on deliberately
broken input.

1. **Algorithm read (FR-<a>).** A saved algorithm reads back equal to what was saved. An
   unknown version and another workspace's version answer 404 `NOT_FOUND`. A principal
   without `rating:read` gets 403. In `generated.json`, the 200 response is a `$ref` to
   `RatingAlgorithm`.
2. **Definition read (FR-<b>).** The response carries no `rows` and no `cells` key. Broken
   input: return `RateTableVersion`, and the test fails.
3. **Cell pages, both storages (FR-<b>, FR-232).**
   - A table written as `rows` and the same cells written as `parquet` (the threshold
     lowered in the test) page to identical sequences, and the calls create no Job.
   - Broken input: sort the rows path in the database under a non-C collation, or leave
     either path unsorted, and the sequences differ on the mixed-case and numeric-string
     fixture. *(Amended 2026-10-01 10:43 BST, F2.)* The expected order is written out in the
     test: `"10"` before `"9"`, and `"B"` before `"a"`.
4. **Pagination.** Concatenated pages equal the full cell set with no duplicates. A
   malformed cursor answers 400 `VALIDATION_FAILED`, and a `limit` above the maximum
   answers 422.
5. **Isolation.** Another workspace's `slug@version` answers 404 `RATE_TABLE_MISS` on both
   reads.
6. **Contract.** The cells read's 200 response is a `$ref` to `Page_RateTableCell_`, whose
   items are a `$ref` to `RateTableCell`. `RateTable.default_row` is no longer an
   `additionalProperties: true` object. `uv run python scripts/generate-contracts.py
   --check` exits 0.
7. **Table list.** The editor's test reads the tables from the Rating Version's
   `pins.rate_tables` and makes no other list call.

## Amendment, 2026-10-01 10:43 BST: auditor-1067's F1, F2 and F3, the open-object line, and FD-1366

*By the decision-maker session `dm-675dp56` (effort `medium`), on auditor-1067's audit of
`272e109b`, all three findings adopted by the lead. The branch was merged with origin/main
`92b4e4ac` (mint batch A) so that `FD-1366` resolves. The ruled routes are unchanged.*

- **F2 (MED): the order is named.** It is code-point order, per key column in declared
  order, compared as strings, sorted in one Python function for both storages, and pinned by
  a red-first mixed-case and numeric-string test. T3, *Ruled* item 2, *What it obliges* and
  Acceptance 3 are rewritten.
- **F1 (LOW-MED): the `int` arm is dropped.** `RateTableCell` is
  `RootModel[dict[str, str]]`. No producer emits an int (`pricing_core/rate_tables/operations.py:81`; `backend/src/app/platform/rate_tables.py:184-186`;
  `03:310`). T5 reads "each value a string (a key level or a decimal string)". The S4 stop now
  fires on any persisted non-`str` value.
- **F3 (LOW):** T5's list of fields `RateTable` lacks adds `diff_vs_previous` and
  `diff_vs_seed` (`03:304-306`).
- **Accepted line:** a typed-value map whose keys are data (FR-228) is not an "open object"
  in FD-1366's sense, and `RateTable.default_row`'s `dict[str, Any]` is removed.
- **FD 9779 (working id) is re-pointed to `FD-1366`** (three places) and added to
  `relates:`.

## Amendment, 2026-10-05: citations re-read at main `ef5dc6e7`, before mint

Citation and currency update only. Nothing ruled above changes (decision-maker `dm-amend-2`,
on the lead's brief of 2026-10-05 10:50 BST, which adopted the batch-2 triage).

- **T1 to T5 re-read at `ef5dc6e7`.** T1: §3.1's last row is still FR-219 (`:88`), before
  `### 3.2` (`:90`). T2's `POST /api/v1/sub-graphs` row moved `:781` → `:897`. T3: FR-1186
  is still `:128`, the last row of §3.3. T4's `rate-tables/{slug}@{version}/diff` row moved
  `:788` → `:904`. T5's `### 4.3` line moved `:345` → `:369`, and `RL-1375`'s blockquote
  now precedes it (noted at T5). `03` §5.1's header is still `| Method | Path | Purpose |`,
  so RL 9907 (working id)'s `Permission` column has not landed and the three-cell forms are
  the ones that apply today.
- **The Evidence, *Ruled* and 10:43 BST amendment sections are dated readings at
  `1dd5e264`** and resolve there (`git show 1dd5e264:<path>`). They are not rewritten. At
  `ef5dc6e7` their moved cites are: `03` §4.2 "Values are stored as decimal strings"
  `03:310` → `:317`, and its `diff_vs_previous`/`diff_vs_seed` example `:304-306` →
  `:311-313`; `_load_table` `rate_tables.py:189-205` → `:243-259`, `_load_version`
  `:462-481` → `:528-547`, `_load_cells` `:484-499` → `:550-565` (its select `:487-492` →
  `:553-558`), `_load_cells_of` `:533-543` → `:599-609`, `_wire_rows` `:184-186` →
  `:238-240`; `RatingAlgorithm` `model_schema/rating.py:374` → `:375`, `Pins.rate_tables` `:74` → `:75`,
  `RateTable` `:684-700` → `:702-718`, `RateTableVersion` `:851-900` → `:899-948`;
  `db/models.py:2084` → `:2088`. FR-232 is still `03:123`, and
  `platform/rating_algorithms.py:135-163`, `api/rating_algorithms.py:28`,
  `pagination.py:48-61`, `:82-88` and `:91`, `api/sub_graphs.py:83-97` and
  `rate_tables/operations.py:81` are unchanged.
- **The pasted `06` permission rows** are verbatim output at `1dd5e264` and stay as
  quoted. At `ef5dc6e7` they are `06-governance.md:280-281`, and both names still exist.
- **`status:` is `active`, not `draft`.** `document-ids.md` §1.2a gives a ruling the subset
  `active`, `superseded`, `retired`, and `audit-docs.py` check 33 refused `draft`. The
  working-id rulings of batch 1 (#977, #979) carry `active` in the same form.
- `tree:` stays `8bd782ac`, the tree of `1dd5e264` that the Evidence was read at, as
  `RL-1407` keeps its own evidence tree. `created:` changes at the mint. RL 9766, RL 9767
  and RL 9907 are still working ids (#1055, #977) and are cited as such.

## Amendment, 2026-10-05 15:29 BST: citations re-read at main `809a3794`, before mint

Citation update only. Nothing ruled above changes (decision-maker `dm-premint2`, on the
lead's prep-wave brief of 2026-10-05, section M).

- **T1 to T5 re-read at `809a3794`.** Each anchor is found exactly once, at the line the
  amendment above gives: `### 3.2` at `03:90` (FR-219 at `:88` is still §3.1's last row),
  the `| `POST` | `/api/v1/sub-graphs` |` row at `:897`, `### 3.4 Rating versions and
  bundles` at `:130` (FR-1186 at `:128` is still §3.3's last row), the
  `rate-tables/{slug}@{version}/diff?against=` row at `:904`, and `### 4.3 `RatingVersion``
  at `:369`. `03` §5.1's header is still `| Method | Path | Purpose |`, so the three-cell
  forms still apply.
- **Moved since `ef5dc6e7`:** `RateTableCellRow`, the Evidence's `db/models.py:2084`, is now
  `db/models.py:2099`; the pasted `06` permission rows are now `06-governance.md:281-282`,
  and `RATING_READ` and `RATING_WRITE` are now `permissions.py:48-49`. Both names still
  exist. `06` §4.1's table starts at `:262`. The other cites the amendment above gives are
  unchanged at `809a3794`, including `03:317` and `03:123`.

## Amendment, 2026-10-05 17:29 BST: T4's anchor re-set so it survives WK-673 Slice 7, before mint

Placement only; T4's two rows, their order and every other text are unchanged (decision-maker
`dm-675s4`, on the maintainer's (by delegation) entry "2026-10-05 17:26:46 BST — WK-675 S4 DP
memo (handover/dp-memo-wk675-s4-2026-10-05.md) RULED", `channel/to-lead.md`, routed by the lead).
That entry: "RL 9753 T4's anchor (#1067 :176-178, ending "diff?against=` |") WILL NOT MATCH
once S7 applies RL-1361 T10 (the row becomes ".../diff?against=&portfolio="): re-anchor RL 9753
PRE-MINT on the prefix without the closing backtick (grep -cF = 1 at main AND after RL-1418 T1)."

- **Why.** WK-673 Slice 7 (`SL-1391`, leaf `PL-1419`) applies `RL-1361` T10, which **replaces**
  the diff row with one beginning
  `` | `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against=&portfolio=` | ``
  (`RL-1361` T10), and `RL-1418` T1, which inserts the `…/diff/cells?against=&portfolio=…` row
  immediately after it. S7 is ahead of WK-675 S4 (they serialise, S7 first). The old anchor,
  ending `` diff?against=` | ``, then matches nothing.
- **The new find string**, exact:
  `` | `GET` | `/api/v1/rate-tables/{slug}@{version}/diff?against= ``
  (from the leading pipe to `against=`, with no closing backtick).
- **Counted** (`grep -cF`, or Python `str.count`, over `docs/specs/03-rating-engine.md`):
  - at origin/main `4d3be141`: **1** (the `:904` row);
  - on that file with `RL-1361` T10's replacement row and `RL-1418` T1's row applied: **1**
    (the T10 row begins with it; the T1 row's path is `/diff/cells?against=`, which does not
    contain it). The old anchor counts 1 at main and **0** after.
- **Placement is unaffected by `RL-1418` T1.** T4 inserts *before* the diff row and T1 *after*
  it, so in either merge order the two rows land above the diff row, and `diff/cells` below it.
- The `:904` cite in the 15:29 BST amendment above stays as read at `809a3794`.
