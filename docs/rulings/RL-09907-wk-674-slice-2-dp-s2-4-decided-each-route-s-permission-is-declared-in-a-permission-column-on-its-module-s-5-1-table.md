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
| A route-to-permission declaration anywhere | **present, once, for 6 routes** | `06` §5.1 carries a blockquoted `\| Route \| Requires \|` table for its approval routes, "stated 2026-08-15 after an independent audit" (`06-governance.md`, the note after the approval-request rows). Its cells are a permission name or `authenticated`. It is the precedent for (a)'s cell vocabulary. |
| Existing `§5.1` parsers | **present, two, reading only the first two cells** | `audit-docs.py:297` `_ENDPOINT_ROW` and `scope-audit.py:68` `_ENDPOINT` each match `^\|\s*method\s*\|([^\|]+)\|` and ignore the rest of the row. A fourth column breaks neither. Check 22 (`audit-docs.py`, "Every markdown table row has its own header's cell count") requires that the header and every row gain the column in the same commit. |
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

   **Multi-method rows.** Five rows name two methods: `GET`/`PUT` `/datasets/{slug}/rule-set`
   (`01:880`); `GET`/`POST` `/roles` (`06:499`); `GET`/`PUT` `/approval-policy` (`06:502`);
   `GET`/`POST` `/environments` (`07:306`); and `GET`/`PUT` `/settings` (`07:311`). Their cell
   is **per method**, in the form `GET: <value>; PUT: <value>`, each value from the list
   above. A cell with no method prefix applies to every method of its row. Rows are not
   split, so the method and path cells, and both existing parsers' reading of them, are
   unchanged. The rows stay at 152. *(Added on auditor-926-927's audit of `070a83fe`:
   three of the five carry different permissions per method.)*

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
   - **(a)'s cost is one-time.** One migration commit edits five §5.1 tables (152 rows).
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
   parser **reuses** the `_ENDPOINT_ROW`/`_ENDPOINT` row shape, never a third reading of
   these tables.
   - **Paths are compared as `audit-docs.py`'s `_path_segments` compares them:** the
     `/api/v1` prefix and any query string are dropped, and every `{placeholder}` collapses
     to one segment. So `01` §5.1's `/api/v1/dataset-versions/{id}/lineage?direction=up|down`
     (`01` §5.1, the lineage row) matches the live `/api/v1/dataset-versions/{version_id}/lineage`.
   - **Two live routes have no row, owned elsewhere, and are an interim allow-list.**
     `GET /api/v1/rating-versions` and `GET /api/v1/rating-versions/{rating_version_id}`
     (`backend/src/app/api/models.py:1113`, `:1139`) appear in no §5.1. `03` §5.1 declares
     only the `POST`. Their rows are other Works' spec changes: FD-1283 makes the list read
     a WK-675 Slice 10 spec change, and the by-id read is DP-5 of the plan with PL working id 9681. This slice
     does not write them. It carries exactly these two, named, dated 2026-09-30,
     shrink-only, each citing its owner, and each owner's commit removes its entry red
     first by adding the row.
4. **The slice that carries it.**
   - **A WK-1178 slice: the column, filled for all 152 rows, and the pin.** WK-1178 is the
     standing maintenance Work that owns the authorisation sweep's gaps, and the lead cuts
     and dispatches it.
   - **Its first commit is the spec change** (`spec-change`): the five columns, and the fold
     of `06`'s route table.
   - **Filling each built row's value is evidence, not copying.** Each value is read from
     the route's code, **and** from `06` §4.1's `Governs` text for that permission. Where the
     two disagree, the disagreement is filed as a finding before the row is written, never
     settled by copying the code.
   - **Serialisation (`RL-1263`), stated in full on the maintainer's entry "11:28:39 BST —
     #977 (DP-S2-4 → a) and the #971 delta: accepted in substance, pending audits".** The
     slice edits **every existing row** of `01`, `02`, `03`, `06` and `07` §5.1. So it
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

     **The rule, not only the list:** the slice serialises against **every** slice holding
     any of the five §5.1 sections open **at its dispatch**. The lead's dispatch record
     (`RL-1263`) names them then. It is dispatched in the first gap in which none is in
     flight, and otherwise it yields.
   - **S2's new routes are declared by whichever of S2 and this slice lands second**, as the
     11:17:35 BST entry says. If this slice lands second, it fills S2's rows. If S2 lands
     second, S2 writes its rows with the column, and its sweep pins them.
   - **It lands after #942.** The name check reads `06` §4.1's Built and Specified tables,
     which #942's D4 makes machine-readable. So this slice is not dispatched before #942 is
     merged.
5. **Every row, now and later, carries a cell.** The slice declares every §5.1 row at its
   tree. Its test then **fails on any §5.1 row, built or unbuilt, whose `Permission` cell is
   missing or empty**, so a later slice that appends a row cannot omit it. Check 22's
   cell-count rule also fails a row with too few cells, but only under `docs.yml`. The test
   runs under `python.yml` on every side (#942's D2).

## What it obliges

- **This commit:** this record only.
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
- A multi-method row whose per-method cell omits a method, or names the wrong permission for
  one method, fails. So `GET: settings:read; PUT: settings:read` fails on `/settings`.
- A third live route with no row fails. The two allow-listed reads pass until their owners
  add their rows.
- A route declared `authenticated` that in fact demands a permission, or the reverse, fails.
- Check 22 passes on all five tables after the migration: the header and every row carry
  four cells.
