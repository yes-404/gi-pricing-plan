---
id: RL-9907
family: ruling
title: WK-674 Slice 2 DP-S2-4 decided — each route's permission is declared in a Permission column on its module's §5.1 table
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 65b334792e65704206d2c21015690d7c613092cc
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1237, RL-1296, FR-343]
---

# RL-9907 — WK-674 Slice 2 DP-S2-4 decided: each route's permission is declared in a Permission column on its module's §5.1 table

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort").
- **Its term was extended to this decision point** by the entry "2026-09-30 11:17:35 BST —
  DATED CORRECTION to my A1 entries (…); DP-S2-4 routing". That entry withdraws an earlier
  statement: that route permissions were already declared in "06/03 §5.1 permission column, or
  the contract". It keeps the principle: pin each route's permission against a declaration,
  never a test-local map. It notes that the declaration does not exist yet, and rejects
  option (c) as circular.
- **The decision point is `DP-S2-4`** of WK-674 Slice 2's leaf plan (PL working id 9920, #973,
  read at `origin/wk674-s2-leaf-plan` @ `632b1ffc`). It gates only Task 0A step (c), the
  authorisation sweep's spec pin, which the maintainer moved out of Slice 2.

## Presence and absence, as verified at `65b33479`

| Claim | Verdict | How it was verified |
|---|---|---|
| A per-route permission column in the module specs | **absent** | Each module spec's `### 5.1` table header, read. `01-data-management.md:847`, `02-modelling.md:1759`, `03-rating-engine.md:742`, `06-governance.md:494` and `07-platform.md:299` are each `\| Method \| Path \| Purpose \|`. The five tables hold 39, 44, 26, 23 and 20 method rows: 152 in all (the rows beginning `` \| `GET` `` and so on, inside `### 5.1`). |
| A permission in the published contract | **absent** | `git show 65b33479:docs/contracts/openapi/generated.json \| grep -c x-permission` prints `0`. |
| A route-to-permission declaration anywhere | **present, once: 6 rows covering 7 operations** (decide and withdraw share a row, `06:514`) | `06` §5.1 carries a blockquoted `\| Route \| Requires \|` table for its approval routes, "stated 2026-08-15 after an independent audit" (`06-governance.md`, the note after the approval-request rows). Its cells are a permission name or `authenticated`. It is the precedent for (a)'s cell vocabulary. |
| Existing `§5.1` parsers | **present, three, reading only the first two cells** *(corrected: this row said "two" and cited `:297`)* | `audit-docs.py:299` `_ENDPOINT_ROW`, `scope-audit.py:68` `_ENDPOINT` and the backend's own copy, `backend/src/app/demo/guide.py:64` `_SPEC_ENDPOINT`, each match `^\|\s*method\s*\|([^\|]+)\|` and ignore the rest of the row. A fourth column breaks neither. Check 22 (`audit-docs.py`, "Every markdown table row has its own header's cell count") requires that the header and every row gain the column in the same commit. |
| How a route states its permission in code | **present, in two forms** | A `requires(<member>)` dependency tags itself with `PERMISSION_ATTRIBUTE` (`backend/src/app/api/authz.py:41`, `:76`). A handler may also call `rbac.require_permission(…, permission=…, resource=…)` itself, which the deploy route must do under #971's item B.2 (an Environment resource). So a pin read from `PERMISSION_ATTRIBUTE` alone would miss a handler-checked route. |

## Ruled

### Option (a): a `Permission` column on each module spec's §5.1 REST table

