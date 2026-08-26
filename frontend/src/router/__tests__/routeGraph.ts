/**
 * The route graph for FR-OVR-22. The test builds the link graph from the router
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

// Vitest's vite-node resolves `import.meta.url` under the `/@fs/` scheme for
// files outside the configured root; strip the prefix so readFileSync sees a
// real path. Outside vitest the prefix is absent and the replace is a no-op.
export const REPO_ROOT = new URL("../../../../", import.meta.url).pathname.replace(
  /^\/@fs/,
  "",
);

const COMMENT = /\/\/[^\n]*|\/\*[\s\S]*?\*\//g;
const RECORD =
  /\{\s*path:\s*"([^"]+)",\s*(?:name:\s*"([^"]*)",\s*)?(?:redirect:\s*"([^"]+)",|[\s\S]*?component:\s*\(\)\s*=>\s*import\("@\/([^"]+)"\),)[\s\S]*?\n\s*\},/g;
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
    trimmed.startsWith("`") ||
    trimmed.startsWith('"') ||
    trimmed.startsWith("{") ||
    trimmed.startsWith("/")
  );
}

export function resolveTarget(raw: string, routes: ParsedRoute[]): string | null {
  const named = /^\{\s*name:\s*'([^']+)'/.exec(raw.trim());
  if (named) {
    const route = routes.find((candidate) => candidate.name === named[1]);
    return route ? route.path : null;
  }
  const trimmed = raw.trim();
  const literal = /^(`[^`]*`|"[^"]*")$/.exec(trimmed);
  // A `to` or `href` attribute captures its value without delimiters
  // (`to="/data"` yields `/data`), while a script-side `href:` captures with
  // them. Both forms resolve here; the segment loop below is shared.
  const target = literal
    ? literal[1].slice(1, -1).split("?")[0]
    : trimmed.startsWith("/")
      ? trimmed.split("?")[0]
      : null;
  if (target === null || !target.startsWith("/")) return null;
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
