// tsconfig.app.json scopes `types` to ["vite/client"] (builtinObjectives.test.ts
// records the convention), so `node:fs` resolves here only through a per-file
// reference — the node types stay out of the app program.
/// <reference types="node" />
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
 * jobs view is a later phase (FR-OVR-21). The exception lifts when that UI
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

describe("route reachability (FR-OVR-22)", () => {
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
