---
id: PL-785
family: plan
kind: leaf
title: W6b-2 — Model Comparison View Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-24
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-24-w6b-2-model-comparison.md
---

# W6b-2 — Model Comparison View Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `02` §5.3's Model comparison view at `/models/compare?ids=` — the aligned metric table, the double-lift chart and the factor-by-factor relativity diff — reading a `ModelComparison` the backend already computes.

**Architecture:** This is a **frontend-only slice.** Every backend part exists and is tested: `POST /api/v1/models/compare` (202 + Job), the `MODEL_COMPARE` worker, the migration, and `GET /api/v1/models/comparisons/{comparison_id}`. The view's real content is therefore not rendering — it is the **asynchronous `POST` → poll → `GET` sequence**, which this frontend has exactly one precedent for (`RuleBuilder.vue`) and that precedent never fetches the artifact the job produced. One new API module, one new route, one view, one shared ref-renderer and three panel components.

**Tech Stack:** Vue 3 Composition API with `<script setup lang="ts">`, vue-router, `vue-echarts` / `echarts`, Tailwind, Vitest + happy-dom + `@testing-library/vue`. No Pinia (the repository has no `frontend/src/stores/` and nothing imports it).

**Spec:** [`../specs/02-modelling.md`](../specs/02-modelling.md) — §4.11 `ModelComparison` (the artifact and its invariants), §5.1 (the two endpoints), §5.3 (the view row), FR-186.

---

## Global Constraints

Copied verbatim from the governing documents. Every task's requirements implicitly include this section.

- **Vue 3 Composition API with `<script setup lang="ts">` only** — never Options API, JSX, React. (`CLAUDE.md` §3.)
- **Never hand-write an API type in the frontend; generate it from OpenAPI.** (`CLAUDE.md` §3.) Every domain type in this plan is `components["schemas"][...]` re-exported from a hand-written module in `frontend/src/api/`, per [`../adrs/ADR-00704-model-schema-is-the-single-source-of-truth-for-shared-shapes.md`](../adrs/ADR-00704-model-schema-is-the-single-source-of-truth-for-shared-shapes.md). `frontend/src/api/generated/` is VCS-ignored and may not be edited or cited as evidence.
- **Nobody hand-writes a shape that already exists in `model-schema`** — "A shape defined twice will diverge, and in a pricing platform a diverged shape is a mispricing." (`CLAUDE.md` §2.) Test fixtures included: they are **annotated** with the generated type, never `as unknown as T`.
- **FR-10** — money is integer minor units in "the rating path and all persisted rate tables"; "Floats are permitted only inside model fitting and diagnostics, never in a quoted premium." A comparison artifact is a diagnostic read, so its floats are in scope of that permission. `exposure_years` is nevertheless a `DecimalStr` (a **string**) on the wire and needs `Number()` at the chart boundary with a comment saying why, matching `OneWayChart.vue`.
- **The gate has two halves and both must pass locally before pushing** (`CLAUDE.md` §11). For this slice: `pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend test && pnpm --dir frontend build`, and `python3 scripts/audit-docs.py` for this document.
- `pnpm --dir frontend generate:api` must have been run in the worktree, or `frontend/src/api/generated/schema.d.ts` is absent and every import in this plan fails to resolve. It is git-ignored; a fresh worktree does not have it.
- **Requirement IDs are permanent** (`CLAUDE.md` §5). This slice appends none.

**Requirement ids cited by this plan, all of which already exist:** FR-171, FR-186, FR-139, FR-94, FR-167, FR-10, **FR-24**, FR-76, FR-43, FR-400, NFR-528, NFR-463. **No new ids; no `Next free:` marker.**

**Frozen against `f838662`** — the commit that landed FR-24. Every line number and every quoted literal in this plan was read at that revision; a line number in a document someone is appending rows to goes stale without moving, so the revision travels with them.

---

## Where this view's contents come from, and why the §5.3 cell is not the source

**FR-24** (`00-overview.md:227`, landed 2026-08-24 as the ruling on OQ-549): *"A Contents cell in a module spec's §5.3 Frontend views table is prose and binds nothing … What a view must show is stated in a numbered requirement or in the generated contract."* It is **prospective, and not in force** until seven §5.3 obligations carried nowhere else are discharged; `02` Model comparison is not among the seven, and this plan adds no obligation to it.

This plan therefore derives the three panels from **a numbered requirement and the generated contract**, which is the route FR-24 names, and the cell corroborates rather than supplies:

| Source | Standing under FR-24 | What it names |
|---|---|---|
| `02` FR-186 | Numbered requirement — binding | "compared on aligned metrics, double-lift, and factor-by-factor relativity differences" |
| `ComparisonSummary` in `packages/model-schema/src/model_schema/comparison.py` | Generated contract — binding | the three collections `metrics`, `double_lift`, `relativity_differences` |
| `02` §5.3, the Contents cell | Prose — binds nothing | "Aligned metric table, double-lift chart, factor-by-factor relativity diff" |

The cell could be **deleted** and nothing in this plan would move.

**The same conclusion held before FR-24 existed, which is why this slice was plannable while OQ-549 was still open.** The question OQ-549 asked — enumeration or prose — had no consequence here, because the requirement and the artifact each independently produce the same three panels. That was over-determination; the ruling has now made it the general rule. The test to carry into every later slice is unchanged and now has a requirement behind it: **is the cell the sole source?** Here it is not. For `W6b-1b` it was, which is why that slice waited and why it is now planned against the contract rather than against the cell.

---

## Verified repository literals

`docs/plans/README.md`'s first unenforced convention: *verify every repository literal against the shipped source before it enters sample code.* Each row below was read from the tree at `origin/main` **b05b0b1** before being written into a task.

| Literal | Verified at | Note |
|---|---|---|
| `POST /api/v1/models/compare` → 202 + `Job` | `backend/src/app/api/models.py:803`, and `models.py:22` (the spec's own §5.1 table, quoted in the module docstring) | `Location: /api/v1/jobs/{id}` header also set |
| `GET /api/v1/models/comparisons/{comparison_id}` → `ModelComparison` | `backend/src/app/api/models.py:848`, `models.py:23` | `model:read`, not `model:fit` |
| `CompareModels` = `model_ids: UUID[]` (min 2) + `baseline_id: UUID \| null` | `backend/src/app/api/models.py`, class `CompareModels` | `model_ids` is "in the order the table should present them" |
| Schema names in the contract | `docs/contracts/openapi/generated.json` | `CompareModels`, `ComparisonMetric`, `ComparisonSummary`, `ComparisonValue`, `DoubleLift`, `DoubleLiftBin`, `MetricDirection`, `ModelComparison` |
| **`JobResult.ref` is `model_comparison:{uuid}`** | `backend/src/app/worker/model_handlers.py:786` | **Not** `comparison:{id}`. See the warning below |
| `JobResult` = `kind: "artifact" \| "blob" \| "none"`, `ref: string \| null` | `docs/contracts/openapi/generated.json` | |
| `JobStatus` terminal set | `frontend/src/api/jobs.ts:8` | `TERMINAL = ["succeeded", "failed", "cancelled"]` |
| `waitForJob` never throws on failure or timeout | `frontend/src/api/jobs.ts:14-31` | "a caller must read `status`, not assume the wait succeeded" |
| `request<T>(path, {query, body, method})`, `BASE = "/api/v1"` | `frontend/src/api/client.ts:15-35` | `undefined` query values are dropped |
| `ProblemError`, `isProblem(error, code?)` | `frontend/src/api/problem.ts:13,49` | |
| ID-3 model ref pattern | `packages/model-schema/src/model_schema/refs.py:30-43` | `^model:[a-z0-9][a-z0-9-]{1,62}@[1-9][0-9]*$` |
| Chart palette rule: grey `#cbd5e1` is reserved for exposure across charts | `frontend/src/components/HistogramChart.vue:37` (the rule), `:66` (the use) | |
| URLs in this app carry slug + version, never a UUID | `frontend/src/router/index.ts:34-44` (`/data/:slug/v/:version`), `:54-59` (`/models/:slug`, `?version=`) | The `/models/:slug` entry's comment gives the reason: an `@` "must be percent-encoded by every client" |
| `stubByUrl` returns 200 for a hit and a full problem document for a miss | `frontend/src/views/__tests__/ModelDetailView.test.ts:64-82` | Signature is `Record<string, unknown>` — it **cannot** express a 202 or a 409 |

### The one literal most likely to be written from memory, and wrong

`JobResult.ref` for this job is **`model_comparison:{uuid}`**. FR-94 records the backtest job's result as `backtest:{id}`, and the analogy invites writing `comparison:{id}`. It is `model_comparison:`.

**And it is not an ID-3 reference.** All twelve `JobResult` refs the workers emit use a `{entity}:{uuid}` form, and only two of the twelve entity names (`dataset_version`, `model`) are members of `ARTIFACT_TYPES` in `refs.py`; `model_comparison` is not one of them, and there is no `@version` segment. So:

- **Never run `JobResult.ref` through an ID-3 parser.** Split on the first `:` and assert the prefix.
- `model_handlers.py:554` emits `model:{uuid}` for a fit job, which shares a prefix with the ID-3 `model:{slug}@{version}` and is a different namespace. A check of the form "starts with `model:`" therefore accepts two unrelated things. Neither this plan nor the view performs one.

---

## File structure

| File | Responsibility |
|---|---|
| `frontend/src/api/jobs.ts` *(modify)* | Add an optional `onPoll` callback to `waitForJob`. Purely additive |
| `frontend/src/api/comparisons.ts` *(create)* | Type re-exports, the two endpoint calls, `comparisonIdFromJob`, and the pure presentation helpers `parseModelRef`, `leaderState` |
| `frontend/src/api/__tests__/comparisons.test.ts` *(create)* | Unit tests for the four pure functions |
| `frontend/src/components/ModelRefLink.vue` *(create)* | One ID-3 ref rendered as a link, or as plain text when it does not parse |
| `frontend/src/components/ComparisonMetricTable.vue` *(create)* | The aligned metric table — models as columns, metrics as rows |
| `frontend/src/components/DoubleLiftChart.vue` *(create)* | One `DoubleLift` series as an ECharts chart |
| `frontend/src/components/RelativityDiffTable.vue` *(create)* | Factor-by-factor relativity differences, grouped by factor |
| `frontend/src/components/__tests__/*.test.ts` *(create, four)* | One per component |
| `frontend/src/router/index.ts` *(modify)* | The `/models/compare` route, declared **before** `/models/:slug` |
| `frontend/src/views/ModelComparisonView.vue` *(create)* | Reads `?ids=`, runs `POST` → poll → `GET`, owns the five UI states |
| `frontend/src/views/__tests__/ModelComparisonView.test.ts` *(create)* | The state machine, over a URL-routing fetch stub |
| `frontend/src/views/__tests__/fixtures.ts` *(modify)* | Add `COMPARISON: ModelComparison`, built from §4.11's own example |

**Not built by this slice, deliberately:**

- **A tabular fallback for the double-lift chart.** NFR-463 requires one for every chart; the revised slice map gives it to **W6b-9** ("Tabular chart fallback (`NFR-463`)") as a single cross-cutting slice. Building a bespoke one here would be the shape W6b-9 then has to unpick.
- **A progress bar.** `Progress` (FR-400) carries `fraction`, `stage` and `counters`, and `Job.stalled` is derived on read (NFR-528). Task 6 surfaces the **stage label and elapsed attempts** only. A fraction the worker may never populate renders as a bar stuck at zero, which reads worse than no bar.
- **An entry point.** See the scope findings.

---

## Design decisions this plan makes, and the reasoning

These are recorded rather than taken silently (`CLAUDE.md` §10). None of them is a question the specs leave open; each is a derivation with one defensible answer.

**1. The query is `?ids=<uuid>,<uuid>` — comma-separated UUIDs.** §5.3 names the parameter (`?ids=`) and not its contents. `CompareModels.model_ids` is `tuple[UUID, ...]`, so UUIDs are what the endpoint accepts, and any other encoding needs a resolution step no endpoint offers for a batch.

This **deviates from every other URL in the app**, which carries a slug and a version number and never a UUID — `/data/:slug/v/:version` and `/models/:slug?version=`, the latter with a comment giving the reason it is a query rather than an `@` in the path. The deviation is forced by the request body's type, not chosen, and it is recorded as a scope finding rather than hidden.

**2. No `?baseline=` parameter.** `CompareModels.baseline_id` defaults to the first of `model_ids`, and `model_ids` is ordered ("in the order the table should present them"). Ordering the ids therefore already chooses the baseline. A second parameter would be a second way to say the same thing, and `?ids=A,B&baseline=C` would be a state the URL can express and the endpoint rejects.

**3. Model refs are parsed with a plain-text fallback.** `ComparisonValue.model_ref`, `DoubleLift.baseline_ref` and `ComparisonSummary.model_refs` are **bare `str`**, not the validated `ModelRef` type — `comparison.py` imports `Weighting`, `SplitRef` and `DecimalStr` and never imports `refs`, and its four `model_validator`s enforce only referential integrity **inside** the artifact (leader among the measured, no repeated model, baseline in the set, every metric measuring the same set). None constrains the ref's format. **Adopting `ModelRef` on these fields was raised and ruled against on 2026-08-24**: a `ModelRef` puts a renameable slug in the identity position, and house style keeps id and version as separate fields for exactly that reason (`modelling.py`'s `IntervalFor`: "The id is what the lookup uses; the version is what a human reads in a review"). So the view parses, and renders the raw string when the parse fails. That is correct under either outcome and needs no revisiting.

