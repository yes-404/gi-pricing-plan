---
id: PL-9574
family: plan
kind: leaf
title: WK-675 Slice 14 — Job detail, the /jobs/:id view with logs, cancel and error detail (FR-25, FR-399, FR-400, FR-401, FR-402, FR-403, NFR-528, NFR-463): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05
owner: planner
tree: 9489405370a1ce06c2b985ad88c7d471438febb1
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1286, PL-1371, FD-1284, FD-1335, PL-1364, RL-1263]
---

# PL 9574 (working id) — WK-675 Slice 14: Job detail, the `/jobs/:id` view, leaf plan

This plan is filed under working id 9574. Its `SL-` row under WK-675 in
[`../roadmap.md`](../roadmap.md) is slice working id 9575, `draft`, cut in the S4 leaf plan's
PR (PL 9582, working id) with the rows for S3, S13 and S14. The lead reserved all eight ids
(S4 = SL 9583 + PL 9582; S3 = SL 9581 + PL 9578; S13 = SL 9577 + PL 9576; S14 = SL 9575 + PL 9574)
and mints them at the merge turn. Written by the planner (planner-675) on the lead's brief of
2026-10-05 (`brief-prep-wave-2026-10-05.md`, section AW). Evidence was read at origin/main
`137bc817`, tree `94894053`, at 2026-10-05 17:05–17:35 BST.

**This plan builds on S13's plan, PL 9576 (working id, #1185), not on its code.** S13 is
unmerged at this writing. Every S13 symbol named below is quoted from PL 9576's *Interfaces*
blocks; Task 0 re-reads them from S13's merged code and stops on any difference.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds:
> - `test-driven-development`: every acceptance item is seen red, by its cause, before the
>   code that turns it green;
> - `vue-frontend` and `vue-best-practices`: Tasks 2–4;
> - `vue-router-best-practices`: Task 4;
> - `vue-testing-best-practices`: every test;
> - `dev-commands`: the pnpm install and the two-half gate;
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The
> executor is spawned from `.claude/roles/executor.md`.

## Goal

From a row of the Jobs list, an actuary opens `/jobs/:id` and sees one Job in full: its kind,
status, the submitter, the queued, started and finished times, its input parameters, its
progress (fraction, stage and counters), live while it runs; its captured log lines, each with
its `trace_id`; a link to its result where the result is addressable; the typed error of a
failed Job; and a **Cancel** action for a Job that has not finished.

**Architecture.** Frontend only; no backend change (`PL-1286` `:317`).
- `frontend/src/api/jobs.ts` gains `getJobLogs` and `cancelJob`;
- `frontend/src/jobResult.ts` (new) holds the result-link resolution. S13's backtest
  resolution moves here and gains `model:` and `dataset_version:`; `JobsView.vue` calls it;
- `frontend/src/views/JobDetailView.vue`, the `/jobs/:id` route, and a row link from
  `JobsView.vue`, which makes the route reachable (FR-25).

**Tech stack:** Vue 3 `<script setup lang="ts">`, vue-router, Tailwind, Vitest with
`@testing-library/vue`, the generated `components["schemas"]` types.

**Spec:** [`../specs/07-platform.md`](../specs/07-platform.md) §3.1 (FR-399–FR-403), §5.1
(the job routes, `07:306-310` at `137bc817`), §5.3 (the Job detail row, `07:399`), §9
(NFR-528); [`../specs/00-overview.md`](../specs/00-overview.md) FR-24, FR-25, NFR-463.

## The decisions this plan rests on, quoted

- **The view is WK-675's, as S14.** `FD-1284`: *"The maintainer ruled, by delegation: option D
  (split by view)."* `PL-1286` `:205-206`: *"They are bound by FR-402's UI limb ("viewable in
  the UI with the `trace_id`", `07:91`) and FR-401 (cancellation, `07:90`)."*
