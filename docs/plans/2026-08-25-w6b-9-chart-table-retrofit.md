# W6b-9 — The Chart/Table Retrofit Implementation Plan

**Status:** proposed, 2026-08-25. Awaiting the lead's arbitration on the two decisions in
[§Decisions for arbitration](#decisions-for-arbitration). **No code is written until that
line is signed.**

**Author:** `w6b-executor`, planning rather than building because `w6b-planner` is no longer
reachable and only the maintainer can restart it.

**Base:** `dbb4ea0` on `main` — W6b-1b (#194) merged.

---

## Global Constraints

- **`CLAUDE.md` §0** — Phase 1b, inside scope, so the deliverable is code. Where code and a
  spec disagree, stop and resolve rather than quietly making either match the other.
- **`CLAUDE.md` §2** — nobody hand-writes a shape `model-schema` already declares.
- **`CLAUDE.md` §13** — every enforcement proven on deliberately broken input; a check that
  has never printed a failure has not been tested.
- **`CLAUDE.md` §11** — both halves of the gate, each exit code read separately.
- **The slice map is frozen.** `docs/plans/2026-08-24-w6b-slice-map-revised.md` is not
  edited by this plan, including its `W6b-9` row and its chart count. F3 stands as filed and
  is the lead's.

---

## What this slice is, and what it is not

The map held `W6b-9` back on the argument that a shared chart/table fallback proven against
the two charts that existed then would be *a positive control run on the easy case*. #194
removed that objection by building `ChartFigure` once and proving it against nine charts in
a single slice. So `W6b-9` is now exactly the retrofit its name describes: **bring the charts
that predate the wrapper onto it.**

It adds no chart, no view, no route and no requirement. It changes what three existing
charts expose to a reader who cannot see a canvas.

---

## Scope, derived from the code

Ten components render an ECharts canvas (`git grep -l VChart -- src/`). Seven route their
table through `ChartFigure`; all seven landed in #194. Three do not, and each arrived before
the wrapper existed:

| Component | Added | Mounted by | Tabular equivalent today | Tests today |
|---|---|---|---|---|
| `OneWayChart.vue` | `17e35f7` (#53, W6a) | `ProfileView` | A table in the **view**, not the component — anonymous, and **missing the frequency CI** | **None.** No component test, and its only consumer stubs it |
| `HistogramChart.vue` | `667c8fe` (#113) | `ProfileView` column cards | **None** | 4, all against the chart option |
| `DoubleLiftChart.vue` | `4307b05` (#192, W6b-2) | `ModelComparisonView` | **None** | 5, all against the chart option |

`NFR-OVR-10` (`00` §9): *"Accessibility: the SPA meets WCAG 2.2 AA; all charts have an
accessible tabular equivalent."* It is a universal, and it is unmet outright in two of the
three and partially in the third. That is the whole of this slice's scope — three components,
not the map's eight and not the contract's nine.

Two things checked and deliberately excluded:

- **`EbmShapePanel.vue` renders a table and no chart.** It is the inverse case and satisfies
  the NFR trivially; making it draw a chart is a feature, not a retrofit.
- **`ColumnDrift.vue`** renders no canvas — it is a number and a band, already textual.

---

## Findings

### F1 — the one-way's tabular equivalent omits the one series it exists to publish

`OneWayChart` draws three things: exposure as bars, frequency as a line, and **the exact
Poisson interval per level as a custom-rendered whisker**. The component's own comment says
why the third is there:

> The exact Poisson interval (FR-DATA-26), drawn as a whisker per level. A frequency without
> one invites a decision the count cannot support — nine claims in a young-driver band look
> either significant or like noise depending entirely on this.

`ProfileView`'s hand-written table beneath it carries Level, Exposure, Claims, Incurred,
Frequency, Mean severity and Mean burning cost. **It does not carry the interval.** So a
reader on a screen reader receives the frequency and not the thing that says whether the
frequency means anything — the exact decision the whisker was drawn to prevent. The table is
also anonymous: no `aria-label` and no `<caption>`, so it cannot be addressed by name in the
accessibility tree or in a test.

This is not "no tabular equivalent". It is a tabular equivalent that is not equivalent, which
is the harder failure to see, because the page looks compliant.

### F2 — nothing in this repository relates a table header to a cell

`ChartFigure` takes `columns` and `rows` as two independent props:

```ts
columns: readonly string[];
/** Row-major, one array per row, in the same order as `columns`. */
rows: readonly (readonly (string | number | null)[])[];
```

"in the same order as `columns`" is a docstring, not a constraint. The component renders
whatever it is handed: a row shorter than `columns` renders fewer cells, a longer row renders
cells sitting under no header at all, and a row whose values are permuted renders every value
under the wrong heading. Nothing errors and nothing warns.

Nor is it caught downstream. Thirteen test files address cells positionally —
`within(row).getAllByRole("cell")[i]` — and **not one test in the repository resolves a
column by its header text.** A permutation of `rows` that leaves `columns` alone passes the
entire frontend suite, all 285 tests. This is constraint 3 as the lead put it, and the
mechanism is worse than "row-scoped assertions": the header and the cell are never compared
to each other by anything, at any layer.

A retrofit is precisely where this bites, because a retrofit's whole job is to hand
`ChartFigure` a `columns`/`rows` pair transcribed from a chart option that is already
correct. Three transcriptions, each of which the suite would accept scrambled.

### F3 — untouched

The slice map's "eight charts" against the contract's nine, with different membership. Filed
in the W6b-1b plan, arbitrated by the lead, not acted on here.

---

## Decisions for arbitration

### Decision 1 — how the `columns`/`rows` correspondence gets enforced (F2's answer)

**(a) A dev-time arity guard inside `ChartFigure`.** Each row's length must equal
`columns.length`; a mismatch throws in dev and test, and is stripped or downgraded in
production. Catches every arity error at every call site, present and future, including ones
this slice never touches. Catches no permutation — a scrambled row of the right length passes.

**(b) A header-resolving test helper.** `cellUnder(table, rowName, columnName)` resolves the
column index from the `columnheader` text, then indexes that row's cells. Every retrofit test
addresses values through it. Catches permutation exactly where it is asserted; catches
nothing at a call site nobody wrote a test for; depends on discipline that a later slice can
silently drop.

**(c) Both.** The guard is structural and unconditional, the helper is per-assertion and
catches the class the guard cannot. They fail on disjoint inputs, which is why one is not a
substitute for the other.

**Recommendation: (c).** Costs roughly twenty lines and one test file more than (b) alone,
and (a) alone leaves the failure mode that actually motivates the slice — a transcription in
the wrong order — undetected. Under §13 both halves get a broken-input proof: a short row, a
long row, and a permuted row, with the permuted row failing only under (b), which is the
evidence that (c) is not (a) with extra steps.

*(If the lead prefers, (a) can instead be a `columns`-keyed row type — `Record<string, …>` —
which makes permutation unrepresentable rather than detectable. Rejected as the default here
because it rewrites seven working call sites from #194 to fix a defect none of them has, and
`CLAUDE.md` §10 asks for the smallest sufficient change; raising it because "unrepresentable"
beats "checked" when the cost is not this high.)*

### Decision 2 — what becomes of `ProfileView`'s hand-written one-way table

**(a) Move it into `OneWayChart` via `ChartFigure`, as a superset, and delete the view's.**
One table, named, carrying every plotted series including the CI (F1) plus the four
statistics the chart does not plot. Cost: `OneWayChart` gains a `currency` prop, because
`Incurred` is formatted with `formatMinor(row.claim_amount_minor, currency)`, and the
component takes only `summary` today.

**(b) Two tables** — the view keeps its statistics table, the component gains a
chart-equivalent one (Level, Exposure, Frequency, CI). Cost: a screen reader meets the same
levels twice under one heading, which is worse than one table, not better.

**(c) Leave the view's table alone and add the CI column to it.** Cheapest, fixes F1, leaves
the equivalence uncoupled from the chart — the next person to add a series to `OneWayChart`
has no reason to look in `ProfileView`, which is how F1 happened.

**Recommendation: (a).** It is the only one of the three where adding a series to the chart
puts the series in the table by construction rather than by memory. The `currency` prop is a
real cost and is stated rather than hidden; note in passing that `ProfileView` defaults
`currency` to `"GBP"` when its prop is absent, which is a money-correctness question this
slice observes and does not touch.

---

## File Structure

```
frontend/src/components/
  ChartFigure.vue                     MODIFIED  arity guard (Decision 1a)
  OneWayChart.vue                     MODIFIED  ChartFigure + CI column + currency prop
  HistogramChart.vue                  MODIFIED  ChartFigure
  DoubleLiftChart.vue                 MODIFIED  ChartFigure
  __tests__/
    OneWayChart.test.ts               NEW       the baseline that does not exist today
    ChartFigure.test.ts               MODIFIED  broken-input proofs for the guard
    HistogramChart.test.ts            MODIFIED  table assertions via the helper
    DoubleLiftChart.test.ts           MODIFIED  table assertions via the helper
frontend/src/test/
  tables.ts                           NEW       cellUnder(), the header-resolving helper
frontend/src/views/
  ProfileView.vue                     MODIFIED  hand table deleted (Decision 2a)
  __tests__/ProfileView.test.ts       MODIFIED  stop stubbing OneWayChart, or assert in kind
```

---

## Tasks

Ordered so that nothing is retrofitted before it is testable, which is constraint 2.

### Task 1 — Test `OneWayChart` as it stands

No behaviour change. Pin what the component does today so the retrofit has something to
preserve: exposure as bars on the left axis, frequency as a line on the right, the CI series
carrying `[index, low, high]` per level with `null` where the interval is absent, the two
named y-axes, and the "This column has no stored one-way." empty state.

Also pin `Number(row.exposure_years)`: the value is an exact decimal **string** (FR-OVR-7)
and is converted for plotting only. A test that a level whose exposure is `"1234.56"` reaches
the option as the number `1234.56` and reaches the *table*, in Task 5, as the string — that
is the FR-OVR-7 boundary this component sits on, and it is currently asserted nowhere.

**Acceptance:** `OneWayChart.test.ts` exists with ≥6 tests, all green against unmodified
source. **§13 proof:** deleting the CI series from the option fails exactly one test; swapping
`yAxisIndex` on the frequency line fails exactly one.

### Task 2 — The correspondence enforcement (Decision 1)

`cellUnder(table, rowName, columnName)` in `src/test/tables.ts`, plus the `ChartFigure` arity
guard if (a) or (c) is signed.

**§13 proof, on deliberately broken input, three cases:** a row shorter than `columns`, a row
longer, and a row of the right length whose values are permuted. Under (c) the first two fail
the guard's test and the third fails a `cellUnder` assertion — which is the demonstration
that the two catch disjoint classes. If the third case passes everything, (c) has not been
built.

### Task 3 — Retrofit `HistogramChart`

Smallest and least coupled: no view owns any part of its table. Columns `Bin`, `Rows`,
`Exposure`, one row per bin, the bin label reusing the existing `"0–10"` edge formatting so
the table and the x-axis cannot disagree about a boundary. `Exposure` is present only when
the histogram carries it (`FR-DATA-48`); the column is omitted rather than filled with `—`
when the whole series is absent, and that choice gets a test in both directions.

### Task 4 — Retrofit `DoubleLiftChart`

Columns `Bin (by prediction ratio)`, `Exposure`, `Actual`, `Baseline predicted`,
`Challenger predicted`. The component already differentiates its three lines by line type as
well as hue for NFR-OVR-10's non-colour channel; the table is the second half of the same
requirement and each series must appear as its own column, named as the legend names it, so
the two channels cannot drift apart.

### Task 5 — Retrofit `OneWayChart` and reconcile `ProfileView` (Decision 2)

Under (a): `OneWayChart` takes `currency`, renders the superset table through `ChartFigure`,
and `ProfileView`'s hand-written table is deleted in the same commit — never left in place
"until the next slice", which would put two tables under one heading in a shipped build.

The CI column carries the interval as `low – high` in one cell, formatted to the same
precision as the frequency it qualifies, and `—` where `frequency_ci` is null. A frequency
with no interval must read as *no interval*, not as a zero-width one.

**`ProfileView.test.ts` stubs `OneWayChart`**, so none of these assertions run there. Either
un-stub it for the one test that checks the table reaches the page, or assert the equivalent
in `OneWayChart.test.ts` and say in the commit why the stub stays. The stub is what let F1
survive from #53 to now, so leaving it wholly unexamined is not an option.

### Task 6 — The gate, both halves, and the close

`ruff`, `mypy`, `lint-imports`, `pytest`, `audit-docs`, `req-coverage`,
`generate-contracts --check`, then `pnpm lint`, `type-check`, `test`, `build` — each exit
code read separately, never chained with `&&`.

Two known traps apply: vitest prints `Tests N passed` while exiting `1` when an error is
thrown outside a test (grep `Errors ` as well — recorded in `.claude/skills/dev-commands`),
and `req-coverage.py` cannot see the frontend, so no requirement here becomes evidenced by it
and an unchanged count is not a failure.

No demo-guide change is expected: `/data/:slug/v/:version/profile` and `/models/compare` are
already routed, and #194 fixed the query-stripping defect that made two such rows read as not
built. Confirm rather than assume.

---

## What would make this plan wrong

Stated so the lead can check the cheap things rather than re-derive the slice:

1. **If any of the three components already has a table I did not find.** The claim rests on
   reading each component's template and each mounting view around the mount point. The
   one-way's table *was* found this way, which is the evidence the method works; a fourth
   table somewhere else in a view would change F1's shape.
2. **If `ChartFigure`'s two-prop shape is deliberate** in a way I have not read. Its
   docstring explains why the table is always in the DOM and never behind a `<details>`; it
   says nothing about why `columns` and `rows` are unrelated types, and I take that silence
   as an unforced default rather than a decision.
3. **If the map's `W6b-9` row scopes work this plan drops.** The row is read as the retrofit
   its title describes; it is frozen and unedited either way, and a wider reading is the
   lead's to impose.
