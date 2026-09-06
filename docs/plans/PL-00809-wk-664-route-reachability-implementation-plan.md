---
id: PL-809
family: plan
kind: leaf
title: WK-664 Route Reachability Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-26
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-26-w6b-route-reachability.md
---

# WK-664 Route Reachability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every route the frontend registers reachable from the application entry by links alone, enforced by a route-graph test (FR-25).

**Architecture:** A test builds the link graph from the router source and the view sources, then names every route with no inbound path from the entry. The route-graph test is the mechanism that sees paths, so it lands first and its positive control runs against the current tree. Four connection tasks then close the graph: the route-graph test, the dataset list repair, the model list entrance, and the navigation links.

**Tech Stack:** Vue 3 Composition API with `<script setup lang="ts">`, vue-router 5.2, Vitest and Testing Library. The graph test reads source files with node:fs. The backend demo guide's `_routed_paths` (backend/src/app/demo/guide.py:124-144) is the precedent.

**Spec:** `docs/specs/00-overview.md` §5.1 — FR-25 (line 228): "A route the frontend registers is reachable from the application entry by following links alone."

**Slice source:** Backlog #136 (HANDOVER §5, close-record skeleton §5): FR-25 specified, the four-item connection scope agreed, nothing built. Phase-exit blocker. No slice-map row exists. FR-25's owner clause names "the slice that carries the connection work".

**Highest ids:** No requirement id is minted by this slice. The slice changes no spec. FR-25 governs. FR-408 and FR-24 bound it (Global Constraints).

## Global Constraints

- FR-25: every registered route is reachable from the entry by links alone.
- The graph counts registered routes and view-source links only. Component-sourced links do not count.
- FR-408: the demo path is gated behind `dev_auth_enabled`. The demo entrance does not discharge reachability.
- FR-24: the jobs view belongs to no Phase 1b slice. No slice builds one.
- Vue 3 Composition API with `<script setup lang="ts">` only.
- Never hand-write an API type. `Model` and `Dataset` come from the generated schema.
- Both gate halves pass before a push. This slice is frontend-only. CI runs the frontend workflow.
- A whitelist entry names its route and its reason. No other exception exists.
- ASD-STE100 prose. Code, identifiers and file paths stay unchanged.
- A filed plan stays frozen at its date.

---

## Findings (verified 2026-08-26 against origin/main c56ec75)

**F1. The route count moved.** FR-25's measured "3 of 18" is a dated record from 2026-08-25. The router now registers 23 routes. The graph test re-measures. The plan's expected named set is 16.

**F2. The dataset list renders no links.** DatasetListView.vue:182-184 renders each dataset name as a plain span. The SFC contains no `to=`, no `href` and no router call. The list is the only gate on the whole `/data/:slug` subtree.

**F3. The model subtree has no list entrance.** `/models` is not registered (six `/models/...` paths exist). No ModelListView.vue exists. `listModels()` (frontend/src/api/models.ts:49-51) is the data source. The route slug is `model_family_slug`. ModelRefLink.vue:16 is the row-link precedent. ModelComparisonView.vue:104 links `to="/models"`, a dead link until this slice registers it.

**F4. The WF-698 A9 profile route is orphaned.** `/data/:slug/v/:version/profile` has no inbound link. VersionDetailView.vue:114-131 links the validation report and the factor workbench. It omits the profile. ProfileView is built.

**F5. Three library routes have no inbound link.** The nav offers Data, Demo and Reference only (App.vue:17-37). `/objectives`, `/metrics` and `/peril-structures` are orphans. Their children are script-href linked from the libraries (ObjectiveLibraryView.vue:45, PerilStructureLibraryView.vue:36, rendered through ArtifactLibraryTable.vue:91-97).

**F6. One route cannot be wired.** `/models/:slug/backtests/:backtestId` is job-result-addressed: frontend/src/api/backtests.ts:10-12 carries the reason verbatim, the backend exposes only GET /models/backtests/{id}, and the Model type carries no backtest ids. The jobs view is a later phase (FR-24). **Ruling (manager, 2026-08-26):** the graph test whitelists this route with its reason. The exception lifts when the jobs UI lands.

**F7. The demo entrance stays out of the graph.** DemoView.vue:161 binds `:to="view.route"`, a computed value with no literal. The extractor counts literals only, so the demo adds no edges. This matches FR-408's gate.

**F8. The auth flow stays out of the graph.** `/callback` and `/silent-renew` are the OIDC flow's entry points (W6b-10): the identity provider redirects the browser to them. Nothing in the app links to them. **Ruling (manager, 2026-08-26):** the whitelist names them with that reason.

**F9. The corpus is fully enumerated.** The literal inventory (App.vue plus all views) holds 22 link candidates. 21 resolve to registered routes. One (`/models`, ModelComparisonView.vue:104) is dead. DemoView's bound `:to` is data, not a literal. Before the connections, the BFS reaches `/`, `/data`, `/demo` and `/reference` only.

**F10. The demo guide needs no change.** `_routed_paths` (backend/src/app/demo/guide.py:124-144) regex-reads the router source. `/models` badges itself once registered.

