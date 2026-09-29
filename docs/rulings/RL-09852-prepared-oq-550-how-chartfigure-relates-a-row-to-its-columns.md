---
id: RL-9852
family: ruling
title: PREPARED, NOT RULED — OQ-550, how `ChartFigure` relates a row's values to its columns
status: draft                  # PREPARED, NOT RULED — see the banner; RL's §1.2 subset has no draft (reported to the lead)
created: 2026-09-30
owner: decision-maker
tree: aa14e90dd77c7461aa35cc6461557b129959463f
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [OQ-550, RL-1184, NFR-463]
---

# RL-9852 (working id) — PREPARED, NOT RULED: OQ-550, how `ChartFigure` relates a row to its columns

> **Nothing in this record is ruled.** It was prepared at medium effort, under the
> maintainer's decision by delegation (lead channel, 2026-09-30 00:42 BST, "the DM PREPARES
> the blocked rulings"). It carries evidence, options and a **provisional** recommendation
> only. Do not rely on it. No slice may activate on it, no open question is closed by it, and
> no spec, gate row or plan is amended by it. The ruling is a later pass at effort high, which
> re-reads this record and then confirms or revises it.

## Evidence, read at `aa14e90dd77c7461aa35cc6461557b129959463f` (origin/main)

**The question, in both mirrors.**
- The register is `docs/open-questions.md:41`. It asks whether `ChartFigure` should relate a
  row's values to its column headers **by name** rather than by position.
  - The row gives options (a), (b) and (c).
  - It recommends "(b) or (c)".
  - The owner is WK-675 at its map plan, and the status is **open**.
- The mirror is `docs/specs/00-overview.md:552`. It gives the same question, owner and status
  in a shorter form: it does not letter the options or name a recommendation.
- The two mirrors agree in substance.

**Why it is open again.** `RL-1184` E10 re-opened it
(`docs/rulings/RL-01184-…-gate-rows.md:154-161`), in the deputy's words: *"its trigger fired
(#257 added a `ChartFigure` caller; there are now 13 call sites). Re-open it as a WK-675
entry decision, due at WK-675's map plan"*. No record has ever closed OQ-550 on its merits.
It was deferred on 2026-08-25, the deferral was confirmed on 2026-08-26, and it was re-opened
on 2026-09-28.

> **Lettering trap.** PL-803's Decision 1 "(c)" (`docs/plans/PL-00803-…:151-185`) means
> *guard plus helper*, which is OQ-550's option **(a)**. A citation that says "(c) was chosen
> before" is backwards.

**The component.** `frontend/src/components/ChartFigure.vue`:
- **Props (lines 31-39).** `columns: readonly string[]` and `rows: readonly (readonly
  (string | number | null)[])[]` are independent props. Their correspondence exists only in
  a docstring: "Row-major, one array per row, in the same order as `columns`."
- **Arity guard (lines 60-72).** A computed property throws on a row length mismatch, only
  when `import.meta.env.DEV` is set. It cannot detect values in the wrong order, and it is not
  in the production build.
- **Test helper.** `frontend/src/test-tables.ts:23` defines `cellUnder`, which reads a cell by
  its header text. It checks order only where a test uses it.
- **Latent defect.** The component keys each `<th>` by the column text (`:key="column"`), so
  two equal headings collide.
- **Diagnostics-only wording.** The empty-state text says "diagnostic", and the body has no
  `<th scope="row">`. Both are wrong for rating views.

**Callers.**
- There are 13 `<ChartFigure` call sites in 11 files, all under `frontend/src/components/`.
  Predicate: `git grep -n '<ChartFigure' origin/main -- 'frontend/src/*.vue'`.
- No open branch changes `frontend/`. The branches checked were `wk675-map-plan`,
  `p2-wk690-map`, `p2-wk690-rl`, `p2-f2-rs`, `p2-wk673-map`, `p2-wk673-rl` and
  `worktree-planner-p2-wk674-s1`.
- The new callers exist only in plans:
  - WK-690 Slice 5's loss-curve preview (working id 9103, `origin/p2-wk690-map` at `69be18ae`,
    lines 529-530).
  - At least four WK-675 charts (working id 9681, `origin/wk675-map-plan` at `1a2427f1`).
- There is no backend or `model-schema` counterpart. `git grep ChartFigure` over `backend/`
  and `packages/` finds nothing, so CLAUDE.md §2's no-second-shape rule does not bind here.

**What constrains the answer.**
- `NFR-463` (`docs/specs/00-overview.md:529`): "all charts have an accessible tabular
  equivalent". A table that differs from its chart fails that requirement silently.
- Money is never a float (`FR-21`). This matters for cell typing in rating views.
- Vue `^3.5.43` and vue-tsc `^3.3.11` (`frontend/package.json:23,47`) support
  `<script setup generic="…">`. No component at this tree uses it yet
  (`git grep -n 'generic=' origin/main -- frontend/src` finds nothing).

**What WK-675 needs.**
- Working id 9681's DP-1 is this question. That plan recommends **(b)**, stays `draft` until
  DP-1 is ruled, and makes Slice 1 ("Chart foundation") migrate all 13 call sites first.
