---
id: PL-8054
family: plan
kind: map
title: WK-675 — Slice 7 (SL-1550), the sandbox compare view: its components, its own_change label rule and its red-first tests: a dated Work-plan delta to PL-1546
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-16
owner: planner
tree: 0877e6e7a756c4621890713a4d3b016e75e33654
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1546, PL-1286, SL-1550, SL-1548, SL-1549, SL-1367, RL-1261, LG-1699, LG-1673, RL 8057]   # RL 8057 in working-id (space) form until the mint, which writes its minted id
---

# PL-8054 — WK-675 Slice 7 (SL-1550): the sandbox compare view and its red-first tests (delta to PL-1546)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5. It follows
> `document-ids.md` §1.6, PL row: *"a change is one dated Work-plan delta, a new `PL-` that
> `relates:` the Work's plan"*. It changes **one row** of
> [`PL-1546`](PL-01546-wk-675-slices-5-to-11-work-plan-delta.md): row 4, `SL-1550`. It adds the
> design and the test list that row and `PL-1286`'s S7 row leave open. `PL-1546`'s body is
> frozen and is not edited. **Read `PL-1286`'s S7 row (`:309`) and Acceptance item 8
> (`:131-133`) first, then `PL-1546` row 4 (`:149`) and Acceptance item 7 (`:107-108`), then this
> file. Where they differ, this file is the later statement.** The executor binds what
> `PL-1546`'s header names: `vue-frontend`, `vue-best-practices`, `vue-testing-best-practices`,
> `test-driven-development`, `dev-commands` and `git-hygiene`. This delta adds no skill. The
> executor is spawned from `.claude/roles/executor.md`. Its `LG-` quotes `PL-1546` row 4 and
> this file's §"Tasks" as its scope. REQUIRED SUB-SKILL: subagent-driven-development
> (recommended) or executing-plans.