**F11. Every orphan gets a task.** F3 becomes Task 3. F4 becomes Task 4. F2 becomes Task 2. F1, F9 and the mechanism become Task 1.

### Closure after the connections (route → inbound edge)

| Route | Inbound edge |
|---|---|
| /data/:slug | DatasetListView row (Task 2) |
| /data/:slug/rules | DatasetDetailView.vue:111 |
| /data/:slug/v/:version | DatasetDetailView.vue:202 |
| /data/:slug/v/:version/validation | VersionDetailView.vue:115 |
| /data/:slug/v/:version/profile | VersionDetailView (Task 4) |
| /factors/:datasetVersionId | VersionDetailView.vue:127 |
| /models/compare | ModelListView header (Task 3) |
| /models/:slug | ModelListView row (Task 3) |
| /models/:slug/diagnostics | ModelDetailView.vue:167 |
| /models/:slug/predict | ModelDetailView (Task 4) |
| /models/new | ModelListView header (Task 3) |
| /objectives | App.vue nav (Task 4) |
| /objectives/:id/certificate | ObjectiveLibraryView.vue:45 |
| /metrics | App.vue nav (Task 4) |
| /peril-structures | App.vue nav (Task 4) |
| /peril-structures/:id | PerilStructureLibraryView.vue:36 |

Whitelisted routes: `/callback`, `/silent-renew`, `/models/:slug/backtests/:backtestId` (F6, F8).

---

### Task 1: The route-graph test

**Files:**
- Create: `frontend/src/router/__tests__/routeGraph.ts`
- Create: `frontend/src/router/__tests__/routeGraph.test.ts`
- Create: `frontend/src/router/__tests__/reachability.test.ts`

**Interfaces:**
- Produces: `parseRoutes(source: string): ParsedRoute[]`, `linkCandidates(source: string): string[]`, `isLiteralTarget(raw: string): boolean`, `resolveTarget(raw: string, routes: ParsedRoute[]): string | null`, `extractTargets(source: string, routes: ParsedRoute[]): string[]`, `REPO_ROOT: string`. `ParsedRoute` = `{ path: string; name?: string; redirect?: string; view?: string }`. Tasks 2-4 use nothing from here. The test owns the mechanism.

- [ ] **Step 1: Write the extractor module**

Create `frontend/src/router/__tests__/routeGraph.ts`:

```ts
/**
 * The route graph for FR-25. The test builds the link graph from the router
 * source and the view sources, then reports every route with no inbound path
 * from the application entry.
 *
 * The graph counts what the requirement counts: literal `to` targets, template
 * literals, named-route objects and `href` literals in view sources and the app
 * shell. A `:to` bound to a computed value carries no literal and no edge.
 */

import { readFileSync } from "node:fs";

export interface ParsedRoute {
  path: string;
  name?: string;
  redirect?: string;
  view?: string;
}

export const REPO_ROOT = new URL("../../../../", import.meta.url).pathname;

const COMMENT = /\/\/[^\n]*|\/\*[\s\S]*?\*\//g;
const RECORD =
  /\{\s*path:\s*"([^"]+)",\s*(?:name:\s*"([^"]*)",\s*)?(?:redirect:\s*"([^"]+)",|component:\s*\(\)\s*=>\s*import\("@\/([^"]+)"\),)[\s\S]*?\n\s*\},/g;
const TO_TARGET = /\bto="([^"]*)"/g;
const HREF_ATTR = /\bhref="([^"]*)"/g;
const HREF_SCRIPT = /href:\s*(`[^`]*`|"[^"]*")/g;

export function parseRoutes(source: string): ParsedRoute[] {
  const cleaned = source.replace(COMMENT, "");
  const routes: ParsedRoute[] = [];
  for (const match of cleaned.matchAll(RECORD)) {
    routes.push({ path: match[1], name: match[2], redirect: match[3], view: match[4] });
  }
  return routes;
}

export function isLiteralTarget(raw: string): boolean {
  const trimmed = raw.trim();
  return (
    trimmed.startsWith("`") || trimmed.startsWith('"') || trimmed.startsWith("{")
  );
}

export function resolveTarget(raw: string, routes: ParsedRoute[]): string | null {
  const named = /^\{\s*name:\s*'([^']+)'/.exec(raw.trim());
  if (named) {
    const route = routes.find((candidate) => candidate.name === named[1]);
    return route ? route.path : null;
  }
  const literal = /^(`[^`]*`|"[^"]*")$/.exec(raw.trim());
  if (!literal) return null;
  const target = literal[1].slice(1, -1).split("?")[0];
  if (!target.startsWith("/")) return null;
  const normalized = target.replace(/\$\{[^}]*\}/g, "¶");
  const segments = normalized.split("/");
  for (const route of routes) {
    const pattern = route.path.split("/");
    if (segments.length !== pattern.length) continue;
    const matches = segments.every(
      (segment, index) =>
        pattern[index].startsWith(":") || pattern[index] === segment,
    );
    if (matches) return route.path;
  }
  return null;
}

export function linkCandidates(source: string): string[] {
  const cleaned = source.replace(COMMENT, "");
  const candidates: string[] = [];
  for (const re of [TO_TARGET, HREF_ATTR, HREF_SCRIPT]) {
    for (const match of cleaned.matchAll(re)) candidates.push(match[1]);
  }
  return candidates;
}

export function extractTargets(source: string, routes: ParsedRoute[]): string[] {
  const targets: string[] = [];
  for (const raw of linkCandidates(source)) {
    const resolved = resolveTarget(raw, routes);
    if (resolved) targets.push(resolved);
  }
  return targets;
}
```

