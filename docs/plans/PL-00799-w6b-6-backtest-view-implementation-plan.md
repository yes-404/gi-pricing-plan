---
id: PL-799
family: plan
kind: leaf
title: W6b-6 Backtest View Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-25
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-25-w6b-6-backtest-view.md
---

# W6b-6 Backtest View Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render a stored backtest at `/models/:slug/backtests/:backtestId` — its single
`PartitionDiagnostics` through the four shared diagnostic instruments, captioned `Backtest`.

**Architecture:** Frontend-only, three files created and five modified. The one structural
change is a **`PartitionCaption` supertype**: the four shared instruments widen their caption
prop to it, while `PartitionLabel` and `partitions()` keep their exact present meaning, so
W6b-1b's surface loses no precision. No backend work — every requirement in this set is
already evidenced over HTTP.

**Tech Stack:** Vue 3 `<script setup lang="ts">` · vue-router 5.2.0 (function-mode props) ·
Vitest 4 + `@testing-library/vue` + happy-dom · ECharts via `vue-echarts` · Tailwind · pnpm.

**Spec:** [`../specs/02-modelling.md`](../specs/02-modelling.md) — FR-187, FR-94,
§4.12, §5.1, §5.3.

**Verified against `origin/main` `7f671d5`, 2026-08-25.** Every repository literal below —
route paths, field names, line numbers, template-string headings, fixture names — was read
from shipped source at that revision. A plan is frozen at its date
([`README.md`](README.md)): if the tree has moved, re-derive rather than editing this file.

---

## Global Constraints

Project-wide rules that every task below inherits. Copied verbatim from `CLAUDE.md` §2/§3 and
`frontend/tsconfig.app.json` at `7f671d5`.

- **Vue 3 Composition API with `<script setup lang="ts">` only** — never Options API, JSX, React.
- **Never hand-write an API type.** Every contract shape is `components["schemas"][...]` from
  `@/api/generated/schema`. That directory is **git-ignored**; regenerate with
  `pnpm --dir frontend generate:api` before type-checking in a fresh clone.
- **`tsconfig.app.json` runs `strict` plus four options that change what compiles:**
  `noUncheckedIndexedAccess` (so `arr[0]` is `T | undefined`), `exactOptionalPropertyTypes`
  (so `{ caption: undefined }` does **not** satisfy `caption?: string`), `noImplicitOverride`,
  `verbatimModuleSyntax` (so type-only imports must say `import type`).
- **Money is integer minor units, or Decimal in the rating path — never float.** Nothing in
  this slice carries money; the constraint is stated so a later reader does not have to check.
- **The gate has two halves and both must pass before pushing** (`CLAUDE.md` §11):
  ```bash
  uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
  python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
  pnpm --dir frontend lint && pnpm --dir frontend type-check
  pnpm --dir frontend test && pnpm --dir frontend build
  ```
- **The caption is exactly `"Backtest"`.** Not the period, not `slug@version`, not
  "Out-of-time" and not "Later period". This is spec, not preference — see the next section.

---

## What binds this slice

### The caption rule is already in the spec. This slice discharges it in code.

**The brief this plan was written from said W6b-6 owed a spec change. It no longer does.**
FR-187's caption limb landed on `origin/main` between `8d0dcf4` and `7f671d5`, both on
2026-08-25, and `02` §5.3's Backtest cell was corrected in the same change. An executor who
goes looking for a spec task will not find one; that is expected, not a gap.

FR-187 now states the general rule, quoted from `../specs/02-modelling.md`:

> **a caption for this partition may not assert a relationship the artifact does not carry.**
> […] **The caption is "Backtest"**, which claims only what the artifact is.

and gives the reasoning that rules out each near-miss: `"Holdout"` claims a split nobody made;
`"Out-of-time"` and `"Later period"` are refused *"for the same reason as 'holdout' — this
requirement demands a version **other than** the one fitted on, and §4.12's 'typically a later
period' is a description of the usual case, not an invariant, so a caption asserting lateness
claims something no validator checks."*

**FR-187 carries a split status and any closure record citing it must say which limb.**
Its row states this itself: *"Evidenced over HTTP 2026-08-23 (W32-6)"* discharges the artifact
limbs — the 202-and-`Location` contract, the read-back shape, both permission gates and the
refusals — while **the caption limb's verdict is `not started`, owner `W6b-6`**. The row also
warns why the distinction cannot be read off tooling: *"`req-coverage.py` will keep reporting
this id green off those backend markers whether or not any surface honours the caption rule,
because it scans backend tests only and cannot see a frontend assertion at all."*

**Task 3 is what discharges that limb**, and it does so by asserting the rendered heading
text — the only kind of evidence that exists for it.

### The §5.3 Contents cell binds nothing

FR-24 (`../specs/00-overview.md`) makes a §5.3 Contents cell prose that binds nothing,
with a **per-cell** carve-out for seven named cells. **Backtest is not among the seven** —
checked per-cell rather than assumed. Two consequences an executor will otherwise trip on:

- §5.3's *"Period-by-period A/E and lift"* is **non-binding prose and not a defect to fix**.
  `BacktestSummary` carries one optional window (`period_from`/`period_to`) and no period
  series at all. Do not build a period breakdown; there is no field to build it from.
- The floor is the **generated contract**, and OQ-587's decided rule of 2026-08-21 makes
  it *a floor and not a ceiling*: where this view needs something the contract lacks, **raise
  it as a new requirement at build time** and bring it to the maintainer. Never scope the view
  down to what the contract happens to carry, and never add a field silently.

### Requirement set and verdicts

Three requirements, all backend-evidenced. The other six of the pre-split set — FR-194,
77, 93, 98, 99, 124 — are prediction-side uncertainty and belong to **W6b-6b**, a separate
slice with its own plan. The split is clean: 3 + 6 = 9, nothing straddles.

