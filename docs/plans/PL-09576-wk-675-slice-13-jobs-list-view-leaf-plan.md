---
id: PL-9576
family: plan
kind: leaf
title: WK-675 Slice 13 — Jobs, the /jobs list view, live over the event stream (FR-25, FR-399, FR-400, NFR-528, NFR-463): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05
owner: planner
tree: 9489405370a1ce06c2b985ad88c7d471438febb1
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1286, PL-1371, FD-1284, FD-1335, PL-1364, SL-1367, RL-1263, PL-1368, SL-1369, PL-9713, PL-9582, PL-9574]
---

# PL 9576 (working id) — WK-675 Slice 13: Jobs, the `/jobs` list view, leaf plan

This plan is filed under working id 9576. Its `SL-` row under WK-675 in
[`../roadmap.md`](../roadmap.md) is slice working id 9577, `draft`, cut in the S4 leaf plan's
PR (PL 9582, working id) with the rows for S3, S13 and S14. The lead reserved all eight ids
(S4 = SL 9583 + PL 9582; S3 = SL 9581 + PL 9578; S13 = SL 9577 + PL 9576; S14 = SL 9575 + PL 9574)
and mints them at the merge turn. Written by the planner (planner-675) on the lead's brief of
2026-10-05 (`brief-prep-wave-2026-10-05.md`, section AW). Evidence was read at origin/main
`137bc817`, tree `94894053`, at 2026-10-05 17:05–17:20 BST.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds:
> - `test-driven-development`: every acceptance item is seen red, by its cause, before the
>   code that turns it green;
> - `vue-frontend` and `vue-best-practices`: Tasks 2–5;
> - `vue-router-best-practices`: Task 4;
> - `vue-testing-best-practices`: every test;
> - `dev-commands`: the pnpm install and the two-half gate;
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The
> executor is spawned from `.claude/roles/executor.md`.

## Goal

An actuary opens **Jobs** from the application's navigation and sees the workspace's Jobs,
newest first: kind, status, a progress bar with the current stage, the submitter and the
duration. A stalled Job is flagged. The list filters by status and kind and pages by cursor.
Running Jobs on the visible page update live over `GET /api/v1/jobs/{id}/events`. A succeeded
`model.backtest` Job links to its backtest, so `/models/:slug/backtests/:backtestId` becomes
reachable by links and leaves `reachability.test.ts`'s exception list.

**Architecture.** Frontend only; no backend change (`PL-1286` `:316`). Three layers:
- `frontend/src/api/client.ts` gains one export, `streamEvents`, a `fetch`-based reader for
  `text/event-stream` that sends the same `Authorization` and `Workspace-Id` headers as
  `request` (Choice 1);
- `frontend/src/api/jobs.ts` gains `listJobs`, `streamJobEvents`, `JOB_KINDS`,
  `JOB_STATUSES` and `durationMs`; `getJob` and `waitForJob` are not edited;
- `frontend/src/views/JobsView.vue`, the `/jobs` route, and a navigation link in `App.vue`.

**Tech stack:** Vue 3 `<script setup lang="ts">`, vue-router, Tailwind, Vitest with
`@testing-library/vue`, the generated `components["schemas"]` types.

**Spec:** [`../specs/07-platform.md`](../specs/07-platform.md) §3.1 (FR-399, FR-400), §5.1
(the job routes, `07:306-310` at `137bc817`), §5.3 (the Jobs row, `07:398`), §9 (NFR-528);
[`../specs/00-overview.md`](../specs/00-overview.md) FR-24, FR-25, NFR-463 and §5.6 (`00:423`).

## The decisions this plan rests on, quoted

- **The view is WK-675's, as S13.** `FD-1284`, *"The maintainer ruled, by delegation: option D
  (split by view)."*; `PL-1286` `:202-207`: *"**Jobs** (`/jobs`, `07:390`) and **Job detail**
  (`/jobs/:id`, `07:391`) are **WK-675's**, as **S13** and **S14** (appended). No spec change is
  needed: every route is declared (`07:301-305`) and built."* Those `07` line numbers have
  moved: at `137bc817` the routes are `07:306-310` and the view rows `07:398-399`.