The record regex requires three facts about `frontend/src/router/index.ts`: a record starts with `{`, `path` is the first literal, and a record closes with `},` alone on its line. The `COMMENT` strip handles the comment blocks at the start of the `/` and `/demo` records. The coverage-parity test in Step 2 proves the parse against the real file, so a future record shape that breaks the regex fails loudly instead of a silent pass.

- [ ] **Step 2: Write the extractor unit tests**

Create `frontend/src/router/__tests__/routeGraph.test.ts`:

```ts
import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import { routes } from "../index";
import { extractTargets, parseRoutes, REPO_ROOT, resolveTarget } from "./routeGraph";

const SAMPLE = `{
  // The entry: the redirect target carries the guard.
  path: "/",
  redirect: "/data",
},
{
  path: "/models",
  name: "models",
  component: () => import("@/views/ModelListView.vue"),
},
{
  path: "/models/:slug",
  name: "model-detail",
  component: () => import("@/views/ModelDetailView.vue"),
  props: (route: RouteLocationNormalizedLoaded) => ({ slug: route.params.slug }),
  meta: { requiresAuth: true },
},`;

describe("parseRoutes", () => {
  it("reads path, name, redirect and view from a router source", () => {
    expect(parseRoutes(SAMPLE)).toEqual([
      { path: "/", redirect: "/data" },
      { path: "/models", name: "models", view: "views/ModelListView.vue" },
      { path: "/models/:slug", name: "model-detail", view: "views/ModelDetailView.vue" },
    ]);
  });

  it("parses every route the router exports", () => {
    const source = readFileSync(`${REPO_ROOT}/frontend/src/router/index.ts`, "utf8");
    const parsed = parseRoutes(source)
      .map((route) => route.path)
      .sort();
    const exported = routes.map((route) => route.path).sort();
    expect(parsed).toEqual(exported);
  });
});

describe("resolveTarget", () => {
  const SAMPLE_ROUTES = [
    { path: "/data/:slug" },
    { path: "/data/:slug/v/:version/validation" },
    { path: "/models/:slug" },
    { path: "/models/:slug/predict", name: "model-predict" },
    { path: "/objectives/:id/certificate" },
  ] as unknown as ReturnType<typeof parseRoutes>;

  it("resolves a template literal with params", () => {
    expect(
      resolveTarget("`/data/${slug}/v/${detail.version}/validation`", SAMPLE_ROUTES),
    ).toBe("/data/:slug/v/:version/validation");
  });

  it("drops the query before matching", () => {
    expect(resolveTarget("`/models/${slug}?version=${version}`", SAMPLE_ROUTES)).toBe(
      "/models/:slug",
    );
  });

  it("resolves a named-route object through the name map", () => {
    expect(resolveTarget("{ name: 'model-predict', params: { slug } }", SAMPLE_ROUTES)).toBe(
      "/models/:slug/predict",
    );
  });

  it("returns null for a computed value", () => {
    expect(resolveTarget("view.route", SAMPLE_ROUTES)).toBeNull();
  });

  it("returns null for an unregistered name", () => {
    expect(resolveTarget("{ name: 'nope', params: {} }", SAMPLE_ROUTES)).toBeNull();
  });

  it("returns null for a literal that matches no route", () => {
    expect(resolveTarget("`/nope/${id}`", SAMPLE_ROUTES)).toBeNull();
  });
});

describe("extractTargets", () => {
  it("extracts static, template and script-side targets from an SFC", () => {
    const source = `
<template>
  <RouterLink to="/data">Data</RouterLink>
  <RouterLink :to="\`/data/\${slug}/rules\`">Rules</RouterLink>
  <!-- <RouterLink :to="\`/data/\${slug}/profile\`">gone</RouterLink> -->
  <a href="/models">Models</a>
</template>
<script setup lang="ts">
const rows = [{ href: \`/objectives/\${id}/certificate\` }];
const bound = view.route;
</script>`;
    const targetRoutes = [
      { path: "/data" },
      { path: "/data/:slug/rules" },
      { path: "/models" },
      { path: "/objectives/:id/certificate" },
    ] as unknown as ReturnType<typeof parseRoutes>;
    expect(extractTargets(source, targetRoutes).sort()).toEqual([
      "/data",
      "/data/:slug/rules",
      "/models",
      "/objectives/:id/certificate",
    ]);
  });
});
```

- [ ] **Step 3: Run the unit tests to verify they fail**

Run: `pnpm --dir frontend vitest run src/router/__tests__/routeGraph.test.ts`
Expected: FAIL, "No test files found" or a module error. The module does not exist yet.

- [ ] **Step 4: Write the reachability test**

Create `frontend/src/router/__tests__/reachability.test.ts`:

```ts
import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import {
  extractTargets,
  isLiteralTarget,
  linkCandidates,
  parseRoutes,
  REPO_ROOT,
  resolveTarget,
} from "./routeGraph";