| Requirement | Status entering this slice | What this slice adds |
|---|---|---|
| FR-187 | Artifact limbs evidenced over HTTP 2026-08-23 (W32-6); **caption limb `not started`, owner W6b-6** | Discharges the caption limb (Task 3) |
| FR-94 | Evidenced over HTTP — backtest readable by id | First frontend consumer of the read |
| §4.12 | Three `test_backtests` suites | — |

### A missing neighbour, which is a scope finding

**There is no backtest surface in the frontend at all, and no backtest test coverage.**
`git grep -n backtest origin/main -- frontend` returns exactly **one line**:
`frontend/src/api/__tests__/comparisons.test.ts:36`, where `"backtest:{uuid}"` appears as a
**negative fixture** — a ref `comparisonIdFromJob` must reject.

That zero is recorded here because `docs/plans/README.md` requires it: a module with no
neighbouring test for the verb under test has no coverage to mirror, and that belongs in a
plan's scope section rather than being discovered mid-task. Every test in this plan is new.
Where a pattern is needed, this plan names the file to mirror.

---

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `frontend/src/api/diagnostics.ts` | Modify (after `:40`) | Adds `PartitionCaption`; `PartitionLabel` and `partitions()` unchanged |
| `frontend/src/api/__tests__/diagnostics.test-d.ts` | **Create** | Type-level proof that the widening is a supertype and stays closed |
| `frontend/src/components/AeByFactorChart.vue` | Modify (`:9`, `:15`) | Caption prop widens |
| `frontend/src/components/CalibrationChart.vue` | Modify (`:9`, `:15`) | Caption prop widens |
| `frontend/src/components/LiftChart.vue` | Modify (`:9`, `:15`) | Caption prop widens |
| `frontend/src/components/PartitionTable.vue` | Modify (`:2`, `:14`) | Column type widens |
| `frontend/src/api/backtests.ts` | **Create** | `Backtest` types, `getBacktest`, `periodLabel` |
| `frontend/src/api/__tests__/backtests.test.ts` | **Create** | `periodLabel`'s four absence cases |
| `frontend/src/views/BacktestView.vue` | **Create** | The view |
| `frontend/src/views/__tests__/BacktestView.test.ts` | **Create** | Fetch, caption, degradation |
| `frontend/src/views/__tests__/fixtures.ts` | Modify (append) | `BACKTEST` fixture |
| `frontend/src/router/index.ts` | Modify | Route registration |
| `frontend/src/router/__tests__/index.test.ts` | Modify (append) | Resolution assertion |

---

## Task 1: `PartitionCaption` and the four shared instruments

**Files:**
- Modify: `frontend/src/api/diagnostics.ts:40` (append after the `PartitionLabel` line)
- Modify: `frontend/src/components/AeByFactorChart.vue:9,15`
- Modify: `frontend/src/components/CalibrationChart.vue:9,15`
- Modify: `frontend/src/components/LiftChart.vue:9,15`
- Modify: `frontend/src/components/PartitionTable.vue:2,14`
- Test: `frontend/src/api/__tests__/diagnostics.test-d.ts` (create)

**Interfaces:**
- Consumes: nothing.
- Produces: `export type PartitionCaption = PartitionLabel | "Backtest"` from
  `@/api/diagnostics`. The four components accept
  `readonly (readonly [PartitionCaption, PartitionDiagnostics])[]`
  (`PartitionTable`: `readonly PartitionCaption[]`). Task 3 depends on this.

### Why a supertype and not a wider `PartitionLabel`

Both options were recorded; the supertype was ruled on 2026-08-25. **Widening `PartitionLabel`
in place would make `partitions()`'s return type lie** — that function can only ever produce
`Train` and `Holdout`, and a signature advertising a third member is a false statement about
the function. Widen the consumer; keep the producer precise.

### The seam is measured, and it breaks nothing

`git grep -n PartitionLabel origin/main -- frontend/src` returns **ten occurrences in five
files**, all listed in the File Structure table above. Three facts follow, each checked:

- **Nothing consumes the union exhaustively.** There is no `Record<PartitionLabel, …>`, no
  `switch` on a `PartitionLabel`, and no colour or style map keyed by one. The only `switch`
  statements in `frontend/src` are in `ValidationBanner.vue`, on an unrelated `state`.
- **Every site is an input position.** A caller still passing `"Train" | "Holdout"` satisfies
  a wider parameter type. Widening a union breaks callers only where it is *produced* and
  exhaustively *consumed*; here it is neither.
- **Existing tests assert runtime values** from Train/Holdout fixtures — `diagnostics.test.ts:55`,
  `AeByFactorChart.test.ts:35`, `PartitionTable.test.ts:11,28`, `DiagnosticsView.test.ts:110`.
  A type-level widening cannot move any of them.

**Two things that look like counterexamples and are not.** Record them here so a later grep
does not re-open a settled measurement:

- `GbmEvalCurveChart.vue` hardcodes `"Train"`/`"Holdout"` at `:40,58,65` but **never imports
  `PartitionLabel`**. It is not wired to the union and widening cannot reach it. It passes
  `["Iteration","Train","Holdout"]` to `ChartFigure`, whose `columns` is `readonly string[]`,
  which is why it compiles today. It is not a sixth caller.
- `CalibrationChart.vue:43` (`values.length === 0`) and `:59-60` (`extent.value[0]`/`[1]`)
  look like partition-arity assumptions. They are not: `:43` counts plotted *values* and
  `:59-60` are the axis extent `[min, max]`. Neither indexes the partition list.

**`PartitionTable`'s narrow prop is deliberate, and widening does not weaken it.** Its
docstring: *"The partition columns are passed in rather than derived, so a caller cannot
render a holdout column for a diagnostic that has no holdout value […] A caller with one
partition passes one column."* That guard is about **column count**, enforced by passing
columns in rather than deriving them — not by the label vocabulary. A third admissible
caption leaves it exactly as strong.

