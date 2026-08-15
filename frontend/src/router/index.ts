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
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