const ROUTER_SOURCE = readFileSync(`${REPO_ROOT}/frontend/src/router/index.ts`, "utf8");
const ROUTES = parseRoutes(ROUTER_SOURCE);
const SHELL = readFileSync(`${REPO_ROOT}/frontend/src/App.vue`, "utf8");

/**
 * Routes the graph cannot reach by links, each with its reason.
 *
 * /callback and /silent-renew are the OIDC flow's entry points (W6b-10). The
 * identity provider redirects the browser to them. Nothing in the app links to
 * them.
 *
 * /models/:slug/backtests/:backtestId is job-result-addressed
 * (frontend/src/api/backtests.ts:10-12). A caller who has just run a backtest
 * reaches it through the Job's backtest:{id} result. The backend exposes only
 * GET /models/backtests/{id} and the Model type carries no backtest ids. The
 * jobs view is a later phase (FR-24). The exception lifts when that UI
 * lands.
 */
const WHITELISTED = new Set([
  "/callback",
  "/silent-renew",
  "/models/:slug/backtests/:backtestId",
]);

function viewSource(view: string): string {
  return readFileSync(`${REPO_ROOT}/frontend/src/${view}`, "utf8");
}

function reachableSet(): Set<string> {
  const shellTargets = extractTargets(SHELL, ROUTES);
  const reached = new Set<string>();
  const queue = ["/"];
  while (queue.length > 0) {
    const path = queue.shift()!;
    if (reached.has(path)) continue;
    reached.add(path);
    const record = ROUTES.find((route) => route.path === path);
    if (!record) continue;
    if (record.redirect) queue.push(record.redirect);
    const targets = record.view ? extractTargets(viewSource(record.view), ROUTES) : [];
    for (const target of [...shellTargets, ...targets]) queue.push(target);
  }
  return reached;
}

describe("route reachability (FR-25)", () => {
  it("names every route with no inbound path from the entry", () => {
    const reached = reachableSet();
    const unreachable = ROUTES.map((route) => route.path).filter(
      (path) => !reached.has(path) && !WHITELISTED.has(path),
    );
    expect(unreachable).toEqual([]);
  });

  it("finds no literal link to an unregistered route", () => {
    const views = ROUTES.map((route) => (route.view ? viewSource(route.view) : ""));
    const candidates = [SHELL, ...views].flatMap(linkCandidates);
    const dead = [
      ...new Set(
        candidates
          .filter(isLiteralTarget)
          .filter((raw) => resolveTarget(raw, ROUTES) === null),
      ),
    ];
    expect(dead).toEqual([]);
  });
});
```

- [ ] **Step 5: Run the reachability test on the current tree — the positive control**

Run: `pnpm --dir frontend vitest run src/router/__tests__/reachability.test.ts`
Expected: FAIL. The first test names exactly these 16 routes:

```
/data/:slug
/data/:slug/rules
/data/:slug/v/:version
/data/:slug/v/:version/profile
/data/:slug/v/:version/validation
/factors/:datasetVersionId
/models/compare
/models/:slug
/models/:slug/diagnostics
/models/:slug/predict
/models/new
/objectives
/objectives/:id/certificate
/metrics
/peril-structures
/peril-structures/:id
```

The second test names exactly `"/models"` (ModelComparisonView.vue:104).

This run is the CLAUDE.md §13 broken-input proof: the check must print a failure before it can count as tested. Record the failure output verbatim in the task report. It becomes the PR body's evidence.

**Convention guard:** a different named set means the plan's facts or the extractor is wrong. Stop and report the output. Never edit the expectation to match the output. A larger set than the 16 means the extractor missed links; a smaller set means the plan's facts are stale.

- [ ] **Step 6: Run the full new-file suite to verify the split**

Run: `pnpm --dir frontend vitest run src/router/__tests__/routeGraph.test.ts src/router/__tests__/reachability.test.ts`
Expected: routeGraph.test.ts PASS (9 tests), reachability.test.ts FAIL (2 tests, per Step 5). The extractor units pass while the graph is red; the red is the tree's state, not the mechanism's.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/router/__tests__/routeGraph.ts frontend/src/router/__tests__/routeGraph.test.ts frontend/src/router/__tests__/reachability.test.ts
git commit -m "test(frontend): route-graph reachability test for FR-25

The test names every registered route with no inbound path from the entry.
Red on the current tree by design: the run records the 16-route orphan set
as the positive control. Whitelists /callback and /silent-renew (OIDC flow
entries, W6b-10) and /models/:slug/backtests/:backtestId (job-result-
addressed, api/backtests.ts:10-12)."
```

The red commit is deliberate and documented. Tasks 2-4 flip it green. Task 5 runs the same test as the gate's reachability check.

---

### Task 2: Repair the dataset list

**Files:**
- Modify: `frontend/src/views/DatasetListView.vue:182-184`
- Test: `frontend/src/views/__tests__/DatasetListView.test.ts`