- [ ] **Step 1: Write the failing type test**

Create `frontend/src/api/__tests__/diagnostics.test-d.ts`. Mirror
`frontend/src/api/__tests__/versions.test-d.ts` — same `expectTypeOf` idiom, same
describe/it shape.

```ts
import { describe, expectTypeOf, it } from "vitest";

import type { PartitionCaption, PartitionLabel } from "@/api/diagnostics";
import { partitions } from "@/api/diagnostics";

describe("PartitionCaption widens the presentation seam without widening the fit", () => {
  // FR-187: a backtest's single partition is neither of the fit's two, and calling it
  // a holdout "would claim a split nobody made". The instruments must accept a third
  // caption; the fit's own vocabulary must not gain one.
  it("admits every fit label, so no existing caller has to change", () => {
    expectTypeOf<PartitionLabel>().toExtend<PartitionCaption>();
  });

  it("admits the backtest caption, which PartitionLabel does not", () => {
    expectTypeOf<"Backtest">().toExtend<PartitionCaption>();
    expectTypeOf<"Backtest">().not.toExtend<PartitionLabel>();
  });

  // The point of the supertype rather than widening in place. `partitions()` can only ever
  // produce Train and Holdout, so a return type advertising a third would be a false
  // statement about the function.
  it("leaves partitions() producing exactly the fit's two", () => {
    expectTypeOf<Awaited<ReturnType<typeof partitions>>[number][0]>().toEqualTypeOf<PartitionLabel>();
  });

  // Closed, not `string`. A caption nobody specified is the defect FR-187 guards.
  it("stays a closed union", () => {
    expectTypeOf<PartitionCaption>().not.toEqualTypeOf<string>();
    expectTypeOf<"Out-of-time">().not.toExtend<PartitionCaption>();
  });
});
```

- [ ] **Step 2: Run it and confirm it fails for the right reason**

```bash
pnpm --dir frontend test src/api/__tests__/diagnostics.test-d.ts
```

`vitest.config.ts:45-49` sets `typecheck: { enabled: true, include: ["src/**/*.test-d.ts"] }`,
so `vitest run` **does** evaluate these assertions. They are not inert.

**Expected failure mode:** the import of `PartitionCaption` does not resolve — `diagnostics.ts`
exports no such type yet. The message names the missing export.

**This is a plan defect if the run fails any other way.** In particular, a failure reporting
that `"Backtest"` *does* extend `PartitionCaption` would mean the type already exists and the
seam has moved since `7f671d5`; stop and re-derive rather than editing the test to agree.

- [ ] **Step 3: Add the supertype**

In `frontend/src/api/diagnostics.ts`, immediately after line 40
(`export type PartitionLabel = "Train" | "Holdout";`) and **before** the `partitions()`
docstring:

```ts
/**
 * What a shared instrument may caption a column.
 *
 * `PartitionLabel` is the *fit's* two partitions and keeps that exact meaning — a backtest's
 * single partition is neither of them (FR-187), and the instruments interpolate whatever
 * they are given straight into a heading. Widening `PartitionLabel` itself would make
 * `partitions()` advertise a member it can never produce.
 *
 * Closed rather than `string`: FR-187 forbids a caption that "asserts a relationship the
 * artifact does not carry", so a new member is a spec question, not a type change.
 */
export type PartitionCaption = PartitionLabel | "Backtest";
```

- [ ] **Step 4: Widen the four instruments**

In each of `AeByFactorChart.vue`, `CalibrationChart.vue` and `LiftChart.vue`, change line 9
and line 15 — nothing else in those files changes:

```ts
import type { PartitionCaption, PartitionDiagnostics } from "@/api/diagnostics";
```
```ts
  partitions: readonly (readonly [PartitionCaption, PartitionDiagnostics])[];
```

In `PartitionTable.vue`, change line 2 and line 14:

```ts
import type { PartitionCaption } from "@/api/diagnostics";
```
```ts
  columns: readonly PartitionCaption[];
```

**Do not touch `PartitionTable.vue`'s docstring.** Its guard is about column count and is
still accurate word for word.

- [ ] **Step 5: Run the type test and the full frontend suite**

```bash
pnpm --dir frontend test
```
Expected: PASS, including every pre-existing `DiagnosticsView`, `PartitionTable`,
`AeByFactorChart`, `LiftChart` and `CalibrationChart` test. **Zero existing tests should
change.** If one needed editing, the widening was done wrong — re-read the seam measurement
above rather than adjusting the test.

- [ ] **Step 6: Type-check and lint**

```bash
pnpm --dir frontend type-check && pnpm --dir frontend lint
```
Expected: both clean.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/api/diagnostics.ts frontend/src/api/__tests__/diagnostics.test-d.ts \
  frontend/src/components/AeByFactorChart.vue frontend/src/components/CalibrationChart.vue \
  frontend/src/components/LiftChart.vue frontend/src/components/PartitionTable.vue
git commit -m "feat(w6b-6): widen the instrument caption seam to PartitionCaption"
```

---

## Task 2: The backtest API module

**Files:**
- Create: `frontend/src/api/backtests.ts`
- Test: `frontend/src/api/__tests__/backtests.test.ts` (create)

**Interfaces:**
- Consumes: `request` from `@/api/client`; `components` from `@/api/generated/schema`.
- Produces: `Backtest`, `BacktestSummary` types; `getBacktest(backtestId: string):
  Promise<Backtest>`; `periodLabel(summary: BacktestSummary): string | null`.

### Verified contract shapes at `7f671d5`

Read from `docs/contracts/openapi/generated.json` — the **generated** tier. (`docs/contracts/`
holds a generated tier and a hand-authored tier; there is no hand-authored `backtest.schema.json`,
so the generated one is the whole contract for this artifact.)

```
Backtest         required: id, model_id, dataset_version_id, computed_at, summary
                 job_id                     uuid | null
