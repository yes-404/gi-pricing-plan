---
id: RL-9852
family: ruling
title: OQ-550 decided — ChartFigure takes column descriptors that read each cell from the caller's own row
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 7040cf1e5ead768059398d3c2dc02404b1e695f7
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-550, RL-1184, NFR-463, PL-1286, PL-1268, PL-803]
---

# RL-9852 — OQ-550 decided: `ChartFigure` takes column descriptors that read each cell from the caller's own row

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort"). The session's
own `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`.

The record was prepared at effort `medium` (PR #936, head `5aef0637`, "PREPARED, NOT
RULED"). The preparation named one fact as deciding and not in evidence: whether vue-tsc
infers the row type of a generic `ChartFigure` at a real call site and reports a wrong
accessor. This pass established it by a spike on the locked toolchain (below), and rules.
It keeps the working id 9852; the id is minted at the lead's merge turn.

**Scope, as decided before this pass** (the maintainer by delegation, `to-lead.md` entry
"2026-09-30 00:51:17 BST — SCOPE DECISION: OQ-550 is owned by WK-675"): `RL-1184` E10
stands, OQ-550 is WK-675's and is decided at its map plan, and WK-690 Slice 5 consumes this
ruling if it exists by then. This record rules only the technical question.

## Verified first, at 7040cf1e5ead768059398d3c2dc02404b1e695f7

**The question, in both mirrors.** `docs/open-questions.md:41` asks whether `ChartFigure`
should relate a row's values to its column headers **by name** rather than by position,
gives options (a), (b), (c), recommends "(b) or (c)", owner WK-675, status **open**. The
mirror `docs/specs/00-overview.md:552` asks the same, shorter, status **open**. Re-opened by
`RL-1184` E10 on 2026-09-28; never closed on its merits before this record.

> **Lettering trap.** PL-803's Decision 1 "(c)" means *guard plus helper*, which is
> OQ-550's option **(a)**. A citation that says "(c) was chosen before" is backwards.

**The component** (`frontend/src/components/ChartFigure.vue`, unchanged since `aa14e90d`:
`git log --oneline aa14e90d..origin/main -- frontend/src/components/ChartFigure.vue
frontend/src/test-tables.ts` prints nothing):
- `columns: readonly string[]` and `rows: readonly (readonly (string | number | null)[])[]`
  are independent props. Their correspondence is the docstring "Row-major, one array per
  row, in the same order as `columns`."
- The arity guard, a computed that throws on a row-length mismatch only under
  `import.meta.env.DEV`, says of itself: *"It cannot see a row of the right length whose
  **values** are permuted."*
- `cellUnder` (`frontend/src/test-tables.ts:23`) reads a cell by its header, and only where a
  test uses it.

**Callers.** `git grep -n '<ChartFigure' origin/main -- 'frontend/src/*.vue'` prints 13
lines in 11 files. `git grep -n 'generic=' origin/main -- frontend/src` prints nothing; no
component uses a generic yet. `ChartFigure` has no backend or `model-schema` counterpart, so
`CLAUDE.md` §2's no-second-shape rule does not bind the component's own props. Planned new
callers: at least four WK-675 charts (`PL-1286` §Tasks) and WK-690 Slice 5's loss-curve
preview (`PL-1268` §Tasks, Slice 5).

**What WK-675 needs.** `PL-1286` §Decision points, row "DP-1 = OQ-550", is this question;
the plan is `draft` while DP-1 is open (`:28`, §Status). Its S1 "Chart foundation" applies
DP-1 and migrates the 13 call sites (§Tasks, `:303`). Acceptance item 5 (`:124-125`) asserts
each new chart's table *"with the column-by-name reader the ruling names"*.

**The toolchain.** `frontend/pnpm-lock.yaml` at this tree resolves `vue-tsc@3.3.11`,
`vue@3.5.43`, `typescript@5.9.3`. The primary checkout's installed `node_modules` holds
older versions (`vue-tsc` 3.3.9, `vue` 3.5.41), so the spike was run on a fresh install from
the lockfile, not on that one.

## The spike — the deciding fact

Scratch directory outside the repository (not committed):
`/tmp/claude-1000/-home-puzhenhao1989-gi-pricing-plan/3a4f8a8b-…/scratchpad/spike550`.
`package.json` and `pnpm-lock.yaml` were taken from `origin/main` by `git show`, and
`pnpm install --frozen-lockfile --ignore-scripts` installed `vue-tsc 3.3.11`, `vue 3.5.43`,
`typescript 5.9.3`. The `tsconfig.json` carries `frontend/tsconfig.app.json`'s compiler
options (`strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, …) minus the
build-mode keys. The component under test:

```vue
<script setup lang="ts" generic="T">
export type Cell = string | number | null;
export interface Column<R> { key: string; label: string; value: (row: R) => Cell }
defineProps<{ title: string; columns: readonly Column<T>[]; rows: readonly T[] }>();
</script>
```

Callers: one correct (`GoodCaller.vue`, inline column literals with untyped `(r) => r.band`),
and four deliberately broken. `./node_modules/.bin/vue-tsc -p tsconfig.json --noEmit`,
2026-09-30 08:43:30 UTC, verbatim:

```text
src/components/BadAccessor.vue(8,62): error TS2339: Property 'bnad' does not exist on type 'Band'.
src/components/BadCellType.vue(8,60): error TS2322: Type 'string[]' is not assignable to type 'Cell'.
src/components/Mismatch.vue(8,37): error TS2322: Type 'Band[]' is not assignable to type 'readonly Other[]'.
  Property 'level' is missing in type 'Band' but required in type 'Other'.
src/components/NoAnyLeak.vue(9,62): error TS2322: Type 'string' is not assignable to type 'number'.
all rc=2
```

With the four broken callers moved out, the same command on `GoodCaller.vue` alone: **rc 0**.
So at a real call site vue-tsc infers `T` from `rows`, types each inline accessor's
parameter as `T` (not `any`: `NoAnyLeak` fails on the inferred type), refuses a misspelt
field, refuses a value that is not a cell, and refuses columns written for another row type.

## Options

As prepared, unchanged:

| | Option | For | Against |
|---|---|---|---|
| (a) | Keep positional rows, plus the arity guard and `cellUnder` | No migration. | Order errors stay undetectable except where a test happens to use `cellUnder`. The guard is dev-only. The cost is paid again at every new caller: 13 today, at least 18 after WK-675 and WK-690. |
| (b) | Rows keyed by column name: `Record<K, Cell>`, with `K` constrained to `columns` | A missing or misspelt key is a compile error. The migration is mechanical at 13 sites. | A heading becomes an identifier, so renaming its text is a code change. Two cells can still be swapped under two correct keys. Compile-time checking **also needs a generic component**, so the plan's contrast "(c) makes it generic, (b) does not" is overstated. |
| (b′) | (b), but with `columns: {key, label}[]` and rows keyed by `key` | Keeps (b)'s checking, and label text is free to change. It also removes the `:key` collision. | A little more ceremony at each call site. Neither mirror lists this variant. |
| (c) | A column descriptor `{key, label, value: (row: T) => Cell}`, with rows that stay the caller's own objects | Heading and value source sit in **one object**, so a misaligned row cannot be expressed. Rows can be the generated API types themselves, so no transcription remains. Row length always equals the column count, so the arity guard retires by construction. | The largest change: a generic `T` over rows. Each of the 13 migrated sites is rewritten, not re-keyed. vue-tsc inference of `T` through the descriptor is unproven in this repository. |

The last "Against" clause of (c) is **discharged by the spike above**.

## Ruled

**Option (c), in the descriptor form `{ key, label, value }`.**

1. **The API.** `ChartFigure` becomes a generic component (`<script setup lang="ts"
   generic="T">`). It takes `rows: readonly T[]`, the caller's own row objects, and
   `columns: readonly Column<T>[]`, where a column is `{ key: string; label: string; value:
   (row: T) => Cell }` and `Cell` is `string | number | null`, as today. The table renders
   each cell as `column.value(row)`. `title` and `caption` are unchanged.
2. **Why (c).** The failure OQ-550 names is transcription: a value hand-copied into a slot
   that means something else. (b) and (b′) move the risk from position to key, but a value can
   still be written under the wrong key. (c) puts the heading and the value's source in one
   object, so a table whose value sits under the wrong heading cannot be written without the
   accessor itself being wrong, and the accessor is type-checked against the row. The one
   open cost, inference, is shown to hold at the locked versions. (c)'s remaining cost, a
   rewrite rather than a re-key at 13 sites, is paid once, before the 14th to 18th callers.
3. **`key` and `label` are separate, the (b′) half.** The register's (c) wrote `{ name, value
   }`. A single `name` would be both the heading text and the Vue `:key`, which keeps the
   present collision where two equal headings share a key. `label` is display text, free to
   change; `key` is an identifier, unique within a figure.
4. **The two W6b-9 checks — each kept or retired, with its reason** (`CLAUDE.md` §13):
   - **The dev-only arity guard retires, by construction.** Every row renders exactly one
     cell per column, so the class it caught (a row of the wrong length) can no longer be
     written. Its replacement check is the type-check failure above, which is stronger: it
     runs in CI and in the production build's `vue-tsc --build`.
   - **`cellUnder` stays.** It still reads hand-written tables (for example
     `DatasetListView`), and it is **the column-by-name reader** `PL-1286` acceptance item 5
     names: each new chart's table is asserted under test by reading cells under their
     `label`.
5. **Slice 1's scope, beyond the API** (`PL-1286` S1). The same slice (i) keys each `<th>`
   and `<td>` by the descriptor's `key` and refuses a duplicated `key` within one figure; (ii)
   renders the first column's cells as `<th scope="row">`, so each row is named for assistive
   technology (NFR-463); (iii) replaces the empty-state text "diagnostic" with wording that
   does not name one module, since rating views will use the component.
6. **Money.** A money value reaches a cell through its accessor, which formats integer minor
   units (FR-21) to a string. `Cell` stays `string | number | null`; no float money is
   introduced by this API, and none is made possible that was not before.
7. **One decision, one place.** OQ-550 is answered here, once. WK-690 Slice 5's loss-curve
   preview adopts this API if WK-675 Slice 1 has landed by then. Otherwise it adds its caller
   under the current API and records it in the call-site count, as the scope decision says,
   and WK-675 Slice 1 migrates it with the others.

**Not ruled here.** The migration order of the 13 sites inside S1, and the exact empty-state
wording: both are S1's.

**An `NFR-` amendment, not a new requirement.** NFR-463 already obliges "an accessible
tabular equivalent" for every chart. This ruling says how the equivalent is kept equal to its
chart, so NFR-463 carries a dated clause naming it.

## What it obliges

- **This commit:** `00` NFR-463 carries a dated clause. `OQ-550` is closed in both mirrors
  (`docs/open-questions.md` and `00` §10), citing this record.
- **The roadmap (the lead's file, not edited here):** the *Deferred / any time* row strikes
  `OQ-550` as decided by this record. A decided question keeps its row.
- **`PL-1286` (the planner's file, not edited here):** DP-1 has its resolver.
- **WK-675 Slice 1 (`PL-1286` S1):** items 1, 3, 4 and 5 above, with all 13 call sites
  migrated.

## Acceptance — the violation that must become detectable

The violation: **a `ChartFigure` table shows a value under a heading it does not belong
to.** Slice 1 carries the checks, each shown red on deliberately broken input:
- *Violation:* a call site's accessor reads a field the row type does not have, or returns a
  non-cell value. `pnpm --dir frontend type-check` fails. A deliberately broken fixture
  call site proves it, as the spike's `BadAccessor` and `BadCellType` do.
- *Violation:* columns written for one row type are passed with rows of another.
  `type-check` fails (the spike's `Mismatch`).
- *Violation:* two columns in one figure share a `key`. Refused, under test.
- *Violation:* a new WK-675 chart's table differs from its chart. Its test reads each cell
  with `cellUnder` by `label` and compares it with the chart's source data.