**Interfaces:**
- Consumes: `Dataset.slug` (generated schema). The route `/data/:slug` already exists with `props: true`, so `slug` arrives as a prop in DatasetDetailView.
- Produces: the name cell renders a RouterLink whose target is `/data/<slug>`.

- [ ] **Step 1: Write the failing test**

In `frontend/src/views/__tests__/DatasetListView.test.ts`, change the `table()` helper's render call (line 55) to mount the RouterLink stub that exposes `to`:

```ts
async function table(body: unknown = SEEDED): Promise<HTMLElement> {
  stubFetch(200, body);
  render(DatasetListView, {
    global: {
      stubs: { RouterLink: { props: ["to"], template: '<a :href="to"><slot /></a>' } },
    },
  });
  await screen.findByRole("table");
  return screen.getByRole("table");
}
```

Then add this test inside the `describe("the dataset list", ...)` block:

```ts
it("links a dataset name to its detail route", async () => {
  // FR-25: the list is the only way into the /data/:slug subtree, so the
  // name must be a link. The slug stays visible beside it, unchanged.
  const t = await table();

  const name = cellUnder(t, /freMTPL2/, "Name");
  const link = within(name).getByRole("link", { name: /freMTPL2 — French motor TPL/ });
  expect(link).toHaveAttribute("href", "/data/fremtpl2-a78676");
  expect(within(name).getByText("fremtpl2-a78676")).toBeInTheDocument();
});
```

Add `within` to the `@testing-library/vue` import at the top of the file.

- [ ] **Step 2: Run the test to verify it fails**

Run: `pnpm --dir frontend vitest run src/views/__tests__/DatasetListView.test.ts`
Expected: FAIL. `getByRole("link")` finds nothing (the name renders as a span), and the existing tests fail on the un-stubbed RouterLink.

- [ ] **Step 3: Implement the link**

In `frontend/src/views/DatasetListView.vue`, replace lines 182-184:

```vue
          <td class="py-3">
            <span class="font-medium">{{ dataset.name || dataset.slug }}</span>
            <span class="ml-2 font-mono text-xs text-slate-500">{{ dataset.slug }}</span>
          </td>
```

with:

```vue
          <td class="py-3">
            <RouterLink
              :to="`/data/${dataset.slug}`"
              class="font-medium text-sky-700 hover:underline"
            >
              {{ dataset.name || dataset.slug }}
            </RouterLink>
            <span class="ml-2 font-mono text-xs text-slate-500">{{ dataset.slug }}</span>
          </td>
```

The link class copies ModelDetailView's inline-link style (`text-sky-700 hover:underline`). The slug span stays untouched: FR-55's badge semantics still hold, and the graph counts the RouterLink only.

- [ ] **Step 4: Run the test to verify it passes**

Run: `pnpm --dir frontend vitest run src/views/__tests__/DatasetListView.test.ts`
Expected: PASS, all tests in the file.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/DatasetListView.vue frontend/src/views/__tests__/DatasetListView.test.ts
git commit -m "feat(frontend): link dataset names to their detail route

FR-25. The dataset list severed the graph: the whole /data/:slug
subtree hung on a name rendered as a span. The name is now a RouterLink."
```

---

### Task 3: The model subtree's list entrance

**Files:**
- Create: `frontend/src/views/ModelListView.vue`
- Modify: `frontend/src/router/index.ts` (insert the `/models` record before the `/models/compare` record)
- Test: `frontend/src/views/__tests__/ModelListView.test.ts`
- Test: `frontend/src/router/__tests__/index.test.ts`

**Interfaces:**
- Consumes: `listModels(): Promise<Paged<Model>>` (frontend/src/api/models.ts:49-51), `Model.model_family_slug`, `Model.version`, `Model.status` (generated schema).
- Produces: the route `/models` named `models`, and a view with three outbound edges: `/models/:slug?version=...` per row, `/models/new`, `/models/compare`. Tasks 1 and 4 depend on these edges.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/views/__tests__/ModelListView.test.ts`:

```ts
import { render, screen, waitFor } from "@testing-library/vue";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { Model } from "@/api/models";

import ModelListView from "../ModelListView.vue";

const listModels = vi.fn();

vi.mock("@/api/models", async (importOriginal) => ({
  ...(await importOriginal<object>()),
  listModels: () => listModels(),
}));

function model(over: Partial<Model> = {}): Model {
  return {
    id: "01a00500-0000-7000-8000-000000000001",
    dataset_version_id: "01a00495-58d0-71f8-a039-cd4c45337960",
    model_family_slug: "motor-ad-frequency",
    version: 7,
    status: "approved",
    ...over,
  } as Model;
}

afterEach(() => vi.clearAllMocks());

const stubs = {
  RouterLink: { props: ["to"], template: '<a :href="to"><slot /></a>' },
};

describe("the model list", () => {
  it("links each model row to its detail route with its version", async () => {
    listModels.mockResolvedValue({
      items: [
        model(),
        model({ id: "m2", model_family_slug: "freq-poisson", version: 3 }),
      ],
      truncated: false,
    });
    render(ModelListView, { global: { stubs } });

    const rows = await screen.findAllByRole("link");
    expect(
      rows.some((row) => row.getAttribute("href") === "/models/motor-ad-frequency?version=7"),
    ).toBe(true);
    expect(rows.some((row) => row.getAttribute("href") === "/models/freq-poisson?version=3")).toBe(
      true,
    );
  });

  it("offers the two header actions: a new model and a comparison", async () => {
    listModels.mockResolvedValue({ items: [], truncated: false });
    render(ModelListView, { global: { stubs } });

    const newLink = await screen.findByRole("link", { name: "New model" });
    expect(newLink.getAttribute("href")).toBe("/models/new");
    const compare = screen.getByRole("link", { name: "Compare" });
    expect(compare.getAttribute("href")).toBe("/models/compare");
  });

  it("says when nothing has been fitted yet", async () => {
    listModels.mockResolvedValue({ items: [], truncated: false });
    render(ModelListView, { global: { stubs } });

    await waitFor(() =>
      expect(screen.getByText(/no models yet/i)).toBeInTheDocument(),
    );
  });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pnpm --dir frontend vitest run src/views/__tests__/ModelListView.test.ts`