Backtest.summary → BacktestSummary
BacktestSummary  required: model_ref, dataset_version_ref, fitted_on_ref, partition
                 period_from, period_to     date | null   ← AND optional: absent OR null
                 partition                  → one PartitionDiagnostics
```

`packages/model-schema/src/model_schema/backtests.py:60-70` gives the reference forms, which
the fixture in Task 3 must match: `model_ref` is `model:{family}@{version}`,
`dataset_version_ref` is `dataset_version:{slug}@{version}`, and `fitted_on_ref` takes the
same form as `dataset_version_ref`. A `model_validator` there **rejects a summary whose
`dataset_version_ref` equals its `fitted_on_ref`** — the two must differ in any fixture.

### Two endpoints exist; this slice calls one

| Method | Path | Requirement | This slice |
|---|---|---|---|
| `GET` | `/api/v1/models/backtests/{backtest_id}` | FR-94 | **calls it** |
| `POST` | `/api/v1/models/{model_id}/backtest` | FR-187 | does not call it — no launcher |

**`GET /models/backtests/{id}` is not nested under the model.** The read is addressed by
backtest id alone, because a model has many — one per period it has been measured against
(FR-94). So the `:slug` in the view's route is for the breadcrumb and the fit link, and
**not** for the fetch.

### Do not build `backtestIdFromJob`. The ruling that removed the launcher removed its caller.

The brief this plan derives from carried a trap about reading `backtest:{id}` off a Job
result, with `frontend/src/api/comparisons.ts:36-53` as the precedent. **That trap is inert
under the no-launcher ruling and this plan deliberately does not discharge it.** Nothing in
this slice ever holds a backtest Job: the view receives a uuid from the URL. A
`backtestIdFromJob` built now would be an exported function with no caller — speculative
scaffolding, and untestable against any real flow.

**It becomes live the moment a launcher is built**, which is the finding booked below. Whoever
builds it should read the prefix off `backend/src/app/worker/model_handlers.py:1308` —
`JobResult(kind="artifact", ref=f"backtest:{backtest_id}")` — and match it **in full**, for
the reason `comparisons.ts` records at its own constant: the worker writes
`model_comparison:`, not the `comparison:` the analogy invites, and a loose prefix check would
also accept the `model:{uuid}` a fit job emits.

### A contract/runtime difference that is not a spec disagreement

Worth knowing before anyone writes a POST test. `POST /models/{id}/backtest` is documented as
**202 with a `Location` header** — `backend/src/app/api/models.py:926-927` sets both — but the
**generated contract declares `200`**. This is not a defect and needs no reconciliation: the
handler mutates `response.status_code` at runtime, which FastAPI's schema generation cannot
see. Eight of the twelve Job-returning POSTs in the contract are in this position; the four
that declare `202` set it in the decorator instead. **Do not "fix" either side.**

- [ ] **Step 1: Write the failing test**

Create `frontend/src/api/__tests__/backtests.test.ts`. Mirror
`frontend/src/api/__tests__/comparisons.test.ts` — pure-function tests, no fetch stubbing.

```ts
import { describe, expect, it } from "vitest";

import { periodLabel } from "@/api/backtests";
import type { BacktestSummary } from "@/api/backtests";

// Only the two fields `periodLabel` reads. Annotated and cast at the call rather than
// `as BacktestSummary` inline, so a required field added to the contract does not silently
// pass here — the cast is in one place and says exactly what it hides.
// (`comparisons.test.ts:9-12`'s `jobWith` is the precedent for this shape.)
function summaryWith(period: Partial<BacktestSummary>): BacktestSummary {
  return period as BacktestSummary;
}

describe("periodLabel", () => {
  // FR-187 calls a backtest "the evidence bridge into 05-monitoring.md", and
  // `backtests.py` adds that "a deterioration nobody can date is not evidence of drift".
  // So the window is shown whenever the artifact carries one.
  it("reads a closed window as a range", () => {
    expect(periodLabel(summaryWith({ period_from: "2025-01-01", period_to: "2025-12-31" })))
      .toBe("2025-01-01 to 2025-12-31");
  });

  // Both fields are optional AND nullable, so absence has two representations and the view
  // must not print an empty date for either. Null is the wire form; undefined is what an
  // omitted key deserialises to.
  it("returns null when the artifact declares no window at all", () => {
    expect(periodLabel(summaryWith({ period_from: null, period_to: null }))).toBeNull();
    expect(periodLabel(summaryWith({}))).toBeNull();
  });

  // A half-open window is representable: `backtests.py`'s validator only orders the pair
  // when both are present, so one-sided is a state the artifact can reach.
  it("names which end it has when only one is declared", () => {
    expect(periodLabel(summaryWith({ period_from: "2025-01-01", period_to: null })))
      .toBe("from 2025-01-01");
    expect(periodLabel(summaryWith({ period_from: null, period_to: "2025-12-31" })))
      .toBe("to 2025-12-31");
  });
});
```

- [ ] **Step 2: Run it and confirm it fails for the right reason**

```bash
pnpm --dir frontend test src/api/__tests__/backtests.test.ts
```

**Expected failure mode:** the module `@/api/backtests` does not resolve — the file does not
exist. Vitest reports a failed import, not a failed assertion.

A run that instead reports *assertion* failures would mean the module already exists; stop and
find out who wrote it before overwriting.

- [ ] **Step 3: Write the module**

Create `frontend/src/api/backtests.ts`:

```ts
import { request } from "./client";
import type { components } from "./generated/schema";

export type Backtest = components["schemas"]["Backtest"];
export type BacktestSummary = components["schemas"]["BacktestSummary"];