**4. Metric keys render as raw keys in a monospace cell, with no label map.** The metric set is open — FR-167's custom metric library means a workspace can define its own — so a hard-coded label map either mislabels an unknown metric or blanks it. `gini_normalised` is the vocabulary a pricing actuary already uses.

**5. Chart channels.** Grey `#cbd5e1` stays reserved for exposure (`HistogramChart.vue:39`). The three value series take slate `#0f172a` for **actual** (the reference truth, so the neutral darkest), teal `#0f766e` for **baseline** (the established primary), amber `#b45309` for **challenger**. They are additionally distinguished by line type — actual solid, baseline dashed, challenger dotted — so the series are separable without colour, which is what NFR-463's WCAG 2.2 AA obligation needs.

---

## Rules from §4.11 the view must honour

Read from [`../specs/02-modelling.md`](../specs/02-modelling.md) §4.11. Each becomes a test.

1. **`leader === null` means one of two different things.** §4.11: *"`leader ∈` the metric's own model refs, and null where the metric does not order **or the models tie** — a winner chosen by tie-break is one the data did not choose."* So a null leader on a `not_ordered` metric is "not ranked"; a null leader on any other direction is "**tied**". Rendering both as an empty cell destroys a real measurement.
2. **`value === null` means "the metric does not apply to this model", never zero.** §4.11: every metric carries a value for every model, *"null where the metric does not apply, because a missing model reads as one that scored nothing rather than one nobody measured."*
3. **Double-lift bins are already ordered by the ratio of the two predictions** and must be rendered in array order. §4.11: sorting by either model's prediction *"gives two lift curves side by side, which answers 'does each model order risk?'; the ratio answers 'where they disagree, which one does the data support?'"* — a re-sort in the chart silently substitutes the weaker question.
4. **`direction` is part of the metric, not the reader's assumption.** `closer_to_one_is_better` exists because an A/E of 1.4 and one of 0.6 are equally wrong. The view never ranks; it marks the server's `leader`. It must not, for instance, style cells by magnitude.
5. **The shared holdout is stored, not promised** (FR-76). `split_ref` and `holdout_rows` are on the summary so the claim is checkable by a reader; the view shows both.
6. **Double lift is not a diagnostic.** FR-171's 2026-08-17 amendment removed it from the universal diagnostics list — *"double lift is pairwise, the comparison model is unknown at fit time"* — and it lives only here. Nothing in this view reads from `Diagnostics`.

---

## Task 1: The API module and the poll callback

**Files:**
- Modify: `frontend/src/api/jobs.ts:22-31`
- Create: `frontend/src/api/comparisons.ts`
- Test: `frontend/src/api/__tests__/comparisons.test.ts`

**Interfaces:**
- Consumes: `request` from `./client`; `Job`, `TERMINAL`, `waitForJob` from `./jobs`.
- Produces: `type ModelComparison`, `ComparisonSummary`, `ComparisonMetric`, `ComparisonValue`, `DoubleLift`, `DoubleLiftBin`, `RelativityDifference`, `MetricDirection`; `startComparison(modelIds: string[]): Promise<Job>`; `getComparison(id: string): Promise<ModelComparison>`; `comparisonIdFromJob(job: Job): string | null`; `parseModelRef(ref: string): { slug: string; version: number } | null`; `leaderState(metric: ComparisonMetric, modelRef: string): "leader" | "tied" | "unranked" | "behind"`.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/api/__tests__/comparisons.test.ts`:

```ts
import { describe, expect, it } from "vitest";

import { comparisonIdFromJob, leaderState, parseModelRef } from "@/api/comparisons";
import type { ComparisonMetric } from "@/api/comparisons";
import type { Job } from "@/api/jobs";

// A Job with only the fields these helpers read. Annotated `Partial<Job>` and cast at the
// call, rather than `as Job`, so a required field added to the contract does not silently
// pass here — the cast is at one place and says exactly what it is hiding.
function jobWith(result: Job["result"]): Job {
  return { result } as Job;
}

describe("comparisonIdFromJob", () => {
  // `backend/src/app/worker/model_handlers.py:786` — the ref is `model_comparison:{uuid}`,
  // NOT `comparison:{uuid}` and NOT an ID-3 `{type}:{slug}@{version}` reference.
  // `model_comparison` is not in `refs.py`'s ARTIFACT_TYPES and there is no version segment.
  it("reads the id out of a model_comparison ref", () => {
    const job = jobWith({ kind: "artifact", ref: "model_comparison:0e3f7a1c-1111-4222-8333-444455556666" });
    expect(comparisonIdFromJob(job)).toBe("0e3f7a1c-1111-4222-8333-444455556666");
  });

  // `model_handlers.py:554` emits `model:{uuid}` for a fit job. A prefix check loose enough
  // to accept that would hand the view a model id and a 404 it could not explain.
  it("refuses every other artifact ref, and a job with no result", () => {
    expect(comparisonIdFromJob(jobWith({ kind: "artifact", ref: "model:0e3f7a1c-1111-4222-8333-444455556666" }))).toBeNull();
    expect(comparisonIdFromJob(jobWith({ kind: "artifact", ref: "backtest:0e3f7a1c-1111-4222-8333-444455556666" }))).toBeNull();
    expect(comparisonIdFromJob(jobWith({ kind: "none", ref: null }))).toBeNull();
    expect(comparisonIdFromJob(jobWith(null))).toBeNull();
  });
});