Expected: FAIL, module not found. The component does not exist yet.

- [ ] **Step 3: Implement the view**

Create `frontend/src/views/ModelListView.vue`:

```vue
<script setup lang="ts">
import { onMounted, ref } from "vue";

import { listModels, type Model } from "@/api/models";

const models = ref<Model[]>([]);
const loadFailure = ref<string | null>(null);

onMounted(async () => {
  try {
    const page = await listModels();
    models.value = page.items;
  } catch (error) {
    loadFailure.value = error instanceof Error ? error.message : String(error);
  }
});
</script>

<template>
  <section>
    <header class="mb-5 flex items-center justify-between">
      <h1 class="text-xl font-semibold tracking-tight">Models</h1>
      <div class="flex gap-3">
        <RouterLink
          to="/models/new"
          class="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
        >
          New model
        </RouterLink>
        <RouterLink
          to="/models/compare"
          class="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
        >
          Compare
        </RouterLink>
      </div>
    </header>

    <p
      v-if="loadFailure"
      class="text-sm text-red-600"
    >
      {{ loadFailure }}
    </p>
    <p
      v-else-if="models.length === 0"
      class="text-sm text-slate-500"
    >
      No models yet. Fit one from the factor workbench.
    </p>
    <table
      v-else
      class="w-full text-left text-sm"
    >
      <thead class="border-b border-slate-200 text-slate-500">
        <tr>
          <th class="py-2 pr-4">Model</th>
          <th class="py-2 pr-4">Version</th>
          <th class="py-2">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="model in models"
          :key="model.id"
          class="border-b border-slate-100"
        >
          <td class="py-3 pr-4">
            <RouterLink
              :to="`/models/${model.model_family_slug}?version=${model.version}`"
              class="font-medium text-sky-700 hover:underline"
            >
              {{ model.model_family_slug }}
            </RouterLink>
          </td>
          <td class="py-3 pr-4">{{ model.version }}</td>
          <td class="py-3">{{ model.status }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
```

The row target copies ModelRefLink.vue:16. The `?version=` query selects the version in ModelDetailView's props function. The Compare link lands on ModelComparisonView's existing refused state ("Select two or more models to compare", ModelComparisonView.vue:33-39), which explains the empty case. The list shows `page.items`. MODEL_PAGE_CAP=5 bounds the page through the API client, so the table cannot overflow.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pnpm --dir frontend vitest run src/views/__tests__/ModelListView.test.ts`
Expected: PASS, all three tests.

- [ ] **Step 5: Register the route**

In `frontend/src/router/index.ts`, insert this record immediately before the `path: "/models/compare"` record:

```ts
{
  path: "/models",
  name: "models",
  component: () => import("@/views/ModelListView.vue"),
},
```

The static `/models` segment outranks `/models/:slug` at any position (measured in index.test.ts's own preamble, vue-router 5.2.0), so declaration order does not matter, but the plan puts the list before its children for readability.

- [ ] **Step 6: Extend the router resolution test**

In `frontend/src/router/__tests__/index.test.ts`, inside the `describe("the /models routes", ...)` block, add:

```ts
it("resolves /models to the model list", () => {
  expect(matchedNames("/models")).toContain("models");
});
```

- [ ] **Step 7: Run the router test to verify it passes**

Run: `pnpm --dir frontend vitest run src/router/__tests__/index.test.ts`
Expected: PASS, all tests in the file.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/views/ModelListView.vue frontend/src/router/index.ts frontend/src/views/__tests__/ModelListView.test.ts frontend/src/router/__tests__/index.test.ts
git commit -m "feat(frontend): register /models with a model list view

FR-25. The model subtree had six routes and no list entrance. The new
view lists listModels() rows, links each to /models/:slug?version=...,
and carries the new-model and compare actions."
```

---

### Task 4: The navigation connections

**Files:**
- Modify: `frontend/src/views/VersionDetailView.vue` (add the profile link after the factor workbench link)
- Modify: `frontend/src/views/ModelDetailView.vue` (add the predict link after the diagnostics link)
- Modify: `frontend/src/App.vue` (add four nav entries after the Data entry)
- Test: `frontend/src/views/__tests__/VersionDetailView.test.ts`
- Test: `frontend/src/views/__tests__/ModelDetailView.test.ts`