- **The map's row** (`PL-1286` `:317`), whose scope this plan does not change: *"Parameters,
  progress stages, logs with `trace_id` (FR-402's UI limb, `07:91`; `GET /jobs/{id}/logs`), the
  result link, the cancel action (FR-401, `POST /jobs/{id}/cancel`), error detail. The logs
  render nothing FR-402 excludes (no secrets, no full quote inputs) | S13"*. Its `07:391` cite
  for the view row is `07:399` at `137bc817`.
- **The routes S14 calls are typed.** In `docs/contracts/openapi/generated.json` at `137bc817`:
  `GET /api/v1/jobs/{job_id}` → `Job`; `GET …/logs` → `Page_JobLogLine_`;
  `POST …/cancel` → `Job`. `GET …/events` is `FD-1335`'s permanent exclusion
  (`text/event-stream`), which *"does not block WK-675"*.
- **The `07` §5.3 Job detail cell binds nothing by itself** (`00` FR-24; the cell at `07:399`
  declares no kind). What binds the view is the numbered requirements below and the map row.

## Status

`draft`. No open decision point blocks it. It stays `draft` until its **Activation needs**
are met in a separate activation PR.

### Activation needs, in order

1. **S13 merged** (SL 9577, PL 9576, working ids). S14 consumes `listJobs`, `streamJobEvents`,
   `JobStreamEvent`, `durationMs` and `JobsView.vue`: a plan dependency, so the two never run
   at once (`RL 9620` item 2 (b)).
2. **DP-S13-1's resolver read**: if it is (b), S14's single stream (Task 3) is still within it,
   since (b) concerns the list only; the lead confirms that reading in the dispatch record.
3. **The ids minted** (SL 9575, PL 9574) at this plan's merge turn.
4. **Task 0 re-run** at the dispatch tree.
5. **The maintainer's agreement**, as a dated line, and **the lead's go** in the activation PR,
   which sets this plan and its row `active`.

## Acceptance Standard

Every item is a command a fresh reviewer runs from the slice worktree after
`pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api`. Each
`vitest` item was seen red by its stated cause before its code landed; the ledger holds the
red output. A matching failure count with a different cause is a plan defect, not a pass.

1. `pnpm --dir frontend exec vitest run src/api/__tests__/jobs.test.ts` passes, and includes:
   `getJobLogs("j1", "c1")` requests `/api/v1/jobs/j1/logs?cursor=c1&limit=200` and returns the
   page unchanged; `cancelJob("j1")` sends `POST /api/v1/jobs/j1/cancel` and returns the `Job`;
   a 409 `JOB_NOT_CANCELLABLE` answer throws `ProblemError` with that code.
2. `pnpm --dir frontend exec vitest run src/__tests__/jobResult.test.ts` passes, and includes
   one case per row of *Choice 2*'s table: `backtest:`, `model:` and `dataset_version:`
   resolve to their named route; an unresolvable `backtest:` or `model:` gives the reason
   text; every other artifact ref, a `blob` and `none` give no link and the reference text.
3. `pnpm --dir frontend exec vitest run src/views/__tests__/JobDetailView.test.ts` passes, and
   includes: kind, status, submitter `display`, queued, started and finished times; each
   parameter key with its value; the progress fraction, stage and each counter (FR-400); the
   "Stalled" flag (NFR-528).
4. The same file: log lines render oldest first with `at`, `level`, `logger`, `message` and
   `trace_id` (FR-402); **Load more** passes `next_cursor` and appends; a `message` holding
   `<img src=x onerror=alert(1)>` renders as text and adds no element; a log line object
   carrying a property outside `JobLogLine`'s five renders nothing of it.
5. The same file: **Cancel** shows for `queued` and `running` and not for a terminal status;
   clicking it calls `cancelJob`; a `running` answer shows *"Cancellation requested. The Job
   stops at its next checkpoint."*; a `cancelled` answer replaces the Job; a
   `JOB_NOT_CANCELLABLE` refusal shows its `title` and `detail` in `role="alert"`.
6. The same file: a `failed` Job shows its `error.code`, `error.message`, whether it is
   retryable, and each `error.detail` key (FR-403).
7. The same file: a non-terminal Job opens exactly one `streamJobEvents` stream; a `progress`
   event updates the progress; a `done` event re-reads the Job with `getJob` and the logs' first
   page; unmount aborts the stream. A terminal Job opens none.
8. `pnpm --dir frontend exec vitest run src/views/__tests__/JobsView.test.ts` passes, including a
   case that each row links to `{"name":"job-detail","params":{"id":"<job id>"}}`, and S13's
   backtest cases unchanged.
9. `pnpm --dir frontend exec vitest run src/router/__tests__` passes: the reachability test
   reaches `/jobs/:id` with no new exception, and `/jobs/:id` resolves to `job-detail` with prop
   `id`. The reachability test was seen red after the route was added and before the row link.
10. `git diff --stat origin/main...HEAD` lists only the *Write set* paths, the ledger and
    `docs/INDEX.md`; `git diff origin/main...HEAD -- backend/ packages/ docs/contracts/` is
    empty; `git grep -n 'v-html' -- frontend/src/views/JobDetailView.vue` prints nothing.
11. The full gate, both halves (`CLAUDE.md` §11), green on the slice head, run by
    `gate-runner` as the only full gate on the box (`RL 9620` item 1), with its per-command
    table in the ledger.

## Global Constraints

- **Vue 3 Composition API with `<script setup lang="ts">` only**; never Options API, JSX or
  React (`CLAUDE.md` §3).
- **Never hand-write an API type** (`CLAUDE.md` §3). `Job`, `JobError`, `JobLogLine`,
  `Page_JobLogLine_`, `Progress`, `Model` and `DatasetVersion` come from
  `components["schemas"]`.
- **Log and parameter text is rendered by interpolation, never `v-html`.** A log message is
  data the platform captured; it is shown, never interpreted.
- **WCAG 2.2 AA** (`00` NFR-463): headings in order, the parameters and error detail as
  description lists, the logs as a captioned table, the Cancel button a real `<button>`, the
  live progress in a polite live region. No chart is added.
- **No test reaches the network** (`frontend/src/test-setup.ts`, F39).
- **At most one full gate on the box at a time**, and S13 and S14 never run at once
  (`RL-1263` as amended by `RL 9620`, #1162, read at `381254c3`).

## Scope

### Requirement coverage, each id individually

| Id | Clause, at `137bc817` | What S14 does with it |
|---|---|---|
| `00` FR-25 | *"A route the frontend registers is reachable from the application entry by following links alone."* | `/jobs/:id` linked from each `JobsView.vue` row (Acceptance 8, 9) |
| `07` FR-399 | *"…`queued_at`, `started_at`, `finished_at`, the submitting Principal, the Job Kind, its input parameters, and a result reference."* | every field shown; the result reference as a link or as text (Acceptance 2, 3) |
| `07` FR-400 | *"a fraction complete, a current-stage label, and optional counters"* | all three, live while running (Acceptance 3, 7) |
| `07` FR-401 | *"Jobs are **cancellable**. Cancellation is cooperative…"* | the Cancel action and its cooperative wording (Acceptance 5) |
| `07` FR-402 | *"Job logs are captured, retained with the Job, and viewable in the UI with the `trace_id` (R4). Logs never contain secrets or full quote inputs (R3, `06` FR-375)."* | the UI limb: the log lines with their `trace_id`; the view renders only `JobLogLine`'s five fields, as text (Acceptance 4). The exclusion itself is enforced where the line is captured (`backend/src/app/worker/logs.py:1-8`: *"Only the formatted message is stored"*), not in the view |
| `07` FR-403 | *"Failed Jobs record a typed error code, a human message, and — where the failure is deterministic … — the field-level cause."* | `JobError`'s code, message, retryable and detail shown (Acceptance 6) |
| `07` NFR-528 | *"…or the Job is treated as stalled and flagged."* | the flag (Acceptance 3) |
| `00` NFR-463 | WCAG 2.2 AA | Global Constraints; Task 3's markup |

### Task 0 at planning time (measured, not asserted)

At `137bc817`:
- `GET /api/v1/jobs/{job_id}/logs` pages oldest first by `seq`, `limit` 1–200, and returns
  `JobLogLine(at, level, logger, message, trace_id)` (`backend/src/app/api/jobs.py:172-230`).
- `POST /api/v1/jobs/{job_id}/cancel` needs `Perm.JOB_CANCEL` (`jobs.py:63`); a terminal Job
  answers 409 `JOB_NOT_CANCELLABLE` (`backend/src/app/platform/jobs.py:275-281`); a `running`
  Job is marked and answered still `running` (`jobs.py:240-245`).
- `Job` has no field recording a cancellation request (its properties in `generated.json`), so
  after a reload the view cannot show that one was made. Recorded, not worked around.
- `Progress` is one `{fraction, stage, counters}`; no stage history is stored or served.
- Result refs written by the handlers (`git grep -n 'JobResult(kind="artifact", ref=f"' -- backend/src/app`):
  `backtest:`, `dataset_version:` (two sites), `model:`, `model_comparison:`,
  `metric_certificate:`, `objective_certificate:`, `profile:`, `regression_run:`,
  `transparency:` (two sites), `validation_report:`; and `JobResult(kind="blob", …)` and
  `JobResult(kind="none")` elsewhere.
- `getVersionById` reads `/dataset-versions/{id}` (`frontend/src/api/versions.ts:43-45`);
  `DatasetVersion.slug` *"is the dataset's slug"*
  (`packages/model-schema/src/model_schema/datasets.py:339-340`).
- `score.batch` parameters are references (`dataset_version_id`, `rating_version_refs`,
  `table_name`, `chunk_rows`, `abort_failure_rate`; `backend/src/app/api/score.py:588-595`),
  and `score.trace_produce` carries `scoring_trace_id` (`score.py:518-524`): no quote input
  sits in a Job's parameters for either.
- `gh pr list --state open` at 17:09 BST: no open PR touches `frontend/`. S13's PR is #1185.

### Write set, by file and symbol

| Path | Change |
|---|---|
| `frontend/src/api/jobs.ts` | **add** `JobLogLine`, `JobLogPage`, `getJobLogs`, `cancelJob` |
| `frontend/src/jobResult.ts` | **new**: `ResultLink`, `resolveResultLink` |
| `frontend/src/views/JobDetailView.vue` | **new** |
| `frontend/src/views/JobsView.vue` (S13's) | **add** the row link; **replace** the inline backtest resolution with `resolveResultLink`; the backtest `RouterLink` literal stays |
| `frontend/src/router/index.ts` | **add** one record, `/jobs/:id`, name `job-detail` |
| `frontend/src/api/__tests__/jobs.test.ts`, `frontend/src/views/__tests__/JobsView.test.ts`, `frontend/src/router/__tests__/index.test.ts` | **add** cases |
| `frontend/src/__tests__/jobResult.test.ts`, `frontend/src/views/__tests__/JobDetailView.test.ts` | **new** |
| `docs/INDEX.md`, the slice's ledger | registry-exempt |

### Contention (`RL-1263`, `RL 9620`)

- **S13**: plan dependency (Activation need 1). Serial.
- **S4 (PL 9582)** and **S2 (PL 9713)**, working ids: each adds a different record to
  `router/index.ts`'s `routes`; S14 runs after both in `PL-1286`'s order. The second to merge
  rebases with merge-tree rc 0 and re-gates. S14 does not edit `App.vue`.
- **WK-690 Slice 5 (SL-1275)**: S14 adds functions and edits no poll helper (`PL-1286` `:409`).

### Size

1 / 2 days (likely / worst), `PL-1286` `:317`. Six tasks.

## Choices this plan makes

1. **"Progress stages" is FR-400's stage label, shown live.** The contract holds one current
   `Progress`, not a history, so the view shows the current stage and counters and updates them
   from the stream. It does not keep a client-side stage history, which would show a different
   list to two readers who opened the page at different times.
2. **The result link, by ref prefix.** A link where one existing read resolves the route;
   otherwise the reference text, so FR-399's "result reference" is always visible:

   | `result` | Resolution | Link |
   |---|---|---|
   | `artifact`, `backtest:<id>` | `getBacktest` → `model_id`; `listModels()` → `model_family_slug` (S13's Choice 3) | `{ name: 'model-backtest', params: { slug, backtestId } }` |
   | `artifact`, `model:<id>` | `listModels()` → the Model with that `id` | `{ name: 'model-detail', params: { slug: model_family_slug }, query: { version } }` |
   | `artifact`, `dataset_version:<id>` | `getVersionById(id)` → `slug`, `version` | `{ name: 'version-detail', params: { slug, version } }` |
   | any other `artifact` ref, `blob`, `none` | none | the text `Result: <kind> <ref>`, or `No result` for `none` |

   The other artifact refs need a second read or a route that does not exist yet
   (`regression_run:` is S11's). A slice that adds such a route adds its row here.
3. **Cancel needs no confirmation dialog.** Cancellation is cooperative and audited
   (`platform/jobs.py:283-296`), and it cannot be undone, but it destroys no artifact
   (`07` FR-401: *"A cancelled Job leaves no partially-visible artifact"*). The button's
   accessible name is *"Cancel this Job"*. The permission is checked by the server; a 403 is
   shown as the platform's problem, as every other refusal is.

## Decision points

None open. The lead may raise *Choice 2*'s table as a decision point at dispatch.

## Tasks

### Task 0: Preconditions (no code)

**Files:** the ledger only.

- [ ] **Step 1: Name the tree.** `git -C <wt> fetch origin && git -C <wt> rev-parse origin/main`;
  branch from it; record the SHA. Confirm S13 is merged (`git -C <wt> log --oneline origin/main -- frontend/src/views/JobsView.vue`
  prints its commit).
- [ ] **Step 2: Re-read S13's interfaces** from the merged code:
  `git -C <wt> grep -n 'export' -- frontend/src/api/jobs.ts frontend/src/api/client.ts`. They
  must include `listJobs`, `streamJobEvents`, `JobStreamEvent`, `durationMs`, `TERMINAL` and
  `streamEvents`. Read how `JobsView.vue` resolves the backtest link. Any difference from
  PL 9576's *Interfaces*: stop and report.
- [ ] **Step 3: Re-measure** each line under *Task 0 at planning time*; record the output.
- [ ] **Step 4: Contention.** `gh pr list --state open --json number,files` for any PR touching
  a *Write set* path; record it.
- [ ] **Step 5: Install.** `pnpm --dir frontend install --frozen-lockfile` and
  `pnpm --dir frontend generate:api`.

### Task 1: `getJobLogs` and `cancelJob`

**Files:** Modify `frontend/src/api/jobs.ts`; Test `frontend/src/api/__tests__/jobs.test.ts`.

**Interfaces:**
- Produces:
  - `export type JobLogLine = components["schemas"]["JobLogLine"];`
  - `export type JobLogPage = components["schemas"]["Page_JobLogLine_"];`
  - `export function getJobLogs(jobId: string, cursor?: string): Promise<JobLogPage>`: `request`
    with `query: { cursor, limit: PAGE_SIZE }` (`PAGE_SIZE` from `./paging`, the server's
    `MAX_LIMIT`);
  - `export function cancelJob(jobId: string): Promise<Job>`: `request<Job>(…/cancel, { method: "POST" })`.

- [ ] **Step 1: Write the failing tests** for Acceptance 1, stubbing `fetch` with the file's
  existing helper (S13 added it).
- [ ] **Step 2: Run red.** `pnpm --dir frontend exec vitest run src/api/__tests__/jobs.test.ts`
  fails because `getJobLogs` and `cancelJob` are not exported. Any other cause: stop.
- [ ] **Step 3: Implement.**

```ts
export type JobLogLine = components["schemas"]["JobLogLine"];
export type JobLogPage = components["schemas"]["Page_JobLogLine_"];

/** Oldest first, a page at a time (FR-402; the route orders by capture sequence). */
export function getJobLogs(jobId: string, cursor?: string): Promise<JobLogPage> {
  return request<JobLogPage>(`/jobs/${encodeURIComponent(jobId)}/logs`, {
    query: { cursor, limit: PAGE_SIZE },
  });
}

/**
 * Ask a Job to stop (FR-401). Cooperative: a `running` Job is answered still `running` and
 * stops at its next checkpoint; a finished one is refused 409 `JOB_NOT_CANCELLABLE`.
 */
export function cancelJob(jobId: string): Promise<Job> {
  return request<Job>(`/jobs/${encodeURIComponent(jobId)}/cancel`, { method: "POST" });
}
```

- [ ] **Step 4: Run green. Step 5: Commit** `feat(frontend): getJobLogs and cancelJob (WK-675 S14)`.

### Task 2: `jobResult.ts`

**Files:** Create `frontend/src/jobResult.ts`, `frontend/src/__tests__/jobResult.test.ts`;
Modify `frontend/src/views/JobsView.vue`.

**Interfaces:**
- Consumes: `getBacktest` (`@/api/backtests`), `listModels` (`@/api/models`),
  `getVersionById` (`@/api/versions`), `Job` (`@/api/jobs`).
- Produces:

```ts
import type { RouteLocationRaw } from "vue-router";

export type ResultLink =
  | { readonly kind: "link"; readonly to: RouteLocationRaw; readonly label: string }
  | { readonly kind: "text"; readonly text: string };

export function resolveResultLink(job: Job): Promise<ResultLink>;
```

- [ ] **Step 1: Write the failing tests**, one per row of *Choice 2*'s table, plus: a
  `backtest:` whose model is absent from a `truncated` list gives text containing *"not in the
  first 1000 models listed"*, the wording S13 shipped (read it from `JobsView.vue` at Task 0
  and use it verbatim); a Job with `result: null` gives `{ kind: "text", text: "No result" }`.
  Mock the three API modules with `vi.mock`.
- [ ] **Step 2: Run red.** `pnpm --dir frontend exec vitest run src/__tests__/jobResult.test.ts`
  fails because `@/jobResult` does not exist.
- [ ] **Step 3: Implement** the table: split `result.ref` at the first `:`; switch on the prefix;
  for `backtest:` move S13's resolution here unchanged in behaviour. Labels: *"Open backtest"*,
  *"Open model"*, *"Open dataset version"*. `listModels()` is called at most once per
  `resolveResultLink` call.
- [ ] **Step 4: Point `JobsView.vue` at it.** Replace S13's inline backtest resolution with a call
  to `resolveResultLink` for each succeeded row, and render a `kind: "link"` result for a
  `backtest:` ref with S13's **literal** named-route `RouterLink` (it stays, because
  `routeGraph.ts` counts only literals, `routeGraph.ts:61`), and other links with
  `<RouterLink :to="link.to">`.
- [ ] **Step 5: Run green**: `jobResult.test.ts`, then `JobsView.test.ts` (S13's backtest cases
  unchanged) and `src/router/__tests__/reachability.test.ts`. **Step 6: Commit**
  `refactor(frontend): the job result link resolved in one place, with model and dataset version (WK-675 S14)`.

### Task 3: `JobDetailView.vue`

**Files:** Create `frontend/src/views/JobDetailView.vue`,
`frontend/src/views/__tests__/JobDetailView.test.ts`.

**Interfaces:**
- Props: `{ id: string }`.
- Consumes: `getJob`, `getJobLogs`, `cancelJob`, `streamJobEvents`, `durationMs`, `TERMINAL`
  (`@/api/jobs`); `resolveResultLink` (`@/jobResult`); `ProblemError` (`@/api/problem`).

- [ ] **Step 1: Write the failing tests** for Acceptance 3–7. Mock `@/api/jobs` and
  `@/jobResult` as `ModelListView.test.ts:8-13` mocks its module, keeping `TERMINAL` and
  `durationMs` real. Use an annotated `Job` factory with the eight required fields (`id`,
  `workspace_id`, `kind`, `status`, `queue`, `submitted_by`, `source`, `queued_at`). For the
  out-of-contract log property, build the line as
  `{ ...line, secret_field: "s3cr3t" } as JobLogLine` and assert `queryByText("s3cr3t")` is
  null. For the markup case assert `container.querySelector("img")` is null and the message
  text is present.
- [ ] **Step 2: Run red.** `pnpm --dir frontend exec vitest run src/views/__tests__/JobDetailView.test.ts`
  fails because `../JobDetailView.vue` does not exist; then, with a skeleton that renders only
  the heading, each case fails on its own assertion. Record each.
- [ ] **Step 3: Implement.**
  - On mount: `getJob(id)`, `getJobLogs(id)`, `resolveResultLink(job)` when the Job has a
    `result`; if the status is not in `TERMINAL`, open one `streamJobEvents(id, signal)`.
    A `progress` event sets `status`, `progress`, `trace_id`, and `stalled = false` when
    `progress` changed. A `done` event re-reads `getJob(id)` and the logs' first page, then
    resolves the result. `onBeforeUnmount` aborts the stream.
  - Header: `<h1>` with the kind; status, with *"Stalled"* when `job.stalled`; submitter
    `submitted_by.display`; `queued_at`, `started_at`, `finished_at`; duration from
    `durationMs(job, Date.now())`; the Job's `trace_id`.
  - **Parameters:** a `<dl>`, one `<dt>`/`<dd>` per key of `job.parameters`; a non-string value
    rendered as `JSON.stringify(value)`; interpolated, never `v-html`.
  - **Progress:** `<progress :value="job.progress?.fraction ?? 0" max="1">` labelled with the
    percentage and stage; the counters as a `<dl>`; the region `aria-live="polite"`.
  - **Result:** `ResultLink` rendered as a `RouterLink` or as text.
  - **Error** (`job.error` present): code, message, *"Retryable"* or *"Not retryable"*, and a
    `<dl>` of `error.detail`.
  - **Logs:** a `<table>` with `<caption>Log</caption>`, columns Time, Level, Logger, Message,
    Trace id, one row per line, each cell `{{ line.at }}` and so on for exactly those five
    fields. **Load more** while `next_cursor` is set.
  - **Cancel:** a `<button>` *"Cancel this Job"*, shown while the status is not in `TERMINAL`.
    On click: `cancelJob(id)`; replace the Job with the answer; if the answer is still
    `running`, show *"Cancellation requested. The Job stops at its next checkpoint."* A
    `ProblemError` shows `title` and `detail` in `role="alert"`.
- [ ] **Step 4: Run green. Step 5: Commit**
  `feat(frontend): the Job detail view — parameters, progress, logs with trace_id, result, cancel, error (WK-675 S14)`.

### Task 4: The route and the link from the list

**Files:** Modify `frontend/src/router/index.ts`, `frontend/src/views/JobsView.vue`,
`frontend/src/views/__tests__/JobsView.test.ts`, `frontend/src/router/__tests__/index.test.ts`.

- [ ] **Step 1: Add the route first, and see red.** After S13's `/jobs` record, in the form
  `routeGraph.ts`'s `RECORD` parses (`path` first, `name` second):

```ts
  {
    // `07` §5.3 Job detail (`07:399`); WK-675 S14 (FD-1284 option D).
    path: "/jobs/:id",
    name: "job-detail",
    meta: { requiresAuth: true },
    component: () => import("@/views/JobDetailView.vue"),
    props: (route) => ({ id: String(route.params.id) }),
  },
```

  Run `pnpm --dir frontend exec vitest run src/router/__tests__/reachability.test.ts`. Expected:
  *"names every route with no inbound path from the entry"* fails with `["/jobs/:id"]`. Record
  it.
- [ ] **Step 2: Add the row link** in `JobsView.vue`: the kind cell becomes
  `<RouterLink :to="{ name: 'job-detail', params: { id: job.id } }">` on one line, with single
  quotes, so `routeGraph.ts:61` counts it. Add the `JobsView.test.ts` case (Acceptance 8).
- [ ] **Step 3: Add the resolution case** to `index.test.ts`: `/jobs/0193…` resolves to
  `job-detail`, mirroring that file's `router().resolve(…)` cases (`:36`, `:51`).
- [ ] **Step 4: Run green**: `pnpm --dir frontend exec vitest run src/router/__tests__ src/views/__tests__/JobsView.test.ts`.
  **Step 5: Commit** `feat(frontend): /jobs/:id route, linked from the Jobs list (WK-675 S14)`.

### Task 5: Type-check, lint and build

- [ ] `pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend build`;
  each rc 0. Record the chunk table: `JobDetailView-*.js` is a new lazy chunk; report the
  shared `index-*.js` delta, before → after, raw and gzip.

### Task 6: The gate and the ledger

- [ ] **Step 1: The full gate, both halves** (`CLAUDE.md` §11), delegated to `gate-runner`, as the
  only full gate on the box (`RL 9620` item 1). Announce it first (`delivery-process.md` §8).
- [ ] **Step 2: Self-check Acceptance 1–11**, pasting each output into the ledger.
- [ ] **Step 3: Open the PR**, naming the range `origin/main...HEAD` and the bundle delta.

## Hand-off

- **To S5, S8 and S11:** a view that starts a Job links to `{ name: 'job-detail', params: { id } }`
  rather than building its own progress display (`PL-1286` `:372-375`). A slice that adds a
  route for a result kind (S11: `regression_run:`) adds its row to `jobResult.ts`.
- **To the auditor at slice close:** two recorded gaps, neither against a numbered requirement:
  the view cannot show a pending cancellation after a reload (no field in `Job`), and *Choice
  2*'s text-only refs.

## Self-review

- **Spec coverage.** FR-25, FR-399, FR-400, FR-401, FR-402, FR-403, NFR-528 and NFR-463 each
  map to an Acceptance item. FR-402's exclusion clause is placed where it is enforced (capture),
  and the view's share of it (render only the five fields, as text) is tested.
- **Literals verified at `137bc817`:** the routes, permission, refusal code and cancel
  behaviour (`api/jobs.py:63`, `:172-245`; `platform/jobs.py:262-296`); `JobLogLine`'s fields,
  `Job`'s required fields, `JobError`, `Progress` (`generated.json`); the result-ref prefixes
  (the `git grep` under *Task 0*); `getVersionById` (`versions.ts:43-45`); `DatasetVersion.slug`
  (`datasets.py:339-340`); the route names `model-backtest`, `model-detail` and
  `version-detail` (`router/index.ts:116`, `:219`, `:55`); `PAGE_SIZE` (`paging.ts:18`);
  `RECORD` and the named-route form (`routeGraph.ts:28-29`, `:61`).
  **Not verified, because S13 is unmerged:** S13's symbols and wording. Task 0 Step 2 re-reads
  them and stops on a difference.
- **Placeholders:** none.
- **Rulings re-checked before the PR:** open PRs at 17:09 BST, none touching `frontend/` or
  ruling on the Jobs views besides S13's #1185. `RL 9620` read at `381254c3` (#1162, unmerged).
