---
id: PL-1368
family: plan
kind: leaf
title: WK-675 Slice 1 — ChartFigure's accessible table per RL-1307, its 13 call sites migrated, and F39's socket diagnosis: leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-01
owner: planner
tree: 1dd5e264195677b4a13268b80ac8673c2c027135
phase: P2
work: WK-675
slice: SL-1369
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-1369, PL-1286, RL-1307, RL-1184, RL-1263, PL-1268, PL-803, CR-1212, NFR-463, SL-1275]
---

# PL-1368 — WK-675 Slice 1 — ChartFigure's accessible table per RL-1307, its 13 call sites migrated, and F39's socket diagnosis: leaf plan

The leaf plan for slice row **SL-1369**. Drafted as working id 9769; minted 2026-10-01 as
PL-1368. The slice row was drafted as working id 9768 and minted the same day as SL-1369.
Both ids were allocated by the lead, the only allocator, in merge order at `origin/main`
`92b4e4ac`. Minting does not activate: `status:` stays `draft` until the activation PR.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `test-driven-development` (every red-first
> step), `vue-frontend` and `vue-best-practices` (every component task),
> `vue-testing-best-practices` (every test), `dev-commands` (the gate, the gate slot and the
> build), `git-hygiene`, and `systematic-debugging` (Task 1, F39). It reads
> [`README.md`](README.md)'s five unchecked conventions before its first step. The executor is
> spawned from `.claude/roles/executor.md`, whose Model / effort line it quotes verbatim.

## Goal

Make `ChartFigure`'s accessible table unable to show a value under a heading it does not
belong to, as `RL-1307` rules: the component becomes generic over the caller's own row
objects, and each column carries its own accessor. All 13 existing call sites move to the new
API in this slice, before WK-675's first new chart (S6) and WK-690 Slice 5's loss-curve
preview add more. The same slice diagnoses register row **F39**: what opens a TCP connection
to port 3000 during `pnpm --dir frontend test`.

**Architecture.** `ChartFigure.vue` takes `<script setup lang="ts" generic="T">`,
`rows: readonly T[]` and `columns: readonly Column<T>[]`. The `Cell` and `Column` types live in
a new plain module, `frontend/src/chart-table.ts`, which callers import. Each cell renders as
`column.value(row)`; the first column's cells render as `<th scope="row">`. The dev-only arity
guard is deleted. A duplicate-key refusal that runs in **every build** replaces it: the figure
shows a visible error in place of its table, and never renders a table with colliding keys. Type-level refusals are
held in the gate by fixture components under `frontend/src/components/__typecheck__/`, each
marked `<!-- @vue-expect-error -->`. `vue-tsc` fails if the marked error stops occurring.
Runtime behaviour is tested in vitest. The 13 call sites are rewritten in three groups,
simplest first. F39 is diagnosed by locating the test file that opens the socket, and is
then remedied in the test layer if the cause is there.

**Tech Stack:** Vue 3.5 (`<script setup lang="ts">` only), TypeScript 5.9, `vue-tsc` 3.3
(`pnpm --dir frontend type-check` is `vue-tsc --build --force`, `frontend/package.json:14`),
vitest 4 with happy-dom (`frontend/vitest.config.ts`), `@testing-library/vue`, ECharts through
`vue-echarts`. **No new dependency:** neither `frontend/package.json` nor
`frontend/pnpm-lock.yaml` changes. No backend, `model-schema` or `docs/contracts/` change.
`ChartFigure` has no backend counterpart, so `CLAUDE.md` §2's no-second-shape rule does not
bind its props (`RL-1307`, "Callers").

**Spec:**
- [`../rulings/RL-01307-oq-550-decided-chartfigure-takes-column-descriptors-that-read-each-cell-from-the-caller-s-own-row.md`](../rulings/RL-01307-oq-550-decided-chartfigure-takes-column-descriptors-that-read-each-cell-from-the-caller-s-own-row.md)
  in full. It is this slice's authority (quoted below).
- [`../specs/00-overview.md`](../specs/00-overview.md) **NFR-463** (`00:530`), with its
  2026-09-30 dated clause naming `RL-1307`; **FR-10** and **FR-21** (money is never a float).
  An accessor formats money; this slice changes no formatting.
- [`PL-1286`](PL-01286-wk-675-frontend-dag-designer-rate-table-editor-quote-sandbox-and-dislocation-views-map-plan.md),
  the map plan: its S1 row (`:303`), the F39 carried obligation (`:285-286`), Acceptance items
  5, 7, 9 and 10 (`:124-126`, `:128-130`, `:134-136`, `:137-138`), Sequencing (`:368-370`),
  and the contention row for S1 (`:406`).
- [`../findings/register.md`](../findings/register.md) row **F39** (`:81`).

### `PL-1286` is stale on DP-1, and `RL-1307` governs

`PL-1286` was written before `RL-1307` and is frozen, so it is not edited here. Three passages
in it still describe DP-1 (OQ-550) as **open** and recommend option **(b)**:
- the DP-1 row of its Decision points table (`:240`): "Recommendation **(b).**";
- the freeze paragraph (`:248-250`): "**DP-1 is open, and it is the decision-maker's**";
- its Status section (`:415-416`): "It stays `draft` while DP-1 (OQ-550, the
  decision-maker's, #936) or any other open DP has no resolver".

