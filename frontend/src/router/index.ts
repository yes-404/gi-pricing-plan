import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

/**
 * Routes follow `01` §5.3 exactly — the spec names them, and a route invented here would
 * be a second source of truth for where a thing lives.
 */
export const routes: RouteRecordRaw[] = [
  { path: "/", redirect: "/data" },
  {
    // FR-PLAT-53's entrance. Routed unconditionally; the API answers 404 where the demo is
    // not enabled, and the view reads that as a state rather than a failure — so there is
    // one switch (`dev_auth_enabled`), not a second one in the frontend build.
    path: "/demo",
    name: "demo",
    component: () => import("@/views/DemoView.vue"),
  },
  {
    path: "/data",
    name: "datasets",
    component: () => import("@/views/DatasetListView.vue"),
  },
  {
    path: "/data/:slug",
    name: "dataset-detail",
    component: () => import("@/views/DatasetDetailView.vue"),
    props: true,
  },
  {
    path: "/data/:slug/rules",
    name: "rule-set",
    component: () => import("@/views/RuleSetView.vue"),
    props: true,
  },
  {
    path: "/data/:slug/v/:version",
    name: "version-detail",
    component: () => import("@/views/VersionDetailView.vue"),
    props: true,
  },
  {
    path: "/data/:slug/v/:version/profile",
    name: "profile",
    component: () => import("@/views/ProfileView.vue"),
    props: true,
  },
  {
    path: "/data/:slug/v/:version/validation",
    name: "validation-report",
    component: () => import("@/views/ValidationReportView.vue"),
    // `props: true` so the view takes its inputs as props rather than reaching into the
    // router — which is what makes it renderable in a test without a router at all.
    props: true,
  },
  {
    // `02` §5.3. Both this and `/models/:slug` match the path `/models/compare`, and a model
    // slug of `compare` is legal under `refs.py`'s pattern — so which one wins is a real
    // question. **Vue Router's ranking of a static segment above a dynamic one is what
    // decides it**: moving this entry below `/models/:slug` was tried, and the resolution
    // test still passed. Declaring it first is therefore defensive rather than load-bearing,
    // and the test is what holds the guarantee.
    // No `props: true`: it maps path params only, and this view's input is a query. The
    // `/models/:slug` entry below is the precedent for a query-carried input.
    path: "/models/compare",
    name: "model-comparison",
    component: () => import("@/views/ModelComparisonView.vue"),
  },
  {
    // `02` §5.3. Three segments, so it cannot collide with `/models/:slug` the way
    // `/models/compare` does — the ranking question above does not arise here.
    //
    // Function-mode props, not `props: true`: the boolean form maps `route.params` only, and
    // `?version=` is a query. Every route whose view takes a version is in this form; the
    // `/models/:slug` entry below was the one that was not, and its `version` prop was
    // permanently `undefined` for it.
    path: "/models/:slug/diagnostics",
    name: "model-diagnostics",
    component: () => import("@/views/DiagnosticsView.vue"),
    props: (route) => ({
      slug: String(route.params.slug),
      version: typeof route.query.version === "string" ? route.query.version : undefined,
    }),
  },
  {
    // `02` §5.3's Backtest view. Addressed by backtest id, not by model — a model has many
    // (FR-MODEL-92) — so `:slug` here is for the breadcrumb and the link back to the fit.
    path: "/models/:slug/backtests/:backtestId",
    name: "model-backtest",
    component: () => import("@/views/BacktestView.vue"),
    props: (route) => ({
      slug: String(route.params.slug),
      backtestId: String(route.params.backtestId),
    }),
  },
  {
    // `02` §5.3. Three segments, so it cannot collide with `/models/:slug` — the ranking
    // question recorded at the `/models/compare` entry does not arise here, and
    // `/models/:slug/diagnostics` above is the precedent for exactly this shape.
    //
    // Function-mode props, not `props: true`: the boolean form maps `route.params` only, and
    // `?version=` is a query.
    path: "/models/:slug/predict",
    name: "model-predict",
    component: () => import("@/views/PredictionView.vue"),
    props: (route) => ({
      slug: String(route.params.slug),
      version: typeof route.query.version === "string" ? route.query.version : undefined,
    }),
  },
  {
    // `02` §5.3. List only — FR-MODEL-127. The cell's editor is Phase 2 (FR-MODEL-75 gates
    // `expression` authoring off throughout Phase 1), and under FR-OVR-21 the cell binds
    // nothing, so the editor is not a shortfall here.
    path: "/objectives",
    name: "objective-library",
    component: () => import("@/views/ObjectiveLibraryView.vue"),
  },
  {
    // `02` §5.3's mirror of the objective library. **Name collision, latent and deliberate.**
    // The API serves an unauthenticated Prometheus endpoint at `/metrics`
    // (`backend/src/app/api/health.py`, FR-PLAT-40). Nothing collides today: the API is
    // mounted under `/api/v1` and the SPA is served separately, so the two `/metrics` never
    // share an origin. Under same-origin serving they would, and the scrape path is the one
    // with an external consumer. Recorded here rather than renamed — renaming a scrape path
    // to pre-empt a deployment that does not exist breaks a live config to fix nothing.
    path: "/metrics",
    name: "metric-library",
    component: () => import("@/views/MetricLibraryView.vue"),
  },
  {
    // `02` §5.3's Model spec builder.
    //
    // Declared above `/models/:slug` for readability, **not** because order decides the
    // match. W6b-4a's plan asserted a `/models/new` record placed after the parameterised
    // one would be captured by `:slug`. That is false, and it is now measured twice on
    // **vue-router 5.2.0**, on two different collisions:
    //
    //   - W6b-2, 2026-08-24 — `/models/compare` vs `/models/:slug`, recorded at the
    //     `/models/compare` entry twelve lines above `/models/:slug`.
    //   - W6b-4a, 2026-08-25 — this entry, with a positive control: two *equal-rank*
    //     dynamic routes, where only declaration order can break the tie, do flip. So the
    //     probe can detect order mattering, and reports that here it does not.
    //
    // A static segment outranks a dynamic one from either position. The tests in
    // `__tests__/index.test.ts` therefore assert **resolution**, which is the property
    // that matters and survives reordering. Nothing here is a warning against moving the
    // record; a future route that makes ordering load-bearing needs its own evidence.
    path: "/models/new",
    name: "model-spec-builder",
    component: () => import("@/views/ModelSpecBuilderView.vue"),
  },
  {
    // `02` §5.3. `?version=` selects one; the latest by default. Not `@version` in the
    // path: an `@` must be percent-encoded by every client, and `family@7` then reads as
    // `family%407` in every log and support conversation.
    path: "/models/:slug",
    name: "model-detail",
    component: () => import("@/views/ModelDetailView.vue"),
    // Function mode, not `props: true`: the boolean form maps `route.params` only, and
    // `?version=` is a query, so this view's `version` prop was permanently `undefined` and
    // every load fetched the latest model. `02` §5.3 promises the selector works, and
    // `QuantileBoundNotice` builds a link carrying it, labelled `slug@version` — so the link
    // named one version and the page showed whichever was latest.
    props: (route) => ({
      slug: String(route.params.slug),
      version: typeof route.query.version === "string" ? route.query.version : undefined,
    }),
  },
  {
    // `02` §5.3 and `00` §5.6, both of which name this path exactly. Routed on the version
    // **id** rather than slug-and-number, because a banding is derived against one specific
    // version and the id is what every `/dataset-versions/{id}/…` route already takes.
    path: "/factors/:datasetVersionId",
    name: "factor-workbench",
    component: () => import("@/views/FactorWorkbenchView.vue"),
    props: true,
  },
  {
    path: "/reference",
    name: "reference",
    component: () => import("@/views/ReferenceView.vue"),
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