**Interfaces:**
- Consumes: routes `/data/:slug/v/:version/profile` and `/models/:slug/predict` (both exist). ModelDetailView's props function reads `slug` and `version` from the route.
- Produces: three new inbound edges: `/data/:slug/v/:version/profile`, `/models/:slug/predict`, and the four nav entries `/models`, `/objectives`, `/metrics`, `/peril-structures`. Task 5's green graph test verifies all of them.

- [ ] **Step 1: Write the failing profile-link test**

In `frontend/src/views/__tests__/VersionDetailView.test.ts`, add this test inside the `describe("the version detail view", ...)` block:

```ts
it("links the WF-698 A9 profile for a version at any status", async () => {
  // FR-25: the profile screen was built but nothing reached it. It is a
  // version-level surface like the validation report, not gated on `validated`.
  stub();
  render(VersionDetailView, { props, ...mounted });
  const link = await screen.findByText("Profile");
  expect(link.closest("a")!.getAttribute("to")).toBe(
    `/data/${props.slug}/v/${VERSION.version}/profile`,
  );
});
```

The existing `mounted` stub keeps `to` as an attribute on the rendered `<a>`, so `getAttribute("to")` returns the evaluated template literal, exactly as the Factor workbench test asserts at its own line.

- [ ] **Step 2: Run the test to verify it fails**

Run: `pnpm --dir frontend vitest run src/views/__tests__/VersionDetailView.test.ts`
Expected: FAIL. `findByText("Profile")` times out; no such link exists.

- [ ] **Step 3: Implement the profile link**

In `frontend/src/views/VersionDetailView.vue`, insert after the Factor workbench RouterLink (which closes at line 131) and before the `</div>` that closes the `flex flex-wrap gap-3` container:

```vue
        <RouterLink
          :to="`/data/${slug}/v/${detail.version}/profile`"
          class="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
        >
          Profile
        </RouterLink>
```

The link copies the validation-report link's class and shape. It is unconditional, like the validation-report link: the profile route answers for a version at any status.

- [ ] **Step 4: Run the test to verify it passes**

Run: `pnpm --dir frontend vitest run src/views/__tests__/VersionDetailView.test.ts`
Expected: PASS, all tests in the file.

- [ ] **Step 5: Write the failing predict-link test**

In `frontend/src/views/__tests__/ModelDetailView.test.ts`, add this test inside the first `describe` block (the one whose `mounted` stub is `{ global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } } }`):

```ts
it("links the predict screen with this model's slug and version", async () => {
  stub();
  render(ModelDetailView, {
    props,
    global: {
      stubs: {
        RouterLink: {
          props: ["to"],
          template: '<a :href="typeof to === \'string\' ? to : to.name"><slot /></a>',
        },
      },
    },
  });
  const link = await screen.findByText("Predict");
  expect(link.closest("a")!.getAttribute("href")).toBe("model-predict");
});
```

The overridden stub renders the named target as the href; the target itself is the route graph's assertion (Task 1 resolves `name: 'model-predict'` to `/models/:slug/predict`).

- [ ] **Step 6: Run the test to verify it fails**

Run: `pnpm --dir frontend vitest run src/views/__tests__/ModelDetailView.test.ts`
Expected: FAIL. `findByText("Predict")` times out; no such link exists.

- [ ] **Step 7: Implement the predict link**

In `frontend/src/views/ModelDetailView.vue`, insert after the Diagnostics RouterLink (which closes at line 175, before `</header>`):

```vue
      <!-- Nothing else in the app reaches the predict screen, and a screen nothing
           links to is not delivered. -->
      <RouterLink
        v-if="model"
        :to="{
          name: 'model-predict',
          params: { slug },
          query: { version: String(model.version) },
        }"
        class="mt-2 inline-block text-sm text-sky-700 hover:underline"
      >
        Predict
      </RouterLink>
```

The link mirrors the Diagnostics link exactly, with the version query, so PredictionView shows this model's evidence.

- [ ] **Step 8: Run the test to verify it passes**

Run: `pnpm --dir frontend vitest run src/views/__tests__/ModelDetailView.test.ts`
Expected: PASS, all tests in the file.

- [ ] **Step 9: Add the four nav entries**

In `frontend/src/App.vue`, insert after the Data RouterLink (which closes at line 23) and before the Demo RouterLink (line 24):

```vue
        <RouterLink
          to="/models"
          class="text-sm text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-medium"
        >
          Models
        </RouterLink>
        <RouterLink
          to="/objectives"
          class="text-sm text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-medium"
        >
          Objectives
        </RouterLink>
        <RouterLink
          to="/metrics"
          class="text-sm text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-medium"
        >
          Metrics
        </RouterLink>
        <RouterLink
          to="/peril-structures"
          class="text-sm text-slate-600 hover:text-slate-900"
          active-class="text-slate-900 font-medium"
        >
          Peril structures
        </RouterLink>
```