**`RL-1307` ruled option (c)** on 2026-09-30, and OQ-550 is closed in both mirrors
(`docs/open-questions.md:41`, `00:553`). Where `PL-1286` and this plan differ on DP-1, this
plan and `RL-1307` govern. The maintainer's line for S1's dispatch record says the same
(handover holds file, 2026-10-01, "WK-675 S1 dispatch-record line"): those three passages are
superseded by `RL-1307` (c), `PL-1286` stays `draft` under its own rule, and leaf plans
activate individually. `PL-1286` Acceptance item 5 already defers to the ruling ("in the form
DP-1 rules"), so it needs no correction.

## What `RL-1307` rules, quoted verbatim

From `RL-1307` §Ruled (`:262-303`). Items 1, 3, 4 and 5 are this slice's scope ("What it
obliges": "WK-675 Slice 1 (`PL-1286` S1): items 1, 3, 4 (including `cellUnder`'s stale text)
and 5 above, with all 13 call sites migrated").

> **Option (c), in the descriptor form `{ key, label, value }`.**
>
> 1. **The API.** `ChartFigure` becomes a generic component (`<script setup lang="ts"
>    generic="T">`). It takes `rows: readonly T[]`, the caller's own row objects, and
>    `columns: readonly Column<T>[]`, where a column is `{ key: string; label: string; value:
>    (row: T) => Cell }` and `Cell` is `string | number | null`, as today. The table renders
>    each cell as `column.value(row)`. `title` and `caption` are unchanged.

> 3. **`key` and `label` are separate, the (b′) half.** The register's (c) wrote `{ name, value
>    }`. A single `name` would be both the heading text and the Vue `:key`, which keeps the
>    present collision where two equal headings share a key. `label` is display text, free to
>    change; `key` is an identifier, unique within a figure.
> 4. **The two W6b-9 checks — each kept or retired, with its reason** (`CLAUDE.md` §13):
>    - **The dev-only arity guard retires, by construction.** Every row renders exactly one
>      cell per column, so the class it caught (a row of the wrong length) can no longer be
>      written. Its replacement check is the type-check failure above, which is stronger:
>      it runs in the gate. `pnpm --dir frontend type-check` is `vue-tsc --build --force`, which
>      the frontend workflow runs, and runs C and D show that mode refusing the broken callers
>      and passing the correct one. The dev guard ran only in development.
>    - **`cellUnder` stays.** It still reads hand-written tables (for example
>      `DatasetListView`), and it is **the column-by-name reader** `PL-1286` acceptance item 5
>      names: each new chart's table is asserted under test by reading cells under their
>      `label`. **S1 updates its text**, because three statements in
>      `frontend/src/test-tables.ts` go stale once the guard retires and S1 renders
>      `<th scope="row">`: the thrown message's clause "…the arity failure ChartFigure's own
>      guard should have caught first" (`:44-46`); the docstring's DOM-order explanation that
>      "a `ChartFigure` row is all `<td>`" (`:18-21`); and the module docstring's description of
>      `columns` and `rows` as "two independent props with no relation enforced between them"
>      (`:10-13`). Its lookup by DOM order within the row stays correct for both shapes.
> 5. **Slice 1's scope, beyond the API** (`PL-1286` S1). The same slice (i) keys each `<th>`
>    and `<td>` by the descriptor's `key` and refuses a duplicated `key` within one figure; (ii)
>    renders the first column's cells as `<th scope="row">`, so each row is named for assistive
>    technology (NFR-463); (iii) replaces the empty-state text "diagnostic" with wording that
>    does not name one module, since rating views will use the component.

`RL-1307` §Acceptance (`:330-341`), the four violations, each shown red on deliberately broken
input:

> The violation: **a `ChartFigure` table shows a value under a heading it does not belong
> to.** Slice 1 carries the checks, each shown red on deliberately broken input:
> - *Violation:* a call site's accessor reads a field the row type does not have, or returns a
>   non-cell value. `pnpm --dir frontend type-check` fails. A deliberately broken fixture
>   call site proves it, as the spike's `BadAccessor` and `BadCellType` do.
> - *Violation:* columns written for one row type are passed with rows of another.
>   `type-check` fails (the spike's `Mismatch`).
> - *Violation:* two columns in one figure share a `key`. Refused, under test.
> - *Violation:* a new WK-675 chart's table differs from its chart. Its test reads each cell
>   with `cellUnder` by `label` and compares it with the chart's source data.

The fourth violation binds **new** WK-675 charts (S6 onwards). S1 adds no new chart. S1 does
apply its form, reading cells with `cellUnder` by label, to the three migrated sites that have
no test today (Task 3, Task 5), and to every migrated assertion that read a chart-table cell
by position.

**`RL-1307` left two choices open** ("Not ruled here. The migration order of the 13 sites
inside S1, and the exact empty-state wording: both are S1's"). This plan makes them, with
reasons, under *Choices this plan makes*.

## Status

`draft`. This plan has no open blocking decision point: DP-1 is resolved by `RL-1307`, and
the plan makes the other choices itself. It stays `draft` until its **Activation needs** are
met in a separate activation PR.

## Activation needs

Each is met before the lead dispatches S1. The activation is its own PR, not this one.

1. **The maintainer's agreement** to this leaf plan, as a dated line.
2. **The lead's go**, recorded in the activation PR. That PR sets this plan `active` and
   SL-1369 `active` at dispatch. The ids were minted in #1058 (PL-1368, SL-1369); minting did
   not activate.
3. **S1's dispatch record carries the maintainer's line** (handover holds file, 2026-10-01,
   "WK-675 S1 dispatch-record line"): `PL-1286` `:240`, `:249-250` and `:415-416` (DP-1 open,
   recommending (b)) are superseded by `RL-1307` (c).
4. **The holds are read at dispatch** (handover holds file, 2026-10-01). Two holds name WK-675,
   and **neither applies to S1**, because S1 calls no route. It changes Vue components, their
   tests, `frontend/src/test-tables.ts`, and possibly `frontend/src/test-setup.ts`; it adds no
   API call and no `frontend/src/api/` function:
   - the **FD 9779 (working id) per-route hold** covers a WK-675 slice that calls one of five
     POST routes (`seed-from-model`, `bulk-operation`, `POST /rating-algorithms`,
     `POST /sub-graphs`, `POST /sub-graphs/{slug}/versions`). S1 calls none of them;
   - the **FD-1335 `/score` hold** covers WK-675 slices that consume `/score` or
     `/score/compare` (S6, S7, S7b). S1 consumes neither.
   The F39 remedy (Task 1) makes an unstubbed `fetch` in a test fail; it adds no call.
5. **A free lane under `RL-1263`** (at most two build slices at once, from different Works,
   each holding a gate slot, no shared files). See *Concurrency*.
6. **Task 0's re-measurement** of the call-site count at the dispatch tree. If WK-690 Slice 5
   (SL-1275) has merged first, its caller is the fourteenth site and S1 migrates it too
   (`RL-1307` item 7; `PL-1286` `:406`).

## Choices this plan makes

These are the planner's choices on method, inside what `RL-1307` rules. None changes what
`RL-1307` decided. The decision-maker may overrule any of them by an `RL-` before dispatch.

1. **The migration order** (`RL-1307` leaves it open). Three groups, after the component
   itself:
   - **Group A, Task 3** (7 sites, static columns; six already map over one row object per
     row, and `LineageGraph` builds tuple arrays, so it gets a component-local row interface):
     `GbmEvalCurveChart`, `CrossValidationPanel` (2), `GbmImportanceCharts` (2),
     `PartialDependencePanel`, `LineageGraph`.
   - **Group B, Task 4** (3 sites, a column present or absent at run time, or formatted
     cells): `HistogramChart`, `DoubleLiftChart`, `OneWayChart`.
   - **Group C, Task 5** (3 sites, columns generated per partition): `AeByFactorChart`,
     `CalibrationChart`, `LiftChart`.

   *Reasons.* (i) The simplest sites first fix the pattern before the harder ones use it.
   (ii) Group C is the only place where keys are generated, so the duplicate-key refusal
   matters most there, and it lands last, when the component and its test are settled. (iii)
   The three sites with **no test file today** (`CalibrationChart`, `GbmEvalCurveChart`,
   `LineageGraph`; measured below) each get one in the task that migrates them, so no site is
   rewritten without a check. (iv) The type-check names each unmigrated site, so its error
   list shrinks task by task. That list is each task's progress check.
2. **The empty-state wording** (`RL-1307` leaves it open):
   `No rows — this figure has no data to show.` *Reasons.* It keeps the leading "No rows",
   so the existing assertion `screen.getByText(/no rows/i)` (`ChartFigure.test.ts:54`) still
   reads it. It names no module and no artifact kind. "Diagnostic" and "model" are both
   dropped, so it is true for a rating version's sandbox chart as well as a model's
   diagnostic. No other test or view matches the old text: `git grep -n 'recorded nothing'
   1dd5e264 -- frontend/src` prints only `ChartFigure.vue:128`.
3. **The duplicate-key refusal runs in every build, with no `import.meta.env.DEV` gate.**
   *Revised 2026-10-01 on the maintainer's overrule of this choice, relayed by the lead on
   #1058.* This plan first made the refusal dev-only. The maintainer ruled that this re-creates
   what `RL-1307` removed. `RL-1307` retires the arity guard because it was dev-only ("The
   dev guard ran only in development", `:288`). Item 5 (i) says the slice "refuses a duplicated
   `key` within one figure" (`:300`), and §Acceptance says "Refused, under test" (`:339`).
   So:
   - **In every build**, when two columns share a `key`, `ChartFigure` renders no table and
     no colliding cells. In the table's place it renders a visible error, `role="alert"`. It
     never falls back silently to Vue's last-wins patching. The chart slot still renders.
   - **It does not throw.** A throw from a render would blank the whole page in production.
     A visible error in the figure is the refusal, and it is what a reader and a test can see.
   - **It is tested in the CI frontend run** (`pnpm --dir frontend test`). The test runs twice,
     once as built and once with `vi.stubEnv("DEV", false)`, so a later `DEV` gate fails it.
     It is shown red first with a duplicated key, and the output is pasted (Acceptance 4).
   - **No type-level uniqueness check is added in S1.** One may be added later on top of the
     runtime refusal, never instead of it. Dynamic keys (Task 5) cannot be checked by type.
   Generated keys still use the partition's **index**, not its caption (Task 5), so two
   partitions captioned alike cannot trigger the refusal.
   **The error-state wording is a plan choice:**
   `Table unavailable: two columns in "<title>" share the key "<key>" (<key> | <key> | …).`
   *Reasons.* (i) It says that the accessible table is **missing**. A screen-reader user is
   told that the figure's tabular equivalent is absent, rather than being shown values under
   the wrong headings or nothing at all. `role="alert"` makes it announced. (ii) It names the
   figure, because a page may hold several (`title` is unique per page,
   `ChartFigure.vue:32`). (iii) It names the key and the full key list, so a bug report carries
   the cause without anyone opening developer tools. (iv) It names no module, like the
   empty-state wording (*Choices* 2).
4. **`Cell` and `Column` live in `frontend/src/chart-table.ts`**, not as exports from the SFC.
   *Reasons.* The spike exported them from `<script setup>`, but it ran only `vue-tsc`. A plain
   module is also safe for the Vite build and ESLint, and it follows `frontend/src/test-tables.ts`'s
   placement. `RL-1307` fixes the types' shape, not their file.
5. **The type-level refusals stay in the gate**, as fixture components under
   `frontend/src/components/__typecheck__/` marked `<!-- @vue-expect-error -->`. They are not a
   one-off scratch run. *Reasons.* `CLAUDE.md` §13: "a check that has never printed a failure
   has not been tested". A committed fixture also keeps failing if a later change weakens the
   API, for example by widening `T` to `any`. With the directive in place, a fixture fails the
   type-check (TS2578, unused directive) as soon as its error stops occurring. **Probed by the
   planner** (below) on the installed `vue-tsc` 3.3.9, **not** the locked 3.3.11, so Task 2
   Step 6 re-proves it on the locked toolchain before anything rests on it.
6. **`ChartFigure.test.ts` renders the component through a `Component`-typed alias.**
   *Reason, probed (below):* `@testing-library/vue`'s `render()` infers the generic `T` as
   `unknown`, so `render(ChartFigure, { props: { columns: Column<Bin>[], … } })` fails the
   type-check (TS2322, `Column<Bin>` not assignable to `Column<unknown>`). `h()` inside a
   wrapper fails the same way (TS2769). `const Figure: Component = ChartFigure` passes. Type
   checking of the generic is the fixtures' job (choice 5). The runtime test checks rendering.
7. **F39's remedy lands in S1 only if it is confined to test code** (`frontend/src/test-setup.ts`
   and `*.test.ts` files). If the cause is in production code, or in a dependency's
   behaviour that a test cannot stub, S1 lands the diagnosis only. The auditor then files an
   `FD-` for the remedy, and the lead sets its owner. *Reason:* the map gives S1 "F39's socket
   diagnosis" (`PL-1286` `:303`), sized at 1 / 2 days for the whole slice. A remedy outside test
   code is a different change, reviewed differently.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 = OQ-550 | How does `ChartFigure` relate a row's values to its columns? | (a) positional, (b) keyed rows, (c) column descriptors | (c) | decision point | yes, for this slice | **`RL-1307`: (c)**, in the form `{ key, label, value }` |
| DP-2 | The migration order of the 13 sites | as `RL-1307` leaves it | Groups A, B, C (*Choices* 1) | design | no | this plan, *Choices* 1 (`RL-1307`: "S1's") |
| DP-3 | The empty-state wording | as `RL-1307` leaves it | `No rows — this figure has no data to show.` (*Choices* 2) | design | no | this plan, *Choices* 2 (`RL-1307`: "S1's") |
| DP-4 | Who owns an F39 remedy that falls outside test code? | (a) S1 widens; (b) a new `FD-` with an owner | (b) (*Choices* 7) | scope | no; S1 lands the diagnosis either way | **owner: the lead**, who sets the new `FD-`'s `decision:` if Task 1 Step 5 finds the cause outside test code (`document-ids.md` §1.6, FD row) |

## Acceptance Standard

Every command runs in the executor's worktree at the slice head, against the range
`origin/main...HEAD`.

1. **The component is generic and the old shape is gone.**
   `grep -c 'generic="T"' frontend/src/components/ChartFigure.vue` prints `1`;
   `git grep -n 'checkedRows\|row.length !== width\|columns: readonly string\[\]' HEAD -- frontend/src`
   prints nothing; `frontend/src/chart-table.ts` exports `Cell` and `Column`.
2. **Every call site is migrated.** At the slice head,
   `git grep -n '<ChartFigure' HEAD -- 'frontend/src/*.vue'` prints the same files Task 0
   recorded at the dispatch tree (13 lines in 11 files at `1dd5e264`, plus any site added
   since), and `pnpm --dir frontend type-check` exits 0. A site still passing string headers
   cannot type-check against `columns: readonly Column<T>[]`. The ledger records the error
   list after each of Tasks 2 to 5, shrinking to nothing.
3. **The type-level violations are refused in the gate, each shown red** (`RL-1307` §Acceptance,
   violations 1 and 2). Four fixtures exist under `frontend/src/components/__typecheck__/`:
   `ChartFigureBadAccessor.vue` and `ChartFigureBadCellType.vue` (violation 1),
   `ChartFigureMismatch.vue` (violation 2), and `ChartFigureNoAnyLeak.vue`. **`NoAnyLeak` is an
   extra fixture beyond the ruling's four violations**, taken from its spike. Each holds
   one `<!-- @vue-expect-error -->` directive, and `type-check` exits 0 with them in place. **The
   fixtures are proven on the locked `vue-tsc` 3.3.11** (Task 0 Step 4 records the installed
   version; a run on any other version does not satisfy this item). **The ledger records two
   red runs per fixture**, each with its own output verbatim:
   (a) with the directive removed, `type-check` fails with the named error: TS2339 "Property
   'bnad' does not exist on type 'Band'", TS2322 "Type 'string[]' is not assignable to type
   'Cell'", TS2322 "Type 'Band[]' is not assignable to type 'readonly Other[]'", and TS2322
   "Type 'string' is not assignable to type 'number'". (b) With the directive kept and the
   fault corrected, `type-check` fails with TS2578 "Unused '@ts-expect-error' directive". A
   failure with the right status code and a **different message** is a plan defect, not a
   pass (`README.md` convention 2).
4. **A duplicated key is refused in every build, under test** (`RL-1307` §Acceptance,
   violation 3; *Choices* 3 as revised on the maintainer's overrule).
   - `git grep -n 'import.meta.env.DEV' HEAD -- frontend/src/components/ChartFigure.vue` prints
     nothing.
   - `pnpm --dir frontend exec vitest run src/components/__tests__/ChartFigure.test.ts` passes
     the test whose name contains `NFR-463` and "refuses two columns that share a key", in
     **both** of its cases (as built, and with `DEV` stubbed `false`).
   - Each case asserts three things: the alert's exact text
     `Table unavailable: two columns in "Lift by decile" share the key "predicted" (bin | predicted | predicted).`;
     that `queryByRole("table")` is `null`, so no colliding table renders; and that the chart
     slot still renders.
   - The test also runs in the CI frontend workflow's `pnpm --dir frontend test` step, and the
     PR's CI run is cited in the ledger.
   - **Red first, with output pasted:** the ledger records both cases failing on the old
     component (Task 2 Step 3), where no alert renders. If the executor writes the refusal
     with a `DEV` gate at any point, the stubbed case is the one that must fail. Task 2
     Step 5a proves that by adding the gate temporarily and pasting the failure.
5. **Each row is named by its first cell** (`RL-1307` item 5 (ii)). The same file asserts that
   `within(table).getAllByRole("rowheader")` has one element per row, with the first column's
   text, and that a `null` first-column value renders `—`.
6. **The empty state names no module** (item 5 (iii)).
   `git grep -n 'this diagnostic recorded nothing' HEAD -- frontend/src` prints nothing, and
   `ChartFigure.test.ts` asserts `No rows — this figure has no data to show.` exactly.
7. **`cellUnder`'s stale text is gone** (item 4).
   `git grep -n "guard should have caught first\|row is all <td>\|two independent props with no relation" HEAD -- frontend/src/test-tables.ts`
   prints nothing. `cellUnder`'s code is unchanged except the thrown message.
8. **Every migrated site keeps its table's content.** Each site's existing test file passes.
   Every assertion that read a chart-table cell by position (`getAllByRole("cell")[n]`) now
   reads it with `cellUnder` by label. `CalibrationChart`, `GbmEvalCurveChart` and
   `LineageGraph` each gain a test file whose test name contains `NFR-463` and which reads at
   least two cells with `cellUnder`, comparing each with the fixture's source value.
   **`RL-1307` §Acceptance's fourth violation is shown red once** (Task 3 Step 4a): in
   `GbmEvalCurveChart.test.ts`, with one accessor deliberately pointed at the wrong field
   (`Train` reading `p.holdout`), the `cellUnder` assertion for `Train` fails with
   `expected element to have text content` naming the fixture's train value. The ledger
   pastes that output verbatim. The test passes again once the accessor is restored. A
   failure from any other cause (a missing row, a missing column) is a plan defect.
9. **F39 is diagnosed** (`PL-1286` Acceptance 9). The ledger names the test file(s) and the
   call that open the socket, with the commands and their output verbatim, at a named tree.
   If the remedy lands (*Choices* 7): `pnpm --dir frontend test 2>&1 | grep -c ECONNREFUSED`
   prints `0`, and the guard is shown red on a deliberately unstubbed test (Task 1 Step 6). If
   it does not land, the ledger says so and names the reason. In both cases **the auditor
   writes F39's dated resolution in `docs/findings/register.md` at slice close**, citing the
   PR. The register is the auditor's (`document-ids.md` §1.6, FD row). The executor does not
   edit it.
10. **The gate is green, both halves** (`CLAUDE.md` §11; `PL-1286` Acceptance 10), at the
    slice head, under a gate slot (`dev-commands`). The PR body reports **the bundle size
    change** (`PL-1286` Acceptance 7): for every `frontend/dist/assets/*.js` chunk whose size
    differs between `origin/main` and the slice head, at least the shared entry chunk
    `index-*.js`, the raw and gzip sizes Vite prints, before and after.
11. **The docs checks pass:** `python3 scripts/audit-docs.py`, `python3 scripts/doc-id.py check`,
    `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` each exit 0,
    apart from any red the lead has recorded as expected on `main`.

## Global Constraints

- **Vue 3 Composition API with `<script setup lang="ts">` only**; never Options API, JSX or
  React (`CLAUDE.md` §3). The generic form is `<script setup lang="ts" generic="T">`.
- **Never hand-write an API type** (`CLAUDE.md` §3). Row types are the generated or `api/`
  module types each caller already imports (`GbmEvalPoint`, `PartialDependence`,
  `DatasetLineage`, …). `chart-table.ts` defines only the component's own `Cell` and `Column`,
  which have no backend counterpart (`RL-1307`).
- **Money is integer minor units or a decimal string, never a float** (`00` FR-10, FR-21). An
  accessor returns exactly what the old row array held, so `OneWayChart`'s `formatMinor` and
  the decimal strings in `AeByFactorChart`, `DoubleLiftChart` and `HistogramChart` pass through
  unchanged (`RL-1307` item 6).
- **WCAG 2.2 AA and an accessible tabular equivalent for every chart** (`00` NFR-463). The table
  stays always in the DOM (`ChartFigure.vue:25-27`).
- **One slice at a time within the Work; at most two build slices at once, from different
  Works, each holding a gate slot, no shared files** (`delivery-process.md` §8 as amended,
  `RL-1263`).

## Scope

### Requirement coverage, each id individually

| Id | What S1 does with it |
|---|---|
| NFR-463 | the generic descriptor API (its 2026-09-30 clause), the row headers, and the tests named for it |
| FR-10 | unchanged money handling at every migrated site, checked by the existing tests |
| FR-21 | the same |

### Measurements at `1dd5e264`

- **Call sites.** Predicate, verbatim:
  `git grep -n '<ChartFigure' origin/main -- 'frontend/src/*.vue'`, run with `origin/main` at
  `1dd5e264195677b4a13268b80ac8673c2c027135`. It prints **13 lines in 11 files**:
  `AeByFactorChart.vue:86`, `CalibrationChart.vue:92`, `CrossValidationPanel.vue:148`,
  `CrossValidationPanel.vue:161`, `DoubleLiftChart.vue:150`, `GbmEvalCurveChart.vue:73`,
  `GbmImportanceCharts.vue:133`, `GbmImportanceCharts.vue:146`, `HistogramChart.vue:111`,
  `LiftChart.vue:98`, `LineageGraph.vue:122`, `OneWayChart.vue:181`,
  `PartialDependencePanel.vue:83` (all under `frontend/src/components/`). This agrees with
  `RL-1307`'s 13 at `7040cf1e`.
- **Test files per site.** `ls frontend/src/components/__tests__/<Name>.test.ts` at
  `1dd5e264`: present for 8 of the 11 files, **absent for `CalibrationChart`,
  `GbmEvalCurveChart` and `LineageGraph`**. A missing neighbour is a scope finding
  (`README.md`), so Tasks 3 and 5 add the three test files.
- **Positional chart-cell reads that the row header shifts.** Predicate:
  `grep -c 'ByRole("cell")' frontend/src/components/__tests__/<Name>.test.ts`, per file:
  `ChartFigure` 2, `AeByFactorChart` 1, `CrossValidationPanel` 1, `GbmImportanceCharts` 5,
  `LiftChart` 1, `PartialDependencePanel` 1, `DoubleLiftChart` 0, `HistogramChart` 0,
  `OneWayChart` 0. `GlmDiagnosticsPanel.test.ts` (4) and
  `frontend/src/views/__tests__/DiagnosticsView.test.ts` (4) also match. Whether each of
  those reads a **`ChartFigure`** table or a hand-written one is not established here: Task 4
  Step 5 checks each. Once a `ChartFigure` row's first cell is a `rowheader`, `getAllByRole("cell")`
  no longer returns it, and every index after it shifts by one.
- **F39's environment.** `frontend/vitest.config.ts` sets `environment: "happy-dom"`, and
  `frontend/src/test-setup.ts` holds one import and no `fetch` stub. `frontend/src/api/client.ts`
  builds request URLs from `window.location.origin` (as the comment at
  `frontend/src/api/__tests__/diagnostics.test.ts:21-23` records: "`http://localhost:3000/...`").
  **Planner's hypothesis, not verified by a run:** a test renders a component whose mount
  calls the API client without stubbing `fetch`, so a real request goes to the test
  environment's default origin on port 3000. Task 1 tests this hypothesis and does not assume it.
- **The planner's probes** (2026-10-01 10:12 BST, scratch directory
  `/tmp/planner-675s1-probe`, not committed; `vue-tsc` **3.3.9** from the primary checkout's
  installed `node_modules`, not the locked 3.3.11; the `tsconfig.json` from `RL-1307`'s spike):
  - a generic component with `columns: readonly Column<T>[]`, `T` imported from a plain
    `chart-table.ts`: a caller with `value: (r) => r.bnad` under `<!-- @vue-expect-error -->`
    passes. The same caller with the directive removed fails with
    `TS2339: Property 'bnad' does not exist on type 'Band'.` A correct caller under the
    directive fails with `TS2578: Unused '@ts-expect-error' directive.` So the directive
    holds the refusal in the gate in both directions;
  - `render(Fig, { props: { title, columns, rows } })` with `columns: readonly Column<Bin>[]`
    fails: `TS2322: Type 'readonly Column<Bin>[]' is not assignable to type 'readonly
    Column<unknown>[]'`. A typed `h(Fig, …)` wrapper fails with TS2769. `const Figure: Component
    = Fig; render(Figure, …)` exits 0.

### File contention (for the lead, under `RL-1263` (c))

| S1 path | Other slice | Kind |
|---|---|---|
| `frontend/src/components/ChartFigure.vue`, `frontend/src/chart-table.ts`, the 11 caller files, their tests, `frontend/src/test-tables.ts`, `frontend/src/test-setup.ts` | WK-690 Slice 5, SL-1275 (`draft`, starts after SL-1273, also `draft`): adds a `ChartFigure` caller (`PL-1268` `:541-547`) | **ordered, not concurrent** (`PL-1286` `:406`). If S1 lands first, SL-1275 uses the new API (`RL-1307` item 7). If SL-1275 lands first, S1 migrates its caller as a fourteenth site (Task 0) |
| `docs/INDEX.md`, the slice's ledger | any | exempt (append-only registry) |

### Concurrency at `1dd5e264` (2026-10-01 10:07 BST)

- **Active slice rows** in `docs/roadmap.md` (`status: active` under an `id: SL-` header): only
  **SL-1360** (WK-1178, the permission-parity check). Its PR #1049 changes
  `docs/INDEX.md`, its ledger and `tests/test_permission_parity.py`, so it shares no file with S1.
- **Open PRs touching `frontend/`:** none. Command:
  `gh pr list --state open --limit 40 --json number,files --jq '.[] | "\(.number) \([.files[].path | select(startswith("frontend/"))] | join(","))"'`
  printed an empty file list for all 24 open PRs.
- **WK-675 has no other slice row**: S1 is its first.
- The lead re-reads both at dispatch, because this is a claim about a moving tree.

### Size

1 / 2 days (likely / worst), `PL-1286` `:303`. Six tasks. Most of the line count is the 13
rewritten `columns` blocks.

## Tasks

### Task 0: Preconditions (no code)

**Files:** none (ledger only).

- [ ] **Step 1: Name the tree.** `git -C <worktree> fetch origin && git -C <worktree> rev-parse origin/main`.
  Branch from it. Record the SHA in the ledger.
- [ ] **Step 2: Re-measure the call sites with the same predicate.**
  Run `git grep -n '<ChartFigure' origin/main -- 'frontend/src/*.vue'`. Record the output verbatim.
  If it prints anything beyond the 13 lines under *Measurements*, the extra lines are sites to
  migrate in this slice. Put each one in the group its columns match (*Choices* 1), and say so
  in the ledger.
- [ ] **Step 3: Re-read the holds** (`~/gi-pricing-plan.local/handover/holds-*.md`, the newest
  one) and confirm in the ledger that no hold names S1. Also confirm `RL-1307` is unchanged:
  `git log --oneline 1dd5e264..origin/main -- docs/rulings/RL-01307-*.md` prints nothing, or
  read the diff.
- [ ] **Step 4: Install from the lockfile.**
  `pnpm --dir frontend install --frozen-lockfile` and then `pnpm --dir frontend generate:api`.
  Record `vue-tsc`'s version from `frontend/node_modules/vue-tsc/package.json`. It must be the
  locked 3.3.11, not the primary checkout's 3.3.9 (`RL-1307`, "The toolchain").

### Task 1: F39 — what opens port 3000

**Files:**
- Modify (only if the cause is in test code): `frontend/src/test-setup.ts`, and the culprit
  `*.test.ts` file(s)
- Ledger: the diagnosis

**Interfaces:**
- Produces: a vitest run with no `ECONNREFUSED` line, if the remedy lands. Every later task
  reads vitest output, and a known-noise line at its head can hide a new one. That is why this
  task comes first.

Announce the test runs to the team before Step 1 (`delivery-process.md` §8: announce an
expensive verification, and check for one already in flight).

- [ ] **Step 1: Reproduce.** `pnpm --dir frontend test > /tmp/<slice>-f39-full.txt 2>&1; echo "rc=$?"`,
  then `grep -n -m5 'ECONNREFUSED\|AggregateError' /tmp/<slice>-f39-full.txt`. Record both.
  The register row's text: an `AggregateError` with `ECONNREFUSED ::1:3000` and
  `127.0.0.1:3000` before any test output, exit 0. **If it does not reproduce**, record that,
  with the tree and the command, run Step 2 once anyway (a per-file run can expose what a
  parallel run hides), and go to Step 7.
- [ ] **Step 2: Localise to a file.** Run each test file alone and record which print the error:

```bash
git -C <worktree> ls-files 'frontend/src/*.test.ts' | sed 's#^frontend/##' > /tmp/<slice>-f39-files.txt
while read -r f; do
  if pnpm --dir frontend exec vitest run "$f" 2>&1 | grep -q ECONNREFUSED; then echo "HIT $f"; fi
done < /tmp/<slice>-f39-files.txt | tee /tmp/<slice>-f39-hits.txt
```

  Expected: one or more `HIT` lines. Zero hits while Step 1 reproduced means the cause is
  in cross-file interaction or in setup. Record that, and run the hit search again over pairs
  of files only if the band allows. Otherwise go to Step 7 with "not localised".
- [ ] **Step 3: Localise to the call.** For each hit file, find the test and the call. Run it
  with `--reporter=verbose` and see which test the error sits under. Then read what that
  test mounts and what the mounted code calls on mount: `fetch` through
  `frontend/src/api/client.ts`, an `EventSource`, a `WebSocket`, or a resource that happy-dom
  loads itself. Record the file, the test name, and the calling line.
- [ ] **Step 4: Test the hypothesis.** If the call is `fetch` through `client.ts`, stub `fetch`
  in that test alone (`vi.stubGlobal("fetch", vi.fn(...))`, following that file's neighbouring
  tests rather than a new pattern). Re-run the file and confirm the error is gone. If the call
  is something else, record what it is: the hypothesis was wrong, and the record says so.
- [ ] **Step 5: Decide the remedy's home** (*Choices* 7). The cause is confined to test code →
  Steps 6 and 7. It is in production code or in happy-dom's own loading → Step 7 only, and
  the ledger states "remedy not in S1" with the reason, for the auditor's `FD-` (DP-4).
- [ ] **Step 6: The remedy, and the guard proven red.** Fix each culprit test with a stub.
  Then add a guard to `frontend/src/test-setup.ts` that fails any test calling `fetch`
  without stubbing it. It is installed by **plain assignment**, not `vi.stubGlobal`: a test's
  `vi.unstubAllGlobals()` restores what was there when it stubbed, so it restores the guard
  and not the real `fetch`.

```ts
import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";

/**
 * Register row F39: the suite opened a TCP connection to port 3000, which is the test
 * environment's default origin, because a test reached the network through `fetch` without
 * stubbing it. Harmless while the connection is refused. It turns into a silent flake where
 * something answers on that port. A test that needs `fetch` stubs it
 * (`vi.stubGlobal("fetch", …)`); any other call fails the test that made it, by name.
 */
const unstubbedFetches: string[] = [];

globalThis.fetch = ((input: RequestInfo | URL) => {
  const url = input instanceof Request ? input.url : String(input);
  unstubbedFetches.push(url);
  return Promise.reject(new Error(`unstubbed fetch in a test: ${url}`));
}) as typeof fetch;

afterEach(() => {
  if (unstubbedFetches.length > 0) {
    const urls = unstubbedFetches.splice(0).join(", ");
    throw new Error(`F39: this test called fetch without stubbing it: ${urls}`);
  }
});
```

  **Red first:** before the culprit's stub is added, run the culprit file with the guard in
  place. Expected: FAIL, with the message `F39: this test called fetch without stubbing it:
  http://localhost:3000/` followed by the path. A failure with any other message is a plan
  defect. Then add the stub and see it pass. Then run the full suite:
  `pnpm --dir frontend test 2>&1 | grep -c ECONNREFUSED` prints `0`, and the suite's pass
  count equals Step 1's. A **lower** count means the guard turned a passing test red. That test
  also reached the network: stub it, and list it in the ledger.
  If the guard turns more than three further test files red, stop and report to the lead
  before stubbing them. That is wider than the band, and it is DP-4's call.
- [ ] **Step 7: Record the diagnosis** in the ledger: the commands, their output, the tree,
  the file(s), the call, whether the hypothesis held, and whether the remedy landed. Then
  commit: `test(frontend): F39 — diagnose the port-3000 socket (WK-675 S1)`, with the guard if
  it landed. Do **not** edit `docs/findings/register.md` (Acceptance 9).

### Task 2: The generic `ChartFigure`, its types, its tests and the type-level fixtures

**Files:**
- Create: `frontend/src/chart-table.ts`
- Modify: `frontend/src/components/ChartFigure.vue` (whole `<script>` and the `<table>`/empty-state markup)
- Modify: `frontend/src/components/__tests__/ChartFigure.test.ts` (rewritten)
- Modify: `frontend/src/test-tables.ts:10-13`, `:18-21`, `:43-47`
- Create: `frontend/src/components/__typecheck__/ChartFigureBadAccessor.vue`,
  `ChartFigureBadCellType.vue`, `ChartFigureMismatch.vue`, `ChartFigureNoAnyLeak.vue`

**Interfaces:**
- Produces: `export type Cell = string | number | null;` and
  `export interface Column<R> { readonly key: string; readonly label: string; readonly value: (row: R) => Cell }`
  from `@/chart-table`. `ChartFigure` props: `title: string; caption?: string; columns:
  readonly Column<T>[]; rows: readonly T[]`. In every build, the visible error that replaces
  the table when two columns share a key (`role="alert"`):
  `Table unavailable: two columns in "<title>" share the key "<key>" (<key> | <key> | …).`

- [ ] **Step 1: Create the types module.** Create `frontend/src/chart-table.ts`:

```ts
/**
 * The column descriptor `ChartFigure` takes (RL-1307, OQ-550 (c)).
 *
 * Each column carries its own accessor, so a table cell is read from the caller's own row
 * by the column it sits under. A value cannot be placed under a heading it does not belong
 * to without the accessor itself being wrong, and `vue-tsc` checks the accessor against the
 * row type. `key` is an identifier, unique within one figure. `label` is the heading text,
 * free to change.
 */
export type Cell = string | number | null;

export interface Column<R> {
  readonly key: string;
  readonly label: string;
  readonly value: (row: R) => Cell;
}
```

  The directive's proof on the locked toolchain (*Choices* 5) is Step 6, after the component
  exists. Nothing before Step 6 rests on it.

- [ ] **Step 2: Write the four fixtures.** Each is a deliberately broken call site with the
  directive on the line before the broken element. Each one's comment names the error it
  expects.

`frontend/src/components/__typecheck__/ChartFigureBadAccessor.vue`:

```vue
<script setup lang="ts">
/**
 * Type-check fixture, never rendered (RL-1307 §Acceptance): an accessor that reads a field the
 * row type does not have. Expected error: TS2339, Property 'bnad' does not exist on type 'Band'.
 * If the directive below ever stops being needed, `pnpm --dir frontend type-check` fails
 * with TS2578, which means the generic API has stopped checking accessors.
 */
import ChartFigure from "@/components/ChartFigure.vue";

interface Band {
  band: string;
  exposure: number;
}
const rows: Band[] = [{ band: "A", exposure: 1.5 }];
</script>

<template>
  <!-- @vue-expect-error TS2339: the accessor reads a field Band does not have -->
  <ChartFigure title="t" :rows="rows" :columns="[{ key: 'band', label: 'Band', value: (r) => r.bnad }]" />
</template>
```

`frontend/src/components/__typecheck__/ChartFigureBadCellType.vue`:

```vue
<script setup lang="ts">
/**
 * Type-check fixture, never rendered (RL-1307 §Acceptance): an accessor that returns a value
 * that is not a cell. Expected error: TS2322, Type 'string[]' is not assignable to type 'Cell'.
 */
import ChartFigure from "@/components/ChartFigure.vue";

interface Band {
  band: string;
  tags: string[];
}
const rows: Band[] = [{ band: "A", tags: [] }];
</script>

<template>
  <!-- @vue-expect-error TS2322: string[] is not a Cell -->
  <ChartFigure title="t" :rows="rows" :columns="[{ key: 'tags', label: 'Tags', value: (r) => r.tags }]" />
</template>
```

`frontend/src/components/__typecheck__/ChartFigureMismatch.vue`:

```vue
<script setup lang="ts">
/**
 * Type-check fixture, never rendered (RL-1307 §Acceptance): columns written for one row type
 * passed with rows of another. Expected error: TS2322, Type 'Band[]' is not assignable to
 * type 'readonly Other[]'.
 */
import type { Column } from "@/chart-table";
import ChartFigure from "@/components/ChartFigure.vue";

interface Band {
  band: string;
}
interface Other {
  level: number;
}
const rows: Band[] = [{ band: "A" }];
const columns: Column<Other>[] = [{ key: "level", label: "Level", value: (o) => o.level }];
</script>

<template>
  <!-- @vue-expect-error TS2322: columns for Other, rows of Band -->
  <ChartFigure title="t" :rows="rows" :columns="columns" />
</template>
```

`frontend/src/components/__typecheck__/ChartFigureNoAnyLeak.vue`:

```vue
<script setup lang="ts">
/**
 * Type-check fixture, never rendered (RL-1307's spike, beyond its four acceptance checks): the
 * accessor's parameter is inferred as the row type, not `any`. `r.band` is a string, so
 * assigning it to a number must fail. Expected error: TS2322, Type 'string' is not assignable
 * to type 'number'. If `T` ever widened to `any`, this directive would go unused and the
 * type-check would fail with TS2578.
 */
import ChartFigure from "@/components/ChartFigure.vue";

interface Band {
  band: string;
}
const rows: Band[] = [{ band: "A" }];
</script>

<template>
  <!-- @vue-expect-error TS2322: r is Band, so r.band is a string -->
  <ChartFigure title="t" :rows="rows" :columns="[{ key: 'x', label: 'X', value: (r) => { const n: number = r.band; return n; } }]" />
</template>
```

  If ESLint or Prettier wraps the `<ChartFigure …/>` element over several lines, the directive
  then covers only the next line. Keep the broken attribute on the line right after the
  directive. If the formatter will not allow that, place the directive immediately above the
  broken attribute line, inside the element. Step 6 proves whichever placement is used.

- [ ] **Step 3: Rewrite `ChartFigure.test.ts`, red first.** Replace the file:

```ts
import { render, screen, within } from "@testing-library/vue";
import type { Component } from "vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { Column } from "@/chart-table";
import { cellUnder } from "@/test-tables";

import ChartFigure from "../ChartFigure.vue";

/**
 * `render()` infers a generic component's `T` as `unknown`, so it would refuse correctly typed
 * columns. Type checking of the generic is the `__typecheck__` fixtures' job. This file checks
 * what renders.
 */
const Figure: Component = ChartFigure;

interface Bin {
  readonly label: string | null;
  readonly predicted: number;
  readonly actual: number | null;
}

const ROWS: readonly Bin[] = [
  { label: "Decile 1", predicted: 0.021, actual: 0.023 },
  { label: "Decile 2", predicted: 0.049, actual: null },
];

const COLUMNS: readonly Column<Bin>[] = [
  { key: "bin", label: "Bin", value: (r) => r.label },
  { key: "predicted", label: "Predicted", value: (r) => r.predicted },
  { key: "actual", label: "Actual", value: (r) => r.actual },
];

function renderFigure(
  columns: readonly Column<Bin>[] = COLUMNS,
  rows: readonly Bin[] = ROWS,
) {
  return render(Figure, {
    props: { title: "Lift by decile", columns, rows },
    slots: { default: "<div data-testid='chart' />" },
  });
}

function table(): HTMLElement {
  return screen.getByRole("table", { name: /lift by decile/i });
}

describe("ChartFigure (NFR-463)", () => {
  it("renders the chart it was given", () => {
    renderFigure();
    expect(screen.getByTestId("chart")).toBeInTheDocument();
  });

  it("gives the table the figure's own name, so a screen reader can tell two apart", () => {
    renderFigure();
    expect(table()).toBeInTheDocument();
  });

  it("renders one header per column, labelled by the descriptor's label, and one row per datum", () => {
    renderFigure();
    const headers = within(table()).getAllByRole("columnheader").map((h) => h.textContent?.trim());
    expect(headers).toEqual(["Bin", "Predicted", "Actual"]);
    expect(within(table()).getAllByRole("row")).toHaveLength(ROWS.length + 1);
  });

  it("NFR-463: names each row by its first column, rendered as a row header", () => {
    renderFigure();
    const rowHeaders = within(table()).getAllByRole("rowheader");
    expect(rowHeaders).toHaveLength(ROWS.length);
    expect(rowHeaders.map((h) => h.textContent?.trim())).toEqual(["Decile 1", "Decile 2"]);
  });

  it("NFR-463: reads every cell from its own column's accessor", () => {
    renderFigure();
    expect(cellUnder(table(), /Decile 1/, "Predicted")).toHaveTextContent("0.021");
    expect(cellUnder(table(), /Decile 1/, "Actual")).toHaveTextContent("0.023");
    expect(cellUnder(table(), /Decile 2/, "Predicted")).toHaveTextContent("0.049");
  });

  it("NFR-463: a reordered columns prop moves each value with its heading", () => {
    // The case the positional shape got wrong: the headers moved and the values stayed.
    // With descriptors, a value travels with its own column.
    renderFigure([COLUMNS[0]!, COLUMNS[2]!, COLUMNS[1]!]);
    expect(cellUnder(table(), /Decile 1/, "Predicted")).toHaveTextContent("0.021");
    expect(cellUnder(table(), /Decile 1/, "Actual")).toHaveTextContent("0.023");
  });

  it("writes a missing value as an em dash rather than as a zero, in a cell and in a row header", () => {
    renderFigure(COLUMNS, [...ROWS, { label: null, predicted: 0.06, actual: 0.07 }]);
    expect(cellUnder(table(), /Decile 2/, "Actual")).toHaveTextContent("—");
    expect(cellUnder(table(), /Decile 2/, "Actual")).not.toHaveTextContent("0");
    const rowHeaders = within(table()).getAllByRole("rowheader");
    expect(rowHeaders[2]).toHaveTextContent("—");
  });

  it("renders the table for a chart with no data, and says so without naming a module", () => {
    renderFigure(COLUMNS, []);
    expect(within(table()).getAllByRole("row")).toHaveLength(1);
    expect(screen.getByText("No rows — this figure has no data to show.")).toBeInTheDocument();
  });

  describe("NFR-463: refuses two columns that share a key, in every build", () => {
    // RL-1307 item 5 (i): `key` is the Vue key and must be unique within one figure. Two
    // equal keys would let Vue patch one column's cells with the other's. The refusal must
    // not depend on a dev build: RL-1307 retired the arity guard because it was dev-only, so
    // the second case runs with DEV stubbed false, and a DEV gate fails it.
    afterEach(() => {
      vi.unstubAllEnvs();
    });

    const duplicate: readonly Column<Bin>[] = [
      COLUMNS[0]!,
      COLUMNS[1]!,
      { key: "predicted", label: "Actual", value: (r) => r.actual },
    ];

    it.each([
      ["as built", undefined],
      ["with DEV false, as in production", false],
    ] as const)("refuses two columns that share a key, %s", (_name, dev) => {
      if (dev !== undefined) vi.stubEnv("DEV", dev);
      renderFigure(duplicate);
      expect(screen.getByRole("alert")).toHaveTextContent(
        'Table unavailable: two columns in "Lift by decile" share the key "predicted" (bin | predicted | predicted).',
      );
      expect(screen.queryByRole("table")).toBeNull();
      expect(screen.getByTestId("chart")).toBeInTheDocument();
    });
  });

  it("accepts two columns with the same label under different keys", () => {
    // The (b′) half of RL-1307 item 3: a label is display text, so equal labels are allowed.
    renderFigure([
      COLUMNS[0]!,
      { key: "a", label: "Rate", value: (r) => r.predicted },
      { key: "b", label: "Rate", value: (r) => r.actual },
    ]);
    expect(within(table()).getAllByRole("columnheader")).toHaveLength(3);
  });
});
```

  Run: `pnpm --dir frontend exec vitest run src/components/__tests__/ChartFigure.test.ts`.
  Expected: FAIL. The cause must be that the old component treats each column as a string:
  the headers render as `[object Object]`, or a render throws in the arity guard with "row 0
  has … cells" (rows are objects, so `row.length` is `undefined`). Both duplicate-key cases
  fail because no `alert` renders: `getByRole("alert")` finds nothing. Paste that output into
  the ledger (Acceptance 4). Record which tests fail and
  why. A failure from a missing import or a syntax error is a test defect: fix it and re-run
  until every failure has one of the causes above.

- [ ] **Step 4: Rewrite `ChartFigure.vue`.** Keep the top docstring (lines 2-28), changing only
  its "superset" paragraph's reference to "the tests here". Replace the props, the guard and
  the markup:

```vue
<script setup lang="ts" generic="T">
/**
 * (lines 2-28 of the old file, unchanged)
 *
 * Each column is a descriptor, `{ key, label, value }`, and each cell is `column.value(row)`
 * over the caller's own row objects (RL-1307, OQ-550 (c)). The heading and the value's source
 * sit in one object, so a value cannot be placed under a heading it does not belong to
 * without the accessor itself being wrong, and `vue-tsc` checks every accessor against the
 * row type in the gate (`src/components/__typecheck__/`). The positional shape's two checks
 * went with it: the arity guard retired by construction, since every row now renders one
 * cell per column, and `cellUnder` (`src/test-tables.ts`) stays as the reader a test uses to
 * compare a table with its chart's data by label.
 */
import { computed } from "vue";

import type { Column } from "@/chart-table";

const props = defineProps<{
  /** Names the figure and labels the table. Two figures on a page must not share one. */
  title: string;
  /** Optional sentence under the heading: the place to say what a partition or a unit is. */
  caption?: string;
  /** One descriptor per column. The first column names each row, as its row header. */
  columns: readonly Column<T>[];
  /** The caller's own row objects. Each cell is read from one by its column's accessor. */
  rows: readonly T[];
}>();

/**
 * The refusal of two columns that share a `key`, in **every build** (RL-1307 item 5 (i)).
 *
 * `key` is the Vue key of every header and cell in its column, so two equal keys would let
 * Vue patch one column's cells with the other's: a table showing a value under a heading it
 * does not belong to, which is the violation this component exists to make impossible. A
 * label is display text and may repeat. There is deliberately no `import.meta.env.DEV` gate.
 * RL-1307 retired the arity guard because it ran only in development, so this check runs in
 * production too. It does not throw, because a throw from a render blanks the page. The figure
 * shows a visible error in its table's place, and no table renders.
 */
const duplicateKeyError = computed<string | null>(() => {
  const seen = new Set<string>();
  for (const column of props.columns) {
    if (seen.has(column.key)) {
      return (
        `Table unavailable: two columns in "${props.title}" share the key "${column.key}" ` +
        `(${props.columns.map((c) => c.key).join(" | ")}).`
      );
    }
    seen.add(column.key);
  }
  return null;
});
</script>

<template>
  <figure class="mt-6">
    <figcaption>
      <h3 class="text-sm font-semibold text-slate-700">
        {{ title }}
      </h3>
      <p
        v-if="caption"
        class="mt-1 text-xs text-slate-500"
      >
        {{ caption }}
      </p>
    </figcaption>

    <slot />

    <p
      v-if="duplicateKeyError"
      role="alert"
      class="mt-2 text-sm text-red-700"
    >
      {{ duplicateKeyError }}
    </p>

    <table
      v-else
      :aria-label="title"
      class="mt-2 w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            scope="col"
            class="py-2 font-medium"
          >
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, index) in rows"
          :key="index"
          class="border-b border-slate-100"
        >
          <template
            v-for="(column, columnIndex) in columns"
            :key="column.key"
          >
            <th
              v-if="columnIndex === 0"
              scope="row"
              class="py-1 font-normal tabular-nums"
            >
              {{ column.value(row) ?? "—" }}
            </th>
            <td
              v-else
              class="py-1 tabular-nums"
            >
              {{ column.value(row) ?? "—" }}
            </td>
          </template>
        </tr>
      </tbody>
    </table>

    <p
      v-if="!duplicateKeyError && rows.length === 0"
      class="mt-1 text-xs text-slate-500"
    >
      No rows — this figure has no data to show.
    </p>
  </figure>
</template>
```

  Write the real lines 2-28 in place of the placeholder comment line. Do not leave
  "(lines 2-28 of the old file, unchanged)" in the file.

- [ ] **Step 5: Run the component's test.** Same command as Step 3. Expected: PASS, every test.
- [ ] **Step 5a: Prove that a `DEV` gate is caught** (Acceptance 4). Temporarily wrap the body
  of `duplicateKeyError` in `if (import.meta.env.DEV) { … }` and return `null` otherwise.
  Re-run Step 3's command. Expected: FAIL in the case "refuses two columns that share a key,
  with DEV false, as in production" only, because `getByRole("alert")` finds nothing. Paste the
  output into the ledger, then remove the gate and re-run to PASS. The gated version is never
  committed. If both cases pass with the gate in place, `vi.stubEnv` does not reach this
  component's `import.meta.env`. Stop and report: the plan's proof does not hold on this
  toolchain.
- [ ] **Step 6: Prove each fixture red twice** (Acceptance 3). For each of the four fixtures:
  (a) delete its directive line, run `pnpm --dir frontend type-check 2>&1 | grep __typecheck__`,
  record the line, and restore the directive. (b) Correct the fault (`r.bnad` → `r.band`;
  `r.tags` → `r.band`; `Column<Other>` → a `Column<Band>` reading `b.band`; `const n: number`
  → `const n: string`), run the same command, record the TS2578 line, and restore the fault.
  Expected messages are in Acceptance 3. Then run `pnpm --dir frontend type-check 2>&1 | grep -c 'error TS'`
  and record the count. The remaining errors must all be in the 11 unmigrated caller files,
  and none in `ChartFigure.vue`, `chart-table.ts`, `ChartFigure.test.ts` or `__typecheck__/`.
- [ ] **Step 7: Update `test-tables.ts`'s three stale statements** (`RL-1307` item 4).
  Replace lines 10-13 ("`ChartFigure` takes `columns` … agrees with it.") with:

```ts
 * row whose **values** are permuted under unchanged headers. A hand-written table enforces no
 * relation between its header row and its body cells, so that permutation renders every value
 * under the wrong heading, silently, and a positional assertion agrees with it. `ChartFigure`
 * closes the gap at compile time (RL-1307: each column carries its own accessor). This helper
 * is how a test compares a chart's table with the chart's data by label (PL-1286 acceptance 5).
```

  Replace lines 18-21 with:

```ts
 * Cells are located by **DOM order within the row**, not by role, deliberately: a
 * `ChartFigure` row's first cell is `<th scope="row">` (`rowheader`) and the rest are `<td>`
 * (`cell`), and a hand-written table may or may not name its rows the same way. Filtering by
 * role would shift every index by one between shapes, which is precisely the column shift this
 * helper exists to catch.
```

  Replace the thrown message (lines 43-47) with:

```ts
    throw new Error(
      `Row ${String(rowName)} has ${cells.length} cells, so nothing sits under ` +
        `"${columnName}" (column ${column}). The row is shorter than the header row.`,
    );
```

  Run `git grep -n "guard should have caught first\|row is all <td>\|two independent props with no relation" -- frontend/src/test-tables.ts`.
  Expected: nothing.
- [ ] **Step 8: Lint.** `pnpm --dir frontend lint` over the new and changed files. It must not
  flag `generic="T"` or the fixtures. If `eslint-plugin-vue` flags the generic attribute,
  stop and report: that is a toolchain fact this plan did not establish.
- [ ] **Step 9: Commit.** `feat(frontend): ChartFigure takes column descriptors (RL-1307, WK-675 S1)`.
  The type-check is red at this commit only in the unmigrated caller files (Step 6's list).

### Task 3: Group A — seven sites with static columns

**Files:**
- Modify: `frontend/src/components/GbmEvalCurveChart.vue:65-69,76-77`,
  `CrossValidationPanel.vue:66-73,94-96,151-152,164-165`,
  `GbmImportanceCharts.vue:52-59,90-99,136-137,149-150`,
  `PartialDependencePanel.vue:47-49,87-88`, `LineageGraph.vue:103-118,125-126`
- Modify: the existing tests for `CrossValidationPanel`, `GbmImportanceCharts`, `PartialDependencePanel`
- Create: `frontend/src/components/__tests__/GbmEvalCurveChart.test.ts`,
  `frontend/src/components/__tests__/LineageGraph.test.ts`

**Interfaces:**
- Consumes: `Column` from `@/chart-table`; `ChartFigure`'s props (Task 2).

Each site follows one pattern: the old `rows` array of arrays goes away; `:rows` takes the
row objects the old code mapped over. **`LineageGraph` is the exception:** it builds tuple
arrays (`["Built from", name, op, null]`, `:106-117`) rather than mapping over an existing
object. There the executor defines a component-local row interface,
`interface LineageRow { kind: string; name: string; operation: string | null; status: string | null }`,
and builds objects instead. This is not an API type (no backend or `model-schema` shape
describes a lineage table row), so `CLAUDE.md` §3's "never hand-write an API type" is not
engaged. Then `:columns` takes descriptors whose labels are the old
header strings **verbatim**, in the same order, and whose accessors return exactly what the old
array held in that position. Descriptor arrays that do not depend on props are module
constants. Ones that do are `computed`. Each is annotated `readonly Column<RowType>[]` with
the row type the file already imports or derives.

| Site | `:rows` | Columns: label → accessor (key) |
|---|---|---|
| `GbmEvalCurveChart` | `evalCurve` (`GbmEvalPoint`) | `Iteration` → `p.iteration` (`iteration`); `Train` → `p.train ?? null` (`train`); `Holdout` → `p.holdout ?? null` (`holdout`) |
| `CrossValidationPanel`, path | `crossValidation.path` | `Alpha` → `point.alpha` (`alpha`); `Std score` → `point.std_score` (`std-score`); `Mean score` → `point.mean_score` (`mean-score`); `Choice` → `point.alpha === props.crossValidation.selected_alpha ? "Selected" : "—"` (`choice`), a `computed` because it reads `selected_alpha` |
| `CrossValidationPanel`, folds | `crossValidation.fold_metrics` | `Fold` → `fold.fold` (`fold`); `Rows` → `fold.rows` (`rows`); `Score` → `fold.score` (`score`) |
| `GbmImportanceCharts`, gain | `importances` (`FeatureImportance`) | `Feature` → `i.feature` (`feature`); `Cover` → `i.cover ?? null` (`cover`); `Frequency` → `i.frequency` (`frequency`); `Gain` → `i.gain` (`gain`) |
| `GbmImportanceCharts`, permutation | `permutationImportances` (`PermutationImportance`) | `Feature` → `i.feature`; `Baseline` → `i.baseline`; `Permuted` → `i.permuted`; `Repeats` → `i.repeats`; `Seed` → `i.seed`; `Degradation` → `i.degradation` (keys: the field names) |
| `PartialDependencePanel` | `entry.points` (`PartialDependence["points"][number]`) | `Value` → `point.value` (`value`); `Mean prediction` → `point.mean_prediction` (`mean-prediction`); `Exposure share` → `point.exposure_share` (`exposure-share`) |
| `LineageGraph` | a `computed` list of `{ kind, name, operation, status }` objects built by the same pushes as today's `list` (`:106-117`), each field `string \| null` | `Kind` → `r.kind`; `Name` → `r.name`; `Operation` → `r.operation`; `Status` → `r.status` (keys: the field names) |

If an accessor's return type is not assignable to `Cell` (for example a field typed
`number | undefined`), add `?? null` exactly where the old array did. Do not add one where the
old array did not. The type-check tells you which.

For example, `GbmEvalCurveChart.vue` becomes:

```ts
import type { Column } from "@/chart-table";

const columns: readonly Column<GbmEvalPoint>[] = [
  { key: "iteration", label: "Iteration", value: (p) => p.iteration },
  { key: "train", label: "Train", value: (p) => p.train ?? null },
  { key: "holdout", label: "Holdout", value: (p) => p.holdout ?? null },
];
```

with `:rows="evalCurve"` in the template, and the old `rows` computed deleted.

- [ ] **Step 1: Write the two new test files, red first.** Copy each file's props fixture from
  the view test that renders the component today, rather than inventing one. Find the parent
  with `git grep -ln 'GbmEvalCurveChart\|LineageGraph' -- frontend/src/views frontend/src/components`
  and mirror its data. Each test is named `NFR-463: …`, renders the component, finds its table
  by name (`Evaluation curve`, `Lineage`), and reads at least two cells with `cellUnder`
  by row name and label, comparing each with the fixture value it came from. Run them on the
  unmigrated components. Expected: FAIL, because the first column is not yet a `rowheader`
  and the component cannot render (the old positional rows reach a descriptor-only
  `ChartFigure`). Record the reason. Any other cause is a test defect.
- [ ] **Step 2: Convert the existing positional reads** in the `CrossValidationPanel`,
  `GbmImportanceCharts` and `PartialDependencePanel` tests: each `getAllByRole("cell")[n]` that
  reads a `ChartFigure` table becomes `cellUnder(table, rowName, label)`. A read of a
  hand-written table in the same file (for example `GbmImportanceCharts`' monotonicity table,
  if it is hand-written) is left alone. Read the template to tell which table each assertion reads.
- [ ] **Step 3: Migrate the seven sites** per the table.
- [ ] **Step 4: Run** `pnpm --dir frontend exec vitest run src/components/__tests__/{GbmEvalCurveChart,CrossValidationPanel,GbmImportanceCharts,PartialDependencePanel,LineageGraph}.test.ts`.
  Expected: PASS. Then `pnpm --dir frontend type-check 2>&1 | grep 'error TS'`: no line names a
  Group A file. Record the remaining list.
- [ ] **Step 4a: Show `RL-1307`'s fourth violation red** (Acceptance 8). In
  `GbmEvalCurveChart.vue`, temporarily change the `Train` accessor to `(p) => p.holdout ?? null`.
  Run `pnpm --dir frontend exec vitest run src/components/__tests__/GbmEvalCurveChart.test.ts`.
  Expected: FAIL, with `cellUnder(…, "Train")`'s assertion reporting the holdout value where the
  fixture's train value was expected. Paste the output into the ledger. Restore the accessor,
  re-run, and confirm PASS. This deliberately broken change is not committed. The fixture must
  give `train` and `holdout` different values at the row read, or the check cannot fail: if
  they are equal, change the fixture first.
- [ ] **Step 5: Commit.** `refactor(frontend): migrate seven static-column ChartFigure sites (RL-1307, WK-675 S1)`.

### Task 4: Group B — conditional columns and formatted cells

**Files:**
- Modify: `frontend/src/components/HistogramChart.vue:92-107,118-119`,
  `DoubleLiftChart.vue:122-146,153-154`, `OneWayChart.vue:137-147,165-177,186-187`
- Modify: their tests, where a positional read touches a `ChartFigure` table
- Read (Step 5): `GlmDiagnosticsPanel.test.ts`, `frontend/src/views/__tests__/DiagnosticsView.test.ts`

**Interfaces:**
- Consumes: as Task 3.

| Site | `:rows` | Columns: label → accessor (key) |
|---|---|---|
| `HistogramChart` | `computed(() => labels.value.map((label, i) => ({ label, count: counts.value[i] ?? null, exposure: exposure.value[i] ?? null })))` | `Bin` → `r.label` (`bin`); `Rows` → `r.count` (`rows`); and, only when `exposure.value.length`, `Exposure` → `r.exposure` (`exposure`). `columns` stays a `computed`, as today (`:92-94`) |
| `DoubleLiftChart` | `bins.value` | `Bin (by prediction ratio)` → `String(b.bin)` (`bin`); `Rows` → `b.rows` (`rows`); only when `exposureText.value` is non-null, `Exposure` → `b.exposure_years ?? null` (`exposure`); `Actual` → `b.actual` (`actual`); `Baseline predicted` → `b.baseline_predicted` (`baseline-predicted`); `Challenger predicted` → `b.challenger_predicted` (`challenger-predicted`) |
| `OneWayChart` | `rows.value` (the summary rows, `:33`) | `Level` → `row.level`; `Exposure` → `formatDecimalString(row.exposure_years)`; `Claims` → `row.claim_count.toLocaleString()`; `Incurred` → `formatMinor(row.claim_amount_minor, props.currency)`; `Frequency` → `row.frequency?.toFixed(4) ?? null`; `Frequency CI` → `interval(row.frequency_ci, 4)`; `Severity` → `row.mean_severity == null ? null : (row.mean_severity / 100).toFixed(2)`; `Severity CI` → `interval(row.severity_ci, 2, 100)`; `Burning cost` → `row.mean_burning_cost == null ? null : (row.mean_burning_cost / 100).toFixed(2)` (keys: kebab-case of the label). `columns` becomes a `computed`, because `Incurred` reads `props.currency` |

**`DoubleLiftChart`'s exposure cell, checked:** today's cell is `exposureText.value[i]`, and
`exposureText` is `bins.value.map((b) => b.exposure_years)` when every value is a string
(`:39-42`). So `b.exposure_years` is the same value, and the column is present under the same
condition. The existing `cellUnder` assertions in `DoubleLiftChart.test.ts` (3) check it.

- [ ] **Step 1: Run the three existing test files on the Task 3 head.** Expected: FAIL, because
  the components still pass positional rows to the descriptor-only `ChartFigure`. Record it.
- [ ] **Step 2: Migrate the three sites** per the table. Keep the docstrings on the FR-10
  decimal strings (`HistogramChart.vue:96-100`, `DoubleLiftChart.vue:131-136`,
  `OneWayChart.vue:149-164`), moving each to sit above its descriptor array.
- [ ] **Step 3: Run** `pnpm --dir frontend exec vitest run src/components/__tests__/{HistogramChart,DoubleLiftChart,OneWayChart}.test.ts`.
  Expected: PASS. These three already read by `cellUnder` (4, 3 and 10 calls), so a pass shows
  that each value still sits under its heading.
- [ ] **Step 4: Type-check.** No error line names a Group B file. Record the remaining list.
- [ ] **Step 5: Check the two other positional readers.** For each `getAllByRole("cell")` in
  `GlmDiagnosticsPanel.test.ts` and `DiagnosticsView.test.ts`, read which table it reads. A
  `ChartFigure` table → convert it to `cellUnder`. A hand-written table → leave it, and say so
  in the ledger, one line per file.
- [ ] **Step 6: Commit.** `refactor(frontend): migrate the conditional-column ChartFigure sites (RL-1307, WK-675 S1)`.

### Task 5: Group C — columns generated per partition

**Files:**
- Modify: `frontend/src/components/AeByFactorChart.vue:64-82,89-90`,
  `CalibrationChart.vue:75-88,95-96`, `LiftChart.vue:77-94,101-102`
- Modify: `AeByFactorChart.test.ts`, `LiftChart.test.ts` (one positional read each)
- Create: `frontend/src/components/__tests__/CalibrationChart.test.ts`

**Interfaces:**
- Consumes: as Task 3.

**Keys use the partition's index, never its caption** (*Choices* 3): `p${index}-…`. A caption
is display text. Two partitions captioned alike must not produce a duplicate key.

`AeByFactorChart.vue`, the rows are the level labels (`levels.value`, strings), and `key()`
(`:28`) still identifies a cell:

```ts
import type { Column } from "@/chart-table";

const columns = computed<readonly Column<string>[]>(() => [
  { key: "level", label: "Factor and level", value: (level) => level },
  ...props.partitions.flatMap(([label, partition], index): Column<string>[] => {
    const cellAt = (level: string) =>
      partition.ae_by_factor.find((candidate) => key(candidate) === level);
    return [
      { key: `p${index}-ae`, label: `${label} A/E`, value: (level) => cellAt(level)?.ae ?? null },
      {
        key: `p${index}-exposure-years`,
        label: `${label} exposure years`,
        value: (level) => cellAt(level)?.exposure_years ?? null,
      },
    ];
  }),
]);
```

with `:rows="levels"`. Keep the FR-10 docstring (`:69-73`) above it.

| Site | `:rows` | Columns: label → accessor (key) |
|---|---|---|
| `CalibrationChart` | `bins` (numbers) | `Bin` → `bin` (`bin`); per partition `index`: `` `${label} predicted` `` → `partition.calibration.find((c) => c.bin === bin)?.predicted ?? null` (`p${index}-predicted`); `` `${label} actual` `` → `…?.actual ?? null` (`p${index}-actual`) |
| `LiftChart` | `bins` (numbers) | `Bin` → `bin` (`bin`); per partition `index`: `` `${label} rows` `` → `partition.lift.find((c) => c.bin === bin)?.rows ?? null` (`p${index}-rows`); `` `${label} predicted` `` → `…?.predicted ?? null` (`p${index}-predicted`); `` `${label} actual` `` → `…?.actual ?? null` (`p${index}-actual`) |

- [ ] **Step 1: Write `CalibrationChart.test.ts`, red first.** Mirror its parent's fixture
  (`git grep -ln 'CalibrationChart' -- frontend/src`). Test name `NFR-463: …`. Use two
  partitions (for example Train and Holdout) and read `Train predicted` and `Holdout actual`
  for one bin with `cellUnder`, comparing each with the fixture. **Add one case with two
  partitions sharing a caption** and assert the render succeeds with both columns present.
  That case fails if keys were built from captions. Run it on the unmigrated component.
  Expected: FAIL (positional rows reaching the descriptor-only component). Record the reason.
- [ ] **Step 2: Convert** the positional read in `AeByFactorChart.test.ts` and in
  `LiftChart.test.ts` to `cellUnder`, if each reads the `ChartFigure` table.
- [ ] **Step 3: Migrate the three sites.**
- [ ] **Step 4: Run** `pnpm --dir frontend exec vitest run src/components/__tests__/{AeByFactorChart,CalibrationChart,LiftChart}.test.ts`.
  Expected: PASS.
- [ ] **Step 5: Type-check the whole frontend.** `pnpm --dir frontend type-check; echo "rc=$?"`.
  Expected: `rc=0`. Every site is migrated, and the four fixtures' directives are all used.
  Re-run Task 0 Step 2's predicate on the branch and record that every file it prints was
  touched in Tasks 3 to 5, or in a site added under Task 0 Step 2.
- [ ] **Step 6: Commit.** `refactor(frontend): migrate the per-partition ChartFigure sites (RL-1307, WK-675 S1)`.

### Task 6: The gate, the bundle delta and the ledger

**Files:** the ledger; the PR body.

- [ ] **Step 1: The full gate, both halves** (`CLAUDE.md` §11), delegated to `gate-runner`,
  under a gate slot per `dev-commands`. Announce it first (`delivery-process.md` §8). Every
  command's rc is 0. Record the per-command table and the tree it ran on.
- [ ] **Step 2: The bundle delta** (`PL-1286` Acceptance 7). Build `origin/main` in a scratch
  worktree and the slice head in yours, each with `pnpm --dir frontend build`. Record Vite's
  chunk table from each, and list in the PR body every `dist/assets/*.js` chunk whose size
  changed, raw and gzip, before → after. Always include the shared entry chunk `index-*.js`.
  An increase is reported, not hidden. Expect a small change, since this slice adds no
  dependency.
- [ ] **Step 3: Self-check Acceptance 1–11** command by command. Paste each output into the
  ledger.
- [ ] **Step 4: Open the PR**, naming the range `origin/main...HEAD`, the F39 outcome (and,
  if the remedy did not land, the reason the auditor needs for the `FD-`), and the bundle delta.

## Hand-off

- **To the auditor at slice close:** F39's dated register resolution (Acceptance 9). The
  `PL-1286` `:285-286` note says F39's register cell still names "the frontend workstream"
  rather than WK-675, so `register-owed.py WK-675` misses it. The resolution text should name
  WK-675 S1 and the PR.
- **To WK-690 Slice 5 (SL-1275):** if S1 lands first, the loss-curve preview imports `Column`
  from `@/chart-table` and passes descriptors (`RL-1307` item 7). If it runs before S1, it
  records its caller, and S1's Task 0 picks it up.
- **To S6 onwards:** a new chart's test reads its table with `cellUnder` by label and compares
  each cell with the chart's source data (`RL-1307` §Acceptance, the fourth violation).

## Self-review

- **Ruling coverage, by site class** (`README.md` convention 5). `RL-1307` items 1, 3, 4 and 5
  and its four acceptance violations each appear in four places: the narrative (*What
  `RL-1307` rules*), the Files lists (Task 2: `chart-table.ts`, `ChartFigure.vue`,
  `test-tables.ts`, the fixtures; Tasks 3-5: the 13 sites), the Steps (Task 2 Steps 2-7;
  Tasks 3-5), and the Acceptance items (1 → item 1; 3 → violations 1 and 2; 4 → item 5 (i) and
  violation 3; 5 → item 5 (ii); 6 → item 5 (iii); 7 → item 4's `cellUnder` text; 8 → the
  fourth violation's form applied to migrated sites). Item 3 (`key` and `label` separate) sits
  in Task 2's interface, the equal-labels test, and Task 5's index-based keys.
- **Literals verified against the source at `1dd5e264`:** the 13 call-site lines; each site's
  header strings and row-building code (read in each file at the line ranges in the Files
  lists); the prop type names (`GbmEvalPoint`, `FeatureImportance`, `PermutationImportance`,
  `PartialDependence`, `DatasetLineage`, `PartitionCaption`, `PartitionDiagnostics`,
  `DoubleLift`, `Histogram`, `OneWaySummary`); `ChartFigure.vue`'s guard and empty-state text
  (`:60-72`, `:128`); `test-tables.ts`'s three statements (`:10-13`, `:18-21`, `:44-46`);
  `frontend/package.json:14` (`type-check`); `frontend/vitest.config.ts` (`happy-dom`).
  **Not verified:** the exact optionality of each generated field (for example whether
  `point.exposure_share` can be `undefined`). The type-check decides it, and Task 3 says how
  to respond.
- **Placeholders:** the one comment placeholder in Task 2 Step 4's sample is named as such,
  with an instruction to replace it. The two new view-fixture tests (Task 3 Step 1, Task 5
  Step 1) name their authority, the parent's existing fixture, rather than inventing data
  (`README.md` convention 3).
- **Rulings re-checked before the PR:** open PRs at 2026-10-01 10:07 BST (24, none touching
  `frontend/`, none ruling on `ChartFigure` or OQ-550). `RL-1307` was read at `1dd5e264`.