- **The map's row** (`PL-1286` `:316`), whose scope this plan does not change: *"The filterable
  list with kind, status, progress bars, submitter and duration, live over the SSE stream
  (`GET /api/v1/jobs` and `/jobs/{id}/events`, `07:301, 305`); FR-25 link from the entry;
  **removes the `reachability.test.ts` exception** for `/models/:slug/backtests/:backtestId`
  (reachable through a Job's result link) and **corrects its FR-24 comment** (`:33`). New
  functions in `frontend/src/api/jobs.ts`; no backend change | S4 (order: before S5, the first
  slice that renders a Job)"*.
- **The event stream is not a hold.** `FD-1335` lists `GET /api/v1/jobs/{job_id}/events` as one
  of *"the four permanent exclusions"* (`text/event-stream`, `backend/src/app/api/jobs.py:308-310`),
  and of its media-type sub-item: *"it does not block WK-675."* `PL-1364` `:739` records S13 and
  S14 against it as *"no conflict"*.
- **The `07` §5.3 Jobs cell binds nothing by itself.** `00` FR-24: *"A Contents cell in a module
  spec's §5.3 Frontend views table is prose and binds nothing"*; the Jobs cell (`07:398`)
  declares no kind. What binds the view is the numbered requirements below and the map row's
  scope, which the maintainer accepted with `PL-1286`.

## Status

`draft`. One decision point is open and blocks activation (DP-S13-1). The plan stays
`draft` until its **Activation needs** are met in a separate activation PR.

### Activation needs, in order

1. **DP-S13-1 has a resolver**: the decision-maker's ruling, or the maintainer's line.
2. **The order holds.** `PL-1286` places S13 after S4 (SL 9583, working id). That is order,
   not dependency: S13 consumes nothing S4 builds (`PL-1286` `:372-375`, *"No dependency
   forces this"*). If the lead runs S13 beside S4, the dispatch record shows `RL 9620`'s two
   conditions (see *Write set, and its contention*).
3. **The ids minted** (SL 9577, PL 9576) at this plan's merge turn.
4. **Task 0 re-run** at the dispatch tree.
5. **The maintainer's agreement**, as a dated line, and **the lead's go** in the activation PR,
   which sets this plan and its row `active`.

## Acceptance Standard

Every item is a command a fresh reviewer runs from the slice worktree after
`pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api`. Each
`vitest` item was seen red by its stated cause before its code landed; the ledger holds the
red output. A matching failure count with a different cause is a plan defect, not a pass.

1. `pnpm --dir frontend exec vitest run src/api/__tests__/jobs.test.ts` passes, and includes:
   `listJobs` sends `status`, `kind`, `cursor` and `limit` as query parameters and omits each
   that is undefined; it returns the page's `items`, `next_cursor` and `total_estimate`
   unchanged.
2. `pnpm --dir frontend exec vitest run src/api/__tests__/client.test.ts` passes, and includes
   four `streamEvents` cases: it sends `Accept: text/event-stream`, `Authorization` and
   `Workspace-Id`; it parses two frames split across three chunks at arbitrary byte positions;
   a non-2xx answer throws `ProblemError` carrying the platform's `code`; an aborted signal
   ends the iteration without an error.
3. The same `jobs.test.ts` shows `streamJobEvents` yielding `progress` events as
   `JobStreamEvent` objects and returning after the first `done` event.
4. `pnpm --dir frontend exec vitest run src/views/__tests__/JobsView.test.ts` passes, and
   includes: one row per Job with kind, status, submitter `display`, duration, and a
   `<progress>` whose accessible text names the fraction and the stage (FR-400); a `stalled`
   Job shows the flag text "Stalled" (NFR-528); changing the status or kind filter re-reads
   page one with that filter; **Load more** passes `next_cursor` and appends.
5. The same file shows the live behaviour DP-S13-1 rules. Under recommendation (a): at most
   four streams are open at once, for the newest non-terminal rows; a `progress` event updates
   that row only; a `done` event re-reads the current filter's first page; every stream's
   signal is aborted on unmount.
6. The same file shows a succeeded `model.backtest` Job with `result.ref` `backtest:<id>`
   rendering a link to the route named `model-backtest` with the model's `model_family_slug`;
   when the slug cannot be resolved, the row states why and renders no link.
7. `pnpm --dir frontend exec vitest run src/router/__tests__/reachability.test.ts` passes, and
   `git grep -n 'backtests/:backtestId' -- frontend/src/router/__tests__/reachability.test.ts`
   prints nothing. The test was seen red after the exception was removed and before the link
   landed, naming `/models/:slug/backtests/:backtestId` as unreachable.
8. `git grep -n 'later phase (FR-24)' -- frontend/` prints nothing.
9. `pnpm --dir frontend exec vitest run --typecheck.only src/api/__tests__/jobs.test-d.ts`
   passes: `JOB_KINDS` and `JOB_STATUSES` equal the generated `JobKind` and `JobStatus` unions
   in both directions. It was seen red with one member removed from each array.
10. `pnpm --dir frontend exec vitest run src/router/__tests__` passes, including a resolution
    test that `/jobs` resolves to the route named `jobs`.
11. `git diff --stat origin/main...HEAD` lists only the *Write set* paths, the ledger and
    `docs/INDEX.md`; `git diff origin/main...HEAD -- backend/ packages/ docs/contracts/` is
    empty.
12. The full gate, both halves (`CLAUDE.md` §11), green on the slice head, run by `gate-runner`
    as the only full gate on the box (`RL 9620` item 1), with its per-command table in the
    ledger.

## Global Constraints

- **Vue 3 Composition API with `<script setup lang="ts">` only**; never Options API, JSX or
  React (`CLAUDE.md` §3).
- **Never hand-write an API type** (`CLAUDE.md` §3). `Job`, `JobStatus`, `JobKind`,
  `JobLogLine` and `Page_Job_` come from `components["schemas"]`. The stream event is
  `Pick<Job, "id" | "status" | "progress" | "trace_id">`, the four keys the handler writes
  (`backend/src/app/api/jobs.py:288-296`), not a new shape.
- **No hand-written copy of a contract enum that is not checked against it.** `JOB_KINDS` and
  `JOB_STATUSES` are `as const satisfies readonly …[]` and a `.test-d.ts` checks equality both
  ways (precedent: `frontend/src/components/__tests__/objectiveVocabulary.test-d.ts`).
- **WCAG 2.2 AA** (`00` NFR-463). The progress bar is a native `<progress>`, labelled; the
  table has a caption and column headers; the filters are labelled controls. No chart is
  added, so NFR-463's tabular-equivalent clause has no site here.
- **No test reaches the network.** `frontend/src/test-setup.ts` rejects an unstubbed `fetch`
  (F39, `SL-1369`); every test stubs it or mocks the API module.
- **One slice at a time within the Work unless `RL 9620`'s two conditions are recorded; at
  most one full gate on the box at a time** (`RL-1263` as amended by `RL 9620`, #1162, item 1,
  read at `381254c3`). Executors' single-file test runs stay outside the gate window.

## Scope

### Requirement coverage, each id individually

| Id | Clause, at `137bc817` | What S13 does with it |
|---|---|---|
| `00` FR-25 | *"A route the frontend registers is reachable from the application entry by following links alone."* | the `/jobs` link in `App.vue`; the backtest route made reachable and its exception removed (Acceptance 7, 10) |
| `00` FR-24 | the §5.3 Contents-cell rule | cited, not implemented: the `reachability.test.ts:33` comment that mis-cites it is corrected (Acceptance 8) |
| `07` FR-399 | *"…`queued_at`, `started_at`, `finished_at`, the submitting Principal, the Job Kind, its input parameters, and a result reference."* | the list's kind, status, submitter and duration columns; the result reference for `backtest:` (Acceptance 4, 6). Parameters are S14's |
| `07` FR-400 | *"Jobs report **structured progress**: a fraction complete, a current-stage label, and optional counters"* | the fraction and stage in the row's `<progress>` (Acceptance 4). Counters are S14's |
| `07` NFR-528 | *"Progress updates arrive at least every 5 s for a running Job, or the Job is treated as stalled and flagged."* | the flag (Acceptance 4). Its derivation stays server-side (`07:219-223`) |
| `00` NFR-463 | WCAG 2.2 AA | Global Constraints; Task 3's markup |

FR-401 (cancel), FR-402 (logs with `trace_id`) and FR-403 (error detail) are S14's (PL 9574,
working id).

### Task 0 at planning time (measured, not asserted)

At `137bc817`:
- `git grep -n 'path: "/jobs' -- frontend/src/router/index.ts` prints nothing: no `/jobs`
  route exists.
- `frontend/src/api/jobs.ts` is 38 lines: `Job`, `JobStatus`, `TERMINAL`, `getJob`,
  `waitForJob`. Its consumers: `ModelComparisonView.vue`, `components/RuleBuilder.vue`,
  `api/__tests__/comparisons.test.ts`.
- `reachability.test.ts:22-40`: the exception list holds `/callback`, `/silent-renew` and
  `/models/:slug/backtests/:backtestId`; the comment at `:30-35` says *"The jobs view is a later
  phase (FR-24)."*
- The generated OpenAPI (`docs/contracts/openapi/generated.json`) types `GET /api/v1/jobs` as
  `Page_Job_`, and `GET /api/v1/jobs/{job_id}` and `POST /api/v1/jobs/{job_id}/cancel` as
  `Job`, `…/logs` as `Page_JobLogLine_`. `…/events` documents `application/json` with an empty
  schema: `FD-1335`'s permanent exclusion, quoted above.
- `GET /api/v1/jobs` takes `status`, `kind`, `submitted_by`, `cursor`, `limit`
  (`backend/src/app/api/jobs.py:105-115`); `DEFAULT_LIMIT` 50, `MAX_LIMIT` 200
  (`backend/src/app/api/pagination.py:37-38`); order `JobRow.id.desc()` (`jobs.py:131`).
- The event payload is `{"id", "status", "progress", "trace_id"}`, sent as `event: progress`
  on change and `event: done` at a terminal status (`jobs.py:288-305`).
- The backtest Job's result is `JobResult(kind="artifact", ref=f"backtest:{backtest_id}")`
  (`backend/src/app/worker/model_handlers.py:1325`). `Backtest` carries `model_id`, not a slug;
  `GET /api/v1/models/{slug}` resolves by slug only (`backend/src/app/api/models.py:632-652`).
- `gh pr list --state open` at 17:09 BST: no open PR touches `frontend/`.

### Write set, by file and symbol, at `137bc817`

| Path | Change |
|---|---|
| `frontend/src/api/client.ts` | **add** `streamEvents` and its `ServerEvent` interface; no existing symbol edited |
| `frontend/src/api/jobs.ts` | **add** `JobKind`, `JobPage`, `JobStreamEvent`, `JOB_KINDS`, `JOB_STATUSES`, `listJobs`, `streamJobEvents`, `durationMs`; `getJob`, `waitForJob`, `TERMINAL` unchanged |
| `frontend/src/views/JobsView.vue` | **new** |
| `frontend/src/router/index.ts` | **add** one `routes` record, `/jobs`, name `jobs` |
| `frontend/src/App.vue` | **add** one `RouterLink` to `/jobs` |
| `frontend/src/router/__tests__/reachability.test.ts` | **remove** one exception and correct its comment (`:30-40`) |
| `frontend/src/api/__tests__/client.test.ts` | **add** the `streamEvents` cases |
| `frontend/src/api/__tests__/jobs.test.ts`, `frontend/src/api/__tests__/jobs.test-d.ts`, `frontend/src/views/__tests__/JobsView.test.ts` | **new** |
| `frontend/src/router/__tests__/index.test.ts` | **add** the `/jobs` resolution case |
| `docs/INDEX.md`, the slice's ledger | registry-exempt |

### Write set, and its contention (`RL-1263`, `RL 9620`)

- **S2 (SL 9711, PL 9713, working ids)** adds a route (`/rating/:slug/v/:version/design`) to
  `frontend/src/router/index.ts` and a link in `RatingVersionView.vue`. S13 adds a different
  record to the same `routes` array. Not exempt; ordered (S2 precedes S13 in `PL-1286`), and the
  second to merge rebases with merge-tree rc 0 and re-gates.
- **S4 (SL 9583, PL 9582, working ids)**: its route and `App.vue` hunks are the lead's to compare
  at dispatch from PL 9582's write set. If both slices add a `RouterLink` in `App.vue`'s `nav`,
  the hunks are adjacent and the pair **serialises**. Under `RL 9620` item 2 the pair may run at
  once only when the dispatch record shows (a) the file sets resolved and (b) no plan dependency
  either way. (b) holds on S13's side: S13 consumes nothing S4 builds, and S4 consumes nothing
  S13 builds.
- **S14 (SL 9575, PL 9574)** consumes S13's `jobs.ts` additions and edits `JobsView.vue`: a
  plan dependency, so S13 and S14 never run at once.
- **WK-690 Slice 5 (SL-1275)**: `PL-1286` `:409` serialises only an edit to the poll helper.
  S13 adds functions and does not edit `waitForJob`: no conflict.
- **`client.ts`**: no open PR touches it at 17:09 BST. Re-read at Task 0.

### Size

1 / 2 days (likely / worst), `PL-1286` `:316`. Six tasks.

## Choices this plan makes

1. **A `fetch` reader, not `EventSource`.** The platform authenticates with a bearer token
   (`client.ts:19-23`, `07` FR-393) and selects the workspace with a `Workspace-Id` header
   (`client.ts:29-35`, FR-397). `EventSource` cannot send either header, so a browser
   `EventSource` on `/jobs/{id}/events` is refused before it streams. The reader lives in
   `client.ts`, beside `request`, because the headers are that module's private state, and a
   second copy of them would be a second copy of the auth convention.
2. **The submitter filter is not offered.** `submitted_by` takes a Principal UUID
   (`jobs.py:112`), and the frontend has no source for the signed-in Principal's id at
   `137bc817` (`frontend/src/api/me.ts` exports only workspace functions). The column shows
   `submitted_by.display`. The Jobs cell is prose under FR-24; S13 records this rather than
   adding a backend read.
3. **The backtest link resolves the slug on the client.** `getBacktest(id)` gives `model_id`;
   `listModels()` (`frontend/src/api/models.ts:49-51`, capped at `MODEL_PAGE_CAP` = 5 pages)
   gives the model whose `id` matches, and its `model_family_slug`. If the list is `truncated`
   and holds no match, or the Model is absent, the row says *"Backtest saved; its model is not
   in the first 1000 models listed"* or *"Backtest saved; its model was not found"*, and shows
   no link. No backend change (`PL-1286` `:316`). Resolution runs only for succeeded
   `model.backtest` rows on the visible page, once per row, and `listModels()` is called at
   most once per page render.
4. **The link is a named-route object in `JobsView.vue` itself.** `routeGraph.ts` reads a
   route's own view file and the shell, not child components (`reachability.test.ts:47-60`),
   and counts a named-route object only in the form `{ name: '…'` with single quotes
   (`routeGraph.ts:61`). A computed `:to` carries no edge (`routeGraph.ts:7-8`).

## Decision points

| DP | Question | Options | Recommendation | Blocks |
|---|---|---|---|---|
| **DP-S13-1** | How many event streams does the list hold open? The backend polls one row per stream per second (`jobs.py:254-300`); a browser on HTTP/1.1 holds at most six connections to one origin, so a stream per running row on a 50-row page can starve every other request. | **(a)** At most **4** streams, for the newest non-terminal rows on the visible page. A `done` event re-reads the current filter's first page, which brings in the next running rows. Rows without a stream show their state as of the last read. **(b)** No streams in the list: re-read the page every 5 s while any row is non-terminal. Simpler, but the map row says *"live over the SSE stream"*, so (b) is a change to `PL-1286`'s scope and is the maintainer's. **(c)** One stream per non-terminal row, unbounded. | **(a)**: it keeps the map's scope, bounds the connections, and leaves two for the page's own requests. | activation |

## Tasks

### Task 0: Preconditions (no code)

**Files:** the ledger only.

- [ ] **Step 1: Name the tree.** `git -C <wt> fetch origin && git -C <wt> rev-parse origin/main`.
  Branch from it and record the SHA.
- [ ] **Step 2: Re-measure.** Re-run each command under *Task 0 at planning time* and record the
  output. If `/jobs` now exists, or the exception list differs, stop and report to the lead.
- [ ] **Step 3: Read DP-S13-1's resolver** and record it. Tasks 3 and Acceptance 5 follow it.
  If it is (b), the stream functions in Task 1 and 2 are still built (S14 uses them).
- [ ] **Step 4: Re-read the contention.** `gh pr list --state open --json number,files` for any
  PR touching a *Write set* path; record it.
- [ ] **Step 5: Install.** `pnpm --dir frontend install --frozen-lockfile` and
  `pnpm --dir frontend generate:api`.

### Task 1: `streamEvents` in `client.ts`

**Files:**
- Modify: `frontend/src/api/client.ts` (append after `request`)
- Test: `frontend/src/api/__tests__/client.test.ts`

**Interfaces:**
- Produces: `export interface ServerEvent { event: string; data: string }` and
  `export async function* streamEvents(path: string, options?: { signal?: AbortSignal }): AsyncGenerator<ServerEvent>`.

- [ ] **Step 1: Write the failing tests.** Append to `client.test.ts`:

```ts
function streamOf(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(encoder.encode(chunk));
      controller.close();
    },
  });
}

describe("streamEvents", () => {
  it("sends the stream, auth and workspace headers", async () => {
    const fetchMock = vi.fn(async () => new Response(streamOf([]), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    setAccessToken("tok");
    setWorkspaceId("ws-1");
    for await (const _ of streamEvents("/jobs/j1/events")) void _;
    const init = fetchMock.mock.calls[0]![1] as RequestInit;
    expect(init.headers).toMatchObject({
      Accept: "text/event-stream",
      Authorization: "Bearer tok",
      "Workspace-Id": "ws-1",
    });
  });

  it("parses frames split across chunks", async () => {
    const body = streamOf([
      "event: progress\nda",
      'ta: {"a":1}\n\nevent: do',
      'ne\ndata: {"a":2}\n\n',
    ]);
    vi.stubGlobal("fetch", vi.fn(async () => new Response(body, { status: 200 })));
    const seen = [];
    for await (const frame of streamEvents("/jobs/j1/events")) seen.push(frame);
    expect(seen).toEqual([
      { event: "progress", data: '{"a":1}' },
      { event: "done", data: '{"a":2}' },
    ]);
  });

  it("throws the platform's problem on a refusal", async () => {
    respond(404, { title: "Job not found", status: 404, code: "NOT_FOUND", errors: [] });
    const failure = await (async () => {
      for await (const _ of streamEvents("/jobs/j1/events")) void _;
    })().catch((error: unknown) => error);
    expect(isProblem(failure, "NOT_FOUND")).toBe(true);
  });

  it("ends without an error when its signal aborts", async () => {
    const controller = new AbortController();
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        controller.abort();
        throw new DOMException("aborted", "AbortError");
      }),
    );
    const seen = [];
    for await (const frame of streamEvents("/jobs/j1/events", { signal: controller.signal }))
      seen.push(frame);
    expect(seen).toEqual([]);
  });
});
```

  Add `streamEvents` to the file's import from `"../client"`.
- [ ] **Step 2: Run, and see each red by its cause.**
  `pnpm --dir frontend exec vitest run src/api/__tests__/client.test.ts`. Expected: the four new
  cases fail because `streamEvents` is not exported (a `TypeError: streamEvents is not a
  function`, or the type-check equivalent). Any other cause is a plan defect: stop and report.
- [ ] **Step 3: Implement.** Refactor the header-building lines of `request`
  (`client.ts:56-60`) into a private `function platformHeaders(accept: string): Record<string, string>`
  used by both, so the convention has one copy:

```ts
function platformHeaders(accept: string): Record<string, string> {
  const headers: Record<string, string> = { Accept: accept };
  if (currentWorkspaceId) headers["Workspace-Id"] = currentWorkspaceId;
  if (currentAccessToken) headers["Authorization"] = `Bearer ${currentAccessToken}`;
  return headers;
}

export interface ServerEvent {
  readonly event: string;
  readonly data: string;
}

/**
 * Read a `text/event-stream` response frame by frame.
 *
 * `fetch`, not `EventSource`: `EventSource` cannot send `Authorization` or `Workspace-Id`,
 * and the platform refuses a request without them (07 FR-393, FR-397). Ends when the
 * server closes the stream or `signal` aborts; a refusal throws `ProblemError` as
 * `request` does.
 */
export async function* streamEvents(
  path: string,
  options: { readonly signal?: AbortSignal } = {},
): AsyncGenerator<ServerEvent> {
  const url = new URL(`${BASE}${path}`, window.location.origin);
  let response: Response;
  try {
    response = await fetch(url, {
      headers: platformHeaders("text/event-stream"),
      ...(options.signal ? { signal: options.signal } : {}),
    });
  } catch (error) {
    if (options.signal?.aborted) return;
    throw error;
  }
  if (!response.ok) throw new ProblemError(await readProblem(response));
  if (!response.body) return;

  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) return;
      buffer += value;
      let end = buffer.indexOf("\n\n");
      while (end !== -1) {
        const frame = buffer.slice(0, end);
        buffer = buffer.slice(end + 2);
        let event = "message";
        const data: string[] = [];
        for (const line of frame.split("\n")) {
          if (line.startsWith("event:")) event = line.slice(6).trim();
          else if (line.startsWith("data:")) data.push(line.slice(5).trimStart());
        }
        yield { event, data: data.join("\n") };
        end = buffer.indexOf("\n\n");
      }
    }
  } catch (error) {
    if (options.signal?.aborted) return;
    throw error;
  } finally {
    reader.releaseLock();
  }
}
```

  In `request`, replace the three header lines with
  `const headers = platformHeaders("application/json");` and keep the `Content-Type` and
  `Idempotency-Key` lines after it, unchanged.
- [ ] **Step 4: Run green.** The same command; every case in `client.test.ts` passes, the
  existing ones included. If `TextDecoderStream` is absent under `happy-dom`
  (`frontend/vitest.config.ts`), stop and report: do not polyfill without the lead.
- [ ] **Step 5: Commit.** `feat(frontend): streamEvents — a fetch reader for text/event-stream (WK-675 S13)`.

### Task 2: The jobs API functions

**Files:**
- Modify: `frontend/src/api/jobs.ts`
- Create: `frontend/src/api/__tests__/jobs.test.ts`, `frontend/src/api/__tests__/jobs.test-d.ts`

**Interfaces:**
- Consumes: `request`, `streamEvents` (Task 1).
- Produces:
  - `export type JobKind = components["schemas"]["JobKind"];`
  - `export type JobPage = components["schemas"]["Page_Job_"];`
  - `export type JobStreamEvent = Pick<Job, "id" | "status" | "progress" | "trace_id">;`
  - `export const JOB_STATUSES` and `export const JOB_KINDS` (`as const satisfies readonly …[]`);
  - `export interface JobFilter { status?: JobStatus; kind?: JobKind; cursor?: string; limit?: number }`;
  - `export function listJobs(filter: JobFilter = {}): Promise<JobPage>`;
  - `export async function* streamJobEvents(jobId: string, signal?: AbortSignal): AsyncGenerator<{ kind: "progress" | "done"; job: JobStreamEvent }>`;
  - `export function durationMs(job: Job, now: number): number | null`: `null` while queued;
    `finished_at − started_at` when finished; `now − started_at` while running.

- [ ] **Step 1: Write the failing tests.** `jobs.test.ts` stubs `fetch` as `client.test.ts`
  does (copy its `respond` helper; do not import it). Cases: `listJobs({ status: "running" })`
  calls a URL whose search is exactly `?status=running`; `listJobs({ kind: "model.fit", cursor: "c1", limit: 50 })`
  carries all three; the returned page equals the stubbed body. `streamJobEvents` over a
  stubbed stream of `progress`, `progress`, `done`, `progress` yields three items and stops
  after `done`. `durationMs` for a queued Job (`started_at: null`) is `null`; for a finished
  Job with `started_at` `2026-10-05T10:00:00Z` and `finished_at` `2026-10-05T10:01:30Z` it is
  `90000`. `jobs.test-d.ts`:

```ts
import { describe, expectTypeOf, it } from "vitest";

import { JOB_KINDS, JOB_STATUSES, type JobKind, type JobStatus } from "@/api/jobs";

describe("the jobs filter vocabularies", () => {
  it("offers exactly the job kinds the contract declares", () => {
    expectTypeOf<JobKind>().toEqualTypeOf<(typeof JOB_KINDS)[number]>();
  });
  it("offers exactly the job statuses the contract declares", () => {
    expectTypeOf<JobStatus>().toEqualTypeOf<(typeof JOB_STATUSES)[number]>();
  });
});
```

- [ ] **Step 2: Run red.** `pnpm --dir frontend exec vitest run src/api/__tests__/jobs.test.ts`
  fails because `listJobs`, `streamJobEvents` and `durationMs` are not exported. Then write the
  arrays with one member missing each and run
  `pnpm --dir frontend exec vitest run --typecheck.only src/api/__tests__/jobs.test-d.ts`:
  it fails on both `toEqualTypeOf` lines. Record both outputs.
- [ ] **Step 3: Implement.** The arrays are the generated enums, copied from
  `docs/contracts/openapi/generated.json` `components.schemas.JobKind.enum` (23 members, in that
  order) and `JobStatus.enum` (`queued`, `running`, `succeeded`, `failed`, `cancelled`).
  `listJobs` is `request<JobPage>("/jobs", { query: { status, kind, cursor, limit } })`.
  `streamJobEvents` wraps `streamEvents(\`/jobs/${encodeURIComponent(jobId)}/events\`, { signal })`,
  `JSON.parse`s each frame's `data` as `JobStreamEvent`, yields `progress` and `done` frames,
  ignores any other event name, and returns after `done`.
- [ ] **Step 4: Run green**, both commands. **Step 5: Commit**
  `feat(frontend): listJobs, streamJobEvents and the job vocabularies (WK-675 S13)`.

### Task 3: `JobsView.vue`

**Files:**
- Create: `frontend/src/views/JobsView.vue`, `frontend/src/views/__tests__/JobsView.test.ts`

**Interfaces:**
- Consumes: `listJobs`, `streamJobEvents`, `durationMs`, `JOB_KINDS`, `JOB_STATUSES`,
  `TERMINAL` (`@/api/jobs`); `getBacktest` (`@/api/backtests`); `listModels` (`@/api/models`).
- Produces: the view S14 extends with a row link to `/jobs/:id`.

- [ ] **Step 1: Write the failing tests.** Mock the three API modules as
  `ModelListView.test.ts:8-13` does (`vi.mock(…, async (importOriginal) => ({ ...(await importOriginal<object>()), … }))`),
  keeping `JOB_KINDS`, `JOB_STATUSES`, `TERMINAL` and `durationMs` real. Stub `RouterLink` as
  that file does (`:27-29`) but render `JSON.stringify(to)` into `data-to`, so a named-route
  object is assertable. Build each `Job` with an annotated factory (`const job = (over: Partial<Job> = {}): Job => ({ … , ...over })`)
  carrying the eight required fields (`id`, `workspace_id`, `kind`, `status`, `queue`,
  `submitted_by`, `source`, `queued_at`). Cases, one `it` each, matching Acceptance 4, 5 and 6:
  1. a running Job with `progress: { fraction: 0.4, stage: "boosting", counters: {} }` renders a
     `<progress>` with `value` 0.4 and accessible name containing `40%` and `boosting`;
  2. `stalled: true` renders `Stalled` in that row;
  3. selecting status `failed` calls `listJobs` with `{ status: "failed" }` and no cursor;
  4. **Load more** calls `listJobs` with the page's `next_cursor` and the rows grow;
  5. six running rows open exactly four `streamJobEvents` calls, for the four newest ids;
  6. a `progress` event for row 2 changes row 2's bar and no other row's;
  7. a `done` event calls `listJobs` again with the current filter and no cursor;
  8. unmount aborts every signal passed to `streamJobEvents`;
  9. a succeeded `model.backtest` Job with `result: { kind: "artifact", ref: "backtest:b1" }`,
     `getBacktest` → `{ model_id: "m1", … }`, `listModels` → `{ items: [{ id: "m1", model_family_slug: "freq" }], truncated: false }`
     renders a link whose `data-to` is
     `{"name":"model-backtest","params":{"slug":"freq","backtestId":"b1"}}`;
  10. the same with `listModels` → `{ items: [], truncated: true }` renders the text
      *"its model is not in the first 1000 models listed"* and no link.
- [ ] **Step 2: Run red.** `pnpm --dir frontend exec vitest run src/views/__tests__/JobsView.test.ts`
  fails because `../JobsView.vue` does not exist. Then, with a skeleton view that renders only
  the table, each case fails on its own assertion; record each.
- [ ] **Step 3: Implement** with `<script setup lang="ts">`. State: `jobs: Ref<Job[]>`,
  `nextCursor`, `filter: { status?: JobStatus; kind?: JobKind }`, `error: ProblemError | null`,
  a `Map<string, AbortController>` of open streams, and a `Map<string, BacktestLink>` where
  `type BacktestLink = { slug: string; backtestId: string } | { reason: string }`.
  - `load(reset)`: `listJobs({ ...filter, cursor: reset ? undefined : nextCursor })`; replace or
    append; then `syncStreams()` and `resolveBacktests()`.
  - `syncStreams()` (DP-S13-1 (a)): the four newest rows whose status is not in `TERMINAL`
    keep or get a stream; every other stream is aborted and removed. Each stream's loop applies
    a `progress` event to its row (`status`, `progress`, `trace_id`; `stalled` set `false` when
    `progress` changed), and on `done` applies it, then calls `load(true)`.
  - `onBeforeUnmount`: abort every controller.
  - Markup: a `<table>` with `<caption>Jobs</caption>`; columns Kind, Status, Progress,
    Submitted by, Duration, Result. Progress cell:
    `<progress :value="job.progress?.fraction ?? 0" max="1" :aria-label="`${Math.round((job.progress?.fraction ?? 0) * 100)}% — ${job.progress?.stage || 'no stage reported'}`">`
    with the stage as visible text beside it. Status cell shows `Stalled` after the status when
    `job.stalled`. Duration formats `durationMs(job, Date.now())` as `m:ss`, or `—` when `null`.
    Result cell, for a resolved backtest:
    `<RouterLink :to="{ name: 'model-backtest', params: { slug: link.slug, backtestId: link.backtestId } }">Open backtest</RouterLink>`
    written on one line, with single quotes inside, so `routeGraph.ts` counts it (Choice 4).
  - Filters: two labelled `<select>`s over `JOB_STATUSES` and `JOB_KINDS`, each with an
    "Any" option; a change calls `load(true)`.
  - A `ProblemError` renders its `title` and `trace_id` in a `role="alert"` region.
- [ ] **Step 4: Run green.** **Step 5: Commit**
  `feat(frontend): the Jobs list view, live over the job event stream (WK-675 S13)`.

### Task 4: The route, the link from the entry, and the reachability exception

**Files:**
- Modify: `frontend/src/router/index.ts`, `frontend/src/App.vue`,
  `frontend/src/router/__tests__/reachability.test.ts`, `frontend/src/router/__tests__/index.test.ts`

- [ ] **Step 1: Remove the exception first, and see red.** Delete
  `"/models/:slug/backtests/:backtestId",` from `WHITELISTED` and rewrite the comment's third
  paragraph to say what is true: *"/models/:slug/backtests/:backtestId was excepted until the
  Jobs view (WK-675 S13) linked it from a succeeded backtest Job's result."* (delete the
  sentence *"The jobs view is a later phase (FR-24)."* and *"The exception lifts when that UI
  lands."*). Run `pnpm --dir frontend exec vitest run src/router/__tests__/reachability.test.ts`.
  Expected: *"names every route with no inbound path from the entry"* fails with
  `["/models/:slug/backtests/:backtestId"]`. Record it.
- [ ] **Step 2: Add the route** after the `/reference` record, in the form `RECORD`
  (`routeGraph.ts:28-29`) parses: `path` first, `name` second.

```ts
  {
    // `07` §5.3 Jobs (`07:398`); WK-675 S13 (FD-1284 option D). FR-25: linked from the shell.
    path: "/jobs",
    name: "jobs",
    meta: { requiresAuth: true },
    component: () => import("@/views/JobsView.vue"),
  },
```

- [ ] **Step 3: Add the link** in `App.vue`'s `nav`, after `Peril structures`, in the existing
  form: `to="/jobs"`, the same two classes, text `Jobs`.
- [ ] **Step 4: Add the resolution case** to `frontend/src/router/__tests__/index.test.ts`:
  `/jobs` resolves to the route named `jobs`, mirroring that file's `router().resolve(…)` cases
  (`:36`, `:51`).
- [ ] **Step 5: Run green.** `pnpm --dir frontend exec vitest run src/router/__tests__`; all pass,
  the reachability case included. **Step 6: Commit**
  `feat(frontend): /jobs route and entry link; the backtest route leaves the FR-25 exception list (WK-675 S13)`.

### Task 5: Type-check, lint and build

- [ ] `pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend build`.
  Each rc 0. Record the build's chunk table: `JobsView-*.js` is a new lazy chunk, and the shared
  `index-*.js` delta is reported, before → after, raw and gzip.

### Task 6: The gate and the ledger

- [ ] **Step 1: The full gate, both halves** (`CLAUDE.md` §11), delegated to `gate-runner`, as the
  only full gate on the box (`RL 9620` item 1). Announce it first (`delivery-process.md` §8).
  Record the per-command table and the tree.
- [ ] **Step 2: Self-check Acceptance 1–12** command by command; paste each output into the
  ledger.
- [ ] **Step 3: Open the PR**, naming the range `origin/main...HEAD`, DP-S13-1's resolver, and
  the bundle delta.

## Hand-off

- **To S14 (PL 9574, working id):** `listJobs`, `streamJobEvents`, `JobStreamEvent`, `durationMs`
  and `streamEvents` exist; S14 adds the row link from `JobsView.vue` to `/jobs/:id` and the
  detail view. The backtest-link resolution (Choice 3) is reused there, not rewritten.
- **To S5, S8 and S11:** a slice that starts a Job links to `/jobs` now, and to `/jobs/:id`
  after S14 (`PL-1286` `:372-375`).
- **To the auditor at slice close:** Choice 2 (no submitter filter) is a recorded gap against the
  route's `submitted_by` parameter, not against a numbered requirement.

## Self-review

- **Spec coverage.** FR-25, FR-399 (the list's fields), FR-400 (fraction and stage), NFR-528 and
  NFR-463 each map to an Acceptance item; FR-401, FR-402 and FR-403 are named as S14's. FR-24 is
  cited only for the comment correction.
- **Literals verified at `137bc817`:** route paths and parameters (`jobs.py:105-317`); the event
  names and payload keys (`jobs.py:288-305`); `JobResult` ref form (`model_handlers.py:1325`);
  `Backtest` and `Model` fields and `JobKind`/`JobStatus` enums (`generated.json`);
  `MODEL_PAGE_CAP` (`models.ts:35`); `WHITELISTED` and its comment (`reachability.test.ts:22-40`);
  `RECORD`, `TO_TARGET` and the named-route form (`routeGraph.ts:28-31`, `:61`); the route name
  `model-backtest` (`router/index.ts:116`); the `App.vue` link classes; the `vi.mock` and
  `RouterLink` stub idiom (`ModelListView.test.ts:8-29`). **Not verified:** whether
  `TextDecoderStream` exists under the test environment; Task 1 Step 4 says what to do.
- **Placeholders:** none.
- **Rulings re-checked before the PR:** open PRs at 17:09 BST; none touches `frontend/` or rules
  on the Jobs views. `RL 9620` read at `381254c3` (#1162, unmerged).