/**
 * One stored backtest, by its own id (FR-94, `02` §5.1).
 *
 * Not nested under the model: a model has many backtests — one per period it has been
 * measured against — so unlike `Diagnostics` there is no "the" backtest for a model to fetch.
 * A caller who has just run one reaches it through the Job's `backtest:{id}` result.
 */
export function getBacktest(backtestId: string): Promise<Backtest> {
  return request<Backtest>(`/models/backtests/${encodeURIComponent(backtestId)}`);
}

/**
 * The period the backtested version covers, or null when it declares none.
 *
 * Both fields are **optional and nullable**, so absence arrives as `null` from the wire and
 * as `undefined` from an omitted key, and neither may render as an empty date. A one-sided
 * window is a real state: `backtests.py`'s ordering validator only fires when both ends are
 * present.
 *
 * The caption is deliberately not built from this (FR-187) — a period in a column
 * heading would assert a relationship the artifact does not carry.
 */
export function periodLabel(summary: BacktestSummary): string | null {
  const from = summary.period_from ?? null;
  const to = summary.period_to ?? null;
  if (from !== null && to !== null) return `${from} to ${to}`;
  if (from !== null) return `from ${from}`;
  if (to !== null) return `to ${to}`;
  return null;
}
```

- [ ] **Step 4: Run the test**

```bash
pnpm --dir frontend test src/api/__tests__/backtests.test.ts
```
Expected: PASS, 3 tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/backtests.ts frontend/src/api/__tests__/backtests.test.ts
git commit -m "feat(w6b-6): read a stored backtest by id"
```

---

## Task 3: The backtest view and its route

**Files:**
- Create: `frontend/src/views/BacktestView.vue`
- Create: `frontend/src/views/__tests__/BacktestView.test.ts`
- Modify: `frontend/src/views/__tests__/fixtures.ts` (append)
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/router/__tests__/index.test.ts` (append)

**Interfaces:**
- Consumes: `getBacktest`, `periodLabel`, `type Backtest` from `@/api/backtests` (Task 2);
  `PartitionCaption` from `@/api/diagnostics` (Task 1); `getModel`, `type Model` from
  `@/api/models`; `weightingLabel` from `@/api/diagnostics`; `ProblemError` from `@/api/problem`.
- Produces: `BacktestView.vue` with `defineProps<{ slug: string; backtestId: string }>()`, and
  the route named `model-backtest`.

### Trap: slug addressing versus id addressing

`GET /models/{slug}` and `/models/{slug}/diagnostics` are **slug**-addressed; the view's route
carries `:slug`. But the backtest read is by **backtest id**, and `POST /models/{id}/backtest`
takes a **uuid**. W6b-1b never had to resolve one to the other.

**The precedent to mirror is `frontend/src/views/ModelDetailView.vue:99`** —
`artifact.value = await getTransparency(loaded.id)`, where `loaded` is the `Model` returned by
`getModel(slug)` and `Model.id` is the uuid. This view needs the same shape only if it comes
to need a `model_id`; for the read it does not, because `backtestId` arrives from the URL.
Fetch the model for the breadcrumb and the fit link, not to address the backtest.

### Trap: no Train/Holdout anywhere in this view

One partition, one column, one series. A reviewer should be able to grep the rendered output
for `Holdout` and get nothing. If a Train/Holdout pair appears, something called `partitions()`
that should not have.

### Bypassing `partitions()` is correct here, and the reason is not the obvious one

The view **cannot** call `partitions()`: that helper takes a `UniversalDiagnostics` and a
`BacktestSummary` has none. It will hand-build `[["Backtest", summary.partition]]`, which is
textually the pattern the helper exists to stop. This needs an answer at the call site rather
than silence, because a reviewer who checks the pattern rather than the hazard will file it as
a defect.

**The answer is in the helper's own docstring.** It names the hazard precisely: it exists
*"so that every universal instrument iterates the same pair in the same order […] a chart that
plotted holdout first would compare against the neighbouring chart wrongly."* The guarded
hazard is **inconsistent ordering between two partitions**. That is arity-dependent, and **at
one element there is no order to get wrong.** The backtest view reproduces the *shape* of the
pattern while the *risk* it carried does not exist here.

**Do not add a single-partition helper.** The durable reason: **a one-partition helper would
have no invariant to enforce.** A helper earns its place by holding something steady across
call sites; `partitions()` earns its by fixing train-then-holdout order for every universal
instrument. At one partition there is no order to fix and no field to choose. *That there is
currently only one call site is a supporting fact, not the reason* — facts of that kind expire.

**Reopen condition, greppable and stated with its current count.** The question returns when a
**second single-partition instrument caller** exists, because then there *is* an invariant: the
two would have to agree on the caption vocabulary.
`git grep -c ": PartitionDiagnostics" origin/main -- packages backend` returns **3** at
`7f671d5` — `diagnostics.py:179` (`train`), `:180` (`holdout`), `backtests.py:72` (`partition`).
So the trigger is **a fourth declaration, or any hit outside those two files**. *"A third
declaration"* is already true today and would fire immediately; `UniversalDiagnostics`
contributes two of the three. **W6b-6b is not the trigger** — `Prediction` and `PredictedRow`
carry no partition at all.

**A citation to retire, and not to reproduce in the call-site comment.** `partitions()`'s
docstring continues: *"There is no matching helper for `glm`, `complexity` or
`cross_validation`: those declare neither field […]"*. That sentence **does not reach a
backtest** and must not be cited for it: its scope clause is *"those declare **neither**
field"*, describing artifacts with no partition data at all, where a partition-listing helper
would be nonsense. A backtest declares exactly one, so `[["Backtest", partition]]` would be
*accurate*. The conclusion above is unchanged; the reason is narrower. A code comment is
exactly where an over-wide citation survives longest — nobody re-greps a comment against the
docstring it paraphrases.

- [ ] **Step 1: Add the fixture**

Append to `frontend/src/views/__tests__/fixtures.ts`. **Reuse `DIAGNOSTICS.universal.train` as
the partition rather than hand-writing a `PartitionDiagnostics`** — that shape has nine fields
and inventing values for them would put unverified literals in a fixture. Add the import of
`Backtest` to the existing type imports at the top of the file.

```ts
/**
 * One stored backtest (FR-94). The partition is borrowed from `DIAGNOSTICS` rather than
 * written out: a `PartitionDiagnostics` is the same shape wherever it appears, and a second
 * hand-built copy is a second thing to keep true.
 *
 * `dataset_version_ref` and `fitted_on_ref` **must differ** — `backtests.py`'s
 * `_a_backtest_is_not_run_on_the_data_it_learned_on` validator rejects a summary where they
 * match, so an equal pair here would be a fixture the backend could never have produced.
 */
