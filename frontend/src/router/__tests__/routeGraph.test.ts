// tsconfig.app.json scopes `types` to ["vite/client"] (builtinObjectives.test.ts
// records the convention), so `node:fs` resolves here only through a per-file
// reference — the node types stay out of the app program.
/// <reference types="node" />
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