describe("parseModelRef", () => {
  // `packages/model-schema/src/model_schema/refs.py:30-43`. `ComparisonValue.model_ref` is a
  // bare `str` with no validator, so this parse can fail on a well-formed artifact and the
  // caller renders the raw string instead.
  it("splits an ID-3 model ref into slug and version", () => {
    expect(parseModelRef("model:motor-ad-frequency@7")).toEqual({ slug: "motor-ad-frequency", version: 7 });
  });

  it("returns null for anything the pattern does not accept", () => {
    expect(parseModelRef("model:motor-ad-frequency")).toBeNull(); // no version
    expect(parseModelRef("model:motor-ad-frequency@0")).toBeNull(); // versions start at 1
    expect(parseModelRef("dataset:motor@3")).toBeNull(); // not a model
    expect(parseModelRef("model:Motor-AD@7")).toBeNull(); // slugs are lower-case
    expect(parseModelRef("model:0e3f7a1c-1111-4222-8333-444455556666")).toBeNull(); // a JobResult ref
  });
});

describe("leaderState", () => {
  const metric = (direction: ComparisonMetric["direction"], leader: string | null): ComparisonMetric => ({
    metric: "gini_normalised",
    weighting: "exposure",
    direction,
    values: [
      { model_ref: "model:a@1", value: 0.41 },
      { model_ref: "model:b@1", value: 0.43 },
    ],
    leader,
  });

  it("names the leader and the models behind it", () => {
    expect(leaderState(metric("higher_is_better", "model:b@1"), "model:b@1")).toBe("leader");
    expect(leaderState(metric("higher_is_better", "model:b@1"), "model:a@1")).toBe("behind");
  });

  // `02` §4.11: leader is null "where the metric does not order **or the models tie** — a
  // winner chosen by tie-break is one the data did not choose". Two different facts; a view
  // that renders both as an empty cell loses one of them.
  it("distinguishes a tie from a metric that does not order", () => {
    expect(leaderState(metric("higher_is_better", null), "model:a@1")).toBe("tied");
    expect(leaderState(metric("closer_to_one_is_better", null), "model:a@1")).toBe("tied");
    expect(leaderState(metric("not_ordered", null), "model:a@1")).toBe("unranked");
  });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pnpm --dir frontend test src/api/__tests__/comparisons.test.ts`

Expected: FAIL — Vite cannot resolve the import `@/api/comparisons`, because the module does not exist yet. **Stated by its cause, not by a status:** every assertion in the file is unreached, so a run that reports individual assertion failures instead means the module resolved and something else is wrong.

- [ ] **Step 3: Add the `onPoll` callback to `waitForJob`**

The comparison scores a holdout for two or more models, so the wait is long enough that a caller needs to say something while it runs. `waitForJob` is the responsible layer and the change is additive — `RuleBuilder.vue`, its only existing caller, is unaffected.

Replace `frontend/src/api/jobs.ts:22-31` with:

```ts
export async function waitForJob(
  jobId: string,
  {
    attempts = 60,
    intervalMs = 1000,
    onPoll,
  }: { attempts?: number; intervalMs?: number; onPoll?: (job: Job) => void } = {},
): Promise<Job> {
  let job = await getJob(jobId);
  onPoll?.(job);
  for (let n = 1; n < attempts && !TERMINAL.includes(job.status); n += 1) {
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
    job = await getJob(jobId);
    onPoll?.(job);
  }
  return job;
}
```

Leave the existing doc comment above it untouched — its warning that the caller must read `status` is exactly what Task 6 depends on.

- [ ] **Step 4: Write `frontend/src/api/comparisons.ts`**

```ts
import { request } from "./client";
import type { components } from "./generated/schema";
import type { Job } from "./jobs";

export type ModelComparison = components["schemas"]["ModelComparison"];
export type ComparisonSummary = components["schemas"]["ComparisonSummary"];
export type ComparisonMetric = components["schemas"]["ComparisonMetric"];
export type ComparisonValue = components["schemas"]["ComparisonValue"];
export type DoubleLift = components["schemas"]["DoubleLift"];
export type DoubleLiftBin = components["schemas"]["DoubleLiftBin"];
export type RelativityDifference = components["schemas"]["RelativityDifference"];
export type MetricDirection = components["schemas"]["MetricDirection"];

/**
 * Start a comparison (FR-186). **202 with a Job, not the artifact** — the comparison
 * reads the holdout and scores every candidate, which is work.
 *
 * Every comparability rule is answered by this call before a Job exists — two or more models,
 * all fitted, one shared split, a baseline among them — so a 409 here is a complete answer
 * and not a job that will fail later. `baseline_id` is deliberately not sent: it defaults to
 * the first id, and `model_ids` is already ordered "in the order the table should present
 * them", so ordering the ids is how a caller chooses the baseline.
 */
export function startComparison(modelIds: readonly string[]): Promise<Job> {
  return request<Job>("/models/compare", {
    method: "POST",
    body: { model_ids: modelIds },
  });
}

/** The stored artifact (`02` §5.1), by comparison id. */
export function getComparison(comparisonId: string): Promise<ModelComparison> {
  return request<ModelComparison>(`/models/comparisons/${encodeURIComponent(comparisonId)}`);
}

/** The prefix `model_handlers.py:786` writes. Not `comparison:`, and not an ID-3 ref. */
const COMPARISON_REF = "model_comparison:";

/**
 * The comparison id a succeeded Job produced, or null.
 *
 * `JobResult.ref` is `{entity}:{uuid}` — a namespace of its own, not the ID-3
 * `{type}:{slug}@{version}` that `ComparisonValue.model_ref` carries. `model_comparison` is
 * not even a member of `refs.py`'s `ARTIFACT_TYPES`. The prefix is matched in full because a
 * looser check would also accept `model:{uuid}`, which a fit job emits.
 */
export function comparisonIdFromJob(job: Job): string | null {
  const ref = job.result?.ref;
  if (typeof ref !== "string" || !ref.startsWith(COMPARISON_REF)) return null;
  const id = ref.slice(COMPARISON_REF.length);
  return id.length > 0 ? id : null;
}

/**
 * `refs.py:30-43`'s `ModelRef` pattern, restated here because the frontend has no access to
 * the Python type and `ComparisonValue.model_ref` is published as an unconstrained string.
 * Kept character-for-character: slug is `[a-z0-9][a-z0-9-]{1,62}`, version `[1-9][0-9]*`.
 */
const MODEL_REF = /^model:([a-z0-9][a-z0-9-]{1,62})@([1-9][0-9]*)$/;

/**
 * Split an ID-3 model ref, or null when it does not parse.
 *
 * Null is a real outcome, not a defensive branch: `comparison.py` never imports `refs`, and
 * its four validators constrain only referential integrity inside the artifact. A caller
 * renders the raw string in that case rather than dropping it.
 */
export function parseModelRef(ref: string): { slug: string; version: number } | null {
  const match = MODEL_REF.exec(ref);
  return match === null ? null : { slug: match[1], version: Number(match[2]) };
}

/**
 * How one model stands on one metric.
 *
 * `02` §4.11 makes a null `leader` mean two different things — "the metric does not order"
 * **or** "the models tie", since "a winner chosen by tie-break is one the data did not
 * choose". `direction` is what separates them, and the view must show both.
 */
export function leaderState(
  metric: ComparisonMetric,
  modelRef: string,
): "leader" | "tied" | "unranked" | "behind" {
  if (metric.direction === "not_ordered") return "unranked";
  if (metric.leader === null || metric.leader === undefined) return "tied";
  return metric.leader === modelRef ? "leader" : "behind";
}
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pnpm --dir frontend test src/api/__tests__/comparisons.test.ts`
Expected: PASS, 6 tests.

- [ ] **Step 6: Type-check, because the fixture cast is where this task can be wrong**

Run: `pnpm --dir frontend type-check`
Expected: PASS. If `components["schemas"]["RelativityDifference"]` does not resolve, `pnpm --dir frontend generate:api` has not been run in this worktree — the generated file is git-ignored.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/api/comparisons.ts frontend/src/api/__tests__/comparisons.test.ts frontend/src/api/jobs.ts
git commit -m "feat(w6b-2): the comparison API module, and a poll callback on waitForJob"
```

---

## Task 2: `ModelRefLink` — one model reference, linked or plain

**Files:**
- Create: `frontend/src/components/ModelRefLink.vue`
- Test: `frontend/src/components/__tests__/ModelRefLink.test.ts`

**Interfaces:**
- Consumes: `parseModelRef` from `@/api/comparisons`.
- Produces: a component taking `defineProps<{ modelRef: string; muted?: boolean }>()`.

All three panels render model refs, so this exists once. `QuantileBoundNotice.vue` is the precedent for linking to another model version — it links `/models/{slug}?version={n}` — and `ModelDetailView.vue:156-168` is the precedent for *not* linking, where the reference is a bare UUID that resolves to no route.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/__tests__/ModelRefLink.test.ts`:

```ts
import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import ModelRefLink from "@/components/ModelRefLink.vue";

// The component renders a RouterLink, which needs the router symbol. A stub keeps this test
// about the parse rather than about routing; ModelComparisonView.test.ts exercises the real
// router.
const global = { stubs: { RouterLink: { props: ["to"], template: "<a :href='to'><slot /></a>" } } };

describe("ModelRefLink", () => {
  it("links a parseable ref to the model detail route, at its version", () => {
    render(ModelRefLink, { props: { modelRef: "model:motor-ad-frequency@7" }, global });
    const link = screen.getByRole("link", { name: /motor-ad-frequency/ });
    expect(link).toHaveAttribute("href", "/models/motor-ad-frequency?version=7");
    // The version is visible, not only in the href: `02` §4.11 keeps refs so "a comparison
    // read years later still names exactly which model versions it held".
    expect(link).toHaveTextContent("motor-ad-frequency@7");
  });

  // `comparison.py` imports Weighting, SplitRef and DecimalStr and never imports `refs`, so
  // `model_ref` is an unconstrained string on a perfectly valid artifact. An unparseable ref
  // is shown, not dropped — dropping it would leave a metric row with a nameless column.
  it("renders an unparseable ref as plain text, with no link", () => {
    render(ModelRefLink, { props: { modelRef: "legacy-model-4" }, global });
    expect(screen.getByText("legacy-model-4")).toBeInTheDocument();
    expect(screen.queryByRole("link")).toBeNull();
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir frontend test src/components/__tests__/ModelRefLink.test.ts`
Expected: FAIL — `@/components/ModelRefLink.vue` cannot be resolved.

- [ ] **Step 3: Write the component**

Create `frontend/src/components/ModelRefLink.vue`:

```vue
<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";

import { parseModelRef } from "@/api/comparisons";

const props = defineProps<{ modelRef: string; muted?: boolean }>();

// Null on a well-formed artifact, not only on a malformed one — see `parseModelRef`.
const parsed = computed(() => parseModelRef(props.modelRef));
</script>

<template>
  <RouterLink
    v-if="parsed"
    :to="`/models/${parsed.slug}?version=${parsed.version}`"
    class="font-mono text-xs underline decoration-slate-300 underline-offset-2 hover:decoration-slate-900"
    :class="muted ? 'text-slate-500' : 'text-slate-900'"
  >{{ parsed.slug }}@{{ parsed.version }}</RouterLink>
  <span
    v-else
    class="font-mono text-xs"
    :class="muted ? 'text-slate-500' : 'text-slate-900'"
    title="Not a versioned model reference, so it cannot be resolved to a model page"
  >{{ modelRef }}</span>
</template>
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pnpm --dir frontend test src/components/__tests__/ModelRefLink.test.ts`
Expected: PASS, 2 tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ModelRefLink.vue frontend/src/components/__tests__/ModelRefLink.test.ts
git commit -m "feat(w6b-2): render a model reference as a link, or as text when it does not parse"
```

---

## Task 3: `ComparisonMetricTable` — the aligned metric table

**Files:**
- Create: `frontend/src/components/ComparisonMetricTable.vue`
- Test: `frontend/src/components/__tests__/ComparisonMetricTable.test.ts`

**Interfaces:**
- Consumes: `ComparisonMetric`, `leaderState` from `@/api/comparisons`; `ModelRefLink` from Task 2.
- Produces: a component taking `defineProps<{ metrics: readonly ComparisonMetric[]; modelRefs: readonly string[] }>()`.

Models are columns and metrics are rows — that is what "aligned" means in FR-186, and §4.11's invariant that every metric carries a value for every model is what makes the grid rectangular. `modelRefs` comes from the summary rather than being derived from the metrics, so a metric measuring the wrong set would show as a gap rather than reshaping the table.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/__tests__/ComparisonMetricTable.test.ts`:

```ts
import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { ComparisonMetric } from "@/api/comparisons";
import ComparisonMetricTable from "@/components/ComparisonMetricTable.vue";

const global = { stubs: { RouterLink: { props: ["to"], template: "<a :href='to'><slot /></a>" } } };
const REFS = ["model:motor-ad-frequency@7", "model:motor-ad-frequency-gbm@2"];

const METRICS: ComparisonMetric[] = [
  {
    metric: "gini_normalised",
    weighting: "exposure",
    direction: "higher_is_better",
    values: [
      { model_ref: REFS[0], value: 0.412 },
      { model_ref: REFS[1], value: 0.43 },
    ],
    leader: REFS[1],
  },
  {
    metric: "rows",
    weighting: "exposure",
    direction: "not_ordered",
    values: [
      { model_ref: REFS[0], value: 169503 },
      { model_ref: REFS[1], value: 169503 },
    ],
    leader: null,
  },
  {
    metric: "deviance_ratio",
    weighting: "exposure",
    direction: "lower_is_better",
    values: [
      { model_ref: REFS[0], value: 0.77 },
      { model_ref: REFS[1], value: null },
    ],
    leader: REFS[0],
  },
];

function row(name: string): HTMLElement {
  return screen.getByRole("row", { name: new RegExp(name) });
}

describe("ComparisonMetricTable", () => {
  it("puts every model in a column and every metric in a row", () => {
    render(ComparisonMetricTable, { props: { metrics: METRICS, modelRefs: REFS }, global });
    expect(screen.getAllByRole("columnheader")).toHaveLength(REFS.length + 2); // metric, direction, two models
    expect(screen.getAllByRole("row")).toHaveLength(METRICS.length + 1);
  });

  // `02` §4.11: leader is null "where the metric does not order **or the models tie**". Two
  // different measurements, so they get two different words — not one blank cell each.
  it("says 'not ranked' for an unordered metric and 'tied' for a tie", () => {
    const tied: ComparisonMetric = { ...METRICS[0], leader: null };
    render(ComparisonMetricTable, { props: { metrics: [METRICS[1], tied], modelRefs: REFS }, global });
    expect(within(row("rows")).getByText(/not ranked/i)).toBeInTheDocument();
    expect(within(row("gini_normalised")).getByText(/tied/i)).toBeInTheDocument();
  });

  // §4.11: a value is null "where the metric does not apply, because a missing model reads as
  // one that scored nothing rather than one nobody measured". Rendering 0 or an empty cell is
  // the exact misreading that sentence forbids.
  it("renders a null value as 'n/a', never as a number", () => {
    render(ComparisonMetricTable, { props: { metrics: [METRICS[2]], modelRefs: REFS }, global });
    const cells = within(row("deviance_ratio")).getAllByRole("cell");
    expect(cells[2]).toHaveTextContent("0.77");
    expect(cells[3]).toHaveTextContent("n/a");
    expect(cells[3]).not.toHaveTextContent("0");
  });

  // The direction is on the row because §4.11 makes it "part of the metric, not the reader's
  // assumption" — a reader who cannot see it cannot tell whether 1.4 beat 1.0.
  it("shows each metric's direction", () => {
    render(ComparisonMetricTable, { props: { metrics: METRICS, modelRefs: REFS }, global });
    expect(within(row("gini_normalised")).getByText(/higher is better/i)).toBeInTheDocument();
    expect(within(row("deviance_ratio")).getByText(/lower is better/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir frontend test src/components/__tests__/ComparisonMetricTable.test.ts`
Expected: FAIL — `@/components/ComparisonMetricTable.vue` cannot be resolved.

- [ ] **Step 3: Write the component**

Create `frontend/src/components/ComparisonMetricTable.vue`:

```vue
<script setup lang="ts">
import type { ComparisonMetric, MetricDirection } from "@/api/comparisons";
import { leaderState } from "@/api/comparisons";
import ModelRefLink from "@/components/ModelRefLink.vue";

const props = defineProps<{
  metrics: readonly ComparisonMetric[];
  modelRefs: readonly string[];
}>();

const DIRECTION_LABEL: Record<MetricDirection, string> = {
  higher_is_better: "higher is better",
  lower_is_better: "lower is better",
  closer_to_one_is_better: "closer to 1 is better",
  not_ordered: "not ordered",
};

/**
 * The metric's value for one model, or `undefined` when the metric does not carry that model
 * at all. §4.11 makes that impossible on a well-formed artifact — every metric carries a
 * value for every model — so it renders as an em dash distinct from the `n/a` a stored null
 * gets, and the difference is the difference between "nobody measured" and "does not apply".
 */
function valueFor(metric: ComparisonMetric, modelRef: string): number | null | undefined {
  return metric.values.find((v) => v.model_ref === modelRef)?.value;
}

function format(value: number | null | undefined): string {
  if (value === undefined) return "—";
  if (value === null) return "n/a";
  // Integral values are counts (§4.11's `rows` is 169503.0) and reading "169503.0000" as a
  // measurement is worse than reading it as a count.
  return Number.isInteger(value) ? String(value) : value.toFixed(4);
}
</script>

<template>
  <table
    class="mt-2 w-full text-left text-sm"
    aria-label="Aligned metrics"
  >
    <thead>
      <tr class="border-b border-slate-200">
        <th
          scope="col"
          class="py-2 font-medium"
        >
          Metric
        </th>
        <th
          scope="col"
          class="py-2 font-medium"
        >
          Direction
        </th>
        <th
          v-for="ref in props.modelRefs"
          :key="ref"
          scope="col"
          class="py-2 font-medium"
        >
          <ModelRefLink :model-ref="ref" />
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="metric in props.metrics"
        :key="metric.metric"
        class="border-b border-slate-100"
      >
        <th
          scope="row"
          class="py-2 font-mono text-xs font-normal"
        >
          {{ metric.metric }}
        </th>
        <td class="py-2 text-xs text-slate-500">
          {{ DIRECTION_LABEL[metric.direction] }}
          <span
            v-if="metric.direction === 'not_ordered'"
            class="ml-1 rounded bg-slate-100 px-1 py-0.5 text-slate-600"
          >not ranked</span>
          <span
            v-else-if="metric.leader === null || metric.leader === undefined"
            class="ml-1 rounded bg-slate-100 px-1 py-0.5 text-slate-600"
          >tied</span>
        </td>
        <td
          v-for="ref in props.modelRefs"
          :key="ref"
          class="py-2 font-mono text-xs"
          :class="leaderState(metric, ref) === 'leader' ? 'font-semibold text-teal-800' : ''"
        >
          {{ format(valueFor(metric, ref)) }}
          <span
            v-if="leaderState(metric, ref) === 'leader'"
            class="ml-1 not-italic"
            aria-label="leads this metric"
            title="Leads this metric"
          >★</span>
        </td>
      </tr>
    </tbody>
  </table>
</template>
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pnpm --dir frontend test src/components/__tests__/ComparisonMetricTable.test.ts`
Expected: PASS, 4 tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ComparisonMetricTable.vue frontend/src/components/__tests__/ComparisonMetricTable.test.ts
git commit -m "feat(w6b-2): the aligned metric table, with tie and not-ordered as distinct readings"
```

---

## Task 4: `DoubleLiftChart` — one challenger against the baseline

**Files:**
- Create: `frontend/src/components/DoubleLiftChart.vue`
- Test: `frontend/src/components/__tests__/DoubleLiftChart.test.ts`

**Interfaces:**
- Consumes: `DoubleLift` from `@/api/comparisons`.
- Produces: a component taking `defineProps<{ series: DoubleLift }>()`.

Follow `HistogramChart.vue` exactly for the ECharts shape: tree-shaken imports, a module-level `use([...])`, one `computed` option object with `as const` on every ECharts string literal, and `<VChart class="h-80 w-full" :option="option" autoresize />`.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/__tests__/DoubleLiftChart.test.ts`:

```ts
import { render, screen } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import type { DoubleLift } from "@/api/comparisons";
import DoubleLiftChart from "@/components/DoubleLiftChart.vue";

// `HistogramChart.test.ts`'s precedent: mock the renderer and assert against the option
// object, because a canvas in happy-dom tells you nothing about what was plotted.
vi.mock("vue-echarts", () => ({
  default: {
    name: "VChart",
    props: ["option"],
    template: "<div data-testid='chart'>{{ JSON.stringify(option) }}</div>",
  },
}));

// Bins deliberately out of ascending prediction order and in ascending *ratio* order, which
// is the order `02` §4.11 says the server already produced.
const SERIES: DoubleLift = {
  baseline_ref: "model:motor-ad-frequency@7",
  challenger_ref: "model:motor-ad-frequency-gbm@2",
  weighting: "exposure",
  bins: [
    { bin: 1, rows: 16950, actual: 0.0491, baseline_predicted: 0.0523, challenger_predicted: 0.0447, exposure_years: "14203.400000" },
    { bin: 2, rows: 16950, actual: 0.0402, baseline_predicted: 0.0399, challenger_predicted: 0.0405, exposure_years: "14180.000000" },
    { bin: 3, rows: 16950, actual: 0.0350, baseline_predicted: 0.0310, challenger_predicted: 0.0372, exposure_years: "14150.000000" },
  ],
};

function option(): Record<string, unknown> {
  return JSON.parse(screen.getByTestId("chart").textContent ?? "{}");
}

describe("DoubleLiftChart", () => {
  // §4.11: bins are ordered by the RATIO of the two predictions, and sorting by either
  // prediction "gives two lift curves side by side, which answers a different and much weaker
  // question". A re-sort here would substitute that question silently.
  it("plots the bins in the order the artifact gave them", () => {
    render(DoubleLiftChart, { props: { series: SERIES } });
    const opt = option() as { xAxis: { data: string[] }; series: { data: number[] }[] };
    expect(opt.xAxis.data).toEqual(["1", "2", "3"]);
    const baseline = opt.series.find((s) => (s as { name?: string }).name === "Baseline predicted");
    expect(baseline?.data).toEqual([0.0523, 0.0399, 0.031]);
  });

  it("plots actual, baseline and challenger as three separate series", () => {
    render(DoubleLiftChart, { props: { series: SERIES } });
    const names = (option().series as { name: string }[]).map((s) => s.name);
    expect(names).toContain("Actual");
    expect(names).toContain("Baseline predicted");
    expect(names).toContain("Challenger predicted");
  });

  // NFR-463 is WCAG 2.2 AA. Three lines separable only by hue fail for a reader who cannot
  // distinguish them, so line type carries the same information.
  it("distinguishes the three series by line type as well as colour", () => {
    render(DoubleLiftChart, { props: { series: SERIES } });
    const lines = (option().series as { type: string; lineStyle?: { type?: string } }[]).filter((s) => s.type === "line");
    const types = lines.map((s) => s.lineStyle?.type ?? "solid");
    expect(new Set(types).size).toBe(lines.length);
  });

  // `exposure_years` is a DecimalStr — a string on the wire (FR-10's exact-decimal type).
  // It must reach ECharts as a number or the bars silently do not draw.
  it("converts the decimal-string exposure to numbers", () => {
    render(DoubleLiftChart, { props: { series: SERIES } });
    const exposure = (option().series as { name: string; data: unknown[] }[]).find((s) => s.name === "Exposure");
    expect(exposure?.data).toEqual([14203.4, 14180, 14150]);
  });

  // The same field is nullable, and a partly-populated exposure would draw a bar chart with
  // silent holes in it. Omit the series rather than plot a hole.
  it("omits the exposure series when any bin is missing it", () => {
    const partial: DoubleLift = {
      ...SERIES,
      bins: SERIES.bins.map((b, i) => (i === 1 ? { ...b, exposure_years: null } : b)),
    };
    render(DoubleLiftChart, { props: { series: partial } });
    const names = (option().series as { name: string }[]).map((s) => s.name);
    expect(names).not.toContain("Exposure");
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir frontend test src/components/__tests__/DoubleLiftChart.test.ts`
Expected: FAIL — `@/components/DoubleLiftChart.vue` cannot be resolved.

- [ ] **Step 3: Write the component**

Create `frontend/src/components/DoubleLiftChart.vue`:

```vue
<script setup lang="ts">
import { BarChart, LineChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

import type { DoubleLift } from "@/api/comparisons";

use([BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{ series: DoubleLift }>();

/**
 * Bins in the artifact's own order. `02` §4.11 orders them by the **ratio** of the two
 * predictions, which is what makes the chart answer "where the models disagree, which one is
 * right?"; re-sorting by either prediction answers the weaker question instead.
 */
const bins = computed(() => props.series.bins);

const labels = computed(() => bins.value.map((b) => String(b.bin)));

/**
 * `exposure_years` is a `DecimalStr` — exact decimal, carried as a string, so a float never
 * silently rounds it (FR-10's rule about the rating path; here it is a diagnostic read and
 * the conversion is safe). It is also nullable, and a bar chart with holes in it reads as
 * zero exposure rather than as unknown exposure, so the whole series is omitted unless every
 * bin has one.
 */
const exposure = computed(() => {
  const raw = bins.value.map((b) => b.exposure_years);
  return raw.every((v) => typeof v === "string") ? raw.map((v) => Number(v)) : null;
});

const option = computed(() => ({
  tooltip: { trigger: "axis" as const },
  legend: { bottom: 0 },
  grid: { left: 56, right: 56, top: 16, bottom: 56 },
  xAxis: {
    type: "category" as const,
    data: labels.value,
    name: "Bin (by prediction ratio)",
    nameLocation: "middle" as const,
    nameGap: 30,
  },
  yAxis: [
    { type: "value" as const, name: "Rate", position: "left" as const },
    ...(exposure.value
      ? [{ type: "value" as const, name: "Exposure", position: "right" as const, splitLine: { show: false } }]
      : []),
  ],
  series: [
    // Grey is reserved for exposure across every chart in this app (HistogramChart.vue).
    ...(exposure.value
      ? [
          {
            name: "Exposure",
            type: "bar" as const,
            yAxisIndex: 1,
            data: exposure.value,
            itemStyle: { color: "#cbd5e1" },
          },
        ]
      : []),
    // Actual is the reference truth, so it takes the neutral darkest and a solid line. The
    // three lines differ by line type as well as by hue, which is what NFR-463's WCAG
    // obligation needs.
    {
      name: "Actual",
      type: "line" as const,
      data: bins.value.map((b) => b.actual),
      itemStyle: { color: "#0f172a" },
      lineStyle: { color: "#0f172a", type: "solid" as const, width: 2 },
    },
    {
      name: "Baseline predicted",
      type: "line" as const,
      data: bins.value.map((b) => b.baseline_predicted),
      itemStyle: { color: "#0f766e" },
      lineStyle: { color: "#0f766e", type: "dashed" as const, width: 2 },
    },
    {
      name: "Challenger predicted",
      type: "line" as const,
      data: bins.value.map((b) => b.challenger_predicted),
      itemStyle: { color: "#b45309" },
      lineStyle: { color: "#b45309", type: "dotted" as const, width: 2 },
    },
  ],
}));
</script>

<template>
  <div>
    <VChart
      class="h-80 w-full"
      :option="option"
      autoresize
    />
  </div>
</template>
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pnpm --dir frontend test src/components/__tests__/DoubleLiftChart.test.ts`
Expected: PASS, 5 tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/DoubleLiftChart.vue frontend/src/components/__tests__/DoubleLiftChart.test.ts
git commit -m "feat(w6b-2): the double-lift chart, in the artifact's own ratio order"
```

---

## Task 5: `RelativityDiffTable` — factor by factor

**Files:**
- Create: `frontend/src/components/RelativityDiffTable.vue`
- Test: `frontend/src/components/__tests__/RelativityDiffTable.test.ts`

**Interfaces:**
- Consumes: `RelativityDifference` from `@/api/comparisons`; `ModelRefLink` from Task 2.
- Produces: a component taking `defineProps<{ differences: readonly RelativityDifference[]; modelRefs: readonly string[] }>()`.

`RelativityDifference` is `factor`, `level`, `values` (the same `ComparisonValue` shape the metrics use, min 2) and `max_abs_difference: float | None`. Rows are per factor **level**, so they are grouped by factor and ordered largest difference first within each group — that is the order an actuary reads a relativity diff in, and the artifact does not impose one.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/__tests__/RelativityDiffTable.test.ts`:

```ts
import { render, screen, within } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { RelativityDifference } from "@/api/comparisons";
import RelativityDiffTable from "@/components/RelativityDiffTable.vue";

const global = { stubs: { RouterLink: { props: ["to"], template: "<a :href='to'><slot /></a>" } } };
const REFS = ["model:motor-ad-frequency@7", "model:motor-ad-frequency-gbm@2"];

const DIFFS: RelativityDifference[] = [
  {
    factor: "driver_age_banded",
    level: "21-25",
    values: [
      { model_ref: REFS[0], value: 1.31 },
      { model_ref: REFS[1], value: 1.34 },
    ],
    max_abs_difference: 0.03,
  },
  {
    factor: "driver_age_banded",
    level: "17-20",
    values: [
      { model_ref: REFS[0], value: 1.718 },
      { model_ref: REFS[1], value: 1.902 },
    ],
    max_abs_difference: 0.184,
  },
  {
    factor: "vehicle_group",
    level: "G12",
    values: [
      { model_ref: REFS[0], value: 0.91 },
      { model_ref: REFS[1], value: null },
    ],
    max_abs_difference: null,
  },
];

describe("RelativityDiffTable", () => {
  it("groups the levels under their factor", () => {
    render(RelativityDiffTable, { props: { differences: DIFFS, modelRefs: REFS }, global });
    expect(screen.getByRole("heading", { name: "driver_age_banded" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "vehicle_group" })).toBeInTheDocument();
  });

  // The largest disagreement is the row a selection decision turns on, and the artifact
  // imposes no order — so this is the view's ordering, applied within a factor only.
  it("orders levels within a factor by descending absolute difference", () => {
    render(RelativityDiffTable, { props: { differences: DIFFS, modelRefs: REFS }, global });
    const table = screen.getByRole("table", { name: /driver_age_banded/ });
    const levels = within(table).getAllByRole("rowheader").map((el) => el.textContent?.trim());
    expect(levels).toEqual(["17-20", "21-25"]);
  });

  // Same rule as the metric table: a null relativity is "does not apply", never zero. Here it
  // also means `max_abs_difference` is null, because a difference against nothing is not 0.
  it("renders a null relativity and a null difference as 'n/a'", () => {
    render(RelativityDiffTable, { props: { differences: [DIFFS[2]], modelRefs: REFS }, global });
    const cells = within(screen.getByRole("row", { name: /G12/ })).getAllByRole("cell");
    expect(cells.map((c) => c.textContent?.trim())).toContain("n/a");
    expect(cells.map((c) => c.textContent?.trim())).not.toContain("0.0000");
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir frontend test src/components/__tests__/RelativityDiffTable.test.ts`
Expected: FAIL — `@/components/RelativityDiffTable.vue` cannot be resolved.

- [ ] **Step 3: Write the component**

Create `frontend/src/components/RelativityDiffTable.vue`:

```vue
<script setup lang="ts">
import { computed } from "vue";

import type { RelativityDifference } from "@/api/comparisons";
import ModelRefLink from "@/components/ModelRefLink.vue";

const props = defineProps<{
  differences: readonly RelativityDifference[];
  modelRefs: readonly string[];
}>();

/**
 * One group per factor, levels ordered by descending absolute difference within it.
 *
 * The artifact imposes no order on `relativity_differences`, so this is the view's — and it
 * is applied **within** a factor rather than across all of them, because a table sorted
 * globally scatters one factor's levels through the page and stops being a factor-by-factor
 * diff, which is what FR-186 asks for.
 */
const groups = computed(() => {
  const byFactor = new Map<string, RelativityDifference[]>();
  for (const diff of props.differences) {
    const existing = byFactor.get(diff.factor);
    if (existing) existing.push(diff);
    else byFactor.set(diff.factor, [diff]);
  }
  return [...byFactor.entries()].map(([factor, rows]) => ({
    factor,
    rows: [...rows].sort((a, b) => (b.max_abs_difference ?? -1) - (a.max_abs_difference ?? -1)),
  }));
});

function valueFor(diff: RelativityDifference, modelRef: string): number | null | undefined {
  return diff.values.find((v) => v.model_ref === modelRef)?.value;
}

function format(value: number | null | undefined): string {
  if (value === undefined) return "—";
  if (value === null) return "n/a";
  return value.toFixed(4);
}
</script>

<template>
  <div
    v-for="group in groups"
    :key="group.factor"
    class="mt-5"
  >
    <h3 class="font-mono text-xs font-semibold text-slate-700">
      {{ group.factor }}
    </h3>
    <table
      class="mt-2 w-full text-left text-sm"
      :aria-label="`Relativity differences for ${group.factor}`"
    >
      <thead>
        <tr class="border-b border-slate-200">
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Level
          </th>
          <th
            v-for="ref in props.modelRefs"
            :key="ref"
            scope="col"
            class="py-2 font-medium"
          >
            <ModelRefLink :model-ref="ref" />
          </th>
          <th
            scope="col"
            class="py-2 font-medium"
          >
            Max abs difference
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="diff in group.rows"
          :key="diff.level"
          class="border-b border-slate-100"
        >
          <th
            scope="row"
            class="py-2 font-mono text-xs font-normal"
          >
            {{ diff.level }}
          </th>
          <td
            v-for="ref in props.modelRefs"
            :key="ref"
            class="py-2 font-mono text-xs"
          >
            {{ format(valueFor(diff, ref)) }}
          </td>
          <td class="py-2 font-mono text-xs">
            {{ format(diff.max_abs_difference) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pnpm --dir frontend test src/components/__tests__/RelativityDiffTable.test.ts`
Expected: PASS, 3 tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/RelativityDiffTable.vue frontend/src/components/__tests__/RelativityDiffTable.test.ts
git commit -m "feat(w6b-2): the factor-by-factor relativity difference table"
```

---

## Task 6: The view and the route — `POST` → poll → `GET`

**Files:**
- Modify: `frontend/src/router/index.ts`
- Create: `frontend/src/views/ModelComparisonView.vue`
- Modify: `frontend/src/views/__tests__/fixtures.ts`
- Test: `frontend/src/views/__tests__/ModelComparisonView.test.ts`

**Interfaces:**
- Consumes: everything from Tasks 1-5; `waitForJob`, `TERMINAL` from `@/api/jobs`; `ProblemError` from `@/api/problem`.
- Produces: the route named `model-comparison`.

**This task is the slice.** The three panels are rendering; this is the asynchronous sequence, and the frontend's only precedent (`RuleBuilder.vue:76-84`) polls a job and then *stops* — it never fetches the artifact the job produced. So the two things without precedent here are **reading `JobResult.ref` to find the artifact** and **a poll long enough that running out of attempts is a state a user will actually see**.

### The route ordering risk, and why it gets a test

`/models/compare` and `/models/:slug` both match the path `/models/compare`. Vue Router ranks a static segment above a dynamic one, so the static route should win regardless of declaration order — but "should" is the word this repository's conventions exist to remove, and the failure mode is a page that renders a 404 for a model named `compare` instead of the comparison view. The route is declared **before** `/models/:slug` and a test resolves the path and asserts the name.

### The poll budget

`waitForJob`'s default is 60 attempts at 1000 ms, i.e. one minute. A comparison scores a holdout for two or more models; §4.11's own example holdout is 169,503 rows. **No NFR names a budget for `MODEL_COMPARE`,** so five minutes (150 attempts at 2000 ms) is a chosen ceiling and not a measured one. What makes the choice non-fatal is that the "still running" branch is rendered explicitly rather than as a failure — see below.

- [ ] **Step 1: Add the fixture**

Append to `frontend/src/views/__tests__/fixtures.ts`. It is annotated with the generated type, per that file's own header rule: annotation is what makes contract drift fail `type-check` instead of review.

```ts
import type { ModelComparison } from "@/api/comparisons";

/**
 * `02` §4.11's own example, transcribed. The spec writes the large integers with numeric
 * separators (`169_503`); they are written plainly here because the two forms are equal in
 * TypeScript and a reader diffing this against the spec should not have to check that.
 */
export const COMPARISON: ModelComparison = {
  id: "5c1b0e6a-7777-4888-8999-aaaabbbbcccc",
  computed_at: "2026-08-17T15:20:11Z",
  job_id: "1a2b3c4d-5555-4666-8777-888899990000",
  summary: {
    model_refs: ["model:motor-ad-frequency@7", "model:motor-ad-frequency-gbm@2"],
    baseline_ref: "model:motor-ad-frequency@7",
    split_ref: {
      split_artifact_id: "9f8e7d6c-1111-4222-8333-444455556666",
      train_part: "train",
      holdout_part: "test",
    },
    holdout_rows: 169503,
    metrics: [
      {
        metric: "gini_normalised",
        weighting: "exposure",
        direction: "higher_is_better",
        values: [
          { model_ref: "model:motor-ad-frequency@7", value: 0.412 },
          { model_ref: "model:motor-ad-frequency-gbm@2", value: 0.43 },
        ],
        leader: "model:motor-ad-frequency-gbm@2",
      },
      {
        metric: "ae_overall",
        weighting: "exposure",
        direction: "closer_to_one_is_better",
        values: [
          { model_ref: "model:motor-ad-frequency@7", value: 1.001 },
          { model_ref: "model:motor-ad-frequency-gbm@2", value: 0.994 },
        ],
        leader: "model:motor-ad-frequency@7",
      },
    ],
    double_lift: [
      {
        baseline_ref: "model:motor-ad-frequency@7",
        challenger_ref: "model:motor-ad-frequency-gbm@2",
        weighting: "exposure",
        bins: [
          {
            bin: 1,
            rows: 16950,
            actual: 0.0491,
            baseline_predicted: 0.0523,
            challenger_predicted: 0.0447,
            exposure_years: "14203.400000",
          },
        ],
      },
    ],
    relativity_differences: [
      {
        factor: "driver_age_banded",
        level: "17-20",
        values: [
          { model_ref: "model:motor-ad-frequency@7", value: 1.718 },
          { model_ref: "model:motor-ad-frequency-gbm@2", value: 1.902 },
        ],
        max_abs_difference: 0.184,
      },
    ],
  },
};
```

- [ ] **Step 2: Write the failing view test**

Create `frontend/src/views/__tests__/ModelComparisonView.test.ts`:

```ts
import { render, screen, waitFor } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import { router } from "@/router";
import ModelComparisonView from "@/views/ModelComparisonView.vue";

import { COMPARISON } from "./fixtures";

// The three panels are tested in their own files; stub them so this test is about the state
// machine. ProfileView.test.ts is the precedent for the template-stub shape.
vi.mock("@/components/ComparisonMetricTable.vue", () => ({
  default: { name: "ComparisonMetricTable", props: ["metrics", "modelRefs"], template: "<div data-testid='metrics' />" },
}));
vi.mock("@/components/DoubleLiftChart.vue", () => ({
  default: { name: "DoubleLiftChart", props: ["series"], template: "<div data-testid='double-lift' />" },
}));
vi.mock("@/components/RelativityDiffTable.vue", () => ({
  default: { name: "RelativityDiffTable", props: ["differences", "modelRefs"], template: "<div data-testid='relativity' />" },
}));

const routeQuery: { ids?: string } = {};
vi.mock("vue-router", async (importOriginal) => ({
  ...(await importOriginal<typeof import("vue-router")>()),
  useRoute: () => ({ query: routeQuery }),
}));

const IDS = "11111111-1111-4111-8111-111111111111,22222222-2222-4222-8222-222222222222";
const COMPARISON_REF = `model_comparison:${COMPARISON.id}`;

/**
 * A fetch stub that answers by URL, because this page makes three different calls.
 *
 * Modelled on `ModelDetailView.test.ts:64`'s `stubByUrl` and **deliberately not shared with
 * it**: that one is `Record<string, unknown>` and always answers 200, which cannot express
 * the 202 the POST returns or the 409 a refusal returns — both of which this page branches
 * on. Its behaviour for an unstubbed URL is kept exactly, a real problem document carrying
 * `code: "NOT_FOUND"`, because views branch on the code and never on the status.
 */
function stubByUrl(routes: Record<string, { status?: number; body: unknown }>): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      const key = Object.keys(routes).find((path) => url.includes(path));
      const hit = key ? routes[key] : undefined;
      const body = hit?.body ?? { type: "about:blank", title: "Not found", status: 404, code: "NOT_FOUND" };
      return new Response(JSON.stringify(body), {
        status: hit?.status ?? 404,
        headers: { "Content-Type": "application/json" },
      });
    }),
  );
}

function job(status: string, ref: string | null = null): unknown {
  return {
    id: "1a2b3c4d-5555-4666-8777-888899990000",
    kind: "model_compare",
    status,
    result: ref ? { kind: "artifact", ref } : null,
    error: status === "failed" ? { code: "SPLIT_MISMATCH", message: "The models do not share a holdout.", retryable: false } : null,
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
  delete routeQuery.ids;
});

describe("ModelComparisonView", () => {
  it("declares /models/compare as a static route that wins over /models/:slug", () => {
    // Both routes match this path. Vue Router ranks static above dynamic, but a model whose
    // slug is literally `compare` is legal under refs.py's slug pattern, so the resolution is
    // asserted rather than assumed.
    expect(router.resolve("/models/compare").name).toBe("model-comparison");
    expect(router.resolve("/models/motor-ad-frequency").name).toBe("model-detail");
  });

  it("posts, polls, then fetches the artifact the job names", async () => {
    routeQuery.ids = IDS;
    stubByUrl({
      "/models/compare": { status: 202, body: job("queued") },
      "/jobs/": { status: 200, body: job("succeeded", COMPARISON_REF) },
      [`/models/comparisons/${COMPARISON.id}`]: { status: 200, body: COMPARISON },
    });
    render(ModelComparisonView, { props: { pollIntervalMs: 0 } });

    await waitFor(() => expect(screen.getByTestId("metrics")).toBeInTheDocument());
    expect(screen.getByTestId("double-lift")).toBeInTheDocument();
    expect(screen.getByTestId("relativity")).toBeInTheDocument();
    // FR-76 makes the shared holdout stored rather than promised, and §4.11 keeps the
    // SplitRef "so the claim is checkable by a reader". The reader has to be shown it.
    expect(screen.getByText(/169503/)).toBeInTheDocument();
  });

  // `waitForJob` returns the job in whatever state it is in, so a failed job arrives through
  // the success path. Its `error.message` is the only thing that says what went wrong.
  it("shows a failed job's message, and does not fetch an artifact", async () => {
    routeQuery.ids = IDS;
    stubByUrl({
      "/models/compare": { status: 202, body: job("queued") },
      "/jobs/": { status: 200, body: job("failed") },
    });
    render(ModelComparisonView, { props: { pollIntervalMs: 0 } });

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/do not share a holdout/));
    expect(screen.queryByTestId("metrics")).toBeNull();
  });

  // The state `waitForJob`'s own doc comment warns about: attempts ran out and the job is
  // still running. It is NOT a failure, and telling a user the comparison failed when it is
  // still computing is the specific misreading that comment exists to prevent.
  it("distinguishes 'still running' from 'failed' when the poll budget runs out", async () => {
    routeQuery.ids = IDS;
    stubByUrl({
      "/models/compare": { status: 202, body: job("queued") },
      "/jobs/": { status: 200, body: job("running") },
    });
    render(ModelComparisonView, { props: { pollIntervalMs: 0, pollAttempts: 3 } });

    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent(/still running/i));
    expect(screen.queryByRole("alert")).toBeNull();
  });

  // The comparability rules are answered by the POST before a Job exists, so a 409 here is a
  // complete answer and must be shown as one rather than retried.
  it("shows the problem document when the comparison is refused", async () => {
    routeQuery.ids = IDS;
    stubByUrl({
      "/models/compare": {
        status: 409,
        body: { type: "about:blank", title: "Models do not share a split", status: 409, code: "CONFLICT", detail: "motor-ad-frequency-gbm@2 was fitted on a different split." },
      },
    });
    render(ModelComparisonView, { props: { pollIntervalMs: 0 } });

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Models do not share a split"));
  });

  // FR-186 compares "two or more". One id is a diagnostics read, and the endpoint would
  // 422 it — refusing before the request makes that a sentence rather than a stack trace.
  it("refuses fewer than two ids without calling the API", async () => {
    routeQuery.ids = "11111111-1111-4111-8111-111111111111";
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    render(ModelComparisonView, { props: { pollIntervalMs: 0 } });

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/two or more/i));
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 3: Run it to verify it fails**

Run: `pnpm --dir frontend test src/views/__tests__/ModelComparisonView.test.ts`
Expected: FAIL — `@/views/ModelComparisonView.vue` cannot be resolved. The route test fails for the same reason once the module resolves and the route is still missing; that second failure is the one that proves the route was added, so do not skip re-running after Step 4.

- [ ] **Step 4: Add the route**

In `frontend/src/router/index.ts`, insert **immediately before** the `/models/:slug` entry (currently at lines 54-62):

```ts
  {
    // `02` §5.3. Declared before `/models/:slug` because both match this path. Vue Router
    // ranks a static segment above a dynamic one, so order is belt and braces — but a model
    // slug of `compare` is legal under `refs.py`'s pattern, and this is the route that wins.
    // No `props: true`: it maps path params only, and this view's input is a query. The
    // `/models/:slug` entry below is the precedent for a query-carried input.
    path: "/models/compare",
    name: "model-comparison",
    component: () => import("@/views/ModelComparisonView.vue"),
  },
```

- [ ] **Step 5: Write the view**

Create `frontend/src/views/ModelComparisonView.vue`:

```vue
<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";

import type { ModelComparison } from "@/api/comparisons";
import { comparisonIdFromJob, getComparison, startComparison } from "@/api/comparisons";
import { TERMINAL, waitForJob } from "@/api/jobs";
import { ProblemError } from "@/api/problem";

import ComparisonMetricTable from "@/components/ComparisonMetricTable.vue";
import DoubleLiftChart from "@/components/DoubleLiftChart.vue";
import RelativityDiffTable from "@/components/RelativityDiffTable.vue";

/**
 * The poll budget, injectable so a test does not wait real seconds.
 *
 * Five minutes by default. No NFR names a budget for `MODEL_COMPARE`, so this is a chosen
 * ceiling rather than a measured one — which is safe only because running out of it renders
 * as "still running" and never as a failure.
 */
const props = withDefaults(
  defineProps<{ pollAttempts?: number; pollIntervalMs?: number }>(),
  { pollAttempts: 150, pollIntervalMs: 2000 },
);

const route = useRoute();

const comparison = ref<ModelComparison | null>(null);
const problem = ref<ProblemError | null>(null);
/**
 * A discriminated stage rather than a set of booleans (RuleBuilder.vue's precedent). `waiting`
 * and `stalled` are different things to tell a user, which is why `waitForJob` returns a
 * non-terminal job rather than throwing.
 */
const stage = ref<"starting" | "waiting" | "ready" | "failed" | "stalled" | "refused">("starting");
const jobStage = ref("");
const failure = ref("");

/** `?ids=a,b` — UUIDs, because `CompareModels.model_ids` is a tuple of UUIDs. */
function idsFromQuery(): string[] {
  const raw = typeof route.query.ids === "string" ? route.query.ids : "";
  return raw.split(",").map((id) => id.trim()).filter((id) => id.length > 0);
}

onMounted(async () => {
  const ids = idsFromQuery();
  // FR-186 compares two or more; "one model measured against nothing is a diagnostics
  // read" (§4.11). Refusing here turns a 422 into a sentence.
  if (ids.length < 2) {
    stage.value = "refused";
    failure.value = "Select two or more models to compare — one model measured against nothing is a diagnostics read.";
    return;
  }

  try {
    const accepted = await startComparison(ids);
    stage.value = "waiting";
    const job = await waitForJob(accepted.id, {
      attempts: props.pollAttempts,
      intervalMs: props.pollIntervalMs,
      onPoll: (polled) => {
        jobStage.value = polled.progress?.stage ?? "";
      },
    });

    // `waitForJob` returns whatever state it reached, so all three outcomes arrive here.
    if (!TERMINAL.includes(job.status)) {
      stage.value = "stalled";
      return;
    }
    if (job.status !== "succeeded") {
      stage.value = "failed";
      failure.value = job.error?.message ?? `The comparison ${job.status}.`;
      return;
    }

    const comparisonId = comparisonIdFromJob(job);
    if (comparisonId === null) {
      stage.value = "failed";
      failure.value = "The comparison finished but did not name an artifact to read.";
      return;
    }
    comparison.value = await getComparison(comparisonId);
    stage.value = "ready";
  } catch (error) {
    // A ProblemError from the POST is a complete answer — every comparability rule is
    // decided before a Job exists, so a 409 here means the request was wrong, not that a run
    // failed. Anything that is not a problem document is rethrown, never swallowed.
    if (error instanceof ProblemError) {
      problem.value = error;
      stage.value = "failed";
    } else throw error;
  }
});
</script>

<template>
  <section>
    <header class="mb-5">
      <RouterLink
        to="/models"
        class="text-sm text-slate-500 underline"
      >Models</RouterLink>
      <h1 class="mt-1 text-xl font-semibold tracking-tight">
        Model comparison
      </h1>
      <p
        v-if="comparison"
        class="mt-1 text-sm text-slate-500"
      >
        {{ comparison.summary.model_refs.length }} models on a shared holdout of
        {{ comparison.summary.holdout_rows }} rows
        <span class="font-mono text-xs">({{ comparison.summary.split_ref.holdout_part }})</span>
      </p>
    </header>

    <p
      v-if="stage === 'starting' || stage === 'waiting'"
      role="status"
      class="text-sm text-slate-500"
    >
      {{ stage === "starting" ? "Starting the comparison…" : `Scoring the holdout…${jobStage ? ` ${jobStage}` : ""}` }}
    </p>

    <p
      v-else-if="stage === 'stalled'"
      role="status"
      class="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"
    >
      The comparison is still running. It has not failed — reload this page to pick it up.
    </p>

    <div
      v-else-if="stage === 'failed' || stage === 'refused'"
      role="alert"
      class="rounded-md border border-red-200 bg-red-50 p-4"
    >
      <p class="font-medium text-red-900">
        {{ problem ? problem.problem.title : "The comparison did not produce a result" }}
      </p>
      <p class="mt-1 text-sm text-red-800">
        {{ problem ? problem.problem.detail : failure }}
      </p>
    </div>

    <template v-else-if="comparison">
      <h2 class="mt-6 text-sm font-semibold uppercase tracking-wide text-slate-500">
        Aligned metrics
      </h2>
      <ComparisonMetricTable
        :metrics="comparison.summary.metrics"
        :model-refs="comparison.summary.model_refs"
      />

      <template v-if="comparison.summary.double_lift.length">
        <h2 class="mt-8 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Double lift
        </h2>
        <div
          v-for="series in comparison.summary.double_lift"
          :key="series.challenger_ref"
        >
          <p class="mt-3 text-sm text-slate-500">
            Baseline against {{ series.challenger_ref }}, {{ series.weighting }}-weighted, binned by
            the ratio of the two predictions
          </p>
          <DoubleLiftChart :series="series" />
        </div>
      </template>

      <template v-if="comparison.summary.relativity_differences.length">
        <h2 class="mt-8 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Relativity differences
        </h2>
        <RelativityDiffTable
          :differences="comparison.summary.relativity_differences"
          :model-refs="comparison.summary.model_refs"
        />
      </template>
    </template>
  </section>
</template>
```

- [ ] **Step 6: Run the view tests to verify they pass**

Run: `pnpm --dir frontend test src/views/__tests__/ModelComparisonView.test.ts`
Expected: PASS, 6 tests.

- [ ] **Step 7: Prove the route ordering test can fail**

`CLAUDE.md` §13: a check that has never printed a failure has not been tested. Temporarily move the `/models/compare` route entry to **after** `/models/:slug` and re-run.

Run: `pnpm --dir frontend test src/views/__tests__/ModelComparisonView.test.ts -t "static route"`

Two outcomes, and both are worth recording in the commit message:
- **FAIL** — declaration order matters here, and the comment in the route entry is load-bearing rather than decorative.
- **PASS** — Vue Router's static-over-dynamic ranking is doing the work and order is genuinely belt and braces. The comment stays, reworded to say the ranking is what protects this and the order is defensive.

Restore the original order either way.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/router/index.ts frontend/src/views/ModelComparisonView.vue frontend/src/views/__tests__/ModelComparisonView.test.ts frontend/src/views/__tests__/fixtures.ts
git commit -m "feat(w6b-2): the model comparison view, post to poll to artifact"
```

---

## Task 7: The gate, and the findings this slice records rather than fixes

**Files:** none created; this task runs the gate and writes the findings into the PR body.

- [ ] **Step 1: Run the frontend half of the gate in full**

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend lint
pnpm --dir frontend type-check
pnpm --dir frontend test
pnpm --dir frontend build
```

Expected: all six pass. `lint` is where the template formatting rules bite — this repository's ESLint config enforces one attribute per line on multi-attribute elements, which every template above already follows.

- [ ] **Step 2: Run the Python and docs half**

```bash
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
```

Expected: audit passes. `req-coverage.py` **cannot see the frontend** — it will not mark FR-186 as evidenced by anything in this slice, and that is the script's known blind spot rather than a gap in the work. Do not add a marker to make it look otherwise.

- [ ] **Step 3: Record the three scope findings in the PR body**

None of these is fixed by this slice. Each is stated so the next planner inherits it rather than rediscovers it.

**Finding 1 — nothing links to `/models/compare`.** The route is reachable only by a typed URL. No §5.3 Contents cell places a compare entry point: the Model detail cell is "Spec summary, coefficient/relativity tables with CI bars, fit metadata, lineage strip, flags", and a model list with multi-select is in no cell at all. Building one would be inventing a view §5.3 does not describe (`CLAUDE.md` §0 puts an unspecified capability in the spec first). *A missing neighbour is a scope finding* — `docs/plans/README.md`. **Route to the work lead as a spec question:** which view carries the entry point, and does its Contents cell need a row?

**Finding 2 — a model whose slug is `compare` becomes unreachable at `/models/compare`.** `refs.py`'s `_SLUG` is `[a-z0-9][a-z0-9-]{1,62}`, which accepts `compare`, and no backend rule reserves it. The collision is in the frontend routing only; the model is still reachable through the API and through `/models/compare?version=N` would resolve to the comparison view, not to it. Low likelihood, zero cost to record, and the fix — a reserved-slug list, or moving the view to `/models/comparison` — is a spec change to §5.3's Route column.

**Finding 3 — `?ids=` carries UUIDs, against every other URL in the app.** `/data/:slug/v/:version` and `/models/:slug?version=` both carry a slug and a human-readable version, and the `/models/:slug` route entry has a comment explaining that even the `@` of an ID-3 ref was rejected because "an `@` must be percent-encoded by every client, and `family@7` then reads as `family%407` in every log and support conversation". A URL carrying two raw UUIDs is further from that standard than the form it rejected. This view cannot do better: `CompareModels.model_ids` is a tuple of UUIDs and no endpoint resolves a batch of slugs to ids. The consequence is a shared comparison URL that is opaque and does not survive being read aloud. Recording it because two conventions now disagree in the same app, and the next person to notice should find the reason already written down rather than "fix" it into a request the endpoint rejects.

- [ ] **Step 4: Open the PR**

```bash
git push -u origin plan/w6b-2-model-comparison
gh pr create --title "feat(w6b-2): the model comparison view" --body-file <the findings above>
```

---

## Self-review

**1. Spec coverage.** `02` §5.3's Contents cell has three items and each has a task: aligned metric table (Task 3), double-lift chart (Task 4), factor-by-factor relativity diff (Task 5). FR-186's four clauses — two or more models, a shared holdout, the three comparisons, a persisted artifact — are covered by Task 6's minimum-two guard, the rendered `split_ref`/`holdout_rows`, Tasks 3-5, and the `GET` by comparison id. §4.11's six rules each have a named test. NFR-463 is partly covered (the non-colour channel in Task 4) and partly **deferred to W6b-9 by the slice map**, stated in the file structure.

**2. Placeholders.** None. Every code step carries complete, runnable content; no "TBD", no "add error handling", no "similar to Task N". A draft of Task 5 carried a typo in the `groups` computed (`[...byFactor entries()]`) and it is corrected — a plan that ships a defect for the implementer to find teaches them to distrust the rest of it.

**3. Type consistency.** `parseModelRef` returns `{ slug, version }` and is consumed under those names in Task 2. `leaderState` returns the four-value union used in Task 3's `:class` and `v-if`. `comparisonIdFromJob` returns `string | null` and Task 6 branches on `=== null`. `startComparison` takes `readonly string[]` and Task 6 passes `string[]`, which is assignable. The panel props (`metrics`/`modelRefs`, `series`, `differences`/`modelRefs`) match the mocks in Task 6's test and the bindings in the view.

**4. What could still be wrong.** The `Progress` field name `stage` is read from the published contract, but nothing in this repository populates it for a `MODEL_COMPARE` job — the view renders an empty string in that case, which is the intended behaviour and not a defect. If `pnpm generate:api` produces `values` as a fixed-length tuple rather than an array, Task 3's `.find` still type-checks; if it produces `readonly` collections, the `[...rows].sort` in Task 5 is already a copy.