Filed under **working id 8054**, reserved by the lead (`~/gi-pricing-plan.local/handover/eta.md`,
"2026-10-16 09:33:10 BST — Lead: RESERVED PL 8054 = the SL-1550 (lane C S7) red-first test
design (planner-1550), or its LG task plan if the planner shows that is the right vehicle"). Written 2026-10-16 by the planner
(seat planner-1550). **Tree read:** `origin/main` `0877e6e7a756c4621890713a4d3b016e75e33654`
(#1307, 2026-10-16T09:23:54+01:00). Every `file:line` below was read at that tree. **No test
was run at planning time.**

**Amended 2026-10-16 by the planner (seat planner-8054b), before this file's first
merge, applying RL 8057** (working id; branch `rl-8057-pl8054-dps-2026-10-16` at
`368685f9b8dba835a16f2faaa538548b823d5cfb`, reserved by the lead in `eta.md`, "2026-10-16
09:42:47 BST — Lead: RESERVED RL 8057"). RL 8057 rules DP-1 (a) and DP-2 (a), and corrects one
premise: `GET /api/v1/rating-versions` has **no** `03` §5.1 row. The changes, each marked
*(amended … RL 8057)* at its site: Context 5 and 7; the Files table (`03-rating-engine.md`);
Task 2 Step T1 (the §5.1 row, verbatim); C1 and B5 tied to RL 8057's Acceptance; §"Decision
points" (both ruled, DP-1's premise corrected); Acceptance items 9 and 10; Global Constraints;
Self-review. **`status:` stays `draft`**: both blocking rows have a resolver, but the maintainer's confirmation of RL 8057 in `to-lead.md`, "2026-10-16 09:49:25 BST — Maintainer: RL 8057 (PL 8054 DP-1 (a), DP-2 (a), SL-1550 lane C S7) CONFIRMED",
condition (3), reads *"RL 8057 is minted in the next batch in id order, and PL 8054 activates
only after it is on main."* Its conditions (1) and (2) are carried at T1, Acceptance 9, C1
and B5, each citing 09:49:25. `relates:` names RL 8057 in working-id (space) form, which check
32 does not resolve; the mint writes its minted id there and at T1. *(Amended 2026-10-16, before
the mint, by the planner, on the lead's mint-time edit list (lead handover 2026-10-16 §7, "PL 8054
relates+T1 id"): the sentence read "RL 8057 stays out of `relates:` until it is minted (check 32);
the mint adds it.")*

## Why a delta, and not the slice's ledger

The `LG-` is the executor's file (`document-ids.md` §1.6, LG row: *"executor, appends per task
and per PR"*; SL row: the executor *"writes the `LG-`'s scope, tasks, gate and build log"*). A
planner does not write it. The design below is a change to what a Work-plan row says, so under
L5 it is a new `PL-` that `relates:` the Work's plan. There is no per-slice leaf plan. The
precedent is `PL-1668`, the same kind of delta for S5 (row 1).

## Context — what is open, and what changed since `PL-1546` (tree `60e9254c`)

1. **The rows name no test.** `PL-1546:149` (row 4) says only *"`PL-1286` S7 row | `03` §3.8:
   FR-262 (view limb); §4.10's `own_change` rendering rule"*. `PL-1286:309` says *"FR-262's view
   limb over `POST /score/compare`; the `own_change` rendering rule"*. Neither names a
   component, a label text, a mount point or a test.
2. **No compare code exists in `frontend/`.** At this tree, `git ls-tree -r --name-only
   origin/main frontend/src | grep -iE 'sandbox|compare|score'` prints only S6's files:
   `api/score.ts`, five components under `components/sandbox/` with their tests,
   `views/QuoteSandboxView.vue` and its test. `api/score.ts` has `scoreQuote` only (`:20-25`).
   `QuoteSandboxView.vue` calls `scoreQuote` only (`:62-68`).
3. **The meaning of `own_change: false` changed on 2026-10-12.** `SL-1549` (S7b, `LG-1699`)
   delivered `RL-1261`. `03` §4.10 struck the bullet *"`own_change: false` means 'no own change
   attributable from the traces'. It never means 'unchanged' or 'not edited'"* (`03:951`), with
   the note *"`false` now means the step's own definition is the same on both sides"*. The
   generated `StepChange.own_change` description now reads: *"False means the step's own
   definition is the same on both sides and it differs in the traces only through what it
   consumed; a definition that changed but whose trace is identical for this quote is not
   listed at all."* (`docs/contracts/openapi/generated.json`, `components.schemas.StepChange`).
   **`PL-1286` Acceptance item 8 (`:131-133`) and its reason at `:274-276` quote the struck
   meaning.** The label rule below satisfies item 8 as written: no label for any `StepChange`
   contains "unchanged" or "not edited". It is also true under the new meaning. So this delta
   raises no decision point on item 8. It records that item 8's stated reason is stale.
4. **The F5 case now reads `own_change: true`.** Item 8 asks for *"a compare-view test with an
   edited step whose input also moved"*. After `SL-1549`, that step reads `own_change: true`
   (`03:952`, struck: *"an edited downstream step whose input also moved now reads
   `own_change: true`"*). The view test for item 8 asserts the label for that case (test B1).
5. **`RL-1261` left one view question to WK-675's map plan, and no plan has decided it.**
   `RL-1261:100-104`: *"Whether the view should also show 'edited, no effect on this quote' is
   a view design question for WK-675's map plan."* `git grep -n 'no effect' origin/main --
   docs/plans/PL-01286-* docs/plans/PL-01546-*` prints nothing. This is DP-2. *(amended 2026-10-16 by the planner (seat planner-8054b), pre-merge, applying RL 8057, working id)*:
   RL 8057 answers it for WK-675: **no**, the sandbox does not show "edited, no effect on this
   quote"; FR-219's structural diff overlay in the DAG designer (`03` §5.3) is where an edit is
   read. Nothing is carried.
6. **`LG-1699`'s audit flagged a mounted case for this slice.** `LG-1699:88`: *"no HTTP test
   mounts a sub-graph … flagged for `SL-1550`'s view tests if a mounted case is wanted"*. Test
   B4 covers it at the view: a namespaced `step_id` is shown as it is, with no special case.
7. **Activation needs, each read on `docs/roadmap.md` at this tree:** `SL-1548` (S6)
   `status: closed`; `SL-1549` (S7b) `status: closed`; `SL-1367` `status: closed`; `RL-1261`
   `status: active`. All are met. **`SL-1550` stays `draft` until DP-1 and DP-2 are ruled.**
   **Added need (amended 2026-10-16, on the maintainer's confirmation of RL 8057 in `to-lead.md`, "2026-10-16 09:49:25 BST — Maintainer: RL 8057 (PL 8054 DP-1 (a), DP-2 (a), SL-1550 lane C S7) CONFIRMED", condition (3)):** RL 8057 is minted, in the
   next batch in id order, and is on `origin/main`. **This plan moves `draft → active` only
   then**, and SL-1550 is not GO'd before it. Check (the title's last clause, which no mint rewrites):
   `git grep -l 'the sandbox compare shows only what this quote shows' origin/main -- docs/rulings`
   prints one file, and its `id:` is a minted `RL-` id.
   *(amended 2026-10-16 by the planner (seat planner-8054b), pre-merge, applying RL 8057, working id)*: both are ruled (a) by RL 8057. `SL-1550`'s `draft → active` is the lead's at GO;
   this plan does not edit its row.

## Goal

Build FR-262's view limb in the quote sandbox. An actuary picks a comparison version and
scores one quote. The page then shows both results, side by side, and the step-by-step
difference of their traces. Each changed step carries a label that says what `own_change`
means and never says "unchanged" or "not edited".

## Spec and contract read (all at `0877e6e7`)

- **FR-262** (`03:183`): *"The **Quote Sandbox** lets an actuary score an arbitrary quote against
  any accessible Rating Version and see the full trace inline, alongside the same quote scored
  against a comparison version with a step-by-step difference. … The Quote Sandbox view is
  WK-675's."*
- **The route** (`03:1060`): `POST /api/v1/score/compare`, **200** `ScoreComparison`. *"422 for a
  `context` carrying its own `options.rating_version_ref`"*. *"A per-quote error on either side
  answers 422 with that code, and the problem names the failing side"*. 404 and 409 name their
  side the same way. The side is a prefix on `detail`: `backend/src/app/api/score.py:455-457`,
  `detail = f"{side}: {problem.detail}"`.
- **§4.10** (`03:914-954`): `steps` lists base steps in base order, then added steps in
  comparison order. `base` or `comparison` is `null` on the side where the step is missing.
  `unchanged` counts the steps with identical traces.
- **The view and its route** (`03:1410`; `00:430`): *"Quote sandbox | `/rating/:slug/v/:version/sandbox`
  | … side-by-side compare against another version"*. **Compare is inside the sandbox route.
  No new route.** FR-25 is met by the sandbox route's existing reachability.
- **The generated shapes** (`generated.json`, `components.schemas`):
  - `ScoreCompareRequest`: `context` (`QuoteContext`), `base` and `comparison` (`ArtifactRef`),
    all required.
  - `ScoreComparison`: `base` and `comparison` (`ScoringResult`), `diff` (`TraceDiff`), all
    required.
  - `TraceDiff`: `steps` (`StepChange[]`), `unchanged` (integer ≥ 0), both required.
  - `StepChange`: `step_id`, `change` (`added` \| `removed` \| `changed`) and `own_change`
    required; `changed_fields` (subset of `type`, `label`, `consumed`, `produced`, `matched`,
    `violation`), `base` and `comparison` (`TraceStep` or `null`) optional.
  - `ScoringResult` requires `outcome`, `rating_version_ref`, `bundle_hash`, `premium_ladder`.
    `TraceStep` requires `step_id` and `type`.
- **The frontend uses generated types only** (`CLAUDE.md` §2, §3). The types come from
  `frontend/src/api/generated/schema` (responses) and `.../schema.requests` (request bodies), as
  `api/score.ts:1-11` already does.
- **No chart is added.** The step difference is a table. NFR-463's chart-table rule does not
  apply. WCAG 2.2 AA does: the label is text, never colour alone.

## The design

### Files

| File | Change | Responsibility |
|---|---|---|
| `docs/specs/03-rating-engine.md` | Modify | **T1** (Task 2 Step T1): the §5.1 row for `GET /api/v1/rating-versions`, verbatim from RL 8057, above the `GET /api/v1/rating-versions/{slug}@{version}` row. Records an existing route; no behaviour or shape changes *(amended 2026-10-16 by the planner (seat planner-8054b), pre-merge, applying RL 8057, working id)* |
| `frontend/src/api/score.ts` | Modify | Add the generated aliases `ScoreComparison`, `StepChange`, `ScoreCompareRequest` and `scoreCompare()` |
| `frontend/src/components/sandbox/stepChange.ts` | Create | `stepChangeLabel(change: StepChange): string`, the one place the label rule lives |
| `frontend/src/components/sandbox/QuoteComparison.vue` | Create | The compare panel: a summary table (both sides) and the step-difference table |
| `frontend/src/views/QuoteSandboxView.vue` | Modify | The "Compare against" picker; scoring through `scoreCompare` when a comparison is chosen; mounting `QuoteComparison` |
| `frontend/src/components/sandbox/__tests__/stepChange.test.ts` | Create | Tests A1–A6 |
| `frontend/src/components/sandbox/__tests__/QuoteComparison.test.ts` | Create | Tests B1–B6 |
| `frontend/src/views/__tests__/QuoteSandboxView.test.ts` | Modify | Tests C1–C6, and the two new mocked exports |

**Why `QuoteOutcome` is not reused for the comparison side.** `QuoteOutcome.vue:18-25` renders
`aria-labelledby="outcome-heading"` with `id="outcome-heading"` and `data-testid="outcome"`. Two
instances on one page give a duplicate `id` (a WCAG defect), and the S6 view test's
`findByTestId("outcome")` (`QuoteSandboxView.test.ts:107`) would find two. The comparison side is
summarised in `QuoteComparison`'s own table instead.

### The label rule (exact text)

`stepChangeLabel` returns, for one `StepChange`:

| `change` | `own_change` | `"consumed"` in `changed_fields` | Label |
|---|---|---|---|
| `added` | (always true) | — | `Added in comparison` |
| `removed` | (always true) | — | `Removed in comparison` |
| `changed` | `true` | no | `Edited` |
| `changed` | `true` | yes | `Edited; its inputs also changed` |
| `changed` | `false` | (any) | `Changed through its inputs` |

- **Row 4 is item 8's case.** It is the edited step whose input also moved, and after
  `SL-1549` the backend reports it `own_change: true` (Context 4). Its label names both causes.
- **Row 5 is `own_change: false`.** Its label is true under the current meaning (Context 3): the
  definition is the same and the step moved through what it consumed. It contains neither
  "unchanged" nor "not edited", so `PL-1286` item 8 and `PL-1546` item 7 hold.
- **No label contains `unchanged` or `not edited`** (case-insensitive), for any of the 12
  combinations of `change` × `own_change` × `consumed` present. Test A6 holds this.
- The `unchanged` count is written as **`{n} steps unchanged for this quote`**. "For this
  quote" is exact: `RL-1261:100-101` says a step whose definition changed but whose trace is
  identical is counted there. This text is in the step table's caption, never in a row.

```ts
// frontend/src/components/sandbox/stepChange.ts
/**
 * The label a compare row carries for one StepChange (03 FR-262, §4.10; RL-1261).
 * `own_change: false` means the step's definition is the same on both sides and it moved only
 * through what it consumed. No label says "unchanged" or "not edited" (PL-1286 item 8).
 */
import type { StepChange } from "@/api/score";

export function stepChangeLabel(change: StepChange): string {
  if (change.change === "added") return "Added in comparison";
  if (change.change === "removed") return "Removed in comparison";
  if (!change.own_change) return "Changed through its inputs";
  return (change.changed_fields ?? []).includes("consumed")
    ? "Edited; its inputs also changed"
    : "Edited";
}
```

### `api/score.ts` additions

```ts
export type ScoreComparison = components["schemas"]["ScoreComparison"];
export type StepChange = components["schemas"]["StepChange"];
/** The request body: the permissive generated set, as for QuoteContext. */
export type ScoreCompareRequest = requestComponents["schemas"]["ScoreCompareRequest"];

/**
 * Score one quote against two Rating Versions with a step-level trace diff (03 FR-262,
 * `POST /api/v1/score/compare`). `context` never carries `options.rating_version_ref`: the
 * route refuses it with 422, because `base` and `comparison` name the versions (03:1060).
 * A per-quote error on either side rejects with a `ProblemError` whose detail names the side.
 */
export function scoreCompare(
  body: ScoreCompareRequest,
  signal?: AbortSignal,
): Promise<ScoreComparison> {
  return request<ScoreComparison>("/score/compare", {
    method: "POST",
    body,
    ...(signal ? { signal } : {}),
  });
}
```

### `QuoteComparison.vue`

Props: `defineProps<{ comparison: ScoreComparison }>()`. It renders:

1. A `<section aria-labelledby="comparison-heading">` with
   `<h2 id="comparison-heading">Compared with <span class="font-mono">{{ comparison.comparison.rating_version_ref }}</span></h2>`.
   Its accessible name is therefore `Compared with rating_version:<slug>@<version>`.
2. A summary `<table>` with `<caption>Both results</caption>`, column headers `Base` and
   `Comparison` (`<th scope="col">`), and three rows headed by `<th scope="row">`: `Version`
   (`rating_version_ref`), `Outcome` (`outcome`), `Payable premium` (the `premium_ladder` rung
   whose `rung` is `payable_premium`, through `formatAmount` from `components/sandbox/ladder.ts:46`;
   `—` when the rung is absent).
3. A step `<table>` with `<caption>Step differences · {{ comparison.diff.unchanged }} steps unchanged for this quote</caption>`,
   column headers `Step`, `Change`, `Base produced`, `Comparison produced`, and one `<tr>` per
   `comparison.diff.steps` entry, in the response's order (no re-sorting: §4.10 fixes it).
   `Step` shows `step_id` in mono and the `label` of whichever side is present. `Change` shows
   `stepChangeLabel(step)`. Each produced cell shows `JSON.stringify(side.produced)`, as
   `TraceTimeline.vue` does, or `—` when that side is `null`.

### `QuoteSandboxView.vue` changes

- **Load.** After the version resolves (`:41-48`), call `listRatingVersions()`
  (`api/ratingVersions.ts:7`) in its own `try`. A `ProblemError` sets `versionsProblem` and
  leaves the sandbox usable. Any other error is re-thrown, as `:49-51` does.
- **State.** `versions: RatingVersion[]`, `versionsProblem: ProblemError | null`,
  `comparisonRef: string` (`""` means no comparison), `comparison: ScoreComparison | null`, and
  `comparable = computed(() => versions.value.filter((v) => v.id !== rating.value?.id))`.
- **The picker (DP-1 (a)).** In the left column, above `QuoteForm` (`:132-136`); the column
  becomes a `<div class="space-y-6">` holding both. A `<label for="compare-against">Compare against</label>`
  and `<select id="compare-against" v-model="comparisonRef">`. Its first option is
  `<option value="">No comparison</option>`, then one option per `comparable` version, with
  value `rating_version:${v.slug}@${v.version}` and text `${v.slug}@${v.version} · ${v.status}`.
  When `versionsProblem` is set, a `<p role="status">` reads
  `Versions to compare against could not be loaded: {{ versionsProblem.problem.detail }}` and
  the select holds only "No comparison".
- **Scoring.** `score()` (`:57-75`) resets `comparison` as well as `result`. With
  `comparisonRef === ""` it calls `scoreQuote` exactly as today. Otherwise it calls
  `scoreCompare({ context: { purpose, quoted_at, effective_date, inputs }, base: versionRef.value, comparison: comparisonRef.value })`.
  The `context` has **no `options` key**. It sets `result.value = response.base` and
  `comparison.value = response`. The base side is the version in view, so the outcome,
  waterfall and trace of `:143-150` render unchanged from the base result. A `ProblemError`
  goes to `scoreProblem` as today, and `QuoteError` shows its `detail`, which starts with the
  failing side (`QuoteError.vue:52-54`).
- **Mount.** `<QuoteComparison v-if="comparison" :comparison="comparison" />` inside the
  `v-if="result"` template, after `TraceTimeline` (`:146-149`).

## Tasks

Each task is red first. **Every red fails at its own `expect`, never on a missing module or a
thrown query.** For that: (i) a new module lands first as a stub that compiles and exports its
name; (ii) each test reads with `query*` and asserts the result, or wraps its assert in
`waitFor(() => expect(...))`, so the thrown error is the `expect`'s. A predicted red names the
stub or the code line that makes it fail, not only the status (`docs/plans/README.md`
convention 2). Runs go through `~/gi-pricing-plan.local/handover/run-small.sh <worktree> <test-file>`
(≤3 files; RL-1626), never a full suite.

### Task 1 — the label rule (`stepChange.ts`), tests A1–A6

**Stub first** (commit it with the tests):

```ts
import type { StepChange } from "@/api/score";
export function stepChangeLabel(_change: StepChange): string {
  return "";
}
```

`StepChange` must be exported from `api/score.ts` for this to type-check, so Task 1 also adds
the three type aliases (not yet `scoreCompare`).

Tests, in `frontend/src/components/sandbox/__tests__/stepChange.test.ts`. Each fixture is typed
`StepChange`; each test name carries `FR-262`.

| Test | Input | Assert | Red cause, on the stub |
|---|---|---|---|
| A1 | `{ step_id: "s_new", change: "added", own_change: true, base: null }` | `expect(stepChangeLabel(c)).toBe("Added in comparison")` | stub returns `""` |
| A2 | `{ step_id: "s_old", change: "removed", own_change: true, comparison: null }` | `toBe("Removed in comparison")` | stub returns `""` |
| A3 | `changed`, `own_change: true`, `changed_fields: ["produced"]` | `toBe("Edited")` | stub returns `""` |
| A4 (item 8) | `changed`, `own_change: true`, `changed_fields: ["consumed", "produced"]` | `toBe("Edited; its inputs also changed")` | stub returns `""` |
| A5 | `changed`, `own_change: false`, `changed_fields: ["consumed", "produced"]` | `toBe("Changed through its inputs")` | stub returns `""` |
| A6 (item 8 guard) | all 12 of `change` × `own_change` × (`consumed` in `changed_fields` or not) | for each: `expect(label).not.toBe("")` then `expect(label).not.toMatch(/unchanged\|not edited/i)` | stub returns `""`, so the first assert fails |

Green: the `stepChangeLabel` body in §"The label rule". **Broken-input proof** (record it in
the `LG-`): change row 5's text to `Not edited` and run the file. A5 and A6 must go red, and A6
must fail at the `not.toMatch` assert. Restore the text.

### Task 2 — the picker and the compare call, tests C1–C3, C5, C6

**Step T1 — the `03` §5.1 row first (DP-1, RL 8057)** *(amended 2026-10-16 by the planner (seat planner-8054b), pre-merge, applying RL 8057, working id)*. `GET /api/v1/rating-versions`
exists (`backend/src/app/api/models.py:1106-1129`, client `api/ratingVersions.ts:7`) but `03`
§5.1 does not declare it (RL 8057 "Verified first" item 7). Insert this row **verbatim**
directly above the `GET /api/v1/rating-versions/{slug}@{version}` row (`03:1051` at
`0877e6e7`):

```
| `GET` | `/api/v1/rating-versions` | List the caller's workspace's Rating Versions, every status, ordered by `version` (FR-262: the Quote Sandbox's comparison picker); requires `rating:read`. **200** with a `RatingVersion[]` (§4.3), unpaginated; 401; 403. Built in Phase 1b (FR-440); records an existing route, declared 2026-10-16 (RL 8057, working id), owner WK-675. S10 (`SL-1552`) amends this row with its own FR and the list view's needs; it does not add a second row |
```

- **Same commit as the first call** (condition (1) of the maintainer's confirmation of RL 8057 in `to-lead.md`, "2026-10-16 09:49:25 BST — Maintainer: RL 8057 (PL 8054 DP-1 (a), DP-2 (a), SL-1550 lane C S7) CONFIRMED"). T1 lands in the commit that first calls
  `listRatingVersions` from `QuoteSandboxView.vue` (the picker's green step below), never
  before it and never after (`CLAUDE.md` §2). If RL 8057 is minted before SL-1550's PR, write
  its minted id in place of "RL 8057, working id"; otherwise the mint rewrites it.
- **Check.** `flock -w 900 /tmp/slots/gate-2 env -C <wt> python3 scripts/audit-docs.py` on that
  commit, rc printed; then the Acceptance item 9 grep.
- **Test tied to T1: C1** (RL 8057 Acceptance 2). C1 is the first test that needs the list
  route; T1 is what makes its route a spec'd one.
- **S10 later amends T1's row, never adds a second one** (RL 8057 "What it obliges"). Pagination,
  status or slug filters and cross-slug sort order are S10's (`PL-1286:313`), not S7's.

Add `scoreCompare` to `api/score.ts` (§"`api/score.ts` additions"). In
`QuoteSandboxView.test.ts`, extend the two mock factories (`:13-21`) with
`listRatingVersions` and `scoreCompare`, each forwarding to a `vi.fn()`, as the existing
entries do. In `beforeEach` (`:78-82`), add `listRatingVersions.mockResolvedValue([RATING, OTHER])`,
where `OTHER` is `RATING` with `id` `"01a04394-338b-7651-9e42-c73ee70396f9"`, `version: 2` and
`status: "approved"`. Add `scoreCompare.mockResolvedValue(COMPARISON)`. `COMPARISON` is typed
`ScoreComparison`: `base` is `RESULT` (`:46-61`), `comparison` is `RESULT` with
`rating_version_ref: "rating_version:motor-gb@2"` and a payable rung of `60000`, and `diff` is
`{ steps: [<the s_rate row of Task 3's fixture>], unchanged: 1 }`. Extending the mocks changes
no existing test: today's view calls neither export.

| Test | What it does | Assert | Red cause, on `origin/main`'s view |
|---|---|---|---|
| C1 | Render; `await screen.findByLabelText("driver_age")`; `picker = screen.queryByLabelText("Compare against")` | `expect(picker).not.toBeNull()`; then its options' text equals `["No comparison", "motor-gb@2 · approved"]` (the version in view is excluded) | No control is labelled "Compare against": `QuoteSandboxView.vue:128-158` renders only `QuoteForm` and the result column. C1 holds condition (2) of the maintainer's `to-lead.md` entry "2026-10-16 09:49:25 BST": the version in view is **excluded** and "No comparison" is **first**. **Broken-input proof for the `LG-`** (RL 8057 Acceptance 2) *(amended 2026-10-16 by the planner (seat planner-8054b), pre-merge, applying RL 8057, working id)*: drop the `comparable` filter (offer `versions` unfiltered), and C1 goes red at the options' text assert, because `motor-gb@3 · …` is offered |
| C2 | Select `motor-gb@2 · approved`, then `fillAndSubmit()` (`:68-72`) | `await waitFor(() => expect(scoreCompare).toHaveBeenCalledTimes(1))`; the body has `base: "rating_version:motor-gb@3"`, `comparison: "rating_version:motor-gb@2"`, `context.purpose: "what_if"`, `context.inputs: { driver_age: 34, channel: "direct" }`; `expect(body.context).not.toHaveProperty("options")` (03:1060's 422); `expect(scoreQuote).not.toHaveBeenCalled()` | After C1's picker lands, `score()` (`:62-68`) still calls `scoreQuote`, so `scoreCompare` has 0 calls |
| C3 | `scoreCompare.mockRejectedValue(problem(422, "INPUT_CONTRACT_VIOLATION", "comparison: driver_age is above its max"))` (`problem` is `:74-76`); select a comparison; submit | `await waitFor(() => expect(screen.queryByRole("alert")).toHaveTextContent("comparison: driver_age is above its max"))` | `scoreQuote` is called and resolves `RESULT`, so no alert renders |
| C5 (guard) | No comparison chosen; `fillAndSubmit()` | `await waitFor(() => expect(scoreQuote).toHaveBeenCalledTimes(1))`; `expect(scoreCompare).not.toHaveBeenCalled()` | **Green on arrival, by design**: it holds today's path. Broken-input proof for the `LG-`: make `score()` always call `scoreCompare`, and C5 goes red at `not.toHaveBeenCalled()` |
| C6 | `listRatingVersions.mockRejectedValue(problem(403, "WORKSPACE_SCOPE_DENIED", "no access"))`; render; `await screen.findByLabelText("driver_age")` | `expect(screen.queryByText(/Versions to compare against could not be loaded/)).not.toBeNull()`; `expect(screen.getByRole("button", { name: "Score quote" })).toBeEnabled()` | The view never calls `listRatingVersions`, so the message never renders |

Write C1 and C6 red, then the picker green. Then write C2 and C3 red, then the scoring change
green. Each red is run and its failing assert recorded in the `LG-`.

### Task 3 — the compare panel (`QuoteComparison.vue`) and its mount, tests B1–B6, C4

**Stub first** (commit it with the tests):

```vue
<script setup lang="ts">
import type { ScoreComparison } from "@/api/score";

defineProps<{ comparison: ScoreComparison }>();
</script>

<template>
  <section />
</template>
```

The fixture in `QuoteComparison.test.ts` is typed `ScoreComparison`. Its `base` and
`comparison` are scored results, as in Task 2: `motor-gb@3`, payable `63000`, `quoted`; and
`motor-gb@2`, payable `60000`, `declined`. `diff.unchanged` is `11`. `diff.steps` are:

| `step_id` | `change` | `own_change` | `changed_fields` | Case |
|---|---|---|---|---|
| `s_rate` | `changed` | `true` | `["produced"]` | the edited rate table step (`RL-1172` §5's one-step case) |
| `s_total` | `changed` | `true` | `["consumed", "produced"]` | **item 8**: edited, and its input also moved (F5) |
| `s_ipt` | `changed` | `false` | `["consumed", "produced"]` | knock-on: same definition, moved inputs |
| `m_ncd__s_cap` | `changed` | `true` | `["consumed", "produced"]` | a mounted step's namespaced id (`LG-1699:88`) |
| `s_new` | `added` | `true` | — | `base: null` |

Each `TraceStep` side carries `step_id`, `type`, `label` and a `produced` object. `s_new`'s
`comparison.produced` is `{ "loading": "1.05" }`.

Each B test begins the same way:
`const table = screen.queryByRole("table", { name: /Step differences/ }); expect(table).not.toBeNull();`.
On the stub this first assert fails, because the stub renders an empty `<section />`. That is
the red cause for B1–B5. A row is found with
`within(table!).getAllByRole("row").find((r) => r.textContent?.includes(id))`, then
`expect(row).toBeDefined()`. Row asserts use `within(row!)`, so the caption's "unchanged" is
never in scope.

| Test | Assert (after the table assert) |
|---|---|
| B1 (item 8) | the `s_total` row has text `Edited; its inputs also changed`; `expect(within(row!).queryByText(/unchanged\|not edited/i)).toBeNull()` |
| B2 | the `s_ipt` row has text `Changed through its inputs`, and the same `toBeNull()` |
| B3 | the `s_new` row has `Added in comparison`, its `Base produced` cell is `—` and its `Comparison produced` cell is `{"loading":"1.05"}` |
| B4 | the `m_ncd__s_cap` row exists, shows `m_ncd__s_cap` verbatim and has `Edited; its inputs also changed` |
| B5 (DP-2, RL 8057; condition (2) of the maintainer's `to-lead.md` entry "2026-10-16 09:49:25 BST": the caption keeps "for this quote") | the table's accessible name contains `11 steps unchanged for this quote`; the body has exactly 5 rows, in fixture order (`s_rate`, `s_total`, `s_ipt`, `m_ncd__s_cap`, `s_new`): only `diff.steps` become rows. **Broken-input proof for the `LG-`** (RL 8057 Acceptance 3 and 4) *(amended 2026-10-16 by the planner (seat planner-8054b), pre-merge, applying RL 8057, working id)*: (i) append one row not in `diff.steps`, and B5 goes red at the row count; (ii) drop "for this quote" from the caption, and B5 goes red at the accessible-name assert |
| B6 | `const summary = screen.queryByRole("table", { name: "Both results" }); expect(summary).not.toBeNull()` (red on the stub at this assert); it shows both refs, `quoted` and `declined`, and `formatAmount(63000)` and `formatAmount(60000)` |

Then mount it in the view and add **C4** to `QuoteSandboxView.test.ts`: select a comparison,
`fillAndSubmit()`, then
`await waitFor(() => expect(screen.queryByRole("region", { name: /Compared with rating_version:motor-gb@2/ })).not.toBeNull())`,
and `expect(screen.queryByTestId("outcome")).toHaveTextContent("quoted")` (one `QuoteOutcome`,
from `COMPARISON.base`). **C4's red cause:** after Task 2, `comparison` is set but nothing
mounts it, so no region carries that name. Write C4 before the mount line.

## Decision points

Planner does not rule these (`delivery-process.md` §3). **DP-1 and DP-2 block** because each
changes the test list. This plan is `draft` until both are ruled. Planner recommends (a) for
both. If both are ruled (a), the design above applies as written.

*(amended 2026-10-16 by the planner (seat planner-8054b), pre-merge, applying RL 8057, working id)* **Both are ruled (a) by RL 8057.** The design applies as written, plus Task 2 Step T1.
DP-1's premise is corrected: the route is generated and used, but **undeclared in `03` §5.1
until T1** (RL 8057 "Verified first" item 7). DP-2 answers `RL-1261:100-104` for WK-675; no open
question is raised. No row is open, but the plan stays `draft` until RL 8057 is minted and on
`origin/main` (Context 7's added need; the maintainer's `to-lead.md` entry "2026-10-16 09:49:25
BST", condition (3)).

| DP | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| **DP-1** | How does the actuary choose the comparison version? | **(a)** A select fed by `GET /api/v1/rating-versions` (`listRatingVersions`, `api/ratingVersions.ts:7`, already generated and used by `DemoView.vue:72`; *corrected by RL 8057: undeclared in `03` §5.1 until Task 2 Step T1*): every version except the one in view, "No comparison" first and selected. **(b)** A free-text ref field (`rating_version:<slug>@<n>`): no list call, but a typo is a 404 and nothing is discoverable. **(c)** (a) plus a `?against=` query on the sandbox route, so a comparison can be linked: adds router state and one more test, and FR-262 does not ask for it. | **(a).** FR-262 says *"any accessible Rating Version"*: the list route returns the versions the principal can read, so it is that set. The route and the client exist, so nothing new is built. A version that is not compiled answers 409 `BUNDLE_COMPILE_FAILED` naming its side (`03:1060`). `QuoteError` shows it, so the picker need not filter by compile state. | decision point | yes | **RL 8057** (working id): ruled **(a)**, with T1 first |
| **DP-2** | `RL-1261:100-104`: should the view also show a step whose definition changed but whose trace is identical for this quote ("edited, no effect on this quote")? | **(a)** Not in S7. The caption says `{n} steps unchanged for this quote`, which is exact. The question stays with WK-675, recorded by whatever the ruling names. **(b)** In S7: the view also reads FR-219's structural diff (`GET /api/v1/rating-algorithms/{slug}@{version}/diff`, in `generated.json` `paths`) for the two versions' algorithms. It lists every definition-changed step absent from `diff.steps` as `Edited, no effect on this quote`. This adds two reads, one more test (B7), and a check of the route's `against` parameter, which this plan has not read. **(c)** The backend adds those steps to `TraceDiff`. This changes the §4.10 shape that `RL-1261` says *"do[es] not change"*, so it needs a spec change first, and it is outside S7's row. | **(a).** S7's row is size 1 and names FR-262's view limb only. (b) adds nothing that (a) must later remove, so it can follow as its own row. (c) reopens a shape `RL-1261` closed. | decision point | yes | **RL 8057** (working id): ruled **(a)**; caption `{n} steps unchanged for this quote`; held by B5 |

## Acceptance Standard

1. **The label rule is held by test.** `run-small.sh <wt> frontend/src/components/sandbox/__tests__/stepChange.test.ts`
   passes, and the `LG-` records the broken-input run of Task 1 (A5 and A6 red on `Not edited`).
2. **Item 8 holds at the component** (`PL-1286` item 8; `PL-1546` item 7). B1 and B2 pass, and
   `grep -nE "unchanged|not edited" frontend/src/components/sandbox/stepChange.ts` prints
   only lines in the doc comment.
3. **Each test names its FR** (`PL-1546` item 3): `grep -rlE 'FR-262[^0-9]' frontend/src --include=*.test.ts`
   prints `stepChange.test.ts`, `QuoteComparison.test.ts` and `QuoteSandboxView.test.ts`.
4. **No hand-written API shape** (`PL-1546` item 4): `git grep -nE "^(export )?(interface|type) (ScoreComparison|StepChange|TraceDiff|ScoreCompareRequest)\b" frontend/src`
   prints only the three `components[...]` aliases in `api/score.ts`. `pnpm --dir frontend generate:api`
   leaves `git status --short frontend/src/api/generated` empty.
5. **The request never carries a version in `context`:** C2 passes, with its
   `not.toHaveProperty("options")` assert.
6. **Every red was seen at its assert:** the `LG-` lists A1–A6, B1–B6 and C1–C4, C6 with the
   failing `expect` line each printed on its red run. C5 is listed as a guard, with its
   broken-input run.
7. **No new route, no new dependency:** `git diff --stat origin/main...HEAD -- frontend/src/router frontend/package.json`
   prints nothing.
8. **The gate is green on the slice's merge tree** (`PL-1546` item 8): the `CLAUDE.md` §11
   commands, both halves, each rc 0, against `origin/main...<slice branch>`, in a gate slot the
   lead grants.
9. **T1 is in the spec, exactly one row (DP-1, RL 8057 Acceptance 1; condition (1) of the maintainer's `to-lead.md` entry "2026-10-16 09:49:25 BST")** *(amended 2026-10-16 by the planner (seat planner-8054b), pre-merge, applying RL 8057, working id)*: this command prints
   exactly one line, T1's row:

   ```
   git grep -nE '^\| `GET` \| `/api/v1/rating-versions` \|' -- docs/specs/03-rating-engine.md
   ```

   Broken input: at `origin/main` `0877e6e7` it prints nothing (rc 1, RL 8057). The row is in
   the same commit as the first `listRatingVersions` call from `QuoteSandboxView.vue`: the
   oldest commit each of these prints, over `origin/main..HEAD`, is the same one:

   ```
   git log --reverse --format=%h -S listRatingVersions origin/main..HEAD -- frontend/src/views/QuoteSandboxView.vue
   git log --reverse --format=%h -S 'records an existing route, declared 2026-10-16' origin/main..HEAD -- docs/specs/03-rating-engine.md
   ```

   `audit-docs.py` exits 0 on that commit.
10. **RL 8057's breakers are recorded** *(amended 2026-10-16 by the planner (seat planner-8054b), pre-merge, applying RL 8057, working id)*: the `LG-` lists C1's red on the unfiltered
   picker and B5's two reds (appended row; caption without "for this quote"), each with its
   failing `expect` line.

## Global Constraints

`PL-1546`'s Global Constraints apply unchanged: Vue 3 `<script setup lang="ts">` only; no
hand-written API type; money never a float (the payable premium is `value_minor`, an integer,
shown through `formatAmount`); WCAG 2.2 AA (text labels, `<caption>`, `<th scope>`); one PR per
slice (L1 (a')) carrying code, tests, the `SL-1550` status line and its one `LG-`. Added here:

- **No new route** (`03:1410` puts compare inside the sandbox route).
- **No new dependency.**
- **The quote-form re-merge rule binds S7**, because S7 edits `QuoteSandboxView.vue`. The
  maintainer's (by delegation) entry in `to-lead.md`, "2026-10-12 05:35:05 BST — S7 joins the
  quote-form re-merge rule", verbatim: *"any slice touching the sandbox quote form
  (frontend/src/components/sandbox/quoteForm.ts, QuoteForm.vue, QuoteSandboxView.vue) that
  merges after another one re-merges main and re-runs the sandbox tests
  (frontend/src/components/sandbox/__tests__ and views/__tests__/QuoteSandboxView.test.ts)
  before its ACK request. Put it in S7's brief and in eta."*
- **No backend or contract change.** The one spec change is T1 (RL 8057), which records an
  existing route and changes no shape *(amended 2026-10-16 by the planner (seat planner-8054b), pre-merge, applying RL 8057, working id)*. If the executor finds the generated `ScoreComparison`
  differs from §"Spec and contract read", it stops and reports. It does not edit `model-schema`
  in this slice.

## Self-review

- **Spec coverage.** FR-262's view limb: picker (Task 2), one-quote-two-versions call (C2),
  side-by-side results (B6, C4), step difference (B1–B5). §4.10's order and null side: B3, B5.
  §5.1's 422-on-`options` and side naming: C2, C3. `PL-1286` item 8: A4, A6, B1, B2. `LG-1699:88`:
  B4. `RL-1261:100-104`: DP-2, answered by RL 8057 (B5). The list route's §5.1 row: T1 (RL 8057),
  held by Acceptance 9 and C1 *(amended 2026-10-16 by the planner (seat planner-8054b), pre-merge, applying RL 8057, working id)*.
- **Placeholder scan.** Each test has its input, its assert and its red cause. Each stub is
  given in full.
- **Type consistency.** `stepChangeLabel(change: StepChange): string`, `scoreCompare(body:
  ScoreCompareRequest, signal?)`, and `QuoteComparison` props `{ comparison: ScoreComparison }`
  are the same names in every task.
- **Literals verified at `0877e6e7`:** `QuoteSandboxView.vue:57-75`, `:128-158`;
  `QuoteSandboxView.test.ts:13-21`, `:46-61`, `:68-76`, `:107`; `QuoteOutcome.vue:18-25`;
  `QuoteError.vue:52-54`; `ladder.ts:46` (`formatAmount(minor: number)`);
  `api/ratingVersions.ts:7`; `api/score.ts:1-25`; `backend/src/app/api/score.py:455-457`.
