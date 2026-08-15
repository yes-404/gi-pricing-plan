import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

/**
 * Routes follow `01` §5.3 exactly — the spec names them, and a route invented here would
 * be a second source of truth for where a thing lives.
 */
const routes: RouteRecordRaw[] = [
  { path: "/", redirect: "/data" },
  {
    path: "/data",
    name: "datasets",
    component: () => import("@/views/DatasetListView.vue"),
  },
  {
    path: "/data/:slug/v/:version",
    name: "version-detail",
    component: () => import("@/views/VersionDetailView.vue"),
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
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