1. **The declaration.** Each of the five §5.1 tables (`01`, `02`, `03`, `06`, `07`) gains a
   fourth column, **`Permission`**, filled on **every** row, built and unbuilt, because the
   spec states a route's contract before the code exists. A cell holds exactly one of:
   - one or more **permission names**, backticked. Each is a name in `06` §4.1's Built table
     or its Specified table (#942's D4). Where the check is scoped to a resource (for
     example `deployment:promote` against an Environment, #971 B.2), the cell says so after
     the name;
   - **`authenticated`**: any authenticated caller, with no permission, as `06`'s
     2026-08-15 table already writes it;
   - **`open`**: no authentication, as for the health and version routes.

   **Multi-method rows are split, one row per method** (the maintainer's entry "11:37:11 BST
   — #977 NOT CLEAN: steers; …", item 1). Five rows name two methods:
   - `GET`/`PUT` `/datasets/{slug}/rule-set` (`01:880`);
   - `GET`/`POST` `/roles` (`06:499`);
   - `GET`/`PUT` `/approval-policy` (`06:502`);
   - `GET`/`POST` `/environments` (`07:306`);
   - `GET`/`PUT` `/settings` (`07:311`).

   Three of them carry different permissions per method. Each becomes two rows with one
   method and its own `Permission` cell, and there is **no per-method cell syntax**. The
   tables go from **152 to 157 rows**. The first two cells keep their shape, so the shared
   row reader of item 3 reads the split rows unchanged. *(This supersedes this record's previous head, which kept
   152 rows with a per-method cell.)*

   An empty cell fails. `06`'s blockquoted `| Route | Requires |` table is folded into
   `06` §5.1's column in the same commit, and a dated note records the move. One
   declaration is kept, not two.
2. **Why (a) over (b).**
   - **The steady state costs nothing new.** A slice that adds a route already writes that
     route's row in its module's §5.1, because the spec comes first (`CLAUDE.md` §0) and
     `scope-audit.py --endpoints` compares each §5.1 table with the published routes. Under (a), it fills the permission in the
     same row. Under (b), every route-adding slice in any module must **also** edit `06`
     §4.1, a governance section. That creates a new, permanent point of contention that
     serialises every such slice with every other.
   - **(b) keys routes by permission.** A route guarded by two permissions, by
     `authenticated`, or by nothing has no natural row, and `rating:read`'s cell alone would
     list dozens of routes. A reader asking "what does this route need" would have to scan
     the whole catalogue. The row a reader already reads is the route's own.
   - **(a)'s cost is one-time.** One migration commit edits five §5.1 tables: 152 rows at this tree, 157 after the split and 159 with the two added reads.
     That serialises once, against the slices in flight that append §5.1 rows (item 4),
     rather than forever.
   - **(c) stays rejected**, as the maintainer ruled. A declaration generated from
     `requires()` would move with the code under test. The leaf plan's own red case, a
     `ReadAudit` swapped from `AUDIT_READ` to `JOB_READ` (`api/audit.py:52`), would then
     stay green.
3. **The pin (Task 0A step (c)).** For every route of the live app, **with the included
   routers flattened** (#942's D1 item 2), the test compares the permission the spec
   declares with the permission the route checks. The route side is:
   - the `PERMISSION_ATTRIBUTE` of its `requires()` dependency; **and**
   - for a handler-checked route, the `permission=` argument of `require_permission(` in
     its handler, found by the AST walk #942 rules for the same purpose.

   `authenticated` matches a route with an authenticated caller and no permission. `open`
   matches a route in the sweep's named open-by-design set. The comparison fails in **both**
   directions:
   - a live route whose row is missing or whose cell differs;
   - a built row, whose route exists, that the live app does not check as declared.

   Unbuilt rows are declarations only, and the pin reads them when their route appears. The
   pin reads the rows through the shared `table_rows` module of the next bullet, and never
   through a reading of its own.
   - **Paths are compared as `audit-docs.py`'s `_path_segments` compares them:** the
     `/api/v1` prefix and any query string are dropped, and every `{placeholder}` collapses
     to one segment. So `01` §5.1's `/api/v1/dataset-versions/{id}/lineage?direction=up|down`
     (`01` §5.1, the lineage row) matches the live `/api/v1/dataset-versions/{version_id}/lineage`.
   - **One shared row parser, `packages/model-schema/src/model_schema/table_rows.py`,
     stdlib-only. It replaces every markdown-table row split in the repository, and it reads
     the escaped pipe.** *(Restated on the maintainer's entry "11:49:44 BST — DECISION: the
     shared row parser is route (a), a stdlib-only module file; this amends my 11:46:58
     'model-schema helper'". It supersedes this bullet's earlier rule of "one regex change
     to both parsers, never a third". That rule missed the backend's copy, and it left the
     row splits outside §5.1 in place. The finding is #983, working id 9894, MEDIUM, owned by
     this slice, cited in prose until minted.)*
     - **The defect (measured).** Every copy captures the path cell with `([^|]+)`, so an
       escaped `\|` ends the capture. At `daa7f5f8`, three path cells carry one: `01:873`
       (`…/lineage?direction=up\|down`), `06:539` (`…?format=html\|pdf\|bundle`) and
       `06:543` (`…/dependencies?direction=up\|down`). Measured at `d15d4c8f` by loading
       `scripts/scope-audit.py` by path: `declared_endpoints("DATA")` is 39 and
       `declared_endpoints("GOV")` is 23. With the path cell `((?:\\\||[^|])+)` substituted,
       they are 40 and 25. Two more rows carry an escaped pipe in the Purpose cell
       (`01:866`, `02:1784`), where a naive split would misplace the new `Permission` cell.
     - **Rewriting the cells is rejected.** `\|` is the markdown-correct way to write a pipe
       inside a cell, it occurs in five rows, and a later row would bring it back.
     - **Why a module file, and why stdlib-only.** `docs.yml` runs the scripts under bare
       `setup-python` (`python3 scripts/audit-docs.py` at `docs.yml:68`, `doc-id.py check`
       at `:76`, `doc-index.py --check` at `:80`), with no packages and no pydantic. So:
       - **the scripts load `table_rows.py` by path** with `importlib.util`, as
         `audit-docs.py` already loads `register-lint.py` (`_load_register_lint`, `:261`).
         The path resolves from the loading script's own `__file__`, never from the working
         directory. A script loaded inside a `doc-id.py migrate --verify` snapshot then
         reads that snapshot's `table_rows.py`, not the live tree's. It writes no bytecode
         into the snapshot, as `audit-docs.py`'s `_load_module` (`:1232`) already
         ensures by setting `sys.dont_write_bytecode` around the load (`:1252-1257`);
       - **the backend imports it normally** (`from model_schema.table_rows import …`),
         which the `.importlinter` layering already allows;
       - **`docs.yml` is unchanged.** Route (b), installing `model-schema` in `docs.yml`, is
         rejected by the same entry.
     - **What it owns:** the row split, on unescaped pipes only, with `\|` kept inside its
       cell. `register-lint.py`'s `_split_row` (`:165`) is the model and becomes a caller.
       It also owns the §5.1 endpoint-row reading (the method cell and the path cell) built
       on that split. Callers keep their own meaning for each cell. What the module owns is
       only how a row becomes cells.
     - **Every row split migrates, and "never a fourth" means the row-split logic.**
       *(Widened on auditor-926-927's audit of `142c4594`. The previous head's four
       fixed-string predicates missed the first-cell splits `doc-id.py:2921` and
       `tests/test_doc_id_migrate.py:4951`, and any `partition`, `rsplit`, single-quoted or
       `[^|]*` form.)* The population is defined by four regexes, which are also the pin's.
       Each is matched against every tracked `*.py`, with the vendored
       `.claude/skills/ui-ux-pro-max/` excluded. Those files split CSV alias fields, not
       markdown rows, and vendored files stay as upstream wrote them (`CLAUDE.md` §12).
       - **P1, a string-method split on a pipe:** the ERE
         `(split|rsplit|partition|rpartition)\(\s*[rb]?['"]\\?\|['"]`. At `d15d4c8f` it
         has 11 hits:
         - `audit-docs.py:353`, `:394`, `:578` and `:4118`;
         - `doc-index.py:1061`;
         - `_docid.py:1611`;
         - `doc-id.py:2921` (with its `.strip("|")` at `:2920`);
         - `register-lint.py:169`;
         - `backend/src/app/demo/guide.py:87`;
         - `tests/test_findings_ids.py:157`;
         - `tests/test_doc_id_migrate.py:4951`.
       - **P2, a negated pipe class, `[^|` in any form:** the ERE `\[\^\|`. It has 6 hits:
         - the three §5.1 endpoint regexes, `audit-docs.py:299`, `scope-audit.py:68` and
           `guide.py:64`;
         - the first-cell id matchers `doc-index.py:461` (`_BOLD_ID_ROW`) and
           `scripts/graphify-docs-extract.py:41` (`OQ_DEF`);
         - the comment at `doc-index.py:458`.
       - **P3, the unescaped-pipe lookbehind:** the fixed string `(?<!\\)\|`. It has 6 hits:
         - `audit-docs.py:636` (check 22's cell count) and `:642`;
         - `doc-index.py:477` (`_UNESCAPED_PIPE`, used at `:557`);
         - `register-lint.py:126` (used at `:309`);
         - `tests/test_audit_docs_ids.py:2413` and `:2462`.
       - **P4, the retired name:** the ERE `\b_split_row\b`. `register-lint.py`'s
         `_split_row` (`:165`, called at `:242` and `:267`) is **deleted**, not kept as a
         wrapper. Its callers, and `doc-id.py:3202` with its docstring at `:3185-3189`, call
         `table_rows` directly, so this predicate reaches zero.

       Every hit migrates to `table_rows`, except the pin's exemptions below. The hit lists
       above were reproduced at this ruling by compiling each pattern with Python's `re`
       (P3 escaped with `re.escape`) and matching it line by line over
       `git ls-files '*.py'`, minus the vendored directory. That form is used because P1
       contains both quote characters, which a shell-quoted `git grep` would mangle. Each
       migrated
       site is read at the slice, and a site the slice finds is not a markdown-row split is
       named in its record, not silently left. **Outside the predicates, and staying:**
       `audit-docs.py:508` and `:3965` match two-cell `| **key** | value |` rows anchored at
       both ends, so a `\|` in the value cell is read as part of the value. They are not
       splits.
     - **`doc-index.py --phase P2` is carried by this slice.** Its register split at
       `doc-index.py:1061` raises on the register rows that carry `\|` (#983 reports `:197`
       and `:213`). It is one of the population above, fixed by the same splitter, and so
       fixed before the P2 exit review. The default `--check` does not call it.
     - **A static test pins the population at zero.** P1 to P4 match nowhere outside
       three exemptions, and **no exemption is a whole file except the owner and the pin**:
       - `table_rows.py`, the owner;
       - the pin's own test file, which holds the four predicates as data;
       - one line-level exemption, keyed by `(path, enclosing function, the exact source
         text of the string literal)`, never by line number: `audit-docs.py`'s
         `check_table_rows` (`:604`), the literal at `:642`. That is check 22's lint for a
         raw pipe inside a code span. It is a lint, not a split. Its neighbour at `:636`,
         check 22's cell count, **migrates**, so every other split in `audit-docs.py` is
         still caught.

       The pin tokenizes each file and ignores `COMMENT` tokens, so `doc-index.py:458` is
       not a hit. A docstring hit is migrated or reworded.
       - **Red first:** a planted `line.split('|')`, a planted `line.partition("|")`, a
         planted `[^|]*` regex and a planted `def _split_row` each fail it;
       - so does a second `(?<!\\)\|` literal added inside `check_table_rows`.
   - **Two live routes have no row. The spec is behind the code (`CLAUDE.md` §0), and the
     slice adds both rows spec-first** (the 11:37:11 BST entry, item 2). They are
     `GET /api/v1/rating-versions` and `GET /api/v1/rating-versions/{rating_version_id}`
     (`backend/src/app/api/models.py:1113`, `:1139`). `03` §5.1 declares only the `POST`.
     - Each row carries a dated note: "records an existing route, 2026-09-30", and cites the
       row's owner Work. The list read belongs to WK-675 Slice 10 (FD-1283). The by-id read
       belongs to DP-5 of the plan with PL working id 9681.
     - The pin is then green on day one, and the owners' later spec changes amend those
       rows, not add them.
     - **The third route the audit reported already has a row.** `01` §5.1's
       `GET /api/v1/dataset-versions/{id}/lineage?direction=up|down` is the live
       `/api/v1/dataset-versions/{version_id}/lineage`. They differ only in the placeholder
       name and the query string, both of which the comparison above collapses. No row is
       added for it.
4. **The slice that carries it.**
   - **A WK-1178 slice: the column, filled on every row (157 after the split, plus the two added reads), and the pin.** WK-1178 is the
     standing maintenance Work that owns the authorisation sweep's gaps, and the lead cuts
     and dispatches it.
   - **Its first commit is the spec change** (`spec-change`): the seven columns, and the fold
     of `06`'s route table.
   - **Filling each built row's value is evidence, not copying.** Each value is read from
     the route's code, **and** from `06` §4.1's `Governs` text for that permission. Where the
     two disagree, the disagreement is filed as a finding before the row is written, never
     settled by copying the code.
   - **Serialisation (`RL-1263`), stated in full on the maintainer's entry "11:28:39 BST —
     #977 (DP-S2-4 → a) and the #971 delta: accepted in substance, pending audits".** The
     slice edits **every existing row** of the seven §5.1 tables: `01-data-management.md` §5.1 (`:845`), `02-modelling.md` §5.1 (`:1813`), `03-rating-engine.md` §5.1 (`:891`), `04-optimisation.md` §5.1 (`:302`, table header `:304`), `05-monitoring.md` §5.1 (`:276`, header `:278`), `06-governance.md` §5.1 (`:547`) and `07-platform.md` §5.1 (`:303`), headings at origin/main `072c56e1`. *(Restated 2026-10-05 before mint, on the Q1 clarification below and the entry headed "2026-10-05 10:11:16 BST — #977 (RL 9907) item 4: RESTATE …".)* So it
     serialises against **every slice holding any of those sections open**, and at this tree
     those are four:
     - **WK-674 Slice 2** (`03` and `07` §5.1);
     - **the WK-1178 fix slice**;
     - **the #969 slice** (the `??`/FR-244 ruling's WK-1178 code slice);
     - **WK-1250 Slice 1** (`03` §5.1);
     - *(added on auditor-926-927's audit)* **WK-675 Slices 2 and 4** (each new read route
       is spec-changed first, DP-4 (a)), **WK-675 Slice 10** (the list read), **the three
       view slices' backend additions**, and **the fix for finding 1297** (not on `main` at this tree), which edits the code
       catalogue inside `03` §5.1 (`03:772-776`).

     **Its code write-set joins the serialisation** (auditor-926-927's audit of
     `142c4594`). Besides the seven §5.1 tables, the slice edits:
     - `scripts/audit-docs.py`, `scope-audit.py`, `doc-index.py`, `doc-id.py`, `_docid.py`,
       `register-lint.py` and `graphify-docs-extract.py`;
     - `backend/src/app/demo/guide.py`;
     - the new `packages/model-schema/src/model_schema/table_rows.py`;
     - `tests/test_audit_docs_ids.py`, `tests/test_findings_ids.py` and
       `tests/test_doc_id_migrate.py`;
     - its own new test files.

     A slice holding any of those files open is serialised against it like a §5.1 holder.
     The list is re-derived from P1 to P4 and checked again at dispatch, because the
     population can grow before then.

     **The rule, not only the list:** the slice serialises against **every** slice holding
     any of the seven §5.1 sections, **or any file of its code write-set**, open **at its
     dispatch**. The lead's dispatch record
     (`RL-1263`) names them then. It is dispatched in the first gap in which none is in
     flight, and otherwise it yields.
   - **S2's new routes are declared by whichever of S2 and this slice lands second**, as the
     11:17:35 BST entry says. If this slice lands second, it fills S2's rows. If S2 lands
     second, S2 writes its rows with the column, and its sweep pins them.
   - **It lands after #942, and its name check reads #942's tables.** The check reads `06`
     §4.1's Built and Specified tables, which #942's D4 makes machine-readable. At `65b33479`,
     before #942, 15 of the 21 permissions that live `requires()` routes use have no §4.1 row
     (auditor-926-927's measurement; `admin:manage_roles`, for one, appears only in FR-348
     and FR-360). So this slice is not dispatched before #942 is merged.
   - **Known future §5.1 holders**, named so the lead can plan the gap: WK-675 Slices 2, 4
     and 10.
5. **Every row, now and later, carries a cell.** The slice declares every §5.1 row at its
   tree. Its test then **fails on any §5.1 row, built or unbuilt, whose `Permission` cell is
   missing or empty**, so a later slice that appends a row cannot omit it. Check 22's
   cell-count rule also fails a row with too few cells, but only under `docs.yml`. The test
   runs under `python.yml` on every side (#942's D2).

## What it obliges

- **This commit:** this record only. The finding #983 (working id 9894) is carried by the
  WK-1178 slice of item 4, including `doc-index.py --phase P2`.
- **The leaf plan (PL working id 9920, the planner's file, not edited here):** DP-S2-4's
  "Resolved by" cell cites this record once it is minted. Task 0A step (c) is carried by the
  WK-1178 slice of item 4, and not by Slice 2.
- **The lead:** cuts that WK-1178 slice and places it in the serial order of item 4.

## Acceptance — the violation that must become detectable

Each is shown failing on deliberately broken input (`CLAUDE.md` §13), in the WK-1178 slice:
- **The leaf plan's red case:** on a scratch copy, `ReadAudit` is switched from
  `Permission.AUDIT_READ` to `Permission.JOB_READ` (`api/audit.py:52`). The pin fails,
  naming the audit routes.
- A live route with no §5.1 row, or with an empty `Permission` cell, fails.
- **Any §5.1 row with a missing or empty `Permission` cell fails, built or unbuilt**, shown on a
  planted appended row with no cell (item 5).
- A handler-checked route (the deploy route of #971 B.2) whose handler's `permission=`
  differs from its row fails, although it carries no `PERMISSION_ATTRIBUTE`.
- A cell naming a permission in neither of `06` §4.1's Built and Specified tables fails.
- After the split, `PUT /settings` declared `settings:read` fails, and so does any split row
  whose permission differs from its method's check.
- **Escaped pipes are read, through one shared parser** (item 3's `table_rows` bullet):
  - `declared_endpoints("DATA")` counts 40 and `declared_endpoints("GOV")` counts 25, up
    from 39 and 23. The `01:873`, `06:539` and `06:543` rows are read with their full
    paths;
  - a planted row with `\|` in its path cell is read identically by all three consumers:
    `audit-docs.py`, `scope-audit.py` and `backend/src/app/demo/guide.py`;
  - a row whose Purpose cell holds `\|` (`01:866`) still yields its correct `Permission`
    cell;
  - with the old `([^|]+)` restored, the DATA and GOV counts fall back and the case fails;
  - `doc-index.py --phase P2` completes on the live register;
  - a test fails if `table_rows.py` imports any module outside `sys.stdlib_module_names`.
    Red first: a planted `import pydantic`;
  - `audit-docs.py` is proven to run under a bare Python, with no project packages
    installed. For example, `python3 -I -S scripts/audit-docs.py` exits as it does under
    the venv. At `d15d4c8f` it does: system Python 3.13.5 under `-I -S` gave rc 1, with
    only check 31's working-id gap;
  - the static population test of item 3 fails on each of its planted forms, and
    `git grep -n -F '_split_row' -- '*.py'` prints nothing.
- A live route with no row fails. The two rating-version reads pass through their
  "records an existing route" rows.
- A route declared `authenticated` that in fact demands a permission, or the reverse, fails.
- Check 22 passes on all five tables after the migration: the header and every row carry
  four cells.

## Amendment, 2026-10-01 10:18 BST: F-A3 and the F-A2 drift note

*By the decision-maker session `dm-675dp56` (effort `medium`; `CLAUDE_EFFORT=medium`), on the
lead's relay of the maintainer's instruction: "#977 waits for a DM-dated line (F-A3; medium;
can share a small session)". The branch was merged with origin/main `1dd5e264`. Nothing ruled
above is changed. This section adds one population member (F-A3) and records drift (F-A2).*

**F-A3: a new P1 hit from #1049.** #1049 (SL-1360, draft) adds
`tests/test_permission_parity.py`. Its line 62 splits a markdown row of `06` §4.1 on a bare
pipe:

```text
rows.append([cell.strip() for cell in line.strip("|").split("|")])
```

The line is a member of item 3's population.
- **When #1049 merges, the WK-1178 pin slice migrates that line to `table_rows`.**
- `tests/test_permission_parity.py` joins the code write-set and its serialisation list. Like
  every other entry, that list is re-checked at dispatch.
- If #1049 has not merged at the slice's dispatch, the file is not in the slice's tree. The
  dispatch-time re-derivation then finds it whenever it lands.

P1 was re-run on #1049's head `9a79c9c6` (`9a79c9c639d3ad90ecf3fd5339f1b26fe53d3399`). The
form is the one item 3 states: the ERE compiled with Python's `re` and matched line by line
over `git ls-tree -r --name-only` `*.py` at that commit, minus `.claude/skills/ui-ux-pro-max/`.
The output, verbatim:

```text
backend/src/app/demo/guide.py:87: return [cell.strip() for cell in line.strip().strip("|").split("|")]
scripts/_docid.py:1611: cells = [c.strip() for c in line.strip("|").split("|")]
scripts/audit-docs.py:353: cells = [c.strip() for c in line.strip().strip("|").split("|")]
scripts/audit-docs.py:394: cells = [c.strip() for c in line.strip().strip("|").split("|")]
scripts/audit-docs.py:578: cells = [c.strip() for c in line.strip().strip("|").split("|")]
scripts/audit-docs.py:4122: cells = [c.strip() for c in line.strip().strip("|").split("|")]
scripts/doc-id.py:2921: title = row_match.group(4).split("|", 1)[0].strip()
scripts/doc-index.py:1061: cells = [c.strip() for c in line.strip().strip("|").split("|")]
scripts/register-lint.py:169: fields = [f.strip() for f in tmp.strip().strip("|").split("|")]
tests/test_doc_id_migrate.py:4951: cell = line[1:].split("|", 1)[0].strip()
tests/test_findings_ids.py:157: seen += _CITED_ID.findall(line.split("|")[1])
tests/test_permission_parity.py:62: rows.append([cell.strip() for cell in line.strip("|").split("|")])
COUNT 12
```

At origin/main `1dd5e264` the same predicate gives 11 hits: the same lines without
`test_permission_parity.py:62`. One of item 3's locators has drifted. `audit-docs.py:4118` is
now `:4122`, with the same source text.

**F-A2: drift only.** The population is re-derived at dispatch (item 4), so this records
the movement and rules nothing. The predicate: in each of the five specs, the lines from
`### 5.1` up to the next `##`/`###` heading that match the Python regex
``^\| `?(GET|POST|PUT|PATCH|DELETE)``. A blockquoted table starts with `>`, so it is not
counted. Results at origin/main `1dd5e264`:

| Spec | §5.1 heading line | Rows | Multi-method rows |
|---|---|---|---|
| `01` | `:845` | 39 | 1 |
| `02` | `:1805` | 44 | 0 |
| `03` | `:775` | 30 (was 26; WK-1250 Slice 1's four sub-graph rows) | 0 |
| `06` | `:529` | 23 | 2 |
| `07` | `:297` | 20 | 2 |
| **Total** | | **156** (was 152) | **5** |

- **After the split: 161 rows. With the two added reads: 163** (they were 157 and 159).
- The same predicate at this record's tree `65b33479` gives 152, the figure ruled above.
- `06`'s blockquoted `| Route | Requires |` table is now at `06:551`.
- These counts agree with the lead's relay.

**An overlap to resolve before mint (not ruled here).** RL 9766 (working id; #1055, PL-1286
DP-5) also adds a §5.1 row for the existing `GET /api/v1/rating-versions/{id}`, the same route
as item 4's added read `GET /api/v1/rating-versions/{rating_version_id}`. Whichever of the two
lands second must not add a second row for it. The lead orders the two, and the
decision-maker amends the second record's text to match.

## Amendment, 2026-10-01 10:28 BST: the by-id row's exact text, and WK-675 Slices 2 and 3 in item 4's list (F-2, F-3)

*By the decision-maker session `dm-675dp56` (effort `medium`), on the lead's order of
2026-10-01 10:27 BST after auditor-1055's scoped re-check of #1055. This **resolves the
10:18 BST amendment's "overlap to resolve before mint"**. Nothing ruled above is changed.*

- **F-2: the by-id read of item 3 is satisfied by RL 9766 (working id) T2's by-id row,
  verbatim.** This record describes the two added reads under item 3 and gives no row text.
  RL 9766's T2 carries the one exact text for `GET /api/v1/rating-versions/{id}`, the live
  `/rating-versions/{rating_version_id}`, in a three-cell and a four-cell form. This slice
  applies the four-cell form, because it lands the `Permission` column. Whichever of
  WK-675 Slice 2 and this record's WK-1178 slice applies first adds the row, and the other
  adds nothing. The list read, `GET /api/v1/rating-versions`, is unaffected: it is still
  described here and owned by WK-675 Slice 10.
- **F-3: WK-675 Slices 2 and 3 join item 4's serialisation and contention list.** Slice 2
  adds RL 9766 (working id)'s rows, and Slice 3 adds RL 9767 (working id)'s validate row,
  both to `03` §5.1. If this record's slice lands second, it fills the `Permission` cell
  of any row already added: `rating:read` for RL 9766's rows and `rating:write` for RL
  9767's row, as those records' four-cell forms give them. If it lands first, those slices
  apply their four-cell forms.

## Amendment, 2026-10-01 10:36 BST: the note's exact phrase, and the mint stop (G1, G2, G3)

*By the decision-maker session `dm-675dp56` (effort `medium`), on auditor-1055's
side-by-side re-check, as the lead relayed it at 10:35 BST. Nothing ruled above is changed.*

- **G1: the phrase is exact.** Item 3's note, "records an existing route, 2026-09-30", is
  matched exactly: lower case, with the fixed date 2026-09-30. RL 9766 (working id) T2's
  by-id row now carries it byte for byte ("…; records an existing route, 2026-09-30;
  declared <date> …"). So the acceptance check that passes the reads "through their
  'records an existing route' rows" needs no case-insensitive or any-date matching.
- **G2: the mint stop.** RL 9766's row cites `RL-<this>`, RL 9766's own minted id. Either
  applier needs that record minted, and an unminted record is a stop. This binds this
  record's WK-1178 slice exactly as it binds WK-675 Slice 2.
- **G3: the list is extended.** Item 4's list of known §5.1 holders (`:251`, `:283-284`:
  WK-675 Slices 2, 4 and 10) is extended by the 10:28 BST amendment to include WK-675
  Slice 3.

## Amended 2026-10-05 before mint: currency at origin/main `47d770e8`

*By the decision-maker session `dm-amend` (effort `medium`), on the lead's brief of
2026-10-05 09:55 BST. Citation and currency only: nothing ruled above is changed. Every
fact below was re-read at origin/main `47d770e8fcbd2410fa101019ed8cf3aae69a1baa`. The
`tree:` field stays `65b33479`, because the figures and line cites in the body above ("at
this tree") were measured there and stay true there; this section carries their values at
`47d770e8`.*

- **H1: the five §5.1 table headers have moved.** Each is still `\| Method \| Path \|
  Purpose \|`, found by `grep -n -E '^\| *Method *\| *Path' docs/specs/0*.md`:
  `01-data-management.md:847` (unchanged), `02-modelling.md:1815` (was `:1759`),
  `03-rating-engine.md:893` (was `:742`), `06-governance.md:538` (was `:494`) and
  `07-platform.md:305` (was `:299`). No §5.1 table has a `Permission` column, and no file
  under `docs/contracts/` contains `x-permission`.
- **H2: row counts.** With F-A2's predicate (the lines from `### 5.1` up to the next
  `##`/`###` heading that match ``^\| `?(GET|POST|PUT|PATCH|DELETE)``):

  | Spec | §5.1 heading line | Rows | Multi-method rows |
  |---|---|---|---|
  | `01` | `:845` | 39 | 1 |
  | `02` | `:1813` | 44 | 0 |
  | `03` | `:891` | 32 | 0 |
  | `06` | `:536` | 23 | 2 |
  | `07` | `:303` | 22 | 2 |
  | **Total** | | **160** (152 at `65b33479`; 156 at `1dd5e264`) | **5** |

  The population is re-derived at dispatch (item 4), so this records movement and rules
  nothing. `06`'s blockquoted `| Route | Requires |` table is now at `06:558`.
- **H3: the three parsers are unchanged.** `_ENDPOINT_ROW` is at `scripts/audit-docs.py:299`,
  `_ENDPOINT` at `scripts/scope-audit.py:68` and `_SPEC_ENDPOINT` at
  `backend/src/app/demo/guide.py:64`; each still captures the path cell with `([^|]+)`.
  `scripts/table_rows.py` does not exist yet. `PERMISSION_ATTRIBUTE` is defined at
  `backend/src/app/api/authz.py:41`.
- **H4: the flattened sweep has landed.** Item 3's "with the included routers flattened"
  now exists on `main`: `_flattened_operations` (`backend/tests/test_api_authorisation_sweep.py:108`)
  descends each include's `original_router`, merged by `dfddfad8` (#1104, SL-1256). The pin
  this record rules (the spec-declared permission compared with the route's) is not part of
  #1104 and is still undone.
- **H5: `04` and `05` also have §5.1 tables.** `04-optimisation.md:304` and
  `05-monitoring.md:278` are `\| Method \| Path \| Purpose \|` headers, with 10 and 16 rows
  by H2's predicate. Both tables already existed at `65b33479` (same lines). This record
  names five tables (item 1) and does not say whether these two are in or out of scope.
  **That is a scope question, not a citation fix, and it is not decided here**; it is
  raised to the lead.

## Clarified 2026-10-05 before mint: `04` and `05` §5.1 are in scope (H5's question)

*By the decision-maker session `dm-premint` (effort `medium`), on the lead's brief of
2026-10-05 10:08 BST. This section rules nothing: it records the maintainer's ruling, by
delegation, from `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed
"2026-10-05 09:59:49 BST — A10 early ACCEPTED (start when dm-9718 reports, about 10:10, solo 30 min); RL 9907 Q1 RULED "in scope"; PL 9728 DP-6 RULED (b) with a binding condition. Both ruled by me (the maintainer, by delegation), so no DM is needed". Its RL 9907 bullet, verbatim:*

- **RL 9907 Q1 (#977, pre-merge), RULED: the 04 (:304, 10 rows) and 05 (:278, 16 rows) §5.1 tables are IN SCOPE.** Reason: item 5's own text ("fails on any §5.1 row") governs. A permission test that skips two modules' tables passes vacuously, the class FD 9988 files. Item 1's list of five tables is read as examples, not an exhaustive set. Recorded as a dated clarification section in #977 before its mint, citing this header; the ruling's other substance is unchanged.

- **What it settles.** H5's question is closed: `04-optimisation.md` §5.1 (header `:304`) and
  `05-monitoring.md` §5.1 (header `:278`) are covered. Item 5's "fails on any §5.1 row"
  governs, and item 1's list of five tables (`01`, `02`, `03`, `06`, `07`) is read as
  examples, not an exhaustive set. The ruling's other substance is unchanged.
- **Where "five" appears above.** The presence table, item 1, item 2's cost bullet, item 4
  (its first-commit bullet, its edit list and its open-PR rule), the Acceptance bullet on
  check 22, the 2026-10-01 10:18 amendment's predicate, and H1–H2 name five tables or five
  specs. They were written before this clarification; read them with `04` and `05`
  included. The counts they give stay true for the five tables they counted. Item 4 is restated for all seven (2026-10-05).
- **Re-verified at origin/main `47d770e8fcbd2410fa101019ed8cf3aae69a1baa`**, by
  `grep -n -E '^\| *Method *\| *Path' docs/specs/0*.md`: `04-optimisation.md:304` and
  `05-monitoring.md:278` are each `\| Method \| Path \| Purpose \|`, under `### 5.1 REST
  API` at `04:302` and `05:276`.
- **Row count, seven tables.** By H2's predicate, verbatim (the lines from `### 5.1` up to
  the next `##`/`###` heading that match ``^\| `?(GET|POST|PUT|PATCH|DELETE)``): `04` has
  10 rows (5 `GET`, 5 `POST`) and `05` has 16 (8 `GET`, 8 `POST`), with no multi-method
  row in either. With H2's 160 for the five tables, the seven §5.1 tables hold **186**
  rows at `47d770e8`, 5 of them multi-method. As H2 says, the population is re-derived at
  dispatch (item 4); this records it and rules nothing.