export const BACKTEST: Backtest = {
  id: "0e3f7a1c-1111-4222-8333-444455556666",
  model_id: "1a2b3c4d-5555-4666-8777-888899990000",
  dataset_version_id: "2b3c4d5e-6666-4777-8888-999900001111",
  computed_at: "2026-07-01T09:30:00Z",
  job_id: null,
  summary: {
    model_ref: "model:motor-frequency@3",
    dataset_version_ref: "dataset_version:motor@9",
    fitted_on_ref: "dataset_version:motor@4",
    period_from: "2025-01-01",
    period_to: "2025-12-31",
    partition: DIAGNOSTICS.universal.train,
  },
};
```

- [ ] **Step 2: Write the failing view test**

Create `frontend/src/views/__tests__/BacktestView.test.ts`. **Mirror
`frontend/src/views/__tests__/DiagnosticsView.test.ts` for the harness** — the ECharts mock,
`stubByUrl`, the `mounted` stubs and `pathOf` are all defined there and this file needs the
same four. Copy them rather than importing: that file does not export them.

```ts
import { render, screen, within } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import BacktestView from "../BacktestView.vue";
import { BACKTEST, GBM_MODEL } from "./fixtures";

// Same reason as `DiagnosticsView.test.ts:14-24`: ECharts paints to a canvas happy-dom does
// not provide, and the unhandled `clearRect` on null exits vitest 1 while printing every test
// as passed. Each chart asserts its own `option` in its own file; this file tests the tables,
// the captions and the fetches.
vi.mock("vue-echarts", () => ({
  default: { name: "VChart", props: ["option"], template: "<div data-testid='chart' />" },
}));

const NOT_FOUND = {
  type: "about:blank",
  title: "Not Found",
  status: 404,
  code: "NOT_FOUND",
  detail: "No such backtest.",
};

function stubByUrl(routes: Record<string, { status?: number; body: unknown }>): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    for (const [path, response] of Object.entries(routes)) {
      if (url.includes(path)) {
        return new Response(JSON.stringify(response.body), {
          status: response.status ?? 200,
          headers: { "content-type": "application/json" },
        });
      }
    }
    return new Response(JSON.stringify(NOT_FOUND), {
      status: 404,
      headers: { "content-type": "application/problem+json" },
    });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

const mounted = { global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } };
const props = { slug: "motor-frequency", backtestId: BACKTEST.id };

// `/models/backtests/` is matched before `/models/motor-frequency`, because the backtest path
// does not contain the slug at all and the looser key must not answer both.
function stubBoth(backtest: unknown = BACKTEST): ReturnType<typeof vi.fn> {
  return stubByUrl({
    "/models/backtests/": { body: backtest },
    "/models/motor-frequency": { body: GBM_MODEL },
  });
}

afterEach(() => vi.unstubAllGlobals());