The entries copy the Data entry's class and `active-class` exactly. `AuthControl` stays the last element of the nav. These four entries are the inbound edges for `/models`, `/objectives`, `/metrics` and `/peril-structures`; no App shell test exists, and the route-graph test owns the assertions.

- [ ] **Step 10: Run the reachability test — the graph flips green**

Run: `pnpm --dir frontend vitest run src/router/__tests__/reachability.test.ts`
Expected: PASS. Both tests pass; the first names no route, the second finds no dead link. The 16-route orphan set from Task 1 is now empty. If any route is still named, stop and report: the plan's closure table (Findings) lists the expected inbound edge per route.

- [ ] **Step 11: Commit**

```bash
git add frontend/src/App.vue frontend/src/views/VersionDetailView.vue frontend/src/views/ModelDetailView.vue frontend/src/views/__tests__/VersionDetailView.test.ts frontend/src/views/__tests__/ModelDetailView.test.ts
git commit -m "feat(frontend): close the last reachability gaps

FR-25. The version detail links its WF-698 A9 profile, the model detail
links the predict screen, and the nav reaches the model list and the three
libraries. The route-graph test flips green."
```

---

### Task 5: Residual sweep and gate

**Files:**
- Modify: none expected
- Check: the whole change set

- [ ] **Step 1: Sweep for commented-out links**

Run: `grep -rn "<!--" frontend/src/views frontend/src/App.vue`
Read every hit. A comment block that also contains `to=` or `href=` is a link the extractor deliberately ignores (the `COMMENT` strip). Such a link must not exist in the corpus. Expected: zero comment blocks contain `to=` or `href=`. The VersionDetailView comment block names "the link" in prose only, which is fine.

- [ ] **Step 2: Verify the demo guide self-updates**

Run: `grep -n "_routed_paths" backend/src/app/demo/guide.py`
Expected: the function reads `frontend/src/router/index.ts` (lines 124-144). No change needed: `/models` badges itself in the demo table once registered. State this in the task report.

- [ ] **Step 3: Run the full frontend gate**

Run: `pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend test && pnpm --dir frontend build`
Expected: PASS. `pnpm --dir frontend test` runs the route-graph suite green (Task 4, Step 10), the three touched view suites, and the untouched suites. `type-check` proves the new files against the generated schema types.

- [ ] **Step 4: Run the docs audit**

Run: `python3 scripts/audit-docs.py`
Expected: PASS. The plan is the only `docs/` change. Every requirement id it cites (FR-25, FR-408, FR-24) exists.

- [ ] **Step 5: Pre-push file check**

Run: `git diff --stat origin/main...HEAD`
Expected: exactly these files, all in the frontend or docs/plans:

```
frontend/src/App.vue
frontend/src/router/index.ts
frontend/src/views/DatasetListView.vue
frontend/src/views/ModelDetailView.vue
frontend/src/views/ModelListView.vue
frontend/src/views/VersionDetailView.vue
frontend/src/views/__tests__/DatasetListView.test.ts
frontend/src/views/__tests__/ModelDetailView.test.ts
frontend/src/views/__tests__/ModelListView.test.ts
frontend/src/views/__tests__/VersionDetailView.test.ts
frontend/src/router/__tests__/index.test.ts
frontend/src/router/__tests__/reachability.test.ts
frontend/src/router/__tests__/routeGraph.test.ts
frontend/src/router/__tests__/routeGraph.ts
docs/plans/PL-00809-wk-664-route-reachability-implementation-plan.md
```

A file outside this list means the working tree is dirty or the branch base is wrong. Stop and check.

- [ ] **Step 6: Commit any residual and report**

No further code is expected. Push the branch, then report to the manager: the positive control named the 16-route set and the dead `/models` link, the graph flips green, the gate passes, and the whitelist carries the two named exceptions for the review.

---

## Self-review

**1. Spec coverage.** FR-25's enforcement is Task 1 (the graph test plus its positive control). The dataset-list finding is Task 2. The absent `/models` route is Task 3. The profile and predict orphans plus the three nav-less libraries are Task 4. The two recorded findings and the closure table cover every route: 23 registered, 4 reached by the entry, 16 wired by this slice, 3 whitelisted with reasons. FR-408's gated demo and FR-24's jobs phase bound the whitelist. Neither is violated. No spec change, so no requirement id is minted.

**2. Placeholder scan.** Every step carries its code, its run command and its expected result. The only conditional language is the convention guard in Task 1, which states what a discrepancy means and what to do. The two whitelist entries carry the manager's ruling of 2026-08-26, recorded in F6 and F8.

**3. Type consistency.** `parseRoutes` returns `ParsedRoute` with `path`, `name`, `redirect`, `view`. `resolveTarget` and `extractTargets` take `ParsedRoute[]` throughout Task 1. Task 3's route record uses `name: "models"`, which the index.test.ts assertion expects. ModelListView consumes `Model.model_family_slug`, `version` and `status` — the generated schema's field names, the same ones ModelSelector.test.ts's fixture uses. The row target `/models/${slug}?version=${version}` and the predict link's `query: { version: String(model.version) }` both feed ModelDetailView's props function, which reads `route.query.version`. The closure table's route names match the router's patterns verbatim.