- Its acceptance item 5 asserts each new chart "with the column-by-name reader the ruling
  names". The ruling must therefore say whether `cellUnder` stays.

## Options

| | Option | For | Against |
|---|---|---|---|
| (a) | Keep positional rows, plus the arity guard and `cellUnder` | No migration. | Order errors stay undetectable except where a test happens to use `cellUnder`. The guard is dev-only. The cost is paid again at every new caller: 13 today, at least 18 after WK-675 and WK-690. |
| (b) | Rows keyed by column name: `Record<K, Cell>`, with `K` constrained to `columns` | A missing or misspelt key is a compile error. The migration is mechanical at 13 sites. | A heading becomes an identifier, so renaming its text is a code change. Two cells can still be swapped under two correct keys. Compile-time checking **also needs a generic component**, so the plan's contrast "(c) makes it generic, (b) does not" is overstated. |
| (b′) | (b), but with `columns: {key, label}[]` and rows keyed by `key` | Keeps (b)'s checking, and label text is free to change. It also removes the `:key` collision. | A little more ceremony at each call site. Neither mirror lists this variant. |
| (c) | A column descriptor `{key, label, value: (row: T) => Cell}`, with rows that stay the caller's own objects | Heading and value source sit in **one object**, so a misaligned row cannot be expressed. Rows can be the generated API types themselves (for example the dislocation and ladder shapes that WK-675 consumes), so no transcription remains. Row length always equals the column count, so the arity guard retires by construction. | The largest change: a generic `T` over rows. Each of the 13 migrated sites is rewritten, not re-keyed. vue-tsc inference of `T` through the descriptor is unproven in this repository. |

## Provisional recommendation: (c), with (b′) as the fallback. This departs from the planner's (b).

**Why (c).**
- The failure OQ-550 names is *transcription*: a value is hand-copied into a slot that means
  something else. Only (c) removes the transcription.
- (b) and (b′) move the risk from *position* to *key*, but a value can still be written under
  the wrong key.
- The planner prefers (b) because "(c) makes it generic". But (b) needs a generic component
  too, so the cost difference is the accessor per column, not genericity.
- WK-675's new charts read generated API types. Under (c), those types feed the table
  directly, which is also closest to CLAUDE.md §2's spirit: the platform does not restate a
  shape in a second form.

**Why the fallback.** The deciding fact is not in evidence at this tree: does vue-tsc infer
`T` through `columns` and `rows` at a real call site, and does it report a wrong accessor? If
the high-effort pass cannot establish that, it should choose (b′). (b′) still makes the
common errors (a missing column or a misspelt key) into compile errors, with no inference
risk.

**What the ruling should also settle, whichever option it picks.**
1. **Sequencing.** WK-690 Slice 5's loss-curve preview adopts the ruled shape. Working id
   9103, lines 529-530, says that Slice 5's leaf plan "revisits OQ-550". That conflicts with
   `RL-1184` E10, which assigns OQ-550 to WK-675. The ruling should state that the question
   is answered once, here. Otherwise a 14th positional caller can land before WK-675 Slice 1
   migrates the others.
2. **The two W6b-9 checks.** For each check, state whether it is kept or retired, with the
   reason. Retiring one silently would drop a proven check (CLAUDE.md §13).
   - Under (c), the arity guard retires by construction.
   - `cellUnder` stays in every option. It still reads hand-written tables such as
     `DatasetListView`, and it is the "column-by-name reader" that working id 9681's
     acceptance needs.
3. **Slice 1's scope.** It also fixes the heading-text `:key` collision, the "diagnostic"
   empty-state text and the missing `<th scope="row">` row headers.
4. **The mirrors.** At the ruling, OQ-550 closes in both `docs/open-questions.md` and
   `00` §10 with the resolver cited, and the roadmap Deferred row is updated in the same
   commit.

## What would change the provisional recommendation

- **A spike showing vue-tsc cannot infer `T` usefully.** Choose (b′).
- **Evidence that a heading must stay a stable identifier** (for example, exported column
  names). Then (b)'s cost of renaming by code becomes a benefit.

## Ruled

**Nothing.** This section is held for the high-effort pass, which writes the ruling here or
replaces this record. The provisional recommendation above is not a ruling.

## What it obliges

**Nothing yet.** When the ruling is made, it obliges the items listed under "What the ruling
should also settle": WK-675 Slice 1's migration and its extra fixes, WK-690 Slice 5's
adoption of the ruled shape, the kept-or-retired decision on each W6b-9 check, and the
mirror, gate-row and close edits for OQ-550.

## Acceptance — the violation that must become detectable

**Not set, because the option is not ruled.** Under the provisional (c): a `ChartFigure` call
site that supplies a row value unrelated to its column heading can no longer be written,
because each value comes from its own column's accessor. Under (b′): a row missing a column
key, or carrying a key not in `columns`, fails `pnpm --dir frontend type-check`. In both
cases a deliberately broken call site in a test fixture must print that failure (CLAUDE.md
§13).