describe("BacktestView", () => {
  it("fetches the backtest by its own id, not under the model", async () => {
    const fetchMock = stubBoth();
    render(BacktestView, { props, ...mounted });
    await screen.findByRole("table", { name: /headline metrics/i });
    const paths = fetchMock.mock.calls.map((call) => new URL(String(call[0])).pathname);
    expect(paths).toContain(`/api/v1/models/backtests/${BACKTEST.id}`);
  });

  // FR-187's caption limb. This assertion is the only evidence that limb can have:
  // `req-coverage.py` scans backend tests and cannot see a frontend caption at all.
  it("captions the single partition Backtest, and shows no fit partition", async () => {
    stubBoth();
    render(BacktestView, { props, ...mounted });
    const table = await screen.findByRole("table", { name: /headline metrics/i });
    expect(within(table).getAllByRole("columnheader").map((h) => h.textContent?.trim())).toEqual([
      "Metric",
      "Backtest",
    ]);
    // "would claim a split nobody made" — neither fit label may appear anywhere in the view.
    expect(screen.queryByText(/holdout/i)).toBeNull();
    expect(screen.queryByText(/\btrain\b/i)).toBeNull();
  });

  it("shows the period the backtest covers", async () => {
    stubBoth();
    render(BacktestView, { props, ...mounted });
    expect(await screen.findByText(/2025-01-01 to 2025-12-31/)).toBeInTheDocument();
  });

  // Both period fields are optional and nullable, so this is an ordinary artifact and not an
  // error state. The view must not print an empty date.
  it("renders a backtest that declares no period", async () => {
    const undated = {
      ...BACKTEST,
      summary: { ...BACKTEST.summary, period_from: null, period_to: null },
    };
    stubBoth(undated);
    render(BacktestView, { props, ...mounted });
    await screen.findByRole("table", { name: /headline metrics/i });
    expect(screen.getByText(/no period declared/i)).toBeInTheDocument();
  });

  it("shows the problem detail when there is no such backtest", async () => {
    stubByUrl({});
    render(BacktestView, { props, ...mounted });
    expect(await screen.findByText(/no such backtest/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 3: Run it and confirm it fails for the right reason**

```bash
pnpm --dir frontend test src/views/__tests__/BacktestView.test.ts
```

**Expected failure mode:** `../BacktestView.vue` does not resolve — the component does not
exist, so the import fails before any assertion runs.

**A failure whose message is a missing `headline metrics` table would mean the component
exists and renders wrongly** — a different situation, and one to investigate rather than
implement over.

- [ ] **Step 4: Write the view**

Create `frontend/src/views/BacktestView.vue`. The `<template>` is not reproduced field by
field below — mirror `DiagnosticsView.vue:200-220` for the instrument block and the
`PartitionTable` wiring, which is the layout this view is a one-column case of.

```vue
<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { getBacktest, periodLabel, type Backtest } from "@/api/backtests";
import { weightingLabel, type PartitionCaption, type PartitionDiagnostics } from "@/api/diagnostics";
import { getModel, type Model } from "@/api/models";
import { ProblemError } from "@/api/problem";
import AeByFactorChart from "@/components/AeByFactorChart.vue";
import CalibrationChart from "@/components/CalibrationChart.vue";
import LiftChart from "@/components/LiftChart.vue";
import PartitionTable from "@/components/PartitionTable.vue";

const props = defineProps<{ slug: string; backtestId: string }>();

const backtest = ref<Backtest | null>(null);
const model = ref<Model | null>(null);
const loading = ref(true);
const problem = ref<ProblemError | null>(null);

/**
 * The backtest's one partition, in the shape the four shared instruments take.
 *
 * **Built here rather than through `partitions()`, deliberately.** That helper takes a
 * `UniversalDiagnostics` and a `BacktestSummary` has none. It exists to fix train-then-holdout
 * order across instruments, so that "a chart that plotted holdout first would compare against
 * the neighbouring chart wrongly" — a hazard between *two* partitions. At one element there is
 * no order to get wrong, and a one-partition helper would have no invariant to hold.
 *
 * **Revisit if a second single-partition caller appears**, because two of them would have to
 * agree on the caption vocabulary and that is an invariant worth a helper.
 *
 * The caption is `"Backtest"` and may not be the period or the `slug@version`: FR-187
 * forbids a caption that asserts a relationship the artifact does not carry, and the
 * instruments interpolate it straight into a heading (`${label} A/E`).
 */
const partition = computed<readonly (readonly [PartitionCaption, PartitionDiagnostics])[]>(() =>
  backtest.value === null ? [] : [["Backtest", backtest.value.summary.partition]],
);

const period = computed(() =>
  backtest.value === null ? null : periodLabel(backtest.value.summary),
);

const weighting = computed(() =>
  backtest.value === null ? null : weightingLabel(backtest.value.summary.partition.weighting),
);

/** FR-171's scalar metrics, one column because there is one partition. */
const headline = computed(() => {
  const found = backtest.value;
  if (found === null) return [];
  const p = found.summary.partition;
  return [
    { name: "Rows", values: [p.rows] },
    { name: "Overall A/E", values: [p.ae_overall] },
    { name: "Gini", values: [p.gini] },
    { name: "Normalised Gini", values: [p.gini_normalised] },
  ];
});

/**
 * All six fields `ResidualSummary` declares, not four — `p01` and `p99` are the tails, the
 * part of a residual distribution a reviewer reads first. `DiagnosticsView.vue` records the
 * same list and the same reason.
 */
const RESIDUAL_FIELDS = ["mean", "std", "minimum", "maximum", "p01", "p99"] as const;

const RESIDUAL_LABELS: Record<(typeof RESIDUAL_FIELDS)[number], string> = {
  mean: "Mean",
  std: "Std dev",
  minimum: "Minimum",
  maximum: "Maximum",
  p01: "P01",
  p99: "P99",
};

const residuals = computed(() => {
  const found = backtest.value;
  if (found === null) return [];
  const summary = found.summary.partition.residual_summary;
  return RESIDUAL_FIELDS.map((field) => ({
    name: RESIDUAL_LABELS[field],
    values: [summary[field]],
  }));
});

onMounted(async () => {
  try {
    // The backtest is addressed by its own id (FR-94); the model is fetched only for
    // the breadcrumb and the link back to the fit, never to address the backtest.
    backtest.value = await getBacktest(props.backtestId);
    model.value = await getModel(props.slug);
  } catch (error) {
    if (error instanceof ProblemError) problem.value = error;
    else throw error;
  } finally {
    loading.value = false;
  }
});
</script>
```

The template must render, in addition to the instrument block mirrored from
`DiagnosticsView.vue:200-220`:

- `<PartitionTable title="Headline metrics" :columns="['Backtest']" :rows="headline" />` and a
  second `PartitionTable` for `residuals` — `PartitionTable` puts `title` on the table's
  `aria-label`, which is what the tests query by.
- The three instruments, each `:partitions="partition"`.
- `period` when it is non-null, and the literal text **"No period declared"** when it is null.
  Do not render an empty date and do not treat the absence as an error.
- `model_ref`, `dataset_version_ref` and `fitted_on_ref` rendered as text. **Render them raw.**
  `comparisons.ts` exports a `parseModelRef`, but reusing it here would couple backtests to the
  comparison module for a display nicety; the refs are unconstrained strings in the contract.
- The weighting label (FR-184), and `computed_at`.
- The `problem` state — mirror `DiagnosticsView.vue`'s branch, which is what makes the
  `detail` string findable by the last test.

- [ ] **Step 5: Register the route**

In `frontend/src/router/index.ts`, add after the `model-diagnostics` entry. **Function-mode
props, matching every other model route** — note the comment at that entry explaining that
`props: true` maps `route.params` only:

```ts
  {
    // `02` §5.3's Backtest view. Addressed by backtest id, not by model — a model has many
    // (FR-94) — so `:slug` here is for the breadcrumb and the link back to the fit.
    path: "/models/:slug/backtests/:backtestId",
    name: "model-backtest",
    component: () => import("@/views/BacktestView.vue"),
    props: (route) => ({
      slug: String(route.params.slug),
      backtestId: String(route.params.backtestId),
    }),
  },
```

There is no ordering hazard: this path has four segments and collides with nothing. The
existing `/models/compare` and `/models/new` records both carry measurements showing a static
segment outranks a dynamic one from either position.

- [ ] **Step 6: Assert resolution in the router test**

Append to `frontend/src/router/__tests__/index.test.ts`, mirroring the assertions already
there — that file asserts **resolution** rather than declaration order, which is the property
that matters and survives reordering.

```ts
  it("resolves a backtest to its own view, with both params", () => {
    const resolved = router.resolve("/models/motor-frequency/backtests/0e3f7a1c-1111-4222-8333-444455556666");
    expect(resolved.name).toBe("model-backtest");
    expect(resolved.params.slug).toBe("motor-frequency");
    expect(resolved.params.backtestId).toBe("0e3f7a1c-1111-4222-8333-444455556666");
  });
```

Read the file's existing `router` construction before writing this — mirror how the
neighbouring tests obtain it rather than building a second router.

- [ ] **Step 7: Run the whole frontend gate**

```bash
pnpm --dir frontend test && pnpm --dir frontend lint && \
  pnpm --dir frontend type-check && pnpm --dir frontend build
```
Expected: all four clean, with five new `BacktestView` tests, one new router test, three
`backtests` tests and four `diagnostics.test-d` type assertions.

- [ ] **Step 8: Run the Python and docs half**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
```
Expected: clean. **Nothing in this slice touches Python**, so a failure here is either a stale
`.venv` (run `uv sync --all-packages`) or a pre-existing condition on the branch — not this
slice's change.

- [ ] **Step 9: Commit**

```bash
git add frontend/src/views/BacktestView.vue frontend/src/views/__tests__/BacktestView.test.ts \
  frontend/src/views/__tests__/fixtures.ts frontend/src/router/index.ts \
  frontend/src/router/__tests__/index.test.ts
git commit -m "feat(w6b-6): the backtest view, captioning its one partition Backtest"
```

---

## Findings to book at closure

Both are for the closure record's element 5. **Neither is W6b-6 work**, and `CLAUDE.md` §13
admits no silent fifth verdict — each gets one of the four.

**1. No UI path exists to create or find a backtest.** *Deferred, owner unassigned.*

Ruled out of scope 2026-08-25: the slice map scopes W6b-6 to the registered §5.3 view, and
`POST /api/v1/models/{id}/backtest` already exists — so the gap is a **missing UI affordance,
not a missing capability**. It is still a real gap: after this slice ships, the platform has a
view onto an artifact it gives the user no way to create and no way to list. A user reaches it
only by holding a Job result — in practice by having just run one, or by pasting a uuid.

Two things the launcher will need, recorded so they are not re-derived: `backtestIdFromJob`
(Task 2 explains why it is not built now), and `RunBacktest.dataset_version_id`, documented in
the contract as *"Must be validated, and must not be the version the model was fitted on nor a
part of its split (FR-187) — typically a later period."*

**If the view turns out not to function without a launcher, that is a new requirement raised
at build time and it goes to the maintainer — never a silent addition.**

**2. No list-backtests-by-model route exists anywhere.** *Not started — and reasoned, not missed.*

FR-94 states the reason: *"By backtest id rather than by model, because unlike
`Diagnostics` a model has many — one per period it has been measured against. The Job's result
carries the id (`backtest:{id}`), which is how a caller who has just requested one reaches
it."* A future plan that assumes an index page to link from is assuming a route nobody wrote,
and adding one is a spec change rather than a view (`CLAUDE.md` §0).

---

## Explicitly not in scope

- **The prediction view — that is `W6b-6b`**, with its own plan and its own six requirements
  (FR-MODEL-63, 77, 93, 98, 99, 124).
- **Any backend change.** All three requirements in this set are evidenced; the caption limb is
  discharged by a frontend assertion, which is the only evidence it can have.
- **A period-by-period breakdown.** The artifact has no period series — see FR-24 above.
- **A backtest launcher, and a list-by-model route.** Both booked as findings.
- **Reconciling the contract's `200` against the documented `202`.** Task 2 explains why that
  difference is a schema-generation limit and not a defect.

---

## Self-review

**Spec coverage.** FR-187's artifact limbs are backend-evidenced and untouched; its
caption limb is discharged by Task 3 step 2's second test, which is the assertion the
requirement's own row says nothing in the repository yet makes. FR-94 is consumed by
Task 2's `getBacktest` and asserted by Task 3's first test. §4.12's shape decisions — one
artifact, one `PartitionDiagnostics`, `fitted_on_ref` stored — are all reflected in the fixture
and its validator note. §5.3's non-binding "period-by-period" is answered explicitly rather
than left as an apparent gap.

**Placeholder scan.** No TBD, no "add error handling", no "similar to Task N". The one place
this plan does not supply literal code is `BacktestView.vue`'s `<template>`, and per
`docs/plans/README.md`'s third unenforced convention it names the authority instead —
`DiagnosticsView.vue:200-220` — rather than inventing markup whose class strings and ARIA roles
were not read from source.

**Type consistency.** `PartitionCaption` is produced by Task 1 and consumed by Task 3 under
that exact name. `getBacktest`/`periodLabel` are declared in Task 2's Interfaces block and used
under those names in Task 3. `BACKTEST` is the fixture name in both the fixture step and every
test. `partition` is the computed's name in the view and `:partitions` the prop it feeds.

**Known limit of this plan's evidence.** The `<template>` assertions in Task 3 — the
`headline metrics` accessible name, the "No period declared" text — are strings **this plan
specifies**, not strings read from existing source. They are testable and consistent between
the test and the template instruction, but an executor who renames one must rename both.
