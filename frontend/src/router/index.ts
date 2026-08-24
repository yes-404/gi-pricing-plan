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
    // `?version=` is a query. The `/models/:slug` entry below declares `props: true` while
    // its view reads `props.version`, which is the bug Task 12 fixes; this entry does not
    // copy it.
    path: "/models/:slug/diagnostics",
    name: "model-diagnostics",
    component: () => import("@/views/DiagnosticsView.vue"),
    props: (route) => ({
      slug: String(route.params.slug),
      version: typeof route.query.version === "string" ? route.query.version : undefined,
    }),
  },
  {
    // `02` §5.3. `?version=` selects one; the latest by default. Not `@version` in the
    // path: an `@` must be percent-encoded by every client, and `family@7` then reads as
    // `family%407` in every log and support conversation.
    path: "/models/:slug",
    name: "model-detail",
    component: () => import("@/views/ModelDetailView.vue"),
    props: true,
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
